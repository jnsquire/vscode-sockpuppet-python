"""
Example: Creating and managing webview panels
"""

import time

from vscode_sockpuppet import VSCodeClient, WebviewOptions


class WebviewState:
    """Manages state for the webview demo."""

    def __init__(self):
        self.counter = 0
        self.running = True

    def increment(self):
        """Increment the counter."""
        self.counter += 1

    def reset(self):
        """Reset the counter to zero."""
        self.counter = 0

    def stop(self):
        """Stop the main loop."""
        self.running = False


with VSCodeClient() as client:
    print("Creating webview panel...")

    # Create a simple webview with HTML content
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Python Webview</title>
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
            .container {
                max-width: 800px;
                margin: 0 auto;
            }
            button {
                background-color: var(--vscode-button-background);
                color: var(--vscode-button-foreground);
                border: none;
                padding: 10px 20px;
                margin: 10px 5px;
                cursor: pointer;
                border-radius: 3px;
                font-size: 14px;
            }
            button:hover {
                background-color: var(--vscode-button-hoverBackground);
            }
            .message {
                padding: 15px;
                margin: 15px 0;
                border-left: 4px solid var(--vscode-textLink-foreground);
                background-color: var(--vscode-editor-selectionBackground);
            }
            #counter {
                font-size: 48px;
                font-weight: bold;
                text-align: center;
                margin: 30px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🐍 Python-Controlled Webview</h1>
            <p>This webview is being controlled by a Python script!</p>

            <div class="message">
                <strong>Tip:</strong> This panel uses VS Code's theming variables,
                so it will automatically match your color theme.
            </div>

            <div id="counter">0</div>

            <div style="text-align: center;">
                <button onclick="sendMessage('increment')">Increment Counter</button>
                <button onclick="sendMessage('reset')">Reset Counter</button>
                <button onclick="sendMessage('hello')">Say Hello</button>
            </div>

            <div id="messages" style="margin-top: 30px;"></div>
        </div>

        <script>
            const vscode = acquireVsCodeApi();
            let counter = 0;

            function sendMessage(action) {
                vscode.postMessage({ action: action });
            }

            // Listen for messages from Python
            window.addEventListener('message', event => {
                const message = event.data;

                if (message.type === 'updateCounter') {
                    counter = message.value;
                    document.getElementById('counter').textContent = counter;
                }

                if (message.type === 'showMessage') {
                    const messagesDiv = document.getElementById('messages');
                    const msgElement = document.createElement('div');
                    msgElement.className = 'message';
                    msgElement.textContent = message.text;
                    messagesDiv.insertBefore(msgElement, messagesDiv.firstChild);
                }
            });
        </script>
    </body>
    </html>
    """

    # Create webview with JavaScript enabled
    options = WebviewOptions(enable_scripts=True, retain_context_when_hidden=True)

    with client.window.create_webview_panel(
        title="Python Webview Demo", html=html_content, options=options
    ) as panel:
        print(f"Created webview panel: {panel.id}")

        # Create state object to manage counter and running status
        state = WebviewState()

        # Subscribe to disposal event to exit when webview is closed
        def on_dispose():
            print("\n🔔 Webview was closed!")
            state.stop()

        panel.on_did_dispose(on_dispose)

        # Subscribe to messages from the webview using the panel method
        def handle_message(message):
            print(f"Message from webview: {message}")
            action = message.get("action")

            print(f"Received message from webview: {action}")

            if action == "increment":
                # Increment the Python counter
                state.increment()
                panel.post_message({"type": "updateCounter", "value": state.counter})
            elif action == "reset":
                # Reset the Python counter
                state.reset()
                panel.post_message({"type": "updateCounter", "value": state.counter})
            elif action == "hello":
                panel.post_message(
                    {
                        "type": "showMessage",
                        "text": f"Hello from Python! Time: {time.strftime('%H:%M:%S')}",
                    }
                )

        # Subscribe using the panel's method
        unsubscribe = panel.on_did_receive_message(handle_message)

        # Update the webview periodically
        print("Webview is running. Try clicking the buttons!")
        print("Close the webview panel to exit, or press Ctrl+C...")

        try:
            while state.running:
                time.sleep(3)
                state.increment()

                # Update the counter from Python
                if state.running:  # Check if still running before sending
                    panel.post_message({"type": "updateCounter", "value": state.counter})

                # Every 10 seconds, update the title
                if state.counter % 10 == 0 and state.running:
                    panel.update_title(f"Python Webview Demo - Count: {state.counter}")

        except KeyboardInterrupt:
            print("\n⌨️  Keyboard interrupt detected...")
        finally:
            if not panel.disposed:
                print("\nCleaning up...")
                panel.dispose()
            print("✅ Webview example complete!")
