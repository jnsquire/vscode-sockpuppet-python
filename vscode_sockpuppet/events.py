"""
Event emitter classes for VS Code-style event subscriptions
"""

from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .client import VSCodeClient


class Event:
    """
    Represents a VS Code event that can be subscribed to.

    Similar to VS Code's Event<T> interface, provides a callable
    subscription interface.
    """

    def __init__(self, client: "VSCodeClient", event_name: str):
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

    def __init__(self, client: "VSCodeClient"):
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


class WorkspaceEvents:
    """
    Event emitters for workspace-related VS Code events.

    Provides VS Code-style event subscription with on_did_* methods.
    """

    def __init__(self, client: "VSCodeClient"):
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
