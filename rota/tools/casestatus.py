"""
Where every model-facing case actually stands, without running anything.

    python -m rota.tools.casestatus            # everything, worst first
    python -m rota.tools.casestatus --red      # only what is not green

The report reads one model's recordings and says which on its second line.
`--model` names it, `ROTA_MODEL` sets it, and the last resort is the model the
gate replays. A count read under a model the suite does not run is a true
number about nothing, and one was quoted for two days as prompt drift.

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
import os
import sqlite3
from pathlib import Path

from .. import paths
from ..llm.cassettes import trust
from ..llm.llm import DEFAULT_NUM_CTX, Pins, think_for

from ..testkit import fixtures


def _cases() -> list[dict]:
    out = []
    for pattern in ("l*.yaml", "g*.yaml"):
        for path in sorted(paths.CASES.glob(pattern)):
            out.extend(fixtures.load_case(path) or [])
    return out


def model_for(named: str = "") -> str:
    """
    Which model's recordings this report reads. Named, then ambient, then the
    gate's.

    The default was `llama3.1:8b` and `status` read no environment at all, so
    the same register answered two ways: the bare command printed 67 stale and
    50 green, and `--model qwen3:8b` printed 0 stale and 107 green (observed:
    frame 54's run of both commands, 2026-09-21). Both numbers were right.
    Frame 49 then carried a 72-case obligation that was an artefact of this
    default, and no reader could see it, because the report never said which
    model it had read.

    The last resort is the gate's model and never `DEFAULT_MODEL`, whose own
    fallback is the `llama3.1:8b` that caused this.
    """
    if named:
        return named
    # Lazily, and from the gate, because the gate declares the model the suite
    # replays. One declaration: a second copy here would be the same fault in
    # a new place.
    from .gate import FALLBACK_MODEL

    return os.environ.get("ROTA_MODEL") or FALLBACK_MODEL


def status(model: str = "") -> list[dict]:
    # Through the one opener that migrates: a raw connect here read the
    # committed db from before `load_id` existed and died inside `trust`.
    from ..llm.cassettes import open_dev_db

    model = model_for(model)
    conn = open_dev_db(paths.DEV_DB)

    rows = []
    for case in _cases():
        role = case.get("role") or (case.get("then") or {}).get("role")
        if not role:
            continue
        # The one-model ruling: a case that declares `model:` is held by
        # that model, and this report must read the same recordings the
        # suite replays -- a qwen-held green rendering as a llama STALE
        # would be the report contradicting the register it exists to show.
        #
        # The pins are the tiers' own, field by field, because the report
        # matches a recording on them (frame 54, 2026-09-21). `num_ctx` comes
        # from `DEFAULT_NUM_CTX`, which is what a tier runs at: all three tier
        # files deliberately pin no window. The temperature is 0.0, and every
        # cassette in the register is at 0.0. `think` comes from
        # `ROTA_PROFILE`, through the one rule the tier stamps with.
        pinned = case.get("model", model)
        want = Pins(model=pinned, temperature=0.0,
                    think=think_for(pinned)).with_prompt(
            fixtures.instructions_for(case))

        # A run that died for want of a cassette is not a result, and until
        # `record_case_run` refused to write those there were three thousand of
        # them. They are excluded rather than deleted: the rows are somebody's
        # history even when they are not evidence.
        #
        # They can carry a *current* prompt hash, which is what made them
        # dangerous. `prompt_hash` covers the composed brief, the mode prompt
        # included, so a brief edit does stale a case. What it does not cover
        # is the runner's session prose and the working set's `TOOL:` lines,
        # which are the rest of the system text and are in the cassette key --
        # so a tools edit left every hash current and the case read green
        # while the suite could not replay it.
        #
        # `system_hash` is therefore written by `record_case_run` and is not
        # matched on here. The blocker is that this report cannot compose the
        # system text: it is built inside `run_session`, from a sandbox over
        # the case's seeded database, and there is no second definition of it
        # to call. Matching on a value this report cannot compute would stale
        # every case. The match is widened when one composition serves both.
        #
        # `load_id` stays out for two reasons. It is `model@epoch//7200`, so
        # matching on it would stale every case two hours after its recording,
        # and `trust` reads several loads to tell `provisional` from `earned`.
        here = list(conn.execute(
            "SELECT passed, problems FROM case_runs "
            "WHERE case_id = ? AND prompt_hash = ? AND model = ? "
            "  AND num_ctx = ? AND temperature = ? AND protocol = ? "
            "  AND extras = ? "
            "  AND NOT (passed = 0 AND (problems LIKE '%no cassette for%' "
            "                        OR transcript LIKE '%no cassette for%')) "
            "ORDER BY seq DESC LIMIT ?",
            (case["id"], want.prompt_hash, want.model, want.num_ctx,
             want.temperature,
             # Text, because 18570 of the register's 18604 cassettes key as
             # text and none as native (observed: the design review's probe 5,
             # 2026-09-21). A tier offers the model no native schemas.
             "text",
             json.dumps(want.extras(), sort_keys=True),
             case.get("runs", 5))))
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
            # The ruling (2026-08-27): a green that flipped from red counts
            # as fixed only after a second load confirms it. `trust` reads
            # the same rows; a provisional green renders as its own state so
            # a lucky load cannot be quoted as a fix.
            if state == "green" and trust(conn, case["id"]) == "provisional":
                state = "PROV"

        why = ""
        if state == "FAIL":
            problems = [p for r in here for p in json.loads(r["problems"] or "[]")]
            why = problems[0] if problems else ""

        rows.append({"id": case["id"], "state": state, "passed": passed,
                     "of": len(here), "need": threshold, "why": why,
                     "role": role, "ever": ever})
    return rows


def render(rows: list[dict], red_only: bool = False, model: str = "") -> str:
    order = {"FAIL": 0, "PROV": 1, "STALE": 2, "NEW": 3, "green": 4}
    rows = sorted(rows, key=lambda r: (order[r["state"]], r["id"]))
    counts = {k: sum(1 for r in rows if r["state"] == k) for k in order}

    out = [f"{counts['FAIL']} failing, {counts['PROV']} provisional, "
           f"{counts['STALE']} stale, {counts['NEW']} never measured, "
           f"{counts['green']} green"]
    if model:
        # The key these counts were read under, printed with them. A count
        # quoted without its model is the 72 of frame 49: a true number about
        # a model the suite does not run.
        extras = json.dumps(Pins(model=model, think=think_for(model)).extras(),
                            sort_keys=True)
        out.append(f"  read under {model}, window {DEFAULT_NUM_CTX}, "
                   f"protocol text" + (f", pins {extras}" if extras != "{}" else ""))
    if counts["PROV"]:
        out.append("  provisional greened on one load after being red: "
                   "re-earn on a second load before quoting it as fixed")
    if counts["STALE"] or counts["NEW"]:
        # Through the one definition the tiers print, because this footer was
        # the last place that still named no model. Frame 60 repaired the
        # tiers' own STALE message and their usage lines, and the report's
        # advice line was a fourth site nobody had read: it told the reader to
        # re-earn a case under whatever was ambient, which is how two cases
        # flipped from fail to pass on the model alone (observed: frame 60,
        # the same 20 case ids run twice, 2026-09-21).
        out.append("  stale is unmeasured, not bad: " + fixtures.rerecord_command(
            Pins(model=model or "", num_ctx=DEFAULT_NUM_CTX,
                 think=think_for(model) if model else None),
            "tests/rota/test_l1.py"))
    out.append("")

    for r in rows:
        if red_only and r["state"] in ("green", "PROV"):
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
    ap.add_argument("--model", default="",
                    help="the model the recordings are held by; the default "
                         "is ROTA_MODEL, then the model the gate replays")
    args = ap.parse_args()
    model = model_for(args.model)
    print(render(status(model), red_only=args.red, model=model))
