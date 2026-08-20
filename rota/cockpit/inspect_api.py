"""
Deep inspection: the actual rows, the actual prompts, the actual calls.

The graph shows structure; this shows contents. Summaries are what you build when
you cannot serve the real thing — here we can, so nothing is aggregated away. If
you click `glossary`, you get the glossary, not a count of it.

Everything is assembled from the same sources the system runs on. There is no
reporting layer with its own idea of the truth.
"""
from __future__ import annotations

import json
import sqlite3
from typing import Any

from ..design import graph as graph_mod
from ..roles import prompts as prompts_mod
from ..core.db import TABLES_OF_ARTEFACT, connect
from ..core.sandbox import build as build_sandbox

# Columns worth showing first, per table. Everything else follows.
LEAD_COLUMNS = {
    "entries": ("id", "author", "ts_order", "text"),
    "statements": ("id", "status", "span_entry", "text"),
    "items": ("id", "kind", "approval", "approval_ver", "priority", "version", "text"),
    "glossary_terms": ("id", "term", "sense_short", "provenance"),
    "constraints": ("id", "headline", "provenance", "is_global"),
    "tickets": ("id", "item_id", "text"),
    "criteria": ("id", "ticket_id", "text", "term_refs"),
    "batches": ("id", "item_id", "status", "worktree", "head_commit"),
    "batch_touch": ("batch_id", "grain", "grain_kind", "confidence"),
    "findings": ("id", "batch_id", "constraint_id", "status", "grain"),
    "test_runs": ("id", "batch_id", "test_id", "result", "attempt"),
    "tests": ("id", "batch_id", "criterion_id", "path"),
    "verdicts": ("id", "batch_id", "result", "failed_criterion"),
    "ledger": ("id", "status", "author", "about_ref", "default_taken"),
    "decisions": ("id", "author", "supersedes", "text"),
}


def _columns(conn: sqlite3.Connection, table: str) -> list[str]:
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]
    lead = [c for c in LEAD_COLUMNS.get(table, ()) if c in cols]
    return lead + [c for c in cols if c not in lead]


def artefact(conn: sqlite3.Connection, artefact_id: str, limit: int = 300) -> dict[str, Any]:
    """Every row backing an artefact, table by table. The record itself."""
    g = graph_mod.load()
    node = g.nodes.get(artefact_id)
    tables = TABLES_OF_ARTEFACT.get(artefact_id, ())

    out: dict[str, Any] = {
        "id": artefact_id,
        "label": node.label if node else artefact_id,
        "note": node.note if node else "",
        "contact": node.contact if node else True,
        "contact_why": node.contact_why if node else "",
        "written_by": sorted(g.writer_of(artefact_id)),
        "read_by": sorted(r for r in g.roles if artefact_id in g.read_set(r)),
        "operations": [
            {"role": e.s, "type": e.type, "verb": e.v, "noun": e.n,
             "rows": e.rows, "depth": e.depth,
             "label": e.label, "actor": e.actor}
            for e in g.edges
            if e.t == artefact_id and e.type in ("reads", "writes")
        ],
        "refs_out": [{"to": e.t, "rel": e.v, "card": e.card}
                     for e in g.of_type("refs") if e.s == artefact_id],
        "refs_in": [{"from": e.s, "rel": e.v, "card": e.card}
                    for e in g.of_type("refs") if e.t == artefact_id],
        "tables": [],
    }

    for table in tables:
        try:
            cols = _columns(conn, table)
            rows = [dict(r) for r in conn.execute(
                f"SELECT {', '.join(cols)} FROM {table} LIMIT {limit}")]
            version = conn.execute(
                "SELECT version FROM artefact_versions WHERE table_name = ?",
                (table,)).fetchone()
            out["tables"].append({
                "name": table, "columns": cols, "rows": rows,
                "version": version["version"] if version else 0,
                "count": conn.execute(f"SELECT COUNT(*) n FROM {table}").fetchone()["n"],
            })
        except sqlite3.Error as exc:
            out["tables"].append({"name": table, "error": str(exc)})

    out["receipts"] = [dict(r) for r in conn.execute(
        "SELECT r.table_name, r.row_id, r.new_version, s.role, s.id AS session "
        "FROM receipts r JOIN sessions s ON s.id = r.session_id "
        f"WHERE r.table_name IN ({', '.join('?' * len(tables))}) "
        "ORDER BY r.rowid DESC LIMIT 40", tables)] if tables else []

    return out


