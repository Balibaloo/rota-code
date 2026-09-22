"""
Frame 64's second count: can each register row be given its cassette key?

A row names its cassette through the replies in its transcript, the way
frame 54's migration resolved rows. This pass adds the two narrowing facts a
row carries: its model and, where it has one, its system_hash. It counts how
many rows resolve to exactly one turn-1 cassette key.
"""
import hashlib
import json
import sqlite3
import sys
import time
from collections import Counter, defaultdict

sys.path.insert(0, "D:/repos/rota")
from rota import paths                                        # noqa: E402

reg = sqlite3.connect(str(paths.DEV_DB))
reg.row_factory = sqlite3.Row


def sha16(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:16]


BY_REPLY: dict = defaultdict(set)     # (model, sha(completion)) -> keys
SYSTEM_OF: dict = {}                   # key -> system_hash
started = time.perf_counter()
for row in reg.execute("SELECT key, model, system, completion FROM cassettes"):
    BY_REPLY[(row["model"], sha16(row["completion"]))].add(row["key"])
    SYSTEM_OF[row["key"]] = sha16(row["system"])
print(f"index: {len(SYSTEM_OF)} cassettes in {time.perf_counter() - started:.0f}s")

counts: Counter = Counter()
by_state: dict = defaultdict(Counter)
started = time.perf_counter()
for row in reg.execute("SELECT model, system_hash, transcript FROM case_runs"):
    try:
        items = json.loads(row["transcript"] or "[]")
    except ValueError:
        items = []
    says = [i["say"] for i in items if isinstance(i, dict) and "say" in i]
    legacy = row["system_hash"] in ("", "unbuilt")
    if not says:
        verdict = "no reply"
    else:
        first = BY_REPLY.get((row["model"], sha16(says[0])), set())
        if not legacy:
            first = {k for k in first if SYSTEM_OF.get(k) == row["system_hash"]}
        if len(first) == 1:
            verdict = "unique by first reply"
        elif not first:
            verdict = "none"
        else:
            # Every reply of the session came from one system text, so the
            # cassettes they agree on narrow the first turn's candidates.
            agreed = None
            for say in says:
                found = BY_REPLY.get((row["model"], sha16(say)))
                if not found:
                    continue
                systems = {SYSTEM_OF[k] for k in found}
                agreed = systems if agreed is None else (agreed & systems)
            narrowed = {k for k in first if agreed and SYSTEM_OF[k] in agreed}
            verdict = ("unique by all replies" if len(narrowed) == 1
                       else "several" if narrowed else "none after narrowing")
    counts[verdict] += 1
    by_state["legacy" if legacy else "keyed"][verdict] += 1

total = sum(counts.values())
print(f"rows {total} in {time.perf_counter() - started:.0f}s")
for k, v in counts.most_common():
    print(f"  {k}: {v} ({100 * v / total:.1f}%)")
for kind, c in by_state.items():
    n = sum(c.values())
    print(f"{kind} rows {n}: " + ", ".join(f"{k} {v}" for k, v in c.most_common()))
