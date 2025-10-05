"""
Webview API for creating and managing VS Code webview panels.
"""

from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

from .events import WebviewMessageEvent, WebviewViewStateEvent

if TYPE_CHECKING:
    from .client import VSCodeClient


# Global registries so we create at most one "webview.onDidReceiveMessage"
# subscription per VSCodeClient and dispatch messages to the correct
# WebviewPanel instance by id.
#
# _global_message_registry: client -> { panel_id: WebviewPanel }
_global_message_registry: Dict["VSCodeClient", Dict[str, "WebviewPanel"]] = {}
# _global_message_handler_ref: client -> handler callable (so we can unsubscribe)
_global_message_handler_ref: Dict["VSCodeClient", Callable[[], None]] = {}


def _unregister_panel_from_global(client: "VSCodeClient", panel_id: str) -> None:
    """Remove a panel from the global registry and unsubscribe the global
    handler for the client if no panels remain.
    """
    try:
        panels = _global_message_registry.get(client)
        if not panels:
            return

        if panel_id in panels:
            del panels[panel_id]

        # If no panels remain for this client, remove registry and
        # unsubscribe the global handler.
        if not panels:
            # delete registry entry
            del _global_message_registry[client]
            # unsubscribe global handler if present
            handler = _global_message_handler_ref.pop(client, None)
            if handler is not None:
                try:
                    # handler here is the unsubscribe callable
                    handler()
                except Exception:
                    pass
    except Exception as e:
        print(f"Error unregistering webview panel from global registry: {e}")


# Dispose event global registries
_global_dispose_registry: Dict["VSCodeClient", Dict[str, "WebviewPanel"]] = {}
_global_dispose_handler_ref: Dict["VSCodeClient", Callable[[], None]] = {}


def _unregister_dispose_panel_from_global(client: "VSCodeClient", panel_id: str) -> None:
    """Remove a panel from the global dispose registry and unsubscribe the
    global dispose handler for the client if no panels remain.
    """
    try:
        panels = _global_dispose_registry.get(client)
        if not panels:
            return

        if panel_id in panels:
            del panels[panel_id]

        if not panels:
            del _global_dispose_registry[client]
            handler = _global_dispose_handler_ref.pop(client, None)
            if handler is not None:
                try:
                    handler()
                except Exception:
                    pass
    except Exception as e:
        print(f"Error unregistering webview dispose panel: {e}")


# View state event global registries
_global_viewstate_registry: Dict["VSCodeClient", Dict[str, "WebviewPanel"]] = {}
_global_viewstate_handler_ref: Dict["VSCodeClient", Callable[[], None]] = {}


def _unregister_viewstate_panel_from_global(client: "VSCodeClient", panel_id: str) -> None:
    """Remove a panel from the global view-state registry and unsubscribe the
    handler for the client if no panels remain.
    """
    try:
        panels = _global_viewstate_registry.get(client)
        if not panels:
            return

        if panel_id in panels:
            del panels[panel_id]

        if not panels:
            del _global_viewstate_registry[client]
            handler = _global_viewstate_handler_ref.pop(client, None)
            if handler is not None:
                try:
                    handler()
                except Exception:
                    pass
    except Exception as e:
        print(f"Error unregistering webview viewstate panel: {e}")


