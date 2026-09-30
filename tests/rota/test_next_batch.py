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


def _lift(conn, batch_id: str) -> None:
    """Remove the batch's quarantined `tests_failing` key."""
    # Night 92 ended with this key quarantined. Frame 87 parks a deferred
    # batch that holds one, so a pin of the order or the cap lifts it first.
    conn.execute("DELETE FROM tick_attempts WHERE tick_key = ?",
                 (f"developer|tick:tests_failing|{batch_id}",))


def test_priority_chooses_and_a_deferred_batch_resumes():
    """Pin 5. `b_3` outranks `b_2`, so the start offers `b_3`. With `b_3`
    merged, `b_2` comes back as a resume that names its attempt and tests."""
    conn = load(92)
    # The night's own rows: `b_2` holds its quarantined key, so it is parked
    # and only `b_3` is offered (frame 87, ruled 2026-09-27).
    assert [r["id"] for r in next_batch(conn)] == ["b_3"]
    _lift(conn, "b_2")

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


def test_the_harness_is_never_counted():
    """The diff review of frame 83. The harness fires once for each new test
    at one head commit, so a count of it reaches the cap on honest work."""
    from rota.core.predicates import SCHEDULER
    from rota.core.scheduler import Wake

    conn = load(92)
    wake = Wake(SCHEDULER, "do:harness", refs=("b_2",))
    for _ in range(4):
        assert note_dispatch(conn, wake) == 0

    assert quarantine_stalled(conn, [wake]) == [wake]
    assert conn.execute("SELECT 1 FROM tick_attempts WHERE tick_key = ?",
                        (tick_key(wake),)).fetchone() is None


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


def _commit_head(conn, batch_id: str, sha: str) -> None:
    """A Developer's head commit, written through `session_commit`."""
    from rota.core.db import SessionResult, Write, session_commit

    conn.commit()
    session_commit(conn, SessionResult(
        session_id=f"s_{sha}", role="developer",
        writes=[Write("batches", batch_id, {"head_commit": sha}, op="update",
                      amends=False)]))


def _attempt(conn, batch_id: str, n: int) -> None:
    conn.execute("UPDATE test_runs SET attempt = ? WHERE batch_id = ?", (n, batch_id))


def test_a_preempted_batch_past_its_cap_resumes_exhausted():
    """Frame 86. Night 93 resumed `b_1` at attempt 11 of 10, and nothing woke
    on it after. A preempted batch at or past `loop_cap` is not offered a
    resume. It stays deferred, and the ladder's first rung wakes on it. Below
    the cap the resume stands as before."""
    conn = load(92)
    batch_start = P.REGISTRY["batch_start"].fn
    exhausted = P.REGISTRY["exhausted"].fn
    preempt = P.REGISTRY["preempt"].fn
    _lift(conn, "b_2")
    _status(conn, "b_3", "merged")

    _attempt(conn, "b_2", 11)
    assert [r["id"] for r in next_batch(conn)] == []
    assert batch_start(conn) == []
    assert [(w.role, w.kind, w.refs, w.detail) for w in exhausted(conn)] == [
        ("developer", "tick:exhausted", ("b_2",), "attempt 11 of 10")]

    # An exhausted batch that outranks the running one does not preempt it.
    _status(conn, "b_3", "running")
    conn.execute("UPDATE items SET priority = 9 WHERE id = "
                 "(SELECT item_id FROM batches WHERE id = 'b_2')")
    assert preempt(conn) == []

    _status(conn, "b_3", "merged")
    _attempt(conn, "b_2", 3)
    (wake,) = batch_start(conn)
    assert (wake.kind, wake.refs) == ("tick:batch_start", ("b_2",))
    assert wake.detail.startswith("resume after attempt 3:")
    assert exhausted(conn) == []


