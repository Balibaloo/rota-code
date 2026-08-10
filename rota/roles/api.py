"""
Artefact operations. One function per (artefact, verb) edge in the graph.

These are the bodies behind the wiring. The graph declares that
`critic reads criteria (load, rows=batch, depth=body)` exists; this file says
what `load` *does*. Two axes on the edge decide how much it may return:

    rows    none | single | batch | window | delta | query | all
    depth   index (id plus one line each) | body (the prose too)

The pair is what keeps an 8k working set viable whether the glossary holds
ninety terms or nine hundred: almost everything reads `all` rows at `index`
depth and fetches bodies singly. It also makes the one dangerous combination
sayable — every row, in full — so the graph can forbid it to non-owners. That
restriction is about authority, not cost.

Every function takes the session context first so reach and provenance can be
enforced centrally; the sandbox binds that away before the model ever sees them.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Any, Callable

REGISTRY: dict[tuple[str, str], Callable] = {}


@dataclass
class Ctx:
    """What a session is allowed to do, carried alongside the connection."""
    conn: sqlite3.Connection
    role: str
    mode: str = "normal"
    session_id: str = ""
    batch_id: str | None = None
    entry_id: str | None = None
    writes: list = None          # populated by the sandbox; committed atomically
    outbound: list = None        # messages staged this session
    trigger: str | None = None

    def __post_init__(self):
        if self.writes is None:
            self.writes = []
        if self.outbound is None:
            self.outbound = []


def op(artefact: str, verb: str):
    """Register an implementation for one graph edge."""
    def deco(fn: Callable) -> Callable:
        REGISTRY[(artefact, verb)] = fn
        return fn
    return deco


def _rows(cur) -> list[dict]:
    return [dict(r) for r in cur.fetchall()]


# ---------------------------------------------------------------------------
# transcript / brief
# ---------------------------------------------------------------------------

@op("transcript", "append")
def transcript_append(ctx: Ctx, id: str, author: str, text: str) -> dict:
    """Record an entry verbatim. Greetings included: the transcript exists so
    interpretations can be adjudicated against something un-interpreted."""
    nxt = ctx.conn.execute(
        "SELECT COALESCE(MAX(ts_order), 0) + 1 n FROM entries").fetchone()["n"]
    ctx.writes.append(("entries", id,
                       {"author": author, "text": text, "ts_order": nxt}))
    return {"id": id, "ts_order": nxt}


@op("transcript", "quote")
def transcript_quote(ctx: Ctx, entry_id: str) -> dict:
    """Recover emphasis: one entry, verbatim. A window, never bulk."""
    row = ctx.conn.execute(
        "SELECT id, author, text, ts_order FROM entries WHERE id = ?",
        (entry_id,)).fetchone()
    return dict(row) if row else {}


@op("brief", "segment")
def brief_segment(ctx: Ctx, id: str, span_start: int, span_end: int,
                  text: str, span_entry: str | None = None) -> dict:
    """
    Propose one statement at principal granularity.

    One thing they asked for is one statement; downstream roles re-decompose into
    their own artefacts.

    `span_entry` defaults to the entry this session is segmenting. A
    session segments exactly one entry and the system already knows which —
    asking the model to supply it added an argument it got wrong, and a wrong
    foreign key takes down the whole session rather than one call.
    """
    target = span_entry or ctx.entry_id
    if not target:
        raise ValueError("no entry to segment against")
    ctx.writes.append(("statements", id, {
        "span_entry": target, "span_start": span_start,
        "span_end": span_end, "text": text, "status": "proposed"}))
    return {"id": id, "span_entry": target}


@op("brief", "ratify")
def brief_ratify(ctx: Ctx, id: str) -> dict:
    ctx.writes.append(("statements", id, {"status": "ratified"}, False))
    return {"id": id, "status": "ratified"}


@op("brief", "list")
def brief_list(ctx: Ctx, since_version: int = 0) -> list[dict]:
    """Ratified statements, ids plus text. Superseded entries are excluded —
    the plateau is achieved by scoping, not by deleting."""
    return _rows(ctx.conn.execute(
        "SELECT id, text, status FROM statements "
        "WHERE status = 'ratified' AND version > ? ORDER BY id", (since_version,)))


# ---------------------------------------------------------------------------
# problem statement
# ---------------------------------------------------------------------------

@op("problem", "assert")
def problem_assert(ctx: Ctx, id: str, text: str, kind: str = "in_scope",
                   provenance: str = "decided") -> dict:
    ctx.writes.append(("items", id, {
        "text": text, "kind": kind, "provenance": provenance, "approval": "draft"}))
    return {"id": id}


@op("problem", "set approval")
def problem_set_approval(ctx: Ctx, id: str, approval: str) -> dict:
    """Approval must postdate the item's last amendment, so it is stamped with
    the item's current version at the moment it is granted."""
    row = ctx.conn.execute("SELECT version FROM items WHERE id = ?", (id,)).fetchone()
    ctx.writes.append(("items", id, {
        "approval": approval, "approval_ver": row["version"] if row else 1}, False))
    return {"id": id, "approval": approval}


