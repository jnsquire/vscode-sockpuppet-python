"""Window, editor, and terminal event TypedDicts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    from ..client import VSCodeClient

from .core import Event
from .workspace import PositionDict, RangeDict


# Window / editor / terminal payloads
class WindowStateEvent(TypedDict):
    focused: bool


class SelectionDict(TypedDict):
    start: PositionDict
    end: PositionDict
    active: PositionDict
    anchor: PositionDict


class TextEditorSelectionEvent(TypedDict):
    uri: str
    selections: list[SelectionDict]


class VisibleEditorSummary(TypedDict):
    uri: str
    languageId: str


class VisibleTextEditorsEvent(TypedDict):
    count: int
    editors: list[VisibleEditorSummary]


class TextEditorVisibleRangesEvent(TypedDict):
    uri: str
    visibleRanges: list[RangeDict]


class TextEditorOptionsDict(TypedDict, total=False):
    tabSize: int
    insertSpaces: bool
    cursorStyle: Any
    lineNumbers: Any


class TextEditorOptionsEvent(TypedDict):
    uri: str
    options: TextEditorOptionsDict


class TextEditorViewColumnEvent(TypedDict):
    uri: str
    viewColumn: int


class TerminalEvent(TypedDict):
    name: str


class TerminalStateEvent(TypedDict):
    name: str
    isInteractedWith: bool


class WindowEvents:
    """
    Event emitters for window-related VS Code events.

    Provides VS Code-style event subscription with on_did_* methods.
    """

    def __init__(self, client: VSCodeClient):
        """Initialize window events."""
        self._client = client

    @property
    def on_did_change_active_text_editor(self) -> Event:
        """
        Event fired when the active text editor changes.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(editor):
                if editor:
                    print(f"Active editor: {editor['fileName']}")

            dispose = window.on_did_change_active_text_editor(handler)
        """
        return Event(self._client, "window.onDidChangeActiveTextEditor")

    @property
    def on_did_change_text_editor_selection(self) -> Event:
        """
        Event fired when the selection in an editor changes.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(data):
                sel = data['selections'][0]
                print(f"Line {sel['start']['line']}")

            dispose = window.on_did_change_text_editor_selection(handler)
        """
        return Event(self._client, "window.onDidChangeTextEditorSelection")

    @property
    def on_did_change_visible_text_editors(self) -> Event:
        """
        Event fired when the visible text editors change.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(data):
                print(f"{data['count']} editors visible")

            dispose = window.on_did_change_visible_text_editors(handler)
        """
        return Event(self._client, "window.onDidChangeVisibleTextEditors")

    @property
    def on_did_open_terminal(self) -> Event:
        """
        Event fired when a terminal is opened.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(terminal):
                print(f"Terminal opened: {terminal['name']}")

            dispose = window.on_did_open_terminal(handler)
        """
        return Event(self._client, "window.onDidOpenTerminal")

    @property
    def on_did_close_terminal(self) -> Event:
        """
        Event fired when a terminal is closed.

        Returns:
            Event that can be called with a handler

        Example:
            dispose = window.on_did_close_terminal(handler)
        """
        return Event(self._client, "window.onDidCloseTerminal")

    @property
    def on_did_change_terminal_state(self) -> Event:
        """
        Event fired when a terminal's state changes.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(data):
                print(f"Terminal {data['name']}: interacted = {data['isInteractedWith']}")

            dispose = window.on_did_change_terminal_state(handler)
        """
        return Event(self._client, "window.onDidChangeTerminalState")

    @property
    def on_did_change_text_editor_visible_ranges(self) -> Event:
        """
        Event fired when visible ranges in an editor change (scrolling).

        Returns:
            Event that can be called with a handler

        Example:
            def handler(data):
                print(f"Visible in {data['uri']}: {len(data['visibleRanges'])} ranges")

            dispose = window.on_did_change_text_editor_visible_ranges(handler)
        """
        return Event(self._client, "window.onDidChangeTextEditorVisibleRanges")

    @property
    def on_did_change_text_editor_options(self) -> Event:
        """
        Event fired when text editor options change.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(data):
                opts = data['options']
                print(f"Tab size: {opts['tabSize']}")

            dispose = window.on_did_change_text_editor_options(handler)
        """
        return Event(self._client, "window.onDidChangeTextEditorOptions")

    @property
    def on_did_change_text_editor_view_column(self) -> Event:
        """
        Event fired when an editor's view column changes.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(data):
                print(f"Editor moved to column {data['viewColumn']}")

            dispose = window.on_did_change_text_editor_view_column(handler)
        """
        return Event(self._client, "window.onDidChangeTextEditorViewColumn")

    @property
    def on_did_change_window_state(self) -> Event:
        """
        Event fired when the window state changes (focus).

        Returns:
            Event that can be called with a handler

        Example:
            def handler(data):
                if data['focused']:
                    print("Window gained focus")
                else:
                    print("Window lost focus")

            dispose = window.on_did_change_window_state(handler)
        """
        return Event(self._client, "window.onDidChangeWindowState")
