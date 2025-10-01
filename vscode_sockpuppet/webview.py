"""
Webview API for creating and managing VS Code webview panels.
"""

from typing import TYPE_CHECKING, Optional, Any, Dict

if TYPE_CHECKING:
    from .client import VSCodeClient


class WebviewPanel:
    """
    Represents a VS Code webview panel.
    
    A webview panel displays custom HTML content in a VS Code editor tab.
    """
    
    def __init__(
        self, client: 'VSCodeClient', panel_id: str,
        view_type: str, title: str
    ):
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
        
        self._client._send_request("window.updateWebviewPanel", {
            "id": self._id,
            "html": html
        })
    
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
        self._client._send_request("window.updateWebviewPanel", {
            "id": self._id,
            "title": title
        })
    
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
        
        self._client._send_request("window.updateWebviewPanel", {
            "id": self._id,
            "iconPath": icon_path
        })
    
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
        
        self._client._send_request("window.postMessageToWebview", {
            "id": self._id,
            "message": message
        })
    
    def dispose(self) -> None:
        """
        Dispose of the webview panel, closing it in VS Code.
        
        After disposal, the panel cannot be used anymore.
        """
        if self._disposed:
            return
        
        self._client._send_request("window.disposeWebviewPanel", {
            "id": self._id
        })
        self._disposed = True
    
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
        local_resource_roots: Optional[list[str]] = None
    ):
        """
        Initialize webview options.
        
        Args:
            enable_scripts: Whether to enable JavaScript in the webview
            retain_context_when_hidden: Whether to keep the webview's context when hidden
            local_resource_roots: List of URI paths that the webview can load local resources from
        """
        self.enable_scripts = enable_scripts
        self.retain_context_when_hidden = retain_context_when_hidden
        self.local_resource_roots = local_resource_roots or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert options to a dictionary for JSON serialization."""
        return {
            "enableScripts": self.enable_scripts,
            "retainContextWhenHidden": self.retain_context_when_hidden,
            "localResourceRoots": self.local_resource_roots
        }
