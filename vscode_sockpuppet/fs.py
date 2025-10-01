"""
File system operations for VS Code
"""

from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from .client import VSCodeClient


class FileType:
    """File type enumeration."""

    Unknown = 0
    File = 1
    Directory = 2
    SymbolicLink = 64


class FileStat:
    """File metadata."""

    def __init__(self, data: dict):
        self.type: int = data["type"]
        self.ctime: int = data["ctime"]
        self.mtime: int = data["mtime"]
        self.size: int = data["size"]


class FileSystem:
    """VS Code file system operations."""

    def __init__(self, client: "VSCodeClient"):
        self.client = client

    def read_file(self, uri: str) -> bytes:
        """
        Read a file.

        Args:
            uri: The URI of the file to read

        Returns:
            The file contents as bytes
        """
        result = self.client._send_request("fs.readFile", {"uri": uri})
        return bytes(result)

    def write_file(self, uri: str, content: bytes) -> None:
        """
        Write to a file.

        Args:
            uri: The URI of the file to write
            content: The content to write
        """
        self.client._send_request(
            "fs.writeFile", {"uri": uri, "content": list(content)}
        )

    def delete(
        self, uri: str, recursive: bool = False, use_trash: bool = False
    ) -> None:
        """
        Delete a file or directory.

        Args:
            uri: The URI of the file/directory to delete
            recursive: Delete recursively if a directory
            use_trash: Use the OS trash/recycle bin
        """
        options = {"recursive": recursive, "useTrash": use_trash}
        self.client._send_request(
            "fs.delete", {"uri": uri, "options": options}
        )

    def rename(
        self, source: str, target: str, overwrite: bool = False
    ) -> None:
        """
        Rename/move a file or directory.

        Args:
            source: Source URI
            target: Target URI
            overwrite: Overwrite if target exists
        """
        options = {"overwrite": overwrite}
        self.client._send_request(
            "fs.rename",
            {"source": source, "target": target, "options": options},
        )

    def copy(self, source: str, target: str, overwrite: bool = False) -> None:
        """
        Copy a file or directory.

        Args:
            source: Source URI
            target: Target URI
            overwrite: Overwrite if target exists
        """
        options = {"overwrite": overwrite}
        self.client._send_request(
            "fs.copy", {"source": source, "target": target, "options": options}
        )

    def create_directory(self, uri: str) -> None:
        """
        Create a directory.

        Args:
            uri: The URI of the directory to create
        """
        self.client._send_request("fs.createDirectory", {"uri": uri})

    def read_directory(self, uri: str) -> List[Tuple[str, int]]:
        """
        Read a directory.

        Args:
            uri: The URI of the directory to read

        Returns:
            List of (name, type) tuples where type is from FileType
        """
        result = self.client._send_request("fs.readDirectory", {"uri": uri})
        return [(entry["name"], entry["type"]) for entry in result]

    def stat(self, uri: str) -> FileStat:
        """
        Get file metadata.

        Args:
            uri: The URI of the file

        Returns:
            File metadata
        """
        result = self.client._send_request("fs.stat", {"uri": uri})
        return FileStat(result)

    # Convenience methods for common operations
    def read_text(self, uri: str, encoding: str = "utf-8") -> str:
        """
        Read a text file.

        Args:
            uri: The URI of the file
            encoding: Text encoding (default: utf-8)

        Returns:
            File contents as string
        """
        content = self.read_file(uri)
        return content.decode(encoding)

    def write_text(self, uri: str, text: str, encoding: str = "utf-8") -> None:
        """
        Write a text file.

        Args:
            uri: The URI of the file
            text: Text content to write
            encoding: Text encoding (default: utf-8)
        """
        content = text.encode(encoding)
        self.write_file(uri, content)

    def exists(self, uri: str) -> bool:
        """
        Check if a file or directory exists.

        Args:
            uri: The URI to check

        Returns:
            True if exists, False otherwise
        """
        try:
            self.stat(uri)
            return True
        except Exception:
            return False

    def is_directory(self, uri: str) -> bool:
        """
        Check if a URI points to a directory.

        Args:
            uri: The URI to check

        Returns:
            True if directory, False otherwise
        """
        try:
            stat = self.stat(uri)
            return stat.type == FileType.Directory
        except Exception:
            return False

    def is_file(self, uri: str) -> bool:
        """
        Check if a URI points to a file.

        Args:
            uri: The URI to check

        Returns:
            True if file, False otherwise
        """
        try:
            stat = self.stat(uri)
            return stat.type == FileType.File
        except Exception:
            return False
