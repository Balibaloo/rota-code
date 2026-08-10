"""
Progress: how far the build is, computed rather than reported.

Every number here is derived from something that already exists for another
reason — the milestone's own checkboxes, the graph, the case files, the case-run
log the L1 suite writes. Nothing is a figure somebody types in and forgets to
update, which is the only kind of progress dashboard worth having.

**The stale result is the point.** A case that passed 5/5 against a prompt that
has since been edited is not evidence about the prompt in the tree, and a green
row that quietly means "green last week" is worse than a grey one, because it is
the number you would stop checking. Every L1 result is keyed by the prompt hash
it ran against and compared to the hash now on disk; a mismatch shows as stale.
"""
from __future__ import annotations

import re
import sqlite3
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .. import paths
from ..design import graph as graph_mod
from ..llm.llm import Pins
from ..roles import prompts
from ..testkit import fixtures, obligations

CASES = paths.REPO / "tests" / "rota" / "cases"
MILESTONE = paths.PACKAGE / "MILESTONE.md"

_STAGE = re.compile(r"^##\s+(\d+\S*)\s*[·.]?\s*(.*)$")
_BOX = re.compile(r"^\s*-\s*\[( |x|X)\]\s*(?:\*\*)?([^*\n]+)")


# ---------------------------------------------------------------------------
# The milestone, from its own checkboxes
# ---------------------------------------------------------------------------

@dataclass
class Stage:
    key: str
    title: str
    done: int = 0
    total: int = 0
    open_items: list[str] = field(default_factory=list)


def milestone() -> list[dict]:
    if not MILESTONE.exists():
        return []
    stages: list[Stage] = []
    for line in MILESTONE.read_text(encoding="utf-8").splitlines():
        head = _STAGE.match(line)
        if head:
            stages.append(Stage(key=head.group(1), title=head.group(2).strip()))
            continue
        box = _BOX.match(line)
        if box and stages:
            stages[-1].total += 1
            if box.group(1).lower() == "x":
                stages[-1].done += 1
            else:
                stages[-1].open_items.append(box.group(2).strip().rstrip(".").strip())
    return [asdict(s) for s in stages if s.total]


# ---------------------------------------------------------------------------
# Coverage: what has a case at all
# ---------------------------------------------------------------------------

def _cases() -> list[dict]:
    out = []
    for path in sorted(CASES.glob("l1_*.yaml")):
        out.extend(fixtures.load_case(path) or [])
    return out


def coverage() -> dict:
    """
    Two different questions that are easy to confuse.

    *Modes* is whether every prompt piece is exercised at all — one case per
    piece, which is the unit a pass-rate drop is attributable to. *Obligations*
    is the finer grid the graph generates: every action a role can take, every
    situation, every handoff. The first is complete; the second is the long haul,
    and showing them together is the only way the first does not read as done.
    """
    cases = _cases()
    cased_modes = {(c["role"], fixtures.mode_of(c)) for c in cases}
    all_modes = {(role, mode)
                 for role in graph_mod.load().roles
                 for mode in prompts.available(role)}

    covered_actions = set()
    for case in cases:
        for table in ((case.get("expect") or {}).get("writes") or {}):
            covered_actions.add(f"{case['role']}:{table}")
        for fn in (case.get("expect") or {}).get("calls") or []:
            covered_actions.add(f"{case['role']}:{fn.split('.')[0]}")

    counts = obligations.summary()
    l1_done = sum(1 for o in obligations.l1()
                  if f"{o.role}:{o.what.split('.')[0]}" in covered_actions)

    return {
        "modes": {"done": len(cased_modes & all_modes), "total": len(all_modes),
                  "missing": sorted(f"{r}/{m}" for r, m in all_modes - cased_modes)},
        "cases": len(cases),
        "tiers": [
            {"tier": "L1", "label": "actions", "done": l1_done,
             "total": counts.get("L1", 0)},
            {"tier": "L2", "label": "situations", "done": 0,
             "total": counts.get("L2", 0)},
            {"tier": "L3", "label": "handoffs", "done": 0,
             "total": counts.get("L3", 0)},
        ],
    }


# ---------------------------------------------------------------------------
# L1 health, with staleness
# ---------------------------------------------------------------------------

def _prompt_hash(case: dict, model: str) -> str:
    """The hash the case *would* record against if it ran now."""
    instructions = prompts.compose(case["role"], fixtures.mode_of(case))
    return Pins(model=model, temperature=0.0, num_ctx=8192).with_prompt(
        instructions).prompt_hash


def l1(dev_db: Path | None = None) -> dict:
    """Latest recorded outcome per case, and whether it still means anything."""
    path = dev_db or paths.DEV_DB
    cases = {c["id"]: c for c in _cases()}
    rows: list[dict] = []

    recorded: dict[str, list] = {}
    model = ""
    if path.exists():
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        try:
            for r in conn.execute(
                "SELECT case_id, model, prompt_hash, run_no, passed, problems, seq "
                "FROM case_runs ORDER BY seq"
            ):
                recorded.setdefault(r["case_id"], []).append(dict(r))
                model = r["model"]
        except sqlite3.Error:                               # pragma: no cover
            recorded = {}
        finally:
            conn.close()

    for case_id, case in cases.items():
        runs = recorded.get(case_id, [])
        entry = {
            "id": case_id, "role": case["role"], "mode": fixtures.mode_of(case),
            "threshold": int(case.get("pass", case.get("runs", 1))),
            "runs": int(case.get("runs", 1)),
            "passed": None, "state": "never run", "problems": [],
        }
        if runs:
            latest_hash = runs[-1]["prompt_hash"]
            batch = [r for r in runs if r["prompt_hash"] == latest_hash][-entry["runs"]:]
            entry["passed"] = sum(r["passed"] for r in batch)
            entry["problems"] = sorted({
                p for r in batch for p in __import__("json").loads(r["problems"])})
            fresh = latest_hash == _prompt_hash(case, model or "llama3.1:8b")
            if not fresh:
                entry["state"] = "stale"
            elif entry["passed"] >= entry["threshold"]:
                entry["state"] = "pass"
            else:
                entry["state"] = "fail"
        rows.append(entry)

    rows.sort(key=lambda r: (r["role"], r["id"]))
    tally = {}
    for r in rows:
        tally[r["state"]] = tally.get(r["state"], 0) + 1
    return {"model": model, "cases": rows, "tally": tally}


# ---------------------------------------------------------------------------
# Onboarding readiness — the stage that was a predicate over an empty world
# ---------------------------------------------------------------------------

def onboarding(conn: sqlite3.Connection) -> dict:
    def one(sql, *args):
        row = conn.execute(sql, args).fetchone()
        return row[0] if row else 0

    try:
        indexed = one("SELECT COUNT(*) FROM code_index")
        return {
            "indexed": indexed,
            "edges": one("SELECT COUNT(*) FROM code_edges"),
            "areas": one("SELECT COUNT(DISTINCT area) FROM code_index "
                         "WHERE area IS NOT NULL"),
            "surveyed": one("SELECT COUNT(DISTINCT area) FROM survey_records"),
            "under_zero": one("SELECT COUNT(*) FROM constraint_bindings "
                              "WHERE constraint_id = 'k0'"),
        }
    except sqlite3.Error:                                   # pragma: no cover
        return {"indexed": 0, "edges": 0, "areas": 0, "surveyed": 0,
                "under_zero": 0}


def report(conn: sqlite3.Connection) -> dict:
    return {
        "milestone": milestone(),
        "coverage": coverage(),
        "l1": l1(),
        "onboarding": onboarding(conn),
    }
