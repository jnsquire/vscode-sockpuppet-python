import json
import multiprocessing
import socket
import threading
import time
from contextlib import contextmanager
from multiprocessing.process import BaseProcess
from typing import Any, Dict, List

from vscode_sockpuppet.client import VSCodeClient
from vscode_sockpuppet.webview import WebviewPanel


class SocketPipeAdapter:
    """Wrap a socket with Windows pipe-like semantics for VSCodeClient."""

    def __init__(self, sock: socket.socket):
        self._sock = sock
        self._lock = threading.Lock()

    def write(self, data: bytes) -> None:
        with self._lock:
            self._sock.sendall(data)

    def flush(self) -> None:  # pragma: no cover - included for API completeness
        pass

    def read(self, n: int) -> bytes:
        return self._sock.recv(n)

    def close(self) -> None:
        try:
            self._sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        finally:
            try:
                self._sock.close()
            except Exception:
                pass


def _extension_host_sequence(
    port_queue: multiprocessing.Queue, script: Dict[str, List[Dict[str, Any]]]
) -> None:
    """Run a tiny extension host that serves responses and scripted events."""

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        _, port = server.getsockname()
        port_queue.put(port)

        conn, _ = server.accept()
        try:
            buf = b""
            pending = {event: list(entries) for event, entries in script.items()}
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    if not line.strip():
                        continue
                    request = json.loads(line.decode("utf-8"))
                    method = request.get("method")
                    if method == "events.subscribe":
                        event_name = request.get("params", {}).get("event")
                        response = {"id": request.get("id"), "result": True}
                        conn.sendall((json.dumps(response) + "\n").encode("utf-8"))
                        notifications = pending.pop(event_name, [])
                        for entry in notifications:
                            delay = float(entry.get("delay", 0.0))
                            if delay:
                                time.sleep(delay)
                            payload = {
                                "type": "event",
                                "event": event_name,
                                "data": entry.get("data"),
                            }
                            conn.sendall((json.dumps(payload) + "\n").encode("utf-8"))
                    elif method == "events.unsubscribe":
                        response = {"id": request.get("id"), "result": True}
                        conn.sendall((json.dumps(response) + "\n").encode("utf-8"))
                    else:
                        response = {"id": request.get("id"), "result": True}
                        conn.sendall((json.dumps(response) + "\n").encode("utf-8"))
                if not pending:
                    break
            time.sleep(0.1)
        finally:
            try:
                conn.close()
            except Exception:
                pass
    finally:
        try:
            server.close()
        except Exception:
            pass


def _start_client_and_host(
    script: Dict[str, List[Dict[str, Any]]],
) -> tuple[VSCodeClient, BaseProcess, multiprocessing.Queue]:
    ctx = multiprocessing.get_context("spawn")
    port_queue = ctx.Queue()
    host_proc = ctx.Process(target=_extension_host_sequence, args=(port_queue, script))
    host_proc.start()

    client: VSCodeClient | None = None

    try:
        port = port_queue.get(timeout=5.0)
        raw_sock = socket.create_connection(("127.0.0.1", port))
        client = VSCodeClient()
        client.sock = SocketPipeAdapter(raw_sock)
        client._buffer = ""
        return client, host_proc, port_queue
    except Exception:
        if host_proc.is_alive():
            host_proc.terminate()
        raise


def _prepare_event_loop(client: VSCodeClient) -> threading.Event:
    allow_event_loop_start = threading.Event()
    original_loop = client._event_loop

    def _delayed_loop():
        allow_event_loop_start.wait(timeout=5.0)
        return original_loop()

    client._event_loop = _delayed_loop
    return allow_event_loop_start


@contextmanager
def panel_message_handler(panel: WebviewPanel, handler):
    """Context manager that registers a message handler on a panel and
    automatically unsubscribes on exit.
    """
    unsub = panel.on_did_receive_message(handler)
    try:
        yield handler
    finally:
        try:
            unsub()
        except Exception:
            pass


@contextmanager
def panel_dispose_handler(panel: WebviewPanel, handler):
    unsub = panel.on_did_dispose(handler)
    try:
        yield handler
    finally:
        try:
            unsub()
        except Exception:
            pass


@contextmanager
def panel_viewstate_handler(panel: WebviewPanel, handler):
    unsub = panel.on_did_change_view_state(handler)
    try:
        yield handler
    finally:
        try:
            unsub()
        except Exception:
            pass


def _cleanup_client(client: VSCodeClient | None) -> None:
    if client is None:
        return
    client._running = False
    if client._event_thread:
        client._event_thread.join(timeout=1.0)
    if client.sock:
        client.sock.close()


def _cleanup_host(host_proc: BaseProcess, port_queue: multiprocessing.Queue) -> None:
    try:
        port_queue.close()
    except Exception:
        pass
    if host_proc.is_alive():
        host_proc.join(timeout=1.0)
    if host_proc.is_alive():
        host_proc.terminate()
        host_proc.join(timeout=1.0)


