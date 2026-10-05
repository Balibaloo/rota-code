"""
S7 up to the Critic: the review wake on a test that does not encode its
criterion.

The Critic's rows of S7 run here, because the structural review that S7
ends at needs a pass verdict, and one commit gets one verdict. The proof by
removal is the claim door of `verdicts_emit`: a fail stands on a claim that
the test encodes its criterion.
"""
from __future__ import annotations

from tests.rota.scene_tests import make

NAME = "critic"


def test_the_frontier_holds_the_critics_review_of_b1(scene):
    from rota.core import scheduler
    assert [w.refs for w in scheduler.frontier_readonly(scene.conn, True)
            if w.kind == "tick:review"] == [("b1",)]


globals().update(make(NAME))
