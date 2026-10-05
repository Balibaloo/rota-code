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

from ..core.worktrees import GIT

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
    # The wake kind, as a fact: an onboarding tick reads the code, so what
    # it writes rests on the grains it opened. `stage_grain_refs` records
    # them on that kind of wake only. On a delivery wake the same write
    # would mark a reasoned row observed.
    onboarding: bool = False
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
    # The wake kind. The park ask's door reads it: the ask's id and refs are
    # facts of the wake, and never the session's to type (frame 87).
    wake_kind: str = ""
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
    # The mandatory branch behind a fail verdict: criterion_id -> does its
    # test actually encode it, per the Critic's own claim this session.
    # `verdicts.claim_encodes` is the only way in; `verdicts.emit` reads it
    # to refuse a fail the Critic never branched on. Session-scoped like
    # `refusals` and `opened` -- the claim only has to outlive the session
    # that acts on it, and `tool_calls` already logs the call itself for
    # the record.
    verdict_claims: dict = None
    # What this session's ops shortened, one line each, for the record rather
    # than for the prompt. A silent cut writes no string at all, so a reader of
    # the record could not tell a short account from a shortened one, and the
    # principal's ledger row can be shorter than the challenge row it derives
    # from (frame 46's design record, section 2.7). The runner drains this into
    # `outcome.errors`, which `session_note` writes as the session's last turn.
    # Session-scoped like `refusals`: the reason only has to outlive the session
    # that made the cut.
    cuts: list = None
    # The files each batch's diff changed, by batch id, read once per session.
    # `batch_files` runs three git calls, about 230 ms, and `findings.find`
    # needs the list on every refusal path (frame 90's diff review, finding 1).
    diff_files: dict = None

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
        if self.verdict_claims is None:
            self.verdict_claims = {}
        if self.cuts is None:
            self.cuts = []
        if self.diff_files is None:
            self.diff_files = {}


# What a role can do about words a row did not keep: nothing, and the habit
# that makes the loss harmless. The row holds the first characters, so the
# deciding sentence belongs first.
_WORDS_NOT_KEPT = ("Nothing returns the words the row did not keep. Put what "
                   "decides it first.")


def _cut(ctx: "Ctx", what: str, kept: int, whole: int, unit: str,
         call: str = "", stored: bool = True) -> str:
    """
    Record a cut for the reader, and return the seat's notice when it has one.

    Two outputs, because two readers ask different questions. The seat asks
    what it is looking at, so the notice goes in the result through `cut_note`
    and reads like every other cut. A reader of the record asks how often the
    system shortens what a role wrote, and no prompt survives to answer that,
    so the reason goes on the session's own account.

    A site with no call for the seat passes none, and records the reason alone.
    The principal's ledger row is that case: the Critic cannot act on a row
    that is not its own, and a reader of the record still has to be able to
    count it (frame 46's design record, section 2.7).

    Keep a dot out of `what`. The recorded reason joins the session's errors,
    and `testkit.fixtures` reads the text before the first colon as a refused
    call whenever that text holds a dot. So "the batch's diff" is safe and
    "code.diff" would be counted as a refusal on every case that cuts.

    `stored` is false at a read. Nothing was written down there, so the reason
    says "not shown" rather than claiming a row holds less than it does (the
    diff review of 0cc624b).
    """
    if whole <= kept:
        return ""
    cuts = getattr(ctx, "cuts", None)
    if cuts is not None:
        cuts.append(f"cut {what}: {whole - kept} of {whole} {unit} "
                    f"{'not stored' if stored else 'not shown'}")
    if not call:
        return ""
    from ..core.runner import cut_note
    return cut_note(what, whole - kept, whole, unit, call)


def _cut_words(ctx: "Ctx", what: str, fields: dict) -> str:
    """The notice for a row that stored a prefix of what a role wrote."""
    notes = [_cut(ctx, f"{what} {name}", cap, len(text), "characters",
                  _WORDS_NOT_KEPT)
             for name, (text, cap) in fields.items()]
    return " ".join(note for note in notes if note)


def op(artefact: str, verb: str):
    """Register an implementation for one graph edge."""
    def deco(fn: Callable) -> Callable:
        REGISTRY[(artefact, verb)] = fn
        return fn
    return deco


def _rows(cur) -> list[dict]:
    return [dict(r) for r in cur.fetchall()]


def _shown_rows(cur) -> list[dict]:
    """Rows joined to a provenance view, with today's word for the value.

    The SELECT puts `provenance` where the result shows it and `basis` last.
    The basis leaves the row: a result key stays what it was (Q10)."""
    from ..core.db import shown_provenance

    rows = _rows(cur)
    for r in rows:
        r["provenance"] = shown_provenance(r["provenance"], r.pop("basis"))
    return rows


def _term_refs_of(conn: sqlite3.Connection, src_table: str, src_id: str) -> list[str]:
    """The glossary ids a row rests on, from the relation.

    In the order they were written: the result shows the list as the column
    held it, and the prompt is the cassette key."""
    return [r["target"] for r in conn.execute(
        "SELECT target FROM refs WHERE src_table = ? AND src_id = ? "
        "AND kind = 'term' ORDER BY rowid", (src_table, src_id))]


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
# refs: what a row rests on.
#
# Every writer stages the refs rows its row rests on. The `provenance` view
# derives a row's provenance from the rows, and every reader reads the view
# or the relation (frame 21). A refs write is receipted under its source
# row, so stage it after that row's own write.
# ---------------------------------------------------------------------------

GRAIN_REFS_CAP = 12

# The legal values of `refs.kind` and `refs.src_table`. The schema carries
# the same lists as a CHECK. This door refuses a bad value before the commit.
REF_KINDS = ("statement", "reference", "term", "grain", "ruling")
REF_SOURCES = ("items", "glossary_terms", "constraints", "model_areas",
               "frame_rulings", "criteria", "business_rules")


def stage_ref(ctx: Ctx, src_table: str, src_id: str, kind: str, target: str,
              resolves: int = 1) -> None:
    """Stage one refs row. The same row twice in a session is one write."""
    if kind not in REF_KINDS:
        raise ValueError(f"kind is one of {', '.join(REF_KINDS)}, not {kind!r}")
    if src_table not in REF_SOURCES:
        raise ValueError(f"{src_table!r} is not a table that carries refs")
    row_id = f"{src_table}:{src_id}:{kind}:{target}"
    last = _last_ref_write(ctx, row_id)
    if last is not None and not last[2].get("retire"):
        return
    ctx.writes.append(("refs", row_id, {
        "src_table": src_table, "src_id": src_id, "kind": kind,
        "target": target, "resolves": resolves}))


def _last_ref_write(ctx: Ctx, row_id: str):
    """The last write staged for one refs row this session, or None."""
    for w in reversed(ctx.writes):
        if w[0] == "refs" and w[1] == row_id:
            return w
    return None


def retire_ref(ctx: Ctx, src_table: str, src_id: str, kind: str, target: str) -> None:
    """Stage the removal of one refs row. `db._apply_ref` deletes the row
    and receipts the source row when a row was on file. The writes of one
    row land in the order staged, so the last one wins."""
    row_id = f"{src_table}:{src_id}:{kind}:{target}"
    last = _last_ref_write(ctx, row_id)
    if last is not None and last[2].get("retire"):
        return
    ctx.writes.append(("refs", row_id, {
        "src_table": src_table, "src_id": src_id, "kind": kind,
        "target": target, "retire": True}))


def named_statements(ctx: Ctx) -> list[str]:
    """The statements a wake names: the wake's refs, then the refs of the
    message that woke the session, each one that is a row of `statements`.
    A row written on such a wake rests on them, so decided cascades from
    a ratified statement along the refs. A wake that names no statement
    gives a reasoned row."""
    named: list[str] = list(getattr(ctx, "wake_refs", ()) or ())
    if getattr(ctx, "trigger", None):
        from ..core.db import refs_of
        row = ctx.conn.execute("SELECT body_refs FROM messages WHERE id = ?",
                               (ctx.trigger,)).fetchone()
        named += [r for r in refs_of(row["body_refs"]) if r not in named] if row else []
    return [r for r in named if ctx.conn.execute(
        "SELECT 1 FROM statements WHERE id = ?", (r,)).fetchone()]


def stage_grain_refs(ctx: Ctx, src_table: str, src_id: str,
                     grains=None, *, always: bool = False) -> None:
    """A grain ref per path this session opened, capped at `GRAIN_REFS_CAP`.
    Recorded on an onboarding wake, or when the caller says `always`."""
    if not always and not getattr(ctx, "onboarding", False):
        return
    opened = grains if grains is not None else (ctx.opened or ())
    for grain in sorted(str(g) for g in opened)[:GRAIN_REFS_CAP]:
        stage_ref(ctx, src_table, src_id, "grain", grain)


def stage_copied_refs(ctx: Ctx, src_table: str, from_id: str, to_id: str) -> None:
    """The kept row inherits the refs of a row it replaces."""
    for r in ctx.conn.execute(
            "SELECT kind, target, resolves FROM refs "
            "WHERE src_table = ? AND src_id = ? ORDER BY kind, target",
            (src_table, from_id)):
        stage_ref(ctx, src_table, to_id, r["kind"], r["target"], r["resolves"])


# The table a ref of each kind names. A grain names the index by its own
# key and has no table here (the table comment in schema.sql).
_REF_TARGET_TABLE = {"statement": "statements", "reference": "references_",
                     "term": "glossary_terms", "ruling": "rulings"}


def _ref_target_on_file(ctx: Ctx, kind: str, target: str) -> bool:
    """Whether `target` names a row of its kind: staged this session, or on
    file. A grain is on file when the index holds it, as the owner ops
    read it."""
    if kind == "grain":
        return ctx.conn.execute("SELECT 1 FROM code_index WHERE grain = ?",
                                (target,)).fetchone() is not None
    table = _REF_TARGET_TABLE[kind]
    if any(w[0] == table and w[1] == target for w in ctx.writes):
        return True
    return ctx.conn.execute(f"SELECT 1 FROM {table} WHERE id = ?",
                            (target,)).fetchone() is not None


# The owner tables behind each artefact that writes refs. The graph declares
# one `cite` edge per owner with `actor: system`: the system stages the rows
# beside the owner's own writes, and no session calls the op.
_CITE_TABLES = {
    "problem": ("items",),
    "glossary": ("glossary_terms", "business_rules"),
    "model": ("constraints", "model_areas"),
    "frame": ("frame_rulings",),
    "criteria": ("criteria",),
}


def _cite_op(artefact: str, tables: tuple[str, ...]) -> Callable:
    def cite(ctx: Ctx, id: str, kind: str, target: str) -> dict:
        """One refs row for a row of this artefact: what the row rests on."""
        table = next(
            (t for t in tables
             if any(w[0] == t and w[1] == id for w in ctx.writes)
             or ctx.conn.execute(f"SELECT 1 FROM {t} WHERE id = ?",
                                 (id,)).fetchone()), None)
        if table is None:
            raise ValueError(f"{id!r} is not a row of {artefact}")
        # The target names a row of its kind, as the owner ops check
        # before they stage a ref. A bad kind is refused by `stage_ref`.
        if kind in REF_KINDS and not _ref_target_on_file(ctx, kind, target):
            names = ("a grain of the index" if kind == "grain"
                     else f"a row of {_REF_TARGET_TABLE[kind]}")
            raise ValueError(
                f"{target!r} names no {kind}: a {kind} ref targets {names}")
        stage_ref(ctx, table, id, kind, target)
        return {"id": id, "kind": kind, "target": target}
    cite.__name__ = f"{artefact}_cite"
    return cite


for _artefact, _tables in _CITE_TABLES.items():
    op(_artefact, "cite")(_cite_op(_artefact, _tables))


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

    # Found never overwrites decided. tipsU (2026-09-09): the principal's
    # `split_bill` was delivered as decided, then orient and reorient
    # asserted it again from the code as observed, and the slicing rule
    # read it as a record of what exists. An observed session records the
    # code; a decided item is the principal's, and it stays as it is.
    if getattr(ctx, "onboarding", False):
        decided = ctx.conn.execute(
            "SELECT 1 FROM item_provenance WHERE id = ? AND provenance = 'decided'",
            (id,)).fetchone()
        if decided:
            return {"id": id, "note": (f"{id} is decided by the principal and "
                                       f"stays as it is; an observation does "
                                       f"not amend it")}
    else:
        # The other direction. clickI night 18 (2026-09-12): delivering
        # the principal's one sentence, the Vision Keeper asserted its item
        # and then the three account items from onboarding again, word for
        # word. A decided wake writes decided, so the account became
        # buildable: 119 criteria for behaviour the repository already has,
        # a batch for it ahead of the sentence's, and the Developer
        # quarantined on it. The words are the fact: the same words on an
        # observed row change nothing and build what exists.
        observed = ctx.conn.execute(
            "SELECT i.text FROM items i JOIN item_provenance p ON p.id = i.id "
            "WHERE i.id = ? AND p.provenance = 'observed'",
            (id,)).fetchone()
        if observed and observed["text"]:
            old_words = set(_prose_words(observed["text"]))
            new_words = set(_prose_words(text))
            if old_words and len(old_words & new_words) >= 0.8 * len(old_words | new_words):
                raise ValueError(
                    f"{id} is the account's observed row and these are its "
                    f"words. Asserting it again makes what the repository "
                    f"already does a thing to build. Assert only what the "
                    f"principal asked for; an observed item stays observed "
                    f"until their words change it")
            # Night 19: the same three items again, paraphrased past the
            # door above. What changes an observed item is the principal's
            # words, and this session was woken with them: the statements
            # on the wake. A text that shares none of their words is the
            # desk rewording the account, not the principal changing it.
            said: set[str] = set()
            for ref in getattr(ctx, "wake_refs", ()) or ():
                st = ctx.conn.execute(
                    "SELECT text FROM statements WHERE id = ?", (ref,)).fetchone()
                if st and st["text"]:
                    said |= set(_prose_words(st["text"]))
            if said and new_words and len(new_words & said) < 0.3 * len(new_words):
                raise ValueError(
                    f"{id} is observed, and these are not the principal's "
                    f"words: the statement you were woken with says "
                    f"something else. An observed item changes only when "
                    f"their words change it; what they asked for is its "
                    f"own item under its own name")

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
    # The account is the whole program, and a delivered statement is a
    # behaviour. tipsAI (2026-09-10): delivered "split the bill", the Vision
    # Keeper asserted `how_it_works` as the split, and the account of the
    # tip calculator was gone. Nothing slices the account, so the split was
    # never built. A fact about the words: the new account keeps none of
    # the old one's.
    # A criterion's words are a criterion, not an item. tipsAX (2026-09-12):
    # answering the Terminologist's challenge, the Vision Keeper asserted
    # the challenged criterion's sentence as a new item under the
    # criterion's own id, and the run then built "the function must divide
    # the sum" as scope beside the item it came from.
    crit_words = " ".join((text or "").lower().split())
    twin_crit = ctx.conn.execute(
        "SELECT id FROM criteria WHERE lower(trim(text)) = ?", (crit_words,)).fetchone()
    if twin_crit:
        raise ValueError(
            f"those are {twin_crit['id']}'s words, a criterion of an item that "
            f"exists. An item is what the principal asked for, in their words; "
            f"a criterion is what done means for it. Answer the challenge about "
            f"the criterion; do not make it scope")

    if id == "how_it_works":
        cur_acc = ctx.conn.execute(
            "SELECT text FROM items WHERE id = 'how_it_works'").fetchone()
        old_words = set(_prose_words(cur_acc["text"])) if cur_acc and cur_acc["text"] else set()
        new_words = set(_prose_words(text))
        if old_words and len(old_words & new_words) < max(3, len(old_words) // 2):
            raise ValueError(
                f"how_it_works is the account of the whole program, and this "
                f"text keeps almost none of its words ({cur_acc['text']!r}). A "
                f"behaviour the principal asked for is its own item: assert it "
                f"under its own name, kind in_scope. Amend the account only to "
                f"add the new behaviour to what it already says")

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
        # The account is never a behaviour, and a behaviour never folds into
        # it. On an existing repo the Vision Keeper rewrote the account to
        # describe the one new feature, then asserted the feature, and the
        # feature folded into the account: one item, nothing to slice, the
        # run went quiet (tipsL, 2026-09-09).
        account = "how_it_works"
        for t, i, vals, *_ in ctx.writes:
            if (t == "items" and i != id and vals.get("kind") == kind
                    and account not in (i, id)
                    and _near_duplicate(prose, _prose_words(vals.get("text") or ""))):
                return {"id": i, "note": f"close enough to {i!r} to be the same "
                        f"item ({vals.get('text')!r}) -- not written twice"}
        for r in ctx.conn.execute(
                "SELECT id, text FROM items WHERE id <> ? AND kind = ? "
                "AND id <> ? AND ? <> ?", (id, kind, account, id, account)):
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
    # A message wake carries its refs on the message, not on the wake:
    # clickI night 37 (2026-09-13) had one ratified statement, one item read
    # from it through the Liaison's deliver, and no statement ref on it,
    # so the Developer's wake said "the principal said: []".
    # `named_statements` reads both, for this op and the other owners.
    named = named_statements(ctx)
    staged = {"text": text, "kind": kind, "approval": "draft"}
    # An item read from the code, and the account, say what the software is.
    # They ask for nothing, so they are descriptions by construction (frame
    # 80). Any other wake stages no key, so an amendment keeps the flag.
    if getattr(ctx, "onboarding", False) or id == "how_it_works":
        staged["is_description"] = 1
    ctx.writes.append(("items", id, staged))
    # After the item row: the refs are receipted under it.
    for ref in named:
        stage_ref(ctx, "items", id, "statement", ref)
    # What the item rests on when an onboarding wake wrote it: the code it
    # read. A `source_refs` parameter for a reference waits for the
    # re-record: the advertised signature is in the prompt.
    stage_grain_refs(ctx, "items", id)
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


@op("problem", "describe")
def problem_describe(ctx: Ctx, id: str) -> dict:
    """
    Mark an item as a description: it says what the software is and asks for
    no piece of work. Call it instead of cutting tickets for such an item.

    A description is never cut and never owes criteria (ruled: Roman,
    2026-09-24, frame 80). The write moves no version, because a version move
    fires `cancel` and `reopen` and never reaches the owner. `draft` brings
    the item back to the owner's page, where the owner approves or contests
    the word. The door keeps the principal's own words and live work on the
    path: night 91's challenges named the one real request.
    """
    _must_exist(ctx, "items", id)
    prov = ctx.conn.execute(
        "SELECT provenance FROM item_provenance WHERE id = ?", (id,)).fetchone()
    if prov and prov["provenance"] == "decided":
        raise ValueError(
            f"{id} is the principal's own words, so it asks for something. "
            f"If its tickets are wrong, answer the challenge with "
            f"decisions.author and say which work the item asks for")
    live = ctx.conn.execute(
        "SELECT b.id FROM batches b WHERE b.status NOT IN ('merged', 'abandoned') "
        "AND (b.item_id = ? OR b.id IN (SELECT bt.batch_id FROM batch_tickets bt "
        "JOIN tickets t ON t.id = bt.ticket_id WHERE t.item_id = ?))",
        (id, id)).fetchone()
    if live:
        raise ValueError(
            f"{id} has work in batch {live['id']}, so it asks for something. "
            f"Answer the challenge with decisions.author and say which work "
            f"the item asks for")
    # A slice sent before the describe in the same reply lands nothing. The
    # recorded seat sliced and described one item in one reply (frame 80).
    dropped = [w[1] for w in ctx.writes
               if w[0] == "tickets" and w[2].get("item_id") == id]
    ctx.writes[:] = [w for w in ctx.writes
                     if not (w[0] == "tickets" and w[2].get("item_id") == id)]
    ctx.writes.append(("items", id, {"is_description": 1, "approval": "draft"},
                       False))
    note = "a description has no tickets; this item is finished"
    if dropped:
        note += (f". The tickets staged for it this session land nothing: "
                 f"{', '.join(dropped)}")
    return {"id": id, "described": True, "note": note}


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

    `from_statements` is part of this artefact -- the `statement` refs of an
    item, receipted under `problem` -- and was the half nothing returned. An
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
            "SELECT src_id AS item_id, target AS statement_id FROM refs "
            "WHERE src_table = 'items' AND kind = 'statement' "
            "ORDER BY src_id, rowid"):        # within an item, as written
        derives.setdefault(r["item_id"], []).append(r["statement_id"])
    # The flag rides only on a description. The select above stays as it is:
    # recordings hash the user text, and a new key on every row stales them.
    described = _described_ids(ctx.conn)
    for row in rows:
        row["from_statements"] = derives.get(row["id"], [])
        if row["id"] in described:
            row["is_description"] = 1
    return rows


def _described_ids(conn) -> set[str]:
    """The ids of the items that are descriptions. Empty on a run database
    that predates the column."""
    from ..core.db import _has_column
    if not _has_column(conn, "items", "is_description"):
        return set()
    return {r["id"] for r in conn.execute(
        "SELECT id FROM items WHERE is_description = 1")}


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
        "SELECT i.id, i.text FROM items i JOIN item_provenance p ON p.id = i.id "
        "WHERE p.provenance = 'observed' AND i.kind = 'in_scope' ORDER BY i.id"))


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

def _verdict_of(ctx: Ctx) -> tuple[str, dict[str, str]] | None:
    """The verdict on this wake's cause chain: (the message that carries the
    words, the per-row ruling). None when the wake carries no ruling at all.

    `principal.chain_verdict` does the walk. The runner builds the relay's
    `principal_verdict` from the same function, so what a session is shown and
    what it may adopt cannot part company.
    """
    from .principal import chain_verdict

    trigger = getattr(ctx, "trigger", None)
    if not trigger:
        return None
    found = chain_verdict(ctx.conn, trigger)
    return (found[0], found[1]) if found else None


def _ruled_ids(ctx: Ctx) -> set[str] | None:
    """The ids the principal's ruling approves, off this wake's cause chain.

    None when the wake carries no ruling at all -- distinct from a ruling that
    approves nothing, which is an empty set.
    """
    found = _verdict_of(ctx)
    if found is None:
        return None
    _, verdict = found
    approved = {i for i, ruling in verdict.items()
                if ruling in ("approve", "approved", "confirm", "confirmed")}
    # The rows this wake carries, and no others. The runner filters the
    # verdict to the relay's own refs before it shows it (`runner.py`, the
    # `principal_verdict` block), and this did not, so a chain walk that now
    # spans the whole chain let a session adopt an ancestor's ruling on a row
    # it was never woken about (the diff review of 6895000).
    mine = _wake_refs(ctx)
    return {i for i in approved if i in mine} if mine else approved


def _wake_refs(ctx: Ctx) -> set[str]:
    """The rows the wake named: the trigger message's refs, or the tick's."""
    trigger = getattr(ctx, "trigger", None)
    row = ctx.conn.execute(
        "SELECT body_refs FROM messages WHERE id = ?",
        (trigger,)).fetchone() if trigger else None
    try:
        given = json.loads(row["body_refs"] or "[]") if row else []
    except (TypeError, ValueError):
        given = []
    return {r for r in given if isinstance(r, str)} or set(ctx.wake_refs or ())


def _landed_ruling(ctx: Ctx) -> str | None:
    """The `rulings` row of the verdict on this wake's cause chain, landed.
    `principal.land` writes one for every verdict, so the ref has a target."""
    from .principal import chain_verdict

    trigger = getattr(ctx, "trigger", None)
    if not trigger:
        return None
    found = chain_verdict(ctx.conn, trigger)
    return found[2] if found else None


def _adopt_rows(ctx: Ctx, table: str, ids: list[str]) -> dict:
    if not ids:
        raise ValueError("adopt names the rows the principal approved, and "
                         "you named none")
    ruled = _ruled_ids(ctx)
    ruling_id = _landed_ruling(ctx)
    if ruling_id is None:
        # An adopted row rests on the ruling that approved it. With no
        # landed ruling on the cause chain the row has nothing to rest on.
        raise ValueError(
            "adopt needs a landed ruling on the chain of the message that "
            "woke you: the principal's verdict, relayed by the Liaison. None "
            "is on file, so there is no ruling for these rows to rest on.")
    from ..core.db import PROVENANCE_VIEW_OF_TABLE
    view = PROVENANCE_VIEW_OF_TABLE[table]
    out, skipped = [], []
    for rid in ids:
        # The view, not the column: a row's provenance is what it rests on.
        row = ctx.conn.execute(
            f"SELECT provenance FROM {view} WHERE id = ?", (rid,)).fetchone()
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
        # The row now rests on the ruling that approved it.
        stage_ref(ctx, table, rid, "ruling", ruling_id)
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
        # An area for a survey; nothing for a word defined over the whole
        # program. `@term:x` is a subject, not a place the word was seen.
        "area": ctx.area if is_area(ctx.area) else ""}))
    # What the sense rests on when an onboarding wake wrote it: the code it
    # read. A `source_refs` parameter for a reference waits for the
    # re-record: the advertised signature is in the prompt.
    stage_grain_refs(ctx, "glossary_terms", id)
    # What the sense rests on when a delivery wake wrote it: the statements
    # the wake names. Decided cascades from a ratified statement along the
    # refs. A wake that names no statement gives a reasoned row.
    for ref in named_statements(ctx):
        stage_ref(ctx, "glossary_terms", id, "statement", ref)
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
        "SELECT id, term, sense_short, sense_body, "
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
    # A synthesis is not a choice with the reason on file. Nobody chose it:
    # it was assembled from rows that were themselves found in the code, plus
    # the concordance. Law 11 splits these on *found not chosen*, and this is
    # found. So the kept row asserts nothing of its own: it inherits the
    # readings' refs below, and the view says of it what it says of them. A
    # synthesis over anything decided stays decided.
    ctx.writes.append(("glossary_terms", keep, {
        "term": term, "sense_short": sense_short, "sense_body": sense_body,
        "area": rows[keep]["area"] if keep in rows else "",
        "superseded_by": None}))
    for i, r in rows.items():
        if i == keep or r["superseded_by"]:
            continue
        ctx.writes.append(("glossary_terms", i, {
            "term": r["term"], "sense_short": r["sense_short"],
            "sense_body": r["sense_body"], "area": r["area"],
            "superseded_by": keep}))
    # The kept row inherits the readings' refs: composed from what they
    # rest on, it rests on the same.
    for i in rows:
        if i != keep:
            stage_copied_refs(ctx, "glossary_terms", i, keep)
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
        "SELECT id, term, sense_short, sense_body, "
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
    # A word of difference inside a negation says the opposite. clickI
    # (2026-09-16): "... the same parameter type, not a distinct meaning"
    # was read as "distinct" and refused seventeen sessions running, and
    # the walk cycled on the collision. The negated span leaves the text
    # before the check; a plain "distinct" is still refused.
    low = re.sub(r"\b(?:not|no|nor|never|neither)\s+(?:\w+\s+){0,2}?"
                 r"(?:different|differ\w*|distinct\w*|separate\w*|unlike|"
                 r"another sense)\b", " ", reason.lower())
    against = [w for w in ("different", "differ", "distinct", "separate",
                           "unlike", "not the same", "another sense")
               if w in low]
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
        "sense_body": b["sense_body"], "area": b["area"],
        "superseded_by": keep}))
    # The survivor inherits what the losing row rests on.
    stage_copied_refs(ctx, "glossary_terms", drop, keep)

    # Anything pointing at the losing row is repointed at the survivor. The
    # claim being made is that the two say the same thing, so a reference to one
    # is a reference to the other -- and leaving them is the quiet kind of wrong
    # this whole change is against: `check_criteria_terms` validates against
    # every row including superseded ones, so a stale ref stays green while
    # naming the sense that was just declared redundant.
    #
    # Empty during onboarding, because criteria do not exist yet. It is the
    # delivery loop that would have paid for it.
    #
    # The repoint is on the relation. The ref to the losing row is retired,
    # so the relation lists the kept term only. The kept row carries the
    # losing row's own refs (`stage_copied_refs` above).
    #
    # The walk is the one the columns had: the criteria first, then the
    # business rules, each in the order the refs were written. A table that
    # carries term refs only since the relation comes after them.
    repointed = []
    for r in ctx.conn.execute(
            "SELECT src_table, src_id FROM refs WHERE kind = 'term' "
            "AND target = ? ORDER BY CASE src_table WHEN 'criteria' THEN 0 "
            "WHEN 'business_rules' THEN 1 ELSE 2 END, src_table, rowid",
            (drop,)):
        stage_ref(ctx, r["src_table"], r["src_id"], "term", keep)
        retire_ref(ctx, r["src_table"], r["src_id"], "term", drop)
        if r["src_id"] not in repointed:
            repointed.append(r["src_id"])

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
        rows = _shown_rows(ctx.conn.execute(
            "SELECT g.id, g.term, g.sense_short, g.sense_body, g.area, "
            "p.provenance, p.basis "
            "FROM glossary_terms g JOIN term_provenance p ON p.id = g.id "
            f"WHERE g.id IN ({','.join('?' * len(ctx.wake_refs))})",
            tuple(ctx.wake_refs)))
        return rows or {"note": "the rows this wake named are gone."}

    rows = _shown_rows(ctx.conn.execute(
        "SELECT g.id, g.term, g.sense_short, g.sense_body, p.provenance, p.basis "
        "FROM glossary_terms g JOIN term_provenance p ON p.id = g.id "
        "WHERE g.term = ? ORDER BY g.id", (term,)))
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
        return _shown_rows(ctx.conn.execute(
            "SELECT g.id, g.term, g.sense_short, p.provenance, p.basis "
            "FROM glossary_terms g JOIN term_provenance p ON p.id = g.id "
            f"WHERE g.term IN ({marks}) ORDER BY g.term", terms))
    return _shown_rows(ctx.conn.execute(
        "SELECT g.id, g.term, g.sense_short, p.provenance, p.basis "
        "FROM glossary_terms g JOIN term_provenance p ON p.id = g.id "
        "ORDER BY g.term"))


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
    # A name with its kind is an inventory row, not a promise. A survey wrote
    # eleven of them, one per public name, "total_of function" among them
    # (ruled: Roman, 2026-09-24 21:20, the survey desk gets this guard).
    kind = re.fullmatch(
        r"(?:the\s+)?(?:`?(?P<n1>[\w./:()]+)`?\s+(?P<k1>class|function|method|"
        r"module|variable)|(?P<k2>class|function|method|module|variable)\s+"
        r"`?(?P<n2>[\w./:()]+)`?)",
        headline.strip(), re.IGNORECASE)
    if kind:
        # The abstract hint made a seat repeat eleven refused calls three
        # times. The refusal now names the headline that passes.
        name = (kind.group("n1") or kind.group("n2")).rstrip("()")
        name = name.rsplit("::", 1)[-1]
        what = (kind.group("k1") or kind.group("k2")).lower()
        # A module is a file, and a file has no `::name` part. Frame 82's
        # diff review: the hint built `charges.py::src/billing/charges.py`.
        if what == "module" or "/" in name or ".py" in name:
            where = _grain_path(bindings[0]) if bindings else "<path>"
            first = ("" if bindings else
                     "First `code.source` the file, and put its path in "
                     "bindings=. Then write ")
            raise ValueError(
                f"{headline!r} names a {what}, and a constraint is what a "
                f"caller outside relies on. {first or 'Write '}"
                f"headline=\"{where}\" with no ::name part, and in text say "
                f"who outside this area breaks and what they see.")
        if bindings:
            raise ValueError(
                f"{headline!r} names a {what}, and a constraint is what a "
                f"caller outside relies on. Write "
                f"headline=\"{_grain_path(bindings[0])}::{name}\" and in text "
                f"say who outside this repository breaks and what they see.")
        raise ValueError(
            f"{headline!r} names a {what}, and a constraint is what a caller "
            f"outside relies on. First `code.source` the file that defines "
            f"{name}, and put its path in bindings=. Then write "
            f"headline=\"<path>::{name}\" and in text say who outside this "
            f"repository breaks and what they see.")
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
        # The last green survey wrote "Code that calls ..." in text. The
        # refusal names that form, so the seat does not guess a second time.
        subject = headline.strip().rsplit("::", 1)[-1]
        raise ValueError(
            f"{headline!r} names nobody outside this area -- a maintainer, "
            f"the codebase, the build are inside. A constraint is kept to "
            f"someone who does not read this code: say who, or this is not one. "
            f"Name the caller: another area of this repository that imports "
            f"it, a test that patches it, a program that imports this package. "
            f"Write text=\"<caller> calls {subject} and breaks when ...\".")
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

    # A survey's constraint binds a grain of the area it surveyed. The brief
    # says so; the tool says it too, with the area's path shape in hand, so
    # an amend that forgets its bindings is a tool error and not a global
    # constraint by accident (the survey spike, 2026-09-15: qwen3:8b bound
    # every constraint it wrote, at file grain, under both wordings).
    surveyed = ctx.area or next((r for r in (ctx.wake_refs or ()) if "/" in str(r) and not str(r).startswith("@")), None)
    if surveyed and not bindings:
        raise ValueError(
            f"a constraint from the survey of {surveyed} binds the grain that "
            f"keeps it: bindings=['{surveyed}/<file>.py::<name>'], a path "
            f"[code.area] printed and you opened. A commitment nobody can "
            f"point at is not one; send the amend again with its bindings")

    # `source_refs` is the clause this constraint encodes, recorded as a
    # `reference` ref: "constraints are where external obligations actually
    # land, so a constraint that cannot point at the clause it encodes is the
    # one that most needed to." The brief says to cite the reference here and
    # the parameter was never on the function, so the Architect put reference
    # ids in `bindings` -- the only list it had -- and the read-check refused
    # them, correctly and forever: a reference is not a grain and no amount of
    # `code.source` would make it one. Six identical refused amends in one
    # session.
    #
    # A row that rests on the world is `cited`, the one provenance that can go
    # stale on its own, so the ref is written from the presence of a source
    # rather than supplied: a session that names the clause has cited it,
    # whatever it would have claimed.
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
        "is_global": 0 if bindings else 1}))
    # The kind comes from the index row, so a future `table` row there is
    # stamped `table` with no change here. Every binding stamped `path` made
    # a table bind nothing (observed: frame 90's third diff review,
    # 2026-09-28). The grain is folded as the read check folds it, so
    # `./x.py` and `x.py` are one binding. The row stores the index's own
    # spelling, because every reader compares grains with the index.
    def _fold(g: str) -> str:
        head, _, sym = str(g).partition("::")
        return _grain_path(head) + (f"::{sym.strip()}" if sym else "")
    kinds: dict[str, str] = {}
    raw: dict[str, str] = {}
    for r in ctx.conn.execute("SELECT grain, grain_kind FROM code_index"):
        # Both from the same row, so a fold collision of two seeded rows
        # pairs one row's grain with that row's kind (the review of pass 3).
        kinds.setdefault(_fold(r["grain"]), r["grain_kind"])
        raw.setdefault(_fold(r["grain"]), r["grain"])
    for grain in map(_fold, bindings or []):
        # A symbol the indexer never emitted still passed the read check on
        # its file. With no index, a binding is a file the session read.
        kind = kinds.get(grain, "symbol" if "::" in grain else "path")
        grain = raw.get(grain, grain)
        ctx.writes.append(("constraint_bindings", f"{id}:{grain}", {
            "constraint_id": id, "grain": grain, "grain_kind": kind}))
    # What the constraint rests on: the clause it cites, and the code an
    # onboarding wake read.
    for ref in cited:
        stage_ref(ctx, "constraints", id, "reference", ref)
    stage_grain_refs(ctx, "constraints", id)
    # And the statements a delivery wake names, as `glossary.amend` does.
    for ref in named_statements(ctx):
        stage_ref(ctx, "constraints", id, "statement", ref)
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
    rows = _rows(ctx.conn.execute(
        "SELECT f.id, f.constraint_id, f.commit_sha, f.status, f.grain, "
        "  (SELECT fr.ruling FROM finding_rulings fr WHERE fr.finding_id = f.id "
        "   AND fr.commit_sha = f.commit_sha) AS ruling "
        "FROM findings f WHERE f.batch_id = ? ORDER BY f.id", (bid,)))
    # The Critic dismissed it, so it holds nothing (ruled: Roman, 2026-09-27).
    # The Developer's brief says fix every violated finding, so a dismissed
    # one stays out of its sight. Any other reader sees the label. The key
    # appears on a dismissed row only, so every other result keeps its shape.
    out = []
    for r in rows:
        ruling = r.pop("ruling", None)
        if ruling == "dismissed":
            if ctx.role == "developer":
                continue
            r["ruling"] = ruling
        out.append(r)
    return out


