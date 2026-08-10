"""
Partitioning a checkout into areas.

An area is the unit onboarding is scheduled in: one survey session per role per
area, in role order. So the partition decides how much a single session has to
hold, and getting it wrong is expensive in both directions — too coarse and a
session is asked to characterise a third of the codebase from one context window;
too fine and the same term gets surveyed eleven times by eleven sessions that
cannot see each other's answers.

**Directories, checked against the dependency graph.** Not clustering. A
directory layout is a partition somebody already chose, usually for the right
reasons, and inventing a different one from import counts would mean every later
area-scoped decision is filed somewhere nobody would look. What the graph is for
is *checking* it: an area that imports another twice as often as it imports
itself is not an area, and that is worth saying out loud rather than quietly
repairing.

The `area` column is pinned by decision, so this proposes and something else
commits. `propose()` is a pure function of the index; `pin()` is the write.
"""
from __future__ import annotations

import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass, field

# Below this, a directory is not worth a survey session of its own and folds
# into its parent. Three files is roughly where a session stops being mostly
# preamble.
MIN_FILES = 3


@dataclass
class Proposal:
    areas: dict[str, str] = field(default_factory=dict)      # grain -> area
    sizes: Counter = field(default_factory=Counter)
    internal: Counter = field(default_factory=Counter)       # area -> edges within
    crossing: Counter = field(default_factory=Counter)       # (a, b) -> edges

    def leaky(self) -> list[tuple[str, str, int, int]]:
        """
        Areas coupled more tightly to another area than to themselves.

        Not an error and not repaired here. It is the one fact about a proposed
        partition that a person should see before pinning it, because it is the
        shape of "these two directories are one thing wearing two names".
        """
        out = []
        for (src, dst), n in self.crossing.items():
            if n > self.internal.get(src, 0):
                out.append((src, dst, n, self.internal.get(src, 0)))
        return sorted(out, key=lambda r: -r[2])


def _directory(grain: str) -> str:
    parts = grain.split("/")
    return "/".join(parts[:-1]) if len(parts) > 1 else ""


def _parent(area: str) -> str:
    return area.rsplit("/", 1)[0] if "/" in area else ""


def propose(conn: sqlite3.Connection) -> Proposal:
    """Group the index by directory, fold the small ones up, and measure."""
    paths = [r["grain"] for r in conn.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'path' ORDER BY grain")]
    if not paths:
        return Proposal()

    assigned = {p: _directory(p) or "." for p in paths}

    # Fold upward until nothing is under the floor. A directory with two files
    # beside a sibling with forty is not a peer of it; it is part of whatever
    # contains them both.
    while True:
        sizes = Counter(assigned.values())
        small = [a for a, n in sizes.items()
                 if n < MIN_FILES and _parent(a) or (n < MIN_FILES and a != ".")]
        if not small:
            break
        moved = False
        for area in small:
            target = _parent(area) or "."
            if target == area:
                continue
            for grain, a in assigned.items():
                if a == area:
                    assigned[grain] = target
                    moved = True
        if not moved:
            break

    prop = Proposal(areas=assigned, sizes=Counter(assigned.values()))
    for row in conn.execute("SELECT src, dst FROM code_edges"):
        a, b = assigned.get(row["src"]), assigned.get(row["dst"])
        if a is None or b is None:
            continue
        if a == b:
            prop.internal[a] += 1
        else:
            prop.crossing[(a, b)] += 1
    return prop


def pin(conn: sqlite3.Connection, proposal: Proposal) -> int:
    """
    Write the partition onto the index.

    Separate from `propose` because the assignment is a decision — onboarding
    schedules itself off this column, so a partition that changes underneath a
    half-finished survey would strand the areas already done.
    """
    for grain, area in proposal.areas.items():
        conn.execute("UPDATE code_index SET area = ? WHERE grain = ?", (area, grain))
    # Symbols inherit their file's area, so `code.survey` returns a definition
    # beside the file it is defined in rather than in an area of its own.
    by_path = defaultdict(str, proposal.areas)
    for row in conn.execute(
            "SELECT grain FROM code_index WHERE grain_kind = 'symbol'").fetchall():
        path = row["grain"].split("::", 1)[0]
        if path in by_path:
            conn.execute("UPDATE code_index SET area = ? WHERE grain = ?",
                         (by_path[path], row["grain"]))
    return len(set(proposal.areas.values()))
