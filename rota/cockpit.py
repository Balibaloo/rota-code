"""
The cockpit: a local server that makes the running system visible.

Two things it serves, from one origin so the viewer can fetch both:

  * the design graph (structure)   — what the system is wired to do
  * the live database (state)      — what it is actually doing

That combination is the point. The stories and the real traces render in the same
picture, so drift between design and implementation is visually obvious rather
than something you have to go looking for.

It also answers the question you will actually be asking when you glance at it:
**idle or stuck?** Quiescence is an empty frontier with no predicate firing;
stuck is a frontier that is not advancing. Those look alike in a log and are
plainly different here.

Run:  python -m rota.cockpit [project_root] [--port 8899]
"""
from __future__ import annotations

import json
import sqlite3
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from . import graph as graph_mod
from .boot import state_dir
from .db import connect
from .scheduler import (
    TICKS, is_quiescent, open_tips, predicate_wakes, tick_agenda,
)

HERE = Path(__file__).resolve().parent
VIEWER = HERE / "viewer.html"


def snapshot(conn: sqlite3.Connection) -> dict:
    """Everything the viewer needs, in one read."""
    tips = open_tips(conn)
    preds = predicate_wakes(conn, client_present=True)

    per_tick = {}
    for tick in TICKS:
        name = tick.__name__.replace("tick_", "")
        try:
            per_tick[name] = [str(w) for w in tick(conn)]
        except Exception as exc:
            per_tick[name] = [f"ERROR {exc}"]
    per_tick["agenda"] = [str(w) for w in tick_agenda(conn, client_present=True)]

    def rows(sql, *args):
        return [dict(r) for r in conn.execute(sql, args)]

    return {
        "quiescent": is_quiescent(conn, client_present=True),
        "frontier": {
            "tips": [{"role": w.role, "message": w.message_id, "verb": w.detail}
                     for w in tips],
            "predicates": [{"role": w.role, "kind": w.kind, "refs": list(w.refs),
                            "detail": w.detail} for w in preds],
        },
        "predicate_status": per_tick,
        "versions": rows("SELECT table_name, version FROM artefact_versions ORDER BY table_name"),
        "sessions": rows(
            "SELECT id, role, trigger_msg, mode, committed, model, prompt_hash "
            "FROM sessions ORDER BY seq DESC LIMIT 40"),
        "messages": rows(
            "SELECT id, from_role, to_role, verb, status, body_refs, cause_id, attempts "
            "FROM messages ORDER BY seq DESC LIMIT 60"),
        "receipts": rows(
            "SELECT r.session_id, s.role, r.table_name, r.row_id, r.new_version "
            "FROM receipts r LEFT JOIN sessions s ON s.id = r.session_id "
            "ORDER BY r.rowid DESC LIMIT 60"),
        "tool_calls": rows(
            "SELECT session_id, fn, args_summary, seq FROM tool_calls "
            "ORDER BY rowid DESC LIMIT 60"),
        "claims": rows("SELECT role, session_id, message_id FROM claims"),
        "checkpoints": rows("SELECT session_id, role, valid FROM checkpoints"),
        "ledger": rows(
            "SELECT id, about_ref, default_taken, status, author FROM ledger "
            "WHERE status='open'"),
        "batches": rows("SELECT id, item_id, status, priority, worktree FROM batches"),
        "items": rows(
            "SELECT id, kind, approval, approval_ver, version, substr(text,1,90) AS headline "
            "FROM items ORDER BY id"),
        "counts": {
            t: conn.execute(f"SELECT COUNT(*) n FROM {t}").fetchone()["n"]
            for t in ("utterances", "statements", "items", "glossary_terms",
                      "constraints", "tickets", "criteria", "batches", "tests",
                      "verdicts", "ledger", "decisions", "messages", "sessions")
        },
    }


def make_handler(db_path: Path):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, body: bytes, content_type: str) -> None:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):  # noqa: N802
            path = urlparse(self.path).path
            try:
                if path in ("/", "/index.html"):
                    self._send(VIEWER.read_bytes(), "text/html; charset=utf-8")
                elif path == "/graph.json":
                    self._send((graph_mod.DESIGN_DIR / "graph.json").read_bytes(),
                               "application/json")
                elif path == "/layout.json":
                    self._send((graph_mod.DESIGN_DIR / "layout.json").read_bytes(),
                               "application/json")
                elif path == "/stories.json":
                    self._send((graph_mod.DESIGN_DIR / "stories.json").read_bytes(),
                               "application/json")
                elif path == "/state.json":
                    conn = connect(db_path)
                    try:
                        body = json.dumps(snapshot(conn), default=str).encode("utf-8")
                    finally:
                        conn.close()
                    self._send(body, "application/json")
                else:
                    self.send_error(404)
            except FileNotFoundError:
                self.send_error(404)
            except Exception as exc:                       # pragma: no cover
                self.send_error(500, str(exc))

        def log_message(self, *args):                      # quiet
            pass

    return Handler


def serve(project_root: str | Path = ".", port: int = 8899, open_browser: bool = True):
    db_path = state_dir(project_root) / "rota.db"
    if not db_path.exists():
        raise SystemExit(f"no rota database at {db_path}; boot the project first")

    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(db_path))
    url = f"http://127.0.0.1:{port}/"
    print(f"cockpit: {url}  (db: {db_path})")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("project_root", nargs="?", default=".")
    ap.add_argument("--port", type=int, default=8899)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()
    serve(args.project_root, args.port, not args.no_browser)
