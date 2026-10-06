"""
S3 and S4, one park scene.

b1 failed five attempts, its `tests_failing` key is quarantined and
reported, item 2's preempt deferred it, and the Liaison opened its park
ask. The scene ends there, before the walk answers the ask, as night 121
stood at s277. b2 is pending. The proof by removal is the park ask that
names its batch (the design's section 5, 0c6e54e, in its present form from
b23d17b). The answered park ask is in the scene `two_batches`.

The second build is in `test_scene_park_again.py`.
"""
from __future__ import annotations

from tests.rota.scene_tests import make

NAME = "park"
KEY = "developer|tick:tests_failing|b1"


def test_b1_is_parked_with_one_open_ask_and_b2_waits(scene):
    from rota.core import scheduler
    conn = scene.conn
    assert [tuple(r) for r in conn.execute("SELECT id, status FROM batches ORDER BY id")] == [
        ("b1", "deferred"), ("b2", "pending")]
    assert scheduler.failing_attempt(conn, "b1") == 5
    assert scheduler.given_up(conn, "b1") == [KEY]
    assert scheduler.parked(conn, "b1")
    asks = conn.execute("SELECT id FROM messages WHERE status = 'open' AND to_role = 'principal' "
                        "AND verb = 'clarify'").fetchall()
    assert [r["id"] for r in asks] == [scene.ids["ask"]]
    assert scheduler.park_ask_batch(scene.ids["ask"]) == "b1"
    # The park keeps b1 out of the start's order. b1 is deferred, and a
    # deferred batch that is not parked is in the order beside b2.
    assert [r["id"] for r in scheduler.next_batch(conn)] == ["b2"]


def test_the_key_is_quarantined_at_the_cap_and_the_liaison_reported_it(scene):
    # The loop's frontier quarantines the key at three dispatches with no
    # commit. Without the quarantine the loop never reaches the report, and
    # the build fails.
    row = scene.conn.execute("SELECT attempts, quarantined, reported FROM tick_attempts "
                             "WHERE tick_key = ?", (KEY,)).fetchone()
    assert tuple(row) == (3, 1, 1)
    # The report is the loop's next pick after the key's last dispatch.
    last = max(i for i, s in enumerate(scene.steps) if s == KEY)
    assert scene.steps[last + 1] == "liaison|tick:quarantined|b1"


globals().update(make(
    NAME,
    end=["architect|tick:annotate|b2", "developer|tick:batch_start|b2"],
    attempts=[("-|do:preempt|b1,b2", 1, 0, 0),
              (KEY, 3, 1, 1),
              ("liaison|tick:park_ask|i1,b1", 1, 0, 0),
              ("liaison|tick:quarantined|b1", 1, 0, 0)],
    asks=[("clarify", "i1")]))
