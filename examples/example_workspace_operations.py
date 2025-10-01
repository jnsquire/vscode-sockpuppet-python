"""
Workspace Operations Example

Demonstrates VS Code workspace operations for finding files, getting workspace
folder information, and working with relative paths.
"""

import time

from vscode_sockpuppet import VSCodeClient


def example_find_files(client: VSCodeClient):
    """Example 1: Finding files with glob patterns."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Finding Files")
    print("=" * 70)

    # Find all Python files
    print("\n1. Finding all Python files:")
    python_files = client.workspace.find_files("**/*.py")
    print(f"   Found {len(python_files)} Python files")
    for uri in python_files[:5]:  # Show first 5
        print(f"   - {uri}")
    if len(python_files) > 5:
        print(f"   ... and {len(python_files) - 5} more")

    # Find specific file type with exclusions
    print("\n2. Finding Markdown files, excluding node_modules:")
    md_files = client.workspace.find_files(
        "**/*.md", "**/node_modules/**"
    )
    print(f"   Found {len(md_files)} Markdown files")
    for uri in md_files[:3]:
        print(f"   - {uri}")

    # Find with multiple extensions
    print("\n3. Finding TypeScript/JavaScript files:")
    ts_js_files = client.workspace.find_files("**/*.{ts,js}")
    print(f"   Found {len(ts_js_files)} TS/JS files")
    for uri in ts_js_files[:3]:
        print(f"   - {uri}")

    # Limit results
    print("\n4. Finding files with result limit:")
    limited_files = client.workspace.find_files("**/*", max_results=5)
    print(f"   Found (up to 5): {len(limited_files)} files")
    for uri in limited_files:
        print(f"   - {uri}")


def example_workspace_folder(client: VSCodeClient):
    """Example 2: Getting workspace folder information."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Workspace Folder Information")
    print("=" * 70)

    # Get workspace folders
    folders = client.workspace.get_workspace_folders()
    if not folders:
        print("\n   No workspace folders open")
        return

    print(f"\n   Workspace has {len(folders)} folder(s)")

    # Find some files and check their workspace folders
    files = client.workspace.find_files("**/*.py", max_results=3)

    print("\n   Checking workspace folder for each file:")
    for uri in files:
        folder = client.workspace.get_workspace_folder(uri)
        if folder:
            print(f"\n   File: {uri}")
            print(f"   Folder: {folder['name']}")
            print(f"   Folder URI: {folder['uri']}")
            print(f"   Folder Index: {folder['index']}")
        else:
            print(f"\n   File: {uri}")
            print("   Not in any workspace folder")


def example_relative_paths(client: VSCodeClient):
    """Example 3: Converting paths to workspace-relative."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Relative Path Conversion")
    print("=" * 70)

    # Get some files
    files = client.workspace.find_files("**/*.py", max_results=5)
    if not files:
        print("\n   No Python files found")
        return

    print("\n1. Convert absolute paths to relative:")
    for uri in files[:3]:
        rel_path = client.workspace.as_relative_path(uri)
        print(f"\n   Original: {uri}")
        print(f"   Relative: {rel_path}")

    print("\n2. With workspace folder name (multi-folder workspaces):")
    for uri in files[:2]:
        rel_path = client.workspace.as_relative_path(
            uri, include_workspace_folder=True
        )
        print(f"\n   Original: {uri}")
        print(f"   Relative: {rel_path}")


def example_combined_workflow(client: VSCodeClient):
    """Example 4: Combined workflow using all operations."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Combined Workflow")
    print("=" * 70)
    print("\nScenario: Find all test files and organize by workspace folder")

    # Step 1: Find all test files
    print("\n1. Finding test files...")
    test_files = client.workspace.find_files("**/*test*.py")
    print(f"   Found {len(test_files)} test files")

    # Step 2: Group by workspace folder
    print("\n2. Organizing by workspace folder...")
    by_folder = {}

    for uri in test_files:
        folder = client.workspace.get_workspace_folder(uri)
        if folder:
            folder_name = folder["name"]
            if folder_name not in by_folder:
                by_folder[folder_name] = []
            by_folder[folder_name].append(uri)
        else:
            if "No Folder" not in by_folder:
                by_folder["No Folder"] = []
            by_folder["No Folder"].append(uri)

    # Step 3: Display organized results with relative paths
    print("\n3. Test files by workspace folder:")
    for folder_name, files in by_folder.items():
        print(f"\n   {folder_name} ({len(files)} files):")
        for uri in files[:3]:  # Show first 3
            rel_path = client.workspace.as_relative_path(uri)
            print(f"      - {rel_path}")
        if len(files) > 3:
            print(f"      ... and {len(files) - 3} more")


def example_file_search_patterns(client: VSCodeClient):
    """Example 5: Advanced file search patterns."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Advanced Search Patterns")
    print("=" * 70)

    patterns = [
        ("**/*.json", "JSON files"),
        ("**/src/**/*.ts", "TypeScript files in src"),
        ("**/{test,tests}/**/*.py", "Python test files"),
        ("**/package.json", "Package.json files"),
        ("**/*.{yml,yaml}", "YAML files"),
    ]

    for pattern, description in patterns:
        files = client.workspace.find_files(pattern, max_results=10)
        print(f"\n{description} ({pattern}):")
        print(f"   Found {len(files)} files")
        if files:
            for uri in files[:2]:  # Show first 2
                rel_path = client.workspace.as_relative_path(uri)
                print(f"   - {rel_path}")
            if len(files) > 2:
                print(f"   ... and {len(files) - 2} more")


def example_workspace_statistics(client: VSCodeClient):
    """Example 6: Gather workspace statistics."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Workspace Statistics")
    print("=" * 70)

    file_types = {
        "Python": "**/*.py",
        "TypeScript": "**/*.ts",
        "JavaScript": "**/*.js",
        "JSON": "**/*.json",
        "Markdown": "**/*.md",
        "YAML": "**/*.{yml,yaml}",
    }

    print("\nGathering workspace statistics...")
    stats = {}

    for name, pattern in file_types.items():
        files = client.workspace.find_files(pattern)
        stats[name] = len(files)

    # Display statistics
    print("\n   File Type Distribution:")
    total = sum(stats.values())
    for name, count in sorted(
        stats.items(), key=lambda x: x[1], reverse=True
    ):
        if count > 0:
            percentage = (count / total * 100) if total > 0 else 0
            print(f"   {name:15} {count:5} files ({percentage:5.1f}%)")

    print(f"\n   Total Files: {total}")


def main():
    """Run all workspace operations examples."""
    print("Workspace Operations Examples")
    print("=" * 70)
    print("Demonstrates finding files, workspace folders, and relative paths")

    client = VSCodeClient()
    client.connect()

    try:
        # Check if workspace is open
        folders = client.workspace.get_workspace_folders()
        if not folders:
            print("\n❌ No workspace folder open")
            print("   Please open a folder in VS Code first")
            return

        print("\n✓ Connected to VS Code")
        print(f"✓ Workspace: {folders[0]['name']}")
        if len(folders) > 1:
            print(f"✓ Multi-folder workspace ({len(folders)} folders)")

        # Run examples with pauses
        example_find_files(client)
        time.sleep(1)

        example_workspace_folder(client)
        time.sleep(1)

        example_relative_paths(client)
        time.sleep(1)

        example_combined_workflow(client)
        time.sleep(1)

        example_file_search_patterns(client)
        time.sleep(1)

        example_workspace_statistics(client)

        print("\n" + "=" * 70)
        print("Examples completed!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