@op("problem", "prioritize")
def problem_prioritize(ctx: Ctx, id: str, priority: int) -> dict:
    """
    Priority moves batches whole, by moving the item they trace to.

    It alters no approved content, trips no revocation, involves no Architect
    and never recomposes a batch — hence `amends=False`. Putting the number on
    the item rather than the batch is what makes that true by construction:
    there is no per-batch priority for a recomposition to have to preserve.
    """
    ctx.writes.append(("items", id, {"priority": priority}, False))
    return {"id": id, "priority": priority}


@op("problem", "consult")
def problem_consult(ctx: Ctx) -> list[dict]:
    """Every row at index depth: ids, kind and approval, no prose bodies."""
    return _rows(ctx.conn.execute(
        "SELECT id, kind, approval, approval_ver, version, substr(text, 1, 120) AS headline "
        "FROM items ORDER BY id"))


# ---------------------------------------------------------------------------
# glossary
# ---------------------------------------------------------------------------

@op("glossary", "amend")
def glossary_amend(ctx: Ctx, id: str, term: str, sense_short: str,
                   sense_body: str = "", provenance: str = "decided") -> dict:
    ctx.writes.append(("glossary_terms", id, {
        "term": term, "sense_short": sense_short, "sense_body": sense_body,
        "provenance": provenance}))
    return {"id": id}


@op("glossary", "lookup")
def glossary_lookup(ctx: Ctx, term: str) -> list[dict]:
    """One term, all senses — collisions are visible by construction."""
    return _rows(ctx.conn.execute(
        "SELECT id, term, sense_short, sense_body, provenance FROM glossary_terms "
        "WHERE term = ? ORDER BY id", (term,)))


@op("glossary", "consult")
def glossary_consult(ctx: Ctx, terms: list[str] | None = None) -> list[dict]:
    """
    Every row at index depth: id, term, one-line sense. Bodies stay out.

    Optionally filtered to terms in play. Filtering is principled rather than
    economising: a term absent from the working set's statements cannot collide
    with them.
    """
    if terms:
        marks = ", ".join("?" for _ in terms)
        return _rows(ctx.conn.execute(
            f"SELECT id, term, sense_short, provenance FROM glossary_terms "
            f"WHERE term IN ({marks}) ORDER BY term", terms))
    return _rows(ctx.conn.execute(
        "SELECT id, term, sense_short, provenance FROM glossary_terms ORDER BY term"))


# ---------------------------------------------------------------------------
# system model
# ---------------------------------------------------------------------------

@op("model", "amend")
def model_amend(ctx: Ctx, id: str, headline: str, text: str = "",
                bindings: list[str] | None = None,
                provenance: str = "decided") -> dict:
    ctx.writes.append(("constraints", id, {
        "headline": headline, "text": text, "provenance": provenance,
        "is_global": 0 if bindings else 1}))
    for grain in bindings or []:
        ctx.writes.append(("constraint_bindings", f"{id}:{grain}", {
            "constraint_id": id, "grain": grain, "grain_kind": "path"}))
    return {"id": id, "bindings": bindings or []}


