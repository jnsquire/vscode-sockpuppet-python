"""Tab group and tab event TypedDicts."""

from typing import TypedDict


class TabGroupsChangeEvent(TypedDict):
    opened: int
    closed: int
    changed: int


class TabsChangeEvent(TypedDict):
    opened: int
    closed: int
    changed: int
