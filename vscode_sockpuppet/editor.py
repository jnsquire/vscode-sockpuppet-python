"""
Editor operations for VS Code
"""

from typing import TYPE_CHECKING, Callable, Optional, Union

from .window_types import DecorationRenderOptions, PositionDict, RangeDict

if TYPE_CHECKING:
    from .client import VSCodeClient
    from .document import Position, Range

# Type aliases for flexibility
PositionType = Union[PositionDict, "Position"]
RangeType = Union[RangeDict, "Range"]


def _normalize_position(pos: PositionType) -> PositionDict:
    """Convert Position (dataclass or dict) to dict format."""
    if isinstance(pos, dict):
        return pos  # type: ignore[return-value]
    # It's a Position dataclass from document.py
    return {"line": pos.line, "character": pos.character}


def _normalize_range(rng: RangeType) -> RangeDict:
    """Convert Range (dataclass or dict) to dict format."""
    if isinstance(rng, dict):
        return rng  # type: ignore[return-value]
    # It's a Range dataclass from document.py
    return {
        "start": _normalize_position(rng.start),
        "end": _normalize_position(rng.end),
    }


class DecorationType:
    """
    Wrapper for a text editor decoration type.

    This object automatically disposes the server-side decoration
    resource when it's garbage collected, preventing resource leaks.
    """

    def __init__(self, client: "VSCodeClient", decoration_id: str):
        self._client = client
        self.id = decoration_id
        self._disposed = False

    def dispose(self) -> dict:
        """
        Manually dispose the decoration type on the server.

        Returns:
            Success status from server
        """
        if self._disposed:
            return {"success": True}

        self._disposed = True
        return self._client._send_request(
            "window.disposeTextEditorDecorationType",
            {"decorationId": self.id},
        )

    def __del__(self):
        """Best-effort cleanup when object is garbage collected."""
        if not self._disposed:
            try:
                self._client._send_request(
                    "window.disposeTextEditorDecorationType",
                    {"decorationId": self.id},
                )
            except Exception:
                # Silently ignore errors during cleanup
                pass

    def __repr__(self) -> str:
        status = "disposed" if self._disposed else "active"
        return f"DecorationType(id={self.id!r}, {status})"


