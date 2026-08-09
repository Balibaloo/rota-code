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

from . import paths
from urllib.parse import parse_qs, urlparse

from . import graph as graph_mod, prompts as prompts_mod
from .boot import state_dir
from .coverage import render as render_coverage, report as coverage_report
from .db import connect, init_db
from . import inspect_api
from .sandbox import build as build_sandbox
from .traceview import (
    coverage_edges, frontier_overlay, steps_from_db,
)
from .scheduler import (
    TICKS, is_quiescent, open_tips, predicate_wakes, tick_agenda,
)

HERE = paths.PACKAGE
VIEWER = paths.VIEWER
STATIC = paths.STATIC


def snapshot(conn: sqlite3.Connection) -> dict:
    """Everything the viewer needs, in one read."""
    tips = open_tips(conn)
    preds = predicate_wakes(conn, principal_present=True)

    per_tick = {}
    for tick in TICKS:
        name = tick.__name__.replace("tick_", "")
        try:
            per_tick[name] = [str(w) for w in tick(conn)]
        except Exception as exc:
            per_tick[name] = [f"ERROR {exc}"]
    per_tick["agenda"] = [str(w) for w in tick_agenda(conn, principal_present=True)]

    def rows(sql, *args):
        return [dict(r) for r in conn.execute(sql, args)]

    return {
        "quiescent": is_quiescent(conn, principal_present=True),
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
        # Priority comes from the item now, so this joins rather than selecting a
        # column that no longer exists. The old query was still here because the
        # database it was reading predated the move.
        "batches": rows(
            "SELECT b.id AS id, b.item_id AS item_id, b.status AS status, "
            "       i.priority AS priority, b.worktree AS worktree "
            "FROM batches b JOIN items i ON i.id = b.item_id "
            "ORDER BY i.priority DESC, b.id"),
        "items": rows(
            "SELECT id, kind, approval, approval_ver, version, substr(text,1,90) AS headline "
            "FROM items ORDER BY id"),
        "counts": {
            t: conn.execute(f"SELECT COUNT(*) n FROM {t}").fetchone()["n"]
            for t in ("entries", "statements", "items", "glossary_terms",
                      "constraints", "tickets", "criteria", "batches", "tests",
                      "verdicts", "ledger", "decisions", "messages", "sessions")
        },
    }


def prompt_bundle(db_path: Path) -> dict:
    """
    What each role is actually told, assembled the way a session assembles it.

    Base plus every mode piece, plus the tool signatures the runner advertises —
    because the prompt a role receives is not the markdown file, it is the
    composition, and the composition is what you need to read when a role
    misbehaves. Rendering it anywhere but here would be a second implementation
    that could disagree with the first.
    """
    g = graph_mod.load()
    conn = connect(db_path)
    try:
        out = {}
        for role in sorted(g.roles):
            sb = build_sandbox(role, conn, g=g)
            modes = {}
            for mode in prompts_mod.available(role):
                modes[mode] = {
                    "piece": prompts_mod.piece(role, mode),
                    "composed_chars": len(prompts_mod.compose(role, mode)),
                }
            out[role] = {
                "base": prompts_mod.base(role),
                "modes": modes,
                "inbound_verbs": sorted(prompts_mod.inbound_verbs(role)),
                "signatures": sb.signatures(),
                "namespace_size": len(sb.functions()),
            }
        return out
    finally:
        conn.close()


def source_fingerprint() -> str:
    """Cheap change detector for hot reload: mtimes of everything that shapes a
    prompt or the wiring."""
    import hashlib

    h = hashlib.sha256()
    roots = [paths.PROMPTS, paths.DESIGN, paths.PACKAGE]
    for root in roots:
        if not root.exists():
            continue
        for f in sorted(root.rglob("*")):
            if f.is_file() and f.suffix in (".md", ".json", ".py", ".html"):
                h.update(f"{f}:{f.stat().st_mtime_ns}".encode())
    return h.hexdigest()[:16]


