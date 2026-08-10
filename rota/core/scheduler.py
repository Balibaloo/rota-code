"""
The scheduler: stateless, disposable, ~one loop.

It holds nothing. The frontier is a query, the schedule is derived, claims and
checkpoints are rows. Killing and restarting it at any moment loses nothing —
that is a required property with its own test, and it is what makes hand-rolling
it safe: this file can be deleted and rewritten against the database contract.

Frontier = open message tips ∪ tick predicates evaluated against current state.

The second half matters as much as the first. An approved item with no tickets is
not a message, it is a *state*; nothing would ever wake Gatekeeper for it. Because the
predicates are re-evaluated every pass, residual work cannot be lost — deferred
batches, half-sliced items, criteria-less tickets are all re-derived from state.
That is also why the scheduler can be thrown away: pending work was never held in
memory to lose.

Quiescence = no open tips + no predicate firing + no schedulable batch.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from graphlib import CycleError, TopologicalSorter
from typing import Callable, Iterable

from ..design import graph as graph_mod


@dataclass(frozen=True)
class Wake:
    """One unit of work: a role to wake, and what woke it."""
    role: str
    kind: str                       # 'message' | tick name | 'cascade'
    message_id: str | None = None
    refs: tuple[str, ...] = ()
    detail: str = ""

    def __str__(self) -> str:
        src = self.message_id or self.detail or ""
        return f"{self.role}<-{self.kind}({src})"


# ---------------------------------------------------------------------------
# Message tips
# ---------------------------------------------------------------------------

def open_tips(conn: sqlite3.Connection) -> list[Wake]:
    """
    Messages awaiting a session: open, not quarantined, addressed to a role.

    Messages to the principal are open too, but the principal is not schedulable — it
    answers when it answers. They are excluded here and surfaced by the agenda
    tick instead.

    Reports inside a broadcast round are excluded for the same kind of reason:
    they are not addressed to a session, they are addressed to a *harvest*.
    `tick_round_close` says why — dedupe "is impossible if Liaison wakes per
    report" — and until this exclusion existed the scheduler did exactly that.
    Tips are `traffic`, band 0; round_close is `gate`, band 20. The first report
    won the race every time, Liaison clarified from the one report it could see,
    and the `harvested` check then suppressed round_close permanently. The round
    was in the design, in the docstring, and in the prompt, and it never ran.

    A report *outside* a broadcast thread still tips, and that is the whole of
    what `report` mode is for: the top of the escalation ladder, where Gatekeeper
    has run out of rungs and the next step is a person.
    """
    rows = conn.execute(
        "SELECT id, to_role, verb FROM messages m "
        "WHERE status = 'open' AND to_role != 'principal' "
        "  AND NOT (verb = 'report' AND to_role = 'liaison' AND EXISTS ("
        "    SELECT 1 FROM messages d WHERE d.thread_id = m.thread_id "
        "      AND d.verb = 'deliver' AND d.from_role = 'liaison')) "
        "ORDER BY seq"
    ).fetchall()
    return [
        Wake(role=r["to_role"], kind="message", message_id=r["id"], detail=r["verb"])
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Tick predicates. Each is a pure query over current state.
# ---------------------------------------------------------------------------

def tick_round_close(conn: sqlite3.Connection) -> list[Wake]:
    """
    Liaison harvests once a broadcast's whole subtree has terminated.

    A round exists for one reason: dedupe. Two roles reporting the same blocker
    in different vocabulary must become one question, which is impossible if
    Liaison wakes per report. Waiting is the feature.

    A role with nothing to say emits nothing — the committed session is the
    terminator, so silence is legible without a null-message convention.
    """
    broadcasts = conn.execute(
        "SELECT DISTINCT thread_id FROM messages WHERE verb = 'deliver' AND from_role = 'liaison'"
    ).fetchall()

    wakes = []
    for b in broadcasts:
        thread = b["thread_id"]
        # Every recipient of the broadcast has committed, and nothing in the
        # subtree is still open (a terminologist->gatekeeper challenge keeps it open).
        pending = conn.execute(
            "SELECT COUNT(*) AS n FROM messages "
            "WHERE thread_id = ? AND status = 'open' AND to_role != 'liaison'",
            (thread,),
        ).fetchone()["n"]
        if pending:
            continue
        # Reports harvested already?
        harvested = conn.execute(
            "SELECT COUNT(*) AS n FROM messages "
            "WHERE thread_id = ? AND from_role = 'liaison' AND verb IN ('clarify','present')",
            (thread,),
        ).fetchone()["n"]
        reports = conn.execute(
            "SELECT COUNT(*) AS n FROM messages WHERE thread_id = ? AND verb = 'report'",
            (thread,),
        ).fetchone()["n"]
        if reports and not harvested:
            wakes.append(Wake("liaison", "tick:round_close", refs=(thread,),
                              detail=f"{reports} report(s)"))
    return wakes


def tick_slicing(conn: sqlite3.Connection) -> list[Wake]:
    """
    Gatekeeper slices tickets from items whose approval postdates their last
    amendment. Fires per *gate result* rather than per item: one session with the
    whole batch of approvals is cheaper and better informed.
    """
    rows = conn.execute(
        "SELECT id FROM items "
        "WHERE kind = 'in_scope' AND approval = 'approved' "
        "  AND approval_ver >= version "
        "  AND id NOT IN (SELECT item_id FROM tickets)"
    ).fetchall()
    if not rows:
        return []
    return [Wake("gatekeeper", "tick:slicing", refs=tuple(r["id"] for r in rows))]


def tick_criteria(conn: sqlite3.Connection) -> list[Wake]:
    """
    Terminologist writes criteria for tickets that have none. Fires per *item*: criteria
    written for one ticket in isolation is how you get criteria that contradict
    their siblings.
    """
    rows = conn.execute(
        "SELECT DISTINCT t.item_id AS item_id FROM tickets t "
        "WHERE t.id NOT IN (SELECT ticket_id FROM criteria)"
    ).fetchall()
    return [
        Wake("terminologist", "tick:criteria", refs=(r["item_id"],))
        for r in rows
    ]


def tick_batch_start(conn: sqlite3.Connection) -> list[Wake]:
    """
    Start the next batch: schedulable, ordered first, and nothing running
    (Developer is single-instance).

    Schedulable is the revocation predicate: the batch's item must be approved
    *and* that approval must postdate the item's last amendment.
    """
    running = conn.execute(
        "SELECT COUNT(*) AS n FROM batches WHERE status = 'running'"
    ).fetchone()["n"]
    if running:
        return []

    candidates = [r["id"] for r in conn.execute(
        "SELECT b.id AS id FROM batches b JOIN items i ON i.id = b.item_id "
        "WHERE b.status IN ('pending','deferred') "
        "  AND i.approval = 'approved' AND i.approval_ver >= i.version "
        "ORDER BY i.priority DESC, b.id"
    ).fetchall()]
    if not candidates:
        return []

    order = schedule_order(conn)
    ranked = sorted(candidates, key=lambda b: order.index(b) if b in order else len(order))
    return [Wake("developer", "tick:batch_start", refs=(ranked[0],))]


def tick_signoff(conn: sqlite3.Connection) -> list[Wake]:
    """
    Draft items with no gate open on them: Gatekeeper submits them for approval.

    Fires per *set* rather than per item, because Signoff presents one document —
    the principal is approving an interpretation, and interpretations are read
    whole. An item already awaiting a verdict is not resubmitted.
    """
    drafts = [r["id"] for r in conn.execute(
        "SELECT id FROM items WHERE approval = 'draft' ORDER BY id")]
    if not drafts:
        return []
    pending = conn.execute(
        "SELECT COUNT(*) n FROM messages "
        "WHERE status = 'open' AND verb IN ('submit', 'present')"
    ).fetchone()["n"]
    if pending:
        return []
    return [Wake("gatekeeper", "tick:signoff", refs=tuple(drafts))]


# Terms first, because constraints are written in glossary terms; observed
# baseline last, because it describes behaviour in those terms. Named rather
# than inlined so the obligation set can see which roles onboarding wakes —
# buried in the loop below, the three survey modes were invisible to it, and
# they were the three that turned out to have no prompt at all.
SURVEY_ORDER = ("terminologist", "architect", "gatekeeper")


def tick_survey(conn: sqlite3.Connection) -> list[Wake]:
    """
    Onboarding: one session per elected area, per role, in the order
    Terminologist -> Architect -> Gatekeeper. Terms first, because constraints are written
    in glossary terms; observed baseline last, because it describes behaviour in
    those terms.

    Sessions compound through artefacts, not context: area N's session consults
    its own artefact and sees everything areas 1..N-1 found.
    """
    areas = [r["area"] for r in conn.execute(
        "SELECT DISTINCT area FROM code_index WHERE area IS NOT NULL ORDER BY area"
    ).fetchall()]
    if not areas:
        return []

    wakes = []
    for role in SURVEY_ORDER:
        for area in areas:
            done = conn.execute(
                "SELECT COUNT(*) AS n FROM survey_records WHERE area = ? AND id LIKE ?",
                (area, f"{role}:%"),
            ).fetchone()["n"]
            if not done:
                wakes.append(Wake(role, "tick:survey", refs=(area,)))
                break            # one area at a time: they must see each other's output
        if wakes:
            break                # and one role at a time, in order
    return wakes


def tick_agenda(conn: sqlite3.Connection, principal_present: bool = False) -> list[Wake]:
    """
    On principal presence, with open ledger entries or gates awaiting a verdict,
    wake Liaison to present what is blocked on the principal.

    Presentation, not a gate: the principal may defer indefinitely and keep working.
    What deferral costs is deferred, not waived — open assumptions reappear at
    each of their lineage's gates.
    """
    if not principal_present:
        return []

    # If something is already open to the principal, they can see they are being
    # waited on and there is nothing to add. This is also what makes the tick
    # terminate: presenting an agenda opens a message to the principal, which
    # silences the predicate until it is answered. Without that it fires
    # forever, because Liaison has no verb that could satisfy it.
    awaiting = conn.execute(
        "SELECT COUNT(*) AS n FROM messages WHERE status = 'open' AND to_role = 'principal'"
    ).fetchone()["n"]
    if awaiting:
        return []

    open_ledger = conn.execute(
        "SELECT COUNT(*) AS n FROM ledger WHERE status = 'open'"
    ).fetchone()["n"]
    if not open_ledger:
        return []
    return [Wake("liaison", "tick:agenda", detail=f"ledger={open_ledger}")]


TICKS: tuple[Callable[[sqlite3.Connection], list[Wake]], ...] = (
    tick_round_close,
    tick_signoff,
    tick_slicing,
    tick_criteria,
    tick_batch_start,
    tick_survey,
)


def predicate_wakes(conn: sqlite3.Connection, principal_present: bool = False) -> list[Wake]:
    """
    Every predicate except the message tips, for callers that want the second
    half on its own. The registry is the definition; `TICKS` above is the set of
    query bodies several of them delegate to.
    """
    from .predicates import REGISTRY, all_wakes

    tips = {id(REGISTRY["message_tips"])}
    return [w for p, w in (
        (p, w) for p in sorted(REGISTRY.values(), key=lambda p: (p.order, p.name))
        if id(p) not in tips and (principal_present or not p.needs_principal)
        for w in p.fn(conn))]


def frontier(conn: sqlite3.Connection, principal_present: bool = False) -> list[Wake]:
    """
    The ready queue.

    It used to be `open_tips(conn) + predicate_wakes(...)`, which stated the
    frontier in two places — and the tips half was invisible to every check
    written against the predicate half. Open tips are a predicate now, so this
    is one call, ordered fix-before-start.
    """
    from .predicates import all_wakes

    return all_wakes(conn, principal_present=principal_present)


def is_quiescent(conn: sqlite3.Connection, principal_present: bool = False) -> bool:
    return not frontier(conn, principal_present)


# ---------------------------------------------------------------------------
# Ordering: a topological sort of Architect's declared dependency facts.
# Not a role — ordering carries no judgement beyond the deps.
# ---------------------------------------------------------------------------

class UnsatisfiableSchedule(RuntimeError):
    """Declared dependency facts contain a cycle. Wakes Architect."""


def schedule_order(conn: sqlite3.Connection) -> list[str]:
    batches = [r["id"] for r in conn.execute("SELECT id FROM batches ORDER BY id")]
    deps: dict[str, set[str]] = {b: set() for b in batches}
    for r in conn.execute("SELECT before_batch, after_batch FROM batch_dep_facts"):
        deps.setdefault(r["after_batch"], set()).add(r["before_batch"])
        deps.setdefault(r["before_batch"], set())
    try:
        return list(TopologicalSorter(deps).static_order())
    except CycleError as exc:
        raise UnsatisfiableSchedule(str(exc)) from exc


def rebuild_schedule(conn: sqlite3.Connection) -> list[str]:
    """Recompute schedule_deps from declared facts. Derived state, no receipts."""
    order = schedule_order(conn)
    conn.execute("DELETE FROM schedule_deps")
    for before, after in zip(order, order[1:]):
        conn.execute(
            "INSERT OR IGNORE INTO schedule_deps (before_batch, after_batch) VALUES (?, ?)",
            (before, after),
        )
    return order


# ---------------------------------------------------------------------------
# Claims — law 6's single-instance property, enforced by the primary key.
# ---------------------------------------------------------------------------

class RoleBusy(RuntimeError):
    """The role already has a live session. Roles are single-instance: this is
    what makes cycle collapse (resume-with-question) possible."""


def claim(conn: sqlite3.Connection, role: str, session_id: str,
          message_id: str | None = None) -> None:
    held = conn.execute("SELECT session_id FROM claims WHERE role = ?", (role,)).fetchone()
    if held:
        raise RoleBusy(f"{role} already claimed by {held['session_id']}")
    conn.execute(
        "INSERT INTO claims (role, session_id, message_id) VALUES (?, ?, ?)",
        (role, session_id, message_id),
    )


def release(conn: sqlite3.Connection, role: str) -> None:
    conn.execute("DELETE FROM claims WHERE role = ?", (role,))


# ---------------------------------------------------------------------------
# Cascade — receipts wake owners along the refs DAG. No role-to-role messages
# exist anywhere in the cascade; the scheduler walks the DAG and summons owners.
# ---------------------------------------------------------------------------

class UnorderableCascade(RuntimeError):
    """The refs graph has a cycle, so "dependency order" has no meaning."""


def cascade_order(g: graph_mod.Graph | None = None) -> list[str]:
    """
    Artefacts in dependency order, derived from the graph's refs edges.

    Non-cascading refs are excluded. `model -> code` is one: it is a *binding*,
    used for the mechanical intersection that triggers structural review, not a
    path along which a change propagates. Including it closed the cycle
    model -> code -> batches -> model.

    This used to catch `CycleError` and return `sorted(deps)`. The cycle was
    always present, so the documented order in law 9 had never once run — every
    cascade since the system was built fired alphabetically, and a cascade in
    the wrong order looks exactly like one in the right order. A fallback that
    silently changes documented behaviour is worse than the failure it hides.
    """
    g = g or graph_mod.load()
    deps: dict[str, set[str]] = {a: set() for a in g.artefacts}
    for e in g.of_type("refs"):
        if not e.cascade:
            continue
        # `s refs t` means s depends on t: t is resolved first.
        deps.setdefault(e.s, set()).add(e.t)
        deps.setdefault(e.t, set())
    try:
        return list(TopologicalSorter(deps).static_order())
    except CycleError as exc:
        raise UnorderableCascade(
            f"the refs graph has a cycle, so cascade order is undefined: "
            f"{exc.args[1]}. Mark one of those refs `cascade: false` if it is a "
            f"lookup rather than a wake path.") from exc


def cascade_wakes(conn: sqlite3.Connection, session_id: str,
                  g: graph_mod.Graph | None = None) -> list[Wake]:
    """
    Given a committed session's receipts, produce the wake order: owners of every
    artefact downstream of what changed, in refs-DAG order, developer never first.
    """
    from .db import ARTEFACT_OF_TABLE

    g = g or graph_mod.load()
    touched = {
        ARTEFACT_OF_TABLE[r["table_name"]]
        for r in conn.execute(
            "SELECT DISTINCT table_name FROM receipts WHERE session_id = ?", (session_id,)
        )
        if r["table_name"] in ARTEFACT_OF_TABLE
    }
    if not touched:
        return []

    order = cascade_order(g)
    dependents: dict[str, set[str]] = {a: set() for a in g.artefacts}
    for e in g.of_type("refs"):
        dependents.setdefault(e.t, set()).add(e.s)

    affected: set[str] = set()
    queue = list(touched & set(dependents))
    while queue:
        a = queue.pop()
        for dep in dependents.get(a, ()):
            if dep not in affected:
                affected.add(dep)
                queue.append(dep)

    wakes: list[Wake] = []
    for artefact in order:
        if artefact not in affected:
            continue
        for owner in sorted(g.writer_of(artefact)):
            w = Wake(owner, "cascade", refs=(artefact,), detail=session_id)
            if w not in wakes:
                wakes.append(w)
    return wakes


# ---------------------------------------------------------------------------
# Checkpoint invalidation — mechanical, by version stamps.
# ---------------------------------------------------------------------------

def sweep_checkpoints(conn: sqlite3.Connection) -> list[str]:
    """Invalidate any checkpoint whose working set has been overtaken."""
    invalidated = []
    for row in conn.execute("SELECT session_id, working_set FROM checkpoints WHERE valid = 1"):
        stamps = json.loads(row["working_set"])
        for table, version in stamps:
            current = conn.execute(
                "SELECT version FROM artefact_versions WHERE table_name = ?", (table,)
            ).fetchone()
            if current and int(current["version"]) > int(version):
                conn.execute(
                    "UPDATE checkpoints SET valid = 0 WHERE session_id = ?",
                    (row["session_id"],),
                )
                invalidated.append(row["session_id"])
                break
    return invalidated


# ---------------------------------------------------------------------------
# Binding intersection — the structural-review trigger, and the filter for
# binding-scoped index reads.
# ---------------------------------------------------------------------------

def constraints_for_grains(conn: sqlite3.Connection, grains: Iterable[str]) -> list[str]:
    """
    Constraints triggered by a diff touching `grains`.

    Fail-safe by construction: a constraint with no bindings is global, and a
    constraint whose bindings no longer resolve is *promoted* to global. Every
    degradation path lands on "always loaded, therefore expensive" rather than
    "filtered out, therefore wrong".
    """
    grains = list(grains)
    hits: set[str] = set()

    for r in conn.execute("SELECT id FROM constraints WHERE is_global = 1"):
        hits.add(r["id"])

    for r in conn.execute(
        "SELECT c.id AS id FROM constraints c "
        "LEFT JOIN constraint_bindings b ON b.constraint_id = c.id "
        "GROUP BY c.id HAVING COUNT(b.grain) = 0"
    ):
        hits.add(r["id"])                                  # unbound = global

    for r in conn.execute(
        "SELECT DISTINCT constraint_id AS id FROM constraint_bindings WHERE resolves = 0"
    ):
        hits.add(r["id"])                                  # unresolvable = global

    if grains:
        placeholders = ", ".join("?" for _ in grains)
        for r in conn.execute(
            f"SELECT DISTINCT constraint_id AS id FROM constraint_bindings "
            f"WHERE resolves = 1 AND grain IN ({placeholders})",
            grains,
        ):
            hits.add(r["id"])

    return sorted(hits)


def constraint_zero_area_coverage(conn: sqlite3.Connection) -> tuple[set[str], set[str]]:
    """Areas surveyed (including none_found) vs areas still under constraint zero."""
    all_areas = {r["area"] for r in conn.execute(
        "SELECT DISTINCT area FROM code_index WHERE area IS NOT NULL"
    )}
    surveyed = {r["area"] for r in conn.execute("SELECT DISTINCT area FROM survey_records")}
    return surveyed, all_areas - surveyed
