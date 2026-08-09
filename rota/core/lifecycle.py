"""
A batch's runtime state, and the only place that writes it.

`batches.status` is not artefact content. Architect owns what a batch *is* — the
tickets in it, the constraints it touches — and that composition is immutable
once formed. Whether it is running, deferred or merged is something the
scheduler observes about the world, the same kind of fact as a claim or a
checkpoint, and it carries no judgement at all.

Keeping it on the `batches` row is a convenience: it belongs in its own table
alongside `claims` and `checkpoints`, and the reason it is not there yet is that
moving it touches every query in the scheduler for no behavioural gain. What
matters is that it has exactly one writer, which is this module. That is what
law 1 is protecting; the table layout is how the protection is implemented, not
what it is.

None of these transitions produce receipts. A receipt says a role decided
something, and nothing here is decided — starting the next batch is what the
schedule already said, and merging is what a passing verdict already meant.
"""
from __future__ import annotations

import sqlite3

from . import config


def start(conn: sqlite3.Connection, batch_id: str) -> None:
    """Dispatch. Only reachable through `batch_start`, which already refused if
    anything else was running."""
    conn.execute("UPDATE batches SET status = 'running' WHERE id = ?", (batch_id,))


def defer(conn: sqlite3.Connection, batch_id: str) -> None:
    """
    Preemption: a higher-priority batch arrived.

    The worktree and its commits survive — commit-first is what bounds the loss,
    because an uncommitted change never existed. The checkpoint does not: a
    deferred batch resumes cold, in the worktree it left behind.
    """
    conn.execute("UPDATE batches SET status = 'deferred' WHERE id = ?", (batch_id,))
    conn.execute("UPDATE checkpoints SET valid = 0 WHERE batch_id = ?", (batch_id,))


def merge(conn: sqlite3.Connection, batch_id: str) -> None:
    """Delivered. The end of the line for a batch, and the only terminal state
    that means the work happened."""
    conn.execute("UPDATE batches SET status = 'merged' WHERE id = ?", (batch_id,))


def record_test_run(conn: sqlite3.Connection, run_id: str, batch_id: str,
                    test_id: str, result: str, attempt: int = 1) -> None:
    """
    One test, one outcome.

    Mechanical, like recording an entry: the harness ran the test and the test
    said what it said. Routing that through a model would introduce a paraphrase
    risk over a boolean.
    """
    conn.execute(
        "INSERT OR REPLACE INTO test_runs (id, batch_id, test_id, result, attempt) "
        "VALUES (?, ?, ?, ?, ?)", (run_id, batch_id, test_id, result, attempt))


def next_attempt(conn: sqlite3.Connection, batch_id: str) -> int:
    row = conn.execute(
        "SELECT COALESCE(MAX(attempt), 0) + 1 AS n FROM test_runs WHERE batch_id = ?",
        (batch_id,)).fetchone()
    return row["n"]


# ---------------------------------------------------------------------------
# The merge gate
# ---------------------------------------------------------------------------

def mergeable(conn: sqlite3.Connection, batch_id: str) -> str | None:
    """
    Why this batch cannot merge, or None if it can.

    Three conditions, and the order is the review order: the harness passed, the
    Critic passed, the Architect found nothing violated. Returning the *reason*
    rather than a boolean is what lets the loop say why a batch is sitting there
    instead of leaving it to be inferred from its absence.
    """
    verdict = conn.execute(
        "SELECT result FROM verdicts WHERE batch_id = ? "
        "ORDER BY rowid DESC LIMIT 1", (batch_id,)).fetchone()
    if not verdict:
        return "no verdict"
    if verdict["result"] != "pass":
        return f"verdict {verdict['result']}"

    failing = conn.execute(
        "SELECT COUNT(*) AS n FROM test_runs WHERE batch_id = ? AND result != 'pass'",
        (batch_id,)).fetchone()["n"]
    if failing:
        return f"{failing} test(s) not passing"

    reviewed = conn.execute(
        "SELECT COUNT(*) AS n FROM findings WHERE batch_id = ?",
        (batch_id,)).fetchone()["n"]
    if not reviewed:
        return "no structural review yet"

    violated = conn.execute(
        "SELECT COUNT(*) AS n FROM findings "
        "WHERE batch_id = ? AND status = 'violated'", (batch_id,)).fetchone()["n"]
    if violated:
        return f"{violated} constraint(s) violated"

    if config.get(conn, "merge_gate") == "review":
        return "waiting on the principal's review"

    return None
