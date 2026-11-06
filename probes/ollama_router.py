"""
One address for two Ollama servers. The router picks the server by the model.

Rota reads one address, `OLLAMA_HOST` (`rota/llm/llm.py:44`), and every seat
uses it. The box has two cards, and no one card runs every seat's model well
(observed: dry run 6, 2026-11-06). The router listens on one port and sends
each request to the server that runs the request's model.

Usage:

    python probes/ollama_router.py --port 11436 --default http://127.0.0.1:11434 --route gemma4=http://127.0.0.1:11435

    OLLAMA_HOST=http://127.0.0.1:11436 python -m rota ...

- `--route KEY=URL` repeats. KEY is a prefix of the model name. The first
  matching route wins. A model with no match goes to `--default`.
- A request whose JSON body holds `model` goes to that model's server. The
  body passes unchanged. A request with no model goes to the default.
- `GET /api/tags` and `GET /api/ps` return the union of the servers' lists.
  For a name that two servers hold, the default's entry stays.
- The reply streams through chunk by chunk, with the upstream status and
  headers.
- When the client closes its connection, the router closes the upstream
  connection. Ollama then stops the generation, so the card is free again.
- Each request gets one thread and one log line on stderr.

Standard library only, so the router runs from any Python on the box.
"""
from __future__ import annotations

import argparse
import http.client
import http.server
import json
import select
import socket
import sys
import threading
import time
import urllib.parse

# These headers belong to one connection, not to the message (RFC 9110 7.6.1).
HOP = {"connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
       "proxy-connection", "te", "trailer", "transfer-encoding", "upgrade"}
UNION_PATHS = {"/api/tags", "/api/ps"}
CHUNK = 65536


def pick(model: str | None, routes: list[tuple[str, str]], default: str) -> str:
    """The server for a model. The first route whose key starts the name wins."""
    if model:
        for key, url in routes:
            if model.startswith(key):
                return url
    return default


def model_of(body: bytes) -> str | None:
    if not body:
        return None
    try:
        doc = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        return None
    model = doc.get("model") if isinstance(doc, dict) else None
    return model if isinstance(model, str) else None


def connect(url: str, timeout: float = 10.0) -> http.client.HTTPConnection:
    parts = urllib.parse.urlsplit(url)
    conn = http.client.HTTPConnection(parts.hostname, parts.port or 80,
                                      timeout=timeout)
    conn.connect()
    # A long prompt sends no byte until its first token. The client keeps the
    # time limit, and its close reaches the upstream through the watcher.
    conn.sock.settimeout(None)
    return conn


def fetch_json(url: str, path: str, timeout: float) -> dict | None:
    try:
        conn = http.client.HTTPConnection(
            urllib.parse.urlsplit(url).hostname,
            urllib.parse.urlsplit(url).port or 80, timeout=timeout)
        conn.request("GET", path)
        resp = conn.getresponse()
        data = resp.read()
        conn.close()
        if resp.status != 200:
            return None
        return json.loads(data)
    except (OSError, ValueError, http.client.HTTPException):
        return None


def union(servers: list[str], path: str, timeout: float = 4.0) -> dict | None:
    """The servers' `models` lists joined, one entry per name, in server order.
    The fetches run at once, so one slow server costs one timeout in total."""
    found: dict[int, dict | None] = {}

    def one(i: int, url: str) -> None:
        found[i] = fetch_json(url, path, timeout)

    threads = [threading.Thread(target=one, args=(i, u), daemon=True)
               for i, u in enumerate(servers)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout + 1)
    bodies = [found.get(i) for i in range(len(servers))]
    if all(b is None for b in bodies):
        return None
    models, seen = [], set()
    for body in bodies:
        for entry in (body or {}).get("models") or []:
            name = entry.get("name") or entry.get("model")
            if name in seen:
                continue
            seen.add(name)
            models.append(entry)
    return {"models": models}


def watch_client(sock: socket.socket, upstream: http.client.HTTPConnection,
                 done: threading.Event, gone: threading.Event) -> None:
    """Close the upstream when the client closes. A client sends nothing after
    its request, so a readable socket with no data is a closed client."""
    while not done.is_set():
        try:
            ready, _, _ = select.select([sock], [], [], 0.25)
        except (OSError, ValueError):
            ready = [sock]
        if not ready:
            continue
        try:
            peek = sock.recv(1, socket.MSG_PEEK)
        except OSError:
            peek = b""
        if peek:
            return  # The client sent more bytes. It is alive, so stop watching.
        gone.set()
        close_upstream(upstream)
        return


