"""
Example: Webview visibility and active state tracking
"""

from vscode_sockpuppet import VSCodeClient, WebviewOptions


class ViewState:
    """Tracks webview visibility state."""

    def __init__(self):
        self.running = True
        self.is_visible = True
        self.is_active = False


with VSCodeClient() as client:
    print("Creating webview with view state tracking...")

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>View State Demo</title>
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
            .info-box {
                padding: 15px;
                margin: 15px 0;
                border-left: 4px solid var(--vscode-textLink-foreground);
                background-color: var(--vscode-editor-selectionBackground);
            }
            .status {
                display: inline-block;
                padding: 5px 10px;
                border-radius: 3px;
                margin: 5px 5px 5px 0;
                font-size: 14px;
            }
            .status.active {
                background-color: #4caf50;
                color: white;
            }
            .status.inactive {
                background-color: #757575;
                color: white;
            }
        </style>
    </head>
    <body>
        <h1>👁️ View State Tracking Demo</h1>

        <div class="info-box">
            <p><strong>Try these actions to see view state changes:</strong></p>
            <ul>
                <li>Switch to another tab, then back (visibility changes)</li>
                <li>Click on this panel vs another panel (active state changes)</li>
                <li>Split the editor and move panels around</li>
            </ul>
        </div>

        <p>Python is tracking when this panel becomes visible/hidden or active/inactive.</p>
        <p>Check the terminal to see events being logged!</p>
    </body>
    </html>
    """

    options = WebviewOptions(enable_scripts=True, retain_context_when_hidden=True)

    with client.window.create_webview_panel(
        title="View State Demo", html=html_content, options=options
    ) as panel:
        print(f"Created webview panel: {panel.id}\n")

        state = ViewState()

        # Handle disposal
        def on_dispose():
            print("\n✓ Webview closed")
            state.running = False

        panel.on_did_dispose(on_dispose)

        # Handle view state changes
        def on_view_state_change(view_state):
            visible = view_state["visible"]
            active = view_state["active"]

            # Track state changes
            visibility_changed = visible != state.is_visible
            active_changed = active != state.is_active

            state.is_visible = visible
            state.is_active = active

            # Log changes
            if visibility_changed or active_changed:
                print("\n🔔 View State Changed:")
                if visibility_changed:
                    status = "VISIBLE" if visible else "HIDDEN"
                    print(f"   Visibility: {status}")
                if active_changed:
                    status = "ACTIVE" if active else "INACTIVE"
                    print(f"   Active: {status}")

        panel.on_did_change_view_state(on_view_state_change)

        print("✅ View state tracking active!")
        print("\n📋 Instructions:")
        print("  • Switch tabs to see visibility changes")
        print("  • Click different panels to see active state changes")
        print("  • Close the webview to exit\n")

        # Keep running until panel is closed
        while state.running:
            import time

            time.sleep(0.5)

        print("\n✅ View state demo complete!")
