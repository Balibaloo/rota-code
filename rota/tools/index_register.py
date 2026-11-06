"""
Give an existing register the two `seq` indexes, once.

    python -m rota.tools.index_register
    python -m rota.tools.index_register --db <path>

Frame 362, 2026-11-06. Each insert into `case_runs` or `key_misses` takes its
`seq` from a `MAX(seq)` over both tables, with the write lock held. No index
started with `seq`, so the first insert of a gate read the whole key index,
81 to 195 s on a cold cache. The other xdist workers raised `database is
locked` (observed: `plans/l3r-load-reds-read-2026-11-06.md`).

`open_dev_db` gives an empty table its index and never builds on a table with
rows. A build on the 2.1 GB register holds the write lock for its whole time,
and every worker of a gate would wait on it. So one person runs this tool once,
on a quiet machine, with no gate and no recording pass running.

The tool is additive. It writes two indexes and no row, and a second run builds
nothing. `DROP INDEX` undoes it. It is not a step of `migrate_register`: that
tool rebuilds a register into a new file and never writes its source in place.
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
import time
from pathlib import Path

from .. import paths
from ..core.config import REGISTER_WAIT
from ..llm.cassettes import SEQ_INDEXES, seq_index_sql


def build(path: str | Path) -> list[tuple[str, float]]:
    """Build each missing entry of `SEQ_INDEXES`. Return each name built and
    its time in seconds. An index the register holds is not built again."""
    conn = sqlite3.connect(str(path), isolation_level=None,
                           timeout=float(REGISTER_WAIT.default))
    built: list[tuple[str, float]] = []
    started = time.perf_counter()
    try:
        held = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'index'")}
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'")}
        for name, table in SEQ_INDEXES.items():
            if table not in tables:
                print(f"no table {table}: {name} not built")
                continue
            if name in held:
                print(f"already built: {name}")
                continue
            one = time.perf_counter()
            conn.execute(seq_index_sql(name))
            seconds = time.perf_counter() - one
            built.append((name, seconds))
            print(f"built {name} on {table} in {seconds:.1f}s")
    finally:
        conn.close()
    print(f"total {time.perf_counter() - started:.1f}s, "
          f"{len(built)} of {len(SEQ_INDEXES)} indexes built")
    return built


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=str(paths.DEV_DB),
                    help="the register, by default paths.DEV_DB")
    args = ap.parse_args(argv)
    path = Path(args.db)
    # sqlite3 creates a missing file, and an empty register would then stop
    # `ensure_for_tests` from fetching the real one.
    if not path.is_file():
        raise SystemExit(f"no register at {path}")
    build(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
