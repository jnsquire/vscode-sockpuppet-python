"""
Progress indicator operations for VS Code
"""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .client import VSCodeClient


class ProgressLocation:
    """Progress location options."""

    Notification = "notification"
    Window = "window"
    SourceControl = "sourcecontrol"


class Progress:
    """
    Represents a progress indicator.

    Note: This is a simplified version. For complex progress scenarios,
    you may want to manage progress updates through custom events.
    """

    def __init__(self, client: "VSCodeClient", progress_id: str):
        """
        Create a progress indicator.

        Args:
            client: The VS Code client
            progress_id: Unique progress identifier
        """
        self.client = client
        self.progress_id = progress_id

    def report(self, message: Optional[str] = None, increment: Optional[int] = None) -> None:
        """
        Report progress.

        Args:
            message: Progress message
            increment: Progress increment (percentage)
        """
        # This would need additional server-side support
        # for real-time progress updates
        pass


def with_progress(
    client: "VSCodeClient",
    location: str = ProgressLocation.Notification,
    title: str = "",
    cancellable: bool = False,
    message: Optional[str] = None,
) -> dict:
    """
    Show a progress indicator.

    Args:
        client: The VS Code client
        location: Where to show progress (notification, window, sourcecontrol)
        title: Progress title
        cancellable: Whether the operation can be cancelled
        message: Initial progress message

    Returns:
        Result dictionary with success status

    Example:
        >>> with_progress(
        ...     client,
        ...     location=ProgressLocation.Notification,
        ...     title="Processing",
        ...     message="Please wait..."
        ... )
    """
    return client._send_request(
        "window.withProgress",
        {
            "location": location,
            "title": title,
            "cancellable": cancellable,
            "message": message,
            "task": "wait",
        },
    )
