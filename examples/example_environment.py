"""
Example: Environment Properties

Demonstrates accessing VS Code environment properties and methods:
- Application information (name, root, version)
- System identifiers (machine ID, session ID)
- UI configuration (language, UI kind, URI scheme, shell)
- Clipboard operations
- Opening external URIs
"""

from vscode_sockpuppet import VSCodeClient


def example_environment_info():
    """Display all environment information."""
    print("=" * 60)
    print("Example 1: Environment Information")
    print("=" * 60)

    with VSCodeClient() as client:
        env = client.workspace.env

        # Application information
        print("\n📦 Application Information:")
        print(f"  Name: {env.app_name}")
        print(f"  Root: {env.app_root}")
        print(f"  URI Scheme: {env.uri_scheme}")

        # UI configuration
        print("\n🎨 UI Configuration:")
        print(f"  Language: {env.language}")
        ui_kind = "Desktop" if env.ui_kind == 1 else "Web"
        print(f"  UI Kind: {ui_kind} (value: {env.ui_kind})")

        # System information
        print("\n💻 System Information:")
        print(f"  Default Shell: {env.shell}")
        print(f"  Machine ID: {env.machine_id[:16]}...")  # Truncate for privacy
        print(f"  Session ID: {env.session_id[:16]}...")


def example_clipboard_operations():
    """Demonstrate clipboard read/write operations."""
    print("\n" + "=" * 60)
    print("Example 2: Clipboard Operations")
    print("=" * 60)

    with VSCodeClient() as client:
        env = client.workspace.env

        # Write to clipboard
        test_text = "Hello from VS Code Sockpuppet!"
        print(f"\n📋 Writing to clipboard: '{test_text}'")
        env.write_clipboard(test_text)

        # Read from clipboard
        clipboard_content = env.read_clipboard()
        print(f"✅ Read from clipboard: '{clipboard_content}'")

        # Verify
        if clipboard_content == test_text:
            print("✓ Clipboard operation successful!")
        else:
            print("✗ Clipboard content doesn't match")

        # Write structured data (as JSON string)
        import json

        data = {"name": "VS Code", "version": "1.0", "features": ["edit", "debug"]}
        json_str = json.dumps(data, indent=2)
        env.write_clipboard(json_str)
        print(f"\n📋 Wrote JSON to clipboard:\n{json_str}")

        # Read it back
        read_json = env.read_clipboard()
        parsed = json.loads(read_json)
        print("\n✅ Read back and parsed:")
        print(f"  Name: {parsed['name']}")
        print(f"  Version: {parsed['version']}")
        print(f"  Features: {', '.join(parsed['features'])}")


def example_external_urls():
    """Demonstrate opening external URLs."""
    print("\n" + "=" * 60)
    print("Example 3: Opening External URLs")
    print("=" * 60)

    with VSCodeClient() as client:
        env = client.workspace.env

        print("\n🌐 Opening external URLs...")

        # Open documentation
        url = "https://code.visualstudio.com/docs"
        print(f"\n1. Opening VS Code documentation: {url}")
        success = env.open_external(url)
        if success:
            print("   ✅ URL opened in default browser")
        else:
            print("   ✗ Failed to open URL")

        # Note: These don't actually open in this example to avoid spam
        # Uncomment to try them:

        # # Open GitHub repository
        # repo_url = "https://github.com/microsoft/vscode"
        # print(f"\n2. Opening GitHub repo: {repo_url}")
        # env.open_external(repo_url)

        # # Open email client
        # email = "mailto:feedback@example.com?subject=VS%20Code%20Feedback"
        # print(f"\n3. Opening email client: {email}")
        # env.open_external(email)

        # # Open file protocol (Windows example)
        # if env.ui_kind == 1:  # Desktop only
        #     file_path = "file:///C:/Windows/System32"
        #     print(f"\n4. Opening file explorer: {file_path}")
        #     env.open_external(file_path)


def example_environment_detection():
    """Use environment properties to detect runtime context."""
    print("\n" + "=" * 60)
    print("Example 4: Environment Detection")
    print("=" * 60)

    with VSCodeClient() as client:
        env = client.workspace.env

        print("\n🔍 Detecting runtime environment...")

        # Check if running in VS Code or VS Code Insiders
        if "insiders" in env.uri_scheme.lower():
            print("  Running in: VS Code Insiders")
        else:
            print("  Running in: VS Code Stable")

        # Check UI type
        if env.ui_kind == 1:
            print("  Platform: Desktop Application")
            print(f"  Default Shell: {env.shell}")
        else:
            print("  Platform: Web Browser")

        # Check language for localization
        lang = env.language.lower()
        greetings = {
            "en": "Hello!",
            "es": "¡Hola!",
            "fr": "Bonjour!",
            "de": "Guten Tag!",
            "zh-cn": "你好!",
            "ja": "こんにちは!",
        }
        greeting = greetings.get(lang, "Hello!")
        print(f"  UI Language: {env.language}")
        print(f"  Localized greeting: {greeting}")


def example_environment_caching():
    """Demonstrate that environment properties are cached."""
    print("\n" + "=" * 60)
    print("Example 5: Environment Property Caching")
    print("=" * 60)

    with VSCodeClient() as client:
        env = client.workspace.env

        print("\n⚡ Environment properties are cached for performance")
        print("   (First access queries VS Code, subsequent accesses use cache)")

        # First access - queries VS Code
        print("\n1. First access to app_name...")
        name1 = env.app_name
        print(f"   Result: {name1}")

        # Second access - from cache
        print("\n2. Second access to app_name (from cache)...")
        name2 = env.app_name
        print(f"   Result: {name2}")

        # Verify caching
        print(f"\n✓ Both accesses returned the same value: {name1 == name2}")

        # Access multiple properties
        print("\n3. Accessing multiple properties:")
        properties = {
            "app_name": env.app_name,
            "language": env.language,
            "ui_kind": env.ui_kind,
            "uri_scheme": env.uri_scheme,
        }

        for key, value in properties.items():
            print(f"   {key}: {value}")


def main():
    """Run all environment examples."""
    print("\n" + "=" * 60)
    print("VS Code Environment API Examples")
    print("=" * 60)

    try:
        # Run examples
        example_environment_info()
        example_clipboard_operations()
        example_external_urls()
        example_environment_detection()
        example_environment_caching()

        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
