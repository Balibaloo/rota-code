"""
Frame 330: a running batch whose `tests_failing` key the tick quarantine took
climbs law 6's ladder, and the park frees the one batch seat.

The rows copy night 168 after s154. `batch_1` runs at head d607d440 with
attempt 6 of 10. Its two criterion tests fail with `error`. The key
`developer|tick:tests_failing|batch_1` holds 3 attempts, quarantined and
reported. `batch_2` waits `pending`, and every item holds priority 1.
"""
from __future__ import annotations

import pytest

from rota.core import predicates as P
from rota.core.db import init_db
from rota.core.predicates import LADDER
from rota.core.scheduler import Wake, next_batch, parked, tick_batch_start

KEY = "developer|tick:tests_failing|batch_1"
HEAD = "d607d440"


@pytest.fixture
def night_168(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    for iid in ("i_1", "i_2"):
        conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                     "version, priority) VALUES (?, 'x', 'in_scope', 'approved', "
                     "1, 1, 1)", (iid,))
    conn.execute("INSERT INTO batches (id, item_id, status, worktree, head_commit) "
                 "VALUES ('batch_1', 'i_1', 'running', 'wt/batch_1', ?)", (HEAD,))
    conn.execute("INSERT INTO batches (id, item_id, status) "
                 "VALUES ('batch_2', 'i_2', 'pending')")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('t_1', 'i_1', 'x')")
    for n in (1, 2):
        conn.execute("INSERT INTO criteria (id, ticket_id, text) "
                     "VALUES (?, 't_1', 'x')", (f"cr_{n}",))
        conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                     "VALUES (?, 'batch_1', ?, 'p', 'b')", (f"tst_crit_{n}", f"cr_{n}"))
        conn.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
                     "result, attempt) VALUES (?, 'batch_1', ?, ?, 'error', 6)",
                     (f"r_{n}", f"tst_crit_{n}", HEAD))
    conn.execute("INSERT INTO tests (id, batch_id, path, body) "
                 "VALUES ('tst_ok', 'batch_1', 'p', 'b')")
    conn.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, "
                 "attempt) VALUES ('r_ok', 'batch_1', 'tst_ok', ?, 'pass', 6)", (HEAD,))
    conn.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
                 "reported) VALUES (?, 3, 1, 1)", (KEY,))
    conn.commit()
    return conn


def _asked(conn, *roles: str) -> None:
    """A committed session per rung on `tick:exhausted` that names `batch_1`."""
    for role in roles:
        conn.execute("INSERT OR IGNORE INTO sessions (id, role, committed, seq, "
                     "wake_kind, wake_refs) VALUES (?, ?, 1, ?, 'tick:exhausted', "
                     "'[\"batch_1\"]')",
                     (f"s_{role}", role, 900 + LADDER.index(role)))


def _ladder(conn) -> list[tuple]:
    return [(w.role, w.kind, w.refs) for w in P.exhausted(conn)]


def test_a_quarantined_key_below_the_cap_wakes_the_developer_rung(night_168):
    """Night 168: the key ran out at attempt 6 of 10, and no rung woke.
    Law 6 says "Budget exhaustion escalates one rung"."""
    assert _ladder(night_168) == [("developer", "tick:exhausted", ("batch_1",))]


def test_a_running_batch_at_the_cap_still_wakes_the_first_rung(night_168):
    night_168.execute("DELETE FROM tick_attempts")
    night_168.execute("UPDATE test_runs SET attempt = 10")
    assert _ladder(night_168) == [("developer", "tick:exhausted", ("batch_1",))]


def test_a_running_batch_below_the_cap_with_no_quarantine_wakes_nothing(night_168):
    night_168.execute("DELETE FROM tick_attempts")
    assert _ladder(night_168) == []
    assert not parked(night_168, "batch_1")


def test_the_spent_ladder_parks_the_quarantined_batch_and_frees_the_seat(night_168):
    """Frame 86's `do:park` path, now reached by the key's quarantine."""
    from rota.core.loop import _perform

    _asked(night_168, "developer")
    assert _ladder(night_168) == [("architect", "tick:exhausted", ("batch_1",))]
    assert P.preempt(night_168) == [], "a rung is still owed, so the batch keeps the seat"

    _asked(night_168, "developer", "architect", "vision_keeper")
    assert _ladder(night_168) == []
    assert parked(night_168, "batch_1")
    (wake,) = P.preempt(night_168)
    assert (wake.kind, wake.refs) == ("do:park", ("batch_1",))
    assert [r["id"] for r in next_batch(night_168)] == ["batch_2"]

    _perform(night_168, Wake(P.SCHEDULER, "do:park", refs=("batch_1",)))
    assert night_168.execute("SELECT status FROM batches WHERE id = 'batch_1'"
                             ).fetchone()["status"] == "deferred"
    assert [w.refs for w in tick_batch_start(night_168)] == [("batch_2",)]


def test_the_wake_says_the_tests_still_fail_after_3_tries(night_168):
    """Pass 2: below the cap "attempt 6 of 10" is false, and the detail
    reaches a prompt. A batch at `loop_cap` keeps the old text."""
    def details(conn):
        return [w.detail for w in P.exhausted(conn)]

    assert details(night_168) == ["the tests still fail after 3 tries"]
    _asked(night_168, *LADDER)
    (wake,) = P.preempt(night_168)
    assert wake.detail == ("batch_1: the tests still fail after 3 tries, "
                           "and its ladder is spent")

    night_168.execute("DELETE FROM sessions")
    night_168.execute("UPDATE test_runs SET attempt = 10")
    assert details(night_168) == ["attempt 10 of 10"]
    _asked(night_168, *LADDER)
    (wake,) = P.preempt(night_168)
    assert wake.detail == "batch_1 is past its cap and its ladder is spent"


def test_a_deferred_batch_s_given_up_key_still_parks_it(night_168):
    """Frame 87 (ruled 2026-09-27): a given-up deferred batch waits for the
    principal. The ladder does not wake on it."""
    night_168.execute("UPDATE batches SET status = 'deferred' WHERE id = 'batch_1'")
    assert parked(night_168, "batch_1")
    assert _ladder(night_168) == []
    assert [r["id"] for r in next_batch(night_168)] == ["batch_2"]