def _capped_ids(ids: list[str], cap: int = 20) -> str:
    """A list of ids a refusal can hold. The six-row cap of `_must_exist`
    hid half the constraints on night 95 (2026-09-28)."""
    more = f", and {len(ids) - cap} more" if len(ids) > cap else ""
    return f"{ids[:cap]}{more}"


def _binding_grains(files: list[str]) -> set[str]:
    """The grains a binding can name for `files`. A binding can name a
    directory, as `src/billing` does in L1-AR-find-against-a-constraint, so
    each file's parent directories count too."""
    grains: set[str] = set()
    for f in files:
        parts = f.replace(chr(92), "/").split("/")
        grains.update("/".join(parts[:n]) for n in range(1, len(parts) + 1))
    return grains


def _reaching_constraints(conn: sqlite3.Connection, files: list[str]) -> set[str]:
    """
    The constraints whose bindings reach `files`. This is the one place that
    decides it, so the push, the door and the refusal show one list. Frame
    90's second diff review, findings 6a and 6b: equality on the grain hid
    `src/click/utils.py::echo` from a diff on `src/click/utils.py`.

    A binding reaches the files when its grain, or the part before "::",
    is a file or a parent directory of one. A symbol is judged by its file.
    A binding that is not a path or a symbol, such as a table, cannot be
    judged against a diff. That binding reaches every diff. So does a
    binding that no longer resolves, as in `constraints_for_grains`. A
    constraint with no binding, or marked global, reaches every diff.
    """
    grains = _binding_grains(files)
    hits = {r["id"] for r in conn.execute(
        "SELECT c.id AS id FROM constraints c "
        "LEFT JOIN constraint_bindings b ON b.constraint_id = c.id "
        "GROUP BY c.id HAVING COUNT(b.grain) = 0 OR MAX(c.is_global) = 1")}
    for r in conn.execute(
            "SELECT constraint_id, grain, grain_kind, resolves FROM constraint_bindings"):
        grain = (r["grain"] or "").replace(chr(92), "/")
        if (r["grain_kind"] not in ("path", "symbol") or not r["resolves"]
                or grain.split("::", 1)[0] in grains):
            hits.add(r["constraint_id"])
    return hits


def _diff_files(ctx: "Ctx", batch_id: str) -> list[str] | None:
    """The batch's changed files, read once per session and batch."""
    if batch_id not in ctx.diff_files:
        from ..core import worktrees as _wt
        ctx.diff_files[batch_id] = _wt.batch_files(ctx.conn, batch_id)
    return ctx.diff_files[batch_id]


def _bound_exit(ctx: "Ctx", files: list[str] | None, grain: str | None) -> str:
    """The sentence that tells the Architect which constraint ids to send.
    Night 95 (2026-09-28): no constraint bound the diff, no text said so,
    and the Architect filled the gap with a criterion id."""
    from ..onboarding.boot import ZERO
    if files is None:
        have = [r["id"] for r in ctx.conn.execute(
            "SELECT id FROM constraints ORDER BY id")]
        return f"The constraints rows are {_capped_ids(have)}."
    bound = sorted(k for k in _reaching_constraints(ctx.conn, files) if k != ZERO)
    if not bound:
        example = grain if grain in files else (files[0] if files else None)
        like = f", for example {example!r}" if example else ""
        return (f"No constraint binds this diff. File {ZERO!r} satisfied, "
                f"with a changed file as the grain{like}.")
    return (f"The constraints that bind this diff are {_capped_ids(bound)}. "
            f"File one finding for each one you checked.")


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
    # Constraint zero is the register's account of what no survey has
    # read. A diff cannot violate it: a file the batch wrote is read by
    # this very review. tipsAN (2026-09-11): four k0 findings on the
    # batch's own new files stood between green tests and the merge, and
    # the Developer had nothing to restore.
    from ..onboarding.boot import ZERO
    # Law 14 at the door, not at the commit. Night 64 (2026-09-14): the
    # Architect filed findings against inherited test ids as constraints;
    # the tool said OK, the foreign key refused the session at commit,
    # three sessions, the night stuck.
    _must_exist(ctx, "batches", batch_id)
    # A grain is a path, a path::symbol, or a bare symbol; only a path
    # can be checked against the diff (L1-AR-find-against-a-constraint
    # names bare symbols and passed before this door).
    grain_file = grain.split("::", 1)[0]
    path_shaped = "/" in grain_file or grain_file.endswith(".py")
    # The check sits here and not in `_must_exist`, because only this door
    # knows the batch. Night 95 (2026-09-28): the Architect sent a criterion
    # id as the constraint, and the refusal named 6 of 12 rows and no exit.
    if constraint_id != ZERO and ctx.conn.execute(
            "SELECT 1 FROM constraints WHERE id = ?", (constraint_id,)).fetchone() is None:
        held = [t for t in ("criteria", "tests") if ctx.conn.execute(
            f"SELECT 1 FROM {t} WHERE id = ?", (constraint_id,)).fetchone()]
        what = (f"{constraint_id!r} is a row of {held[0]}, not a constraint"
                if held else f"no constraints row has id={constraint_id!r}")
        raise ValueError(
            f"{what}. A finding names a constraint from model.consult. "
            f"{_bound_exit(ctx, _diff_files(ctx, batch_id), grain_file if path_shaped else None)}")
    # A finding says what the batch's diff broke, so its grain is a file
    # the diff changed. Night 65 (2026-09-14): three findings against one
    # constraint, two on test files the diff never touched; the Developer
    # read them, found nothing to fix, and looped. The list of changed
    # files is a fact of the worktree.
    if status == "violated":
        files = _diff_files(ctx, batch_id)
        if files is not None and path_shaped and grain_file not in files:
            raise ValueError(
                f"the batch's diff does not touch {grain_file!r}; it changed "
                f"{files}. A finding names what the diff broke, on a file the "
                f"diff changed. A constraint the diff did not reach is not "
                f"violated by this batch")
        # A diff breaks only a constraint that binds what it changed. The
        # design review of frame 90 (2026-09-28): a violated finding on an
        # unbound constraint was accepted and woke the Critic for nothing.
        reach = ([grain_file] if path_shaped
                 else files if files is not None else None)
        if constraint_id != ZERO and reach is not None \
                and constraint_id not in _reaching_constraints(ctx.conn, reach):
            where = repr(grain_file) if path_shaped else "this diff's files"
            raise ValueError(
                f"{constraint_id!r} does not bind {where}, so this diff cannot "
                f"violate it. {_bound_exit(ctx, files, grain_file if path_shaped else None)}")
    if constraint_id == ZERO and status == "violated":
        raise ValueError(
            f"{ZERO} is constraint zero, the area no survey has read. It is "
            f"a fact about the register, not a rule the code can break, and "
            f"a file this batch wrote is read by this review. Record it "
            f"satisfied, or check the constraints that bind {grain!r}")
    # One finding per constraint and grain in a session. `findings.load`
    # does not show staged writes, so the seat cannot see its own row.
    # Frame 90's diff review, finding 5: one recorded run filed the k0 row
    # three times. The same pattern as `statements.segment`.
    same = [w for w in ctx.writes
            if w[0] == "findings"
            and w[2].get("batch_id") == batch_id
            and w[2].get("constraint_id") == constraint_id
            and w[2].get("grain") == grain]
    if same and same[0][2].get("status") == status:
        return {"id": same[0][1], "unchanged": True,
                "note": f"this finding is already filed, as {same[0][1]}; "
                        f"nothing was written. Your review is done."}
    if same:
        raise ValueError(
            f"you have already filed {constraint_id} "
            f"{same[0][2].get('status')} on {grain} in this session; decide, "
            f"and send the one")
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
    ctx.writes.append(("model_areas", area, {"account": account}))
    # What the account rests on: the paths this session opened, as grain
    # refs, on every kind of wake.
    stage_grain_refs(ctx, "model_areas", area, always=True)
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
        return _shown_rows(ctx.conn.execute(
            "SELECT c.id, c.headline, p.provenance, c.is_global, p.basis "
            "FROM constraints c JOIN constraint_provenance p ON p.id = c.id "
            "ORDER BY c.id"))
    if not ids:
        return []
    marks = ", ".join("?" for _ in ids)
    return _shown_rows(ctx.conn.execute(
        "SELECT c.id, c.headline, p.provenance, c.is_global, p.basis "
        "FROM constraints c JOIN constraint_provenance p ON p.id = c.id "
        f"WHERE c.id IN ({marks}) ORDER BY c.id", ids))


@op("model", "load")
def model_load(ctx: Ctx, ids: list[str]) -> list[dict]:
    """Bodies, fetched singly by id. The other half of the index/body split."""
    if not ids:
        return []
    marks = ", ".join("?" for _ in ids)
    return _shown_rows(ctx.conn.execute(
        "SELECT c.id, c.headline, c.text, p.provenance, p.basis "
        "FROM constraints c JOIN constraint_provenance p ON p.id = c.id "
        f"WHERE c.id IN ({marks})", ids))


def _re_split_paths(val: str) -> list[str]:
    import re as _re

    return [t.strip("'\"[]") for t in _re.split(r"[\s,]+", val.strip()) if t.strip("'\"[]")]


def area_content_hash(conn, area: str) -> str:
    """
    The area's aggregate content, as main last stood.

    The value is the same aggregate this function used to compute live from the
    path grains: sorted, a function of (files, contents) and nothing else. It is
    read from `area_hashes` because the index no longer describes one tree for
    the whole run. Between a Developer's commit and the merge it describes the
    batch's worktree, and a live aggregate would then reopen every touched area
    on every commit the batch makes. `indexer.stamp_area_hashes` writes the
    table at onboarding and at every refresh of the main checkout.

    Empty when the area has no stamp -- a new area, an area with no path grains,
    or a database from before the table. **Empty matches everything**:
    `scheduler._survey_wakes` reads an empty aggregate as "the view is unknown,
    so leave the record alone", and every survey of the area then counts as
    current. That is why `core.boot` stamps the table when it opens a database
    that has areas and no stamps: unstamped is quiet, not loud.
    """
    row = conn.execute("SELECT hash FROM area_hashes WHERE area = ?",
                       (area,)).fetchone()
    return (row["hash"] if row else "") or ""


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

    if area == _PROSE or area.startswith(_PROSE + ":"):
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
        # A frame ruling's body is its `reason`. Without it here, every
        # frame attestation on an existing repo was refused as a title with
        # nothing under it, three times, and the run was quarantined at the
        # frame with nothing built (tipsJ, 2026-09-09).
        bodied = [v for v in mine
                  if (v.get("text") or v.get("sense_short") or
                      v.get("sense_body") or v.get("statement") or
                      v.get("default_taken") or v.get("reason") or "").strip()]
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
    # The frame is the exception: its ruling is a reading of the tree, and
    # `code.tree` carries the priors and the entry imports so the judge
    # need not open files. Held to this guard, the Architect's attestation
    # was refused three times on an existing repo and the run was
    # quarantined at the frame (tipsK, 2026-09-09).
    from ..core.scheduler import FRAME as _FRAME_AREA
    if inside and not read and getattr(ctx, "area", None) != _FRAME_AREA:
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
    # Observed items are what the repository already does, and the account
    # is the whole program: neither is work. clickI night 9 (2026-09-11):
    # the Vision Keeper sliced tickets for three observed items and for
    # how_it_works, the Terminologist wrote sixteen criteria for the
    # account against examples/, and the first batch carried five tickets
    # of which one was asked for. The slicing predicate has never fired for
    # these rows; the call was reachable from another mode.
    kind = ctx.conn.execute(
        "SELECT provenance FROM item_provenance WHERE id = ?", (item_id,)).fetchone()
    if item_id == "how_it_works":
        raise ValueError(
            "how_it_works is the account of the whole program, not a "
            "behaviour to build. Tickets come from the items the principal "
            "asked for; the account is never sliced")
    if kind and kind["provenance"] == "observed":
        raise ValueError(
            f"{item_id} is observed: it is what the repository already does, "
            f"and a ticket for it would build what exists. Slice the items "
            f"the principal asked for, the decided ones")
    # A description has no tickets (frame 80). An answer, not a refusal: a
    # refused argument loops a 9B seat (frame 81). The recorded seat sent
    # the describe and then a slice for the same item.
    described = any(w[0] == "items" and w[1] == item_id
                    and w[2].get("is_description") == 1 for w in ctx.writes)
    if described or item_id in _described_ids(ctx.conn):
        return {"id": id, "unchanged": True,
                "note": f"{item_id} is a description, and a description has "
                        f"no tickets. Nothing was written. This session is "
                        f"finished"}
    # An id you invent is yours once. tipsT (2026-09-09): every slicing
    # session wrote tk_1 and tk_2, the ids re-parented to whichever items
    # the wake named, the other items lost their tickets, and the two sets
    # ping-ponged for 130 sessions. Same rule as `criteria.specify`.
    owner = next((w[2].get("item_id") for w in ctx.writes
                  if w[0] == "tickets" and w[1] == id), None)
    if owner is None:
        row = ctx.conn.execute(
            "SELECT item_id FROM tickets WHERE id = ?", (id,)).fetchone()
        owner = row["item_id"] if row else None
    derived_note = None
    if owner is not None and owner != item_id:
        # Derived, not refused. tipsAW (2026-09-12): the Vision Keeper,
        # slicing three new items after an amendment, wrote tk_1, tk_2 and
        # tk_3 again, was refused three times a session, and the tick was
        # quarantined. The words are the identity (law 14); the id is a
        # handle, and a handle that collides gets the item's name on it.
        derived = f"{id}_{item_id}"[:64]
        derived_note = (f"{id!r} was already {owner}'s ticket, so this one "
                        f"is {derived!r}: two items never share a ticket id")
        id = derived
    # A delivered ticket is not a ticket to reuse. An item amended after its
    # delivery is sliced again, and the Vision Keeper wrote the old id back:
    # the upsert changed nothing, three sessions did the same, and the tick
    # was quarantined (tipsAH, 2026-09-09, from the seat).
    spent = ctx.conn.execute(
        "SELECT b.id FROM batch_tickets bt JOIN batches b ON b.id = bt.batch_id "
        "WHERE bt.ticket_id = ? AND b.status IN ('merged', 'abandoned') LIMIT 1",
        (id,)).fetchone()
    if spent:
        raise ValueError(
            f"{id!r} went out in batch {spent['id']}, which is {ctx.conn.execute('SELECT status FROM batches WHERE id = ?', (spent['id'],)).fetchone()['status']}. "
            f"New work is a new ticket: give it a new id of your own")
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
    return {"id": id, **({"note": derived_note} if derived_note else {})}


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


def _woken_tickets(ctx: Ctx) -> list[str]:
    """The wake's refs, kept only where they name a ticket row."""
    refs = [r for r in ctx.wake_refs if isinstance(r, str)]
    if not refs:
        return []
    marks = ",".join("?" * len(refs))
    return [r["id"] for r in ctx.conn.execute(
        f"SELECT id FROM tickets WHERE id IN ({marks}) ORDER BY id", refs)]


def _batch_is_subject(ctx: Ctx, tickets: list[str]) -> bool:
    """True when the session's batch, not the woken tickets, is the subject."""
    # A grouping wake names the tickets with no live batch. The scheduler
    # still gives the session the running batch as a fallback. Night 98's
    # push then showed only that batch's ticket, and three Architect
    # sessions grouped it again (observed: night98 walk, section 5,
    # 2026-09-29). A wake that names its batch keeps the batch.
    return bool(ctx.batch_id) and (ctx.batch_id in ctx.wake_refs or not tickets)


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
    tickets = _woken_tickets(ctx)
    if _batch_is_subject(ctx, tickets):
        return _rows(ctx.conn.execute(
            "SELECT t.id, t.item_id, substr(t.text,1,120) AS headline "
            "FROM tickets t JOIN batch_tickets bt ON bt.ticket_id = t.id "
            "WHERE bt.batch_id = ? ORDER BY t.id", (ctx.batch_id,)))
    if tickets:
        marks = ",".join("?" * len(tickets))
        return _rows(ctx.conn.execute(
            f"SELECT id, item_id, substr(text,1,120) AS headline FROM tickets "
            f"WHERE id IN ({marks}) ORDER BY id", tickets))
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


def _area_resolves(ctx: Ctx, ref: str) -> bool:
    """Whether `@name` names an area this run declared.

    Any `@` string passed before. Night 85 (2026-09-18): a blindspot session
    copied a `code.gaps` fact line whole and logged a ledger row about
    `@constraint_zero` in `model_areas`, which held only `.` and `src/click`.
    The gap reached the page as an assumption and the signoff wrote a decision
    with a dangling ref. The blindspot brief already forbids a row about a
    tick, a message or a counter, and this is the door behind the brief.
    """
    from ..core.scheduler import PSEUDO_AREAS, PSEUDO_AREA_PREFIXES

    if ref in PSEUDO_AREAS or any(ref.startswith(p) for p in PSEUDO_AREA_PREFIXES):
        return True
    name = ref[1:]
    if not name:
        return False
    if name == getattr(ctx, "area", None) or ref == getattr(ctx, "area", None):
        return True
    if any(w[0] == "model_areas" and w[1] == name for w in ctx.writes):
        return True
    if ctx.conn.execute("SELECT 1 FROM model_areas WHERE id = ?",
                        (name,)).fetchone():
        return True
    # The partition onboarding stamped, which exists before the Architect has
    # written an account of any area.
    try:
        return ctx.conn.execute("SELECT 1 FROM area_hashes WHERE area = ?",
                                (name,)).fetchone() is not None
    except sqlite3.Error:             # a database older than the table
        return False


def ref_resolves(ctx: Ctx, ref: str) -> bool:
    """A ref is a promise that a row exists somewhere -- kept, staged, or a
    declared prefix. The world-audit found 258 broken promises in the
    historical runs; this is the door that stops new ones."""
    if ref.startswith("@"):
        return _area_resolves(ctx, ref)
    if ref.startswith("e_"):
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


def _vet_surface(ctx: Ctx, surface_refs, *, required: bool,
                 ticket_id: str | None = None) -> list[str]:
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
            # A test is not a surface. tipsS (2026-09-09): the split's first
            # criterion named `tests/test_calculate_tip.py::test_calculate_tip`
            # as its surface, the second named the existing tip function,
            # and the Tester tested the split through the tip.
            g = hit["grain"]
            gpath, _, gname = g.partition("::")
            if ("tests" in gpath.replace("\\", "/").split("/")[:-1]
                    or gpath.rsplit("/", 1)[-1].startswith("test_")
                    or gname.startswith("test_")):
                raise ValueError(
                    f"{ref!r} is a test ({g}), and a test is not a surface. "
                    f"The surface is the program callable a test would "
                    f"exercise. Name that callable; if the behaviour is new, "
                    f"name the callable that will implement it")
            vetted.append(g)
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
        # the design decision a criterion is for. Kept as written -- when the
        # item or the ticket gives the name, or the worktree defines it.
        # Click night 56 (2026-09-14): a repair named `inspect_signature`,
        # a library function the program does not have, and every test of
        # the criterion was refused for never calling it.
        bare = ref.split("::")[-1].rsplit(".", 1)[-1]
        given = set(_named_new_callables(ctx, ticket_id)) if ticket_id else set()
        in_tree = False
        try:
            in_tree = bool(_defined_in_tree(ctx, bare, ""))
        except Exception:                                  # noqa: BLE001
            in_tree = False
        # At the repair only: a first criterion may name the entry point a
        # new feature will have (test_a_name_with_no_neighbour_is_a_design
        # _not_a_typo); a repair exists because a test could not be written,
        # and a surface the program lacks cannot be the fix.
        if required and ticket_id and bare not in given and not in_tree:
            raise ValueError(
                f"{ref!r} is not a symbol the index knows, not a name the item "
                f"or the ticket gives, and nothing in the worktree defines it. "
                f"A surface is a callable of this program that a test would "
                f"exercise: name the one that exists, or the new name the "
                f"ticket asks for")
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


def _named_new_callables(ctx: Ctx, ticket_id: str) -> list[str]:
    """
    Callable names the item or its ticket give in words that the index does
    not hold: snake_case identifiers, and a name after "function named" or
    "function called". A4 (2026-09-10): "the share lives in a new function
    named split_bill" beside an index holding calculate_tip, and llama3.1:8b
    and qwen3.5:9b both named calculate_tip as the surface, 0/5 each.
    """
    import re as _re

    row = ctx.conn.execute(
        "SELECT t.text AS ticket, i.text AS item FROM tickets t "
        "JOIN items i ON i.id = t.item_id WHERE t.id = ?", (ticket_id,)).fetchone()
    if not row:
        return []
    text = f"{row['item'] or ''} {row['ticket'] or ''}"
    # Only names the words call a callable: "a function named X", "X()".
    # A bare snake_case word is not enough. clickI night 8 (2026-09-11):
    # "give version_option a show_python flag" made `show_python`, a flag,
    # a callable the criteria had to name, and the Terminologist named
    # the item's own id instead.
    # The word after "function" is a name only in a callable's form. Night
    # 116 (2026-10-04): "The confirm() function already takes" made
    # `already` a callable, and the criteria door refused three
    # Terminologists. "helper next to echo" made `next` on nights 113-117.
    # A form rule, not a stop list: a stop list misses the next word.
    # So "a helper slugify" gives no name, on purpose: no night text has
    # the form. `_vet_surface` reads this result too and refuses that repair.
    kind = r"(?:function|callable|method|helper|decorator)\s+"
    ident = r"[A-Za-z_][A-Za-z0-9_]*"
    # "named" or "called" says the next word is a name, whatever its form.
    names = set(_re.findall(kind + r"(?:named|called)\s+`?(" + ident + r")`?", text))
    names |= set(_re.findall(kind + r"`(" + ident + r")`", text))
    # A snake_case or camelCase word is an identifier, and English has none.
    # A leading underscore counts, so `_private` and `__init__` stay names.
    names |= set(_re.findall(
        kind + r"(_+[A-Za-z][A-Za-z0-9_]*|[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]*"
        r"|[a-z][a-z0-9]*[A-Z][A-Za-z0-9]*)\b",
        text))
    # A dotted path names its last part, the callable a surface ends in.
    names |= set(_re.findall(kind + r"`?(?:" + ident + r"\.)+(" + ident + r")\b", text))
    names |= set(_re.findall(r"`?([A-Za-z_][A-Za-z0-9_]*)\(", text))
    # "function(s)" matches the call form, and a kind word is never a name.
    names -= {"a", "the", "named", "called", "new", "that", "which", "in", "to",
              "function", "callable", "method", "helper", "decorator"}
    out = []
    for name in sorted(names):
        known = ctx.conn.execute(
            "SELECT 1 FROM code_index WHERE grain = ? OR grain LIKE ?",
            (name, f"%::{name}")).fetchone()
        if not known:
            out.append(name)
    return out


def _named_existing_callables(ctx: Ctx, ticket_id: str) -> list[str]:
    """Callable names the item or its ticket give in words that the index
    holds: a snake_case word that is a definition. Night 70 (2026-09-15),
    click sentence three: "give version_option a show_python flag" names
    version_option, a definition; show_python is not one and drops out."""
    import re as _re

    row = ctx.conn.execute(
        "SELECT t.text AS ticket, i.text AS item FROM tickets t "
        "JOIN items i ON i.id = t.item_id WHERE t.id = ?", (ticket_id,)).fetchone()
    if not row:
        return []
    text = f"{row['item'] or ''} {row['ticket'] or ''}"
    words = set(_re.findall(r"[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]+", text))
    return sorted(w for w in words if ctx.conn.execute(
        "SELECT 1 FROM code_index WHERE grain = ? OR grain LIKE ?",
        (w, f"%::{w}")).fetchone())


def _surface_names_what_the_item_names(ctx: Ctx, ticket_id: str, surface_refs) -> None:
    """A fact about three texts: the item names a callable the index does not
    hold, and the surface names only callables it does. Or the item names a
    callable the index holds, and the surface names another one."""
    new = _named_new_callables(ctx, ticket_id)
    if not new:
        # Night 70 (2026-09-15), click sentence three: the item said "give
        # version_option a show_python flag", the criteria carried
        # custom_version_option as their surface, a real companion whose
        # docstring offers itself for the Python version. The Developer
        # changed version_option and the duplicate-name door refused it:
        # no criterion named it. Three sessions, stuck.
        named = _named_existing_callables(ctx, ticket_id)
        refs = [str(r) for r in (surface_refs or [])]
        tails = {r.split("::")[-1] for r in refs}
        if named and refs and not (tails & set(named)):
            raise ValueError(
                f"the item names {', '.join(named)}, a callable the index holds, "
                f"and this surface names {', '.join(sorted(tails))}. A criterion "
                f"on another callable tests another behaviour, and the Developer's "
                f"change to {named[0]} is refused as a change no criterion names. "
                f"Name {named[0]} as the surface, in its own file")
        return
    refs = [str(r) for r in (surface_refs or [])]
    tails = {r.split("::")[-1] for r in refs}
    if tails & set(new):
        return
    # The mirror: a bare name the index does not hold and no item names is
    # invented. clickI night 9: `range_argument` and `get_usage` as
    # surfaces, and the Developer could define nothing the item asked for.
    invented = [r for r in refs if "::" not in r and r not in new
                and not ctx.conn.execute(
                    "SELECT 1 FROM code_index WHERE grain = ? OR grain LIKE ?",
                    (r, f"%::{r}")).fetchone()]
    if invented:
        raise ValueError(
            f"{', '.join(invented)} is a name the index does not hold and no "
            f"item or ticket gives. A surface is an existing callable or the "
            f"one the item names in words ({', '.join(new)}); nothing else")
    existing = [r for r in refs if ctx.conn.execute(
        "SELECT 1 FROM code_index WHERE grain = ? OR grain LIKE ?",
        (r, f"%::{r.split('::')[-1]}")).fetchone()]
    if refs and len(existing) == len(refs):
        raise ValueError(
            f"the item names {', '.join(new)}, and the index has no such "
            f"callable: a new behaviour is a new callable, and the item gives "
            f"its name. This surface names only what exists today "
            f"({', '.join(refs)}), so a test of it would test the old "
            f"behaviour. Name {new[0]} as the surface, in the file the item "
            f"names or the one the existing callables live in")


@op("criteria", "specify")
def criteria_specify(ctx: Ctx, id: str, ticket_id: str, text: str,
                     term_refs: list[str] | None = None,
                     surface_refs: list[str] | None = None) -> dict:
    """Criteria are written in glossary terms and name the surface a test
    would exercise; neither list is decoration."""
    # `ticket_id` that names an item. The model put the item under
    # `ticket_id` and the ticket under `id`, and each refusal named one of
    # the two, so it fixed one per round and flipped back the next: three
    # sessions, quarantine, no criterion (tipsN, 2026-09-09). One message
    # names both arguments and the call shape.
    if not ctx.conn.execute("SELECT 1 FROM tickets WHERE id = ?",
                            (ticket_id,)).fetchone():
        owned = [r["id"] for r in ctx.conn.execute(
            "SELECT id FROM tickets WHERE item_id = ? ORDER BY id", (ticket_id,))]
        if owned:
            raise ValueError(
                f"{ticket_id!r} is an item, not a ticket. Its tickets are "
                f"{owned}. A criterion belongs to one ticket: send "
                f"criteria.specify(id='c_1', ticket_id={owned[0]!r}, text=...) "
                f"with a new c_ id of your own and one of those ticket ids")
    _must_exist(ctx, "tickets", ticket_id)
    # The wake names the item whose tickets want criteria. clickI
    # (2026-09-10): woken for `show_python`, the Terminologist specified
    # criteria for `echo_json` three sessions running, and `show_python`
    # was quarantined with none. The ticket's item is a fact.
    woken = [r for r in (getattr(ctx, "wake_refs", ()) or ())
             if ctx.conn.execute("SELECT 1 FROM items WHERE id = ?", (r,)).fetchone()]
    if woken:
        owner = ctx.conn.execute(
            "SELECT item_id FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if owner and owner["item_id"] not in woken:
            theirs = [r["id"] for r in ctx.conn.execute(
                "SELECT id FROM tickets WHERE item_id = ? ORDER BY id", (woken[0],))]
            raise ValueError(
                f"{ticket_id!r} belongs to {owner['item_id']!r}, and you were "
                f"woken for {woken[0]!r}, whose tickets are {theirs}. Write "
                f"the criteria for those")
    # An id already claimed by a different ticket's criterion is not this
    # ticket's to reuse. Undetected, a second `criteria.specify` under the
    # same id silently overwrote the first at commit -- same primary key,
    # last write wins -- so the id's `ticket_id` and `text` both flipped to
    # the second ticket's, and the first ticket kept no criterion at all,
    # with no error to read and correct from. Measured on an empty-project
    # walk: two tickets under one item, one id reused for both across three
    # attempts, one criterion ever landed, the other ticket shipped with no
    # criterion and no test -- and the session's own closing reply narrated
    # both as done. Refused now, at the id, the same shape `problem.assert`
    # already refuses a kind clash on.
    prior_ticket = next((w[2].get("ticket_id") for w in ctx.writes
                        if w[0] == "criteria" and w[1] == id), None)
    if prior_ticket is None:
        row = ctx.conn.execute(
            "SELECT ticket_id FROM criteria WHERE id = ?", (id,)).fetchone()
        prior_ticket = row["ticket_id"] if row else None
    if prior_ticket is not None and prior_ticket != ticket_id:
        raise ValueError(
            f"{id!r} is already {prior_ticket}'s criterion. An id you invent "
            f"is yours once -- {ticket_id} needs its own; two tickets never "
            f"share one criterion's id, even written in the same turn")
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
    # Nearly the same words are the same criterion too. clickI night 18
    # (2026-09-12): 63 criteria for one flag, "the usage string must
    # include --show-python" beside "the usage string must explicitly list
    # --show-python", 55 of them in one reply. Word overlap is a fact about
    # two sentences; whether the ticket needs a fifth criterion is not.
    mine = set(_prose_words(text or ""))
    if mine:
        others = [(w[1], w[2].get("text", "")) for w in ctx.writes
                  if w[0] == "criteria" and isinstance(w[2], dict)
                  and w[2].get("ticket_id") == ticket_id]
        others += [(r["id"], r["text"]) for r in ctx.conn.execute(
            "SELECT id, text FROM criteria WHERE ticket_id = ?", (ticket_id,))]
        for other_id, other_text in others:
            theirs = set(_prose_words(other_text or ""))
            # 0.85, not 0.7: at 0.7 the door refused the fifth criterion of
            # `L3-a-challenge-reaches-the-role-that-can-answer-it` and llama
            # fell into prose instead of the challenge the case measures.
            # Near-verbatim only; the size of a ticket's criteria is the
            # brief's sentence, not this door's.
            if theirs and len(mine & theirs) >= 0.85 * len(mine | theirs):
                raise ValueError(
                    f"this says what {other_id} says, in nearly the same words "
                    f"({other_text[:80]!r}). One criterion per thing that must "
                    f"be true; a second sentence for the same thing is a second "
                    f"test of one fact")
    # Three is usual and six is many (the criteria brief, ruled 2026-09-12).
    # clickI night 38 (2026-09-13): twenty-four criteria on one ticket
    # (datetime, unicode, a docstring, test coverage, "no upper limit on
    # indent"), then a signoff page of twenty-five lines the principal
    # would not read, a relay that mistook them for items, and a landing
    # cut at the output budget. The count is a fact.
    existing = {r["id"] for r in ctx.conn.execute(
        "SELECT id FROM criteria WHERE ticket_id = ?", (ticket_id,))}
    existing |= {w[1] for w in ctx.writes
                 if w[0] == "criteria" and w[2].get("ticket_id") == ticket_id}
    if id not in existing and len(existing) >= 6:
        raise ValueError(
            f"{ticket_id} has {len(existing)} criteria already, and six is many. "
            f"A seventh decides scope the ticket never named. If the ticket "
            f"holds more than one piece of work, that is the Vision Keeper's to "
            f"slice: msg.challenge_vision_keeper with the ticket. Otherwise the "
            f"criteria are written; end")
    _surface_names_what_the_item_names(ctx, ticket_id, surface_refs)
    surface = _vet_surface(ctx, surface_refs, required=False, ticket_id=ticket_id)
    ctx.writes.append(("criteria", id, {
        "ticket_id": ticket_id, "text": text,
        "surface_refs": json.dumps(surface)}))
    # The glossary entries the criterion rests on, as `term` refs.
    for ref in term_refs or []:
        if isinstance(ref, str):
            stage_ref(ctx, "criteria", id, "term", ref)
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
    cur = ctx.conn.execute("SELECT text, ticket_id FROM criteria WHERE id = ?", (id,)).fetchone()
    if cur and _same_words(text, cur["text"]):
        return {"id": id, "unchanged": True,
                "note": "those are the criterion's own words; a repair changes "
                        "what a test can assert, and this did not. If this "
                        "criterion is right as it stands, the one that cannot "
                        "be encoded is a different row"}
    payload: dict = {"text": text,
                     "surface_refs": json.dumps(
                         _vet_surface(ctx, surface_refs, required=True,
                                      ticket_id=cur["ticket_id"] if cur else None))}
    # A respecified criterion is an amendment, so its version moves and the
    # Tester that gave up on it wakes. No reader reads a criterion's version.
    ctx.writes.append(("criteria", id, payload, True))
    # A list given replaces the list on file, and the list an earlier call
    # of this session staged: the refs not in it are retired. No list
    # leaves the refs as they are.
    if term_refs is not None:
        wanted = [ref for ref in term_refs if isinstance(ref, str)]
        staged = [w[2]["target"] for w in ctx.writes
                  if w[0] == "refs" and w[2].get("src_table") == "criteria"
                  and w[2].get("src_id") == id and w[2].get("kind") == "term"
                  and not w[2].get("retire")]
        for old in dict.fromkeys(_term_refs_of(ctx.conn, "criteria", id) + staged):
            if old not in wanted:
                retire_ref(ctx, "criteria", id, "term", old)
        for ref in wanted:
            stage_ref(ctx, "criteria", id, "term", ref)
        # The refs read back by rowid, as a set: the list's order is not kept.
    return {"id": id, "respecified": True}


@op("criteria", "load")
def criteria_load(ctx: Ctx, batch_id: str | None = None) -> list[dict]:
    bid = batch_id or ctx.batch_id
    if bid:
        # `tested_by` travels with the row. Walk eleven: three criteria had
        # tests and one did not, and every wake re-triaged and re-encoded
        # all four -- the mode could not see which debt was its own.
        rows = _rows(ctx.conn.execute(
            "SELECT c.id, c.ticket_id, c.text, c.surface_refs, "
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
                "SELECT c.id, c.ticket_id, c.text, c.surface_refs "
                "FROM criteria c WHERE c.id = ? OR EXISTS ("
                "  SELECT 1 FROM refs r WHERE r.src_table = 'criteria' "
                "    AND r.src_id = c.id AND r.kind = 'term' AND r.target = ?) "
                "ORDER BY c.id", (ref, ref))))
        seen = set()
        rows = [r for r in rows if not (r["id"] in seen or seen.add(r["id"]))]
    # The `term_refs` key stays, in its place in the row: after `text`,
    # before `surface_refs`. The row is the prompt. Its list comes from the
    # relation.
    for r in rows:
        after = {k: r.pop(k) for k in ("surface_refs", "tested_by") if k in r}
        r["term_refs"] = json.dumps(_term_refs_of(ctx.conn, "criteria", r["id"]))
        r.update(after)
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
    tickets = _woken_tickets(ctx)
    if _batch_is_subject(ctx, tickets):
        return _rows(ctx.conn.execute(
            "SELECT c.id, c.ticket_id, substr(c.text,1,120) AS headline "
            "FROM criteria c JOIN batch_tickets bt ON bt.ticket_id = c.ticket_id "
            "WHERE bt.batch_id = ? ORDER BY c.id", (ctx.batch_id,)))
    if tickets:
        marks = ",".join("?" * len(tickets))
        return _rows(ctx.conn.execute(
            f"SELECT id, ticket_id, substr(text,1,120) AS headline FROM criteria "
            f"WHERE ticket_id IN ({marks}) ORDER BY id", tickets))
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
    else:
        # The rule, said at the door. Measured on a cold walk (tipsE,
        # 2026-09-08): the Architect grouped tk_1 and tk_2, from two items,
        # under an invented id "calculate_tip_and_display_results". The
        # existence check refused the id and named the items that exist. The
        # model tried twice more and the tick was quarantined. Nothing said
        # that a batch is one item's tickets, or how to split.
        by_item: dict[str, list[str]] = {}
        for tid in ticket_ids:
            for r in ctx.conn.execute("SELECT item_id FROM tickets WHERE id = ?",
                                      (tid,)):
                by_item.setdefault(r["item_id"], []).append(tid)
        if by_item and item_id not in by_item:
            split = "; ".join(f"item_id={k!r} with ticket_ids={v}"
                              for k, v in sorted(by_item.items()))
            raise ValueError(
                f"{item_id!r} is not the item any of these tickets trace to. "
                f"A batch delivers exactly one approved item, and the item is "
                f"the one the tickets already name. Make one batch per item: "
                f"{split}. Do not invent an item id")
    _must_exist(ctx, "items", item_id)
    # A batch id is never reused. S0 walk thirty-four: after the cancel, the
    # Architect grouped the same tickets under id="b1" and the upsert
    # resurrected the abandoned batch -- its worktree, its regressed code,
    # its head commit -- which "abandoned is terminal" exists to forbid.
    # The grouping wake names the tickets that have no live batch; those
    # are the ones to group. tipsAV (2026-09-12): woken for the amended
    # item's new ticket, the Architect grouped two tickets already sitting
    # in a pending batch, four turns running, and the new ticket waited
    # until the tick was quarantined. Which tickets are unbatched is a fact
    # the wake already carries.
    if ctx.wake_refs and ticket_ids:
        stray = [t for t in ticket_ids if t not in ctx.wake_refs]
        if stray:
            raise ValueError(
                f"{', '.join(stray)} {'is' if len(stray) == 1 else 'are'} not "
                f"among the tickets you were woken to group. Those are "
                f"{', '.join(ctx.wake_refs)}: the tickets with no live batch. "
                f"A ticket already in a batch is not grouped again")
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
    # A predicted path lives where the tree has paths. seat1 (2026-09-12):
    # the touch note put "src/split_bill.py" to the person at the seat on a
    # repository with no src/, and they had to say so. A new file beside
    # existing ones is a prediction; a directory the index has never seen
    # is a guess about the tree, and the index is the fact.
    known_dirs = {""}
    for row in ctx.conn.execute(
            "SELECT grain FROM code_index WHERE grain_kind = 'path'"):
        parts = row["grain"].replace("\\", "/").split("/")
        for i in range(1, len(parts)):
            known_dirs.add("/".join(parts[:i]))
    # Only a nested path is checked: a new file at the root is a prediction
    # the tree can always hold.
    # No index, no fact: a run that has not scanned the tree cannot say
    # which directories it lacks.
    strays = [p for p in paths if "/" in p.replace("\\", "/")
              and "/".join(p.replace("\\", "/").split("/")[:-1]) not in known_dirs
              ] if known_dirs != {""} else []
    if strays:
        top = sorted(d for d in known_dirs if d and "/" not in d)[:6]
        raise ValueError(
            f"{strays[0]} is under a directory the tree does not have. The "
            f"directories here are {', '.join(top) or 'none: the modules sit at the root'}; "
            f"a new file goes beside the ones that exist, and the index says "
            f"where they are")
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

