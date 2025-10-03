"""
Type definitions for VS Code API options and interfaces.

This module contains TypedDict classes that match the VS Code API interfaces,
providing type hints and IDE autocomplete support for API options.
"""

from typing import TypedDict


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
