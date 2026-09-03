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

import difflib
import json as _json

import re

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
    # The rows this session was woken about, as the wake named them.
    #
    # `area` is the same idea for a survey: the scheduler decides the subject
    # and the role never guesses it. `term_collision` had no equivalent, so the
    # only place its subject appeared was the `Refs:` line -- and the line above
    # it reads "You were woken by: tick:term_collision". Measured on `cnt_q`: a
    # session woken for `['template', 'template#src_intents', ...]` called
    # `glossary.synthesise(ids=['tick', 'tock'], sense_short='a unit of time')`.
    # It defined `tick`, off the wake kind, forty-two times.
    wake_refs: tuple = ()
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
    # Terms this session looked up and did not find. The session already knows
    # it found nothing; nothing asked it, and that is the difference between
    # "there is nothing to add" being true and being an exit.
    lookup_misses: set = None
    # The words this session has actually read, taken from the text of every
    # grain it opened. `opened` answers "did you read a file"; a glossary term
    # needs the narrower "did you read a file that uses this word", because
    # opening one file and defining eight words off it is the shape that
    # produced `intent: a specific action or goal` on a plugin where an intent
    # is a note-creation recipe declared in frontmatter.
    read_words: set = None
    # The identifiers and paths this session has actually been shown --
    # `intents_to`, `TemplateVariableType`, `src/intents/index.ts` -- as the
    # code spells them. `read_words` is the decomposed vocabulary; this is the
    # other grain, for the one check that needs it: a definition saying *where*
    # a word is written down has to name a place that was in front of it.
    read_idents: set = None
    # Calls this session made that were refused: (label, reason). The session
    # already knows; nothing asked it. `surveys.attest` needs it to tell "wrote
    # nothing because there was nothing" from "wrote nothing because the
    # write was refused" -- the first is `none_found`, the second is not a
    # result at all and must not close the subject.
    refusals: list = None
    # What the concordance found settles the word, for the define guard:
    # {"enum": name, "siblings": [...], "members": [...], "options": [...]}.
    # A word the code declares as a member of an enum is defined by that enum
    # and its siblings; an enum is defined by its members; an option a user
    # writes is defined among the other options. The session was shown these
    # and the guard asks that the sense carry at least one of them.
    kind_facts: dict = None

    def __post_init__(self):
        if self.writes is None:
            self.writes = []
        if self.outbound is None:
            self.outbound = []
        if self.opened is None:
            self.opened = set()
        if self.read_words is None:
            self.read_words = set()
        if self.lookup_misses is None:
            self.lookup_misses = set()
        if self.read_idents is None:
            self.read_idents = set()
        if self.refusals is None:
            self.refusals = []
        if self.kind_facts is None:
            self.kind_facts = {}


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


class Wall(ValueError):
    """A refusal that is a fact about the harness, not a judgement about the
    work: the thing refused could not pass against any code. The derived
    reask keys on this class, not on the wording of the message -- the
    messages are rewritten freely and the state machine must not care."""


def _same_words(a: str, b: str) -> bool:
    """
    Two strings that say the same thing in the same order.

    Case, punctuation and line-folding are all differences a copy acquires for
    free -- both measured sessions capitalised the first word and meant nothing
    by it, and a criterion stored across two lines of YAML arrives with its
    break in a different place. Word order is kept, because the check is for a
    restatement and not for an overlapping vocabulary: a real test can be built
    entirely out of the criterion's own nouns.
    """
    import re as _re
    norm = lambda s: _re.findall(r"[a-z0-9]+", (s or "").lower())   # noqa: E731
    return bool(norm(a)) and norm(a) == norm(b)


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

    Found by L1: a Vision Keeper session ruled on an item id it had invented, and
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


# ---------------------------------------------------------------------------
# Intake gives one answer.
#
# The principal says one thing and Liaison decides what it is: chat, a question
# about the program as it already is, or work. Three answers, exclusive by the
# brief and until now by nothing -- chat and ratification were reconciled at
# commit by discarding the segmentation, and routing sat outside the rule
# entirely, so a session could route a question and chat about it in the same
# breath. It did, five runs out of five.
#
# Which call loses is not a judgement. Across 42 recorded sessions that gave
# two answers, the first was the right one in all 42 and the second came on a
# wind-down turn, after the harness had already said the work was done. So the
# first answer stands and the second is refused, which costs a turn instead of
# a session's work.
# ---------------------------------------------------------------------------

def answers_given(ctx: Ctx) -> dict[str, str]:
    """
    Which of the three intake answers this session has given, and what it did.

    The description is carried rather than looked up because one answer has two
    ways of being given: work is segmenting *or* asking the principal to
    confirm. Named from a table, the refusal told a session that had only sent
    a confirm that it "had already segmented this into statements" -- work it
    had not done, which leaves it no way back to the work it should have.
    """
    given: dict[str, str] = {}
    for m in ctx.outbound:
        if m["verb"] == "converse" and m["to_role"] == "principal":
            given["chat"] = "replied to the principal"
        elif m["verb"] == "ask":
            given["inquiry"] = "asked an owner about this"
        elif m["verb"] == "confirm" and m["to_role"] == "principal":
            given["work"] = "asked the principal to confirm a segmentation"
    if any(w[0] == "statements" for w in ctx.writes):
        given["work"] = "segmented this into statements"
    return given


def refuse_second_answer(ctx: Ctx, answer: str) -> None:
    """Raise if this session has already answered the principal another way."""
    others = {k: v for k, v in answers_given(ctx).items() if k != answer}
    if others:
        was = others[sorted(others)[0]]
        raise ValueError(
            f"you have already {was}, which is one answer to what the "
            f"principal said. This is a different one, and sending both "
            f"leaves them holding two. Your work here is done")


@op("brief", "intake")
def brief_intake(ctx: Ctx, verdict: str) -> dict:
    """
    The branch claim at intake: chat or work, never both silently.

    S0's blocker, measured live: handed "Hello, Please build a python
    script...", the converse session answered the greeting and closed --
    zero statements, the request gone. The greeting-handling brief patch was
    prose and lost, prose's fourth loss this month. Same cure as the
    Tester's fork: the judgment becomes an act. `work` means the reply must
    carry refs to what intake produced; `chat` means a bare reply is legal.
    Two verdicts only -- the taxonomy lesson says never three.
    """
    if not hasattr(ctx, "intake"):
        ctx.intake = None
    ctx.intake = verdict
    nxt = {
        "work": "they asked for something: brief.segment each thing asked "
                "for (their words, spans of the entry), then "
                "msg.confirm_principal with the statement ids. Your reply "
                "carries refs; a bare reply is refused",
        "chat": "no work was asked for: msg.converse_principal replies in "
                "words, refs may be empty",
    }[verdict]
    return {"verdict": verdict, "next": nxt}


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
    refuse_second_answer(ctx, "work")

    # You cannot ratify a question. Handed "remind me, what did we decide
    # about invoice retention?", intake segmented it into three statements
    # and sent the principal their own question back to confirm -- five runs
    # of five. A statement is a claim the principal made; the sentence a span
    # lands in ending in a question mark means they asked, and asking is
    # answered or routed, never proposed back for ratification.
    row = ctx.conn.execute("SELECT text FROM entries WHERE id = ?",
                           (target,)).fetchone()
    if row and row["text"]:
        # The span's sentence is the one its start lands in: the first
        # terminator at or after span_start closes it. Anchoring at the end
        # misjudged a span that sloppily overshot its own full stop.
        source = row["text"]
        stop = len(source)
        for mark in (".", "!", "?"):
            k = source.find(mark, max(0, min(span_start, len(source))))
            if k != -1:
                stop = min(stop, k)
        if stop < len(source) and source[stop] == "?":
            raise ValueError(
                "that span is a question, and a question is never a "
                "statement to ratify. Answer it -- msg.converse_principal "
                "with the rows that answer it in refs -- or ask the owner "
                "whose artefact holds the answer")


    # The same span twice is the same statement twice, whatever id it is given.
    #
    # The ids are the model's, so nothing collided and nothing complained:
    # `L1-LI-segment` produced twenty-four statements from one sentence, which
    # were three statements issued eight times, and passed 5/5 because the case
    # asserted `count: ">=1"`. Every one of them would have gone to the
    # principal to ratify and to three roles to work from.
    #
    # Reported rather than refused, on `tests.encode`'s precedent: the session
    # is not doing anything wrong by arriving at the same segmentation, and an
    # error would invite it to invent a different one.
    same = [w for w in ctx.writes
            if w[0] == "statements"
            and w[2].get("span_start") == span_start
            and w[2].get("span_end") == span_end
            and w[2].get("span_entry") == target]
    if same:
        return {"id": same[0][1], "unchanged": True,
                "note": "this span is already segmented, as "
                        f"{same[0][1]}; nothing was written."}

    # Segmenting is not interpreting, and the span is what makes that checkable.
    # A statement whose text is not in the entry is one the principal never
    # said -- a live run produced "and also fix the login timeout" against a
    # sentence about SSO and LDAP. The span was always the way back to their
    # words; nothing had ever looked through it.
    row = ctx.conn.execute(
        "SELECT text FROM entries WHERE id = ?", (target,)).fetchone()
    if row is not None and text.strip() and text.strip() not in row["text"]:
        raise ValueError(
            f"{text.strip()[:60]!r} does not appear in the entry you are "
            f"segmenting. A statement is a span of what they said, so its text "
            f"has to be their words -- the entry reads: {row['text'][:120]!r}")

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
    the plateau is achieved by scoping, not by deleting.

    `span_entry` travels because it is the only way back to what the principal
    actually said. It is an id and not prose, so law 2 is untouched: the
    conclusion travels, and whoever needs the words follows the id into
    `transcript.quote` — which several briefs already instruct and none could
    obey, because nothing handed out an entry id.
    """
    return _rows(ctx.conn.execute(
        "SELECT id, text, status, span_entry FROM statements "
        "WHERE status = 'ratified' AND version > ? ORDER BY id", (since_version,)))


# ---------------------------------------------------------------------------
# problem statement
# ---------------------------------------------------------------------------

@op("problem", "assert")
def problem_assert(ctx: Ctx, id: str, text: str, kind: str = "in_scope") -> dict:
    """
    An item, and the one judgement this call exists to make: in scope or out.

    A session may not make both about the same item. `L3-ratified-statement-
    becomes-scope` passed 5/5 while recording seventeen writes to `items` from
    one ratified statement, and reading the calls back showed
    `problem.assert(id="invoice_retention", kind='in_scope')` followed by the
    same id at `out_of_scope`. Both staged, the last won at commit, and the
    case's `count: ">=1"` was satisfied by seventeen. Which answer reached the
    database was decided by list order, which is not a judgement.

    Restating the same scope stays allowed. That is a role repeating itself,
    it costs nothing, and there is nothing for it to correct -- the same
    reasoning as the byte-identical re-encode in `tests.encode`.
    """
    prior = [w for w in ctx.writes
             if w[0] == "items" and w[1] == id and "kind" in w[2]]
    clash = next((w for w in prior if w[2]["kind"] != kind), None)
    if clash is not None:
        raise ValueError(
            f"you have already put {id} {clash[2]['kind']} in this session and "
            f"this says {kind}. Those are the two answers this call chooses "
            f"between, so both is not an answer; decide, and send the one")

    # An item named after a grain is a sentence about that grain.
    #
    # `items.yaml` in the cnt key states the test an item passes -- "it says
    # something about the product that a reader could act on, and it would still
    # be true if every identifier were renamed" -- and warns about the failure
    # by name: "A sentence about a function is not an item." The vision_keeper
    # brief says the same thing in its own words, that a behaviour composed from
    # names is a guess wearing an observation's provenance. Prose, and nothing
    # held it.
    #
    # Measured on `cnt_i`, the first run in nine to reach this role at all: of
    # eight items, `id='src/variables/index.ts'` and `id='getRelativePath'`
    # ("Returns the relative path of a given path"). Both are grains. The other
    # six -- `release_workflow`, `settings_behaviour`, `intent-processing` --
    # are not, and all six are about the product.
    #
    # The id is the check because the id is where it shows. Renaming does not
    # catch it: rename `getRelativePath` to anything and "returns the relative
    # path" stays true, which is exactly why it says nothing about this product.
    # Naming the item after the code is the tell.
    if ctx.conn.execute(
            "SELECT 1 FROM code_index WHERE grain = ? OR grain LIKE ?",
            (id, f"%::{id}")).fetchone():
        raise ValueError(
            f"{id!r} is a grain in the index, so this is a sentence about a "
            f"file or a function. An item says what the *product* does -- one a "
            f"reader could act on, still true if every identifier in the "
            f"repository were renamed. `release_workflow` and "
            f"`settings_behaviour` are items; `getRelativePath` is a signature. "
            f"Name the behaviour, not the code you found it in.")

    # The same sentence under a second id is the same item. The no-prose
    # orientation wrote its five behaviours on turn one and wrote them again
    # on turn two as `user_writes_intents`, `program_reads_intents`, ... --
    # ten items, five of them. Restating costs nothing and is not refused;
    # it is answered with the id the item already has.
    words = _words_in(text)
    norm = " ".join(words)
    if norm:
        for t, i, vals, *_ in ctx.writes:
            if t == "items" and i != id and " ".join(_words_in(vals.get("text") or "")) == norm:
                return {"id": i, "note": f"already an item as {i!r}; not written twice"}
        for r in ctx.conn.execute("SELECT id, text FROM items WHERE id <> ?", (id,)):
            if " ".join(_words_in(r["text"] or "")) == norm:
                return {"id": r["id"], "note": f"already an item as {r['id']!r}; not written twice"}

        # A restatement is not always a *repeat* of the words -- an item found
        # on an empty project drifted round to round ("do not ask for X" ->
        # "the software will not ask for X in any script") while staying the
        # same claim, and the exact check above cannot see it: different
        # words, same meaning, so it never once matched and the same claim
        # landed under five separate ids. Word-set overlap catches the drift.
        # `_prose_words`, not `_words_in`: the latter's stoplist drops "name"
        # and "show" as identifier noise, which are the two words that
        # separate "ask for a name" from "show a greeting" here. Scoped to
        # the same `kind` -- overlapping vocabulary between an in-scope and
        # an out-of-scope claim is evidence they share a subject, not that
        # they are one claim.
        prose = _prose_words(text)
        for t, i, vals, *_ in ctx.writes:
            if (t == "items" and i != id and vals.get("kind") == kind
                    and _near_duplicate(prose, _prose_words(vals.get("text") or ""))):
                return {"id": i, "note": f"close enough to {i!r} to be the same "
                        f"item ({vals.get('text')!r}) -- not written twice"}
        for r in ctx.conn.execute(
                "SELECT id, text FROM items WHERE id <> ? AND kind = ?", (id, kind)):
            if _near_duplicate(prose, _prose_words(r["text"] or "")):
                return {"id": r["id"], "note": f"close enough to {r['id']!r} to be "
                        f"the same item ({r['text']!r}) -- not written twice"}

    # The item's own words are not an amendment. S0 walk thirty-one: the
    # Vision Keeper, at the top of the exhausted ladder, re-asserted the
    # item verbatim; the version moved, the revocation predicate read a
    # withdrawn approval, and the batch with three green tests was
    # cancelled. Restating is free; it just is not a write.
    cur = ctx.conn.execute("SELECT text, kind FROM items WHERE id = ?",
                           (id,)).fetchone()
    if cur and cur["kind"] == kind and _same_words(text, cur["text"]):
        return {"id": id, "unchanged": True,
                "note": "those are the item's own words and its own kind; "
                        "nothing was written and no version moved"}
    # The intent thread's first link. An item is a reading of something the
    # principal said; the pair table that records *which* statement had a
    # reader (`problem.consult` returns `from_statements`), a docstring
    # quoting a role asking for it, and no writer -- so the refs road from
    # any artefact back to the principal's words ended one hop from the
    # top, in every walk. Mechanical: the statements this session was woken
    # about are what this item reads.
    for ref in getattr(ctx, "wake_refs", ()) or ():
        if ctx.conn.execute("SELECT 1 FROM statements WHERE id = ?",
                            (ref,)).fetchone():
            ctx.writes.append(("item_statements", f"{id}:{ref}", {
                "item_id": id, "statement_id": ref}))
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
    """
    Every row at index depth: ids, kind and approval, no prose bodies.

    `from_statements` is part of this artefact -- `problem` is
    `("items", "item_statements")` -- and was the half nothing returned. An
    item is a reading of something the principal said, and a Vision Keeper woken
    on a contested one is told by its brief to `transcript.quote` what they
    actually said. It holds one id, the item's. An exit interview put it
    plainly: "I needed to know what the principal said they meant instead, but
    that information was not available."

    Ids, not prose, so law 2 is untouched. The hop is
    item -> statement -> `span_entry` -> entry, and every edge of it was
    already granted; only the columns were missing.
    """
    rows = _rows(ctx.conn.execute(
        "SELECT id, kind, approval, approval_ver, version, substr(text, 1, 120) AS headline "
        "FROM items ORDER BY id"))
    derives: dict[str, list[str]] = {}
    for r in ctx.conn.execute(
            "SELECT item_id, statement_id FROM item_statements ORDER BY item_id"):
        derives.setdefault(r["item_id"], []).append(r["statement_id"])
    for row in rows:
        row["from_statements"] = derives.get(row["id"], [])
    return rows


@op("problem", "baseline")
def problem_baseline(ctx: Ctx) -> list[dict]:
    """
    What the program does, as observed: the orientation, whole.

    The define and survey phases are written with this in front of them, and
    it is the one context that measurably displaces the everyday reading of a
    word -- handed the call trace, the model kept "an intent is a user's goal";
    handed the account of what the program does for its user, it wrote "a
    recipe for making a note". `problem.consult` is the index line, cut at 120
    characters, and an account cut in half is not an account.

    A query, not the artefact: observed items only, which during onboarding is
    the baseline the Vision Keeper wrote from the program's front and during
    delivery is the part of the model that was found rather than decided.
    Non-owners read it whole because it is the phase's output being handed to
    the next phase, which is what "shared state must be artefacts" is for.
    """
    return _rows(ctx.conn.execute(
        "SELECT id, text FROM items WHERE provenance = 'observed' "
        "AND kind = 'in_scope' ORDER BY id"))


# ---------------------------------------------------------------------------
# glossary
# ---------------------------------------------------------------------------

def _slug_of(term: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (term or "").strip().lower()).strip("_")


def _singular(slug: str) -> str:
    """`intents` -> `intent`, by the rule `_words_in` already uses on identifiers."""
    if slug.endswith("ies") and len(slug) > 5:
        return slug[:-3] + "y"
    if slug.endswith("s") and not slug.endswith("ss") and len(slug) > 4:
        return slug[:-1]
    return slug


def _same_sense(text: str) -> str:
    """Two senses read as one when the index line reads the same.

    Case, spacing and a trailing full stop are not a distinction a reader of
    the glossary index can act on, so they are not one here either.
    """
    import re
    return re.sub(r"\s+", " ", (text or "").strip().lower()).strip(" .;:,")


# ---------------------------------------------------------------------------
# The observed exit. Law 11: an observed row is found, not chosen, and its
# first decision is forced by a challenge -- or granted, here, by the
# principal confirming it. Validation 3 calls this "`observed` becomes decided
# where they said so", and until these existed it was true of items only:
# the ruling path ended at `problem.set_approval` and the other three tables
# had no operation anywhere that could write `provenance='decided'`. Once a
# present was answered, `observed_entries` saw the same rows and fired again.
#
# Adoption is not authorship. The row's content is untouched -- what changes is
# who stands behind it, which is exactly what provenance records. Only rows
# the ruling names may move: the ruling is on the wake's cause chain, the same
# place `principal_verdict` comes from, so the op can check rather than trust.
# ---------------------------------------------------------------------------

def _ruled_ids(ctx: Ctx) -> set[str] | None:
    """The ids the principal's ruling approves, off this wake's cause chain.

    None when the wake carries no ruling at all -- distinct from a ruling that
    approves nothing, which is an empty set.
    """
    from .principal import verdict_for

    trigger = getattr(ctx, "trigger", None)
    if not trigger:
        return None
    seen = set()
    mid = trigger
    while mid and mid not in seen:
        seen.add(mid)
        verdict = verdict_for(ctx.conn, mid)
        if verdict:
            return {i for i, ruling in verdict.items()
                    if ruling in ("approve", "approved", "confirm", "confirmed")}
        row = ctx.conn.execute(
            "SELECT cause_id FROM messages WHERE id = ?", (mid,)).fetchone()
        mid = row["cause_id"] if row else None
    return None


def _adopt_rows(ctx: Ctx, table: str, ids: list[str]) -> dict:
    if not ids:
        raise ValueError("adopt names the rows the principal approved, and "
                         "you named none")
    ruled = _ruled_ids(ctx)
    out, skipped = [], []
    for rid in ids:
        row = ctx.conn.execute(
            f"SELECT provenance FROM {table} WHERE id = ?", (rid,)).fetchone()
        if row is None:
            raise ValueError(f"{rid!r} is not a row of {table}; adopt what "
                             f"the ruling names, from the refs you were given")
        if ruled is not None and rid not in ruled:
            # The ruling is on file and does not approve this row. Skipped
            # rather than refused: the ruling names what it names, and a
            # session listing one extra id should not lose the ones ruled on.
            skipped.append(rid)
            continue
        if row["provenance"] != "observed":
            skipped.append(rid)
            continue
        ctx.writes.append((table, rid, {"provenance": "decided"}, False))
        out.append(rid)
    result = {"adopted": out}
    if skipped:
        result["skipped"] = skipped
        result["note"] = ("skipped rows are not observed, or the ruling does "
                          "not approve them; they are unchanged")
    return result


@op("glossary", "adopt")
def glossary_adopt(ctx: Ctx, ids: list[str]) -> dict:
    """The principal approved these observed senses; the project adopts them."""
    return _adopt_rows(ctx, "glossary_terms", ids)


@op("model", "adopt")
def model_adopt(ctx: Ctx, ids: list[str]) -> dict:
    """The principal approved these observed constraints or areas."""
    both = {"constraints": [], "model_areas": []}
    for rid in ids:
        table = ("constraints" if ctx.conn.execute(
            "SELECT 1 FROM constraints WHERE id = ?", (rid,)).fetchone()
            else "model_areas")
        both[table].append(rid)
    merged: dict = {"adopted": [], "skipped": []}
    for table, tids in both.items():
        if not tids:
            continue
        r = _adopt_rows(ctx, table, tids)
        merged["adopted"] += r["adopted"]
        merged["skipped"] += r.get("skipped", [])
    if not merged["skipped"]:
        merged.pop("skipped")
    return merged


@op("glossary", "amend")
def glossary_amend(ctx: Ctx, term: str, sense_body: str = "",
                   sense_short: str = "", sense: str = "") -> dict:
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

    That argument turned out to be payable by accident. On the icalendar run a
    survey session wrote `Alarm`, and a later one wrote `alarm` with
    `sense="observed"` — the word the brief puts in front of it twice on the
    same page, *"everything you write here is `observed`, not `decided`"* — and
    bought a second row with the sense_short character-for-character identical
    to the first. Three words did it: alarm, calendar, component. The brief
    already ruled on this: **"the same sense twice is not two senses"**, and a
    `sense` you have not actually distinguished "puts a collision in the record
    that does not exist". Prose, and nothing holding it — so `term_collision`
    duly raised three, and every one of them was a phantom.

    So `sense` now has to buy something. It names a second meaning, and a second
    meaning is one that differs from the first; when it does not, the call is an
    amendment wearing an argument, and it is taken as the error it is rather
    than written as the collision it is not.

    **The explanation comes first and the one-liner after it**, which is why the
    arguments are in this order. `sense_short` used to be asked for first, and a
    field called "short" asked for before any explanation exists reads as a
    request for a *label*. That is exactly what came back, on the Obsidian
    plugin, across 57 calls:

        term='github'      sense_short='repository'    sense_body='a collection of files…'
        term='repository'  sense_short='data storage'

    github is a repository, repository is data storage — a taxonomy, not a
    meaning, and the definition pushed into the body where the index never shows
    it. Then a later session took the label it found in `sense_short` and passed
    it as `sense=` with the short left empty, which minted `github#repository` as
    a second row, and `term_collision` spent 44 of that run's 71 turns on the
    word. Asked *after* the explanation, the short one is a summary of something
    already written rather than a category guessed at in advance.

    Both are required, and neither may be blank. A blank `sense_short` is not
    only a blank index line -- it is also what the second-sense check compares,
    so an empty one walked straight past the guard that exists to stop precisely
    the row it was creating. Declining to define a term stays free: not writing
    the row at all is always allowed, and a thin glossary of real meanings beats
    a full one of labels.
    """
    import re

    # `filteredOpenerApiGetListOfNoteFilterSets#src` -- a row *id* echoed back
    # as a term, because `[glossary.consult]` prints ids and a second-area row
    # is `word#area`. The id is derived and never the role's to write; the
    # word is what precedes the `#`.
    if "#" in term:
        term = term.split("#", 1)[0]
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
    if not (sense_body or "").strip():
        raise ValueError(
            f"{term!r} has no sense under it. A glossary of words is the index "
            f"with the columns relabelled -- say what the word means here, in "
            f"the sense this area uses it, or leave it out. `sense_body` is "
            f"where that goes: what it does, what this project means by the "
            f"word, what would break if it meant the other thing.")

    if not (sense_short or "").strip():
        raise ValueError(
            f"{term!r} has a body and no `sense_short`. That is the one line "
            f"every reader of the glossary index is shown, and every session "
            f"after you sees it and nothing else -- a blank one is a term "
            f"nobody downstream can use. Summarise what you just wrote in a "
            f"clause: not a category the word belongs to, which is how "
            f"'github' came to mean 'repository', but what it means.")

    # A word is defined by the code that uses it, and this was the one artefact
    # write in the system that did not say so. `model.amend` has refused to bind
    # a constraint to an unread grain since law 12 -- "you cannot have found one
    # in a file you did not read" -- and `surveys.attest` refuses a citation for
    # a grain nobody opened. The glossary, which every role downstream inherits
    # as fact, had neither.
    #
    # Measured: a session woken for `src/intents` called `code.source` once, on
    # the directory -- which returns a listing and deliberately leaves `opened`
    # untouched, because listing is not reading -- and then wrote `intent`,
    # `note` and `template`. `intent` came out as "a specific action or goal",
    # which is what the word means in English and not what it means here. The
    # brief said "open a grain before you define a word in it". Prose asks.
    #
    # Against the words actually read rather than against reading in general,
    # and from the same decomposition `code.vocabulary` ranks by, so the block
    # cannot offer a word this then refuses. Opening one file and defining eight
    # words off it is the shape this stops.
    # The frame is not vocabulary, and the read gate said so in the wrong words.
    #
    # `d`'s brief asks for "the words your account needed", and the account is
    # written in the frame's words because the prompt is: "MODE: survey — this
    # area's code", "what this area does". Measured on `cnt_k`, all three
    # sessions on `.github` opened with *"This area appears to be a survey of
    # the `.github` directory"* and then tried to define `survey` and `area`.
    #
    # The read gate refused them — correctly, and with "nothing you read this
    # session says 'survey'", which is true and reads as *read more*. So they
    # read more, tried again, and the area was quarantined on the third attempt
    # having produced one term. `.github` legitimately has almost no project
    # vocabulary and `none_found` was the right ending the whole time.
    #
    # Same refusal, said as what it is, and pointing at the ending that was
    # available. `_FRAME_WORDS` is the list already earned by `sense=`.
    # The subject of a define session is one word, decided by the scheduler.
    #
    # The wake names the word; the session defines it. A session that defines
    # some other word has done a different session's work and left its own
    # undone -- the wake fires again, and the word it wrote is one nobody
    # asked for, which is how off-key entries arrive. The common honest case
    # is a spelling: woken for `template variable type` the model writes
    # `TemplateVariableType`, the project's own spelling of the same words,
    # and that is filed under the word the wake named, with a note.
    from ..core.scheduler import is_area, term_of

    subject = term_of(ctx.area) if ctx.area else ""
    if subject:
        same = (_singular(slug) == _singular(_slug_of(subject))
                or (set(_words_in(term)) and
                    set(_words_in(term)) == set(_words_in(subject))))
        if not same:
            raise ValueError(
                f"this session is about {subject!r} and nothing else; "
                f"{term!r} is not that word. Define {subject!r} from the "
                f"concordance, or `surveys.attest(outcome='none_found')` if "
                f"this project means nothing of its own by it.")
        if slug != _slug_of(subject):
            filed_under = subject
            term, slug = subject, _slug_of(subject)
        else:
            filed_under = ""
        # A definition says where the word is written down, by name. Every
        # entry the answer key holds does -- `intents_to`, `with_prompts`,
        # `of_type`, a file -- and every generic entry a define session has
        # produced does not: "a note's purpose or goal", "a category of note
        # organization", "a type used to create notes based on user input".
        # The brief asks for it in prose and prose was inert, so the sense has
        # to name at least one identifier or path the concordance actually
        # showed. Not *which* -- a list of candidates in a refusal is the list
        # that gets transcribed -- only that one is named, spelled as the code
        # spells it.
        named = _idents_in(f"{sense_body} {sense_short}")
        placed = bool(named & ctx.read_idents) if ctx.read_idents else True
        # A file stem the concordance showed counts as a place: "declared in
        # the settings module" names `settings.ts` as surely as the path does,
        # and the model writes the word far more often than the path.
        if not placed:
            stems = {i.rsplit("/", 1)[-1].split(".")[0] for i in ctx.read_idents
                     if "/" in i or "." in i}
            placed = bool(set(_words_in(f"{sense_body} {sense_short}"))
                          & {w for st in stems for w in _words_in(st)} - set(_words_in(term)))
        already = sum(1 for fn, why, *_ in (getattr(ctx, "refusals", None) or [])
                      if fn == "glossary.amend" and "written down" in why)
        if not placed and not already:
            # Once. Measured: refused, the session opened the declaring file --
            # the nudge works that far -- and then re-sent the same sense for
            # eleven turns. A gate this model cannot satisfy is a loop that
            # loses the word; a flag it can read is a note on the row.
            raise ValueError(
                f"{term!r} is defined without saying where it is written "
                f"down. Name the key a user writes, or the type or file the "
                f"code declares, as the concordance spells it -- a sense that "
                f"names no place in this project is a sense from somewhere "
                f"else.")
        unplaced = not placed
        # A kind is defined by its kind. The concordance showed the session
        # that `note` is a member of `TemplateVariableType` beside `text`,
        # `number`, `natural_date` and `folder`, and an option of `of_type`
        # among the same five -- and the sense came back "a piece of
        # information to be stored". Measured on every run: the model read
        # the settling lines and summarised them away. So a sense for a word
        # the code declares as a kind has to carry the kind or a sibling, and
        # the sense of an enum has to name its members. Once, then flagged,
        # like every other guard here.
        facts = getattr(ctx, "kind_facts", None) or {}
        said = f"{sense_body} {sense_short}".lower()
        said_words = set(_words_in(said))
        unkinded = False
        def _names(m: str) -> bool:
            low = m.lower()
            return (low in said or low.replace("_", " ") in said
                    or (len(_words_in(m)) > 1 and set(_words_in(m)) <= said_words))

        if facts.get("members"):
            named_members = [m for m in facts["members"] if _names(m)]
            # All of them when there are few: "the five kinds a prompt may be"
            # is the sense of `TemplateVariableType`, and a sense that names
            # two of five has named a sample.
            want_n = len(facts["members"]) if len(facts["members"]) <= 8 else 2
            unkinded = len(named_members) < want_n
            ask = (f"name its members -- it is an enumeration of "
                   f"{len(facts['members'])}, and its members are what it means")
        elif facts.get("enum") or facts.get("options"):
            enum_words = set(_words_in(facts.get("enum") or ""))
            kin = [m for m in (facts.get("siblings") or []) + (facts.get("options") or [])
                   if _names(m)]
            unkinded = not ((enum_words and enum_words <= said_words) or kin)
            ask = (f"say what it is one of -- the kind the code declares it a member "
                   f"of, and at least one of the other kinds beside it")
        already_kind = sum(1 for fn, why, *_ in (getattr(ctx, "refusals", None) or [])
                           if fn == "glossary.amend" and "one of" in why)
        if unkinded and not already_kind:
            raise ValueError(
                f"{term!r} is a kind here, and the sense does not say so. "
                f"The concordance shows it declared as one of several; {ask}. A "
                f"sense that could be written without that is the everyday "
                f"word, not this project's.")
    else:
        filed_under = ""
        unplaced = False
        unkinded = False

    if slug in _FRAME_WORDS:
        raise ValueError(
            f"{term!r} is the frame you were woken in, not something this "
            f"project means by it — every repository would have the same entry, "
            f"which is the test a definition has to fail. Define what the code "
            f"calls its own things, and if this area names none, "
            f"`surveys.attest(outcome='none_found')` is a real answer and often "
            f"the right one.")

    # Only where there is code to have read. The gate was built for survey mode
    # -- "against the words actually read rather than against reading in
    # general" -- and fired in every mode, including the ones with no codebase
    # in front of them at all.
    #
    # `deliver` wakes the Terminologist on a ratified statement: "let users
    # delete their account", and the job is to say what `delete` means here. The
    # evidence is the statement, and there is nothing to `code.source`. Measured
    # on `L1-TE-amend-glossary`, 0 of 5 runs, every one refused with "nothing you
    # read this session says 'delete'" after producing a correct call. The case
    # had been stale since before today, so nothing reported it.
    #
    # `area` is the discriminator the context already carries: set by the
    # scheduler for a survey, `None` for every other mode.
    seen = getattr(ctx, "read_words", None) if ctx.area else None
    if seen is not None and slug.replace("_", " ") not in " ".join(seen):
        if _words_in(term) and not (set(_words_in(term)) & set(seen)):
            raise ValueError(
                f"nothing you read this session says {term!r}. A word means "
                f"what the code using it makes it mean, so a definition written "
                f"from a file that never says it is a definition from somewhere "
                f"else -- usually from the word itself. `code.vocabulary` names "
                f"the grain each word appears in; `code.source` that one. "
                f"Defining nothing is always allowed."
                + (f" You have opened {sorted(ctx.opened)[:2]}."
                   if ctx.opened else " You have opened nothing."))

    # A tag that slugifies to nothing is not a tag. Both branches below build
    # the id as `slug#tag`, and both could produce a bare trailing `#`:
    # `sense="  "` here, and area `.` -- the root area, which every repository
    # has -- in the area branch. Measured on cnt: `intent#`, which the session
    # then spent a whole `term_collision` wake failing to name. It looked the id
    # up as a *term* twice, called `glossary.same(keep='both')`, and reported to
    # the Liaison. An id nobody can type is an id nobody can discharge.
    # A plural is the same word. The id derivation promises that writing a word
    # twice amends it -- "accidental duplication is impossible", earned on
    # oauthlib where twelve sessions wrote `endpoint` five times -- and it was
    # never true across a plural, because the slug is not stemmed while
    # `_words_in` is.
    #
    # Measured on `cnt_l`: the session for `src/intents`, the area that declares
    # what an Intent *is*, wrote `intents`, `templates` and `variables`. Three
    # new rows beside `intent`, `template` and `variable`, saying the same
    # things in the same words about the same code, and three of the eight
    # terms that run wrote which are not in the key at all are exactly these.
    #
    # Only when the singular is already there. This does not decide that English
    # plurals are never distinct -- it declines to create a second row for one
    # when the first row exists, which is the same judgement the derivation
    # already makes for `Endpoint` and `endpoint`.
    # Either order. The first version mapped plural onto singular and only that,
    # so it depended on which spelling arrived first: `cnt_n`'s `src/intents`
    # session wrote `variables` before `variable`, there was no `variable` row to
    # amend, and both landed — with the same `sense_short`, "data types for
    # storing values in intents", in the same area, from the same reading.
    #
    # So the match is on the singular *family*, and the row that already exists
    # keeps its spelling whichever one it is. First writer names the word; the
    # second amends it.
    pending = {w[1] for w in ctx.writes if w[0] == "glossary_terms"}
    if slug not in pending:
        stem = _singular(slug)
        kin = [i for i in pending if _singular(i) == stem and "#" not in i]
        kin += [r["id"] for r in ctx.conn.execute(
            "SELECT id FROM glossary_terms WHERE id IN (?, ?)", (stem, stem + "s"))
            if r["id"] not in kin]
        if kin:
            slug = kin[0]

    ignored_sense = ""
    # A define session writes the first entry for its word, over the whole
    # program. There is no second sense to name yet, so a `sense=` here is the
    # escape hatch paid by accident -- measured on the first run of the phase:
    # `prompt#category`, `provider#category`, the word "category" being the
    # most available noun in a brief that says "a category and not a
    # meaning". Ignored, with a note, the same way a malformed tag is.
    if sense and subject:
        ignored_sense = (f"`sense={sense!r}` ignored: this is the first entry "
                         f"for {subject!r}, so there is no second sense to name.")
        sense = ""
    sense_tag = _slug_of(sense) if sense else ""
    # `sense` names a meaning, and in twelve runs it has never once named one.
    #
    # Every non-empty value ever passed, counted across every cnt database:
    # `area` x24, `code.area()` x5, `repository` x3, `data storage` x3,
    # `survey` x2, `error` x1, plus three whole sentences that swallowed
    # `, sense_body=` into themselves. Nine runs carry a row with a bogus tag --
    # `workflow#code_area_`, `templates#area`, `templates#survey`,
    # `github#repository`, `filteredopenermissingnotice#error`.
    #
    # They are all the same mistake and it is not carelessness: asked for a word
    # naming which sense this is, a session reaches for the most available noun,
    # and the most available nouns are the frame it was woken in and the tool it
    # just called. The escape hatch has a zero percent correct-use rate, and it
    # costs a real row and a real collision every time it is paid by accident.
    #
    # Shape, not vocabulary. A second sense is named in the project's words, in
    # a word or two -- `nonce`'s `binding` against its replay guard. A tool call,
    # the name of the mode, or a sentence is none of those.
    id = f"{slug}#{sense_tag}" if sense_tag else slug

    if sense_tag:
        raw = sense.strip()
        why_not = None
        if "(" in raw or "." in raw:
            why_not = (f"{raw!r} is a call, not a meaning")
        elif len(_words_in(raw)) > 3 or len(raw) > 40:
            why_not = (f"{raw!r} is an explanation, not a name for one -- that "
                       f"belongs in `sense_body`")
        elif ({slug, sense_tag} & (_FRAME_WORDS - _PROVENANCE_WORDS)):
            why_not = (f"{raw!r} is a word from the frame you were woken in, "
                       f"not something {term!r} means")
        if why_not:
            # Ignored, not refused. The first version of this raised, and the
            # session could not act on it: `cnt_m`'s `.github` sessions sent
            # `sense='survey'` and re-sent the identical call twelve times for
            # `templates` and nine apiece for two more, landing nothing. The
            # refusal ends with "drop `sense` and amend the entry you have" and
            # the model does not drop it.
            #
            # Dropping it is always the right reading anyway. Across twelve runs
            # `sense` has never once named a real second meaning, so a malformed
            # one carries no information to preserve -- and with it gone the
            # call is the plain amend it should have been. The duplicate-sense
            # guard above and the area rule below still decide whether this is
            # one row or two, which is the decision that actually matters.
            #
            # Said in the result rather than silently: a note the session can
            # read, on a write that landed.
            ignored_sense = f"`sense={sense!r}` ignored: {why_not}."
            sense_tag = ""
            id = slug          # the id was derived above; derive it again

    # A second sense must mean something the first does not. Compared on
    # `sense_short` because that is the line every downstream reader is shown --
    # two rows whose shorts match are indistinguishable in the index whatever
    # else differs, which is the whole harm. Pending writes count as well as
    # committed rows: a session can do this to itself inside one turn.
    if sense:
        # A row cannot collide with itself: writing this same id again is an
        # amendment of that row, and keeping its sense_short while changing the
        # body is exactly what an amendment looks like.
        seen = {_same_sense(r["sense_short"]): r["term"] for r in ctx.conn.execute(
            "SELECT id, term, sense_short FROM glossary_terms "
            "WHERE (id = ? OR id LIKE ? || '#%') AND id <> ?",
            (slug, slug, id))}
        seen.update({_same_sense(w[2].get("sense_short", "")): w[2].get("term", "")
                     for w in ctx.writes
                     if w[0] == "glossary_terms" and w[1] != id
                     and (w[1] == slug or w[1].startswith(slug + "#"))})
        seen.pop("", None)
        if _same_sense(sense_short) in seen:
            raise ValueError(
                f"{term!r} already means that. `sense={sense!r}` asks for a "
                f"second sense of the word, and a second sense is one the "
                f"glossary does not already carry -- "
                f"{seen[_same_sense(sense_short)]!r} says the same thing you "
                f"just wrote. Drop `sense` to amend the entry you have, or "
                f"give the meaning that is genuinely different. (`sense` names "
                f"*which meaning*, not where it came from: provenance is "
                f"`observed` here without your saying so.)")



    # A second session saying something different about the same word is the
    # collision signal, and it was being thrown away as a duplicate.
    #
    # Both arrive in the identical shape -- one word, written twice, by two
    # sessions -- and `INSERT OR REPLACE` on an id derived from the term kept
    # the last. So the system could not tell `endpoint` written five times
    # meaning the same thing, which is the failure the derivation was built to
    # stop, from `folder` written twice meaning two different things, which is
    # what this repository actually does. It resolved both by silent
    # last-writer-wins.
    #
    # What that cost, measured across two runs: the correct sense was written
    # by an early session and destroyed by a later one four times.
    # `folder: "in the context of template variables"` overwritten by
    # `"a directory where notes are stored"`. `intent: "a type of frontmatter
    # that defines a template or action"` overwritten by `"a plugin for
    # Obsidian"`. Half the bad glossary was answers the run already had.
    #
    # Area is evidence and not authority. Two senses written while reading one
    # area are one thing described twice, so that stays an amendment. Two from
    # different areas are the word doing different work in two places, which is
    # a second row -- exactly what `sense=` makes deliberately, arrived at from
    # what happened instead of from the model noticing.
    #
    # Which sense survives is not decided here and is not computable: see the
    # note on `glossary_terms.area`. Nothing wins silently is the whole change.
    # A row with no area was written about the whole program, by the define
    # phase, and an area session saying something different about the word
    # is the same situation as two areas disagreeing -- a second row, never a
    # replacement. The first version of this test read `prior["area"] and`,
    # so a program-level row (area empty) was silently overwritten by the
    # first area to say the word differently, which destroyed exactly the
    # sense the define phase exists to write.
    if not sense and is_area(ctx.area):
        prior = ctx.conn.execute(
            "SELECT id, area, sense_short, sense_body FROM glossary_terms "
            "WHERE id = ? AND superseded_by IS NULL", (slug,)).fetchone()
        # A second sense says something the first does not. "In this area, a
        # template variable type is a type of variable" beside "A type of
        # variable" is the same reading in more words, and the root area wrote
        # one of those for nearly every program-level word -- then two of them
        # were raised to the principal as collisions. Content words, minus the
        # term's own: if the new sense adds none, there is nothing to record.
        if prior and (prior["area"] or "") != ctx.area:
            own = set(_words_in(term))
            new_words = set(_words_in(f"{sense_short} {sense_body}")) - own - _FRAME_WORDS
            old_words = set(_words_in(
                f"{prior['sense_short']} {prior['sense_body'] or ''}")) - own
            if new_words and new_words <= old_words:
                raise ValueError(
                    f"{term!r} already means that: the glossary's entry says "
                    f"everything this one does. A second sense is one the "
                    f"glossary does not carry -- what this area means by the "
                    f"word that the entry above does not say. If it means the "
                    f"same here, there is nothing to record.")
        if (prior and (prior["area"] or "") != ctx.area
                and _same_sense(prior["sense_short"]) != _same_sense(sense_short)):
            # `root`, not the empty string: the root area is a real area and
            # its second sense is a real second row, so it needs a name and
            # cannot collapse back onto `slug`.
            id = f"{slug}#{_slug_of(ctx.area) or 'root'}"

    ctx.writes.append(("glossary_terms", id, {
        "term": term, "sense_short": sense_short, "sense_body": sense_body,
        "provenance": ctx.provenance,
        # An area for a survey; nothing for a word defined over the whole
        # program. `@term:x` is a subject, not a place the word was seen.
        "area": ctx.area if is_area(ctx.area) else ""}))
    out = {"id": id}
    if ignored_sense:
        out["note"] = ignored_sense
    if filed_under:
        out["note"] = ((out.get("note", "") + " ").strip() +
                       f" filed under {filed_under!r}, the word this session "
                       f"is about.").strip()
    if unplaced:
        out["note"] = ((out.get("note", "") + " ").strip() +
                       " recorded, naming no place this project writes the "
                       "word down; a reader will have to find one.").strip()
    if subject and unkinded:
        out["note"] = ((out.get("note", "") + " ").strip() +
                       " recorded without naming the kind the code declares it "
                       "one of; a reader will have to find that out.").strip()
    return out


