"""Workspace and document event TypedDicts."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, Union

if TYPE_CHECKING:
    from ..client import VSCodeClient

from .core import Event


# Small reusable shapes
class PositionDict(TypedDict):
    line: int
    character: int


class RangeDict(TypedDict):
    start: PositionDict
    end: PositionDict


class ContentChangeDict(TypedDict):
    range: RangeDict
    text: str


# Workspace / document-related payloads
class TextDocumentDict(TypedDict):
    uri: str
    fileName: str
    languageId: str


class DidChangeTextDocumentEvent(TypedDict):
    uri: str
    contentChanges: list[ContentChangeDict]


class CreatedFileDict(TypedDict):
    uri: str


class RenamedFileDict(TypedDict):
    oldUri: str
    newUri: str


class FileOperationEvent(TypedDict):
    # For create/delete: list[CreatedFileDict]
    # For rename: list[RenamedFileDict]
    files: list[Union[CreatedFileDict, RenamedFileDict]]


class WorkspaceFolderDict(TypedDict):
    uri: str
    name: str


class WorkspaceFoldersChangeEvent(TypedDict):
    added: list[WorkspaceFolderDict]
    removed: list[WorkspaceFolderDict]


class ConfigurationChangeEvent(TypedDict, total=False):
    # The server currently doesn't serialize a usable payload for this
    # event (functions are omitted by JSON). Keep this opaque for now.
    pass


class WorkspaceEvents:
    """
    Event emitters for workspace-related VS Code events.

    Provides VS Code-style event subscription with on_did_* methods.
    """

    def __init__(self, client: VSCodeClient):
        """Initialize workspace events."""
        self._client = client

    @property
    def on_did_open_text_document(self) -> Event:
        """
        Event fired when a text document is opened.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(document):
                print(f"Opened: {document['fileName']}")

            dispose = workspace.on_did_open_text_document(handler)
        """
        return Event(self._client, "workspace.onDidOpenTextDocument")

    @property
    def on_did_close_text_document(self) -> Event:
        """
        Event fired when a text document is closed.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(document):
                print(f"Closed: {document['fileName']}")

            dispose = workspace.on_did_close_text_document(handler)
        """
        return Event(self._client, "workspace.onDidCloseTextDocument")

    @property
    def on_did_save_text_document(self) -> Event:
        """
        Event fired when a text document is saved.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(document):
                print(f"Saved: {document['fileName']}")

            dispose = workspace.on_did_save_text_document(handler)
        """
        return Event(self._client, "workspace.onDidSaveTextDocument")

    @property
    def on_did_change_text_document(self) -> Event:
        """
        Event fired when a text document changes.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(event):
                print(f"Changed: {event['uri']}")
                for change in event['contentChanges']:
                    print(f"  Text: {change['text']}")

            dispose = workspace.on_did_change_text_document(handler)
        """
        return Event(self._client, "workspace.onDidChangeTextDocument")

    @property
    def on_did_change_workspace_folders(self) -> Event:
        """
        Event fired when workspace folders are added or removed.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(event):
                print(f"Added: {len(event['added'])}")
                print(f"Removed: {len(event['removed'])}")

            dispose = workspace.on_did_change_workspace_folders(handler)
        """
        return Event(self._client, "workspace.onDidChangeWorkspaceFolders")

    @property
    def on_did_change_configuration(self) -> Event:
        """
        Event fired when the configuration changes.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(event):
                print("Configuration changed")

            dispose = workspace.on_did_change_configuration(handler)
        """
        return Event(self._client, "workspace.onDidChangeConfiguration")

    @property
    def on_did_create_files(self) -> Event:
        """
        Event fired when files are created.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(data):
                for file in data['files']:
                    print(f"Created: {file['uri']}")

            dispose = workspace.on_did_create_files(handler)
        """
        return Event(self._client, "workspace.onDidCreateFiles")

    @property
    def on_did_delete_files(self) -> Event:
        """
        Event fired when files are deleted.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(data):
                for file in data['files']:
                    print(f"Deleted: {file['uri']}")

            dispose = workspace.on_did_delete_files(handler)
        """
        return Event(self._client, "workspace.onDidDeleteFiles")

    @property
    def on_did_rename_files(self) -> Event:
        """
        Event fired when files are renamed or moved.

        Returns:
            Event that can be called with a handler

        Example:
            def handler(data):
                for file in data['files']:
                    print(f"Renamed: {file['oldUri']} -> {file['newUri']}")

            dispose = workspace.on_did_rename_files(handler)
        """
        return Event(self._client, "workspace.onDidRenameFiles")