# The one word pair where a criterion and the request disagree most often.
# `tests.encode` reads both sets for its prints-or-returns wall, and
# `tests.triage` reads them for the wall at `encodable` (frame 81).
PRINTS = {"print", "prints", "printed", "printing", "output", "outputs",
          "display", "displays", "show", "shows", "write", "writes", "echo",
          "echoes"}
RETURNS = {"return", "returns", "returned", "returning", "result"}

_QUOTES = "\"'`‘’“”"


def _request_rows(ctx: Ctx, criterion_id: str) -> list[tuple[str, str]]:
    """
    The request's words behind a criterion, as (name, text), in order.

    The statements the item rests on come first, then the item, then the
    ticket. The ticket is a seat's derivation of the request, so it is last.
    The statement query is the one `batches.expect` reads for "the principal
    said".
    """
    crit = ctx.conn.execute("SELECT ticket_id FROM criteria WHERE id = ?",
                            (criterion_id,)).fetchone()
    tk = ctx.conn.execute("SELECT id, item_id, text FROM tickets WHERE id = ?",
                          (crit["ticket_id"] if crit else "",)).fetchone()
    if tk is None:
        return []
    it = ctx.conn.execute("SELECT id, text FROM items WHERE id = ?",
                          (tk["item_id"],)).fetchone()
    rows = [(r["id"], r["text"]) for r in ctx.conn.execute(
        "SELECT s.id AS id, s.text AS text FROM refs x "
        "JOIN statements s ON s.id = x.target "
        "WHERE x.src_table = 'items' AND x.kind = 'statement' AND x.src_id = ? "
        "AND s.status != 'superseded' ORDER BY s.id", (tk["item_id"],))]
    if it is not None:
        rows.append((f"item {it['id']}", it["text"] or ""))
    rows.append((f"ticket {tk['id']}", tk["text"] or ""))
    return rows


def _flat(text: str) -> str:
    """Lowercase, with each run of whitespace made one space."""
    return " ".join((text or "").split()).lower()


def _span_clean(span: str) -> str:
    """A copied span without its outer quote marks or its final stop."""
    t = " ".join((span or "").split())
    return t.strip(_QUOTES).rstrip(".,;:!?").strip(_QUOTES).strip()


def _span_flat(span: str) -> str:
    """A copied span in the form the check compares."""
    return _span_clean(span).lower()


def _verb_words(text: str) -> list[str]:
    """
    The plain words of a sentence, in order, without its identifiers.

    An identifier is a name and not a claim. Night 91's criterion says
    "echo_json returns a string", and "echo" there names the helper.
    """
    import re as _re
    out: list[str] = []
    for token in (text or "").lower().split():
        if "_" in token or _re.search(r"[a-z]\.[a-z]", token):
            continue
        out += _re.findall(r"[a-z]+", token)
    return out


def _first_verb(words: list[str], family: set[str]) -> str | None:
    """The word of the family to quote: a print or return word first."""
    hits = [w for w in words if w in family]
    if not hits:
        return None
    return sorted(hits, key=lambda w: (not w.startswith(("print", "return")),
                                       hits.index(w)))[0]


@op("tests", "triage")
def tests_triage(ctx: Ctx, criterion_id: str, verdict: str,
                 request_span: str | None = None,
                 criterion_span: str | None = None) -> dict:
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

    The sixth verdict, `contradicts_request`, answers a second question: does
    the criterion say what the request says? Night 91 (2026-09-24): the
    criterion said "returns a string", the request said "prints", and the
    Tester triaged `encodable`. The verdict carries two copied spans, and the
    op checks each against its source, as the parroting guard does. A
    verdict that passes stages the question to the Terminologist itself,
    born unresolved, so `criterion_repair` wakes the criterion's writer.
    """
    _must_exist(ctx, "criteria", criterion_id)
    if not hasattr(ctx, "triaged"):
        ctx.triaged = {}
    # A span on another verdict is ignored, not refused. qwen3:8b fills both
    # spans on every call, and the refusal looped the seat to an empty
    # session: L1-TS-encode-a-criterion went to 0/5 (frame 81, re-record).
    if verdict == "contradicts_request" and not (
            _span_flat(request_span or "") and _span_flat(criterion_span or "")):
        raise ValueError(
            "contradicts_request needs two spans. Copy request_span= from the "
            "request's words. Copy criterion_span= from the criterion.")
    done = ctx.conn.execute("SELECT id FROM tests WHERE criterion_id = ?",
                            (criterion_id,)).fetchone()
    crit_text = (ctx.conn.execute("SELECT text FROM criteria WHERE id = ?",
                                  (criterion_id,)).fetchone()["text"] or "")
    request = _request_rows(ctx, criterion_id) if not done else []
    found_in = None
    if verdict == "contradicts_request" and not done:
        # Every claim cites a source, and the op checks the claim against the
        # source. The composition's rule, in the parroting guard's shape.
        want = _span_flat(request_span or "")
        found_in = next((name for name, text in request
                         if want in _flat(text)), None)
        if found_in is None:
            raise ValueError(
                "request_span is not in the statements, the item or the "
                "ticket. Copy the span from the request's words, not a "
                "paraphrase")
        if _span_flat(criterion_span or "") not in _flat(crit_text):
            raise ValueError(
                f"criterion_span is not in the words of {criterion_id}. Copy "
                f"the span from the criterion, not a paraphrase")
    if verdict == "encodable" and not done and request:
        # The one measured pair, walled: a brief line alone is a prediction
        # about a 9B model, and s144 never said "prints" (frame 81, finding 6).
        # On the request side, "echo" names the helper in "next to echo". The
        # criterion side keeps the full set (frame 81, the diff review).
        req_prints = PRINTS - {"echo", "echoes"}
        crit_words = _verb_words(crit_text)
        req = [(name, _verb_words(text)) for name, text in request]
        req_words = [w for _, ws in req for w in ws]
        for c_says, c_other, r_says, r_other in (
                (RETURNS, PRINTS, req_prints, RETURNS),
                (PRINTS, RETURNS, RETURNS, req_prints)):
            cw = _first_verb(crit_words, c_says)
            rw = _first_verb(req_words, r_says)
            if (cw and rw and not _first_verb(crit_words, c_other)
                    and not _first_verb(req_words, r_other)):
                row = next(name for name, ws in req if rw in ws)
                raise ValueError(
                    f"{criterion_id} says '{cw}' and {row} says '{rw}'. Send "
                    f"tests.triage(criterion_id='{criterion_id}', "
                    f"verdict='contradicts_request', request_span='{rw}', "
                    f"criterion_span='{cw}').")
    ctx.triaged[criterion_id] = verdict
    if done:
        return {"criterion": criterion_id, "verdict": verdict,
                "next": f"nothing -- {done['id']} already encodes it; the "
                        f"criteria you were woken for are the ones without "
                        f"a tested_by"}
    # The ladder's rung is a fact of the message log: once the Terminologist
    # has answered two questions on this criterion, the message door refuses
    # a third, so the exit for `cannot` climbs. Night 63 (2026-09-14): the
    # Tester triaged `cannot`, was told to ask the Terminologist, was refused
    # for asking a third time, triaged `cannot` again, three sessions.
    import json as _json
    answered = 0
    for row in ctx.conn.execute(
            "SELECT m.body_refs FROM messages m JOIN messages a ON a.cause_id = m.id "
            "WHERE m.from_role = ? AND m.to_role = 'terminologist' "
            "AND m.verb = 'question' AND a.verb = 'answer'", (ctx.role,)):
        try:
            if criterion_id in set(_json.loads(row["body_refs"] or "[]")):
                answered += 1
        except (TypeError, ValueError):
            continue
    cannot_next = (
        "say what stops you: msg.question_terminologist with the "
        "criterion in refs and what you cannot do in the question. "
        "You do not have to know whose problem it is -- an answer "
        "that does not land climbs to the right desk on its own"
        if answered < 2 else
        f"the terminologist has answered {answered} questions on this "
        f"criterion and it is not settled, so the question climbs: "
        f"msg.question_vision_keeper with the criterion in refs and what "
        f"you cannot check in the question")
    nxt = {
        "encodable": "encode it: tests.encode names this criterion",
        "cannot": cannot_next,
        "ambiguous_word": "a word could mean more than one thing: "
                          "msg.question_terminologist with the criterion in "
                          "refs and the word in the question",
        "no_machine_check": "no machine could check the sentence however the "
                            "words are read: msg.question_vision_keeper with "
                            "the criterion in refs",
        "outside_fact": "checking needs a fact this project does not hold: "
                        "msg.question_researcher, saying what fact",
        # No "encode the others": the runner ends a session that holds a
        # staged message, as it does after `cannot`.
        "contradicts_request": f"routed: the Terminologist rewrites "
                               f"{criterion_id} before any test exists. End "
                               f"the session",
    }[verdict]
    out: dict = {}
    if verdict == "contradicts_request":
        # The verified spans are the evidence, and the order of the calls is
        # not. Compare the order-based guard that sandbox.py removed.
        staged = [w for w in ctx.writes if w[0] == "tests"
                  and w[2].get("criterion_id") == criterion_id]
        for w in staged:
            ctx.writes.remove(w)
        if staged:
            out["withdrawn"] = [w[1] for w in staged]
            out["note"] = (f"The verdict withdraws the test staged for "
                           f"{criterion_id} ({', '.join(out['withdrawn'])}). A "
                           f"criterion that contradicts the request gets no "
                           f"test.")
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
        # One row per criterion: a row this session staged counts as asked.
        tagged = next((m for m in ctx.outbound if m.get("route") == "triage"
                       and criterion_id in m["body_refs"]), None)
        if open_q:
            nxt = (f"already asked -- {open_q['id']} is open about this "
                   f"criterion and the answer will wake you. Encode the "
                   f"others or end the session")
        elif tagged:
            nxt = (f"already asked -- {tagged['id']} carries this criterion "
                   f"to the Terminologist. Encode the others or end the "
                   f"session")
        elif verdict == "contradicts_request":
            from ..core.runner import new_id
            crit = ctx.conn.execute("SELECT ticket_id FROM criteria WHERE id = ?",
                                    (criterion_id,)).fetchone()
            note = (f"{found_in} says '{_span_clean(request_span or '')}' and "
                    f"{criterion_id} says '{_span_clean(criterion_span or '')}'. "
                    f"Both cannot hold.")
            # The verdict is the route. A route the model must take in a
            # second call is the route s144 did not take (frame 81).
            ctx.outbound.append({
                "id": new_id("m", ctx.conn, offset=len(ctx.outbound)),
                "to_role": "terminologist", "verb": "question",
                "body_refs": [criterion_id, crit["ticket_id"]],
                "body_text": None, "round_no": 0, "cause_id": ctx.trigger,
                "status": "unresolved", "unresolved_note": note,
                "route": "triage",
            })
    return {"criterion": criterion_id, "verdict": verdict, "next": nxt, **out}



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
        "SELECT text, surface_refs, ticket_id FROM criteria "
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
        for ref in _term_refs_of(ctx.conn, "criteria", criterion_id):
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


# One signal, one check. Night 106 (2026-10-02): bg_2's two tests assigned
# `sys.stdin = io.StringIO(...)`. `code.write` counted only the words
# "monkeypatch" and "builtins" as a shield, so it refused every fix as
# unshielded. It sent the seat to a challenge the Tester had answered.
# `tests.encode` already counted the string "sys.stdin". Both doors now read
# the parsed body, so a word in a comment shields nothing either.
def _stdin_shields(tree) -> set[str]:
    """The dotted names a test body replaces: 'sys.stdin', 'builtins.input',
    or a module's own name such as 'click.termui.visible_prompt_func'.

    Reads `sys.stdin = ...`, and the calls `setattr(obj, 'name', ...)`,
    `setattr('dotted.name', ...)`, `patch('dotted.name')` and
    `patch.object(obj, 'name')` on any receiver. A module's own name counts
    only as a dotted path of identifiers, or on a name the body imports."""
    import ast as _ast
    import re as _re

    def dotted(node) -> str | None:
        parts = []
        while isinstance(node, _ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if not isinstance(node, _ast.Name):
            return None
        parts.append(node.id)
        return ".".join(reversed(parts))

    def text(node) -> str | None:
        if isinstance(node, _ast.Constant) and isinstance(node.value, str):
            return node.value
        return None

    def flat(t):
        # `sys.stdin, old = io.StringIO(''), sys.stdin` assigns sys.stdin too.
        if isinstance(t, (_ast.Tuple, _ast.List)):
            for e in t.elts:
                yield from flat(e)
        elif isinstance(t, _ast.Starred):
            yield from flat(t.value)
        else:
            yield t

    # `ns.input = 3` or `client.patch('/v1.input')` replaces no module's
    # name. The diff review of 538b84a (2026-10-02) found both passed.
    modules = {(a.asname or a.name).split(".")[0] for n in _ast.walk(tree)
               if isinstance(n, (_ast.Import, _ast.ImportFrom)) for a in n.names}
    path_shape = _re.compile(r"[A-Za-z_]\w*(\.[A-Za-z_]\w*)+")

    out: set[str] = set()
    for n in _ast.walk(tree):
        if isinstance(n, (_ast.Assign, _ast.AnnAssign)):
            for t in (n.targets if isinstance(n, _ast.Assign) else [n.target]):
                for e in flat(t):
                    if isinstance(e, _ast.Attribute) and dotted(e) == "sys.stdin":
                        out.add("sys.stdin")
            continue
        if not isinstance(n, _ast.Call) or not n.args:
            continue
        f = n.func
        verb = (f.attr if isinstance(f, _ast.Attribute)
                else f.id if isinstance(f, _ast.Name) else None)
        # `patch.object(obj, 'name')` is the object form of `patch`.
        if verb == "object" and not (isinstance(f, _ast.Attribute)
                                     and (dotted(f.value) or "").endswith("patch")):
            continue
        if verb not in ("setattr", "patch", "object"):
            continue
        first = text(n.args[0])
        if first is not None:
            if verb == "object" or not path_shape.fullmatch(first):
                continue
            target, values = first, n.args[1:]
        else:
            second = text(n.args[1]) if len(n.args) > 1 else None
            base = dotted(n.args[0])
            if verb == "patch" or not (second and base):
                continue
            if base not in ("sys", "builtins") and base.split(".")[0] not in modules:
                continue
            target, values = f"{base}.{second}", n.args[2:]
        # A bare `patch('sys.stdin')` puts a MagicMock there, and input()
        # then raises "readline() returned non-string". A stream is named.
        if target == "sys.stdin" and not (values or any(
                k.arg in ("new", "new_callable") for k in n.keywords)):
            continue
        out.add(target)
    return out


def _shields_input(shields: set[str]) -> bool:
    """True when the body gives `input()` a stream or a stand-in."""
    return "sys.stdin" in shields or "builtins.input" in shields


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
    # One form of the path for every door and for the stored row. A row
    # stored with backslashes ran as `error no tests ran` in
    # `harness._run_one` for good (frame 135's review at eb6c7ef).
    path = path.replace("\\", "/")
    # The fork is mandatory where the mode offers it: an encode is only legal
    # for a criterion this session has claimed encodable. The other three
    # verdicts name their owner, and taking that door is equally a completion.
    if hasattr(ctx, "triaged") and ctx.triaged.get(criterion_id) not in (None, "encodable"):
        # A routed criterion was judged already. "No triage verdict from you
        # yet" was false for it (s144's runner account, night 91).
        raise ValueError(
            f"{criterion_id} was triaged {ctx.triaged[criterion_id]} in this "
            f"session. A routed criterion gets no test. Encode the others or "
            f"end the session")
    if hasattr(ctx, "triaged") and ctx.triaged.get(criterion_id) != "encodable":
        # Said as the step, not as a name for it. qwen3.5:9b on the Titan
        # (2026-09-14) read "has no branch claim" as a field the criterion
        # lacked, triaged it `cannot` and asked the Vision Keeper what a
        # branch claim is, fifteen runs of fifteen.
        raise ValueError(
            f"{criterion_id} has no triage verdict from you yet. Call "
            f"tests.triage(criterion_id='{criterion_id}', verdict='encodable') "
            f"and then tests.encode in the same reply. The verdict 'cannot' "
            f"sends the criterion to the desk that can repair it instead")

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
    from ..core import fence as _fence
    _fence.check(path, tree, _criteria_texts(ctx))
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
    shields = _stdin_shields(tree)
    if "input" in names and not _shields_input(shields):
        raise Wall(
            "this test calls input(), and pytest captures stdin: the call "
            "raises OSError before any assertion runs, against any code. "
            "Feed the name in instead -- monkeypatch.setattr('builtins.input', "
            "lambda _='': 'Alice') -- or test the function that takes the "
            "name as an argument")
    # Closing the process's stdin is the same trap from the other side.
    # Click night 50, walk 2 (2026-09-14): two EOF tests did
    # `sys.stdin.close()`, the pytest process lost its stdin, both failed
    # against a correct confirm(), the Developer challenged, the Tester
    # held, ten rounds to the cap.
    closes_stdin = any(
        isinstance(n.func, _ast.Attribute) and n.func.attr == "close"
        and isinstance(n.func.value, _ast.Attribute) and n.func.value.attr == "stdin"
        for n in calls)
    if closes_stdin:
        raise Wall(
            "this test closes sys.stdin, and pytest's own stdin goes with it: "
            "the test fails against any code and can break the tests after "
            "it. An EOF is an empty stream: monkeypatch.setattr('sys.stdin', "
            "io.StringIO('')) -- then the call under test reads EOF and the "
            "assertion runs")
    # Same trap, one hop indirect: the test does not call input() itself, it
    # calls a function that does. `get_user_name()` reading input()
    # internally and a test asserting `get_user_name() == "User"` hits the
    # identical OSError -- stdin captured, no assertion ever runs -- and the
    # check above cannot see it, because the literal word "input" never
    # appears in this file's own text. Only checked against files already in
    # the worktree: a function the Developer has not written yet cannot be
    # inspected, and the ordinary NameError guard covers that case anyway.
    # A patch of builtins.input does not reach a module that bound `input`
    # to its own name at import. Click night 53 (2026-09-14): the test
    # patched builtins.input, confirm() read through visible_prompt_func,
    # and pytest raised OSError for the whole loop. The scan runs when the
    # body patches nothing, or patches builtins.input only.
    # `sys.stdin` as code, not the word in a comment: night 54 (2026-09-14)
    # wrote "when stdin is closed" in a comment and the scan stood down.
    patches_builtin_only = ("builtins.input" in shields
                            and "sys.stdin" not in shields)
    # A body that replaces sys.stdin, by monkeypatch or by assignment, has
    # given the reader a stream: night 57 (2026-09-14) assigned
    # `sys.stdin = io.StringIO('')` with a restore and was refused three
    # times as if it had patched nothing.
    unpatched = not _shields_input(shields)
    # A patch of the name the function reads through reaches it, as
    # `monkeypatch.setattr('click.termui.visible_prompt_func', ...)` does.
    reached = {t.rsplit(".", 1)[-1] for t in shields
               if t not in ("sys.stdin", "builtins.input")}
    if (unpatched or patches_builtin_only) and ctx.batch_id:
        try:
            root = _worktree_of(ctx)
        except Exception:                     # noqa: BLE001 -- no worktree yet
            root = None
        if root:
            called_bare = {n.func.id for n in calls
                           if isinstance(n.func, _ast.Name) and n.func.id != "input"}
            for pyfile in root.rglob("*.py"):
                rel = pyfile.relative_to(root).as_posix()
                if rel.startswith("tests/") or pyfile.stem.startswith("test_"):
                    continue
                try:
                    fn_tree = _ast.parse(pyfile.read_text(encoding="utf-8"))
                except (OSError, SyntaxError, UnicodeDecodeError):
                    continue
                # A module-level name bound to input() is input() by another
                # name: click's `visible_prompt_func = input`, passed down
                # into `_readline_prompt`. Click night 52 (2026-09-14): a
                # test called confirm() directly, the door saw no `input`,
                # pytest raised OSError, and the loop ran to the cap.
                readers = {"input"} | {
                    t.id for n in fn_tree.body
                    if isinstance(n, (_ast.Assign, _ast.AnnAssign))
                    and isinstance(getattr(n, "value", None), _ast.Name)
                    and n.value.id == "input"
                    for t in (n.targets if isinstance(n, _ast.Assign) else [n.target])
                    if isinstance(t, _ast.Name)}
                for node in _ast.walk(fn_tree):
                    if not (isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef))
                            and node.name in called_bare):
                        continue
                    via = {c.id for c in _ast.walk(node)
                           if isinstance(c, _ast.Name) and isinstance(c.ctx, _ast.Load)
                           and c.id in readers}
                    if not via or via & reached:
                        continue
                    aliases = sorted(via - {"input"})
                    if patches_builtin_only and not aliases:
                        continue                 # the patch reaches input() itself
                    module = rel[:-3].replace("/", ".")
                    if module.startswith("src."):
                        module = module[4:]
                    if aliases:
                        raise Wall(
                            f"{node.name}() reads input() through {aliases[0]}, a name "
                            f"{pyfile.name} bound to input at import, and this test "
                            f"calls {node.name}() under pytest, where stdin is captured: "
                            f"the call raises OSError before any assertion runs. A patch "
                            f"of builtins.input does not reach {aliases[0]}. Patch the "
                            f"name it reads through -- monkeypatch.setattr("
                            f"'{module}.{aliases[0]}', lambda _='': 'y') -- or give it "
                            f"an empty stream: monkeypatch.setattr('sys.stdin', "
                            f"io.StringIO(''))")
                    raise Wall(
                        f"{node.name}() reads input() internally "
                        f"({pyfile.name}), and this test calls "
                        f"{node.name}() directly under pytest, where "
                        f"stdin is captured: the call raises OSError "
                        f"before any assertion runs, against any code. "
                        f"Feed the name in instead -- "
                        f"monkeypatch.setattr('builtins.input', "
                        f"lambda _='': 'Alice') before calling "
                        f"{node.name}()")
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
        elif isinstance(n, _ast.ClassDef):
            defined.add(n.name)
        elif isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.Lambda)):
            # The def's own name is a binding too. Night 81 (2026-09-16): the
            # Tester defined `def cmd(): pass` in the body and invoked it, and
            # was refused for using cmd without importing it, twice.
            if not isinstance(n, _ast.Lambda):
                defined.add(n.name)
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
        # A library module used and never imported gets the line to add.
        # clickI night 46 (2026-09-14): `json.loads` with no `import json`,
        # the hint said "import the function the criterion's surface names",
        # the test already imported that function, and the same refusal
        # ended the session on its fourth turn.
        import importlib.util as _ilu
        try:
            is_module = _ilu.find_spec(unbound[0]) is not None
        except (ImportError, ValueError):
            is_module = False
        if is_module:
            raise Wall(
                f"the test uses {unbound[0]} and never imports it: a NameError "
                f"against any code. Add the line `import {unbound[0]}` at the "
                f"top of the body and send the encode again")
        # A Tester told to "import the function the surface names" invented
        # ledger, app and create_account five runs of five. The criterion
        # carries the surface, so the Wall names the import line.
        srow = ctx.conn.execute(
            "SELECT surface_refs FROM criteria WHERE id = ?",
            (criterion_id,)).fetchone()
        named = [s for s in (json.loads(srow["surface_refs"] or "[]") if srow else [])
                 if isinstance(s, str) and "::" in s]
        # A project with no build system is not installed, so pytest imports
        # it from the root and `src.` stays in the line. Frame 82's diff
        # review: `from billing.accounts import ...` failed at collection.
        from ..core.provision import project_installable
        try:
            _installed = project_installable(_worktree_of(ctx))
        except Exception:  # noqa: BLE001 -- no worktree yet: import from the root
            _installed = False
        module = (_dotted_module(_grain_path(named[0].split("::", 1)[0]),
                                 keep_root=not _installed) if named else "")
        if module:
            symbol = named[0].split("::", 1)[1].split(".", 1)[0]
            raise Wall(
                f"the test uses {unbound[0]} and never imports or defines it: "
                f"a NameError against any code. The criterion's surface is "
                f"{named[0]}: add `from {module} import {symbol}` and assert "
                f"on what it returns.")
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
    # A check can be a raise as well as an assert: `raise AssertionError`
    # in an except branch, `pytest.raises`, `pytest.fail`. Night 63
    # (2026-09-14): a signature test called confirm() with the new argument,
    # re-raised a TypeError as AssertionError, ended on `assert True`, and
    # was refused as checking nothing.
    def _raises_a_check(n) -> bool:
        if isinstance(n, _ast.Raise) and n.exc is not None:
            target = n.exc.func if isinstance(n.exc, _ast.Call) else n.exc
            return getattr(target, "id", None) == "AssertionError"
        if isinstance(n, _ast.Call):
            f = n.func
            return (isinstance(f, _ast.Attribute) and f.attr in ("raises", "fail")
                    and getattr(f.value, "id", None) == "pytest")
        return False
    checks_by_raise = any(_raises_a_check(n) for n in _ast.walk(tree))
    if (asserts and not checks_by_raise
            and all(isinstance(a.test, _ast.Constant) for a in asserts)):
        # Walk ten: `assert True` under "unit tests must validate the
        # script's behaviour" -- a criterion that is not a behaviour, met
        # with a test that is not a check. The honest verdict was `cannot`.
        raise Wall(
            "every assertion here is on a constant, so the test checks "
            "nothing and would report as coverage. If the criterion names "
            "no behaviour a call could exercise, that is tests.triage "
            "verdict='cannot' -- say what stops you and route it")
    # Names bound to a Mock -- `X = mock.Mock(...)`/`MagicMock(...)`, or
    # `with mock.patch(...) as X:` -- both spellings measured in the same
    # walk that found the guard below is needed.
    _mock_ctor = {"Mock", "MagicMock", "AsyncMock", "NonCallableMock"}
    mock_vars: set[str] = set()
    for n in _ast.walk(tree):
        if isinstance(n, _ast.Assign) and isinstance(n.value, _ast.Call):
            callee = n.value.func
            ctor = callee.attr if isinstance(callee, _ast.Attribute) else (
                callee.id if isinstance(callee, _ast.Name) else None)
            if ctor in _mock_ctor:
                mock_vars |= {t.id for t in n.targets if isinstance(t, _ast.Name)}
        elif isinstance(n, _ast.With):
            for item in n.items:
                fn = item.context_expr.func if isinstance(
                    item.context_expr, _ast.Call) else None
                fn_name = (fn.attr if isinstance(fn, _ast.Attribute) else
                          fn.id if isinstance(fn, _ast.Name) else "")
                if fn_name == "patch" and isinstance(item.optional_vars, _ast.Name):
                    mock_vars.add(item.optional_vars.id)
    _real_mock_methods = {
        "assert_called", "assert_called_once", "assert_called_with",
        "assert_called_once_with", "assert_any_call", "assert_has_calls",
        "assert_not_called", "reset_mock", "configure_mock", "attach_mock"}

    for a in asserts:
        # Walk thirteen: `assert print(...) == "Hello Alice!"` -- the print
        # moved inside a comparison and the guard on the bare call missed it.
        if any(isinstance(n, _ast.Call) and isinstance(n.func, _ast.Name)
               and n.func.id == "print" for n in _ast.walk(a.test)):
            # The fact and no recipe (Roman, 2026-09-15: the capsys clause
            # was the stdin family again; night 80's Tester wrote the shape
            # it was handed and no command ran).
            raise Wall(
                "`assert print(...)` is always False: print returns None, so "
                "the assertion compares None")
        # `mock_x.called_with(...)` -- not a real Mock method. Mock invents
        # an attribute for any name asked of it, so this silently returns a
        # new mock (always true) instead of raising AttributeError; the
        # assertion passes no matter what the mock saw. Measured (empty-
        # project walk, 2026-09-03): `assert mock_print.called_with("Hello
        # User!")` after the surface-call guard forced a real call to
        # `greet_user` -- the test finally exercised the function and still
        # could not fail, on this second, narrower wall.
        for n in _ast.walk(a.test):
            if (isinstance(n, _ast.Call) and isinstance(n.func, _ast.Attribute)
                    and isinstance(n.func.value, _ast.Name)
                    and n.func.value.id in mock_vars
                    and n.func.attr not in _real_mock_methods):
                raise Wall(
                    f"{n.func.value.id}.{n.func.attr}(...) is not a real Mock "
                    f"method -- Mock invents one for any name you ask it for, "
                    f"so this always returns a truthy mock instead of raising "
                    f"AttributeError, and the assertion cannot fail. The real "
                    f"check is {n.func.value.id}.assert_called_with(...) (or "
                    f"assert_any_call, assert_called_once_with)")

    # The criterion is checked *first*, because the batch is derived from it and
    # a derivation from a bad input fails in terms of the derived thing. An
    # invented `criterion_id` used to come back as "no batch in this session and
    # none given" -- true, unactionable, and about the one argument the model was
    # never given and cannot supply. Ten identical retries in one session, on a
    # case that had passed 130 times out of 140, and the fault was named nowhere
    # in the message. `_must_exist` names the ids that would have worked.
    _must_exist(ctx, "criteria", criterion_id)

    # A test that never calls what the criterion names as its surface has
    # not exercised the program -- it has exercised whatever it did call
    # instead, and a stub is indistinguishable from a correct implementation
    # to a test that never calls either. A harness fact, the same class as
    # stdin capture and `assert print(...)`: true for any code, not a
    # judgement about this one. Measured (empty-project walk, 2026-09-03):
    # `get_user_name`'s test mocked `builtins.input` and asserted on the
    # mock directly; `greet_user`'s test mocked `builtins.print` the same
    # way. Both passed forever, against a stub or a real implementation
    # alike, and the Developer had no door back from tests that could never
    # distinguish its work from a placeholder.
    surface_row = ctx.conn.execute(
        "SELECT surface_refs FROM criteria WHERE id = ?", (criterion_id,)
    ).fetchone()
    surface = json.loads(surface_row["surface_refs"] or "[]") if surface_row else []
    if surface:
        called_names = {n.func.id for n in calls if isinstance(n.func, _ast.Name)}
        called_names |= {n.func.attr for n in calls
                         if isinstance(n.func, _ast.Attribute)}
        # A reference is a use too: `inspect.signature(confirm)` exercises
        # confirm's signature without calling it. Click night 56
        # (2026-09-14): a signature criterion, refused as "never calls".
        called_names |= {n.id for n in _ast.walk(tree)
                         if isinstance(n, _ast.Name) and isinstance(n.ctx, _ast.Load)}
        # A surface ref is `path::name`. The test calls the name. Compared
        # whole, `from main import calculate_tip` + `calculate_tip(100, 10)`
        # was refused as never calling `main.py::calculate_tip`, three
        # sessions, quarantine, nothing merged (tipsK, 2026-09-09).
        surface_names = {s.rsplit("::", 1)[-1] for s in surface} | set(surface)
        # And from the surface's own module. tipsU (2026-09-09): the surface
        # was `main.py::calculate_tip` and the test did `from billing import
        # calculate_tip`; no such module, ImportError at collection, three
        # sessions, quarantine. The path half of a surface ref says where
        # the name lives.
        import re as _re2
        surface_mods = {s.split("::", 1)[0].replace("\\", "/").rsplit("/", 1)[-1][:-3]
                        for s in surface if "::" in s and s.split("::", 1)[0].endswith(".py")}
        _dotted = _dotted_module
        imported_from = set(_re2.findall(r"^\s*from\s+([A-Za-z_][\w.]*)\s+import", body, _re2.M))
        imported_from |= set(_re2.findall(r"^\s*import\s+([A-Za-z_]\w*)", body, _re2.M))
        # Every module the test imports must exist where the harness will
        # look: the worktree root, src/, an installed package, the standard
        # library. clickI night 24 (2026-09-12): three tests began `from
        # echo import echo_json`; `echo` is a function in click.utils, no
        # module named echo exists, every one died at collection, and the
        # Developer spent its fix sessions challenging the wrong test.
        import sys as _sys2
        try:
            _root = _worktree_of(ctx)
        except Exception:  # noqa: BLE001 -- no worktree yet: nothing to check against
            _root = None
        _known = set(getattr(_sys2, "stdlib_module_names", ())) | {"pytest"}
        if _root is None:
            _known |= {m.split(".")[0] for m in imported_from}
        else:
            _known |= {p.stem for p in _root.glob("*.py")} | {p.name for p in _root.iterdir() if p.is_dir()}
            for base in (_root / "src", _root / "lib"):
                if base.is_dir():
                    _known |= {p.stem for p in base.glob("*.py")} | {p.name for p in base.iterdir() if p.is_dir()}
        try:
            import tomllib as _toml
            if _root is not None and (_root / "pyproject.toml").is_file():
                _known.add((_toml.loads((_root / "pyproject.toml").read_text(encoding="utf-8"))
                            .get("project", {}).get("name", "") or "").replace("-", "_"))
        except Exception:  # noqa: BLE001 -- a manifest that does not parse names nothing
            pass
        _missing_mods = sorted(m.split(".")[0] for m in imported_from
                               if m.split(".")[0] not in _known)
        if _missing_mods:
            dotted_surfaces = sorted({_dotted(s.split("::", 1)[0]) for s in surface
                                      if "::" in s and s.split("::", 1)[0].endswith(".py")})
            # A bare surface names no file; the tree does. Night 25: the
            # hint listed .devcontainer, .github and .venv as "the modules
            # there" and never said `from click.echo_json import echo_json`.
            if not dotted_surfaces and _root is not None:
                for s in surface:
                    if "::" in s or not _re2.fullmatch(r"[A-Za-z_]\w*", s):
                        continue
                    pat = _re2.compile(rf"^\s*(?:def|class)\s+{_re2.escape(s)}(?!\w)", _re2.M)
                    for py in _root.rglob("*.py"):
                        rel = py.relative_to(_root).parts
                        if any(part.startswith(".") for part in rel) or "tests" in rel:
                            continue
                        try:
                            if pat.search(py.read_text(encoding="utf-8", errors="replace")):
                                dotted_surfaces.append(_dotted("/".join(rel)))
                                break
                        except OSError:
                            continue
            plain = sorted(m for m in _known - set(getattr(_sys2, "stdlib_module_names", ()))
                           if not m.startswith(".") and m not in ("tests", "docs", "pytest"))
            want = ", ".join(dotted_surfaces or plain[:6])
            hint = (f" Import the surface from its own module: `from {dotted_surfaces[0]} "
                    f"import {surface[0].rsplit('::', 1)[-1]}`") if dotted_surfaces else ""
            raise Wall(
                f"this test imports {', '.join(_missing_mods)}, and no module of "
                f"that name exists in the tree: the import path is the worktree "
                f"root and src/, and the modules there are {want}.{hint} If the "
                f"surface has no module yet, the Developer writes it first")
        # And only the surface, or what the module defines today. tipsAC
        # (2026-09-09): the Tester wrote `from main import calculate_tip,
        # Bill` and asserted on a list; nothing defined `Bill`, no criterion
        # named it, and the Developer rebuilt the program around the
        # invented API until quarantine. A test is black-box on the surface;
        # a name it invents is a design nobody asked for.
        for mod in surface_mods:
            names = set()
            for m in _re2.finditer(r"^\s*from\s+" + _re2.escape(mod) + r"\s+import\s+([^\r\n]+)",
                                   body, _re2.M):
                names |= {x.strip().split(" as ")[0] for x in m.group(1).split(",")}
            names.discard("*")
            defined: set[str] = set()
            mf = None
            try:
                # The module may be a file or a package, at the root or under
                # src/. tipsAY (2026-09-12): the Developer made a package
                # `split_bill/` with an empty __init__.py beside a `split_bill`
                # function in main.py, the Tester imported the name from the
                # package, this door looked only for split_bill.py, and every
                # test died at collection.
                _wt = _worktree_of(ctx)
                mf = next((p for p in (_wt / f"{mod}.py", _wt / mod / "__init__.py",
                                       _wt / "src" / f"{mod}.py", _wt / "src" / mod / "__init__.py")
                           if p.is_file()), _wt / f"{mod}.py")
                if mf.is_file():
                    defined = {n.name for n in _ast.parse(
                        mf.read_text(encoding="utf-8", errors="replace")).body
                        if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef,
                                          _ast.ClassDef))}
                    defined |= {t.id for n in _ast.parse(
                        mf.read_text(encoding="utf-8", errors="replace")).body
                        if isinstance(n, _ast.Assign) for t in n.targets
                        if isinstance(t, _ast.Name)}
            except Exception:  # noqa: BLE001 -- no worktree yet is "defines nothing"
                defined = set()
            invented = sorted(n for n in names if n and n not in surface_names
                              and n not in defined)
            if invented:
                raise Wall(
                    f"this test imports {', '.join(invented)} from {mod}, and "
                    f"{mod}.py defines no such name and no criterion names it. "
                    f"A test calls the surface the criterion names, "
                    f"{surface[0]!r}, and nothing it invents; if the surface "
                    f"needs a new type or helper, that is the Developer's to "
                    f"add and the criterion's to name. If the criterion's "
                    f"surface is the wrong callable for this behaviour, say so "
                    f"to its owner: msg.question_terminologist with the "
                    f"criterion and the name the test needs")
        # The surface's own name, imported from a module that exists and does
        # not define it. tipsAY (2026-09-12): `from split_bill import
        # split_bill` against an empty split_bill/__init__.py while main.py
        # held the function; four tests died at collection and the Developer
        # challenged the Tester for it. Every `from X import` in the body is
        # read, whatever the surface's own spelling; the tree says which file
        # defines the name.
        if _root is not None:
            for m in _re2.finditer(r"^\s*from\s+([A-Za-z_][\w.]*)\s+import\s+([^\r\n]+)", body, _re2.M):
                mod_name, imported = m.group(1), {x.strip().split(" as ")[0]
                                                 for x in m.group(2).split(",")}
                rel_mod = mod_name.replace(".", "/")
                found = next((p for p in (_root / f"{rel_mod}.py", _root / rel_mod / "__init__.py",
                                          _root / "src" / f"{rel_mod}.py",
                                          _root / "src" / rel_mod / "__init__.py")
                              if p.is_file()), None)
                if found is None:
                    continue
                try:
                    tree_mod = _ast.parse(found.read_text(encoding="utf-8", errors="replace"))
                except SyntaxError:
                    continue
                has = {n.name for n in tree_mod.body
                       if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef))}
                has |= {t.id for n in tree_mod.body if isinstance(n, _ast.Assign)
                        for t in n.targets if isinstance(t, _ast.Name)}
                has |= {a.name.split(".")[0] if a.asname is None else a.asname
                        for n in tree_mod.body if isinstance(n, (_ast.Import, _ast.ImportFrom))
                        for a in n.names}
                # Any imported name the module lacks, not only the criteria's
                # surfaces. Click night 55 (2026-09-14): `from click._compat
                # import _sentinel`, a name nothing defines, invented by the
                # Tester; ImportError at collection for the whole batch.
                misplaced = sorted(n for n in imported if n not in has and n != "*")
                if not misplaced:
                    continue
                if misplaced[0] not in surface_names:
                    raise Wall(
                        f"{found.relative_to(_root).as_posix()} does not define "
                        f"{misplaced[0]}, and no criterion names it: this test "
                        f"imports a name the module does not have, and the "
                        f"harness dies at collection. Import only what the module "
                        f"defines, or the surface the criterion names")
                where = None
                pat = _re2.compile(rf"^\s*(?:def|class)\s+{_re2.escape(misplaced[0])}(?!\w)", _re2.M)
                for py in _root.rglob("*.py"):
                    rel = py.relative_to(_root).parts
                    if any(part.startswith(".") for part in rel) or "tests" in rel:
                        continue
                    try:
                        if pat.search(py.read_text(encoding="utf-8", errors="replace")):
                            where = _dotted("/".join(rel))
                            break
                    except OSError:
                        continue
                raise Wall(
                    f"{found.relative_to(_root).as_posix()} does not define "
                    f"{misplaced[0]}, and this test imports it from there; the "
                    f"harness dies at collection. "
                    + (f"It is defined in {where}: `from {where} import {misplaced[0]}`"
                       if where else
                       f"Nothing in the tree defines it yet; the Developer writes it first"))
        # The dotted module a test imports, from the surface's path: a src
        # layout's `src/click/core.py` is `click.core`, a root module is its
        # stem. clickI night 23 (2026-09-12): the door compared the stem
        # `core` with the first segment of `click.core`, refused a correct
        # import twelve turns running, and told the Tester `from core
        # import`, which cannot import.
        surface_dotted = {_dotted(s.split("::", 1)[0])
                          for s in surface if "::" in s and s.split("::", 1)[0].endswith(".py")}
        # A root module imports by its stem; a package module by its dotted
        # name, and the bare stem of a package module does not import.
        imports_ok = any(m == d or ("." not in d and m.rsplit(".", 1)[-1] == d)
                         for m in imported_from for d in surface_dotted)
        if surface_dotted and imported_from and not imports_ok:
            want = sorted(surface_dotted)[0]
            raise Wall(
                f"the surface {surface[0]!r} lives in "
                f"{sorted(surface_mods)[0]}.py and this test imports from "
                f"{sorted(imported_from)[0]}. Import the surface from its own "
                f"module: `from {want} import "
                f"{surface[0].rsplit('::', 1)[-1]}`")
        if not (surface_names & called_names):
            raise Wall(
                f"this test never calls {surface[0]!r}, the surface the "
                f"criterion names -- call it and assert on what it returns "
                f"or does. A test that calls something else instead (a "
                f"mocked builtin, a different function) cannot tell a "
                f"correct {surface[0]} from a stub that never runs")

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
    # A test that uses the surface's return value asserts on a promise the
    # material may not make. clickI night 28 (2026-09-13): the sentence said
    # echo_json "prints an object as JSON", the one test did
    # `result = echo_json(obj); result.split(...)`, the helper printed and
    # returned None, and the fix loop ran to quarantine on both desks. The
    # same shape as an invented literal: an assumption, logged where it is
    # made, and the encode sent again unchanged.
    surface_now = json.loads(row["surface_refs"] or "[]") if (row := ctx.conn.execute(
        "SELECT surface_refs FROM criteria WHERE id = ?", (criterion_id,)).fetchone()) else []
    surface_now = {s.rsplit("::", 1)[-1] for s in surface_now}
    uses_return = None
    for node in _ast.walk(tree):
        call = None
        if isinstance(node, _ast.Assign) and isinstance(node.value, _ast.Call):
            call = node.value
        elif isinstance(node, (_ast.Compare, _ast.Return)):
            for sub in _ast.walk(node):
                if isinstance(sub, _ast.Call):
                    call = sub
                    break
        if call is not None:
            fn = call.func
            name = fn.id if isinstance(fn, _ast.Name) else getattr(fn, "attr", None)
            if name in surface_now:
                uses_return = name
                break
    if uses_return:
        material = _material_words(ctx, criterion_id)
        logged: set[str] = set()
        for r in ctx.conn.execute("SELECT default_taken FROM ledger WHERE about_ref = ?",
                                  (criterion_id,)):
            logged |= _words(r["default_taken"] or "")
        logged |= {w for t, i, *rest in ctx.writes if t == "ledger"
                   for w in _words(rest[0].get("default_taken", ""))}
        material |= logged
        # Only when the material's own words say the surface prints, writes
        # or shows: a pure function is tested on its return value, and that
        # is the normal shape of a test. The word sets are PRINTS and
        # RETURNS at module level, which `tests.triage` reads too.
        # The criterion under test speaks first. clickI night 42 (2026-09-13):
        # its own words said "printing", a sibling criterion on the ticket
        # said "return behavior", the union said both, and four tests that
        # asserted on the return value landed and failed against a helper
        # that printed the right JSON.
        own_row = ctx.conn.execute("SELECT text FROM criteria WHERE id = ?",
                                   (criterion_id,)).fetchone()
        own = _words(own_row["text"] or "") if own_row else set()
        own_prints = bool(PRINTS & own and not RETURNS & own)
        if own_prints:
            # No lift by a ledger row: clickI night 45 (2026-09-14) logged
            # "assumes echo_json prints rather than returning a value", whose
            # words lifted the door, and the test asserted on the return
            # value it had just said did not exist. The criterion says it
            # prints; the test asserts on what it prints.
            says_prints, says_returns = PRINTS & own, set()
        else:
            says_prints = PRINTS & material
            says_returns = RETURNS & material
        if says_prints and not says_returns and own_prints:
            raise ValueError(
                f"the test uses what {uses_return} returns, and the criterion "
                f"{criterion_id} says it prints")
        if says_prints and not says_returns:
            raise ValueError(
                f"the test uses what {uses_return} returns, and the criterion, "
                f"its ticket or the principal's words say it prints; nothing "
                f"says it returns anything. That is an assumption, and it is "
                f"logged where it is made: ledger.log(about_ref={criterion_id!r}, "
                f"about_table='criteria', assumption=\"the test assumes "
                f"{uses_return} returns what it prints\") -- then send this "
                f"encode again unchanged. Or assert on what it prints")

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
            # All of them in one refusal, one log covering all. clickI night
            # 46 (2026-09-14): 'key', then 'nested', then 'array', one per
            # turn, each logged and re-sent, and the session ran out.
            named = ", ".join(repr(w) for w in owed[:6])
            joined = " and ".join(owed[:6])
            raise ValueError(
                f"the test chooses {named}, and nothing in the criterion, "
                f"its ticket, the glossary or the principal's words says it. "
                f"That is an assumption, and it is logged where it is made: "
                f"ledger.log(about_ref={criterion_id!r}, about_table='criteria', "
                f"assumption=\"the test assumes {joined} where the material "
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
        "SELECT path, body, criterion_id FROM tests WHERE id = ?",
        (id,)).fetchone()
    if prior and prior["path"] == path and prior["body"] == body:
        return {"id": id, "unchanged": True,
                "note": "identical to what is already on file, so nothing was "
                        "written and no version moved."}

    # A project test is a row `harness.inherit` wrote. Two signs, either one:
    # no criterion, because every encode names one, or the id `inherit`
    # derives from the stored path, because a landed fix gives the row a
    # criterion and keeps the id. The `inh_` prefix alone is not a sign: a
    # Tester named its own tests `inh_echo_json_01` on night 119. Frame 135,
    # night 120 s140: a new test under a project id replaced test_confirm.py,
    # and bg_1 merged without running it.
    from ..core.harness import inherited_id
    project = prior is not None and (
        prior["criterion_id"] is None
        or id == inherited_id(prior["path"].replace("\\", "/")))
    # A wake challenges this project test only when the trigger's verb is
    # `challenge` and its refs name this id. All 31 Tester challenges of
    # nights 113 to 120 name the challenged test there. A challenge wake runs
    # in the sandbox mode `normal`, so the mode is no sign. A fix of the
    # project test at its own path in that wake is frame 128's open
    # question, and it behaves as it did before frame 135.
    challenged = False
    if project and getattr(ctx, "trigger", None):
        from ..core.db import refs_of
        msg = ctx.conn.execute(
            "SELECT verb, body_refs FROM messages WHERE id = ?",
            (ctx.trigger,)).fetchone()
        challenged = (msg is not None and msg["verb"] == "challenge"
                      and id in refs_of(msg["body_refs"]))
    # Each sentence names only a call this door then admits. Three reviews
    # found that a sentence naming any other call opened a new route. A path
    # that is another test's file is the clash door's, on the next call.
    if project and (prior["path"] != path or not challenged):
        said = f"{id} is the id of the project's test {prior['path']}."
        if challenged:
            said += (f" A fix of that test keeps its file: send this encode "
                     f"again with path={prior['path']!r}, or send a new id "
                     f"that you invent.")
        else:
            said += (" An encode never replaces a project test. Send this "
                     "encode again with a new id that you invent.")
        raise ValueError(said)

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
    #
    # A stored test of this criterion, sent under its own id, is a replace and
    # not a second test. Frame 123, night 117 s213: the guard refused the old
    # id with a real fix, because a new-id "fix" had landed first.
    stored = ctx.conn.execute(
        "SELECT path FROM tests WHERE id = ? AND criterion_id = ? "
        "AND batch_id = ?", (id, criterion_id, batch_id)).fetchone()
    replaces = stored is not None
    if replaces and stored["path"] != path:
        # The harness writes each row to its path and deletes nothing. A
        # replace under a new path leaves the old file on disk.
        raise ValueError(
            f"{id} is stored at {stored['path']}. To replace it, send this "
            f"encode again with path={stored['path']!r}.")
    done = [w for w in ctx.writes
            if w[0] == "tests" and w[2].get("criterion_id") == criterion_id]
    if done and not replaces:
        return {"id": done[0][1], "unchanged": True,
                "note": f"{criterion_id} already has a test this session "
                        f"({done[0][1]}), and one criterion takes one. Nothing "
                        f"was written. If that test is wrong, this is not the "
                        f"session that discovers it."}

    # A stored test belongs to its batch. The commit UPDATEs every staged
    # column (db.py), so an encode from another batch moved the row into
    # this one. After the one-test guard, so its answer stays as it was.
    other = ctx.conn.execute(
        "SELECT batch_id FROM tests WHERE id = ? AND batch_id != ?",
        (id, batch_id)).fetchone()
    if other is not None:
        raise ValueError(
            f"{id} is a test of batch {other['batch_id']}, and this session "
            f"writes batch {batch_id}. Choose another id.")

    # One file per test. Walk twelve: two tests named tests/test_input_
    # validation.py, the second overwrote the first on disk, and the harness
    # ran a file that encoded one criterion under two ids.
    clash = ctx.conn.execute(
        "SELECT id, criterion_id FROM tests "
        "WHERE path = ? AND id != ? AND batch_id = ?",
        (path, id, batch_id)).fetchone()
    if clash is not None and clash["criterion_id"] == criterion_id:
        # Frame 123: in 4 of 4 challenge sessions the Tester sent its fix
        # under a new id. The old door offered only a new file, so the old
        # test stayed and ran beside the fix.
        raise ValueError(
            f"{path} is {clash['id']}'s file, and {clash['id']} is the test "
            f"of this same criterion. To fix that test, send this encode "
            f"again with id={clash['id']!r}. The same id replaces it.")
    if clash is None:
        clash = next((w for w in ctx.writes if w[0] == "tests" and w[1] != id
                      and w[2].get("path") == path), None)
        clash = {"id": clash[1]} if clash else None
    if clash:
        raise ValueError(
            f"{path} is already {clash['id']}'s file; two tests in one file "
            f"overwrite each other on disk. Name this one for its own "
            f"criterion -- tests/test_<what it checks>.py")
    # A replace supersedes every test this session staged on the criterion.
    # The same id twice would move the version twice. Another id is the
    # left-over test frame 123 exists to stop (night 117 s213). A staged
    # row has no file yet: the harness writes files from stored rows only.
    dropped = []
    if replaces:
        dropped = [w[1] for w in done
                   if w[1] != id and w[2].get("batch_id") == batch_id]
        ctx.writes[:] = [w for w in ctx.writes
                         if not (w[0] == "tests"
                                 and w[2].get("batch_id") == batch_id and (
                                     w[1] == id
                                     or w[2].get("criterion_id") == criterion_id))]
    ctx.writes.append(("tests", id, {
        "batch_id": batch_id, "criterion_id": criterion_id,
        "path": path, "body": body}))
    if dropped:
        # A staged message that names a dropped test would land with a ref
        # to no row: the commit checks no refs. It names the replace instead.
        renamed = []
        for m in getattr(ctx, "outbound", None) or []:
            refs = m.get("body_refs") or []
            if not set(dropped) & set(refs):
                continue
            new_refs = []
            for r in refs:
                r = id if r in dropped else r
                if r == id and id in new_refs:
                    continue
                new_refs.append(r)
            m["body_refs"] = new_refs
            renamed.append(m["id"])
        note = (f"{', '.join(dropped)} was not kept: {id} replaces the "
                f"test of {criterion_id}, and one criterion takes one.")
        for mid in renamed:
            note += f" Your message {mid} now names {id}."
        return {"id": id, "note": note}
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

    The batch's own tests come first, then the inherited tests, each group in
    insertion order. An inherited test that passes or has no run shows its
    length and its file, not its body. A red inherited test keeps its body.
    """
    bid = batch_id or ctx.batch_id
    if not bid:
        return []
    rows = _rows(ctx.conn.execute(
        "SELECT t.id AS id, t.criterion_id AS criterion_id, t.path AS path, "
        "       t.body AS body, r.result AS last_result, "
        "       CASE WHEN r.result = 'pass' THEN NULL ELSE r.output END AS said, "
        "       r.commit_sha AS run_sha "
        "FROM tests t "
        "LEFT JOIN test_runs r ON r.id = ("
        "    SELECT id FROM test_runs WHERE test_id = t.id "
        "    ORDER BY attempt DESC, rowid DESC LIMIT 1) "
        "WHERE t.batch_id = ? "
        "ORDER BY t.criterion_id IS NULL, t.rowid", (bid,)))
    # A run is a statement about one commit. Finding 66 (2026-09-14): the
    # 9B wrote the fix, loaded the tests, read the old red as its fix
    # failing, and started over until the loop cut it. The files that
    # changed since the run are a fact of the worktree, so the row says
    # them. Nothing is said when nothing changed.
    from ..core import worktrees as _wt
    try:
        root = _worktree_of(ctx, bid)
    except Exception:
        # No project root or worktree (a synthetic fixture): the
        # changed-since fact has nothing to read and says nothing.
        root = None
    # The harness materialises the batch's tests into the worktree at run
    # time and the Developer's commits leave them out, so a test file is
    # the harness's furniture, not a change.
    furniture = {_grain_path(r["path"]) for r in rows if r.get("path")}
    seen: dict[str | None, list[str]] = {}
    # Where a red run raised, and whether the diff reached that file. Night
    # 75 (2026-09-15, finding 78): five tests failed inside click's own
    # test runner because the Tester invoked a bare function; the Developer
    # read its function seven times and never challenged. The frame is a
    # fact of the output, the touched files a fact of the worktree.
    import re as _re
    touched = set(_wt.batch_files(ctx.conn, bid) or []) if bid and root else set()
    for row in rows:
        sha = row.pop("run_sha", None)
        if row.get("last_result") in (None, "pass"):
            # Night 103, s170: 34 inherited bodies, 460,000 characters, put the
            # batch's own tests behind the push cap. A green inherited body
            # tells the reader nothing, so the row names its file (frame 101).
            if row.get("criterion_id") is None:
                state = "passing" if row.get("last_result") == "pass" else "not run yet"
                row["body"] = (f"{len(row.get('body') or '')} characters, {state}, "
                               f"not shown")
            continue
        if sha not in seen:
            seen[sha] = [p for p in (_wt.changed_since(root, sha) if root else [])
                         if _grain_path(p) not in furniture]
        if seen[sha]:
            row["changed since this run, not run"] = seen[sha]
        said = row.get("said") or ""
        frames = _re.findall(r"^(?P<path>[^\s:]+\.py):(?P<line>\d+): (?P<err>\w+(?:Error|Exception|Exit))", said, _re.M)
        if frames:
            path, line, err = frames[-1]
            path = path.replace(chr(92), "/")
            if err == "AssertionError":
                row["raised at"] = f"{path}:{line}, the test's own assertion"
            else:
                reach = "a file your diff touched" if path in touched else "a file your diff did not touch"
                row["raised at"] = (f"{path}:{line} ({err}) before any assertion ran, "
                                    f"in {reach}")
    return rows


