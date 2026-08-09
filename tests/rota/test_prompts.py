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


def test_liaison_has_a_piece_per_inbound_verb():
    """
    Liaison's modes are enumerable from the graph, which is what makes each
    T1 case attributable to exactly one piece.
    """
    verbs = prompts.inbound_verbs("liaison")
    have = set(prompts.available("liaison"))
    missing = verbs - have
    assert not missing, f"Liaison has no piece for {sorted(missing)}"


def test_compose_includes_base_and_piece():
    composed = prompts.compose("liaison", "converse")
    assert "You are Liaison" in composed
    assert "MODE: converse" in composed


def test_compose_falls_back_to_base_for_unknown_mode():
    composed = prompts.compose("liaison", "not_a_verb")
    assert "You are Liaison" in composed
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


def test_every_mode_has_a_piece():
    """
    A role's modes are enumerable — one per inbound verb, one per predicate that
    wakes it — which is what makes a T1 failure attributable to exactly one
    piece. A mode with no piece silently falls back to the base, and the session
    runs with instructions for a job it is not doing.
    """
    import collections

    from rota import predicates as P

    g = graph_mod.load()
    ticks = collections.defaultdict(set)
    for p in P.REGISTRY.values():
        if p.wakes in g.roles:
            ticks[p.wakes].add(p.name)

    missing = {
        role: sorted((prompts.inbound_verbs(role) | ticks[role])
                     - set(prompts.available(role)))
        for role in sorted(g.roles)
    }
    missing = {r: m for r, m in missing.items() if m}
    assert not missing, missing


def test_every_piece_names_its_own_mode():
    """
    The mode key *is* the filename. A header reading "MODE: intake" on
    `converse.md` is a second name for one thing, which is the drift this whole
    vocabulary pass removed everywhere else — and it is load-bearing here,
    because scripted backends match on the header.
    """
    problems = []
    for role in sorted(graph_mod.load().roles):
        for mode in prompts.available(role):
            first = prompts.piece(role, mode).splitlines()[0]
            if not first.startswith(f"MODE: {mode}"):
                problems.append(f"{role}/{mode}.md opens {first!r}")
    assert not problems, "\n".join(problems)


def test_a_mode_narrowing_cannot_widen_the_role():
    """
    The graph grants the ceiling; a mode may only narrow it. A `.tools` file
    naming something outside the role's namespace would be a prompt granting a
    capability, which is the one thing prompts must never do.
    """
    conn = init_db(__import__("tempfile").mkdtemp() + "/rota.db")
    problems = []
    for role in sorted(graph_mod.load().roles):
        have = set(build(role, conn).functions())
        for mode in prompts.available(role):
            for fn in prompts.mode_tools(role, mode) or []:
                if fn not in have:
                    problems.append(f"{role}/{mode}.tools names {fn}")
    assert not problems, "\n".join(problems)
