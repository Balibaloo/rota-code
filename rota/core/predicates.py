"""
The predicates, declared — and the lint that says none may be missing.

The frontier is open message tips ∪ predicates evaluated against state. That only
holds if **every state a row can be in has a way out**. A state with no predicate
draining it is a place work stops silently, and the danger is precise: quiescence
means "no predicate fires", so a dead-end state makes the system look *finished*
while work has been abandoned. The invariant we rely on would pass.

Sweeping the schema found four such dead ends — a contested item, a contradicted
statement, a batch that passed review and was never merged, and a quarantined
message nobody is ever told about. None of them were noticeable by reading; all
four fall out of one mechanical check.

So predicates are declared here rather than defined ad hoc, each naming the state
it drains, and `check_terminal_states()` asserts the set is complete. A state is
legal only if some predicate drains it or it is declared terminal with a reason.
That is a hard constraint: adding a state to the schema without a way out fails
the build.

"""
from __future__ import annotations

import json

import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from .. import paths
from typing import Callable

from .scheduler import SURVEY_ORDER, Wake, live_tests

SCHEMA = paths.SCHEMA


# What a predicate does when it fires. `wakes` was a role id or the empty string,
# and the empty string was carrying two unrelated meanings — "the role is
# computed per row" and "no role at all, the scheduler acts". That flattening is
# why the field drifted twice: a lint checking it could not tell a typo from a
# deliberate blank.
# Law 6's ladder, and the only place it is written down as a sequence. Each rung
# is a role that can be *asked*, in the order a question climbs.
LADDER = ("developer", "architect", "vision_keeper")

# The same climb for a question rather than a batch, and it starts a rung higher
# because Developer is never the answer to somebody else's dead answer -- it is
# the role most likely to have asked. Both ladders end at Vision Keeper, who is the
# last rung anything wakes: above that is the principal, and nothing wakes a
# person.
QUESTION_LADDER = ("architect", "vision_keeper")


DERIVED = "*"        # the wake's role comes from the rows, not the declaration
SCHEDULER = "-"      # no role: the scheduler does this itself

# The Liaison's ledger row for a reply that answered nothing about the rows.
# One sentence in two places: `rota/roles/prompts/liaison/answering.md` tells
# the Liaison to write it, and `term_collision` reads it. Lower case, matched
# as a substring, because the Liaison names the rows after it.
UNADDRESSED_ANSWER = "the answer did not address the question"

# When a predicate fires, relative to the others. Lower goes first.
#
# Fix before start. A failed verdict and a failing test outrank a new batch,
# because a system that starts new work while old work is broken accumulates
# both. One thing at a time is not a scheduling nicety here — every role is
# single-instance, so starting something new is *how* the fix gets starved.
ORDER = {
    "traffic": 0,    # a message already in flight; someone is waiting
    "fix":    10,    # something is wrong and known
    "gate":   20,    # work finished, awaiting judgement
    "start":  30,    # new work
}


@dataclass(frozen=True)
class Predicate:
    name: str
    wakes: str                      # a role id, or DERIVED, or SCHEDULER
    drains: tuple[tuple[str, str, str], ...]   # (table, column, value)
    fn: Callable[[sqlite3.Connection], list[Wake]]
    why: str = ""
    band: str = "start"
    # Position in the file, stamped at registration. Within a band this is
    # the offer order -- the frontier ruling (2026-08-28): ordering must be
    # logical, and "alphabetically by predicate name" made the schedule a
    # fact about naming accidents. The file is organised as the spine, so
    # its order is a reviewable declaration where a name is not; messages
    # were always FIFO by seq and stay so.
    seq: int = 0
    needs_principal: bool = False   # only meaningful while they are here
    # Which roles a DERIVED predicate can actually wake. The role is computed
    # per row at runtime, which left it knowable only by reading the function —
    # so the obligation set, which asks "what modes exist", could not see the
    # three survey modes at all, and they were the ones with no prompt.
    derives: tuple[str, ...] = ()

    @property
    def order(self) -> int:
        return ORDER[self.band]


REGISTRY: dict[str, Predicate] = {}


def predicate(name: str, wakes: str, drains: tuple = (), why: str = "",
              band: str = "start", needs_principal: bool = False,
              derives: tuple = ()):
    def deco(fn):
        seq = len(REGISTRY)
        REGISTRY[name] = Predicate(
            name=name, wakes=wakes, drains=tuple(drains), fn=fn,
            why=why or (fn.__doc__ or "").strip(),
            band=band, needs_principal=needs_principal,
            derives=tuple(derives), seq=seq)
        return fn
    return deco


# ---------------------------------------------------------------------------
# Columns whose values are a *lifecycle* — a row passes through them and must be
# able to leave. Everything else is a classification: `kind`, `mode`,
# `cause_kind` and `grain_kind` say what a row *is*, not where it is, and asking
# what drains "out_of_scope" is a category error.
# ---------------------------------------------------------------------------

LIFECYCLE_COLUMNS = {
    ("statements", "status"),
    ("items", "approval"),
    ("batches", "status"),
    ("test_runs", "result"),
    ("ledger", "status"),
    ("verdicts", "result"),
    ("messages", "status"),
    ("survey_records", "outcome"),
}

# States that are ends, with the reason. A terminal state is a claim that nothing
# further is owed — which is exactly the claim worth having to write down.
TERMINAL: dict[tuple[str, str, str], str] = {
    ("ledger", "status", "parked"):
        "the row's item merged with the row open. The shipped line of the "
        "state view counts it, and no page asks for it (frame 204's design, "
        "section 4)",
    ("batches", "status", "abandoned"):
        "cancelled by ruling: the item's approval was withdrawn and the work "
        "did not happen. Never re-offered; the worktree stays as evidence",
    ("statements", "status", "ratified"):
        "the principal confirmed it; it is now material, not pending work",
    ("statements", "status", "superseded"):
        "replaced by a later statement, which carries the work forward",
    ("statements", "status", "clarified"):
        "the ambiguity was resolved in a later statement",
    ("items", "approval", "dropped"):
        "the principal dropped it, so no seat amends it and no page asks for "
        "it again (frame 357)",
    ("statements", "status", "dropped"):
        "the principal dropped it, so no page asks for it again (frame 357)",
    ("items", "approval", "approved"):
        "drained by slicing once tickets exist; approval itself owes nothing",
    ("items", "approval", "pending"):
        "an open gate to the principal holds it; the gate is the pending work",
    ("batches", "status", "merged"): "delivered",
    ("batches", "status", "running"): "a live session holds it",
    ("test_runs", "result", "pass"): "nothing is owed by a passing test",
    ("ledger", "status", "resolved"): "a decision closed it",
    ("verdicts", "result", "pass"): "drained by the merge action",
    ("messages", "status", "answered"): "a session committed against it",
    ("survey_records", "outcome", "found"): "the survey produced its record",
    ("survey_records", "outcome", "none_found"):
        "also a result — it is what starves constraint zero",
}


# ---------------------------------------------------------------------------
# The other half of the frontier, declared as a predicate.
#
# The lint caught this: `messages.status = 'open'` had no predicate draining it,
# because open tips were the *other* half of "tips ∪ predicates". That split put
# the frontier's definition in two places, and the second half was invisible to
# every check written against the first. Declared here, the frontier is simply
# "every predicate", and one of them happens to be a message query.
# ---------------------------------------------------------------------------

@predicate("message_tips", wakes=DERIVED, band="traffic",
           drains=[("messages", "status", "open")])
def message_tips(conn) -> list[Wake]:
    """Messages awaiting a session. Messages to the principal are excluded — they
    are a gate, and the principal is not schedulable."""
    from .scheduler import open_tips
    return open_tips(conn)


def _request_finished(conn, cur: dict) -> bool:
    """True when the request has work items and each is delivered or dropped.
    A request with no item yet is not finished: its work is still to come."""
    from ..roles.principal import _delivered, request_of
    from .scheduler import dropped_items

    here = set(cur["entries"])
    # `request_of` gives a description no request, so it is no work item
    # of the request (F15).
    mine = [r["id"] for r in conn.execute(
                "SELECT id FROM items WHERE kind = 'in_scope'")
            if request_of(conn, r["id"]) in here]
    if not mine:
        return False
    dropped = dropped_items(conn)
    return all(_delivered(conn, i) or i in dropped for i in mine)


@predicate("request_shift", wakes="liaison", band="traffic")
def request_shift(conn) -> list[Wake]:
    """
    A new request has a statement while an earlier request is not finished:
    ask the principal which goes first.

    Roman ruled that a request boundary is a question to the principal, not a
    silent park (frame 193's design, 2.F.1, ruled 2026-10-10 04:33). One wake
    per open earlier item, the oldest request first. The refs are the earlier
    item and the new request's statement, and the detail carries the facts
    the page shows. The question's id names the pair, so it is asked once.
    """
    from ..roles.principal import (_shift_waits, _shift_where, current_request,
                                   open_earlier_items)

    # No request message, no boundary: the common case costs one query.
    if not conn.execute(
            "SELECT 1 FROM messages WHERE from_role = 'principal' "
            "AND cause_id IS NULL AND verb = 'converse' LIMIT 1").fetchone():
        return []
    cur = current_request(conn, unread=False)
    if not cur or not cur["statements"]:
        return []
    # A finished request asks nothing. At a chain's end the delivered C
    # stayed current, and the wake asked about A against it (the review of
    # 61a0f41d, finding 4).
    if _request_finished(conn, cur):
        return []
    out = []
    for item in open_earlier_items(conn, cur, asked=False):
        out.append(Wake("liaison", "tick:request_shift",
                        refs=(item, cur["statements"][0]),
                        detail=(f"{item} is from an earlier request. Where it "
                                f"stands: {_shift_where(conn, item)} What it "
                                f"waits on: {_shift_waits(conn, item)}")))
    return out


# ---------------------------------------------------------------------------
# Understanding loop — these existed, now declared
# ---------------------------------------------------------------------------

@predicate("awaiting_confirm", wakes="liaison", band="gate",
           drains=[("statements", "status", "proposed")])
def awaiting_confirm(conn) -> list[Wake]:
    """A proposed statement with no confirm outstanding: ratification has stalled.

    Without this, a segmentation that never reached the principal sits forever
    and the system reports itself quiescent."""
    rows = conn.execute(
        "SELECT id FROM statements WHERE status = 'proposed' AND id NOT IN ("
        "  SELECT value FROM config WHERE 0)"          # placeholder join
    ).fetchall()
    if not rows:
        return []
    pending = conn.execute(
        "SELECT COUNT(*) n FROM messages "
        "WHERE status = 'open' AND to_role = 'principal' AND verb = 'confirm'"
    ).fetchone()["n"]
    if pending:
        return []
    return [Wake("liaison", "tick:awaiting_confirm",
                 refs=tuple(r["id"] for r in rows))]


@predicate("contradiction", wakes="liaison", band="fix",
           drains=[("statements", "status", "contradicted")])
def contradiction(conn) -> list[Wake]:
    """Two statements conflict. Only the principal can say which stands, so this
    goes back out rather than being resolved internally."""
    rows = conn.execute(
        "SELECT id FROM statements WHERE status = 'contradicted'").fetchall()
    if not rows:
        return []
    # A park ask can stay open all night, and it is not this question
    # (observed: frame 87's pass 3 review, 2026-09-30).
    from .scheduler import PARK_ASK

    asked = conn.execute(
        "SELECT COUNT(*) n FROM messages WHERE status='open' AND to_role='principal' "
        "AND verb='clarify' AND substr(id, 1, ?) != ?",
        (len(PARK_ASK), PARK_ASK)).fetchone()["n"]
    return [] if asked else [
        Wake("liaison", "tick:contradiction", refs=tuple(r["id"] for r in rows))]


@predicate("contested", wakes="vision_keeper", band="fix",
           drains=[("items", "approval", "contested")])
def contested(conn) -> list[Wake]:
    """The principal rejected an item.

    This was a dead end: the highest-value signal in the system landed nowhere.
    It wakes the item's owner to amend it or author a decision defending it."""
    # law 9: a ratified amendment drops the item to pending, stops batches
    # An item set aside wakes no owner until it resumes (frame 193's design,
    # 2.F.4). Night 137's s304, s307 and s310 amended the confirm item after
    # the principal had moved to the version option.
    from .scheduler import not_parked
    rows = conn.execute(
        "SELECT id FROM items WHERE approval = 'contested'"
        + not_parked(conn, "id")).fetchall()
    return [Wake("vision_keeper", "tick:contested", refs=(r["id"],)) for r in rows]


@predicate("guess", wakes="architect", band="gate")
def guess(conn) -> list[Wake]:
    """A request item with no guess of its code at its current version."""
    # Frame 298's design, 4.1 (ruled: Roman, 2026-10-18, "the architect owns
    # the guess"). Declared before `signoff`, so the gate band offers the
    # guess first. A live batch with a prediction already shows the plan, and
    # no index means no code yet (the `deliver` brief).
    from ..roles.principal import _is_request_item
    from .scheduler import not_parked

    if not conn.execute("SELECT 1 FROM code_index WHERE grain_kind = 'path' "
                        "LIMIT 1").fetchone():
        return []
    # A contest of his on the guess line stays owed until a set carries its
    # verdict. Dry run 6b's s145 read his files, wrote nothing, and the
    # commit called the relay answered. The tick carries the verdict, so
    # each ruling has its own bound (frame 362, the one rule).
    from .scheduler import owed, owed_in_flight, owed_park

    for r in conn.execute(
            "SELECT i.id AS id FROM items i WHERE i.approval IN ('draft', 'approved')"
            + not_parked(conn, "i.id") + " ORDER BY i.id").fetchall():
        found = owed(conn, r["id"])
        if (found is not None and found["line"] == "guess"
                and not owed_in_flight(conn, found["verdict"])
                # A spent key is a park, and the next item gets the wake.
                and not owed_park(conn, r["id"])
                and _is_request_item(conn, r["id"])):
            return [Wake("architect", "tick:guess", refs=(r["id"], found["verdict"]))]
    rows = conn.execute(
        "SELECT i.id AS id FROM items i "
        "WHERE i.approval IN ('draft', 'approved')"
        + not_parked(conn, "i.id") +
        "  AND NOT EXISTS (SELECT 1 FROM touch_guesses g "
        "                  WHERE g.item_id = i.id AND g.item_ver = i.version)"
        "  AND NOT EXISTS (SELECT 1 FROM batches b JOIN batch_touch t "
        "                  ON t.batch_id = b.id WHERE b.item_id = i.id "
        "                  AND b.status IN ('pending', 'deferred', 'running'))"
        " ORDER BY i.id").fetchall()
    item = next((r["id"] for r in rows if _is_request_item(conn, r["id"])), None)
    return [Wake("architect", "tick:guess", refs=(item,))] if item else []


@predicate("signoff", wakes="vision_keeper", band="gate",
           drains=[("items", "approval", "draft")])
def signoff(conn) -> list[Wake]:
    """Draft items with no gate open: submit them for approval, together."""
    from .scheduler import tick_signoff
    return tick_signoff(conn)