def schema_drift(db_path: Path) -> list[str]:
    """
    Tables and columns `schema.sql` declares that the file does not have.

    Read off the DDL rather than a hand-kept list, so it cannot fall behind the
    thing it is checking — which is the failure it exists to catch.
    """
    import re

    from .db import SCHEMA_PATH

    ddl = SCHEMA_PATH.read_text(encoding="utf-8")
    declared: dict[str, set[str]] = {}
    for block in re.finditer(
            r"CREATE TABLE IF NOT EXISTS (\w+)\s*\((.*?)\n\);", ddl, re.S):
        table, body = block.group(1), block.group(2)
        cols = set()
        for line in body.splitlines():
            line = line.strip()
            m = re.match(r"(\w+)\s+(TEXT|INTEGER|REAL|BLOB)", line)
            if m:
                cols.add(m.group(1))
        declared[table] = cols

    problems = []
    conn = connect(db_path)
    try:
        have = {r["name"] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        for table, cols in sorted(declared.items()):
            if table not in have:
                problems.append(f"missing table {table}")
                continue
            actual = {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
            for missing in sorted(cols - actual):
                problems.append(f"{table} has no column {missing}")
    finally:
        conn.close()
    return problems


def make_handler(db_path: Path):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, body: bytes, content_type: str) -> None:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):  # noqa: N802
            parsed = urlparse(self.path)
            path = parsed.path
            q = parse_qs(parsed.query)
            try:
                if path in ("/", "/index.html"):
                    # Read from disk every request: editing the viewer and hitting
                    # refresh should show the edit, not a cached copy.
                    self._send(VIEWER.read_bytes(), "text/html; charset=utf-8")
                elif path == "/graph.json":
                    graph_mod.load.cache_clear()      # hot reload: re-read on request
                    self._send((graph_mod.DESIGN_DIR / "graph.json").read_bytes(),
                               "application/json")
                elif path == "/layout.json":
                    self._send((graph_mod.DESIGN_DIR / "layout.json").read_bytes(),
                               "application/json")
                elif path == "/stories.json":
                    self._send((graph_mod.DESIGN_DIR / "stories.json").read_bytes(),
                               "application/json")
                elif path.endswith(".js"):
                    self._send((STATIC / Path(path).name).read_bytes(),
                               "application/javascript; charset=utf-8")
                elif path in ("/artefact.json", "/role.json", "/edge.json",
                              "/blast.json"):
                    conn = connect(db_path)
                    try:
                        if path == "/artefact.json":
                            data = inspect_api.artefact(conn, q.get("id", [""])[0])
                        elif path == "/role.json":
                            data = inspect_api.role(conn, q.get("id", [""])[0])
                        elif path == "/blast.json":
                            data = inspect_api.blast_radius(q.get("id", [""])[0])
                        else:
                            data = inspect_api.edge(
                                conn, q.get("s", [""])[0], q.get("t", [""])[0],
                                q.get("type", ["reads"])[0])
                    finally:
                        conn.close()
                    self._send(json.dumps(data, default=str).encode("utf-8"),
                               "application/json")
                elif path == "/messages.json":
                    conn = connect(db_path)
                    try:
                        body = json.dumps(inspect_api.message_graph(conn),
                                          default=str).encode("utf-8")
                    finally:
                        conn.close()
                    self._send(body, "application/json")
                elif path == "/trace.json":
                    conn = connect(db_path)
                    try:
                        body = json.dumps({
                            "steps": steps_from_db(conn),
                            "overlay": frontier_overlay(conn),
                            "coverage": coverage_edges(),
                        }, default=str).encode("utf-8")
                    finally:
                        conn.close()
                    self._send(body, "application/json")
                elif path == "/prompts.json":
                    body = json.dumps(prompt_bundle(db_path), default=str).encode("utf-8")
                    self._send(body, "application/json")
                elif path == "/coverage.json":
                    rep = coverage_report()
                    body = json.dumps({
                        "percent": rep.percent,
                        "covered": len(rep.covered),
                        "total": rep.total,
                        "by_role": {r: list(v) for r, v in rep.by_role().items()},
                        "missing": [str(k) for k in sorted(rep.missing, key=str)],
                    }).encode("utf-8")
                    self._send(body, "application/json")
                elif path == "/fingerprint":
                    self._send(source_fingerprint().encode("utf-8"), "text/plain")
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

        def do_POST(self):  # noqa: N802
            """Persist a dragged layout. Positions are a viewer concern, kept out
            of graph.json so editing what the graph *means* never touches
            geometry — and out of git's way for the same reason."""
            if urlparse(self.path).path != "/layout.json":
                self.send_error(404)
                return
            length = int(self.headers.get("Content-Length", 0))
            payload = self.rfile.read(length).decode("utf-8")
            try:
                json.loads(payload)
            except json.JSONDecodeError as exc:
                self.send_error(400, str(exc))
                return
            (graph_mod.DESIGN_DIR / "layout.json").write_text(payload, encoding="utf-8")
            self._send(b'{"ok":true}', "application/json")

        def log_message(self, *args):                      # quiet
            pass

    return Handler


