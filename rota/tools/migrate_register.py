"""
Rebuild the register from the legacy clone, with the cassette key on every row.

    python -m rota.tools.migrate_register \\
        --source tests/rota/cassettes-legacy-2026-09-21.db \\
        --target tests/rota/cassettes-migrated.db \\
        --expect-columns 9 --expect-runs 204058 --expect-cassettes 18604

Frame 54, 2026-09-21. Roman ruled: "clone this as a backup legacy dB and
migrate over what's useful, full re-record is approved if necessary". The
ruling separates two things the register had joined. The clone keeps the record
of what the model did. The new register holds only the evidence that gates an
acceptance.

**The source is read-only and this tool never writes to it.** It opens the
source with `mode=ro`, and it writes a new file. The caller swaps the new file
in. A migration that edits the register in place cannot be undone, and the
clone is the only copy of the pre-migration evidence.

What migrates, and why:

  * **Every cassette, as it stands.** A cassette is keyed by the whole text, so
    it is already evidence about exactly one input and needs no repair.
  * **A `case_runs` row whose cassette can be identified.** The five new
    columns are then read off that cassette: the window, the temperature, the
    protocol, the extras and a hash of the cassette's own system text.
  * **`case_interviews`, whole.** 75 rows, no reader, and it is evidence about
    failed runs. Copying it keeps the new register a superset of the old one.

What does not migrate:

  * **A row with no identifiable cassette.** It stays in the clone, which is
    history. Guessing its window would write a measurement that nobody made.
  * **A chain's rows.** A chain runs two sessions and its transcript holds only
    leg two's replies, so leg one's system text cannot be identified. The
    stamped hash is both legs joined, so half of it is unknowable. Two rules
    were measured and both failed: leg one's brief as a prefix names only the
    system the tree composes today, and the recording order names the right
    cassette for 2781 of 9184 chain rows (observed: frame 54's pass 3,
    2026-09-21). A chain case is re-recorded instead.

The join is the design review's: the row's transcript completions against the
cassettes' completions, inside the row's own model. A session sends one system
text and gets several replies, so the answer is the *intersection* over the
row's replies. One reply names many candidates; several replies name one.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

from .. import paths
from ..llm.cassettes import key_for, open_dev_db, system_hash
from ..llm.llm import Pins
from ..testkit import fixtures

#: The pin sets a cassette can have been keyed under. `protocol` and the
#: optional pins are in the key's hash and in no column, so they are recovered
#: by rebuilding the key and comparing. An unresolved cassette is a hard error,
#: because a cassette whose own key cannot be rebuilt is not evidence about
#: anything the runner can ask for.
#:
#: The census, for qwen3:8b: 1697 cassettes at `{}`, 370 at `{"think": false}`
#: and 1 at `{"think": true}` (observed: frame 65's diff review, 2026-09-23).
#: Frame 65 makes `think` a value on every tier run, so the `{}` rows are the
#: ones a re-record replaces. Superseded: all 18604 cassettes in the clone
#: resolved as 18570 text with no extras and 34 text at `think=True`
#: (observed: frame 54's pass 3, 2026-09-21).
PIN_SETS = (("text", None), ("text", True), ("text", False),
            ("native", None), ("native", True), ("native", False))

#: A row about a case the tree no longer holds still migrates: it is somebody's
#: history and nothing in the tree reads it. A *gone* chain is the exception.
#: The tree can no longer say whether such a case ran one session or two, and a
#: chain's system hash is unknowable, so an id shaped like a chain's stays in
#: the clone. Ten rows, of two ids (observed: frame 54's pass 3, 2026-09-21).
GONE_CHAIN_PREFIXES = ("L3-", "G1-")


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def open_source(path: str | Path) -> sqlite3.Connection:
    """The clone, read-only for ever. SQLite refuses a write on this handle."""
    uri = Path(path).resolve().as_uri().replace("file:///", "file:/")
    conn = sqlite3.connect(f"{uri}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def shape_of(row: sqlite3.Row) -> tuple:
    """
    The five columns a migrated result takes, read off the cassette that
    earned it: the window, the temperature, the protocol, the extras and the
    hash of the whole system text.
    """
    for protocol, think in PIN_SETS:
        pins = Pins(model=row["model"], temperature=row["temperature"],
                    num_ctx=row["num_ctx"], think=think)
        if key_for(row["system"], row["user"], pins, protocol) == row["key"]:
            return (row["num_ctx"], row["temperature"], protocol,
                    json.dumps(pins.extras(), sort_keys=True),
                    system_hash(row["system"]))
    raise ValueError(f"cassette {row['key']} does not rebuild its own key")


def chain_ids() -> set[str]:
    """The cases that run two sessions. Their rows cannot carry a system hash."""
    out = set()
    for pattern in ("l*.yaml", "g*.yaml"):
        for path in sorted(paths.CASES.glob(pattern)):
            for case in fixtures.load_case(path) or []:
                if case.get("first"):
                    out.add(case["id"])
    return out


def tree_ids() -> set[str]:
    out = set()
    for pattern in ("l*.yaml", "g*.yaml"):
        for path in sorted(paths.CASES.glob(pattern)):
            out.update(c["id"] for c in (fixtures.load_case(path) or []))
    return out


def index_cassettes(src: sqlite3.Connection) -> dict:
    """`(model, sha(completion))` to the shapes a cassette with it can have."""
    index: dict = defaultdict(set)
    for row in src.execute("SELECT key, model, temperature, num_ctx, system, "
                           "user, completion FROM cassettes"):
        index[(row["model"], _sha(row["completion"]))].add(shape_of(row))
    return index


def resolve(model: str, transcript: str, index: dict) -> tuple:
    """
    The shape the row was earned under, or a reason it cannot be named.

    The intersection, not the union. A short reply such as a bare refusal is
    recorded under many system texts, so one reply rarely names one cassette.
    A session's replies all came from one system text, so the shapes they
    agree on are the shapes the session can have run under.
    """
    try:
        items = json.loads(transcript or "[]")
    except ValueError:
        items = []
    says = [i["say"] for i in items if isinstance(i, dict) and "say" in i]
    if not says:
        return None, "the row holds no model reply"
    agreed = None
    for say in says:
        found = index.get((model, _sha(say)))
        if not found:
            continue
        agreed = set(found) if agreed is None else (agreed & found)
    if agreed is None:
        return None, "no reply matches a cassette"
    if not agreed:
        return None, "the replies name no one cassette"
    if len(agreed) > 1:
        return None, "the replies name more than one cassette"
    return next(iter(agreed)), ""


def check_source(src: sqlite3.Connection, columns: int = 0, runs: int = 0,
                 cassettes: int = 0) -> tuple[int, int, int]:
    """
    Print the clone's shape, and refuse when a named expectation is missed.

    The caller names the shape it cloned. A source that has moved is a source
    something has written to, and the whole point of the clone is that nothing
    did.
    """
    have = [r["name"] for r in src.execute("PRAGMA table_info(case_runs)")]
    n_runs = src.execute("SELECT COUNT(*) n FROM case_runs").fetchone()["n"]
    n_cass = src.execute("SELECT COUNT(*) n FROM cassettes").fetchone()["n"]
    print(f"source: {len(have)} columns on case_runs, {n_runs} rows, "
          f"{n_cass} cassettes")
    for name, want, got in (("columns", columns, len(have)),
                            ("runs", runs, n_runs),
                            ("cassettes", cassettes, n_cass)):
        if want and want != got:
            raise SystemExit(f"the source is not the clone: {name} is {got}, "
                             f"and {want} was expected")
    return len(have), n_runs, n_cass


#: The tables the migration copies rather than rebuilds, with the reason.
#: `case_interviews` is what a failed run said about itself. `key_misses` is
#: a look that measured nothing, and it has no cassette to rebuild from, so a
#: target without it reads "nobody has looked" for a case whose last look
#: missed the key (frame 64's diff review, 2026-09-22).
CARRIED = ("case_interviews", "key_misses")


def copy_table(src: sqlite3.Connection, dst: sqlite3.Connection,
               name: str) -> int:
    """
    One table, whole and unchanged, when the source holds it.

    Neither carried table has a cassette key to repair, and dropping one would
    lose evidence for nothing, so the new register stays a superset of the old
    one. The columns are named from the source rather than left to their
    order, so a source written under an older shape still lands.

    `name` comes from `CARRIED` and never from a caller's input.
    """
    ddl = src.execute("SELECT sql FROM sqlite_master WHERE type = 'table' "
                      "AND name = ?", (name,)).fetchone()
    if not ddl:
        return 0
    dst.executescript(ddl["sql"].replace("CREATE TABLE",
                                         "CREATE TABLE IF NOT EXISTS", 1))
    columns = [r["name"] for r in src.execute(f"PRAGMA table_info({name})")]
    listed = ", ".join(columns)
    rows = [tuple(r) for r in src.execute(f"SELECT {listed} FROM {name}")]
    if rows:
        marks = ",".join("?" * len(columns))
        dst.executemany(f"INSERT OR REPLACE INTO {name} ({listed}) "
                        f"VALUES ({marks})", rows)
    print(f"{name} copied: {len(rows)} rows")
    return len(rows)


def check_target(target: Path, force: bool = False) -> None:
    """
    Refuse a target that already holds results, unless the caller insists.

    The tool writes with `INSERT OR REPLACE`, which is what makes a second run
    over the same target a no-op rather than a failure. It also means a target
    named by mistake is written into rather than refused, and the register is
    780 MB of evidence with no copy but the clone. `--force` is the word that
    says the caller meant this file.
    """
    if not target.exists():
        return
    conn = sqlite3.connect(str(target))
    try:
        held = conn.execute("SELECT COUNT(*) FROM case_runs").fetchone()[0]
    except sqlite3.Error:
        held = 0                       # not a register, so nothing to lose
    finally:
        conn.close()
    if held and not force:
        raise SystemExit(
            f"{target} already holds {held} results. Name a target that does "
            f"not exist, or pass --force to write into this one.")


def migrate(src: sqlite3.Connection, target: Path, *, dry_run: bool = False,
            batch: int = 2000) -> dict:
    """Write the new register. Returns the numbers the closing status needs."""
    skip = chain_ids()
    known = tree_ids()
    dst = None
    if not dry_run:
        dst = open_dev_db(target)

    started = time.perf_counter()
    index = index_cassettes(src)
    print(f"cassettes indexed: {len(index)} distinct replies in "
          f"{time.perf_counter() - started:.1f}s")

    if dst is not None:
        # Verbatim. Every cassette is evidence about exactly one input.
        # `INSERT OR REPLACE` on the primary key is what makes a second run of
        # this tool a no-op rather than a failure.
        # The insert names the source's columns. A source from before frame
        # 233 holds no `done_reason`, and the target's default fills it.
        cols = [r[1] for r in src.execute("PRAGMA table_info(cassettes)")]
        insert = (f"INSERT OR REPLACE INTO cassettes ({', '.join(cols)}) "
                  f"VALUES ({', '.join('?' * len(cols))})")
        dst.execute("BEGIN")
        rows = []
        for row in src.execute(f"SELECT {', '.join(cols)} FROM cassettes"):
            rows.append(tuple(row))
            if len(rows) >= batch:
                dst.executemany(insert, rows)
                rows = []
        if rows:
            dst.executemany(insert, rows)
        dst.execute("COMMIT")
        for carried in CARRIED:
            copy_table(src, dst, carried)

    tally: Counter = Counter()
    per_case: dict = defaultdict(Counter)
    pending: list = []
    # `live` and `at` are left at their defaults, 0 and '' (frame 66,
    # 2026-09-23). An old row is a run of unknown provenance, and 0 says so.
    insert = ("INSERT OR REPLACE INTO case_runs (case_id, model, prompt_hash, "
              "run_no, load_id, passed, problems, transcript, seq, num_ctx, "
              "temperature, protocol, extras, system_hash) "
              "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)")
    if dst is not None:
        dst.execute("BEGIN")
    for row in src.execute("SELECT case_id, model, prompt_hash, run_no, "
                           "load_id, passed, problems, transcript, seq "
                           "FROM case_runs"):
        tally["rows"] += 1
        case_id = row["case_id"]
        gone_chain = (case_id not in known
                      and case_id.startswith(GONE_CHAIN_PREFIXES))
        if case_id in skip or gone_chain:
            tally["left: a chain runs two sessions"] += 1
            per_case[case_id]["left"] += 1
            continue
        shape, why = resolve(row["model"], row["transcript"], index)
        if shape is None:
            tally[f"left: {why}"] += 1
            per_case[case_id]["left"] += 1
            continue
        tally["migrated"] += 1
        per_case[case_id]["migrated"] += 1
        if dst is not None:
            pending.append((case_id, row["model"], row["prompt_hash"],
                            row["run_no"], row["load_id"], row["passed"],
                            row["problems"], row["transcript"], row["seq"],
                            *shape))
            if len(pending) >= batch:
                dst.executemany(insert, pending)
                pending = []
    if dst is not None:
        if pending:
            dst.executemany(insert, pending)
        dst.execute("COMMIT")
        dst.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        dst.close()
    return {"tally": tally, "per_case": per_case}


def report(result: dict, model: str = "") -> None:
    tally, per_case = result["tally"], result["per_case"]
    rows, kept = tally["rows"], tally["migrated"]
    print()
    print(f"rows migrated   : {kept}")
    print(f"rows left behind: {rows - kept}")
    print(f"migrated        : {100.0 * kept / rows:.1f}% of {rows}")
    for reason, n in sorted(tally.items()):
        if reason.startswith("left: "):
            print(f"  {reason[6:]:<40} {n}")

    # Which cases now hold fewer runs than their threshold. The threshold is
    # the case's own `pass`, and the count here is every row that survived,
    # before the report narrows it to one model and one key. A case short here
    # is short under every key, so this is the floor and not the answer.
    short = []
    for pattern in ("l*.yaml", "g*.yaml"):
        for path in sorted(paths.CASES.glob(pattern)):
            for case in fixtures.load_case(path) or []:
                kept_here = per_case[case["id"]]["migrated"]
                if kept_here < int(case.get("pass", 3)):
                    short.append((case["id"], kept_here,
                                  int(case.get("pass", 3))))
    print()
    print(f"cases below their threshold after the migration: {len(short)}")
    for case_id, have, need in sorted(short):
        print(f"  {case_id:<56} {have} of {need}")
    if model:
        print()
        print("read the register's own report with")
        print(f"  ROTA_DEV_DB=<target> python -m rota.tools.casestatus "
              f"--model {model}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True,
                    help="the legacy clone, opened read-only")
    ap.add_argument("--target", required=True,
                    help="the new register, created if it is absent")
    ap.add_argument("--dry-run", action="store_true",
                    help="measure the join and write nothing")
    ap.add_argument("--expect-columns", type=int, default=0)
    ap.add_argument("--expect-runs", type=int, default=0)
    ap.add_argument("--expect-cassettes", type=int, default=0)
    ap.add_argument("--force", action="store_true",
                    help="write into a target that already holds results")
    ap.add_argument("--model", default="qwen3:8b",
                    help="named in the closing advice, never read here")
    args = ap.parse_args(argv)

    source = Path(args.source)
    target = Path(args.target)
    if source.resolve() == target.resolve():
        raise SystemExit("the source is read-only: name a different target")
    if not args.dry_run:
        check_target(target, args.force)
    src = open_source(source)
    check_source(src, args.expect_columns, args.expect_runs,
                 args.expect_cassettes)
    started = time.perf_counter()
    result = migrate(src, target, dry_run=args.dry_run)
    src.close()
    report(result, model=args.model)
    print()
    print(f"{'measured' if args.dry_run else 'written'} in "
          f"{time.perf_counter() - started:.1f}s"
          + ("" if args.dry_run else f" to {target}"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
