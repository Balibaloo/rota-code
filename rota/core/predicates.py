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

from .scheduler import SURVEY_ORDER, Wake

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
        REGISTRY[name] = Predicate(
            name=name, wakes=wakes, drains=tuple(drains), fn=fn,
            why=why or (fn.__doc__ or "").strip(),
            band=band, needs_principal=needs_principal,
            derives=tuple(derives))
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
    ("items", "provenance"),
    ("glossary_terms", "provenance"),
    ("constraints", "provenance"),
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
    ("statements", "status", "ratified"):
        "the principal confirmed it; it is now material, not pending work",
    ("statements", "status", "superseded"):
        "replaced by a later statement, which carries the work forward",
    ("statements", "status", "clarified"):
        "the ambiguity was resolved in a later statement",
    ("items", "approval", "approved"):
        "drained by slicing once tickets exist; approval itself owes nothing",
    ("items", "approval", "pending"):
        "an open gate to the principal holds it; the gate is the pending work",
    ("items", "provenance", "decided"):
        "someone chose it and the reason is on file",
    ("glossary_terms", "provenance", "decided"): "reason on file",
    ("constraints", "provenance", "decided"): "reason on file",
    # `cited` is law 11's third value: found outside the repository, attributable
    # to a source. Terminal for the same reason the other two are — provenance
    # records where a row came from and is not a stage anything moves through.
    #
    # It is the only provenance that can become false without anyone touching
    # the project, but that is *drift*, and drift is drained by waking the owner
    # of whatever cited a changed source. It is not a state this row is stuck in.
    ("items", "provenance", "cited"): "found outside; the source is on file",
    ("glossary_terms", "provenance", "cited"): "found outside; the source is on file",
    ("constraints", "provenance", "cited"): "found outside; the source is on file",
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
    asked = conn.execute(
        "SELECT COUNT(*) n FROM messages WHERE status='open' AND to_role='principal' "
        "AND verb='clarify'").fetchone()["n"]
    return [] if asked else [
        Wake("liaison", "tick:contradiction", refs=tuple(r["id"] for r in rows))]


@predicate("contested", wakes="vision_keeper", band="fix",
           drains=[("items", "approval", "contested")])
def contested(conn) -> list[Wake]:
    """The principal rejected an item.

    This was a dead end: the highest-value signal in the system landed nowhere.
    It wakes the item's owner to amend it or author a decision defending it."""
    rows = conn.execute(
        "SELECT id FROM items WHERE approval = 'contested'").fetchall()
    return [Wake("vision_keeper", "tick:contested", refs=(r["id"],)) for r in rows]


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

    ruled: set[str] = set()
    for d in conn.execute("SELECT refs FROM decisions"):
        try:
            ruled.update(json.loads(d["refs"] or "[]"))
        except (ValueError, TypeError):
            continue

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

    wakes = []
    for r in rows:
        ids = sorted(r["ids"].split(","))
        if any(i in ruled for i in ids):
            continue                      # somebody has ruled on this word
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
    rows = conn.execute(
        "SELECT DISTINCT c.ticket_id AS tid FROM criteria c "
        "WHERE c.ticket_id NOT IN (SELECT ticket_id FROM batch_tickets)"
    ).fetchall()
    if not rows:
        return []
    return [Wake("architect", "tick:grouping",
                 refs=tuple(r["tid"] for r in rows))]


@predicate("observed_entries", wakes="liaison", band="start",
           drains=[("glossary_terms", "provenance", "observed"),
                   ("constraints", "provenance", "observed"),
                   ("model_areas", "provenance", "observed"),
                   ("items", "provenance", "observed")])
