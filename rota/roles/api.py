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
    # Law 11 in one field. `observed` means extracted from an onboarded
    # codebase — found, not chosen — and that is true of a survey session and
    # of nothing else. It was an argument the model supplied, and Architect
    # filled it with `deliver`: the name of the mode it was woken in. A field
    # whose value is a fact about the session should be filled by the session.
    provenance: str = "decided"
    session_id: str = ""
    batch_id: str | None = None
    # Which area a survey session is surveying. Decided by the scheduler, which
    # runs one area at a time in role order, and never by the role -- the same
    # reasoning as `batch_id`. Without it `code.survey(area=...)` was the one
    # call a survey mode exists to make and the one the session had to guess an
    # argument for, so nothing was pushed and all three survey roles opened by
    # consulting their own artefact and stopping.
    area: str | None = None
    entry_id: str | None = None
    writes: list = None          # populated by the sandbox; committed atomically
    outbound: list = None        # messages staged this session
    trigger: str | None = None
    # Files this session actually opened, by `code.source`. Law 12 says a
    # constraint is a commitment to something outside the codebase; you cannot
    # have found one in a file you did not read, and the first foreign repo
    # produced twenty-four constraints from sessions that had opened almost
    # nothing. The session already knew what it had read — nobody asked it.
    opened: set = None

    def __post_init__(self):
        if self.writes is None:
            self.writes = []
        if self.outbound is None:
            self.outbound = []
        if self.opened is None:
            self.opened = set()


def op(artefact: str, verb: str):
    """Register an implementation for one graph edge."""
    def deco(fn: Callable) -> Callable:
        REGISTRY[(artefact, verb)] = fn
        return fn
    return deco


def _rows(cur) -> list[dict]:
    return [dict(r) for r in cur.fetchall()]


def _batch_of_criterion(ctx: "Ctx", criterion_id: str) -> str | None:
    """
    The batch a criterion's ticket belongs to, when the session was not woken
    holding one.

    `ctx.batch_id` covers the `tests_missing` tick, where the scheduler names
    the batch. It is empty when Tester is woken by a *message* -- a term answer
    arrives, and the answer settles what the criterion means, so a test follows
    from it. The batch is still the same batch, and it is two joins away.

    Asking the role for it instead produced `batch_id='g_1a4b8f'` nineteen times
    in one session: the glossary term id from the message that woke it, because
    a required argument has to be filled with something and that was the only id
    in front of it. Making a role supply a fact the database can derive is
    asking it to do a join, and it will guess rather than refuse.

    Ambiguity is left alone. A ticket in two batches has no single answer here,
    and inventing one would file a test against the wrong delivery.
    """
    rows = ctx.conn.execute(
        "SELECT DISTINCT bt.batch_id AS id FROM criteria c "
        "JOIN batch_tickets bt ON bt.ticket_id = c.ticket_id "
        "WHERE c.id = ?", (criterion_id,)).fetchall()
    return rows[0]["id"] if len(rows) == 1 else None


def _must_exist(ctx: "Ctx", table: str, id: str) -> None:
    """
    A state change needs something to change the state *of*.

    Without this, setting the approval of an id that does not exist stages a
    partial write, `_apply_write` inserts it because there is no row to update,
    and SQLite raises NOT NULL inside the transaction — taking down a session
    that was otherwise sound. That is precisely what the sandbox's argument
    validation exists to prevent, applied one level deeper: a bad *reference* is
    as recoverable as a bad enum, and both should come back as tool errors the
    model can correct on its next turn.

    Found by L1: a Gatekeeper session ruled on an item id it had invented, and
    the whole session was lost instead of one call.
    """
    hit = ctx.conn.execute(
        f"SELECT 1 FROM {table} WHERE id = ?", (id,)).fetchone()
    if hit is None:
        # Name the ids that would have worked. "The id has to be one you were
        # given" is true and unhelpful when the model is holding four ids and
        # picked the wrong kind -- a glossary term where a batch was wanted.
        # Saying which rows exist turns a scolding into a correction.
        have = [r["id"] for r in ctx.conn.execute(
            f"SELECT id FROM {table} ORDER BY id LIMIT 6")]
        known = (f"; {table} rows are {have}" if have
                 else f"; there are no {table} rows at all")
        raise ValueError(
            f"no {table} row with id={id!r}; this changes an existing row, so "
            f"the id has to be one you were given{known}")


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
    _must_exist(ctx, "statements", id)
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
def problem_assert(ctx: Ctx, id: str, text: str, kind: str = "in_scope") -> dict:
    ctx.writes.append(("items", id, {
        "text": text, "kind": kind, "provenance": ctx.provenance,
        "approval": "draft"}))
    return {"id": id}