@predicate("term_collision", wakes="terminologist", band="fix")
def term_collision(conn) -> list[Wake]:
    """
    One word, two live senses, nobody ruling. The glossary's `contradiction`.

    Two statements that conflict already raise an obligation and go to the
    principal, because only they can say which stands. Two senses of one word
    are the same situation in the other artefact and raised nothing at all: the
    collision sat in the glossary until some role tripped over it while trying
    to do something else, and then it was that role's problem to notice.

    Which is why "two roles blocked on one ambiguity are two discoveries". The
    ambiguity is one fact about the glossary and belongs on the register once,
    owned by the role that owns the artefact.

    Derived from the rows: two or more entries sharing a term, with no decision
    referring to them. Discharged by that decision, or by the glossary coming
    back to one sense. Nobody declares it and nobody can forget to.
    """
    import json

    from ..roles.api import _singular, _slug_of
    from .scheduler import tick_survey

    # Not while the survey pass is still running.
    #
    # This is band `fix` and surveying is band `start`, so a collision found in
    # the second area is drained before the third is looked at. Measured: one
    # `.github` collision held a whole run and it finished with zero survey
    # records in 71 turns. The band order is right in general and wrong here,
    # because the cost of an unresolved collision is downstream work built on an
    # ambiguous word -- and during onboarding there is no downstream work.
    # `rests_on_a_collision` already suppresses any consumer whose criteria
    # touch the word, so waiting is safe by a mechanism that already exists.
    #
    # It is also judging on partial evidence. `folder`'s second sense arrived
    # from a different area three sessions later; ruling after the first two
    # would have settled it before the relevant fact existed.
    #
    # Conditional rather than a phase: a collision created later, in delivery,
    # fires at once, because by then something does depend on the word.
    from .scheduler import onboarding_phase

    if (onboarding_phase(conn) in ("orient", "reconcile", "define")
            or any(w.role == "terminologist" for w in tick_survey(conn))):
        return []

    # A second sense from area `.` is a row, not a collision.
    #
    # `tick_survey` says what `.` is, in its own words: "*what did not belong
    # anywhere else* by construction -- `areas.py` folds small directories up
    # into it. So it is the one area whose vocabulary is least likely to be the
    # project's." The second-row rule in `glossary.amend` is justified by the
    # opposite claim -- "two senses from different areas are the word doing
    # different work in two places" -- and that claim does not hold for a bucket.
    # `.` is not a place.
    #
    # Measured across `cnt_i` and `cnt_j`: of the distinct collisions raised,
    # two of five and two of four were a `#root` row against a real area's --
    # `variable`/`variable#root`, `frontmatter`/`frontmatter#root`. Each cost up
    # to three sessions and two of them exhausted the attempt bound, in runs
    # that then had no budget left to reach the Architect.
    #
    # The row is still written and still readable, which is the half that
    # matters: refusing `.`'s sense would let the earlier area win silently, and
    # nothing winning silently is what this whole design rests on. What is
    # withdrawn is the *wake* -- the claim that a person must rule on it -- and
    # only for the one area that is a leftover bag by construction.
    # Grouped by the id family, and `.` is material but not a trigger.
    #
    # Two separate bugs, both of which shrank what the woken session was given.
    #
    # `GROUP BY term` groups on the spelling a session happened to type. The
    # plural rule in `glossary.amend` already files `intents` under the `intent`
    # id, so the two rows are one word by every part of the system except this
    # one -- and `cnt_p`'s wake for `intent` carried two of the family's four
    # rows: `intent` and `intent#src_variables`, while `intent#src_intents`
    # (term `intents`) went to a group of its own and `intent#root` was dropped
    # by the rule above. The id before `#` is the family, and it is what the
    # rest of the system already agrees on.
    #
    # And `.` stays out of the *count* while staying in the *refs*. Not raising
    # a wake over the fold-up bucket is the earned half; withholding its row
    # from a session that has been woken anyway is not. `intent#root` says
    # "template with specific action" -- wrong, and it is still one of the four
    # partial readings of the word, which is exactly what this session is for.
    # Grouped on the stemmed term, in Python, because SQLite cannot stem and
    # the id is not safe to group on.
    #
    # `GROUP BY term` groups on the spelling a session happened to type. The
    # plural rule in `glossary.amend` files `intents` under the `intent` id, so
    # the two rows are one word everywhere except here -- and `cnt_p`'s wake for
    # `intent` carried two of the family's four rows, while `intent#src_intents`
    # (term `intents`) went to a group of its own.
    #
    # Grouping on the id family instead looked equivalent and is not: it holds
    # only because `glossary.amend` derives ids from terms, and any row written
    # another way -- every fixture in the suite -- has an id that says nothing
    # about its word. Two senses of `issue_template` under `g1` and `g2` stopped
    # colliding entirely.
    #
    # And `.` stays out of the *count* while staying in the *refs*. Not raising
    # a wake over the fold-up bucket is the earned half; withholding its row
    # from a session woken anyway is not. `intent#root` says "template with
    # specific action" -- wrong, and still one of the four partial readings of
    # the word, which is exactly what that session is for.
    groups: dict[str, list] = {}
    for r in conn.execute(
            "SELECT id, term, area FROM glossary_terms WHERE superseded_by IS NULL"):
        groups.setdefault(_singular(_slug_of(r["term"])), []).append(r)

    rows = []
    for _stem, members in groups.items():
        if sum(1 for m in members if (m["area"] or "") != ".") < 2:
            continue
        rows.append({"term": members[0]["term"],
                     "ids": ",".join(sorted(m["id"] for m in members)),
                     "n": len(members)})
    if not rows:
        return []

    # A decision that resolves a parking row is not a ruling on the word. The
    # diff review of 6895000 approved the parking row on the agenda page: the
    # keypress wrote a decision whose refs name the sense, and the word went
    # quiet for ever with two live senses and no ruling. One keypress on a
    # row that says "the answer did not address the question" cannot answer
    # the question. The class is on the ledger row, not in its prose.
    ruled: set[str] = set()
    for d in conn.execute(
            "SELECT d.refs AS refs FROM decisions d "
            "LEFT JOIN ledger l ON l.id = d.resolves_ledger "
            "WHERE d.resolves_ledger IS NULL OR l.kind IS NULL "
            "OR l.kind != 'unaddressed_answer'"):
        try:
            ruled.update(json.loads(d["refs"] or "[]"))
        except (ValueError, TypeError):
            continue

    # A ruling that names the row rules it, whatever the verdict. `contest`
    # and `revise` are rulings: the principal answered, and the word is
    # settled for this cycle. Reading approvals only, through `glossary.adopt`
    # alone, sent a contest-only ruling round the loop again with no ledger
    # row and no ruling ref to stop it (the diff review of 6895000).
    from ..roles.principal import ruled as ruled_rows

    ruled.update(r["ref"] for r in ruled_rows(conn))

    # An adopted sense is ruled by the same query: `glossary.adopt` writes a
    # `refs` row of kind `ruling` and no decision (`api._adopt_rows`), and the
    # ruling it rests on names the row.
    #
    # The ruling has to name the row, not merely exist. A `ruling` ref is what
    # the provenance view reads as `decided`, and a decided sense is not a
    # ruled collision: `L1-TE-put-a-word-with-two-senses-to-the-principal`
    # seeds two decided senses and is the case this tick exists for, and
    # `test_work_resting_on_an_unresolved_collision_is_not_offered` seeds one
    # decided sense beside one observed. The fixture ruling names no row.

    # Already put to somebody. `contradiction` -- the twin this predicate was
    # built from, named two paragraphs up -- has had this check all along and
    # terminates because of it; this copied the intent and not the check.
    #
    # What that cost, measured: a survey of `.github` wrote two senses of
    # `issue_template`, correctly, because a bug-report template and a
    # feature-request template are two things. The mode's whole working set is
    # `glossary.consult`, `glossary.lookup`, `msg.report_liaison` -- it is
    # forbidden to amend here, deliberately, because collapsing two senses is a
    # decision. So the session reported, on turn 3, first opportunity, exactly
    # as briefed, and was woken again. Six sessions, three of them to the
    # 12-turn cap, 44 of the run's 71 turns. `fix` outranks `start`, so the
    # survey wakes behind it were never reached and the run produced no survey
    # record at all. `tick_agenda` states the rule for its own case: without
    # this, "it fires forever, because Liaison has no verb that could satisfy
    # it."
    #
    # Separate from `ruled` because they mean different things. A decision
    # discharges the obligation; an open message parks it, and the register
    # still carries it under `awaiting_principal`. A wake-suppression is not a
    # discharge.
    #
    # By refs rather than `contradiction`'s cruder "any open clarify exists",
    # so one reported collision does not hide every other -- and so a third
    # sense appearing joins the open case instead of raising a new one, which
    # is what happened here when a session tried to settle the word by writing
    # a merged third row.
    raised: set[str] = set()
    for m in conn.execute("SELECT body_refs FROM messages WHERE status = 'open'"):
        try:
            raised.update(json.loads(m["body_refs"] or "[]"))
        except (ValueError, TypeError):
            continue

    # brief: answering.md, an answer about something else parks the row unaddressed
    # An answer that missed the question parks the word too. The Liaison reads
    # the principal's words against the rows and finds they name none of them.
    # Nothing is ruled, so it logs one row per row and relays nothing
    # (`rota/roles/prompts/liaison/answering.md`). Night 84 (2026-09-17): the
    # report, the clarify and the relay were all answered when their sessions
    # ended, nothing was open, and the same three sessions ran seventeen
    # times. The ledger row is what holds the word between cycles.
    #
    # Parked, not discharged, as the open message above is. The row stays open
    # in the ledger and in `outstanding` until a decision resolves it, and the
    # decision names the row, so `ruled` takes over from there.
    # The class is the column, never the prose. A paraphrase of the parking
    # sentence parked nothing and wrote a new ledger row every cycle (the
    # diff review of 6895000). No predicate may rest on a model copying a
    # sentence, so the door stamps `kind` and this reads it.
    for r in conn.execute(
            "SELECT about_ref FROM ledger WHERE status = 'open' "
            "AND about_table = 'glossary_terms' "
            "AND kind = 'unaddressed_answer'"):
        raised.add(r["about_ref"])

    wakes = []
    for r in rows:
        ids = sorted(r["ids"].split(","))
        if all(i in ruled for i in ids):
            continue                      # every sense of this word is ruled
        # Every sense, not any sense. One adopted sense beside one live,
        # observed, contested sense is still a word that means two things, and
        # the only other reader of that row is `observed_entries`, which is
        # quarantined (the diff review of 6895000).
        if any(i in raised for i in ids):
            continue                      # it is already in front of somebody
        wakes.append(Wake("terminologist", "tick:term_collision",
                          refs=tuple(ids), detail=r["term"]))
    return wakes


@predicate("round_close", wakes="liaison", band="gate")
def round_close(conn) -> list[Wake]:
    """A broadcast's subtree has terminated: harvest the reports."""
    from .scheduler import tick_round_close
    return tick_round_close(conn)


@predicate("slicing", wakes="vision_keeper", band="start")
def slicing(conn) -> list[Wake]:
    """An approved item with no tickets."""
    from .scheduler import tick_slicing
    return tick_slicing(conn)


@predicate("criteria", wakes="terminologist", band="start")
def criteria(conn) -> list[Wake]:
    """Tickets with no criteria, per item."""
    from .scheduler import tick_criteria
    return tick_criteria(conn)


@predicate("grouping", wakes="architect", band="start")
def grouping(conn) -> list[Wake]:
    """
    Tickets that have criteria and belong to no batch.

    This was the hole between the two loops. `criteria` produced them and
    `batch_start` waited for batches, and nothing turned one into the other — so
    the understanding loop ran to completion and the delivery loop never began.

    Nothing caught it, because every check we had was about *states*: no state
    was unreachable and no state was undrained. A missing step between two
    reachable states is invisible to both.
    """
    # law 9: a ratified amendment drops the item to pending, stops batches
    # An abandoned batch is not a batch the ticket belongs to. S0 walk
    # thirty-one: the ladder's last rung amended the item, the revocation
    # cancelled the batch with three green tests, the item was re-approved
    # -- and its tickets still "belonged" to the abandoned batch, so nothing
    # re-grouped them and the world went quiet.
    # A described item's ticket is not grouped: a description asks for no
    # work (frame 80). The ticket may exist from before the item was described.
    # A retired ticket predates its item's amendment, so its criteria do not
    # hold the principal's words (frame 190's design, 2.F, amendment 4).
    # A ticket whose item is not approved at its version is not grouped. The
    # batch would wait behind `next_batch`'s same test, and `cancel` would
    # abandon it at once. Night 137's s321 grouped a contested item's ticket
    # twice (frame 193's design, 2.4).
    # An item set aside opens no batch (frame 193's design, 2.F.4).
    from .scheduler import live_criteria, not_described, not_parked, not_retired
    rows = conn.execute(
        "SELECT DISTINCT c.ticket_id AS tid FROM criteria c "
        "JOIN tickets t ON t.id = c.ticket_id "
        "JOIN items i ON i.id = t.item_id "
        "WHERE i.approval = 'approved' AND i.approval_ver >= i.version "
        + live_criteria(conn, "c.retired_by") + " "
        "  AND c.ticket_id NOT IN (SELECT bt.ticket_id FROM batch_tickets bt "
        "                          JOIN batches b ON b.id = bt.batch_id "
        "                          WHERE b.status != 'abandoned')"
        + not_described(conn, "c.ticket_id", of="ticket")
        + not_retired(conn, "c.ticket_id")
        + not_parked(conn, "c.ticket_id", of="ticket")
    ).fetchall()
    if not rows:
        return []
    return [Wake("architect", "tick:grouping",
                 refs=tuple(r["tid"] for r in rows))]


def groupable_tickets(conn) -> list[str]:
    """The tickets the grouping wakes for. `batches.group` reads the same set,
    so its refusal names only tickets the wake would carry (frame 193's
    review of pass 1, finding 1)."""
    wakes = grouping(conn)
    return list(wakes[0].refs) if wakes else []


@predicate("observed_entries", wakes="liaison", band="start",
           # The code half of observed: a row whose refs reach a grain and
           # nothing stronger. The views stand over `refs`; no owner table
           # carries the word.
           drains=[("term_provenance", "basis", "code"),
                   ("constraint_provenance", "basis", "code"),
                   ("area_provenance", "basis", "code"),
                   ("item_provenance", "basis", "code")])