class WebviewPanel:
    """
    Represents a VS Code webview panel.

    A webview panel displays custom HTML content in a VS Code editor tab.
    """

    def __init__(self, client: "VSCodeClient", panel_id: str, view_type: str, title: str):
        """
        Initialize a WebviewPanel.

        Args:
            client: The VS Code client instance
            panel_id: Unique identifier for this panel
            view_type: Identifier for the webview type
            title: Title displayed in the editor tab
        """
        self._client = client
        self._id = panel_id
        self._view_type = view_type
        self._title = title
        self._disposed = False
        # Panel-level message handlers receive the 'message' payload (Any)
        self._message_handlers: list[Callable[[Any], None]] = []
        # Dispose handlers receive no arguments
        self._dispose_handlers: list[Callable[[], None]] = []
        # View state handlers receive the small state dict
        self._view_state_handlers: list[Callable[[WebviewViewStateEvent], None]] = []
        self._subscription_active = False
        self._dispose_subscription_active = False
        self._view_state_subscription_active = False

    @property
    def id(self) -> str:
        """Get the unique identifier for this panel."""
        return self._id

    @property
    def view_type(self) -> str:
        """Get the view type identifier."""
        return self._view_type

    @property
    def title(self) -> str:
        """Get the panel title."""
        return self._title

    @property
    def disposed(self) -> bool:
        """Check if the panel has been disposed."""
        return self._disposed

    def update_html(self, html: str) -> None:
        """
        Update the HTML content of the webview.

        Args:
            html: The new HTML content to display

        Raises:
            RuntimeError: If the panel has been disposed
        """
        if self._disposed:
            raise RuntimeError("Cannot update disposed webview panel")

        self._client._send_request("window.updateWebviewPanel", {"id": self._id, "html": html})

    def update_title(self, title: str) -> None:
        """
        Update the title of the webview panel.

        Args:
            title: The new title to display

        Raises:
            RuntimeError: If the panel has been disposed
        """
        if self._disposed:
            raise RuntimeError("Cannot update disposed webview panel")

        self._title = title
        self._client._send_request("window.updateWebviewPanel", {"id": self._id, "title": title})

    def update_icon(self, icon_path: str) -> None:
        """
        Update the icon of the webview panel.

        Args:
            icon_path: Absolute path to the icon file

        Raises:
            RuntimeError: If the panel has been disposed
        """
        if self._disposed:
            raise RuntimeError("Cannot update disposed webview panel")

        self._client._send_request(
            "window.updateWebviewPanel",
            {"id": self._id, "iconPath": icon_path},
        )

    def post_message(self, message: Any) -> None:
        """
        Post a message to the webview's JavaScript context.

        The message can be received in the webview's JavaScript using:
        window.addEventListener('message', event => {
            const message = event.data;
            // Handle message
        });

        Args:
            message: The message to send (must be JSON-serializable)

        Raises:
            RuntimeError: If the panel has been disposed
        """
        if self._disposed:
            raise RuntimeError("Cannot post message to disposed webview panel")

        self._client._send_request(
            "window.postMessageToWebview", {"id": self._id, "message": message}
        )

    def as_webview_uri(self, local_uri: str) -> str:
        """
        Convert a local file URI to a webview URI.

        Webviews cannot directly load resources from the workspace or local
        file system using file: URIs. This method converts a local file:
        URI into a URI that can be used inside the webview to load the same
        resource.

        The local resource must be in a directory listed in
        localResourceRoots when creating the webview, otherwise it cannot
        be loaded.

        Args:
            local_uri: Local file URI (e.g., 'file:///path/to/file.png')
                or absolute file path

        Returns:
            Webview URI that can be used in webview HTML

        Raises:
            RuntimeError: If the panel has been disposed

        Example:
            # Convert a local file to webview URI
            img_uri = panel.as_webview_uri('file:///path/to/image.png')

            # Use in HTML
            html = f'<img src="{img_uri}">'
            panel.update_html(html)
        """
        if self._disposed:
            raise RuntimeError("Cannot convert URI for disposed webview panel")

        # Ensure URI is in proper format
        if not local_uri.startswith("file://"):
            # Convert absolute path to file URI
            normalized_path = local_uri.replace("\\", "/")
            local_uri = f"file://{normalized_path}"

        result = self._client._send_request(
            "window.asWebviewUri", {"id": self._id, "uri": local_uri}
        )
        return result["webviewUri"]

    def on_did_receive_message(self, handler: Callable[[Any], None]) -> Callable[[], None]:
        """
        Subscribe to messages posted from the webview's JavaScript.

        The handler will be called whenever the webview posts a message using:
        const vscode = acquireVsCodeApi();
        vscode.postMessage({ your: 'data' });

        Args:
            handler: Callback function that receives the message data

        Returns:
            A function that can be called to unsubscribe the handler

        Example:
            def handle_message(message):
                print(f"Received: {message}")

            # Subscribe
            unsubscribe = panel.on_did_receive_message(handle_message)

            # Later, to unsubscribe
            unsubscribe()
        """
        if self._disposed:
            raise RuntimeError("Cannot subscribe to disposed webview panel")

        # Add handler to our list
        self._message_handlers.append(handler)

        # Set up (or register with) global subscription for this client
        if not self._subscription_active:
            self._setup_message_subscription()
            self._subscription_active = True

        # Return unsubscribe function
        def unsubscribe():
            if handler in self._message_handlers:
                self._message_handlers.remove(handler)

            # If no message handlers left for this panel, remove panel from
            # registry so it no longer receives dispatched messages.
            if not self._message_handlers:
                _unregister_panel_from_global(self._client, self._id)

        return unsubscribe

    def on_did_dispose(self, handler: Callable[[], None]) -> Callable[[], None]:
        """
        Subscribe to the panel disposal event.

        The handler will be called when the webview panel is disposed,
        either by calling dispose() or when the user closes the panel.

        Args:
            handler: Callback function called when the panel is disposed

        Returns:
            A function that can be called to unsubscribe the handler

        Example::

            def on_dispose():
                print("Webview was closed")

            # Subscribe
            unsubscribe = panel.on_did_dispose(on_dispose)

            # Later, to unsubscribe
            unsubscribe()
        """
        if self._disposed:
            # Already disposed, call handler immediately
            handler()
            return lambda: None

        # Add handler to our list
        self._dispose_handlers.append(handler)

        # Register with global dispose dispatcher for this client
        if not self._dispose_subscription_active:
            self._setup_dispose_subscription()
            self._dispose_subscription_active = True

        # Return unsubscribe function
        def unsubscribe():
            if handler in self._dispose_handlers:
                self._dispose_handlers.remove(handler)

            # If no dispose handlers remain for this panel, remove it from
            # the global dispose registry.
            if not self._dispose_handlers:
                _unregister_dispose_panel_from_global(self._client, self._id)

        return unsubscribe

    def on_did_change_view_state(self, handler: Callable[[dict], None]) -> Callable[[], None]:
        """
        Subscribe to view state change events.

        The handler will be called when the panel's visibility or active
        state changes (e.g., when the user switches tabs or focuses the panel).

        Args:
            handler: Callback function that receives a dict with 'visible' and 'active' keys

        Returns:
            A function that can be called to unsubscribe the handler

        Example::

            def on_view_state_change(state):
                print(f"Visible: {state['visible']}, Active: {state['active']}")
                if state['active']:
                    print("Panel is now in focus!")

            # Subscribe
            unsubscribe = panel.on_did_change_view_state(on_view_state_change)

            # Later, to unsubscribe
            unsubscribe()
        """
        if self._disposed:
            return lambda: None

        # Add handler to our list
        self._view_state_handlers.append(handler)

        # Register with global view-state dispatcher for this client
        if not self._view_state_subscription_active:
            self._setup_view_state_subscription()
            self._view_state_subscription_active = True

        # Return unsubscribe function
        def unsubscribe():
            if handler in self._view_state_handlers:
                self._view_state_handlers.remove(handler)

            if not self._view_state_handlers:
                _unregister_viewstate_panel_from_global(self._client, self._id)

        return unsubscribe

    def _setup_message_subscription(self) -> None:
        """Register this panel with the global dispatcher for this client.

        Instead of creating a new subscription per panel, we maintain a single
        event subscription per VSCodeClient and dispatch incoming messages to
        the correct panel based on the event's 'id' field.
        """

        client = self._client

        # Ensure registry for this client exists
        panels = _global_message_registry.setdefault(client, {})
        panels[self._id] = self

        # If we don't yet have a global handler installed for this client,
        # create and subscribe it.
        if client not in _global_message_handler_ref:

            def _global_handler(event: WebviewMessageEvent):
                # event expected to be a dict with 'id' and 'message'
                try:
                    panel_id = event.get("id")
                    if not panel_id:
                        return
                    panels_map = _global_message_registry.get(client)
                    if not panels_map:
                        return
                    panel = panels_map.get(panel_id)
                    if not panel:
                        return
                    message = event.get("message")
                    for handler in panel._message_handlers[:]:
                        try:
                            handler(message)
                        except Exception as e:
                            print(f"Error in webview message handler: {e}")
                except Exception as e:
                    print(f"Error in global webview message dispatch: {e}")

            # keep reference so we can unsubscribe later if needed
            # store unsubscribe callable returned by client.add_event_listener
            _global_message_handler_ref[client] = client.add_event_listener(
                "webview.onDidReceiveMessage", _global_handler
            )

    def _setup_dispose_subscription(self) -> None:
        """Register this panel with a global dispose dispatcher for the client."""

        client = self._client
        panels = _global_dispose_registry.setdefault(client, {})
        panels[self._id] = self

        if client not in _global_dispose_handler_ref:

            def _global_dispose_handler(event):
                try:
                    panel_id = event.get("id")
                    if not panel_id:
                        return
                    panels_map = _global_dispose_registry.get(client)
                    if not panels_map:
                        return
                    panel = panels_map.get(panel_id)
                    if not panel:
                        return
                    # Mark as disposed and call handlers
                    panel._disposed = True
                    for handler in panel._dispose_handlers[:]:
                        try:
                            handler()
                        except Exception as e:
                            print(f"Error in webview dispose handler: {e}")
                    panel._dispose_handlers.clear()
                except Exception as e:
                    print(f"Error in global webview dispose dispatch: {e}")

            _global_dispose_handler_ref[client] = client.add_event_listener(
                "webview.onDidDispose", _global_dispose_handler
            )

    def _setup_view_state_subscription(self) -> None:
        """Register this panel with a global view-state dispatcher for the client."""

        client = self._client
        panels = _global_viewstate_registry.setdefault(client, {})
        panels[self._id] = self

        if client not in _global_viewstate_handler_ref:

            def _global_viewstate_handler(event):
                try:
                    panel_id = event.get("id")
                    if not panel_id:
                        return
                    panels_map = _global_viewstate_registry.get(client)
                    if not panels_map:
                        return
                    panel = panels_map.get(panel_id)
                    if not panel:
                        return
                    state = {
                        "visible": event.get("visible", False),
                        "active": event.get("active", False),
                    }
                    for handler in panel._view_state_handlers[:]:
                        try:
                            handler(state)
                        except Exception as e:
                            print(f"Error in webview view state handler: {e}")
                except Exception as e:
                    print(f"Error in global webview viewstate dispatch: {e}")

            _global_viewstate_handler_ref[client] = client.add_event_listener(
                "webview.onDidChangeViewState", _global_viewstate_handler
            )

    def dispose(self) -> None:
        """
        Dispose of the webview panel, closing it in VS Code.

        After disposal, the panel cannot be used anymore.
        This will trigger any registered on_did_dispose handlers.
        """
        if self._disposed:
            return

        self._client._send_request("window.disposeWebviewPanel", {"id": self._id})
        self._disposed = True

        # Call dispose handlers
        for handler in self._dispose_handlers[:]:
            try:
                handler()
            except Exception as e:
                print(f"Error in webview dispose handler: {e}")
        # Clear handlers after calling them
        self._dispose_handlers.clear()

        # Remove from global message registry so the dispatcher no longer
        # attempts to route messages to this panel.
        _unregister_panel_from_global(self._client, self._id)
        # Also remove from dispose and viewstate registries so client-level
        # handlers can be unsubscribed when no panels remain.
        _unregister_dispose_panel_from_global(self._client, self._id)
        _unregister_viewstate_panel_from_global(self._client, self._id)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically dispose the panel."""
        self.dispose()
        return False


class WebviewOptions:
    """Options for configuring a webview panel."""

    def __init__(
        self,
        enable_scripts: bool = True,
        retain_context_when_hidden: bool = False,
        local_resource_roots: Optional[list[str]] = None,
    ):
        """
        Initialize webview options.

        Args:
            enable_scripts: Whether to enable JavaScript in the webview
            retain_context_when_hidden: Whether to keep the webview's
                context when hidden
            local_resource_roots: List of URI paths that the webview can
                load local resources from
        """
        self.enable_scripts = enable_scripts
        self.retain_context_when_hidden = retain_context_when_hidden
        self.local_resource_roots = local_resource_roots or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert options to a dictionary for JSON serialization."""
        return {
            "enableScripts": self.enable_scripts,
            "retainContextWhenHidden": self.retain_context_when_hidden,
            "localResourceRoots": self.local_resource_roots,
        }
