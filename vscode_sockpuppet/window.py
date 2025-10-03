"""
Window operations for VS Code
"""

import uuid
from typing import TYPE_CHECKING, Optional

from .events import WindowEvents
from .window_types import (
    InputBoxOptions,
    OpenDialogOptions,
    QuickPickOptions,
    SaveDialogOptions,
    TextDocumentShowOptions,
)

if TYPE_CHECKING:
    from .client import VSCodeClient
    from .tabs import TabGroups
    from .terminal import Terminal
    from .webview import WebviewOptions, WebviewPanel


class Window:
    """VS Code window operations."""

    def __init__(self, client: "VSCodeClient"):
        self.client = client
        self._events = WindowEvents(client)
        self._tab_groups: Optional[TabGroups] = None

    # Event subscriptions (VS Code-style API)
    @property
    def tab_groups(self) -> "TabGroups":
        """Get the tab groups manager."""
        if self._tab_groups is None:
            from .tabs import TabGroups
            self._tab_groups = TabGroups(self.client)
        return self._tab_groups

    @property
    def on_did_change_active_text_editor(self):
        """Event fired when the active text editor changes."""
        return self._events.on_did_change_active_text_editor

    @property
    def on_did_change_text_editor_selection(self):
        """Event fired when the selection in an editor changes."""
        return self._events.on_did_change_text_editor_selection

    @property
    def on_did_change_visible_text_editors(self):
        """Event fired when the visible text editors change."""
        return self._events.on_did_change_visible_text_editors

    @property
    def on_did_open_terminal(self):
        """Event fired when a terminal is opened."""
        return self._events.on_did_open_terminal

    @property
    def on_did_close_terminal(self):
        """Event fired when a terminal is closed."""
        return self._events.on_did_close_terminal

    @property
    def on_did_change_terminal_state(self):
        """Event fired when a terminal's state changes."""
        return self._events.on_did_change_terminal_state

    @property
    def on_did_change_text_editor_visible_ranges(self):
        """Event fired when visible ranges in an editor change."""
        return self._events.on_did_change_text_editor_visible_ranges

    @property
    def on_did_change_text_editor_options(self):
        """Event fired when text editor options change."""
        return self._events.on_did_change_text_editor_options

    @property
    def on_did_change_text_editor_view_column(self):
        """Event fired when an editor's view column changes."""
        return self._events.on_did_change_text_editor_view_column

    @property
    def on_did_change_window_state(self):
        """Event fired when the window state changes (focus)."""
        return self._events.on_did_change_window_state

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
        self, items: list[str], options: Optional[QuickPickOptions] = None
    ) -> Optional[str]:
        """
        Show a quick pick menu.

        Args:
            items: The items to pick from
            options: Quick pick options (QuickPickOptions TypedDict)

        Returns:
            The selected item(s) or None if dismissed
        """
        return self.client._send_request(
            "window.showQuickPick", {"items": items, "options": options or {}}
        )

    def show_input_box(
        self, options: Optional[InputBoxOptions] = None
    ) -> Optional[str]:
        """
        Show an input box.

        Args:
            options: Input box options (InputBoxOptions TypedDict)

        Returns:
            The entered text or None if dismissed
        """
        return self.client._send_request(
            "window.showInputBox", {"options": options or {}}
        )

    def show_open_dialog(
        self, options: Optional[OpenDialogOptions] = None
    ) -> Optional[list[str]]:
        """
        Show a file open dialog to the user.

        Args:
            options: Dialog options (OpenDialogOptions TypedDict)

        Returns:
            List of selected file/folder URIs, or None if canceled

        Example:
            # Select a single Python file
            uris = client.window.show_open_dialog({
                'canSelectFiles': True,
                'canSelectFolders': False,
                'canSelectMany': False,
                'filters': {'Python': ['py']},
                'title': 'Select a Python file'
            })

            # Select multiple files or folders
            uris = client.window.show_open_dialog({
                'canSelectFiles': True,
                'canSelectFolders': True,
                'canSelectMany': True,
                'title': 'Select files or folders'
            })
        """
        result = self.client._send_request(
            "window.showOpenDialog", {"options": options or {}}
        )
        return result.get("uris") if result else None

    def show_save_dialog(
        self, options: Optional[SaveDialogOptions] = None
    ) -> Optional[str]:
        """
        Show a file save dialog to the user.

        Args:
            options: Dialog options (SaveDialogOptions TypedDict)

        Returns:
            Selected save location URI, or None if canceled

        Example:
            # Save a Python file
            uri = client.window.show_save_dialog({
                'filters': {'Python': ['py']},
                'title': 'Save Python file',
                'saveLabel': 'Save'
            })

            if uri:
                # Write to the selected location
                client.fs.write_text(uri, 'print("Hello")')
        """
        result = self.client._send_request(
            "window.showSaveDialog", {"options": options or {}}
        )
        return result.get("uri") if result else None

    def show_text_document(
        self, uri: str, options: Optional[TextDocumentShowOptions] = None
    ) -> dict:
        """
        Show a text document.

        Args:
            uri: The URI of the document to show
            options: View options (TextDocumentShowOptions TypedDict)

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
    ) -> "Terminal":
        """
        Create a terminal.

        Args:
            name: The name of the terminal
            shell_path: Path to the shell executable
            shell_args: Arguments for the shell

        Returns:
            Terminal instance for interacting with the terminal

        Example:
            # Create a simple terminal
            terminal = window.create_terminal(name="My Terminal")

            # Create with custom shell
            terminal = window.create_terminal(
                name="Bash",
                shell_path="/bin/bash"
            )

            # Use the terminal
            terminal.send_text("echo 'Hello!'")
            terminal.show()
        """
        from .terminal import Terminal

        result = self.client._send_request(
            "window.createTerminal",
            {
                "name": name,
                "shellPath": shell_path,
                "shellArgs": shell_args,
            },
        )
        return Terminal(self.client, result["terminalId"], name)

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