def test_subprocess_message_dispatch():
    script = {
        "webview.onDidReceiveMessage": [
            {"data": {"id": "panel-subproc", "message": {"value": 0}}},
            {"data": {"id": "panel-subproc", "message": {"value": 1}}, "delay": 0.05},
            {"data": {"id": "panel-subproc", "message": {"value": 2}}, "delay": 0.05},
        ]
    }

    client, host_proc, port_queue = _start_client_and_host(script)
    allow_event_loop_start = _prepare_event_loop(client)

    panel = WebviewPanel(client, panel_id="panel-subproc", view_type="tests", title="panel")
    received: List[Any] = []
    unsubscribe = panel.on_did_receive_message(lambda payload: received.append(payload))

    expected_messages = len(script["webview.onDidReceiveMessage"])
    delivered = threading.Event()

    def session_listener(state: str, payload: Dict[str, Any]) -> None:
        if state != "event-dispatched":
            return
        if payload.get("event") != "webview.onDidReceiveMessage":
            return
        if len(received) >= expected_messages:
            delivered.set()

    with client.session_listener(session_listener):
        allow_event_loop_start.set()
        assert delivered.wait(timeout=1.0)

    try:
        assert received == [{"value": 0}, {"value": 1}, {"value": 2}]
    finally:
        unsubscribe()
        _cleanup_client(client)
        _cleanup_host(host_proc, port_queue)


def test_subprocess_multiple_panels_share_single_subscription():
    script = {
        "webview.onDidReceiveMessage": [
            {"data": {"id": "alpha", "message": "one"}},
            {"data": {"id": "beta", "message": "two"}, "delay": 0.05},
        ]
    }

    client, host_proc, port_queue = _start_client_and_host(script)
    allow_event_loop_start = _prepare_event_loop(client)

    panel_a = WebviewPanel(client, panel_id="alpha", view_type="tests", title="A")
    panel_b = WebviewPanel(client, panel_id="beta", view_type="tests", title="B")

    received_a: List[Any] = []
    received_b: List[Any] = []

    unsub_a = panel_a.on_did_receive_message(received_a.append)
    unsub_b = panel_b.on_did_receive_message(received_b.append)

    delivery_ready = threading.Event()

    def session_listener(state: str, payload: Dict[str, Any]) -> None:
        if state != "event-dispatched":
            return
        if payload.get("event") != "webview.onDidReceiveMessage":
            return
        if len(received_a) >= 1 and len(received_b) >= 1:
            delivery_ready.set()

    with client.session_listener(session_listener):
        allow_event_loop_start.set()
        assert delivery_ready.wait(timeout=1.0)

    try:
        assert received_a == ["one"]
        assert received_b == ["two"]
    finally:
        unsub_a()
        unsub_b()
        _cleanup_client(client)
        _cleanup_host(host_proc, port_queue)


def test_subprocess_dispose_event_marks_panel_disposed():
    script = {
        "webview.onDidDispose": [
            {"data": {"id": "disposer"}, "delay": 0.05},
        ]
    }

    client, host_proc, port_queue = _start_client_and_host(script)
    allow_event_loop_start = _prepare_event_loop(client)

    panel = WebviewPanel(client, panel_id="disposer", view_type="tests", title="dispose")

    dispose_called = threading.Event()
    panel.on_did_dispose(lambda: dispose_called.set())

    allow_event_loop_start.set()
    assert dispose_called.wait(timeout=1.0)
    assert panel.disposed is True

    try:
        panel.dispose()
    finally:
        _cleanup_client(client)
        _cleanup_host(host_proc, port_queue)


def test_subprocess_view_state_event_routes_to_handler():
    script = {
        "webview.onDidChangeViewState": [
            {
                "data": {
                    "id": "stateful",
                    "visible": True,
                    "active": False,
                },
                "delay": 0.05,
            }
        ]
    }

    client, host_proc, port_queue = _start_client_and_host(script)
    allow_event_loop_start = _prepare_event_loop(client)

    panel = WebviewPanel(client, panel_id="stateful", view_type="tests", title="state")

    states: List[dict[str, Any]] = []
    panel.on_did_change_view_state(lambda state: states.append(state))

    state_notified = threading.Event()

    def session_listener(state: str, payload: Dict[str, Any]) -> None:
        if state != "event-dispatched":
            return
        if payload.get("event") != "webview.onDidChangeViewState":
            return
        if states:
            state_notified.set()

    with client.session_listener(session_listener):
        allow_event_loop_start.set()
        assert state_notified.wait(timeout=1.0)

    try:
        assert states == [{"visible": True, "active": False}]
    finally:
        _cleanup_client(client)
        _cleanup_host(host_proc, port_queue)


