"""
Frame 64's count: compose the whole cassette key for every case, cold.

For each case the script runs the case against a replay backend that records
every key it is asked for, and whether the register holds a cassette at it.
No model call. The register is read and never written.

Prints: how many cases hit on turn 1, how many miss anywhere, how many rows at
the current narrow key map to the composed turn-1 key, and how many rows of
the whole register resolve to one cassette by their first reply.
"""
import hashlib
import json
import os
import shutil
import sqlite3
import stat
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "D:/repos/rota")
os.environ.setdefault("ROTA_MODEL", "qwen3:8b")

from rota import paths                                        # noqa: E402
from rota.llm.cassettes import ReplayOnlyBackend, key_for     # noqa: E402
from rota.testkit import fixtures                             # noqa: E402
from rota.tools import casestatus                             # noqa: E402

OUT = Path(__file__).with_name("count64.jsonl")
MODEL = os.environ["ROTA_MODEL"]
reg = sqlite3.connect(str(paths.DEV_DB))
reg.row_factory = sqlite3.Row


def _sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:16]


class Capture(ReplayOnlyBackend):
    def __init__(self, conn, log):
        super().__init__(conn)
        self.log = log

    def complete(self, system, user, pins, tools=None):
        protocol = "native" if tools else "text"
        key = key_for(system, user, pins, protocol)
        hit = reg.execute("SELECT 1 FROM cassettes WHERE key = ?",
                          (key,)).fetchone() is not None
        self.log.append({"turn": len(self.log) + 1, "key": key, "hit": hit,
                         "system_len": len(system), "user_len": len(user),
                         "protocol": protocol,
                         "extras": json.dumps(pins.extras(), sort_keys=True)})
        return super().complete(system, user, pins, tools)


def _rm(path: Path) -> None:
    def onerror(fn, p, exc):
        try:
            os.chmod(p, stat.S_IWRITE)
            fn(p)
        except OSError:
            pass
    shutil.rmtree(path, onerror=onerror)


def one_case(case: dict) -> dict:
    log: list = []
    pins = casestatus.wanted_pins(case, MODEL)
    tmp = Path(tempfile.mkdtemp(prefix="count64_"))
    started = time.perf_counter()
    err = ""
    try:
        if case.get("first"):
            fixtures.run_chain(case, tmp / "case.db",
                               lambda: Capture(reg, log), pins=pins)
        else:
            fixtures.run_case(case, tmp / "case.db", Capture(reg, log),
                              pins=pins,
                              instructions=fixtures.instructions_for(case))
    except Exception as exc:                                  # noqa: BLE001
        err = f"{type(exc).__name__}: {exc}"[:200]
    finally:
        try:
            _rm(tmp)
        except OSError:
            pass
    seconds = time.perf_counter() - started

    # The rows the narrow match reads today, and whether their first reply
    # names the cassette at the composed turn-1 key.
    rows = reg.execute(
        "SELECT transcript FROM case_runs WHERE case_id = ? AND model = ? "
        "AND prompt_hash = ? ORDER BY seq DESC LIMIT 5",
        (case["id"], pins.model, pins.prompt_hash)).fetchall()
    turn1 = log[0]["key"] if log else ""
    maps = 0
    for r in rows:
        keys = first_reply_keys(pins.model, r["transcript"])
        if turn1 and turn1 in keys:
            maps += 1
    return {"id": case["id"], "chain": bool(case.get("first")),
            "repo": bool(case.get("repo")), "turns": len(log),
            "turn1_key": turn1, "turn1_hit": bool(log and log[0]["hit"]),
            "misses": sum(1 for t in log if not t["hit"]),
            "rows_narrow": len(rows), "rows_map_turn1": maps,
            "seconds": round(seconds, 2), "error": err}


INDEX: dict = defaultdict(set)


def build_index() -> None:
    for row in reg.execute("SELECT key, model, completion FROM cassettes"):
        INDEX[(row["model"], _sha(row["completion"]))].add(row["key"])


def first_reply_keys(model: str, transcript: str) -> set:
    try:
        items = json.loads(transcript or "[]")
    except ValueError:
        return set()
    for item in items:
        if isinstance(item, dict) and "say" in item:
            return INDEX.get((model, _sha(item["say"])), set())
    return set()


def register_pass() -> Counter:
    """Every row: does its first reply name one cassette, several, or none."""
    out: Counter = Counter()
    for row in reg.execute("SELECT model, transcript FROM case_runs"):
        keys = first_reply_keys(row["model"], row["transcript"])
        out["unique" if len(keys) == 1 else "several" if keys else "none"] += 1
    return out


def main() -> None:
    build_index()
    cases = casestatus._cases()
    results = []
    with OUT.open("w", encoding="utf-8") as f:
        for case in cases:
            r = one_case(case)
            results.append(r)
            f.write(json.dumps(r) + "\n")
            f.flush()
    n = len(results)
    chains = sum(1 for r in results if r["chain"])
    print(f"cases {n}: {n - chains} single, {chains} chains, "
          f"{sum(1 for r in results if r['repo'])} with repo")
    print(f"turn-1 hit: {sum(1 for r in results if r['turn1_hit'])} of {n}")
    print(f"any miss: {sum(1 for r in results if r['misses'])} of {n}; "
          f"turns total {sum(r['turns'] for r in results)}, "
          f"misses total {sum(r['misses'] for r in results)}")
    print(f"errors: {sum(1 for r in results if r['error'])}")
    for r in results:
        if r["error"] or not r["turn1_hit"]:
            print(f"  {r['id']}: turns={r['turns']} misses={r['misses']} "
                  f"hit1={r['turn1_hit']} {r['error']}")
    rn = sum(r["rows_narrow"] for r in results)
    rm = sum(r["rows_map_turn1"] for r in results)
    print(f"rows at the narrow key, last 5 per case: {rn}; "
          f"map to the composed turn-1 key: {rm}")
    print(f"cases whose every narrow row maps: "
          f"{sum(1 for r in results if r['rows_narrow'] and r['rows_map_turn1'] == r['rows_narrow'])} of "
          f"{sum(1 for r in results if r['rows_narrow'])} with rows")
    secs = [r["seconds"] for r in results]
    print(f"compose time: total {sum(secs):.1f}s, max {max(secs):.1f}s, "
          f"repo cases {sum(r['seconds'] for r in results if r['repo']):.1f}s")
    started = time.perf_counter()
    c = register_pass()
    total = sum(c.values())
    print(f"whole register, {total} rows, first reply resolves: "
          f"unique {c['unique']}, several {c['several']}, none {c['none']} "
          f"({time.perf_counter() - started:.0f}s)")


if __name__ == "__main__":
    main()
