"""
S7, review with a bound constraint.

The Architect's survey binds a constraint to `src/billing/charges.py`, its
annotation of b1 names that file, b1's diff violates the constraint, and
the Tester's test does not encode its criterion. The Critic passed the
batch, so the frontier holds the Architect's structural review. The
Architect's violated finding is in the sweep, and the Critic's rows are in
`test_scene_critic.py`. The proof by removal is f933f25's
matcher, `api._reaching_constraints`, which puts the bound constraint in
the review wake's push.
"""
from __future__ import annotations

from rota.testkit import scenes
from tests.rota.scene_tests import make

NAME = "review"


def test_the_touch_set_meets_the_binding_and_the_review_wake_is_held(scene):
    from rota.core import lifecycle, scheduler
    conn = scene.conn
    # The touch set is known, so the review is not owed for an unknown one.
    # Constraint zero binds nothing after the survey, as on nights 119 to
    # 124, so it reaches every diff too.
    assert conn.execute("SELECT grain FROM batch_touch t JOIN constraint_bindings b "
                        "USING (grain, grain_kind) WHERE t.batch_id = 'b1' "
                        "AND b.constraint_id = ?", (scene.ids["constraint"],)
                        ).fetchall()[0]["grain"] == scenes.CHARGES
    assert lifecycle.needs_structural_review(conn, "b1")
    assert [w.refs for w in scheduler.frontier_readonly(conn, True)
            if w.kind == "tick:structural_review"] == [("b1",)]


def test_the_structural_review_wake_shows_the_bound_constraint(scene):
    from rota.core.runner import build_prompt, push_working_set, resolve_inbound
    from rota.core.scheduler import Wake
    from rota.roles import prompts
    conn = scene.conn
    wake = Wake("architect", "tick:structural_review", refs=("b1",))
    sb = scenes.sandbox_for(scene, scenes.Call("review", "push", wake, "", ()))
    pushed = push_working_set("architect", sb, wake)
    assert scene.ids["constraint"] in [r.get("id") for r in pushed["model.consult"]]
    system, user = build_prompt("architect", sb, wake, pushed,
                                prompts.compose("architect", "structural_review"),
                                resolve_inbound(conn, wake))
    assert scenes.CONSTRAINT in system + user


globals().update(make(NAME))