def observed_entries(conn) -> list[Wake]:
    """
    Entries extracted from a codebase, awaiting their first decision.

    Onboarding produces these by the hundred and nothing was ever going to ask
    the principal to confirm them, so `observed` was a state with no exit.

    Not before onboarding is done. Fired mid-onboarding, each wake carried
    the one or two rows written since the last, and the principal saw the
    same page sixteen times on one run (tipsM, 2026-09-09). One page, once
    the rows are all there. `none` is a run with nothing onboarded, where
    the rows can only be fixture rows.
    """
    from .scheduler import onboarding_phase

    if onboarding_phase(conn) not in ("done", "none"):
        return []
    # Not re-presented. With the confirm path built, an approved row leaves
    # `observed`; a contested one stays, and it is on file as contested --
    # asking the principal about it again is spending their attention on a
    # question they have answered. Presented is derived from the present
    # messages themselves, so a row is put to them once, whatever came of it.
    presented: set[str] = set()
    for r in conn.execute(
            "SELECT body_refs FROM messages WHERE verb = 'present'"):
        try:
            presented.update(x for x in json.loads(r["body_refs"] or "[]")
                             if isinstance(x, str))
        except (TypeError, ValueError):
            continue

    # The code half of observed only. A row that rests on the world (a
    # reference) is cited, and a cited row was never put to the principal.
    from .db import PROVENANCE_VIEW_OF_TABLE

    counts, offered, owed = [], [], []
    noted = resurvey_noted(conn)
    for table in ("glossary_terms", "constraints", "model_areas", "items"):
        view = PROVENANCE_VIEW_OF_TABLE[table]
        # One id once. The view can hold a row twice, and the eager wake of
        # dry3w7 carried 240 refs for 223 rows (review p1 of frame 361, 8).
        rows = list(dict.fromkeys(r["id"] for r in conn.execute(
            f"SELECT id FROM {view} WHERE basis = 'code' ORDER BY id")))
        # A re-survey after a merge is no onboarding, so its rows go to the
        # ledger and not to a page. Night 175's m145 put 15 such notes to the
        # principal with nothing to build (frame 358).
        late = resurvey_rows(conn, table, rows)
        owed += [i for i in rows if i in late and i not in noted]
        fresh = [i for i in rows if i not in presented and i not in late]
        # An id in two tables is one ref on the wake.
        fresh = [i for i in fresh if i not in offered]
        if fresh:
            counts.append(f"{table}:{len(fresh)}")
            offered += fresh
    if owed:
        return [Wake(SCHEDULER, "do:resurvey_note", refs=tuple(owed),
                     detail=f"re-survey rows after a merge: {len(owed)}")]
    # A deferral is an election. A present answered without a ruling -- the
    # principal read it and moved on -- left its rows in limbo: not decided,
    # not ledgered, and never re-offered, because a row is put to them once.
    # The put-once rule assumed a ruling always comes. It does not, and the
    # lazy path is what deferral *means*: those rows become assumptions
    # awaiting first touch, exactly as if the election had said so, without
    # re-spending the attention that was already declined.
    from .lifecycle import touch_notes

    # A touch note answered is read, not deferred: its refs are a batch and
    # an item the principal already ruled on, and an acknowledgement lands no
    # verdict on purpose (P4, 2026-09-03). Counting it here would log the
    # item as a baseline deferral it never was.
    notes = touch_notes(conn, status=None)
    limbo = []
    for r in conn.execute(
            "SELECT m.id, m.body_refs FROM messages m WHERE m.verb='present' "
            "AND m.status='answered' AND NOT EXISTS ("
            "  SELECT 1 FROM messages v WHERE v.cause_id = m.id "
            "    AND v.verb = 'verdict')"):
        if r["id"] in notes:
            continue
        try:
            limbo += [x for x in json.loads(r["body_refs"] or "[]")
                      if isinstance(x, str)]
        except (TypeError, ValueError):
            continue
    if limbo:
        deferred = {r["about_ref"] for r in conn.execute(
            "SELECT about_ref FROM ledger")}
        from ..roles.principal import principal_objects
        from .db import tables_of

        # `db.tables_of` finds the tables that hold the id (F22). The basis
        # is then read in the provenance view of each one. A row that holds
        # his drop has his answer, so it is not deferred without a ruling
        # (ruled: Roman, 2026-11-02 11:43, frame 357, shape B).
        # A re-survey row is on file in its own ledger row already. Its
        # about_ref is the item, so `deferred` misses it (review p1 of
        # frame 358, finding 1).
        deferred |= resurvey_noted(conn)
        still = [i for i in dict.fromkeys(limbo)
                 if i in presented and i not in deferred
                 and not principal_objects(conn, i) and any(
                     conn.execute(f"SELECT 1 FROM {PROVENANCE_VIEW_OF_TABLE[t]} "
                                  f"WHERE id = ? AND basis = 'code'", (i,)).fetchone()
                     for t in tables_of(conn, i, among=(
                         "glossary_terms", "constraints", "model_areas",
                         "items")))]
        if still:
            return [Wake(SCHEDULER, "do:defer_baseline", refs=tuple(still),
                         detail=f"deferred without ruling: {len(still)}")]

    if not counts:
        return []
    # The election. "Confirm the whole baseline up front, or lazily as work
    # first touches each area" -- the principal's call, and recorded as
    # config by the seat because it is literally theirs: no session decides
    # it, interprets it, or writes it. Under `lazy`, the offer becomes
    # clerical deferral -- a scheduler action, like constraint zero's
    # bindings, because logging "this observation is unconfirmed" has no
    # judgement in it for a session to get wrong. Rows already deferred are
    # excluded the same way presented ones are: the ledger row is the record.
    # No ruling reads as `lazy`, and an empty value reads the same (ruled:
    # Roman, 2026-11-03 01:05). `config.get` holds both rules, so one reader
    # decides (review p1 of frame 361, finding 7). A bare word written past
    # the registry is not JSON, and it reads as the word.
    from . import config as config_mod

    try:
        election = config_mod.get(conn, "baseline_election")
    except ValueError:
        election = conn.execute(
            "SELECT value FROM config WHERE key = 'baseline_election'"
        ).fetchone()["value"].strip('"')
    if election == "lazy":
        deferred = {r["about_ref"] for r in conn.execute(
            "SELECT about_ref FROM ledger")}
        fresh = [i for i in offered if i not in deferred]
        return [Wake(SCHEDULER, "do:defer_baseline", refs=tuple(fresh),
                     detail=", ".join(counts))] if fresh else []

    # An open touch note is not an open ask: nothing waits on it (R7), so it
    # cannot be the reason the baseline is withheld.
    asked = conn.execute(
        "SELECT COUNT(*) n FROM messages WHERE status='open' AND to_role='principal' "
        "AND verb='present'").fetchone()["n"] - len(touch_notes(conn))
    # The ids ride the wake. Liaison's `observed_entries` mode holds one send
    # and no read that could enumerate these tables -- live, woken with counts
    # alone, it was asked to name 91 rows it cannot see, invented a dict ref,
    # and the present never went out. The predicate counted the rows; it names
    # them.
    return [] if asked else [
        Wake("liaison", "tick:observed_entries", refs=tuple(offered),
             detail=", ".join(counts))]


# The words of the one ledger row per re-survey after a merge. The refs
# follow as JSON, so the predicate reads back which rows the row holds.
RESURVEY_WORDS = "After the merge the team re-read the project and recorded these notes: "

# The words that open each row the lazy election defers. The prefix is the
# mark: the agenda leaves these rows out, and the touch note shows them at
# their first touch (frame 361). No column carries the mark, so an older
# run database keeps its schema.
LAZY_WORDS = "observed and unconfirmed under the lazy election: "

# The words of the one parked ledger row per touch note that showed lazy
# rows. The JSON after them names the batch and the rows it showed, so a row
# is shown once and its note shows it again on every render (frame 361).
FIRST_TOUCH_WORDS = "Shown at the first touch of a change: "


def lazy_count(conn) -> int:
    """The count of the lazy rows that still wait for their first touch."""
    return conn.execute(
        "SELECT COUNT(*) FROM ledger WHERE status = 'open' "
        "AND substr(default_taken, 1, ?) = ?",
        (len(LAZY_WORDS), LAZY_WORDS)).fetchone()[0]


def resurvey_rows(conn, table: str, ids: list[str]) -> dict[str, str]:
    """The rows of `ids` that a re-survey after a merge wrote, each mapped to
    the merged batch it followed.

    No column dates a merge, and no column dates a row. The receipts date
    both by session seq. A batch's date is the seq of its first receipt. A
    row's date is the seq of the session that first wrote it.

    A row is a re-survey row when a `tick:survey` session wrote it after the
    first merged batch's date. The delivery loop waits for onboarding, so
    no batch exists while the first onboarding writes. A row with no
    receipt is an onboarding row, as before."""
    if not ids:
        return {}
    merged = conn.execute(
        "SELECT b.id, b.item_id, MIN(s.seq) AS seq FROM batches b "
        "JOIN receipts r ON r.table_name = 'batches' AND r.row_id = b.id "
        "JOIN sessions s ON s.id = r.session_id "
        "WHERE b.status = 'merged' GROUP BY b.id ORDER BY seq").fetchall()
    if not merged:
        return {}
    first = conn.execute(
        # SQLite gives the bare column of the row that holds the MIN.
        "SELECT r.row_id AS id, MIN(s.seq) AS seq, s.wake_kind AS kind "
        "FROM receipts r JOIN sessions s ON s.id = r.session_id "
        "WHERE r.table_name = ? GROUP BY r.row_id", (table,)).fetchall()
    out: dict[str, str] = {}
    wanted = set(ids)
    for r in first:
        # A survey session only. A challenge after a merge is no re-read of
        # the project, so its row still pages (review p1 of frame 358,
        # finding 2).
        if (r["id"] not in wanted or r["kind"] != "tick:survey"
                or r["seq"] is None or r["seq"] <= merged[0]["seq"]):
            continue
        # The latest merged batch dated before the row is the merge it followed.
        out[r["id"]] = [b["id"] for b in merged if b["seq"] < r["seq"]][-1]
    return out


def resurvey_noted(conn) -> set[str]:
    """The refs that the re-survey ledger rows already hold."""
    held: set[str] = set()
    for r in conn.execute("SELECT default_taken FROM ledger "
                          "WHERE substr(default_taken, 1, ?) = ?",
                          (len(RESURVEY_WORDS), RESURVEY_WORDS)):
        try:
            held.update(json.loads(r["default_taken"][len(RESURVEY_WORDS):]))
        except (TypeError, ValueError):
            continue
    return held


def resurvey_note(conn) -> list[str]:
    """Write one ledger row per merge for the re-survey rows no row holds yet.

    The row is `parked`: no page shows it, and the state view counts it
    (frame 204's design, section 4). Its about_ref is the merged item, so
    `ledger.list(shipped=...)` shows its words. Return the ledger ids."""
    import hashlib

    from .db import PROVENANCE_VIEW_OF_TABLE

    noted = resurvey_noted(conn)
    by_batch: dict[str, list[str]] = {}
    for table in ("glossary_terms", "constraints", "model_areas", "items"):
        rows = [r["id"] for r in conn.execute(
            f"SELECT id FROM {PROVENANCE_VIEW_OF_TABLE[table]} "
            "WHERE basis = 'code' ORDER BY id")]
        for ref, batch in resurvey_rows(conn, table, rows).items():
            if ref not in noted:
                by_batch.setdefault(batch, []).append(ref)
    written = []
    for batch, refs in by_batch.items():
        item = conn.execute("SELECT item_id FROM batches WHERE id = ?",
                            (batch,)).fetchone()["item_id"]
        words = RESURVEY_WORDS + json.dumps(sorted(refs))
        lid = "l_" + hashlib.sha256(f"items|{item}|{words}".encode()).hexdigest()[:10]
        conn.execute(
            "INSERT OR IGNORE INTO ledger (id, about_ref, about_table, "
            "default_taken, kind, status, author) VALUES (?, ?, 'items', ?, "
            "'other', 'parked', 'scheduler')", (lid, item, words))
        written.append(lid)
    return written


def resurvey_count(conn) -> int:
    """The count of notes that the re-survey ledger rows hold."""
    return len(resurvey_noted(conn))


# ---------------------------------------------------------------------------
# Delivery loop — one predicate existed; these are the rest
# ---------------------------------------------------------------------------

@predicate("tests_missing", wakes="tester", band="start")
def tests_missing(conn) -> list[Wake]:
    """Criteria for a batch with no tests, after the Developer has committed.

    The Tester ran as soon as criteria existed, before the Developer. On a
    greenfield batch there is nothing to call. Every test the Tester could
    write asserted a constant it had just assigned. The encode door refused
    each one. Measured as the principal on three walks (2026-09-04): six of
    seven tests red, no program, and a question to the principal that the
    criteria had already answered.

    The Tester now waits for `head_commit`. It stays black-box. Criteria are
    still its only material. The thing the criterion names now exists to be
    imported and called. The criteria are the specification, written by
    another role before this. The order of these two roles does not change
    them. `batch_start` needs no tests, so nothing deadlocks.
    """
    # law 8: gates are predicates, not judgement
    # Per criterion, not per batch. Walk nine: four criteria, three encodes
    # refused at the harness-fact bar, one landed -- and the batch never
    # woke the Tester again, because "a batch with no tests" had one. The
    # fork is per criterion, so the debt is: a criterion with no test and no
    # open question of the Tester's about it (routed is done; the answer
    # wakes it).
    # The wake names the criteria it is about. clickI night 46 (2026-09-14):
    # shown six criteria and three tests, the Tester re-encoded the three
    # that had tests and asked the Terminologist about one that had none.
    # A retired ticket's criteria owe no test (frame 190's design, 2.F,
    # amendment 4).
    # A test counts for its own batch only. Night 147, walk 2: bg_2 was
    # abandoned with three tests, and bg_3 took its criteria. Those tests
    # satisfied the NOT EXISTS, so this predicate gave no wake. bg_3 merged
    # with no test of its own (frame 239).
    # A retired criterion owes no test either (frame 306, pass 1b). A test he
    # retired encodes nothing, so its criterion owes a test again (frame 306,
    # W-A, review medium 2).
    from .scheduler import live_criteria, live_tests, not_retired
    rows = conn.execute(
        "SELECT bt.batch_id AS bid, c.id AS cid FROM batch_tickets bt "
        "JOIN batches b ON b.id = bt.batch_id "
        "JOIN criteria c ON c.ticket_id = bt.ticket_id "
        "WHERE b.status = 'running' "
        "  AND b.head_commit IS NOT NULL AND b.head_commit != '' "
        "  AND NOT EXISTS (SELECT 1 FROM tests t WHERE t.criterion_id = c.id "
        "                  AND t.batch_id = bt.batch_id" + live_tests(conn, "t.id")
        + ") "
        "  AND NOT EXISTS (SELECT 1 FROM messages m WHERE m.from_role = 'tester' "
        "                  AND m.verb = 'question' AND m.status IN ('open', 'unresolved') "
        "                  AND m.body_refs LIKE '%\"' || c.id || '\"%') "
        + not_retired(conn, "bt.ticket_id") + live_criteria(conn, "c.retired_by")
        + " ORDER BY bt.batch_id, c.id"
    ).fetchall()
    missing: dict[str, list[str]] = {}
    claimed = _claimed_batches(conn)
    for r in rows:
        # The Tester of a claim waits for the Architect's run, so it reads
        # the printout before it writes a test (frame 360, shape H1, RA F12).
        # A wait on a seat, which frame 204's design keeps.
        if r["bid"] in claimed and not claim_settled(conn, r["bid"]):
            continue
        missing.setdefault(r["bid"], []).append(r["cid"])
    return [Wake("tester", "tick:tests_missing", refs=(bid,),
                 detail="without a test: " + ", ".join(cids)
                 + ("\n" + CLAIM_DETAIL if bid in claimed else ""))
            for bid, cids in missing.items()]


# Run 1 of frame 362: s153 was not told of the claim, and its three tests
# passed on the code as it was. So the Tester of a claimed batch is told,
# and its tests decide the claim (plans/design-false-claim-2026-11-06.md,
# Revision R2 F). Shape H1 makes the Architect's run evidence too, so the
# sentence names the run (review p1 of frame 360, finding 9).
CLAIM_DETAIL = ("No code changed on this batch. The Developer claims that the "
                "code as it is already meets each criterion. The Architect's "
                "run of the code and your tests decide the claim.")


def _claimed_batches(conn) -> set[str]:
    """The batches whose head is a claim. Equality is the only test of a
    claim, because a later real commit leaves no claim (review p1, F7)."""
    from .db import _has_column

    if not _has_column(conn, "batches", "claimed_head"):
        return set()
    return {r[0] for r in conn.execute(
        "SELECT id FROM batches WHERE claimed_head IS NOT NULL "
        "AND claimed_head = head_commit")}


