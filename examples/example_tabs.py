"""
Tab Groups and Tab Management Example

This example demonstrates tab group operations including:
- Listing all tab groups and tabs
- Getting the active tab group
- Closing specific tabs
- Closing entire tab groups
- Subscribing to tab change events
"""

import time

from vscode_sockpuppet import VSCodeClient


def list_all_tabs(client: VSCodeClient):
    """List all tab groups and their tabs."""
    print("\n=== All Tab Groups ===")

    groups = client.window.tab_groups.get_all()
    print(f"Total tab groups: {len(groups)}\n")

    for i, group in enumerate(groups, 1):
        active_marker = " (ACTIVE)" if group.is_active else ""
        print(f"Group {i} - Column {group.view_column}{active_marker}:")
        print(f"  Tabs: {len(group.tabs)}")

        for tab in group.tabs:
            markers = []
            if tab.is_active:
                markers.append("active")
            if tab.is_dirty:
                markers.append("dirty")
            if tab.is_pinned:
                markers.append("pinned")
            if tab.is_preview:
                markers.append("preview")

            marker_str = f" [{', '.join(markers)}]" if markers else ""
            print(f"    - {tab.label}{marker_str}")

        print()


def get_active_tab_info(client: VSCodeClient):
    """Get information about the active tab group."""
    print("\n=== Active Tab Group ===")

    active_group = client.window.tab_groups.get_active_tab_group()

    if not active_group:
        print("No active tab group found")
        return

    print(f"Active group is in column {active_group.view_column}")
    print(f"Total tabs in active group: {len(active_group.tabs)}")

    if active_group.active_tab:
        print(f"Active tab: {active_group.active_tab.label}")
        print(f"  Dirty: {active_group.active_tab.is_dirty}")
        print(f"  Pinned: {active_group.active_tab.is_pinned}")
        print(f"  Preview: {active_group.active_tab.is_preview}")
    else:
        print("No active tab in the group")


def close_untitled_tabs(client: VSCodeClient):
    """Close all untitled tabs."""
    print("\n=== Closing Untitled Tabs ===")

    groups = client.window.tab_groups.get_all()
    closed_count = 0

    for group in groups:
        for tab in group.tabs:
            if "Untitled" in tab.label:
                print(f"Closing: {tab.label}")
                success = client.window.tab_groups.close_tab(tab)
                if success:
                    closed_count += 1
                    time.sleep(0.2)  # Small delay between closes

    print(f"\nClosed {closed_count} untitled tab(s)")


def close_preview_tabs(client: VSCodeClient):
    """Close all preview tabs."""
    print("\n=== Closing Preview Tabs ===")

    groups = client.window.tab_groups.get_all()
    closed_count = 0

    for group in groups:
        for tab in group.tabs:
            if tab.is_preview and not tab.is_active:
                print(f"Closing preview tab: {tab.label}")
                success = client.window.tab_groups.close_tab(tab)
                if success:
                    closed_count += 1
                    time.sleep(0.2)

    print(f"\nClosed {closed_count} preview tab(s)")


def close_inactive_groups(client: VSCodeClient):
    """Close all non-active tab groups."""
    print("\n=== Closing Inactive Tab Groups ===")

    groups = client.window.tab_groups.get_all()
    closed_count = 0

    for group in groups:
        if not group.is_active:
            print(
                f"Closing group in column {group.view_column} "
                f"({len(group.tabs)} tabs)"
            )
            success = client.window.tab_groups.close_group(group)
            if success:
                closed_count += 1
                time.sleep(0.3)

    print(f"\nClosed {closed_count} tab group(s)")


def watch_tab_changes(client: VSCodeClient):
    """Watch for tab and tab group changes."""
    print("\n=== Watching Tab Changes ===")
    print("Make changes to your tabs (open, close, switch)")
    print("Press Ctrl+C to stop\n")

    def on_tabs_changed(data):
        print(f"📝 Tabs changed - {data}")
        active = client.window.tab_groups.get_active_tab_group()
        if active and active.active_tab:
            print(f"   Active tab is now: {active.active_tab.label}")

    def on_groups_changed(data):
        print(f"🗂️  Tab groups changed - {data}")
        groups = client.window.tab_groups.get_all()
        print(f"   Total groups: {len(groups)}")

    # Subscribe to events
    dispose1 = client.window.tab_groups.on_did_change_tabs(on_tabs_changed)
    dispose2 = client.window.tab_groups.on_did_change_tab_groups(
        on_groups_changed
    )

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping watchers...")

    # Clean up
    dispose1()
    dispose2()
    print("Watchers disposed")


def find_tabs_by_name(client: VSCodeClient, search_term: str):
    """Find tabs containing a specific string in their label."""
    print(f"\n=== Finding Tabs Matching '{search_term}' ===")

    groups = client.window.tab_groups.get_all()
    found_tabs = []

    for group in groups:
        for tab in group.tabs:
            if search_term.lower() in tab.label.lower():
                found_tabs.append((group, tab))

    if not found_tabs:
        print(f"No tabs found matching '{search_term}'")
        return

    print(f"Found {len(found_tabs)} matching tab(s):\n")
    for group, tab in found_tabs:
        print(
            f"  - {tab.label} (Group column {group.view_column})"
        )


def count_file_types(client: VSCodeClient):
    """Count tabs by file extension."""
    print("\n=== Tab Count by File Type ===")

    groups = client.window.tab_groups.get_all()
    extensions = {}

    for group in groups:
        for tab in group.tabs:
            # Extract extension from label
            if "." in tab.label:
                ext = tab.label.rsplit(".", 1)[-1]
                extensions[ext] = extensions.get(ext, 0) + 1
            else:
                extensions["(no extension)"] = (
                    extensions.get("(no extension)", 0) + 1
                )

    print("File type distribution:")
    for ext, count in sorted(
        extensions.items(), key=lambda x: x[1], reverse=True
    ):
        print(f"  .{ext}: {count} tab(s)")

    total_tabs = sum(extensions.values())
    print(f"\nTotal tabs: {total_tabs}")


def main():
    """Run tab management examples."""
    with VSCodeClient() as client:
        print("=== Tab Groups Management Examples ===")

        while True:
            print("\n" + "=" * 50)
            print("Available operations:")
            print("1. List all tabs")
            print("2. Show active tab info")
            print("3. Close untitled tabs")
            print("4. Close preview tabs")
            print("5. Close inactive groups")
            print("6. Watch tab changes")
            print("7. Find tabs by name")
            print("8. Count file types")
            print("9. Exit")
            print("=" * 50)

            choice = input("\nEnter choice (1-9): ").strip()

            if choice == "1":
                list_all_tabs(client)
            elif choice == "2":
                get_active_tab_info(client)
            elif choice == "3":
                close_untitled_tabs(client)
            elif choice == "4":
                close_preview_tabs(client)
            elif choice == "5":
                close_inactive_groups(client)
            elif choice == "6":
                watch_tab_changes(client)
            elif choice == "7":
                search = input("Enter search term: ").strip()
                find_tabs_by_name(client, search)
            elif choice == "8":
                count_file_types(client)
            elif choice == "9":
                print("\nExiting...")
                break
            else:
                print("Invalid choice, please try again")


if __name__ == "__main__":
    main()
