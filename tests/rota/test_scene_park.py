"""
S3 and S4, one park scene.

b1 failed five attempts, its `tests_failing` key is quarantined and
reported, a preempt deferred it, and the Liaison opened its park ask. b2
and b3 are pending. The proof by removal is the park ask that names its
batch (the design's section 5, 0c6e54e, in its present form from b23d17b).
The second build is in `test_scene_park_again.py`, so that a second worker
builds it.
"""
from __future__ import annotations

from tests.rota.scene_tests import make

NAME = "park"


def test_b1_is_parked_with_one_open_ask_and_b2_and_b3_wait(scene):
    from rota.core import scheduler
    conn = scene.conn
    assert [tuple(r) for r in conn.execute("SELECT id, status FROM batches ORDER BY id")] == [
        ("b1", "deferred"), ("b2", "pending"), ("b3", "pending")]
    assert scheduler.failing_attempt(conn, "b1") == 5
    assert scheduler.given_up(conn, "b1") == [scene.ids["key"]]
    assert scheduler.parked(conn, "b1")
    asks = conn.execute("SELECT id FROM messages WHERE status = 'open' AND to_role = 'principal' "
                        "AND verb = 'clarify'").fetchall()
    assert [r["id"] for r in asks] == [scene.ids["ask"]]
    assert scheduler.park_ask_batch(scene.ids["ask"]) == "b1"
    # The park keeps b1 out of the start's order. No night holds a declared
    # order of batches, so b2 and b3 wait by priority alone.
    assert [r["id"] for r in scheduler.next_batch(conn)] == ["b2", "b3"]


def test_quarantine_overrun_marked_the_key_and_the_liaison_reported_it(scene):
    # `frontier` runs `quarantine_overrun` first, so it marks the key at the
    # cap. `quarantine_stalled` marks a key at the same count, and then finds
    # this one marked already.
    assert scene.ids["overrun"] == 1
    row = scene.conn.execute("SELECT attempts, quarantined, reported FROM tick_attempts "
                             "WHERE tick_key = ?", (scene.ids["key"],)).fetchone()
    assert tuple(row) == (3, 1, 1)


globals().update(make(NAME, parts=("calls",)))
