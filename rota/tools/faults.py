"""
The build session's discharge of a seat's fault reports.

    python -m rota.tools.faults close --db <run name or path> --call <name> --frame <n>
    python -m rota.tools.faults list --db <run name or path>

A seat that meets a door of rota that failed writes a row of `faults`
through `ledger.log(kind='fault')` or `kind='blocked'` (frame 204's design,
section 7). No page shows the row, and no seat answers it. The build
session, the meta workflow, fixes the cause in a frame. Then it closes every
open row of that refused call, and writes the frame's number in `closed_by`.

A seat never closes a fault, and the principal is never asked to. The door
writes the row, and this command writes `status` and `closed_by`, so each
column has one writer, as on `ledger`.
"""
from __future__ import annotations

import argparse
import sqlite3
import sys


def close(conn: sqlite3.Connection, call: str, frame: str) -> int:
    """Close every open fault of `call`, and return the count closed."""
    cur = conn.execute(
        "UPDATE faults SET status = 'resolved', closed_by = ? "
        "WHERE call = ? AND status = 'open'", (str(frame), call))
    return cur.rowcount


def open_counts(conn: sqlite3.Connection) -> list[tuple[str, int]]:
    """The open faults per refused call, the largest count first."""
    return [(r[0], r[1]) for r in conn.execute(
        "SELECT call, COUNT(*) AS n FROM faults WHERE status = 'open' "
        "GROUP BY call ORDER BY n DESC, call")]


def main(argv: list[str] | None = None) -> int:
    from ..cli import resolve
    from ..core.db import init_db

    ap = argparse.ArgumentParser(prog="python -m rota.tools.faults")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("close", help="close every open fault of one refused call")
    c.add_argument("--db", required=True, help="a run name or a path to a run database")
    c.add_argument("--call", required=True, help="the refused call, as `faults.call` holds it")
    c.add_argument("--frame", required=True, help="the number of the build frame that fixed it")
    ls = sub.add_parser("list", help="the open faults per refused call")
    ls.add_argument("--db", required=True, help="a run name or a path to a run database")
    args = ap.parse_args(argv)

    path = resolve(args.db)
    if not path.exists():
        print(f"no run database at {path}", file=sys.stderr)
        return 2
    conn = init_db(path)
    try:
        if args.cmd == "close":
            n = close(conn, args.call, args.frame)
            print(f"closed {n} open fault{'s' if n != 1 else ''} of {args.call} "
                  f"by frame {args.frame}")
            return 0
        rows = open_counts(conn)
        for call, n in rows:
            print(f"{call} {n}")
        if not rows:
            print("no open faults")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