def test_a_quarantined_batch_resumed_after_a_preempt_waits_for_the_principal():
    """Frame 87. Night 94 quarantined `bg_1` on `tests_failing` at attempt 7,
    deferred it for a higher priority, and resumed it when that batch
    stopped. Nothing woke on it, and `bg_2` never started. A deferred batch
    with a quarantined key is parked: no seat wakes for it, the page names it
    with the way out, and a sibling starts (ruled: Roman, 2026-09-27)."""
    from rota.core.loop import _perform
    from rota.core.scheduler import frontier
    from rota.roles.principal import render_state

    conn = load(93)
    preempt = P.REGISTRY["preempt"].fn
    batch_start = P.REGISTRY["batch_start"].fn
    # Night 94's shape: below the cap, the key quarantined and reported.
    _attempt(conn, "b_1", 7)
    key = "developer|tick:tests_failing|b_1"
    conn.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
                 "reported) VALUES (?, 3, 1, 1)", (key,))
    # A batch that ran was annotated, and the principal answered its touch
    # note. The fixture keeps neither, so the start phase would wake on `b_1`.
    conn.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) "
                 "VALUES ('b_1', 'src/click/utils.py', 'path')")
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "body_refs, status, seq) VALUES ('m_touch', 't', 'liaison', "
                 "'principal', 'present', '[\"b_1\", \"echo_json\"]', 'answered', 0)")
    conn.execute("UPDATE items SET priority = 9 WHERE id = 'version_option_show_python'")

    (wake,) = preempt(conn)
    assert (wake.kind, wake.refs) == ("do:preempt", ("b_1", "b_1_version"))
    _perform(conn, wake)
    assert [w.refs for w in batch_start(conn)] == [("b_1_version",)]

    # The challenger stops. The seat is free, and the resume would come now.
    _status(conn, "b_1_version", "merged")
    assert [w.refs for w in batch_start(conn)] == [("b_1_b_1",)], "a sibling starts"
    assert not [w for w in frontier(conn) if "b_1" in w.refs], "no wake for b_1"
    assert conn.execute("SELECT quarantined FROM tick_attempts WHERE tick_key = ?",
                        (key,)).fetchone()["quarantined"] == 1, "the mark stays"

    _status(conn, "b_1_b_1", "running")
    page = render_state(conn)
    assert ("Stuck: b_1 is parked. The team gave up on: tests_failing for b_1. "
            "The other changes go on. A new commit on the change starts it "
            "again. Tell me what to change, or contest echo_json to stop "
            "it.") in page
    assert "nothing moves until" not in page
    assert "Building: 2 changes in progress." in page

    # With every sibling merged, no other change goes on.
    for sibling in ("b_1_b_1", "b_1_confirm"):
        _status(conn, sibling, "merged")
    page = render_state(conn)
    assert "Done: 3 changes" in page
    assert "Stuck: b_1 is parked." in page
    assert "The other changes go on." not in page

    # The principal's change arrives as a commit, which lifts the key.
    _commit_head(conn, "b_1", "f1x")
    assert [w.refs for w in batch_start(conn)] == [("b_1",)]


def test_a_hand_commit_found_at_boot_ends_a_quarantine_park(monkeypatch):
    """Frame 87, pass 2. A commit made by hand in the worktree reaches the
    row through `reconcile_worktrees`. Its raw write skipped the lift, so the
    batch stayed parked after the way out the page names (observed: frame
    87's diff review, 2026-09-30). The boot's write lifts the key, and the
    batch is offered again below its cap."""
    from rota.core import boot
    from rota.core.scheduler import parked

    conn = load(93)
    _attempt(conn, "b_1", 7)
    _status(conn, "b_1", "deferred")
    conn.execute("UPDATE batches SET worktree = 'wt_b_1' WHERE id = 'b_1'")
    key = "developer|tick:tests_failing|b_1"
    conn.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
                 "reported) VALUES (?, 3, 1, 1)", (key,))
    assert parked(conn, "b_1")
    assert "b_1" not in [r["id"] for r in next_batch(conn)]

    monkeypatch.setattr(boot, "_git_head", lambda wt: "h4nd" if wt == "wt_b_1" else None)
    assert [d[0] for d in boot.reconcile_worktrees(conn)] == ["b_1"]
    assert conn.execute("SELECT 1 FROM tick_attempts WHERE tick_key = ?",
                        (key,)).fetchone() is None
    assert not parked(conn, "b_1")
    assert [r["id"] for r in next_batch(conn)][0] == "b_1"