def role(conn: sqlite3.Connection, role_id: str) -> dict[str, Any]:
    """
    What this role is, can do, is told, and has done.

    The working set is built the same way a session builds it, so what is shown
    here is what the model is actually handed — not a description of it.
    """
    g = graph_mod.load()
    node = g.nodes.get(role_id)
    sb = build_sandbox(role_id, conn, g=g)

    # Contacts, each with the artefact and clause that justifies it. Law 3 made
    # inspectable: a contact you cannot explain is one that should not exist.
    contacts = []
    for other in sorted(g.derived_contacts(role_id)):
        ask = sorted(a for a in g.read_set(role_id)
                     if other in g.writer_of(a) and g.contactable(a))
        inform = sorted(a for a in g.write_set(role_id)
                        if a in g.read_set(other) and g.contactable(a))
        verbs = sorted({e.v for e in g.of_type("messages")
                        if e.s == role_id and e.t == other})
        contacts.append({
            "role": other, "verbs": verbs,
            "because_reads": ask, "because_writes": inform,
            "clause": "ask" if ask else "inform",
        })

    modes = {}
    for mode in prompts_mod.available(role_id):
        allow = prompts_mod.mode_tools(role_id, mode)
        scoped = build_sandbox(role_id, conn, allow=allow, g=g) if allow else sb
        modes[mode] = {
            "piece": prompts_mod.piece(role_id, mode),
            "composed": prompts_mod.compose(role_id, mode),
            "tools": scoped.signatures(),
        }

    sessions = [dict(r) for r in conn.execute(
        "SELECT id, trigger_msg, mode, committed, model, prompt_hash, seq "
        "FROM sessions WHERE role = ? ORDER BY seq DESC LIMIT 25", (role_id,))]
    for s in sessions:
        s["writes"] = [dict(r) for r in conn.execute(
            "SELECT table_name, row_id FROM receipts WHERE session_id = ?", (s["id"],))]
        s["calls"] = [r["fn"] for r in conn.execute(
            "SELECT fn FROM tool_calls WHERE session_id = ? ORDER BY seq", (s["id"],))]

    from ..testkit.coverage import all_edges, load as load_coverage

    seen = load_coverage()
    mine = [e for e in all_edges(g) if e.role == role_id]
    covered = [e for e in mine
               if e in seen or type(e)(e.role, e.kind, e.target, "*") in seen]

    return {
        "id": role_id,
        "label": node.label if node else role_id,
        "note": node.note if node else "",
        "base_prompt": prompts_mod.base(role_id),
        "working_set": sb.signatures(),
        "reads": sorted(g.read_set(role_id)),
        "writes": sorted(g.write_set(role_id)),
        "contacts": contacts,
        "inbound_verbs": sorted(prompts_mod.inbound_verbs(role_id)),
        "modes": modes,
        "sessions": sessions,
        "coverage": {"covered": len(covered), "total": len(mine),
                     "missing": [str(e) for e in mine if e not in covered]},
    }