def serve(project_root: str | Path = ".", port: int = 8899, open_browser: bool = True):
    db_path = state_dir(project_root) / "rota.db"
    if not db_path.exists():
        raise SystemExit(f"no rota database at {db_path}; boot the project first")

    # Bring the file up to the current schema, and refuse to serve it if that
    # was not enough.
    #
    # `CREATE TABLE IF NOT EXISTS` adds missing *tables* and cannot add a
    # missing *column*, so a database written before `items.priority` moved
    # looks fine until one panel returns a 500 — which the viewer renders as an
    # empty box that reads like "no rows yet". Saying so plainly is worth more
    # than serving eight panels and lying about the ninth.
    #
    # It sits in `serve` rather than the request path on purpose: a *viewer*
    # that migrates per request is a viewer with side effects, and the one thing
    # this tool must never do is change what it is showing you.
    init_db(db_path).close()
    drift = schema_drift(db_path)
    if drift:
        raise SystemExit(
            f"{db_path} is behind schema.sql:\n" +
            "\n".join(f"  {d}" for d in drift) +
            "\n\nDatabases here are throwaway — every one is built by init_db at "
            "boot. Move it aside and it will be rebuilt:\n"
            f"  mv {db_path} {db_path}.old")

    # Deliberately NOT allow_reuse_address. On Windows SO_REUSEADDR permits a
    # second process to bind a port that is already *actively listening* — not
    # merely in TIME_WAIT — so setting it stacks servers silently and the oldest
    # one keeps answering. A restart then appears to succeed while serving stale
    # code, which is a worse failure than a refused bind.
    ThreadingHTTPServer.daemon_threads = True
    try:
        server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(db_path))
    except OSError as exc:
        raise SystemExit(
            f"port {port} is in use ({exc}). Stop the other cockpit, or pass "
            f"--port. Refusing to stack a second server on it.") from exc
    url = f"http://127.0.0.1:{port}/"
    print(f"cockpit: {url}  (db: {db_path})")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


def serve_reloading(project_root: str | Path, port: int, open_browser: bool):
    """
    Restart the server when Python changes, the way the page already reloads
    when prompts or the graph change.

    The page had hot reload from the start and the *server* did not, so every
    backend edit meant killing a process, picking a new port because the old one
    had not released, and losing the browser state. Half a reload loop is worse
    than none: it teaches you to distrust what you are looking at.
    """
    from watchfiles import run_process

    watch = [paths.PACKAGE]
    print(f"watching {watch[0]} for changes")
    run_process(*watch, target=serve, args=(project_root, port, open_browser),
                callback=lambda changes: print(
                    f"reload: {', '.join(sorted(Path(c[1]).name for c in changes))}"))


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("project_root", nargs="?", default=".")
    ap.add_argument("--port", type=int, default=8899)
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--no-reload", action="store_true",
                    help="do not restart on source changes")
    args = ap.parse_args()
    runner = serve if args.no_reload else serve_reloading
    runner(args.project_root, args.port, not args.no_browser)
