"""
Example: Handling webview panel disposal events

NOTE: This example requires the extension to be running in debug mode
      (Press F5 to launch Extension Development Host)
"""

import time

from vscode_sockpuppet import VSCodeClient, WebviewOptions


class DisposalState:
    """Tracks disposal state for the demo."""

    def __init__(self):
        self.disposal_detected = False

    def mark_disposed(self):
        """Mark the panel as disposed."""
        self.disposal_detected = True


print("=" * 70)
print("WEBVIEW DISPOSAL EVENT DEMO")
print("=" * 70)
print("\nIMPORTANT: Make sure you're running this in the Extension Development")
print("Host (press F5 to launch) so the updated extension is loaded.\n")

with VSCodeClient() as client:
    print("Creating webview panel with disposal event handler...")

    # Create HTML content
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Disposal Event Demo</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                padding: 20px;
                background-color: var(--vscode-editor-background);
                color: var(--vscode-editor-foreground);
            }
            h1 {
                color: var(--vscode-textLink-foreground);
            }
            .info {
                padding: 15px;
                margin: 15px 0;
                border-left: 4px solid var(--vscode-textLink-foreground);
                background-color: var(--vscode-editor-selectionBackground);
            }
        </style>
    </head>
    <body>
        <h1>🗑️ Disposal Event Demo</h1>
        <div class="info">
            <strong>Try this:</strong> Close this panel by clicking the X button
            or pressing Ctrl+W. The Python script will detect the disposal event
            and print a message.
        </div>
        <p>This panel demonstrates the <code>on_did_dispose</code> event.</p>
        <p>The Python script is monitoring when this panel gets closed.</p>
    </body>
    </html>
    """

    # Create webview with JavaScript enabled
    options = WebviewOptions(enable_scripts=True, retain_context_when_hidden=True)

    panel = client.window.create_webview_panel(
        title="Disposal Event Demo", html=html_content, options=options
    )

    print(f"Created webview panel: {panel.id}")

    # Create state object to track disposal
    state = DisposalState()

    # Subscribe to disposal event
    def on_dispose():
        print("\n🔔 Disposal event detected!")
        print("The webview panel was closed (either by user or programmatically)")
        state.mark_disposed()

    unsubscribe = panel.on_did_dispose(on_dispose)
    print("✅ Disposal event handler registered")
    print("\nWaiting for panel to be disposed...")
    print("(Close the panel manually or wait 15 seconds for auto-dispose)\n")

    # Wait for disposal or timeout
    try:
        start_time = time.time()
        counter = 0
        while not state.disposal_detected and (time.time() - start_time) < 15:
            time.sleep(1)
            counter += 1
            if counter % 5 == 0:
                print(f"Still waiting... ({counter}s elapsed)")

        if not state.disposal_detected:
            print("\n⏰ Timeout reached - disposing programmatically...")
            panel.dispose()
            time.sleep(0.5)  # Give event handler time to fire

    except KeyboardInterrupt:
        print("\n\n⌨️  Keyboard interrupt - disposing panel...")
        panel.dispose()

    print("\n✅ Example complete!")
    print(f"Disposal was detected: {state.disposal_detected}")