@op("glossary", "synthesise")
def glossary_synthesise(ctx: Ctx, ids: list[str], sense_short: str,
                        sense_body: str) -> dict:
    """
    Several partial readings of one word, and the sense none of them holds.

    The glossary had two relations between rows and needed three. Two senses
    that differ are a *collision*, kept apart. One sense written twice is a
    *duplicate*, collapsed by `glossary.same`. Neither describes what a survey
    pass actually produces, which is N sessions each seeing the word in one
    place and writing what it looked like from there:

        intent               [src]            note with properties and templates
        intent#src_intents   [src/intents]    custom actions in Obsidian
        intent#src_variables [src/variables]  function or action in a plugin
        intent#root          [.]              template with specific action

    Not duplicates -- no two say the same thing. Not a collision -- there is one
    intent in this codebase. Four fragments of one meaning, and the answer key's
    sense, "a recipe for making a note, declared in another note's frontmatter
    under `intents_to`", is in none of them and composable from all of them plus
    `code.concordance`.

    `glossary.same` cannot do this: it collapses onto a row that already exists,
    and the sense being written here exists nowhere yet. That is the whole
    difference between choosing among readings and writing the reading.

    **Superseded, never deleted**, on the same argument as `glossary.same`: the
    partials stay readable and the composition stays reversible, because it is a
    judgement being delegated to a session that cannot be checked mechanically.

    No argument is required for it. `glossary.same` asks the session to say why
    two senses are the same and the model demonstrably cannot -- five runs of
    `different provenance`, `same sense`, `same term`. What is checked here is
    the shape of the result, not the quality of a justification: more than one
    row, one family, and a sense that is not simply one of the partials picked.
    """
    if len(set(ids)) < 2:
        raise ValueError(
            "synthesis composes more than one reading. One row is an amendment "
            "-- `glossary.amend` -- and this is for the several partial senses "
            "the wake put in front of you.")

    # The rows the wake named, or a refusal that says what they were.
    #
    # `cnt_q` answered `ids=['tick','tock']` -- words off the wake *kind*, not
    # the wake's refs -- and got "is not a glossary id", which is true and does
    # not say which ids were. Same shape as the fix in `glossary.same`: name the
    # set, do not merely reject the guess.
    if ctx.wake_refs and not set(ids) <= set(ctx.wake_refs):
        raise ValueError(
            f"{sorted(set(ids) - set(ctx.wake_refs))} is not among the rows you "
            f"were woken about. Those are {list(ctx.wake_refs)}, and they are "
            f"the readings this session exists to compose.")

    rows = {r["id"]: r for r in ctx.conn.execute(
        "SELECT id, term, sense_short, sense_body, provenance, source_refs, "
        "area, superseded_by FROM glossary_terms "
        f"WHERE id IN ({','.join('?' * len(set(ids)))})", tuple(set(ids)))}
    missing = [i for i in set(ids) if i not in rows]
    if missing:
        raise ValueError(
            f"{missing} is not a glossary id. The ids are the ones the wake "
            f"named, spelled as they were given.")

    fams = {i.split("#")[0] for i in rows}
    if len(fams) > 1:
        raise ValueError(
            f"{sorted(fams)} are different words. Synthesis writes one sense of "
            f"one word from the readings of it; two words are two entries.")

    if not (sense_short or "").strip() or not (sense_body or "").strip():
        raise ValueError(
            "a synthesised sense needs both: `sense_body` is what the readings "
            "add up to, `sense_short` the one line every later reader is shown.")

    same_as = next((i for i, r in rows.items()
                    if _same_sense(r["sense_short"]) == _same_sense(sense_short)),
                   None)
    if same_as:
        raise ValueError(
            f"that is {same_as!r} again, word for word. Synthesis is for the "
            f"sense the readings add up to and none of them states. If one of "
            f"them is simply right and the others say the same thing in other "
            f"words, `glossary.same` is the call.")

    keep = sorted(fams)[0]

    # It has to say something the readings do not.
    #
    # A sense composed only from the readings is a summary of them, and summing
    # partial views generalises: measured on `cnt_r`, the first run where this
    # verb worked at all, all three results were the readings welded together.
    #
    #   templates <- 3   "customizable note or document structure"
    #   intent    <- 2   "template or instruction for organizing and processing notes"
    #   variable  <- 1   "template placeholder or variable used in templates"
    #
    # `templates` is arguably worse than one of its own partials ("Pre-defined
    # template for generating new notes") and `variable` is circular. None of
    # the three contains one word from the concordance that was pushed into the
    # prompt beside them.
    #
    # Checkable, unlike the argument `glossary.same` asks for: the concordance
    # holds 53 content words for `intent` and the readings hold 26, so 47 are
    # available. The produced sense brings in none of them; the answer key's --
    # "a recipe for making a note, declared in another note's frontmatter under
    # `intents_to`" -- brings in `declared`, `frontmatter`, `intent`.
    #
    # The refusal names none of the candidates. `cnt_o` put a list of grains in
    # an error message and the session defined the list; a list of words a sense
    # could contain is the same act with the same outcome.
    said = set()
    for r in rows.values():
        said |= set(_words_in(f"{r['sense_short']} {r['sense_body'] or ''}"))
    # Gated on there being an index, not wrapped in `except Exception`. The
    # first version swallowed everything, and what it swallowed was an
    # `AttributeError` from a context missing `batch_id` -- so the guard was
    # silently off and its own test passed by not raising. A check that
    # disables itself on any error is the failure this file keeps finding.
    indexed = ctx.conn.execute("SELECT 1 FROM code_index LIMIT 1").fetchone()
    evidence = (set(_words_in(code_concordance(ctx, term=keep)["where"]))
                if indexed else set())
    summary_only = False
    if evidence:
        brought = set(_words_in(f"{sense_short} {sense_body}")) & (evidence - said)
        asked = sum(1 for fn, why, *_ in (getattr(ctx, "refusals", None) or [])
                    if fn == "glossary.synthesise" and "nothing the readings" in why)
        # Once. Two collision sessions re-sent a summary twelve times each
        # against this refusal; the second attempt lands, flagged, like every
        # other guard here -- a composition that adds nothing is still one
        # row where there were three, and the flag says what it is.
        if not brought and not asked:
            raise ValueError(
                "that says nothing the readings did not already say -- it is a "
                "summary of them, and summing partial views of a word gives a "
                "vaguer word, not a truer one. The readings are where it is "
                "used; `[code.concordance]` is what it *is* -- where the "
                "project declares it and what happens to it. A synthesised "
                "sense has to carry something only that could tell you.")
        summary_only = not brought

    term = rows.get(keep, next(iter(rows.values())))["term"]
    # Composed from observed readings is still observed.
    #
    # `ctx.provenance` is `observed` only on a `tick:survey` wake and `decided`
    # everywhere else, this mode included -- so a synthesised sense would arrive
    # claiming someone chose it with the reason on file. Nobody did: it was
    # assembled from rows that were themselves found in the code, plus the
    # concordance. Law 11 splits these on *found not chosen*, and this is found.
    #
    # Taken from the readings rather than asserted, so a synthesis over anything
    # decided stays decided.
    provenance = ("decided" if any(r["provenance"] == "decided"
                                   for r in rows.values()) else "observed")
    ctx.writes.append(("glossary_terms", keep, {
        "term": term, "sense_short": sense_short, "sense_body": sense_body,
        "provenance": provenance,
        "area": rows[keep]["area"] if keep in rows else "",
        "superseded_by": None}))
    for i, r in rows.items():
        if i == keep or r["superseded_by"]:
            continue
        ctx.writes.append(("glossary_terms", i, {
            "term": r["term"], "sense_short": r["sense_short"],
            "sense_body": r["sense_body"], "provenance": r["provenance"],
            "source_refs": r["source_refs"], "area": r["area"],
            "superseded_by": keep}))
    out = {"id": keep, "composed_from": sorted(i for i in rows if i != keep)}
    if summary_only:
        out["note"] = ("recorded as a summary of the readings, carrying nothing "
                       "the concordance alone could tell; a reader should weigh "
                       "it as such.")
    return out


@op("glossary", "same")
def glossary_same(ctx: Ctx, keep: str, drop: str, why: str) -> dict:
    """
    Two rows, one meaning. Say so, and the duplicate stops being a question.

    `term_collision`'s brief has always named two outcomes -- *"two entries for
    one word are sometimes one sense written twice in different words; if they
    say the same thing, that is a duplicate and not a collision, and saying so
    is the answer"* -- and the mode's whole working set was `glossary.lookup`,
    `glossary.consult` and `msg.report_liaison`. The only way to say anything
    was to escalate. Measured: three sessions looked the same two rows up eleven
    times each and ended with nothing they could do.

    This does not touch the rule it looks like it touches. *Collapsing two
    senses* is a decision and stays the principal's, because choosing which one
    the project means is about their intent. *Recognising that there was only
    ever one sense* is an observation: nothing is chosen, and the alternative is
    a question put to a person that answers itself.

    It is also the easy half. Judging whether "a file in the Obsidian vault
    containing frontmatter" and "a document or file in Obsidian that contains
    notes" say the same thing is a far smaller task than producing either, which
    is why it is worth a session at this model size.

    **Superseded, never deleted.** Sameness is a judgement being delegated and
    it cannot be checked mechanically, so the losing sense stays readable and
    the merge stays reversible. Wrongly calling two senses different costs the
    principal a glance; wrongly calling them the same destroys the ambiguity
    this system exists to surface. Only one of those is recoverable, so only one
    of them is allowed to be quiet.
    """
    rows = {r["id"]: r for r in ctx.conn.execute(
        "SELECT id, term, sense_short, sense_body, provenance, source_refs, "
        "area, superseded_by FROM glossary_terms WHERE id IN (?, ?)",
        (keep, drop))}
    missing = [i for i in (keep, drop) if i not in rows]
    if missing:
        # Say which ids exist, rather than where they came from.
        #
        # The old message named the wake — "both ids come from the wake that
        # woke you, spelled as they were given" — and a session that has already
        # lost track of them cannot act on that. Measured on `cnt_k`: woken for
        # `template, template#src_variables_providers`, three sessions called
        # `glossary.same(drop='templatevariable', keep='intent#src_variables_providers')`
        # — the wrong term and an id that does not exist — identically each
        # time, and the collision was quarantined on the third.
        #
        # The open collisions are derivable here: two live rows sharing a term
        # is what the predicate means by one. So the refusal shows them.
        open_now = [(r["term"], r["ids"]) for r in ctx.conn.execute(
            "SELECT term, GROUP_CONCAT(id) AS ids, COUNT(*) AS n "
            "FROM glossary_terms WHERE superseded_by IS NULL "
            "AND COALESCE(area, '') <> '.' "
            "GROUP BY term HAVING n > 1 LIMIT 5")]
        listing = ("; ".join(f"{t!r}: {ids}" for t, ids in open_now)
                   if open_now else "none right now")
        raise ValueError(
            f"{missing} is not a glossary id. The words with more than one live "
            f"sense are — {listing}. Use two ids from one of those, exactly as "
            f"spelled; this call says two rows are one word said twice.")
    if keep == drop:
        raise ValueError("keep and drop are the same row; nothing to merge.")

    a, b = rows[keep], rows[drop]
    if _slug_of(a["term"]) != _slug_of(b["term"]):
        raise ValueError(
            f"{a['term']!r} and {b['term']!r} are different words. This says two "
            f"rows are one word said twice; it is not for relating two words.")
    # `why` has to be an argument, not a filled field.
    #
    # The first version required it to be non-empty, which is not the same as
    # requiring it to say anything -- and the run answered `why="term_collision"`
    # (the mode's own name) three times, and `why="different provenance"` twice,
    # merging two rows while stating a reason they are not the same. A guard
    # that accepts any non-empty string is a guard against forgetting, and
    # forgetting was not the risk.
    #
    # Two checks, both cheap. It may not argue difference -- that is a reason to
    # report, and the words for it are few and unambiguous. And it has to be
    # about these two senses: a reason sharing no content word with either of
    # them is a reason about something else, which is what a mode name is.
    reason = (why or "").strip()
    if not reason:
        raise ValueError(
            "say why they are the same before merging them. Reporting two "
            "senses costs the principal a glance; calling them the same "
            "destroys an ambiguity only they can settle, so this one has to be "
            "argued.")
    against = [w for w in ("different", "differ", "distinct", "separate",
                           "unlike", "not the same", "another sense")
               if w in reason.lower()]
    if against:
        raise ValueError(
            f"{reason!r} is a reason they are *not* the same -- it says "
            f"{against[0]!r}. Two senses that differ go to the principal with "
            f"`msg.report_liaison`; this call is for two rows that say one "
            f"thing.")
    said = set(_words_in(f"{a['sense_short']} {a['sense_body'] or ''} "
                         f"{b['sense_short']} {b['sense_body'] or ''}"))
    if said and not (set(_words_in(reason)) & said):
        raise ValueError(
            f"{reason!r} does not mention anything either sense says. Name what "
            f"the two have in common, in their own words -- {a['sense_short']!r} "
            f"and {b['sense_short']!r} -- or report them instead.")

    if b["superseded_by"]:
        return {"id": keep, "note": f"{drop} was already superseded."}

    # No ledger entry and no stored prose. The ledger is for a sense picked when
    # the material did not settle it, and a duplicate is not an assumption --
    # filling it with these would put non-questions in front of the principal
    # and block milestones on them. Law 2 keeps prose off artefacts anyway: the
    # record is the pointer and both rows still being readable.
    #
    # `why` is required and goes nowhere. It is here so the case has to be
    # stated before the act, which is the whole guard on a judgement that cannot
    # be checked.
    # The whole row, not the changed column. Writes land as `INSERT OR REPLACE`
    # with only the columns given, so a partial write nulls the rest -- and the
    # first version of this dropped `sense_body`, destroying the sense it had
    # just promised to keep readable. Supersede has to carry the row forward.
    ctx.writes.append(("glossary_terms", drop, {
        "term": b["term"], "sense_short": b["sense_short"],
        "sense_body": b["sense_body"], "provenance": b["provenance"],
        "source_refs": b["source_refs"], "area": b["area"],
        "superseded_by": keep}))

    # Anything pointing at the losing row is repointed at the survivor. The
    # claim being made is that the two say the same thing, so a reference to one
    # is a reference to the other -- and leaving them is the quiet kind of wrong
    # this whole change is against: `check_criteria_terms` validates against
    # every row including superseded ones, so a stale ref stays green while
    # naming the sense that was just declared redundant.
    #
    # Empty during onboarding, because criteria do not exist yet. It is the
    # delivery loop that would have paid for it.
    repointed = []
    for table in ("criteria", "business_rules"):
        try:
            rows = list(ctx.conn.execute(
                f"SELECT * FROM {table} WHERE term_refs LIKE ?", (f'%"{drop}"%',)))
        except sqlite3.OperationalError:                    # pragma: no cover
            continue
        for r in rows:
            refs = json.loads(r["term_refs"] or "[]")
            if drop not in refs:
                continue
            moved = [keep if x == drop else x for x in refs]
            seen_once, out_refs = set(), []
            for x in moved:
                if x not in seen_once:
                    seen_once.add(x); out_refs.append(x)
            whole = {k: r[k] for k in r.keys() if k != "id"}
            whole["term_refs"] = json.dumps(out_refs)
            ctx.writes.append((table, r["id"], whole))
            repointed.append(r["id"])

    out = {"id": keep, "superseded": drop,
           "note": f"{drop} now points at {keep}. Both senses stay readable."}
    if repointed:
        out["repointed"] = repointed
    return out


