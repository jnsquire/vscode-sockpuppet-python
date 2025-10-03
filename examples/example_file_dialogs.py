"""
File Dialog Examples

Demonstrates using showOpenDialog and showSaveDialog for file selection.
"""

import time

from vscode_sockpuppet import VSCodeClient


def example_open_single_file(client: VSCodeClient):
    """Example 1: Select a single file."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Open Single File")
    print("=" * 70)

    print("\n   Opening file dialog...")

    uris = client.window.show_open_dialog(
        {
            "canSelectFiles": True,
            "canSelectFolders": False,
            "canSelectMany": False,
            "title": "Select a file to open",
        }
    )

    if uris:
        print(f"\n   Selected file: {uris[0]}")

        # Read the file content
        try:
            content = client.fs.read_text(uris[0])
            lines = content.split("\n")
            print(f"   File has {len(lines)} lines")
            print("   First 3 lines:")
            for line in lines[:3]:
                print(f"      {line}")
        except Exception as e:
            print(f"   Could not read file: {e}")
    else:
        print("\n   Dialog canceled")


def example_open_multiple_files(client: VSCodeClient):
    """Example 2: Select multiple files."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Open Multiple Files")
    print("=" * 70)

    print("\n   Opening file dialog (select multiple)...")

    uris = client.window.show_open_dialog(
        {
            "canSelectFiles": True,
            "canSelectFolders": False,
            "canSelectMany": True,
            "title": "Select one or more files",
        }
    )

    if uris:
        print(f"\n   Selected {len(uris)} file(s):")
        for uri in uris:
            # Get file stats
            try:
                stat = client.fs.stat(uri)
                size_kb = stat.size / 1024
                print(f"      - {uri} ({size_kb:.1f} KB)")
            except Exception as e:
                print(f"      - {uri} (error: {e})")
    else:
        print("\n   Dialog canceled")


def example_open_with_filters(client: VSCodeClient):
    """Example 3: Open file with type filters."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Open File with Filters")
    print("=" * 70)

    print("\n   Opening file dialog with Python filter...")

    uris = client.window.show_open_dialog(
        {
            "canSelectFiles": True,
            "canSelectFolders": False,
            "canSelectMany": False,
            "filters": {
                "Python Files": ["py", "pyi"],
                "Text Files": ["txt", "md"],
                "All Files": ["*"],
            },
            "title": "Select a Python or text file",
        }
    )

    if uris:
        uri = uris[0]
        print(f"\n   Selected: {uri}")

        # Check if it's a Python file
        if uri.endswith(".py"):
            print("   ✓ Python file detected")

            # Count lines and imports
            try:
                content = client.fs.read_text(uri)
                lines = content.split("\n")
                imports = [line for line in lines if line.strip().startswith(("import ", "from "))]
                print(f"   Lines: {len(lines)}")
                print(f"   Imports: {len(imports)}")
            except Exception as e:
                print(f"   Error reading: {e}")
    else:
        print("\n   Dialog canceled")


def example_select_folder(client: VSCodeClient):
    """Example 4: Select a folder."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Select Folder")
    print("=" * 70)

    print("\n   Opening folder dialog...")

    uris = client.window.show_open_dialog(
        {
            "canSelectFiles": False,
            "canSelectFolders": True,
            "canSelectMany": False,
            "title": "Select a folder",
        }
    )

    if uris:
        folder_uri = uris[0]
        print(f"\n   Selected folder: {folder_uri}")

        # List contents
        try:
            entries = client.fs.read_directory(folder_uri)
            print(f"\n   Folder contains {len(entries)} items:")

            # Separate files and folders
            files = [name for name, file_type in entries if file_type == 1]  # FileType.File = 1
            folders = [
                name for name, file_type in entries if file_type == 2
            ]  # FileType.Directory = 2

            if folders:
                print(f"\n   Folders ({len(folders)}):")
                for name in folders[:5]:  # Show first 5
                    print(f"      📁 {name}")
                if len(folders) > 5:
                    print(f"      ... and {len(folders) - 5} more")

            if files:
                print(f"\n   Files ({len(files)}):")
                for name in files[:5]:  # Show first 5
                    print(f"      📄 {name}")
                if len(files) > 5:
                    print(f"      ... and {len(files) - 5} more")

        except Exception as e:
            print(f"   Error reading folder: {e}")
    else:
        print("\n   Dialog canceled")


def example_save_dialog(client: VSCodeClient):
    """Example 5: Save file dialog."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Save File Dialog")
    print("=" * 70)

    print("\n   Opening save dialog...")

    uri = client.window.show_save_dialog(
        {
            "filters": {
                "Python Files": ["py"],
                "Text Files": ["txt"],
                "All Files": ["*"],
            },
            "title": "Save Python file",
            "saveLabel": "Save",
        }
    )

    if uri:
        print(f"\n   Save location: {uri}")

        # Create sample content
        content = f"""'''
Sample Python file created by VSCode Sockpuppet
Created at: {time.strftime("%Y-%m-%d %H:%M:%S")}
'''

