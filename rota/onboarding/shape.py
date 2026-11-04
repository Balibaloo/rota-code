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

import ast
import json
import re
import sqlite3
from pathlib import Path

from ..core.worktrees import grain_path
from .areas import is_attached
from .harvest import entry_guard

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
        # The path half goes through the one reader (F11, frame 362 pass 1e).
        path, name = grain_path(grain), grain.partition("::")[2]
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

    Each `entry_point` row of the harvest gives its bound files, and the
    reason is the form: the pyproject line of a script target, the guard, or
    the README run line. A file named `__main__.py` comes from the index. A
    file that holds a `__main__` guard comes from the file under `root` when
    no harvest names it, and `harvest.entry_guard` decides, so the guard
    filter of section 6.1 holds for both reads."""
    out: dict[str, str] = {}
    for row in conn.execute(
            "SELECT b.path, c.text, c.detail FROM candidate_bindings b "
            "JOIN commitment_candidates c ON c.id = b.witness_id "
            "WHERE c.kind = 'entry_point' "
            # A README line names a file that a script or a guard may name
            # too, and the reason in the file is the stronger one.
            "ORDER BY c.detail LIKE '%\"readme\"%', c.line"):
        if row[0] not in paths or row[0] in out:
            continue
        form = json.loads(row[2] or "{}").get("form")
        if form == "script":
            out[row[0]] = "script: " + row[1].strip()
        elif form == "readme":
            out[row[0]] = "README run line: " + row[1].strip()
        elif form == "guard":
            out[row[0]] = "__main__ guard"
        else:
            out[row[0]] = "__main__ module"
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
        if not MAIN_GUARD.search(text):
            continue
        try:
            module = ast.parse(text)
        except (SyntaxError, ValueError):
            continue
        if entry_guard(path, module):
            out[path] = "__main__ guard"
    return out
