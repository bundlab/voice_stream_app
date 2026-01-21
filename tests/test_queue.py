# import pytest
import os
import sys

# Ensure project root is on sys.path for test discovery/imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import print_worker


def test_print_worker_enqueue_lines():
    from queue import Queue
    from threading import Event

    msg_queue = Queue()
    stop_event = Event()
    lines = ["line 1", "line 2", "line 3"]

    # Run the print_worker as a separate thread or function.
    # Here you'd typically use threading to test concurrently.
    # Simulate call to the print_worker function. Use run_once to exit.
    print_worker(
        lines,
        msg_queue,
        stop_event,
        print_interval=0,
        enqueue_for_tts=True,
        run_once=True,
    )

    # Check that all lines were enqueued.
    for line in lines:
        assert msg_queue.get(timeout=1) == line

    # Ensure queue is empty after processing lines.
    assert msg_queue.empty()
