"""
S1, two batches that share the project's tests.

b1's Developer turns `tests/test_charges.py` red and stays red, b1 is
deferred by the preempt, and b2 starts and takes in the project's tests
under the same ids. In the night's order b1's key is quarantined twice
before item 2 comes, so b1 is parked once the preempt defers it, and the
walk approves every line of the park page before b2 starts. The proof by removal is
frame 135's project-id door (the design's section 5): without it, the
catalogue's two calls with the project's id land.

The second build and its landing are in `test_scene_two_batches_again.py`.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from tests.rota.scene_tests import make

NAME = "two_batches"
PARK = "liaison|tick:park_ask|i1,b1"


NIGHT_126 = Path("D:/repos/rota/.rota/clickI_night126.db")


@pytest.mark.skipif(not NIGHT_126.exists(), reason="night 126's database is not on this machine")
def test_the_s156_row_holds_the_nights_bytes():
    # The catalogue row claims s156's line as sent. Nothing else ties it to
    # the night (the review of 96fe3425, its first low).
    from rota.testkit import scenes

    conn = sqlite3.connect(f"file:{NIGHT_126.as_posix()}?mode=ro&immutable=1", uri=True)
    try:
        row = conn.execute("SELECT completion FROM turns WHERE session_id = 's156' "
                           "AND seq = 2").fetchone()
    finally:
        conn.close()
    assert row is not None and row[0].strip() == scenes._S156_SENT


def test_b1_failed_the_project_test_and_b2_took_the_project_tests_in(scene):
    conn, ids = scene.conn, scene.ids
    assert [tuple(r) for r in conn.execute(
        "SELECT id, status FROM batches ORDER BY id")] == [("b1", "deferred"), ("b2", "running")]
    # The preempt deferred b1, and not the park's own action.
    assert "-|do:preempt|b1,b2" in scene.steps
    assert "-|do:park|b1" not in scene.steps
    assert conn.execute(
        "SELECT result FROM test_runs WHERE batch_id = 'b1' AND test_id = ? "
        "AND commit_sha = ?", (ids["charges"], ids["head1"])).fetchone()["result"] == "fail"
    assert {r["path"] for r in conn.execute(
        "SELECT path FROM tests WHERE batch_id = 'b2' AND criterion_id IS NULL")} == {
        "tests/test_charges.py", "tests/test_pricing.py", "tests/test_templates.py"}


def test_the_walk_approves_the_park_page_and_the_park_rests(scene):
    # Night 121 answered bg_2's park ask three times with the walk's stock
    # sentence, s277, s282 and s287, and the key ended at (3, 1, 1) (the
    # review of 7a056ce0, finding 2). Frame 142: the park ask is a page with
    # the item and its criteria. The walk with no words approves every line,
    # which is the ceiling, and the page rests (ruled: Roman, 2026-10-08).
    from rota.core import scheduler
    conn, steps = scene.conn, scene.steps
    asks = [tuple(r) for r in conn.execute(
        "SELECT id, verb, status, body_refs FROM messages WHERE substr(id, 1, 7) = 'm_park_' "
        "ORDER BY seq")]
    assert [(v, s, r) for _, v, s, r in asks] == [("present", "answered", '["i1", "c1"]')]
    assert scheduler.park_ask_batch(asks[0][0]) == "b1"
    assert scheduler.park_rests(conn, "b1")
    (verdict,) = conn.execute("SELECT status FROM messages WHERE cause_id = ? "
                              "AND verb = 'verdict'", (asks[0][0],)).fetchall()
    assert verdict["status"] == "answered", "the ceiling wakes no Liaison"
    i = steps.index(PARK)
    assert steps[i + 1:i + 3] == ["principal|present|i1,c1", "architect|tick:annotate|b2"]
    assert "liaison|tick:quarantined|i1,b1" not in steps


@pytest.mark.xfail(strict=True, reason=(
    "held by frame 130: `harness.inherit` keys a project test on its path "
    "alone, so b2's start moves b1's rows to b2"))
def test_every_run_names_a_test_of_its_own_batch(scene):
    bad = [tuple(r) for r in scene.conn.execute(
        "SELECT r.batch_id, r.test_id, t.batch_id FROM test_runs r "
        "JOIN tests t ON t.id = r.test_id WHERE t.batch_id != r.batch_id")]
    assert bad == []


globals().update(make(
    NAME,
    end=["tester|tick:tests_missing|b2"],
    attempts=[("developer|tick:tests_failing|b1", 3, 1, 1),
              (PARK, 1, 0, 0),
              ("liaison|tick:quarantined|b1", 1, 0, 0)],
    asks=[],
    # I4: b2 took in the project's tests under b1's ids, so b1's runs name
    # tests of b2. I5 holds: the approved page rests, so parked b1 owes no
    # open ask (frame 142).
    known={"I4": "frame 130"}))
