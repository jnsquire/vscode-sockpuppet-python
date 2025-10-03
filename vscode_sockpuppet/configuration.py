"""
Configuration management for VS Code settings.
"""

from enum import IntEnum
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .client import VSCodeClient


class ConfigurationTarget(IntEnum):
    """Configuration target specifies where to save settings."""

    GLOBAL = 1  # User settings
    WORKSPACE = 2  # Workspace settings
    WORKSPACE_FOLDER = 3  # Workspace folder settings


class WorkspaceConfiguration:
    """
    VS Code workspace configuration.

    Represents configuration values that can be read and updated.
    """

    def __init__(
        self,
        client: "VSCodeClient",
        section: Optional[str] = None,
        scope: Optional[str] = None,
    ):
        """
        Initialize configuration.

        Args:
            client: The VS Code client
            section: Configuration section (e.g., 'editor', 'python.linting')
            scope: Resource URI or language ID for scoped configuration
        """
        self.client = client
        self.section = section or ""
        self.scope = scope

    def get(self, key: str, default_value: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key (supports dot notation)
            default_value: Default value if key doesn't exist

        Returns:
            Configuration value or default_value

        Example:
            config = client.workspace.get_configuration('editor')
            font_size = config.get('fontSize', 14)
        """
        full_key = f"{self.section}.{key}" if self.section else key

        result = self.client._send_request(
            "workspace.getConfiguration",
            {"section": full_key, "scope": self.scope},
        )

        if result is None:
            return default_value
        return result

    def has(self, key: str) -> bool:
        """
        Check if a configuration key exists.

        Args:
            key: Configuration key (supports dot notation)

        Returns:
            True if the key exists

        Example:
            config = client.workspace.get_configuration('editor')
            if config.has('fontSize'):
                print("Font size is configured")
        """
        full_key = f"{self.section}.{key}" if self.section else key

        return self.client._send_request(
            "workspace.hasConfiguration",
            {"section": full_key, "scope": self.scope},
        )

    def inspect(self, key: str) -> Optional[dict]:
        """
        Inspect all configuration values for a key.

        Returns detailed information about where a configuration value
        comes from (default, global, workspace, workspace folder).

        Args:
            key: Configuration key (supports dot notation)

        Returns:
            Dictionary with keys: key, defaultValue, globalValue,
            workspaceValue, workspaceFolderValue, etc.
            Returns None if key doesn't exist.

        Example:
            config = client.workspace.get_configuration('editor')
            info = config.inspect('fontSize')
            if info:
                print(f"Default: {info.get('defaultValue')}")
                print(f"Global: {info.get('globalValue')}")
                print(f"Workspace: {info.get('workspaceValue')}")
        """
        full_key = f"{self.section}.{key}" if self.section else key

        return self.client._send_request(
            "workspace.inspectConfiguration",
            {"section": full_key, "scope": self.scope},
        )

    def update(
        self,
        key: str,
        value: Any,
        configuration_target: Optional[ConfigurationTarget | bool | None] = None,
        override_in_language: bool = False,
    ) -> None:
        """
        Update a configuration value.

        Args:
            key: Configuration key (supports dot notation)
            value: New value (use None to remove the setting)
            configuration_target: Where to save the setting:
                - ConfigurationTarget.GLOBAL: User settings
                - ConfigurationTarget.WORKSPACE: Workspace settings
                - ConfigurationTarget.WORKSPACE_FOLDER: Folder settings
                - True: User settings (same as GLOBAL)
                - False: Workspace settings
                - None: Auto-detect based on scope
            override_in_language: Whether to update language-specific value

        Raises:
            Exception: If update fails (e.g., invalid key, no workspace)

        Example:
            config = client.workspace.get_configuration('editor')
            # Update user settings
            config.update('fontSize', 16, ConfigurationTarget.GLOBAL)
            # Update workspace settings
            config.update('tabSize', 2, ConfigurationTarget.WORKSPACE)
            # Remove a setting
            config.update('fontSize', None, ConfigurationTarget.GLOBAL)
        """
        full_key = f"{self.section}.{key}" if self.section else key

        # Convert boolean to ConfigurationTarget
        if isinstance(configuration_target, bool):
            target = (
                ConfigurationTarget.GLOBAL
                if configuration_target
                else ConfigurationTarget.WORKSPACE
            )
        elif configuration_target is None:
            target = None
        else:
            target = configuration_target

        self.client._send_request(
            "workspace.updateConfiguration",
            {
                "section": full_key,
                "value": value,
                "configurationTarget": target.value if target else None,
                "scope": self.scope,
                "overrideInLanguage": override_in_language,
            },
        )
