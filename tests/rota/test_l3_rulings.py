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
TABLE: list[tuple[str, int, str, int, int, int]] = []

rota_serial_plugin.refuse_a_key_the_register_does_not_hold()

pytestmark = pytest.mark.skipif(
    not (os.environ.get("ROTA_L1") or paths.DEV_DB.exists()),
    reason="no cassettes recorded; set ROTA_L1=1 to run against a model",
)


def _cases() -> list[dict]:
    return list(fixtures.load_case(CASES) or [])


def landed_lines(db_path: Path, reply_id: str,
                 by_ref: bool = False) -> dict[str, dict] | None:
    """The seat's rows of the landed ruling on `reply_id`, by line, or by
    ref for a clarify, or None when no ruling landed. A stale ruling is no
    landing (the review of 5b525a72, low 1). The door writes a clarify row
    with no line, so a clarify case reads its rows by ref (high 1)."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        ruling = conn.execute("SELECT id FROM rulings WHERE reply_id = ? "
                              "AND status = 'landed'", (reply_id,)).fetchone()
        if ruling is None:
            return None
        rows = [dict(r) for r in conn.execute(
            "SELECT line, ref, verdict, act, target_kind FROM ruled_refs "
            "WHERE ruling_id = ? AND source = 'reading'", (ruling["id"],))]
        key = "ref" if by_ref else "line"
        return {str(r[key]): r for r in rows if r[key] is not None}
    finally:
        conn.close()


def judge(case: dict, got: dict[str, dict] | None, asked: bool) -> list[str]:
    """Each line's verdict, act and target kind against `expect_lines`, or
    each row's against `expect_refs` for a clarify."""
    want = ({"lines": case["expect_refs"]} if case.get("expect_refs")
            else case["expect_lines"])
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


def retire_problems(db_path: Path, case: dict) -> list[str]:
    """One problem for each criterion of `expect_retired` that the landed
    ruling does not retire. A case with no such field gets none.

    The check reads `criteria_page_acts`, the reader the relay wake offers
    `criteria.retire` by, so the case counts the retire the code would do
    (sprint 35, row 3). The case runs no relay wake, so no row holds
    `retired_by` yet."""
    want = case.get("expect_retired") or []
    if not want:
        return []
    from rota.roles.api import criteria_page_acts

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        retired = set(criteria_page_acts(conn, want)["retire"])
    finally:
        conn.close()
    return [f"criterion {cid}: not retired, expected a retire"
            for cid in want if cid not in retired]


class _Turns:
    """The backend, counting its completions, so each call the sandbox
    runs knows the turn that produced it."""

    def __init__(self, inner):
        self.inner, self.turn, self.calls = inner, 0, []
        self.name = getattr(inner, "name", "")

    @property
    def misses(self) -> int:
        return getattr(self.inner, "misses", 0)

    def complete(self, system, user, pins, tools=None):
        self.turn += 1
        return self.inner.complete(system, user, pins, tools=tools)


def _logged_calls(turns: list[_Turns]):
    """`Sandbox.call`, writing each call with its turn and its refusal.

    A door refusal is the exception the call raises. The runner's own
    errors, a repeated turn or a budget, raise in no call (the review of
    5b525a72, high 2)."""
    from unittest import mock

    from rota.core.sandbox import Sandbox

    real = Sandbox.call

    def call(self, dotted, *pos, **kwargs):
        log = turns[-1]
        try:
            out = real(self, dotted, *pos, **kwargs)
        except Exception as exc:
            log.calls.append({"turn": log.turn, "fn": dotted,
                              "refusal": f"{dotted}: {exc}"})
            raise
        log.calls.append({"turn": log.turn, "fn": dotted, "refusal": None})
        return out

    return mock.patch.object(Sandbox, "call", call)


def refusals(log: _Turns) -> list[dict]:
    """Every door refusal with its turn and the seat's next call."""
    rows = []
    # Turn 0 is the runner's own read before the first completion, and no
    # seat made it.
    calls = [c for c in log.calls if c["turn"] > 0]
    for i, c in enumerate(calls):
        if c["refusal"] is None:
            continue
        nxt = calls[i + 1] if i + 1 < len(calls) else None
        rows.append({"turn": c["turn"], "refusal": c["refusal"],
                     "next": f"turn {nxt['turn']} {nxt['fn']}" if nxt else "none"})
    return rows


def runner_errors(result, refused: list[dict]) -> list[str]:
    """The session's errors that no door raised."""
    # The text after the first colon, because a held call's error reads
    # "<fn> (held): <refusal>" (the review of d9bc5e96, low 1).
    def tail(text: str) -> str:
        return text.split(":", 1)[-1].strip()

    door = {tail(r["refusal"]) for r in refused}
    return [e for e in result.outcome.errors if tail(e) not in door]


@pytest.mark.parametrize("case", _cases(), ids=[c["id"] for c in _cases()])
def test_l3_rulings_case(case, tmp_path, backend_factory, dev_db):  # noqa: F811
    if PROFILE_ERROR:
        pytest.fail(PROFILE_ERROR)
    instructions = fixtures.instructions_for(case)
    pinned = MODEL if os.environ.get("ROTA_MODEL_FORCE") else case.get("model", MODEL)
    pins = Pins(model=pinned, temperature=0.0, think=think_for(pinned),
                **PROFILE_PINS)
    turns: list[_Turns] = []

    def counted():
        turns.append(_Turns(backend_factory()))
        return turns[-1]

    with _logged_calls(turns):
        passed, threshold, results = fixtures.run_sampled(
            case, tmp_path, counted, pins=pins, instructions=instructions)
    stamp = pins.with_prompt(instructions)
    for r, log in zip(results, turns):
        problem = fixtures.for_run(case, r.run)
        reply_id = problem["inbound"]["id"]
        db_path = tmp_path / f"{case['id']}_{r.run}.db"
        got = landed_lines(db_path, reply_id,
                           by_ref=bool(problem.get("expect_refs")))
        asked = any(m["to_role"] == "principal" for m in r.delta.messages)
        wrong = judge(problem, got, asked) + retire_problems(db_path, problem)
        refused = refusals(log)
        errors = runner_errors(r, refused)
        r.problems = list(r.problems) + wrong
        r.passed = not r.problems
        transcript = r.transcript() + [{"refusals": refused,
                                        "runner_errors": errors}]
        record_case_run(dev_db, case["id"], stamp, r.run, r.passed,
                        r.problems, transcript, live=r.live_calls > 0,
                        system=r.system_text(),
                        protocol="native" if native_default() else "text")
        TABLE.append((case["id"], r.run, "right" if not wrong else "wrong",
                      len(r.outcome.completions), len(refused), len(errors)))
        for row in refused:
            print(f"\n{case['id']} run {r.run} turn {row['turn']}: "
                  f"{row['refusal'][:300]}\n  next call: {row['next']}")
        for e in errors:
            print(f"\n{case['id']} run {r.run} runner: {e[:200]}")
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
    """One table for the run: case, right or wrong, turns, refusals,
    and the runner errors in a column of their own."""
    if not TABLE:
        return
    print("\ncase | run | reading | turns | refusals | runner errors")
    for row in TABLE:
        print(" | ".join(str(x) for x in row))