def observed_entries(conn) -> list[Wake]:
    """
    Entries extracted from a codebase, awaiting their first decision.

    Onboarding produces these by the hundred and nothing was ever going to ask
    the principal to confirm them, so `observed` was a state with no exit.
    """
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

    counts, offered = [], []
    for table in ("glossary_terms", "constraints", "model_areas", "items"):
        rows = [r["id"] for r in conn.execute(
            f"SELECT id FROM {table} WHERE provenance = 'observed' ORDER BY id")]
        fresh = [i for i in rows if i not in presented]
        if fresh:
            counts.append(f"{table}:{len(fresh)}")
            offered += fresh
    # A deferral is an election. A present answered without a ruling -- the
    # principal read it and moved on -- left its rows in limbo: not decided,
    # not ledgered, and never re-offered, because a row is put to them once.
    # The put-once rule assumed a ruling always comes. It does not, and the
    # lazy path is what deferral *means*: those rows become assumptions
    # awaiting first touch, exactly as if the election had said so, without
    # re-spending the attention that was already declined.
    limbo = []
    for r in conn.execute(
            "SELECT m.body_refs FROM messages m WHERE m.verb='present' "
            "AND m.status='answered' AND NOT EXISTS ("
            "  SELECT 1 FROM messages v WHERE v.cause_id = m.id "
            "    AND v.verb = 'verdict')"):
        try:
            limbo += [x for x in json.loads(r["body_refs"] or "[]")
                      if isinstance(x, str)]
        except (TypeError, ValueError):
            continue
    if limbo:
        deferred = {r["about_ref"] for r in conn.execute(
            "SELECT about_ref FROM ledger")}
        still = [i for i in dict.fromkeys(limbo)
                 if i in presented and i not in deferred and any(
                     conn.execute(f"SELECT 1 FROM {t} WHERE id = ? AND "
                                  f"provenance='observed'", (i,)).fetchone()
                     for t in ("glossary_terms", "constraints",
                               "model_areas", "items"))]
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
    election = conn.execute(
        "SELECT value FROM config WHERE key = 'baseline_election'").fetchone()
    if election and election["value"].strip('"') == "lazy":
        deferred = {r["about_ref"] for r in conn.execute(
            "SELECT about_ref FROM ledger")}
        fresh = [i for i in offered if i not in deferred]
        return [Wake(SCHEDULER, "do:defer_baseline", refs=tuple(fresh),
                     detail=", ".join(counts))] if fresh else []

    asked = conn.execute(
        "SELECT COUNT(*) n FROM messages WHERE status='open' AND to_role='principal' "
        "AND verb='present'").fetchone()["n"]
    # The ids ride the wake. Liaison's `observed_entries` mode holds one send
    # and no read that could enumerate these tables -- live, woken with counts
    # alone, it was asked to name 91 rows it cannot see, invented a dict ref,
    # and the present never went out. The predicate counted the rows; it names
    # them.
    return [] if asked else [
        Wake("liaison", "tick:observed_entries", refs=tuple(offered),
             detail=", ".join(counts))]


# ---------------------------------------------------------------------------
# Delivery loop — one predicate existed; these are the rest
# ---------------------------------------------------------------------------

