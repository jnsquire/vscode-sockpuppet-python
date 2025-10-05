"""Core event emitter and event wrapper classes."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Callable, Generic, TypeVar

if TYPE_CHECKING:
    from ..client import VSCodeClient

T = TypeVar("T")


class EventEmitter(Generic[T]):
    """Tiny thread-safe event emitter.

    on_first_add: optional callable invoked once when the first handler is
    registered. on_no_listeners: optional callable invoked once when the
    last handler is removed.
    """

    def __init__(
        self,
        on_first_add: Callable[[], None] | None = None,
        on_no_listeners: Callable[[], None] | None = None,
    ) -> None:
        self._handlers: list[Callable[[T], None]] = []
        self._lock = threading.Lock()
        self._on_first_add = on_first_add
        self._on_no_listeners = on_no_listeners

    def event(self, handler: Callable[[T], None]) -> Callable[[], None]:
        """Register a handler and return an unsubscribe callable."""
        first = False
        with self._lock:
            if not self._handlers:
                first = True
            self._handlers.append(handler)

        if first and self._on_first_add:
            try:
                self._on_first_add()
            except Exception:
                # Avoid bubbling subscription hook errors into callers
                pass

        def _dispose() -> None:
            no_listeners = False
            with self._lock:
                if handler in self._handlers:
                    self._handlers.remove(handler)
                if not self._handlers:
                    no_listeners = True

            if no_listeners and self._on_no_listeners:
                try:
                    self._on_no_listeners()
                except Exception:
                    pass

        return _dispose

    def remove(self, handler: Callable[[T], None]) -> None:
        """Remove a specific handler."""
        no_listeners = False
        with self._lock:
            if handler in self._handlers:
                self._handlers.remove(handler)
            if not self._handlers:
                no_listeners = True

        if no_listeners and self._on_no_listeners:
            try:
                self._on_no_listeners()
            except Exception:
                pass

    def has_listeners(self) -> bool:
        with self._lock:
            return bool(self._handlers)

    def fire(self, data: T) -> None:
        with self._lock:
            handlers = list(self._handlers)

        for h in handlers:
            try:
                h(data)
            except Exception as e:
                # Keep this lightweight — printing is acceptable for now
                print(f"Error in EventEmitter handler: {e}")


class Event(Generic[T]):
    """
    Represents a VS Code event that can be subscribed to.

    Similar to VS Code's Event<T> interface, provides a callable
    subscription interface.
    """

    def __init__(self, client: VSCodeClient, event_name: str):
        """
        Initialize an event.

        Args:
            client: The VS Code client instance
            event_name: The full event name (e.g., 'workspace.onDidSaveTextDocument')
        """
        self._client = client
        self._event_name = event_name

    @property
    def emitter(self) -> EventEmitter[T]:
        """Access the underlying EventEmitter for this event name.

        This is useful when callers want to keep or inspect the returned
        unsubscribe callable or perform more advanced interactions with the
        emitter itself.
        """
        return self._client.get_emitter(self._event_name)

    def __call__(self, handler: Callable[[T], None]) -> Callable[[], None]:
        """
        Subscribe to the event.

        Args:
            handler: Callback function to handle event data

        Returns:
            Disposable function that unsubscribes when called

        Example:
            dispose = workspace.on_did_save_text_document(handler)
            # Later:
            dispose()
        """
        # Register using the new add_event_listener API which returns an
        # unsubscribe callable. This centralizes subscription management in
        # the client and avoids direct subscribe/unsubscribe calls here.
        # Delegate to client's add_event_listener which returns an
        # unsubscribe callable. Type is preserved via the generic T.
        unsubscribe = self._client.add_event_listener(self._event_name, handler)  # type: ignore[arg-type]
        return unsubscribe
