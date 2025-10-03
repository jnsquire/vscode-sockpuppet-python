"""
Workspace operations for VS Code
"""

from typing import TYPE_CHECKING, Optional

from .configuration import WorkspaceConfiguration
from .document import TextDocument
from .events import WorkspaceEvents

if TYPE_CHECKING:
    from .client import VSCodeClient
    from .filewatcher import FileSystemWatcher


class Environment:
    """VS Code environment properties and methods."""

    def __init__(self, client: "VSCodeClient"):
        self.client = client
        self._cached_properties = {}

    def _get_property(self, prop_name: str):
        """Get an environment property, with caching."""
        if prop_name not in self._cached_properties:
            result = self.client._send_request(f"env.{prop_name}")
            self._cached_properties[prop_name] = result
        return self._cached_properties[prop_name]

    @property
    def app_name(self) -> str:
        """
        The application name of the editor, like 'VS Code'.

        Returns:
            Application name

        Example:
            print(f"Running in: {client.workspace.env.app_name}")
        """
        return self._get_property("appName")

    @property
    def app_root(self) -> str:
        """
        The application root folder from which the editor is running.

        Returns:
            Application root path (empty string if not applicable)

        Example:
            print(f"App root: {client.workspace.env.app_root}")
        """
        return self._get_property("appRoot")

    @property
    def language(self) -> str:
        """
        The UI language of VS Code.

        Returns:
            Language identifier (e.g., 'en', 'de', 'zh-cn')

        Example:
            if client.workspace.env.language == 'en':
                print("English UI")
        """
        return self._get_property("language")

    @property
    def machine_id(self) -> str:
        """
        A unique identifier for the machine.

        Returns:
            Machine identifier (anonymized)

        Example:
            print(f"Machine ID: {client.workspace.env.machine_id}")
        """
        return self._get_property("machineId")

    @property
    def session_id(self) -> str:
        """
        A unique identifier for the current session.

        Returns:
            Session identifier

        Example:
            print(f"Session: {client.workspace.env.session_id}")
        """
        return self._get_property("sessionId")

    @property
    def uri_scheme(self) -> str:
        """
        The custom URI scheme the editor registers in the OS.

        Returns:
            URI scheme (typically 'vscode' or 'vscode-insiders')

        Example:
            print(f"URI scheme: {client.workspace.env.uri_scheme}")
        """
        return self._get_property("uriScheme")

    @property
    def shell(self) -> str:
        """
        The detected default shell for the extension host.

        Returns:
            Path to the default shell

        Example:
            print(f"Default shell: {client.workspace.env.shell}")
        """
        return self._get_property("shell")

    @property
    def ui_kind(self) -> int:
        """
        The UI kind property indicates from which UI extensions are accessed.

        Returns:
            UI kind (1 = Desktop, 2 = Web)

        Example:
            if client.workspace.env.ui_kind == 1:
                print("Running in desktop VS Code")
            else:
                print("Running in web VS Code")
        """
        return self._get_property("uiKind")

    def write_clipboard(self, text: str) -> None:
        """
        Write text to clipboard.

        Args:
            text: The text to write

        Example:
            client.workspace.env.write_clipboard("Hello, clipboard!")
        """
        self.client._send_request("env.clipboard.writeText", {"text": text})

    def read_clipboard(self) -> str:
        """
        Read text from clipboard.

        Returns:
            The clipboard text

        Example:
            text = client.workspace.env.read_clipboard()
            print(f"Clipboard: {text}")
        """
        return self.client._send_request("env.clipboard.readText")

    def open_external(self, uri: str) -> bool:
        """
        Open an external URI in the default application.

        Args:
            uri: The URI to open (http, https, mailto, etc.)

        Returns:
            True if successful

        Example:
            # Open URL in browser
            client.workspace.env.open_external("https://code.visualstudio.com")

            # Open email client
            client.workspace.env.open_external("mailto:user@example.com")
        """
        return self.client._send_request("env.openExternal", {"uri": uri})


