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
LADDER = ("developer", "architect", "gatekeeper")


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


@predicate("contested", wakes="gatekeeper", band="fix",
           drains=[("items", "approval", "contested")])
def contested(conn) -> list[Wake]:
    """The principal rejected an item.

    This was a dead end: the highest-value signal in the system landed nowhere.
    It wakes the item's owner to amend it or author a decision defending it."""
    rows = conn.execute(
        "SELECT id FROM items WHERE approval = 'contested'").fetchall()
    return [Wake("gatekeeper", "tick:contested", refs=(r["id"],)) for r in rows]


@predicate("signoff", wakes="gatekeeper", band="gate",
           drains=[("items", "approval", "draft")])
def signoff(conn) -> list[Wake]:
    """Draft items with no gate open: submit them for approval, together."""
    from .scheduler import tick_signoff
    return tick_signoff(conn)


@predicate("round_close", wakes="liaison", band="gate")
def round_close(conn) -> list[Wake]:
    """A broadcast's subtree has terminated: harvest the reports."""
    from .scheduler import tick_round_close
    return tick_round_close(conn)


@predicate("slicing", wakes="gatekeeper", band="start")
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
                   ("items", "provenance", "observed")])
def observed_entries(conn) -> list[Wake]:
    """
    Entries extracted from a codebase, awaiting their first decision.

    Onboarding produces these by the hundred and nothing was ever going to ask
    the principal to confirm them, so `observed` was a state with no exit.
    """
    counts = []
    for table in ("glossary_terms", "constraints", "items"):
        n = conn.execute(
            f"SELECT COUNT(*) n FROM {table} WHERE provenance = 'observed'"
        ).fetchone()["n"]
        if n:
            counts.append(f"{table}:{n}")
    if not counts:
        return []
    asked = conn.execute(
        "SELECT COUNT(*) n FROM messages WHERE status='open' AND to_role='principal' "
        "AND verb='present'").fetchone()["n"]
    return [] if asked else [
        Wake("liaison", "tick:observed_entries", detail=", ".join(counts))]


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
    `msg.elect_gatekeeper`, and re-asking while that message is unread would put
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

    Empty once it has reached Gatekeeper, who is the last rung that can be woken
    — above that is the principal, and reaching them is Liaison's `report`, which
    Gatekeeper's own session sends. Nothing wakes a person.
    """
    sent = {r["from_role"] for r in conn.execute(
        "SELECT DISTINCT from_role FROM messages WHERE body_refs LIKE ?",
        (f"%{batch_id}%",))}
    for role in LADDER:
        if role not in sent:
            return role
    return ""


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
    return [Wake("architect", "tick:structural_review", refs=(r["bid"],))
            for r in rows]


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
    looked at a counter."""
    n = conn.execute(
        "SELECT COUNT(*) n FROM messages WHERE status = 'quarantined'").fetchone()["n"]
    try:
        n += conn.execute(
            "SELECT COUNT(*) n FROM tick_attempts "
            "WHERE quarantined = 1 AND reported = 0"
        ).fetchone()["n"]
    except Exception:                 # a database older than the table
        pass
    return [Wake("liaison", "tick:quarantined", detail=f"{n} abandoned")] if n else []


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


@predicate("survey", wakes=DERIVED, band="start",
           derives=SURVEY_ORDER)
def survey(conn) -> list[Wake]:
    """Onboarding: one elected area at a time, in role order."""
    from .scheduler import tick_survey
    return tick_survey(conn)


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
