"""
Example demonstrating editor decoration types with automatic disposal.

This example shows how to create and apply text decorations to highlight
code ranges in the active editor. The DecorationType object automatically
disposes server-side resources when it goes out of scope.
"""

from vscode_sockpuppet import RangeDict, VSCodeClient

client = VSCodeClient()

# Create decoration types with different styles
highlight_decoration = client.editor.create_decoration_type(
    {
        "backgroundColor": "rgba(255, 255, 0, 0.3)",  # Yellow highlight
        "border": "1px solid yellow",
    }
)

error_decoration = client.editor.create_decoration_type(
    {
        "backgroundColor": "rgba(255, 0, 0, 0.2)",  # Red background
        "border": "2px solid red",
        "borderRadius": "3px",
    }
)

print(f"Created decorations: {highlight_decoration}, {error_decoration}")

# Apply decorations to ranges in the active editor
# Using RangeDict for type safety (IDE autocomplete will help!)
highlight_ranges: list[RangeDict] = [
    {
        "start": {"line": 0, "character": 0},
        "end": {"line": 0, "character": 10},
    },
    {
        "start": {"line": 2, "character": 5},
        "end": {"line": 2, "character": 15},
    },
]

error_ranges: list[RangeDict] = [
    {
        "start": {"line": 5, "character": 0},
        "end": {"line": 5, "character": 20},
    },
]

client.editor.set_decorations(highlight_decoration, highlight_ranges)
client.editor.set_decorations(error_decoration, error_ranges)

print("Decorations applied! Check the active editor.")

# Manual disposal example (optional - automatic on script end)
input("Press Enter to manually dispose decorations...")

highlight_decoration.dispose()
error_decoration.dispose()

print("Decorations disposed manually.")

# Note: If you don't call dispose() manually, the decorations will be
# automatically disposed when the DecorationType objects are garbage collected
# (e.g., when the script ends).
