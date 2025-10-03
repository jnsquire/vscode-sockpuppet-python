"""
Diagnostics operations for VS Code
"""

from typing import TYPE_CHECKING, List, Optional, Union

if TYPE_CHECKING:
    from .client import VSCodeClient


class DiagnosticSeverity:
    """Diagnostic severity levels."""

    Error = 0
    Warning = 1
    Information = 2
    Hint = 3


class DiagnosticRelatedInformation:
    """Related information for a diagnostic."""

    def __init__(self, location: dict, message: str):
        """
        Create diagnostic related information.

        Args:
            location: Location dict with uri and range
            message: Related message
        """
        self.location = location
        self.message = message

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "location": self.location,
            "message": self.message,
        }


class Diagnostic:
    """Represents a diagnostic, such as a compiler error or warning."""

    def __init__(
        self,
        range: dict,
        message: str,
        severity: Union[int, str] = DiagnosticSeverity.Error,
        source: Optional[str] = None,
        code: Optional[Union[str, int]] = None,
    ):
        """
        Create a diagnostic.

        Args:
            range: Range dict with start and end positions
            message: Diagnostic message
            severity: Severity level (Error, Warning, Information, Hint)
            source: Source of the diagnostic (e.g., 'python', 'mypy')
            code: Diagnostic code
        """
        self.range = range
        self.message = message
        self.severity = severity
        self.source = source
        self.code = code
        self.related_information: List[DiagnosticRelatedInformation] = []

    def add_related_information(self, location: dict, message: str) -> "Diagnostic":
        """
        Add related information to this diagnostic.

        Args:
            location: Location dict with uri and range
            message: Related message

        Returns:
            Self for chaining
        """
        self.related_information.append(DiagnosticRelatedInformation(location, message))
        return self

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "range": self.range,
            "message": self.message,
            "severity": self.severity,
        }
        if self.source:
            result["source"] = self.source
        if self.code is not None:
            result["code"] = self.code
        if self.related_information:
            result["relatedInformation"] = [info.to_dict() for info in self.related_information]
        return result


class DiagnosticCollection:
    """A collection of diagnostics for a specific source."""

    def __init__(self, client: "VSCodeClient", name: str):
        """
        Create a diagnostic collection.

        Args:
            client: The VS Code client
            name: Name of the collection
        """
        self.client = client
        self.name = name

    def set(self, uri: str, diagnostics: Optional[List[Diagnostic]] = None) -> None:
        """
        Set diagnostics for a URI.

        Args:
            uri: The URI to set diagnostics for
            diagnostics: List of diagnostics (None or [] clears)
        """
        diag_list = [d.to_dict() for d in diagnostics] if diagnostics else []
        self.client._send_request(
            "languages.setDiagnostics",
            {"name": self.name, "uri": uri, "diagnostics": diag_list},
        )

    def delete(self, uri: str) -> None:
        """
        Delete diagnostics for a URI.

        Args:
            uri: The URI to clear diagnostics for
        """
        self.client._send_request("languages.clearDiagnostics", {"name": self.name, "uri": uri})

    def clear(self) -> None:
        """Clear all diagnostics in this collection."""
        self.client._send_request("languages.clearDiagnostics", {"name": self.name})

    def dispose(self) -> None:
        """Dispose this diagnostic collection."""
        self.client._send_request("languages.disposeDiagnosticCollection", {"name": self.name})


class Languages:
    """Language-related operations for VS Code."""

    def __init__(self, client: "VSCodeClient"):
        self.client = client
        self._collections: dict[str, DiagnosticCollection] = {}

    def create_diagnostic_collection(self, name: str = "default") -> DiagnosticCollection:
        """
        Create a diagnostic collection.

        Args:
            name: Name of the collection (default: 'default')

        Returns:
            A new diagnostic collection
        """
        if name in self._collections:
            return self._collections[name]

        self.client._send_request("languages.createDiagnosticCollection", {"name": name})
        collection = DiagnosticCollection(self.client, name)
        self._collections[name] = collection
        return collection


# Helper functions for creating ranges and positions
def create_range(start_line: int, start_char: int, end_line: int, end_char: int) -> dict:
    """
    Create a range object.

    Args:
        start_line: Start line (0-based)
        start_char: Start character (0-based)
        end_line: End line (0-based)
        end_char: End character (0-based)

    Returns:
        Range dictionary
    """
    return {
        "start": {"line": start_line, "character": start_char},
        "end": {"line": end_line, "character": end_char},
    }


def create_position(line: int, character: int) -> dict:
    """
    Create a position object.

    Args:
        line: Line number (0-based)
        character: Character position (0-based)

    Returns:
        Position dictionary
    """
    return {"line": line, "character": character}


def create_location(uri: str, range: dict) -> dict:
    """
    Create a location object.

    Args:
        uri: The URI of the location
        range: The range in the document

    Returns:
        Location dictionary
    """
    return {"uri": uri, "range": range}
