"""
S1, two batches that share the project's tests.

b1's Developer turns `tests/test_charges.py` red and stays red, b1 is
deferred by the preempt, and b2 starts and takes in the project's tests
under the same ids. In the night's order b1's key is quarantined twice
before item 2 comes, so b1 is parked once the preempt defers it, and the
walk answers three park asks before b2 starts. The proof by removal is
frame 135's project-id door (the design's section 5): without it, the
catalogue's two calls with the project's id land.

The second build and its landing are in `test_scene_two_batches_again.py`.
"""
from __future__ import annotations

import warnings

import pytest

from tests.rota.scene_tests import make

NAME = "two_batches"
PARK = "liaison|tick:park_ask|i1,b1"


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


def test_the_walk_answers_the_park_ask_and_the_loop_asks_again(scene):
    # Night 121 answered bg_2's park ask three times with the walk's stock
    # sentence, s277, s282 and s287, and the key ended at (3, 1, 1) (the
    # review of 7a056ce0, finding 2). The scene's principal answers as the
    # walk did: words that name neither option.
    from rota.core import scheduler
    conn, steps = scene.conn, scene.steps
    asks = [tuple(r) for r in conn.execute(
        "SELECT id, status FROM messages WHERE verb = 'clarify' AND to_role = 'principal' "
        "ORDER BY seq")]
    assert len(asks) == 3 and {s for _, s in asks} == {"answered"}
    assert {scheduler.park_ask_batch(i) for i, _ in asks} == {"b1"}
    # What the loop does next after each answer: the Liaison reads the words
    # and sends one sentence back, the walk answers that sentence, and the
    # Liaison takes it in as a new statement. Then the loop asks again.
    answered = [i for i, s in enumerate(steps) if s == "principal|clarify|i1"]
    assert len(answered) == 3
    for n, i in enumerate(answered, 1):
        assert steps[i + 1:i + 5] == ["liaison|converse|i1", f"liaison|converse|e_p{n}",
                                     f"principal|confirm|sp{n}", f"liaison|verdict|sp{n}"]
    assert [i for i, s in enumerate(steps) if s == PARK] == [i - 1 for i in answered]
    # After the third ask the key is quarantined, and the Liaison reports it.
    assert steps[steps.index("liaison|tick:quarantined|i1,b1") - 1] == "architect|deliver|sp3"
    warnings.warn(
        "an open question, held by frame 142: may a park ask that the principal "
        "answered in words with no option be asked again? Today the loop asks "
        "again after each answer, three times, and then quarantines the key.")


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
              (PARK, 3, 1, 1),
              ("liaison|tick:quarantined|b1", 1, 0, 0),
              ("liaison|tick:quarantined|i1,b1", 1, 0, 0)],
    asks=[]))
