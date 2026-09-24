"""
Write the frame 83 fixtures from the night copies in `.rota`.

    python tests/rota/fixtures/extract_night.py

Night 92 repeated one Developer session nineteen times and night 91 a round
of ten (observed: nights 91 and 92, 2026-09-24). The pins of
`test_cycles.py` and `test_next_batch.py` read the rows of those nights.
The suite reads the JSON files and never runs this script.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent

SESSION_COLUMNS = ("id", "role", "trigger_msg", "wake_kind", "wake_detail",
                   "wake_refs", "committed", "seq")
# The batch's own state at the stop, for the scheduler pins. Night 92 only.
STATE_TABLES = ("items", "batches", "batch_dep_facts", "tests", "test_runs",
                "tick_attempts")


def _rows(conn: sqlite3.Connection, sql: str) -> list[dict]:
    return [dict(r) for r in conn.execute(sql)]


def extract(night: int, state: bool) -> dict:
    src = REPO / ".rota" / f"clickI_night{night}.db"
    conn = sqlite3.connect(f"file:{src.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    out = {
        "sessions": _rows(conn, f"SELECT {', '.join(SESSION_COLUMNS)} FROM sessions "
                                "ORDER BY seq"),
        "receipts": _rows(conn, "SELECT session_id, table_name, row_id, new_version "
                                "FROM receipts ORDER BY rowid"),
        "messages": _rows(conn, "SELECT id, verb FROM messages ORDER BY rowid"),
    }
    if state:
        for table in STATE_TABLES:
            cols = "*"
            if table == "tests":
                # The body is not read by any pin, and it is most of the bytes.
                cols = "id, batch_id, criterion_id, path, '' AS body, version"
            if table == "test_runs":
                cols = "id, batch_id, test_id, commit_sha, result, '' AS output, attempt"
            out[table] = _rows(conn, f"SELECT {cols} FROM {table} ORDER BY rowid")
    conn.close()
    return out


def load(night: int) -> sqlite3.Connection:
    """The night's rows in a fresh in-memory database with the current schema."""
    from rota.core.db import init_db

    data = json.loads((HERE / f"night{night}_cycle.json").read_text(encoding="utf-8"))
    conn = init_db(":memory:")
    # The fixture holds a slice of the night, so a row may name one it omits.
    conn.execute("PRAGMA foreign_keys = OFF")
    # A message row carries its verb only. The schema's other required
    # columns get a filler that no pin reads.
    filler = {"messages": {"thread_id": "t", "from_role": "-", "to_role": "-", "seq": 0}}
    for table, rows in data.items():
        for row in rows:
            row = {**filler.get(table, {}), **row}
            cols = ", ".join(row)
            marks = ", ".join("?" for _ in row)
            conn.execute(f"INSERT INTO {table} ({cols}) VALUES ({marks})",
                         tuple(row.values()))
    conn.commit()
    return conn


def main() -> None:
    for night, state in ((92, True), (91, False)):
        path = HERE / f"night{night}_cycle.json"
        text = json.dumps(extract(night, state), indent=0, sort_keys=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
        print(path, path.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
