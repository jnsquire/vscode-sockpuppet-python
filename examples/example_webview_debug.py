"""
Example: Webview with debug logging to diagnose event issues
"""

import signal
import threading
import time

from vscode_sockpuppet import VSCodeClient, WebviewOptions


class WebviewState:
    """Manages state for the webview demo."""

    def __init__(self):
        self.counter = 0
        self.stop_event = threading.Event()
        # Event set when webview JS posts a 'ready' message
        self.ready_event = threading.Event()

    def increment(self):
        """Increment the counter."""
        self.counter += 1

    def reset(self):
        """Reset the counter to zero."""
        self.counter = 0

    def stop(self):
        """Signal the main loop to stop."""
        self.stop_event.set()

    @property
    def running(self):
        """Check if still running (not stopped)."""
        return not self.stop_event.is_set()


with VSCodeClient() as client:
    print("Creating webview panel...")

    # Create state object first
    state = WebviewState()

    # Set up signal handler for Ctrl-C that fires stop event
    def signal_handler(sig, frame):
        print("\n⌨️  Ctrl-C detected, shutting down...")
        state.stop()

    signal.signal(signal.SIGINT, signal_handler)
    # On Windows, SIGBREAK handles Ctrl-Break; register the same handler if available
    try:
        if hasattr(signal, "SIGBREAK"):
            signal.signal(signal.SIGBREAK, signal_handler)
    except Exception:
        # If the platform doesn't support SIGBREAK or setting it fails, ignore.
        pass

    # Add session listener to see all events
    def session_listener(state, payload):
        print(f"[SESSION] {state}: {payload}")

    client.add_session_listener(session_listener)

    # Create a simple webview with HTML content
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline';">
        <title>Debug Webview</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                padding: 20px;
                background-color: var(--vscode-editor-background);
                color: var(--vscode-editor-foreground);
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
            #counter {
                font-size: 48px;
                font-weight: bold;
                text-align: center;
                margin: 30px 0;
            }
            #log {
                margin-top: 20px;
                padding: 10px;
                background: var(--vscode-editor-selectionBackground);
                font-family: monospace;
                font-size: 12px;
                max-height: 300px;
                overflow-y: auto;
            }
        </style>
    </head>
    <body>
        <h1>🐛 Debug Webview</h1>
        <p>Click buttons and watch the console/log below.</p>

        <div id="counter">0</div>

        <div style="text-align: center;">
            <button onclick="sendMessage('increment')">Increment Counter</button>
            <button onclick="sendMessage('reset')">Reset Counter</button>
            <button onclick="sendMessage('hello')">Say Hello</button>
        </div>

        <div id="log"></div>

        <script>
            const logDiv = document.getElementById('log');

            function addLog(message) {
                const timestamp = new Date().toISOString().split('T')[1].split('.')[0];
                logDiv.innerHTML += `[${timestamp}] ${message}<br>`;
                logDiv.scrollTop = logDiv.scrollHeight;
            }

            addLog('Script loaded successfully');

            const vscode = acquireVsCodeApi();
            addLog('acquireVsCodeApi() called successfully');

            let counter = 0;

            function sendMessage(action) {
                addLog(`Sending message: ${action}`);
                try {
                    vscode.postMessage({ action: action });
                    addLog(`postMessage() completed for: ${action}`);
                } catch (e) {
                    addLog(`ERROR in postMessage: ${e.message}`);
                }
            }

            // Listen for messages from Python
            window.addEventListener('message', event => {
                addLog(`Received message from Python: ${JSON.stringify(event.data)}`);
                const message = event.data;

                if (message.type === 'updateCounter') {
                    counter = message.value;
                    document.getElementById('counter').textContent = counter;
                    addLog(`Counter updated to: ${counter}`);
                }

                if (message.type === 'showMessage') {
                    addLog(`Show message: ${message.text}`);
                }
            });

            addLog('Event listener registered');
            // Notify Python that the webview is ready to receive messages
            try {
                vscode.postMessage({ type: 'ready' });
                addLog('Sent ready message to Python');
            } catch (e) {
                addLog(`ERROR sending ready message: ${e.message}`);
            }
        </script>
    </body>
    </html>
    """

    # Create webview with JavaScript enabled
    options = WebviewOptions(enable_scripts=True, retain_context_when_hidden=True)

    with client.window.create_webview_panel(
        title="Debug Webview", html=html_content, options=options
    ) as panel:
        print(f"Created webview panel: {panel.id}")
        print(f"Panel visible: {panel.visible}, disposed: {panel.disposed}")

        # Create state object to manage counter and running status
        state = WebviewState()

        # Subscribe to disposal event to exit when webview is closed
        def on_dispose():
            print("\n🔔 Webview was closed!")
            state.stop()

        panel.on_did_dispose(on_dispose)
        print("Disposal handler registered")

        # Subscribe to messages from the webview using the panel method
        def handle_message(message):
            print(f"[PYTHON] Received message from webview: {message}")
            # Handshake: webview signals readiness
            if message.get("type") == "ready":
                print("[PYTHON] Webview ready")
                state.ready_event.set()
                return

            action = message.get("action")

            if action == "increment":
                state.increment()
                print(f"[PYTHON] Incrementing counter to: {state.counter}")
                panel.post_message({"type": "updateCounter", "value": state.counter})
            elif action == "reset":
                state.reset()
                print(f"[PYTHON] Resetting counter to: {state.counter}")
                panel.post_message({"type": "updateCounter", "value": state.counter})
            elif action == "hello":
                msg = f"Hello from Python! Time: {time.strftime('%H:%M:%S')}"
                print(f"[PYTHON] Sending hello: {msg}")
                panel.post_message({"type": "showMessage", "text": msg})

        # Subscribe using the panel's method
        unsubscribe = panel.on_did_receive_message(handle_message)
        print("Message handler registered")

        # Check subscriptions
        subs = client.get_subscriptions()
        print(f"Active subscriptions: {subs}")

        # Wait for webview JS to signal it's ready before sending updates
        print("Waiting for webview to signal ready (5s timeout)...")
        if not state.ready_event.wait(timeout=5.0):
            print("Warning: webview did not signal ready within timeout; messages may be lost")

        # Start a small stdin listener so pressing Enter will also stop the demo.
        # This is a helpful fallback in environments where Ctrl-C isn't delivered
        # to the process (some terminals or runners). The thread is a daemon so
        # it won't block shutdown.
        def _stdin_watch():
            try:
                # Prompt silently - users can press Enter to stop
                input()
                print("\n[STDIN] Input received, shutting down...")
                state.stop()
            except Exception:
                pass

        stdin_thread = threading.Thread(target=_stdin_watch, daemon=True)
        stdin_thread.start()

        # Update the webview periodically
        print("\nWebview is running. Try clicking the buttons!")
        print("Close the webview panel to exit, or press Ctrl+C...")

        try:
            iteration = 0
            while state.running:
                # Wait for 3 seconds OR until stop event is set
                # This is fully event-driven and responds immediately
                if state.stop_event.wait(timeout=3.0):
                    # Stop event was set
                    print("[LOOP] Stop event detected, exiting loop")
                    break

                # Timeout expired - do periodic work
                iteration += 1
                state.increment()
                print(
                    f"[LOOP] Iteration {iteration}, counter={state.counter}, running={state.running}"
                )

                # Send counter update to webview
                print(f"[PYTHON] Sending counter update: {state.counter}")
                panel.post_message({"type": "updateCounter", "value": state.counter})

        except KeyboardInterrupt:
            print("\n⌨️  Keyboard interrupt detected...")
            state.stop()
        finally:
            if not panel.disposed:
                print("\nCleaning up...")
                panel.dispose()
            print("✅ Webview example complete!")
