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


# Directory names and filename shapes that mean "this is a test". Tests are
# indexed -- a role asked to say what the code *does* should not be blind to the
# suite that pins it, and for a repo whose spec conformance lives in its tests
# that is most of the evidence there is -- but they never form an area of their
# own. Measured on icalendar before this existed: six of fourteen proposed areas
# were `tests/*`, and `tests` alone was the largest area in the repository.
TEST_DIRS = {"test", "tests", "testing", "spec", "specs", "__tests__"}
TEST_FILE_PREFIXES = ("test_", "conftest")
TEST_FILE_INFIXES = ("_test.", ".test.", ".spec.", "_spec.")


def is_test(grain: str) -> bool:
    """
    A path is a test if a directory component says so, or the filename does.

    Deliberately not `"test" in path`: that catches `latest.py` and
    `contest/manifest.go`, and a source file misfiled as a test is invisible to
    the partition that decides what gets surveyed at all.
    """
    parts = grain.split("/")
    if any(p.lower() in TEST_DIRS for p in parts[:-1]):
        return True
    name = parts[-1].lower()
    return (name.startswith(TEST_FILE_PREFIXES)
            or any(i in name for i in TEST_FILE_INFIXES))


def _untest(directory: str) -> str:
    """The directory with its test components removed: `tests/prop` -> `prop`."""
    return "/".join(p for p in directory.split("/")
                    if p and p.lower() not in TEST_DIRS)


@dataclass
class Proposal:
    areas: dict[str, str] = field(default_factory=dict)      # grain -> area
    sizes: Counter = field(default_factory=Counter)
    internal: Counter = field(default_factory=Counter)       # area -> edges within
    crossing: Counter = field(default_factory=Counter)       # (a, b) -> edges
    tests: Counter = field(default_factory=Counter)          # area -> tests attached

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
    """
    Group the index by directory, fold the small ones up, and measure.

    Only source decides the partition. Tests are attached to it afterwards by
    `_attach_tests`, so they are findable from the area they exercise without
    ever creating one, inflating one, or being counted when deciding what is too
    small to survey alone.
    """
    every = [r["grain"] for r in conn.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'path' ORDER BY grain")]
    if not every:
        return Proposal()

    paths = [p for p in every if not is_test(p)]
    tests = [p for p in every if is_test(p)]
    if not paths:                      # a repository of nothing but tests
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

    prop = Proposal(areas=dict(assigned), sizes=Counter(assigned.values()))
    _attach_tests(prop, tests, set(assigned.values()))

    # Source edges only. A test importing the thing it tests is not evidence
    # about how the source is coupled, and counting it would make every area
    # look tightly bound to wherever its tests landed.
    for row in conn.execute("SELECT src, dst FROM code_edges"):
        if is_test(row["src"]) or is_test(row["dst"]):
            continue
        a, b = assigned.get(row["src"]), assigned.get(row["dst"])
        if a is None or b is None:
            continue
        if a == b:
            prop.internal[a] += 1
        else:
            prop.crossing[(a, b)] += 1
    return prop


def _attach_tests(prop: Proposal, tests: list[str], areas: set[str]) -> None:
    """
    Put each test with the area it exercises.

    `tests/prop/test_recur.py` belongs with `prop`, which is what a person would
    expect and what makes "survey this area" return the code *and* the suite that
    pins it. Where stripping the test components names no real area --
    `tests/rfc_7265_jcal` against a repo with no `rfc_7265_jcal` directory -- walk
    up until something exists, and land at the root if nothing does.
    """
    for grain in tests:
        target = _untest(_directory(grain))
        while target and target not in areas:
            target = _parent(target)
        area = target if target in areas else "."
        prop.areas[grain] = area
        prop.tests[area] += 1


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
