"""
Main client for communicating with VS Code extension
"""

import json
import os
import socket
import tempfile
import threading
from contextlib import contextmanager
from typing import Any, Callable, Dict, Literal, Optional, Union, overload

from .diagnostics import Languages
from .editor import Editor
from .events import EventEmitter
from .fs import FileSystem
from .language_model import LanguageModel
from .window import Window
from .workspace import Workspace


class VSCodeClient:
    """Main client for interacting with VS Code via Sockpuppet extension."""

    def __init__(self, pipe_path: Optional[str] = None):
        """
        Initialize the VS Code client.

        Args:
            pipe_path: Path to the named pipe/socket.
                      If None, checks VSCODE_SOCKPUPPET_PIPE environment
                      variable, then falls back to platform default.
        """
        if pipe_path is None:
            # First try environment variable (set by other extensions)
            pipe_path = os.environ.get("VSCODE_SOCKPUPPET_PIPE")

        if pipe_path is None:
            # Use platform-specific default paths
            if os.name == "nt":  # Windows
                pipe_path = r"\\.\pipe\vscode-sockpuppet"
            else:  # Unix/Linux/Mac
                pipe_path = os.path.join(tempfile.gettempdir(), "vscode-sockpuppet.sock")

        self.pipe_path = pipe_path
        self.sock: Optional[Union[socket.socket, Any]] = None
        self._request_id = 0
        self._lock = threading.Lock()
        self._buffer = ""
        # Emitters map: event name -> EventEmitter
        self._emitters: Dict[str, EventEmitter] = {}
        self._event_thread: Optional[threading.Thread] = None
        self._running = False
        self._session_listeners: list[Callable[[str, Dict[str, Any]], None]] = []
        self._session_listener_lock = threading.Lock()

        # API namespaces
        self.window = Window(self)
        self.workspace = Workspace(self)
        self.editor = Editor(self)
        self.fs = FileSystem(self)
        self.languages = Languages(self)
        self.lm = LanguageModel(self)

    def connect(self) -> None:
        """Connect to the VS Code extension via named pipe/socket."""
        if os.name == "nt":  # Windows named pipe
            try:
                # On Windows, use standard file operations for named pipes
                # Python 3 can open named pipes like regular files
                import time

                # Wait for pipe to be available (retry for up to 5 seconds)
                max_retries = 50
                retry_delay = 0.1

                for attempt in range(max_retries):
                    try:
                        # Open named pipe with read/write binary mode
                        self.sock = open(self.pipe_path, "r+b", buffering=0)
                        break
                    except FileNotFoundError as e:
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                        else:
                            raise ConnectionError(
                                f"Named pipe not found: {self.pipe_path}. "
                                "Make sure VS Code extension is running."
                            ) from e
                    except PermissionError as e:
                        raise ConnectionError(f"Permission denied accessing pipe: {e}") from e
            except Exception as e:
                if not isinstance(e, ConnectionError):
                    raise ConnectionError(
                        f"Could not connect to VS Code. Make sure extension is running. Error: {e}"
                    ) from e
                raise
        else:  # Unix domain socket
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                self.sock.connect(self.pipe_path)
            except Exception as e:
                raise ConnectionError(
                    f"Could not connect to VS Code. Make sure extension is running. Error: {e}"
                ) from e

    def disconnect(self) -> None:
        """Disconnect from the VS Code extension."""
        if self.sock:
            try:
                if hasattr(self.sock, "close"):
                    self.sock.close()
            except Exception:
                pass
            self.sock = None
        self._notify_session_listeners("event-loop-stopped", {})

    def is_connected(self) -> bool:
        """Check if connected to VS Code."""
        return self.sock is not None

    def _send_request(self, method: str, params: Optional[dict] = None) -> Any:
        """
        Send a request to VS Code and wait for response.

        Args:
            method: The method to call
            params: Parameters for the method

        Returns:
            The result from VS Code

        Raises:
            ConnectionError: If not connected to VS Code
            RuntimeError: If the request fails
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to VS Code. Call connect() first.")

        with self._lock:
            self._request_id += 1
            request_id = self._request_id

        request = {"id": request_id, "method": method, "params": params or {}}

        # Send request with newline delimiter
        message = json.dumps(request) + "\n"
        message_bytes = message.encode("utf-8")

        if os.name == "nt":
            # Windows named pipe opened as file
            self.sock.write(message_bytes)  # type: ignore
            self.sock.flush()  # type: ignore
        else:
            # Unix socket
            self.sock.sendall(message_bytes)  # type: ignore

        # Receive response
        while True:
            if os.name == "nt":
                # Read from Windows named pipe
                chunk_bytes = self.sock.read(4096)  # type: ignore
                if not chunk_bytes:
                    raise ConnectionError("Connection closed by VS Code")
                chunk = chunk_bytes.decode("utf-8")
            else:
                # Read from Unix socket
                chunk_bytes = self.sock.recv(4096)  # type: ignore
                if not chunk_bytes:
                    raise ConnectionError("Connection closed by VS Code")
                chunk = chunk_bytes.decode("utf-8")

            self._buffer += chunk

            # Look for complete message (newline-delimited)
            if "\n" in self._buffer:
                lines = self._buffer.split("\n")
                self._buffer = "\n".join(lines[1:])
                response_str = lines[0]
                break

        response = json.loads(response_str)

        if "error" in response:
            raise RuntimeError(f"VS Code error: {response['error']}")

        return response.get("result")

    def execute_command(self, command: str, *args) -> Any:
        """
        Execute a VS Code command.

        Args:
            command: The command identifier
            *args: Arguments to pass to the command

        Returns:
            The result of the command execution
        """
        return self._send_request(
            "commands.executeCommand", {"command": command, "args": list(args)}
        )

    def get_commands(self, filter_internal: bool = False) -> list[str]:
        """
        Get all available VS Code commands.

        Args:
            filter_internal: Whether to filter internal commands

        Returns:
            List of command identifiers
        """
        return self._send_request("commands.getCommands", {"filterInternal": filter_internal})

    # Strongly-typed subscribe overloads for common events
    @overload
    def subscribe(
        self,
        event: Literal["webview.onDidReceiveMessage"],
        handler: Callable[[Dict[str, Any]], None],
    ) -> None:  # pragma: no cover - typing only
        ...

    @overload
    def subscribe(
        self, event: Literal["webview.onDidDispose"], handler: Callable[[Dict[str, Any]], None]
    ) -> None:  # pragma: no cover - typing only
        ...

    @overload
    def subscribe(
        self,
        event: Literal["webview.onDidChangeViewState"],
        handler: Callable[[Dict[str, Any]], None],
    ) -> None:  # pragma: no cover - typing only
        ...

    @overload
    def subscribe(
        self, event: str, handler: Callable[[Any], None]
    ) -> None:  # pragma: no cover - typing only
        ...

    def subscribe(self, event: str, handler: Callable[[Any], None]) -> None:
        """
        Subscribe to a VS Code event.

        Args:
            event: Event name (e.g., 'workspace.onDidSaveTextDocument')
            handler: Callback function to handle the event data

        Available events:
            - workspace.onDidOpenTextDocument
            - workspace.onDidCloseTextDocument
            - workspace.onDidSaveTextDocument
            - workspace.onDidChangeTextDocument
            - window.onDidChangeActiveTextEditor
            - window.onDidChangeTextEditorSelection
            - window.onDidChangeVisibleTextEditors
            - window.onDidOpenTerminal
            - window.onDidCloseTerminal
            - workspace.onDidChangeWorkspaceFolders
            - workspace.onDidChangeConfiguration
        """
        # Start event listener thread if not running
        if not self._running and self._event_thread is None:
            self._running = True
            self._event_thread = threading.Thread(target=self._event_loop, daemon=True)
            self._event_thread.start()

        if event not in self._emitters:
            # create emitter that subscribes/unsubscribes on first add / last remove
            def _on_first_add() -> None:
                try:
                    self._send_request("events.subscribe", {"event": event})
                finally:
                    self._notify_session_listeners("subscription-ack", {"event": event})

            def _on_no_listeners() -> None:
                try:
                    self._send_request("events.unsubscribe", {"event": event})
                finally:
                    self._notify_session_listeners("unsubscription-ack", {"event": event})

            self._emitters[event] = EventEmitter(
                on_first_add=_on_first_add, on_no_listeners=_on_no_listeners
            )

        # register handler
        self._emitters[event].event(handler)

    def unsubscribe(self, event: str, handler: Optional[Callable] = None) -> None:
        """
        Unsubscribe from a VS Code event.

        Args:
            event: Event name
            handler: Specific handler to remove, or None to remove all
        """
        if event not in self._emitters:
            return

        emitter = self._emitters[event]

        if handler is None:
            # Remove all handlers and explicitly unsubscribe from server
            try:
                # avoid double-unsubscribe race by directly sending and dropping emitter
                self._send_request("events.unsubscribe", {"event": event})
            finally:
                del self._emitters[event]
        else:
            emitter.remove(handler)
            # If emitter has no listeners, remove it from map (on_no_listeners already sent ack)
            if not emitter.has_listeners():
                if event in self._emitters:
                    del self._emitters[event]

    def get_subscriptions(self) -> list[str]:
        """
        Get list of currently subscribed events.

        Returns:
            List of event names
        """
        return self._send_request("events.listSubscriptions")

    def _event_loop(self) -> None:
        """Background thread that listens for events from VS Code."""
        self._notify_session_listeners("event-loop-started", {})
        while self._running:
            try:
                if os.name == "nt":
                    # Read from Windows named pipe
                    chunk_bytes = self.sock.read(4096)  # type: ignore
                    if not chunk_bytes:
                        break
                    chunk = chunk_bytes.decode("utf-8")
                else:
                    # Read from Unix socket
                    chunk_bytes = self.sock.recv(4096)  # type: ignore
                    if not chunk_bytes:
                        break
                    chunk = chunk_bytes.decode("utf-8")

                self._buffer += chunk

                # Process complete messages
                while "\n" in self._buffer:
                    line, self._buffer = self._buffer.split("\n", 1)
                    if line.strip():
                        message = json.loads(line)

                        # Check if it's an event (not a response)
                        if message.get("type") == "event":
                            event_name = message.get("event")
                            event_data = message.get("data")

                            # Dispatch via emitter if present
                            if event_name in self._emitters:
                                try:
                                    self._emitters[event_name].fire(event_data)
                                except Exception as e:
                                    print(f"Error dispatching event {event_name}: {e}")

                                self._notify_session_listeners(
                                    "event-dispatched",
                                    {"event": event_name, "data": event_data},
                                )

            except Exception as e:
                if self._running:
                    print(f"Error in event loop: {e}")
                break
        self._notify_session_listeners("event-loop-stopped", {})

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self._running = False
        if self._event_thread:
            self._event_thread.join(timeout=1.0)
        self.disconnect()

    def add_session_listener(
        self, listener: Callable[[str, Dict[str, Any]], None]
    ) -> Callable[[], None]:
        """Register a listener for session state notifications."""

        with self._session_listener_lock:
            self._session_listeners.append(listener)

        def _remove() -> None:
            self.remove_session_listener(listener)

        return _remove

    def remove_session_listener(self, listener: Callable[[str, Dict[str, Any]], None]) -> None:
        """Remove a previously registered session listener."""

        with self._session_listener_lock:
            if listener in self._session_listeners:
                self._session_listeners.remove(listener)

    def _notify_session_listeners(self, state: str, payload: Dict[str, Any]) -> None:
        with self._session_listener_lock:
            listeners = list(self._session_listeners)

        for listener in listeners:
            try:
                listener(state, payload)
            except Exception as exc:  # pragma: no cover - diagnostics only
                print(f"Error in session listener for {state}: {exc}")

    @contextmanager
    def session_listener(self, listener: Callable[[str, Dict[str, Any]], None]) -> Any:
        """Context manager to automatically add and remove a session listener."""

        remove = self.add_session_listener(listener)
        try:
            yield listener
        finally:
            remove()

    @contextmanager
    def subscription(self, event: str, handler: Callable[[Any], None]) -> Any:
        """Context manager that registers a subscription and ensures it's removed.

        Example:

            with client.subscription('webview.onDidReceiveMessage', handler):
                # handler will receive events here
                ...
        """

        # Subscribe and yield control to the caller
        self.subscribe(event, handler)
        try:
            yield handler
        finally:
            # Best-effort unsubscribe
            try:
                self.unsubscribe(event, handler)
            except Exception:
                pass