def edge(conn: sqlite3.Connection, s: str, t: str, etype: str) -> dict[str, Any]:
    """The grammar of one edge, and the evidence it has ever been used."""
    g = graph_mod.load()
    matches = [e for e in g.edges if e.s == s and e.t == t and e.type == etype]
    if not matches:
        return {"error": f"no {etype} edge {s} -> {t}"}

    out: dict[str, Any] = {
        "source": s, "target": t, "type": etype,
        "variants": [
            {"verb": e.v, "noun": e.n, "rows": e.rows, "depth": e.depth,
             "label": e.label,
             "actor": e.actor, "card": e.card}
            for e in matches
        ],
        "evidence": [],
    }

    if etype == "messages":
        out["evidence"] = [dict(r) for r in conn.execute(
            "SELECT id, verb, status, body_refs, round_no, attempts FROM messages "
            "WHERE from_role = ? AND to_role = ? ORDER BY seq DESC LIMIT 40", (s, t))]
    else:
        verbs = tuple(f"{t}.{e.v.replace(' ', '_')}" for e in matches)
        if verbs:
            out["evidence"] = [dict(r) for r in conn.execute(
                "SELECT tc.fn, tc.args_summary, tc.session_id FROM tool_calls tc "
                "JOIN sessions ses ON ses.id = tc.session_id "
                f"WHERE ses.role = ? AND tc.fn IN ({', '.join('?' * len(verbs))}) "
                "ORDER BY tc.rowid DESC LIMIT 40", (s, *verbs))]

    from ..testkit.coverage import load as load_coverage

    seen = load_coverage()
    out["covered"] = any(k.role == s and k.target == t and k.kind == etype for k in seen)
    return out


def blast_radius(artefact_id: str) -> dict[str, Any]:
    """
    What a change here would cascade to, in wake order.

    The cascade walks the refs DAG and summons each owner; this is that walk,
    made visible before it happens rather than reconstructed afterwards.
    """
    from ..core.scheduler import cascade_order

    g = graph_mod.load()
    dependents: dict[str, set[str]] = {a: set() for a in g.artefacts}
    for e in g.of_type("refs"):
        dependents.setdefault(e.t, set()).add(e.s)

    affected, queue = set(), [artefact_id]
    while queue:
        a = queue.pop()
        for dep in dependents.get(a, ()):
            if dep not in affected:
                affected.add(dep)
                queue.append(dep)

    order = [a for a in cascade_order(g) if a in affected]
    return {
        "from": artefact_id,
        "artefacts": order,
        "wakes": [{"artefact": a, "owners": sorted(g.writer_of(a))} for a in order],
    }


def message_graph(conn: sqlite3.Connection, limit: int = 400) -> dict[str, Any]:
    """
    The conversation, as a graph.

    Every message refs its cause, so the message log *is* a DAG — roots are
    principal entries, gate events and ticks. Drawing it shows the shape of a
    conversation the way the role graph shows the shape of the team: which
    threads branched, where a round closed, what is still open.

    Each message carries what its session produced, so the picture answers "and
    then what happened" without a second lookup.
    """
    rows = [dict(r) for r in conn.execute(
        "SELECT id, cause_id, cause_kind, thread_id, from_role, to_role, verb, "
        "       body_refs, round_no, seq, attempts, status "
        "FROM messages ORDER BY seq LIMIT ?", (limit,))]

    produced: dict[str, dict] = {}
    for s in conn.execute(
        "SELECT id, role, trigger_msg, mode, committed, model FROM sessions "
        "WHERE trigger_msg IS NOT NULL"
    ):
        produced[s["trigger_msg"]] = {
            "session": s["id"], "role": s["role"], "mode": s["mode"],
            "committed": bool(s["committed"]), "model": s["model"],
            "calls": [c["fn"] for c in conn.execute(
                "SELECT fn FROM tool_calls WHERE session_id = ? ORDER BY seq",
                (s["id"],))],
            "writes": [f'{w["table_name"]}:{w["row_id"]}' for w in conn.execute(
                "SELECT table_name, row_id FROM receipts WHERE session_id = ?",
                (s["id"],))],
        }

    for r in rows:
        r["body_refs"] = json.loads(r["body_refs"] or "[]")
        r["produced"] = produced.get(r["id"])
        r["entry"] = None
        if r["from_role"] == "principal":
            u = conn.execute(
                "SELECT text FROM entries WHERE id = ?", (f'e_{r["id"]}',)).fetchone()
            if u:
                r["entry"] = u["text"]

    threads: dict[str, list[str]] = {}
    for r in rows:
        threads.setdefault(r["thread_id"], []).append(r["id"])

    return {"messages": rows, "threads": threads,
            "open": [r["id"] for r in rows if r["status"] == "open"]}


