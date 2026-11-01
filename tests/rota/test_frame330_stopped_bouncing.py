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
from rota.core import scheduler
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
    # Review finding 2: a later run of a shared test id in another batch
    # hid attempt 10 from the detail, and the gate still read it.
    night_168.execute("UPDATE test_runs SET attempt = 4 WHERE id = 'r_2'")
    night_168.execute("INSERT INTO test_runs (id, batch_id, test_id, result, attempt) "
                      "VALUES ('r_b2', 'batch_2', 'tst_crit_1', 'error', 4)")
    assert [w.detail for w in P.exhausted(night_168)] == ["attempt 10 of 10"]


def test_a_rung_still_owed_keeps_law_9_s_preempt(night_168):
    """Review finding 1: law 9's preempt of a quarantined running batch.
    With a rung owed `preempt` does not park, so a higher priority wins."""
    night_168.execute("UPDATE items SET priority = 9 WHERE id = 'i_2'")
    _asked(night_168, "developer")
    (wake,) = P.preempt(night_168)
    assert (wake.kind, wake.refs) == ("do:preempt", ("batch_1", "batch_2"))


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


def test_the_wake_says_the_tests_still_fail_after_3_attempts(night_168):
    """Pass 2: below the cap "attempt 6 of 10" is false, and the detail
    reaches a prompt. A batch at `loop_cap` keeps the old text. Pass 5: the
    words come from the page's one table, `TICK_WORDS`."""
    def details(conn):
        return [w.detail for w in P.exhausted(conn)]

    # Wall W12: the words name the red test file, here `p`, and not the kind.
    assert details(night_168) == ["p still fails after 3 attempts"]
    _asked(night_168, *LADDER)
    (wake,) = P.preempt(night_168)
    assert wake.detail == ("batch_1: p still fails after 3 attempts, "
                           "and its ladder is spent")

    night_168.execute("DELETE FROM sessions")
    night_168.execute("UPDATE test_runs SET attempt = 10")
    assert details(night_168) == ["attempt 10 of 10"]
    _asked(night_168, *LADDER)
    (wake,) = P.preempt(night_168)
    assert wake.detail == "batch_1 is past its cap and its ladder is spent"


def _only_key(conn, key: str, *, red: bool = False) -> None:
    """The batch holds `key` quarantined as its one given-up key. Its tests
    pass unless `red`."""
    conn.execute("DELETE FROM tick_attempts")
    conn.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
                 "reported) VALUES (?, 3, 1, 1)", (key,))
    if not red:
        conn.execute("UPDATE test_runs SET result = 'pass'")


def _frees_the_seat(conn) -> None:
    """The spent ladder parks `batch_1`, and `batch_2` starts."""
    from rota.core.loop import _perform

    assert parked(conn, "batch_1")
    _asked(conn, *LADDER)
    assert _ladder(conn) == []
    (wake,) = P.preempt(conn)
    assert (wake.kind, wake.refs) == ("do:park", ("batch_1",))
    assert [r["id"] for r in next_batch(conn)] == ["batch_2"]
    _perform(conn, Wake(P.SCHEDULER, "do:park", refs=("batch_1",)))
    assert [w.refs for w in tick_batch_start(conn)] == [("batch_2",)]


def test_night_169_a_quarantined_start_climbs_the_ladder_and_frees_the_seat(night_168):
    """Night 169: `batch_1` ran with no commit, its start key ran out at 3,
    and `batch_2` never started. `given_up` listed the key, and no seat rule
    read it (plans/frame330-agency-read.md, section 3, instance 9)."""
    night_168.execute("DELETE FROM test_runs")
    night_168.execute("DELETE FROM tests")
    night_168.execute("UPDATE batches SET head_commit = NULL WHERE id = 'batch_1'")
    _only_key(night_168, "developer|tick:batch_start|batch_1")
    assert _ladder(night_168) == [("developer", "tick:exhausted", ("batch_1",))]
    assert [w.detail for w in P.exhausted(night_168)] == [
        "the change could not start after 3 attempts"]
    _frees_the_seat(night_168)


# The nine other keys of a running batch that `given_up` lists, section 3 of
# the agency read. The last is a ladder rung's own key, so its rung is asked.
OTHER_KEYS = [
    ("developer|tick:verdict_failed|batch_1", "developer"),
    ("developer|tick:finding_violated|batch_1", "developer"),
    ("developer|tick:touch_mistaken|batch_1", "developer"),
    ("critic|tick:review|batch_1", "developer"),
    ("architect|tick:structural_review|batch_1", "developer"),
    ("architect|tick:touch_strayed|batch_1", "developer"),
    ("tester|tick:tests_missing|batch_1", "developer"),
    ("developer|tick:batch_start|batch_1", "developer"),
    ("developer|tick:exhausted|batch_1", "architect"),
]


