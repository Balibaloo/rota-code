"""
Where every model-facing case actually stands, without running anything.

    python -m rota.tools.casestatus            # everything, worst first
    python -m rota.tools.casestatus --red      # only what is not green

The distinction this exists for is **stale versus failing**, and it is not
cosmetic. A case with no recording against the current prompt is *unmeasured*:
the role may be doing the job perfectly and nobody has looked since the brief
was edited. A case that failed is a case that was measured and got it wrong.
The suite prints them differently and I still read a run of seven failures as
seven failures when three of them were unknowns -- because the count is on the
last line and the reason is thirty lines up, and I quoted the count.

So the count is the thing that has to carry the distinction:

    4 failing, 3 stale, 61 green

`case_runs` records the prompt hash each result was earned against, which makes
this a query rather than a test run. Recomposing the brief here costs
milliseconds and is the same composition the tier uses, so a case is stale here
exactly when it is stale there.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from .. import paths
from ..llm.llm import Pins

from ..testkit import fixtures


def _cases() -> list[dict]:
    out = []
    for path in sorted(paths.CASES.glob("l*.yaml")):
        out.extend(fixtures.load_case(path) or [])
    return out


def status(model: str = "llama3.1:8b") -> list[dict]:
    conn = sqlite3.connect(paths.DEV_DB)
    conn.row_factory = sqlite3.Row

    rows = []
    for case in _cases():
        role = case.get("role") or (case.get("then") or {}).get("role")
        if not role:
            continue
        want = Pins(model=model, temperature=0.0).with_prompt(
            fixtures.instructions_for(case))

        here = list(conn.execute(
            "SELECT passed, problems FROM case_runs "
            "WHERE case_id = ? AND prompt_hash = ? ORDER BY seq DESC LIMIT ?",
            (case["id"], want.prompt_hash, case.get("runs", 5))))
        ever = conn.execute(
            "SELECT COUNT(*) n FROM case_runs WHERE case_id = ?",
            (case["id"],)).fetchone()["n"]

        threshold = case.get("pass", 3)
        if not here:
            state = "STALE" if ever else "NEW"
            passed = None
        else:
            passed = sum(r["passed"] for r in here)
            state = "green" if passed >= threshold else "FAIL"

        why = ""
        if state == "FAIL":
            problems = [p for r in here for p in json.loads(r["problems"] or "[]")]
            why = problems[0] if problems else ""

        rows.append({"id": case["id"], "state": state, "passed": passed,
                     "of": len(here), "need": threshold, "why": why,
                     "role": role, "ever": ever})
    return rows


def render(rows: list[dict], red_only: bool = False) -> str:
    order = {"FAIL": 0, "STALE": 1, "NEW": 2, "green": 3}
    rows = sorted(rows, key=lambda r: (order[r["state"]], r["id"]))
    counts = {k: sum(1 for r in rows if r["state"] == k) for k in order}

    out = [f"{counts['FAIL']} failing, {counts['STALE']} stale, "
           f"{counts['NEW']} never measured, {counts['green']} green"]
    if counts["STALE"] or counts["NEW"]:
        out.append("  stale is unmeasured, not bad: "
                   "ROTA_L1=1 python -m pytest tests/rota/test_l1.py -q")
    out.append("")

    for r in rows:
        if red_only and r["state"] == "green":
            continue
        score = f"{r['passed']}/{r['of']}" if r["passed"] is not None else "  -"
        line = f"  {r['state']:<5} {score:>5} (need {r['need']})  {r['id']}"
        out.append(line)
        if r["why"]:
            out.append(f"              {r['why'][:96]}")
    return "\n".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--red", action="store_true", help="hide green cases")
    ap.add_argument("--model", default="llama3.1:8b")
    args = ap.parse_args()
    print(render(status(args.model), red_only=args.red))
