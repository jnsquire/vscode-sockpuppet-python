"""
Comprehensive example demonstrating new high-value VSCode Sockpuppet features.

This example shows:
1. File System API - Read/write/delete files
2. Diagnostics API - Show errors/warnings
3. Status Bar Items - Extension UI
4. Progress Indicators - Long-running operations
5. Command Execution - Run VS Code commands
"""

from vscode_sockpuppet import (
    Diagnostic,
    DiagnosticSeverity,
    ProgressLocation,
    StatusBarAlignment,
    VSCodeClient,
    create_range,
    create_status_bar_item,
    with_progress,
)


def demonstrate_file_system(client: VSCodeClient):
    """Demonstrate file system operations."""
    print("\n=== File System Operations ===")

    # Create a test file
    test_uri = "file:///tmp/test_file.txt"
    client.fs.write_text(test_uri, "Hello from Python!")
    print(f"✓ Created file: {test_uri}")

    # Read the file
    content = client.fs.read_text(test_uri)
    print(f"✓ Read content: {content}")

    # Check if file exists
    exists = client.fs.exists(test_uri)
    print(f"✓ File exists: {exists}")

    # Get file stats
    stat = client.fs.stat(test_uri)
    print(f"✓ File size: {stat.size} bytes")

    # Create a directory
    dir_uri = "file:///tmp/test_directory"
    client.fs.create_directory(dir_uri)
    print(f"✓ Created directory: {dir_uri}")

    # List directory
    entries = client.fs.read_directory("file:///tmp")
    print(f"✓ Found {len(entries)} entries in /tmp")

    # Copy file
    copy_uri = "file:///tmp/test_file_copy.txt"
    client.fs.copy(test_uri, copy_uri)
    print(f"✓ Copied file to: {copy_uri}")

    # Clean up
    client.fs.delete(test_uri)
    client.fs.delete(copy_uri)
    print("✓ Cleaned up test files")


def demonstrate_diagnostics(client: VSCodeClient):
    """Demonstrate diagnostic operations."""
    print("\n=== Diagnostics API ===")

    # Create a diagnostic collection
    collection = client.languages.create_diagnostic_collection(
        "example-linter"
    )
    print("✓ Created diagnostic collection")

    # Open or create a test document
    doc = client.workspace.open_text_document(
        content="def hello():\n  print('world')\n  undefined_variable\n",
        language="python",
    )
    print(f"✓ Opened document: {doc.uri}")

    # Create some diagnostics
    diagnostics = [
        # Error on line 3 (undefined variable)
        Diagnostic(
            range=create_range(2, 2, 2, 20),
            message="Undefined variable 'undefined_variable'",
            severity=DiagnosticSeverity.Error,
            source="example-linter",
            code="E001",
        ),
        # Warning on line 2 (indentation)
        Diagnostic(
            range=create_range(1, 0, 1, 2),
            message="Inconsistent indentation",
            severity=DiagnosticSeverity.Warning,
            source="example-linter",
            code="W001",
        ),
        # Info on line 1
        Diagnostic(
            range=create_range(0, 0, 0, 12),
            message="Function could have a docstring",
            severity=DiagnosticSeverity.Information,
            source="example-linter",
            code="I001",
        ),
    ]

    # Set diagnostics for the document
    collection.set(doc.uri, diagnostics)
    print(f"✓ Set {len(diagnostics)} diagnostics on document")
    print("  - Check the Problems panel to see them!")

    # Wait a bit so user can see the diagnostics
    print("  (Diagnostics are visible in VS Code Problems panel)")

    return collection, doc.uri


def demonstrate_status_bar(client: VSCodeClient):
    """Demonstrate status bar operations."""
    print("\n=== Status Bar Items ===")

    # Create a status bar item
    status_item = create_status_bar_item(
        client, alignment=StatusBarAlignment.Left, priority=100
    )
    print("✓ Created status bar item")

    # Set properties
    status_item.text = "$(rocket) Python Active"
    status_item.tooltip = "VSCode Sockpuppet is running"
    status_item.command = "workbench.action.showCommands"
    status_item.color = "#00ff00"
    print("✓ Configured status bar item")

    # Show the item
    status_item.show()
    print("✓ Status bar item is now visible")
    print("  (Check the bottom-left of VS Code window)")

    return status_item


def demonstrate_progress(client: VSCodeClient):
    """Demonstrate progress indicators."""
    print("\n=== Progress Indicators ===")

    # Show a progress notification
    print("✓ Showing progress notification...")
    result = with_progress(
        client,
        location=ProgressLocation.Notification,
        title="Processing Python Code",
        message="Analyzing files...",
        cancellable=True,
    )
    print(f"✓ Progress result: {result}")


def demonstrate_commands(client: VSCodeClient):
    """Demonstrate command execution."""
    print("\n=== Command Execution ===")

    # Get list of available commands
    commands = client._send_request(
        "commands.getCommands", {"filterInternal": True}
    )
    print(f"✓ Found {len(commands)} commands")
    print(f"  Examples: {commands[:5]}")

    # Execute a command (open settings)
    print("✓ Executing command: workbench.action.openSettings")
    client._send_request(
        "commands.executeCommand", {"command": "workbench.action.openSettings"}
    )


def main():
    """Run all demonstrations."""
    print("VSCode Sockpuppet - High-Value Features Demo")
    print("=" * 50)

    # Connect to VS Code
    with VSCodeClient() as client:
        print("✓ Connected to VS Code\n")

        # Demonstrate all features
        demonstrate_file_system(client)
        collection, doc_uri = demonstrate_diagnostics(client)
        status_item = demonstrate_status_bar(client)
        demonstrate_progress(client)
        demonstrate_commands(client)

        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("=" * 50)
        print("\nPress Enter to clean up and exit...")
        input()

        # Clean up
        print("\nCleaning up...")
        collection.clear()
        collection.dispose()
        status_item.dispose()
        print("✓ Cleaned up resources")


if __name__ == "__main__":
    main()
