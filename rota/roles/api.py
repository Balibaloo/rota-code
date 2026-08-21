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
    item is a reading of something the principal said, and a Gatekeeper woken
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


# ---------------------------------------------------------------------------
# glossary
# ---------------------------------------------------------------------------

def _slug_of(term: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (term or "").strip().lower()).strip("_")


def _same_sense(text: str) -> str:
    """Two senses read as one when the index line reads the same.

    Case, spacing and a trailing full stop are not a distinction a reader of
    the glossary index can act on, so they are not one here either.
    """
    import re
    return re.sub(r"\s+", " ", (text or "").strip().lower()).strip(" .;:,")


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
    seen = getattr(ctx, "read_words", None)
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

    id = f"{slug}#{re.sub(r'[^a-z0-9]+', '_', sense.strip().lower())}" if sense else slug

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
    if not sense and ctx.area:
        prior = ctx.conn.execute(
            "SELECT id, area, sense_short FROM glossary_terms "
            "WHERE id = ? AND superseded_by IS NULL", (slug,)).fetchone()
        if (prior and prior["area"] and prior["area"] != ctx.area
                and _same_sense(prior["sense_short"]) != _same_sense(sense_short)):
            id = f"{slug}#{re.sub(r'[^a-z0-9]+', '_', ctx.area.lower()).strip('_')}"

    ctx.writes.append(("glossary_terms", id, {
        "term": term, "sense_short": sense_short, "sense_body": sense_body,
        "provenance": ctx.provenance, "area": ctx.area or ""}))
    return {"id": id}


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
        raise ValueError(
            f"{missing} is not a glossary id. Both ids come from the wake that "
            f"woke you, spelled as they were given.")
    if keep == drop:
        raise ValueError("keep and drop are the same row; nothing to merge.")
    if not (why or "").strip():
        raise ValueError(
            "say why they are the same before merging them. Reporting two "
            "senses costs the principal a glance; calling them the same "
            "destroys an ambiguity only they can settle, so this one has to be "
            "argued.")

    a, b = rows[keep], rows[drop]
    if _slug_of(a["term"]) != _slug_of(b["term"]):
        raise ValueError(
            f"{a['term']!r} and {b['term']!r} are different words. This says two "
            f"rows are one word said twice; it is not for relating two words.")
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
def glossary_lookup(ctx: Ctx, term: str) -> list[dict] | dict:
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
            raise ValueError(
                f"{', '.join(strangers)} is not a grain in the index. Bindings "
                f"name code the index already knows, and `code.probe` returns "
                f"those ids.")
    elif bindings:
        raise ValueError(
            f"there is no code index in this engagement, so {', '.join(bindings)} "
            f"names nothing that could be bound.")

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
    area = ctx.area
    if not area:
        raise ValueError(
            "no area: attesting closes the area you were woken for, and this "
            "session was not woken for one")

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
            "gatekeeper": "items"}.get(ctx.role)
    if outcome == "found":
        mine = [v for t, _id, v in ctx.writes if t == owed]
        if not mine:
            raise ValueError(
                f"you attested `found` and wrote no {owed} this session. That "
                f"is the artefact this mode exists to produce -- write what you "
                f"found, or attest `none_found`, which is a real answer and the "
                f"commonest right one here.")
        bodied = [v for v in mine
                  if (v.get("text") or v.get("sense_short") or
                      v.get("sense_body") or v.get("statement") or "").strip()]
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
    unknown, inside = [], []
    for grain in citations or []:
        exists = ctx.conn.execute(
            "SELECT 1 FROM code_index WHERE grain = ?", (grain,)).fetchone()
        if not exists:
            unknown.append(grain)
        elif area == "." or grain == area or grain.startswith(area.rstrip("/") + "/"):
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

    if not inside:
        outside = [g for g in (citations or []) if g not in unknown]
        raise ValueError(
            f"attesting closes {area!r}, and closing an area means citing what "
            f"you read in it -- `citations=[...]` naming grains, spelled as "
            f"they were listed for you and without line numbers. " +
            (f"These are indexed but not under {area!r}: {outside}. "
             if outside else "") +
            (f"These are not in the index at all: {unknown}. " if unknown else "") +
            f"Reading nothing and reporting nothing are not the same answer.")

    # What this was a survey *of*. See the column's note in schema.sql: the
    # index it read was built at this commit, so this is the commit surveyed.
    at = ctx.conn.execute(
        "SELECT value FROM config WHERE key = 'project_commit'").fetchone()
    ctx.writes.append(("survey_records", id, {
        "area": area, "outcome": outcome,
        "commit_sha": (at["value"] if at else "") or ""}))
    for grain in citations or []:
        ctx.writes.append(("survey_citations", f"{id}:{grain}", {
            "survey_id": id, "grain": grain,
            "resolves": 1 if grain not in unknown else 0}))
    # Unresolved ones are still reported rather than fatal. The bar is showing
    # what you read, not spelling every path correctly, and a session that can
    # see what it got wrong can fix it.
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
    _must_exist(ctx, "items", item_id)
    for tid in ticket_ids:
        _must_exist(ctx, "tickets", tid)

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
        raise ValueError(
            f"that is {criterion_id}'s own sentence written back, so nothing has "
            f"been encoded and a test that reports as coverage would exist. If "
            f"there is nothing you can add to it, the criterion is what is wrong "
            f"and saying so is the work of this session")

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
    # A decision is a thing *you* decided, and adopting what you were told is
    # not one. A Gatekeeper handed "no, I meant closing the account, not
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
    # something amended -- and the Gatekeeper ending an exhausted batch does
    # exactly that. Refused, it invented a fresh id and tried again, six times,
    # superseding itself down a spiral it never came out of: twelve turns, no
    # commit, every write discarded. A guard the model can walk into repeatedly
    # is worse than no guard, because the session dies instead of the call.
    #
    # The subject is still caught, which is what the rule was for: the contested
    # session passed the *item's own id* as the decision id.
    minuted = id if id in {i for t, i, *_ in ctx.writes if t == "items"} else None
    if minuted:
        raise ValueError(
            f"you amended {minuted} this session, so a decision "
            f"about it would be minuting your own edit. The amended item is the "
            f"record -- a decision is something you decided, and taking the "
            f"correction you were given is not. Report it and stop.")

    # Both of these are foreign keys, and a dangling one does not fail the call
    # -- it fails `session_commit`, which takes the whole session down with an
    # `IntegrityError` naming no column. Fourteen turns of a Gatekeeper's work
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

    if row is None or row["verb"] != "question":
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

    paths = [g for g, _ in sorted({**own, **imported}.items(), key=order)]

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

    budget, shown, omitted, bodies = 5200, [], [], {}
    for rel in paths:
        f = root / rel
        if not f.is_file():
            continue
        try:
            bodies[rel] = f.read_text(encoding="utf-8", errors="replace")
        except OSError:                                     # pragma: no cover
            continue

    for rel, body in bodies.items():
        if len(body) <= budget:
            take(rel, body, False)
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
    body = chr(10).join(lines[start:end])
    ctx.read_words.update(_words_in(path))
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