class Workspace:
    """VS Code workspace operations."""

    def __init__(self, client: "VSCodeClient"):
        self.client = client
        self._events = WorkspaceEvents(client)
        self._env: Optional[Environment] = None

    @property
    def env(self) -> Environment:
        """
        Access environment properties and methods.

        Returns:
            Environment object with properties and methods

        Example:
            print(f"Running in: {client.workspace.env.app_name}")
            print(f"UI Language: {client.workspace.env.language}")
            client.workspace.env.open_external("https://example.com")
        """
        if self._env is None:
            self._env = Environment(self.client)
        return self._env

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

    @property
    def on_did_create_files(self):
        """Event fired when files are created."""
        return self._events.on_did_create_files

    @property
    def on_did_delete_files(self):
        """Event fired when files are deleted."""
        return self._events.on_did_delete_files

    @property
    def on_did_rename_files(self):
        """Event fired when files are renamed or moved."""
        return self._events.on_did_rename_files

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
        data = self.client._send_request("workspace.getTextDocument", {"uri": uri})
        return TextDocument(self.client, data)

    def find_files(
        self,
        include: str,
        exclude: Optional[str] = None,
        max_results: Optional[int] = None,
    ) -> list[str]:
        """
        Find files across all workspace folders.

        Args:
            include: Glob pattern for files to search for
                (e.g., '**/*.py', '**/*.{js,ts}')
            exclude: Glob pattern for files/folders to exclude
                (e.g., '**/node_modules/**'). Use None for default
                excludes (files.exclude setting)
            max_results: Maximum number of results to return

        Returns:
            List of file URIs matching the pattern

        Example:
            # Find all Python files
            files = client.workspace.find_files('**/*.py')

            # Find JavaScript files, excluding node_modules
            files = client.workspace.find_files(
                '**/*.js',
                '**/node_modules/**'
            )

            # Limit results
            files = client.workspace.find_files('**/*.ts', max_results=10)
        """
        result = self.client._send_request(
            "workspace.findFiles",
            {
                "include": include,
                "exclude": exclude,
                "maxResults": max_results,
            },
        )
        return result["files"]

    def get_workspace_folder(self, uri: str) -> Optional[dict]:
        """
        Get the workspace folder that contains a given URI.

        Args:
            uri: The URI to find the workspace folder for

        Returns:
            Workspace folder dict (uri, name, index) or None if not found

        Example:
            folder = client.workspace.get_workspace_folder(
                'file:///path/to/file.py'
            )
            if folder:
                print(f"File is in workspace: {folder['name']}")
        """
        result = self.client._send_request("workspace.getWorkspaceFolder", {"uri": uri})
        return result["folder"]

    def as_relative_path(self, path_or_uri: str, include_workspace_folder: bool = False) -> str:
        """
        Convert a path or URI to a workspace-relative path.

        Args:
            path_or_uri: Absolute path or URI to convert
            include_workspace_folder: Whether to prepend workspace
                folder name when multiple folders exist

        Returns:
            Path relative to workspace root, or original input if not
            in workspace

        Example:
            # Convert absolute path
            rel_path = client.workspace.as_relative_path(
                '/Users/name/project/src/main.py'
            )
            # Returns: 'src/main.py'

            # With workspace folder name (when multiple folders)
            rel_path = client.workspace.as_relative_path(
                '/Users/name/project/src/main.py',
                include_workspace_folder=True
            )
            # Returns: 'project-name/src/main.py'
        """
        result = self.client._send_request(
            "workspace.asRelativePath",
            {
                "pathOrUri": path_or_uri,
                "includeWorkspaceFolder": include_workspace_folder,
            },
        )
        return result["relativePath"]

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

    def create_file_system_watcher(
        self,
        glob_pattern: str,
        ignore_create_events: bool = False,
        ignore_change_events: bool = False,
        ignore_delete_events: bool = False,
    ) -> "FileSystemWatcher":
        """
        Create a file system watcher for the given glob pattern.

        Args:
            glob_pattern: Glob pattern to watch
                (e.g., '**/*.py', '**/*.{js,ts}')
            ignore_create_events: Don't fire events when files are created
            ignore_change_events: Don't fire events when files are changed
            ignore_delete_events: Don't fire events when files are deleted

        Returns:
            FileSystemWatcher instance

        Example:
            # Watch all Python files in workspace
            watcher = workspace.create_file_system_watcher("**/*.py")

            def on_python_file_created(uri):
                print(f"New Python file: {uri}")

            def on_python_file_changed(uri):
                print(f"Python file modified: {uri}")

            # Subscribe to events
            dispose1 = watcher.on_did_create(on_python_file_created)
            dispose2 = watcher.on_did_change(on_python_file_changed)

            # Later, stop watching
            watcher.dispose()

            # Or use as context manager
            with workspace.create_file_system_watcher("**/*.js") as watcher:
                watcher.on_did_create(lambda uri: print(f"Created: {uri}"))
                # ... do work ...
            # Automatically disposed when exiting context
        """
        from .filewatcher import FileSystemWatcher

        result = self.client._send_request(
            "workspace.createFileSystemWatcher",
            {
                "globPattern": glob_pattern,
                "ignoreCreateEvents": ignore_create_events,
                "ignoreChangeEvents": ignore_change_events,
                "ignoreDeleteEvents": ignore_delete_events,
            },
        )

        return FileSystemWatcher(
            self.client,
            result["watcherId"],
            glob_pattern,
            ignore_create_events,
            ignore_change_events,
            ignore_delete_events,
        )
