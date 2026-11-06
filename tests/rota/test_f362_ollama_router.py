"""
Frame 362: the router gives one address to two model servers.

Two stub servers from `http.server` stand in for the two cards. No real model
server runs in these tests.
"""
from __future__ import annotations

import http.client
import http.server
import io
import json
import socket
import threading
import time

import pytest

from probes.ollama_router import Router, pick


class Stub(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, name: str, models: list[str]):
        self.name = name
        self.models = models
        self.seen: list[tuple[str, str, bytes]] = []
        self.next_line = threading.Event()   # the test lets the second line go
        self.got_slow = threading.Event()    # the slow request arrived
        self.slow_closed = threading.Event()  # the router closed the slow one
        super().__init__(("127.0.0.1", 0), StubHandler)

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.server_address[1]}"


class StubHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server: Stub

    def log_message(self, format, *args):  # noqa: A002 -- the base signature
        pass

    def reply(self, doc: dict) -> None:
        data = json.dumps(doc).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self.server.seen.append(("GET", self.path, b""))
        if self.path in ("/api/tags", "/api/ps"):
            self.reply({"models": [{"name": m, "server": self.server.name}
                                   for m in self.server.models]})
        else:
            self.reply({"version": self.server.name})

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        self.server.seen.append(("POST", self.path, body))
        model = json.loads(body)["model"]
        if model == "slow":
            # A long prompt: Ollama sends no byte until the first token.
            self.server.got_slow.set()
            self.connection.settimeout(10)
            try:
                if self.connection.recv(1) == b"":
                    self.server.slow_closed.set()
            except OSError:
                self.server.slow_closed.set()
            return
        if model == "stream":
            self.send_response(200)
            self.send_header("Content-Type", "application/x-ndjson")
            self.send_header("Transfer-Encoding", "chunked")
            self.end_headers()
            for n, line in enumerate((b'{"n":1}\n', b'{"n":2}\n', b'{"n":3}\n')):
                if n:
                    # A router that buffers holds line one, so the test never
                    # releases the next line, and the stub sends n=0 instead.
                    if not self.server.next_line.wait(3):
                        line = b'{"n":0}\n'
                    self.server.next_line.clear()
                self.wfile.write(b"%x\r\n%s\r\n" % (len(line), line))
            self.wfile.write(b"0\r\n\r\n")
            return
        self.reply({"server": self.server.name, "model": model})


@pytest.fixture
def rig():
    first = Stub("first", ["qwen3.5:9b", "gemma4:12b-it-qat"])
    second = Stub("second", ["gemma4:12b-it-qat", "gemma4:26b"])
    log = io.StringIO()
    router = Router(("127.0.0.1", 0), first.url, [("gemma4", second.url)], log=log)
    servers = (first, second, router)
    for s in servers:
        threading.Thread(target=s.serve_forever, daemon=True).start()
    yield first, second, router, log
    for s in servers:
        s.shutdown()
        s.server_close()


def post(router, path: str, doc: dict) -> http.client.HTTPResponse:
    conn = http.client.HTTPConnection("127.0.0.1", router.server_address[1],
                                      timeout=10)
    conn.request("POST", path, body=json.dumps(doc),
                 headers={"Content-Type": "application/json"})
    return conn.getresponse()


def test_the_first_matching_prefix_wins_and_no_match_goes_to_the_default():
    routes = [("gemma4:26", "B"), ("gemma4", "C")]
    assert pick("gemma4:26b", routes, "A") == "B"
    assert pick("gemma4:12b-it-qat", routes, "A") == "C"
    assert pick("qwen3.5:9b", routes, "A") == "A"
    assert pick(None, routes, "A") == "A"


def test_each_model_reaches_its_own_server(rig):
    first, second, router, log = rig
    for path in ("/api/chat", "/api/show", "/v1/chat/completions"):
        assert json.loads(post(router, path, {"model": "gemma4:12b-it-qat"})
                          .read())["server"] == "second"
        assert json.loads(post(router, path, {"model": "qwen3.5:9b"})
                          .read())["server"] == "first"
    sent = {"model": "gemma4:12b-it-qat", "messages": [{"role": "user",
                                                         "content": "hi"}]}
    post(router, "/api/chat", sent).read()
    # The body passes unchanged.
    assert second.seen[-1] == ("POST", "/api/chat", json.dumps(sent).encode())
    lines = log.getvalue().splitlines()
    assert any("model=gemma4:12b-it-qat" in ln and f"server={second.url}" in ln
               and "status=200" in ln and "seconds=" in ln for ln in lines)


def test_a_streamed_reply_arrives_line_by_line_and_in_order(rig):
    _, second, router, _ = rig
    router.routes.insert(0, ("stream", second.url))
    resp = post(router, "/api/chat", {"model": "stream"})
    assert resp.status == 200
    assert resp.getheader("Content-Type") == "application/x-ndjson"
    got = []
    for _ in range(3):
        # The stub holds each next line until the test has read the one
        # before. A router that buffers the reply never gets past line one.
        line = _read_line(resp)
        got.append(json.loads(line)["n"])
        second.next_line.set()
    assert got == [1, 2, 3]
    assert resp.read() == b""


def _read_line(resp: http.client.HTTPResponse) -> bytes:
    buf = b""
    while not buf.endswith(b"\n"):
        piece = resp.read1(1)
        assert piece, "the stream ended before the line"
        buf += piece
    return buf


def get(router, path: str):
    conn = http.client.HTTPConnection("127.0.0.1", router.server_address[1],
                                      timeout=10)
    conn.request("GET", path)
    return json.loads(conn.getresponse().read())


def test_tags_hold_both_servers_models_once_each(rig):
    _, _, router, _ = rig
    assert [m["name"] for m in get(router, "/api/tags")["models"]] == [
        "qwen3.5:9b", "gemma4:12b-it-qat", "gemma4:26b"]
    assert get(router, "/api/version") == {"version": "first"}


def test_a_model_both_servers_list_keeps_the_picked_servers_entry(rig):
    # discover.py reads `context_length` from /api/ps, so the entry must come
    # from the server that runs the model, not from the first server listed.
    _, second, router, _ = rig
    second.models.insert(0, "qwen3.5:9b")
    for path in ("/api/ps", "/api/tags"):
        by_name = {m["name"]: m["server"] for m in get(router, path)["models"]}
        assert by_name == {"qwen3.5:9b": "first", "gemma4:12b-it-qat": "second",
                           "gemma4:26b": "second"}


def test_a_client_that_closes_early_closes_the_upstream(rig):
    _, second, router, log = rig
    # The stub holds a "slow" request silent, as a long prompt does.
    data = json.dumps({"model": "slow"}).encode()
    router.routes.insert(0, ("slow", second.url))
    client = socket.create_connection(("127.0.0.1", router.server_address[1]))
    client.sendall(b"POST /api/chat HTTP/1.1\r\nHost: x\r\n"
                   b"Content-Type: application/json\r\n"
                   b"Content-Length: %d\r\n\r\n%s" % (len(data), data))
    assert second.got_slow.wait(5)
    client.close()
    assert second.slow_closed.wait(5), "the upstream stayed open"
    deadline = time.monotonic() + 5
    while "client-closed" not in log.getvalue() and time.monotonic() < deadline:
        time.sleep(0.05)
    assert "status=client-closed" in log.getvalue()