@predicate("tests_missing", wakes="tester", band="start")
def tests_missing(conn) -> list[Wake]:
    """Criteria for a batch with no tests. Tester needs only criteria, so it can
    run as soon as they exist — it does not wait for the Developer."""
    rows = conn.execute(
        "SELECT DISTINCT bt.batch_id AS bid FROM batch_tickets bt "
        "JOIN criteria c ON c.ticket_id = bt.ticket_id "
        "WHERE bt.batch_id NOT IN (SELECT batch_id FROM tests)"
    ).fetchall()
    return [Wake("tester", "tick:tests_missing", refs=(r["bid"],)) for r in rows]


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
    rows = conn.execute(
        "SELECT b.id AS bid FROM batches b "
        "WHERE b.status = 'running' AND b.head_commit IS NOT NULL "
        "  AND b.id IN (SELECT batch_id FROM tests) "
        "  AND NOT EXISTS (SELECT 1 FROM test_runs r "
        "                  WHERE r.batch_id = b.id AND r.commit_sha = b.head_commit)"
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
    rows = conn.execute(
        "SELECT id FROM batches WHERE status IN ('pending','deferred') "
        "  AND id NOT IN (SELECT DISTINCT batch_id FROM batch_touch)"
        "  LIMIT 1"
    ).fetchall()
    return [Wake("architect", "tick:annotate", refs=(r["id"],)) for r in rows]


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
    rows = conn.execute(
        "SELECT DISTINCT batch_id AS bid, MAX(attempt) AS att FROM test_runs "
        "WHERE result IN ('fail','error') GROUP BY batch_id"
    ).fetchall()
    return [Wake("developer", "tick:tests_failing", refs=(r["bid"],),
                 detail=f"attempt {r['att']}")
            for r in rows if (r["att"] or 1) < cap]


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
    A batch that hit `loop_cap` and stopped bouncing.

    `tests_failing` goes quiet above the cap, which on its own is abandonment
    wearing the clothes of a budget: the work is still undone, nothing fires,
    and the system reports itself quiescent. Exhaustion escalates instead.

    One rung at a time, because the usual *reason* a loop exhausts itself is not
    knowing who to ask — and handing it straight to the principal skips the two
    people who could have answered it. The rung is derived from what has already
    been sent about this batch rather than stored, so it cannot drift out of step
    with the messages that are the actual escalation.
    """
    from . import config

    cap = config.get(conn, "loop_cap")
    rows = conn.execute(
        "SELECT batch_id AS bid, MAX(attempt) AS att FROM test_runs "
        "WHERE result IN ('fail','error') GROUP BY batch_id"
    ).fetchall()

    wakes = []
    for r in rows:
        if (r["att"] or 1) < cap:
            continue                       # still bouncing; tests_failing has it
        role = _next_rung(conn, r["bid"])
        if role:
            wakes.append(Wake(role, "tick:exhausted", refs=(r["bid"],),
                              detail=f"attempt {r['att']} of {cap}"))
    return wakes


def _next_rung(conn, batch_id: str) -> str:
    """
    Who has not yet been asked about this batch.

    Empty once it has reached Vision Keeper, who is the last rung that can be woken
    — above that is the principal, and reaching them is Liaison's `report`, which
    Vision Keeper's own session sends. Nothing wakes a person.
    """
    sent = {r["from_role"] for r in conn.execute(
        "SELECT DISTINCT from_role FROM messages WHERE body_refs LIKE ?",
        (f"%{batch_id}%",))}
    for role in LADDER:
        if role not in sent:
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
        "SELECT id, from_role, thread_id, unresolved_note FROM messages "
        "WHERE status = 'unresolved' ORDER BY seq").fetchall()
    if not rows:
        return []

    g = graph_mod.load()
    can_answer: dict[str, set[str]] = {}
    for e in g.of_type("messages"):
        if e.v == "answer":
            can_answer.setdefault(e.t, set()).add(e.s)

    wakes = []
    for r in rows:
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
            if r["from_role"] == "liaison":
                wakes.append(Wake("liaison", "tick:unresolved", refs=(r["id"],),
                                  detail=r["unresolved_note"] or ""))
    return wakes


def _names_a_criterion(conn, message_id: str) -> bool:
    refs = _refs_of(conn.execute(
        "SELECT body_refs FROM messages WHERE id = ?",
        (message_id,)).fetchone()["body_refs"])
    return any(conn.execute("SELECT 1 FROM criteria WHERE id = ?",
                            (ref,)).fetchone() for ref in refs)


def _repair_attempted(conn, message_id: str) -> bool:
    return bool(conn.execute(
        "SELECT 1 FROM sessions WHERE wake_kind = 'tick:criterion_repair' "
        "AND wake_refs LIKE ?", (f'%"{message_id}"%',)).fetchone())


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
    rows = conn.execute(
        "SELECT b.id AS bid FROM batches b "
        "WHERE b.status = 'running' AND b.head_commit IS NOT NULL "
        "  AND NOT EXISTS (SELECT 1 FROM verdicts v "
        "                  WHERE v.batch_id = b.id AND v.commit_sha = b.head_commit) "
        "  AND NOT EXISTS (SELECT 1 FROM test_runs r "
        "                  WHERE r.batch_id = b.id AND r.commit_sha = b.head_commit "
        "                    AND r.result != 'pass') "
        "  AND EXISTS (SELECT 1 FROM test_runs r "
        "              WHERE r.batch_id = b.id AND r.commit_sha = b.head_commit)"
    ).fetchall()
    return [Wake("critic", "tick:review", refs=(r["bid"],)) for r in rows]


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
    """A failed verdict with no newer commit: the Developer has not answered it."""
    rows = conn.execute(
        "SELECT v.batch_id AS bid FROM verdicts v JOIN batches b ON b.id = v.batch_id "
        "WHERE v.result = 'fail' AND b.status = 'running'"
    ).fetchall()
    return [Wake("developer", "tick:verdict_failed", refs=(r["bid"],)) for r in rows]


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
    dead = conn.execute(
        "SELECT body_refs FROM messages WHERE status = 'quarantined'").fetchall()
    # Ordered, deduplicated, and never the message ids: one dead delivery can
    # carry several items, and two can carry the same one.
    refs: list[str] = []
    for row in dead:
        for ref in _refs_of(row["body_refs"]):
            if ref not in refs:
                refs.append(ref)

    n = len(dead)
    try:
        n += conn.execute(
            "SELECT COUNT(*) n FROM tick_attempts "
            "WHERE quarantined = 1 AND reported = 0"
        ).fetchone()["n"]
    except Exception:                 # a database older than the table
        pass
    # A stalled tick has no payload to offer and that is the honest answer
    # rather than a hole: it was never about an item, so there is nothing to
    # name. It still wakes, because a tick that cannot drain is the worse half.
    return [Wake("liaison", "tick:quarantined", refs=tuple(refs),
                 detail=f"{n} abandoned")] if n else []


@predicate("agenda", wakes="liaison", band="gate", needs_principal=True,
           drains=[("ledger", "status", "open")])
def agenda(conn) -> list[Wake]:
    """On principal presence, present what is blocked on them."""
    from .scheduler import tick_agenda
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
    want = {r["area"] for r in conn.execute(
        "SELECT DISTINCT area FROM code_index WHERE area IS NOT NULL")} - surveyed

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
    "checkpoint_invalid", "survey", "term_collision", "unresolved",
    "orient", "define", "boundary", "frame", "reorient", "challenge",
    "blindspot", "criterion_repair",
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
    problems = []

    for name, p in REGISTRY.items():
        src = inspect.getsource(p.fn)
        queried = set(re.findall(r"FROM (\w+)", src)) | set(re.findall(r"JOIN (\w+)", src))
        # A predicate may build its table name at runtime (`FROM {table}`), which
        # no static read can follow. Those are exempt rather than falsely flagged.
        dynamic = "FROM {" in src or "from {" in src
        delegated = "from .scheduler import" in src or dynamic

        for t in queried - tables:
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
            # taken from the call. `provenance` stopped being an argument when
            # Architect filled it with the name of its own mode — it is a fact
            # about the session now, and `ctx.provenance` is where it comes from.
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
    for p in sorted(REGISTRY.values(), key=lambda p: (p.order, p.name)):
        if p.needs_principal and not principal_present:
            continue
        out.extend(p.fn(conn))
    return out


if __name__ == "__main__":
    import sys

    print(f"{len(REGISTRY)} predicates, in the order they are offered\n")
    labels = {DERIVED: "(per row)", SCHEDULER: "(scheduler)"}
    band = None
    for p in sorted(REGISTRY.values(), key=lambda p: (p.order, p.name)):
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
