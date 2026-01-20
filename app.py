import threading
import queue
import time
import logging
import signal
import sys
import argparse
from pathlib import Path

# NOTE: import pyttsx3 only inside TTS functions to avoid import-time errors in CI/tests
# Configuration defaults
DEFAULT_LINES = [
    "Hello, this is a live speaking text printer.",
    "This app prints and speaks text continuously.",
    "You can modify the text list to include your own content.",
    "Python makes it easy to combine speech and printing.",
    "Thanks for using this demo!"
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def tts_worker(msg_queue: queue.Queue, stop_event: threading.Event, rate: int = 150, volume: float = 1.0):
    """TTS worker that initializes the pyttsx3 engine inside the thread and speaks queued messages.

    This avoids sharing the engine across threads and keeps runAndWait blocking only inside this thread.
    """
    try:
        import pyttsx3
    except Exception as e:
        logging.exception("pyttsx3 is not available: %s", e)
        return

    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", rate)
        engine.setProperty("volume", volume)
    except Exception as e:
        logging.exception("Failed to initialize TTS engine: %s", e)
        return

    logging.info("TTS worker started")
    try:
        while not stop_event.is_set():
            try:
                line = msg_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if line is None:
                # sentinel
                break

            try:
                engine.say(line)
                engine.runAndWait()
            except Exception:
                logging.exception("Error while speaking line: %r", line)
            finally:
                msg_queue.task_done()
    finally:
        try:
            engine.stop()
        except Exception:
            pass
        logging.info("TTS worker exiting")

def print_worker(lines, msg_queue: queue.Queue, stop_event: threading.Event, print_interval: float = 0.5, enqueue_for_tts: bool = True, run_once: bool = False):
    """Printer worker that prints lines and optionally enqueues them for TTS.

    Args:
        lines: iterable of strings to print.
        msg_queue: queue to put lines on for TTS.
        stop_event: threading.Event to stop the worker.
        print_interval: delay between lines.
        enqueue_for_tts: whether to put printed lines on the msg_queue.
        run_once: if True, run through the lines once and then exit.
    """
    logging.info("Printer worker started")
    try:
        while not stop_event.is_set():
            for line in lines:
                if stop_event.is_set():
                    break
                print(line)
                if enqueue_for_tts and msg_queue is not None:
                    try:
                        msg_queue.put(line, timeout=0.5)
                    except queue.Full:
                        logging.warning("TTS queue full; skipping line")
                if print_interval:
                    time.sleep(print_interval)
            if run_once:
                break
    except Exception:
        logging.exception("Printer worker error")
    finally:
        logging.info("Printer worker exiting")

def synthesize_to_file(lines, output_path: str, rate: int = 150, volume: float = 1.0):
    """Synthesize the provided lines to a file using pyttsx3.save_to_file and runAndWait.
    """
    try:
        import pyttsx3
    except Exception as e:
        logging.exception("pyttsx3 is not available: %s", e)
        raise

    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)

    text = "\n".join(lines)
    output_path = str(output_path)
    logging.info("Saving synthesized audio to %s", output_path)
    engine.save_to_file(text, output_path)
    engine.runAndWait()
    logging.info("Finished saving %s", output_path)

def run(lines=None, *, continuous=False, rate=150, volume=1.0, print_interval=0.5):
    """Run the printer + TTS workers until interrupted.

    Returns after graceful shutdown.
    """
    if lines is None:
        lines = DEFAULT_LINES

    stop_event = threading.Event()
    msg_queue = queue.Queue(maxsize=64)

    def handle_signal(signum, frame):
        logging.info("Signal %s received, shutting down", signum)
        stop_event.set()
        # Wake TTS worker if waiting
        try:
            msg_queue.put_nowait(None)
        except Exception:
            pass

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    tts_thread = threading.Thread(target=tts_worker, args=(msg_queue, stop_event, rate, volume), daemon=True)
    printer_thread = threading.Thread(
        target=print_worker, args=(lines, msg_queue, stop_event, print_interval, True, not continuous), daemon=True
    )

    tts_thread.start()
    printer_thread.start()

    try:
        while (tts_thread.is_alive() or printer_thread.is_alive()) and not stop_event.is_set():
            time.sleep(0.2)
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt, initiating shutdown")
        stop_event.set()
        try:
            msg_queue.put_nowait(None)
        except Exception:
            pass

    # Wait a short while for threads to finish
    tts_thread.join(timeout=2.0)
    printer_thread.join(timeout=2.0)
    logging.info("Shutdown complete")

def _read_lines_from_file(path: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    return [l.rstrip("\n\r") for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]

def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Voice stream demo: print text and speak it locally using pyttsx3.")
    parser.add_argument("--lines-file", help="Path to a text file with one line per utterance (overrides built-in lines)")
    parser.add_argument("--continuous", action="store_true", help="Loop continuously over the provided lines")
    parser.add_argument(
        "--rate", 
        type=int, 
        default=150, 
        help="Speech rate for TTS (words per minute)"
    )
    
    parser.add_argument(
        "--volume", 
        type=float, 
        default=1.0, 
        help="TTS volume (0.0..1.0)"
    )
    
    parser.add_argument(
        "--print-interval", 
        type=float, 
        default=0.5, 
        help="Seconds between printed lines"
    )
    
    parser.add_argument(
        "--save", 
        metavar="OUTPUT", 
        help="Synthesize lines to a file (e.g., output.mp3 or output.wav) and exit"
    )
    
    parser.add_argument(
        "--run-once", 
        dest="run_once", 
        action="store_true", 
        help="Print and speak the lines once and exit (overrides --continuous)"
    )
    return parser.parse_args(argv)

def main(argv=None):
    args = parse_args(argv)

    if args.lines_file:
        lines = _read_lines_from_file(args.lines_file)
    else:
        lines = DEFAULT_LINES

    if args.save:
        synthesize_to_file(lines, args.save, rate=args.rate, volume=args.volume)
        return

    # run_once flag means not continuous
    continuous = bool(args.continuous) and not args.run_once
    run(lines, continuous=continuous, rate=args.rate, volume=args.volume, print_interval=args.print_interval)


if __name__ == "__main__":
    main()