@op("problem", "set approval")
def problem_set_approval(ctx: Ctx, id: str, approval: str) -> dict:
    """Approval must postdate the item's last amendment, so it is stamped with
    the item's current version at the moment it is granted."""
    _must_exist(ctx, "items", id)
    row = ctx.conn.execute("SELECT version FROM items WHERE id = ?", (id,)).fetchone()
    ctx.writes.append(("items", id, {
        "approval": approval, "approval_ver": row["version"]}, False))
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
    _must_exist(ctx, "items", id)
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
def glossary_amend(ctx: Ctx, term: str, sense_short: str,
                   sense_body: str = "", sense: str = "") -> dict:
    """
    One meaning per word — so writing the same word twice amends it, and a second
    *sense* has to be asked for.

    The id is derived from the term. It used to be the role's to invent, and on
    the first foreign repository twelve sessions invented one apiece: `endpoint`
    five times, `client` three, `token` three, every one of them the same meaning
    written down again because the session that wrote it could not see itself in
    the glossary it had just been shown. Ten distinct terms, eighteen rows.

    `sense` is how a genuine collision is recorded — `nonce` meaning a replay
    guard in one module and a session binding in another is two rows, and it
    should take a deliberate act to make them. Accidental duplication is now
    impossible; deliberate duplication costs one argument.
    """
    import re

    slug = re.sub(r"[^a-z0-9]+", "_", term.strip().lower()).strip("_")
    if not slug:
        raise ValueError("a term needs a word in it")

    # `sense_short` is a required argument, which means positionally present
    # rather than filled -- nothing stopped an empty string, and the audit had
    # no counterpart to `a_constraint_needs_a_body` to catch one afterwards.
    #
    # A guard, not a scar: no run has produced a senseless term. It is here
    # because the constraint side needed exactly this rule and the glossary was
    # the one artefact where writing nothing cost nothing. Declining to define a
    # term stays free -- not writing the row at all is always allowed.
    if not (sense_short or "").strip() and not (sense_body or "").strip():
        raise ValueError(
            f"{term!r} has no sense under it. A glossary of words is the index "
            f"with the columns relabelled -- say what the word means here, in "
            f"the sense this area uses it, or leave it out.")

    id = f"{slug}#{re.sub(r'[^a-z0-9]+', '_', sense.strip().lower())}" if sense else slug

    ctx.writes.append(("glossary_terms", id, {
        "term": term, "sense_short": sense_short, "sense_body": sense_body,
        "provenance": ctx.provenance}))
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
def model_amend(ctx: Ctx, headline: str, text: str = "",
                bindings: list[str] | None = None,
                ) -> dict:
    """
    Write a constraint, and the grains it governs.

    The id derives from the headline, so writing the same commitment twice amends
    it. It used to be the role's to invent, and on the first foreign repository
    twelve sessions invented one apiece: 24 constraints carrying 6 distinct
    headlines, "Retention period for client tokens" eight times over. A duplicate
    glossary entry is clutter; a duplicate constraint is a duplicate *gate* —
    each one enters range at review, each has to be satisfied or argued with, and
    satisfying the first does nothing for the other seven.

    A headline is authored prose, not a word, so there is no `sense=` escape here
    and none is wanted: two commitments that genuinely differ have headlines that
    differ. The cost is that correcting a headline writes a new row rather than
    renaming the old one, which is the same trade the glossary makes.

    Constraint zero cannot be reached at all now. Its bindings are *derived* —
    exactly the areas nobody has surveyed — and the scheduler recomputes them
    from the survey records every time one lands, so the binding cannot drift
    from the evidence. That used to be a check on a supplied id; with no id to
    supply, only its seeded headline could collide, and that is refused by name.

    Refused rather than ignored, because ignoring it produced a livelock nobody
    could see from inside a session: an Architect survey bound a grain onto
    constraint zero, `tick_constraint_zero` noticed the bindings no longer
    matched the unsurveyed set and recomputed them away, the next Architect
    session bound it again, and the two alternated forever. Both were committing.
    Both were productive. Nothing was progressing.
    """
    import re

    from ..onboarding import boot

    slug = re.sub(r"[^a-z0-9]+", "_", headline.strip().lower()).strip("_")
    if not slug:
        raise ValueError("a constraint needs a headline with a word in it")
    if slug == boot.ZERO or headline.strip().lower() == boot.ZERO_HEADLINE.lower():
        raise ValueError(
            f"{boot.ZERO} is derived: its bindings are the areas nobody has "
            f"surveyed, and a survey record is what shrinks it. Write your own "
            f"constraint for what you found.")

    # You cannot have found a commitment in a file you did not open. The first
    # foreign repository produced constraints naming grains no session had read
    # -- the brief said to open them, the harness was cutting the result to a
    # docstring, so opening them achieved nothing and nothing checked either way.
    # `code.survey` is not reading: it returns the index, and the index is
    # exactly the material a fabricated constraint is made of.
    #
    # Checked after constraint zero, whose refusal is the more specific one and
    # was briefly being swallowed by this.
    unread = sorted(g for g in (bindings or []) if _grain_path(g) not in ctx.opened)
    if unread:
        raise ValueError(
            f"you have not read {', '.join(unread)} this session. A constraint "
            f"binds the grains it governs, and it cannot govern what nobody "
            f"opened -- `code.source` them first, or bind only what you read.")

    id = slug[:120]
    ctx.writes.append(("constraints", id, {
        "headline": headline, "text": text, "provenance": ctx.provenance,
        "is_global": 0 if bindings else 1}))
    for grain in bindings or []:
        ctx.writes.append(("constraint_bindings", f"{id}:{grain}", {
            "constraint_id": id, "grain": grain, "grain_kind": "path"}))
    return {"id": id, "bindings": bindings or []}