def claim_settled(conn, batch_id: str) -> bool:
    """The claim of `batch_id` has a run on record, or its `tick:claim`
    session ended. The key is the batch, because `boot.py` moves the
    claimed head to the merge's tests commit (frame 360, RA F12)."""
    has_runs = conn.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' "
                            "AND name = 'claim_runs'").fetchone()
    if has_runs and conn.execute(
            "SELECT 1 FROM claim_runs WHERE batch_id = ? LIMIT 1",
            (batch_id,)).fetchone():
        return True
    # A session row exists only for a session that ended, committed or not.
    if conn.execute(
            "SELECT 1 FROM sessions s, json_each(s.wake_refs) j "
            "WHERE s.wake_kind = 'tick:claim' AND j.value = ? LIMIT 1",
            (batch_id,)).fetchone() is not None:
        return True
    # The attempt cap can quarantine the key before any session row exists.
    # The Tester then never woke on the batch (review p1 of frame 360,
    # finding 8).
    from .scheduler import quarantined_keys

    return bool(quarantined_keys(conn, batch_id, kind="tick:claim"))


def _is_test_path(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return ("/tests/" in "/" + path or name.startswith("test_")
            or name.endswith("_test.py") or name == "conftest.py")


def claim_touch(conn, batch_id: str) -> dict:
    """The touch of a claimed batch: the expected files, the source files
    among them, and the symbols that the wake names.

    A symbol is a `symbol` row of `batch_touch`, or a definition in a source
    file of the touch whose name holds a word of the request. The probe's
    wake named `_foldline` this way (frame 360, H5)."""
    rows = conn.execute(
        "SELECT grain, grain_kind FROM batch_touch WHERE batch_id = ? "
        "AND confidence = 'expected' ORDER BY rowid", (batch_id,)).fetchall()
    files = [r["grain"] for r in rows if r["grain_kind"] == "path"]
    symbols = [r["grain"] for r in rows if r["grain_kind"] == "symbol"]
    for grain in symbols:
        path = grain.split("::", 1)[0]
        if path not in files:
            files.append(path)
    sources = [f for f in files if f.endswith(".py") and not _is_test_path(f)]
    words = set(re.findall(r"[a-z]{4,}", claim_request(conn, batch_id).lower()))
    for path in sources:
        for r in conn.execute(
                "SELECT grain FROM code_index WHERE grain LIKE ? AND "
                "grain_kind = 'symbol' ORDER BY line_start",
                (path.replace("%", "") + "::%",)):
            name = r["grain"].split("::", 1)[1]
            if (r["grain"] not in symbols and "." not in name
                    and any(w in name.lower() for w in words)):
                symbols.append(r["grain"])
    return {"files": files, "sources": sources, "symbols": symbols}


def claim_request(conn, batch_id: str) -> str:
    row = conn.execute("SELECT i.text FROM items i JOIN batches b ON "
                       "b.item_id = i.id WHERE b.id = ?", (batch_id,)).fetchone()
    return (row["text"] or "") if row else ""


def claim_wake_detail(conn, batch_id: str) -> str:
    """The request, the touch and the act, in the words of H1's wake."""
    touch = claim_touch(conn, batch_id)
    named = ", ".join(touch["files"] + [
        f"`{g.split('::', 1)[1]}` in {g.split('::', 1)[0]}"
        for g in touch["symbols"]]) or "no file is named"
    return ("The Developer changed no code and says that the request is "
            f"already true of the code. The request: "
            f"\"{claim_request(conn, batch_id)}\". The touch: {named}.\n"
            "Show what the code does with one run. Import the function of the "
            "touch from its module, call it with one example from the request, "
            "and print the input and the result. Send the program with "
            "code.run(text). The run is the record.")


@predicate("claim", wakes="architect", band="start")
def claim(conn) -> list[Wake]:
    """
    A claimed batch with no run of its code on record.

    Frame 360, shape H1 (ruled: Roman, 2026-11-08 10:01, "Yes, it closes
    with approval"). On dry run 6b the Developer said "already done", three
    tests passed on the old code, and the claim merged false. The Architect
    runs one program at the touch, and the door records what it printed.
    One wake per batch: an ended `tick:claim` session settles it, run or no
    run. The Tester's `tests_missing` waits for it.
    """
    rows = conn.execute(
        "SELECT id FROM batches WHERE status = 'running' ORDER BY id").fetchall()
    claimed = _claimed_batches(conn)
    return [Wake("architect", "tick:claim", refs=(r["id"],),
                 detail=claim_wake_detail(conn, r["id"]))
            for r in rows
            if r["id"] in claimed and not claim_settled(conn, r["id"])]


@predicate("harness", wakes=SCHEDULER, band="gate",
           drains=[("test_runs", "result", "error")])
def harness(conn) -> list[Wake]:
    """
    A batch with tests and a commit, whose tests have not been run against it.

    An action, not a wake: running tests is the one gate with no judgement in it.
    It is also the first gate, because it is the cheapest — a subprocess against
    a model call — which is what makes `loop_cap` bounces affordable enough to
    be the normal way a batch converges rather than a failure path.

    `head_commit` is the guard against re-running: a commit that has already
    been tested has its results, and the Developer committing again is what asks
    for another attempt. Matching on the *commit* rather than on the batch is
    what makes that true — the first version asked whether any run existed, so
    a batch was tested once and never again.
    """
    # Per test, not per batch. S0 walk eighteen: the Tester re-encoded the
    # one failing test with the input fed in, and it never ran -- the batch
    # already had runs at this commit, so the gate was satisfied while every
    # later session read the stale result. A test with no run at the head
    # commit is owed one, whichever side moved. The newest run says it: a
    # run at the head that a later run superseded is no run of the head now.
    rows = conn.execute(
        "SELECT DISTINCT b.id AS bid FROM batches b JOIN tests t ON t.batch_id = b.id "
        "WHERE b.status = 'running' AND b.head_commit IS NOT NULL "
        "  AND NOT EXISTS (SELECT 1 FROM latest_runs r "
        "                  WHERE r.batch_id = b.id AND r.commit_sha = b.head_commit "
        "                    AND r.test_id = t.id)"
        # The harness run skips a test of a retired criterion, so that test
        # owes no run. Without this line the harness fires for ever (frame
        # 306, pass 2b).
        + live_tests(conn, "t.id")
    ).fetchall()
    return [Wake("", "do:harness", refs=(r["bid"],)) for r in rows]


@predicate("annotate", wakes="architect", band="start")
def annotate(conn) -> list[Wake]:
    """
    A batch with no expected touch set.

    One batch at a time and deliberately separate from grouping: grouping is
    cheap and index-only, annotating reads source, and doing every batch in one
    session would exhaust the context that makes the annotation worth having.
    """
    # An owed contest of his holds the batch's plan. On the guess line the
    # guess comes first: dry run 6b's s150 copied the guess he called wrong.
    # On the batch line the tick carries the verdict (frame 362).
    from .scheduler import owed, owed_in_flight, owed_park

    for r in conn.execute("SELECT id FROM batches WHERE status IN "
                          "('pending','deferred') ORDER BY rowid").fetchall():
        found = owed(conn, r["id"])
        if found is None:
            continue
        if (found["line"] == "batch" and found["ref"] == r["id"]
                and not owed_in_flight(conn, found["verdict"])
                and not owed_park(conn, r["id"])):
            return [Wake("architect", "tick:annotate", refs=(r["id"], found["verdict"]))]
    rows = conn.execute(
        "SELECT id FROM batches WHERE status IN ('pending','deferred') "
        "  AND id NOT IN (SELECT DISTINCT batch_id FROM batch_touch)"
    ).fetchall()
    rows = [r for r in rows if owed(conn, r["id"]) is None][:1]
    return [Wake("architect", "tick:annotate", refs=(r["id"],)) for r in rows]


@predicate("touch_note", wakes="liaison", band="start")
def touch_note(conn) -> list[Wake]:
    """
    A batch's predicted touch, owed to the principal until presented.

    P4 (ruled R16/R17, 2026-09-03): the modification scope is put to the
    seat as a sense check before the batch builds -- the paths the Architect
    expects, the symbols it only guesses, the touched ground nobody surveyed,
    the commitments bound to it. Register-shaped: presented is derived from
    the presents themselves, so a batch is put to them once whatever came of
    it. Non-blocking by R7: `batch_start` never waits on the answer -- the
    file order merely offers the note first -- and a batch that got ahead is
    still owed its note, because the levers the note exists for (reorder,
    interrupt, contest the item) act on a running batch too. The refs are
    the batch and its item, and they ride the present mechanically.
    """
    from .db import refs_of
    from .scheduler import not_parked

    presented: set[str] = set()
    for r in conn.execute("SELECT body_refs FROM messages WHERE verb = 'present'"):
        presented.update(refs_of(r["body_refs"]))
    rows = conn.execute(
        "SELECT b.id AS id, b.item_id AS item, "
        "       SUM(t.confidence = 'expected') AS expected, "
        "       SUM(t.confidence != 'expected') AS possible "
        "FROM batches b JOIN batch_touch t ON t.batch_id = b.id "
        "WHERE b.status IN ('pending', 'deferred', 'running') "
        # A set-aside item's batch owes no page while it waits (2.F.4).
        + not_parked(conn, "b.item_id") +
        "GROUP BY b.id ORDER BY b.id"
    ).fetchall()
    # A presented note showed the lazy rows bound to its touch, so the clerk
    # takes them out of the open set. Its page reads them from the record
    # after that, and the next note on the same ground names none of them
    # (frame 361).
    from .lifecycle import first_touch_rows, first_touch_shown
    from .scheduler import owed

    # A set that he contested and nobody rewrote is no plan to show him.
    # Dry run 6b's m31 showed him the guess he had called wrong (frame 362).
    rows = [r for r in rows if owed(conn, r["id"]) is None]
    for r in rows:
        if r["id"] in presented and first_touch_shown(conn, r["id"]) is None:
            shown = first_touch_rows(conn, r["id"])
            if shown:
                return [Wake(SCHEDULER, "do:first_touch",
                             refs=(r["id"], *shown),
                             detail=f"lazy rows shown at first touch: {len(shown)}")]
    return [Wake("liaison", "tick:touch_note", refs=(r["id"], r["item"]),
                 detail=f"expected {r['expected']}, possible {r['possible']}")
            for r in rows if r["id"] not in presented]


@predicate("batch_start", wakes="developer", band="start",
           drains=[("batches", "status", "pending"),
                   ("batches", "status", "deferred")])
def batch_start(conn) -> list[Wake]:
    """Next schedulable batch, nothing running."""
    from .scheduler import tick_batch_start
    return tick_batch_start(conn)


@predicate("tests_failing", wakes="developer", band="fix",
           drains=[("test_runs", "result", "fail"), ("test_runs", "result", "error")])
def tests_failing(conn) -> list[Wake]:
    """A failing test goes straight back, capped. This *is* the cheap loop —
    a test costs a subprocess, so it bounces rather than waiting for review.

    The cap was a literal `10` sitting here, which made it a decision nobody
    could find and nobody could change. It is `loop_cap` now, and it spends
    compute — which is why it is generous, and why it is not the same number as
    the cap on interrupting the principal."""
    from . import config

    cap = config.get(conn, "loop_cap")
    # A test's *latest* run is its result. S0 walk nineteen: all four tests
    # passed at step 84 and the Developer was woken anyway, on a fail row
    # from an earlier run of the same batch, rewrote working code and broke
    # it. A pass supersedes the fail before it; only the newest row per
    # test says anything.
    # A running batch only. A deferred batch's failures wait for its resume.
    # The harness tests running batches only. A revived key of a deferred
    # batch then loops without a bound (observed: the design review of frame
    # 83, 2026-09-24).
    # A test red at the base is not the Developer's red. It woke him at
    # every commit (review of frame 362, pass 5b, finding 10).
    from .harness import drop_base_reds

    reds = drop_base_reds(conn, conn.execute(
        "SELECT r.batch_id, r.test_id, r.output, r.attempt FROM latest_runs r "
        "JOIN batches b ON b.id = r.batch_id AND b.status = 'running' "
        "WHERE r.result IN ('fail','error') "
        # A red test of a retired criterion wakes no fix. Night 163 looped
        # on the stop page that such a red led to (frame 306, pass 2b).
        + live_tests(conn, "r.test_id") +
        " ORDER BY r.batch_id"
    ).fetchall())
    # The highest attempt per batch. SQL's MAX skipped a NULL attempt.
    att: dict[str, int | None] = {}
    for r in reds:
        had, now = att.get(r["batch_id"]), r["attempt"]
        att[r["batch_id"]] = now if had is None else had if now is None else max(had, now)
    # The challenge bound of `stopped_bouncing` ends the fix loop too, or
    # the wake holds the frontier and `quiet_park` never fires below the
    # cap (review p1 of frame 278, H1).
    from .scheduler import challenged_reds

    return [Wake("developer", "tick:tests_failing", refs=(bid,),
                 detail=f"attempt {a}")
            for bid, a in att.items() if (a or 1) < cap
            and not challenged_reds(conn, bid)]


@predicate("reopen", wakes="developer", band="fix",
           drains=[("batches", "status", "running"),
                   ("batches", "status", "deferred")])
def reopen(conn) -> list[Wake]:
    """
    A batch whose item stopped being approved under it.

    Revocation had one half. `batch_start` refuses to *start* a batch whose item
    is no longer approved, and nothing at all happened to one already running —
    so the Developer kept building against a withdrawn specification, Critic
    judged it against withdrawn criteria, and it merged. The half that was
    missing is the expensive one, because it is the only case where work is
    actively being done against something nobody wants any more.

    `reopen` had a graph edge and a prompt file describing the election in
    detail, and no producer. This is it.

    It goes quiet once the election is in flight: the Developer answers with
    `msg.elect_vision_keeper`, and re-asking while that message is unread would put
    the same decision on the frontier every pass.
    """
    rows = conn.execute(
        "SELECT b.id AS bid, b.item_id AS iid FROM batches b "
        "JOIN items i ON i.id = b.item_id "
        "WHERE b.status IN ('running','deferred') "
        "  AND (i.approval != 'approved' OR i.approval_ver < i.version) "
        "  AND NOT EXISTS (SELECT 1 FROM messages m "
        "                  WHERE m.from_role = 'developer' AND m.verb = 'elect' "
        "                    AND m.body_refs LIKE '%' || b.id || '%')"
    ).fetchall()
    return [Wake("developer", "tick:reopen", refs=(r["bid"], r["iid"]))
            for r in rows]


@predicate("exhausted", wakes=DERIVED, band="fix", derives=LADDER,
           drains=[("test_runs", "result", "fail")])
def exhausted(conn) -> list[Wake]:
    """
    A batch that stopped bouncing: it hit `loop_cap`, or the tick quarantine
    took a key of it that `given_up` lists while it runs.

    `tests_failing` goes quiet above the cap, which on its own is abandonment
    wearing the clothes of a budget: the work is still undone, nothing fires,
    and the system reports itself quiescent. Exhaustion escalates instead.

    One rung at a time, because the usual *reason* a loop exhausts itself is not
    knowing who to ask — and handing it straight to the principal skips the two
    people who could have answered it. The rung derives from the sessions the
    exhaustion opened. Nothing stores it. A stored rung is a second record, and
    it can disagree with the wakes.
    """
    from . import config

    # Law 6, amended 2026-09-24 (frame 79): the seat tries an answer before the
    # ladder climbs. The Developer is single-instance. One batch runs at a time.
    # The guard reads no refs. Any open message to the Developer holds the ladder.
    if conn.execute("SELECT 1 FROM messages WHERE to_role = 'developer' "
                    "AND status = 'open' LIMIT 1").fetchone():
        return []

    cap = config.get(conn, "loop_cap")
    from .harness import drop_base_reds

    rows = [{"bid": r["batch_id"]} for r in drop_base_reds(conn, conn.execute(
        # Each test's latest run only, like tests_failing: a fail that a later
        # pass superseded is not an attempt still failing (2026-09-16 review).
        "SELECT batch_id, test_id, output FROM latest_runs "
        "WHERE result IN ('fail','error') "
        # A retired criterion's red climbs no ladder (frame 306, pass 2b).
        + live_tests(conn, "test_id")
    ).fetchall())]
    # A test red at the base climbs no ladder (review of frame 362, pass 5b,
    # finding 10). `failing_attempt` reads the same rule for the cap.

    from .scheduler import failing_attempt, stop_detail, stopped_bouncing

    # A running batch stops on any key that `given_up` lists, and a green
    # batch has no failing test. Night 169's batch ran with no commit and
    # no test (frame 330, pass 5).
    bids = sorted({r["bid"] for r in rows} | {r["id"] for r in conn.execute(
        "SELECT id FROM batches WHERE status = 'running'")})
    wakes = []
    for bid in bids:
        # Law 6: the first budget that runs out climbs the ladder, a seat
        # key's cap of 3 too (frame 330).
        if not stopped_bouncing(conn, bid):
            continue                       # still bouncing; its seat has it
        role = _next_rung(conn, bid)
        if role:
            wakes.append(Wake(role, "tick:exhausted", refs=(bid,),
                              detail=stop_detail(conn, bid)
                              # The gate's own count, so the text is true.
                              or f"attempt {failing_attempt(conn, bid)} of {cap}"))
    return wakes


@predicate("findings_exhausted", wakes=DERIVED, band="fix", derives=LADDER)
def findings_exhausted(conn) -> list[Wake]:
    """
    A batch whose findings loop hit `loop_cap`: the same ladder as `exhausted`.

    `finding_violated` goes quiet at `loop_cap` upheld rounds, and the batch
    stayed running and woke nobody (frame 88's diff review, 2026-09-27). A
    batch that `exhausted` wakes for its tests is left to that ladder.
    """
    from . import config
    from ..onboarding.boot import ZERO

    woken = {w.refs[0] for w in exhausted(conn)}
    # The same hold as `exhausted`: the seat tries an answer first (law 6).
    if conn.execute("SELECT 1 FROM messages WHERE to_role = 'developer' "
                    "AND status = 'open' LIMIT 1").fetchone():
        return []
    cap = config.get(conn, "loop_cap")
    wakes = []
    for r in conn.execute(
            "SELECT b.id AS bid, "
            "  (SELECT COUNT(DISTINCT fr.commit_sha) FROM finding_rulings fr "
            "   JOIN findings f2 ON f2.id = fr.finding_id "
            "   WHERE f2.batch_id = b.id AND fr.ruling = 'upheld') AS rounds "
            "FROM batches b "
            "WHERE b.status = 'running' AND b.head_commit IS NOT NULL "
            f"  AND EXISTS (SELECT 1 FROM findings f WHERE {_VIOLATED_AT_HEAD} "
            f"              AND EXISTS ({_RULED_AT_HEAD} AND fr.ruling = 'upheld')) "
            # The same guard as `finding_violated`: the Critic rules on every
            # finding at head first, so its review and this never share a tick.
            f"  AND NOT EXISTS (SELECT 1 FROM findings f WHERE {_VIOLATED_AT_HEAD} "
            f"                  AND NOT EXISTS ({_RULED_AT_HEAD})) "
            "ORDER BY b.id", (ZERO, ZERO)).fetchall():
        if r["rounds"] < cap or r["bid"] in woken:
            continue                       # finding_violated still has it
        role = _next_rung(conn, r["bid"])
        if not role:
            continue
        # The Developer's `exhausted` brief says the tests are red, and here
        # they are green. So its rung has its own mode. The upper rungs' briefs
        # speak of a batch out of loop, which holds for either loop.
        kind = ("tick:findings_exhausted" if role == "developer"
                else "tick:exhausted")
        detail = _upheld_detail(conn, r["bid"], r["rounds"]).replace(
            f"round {r['rounds']}", f"cap {cap} reached", 1)
        wakes.append(Wake(role, kind, refs=(r["bid"],), detail=detail))
    return wakes


def _next_rung(conn, batch_id: str) -> str:
    """
    Who has not yet been asked about this batch.

    Empty once it has reached Vision Keeper, who is the last rung that can be woken
    — above that is the principal, and reaching them is Liaison's `report`, which
    Vision Keeper's own session sends. Nothing wakes a person.

    A role is asked once a committed session on `tick:exhausted` names this
    batch. The runner stamps `wake_refs` from the wake. A message carries the
    refs the model passed. The id is quoted, so `b1` never matches `b10`.
    """
    # `tick:findings_exhausted` is the Developer's rung of the same ladder
    # when the findings loop ran out (frame 88), so it counts as asked.
    asked = {r["role"] for r in conn.execute(
        "SELECT DISTINCT role FROM sessions WHERE wake_kind IN "
        "('tick:exhausted', 'tick:findings_exhausted') "
        "AND committed = 1 AND wake_refs LIKE ?", (f'%"{batch_id}"%',))}
    # A rung whose own key the tick quarantine took was asked too. It
    # committed no session, so the ladder asked it for ever and `preempt`
    # never parked (frame 330, the agency read, instance 10).
    from .scheduler import key_parts, quarantined_keys
    asked |= {role for role, kind, _ in map(key_parts, quarantined_keys(conn, batch_id))
              if role in LADDER
              and kind in ("tick:exhausted", "tick:findings_exhausted")}
    for role in LADDER:
        if role not in asked:
            return role
    return ""


@predicate("unresolved", wakes=DERIVED, band="fix",
           derives=(*QUESTION_LADDER, "liaison"),
           drains=[("messages", "status", "unresolved")])
def unresolved(conn) -> list[Wake]:
    """
    A question that was answered and did not land, climbing to somebody new.

    This is the register's one declared entry, and everything after the
    declaration is derived like the rest. The asker says `schedule.unresolved`;
    who hears about it next is a function of who has already spoken in the
    thread, so it cannot drift out of step with the conversation it is about.

    What it replaces is the sentence that used to be in `developer/answer.md`:
    "if the block truly survives the answer, the batch will bounce and wake you
    where the ladder is." That is a role being told to spend attempts it knows
    are wasted so that a *cap* can notice what it already knows. Caps exist for
    glitches. A role that reports being blocked is doing its job, and the system
    should act on the report rather than wait for the budget to agree with it.

    The next rung is the first role in the ladder that has not spoken in this
    thread *and can actually reply to the asker*, Liaison last, because a
    question the roles cannot answer is one the principal has to and Liaison is
    how anything reaches them. When everyone has spoken it goes quiet: by then
    Liaison has sent, which means it is on the principal's agenda, and that has
    a drain of its own.

    Reply-capability is read off the graph rather than assumed, because the
    graph does not grant it uniformly: Architect can ask Terminologist and
    Terminologist has no edge to answer Architect, which is the only question
    channel in the system missing its return path. Waking a rung that cannot
    speak to the asker would produce a session with nothing it could do —
    a silence indistinguishable from the answer landing.

    Note that the asker is skipped for free -- it is in the thread by
    construction, having asked -- so there is no rule about it to get wrong.
    """
    from ..design import graph as graph_mod

    rows = conn.execute(
        "SELECT id, from_role, to_role, thread_id, verb, body_refs, unresolved_note "
        "FROM messages WHERE status = 'unresolved' ORDER BY seq").fetchall()
    if not rows:
        return []

    g = graph_mod.load()
    can_answer: dict[str, set[str]] = {}
    for e in g.of_type("messages"):
        if e.v == "answer":
            can_answer.setdefault(e.t, set()).add(e.s)

    wakes = []
    for r in rows:
        # Frame 245, wall guide cause 6: the row outlives its cause. A
        # challenge names a red test. A green newest run answers the
        # challenge, and the status row does not change. Night 148 woke two
        # rungs on m76 after run 4 passed. The Liaison then asked the
        # principal about a passing test at m81. The Developer's challenge
        # only: a Critic challenge says a green test misses its criterion,
        # so a green run is its premise and not its answer (law 6, never
        # silence; frame 245 review 1, finding 1).
        if (r["verb"] == "challenge" and r["from_role"] == "developer"
                and r["to_role"] == "tester"
                and _tests_green(conn, r["body_refs"])):
            continue
        # The Tester's criteria-ref questions belong to `criterion_repair`,
        # which wakes the criterion's writer in a mode that can rewrite it.
        # Ceded here rather than raced: two predicates offering one question
        # would dispatch whichever band sorts first and starve the other.
        if r["from_role"] == "tester" and _names_a_criterion(conn, r["id"]):
            if not _repair_attempted(conn, r["id"]):
                continue
        spoken = {m["from_role"] for m in conn.execute(
            "SELECT DISTINCT from_role FROM messages WHERE thread_id = ?",
            (r["thread_id"],))}
        # The once-guard (frame 174, design 200 change 5). A role that had a
        # session for this row and sent nothing has not spoken, so without
        # this it woke again on the same row until `tick_attempt_cap` stopped
        # it. One wake per role per row: the ladder climbs past it instead.
        spoken |= _woken_for(conn, r["id"])
        able = can_answer.get(r["from_role"], set())
        # Two shapes, because two things are being climbed.
        #
        # A role's blocked question climbs toward a *ruling*: structure, then
        # scope, then a person. `QUESTION_LADDER` is that order and Terminologist
        # is deliberately not in it -- it does not rule on anything.
        #
        # The principal's question is not an escalation. It is a question
        # looking for whoever holds the answer, and the holders are the roles
        # the graph says can answer Liaison: the three artefact owners. Ordering
        # them by the ruling ladder put Terminologist nowhere, which is the one
        # owner that holds what a word means -- and "what does this mean here?"
        # is most of what a maintainer asks. Measured on the click run: the
        # question named a `recipe`, Architect said the area was unsurveyed, and
        # the ladder went to Vision Keeper while the glossary sat unread.
        #
        # Derived from the graph rather than named, so it cannot fall behind it.
        ladder = (*QUESTION_LADDER, "liaison") if r["from_role"] != "liaison"             else (*sorted(able), "liaison")
        for role in ladder:
            if role in spoken:
                continue
            if role != "liaison" and role not in able:
                continue              # cannot reply to this asker; not a rung
            wakes.append(Wake(role, "tick:unresolved", refs=(r["id"],),
                              detail=r["unresolved_note"] or ""))
            break
        else:
            # Nobody left, and for a principal's question that is not the end.
            #
            # The asker is skipped above because it is blocked and cannot answer
            # itself -- true of every role. Liaison is the exception that the
            # rule was never asked about: it is the asker *and* the only way
            # back to the person who asked. Without this the thread stops in
            # silence, which from the principal's side is indistinguishable
            # from the system losing the question.
            #
            # `liaison/unresolved.md` already says the right thing for this
            # wake and had no way to be reached for it: "every role that could
            # have taken it next has already spoken in this thread ... this is
            # the strongest kind of question you can put to the principal".
            if r["from_role"] == "liaison" and "liaison" not in _woken_for(
                    conn, r["id"], kinds=("tick:unresolved",)):
                wakes.append(Wake("liaison", "tick:unresolved", refs=(r["id"],),
                                  detail=r["unresolved_note"] or ""))
    return wakes


def _woken_for(conn, msg_id: str,
               kinds: tuple[str, ...] = ("message", "tick:unresolved")) -> set[str]:
    """
    The roles that had a committed session for the message `msg_id`.

    `message` is the addressee's own wake, which `sessions.trigger_msg` names.
    `tick:unresolved` is a ladder wake, which names the row in `wake_refs`.
    """
    roles: set[str] = set()
    if "message" in kinds:
        roles |= {s["role"] for s in conn.execute(
            "SELECT DISTINCT role FROM sessions "
            "WHERE committed = 1 AND trigger_msg = ?", (msg_id,))}
    if "tick:unresolved" in kinds:
        roles |= {s["role"] for s in conn.execute(
            "SELECT DISTINCT s.role FROM sessions s, json_each(s.wake_refs) j "
            "WHERE s.committed = 1 AND s.wake_kind = 'tick:unresolved' "
            "  AND j.value = ?", (msg_id,))}
    return roles


def _tests_green(conn, body_refs: str | None) -> bool:
    """
    True when the refs name a test with a run, and every such test passes.

    The newest run of the test's own batch counts, because an inherited test
    keeps its id across batches (frame 210). A ref with no run is not a test
    the harness has spoken about, so it does not count either way.
    """
    seen = False
    for ref in _refs_of(body_refs):
        row = conn.execute(
            "SELECT tr.result FROM latest_runs tr JOIN tests t ON t.id = tr.test_id "
            "WHERE tr.test_id = ? AND tr.batch_id = t.batch_id", (ref,)).fetchone()
        if row is None:
            continue
        if row["result"] != "pass":
            return False
        seen = True
    return seen


def _names_a_criterion(conn, message_id: str) -> bool:
    refs = _refs_of(conn.execute(
        "SELECT body_refs FROM messages WHERE id = ?",
        (message_id,)).fetchone()["body_refs"])
    return any(conn.execute("SELECT 1 FROM criteria WHERE id = ?",
                            (ref,)).fetchone() for ref in refs)


def _repair_attempted(conn, message_id: str) -> bool:
    return bool(conn.execute(
        "SELECT 1 FROM sessions WHERE wake_kind = 'tick:criterion_repair' "
        "AND committed = 1 AND wake_refs LIKE ?", (f'%"{message_id}"%',)).fetchone())


@predicate("criterion_repair", wakes="terminologist", band="fix",
           drains=[("messages", "status", "unresolved")])
def criterion_repair(conn) -> list[Wake]:
    """
    A Tester's unresolved question that names a criterion wakes the
    criterion's writer, in a mode that can rewrite it.

    Not a ladder rung. A question whose refs name a criterion, asked by the
    role whose job is turning criteria into assertions, is a defect report
    about an artefact with one writer -- found live on delivery rung one,
    where the Tester took the parroting guard's exit, the question landed in
    a mode whose own brief says "answering is not amending", and the pair
    looped to the budget. `criteria.specify` inserts and its predicate fires
    per ticket *without* criteria, so once written, wrong stayed wrong.

    A Developer's criterion question stays with the ladder: theirs is about
    what done *means*, which is ruling territory. Once per question -- a
    repair session that leaves it unresolved has said the criterion is not
    the problem, and the ladder resumes.
    """
    return [
        Wake("terminologist", "tick:criterion_repair", refs=(r["id"],),
             detail=r["unresolved_note"] or "")
        for r in conn.execute(
            "SELECT id, unresolved_note FROM messages "
            "WHERE status = 'unresolved' AND from_role = 'tester' "
            "ORDER BY seq")
        if _names_a_criterion(conn, r["id"])
        and not _repair_attempted(conn, r["id"])
    ]


@predicate("review", wakes="critic", band="gate")
def review(conn) -> list[Wake]:
    """A batch with a committed diff and a green harness, not yet judged.

    Critic runs before Architect: most failures are failures of intent, and
    screening them first means never paying for a constraint review on work that
    does not do what was asked.

    Per commit, not per batch. Guarding on "has a verdict" meant a batch that
    failed review could never pass: the Developer fixed it, committed, and
    nothing re-judged."""
    from .harness import reds_that_hold
    from .scheduler import live_criteria, not_retired
    rows = conn.execute(
        "SELECT b.id AS bid, b.head_commit AS head FROM batches b "
        "WHERE b.status = 'running' AND b.head_commit IS NOT NULL "
        "  AND NOT EXISTS (SELECT 1 FROM verdicts v "
        "                  WHERE v.batch_id = b.id AND v.commit_sha = b.head_commit) "
        "  AND EXISTS (SELECT 1 FROM latest_runs r "
        "              WHERE r.batch_id = b.id AND r.commit_sha = b.head_commit) "
        # law 8: the merge gate runs harness, then Critic, then Architect
        # And every criterion has its test. Since the repository's own tests
        # join the batch, a green harness no longer means the Tester has been
        # here: tipsZ (2026-09-09) merged on the inherited test alone, with
        # no test of either criterion and no Tester session. The Tester's tick
        # is in the start band; review waits for it.
        # The test must be of this batch. Night 147, walk 2: bg_2's tests
        # let the Critic judge bg_3 before its Tester ran (frame 239).
        # The debt is the one `tests_missing` wakes the Tester for. Night 164:
        # his m37 retired three of bg_1's criteria. This count kept them, so
        # bg_1 stayed green at 37 of 37 and no Critic woke (frame 306, W-C).
        "  AND NOT EXISTS (SELECT 1 FROM batch_tickets bt "
        "                  JOIN criteria c ON c.ticket_id = bt.ticket_id "
        "                  WHERE bt.batch_id = b.id "
        "                    AND NOT EXISTS (SELECT 1 FROM tests t "
        "                                    WHERE t.criterion_id = c.id "
        "                                      AND t.batch_id = b.id)"
        + not_retired(conn, "bt.ticket_id") + live_criteria(conn, "c.retired_by")
        + ")"
    ).fetchall()
    # A red test at the head holds the review. One helper decides for this
    # gate and the merge check, and a test red at the base holds neither
    # (frame 362, pass 5b).
    return [Wake("critic", "tick:review", refs=(r["bid"],)) for r in rows
            if not reds_that_hold(conn, r["bid"], r["head"])]


# A violated finding at the head commit, on a real constraint. Shared by the
# Critic's wake and the Developer's, so the two never disagree on which
# findings count.
_VIOLATED_AT_HEAD = (
    "f.batch_id = b.id AND f.commit_sha = b.head_commit "
    "AND f.status = 'violated' AND f.constraint_id != ?")
_RULED_AT_HEAD = (
    "SELECT 1 FROM finding_rulings fr WHERE fr.finding_id = f.id "
    "AND fr.commit_sha = b.head_commit")


@predicate("finding_review", wakes="critic", band="gate")
def finding_review(conn) -> list[Wake]:
    """A violated finding at the head commit that the Critic has not ruled on.

    Ruled by Roman on 2026-09-27: only the Critic can reopen a green,
    signed-off batch. Night 94: the Architect filed `fnd_1` against `echo`
    after the Critic's pass, on a constraint the Critic had falsified. The
    Developer woke twice, broke the imports, and the batch never merged.
    Every finding comes after a pass, so every finding reaches the Critic
    first. One wake per finding: the ruling is per finding and commit.

    law 8: the merge gate runs harness, then Critic, then Architect
    """
    from ..onboarding.boot import ZERO

    rows = conn.execute(
        "SELECT b.id AS bid, f.id AS fid FROM batches b JOIN findings f "
        f"  ON {_VIOLATED_AT_HEAD} "
        "WHERE b.status = 'running' AND b.head_commit IS NOT NULL "
        f"  AND NOT EXISTS ({_RULED_AT_HEAD}) "
        "ORDER BY b.id, f.id", (ZERO,)).fetchall()
    return [Wake("critic", "tick:finding_review", refs=(r["bid"], r["fid"]))
            for r in rows]


@predicate("structural_review", wakes="architect", band="gate")
def structural_review(conn) -> list[Wake]:
    """A diff whose grains intersect constraint bindings, after intent passed.

    Expensive — it costs a session — so it runs once, late, on work that already
    satisfies its criteria.

    *Once*: batches that already carry findings are excluded. Without that it
    fires forever on every reviewed batch, which is the livelock the loop guard
    catches — after two wasted sessions, and only if someone reads the trace."""
    rows = conn.execute(
        "SELECT v.batch_id AS bid FROM verdicts v "
        "JOIN batches b ON b.id = v.batch_id "
        "WHERE v.result = 'pass' AND b.status = 'running' "
        "  AND v.commit_sha = b.head_commit "
        "  AND NOT EXISTS (SELECT 1 FROM findings f "
        "                  WHERE f.batch_id = b.id AND f.commit_sha = b.head_commit)"
    ).fetchall()
    # And only where there is something to check it against, which is what the
    # first line of this docstring always claimed and the query never did. With
    # no constraints in the project there is no finding Architect could legally
    # record -- `constraint_id` is NOT NULL and references `constraints` -- so
    # firing here woke a role to do something impossible, forever. The gate asks
    # the same question through the same function, because two answers to one
    # question is how they came to disagree.
    from .lifecycle import needs_structural_review
    return [Wake("architect", "tick:structural_review", refs=(r["bid"],))
            for r in rows if needs_structural_review(conn, r["bid"])]


@predicate("verdict_failed", wakes="developer", band="fix",
           drains=[("verdicts", "result", "fail")])
def verdict_failed(conn) -> list[Wake]:
    """A failed verdict with no newer commit: the Developer has not answered it.

    At the head commit only, as the first line always said. Night 101
    (2026-09-30): the Critic failed bg_1, the Developer committed five fixes,
    and this band sorted before `review` each time. Five Developer wakes, and
    the Critic never judged the new head.

    law 8: the merge gate runs harness, then Critic, then Architect
    """
    rows = conn.execute(
        "SELECT v.batch_id AS bid FROM verdicts v JOIN batches b ON b.id = v.batch_id "
        "WHERE v.result = 'fail' AND b.status = 'running' "
        "  AND v.commit_sha = b.head_commit"
    ).fetchall()
    return [Wake("developer", "tick:verdict_failed", refs=(r["bid"],)) for r in rows]


@predicate("finding_violated", wakes="developer", band="fix",
           drains=[("findings", "status", "violated")])
def finding_violated(conn) -> list[Wake]:
    """
    A violated finding on the batch's head commit: the Developer has not
    answered it.

    tipsAJ (2026-09-10): every test passed, the Critic passed twice, the
    structural review found four constraints violated, and nothing woke
    anyone. The merge gate said "4 constraint(s) violated" and the run
    was quiet. A finding is answered by a newer commit, which the review
    reads again, or by an escalation to the Architect who owns the
    constraint. Capped like the test loop: `loop_cap` commits with a
    violated finding on them, then the batch is exhausted.

    Frame 88 (ruled by Roman, 2026-09-27): only the Critic's fresh verdict
    sends the Developer back. So the Developer wakes on a finding the
    Critic upheld at the head commit, and only once the Critic has ruled
    on every violated finding there. The rounds count the commits with an
    upheld ruling. The old count read `findings`, and it never bound,
    because `findings.find` overwrites a finding's row by id.
    """
    from . import config
    from ..onboarding.boot import ZERO

    cap = config.get(conn, "loop_cap")
    rows = conn.execute(
        "SELECT b.id AS bid, "
        "  (SELECT COUNT(DISTINCT fr.commit_sha) FROM finding_rulings fr "
        "   JOIN findings f2 ON f2.id = fr.finding_id "
        "   WHERE f2.batch_id = b.id AND fr.ruling = 'upheld') AS rounds "
        "FROM batches b "
        "WHERE b.status = 'running' AND b.head_commit IS NOT NULL "
        f"  AND EXISTS (SELECT 1 FROM findings f WHERE {_VIOLATED_AT_HEAD} "
        f"              AND EXISTS ({_RULED_AT_HEAD} AND fr.ruling = 'upheld')) "
        f"  AND NOT EXISTS (SELECT 1 FROM findings f WHERE {_VIOLATED_AT_HEAD} "
        f"                  AND NOT EXISTS ({_RULED_AT_HEAD})) "
        "  AND NOT EXISTS (SELECT 1 FROM messages m WHERE m.from_role = 'developer' "
        "                  AND m.verb = 'escalate' AND m.status = 'open' "
        "                  AND m.body_refs LIKE '%' || b.id || '%') "
        "ORDER BY b.id", (ZERO, ZERO)).fetchall()
    return [Wake("developer", "tick:finding_violated", refs=(r["bid"],),
                 detail=_upheld_detail(conn, r["bid"], r["rounds"]))
            for r in rows if (r["rounds"] or 1) < cap]


def _upheld_detail(conn, batch_id: str, rounds: int) -> str:
    """The round, and which findings the Critic upheld at the head commit.

    The Developer's brief says the Architect found the violation. Since frame
    88 the Critic upholds a finding before the Developer sees it, so the wake
    says so (frame 88's diff review, 2026-09-27)."""
    upheld = conn.execute(
        "SELECT f.id AS fid, f.constraint_id AS cid FROM findings f "
        "JOIN batches b ON b.id = f.batch_id AND f.commit_sha = b.head_commit "
        "JOIN finding_rulings fr ON fr.finding_id = f.id "
        "  AND fr.commit_sha = f.commit_sha AND fr.ruling = 'upheld' "
        "WHERE f.batch_id = ? AND f.status = 'violated' ORDER BY f.id",
        (batch_id,)).fetchall()
    named = ", ".join(f"{u['fid']} on {u['cid']}" for u in upheld)
    return f"round {rounds}: the Critic upheld {named}"


@predicate("cancel", wakes=SCHEDULER, band="fix",
           drains=[("batches", "status", "pending"),
                   ("batches", "status", "running"),
                   ("batches", "status", "deferred")])
def cancel(conn) -> list[Wake]:
    """
    A live batch whose item is no longer schedulable.

    The revocation predicate, given its missing exit: `batch_start` filters
    unschedulable items, which stops the work but leaves the batch waiting in
    the game forever -- pending, deferred, or worse, running while the
    approval it delivers against has been withdrawn. Law 9 owns starting and
    reordering; this is the same authority ending: the scheduler performs the
    abandonment itself, because whether a batch may exist is a scheduling
    fact, and no session is woken to decide it.
    """
    # A drop on the shift page stops the earlier request, so its live change
    # is abandoned as for any revocation (frame 193's design, 2.F.3).
    from .scheduler import _has_parks
    dropped = ("OR (SELECT p.kind FROM item_parks p WHERE p.item_id = i.id "
               "ORDER BY p.seq DESC, p.rowid DESC LIMIT 1) = 'drop' "
               if _has_parks(conn) else "")
    rows = conn.execute(
        "SELECT b.id AS bid FROM batches b JOIN items i ON i.id = b.item_id "
        "WHERE b.status IN ('pending','running','deferred') "
        "  AND (i.approval != 'approved' OR i.approval_ver < i.version "
        + dropped + ") ORDER BY b.id").fetchall()
    return [Wake(SCHEDULER, "do:cancel", refs=(r["bid"],),
                 detail=f"{r['bid']}'s item is no longer schedulable")
            for r in rows]


@predicate("preempt", wakes=SCHEDULER, band="fix",
           drains=[("batches", "status", "running")])
def preempt(conn) -> list[Wake]:
    """
    A schedulable batch whose item outranks the running one's.

    Law 9's reorder, as a predicate: priority moves batches whole, and a
    priority raised mid-flight was inert until the running batch happened to
    finish, because `batch_start` refuses while anything runs. Strictly
    greater -- a preemption discards a checkpoint, and equal urgency does not
    pay for that. The scheduler performs the deferral itself: which batch
    runs is a scheduling fact, and no session is woken to decide it.
    """
    running = conn.execute(
        "SELECT b.id AS bid, b.item_id AS item, i.priority AS pri FROM batches b "
        "JOIN items i ON i.id = b.item_id WHERE b.status = 'running'"
    ).fetchone()
    if not running:
        return []
    # A running batch whose item was put aside is deferred, so its worktree
    # and commits persist as deferred work (law 9; frame 193's design, 2.F.4).
    from .scheduler import aside_items, park_kind

    if running["item"] in aside_items(conn):
        from ..roles.principal import park_behind

        behind = (park_behind(conn, running["item"], as_id=True)
                  if park_kind(conn, running["item"]) == "park" else None)
        why = (f"{running['item']} is set aside behind {behind}" if behind
               else f"{running['item']} is set aside")
        return [Wake(SCHEDULER, "do:preempt", refs=(running["bid"], running["item"]),
                     detail=why)]
    # law 9: a reorder ahead of the running batch preempts it
    # The start's order, so the two never disagree. Night 92 started `b_2`
    # and preempted it for `b_3` nineteen times (observed: night 92, 2026-09-24).
    from .scheduler import next_batch

    ranked = next_batch(conn)
    if not ranked:
        # With no challenger the scheduler's quiet parks a spent batch
        # (`scheduler.quiet_park`). dry1 held its one batch here with
        # nothing awake (dry1's fourth wall, 2026-11-01, frame 330).
        return []
    challenger = ranked[0]["id"]
    park = spent_park(conn, running["bid"])
    if park:
        return [park]
    if (ranked[0]["priority"] or 0) <= (running["pri"] or 0):
        return []
    return [Wake(SCHEDULER, "do:preempt",
                 refs=(running["bid"], challenger),
                 detail=f"{challenger} outranks {running['bid']}")]


def spent_park(conn, bid: str) -> Wake | None:
    """The `do:park` wake of the running batch `bid` when it is parked and
    no rung is left, or None.

    law 6: exhaustion escalates one rung at a time. A running batch past its
    cap with every rung asked wakes nobody again. Night 93 held `b_1` so,
    and three ready batches waited to the end (observed: night 93,
    2026-09-25). The deferral frees the seat, and `next_batch` keeps the
    batch out until a new head commit. The refs hold batch ids only, so
    frame 83's counter rules read the key unchanged. `preempt` reads it
    with a challenger, and the scheduler's quiet reads it with none
    (`scheduler.quiet_park`, frame 330).
    """
    from .scheduler import parked, stop_detail

    if not parked(conn, bid) or _next_rung(conn, bid):
        return None
    why = stop_detail(conn, bid)
    return Wake(SCHEDULER, "do:park", refs=(bid,),
                detail=(f"{bid}: {why}, and its ladder is spent" if why
                        else f"{bid} is past its cap and its ladder is spent"))


@predicate("merge", wakes=SCHEDULER, band="gate",
           drains=[("verdicts", "result", "pass")])
def merge(conn) -> list[Wake]:
    """
    A batch that passed review and was never merged.

    This was the worst dead end: the delivery loop terminated one step before
    delivering. It wakes nobody — merging is mechanical once the verdict is in,
    the same shape as the harness. The optional principal review gates it.

    An action, not a wake. The role is empty, and the loop performs `do:` wakes
    itself rather than dispatching a session for them. Declaring `wakes` as
    SCHEDULER and then returning role wakes would be the same flattening the
    sentinel exists to prevent.
    """
    from .lifecycle import mergeable

    rows = conn.execute(
        "SELECT DISTINCT batch_id AS bid FROM verdicts v "
        "WHERE v.result = 'pass' AND v.batch_id IN "
        "  (SELECT id FROM batches WHERE status = 'running')"
    ).fetchall()
    return [Wake("", "do:merge", refs=(r["bid"],))
            for r in rows if mergeable(conn, r["bid"]) is None]


# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------

@predicate("checkpoint_invalid", wakes=DERIVED, band="fix")
def checkpoint_invalid(conn) -> list[Wake]:
    """An invalidated checkpoint: the suspended role must restart cold. Boot
    sweeps these; nothing did at runtime, so a mid-run invalidation stranded the
    session until the next restart."""
    rows = conn.execute(
        "SELECT session_id, role FROM checkpoints WHERE valid = 0").fetchall()
    return [Wake(r["role"], "tick:checkpoint_invalid", detail=r["session_id"])
            for r in rows]


def _refs_of(body_refs: str | None) -> list[str]:
    """The ids a message was carrying, and nothing if the column is unreadable.

    A malformed `body_refs` is a bad row, not a reason to stop reporting that
    work has been abandoned — the count is the part that must survive.
    """
    import json
    try:
        loaded = json.loads(body_refs or "[]")
    except (TypeError, ValueError):
        return []
    return [r for r in loaded if isinstance(r, str) and r]


@predicate("quarantined", wakes="liaison", band="fix",
           drains=[("messages", "status", "quarantined")])
def quarantined(conn) -> list[Wake]:
    """The system gave up on a message, or on a tick. That is something the
    principal should be told, not something to bury — it was invisible before.

    Ticks joined messages here because a stalled one is *worse*: an abandoned
    message at least stops. A tick that cannot drain is produced again every
    pass, so the system stays busy, keeps committing, and never arrives —
    quiescence never comes and nothing reports that anything is wrong. The first
    foreign repository spun six sessions on area one of twelve before anybody
    looked at a counter.

    **The wake carries the payload, not the envelope.** Liaison's whole working
    set here is `msg.present_principal`, and that channel refuses message ids —
    the principal has never seen a message and cannot resolve one. So a wake
    naming the dead message hands the session the single id its only call will
    reject, with no tool to trade it for anything better. Measured before this
    was fixed: five runs, five sessions spent arguing with the guard and then
    reaching six times for a tool they do not have. Nothing sent.

    What stalled is what the message was *about*, which is also what the brief
    asks for — "name the work that is now stalled, not the mechanism" — and the
    only part of this the principal has a name for."""
    # Untold only, as the tick keys below are unreported only. A committed
    # report marks the message told in `loop.step` (frame 355).
    # A read-only open adds no column, so an old database has no `told`.
    # Then no message was told yet. The cockpit's overlay and `rota ls`
    # raised there (frame 355, review 2, finding 5).
    from .db import _has_column

    untold = " AND told = 0" if _has_column(conn, "messages", "told") else ""
    dead = conn.execute(
        "SELECT id, body_refs FROM messages WHERE status = 'quarantined'"
        + untold).fetchall()
    # Ordered, deduplicated, and never the message ids: one dead delivery can
    # carry several items, and two can carry the same one.
    refs: list[str] = []
    for row in dead:
        for ref in _refs_of(row["body_refs"]):
            if ref not in refs:
                refs.append(ref)

    n = len(dead)
    # law 6: a wake past its cap is quarantined and said out loud
    # A stalled tick's key carries its refs (`role|tick:name|ref,ref`), and
    # those are the batch or the item the work was about: the payload the
    # brief asks the Liaison to name. clickI night 37 (2026-09-13): the wake
    # said "1 abandoned" and nothing else, and the Liaison sent
    # `refs=["tick:quarantined"]` three times to a door that refused it.
    stalled: list[str] = []
    from ..roles.principal import _items_reached
    from .scheduler import (aside_items, given_up, key_parts, park_owns,
                            quarantined_keys, rowless_key)

    aside = aside_items(conn)

    try:
        for key in quarantined_keys(conn, unreported=True, groups=False):
            # law 6: a wake past its cap is quarantined and said out loud
            # A key that a park owns is said by the park page or the note.
            # Night 133's s319 and s325 presented the batch alone, and the
            # rulings on it moved nothing (frame 142's design, 2.D). A key
            # of a running batch stays, because a running batch has no park.
            role, kind, keyed = key_parts(key)
            if (len(keyed) == 1 and key in given_up(conn, keyed[0])
                    and park_owns(conn, keyed[0])):
                continue
            # A key whose refs reach only items set aside waits with them.
            # Night 137's m186 put the confirm item to the principal after
            # the version option request (frame 193's design, 2.F.4).
            keyed_items = set()
            for ref in keyed:
                keyed_items.update(_items_reached(conn, ref))
            if keyed_items and keyed_items <= aside:
                continue
            n += 1
            kind = kind.replace("tick:", "")
            attempts = conn.execute(
                "SELECT attempts FROM tick_attempts WHERE tick_key = ?",
                (key,)).fetchone()["attempts"]
            from .db import table_of

            for ref in keyed:
                # `db.table_of` finds the row. The scope is the rows a page names (F22).
                if ref not in refs and table_of(
                        conn, ref, among=("batches", "items", "tickets")):
                    refs.append(ref)
            # A key that reaches no row travels as its own ref. Nothing stops
            # quietly (composition), and frame 354 measured the cost: m3 was a
            # page with no line for the constraint zero key.
            if key not in refs and rowless_key(conn, key):
                refs.append(key)
            stalled.append(f"{kind} for {', '.join(keyed) or 'the run'}"
                           f"{f' ({role})' if role and role != '-' else ''}, "
                           f"{attempts} attempts")
    except Exception:                 # a database older than the table
        pass
    detail = f"{n} abandoned" + (": " + "; ".join(stalled) if stalled else "")
    return [Wake("liaison", "tick:quarantined", refs=tuple(refs),
                 detail=detail,
                 message_ids=tuple(r["id"] for r in dead))] if n else []


@predicate("park_ask", wakes="liaison", band="fix")
def park_ask(conn) -> list[Wake]:
    """
    A deferred batch the team gave up on, owed one ask to the principal.

    A given-up batch put back in the chair waits for the principal (ruled:
    Roman, 2026-09-27). The principal answers through a gate, and the
    Liaison writes the gate (ruled: Roman, 2026-09-30). The park message
    is a page with the item and its criteria when a criterion's own test is
    red, and a note otherwise (ruled: Roman, 2026-10-08). The Tester's give-up
    before any test of the criteria existed is a page too (ruled: Roman,
    2026-11-01). Its id comes from
    the batch, its head commit, its keys, the versions of its criteria and
    tests, and the closed asks that did not rest. A note or a page approved
    whole rests, so nothing more is asked until something moves. The refs
    are the item and the batch. The door writes the page's own refs.
    """
    from .scheduler import (given_up, key_parts, open_park_ask, park_ask_id,
                            park_owns, park_rows)

    from .scheduler import not_parked

    out = []
    # A set-aside item's batch owes no page while it waits (frame 193's
    # design, 2.F.4).
    for b in conn.execute(
            "SELECT b.id, b.item_id FROM batches b JOIN items i ON i.id = b.item_id "
            # A pending batch parks on an owed write (frame 362). `park_owns`
            # keeps only a real park.
            "WHERE b.status IN ('deferred', 'pending')" + not_parked(conn, "b.item_id")
            + " ORDER BY b.id").fetchall():
        # A contested item's batch goes to `do:cancel`, so nothing is asked.
        # A contest closes the ask before the cancel runs, and the next id
        # would open a second ask on a batch that is going.
        if not park_owns(conn, b["id"]) or open_park_ask(conn, b["id"]) or conn.execute(
                "SELECT 1 FROM messages WHERE id = ?",
                (park_ask_id(conn, b["id"]),)).fetchone():
            continue
        keys = given_up(conn, b["id"])
        # The Liaison reads this detail, and the door writes the page from
        # the records. So the detail keeps the kind's name (fact F21).
        what = ", ".join(f"{key_parts(k)[1].replace('tick:', '')} for {b['id']}"
                         for k in keys)
        # A park on the challenge count has no key to name, so the detail
        # carries the first rung's clause (review p2 of frame 278).
        from . import config
        from .scheduler import challenge_words, failing_attempt, park_reds

        # A park at `loop_cap` has no key either, so the detail names the
        # cap and the red tests (frame 330, pass 3).
        tries, cap = failing_attempt(conn, b["id"]), config.get(conn, "loop_cap")
        reds = [r["test_id"] for part in park_reds(conn, b["id"]) for r in part]
        capped = (f"attempt {tries} of {cap} with {', '.join(reds)} red"
                  if tries >= cap and reds else "")
        what = "; ".join(p for p in (what, capped, challenge_words(conn, b["id"])) if p)
        kind = "note" if park_rows(conn, b["id"]) == [b["id"]] else "page"
        out.append(Wake("liaison", "tick:park_ask", refs=(b["item_id"], b["id"]),
                        detail=f"{b['id']} is parked. The team gave up on: {what}. "
                               f"It is a {kind}."))
    return out


@predicate("agenda", wakes="liaison", band="start", needs_principal=True,
           drains=[("ledger", "status", "open")])
def agenda(conn) -> list[Wake]:
    """
    On principal presence, present what is blocked on them.

    Not before onboarding is done. The Critic's challenge ticks run in the
    start band and each writes one ledger row; the agenda in the gate band
    outranked them, so every row raised its own page before the next
    challenge ran: thirteen pages on one run (tipsV, 2026-09-09). One page,
    once the rows are all there; the same gate as `observed_entries`.

    Band `start`, after `annotate`, `touch_note` and `batch_start` in the
    file. On night 136 the agenda fired 13 times after s514 and bg_4 was
    never annotated. The ruling of 2026-09-13, point 2: "After that, nothing
    waits on a page" (frame 190's design, 2.4).

    law 6: at the Liaison it is a page, a hold or a note
    """
    from .scheduler import onboarding_phase, tick_agenda

    if onboarding_phase(conn) not in ("done", "none"):
        return []
    return tick_agenda(conn, principal_present=True)


@predicate("constraint_zero", wakes=SCHEDULER, band="gate",
           drains=[("survey_records", "outcome", "found"),
                   ("survey_records", "outcome", "none_found")])
def constraint_zero(conn) -> list[Wake]:
    """
    A survey has landed and constraint zero still covers the area it looked at.

    Nobody's judgement: the area was read, so it is no longer unread, and there
    is no version of that fact a session could weigh. Dispatching a role to
    press the button would be inventing a decision to have.

    It fires on a mismatch rather than on the survey, which is what keeps the
    binding a function of the evidence — a survey rolled back with its session
    takes its shrinkage with it, and a re-onboarding onto a later commit
    re-derives the whole binding without remembering anything.
    """
    from ..onboarding import boot

    bound = {r["grain"] for r in conn.execute(
        "SELECT grain FROM constraint_bindings WHERE constraint_id = ?",
        (boot.ZERO,))}
    if not bound and not conn.execute(
            "SELECT 1 FROM code_index LIMIT 1").fetchone():
        return []                       # nothing onboarded; nothing to cover

    surveyed = {r["area"] for r in conn.execute(
        "SELECT DISTINCT area FROM survey_records")}
    # The refresh binds only areas with code, so want reads the same set.
    want = set(boot.coded_areas(conn)) - surveyed

    return [] if bound == want else [
        Wake(SCHEDULER, "tick:constraint_zero", refs=tuple(sorted(bound - want)))]


@predicate("frame", wakes="architect", band="start")
def frame(conn) -> list[Wake]:
    """Onboarding, zeroth: the tree is classified before anything reads it.
    The partition decides what every later session can see; judging it is
    one session, and the attest re-pins."""
    from .scheduler import tick_frame
    return tick_frame(conn)


@predicate("orient", wakes="vision_keeper", band="start")
def orient(conn) -> list[Wake]:
    """
    Onboarding, first: what does this program do for the person using it.

    One wake over the whole program, before any word in it is named, because
    the account of what the program is for is the one context that displaces
    the everyday reading of its words -- measured: handed the call trace, the
    model kept "an intent is a user's goal"; handed the account, it wrote "a
    recipe for making a note". Owned by the role answerable for what the
    project is, and discharged by its attestation.
    """
    from .scheduler import tick_orient
    return tick_orient(conn)


@predicate("reconcile", wakes="vision_keeper", band="start")
def reconcile(conn) -> list[Wake]:
    """
    Onboarding, after orient: the README read against the account.

    The account is written from code alone; the README is then a check, not a
    source. A claim the account does not support is not merged -- it is a
    ledger entry ("README says X; the code shows Y") for the principal, whose
    agenda already carries open assumptions. Discharged by the attestation on
    `@prose`, whose owed artefact is the ledger.
    """
    from .scheduler import tick_reconcile
    return tick_reconcile(conn)


@predicate("define", wakes="terminologist", band="start")
def define(conn) -> list[Wake]:
    """
    Onboarding, second: one word at a time, from the project's own list.

    A meaning is not shaped like a place -- `intent` lives in five areas and no
    area-shaped question reaches it -- so the subject of this wake is a word,
    the concordance is pushed, and the lexicon says which words. Discharged by
    a glossary row in the word's family, or by `none_found` for the word.
    """
    from .scheduler import tick_define
    return tick_define(conn)


@predicate("survey", wakes=DERIVED, band="start",
           derives=SURVEY_ORDER)
def survey(conn) -> list[Wake]:
    """Onboarding, third: one elected area at a time, in role order."""
    from .scheduler import tick_survey
    return tick_survey(conn)


@predicate("commitments", wakes="architect", band="start")
def commitments(conn) -> list[Wake]:
    """Onboarding, after an area's Architect survey: its witness lines, each
    stated or declined in a session of their own (frame 362, pass 4b)."""
    from .scheduler import tick_commitments
    return tick_commitments(conn)



# ---------------------------------------------------------------------------
# The register, as a set the code holds rather than a list a document keeps.
# ---------------------------------------------------------------------------

@predicate("reorient", wakes="vision_keeper", band="start")
def reorient(conn) -> list[Wake]:
    """Onboarding, after the surveys: the draft account re-read with the
    full glossary and model in hand, before the boundary sessions consume
    it. One session; the fixpoint loop's single iteration."""
    from .scheduler import tick_reorient
    return tick_reorient(conn)


@predicate("boundary", wakes="architect", band="start")
def boundary(conn) -> list[Wake]:
    """
    Onboarding, last: one session per file the outside touches.

    The area survey kept answering the constraint question at symbol grain --
    ten identifier-headlined rows on the first measured run, zero of the two
    the answer key requires -- because an area's context is its source and a
    session holds the names it just read. This pass asks outside-in: the
    subject is a boundary file (authoring surface, manifest), the front is
    that file and every reader of it, and the question is what the other
    side relies on and whether its failure is loud or silent.
    """
    from .scheduler import tick_boundary
    return tick_boundary(conn)


@predicate("challenge", wakes="critic", band="start")
def challenge(conn) -> list[Wake]:
    """Onboarding, last: the Critic tries to falsify the load-bearing
    claims against source. A claim's standing comes from surviving this,
    never from who wrote it; a break is a citation, or it is refused."""
    from .scheduler import tick_challenge
    return tick_challenge(conn)


@predicate("blindspot", wakes="liaison", band="start")
def blindspot(conn) -> list[Wake]:
    """Onboarding's last word: what this run could not see, said to the
    ledger. Static tripwires catch the named assumptions; this session
    exists for the rest."""
    from .scheduler import tick_blindspot
    return tick_blindspot(conn)


REGISTER_ENTRIES = frozenset({
    "contradiction", "contested", "constraint_zero", "awaiting_confirm",
    "agenda", "quarantined", "exhausted", "round_close",
    "observed_entries", "reconcile", "reopen", "tests_failing", "verdict_failed",
    "finding_violated",
    "checkpoint_invalid", "survey", "commitments", "term_collision", "unresolved",
    "orient", "define", "boundary", "frame", "reorient", "challenge",
    "blindspot", "criterion_repair", "touch_note",
    # A parked batch is owed one ask to the principal until it is written
    # (frame 87, ruled 2026-09-30).
    "park_ask",
    # A new request is owed one shift question to the principal while an
    # earlier request is open, until it is written (frame 193's design,
    # 2.F.1, ruled 2026-10-10).
    "request_shift",
    # A request item is owed the Architect's guess of its code at each item
    # version, until it is written (frame 298's design, 4.1, ruled 2026-10-18).
    "guess",
})


def outstanding(conn) -> list[dict]:
    """
    What this system does not know, as one query.

    `REGISTER.md` classified sixteen predicates as register entries -- something
    is owed and the predicate keeps offering it until it is not -- and then said
    the obvious thing was still missing: every row of "what is outstanding"
    existed and nothing counted them together. Each predicate answered its own
    question and none of them answered that one.

    It is a fold over work already done, which is why it needed no artefact. The
    obligations were always derived; only the sum was missing.

    Failures are reported rather than raised. This is the view somebody opens
    when they want to know where things stand, and a predicate that throws
    should not be able to make the whole answer unavailable -- that is the
    quiescence failure again, one level up.
    """
    out = []
    for name in sorted(REGISTER_ENTRIES):
        p = REGISTRY.get(name)
        if p is None:
            continue
        try:
            wakes = p.fn(conn)
        except Exception as exc:                       # noqa: BLE001
            out.append({"obligation": name, "count": 0, "owners": [],
                        "refs": [], "error": str(exc)[:120]})
            continue
        if not wakes:
            continue
        out.append({
            "obligation": name,
            "count": len(wakes),
            "owners": sorted({w.role for w in wakes if w.role not in (DERIVED, SCHEDULER)}),
            "refs": sorted({r for w in wakes for r in (w.refs or ())})[:8],
        })

    # And what the principal is sitting on, asked of the state rather than of a
    # scheduler.
    #
    # Every predicate above answers "should I wake somebody". That is a
    # different question from "is anything owed", and they part company at
    # exactly one point: when the answer is *the principal*, who is not
    # schedulable. `tick_agenda` returns nothing while a message to them is
    # already open -- rightly, because presenting again tells them what they can
    # already see, and it is what makes that tick terminate. Folding it here
    # read "there is no point waking Liaison" as "nothing is owed".
    #
    # Measured on a real repository: fifteen surveys, twenty-two scope items,
    # quiescent in 125 seconds, an open `present` in front of the principal and
    # an open assumption in the ledger -- and this function returned an empty
    # list. The pane the cockpit and the TUI render as *what the system owes*
    # was blank at the moment the answer was "you".
    #
    # A wake-suppression is not a discharge.
    try:
        asks = conn.execute(
            "SELECT id, body_refs FROM messages "
            "WHERE status = 'open' AND to_role = 'principal' ORDER BY seq"
        ).fetchall()
    except Exception as exc:                           # noqa: BLE001
        out.append({"obligation": "awaiting_principal", "count": 0,
                    "owners": [], "refs": [], "error": str(exc)[:120]})
        return out

    if asks:
        refs: list[str] = []
        for row in asks:
            for ref in _refs_of(row["body_refs"]):
                if ref not in refs:
                    refs.append(ref)
        out.append({
            "obligation": "awaiting_principal",
            "count": len(asks),
            "owners": ["principal"],
            "refs": refs[:8],
        })
    return out


# ---------------------------------------------------------------------------
# The lint: every state must have a way out
# ---------------------------------------------------------------------------

def schema_states() -> dict[tuple[str, str], list[str]]:
    """Every CHECK-constrained value in the schema, by table and column."""
    sql = SCHEMA.read_text(encoding="utf-8")
    out: dict[tuple[str, str], list[str]] = {}
    table = None
    for line in sql.splitlines():
        m = re.search(r"CREATE TABLE IF NOT EXISTS (\w+)", line)
        if m:
            table = m.group(1)
        if table == "refs":
            continue    # `refs` CHECK values are table names and nouns, not states
        if table:
            c = re.search(r"(\w+)\s+TEXT[^,]*CHECK\s*\(\s*\w+\s+IN\s*\(([^)]*)\)", line)
            if not c:
                c = re.search(r"CHECK\s*\((\w+)\s+IN\s*\(([^)]*)\)", line)
            if c:
                values = re.findall(r"'([^']+)'", c.group(2))
                if values:
                    out[(table, c.group(1))] = values
    return out


def drained_states() -> set[tuple[str, str, str]]:
    return {d for p in REGISTRY.values() for d in p.drains}


def check_terminal_states() -> list[str]:
    """
    Hard constraint: every lifecycle state is drained by a predicate or declared
    terminal with a reason.

    A state that is neither is a place work stops while the system reports
    itself finished — and that is invisible to every other check, because
    quiescence is defined as "no predicate fires".
    """
    problems = []
    drained = drained_states()
    for (table, column), values in schema_states().items():
        if (table, column) not in LIFECYCLE_COLUMNS:
            continue
        for value in values:
            key = (table, column, value)
            if key in drained or key in TERMINAL:
                continue
            problems.append(
                f"{table}.{column} = '{value}' has no predicate draining it and is "
                f"not declared terminal — work can stop here silently")
    return problems


def check_predicates_can_fire() -> list[str]:
    """
    A declared drain is not an implemented one.

    `check_terminal_states` reads declarations, so it can be satisfied by lying —
    a predicate that claims to drain a state and does nothing passes it. That is
    exactly what happened: `merge` declared it drained a passing verdict and its
    body was `return []`, in the same commit that claimed to close the dead end.

    Three static checks, all cheap:
      * every table a predicate queries must exist
      * a predicate declaring a drain must actually query that table
      * a predicate must be able to return something
    """
    import inspect

    schema = SCHEMA.read_text(encoding="utf-8")
    tables = set(re.findall(r"CREATE TABLE IF NOT EXISTS (\w+)", schema))
    # A view is a source too. The provenance views stand over `refs`, and a
    # predicate that reads one reads the schema.
    views = set(re.findall(r"CREATE VIEW IF NOT EXISTS (\w+)", schema))
    # A predicate that reads a view queries the tables under the view. A drain
    # on `test_runs` is then met by a read of `latest_runs` (fact F4).
    under = {v: set(re.findall(r"(?:FROM|JOIN) (\w+)", body))
             for v, body in re.findall(
                 r"CREATE VIEW IF NOT EXISTS (\w+) AS(.*?);", schema, re.S)}
    problems = []

    for name, p in REGISTRY.items():
        src = inspect.getsource(p.fn)
        queried = set(re.findall(r"FROM (\w+)", src)) | set(re.findall(r"JOIN (\w+)", src))
        queried |= {t for v in queried & views for t in under.get(v, ())}
        # A predicate may build its table name at runtime (`FROM {table}`), which
        # no static read can follow. Those are exempt rather than falsely flagged.
        dynamic = "FROM {" in src or "from {" in src
        delegated = "from .scheduler import" in src or dynamic

        for t in queried - tables - views:
            if t.isupper() or t in ("sqlite_master",):
                continue
            problems.append(f"{name} queries {t!r}, which is not in the schema")

        body = src.split('"""')[-1]
        if not delegated and body.count("return") and "return []" in body.strip()[-12:]:
            problems.append(f"{name} can never return a wake — its body always returns []")

        for table, _col, value in p.drains:
            if not delegated and table not in queried:
                problems.append(
                    f"{name} declares it drains {table}.{value!r} but never queries {table}")
    return problems


def _parameterised_writes(root: Path) -> set[tuple[str, str]]:
    """
    (table, column) pairs written from an argument rather than a literal.

    Most writes are parameterised — the model supplies `approval='approved'` and
    the sandbox validates it against the column's enum — so there is no literal
    to grep for. Flagging those would bury the real holes in noise.

    This looked only at `api.py`'s `@op` blocks, which was fine while every
    write was a role's. `lifecycle.record_test_run` is not: the harness writes
    a result nobody decided. Walking every function that writes finds both, and
    removes a special case that would have had to grow one entry per exception.
    """
    import ast

    pairs: set[tuple[str, str]] = set()
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError:                      # pragma: no cover
            continue
        for fn in (n for n in ast.walk(tree)
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))):
            body = ast.get_source_segment(source, fn) or ""
            args = {a.arg for a in fn.args.args + fn.args.kwonlyargs} - {"conn", "ctx"}
            # A value taken from the session context is as parameterised as one
            # taken from the call. The wake kind is such a value: it travels as
            # `ctx.onboarding`, a fact about the session, and decides which
            # refs a write records.
            args |= set(re.findall(r"ctx\.(\w+)", body)) - {"conn", "writes",
                                                            "outbound", "role"}

            tables = set(re.findall(r"INSERT (?:OR \w+ )?INTO (\w+)", body))
            tables |= set(re.findall(r"UPDATE (\w+) SET", body))
            # api.py stages writes rather than issuing SQL, so its table name is
            # a tuple element instead of a keyword.
            tables |= set(re.findall(r"""writes\.append\(\(\s*["'](\w+)["']""", body))

            for table in tables:
                for arg in args:
                    pairs.add((table, arg))
    return pairs


