"""Law 13: no date, duration or timestamp column in the schema.

The law's enforcement note promised a build check that scans the schema.
Until 2026-09-13 the only check read one table. This reads them all. The
one runtime-bookkeeping column, `runtime_processes.started_at`, is named
here because boot reaps orphans by it and the docs assert it exists.
"""
import re

from rota import paths

ALLOWED = {("runtime_processes", "started_at")}
CLOCK = re.compile(r"(_at$|^at_|date|time|stamp|duration|elapsed|seconds|_ms$)", re.I)


def test_no_table_carries_a_clock_column():
    sql = paths.SCHEMA.read_text(encoding="utf-8")
    found = []
    for m in re.finditer(r"CREATE TABLE IF NOT EXISTS (\w+)\s*\((.*?)\);", sql, re.S):
        table, body = m.group(1), m.group(2)
        for line in body.splitlines():
            line = line.split("--", 1)[0].strip()
            col = line.split()[0] if line and not line.upper().startswith(
                ("PRIMARY", "FOREIGN", "UNIQUE", "CHECK", "CONSTRAINT")) else ""
            if col and CLOCK.search(col) and (table, col) not in ALLOWED:
                found.append((table, col))
    assert not found, f"clock columns in the schema: {found}"