@op("tests", "consult")
def tests_consult(ctx: Ctx) -> list[dict]:
    return _rows(ctx.conn.execute(
        "SELECT id, batch_id, criterion_id, path FROM tests ORDER BY id"))


# ---------------------------------------------------------------------------
# journals
# ---------------------------------------------------------------------------

def _ask_of(ctx: Ctx):
    """The confirm, present or clarify the triggering reply answers, or None.

    A confirm or a present must still be open. Two consoles can read one
    present, and the first ruling to land wins (`principal.land`).

    A clarify is already answered, always: `parse_reply` turns a reply to a
    clarify into a `converse` and `land` closes the ask on the keypress. The
    Liaison still has to read the words, so the page is the clarify and the
    status check cannot apply to it. A park ask is the one clarify that stays
    open after words (frame 87).
    """
    trigger = getattr(ctx, "trigger", None)
    if not trigger:
        return None
    return ctx.conn.execute(
        "SELECT a.id, a.verb, a.body_refs, a.body_text FROM messages m "
        "JOIN messages a ON a.id = m.cause_id WHERE m.id = ? "
        "AND (a.verb = 'clarify' "
        "     OR (a.verb IN ('confirm', 'present') AND a.status = 'open'))",
        (trigger,)).fetchone()


@op("rulings", "rule")
def rulings_rule(ctx: Ctx, rulings: dict | None = None, words: str = "",
                 ask: str = "") -> dict:
    """
    The principal's reply, read as a ruling on the page it answers.

    One function for the whole mode. `rulings` records the ruling. `ask`
    instead sends the principal one sentence: an answer to a question about
    the page, or the one thing the reply does not settle. Measured with a
    second function for that (2026-09-10): given `msg.converse_principal`
    beside this one, llama3.1:8b sent the principal's words back as a
    converse 5/5 on every ruling case, under three briefs and two bases.
    The tool in the list was the invitation.

    The seat is text. The principal answers a page in their own words, and
    no parser reads the words. The Liaison reads them with the page in front
    of it and records the reading here: each numbered line of the page, or
    each row id, to approve, contest or revise. `words` carry the reply for
    the owner of a contested row. The ruling lands through `principal.land`
    after this session commits, so a session that dies lands nothing.

    Mechanical here: the page is a fact. A line number must be on the page.
    Every line of the page needs a ruling, because the ask closes when the
    ruling lands and an unnamed line would close unruled. One ruling per
    session: a second is a second reading of the same words.
    """
    from ..core.runner import new_id
    from .principal import render_page

    page = _ask_of(ctx)
    if page is None:
        raise ValueError(
            "no open page: this session was not woken by a reply to a "
            "confirm, a present or a clarify, so there is nothing to rule "
            "on. Stop")
    if any(w[0] == "rulings" for w in (ctx.writes or [])):
        raise ValueError(
            "this reply is already read: one ruling per reply. Stop")
    if (ask or "").strip():
        # A question beside a ruling is the question. The register
        # (2026-09-11): qwen3:8b answered a question about line 3 with the
        # right sentence in `ask` and a rulings map beside it, 5/5, and
        # the refusal "not both" cost the answer. The map is dropped: a
        # question keeps the page open, and the next reply rules.
        if any(m["to_role"] == "principal" for m in (ctx.outbound or [])):
            raise ValueError("the principal has your sentence. Stop")
        refs = json.loads(page["body_refs"] or "[]")
        mid = new_id("m", ctx.conn, offset=len(ctx.outbound or []))
        ctx.outbound.append({
            "id": mid, "to_role": "principal", "verb": "converse",
            "body_refs": refs, "body_text": ask.strip(), "round_no": 0,
            "cause_id": ctx.trigger})
        return {"id": mid, "to": "principal", "said": ask.strip()}
    # A park ask closes on a commit or a contest, and never on a reading of
    # words. A ruling here would close it and cancel the batch on the
    # Liaison's reading (ruled: Roman, 2026-09-27: the principal decides).
    from ..core.scheduler import park_ask_batch

    if park_ask_batch(page["id"]):
        refs = json.loads(page["body_refs"] or "[]")
        raise ValueError(
            f"this page is a park ask, and it has no line to rule. A new commit "
            f"starts the change again, and a contest of "
            f"{refs[0] if refs else 'the item'} stops it. Answer the reply in "
            f"one sentence with `ask`")
    ask = page
    refs = json.loads(ask["body_refs"] or "[]")
    order = render_page(ctx.conn, ask["verb"], refs, ask["body_text"])[1] or []
    # A page with no numbered line, the touch note, takes an empty ruling:
    # the reply acknowledged it. tipsAS (2026-09-11): the Liaison sent
    # rulings={} for the touch note and was refused, the only right
    # answer, and the page stayed open under "Waiting on you".
    batches_only = bool(refs) and all(ctx.conn.execute(
        "SELECT 1 FROM batches WHERE id = ?", (r,)).fetchone() for r in refs)
    # A clarify numbers no line, so `order` is empty for every clarify. The
    # door above would then read an empty ruling as "approve all", which is
    # the reading this fix exists to stop: silence is not consent
    # (`principal.land`, the empty-converse walk of clickI).
    #
    # The page stays empty. Filling `order` from the refs gave the reply a
    # numbered page the principal never saw, and the door then refused a
    # partial reading with "a line the reply does not contest is approve".
    # The diff review of 6895000 landed two approves for the reply "what time
    # is the meeting" through that door. A clarify takes a partial map, and
    # each row the map leaves out is parked, not approved.
    is_clarify = ask["verb"] == "clarify"
    if is_clarify:
        batches_only = False
    if (isinstance(rulings, dict) and not rulings and not is_clarify
            and (not order or batches_only)):
        rid = new_id("r", ctx.conn)
        ctx.writes.append(("rulings", rid, {
            "id": rid, "ask_id": ask["id"], "reply_id": ctx.trigger,
            "per_item": json.dumps({r: "approve" for r in refs}),
            "words": (words or "").strip(), "status": "open"}))
        return {"id": rid, "per_item": {r: "approve" for r in refs},
                "note": "the page had no line to rule on; acknowledged"}
    if not isinstance(rulings, dict) or not rulings:
        raise ValueError(
            "rulings is a map of page line number (or row id) to approve, "
            "contest or revise, for example {\"1\": \"approve\", "
            "\"2\": \"contest\"}")
    if not is_clarify:
        order = order or refs
    per_item: dict[str, str] = {}
    for key, ruling in rulings.items():
        key = str(key).strip()
        ruling = str(ruling).strip().lower()
        if ruling not in ("approve", "contest", "revise"):
            raise ValueError(
                f"line {key}: {ruling!r} is not a ruling. Each line takes "
                f"approve, contest or revise")
        if order and key.isdigit() and 1 <= int(key) <= len(order):
            per_item[order[int(key) - 1]] = ruling
        elif key in refs:
            per_item[key] = ruling
        elif is_clarify:
            raise ValueError(
                f"{key!r} is not a row of this question. A clarify numbers no "
                f"line, so each key is a row id from `about`: "
                f"{', '.join(refs)}")
        else:
            raise ValueError(
                f"{key!r} is not a line of the page. The page numbers its "
                f"rows 1 to {len(order)}; use those numbers")
    if not is_clarify:
        unnamed = [str(i + 1) for i, r in enumerate(order) if r not in per_item]
        if unnamed:
            raise ValueError(
                f"lines {', '.join(unnamed)} have no ruling. Every line of the "
                f"page takes one: the ask closes when the ruling lands. A line "
                f"the reply does not contest is approve")
    if is_clarify and not (words or "").strip():
        # A reading rests on the principal's words. The door cannot read them,
        # so it holds the one fact it can check: a ruling with no words on
        # file is a ruling with nothing behind it.
        raise ValueError(
            "a reading carries the principal's words, and words is empty. "
            "Pass the reply, whole")
    if any(v != "approve" for v in per_item.values()) and not (words or "").strip():
        raise ValueError(
            "a contest carries the principal's words to the row's owner, and "
            "words is empty. Pass the reply, whole")
    # Each row the answer left out is parked, one ledger row each, with the
    # class on the row. The obligation stays visible and countable until a
    # ruling discharges it (`plans/composition.md`, Records).
    parked = []
    if is_clarify:
        from ..core.predicates import UNADDRESSED_ANSWER

        asked = " ".join((ask["body_text"] or "the question").split())
        for r in refs:
            if r in per_item:
                continue
            table = _table_of_ref(ctx.conn, r)
            if table is None:
                continue
            _stage_ledger(ctx, r, table, f"{UNADDRESSED_ANSWER}: {asked}",
                          UNADDRESSED_KIND)
            parked.append(r)
    rid = new_id("r", ctx.conn)
    ctx.writes.append(("rulings", rid, {
        "id": rid, "ask_id": ask["id"], "reply_id": ctx.trigger,
        "per_item": json.dumps(per_item), "words": (words or "").strip(),
        "status": "open"}))
    out = {"id": rid, "per_item": per_item}
    if parked:
        out["parked"] = parked
        out["note"] = ("the answer said nothing about these rows, so each one "
                       "is logged and stays on the principal's agenda")
    return out


@op("rulings", "line")
def rulings_line(ctx: Ctx, line: str) -> dict:
    """
    The row behind one numbered line of the page.

    A long page carries `rows_not_shown` instead of `line_rows`, and this is
    how the seat reads one of the rows that did not fit. A present of 77 lines
    carried every row twice and came to 17,220 tokens against a 12,288 window,
    so ollama cut the prompt to half the window, kept the tail, and both seats
    answered as generic assistants (night 85, 2026-09-18). The page holds every
    line as the principal read it. This answers the one question the page does
    not: where a line came from, or what it says in full.

    `line` takes no default, so the wake never pushes this read. A row arrives
    when the seat asks for it, which is the whole point of the change.
    """
    from ..core.runner import _resolve_refs, _table_of
    from .principal import render_page

    page = _ask_of(ctx)
    if page is None:
        raise ValueError(
            "no open page: this session was not woken by a reply to a "
            "confirm, a present or a clarify, so there is no line to read. "
            "Stop")
    refs = json.loads(page["body_refs"] or "[]")
    order = render_page(ctx.conn, page["verb"], refs,
                        page["body_text"])[1] or refs
    # A long page numbers its lines `"3": "l_1 (ledger)"`, so a seat that
    # copies the value back is passing the id with its kind on it.
    key = str(line).strip().split(" (")[0].strip()
    if key.isdigit() and 1 <= int(key) <= len(order):
        ref = order[int(key) - 1]
    elif key in order:
        ref = key
    else:
        raise ValueError(
            f"{key!r} is not a line of the page. The page numbers its rows 1 "
            f"to {len(order)}; `line` takes one of those numbers")
    row = _resolve_refs(ctx.conn, [ref]).get(ref)
    if not row:
        return {"line": key, "ref": ref, "row": None,
                "note": "the line names a row that no table holds"}
    row["table"] = _table_of(ctx.conn, ref) or row.get("table")
    return {"line": key, "ref": ref, "row": row}


