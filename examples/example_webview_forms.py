"""
Example: Webview with forms - Interactive data collection
"""

import signal
import sys
import threading
import time
import traceback

from vscode_sockpuppet import VSCodeClient, WebviewOptions


def debug_stack_tracer(interval=5):
    """Periodically dump stack traces of all threads for debugging."""

    def tracer():
        while True:
            time.sleep(interval)
            print("\n" + "=" * 80)
            print(f"STACK TRACE DUMP - {time.strftime('%H:%M:%S')}")
            print("=" * 80)
            for thread_id, frame in sys._current_frames().items():
                thread_name = None
                for thread in threading.enumerate():
                    if thread.ident == thread_id:
                        thread_name = thread.name
                        break
                print(f"\n--- Thread: {thread_name} (ID: {thread_id}) ---")
                traceback.print_stack(frame)
            print("=" * 80 + "\n")

    thread = threading.Thread(target=tracer, daemon=True, name="StackTracer")
    thread.start()
    return thread


class FormState:
    """Manages form submission state."""

    def __init__(self):
        self.submissions = []
        self.stop_event = threading.Event()

    def add_submission(self, data):
        """Add a form submission."""
        self.submissions.append(data)

    def stop(self):
        """Signal the main loop to stop."""
        self.stop_event.set()

    @property
    def running(self):
        """Check if still running (not stopped)."""
        return not self.stop_event.is_set()


