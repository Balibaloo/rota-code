"""
The benchmarks table: what measurement says about each model, per
capability, written once from the record and shipped. plans/model-setup.md,
step 5. Users never run benchmarks; `recommend` reads this table.

Sources, all on record:

- the register, `case_runs`: per role, the share of cases a model passes on
  its latest prompt;
- the walks, `tests/rota/walks.jsonl`: per profile, whether the walk merged,
  credited to every model the profile names;
- the provider tool check, the `T0-PROVIDER` rows: the transport works.

A capability is a role today. Step 7 derives groups from the graph and the
same rows fold into them. A model with no row for a capability is not
ranked, and the screen says "no benchmark on record".
"""
from __future__ import annotations

import datetime
import json
import sqlite3
from collections import defaultdict
from pathlib import Path

from .. import paths

SHIPPED = paths.PACKAGE / "llm" / "benchmarks.json"


def from_register(conn: sqlite3.Connection) -> list[dict]:
    """Per (model, role): passed cases over cases recorded, on each case's
    latest prompt for that model."""
    rows = conn.execute(
        "SELECT case_id, model, prompt_hash, seq, passed FROM case_runs "
        "WHERE case_id NOT LIKE 'T0-PROVIDER-%'").fetchall()
    latest: dict[tuple[str, str], tuple[int, str]] = {}
    for cid, model, ph, seq, _p in rows:
        key = (cid, model)
        if key not in latest or seq > latest[key][0]:
            latest[key] = (seq, ph)
    tally: dict[tuple[str, str], list[int]] = defaultdict(lambda: [0, 0])
    per_case: dict[tuple[str, str], list[int]] = defaultdict(lambda: [0, 0])
    for cid, model, ph, seq, passed in rows:
        if latest[(cid, model)][1] != ph:
            continue
        per_case[(cid, model)][0] += int(passed)
        per_case[(cid, model)][1] += 1
    for (cid, model), (ok, n) in per_case.items():
        role = cid.split("-")[1] if cid.startswith(("L1-", "L2-")) else "chain"
        threshold = max(3, int(n * 0.6)) if n >= 3 else n
        tally[(model, role)][0] += int(ok >= threshold)
        tally[(model, role)][1] += 1
    today = datetime.date.today().isoformat()
    return [{"model": m, "capability": role, "score": round(ok / n, 3), "cases": n,
             "source": "register", "recorded_on": today}
            for (m, role), (ok, n) in sorted(tally.items()) if n]


def from_tool_check(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT case_id, model, passed FROM case_runs WHERE case_id LIKE 'T0-PROVIDER-%' "
        "ORDER BY seq").fetchall()
    last: dict[tuple[str, str], int] = {}
    for cid, model, passed in rows:
        kind = "tool-line" if cid.endswith("-tool-line") else "native-call"
        last[(model, kind)] = int(passed)
    today = datetime.date.today().isoformat()
    return [{"model": m, "capability": f"transport:{kind}", "score": float(v),
             "cases": 1, "source": "toolcheck", "recorded_on": today}
            for (m, kind), v in sorted(last.items())]


def from_walks(path: Path, profiles: dict[str, list[str]]) -> list[dict]:
    """Per model: the share of walks that merged on a profile naming it."""
    if not path.is_file():
        return []
    tally: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        for model in profiles.get(row.get("profile", ""), []):
            tally[model][0] += int(row.get("merged") or 0)
            tally[model][1] += 1
    today = datetime.date.today().isoformat()
    return [{"model": m, "capability": "walk:merge", "score": round(ok / n, 3), "cases": n,
             "source": "walks", "recorded_on": today} for m, (ok, n) in sorted(tally.items()) if n]


def profile_models() -> dict[str, list[str]]:
    from . import profile as profile_mod
    out: dict[str, list[str]] = {}
    for name, _src in profile_mod.available(None):
        try:
            p = profile_mod.find(name)
        except Exception:
            continue
        out[name] = sorted({p.default_model, *p.roles.values()})
    return out


def build(dev_db: Path | None = None, walks: Path | None = None) -> list[dict]:
    from . import cassettes
    conn = cassettes.open_dev_db(dev_db or paths.DEV_DB)
    try:
        rows = from_register(conn) + from_tool_check(conn)
    finally:
        conn.close()
    rows += from_walks(walks or (paths.REPO / "tests" / "rota" / "walks.jsonl"), profile_models())
    return rows


def write(rows: list[dict], path: Path = SHIPPED) -> Path:
    path.write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
    return path


def load(path: Path = SHIPPED) -> list[dict]:
    if not path.is_file():
        return []
    return json.loads(path.read_text(encoding="utf-8"))
