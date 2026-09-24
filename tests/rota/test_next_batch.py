"""
One order for the start and the preempt, and counts that survive absence.

Night 92 (2026-09-24): the start offered `b_2` by the schedule, the preempt
deferred it for `b_3` by priority, and each step's frontier erased the other
rule's count. The pins read the night's rows at the stop, where `b_2` is
deferred at attempt 7 with a head commit and `b_3` is pending.
"""
from __future__ import annotations

from types import SimpleNamespace

from rota.core import predicates as P
from rota.core.db import _lift_quarantines
from rota.core.scheduler import (
    next_batch, note_dispatch, quarantine_stalled, tick_batch_start, tick_key,
)
from tests.rota.fixtures.extract_night import load


def _status(conn, batch_id: str, status: str) -> None:
    conn.execute("UPDATE batches SET status = ? WHERE id = ?", (status, batch_id))


def test_priority_chooses_and_a_deferred_batch_resumes():
    """Pin 5. `b_3` outranks `b_2`, so the start offers `b_3`. With `b_3`
    merged, `b_2` comes back as a resume that names its attempt and tests."""
    conn = load(92)

    assert [r["id"] for r in next_batch(conn)] == ["b_3", "b_2"]
    wakes = tick_batch_start(conn)
    assert [(w.refs, w.detail) for w in wakes] == [(("b_3",), "")]

    _status(conn, "b_3", "merged")
    (wake,) = tick_batch_start(conn)
    assert wake.refs == ("b_2",)
    assert wake.detail.startswith("resume after attempt 7: 7 of 43 tests failing:")
    assert "tst_confirm_eof_1" in wake.detail


def test_a_deferred_batch_s_failures_wait_for_its_resume():
    """Pin 6. The harness tests running batches only, so a deferred batch's
    failures are not a wake until the batch runs again."""
    conn = load(92)
    tests_failing = P.REGISTRY["tests_failing"].fn

    assert tests_failing(conn) == []
    _status(conn, "b_2", "running")
    assert [(w.refs, w.detail) for w in tests_failing(conn)] == [(("b_2",), "attempt 7")]


def test_the_preempt_reads_the_start_s_order_and_is_bounded():
    """Pin 7. With `b_3` running nothing outranks it. With `b_2` running the
    preempt fires, and its third dispatch quarantines it."""
    conn = load(92)
    preempt = P.REGISTRY["preempt"].fn

    _status(conn, "b_3", "running")
    assert preempt(conn) == []

    _status(conn, "b_3", "pending")
    _status(conn, "b_2", "running")
    (wake,) = preempt(conn)
    assert (wake.kind, wake.refs) == ("do:preempt", ("b_2", "b_3"))

    for _ in range(3):
        note_dispatch(conn, wake)
    assert quarantine_stalled(conn, [wake]) == []
    assert tick_key(wake).endswith("|do:preempt|b_2,b_3"), "keyed by the refs"
    row = conn.execute("SELECT quarantined FROM tick_attempts WHERE tick_key = ?",
                       (tick_key(wake),)).fetchone()
    assert row is not None and row["quarantined"] == 1


def test_a_batch_count_survives_absence_and_a_move_resets_it():
    """Pin 8. The start's key for `b_2` keeps its count while absent. A head
    commit of `b_2` resets it. A key that names no batch still clears."""
    conn = load(92)
    start = "developer|tick:batch_start|b_2"
    agenda = "liaison|tick:agenda|e_1"
    for key in (start, agenda):
        conn.execute("INSERT INTO tick_attempts (tick_key, attempts) VALUES (?, 2)", (key,))

    quarantine_stalled(conn, [])

    def attempts(key):
        row = conn.execute("SELECT attempts FROM tick_attempts WHERE tick_key = ?",
                           (key,)).fetchone()
        return row["attempts"] if row else None

    assert attempts(start) == 2, "absence alone must not erase a batch's count"
    assert attempts(agenda) is None, "a key with no batch keeps delete-on-absence"

    _lift_quarantines(conn, SimpleNamespace(table="batches", row_id="b_2", op="update",
                                            values={"head_commit": "c8"}), True)
    assert attempts(start) is None, "a head commit is the batch moving"
