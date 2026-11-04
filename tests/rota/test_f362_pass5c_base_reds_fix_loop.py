"""
Frame 362, pass 5c, section 4: the review of pass 5b, findings 10, 3 and 11.

Finding 10: the fix loop read every red test as the Developer's, so the 5
icalendar files red at the base woke him at every commit. Finding 11: an
inherited test is a whole file, so a new failure inside a file red at the
base held no gate. Finding 3: the test-folder cut read the whole subtree,
so `numpy/testing/overrides.py` was cut by `numpy/testing/tests/`.
"""
from __future__ import annotations

from rota.core import harness, predicates
from rota.core.scheduler import failing_attempt, park_reds
from rota.onboarding.areas import kind_of

from .test_f362_pass5_test_dir_ruling import _conn
from .test_f362_pass5b_base_red_gates import (  # noqa: F401
    PROJECT, _base, db)

INH = harness.inherited_id(PROJECT)
BASE_SAID = f"FAILED {PROJECT}::test_a - assert 1 == 2\n1 failed, 3 passed"


def _head(conn, said, attempt=1):
    conn.execute("UPDATE test_runs SET output = ?, attempt = ? WHERE test_id = ?",
                 (said, attempt, INH))


def test_a_red_at_the_base_wakes_no_developer_and_exhausts_nothing(db):
    _base(db, {INH: {"result": "fail", "output": BASE_SAID}})
    _head(db, BASE_SAID)
    assert not [w for w in predicates.tests_failing(db) if w.refs == ("b1",)]
    assert park_reds(db, "b1") == ([], [])
    _head(db, BASE_SAID, attempt=99)
    assert failing_attempt(db, "b1") == 0
    assert not [w for w in predicates.exhausted(db) if w.refs == ("b1",)]


def test_one_more_failing_node_in_a_base_red_file_holds_the_gates(db):
    _base(db, {INH: {"result": "fail", "output": BASE_SAID}})
    _head(db, f"FAILED {PROJECT}::test_a - assert 1 == 2\n"
              f"FAILED {PROJECT}::test_b - assert 0\n2 failed, 2 passed")
    assert harness.reds_that_hold(db, "b1", "h1") == [INH]
    assert [w.refs for w in predicates.tests_failing(db)] == [("b1",)]


def test_a_test_file_below_a_child_folder_does_not_cut_its_parent(tmp_path):
    conn = _conn(tmp_path, ("numpy", "program", "observed"))
    for g in ("numpy/testing/overrides.py", "numpy/testing/tests/test_utils.py"):
        conn.execute("INSERT INTO code_index (grain, grain_kind) "
                     "VALUES (?, 'path')", (g,))
    assert kind_of(conn, "numpy/testing/overrides.py") == "program"
    assert kind_of(conn, "numpy/testing/tests/test_utils.py") == "attached"
    assert kind_of(conn, "numpy/testing/tests/conftest.py") == "attached"
