"""
Webview API for creating and managing VS Code webview panels.
"""

from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

if TYPE_CHECKING:
    from .client import VSCodeClient


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
        self._message_handlers: list[Callable[[Any], None]] = []
        self._dispose_handlers: list[Callable[[], None]] = []
        self._view_state_handlers: list[Callable[[dict], None]] = []
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

        # Set up global subscription if not already active
        if not self._subscription_active:
            self._setup_message_subscription()
            self._subscription_active = True

        # Return unsubscribe function
        def unsubscribe():
            if handler in self._message_handlers:
                self._message_handlers.remove(handler)

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

        # Set up global subscription if not already active
        if not self._dispose_subscription_active:
            self._setup_dispose_subscription()
            self._dispose_subscription_active = True

        # Return unsubscribe function
        def unsubscribe():
            if handler in self._dispose_handlers:
                self._dispose_handlers.remove(handler)

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

        # Set up global subscription if not already active
        if not self._view_state_subscription_active:
            self._setup_view_state_subscription()
            self._view_state_subscription_active = True

        # Return unsubscribe function
        def unsubscribe():
            if handler in self._view_state_handlers:
                self._view_state_handlers.remove(handler)

        return unsubscribe

    def _setup_message_subscription(self) -> None:
        """Set up the global webview message event subscription."""

        def global_handler(event):
            # Filter messages for this specific panel
            # event is the data dict with 'id' and 'message' keys
            if event.get("id") == self._id:
                message = event["message"]
                # Call all registered handlers
                for handler in self._message_handlers[:]:
                    try:
                        handler(message)
                    except Exception as e:
                        print(f"Error in webview message handler: {e}")

        self._client.subscribe("webview.onDidReceiveMessage", global_handler)

    def _setup_dispose_subscription(self) -> None:
        """Set up the global webview disposal event subscription."""

        def global_handler(event):
            # Filter disposal events for this specific panel
            if event.get("id") == self._id:
                # Mark as disposed
                self._disposed = True
                # Call all registered dispose handlers
                for handler in self._dispose_handlers[:]:
                    try:
                        handler()
                    except Exception as e:
                        print(f"Error in webview dispose handler: {e}")
                # Clear handlers after calling them
                self._dispose_handlers.clear()

        self._client.subscribe("webview.onDidDispose", global_handler)

    def _setup_view_state_subscription(self) -> None:
        """Set up the global webview view state change event subscription."""

        def global_handler(event):
            # Filter events for this specific panel
            if event.get("id") == self._id:
                state = {
                    "visible": event.get("visible", False),
                    "active": event.get("active", False)
                }
                # Call all registered view state handlers
                for handler in self._view_state_handlers[:]:
                    try:
                        handler(state)
                    except Exception as e:
                        print(f"Error in webview view state handler: {e}")

        self._client.subscribe("webview.onDidChangeViewState", global_handler)

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
