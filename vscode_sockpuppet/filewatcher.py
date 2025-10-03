"""
File System Watcher for VS Code workspace
"""

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .client import VSCodeClient


class FileSystemWatcher:
    """
    Watches for file system changes (create, change, delete).

    File system watchers use glob patterns to match files and can monitor
    workspace folders or specific paths.
    """

    def __init__(
        self,
        client: "VSCodeClient",
        watcher_id: str,
        glob_pattern: str,
        ignore_create_events: bool = False,
        ignore_change_events: bool = False,
        ignore_delete_events: bool = False,
    ):
        """
        Initialize a FileSystemWatcher.

        Args:
            client: The VSCodeClient instance
            watcher_id: Unique identifier for this watcher
            glob_pattern: Glob pattern to match files (e.g., '**/*.py')
            ignore_create_events: If true, file creation events are ignored
            ignore_change_events: If true, file change events are ignored
            ignore_delete_events: If true, file deletion events are ignored
        """
        self.client = client
        self.watcher_id = watcher_id
        self.glob_pattern = glob_pattern
        self.ignore_create_events = ignore_create_events
        self.ignore_change_events = ignore_change_events
        self.ignore_delete_events = ignore_delete_events
        self._disposed = False

        # Event handler callbacks
        self._on_create_handlers: list[Callable[[str], None]] = []
        self._on_change_handlers: list[Callable[[str], None]] = []
        self._on_delete_handlers: list[Callable[[str], None]] = []

        # Subscribe to watcher events
        if not ignore_create_events:
            event_name = f"watcher.{watcher_id}.onCreate"
            self.client.subscribe(event_name, self._handle_create)

        if not ignore_change_events:
            event_name = f"watcher.{watcher_id}.onChange"
            self.client.subscribe(event_name, self._handle_change)

        if not ignore_delete_events:
            event_name = f"watcher.{watcher_id}.onDelete"
            self.client.subscribe(event_name, self._handle_delete)

    def _handle_create(self, data: dict) -> None:
        """Handle file creation events."""
        uri = data.get("uri", "")
        for handler in self._on_create_handlers:
            try:
                handler(uri)
            except Exception as e:
                print(f"Error in onCreate handler: {e}")

    def _handle_change(self, data: dict) -> None:
        """Handle file change events."""
        uri = data.get("uri", "")
        for handler in self._on_change_handlers:
            try:
                handler(uri)
            except Exception as e:
                print(f"Error in onChange handler: {e}")

    def _handle_delete(self, data: dict) -> None:
        """Handle file deletion events."""
        uri = data.get("uri", "")
        for handler in self._on_delete_handlers:
            try:
                handler(uri)
            except Exception as e:
                print(f"Error in onDelete handler: {e}")

    def on_did_create(self, handler: Callable[[str], None]) -> Callable[[], None]:
        """
        Register a handler for file creation events.

        Args:
            handler: Callback function that takes a file URI string

        Returns:
            Dispose function to unregister the handler

        Example:
            def on_file_created(uri: str):
                print(f"File created: {uri}")

            watcher = workspace.create_file_system_watcher("**/*.py")
            dispose = watcher.on_did_create(on_file_created)

            # Later, to stop listening:
            dispose()
        """
        if self.ignore_create_events:
            raise ValueError("Cannot register onCreate handler when ignoreCreateEvents is True")

        self._on_create_handlers.append(handler)

        def dispose():
            if handler in self._on_create_handlers:
                self._on_create_handlers.remove(handler)

        return dispose

    def on_did_change(self, handler: Callable[[str], None]) -> Callable[[], None]:
        """
        Register a handler for file change events.

        Args:
            handler: Callback function that takes a file URI string

        Returns:
            Dispose function to unregister the handler

        Example:
            def on_file_changed(uri: str):
                print(f"File changed: {uri}")

            watcher = workspace.create_file_system_watcher("**/*.py")
            dispose = watcher.on_did_change(on_file_changed)
        """
        if self.ignore_change_events:
            raise ValueError("Cannot register onChange handler when ignoreChangeEvents is True")

        self._on_change_handlers.append(handler)

        def dispose():
            if handler in self._on_change_handlers:
                self._on_change_handlers.remove(handler)

        return dispose

    def on_did_delete(self, handler: Callable[[str], None]) -> Callable[[], None]:
        """
        Register a handler for file deletion events.

        Args:
            handler: Callback function that takes a file URI string

        Returns:
            Dispose function to unregister the handler

        Example:
            def on_file_deleted(uri: str):
                print(f"File deleted: {uri}")

            watcher = workspace.create_file_system_watcher("**/*.py")
            dispose = watcher.on_did_delete(on_file_deleted)
        """
        if self.ignore_delete_events:
            raise ValueError("Cannot register onDelete handler when ignoreDeleteEvents is True")

        self._on_delete_handlers.append(handler)

        def dispose():
            if handler in self._on_delete_handlers:
                self._on_delete_handlers.remove(handler)

        return dispose

    def dispose(self) -> None:
        """
        Dispose the file system watcher and stop watching for events.

        Example:
            watcher = workspace.create_file_system_watcher("**/*.py")
            # ... use watcher ...
            watcher.dispose()  # Stop watching
        """
        if self._disposed:
            return

        self._disposed = True

        # Clear all handlers
        self._on_create_handlers.clear()
        self._on_change_handlers.clear()
        self._on_delete_handlers.clear()

        # Notify server to dispose watcher
        self.client._send_request(
            "workspace.disposeFileSystemWatcher",
            {"watcherId": self.watcher_id},
        )

    def __repr__(self) -> str:
        """String representation of the watcher."""
        return f"FileSystemWatcher(id={self.watcher_id!r}, pattern={self.glob_pattern!r})"

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically dispose."""
        self.dispose()
