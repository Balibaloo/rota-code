"""
`rota/AUDIT.md` is checked: every item names where it happens, and the
place exists. A row whose file is gone is a row about nothing.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "rota"


def test_every_audit_item_names_a_place_that_exists():
    text = (ROOT / "AUDIT.md").read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if re.match(r"\|\s*\d+\s*\|", line)]
    assert len(rows) >= 9
    for row in rows:
        cells = [c.strip() for c in row.strip("|").split("|")]
        where = cells[2]
        paths = re.findall(r"`([a-z_/]+\.py)`", where)
        assert paths, f"row {cells[0]} names no file: {where!r}"
        for p in paths:
            assert (ROOT / p).exists(), f"row {cells[0]}: {p} does not exist"


def test_the_two_doors_the_audit_landed_exist():
    from rota.core import fence, worktrees

    assert callable(fence.check_manifest)
    assert "core.hooksPath=" in " ".join(worktrees.GIT)
