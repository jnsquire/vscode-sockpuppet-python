"""
Advanced Text Editor Operations

This example demonstrates advanced text editing capabilities including:
- Multi-operation atomic edits with EditBuilder
- Snippet insertion with placeholders
- Scroll control and viewport management
- Multiple cursor selection and editing
- Reading and modifying editor options
- Querying visible ranges and view column
"""

from vscode_sockpuppet import VSCodeClient


def demonstrate_atomic_edits(client: VSCodeClient):
    """Show how to perform multiple edits atomically using EditBuilder."""
    print("\n=== Atomic Multi-Operation Edits ===")
    editor = client.editor
    if not editor:
        print("No active editor")
        return

    # Perform multiple edits in a single atomic operation
    def apply_edits(builder):
        # Insert a header at the top
        builder.insert(0, 0, "# Code Review Comments\n\n")

        # Insert a comment at line 5
        builder.insert(5, 0, "    # TODO: Optimize this section\n")

        # Replace text at line 10
        builder.replace(10, 0, 10, 20, "improved_function_name")

        # Delete a line at line 15
        builder.delete(15, 0, 16, 0)

    editor.edit(apply_edits, undo_stop_before=True, undo_stop_after=True)
    print("Applied multiple edits atomically")


def demonstrate_snippet_insertion(client: VSCodeClient):
    """Show how to insert snippets with placeholders."""
    print("\n=== Snippet Insertion ===")
    editor = client.editor
    if not editor:
        print("No active editor")
        return

    # Insert a function template with tab stops
    snippet = """def ${1:function_name}(${2:params}):
    \"\"\"${3:Description}\"\"\"
    ${0:pass}
"""

    # Insert at current cursor position
    editor.insert_snippet(snippet)
    print("Inserted function template snippet")

    # Insert a class template at a specific position
    class_snippet = """class ${1:ClassName}:
    \"\"\"${2:Class description}\"\"\"

    def __init__(self, ${3:args}):
        ${0:pass}
"""

    editor.insert_snippet(class_snippet, location={"line": 20, "character": 0})
    print("Inserted class template at line 20")


def demonstrate_scroll_control(client: VSCodeClient):
    """Show different ways to scroll the editor viewport."""
    print("\n=== Scroll Control ===")
    editor = client.editor
    if not editor:
        print("No active editor")
        return

    # Scroll to line 50 and center it
    editor.reveal_range(50, 0, 50, 0, reveal_type="InCenter")
    print("Scrolled to line 50 (centered)")

    # Scroll to line 100 and place it at the top
    editor.reveal_range(100, 0, 100, 0, reveal_type="AtTop")
    print("Scrolled to line 100 (at top)")

    # Scroll to a range only if it's outside the viewport
    editor.reveal_range(150, 0, 160, 0, reveal_type="InCenterIfOutsideViewport")
    print("Scrolled to lines 150-160 (if needed)")


def demonstrate_multiple_selections(client: VSCodeClient):
    """Show how to work with multiple cursors/selections."""
    print("\n=== Multiple Selections ===")
    editor = client.editor
    if not editor:
        print("No active editor")
        return

    # Get current selections (could be multiple with multi-cursor)
    selections = editor.get_selections()
    print(f"Current selections: {len(selections)}")
    for i, sel in enumerate(selections):
        print(f"  Selection {i + 1}: {sel}")

    # Set multiple selections at specific locations
    # This creates three cursors
    editor.set_selections(
        [
            {"anchor": {"line": 10, "character": 0}, "active": {"line": 10, "character": 0}},
            {"anchor": {"line": 20, "character": 0}, "active": {"line": 20, "character": 0}},
            {"anchor": {"line": 30, "character": 0}, "active": {"line": 30, "character": 0}},
        ]
    )
    print("Set three cursors at lines 10, 20, and 30")

    # Now any edit will apply to all three locations
    # Note: Use edit() with EditBuilder for multi-cursor edits
    print("Set three cursors ready for editing")


def demonstrate_editor_options(client: VSCodeClient):
    """Show how to read and modify editor options."""
    print("\n=== Editor Options ===")
    editor = client.editor
    if not editor:
        print("No active editor")
        return

    # Get current options
    options = editor.get_options()
    print("Current options:")
    print(f"  Tab size: {options.get('tabSize')}")
    print(f"  Insert spaces: {options.get('insertSpaces')}")
    print(f"  Cursor style: {options.get('cursorStyle')}")
    print(f"  Line numbers: {options.get('lineNumbers')}")

    # Modify options (e.g., switch to tabs instead of spaces)
    editor.set_options({"insertSpaces": False, "tabSize": 4})
    print("\nChanged to tabs (size 4)")

    # Verify the change
    new_options = editor.get_options()
    print(f"New insert spaces: {new_options.get('insertSpaces')}")


def demonstrate_viewport_queries(client: VSCodeClient):
    """Show how to query viewport information."""
    print("\n=== Viewport Information ===")
    editor = client.editor
    if not editor:
        print("No active editor")
        return

    # Get visible ranges (what's currently in view)
    visible_ranges = editor.get_visible_ranges()
    print(f"Visible ranges: {len(visible_ranges)}")
    for i, range_data in enumerate(visible_ranges):
        start = range_data["start"]
        end = range_data["end"]
        print(f"  Range {i + 1}: lines {start['line']}-{end['line']}")

    # Get view column (which column group the editor is in)
    view_column = editor.get_view_column()
    print(f"View column: {view_column}")
    print("  (1=first column, 2=second column, etc.)")


def demonstrate_practical_use_case(client: VSCodeClient):
    """Show a practical use case combining multiple features."""
    print("\n=== Practical Use Case: Code Refactoring ===")
    editor = client.editor
    if not editor:
        print("No active editor")
        return

    # 1. Find all occurrences of a pattern (simulated with known positions)
    occurrences = [
        (10, 5, 10, 15),  # Line 10, chars 5-15
        (25, 8, 25, 18),  # Line 25, chars 8-18
        (40, 3, 40, 13),  # Line 40, chars 3-13
    ]

    # 2. Set multiple selections at those positions
    selections = []
    for start_line, start_char, end_line, end_char in occurrences:
        selections.append(
            {
                "anchor": {"line": start_line, "character": start_char},
                "active": {"line": end_line, "character": end_char},
            }
        )

    editor.set_selections(selections)
    print(f"Found {len(occurrences)} occurrences to refactor")

    # 3. Insert a snippet at all locations simultaneously
    snippet = "${1:new_name}"
    editor.insert_snippet(snippet)
    print("Inserted refactoring snippet at all locations")

    # 4. Scroll to the first occurrence to review
    first_occurrence = occurrences[0]
    editor.reveal_range(
        first_occurrence[0],
        first_occurrence[1],
        first_occurrence[2],
        first_occurrence[3],
        reveal_type="InCenter",
    )
    print("Scrolled to first occurrence for review")


def main():
    """Run all advanced editor demonstrations."""
    with VSCodeClient() as client:
        print("=== Advanced Editor Operations Demo ===")
        print("Make sure you have a file open in VS Code!")

        # Wait for connection
        import time

        time.sleep(1)

        # Run demonstrations
        demonstrate_atomic_edits(client)
        time.sleep(0.5)

        demonstrate_snippet_insertion(client)
        time.sleep(0.5)

        demonstrate_scroll_control(client)
        time.sleep(0.5)

        demonstrate_multiple_selections(client)
        time.sleep(0.5)

        demonstrate_editor_options(client)
        time.sleep(0.5)

        demonstrate_viewport_queries(client)
        time.sleep(0.5)

        demonstrate_practical_use_case(client)

        print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