@op("glossary", "lookup")
def glossary_lookup(ctx: Ctx, term: str = "") -> list[dict] | dict:
    """
    One term, all senses — collisions are visible by construction.

    A hit returns the rows and nothing else, exactly as it always has. A *miss*
    says how big the glossary is, because an empty result on its own is a
    vacuous signal that has been read as a strong one: two Tester sessions
    looked a whole clause up in a glossary with no rows in it at all, got `[]`,
    concluded the criterion turned on an undefined word, and sent the
    sentence's problem to the wrong desk. Nothing was undefined; there was
    nothing to define against.

    The count is a fact the system already holds and did not mention. It is
    reported rather than interpreted — no advice about what to do with it,
    because the judgement is the role's and this is the input it was missing.
    """
    # With no term, the rows the wake named.
    #
    # `term_collision` wakes a session *about* specific rows and the only place
    # they appeared was the `Refs:` line, so their senses -- the entire subject
    # of the session -- had to be fetched by a call the model had to think of.
    # Callable-with-no-arguments is what `push_working_set` sends unasked, and
    # this is exactly the case its docstring describes: "if the session already
    # holds everything a read needs, making the model ask for it is a turn spent
    # on nothing."
    if not (term or "").strip() and ctx.wake_refs:
        rows = _rows(ctx.conn.execute(
            "SELECT id, term, sense_short, sense_body, area, provenance "
            "FROM glossary_terms WHERE id IN "
            f"({','.join('?' * len(ctx.wake_refs))})", tuple(ctx.wake_refs)))
        return rows or {"note": "the rows this wake named are gone."}

    rows = _rows(ctx.conn.execute(
        "SELECT id, term, sense_short, sense_body, provenance FROM glossary_terms "
        "WHERE term = ? ORDER BY id", (term,)))
    if rows:
        ctx.lookup_misses.discard(term)
        return rows

    ctx.lookup_misses.add(term)
    total = ctx.conn.execute(
        "SELECT COUNT(*) n FROM glossary_terms").fetchone()["n"]
    return {"term": term, "senses": [], "glossary_size": total,
            "note": (f"no entry for {term!r}. The glossary holds {total} "
                     f"term{'' if total == 1 else 's'}"
                     + ("" if total else ", so a miss here says nothing about "
                                        "whether any word is unclear"))}


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
                source_refs: list[str] | None = None,
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

    # A headline is what is promised, in the source's words. "commitment 1",
    # "constraint 2": a label, and five of them arrived in one session with
    # the orientation's items pasted under them. A headline with no word of
    # its own beyond the frame's is not a headline.
    if not [w for w in _words_in(headline)
            if w not in ("commitment", "constraint", "promise", "contract")]:
        raise ValueError(
            f"{headline!r} is a label, not a headline. Say what is promised, "
            f"in the words the source uses at the place it is kept.")
    # And an item restated is an item. The baseline is pushed into this
    # session as context -- what the program *does* -- and the same run wrote
    # each of its five behaviours back as a constraint, word for word. A
    # constraint answers a different question: who outside breaks if this
    # changes. If the text is an item's text, it has not answered it.
    # Who breaks must be outside. "A maintainer would encounter errors if they
    # tried to call this function" names the one party the brief rules out,
    # and a run wrote nine constraints of that shape, one per identifier it
    # had been shown. Inside is not outside; the form is not the finding.
    saying = f"{headline} {text}".lower()
    # "the code inside PTPlugin.onload()", "the program's internal logic",
    # "the manifest.json file" as WHO BREAKS: the 14B Architect's root-area
    # pass wrote twelve of those around the one real commitment. Code, logic
    # and files of this repository are inside, however they are named.
    inside = re.search(r"\b(maintainers?|developers?|other parts of the code"
                       r"(?:base)?|the codebase|the build|test suite|the tests|"
                       r"this (?:function|constant|type|class|component|file|"
                       r"module)|the code inside|internal(?:ly)?|"
                       r"the program'?s? (?:own )?(?:logic|code)|hardcoded in|"
                       r"the [\w./-]+\.\w+ file)\b", saying)
    outside = re.search(r"\b(users?|registry|obsidian|vault|notes?|another plugin|"
                        r"other plugin|external|api|npm|github|community|client|"
                        r"consumer|caller outside|downstream)\b", saying)
    # "users of this repository who import getIntentsFromTFile" wears the word
    # `users` over an inside party: anyone described as importing, extending
    # or calling an identifier reads this code, whatever they are called. The
    # disguise vetoes the outside word.
    disguised = re.search(r"who (?:import|imports|extend|extends|call|calls|"
                          r"use|uses|reference|references)\b|the import of\b",
                          saying)
    if (inside and not outside) or disguised:
        raise ValueError(
            f"{headline!r} names nobody outside this repository -- a maintainer, "
            f"the codebase, the build are inside. A constraint is kept to "
            f"someone who does not read this code: say who, or this is not one.")
    item_texts = [r["text"] for r in ctx.conn.execute("SELECT text FROM items")]
    mine_words = set(_words_in(f"{headline} {text}"))
    for it in item_texts:
        iw = set(_words_in(it))
        if len(iw) >= 4 and len(mine_words & iw) >= max(4, int(0.7 * len(iw))):
            raise ValueError(
                f"that is what the product does, and an item already says it. "
                f"A constraint is what would break outside this repository if "
                f"the code here changed -- who notices, and how. If nothing "
                f"outside would, this area holds no constraint.")
    if slug == boot.ZERO or headline.strip().lower() == boot.ZERO_HEADLINE.lower():
        raise ValueError(
            f"{boot.ZERO} is derived: its bindings are the areas nobody has "
            f"surveyed, and a survey record is what shrinks it. Write your own "
            f"constraint for what you found.")

    # A new constraint about a subject an existing constraint already governs
    # is either the same commitment (the headline-derived id catches the exact
    # words) or a *contradicting twin* -- and the second kind was written
    # live: handed "closing an account deletes its invoices" against a
    # decided seven-year retention constraint, the Architect spent five runs
    # of five trying to record the conflict as a second constraint, once with
    # an invented attribution to justify it. Two constraints about one
    # subject saying different things is incoherence whatever the intent, so
    # the door refuses and names the honest exits.
    stop = {"the", "and", "for", "with", "after", "are", "is", "not", "its"}
    def _stems(words: str) -> set[str]:
        return {w.rstrip("s") for w in re.findall(r"[a-z]+", words.lower())
                if len(w) >= 4 and w not in stop}
    mine = _stems(headline + " " + (text or ""))
    from ..onboarding import boot as _boot

    for row in ctx.conn.execute(
            "SELECT id, headline FROM constraints WHERE id NOT IN (?, ?)",
            (slug, _boot.ZERO)):
        shared = mine & _stems(row["headline"])
        if len(shared) >= 2:
            raise ValueError(
                f"{row['id']} already governs this subject: "
                f"{row['headline']!r}. If both commitments hold together, "
                f"say what distinguishes them in the headline; if they "
                f"cannot both be true, that is not a second constraint, it "
                f"is msg.challenge_vision_keeper with both rows in refs and "
                f"quotes= copying the span of each")
    # You cannot have found a commitment in a file you did not open. The first
    # foreign repository produced constraints naming grains no session had read
    # -- the brief said to open them, the harness was cutting the result to a
    # docstring, so opening them achieved nothing and nothing checked either way.
    # `code.survey` is not reading: it returns the index, and the index is
    # exactly the material a fabricated constraint is made of.
    #
    # Checked after constraint zero, whose refusal is the more specific one and
    # was briefly being swallowed by this.
    # A reference id in `bindings` is the commonest way in, and "you have not
    # read it" is true and useless for one: no amount of `code.source` turns a
    # reference into a grain, so the session re-amends against the same wall.
    # Six times, in one recorded run. Name the other parameter instead.
    refs_here = sorted(g for g in (bindings or [])
                       if ctx.conn.execute(
                           "SELECT 1 FROM references_ WHERE id = ?", (g,)).fetchone())
    if refs_here:
        raise ValueError(
            f"{', '.join(refs_here)} is a reference, not a grain -- bindings are "
            f"the code a constraint governs, and reading it would not make it "
            f"one. The clause a constraint rests on goes in `source_refs=`, "
            f"which also makes the entry `cited`.")

    # Same argument as the reference case above, one step earlier: a name that
    # is not a grain at all cannot be made into one by reading it either, and
    # "you have not read it" sends the session to `code.source` with a string
    # that names no file. An Architect bound `account` -- the pattern it had
    # probed with, not anything the probe returned -- and spent all twelve turns
    # alternating `code.source(ids=['account'])` with the identical amend, in a
    # fixture whose code index is empty. Nothing it could have done would have
    # satisfied the advice it was given.
    # Folded to the file, the same way the read-check folds: a symbol is a real
    # binding whether or not the indexer emitted a row for it, because the file
    # it lives in is what anybody opens.
    indexed = {r["grain"] for r in ctx.conn.execute("SELECT grain FROM code_index")}
    indexed |= {_grain_path(g) for g in indexed}
    if bindings and indexed:
        strangers = sorted(g for g in bindings
                           if g not in indexed and _grain_path(g) not in indexed)
        if strangers:
            # Paths, never symbols, for the same reason `surveys.attest` lists
            # paths: a list of symbols in a refusal is a list that gets
            # transcribed. And what the session *opened*, not `code.probe`,
            # which the survey mode does not carry -- an Architect told to
            # probe for ids it could not probe for spent three sessions binding
            # JSON keys out of manifest.json.
            opened = sorted(p for p in (ctx.opened or set()) if "::" not in p)[:6]
            raise ValueError(
                f"{', '.join(str(x) for x in strangers)} is not a grain in the "
                f"index. A binding is the path of a file that keeps the "
                f"commitment" +
                (f" -- you have opened {opened}, and any of those can be bound."
                 if opened else
                 " -- `code.source` the file that keeps it, then bind its path."))
    elif bindings:
        # No index -- a delivery engagement that never onboarded. A binding is
        # then the path of a file this session actually read; a symbol cannot
        # be folded to its file mechanically, so it is refused by name.
        strangers = sorted(str(g) for g in bindings
                           if _grain_path(str(g)) not in (ctx.opened or set()))
        if strangers:
            opened = sorted(p for p in (ctx.opened or set()) if "::" not in p)[:6]
            raise ValueError(
                f"{', '.join(strangers)} is not the path of a file this session "
                f"read, and there is no code index in this engagement to resolve "
                f"it. A binding is the path of a file that keeps the commitment" +
                (f" -- you have opened {opened}, and any of those can be bound."
                 if opened else
                 " -- `code.source` the file that keeps it, then bind its path."))

    # Neither message offers the empty list as the way out, and that is
    # deliberate. The first draft of the second one ended "leave `bindings`
    # empty: a constraint with none is global" -- true, and read as permission.
    # `L2-AR-place-a-block-developer-could-not` took it and wrote the constraint
    # the case exists to forbid. An error says what is wrong with what you sent;
    # the moment it also names something else you could send instead, it is a
    # brief, and briefs that name an alternative to the decisive action get the
    # alternative. Four cases lost to that shape today in three different files.

    unread = sorted(g for g in (bindings or []) if _grain_path(g) not in ctx.opened)
    if unread:
        raise ValueError(
            f"you have not read {', '.join(unread)} this session. A constraint "
            f"binds the grains it governs, and it cannot govern what nobody "
            f"opened -- `code.source` them first, or bind only what you read.")

    # `source_refs` is the clause this constraint encodes, and the column has
    # existed all along: "constraints are where external obligations actually
    # land, so a constraint that cannot point at the clause it encodes is the
    # one that most needed to." The brief says to cite the reference here and
    # the parameter was never on the function, so the Architect put reference
    # ids in `bindings` -- the only list it had -- and the read-check refused
    # them, correctly and forever: a reference is not a grain and no amount of
    # `code.source` would make it one. Six identical refused amends in one
    # session.
    #
    # `cited` is law 11's third provenance and the only one that can go stale on
    # its own, so it is set by the presence of a source rather than supplied: a
    # session that names the clause has cited it, whatever it would have claimed.
    # Unknown refs are dropped and reported, never refused. Refusing loses the
    # constraint -- the actual work -- over its footnote, and a session told
    # "no such reference" answers by trying another id rather than by writing
    # the commitment down. The citation is worth having and is not worth the row.
    known = {r["id"] for r in ctx.conn.execute("SELECT id FROM references_")}
    wanted = [r for r in (source_refs or []) if isinstance(r, str)]
    cited = [r for r in wanted if r in known]
    dropped = [r for r in wanted if r not in known]

    # A constraint needs a body, and the check was in the wrong place.
    #
    # `surveys.attest` has the right words already -- "A title cannot be checked,
    # argued with or satisfied -- say what it is and who outside would notice" --
    # and applies them only when a session attests `found`. A session that writes
    # two headlines and attests `none_found` walks past it. Measured: the cnt
    # baseline wrote 2 constraints, both empty; `cnt_j` wrote
    # `intent_schema_validation` and
    # `intent_schema_validation_binds_to_the_intent_type`, both empty, then
    # attested `architect:src none_found`. The key has carried
    # `constraints_must_have_a_body: true` since it was written.
    #
    # At write time it also closes a second hole: `text` is always in the write,
    # so amending a constraint to add a binding, with no text, blanked the body
    # it already had.
    if not (text or "").strip():
        raise ValueError(
            f"{headline!r} is a title with nothing under it. A title cannot be "
            f"checked, argued with or satisfied -- `text` says what the "
            f"commitment is and who outside this repository would notice if it "
            f"stopped being true. If you cannot say that, it is probably a "
            f"tunable default rather than a commitment, and the honest answer "
            f"is not to write it.")

    id = slug[:120]
    ctx.writes.append(("constraints", id, {
        "headline": headline, "text": text,
        "provenance": "cited" if cited else ctx.provenance,
        "source_refs": json.dumps(cited),
        "is_global": 0 if bindings else 1}))
    for grain in bindings or []:
        ctx.writes.append(("constraint_bindings", f"{id}:{grain}", {
            "constraint_id": id, "grain": grain, "grain_kind": "path"}))
    out = {"id": id, "bindings": bindings or [], "source_refs": cited}
    if dropped:
        out["not_cited"] = (
            f"{', '.join(dropped)} is not a reference on file, so the constraint "
            f"is written without it. Only a row from `references.load` can be "
            f"cited; a citation nobody can follow is worse than none.")
    return out


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


@op("model", "describe")
def model_describe(ctx: Ctx, account: str, area: str | None = None) -> dict:
    """
    What this area is for and how it works, in the surveyor's own words --
    the two sentences every survey session already writes and the transcript
    was discarding. One row per area, under the model, because "what is
    buildable here" starts with what each part is.
    """
    from ..core.scheduler import is_area

    area = area or ctx.area
    if not is_area(area):
        raise ValueError(
            f"{area!r} is not an area: the account of the whole program is the "
            f"orientation's item, not a model row.")
    account = (account or "").strip()
    if len(account) < 40:
        raise ValueError(
            "an account says what the area is for and how it works -- a "
            "sentence or two, not a label.")
    words = account.split()
    pathy = sum(1 for w in words if "/" in w or w.count(".") >= 2)
    if pathy > len(words) // 2:
        raise ValueError(
            "that is a list of files, and the index already holds it. Say what "
            "the area does with them.")
    ctx.writes.append(("model_areas", area, {
        "account": account,
        "source_refs": _json.dumps(sorted(ctx.opened)[:12]),
        "provenance": ctx.provenance or "observed"}))
    return {"area": area}


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


def _re_split_paths(val: str) -> list[str]:
    import re as _re

    return [t.strip("'\"[]") for t in _re.split(r"[\s,]+", val.strip()) if t.strip("'\"[]")]


def area_content_hash(conn, area: str) -> str:
    """
    The area's aggregate content, from the index the sessions read.

    Path grains only, sorted, so the value is a function of (files, contents)
    and nothing else. Empty when the area holds no path grains or the index
    predates content hashes -- and empty never matches a real digest, so an
    old record reads as "view unknown" rather than "still fresh".
    """
    import hashlib

    rows = [f"{r['grain']}={r['content_hash']}" for r in conn.execute(
        "SELECT grain, content_hash FROM code_index "
        "WHERE grain_kind = 'path' AND area = ? AND content_hash != '' "
        "ORDER BY grain", (area,))]
    if not rows:
        return ""
    return hashlib.sha256("|".join(rows).encode()).hexdigest()[:16]


@op("surveys", "attest")
def surveys_attest(ctx: Ctx, outcome: str,
                   citations: list[str] | None = None) -> dict:
    """
    Close the area you were woken for. **Citations are required and validated
    against the code index**, so "surveyed, none found" is evidence rather than
    a claim — a lazy surveyor cannot starve constraint zero by asserting it
    everywhere. At least one cited grain must be in the index and under this
    area; the rest are reported back unresolved rather than refused.

    `outcome` is 'found' or 'none_found' -- 'found' meaning you wrote down
    what this mode exists to find, which is not the same artefact for every role.

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
    import re as _re

    from ..core.scheduler import PROGRAM, is_area

    area = ctx.area
    if not area:
        raise ValueError(
            "no area: attesting closes the area you were woken for, and this "
            "session was not woken for one")

    # Citations are paths, as strings. A session wrote
    # `citations=[['problem.baseline']]` -- a list inside the list -- and the
    # database answered "type 'list' is not supported" twelve turns running,
    # which names nothing the session can act on. Flattened, the nested name
    # is then simply not in the index, and the refusal for that says what is.
    # And `citations=".github/workflows/release.yml"` -- one path, as a string,
    # not a list -- is one citation, not thirty-six one-character grains that
    # are "not in the index at all", which is what iterating it produced for
    # three turns of one 14B session.
    if isinstance(citations, str):
        citations = [citations]
    flat: list[str] = []
    for cval in citations or []:
        if isinstance(cval, (list, tuple, set)):
            flat.extend(str(x) for x in cval if x is not None)
        elif cval is not None:
            flat.append(str(cval))
    # `citations="a.md b.yml c.md"` -- several paths in one string, separated
    # by spaces or commas -- is several citations. A path with a space in it
    # is then two grains neither of which resolves, and the refusal says so.
    citations = [tok for cval in flat
                 for tok in (_re_split_paths(cval) if (" " in cval or "," in cval) else [cval])
                 if tok]
    # `/src/main.ts` and `./src/main.ts` are `src/main.ts`: a grain is a path
    # relative to the root, and the index holds it without the prefix.
    citations = [_re.sub(r"^(?:\./|/)+", "", c) for c in citations]

    # The outcome has to match what the session actually did.
    #
    # The brief says most code is not a constraint and that `none_found` is most
    # often the right answer here. Architect returned a finding for ten of eleven
    # areas of a repository holding three or four real external commitments --
    # and eight of those eleven constraints were a headline with no body. Not
    # dishonesty: being woken *for an area* is a demand, and the two outcomes
    # cost exactly the same, so one of them looks more like work.
    #
    # So they stop costing the same. Finding something means having written
    # something, with a body on it; finding nothing stays free. The asymmetry is
    # the point, because the honest answer is the one we need to be cheap.
    #
    # And it must be *this role's* artefact. The outcome used to be spelled
    # `constraints_found` for all three surveying roles, two of which do not
    # write constraints -- so the evidence check accepted any of the three
    # tables, and a Terminologist could attest constraints it had never written.
    # On icalendar eight of eleven areas came back claiming constraints against a
    # run that wrote none. That was not a lie the model told; it was the only
    # word we gave it.
    owed = {"terminologist": "glossary_terms",
            "architect": "constraints",
            "vision_keeper": "items"}.get(ctx.role)
    # The reconcile phase's subject is the README, and what that mode exists
    # to find is disagreements -- ledger entries, not items.
    from ..core.scheduler import FRAME as _FRAME
    from ..core.scheduler import PROSE as _PROSE

    from ..core.scheduler import BLINDSPOTS as _BLIND

    if area == _PROSE:
        owed = "ledger"
    if area == _BLIND:
        owed = "ledger"
    if area == _FRAME:
        owed = "frame_rulings"
    owed_fn = {"glossary_terms": "glossary.amend", "constraints": "model.amend",
               "items": "problem.assert", "ledger": "ledger.log",
               "frame_rulings": "frame.assign"}.get(owed or "", "")
    mine = [v for t, _id, v in ctx.writes if t == owed]
    note = ""
    # The outcome follows what the session did, not what it says.
    #
    # Claimed `found` with nothing written, refused, claimed again: the first
    # per-area session of the phase design spent twelve turns re-sending the
    # same `found` over the same refusal, and the run before it had measured
    # the same shape on another repository. Being woken for a subject is a
    # demand, and `found` looks more like work. So the record is derived: a
    # session that wrote the owed artefact found something; one that wrote
    # none of it, and was not refused trying, read and found nothing -- which
    # is `none_found`, said for it.
    #
    # The one case that is neither: the write was *refused* this session and
    # nothing of that kind landed. That is not a result, and closing the
    # subject on it would lose the word or the constraint the refusal was
    # asking the session to fix. That stays a refusal, with the reason.
    refusals = getattr(ctx, "refusals", None) or []
    refused = [why for fn, why, *_ in refusals if fn == owed_fn]
    held = sum(1 for fn, why, *_ in refusals
               if fn == "surveys.attest" and "was refused this session" in why)
    if not mine and refused and not held:
        # Either claim, after a refused write and nothing landed, closes the
        # subject on a definition that was asked to be fixed. `none_found`
        # after a refusal was the commoner shape -- the define brief offered
        # it as the way out and the model took it the turn after the place
        # guard refused a generic sense -- and a word lost that way is lost
        # silently, which the attempt bound at least is not.
        #
        # Once. The turn after, the record follows what landed: a refusal the
        # session cannot act on -- a frame word it keeps re-sending, a read
        # gate it cannot satisfy -- held `.github` for twelve turns and three
        # sessions, with the right answer (`none_found`) refused every time
        # because the attest rule and the write rule were pointing at each
        # other.
        raise ValueError(
            f"your {owed_fn} was refused this session: {refused[-1][:240]} -- "
            f"and nothing of that kind has landed. Fix that call, or drop it; "
            f"a refused {owed} is not `{outcome}`.")
    if outcome == "found" and not mine:
        # A `found` with nothing written, once, is refused with the shape of
        # the call; the turn after, the record follows the writes like
        # everywhere else. It began as the orientation's rule -- the one
        # subject whose empty record costs the whole run, and the one session
        # that reliably wrote its account and then listed the behaviours as
        # prose. Then the 14B Architect did the same for the root area: five
        # RENAME WHAT / WHO BREAKS / WHAT HAPPENS answers over manifest.json,
        # the plugin's id and name among them, and `found` -- and not one
        # `model.amend`. Deriving `none_found` there was true to the writes
        # and false to the session. Bounded, like the place guard, because a
        # refusal the model cannot act on is a loop.
        asked = sum(1 for fn, why, *_ in (getattr(ctx, "refusals", None) or [])
                    if fn == "surveys.attest" and "then attest again" in why)
        if not asked:
            if area == PROGRAM:
                raise ValueError(
                    "you have attested `found` and written no items. The account "
                    "is not the record -- each behaviour in it is one call per "
                    "behaviour: `problem.assert(id=..., text=..., kind='in_scope')` "
                    "on its own line, and then attest again.")
            raise ValueError(
                f"you have attested `found` and written no {owed}. What you "
                f"found is not the record until it is written: one `{owed_fn}` "
                f"per finding, on its own line, and then attest again -- or "
                f"attest `none_found` if, written out, none of it holds.")
    if outcome == "found" and not mine:
        outcome = "none_found"
        note = (f"recorded as `none_found`: you wrote no {owed} this session, "
                f"and the record follows what was written.")
    elif outcome == "none_found" and mine:
        outcome = "found"
        note = (f"recorded as `found`: you wrote {owed} this session, and the "
                f"record follows what was written.")
    if outcome == "found":
        bodied = [v for v in mine
                  if (v.get("text") or v.get("sense_short") or
                      v.get("sense_body") or v.get("statement") or
                      v.get("default_taken") or "").strip()]
        if not bodied:
            titles = ", ".join(str(v.get("headline") or v.get("term") or "?")
                               for v in mine)
            raise ValueError(
                f"everything you wrote this session is a title with nothing "
                f"under it ({titles}). A title cannot be checked, argued with or "
                f"satisfied -- say what it is and who outside would notice, or "
                f"attest `none_found`.")

    id = f"{ctx.role}:{area}"

    # **Citations are the evidence, and they were never required.**
    #
    # `REGISTER.md` names this as constraint zero's third property -- it shrinks
    # only by evidence -- and the docstring above has always repeated it. It was
    # prose. `attest(outcome="none_found")` with no citations raised nothing,
    # wrote the record, and `refresh_constraint_zero` duly took k0 from 7 to 6:
    # an area marked examined on nothing at all. `validators.check_survey_citations`
    # flags exactly this and had no caller outside the test suite -- an assertion
    # over synthetic rows while the running system let it through.
    #
    # The asymmetry earned above is kept, and it was never this one. What the
    # icalendar lesson removed was the cost of *having to produce a finding*,
    # because that made one answer look more like work than the other. The cost
    # of *showing what you read* is the same for both outcomes and is the whole
    # of what makes either one evidence. Every survey brief already asks for it,
    # in all three surveying roles, which is what made this a missing gate rather
    # than a missing idea.
    #
    # Cheap for a session that looked -- `code.survey` has just handed it the
    # list -- and not fakeable by one that did not, because a grain must be in
    # the index and under this area.
    # A bare symbol resolves to its grain rather than being refused.
    #
    # The precondition of this gate is stated in the comment above -- "cheap for
    # a session that looked, `code.survey` has just handed it the list". A
    # design that hands over the *source* instead has no such list, and the
    # session cites what source shows it: declarations. Measured on `d`, whose
    # working set is `code.area` and `code.source` with no `code.survey` at all:
    # three sessions cited `["TemplateVariableType", "TemplateVariableVariables"]`,
    # were refused three times, hit the attempt bound, and `src/variables` and
    # `src/variables/providers` were both quarantined -- the two richest areas
    # in the repository and the only ones holding `variable_type`, `provider`
    # and the five prompt types. Thirty-six turns, and the reading was done.
    #
    # Resolving costs the gate nothing it was built for. `TemplateVariableType`
    # cannot be named by a session that did not look, which is the whole test;
    # the index is what decides, and an unambiguous suffix match inside this
    # area is the index deciding. Ambiguity is left unresolved rather than
    # guessed at, because picking one of two grains for the session is the class
    # of help that produces a citation nobody can trace.
    def _resolve(grain: str) -> str | None:
        if ctx.conn.execute("SELECT 1 FROM code_index WHERE grain = ?",
                            (grain,)).fetchone():
            return grain
        # The dot-stripped spelling of an indexed path, when it names exactly
        # one: `editorconfig` for `.editorconfig`, `github/workflows/x.yml`
        # for `.github/workflows/x.yml`. The comparison form leaks into what
        # sessions type, and a path that unambiguously names one grain is a
        # citation of it.
        like = _indexed_like(ctx, grain)
        if like:
            return like
        if "::" in grain or "/" in grain:
            return None
        hits = [r["grain"] for r in ctx.conn.execute(
            "SELECT grain FROM code_index WHERE area = ? AND grain LIKE ?",
            (area, f"%::{grain}"))]
        return hits[0] if len(hits) == 1 else None

    def _imported(grain: str) -> bool:
        """Is this a file some grain in the area imports? See the note below."""
        return ctx.conn.execute(
            "SELECT 1 FROM code_edges e JOIN code_index i ON i.grain = e.src "
            "WHERE i.area = ? AND e.dst = ? LIMIT 1",
            (area, _grain_path(grain))).fetchone() is not None

    # A subject that is not an area -- the whole program, or one word -- has
    # no "under this path" to check, and any indexed grain the session opened
    # is evidence about it. The orientation's front and the define phase's
    # concordance are assembled by the harness, so what was looked at is
    # known without the citation; the citation is still required for the
    # program, because the session chose which of the front's files to open
    # further, and waived for a word, because the concordance was pushed and
    # "I looked and there is nothing" needs no second proof.
    from ..core.scheduler import PROGRAM, is_area

    unknown, inside = [], []
    for cited in citations or []:
        grain = _resolve(cited)
        if grain is None:
            unknown.append(cited)
        elif (not is_area(area) or area == "." or grain == area
              or grain.startswith(area.rstrip("/") + "/")
              or _imported(grain)):
            # An import the area was *shown* counts as evidence about the area.
            #
            # `code.area` hands over "the area's own files, and the ones it
            # imports", deliberately -- "a file the area imports is part of what
            # the area means, wherever it sits". This gate then required every
            # citation to sit under the area's path. Two tools disagreeing about
            # what belongs to an area, and the gate winning.
            #
            # Measured on `cnt_i`: the session woken for
            # `src/variables/providers` was shown `src/variables/index.ts` and
            # `src/notice/index.ts`, read them, cited them, and was refused
            # twelve times across three sessions. The area was quarantined --
            # the one holding `variable_type`, `provider` and the five prompt
            # types, lost for the second run running, and not for the reason the
            # first one lost it.
            #
            # The evidence test is unharmed: a cited import is a file this area
            # depends on, named by a session that opened it, and the edge comes
            # from the index rather than from the citation.
            inside.append(grain)
    # And you must have opened one of them. Citing was already required, and
    # citing is not reading: the grain list is *in the prompt*, so naming one
    # costs nothing. Measured -- one survey session in three wrote six glossary
    # terms having called `code.source` zero times, which is the vocabulary of
    # an area decided from paths. `Alarm: an event that triggers an action` and
    # `folder: directory in file system` are both readings of a name.
    #
    # `model.amend` has refused exactly this for constraint bindings since Law
    # 12 -- "you cannot have found one in a file you did not read" -- using the
    # same `ctx.opened`. The rule was written and applied one artefact along.
    read = [g for g in inside if _grain_path(g) in (ctx.opened or set())]
    if inside and not read:
        raise ValueError(
            f"you cited {inside[:3]} and opened none of them. `code.survey` "
            f"lists an area; it does not show you what is in it, so a term "
            f"named from a path is a reading of the path. `code.source` one of "
            f"them first, then attest.")

    if not inside and not is_area(area) and area != PROGRAM:
        pass                    # a word: the concordance was the looking
    elif not inside:
        outside = [g for g in (citations or []) if g not in unknown]
        # Say what it *can* cite, not only what it cannot.
        #
        # Four runs lost `src/variables/providers` here, each to a different
        # spelling: bare symbols (`cnt_d`), a file from a neighbouring area
        # (`cnt_i`), symbols declared elsewhere (`cnt_l`), and now enum members
        # as `TemplateVariableType.text` (`cnt_n`, thirty-six turns across three
        # sessions, one of which wrote "It seems like I've been running in
        # circles"). Three resolution rules were added for the first three and a
        # fourth form arrived anyway.
        #
        # The common cause is not the spelling. `d`'s working set is `code.area`
        # and `code.source` with no `code.survey`, so **nothing ever lists the
        # grains** -- and this gate's own comment assumes one has ("cheap for a
        # session that looked, `code.survey` has just handed it the list").
        # `ctx.opened` is exactly the set that would satisfy the check, and the
        # session is the only one who cannot see it.
        # Paths, never symbols. The first version of this listed grains, symbol
        # names included, and the session defined them.
        #
        # Measured on `cnt_o`, session 5: three terms written in the first three
        # turns, then the refusal arrived carrying
        # `[...::TemplateVariableType, ...::TemplateVariableVariables,
        # ...::variableProviderVariableParsers, ...]`, and turn 4 wrote
        # `TemplateVariableType`, `TemplateVariableVariables`,
        # `variableProviderVariableParsers` and `variableProviderVariableGetters`
        # as glossary terms in one go. Eleven of the run's sixteen terms are
        # transcribed identifiers, against zero in the run before it.
        #
        # This document's founding finding, reproduced by me in an error string:
        # a list of symbols handed to a session told to define an area's terms
        # is a specification of the answer, and it does not stop being one
        # because it arrived in a refusal.
        #
        # A path answers the question that was actually asked -- what may I cite
        # -- and nobody defines `src/variables/providers/index.ts` as a word.
        # The index's own spelling, not the comparison form. `_grain_path`
        # strips a leading dot for matching, and the first version of this
        # hint printed that: `editorconfig`, `eslintignore` -- which the
        # session then cited, and which is not in the index, for twelve turns.
        openable = sorted({
            r["grain"] for r in ctx.conn.execute(
                "SELECT grain FROM code_index WHERE grain_kind = 'path' "
                "AND (area = ? OR ? = ?)", (area, area, PROGRAM))
            if _grain_path(r["grain"]) in (ctx.opened or set())})[:6]
        raise ValueError(
            f"attesting closes {area!r}, and closing an area means citing what "
            f"you read in it -- `citations=[...]` naming grains, spelled as the "
            f"index holds them. " +
            (f"These are indexed but not under {area!r}: {outside}. "
             if outside else "") +
            (f"These are not in the index at all: {unknown}. " if unknown else "") +
            (f"You have opened these, and any of them will do: {openable}. "
             if openable else
             f"You have opened nothing in {area!r} yet -- `code.area` or "
             f"`code.source` first. ") +
            f"Reading nothing and reporting nothing are not the same answer.")

    # What this was a survey *of*. See the column's note in schema.sql: the
    # index it read was built at this commit, so this is the commit surveyed.
    at = ctx.conn.execute(
        "SELECT value FROM config WHERE key = 'project_commit'").fetchone()
    ctx.writes.append(("survey_records", id, {
        "area": area, "outcome": outcome,
        "commit_sha": (at["value"] if at else "") or "",
        # What the area held, as the index the session read describes it. The
        # freshness view compares this against the same aggregate later; a
        # record whose view is gone counts as no record, and the survey
        # machinery re-fires unchanged.
        "area_hash": getattr(ctx, "area_hash_at_wake", None)
                       or area_content_hash(ctx.conn, area)}))
    # The record stores what the citation *resolved to*, not what was typed.
    # Storing the bare symbol with `resolves=1` would assert that a grain named
    # `TokenStore` is in the index, and none is -- a citation nobody can follow
    # back, which is the whole thing citations exist to prevent.
    for cited in citations or []:
        grain = _resolve(cited) or cited
        ctx.writes.append(("survey_citations", f"{id}:{grain}", {
            "survey_id": id, "grain": grain,
            "resolves": 1 if cited not in unknown else 0}))
    # Unresolved ones are still reported rather than fatal. The bar is showing
    # what you read, not spelling every path correctly, and a session that can
    # see what it got wrong can fix it.
    out = {"id": id, "outcome": outcome, "unresolved_citations": unknown}
    if note:
        out["note"] = note
    return out


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
    # A ticket naming an item that does not exist fails a foreign key inside
    # the transaction and takes the session with it -- recoverable one level
    # up, so it is refused here, like `batches.group` already does.
    _must_exist(ctx, "items", item_id)
    # A ticket is its text. Recorded after the ledger rename: Vision Keeper
    # sliced six tickets of which five were `text=''` -- work orders saying
    # nothing, which the criteria phase would then be woken to define "done"
    # for. Same family as the ask that carried no refs, and the same shape of
    # refusal: satisfiable, with the way back named.
    if not (text or "").strip():
        raise ValueError(
            "a ticket is its text, and this one says nothing. Slice the "
            "item into a piece of work someone could pick up and write that "
            "piece as the text")
    # The same words are the same ticket, whatever id they are given --
    # `brief.segment`'s rule, one artefact along, and the same measured
    # shape: nine tickets from a one-line item, of which the last five were
    # two sentences elaborating each other. Reported rather than refused, on
    # the same precedent: arriving at the same slice is not a fault, and an
    # error would invite a differently-worded copy.
    norm = " ".join(text.lower().split())
    same = [w for w in ctx.writes
            if w[0] == "tickets"
            and " ".join(str(w[2].get("text", "")).lower().split()) == norm]
    if same:
        return {"id": same[0][1], "unchanged": True,
                "note": f"this slice already exists as {same[0][1]}; "
                        f"nothing was written"}
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


def _woken_items(ctx: Ctx) -> list[str]:
    """The wake's refs, kept only where they name an item row."""
    refs = [r for r in ctx.wake_refs if isinstance(r, str)]
    if not refs:
        return []
    marks = ",".join("?" * len(refs))
    return [r["id"] for r in ctx.conn.execute(
        f"SELECT id FROM items WHERE id IN ({marks}) ORDER BY id", refs)]