def hello():
    print("Hello from saved file!")

if __name__ == "__main__":
    hello()
"""

        try:
            client.fs.write_text(uri, content)
            print("   ✓ File saved successfully!")

            # Verify by reading back
            saved_content = client.fs.read_text(uri)
            print(f"   ✓ Verified: {len(saved_content)} bytes written")

        except Exception as e:
            print(f"   ✗ Error saving file: {e}")
    else:
        print("\n   Dialog canceled")


def example_save_with_default_location(client: VSCodeClient):
    """Example 6: Save dialog with default location."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Save with Default Location")
    print("=" * 70)

    # Get workspace folder for default location
    folders = client.workspace.get_workspace_folders()
    if not folders:
        print("\n   No workspace folder open")
        return

    workspace_uri = folders[0]["uri"]
    default_uri = f"{workspace_uri}/output.txt"

    print(f"\n   Default location: {default_uri}")
    print("   Opening save dialog...")

    uri = client.window.show_save_dialog(
        {
            "defaultUri": default_uri,
            "filters": {"Text Files": ["txt"], "All Files": ["*"]},
            "title": "Save output file",
        }
    )

    if uri:
        print(f"\n   Save location: {uri}")

        # Write timestamped content
        content = f"Output generated at {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += "=" * 50 + "\n"
        content += "This is sample output from VSCode Sockpuppet.\n"

        try:
            client.fs.write_text(uri, content)
            print("   ✓ File saved!")
        except Exception as e:
            print(f"   ✗ Error: {e}")
    else:
        print("\n   Dialog canceled")


def example_workflow_select_and_process(client: VSCodeClient):
    """Example 7: Complete workflow - select, process, save."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Complete Workflow")
    print("=" * 70)
    print("\nWorkflow: Select file → Process → Save result")

    # Step 1: Select input file
    print("\n1. Select input file...")
    input_uris = client.window.show_open_dialog(
        {
            "canSelectFiles": True,
            "canSelectFolders": False,
            "canSelectMany": False,
            "filters": {
                "Text Files": ["txt", "md"],
                "Python Files": ["py"],
                "All Files": ["*"],
            },
            "title": "Select file to process",
        }
    )

    if not input_uris:
        print("   Canceled")
        return

    input_uri = input_uris[0]
    print(f"   Selected: {input_uri}")

    # Step 2: Read and process
    print("\n2. Processing file...")
    try:
        content = client.fs.read_text(input_uri)
        lines = content.split("\n")

        # Create statistics
        stats = {
            "lines": len(lines),
            "chars": len(content),
            "words": len(content.split()),
            "non_empty_lines": len([line for line in lines if line.strip()]),
        }

        print(f"   Lines: {stats['lines']}")
        print(f"   Characters: {stats['chars']}")
        print(f"   Words: {stats['words']}")

    except Exception as e:
        print(f"   Error reading file: {e}")
        return

    # Step 3: Save results
    print("\n3. Save processing results...")
    output_uri = client.window.show_save_dialog(
        {
            "filters": {"Text Files": ["txt"], "All Files": ["*"]},
            "title": "Save analysis results",
            "saveLabel": "Save Results",
        }
    )

    if not output_uri:
        print("   Canceled")
        return

    # Write analysis report
    report = f"""File Analysis Report
Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}
Input File: {input_uri}

Statistics:
-----------
Total Lines: {stats["lines"]}
Non-empty Lines: {stats["non_empty_lines"]}
Total Characters: {stats["chars"]}
Total Words: {stats["words"]}

Average Line Length: {stats["chars"] / max(stats["lines"], 1):.1f} chars
Average Word Length: {stats["chars"] / max(stats["words"], 1):.1f} chars
"""

    try:
        client.fs.write_text(output_uri, report)
        print(f"   ✓ Report saved to: {output_uri}")
    except Exception as e:
        print(f"   ✗ Error saving: {e}")


def main():
    """Run all file dialog examples."""
    print("File Dialog Examples")
    print("=" * 70)
    print("Demonstrates file open and save dialogs")

    client = VSCodeClient()
    client.connect()

    try:
        print("\n✓ Connected to VS Code")

        # Note about running examples
        print("\n" + "=" * 70)
        print("Note: Each example will show a system dialog.")
        print("You can cancel any dialog by pressing Escape.")
        print("=" * 70)

        time.sleep(2)

        # Run examples
        example_open_single_file(client)
        time.sleep(1)

        example_open_multiple_files(client)
        time.sleep(1)

        example_open_with_filters(client)
        time.sleep(1)

        example_select_folder(client)
        time.sleep(1)

        example_save_dialog(client)
        time.sleep(1)

        example_save_with_default_location(client)
        time.sleep(1)

        example_workflow_select_and_process(client)

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
