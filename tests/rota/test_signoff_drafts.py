"""F32: one reader names the drafts that wake a signoff.

`scheduler.signoff_drafts` is the reader. `tick_signoff` wakes the Vision
Keeper on its list, and the submit door refuses a submit that leaves one
of them out. Before F32 the door queried `approval = 'draft'` by its own
SQL (plans/rootfix-audit-2026-10-27-b.md, F32). Law 8 holds: signoff is
per-item approval, presented as one document.
"""
from __future__ import annotations

import re
from pathlib import Path

from rota.core import scheduler
from rota.core.db import init_db

ROOT = Path(__file__).resolve().parents[2] / "rota"


def test_the_tick_wakes_on_the_signoff_drafts(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    for i, approval in (("i1", "draft"), ("i2", "approved"), ("i3", "draft")):
        conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                     "version) VALUES (?, 'x', 'in_scope', ?, 1, 1)", (i, approval))
    assert scheduler.signoff_drafts(conn) == ["i1", "i3"]
    assert [w.refs for w in scheduler.tick_signoff(conn)] == [("i1", "i3")]


def test_one_function_selects_the_draft_items():
    """No second reader queries the draft items by its own SQL."""
    allowed = {("core/scheduler.py", "signoff_drafts")}
    pattern = re.compile(r"FROM items WHERE (?:id = \? AND )?approval = 'draft'")
    found = []
    for path in sorted(ROOT.rglob("*.py")):
        rel = path.relative_to(ROOT).as_posix()
        fn = None
        for no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            head = re.match(r"(?:    )?def (\w+)", line)
            if head:
                fn = head.group(1)
            if pattern.search(line) and (rel, fn) not in allowed:
                found.append(f"{rel}:{no} {fn}")
    assert found == []