# ---------------------------------------------------------------------------
# Why is this row here — the chain, backwards
# ---------------------------------------------------------------------------

CHAIN_LIMIT = 40


def _refs(blob: str | None) -> list[str]:
    try:
        loaded = json.loads(blob or "[]")
    except (TypeError, ValueError):
        return []
    return [r for r in loaded if isinstance(r, str)]


def provenance(conn: sqlite3.Connection, table: str, row_id: str) -> dict[str, Any]:
    """
    From an artefact row back to the thing that caused it.

    **row -> the session that wrote it -> what it was shown and did -> what
    woke it -> what caused that**, to a tick or to the principal's sentence.

    Every piece of this was already recorded and none of it was joined. Twice
    now the question has had to be answered for real — once for the intake bug,
    once for "what is a survey session actually shown" — and both times the
    method was a throwaway script joining four tables by hand. `receipts` is the
    link nobody was following: it has carried `(session_id, table_name, row_id)`
    on every commit since Law 4.

    Read-only, like everything else the cockpit serves.
    """
    out: dict[str, Any] = {
        "table": table, "row_id": row_id, "found": False, "row": {},
        "session": None, "history": [], "woken_by": None, "chain": [],
        "did": [], "shown": {}, "note": "",
    }

    try:
        cols = _columns(conn, table)
    except sqlite3.Error:
        out["note"] = f"no such table: {table}"
        return out

    key = "id" if "id" in cols else cols[0]
    try:
        row = conn.execute(
            f"SELECT * FROM {table} WHERE {key} = ?", (row_id,)).fetchone()
    except sqlite3.Error as exc:
        out["note"] = str(exc)
        return out
    if row is None:
        out["note"] = f"no row {row_id!r} in {table}"
        return out
    out["found"] = True
    out["row"] = {c: row[c] for c in row.keys()}

    # Every session that ever touched it, oldest first. The latest leads
    # because the question is nearly always about what the row says *now*, and
    # the rest stay because "who changed this" is the other half of it.
    out["history"] = [
        {"session": r["session_id"], "version": r["new_version"],
         "role": r["role"], "wake": r["wake_kind"], "detail": r["wake_detail"]}
        for r in conn.execute(
            "SELECT c.session_id, c.new_version, s.role, s.wake_kind, "
            "       s.wake_detail, s.seq "
            "FROM receipts c JOIN sessions s ON s.id = c.session_id "
            "WHERE c.table_name = ? AND c.row_id = ? ORDER BY s.seq",
            (table, row_id))]
    if not out["history"]:
        # Ordinary, not broken: onboarding writes `code_index` and constraint
        # zero outside any session. Saying nothing wrote it beats implying
        # something did.
        out["note"] = ("no session claims this row — written by onboarding or "
                       "by a migration rather than by a role")
        return out

    sid = out["history"][-1]["session"]
    s = conn.execute(
        "SELECT id, role, mode, model, temperature, num_ctx, prompt_hash, "
        "       trigger_msg, committed, seq, wake_kind, wake_detail, wake_refs "
        "FROM sessions WHERE id = ?", (sid,)).fetchone()
    out["session"] = {c: s[c] for c in s.keys()}
    out["woken_by"] = {
        "kind": s["wake_kind"] or ("message" if s["trigger_msg"] else "unrecorded"),
        "detail": s["wake_detail"] or "",
        "refs": _refs(s["wake_refs"]),
        "message": s["trigger_msg"],
    }
    out["did"] = [{"fn": c["fn"], "args": c["args_summary"], "seq": c["seq"]}
                  for c in conn.execute(
                      "SELECT fn, args_summary, seq FROM tool_calls "
                      "WHERE session_id = ? ORDER BY seq", (sid,))]
    out["chain"] = causal_chain(conn, s["trigger_msg"])
    out["shown"] = shown_to(conn, s["role"], s["mode"], s["prompt_hash"], sid)
    return out


