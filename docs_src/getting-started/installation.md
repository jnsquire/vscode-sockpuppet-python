# Getting Started with VSCode Sockpuppet

## Installation

Install the VSCode Sockpuppet extension and Python package to get started.

### 1. Install VS Code Extension

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "VSCode Sockpuppet"
4. Click Install

### 2. Install Python Package

Using pip:

```bash
pip install vscode-sockpuppet
```

Using uv (recommended):

```bash
uv pip install vscode-sockpuppet
```

### 3. Verify Installation

Create a test script:

```python
from vscode_sockpuppet import VSCodeClient

with VSCodeClient() as vscode:
    vscode.window.show_information_message("Hello from Python!")
```

Run it while VS Code is open with the extension active.

## Next Steps

- [Quick Start Guide](quickstart.md) - Learn the basics
- [Examples](examples.md) - See practical use cases
- [API Reference](../api/index.md) - Explore the full API
