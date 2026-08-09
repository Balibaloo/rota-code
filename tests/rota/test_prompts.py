"""
Prompt coverage and composition — deterministic, no model involved.

Prompts carry no authority: a piece instructing a role to do something it has no
edge for cannot succeed, because the function was never built. These cases assert
the *structure* of the prompt layer, not its wording.
"""
from __future__ import annotations

import pytest

from rota import graph as graph_mod, prompts
from rota.db import init_db
from rota.sandbox import build


def test_every_role_has_a_base_prompt():
    assert prompts.check_coverage() == []


def test_interface_has_a_piece_per_inbound_verb():
    """
    Interface's modes are enumerable from the graph, which is what makes each
    T1 case attributable to exactly one piece.
    """
    verbs = prompts.inbound_verbs("interface")
    have = set(prompts.available("interface"))
    missing = verbs - have
    assert not missing, f"Interface has no piece for {sorted(missing)}"


def test_compose_includes_base_and_piece():
    composed = prompts.compose("interface", "converse")
    assert "You are Interface" in composed
    assert "MODE: intake" in composed


def test_compose_falls_back_to_base_for_unknown_mode():
    composed = prompts.compose("interface", "not_a_verb")
    assert "You are Interface" in composed
    assert "MODE:" not in composed


def test_prompts_never_name_a_function_the_role_lacks(tmp_path):
    """
    A prompt naming an unreachable function is a lie the model will act on.

    Checked mechanically: any `msg.x_y` or `artefact.verb` token appearing in a
    role's prompts must exist in that role's namespace.
    """
    import re

    conn = init_db(tmp_path / "rota.db")
    g = graph_mod.load()
    token = re.compile(r"\b([a-z_]+\.[a-z_]+)\b")

    problems = []
    for role in g.roles:
        available = set(build(role, conn).functions())
        text = prompts.base(role)
        for mode in prompts.available(role):
            text += "\n" + prompts.piece(role, mode)

        for match in token.findall(text):
            artefact = match.split(".")[0]
            # only check tokens that look like our namespace, not prose like "e.g."
            if artefact not in {*g.artefacts, "msg"}:
                continue
            if match not in available:
                problems.append(f"{role} prompt names {match}, not in its namespace")

    assert not problems, "\n".join(sorted(set(problems)))
