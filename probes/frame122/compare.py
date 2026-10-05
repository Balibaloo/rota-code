"""
Frame 122's comparison of two call parsers over recorded completions.

Moved on 2026-10-05 by frame 144, item 2, from the scratch area of session
419281dc (`review122c/p4b.py`). It reads every completion of a night
database (`turns.completion`) or of a cassette database
(`cassettes.completion`). It parses each completion with the parser at a git
revision and with the current one, once with the ops' signatures and once
with none. It prints each completion that the two parsers read differently.

A parser change is safe on this measure when no call that parsed before
reads differently. A call that failed before and now parses prints as E2C.

    python -m probes.frame122.compare --against fb1bdba^ .rota/clickI_night118.db
    python -m probes.frame122.compare --against HEAD~1 path/to/cassettes.db

Frame 122 read about 60,000 calls this way (copied: `plans/operating-facts.md`,
the line on `rota/llm/toolproto.py`).
"""
from __future__ import annotations

import argparse
import inspect
import sqlite3
import sys

from probes.frame122.fuzz import ROOT, parser_at


def signatures() -> dict:
    """Each op of `rota.roles.api`: (required arguments, all arguments)."""
    from rota.roles import api
    out = {}
    for (art, verb), fn in api.REGISTRY.items():
        ps = {k: v for k, v in inspect.signature(fn).parameters.items() if k != "ctx"}
        out[f"{art}.{verb}"] = ({k for k, v in ps.items()
                                 if v.default is inspect.Parameter.empty}, set(ps))
    return out


def completions(path: str) -> list[tuple[str, str]]:
    """(a label, the completion) for each recorded completion in `path`."""
    c = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "turns" in tables:
        rows = c.execute(
            "SELECT s.seq || ' ' || s.role || ' ' || t.seq, t.completion FROM turns t "
            "JOIN sessions s ON s.id = t.session_id WHERE t.completion IS NOT NULL")
    elif "cassettes" in tables:
        rows = c.execute("SELECT substr(key, 1, 12), completion FROM cassettes")
    else:
        raise SystemExit(f"{path}: no turns table and no cassettes table")
    return [(str(a), b) for a, b in rows]


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--against", required=True, help="the git revision of the old parser")
    ap.add_argument("db", nargs="+", help="a night database or a cassette database")
    a = ap.parse_args(argv)
    sys.path.insert(0, str(ROOT))
    from rota.llm import toolproto as new
    old = parser_at(a.against)
    sig = signatures()
    for path in a.db:
        rows = completions(path)
        calls = e2c = diff = 0
        for label, comp in rows:
            for s in (sig, None):
                oc = [(x.name, x.args) for x in old.extract(comp, s) if hasattr(x, "args")]
                wc = [(x.name, x.args) for x in new.extract(comp, s) if hasattr(x, "args")]
                if s is sig:
                    calls += len(oc)
                if oc == wc:
                    continue
                which = "sig" if s is sig else "nosig"
                if len(wc) > len(oc) and all(p in wc for p in oc):
                    e2c += 1
                    for p in wc:
                        if p not in oc:
                            print("E2C", which, label, p[0],
                                  {k: str(v)[:50] for k, v in p[1].items()})
                else:
                    diff += 1
                    print("DIFF", which, label, oc[:2], wc[:2])
        print(f"{path}: completions {len(rows)}, old calls {calls}, "
              f"error-to-call {e2c}, read differently {diff}")


if __name__ == "__main__":
    main()
