"""
Type definitions for VS Code API options and interfaces.

This module contains TypedDict classes that match the VS Code API interfaces,
providing type hints and IDE autocomplete support for API options.
"""

from typing import TypedDict


class PositionDict(TypedDict):
    """Dictionary representation of a position in a text document."""

    line: int
    """Line number (0-based)"""

    character: int
    """Character offset on the line (0-based)"""


class RangeDict(TypedDict):
    """Dictionary representation of a range in a text document."""

    start: PositionDict
    """The start position of the range"""

    end: PositionDict
    """The end position of the range"""


class QuickPickOptions(TypedDict, total=False):
    """Options to configure the behavior of the quick pick UI."""

    title: str
    """An optional title for the quick pick"""

    matchOnDescription: bool
    """Controls if the description of items should be matched"""

    matchOnDetail: bool
    """Controls if the detail of items should be matched"""

    placeHolder: str
    """Placeholder text to show in the input box"""

    ignoreFocusOut: bool
    """
    Set to true to keep the picker open when focus moves to another part
    of the editor or to another window
    """

    canPickMany: bool
    """Allow multiple selections"""


class InputBoxOptions(TypedDict, total=False):
    """Options to configure the behavior of the input box UI."""

    title: str
    """An optional title for the input box"""

    value: str
    """The value to prefill in the input box"""

    valueSelection: tuple[int, int]
    """Selection range of the prefilled value (start, end)"""

    prompt: str
    """The text to display underneath the input box"""

    placeHolder: str
    """Placeholder text in the input box"""

    password: bool
    """Set to true to show a password input that hides the typed text"""

    ignoreFocusOut: bool
    """
    Set to true to keep the input box open when focus moves to another
    part of the editor or to another window
    """


class TextDocumentShowOptions(TypedDict, total=False):
    """
    Options to configure the behavior of showing a TextDocument in an editor.
    """

    viewColumn: int
    """
    An optional view column in which the editor should be shown.
    The default is the active column. Columns that do not exist will be
    created as needed.
    """

    preserveFocus: bool
    """
    An optional flag that when true will stop the editor from taking focus
    """

    preview: bool
    """
    An optional flag that controls if an editor-tab will be replaced
    with the next editor or if it will be kept
    """

    selection: dict
    """
    An optional selection to apply to the document.
    Should be a range dict with start and end positions.
    """


class OpenDialogOptions(TypedDict, total=False):
    """
    Options to configure the behavior of a file open dialog.

    Note: On Windows and Linux, a file dialog cannot be both a file selector
    and a folder selector, so if you set both canSelectFiles and
    canSelectFolders to True on these platforms, a folder selector will be
    shown.
    """

    defaultUri: str
    """The default URI to show when the dialog opens"""

    openLabel: str
    """A human-readable string for the open button"""

    canSelectFiles: bool
    """Allow selecting files (default: True)"""

    canSelectFolders: bool
    """Allow selecting folders (default: False)"""

    canSelectMany: bool
    """Allow multiple selections (default: False)"""

    filters: dict[str, list[str]]
    """
    File filters used by the dialog. Each entry is a human-readable label
    and an array of extensions.
    Example: {'Images': ['png', 'jpg'], 'TypeScript': ['ts', 'tsx']}
    """

    title: str
    """Dialog title"""


class SaveDialogOptions(TypedDict, total=False):
    """Options to configure the behavior of a file save dialog."""

    defaultUri: str
    """The resource the dialog shows when opened"""

    saveLabel: str
    """A human-readable string for the save button"""

    filters: dict[str, list[str]]
    """
    File filters used by the dialog. Each entry is a human-readable label
    and an array of extensions.
    Example: {'Images': ['png', 'jpg'], 'TypeScript': ['ts', 'tsx']}
    """

    title: str
    """
    Dialog title.
    Note: This parameter might be ignored, as not all operating systems
    display a title on save dialogs (for example, macOS).
    """


class WorkspaceFolderPickOptions(TypedDict, total=False):
    """Options for showing the workspace folder picker.

    This mirrors the small options bag accepted by VS Code for
    `window.showWorkspaceFolderPick`, currently supporting `placeHolder`
    and `ignoreFocusOut`.
    """

    placeHolder: str
    """Placeholder text shown in the picker"""

    ignoreFocusOut: bool
    """Keep the picker open when focus moves out"""