@pytest.mark.parametrize("key, rung", OTHER_KEYS, ids=[k.split("|")[1] for k, _ in OTHER_KEYS])
def test_every_given_up_key_of_a_green_running_batch_climbs_and_parks(night_168, key, rung):
    """Law 6: "Budget exhaustion escalates one rung" and "It is never
    silence". The check read the `tests_failing` key only, so a green batch
    with any other key kept the seat and woke nobody."""
    _only_key(night_168, key)
    assert _ladder(night_168) == [(rung, "tick:exhausted", ("batch_1",))]
    _frees_the_seat(night_168)


def _one_batch(conn, key: str) -> None:
    """dry1's shape: `batch_1` is the one batch, `key` is its one given-up
    key, and every rung is asked. Its ticket is grouped, so no grouping
    wakes."""
    conn.execute("DELETE FROM batches WHERE id = 'batch_2'")
    conn.execute("DELETE FROM items WHERE id = 'i_2'")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) "
                 "VALUES ('batch_1', 't_1')")
    _only_key(conn, key)
    _asked(conn, *LADDER)


def test_a_quiet_frontier_parks_the_last_batch_with_a_spent_ladder(night_168):
    """dry1's fourth wall: `bg_1` was the one batch, green, with its Tester
    key quarantined and its ladder spent. `preempt` reads no challenger, so
    the batch held the seat as `running` and nothing woke. The quiet now
    parks it (`scheduler.quiet_park`)."""
    _one_batch(night_168, "tester|tick:tests_missing|batch_1")
    # The green batch's review ran out too, so no seat can move it.
    night_168.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
                      "reported) VALUES ('critic|tick:review|batch_1', 3, 1, 1)")
    assert parked(night_168, "batch_1")
    assert _ladder(night_168) == []
    assert next_batch(night_168) == []
    assert P.preempt(night_168) == [], "with no challenger the quiet parks"
    (wake,) = scheduler.frontier(night_168)
    assert (wake.role, wake.kind, wake.refs) == (P.SCHEDULER, "do:park", ("batch_1",))
    assert wake.detail.endswith("and its ladder is spent")


def test_a_tester_wake_on_the_batch_keeps_it_from_the_quiet_park(night_168):
    """Night 119's s259 (frame 134): the Tester's new red test lifts the
    quarantined fix key, and the last fix session lands. A park before the
    Tester's wake loses that route, so a frontier with the wake parks
    nothing."""
    _one_batch(night_168, KEY)
    night_168.execute("UPDATE test_runs SET result = 'error' WHERE id LIKE 'r_%'")
    night_168.execute("INSERT INTO criteria (id, ticket_id, text) "
                      "VALUES ('cr_3', 't_1', 'x')")
    assert parked(night_168, "batch_1")
    assert _ladder(night_168) == []
    assert [(w.role, w.kind, w.refs) for w in scheduler.frontier(night_168)] == [
        ("tester", "tick:tests_missing", ("batch_1",))]
    assert night_168.execute("SELECT status FROM batches WHERE id = 'batch_1'"
                             ).fetchone()["status"] == "running"
    # The park waits for the quiet, and it is due there.
    assert [w.kind for w in scheduler.quiet_park(night_168)] == ["do:park"]


def test_a_quarantined_rung_counts_as_asked(night_168):
    """Instance 10: a rung whose own key ran out committed no session, so
    `_next_rung` asked it for ever and `preempt` never parked."""
    night_168.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
                      "reported) VALUES ('developer|tick:exhausted|batch_1', 3, 1, 1)")
    assert _ladder(night_168) == [("architect", "tick:exhausted", ("batch_1",))]
    assert [w.detail for w in P.exhausted(night_168)] == [
        "the team could not finish a step after 3 attempts; p still fails "
        "after 3 attempts"]


def test_a_stuck_liaison_note_does_not_stop_the_batch(night_168):
    """Review of pass 5, finding 3: the Liaison's note about a pair key
    names the batch alone. A failed report is not a step of the batch."""
    _only_key(night_168, "liaison|tick:quarantined|batch_1")
    assert _ladder(night_168) == []
    assert not parked(night_168, "batch_1")


def test_the_rung_reads_the_cause_in_its_prompt(night_168):
    """Review of pass 5, finding 1: a green batch woke the Developer rung,
    and its prompt said the tests are still red and named no cause."""
    from rota.core.runner import build_prompt
    from rota.core.sandbox import build
    from rota.roles import prompts

    _only_key(night_168, "critic|tick:review|batch_1")
    (wake,) = P.exhausted(night_168)
    sb = build("developer", night_168, mode="exhausted",
               allow=prompts.mode_tools("developer", "exhausted"))
    system, user = build_prompt("developer", sb, wake, {},
                                prompts.compose("developer", "exhausted"))
    assert "the review gave no verdict after 3 attempts" in user
    assert "still red" not in system


def test_a_deferred_batch_s_given_up_key_still_parks_it(night_168):
    """Frame 87 (ruled 2026-09-27): a given-up deferred batch waits for the
    principal. The ladder does not wake on it."""
    night_168.execute("UPDATE batches SET status = 'deferred' WHERE id = 'batch_1'")
    assert parked(night_168, "batch_1")
    assert _ladder(night_168) == []
    assert [r["id"] for r in next_batch(night_168)] == ["batch_2"]
