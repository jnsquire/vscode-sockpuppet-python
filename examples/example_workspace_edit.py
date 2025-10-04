"""
Example demonstrating workspace.applyEdit() for batch modifications.

This example shows how to make atomic changes across multiple files,
including text edits, file creation, deletion, and renaming.
"""

from vscode_sockpuppet import VSCodeClient, WorkspaceEdit


def example_text_edits(client: VSCodeClient):
    """Apply text edits to multiple files atomically."""
    print("\n=== Text Edits Example ===")

    # Get some open documents
    docs = client.workspace.text_documents()
    if not docs:
        print("No open documents. Open some files first.")
        return

    # Create a workspace edit that adds comments to multiple files
    edit: WorkspaceEdit = {
        "documentChanges": [
            {
                "uri": docs[0].uri,
                "edits": [
                    {
                        "range": {
                            "start": {"line": 0, "character": 0},
                            "end": {"line": 0, "character": 0},
                        },
                        "newText": "# Modified by workspace.applyEdit()\n",
                    }
                ],
            }
        ]
    }

    result = client.workspace.apply_edit(edit)
    print(f"Text edits applied: {result['success']}")
    if result["success"]:
        print(f"  Added header comment to {docs[0].uri}")


def example_create_files(client: VSCodeClient):
    """Create new files with content."""
    print("\n=== Create Files Example ===")

    # Get workspace folder
    folders = client.workspace.get_workspace_folders()
    if not folders:
        print("No workspace folder open.")
        return

    workspace_uri = folders[0]["uri"]
    new_file_uri = f"{workspace_uri}/test_created_file.txt"

    # Create file and add content in one atomic operation
    edit: WorkspaceEdit = {
        "createFiles": [{"uri": new_file_uri, "options": {"overwrite": False}}],
        "documentChanges": [
            {
                "uri": new_file_uri,
                "edits": [
                    {
                        "range": {
                            "start": {"line": 0, "character": 0},
                            "end": {"line": 0, "character": 0},
                        },
                        "newText": (
                            "This file was created by "
                            "workspace.applyEdit()\n"
                            "It demonstrates atomic file creation "
                            "with content.\n"
                        ),
                    }
                ],
            }
        ],
    }

    result = client.workspace.apply_edit(edit)
    print(f"File creation: {result['success']}")
    if result["success"]:
        print(f"  Created: {new_file_uri}")


def example_rename_file(client: VSCodeClient):
    """Rename a file."""
    print("\n=== Rename File Example ===")

    folders = client.workspace.get_workspace_folders()
    if not folders:
        print("No workspace folder open.")
        return

    workspace_uri = folders[0]["uri"]
    old_uri = f"{workspace_uri}/test_created_file.txt"
    new_uri = f"{workspace_uri}/test_renamed_file.txt"

    edit: WorkspaceEdit = {
        "renameFiles": [
            {
                "oldUri": old_uri,
                "newUri": new_uri,
                "options": {"overwrite": False},
            }
        ]
    }

    result = client.workspace.apply_edit(edit)
    print(f"File rename: {result['success']}")
    if result["success"]:
        print(f"  Renamed: {old_uri} -> {new_uri}")


def example_delete_file(client: VSCodeClient):
    """Delete a file."""
    print("\n=== Delete File Example ===")

    folders = client.workspace.get_workspace_folders()
    if not folders:
        print("No workspace folder open.")
        return

    workspace_uri = folders[0]["uri"]
    file_uri = f"{workspace_uri}/test_renamed_file.txt"

    edit: WorkspaceEdit = {"deleteFiles": [{"uri": file_uri, "options": {"recursive": False}}]}

    result = client.workspace.apply_edit(edit)
    print(f"File deletion: {result['success']}")
    if result["success"]:
        print(f"  Deleted: {file_uri}")


def example_complex_refactoring(client: VSCodeClient):
    """Demonstrate a complex refactoring across multiple files."""
    print("\n=== Complex Refactoring Example ===")

    docs = client.workspace.text_documents()
    if len(docs) < 2:
        print("Need at least 2 open documents for this example.")
        return

    # Simulate a refactoring that:
    # 1. Adds an import to the first file
    # 2. Updates a function call in the second file
    # 3. Both changes happen atomically
    edit: WorkspaceEdit = {
        "documentChanges": [
            {
                "uri": docs[0].uri,
                "edits": [
                    {
                        "range": {
                            "start": {"line": 0, "character": 0},
                            "end": {"line": 0, "character": 0},
                        },
                        "newText": "# Added import during refactoring\n",
                    }
                ],
            },
            {
                "uri": docs[1].uri,
                "edits": [
                    {
                        "range": {
                            "start": {"line": 0, "character": 0},
                            "end": {"line": 0, "character": 0},
                        },
                        "newText": "# Updated during refactoring\n",
                    }
                ],
            },
        ]
    }

    result = client.workspace.apply_edit(edit)
    print(f"Refactoring: {result['success']}")
    if result["success"]:
        print(f"  Modified {len(edit['documentChanges'])} files atomically")


def main():
    """Run workspace edit examples."""
    with VSCodeClient() as client:
        print("Workspace Edit Examples")
        print("=" * 50)

        # Demonstrate different types of workspace edits
        example_text_edits(client)
        example_create_files(client)
        example_rename_file(client)
        example_delete_file(client)
        example_complex_refactoring(client)

        print("\n" + "=" * 50)
        print("All workspace edit examples completed!")
        print("\nNote: All operations are atomic - they either all succeed or all fail.")
        print("This is useful for refactoring operations that span multiple files.")


if __name__ == "__main__":
    main()
