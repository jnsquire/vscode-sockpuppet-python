"""
Example: Event-driven shutdown pattern

Demonstrates how to use threading.Event for clean, immediate shutdown
on Ctrl-C without polling or sleep loops.
"""

import signal
import threading
import time


class State:
    """Application state with event-driven shutdown."""

    def __init__(self):
        self.counter = 0
        self.stop_event = threading.Event()

    def stop(self):
        """Signal shutdown."""
        self.stop_event.set()

    @property
    def running(self):
        """Check if still running."""
        return not self.stop_event.is_set()


def main():
    """Demonstrate event-driven shutdown."""
    state = State()

    # Set up Ctrl-C handler that fires stop event
    def signal_handler(sig, frame):
        print("\n⌨️  Ctrl-C detected!")
        state.stop()

    signal.signal(signal.SIGINT, signal_handler)

    print("Event-driven shutdown demo")
    print("Press Ctrl-C to exit immediately (no delay!)\n")

    start_time = time.time()

    while state.running:
        # Wait for 2 seconds OR until stop event is set
        if state.stop_event.wait(timeout=2.0):
            # Event was set - exiting promptly after wait (may be up to timeout delay)
            print("Stop event detected, exiting promptly after wait!")
            break

        # Timeout expired - do periodic work
        state.counter += 1
        elapsed = time.time() - start_time
        print(f"[{elapsed:.1f}s] Counter: {state.counter}")

    print(f"\n✅ Exited cleanly after {state.counter} iterations")
    print(f"Total time: {time.time() - start_time:.1f}s")


if __name__ == "__main__":
    main()
