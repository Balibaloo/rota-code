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

Run:  python -m rota.cockpit.server [project_root] [--port 8899]
"""
from __future__ import annotations

import json
import re
import sqlite3
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .. import paths
from urllib.parse import parse_qs, urlparse

from ..design import graph as graph_mod
from ..roles import prompts as prompts_mod
from ..core.boot import state_dir
from ..testkit.coverage import render as render_coverage, report as coverage_report
from ..core.db import connect, connect_readonly, init_db
from . import inspect_api, progress
from ..core.sandbox import build as build_sandbox
from .traceview import (
    coverage_edges, frontier_overlay, steps_from_db,
)
from ..core.predicates import REGISTRY
from ..core.scheduler import (
    TICKS, is_quiescent_readonly, open_tips, predicate_wakes, tick_agenda,
)

HERE = paths.PACKAGE
VIEWER = paths.VIEWER
STATIC = paths.STATIC

# Layouts. `layout.json` is the main arrangement and keeps its name and place —
# every reader of it predates the idea of there being more than one. The rest
# live beside it as `layouts/<name>.json`, one file per arrangement, because a
# layout is saved and deleted whole and never merged.
LAYOUT_FILE = graph_mod.DESIGN_DIR / "layout.json"
LAYOUTS_DIR = graph_mod.DESIGN_DIR / "layouts"

# A layout name becomes a filename, so it is a filename-shaped token or it is
# refused. Anything looser is a path traversal spelled politely.
LAYOUT_NAME = re.compile(r"[A-Za-z0-9_-]{1,40}")


def layout_path(name: str) -> Path:
    if name in ("", "main"):
        return LAYOUT_FILE
    if not LAYOUT_NAME.fullmatch(name):
        raise ValueError(f"not a layout name: {name!r}")
    return LAYOUTS_DIR / f"{name}.json"


def is_layout_file(p: Path) -> bool:
    """Viewer geometry, not source. Saving a layout must not read as 'the
    sources changed': the fingerprint would reload the page that just saved it,
    and the watcher would restart the server under it — which is exactly what
    happened, on every save, for as long as both watched everything."""
    return p == LAYOUT_FILE or LAYOUTS_DIR in p.parents


def snapshot(conn: sqlite3.Connection) -> dict:
    """Everything the viewer needs, in one read."""
    tips = open_tips(conn)
    preds = predicate_wakes(conn, principal_present=True)

    # Structured, not stringified: a firing predicate's `refs` name the exact
    # rows that tripped it, which is the difference between "term_collision is
    # firing" and "term_collision is firing about `context`". Flattening to
    # str(w) threw that away at the door.
    def wake_row(w) -> dict:
        return {"role": w.role, "refs": list(w.refs), "detail": w.detail}

    per_tick = {}
    for tick in TICKS:
        name = tick.__name__.replace("tick_", "")
        try:
            per_tick[name] = [wake_row(w) for w in tick(conn)]
        except Exception as exc:
            per_tick[name] = [{"role": f"ERROR {exc}", "refs": [], "detail": ""}]
    per_tick["agenda"] = [wake_row(w)
                         for w in tick_agenda(conn, principal_present=True)]

    def rows(sql, *args):
        return [dict(r) for r in conn.execute(sql, args)]

    return {
        "quiescent": is_quiescent_readonly(conn, principal_present=True),
        "frontier": {
            "tips": [{"role": w.role, "message": w.message_id, "verb": w.detail}
                     for w in tips],
            "predicates": [{"role": w.role, "kind": w.kind, "refs": list(w.refs),
                            "detail": w.detail} for w in preds],
        },
        "predicate_status": per_tick,
        # What each predicate is *for*, straight off the registry — the same
        # docstring the decorator captured, never a second copy in the viewer
        # that could drift from the function it describes. First paragraph
        # only: the rest is implementation talk.
        "predicate_meta": {
            name: {"why": " ".join((p.why or "").split("\n\n")[0].split()),
                   "wakes": p.wakes, "band": p.band}
            for name, p in REGISTRY.items()
        },
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
    conn = connect_readonly(db_path)
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
            if (f.is_file() and f.suffix in (".md", ".json", ".py", ".html")
                    and not is_layout_file(f)):
                h.update(f"{f}:{f.stat().st_mtime_ns}".encode())
    return h.hexdigest()[:16]


def schema_drift(db_path: Path) -> list[str]:
    """
    Tables and columns `schema.sql` declares that the file does not have.

    Read off the DDL rather than a hand-kept list, so it cannot fall behind the
    thing it is checking — which is the failure it exists to catch.
    """
    import re

    from ..core.db import SCHEMA_PATH

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
    conn = connect_readonly(db_path)
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
    # One mutable slot, because the handler serves *a* run, not *the* run:
    # POST /run swaps which database every later request reads, so the viewer
    # can move between sibling runs without a restart. Everything below reads
    # `state["db"]` at request time and nothing caches a connection.
    state = {"db": Path(db_path)}

    class Handler(BaseHTTPRequestHandler):
        def _send(self, body: bytes, content_type: str) -> None:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            # Never cache. This is a development cockpit whose whole job is to
            # show the current state of a thing being changed, and everything it
            # serves is either live data or a file that was edited a minute ago.
            #
            # Without this the browser kept a copy of `graphview.js` from a few
            # minutes earlier, which happened to be a version that threw at load
            # -- so the canvas went white and stayed white through reloads while
            # the file on disk was fine. Fifteen minutes to find a stale cache.
            self.send_header("Cache-Control", "no-store, must-revalidate")
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
                    self._send(layout_path(q.get("name", [""])[0]).read_bytes(),
                               "application/json")
                elif path == "/layouts.json":
                    names = ["main"] + (sorted(p.stem for p in
                                               LAYOUTS_DIR.glob("*.json"))
                                        if LAYOUTS_DIR.is_dir() else [])
                    self._send(json.dumps({"names": names}).encode("utf-8"),
                               "application/json")
                elif path == "/runs.json":
                    # The siblings of the run being served, newest first. The
                    # mtime is the one wall-clock fact the system has about a
                    # run — the rows themselves carry order, not time, by law.
                    here = state["db"].parent
                    runs = sorted((p for p in here.glob("*.db")),
                                  key=lambda p: p.stat().st_mtime, reverse=True)
                    body = json.dumps({"runs": [
                        {"name": p.stem, "mtime": p.stat().st_mtime,
                         "current": p.resolve() == state["db"].resolve()}
                        for p in runs]}).encode("utf-8")
                    self._send(body, "application/json")
                elif path == "/stories.json":
                    self._send((graph_mod.DESIGN_DIR / "stories.json").read_bytes(),
                               "application/json")
                elif path.endswith(".js"):
                    self._send((STATIC / Path(path).name).read_bytes(),
                               "application/javascript; charset=utf-8")
                elif path in ("/artefact.json", "/role.json", "/edge.json",
                              "/blast.json", "/session.json"):
                    conn = connect_readonly(state["db"])
                    try:
                        if path == "/artefact.json":
                            data = inspect_api.artefact(conn, q.get("id", [""])[0])
                        elif path == "/role.json":
                            data = inspect_api.role(conn, q.get("id", [""])[0])
                        elif path == "/session.json":
                            data = inspect_api.session(conn, q.get("id", [""])[0])
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
                elif path == "/provenance.json":
                    conn = connect_readonly(state["db"])
                    try:
                        body = json.dumps(inspect_api.provenance(
                            conn, q.get("table", [""])[0],
                            q.get("row", [""])[0]), default=str).encode("utf-8")
                    finally:
                        conn.close()
                    self._send(body, "application/json")
                elif path == "/messages.json":
                    conn = connect_readonly(state["db"])
                    try:
                        body = json.dumps(inspect_api.message_graph(conn),
                                          default=str).encode("utf-8")
                    finally:
                        conn.close()
                    self._send(body, "application/json")
                elif path == "/trace.json":
                    conn = connect_readonly(state["db"])
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
                    body = json.dumps(prompt_bundle(state["db"]), default=str).encode("utf-8")
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
                elif path == "/message.json":
                    body = json.dumps(
                        progress.message_text(q.get("id", [""])[0]),
                        default=str).encode("utf-8")
                    self._send(body, "application/json")
                elif path == "/cases.json":
                    body = json.dumps(progress.cases(),
                                      default=str).encode("utf-8")
                    self._send(body, "application/json")
                elif path == "/progress.json":
                    conn = connect_readonly(state["db"])
                    try:
                        body = json.dumps(progress.report(conn),
                                          default=str).encode("utf-8")
                    finally:
                        conn.close()
                    self._send(body, "application/json")
                elif path == "/fingerprint":
                    self._send(source_fingerprint().encode("utf-8"), "text/plain")
                elif path == "/state.json":
                    conn = connect_readonly(state["db"])
                    try:
                        snap = snapshot(conn)
                    finally:
                        conn.close()
                    # How long the run has been still, measured where it
                    # cannot be lost: the file. WAL carries every write, so
                    # the newer of db and -wal is the last time anything was
                    # recorded — it survives page reloads and server restarts,
                    # which the viewer's old poll counter did not. `-shm` is
                    # deliberately excluded: readers touch it, and a stillness
                    # clock the cockpit's own polling resets measures nothing.
                    stamps = [p.stat().st_mtime for p in
                              (state["db"], Path(str(state["db"]) + "-wal"))
                              if p.exists()]
                    snap["quiet_secs"] = (max(0.0, time.time() - max(stamps))
                                          if stamps else None)
                    self._send(json.dumps(snap, default=str).encode("utf-8"),
                               "application/json")
                else:
                    self.send_error(404)
            except FileNotFoundError:
                self.send_error(404)
            except ValueError as exc:
                self.send_error(400, str(exc))
            except Exception as exc:                       # pragma: no cover
                self.send_error(500, str(exc))

        def do_POST(self):  # noqa: N802
            """Persist or delete a layout, or switch which run is served.
            Positions are a viewer concern, kept out of graph.json so editing
            what the graph *means* never touches geometry. `?name=` picks
            which arrangement; none means main."""
            parsed = urlparse(self.path)
            if parsed.path == "/run":
                self._switch_run(parse_qs(parsed.query))
                return
            if parsed.path != "/layout.json":
                self.send_error(404)
                return
            q = parse_qs(parsed.query)
            name = q.get("name", [""])[0]
            try:
                target = layout_path(name)
            except ValueError as exc:
                self.send_error(400, str(exc))
                return
            if q.get("delete"):
                # Main is the one arrangement every fallback lands on; a
                # cockpit with no main is a cockpit that opens onto strays.
                if target == LAYOUT_FILE:
                    self.send_error(400, "main cannot be deleted")
                    return
                try:
                    target.unlink()
                except FileNotFoundError:
                    self.send_error(404)
                    return
                self._send(b'{"ok":true}', "application/json")
                return
            length = int(self.headers.get("Content-Length", 0))
            payload = self.rfile.read(length).decode("utf-8")
            try:
                json.loads(payload)
            except json.JSONDecodeError as exc:
                self.send_error(400, str(exc))
                return
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(payload, encoding="utf-8")
            self._send(b'{"ok":true}', "application/json")

        def _switch_run(self, q) -> None:
            """Point every later request at a sibling run.

            Same gate as the way in: bring the file up to schema, refuse it if
            that was not enough — a viewer that switches to a database it then
            renders as nine empty boxes has answered "switch" with a lie. The
            name is confined to siblings of the current run; a path here would
            be the layout traversal problem with a second spelling.
            """
            name = q.get("name", [""])[0]
            if not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", name) or ".." in name:
                self.send_error(400, f"not a run name: {name!r}")
                return
            target = state["db"].parent / f"{name}.db"
            if not target.exists():
                self.send_error(404, f"no run named {name}")
                return
            # Same write-only-when-needed gate as `prepare_db`: switching to a
            # run must not stamp it as freshly written.
            drift = schema_drift(target)
            if drift:
                init_db(target).close()
                drift = schema_drift(target)
            if drift:
                self.send_error(409, "behind schema: " + "; ".join(drift[:4]))
                return
            state["db"] = target
            self._send(b'{"ok":true}', "application/json")

        def log_message(self, *args):                      # quiet
            pass

    return Handler


def prepare_db(project_root: str | Path | None = None,
               db: str | Path | None = None) -> Path:
    """
    The file this cockpit will show, brought up to schema or refused.

    Two ways in, and they are not the same question.

    A **project root** may legitimately have no run yet, so a missing database
    there is booted: boot is idempotent, and making somebody resolve "no
    database" by hand at a viewer is friction for nothing.

    A **named file** may not. It was typed, or resolved from a run name, and if
    it is not there the answer is that you asked for the wrong one — booting a
    fresh database in its place answers a different question with the same
    confidence, and what it renders as is a system that ran and produced
    nothing. Every foreign-repo run so far went to a name the cockpit had no way
    to open, so this is not a hypothetical: the wrong half of this branch is the
    one that was reachable.
    """
    if db is not None:
        db_path = Path(db)
        if not db_path.exists():
            raise SystemExit(
                f"no database at {db_path}. A cockpit shows a run; it does not "
                f"create one.\n  rota ls           what runs exist\n"
                f"  rota onboard <name> --root <checkout>")
    else:
        # No run named: serve the newest one *that will open*. The person
        # opening a cockpit without naming a run means "the run I was just
        # working on", and mtime is the one honest signal of that — but the
        # newest file can be behind schema.sql while parallel work moves the
        # schema, and refusing outright makes "just open the cockpit" fail
        # on exactly the busiest days. Skipped runs are named, so a wrong
        # guess is loud, and the in-page selector is the two-click correction.
        sdir = state_dir(project_root or ".")
        siblings = sorted(sdir.glob("*.db"),
                          key=lambda p: p.stat().st_mtime, reverse=True) \
            if sdir.is_dir() else []
        db_path = None
        for cand in siblings:
            try:
                drift = schema_drift(cand)
            except sqlite3.Error as exc:
                print(f"skipping {cand.stem}: {exc}")
                continue
            # Missing *tables* are what init_db adds at the gate below;
            # missing columns are not, and that candidate would only be
            # refused after the fact.
            if not drift or all(d.startswith("missing table ") for d in drift):
                db_path = cand
                break
            print(f"skipping {cand.stem}: {drift[0]}"
                  + (f" (+{len(drift) - 1} more)" if len(drift) > 1 else ""))
        if db_path is not None:
            print(f"serving the latest openable run: {db_path.stem}"
                  f" (the selector in the page switches)")
        elif siblings:
            db_path = siblings[0]      # refused below, with the full story
        else:
            db_path = sdir / "rota.db"
            # Boot rather than refuse. This is a viewer; "no database" is not a
            # condition it should make somebody resolve by hand, and boot is
            # idempotent — it reconciles what is there and creates what is not.
            from ..core.boot import boot as boot_project

            print(f"no database at {db_path}; booting")
            conn, _ = boot_project(project_root or ".")
            conn.close()

    # Bring the file up to the current schema, and refuse to serve it if that
    # was not enough.
    #
    # `CREATE TABLE IF NOT EXISTS` adds missing *tables* and cannot add a
    # missing *column*, so a database written before `items.priority` moved
    # looks fine until one panel returns a 500 — which the viewer renders as an
    # empty box that reads like "no rows yet". Saying so plainly is worth more
    # than serving eight panels and lying about the ninth.
    #
    # It sits on the way in rather than in the request path on purpose: a
    # *viewer* that migrates per request is a viewer with side effects, and the
    # one thing this tool must never do is change what it is showing you.
    # Up to schema — but only opening a write connection when the read-only
    # check says something is actually missing. `init_db` on a healthy file
    # refreshes the WAL's mtime, and that mtime is now the stillness clock
    # `/state.json` serves: a viewer that touches the thing it measures reads
    # its own restart as activity, and the watcher restarts on every source
    # edit.
    drift = schema_drift(db_path)
    if drift:
        init_db(db_path).close()
        drift = schema_drift(db_path)
    if drift:
        raise SystemExit(
            f"{db_path} is behind schema.sql:\n" +
            "\n".join(f"  {d}" for d in drift) +
            "\n\nDatabases here are throwaway — every one is built by init_db at "
            "boot. Move it aside and it will be rebuilt:\n"
            f"  mv {db_path} {db_path}.old")
    return db_path


def serve(project_root: str | Path | None = None, port: int = 8899,
          open_browser: bool = False, db: str | Path | None = None):
    db_path = prepare_db(project_root, db)

    # Deliberately NOT allow_reuse_address. On Windows SO_REUSEADDR permits a
    # second process to bind a port that is already *actively listening* — not
    # merely in TIME_WAIT — so setting it stacks servers silently and the oldest
    # one keeps answering. A restart then appears to succeed while serving stale
    # code, which is a worse failure than a refused bind.
    #
    # **And it was never switched off.** `socketserver.TCPServer` defaults it to
    # False, but `http.server.HTTPServer` overrides it to True, and this
    # inherits from that — so the paragraph above described an intention and the
    # flag was on the whole time. The failure it predicts is not hypothetical: I
    # hit it adding an endpoint. Two servers listened on 8899, the older one
    # answered, and the new route came back 404 from a process that had never
    # heard of it. A comment is not a setting.
    ThreadingHTTPServer.allow_reuse_address = False
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


def serve_reloading(project_root: str | Path | None = None, port: int = 8899,
                    open_browser: bool = False, db: str | Path | None = None):
    """
    Restart the server when Python changes, the way the page already reloads
    when prompts or the graph change.

    The page had hot reload from the start and the *server* did not, so every
    backend edit meant killing a process, picking a new port because the old one
    had not released, and losing the browser state. Half a reload loop is worse
    than none: it teaches you to distrust what you are looking at.
    """
    from watchfiles import run_process

    # Resolve before the watcher starts. A refusal raised inside `run_process`
    # is raised in a child it owns and re-raised on every restart, so a mistyped
    # run name would scroll past as a repeating traceback rather than be said
    # once, here, by the process you are looking at. Idempotent either way.
    prepare_db(project_root, db)

    # **A reload never opens a browser.** `run_process` re-invokes the target in
    # a fresh process on every change, so any argument saying "open one" is true
    # again each time — a new tab per backend edit, which across an afternoon is
    # most of a browser. The first attempt at this computed the flag once in the
    # parent and passed it down, which is the same bug with more steps: the
    # value is fixed at startup and every restart reuses it.
    #
    # There is nothing to preserve by reopening. The page reloads itself on the
    # fingerprint change and remembers which view and panel it was on.
    if open_browser:
        webbrowser.open(f"http://127.0.0.1:{port}/")

    # The parent says where it is, because the child's `serve` says it into a
    # subprocess `run_process` owns and nobody sees. The reloading path is the
    # default, so the usual way to start the cockpit was the one that never
    # told you the port -- and it is the one you need on the first run, before
    # you have a tab open to remember it for you.
    print(f"cockpit: http://127.0.0.1:{port}/", flush=True)

    watch = [paths.PACKAGE]
    print(f"watching {watch[0]} for changes")
    # Layout saves come *from* the viewer this server is serving. Restarting on
    # them turned every "save layout" into a dead server under a live page —
    # the same write also has to stay out of `source_fingerprint`, or the page
    # reloads itself a second after saving.
    run_process(*watch, target=serve,
                watch_filter=lambda change, p: not is_layout_file(Path(p)),
                kwargs={"project_root": project_root, "port": port,
                        "open_browser": False, "db": db},
                callback=lambda changes: print(
                    f"reload: {', '.join(sorted(Path(c[1]).name for c in changes))}"))


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("project_root", nargs="?", default=".")
    ap.add_argument("--port", type=int, default=8899)
    # Opt in rather than out. A dev server that grabs focus every time somebody
    # starts it is a dev server people stop restarting.
    ap.add_argument("--open", action="store_true",
                    help="open a browser tab (otherwise just print the URL)")
    ap.add_argument("--no-reload", action="store_true",
                    help="do not restart on source changes")
    ap.add_argument("--db", help="a run database, instead of deriving one from "
                                 "a project root. `rota cockpit <name>` is the "
                                 "same thing with the name resolved for you")
    args = ap.parse_args()
    runner = serve if args.no_reload else serve_reloading
    runner(project_root=args.project_root, port=args.port,
           open_browser=args.open, db=args.db)