@op("model", "find")
def model_find(ctx: Ctx, id: str, batch_id: str, constraint_id: str,
               status: str, grain: str) -> dict:
    """
    Architect's structural verdict on one constraint, for one batch.

    Three fields and no fourth. A finding says which constraint, whether the
    diff satisfied or violated it, and which grain triggered the check — the
    reasoning stays in the decision record, reachable by a ref if anyone needs
    it. Nobody usually does: what the merge gate needs is whether anything is
    violated, and that question has no interesting prose answer.
    """
    ctx.writes.append(("findings", id, {
        "batch_id": batch_id, "constraint_id": constraint_id,
        "commit_sha": _head_commit(ctx, batch_id),
        "status": status, "grain": grain}))
    return {"id": id, "status": status}


@op("model", "consult")
def model_consult(ctx: Ctx, grains: list[str] | None = None) -> list[dict]:
    """
    Every row at index depth, optionally filtered by binding intersection.

    A constraint that does not bind the modules in play genuinely does not apply
    there, so excluding it is correct rather than economising. Unbound and
    unresolvable constraints are always included — degradation lands on
    expensive, never on wrong.
    """
    from ..core.scheduler import constraints_for_grains
    ids = constraints_for_grains(ctx.conn, grains or []) if grains is not None else None
    if ids is None:
        return _rows(ctx.conn.execute(
            "SELECT id, headline, provenance, is_global FROM constraints ORDER BY id"))
    if not ids:
        return []
    marks = ", ".join("?" for _ in ids)
    return _rows(ctx.conn.execute(
        f"SELECT id, headline, provenance, is_global FROM constraints "
        f"WHERE id IN ({marks}) ORDER BY id", ids))


@op("model", "load")
def model_load(ctx: Ctx, ids: list[str]) -> list[dict]:
    """Bodies, fetched singly by id. The other half of the index/body split."""
    if not ids:
        return []
    marks = ", ".join("?" for _ in ids)
    return _rows(ctx.conn.execute(
        f"SELECT id, headline, text, provenance FROM constraints WHERE id IN ({marks})", ids))


@op("model", "survey")
def model_survey(ctx: Ctx, id: str, area: str, outcome: str,
                 citations: list[str] | None = None) -> dict:
    """
    Record a survey. Citations are validated against the code index, so
    "surveyed, none found" is evidence rather than a claim — a lazy surveyor
    cannot starve constraint zero by asserting it everywhere.
    """
    ctx.writes.append(("survey_records", id, {"area": area, "outcome": outcome}))
    unknown = []
    for grain in citations or []:
        exists = ctx.conn.execute(
            "SELECT 1 FROM code_index WHERE grain = ?", (grain,)).fetchone()
        if not exists:
            unknown.append(grain)
        ctx.writes.append(("survey_citations", f"{id}:{grain}", {
            "survey_id": id, "grain": grain, "resolves": 1 if exists else 0}))
    return {"id": id, "unresolved_citations": unknown}


# ---------------------------------------------------------------------------
# backlog: tickets / criteria / batches — one writer each
# ---------------------------------------------------------------------------

@op("tickets", "slice")
def tickets_slice(ctx: Ctx, id: str, item_id: str, text: str) -> dict:
    """Only approved lineages may be sliced; the caller is expected to have
    consulted the problem statement, and the predicate only fires for items whose
    approval postdates their last amendment."""
    ctx.writes.append(("tickets", id, {"item_id": item_id, "text": text}))
    return {"id": id}


@op("tickets", "load")
def tickets_load(ctx: Ctx, batch_id: str | None = None) -> list[dict]:
    bid = batch_id or ctx.batch_id
    if bid:
        return _rows(ctx.conn.execute(
            "SELECT t.id, t.item_id, t.text FROM tickets t "
            "JOIN batch_tickets bt ON bt.ticket_id = t.id WHERE bt.batch_id = ?", (bid,)))
    return []


