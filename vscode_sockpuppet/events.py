"""Lightweight EventEmitter used by the client.

Provides a small API similar to VS Code's EventEmitter:event pair:
  - emitter.event(handler) -> unsubscribe callable
  - emitter.fire(data) -> notify handlers

Also supports optional hooks when the first listener is added and when the
last listener is removed so callers can perform subscription/unsubscription
side-effects (for example, informing a server).
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

if TYPE_CHECKING:
    from .client import VSCodeClient

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


class Event:
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

    def __call__(self, handler: Callable[[Any], None]) -> Callable[[], None]:
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
        self._client.subscribe(self._event_name, handler)

        def dispose():
            """Unsubscribe from the event."""
            self._client.unsubscribe(self._event_name, handler)

        return dispose


class WindowEvents:
    """
    Event emitters for window-related VS Code events.

    Provides VS Code-style event subscription with on_did_* methods.
    """

    def __init__(self, client: VSCodeClient):
        """Initialize window events."""
        self._client = client

    @property
    def on_did_change_active_text_editor(self) -> Event:
        """
        Event fired when the active text editor changes.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(editor):
                if editor:
                    print(f"Active editor: {editor['fileName']}")

            dispose = window.on_did_change_active_text_editor(handler)
        """
        return Event(self._client, "window.onDidChangeActiveTextEditor")

    @property
    def on_did_change_text_editor_selection(self) -> Event:
        """
        Event fired when the selection in an editor changes.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(data):
                sel = data['selections'][0]
                print(f"Line {sel['start']['line']}")

            dispose = window.on_did_change_text_editor_selection(handler)
        """
        return Event(self._client, "window.onDidChangeTextEditorSelection")

    @property
    def on_did_change_visible_text_editors(self) -> Event:
        """
        Event fired when the visible text editors change.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(data):
                print(f"{data['count']} editors visible")

            dispose = window.on_did_change_visible_text_editors(handler)
        """
        return Event(self._client, "window.onDidChangeVisibleTextEditors")

    @property
    def on_did_open_terminal(self) -> Event:
        """
        Event fired when a terminal is opened.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(terminal):
                print(f"Terminal opened: {terminal['name']}")

            dispose = window.on_did_open_terminal(handler)
        """
        return Event(self._client, "window.onDidOpenTerminal")

    @property
    def on_did_close_terminal(self) -> Event:
        """
        Event fired when a terminal is closed.

        Returns:
            Event that can be called with a handler

        Example:
            dispose = window.on_did_close_terminal(handler)
        """
        return Event(self._client, "window.onDidCloseTerminal")

    @property
    def on_did_change_terminal_state(self) -> Event:
        """
        Event fired when a terminal's state changes.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(data):
                print(f"Terminal {data['name']}: interacted = {data['isInteractedWith']}")

            dispose = window.on_did_change_terminal_state(handler)
        """
        return Event(self._client, "window.onDidChangeTerminalState")

    @property
    def on_did_change_text_editor_visible_ranges(self) -> Event:
        """
        Event fired when visible ranges in an editor change (scrolling).

        Returns:
            Event that can be called with a handler

        Example:
            def handler(data):
                print(f"Visible in {data['uri']}: {len(data['visibleRanges'])} ranges")

            dispose = window.on_did_change_text_editor_visible_ranges(handler)
        """
        return Event(self._client, "window.onDidChangeTextEditorVisibleRanges")

    @property
    def on_did_change_text_editor_options(self) -> Event:
        """
        Event fired when text editor options change.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(data):
                opts = data['options']
                print(f"Tab size: {opts['tabSize']}")

            dispose = window.on_did_change_text_editor_options(handler)
        """
        return Event(self._client, "window.onDidChangeTextEditorOptions")

    @property
    def on_did_change_text_editor_view_column(self) -> Event:
        """
        Event fired when an editor's view column changes.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(data):
                print(f"Editor moved to column {data['viewColumn']}")

            dispose = window.on_did_change_text_editor_view_column(handler)
        """
        return Event(self._client, "window.onDidChangeTextEditorViewColumn")

    @property
    def on_did_change_window_state(self) -> Event:
        """
        Event fired when the window state changes (focus).

        Returns:
            Event that can be called with a handler

        Example:
            def handler(data):
                if data['focused']:
                    print("Window gained focus")
                else:
                    print("Window lost focus")

            dispose = window.on_did_change_window_state(handler)
        """
        return Event(self._client, "window.onDidChangeWindowState")


class WorkspaceEvents:
    """
    Event emitters for workspace-related VS Code events.

    Provides VS Code-style event subscription with on_did_* methods.
    """

    def __init__(self, client: VSCodeClient):
        """Initialize workspace events."""
        self._client = client

    @property
    def on_did_open_text_document(self) -> Event:
        """
        Event fired when a text document is opened.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(document):
                print(f"Opened: {document['fileName']}")

            dispose = workspace.on_did_open_text_document(handler)
        """
        return Event(self._client, "workspace.onDidOpenTextDocument")

    @property
    def on_did_close_text_document(self) -> Event:
        """
        Event fired when a text document is closed.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(document):
                print(f"Closed: {document['fileName']}")

            dispose = workspace.on_did_close_text_document(handler)
        """
        return Event(self._client, "workspace.onDidCloseTextDocument")

    @property
    def on_did_save_text_document(self) -> Event:
        """
        Event fired when a text document is saved.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(document):
                print(f"Saved: {document['fileName']}")

            dispose = workspace.on_did_save_text_document(handler)
        """
        return Event(self._client, "workspace.onDidSaveTextDocument")

    @property
    def on_did_change_text_document(self) -> Event:
        """
        Event fired when a text document changes.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(event):
                print(f"Changed: {event['uri']}")
                for change in event['contentChanges']:
                    print(f"  Text: {change['text']}")

            dispose = workspace.on_did_change_text_document(handler)
        """
        return Event(self._client, "workspace.onDidChangeTextDocument")

    @property
    def on_did_change_workspace_folders(self) -> Event:
        """
        Event fired when workspace folders are added or removed.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(event):
                print(f"Added: {len(event['added'])}")
                print(f"Removed: {len(event['removed'])}")

            dispose = workspace.on_did_change_workspace_folders(handler)
        """
        return Event(self._client, "workspace.onDidChangeWorkspaceFolders")

    @property
    def on_did_change_configuration(self) -> Event:
        """
        Event fired when the configuration changes.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(event):
                print("Configuration changed")

            dispose = workspace.on_did_change_configuration(handler)
        """
        return Event(self._client, "workspace.onDidChangeConfiguration")

    @property
    def on_did_create_files(self) -> Event:
        """
        Event fired when files are created.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(data):
                for file in data['files']:
                    print(f"Created: {file['uri']}")

            dispose = workspace.on_did_create_files(handler)
        """
        return Event(self._client, "workspace.onDidCreateFiles")

    @property
    def on_did_delete_files(self) -> Event:
        """
        Event fired when files are deleted.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(data):
                for file in data['files']:
                    print(f"Deleted: {file['uri']}")

            dispose = workspace.on_did_delete_files(handler)
        """
        return Event(self._client, "workspace.onDidDeleteFiles")

    @property
    def on_did_rename_files(self) -> Event:
        """
        Event fired when files are renamed or moved.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(data):
                for file in data['files']:
                    print(f"Renamed: {file['oldUri']} -> {file['newUri']}")

            dispose = workspace.on_did_rename_files(handler)
        """
        return Event(self._client, "workspace.onDidRenameFiles")
