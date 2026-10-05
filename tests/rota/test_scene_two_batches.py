"""
S1, two batches that share the project's tests.

b1's Developer turns `tests/test_charges.py` red and stays red, b1 is
deferred by the preempt, and b2 starts and takes in the project's tests
under the same ids. In the loop's order the fix wake goes first, so b1's
key is quarantined and b1 is parked before the preempt. The proof by
removal is frame 135's project-id door (the design's section 5): without
it, the catalogue's two calls with the project's id land.
"""
from __future__ import annotations

import pytest

from tests.rota.scene_tests import make

NAME = "two_batches"


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
              ("liaison|tick:park_ask|i1,b1", 1, 0, 0),
              ("liaison|tick:quarantined|b1", 1, 0, 0)]))