@op("rulings", "load")
def rulings_load(ctx: Ctx, ask_id: str | None = None) -> list[dict]:
    """The readings on record, for one page or all. Read by the door, not
    offered to a session: the edge is `actor: system`."""
    if ask_id:
        return _rows(ctx.conn.execute(
            "SELECT * FROM rulings WHERE ask_id = ? ORDER BY rowid", (ask_id,)))
    return _rows(ctx.conn.execute("SELECT * FROM rulings ORDER BY rowid"))


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
    # A row of the table it says. tipsQ (2026-09-09): the Terminologist
    # logged `about_table="glossary_terms"` with a ledger id as the ref and
    # a tool refusal as the assumption, the agenda put it to the principal,
    # the approval woke the Terminologist, which logged the next one: 36
    # rounds of a ledger about the ledger.
    if about_table == "ledger" or ctx.conn.execute(
            "SELECT 1 FROM ledger WHERE id = ?", (about_ref,)).fetchone():
        raise ValueError(
            f"{about_ref!r} is a ledger row. An assumption is about an "
            f"artefact, never about another assumption. If a ruling on it "
            f"left you nothing to do, you are done")
    # A rota row under another table's name. A path or an entry as the
    # subject stays legal: reconcile logs "README says X" about README.md
    # under items, and that is the shape the design asks for.
    home = _table_of_ref(ctx.conn, about_ref)
    if home and about_table != home:
        raise ValueError(
            f"{about_ref!r} is a row of {home}, not of {about_table}. "
            f"about_ref and about_table name one row together; send "
            f"about_table={home!r}")

    # A disagreement names what differs. seat2 on click (2026-09-12): the
    # reconcile phase logged "the README says X. The code shows X", nineteen
    # times in the same words, and every one reached the person at the seat
    # as an assumption to rule on. Two halves in the same words are a
    # restatement, and the words are the fact.
    halves = None
    lower = (assumption or "").lower()
    for cut in (". the code shows", "; the code shows", "; code shows", " the code shows"):
        i = lower.find(cut)
        if i > 0:
            halves = (assumption[:i], assumption[i + len(cut):])
            break
    if halves:
        frame = {"the", "readme", "says", "code", "shows", "that", "documentation", "docs"}
        a, b = (set(_prose_words(h)) - frame for h in halves)
        if a and b and len(a & b) >= 0.8 * len(a | b):
            raise ValueError(
                "the two halves of this assumption say the same words: what "
                "the README says and what the code shows are the same "
                "sentence. A disagreement names what differs; a README that "
                "matches the code is nothing to log. Log only where the two "
                "sides differ, in the words each source uses. If every claim "
                "agrees, that is the answer: surveys.attest(outcome='none_found', "
                "citations=[the file]), and no ledger row")

    return {"id": _stage_ledger(ctx, about_ref, about_table, assumption)}


# The tables a ledger row can be about, in the order `ledger.log` checks them.
LEDGER_HOMES = ("items", "statements", "criteria", "tickets", "tests",
                "constraints", "glossary_terms", "model_areas", "frame_rulings")
# The class of a parking row: the principal answered, and the answer said
# nothing about this row. The door stamps the class; no model writes it.
UNADDRESSED_KIND = "unaddressed_answer"


def _table_of_ref(conn, ref: str) -> str | None:
    """The table the row lives in, or None."""
    return next((t for t in LEDGER_HOMES
                 if conn.execute(f"SELECT 1 FROM {t} WHERE id = ?",
                                 (ref,)).fetchone()), None)


def _stage_ledger(ctx: Ctx, about_ref: str, about_table: str, assumption: str,
                  kind: str = "default") -> str:
    """Stage one ledger row of one class, and return its id.

    A classed row keys on its class, not on its prose (`identity.py`). The
    diff review of 6895000 found a paraphrased parking sentence writing a new
    row every cycle, so the ledger grew without bound and nothing parked.
    """
    import hashlib

    seed = (f"{about_table}|{about_ref}|{kind}" if kind != "default"
            else f"{about_table}|{about_ref}|{assumption}")
    id = "l_" + hashlib.sha256(seed.encode()).hexdigest()[:10]
    ctx.writes.append(("ledger", id, {
        "about_ref": about_ref, "about_table": about_table,
        "default_taken": assumption, "kind": kind, "status": "open",
        "author": ctx.role}))
    return id


@op("ledger", "unaddressed")
def ledger_unaddressed(ctx: Ctx, about_ref: str, question: str) -> dict:
    """
    The principal answered, and the answer said nothing about this row.

    One call for each row the answer missed. The row stays open in the ledger
    and on the principal's agenda, so the question comes back to them. Give
    the question you asked, in one sentence. The door writes the class.

    Never rule a row the words do not settle. The principal rules, and you
    write what they ruled (`plans/composition.md`, Records).
    """
    from ..core.predicates import UNADDRESSED_ANSWER

    table = _table_of_ref(ctx.conn, about_ref)
    if table is None:
        raise ValueError(
            f"{about_ref!r} names no row. about_ref is the id of a row the "
            f"question was about, from `about_rows`")
    said = (question or "").strip()
    if not said:
        raise ValueError(
            "question is the question you put to the principal, in one "
            "sentence. The row is parked against that question")
    id = _stage_ledger(ctx, about_ref, table,
                       f"{UNADDRESSED_ANSWER}: {said}", UNADDRESSED_KIND)
    return {"id": id, "about_ref": about_ref, "parked": True}


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


@op("verdicts", "claim encodes")
def verdicts_claim_encodes(ctx: Ctx, criterion_id: str, encodes: bool) -> dict:
    """
    The branch a fail verdict skipped past: does this criterion's test
    actually encode it?

    `CR-a-test-that-encodes-nothing` (chronic, attributed): the model reads
    the criteria in order and emits `verdicts.emit(fail, ...)` on the first
    one whose test looks wrong, following the brief's own numbered steps --
    never reaching the line that says a wrong *test* is `msg.challenge_tester`,
    not a fail. The two acts were both available and nothing made choosing
    between them a decision rather than a default. This is the decision,
    made its own call: `encodes=True` is what a fail verdict is allowed to
    stand on; `encodes=False` is what a challenge is for, not a code fail.
    """
    _must_exist(ctx, "criteria", criterion_id)
    # One claim per criterion, not reversible within the session. Measured
    # the day this landed: refused a fail on a criterion claimed False, and
    # the next turn reclaimed the same criterion True and the fail landed
    # anyway -- the guard asked a question and trusted whatever answer
    # arrived second. Same shape `problem.assert` already refuses a kind
    # clash on: the first claim is the session's, not to be relitigated
    # because the first answer was inconvenient.
    prior = ctx.verdict_claims.get(criterion_id)
    if prior is not None and prior != bool(encodes):
        raise ValueError(
            f"you already claimed {criterion_id}'s test "
            f"{'encodes' if prior else 'does not encode'} it this session; "
            f"that is the session's answer, not to be reversed because a "
            f"fail on it was refused. If the test genuinely does not "
            f"encode the criterion, that is `msg.challenge_tester`, not a "
            f"second claim")
    ctx.verdict_claims[criterion_id] = bool(encodes)
    if encodes:
        return {"criterion_id": criterion_id, "encodes": True}
    return {"criterion_id": criterion_id, "encodes": False,
           "note": "then this is msg.challenge_tester, refs naming the "
                   "criterion and the test, quotes= copying the span that "
                   "does not encode it -- not a fail on the code"}


@op("verdicts", "emit")
def verdicts_emit(ctx: Ctx, batch_id: str, result: str,
                  failed_criterion: str | None = None, reason: str = "",
                  diff_ref: str = "") -> dict:
    """
    Judge a commit. `result` is 'pass' or 'fail'; name the criterion a fail
    fails.

    `reason`, on a fail: the criterion's words the work does not meet, and
    what the work does instead. The Developer reads it beside the ref (ruled
    by Roman, frame 88, 2026-09-30). Never refused, on a pass or on a fail
    without one: an optional argument is filled on every call, and a refusal
    of it loops the seat (observed: frame 81, 2026-09-24).

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
    # Frame 107. The Terminologist's answer wakes the Critic after its
    # verdict landed. The tool refuses a second verdict, so the rule does
    # not rest on the brief alone (ruled: Roman, 2026-10-01: the Critic's
    # doubt about a criterion goes to the Terminologist, the writer of the
    # criteria).
    commit = _head_commit(ctx, batch_id)
    id = f"{ctx.role}:{batch_id}:{commit}"
    if (any(w[0] == "verdicts" and w[1] == id for w in ctx.writes)
            or ctx.conn.execute("SELECT 1 FROM verdicts WHERE id = ?",
                                (id,)).fetchone()):
        raise ValueError(
            f"your verdict on batch {batch_id} at this commit already "
            f"landed, and one commit gets one verdict: end the session")
    if failed_criterion:
        _must_exist(ctx, "criteria", failed_criterion)
        # The mandatory branch: a fail names a criterion whose test was
        # claimed to encode it. Unclaimed or claimed False means the thing
        # actually wrong might be the test, and that question was never
        # asked -- `verdicts.claim_encodes` is where it gets asked.
        claim = ctx.verdict_claims.get(failed_criterion)
        if claim is not True:
            raise ValueError(
                f"a fail on {failed_criterion} stands on its test actually "
                f"encoding it, and that has not been claimed this session"
                + ("" if claim is None else " -- it was claimed False") +
                f". `verdicts.claim_encodes({failed_criterion!r}, encodes=...)` "
                f"first: True and the fail can land, False and this is "
                f"`msg.challenge_tester` instead, not a fail on the code")
    ctx.writes.append(("verdicts", id, {
        "batch_id": batch_id, "result": result,
        "commit_sha": commit,
        "failed_criterion": failed_criterion, "reason": reason,
        "diff_ref": diff_ref}))
    return {"id": id, "result": result}


@op("verdicts", "load")
def verdicts_load(ctx: Ctx, batch_id: str | None = None) -> list[dict]:
    """
    The verdicts at the batch's head commit, or the whole history when none
    is at the head.

    The rule holds in every mode that holds `verdicts.load`, not only for
    the Developer on `tick:verdict_failed`. Night 101 (2026-09-30) left five
    fails with five reasons on one batch, and the seat could not tell which
    was current. A mode woken with nothing at the head, such as an exhausted
    mode, still reads the history. The history comes newest first: each
    commit's verdict is its own row, so the rowid orders the commits.
    """
    bid = batch_id or ctx.batch_id
    cols = ("SELECT v.id, v.batch_id, v.commit_sha, v.result, "
            "v.failed_criterion, v.reason FROM verdicts v ")
    at_head = _rows(ctx.conn.execute(
        cols + "JOIN batches b ON b.id = v.batch_id "
        "WHERE v.batch_id = ? AND v.commit_sha = b.head_commit "
        "ORDER BY v.rowid DESC", (bid,)))
    if at_head:
        return at_head
    return _rows(ctx.conn.execute(
        cols + "WHERE v.batch_id = ? ORDER BY v.rowid DESC", (bid,)))


@op("verdicts", "rule")
def verdicts_rule(ctx: Ctx, finding_id: str, ruling: str, reason: str) -> dict:
    """
    The Critic's ruling on a finding filed after its pass: `upheld` sends the
    Developer back, `dismissed` lets the batch merge past the finding.

    Ruled by Roman on 2026-09-27: only the Critic can reopen a green,
    signed-off batch. Night 94: the Architect filed `fnd_1` against `echo`,
    a constraint the Critic had falsified, and the Developer woke twice and
    broke the imports. One row per finding and commit, and nothing else.
    """
    # The wake names the finding. The same door as `glossary.synthesise`:
    # name the set, do not merely reject the guess.
    named = [r for r in (ctx.wake_refs or ())[1:] if isinstance(r, str)]
    if ctx.wake_refs and finding_id not in named:
        raise ValueError(
            f"{finding_id!r} is not the finding you were woken about. That is "
            f"{', '.join(named) or 'none'}, and it is the finding this "
            f"session exists to rule on")
    if ruling not in ("upheld", "dismissed"):
        raise ValueError(
            f"{ruling!r} is not a ruling. A ruling is 'upheld', and the "
            f"Developer answers the finding, or 'dismissed', and the finding "
            f"does not hold the merge")
    if not (reason or "").strip():
        raise ValueError(
            "a ruling carries its reason: the line or the verdict that "
            "decided it")
    row = ctx.conn.execute(
        "SELECT batch_id FROM findings WHERE id = ?", (finding_id,)).fetchone()
    if not row:
        raise ValueError(f"{finding_id!r} is not a finding on file")
    commit = _head_commit(ctx, row["batch_id"])
    id = f"{ctx.role}:{finding_id}:{commit}"
    ctx.writes.append(("finding_rulings", id, {
        "finding_id": finding_id, "commit_sha": commit, "ruling": ruling,
        "reason": reason, "session_id": ctx.session_id or None}))
    return {"id": id, "ruling": ruling}


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

# How many grains one probe returns. It was 200, and 200 rows of the six
# columns render past `RESULT_CHARS`: measured on a 1048-row index, a probe
# rendered 5553 characters at the median and `option`, `test`, `click`,
# `termui` and `tests` each hit the cap and truncated at about 6084. The two
# span columns add about a quarter to a row. A truncated probe is the worst of
# both: the seat pays for the rows and loses the tail without being told which.
#
# What a full probe costs, corrected: 61 rows render 4,415 characters on a
# real 2,871-symbol index (the diff review of 34c3e72, F2). The first estimate
# of this comment, about 2,200, was taken on short grains and was half the
# truth. A turn that probes and then reads therefore spends about 4.4k before
# the source read starts, which is why the first source read of a turn has a
# floor under it in `rota/core/runner.py`.
PROBE_ROWS = 60


@op("code", "probe")
def code_probe(ctx: Ctx, pattern: str = "") -> list[dict]:
    if not (pattern or "").strip():
        return [{"note": "an empty pattern matches everything and tells you "
                         "nothing. Probe by the name the failing test calls, "
                         "or the word you are tracing -- `code.probe("
                         "pattern='line_total')`."}]
    # The span is why the probe is worth a turn: `line_start` and `line_end`
    # are the arguments of the `code.source` that follows, so a name becomes a
    # forty-line read instead of a four-hundred-line dump.
    #
    # A path grain has no definition to point at, and it said 0 and 0. The
    # brief tells the seat to read the span the probe gives, and
    # `code.source(path, 0, 0)` slices `lines[0:0]` and returns nothing -- the
    # `defs` map rescues a Python file and nothing rescues the rest (the diff
    # review of 34c3e72, F6). The row says what to do instead, and it keeps
    # both keys: `_as_table` drops a ragged row set back to JSON, which costs
    # more than the two cells.
    # A definition before a file. `build` gives every symbol a fan-in of 0
    # (`rota/onboarding/indexer.py:456`), so ordering by fan-in alone put every
    # matching path above every matching definition, and a broad pattern could
    # spend the whole cap on paths and return no span at all. Fan-in still
    # ranks inside each kind, and the grain breaks the tie so the rows are the
    # same rows on every run.
    hits = _rows(ctx.conn.execute(
        "SELECT grain, grain_kind, area, fan_in, line_start, line_end "
        "FROM code_index WHERE grain LIKE ? "
        "ORDER BY CASE grain_kind WHEN 'symbol' THEN 0 ELSE 1 END, "
        "fan_in DESC, grain LIMIT ?", (f"%{pattern}%", PROBE_ROWS)))
    if hits:
        for row in hits:
            if row["grain_kind"] != "symbol":
                row["line_start"], row["line_end"] = "whole file", ""
        total = ctx.conn.execute(
            "SELECT COUNT(*) AS n FROM code_index WHERE grain LIKE ?",
            (f"%{pattern}%",)).fetchone()["n"]
        if total > len(hits):
            # The note is a row of the same shape, so the table survives. It
            # does not offer a next range, because this op has no range
            # argument: the only way to see the rest is a narrower pattern.
            # It says the order it actually used: every symbol has a fan-in of
            # 0, so the definitions come back in name order and the files after
            # them by fan-in (the diff review of 34c3e72, F7).
            hits.insert(0, {"grain": f"{total} grains match '{pattern}'. The "
                                     f"{len(hits)} below are the definitions in "
                                     f"name order, then the files by fan-in. "
                                     f"The pattern is too broad. Probe a longer "
                                     f"name to reach the rest.",
                            "grain_kind": "", "area": "", "fan_in": "",
                            "line_start": "", "line_end": ""})
        return hits
    # Nothing matched, and the index of this batch may be the reason. The
    # lifecycle and the runner record a failed refresh under `index:<batch>`,
    # the way a missing worktree is recorded under `worktree:<batch>`. A probe
    # that comes back empty because the index is a commit behind must say so:
    # the role's next move is different if the name is absent from the tree
    # than if the index never saw the commit that added it.
    note = ctx.conn.execute(
        "SELECT value FROM config WHERE key = ?",
        (f"index:{ctx.batch_id}",)).fetchone() if ctx.batch_id else None
    if note and (note["value"] or "").strip():
        return [{"note": f"nothing in the index matches '{pattern}'. The index "
                         f"was not rebuilt after this batch's last commit "
                         f"({note['value']}), so a name this batch wrote can "
                         f"be missing from it -- read the file instead."}]
    return hits


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
        # One wording for every cut, from the one place that owns it. Imported
        # here, not at the top, because the runner reaches the ops and not the
        # other way round. No cassette carries this string, so the wording costs
        # no re-record (measured over the register, 2026-09-20).
        #
        # The call sentence stays an imperative, because `CLAUDE.md` rules the
        # imperative for an instruction. It is a rule and not a measurement:
        # `L1-TE-survey-an-area-for-its-terms` records 0/5 with this wording and
        # with the wording before it, and at the commit before this frame.
        from ..core.runner import cut_note
        out["not_shown"] = cut_note(
            "this area's files", len(omitted), len(shown) + len(omitted), "files",
            f"`code.source` any of {', '.join(omitted)} if the ones above "
            f"leave a word unexplained.")
    return out


@op("code", "prose")
def code_prose(ctx: Ctx, limit: int = 6000, path: str | None = None) -> dict:
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
    from ..core.scheduler import PROSE as _PROSE
    if path:
        # Asked by path: the file the session wants beside its own. clickI
        # night 38 (2026-09-13): `code.prose(path=...)` refused as an
        # unexpected argument in a wake that is about one file.
        readme = path.replace("\\", "/").lstrip("./")
    elif ctx.area and ctx.area.startswith(_PROSE + ":"):
        # A prose file under docs/, the wake's own subject (one file a
        # session, `prose_areas`). The README is the bare `@prose`.
        readme = ctx.area[len(_PROSE) + 1:]
    else:
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
        from ..core.runner import cut_note
        # An imperative, for the rule named at `code_area`'s own cut.
        out["not_shown"] = cut_note(
            "the front's files", len(omitted), len(shown) + len(omitted), "files",
            f"`code.source` any of {', '.join(omitted)} if the front above "
            f"leaves the program unexplained.")
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


def _challenge_ledger_id(table: str, row: str) -> str:
    """
    The Critic's ledger row for a claim, deterministic per claim and never
    longer than an id may be. `challenge_constraints_<a long constraint
    id>` ran to seventy characters, the ref door allows sixty-four, and the
    agenda could not present the row: three sessions, quarantine (tipsN,
    2026-09-09). A long one keeps its head and ends in a hash of the whole.
    """
    import hashlib

    base = f"challenge_{_slug_of(table)}_{_slug_of(row)}"
    if len(base) <= 60:
        return base
    return base[:52] + "_" + hashlib.sha1(base.encode("utf-8")).hexdigest()[:7]


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

    # A finding review names a batch and a finding, and no claim. The claim is
    # the finding's constraint, and the Critic's own verdict on it travels
    # beside it. Night 94: `fnd_1` stood on `echo`, which the Critic had
    # falsified in s78, and no op showed the Critic that fact (frame 88).
    finding = _finding_of_wake(ctx)
    if finding is not None:
        table, row = "constraints", finding["constraint_id"]
    else:
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
        # What the row rests on, from the relation: the code it read and
        # the world it cites. A sigil (`@fixture`, `@claim:...`) is not a
        # path and not a reference, so it is not cited.
        cited = [x["target"] for x in ctx.conn.execute(
            "SELECT target FROM refs WHERE src_table = ? AND src_id = ? "
            "AND kind IN ('grain', 'reference') ORDER BY rowid", (table, row))
            if not x["target"].startswith("@")]
    # A claim that cites nothing has nothing to open. Loading it is the
    # reading. Without this, `challenge.vacuous` on an item claim could
    # never be reached: the Critic read a file that does not exist, eleven
    # sessions, three quarantines (tipsK, 2026-09-09).
    if not cited:
        ctx.opened.add(f"@claim:{table}:{row}")
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
    out = {"claim": f"[{table}:{row}] {claim}",
           "cited": cited,
           "sources": (chr(10) + chr(10)).join(parts) if parts else
                      "the claim cites nothing -- open what would decide it"}
    # Only on a finding review, so the challenge mode's result keeps its shape
    # and no recorded prompt moves.
    if finding is not None:
        c = ctx.conn.execute(
            "SELECT verdict, citation, quote, why FROM challenges WHERE id = ?",
            (f"{table}:{row}",)).fetchone()
        out["your challenge verdict"] = (
            {k: c[k] for k in ("verdict", "citation", "quote", "why")} if c
            else "you have not challenged this claim")
    return out


def _finding_of_wake(ctx: Ctx):
    """The finding a `tick:finding_review` wake names, or None.

    The wake's refs are `(batch_id, finding_id)`. Any other wake names a
    claim first, and a claim ref is never a finding id."""
    refs = [r for r in (ctx.wake_refs or ()) if isinstance(r, str)]
    if len(refs) < 2:
        return None
    return ctx.conn.execute(
        "SELECT id, batch_id, constraint_id FROM findings WHERE id = ? "
        "AND batch_id = ?", (refs[1], refs[0])).fetchone()


def _not_a_citation(ctx: Ctx, citation: str, verdict: str) -> str:
    """
    Why a citation is refused, naming the fact.

    tipsAI (2026-09-10): the Critic read main.py, then cited the claim's
    own id, `items:how_it_works`, fourteen sessions running, and the
    refusal said "code.source it first" about a file it had opened. The
    citation is the path of a file opened this session. Say so, and say
    which files those are.
    """
    opened = sorted(ctx.opened or ())
    if ":" in citation and "/" not in citation and "." not in citation.split(":")[0]:
        what = (f"{citation!r} is the claim's id, not a file. ")
    else:
        what = f"{citation!r} was not opened this session. "
    where = (f"You opened: {', '.join(opened)}. Cite one of those paths"
             if opened else "You opened nothing. code.source a file first")
    return (f"{what}An {verdict} stands on a line you read: citation= the "
            f"path of the file the quote is from. {where}.")


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
        raise ValueError(_not_a_citation(ctx, citation, "uphold"))
    ctx.writes.append(("challenges", f"{table}:{row}", {
        "verdict": "stands", "citation": citation,
        "quote": quote.strip()[:300], "why": (why or "").strip()[:300]}))
    out = {"id": f"{table}:{row}", "verdict": "stands"}
    # The row keeps a prefix, and until now it kept it in silence.
    cut = _cut_words(ctx, "the challenge row's", {
        "quote": (quote.strip(), 300), "why": ((why or "").strip(), 300)})
    if cut:
        out["not_shown"] = cut
    return out


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
    kept_why = (why.strip() + (f" [{flagged}]" if flagged else ""))[:460]
    ctx.writes.append(("challenges", f"{table}:{row}", {
        "verdict": "falsified", "citation": citation,
        "quote": (quote or "").strip()[:300],
        "why": kept_why}))
    ctx.writes.append(("ledger", _challenge_ledger_id(table, row), {
        "about_ref": f"{table}:{row}", "about_table": table,
        "default_taken": (f"the Critic falsified {table}:{row} against "
                          f"{citation}: \"{quote.strip()[:160]}\" -- "
                          f"{kept_why}. The claim stands in the "
                          f"record until ruled."),
        "author": "critic"}))
    out = {"id": f"{table}:{row}", "verdict": "falsified",
           "note": "recorded, and on the principal's ledger"}
    # The seat's notice covers the seat's own row. The ledger row keeps the
    # quote at 160 characters and the why whole, as the challenge row keeps it.
    # The principal rules from the why. The Critic writes the claim first and
    # the finding second, so a 160-character why lost the finding (frame 59,
    # night 88: 4 of 8 falsified ledger rows). The quote cut is recorded and
    # carries no notice. The row is the principal's, and the Critic has no call
    # that changes it.
    cut = _cut_words(ctx, "the challenge row's", {
        "quote": (quote.strip(), 300),
        "why": ((why.strip() + (f" [{flagged}]" if flagged else "")), 460)})
    _cut(ctx, "the principal's ledger row, from this verdict's quote",
         160, len(quote.strip()), "characters")
    if cut:
        out["not_shown"] = cut
    return out


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
        raise ValueError("vacuity is still a reading's verdict: call "
                         "challenge.load first. It shows the claim and opens "
                         "the files it cites")
    kept_why = why.strip()[:300]
    ctx.writes.append(("challenges", f"{table}:{row}", {
        "verdict": "unfounded", "why": kept_why}))
    # The ledger row keeps the whole why, and the challenge row keeps 300.
    # The principal rules from the why. The Critic writes the claim first and
    # the finding second, so any cap drops the finding. Night 94, s77: the
    # shared cap of 300 cut a 505-character why mid-word (frame 59).
    ctx.writes.append(("ledger", _challenge_ledger_id(table, row), {
        "about_ref": f"{table}:{row}", "about_table": table,
        "default_taken": (f"the Critic found {table}:{row} unfounded: "
                          f"{why.strip()}. An empty claim is kept in "
                          f"the record until ruled."),
        "author": "critic"}))
    out = {"id": f"{table}:{row}", "verdict": "unfounded",
           "note": "recorded, and on the principal's ledger"}
    cut = _cut_words(ctx, "the challenge row's", {"why": (why.strip(), 300)})
    if cut:
        out["not_shown"] = cut
    return out


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
        "SELECT f.id, f.kind, p.provenance, f.reason "
        "FROM frame_rulings f JOIN frame_provenance p ON p.id = f.id "
        "ORDER BY f.id"))


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
        "SELECT provenance FROM frame_provenance WHERE id = ?", (path,)).fetchone()
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
                       {"kind": k, "reason": reason or ""}))
    # The judgement rests on the tree it read: the first indexed grain under
    # the prefix, as `_derive_frame_record` cites it.
    stage_ref(ctx, "frame_rulings", path, "grain", min(covered))
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
    # Recorded, and no notice. A candidate list the seat picks one name from is
    # the case section 2.7's count is for: a reader can ask how often the index
    # was wider than the twenty rows a wake showed, and a sentence on every such
    # result would cost a page for something no seat can act on.
    if not words:
        _cut(ctx, "the candidate symbols", 20, len(rows), "rows", stored=False)
        return rows[:20]
    hits = []
    for r in rows:
        stem = r["grain"].split("::")[-1]
        split = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", stem)
        tokens = {t for t in re.findall(r"[a-z]+", split.lower()) if len(t) >= 3}
        tokens |= {t.rstrip("s") for t in tokens}
        if tokens & words:
            hits.append(r)
    _cut(ctx, "the symbols matching the hint", 40, len(hits), "rows", stored=False)
    if not hits:
        _cut(ctx, "the candidate symbols", 20, len(rows), "rows", stored=False)
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
    # Where the definitions are, so a long file is read at the right
    # place. clickI night 11 (2026-09-11): the Developer paged termui.py
    # four hundred lines at a time looking for `confirm`, read the same
    # windows twice, and ran out of turns without a write.
    if path.endswith(".py") and len(lines) > end - start:
        import ast as _ast
        try:
            tree = _ast.parse(chr(10).join(lines))
            out["defs"] = {n.name: [n.lineno - 1, getattr(n, "end_lineno", n.lineno)]
                           for n in tree.body
                           if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef))}
            out["note"] = ((note + " ") if note else "") + (
                "defs maps each top-level name to its [start, end) lines; "
                "read the one you need with those numbers")
            note = out["note"]
        except SyntaxError:
            pass
    if note:
        out["note"] = note
    return out


def _batch_base(ctx, tree) -> str:
    """The commit a batch worktree forked from, or HEAD~1 with no root."""
    from ..core import worktrees as _wt
    try:
        root = _wt.project_root(ctx.conn)
    except _wt.WorktreeError:
        root = None
    return _wt.base(tree, root)


def _removed_lines(diff_text: str, cap: int = 2000) -> str:
    """
    The removed lines that no added line of the same file carries, as text.

    Frame 97. Night 98's s183 lost 13 lines to an earlier commit, and no
    later session saw the loss inside a long diff. The comparison keeps the
    indentation, because a dedent changes what a Python line means. Each
    added line matches one removed line only, so a line removed twice and
    added once still lists once.

    The result is text with a line break, and never a dict. The runner puts
    every short value on one head line before the `[diff]` block. A dict of
    fifteen deleted files made a 45,415-character head line, and the cut at
    20,000 characters then showed no diff (the diff review of 4876aae). The
    text stops at `cap` characters across all files.
    """
    from collections import Counter

    minus: dict[str, list[str]] = {}
    plus: dict[str, Counter] = {}
    path, old_path, in_hunk = None, None, False
    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            path, old_path, in_hunk = None, None, False
            continue
        if not in_hunk:
            # The file's name comes from its own header lines. A path that
            # holds " b/" broke a split of the `diff --git` line. Git ends a
            # header path that holds a space with a tab.
            if line.startswith("--- a/"):
                old_path = line[6:].rstrip(chr(9))
            elif line.startswith("+++ b/"):
                path = line[6:].rstrip(chr(9))
            elif line.startswith("+++ /dev/null"):
                path = old_path
            elif line.startswith("@@") and path:
                in_hunk = True
            continue
        if line.startswith("-") and line[1:].strip():
            minus.setdefault(path, []).append(line[1:].rstrip())
        elif line.startswith("+") and line[1:].strip():
            plus.setdefault(path, Counter())[line[1:].rstrip()] += 1
    entries: list[tuple[str, str]] = []
    for f, lines in minus.items():
        left = plus.get(f, Counter())
        for text in lines:
            if left[text] > 0:
                left[text] -= 1
            else:
                entries.append((f, text))
    if not entries:
        return ""
    out: list[str] = []
    size, shown, current = 0, 0, None
    for f, text in entries:
        head = [f + ":"] if f != current else []
        entry = "- " + text
        cost = sum(len(a) + 1 for a in head) + len(entry) + 1
        if size + cost > cap:
            if not shown:
                # A tail alone names no file. The review of a6bed3b: one long
                # first line made the whole text "... and 1 more lines".
                room = cap - size - sum(len(a) + 1 for a in head) - 1
                out.extend(head)
                out.append(entry[:max(room, 2)])
                shown = 1
            break
        out.extend(head)
        out.append(entry)
        size += cost
        shown += 1
        current = f
    left = len(entries) - shown
    if left:
        out.append(f"... and {left} more {'line' if left == 1 else 'lines'}")
    return chr(10).join(out)


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
        # The batch's fork, not HEAD~1. Frame 97, night 100 (2026-09-30):
        # a commit and its undo left the tree equal to HEAD~1, and three
        # Developer sessions read an empty diff.
        out = subprocess.run(
            [*GIT, "-C", row["worktree"], "diff", _batch_base(ctx, row["worktree"]),
             "--unified=3"],
            capture_output=True, text=True, timeout=30)
        # The removed lines go in before the diff. The runner writes body
        # blocks in key order, and a long diff cut the block after it
        # (the review of a6bed3b: offset 62,479, cut at 6000 and 20000).
        result = {"batch": bid}
        removed = _removed_lines(out.stdout)
        if removed:
            result["removed lines"] = removed
        result["diff"] = out.stdout[:20000]
        # Silent until now, and pushed to the wake a seat uses to restore what
        # its diff broke (frame 46's design record, section 2.7). A seat reading
        # 20,000 characters of a longer diff cannot tell which files it is not
        # being shown, and the cap is not moved by this line.
        # The sentence names no call, because two modes that grant `code.diff`
        # grant no reader of a file: `architect/escalate.tools` and
        # `architect/exhausted.tools` (the diff review of 0cc624b, finding 5).
        # A cut that names a call the mode lacks is the fault this line set out
        # to remove, and `code.diff` has no narrower argument than a batch.
        cut = _cut(ctx, "this batch's diff", 20000, len(out.stdout), "characters",
                   "Nothing returns the rest of a diff this size. Work from the "
                   "part above.", stored=False)
        if cut:
            result["not_shown"] = cut
        # The diff above is the fork against the working tree, so it shows an
        # edit that no commit holds as if it were committed. Night 62
        # (2026-09-14, finding 68): a Developer session ended at the cap
        # with confirm() written and nothing committed. The next session
        # needs the fact, not the diff alone.
        dirty = _uncommitted(ctx, row["worktree"], bid)
        if dirty:
            result["not committed"] = dirty
            result["lands with"] = "code.commit"
        # An empty diff with no word reads as a diff that failed to load.
        # Frame 106 (2026-10-01): an Architect read the empty diff of a batch
        # with no edit and answered the Developer three times.
        # `code.read` says the same fact in its own note.
        elif not out.stdout and out.returncode == 0:
            result["note"] = ("this batch has no change since its fork: "
                              "no commit and no uncommitted edit")
        # The definitions the batch changed that no criterion names, read
        # from the worktree against the project's own file. Click night 48
        # (2026-09-14): the diff was in front of the Developer and it
        # called 19 red project tests unrelated; the fact is one line.
        from pathlib import Path as _Path
        root = ctx.conn.execute(
            "SELECT value FROM config WHERE key = 'project_root'").fetchone()
        changed: dict[str, list[str]] = {}
        if root and root[0]:
            for line in out.stdout.splitlines():
                if not line.startswith("+++ b/") or not line.endswith(".py"):
                    continue
                rel = line[6:]
                base_file, head_file = _Path(root[0]) / rel, _Path(row["worktree"]) / rel
                if not (base_file.exists() and head_file.exists()):
                    continue
                names = _changed_unnamed_defs(
                    ctx, rel, base_file.read_text(encoding="utf-8", errors="replace"),
                    head_file.read_text(encoding="utf-8", errors="replace"))
                if names:
                    changed[rel] = names
        if changed:
            result["definitions this batch changed that no criterion names"] = changed
            result["what that means"] = ("the project's tests call these as they were; "
                                         "restore them and add only what the criteria name")
        return result
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


def _criteria_texts(ctx) -> list[str]:
    """The criteria of this session's batch, as text, for the fence."""
    if not ctx.batch_id:
        return []
    return [r["text"] or "" for r in ctx.conn.execute(
        "SELECT c.text FROM criteria c "
        "JOIN batch_tickets bt ON bt.ticket_id = c.ticket_id "
        "WHERE bt.batch_id = ?", (ctx.batch_id,)).fetchall()]


def _batch_worktree(ctx) -> "Path":
    """
    The batch's worktree for a write or a commit, and nothing else.

    `_worktree_of` falls back to the project root, which is right for a
    read and wrong for a write: with the worktree missing, the Developer
    wrote and committed on the sample repository's master, six commits,
    and the harness said "no worktree at None" (tipsP, 2026-09-09).
    """
    from pathlib import Path as _P

    row = ctx.conn.execute(
        "SELECT worktree FROM batches WHERE id = ?", (ctx.batch_id,)).fetchone()
    if not (row and row["worktree"]):
        note = ctx.conn.execute(
            "SELECT value FROM config WHERE key = ?",
            (f"worktree:{ctx.batch_id}",)).fetchone()
        why = f" ({note['value']})" if note else ""
        raise ValueError(
            f"batch {ctx.batch_id} has no worktree{why}. Code is written and "
            f"committed in a batch's worktree and nowhere else. Nothing can "
            f"be written until the batch has one; say so and end")
    return _P(row["worktree"])


def _uncommitted(ctx, root, batch_id=None) -> list[str]:
    """The files that differ between HEAD and the working tree, the batch's
    materialised test files excluded: the harness writes those at run time
    and the Developer's commits leave them out, so they are furniture."""
    from ..core import worktrees as _wt
    bid = batch_id or ctx.batch_id
    furniture = {_grain_path(r[0]) for r in ctx.conn.execute(
        "SELECT path FROM tests WHERE batch_id = ?", (bid,))} if bid else set()
    return [f for f in _wt.changed_since(root, _wt.head(root))
            if _grain_path(f) not in furniture]


