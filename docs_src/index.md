# VSCode Sockpuppet Python API

Welcome to the VSCode Sockpuppet Python API documentation!

**VSCode Sockpuppet** is a Python library that lets you programmatically control Visual Studio Code from Python scripts. It provides a clean, typed API that mirrors the VS Code Extension API.

## Key Features

- 🎯 **Full VS Code Control** - Access windows, editors, documents, and workspace
- 🔄 **Real-time Events** - Subscribe to editor changes, file events, and more
- 🎨 **Rich UI** - Create webviews, show messages, and dialogs
- 📝 **Document Manipulation** - Read and edit text documents with full API
- 🔌 **Extension Integration** - Launched by VS Code extensions for seamless integration
- 🐍 **Pythonic API** - Clean, typed, intuitive interface

## Quick Example

```python
from vscode_sockpuppet import VSCodeClient

with VSCodeClient() as vscode:
    # Show a message
    vscode.window.show_information_message("Hello from Python!")
    
    # Get the active editor
    editor = vscode.window.active_text_editor
    if editor:
        doc = editor.document
        print(f"Editing: {doc.file_name}")
        print(f"Language: {doc.language_id}")
        print(f"Lines: {doc.line_count}")
    
    # List workspace folders
    folders = vscode.workspace.workspace_folders
    for folder in folders:
        print(f"Workspace: {folder['name']} at {folder['uri']}")
```

## Installation

```bash
pip install vscode-sockpuppet
```

Or with `uv`:

```bash
uv pip install vscode-sockpuppet
```

## Getting Started

1. **[Quick Start Guide](getting-started/quickstart.md)** - Get up and running in 5 minutes
2. **[API Reference](api/index.md)** - Complete API documentation
3. **[Examples](getting-started/examples.md)** - Working code examples

## Main Components

- **[VSCodeClient](api/client.md)** - Main entry point for connecting to VS Code
- **[Window](api/window.md)** - Window operations (messages, dialogs, editors)
- **[Workspace](api/workspace.md)** - Workspace operations (files, configuration)
- **[Editor](api/editor.md)** - Text editor manipulation and decorations
- **[TextDocument](api/document.md)** - Document access and text operations
- **[Events](api/events.md)** - Event subscription system

## Architecture

VSCode Sockpuppet consists of two parts:

1. **VS Code Extension** (TypeScript) - Runs inside VS Code, provides WebSocket/Named Pipe server
2. **Python Package** (this library) - Connects to VS Code and provides the API

The extension must be installed and running in VS Code for the Python client to work.

## Support

- 📖 [Documentation](https://github.com/jnsquire/vscode-sockpuppet-extension/tree/main/docs)
- 🐛 [Report Issues](https://github.com/jnsquire/vscode-sockpuppet-extension/issues)
- 💬 [Discussions](https://github.com/jnsquire/vscode-sockpuppet-extension/discussions)

## License

MIT License - see [LICENSE](about/license.md) for details.
