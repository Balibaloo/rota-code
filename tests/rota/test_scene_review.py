"""
S7, review with a bound constraint.

The Architect's constraint binds `src/billing/charges.py`, b1's diff
violates it, and the Tester's test does not encode its criterion. The
right calls are in the sweep: the Critic's fail verdict, the Architect's
violated finding and the Developer's challenge.
"""
from __future__ import annotations

import pytest

from rota.testkit import scenes
from tests.rota.scene_tests import make

NAME = "review"


def test_the_structural_review_wake_shows_the_bound_constraint(scene):
    from rota.core import lifecycle
    from rota.core.runner import build_prompt, push_working_set, resolve_inbound
    from rota.core.scheduler import Wake
    from rota.roles import prompts
    conn = scene.conn
    assert lifecycle.needs_structural_review(conn, "b1")
    wake = Wake("architect", "tick:structural_review", refs=("b1",))
    sb = scenes.sandbox_for(scene, scenes.Call("review", "push", wake, "", ()))
    system, user = build_prompt("architect", sb, wake, push_working_set("architect", sb, wake),
                                prompts.compose("architect", "structural_review"),
                                resolve_inbound(conn, wake))
    assert scenes.CONSTRAINT in system + user


globals().update(make(NAME))
