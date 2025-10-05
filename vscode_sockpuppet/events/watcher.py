"""File watcher event TypedDicts."""

from typing import TypedDict


class FileWatcherEvent(TypedDict):
    uri: str