@op("tickets", "scan")
def tickets_scan(ctx: Ctx, item_id: str | None = None) -> list[dict]:
    if item_id:
        return _rows(ctx.conn.execute(
            "SELECT id, item_id, substr(text,1,120) AS headline FROM tickets "
            "WHERE item_id = ? ORDER BY id", (item_id,)))
    # The push calls this with no arguments, and "no arguments" must not mean
    # "every row": at fifty items that is the whole backlog in every prompt,
    # the glossary incident again. The subject is the wake's, never the
    # role's -- a delivery session reads its batch, a session woken about an
    # item reads that item, and only a wake with no subject (a survey has no
    # item to scope by) still reads the world.
    if ctx.batch_id:
        return _rows(ctx.conn.execute(
            "SELECT t.id, t.item_id, substr(t.text,1,120) AS headline "
            "FROM tickets t JOIN batch_tickets bt ON bt.ticket_id = t.id "
            "WHERE bt.batch_id = ? ORDER BY t.id", (ctx.batch_id,)))
    woken = _woken_items(ctx)
    if woken:
        marks = ",".join("?" * len(woken))
        return _rows(ctx.conn.execute(
            f"SELECT id, item_id, substr(text,1,120) AS headline FROM tickets "
            f"WHERE item_id IN ({marks}) ORDER BY id", woken))
    return _rows(ctx.conn.execute(
        "SELECT id, item_id, substr(text,1,120) AS headline FROM tickets ORDER BY id"))


@op("tickets", "consult")
def tickets_consult(ctx: Ctx) -> list[dict]:
    return tickets_scan(ctx)


_REFFABLE_CACHE: dict[int, list] = {}


def _id_tables(conn) -> list[str]:
    """Every table with an id column, computed once per connection."""
    key = id(conn)
    if key not in _REFFABLE_CACHE:
        out = []
        for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
            cols = {c["name"] for c in conn.execute(f"PRAGMA table_info({r['name']})")}
            if "id" in cols:
                out.append(r["name"])
        _REFFABLE_CACHE[key] = out
    return _REFFABLE_CACHE[key]


def ref_resolves(ctx: Ctx, ref: str) -> bool:
    """A ref is a promise that a row exists somewhere -- kept, staged, or a
    declared prefix. The world-audit found 258 broken promises in the
    historical runs; this is the door that stops new ones."""
    if ref.startswith("@") or ref.startswith("e_"):
        return True
    if any(w[1] == ref for w in ctx.writes):
        return True
    for m in getattr(ctx, "outbound", None) or []:
        if isinstance(m, dict) and m.get("id") == ref:
            return True
    for table in _id_tables(ctx.conn):
        if ctx.conn.execute(f"SELECT 1 FROM {table} WHERE id = ?",
                            (ref,)).fetchone():
            return True
    if ctx.conn.execute("SELECT 1 FROM glossary_terms WHERE term = ?",
                        (ref,)).fetchone():
        return True
    # Grains are rows too: constraint bindings, surface_refs and the
    # reconcile ledger all point at what the index holds, by its own key.
    return ctx.conn.execute("SELECT 1 FROM code_index WHERE grain = ?",
                            (ref,)).fetchone() is not None


def _vet_surface(ctx: Ctx, surface_refs, *, required: bool) -> list[str]:
    """
    The surface a criterion names, checked against the index that knows.

    Greenfield is legal: when the index holds no symbols, or the named
    surface does not exist *yet*, naming the intended callable is exactly the
    design decision a criterion is for -- so an unknown name is refused only
    when the index has symbols and none is a near match, with the near
    matches named. `required` is the respecify door: the repair only exists
    where words alone already failed, so words alone cannot be the fix.
    """
    refs = [r for r in (surface_refs or []) if isinstance(r, str) and r.strip()]
    have_symbols = bool(ctx.conn.execute(
        "SELECT 1 FROM code_index WHERE grain_kind = 'symbol' LIMIT 1"
    ).fetchone())
    if not refs:
        if required and have_symbols:
            raise ValueError(
                "this rewrite names no surface, and the repair exists because "
                "the words alone could not be tested. Name the callable a "
                "test would exercise in surface_refs -- the symbols pushed "
                "into this session are the candidates")
        return []
    if not have_symbols:
        return refs                       # greenfield: intent is the surface
    vetted = []
    for ref in refs:
        hit = ctx.conn.execute(
            "SELECT grain FROM code_index WHERE grain_kind='symbol' AND "
            "(grain = ? OR grain LIKE ?)", (ref, f"%::{ref}")).fetchone()
        if hit:
            vetted.append(hit["grain"])
            continue
        # Fuzzy, not substring: 'regster' is one dropped letter from a real
        # symbol and LIKE cannot see that. The symbol index is bounded, so a
        # real closeness scan is affordable at this write's frequency.
        stems = {r["grain"].split("::")[-1]: r["grain"] for r in
                 ctx.conn.execute("SELECT grain FROM code_index "
                                  "WHERE grain_kind='symbol'")}
        near = [stems[m] for m in difflib.get_close_matches(
            ref.split("::")[-1], stems, n=5, cutoff=0.75)]
        if near:
            # A name one edit away from a real symbol is a typo, not a design.
            raise ValueError(
                f"{ref!r} is not a symbol the index knows. A surface is a "
                f"callable a test would exercise; near matches: {near}")
        # No neighbour anywhere in the index: this reads as a callable that
        # does not exist *yet*, and naming the intended entry point is exactly
        # the design decision a criterion is for. Kept as written.
        vetted.append(ref)
    return vetted


def _about_the_tests(text: str) -> bool:
    """A criterion whose subject is the tests names the Tester's job, not a
    behaviour of the program. S0 walks eleven to twenty-eight: "Unit tests
    must validate the script's behaviour..." was encoded as `assert True`,
    as an invented dict API, as calls to tests that exist nowhere -- and
    `criterion_repair` respecified the three good criteria around it with
    identical words. Nothing a machine can check follows from a sentence
    about checking."""
    import re as _re
    head = " ".join((text or "").lower().split())[:60]
    return bool(_re.match(r"^(the\s+)?(unit\s+|automated\s+)?tests?\b", head))


@op("criteria", "specify")
def criteria_specify(ctx: Ctx, id: str, ticket_id: str, text: str,
                     term_refs: list[str] | None = None,
                     surface_refs: list[str] | None = None) -> dict:
    """Criteria are written in glossary terms and name the surface a test
    would exercise; neither list is decoration."""
    _must_exist(ctx, "tickets", ticket_id)
    if _about_the_tests(text):
        raise ValueError(
            "a criterion names what the program does; this one names the "
            "Tester's job. Say what the script does for a valid name and "
            "for an empty or wrong one -- the tests that validate it are "
            "the Tester's to write from that")
    # The same words are the same criterion -- `brief.segment`'s rule, two
    # artefacts along. The over-production disease grew a criteria organ the
    # day the mode was handed candidate callables: eleven criteria for one
    # item, two of them the identical sentence. Same ticket, same words, one
    # row; a session that wants a second criterion writes a second sentence.
    words = " ".join((text or "").lower().split())
    twin = next((w[1] for w in ctx.writes
                 if w[0] == "criteria" and isinstance(w[2], dict)
                 and " ".join(w[2].get("text", "").lower().split()) == words
                 and w[2].get("ticket_id") == ticket_id), None) or (
        lambda r: r["id"] if r else None)(ctx.conn.execute(
            "SELECT id FROM criteria WHERE ticket_id = ? AND "
            "lower(trim(text)) = ?", (ticket_id, words)).fetchone())
    if twin:
        raise ValueError(
            f"those are {twin}'s words already, on the same ticket. The same "
            f"words are the same criterion; if the ticket needs a second "
            f"criterion, it needs a second sentence")
    surface = _vet_surface(ctx, surface_refs, required=False)
    ctx.writes.append(("criteria", id, {
        "ticket_id": ticket_id, "text": text,
        "term_refs": json.dumps(term_refs or []),
        "surface_refs": json.dumps(surface)}))
    out = {"id": id}
    if not surface:
        out["note"] = ("no surface named. The Tester is black-box: your words "
                       "are the whole of what it gets, and a criterion that "
                       "does not say what a test would *call* is one it can "
                       "only restate")
    return out


@op("criteria", "respecify")
def criteria_respecify(ctx: Ctx, id: str, text: str,
                       term_refs: list[str] | None = None,
                       surface_refs: list[str] | None = None) -> dict:
    """
    Rewrite a criterion that was discovered unencodable or wrong.

    `specify` inserts, so a second specify of the same id dies on the primary
    key inside the transaction -- and that was the whole of why a criterion,
    once written, stayed wrong: the writing mode's predicate fires per ticket
    *without* criteria, and no other mode could touch one. Every stable red in
    the delivery cluster sat downstream of "discovered bad, no path to
    repair".

    The ticket is not a parameter. Respecifying is rewording what done means
    for the same piece of work; moving a criterion to another ticket would be
    a different act with different consequences, and the id already knows
    where it lives.
    """
    _must_exist(ctx, "criteria", id)
    if _about_the_tests(text):
        raise ValueError(
            "a criterion names what the program does; this one names the "
            "Tester's job. Rewrite it as what the script does for a valid "
            "name and for an empty or wrong one")
    # Rewording with the same words repairs nothing. The repair session on
    # walk twenty-eight respecified three criteria with their own text and
    # left the fourth, which was the one that could not be encoded.
    cur = ctx.conn.execute("SELECT text FROM criteria WHERE id = ?", (id,)).fetchone()
    if cur and _same_words(text, cur["text"]):
        return {"id": id, "unchanged": True,
                "note": "those are the criterion's own words; a repair changes "
                        "what a test can assert, and this did not. If this "
                        "criterion is right as it stands, the one that cannot "
                        "be encoded is a different row"}
    payload: dict = {"text": text,
                     "surface_refs": json.dumps(
                         _vet_surface(ctx, surface_refs, required=True))}
    if term_refs is not None:
        payload["term_refs"] = json.dumps(term_refs)
    ctx.writes.append(("criteria", id, payload, False))
    return {"id": id, "respecified": True}


@op("criteria", "load")
def criteria_load(ctx: Ctx, batch_id: str | None = None) -> list[dict]:
    bid = batch_id or ctx.batch_id
    if bid:
        # `tested_by` travels with the row. Walk eleven: three criteria had
        # tests and one did not, and every wake re-triaged and re-encoded
        # all four -- the mode could not see which debt was its own.
        rows = _rows(ctx.conn.execute(
            "SELECT c.id, c.ticket_id, c.text, c.term_refs, c.surface_refs, "
            "(SELECT t.id FROM tests t WHERE t.criterion_id = c.id LIMIT 1) "
            "AS tested_by "
            "FROM criteria c JOIN batch_tickets bt ON bt.ticket_id = c.ticket_id "
            "WHERE bt.batch_id = ?", (bid,)))
        for r in rows:
            if r.get("tested_by") is None:
                del r["tested_by"]
    else:
        # No batch, but a subject: a Tester woken by an answer about a term
        # is woken about the criteria that use it. Measured on the register
        # (TS-apply-a-term, both models, 2026-09-01): with nothing running
        # this returned [] and the mode had no criterion in view at all --
        # llama invented `c_456`, qwen said "no criteria were mentioned" and
        # waited. The wake's refs are the subject; a criterion named by
        # them, or naming a term they name, is what the answer bears on.
        rows = []
        for ref in ctx.wake_refs or ():
            rows.extend(_rows(ctx.conn.execute(
                "SELECT c.id, c.ticket_id, c.text, c.term_refs, c.surface_refs "
                "FROM criteria c WHERE c.id = ? OR c.term_refs LIKE ? "
                "ORDER BY c.id", (ref, f'%"{ref}"%'))))
        seen = set()
        rows = [r for r in rows if not (r["id"] in seen or seen.add(r["id"]))]
    # An empty surface is not a fact worth pushing: the readers of this row
    # cannot write one, and a visible "[]" reads as an omission to chase --
    # measured sending the Developer off to ask what a criterion meant
    # instead of fixing what the verdict named.
    for r in rows:
        if r.get("surface_refs") in ("[]", "", None):
            del r["surface_refs"]
    return rows


@op("criteria", "consult")
def criteria_consult(ctx: Ctx) -> list[dict]:
    # Same scope rule as `tickets.scan`: the wake's batch, then its items,
    # and only a subjectless wake reads the world.
    if ctx.batch_id:
        return _rows(ctx.conn.execute(
            "SELECT c.id, c.ticket_id, substr(c.text,1,120) AS headline "
            "FROM criteria c JOIN batch_tickets bt ON bt.ticket_id = c.ticket_id "
            "WHERE bt.batch_id = ? ORDER BY c.id", (ctx.batch_id,)))
    woken = _woken_items(ctx)
    if woken:
        marks = ",".join("?" * len(woken))
        return _rows(ctx.conn.execute(
            f"SELECT c.id, c.ticket_id, substr(c.text,1,120) AS headline "
            f"FROM criteria c JOIN tickets t ON t.id = c.ticket_id "
            f"WHERE t.item_id IN ({marks}) ORDER BY c.id", woken))
    return _rows(ctx.conn.execute(
        "SELECT id, ticket_id, substr(text,1,120) AS headline FROM criteria ORDER BY id"))


@op("criteria", "scan")
def criteria_scan(ctx: Ctx) -> list[dict]:
    return criteria_consult(ctx)


@op("batches", "group")
def batches_group(ctx: Ctx, id: str, ticket_ids: list[str],
                  item_id: str | None = None) -> dict:
    """
    Collision judgement. Batches are complete feature sets, immutable once
    formed: only a scope change may recompose one.

    Both references are checked here, and for the reason `tests.encode` already
    states: a row naming something that does not exist fails a foreign key
    *inside the transaction* and takes the session with it, when it is
    recoverable -- the model can be told and try again.

    Measured on a real repository. Architect's first call was right, naming the
    one real ticket, and it then grouped five more times passing **criteria**
    ids. All six staged, `batch_tickets.ticket_id` references `tickets(id)`, and
    the commit raised `FOREIGN KEY constraint failed` -- losing the whole
    session including the grouping that was correct. Three sessions running, and
    an approved item never got a batch.

    `_must_exist` names the ids that would have worked, so a wrong one costs a
    turn instead of the session.
    """
    for tid in ticket_ids:
        _must_exist(ctx, "tickets", tid)
    if not item_id:
        # Every ticket already names its item. One distinct item across the
        # named tickets is not a judgement; it is the row.
        owners = sorted({r["item_id"] for tid in ticket_ids for r in
                         ctx.conn.execute("SELECT item_id FROM tickets WHERE id = ?",
                                          (tid,))})
        if len(owners) == 1:
            item_id = owners[0]
        else:
            raise ValueError(
                f"item_id is required: the named tickets trace to "
                f"{owners or 'no items'} and a batch delivers exactly one "
                f"approved item.")
    _must_exist(ctx, "items", item_id)
    # A batch id is never reused. S0 walk thirty-four: after the cancel, the
    # Architect grouped the same tickets under id="b1" and the upsert
    # resurrected the abandoned batch -- its worktree, its regressed code,
    # its head commit -- which "abandoned is terminal" exists to forbid.
    prior = ctx.conn.execute("SELECT status FROM batches WHERE id = ?",
                             (id,)).fetchone()
    if prior:
        raise ValueError(
            f"{id} is already a batch ({prior['status']}), and a batch is never "
            f"re-formed under its old id -- the abandoned one is the record of "
            f"what happened to it. Give the new batch a new id")

    # One item's open work is one batch. The over-production investigation
    # (2026-08-28) found the disease's dominant form is *re-issuance* -- a
    # model re-emits an act it already performed, and any artefact whose id
    # is model-invented turns each re-issue into a new row. Every organ that
    # healed did so by deriving identity from content (constraint slug,
    # statement span, ticket words, criteria words); batches were the last
    # organ without a natural key, and both delivery runs duly made b2 and
    # b3, pending, from one sentence. The item is the batch's identity:
    # priority moves batches whole, and only a scope change may recompose
    # one -- so a second open batch for the same item is the same batch,
    # re-issued.
    open_twin = ctx.conn.execute(
        "SELECT id, status FROM batches WHERE item_id = ? "
        "AND status IN ('pending', 'running', 'deferred')",
        (item_id,)).fetchone()
    staged_twin = next((w[1] for w in ctx.writes if w[0] == "batches"
                        and isinstance(w[2], dict)
                        and w[2].get("item_id") == item_id), None)
    twin = staged_twin or (open_twin and open_twin["id"])
    if twin:
        raise ValueError(
            f"{item_id}'s work is already batched as {twin}. A batch "
            f"delivers exactly one approved item and an item's open work is "
            f"one batch -- reorder it with problem.prioritize, or recompose "
            f"it through a scope change; grouping it again would make a "
            f"second gate for the same work")

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

@op("tests", "triage")
def tests_triage(ctx: Ctx, criterion_id: str, verdict: str) -> dict:
    """
    The branch claim: every criterion gets a verdict before it gets a test.

    The mandatory-fork experiment, from the principal's question ("are we
    sure we framed the escalation correctly?"). The three-way routing has
    been in the brief the whole time, as prose under a production headline
    -- and both models skip prose to follow headlines, measured across all
    three routing reds. So the judgement stops being skippable: it is an
    act, performed per criterion, and `tests.encode` refuses a criterion
    that has not been claimed encodable. Both branches are completions; a
    routed criterion is a job done.

    The verdict is two-way, ruled 2026-09-01. The fork's own measurement:
    the can/cannot judgment arrives at 14B, the word/sentence/fact taxonomy
    is beyond every local tier tested -- and the taxonomy only ever existed
    to pick a desk, which the `unresolved` ladder and `criterion_repair`
    already pick mechanically. So `cannot` is a complete verdict: it goes to
    the nearest desk and climbs on its own if the answer does not land. The
    three named kinds stay accepted as sharper claims that route straight to
    their owner, for a model that genuinely holds the distinction.
    """
    _must_exist(ctx, "criteria", criterion_id)
    if not hasattr(ctx, "triaged"):
        ctx.triaged = {}
    ctx.triaged[criterion_id] = verdict
    done = ctx.conn.execute("SELECT id FROM tests WHERE criterion_id = ?",
                            (criterion_id,)).fetchone()
    if done:
        return {"criterion": criterion_id, "verdict": verdict,
                "next": f"nothing -- {done['id']} already encodes it; the "
                        f"criteria you were woken for are the ones without "
                        f"a tested_by"}
    nxt = {
        "encodable": "encode it: tests.encode names this criterion",
        "cannot": "say what stops you: msg.question_terminologist with the "
                  "criterion in refs and what you cannot do in the question. "
                  "You do not have to know whose problem it is -- an answer "
                  "that does not land climbs to the right desk on its own",
        "ambiguous_word": "a word could mean more than one thing: "
                          "msg.question_terminologist with the criterion in "
                          "refs and the word in the question",
        "no_machine_check": "no machine could check the sentence however the "
                            "words are read: msg.question_vision_keeper with "
                            "the criterion in refs",
        "outside_fact": "checking needs a fact this project does not hold: "
                        "msg.question_researcher, saying what fact",
    }[verdict]
    # A cannot re-judged is not a question re-owed. `tests_missing` fires per
    # batch while *any* criterion lacks a test, so a batch with one routed
    # criterion and three encodable ones wakes this mode again with the routed
    # one still testless -- and the second session would ask the same question
    # into the same open thread. The state says it is already travelling.
    if verdict != "encodable":
        open_q = ctx.conn.execute(
            "SELECT id FROM messages WHERE from_role = 'tester' "
            "AND verb = 'question' AND status IN ('open', 'unresolved') "
            "AND body_refs LIKE ?", (f'%"{criterion_id}"%',)).fetchone()
        if open_q:
            nxt = (f"already asked -- {open_q['id']} is open about this "
                   f"criterion and the answer will wake you. Encode the "
                   f"others or end the session")
    return {"criterion": criterion_id, "verdict": verdict, "next": nxt}