def check_states_are_reachable() -> list[str]:
    """
    A state nothing ever writes is a state nothing can be in.

    `batches.status = 'running'` was declared, three predicates depended on it,
    and no code path ever set it — so the whole delivery loop was gated on a
    value that could not occur. Crude grep, but it is the check that would have
    said so.
    """
    schema = SCHEMA.read_text(encoding="utf-8")

    # Only *writes* count. A first attempt grepped every file and found
    # 'running' in a SELECT, so it reported the state reachable when nothing
    # could ever set it. Reading a value and writing one look identical to a
    # grep unless you say which you mean.
    #
    # `rglob` over the package, not `glob` beside the schema: the two used to be
    # the same directory. After the regroup, `SCHEMA.parent` is `core/` and
    # `api.py` — the file holding every artefact write — is in `roles/`.
    writes = (paths.PACKAGE / "roles" / "api.py").read_text(encoding="utf-8")
    for f in sorted(paths.PACKAGE.rglob("*.py")):
        if f.name in ("api.py", "predicates.py") or "__pycache__" in f.parts:
            continue
        text = f.read_text(encoding="utf-8")
        writes += chr(10).join(
            line for line in text.splitlines()
            if "UPDATE " in line or "SET " in line or "INSERT INTO" in line)
    defaults = re.findall(r"DEFAULT '([^']+)'", schema)

    parameterised = _parameterised_writes(paths.PACKAGE)

    problems = []
    for (table, column), values in schema_states().items():
        if (table, column) not in LIFECYCLE_COLUMNS:
            continue
        if (table, column) in parameterised:
            continue
        for value in values:
            if value in defaults:
                continue
            if f"'{value}'" in writes or f'"{value}"' in writes:
                continue
            problems.append(
                f"{table}.{column} = '{value}' is never written by any code path — "
                f"nothing can reach this state, so anything gated on it is dead")
    return problems


