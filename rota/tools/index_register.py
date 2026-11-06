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
and every worker of a gate would wait on it. So the build runs where one
process holds the register: this tool, `rota cassettes pull` after it unpacks
a snapshot, and the gate before its workers start. Run the tool on a quiet
machine, with no gate and no recording pass running.

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
from ..llm.cassettes import SEQ_INDEXES, seq_index_sql, to_wal

#: What `ensure` did with one entry of `SEQ_INDEXES`.
BUILT, HELD, NO_TABLE = "built", "held", "no table"


def missing(path: str | Path) -> list[str]:
    """
    What `ensure` would do, read with no write lock: each absent index, and
    `WAL mode` when the file is in another mode. An empty list means that
    `ensure` would build nothing.

    The gate says one line before a long wait or a build, and stays silent
    when the register is ready (the review of 2c294581, frame 362).
    """
    uri = Path(path).resolve().as_uri().replace("file:///", "file:/")
    conn = sqlite3.connect(f"{uri}?mode=ro", uri=True,
                           timeout=float(REGISTER_WAIT.default))
    try:
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        held = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'index'")}
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'")}
    finally:
        conn.close()
    out = [] if mode.lower() == "wal" else ["WAL mode"]
    return out + [name for name, table in SEQ_INDEXES.items()
                  if table in tables and name not in held]


def ensure(path: str | Path) -> list[tuple[str, str, float]]:
    """
    Put the register in WAL mode, and build each missing entry of
    `SEQ_INDEXES`. Return one `(name, state, seconds)` per entry.

    The one build of the indexes. The tool, `cassette_store.pull` and the
    gate call it, each at a moment when one process holds the register. A
    gate's workers then find a WAL register with both indexes, so no worker
    switches the mode or walks the key index (frame 362).
    """
    conn = sqlite3.connect(str(path), isolation_level=None,
                           timeout=float(REGISTER_WAIT.default))
    out: list[tuple[str, str, float]] = []
    try:
        to_wal(conn)
        held = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'index'")}
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'")}
        for name, table in SEQ_INDEXES.items():
            if table not in tables:
                out.append((name, NO_TABLE, 0.0))
                continue
            if name in held:
                out.append((name, HELD, 0.0))
                continue
            one = time.perf_counter()
            conn.execute(seq_index_sql(name))
            out.append((name, BUILT, time.perf_counter() - one))
        if any(state == BUILT for _, state, _ in out):
            # `pull` deletes the side files of its part file after this
            # call, so the index pages must be in the main file first.
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        conn.close()
    return out


def prepare(path: str | Path, say=print) -> list[tuple[str, float]]:
    """`ensure`, with one line through `say` when it builds and no line when
    both indexes exist. Return each name built and its time in seconds."""
    built = [(name, seconds) for name, state, seconds in ensure(path)
             if state == BUILT]
    if built:
        say("register: built " + ", ".join(
            f"{name} in {seconds:.1f}s" for name, seconds in built))
    return built


def build(path: str | Path) -> list[tuple[str, float]]:
    """The tool's run: `ensure`, with one line per index and the total.
    Return each name built and its time in seconds."""
    started = time.perf_counter()
    built: list[tuple[str, float]] = []
    for name, state, seconds in ensure(path):
        table = SEQ_INDEXES[name]
        if state == NO_TABLE:
            print(f"no table {table}: {name} not built")
        elif state == HELD:
            print(f"already built: {name}")
        else:
            built.append((name, seconds))
            print(f"built {name} on {table} in {seconds:.1f}s")
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
