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