@op("tickets", "scan")
def tickets_scan(ctx: Ctx, item_id: str | None = None) -> list[dict]:
    if item_id:
        return _rows(ctx.conn.execute(
            "SELECT id, item_id, substr(text,1,120) AS headline FROM tickets "
            "WHERE item_id = ? ORDER BY id", (item_id,)))
    return _rows(ctx.conn.execute(
        "SELECT id, item_id, substr(text,1,120) AS headline FROM tickets ORDER BY id"))


@op("tickets", "consult")
def tickets_consult(ctx: Ctx) -> list[dict]:
    return tickets_scan(ctx)


@op("criteria", "specify")
def criteria_specify(ctx: Ctx, id: str, ticket_id: str, text: str,
                     term_refs: list[str] | None = None) -> dict:
    """Criteria are written in glossary terms; term_refs is not decoration."""
    ctx.writes.append(("criteria", id, {
        "ticket_id": ticket_id, "text": text,
        "term_refs": json.dumps(term_refs or [])}))
    return {"id": id}


@op("criteria", "load")
def criteria_load(ctx: Ctx, batch_id: str | None = None) -> list[dict]:
    bid = batch_id or ctx.batch_id
    if not bid:
        return []
    return _rows(ctx.conn.execute(
        "SELECT c.id, c.ticket_id, c.text, c.term_refs FROM criteria c "
        "JOIN batch_tickets bt ON bt.ticket_id = c.ticket_id WHERE bt.batch_id = ?", (bid,)))


@op("criteria", "consult")
def criteria_consult(ctx: Ctx) -> list[dict]:
    return _rows(ctx.conn.execute(
        "SELECT id, ticket_id, substr(text,1,120) AS headline FROM criteria ORDER BY id"))


@op("criteria", "scan")
def criteria_scan(ctx: Ctx) -> list[dict]:
    return criteria_consult(ctx)


@op("batches", "group")
def batches_group(ctx: Ctx, id: str, item_id: str, ticket_ids: list[str]) -> dict:
    """Collision judgement. Batches are complete feature sets, immutable once
    formed: only a scope change may recompose one."""
    ctx.writes.append(("batches", id, {"item_id": item_id, "status": "pending"}))
    for tid in ticket_ids:
        ctx.writes.append(("batch_tickets", f"{id}:{tid}", {
            "batch_id": id, "ticket_id": tid}))
    return {"id": id, "tickets": ticket_ids}


@op("batches", "annotate")
def batches_annotate(ctx: Ctx, batch_id: str, paths: list[str],
                     symbols: list[str] | None = None) -> dict:
    """
    What this batch is expected to touch.

    Paths always; symbols only where you are confident, which is why they are a
    separate argument rather than a flag on each grain — being asked to rate
    your own confidence per item invites rating everything "high".

    Nothing rejects a diff for straying outside this. It exists so that "was
    this change incidental?" has an answer at review time rather than an
    argument, and a prediction that could block work would quietly become a
    permission system nobody designed.
    """
    for path in paths:
        ctx.writes.append(("batch_touch", f"{batch_id}:{path}", {
            "batch_id": batch_id, "grain": path, "grain_kind": "path",
            "confidence": "expected"}))
    for symbol in symbols or []:
        ctx.writes.append(("batch_touch", f"{batch_id}:{symbol}", {
            "batch_id": batch_id, "grain": symbol, "grain_kind": "symbol",
            "confidence": "possible"}))
    return {"batch_id": batch_id, "grains": len(paths) + len(symbols or [])}


@op("batches", "consult")
def batches_consult(ctx: Ctx) -> list[dict]:
    """Priority comes from the item, which is where the principal set it."""
    return _rows(ctx.conn.execute(
        "SELECT b.id AS id, b.item_id AS item_id, b.status AS status, "
        "       i.priority AS priority "
        "FROM batches b JOIN items i ON i.id = b.item_id "
        "ORDER BY i.priority DESC, b.id"))


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

