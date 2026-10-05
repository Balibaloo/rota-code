"""
S3 and S4, one park scene.

b1 failed five attempts, its `tests_failing` key is quarantined, a preempt
deferred it, and the Liaison opened its park ask. b2 and b3 are pending,
and b3 declares b1 as its predecessor. The proof by removal is 0c6e54e,
the park ask that names its batch (the design's section 5).
"""
from __future__ import annotations

import pytest

from rota.testkit import scenes
from tests.rota.scene_tests import make

NAME = "park"


def test_b1_is_parked_with_one_open_ask_and_b3_waits_behind_it(scene):
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
    assert [r["id"] for r in scheduler.next_batch(conn)] == ["b2"]


globals().update(make(NAME))
