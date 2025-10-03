"""
Example: Event Monitoring

Demonstrates all VS Code event subscriptions:
- Window events (editor, terminal, view changes)
- Workspace events (document lifecycle, file operations)
- Real-time monitoring and logging
"""

import time

from vscode_sockpuppet import VSCodeClient


def example_window_events():
    """Monitor all window-related events."""
    print("=" * 60)
    print("Example 1: Window Events")
    print("=" * 60)

    with VSCodeClient() as client:
        print("\n📢 Subscribing to window events...")
        print("   Try: Switching editors, scrolling, changing focus\n")

        # Active editor changes
        def on_active_editor(data):
            if data:
                print(f"✏️  Active editor: {data['fileName']}")
            else:
                print("✏️  No active editor")

        dispose1 = client.window.on_did_change_active_text_editor(on_active_editor)

        # Editor selection changes
        def on_selection(data):
            sel = data["selections"][0]
            start = sel["start"]
            print(f"📍 Selection: Line {start['line'] + 1}, Col {start['character'] + 1}")

        dispose2 = client.window.on_did_change_text_editor_selection(on_selection)

        # Visible ranges (scrolling)
        def on_visible_ranges(data):
            ranges = data["visibleRanges"]
            if ranges:
                start_line = ranges[0]["start"]["line"]
                end_line = ranges[-1]["end"]["line"]
                print(f"👁️  Visible: Lines {start_line + 1}-{end_line + 1}")

        dispose3 = client.window.on_did_change_text_editor_visible_ranges(on_visible_ranges)

        # Editor options changes
        def on_options(data):
            opts = data["options"]
            print(f"⚙️  Options: Tab size={opts['tabSize']}, Insert spaces={opts['insertSpaces']}")

        dispose4 = client.window.on_did_change_text_editor_options(on_options)

        # View column changes
        def on_view_column(data):
            print(f"🔀 Editor moved to column {data['viewColumn']}")

        dispose5 = client.window.on_did_change_text_editor_view_column(on_view_column)

        # Window focus changes
        def on_window_state(data):
            state = "focused" if data["focused"] else "blurred"
            print(f"🪟 Window {state}")

        dispose6 = client.window.on_did_change_window_state(on_window_state)

        # Monitor for 10 seconds
        print("⏱️  Monitoring for 10 seconds...")
        time.sleep(10)

        # Clean up
        dispose1()
        dispose2()
        dispose3()
        dispose4()
        dispose5()
        dispose6()
        print("\n✅ Unsubscribed from all window events")


def example_terminal_events():
    """Monitor terminal-related events."""
    print("\n" + "=" * 60)
    print("Example 2: Terminal Events")
    print("=" * 60)

    with VSCodeClient() as client:
        print("\n📢 Subscribing to terminal events...")
        print("   Try: Creating/closing terminals, using them\n")

        # Terminal opened
        def on_open(data):
            print(f"📂 Terminal opened: {data['name']}")

        dispose1 = client.window.on_did_open_terminal(on_open)

        # Terminal closed
        def on_close(data):
            print(f"📪 Terminal closed: {data['name']}")

        dispose2 = client.window.on_did_close_terminal(on_close)

        # Terminal state changed
        def on_state(data):
            interacted = "✓" if data["isInteractedWith"] else "✗"
            print(f"🔄 Terminal {data['name']}: Interacted {interacted}")

        dispose3 = client.window.on_did_change_terminal_state(on_state)

        # Create a test terminal to trigger events
        print("Creating test terminal...")
        terminal = client.window.create_terminal("Event Test Terminal")
        time.sleep(1)

        terminal.send_text("echo 'Hello from event test'")
        time.sleep(2)

        terminal.dispose()
        time.sleep(1)

        # Clean up
        dispose1()
        dispose2()
        dispose3()
        print("\n✅ Unsubscribed from all terminal events")


def example_document_events():
    """Monitor document lifecycle events."""
    print("\n" + "=" * 60)
    print("Example 3: Document Events")
    print("=" * 60)

    with VSCodeClient() as client:
        print("\n📢 Subscribing to document events...")
        print("   Try: Opening/closing/saving files\n")

        # Document opened
        def on_open(data):
            print(f"📄 Opened: {data['fileName']}")

        dispose1 = client.workspace.on_did_open_text_document(on_open)

        # Document closed
        def on_close(data):
            print(f"🗑️  Closed: {data['fileName']}")

        dispose2 = client.workspace.on_did_close_text_document(on_close)

        # Document saved
        def on_save(data):
            print(f"💾 Saved: {data['fileName']}")

        dispose3 = client.workspace.on_did_save_text_document(on_save)

        # Document changed
        change_count = {"count": 0}

        def on_change(data):
            change_count["count"] += 1
            uri = data["document"]["uri"]
            print(f"✏️  Changed #{change_count['count']}: {uri}")

        dispose4 = client.workspace.on_did_change_text_document(on_change)

        # Monitor for 10 seconds
        print("⏱️  Monitoring for 10 seconds...")
        time.sleep(10)

        # Clean up
        dispose1()
        dispose2()
        dispose3()
        dispose4()
        print(f"\n✅ Detected {change_count['count']} document changes")