def test_a_running_batch_past_its_cap_with_a_spent_ladder_is_deferred():
    """Frame 86, pass 2. Night 93 ended with `b_1` running at attempt 11 of 10
    and its three rungs asked. The next tick defers `b_1`, and the start
    offers `b_1_b_1`."""
    conn = load(93)
    preempt = P.REGISTRY["preempt"].fn
    batch_start = P.REGISTRY["batch_start"].fn
    assert batch_start(conn) == []

    (wake,) = preempt(conn)
    assert (wake.kind, wake.refs) == ("do:park", ("b_1",))
    assert wake.detail == "b_1 is past its cap and its ladder is spent"
    assert tick_key(wake) == "-|do:park|b_1", "apart from the preempt's key"

    _status(conn, "b_1", "deferred")
    assert [w.refs for w in batch_start(conn)] == [("b_1_b_1",)]
    assert preempt(conn) == []


def test_a_parked_batch_resumes_on_a_new_head_commit():
    """Frame 86, pass 3. A parked batch whose siblings merged is offered
    nothing on the failing commit. A new head commit is a fix nobody has
    tested, so the start offers it as a resume. The ladder stays spent."""
    conn = load(93)
    batch_start = P.REGISTRY["batch_start"].fn
    exhausted = P.REGISTRY["exhausted"].fn
    _status(conn, "b_1", "deferred")
    for sibling in ("b_1_b_1", "b_1_confirm", "b_1_version"):
        _status(conn, sibling, "merged")

    assert batch_start(conn) == []
    assert exhausted(conn) == []

    # The Developer's commit reaches the row through the pipeline's write, so
    # `_lift_quarantines` runs as it does for `code.commit` (pass 4).
    _commit_head(conn, "b_1", "f1x")
    (wake,) = batch_start(conn)
    assert wake.refs == ("b_1",)
    assert wake.detail.startswith("resume after attempt 11:")
    assert exhausted(conn) == []


def test_a_message_about_a_deferred_batch_works_in_that_batch():
    """Frame 86, pass 2. A ladder answer that names `b_1` resolves to `b_1`
    while `b_1_b_1` runs. A message that names no batch falls back to the
    running batch."""
    from rota.core.loop import _batch_of
    from rota.core.scheduler import Wake

    conn = load(93)
    _status(conn, "b_1", "deferred")
    _status(conn, "b_1_b_1", "running")
    # Night 93's answers named a criterion and a test, never a batch (pass 3).
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_x', 'echo_json', 'x')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c_x', 'tk_x', 'x')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b_1', 'tk_x')")
    _status(conn, "b_1_version", "merged")
    for mid, refs in (("m_b1", '["c_2", "b_1"]'), ("m_none", '["c_2"]'),
                      ("m_test", '["c_2", "t_ej_02"]'), ("m_crit", '["c_x"]'),
                      ("m_merged", '["b_1_version"]')):
        conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                     "body_refs, seq) VALUES (?, 't', 'architect', 'developer', "
                     "'answer', ?, 0)", (mid, refs))

    def batch(mid):
        return _batch_of(conn, Wake("developer", "message", message_id=mid))

    assert batch("m_b1") == "b_1"
    assert batch("m_none") == "b_1_b_1"
    assert batch("m_test") == "b_1", "a test resolves through tests.batch_id"
    assert batch("m_crit") == "b_1", "a criterion resolves through batch_tickets"
    assert batch("m_merged") == "b_1_b_1", "a merged batch is no work in flight"


def _night_93_parked():
    """Night 93 at the park: `b_1` deferred past its cap, its siblings merged."""
    conn = load(93)
    _status(conn, "b_1", "deferred")
    for sibling in ("b_1_b_1", "b_1_confirm", "b_1_version"):
        _status(conn, sibling, "merged")
    return conn


