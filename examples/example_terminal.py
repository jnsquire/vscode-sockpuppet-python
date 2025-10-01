"""
Terminal Operations Example

This example demonstrates terminal operations including:
- Creating terminals with custom names and shells
- Sending text to terminals
- Showing and hiding terminals
- Disposing terminals
"""

import time

from vscode_sockpuppet import VSCodeClient


def main():
    """Demonstrate terminal operations."""
    with VSCodeClient() as client:
        print("=== Terminal Operations Demo ===\n")

        # Example 1: Create a simple terminal
        print("1. Creating a simple terminal...")
        terminal1 = client.window.create_terminal(name="Demo Terminal")
        print(f"   Created: {terminal1}")

        # Example 2: Send commands to terminal
        print("\n2. Sending commands to terminal...")
        terminal1.send_text("echo 'Hello from Python!'")
        time.sleep(0.5)
        terminal1.send_text("echo 'Current directory:'")
        terminal1.send_text("pwd")
        print("   Commands sent")

        # Example 3: Show the terminal
        print("\n3. Showing the terminal...")
        terminal1.show(preserve_focus=False)  # Show and take focus
        print("   Terminal should now be visible and focused")
        time.sleep(2)

        # Example 4: Create another terminal with custom shell
        print("\n4. Creating a terminal with custom settings...")
        terminal2 = client.window.create_terminal(
            name="Python REPL",
        )
        terminal2.send_text("python")
        terminal2.send_text("print('Hello from Python REPL!')")
        terminal2.send_text("2 + 2")
        terminal2.show()
        print("   Python REPL terminal created and shown")
        time.sleep(2)

        # Example 5: Hide a terminal
        print("\n5. Hiding the first terminal...")
        terminal1.hide()
        print("   First terminal hidden")
        time.sleep(1)

        # Example 6: Run a series of commands
        print("\n6. Running a series of commands...")
        terminal3 = client.window.create_terminal(name="Git Status")
        commands = [
            "git status",
            "git branch",
            "git log --oneline -5",
        ]
        for cmd in commands:
            terminal3.send_text(cmd)
            time.sleep(0.3)
        terminal3.show(preserve_focus=True)
        print("   Git commands executed")
        time.sleep(2)

        # Example 7: Send text without newline (for interactive prompts)
        print("\n7. Demonstrating text without newline...")
        terminal4 = client.window.create_terminal(name="Interactive")
        terminal4.send_text("echo -n 'Type something: '", add_new_line=False)
        terminal4.show()
        print("   Interactive prompt created")
        time.sleep(2)

        # Example 8: Dispose terminals
        print("\n8. Cleaning up - disposing terminals...")
        terminal1.dispose()
        print("   Terminal 1 disposed")
        time.sleep(0.5)

        terminal2.dispose()
        print("   Terminal 2 disposed")
        time.sleep(0.5)

        terminal3.dispose()
        print("   Terminal 3 disposed")
        time.sleep(0.5)

        terminal4.dispose()
        print("   Terminal 4 disposed")

        print("\n=== Demo Complete ===")
        print("All terminals created and disposed successfully!")


def example_build_workflow():
    """Example: Automated build workflow using terminals."""
    print("\n=== Build Workflow Example ===")

    with VSCodeClient() as client:
        # Create a terminal for the build process
        build_terminal = client.window.create_terminal(name="Build Process")

        print("Starting automated build workflow...")

        # Install dependencies
        build_terminal.send_text("echo 'Installing dependencies...'")
        build_terminal.send_text("npm install")

        # Run tests
        build_terminal.send_text("echo 'Running tests...'")
        build_terminal.send_text("npm test")

        # Build the project
        build_terminal.send_text("echo 'Building project...'")
        build_terminal.send_text("npm run build")

        # Show the terminal with results
        build_terminal.show(preserve_focus=False)

        print("Build workflow started in terminal!")
        print("Check the terminal for progress...")


def example_multiple_terminals():
    """Example: Working with multiple terminals for different tasks."""
    print("\n=== Multiple Terminals Example ===")

    with VSCodeClient() as client:
        # Development server terminal
        server_terminal = client.window.create_terminal(name="Dev Server")
        server_terminal.send_text("npm run dev")
        server_terminal.show(preserve_focus=True)

        time.sleep(1)

        # Watch terminal for file changes
        watch_terminal = client.window.create_terminal(name="File Watcher")
        watch_terminal.send_text("npm run watch")
        watch_terminal.show(preserve_focus=True)

        time.sleep(1)

        # Testing terminal
        test_terminal = client.window.create_terminal(name="Test Runner")
        test_terminal.send_text("npm run test:watch")
        test_terminal.show(preserve_focus=True)

        print("Started 3 terminals:")
        print("  1. Dev Server")
        print("  2. File Watcher")
        print("  3. Test Runner")
        print("\nAll running simultaneously!")

        # Keep them running for a bit
        time.sleep(5)

        # Clean up
        print("\nCleaning up...")
        server_terminal.dispose()
        watch_terminal.dispose()
        test_terminal.dispose()
        print("All terminals disposed")


if __name__ == "__main__":
    # Run the main demo
    main()

    # Uncomment to run additional examples:
    # example_build_workflow()
    # example_multiple_terminals()
