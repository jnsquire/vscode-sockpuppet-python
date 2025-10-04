# Examples

Practical examples showing common use cases.

## Example 1: List Open Files

```python
from vscode_sockpuppet import VSCodeClient

with VSCodeClient() as vscode:
    docs = vscode.workspace.text_documents()
    
    print(f"\n📁 {len(docs)} open documents:\n")
    for doc in docs:
        status = "📝" if doc.is_dirty else "✓"
        print(f"{status} {doc.file_name}")
        print(f"   Language: {doc.language_id}")
        print(f"   Lines: {doc.line_count}")
        print()
```

## Example 2: Find and Replace

```python
from vscode_sockpuppet import VSCodeClient, Position

with VSCodeClient() as vscode:
    editor = vscode.window.active_text_editor
    if not editor:
        print("No active editor")
        return
    
    doc = editor.document
    text = doc.get_text()
    
    # Find all occurrences of "TODO"
    lines_with_todo = []
    for i in range(doc.line_count):
        line = doc.line_at(i)
        if "TODO" in line.text:
            lines_with_todo.append((i, line.text))
    
    print(f"Found {len(lines_with_todo)} TODOs:")
    for line_num, text in lines_with_todo:
        print(f"  Line {line_num}: {text.strip()}")
```

## Example 3: Create Webview

```python
from vscode_sockpuppet import VSCodeClient

with VSCodeClient() as vscode:
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: var(--vscode-font-family);
                color: var(--vscode-editor-foreground);
                padding: 20px;
            }
        </style>
    </head>
    <body>
        <h1>Hello from Python!</h1>
        <p>This webview was created by a Python script.</p>
    </body>
    </html>
    """
    
    panel = vscode.window.create_webview_panel(
        title="Python Webview",
        html=html
    )
```

## Example 4: Monitor Events

```python
from vscode_sockpuppet import VSCodeClient
import time

with VSCodeClient() as vscode:
    # Subscribe to editor changes
    def on_editor_change(editor):
        if editor:
            print(f"Now editing: {editor.document.file_name}")
    
    vscode.window.on_did_change_active_text_editor(on_editor_change)
    
    print("Monitoring editor changes... (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped monitoring")
```

## More Examples

See the [examples directory](https://github.com/jnsquire/vscode-sockpuppet-python/tree/main/examples) for more:

- Document manipulation
- Decorations
- Terminal management
- Configuration access
- And more!
