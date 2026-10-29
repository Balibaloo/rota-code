"""
L1 — every action a role can take, against a real model.

The tier that gives the vocabulary rework its verdict. Everything below it
proves the machine; this asks whether a role, told what it is answerable for and
handed a state where exactly one action is right, takes that action.

Cassettes make it affordable: the first run pays model time, every run after it
replays for nothing, and a prompt edit produces a miss — which is correct,
because a recording made against a different prompt is not evidence about this
one.

    ROTA_L1=1 ROTA_MODEL=qwen3:8b pytest tests/rota/test_l1.py -q    # or replay
    ROTA_L1=1 ROTA_MODEL=qwen3:8b ROTA_REFRESH=1 pytest tests/rota/test_l1.py -q

Name the model. Without `ROTA_MODEL` this tier records against `llama3.1:8b`,
which is not the model the gate replays, and two cases scored 0 of 5 on the
wrong model alone (observed: frame 60, 2026-09-21). A STALE failure prints the
whole command, with the window and the profile it would run under.

Serialised on purpose: no `xdist` here. Parallel model calls thrash the GPU and
the timings stop meaning anything.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

import rota_serial_plugin

from rota import paths
from rota.llm.cassettes import (RecordingBackend, ReplayOnlyBackend,
                               open_dev_db, record_case_run)
from rota.core.runner import native_default
from rota.llm.llm import OllamaBackend, Pins, profile_pins, think_for
from rota.roles import prompts
from rota.testkit import fixtures, interview, obligations

CASES = Path(__file__).parent / "cases"
MODEL = os.environ.get("ROTA_MODEL", "llama3.1:8b")
# num_ctx comes from `DEFAULT_NUM_CTX` and is deliberately not pinned here.
# It was pinned, at 8192, and stayed there when the default was raised to
# 12288 to stop the largest prompts being clipped -- so the fix reached
# everything except the suites that measure whether anything works. Two
# cases were still reporting `8192 tokens evaluated against a 8192 window`
# long after that was supposed to be impossible, and a prompt is truncated
# from the front, where the role is told who it is.
# ROTA_PROFILE names a profile whose [think] table sets the think pin per
# model (finding 81, 2026-09-15): the nights run qwen3.5:9b thinking, and
# a column recorded with ROTA_PROFILE=local-gemma-critic measures that.
# Without it the pin stays None and every earlier recording keeps its key.
# The rule lives in `rota.llm.llm` because `casestatus` matches a recording
# on the pin it sets, and two copies of one rule drift (frame 54).
# The profile's `max_tokens`, and its `num_ctx` when ROTA_NUM_CTX is unset
# (frame 323: the trial's cap never reached Ollama). A misspelt profile
# fails each case by name, and does not stop the collection of the suite.
try:
    PROFILE_PINS, PROFILE_ERROR = profile_pins(), ""
    PINS = Pins(model=MODEL, temperature=0.0, think=think_for(MODEL),
                **PROFILE_PINS)
except FileNotFoundError as exc:
    PROFILE_PINS = {}
    PROFILE_ERROR = f"ROTA_PROFILE={os.environ.get('ROTA_PROFILE')!r}: {exc}"
    PINS = Pins(model=MODEL, temperature=0.0)

# The door, called from the file that reads the register (frame 54,
# 2026-09-21). It refuses a replay whose ambient key the register does
# not hold. It is called here and not from a pytest hook: a hook that
# raises after collection runs on an xdist worker and ends the run in
# INTERNALERROR, with the reason nowhere in the output.
rota_serial_plugin.refuse_a_key_the_register_does_not_hold()

pytestmark = pytest.mark.skipif(
    not (os.environ.get("ROTA_L1") or paths.DEV_DB.exists()),
    reason="no cassettes recorded; set ROTA_L1=1 to run against a model",
)


def _cases() -> list[dict]:
    out = []
    for path in sorted(CASES.glob("l*.yaml")):
        out.extend(c for c in (fixtures.load_case(path) or [])
                   if not c.get("first")      # chains are L3's, in test_l3.py
                   # The night pages run in test_l3_rulings.py (frame 345).
                   and c.get("tier") != "l3_rulings")
    # Same-model cases stay contiguous: each alternation of the
    # bar model is a full weight reload on a GPU that fits one.
    out.sort(key=lambda c: c.get("model", ""))
    return out


def _ids(cases) -> list[str]:
    return [c["id"] for c in cases]


@pytest.fixture(scope="session")
def dev_db():
    paths.DEV_DB.parent.mkdir(parents=True, exist_ok=True)
    return open_dev_db(paths.DEV_DB)


@pytest.fixture
def backend_factory(dev_db):
    """
    Replay unless told otherwise.

    This tier used to sit out every default run — eighty tests skipped, so the
    half of the system that reasons was invisible unless you remembered an env
    var. The reason was never that replay is slow or non-deterministic; it is
    neither. It was that `RecordingBackend` turns a cassette *miss* into a live
    call, so a plain `pytest` on a machine with a stale recording would quietly
    start evaluating an 8B model.

    `ReplayOnlyBackend` already existed for exactly this and was never wired in
    here. A miss now fails the case instead, which is also the only honest
    report of an edited prompt: a skipped test and a stale one look identical
    from outside, and one of them is a lie.
    """
    if not os.environ.get("ROTA_L1"):
        return lambda: ReplayOnlyBackend(dev_db)
    refresh = bool(os.environ.get("ROTA_REFRESH"))
    # A column of the benchmark (COMPLETION.md, the order from here, step
    # 1): ROTA_BACKEND=litellm with ROTA_ENDPOINT records the same cases
    # against an OpenAI-compatible server, a llama-server holding a model
    # Ollama does not. Model names then carry litellm's `openai/` prefix.
    if os.environ.get("ROTA_BACKEND") == "litellm":
        from rota.llm.llm import LiteLLMBackend
        live = LiteLLMBackend(api_base=os.environ.get("ROTA_ENDPOINT") or None,
                              timeout=int(os.environ.get("ROTA_LLM_TIMEOUT", "600")))
        return lambda: RecordingBackend(live, dev_db, refresh=refresh)
    return lambda: RecordingBackend(
        OllamaBackend(), dev_db, refresh=refresh)


@pytest.mark.parametrize("case", _cases(), ids=_ids(_cases()))
def test_l1_case(case, tmp_path, backend_factory, dev_db):
    """
    Sampled, with a threshold. The count is kept rather than a bare boolean so a
    drift from 5/5 to 3/5 is visible as the regression it is.
    """
    if PROFILE_ERROR:
        pytest.fail(PROFILE_ERROR)
    instructions = prompts.compose(case["role"], fixtures.mode_of(case))

    # The ruling (2026-08-29): we are not locked to a model -- one model
    # carrying the capability is enough. A case that declares `model:` is
    # held by that model; the default stays the recording reference.
    # ROTA_MODEL_FORCE=1 puts every case on ROTA_MODEL, pins included: a
    # benchmark column measures one model across the register.
    pinned = MODEL if os.environ.get("ROTA_MODEL_FORCE") else case.get("model", MODEL)
    pins = Pins(model=pinned, temperature=0.0, think=think_for(pinned),
                **PROFILE_PINS)
    passed, threshold, results = fixtures.run_sampled(
        case, tmp_path, backend_factory, pins=pins, instructions=instructions)

    # Recorded against the instructions rather than the bare pins, so the
    # cockpit can tell a green result from a green result about a prompt that
    # has since been edited. Instructions only — the full prompt includes the
    # fixture, which would make every case's hash unique and staleness
    # meaningless.
    stamp = pins.with_prompt(instructions)
    for r in results:
        # The whole system text as well, because the brief is only its prefix:
        # the runner's session prose and the working set's `TOOL:` lines are in
        # the cassette key and not in the hash (frame 54).
        # `live` says whether a call reached the model. A replay and a
        # first-seen transcript are the same fourteen columns otherwise, so
        # the register counted one reply many times (frame 66, 2026-09-23).
        record_case_run(dev_db, case["id"], stamp, r.run, r.passed,
                        r.problems, r.transcript(), live=r.live_calls > 0,
                        system=r.system_text(),
                        protocol="native" if native_default() else "text")

    # Opt-in, and only on a failure. It costs a model call per failed run and
    # answers a question no assertion does: what did the session think it had?
    # Off by default because a replay-only pass must stay a replay-only pass --
    # this is the one call in the suite with no cassette behind it.
    if os.environ.get("ROTA_INTERVIEW") and os.environ.get("ROTA_L1"):
        for r in results:
            if r.passed or not r.outcome.user:
                continue
            called = list(r.delta.tool_calls)
            interview.record(
                dev_db, case["id"], r.run, stamp, r.problems,
                interview.conduct(r.outcome, called,
                                  OllamaBackend(), PINS),
                interview.ids_in(r.outcome.user), called)

    # Unknown is not the same as wrong, and reporting one as the other is how a
    # suite loses its meaning. A missing cassette says the prompt was edited and
    # nobody has re-measured; the model may be doing this perfectly. Both used to
    # render as "0/5 passed".
    if any("no cassette" in p for r in results for p in r.problems):
        pytest.fail(
            f"STALE {case['id']}: no recording for the current prompt — this "
            f"result is unknown, not bad. Re-earn it with\n"
            f"    "
            + fixtures.rerecord_command(pins, "tests/rota/test_l1.py"))

    # A guard that fired is not a failure and is not nothing: the role reached
    # for something it must not do and the system held. Printed on a pass too,
    # because that is exactly when it would otherwise be invisible.
    noted = sorted({n for r in results for n in r.notes})
    if noted:
        print(f"\n{case['id']} — reached and refused:\n  " + "\n  ".join(noted))

    # A case red by construction fails on every model, so its red says
    # nothing about the model (frame 326, fault C). After the STALE check,
    # because the gate reads STALE from a FAILED line. A pass means the owed
    # mode exists, and the marker must go.
    from rota.tools.casestatus import red_by_construction

    red = red_by_construction(case)
    if red:
        assert passed < threshold, (
            f"{case['id']}: {passed}/{len(results)} passed while it is marked "
            f"red by construction. Remove `red:` from the case")
        pytest.xfail(f"red by construction: {red}")

    assert passed >= threshold, (
        f"{case['id']}: {passed}/{len(results)} passed, needs {threshold}\n"
        + "\n".join(f"  run {r.run}: {'; '.join(r.problems)}"
                    for r in results if r.problems))


# ---------------------------------------------------------------------------
# The obligation set — which of them have a case
# ---------------------------------------------------------------------------

def test_the_obligation_set_comes_from_the_graph():
    """Drawing an edge creates a red row. The map cannot drift from the design,
    because the design emits it."""
    counts = obligations.summary()
    assert counts["L1"] > 100 and counts["L2"] > 40 and counts["L3"] > 200


def test_every_mode_has_a_case():
    """
    One case per prompt piece, which is the unit a pass-rate drop is
    attributable to.

    Stronger than it looks: a mode is a role plus what woke it, and the modes are
    enumerable from the graph rather than from a list somebody maintains. Adding
    a mode file with no case turns this red, which is the point — the modes that
    went longest without one were Developer's, and both of them had tool lists
    that could not do what the prose asked.
    """
    from rota.design import graph as graph_mod

    covered = {(c["role"], fixtures.mode_of(c)) for c in _cases()}
    missing = sorted(
        f"{role}/{mode}"
        for role in graph_mod.load().roles
        for mode in prompts.available(role)
        if (role, mode) not in covered)
    assert not missing, f"{len(missing)} mode(s) with no L1 case: {missing}"


@pytest.mark.skipif(True, reason="the obligation set is not yet fully covered")
def test_every_l1_obligation_has_a_case():
    """
    The target. Skipped rather than deleted: a red row you can see is worth more
    than an obligation nobody wrote down, and this is the one that says how far
    there is to go.
    """
    covered = set()
    for case in _cases():
        for table in ((case.get("expect") or {}).get("writes") or {}):
            covered.add(f"{case['role']}:{table}")
    missing = [o.id for o in obligations.l1()
               if f"{o.role}:{o.what.split('.')[0]}" not in covered]
    assert not missing, f"{len(missing)} L1 obligations with no case"