with VSCodeClient() as client:
    print("Creating webview form demo...")

    # Create state object first
    state = FormState()

    # Set up signal handler for Ctrl-C that fires stop event
    def signal_handler(sig, frame):
        print("\n⌨️  Ctrl-C detected, shutting down...")
        state.stop()

    signal.signal(signal.SIGINT, signal_handler)

    # Start debug stack tracer
    print("Starting debug stack tracer (dumps every 5 seconds)...")
    debug_stack_tracer(interval=5)

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline';">
        <title>Form Demo</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                padding: 20px;
                background-color: var(--vscode-editor-background);
                color: var(--vscode-editor-foreground);
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
            }
            h1 {
                color: var(--vscode-textLink-foreground);
            }
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: 500;
            }
            input, select, textarea {
                width: 100%;
                padding: 8px;
                background-color: var(--vscode-input-background);
                color: var(--vscode-input-foreground);
                border: 1px solid var(--vscode-input-border);
                border-radius: 3px;
                box-sizing: border-box;
            }
            input:focus, select:focus, textarea:focus {
                outline: 1px solid var(--vscode-focusBorder);
            }
            button {
                background-color: var(--vscode-button-background);
                color: var(--vscode-button-foreground);
                border: none;
                padding: 10px 20px;
                cursor: pointer;
                border-radius: 3px;
                font-size: 14px;
                margin-top: 10px;
            }
            button:hover {
                background-color: var(--vscode-button-hoverBackground);
            }
            .success-message {
                padding: 10px;
                margin-top: 15px;
                background-color: var(--vscode-editorInfo-background);
                color: var(--vscode-editorInfo-foreground);
                border-left: 4px solid var(--vscode-editorInfo-border);
                border-radius: 3px;
                display: none;
            }
            .submission-list {
                margin-top: 30px;
                padding: 15px;
                background-color: var(--vscode-editor-selectionBackground);
                border-radius: 3px;
            }
            .submission-item {
                padding: 10px;
                margin-bottom: 10px;
                background-color: var(--vscode-editor-background);
                border-left: 3px solid var(--vscode-textLink-foreground);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📝 Interactive Form Demo</h1>
            <p>Fill out the form below. Data is sent to Python for processing.</p>

            <form id="userForm">
                <div class="form-group">
                    <label for="name">Name *</label>
                    <input type="text" id="name" required>
                </div>

                <div class="form-group">
                    <label for="email">Email *</label>
                    <input type="email" id="email" required>
                </div>

                <div class="form-group">
                    <label for="role">Role</label>
                    <select id="role">
                        <option value="">Select a role</option>
                        <option value="developer">Developer</option>
                        <option value="designer">Designer</option>
                        <option value="manager">Manager</option>
                        <option value="other">Other</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="message">Message</label>
                    <textarea id="message" rows="4"></textarea>
                </div>

                <button type="submit">Submit</button>
            </form>

            <div id="successMessage" class="success-message">
                ✓ Form submitted successfully!
            </div>

            <div class="submission-list">
                <h3>Submissions (Processed by Python)</h3>
                <div id="submissions"></div>
            </div>
        </div>

        <script>
            const vscode = acquireVsCodeApi();

            // Handle form submission
            document.getElementById('userForm').addEventListener('submit', (e) => {
                e.preventDefault();

                const formData = {
                    name: document.getElementById('name').value,
                    email: document.getElementById('email').value,
                    role: document.getElementById('role').value,
                    message: document.getElementById('message').value,
                    timestamp: new Date().toISOString()
                };

                // Send to Python
                vscode.postMessage({
                    type: 'formSubmit',
                    data: formData
                });

                // Show success message
                const successMsg = document.getElementById('successMessage');
                successMsg.style.display = 'block';
                setTimeout(() => {
                    successMsg.style.display = 'none';
                }, 3000);

                // Clear form
                e.target.reset();
            });

            // Listen for messages from Python
            window.addEventListener('message', event => {
                const message = event.data;

                if (message.type === 'updateSubmissions') {
                    const submissionsDiv = document.getElementById('submissions');
                    submissionsDiv.innerHTML = '';

                    message.submissions.forEach((submission, index) => {
                        const item = document.createElement('div');
                        item.className = 'submission-item';
                        item.innerHTML = `
                            <strong>#${index + 1} - ${submission.name}</strong><br>
                            Email: ${submission.email}<br>
                            Role: ${submission.role || 'Not specified'}<br>
                            ${submission.message ? 'Message: ' + submission.message + '<br>' : ''}
                            <small>Submitted: ${new Date(submission.timestamp).toLocaleString()}</small>
                        `;
                        submissionsDiv.appendChild(item);
                    });
                }
            });
        </script>
    </body>
    </html>
    """

    options = WebviewOptions(enable_scripts=True, retain_context_when_hidden=True)

    with client.window.create_webview_panel(
        title="Form Demo", html=html_content, options=options
    ) as panel:
        print(f"Created webview panel: {panel.id}")

        state = FormState()

        # Handle messages from webview
        def handle_message(message):
            if message.get("type") == "formSubmit":
                data = message.get("data", {})
                print("\n📩 Form submission received:")
                print(f"  Name: {data.get('name')}")
                print(f"  Email: {data.get('email')}")
                print(f"  Role: {data.get('role', 'Not specified')}")
                if data.get("message"):
                    print(f"  Message: {data.get('message')}")

                # Store submission
                state.add_submission(data)

                # Send updated submissions back to webview
                panel.post_message({"type": "updateSubmissions", "submissions": state.submissions})

                # Show notification
                client.window.show_information_message(f"Form submitted by {data.get('name')}")

        print("Adding message handler...")

        panel.on_did_receive_message(handle_message)

        print(f"Created webview panel: {panel.id}")

        # Handle disposal
        def on_dispose():
            print("\n✓ Webview closed")
            print(f"Total submissions: {len(state.submissions)}")
            state.stop()

        panel.on_did_dispose(on_dispose)

        print("Added dispose handler")

        print("\nWebview form is running!")
        print("Fill out the form to see Python receive and process the data.")
        print("Close the webview to exit or press Ctrl-C.\n")

        # Keep running until panel is closed - event-driven, no polling
        try:
            # Wait indefinitely until stop event is set
            # This responds immediately to Ctrl-C or webview disposal
            state.stop_event.wait()
        except KeyboardInterrupt:
            print("\n⌨️  Keyboard interrupt detected...")
            state.stop()

        print("\n✅ Form demo complete!")
