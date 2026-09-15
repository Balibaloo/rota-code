"""
The run's progress, one block, rewritten each step (Roman, 2026-09-15).

Every line is a fact of the run database or the walk: the phase the night
script named, the stage from the tick that fired last, the committed
sessions of this phase against the previous night's count for the same
phase and outcome, minutes elapsed against the previous night's minutes,
the last page and the last wake, and the attempts on the tick at the
frontier. The reference is one night, and the shape changes between
nights, so the raw counts stand beside the percentage.

    python probes/progress.py <run> "<phase>"     # render once, to stdout

walk.py calls `write()` after each step; `finish()` records the phase's
count and minutes as the next night's reference.
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNS = Path(os.environ.get("ROTA_RUNS", REPO / ".rota"))

STAGES = {
    "tick:slicing": "slicing", "tick:criteria": "criteria", "tick:define": "criteria",
    "tick:annotate": "criteria", "tick:grouping": "criteria", "tick:challenge": "criteria",
    "tick:tests_missing": "tests", "tick:batch_start": "build",
    "tick:tests_failing": "fix loop", "tick:verdict_failed": "fix loop",
    "tick:review": "review", "tick:structural_review": "structural review",
    "tick:finding_violated": "structural review", "tick:signoff": "signoff",
    "tick:quarantined": "stuck",
}
PAGES = {"present", "confirm", "converse", "verdict", "submit", "clarify", "report"}


def _ref_path(run: str) -> Path:
    return RUNS / f"progress_ref_{run}.json"


def reference(run: str) -> dict:
    p = _ref_path(run)
    return json.loads(p.read_text()) if p.exists() else {}


def finish(run: str, phase: str, wakes: int, minutes: float, outcome: str, night: str = "") -> None:
    """The phase's count and minutes become the next night's reference for
    the same phase and outcome; the one before it is kept as `previous`."""
    ref = reference(run)
    key = f"{phase} / {outcome}"
    ref[key] = {"wakes": wakes, "minutes": round(minutes, 1), "outcome": outcome,
                "night": night, "previous": ref.get(key, {}).get("wakes")}
    _ref_path(run).write_text(json.dumps(ref, indent=1))


def _stage(conn: sqlite3.Connection, last) -> str:
    merged = conn.execute("SELECT COUNT(*) FROM batches WHERE status = 'merged'").fetchone()[0]
    running = conn.execute("SELECT COUNT(*) FROM batches WHERE status = 'running'").fetchone()[0]
    if merged and not running and last and last["wake_kind"] not in ("tick:slicing", "tick:criteria"):
        return "merge"
    if not last:
        return "start"
    kind, detail = last["wake_kind"], last["wake_detail"] or ""
    if kind == "message":
        return "pages" if (last["role"] == "liaison" and detail in PAGES) else f"message ({last['role']}: {detail})"
    stage = STAGES.get(kind, kind.replace("tick:", ""))
    if stage == "fix loop" and detail.startswith("attempt"):
        stage = f"fix loop ({detail} of 3)"
    return stage


def render(run: str, phase: str, n0: int = 0, t0: float | None = None,
           last_page: str = "", db: Path | None = None) -> str:
    db = db or RUNS / f"{run}.db"
    conn = sqlite3.connect(db); conn.row_factory = sqlite3.Row
    n = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    last = conn.execute("SELECT role, wake_kind, wake_detail, committed FROM sessions "
                        "ORDER BY rowid DESC LIMIT 1").fetchone()
    so_far = n - n0
    minutes = (time.time() - t0) / 60 if t0 else 0.0
    stage = _stage(conn, last)
    # attempts on the frontier tick: the scheduler's own count
    # attempts on the frontier tick: the scheduler's count for the tick that
    # fired last; a quarantined tick from an earlier phase is not the frontier
    tries = None
    if conn.execute("SELECT name FROM sqlite_master WHERE name = 'tick_attempts'").fetchone():
        if last and last["wake_kind"].startswith("tick:"):
            tries = conn.execute("SELECT tick_key, attempts, quarantined FROM tick_attempts "
                                 "WHERE tick_key LIKE ? ORDER BY rowid DESC LIMIT 1",
                                 (f"%|{last['wake_kind']}|%",)).fetchone()
        if tries is None:
            tries = conn.execute("SELECT tick_key, attempts, quarantined FROM tick_attempts "
                                 "WHERE attempts > 0 AND quarantined = 0 "
                                 "ORDER BY attempts DESC, rowid DESC LIMIT 1").fetchone()
    ref = reference(run)
    refs = {k: v for k, v in ref.items() if k.startswith(phase + " /")}
    # the reference for this phase: prefer the outcome that ends the phase well
    pick = None
    for want in ("merged", "onboarded", "stuck", "quiet"):
        for k, v in refs.items():
            if v.get("outcome") == want:
                pick = (k, v); break
        if pick: break
    lines = [f"# {run}: {phase}", f"stage: {stage}"]
    if pick:
        k, v = pick
        est, mins = v["wakes"], v["minutes"]
        left = est - so_far
        left_s = f"about {left}" if left >= 0 else f"past the estimate by {-left}"
        pct = int(100 * so_far / est) if est else 0
        lines += [f"wakes: {so_far} so far / {est} on night {v.get('night') or '?'} ({v['outcome']}) = {pct}%; left: {left_s} (a ceiling: a stuck night ends at three failed attempts of one tick)",
                  f"minutes: {minutes:.0f} so far / {mins:.0f} on night {v.get('night') or '?'} for this phase"]
    else:
        lines += [f"wakes: {so_far} so far; no reference for this phase yet",
                  f"minutes: {minutes:.0f} so far"]
    lines.append(f"last page: {last_page or '(none yet)'}")
    if last:
        lines.append(f"last wake: {last['role']}:{last['wake_kind']}{' ' + last['wake_detail'] if last['wake_detail'] else ''}"
                     f"{'' if last['committed'] else ' (failed)'}")
    if tries:
        q = " (quarantined)" if tries["quarantined"] else ""
        lines.append(f"attempts on {tries['tick_key']}: {tries['attempts']} of 3{q}")
    lines += ["", "reference: one night, one sample; the shape changes between nights (night 69 ran the review three times, night 70 once), so the same count can mean different distances. The raw counts stand beside the percentage.",
              f"written: {time.strftime('%H:%M:%S')}"]
    conn.close()
    return chr(10).join(lines) + chr(10)


def write(run: str, phase: str, n0: int = 0, t0: float | None = None, last_page: str = "") -> Path:
    out = RUNS / f"progress_{run}.md"
    out.write_text(render(run, phase, n0, t0, last_page), encoding="utf-8")
    return out


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    print(render(sys.argv[1], sys.argv[2]), end="")