_STOP = {"the", "and", "for", "you", "your", "with", "this", "that", "from",
         "are", "was", "not", "but", "has", "have", "its", "into", "than",
         "then", "there", "here", "when", "what", "who", "how", "any", "all",
         "one", "two", "per", "via", "use", "used", "using", "set", "get",
         "new", "old", "yes", "true", "false", "none", "test", "tests"}


def _stem(w: str) -> str:
    """Crude and symmetric: 'tombstoned', 'tombstones', 'tombstoning' meet."""
    for suf in ("ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[:-len(suf)]
    return w


def _words(s: str) -> set[str]:
    import re as _re
    return {_stem(w) for w in _re.findall(r"[a-z]{3,}", (s or "").lower())}


def _material_words(ctx: Ctx, criterion_id: str) -> set[str]:
    """Every word the material said about this criterion."""
    words = _words
    material: set[str] = set()
    crit = ctx.conn.execute(
        "SELECT text, term_refs, surface_refs, ticket_id FROM criteria "
        "WHERE id = ?", (criterion_id,)).fetchone()
    if crit:
        material |= words(crit["text"]) | words(crit["surface_refs"])
        tk = ctx.conn.execute("SELECT text, item_id FROM tickets WHERE id = ?",
                              (crit["ticket_id"],)).fetchone()
        if tk:
            material |= words(tk["text"])
            it = ctx.conn.execute("SELECT text FROM items WHERE id = ?",
                                  (tk["item_id"],)).fetchone()
            if it:
                material |= words(it["text"])
        for ref in _refs_list(crit["term_refs"]):
            g = ctx.conn.execute("SELECT term, sense_short, sense_body FROM "
                                 "glossary_terms WHERE id = ?", (ref,)).fetchone()
            if g:
                material |= words(g["term"]) | words(g["sense_short"]) | words(g["sense_body"])
    for row in ctx.conn.execute("SELECT text FROM statements"):
        material |= words(row["text"])
    for row in ctx.conn.execute("SELECT text FROM entries WHERE author = 'principal'"):
        material |= words(row["text"])
    for row in ctx.conn.execute("SELECT term FROM glossary_terms"):
        material |= words(row["term"])
    return material


def _invented_literals(ctx: Ctx, criterion_id: str, tree) -> list[str]:
    """String literals in the body carrying a word the material never said."""
    import ast as _ast
    import re as _re

    words = _words
    material = _material_words(ctx, criterion_id)

    docstrings = set()
    for n in _ast.walk(tree):
        if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.Module)):
            if (n.body and isinstance(n.body[0], _ast.Expr)
                    and isinstance(n.body[0].value, _ast.Constant)):
                docstrings.add(id(n.body[0].value))
    out: list[str] = []
    for n in _ast.walk(tree):
        if (isinstance(n, _ast.Constant) and isinstance(n.value, str)
                and id(n) not in docstrings and len(n.value) >= 3):
            # Code-shaped strings are addresses, not choices: a dotted or
            # slashed path with no spaces ('builtins.input', 'tests/x.py',
            # 'utf-8') names something rather than saying something. An
            # underscored word is not one -- walk twenty-eight's
            # 'valid_data' and 'expected_output' were placeholders the
            # test chose, and the exemption let them through.
            if " " not in n.value and _re.search(r"[./:\-]", n.value):
                continue
            chosen = words(n.value) - material - _STOP
            if chosen and n.value not in out:
                out.append(n.value)
    return out


def _refs_list(raw) -> list[str]:
    import json as _json
    try:
        v = _json.loads(raw) if isinstance(raw, str) else (raw or [])
    except ValueError:
        return []
    return [r for r in v if isinstance(r, str)] if isinstance(v, list) else []

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
    # The fork is mandatory where the mode offers it: an encode is only legal
    # for a criterion this session has claimed encodable. The other three
    # verdicts name their owner, and taking that door is equally a completion.
    if hasattr(ctx, "triaged") and ctx.triaged.get(criterion_id) != "encodable":
        raise ValueError(
            f"{criterion_id} has no branch claim. tests.triage it first -- "
            f"verdict 'encodable' and then encode, or 'cannot', which routes "
            f"the criterion to the desk that can repair it instead")

    # A test is Python the harness can run. S0 measured the alternative: the
    # criterion restated as an English sentence, path 'script', harness says
    # "no tests ran", and the fix loop can never converge because there is
    # nothing to fix. Mechanical on purpose -- ast.parse has no opinion about
    # quality, only about whether pytest will collect anything at all.
    import ast as _ast

    if not path.endswith(".py"):
        raise ValueError(
            f"path {path!r} is not a Python file. The harness runs pytest; "
            f"name the file test_<thing>.py")
    try:
        tree = _ast.parse(body)
    except SyntaxError as exc:
        raise Wall(
            f"the body is not Python ({exc.msg}, line {exc.lineno}). A test "
            f"is code the harness can execute -- def test_...(): with "
            f"assertions, not a description of one") from None
    has_test = any(isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef))
                   and n.name.startswith("test") for n in _ast.walk(tree))
    has_assert = any(isinstance(n, _ast.Assert) for n in _ast.walk(tree))
    if not (has_test and has_assert):
        raise Wall(
            "pytest will collect nothing from this body: it needs a "
            "def test_...() containing at least one assert. A sentence about "
            "the criterion is the criterion again, not a test of it")

    # Two facts about the harness, not judgements about the test. S0 walk
    # eight: four tests, each calling `input()` and asserting on `print()`,
    # failed nine rounds while the Developer challenged and the Tester held
    # -- "the test checks the greeting is displayed" -- because neither of
    # those can ever pass under pytest: stdin is captured and reading it
    # raises, and print returns None. A test that cannot pass against any
    # code is not a definition of done, and the refusal names the shapes
    # that can.
    calls = [n for n in _ast.walk(tree) if isinstance(n, _ast.Call)]
    names = {n.func.id for n in calls if isinstance(n.func, _ast.Name)}
    if "input" in names and "monkeypatch" not in body and "builtins" not in body:
        raise Wall(
            "this test calls input(), and pytest captures stdin: the call "
            "raises OSError before any assertion runs, against any code. "
            "Feed the name in instead -- monkeypatch.setattr('builtins.input', "
            "lambda _='': 'Alice') -- or test the function that takes the "
            "name as an argument")
    # And a third harness fact, from walk nine: `assert test_valid_input()`
    # against a name the test neither imports nor defines is a NameError
    # before any code is consulted. The floor puts the project root on the
    # import path; the test says where the thing comes from.
    import builtins as _builtins
    defined = {n.name for n in _ast.walk(tree)
               if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef))}
    for n in _ast.walk(tree):
        if isinstance(n, (_ast.Import, _ast.ImportFrom)):
            defined |= {(a.asname or a.name).split(".")[0] for a in n.names}
        elif isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
            defined |= {a.arg for a in n.args.args}
        elif isinstance(n, (_ast.Assign,)):
            defined |= {t.id for t in n.targets if isinstance(t, _ast.Name)}
        elif isinstance(n, _ast.For) and isinstance(n.target, _ast.Name):
            defined.add(n.target.id)
    # Narrow on purpose: only names shaped like tests. A bare `prorate()` may
    # be a conftest's doing and the register's own scripted bodies call it
    # unimported; `test_valid_input()` is a test calling a test that exists
    # nowhere, which is the measured shape and a certain NameError.
    # Widened on walk thirteen: `validate_input("Alice")` and
    # `handle_input_error("")`, neither test-shaped, neither imported, four
    # NameErrors the Developer read as "functions that do not exist in the
    # code" and never fixed. Under the floor a bare name resolves through
    # the module's own imports or not at all; a star import is the one
    # shape that could define anything, and it exempts the file.
    star = any(isinstance(n, _ast.ImportFrom) and any(a.name == "*" for a in n.names)
               for n in _ast.walk(tree))
    # Every binding form, so a loaded name is judged against all of them.
    for n in _ast.walk(tree):
        if isinstance(n, _ast.Name) and isinstance(n.ctx, (_ast.Store, _ast.Del)):
            defined.add(n.id)
        elif isinstance(n, (_ast.Global, _ast.Nonlocal)):
            defined |= set(n.names)
        elif isinstance(n, _ast.ExceptHandler) and n.name:
            defined.add(n.name)
        elif isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.Lambda)):
            a = n.args
            defined |= {x.arg for x in a.args + a.kwonlyargs + a.posonlyargs}
            if a.vararg:
                defined.add(a.vararg.arg)
            if a.kwarg:
                defined.add(a.kwarg.arg)
    # Walk twenty-five: `assert script.run(valid_input) == expected_output`
    # with neither name defined anywhere -- not a call, so the call-only
    # check missed it, and the Developer eventually defined the names in
    # script.py and deleted the three working functions to make it pass.
    unbound = [] if star else sorted({
        n.id for n in _ast.walk(tree)
        if isinstance(n, _ast.Name) and isinstance(n.ctx, _ast.Load)
        and n.id not in defined and not hasattr(_builtins, n.id)})
    # Walk twelve: `script.run(valid_input)` with `script` imported nowhere.
    # A module used as a name and never imported is the same certainty.
    unbound += sorted({c.func.value.id for c in calls
                       if isinstance(c.func, _ast.Attribute)
                       and isinstance(c.func.value, _ast.Name)
                       and c.func.value.id not in defined
                       and not hasattr(_builtins, c.func.value.id)})
    if unbound:
        raise Wall(
            f"the test uses {unbound[0]} and never imports or defines it: a "
            f"NameError against any code. A test calls the program -- import "
            f"the function the criterion's surface names and assert on what "
            f"it returns")
    # One program, one name. Walk thirty-two: three tests imported `script`,
    # one imported `main`, script.py was written and main.py never was, and
    # the odd test failed at import for the rest of the batch. While the
    # batch's module does not exist yet, a test that names a different one
    # is naming a second program.
    import re as _re
    _mods = lambda body: set(_re.findall(r"^\s*(?:import|from)\s+([A-Za-z_]\w*)",
                                         body or "", _re.M)) - {
        "pytest", "unittest", "sys", "os", "re", "json", "io", "typing",
        "pathlib", "math", "random", "collections", "builtins"}  # noqa: E731
    mine = _mods(body)
    others: dict[str, int] = {}
    for row in ctx.conn.execute(
            "SELECT body FROM tests WHERE criterion_id != ?", (criterion_id,)):
        for m in _mods(row["body"]):
            others[m] = others.get(m, 0) + 1
    if mine and others:
        agreed = max(others, key=others.get)
        try:
            root = _worktree_of(ctx) if ctx.batch_id else None
        except Exception:               # noqa: BLE001 -- no worktree yet is "does not exist"
            root = None
        exists = bool(root) and ((root / f"{agreed}.py").exists() or (root / agreed).is_dir())
        odd = sorted(m for m in mine if m not in others)
        if odd and agreed not in mine and not exists:
            raise ValueError(
                f"this test imports {odd[0]}, and the batch's other tests import "
                f"{agreed} -- one program, one name. Import from {agreed} like "
                f"the others; a second module is a second program")

    # A fixture the harness does not have fails every test at setup. Walk
    # twenty-nine: four tests took `mocker` (pytest-mock, not installed),
    # every run was an error before the first assertion, and the Developer
    # diagnosed it exactly and had no door. The floor is plain pytest; its
    # own fixtures are the set, plus any the file defines itself.
    own = {n.name for n in _ast.walk(tree)
           if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef))
           and any((isinstance(d, _ast.Attribute) and d.attr == "fixture")
                   or (isinstance(d, _ast.Name) and d.id == "fixture")
                   or (isinstance(d, _ast.Call) and (
                       (isinstance(d.func, _ast.Attribute) and d.func.attr == "fixture")
                       or (isinstance(d.func, _ast.Name) and d.func.id == "fixture")))
                   for d in n.decorator_list)}
    builtin_fixtures = {"monkeypatch", "capsys", "capfd", "capsysbinary",
                        "capfdbinary", "caplog", "tmp_path", "tmp_path_factory",
                        "tmpdir", "tmpdir_factory", "request", "recwarn",
                        "pytestconfig", "cache", "record_property",
                        "record_testsuite_property", "doctest_namespace",
                        "testdir", "pytester", "monkeypatch_session"}
    for fn in (n for n in _ast.walk(tree)
               if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef))
               and n.name.startswith("test")):
        unknown = [a.arg for a in fn.args.args
                   if a.arg not in builtin_fixtures and a.arg not in own
                   and a.arg != "self"]
        if unknown:
            raise Wall(
                f"{fn.name} takes {unknown[0]!r}, and the harness has no such "
                f"fixture -- plain pytest, nothing installed on top -- so "
                f"every run errors at setup before the first assertion. Use "
                f"monkeypatch (monkeypatch.setattr('builtins.input', "
                f"lambda _='': 'Alice')), capsys for printed output, or "
                f"define the fixture in the file")
    asserts = [n for n in _ast.walk(tree) if isinstance(n, _ast.Assert)]
    if asserts and all(isinstance(a.test, _ast.Constant) for a in asserts):
        # Walk ten: `assert True` under "unit tests must validate the
        # script's behaviour" -- a criterion that is not a behaviour, met
        # with a test that is not a check. The honest verdict was `cannot`.
        raise Wall(
            "every assertion here is on a constant, so the test checks "
            "nothing and would report as coverage. If the criterion names "
            "no behaviour a call could exercise, that is tests.triage "
            "verdict='cannot' -- say what stops you and route it")
    for a in asserts:
        # Walk thirteen: `assert print(...) == "Hello Alice!"` -- the print
        # moved inside a comparison and the guard on the bare call missed it.
        if any(isinstance(n, _ast.Call) and isinstance(n.func, _ast.Name)
               and n.func.id == "print" for n in _ast.walk(a.test)):
            raise Wall(
                "`assert print(...)` is always False -- print returns None. "
                "Capture what was printed (capsys.readouterr().out) and "
                "assert on that, or assert on the value the function returns")

    # The criterion is checked *first*, because the batch is derived from it and
    # a derivation from a bad input fails in terms of the derived thing. An
    # invented `criterion_id` used to come back as "no batch in this session and
    # none given" -- true, unactionable, and about the one argument the model was
    # never given and cannot supply. Ten identical retries in one session, on a
    # case that had passed 130 times out of 140, and the fault was named nowhere
    # in the message. `_must_exist` names the ids that would have worked.
    _must_exist(ctx, "criteria", criterion_id)

    # A body that says no more than the criterion says has encoded nothing.
    #
    # The brief already asks for this -- "writing a test that passes trivially is
    # worse than writing none, because it reports as coverage" -- and two cases
    # measured what the sentence achieves alone. Both criteria were deliberately
    # unencodable, one asking for something no machine could check and one
    # needing a fact about somebody else's spec, and in ten runs of ten the
    # session opened by saving the criterion's own words back as the test,
    # before looking anything up. Having written a test it then had nothing left
    # to do, and the question it owed went to whichever role was nearest.
    #
    # Deliberately narrow. It is a copy that is detected, not a shape: a body
    # can be a sentence and still be doing the work -- "the billing entity that
    # owes money, not the login identity" applies a sense the criterion left
    # open -- and a guard demanding syntax would refuse that one too.
    text = ctx.conn.execute(
        "SELECT text FROM criteria WHERE id = ?", (criterion_id,)).fetchone()
    if text is not None and _same_words(body, text["text"]):
        raise Wall(
            f"that is {criterion_id}'s own sentence written back, so nothing has "
            f"been encoded and a test that reports as coverage would exist. If "
            f"there is nothing you can add to it, the criterion is what is "
            f"wrong, and saying so is the work of this session: "
            f"msg.question_terminologist(refs=['{criterion_id}'], "
            f"question='what would make this checkable?') if its words cannot "
            f"be turned into an assertion, "
            f"msg.question_vision_keeper(refs=['{criterion_id}'], "
            f"question='what observable behaviour is promised here?') if no "
            f"machine could check what it promises. And if you already asked "
            f"and the answer changed nothing, schedule.reask(what_is_missing="
            f"'words a test can assert') -- that is what routes the criterion "
            f"to its writer for repair. Retrying the same sentence is the one "
            f"move that cannot land")

    # The first assumptions detector (ruled 2026-08-30: introspection is
    # abandoned, divergence is detected). A string literal in the test whose
    # words the material never said -- not the criterion, its ticket and
    # item, the glossary, the principal's words, the criterion's surface --
    # is a place the material underdetermined the test and the Tester chose.
    # The sentence is demanded there and only there: the encode goes through
    # once a ledger row carries the literal. Walk eight's tests chose
    # 'Enter your name: ' and 'Alice' where the principal said neither.
    invented = _invented_literals(ctx, criterion_id, tree)
    if invented:
        said = [w for t, i, *rest in ctx.writes if t == "ledger"
                for w in [rest[0].get("default_taken", "")]]
        said += [r["default_taken"] for r in ctx.conn.execute(
            "SELECT default_taken FROM ledger WHERE about_ref = ?",
            (criterion_id,))]
        covered = set()
        for d in said:
            covered |= _words(d)
        owed = [lit for lit in invented
                if _words(lit) - covered - _STOP - _material_words(ctx, criterion_id)]
        if owed:
            raise ValueError(
                f"the test chooses {owed[0]!r}, and nothing in the criterion, "
                f"its ticket, the glossary or the principal's words says it. "
                f"That is an assumption, and it is logged where it is made: "
                f"ledger.log(about_ref={criterion_id!r}, about_table='criteria', "
                f"assumption=\"the test assumes {owed[0]} where the material "
                f"is silent\") -- then send this encode again unchanged")

    batch_id = batch_id or ctx.batch_id or _batch_of_criterion(ctx, criterion_id)
    if not batch_id:
        raise ValueError(
            f"{criterion_id} exists and belongs to no batch, and this session "
            f"was not woken for one, so there is nothing to attach the test to")
    _must_exist(ctx, "batches", batch_id)

    # Re-encoding a test byte for byte is not a write, and staging it as one
    # bumps a version to record that nothing happened. A Tester defending a
    # test it had decided was correct did exactly this: answered the challenge
    # properly, explaining what in the criterion its assertion came from, and
    # saved the identical body back on the way past.
    #
    # Reported rather than refused. The session did nothing wrong and there is
    # nothing for it to correct, so an error would only invite it to try
    # something else -- which is how a guard turns one wasted call into a lost
    # session.
    prior = ctx.conn.execute(
        "SELECT path, body FROM tests WHERE id = ?", (id,)).fetchone()
    if prior and prior["path"] == path and prior["body"] == body:
        return {"id": id, "unchanged": True,
                "note": "identical to what is already on file, so nothing was "
                        "written and no version moved."}

    # One test per criterion, which is the brief's first line and was held by
    # nothing. A session that could not encode a criterion honestly wrote a
    # paraphrase, then wrote the same paraphrase again under a new id, then
    # again -- narrating each as a fresh test that "considers the term webhook".
    # Four rows against one criterion is not coverage of it four times over; it
    # is one unanswered question wearing four hats, and Critic downstream cannot
    # tell the difference.
    #
    # Reported rather than refused, for the same reason as the byte-identical
    # re-encode above: the session has already said what it has to say about
    # this criterion, and an error invites it to say it a fifth way.
    done = [w for w in ctx.writes
            if w[0] == "tests" and w[2].get("criterion_id") == criterion_id]
    if done:
        return {"id": done[0][1], "unchanged": True,
                "note": f"{criterion_id} already has a test this session "
                        f"({done[0][1]}), and one criterion takes one. Nothing "
                        f"was written. If that test is wrong, this is not the "
                        f"session that discovers it."}

    # One file per test. Walk twelve: two tests named tests/test_input_
    # validation.py, the second overwrote the first on disk, and the harness
    # ran a file that encoded one criterion under two ids.
    clash = ctx.conn.execute(
        "SELECT id FROM tests WHERE path = ? AND id != ? AND batch_id = ?",
        (path, id, batch_id)).fetchone()
    if clash is None:
        clash = next((w for w in ctx.writes if w[0] == "tests" and w[1] != id
                      and w[2].get("path") == path), None)
        clash = {"id": clash[1]} if clash else None
    if clash:
        raise ValueError(
            f"{path} is already {clash['id']}'s file; two tests in one file "
            f"overwrite each other on disk. Name this one for its own "
            f"criterion -- tests/test_<what it checks>.py")
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
               assumption: str) -> dict:
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
    # The world-audit found ledger rows about 'glossary' and 'problem.assert'
    # -- table names and tool names where a row id belongs, unresolvable at
    # read time. An assumption is about a row; the table half already has its
    # own parameter.
    if not ref_resolves(ctx, about_ref):
        raise ValueError(
            f"{about_ref!r} names no row. about_ref is the id of the row the "
            f"assumption is about (about_table says which table); if it is "
            f"about the whole area, use the @-prefixed area name")

    import hashlib

    digest = hashlib.sha256(
        f"{about_table}|{about_ref}|{assumption}".encode()).hexdigest()[:10]
    id = f"l_{digest}"
    ctx.writes.append(("ledger", id, {
        "about_ref": about_ref, "about_table": about_table,
        "default_taken": assumption, "status": "open", "author": ctx.role}))
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
    # A decision is a thing *you* decided, and adopting what you were told is
    # not one. A Vision Keeper handed "no, I meant closing the account, not
    # deleting it" amended the item correctly and then filed a decision reading
    # "the principal rejected the original wording, and I have amended it to
    # reflect their intention" -- a tidy note that signs the role's name to the
    # principal's choice, in the one log that exists to keep that straight.
    #
    # Two rewrites of the brief did not move it, at 10/115 across every prompt
    # this case has ever had. The amended item is already the record; the note
    # only looks like diligence, and diligence is the hardest thing to argue a
    # model out of in prose.
    #
    # Narrow on purpose: it is the *same item, same session* pair that is a
    # minute. Deciding about something you did not just amend is untouched, and
    # so is defending an item -- because defending means you did not amend it.
    # The subject only, never the refs. `refs` is how a decision points at its
    # context, so refusing on them refused decisions that merely *mentioned*
    # something amended -- and the Vision Keeper ending an exhausted batch does
    # exactly that. Refused, it invented a fresh id and tried again, six times,
    # superseding itself down a spiral it never came out of: twelve turns, no
    # commit, every write discarded. A guard the model can walk into repeatedly
    # is worse than no guard, because the session dies instead of the call.
    #
    # The subject is still caught, which is what the rule was for: the contested
    # session passed the *item's own id* as the decision id.
    #
    # And an id *built from* the item's id is the same subject. Measured on
    # the register (VK-amend-a-contested-item, 2026-09-01): the cross-table id
    # guard fired first on the item's own id, its message said "prefix it with
    # what it is", and the model did -- `c_` plus the item id -- and the minute
    # landed. Two guards keyed on the same signal have to agree on it.
    amended = {i for t, i, *_ in ctx.writes if t == "items"}
    minuted = next((i for i in amended if i == id or i in id), None)
    if minuted:
        raise ValueError(
            f"you amended {minuted} this session, so a decision "
            f"about it would be minuting your own edit. The amended item is the "
            f"record -- a decision is something you decided, and taking the "
            f"correction you were given is not. Report it and stop.")

    # Both of these are foreign keys, and a dangling one does not fail the call
    # -- it fails `session_commit`, which takes the whole session down with an
    # `IntegrityError` naming no column. Fourteen turns of a Vision Keeper's work
    # were discarded that way, and the model was never told why.
    #
    # `resolves_ledger` reads like a flag and got `True`, which is a boolean in
    # a column that references `ledger(id)`. Saying so costs a turn; the commit
    # cost the session.
    staged = {i for t, i, *_ in ctx.writes if t == "decisions"}
    if resolves_ledger is not None and not isinstance(resolves_ledger, str):
        raise ValueError(
            f"resolves_ledger is the id of the ledger entry this decision "
            f"closes, not whether it closes one; you sent "
            f"{resolves_ledger!r}. Leave it out if no assumption is resolved.")
    if resolves_ledger:
        _must_exist(ctx, "ledger", resolves_ledger)
    if supersedes and supersedes not in staged:
        _must_exist(ctx, "decisions", supersedes)

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
    # A tester-challenge and a verdict are two answers to one question, and
    # only one can be this session's: the challenge disputes the measuring
    # instrument, so nothing can be judged until it lands. Measured on the
    # register (CR-a-test-that-encodes-nothing, 2026-09-01): the Critic
    # challenged, then talked itself into "it's not necessary to challenge
    # at this stage" and emitted a fail on top -- the dispute travelling and
    # the batch judged, both.
    #
    # Scoped to the recipient (ruled 2026-09-03): a challenge to the
    # *developer* disputes the code, which is what a fail verdict records --
    # the verb-generic form refused a correct fail-naming-its-criterion
    # verdict five of five (CR-fail-names-its-criterion, re-earned
    # 2026-09-02). The recipient is the mechanical distinction; anything
    # finer is a judgement in disguise.
    staged = [m for m in getattr(ctx, "outbound", [])
              if m.get("verb") == "challenge" and m.get("to_role") == "tester"]
    if staged:
        raise ValueError(
            "you have already challenged the tester this session, and that "
            "is your judgement of this commit until the challenge lands. "
            "A verdict on top of it would judge against a test you just "
            "said is in dispute -- end the session here")
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
# schedule (derived, with one exception)
# ---------------------------------------------------------------------------

@op("schedule", "consult")
def schedule_consult(ctx: Ctx) -> list[dict]:
    return _rows(ctx.conn.execute(
        "SELECT before_batch, after_batch FROM schedule_deps ORDER BY before_batch"))


# The verbs that open a question somebody is waiting on an answer to. `ask` is
# the read-only inquiry route, `question` the escalation ladder; both leave the
# asker blocked, which is the condition `reask` reports.
ASKING_VERBS = ("question", "ask")


@op("schedule", "reask")
def schedule_reask(ctx: Ctx, what_is_missing: str) -> dict:
    """
    The answer came back and left you where you were.

    Named for the action rather than the condition. The first sessions to reach
    it called `schedule.unresolved(still_missing=True)`, then `False` -- both
    names read as fields on a form, so the model set a flag instead of taking an
    action, repeatedly, and the case it was standing in cost five runs out of
    five. The state it produces is still called `unresolved`, which is right:
    the condition is a condition and the call is a call.

    The one declared transition in a register that is otherwise entirely
    derived, and it has to be declared because the evidence disagrees with the
    truth: the question's row says `answered`, a reply exists and is on file,
    and only the asker knows it did not land. No query can tell that from a
    good answer.

    It takes no id. The question is the one this answer replies to, which the
    causal chain already knows -- and asking a role to name a message id in the
    session where it is telling us it is confused is a way to be told about the
    wrong question.

    `what_is_missing` is required and is the point of the call. The next rung
    inherits the whole thread, so it can read what was asked and what came
    back; what it cannot read is the gap between them, which is the only thing
    that stops it answering identically. This is a question, and by the rule
    that settled the mute channels, a question carries words.
    """
    # `what_is_missing=True` is what the first Architect session to reach this
    # tool passed, and the whole value of the call is in that argument: a note
    # nobody can read leaves the next rung with the thread and no idea why the
    # answer missed, which is the one thing it cannot work out for itself.
    if isinstance(what_is_missing, bool) or not str(what_is_missing or "").strip():
        raise ValueError(
            "what_is_missing is what you cannot proceed without, in words. The "
            "role this reaches gets the whole thread and can read the question "
            "and the answer for itself; what it cannot see is why the second "
            "did not settle the first")

    if not ctx.trigger:
        raise ValueError(
            "this says the answer that woke you did not resolve your question, "
            "and nothing woke you with an answer")

    row = ctx.conn.execute(
        "SELECT q.id AS qid, q.from_role AS asker, q.verb AS verb, q.status AS status "
        "FROM messages a JOIN messages q ON q.id = a.cause_id WHERE a.id = ?",
        (ctx.trigger,)).fetchone()

    # Both asking verbs. This read `!= "question"` because Developer, Tester
    # and Architect were the only askers when it was written, and they all use
    # `question`. Liaison asks an artefact's owner with `ask` -- the read-only
    # inquiry route -- so the one role that talks to the principal could not
    # say an answer had not landed, which is the case where it matters most:
    # the alternative is spending the principal's attention on "we don't know"
    # while two owners who might know have not been asked.
    if row is None or row["verb"] not in ASKING_VERBS:
        raise ValueError(
            "the message that woke you is not a reply to a question you asked")
    if row["asker"] != ctx.role:
        raise ValueError(
            f"that question was {row['asker']}'s, not yours; only the role that "
            f"asked can say the answer did not land")

    ctx.writes.append(("messages", row["qid"], {
        "status": "unresolved", "unresolved_note": what_is_missing}, False))
    return {"id": row["qid"], "status": "unresolved"}


