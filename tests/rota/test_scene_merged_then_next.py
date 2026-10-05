"""
S2, a merged batch's Tester file is a project test of the next batch.

The merge delivers the Tester's `test_upgrade.py` in a commit of its own,
and b2's start takes it in. The design's section 5 names no fix for S2, so
the proof is the wall that the state comes from: the merge's delivery of
the Tester's bodies (click night 50, `lifecycle.merge`).
"""
from __future__ import annotations

import pytest

from rota.testkit import scenes
from tests.rota.scene_tests import make

NAME = "merged_then_next"


def test_the_delivered_test_is_a_project_test_of_b2(scene):
    conn = scene.conn
    assert conn.execute("SELECT status FROM batches WHERE id = 'b1'").fetchone()[0] == "merged"
    row = conn.execute("SELECT batch_id, criterion_id, path, body FROM tests WHERE id = ?",
                       (scene.ids["delivered"],)).fetchone()
    assert row is not None, "b2 did not take the delivered test in"
    assert (row["batch_id"], row["criterion_id"], row["path"]) == ("b2", None,
                                                                   scenes.TEST_PATH)
    assert row["body"] == scenes.TEST_BODY
    assert conn.execute("SELECT result FROM test_runs WHERE batch_id = 'b2' AND test_id = ?",
                        (scene.ids["delivered"],)).fetchone()[0] == "pass"


globals().update(make(NAME))
