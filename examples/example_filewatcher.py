"""
File System Watcher Example

This example demonstrates file system watchers including:
- Watching for file creation, changes, and deletion
- Using glob patterns to filter files
- Selective event handling
- Proper disposal of watchers
"""

import time

from vscode_sockpuppet import VSCodeClient


def basic_watcher_example(client: VSCodeClient):
    """Basic file system watcher example."""
    print("\n=== Basic File System Watcher ===")

    # Watch all Python files in workspace
    watcher = client.workspace.create_file_system_watcher("**/*.py")

    # Define event handlers
    def on_file_created(uri: str):
        print(f"✨ Python file created: {uri}")

    def on_file_changed(uri: str):
        print(f"📝 Python file changed: {uri}")

    def on_file_deleted(uri: str):
        print(f"🗑️  Python file deleted: {uri}")

    # Register handlers (store disposers for potential cleanup)
    _dispose1 = watcher.on_did_create(on_file_created)
    _dispose2 = watcher.on_did_change(on_file_changed)
    _dispose3 = watcher.on_did_delete(on_file_deleted)

    print("Watching for Python file changes...")
    print("Try creating, editing, or deleting .py files!")
    print("Press Ctrl+C to stop\n")

    try:
        # Keep watching
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping watcher...")

    # Clean up
    watcher.dispose()
    print("Watcher disposed")


def selective_events_example(client: VSCodeClient):
    """Watch only specific events."""
    print("\n=== Selective Event Watching ===")

    # Only watch for file changes, ignore create/delete
    watcher = client.workspace.create_file_system_watcher(
        "**/*.js",
        ignore_create_events=True,  # Ignore creation
        ignore_delete_events=True,  # Ignore deletion
    )

    def on_js_file_changed(uri: str):
        print(f"JavaScript file modified: {uri}")

    watcher.on_did_change(on_js_file_changed)

    print("Watching only for changes to JavaScript files...")
    print("(Create and delete events are ignored)")

    time.sleep(10)  # Watch for 10 seconds
    watcher.dispose()
    print("Watcher disposed")


def multiple_watchers_example(client: VSCodeClient):
    """Use multiple watchers for different file types."""
    print("\n=== Multiple File Watchers ===")

    # Watch Python files
    python_watcher = client.workspace.create_file_system_watcher("**/*.py")
    python_watcher.on_did_create(
        lambda uri: print(f"🐍 New Python file: {uri}")
    )

    # Watch JavaScript/TypeScript files
    js_watcher = client.workspace.create_file_system_watcher(
        "**/*.{js,ts}"
    )
    js_watcher.on_did_create(
        lambda uri: print(f"📜 New JS/TS file: {uri}")
    )

    # Watch JSON files
    json_watcher = client.workspace.create_file_system_watcher("**/*.json")
    json_watcher.on_did_change(
        lambda uri: print(f"📋 JSON file changed: {uri}")
    )

    print("Watching multiple file types simultaneously...")
    print("- Python files (.py)")
    print("- JavaScript/TypeScript files (.js, .ts)")
    print("- JSON files (.json)\n")

    time.sleep(15)  # Watch for 15 seconds

    # Clean up all watchers
    python_watcher.dispose()
    js_watcher.dispose()
    json_watcher.dispose()
    print("\nAll watchers disposed")


def context_manager_example(client: VSCodeClient):
    """Use watcher as a context manager."""
    print("\n=== Context Manager Pattern ===")

    # Automatically disposes when exiting context
    with client.workspace.create_file_system_watcher("**/*.md") as watcher:
        watcher.on_did_create(
            lambda uri: print(f"📄 New Markdown file: {uri}")
        )
        watcher.on_did_change(
            lambda uri: print(f"✏️  Markdown file edited: {uri}")
        )

        print("Watching Markdown files...")
        print("Watcher will auto-dispose when done\n")
        time.sleep(10)

    print("Context exited - watcher automatically disposed")


def file_counter_example(client: VSCodeClient):
    """Count file operations using a watcher."""
    print("\n=== File Operation Counter ===")

    counts = {"created": 0, "changed": 0, "deleted": 0}

    watcher = client.workspace.create_file_system_watcher("**/*")

    def on_create(uri: str):
        counts["created"] += 1
        print(
            f"📊 Stats - Created: {counts['created']}, "
            f"Changed: {counts['changed']}, "
            f"Deleted: {counts['deleted']}"
        )

    def on_change(uri: str):
        counts["changed"] += 1
        print(
            f"📊 Stats - Created: {counts['created']}, "
            f"Changed: {counts['changed']}, "
            f"Deleted: {counts['deleted']}"
        )

    def on_delete(uri: str):
        counts["deleted"] += 1
        print(
            f"📊 Stats - Created: {counts['created']}, "
            f"Changed: {counts['changed']}, "
            f"Deleted: {counts['deleted']}"
        )

    watcher.on_did_create(on_create)
    watcher.on_did_change(on_change)
    watcher.on_did_delete(on_delete)

    print("Counting all file operations...")
    print("Try creating, editing, or deleting files!\n")

    time.sleep(30)  # Watch for 30 seconds

    watcher.dispose()
    print("\n=== Final Statistics ===")
    print(f"Total files created: {counts['created']}")
    print(f"Total files changed: {counts['changed']}")
    print(f"Total files deleted: {counts['deleted']}")


def main():
    """Run file watcher examples."""
    with VSCodeClient() as client:
        print("=== File System Watcher Examples ===")

        # Choose which example to run
        print("\nAvailable examples:")
        print("1. Basic watcher (watches Python files)")
        print("2. Selective events (only changes)")
        print("3. Multiple watchers (different file types)")
        print("4. Context manager (auto-disposal)")
        print("5. File operation counter (statistics)")

        choice = input("\nEnter example number (1-5) or 'all': ").strip()

        if choice == "1" or choice.lower() == "all":
            basic_watcher_example(client)

        if choice == "2" or choice.lower() == "all":
            selective_events_example(client)

        if choice == "3" or choice.lower() == "all":
            multiple_watchers_example(client)

        if choice == "4" or choice.lower() == "all":
            context_manager_example(client)

        if choice == "5" or choice.lower() == "all":
            file_counter_example(client)

        print("\n=== Examples Complete ===")


if __name__ == "__main__":
    main()
