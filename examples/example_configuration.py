"""
Example: VS Code Configuration Management

This example demonstrates how to read, inspect, and update VS Code settings.
"""

from vscode_sockpuppet import ConfigurationTarget, VSCodeClient


def main():
    # Connect to VS Code
    client = VSCodeClient()
    client.connect()

    print("=" * 60)
    print("VS Code Configuration Management Demo")
    print("=" * 60)

    # Example 1: Get configuration values
    print("\n1. Reading Configuration Values")
    print("-" * 60)

    # Get editor configuration
    editor_config = client.workspace.get_configuration("editor")
    font_size = editor_config.get("fontSize", 14)
    tab_size = editor_config.get("tabSize", 4)
    word_wrap = editor_config.get("wordWrap", "off")

    print(f"Editor Font Size: {font_size}")
    print(f"Editor Tab Size: {tab_size}")
    print(f"Editor Word Wrap: {word_wrap}")

    # Get Python-specific configuration
    python_config = client.workspace.get_configuration("python")
    python_path = python_config.get("defaultInterpreterPath")
    linting_enabled = python_config.get("linting.enabled", False)

    print(f"\nPython Default Interpreter: {python_path}")
    print(f"Python Linting Enabled: {linting_enabled}")

    # Example 2: Check if configuration keys exist
    print("\n2. Checking Configuration Keys")
    print("-" * 60)

    editor_config = client.workspace.get_configuration("editor")
    has_font = editor_config.has("fontSize")
    has_fake = editor_config.has("nonExistentSetting")

    print(f"Has 'fontSize': {has_font}")
    print(f"Has 'nonExistentSetting': {has_fake}")

    # Example 3: Inspect configuration (see all levels)
    print("\n3. Inspecting Configuration Details")
    print("-" * 60)

    editor_config = client.workspace.get_configuration("editor")
    font_info = editor_config.inspect("fontSize")

    if font_info:
        print(f"Key: {font_info.get('key')}")
        print(f"Default Value: {font_info.get('defaultValue')}")
        print(f"Global Value: {font_info.get('globalValue')}")
        print(f"Workspace Value: {font_info.get('workspaceValue')}")
        print(
            f"Workspace Folder Value: "
            f"{font_info.get('workspaceFolderValue')}"
        )

    # Example 4: Update configuration (User Settings)
    print("\n4. Updating Configuration (User Settings)")
    print("-" * 60)

    # Create a test setting in user settings
    test_config = client.workspace.get_configuration("workbench")

    # Update colorTheme in user settings
    print("Setting color theme to 'Default Dark+'...")
    test_config.update(
        "colorTheme",
        "Default Dark+",
        ConfigurationTarget.GLOBAL
    )
    print("User setting updated!")

    # Verify the change
    new_theme = test_config.get("colorTheme")
    print(f"Current theme: {new_theme}")

    # Example 5: Update workspace settings (if workspace is open)
    print("\n5. Updating Workspace Settings")
    print("-" * 60)

    try:
        # Try to update workspace settings
        editor_config = client.workspace.get_configuration("editor")

        # Save current tab size
        current_tab_size = editor_config.get("tabSize", 4)
        print(f"Current workspace tab size: {current_tab_size}")

        # Update workspace tab size
        new_tab_size = 2
        print(f"Updating workspace tab size to {new_tab_size}...")
        editor_config.update(
            "tabSize",
            new_tab_size,
            ConfigurationTarget.WORKSPACE
        )
        print("Workspace setting updated!")

        # Verify
        updated_tab_size = editor_config.get("tabSize")
        print(f"New workspace tab size: {updated_tab_size}")

        # Restore original value
        print(f"Restoring original tab size ({current_tab_size})...")
        editor_config.update(
            "tabSize",
            current_tab_size,
            ConfigurationTarget.WORKSPACE
        )
        print("Original value restored!")

    except Exception as e:
        print(f"Workspace settings not available: {e}")
        print("(This is normal if no workspace/folder is open)")

    # Example 6: Remove a setting (set to None/undefined)
    print("\n6. Removing Configuration Values")
    print("-" * 60)

    # Set a custom setting first
    custom_config = client.workspace.get_configuration("myExtension")
    print("Setting custom value...")
    custom_config.update(
        "customSetting",
        "test value",
        ConfigurationTarget.GLOBAL
    )

    value = custom_config.get("customSetting")
    print(f"Custom setting value: {value}")

    # Remove the setting
    print("Removing custom setting...")
    custom_config.update(
        "customSetting",
        None,
        ConfigurationTarget.GLOBAL
    )

    value_after = custom_config.get("customSetting")
    print(f"Custom setting after removal: {value_after}")

    # Example 7: Get nested configuration
    print("\n7. Working with Nested Configuration")
    print("-" * 60)

    # Get a specific nested configuration
    files_config = client.workspace.get_configuration("files")
    auto_save = files_config.get("autoSave", "off")
    exclude_patterns = files_config.get("exclude", {})

    print(f"Files Auto Save: {auto_save}")
    print(f"Files Exclude Patterns: {len(exclude_patterns)} patterns")
    if exclude_patterns:
        print("First few patterns:")
        for pattern in list(exclude_patterns.keys())[:3]:
            print(f"  - {pattern}")

    # Example 8: Boolean configuration target (shorthand)
    print("\n8. Using Boolean Configuration Target")
    print("-" * 60)

    test_config = client.workspace.get_configuration("editor")

    # True = User (Global) settings
    # False = Workspace settings
    print("Using True (User settings) and False (Workspace settings)")
    print("as shorthand for ConfigurationTarget...")

    # This is equivalent to ConfigurationTarget.GLOBAL
    test_config.update("minimap.enabled", True, True)
    print("Minimap enabled in User settings")

    print("\n" + "=" * 60)
    print("Configuration management demo complete!")
    print("=" * 60)

    client.disconnect()


if __name__ == "__main__":
    main()