class Editor:
    """VS Code editor operations."""

    def __init__(self, client: "VSCodeClient"):
        self.client = client

    def get_selection(self) -> dict:
        """
        Get the current selection in the active editor.

        Returns:
            Selection information with start, end positions and text
        """
        return self.client._send_request("window.activeTextEditor.selection")

    def set_selection(
        self, start_line: int, start_char: int, end_line: int, end_char: int
    ) -> dict:
        """
        Set the selection in the active editor.

        Args:
            start_line: Starting line number
            start_char: Starting character position
            end_line: Ending line number
            end_char: Ending character position

        Returns:
            Success status
        """
        return self.client._send_request(
            "window.activeTextEditor.setSelection",
            {
                "start": {"line": start_line, "character": start_char},
                "end": {"line": end_line, "character": end_char},
            },
        )

    def insert_text(self, line: int, character: int, text: str) -> dict:
        """
        Insert text at a position.

        Args:
            line: Line number
            character: Character position
            text: Text to insert

        Returns:
            Success status
        """
        return self.client._send_request(
            "window.activeTextEditor.edit",
            {
                "edits": [
                    {
                        "type": "insert",
                        "range": {
                            "start": {"line": line, "character": character},
                            "end": {"line": line, "character": character},
                        },
                        "text": text,
                    }
                ]
            },
        )

    def delete_range(self, start_line: int, start_char: int, end_line: int, end_char: int) -> dict:
        """
        Delete text in a range.

        Args:
            start_line: Starting line number
            start_char: Starting character position
            end_line: Ending line number
            end_char: Ending character position

        Returns:
            Success status
        """
        return self.client._send_request(
            "window.activeTextEditor.edit",
            {
                "edits": [
                    {
                        "type": "delete",
                        "range": {
                            "start": {
                                "line": start_line,
                                "character": start_char,
                            },
                            "end": {"line": end_line, "character": end_char},
                        },
                    }
                ]
            },
        )

    def replace_text(
        self,
        start_line: int,
        start_char: int,
        end_line: int,
        end_char: int,
        text: str,
    ) -> dict:
        """
        Replace text in a range.

        Args:
            start_line: Starting line number
            start_char: Starting character position
            end_line: Ending line number
            end_char: Ending character position
            text: Replacement text

        Returns:
            Success status
        """
        return self.client._send_request(
            "window.activeTextEditor.edit",
            {
                "edits": [
                    {
                        "type": "replace",
                        "range": {
                            "start": {
                                "line": start_line,
                                "character": start_char,
                            },
                            "end": {"line": end_line, "character": end_char},
                        },
                        "text": text,
                    }
                ]
            },
        )

    def edit(
        self,
        callback: Callable[["EditBuilder"], None],
        undo_stop_before: bool = True,
        undo_stop_after: bool = True,
    ) -> bool:
        """
        Perform complex edits with multiple operations atomically.

        This is the preferred way to make multiple edits as they will
        be applied together in a single transaction.

        Args:
            callback: Function that receives an EditBuilder and adds edits
            undo_stop_before: Add undo stop before edits
            undo_stop_after: Add undo stop after edits

        Returns:
            True if edits were applied successfully

        Example:
            def make_edits(edit_builder):
                edit_builder.insert(0, 0, "# Header\\n")
                edit_builder.replace(5, 0, 5, 10, "new text")
                edit_builder.delete(10, 0, 11, 0)

            editor.edit(make_edits)
        """
        edit_builder = EditBuilder()
        callback(edit_builder)

        result = self.client._send_request(
            "window.activeTextEditor.edit",
            {
                "edits": edit_builder.edits,
                "undoStopBefore": undo_stop_before,
                "undoStopAfter": undo_stop_after,
            },
        )
        return result.get("success", False)

    def insert_snippet(
        self,
        snippet: str,
        location: Optional[Union[PositionType, RangeType]] = None,
        undo_stop_before: bool = True,
        undo_stop_after: bool = True,
    ) -> bool:
        """
        Insert a snippet at the current selection or specified location.

        Args:
            snippet: Snippet string with placeholders ($1, $2, etc.)
            location: Position/Range (dict or dataclass), or None for current
            undo_stop_before: Add undo stop before insertion
            undo_stop_after: Add undo stop after insertion

        Returns:
            True if snippet was inserted successfully

        Example:
            # Insert at current position
            editor.insert_snippet("console.log('$1');$0")

            # Insert at specific position (dict)
            editor.insert_snippet(
                "for (let ${1:i} = 0; $1 < ${2:10}; $1++) {\\n\\t$0\\n}",
                location={"line": 5, "character": 0}
            )

            # Or use Position/Range from document.py
            from vscode_sockpuppet.document import Position
            editor.insert_snippet("$0", location=Position(5, 0))
        """
        # Normalize location to dict format
        normalized_location = None
        if location is not None:
            if isinstance(location, dict):
                # Check if it's a Position or Range dict
                if "start" in location:
                    normalized_location = _normalize_range(
                        location  # type: ignore[arg-type]
                    )
                else:
                    normalized_location = _normalize_position(
                        location  # type: ignore[arg-type]
                    )
            else:
                # It's a dataclass - check if Position or Range
                if hasattr(location, "start"):
                    normalized_location = _normalize_range(
                        location  # type: ignore[arg-type]
                    )
                else:
                    normalized_location = _normalize_position(
                        location  # type: ignore[arg-type]
                    )

        result = self.client._send_request(
            "window.activeTextEditor.insertSnippet",
            {
                "snippet": snippet,
                "location": normalized_location,
                "undoStopBefore": undo_stop_before,
                "undoStopAfter": undo_stop_after,
            },
        )
        return result.get("success", False)

    def reveal_range(
        self,
        start_line: int,
        start_char: int,
        end_line: int,
        end_char: int,
        reveal_type: Optional[str] = None,
    ) -> dict:
        """
        Scroll to make a range visible in the editor.

        Args:
            start_line: Starting line number
            start_char: Starting character position
            end_line: Ending line number
            end_char: Ending character position
            reveal_type: How to reveal:
                - None/Default: Scroll minimally to reveal range
                - 'InCenter': Scroll to center range in viewport
                - 'InCenterIfOutsideViewport': Center only if outside
                - 'AtTop': Scroll to show range at top

        Returns:
            Success status

        Example:
            # Scroll to line 100
            editor.reveal_range(100, 0, 100, 0)

            # Scroll and center line 50
            editor.reveal_range(50, 0, 50, 0, 'InCenter')
        """
        return self.client._send_request(
            "window.activeTextEditor.revealRange",
            {
                "range": {
                    "start": {"line": start_line, "character": start_char},
                    "end": {"line": end_line, "character": end_char},
                },
                "revealType": reveal_type,
            },
        )

    def get_selections(self) -> list[dict]:
        """
        Get all selections in the active editor.

        Returns:
            List of selection objects with start, end, and text

        Example:
            selections = editor.get_selections()
            for sel in selections:
                print(f"Selected: {sel['text']}")
        """
        return self.client._send_request("window.activeTextEditor.selections")

    def set_selections(self, selections: list[RangeType]) -> dict:
        """
        Set multiple selections (multi-cursor support).

        Args:
            selections: List of Range objects (dict or dataclass)

        Returns:
            Success status

        Example:
            # Using dicts
            editor.set_selections([
                {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 5}
                },
                {
                    "start": {"line": 2, "character": 0},
                    "end": {"line": 2, "character": 5}
                }
            ])

            # Or using Range from document.py
            from vscode_sockpuppet.document import Range, Position
            editor.set_selections([
                Range(Position(0, 0), Position(0, 5)),
                Range(Position(2, 0), Position(2, 5))
            ])
        """
        # Normalize all ranges to dict format
        normalized_selections = [_normalize_range(sel) for sel in selections]

        return self.client._send_request(
            "window.activeTextEditor.setSelections",
            {"selections": normalized_selections},
        )

    def get_options(self) -> dict:
        """
        Get editor options (tab size, insert spaces, etc.).

        Returns:
            Dict with editor options

        Example:
            options = editor.get_options()
            print(f"Tab size: {options['tabSize']}")
            print(f"Insert spaces: {options['insertSpaces']}")
        """
        return self.client._send_request("window.activeTextEditor.options")

    def set_options(self, options: dict) -> dict:
        """
        Set editor options.

        Args:
            options: Dict with options to set (tabSize, insertSpaces, etc.)

        Returns:
            Success status

        Example:
            editor.set_options({
                "tabSize": 2,
                "insertSpaces": True
            })
        """
        return self.client._send_request(
            "window.activeTextEditor.setOptions",
            {"options": options},
        )

    def get_visible_ranges(self) -> list[dict]:
        """
        Get the ranges that are currently visible in the editor.

        Returns:
            List of visible range objects

        Example:
            ranges = editor.get_visible_ranges()
            for r in ranges:
                print(f"Visible: lines {r['start']['line']}-"
                      f"{r['end']['line']}")
        """
        return self.client._send_request("window.activeTextEditor.visibleRanges")

    def get_view_column(self) -> Optional[int]:
        """
        Get the view column of the active editor.

        Returns:
            View column number (1-9), or None

        Example:
            column = editor.get_view_column()
            print(f"Editor in column: {column}")
        """
        return self.client._send_request("window.activeTextEditor.viewColumn")

    def create_decoration_type(self, options: DecorationRenderOptions) -> DecorationType:
        """
        Create a text editor decoration type.

        The returned DecorationType object will automatically dispose the
        server-side resource when garbage collected. Call dispose() manually
        for immediate cleanup.

        Args:
            options: DecorationRenderOptions dict with styling options

        Returns:
            DecorationType object with `id` attribute and dispose() method

        Example:
            from vscode_sockpuppet import DecorationRenderOptions

            # Type-safe decoration options
            options: DecorationRenderOptions = {
                "backgroundColor": "rgba(255, 0, 0, 0.3)",
                "border": "1px solid red",
                "borderRadius": "3px",
                "isWholeLine": True,
                "overviewRulerLane": 2,  # Center
                "light": {
                    "backgroundColor": "rgba(255, 0, 0, 0.1)"
                },
                "dark": {
                    "backgroundColor": "rgba(255, 0, 0, 0.3)"
                }
            }
            decoration = editor.create_decoration_type(options)
            editor.set_decorations(decoration, [range1, range2])

            # Manual disposal
            decoration.dispose()
        """
        result = self.client._send_request(
            "window.createTextEditorDecorationType", {"options": options}
        )
        return DecorationType(self.client, result.get("id"))

    def set_decorations(
        self, decoration: Union[DecorationType, str], ranges: list[RangeType]
    ) -> dict:
        """
        Apply decorations to the active text editor.

        Args:
            decoration: DecorationType object or decoration ID string
            ranges: List of Range objects (dict or dataclass)

        Returns:
            Success status

        Example:
            decoration = editor.create_decoration_type({
                "backgroundColor": "yellow"
            })

            # Using dicts
            ranges = [{
                "start": {"line": 0, "character": 0},
                "end": {"line": 0, "character": 10}
            }]
            editor.set_decorations(decoration, ranges)

            # Or using Range from document.py
            from vscode_sockpuppet.document import Range, Position
            ranges = [Range(Position(0, 0), Position(0, 10))]
            editor.set_decorations(decoration, ranges)
        """
        if isinstance(decoration, DecorationType):
            dec_id = decoration.id
        else:
            dec_id = decoration

        # Normalize all ranges to dict format
        normalized_ranges = [_normalize_range(r) for r in ranges]

        return self.client._send_request(
            "window.activeTextEditor.setDecorations",
            {"decorationId": dec_id, "ranges": normalized_ranges},
        )