def _unchanged_note(ctx, root, path, dirty) -> str:
    """
    What a write that changes nothing tells the seat: the commit that holds
    the text, and the assertion of a test that fails on that commit.

    Frame 93. Night 97 (2026-09-29): two seats sent the landed text of
    `confirm` again, and each read only `"written, not committed": []`.
    The harness output of the red run is in `test_runs`, so the sentence
    quotes the failing line and the error pytest printed for it.
    """
    from ..core import worktrees as _wt
    said = f"{path} already holds this text, so this write changed nothing."
    if _grain_path(path) in {_grain_path(f) for f in dirty}:
        return f"{said} No commit holds it yet. code.commit records it."
    sha = _wt.head(root) or ""
    if not sha:
        return said
    short = sha[:8]
    # The latest attempt on this commit, in the order the harness ran it.
    # Frame 93's review (2026-09-30): `rowid DESC` named the last test run.
    rows = ctx.conn.execute(
        "SELECT test_id, commit_sha, output, attempt FROM test_runs "
        "WHERE batch_id = ? AND result != 'pass' "
        "ORDER BY attempt DESC, rowid ASC", (ctx.batch_id,)).fetchall()
    # A run records the sha the harness read. Either form may be short.
    rows = [r for r in rows
            if r[1] and (sha.startswith(r[1]) or r[1].startswith(sha))]
    rows = [r for r in rows if r[3] == rows[0][3]] if rows else []
    red = list(dict.fromkeys(r[0] for r in rows))

    def _cut(s):
        # A long assert made a sentence of 1915 characters (the same review).
        return s if len(s) <= 200 else s[:197] + "..."

    for test_id, _sha, output, _attempt in rows:
        lines = (output or "").splitlines()
        # pytest marks the failing source line with `>` and its error with
        # `E` below it. The last `>` is the frame that raised.
        marks = [i for i, x in enumerate(lines) if x.startswith(">")]
        err = [x[1:].strip() for x in lines[marks[-1]:] if x.startswith("E ")] if marks else []
        if err:
            src = lines[marks[-1]][1:].strip()
            more = (f", and {len(red) - 1} more fail; tests.load lists them"
                    if len(red) > 1 else "")
            return (f"{said} Commit {short} holds it. {test_id} fails at {short} on "
                    f"`{_cut(src)}`, and pytest said `{_cut(err[0])}`{more}. Read what "
                    f"this assertion needs before the next write.")
    return (f"{said} Commit {short} holds it. tests.load shows what the harness "
            f"said about each failing test.")


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
    g = grain.split("::", 1)[0].replace("\\", "/").strip()
    # Prefixes, not a character set: `lstrip("./")` made `.github/ci.py`
    # into `github/ci.py`, which no index row holds (frame 91's diff review).
    while g.startswith(("./", "/")):
        g = g[2:] if g.startswith("./") else g[1:]
    return g


def _dotted_module(path: str, keep_root: bool = False) -> str:
    """
    The module a test imports, from a surface's path.

    An installed src layout's `src/click/core.py` is `click.core`. A root
    module is its stem. With `keep_root`, `src/` and `lib/` stay in the
    name, because a project that is not installed is imported from its
    root. Frame 82's diff review: the fake repository has no build system,
    and `from billing.accounts import ...` failed at collection.
    """
    parts = path.replace("\\", "/").split("/")
    if not keep_root and parts and parts[0] in ("src", "lib") and len(parts) > 1:
        parts = parts[1:]
    dotted = ".".join(parts)[:-3] if parts and parts[-1].endswith(".py") else ".".join(parts)
    # A package's `__init__.py` is the package. `src/__init__.py` must not
    # give `from __init__ import z`.
    if dotted == "__init__":
        return ""
    return dotted.removesuffix(".__init__")


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
        # The whole batch since its fork. Frame 97: HEAD~1 hid every commit
        # but the last, and night 98's s183 lost 13 lines that way.
        fork = _batch_base(ctx, row["worktree"])
        text = worktrees.diff(row["worktree"], fork)
        # Before the diff, so a long diff's cut never reaches the block.
        removed = _removed_lines(text)
        if removed:
            out["removed lines"] = removed
        out["diff"] = text
        out["touched"] = worktrees.touched(row["worktree"], fork)
        # An empty diff with no word reads as a batch that changed nothing.
        # A fork equal to HEAD means the batch holds no commit yet.
        if fork == worktrees.head(row["worktree"]):
            out["note"] = "no commit yet on this batch"
    else:
        out["diff"] = ""
        out["note"] = "the batch has no worktree yet"
    return out


@op("code", "write")
def code_write(ctx: Ctx, path: str, text: str, start: int = 0, end: int = -1) -> dict:
    """
    Write one file in this batch's worktree: whole, or the span
    `code.source` showed.

    `start` and `end` are the numbers the Developer copies from
    `code.source`. tipsAI (2026-09-10): the whole file arrived with
    `start=0, end=-1` and was refused for the two extra arguments. The
    whole file is `start=0, end=-1`. Any other span replaces those lines
    with `text` (clickI night 16, 2026-09-12: a long module does not fit
    one reply, and the whole-file write was cut at the output cap).

    A line span, never a patch. A patch that does not apply is a failure
    the model must be told about and re-derive from, and small models are
    far worse at producing a valid hunk than a correct file or a correct
    span of one. The diff is computed by git afterwards.

    Not staged through `ctx.writes`: the filesystem is outside the transaction,
    which is the carve-out law 4 already makes for the codebase. A session that
    writes and then dies leaves the worktree ahead of the database, and boot
    reconciles the two.
    """
    return _code_write(ctx, path, text, start, end, dry=False)


def _admits(ctx: Ctx, path: str, text: str, start: int, end: int) -> bool:
    """Whether the doors of `code.write` admit this exact call.

    A refusal names a call only when this returns True. Frame 135's rule:
    a refusal states one fact and one step, and the step is a call the door
    then admits (frame 136). The dry run writes nothing and offers nothing,
    so a refusal built inside it starts no second dry run.
    """
    try:
        _code_write(ctx, path, text, start, end, dry=True)
    except Exception:                                      # noqa: BLE001
        # A call the doors refuse, or one they cannot judge, is not named.
        return False
    return True


def _code_write(ctx: Ctx, path: str, text: str, start: int, end: int, *,
                dry: bool) -> dict:
    """The doors and the write of `code.write`. With `dry`, the doors run
    and the function returns before it changes the disk (frame 136)."""
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
    target = _within(_batch_worktree(ctx), path)
    # A parameter's own name where its value goes is a placeholder. tipsBG
    # (2026-09-14): `code.write(path=path, ...)` made a file called `path`,
    # the stray check raised it, and the Architect could not judge it.
    if path.strip().lower() in ("path", "file", "filename", "text", "..."):
        raise ValueError(
            f"{path!r} is the name of the argument, not a file. Send the file's "
            f"path, the one code.source shows")
    # Only start=0, end=-1 is the whole file. Frame 94 (2026-09-30):
    # start=0, end=0 was read as whole, so an import or a docstring sent
    # to the top replaced the file. The drops refusal offers that span as
    # an insert before the first line.
    span = (start, end) != (0, -1) and end is not None
    # Frame 94's diff review of 44e156a (2026-09-30): a start with no end
    # went to the whole-file path, and the fragment became the file.
    if end is None and start != 0:
        raise ValueError(
            f"start={start} came with no end. Send end=-1 for the whole file, "
            f"or the end of the span")

    # An empty write is a removal of a file this batch added, and nothing
    # else. tipsBG (2026-09-14): told to take a mistake out, the Developer
    # wrote the file empty; an empty module is still a module, and the
    # stray stayed. A file the tree had before the batch is not removed
    # this way: change it, or say why it should go. Frame 94 (2026-09-30):
    # an empty span removed a whole file. An empty span removes its lines.
    def _empty_write():
        in_tree = ctx.conn.execute(
            "SELECT 1 FROM code_index WHERE grain = ? AND grain_kind = 'path'",
            (path.replace("\\", "/"),)).fetchone()
        if target.exists() and not in_tree:
            if dry:
                return {}       # admitted; a dry run removes nothing
            target.unlink()
            return {"removed": path, "note": "the file this batch added is gone; "
                                             "commit to record it"}
        raise ValueError(
            f"an empty write to {path} changes nothing the tree can use. To take "
            f"out a file this batch added, an empty write removes it; a file "
            f"the tree had before the batch stays, and what it should hold is "
            f"the change to send")

    if not span and not text.strip():
        return _empty_write()
    tail_note = None
    repair_note = None
    future_door = None
    if span:
        # A span, the lines `code.source` showed, replaced by `text`. clickI
        # night 16 (2026-09-12): a 688-line module does not fit one reply,
        # the whole-file write was cut at the output cap, and the batch
        # stalled on it three sessions running. The span is the same
        # slice `code.source` returns, so the numbers copy across. The
        # doors below judge the merged file, not the fragment.
        if not target.exists():
            raise ValueError(
                f"{path} does not exist, so start={start}, end={end} names "
                f"no lines to replace. Write a new file whole, with no "
                f"start or end")
        lines = target.read_text(encoding="utf-8").splitlines()
        stop = len(lines) if end < 0 else min(end, len(lines))
        if start < 0 or start > len(lines) or stop < start:
            raise ValueError(
                f"start={start}, end={end} is not a span of {path}, which "
                f"has {len(lines)} lines")
        # A blank span that leaves only blank lines is an empty write of the
        # file. Frame 94's diff reviews of 44e156a and f986adb (2026-09-30):
        # 0..3 with "" left one newline, and 0..1 left two. An insert is
        # never an empty write, because a blank insert into an empty
        # `__init__.py` removed the file.
        if (start < stop and not text.strip()
                and not any(x.strip() for x in lines[:start] + lines[stop:])):
            return _empty_write()
        # A span replaces whole statements. clickI night 37 (2026-09-13):
        # the Developer's span ended inside a multi-line signature, the
        # merged file failed to parse at line 366, and the same write came
        # six times with the same refusal, which named the symptom and not
        # the cut. The original's statement boundaries are a fact.
        if path.endswith(".py"):
            import ast as _ast
            try:
                original = _ast.parse(chr(10).join(lines))
            except SyntaxError:
                original = None
            # At every nesting level: a span that covers whole statements
            # inside a function is a legal edit of that function. Click
            # night 52 (2026-09-14): the Developer's span inside confirm()
            # was refused three sessions running as "cuts through confirm",
            # with only the whole-function spans offered, and the loop
            # never landed a line. The refusal names the innermost
            # statement a boundary falls inside.
            # Frame 92's diff review of 6e993d0 (2026-09-29): every edit
            # inside a case body was refused as "falls inside match". A
            # match_case has no line numbers of its own, so it runs from its
            # pattern to the end of its body.
            _fields = ("body", "orelse", "finalbody", "handlers", "cases")

            def _stmts(part):
                if not isinstance(part, list):
                    return []
                return [x for x in part
                        if hasattr(x, "lineno") or isinstance(x, _ast.match_case)]

            def _children(n):
                out = []
                for field in _fields:
                    out.extend(_stmts(getattr(n, field, None)))
                return out

            def _end(n):
                if isinstance(n, _ast.match_case):
                    return _end(n.body[-1])
                return getattr(n, "end_lineno", n.lineno)

            def _lo(n):
                # A decorated def starts at its first decorator. Frame 92's
                # diff review of pass 4 (2026-09-29): a whole-def span began
                # at the def line and left the decorators above it.
                if isinstance(n, _ast.match_case):
                    # A bracketed pattern can start below its `case (` line.
                    k = n.pattern.lineno - 1
                    # `case_id,` or `case.A` on a continuation line is a
                    # name, not a case header. `case{`, `case-1` and
                    # `case"x"` are headers (frame 94's diff reviews of
                    # 44e156a and f986adb, 2026-09-30).
                    while k > 0 and not re.match(r"\s*case(?![\w.])", lines[k]):
                        k -= 1
                    return k
                decs = getattr(n, "decorator_list", None) or []
                return min([n.lineno] + [x.lineno for x in decs]) - 1

            def _gap(ns, b):
                # A boundary on a statement's edge, or on a blank or comment
                # line between two statements of one list, is whole in that
                # list. The review saw 5..5 in a def's blank lines refused.
                if any(_lo(s) == b or _end(s) == b for s in ns):
                    return True
                return any(_end(x) < b < _lo(y) for x, y in zip(ns, ns[1:]))

            def _cut(nodes, b):
                # The path of (node, lo, hi) from the top-level statement to
                # the innermost statement the boundary falls inside.
                for n in nodes:
                    lo, hi = _lo(n), _end(n)
                    if lo < b < hi:
                        kids = _children(n)
                        # One field list at a time. The review of 928b2dc
                        # (2026-09-29): body and orelse joined read a blank
                        # line before else: as aligned, and the door raised.
                        if any(_gap(_stmts(getattr(n, f, None)), b) for f in _fields):
                            return "aligned"     # on a child's boundary: whole statements
                        inner = _cut(kids, b)
                        if inner == "aligned":
                            return "aligned"
                        return [(n, lo, hi)] + (inner or [])
                return None

            def _inside(nodes, b):
                # The same path for a boundary that falls on a child's
                # boundary, so the message can say where that boundary is.
                for n in nodes:
                    lo, hi = _lo(n), _end(n)
                    if lo < b < hi:
                        return [(n, lo, hi)] + _inside(_children(n), b)
                return []

            _defs = (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef)
            _block = {"body": "body", "orelse": "else block", "cases": "cases",
                      "finalbody": "finally block", "handlers": "except blocks"}
            # The seat reads the word the source shows. The review of
            # 6e993d0 (2026-09-29) saw an elif named if and a docstring expr.
            _plain = {"excepthandler": "except block", "asyncfor": "async for",
                      "asyncwith": "async with", "trystar": "try",
                      "augassign": "assignment", "match_case": "case",
                      "annassign": "annotated assignment", "importfrom": "import",
                      "nonlocal": "nonlocal", "expr": "expression",
                      "assign": "assignment", "delete": "del statement",
                      "typealias": "type alias", "functiondef": "def",
                      "asyncfunctiondef": "async def", "classdef": "class"}
            # The review of 928b2dc (2026-09-29): any bare string was named a
            # docstring. Only the first statement of a module, def or class
            # body is one.
            _docs = set()
            for _h in ([original] + [x for x in _ast.walk(original) if isinstance(x, _defs)]
                       if original else []):
                _b0 = _h.body[0] if _h.body else None
                if (isinstance(_b0, _ast.Expr)
                        and isinstance(getattr(_b0.value, "value", None), str)):
                    _docs.add(id(_b0))

            def _what(n):
                # Only a definition is a thing to edit alone. The diff
                # review of pass 1 saw "To edit err alone" from an except
                # handler's bound name.
                if isinstance(n, _defs):
                    return n.name
                if (isinstance(n, _ast.If) and 0 < n.lineno <= len(lines)
                        and lines[n.lineno - 1].lstrip().startswith("elif")):
                    return "elif"
                if id(n) in _docs:
                    return "docstring"
                word = type(n).__name__.lower()
                return _plain.get(word, word)

            _kind = _what

            def _lists(nodes, parent, field, b, top=False):
                # Frame 92's diff review of pass 5 (2026-09-29): each
                # boundary passed alone, and a span from class C into
                # async def h removed the header of h. A span is whole only
                # when both boundaries sit in one field list of one parent.
                # This gives each (parent, field, statements) list that b
                # sits in, the outermost first. The top level also takes
                # the lines between statements.
                out = []
                if (_gap(nodes, b)
                        or (top and not any(_lo(s) < b < _end(s) for s in nodes))):
                    out.append((parent, field, nodes))
                for s in nodes:
                    if _lo(s) < b <= _end(s):
                        for f in _fields:
                            kids = _stmts(getattr(s, f, None))
                            if kids:
                                out.extend(_lists(kids, s, f, b))
                return out

            def _at(b):
                return _lists(tops, None, "body", b, True)

            def _bounds(ns):
                return {_lo(s) for s in ns} | {_end(s) for s in ns}

            # The review of 6e993d0 (2026-09-29): the innermost list first
            # moved a start past def n when the outer list had def n's own
            # line. The nearest boundary over all lists wins. On a tie the
            # outermost list wins, because its span keeps the header.
            def _moved_end(a, b):
                # The last boundary at or before b in a list that a sits in.
                best = None
                for p, f, ns in _at(a):
                    ok = [x for x in _bounds(ns) if a < x <= b]
                    if ok and (best is None or max(ok) > best[3]):
                        best = (p, f, ns, max(ok))
                return best

            def _moved_start(a, b):
                # The first boundary at or after a in a list that b sits in.
                best = None
                for p, f, ns in _at(b):
                    ok = [x for x in _bounds(ns) if a <= x < b]
                    if ok and (best is None or min(ok) < best[3]):
                        best = (p, f, ns, min(ok))
                return best

            def _end_offer(m):
                p, f, ns, x = m
                if p is not None and ns and x == _end(ns[-1]):
                    if x == _end(p) and isinstance(p, _defs):
                        return f"To edit {p.name} alone send end={x}, which is where {p.name} ends."
                    if x == _end(p):
                        return f"To stop where {_what(p)} ends send end={x}."
                    return f"To stop where the {_block[f]} of {_what(p)} ends send end={x}."
                nxt = [s for s in ns if _lo(s) == x]
                if nxt:
                    return f"To stop before {_what(nxt[0])} send end={x}."
                prev = [s for s in ns if _end(s) == x]
                if prev:
                    return f"To stop after {_what(prev[-1])} send end={x}."
                return f"To stop there send end={x}."

            def _start_offer(m):
                p, f, ns, x = m
                if p is not None and ns and x == _lo(ns[0]):
                    what, b0 = _what(p), ns[0]
                    out = (f"To edit inside {what} send start={x}, "
                           f"which is where the {_block[f]} of {what} starts.")
                    if (isinstance(p, _defs) and f == "body" and isinstance(b0, _ast.Expr)
                            and isinstance(getattr(b0.value, "value", None), str)):
                        out += " Your text replaces the docstring too."
                    return out
                prev = [s for s in ns if _end(s) == x]
                if prev:
                    return f"To start after {_what(prev[-1])} send start={x}."
                nxt = [s for s in ns if _lo(s) == x]
                if nxt:
                    return f"To start before {_what(nxt[0])} send start={x}."
                return f"To start there send start={x}."

            def _whole_parent(b):
                # The statement that holds the list b sits in, whole.
                for p, f, ns in reversed(_at(b)):
                    if p is not None:
                        return (f"To replace {_what(p)} whole send "
                                f"start={_lo(p)}, end={_end(p)}.")
                return None

            tops = original.body if original else []
            cuts = {b: _cut(tops, b) for b in (start, stop)}
            if any(isinstance(c, list) for c in cuts.values()):
                # Click night 96 (2026-09-29): s241 sent both boundaries one
                # line late. The refusal named only get_pager_file and its
                # exits, and the seat was editing confirm. The seat needs
                # the file's own lines at its boundaries, which code.source
                # does not number (observed: turns of s241).
                at_start = isinstance(cuts[start], list)
                path = cuts[start] if at_start else cuts[stop]
                label = f"start={start}" if at_start else f"end={end}"
                other = _inside(tops, stop if at_start else start)
                one_def = bool(other) and other[0][0] is path[0][0]
                top, inner = path[0], path[-1]
                # Night 52's loop came from offering the whole function
                # for an edit inside it, so one definition names the
                # innermost statement.
                named = inner if one_def or not getattr(top[0], "name", None) else top
                name, lo, hi = _kind(named[0]), named[1], named[2]
                # One fact per sentence: the refusal is read by a small model.
                parts = [f"start={start}, end={end}: {label} falls inside {name} "
                         f"(lines {lo} to {hi} in code.source numbering)."]
                if named is not inner:
                    parent = path[-2][0]
                    first = getattr(parent, "body", [None])[0]
                    doc = (inner[0] is first and isinstance(inner[0], _ast.Expr)
                           and isinstance(getattr(inner[0].value, "value", None), str))
                    parts.append(f"{label} is in its {'docstring' if doc else _kind(inner[0])} "
                                 f"at lines {inner[1]} to {inner[2]}.")
                # Frame 92's diff review of pass 5 (2026-09-29): a start on
                # the def line of a decorated def was refused with no word
                # about the decorators above it.
                cut_b = start if at_start else stop
                for n, nlo, _hi in path:
                    if getattr(n, "decorator_list", None) and nlo < cut_b < n.lineno:
                        where = "below" if cut_b == n.lineno - 1 else "inside"
                        parts.append(f"{label} is {where} the decorators of {_what(n)}, "
                                     f"which start at line {nlo}.")
                o_cut = cuts[stop if at_start else start]
                if other and not one_def:
                    o_label = f"end={end}" if at_start else f"start={start}"
                    verb = "also falls inside" if isinstance(o_cut, list) else "is inside"
                    on, olo, ohi = other[0]
                    parts.append(f"{o_label} {verb} {_kind(on)} (lines {olo} to {ohi}).")
                for i in sorted({start, stop - 1, stop}):
                    if 0 <= i < len(lines):
                        parts.append(f"Line {i} is '{lines[i].rstrip()[:60]}'.")
                body = text.splitlines()

                def _near(want, at):
                    # A fact, not a guess: the text's line is in the file
                    # within three lines of the boundary.
                    if not want.strip():
                        return None
                    if 0 <= at < len(lines) and lines[at].rstrip() == want.rstrip():
                        return None
                    for k in sorted(range(at - 3, at + 4), key=lambda k: (abs(k - at), k)):
                        if 0 <= k < len(lines) and lines[k].rstrip() == want.rstrip():
                            return k
                    return None

                if body:
                    k = _near(body[0], start)
                    if k is not None:
                        parts.append(f"Your text's first line is line {k} of the file, "
                                     f"so a span that replaces it starts at start={k}.")
                    k = _near(body[-1], stop - 1)
                    if k is not None:
                        parts.append(f"Your text's last line is line {k} of the file, "
                                     f"so a span that replaces it ends at end={k + 1}.")
                # Click night 97 (2026-09-29): s215 and s217 got a moved
                # start from the end of confirm, and the span cut the def
                # the end sat in. A moved boundary helps only when the other
                # boundary is whole, and it lands in the other boundary's
                # own list. A block header such as else: or finally: has no
                # node, so a list edge never takes one in (observed: turns
                # of s215 and s217, the probes of pass 5's review).
                if start < stop and not isinstance(o_cut, list):
                    m = _moved_start(start, stop) if at_start else _moved_end(start, stop)
                    if m:
                        parts.append(_start_offer(m) if at_start else _end_offer(m))
                    else:
                        w = _whole_parent(stop if at_start else start)
                        if w:
                            parts.append(w)
                if start == stop:
                    parts.append("An insert goes between whole statements.")
                    parts.append(f"To add after {name} send start={hi}, end={hi}.")
                else:
                    parts.append(f"To replace {name} whole send start={lo}, end={hi}.")
                    parts.append(f"To add after it send start={hi}, end={hi}.")
                raise ValueError(" ".join(parts))
            # Frame 94's diff review of 44e156a (2026-09-30): an insert at
            # 0..0 landed above `from __future__ import`. ast.parse took it,
            # compile refused it, and every test failed at import. The drops
            # refusal sends the seat to 0..0 for an import. Any insert at or
            # before the last leading `__future__` import breaks the same way,
            # and the docstring door offers the line after a docstring.
            # Ruled: frame 94's coordinator (2026-09-30). A text of only
            # `__future__` imports passes, and so does a text of no
            # statements, such as comments.
            def _future_door(src):
                futs = []
                for i, s in enumerate(tops):
                    if i == 0 and id(s) in _docs:
                        continue
                    if not (isinstance(s, _ast.ImportFrom) and s.module == "__future__"):
                        break
                    futs.append(s)
                try:
                    own = _ast.parse(src).body
                except SyntaxError:
                    # The parse door below names a text that does not parse.
                    own = None
                own_fut = own is None or all(
                    isinstance(s, _ast.ImportFrom) and s.module == "__future__" for s in own)
                if futs and start <= _lo(futs[-1]) and not own_fut:
                    after = _end(futs[-1])
                    raise ValueError(
                        f"start={start}, end={end}: Python refuses any statement "
                        f"above the `from __future__` import at line {_lo(futs[-1])}. "
                        f"To add after it send start={after}, end={after}.")
                return own

            if start == stop:
                own = _future_door(text)
                # The parse door repairs a broken string, and the repaired
                # text meets this door again (the review of edd3638, point 8).
                future_door = _future_door
            # The review of 6e993d0 (2026-09-29): an insert on a docstring's
            # first line passed and turned the docstring into an expression.
            # A refusal here is smaller than a note in the write's result.
            # A text with no statements, such as a comment, leaves the
            # docstring a docstring (frame 94's second diff review,
            # 2026-09-30). `own` comes from the `__future__` door above. It
            # is None for a text that does not parse alone, such as the
            # indented lines of an insert inside a def, and that insert is
            # judged here (frame 94's last review asked to exempt it, and
            # `test_the_refusal_names_statements_with_the_words_of_the_source`
            # shows why not).
            if start == stop and own != []:
                for p, f, ns in _at(start):
                    # The module's own docstring counts too (review of 928b2dc).
                    if (f == "body" and ns and _lo(ns[0]) == start
                            and id(ns[0]) in _docs):
                        after = _end(ns[0])
                        owner = "the module" if p is None else p.name
                        raise ValueError(
                            f"start={start}, end={end}: line {start} is the docstring "
                            f"of {owner}. Your text goes before it. Then the docstring "
                            f"is no longer a docstring. To add after the docstring "
                            f"send start={after}, end={after}.")
            sl, el = _at(start), _at(stop)
            if start < stop and not any(a[0] is b[0] and a[1] == b[1] for a in sl for b in el):
                # Frame 92's diff review of pass 5 (2026-09-29): both
                # boundaries were whole, and the span still removed the
                # header of async def h or ended on a finally: header.
                def _where(x):
                    p, f = x[0], x[1]
                    return ("the top level of the file" if p is None
                            else f"the {_block[f]} of {_what(p)}")

                parts = [f"start={start}, end={end} crosses from one block to another.",
                         f"start={start} is in {_where(sl[-1]) if sl else 'no block'}.",
                         f"end={end} is in {_where(el[-1]) if el else 'no block'}.",
                         "A span replaces whole statements of one block."]
                for i in sorted({start, stop - 1, stop}):
                    if 0 <= i < len(lines):
                        parts.append(f"Line {i} is '{lines[i].rstrip()[:60]}'.")
                m = _moved_end(start, stop)
                if m:
                    parts.append(_end_offer(m))
                m = _moved_start(start, stop)
                if m:
                    parts.append(_start_offer(m))
                # The innermost statement that holds the whole span. A
                # boundary on a statement's last line is still in that
                # statement. Frame 92 pass 7 (2026-09-29): night46's try
                # tail ended where the try ends and was offered the while.
                n, level = None, tops
                while True:
                    hit = [s for s in level if _lo(s) <= start and stop <= _end(s)]
                    if not hit:
                        break
                    n, level = hit[0], _children(hit[0])
                if n is not None:
                    parts.append(f"To replace {_what(n)} whole send "
                                 f"start={_lo(n)}, end={_end(n)}.")
                else:
                    ps, pe = _inside(tops, start), _inside(tops, stop)
                    a = ps[0][1] if ps else start
                    b = pe[0][2] if pe else stop
                    parts.append(f"To replace the whole top-level statements "
                                 f"send start={a}, end={b}.")
                raise ValueError(" ".join(parts))
        nl = chr(10)
        fragment = text
        # A blank text, "" or a lone newline, replaces the span with no lines.
        new = text.splitlines() if text.strip() else []
        text = nl.join(lines[:start] + new + lines[stop:]) + nl
        # Frame 95: a text that stops short still parses. The result names
        # the lines the write drops, and the write lands.
        if path.endswith(".py"):
            try:
                tail_note = _tail_drop(lines, start, stop, fragment)
            except Exception:
                tail_note = None    # a note never refuses a write
    from ..core import fence as _fence
    _fence.check_manifest(path, _criteria_texts(ctx))
    # A file at the root named like a standard-library module shadows it
    # for every import in the project. clickI (2026-09-10): the Developer
    # wrote `__future__.py` in the worktree root and every test of the
    # repository failed at import, twelve attempts running.
    import sys as _sys
    from pathlib import Path as _SP
    _sp = _SP(path)
    # A src layout keeps its modules in the package. clickI (2026-09-11):
    # the Developer wrote main.py at the root of a library whose package
    # lives in src/click, and the tests could not import it as a module of
    # the project. A fact about the tree: a package under src/ exists, and
    # no criterion names a root path.
    _root = _batch_worktree(ctx)
    _pkgs = sorted(d.name for d in (_root / "src").iterdir()
                   if (d / "__init__.py").is_file()) if (_root / "src").is_dir() else []
    def _root_importable(root) -> bool:
        # A root module is importable by the tests when the project is not
        # an installed package: pytest prepends the test file's directory,
        # and a root conftest or `pythonpath = ["."]` does the rest. An
        # installed src-layout package, one with a build system, is
        # imported from the package and a root module is outside it.
        from ..core.provision import project_installable
        return not project_installable(root)
    if (_sp.suffix == ".py" and len(_sp.parts) == 1 and _pkgs
            and not _sp.stem.startswith("test") and not _root_importable(_root)):
        named_roots = {r.split("::")[0] for c in ctx.conn.execute(
            "SELECT c.surface_refs FROM criteria c JOIN batch_tickets bt "
            "ON bt.ticket_id = c.ticket_id WHERE bt.batch_id = ?", (ctx.batch_id,))
            for r in json.loads(c["surface_refs"] or "[]") if "::" in r}
        if path not in named_roots:
            # The place suggested must be free. clickI night 12 (2026-09-11):
            # the suggestion was src/click/main.py, which exists and is the
            # package's entry point, and the rewrite was refused for that.
            bare = sorted({r for c in ctx.conn.execute(
                "SELECT c.surface_refs FROM criteria c JOIN batch_tickets bt "
                "ON bt.ticket_id = c.ticket_id WHERE bt.batch_id = ?", (ctx.batch_id,))
                for r in json.loads(c["surface_refs"] or "[]") if "::" not in r})
            where = _root / "src" / _pkgs[0] / _sp.name
            if where.exists() and bare:
                where = _root / "src" / _pkgs[0] / f"{bare[0]}.py"
            raise ValueError(
                f"{path} is a new module at the project root, and the project's "
                f"package lives in src/{_pkgs[0]}. A module the tests import as "
                f"part of the project goes there, in a file of its own: "
                f"{where.relative_to(_root).as_posix()}")
    if (_sp.suffix == ".py" and len(_sp.parts) == 1
            and _sp.stem in getattr(_sys, "stdlib_module_names", ())):
        raise ValueError(
            f"{path} at the project root has the name of the standard-library "
            f"module {_sp.stem!r}, and every `import {_sp.stem}` in the project "
            f"would load this file instead. Put the code in the module the "
            f"criteria name, or under another name")
    # A harness fact about modules, not a judgement about the code. S0 walk
    # ten: `script.py` was right in substance and ran `input()` at module
    # level, so every test that imported it died at collection -- OSError,
    # stdin is captured -- and the Developer escalated three times against
    # an error that names the line. Under pytest a module the tests import
    # runs at import; the shape that works is the main guard.
    if path.endswith(".py"):
        import ast as _ast
        if not span:
            fragment = text                 # a whole-file write sends the file

        def _parse_compile(src: str):
            stage = "parse"
            try:
                tree = _ast.parse(src)
                # compile refuses some files that ast.parse takes. Frame 94's
                # second diff review (2026-09-30): a `from __future__` import
                # after another statement landed, and the file failed at import.
                # dont_inherit keeps this module's own future flags out.
                stage = "compile"
                # compile warns where ast.parse does not, and a run with warnings
                # as errors would refuse a valid file (frame 94's last review).
                import warnings as _warnings
                with _warnings.catch_warnings():
                    _warnings.simplefilter("ignore")
                    compile(src, path, "exec", dont_inherit=True)
                return tree, None
            except SyntaxError as exc:
                return None, (stage, exc)

        tree, fail = _parse_compile(text)
        # The call decoder reads the two characters \n as one line break.
        # Night 99 (2026-09-30): s134's `out += "\n"` reached the door as
        # two lines, and three sessions were refused at attempt 3.
        if fail is not None and fail[0] == "parse":
            fixed, joined, crlf = _repair_broken_strings(fragment)
            if joined:
                if future_door is not None:
                    future_door(fixed)
                if span:
                    new = fixed.splitlines() if fixed.strip() else []
                    merged = chr(10).join(lines[:start] + new + lines[stop:]) + chr(10)
                else:
                    merged = fixed
                tree2, fail2 = _parse_compile(merged)
                if fail2 is None:
                    text, fragment, tree, fail = merged, fixed, tree2, None
                    repair_note = _repair_sentence(joined, crlf)
                    if span:
                        try:
                            tail_note = _tail_drop(lines, start, stop, fragment)
                        except Exception:                  # noqa: BLE001
                            tail_note = None    # a note never refuses a write
        if fail is not None:
            stage, exc = fail
            # Click night 120 (2026-10-05): s227 sent the whole header back
            # with `import sys` above `from __future__`, the bare refusal
            # below named no step, and the seat gave up on a repair that
            # was one line away. The step is named only when the doors
            # admit it (frame 136, law of frame 135: one fact, one step).
            order = (_future_order(fragment)
                     if stage == "compile" and "__future__" in (exc.msg or "") else None)
            if order is not None:
                moved, futs, above = order
                many = len(futs) > 1
                quoted = " and ".join(f"'{x}'" for x in futs)
                msg = (f"Python takes {quoted} only above every other statement, "
                       f"and your text puts '{above}' above {'them' if many else 'it'}.")
                if not dry and _admits(ctx, path, moved, start, end):
                    msg += (f" Send the same call with {'those lines' if many else 'that line'} "
                            f"first in text.")
                raise ValueError(msg) from None
            if stage == "compile":
                raise ValueError(
                    f"{path} is not valid Python ({exc.msg}, line "
                    f"{(exc.lineno or 1) - 1} in code.source numbering); the harness "
                    f"imports it and would die at collection.") from None
            # A span whose own lines do not parse: clickI night 40
            # (2026-09-13), the fragment ended with a dangling `def echo(`
            # copied from the file to show where it goes, and the refusal
            # named the merged file's line, not the fragment's, six times.
            frag_note = ""
            if span:
                try:
                    # An indented span parses at the top level (the review
                    # of edd3638), so the note names the real line.
                    _ast.parse(_indent_view(fragment)[0])
                except SyntaxError as fexc:
                    bad = (fragment.splitlines() + [""])[max((fexc.lineno or 1) - 1, 0)]
                    frag_note = (f" Your text itself does not parse: line {fexc.lineno} "
                                 f"of it, counting from 1, is {bad.strip()!r}. Send only the lines you add, "
                                 f"whole statements; the file's own lines stay where they are.")
                    # A fragment that begins with the tail of a compound
                    # statement. Click night 53 (2026-09-14): `except ...:`
                    # sent alone, three sessions, against a try statement
                    # the door had already located. Name the whole statement.
                    first = next((l.strip() for l in fragment.splitlines() if l.strip()), "")
                    tail_kw = next((k for k in ("except", "elif", "else", "finally")
                                    if first.startswith(k) and first.rstrip(":").split(" ")[0] == k), None)
                    if tail_kw:
                        try:
                            orig = _ast.parse(chr(10).join(lines))
                        except SyntaxError:
                            orig = None
                        holder = None
                        for n in (_ast.walk(orig) if orig else []):
                            lo, hi = getattr(n, "lineno", 0) - 1, getattr(n, "end_lineno", 0)
                            if isinstance(n, (_ast.Try, _ast.If, _ast.For, _ast.While)) and lo <= start < hi:
                                if holder is None or lo >= holder[0]:
                                    holder = (lo, hi, type(n).__name__.lower())
                        if holder:
                            lo, hi, kind = holder
                            frag_note += (f" `{tail_kw}` is the tail of the {kind} statement at lines "
                                          f"{lo} to {hi}; send that whole statement, with your "
                                          f"change in it: start={lo}, end={hi}.")
            frag_note += _escape_note(fragment, exc if not span else None)
            raise ValueError(
                f"{path} is not valid Python ({exc.msg}, line {(exc.lineno or 1) - 1} "
                f"in code.source numbering); the harness imports it and would die at "
                f"collection.{frag_note}") from None
        # One name, one definition. tipsS (2026-09-09): the Developer put a
        # second `calculate_tip(total, people)` above the tip function, the
        # later definition won, the test got the tip instead of the share,
        # and the fix loop ran to the step cap. Python keeps the last one
        # silently, which is a fact about the file.
        def _decorator_name(d) -> str:
            # `overload`, `t.overload`, `typing.overload`, `overload()`.
            if isinstance(d, _ast.Call):
                d = d.func
            if isinstance(d, _ast.Attribute):
                return d.attr
            return getattr(d, "id", "") or ""

        seen: dict[str, int] = {}
        for node in tree.body:
            if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef)):
                # A typing overload stub is a signature, not a definition.
                # clickI night 32 (2026-09-13): termui.py carries three
                # `@t.overload` stubs of `prompt` above the one body, and
                # every span write to the file was refused as a duplicate,
                # three identical sessions to quarantine.
                if any(_decorator_name(d).endswith("overload")
                       for d in getattr(node, "decorator_list", [])):
                    continue
                if node.name in seen:
                    raise ValueError(
                        f"{path} defines {node.name} twice (lines "
                        f"{seen[node.name]} and {node.lineno}). Python keeps "
                        f"the last one and the first never runs. One name, "
                        f"one definition: give the new behaviour its own "
                        f"name, or change the one definition")
                seen[node.name] = node.lineno
        # One name, one definition, across the tree too. clickI night 35
        # (2026-09-13): the Developer wrote `src/click/main.py` with its own
        # `def echo` beside `echo_json`, when `src/click/utils.py::echo` is
        # the function the ticket said "next to"; nights 32 to 34 wrote
        # `echo_json` a second time in `src/echo_json.py`. A name the index
        # holds in exactly one other module is a unique surface, and a
        # second definition of it is a copy. A name defined in several
        # modules already (`main`, `setup`) is a convention and passes;
        # tests and private names pass.
        if not _is_test_path(path):
            # A name the file defined before this write is the tree's own
            # duplicate, not this change's. tipsBF (2026-09-13): tipsI keeps
            # `calculate_tip` in main.py and tip_calculator.py both, and a
            # whole-file rewrite of main.py that kept it was refused as a
            # copy, three sessions to quarantine.
            had_before: set[str] = set()
            if target.exists():
                try:
                    had_before = {n.name for n in _ast.parse(
                        target.read_text(encoding="utf-8")).body
                        if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef))}
                except (SyntaxError, UnicodeDecodeError):
                    had_before = set()
            for node in tree.body:
                if not isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef)):
                    continue
                if node.name.startswith("_") or node.name.startswith("test") or node.name in had_before:
                    continue
                elsewhere = {
                    r["grain"].split("::", 1)[0] for r in ctx.conn.execute(
                        "SELECT grain FROM code_index WHERE grain_kind = 'symbol' "
                        "AND grain LIKE ?", (f"%::{node.name}",))
                    if r["grain"].endswith(f"::{node.name}")
                    and r["grain"].split("::", 1)[0].replace("\\", "/") != path.replace("\\", "/")
                    and not _is_test_path(r["grain"].split("::", 1)[0])}
                # The index is the tree at onboarding; the batch's own commits
                # are not in it. clickI night 42 (2026-09-13): `echo_json`
                # landed in utils.py, then a second `echo_json` in a new
                # module the index could not see. The worktree is the fact.
                elsewhere |= _defined_in_tree(ctx, node.name, path)
                elsewhere = sorted(elsewhere)
                # A criterion that names this file asked for the definition
                # here. L1-DV-build-a-clear-criterion (2026-09-14): "money(1999)
                # returns '$19.99' from src/notify/formatting.py", templates.py
                # already held a `money`, and the door sent the Developer to
                # the wrong file against the criterion's own words.
                named_here = any(path.replace("\\", "/") in (t or "").replace("\\", "/")
                                 for t in _criteria_texts(ctx))
                if len(elsewhere) == 1 and not named_here:
                    raise ValueError(
                        f"{path} defines {node.name}, and the tree already defines "
                        f"{node.name} in {elsewhere[0]}. A second definition of a "
                        f"name the project has once is a copy, and the tests and "
                        f"the callers reach the first one. Change {elsewhere[0]}, "
                        f"or give the new behaviour its own name")
        # The fence: a reach outside the project is a fact about the file,
        # and the criteria are the only thing that can ask for one.
        from ..core import fence as _fence
        # The file as it stood is the baseline: a reach it already made is
        # the project's, not this change's (night 38, utils.py line 547).
        _baseline = None
        if target.exists():
            try:
                _baseline = _ast.parse(target.read_text(encoding="utf-8"))
            except (SyntaxError, UnicodeDecodeError):
                _baseline = None
        _fence.check(path, tree, _criteria_texts(ctx), baseline=_baseline)
        # The tests are the Tester's. tipsR (2026-09-09): the Developer
        # rewrote tests/test_split_bill.py to import a module that does not
        # exist, the harness ran the database's copy of the test and passed,
        # the merge carried the Developer's file, and the merged tree's own
        # test suite was broken. A test file is not the Developer's to
        # write: the harness holds the tests from the database.
        from pathlib import Path as _TP
        _tp = _TP(path)
        if ctx.role == "developer" and (
                "tests" in _tp.parts[:-1] or _tp.name.startswith("test_")
                or _tp.name.endswith("_test.py")):
            raise ValueError(
                f"{path} is a test file, and the tests are the Tester's. The "
                f"harness runs the tests on record; a test you cannot pass "
                f"is `msg.challenge_tester`, not a rewrite")
        # An entry point keeps its main guard. tipsR (2026-09-09): main.py
        # went from the interactive program to one function with no guard,
        # nothing imported the dropped functions so the rewrite went
        # through, the Critic passed it, and the merged program printed
        # nothing. A program that ran and now does not is a fact.
        if target.is_file():
            def _guarded(t) -> bool:
                return any(isinstance(n, _ast.If) and isinstance(n.test, _ast.Compare)
                           and any(isinstance(c, _ast.Constant) and c.value == "__main__"
                                   for c in n.test.comparators) for n in t.body)
            try:
                old_tree = _ast.parse(target.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                old_tree = None
            if old_tree is not None and _guarded(old_tree) and not _guarded(tree):
                n_old = len(target.read_text(encoding="utf-8", errors="replace").splitlines())
                raise ValueError(
                    f"{path} is the program's entry point: it has an "
                    f"`if __name__ == \"__main__\":` block today and this "
                    f"write has none, so the program would stop running. "
                    f"Keep the block and the functions it calls; add your "
                    f"change to the file, do not replace it. To add new "
                    f"definitions without retyping the file, write only them "
                    f"with start={n_old}, end={n_old}: {path} has {n_old} "
                    f"lines and that span appends after them")
            # And the guard's body must still resolve. tipsT (2026-09-09):
            # the guard was kept and the three functions it calls were
            # dropped, so the program crashed at the first line.
            if old_tree is not None and _guarded(tree):
                def _defs(t) -> set[str]:
                    return {n.name for n in t.body
                            if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef,
                                              _ast.ClassDef))}
                guard = next(n for n in tree.body
                             if isinstance(n, _ast.If) and isinstance(n.test, _ast.Compare)
                             and any(isinstance(c, _ast.Constant) and c.value == "__main__"
                                     for c in n.test.comparators))
                called = {n.func.id for n in _ast.walk(guard)
                          if isinstance(n, _ast.Call) and isinstance(n.func, _ast.Name)}
                lost = sorted((called & _defs(old_tree)) - _defs(tree))
                if lost:
                    raise ValueError(
                        f"the `__main__` block of {path} calls {', '.join(lost)}, "
                        f"which the file defines today and this write drops. "
                        f"The program would crash at that line. Keep every "
                        f"definition the block calls")
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
    # The same stdin trap, from the writing side. A function that reads
    # input() internally can never satisfy a test that calls it directly and
    # asserts a fixed return value -- stdin is captured under pytest, the
    # call raises before the assertion runs, against any implementation.
    # `tests.encode` refuses this when the function already exists to
    # inspect; tests are written first in this flow, so the common case is
    # the reverse order -- the test lands before this function does, and
    # nothing caught it there.
    #
    # Points at the test, not at a reshape. The first version of this
    # offered "read the value one level up and pass it as a parameter" as
    # an alternative, reasoning that Developer could sidestep the test by
    # changing the function's shape. Measured, twice: it took that door
    # both times, parameterized the function, and the test -- unowned by
    # Developer, uneditable by it -- still called the old zero-argument
    # form. `OSError` became `TypeError`; nothing was fixed, because
    # Developer cannot edit the artefact that needed to change. A function
    # whose whole job is reading external input does not stop needing to
    # read external input because the test calling it is wrong.
    if path.endswith(".py") and ctx.batch_id:
        readers_here = {f.name for f in _ast.walk(tree)
                        if isinstance(f, (_ast.FunctionDef, _ast.AsyncFunctionDef))
                        and any(isinstance(n, _ast.Call) and isinstance(n.func, _ast.Name)
                               and n.func.id == "input" for n in _ast.walk(f))}
        if readers_here:
            for row in ctx.conn.execute(
                    "SELECT body FROM tests WHERE batch_id = ?", (ctx.batch_id,)):
                tbody = row["body"] or ""
                try:
                    ttree = _ast.parse(tbody)
                except SyntaxError:
                    continue
                tshields = _stdin_shields(ttree)
                # A patch of `builtins.input` or of a module's own `input`
                # name reaches the reader too.
                if "sys.stdin" in tshields or any(
                        t.rsplit(".", 1)[-1] == "input" for t in tshields):
                    continue
                called = {n.func.id for n in _ast.walk(ttree)
                         if isinstance(n, _ast.Call) and isinstance(n.func, _ast.Name)}
                hit = called & readers_here
                if hit:
                    fn_name = sorted(hit)[0]
                    raise ValueError(
                        f"{fn_name} reads input() internally, and a test in "
                        f"this batch calls {fn_name}() directly with no "
                        f"monkeypatch or sys.stdin assignment shielding it "
                        f"-- stdin is captured "
                        f"under pytest, so that call raises before the "
                        f"test's assertion ever runs, against this or any "
                        f"other implementation of {fn_name}. Reshaping "
                        f"{fn_name} does not fix a test you cannot edit: "
                        f"this is the test's shape to answer for -- "
                        f"msg.challenge_tester, naming this test and quoting "
                        f"the call that cannot pass against any code")

    # A criterion that names the user as where a value comes from, met by a
    # function that never reads anything. Walk (empty-project, 2026-09-03):
    # "the system must retrieve the user's name" was implemented as
    # `def get_user_name(): return "User"` -- no `input()`, no parameter,
    # nothing that could ever vary -- and nothing caught it, because the
    # value it hardcoded ("User") was a word the material had already used,
    # so the invented-literals detector saw nothing invented. Different
    # failure shape: not a string nobody said, an *operation* nobody
    # performed. Deliberately narrow to the one source this has been
    # measured against -- "the user" -- rather than guessing at files,
    # the environment or the network with no walk behind any of them yet.
    if path.endswith(".py"):
        _ACQUIRE = ("retrieve", "get", "obtain", "ask", "prompt", "read",
                   "collect", "receive", "fetch", "accept", "request")
        criteria_here = ctx.conn.execute(
            "SELECT c.text, c.surface_refs FROM criteria c "
            "JOIN batch_tickets bt ON bt.ticket_id = c.ticket_id "
            "WHERE bt.batch_id = ?", (ctx.batch_id,)).fetchall()
        for crit in criteria_here:
            low = (crit["text"] or "").lower()
            if "user" not in low or not any(v in low for v in _ACQUIRE):
                continue
            try:
                surfaces = json.loads(crit["surface_refs"] or "[]")
            except (json.JSONDecodeError, TypeError):
                continue
            for fn in tree.body:
                if not (isinstance(fn, (_ast.FunctionDef, _ast.AsyncFunctionDef))
                       and fn.name in surfaces):
                    continue
                # A function that takes a parameter can legitimately leave
                # acquisition to its caller -- `greet_user(name)` is fine,
                # the reading happens one level up. Niladic is the tell:
                # nothing passed in, nothing read inside, so nothing could
                # ever make its return value differ from a fixed constant.
                niladic = not (fn.args.args or fn.args.vararg
                               or fn.args.kwonlyargs or fn.args.kwarg
                               or fn.args.posonlyargs)
                if not niladic:
                    continue
                reads = any(
                    (isinstance(n, _ast.Call) and isinstance(n.func, _ast.Name)
                     and n.func.id == "input")
                    or (isinstance(n, _ast.Attribute) and n.attr in
                        ("stdin", "argv", "environ", "getenv"))
                    for n in _ast.walk(fn))
                if not reads:
                    raise ValueError(
                        f"{fn.name} is the surface for a criterion that gets "
                        f"its value from the user ({crit['text']!r}); "
                        f"{fn.name} takes no argument and reads nothing -- no "
                        f"`input()`, nothing that could ever differ from one "
                        f"run to the next. A hardcoded return cannot satisfy "
                        f"'from the user'; read it, or take it as a parameter "
                        f"the caller reads")

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
    # The standard library and the project's own packages are not modules
    # the batch owes. clickI (2026-09-11): the repository's inherited tests
    # import __future__, click, shutil and twenty more, and every write of
    # main.py was refused for "modules that do not exist yet".
    import sys as _sys
    wanted -= set(getattr(_sys, "stdlib_module_names", ()))
    root = _worktree_of(ctx)
    def _present(m: str) -> bool:
        return any(((base / f"{m}.py").exists() or (base / m).is_dir())
                   for base in (root, root / "src", root / "lib"))
    missing = sorted(m for m in wanted if not _present(m))
    from pathlib import Path as _Path
    stem = _Path(path).stem
    # A rewrite that deletes a name the tests import breaks them with
    # certainty. Walk twenty-five: three green tests, and the fourth's fix
    # was a script.py with the three imported functions gone.
    if path.endswith(".py") and target.exists():
        try:
            old_tree = _ast.parse(target.read_text(encoding="utf-8"))
        # A file that does not decode has no names to keep. Frame 95's third
        # review (2026-09-30): a latin-1 byte refused the whole write here.
        except (SyntaxError, OSError, UnicodeDecodeError):
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
            # Two more sources of names the file has to keep. The Developer
            # now writes before the Tester, so on the first write the tests
            # are not there yet to protect anything: tipsO (2026-09-09), the
            # first write replaced four functions with one, the criterion's
            # surface named a vanished one, the test imported it, and the
            # fix loop ran to the step cap. The criteria's surfaces for this
            # file, and what other files in the tree import from it.
            for crit in ctx.conn.execute(
                    "SELECT c.surface_refs FROM criteria c "
                    "JOIN batch_tickets bt ON bt.ticket_id = c.ticket_id "
                    "WHERE bt.batch_id = ?", (ctx.batch_id,)):
                try:
                    refs = json.loads(crit["surface_refs"] or "[]")
                except (json.JSONDecodeError, TypeError):
                    continue
                imported |= {r.rsplit("::", 1)[-1] for r in refs
                             if "::" in r and _Path(r.split("::", 1)[0]).stem == stem}
            for other in root.rglob("*.py"):
                # The worktree lives under `.rota/`, so the exclusion reads
                # the relative parts; on the full path it skipped every
                # file and the importer scan never held (found 2026-09-09).
                relparts = other.relative_to(root).parts
                if other == target or ".rota" in relparts or ".venv" in relparts:
                    continue
                try:
                    src = other.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                # Relative and package-qualified imports count: `from
                # .termui import style`, `from click.termui import secho`.
                # Click night 49, walk 2 (2026-09-14): a span write cut
                # termui.py after `confirm`, twenty definitions gone, core.py
                # imports them with a leading dot, and all 43 tests failed
                # at import for the rest of the batch.
                for m in _re.finditer(
                        r"^\s*from\s+(?:[\w.]*\.)?" + _re.escape(stem)
                        + r"\s+import\s+\(?([^\r\n)]+)",
                        src, _re.M):
                    imported |= {x.strip().split(" as ")[0]
                                 for x in m.group(1).split(",") if x.strip()}
                imported |= set(_re.findall(r"\b" + _re.escape(stem) + r"\.(\w+)", src))
            # The entry point keeps every definition. tipsS, tipsT, tipsU,
            # tipsV (2026-09-09): four walks lost the interactive program to
            # a whole-file write of main.py that kept the feature and the
            # guard. Nothing imported the dropped functions, so the narrow
            # rule let them go, and with them the program. A file with a
            # main guard is the program; elsewhere, dropping a name nobody
            # uses stays the Developer's business.
            entry = any(isinstance(n, _ast.If) and isinstance(n.test, _ast.Compare)
                        and any(isinstance(c, _ast.Constant) and c.value == "__main__"
                                for c in n.test.comparators) for n in old_tree.body)
            dropped = old_defs - new_defs
            gone = sorted(dropped if entry else dropped & imported)
            # A whole-file write that drops a top-level name its own text
            # still uses. ACT-DV-edit-inside-the-function (2026-09-30): the
            # write kept `confirm` alone, `confirm` calls `_readline_prompt`,
            # and no door refused, because nothing imported the helpers.
            # A star import can bind any name, so the check stays silent
            # (frame 95 pass 6). A builtin still resolves after the
            # file's own shadow goes, so the file is not broken.
            used = []
            star = any(isinstance(x, _ast.ImportFrom) and any(a.name == "*" for a in x.names)
                       for x in _ast.walk(tree))
            if not span and not star:
                import builtins as _builtins
                used = sorted((set(_top_binds(old_tree)) - _bound_anywhere(tree)
                               - set(dir(_builtins)))
                              & {x.id for x in _ast.walk(tree)
                                 if isinstance(x, _ast.Name) and isinstance(x.ctx, _ast.Load)})
            if gone or used:
                whys = []
                if gone:
                    whys.append("the program's entry point keeps every definition it has"
                                if entry else
                                "the batch's tests, its criteria or other files use them")
                if used:
                    whys.append("your text still uses "
                                + (", ".join(used) if gone else "them"))
                why = ", and ".join(whys)
                spans = _kept_spans(old_tree, tree) if not span else []
                if spans:
                    # The kept definition's own span edits it in place and
                    # keeps every other line of the file. The offer runs
                    # bottom-up: a span write moves every line below it
                    # (frame 95 pass 6).
                    names = ", ".join(n for n, _lo, _hi in spans)
                    raise ValueError(
                        f"this rewrite of {path} drops {', '.join(sorted(set(gone) | set(used)))}, "
                        f"and {why}. To change {names} alone, write only "
                        f"{_span_offer(spans)}: "
                        f"{'each' if len(spans) > 1 else 'that'} span replaces the lines "
                        f"it holds now and keeps the rest of {path}")
                # tipsAT (2026-09-12): ten refusals in one session, the
                # same whole-file write of only the new functions each
                # time. The way out is a fact about the file, so say it:
                # the line count, and the span that appends.
                n_old = len(target.read_text(encoding="utf-8", errors="replace").splitlines())
                raise ValueError(
                    f"this rewrite of {path} drops {', '.join(sorted(set(gone) | set(used)))}, and "
                    f"{why}. Either write the whole file with every existing "
                    f"definition kept and your change added, or write only "
                    f"the new definitions with start={n_old}, end={n_old}: "
                    f"{path} has {n_old} lines and that span appends after "
                    f"them, keeping the rest. A line for the top of the "
                    f"file, an import, is start=0, end=0: that span inserts "
                    f"before the first line and drops nothing")
            # A definition the criteria do not name keeps its source. Click
            # nights 47 and 48 (2026-09-14): `echo` replaced by a simplified
            # copy while adding `echo_json`; 19 project tests red; nine fix
            # rounds called it unrelated.
            old_text = target.read_text(encoding="utf-8", errors="replace")
            changed = _changed_unnamed_defs(ctx, path, old_text, text)
            if changed:
                named = sorted(_criteria_surface_names(ctx)) or ["nothing"]
                old_lines = old_text.splitlines()
                spans = {n.name: (n.lineno - 1, getattr(n, "end_lineno", n.lineno))
                         for n in old_tree.body
                         if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef))}
                after = spans.get(changed[0], (len(old_lines), len(old_lines)))[1]
                raise ValueError(
                    f"this write changes {', '.join(changed)}, and no criterion of "
                    f"this batch names {'it' if len(changed) == 1 else 'them'}: the "
                    f"criteria name {', '.join(named)}. The project's own tests call "
                    f"{changed[0]} as it is. Leave it: write only your new definition "
                    f"with start={after}, end={after}, which inserts after {changed[0]}. "
                    f"A change to {changed[0]} needs a criterion that names it")
    # A module-level import of the file's own package is a cycle when the
    # package imports this file. Click night 51 (2026-09-14): `from click
    # import command` at the top of utils.py, which click/__init__.py
    # imports; every test failed at import and the loop ran to the cap.
    if path.endswith(".py"):
        cycle = _own_package_import(root, path, tree)
        if cycle:
            pkg, init_rel, name = cycle
            raise ValueError(
                f"{path} imports {name} from {pkg} at module level, and "
                f"{init_rel} imports {path}: a cycle, and every import of "
                f"{pkg} fails. Import {name} from the module that defines it "
                f"(a relative import, `from .core import ...`), or import "
                f"inside the function that uses it")
    # A span write that removes a line the rest of the file still needs.
    # Click night 120 (2026-10-05): s227 meant to add `import sys` and sent
    # start=0, end=5, which replaced the first five lines, and 43 of 43
    # tests went to error at import. Night 113's s146 did the same over 15
    # lines. The whole-file check above (791da68) never ran on a span. It
    # runs last, so every other door has judged the call it offers.
    if span and path.endswith(".py"):
        lost = _span_lost(lines, start, stop, fragment, tree)
        if lost is not None:
            raise ValueError(_span_lost_refusal(
                ctx, path, lines, start, end, fragment, lost, dry))
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
    # Every door has judged the call. A dry run stops before the disk.
    if dry:
        return {}
    # A write the file already holds changes nothing, and the result says so.
    # Night 97 (2026-09-29): s215 and s216 sent the landed text again, read
    # `"written, not committed": []`, and the test failed on one commit from
    # attempt 5 to 7. The red run of that commit is the thing to read.
    try:
        same = target.is_file() and target.read_text(encoding="utf-8") == text
    except (OSError, UnicodeDecodeError):
        same = False
    if same:
        dirty = _uncommitted(ctx, root)
        # The same fields a landed write returns (frame 93's review).
        out = {"path": path, "bytes": len(text.encode("utf-8")), "created": False,
               "unchanged": _unchanged_note(ctx, root, path, dirty),
               "written, not committed": dirty, "lands with": "code.commit"}
        if repair_note:
            out["repaired"] = repair_note
        if missing and stem not in missing:
            out["note"] = (f"the batch's tests import {', '.join(missing)} and no "
                           f"such module exists in the worktree yet")
        return out
    # A whole-file write is a span of the whole old file (frame 95).
    # A note never refuses a write, so a file that does not decode gives no
    # note (frame 95's third review, 2026-09-30).
    if not span and path.endswith(".py") and target.is_file():
        try:
            old = target.read_text(encoding="utf-8").splitlines()
            # A write that keeps some definitions counts the lines it drops
            # above and below them (frame 95 pass 5). The tail note covers
            # a write that keeps the whole shape and stops short.
            tail_note = _whole_drop(old, text) or _tail_drop(old, 0, len(old), text)
        except Exception:                                  # noqa: BLE001
            tail_note = None
    target.parent.mkdir(parents=True, exist_ok=True)
    existed = target.exists()
    target.write_text(text, encoding="utf-8")
    out = {"path": path, "bytes": len(text.encode("utf-8")),
           "created": not existed}
    # A fact, not an order: the seat decides whether the tail goes.
    if tail_note:
        out["dropped"] = tail_note
    # A fact about the text the seat sent, so the seat can send the escape.
    if repair_note:
        out["repaired"] = repair_note
    # A landed write is not a commit, and the result says so. Night 62
    # (2026-09-14, finding 68): the Developer implemented confirm() at
    # turn 9, spent fifteen turns on a test file, and the cap ended the
    # session with the edit in the worktree and nothing committed.
    out["written, not committed"] = _uncommitted(ctx, root)
    out["lands with"] = "code.commit"
    if missing and stem not in missing:
        out["note"] = (f"the batch's tests import {', '.join(missing)} and no "
                       f"such module exists in the worktree yet")
    return out


