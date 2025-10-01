"""
Status bar operations for VS Code
"""

import uuid
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .client import VSCodeClient


class StatusBarAlignment:
    """Status bar alignment options."""

    Left = "left"
    Right = "right"


class StatusBarItem:
    """Represents a status bar item."""

    def __init__(
        self,
        client: "VSCodeClient",
        id: str,
        alignment: str = StatusBarAlignment.Left,
        priority: Optional[int] = None,
    ):
        """
        Create a status bar item.

        Args:
            client: The VS Code client
            id: Unique identifier
            alignment: Alignment (left or right)
            priority: Priority (higher = more left)
        """
        self.client = client
        self.id = id
        self._text = ""
        self._tooltip: Optional[str] = None
        self._command: Optional[str] = None
        self._color: Optional[str] = None
        self._background_color: Optional[str] = None
        self._visible = False

        # Create on server side
        self.client._send_request(
            "window.createStatusBarItem",
            {"id": id, "alignment": alignment, "priority": priority},
        )

    @property
    def text(self) -> str:
        """Get the text of the status bar item."""
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        """Set the text of the status bar item."""
        self._text = value
        self._update()

    @property
    def tooltip(self) -> Optional[str]:
        """Get the tooltip of the status bar item."""
        return self._tooltip

    @tooltip.setter
    def tooltip(self, value: Optional[str]) -> None:
        """Set the tooltip of the status bar item."""
        self._tooltip = value
        self._update()

    @property
    def command(self) -> Optional[str]:
        """Get the command of the status bar item."""
        return self._command

    @command.setter
    def command(self, value: Optional[str]) -> None:
        """Set the command to execute when clicked."""
        self._command = value
        self._update()

    @property
    def color(self) -> Optional[str]:
        """Get the text color."""
        return self._color

    @color.setter
    def color(self, value: Optional[str]) -> None:
        """Set the text color."""
        self._color = value
        self._update()

    @property
    def background_color(self) -> Optional[str]:
        """Get the background color."""
        return self._background_color

    @background_color.setter
    def background_color(self, value: Optional[str]) -> None:
        """Set the background color (theme color name)."""
        self._background_color = value
        self._update()

    def show(self) -> None:
        """Show the status bar item."""
        self._visible = True
        self._update()

    def hide(self) -> None:
        """Hide the status bar item."""
        self._visible = False
        self._update()

    def dispose(self) -> None:
        """Dispose the status bar item."""
        self.client._send_request(
            "window.disposeStatusBarItem", {"id": self.id}
        )

    def _update(self) -> None:
        """Update the status bar item on the server."""
        params = {
            "id": self.id,
            "text": self._text,
            "show": self._visible,
        }
        if self._tooltip is not None:
            params["tooltip"] = self._tooltip
        if self._command is not None:
            params["command"] = self._command
        if self._color is not None:
            params["color"] = self._color
        if self._background_color is not None:
            params["backgroundColor"] = self._background_color

        self.client._send_request("window.updateStatusBarItem", params)


def create_status_bar_item(
    client: "VSCodeClient",
    alignment: str = StatusBarAlignment.Left,
    priority: Optional[int] = None,
) -> StatusBarItem:
    """
    Create a status bar item.

    Args:
        client: The VS Code client
        alignment: Alignment (left or right)
        priority: Priority (higher = more left)

    Returns:
        A new status bar item
    """
    item_id = str(uuid.uuid4())
    return StatusBarItem(client, item_id, alignment, priority)
