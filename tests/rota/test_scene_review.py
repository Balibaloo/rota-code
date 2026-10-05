"""
S7, review with a bound constraint, in two scenes of one chain.

`critic`: the Architect's survey binds a constraint to
`src/billing/charges.py`, and the principal approves it as observed. b1's
annotation names that file, b1's diff violates the constraint, and the
Tester's test does not encode its criterion. The loop's next pick is the
Critic's review. The Critic's rows run on this state. The proof by removal
is the claim door of `verdicts_emit`: a fail stands on a claim that the
test encodes its criterion.

`review`: the build goes on from `critic`, and the Critic passes the batch,
so the loop's next pick is the Architect's structural review. The proof by
removal is f933f25's matcher, `api._reaching_constraints`, which puts the
bound constraint in the review wake's push.

The tests of `critic` come first in this file, because the `review`
fixture moves the same build on.
"""
from __future__ import annotations

from rota.testkit import scenes
from tests.rota.scene_tests import make


def test_the_observed_constraint_is_ruled_and_adopted(critic):
    # A night puts the observed constraint to the principal once the survey
    # is done. The loop picks the Liaison's present, and the approval is
    # relayed to the Architect, who adopts the row (the review of 2d7cc73,
    # finding 3).
    conn, k = critic.conn, critic.ids["constraint"]
    assert conn.execute("SELECT provenance FROM constraint_provenance WHERE id = ?",
                        (k,)).fetchone()[0] != "observed"
    assert conn.execute("SELECT COUNT(*) FROM messages WHERE verb = 'present' "
                        "AND body_refs = ?", (f'["{k}"]',)).fetchone()[0] == 1


globals().update(make("critic", end=["critic|tick:review|b1"], attempts=[],
                      parts=("calls",), fixture="critic"))


def test_the_touch_set_reaches_the_bound_constraint_and_the_review_wake_is_held(review):
    from rota.core import lifecycle, scheduler
    conn, k = review.conn, review.ids["constraint"]
    touch = [r["grain"] for r in conn.execute(
        "SELECT grain FROM batch_touch WHERE batch_id = 'b1'")]
    assert scenes.CHARGES in touch
    # Constraint zero binds nothing after the survey, as on nights 119 to
    # 124, so it reaches every diff. The bound constraint is reached by the
    # touch set alone: with its binding deleted it is global, and with
    # `charges.py` out of the touch set nothing reaches it (the review of
    # 2d7cc73, finding 4).
    assert k in scheduler.constraints_for_grains(conn, touch)
    assert k not in scheduler.constraints_for_grains(conn, [])
    assert lifecycle.needs_structural_review(conn, "b1")


def test_the_structural_review_wake_shows_the_bound_constraint(review):
    from rota.core.runner import build_prompt, push_working_set, resolve_inbound
    from rota.core.scheduler import Wake
    from rota.roles import prompts
    conn = review.conn
    wake = Wake("architect", "tick:structural_review", refs=("b1",))
    sb = scenes.sandbox_for(review, scenes.Call("review", "push", wake, "", ()))
    pushed = push_working_set("architect", sb, wake)
    assert review.ids["constraint"] in [r.get("id") for r in pushed["model.consult"]]
    system, user = build_prompt("architect", sb, wake, pushed,
                                prompts.compose("architect", "structural_review"),
                                resolve_inbound(conn, wake))
    assert scenes.CONSTRAINT in system + user


globals().update(make("review", end=["architect|tick:structural_review|b1"],
                      attempts=[("critic|tick:review|b1", 1, 0, 0)],
                      fixture="review", after="critic"))