def check_predicates_wake_real_roles() -> list[str]:
    from ..design import graph as graph_mod

    legal = set(graph_mod.load().roles) | {DERIVED, SCHEDULER}
    return [f"predicate {p.name!r} wakes {p.wakes!r}, which is not a role"
            for p in REGISTRY.values() if p.wakes not in legal]


def check_bands_are_declared() -> list[str]:
    return [f"predicate {p.name!r} is in band {p.band!r}, which has no order"
            for p in REGISTRY.values() if p.band not in ORDER]


def all_wakes(conn: sqlite3.Connection,
              principal_present: bool = False) -> list[Wake]:
    """
    Every predicate, evaluated, in band order.

    This is the whole frontier, not half of it. It used to be "open message tips
    ∪ the six ticks", which put the definition in two places and left the tips
    invisible to every check written against the other half. `message_tips` is a
    predicate now, and the ∪ is gone.

    Errors are not swallowed. The old version caught `sqlite3.Error` and carried
    on, for predicates over tables that had not been built yet — which meant a
    predicate silently contributing nothing looked exactly like one correctly
    finding nothing. The tables exist; a query that fails now is a bug and
    should say so.
    """
    out: list[Wake] = []
    for p in sorted(REGISTRY.values(), key=lambda p: (p.order, p.seq)):
        if p.needs_principal and not principal_present:
            continue
        out.extend(p.fn(conn))
    return out