def _signature_drift(ctx: Ctx, tree) -> list[str]:
    """
    What the diff did to the names the standing findings are about, as a
    fact: parameters the worktree's definition requires that the project's
    definition did not. tipsAL (2026-09-10): `display_results` gained three
    required parameters, the constraint said a new required parameter
    breaks the main script, and the Developer committed nothing three
    sessions running while saying the constraint held.
    """
    import ast as _ast
    import subprocess as _sp
    from pathlib import Path as _P

    from ..core import worktrees as _wt

    batch = ctx.conn.execute(
        "SELECT head_commit FROM batches WHERE id = ?", (ctx.batch_id,)).fetchone()
    if not (batch and batch["head_commit"]):
        return []
    rows = ctx.conn.execute(
        "SELECT f.grain, f.constraint_id, b.grain AS path FROM findings f "
        "JOIN constraint_bindings b ON b.constraint_id = f.constraint_id "
        "WHERE f.batch_id = ? AND f.commit_sha = ? AND f.status = 'violated' "
        "AND b.grain_kind = 'path' "
        # A finding the Critic dismissed holds nothing (frame 88).
        "AND NOT EXISTS (SELECT 1 FROM finding_rulings fr WHERE fr.finding_id = f.id "
        "  AND fr.commit_sha = f.commit_sha AND fr.ruling = 'dismissed')",
        (ctx.batch_id, batch["head_commit"])).fetchall()
    try:
        root = _wt.project_root(ctx.conn)
    except Exception:
        return []

    def params(src: str, name: str):
        try:
            mod = _ast.parse(src)
        except SyntaxError:
            return None
        for node in _ast.walk(mod):
            if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)) and node.name == name:
                a = node.args
                pos = a.posonlyargs + a.args
                defaults = len(a.defaults)
                required = [p.arg for p in pos[:len(pos) - defaults]]
                required += [k.arg for k, d in zip(a.kwonlyargs, a.kw_defaults) if d is None]
                return required, [p.arg for p in pos] + [k.arg for k in a.kwonlyargs]
        return None

    notes: list[str] = []
    seen: set[tuple[str, str]] = set()
    for r in rows:
        name = (r["grain"] or "").split("::")[-1]
        path = r["path"]
        if (name, path) in seen or not path.endswith(".py"):
            continue
        seen.add((name, path))
        here = _P(tree) / path
        if not here.is_file():
            continue
        base = _sp.run([*_wt.GIT, "-C", str(root), "show", f"HEAD:{path}"],
                       capture_output=True, text=True)
        if base.returncode != 0:
            continue
        old = params(base.stdout, name)
        new = params(here.read_text(encoding="utf-8", errors="replace"), name)
        if old is None and new is None:
            continue
        if old is not None and new is None:
            notes.append(f"{name} is defined in {path} in the project and not in "
                         f"your tree: the constraint {r['constraint_id']} binds it")
            continue
        if old is None:
            continue
        gained = [p for p in new[0] if p not in old[1]]
        if gained:
            notes.append(
                f"{name} in {path} now requires {', '.join(gained)}, which the "
                f"project's {name}({', '.join(old[1])}) did not. A caller with "
                f"the old arguments fails: that is finding {r['constraint_id']}. "
                f"Give {', '.join(gained)} defaults, or restore the old signature")
    return notes


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
    tree = _batch_worktree(ctx)
    # A commit that leaves a criterion's surface undefined is a certain
    # ImportError for every test of it. tipsX (2026-09-09): the criterion
    # named `main.py::split_bill`, the Developer repurposed `calculate_tip`
    # and committed three times without ever defining `split_bill`. The
    # surface is the name the tests import; the file it names must define
    # it before the commit.
    import ast as _ast
    undefined: list[str] = []
    for crit in ctx.conn.execute(
            "SELECT c.id, c.surface_refs FROM criteria c "
            "JOIN batch_tickets bt ON bt.ticket_id = c.ticket_id "
            "WHERE bt.batch_id = ?", (ctx.batch_id,)):
        try:
            refs = json.loads(crit["surface_refs"] or "[]")
        except (json.JSONDecodeError, TypeError):
            continue
        for ref in refs:
            if "::" not in ref:
                # A bare name is a name some file in the tree must define.
                # clickI (2026-09-11): the surface was `echo_json`, the
                # Developer defined `echo_json_helper` in a new main.py,
                # and the commit went through because the bare name was
                # skipped here. Then the test imported a module that did
                # not exist.
                import re as _re
                if not _re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", ref):
                    continue
                pat = _re.compile(rf"^\s*(?:def|class)\s+{_re.escape(ref)}(?!\w)", _re.M)
                # The parts below the tree, not the whole path: a worktree
                # lives under `.rota/worktrees/<batch>`, and the old test
                # on `py.parts` dropped every file in it. clickI night 22
                # (2026-09-12): echo_json defined in src/click/echo_json.py,
                # and the commit refused for a tree that did not define it.
                if not any(pat.search(py.read_text(encoding="utf-8", errors="replace"))
                           for py in tree.rglob("*.py")
                           if ".venv" not in py.relative_to(tree).parts
                           and ".rota" not in py.relative_to(tree).parts
                           and "tests" not in py.relative_to(tree).parts):
                    undefined.append(f"{ref} (the surface criterion {crit['id']} names)")
                continue
            if not ref.split("::", 1)[0].endswith(".py"):
                continue
            rel, name = ref.split("::", 1)
            f = tree / rel
            if not f.is_file():
                continue
            try:
                defs = {n.name for n in _ast.parse(
                    f.read_text(encoding="utf-8", errors="replace")).body
                    if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef,
                                      _ast.ClassDef))}
            except SyntaxError:
                continue
            if name not in defs:
                undefined.append(f"{ref} (the surface criterion {crit['id']} names)")
    if undefined:
        raise ValueError(
            f"the tree does not define {', '.join(undefined)}, the surface "
            f"the criteria name and the tests import. Define it in the file "
            f"named, then commit. A commit without it fails every test of "
            f"it at import")
    drift = _signature_drift(ctx, tree)
    # A commit that puts the tree back where it stood before the last one
    # is churn. clickI night 30 (2026-09-13): twelve commits flipping a
    # trailing newline between a test that passed either way and a Critic
    # that read the criterion differently each time; six pass verdicts,
    # each on a head the next commit left behind, and no merge. The tree
    # two commits back is a fact git holds.
    import subprocess as _sp
    has_two = _sp.run([*worktrees.GIT, "-C", str(tree), "rev-parse", "--verify", "-q", "HEAD~1"],
                      capture_output=True, text=True).returncode == 0
    if has_two:
        same_as_before = _sp.run(
            [*worktrees.GIT, "-C", str(tree), "diff", "--quiet", "HEAD~1", "--", ".",
             ":(exclude).venv", ":(exclude).rota"], capture_output=True, text=True).returncode == 0
        changed_now = _sp.run(
            [*worktrees.GIT, "-C", str(tree), "diff", "--quiet", "HEAD", "--", ".",
             ":(exclude).venv", ":(exclude).rota"], capture_output=True, text=True).returncode != 0
        if same_as_before and changed_now:
            raise ValueError(
                "this commit puts the tree back where it stood before your last "
                "commit: you are undoing yourself. The tests pass both ways, so "
                "the disagreement is not in the code. Say what stands and why "
                "(a decision), challenge the test (msg.challenge_tester) or "
                "escalate the criterion (msg.escalate_architect); do not flip")
    # The Tester's test files are not the Developer's diff. The harness
    # writes the bodies at run time (harness.materialise) and `add -A`
    # was staging whatever version lay there. Click night 50 (2026-09-14):
    # a first encode was committed and merged, the Tester's re-encode
    # reached only the database, and walk 2 inherited a test that could
    # never pass. The merge delivers the current bodies in a commit of
    # their own (lifecycle.merge).
    test_paths = tuple(r["path"] for r in ctx.conn.execute(
        "SELECT path FROM tests WHERE batch_id = ?", (ctx.batch_id,)) if r["path"])
    sha = worktrees.commit(tree, message, exclude=test_paths)
    if sha is None and drift:
        raise ValueError(
            "nothing changed, and the finding stands. " + " ".join(drift)
            + ". Change the file, then commit")
    if sha is None:
        # Not an error -- the docstring says why -- but the bare result read
        # as completion. Recorded after the ledger rename: the Developer
        # probed, loaded criteria, called commit on an untouched tree, logged
        # a real assumption, and ended -- five runs of five, twice, with
        # `code.write` never called. The result now carries the fork the
        # session is actually at.
        #
        # "Say so and finish" named no ending, and the seat picked the one
        # tool it had: ACT-DV-edit-inside-the-function (2026-09-19) answered
        # that the criteria were met and sent `msg.challenge_tester`, the one
        # message `developer/tests_failing.md` gives it. The note now says
        # which ending, because a mode with a single message tool reads any
        # unnamed ending as that message.
        return {"committed": False, "why": "nothing changed",
                "note": ("the tree is exactly as you found it. If the "
                         "criteria are already met, say so in your reply and "
                         "end the session, with no message to anybody; if "
                         "you were going to change the code, the change "
                         "comes first: code.write, then commit")}

    ctx.writes.append(("batches", ctx.batch_id, {"head_commit": sha}, False))
    touched = worktrees.touched(tree)
    # Detector two (`core.divergence`): the paths this commit reached that
    # the batch's prediction never named. Recorded, never refused (law 12).
    # A path already judged for this batch, either way, is not raised
    # again: the Developer's commit that takes a mistake out touches the
    # same path.
    strays = _outside_prediction(ctx, ctx.batch_id, touched)
    out = {"committed": True, "head_commit": sha, "touched": touched}
    if strays:
        for path in strays:
            ctx.writes.append(("touch_strays", f"{ctx.batch_id}:{sha}:{path}", {
                "batch_id": ctx.batch_id, "commit_sha": sha, "path": path,
                "status": "open"}))
        out["outside_prediction"] = strays
        out["note"] = (f"{', '.join(strays[:6])}{' and more' if len(strays) > 6 else ''}: "
                       f"the batch's predicted touch set never named "
                       f"{'this path' if len(strays) == 1 else 'these paths'}. "
                       f"The commit stands. The Architect is asked whether it "
                       f"was foreseen or a mistake before the batch merges; if "
                       f"you know it was a mistake, take it out and commit")
    return out


def _predicted_touch(ctx: Ctx, batch_id: str) -> list[str]:
    """The batch's predicted touch as ground: path grains, and the file a
    file-qualified symbol lives in. Landed rows and the session's own
    staged ones alike."""
    rows = [(r["grain"], r["grain_kind"]) for r in ctx.conn.execute(
        "SELECT grain, grain_kind FROM batch_touch WHERE batch_id = ? "
        "ORDER BY grain", (batch_id,))]
    rows += [(w[2].get("grain"), w[2].get("grain_kind")) for w in ctx.writes
             if w[0] == "batch_touch" and w[2].get("batch_id") == batch_id]
    return [g for g, kind in rows
            if g and (kind == "path" or (kind == "symbol" and "::" in g))]


