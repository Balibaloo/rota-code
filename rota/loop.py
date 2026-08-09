"""
The crank.

Everything else was parts: the scheduler picks wakes, the runner runs sessions,
the client pump moves asks and answers. Nothing turned them. This does, and it is
short on purpose — the design's claim is that dispatch is a *query*, so the loop
that consumes it should be almost nothing.

    while frontier:
        pick one tip per the schedule
        wake one role
        commit atomically
        cascade

Gates need this to exist before they mean anything, because a gate is a pause in
a cycle and there was no cycle. L1 is `confirm` sitting unanswered on the client's
side of the pump; Signoff is `present` doing the same. Neither needs machinery of
its own — a gate is what a loop looks like when the client hasn't answered yet.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field

from . import llm
from .client import ClientBackend, pump
from .runner import RunOutcome, run_session
from .scheduler import (
    RoleBusy, Wake, cascade_wakes, frontier, is_quiescent, release,
)


@dataclass
class Step:
    """One turn of the crank, and what it produced."""
    wake: Wake | None = None
    outcome: RunOutcome | None = None
    client_messages: list[str] = field(default_factory=list)
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
    client: ClientBackend | None = None,
    client_present: bool = True,
    max_iterations: int = 8,
) -> Step:
    """
    One iteration: offer pending asks to the client, then wake one role.

    The client is pumped *first* so an answer given between steps lands before
    the frontier is computed — otherwise the system would look quiescent while
    holding a reply it had not read yet.
    """
    result = Step()

    if client is not None:
        result.client_messages = pump(conn, client)

    ready = frontier(conn, client_present=client_present)
    if not ready:
        result.quiescent = True
        result.note = _why_idle(conn)
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

    batch_id = result.wake.refs[0] if result.wake.kind == "tick:batch_start" else None
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


def run(
    conn: sqlite3.Connection,
    *,
    backend: llm.Backend | None = None,
    pins: llm.Pins | None = None,
    client: ClientBackend | None = None,
    client_present: bool = True,
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
        s = step(conn, backend=backend, pins=pins, client=client,
                 client_present=client_present)
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

    Waiting on the client is a *gate* and is healthy. An empty frontier with
    nothing pending is quiescence. They look identical in a log and are entirely
    different situations.
    """
    waiting = [dict(r) for r in conn.execute(
        "SELECT verb, body_refs FROM messages WHERE status = 'open' AND to_role = 'client'")]
    if waiting:
        verbs = ", ".join(sorted({w["verb"] for w in waiting}))
        return f"gate: waiting on the client ({verbs})"
    open_ledger = conn.execute(
        "SELECT COUNT(*) n FROM ledger WHERE status = 'open'").fetchone()["n"]
    if open_ledger:
        return f"idle with {open_ledger} open assumption(s)"
    return "nothing pending"


def gates_open(conn: sqlite3.Connection) -> list[dict]:
    """Everything the client is currently being waited on for."""
    import json

    return [
        {"id": r["id"], "verb": r["verb"], "refs": json.loads(r["body_refs"] or "[]")}
        for r in conn.execute(
            "SELECT id, verb, body_refs FROM messages "
            "WHERE status = 'open' AND to_role = 'client' ORDER BY seq")
    ]
