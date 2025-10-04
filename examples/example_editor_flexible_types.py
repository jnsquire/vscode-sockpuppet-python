"""
Example demonstrating editor methods accepting both dict and dataclass types.

This shows how editor methods can now accept Position and Range as either
TypedDict (from window_types) or dataclass (from document).
"""

from vscode_sockpuppet import VSCodeClient
from vscode_sockpuppet.document import Position, Range


def main():
    """Demonstrate editor methods with both dict and dataclass types."""
    with VSCodeClient() as client:
        editor = client.window.editor
        print("Editor Methods with Flexible Types Demo")
        print("=" * 60)

        # Get active document
        docs = client.workspace.text_documents()
        if not docs:
            print("No open documents. Open a file to try this demo.")
            return

        doc = docs[0]
        print(f"Working with: {doc.file_name}")

        # ===================================================================
        # Example 1: insert_snippet with Position dataclass
        # ===================================================================
        print("\n1. Insert snippet with Position dataclass")
        pos = Position(line=0, character=0)
        result = editor.insert_snippet("// Added via dataclass\\n", location=pos)
        print(f"   Result: {result}")

        # ===================================================================
        # Example 2: insert_snippet with Position dict
        # ===================================================================
        print("\n2. Insert snippet with Position dict")
        pos_dict = {"line": 1, "character": 0}
        result = editor.insert_snippet("// Added via dict\\n", location=pos_dict)
        print(f"   Result: {result}")

        # ===================================================================
        # Example 3: insert_snippet with Range dataclass
        # ===================================================================
        print("\n3. Insert snippet with Range dataclass (replaces range)")
        rng = Range(start=Position(2, 0), end=Position(2, 10))
        result = editor.insert_snippet("// Replaced via dataclass", location=rng)
        print(f"   Result: {result}")

        # ===================================================================
        # Example 4: set_selections with Range dataclass
        # ===================================================================
        print("\n4. Set selections with Range dataclass")
        selections = [
            Range(Position(0, 0), Position(0, 5)),
            Range(Position(2, 0), Position(2, 5)),
        ]
        editor.set_selections(selections)
        print("   Multi-cursor selections set with dataclasses")

        # ===================================================================
        # Example 5: set_selections with Range dict
        # ===================================================================
        print("\n5. Set selections with Range dict")
        selections_dict = [
            {"start": {"line": 1, "character": 0}, "end": {"line": 1, "character": 5}},
            {"start": {"line": 3, "character": 0}, "end": {"line": 3, "character": 5}},
        ]
        editor.set_selections(selections_dict)
        print("   Multi-cursor selections set with dicts")

        # ===================================================================
        # Example 6: set_decorations with Range dataclass
        # ===================================================================
        print("\n6. Set decorations with Range dataclass")
        decoration = editor.create_decoration_type({"backgroundColor": "rgba(255, 255, 0, 0.3)"})
        ranges = [
            Range(Position(0, 0), Position(0, 10)),
            Range(Position(1, 0), Position(1, 10)),
        ]
        editor.set_decorations(decoration, ranges)
        print("   Decorations applied with dataclasses")

        # ===================================================================
        # Example 7: set_decorations with Range dict
        # ===================================================================
        print("\n7. Set decorations with Range dict")
        decoration2 = editor.create_decoration_type({"backgroundColor": "rgba(0, 255, 0, 0.3)"})
        ranges_dict = [
            {"start": {"line": 2, "character": 0}, "end": {"line": 2, "character": 10}},
            {"start": {"line": 3, "character": 0}, "end": {"line": 3, "character": 10}},
        ]
        editor.set_decorations(decoration2, ranges_dict)
        print("   Decorations applied with dicts")

        # ===================================================================
        # Example 8: Mixing with document methods
        # ===================================================================
        print("\n8. Using document methods that return dataclasses")
        # Get a line from the document
        line = doc.line_at(0)
        print(f"   Line 0 range: {line.range}")

        # Use the range directly in editor methods
        editor.set_decorations(
            editor.create_decoration_type({"backgroundColor": "rgba(255, 0, 0, 0.3)"}),
            [line.range],  # Range dataclass from document
        )
        print("   Applied decoration using Range from doc.line_at()")

        # Get word range at position
        word_range = doc.get_word_range_at_position(Position(0, 5))
        if word_range:
            print(f"   Word at 0,5: {word_range}")
            editor.set_selections([word_range])
            print("   Selected word using Range from get_word_range_at_position()")

        print("\n" + "=" * 60)
        print("Demo complete!")
        print("\nKey benefits:")
        print("  - Use dicts for quick inline definitions")
        print("  - Use dataclasses for type safety and methods")
        print("  - Mix both styles as needed")
        print("  - Document methods return dataclasses with helper methods")


if __name__ == "__main__":
    main()