class EditBuilder:
    """
    Builder for creating multiple text edits.

    Used with Editor.edit() to batch multiple edits together.
    """

    def __init__(self):
        self.edits = []

    def insert(self, line: int, character: int, text: str) -> "EditBuilder":
        """
        Add an insert operation.

        Args:
            line: Line number
            character: Character position
            text: Text to insert

        Returns:
            Self for chaining
        """
        self.edits.append(
            {
                "type": "insert",
                "range": {
                    "start": {"line": line, "character": character},
                    "end": {"line": line, "character": character},
                },
                "text": text,
            }
        )
        return self

    def delete(
        self, start_line: int, start_char: int, end_line: int, end_char: int
    ) -> "EditBuilder":
        """
        Add a delete operation.

        Args:
            start_line: Starting line number
            start_char: Starting character position
            end_line: Ending line number
            end_char: Ending character position

        Returns:
            Self for chaining
        """
        self.edits.append(
            {
                "type": "delete",
                "range": {
                    "start": {"line": start_line, "character": start_char},
                    "end": {"line": end_line, "character": end_char},
                },
            }
        )
        return self

    def replace(
        self,
        start_line: int,
        start_char: int,
        end_line: int,
        end_char: int,
        text: str,
    ) -> "EditBuilder":
        """
        Add a replace operation.

        Args:
            start_line: Starting line number
            start_char: Starting character position
            end_line: Ending line number
            end_char: Ending character position
            text: Replacement text

        Returns:
            Self for chaining
        """
        self.edits.append(
            {
                "type": "replace",
                "range": {
                    "start": {"line": start_line, "character": start_char},
                    "end": {"line": end_line, "character": end_char},
                },
                "text": text,
            }
        )
        return self