if __name__ == "__main__":
    import sys

    print(f"{len(REGISTRY)} predicates, in the order they are offered\n")
    labels = {DERIVED: "(per row)", SCHEDULER: "(scheduler)"}
    band = None
    for p in sorted(REGISTRY.values(), key=lambda p: (p.order, p.seq)):
        if p.band != band:
            band = p.band
            print(f"  --- {band}")
        target = labels.get(p.wakes, p.wakes)
        print(f"  {p.name:22s} -> {target:14s} drains {len(p.drains)}")

    issues = (check_terminal_states() + check_predicates_wake_real_roles()
              + check_bands_are_declared()
              + check_predicates_can_fire() + check_states_are_reachable())
    print()
    if issues:
        print(f"{len(issues)} PROBLEMS:")
        for i in issues:
            print("  -", i)
        sys.exit(1)
    print("every lifecycle state has a way out")


@predicate("touch_strayed", wakes="architect", band="fix",
           drains=[("touch_strays", "status", "open")])
def touch_strayed(conn) -> list[Wake]:
    """
    The head commit touched paths the prediction never named, and nobody
    has said whether that was foreseen or a mistake.

    clickI night 32 (2026-09-13): `echo_json` merged in two files the
    Architect's touch set never named, and nothing asked. The stray rows
    are written by `code.commit`; this wakes the Architect once per batch
    with the paths, and the merge gate waits for the judgement.

    law 12: the touch set is a prediction, never a permission

    Frame 339: a removal's row carries its note, the removed line, on the
    grain's own entry, so the Architect reads the line it judges.
    """
    rows = conn.execute(
        "SELECT b.id AS bid, GROUP_CONCAT(s.path || COALESCE(' (' || s.note || ')', ''), "
        "  ', ') AS paths "
        "FROM batches b JOIN touch_strays s ON s.batch_id = b.id "
        "  AND s.commit_sha = b.head_commit AND s.status = 'open' "
        "WHERE b.status = 'running' AND b.head_commit IS NOT NULL "
        "GROUP BY b.id ORDER BY b.id").fetchall()
    return [Wake("architect", "tick:touch_strayed", refs=(r["bid"],),
                 detail=r["paths"] or "")
            for r in rows]


@predicate("touch_mistaken", wakes="developer", band="fix",
           drains=[("touch_strays", "status", "mistake")])
def touch_mistaken(conn) -> list[Wake]:
    """
    The Architect judged a stray path a mistake, and the head commit still
    carries it. The Developer takes it out; the next commit is a new head
    and the mistake rows stay behind on the old one.
    """
    rows = conn.execute(
        "SELECT b.id AS bid, GROUP_CONCAT(s.path, ', ') AS paths "
        "FROM batches b JOIN touch_strays s ON s.batch_id = b.id "
        "  AND s.commit_sha = b.head_commit AND s.status = 'mistake' "
        "WHERE b.status = 'running' AND b.head_commit IS NOT NULL "
        "  AND NOT EXISTS (SELECT 1 FROM messages m WHERE m.from_role = 'developer' "
        "                  AND m.verb = 'escalate' AND m.status = 'open' "
        "                  AND m.body_refs LIKE '%' || b.id || '%') "
        "GROUP BY b.id ORDER BY b.id").fetchall()
    return [Wake("developer", "tick:touch_mistaken", refs=(r["bid"],),
                 detail=r["paths"] or "")
            for r in rows]
