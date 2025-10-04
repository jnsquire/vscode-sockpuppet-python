"""
VSCode Sockpuppet - Python API for controlling VS Code programmatically
"""

from .client import VSCodeClient
from .configuration import ConfigurationTarget, WorkspaceConfiguration
from .diagnostics import (
    Diagnostic,
    DiagnosticCollection,
    DiagnosticRelatedInformation,
    DiagnosticSeverity,
    Languages,
    create_location,
    create_position,
    create_range,
)
from .document import TextDocument, TextLine
from .editor import DecorationType, EditBuilder, Editor
from .filewatcher import FileSystemWatcher
from .fs import FileStat, FileSystem, FileType
from .language_model import (
    LanguageModel,
    LanguageModelChat,
    LanguageModelChatMessage,
)
from .progress import Progress, ProgressLocation, with_progress
from .statusbar import (
    StatusBarAlignment,
    StatusBarItem,
    create_status_bar_item,
)
from .tabs import Tab, TabGroup, TabGroups
from .terminal import Terminal
from .webview import WebviewOptions, WebviewPanel
from .window import Window
from .window_types import (
    CreateFileOperation,
    DecorationRenderOptions,
    DeleteFileOperation,
    InputBoxOptions,
    OpenDialogOptions,
    PositionDict,
    QuickPickOptions,
    RangeDict,
    RenameFileOperation,
    SaveDialogOptions,
    TextDocumentEdit,
    TextDocumentShowOptions,
    TextEdit,
    ThemableDecorationAttachmentRenderOptions,
    ThemableDecorationRenderOptions,
    WindowState,
    WorkspaceEdit,
    WorkspaceFolderPickOptions,
)
from .workspace import Environment, Workspace

__version__ = "0.1.0"
__all__ = [
    "VSCodeClient",
    "Window",
    "Workspace",
    "Environment",
    "Editor",
    "EditBuilder",
    "DecorationType",
    "TextDocument",
    "PositionDict",
    "RangeDict",
    "TextLine",
    "FileSystemWatcher",
    "WebviewPanel",
    "WebviewOptions",
    "QuickPickOptions",
    "InputBoxOptions",
    "PositionDict",
    "RangeDict",
    "TextEdit",
    "TextDocumentEdit",
    "WorkspaceEdit",
    "CreateFileOperation",
    "DeleteFileOperation",
    "RenameFileOperation",
    "DecorationRenderOptions",
    "ThemableDecorationRenderOptions",
    "ThemableDecorationAttachmentRenderOptions",
    "OpenDialogOptions",
    "SaveDialogOptions",
    "TextDocumentShowOptions",
    "WorkspaceFolderPickOptions",
    "WindowState",
    "FileSystem",
    "FileStat",
    "FileType",
    "Languages",
    "Diagnostic",
    "DiagnosticCollection",
    "DiagnosticRelatedInformation",
    "DiagnosticSeverity",
    "create_range",
    "create_position",
    "create_location",
    "StatusBarItem",
    "StatusBarAlignment",
    "create_status_bar_item",
    "Tab",
    "TabGroup",
    "TabGroups",
    "Terminal",
    "Progress",
    "ProgressLocation",
    "with_progress",
    "WorkspaceConfiguration",
    "ConfigurationTarget",
    "LanguageModel",
    "LanguageModelChat",
    "LanguageModelChatMessage",
]
