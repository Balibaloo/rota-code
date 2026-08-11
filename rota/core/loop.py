"""
The crank.

Everything else was parts: the scheduler picks wakes, the runner runs sessions,
the principal pump moves asks and answers. Nothing turned them. This does, and it is
short on purpose — the design's claim is that dispatch is a *query*, so the loop
that consumes it should be almost nothing.

    while frontier:
        pick one tip per the schedule
        wake one role
        commit atomically
        cascade

Gates need this to exist before they mean anything, because a gate is a pause in
a cycle and there was no cycle. L1 is `confirm` sitting unanswered on the principal's
side of the pump; Signoff is `present` doing the same. Neither needs machinery of
its own — a gate is what a loop looks like when the principal hasn't answered yet.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field

from . import config
from . import lifecycle
from ..llm import llm
from ..roles.principal import PrincipalBackend, pump
from .predicates import SCHEDULER
from .runner import RunOutcome, run_session
from .scheduler import (
    RoleBusy, Wake, cascade_wakes, frontier, is_quiescent, release,
)


@dataclass
class Step:
    """One turn of the crank, and what it produced."""
    wake: Wake | None = None
    outcome: RunOutcome | None = None
    principal_messages: list[str] = field(default_factory=list)
    cascaded: list[str] = field(default_factory=list)
    quiescent: bool = False
    note: str = ""
    productive: bool = False        # did this session change anything?

    def __str__(self) -> str:
        if self.quiescent:
            return f"quiescent ({self.note})" if self.note else "quiescent"
        head = str(self.wake) if self.wake else "-"
        if self.outcome:
            state = "ok" if self.outcome.committed else f"FAILED {self.outcome.errors[:1]}"
            return f"{head} -> {state}"
        return f"{head} -> {self.note}"


@dataclass
class Stuck(Exception):
    """
    A predicate fired, its session changed nothing, and the predicate fired again.

    This is the failure mode that comes with frontier-as-state: predicates are
    re-derived every pass, so a session that does not satisfy the predicate that
    woke it will be woken by it forever. The loop is the only place that can see
    it, because from inside a session everything looks fine — it committed.

    Reported rather than spun on, because "stuck" and "idle" look identical in a
    log and are entirely different situations.
    """
    wake: Wake | None = None
    repeats: int = 0

    def __str__(self) -> str:
        return (f"{self.wake} fired {self.repeats}x without changing state; "
                f"its session commits but does not satisfy the predicate")


@dataclass
class Trace:
    steps: list[Step] = field(default_factory=list)
    stuck: Stuck | None = None

    def render(self) -> str:
        return "\n".join(f"{i:3d}. {s}" for i, s in enumerate(self.steps, 1))

    @property
    def committed(self) -> int:
        return sum(1 for s in self.steps if s.outcome and s.outcome.committed)

    @property
    def failures(self) -> list[Step]:
        return [s for s in self.steps if s.outcome and not s.outcome.committed]

    @property
    def productive(self) -> int:
        return sum(1 for s in self.steps if s.productive)


def step(
    conn: sqlite3.Connection,
    *,
    backend: llm.Backend | None = None,
    pins: llm.Pins | None = None,
    principal: PrincipalBackend | None = None,
    principal_present: bool = True,
    max_iterations: int | None = None,
) -> Step:
    """
    One iteration: offer pending asks to the principal, then wake one role.

    The principal is pumped *first* so an answer given between steps lands before
    the frontier is computed — otherwise the system would look quiescent while
    holding a reply it had not read yet.
    """
    # One number, in one place. The loop defaulted to 8 while the runner's own
    # cap was 12, so a session dispatched by the scheduler got a third less
    # budget than the same session run by a case -- and survey sessions, which
    # are the longest, were the ones that ran out.
    if max_iterations is None:
        from .runner import MAX_ITERATIONS

        max_iterations = MAX_ITERATIONS

    result = Step()

    # Intake lands whether or not the system is dispatching. Recording what the
    # principal said and hearing their answers costs nothing and revokes
    # nothing; a stopped system that also stopped listening would just be a
    # broken one, and the work would be waiting anyway when it resumed.
    if principal is not None:
        result.principal_messages = pump(conn, principal)

    if not config.dispatchable(conn):
        state = config.get(conn, "run_state")
        holding = conn.execute("SELECT COUNT(*) n FROM claims").fetchone()["n"]
        if state == "stopping" and holding:
            result.note = f"stopping: {holding} session(s) still in flight"
            return result
        result.quiescent = True
        result.note = f"{state}: resume is explicit"
        return result

    ready = frontier(conn, principal_present=principal_present)
    if not ready:
        result.quiescent = True
        result.note = _why_idle(conn)
        return result

    # Actions the scheduler performs itself. They wake nobody, cost no model
    # call, and unblock role work — so they go before dispatch rather than
    # queueing behind it.
    #
    # Routed on *who it is addressed to*, not on how the kind is spelled. There
    # were three ways to say "not a role" — `""`, `SCHEDULER`, and a `do:`
    # prefix — and this checked only the prefix. `constraint_zero` uses the other
    # two, so a real onboarding produced a wake addressed to `-` that fell
    # through to dispatch and died on `'-' is not a role in the graph`. The
    # action had a test; the routing to it did not, because the test called
    # `_perform` directly.
    for wake in ready:
        if wake.role in ("", SCHEDULER) or wake.kind.startswith("do:"):
            result.wake = wake
            result.note = _perform(conn, wake)
            result.productive = True
            return result

    # Skip roles that already hold a claim: single-instance is a property to
    # respect here, not an error to raise.
    for wake in ready:
        held = conn.execute(
            "SELECT session_id FROM claims WHERE role = ?", (wake.role,)).fetchone()
        if held:
            continue
        result.wake = wake
        break

    if result.wake is None:
        result.quiescent = True
        result.note = "every ready role is busy"
        return result

    # Which batch a session works in is the scheduler's to say, and it says so
    # from the wake. This read `refs[0] if kind == "tick:batch_start"`, so a
    # Developer woken by `tests_failing` or `verdict_failed` — both of which
    # carry the batch in `refs` — arrived with no worktree and could not reach
    # the code it had been woken to fix.
    # Count this dispatch before it runs, so a session that crashes still
    # spends an attempt. A tick that keeps being produced unchanged is the one
    # shape law 4 had no bound for.
    from .scheduler import note_dispatch

    note_dispatch(conn, result.wake)
    batch_id = _batch_of(conn, result.wake)
    if result.wake.kind == "tick:batch_start" and batch_id:
        # The batch is running from the moment it is dispatched, not from
        # whenever the session gets round to saying so. `batch_start` refuses
        # while anything is running, so leaving this to the session would let a
        # second batch start in the gap.
        lifecycle.start(conn, batch_id)
    try:
        result.outcome = run_session(
            conn, result.wake, backend=backend, pins=pins,
            batch_id=batch_id, max_iterations=max_iterations)
    except RoleBusy as exc:
        result.note = str(exc)
        return result

    if result.outcome.committed:
        res = result.outcome.result
        result.productive = bool(res and (res.writes or res.messages))
        result.cascaded = [str(w) for w in cascade_wakes(conn, result.outcome.session_id)]
    else:
        release(conn, result.wake.role)

    return result


def _batch_of(conn: sqlite3.Connection, wake: Wake) -> str | None:
    """
    The batch a session works in, decided by the scheduler rather than the role.

    Named in the wake's refs where the predicate knows it — `batch_start`,
    `tests_failing`, `verdict_failed`, `review` all carry it. Where it is not,
    the wake is a message and the batch is the one that is running: `batch_start`
    refuses while anything else is, so "the running batch" is unambiguous by
    construction. Returning None is the honest answer when nothing is running,
    and leaves the session with no worktree — which is correct, because there is
    no work in flight for it to be in.
    """
    for ref in wake.refs:
        if conn.execute("SELECT 1 FROM batches WHERE id = ?", (ref,)).fetchone():
            return ref
    rows = conn.execute("SELECT id FROM batches WHERE status = 'running'").fetchall()
    return rows[0]["id"] if len(rows) == 1 else None


def _perform(conn: sqlite3.Connection, wake: Wake) -> str:
    """
    Do what the scheduler said to do.

    These are the predicates that wake nobody. A merge is not a judgement — the
    verdict already made it, the findings already cleared it — so dispatching a
    session to press the button would be inventing a decision to have.
    """
    action = wake.kind.split(":", 1)[1]
    if action == "merge":
        for batch_id in wake.refs:
            lifecycle.merge(conn, batch_id)
        return f"merged {', '.join(wake.refs)}"
    if action == "harness":
        from . import harness

        done = []
        for batch_id in wake.refs:
            results = harness.run(conn, batch_id)
            failed = sum(1 for _, r in results if r != "pass")
            done.append(f"{batch_id}: {len(results)} test(s), {failed} not passing")
        return "; ".join(done)
    if action == "constraint_zero":
        from ..onboarding import boot

        remaining = boot.refresh_constraint_zero(conn)
        return f"constraint zero now covers {remaining} unsurveyed area(s)"
    return f"unknown action {action!r}"


def run(
    conn: sqlite3.Connection,
    *,
    backend: llm.Backend | None = None,
    pins: llm.Pins | None = None,
    principal: PrincipalBackend | None = None,
    principal_present: bool = True,
    max_steps: int = 40,
    stop_on_failure: bool = False,
    on_step=None,
) -> Trace:
    """
    Turn the crank until quiescent or the budget runs out.

    `max_steps` is a tripwire, not a quota — a loop that needs forty sessions to
    settle a toy request is telling you something, and the trace is how you find
    out what.
    """
    trace = Trace()
    barren: dict[str, int] = {}

    for _ in range(max_steps):
        s = step(conn, backend=backend, pins=pins, principal=principal,
                 principal_present=principal_present)
        trace.steps.append(s)
        if on_step:
            on_step(s)
        if s.quiescent:
            break
        if stop_on_failure and s.outcome and not s.outcome.committed:
            break

        # Livelock guard. A wake that commits but changes nothing will be
        # re-derived next pass and wake the same role again, forever.
        if s.wake is not None:
            key = str(s.wake)
            if s.productive:
                barren.pop(key, None)
            else:
                barren[key] = barren.get(key, 0) + 1
                if barren[key] >= 2:
                    trace.stuck = Stuck(wake=s.wake, repeats=barren[key])
                    s.note = str(trace.stuck)
                    break

    return trace


def _why_idle(conn: sqlite3.Connection) -> str:
    """
    Distinguish the two kinds of nothing-happening.

    Waiting on the principal is a *gate* and is healthy. An empty frontier with
    nothing pending is quiescence. They look identical in a log and are entirely
    different situations.
    """
    state = config.get(conn, "run_state")
    if state != "running":
        return f"{state} by the principal; resume is explicit"

    waiting = [dict(r) for r in conn.execute(
        "SELECT verb, body_refs FROM messages WHERE status = 'open' AND to_role = 'principal'")]
    if waiting:
        verbs = ", ".join(sorted({w["verb"] for w in waiting}))
        return f"gate: waiting on the principal ({verbs})"
    open_ledger = conn.execute(
        "SELECT COUNT(*) n FROM ledger WHERE status = 'open'").fetchone()["n"]
    if open_ledger:
        return f"idle with {open_ledger} open assumption(s)"
    return "nothing pending"


def gates_open(conn: sqlite3.Connection) -> list[dict]:
    """Everything the principal is currently being waited on for."""
    import json

    return [
        {"id": r["id"], "verb": r["verb"], "refs": json.loads(r["body_refs"] or "[]")}
        for r in conn.execute(
            "SELECT id, verb, body_refs FROM messages "
            "WHERE status = 'open' AND to_role = 'principal' ORDER BY seq")
    ]
