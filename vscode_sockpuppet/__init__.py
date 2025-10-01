"""
VSCode Sockpuppet - Python API for controlling VS Code programmatically
"""

from .client import VSCodeClient
from .document import Position, Range, TextDocument, TextLine
from .editor import Editor
from .webview import WebviewOptions, WebviewPanel
from .window import Window
from .workspace import Workspace

__version__ = "0.1.0"
__all__ = [
    "VSCodeClient",
    "Window",
    "Workspace",
    "Editor",
    "TextDocument",
    "Position",
    "Range",
    "TextLine",
    "WebviewPanel",
    "WebviewOptions",
]