def close_upstream(conn: http.client.HTTPConnection) -> None:
    sock = conn.sock
    if sock is not None:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
    conn.close()


class Router(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, addr, default: str, routes: list[tuple[str, str]],
                 log=sys.stderr):
        self.default = default.rstrip("/")
        self.routes = [(k, u.rstrip("/")) for k, u in routes]
        self.log = log
        super().__init__(addr, Handler)

    def servers(self) -> list[str]:
        out = [self.default]
        for _, url in self.routes:
            if url not in out:
                out.append(url)
        return out


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server: Router

    def log_message(self, format, *args):  # noqa: A002 -- the base signature
        pass  # One line per request comes from `note`, not from the base class.

    def note(self, model, server, status, started) -> None:
        stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
        line = (f"{stamp} {self.command} {self.path} model={model or '-'} "
                f"server={server} status={status} "
                f"seconds={time.monotonic() - started:.2f}")
        try:
            print(line, file=self.server.log, flush=True)
        except (OSError, ValueError):
            pass

    def do_GET(self):
        self.relay()

    def do_POST(self):
        self.relay()

    def do_DELETE(self):
        self.relay()

    def do_HEAD(self):
        self.relay()

    def do_PUT(self):
        self.relay()

    def send_body(self, status: int, data: bytes, ctype: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Connection", "close")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def relay(self) -> None:
        started = time.monotonic()
        self.close_connection = True
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        path = urllib.parse.urlsplit(self.path).path

        if self.command == "GET" and path in UNION_PATHS:
            joined = union(self.server.servers(), self.path)
            if joined is None:
                self.send_body(502, b'{"error":"no server answered"}',
                               "application/json")
                self.note(None, "all", 502, started)
                return
            self.send_body(200, json.dumps(joined).encode("utf-8"),
                           "application/json; charset=utf-8")
            self.note(None, "all", 200, started)
            return

        model = model_of(body)
        target = pick(model, self.server.routes, self.server.default)
        status = "error"
        try:
            upstream = connect(target)
        except OSError as exc:
            data = json.dumps({"error": f"router: {target}: {exc}"}).encode()
            self.send_body(502, data, "application/json")
            self.note(model, target, 502, started)
            return

        done, gone = threading.Event(), threading.Event()
        watcher = threading.Thread(
            target=watch_client, args=(self.connection, upstream, done, gone),
            daemon=True)
        try:
            headers = {k: v for k, v in self.headers.items()
                       if k.lower() not in HOP and k.lower() != "host"}
            headers["Connection"] = "close"
            upstream.putrequest(self.command, self.path, skip_host=False,
                                skip_accept_encoding=True)
            for key, value in headers.items():
                upstream.putheader(key, value)
            upstream.endheaders(body or None)
            watcher.start()
            resp = upstream.getresponse()
            status = resp.status
            self.send_response_only(resp.status, resp.reason)
            sized = resp.getheader("Content-Length") is not None
            for key, value in resp.getheaders():
                if key.lower() not in HOP:
                    self.send_header(key, value)
            if not sized and self.command != "HEAD":
                self.send_header("Transfer-Encoding", "chunked")
            self.send_header("Connection", "close")
            self.end_headers()
            if self.command == "HEAD":
                return
            while True:
                piece = resp.read1(CHUNK)
                if not piece:
                    break
                if sized:
                    self.wfile.write(piece)
                else:
                    self.wfile.write(b"%x\r\n%s\r\n" % (len(piece), piece))
            if not sized:
                self.wfile.write(b"0\r\n\r\n")
        except (OSError, http.client.HTTPException):
            # The client or the upstream closed. Either way the other side
            # closes too, so a cancelled prompt does not hold the card.
            if gone.is_set():
                status = "client-closed"
        finally:
            done.set()
            close_upstream(upstream)
            self.note(model, target, status, started)


def parse_route(text: str) -> tuple[str, str]:
    key, sep, url = text.partition("=")
    if not sep or not key or not url:
        raise argparse.ArgumentTypeError(f"--route wants KEY=URL, got {text!r}")
    return key, url


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--port", type=int, default=11436)
    ap.add_argument("--bind", default="127.0.0.1")
    ap.add_argument("--default", required=True,
                    help="the server for a model no route names")
    ap.add_argument("--route", type=parse_route, action="append", default=[],
                    metavar="KEY=URL", help="a model-name prefix and its server")
    args = ap.parse_args(argv)
    router = Router((args.bind, args.port), args.default, args.route)
    print(f"router on http://{args.bind}:{args.port}: default {router.default}, "
          f"routes {router.routes}", file=sys.stderr, flush=True)
    try:
        router.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        router.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
