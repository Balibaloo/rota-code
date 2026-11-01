"""
S3 and S4, one park scene.

b1 failed five attempts, its `tests_failing` key is quarantined and
reported, law 6's three rungs woke on it (frame 330), and the quiet after
the report parked it with no sibling batch (dry1's fourth wall,
2026-11-01). The Liaison opened its park ask, and the walk approved the
page before item 2. The scene ends at item 2's grouping, with b2 pending.
The proof by removal is the park ask that names its batch (the design's
section 5, 0c6e54e, in its present form from b23d17b).

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
    # Frame 142: the park ask is a present, a page with the item and c1.
    # Frame 330: the quiet parks b1 before item 2, so the walk answers the
    # page before it says item 2, and the page rests.
    asks = conn.execute("SELECT id, status, body_refs FROM messages "
                        "WHERE substr(id, 1, 7) = 'm_park_'").fetchall()
    assert [tuple(r) for r in asks] == [(scene.ids["ask"], "answered", '["i1", "c1"]')]
    assert scheduler.park_ask_batch(scene.ids["ask"]) == "b1"
    assert scheduler.park_rests(conn, "b1")
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
    # Frame 330: the quarantined key stops the bounce, so law 6's three rungs
    # come first after the key's last dispatch. The report is the next pick.
    last = max(i for i, s in enumerate(scene.steps) if s == KEY)
    assert scene.steps[last + 1:last + 5] == [
        "developer|tick:exhausted|b1", "architect|tick:exhausted|b1",
        "vision_keeper|tick:exhausted|b1", "liaison|tick:quarantined|b1"]


globals().update(make(
    NAME,
    end=["architect|tick:annotate|b2", "developer|tick:batch_start|b2"],
    attempts=[("-|do:park|b1", 1, 0, 0),
              ("architect|tick:exhausted|b1", 1, 0, 0),
              ("architect|tick:grouping|tk2", 1, 0, 0),
              ("developer|tick:exhausted|b1", 1, 0, 0),
              (KEY, 3, 1, 1),
              ("liaison|tick:park_ask|i1,b1", 1, 0, 0),
              ("liaison|tick:quarantined|b1", 1, 0, 0),
              ("vision_keeper|tick:exhausted|b1", 1, 0, 0)],
    asks=[]))