@op("findings", "load")
def findings_load(ctx: Ctx, batch_id: str | None = None) -> list[dict]:
    """What was found last time. Not anchoring, unlike Critic's verdicts: a
    constraint violated on the previous commit is exactly what you want to know
    is still violated."""
    bid = batch_id or ctx.batch_id
    return _rows(ctx.conn.execute(
        "SELECT id, constraint_id, commit_sha, status, grain FROM findings "
        "WHERE batch_id = ? ORDER BY id", (bid,)))


@op("findings", "find")
def findings_find(ctx: Ctx, id: str, batch_id: str, constraint_id: str,
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


@op("surveys", "attest")
def surveys_attest(ctx: Ctx, outcome: str,
                   citations: list[str] | None = None) -> dict:
    """
    Close the area you were woken for. Citations are validated against the code
    index, so "surveyed, none found" is evidence rather than a claim — a lazy
    surveyor cannot starve constraint zero by asserting it everywhere.

    `outcome` is 'constraints_found' or 'none_found'.

    **Both the area and the id are derived, and neither is the role's to choose.**
    The scheduler runs one area at a time in role order and the wake says which;
    a role that names its own would be deciding what it had been asked to do.

    On the first foreign repository this was a parameter, and a Terminologist
    woken for area `.` attested `area='common.py'` — a file inside it. The record
    filed against an area that does not exist, `tick_survey` never saw its area
    close, and the same wake was produced until the attempt bound withdrew it.
    Twelve areas, one survey, and the system reported itself quiescent.

    The id follows from the area for the same reason: `tick_survey` counts one
    row per role per area, so re-attesting replaces rather than accumulating.
    """
    area = ctx.area
    if not area:
        raise ValueError(
            "no area: attesting closes the area you were woken for, and this "
            "session was not woken for one")

    # The outcome has to match what the session actually did.
    #
    # The brief says most code is not a constraint and that `none_found` is most
    # often the right answer here. Architect returned `constraints_found` for ten
    # of eleven areas of a repository holding three or four real external
    # commitments -- and eight of those eleven constraints were a headline with
    # no body. Not dishonesty: being woken *for an area* is a demand, and the two
    # outcomes cost exactly the same, so one of them looks more like work.
    #
    # So they stop costing the same. Finding something means having written
    # something, with a body on it; finding nothing stays free. The asymmetry is
    # the point, because the honest answer is the one we need to be cheap.
    findings = [(t, v) for t, _id, v in ctx.writes
                if t in ("constraints", "glossary_terms", "items")]
    if outcome == "constraints_found":
        if not findings:
            raise ValueError(
                "you attested `constraints_found` and wrote nothing this "
                "session. Write what you found, or attest `none_found` -- which "
                "is a real answer and the commonest right one in this mode.")
        thin = [v.get("headline") or v.get("term")
                for t, v in findings
                if t == "constraints" and not (v.get("text") or "").strip()]
        if thin and len(thin) == len([1 for t, _ in findings if t == "constraints"]):
            raise ValueError(
                f"every constraint you wrote this session is a headline with "
                f"nothing under it ({', '.join(map(str, thin))}). A title cannot "
                f"be checked, argued with or satisfied -- say what the "
                f"commitment is and who outside would notice, or attest "
                f"`none_found`.")

    id = f"{ctx.role}:{area}"
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


@op("surveys", "consult")
def surveys_consult(ctx: Ctx) -> list[dict]:
    """
    Which areas have been surveyed, by whom, and with what result.

    Onboarding sessions compound through artefacts rather than context: area N's
    session has no memory of areas 1..N-1 and would otherwise have no way to
    know they happened, let alone that one of them came back `none_found`.

    One row per area, not per record. Three roles survey every area, so this
    returned 3N rows of bookkeeping — 3,900 characters of "role X did area Y" in
    every survey prompt on oauthlib, crowding out the material the session was
    woken to read.

    **The verdicts are gone from it, and that is the point.** It used to carry
    each area's outcome, so by area nine a session was looking at eight siblings
    that all said `constraints_found` — on a repository with three or four real
    external commitments in it. That is not context, it is a norm, and the
    artefact built to let sessions compound was teaching each one what the
    answer around here is. Ten of eleven areas duly found something.

    What compounds legitimately is what was *found*: the constraints themselves
    through `model.consult`, the terms through `glossary.consult`. Those are the
    findings. "Nine other people concluded something" is not a finding, and a
    session that has read the source does not need to be told the mood.
    """
    rows = _rows(ctx.conn.execute(
        "SELECT area, GROUP_CONCAT(SUBSTR(id, 1, INSTR(id, ':') - 1)) AS by_role "
        "FROM survey_records GROUP BY area ORDER BY area"))
    return [{"area": r["area"], "surveyed_by": sorted((r["by_role"] or "").split(",")),
             } for r in rows]


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
    _must_exist(ctx, "tickets", ticket_id)
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

@op("tests", "encode")
def tests_encode(ctx: Ctx, id: str, criterion_id: str, path: str, body: str,
                 batch_id: str | None = None) -> dict:
    """
    Criteria made executable, written before the diff exists.

    `batch_id` defaults to the batch this session was woken for. Which batch a
    test belongs to is the scheduler's, exactly as the worktree and the survey
    area are: Tester is woken by `tests_missing` with the batch in the wake and
    has no other batch it could mean. Asking for it produced `batch_id='12345'`
    across five runs — the model reaching for a plausible-looking value because
    a required argument had to be filled with something.

    `criterion_id` stays required, because that one is a choice: which criterion
    this test encodes is the whole judgement of the mode.

    Both references are checked here. A test naming a criterion that does not
    exist fails a foreign key *inside the transaction* and takes the session
    with it — the same shape as the invented item id, and recoverable for the
    same reason: the model can be told and try again.
    """
    batch_id = batch_id or ctx.batch_id or _batch_of_criterion(ctx, criterion_id)
    if not batch_id:
        raise ValueError("no batch in this session and none given")
    _must_exist(ctx, "batches", batch_id)
    _must_exist(ctx, "criteria", criterion_id)
    ctx.writes.append(("tests", id, {
        "batch_id": batch_id, "criterion_id": criterion_id,
        "path": path, "body": body}))
    return {"id": id}


@op("tests", "load")
def tests_load(ctx: Ctx, batch_id: str | None = None) -> list[dict]:
    """
    The batch's tests, each with what the harness last said about it.

    The body alone was all a Developer got in `tests_failing`, so the role woken
    to fix a red test could read what the test *asserts* and had to guess what
    red looked like. Two L1 cases turn on exactly that — is the code wrong or is
    the test wrong — and produced precisely swapped answers, which is the right
    answer to a question nobody had given them the evidence for.

    Only the latest run per test, and only when it is not passing. A green test
    has nothing to say and its output is noise in a context that is already the
    scarcest thing here.
    """
    bid = batch_id or ctx.batch_id
    if not bid:
        return []
    return _rows(ctx.conn.execute(
        "SELECT t.id AS id, t.criterion_id AS criterion_id, t.path AS path, "
        "       t.body AS body, r.result AS last_result, "
        "       CASE WHEN r.result = 'pass' THEN NULL ELSE r.output END AS said "
        "FROM tests t "
        "LEFT JOIN test_runs r ON r.id = ("
        "    SELECT id FROM test_runs WHERE test_id = t.id "
        "    ORDER BY attempt DESC, rowid DESC LIMIT 1) "
        "WHERE t.batch_id = ?", (bid,)))


@op("tests", "consult")
def tests_consult(ctx: Ctx) -> list[dict]:
    return _rows(ctx.conn.execute(
        "SELECT id, batch_id, criterion_id, path FROM tests ORDER BY id"))


# ---------------------------------------------------------------------------
# journals
# ---------------------------------------------------------------------------

@op("ledger", "log")
def ledger_log(ctx: Ctx, about_ref: str, about_table: str,
               default_taken: str) -> dict:
    """
    A choice made where the criteria were silent. Logged with the diff, in the
    same session — the silent default is the failure this exists to prevent.

    The id is derived from the assumption, not supplied. No writer can read the
    ledger, so a cold session that hits the same gap on a retry has no way to
    know it already logged this — and a milestone is quiescence with an *empty*
    ledger, so duplicates make the principal resolve one assumption three times.
    Deriving the id makes a repeat an upsert instead. It also means the same
    assumption reached by two roles is one entry, which is the truth.
    """
    import hashlib

    digest = hashlib.sha256(
        f"{about_table}|{about_ref}|{default_taken}".encode()).hexdigest()[:10]
    id = f"l_{digest}"
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
def verdicts_emit(ctx: Ctx, batch_id: str, result: str,
                  failed_criterion: str | None = None, diff_ref: str = "") -> dict:
    """
    Judge a commit. `result` is 'pass' or 'fail'; name the criterion a fail
    fails.

    The id is *derived* from the judge, the batch and the commit, because that is
    what a verdict is: one judgement, by one role, on one commit. `review` gates
    on exactly that triple. Asking the role to name it meant a Critic that
    emitted twice in a session left two verdicts on one commit -- which is not a
    judge changing its mind, it is a judge contradicting itself and leaving both
    on the record.
    """
    _must_exist(ctx, "batches", batch_id)
    if failed_criterion:
        _must_exist(ctx, "criteria", failed_criterion)
    commit = _head_commit(ctx, batch_id)
    id = f"{ctx.role}:{batch_id}:{commit}"
    ctx.writes.append(("verdicts", id, {
        "batch_id": batch_id, "result": result,
        "commit_sha": commit,
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
def code_survey(ctx: Ctx, area: str | None = None) -> list[dict]:
    """The area's grains, most depended-upon first. Defaults to the area this
    session was woken for, which is the only one it has any business in."""
    return _rows(ctx.conn.execute(
        "SELECT grain, grain_kind, fan_in FROM code_index WHERE area = ? "
        "ORDER BY fan_in DESC", (area or ctx.area,)))


@op("code", "source")
def code_source(ctx: Ctx, path: str, start: int = 0, end: int = 400) -> dict:
    """
    Read source, by path and line range. Given a directory it returns the
    listing instead — which is how you find a file worth reading when all you
    have is the area you were woken for.

    Structural review was asking Architect to judge whether a change satisfies a
    constraint while giving it only the code *index* — grain names and fan-in
    counts. That is a collision detector wearing a reviewer's title.

    It reads from the batch's worktree when there is one, and the project root
    otherwise. Same act either way, so it is one verb: which tree you are
    standing in is context, not a different operation. Developer reading its own
    uncommitted work and Architect reading the mainline are the same question
    asked from two places.
    """
    target = _within(_worktree_of(ctx), path)
    if not target.exists():
        return {"path": path, "error": "not found"}

    # A survey session is woken *for an area*, and an area is a directory -- so
    # the one path it holds before reading anything is the one path this could
    # not read. A directory clears the `exists()` guard above and then raises
    # `PermissionError` out of `read_text`, which reached the model as an errno
    # and an absolute host path.
    #
    # That closed a loop over thirteen sessions on the second foreign
    # repository. `ctx.opened` stayed empty, so `model.amend` refused the
    # binding as unread and told the session to `code.source` the file first;
    # the session complied with the only path it had, which was this one. Every
    # `surveys.attest` then refused because nothing had been written. Each of
    # the three refusals was correct on its own, and together they were a dead
    # end: the instruction was followable and following it changed nothing.
    #
    # So answer what the session is really asking -- *what is in here* -- and
    # hand back the names that make the next call possible. Listing is not
    # reading, and `ctx.opened` stays untouched: whoever binds a grain still has
    # to open the file it lives in.
    if target.is_dir():
        stem = path.rstrip("/\\")
        stem = "" if stem in (".", "") else stem + "/"
        entries = sorted(target.iterdir(), key=lambda e: e.name)
        return {
            "path": path,
            "kind": "directory",
            "files": [stem + e.name for e in entries if e.is_file()],
            "directories": [stem + e.name for e in entries if e.is_dir()],
            "note": "A directory is a listing, not source. Read one of the "
                    "files above to see inside it -- and note that this "
                    "listing does not count as having read any of them.",
        }

    lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    end = min(end, len(lines))
    ctx.opened.add(_grain_path(path))
    return {"path": path, "start": start, "end": end,
            "text": chr(10).join(lines[start:end]), "lines": len(lines)}


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


def _worktree_of(ctx, batch_id=None) -> "Path":
    """
    The batch's worktree, or the project root when there is no batch.

    Developer always works inside one — one worktree per batch, one PR per batch
    — and a write that landed in the project root instead would be a change
    nobody reviewed on a branch nobody merged.
    """
    from pathlib import Path as _P

    from ..core.worktrees import project_root

    bid = batch_id or ctx.batch_id
    if bid:
        row = ctx.conn.execute(
            "SELECT worktree FROM batches WHERE id = ?", (bid,)).fetchone()
        if row and row["worktree"]:
            return _P(row["worktree"])
    return project_root(ctx.conn)


def _grain_path(grain: str) -> str:
    """
    The file a grain lives in, normalised for comparison.

    Grains come in two shapes — `oauth1/rfc5849/signature.py` and
    `oauth1/rfc5849/signature.py::sign_hmac` — and a session that read the file
    has read the symbol. Backslashes fold to forward, because the index is built
    on one platform and read on another.
    """
    return grain.split("::", 1)[0].replace("\\", "/").strip().lstrip("./")


def _within(base, path: str):
    """Resolve `path` under `base`, refusing anything that escapes it."""
    target = (base / path).resolve()
    if not str(target).startswith(str(base.resolve())):
        raise ValueError(f"{path!r} escapes the worktree")
    return target


@op("code", "read")
def code_read(ctx: Ctx, batch_id: str | None = None) -> dict:
    """
    The batch diff. Critic's entire view of the implementation.

    It used to return the batch row — id, worktree, head_commit — under this
    same docstring, so the role whose whole job is judging a diff was being
    handed three identifiers. The diff is computed from git, which is where
    diffs come from.
    """
    from ..core import worktrees

    bid = batch_id or ctx.batch_id
    row = ctx.conn.execute(
        "SELECT id, worktree, head_commit FROM batches WHERE id = ?", (bid,)).fetchone()
    if not row:
        return {}
    out = dict(row)
    if row["worktree"]:
        out["diff"] = worktrees.diff(row["worktree"])
        out["touched"] = worktrees.touched(row["worktree"])
    else:
        out["diff"] = ""
        out["note"] = "the batch has no worktree yet"
    return out


@op("code", "write")
def code_write(ctx: Ctx, path: str, text: str) -> dict:
    """
    Write one file, whole, in this batch's worktree.

    Whole-file rather than patch-shaped, deliberately. A patch that does not
    apply is a failure the model must be told about and re-derive from, and
    small models are far worse at producing a valid hunk than a correct file.
    The diff is computed by git afterwards.

    Not staged through `ctx.writes`: the filesystem is outside the transaction,
    which is the carve-out law 4 already makes for the codebase. A session that
    writes and then dies leaves the worktree ahead of the database, and boot
    reconciles the two.
    """
    target = _within(_worktree_of(ctx), path)
    target.parent.mkdir(parents=True, exist_ok=True)
    existed = target.exists()
    target.write_text(text, encoding="utf-8")
    return {"path": path, "bytes": len(text.encode("utf-8")),
            "created": not existed}


@op("code", "commit")
def code_commit(ctx: Ctx, message: str) -> dict:
    """
    Commit the worktree, and record the sha the database now knows about.

    Commit as you go. An uncommitted change never existed: preemption discards
    the checkpoint and keeps the commits, so anything uncommitted is the only
    work a reorder can actually destroy.

    `committed: false` on an empty tree is not a failure. A session that read,
    reasoned and concluded the code was already right has nothing to commit, and
    an empty commit invented to have something to report would be worse.
    """
    from ..core import worktrees

    if not ctx.batch_id:
        raise ValueError("no batch: a commit belongs to one")
    tree = _worktree_of(ctx)
    sha = worktrees.commit(tree, message)
    if sha is None:
        return {"committed": False, "why": "nothing changed"}

    ctx.writes.append(("batches", ctx.batch_id, {"head_commit": sha}, False))
    return {"committed": True, "head_commit": sha,
            "touched": worktrees.touched(tree)}


# ---------------------------------------------------------------------------
# references + web (Researcher) — the one reach outside the engagement
#
# The Researcher owns `references` and writes nothing else. A row here is inert:
# it enters the model only when a role that owns an artefact cites it, which is
# what makes "the internet cannot widen the model" structural rather than a rule
# somebody has to keep.
# ---------------------------------------------------------------------------

@op("web", "fetch")
def web_fetch(ctx: Ctx, url: str, looking_for: str = "") -> dict:
    """
    One passage from one page. `looking_for` picks which passage.

    Never the whole page. An RFC is longer than the working set and four
    paragraphs of it answer the question — the same index/body split that keeps
    a working set viable over a large codebase keeps one over a large document.

    Reachable domains are `research_allowlist`, which is empty by default: a
    capability that reaches outside the engagement is granted, never merely
    not-forbidden. A refusal is not a failure to recover from, it is a fact to
    report back to whoever asked.
    """
    import os

    from ..core import config, web

    fetched = len([c for c in getattr(ctx, "fetches", [])])
    cap = config.get(ctx.conn, "research_cap")
    if fetched >= cap:
        return {"url": url, "refused": f"research_cap of {cap} fetches is spent; "
                                       f"answer with what you have"}
    try:
        # Cache-only unless the network is asked for explicitly. The default is
        # the safe direction: a test suite that could reach out would eventually
        # reach out by accident, and then one machine's results stop matching
        # another's for a reason nobody can see in the diff.
        page = web.fetch(ctx.conn, url,
                         config.get(ctx.conn, "research_allowlist"),
                         offline=not os.environ.get("ROTA_NET"))
    except web.NotAllowed as exc:
        return {"url": url, "refused": str(exc)}
    except Exception as exc:                       # unreachable, timed out, 404
        return {"url": url, "refused": f"could not read it: {exc}"}

    if not hasattr(ctx, "fetches"):
        ctx.fetches = []
    ctx.fetches.append(url)
    fragment = url.split("#", 1)[1] if "#" in url else ""
    return {"url": url, "content_hash": page["content_hash"],
            "passage": web.extract(page["body"], looking_for, fragment)}


@op("references", "record")
def references_record(ctx: Ctx, id: str, url: str, claim: str,
                      quote: str = "") -> dict:
    """
    What a source says, and where — one row, so two roles citing the same clause
    point at the same thing and one page changing is one drift event.

    `quote` is the passage the claim rests on. Everywhere else in this system
    conclusions travel and reasoning stays home; for an outside source the
    passage *is* the evidence, and without it nobody can check whether this was
    read correctly.
    """
    from ..core import web

    page = web.cached(ctx.conn, url) or web.cached(ctx.conn, url.split("#", 1)[0])

    # Who wanted to know, not who looked it up. Derived from the message that
    # woke this session rather than asked for: the Researcher has no reason to
    # know it is being attributed, and one that guessed would file the row under
    # itself every time — which is what this did before, making `asked_by`
    # constant and therefore useless.
    asker = ctx.role
    if ctx.trigger:
        row = ctx.conn.execute(
            "SELECT from_role FROM messages WHERE id = ?", (ctx.trigger,)).fetchone()
        if row:
            asker = row["from_role"]

    ctx.writes.append(("references_", id, {
        "url": url, "claim": claim, "quote": quote or None,
        "content_hash": (page or {}).get("content_hash", ""),
        "asked_by": asker}))
    return {"id": id, "url": url}


@op("references", "load")
def references_load(ctx: Ctx, ids: list[str] | None = None) -> list[dict]:
    """Sources on offer, or the ones a question came back with. Index depth:
    the claim and its URL, never every quote at once."""
    if ids:
        marks = ", ".join("?" for _ in ids)
        return _rows(ctx.conn.execute(
            f"SELECT id, url, claim, quote, asked_by FROM references_ "
            f"WHERE id IN ({marks}) ORDER BY id", ids))
    return _rows(ctx.conn.execute(
        "SELECT id, url, claim, asked_by FROM references_ ORDER BY id"))
