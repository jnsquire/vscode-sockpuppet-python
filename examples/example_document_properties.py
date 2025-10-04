"""
Example demonstrating TextDocument properties.

This example shows how to access all properties of TextDocument objects,
including the newly added encoding property.
"""

from vscode_sockpuppet import VSCodeClient


def main():
    """Demonstrate TextDocument properties."""
    with VSCodeClient() as client:
        print("TextDocument Properties Example")
        print("=" * 60)

        # Get all open documents
        docs = client.workspace.text_documents()

        if not docs:
            print("No open documents. Please open some files first.")
            return

        # Display properties for each document
        for i, doc in enumerate(docs, 1):
            print(f"\nDocument {i}:")
            print("-" * 60)

            # Basic identity properties
            print(f"  URI:          {doc.uri}")
            print(f"  File Name:    {doc.file_name}")
            print(f"  Language ID:  {doc.language_id}")

            # State properties
            print(f"  Is Untitled:  {doc.is_untitled}")
            print(f"  Is Dirty:     {doc.is_dirty}")
            print(f"  Is Closed:    {doc.is_closed}")
            print(f"  Version:      {doc.version}")

            # Content properties
            print(f"  Line Count:   {doc.line_count}")
            print(f"  EOL:          {repr(doc.eol)}")
            print(f"  Encoding:     {doc.encoding}")

            # Get some sample content
            if doc.line_count > 0:
                first_line = doc.line_at(0)
                print(f"  First Line:   {repr(first_line.text[:50])}")

        print("\n" + "=" * 60)
        print(f"Total documents: {len(docs)}")

        # Demonstrate encoding specifically
        print("\n" + "=" * 60)
        print("Encoding Information:")
        print("-" * 60)
        for doc in docs:
            filename = doc.file_name.split("\\")[-1]
            print(f"  {filename:30} -> {doc.encoding}")

        print("\nNote: Common encodings include utf8, utf8bom, utf16le, utf16be, etc.")


if __name__ == "__main__":
    main()
