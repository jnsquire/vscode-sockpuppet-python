# API Reference

This section contains the complete API reference for VSCode Sockpuppet, automatically generated from the Python source code docstrings.

## Core Classes

### Client & Connection
- **[VSCodeClient](client.md)** - Main client for connecting to VS Code

### UI & Windows
- **[Window](window.md)** - Window operations, messages, dialogs
- **[Editor](editor.md)** - Text editor operations and decorations
- **[Webview](webview.md)** - Custom HTML panels

### Documents & Files
- **[TextDocument](document.md)** - Document access and text operations
- **[Workspace](workspace.md)** - Workspace folders, files, configuration
- **[FileSystem](filesystem.md)** - File system operations

### Events & Monitoring
- **[Events](events.md)** - Event subscription system
- **[FileWatcher](filewatcher.md)** - File system watching

### UI Components
- **[Terminal](terminal.md)** - Terminal management
- **[Tabs](tabs.md)** - Tab and tab group management
- **[StatusBar](statusbar.md)** - Status bar items
- **[Progress](progress.md)** - Progress indicators

### Development Tools
- **[Diagnostics](diagnostics.md)** - Problem reporting and language features
- **[Configuration](configuration.md)** - Settings and configuration

### Type Definitions
- **[Types](types.md)** - TypedDict definitions for API structures

## API Design Principles

### 1. **Mirror VS Code API**
The Python API closely mirrors the official [VS Code Extension API](https://code.visualstudio.com/api/references/vscode-api), making it familiar to VS Code extension developers.

```python
# VS Code Extension API (TypeScript)
vscode.window.showInformationMessage("Hello!");

# VSCode Sockpuppet (Python) 
vscode.window.show_information_message("Hello!")
```

### 2. **Pythonic Conventions**
- `snake_case` naming instead of `camelCase`
- Properties instead of getters
- Context managers for resource management
- Type hints throughout

### 3. **Type Safety**
Full type hints with TypedDict for options:

```python
from vscode_sockpuppet import QuickPickOptions

options: QuickPickOptions = {
    "placeHolder": "Select an option",
    "canPickMany": False
}
result = vscode.window.show_quick_pick(["A", "B", "C"], options)
```

### 4. **Event System**
VS Code-style event subscriptions:

```python
# Subscribe to editor changes
def on_change(editor):
    print(f"Now editing: {editor.document.file_name}")

vscode.window.on_did_change_active_text_editor(on_change)
```

## Common Patterns

### Context Manager
Always use the context manager for automatic cleanup:

```python
with VSCodeClient() as vscode:
    # Your code here
    pass
# Connection automatically closed
```

### Error Handling
Methods return `None` when operations fail or are dismissed:

```python
result = vscode.window.show_quick_pick(["A", "B", "C"])
if result is None:
    print("User dismissed the picker")
else:
    print(f"Selected: {result}")
```

### Async Operations
Most operations are synchronous, but events use callbacks:

```python
def handle_save(doc):
    print(f"Saved: {doc.file_name}")

vscode.workspace.on_did_save_text_document(handle_save)
```

## Next Steps

- Browse the individual API pages for detailed documentation
- Check out [Examples](../getting-started/examples.md) for practical use cases
- Read the [Development Guide](../guides/development.md) to contribute
