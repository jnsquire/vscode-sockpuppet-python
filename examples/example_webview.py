"""
Example: Creating and managing webview panels
"""

import time

from vscode_sockpuppet import VSCodeClient, WebviewOptions

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

        # Subscribe to messages from the webview using the panel method
        def handle_message(message):
            print(f"Message from webview: {message}")
            action = message.get("action")

            print(f"Received message from webview: {action}")

            if action == "increment":
                # Send counter update to webview
                panel.post_message({"type": "updateCounter", "value": int(time.time()) % 100})
            elif action == "reset":
                panel.post_message({"type": "updateCounter", "value": 0})
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
        print("Press Ctrl+C to exit...")

        try:
            counter = 0
            while True:
                time.sleep(3)
                counter += 1

                # Update the counter from Python
                panel.post_message({"type": "updateCounter", "value": counter})

                # Every 10 seconds, update the title
                if counter % 10 == 0:
                    panel.update_title(f"Python Webview Demo - Count: {counter}")

        finally:
            print("\nCleaning up...")
            panel.dispose()
            print("Webview disposed!")
