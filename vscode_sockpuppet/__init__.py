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
from .document import Position, Range, TextDocument, TextLine
from .editor import EditBuilder, Editor
from .filewatcher import FileSystemWatcher
from .fs import FileStat, FileSystem, FileType
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
from .workspace import Workspace

__version__ = "0.1.0"
__all__ = [
    "VSCodeClient",
    "Window",
    "Workspace",
    "Editor",
    "EditBuilder",
    "TextDocument",
    "Position",
    "Range",
    "TextLine",
    "FileSystemWatcher",
    "WebviewPanel",
    "WebviewOptions",
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
]
