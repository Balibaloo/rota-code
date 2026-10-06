"""
S2, a merged batch's Tester file is a project test of the next batch.

The merge delivers the Tester's `test_upgrade.py` in a commit of its own,
and b2's start takes it in. The design's section 5 names no fix for S2, so
the proof is the wall that the state comes from: the merge's delivery of
the Tester's bodies (click night 50, `lifecycle.merge`).

The merge changed `src/billing` and the root, so the surveys of both
areas run again after item 2's ratification, before b2 starts.

The second build is in `test_scene_merged_then_next_again.py`.
"""
from __future__ import annotations

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


def test_the_merged_areas_are_surveyed_again_before_b2_starts(scene):
    # The merge re-indexes main and reopens the areas that it changed, as
    # night 120 surveyed them again at s155 to s158. Item 2 is said after
    # the merge, because the walk stops there (the review of 7a056ce0,
    # finding 1).
    steps = scene.steps
    merge, start = steps.index("|do:merge|b1"), steps.index("developer|tick:batch_start|b2")
    assert steps.index("liaison|converse|" + scene.ids["entry2"]) > merge
    assert [s for s in steps[merge:start] if "tick:survey" in s] == [
        "terminologist|tick:survey|src/billing", "terminologist|tick:survey|.",
        "architect|tick:survey|src/billing", "architect|tick:survey|."]


globals().update(make(
    NAME,
    end=["tester|tick:tests_missing|b2"],
    attempts=[],
    asks=[]))
