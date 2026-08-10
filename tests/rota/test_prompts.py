"""
Prompt coverage and composition — deterministic, no model involved.

Prompts carry no authority: a piece instructing a role to do something it has no
edge for cannot succeed, because the function was never built. These cases assert
the *structure* of the prompt layer, not its wording.
"""
from __future__ import annotations

import pytest

from rota.design import graph as graph_mod
from rota.roles import prompts
from rota.core.db import init_db
from rota.core.sandbox import build


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

    from rota.core import predicates as P

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
    conn = init_db(__import__("tempfile").mkdtemp() + "/rota.core.db")
    problems = []
    for role in sorted(graph_mod.load().roles):
        have = set(build(role, conn).functions())
        for mode in prompts.available(role):
            for fn in prompts.mode_tools(role, mode) or []:
                if fn not in have:
                    problems.append(f"{role}/{mode}.tools names {fn}")
    assert not problems, "\n".join(problems)


def test_every_operation_is_offered_by_some_mode():
    """
    A `.tools` narrowing can only remove. Today every role still has at least
    one un-narrowed mode, so nothing is stranded — but the moment the last one
    gets a `.tools` file, any operation missing from every list becomes present
    in the namespace and offered by nothing.
    """
    import pathlib
    import tempfile

    conn = init_db(pathlib.Path(tempfile.mkdtemp()) / "rota.db")
    stranded = {}
    for role in sorted(graph_mod.load().roles):
        modes = prompts.available(role)
        if any(prompts.mode_tools(role, m) is None for m in modes):
            continue                      # an un-narrowed mode offers everything
        offered = {fn for m in modes for fn in (prompts.mode_tools(role, m) or [])}
        missing = sorted(set(build(role, conn).functions()) - offered)
        if missing:
            stranded[role] = missing
    assert not stranded, stranded


def test_every_operation_is_mentioned_in_some_prompt():
    """
    Not redundant — *unbriefed*. The role has the function and is never told
    when to use it, which is the static half of the L1 question: before asking
    whether a role chooses the right action, check it was told the action exists.

    Three of the original nineteen were whole jobs nobody described: Liaison's
    `msg.ask_*` are the entire readonly-inquiry route of law 10,
    `problem.prioritize` is law 9's priority lever, and `ledger.log` appeared
    only in Developer's brief though three other roles had it.
    """
    import pathlib
    import tempfile

    conn = init_db(pathlib.Path(tempfile.mkdtemp()) / "rota.db")
    unbriefed = {}
    for role in sorted(graph_mod.load().roles):
        text = prompts.base(role)
        for mode in prompts.available(role):
            text += "\n" + prompts.piece(role, mode)
            text += "\n" + "\n".join(prompts.mode_tools(role, mode) or [])
        missing = sorted(f for f in build(role, conn).functions() if f not in text)
        if missing:
            unbriefed[role] = missing
    assert not unbriefed, unbriefed


def test_a_mode_names_no_function_it_does_not_offer():
    """
    Narrowing is enforcement; prose is not.

    A mode file that names `code.write` is either briefing the model to use it —
    in which case the tool list must offer it — or warning the model off it, in
    which case naming it is a mistake of a subtler kind: the narrowing already
    made the call impossible, and all the sentence achieves is putting a
    function the model cannot call into the model's head.

    Both faults were live. Developer's `tests_failing` and `verdict_failed` said
    "fix the code" with no `code.write` in reach. Gatekeeper's `signoff` and
    Liaison's `verdict` spent a paragraph each forbidding a function the tool
    list had already withheld.
    """
    import re

    named_but_absent = {}
    for role in sorted(graph_mod.load().roles):
        for mode in prompts.available(role):
            offered = prompts.mode_tools(role, mode)
            if offered is None:
                continue                  # un-narrowed: the role's whole namespace
            named = set(re.findall(r"`([a-z_]+\.[a-z_]+)`", prompts.piece(role, mode)))
            missing = sorted(named - set(offered))
            if missing:
                named_but_absent[f"{role}/{mode}"] = missing
    assert not named_but_absent, named_but_absent


def test_every_mode_narrows():
    """
    An un-narrowed mode is the role's whole namespace, which is what the
    narrowing exists to prevent.

    Fifteen modes had no tool list, and they were the small ones — `answer`,
    `ask`, `elect`, `reopen` — the modes whose whole job is one message. Liaison
    woken to relay an answer had seventeen functions and used nine of them,
    including two messages to roles the mode has nothing to do with.

    A mode may legitimately want everything the role has. It then says so by
    listing it, because "I meant this" and "I never wrote the file" should not
    look the same.
    """
    bare = sorted(f"{role}/{mode}"
                  for role in sorted(graph_mod.load().roles)
                  for mode in prompts.available(role)
                  if prompts.mode_tools(role, mode) is None)
    assert not bare, f"{len(bare)} mode(s) with no tool list: {bare}"


def test_a_read_only_mode_offers_no_writes():
    """
    Three `ask` prompts told the model "you have no write functions in this
    mode; they were not built into your namespace, so there is nothing to
    resist." With no tool list that was simply untrue — Terminologist kept
    `glossary.amend` and `decisions.author` throughout.

    A prompt that claims a structural guarantee has to have one.
    """
    import pathlib
    import tempfile

    conn = init_db(pathlib.Path(tempfile.mkdtemp()) / "rota.db")
    leaks = {}
    for role in sorted(graph_mod.load().roles):
        for mode in ("ask",):
            if mode not in prompts.available(role):
                continue
            offered = set(prompts.mode_tools(role, mode) or [])
            writes = {f for f in offered
                      if f in build(role, conn).functions()
                      and not f.startswith("msg.")
                      and f.split(".")[1] not in (
                          "consult", "load", "list", "lookup", "search",
                          "scan", "probe", "quote", "read", "diff", "source")}
            if writes:
                leaks[f"{role}/{mode}"] = sorted(writes)
    assert not leaks, leaks
