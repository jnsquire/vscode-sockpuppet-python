"""
Window operations for VS Code
"""

import uuid
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .client import VSCodeClient
    from .webview import WebviewOptions, WebviewPanel


class Window:
    """VS Code window operations."""

    def __init__(self, client: "VSCodeClient"):
        self.client = client

    def show_information_message(
        self, message: str, *items: str
    ) -> Optional[str]:
        """
        Show an information message.

        Args:
            message: The message to show
            *items: Optional items to show as buttons

        Returns:
            The selected item or None if dismissed
        """
        return self.client._send_request(
            "window.showInformationMessage",
            {"message": message, "items": list(items)},
        )

    def show_warning_message(self, message: str, *items: str) -> Optional[str]:
        """
        Show a warning message.

        Args:
            message: The message to show
            *items: Optional items to show as buttons

        Returns:
            The selected item or None if dismissed
        """
        return self.client._send_request(
            "window.showWarningMessage",
            {"message": message, "items": list(items)},
        )

    def show_error_message(self, message: str, *items: str) -> Optional[str]:
        """
        Show an error message.

        Args:
            message: The message to show
            *items: Optional items to show as buttons

        Returns:
            The selected item or None if dismissed
        """
        return self.client._send_request(
            "window.showErrorMessage",
            {"message": message, "items": list(items)},
        )

    def show_quick_pick(
        self, items: list[str], options: Optional[dict] = None
    ) -> Optional[str]:
        """
        Show a quick pick menu.

        Args:
            items: The items to pick from
            options: Additional options (placeholder, canPickMany, etc.)

        Returns:
            The selected item(s) or None if dismissed
        """
        return self.client._send_request(
            "window.showQuickPick", {"items": items, "options": options or {}}
        )

    def show_input_box(self, options: Optional[dict] = None) -> Optional[str]:
        """
        Show an input box.

        Args:
            options: Input box options (prompt, placeholder, password, etc.)

        Returns:
            The entered text or None if dismissed
        """
        return self.client._send_request(
            "window.showInputBox", {"options": options or {}}
        )

    def show_text_document(
        self, uri: str, options: Optional[dict] = None
    ) -> dict:
        """
        Show a text document.

        Args:
            uri: The URI of the document to show
            options: View options (viewColumn, preserveFocus, etc.)

        Returns:
            Success status
        """
        return self.client._send_request(
            "window.showTextDocument", {"uri": uri, "options": options or {}}
        )

    def create_output_channel(
        self,
        name: str,
        text: Optional[str] = None,
        show: bool = False,
        preserve_focus: bool = True,
    ) -> dict:
        """
        Create an output channel.

        Args:
            name: The name of the output channel
            text: Optional text to append
            show: Whether to show the channel
            preserve_focus: Whether to preserve focus when showing

        Returns:
            Success status
        """
        return self.client._send_request(
            "window.createOutputChannel",
            {
                "name": name,
                "text": text,
                "show": show,
                "preserveFocus": preserve_focus,
            },
        )

    def create_terminal(
        self,
        name: Optional[str] = None,
        shell_path: Optional[str] = None,
        shell_args: Optional[list] = None,
        text: Optional[str] = None,
        show: bool = False,
        preserve_focus: bool = True,
        add_new_line: bool = True,
    ) -> dict:
        """
        Create a terminal.

        Args:
            name: The name of the terminal
            shell_path: Path to the shell executable
            shell_args: Arguments for the shell
            text: Optional text to send to the terminal
            show: Whether to show the terminal
            preserve_focus: Whether to preserve focus when showing
            add_new_line: Whether to add a new line after text

        Returns:
            Success status
        """
        return self.client._send_request(
            "window.createTerminal",
            {
                "name": name,
                "shellPath": shell_path,
                "shellArgs": shell_args,
                "text": text,
                "show": show,
                "preserveFocus": preserve_focus,
                "addNewLine": add_new_line,
            },
        )

    def set_status_bar_message(
        self, text: str, hide_after_timeout: Optional[int] = None
    ) -> dict:
        """
        Set a status bar message.

        Args:
            text: The message to show
            hide_after_timeout: Optional timeout in milliseconds

        Returns:
            Success status
        """
        return self.client._send_request(
            "window.setStatusBarMessage",
            {"text": text, "hideAfterTimeout": hide_after_timeout},
        )

    def create_webview_panel(
        self,
        title: str,
        html: str,
        view_type: Optional[str] = None,
        panel_id: Optional[str] = None,
        show_options: int = 1,
        options: Optional["WebviewOptions"] = None,
    ) -> "WebviewPanel":
        """
        Create a webview panel with custom HTML content.

        Args:
            title: The title of the webview panel
            html: The HTML content to display
            view_type: Identifier for the webview type (auto-generated if None)
            panel_id: Unique identifier for the panel (auto-generated if None)
            show_options: ViewColumn where to show (1=One, 2=Two, 3=Three)
            options: Webview configuration options

        Returns:
            The created WebviewPanel instance

        Example:
            with window.create_webview_panel(
                "My Panel",
                "<h1>Hello from Python!</h1>"
            ) as panel:
                # Panel will automatically dispose when exiting context
                panel.update_html("<h1>Updated content</h1>")
        """
        from .webview import WebviewOptions, WebviewPanel

        if panel_id is None:
            panel_id = str(uuid.uuid4())

        if view_type is None:
            view_type = f"sockpuppet.webview.{panel_id}"

        params = {
            "id": panel_id,
            "viewType": view_type,
            "title": title,
            "showOptions": show_options,
            "html": html,
        }

        if options:
            params["options"] = options.to_dict()
        else:
            # Default options
            params["options"] = WebviewOptions().to_dict()

        self.client._send_request("window.createWebviewPanel", params)

        return WebviewPanel(self.client, panel_id, view_type, title)
