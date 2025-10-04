# Quick Start

Get started with VSCode Sockpuppet in 5 minutes.

## Your First Script

```python
from vscode_sockpuppet import VSCodeClient

# Connect to VS Code
with VSCodeClient() as vscode:
    # Show a message
    vscode.window.show_information_message("Hello from Python!")
    
    # Get active editor
    editor = vscode.window.active_text_editor
    if editor:
        doc = editor.document
        print(f"Editing: {doc.file_name}")
        print(f"Lines: {doc.line_count}")
```

## Common Operations

### Show Messages

```python
with VSCodeClient() as vscode:
    # Information
    vscode.window.show_information_message("Operation complete!")
    
    # Warning
    vscode.window.show_warning_message("Are you sure?", "Yes", "No")
    
    # Error
    vscode.window.show_error_message("Something went wrong!")
```

### Work with Files

```python
with VSCodeClient() as vscode:
    # List workspace folders
    folders = vscode.workspace.workspace_folders
    for folder in folders:
        print(f"Folder: {folder['name']}")
    
    # Get all open documents
    docs = vscode.workspace.text_documents()
    for doc in docs:
        print(f"{doc.file_name}: {doc.line_count} lines")
```

### Edit Text

```python
with VSCodeClient() as vscode:
    editor = vscode.window.active_text_editor
    if editor:
        # Insert text
        success = editor.edit(lambda edit: edit.insert(0, 0, "// Hello\n"))
        
        # Get selected text
        selection = editor.selection
        text = editor.document.get_text(selection)
```

## Next Steps

- [Examples](examples.md) - More practical examples
- [API Reference](../api/index.md) - Complete API documentation
