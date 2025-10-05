"""Webview event TypedDicts."""

from typing import Any, TypedDict


class WebviewMessageEvent(TypedDict, total=False):
    id: str
    message: Any


class WebviewDisposeEvent(TypedDict):
    id: str


class WebviewViewStateEvent(TypedDict):
    id: str
    visible: bool
    active: bool
