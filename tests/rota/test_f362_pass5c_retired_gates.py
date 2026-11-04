"""
Frame 362, pass 5c, section 3: a red test of a retired criterion holds no gate.

Pass 5b, deviation 3: the merge check dropped such a test (frame 306, pass
2, finding 2), and the review predicate still counted it. So a Critic never
woke for the batch. Both gates now ask `reds_that_hold`, which holds the rule.
"""
from __future__ import annotations

from rota.core import harness, lifecycle

from .test_f362_pass5b_base_red_gates import (  # noqa: F401
    PROJECT, _base, _pass_verdict, _reviewed, db)


def test_a_red_test_of_a_retired_criterion_holds_neither_gate(db):
    _base(db, {harness.inherited_id(PROJECT): {"result": "pass"}})
    db.execute("UPDATE test_runs SET result = 'pass' WHERE test_id != 'own1'")
    db.execute("UPDATE test_runs SET result = 'fail' WHERE test_id = 'own1'")
    db.execute("UPDATE criteria SET retired_by = 'line_1' WHERE id = 'c1'")
    assert harness.reds_that_hold(db, "b1", "h1") == []
    assert _reviewed(db)
    _pass_verdict(db)
    assert "not passing" not in (lifecycle.mergeable(db, "b1") or "")