class ThemableDecorationAttachmentRenderOptions(TypedDict, total=False):
    """Options for rendering decoration attachments (before/after content)."""

    contentText: str
    contentIconPath: str
    border: str
    borderColor: str
    fontStyle: str
    fontWeight: str
    textDecoration: str
    color: str
    backgroundColor: str
    margin: str
    width: str
    height: str


class ThemableDecorationRenderOptions(TypedDict, total=False):
    """Theme-specific rendering options for decorations."""

    backgroundColor: str
    outline: str
    outlineColor: str
    outlineStyle: str
    outlineWidth: str
    border: str
    borderColor: str
    borderRadius: str
    borderSpacing: str
    borderStyle: str
    borderWidth: str
    fontStyle: str
    fontWeight: str
    textDecoration: str
    cursor: str
    color: str
    opacity: str
    letterSpacing: str
    gutterIconPath: str
    gutterIconSize: str
    overviewRulerColor: str
    before: ThemableDecorationAttachmentRenderOptions
    after: ThemableDecorationAttachmentRenderOptions


class DecorationRenderOptions(ThemableDecorationRenderOptions, total=False):
    """Options for rendering text editor decorations.

    This mirrors VS Code's DecorationRenderOptions interface.
    All properties are optional.

    Example:
        decoration_options: DecorationRenderOptions = {
            "backgroundColor": "rgba(255, 0, 0, 0.3)",
            "border": "1px solid red",
            "borderRadius": "3px",
            "isWholeLine": True,
            "overviewRulerLane": 2,  # Center lane
            "light": {
                "backgroundColor": "rgba(255, 0, 0, 0.1)"
            },
            "dark": {
                "backgroundColor": "rgba(255, 0, 0, 0.3)"
            }
        }
    """

    isWholeLine: bool
    rangeBehavior: int  # DecorationRangeBehavior enum value
    # OverviewRulerLane: 1=Left, 2=Center, 4=Right, 7=Full
    overviewRulerLane: int
    light: ThemableDecorationRenderOptions
    dark: ThemableDecorationRenderOptions


class WindowState(TypedDict, total=False):
    """Represents the current window state returned by `window.state`.

    Fields are optional because different VS Code versions/platforms may
    expose slightly different properties. Known fields:
    - focused: bool — whether the window is focused
    - active: bool — whether the window is active (platform-dependent)
    """

    focused: bool
    active: bool


class TextEdit(TypedDict):
    """Represents a single text edit operation."""

    range: RangeDict
    """The range to replace"""

    newText: str
    """The new text for the range"""


class TextDocumentEdit(TypedDict):
    """Represents edits to a single text document."""

    uri: str
    """The URI of the document to edit"""

    edits: list[TextEdit]
    """The text edits to apply"""


class CreateFileOperation(TypedDict, total=False):
    """Represents a file creation operation."""

    uri: str
    """The URI of the file to create"""

    options: dict
    """Additional options (overwrite, ignoreIfExists)"""


class DeleteFileOperation(TypedDict, total=False):
    """Represents a file deletion operation."""

    uri: str
    """The URI of the file to delete"""

    options: dict
    """Additional options (recursive, ignoreIfNotExists)"""


class RenameFileOperation(TypedDict, total=False):
    """Represents a file rename operation."""

    oldUri: str
    """The old URI of the file"""

    newUri: str
    """The new URI of the file"""

    options: dict
    """Additional options (overwrite, ignoreIfExists)"""


class WorkspaceEdit(TypedDict, total=False):
    """Represents a workspace edit with changes to multiple files.

    A workspace edit can contain text edits for documents and file operations
    (create, delete, rename). All changes are applied atomically.
    """

    documentChanges: list[TextDocumentEdit]
    """Text edits grouped by document"""

    createFiles: list[CreateFileOperation]
    """Files to create"""

    deleteFiles: list[DeleteFileOperation]
    """Files to delete"""

    renameFiles: list[RenameFileOperation]
    """Files to rename"""
