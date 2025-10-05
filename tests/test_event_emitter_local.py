import time
import threading

from vscode_sockpuppet.client import VSCodeClient


def test_local_emitter_fire_and_unsubscribe():
    """Verify EventEmitter can be used locally without an extension host.

    The test stubs out the client's network call (_send_request) so that the
    EventEmitter hooks that normally subscribe/unsubscribe on the server won't
    attempt IO. We then register a handler, fire an event locally and assert
    it is delivered, then unsubscribe and verify no further deliveries occur.
    """

    client = VSCodeClient()

    # Stub network interaction used by on_first_add/on_no_listeners hooks.
    client._send_request = lambda method, params=None: True

    # Create an emitter for a test event name
    emitter = client.get_emitter("test.localEvent")

    received: list[dict] = []
    seen = threading.Event()

    def handler(payload: dict) -> None:
        received.append(payload)
        seen.set()

    # Register handler (triggers on_first_add which calls our stub)
    unsubscribe = emitter.event(handler)

    # Fire one event and wait for delivery
    emitter.fire({"value": 42})
    assert seen.wait(timeout=1.0), "Handler was not called"
    assert received == [{"value": 42}]

    # Unsubscribe and ensure no further deliveries
    unsubscribe()
    # Clear and fire again
    received.clear()
    seen.clear()
    emitter.fire({"value": 100})

    # Give a small window for any stray calls
    time.sleep(0.05)
    assert received == [], "Handler was called after unsubscribe"