@op("tests", "author")
def tests_author(ctx: Ctx, id: str, batch_id: str, criterion_id: str,
                 path: str, body: str) -> dict:
    """Criteria made executable, written before the diff exists."""
    ctx.writes.append(("tests", id, {
        "batch_id": batch_id, "criterion_id": criterion_id,
        "path": path, "body": body}))
    return {"id": id}


@op("tests", "load")
def tests_load(ctx: Ctx, batch_id: str | None = None) -> list[dict]:
    bid = batch_id or ctx.batch_id
    if not bid:
        return []
    return _rows(ctx.conn.execute(
        "SELECT id, criterion_id, path, body FROM tests WHERE batch_id = ?", (bid,)))


@op("tests", "consult")
def tests_consult(ctx: Ctx) -> list[dict]:
    return _rows(ctx.conn.execute(
        "SELECT id, batch_id, criterion_id, path FROM tests ORDER BY id"))


# ---------------------------------------------------------------------------
# journals
# ---------------------------------------------------------------------------

@op("ledger", "log")
def ledger_log(ctx: Ctx, id: str, about_ref: str, about_table: str,
               default_taken: str) -> dict:
    """A choice made where the criteria were silent. Logged with the diff, in the
    same session — the silent default is the failure this exists to prevent."""
    ctx.writes.append(("ledger", id, {
        "about_ref": about_ref, "about_table": about_table,
        "default_taken": default_taken, "status": "open", "author": ctx.role}))
    return {"id": id}


@op("ledger", "list")
def ledger_list(ctx: Ctx) -> list[dict]:
    return _rows(ctx.conn.execute(
        "SELECT id, about_ref, about_table, default_taken, author FROM ledger "
        "WHERE status = 'open' ORDER BY id"))


@op("decisions", "author")
def decisions_author(ctx: Ctx, id: str, text: str, refs: list[str] | None = None,
                     supersedes: str | None = None,
                     resolves_ledger: str | None = None) -> dict:
    """
    Authored by whoever decided, in the same session as the decision. There is
    no recording step and no scribe role.

    Resolving a ledger entry happens *here* and nowhere else. There is no
    `ledger.resolve`, deliberately: an assumption that could close itself would
    void "no milestone with open assumptions", which is the only thing making
    the ledger more than a list of regrets. Both writes land in one commit, so a
    resolved entry always has the decision that resolved it.
    """
    ctx.writes.append(("decisions", id, {
        "author": ctx.role, "text": text, "refs": json.dumps(refs or []),
        "supersedes": supersedes, "resolves_ledger": resolves_ledger}))
    if resolves_ledger:
        ctx.writes.append(("ledger", resolves_ledger, {"status": "resolved"}, False))
    return {"id": id, "resolves_ledger": resolves_ledger}


@op("decisions", "search")
def decisions_search(ctx: Ctx, query: str) -> list[dict]:
    """Query scope: matches, never the corpus."""
    return _rows(ctx.conn.execute(
        "SELECT id, author, substr(text,1,200) AS headline, supersedes FROM decisions "
        "WHERE text LIKE ? ORDER BY id", (f"%{query}%",)))


def _head_commit(ctx: Ctx, batch_id: str) -> str | None:
    """
    Which diff a judgement is about.

    Filled by the system, not asked of the role. Critic judges a diff; it has no
    reason to know the sha, and asking would add an argument it could get wrong.
    Same shape as recording an entry: the judgement is the role's, the record of
    what it judged is not.
    """
    row = ctx.conn.execute(
        "SELECT head_commit FROM batches WHERE id = ?", (batch_id,)).fetchone()
    return row["head_commit"] if row else None


@op("verdicts", "emit")
def verdicts_emit(ctx: Ctx, id: str, batch_id: str, result: str,
                  failed_criterion: str | None = None, diff_ref: str = "") -> dict:
    ctx.writes.append(("verdicts", id, {
        "batch_id": batch_id, "result": result,
        "commit_sha": _head_commit(ctx, batch_id),
        "failed_criterion": failed_criterion, "diff_ref": diff_ref}))
    return {"id": id, "result": result}


