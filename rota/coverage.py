"""
Edge coverage: every edge in the graph must be exercised by a test.

The graph enumerates exactly what the system can do — every read, every write,
every message. So "is this system tested" has a mechanical answer: run the suite,
record which edges fired, subtract.

The property that makes this worth building rather than a nice-to-have: **a new
edge creates a new coverage obligation automatically.** Draw an edge and the
matrix grows a row that is red until something exercises it. Coverage cannot
drift from the design, because the design is what generates it.

Two mechanisms:

  * `record()` — called from the session commit path, so *any* test that runs a
    session contributes without knowing this module exists. There is nothing to
    remember to annotate.
  * `report()` — the matrix: per role, per artefact, per verb, exercised or not.

Reads are recorded from `tool_calls`, writes from `receipts`, messages from the
`messages` table. All three are already written for other reasons, so coverage is
derived from evidence rather than from a parallel bookkeeping the tests could
forget to update.
"""
from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from . import graph as graph_mod
from .db import ARTEFACT_OF_TABLE

# Written by any process running sessions; read by the coverage test. A file
# rather than a table because it spans test processes (pytest-xdist included).
COVERAGE_FILE = Path(
    os.environ.get("ROTA_COVERAGE", Path(__file__).resolve().parents[1] / ".rota-coverage.json")
)


@dataclass(frozen=True)
class EdgeKey:
    role: str
    kind: str          # reads | writes | messages
    target: str        # artefact id, or recipient role
    verb: str

    def __str__(self) -> str:
        arrow = {"reads": "<-", "writes": "->", "messages": "=>"}[self.kind]
        return f"{self.role} {arrow} {self.target} ({self.verb})"

    def as_list(self) -> list[str]:
        return [self.role, self.kind, self.target, self.verb]


def all_edges(g: graph_mod.Graph | None = None) -> set[EdgeKey]:
    """Every edge a role can exercise. `refs` are structural, not behaviour."""
    g = g or graph_mod.load()
    out: set[EdgeKey] = set()
    for e in g.edges:
        if e.type in ("reads", "writes"):
            out.add(EdgeKey(e.s, e.type, e.t, e.v))
        elif e.type == "messages" and e.s in g.roles:
            out.add(EdgeKey(e.s, "messages", e.t, e.v))
    return out


def observed_in(conn: sqlite3.Connection) -> set[EdgeKey]:
    """
    Which edges this database shows evidence of.

    Derived from tool_calls, receipts and messages — all written for other
    reasons, so a test cannot pass while forgetting to declare its coverage.
    """
    seen: set[EdgeKey] = set()

    for r in conn.execute(
        "SELECT s.role AS role, t.fn AS fn FROM tool_calls t "
        "JOIN sessions s ON s.id = t.session_id"
    ):
        fn = r["fn"]
        if "." not in fn:
            continue
        artefact, verb = fn.split(".", 1)
        if artefact == "msg":
            continue                       # messages come from the messages table
        # Verb names are python-ified in the sandbox (`set approval` ->
        # `set_approval`); map back so the key matches the graph.
        seen.add(EdgeKey(r["role"], "reads", artefact, verb.replace("_", " ")))
        seen.add(EdgeKey(r["role"], "reads", artefact, verb))
        seen.add(EdgeKey(r["role"], "writes", artefact, verb.replace("_", " ")))
        seen.add(EdgeKey(r["role"], "writes", artefact, verb))

    for r in conn.execute(
        "SELECT s.role AS role, rc.table_name AS tbl FROM receipts rc "
        "JOIN sessions s ON s.id = rc.session_id"
    ):
        artefact = ARTEFACT_OF_TABLE.get(r["tbl"])
        if artefact:
            seen.add(EdgeKey(r["role"], "writes", artefact, "*"))

    for r in conn.execute(
        "SELECT from_role, to_role, verb FROM messages WHERE from_role != 'principal'"
    ):
        seen.add(EdgeKey(r["from_role"], "messages", r["to_role"], r["verb"]))

    return seen


def record(conn: sqlite3.Connection) -> None:
    """Merge this database's evidence into the shared coverage file."""
    existing = load()
    existing |= observed_in(conn)
    save(existing)


def load() -> set[EdgeKey]:
    if not COVERAGE_FILE.exists():
        return set()
    try:
        raw = json.loads(COVERAGE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    return {EdgeKey(*row) for row in raw}


def save(keys: set[EdgeKey]) -> None:
    COVERAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    COVERAGE_FILE.write_text(
        json.dumps(sorted(k.as_list() for k in keys), indent=0), encoding="utf-8")


def reset() -> None:
    COVERAGE_FILE.unlink(missing_ok=True)


@dataclass
class Report:
    covered: set[EdgeKey] = field(default_factory=set)
    missing: set[EdgeKey] = field(default_factory=set)

    @property
    def total(self) -> int:
        return len(self.covered) + len(self.missing)

    @property
    def percent(self) -> float:
        return 100.0 * len(self.covered) / self.total if self.total else 100.0

    def by_role(self) -> dict[str, tuple[int, int]]:
        roles: dict[str, list[int]] = {}
        for key in self.covered:
            roles.setdefault(key.role, [0, 0])[0] += 1
        for key in self.missing:
            roles.setdefault(key.role, [0, 0])[1] += 1
        return {r: (c, m) for r, (c, m) in sorted(roles.items())}


def report(g: graph_mod.Graph | None = None) -> Report:
    g = g or graph_mod.load()
    seen = load()
    declared = all_edges(g)

    covered, missing = set(), set()
    for edge in declared:
        wildcard = EdgeKey(edge.role, edge.kind, edge.target, "*")
        (covered if (edge in seen or wildcard in seen) else missing).add(edge)
    return Report(covered=covered, missing=missing)


def render(rep: Report) -> str:
    lines = [
        f"edge coverage: {len(rep.covered)}/{rep.total} ({rep.percent:.0f}%)",
        "",
    ]
    for role, (c, m) in rep.by_role().items():
        bar = "#" * c + "." * m
        lines.append(f"  {role:10s} {c:3d}/{c + m:<3d} {bar}")
    if rep.missing:
        lines.append("")
        lines.append("uncovered:")
        for key in sorted(rep.missing, key=str):
            lines.append(f"  . {key}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(render(report()))
