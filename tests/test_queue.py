#import pytest
from app import print_worker


def test_print_worker_enqueue_lines():
    from queue import Queue
    from threading import Event

    msg_queue = Queue()
    stop_event = Event()
    lines = ["line 1", "line 2", "line 3"]

    # Run the print_worker as a separate thread or function.
    # Here you'd typically use threading to test concurrently.

    # Simulate call to the print_worker function.
    print_worker(
        lines, msg_queue, 
        stop_event, 
        print_interval=0, 
        enqueue_for_tts=True, 
        run_once=False)

    # Check that all lines were enqueued.
    for line in lines:
        assert msg_queue.get(timeout=1) == line

    # Ensure queue is empty after processing lines.
    assert msg_queue.empty()
