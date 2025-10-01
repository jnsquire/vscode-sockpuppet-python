# VSCode Sockpuppet Python Client

Python package for programmatically controlling VS Code through the VSCode Sockpuppet extension.

## Installation

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh  # Unix/macOS
# or
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# Install the package
cd python
uv pip install -e .

# On Windows, also install:
uv pip install -e ".[windows]"

# Or create a virtual environment with uv
uv venv
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate  # Windows
uv pip install -e ".[dev]"
```

### Using pip

```bash
cd python
pip install -e .

# On Windows, also install:
pip install -e ".[windows]"
```

## Usage

```python
from vscode_sockpuppet import VSCodeClient

# Connect to VS Code
with VSCodeClient() as vscode:
    # Show messages
    vscode.window.show_information_message("Hello from Python!")
    
    # Show quick pick
    choice = vscode.window.show_quick_pick(
        ["Option 1", "Option 2", "Option 3"],
        {"placeholder": "Select an option"}
    )
    print(f"Selected: {choice}")
    
    # Get workspace folders
    folders = vscode.workspace.get_workspace_folders()
    print(f"Workspace folders: {folders}")
    
    # Edit the active document
    vscode.editor.insert_text(0, 0, "# Added by Python\n")
    
    # Execute VS Code commands
    vscode.execute_command("workbench.action.files.save")
```

## API Reference

### Window Operations
- `show_information_message(message, *items)` - Show info message
- `show_warning_message(message, *items)` - Show warning
- `show_error_message(message, *items)` - Show error
- `show_quick_pick(items, options)` - Show quick pick menu
- `show_input_box(options)` - Show input box
- `create_output_channel(name, text, show)` - Create output channel
- `create_terminal(name, shell_path, text, show)` - Create terminal
- `set_status_bar_message(text, timeout)` - Set status bar message
- `create_webview_panel(title, html, options)` - Create custom HTML webview

### Editor Operations
- `get_selection()` - Get current selection
- `set_selection(start_line, start_char, end_line, end_char)` - Set selection
- `insert_text(line, character, text)` - Insert text
- `delete_range(start_line, start_char, end_line, end_char)` - Delete text
- `replace_text(start_line, start_char, end_line, end_char, text)` - Replace text

### Workspace Operations
- `open_text_document(uri, content, language)` - Open document
- `save_all(include_untitled)` - Save all files
- `get_workspace_folders()` - Get workspace folders
- `write_to_clipboard(text)` - Write to clipboard
- `read_from_clipboard()` - Read from clipboard
- `open_external(uri)` - Open external URI

### Commands
- `execute_command(command, *args)` - Execute any VS Code command
- `get_commands(filter_internal)` - Get all available commands

## Documentation

For complete documentation, see:
- [Quick Start Guide](../docs/QUICKSTART.md)
- [TextDocument API](../docs/DOCUMENT_API.md)
- [Webview API](../docs/WEBVIEW_API.md)
- [Event Subscriptions](../docs/EVENTS.md)
- [Extension Integration](../docs/EXTENSION_API.md)
- [Development Guide](../docs/DEVELOPMENT.md)

## Examples

- [examples/example.py](examples/example.py) - Basic operations
- [examples/example_events.py](examples/example_events.py) - Event subscriptions
- [examples/example_document.py](examples/example_document.py) - TextDocument API
- [examples/example_webview.py](examples/example_webview.py) - Webview API