# ---------------------------------------------------------------------------
# code — probes, not questions. The codebase is self-describing, which is why
# reading it grants no contact to its author.
# ---------------------------------------------------------------------------

@op("code", "probe")
def code_probe(ctx: Ctx, pattern: str = "") -> list[dict]:
    if not (pattern or "").strip():
        return [{"note": "an empty pattern matches everything and tells you "
                         "nothing. Probe by the name the failing test calls, "
                         "or the word you are tracing -- `code.probe("
                         "pattern='line_total')`."}]
    return _rows(ctx.conn.execute(
        "SELECT grain, grain_kind, area, fan_in FROM code_index "
        "WHERE grain LIKE ? ORDER BY fan_in DESC LIMIT 200", (f"%{pattern}%",)))


# Words that carry no meaning of their own in any codebase. Not a general
# stoplist -- these are the ones measured as noise on the first two repositories
# this ran against, where `get` topped `src/intents` and `existing` beat
# `provider`.
_NOT_VOCABULARY = {
    "get", "set", "from", "src", "index", "new", "the", "and", "for", "this",
    "that", "export", "import", "const", "let", "var", "return", "type", "path",
    "file", "name", "value", "string", "number", "boolean", "null", "void",
    "async", "await", "class", "interface", "enum", "function", "app", "add",
    "make", "run", "use", "used", "with", "not", "any", "all", "one", "two",
    "existing", "result", "data", "item", "items", "list", "map", "key", "keys",
    "ts", "js", "py", "md", "json", "yaml", "yml", "test", "tests",
    "throw", "parse", "catch", "try", "call", "check", "each", "into", "out",
    "typeof", "instanceof", "keyof", "readonly", "undefined",
    "chosen", "choose", "include", "exclude", "private", "public", "show",
    "hide", "natural", "container", "object", "property", "input", "output",
    "error", "valid", "invalid", "start", "end", "first", "last", "next",
}


# The nouns a survey session is holding when it is asked to name a sense: the
# mode, the unit of work, the tools, the artefact. Measured -- see the note in
# `glossary_amend`. None of them is ever what a word means.
# Left to the duplicate-sense guard below, which has the message earned for
# them: `sense` names which meaning, and provenance is not a meaning.
_PROVENANCE_WORDS = {"observed", "decided", "provenance"}

_FRAME_WORDS = {
    "area", "survey", "surveys", "mode", "session", "repository", "repo",
    "code", "source", "index", "glossary", "term", "terms", "project",
    "observed", "decided", "provenance", "vocabulary", "grain", "collision",
    "error", "data_storage", "storage",
    # The system prompt's own nouns. A per-area session wrote `artefact: a data
    # structure or type representing variables or properties` -- the word the
    # prompt uses for what the role owns, defined as if the project said it.
    "artefact", "artefacts", "working_set", "tool", "tools",
}


def _idents_in(text: str) -> set[str]:
    """
    The identifiers and paths in a piece of text, lowercased, as spelled.

    An identifier here is a token a person would not mistake for English: it
    has an underscore, an internal capital, a dot, a slash or a hyphen --
    `intents_to`, `TemplateVariableType`, `frontmatter.ts`, `filtered-opener`.
    A plain word is not one, because "intent" in a sentence is the word, and
    the check this feeds asks for the place the word is written down.
    """
    import re

    out: set[str] = set()
    for tok in re.findall(r"[A-Za-z_][\w./\-]*", text):
        tok = tok.strip("._/-")
        if len(tok) < 4:
            continue
        if ("_" in tok or "." in tok or "/" in tok or "-" in tok
                or re.search(r"[a-z][A-Z]", tok)):
            out.add(tok.lower())
    return out


def _words_in(text: str) -> list[str]:
    """Identifier text as the words it is made of. `getIntentsFromFM` -> intent."""
    import re

    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    out = []
    for w in re.split(r"[^A-Za-z]+", spaced):
        w = w.lower()
        if len(w) > 2 and w not in _NOT_VOCABULARY:
            if w.endswith("ies") and len(w) > 5:
                w = w[:-3] + "y"            # `properties` was becoming `propertie`
            elif w.endswith("s") and not w.endswith("ss") and len(w) > 4:
                w = w[:-1]
            out.append(w)
    return out


_PROSE_STOPWORDS = frozenset("""
    the a an and or but nor not for from with without into onto upon
    is are was were be been being will would shall should can could may
    might must have has had do does did done this that these those it its
    they them their there here what which who whom when where how why
    all any each every both either neither more most some such only own
    same so than too very just also then once
""".split())


def _prose_words(text: str) -> list[str]:
    """
    Content words for comparing what two items *say*, not what they name.

    `_words_in` exists for identifier text and its stoplist is tuned for
    that: `get`, `set`, `show` and `name` are noise in `getIntentsFromFM`
    but they are the content in "show the user's name", where reusing it
    silently discarded the two words that actually distinguish one item
    from another. This keeps everything but grammatical scaffolding --
    articles, conjunctions, prepositions, auxiliaries, pronouns -- because
    an item's text is an English sentence, not a name.
    """
    import re

    return [w for w in re.findall(r"[a-z]+", text.lower())
            if len(w) > 2 and w not in _PROSE_STOPWORDS]


def _near_duplicate(a: list[str], b: list[str], *,
                    min_shared: int = 4, min_ratio: float = 0.6) -> bool:
    """Two word lists carrying the same claim, wording aside.

    Both a floor on the count of shared words and on their share of the
    larger side: ratio alone calls two four-word items half the same on a
    two-word coincidence, and count alone lets two long, mostly-different
    items through on a handful of words they both happen to use.
    """
    if not a or not b:
        return False
    sa, sb = set(a), set(b)
    shared = len(sa & sb)
    return shared >= min_shared and shared / max(len(sa), len(sb)) >= min_ratio


def _tells_you_something(line: str) -> int:
    """
    How much a line says about a word in it.

    An import says nothing -- it names the word and moves it. The first version
    of this took the earliest lines and returned nothing but the import block at
    the top of every file, which is a listing of names again, arrived at
    differently.
    """
    import re

    t = line.strip()
    if t.startswith(("import ", "} from", "//", "*", "/*", "#")) or ' from "' in t:
        return -1
    score = 0
    if re.match(r"(export\s+)?(type|interface|enum|class|function|const|def)\s", t):
        score += 3
    if "=" in t or "(" in t:
        score += 1
    if ":" in t:
        score += 1
    if len(t) > 25:
        score += 1
    return score


@op("code", "area")
def code_area(ctx: Ctx, area: str | None = None) -> dict:
    """
    The area's source, as source, in fan-in order until the budget runs out.

    Every context this role has been given was an enumeration -- first grains,
    then words -- and an enumeration decomposes the job into one row per item.
    That is the wrong shape for this job. An `intent` cannot be defined from the
    word `intent`: it comes from a note's frontmatter under `intents_to`, it
    holds `templates`, its `newNoteProperties` hold `variables`, and running one
    makes a note. One structure, five words in it. Asked about the five words
    one at a time, every row is answerable from ordinary English -- so it was
    answered that way, correctly per row, and the whole was never assembled. The
    measured output was `intent: an intention or goal`, written before the
    session opened a file and written again unchanged after it had opened all
    three.

    A glossary is an output of understanding a system, not an input to one. So
    this hands over the system.

    It fits, which is the part worth saying plainly. `src/intents/index.ts` --
    the file declaring what an Intent *is*, with its name, templates and
    sourceNotePath -- is 891 bytes. The brief telling the model how to describe
    code it was never shown was 6,950 characters. Eight times the file.

    Fan-in order, whole files while they fit, because the most depended-upon
    file in an area is usually the one that declares its types, and a type
    declaration is the shortest true answer to "what is this". What does not fit
    is named rather than dropped: a session that knows a file was withheld can
    ask for it, and a session that does not know reads a partial area as a whole
    one.
    """
    area = area or ctx.area
    if not area:
        return {"error": "no area"}

    # The area's own files, and the ones it imports.
    #
    # An area is a folded directory and a meaning is not. `intentsSchema.yaml`
    # lists every key an intent may carry and lives in `.`;
    # `src/intents/frontmatter.ts` imports it and lives in `src/intents`. No
    # session ever saw both, so the glossary learned that intents live in
    # frontmatter and never that the key is `intents_to`. The same boundary
    # splits `Template` and `TemplateVariable` from the code that uses them.
    #
    # A file the area imports is part of what the area means, wherever it sits.
    # Depth one only: the edge is evidence that this area depends on that file,
    # and two hops out is somebody else's subject.
    #
    # The four files that carry this domain -- the intent type, the template
    # type, the variable type and the schema -- come to 4,499 bytes together,
    # and they are small for the reason they matter: a barrel or a schema is
    # where the declarations live, and a declaration is short.
    rows = list(ctx.conn.execute(
        "SELECT grain, MAX(fan_in) AS f FROM code_index WHERE area = ? "
        "AND grain_kind = 'path' GROUP BY grain", (area,)))
    own = {r["grain"]: r["f"] for r in rows}
    imported: dict[str, int] = {}
    for r in ctx.conn.execute(
            "SELECT e.dst AS g, MAX(i.fan_in) AS f FROM code_edges e "
            "JOIN code_index i ON i.grain = e.dst "
            "WHERE e.src IN (SELECT grain FROM code_index WHERE area = ?) "
            "AND i.area <> ? GROUP BY e.dst", (area, area)):
        imported[r["g"]] = r["f"] or 0

    root = _worktree_of(ctx)

    def order(item):
        # Most depended-upon first; among equals, the ones that can be shown
        # whole. Truncating a declaration loses the declaration.
        grain, fan = item
        try:
            size = (root / grain).stat().st_size
        except OSError:
            size = 1 << 30
        return (-fan, size)

    # The area's own files first, then what it imports.
    #
    # Both were merged into one dict and sorted by fan-in alone, so an imported
    # file that half the repository depends on outranked the files the session
    # was actually woken for. Measured on `cnt_p`, area
    # `src/variables/providers`: the source began with `src/variables/index.ts`
    # and `src/notice/index.ts` -- both imports -- then the area's own
    # `index.ts`, and `not_shown` held `text.ts`, `number.ts`, `note.ts`,
    # `natural_date.ts` and `folder.ts`. Every one of the five provider
    # implementations was cut, which is to say the five prompt types the key
    # calls `variable_type` and `provider` were named by the enum and never
    # shown. The area lost its own budget to its neighbours.
    #
    # An import is context for the area. It is not the area.
    paths = ([g for g, _ in sorted(own.items(), key=order)]
             + [g for g, _ in sorted(imported.items(), key=order)])
    if not _prose_allowed(ctx):
        paths = [g for g in paths if not _is_prose(g)]

    # Two passes, because completeness beats rank. In one pass the
    # highest-fan-in file that does not fit takes the remainder as a head and
    # the small files behind it are lost -- measured: `src/main.ts` at 8KB and
    # fan-in 2 ate the budget and pushed out `intentsSchema.yaml` at 2KB, which
    # is the file this whole change exists to deliver. A truncated declaration
    # is not a declaration, so whole files are taken first and a head is what
    # the leftover buys, if it buys anything.
    def take(rel, body, cut):
        shown.append((rel, body, cut))
        ctx.opened.add(_grain_path(rel))
        ctx.read_words.update(_words_in(rel))
        ctx.read_words.update(_words_in(body))
        getattr(ctx, "read_idents", set()).update(_idents_in(rel) | _idents_in(body))

    # 5,200 characters was the budget while this push fed the per-word define,
    # and it was sized for a barrel and a schema. For the survey it starved the
    # area of itself. Measured on `cnt_14b`, area `src/intents`: the session
    # was shown `index.ts` (891 bytes) and two *imported* files, and told that
    # `frontmatter.ts` and `intents.ts` -- the area's own parsing code, where
    # every frontmatter key a user writes is read by name -- "did not fit".
    # The Architect attested `none_found` for the one area in the program that
    # holds its largest commitment, and the prompt it was given was 6,644
    # characters of a 12,288-token window.
    #
    # So: the area's own files whole while they fit, then a head of each own
    # file that did not -- a head of the parser shows the keys it parses --
    # then the imports, whole, with what remains. An own file is never shown
    # less than an imported one.
    #
    # 10,000, not more. At 14,000 the same 14B that wrote well-formed calls
    # from a 7,000-character prompt wrote, from a 20,000-character one,
    # `glossary.amend: \`intent_schema\`, The structure defining ...` and
    # `outcome="found", citing` over bare paths -- nothing the parser could
    # take -- twice in a row for `src/intents`, and the area was abandoned.
    # The reader's discipline is a function of the prompt's length, and the
    # own-files-first rule is what puts the parser in front of it; the budget
    # only has to be large enough for that.
    budget, shown, omitted, bodies = 10000, [], [], {}
    for rel in paths:
        f = root / rel
        if not f.is_file():
            continue
        try:
            bodies[rel] = f.read_text(encoding="utf-8", errors="replace")
        except OSError:                                     # pragma: no cover
            continue

    HEAD = 3000
    own_rels = [r for r in bodies if r in own]
    taken: set[str] = set()
    for rel in own_rels:                                   # own, whole
        body = bodies[rel]
        if len(body) <= budget:
            take(rel, body, False); taken.add(rel)
            budget -= len(body)
    for rel in own_rels:                                   # own, heads
        if rel in taken:
            continue
        if budget > 1200:
            head = bodies[rel][:min(HEAD, budget)]
            take(rel, head, True); taken.add(rel)
            budget -= len(head)
        else:
            omitted.append(rel)
    for rel, body in bodies.items():                       # imports, whole
        if rel in taken or rel in own:
            continue
        if len(body) <= budget:
            take(rel, body, False); taken.add(rel)
            budget -= len(body)
        else:
            omitted.append(rel)

    if omitted and budget > 1200:
        rel = omitted.pop(0)
        take(rel, bodies[rel][:budget], True)
        budget = 0

    if not shown:
        return {"area": area,
                "note": f"{area!r} has no readable source. "
                        f"`surveys.attest(outcome='none_found')` is the answer."}

    parts = []
    for rel, body, cut in shown:
        label = ("----- " + rel
                 + (" — imported by this area" if rel in imported else "")
                 + (" (first part only)" if cut else "") + " -----")
        parts.append(label + chr(10) + body)
    text = (chr(10) + chr(10)).join(parts)
    out = {"area": area, "source": text}
    if omitted:
        out["not_shown"] = (f"{omitted} did not fit. `code.source` any of them "
                            f"if the ones above leave a word unexplained.")
    return out