def causal_chain(conn: sqlite3.Connection, message_id: str | None) -> list[dict]:
    """
    A message and everything that caused it, newest first.

    The same `cause_id` walk `scheduler.edge_repeats` makes for the livelock
    bound, turned around: there it counts a chain to stop it, here it reads one
    to explain it.

    Bounded and cycle-guarded for the same reason `edge_repeats` is. `cause_id`
    is data — a hand-edited database or a bug can point a message at itself,
    and a viewer that hangs on a malformed row is worse than one that shows a
    short chain.
    """
    chain: list[dict] = []
    seen: set[str] = set()
    at = message_id
    while at and at not in seen and len(chain) < CHAIN_LIMIT:
        seen.add(at)
        m = conn.execute(
            "SELECT id, cause_id, cause_kind, thread_id, from_role, to_role, "
            "       verb, body_text, round_no, seq, status "
            "FROM messages WHERE id = ?", (at,)).fetchone()
        if m is None:
            break
        chain.append({c: m[c] for c in m.keys()})
        at = m["cause_id"]
    return chain


def shown_to(conn: sqlite3.Connection, role: str, mode: str,
             prompt_hash: str | None, session_id: str = "") -> dict[str, Any]:
    """
    What the session was told — the reconstructible part, and a plain statement
    of the part that is not.

    The **brief** composes exactly: it is a function of role and mode, so it can
    be rebuilt. The **toolkit** derives from the graph the same way. What was
    *pushed* into the prompt — the working set the session actually read — is
    retained nowhere. Only `prompt_hash` is, and it hashes the whole prompt, so
    it cannot even confirm the brief alone is unchanged.

    Saying so is the point rather than a caveat. A reconstruction presented as
    the real prompt is how "the sentence was in there, so the role ignored it"
    survives for a week — and the intake bug turned out to be the opposite: the
    sentence was absent, and only printing the actual prompt showed it.
    """
    out: dict[str, Any] = {
        "role": role, "mode": mode, "brief": "", "tools": [], "turns": [],
        "prompt_hash": prompt_hash, "working_set": None, "note": "",
    }
    # The real thing, when the run recorded it. `turns` holds the exact context
    # and the exact response per round-trip, so there is nothing to reconstruct
    # and nothing to apologise for.
    if session_id:
        out["turns"] = [{k: r[k] for k in r.keys()} for r in conn.execute(
            "SELECT seq, system, user, completion, ms FROM turns "
            "WHERE session_id = ? ORDER BY seq", (session_id,))]
    if out["turns"]:
        return out

    # Older runs, and sessions that never reached the model. The rebuild is the
    # honest fallback and says what it is -- dropping it would make a database
    # written before `turns` less inspectable than it was.
    out["note"] = ("no transcript was recorded for this session; the brief and "
                   "toolkit below are rebuilt from the current prompts and "
                   "graph, which may have changed since it ran, and the working "
                   "set it was pushed is not retained")
    try:
        out["brief"] = prompts_mod.compose(role, mode if mode != "normal" else "")
    except Exception:                                          # noqa: BLE001
        try:
            out["brief"] = prompts_mod.base(role)
        except Exception:                                      # noqa: BLE001
            out["note"] = f"no brief on file for {role}/{mode}; " + out["note"]
    try:
        out["tools"] = list(build_sandbox(role, conn).signatures())
    except Exception as exc:                                   # noqa: BLE001
        out["note"] = f"toolkit unavailable ({exc}); " + out["note"]
    return out