@op("verdicts", "load")
def verdicts_load(ctx: Ctx, batch_id: str | None = None) -> list[dict]:
    bid = batch_id or ctx.batch_id
    return _rows(ctx.conn.execute(
        "SELECT id, batch_id, result, failed_criterion FROM verdicts WHERE batch_id = ?",
        (bid,)))


# ---------------------------------------------------------------------------
# schedule (derived; read-only for everyone)
# ---------------------------------------------------------------------------

@op("schedule", "consult")
def schedule_consult(ctx: Ctx) -> list[dict]:
    return _rows(ctx.conn.execute(
        "SELECT before_batch, after_batch FROM schedule_deps ORDER BY before_batch"))


# ---------------------------------------------------------------------------
# code — probes, not questions. The codebase is self-describing, which is why
# reading it grants no contact to its author.
# ---------------------------------------------------------------------------

@op("code", "probe")
def code_probe(ctx: Ctx, pattern: str = "") -> list[dict]:
    return _rows(ctx.conn.execute(
        "SELECT grain, grain_kind, area, fan_in FROM code_index "
        "WHERE grain LIKE ? ORDER BY fan_in DESC LIMIT 200", (f"%{pattern}%",)))


@op("code", "survey")
def code_survey(ctx: Ctx, area: str) -> list[dict]:
    return _rows(ctx.conn.execute(
        "SELECT grain, grain_kind, fan_in FROM code_index WHERE area = ? "
        "ORDER BY fan_in DESC", (area,)))


@op("code", "source")
def code_source(ctx: Ctx, path: str, start: int = 0, end: int = 400) -> dict:
    """
    Read source, by path and line range.

    Structural review was asking Architect to judge whether a change satisfies a
    constraint while giving it only the code *index* — grain names and fan-in
    counts. That is a collision detector wearing a reviewer's title: it can say a
    diff touched a bound path, which is an intersection, not a judgement.
    """
    from pathlib import Path as _P

    root = ctx.conn.execute(
        "SELECT value FROM config WHERE key = 'project_root'").fetchone()
    base = _P(root["value"].strip('"')) if root else _P(".")
    target = (base / path).resolve()
    if not str(target).startswith(str(base.resolve())):
        raise ValueError(f"{path!r} escapes the project root")
    if not target.exists():
        return {"path": path, "error": "not found"}
    lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    return {"path": path, "start": start, "end": min(end, len(lines)),
            "total_lines": len(lines), "text": chr(10).join(lines[start:end])}


@op("code", "diff")
def code_diff(ctx: Ctx, batch_id: str | None = None) -> dict:
    """
    What changed in a batch's worktree.

    Distinct from `probe`, which searches the index, and from `source`, which
    reads a file as it stands. A review needs the change, not the state.
    """
    import subprocess

    bid = batch_id or ctx.batch_id
    row = ctx.conn.execute(
        "SELECT worktree, head_commit FROM batches WHERE id = ?", (bid,)).fetchone()
    if not row or not row["worktree"]:
        return {"batch": bid, "error": "no worktree"}
    try:
        out = subprocess.run(
            ["git", "-C", row["worktree"], "diff", "HEAD~1", "--unified=3"],
            capture_output=True, text=True, timeout=30)
        return {"batch": bid, "diff": out.stdout[:20000]}
    except Exception as exc:
        return {"batch": bid, "error": str(exc)}


@op("code", "read")
def code_read(ctx: Ctx, batch_id: str | None = None) -> dict:
    """The batch diff. Critic's entire view of the implementation."""
    bid = batch_id or ctx.batch_id
    row = ctx.conn.execute(
        "SELECT id, worktree, head_commit FROM batches WHERE id = ?", (bid,)).fetchone()
    return dict(row) if row else {}


@op("code", "commit")
def code_commit(ctx: Ctx, batch_id: str, head_commit: str) -> dict:
    """Record the commit the database now has a receipt for. Git itself is
    outside the transaction; this is the marker boot reconciles against."""
    ctx.writes.append(("batches", batch_id, {"head_commit": head_commit}, False))
    return {"batch_id": batch_id, "head_commit": head_commit}