def test_subprocess_workspace_change_text_document_routes_to_handler():
    script = {
        "workspace.onDidChangeTextDocument": [
            {
                "data": {
                    "uri": "file:///test/file.py",
                    "contentChanges": [
                        {
                            "range": {
                                "start": {"line": 0, "character": 0},
                                "end": {"line": 0, "character": 1},
                            },
                            "text": "x",
                        }
                    ],
                },
                "delay": 0.05,
            }
        ]
    }

    client, host_proc, port_queue = _start_client_and_host(script)
    allow_event_loop_start = _prepare_event_loop(client)

    received: list[dict] = []
    unsubscribe = client.workspace.on_did_change_text_document(lambda payload: received.append(payload))

    delivered = threading.Event()

    def session_listener(state: str, payload: Dict[str, Any]) -> None:
        if state != "event-dispatched":
            return
        if payload.get("event") != "workspace.onDidChangeTextDocument":
            return
        if received:
            delivered.set()

    with client.session_listener(session_listener):
        allow_event_loop_start.set()
        assert delivered.wait(timeout=1.0)

    try:
        assert (
            received
            == [
                {
                    "uri": "file:///test/file.py",
                    "contentChanges": [
                        {
                            "range": {
                                "start": {"line": 0, "character": 0},
                                "end": {"line": 0, "character": 1},
                            },
                            "text": "x",
                        }
                    ],
                }
            ]
        )
    finally:
        try:
            unsubscribe()
        except Exception:
            pass
        _cleanup_client(client)
        _cleanup_host(host_proc, port_queue)


def test_subprocess_window_on_did_open_terminal_routes_to_handler():
    script = {
        "window.onDidOpenTerminal": [
            {"data": {"name": "test-terminal"}, "delay": 0.05}
        ]
    }

    client, host_proc, port_queue = _start_client_and_host(script)
    allow_event_loop_start = _prepare_event_loop(client)

    received: list[dict] = []
    unsubscribe = client.window.on_did_open_terminal(lambda payload: received.append(payload))

    delivered = threading.Event()

    def session_listener(state: str, payload: Dict[str, Any]) -> None:
        if state != "event-dispatched":
            return
        if payload.get("event") != "window.onDidOpenTerminal":
            return
        if received:
            delivered.set()

    with client.session_listener(session_listener):
        allow_event_loop_start.set()
        assert delivered.wait(timeout=1.0)

    try:
        assert received == [{"name": "test-terminal"}]
    finally:
        try:
            unsubscribe()
        except Exception:
            pass
        _cleanup_client(client)
        _cleanup_host(host_proc, port_queue)


def _run_single_event_test(event_name: str, payload: dict):
    script = {event_name: [{"data": payload}]}

    client, host_proc, port_queue = _start_client_and_host(script)
    allow_event_loop_start = _prepare_event_loop(client)

    received: list[dict] = []
    unsub = client.add_event_listener(event_name, lambda p: received.append(p))

    delivered = threading.Event()

    def session_listener(state: str, payload: Dict[str, Any]) -> None:
        if state != "event-dispatched":
            return
        if payload.get("event") == event_name and received:
            delivered.set()

    with client.session_listener(session_listener):
        allow_event_loop_start.set()
        assert delivered.wait(timeout=1.0)

    try:
        time.sleep(0.02)
        assert received == [payload]
    finally:
        try:
            unsub()
        except Exception:
            pass
        _cleanup_client(client)
        _cleanup_host(host_proc, port_queue)


def test_subprocess_watcher_on_create_routes_to_handler():
    _run_single_event_test("watcher.testwatcher.onCreate", {"uri": "file:///watched/new.txt"})


def test_subprocess_watcher_on_change_routes_to_handler():
    _run_single_event_test("watcher.testwatcher.onChange", {"uri": "file:///watched/new.txt"})


def test_subprocess_watcher_on_delete_routes_to_handler():
    _run_single_event_test("watcher.testwatcher.onDelete", {"uri": "file:///watched/new.txt"})



def test_subprocess_workspace_on_did_create_files_routes_to_handler():
    _run_single_event_test("workspace.onDidCreateFiles", {"files": [{"uri": "file:///a.txt"}]})


def test_subprocess_workspace_on_did_delete_files_routes_to_handler():
    _run_single_event_test("workspace.onDidDeleteFiles", {"files": [{"uri": "file:///b.txt"}]})


def test_subprocess_workspace_on_did_rename_files_routes_to_handler():
    _run_single_event_test(
        "workspace.onDidRenameFiles",
        {"files": [{"oldUri": "file:///c_old.txt", "newUri": "file:///c_new.txt"}]},
    )



def test_subprocess_window_on_did_change_tab_groups_routes_to_handler():
    _run_single_event_test("window.onDidChangeTabGroups", {"opened": 1, "closed": 0, "changed": 0})


def test_subprocess_window_on_did_change_tabs_routes_to_handler():
    _run_single_event_test("window.onDidChangeTabs", {"opened": 0, "closed": 1, "changed": 0})
