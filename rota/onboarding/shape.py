"""
The shape facts that a query reads from the index, with no model.

Frame 362, the shape design, `plans/design-onboarding-shape-2026-11-04.md`.
Section 3.1 holds copies of one function in `code_index`, so a copy needs no
new record: the query here reads it. Section 3.5 names the readers: the
Architect's guess through `code.callables` now, and the shape push and
`model.shape` later. This module writes nothing. The indexer and the harvest
stay the writers of the tables it reads (law 1).
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from .areas import is_attached

# A `__main__` guard as Python writes it, at the start of a line.
MAIN_GUARD = re.compile(r"""^if\s+__name__\s*==\s*['"]__main__['"]""", re.M)


def copies(conn: sqlite3.Connection) -> dict[str, list[str]]:
    """Each name that two or more files of the project define at the top
    level, to the sorted paths of those files.

    The rule of section 3.1. Tests, examples and dot directories stay out, by
    `areas.is_attached`. Dunder names stay out, because a module
    `__getattr__` shim is not a copy. Methods stay out, because the index
    holds no method, and method pairs were 0 of 10 true on icalendar."""
    by: dict[str, set[str]] = {}
    for (grain,) in conn.execute(
            "SELECT grain FROM code_index WHERE grain_kind = 'symbol'"):
        path, _, name = grain.partition("::")
        if not name or is_attached(path):
            continue
        if name.startswith("__") and name.endswith("__"):
            continue
        by.setdefault(name, set()).add(path)
    return {name: sorted(paths) for name, paths in sorted(by.items())
            if len(paths) > 1}


def entry_points(conn: sqlite3.Connection, root: str | Path | None,
                 paths: set[str]) -> dict[str, str]:
    """Of `paths`, each file that a program run starts in, to the reason.

    A `[project.scripts]` target comes from the harvest's candidate where one
    exists, and the reason is the pyproject line. A file named `__main__.py`
    comes from the index. A file that holds a `__main__` guard comes from the
    file under `root`, because the index holds no guard."""
    out: dict[str, str] = {}
    for row in conn.execute(
            "SELECT b.path, c.text FROM candidate_bindings b "
            "JOIN commitment_candidates c ON c.id = b.witness_id "
            "WHERE b.rule = 'entry_point' ORDER BY c.line"):
        if row[0] in paths and row[0] not in out:
            out[row[0]] = "script: " + row[1].strip()
    base = Path(root) if root else None
    for path in sorted(paths - set(out)):
        if path.rsplit("/", 1)[-1] == "__main__.py":
            out[path] = "__main__ module"
            continue
        if base is None or not path.endswith(".py"):
            continue
        try:
            text = (base / path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if MAIN_GUARD.search(text):
            out[path] = "__main__ guard"
    return out