@op("code", "prose")
def code_prose(ctx: Ctx, limit: int = 6000) -> dict:
    """
    The README, for the one phase whose job is to read it -- against the
    account, not instead of it. Everywhere else prose is withheld or on
    demand; here it is the subject.
    """
    import re as _re

    if not _prose_allowed(ctx):
        return {"note": "prose sources are off for this run: there is nothing "
                        "to reconcile. `surveys.attest(outcome='none_found', "
                        "citations=[])` is the answer."}
    paths = [r["grain"] for r in ctx.conn.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'path' ORDER BY grain")]
    readme = next((p for p in paths if _re.match(r"(?i)readme(\.|$)", p)), None)
    if readme is None:
        return {"note": "no README in the index: nothing to reconcile."}
    root = _worktree_of(ctx)
    try:
        body = (root / readme).read_text(encoding="utf-8", errors="replace")
    except OSError:                                         # pragma: no cover
        return {"note": f"{readme} could not be read."}
    body = _re.sub(r"<[^>]+>", "", body)
    cut = len(body) > limit
    ctx.opened.add(_grain_path(readme))
    ctx.read_words.update(_words_in(body))
    return {"path": readme, "text": body[:limit],
            **({"cut": f"first {limit} of {len(body)} characters"} if cut else {})}


@op("code", "front")
def code_front(ctx: Ctx) -> dict:
    """
    The program's front: what a person opening the repository reads first.

    The orientation session is woken for the whole program, before any word
    in it has been named, and what it needs is the material a maintainer
    reaches for on day one -- the manifest that says what this is, the README
    that says what it is for, the authoring surface a user writes into, and
    the declared entry point. Every one of those is computable from the index
    and the tree; none of them is an area, which is why no area-shaped survey
    ever saw them together.

    Measured on cnt before this existed: `Obsidian` 0, `plugin` 0, `note` 0,
    `template` 0 in an 8,050-character system prompt. A role told to define a
    plugin's vocabulary had never been told it was a plugin.

    Whole files while they fit, heads where they do not, and what was withheld
    is named -- the same rule `code.area` uses, for the same reason.
    """
    import re as _re

    from ..onboarding.languages import for_path

    paths = [r["grain"] for r in ctx.conn.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'path' ORDER BY grain")]
    if not paths:
        return {"note": "nothing onboarded: there is no index to read a front "
                        "from, so there is no program to orient to yet."}
    root = _worktree_of(ctx)
    indexed = set(paths)
    fan_in = {r["grain"]: r["fan_in"] for r in ctx.conn.execute(
        "SELECT grain, fan_in FROM code_index WHERE grain_kind = 'path'")}
    has_symbols = {r["g"] for r in ctx.conn.execute(
        "SELECT DISTINCT substr(grain, 1, instr(grain, '::') - 1) AS g "
        "FROM code_index WHERE grain_kind = 'symbol'")}

    def text_of(rel: str, cap: int | None = None) -> str:
        f = root / rel
        if not f.is_file():
            return ""
        try:
            body = f.read_text(encoding="utf-8", errors="replace")
        except OSError:                                     # pragma: no cover
            return ""
        return body if cap is None else body[:cap]

    # 1. Manifests: what the project says it is, to a registry.
    manifests = [p for p in paths if p.lower() in (
        "manifest.json", "package.json", "pyproject.toml", "cargo.toml",
        "go.mod", "composer.json", "setup.cfg", "setup.py")]
    # 2. The README, head only: it says what the thing is for, then goes on.
    readme = next((p for p in paths if _re.match(r"(?i)readme(\.|$)", p)), None)
    # The orientation is written from code: the README is withheld from the
    # front by default and read afterwards, against the account, by the
    # reconcile phase. `orient_prose=on` restores it for comparison runs.
    from ..core import config as _config

    try:
        _front_prose = (_prose_allowed(ctx)
                        and _config.get(ctx.conn, "orient_prose") == "on")
    except Exception:                                       # pragma: no cover
        _front_prose = _prose_allowed(ctx)
    if not _front_prose:
        readme = None
    # 3. The authoring surface: a data file the code imports. What a user
    #    writes, and therefore the side every product meaning is written from.
    surface = sorted(
        (p for p in paths if p not in has_symbols and fan_in.get(p, 0) > 0
         and p.lower() not in ("package.json", "manifest.json")),
        key=lambda p: -fan_in.get(p, 0))
    # 4. The declared entry point. Declared, never inferred: fan-in cannot
    #    find a boundary nothing inside calls.
    entries: list[str] = []
    for cfg in ("esbuild.config.mjs", "esbuild.config.js", "package.json",
                "pyproject.toml"):
        body = text_of(cfg, 6000)
        entries += _re.findall(r"entryPoints:\s*\[\s*[\"']([^\"']+)", body)
        for m in _re.findall(r"[\"']main[\"']:\s*[\"']([^\"']+)", body):
            if m in indexed:
                entries.append(m)
        for m in _re.findall(r"=\s*[\"']([\w.]+):\w+[\"']", body):   # scripts
            rel = m.replace(".", "/") + ".py"
            if rel in indexed:
                entries.append(rel)
    for guess in ("src/main.ts", "src/main.js", "src/index.ts", "src/index.js",
                  "main.ts", "main.js", "index.ts", "index.js", "main.py",
                  "app.py", "__main__.py", "cli.py", "src/main.rs", "main.go",
                  "cmd/main.go", "src/lib.rs"):
        if guess in indexed:
            entries.append(guess)
    for p in paths:
        if p.endswith("/__main__.py") or p.endswith("/main.py"):
            entries.append(p)
    entries = [e for e in dict.fromkeys(e for e in entries if e in indexed)]

    budget, shown, omitted = 5200, [], []
    # Without the README the front has to carry what its first paragraph
    # would have said, in code: a page more, for the file that reads what
    # the user writes.
    if readme is None:
        budget = 7000

    def take(rel: str, body: str, cut: bool, label: str) -> None:
        nonlocal budget
        shown.append((rel, body, cut, label))
        budget -= len(body)
        ctx.opened.add(_grain_path(rel))
        ctx.read_words.update(_words_in(rel))
        ctx.read_words.update(_words_in(body))

    # One manifest, the product's rather than the package manager's when both
    # exist: `package.json` is a build file with a dependency list, and it
    # took the room `intentsSchema.yaml` needed the first time this ran.
    manifests.sort(key=lambda m: (m.lower() == "package.json", m))
    for rel in manifests[:1]:
        body = text_of(rel)
        if body and len(body) <= min(1200, budget):
            take(rel, body, False, "manifest")
        elif body:
            take(rel, body[:800], True, "manifest")
    # The authoring surface before the README: it is the side every product
    # meaning is written from, and it is usually small.
    for rel in surface[:3]:
        body = text_of(rel)
        if not body:
            continue
        if len(body) <= min(2600, budget - 1800):
            # Said as what it is for the reader, not as what it is for the
            # indexer: the first account written from this front said "the
            # user writes values in an authoring surface, which is a data
            # file" -- the label, repeated. A schema is the shape of what a
            # user writes elsewhere.
            take(rel, body, False, "schema of the keys a user may write -- a reference "
                                   "the code imports, not the place the user writes them")
        else:
            omitted.append(rel)
    if readme:
        body = text_of(readme)
        if body:
            # The beginning that says what it is for, not the table of
            # contents: link lists and the HTML that wraps them are skipped.
            kept = [l for l in body.splitlines()
                    if not _re.match(r"^\s*([-*]\s*\[|<|</|\s*$)", l)
                    and not _re.match(r"^\s*[-*]\s*<", l)]
            head = "\n".join(kept)[:min(1400, max(600, budget // 3))]
            # And the first worked example: the first fenced block is usually
            # the README showing what a user writes, in the user's words, and
            # it is where the answer key's own vocabulary comes from.
            m = _re.search(r"```[^\n]*\n(.*?)```", body, _re.S)
            example = (m.group(1).strip() if m else "")[:800]
            if example and example not in head:
                # With the paragraph that introduces it and the sentence that
                # follows. The example alone -- `---` / `intents_to:` -- told
                # three models that intents live in "a YAML file"; the
                # sentence above it in the README says "kept at the start of a
                # note in a special place called the Frontmatter", and the one
                # below says "paste it at the start of any note". A README
                # explains its first example right around it.
                pre = body[:m.start()]
                window = pre[-700:]
                j = window.find("\n\n")
                before = (window[j:] if j >= 0 else window).strip()
                before = _re.sub(r"<[^>]+>", "", before)
                after = _re.sub(r"<[^>]+>", "", body[m.end():m.end() + 400]).strip()
                after = after.split("\n\n")[0][:300]
                head = (head + "\n\n[the README's first example, with what it says "
                        "around it]\n" + before + "\n\n" + example + "\n\n" + after)
            take(readme, head, len(head) < len(body), "README, the beginning")
    # The entry point. With prose withheld it is not the only thing left, so
    # its head is capped to leave room for the file that declares the types.
    head_cap = budget if readme is not None else min(budget, 1800)
    for rel in entries[:2]:
        body = text_of(rel)
        if not body:
            continue
        if len(body) <= head_cap:
            take(rel, body, False, "declared entry point")
        elif head_cap > 900:
            take(rel, body[:head_cap], True, "declared entry point")
        else:
            omitted.append(rel)
    # Without prose the front is the code's own front: after the entry point,
    # the most depended-upon source file that fits, whole -- the barrel or the
    # type file where the program says what its things are.
    if readme is None and budget > 700:
        for rel, _f in sorted(((r, fan_in.get(r, 0)) for r in paths
                               if for_path(r.rsplit("/", 1)[-1]) is not None
                               and r not in entries and not _is_prose(r)),
                              key=lambda x: -x[1]):
            body = text_of(rel)
            if body and len(body) <= budget:
                take(rel, body, False, "most depended-upon source")
                break
    # And the code that reads what the user writes: the importer of the
    # authoring surface. Without the README, every reader told that the
    # schema is "a reference the code imports, not the place the user writes
    # them" still wrote "users write their intents in intentsSchema.yaml" --
    # the label said where they do not, and nothing in front of it said where
    # they do. The file that imports the schema is where the user's writing
    # enters the program (`frontmatter.ts`: `getFileCache(file).frontmatter`),
    # and the edge names it. A head, because the reading is near the top.
    if readme is None and surface and budget > 900:
        shown_rels = {r for r, *_ in shown}
        readers = [r["src"] for r in ctx.conn.execute(
            "SELECT DISTINCT src FROM code_edges WHERE dst IN (%s) ORDER BY src"
            % ",".join("?" * len(surface)), tuple(surface))]
        for rel in readers:
            if rel in shown_rels or _is_prose(rel):
                continue
            body = text_of(rel)
            if not body:
                continue
            cap = min(2000, budget)
            cut = len(body) > cap
            take(rel, body[:cap] if cut else body, cut,
                 "reads what a user writes: imports the schema")
            break

    words = [r["word"] for r in ctx.conn.execute(
        "SELECT word FROM code_lexicon ORDER BY score DESC, uses DESC LIMIT 24")]

    if not shown:
        return {"note": "nothing at the front: no manifest, README, schema or "
                        "entry point in the index. `code.source` what there is."}
    parts = []
    for rel, body, cut, label in shown:
        parts.append(f"----- {rel} -- {label}"
                     + (" (first part only)" if cut else "") + " -----\n" + body)
    out = {"source": "\n\n".join(parts)}
    if words:
        out["names_the_code_declares"] = ", ".join(words)
    if omitted:
        out["not_shown"] = (f"{omitted} did not fit. `code.source` any of them "
                            f"if the front above leaves the program unexplained.")
    return out


@op("code", "vocabulary")
def code_vocabulary(ctx: Ctx, area: str | None = None) -> list[dict]:
    """
    The words this area's code uses, and the lines that use them.

    `code.survey` returns grains -- paths and symbols. The graph has always
    labelled that edge "terms in use" and it is not: it is a list of names, and
    a list of names handed to a session told to define the area's terms is a
    specification of the answer. Measured across four runs on one repository,
    21 of the 28 terms ever written were exactly a symbol name or a path
    fragment, and the rest were generic words about software. Not one was a
    concept the project uses. `getIntentFromTFile: A function that retrieves
    intents from a TFile` is a true and accurate answer to the question that was
    actually asked.

    The vocabulary is in there, spelled inside the identifiers.
    `getIntentsFromFM`, `runIntent`, `fmValidateIntent` and `Intent` are four
    occurrences of a word this project is built on, and splitting on case and
    underscore recovers it. On the same repository this puts `intent`, `note`,
    `template`, `selection` and `variable` at the top of `src/intents`, where
    the grain list put `getIntentsFromFM`.

    Each word arrives with lines that show it working, ranked so a declaration
    beats a use and an import never appears. Three lines across two files says
    more about what a word means than four hundred lines of one file, and costs
    a fiftieth of the window.

    `defined` carries the sense the glossary already holds for that word, which
    is the only reason the whole glossary was ever pushed at a survey session.
    Handed the lot, one session spent itself re-amending four terms from another
    area rather than surveying its own -- the glossary was the most actionable
    list in its prompt, so it did the glossary. This shows the overlap and
    nothing else.
    """
    from pathlib import Path
    from collections import Counter

    area = area or ctx.area
    if not area:
        return []
    paths = sorted({r["grain"].split("::")[0] for r in ctx.conn.execute(
        "SELECT grain FROM code_index WHERE area = ?", (area,))})
    if not paths:
        return []

    # Identifier decomposition is the right operation on code and the wrong one
    # on prose. Run against `.github/ISSUE_TEMPLATE/*.md` it returned `feature`,
    # `problem`, `concise`, `clear` and `you` -- ordinary English, split out of
    # ordinary English sentences, and the session dutifully defined `you`. A
    # word is vocabulary here because the code names things with it, not because
    # a sentence in a template happens to contain it.
    from ..onboarding.languages import for_path

    paths = [rel for rel in paths if for_path(rel.split("/")[-1]) is not None]
    if not paths:
        # `[]` is a vacuous signal and gets read as a strong one -- the same
        # reason `glossary.lookup` says how big the glossary is on a miss. Three
        # sessions spent twelve turns each on `.github`, whose only files are
        # markdown and YAML, working out from `[]` that there was nothing there.
        return [{"note": f"no file in {area!r} is in a language this index "
                         f"parses, so it has no vocabulary to survey. "
                         f"`surveys.attest(outcome='none_found')` is the answer, "
                         f"citing what you opened."}]

    root = _worktree_of(ctx)
    uses: Counter = Counter()
    seen: dict[str, list] = {}
    for rel in paths:
        f = root / rel
        if not f.is_file():
            continue
        try:
            body = f.read_text(encoding="utf-8", errors="replace")
        except OSError:                                     # pragma: no cover
            continue
        for n, line in enumerate(body.splitlines(), 1):
            worth = _tells_you_something(line)
            for w in set(_words_in(line)):
                uses[w] += 1
                if worth > 0:
                    seen.setdefault(w, []).append((worth, rel, n, line.strip()))

    known = {}
    for r in ctx.conn.execute("SELECT term, sense_short FROM glossary_terms"):
        known.setdefault(re.sub(r"[^a-z0-9]+", "", r["term"].lower()), r["sense_short"])

    rows: list[dict] = []
    for word, n in uses.most_common(8):
        picks, files = [], set()
        for _, rel, ln, text in sorted(seen.get(word, []), key=lambda x: -x[0]):
            if rel in files and len(picks) >= 2:
                continue
            files.add(rel)
            picks.append((rel, ln, text))
            if len(picks) == 3:
                break
        if not picks:
            continue
        # One row per word, and no example lines: the source is in the prompt
        # beside this, so lines here would be the same code twice, and the
        # `where` column that carried them was cited verbatim -- line number
        # and all -- into `surveys.attest`, which cost four abandoned areas.
        #
        # `defined` is a marker and not the text. Shown as text, beside blank
        # rows, it was a worked example of the answer: a session handed
        # `note | A note is a piece of information.` next to three empty cells
        # completed the form, matching that register, and the example it was
        # matching was the previous session's own ungrounded guess. This says
        # only that the word is taken, which is all the collision check needs.
        files = sorted({h[1] for h in seen.get(word, [])})
        rows.append({"word": word, "uses": n,
                     "in": ", ".join(f.split("/")[-1] for f in files[:4]),
                     "defined": "yes" if any(word in k or k in word
                                             for k in known) else ""})
    return rows


@op("code", "concordance")
def code_concordance(ctx: Ctx, term: str = "", limit: int = 3) -> dict:
    """
    One word, everywhere the repository uses it, organised by what kind of
    statement each line is.

    Every context this role has ever been given is shaped like a *place*: an
    area's grains, an area's words, an area's source. A meaning is not shaped
    like a place. `intent` is declared in `intentsSchema.yaml`, parsed in
    `src/intents`, stored in `src/settings`, extended in `src/templates` and
    filled from `src/variables` -- no area contains it, so no area-shaped
    question could produce it, and none did. This is the same index pivoted on
    the word.

    The first version ranked lines by how much they "said" -- declarations,
    then the busiest uses -- and for the five words the answer key built its
    probe around that was the wrong order. `note` is used 133 times in the
    README as the ordinary word and once as a member of `enum
    TemplateVariableType`; the line that settles what `note` *is* here is
    `of_type: "text|number|natural_date|note|folder"`, and neither that line nor
    the enum member was in the view. The model defined the document, three runs
    out of three, with the deciding line a few hundred bytes away.

    So the view is sections, in the order a maintainer would weigh them:

        declared as a kind      a member of an enum, with the enum's header
        in what a user writes   lines of the authoring surface that say the word
        a file of its own       a file named for the word, and what it declares
        registered              the word as a key: `[Type.word]: handler`
        declared                the word's own declarations, types before functions
        used                    the busiest uses, prose files last and fewest
        flows                   the imports between the files that say it

    Each section is capped; the whole view is still a few kilobytes. What is
    shown is recorded as read, for the glossary's gate.
    """
    from pathlib import Path

    from ..core.scheduler import term_of
    from ..onboarding.languages import for_path
    from ..onboarding.lexicon import MANIFESTS, parts as _parts, singular as _sing

    term = (term or (ctx.wake_refs[0] if ctx.wake_refs else "")).split("#")[0]
    term = term_of(term) or term          # `@term:intent` is the subject `intent`
    want = set(_words_in(term)) or {_slug_of(term)}
    need = [_sing(w) for w in _parts(term)]

    def hits(line: str) -> bool:
        if len(need) > 1:
            return set(need) <= {_sing(w) for w in _parts(line)}
        return bool(want & set(_words_in(line)))

    paths = sorted({r["grain"].split("::")[0] for r in ctx.conn.execute(
        "SELECT grain FROM code_index")})
    if not paths:
        return {"term": term, "files": 0, "areas": 0,
                "where": "nothing onboarded: there is no index to read."}
    area_of = {r["grain"].split("::")[0]: r["area"] for r in ctx.conn.execute(
        "SELECT grain, area FROM code_index")}
    fan_in = {r["grain"]: r["fan_in"] for r in ctx.conn.execute(
        "SELECT grain, fan_in FROM code_index WHERE grain_kind = 'path'")}
    has_symbols = {r["g"] for r in ctx.conn.execute(
        "SELECT DISTINCT substr(grain, 1, instr(grain, '::') - 1) AS g "
        "FROM code_index WHERE grain_kind = 'symbol'")}

    root = _worktree_of(ctx)
    seen_words = getattr(ctx, "read_words", None)
    idents = getattr(ctx, "read_idents", None)

    def note_read(rel: str, line: str) -> None:
        if seen_words is not None:
            seen_words.update(_words_in(line))
            seen_words.update(_words_in(rel))
        if idents is not None:
            idents.update(_idents_in(line) | _idents_in(rel))

    DECL = re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?"
                      r"(enum|interface|type|class|const|function|def|struct)\s+(\w+)")
    ENUM_OPEN = re.compile(r"^\s*(?:export\s+)?(?:const\s+)?enum\s+(\w+)|"
                           r"^\s*class\s+(\w+)\s*\(\s*(?:\w+\.)?(?:Int|Str)?Enum\s*\)")
    kinds: list[str] = []          # enum member lines, with the header before them
    surface: list[str] = []        # authoring-surface lines
    own_files: list[str] = []      # a file named for the word, and its declarations
    registered: list[str] = []
    decl: list[str] = []
    uses: list[tuple] = []
    hit_files: list[str] = []
    shown_lines: set[tuple] = set()

    word_re = None
    if len(need) == 1:
        word_re = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(need[0]) + r"s?(?![A-Za-z0-9])",
                             re.IGNORECASE)

    prose_ok = _prose_allowed(ctx)
    for rel in paths:
        if not prose_ok and _is_prose(rel):
            continue
        f = root / rel
        if not f.is_file():
            continue
        try:
            body = f.read_text(encoding="utf-8", errors="replace")
        except OSError:                                     # pragma: no cover
            continue
        lines = body.splitlines()
        name = rel.rsplit("/", 1)[-1]
        is_code = for_path(name) is not None
        hit = [(n, l.strip()) for n, l in enumerate(lines, 1) if hits(l)]
        if not hit and not (set(need) <= {_sing(w) for w in _parts(name.rsplit(".", 1)[0])}):
            continue
        if hit:
            hit_files.append(rel)

        # A file named for the word: what it declares, whether or not it says
        # the word on those lines. `providers/note.ts` declares the note
        # prompt's frontmatter parser and value getter, and that is the
        # shortest true account of what a `note` is here.
        stem_words = {_sing(w) for w in _parts(name.rsplit(".", 1)[0])}
        if is_code and set(need) <= stem_words and len(own_files) < 14:
            heads = [(n, l.strip()) for n, l in enumerate(lines, 1) if DECL.match(l)][:5]
            if heads:
                own_files.append(f"  {rel}")
                for n, l in heads:
                    own_files.append(f"      {n}: {l[:110]}")
                    shown_lines.add((rel, n)); note_read(rel, l)

        if is_code:
            # Enum members: the codebase saying "this is one of the kinds".
            enum_name, depth_in = None, 0
            for n, raw in enumerate(lines, 1):
                m = ENUM_OPEN.match(raw)
                if m and enum_name is None:
                    enum_name = m.group(1) or m.group(2)
                    header = (rel, n, raw.strip())
                    hdr_line = n
                    depth_in = 1 if "{" in raw else 0
                    py_enum = m.group(2) is not None
                    continue
                if enum_name is not None:
                    inside = (depth_in > 0) if not py_enum else (raw.startswith((" ", "\t")) or not raw.strip())
                    if not py_enum:
                        depth_in += raw.count("{") - raw.count("}")
                    if inside and hits(raw) and len(kinds) < 12:
                        if header is not None:
                            kinds.append(f"  {header[0]}:{header[1]}  {header[2][:110]}")
                            shown_lines.add((rel, header[1])); note_read(rel, header[2])
                            header = None
                        kinds.append(f"      {n}: {raw.strip()[:110]}")
                        shown_lines.add((rel, n)); note_read(rel, raw)
                        # The enum and its other members, for the guard:
                        # the block's own member lines, from the header to
                        # the closing brace, and nothing outside it -- and
                        # only when the member *is* the word (`note = "note"`,
                        # `natural_date` for `date`), not merely contains it:
                        # `intent_name` in `ReservedVariableName` is not what
                        # an intent is one of.
                        facts = getattr(ctx, "kind_facts", None)
                        mem = re.match(r"^\s*([A-Za-z_]\w*)", raw)
                        mp = [_sing(w) for w in _parts(mem.group(1))] if mem else []
                        is_member = bool(mp) and (mp == need or mp[-len(need):] == need)
                        if facts is not None and enum_name and is_member:
                            sib, k = [], hdr_line
                            while k < len(lines):
                                m2 = lines[k]
                                if k > hdr_line - 1 and "}" in m2:
                                    break
                                mm = re.match(r"^\s*([A-Za-z_]\w*)\s*(?:=|,|$)", m2)
                                if mm and mm.group(1) not in (enum_name,) and                                         not set(_words_in(mm.group(1))) == want and                                         mm.group(1).lower() != need[-1]:
                                    sib.append(mm.group(1))
                                k += 1
                            # A word may be a member of two enums (`folder`
                            # in `TemplateVariableType`, `in_folder` in
                            # `ReservedVariableName`): the one whose member
                            # *is* the word names its kind; a suffix match
                            # only if nothing better has.
                            exact = mp == need
                            if exact or "enum" not in facts:
                                facts["enum"] = enum_name
                                facts["siblings"] = sib[:12]
                            elif not facts.get("exact"):
                                facts["siblings"] = [x for x in dict.fromkeys(
                                    (facts.get("siblings") or []) + sib)][:12]
                            if exact:
                                facts["exact"] = True
                    if (not py_enum and depth_in <= 0) or (py_enum and raw.strip() and not raw.startswith((" ", "\t")) and n > header[1] if header else False):
                        enum_name = None
                    if not py_enum and depth_in <= 0:
                        enum_name = None
            # The word as an enum of its own: its members are its meaning.
            facts = getattr(ctx, "kind_facts", None)
            if facts is not None:
                for n, raw in enumerate(lines, 1):
                    m = ENUM_OPEN.match(raw)
                    # The enum *is* the word: its name's words are the word's,
                    # not merely contain them. `TemplateVariableType` is not
                    # the enum of `template`, and telling the session it was
                    # produced "a template is one of five kinds".
                    en = (m.group(1) or m.group(2) or "") if m else ""
                    if m and [_sing(w) for w in _parts(en)] == need:
                        members = []
                        for m2 in lines[n:n + 30]:
                            if "}" in m2 and not m2.strip().startswith("{"):
                                break
                            mm = re.match(r"^\s*([A-Za-z_]\w*)\s*(?:=|,|$)", m2)
                            if mm:
                                members.append(mm.group(1))
                        if members:
                            facts["members"] = members[:12]
            # Registrations: the word as a key in a mapping.
            for n, l in hit:
                if word_re and re.search(r"\[\s*\w+\." + re.escape(need[0]) + r"\s*\]\s*:", l, re.I) \
                        or re.match(r"^\s*['\"]?" + re.escape(need[-1]) + r"['\"]?\s*:", l, re.I):
                    if len(registered) < 8 and (rel, n) not in shown_lines:
                        registered.append(f"  {rel}:{n}  {l[:110]}")
                        shown_lines.add((rel, n)); note_read(rel, l)
            for n, l in hit:
                if DECL.match(l) and (rel, n) not in shown_lines:
                    decl.append(f"{rel}:{n}  {l[:110]}")
        else:
            is_surface = (rel not in has_symbols and name.lower() not in MANIFESTS
                          and (fan_in.get(rel, 0) > 0
                               or name.lower().endswith((".yaml", ".yml", ".toml"))))
            if is_surface:
                for n, l in hit:
                    if len(surface) < 10:
                        surface.append(f"  {rel}:{n}  {l[:110]}")
                        shown_lines.add((rel, n)); note_read(rel, l)
                    facts = getattr(ctx, "kind_facts", None)
                    if facts is not None and word_re and "|" in l:
                        opts = [o.strip() for o in re.split(r"[|\s\"'()]+", l.split(":", 1)[-1])
                                if o.strip() and re.match(r"^[A-Za-z_]+$", o.strip())]
                        if any(word_re.fullmatch(o) for o in opts):
                            facts.setdefault("options", [])
                            facts["options"] = [o for o in dict.fromkeys(
                                facts["options"] + [o for o in opts
                                                    if not word_re.fullmatch(o)])][:12]

        if hit:
            prose = name.lower().endswith((".md", ".rst", ".txt"))
            # A prose file keeps more candidates than it will normally show:
            # if the word turns out to be prose-only, those lines are the
            # whole evidence and the render gives them the room.
            best = sorted(hit, key=lambda x: -_tells_you_something(x[1]))[
                :(8 if prose else limit)]
            uses.append((rel, area_of.get(rel, "?"), len(hit), prose,
                         [(n, l) for n, l in best if _tells_you_something(l) > 0
                          and (rel, n) not in shown_lines]))

    flow = [f"{r['src']} -> {r['dst']}" for r in ctx.conn.execute(
        "SELECT src, dst FROM code_edges")
        if r["src"] in set(hit_files) and r["dst"] in set(hit_files)]

    # Declarations ranked by whether they declare *this* word: a declaration
    # whose declared name is the word outranks one that merely mentions it,
    # and a type outranks a function that returns it.
    KIND = {"enum": 0, "type": 0, "interface": 0, "class": 1, "struct": 1,
            "const": 2, "function": 2, "def": 2}

    def rank(line: str) -> tuple:
        m = re.search(r"(enum|interface|type|class|const|function|def|struct)\s+(\w+)", line)
        if not m:
            return (9, 9)
        kind, nm = m.group(1), m.group(2)
        got = {_sing(w) for w in _parts(nm)} if len(need) > 1 else set(_words_in(nm))
        key = set(need) if len(need) > 1 else want
        named = 0 if got == key else (1 if key & got else 2)
        return (named, KIND.get(kind, 3))

    decl.sort(key=lambda d: rank(d.split("  ", 1)[-1]))
    for d in decl[:8]:
        note_read(d.split(":", 1)[0], d)
    if seen_words is not None:
        seen_words.update(_words_in(term))

    out: list[str] = []
    if kinds:
        out.append("declared as a kind:")
        out += kinds
    if surface:
        out.append("in what a user writes:")
        out += surface
    if own_files:
        out.append("a file of its own:")
        out += own_files
    if registered:
        out.append("registered:")
        out += registered
    if decl:
        out.append("declared:")
        out += [f"  {d}" for d in decl[:6]]
    code_spoke = bool(kinds or surface or own_files or registered or decl
                      or any(not pr for _, _, _, pr, _ in uses))
    if uses and not code_spoke:
        # Every hit is prose: this is the README's word, not the code's. The
        # one-line prose cap below guards against a README out-shouting the
        # code; here there is no code to out-shout, and these lines are the
        # whole evidence for what the prose means by the word.
        out.append("the code never says this word; the prose does:")
        for rel, area, n, prose, best in sorted(uses, key=lambda x: -x[2])[:2]:
            out.append(f"  {rel}  x{n}")
            for ln, l in best[:8]:
                out.append(f"      {ln}: {l[:150]}")
                note_read(rel, l)
    else:
        out.append("used:")
        # Code first, prose last; the busiest first within each. Capped so the
        # whole view, with the declaring file, stays under the render cap.
        ordered = sorted(uses, key=lambda x: (x[3], -x[2]))
        for rel, area, n, prose, best in ordered[:6]:
            out.append(f"  {rel}  [{area}]  x{n}")
            for ln, l in (best[:1] if prose else best[:2]):
                out.append(f"      {ln}: {l[:110]}")
                note_read(rel, l)
    if flow:
        out.append("flows:")
        out += [f"  {e}" for e in flow[:8]]

    # The declaring file, whole. Three lines of `providers/note.ts` say that a
    # note prompt exists; the file says what it does -- calls another plugin's
    # `api_getNote` with a filter set and validates what comes back -- and that
    # is the meaning. The probes' "declaring file" variant picked the file
    # naively and scored nothing; the sections above pick it: a file named for
    # the word, else the file holding its top-ranked declaration. Whole while
    # it fits, a head when it does not, and named either way.
    declaring = None
    # The file that declares the word as a type, when one does -- `export type
    # Intent` in `index.ts` over `intents.ts`, which is merely named for it --
    # else the file named for it, else the file of its top declaration.
    if decl and rank(decl[0].split("  ", 1)[-1]) <= (0, 1):
        declaring = decl[0].split(":", 1)[0]        # a type, enum, interface or class of that name
    if declaring is None:
        for line in own_files:
            if not line.startswith("      "):
                declaring = line.strip(); break
    if declaring is None and decl:
        declaring = decl[0].split(":", 1)[0]
    file_block = ""
    if declaring:
        f = root / declaring
        if f.is_file():
            try:
                body = f.read_text(encoding="utf-8", errors="replace")
            except OSError:                                     # pragma: no cover
                body = ""
            if body:
                cut = len(body) > 2000
                file_block = ("----- " + declaring + (" (first part only)" if cut else "")
                              + " -----" + chr(10) + body[:2000])
                ctx.opened.add(_grain_path(declaring))
                note_read(declaring, body[:2000])

    result = {"term": term,
              "files": len(hit_files),
              "areas": len({area_of.get(r, "?") for r in hit_files}),
              "where": chr(10).join(out)}
    if file_block:
        result["declaring_file"] = file_block
    return result


@op("code", "gaps")
def code_gaps(ctx: Ctx) -> dict:
    """
    The run's own gaps, recomputed from its record: what it could not read,
    what it gave up on, what nobody checked. Facts for the blind-spot
    session to weigh -- the numbers are mechanical, the judgement of which
    matter is the session's.
    """
    from collections import Counter as _Counter

    lines: list[str] = []
    suf: _Counter = _Counter()
    known = {".py", ".js", ".jsx", ".mjs", ".ts", ".tsx", ".go", ".rs",
             ".java", ".rb"}
    benign = {".md", ".rst", ".txt", ".yaml", ".yml", ".toml", ".json",
              ".cfg", ".ini", ".css", ".scss", ".html", ".svg", ".xml", ""}
    prose = 0
    for r in ctx.conn.execute(
            "SELECT grain FROM code_index WHERE grain_kind = 'path'"):
        name = r["grain"].rsplit("/", 1)[-1]
        ext = ("." + name.rsplit(".", 1)[-1].lower()) if "." in name else ""
        if ext in (".md", ".rst", ".txt"):
            prose += 1
        if ext not in known and ext not in benign:
            suf[ext or name] += 1
    for ext, n in suf.most_common(6):
        if n >= 3:
            lines.append(f"{n} {ext} files no parser reads: their contents "
                         f"never reached a session")
    quarantined = [r["tick_key"] for r in ctx.conn.execute(
        "SELECT tick_key FROM tick_attempts WHERE quarantined = 1")]
    for q in quarantined[:6]:
        lines.append(f"given up after the attempt bound: {q}")
    checked = ctx.conn.execute(
        "SELECT COUNT(*) FROM survey_records WHERE area = '@prose'").fetchone()[0]
    if prose > 3 and checked:
        lines.append(f"{prose} prose files indexed; reconcile checked the "
                     f"root README and nothing else")
    if prose > 3 and not checked:
        lines.append(f"{prose} prose files indexed and none were checked "
                     f"against the account")
    off_terms = ctx.conn.execute(
        "SELECT COUNT(*) FROM glossary_terms WHERE superseded_by IS NULL"
    ).fetchone()[0]
    lines.append(f"the glossary holds {off_terms} live terms; whether they "
                 f"are the program's vocabulary or a directory's furniture "
                 f"is visible in their areas")
    falsified = ctx.conn.execute(
        "SELECT COUNT(*) FROM challenges WHERE verdict = 'falsified'").fetchone()[0]
    if falsified:
        lines.append(f"{falsified} claim(s) stand falsified on the ledger, "
                     f"awaiting a ruling")
    return {"facts": lines}


_CLAIM_TABLES = {
    "constraints": ("headline", "text"),
    "items": ("text",),
    "glossary_terms": ("term", "sense_short", "sense_body"),
    "model_areas": ("account",),
}


def _claim_of(ctx: Ctx) -> tuple[str, str]:
    from ..core.scheduler import CLAIM_PREFIX

    ref = (ctx.wake_refs[0] if ctx.wake_refs else "") or (ctx.area or "")
    if ref.startswith(CLAIM_PREFIX):
        ref = ref[len(CLAIM_PREFIX):]
    table, _, row = ref.partition(":")
    if table not in _CLAIM_TABLES or not row:
        raise ValueError(f"{ref!r} names no claim: a claim ref is "
                         f"<table>:<row id> over {sorted(_CLAIM_TABLES)}")
    return table, row


@op("challenge", "load")
def challenge_load(ctx: Ctx) -> dict:
    """
    The claim this session was woken to attack, with the sources it cites.

    The claim's own citations travel with it -- bindings for a constraint,
    source_refs for a sense or an account -- because the attack the brief
    asks for is *this claim against those lines*, and every file shown is
    marked opened so a break's citation check can hold.
    """
    import json as _json

    try:
        table, row = _claim_of(ctx)
    except ValueError as e:
        return {"note": str(e)}
    cols = _CLAIM_TABLES[table]
    r = ctx.conn.execute(
        f"SELECT * FROM {table} WHERE id = ?", (row,)).fetchone()
    if not r:
        return {"note": f"{table}:{row} no longer exists; nothing to challenge."}
    claim = " -- ".join(str(r[c]) for c in cols if r[c])

    cited: list[str] = []
    if table == "constraints":
        cited = [b["grain"] for b in ctx.conn.execute(
            "SELECT grain FROM constraint_bindings WHERE constraint_id = ?",
            (row,))]
    else:
        try:
            cited = _json.loads(r["source_refs"] or "[]") if "source_refs" in r.keys() else []
        except Exception:
            cited = []
    root = _worktree_of(ctx)
    parts: list[str] = []
    used = 0
    for rel in cited[:6]:
        f = root / rel
        if not f.is_file() or used > 9000:
            continue
        body = f.read_text(encoding="utf-8", errors="replace")
        cap = min(4000, 12000 - used)
        cut = " (first part only)" if len(body) > cap else ""
        parts.append(f"----- {rel}{cut} -----" + chr(10) + body[:cap])
        used += min(len(body), cap)
        ctx.opened.add(_grain_path(rel))
        if getattr(ctx, "read_idents", None) is not None:
            ctx.read_idents.update(_idents_in(body[:cap]))
    return {"claim": f"[{table}:{row}] {claim}",
            "cited": cited,
            "sources": (chr(10) + chr(10)).join(parts) if parts else
                       "the claim cites nothing -- open what would decide it"}


@op("challenge", "uphold")
def challenge_uphold(ctx: Ctx, citation: str, quote: str,
                     why: str = "") -> dict:
    """
    The claim survived -- because of this line, not because nobody looked.

    Measured before the gate existed: a planted falsehood was upheld with an
    empty why. The break always demanded its evidence; an uphold that
    demands none is a free door, and a model at temperature zero takes the
    free door. Symmetric now: either verdict carries the line it stands on,
    from a file opened this session, and the Critic's judgement is which
    side the line lands on.
    """
    import re as _re

    table, row = _claim_of(ctx)
    citation = _re.sub(r"^(?:\./|/)+", "", (citation or "").strip())
    if not (quote or "").strip():
        raise ValueError("an uphold carries the line that supports the "
                         "claim: quote= the source's words. A claim nobody "
                         "checked has not survived anything.")
    if _grain_path(citation) not in ctx.opened:
        raise ValueError(f"{citation!r} was not opened this session: an "
                         f"uphold stands on a line you read. code.source "
                         f"it first.")
    ctx.writes.append(("challenges", f"{table}:{row}", {
        "verdict": "stands", "citation": citation,
        "quote": quote.strip()[:300], "why": (why or "").strip()[:300]}))
    return {"id": f"{table}:{row}", "verdict": "stands"}


@op("challenge", "break")
def challenge_break(ctx: Ctx, citation: str, quote: str, why: str) -> dict:
    """
    The claim is falsified -- by a line of source, never by an opinion.

    Models never adjudicate models: the citation must be a file this
    session opened and the quote must be carried, or the break is refused.
    The verdict is the Critic's own artefact; the consequence goes to the
    ledger for the principal -- no role touches another role's rows.
    """
    import re as _re

    table, row = _claim_of(ctx)
    citation = _re.sub(r"^(?:\./|/)+", "", (citation or "").strip())
    prior = sum(1 for fn, _why, *_ in (getattr(ctx, "refusals", None) or [])
                if fn == "challenge.break")
    flagged = ""
    bad_quote = not (quote or "").strip()
    bad_cite = _grain_path(citation) not in ctx.opened
    if (bad_quote or bad_cite) and not (why or "").strip():
        raise ValueError("a break carries at least its reason: why= what "
                         "defeats the claim")
    if bad_quote or bad_cite:
        if prior == 0:
            # Once, with the teaching. Twice would be the loop the place
            # guard documents: turn twelve of the same re-send, measured.
            raise ValueError(
                "a break carries the line and the reason: quote= the "
                "source's words, citation= a file you opened (not the "
                "claim's ref). A claim false by ABSENCE is broken by "
                "quoting the line that shows what actually happens "
                "instead. A claim no line could support or defeat is "
                "challenge.vacuous(why=...). Send the break again with "
                "its line -- or once more as it is, and it is recorded "
                "flagged on the strength of your reading.")
        if not ctx.opened:
            raise ValueError("a break, even flagged, is a reading's act: "
                             "open the claim's cited files first")
        if bad_cite:
            citation = sorted(ctx.opened)[0]
        flagged = ("evidence-flagged: no line quoted; the verdict stands "
                   "on the reader's account of what the source lacks")
    ctx.writes.append(("challenges", f"{table}:{row}", {
        "verdict": "falsified", "citation": citation,
        "quote": (quote or "").strip()[:300],
        "why": (why.strip() + (f" [{flagged}]" if flagged else ""))[:460]}))
    ctx.writes.append(("ledger", f"challenge_{_slug_of(table)}_{_slug_of(row)}", {
        "about_ref": f"{table}:{row}", "about_table": table,
        "default_taken": (f"the Critic falsified {table}:{row} against "
                          f"{citation}: \"{quote.strip()[:160]}\" -- "
                          f"{why.strip()[:160]}. The claim stands in the "
                          f"record until ruled."),
        "author": "critic"}))
    return {"id": f"{table}:{row}", "verdict": "falsified",
            "note": "recorded, and on the principal's ledger"}


@op("challenge", "vacuous")
def challenge_vacuous(ctx: Ctx, why: str) -> dict:
    """
    The claim commits to nothing a line could support or defeat.

    Measured: identifier tautologies churned three sessions each under the
    two-verdict gate -- no supporting line exists because the claim asserts
    nothing, no defeating line for the same reason. This verdict requires
    the reading (files opened this session) but not a quote, because the
    finding is precisely that no quote can bear on it. Drains to the
    ledger: an empty claim in the record is the principal's to keep or cut.
    """
    table, row = _claim_of(ctx)
    if not (why or "").strip():
        raise ValueError("say what makes it empty: why= the reason no line "
                         "could support or defeat this claim")
    if not ctx.opened:
        raise ValueError("vacuity is still a reading's verdict: open the "
                         "claim's cited files first (challenge.load or "
                         "code.source)")
    ctx.writes.append(("challenges", f"{table}:{row}", {
        "verdict": "unfounded", "why": why.strip()[:300]}))
    ctx.writes.append(("ledger", f"challenge_{_slug_of(table)}_{_slug_of(row)}", {
        "about_ref": f"{table}:{row}", "about_table": table,
        "default_taken": (f"the Critic found {table}:{row} unfounded: "
                          f"{why.strip()[:200]}. An empty claim is kept in "
                          f"the record until ruled."),
        "author": "critic"}))
    return {"id": f"{table}:{row}", "verdict": "unfounded",
            "note": "recorded, and on the principal's ledger"}


@op("code", "tree")
def code_tree(ctx: Ctx) -> dict:
    """
    The repository's top level, with the facts a frame judgement needs.

    The probe that earned this view (probes/partition_judge.py, 34/38 on six
    repositories) showed a judge three things: the tree with per-directory
    file-type counts, the README's first lines, and -- the fzf lesson -- what
    the entry files import, because a README of badges misleads a judge that
    cannot see where main points. Each entry carries the heuristic prior, so
    the session argues with a stated default rather than a blank.
    """
    from collections import Counter as _Counter

    from ..onboarding.areas import is_attached
    from ..onboarding.lexicon import MANIFESTS

    try:
        root = _worktree_of(ctx)
    except Exception:
        root = None
    paths = [r["grain"] for r in ctx.conn.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'path'")]
    tops: dict[str, list[str]] = {}
    for rel in paths:
        top = rel.split("/", 1)[0]
        # A root dot-file's classification changes nothing -- .editorconfig
        # is one file wherever it files -- and each one costs an assignment
        # the attest needs the room for. Dot-directories stay: .github is a
        # real call.
        if "/" not in rel and top.startswith("."):
            continue
        tops.setdefault(top, []).append(rel)

    def prior(top: str, members: list[str]) -> str:
        if "/" not in members[0] and top.lower() in MANIFESTS:
            return "boundary (claimed mechanically -- do not assign)"
        if all(is_attached(m) or _is_prose(m) for m in members):
            return "attached"
        return "program"

    lines = []
    for top in sorted(tops, key=str.lower):
        members = tops[top]
        if len(members) == 1 and "/" not in members[0]:
            lines.append(f"{top}  [prior: {prior(top, members)}]")
            continue
        suf = _Counter((m.rsplit(".", 1)[-1] if "." in m.rsplit("/", 1)[-1]
                        else "(none)") for m in members)
        mix = ", ".join(f".{k} x{v}" if k != "(none)" else f"(none) x{v}"
                        for k, v in suf.most_common(3))
        lines.append(f"{top}/  ({len(members)} files: {mix})  "
                     f"[prior: {prior(top, members)}]")

    entry_imports: list[str] = []
    for r in ctx.conn.execute("SELECT src, dst FROM code_edges"):
        if "/" not in r["src"]:
            entry_imports.append(f"  {r['src']} -> {r['dst']}")
    readme = next((rel for rel in sorted(paths) if "/" not in rel
                   and rel.lower().startswith("readme")), None)
    head = ""
    if readme and root is not None:
        try:
            head = chr(10).join((root / readme).read_text(
                encoding="utf-8", errors="replace").splitlines()[:10])
        except OSError:                                     # pragma: no cover
            pass
    out = "[the repository's top level, with the heuristic prior for each]"
    out += chr(10) + chr(10).join(lines)
    if entry_imports:
        out += chr(10) + chr(10) + "[what the root's own files import]"
        out += chr(10) + chr(10).join(sorted(set(entry_imports))[:12])
    if head:
        out += chr(10) + chr(10) + "[the README's first lines]" + chr(10) + head
    return {"entries": len(tops), "view": out}


# The model-facing word for the fourth class stays `boundary` -- the brief
# and the boundary phase say it -- and it files as `surface`, the value that
# shares the @surface: prefix's word.
_FRAME_KINDS = {"program": "program", "attached": "attached",
                "attach": "attached", "ignore": "ignore",
                "ignored": "ignore", "boundary": "surface",
                "surface": "surface"}


@op("frame", "load")
def frame_load(ctx: Ctx) -> list[dict]:
    """The rulings as they stand -- the judge's observed rows and any
    decided ones, which outrank and are not the judge's to touch."""
    return _rows(ctx.conn.execute(
        "SELECT id, kind, provenance, reason FROM frame_rulings ORDER BY id"))


@op("frame", "assign")
def frame_assign(ctx: Ctx, path: str, kind: str, reason: str = "") -> dict:
    """
    One frame classification, judged: everything under `path` is `kind`.

    The write is the judge's (source='judge'); a principal's ruling on the
    same prefix outranks it and is refused overwriting. Where the judgement
    disagrees with the heuristic prior, a ledger row records the difference
    with the judge's answer as the taken default -- mechanically, because
    the diff is a fact, not a claim.
    """
    from ..onboarding.areas import is_attached
    from ..onboarding.lexicon import MANIFESTS

    k = _FRAME_KINDS.get((kind or "").strip().lower())
    if not k:
        raise ValueError(f"kind must be one of program/attached/ignore/"
                         f"boundary, not {kind!r}")
    path = (path or "").strip().strip("`").rstrip("/")
    path = path.lstrip("./")
    covered = [r["grain"] for r in ctx.conn.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'path' AND "
        "(grain = ? OR grain LIKE ?)", (path, path + "/%"))]
    if not covered:
        raise ValueError(f"{path!r} covers nothing in the index; assign a "
                         f"path the tree above actually shows")
    if "/" not in path and path.lower() in MANIFESTS:
        raise ValueError(f"{path} is a manifest: claimed mechanically as a "
                         f"boundary already, not the judge's to assign")
    ruled = ctx.conn.execute(
        "SELECT provenance FROM frame_rulings WHERE id = ?", (path,)).fetchone()
    if ruled and ruled["provenance"] == "decided":
        raise ValueError(f"{path} carries a principal's ruling, which "
                         f"outranks the judge; it stands")
    # Re-sending the whole classification is the loop this session dies in
    # -- measured: three identical turns, no attest, three sessions. A
    # repeated assignment succeeds by pointing at the act that remains.
    if any(t == "frame_rulings" and i == path for t, i, *_ in ctx.writes):
        return {"id": path, "note": "already assigned this session. What "
                "remains is the ending: surveys.attest(outcome=\"found\", "
                "citations=[the entries you classified])."}

    ctx.writes.append(("frame_rulings", path,
                       {"kind": k, "provenance": "observed",
                        "reason": reason or ""}))
    heuristic = ("attached" if all(is_attached(m) or _is_prose(m)
                                   for m in covered) else "program")
    if k != heuristic:
        ctx.writes.append(("ledger", f"frame_{_slug_of(path)}", {
            "about_ref": path, "about_table": "frame_rulings",
            "default_taken": (f"the frame judge classified {path} as {k} "
                              f"({reason or 'no reason given'}); the "
                              f"heuristics said {heuristic}; the judge's "
                              f"answer is taken"),
            "author": "frame"}))
    return {"id": path, "kind": k,
            "note": ("differs from the heuristic prior; a ledger row "
                     "records it" if k != heuristic else "agrees with the "
                     "heuristic prior")}


@op("code", "boundary")
def code_boundary(ctx: Ctx, path: str = "") -> dict:
    """
    A boundary file, whole, and every file in this repository that reads it.

    The survey's counterfactual produced identifier answers because the
    session stood inside an area's source. This view stands on the boundary:
    the subject is the file the outside touches -- a schema a user writes
    against, a manifest a registry reads -- and the readers travel with it
    because "what happens when the other side writes something unknown" is
    answered by the reader's code, and the absence of a rejecting branch is
    the finding.
    """
    from ..core.scheduler import surface_of

    rel = surface_of(path) or path
    if not rel and ctx.wake_refs:
        rel = surface_of(ctx.wake_refs[0]) or ""
    if not rel:
        return {"note": "no boundary file named: this view reads the file the "
                        "wake names, or pass `path=`."}
    root = _worktree_of(ctx)
    readers = sorted({r["src"] for r in ctx.conn.execute(
        "SELECT src FROM code_edges WHERE dst = ?", (rel,))})
    budget = 12000
    parts: list[str] = []

    # The brief's question is loud-or-silent, and the deciding branch sits
    # wherever it sits. Measured: frontmatter.ts is 8.6k, the cap showed 4k,
    # and validateFmSchema -- console.warn for unknown keys, a Notice for
    # four legacy names -- was at the end of the file. The session asserted
    # silence over a truncated reader, and the constraint repeated the
    # answer key's own unchecked claim. So every reader also carries its
    # failure vocabulary, whole-file, line-numbered: the lines a truncated
    # head would have to guess about.
    _FAILS = re.compile(r"(?i)\b(throw|raise|warn|warning|error|notice|"
                        r"invalid|unknown|unrecognized|unrecognised|missing|"
                        r"reject|refuse|fail|fails|ignore|ignored|silent)\b")

    def take(p2: str, cap: int) -> int:
        f = root / p2
        if not f.is_file():
            return 0
        try:
            body = f.read_text(encoding="utf-8", errors="replace")
        except OSError:                                     # pragma: no cover
            return 0
        cut = " (first part only)" if len(body) > cap else ""
        parts.append(f"----- {p2}{cut} -----" + chr(10) + body[:cap])
        if cut:
            # From the cut region only: the head already shows the top of
            # the file, and on the first re-earn a top-first cap spent all
            # twelve lines on hits the session could already see while the
            # deciding branch at the end stayed dark.
            shown_lines = body[:cap].count(chr(10))
            all_hits = [f"      {n}: {l.strip()[:140]}"
                        for n, l in enumerate(body.splitlines(), 1)
                        if n > shown_lines and _FAILS.search(l)]
            # Both ends of the cut region. A flat cap kept exhausting itself
            # before the end of the file -- twice, measured -- and the
            # deciding branch of a validator tends to sit exactly there.
            hits = (all_hits if len(all_hits) <= 12
                    else all_hits[:6] + all_hits[-6:])
            if hits:
                parts.append(f"[{p2}: every failure-vocabulary line beyond "
                             f"the cut -- the cut cannot hide a branch]"
                             + chr(10) + chr(10).join(hits))
                for h in hits:
                    if getattr(ctx, "read_idents", None) is not None:
                        ctx.read_idents.update(_idents_in(h))
        ctx.opened.add(_grain_path(p2))
        if getattr(ctx, "read_idents", None) is not None:
            ctx.read_idents.update(_idents_in(body[:cap]) | _idents_in(p2))
        if getattr(ctx, "read_words", None) is not None:
            ctx.read_words.update(_words_in(body[:cap]))
        return len(body[:cap])

    used = take(rel, 6000)
    for rd in readers:
        if used >= budget:
            break
        used += take(rd, min(4000, budget - used))
    return {"subject": rel, "readers": readers,
            "view": (chr(10) + chr(10)).join(parts) if parts
            else f"{rel}: not on disk"}


@op("code", "survey")
def code_survey(ctx: Ctx, area: str | None = None) -> list[dict]:
    """The area's grains, most depended-upon first. Defaults to the area this
    session was woken for, which is the only one it has any business in."""
    return _rows(ctx.conn.execute(
        "SELECT grain, grain_kind, fan_in FROM code_index WHERE area = ? "
        "ORDER BY fan_in DESC", (area or ctx.area,)))


@op("code", "callables")
def code_callables(ctx: Ctx, hint: str = "") -> list[dict]:
    """
    The symbols whose names share words with the hint: candidates for a
    criterion's `surface_refs`.

    The question-matched shape again -- glossary bodies are pushed for the
    terms a question's words name, and this is the same rule pointed at the
    code index. The hint is the wake's subject (ticket text, or the asker's
    note), never the role's to choose; identifiers are split the way
    `code.vocabulary` splits them, so "export the recipes" finds
    `export_recipe_csv` and `RecipeExporter` both.
    """
    rows = _rows(ctx.conn.execute(
        "SELECT grain, sym_kind, fan_in FROM code_index "
        "WHERE grain_kind = 'symbol' ORDER BY fan_in DESC"))
    if not rows:
        return [{"note": "the index holds no symbols, so there is nothing to "
                         "match; name the surface as you intend it and it is "
                         "the design"}]
    words = set()
    for w in (hint or "").split():
        w = w.strip("`'\".,?:;()[]").lower()
        if len(w) >= 3:
            words.add(w)
            words.add(w.rstrip("s"))
    if not words:
        return rows[:20]
    hits = []
    for r in rows:
        stem = r["grain"].split("::")[-1]
        split = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", stem)
        tokens = {t for t in re.findall(r"[a-z]+", split.lower()) if len(t) >= 3}
        tokens |= {t.rstrip("s") for t in tokens}
        if tokens & words:
            hits.append(r)
    return hits[:40] or rows[:20]


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
    if not _prose_allowed(ctx) and _is_prose(path):
        return {"path": path, "note": "prose sources are off for this run: the "
                "README and documents are withheld so the program is read from "
                "its code, schema and manifest. Open a source file instead."}

    note = None
    try:
        target = _within(_worktree_of(ctx), path)
    except ValueError:
        target = None

    if target is None or not target.exists():
        hit = _indexed_like(ctx, path)
        if hit is None:
            return {"path": path,
                    "error": f"not found, and no grain in the index is named "
                             f"anything like it. `code.survey` lists the area "
                             f"you were woken for; the paths it returns are the "
                             f"ones this can open."}
        note = (f"{path!r} is not a path in this checkout; read "
                f"{hit!r}, which is the only grain it could be naming. "
                f"Cite that spelling, not yours.")
        path = hit
        target = _within(_worktree_of(ctx), path)

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
    # The corrected spelling, so a citation of it resolves against the index.
    ctx.opened.add(_grain_path(path))
    getattr(ctx, "read_idents", set()).update(_idents_in(path))
    body = chr(10).join(lines[start:end])
    ctx.read_words.update(_words_in(path))
    getattr(ctx, "read_idents", set()).update(_idents_in(body))
    ctx.read_words.update(_words_in(body))
    out = {"path": path, "start": start, "end": end,
           "text": chr(10).join(lines[start:end]), "lines": len(lines)}
    if note:
        out["note"] = note
    return out


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


# Prose: what a person wrote *about* the code rather than the code. Withheld
# from every context when `prose_sources` is off, so understanding can be
# measured on the program alone; a repository's README may be excellent and
# the next repository's may not exist.
_PROSE_SUFFIXES = (".md", ".rst", ".txt", ".adoc", ".markdown")
_PROSE_DIRS = {"docs", "doc", "documentation", "wiki", "site", "man"}


def _is_prose(path: str) -> bool:
    p = path.replace("\\", "/").lower()
    name = p.rsplit("/", 1)[-1]
    if any(seg in _PROSE_DIRS for seg in p.split("/")[:-1]):
        return True
    return name.endswith(_PROSE_SUFFIXES) or name.split(".")[0] in (
        "readme", "changelog", "changes", "contributing", "history", "news", "authors")


def _prose_allowed(ctx) -> bool:
    from ..core import config

    try:
        return config.get(ctx.conn, "prose_sources") != "off"
    except Exception:                                       # pragma: no cover
        return True


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


def _indexed_like(ctx, path: str) -> str | None:
    """
    The grain a mistyped path was reaching for, when exactly one fits.

    A path is copied by hand out of a listing, and a model copying by hand gets
    it wrong. On the Obsidian plugin it read `.github/ISSUE_TEMPLATE/bug_report.md`
    from `code.survey` and asked for `/github/ISSUE_TEMPLATE/bug_report.md` --
    the leading dot turned into a slash. `_within` refuses that as escaping the
    worktree, correctly, and the refusal is terminal: the file cannot be opened,
    so it cannot be cited, so the area cannot be closed. Eleven of that run's 88
    turns ended there, and `.github` sorts first, so it is the opening move.

    Nothing about it is specific to that directory. Any path transcribed wrong
    is unopenable, and "escapes the worktree" tells a session nothing it can act
    on.

    So a miss is checked against the index before it is refused: exactly one
    grain that the request could be naming, or nothing. One, because that is the
    rule `indexer.resolve` already applies to a bare package name -- an
    ambiguous guess is a misread, and a misread is worse than an error.

    Read only. `code.write` keeps `_within` unhelped: guessing which file a role
    meant to open costs a wasted turn, and guessing which file it meant to
    overwrite costs the file.
    """
    want = path.replace("\\", "/").strip().lstrip("/")
    while want.startswith("./"):
        want = want[2:]
    if not want:
        return None

    hits = []
    for r in ctx.conn.execute(
            "SELECT grain FROM code_index WHERE grain_kind = 'path'"):
        g = r["grain"]
        bare = g.lstrip("./")
        if want in (g, bare) or g.endswith("/" + want) or bare.endswith("/" + want):
            hits.append(g)
    return hits[0] if len(hits) == 1 else None


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

    The row is now actually gone, rather than joined by the diff. `code.read` is
    pushed into Critic's working set unasked, so `worktree` put an absolute path
    into every Critic and Developer prompt and `head_commit` put a fresh SHA
    beside it. The prompt hash is a sha256 of the whole prompt, and both of those
    change per run, so no such session could ever replay a recording — eight L1
    cases reported STALE on every suite run, three of them recorded green half an
    hour earlier. A case that cannot replay is not slow to verify, it is
    unverified, and it says so in the same words as work in progress.

    Neither was any use to the reader. A path is where the diff came from and a
    SHA is which diff it is; the question in front of Critic is what the diff
    says.
    """
    from ..core import worktrees

    bid = batch_id or ctx.batch_id
    row = ctx.conn.execute(
        "SELECT id, worktree FROM batches WHERE id = ?", (bid,)).fetchone()
    if not row:
        return {}
    out = {"batch": row["id"]}
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
    # Code is written in a batch's worktree and nowhere else. Walk
    # twenty-three: a Developer woken by a Vision Keeper's message, before
    # any batch existed, wrote script.py into the project root and then
    # met "no batch: a commit belongs to one" -- the write had already
    # landed outside every checkpoint.
    if not ctx.batch_id:
        raise ValueError(
            "no batch: code is written in a batch's worktree, and this "
            "session was not woken for one. Answer the message you were "
            "woken by; the build starts when the batch does")
    target = _within(_worktree_of(ctx), path)
    # A harness fact about modules, not a judgement about the code. S0 walk
    # ten: `script.py` was right in substance and ran `input()` at module
    # level, so every test that imported it died at collection -- OSError,
    # stdin is captured -- and the Developer escalated three times against
    # an error that names the line. Under pytest a module the tests import
    # runs at import; the shape that works is the main guard.
    if path.endswith(".py"):
        import ast as _ast
        try:
            tree = _ast.parse(text)
        except SyntaxError as exc:
            raise ValueError(
                f"{path} is not valid Python ({exc.msg}, line {exc.lineno}); "
                f"the harness imports it and would die at collection") from None
        for node in tree.body:
            if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef,
                                 _ast.ClassDef, _ast.Import, _ast.ImportFrom)):
                continue
            if (isinstance(node, _ast.If) and isinstance(node.test, _ast.Compare)
                    and any(isinstance(c, _ast.Constant) and c.value == "__main__"
                            for c in node.test.comparators)):
                continue
            # Through a local function too: walk thirty-two's
            # `name = prompt_for_name()` at module level, where the function
            # reads input, and every importing test died at collection.
            readers = {f.name for f in tree.body
                       if isinstance(f, (_ast.FunctionDef, _ast.AsyncFunctionDef))
                       and any(isinstance(n, _ast.Call) and isinstance(n.func, _ast.Name)
                               and n.func.id == "input" for n in _ast.walk(f))}
            if any(isinstance(n, _ast.Call) and isinstance(n.func, _ast.Name)
                   and (n.func.id == "input" or n.func.id in readers)
                   for n in _ast.walk(node)):
                raise ValueError(
                    f"{path} reads input() at module level (line {node.lineno}), "
                    f"so importing it under pytest raises OSError before any "
                    f"test runs -- stdin is captured. Put the prompt under "
                    f"`if __name__ == \"__main__\":` and keep the functions "
                    f"the tests import at the top level")
    # What the tests import is the name the module has to have. Walks
    # twenty-three and twenty-four: the tests said `import script`, the
    # Developer wrote greeting_script.py, the result said so, and the
    # harness said ModuleNotFoundError three sessions running. Refused in
    # the one certain case -- a new module, while the module every test
    # names does not exist yet -- and said in the result otherwise, because
    # helpers are legal once the named module is there.
    import re as _re
    wanted = set()
    for row in ctx.conn.execute(
            "SELECT body FROM tests WHERE batch_id = ?", (ctx.batch_id,)):
        wanted |= set(_re.findall(r"^\s*(?:import|from)\s+([A-Za-z_]\w*)",
                                  row["body"] or "", _re.M))
    wanted -= {"pytest", "unittest", "sys", "os", "re", "json", "io",
               "typing", "pathlib", "math", "random", "collections"}
    root = _worktree_of(ctx)
    missing = sorted(m for m in wanted if not (root / f"{m}.py").exists()
                     and not (root / m).is_dir())
    from pathlib import Path as _Path
    stem = _Path(path).stem
    # A rewrite that deletes a name the tests import breaks them with
    # certainty. Walk twenty-five: three green tests, and the fourth's fix
    # was a script.py with the three imported functions gone.
    if path.endswith(".py") and target.exists():
        try:
            old_tree = _ast.parse(target.read_text(encoding="utf-8"))
        except (SyntaxError, OSError):
            old_tree = None
        if old_tree is not None:
            new_defs = {n.name for n in tree.body
                        if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef,
                                          _ast.ClassDef))}
            old_defs = {n.name for n in old_tree.body
                        if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef,
                                          _ast.ClassDef))}
            imported = set()
            for row in ctx.conn.execute(
                    "SELECT body FROM tests WHERE batch_id = ?", (ctx.batch_id,)):
                for m in _re.finditer(
                        r"^\s*from\s+" + _re.escape(stem) + r"\s+import\s+([^\r\n]+)",
                        row["body"] or "", _re.M):
                    imported |= {x.strip().split(" as ")[0]
                                 for x in m.group(1).split(",")}
            gone = sorted((old_defs - new_defs) & imported)
            if gone:
                raise ValueError(
                    f"this rewrite of {path} drops {', '.join(gone)}, which the "
                    f"batch's tests import -- an ImportError on every test that "
                    f"does. Keep what the tests import; add to the file, do not "
                    f"replace it")
    if missing and path.endswith(".py") and not target.exists()             and stem not in wanted and not stem.startswith("test"):
        raise ValueError(
            f"the batch's tests import {', '.join(missing)} and no such "
            f"module exists yet; {path} is a name none of them use. The "
            f"name the tests import is the name the file has to have -- "
            f"write {missing[0]}.py first, helpers after")
    # And at the root. The 14B walk wrote scripts/script.py: the right name
    # in a folder `import script` cannot see, because the floor puts the
    # worktree root on the import path and nothing else.
    if (stem in missing and path.endswith(".py")
            and _Path(path).parent != _Path(".") and _Path(path).name != "__init__.py"):
        raise ValueError(
            f"{path} is not where `import {stem}` looks: the import path is "
            f"the worktree root, so the module is {stem}.py at the top level "
            f"(or {stem}/__init__.py)")
    target.parent.mkdir(parents=True, exist_ok=True)
    existed = target.exists()
    target.write_text(text, encoding="utf-8")
    out = {"path": path, "bytes": len(text.encode("utf-8")),
           "created": not existed}
    if missing and stem not in missing:
        out["note"] = (f"the batch's tests import {', '.join(missing)} and no "
                       f"such module exists in the worktree yet")
    return out


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
        # Not an error -- the docstring says why -- but the bare result read
        # as completion. Recorded after the ledger rename: the Developer
        # probed, loaded criteria, called commit on an untouched tree, logged
        # a real assumption, and ended -- five runs of five, twice, with
        # `code.write` never called. The result now carries the fork the
        # session is actually at.
        return {"committed": False, "why": "nothing changed",
                "note": ("the tree is exactly as you found it. If the "
                         "criteria are already met, say so and finish; if "
                         "you were going to change the code, the change "
                         "comes first: code.write, then commit")}

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

def _refuse(ctx: "Ctx", url: str, why: str) -> dict:
    """
    A refused fetch, remembered so it cannot be cited later.

    The refusal itself is a result and not a failure -- the brief says to answer
    with what was tried, and sessions do. What one also did was call
    `references.record` for the page it had just been told it could not have:
    one row claiming what an unread page says, with `content_hash` empty, which
    records that the claim rests on nothing in a column no reader looks at.

    Only urls this session was refused. Refusing every url without a cache hit
    was the broader rule and it took a legitimate case down with it, because the
    url a session records is not always the url `web.cached` resolves. That is a
    real question and a different one; being told no is not ambiguous.
    """
    if not hasattr(ctx, "refused"):
        ctx.refused = set()
    ctx.refused.add(url)
    ctx.refused.add(url.split("#", 1)[0])
    return {"url": url, "refused": why}


def _search_google(ctx: "Ctx", query: str) -> dict:
    """
    Google Programmable Search, which needs a key and a search-engine id.

    Both come from the environment and neither is written to the project
    database: a credential in `config` would be committed with the run, shown
    in the cockpit, and carried into whatever a session pastes. `GOOGLE_API_KEY`
    and `GOOGLE_CSE_ID` -- absent, this refuses in the same voice as `none`,
    because a role that cannot tell "nothing matches" from "I was given no way
    to look" invents the difference and cites a url it guessed.

    Results are not filtered to `research_allowlist`, and each one is marked
    with whether it is fetchable instead. Discovery is how anybody finds out a
    domain is worth granting, so filtering it would make the allowlist
    unextendable from inside; but a session that does not know which hits it
    may actually read will spend its turns being refused one at a time.
    """
    import os
    import json as _json
    import urllib.parse
    import urllib.request

    from ..core import config, web

    key, cx = os.environ.get("GOOGLE_API_KEY"), os.environ.get("GOOGLE_CSE_ID")
    if not (key and cx):
        absent = [n for n, v in (("GOOGLE_API_KEY", key), ("GOOGLE_CSE_ID", cx))
                  if not v]
        missing = " and ".join(absent)
        is_are = "is" if len(absent) == 1 else "are"
        return {"query": query, "refused":
                f"`research_search` is `google` but {missing} {is_are} not set "
                f"in the environment, so there is no way to look a url up from "
                f"here. "
                f"This is not 'found nothing' -- do not guess an address."}

    url = ("https://www.googleapis.com/customsearch/v1?"
           + urllib.parse.urlencode({"key": key, "cx": cx, "q": query, "num": 8}))
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            payload = _json.loads(response.read().decode("utf-8", "replace"))
    except Exception as exc:                       # noqa: BLE001 - reported, not raised
        return {"query": query, "refused":
                f"the search itself failed ({exc}). No result is not the same "
                f"as no such page; do not answer as though you had looked."}

    allowlist = config.get(ctx.conn, "research_allowlist") or []
    results = [
        {"url": item.get("link", ""),
         "title": item.get("title", ""),
         "snippet": item.get("snippet", ""),
         # A snippet is not a passage. Whatever is claimed from this has to be
         # quoted out of `web.fetch`, and this says which ones that is possible
         # for rather than letting the session discover it one refusal at a time.
         "fetchable": web.allowed(item.get("link", ""), allowlist)}
        for item in payload.get("items", [])
    ]
    return {"query": query, "engine": "google", "results": results,
            "note": "Snippets are search results, not sources. Fetch the page "
                    "before you claim anything from it; a `fetchable: false` "
                    "domain has not been granted and needs the principal."}


@op("web", "search")
def web_search(ctx: Ctx, query: str) -> dict:
    """
    Candidate urls for a question. Names and one line each, never pages —
    `web.fetch` reads what this finds.

    The Researcher takes questions and `web.fetch` takes addresses, and nothing
    joined them. Asked what RFC 6749 section 4.1.3 requires, a session generated
    `datatracker.ietf.org/doc/html/rfc6749#section-4.1.3` -- a plausible url for
    a real document, and not the one it had been given -- was refused, and then
    tried to record a reference for the page it never read. With a dereference
    capability, no discovery capability and a question, guessing is the only move
    that is not refusal.

    Which engine is `research_search`, and it is `none` until somebody grants it,
    for the same reason `research_allowlist` is empty: a capability that reaches
    outside the engagement is granted rather than merely not-forbidden. The
    refusal names the setting, because a role that cannot tell "nothing matches"
    from "I was given no way to look" will invent the difference.

    `cache` searches only pages already fetched. That is what the suite runs on:
    a role whose tests reached the network would be the one role whose results
    differ by machine, and every other tier here rests on that not being so.
    """
    from ..core import config, web

    engine = config.get(ctx.conn, "research_search")
    if engine == "none":
        return {"query": query, "refused":
                "no search engine is granted: `research_search` is `none`, so "
                "there is no way to look a url up from here. This is not 'found "
                "nothing' -- do not guess an address. Answer with what you were "
                "given, or say you need a url."}

    if engine == "google":
        return _search_google(ctx, query)

    if engine != "cache":
        return {"query": query, "refused":
                f"`research_search` is {engine!r}, which is not wired up yet. "
                f"Only `cache` and `google` can answer from here."}

    terms = [w.lower() for w in query.split() if len(w) > 2]
    hits = []
    for row in ctx.conn.execute("SELECT url, body FROM web_cache"):
        body = (row["body"] or "").lower()
        score = sum(1 for w in terms if w in body or w in row["url"].lower())
        if score:
            hits.append((score, row["url"], (row["body"] or "")[:160]))
    hits.sort(reverse=True)
    return {"query": query, "engine": engine,
            "results": [{"url": u, "opening": o} for _, u, o in hits[:8]]}


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
        return _refuse(ctx, url, f"research_cap of {cap} fetches is spent; "
                                 f"answer with what you have")
    try:
        # Cache-only unless the network is asked for explicitly. The default is
        # the safe direction: a test suite that could reach out would eventually
        # reach out by accident, and then one machine's results stop matching
        # another's for a reason nobody can see in the diff.
        page = web.fetch(ctx.conn, url,
                         config.get(ctx.conn, "research_allowlist"),
                         offline=not os.environ.get("ROTA_NET"))
    except web.NotAllowed as exc:
        return _refuse(ctx, url, str(exc))
    except Exception as exc:                       # unreachable, timed out, 404
        return _refuse(ctx, url, f"could not read it: {exc}")

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

    if url in getattr(ctx, "refused", set()):
        raise ValueError(
            f"your fetch of {url} was refused this session, so there is no "
            f"passage behind this claim. A reference is the evidence and not "
            f"the conclusion -- say in your answer what you tried and what it "
            f"said, and record nothing.")

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
