"""
Workspace operations for VS Code
"""

from typing import TYPE_CHECKING, Optional

from .configuration import WorkspaceConfiguration
from .document import TextDocument
from .events import WorkspaceEvents

if TYPE_CHECKING:
    from .client import VSCodeClient


class Workspace:
    """VS Code workspace operations."""

    def __init__(self, client: "VSCodeClient"):
        self.client = client
        self._events = WorkspaceEvents(client)

    # Event subscriptions (VS Code-style API)
    @property
    def on_did_open_text_document(self):
        """Event fired when a text document is opened."""
        return self._events.on_did_open_text_document

    @property
    def on_did_close_text_document(self):
        """Event fired when a text document is closed."""
        return self._events.on_did_close_text_document

    @property
    def on_did_save_text_document(self):
        """Event fired when a text document is saved."""
        return self._events.on_did_save_text_document

    @property
    def on_did_change_text_document(self):
        """Event fired when a text document changes."""
        return self._events.on_did_change_text_document

    @property
    def on_did_change_workspace_folders(self):
        """Event fired when workspace folders are added or removed."""
        return self._events.on_did_change_workspace_folders

    @property
    def on_did_change_configuration(self):
        """Event fired when the configuration changes."""
        return self._events.on_did_change_configuration

    def open_text_document(
        self,
        uri: Optional[str] = None,
        content: Optional[str] = None,
        language: Optional[str] = None,
    ) -> TextDocument:
        """
        Open a text document.

        Args:
            uri: The URI of the document to open
            content: Content for an untitled document
            language: Language identifier for untitled document

        Returns:
            TextDocument object
        """
        data = self.client._send_request(
            "workspace.openTextDocument",
            {"uri": uri, "content": content, "language": language},
        )
        return TextDocument(self.client, data)

    def save_all(self, include_untitled: bool = False) -> bool:
        """
        Save all dirty files.

        Args:
            include_untitled: Whether to include untitled files

        Returns:
            True if all files were saved
        """
        return self.client._send_request(
            "workspace.saveAll", {"includeUntitled": include_untitled}
        )

    def get_workspace_folders(self) -> list[dict]:
        """
        Get all workspace folders.

        Returns:
            List of workspace folders (uri, name, index)
        """
        return self.client._send_request("workspace.workspaceFolders", {})

    def text_documents(self) -> list[TextDocument]:
        """
        Get all open text documents.

        Returns:
            List of TextDocument objects
        """
        docs_data = self.client._send_request("workspace.textDocuments", {})
        return [TextDocument(self.client, data) for data in docs_data]

    def get_text_document(self, uri: str) -> TextDocument:
        """
        Get a specific open text document by URI.

        Args:
            uri: The URI of the document

        Returns:
            TextDocument object
        """
        data = self.client._send_request(
            "workspace.getTextDocument", {"uri": uri}
        )
        return TextDocument(self.client, data)

    def write_to_clipboard(self, text: str) -> dict:
        """
        Write text to clipboard.

        Args:
            text: The text to write

        Returns:
            Success status
        """
        return self.client._send_request(
            "env.clipboard.writeText", {"text": text}
        )

    def read_from_clipboard(self) -> str:
        """
        Read text from clipboard.

        Returns:
            The clipboard text
        """
        return self.client._send_request("env.clipboard.readText")

    def open_external(self, uri: str) -> bool:
        """
        Open an external URI.

        Args:
            uri: The URI to open

        Returns:
            True if successful
        """
        return self.client._send_request("env.openExternal", {"uri": uri})

    def get_configuration(
        self, section: Optional[str] = None, scope: Optional[str] = None
    ) -> WorkspaceConfiguration:
        """
        Get a workspace configuration object.

        Args:
            section: Configuration section (e.g., 'editor', 'python.linting')
            scope: Resource URI or language ID for scoped configuration

        Returns:
            WorkspaceConfiguration object

        Example:
            # Get editor configuration
            config = client.workspace.get_configuration('editor')
            font_size = config.get('fontSize', 14)

            # Update a setting
            config.update('fontSize', 16, ConfigurationTarget.GLOBAL)

            # Get all configuration
            config = client.workspace.get_configuration()
            value = config.get('editor.fontSize')
        """
        return WorkspaceConfiguration(self.client, section, scope)
