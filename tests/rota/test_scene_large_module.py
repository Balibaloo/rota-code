"""
S6, the large module, and the four delivery wakes at the night's window.

The rule of item 5, merged into S6 by the design's change 3: each block that
a wake should hold survives the cut at `num_ctx` 16384. The scene's
sessions run at that window, so each wake is the prompt that the runner
gave the seat, after the cut, and not a wake rebuilt beside it. One test
per wake. Each names the blocks of its wake, and each goes red when the
push drops one of them (observed: the proofs of pass 9, 2026-10-06).

The fix wake holds the batch's red test, the project's red test and a diff
of 199 changed lines. The diff block stands before the red rows and the
source, and the cut falls inside it, as on night 119's s259. Frame 134
holds that wall, so its test is a strict xfail.

The second build is in `test_scene_large_module_again.py`.
"""
from __future__ import annotations

import pytest

from rota.testkit import scenes
from tests.rota.scene_tests import make

NAME = "large_module"


def _keeps(scene, role: str, kind: str, keys: list[str]) -> None:
    prompt = scenes.wake_prompt(scene, role, kind)
    got = scenes.blocks(prompt)
    lost = [k for k in keys if not got.get(k)]
    assert not lost, (f"{role} on {kind}: the cut at 16384 lost {lost}; the blocks "
                      f"of the wake, whole or not: {got}; {len(prompt)} characters")


def test_every_session_of_the_scene_ran_at_the_nights_window(scene):
    windows = {r[0] for r in scene.conn.execute("SELECT DISTINCT num_ctx FROM sessions")}
    assert windows == {16384}, windows


def test_the_batch_start_wake_keeps_its_blocks_at_16384(scene):
    _keeps(scene, "developer", "tick:batch_start",
           ["batches.expect", "criteria.load", "glossary.lookup", "tickets.load"])


def test_the_missing_tests_wake_keeps_its_blocks_at_16384(scene):
    # The table's B3 row names five blocks. `references.load` is the sixth
    # that the push gives, and it is empty on this scene.
    _keeps(scene, "tester", "tick:tests_missing",
           ["batches.expect", "criteria.load", "glossary.lookup", "references.load",
            "tests.consult", "tickets.load"])


@pytest.mark.xfail(strict=True, reason="held by frame 134: the diff block stands before "
                                       "the red rows and the source, and the cut takes them")
def test_the_fix_wake_keeps_its_blocks_at_16384(scene):
    # The diff is not in the list. It announces its own cut at 20,000
    # characters, and frame 134's repair gives it a size limit.
    _keeps(scene, "developer", "tick:tests_failing",
           ["batches.expect", "criteria.load", "references.load", "tests.load",
            "code.source"])


def test_the_fix_wake_holds_both_red_tests_and_the_diff(scene):
    # The state that frame 134 names, read from the rows and not from the
    # prompt: the last fix session ran with the batch's test and the
    # project's test red at the head, and the head's diff holds every rate.
    rows = scene.conn.execute(
        "SELECT t.id, t.criterion_id FROM test_runs r JOIN tests t ON t.id = r.test_id "
        "WHERE r.batch_id = 'b1' AND r.result = 'fail' ORDER BY t.id").fetchall()
    assert {r["criterion_id"] for r in rows} == {"c1", None}, [tuple(r) for r in rows]
    prompt = scenes.wake_prompt(scene, "developer", "tick:tests_failing")
    assert "CUT this batch's diff" in prompt


def test_the_failed_verdict_wake_keeps_its_blocks_at_16384(scene):
    _keeps(scene, "developer", "tick:verdict_failed",
           ["batches.expect", "criteria.load", "verdicts.load"])


globals().update(make(
    NAME,
    end=["developer|tick:verdict_failed|b1"],
    attempts=[("critic|tick:review|b1", 1, 0, 0),
              ("developer|tick:verdict_failed|b1", 1, 0, 0)],
    asks=[]))
