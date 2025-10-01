"""
Tab Groups API for VS Code
"""

from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    from .client import VSCodeClient


class Tab:
    """Represents a tab within a tab group."""

    def __init__(self, data: dict):
        """
        Initialize a Tab from VS Code data.

        Args:
            data: Tab data from VS Code
        """
        self.label = data.get("label", "")
        self.is_active = data.get("isActive", False)
        self.is_dirty = data.get("isDirty", False)
        self.is_pinned = data.get("isPinned", False)
        self.is_preview = data.get("isPreview", False)
        self.group_id = data.get("groupId", 0)
        self.input = data.get("input")

    def __repr__(self) -> str:
        """String representation of the tab."""
        flags = []
        if self.is_active:
            flags.append("active")
        if self.is_dirty:
            flags.append("dirty")
        if self.is_pinned:
            flags.append("pinned")
        if self.is_preview:
            flags.append("preview")
        flag_str = f" [{', '.join(flags)}]" if flags else ""
        return f"Tab({self.label!r}{flag_str})"


class TabGroup:
    """Represents a group of tabs."""

    def __init__(self, data: dict):
        """
        Initialize a TabGroup from VS Code data.

        Args:
            data: Tab group data from VS Code
        """
        self.is_active = data.get("isActive", False)
        self.view_column = data.get("viewColumn", 1)
        self.group_id = data.get("groupId", 0)
        self.tabs = [Tab(tab_data) for tab_data in data.get("tabs", [])]

    @property
    def active_tab(self) -> Optional[Tab]:
        """Get the active tab in this group."""
        for tab in self.tabs:
            if tab.is_active:
                return tab
        return None

    def __repr__(self) -> str:
        """String representation of the tab group."""
        active_str = " (active)" if self.is_active else ""
        return (
            f"TabGroup(column={self.view_column}, "
            f"tabs={len(self.tabs)}{active_str})"
        )


class TabGroups:
    """Manages tab groups in VS Code."""

    def __init__(self, client: "VSCodeClient"):
        """
        Initialize TabGroups.

        Args:
            client: The VSCodeClient instance
        """
        self.client = client

    def get_all(self) -> list[TabGroup]:
        """
        Get all tab groups.

        Returns:
            List of all TabGroup instances

        Example:
            tab_groups = window.tab_groups.get_all()
            for group in tab_groups:
                print(f"Group {group.view_column}: {len(group.tabs)} tabs")
        """
        result = self.client._send_request("window.tabGroups.all")
        return [TabGroup(group_data) for group_data in result.get("groups", [])]

    def get_active_tab_group(self) -> Optional[TabGroup]:
        """
        Get the currently active tab group.

        Returns:
            The active TabGroup or None

        Example:
            active_group = window.tab_groups.get_active_tab_group()
            if active_group:
                print(f"Active group has {len(active_group.tabs)} tabs")
        """
        result = self.client._send_request("window.tabGroups.activeTabGroup")
        group_data = result.get("group")
        return TabGroup(group_data) if group_data else None

    def close_tab(
        self,
        tab: Tab,
        preserve_focus: bool = False,
    ) -> bool:
        """
        Close a specific tab.

        Args:
            tab: The tab to close
            preserve_focus: Whether to preserve focus

        Returns:
            True if successful

        Example:
            groups = window.tab_groups.get_all()
            for group in groups:
                for tab in group.tabs:
                    if "test" in tab.label.lower():
                        window.tab_groups.close_tab(tab)
        """
        result = self.client._send_request(
            "window.tabGroups.closeTab",
            {
                "groupId": tab.group_id,
                "tabLabel": tab.label,
                "preserveFocus": preserve_focus,
            },
        )
        return result.get("success", False)

    def close_group(
        self,
        group: TabGroup,
        preserve_focus: bool = False,
    ) -> bool:
        """
        Close all tabs in a tab group.

        Args:
            group: The tab group to close
            preserve_focus: Whether to preserve focus

        Returns:
            True if successful

        Example:
            groups = window.tab_groups.get_all()
            # Close all groups except the active one
            for group in groups:
                if not group.is_active:
                    window.tab_groups.close_group(group)
        """
        result = self.client._send_request(
            "window.tabGroups.closeGroup",
            {
                "groupId": group.group_id,
                "preserveFocus": preserve_focus,
            },
        )
        return result.get("success", False)

    def on_did_change_tab_groups(
        self,
        handler: Callable[[Any], None],
    ) -> Callable[[], None]:
        """
        Subscribe to tab group changes.

        Args:
            handler: Callback function for tab group changes

        Returns:
            Dispose function to unsubscribe

        Example:
            def on_groups_changed(data):
                print("Tab groups changed!")
                groups = window.tab_groups.get_all()
                print(f"Now have {len(groups)} groups")

            dispose = window.tab_groups.on_did_change_tab_groups(
                on_groups_changed
            )
            # Later: dispose()
        """
        event_name = "window.onDidChangeTabGroups"
        self.client.subscribe(event_name, handler)

        def dispose():
            self.client.unsubscribe(event_name, handler)

        return dispose

    def on_did_change_tabs(
        self,
        handler: Callable[[Any], None],
    ) -> Callable[[], None]:
        """
        Subscribe to tab changes.

        Args:
            handler: Callback function for tab changes

        Returns:
            Dispose function to unsubscribe

        Example:
            def on_tabs_changed(data):
                print("Tabs changed!")
                active = window.tab_groups.get_active_tab_group()
                if active and active.active_tab:
                    print(f"Active tab: {active.active_tab.label}")

            dispose = window.tab_groups.on_did_change_tabs(on_tabs_changed)
            # Later: dispose()
        """
        event_name = "window.onDidChangeTabs"
        self.client.subscribe(event_name, handler)

        def dispose():
            self.client.unsubscribe(event_name, handler)

        return dispose
