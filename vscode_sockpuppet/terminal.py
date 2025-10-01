"""
Terminal operations for VS Code
"""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .client import VSCodeClient


class Terminal:
    """VS Code terminal instance."""

    def __init__(
        self,
        client: "VSCodeClient",
        terminal_id: str,
        name: Optional[str] = None,
    ):
        """
        Initialize a Terminal instance.

        Args:
            client: The VSCodeClient instance
            terminal_id: Unique identifier for this terminal
            name: Optional name of the terminal
        """
        self.client = client
        self.terminal_id = terminal_id
        self.name = name

    def send_text(self, text: str, add_new_line: bool = True) -> dict:
        """
        Send text to the terminal.

        Args:
            text: Text to send to the terminal
            add_new_line: Whether to add a new line after the text

        Returns:
            Success status

        Example:
            terminal.send_text("echo 'Hello, World!'")
            terminal.send_text("cd /path/to/dir", add_new_line=True)
        """
        return self.client._send_request(
            "terminal.sendText",
            {
                "terminalId": self.terminal_id,
                "text": text,
                "addNewLine": add_new_line,
            },
        )

    def show(self, preserve_focus: bool = True) -> dict:
        """
        Show the terminal in the UI.

        Args:
            preserve_focus: If true, the terminal will not take focus

        Returns:
            Success status

        Example:
            terminal.show(preserve_focus=False)  # Show and focus
            terminal.show()  # Show without taking focus
        """
        return self.client._send_request(
            "terminal.show",
            {
                "terminalId": self.terminal_id,
                "preserveFocus": preserve_focus,
            },
        )

    def hide(self) -> dict:
        """
        Hide the terminal from the UI.

        Returns:
            Success status

        Example:
            terminal.hide()
        """
        return self.client._send_request(
            "terminal.hide",
            {"terminalId": self.terminal_id},
        )

    def dispose(self) -> dict:
        """
        Dispose the terminal, closing it permanently.

        Returns:
            Success status

        Example:
            terminal.dispose()
        """
        return self.client._send_request(
            "terminal.dispose",
            {"terminalId": self.terminal_id},
        )

    def __repr__(self) -> str:
        """String representation of the terminal."""
        name_str = f", name={self.name!r}" if self.name else ""
        return f"Terminal(id={self.terminal_id!r}{name_str})"