def example_file_system_events():
    """Monitor file system operation events."""
    print("\n" + "=" * 60)
    print("Example 4: File System Events")
    print("=" * 60)

    with VSCodeClient() as client:
        print("\n📢 Subscribing to file system events...")
        print("   Try: Creating/deleting/renaming files in workspace\n")

        # Files created
        def on_create(data):
            for file in data["files"]:
                print(f"➕ Created: {file['uri']}")

        dispose1 = client.workspace.on_did_create_files(on_create)

        # Files deleted
        def on_delete(data):
            for file in data["files"]:
                print(f"➖ Deleted: {file['uri']}")

        dispose2 = client.workspace.on_did_delete_files(on_delete)

        # Files renamed/moved
        def on_rename(data):
            for file in data["files"]:
                old = file["oldUri"].split("/")[-1]
                new = file["newUri"].split("/")[-1]
                print(f"📝 Renamed: {old} → {new}")

        dispose3 = client.workspace.on_did_rename_files(on_rename)

        # Monitor for 15 seconds
        print("⏱️  Monitoring for 15 seconds...")
        time.sleep(15)

        # Clean up
        dispose1()
        dispose2()
        dispose3()
        print("\n✅ Unsubscribed from all file system events")


def example_comprehensive_monitoring():
    """Monitor all events simultaneously."""
    print("\n" + "=" * 60)
    print("Example 5: Comprehensive Event Monitoring")
    print("=" * 60)

    with VSCodeClient() as client:
        print("\n📢 Subscribing to ALL events...")
        print("   Monitoring workspace activity\n")

        event_counts = {
            "editor_changes": 0,
            "selections": 0,
            "scrolls": 0,
            "terminal_ops": 0,
            "file_ops": 0,
            "doc_changes": 0,
        }

        # Window events
        disposables = []

        def count_event(category):
            def handler(data):
                event_counts[category] += 1

            return handler

        disposables.append(
            client.window.on_did_change_active_text_editor(count_event("editor_changes"))
        )
        disposables.append(
            client.window.on_did_change_text_editor_selection(count_event("selections"))
        )
        disposables.append(
            client.window.on_did_change_text_editor_visible_ranges(count_event("scrolls"))
        )
        disposables.append(client.window.on_did_open_terminal(count_event("terminal_ops")))
        disposables.append(client.window.on_did_close_terminal(count_event("terminal_ops")))

        # Workspace events
        disposables.append(client.workspace.on_did_open_text_document(count_event("file_ops")))
        disposables.append(client.workspace.on_did_close_text_document(count_event("file_ops")))
        disposables.append(
            client.workspace.on_did_change_text_document(count_event("doc_changes"))
        )
        disposables.append(client.workspace.on_did_create_files(count_event("file_ops")))
        disposables.append(client.workspace.on_did_delete_files(count_event("file_ops")))
        disposables.append(client.workspace.on_did_rename_files(count_event("file_ops")))

        # Monitor for 15 seconds
        print("⏱️  Monitoring for 15 seconds...")
        print("   Use VS Code normally to generate events\n")
        time.sleep(15)

        # Report statistics
        print("\n📊 Event Statistics:")
        print(f"   Editor Changes: {event_counts['editor_changes']}")
        print(f"   Text Selections: {event_counts['selections']}")
        print(f"   Scroll Events: {event_counts['scrolls']}")
        print(f"   Terminal Operations: {event_counts['terminal_ops']}")
        print(f"   File Operations: {event_counts['file_ops']}")
        print(f"   Document Changes: {event_counts['doc_changes']}")

        total = sum(event_counts.values())
        print(f"\n   Total Events: {total}")

        # Clean up
        for dispose in disposables:
            dispose()
        print("\n✅ Unsubscribed from all events")


def main():
    """Run all event monitoring examples."""
    print("\n" + "=" * 60)
    print("VS Code Event Monitoring Examples")
    print("=" * 60)

    try:
        # Run examples
        example_window_events()
        example_terminal_events()
        example_document_events()
        example_file_system_events()
        example_comprehensive_monitoring()

        print("\n" + "=" * 60)
        print("✅ All event monitoring examples completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