def test_the_park_wake_defers_the_running_batch():
    """Frame 86, pass 4. `_perform` on a `do:park` wake defers the batch it
    names and says why. No priority is involved."""
    from rota.core.loop import _perform
    from rota.core.scheduler import Wake

    conn = load(93)
    _status(conn, "b_1", "running")
    line = _perform(conn, Wake(P.SCHEDULER, "do:park", refs=("b_1",)))
    assert line == "deferred b_1; its ladder is spent"
    assert conn.execute("SELECT status FROM batches WHERE id = 'b_1'"
                        ).fetchone()["status"] == "deferred"


def test_a_test_or_criterion_of_a_batch_not_in_flight_is_refused():
    """Frame 86, pass 4. A test ref or a criterion ref resolves only to a
    running or deferred batch. A merged or pending batch has no worktree in
    flight, so the message falls back to the running batch."""
    from rota.core.loop import _batch_of
    from rota.core.scheduler import Wake

    conn = load(93)
    _status(conn, "b_1_b_1", "running")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_x', 'echo_json', 'x')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c_x', 'tk_x', 'x')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b_1', 'tk_x')")
    for mid, refs in (("m_test", '["t_ej_02"]'), ("m_crit", '["c_x"]')):
        conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                     "body_refs, seq) VALUES (?, 't', 'architect', 'developer', "
                     "'answer', ?, 0)", (mid, refs))
    for status in ("merged", "pending"):
        _status(conn, "b_1", status)
        for mid in ("m_test", "m_crit"):
            got = _batch_of(conn, Wake("developer", "message", message_id=mid))
            assert got == "b_1_b_1", f"{mid} must not reach a {status} b_1"


def test_a_parked_batch_is_stuck_on_the_page():
    """Frame 86, pass 4. After the park the page read "Done: 3" only. A
    parked batch is an open obligation, so the page says it is stuck and
    names the way out. A new commit ends the park and the line."""
    from rota.roles.principal import render_state

    conn = _night_93_parked()
    page = render_state(conn)
    assert "Done: 3 changes" in page
    assert "Stuck: b_1 is parked." in page
    assert "A new commit on the change starts it again." in page

    # Between the commit and the resume the batch waits, so it is in progress.
    _commit_head(conn, "b_1", "f1x")
    page = render_state(conn)
    assert "parked" not in page
    assert "Building: 1 change in progress." in page


def test_the_park_count_survives_a_commit_and_quarantines():
    """Frame 86, pass 4. A commit is the park's own exit, so the park keeps
    its count across the commit. The start's count still resets. At
    `tick_attempt_cap` the key quarantines, and the page names the batch."""
    from rota.core import config
    from rota.core.scheduler import quarantine_overrun
    from rota.roles.principal import render_state

    conn = _night_93_parked()
    park, start = "-|do:park|b_1", "developer|tick:batch_start|b_1"
    for key in (park, start):
        # Night 93's rows hold the start's key already, so the pin replaces it.
        conn.execute("INSERT OR REPLACE INTO tick_attempts (tick_key, attempts, "
                     "quarantined) VALUES (?, 1, 0)", (key,))

    _commit_head(conn, "b_1", "f1x")

    def attempts(key):
        row = conn.execute("SELECT attempts FROM tick_attempts WHERE tick_key = ?",
                           (key,)).fetchone()
        return row["attempts"] if row else None

    assert attempts(park) == 1, "the commit is the park's exit, not its reset"
    assert attempts(start) is None, "the start's count still resets on a commit"

    conn.execute("UPDATE tick_attempts SET attempts = ? WHERE tick_key = ?",
                 (config.get(conn, "tick_attempt_cap"), park))
    assert quarantine_overrun(conn) == 1
    page = render_state(conn)
    assert "Stuck. The team gave up on: do:park for b_1." in page

    # A commit after the quarantine is the park's exit again, not its lift.
    _commit_head(conn, "b_1", "f2x")
    assert conn.execute("SELECT quarantined FROM tick_attempts WHERE tick_key = ?",
                        (park,)).fetchone()["quarantined"] == 1
    assert "Stuck. The team gave up on: do:park for b_1." in render_state(conn)
