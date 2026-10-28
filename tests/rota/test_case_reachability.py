"""
A case must ask for something the role can actually reach.

Two of the failures this suite spent weeks on were not the model and not the
harness. They were cases written from the design rather than from what the role
can see:

* Tester was told to file a test into a batch, and the batch was in the fixture
  YAML but not in anything the session was handed. It filled the required
  `batch_id` with the only id in front of it -- a glossary term from the message
  that woke it -- nineteen times in one session.
* Liaison was woken at `round_close` with no reports, and `tick_round_close`
  cannot produce that wake. It was being marked down for not recognising a
  situation the system cannot be in.

Both are the same defect and both were found by running a model for twenty-five
minutes and reading a transcript. Neither needed a model at all: a case that
requires a row the role was never given is unsatisfiable on inspection.

Only the wake is checked. Whether an *expected write* is reachable
wants an artefact-to-table map, and inventing one would be a second
vocabulary beside the graph's -- the thing this project spends the
most effort not doing.

This is the same rule the sandbox already enforces for capability -- a role
cannot reach outside its edges because the function was never built -- applied
to the *contents* of a waking rather than to its verbs.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.testkit import fixtures


def _cases():
    out = []
    for path in sorted((Path(__file__).parent / "cases").glob("l*.yaml")):
        out.extend(fixtures.load_case(path) or [])
    return out


CASES = _cases()


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_a_tick_case_names_a_wake_the_scheduler_can_produce(case):
    """
    `tick:` names a predicate. If no predicate has that name, the case is
    testing a situation the frontier cannot put a role in.

    The stronger check -- that the *fixture* would actually make that predicate
    fire -- is the one that would have caught `round_close` with no reports, and
    it is below.
    """
    tick = case.get("tick")
    if not tick:
        return
    from rota.core import predicates as P
    assert tick in P.REGISTRY, (
        f"{case['id']} wakes on tick:{tick}, which is not a predicate")


@pytest.mark.parametrize("case", [c for c in CASES if c.get("tick")],
                         ids=[c["id"] for c in CASES if c.get("tick")])
def test_a_tick_cases_fixture_would_actually_fire_that_predicate(case, tmp_path):
    """
    Seed the fixture, run the predicate, and require it to wake this role.

    This is the check that makes a case honest about its own premise. A wake the
    scheduler would never produce is a situation the role will never meet, and
    grading a model on it measures nothing -- `round_close` with no reports
    failed five times out of five for exactly that reason.

    A fixture that fires nothing must say why. This used to be a blanket skip --
    "the seeded state may be outside what the predicate reads" -- and it was
    true of three cases and an alibi for two others. `L2-VK-end-it-rather-than-
    send-it-back` seeded no `test_runs`, so the ladder it was climbing did not
    exist; `L1-LI-put-a-contradiction-back-unresolved` seeded both statements
    `ratified` when the predicate reads `contradicted`. Both were exactly the
    defect this file exists to catch, and both wore the skip that was written
    for the honest cases.

    `tick_unseedable:` is that skip, named. It carries a reason, it is per case,
    and a fixture that quietly stops firing cannot inherit it.
    """
    from rota.core import predicates as P

    if case["tick"] not in P.REGISTRY:
        pytest.skip("not a predicate; the check above owns that failure")

    conn = init_db(tmp_path / "rota.db")
    fixtures.seed(conn, case.get("fixture") or {})
    conn.commit()

    wakes = P.REGISTRY[case["tick"]].fn(conn)
    if not wakes:
        why = case.get("tick_unseedable")
        assert why, (
            f"{case['id']} seeds a fixture that fires nothing: tick:{case['tick']} "
            f"produces no wake at all, so the situation it grades cannot arise. "
            f"Fix the fixture, or say why it cannot be seeded with "
            f"`tick_unseedable: <reason>`")
        pytest.skip(f"tick:{case['tick']} unseedable: {why}")
    assert any(w.role == case["role"] for w in wakes), (
        f"{case['id']} says it wakes {case['role']} on tick:{case['tick']}, but "
        f"that predicate wakes {sorted({w.role for w in wakes})} here")


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_an_expected_call_has_something_to_read(case):
    """
    Three of this suite's long-standing failures were a case expecting a call
    whose data source its fixture never filled, and the same shape every time:
    the role does something reasonable and scores as wrong.

    `code.probe` reads `code_index`, which `_with_repo` only builds when a case
    asks for `onboard`. Two cases expected a probe without asking.
    `L1-AR-annotate-a-batch` ran 0/5 and `L1-DV-fix-the-code-not-the-test` ran
    10/80 — the brief tells the Developer to find the implementation by probing
    and then read it, and the probe came back empty, so the role concluded the
    symbol did not exist and challenged the Tester. A sound inference from a
    result that was not evidence.

    `web.fetch` reads `web_cache`, which is seeded and never fetched, because a
    role whose tests needed the network would be the one role whose results
    differ by machine.

    This is the same rule as the wake checks above, one step further in: not
    *can the scheduler put the role here*, but *can the role find what it is
    being asked to find once it arrives*. It needs no artefact-to-table map —
    each of these is one call reading one table, named in the op itself.
    """
    needs = {"code.probe": "an index (set `repo.onboard: true`)",
             "code.survey": "an index (set `repo.onboard: true`)",
             "web.fetch": "`fixture.web_cache` pages"}
    wanted = set((case.get("expect") or {}).get("calls") or [])
    repo = case.get("repo") or {}
    fixture = case.get("fixture") or {}

    for call, what in sorted(needs.items()):
        if call not in wanted:
            continue
        if call == "web.fetch":
            assert fixture.get("web_cache"), (
                f"{case['id']} expects {call} and seeds no pages: it wants {what}, "
                f"and without them the call cannot return anything the case "
                f"grades")
        else:
            assert repo.get("onboard"), (
                f"{case['id']} expects {call} and never onboards: it wants "
                f"{what}, and an empty index answers exactly like a search that "
                f"matched nothing")


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_a_prose_channel_is_woken_with_words(case):
    """
    Asking channels carry prose and the graph says which. Law 2 keeps words off
    messages so a recipient reads the row rather than the sender's summary of
    it — which is right for every channel that *tells* somebody something, and
    silent about the ones that ask.

    A question is about something no artefact holds; that is what makes it a
    question. So refs can name its subject and never its content, whether or
    not the two ends share a database. The Researcher made this obvious first
    because it shares none, and for a while that was taken as the whole reason:
    five question channels carried words and five did not, and which half a
    channel fell in depended on its recipient.

    `L1-RS-answer-from-the-clause-not-from-memory` seeded that message with
    neither, and the session said so in its own reply: "the architect's question
    was empty and there were no references to load". It answered from memory,
    which is the one failure the case exists to catch, and nothing else was
    available to it.

    Read off the edge rather than from a role name, for the same reason the
    exception is declared there: one fact in one place.
    """
    from rota.design import graph as graph_mod

    inbound = case.get("inbound") or {}
    if not inbound:
        return

    prose_verbs = {e.prose for e in graph_mod.load().edges if getattr(e, "prose", "")}
    if inbound.get("verb") not in prose_verbs:
        return
    if inbound.get("to") not in {e.t for e in graph_mod.load().edges
                                 if getattr(e, "prose", "")} | {"researcher"}:
        return

    assert (inbound.get("body_text") or "").strip(), (
        f"{case['id']} wakes {inbound.get('to')} with a `{inbound.get('verb')}` "
        f"carrying no words. That channel declares `prose` on the graph because "
        f"refs mean nothing to the recipient, so this is an empty question")


#: The calls that read a repository. `code.source` and `code.read` refuse
#: with no project_root, and `_with_repo` writes it only for a `repo:` block.
CODE_READS = {"code.source", "code.probe", "code.read"}

#: The cases that broke the two rules below when they came in (frame 326,
#: passes 1 to 1c). Each one owes a `repo:` block with the source the case
#: names, which is more than one YAML line. A case that only needed an index
#: got `repo.index_batch: true` in pass 1c. `onboard: true` is not that fix:
#: it indexes the main checkout before the batch worktree exists, and it
#: writes constraint zero. Remove an id when its case is fixed. Add none.
#: `OWED_FRAME` names the frame that owes the set. The F33 test reads it
#: against the open frames of the stack.
OWED_FRAME = "frame 326"
OWED = {
    "L1-AR-rewrite-the-guess-from-the-ruling",
    "L1-AR-re-annotate-from-the-principals-correction",
    "L1-AR-constrain-an-external-commitment",
    "L1-DV-say-why-the-test-cannot-pass",
    "L1-TE-a-new-behaviour-is-a-new-callable",
    "L1-TE-specify-criteria",
    "L1-TE-put-a-word-with-two-senses-to-the-principal",
    "L1-TS-act-on-the-reason-of-a-challenge",
    "L3-scope-becomes-a-ticket-with-criteria",
    "L3-a-challenge-reaches-the-role-that-can-answer-it",
}

#: The size of `OWED` now. The set may only shrink, so lower this number
#: when an id leaves it.
OWED_CEILING = 10


def _seats(case):
    """The role and the mode of each session the case runs."""
    if case.get("first"):
        return [(leg["role"], leg.get("prompt") or leg.get("verb")
                 or leg.get("tick", "")) for leg in (case["first"], case["then"])]
    return [(case.get("role"), fixtures.mode_of(case))]


def _code_problems(case):
    from rota.roles import prompts

    repo = case.get("repo") or {}
    indexed = (repo.get("onboard") or repo.get("index_batch")
               or (case.get("fixture") or {}).get("code_index"))
    for role, mode in _seats(case):
        if not role or not mode:
            continue
        # A mode with no `.tools` file holds the role's whole namespace, and
        # `prompts.available` lists mode names (frame 326, review 1b).
        tools = prompts.mode_tools(role, mode)
        if tools is None:
            import sqlite3

            from rota.core.sandbox import build

            tools = build(role, sqlite3.connect(":memory:")).functions()
        reads = sorted(CODE_READS & set(tools))
        if reads and not repo:
            yield (f"{role}/{mode} holds {', '.join(reads)} and the case "
                   f"declares no `repo:`, so a read refuses with no "
                   f"project_root")
        # The tools, not the brief: `verdict_failed` and `finding_violated`
        # hold the probe and never name it, and their cases probed an empty
        # index (frame 326, review 1, finding 2).
        if "code.probe" in tools and not indexed:
            yield (f"{role}/{mode} holds `code.probe` and the case sets no "
                   f"`repo.index_batch`, no `repo.onboard` and no "
                   f"`fixture.code_index`, so every probe returns nothing")


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_a_case_whose_mode_reads_code_holds_the_code(case):
    """
    Frame 326, faults A and B. The Tester's challenge mode gained
    `code.source` on 2026-10-02, and three of its cases kept no repository.
    The Developer's tests_failing brief says the probe "will find it", and
    its cases indexed nothing. Each case then measured a refusal or an
    empty result, and only in the register: a night always onboards and
    always has project_root. The rule reads the mode's own tools, so a new
    mode or a new case meets it with no edit here.

    A seeded `fixture.code_index` counts as an index. Three Architect cases
    seed the night's rows so the prompt does not move.
    """
    problems = list(_code_problems(case))
    if case["id"] in OWED:
        assert problems, (f"{case['id']} is fixed. Remove it from OWED")
        pytest.skip(f"owed since {OWED_FRAME}: {problems[0]}")
    assert not problems, f"{case['id']}: " + "; ".join(problems)


def test_the_owed_set_only_shrinks_and_names_real_cases():
    """
    `OWED` excuses a case from the rule above. An id that joins the set
    excuses a new fault, and an id that names no case excuses nothing and
    hides a rename (frame 326, review 1, finding 4).
    """
    ids = {c["id"] for c in CASES}
    assert not OWED - ids, (
        f"OWED names no case for {sorted(OWED - ids)}. Remove the id, or "
        f"follow the rename")
    assert len(OWED) <= OWED_CEILING, (
        f"OWED holds {len(OWED)} ids against a ceiling of {OWED_CEILING}. "
        f"Fix the new case. Do not excuse it")
    assert len(OWED) == OWED_CEILING, (
        f"OWED shrank to {len(OWED)}. Lower OWED_CEILING to match")
