"""Event system for VS Code Sockpuppet.

Re-exports all event-related classes and TypedDicts from submodules.
"""

from .core import Event, EventEmitter
from .tabs import TabGroupsChangeEvent, TabsChangeEvent
from .watcher import FileWatcherEvent
from .webview import (
    WebviewDisposeEvent,
    WebviewMessageEvent,
    WebviewViewStateEvent,
)
from .window import (
    SelectionDict,
    TerminalEvent,
    TerminalStateEvent,
    TextEditorOptionsDict,
    TextEditorOptionsEvent,
    TextEditorSelectionEvent,
    TextEditorViewColumnEvent,
    TextEditorVisibleRangesEvent,
    VisibleEditorSummary,
    VisibleTextEditorsEvent,
    WindowEvents,
    WindowStateEvent,
)
from .workspace import (
    ConfigurationChangeEvent,
    ContentChangeDict,
    CreatedFileDict,
    DidChangeTextDocumentEvent,
    FileOperationEvent,
    PositionDict,
    RangeDict,
    RenamedFileDict,
    TextDocumentDict,
    WorkspaceEvents,
    WorkspaceFolderDict,
    WorkspaceFoldersChangeEvent,
)

__all__ = [
    # Core
    "Event",
    "EventEmitter",
    # Webview
    "WebviewMessageEvent",
    "WebviewDisposeEvent",
    "WebviewViewStateEvent",
    # Watcher
    "FileWatcherEvent",
    # Workspace/Document
    "PositionDict",
    "RangeDict",
    "ContentChangeDict",
    "TextDocumentDict",
    "DidChangeTextDocumentEvent",
    "CreatedFileDict",
    "RenamedFileDict",
    "FileOperationEvent",
    "WorkspaceFolderDict",
    "WorkspaceFoldersChangeEvent",
    "ConfigurationChangeEvent",
    "WorkspaceEvents",
    # Window/Editor/Terminal
    "WindowStateEvent",
    "SelectionDict",
    "TextEditorSelectionEvent",
    "VisibleEditorSummary",
    "VisibleTextEditorsEvent",
    "TextEditorVisibleRangesEvent",
    "TextEditorOptionsDict",
    "TextEditorOptionsEvent",
    "TextEditorViewColumnEvent",
    "TerminalEvent",
    "TerminalStateEvent",
    "WindowEvents",
    # Tabs
    "TabGroupsChangeEvent",
    "TabsChangeEvent",
]
