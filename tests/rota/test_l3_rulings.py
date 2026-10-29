"""
L3 rulings: the Liaison reads 24 real pages of nights 170 to 175.

Roman ruled on 2026-10-28: "the night is the wrong scale of test. If we want
to make door changes then test the liaison itself". Each case is one page, his
real reply, and the real doors of `rota/roles/api.py`. The session runs turn
after turn until a ruling lands or the runner ends it, as on a night. The
check reads the landed `ruled_refs` rows per line against the judge's
`expect` line (frame 345).

    ROTA_L1=1 ROTA_MODEL=qwen3:8b pytest tests/rota/test_l3_rulings.py -q
    ROTA_L1=1 ROTA_MODEL=qwen3:8b pytest tests/rota/test_l3_rulings.py -q -s -k n171

Without `ROTA_L1` the cases replay, and a case with no recording is STALE.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pytest

import rota_serial_plugin

from rota import paths
from rota.core.runner import native_default
from rota.llm.cassettes import record_case_run
from rota.llm.llm import Pins, think_for
from rota.testkit import fixtures

from .test_l1 import PROFILE_ERROR, PROFILE_PINS, backend_factory, dev_db  # noqa: F401

CASES = Path(__file__).parent / "cases" / "l3_rulings.yaml"
MODEL = os.environ.get("ROTA_MODEL", "qwen3:8b")
TABLE: list[tuple[str, int, str, int, int]] = []

rota_serial_plugin.refuse_a_key_the_register_does_not_hold()

pytestmark = pytest.mark.skipif(
    not (os.environ.get("ROTA_L1") or paths.DEV_DB.exists()),
    reason="no cassettes recorded; set ROTA_L1=1 to run against a model",
)


def _cases() -> list[dict]:
    return list(fixtures.load_case(CASES) or [])


def landed_lines(db_path: Path, reply_id: str) -> dict[str, dict] | None:
    """The rows of the ruling on `reply_id`, by line, or None when no
    ruling landed."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        ruling = conn.execute("SELECT id FROM rulings WHERE reply_id = ?",
                              (reply_id,)).fetchone()
        if ruling is None:
            return None
        return {str(r["line"]): dict(r) for r in conn.execute(
            "SELECT line, ref, verdict, act, target_kind FROM ruled_refs "
            "WHERE ruling_id = ? AND line IS NOT NULL AND source = 'reading'",
            (ruling["id"],))}
    finally:
        conn.close()


def judge(case: dict, got: dict[str, dict] | None, asked: bool) -> list[str]:
    """Each line's verdict, act and target kind against `expect_lines`."""
    want = case["expect_lines"]
    if want.get("ask"):
        out = [] if asked else ["expected a question to him; none was sent"]
        return out + (["expected no ruling; one landed"] if got else [])
    if got is None:
        return ["no ruling landed"]
    problems = []
    for line, check in want["lines"].items():
        row = got.get(line)
        if check.get("verdict") == "absent":
            if row:
                problems.append(f"line {line}: expected no ruling, got {row['verdict']}")
            continue
        if row is None:
            problems.append(f"line {line}: no ruling")
            continue
        for key, value in check.items():
            if row.get(key) != value:
                problems.append(f"line {line}: {key} {row.get(key)!r}, "
                                f"expected {value!r}")
    return problems


def refusals(result) -> list[dict]:
    """Every refusal with its turn and the seat's next call.

    The runner keeps the refusals in order and not by turn. A turn whose
    call was refused is each turn with a call before the turn that landed,
    so the refusals pair with those turns in order."""
    from rota.llm import toolproto

    out = result.outcome
    turns = []
    for n in range(len(out.completions)):
        calls = fixtures._reply_calls(out, n, toolproto)
        names = [getattr(c, "name", "refused") for c in calls]
        if names:
            turns.append((n + 1, names))
    errors = list(out.errors)
    rows = []
    for i, (turn, _names) in enumerate(turns):
        if not errors:
            break
        nxt = turns[i + 1][1] if i + 1 < len(turns) else []
        rows.append({"turn": turn, "refusal": errors.pop(0), "next": nxt})
    return rows


@pytest.mark.parametrize("case", _cases(), ids=[c["id"] for c in _cases()])
def test_l3_rulings_case(case, tmp_path, backend_factory, dev_db):  # noqa: F811
    if PROFILE_ERROR:
        pytest.fail(PROFILE_ERROR)
    instructions = fixtures.instructions_for(case)
    pinned = MODEL if os.environ.get("ROTA_MODEL_FORCE") else case.get("model", MODEL)
    pins = Pins(model=pinned, temperature=0.0, think=think_for(pinned),
                **PROFILE_PINS)
    passed, threshold, results = fixtures.run_sampled(
        case, tmp_path, backend_factory, pins=pins, instructions=instructions)
    stamp = pins.with_prompt(instructions)
    for r in results:
        problem = fixtures.for_run(case, r.run)
        reply_id = problem["inbound"]["id"]
        got = landed_lines(tmp_path / f"{case['id']}_{r.run}.db", reply_id)
        asked = any(m["to_role"] == "principal" for m in r.delta.messages)
        wrong = judge(problem, got, asked)
        refused = refusals(r)
        r.problems = list(r.problems) + wrong
        r.passed = not r.problems
        transcript = r.transcript() + [{"refusals": refused}]
        record_case_run(dev_db, case["id"], stamp, r.run, r.passed,
                        r.problems, transcript, live=r.live_calls > 0,
                        system=r.system_text(),
                        protocol="native" if native_default() else "text")
        TABLE.append((case["id"], r.run, "right" if not wrong else "wrong",
                      len(r.outcome.completions), len(refused)))
        for row in refused:
            print(f"\n{case['id']} run {r.run} turn {row['turn']}: "
                  f"{row['refusal']}\n  next call: {row['next']}")
    passed = sum(1 for r in results if r.passed)
    if any("no cassette" in p for r in results for p in r.problems):
        pytest.fail(f"STALE {case['id']}: no recording for the current "
                    f"prompt. Re-earn it with\n    "
                    + fixtures.rerecord_command(pins, "tests/rota/test_l3_rulings.py"))
    assert passed >= threshold, (
        f"{case['id']}: {passed}/{len(results)} passed, needs {threshold}\n"
        + "\n".join(f"  run {r.run}: {'; '.join(r.problems)}"
                    for r in results if r.problems))


def teardown_module(module):
    """One table for the run: case, right or wrong, turns, refusals."""
    if not TABLE:
        return
    print("\ncase | run | reading | turns | refusals")
    for row in TABLE:
        print(" | ".join(str(x) for x in row))