def _outside_prediction(ctx: Ctx, batch_id: str, touched: list[str]) -> list[str]:
    """Detector two: the touched paths the prediction never named, less the
    paths already judged for this batch. Empty when nothing was predicted."""
    from ..core.divergence import stray_paths

    judged = {r["path"] for r in ctx.conn.execute(
        "SELECT path FROM touch_strays WHERE batch_id = ? AND status != 'open'",
        (batch_id,))}
    # The tests are the Tester's, and the harness commits them into the
    # batch: clickI night 41 (2026-09-13) raised six test files as the
    # Developer's strays. A test path is never a stray.
    return [p for p in stray_paths(touched, _predicted_touch(ctx, batch_id))
            if p not in judged and not _is_test_path(p)]


@op("batches", "judge_touch")
def batches_judge_touch(ctx: Ctx, batch_id: str, foreseen: list[str] | None = None,
                        mistakes: list[str] | None = None, reason: str = "") -> dict:
    """
    Say which stray paths the prediction should have named and which are a
    mistake. A foreseen path joins the touch set as expected; a mistake
    wakes the Developer to take it out. Every open stray on the head commit
    is judged one way or the other, and the merge waits until then.
    """
    foreseen = [p.replace("\\", "/") for p in (foreseen or [])]
    mistakes = [p.replace("\\", "/") for p in (mistakes or [])]
    _must_exist(ctx, "batches", batch_id)
    head = ctx.conn.execute("SELECT head_commit FROM batches WHERE id = ?",
                            (batch_id,)).fetchone()["head_commit"]
    open_rows = [r["path"] for r in ctx.conn.execute(
        "SELECT path FROM touch_strays WHERE batch_id = ? AND commit_sha = ? "
        "AND status = 'open' ORDER BY path", (batch_id, head or ""))]
    if not open_rows:
        raise ValueError(f"{batch_id} has no unjudged stray on its head commit; "
                         f"nothing to judge")
    # A name that is not an open stray is dropped, not refused: clickI night
    # 41 (2026-09-13), the Architect named the test paths and the symbols
    # of the prediction beside the one stray, three sessions of three
    # identical refused calls. The judgement on the strays it did name is
    # the work; the rest is noise, and is said to be.
    unknown = [p for p in foreseen + mistakes if p not in open_rows]
    foreseen = [p for p in foreseen if p in open_rows]
    mistakes = [p for p in mistakes if p in open_rows]
    both = sorted(set(foreseen) & set(mistakes))
    if both:
        raise ValueError(f"{', '.join(both)} cannot be both foreseen and a mistake")
    left = [p for p in open_rows if p not in foreseen and p not in mistakes]
    if left:
        raise ValueError(
            f"{', '.join(left)} {'is' if len(left) == 1 else 'are'} still unjudged. "
            f"Every open stray is foreseen or a mistake; say which")
    for path in foreseen:
        ctx.writes.append(("batch_touch", f"{batch_id}:{path}", {
            "batch_id": batch_id, "grain": path, "grain_kind": "path",
            "confidence": "expected"}))
        ctx.writes.append(("touch_strays", f"{batch_id}:{head}:{path}", {
            "batch_id": batch_id, "commit_sha": head, "path": path,
            "status": "foreseen", "note": reason or None}))
    for path in mistakes:
        ctx.writes.append(("touch_strays", f"{batch_id}:{head}:{path}", {
            "batch_id": batch_id, "commit_sha": head, "path": path,
            "status": "mistake", "note": reason or None}))
    out = {"batch": batch_id, "foreseen": foreseen, "mistakes": mistakes}
    if unknown:
        out["ignored"] = (f"{', '.join(unknown)}: not an open stray of {batch_id}; "
                          f"the strays were {', '.join(open_rows)}")
    # tipsBH s59 (2026-09-14): the judgement landed on turn one and the
    # Architect sent it twice more, ended by the repeat rule. Say it is done.
    out["next"] = ("recorded; nothing else is owed this wake. End with one "
                   "sentence and no call")
    return out


@op("batches", "strays")
def batches_strays(ctx: Ctx, batch_id: str) -> list[dict]:
    """The stray paths of the batch's head commit and how each was judged."""
    head = ctx.conn.execute("SELECT head_commit FROM batches WHERE id = ?",
                            (batch_id,)).fetchone()
    if head is None:
        raise ValueError(f"{batch_id!r} is not a batch")
    return [dict(r) for r in ctx.conn.execute(
        "SELECT path, status, note FROM touch_strays WHERE batch_id = ? "
        "AND commit_sha = ? ORDER BY path", (batch_id, head["head_commit"] or ""))]


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


@op("batches", "expect")
def batches_expect(ctx: Ctx, batch_id: str | None = None) -> dict:
    """
    What the batch is for and where the Architect expects the change.

    Read 2026-09-13 from a Developer's batch_start wake on tipsI: one line
    of ticket, four criteria naming a callable that did not exist, and
    nothing else. The item, the principal's own sentences behind it, the
    predicted touch set and the batch's tests were all rows the Developer
    could not reach. No argument, so the runner pushes it into the wake.
    """
    bid = batch_id or ctx.batch_id
    if not bid:
        # Pushed into every Developer wake, batch or none: a read that raises
        # here would kill the session before its first turn.
        return {"note": "this session works in no batch"}
    row = ctx.conn.execute(
        "SELECT b.id AS id, b.item_id AS item_id, i.text AS item_text "
        "FROM batches b LEFT JOIN items i ON i.id = b.item_id WHERE b.id = ?",
        (bid,)).fetchone()
    if row is None:
        raise ValueError(f"{bid!r} is not a batch")
    said = [r["text"] for r in ctx.conn.execute(
        "SELECT s.text AS text FROM refs x "
        "JOIN statements s ON s.id = x.target "
        "WHERE x.src_table = 'items' AND x.kind = 'statement' AND x.src_id = ? "
        "AND s.status != 'superseded' ORDER BY s.id",
        (row["item_id"] or "",))]
    touch = [dict(r) for r in ctx.conn.execute(
        "SELECT grain, grain_kind, confidence FROM batch_touch WHERE batch_id = ? "
        "ORDER BY confidence, grain_kind, grain", (bid,))]
    tests = [dict(r) for r in ctx.conn.execute(
        "SELECT id, criterion_id, path FROM tests WHERE batch_id = ? ORDER BY id", (bid,))]
    return {
        "batch": bid,
        "item": row["item_text"] or "",
        "the principal said": said,
        "expected to touch": [t["grain"] for t in touch
                              if t["grain_kind"] == "path" and t["confidence"] == "expected"],
        "might touch": [t["grain"] for t in touch
                        if not (t["grain_kind"] == "path" and t["confidence"] == "expected")],
        "tests": tests,
        "note": ("the touch set is the Architect's prediction, not a permission: a "
                 "path outside it is not refused, it is judged after the commit"),
    }



def _own_package_import(root, path: str, tree) -> tuple[str, str, str] | None:
    """
    (package, init path, name) when `path` imports its own package at
    module level and the package's __init__ imports `path`. Else None.

    `src/click/utils.py` holding `from click import command` while
    `src/click/__init__.py` holds `from .utils import echo` is the shape:
    importing click runs __init__, which imports utils, which imports
    click half-initialised. Module level only; an import inside a function
    runs after the package is whole.
    """
    import ast as _ast
    from pathlib import Path as _Path
    rel = _Path(path.replace("\\", "/"))
    if rel.name == "__init__.py" or len(rel.parts) < 2:
        return None
    pkg_dir = rel.parent
    init = root / pkg_dir / "__init__.py"
    if not init.exists():
        return None
    pkg = pkg_dir.name
    stem = rel.stem
    imports_me = False
    try:
        init_tree = _ast.parse(init.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return None
    for node in init_tree.body:
        if isinstance(node, _ast.ImportFrom):
            mod = node.module or ""
            if (node.level == 1 and (mod == stem or mod.startswith(stem + "."))) \
                    or mod == f"{pkg}.{stem}":
                imports_me = True
            if node.level == 1 and mod == "" and any(a.name == stem for a in node.names):
                imports_me = True
    if not imports_me:
        return None
    for node in tree.body:
        if isinstance(node, _ast.ImportFrom) and node.level == 0 and node.module == pkg:
            return (pkg, (pkg_dir / "__init__.py").as_posix(), node.names[0].name)
        if isinstance(node, _ast.Import) and any(a.name == pkg for a in node.names):
            return (pkg, (pkg_dir / "__init__.py").as_posix(), pkg)
    return None


def _criteria_surface_names(ctx: Ctx) -> set[str]:
    """The names the batch's criteria name as surfaces, bare."""
    import json as _json
    names: set[str] = set()
    if not getattr(ctx, "batch_id", None):
        return names
    for row in ctx.conn.execute(
            "SELECT c.surface_refs FROM criteria c "
            "JOIN batch_tickets bt ON bt.ticket_id = c.ticket_id "
            "WHERE bt.batch_id = ?", (ctx.batch_id,)):
        try:
            refs = _json.loads(row["surface_refs"] or "[]")
        except (ValueError, TypeError):
            continue
        names |= {str(r).rsplit("::", 1)[-1].rsplit(".", 1)[-1] for r in refs if r}
    return names


def _def_sources(text: str) -> dict[str, list[str]]:
    """Top-level definition name to its source segments, in order."""
    import ast as _ast
    out: dict[str, list[str]] = {}
    try:
        tree = _ast.parse(text)
    except SyntaxError:
        return out
    for node in tree.body:
        if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef)):
            out.setdefault(node.name, []).append(_ast.get_source_segment(text, node) or "")
    return out


def _changed_unnamed_defs(ctx: Ctx, path: str, old_text: str, new_text: str) -> list[str]:
    """
    Definitions the write changes that no criterion names, and that the
    write does not restore to the project's own version.

    Click nights 47 and 48 (2026-09-14): asked for `echo_json` next to
    `echo`, the Developer's span write replaced `echo` with a simplified
    copy of its own, 19 of click's tests failed at the commit, and nine
    fix rounds judged the failures unrelated. The criteria name
    `echo_json`; `echo` is the project's, and the project's tests call it
    as it is. A definition the file had, whose source the write changes
    or duplicates, is refused unless a criterion names it or the new
    source is the project's own (a restoration).
    """
    from pathlib import Path as _Path
    named = _criteria_surface_names(ctx)
    if not named:
        return []          # no stated scope to hold the write to
    before = _def_sources(old_text)
    after = _def_sources(new_text)
    base: dict[str, list[str]] = {}
    try:
        root = ctx.conn.execute(
            "SELECT value FROM config WHERE key = 'project_root'").fetchone()
        if root and root[0]:
            base_file = _Path(root[0]) / path
            if base_file.exists():
                base = _def_sources(base_file.read_text(encoding="utf-8", errors="replace"))
    except Exception:                                      # noqa: BLE001
        base = {}
    changed = []
    for name, segs in after.items():
        # Private helpers included: click night 55 (2026-09-14) rewrote
        # `_format_default` whole while adding a flag to confirm(), and
        # three of click's own prompt tests broke on the new wording.
        if name not in before or name in named:
            continue
        if segs == before[name]:
            continue
        if base.get(name) and segs == base[name]:
            continue                                       # restored
        changed.append(name)
    return changed


def _top_binds(tree) -> dict:
    """The names a module binds at its top level, each with its statement.
    An import binds a name too: `import sys` binds `sys` (frame 95 pass 5)."""
    import ast as _ast
    out: dict = {}
    for n in tree.body:
        names: list[str] = []
        if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef)):
            names = [n.name]
        elif isinstance(n, _ast.Import):
            names = [a.asname or a.name.split(".")[0] for a in n.names]
        elif isinstance(n, _ast.ImportFrom):
            names = [a.asname or a.name for a in n.names if a.name != "*"]
        elif isinstance(n, (_ast.Assign, _ast.AnnAssign, _ast.AugAssign)):
            for t in (n.targets if isinstance(n, _ast.Assign) else [n.target]):
                names += [x.id for x in _ast.walk(t) if isinstance(x, _ast.Name)]
        for name in names:
            out.setdefault(name, n)
    return out


def _bound_anywhere(tree) -> set[str]:
    """Every name a module binds at any depth: a local or a parameter of the
    same name is not a use of the old top-level one."""
    import ast as _ast
    out: set[str] = set()
    for x in _ast.walk(tree):
        if isinstance(x, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef)):
            out.add(x.name)
        elif isinstance(x, _ast.arg):
            out.add(x.arg)
        elif isinstance(x, _ast.Name) and not isinstance(x.ctx, _ast.Load):
            out.add(x.id)
        elif isinstance(x, _ast.alias):
            out.add(x.asname or x.name.split(".")[0])
        elif isinstance(x, _ast.ExceptHandler) and x.name:
            out.add(x.name)
        elif isinstance(x, (_ast.MatchAs, _ast.MatchStar)) and x.name:
            out.add(x.name)
        elif isinstance(x, _ast.MatchMapping) and x.rest:
            out.add(x.rest)
    return out


def _is_future(node) -> bool:
    import ast as _ast
    return isinstance(node, _ast.ImportFrom) and node.module == "__future__"


def _is_docstring(node) -> bool:
    import ast as _ast
    return (isinstance(node, _ast.Expr)
            and isinstance(getattr(node.value, "value", None), str))


def _span_lost(lines: list[str], start: int, stop: int, fragment: str, tree) -> dict | None:
    """What a span write removes that the rest of the file still needs.

    `names`: the names the old file bound at the top level, that the merged
    file loads and binds nowhere. `futures`: the `from __future__` imports
    of the span whose features the merged file no longer holds. A star
    import can bind any name, so the check stays silent there, and a
    builtin still resolves after the file's own shadow goes (frame 95).
    """
    import ast as _ast
    import builtins as _builtins
    try:
        old = _ast.parse(chr(10).join(lines))
    except SyntaxError:
        return None
    if any(isinstance(x, _ast.ImportFrom) and any(a.name == "*" for a in x.names)
           for x in _ast.walk(tree)):
        return None

    def _in_span(s) -> bool:
        return start <= s.lineno - 1 and getattr(s, "end_lineno", s.lineno) <= stop

    binds = _top_binds(old)
    loads = {x.id for x in _ast.walk(tree)
             if isinstance(x, _ast.Name) and isinstance(x.ctx, _ast.Load)}
    names = sorted(n for n in (set(binds) - _bound_anywhere(tree)
                               - set(dir(_builtins))) & loads
                   if _in_span(binds[n]))
    have = {a.name for x in tree.body if _is_future(x) for a in x.names}
    futures = [s for s in old.body
               if _is_future(s) and _in_span(s) and any(a.name not in have for a in s.names)]
    if not names and not futures:
        return None
    stmts = sorted({id(s): s for s in futures + [binds[n] for n in names]}.values(),
                   key=lambda s: s.lineno)
    removed = set(_top_binds(_ast.Module(body=[s for s in old.body if _in_span(s)],
                                         type_ignores=[])))
    try:
        own = set(_top_binds(_ast.parse(fragment)))
    except SyntaxError:
        own = None
    return {"names": names, "futures": futures, "stmts": stmts, "old": old,
            "insert": own is not None and not (own & removed)}


def _span_lost_refusal(ctx: Ctx, path: str, lines: list[str], start: int, end: int,
                       fragment: str, lost: dict, dry: bool) -> str:
    """The refusal of a span that removes a needed line: one fact, and one
    call only when the doors admit it (frame 136)."""
    import ast as _ast

    def _seg(s) -> str:
        return chr(10).join(lines[s.lineno - 1:getattr(s, "end_lineno", s.lineno)]).strip()

    segs = [_seg(s) for s in lost["stmts"]]
    quoted = [f"'{x}'" for x in segs]
    quoted = quoted[0] if len(quoted) == 1 else ", ".join(quoted[:-1]) + " and " + quoted[-1]
    names = lost["names"]
    if names:
        listed = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
        fact = (f"start={start}, end={end} removes {quoted}, and the rest of {path} "
                f"still uses {listed}.")
    else:
        fact = (f"start={start}, end={end} removes {quoted}, and the rest of {path} "
                f"runs under that `from __future__` import.")
    if dry:
        return fact
    one = len(segs) == 1
    if lost["insert"]:
        # The seat meant to add its text. The insert goes below a leading
        # docstring and `from __future__` imports, as the doors require.
        body = lost["old"].body
        lead = []
        for i, s in enumerate(body):
            if (i == 0 and _is_docstring(s)) or _is_future(s):
                lead.append(s)
                continue
            break
        at = start
        if lead and start <= lead[-1].lineno - 1:
            at = max(start, lead[-1].end_lineno)
        if _admits(ctx, path, fragment, at, at):
            return (f"{fact} To add your text and keep every line, "
                    f"send start={at}, end={at}.")
        return fact
    # A replace: the text must carry the removed lines itself.
    try:
        own = _ast.parse(fragment).body
    except SyntaxError:
        return fact
    flines = fragment.splitlines()
    doc_end = own[0].end_lineno if own and _is_docstring(own[0]) else 0
    lead_end = doc_end
    for s in own[1 if doc_end else 0:]:
        if not _is_future(s):
            break
        lead_end = s.end_lineno
    futs = [_seg(s) for s in lost["stmts"] if _is_future(s)]
    rest = [_seg(s) for s in lost["stmts"] if not _is_future(s)]
    built = (flines[:doc_end] + futs + flines[doc_end:lead_end] + rest
             + flines[lead_end:])
    if not _admits(ctx, path, chr(10).join(built) + chr(10), start, end):
        return fact
    them = "it" if one else "them"
    which = "that line" if one else "those lines"
    if futs:
        return (f"{fact} To keep {them}, put {which} at the top of your text, the "
                f"`from __future__` line first, and send start={start}, end={end} again.")
    return (f"{fact} To keep {them}, put {which} in your text below any "
            f"`from __future__` line, and send start={start}, end={end} again.")


def _future_order(fragment: str):
    """A text whose `from __future__` imports sit below another statement:
    (the text with them moved up, their lines, the first line above them).
    None when the text has no such import or does not parse."""
    import ast as _ast
    try:
        body = _ast.parse(fragment).body
    except SyntaxError:
        return None
    flines = fragment.splitlines()

    def _seg(s):
        return chr(10).join(flines[s.lineno - 1:s.end_lineno])

    start_i = 1 if body and _is_docstring(body[0]) else 0
    futs = [s for s in body[start_i:] if _is_future(s)]
    if not futs:
        return None
    above = next((s for s in body[start_i:] if not _is_future(s)
                  and s.lineno < futs[-1].lineno), None)
    if above is None:
        return None
    gone = set()
    for s in futs:
        gone.update(range(s.lineno - 1, s.end_lineno))
    top = body[0].end_lineno if start_i else 0
    kept = [x for i, x in enumerate(flines) if i not in gone]
    moved = kept[:top] + [_seg(s) for s in futs] + kept[top:]
    return (chr(10).join(moved) + chr(10), [_seg(s).strip() for s in futs],
            flines[above.lineno - 1].strip())


def _kept_spans(old_tree, new_tree) -> list[tuple[str, int, int]]:
    """The old top-level definitions the new text defines again, each with
    its span in code.source numbering, decorators included."""
    import ast as _ast
    defs = (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef)
    names = {n.name for n in new_tree.body if isinstance(n, defs)}
    out = []
    for n in old_tree.body:
        if isinstance(n, defs) and n.name in names:
            lo = min([n.lineno] + [d.lineno for d in n.decorator_list]) - 1
            out.append((n.name, lo, n.end_lineno))
    return out


def _span_offer(spans) -> str:
    """The spans, last first. A span write moves the lines below it, so a
    span above stays true only while the writes run bottom-up (frame 95
    pass 6)."""
    order = sorted(spans, key=lambda s: s[1], reverse=True)
    offer = ", and then ".join(f"{n} with start={lo}, end={hi}" for n, lo, hi in order)
    if len(order) > 1:
        offer += " (write them in this order, last first)"
    return offer


_BROKEN_STRING = ("unterminated string literal", "unterminated f-string literal",
                  "unterminated t-string literal")


def _find_close(line: str, quote: str, i: int) -> int:
    """Where `quote` closes a string in `line` from `i`, or -1."""
    while i < len(line):
        if line.startswith(quote, i):
            return i
        i += 2 if line[i] == "\\" else 1
    return -1


def _scan_line(line: str, triple: str | None = None) -> tuple[str | None, str | None]:
    """
    Read one line of source from the state `triple`, an open triple quote.

    Return the quote of a short string the line leaves open, and the triple
    quote still open at the end of the line.
    """
    i, n = 0, len(line)
    if triple:
        close = _find_close(line, triple, 0)
        if close < 0:
            return None, triple
        i = close + 3
    while i < n:
        c = line[i]
        if c == "#":
            break
        if c in "'\"":
            if line.startswith(c * 3, i):
                # A triple-quoted string that runs past the line is not a
                # short string, and its line breaks are the seat's own.
                close = _find_close(line, c * 3, i + 3)
                if close < 0:
                    return None, c * 3
                i = close + 3
                continue
            close = _find_close(line, c, i + 1)
            if close < 0:
                return c, None
            i = close + 1
            continue
        i += 1
    return None, None


def _indent_view(fragment: str) -> tuple[str, list[str], list[bool], str]:
    """
    The fragment moved to the top level, line for line, for ast.parse.

    A span inside a def sends indented lines, and ast.parse refuses them
    with `unexpected indent` (frame 99's diff review of edd3638). A line at
    shallower indent inside an indented text can be the rest of a broken
    string, so it keeps its place, and the prefix comes from the first
    line alone (the review of 85f7c4f). textwrap.dedent would shrink it.
    A comment at column 0 does not set the indent of a span, so the first
    line of code sets the prefix (the review of 5d54e9a).
    Return the view, the original lines, which lines lose the prefix, and
    the prefix.
    """
    parts = fragment.split("\n")
    first = next((p for p in parts if p.strip() and not p.lstrip().startswith("#")), "")
    prefix = first[:len(first) - len(first.lstrip())]
    cut = [bool(prefix) and p.startswith(prefix) for p in parts]
    view = "\n".join(p[len(prefix):] if c else p for p, c in zip(parts, cut))
    return view, parts, cut, prefix


def _parse_view(fragment: str) -> SyntaxError | None:
    """The parse error of the fragment at the top level, or None."""
    import ast as _ast
    try:
        _ast.parse(_indent_view(fragment)[0])
        return None
    except SyntaxError as exc:
        return exc


def _repair_broken_strings(fragment: str) -> tuple[str, list[int], set[int]]:
    """
    Join each line break that the call decoder put inside a short string.

    The decoder reads the two characters \\n as one line break, and that is
    right for the lines of the text. Night 99 (2026-09-30): s134 wrote
    `out += "\\n"`, and the text reached the parse door as two lines. Return
    the repaired text, the text's line numbers, from 1, that were joined,
    and the numbers of the lines that were joined with \\r\\n.
    """
    import ast as _ast
    _, parts, cut, prefix = _indent_view(fragment)
    origin = list(range(1, len(parts) + 1))
    joined: list[int] = []
    crlf: set[int] = set()
    last = 0
    # Each join takes one line or more, so the loop ends. A cap of 20 cut
    # a whole file with more breaks short (the review of 85f7c4f).
    for _ in range(len(parts)):
        view = "\n".join(p[len(prefix):] if k else p for p, k in zip(parts, cut))
        try:
            _ast.parse(view)
            break
        except SyntaxError as exc:
            if not (exc.msg or "").startswith(_BROKEN_STRING):
                break
            i = (exc.lineno or 1) - 1
            if i < last or i + 1 >= len(parts):
                break
            quote = _scan_line(parts[i])[0]
            if quote is None:
                break
            # A literal with more escapes arrives as more lines, and only
            # the last of them closes the quote (the review of edd3638).
            close = next((k for k in range(i + 1, min(i + 6, len(parts)))
                          if _find_close(parts[k], quote, 0) >= 0), None)
            if close is None:
                break
            # Accepted risk (the review of edd3638, point 5): a missing close
            # quote can join to a later quote and parse with another meaning.
            # The merged file must still compile, and the result names the line.
            # The decoder reads \r\n as CR LF, so a line that ends in CR
            # keeps both escapes (the review of 85f7c4f).
            if any(p.endswith("\r") for p in parts[i:close]):
                crlf.add(origin[i])
            parts[i] = "".join(p[:-1] + "\\r\\n" if p.endswith("\r") else p + "\\n"
                               for p in parts[i:close]) + parts[close]
            del parts[i + 1:close + 1], origin[i + 1:close + 1], cut[i + 1:close + 1]
            # A second join on the same line is the same line of the text.
            if not joined or joined[-1] != origin[i]:
                joined.append(origin[i])
            last = i
    return "\n".join(parts), joined, crlf


def _repair_sentence(joined: list[int], crlf: set[int] = frozenset()) -> str:
    """
    The one sentence that names each line the repair joined.

    A CR join writes the four characters \\r\\n, and the sentence says so
    (the review of 5d54e9a).
    """
    def _names(ns):
        ns = sorted(ns)
        return str(ns[0]) if len(ns) == 1 else (
            ", ".join(str(n) for n in ns[:-1]) + f" and {ns[-1]}")

    lf = [n for n in joined if n not in crlf]
    cr = [n for n in joined if n in crlf]
    if len(joined) == 1:
        head = (f"Line {joined[0]} of your text, counting from 1, ended inside a "
                f"string literal, so its line break is written as")
    else:
        head = (f"Lines {_names(joined)} of your text, counting from 1, ended inside "
                f"string literals, so their line breaks are written as")
    if not cr:
        return f"{head} the two characters \\n."
    if not lf:
        return f"{head} the four characters \\r\\n."
    return (f"{head} the two characters \\n, and as the four characters \\r\\n "
            f"on line{'s' if len(cr) > 1 else ''} {_names(cr)}.")


def _escape_note(fragment: str, exc: SyntaxError | None) -> str:
    """
    The sentences a refusal gains when the text holds a decoded escape.

    `exc` is the text's own parse error, or None to parse the text here.
    """
    if exc is None:
        exc = _parse_view(fragment)
        if exc is None:
            return ""
    note = ""
    if (exc.msg or "").startswith(_BROKEN_STRING):
        # The seat wrote \n in its call already, and the tool decoded it.
        # The form that passes is the escaped backslash (the review of edd3638).
        note += (" In your call write the newline escape inside a string as a "
                 "backslash, a backslash and n, \\\\n, because the tool decodes "
                 "one \\n into a line break.")
    # Night 99 (2026-09-30): s133 sent `\"\"\"` at turns 14 and 15, and a
    # backslash outside a string does not parse. A line inside a
    # triple-quoted string may hold the same characters as its own text.
    triple = None
    for k, line in enumerate(fragment.splitlines(), 1):
        head = line.strip()[:6]
        if triple is None and head in ('\\"\\"\\"', "\\'\\'\\'"):
            note += (f" Line {k} of your text starts with {head}; write the "
                     f"docstring quotes as three plain quotes.")
            break
        triple = _scan_line(line, triple)[1]
    return note


def _whole_drop(old_lines: list[str], text: str) -> str | None:
    """
    One sentence for a whole-file write that keeps some old top-level
    definitions and drops other top-level lines, or None.

    Frame 95 pass 5. `ACT-DV-edit-inside-the-function` (2026-09-30): the
    write kept `confirm` alone. The tail note named 4 lines after it and
    missed the 5 lines above it. This sentence counts both.

    The note arrives after the file is replaced, so a span in it would
    point into the new file. The note names no span (frame 95 pass 6).
    """
    import ast as _ast
    try:
        old_tree, new_tree = _ast.parse(chr(10).join(old_lines)), _ast.parse(text)
        spans = _kept_spans(old_tree, new_tree)
        if not spans:
            return None
        new_binds = set(_top_binds(new_tree))
        new_heads = {x.strip() for x in text.splitlines()}
        gone: set[int] = set()
        for n in old_tree.body:
            binds = [k for k, v in _top_binds(_ast.Module(body=[n], type_ignores=[])).items()]
            kept = (any(b in new_binds for b in binds) if binds
                    else old_lines[n.lineno - 1].strip() in new_heads)
            if not kept:
                lo = min([n.lineno] + [d.lineno for d in getattr(n, "decorator_list", [])]) - 1
                gone |= {i for i in range(lo, n.end_lineno) if old_lines[i].strip()}
        if not gone:
            return None
        first = old_lines[min(gone)].strip()
        word = "line" if len(gone) == 1 else "lines"
        return (f"This write drops {len(gone)} {word} of the old file, from `{first}`; "
                f"write the whole file again with those lines kept.")
    except Exception:                                      # noqa: BLE001
        return None


def _tail_drop(old_lines: list[str], start: int, stop: int, text: str) -> str | None:
    """
    One sentence that names the lines a write drops after the text's last
    terminator, or None.

    Night 98 (2026-09-29): s183 replaced all of `confirm` with a text that
    stopped at `raise Abort() from None`. The shorter function parsed, every
    door accepted it, and 13 lines went. Night 97 lost the same tail to a
    loop that ended at `continue`. The steps are in frame 95's design note,
    `plans/archive/frame95-design-2026-09-30.md`, section 3.

    A note and never a refusal, because a rewrite may mean to drop a tail.
    So a shape this walk does not expect returns None: a crash in a note is
    a refusal (ruled: frame 95's coordinator, 2026-09-30).
    """
    import ast as _ast
    fields = ("body", "handlers", "orelse", "finalbody", "cases")
    ends = (_ast.Return, _ast.Raise, _ast.Continue, _ast.Break)
    defs = (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef)
    try:
        new = text.splitlines() if text.strip() else []
        merged = old_lines[:start] + new + old_lines[stop:]
        old_tree = _ast.parse(chr(10).join(old_lines))
        new_tree = _ast.parse(chr(10).join(merged))

        def lo(n, src=old_lines):
            # A match_case has no line numbers. It starts at its `case`
            # header, the rule `code_write`'s own `_lo` uses.
            if isinstance(n, _ast.match_case):
                k = n.pattern.lineno - 1
                while k > 0 and not re.match(r"\s*case(?![\w.])", src[k]):
                    k -= 1
                return k
            decs = getattr(n, "decorator_list", None) or []
            return min([n.lineno] + [d.lineno for d in decs]) - 1

        def end(n):
            if isinstance(n, _ast.match_case):
                return end(n.body[-1])
            return n.end_lineno

        def head(src, n):
            if isinstance(n, _ast.match_case):
                return src[lo(n, src)].strip()
            return src[n.lineno - 1].strip()

        def kids(n):
            return [(f, getattr(n, f)) for f in fields if getattr(n, f, None)]

        # The outermost list that holds whole statements of the span, and
        # the index path to it, so the merged tree gives the same list.
        route, level = [], old_tree.body
        while True:
            pool = [x for x in level if start <= lo(x) and end(x) <= stop]
            if pool:
                break
            host = [i for i, x in enumerate(level) if lo(x) <= start and stop <= end(x)]
            if not host:
                return None
            subs = [f for f in fields
                    if any(lo(x) < stop and end(x) > start
                           for x in getattr(level[host[0]], f, None) or [])]
            if not subs:
                return None
            route.append((host[0], subs[0]))
            level = getattr(level[host[0]], subs[0])
        level_new = new_tree.body
        for i, f in route:
            level_new = getattr(level_new[i], f)
        mine = [x for x in level_new if start <= lo(x, merged) < start + len(new)]
        # `theirs` is the list a text statement pairs in. `pool` is every
        # statement at that level, so a dropped else block counts too.
        theirs, dropped, parent = pool, [], None
        while True:
            if not mine:
                return None
            # Pair in order. Frame 95's diff review (2026-09-30): the last
            # match of a first line paired the second of two `if value is
            # None:` blocks when the text stopped in the first one. The
            # cursor keeps each pair after the one before it.
            j, o = 0, None
            for m in mine:
                hits = [x for x in range(j, len(theirs))
                        if head(old_lines, theirs[x]) == head(merged, m)]
                if hits:
                    j = hits[0] + 1
                    o = theirs[hits[0]] if m is mine[-1] else None
            n = mine[-1]
            # The first unpaired old statement of the same type, never the
            # one at the text's index. Frame 95's third review (2026-09-30):
            # after an insert, the index took a later `if` and read 1 line.
            if o is None:
                o = next((x for x in theirs[j:] if type(x) is type(n)), None)
            if o is None:
                # No pair: count the drops found so far (the same review).
                # The leaf below still decides the gate.
                while kids(n):
                    parent, n = n, max(kids(n), key=lambda p: end(p[1][-1]))[1][-1]
                break
            dropped += [(x, n, o) for x in pool if lo(x) >= end(o)]
            if not kids(n):
                break
            f, mine = max(kids(n), key=lambda p: end(p[1][-1]))
            theirs = getattr(o, f, None) or []
            pool = [x for g in fields for x in getattr(o, g, None) or []]
            parent = n
        # The gate: a terminator inside a branch, not a def's own return.
        if not isinstance(n, ends) or parent is None or isinstance(parent, defs):
            return None
        # A line the text still holds at or below its leaf moved there, and
        # is not a loss. A line above the leaf is a different line (review).
        kept = {x.strip() for x in new[max(n.lineno - 1 - start, 0):]}

        def norm(t):
            # An `if` that became an `elif` is the same test (third review).
            t = t.strip()
            return t[2:] if t.startswith("elif ") else t

        def indent(t):
            return len(t) - len(t.lstrip())

        def moved(i, s, o):
            # A line the seat moved into the text statement `s` that holds
            # the leaf, at the level the line was dropped from. Night 97
            # moved the loop's `break` into each branch. The copy sits at the
            # same indent or deeper. The paired old statement `o` must not
            # hold the line, or a like block's header and body would hide
            # the second block (the two-block test, frame 95's third review).
            line = norm(old_lines[i])
            if any(norm(old_lines[k]) == line for k in range(lo(o), end(o))):
                return False
            return any(norm(merged[k]) == line and indent(merged[k]) >= indent(old_lines[i])
                       for k in range(lo(s, merged), end(s)))

        gone = sorted({i for x, s, o in dropped for i in range(lo(x), end(x))
                       if old_lines[i].strip() and old_lines[i].strip() not in kept
                       and not moved(i, s, o)})
        if not gone:
            return None
        word = "line" if len(gone) == 1 else "lines"
        return (f"This write drops {len(gone)} {word} that came after "
                f"`{head(merged, n)}`, from `{old_lines[gone[0]].strip()}`.")
    except Exception:                                      # noqa: BLE001
        return None


def _defined_in_tree(ctx: Ctx, name: str, path: str) -> set[str]:
    """The non-test modules of the batch's worktree that define `name` at
    top level, other than `path`. A regex over the files, not a parse: the
    question is one name, and the tree is small enough to read."""
    import re as _re
    root = _batch_worktree(ctx)
    if root is None or not root.is_dir():
        return set()
    pat = _re.compile(rf"^(?:async\s+def|def|class)\s+{_re.escape(name)}\b", _re.M)
    found: set[str] = set()
    for f in root.rglob("*.py"):
        rel = f.relative_to(root).as_posix()
        if rel == path.replace("\\", "/") or _is_test_path(rel) or rel.startswith((".venv/", ".rota/", "venv/")):
            continue
        try:
            if pat.search(f.read_text(encoding="utf-8", errors="replace")):
                found.add(rel)
        except OSError:
            continue
    return found

def _is_test_path(path: str) -> bool:
    """A test file by pytest's own rule, or anything under a tests directory."""
    p = (path or "").replace("\\", "/")
    name = p.rsplit("/", 1)[-1]
    return ("/tests/" in f"/{p}" or p.startswith("tests/")
            or name.startswith("test_") or name.endswith("_test.py") or name == "conftest.py")
