"""
Example demonstrating VS Code-style event subscriptions.

This example shows the new event emitter API that mirrors VS Code's
TypeScript API style with on_did_* properties.
"""

from vscode_sockpuppet import VSCodeClient


def main():
    """Demonstrate VS Code-style event subscriptions."""
    print("VS Code-Style Event Subscriptions Example")
    print("=" * 50)
    print()
    print("This example demonstrates the VS Code-style event API.")
    print("Events are now subscribed via properties on window/workspace.")
    print()

    with VSCodeClient() as client:
        # Store disposables to clean up later
        disposables = []

        print("Setting up event listeners...\n")

        # Window events - VS Code style!
        dispose1 = client.window.on_did_change_active_text_editor(
            lambda editor: print(
                f"📝 Active editor changed: {editor['fileName'] if editor else 'None'}"
            )
        )
        disposables.append(dispose1)

        dispose2 = client.window.on_did_change_text_editor_selection(
            lambda data: print(
                f"✂️  Selection changed: Line {data['selections'][0]['start']['line']}"
            )
        )
        disposables.append(dispose2)

        dispose3 = client.window.on_did_open_terminal(
            lambda terminal: print(f"🖥️  Terminal opened: {terminal['name']}")
        )
        disposables.append(dispose3)

        # Workspace events - VS Code style!
        dispose4 = client.workspace.on_did_save_text_document(
            lambda doc: print(f"💾 Document saved: {doc['fileName']}")
        )
        disposables.append(dispose4)

        dispose5 = client.workspace.on_did_open_text_document(
            lambda doc: print(f"📂 Document opened: {doc['fileName']}")
        )
        disposables.append(dispose5)

        dispose6 = client.workspace.on_did_close_text_document(
            lambda doc: print(f"❌ Document closed: {doc['fileName']}")
        )
        disposables.append(dispose6)

        def on_document_change(event):
            """Handle document changes with detailed information."""
            print(f"✏️  Document changed: {event['uri']}")
            for i, change in enumerate(event["contentChanges"], 1):
                text = change["text"]
                if len(text) > 50:
                    text = text[:50] + "..."
                print(f"   Change {i}: {repr(text)}")

        dispose7 = client.workspace.on_did_change_text_document(on_document_change)
        disposables.append(dispose7)

        dispose8 = client.workspace.on_did_change_configuration(
            lambda event: print("⚙️  Configuration changed")
        )
        disposables.append(dispose8)

        print("✅ Event listeners registered!\n")
        print("Try the following in VS Code:")
        print("  - Open/close files")
        print("  - Save files")
        print("  - Change text in the active editor")
        print("  - Switch between editor tabs")
        print("  - Open/close terminals")
        print("  - Change VS Code settings")
        print()
        print("Press Ctrl+C to stop...\n")

        try:
            # Keep the script running to receive events
            import time

            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nCleaning up...")

            # Dispose of all event subscriptions
            for dispose in disposables:
                dispose()

            print("✅ All event subscriptions disposed")
            print("Goodbye!")


if __name__ == "__main__":
    main()
