"""
Traces in the stories' shape.

`team-graph.html` steps through authored stories: each step is a title, some
narration, and a set of edges to light up. That data structure turns out to be
exactly what a *real* run produces too — a session reads some artefacts, writes
some, sends some messages, and that is an edge set.

So both feed one renderer, and the payoff is the thing this viewer was for:
**the design's stories and the system's actual behaviour render in the same
picture.** A story that fires an edge the implementation never touches, or a run
that lights an edge no story anticipated, is visible rather than argued about.

Step shape (shared with `design/stories.json`):

    {title, round, text, edges: [[source, target, kind, verb], ...]}
"""
from __future__ import annotations

import json
import sqlite3
from typing import Any

from ..core.db import ARTEFACT_OF_TABLE


def steps_from_db(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """
    Every committed session, in order, as a step.

    Reads come from the tool-call log, writes from receipts, messages from the
    message log — the same three sources edge coverage uses, because they are the
    evidence a session actually leaves rather than a parallel record that could
    disagree with it.
    """
    steps: list[dict[str, Any]] = []

    sessions = [dict(r) for r in conn.execute(
        "SELECT id, role, trigger_msg, mode, seq, model FROM sessions "
        "WHERE committed = 1 ORDER BY seq")]

    for s in sessions:
        edges: list[list[str]] = []
        seen: set[tuple] = set()

        def add(src, dst, kind, verb):
            key = (src, dst, kind, verb)
            if key not in seen:
                seen.add(key)
                edges.append([src, dst, kind, verb])

        for call in conn.execute(
            "SELECT fn FROM tool_calls WHERE session_id = ? ORDER BY seq", (s["id"],)
        ):
            fn = call["fn"]
            if "." not in fn or fn.startswith("msg."):
                continue
            artefact, verb = fn.split(".", 1)
            add(s["role"], artefact, "reads", verb.replace("_", " "))

        for r in conn.execute(
            "SELECT DISTINCT table_name FROM receipts WHERE session_id = ?", (s["id"],)
        ):
            artefact = ARTEFACT_OF_TABLE.get(r["table_name"])
            if artefact:
                # A write supersedes a read of the same artefact in the picture:
                # the stronger relationship is the one worth seeing.
                edges[:] = [e for e in edges
                            if not (e[0] == s["role"] and e[1] == artefact
                                    and e[2] == "reads")]
                add(s["role"], artefact, "writes", "")

        trigger = None
        if s["trigger_msg"]:
            trigger = conn.execute(
                "SELECT from_role, to_role, verb FROM messages WHERE id = ?",
                (s["trigger_msg"],)).fetchone()
            if trigger:
                add(trigger["from_role"], trigger["to_role"], "messages",
                    trigger["verb"])

        for m in conn.execute(
            "SELECT to_role, verb FROM messages WHERE from_role = ? AND cause_id = ?",
            (s["role"], s["trigger_msg"])
        ):
            add(s["role"], m["to_role"], "messages", m["verb"])

        woke_by = (f"{trigger['verb']} from {trigger['from_role']}"
                   if trigger else "a predicate")
        steps.append({
            "title": f"{s['role']} — {woke_by}",
            "round": s["mode"],
            "text": _narrate(conn, s, edges),
            "edges": edges,
            "session": s["id"],
        })

    return steps


def _narrate(conn: sqlite3.Connection, session: dict, edges: list) -> str:
    """Plain description of what the session did. Facts, not prose."""
    writes = [e[1] for e in edges if e[2] == "writes"]
    reads = [e[1] for e in edges if e[2] == "reads"]
    sent = [f"{e[3]} → {e[1]}" for e in edges
            if e[2] == "messages" and e[0] == session["role"]]

    parts = []
    if reads:
        parts.append(f"read {', '.join(sorted(set(reads)))}")
    if writes:
        rows = conn.execute(
            "SELECT COUNT(*) n FROM receipts WHERE session_id = ?",
            (session["id"],)).fetchone()["n"]
        parts.append(f"wrote {rows} row(s) to {', '.join(sorted(set(writes)))}")
    if sent:
        parts.append(f"sent {', '.join(sent)}")
    if not parts:
        parts.append("committed without changing anything")

    pin = f" [{session['model']}]" if session.get("model") else ""
    return "; ".join(parts).capitalize() + "." + pin


def steps_from_trace(trace) -> list[dict[str, Any]]:
    """A live `loop.Trace`, for watching a run as it happens."""
    steps = []
    for i, s in enumerate(trace.steps, 1):
        if s.quiescent:
            steps.append({"title": f"{i}. quiescent", "round": "idle",
                          "text": s.note, "edges": []})
            continue
        edges = []
        if s.wake and s.wake.message_id:
            edges.append(["principal", s.wake.role, "messages", s.wake.detail])
        steps.append({
            "title": f"{i}. {s.wake}" if s.wake else f"{i}.",
            "round": "run",
            "text": s.note or ("ok" if s.outcome and s.outcome.committed else "failed"),
            "edges": edges,
        })
    return steps


def coverage_edges() -> dict[str, list[list[str]]]:
    """Covered and uncovered edges, for painting the graph."""
    from ..testkit.coverage import report

    rep = report()
    return {
        "covered": [[k.role, k.target, k.kind, k.verb] for k in sorted(rep.covered, key=str)],
        "missing": [[k.role, k.target, k.kind, k.verb] for k in sorted(rep.missing, key=str)],
    }


def frontier_overlay(conn: sqlite3.Connection) -> dict[str, Any]:
    """Who is about to move, and who is mid-session."""
    from ..core.scheduler import frontier

    ready = frontier(conn, principal_present=True)
    claimed = {r["role"]: r["session_id"] for r in
               conn.execute("SELECT role, session_id FROM claims")}
    counts = {}
    for artefact, tables in _artefact_tables().items():
        total = 0
        for t in tables:
            try:
                total += conn.execute(f"SELECT COUNT(*) n FROM {t}").fetchone()["n"]
            except sqlite3.Error:
                pass
        counts[artefact] = total
    return {
        "ready": [{"role": w.role, "kind": w.kind, "detail": w.detail} for w in ready],
        "claimed": claimed,
        "volume": counts,
    }


def _artefact_tables() -> dict[str, tuple[str, ...]]:
    from ..core.db import TABLES_OF_ARTEFACT

    return TABLES_OF_ARTEFACT
