"""
Onboarding, from a checkout to a schedulable world.

One entry point, shared by the CLI and by every test that needs an onboarded
database. The steps are separable and each is a pure function of the one before,
so a re-run on a later commit produces the same answer without remembering that
it ran — which is the same property the frontier has, for the same reason.

    index      what exists, and what depends on what        (mechanical)
    partition  areas, from directories, checked by the graph (mechanical)
    zero       one constraint over everything unsurveyed     (mechanical)
    survey     what any of it means                          (sessions)

Constraint zero is the piece that makes the last step honest. Before a codebase
has been looked at, the true statement about it is "this may be committed to
things nobody here knows about" — so onboarding writes exactly that, bound to
every area, and every completed survey shrinks its binding by one area. It is
never removed by judgement and no role can write it: an area stops being covered
by it when somebody has looked, and only then.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from . import areas as areas_mod
from . import indexer

ZERO = "k0"

ZERO_HEADLINE = "this area has not been surveyed"

ZERO_TEXT = (
    "Nobody has read this area yet, so what it is committed to is unknown. "
    "Treat a change here as touching commitments that have not been written "
    "down: it is not a prohibition, it is the absence of the information that "
    "would let anyone say. Surveying the area removes it from this constraint, "
    "including a survey that finds nothing — that is a result."
)


@dataclass
class OnboardReport:
    index: indexer.IndexReport
    areas: int
    unsurveyed: int
    leaky: list


def onboard(conn: sqlite3.Connection, root: str | Path) -> OnboardReport:
    """Index, partition, and put everything under constraint zero."""
    report = indexer.build(conn, root)
    proposal = areas_mod.propose(conn)
    count = areas_mod.pin(conn, proposal)
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
                 "('project_root', ?)", (str(Path(root)),))
    unsurveyed = refresh_constraint_zero(conn)
    return OnboardReport(index=report, areas=count, unsurveyed=unsurveyed,
                         leaky=proposal.leaky())


def refresh_constraint_zero(conn: sqlite3.Connection) -> int:
    """
    Bind constraint zero to exactly the areas nobody has surveyed.

    Derived, never accumulated. The bindings are recomputed from the surveys
    that exist rather than deleted one at a time as they arrive, so a survey
    that is rolled back with its session takes its shrinkage with it — the
    binding cannot drift from the evidence, because it is a function of it.
    """
    conn.execute(
        "INSERT OR IGNORE INTO constraints (id, headline, text, provenance, "
        "is_global) VALUES (?, ?, ?, 'observed', 0)",
        (ZERO, ZERO_HEADLINE, ZERO_TEXT))

    surveyed = {r["area"] for r in conn.execute(
        "SELECT DISTINCT area FROM survey_records")}
    remaining = [r["area"] for r in conn.execute(
        "SELECT DISTINCT area FROM code_index WHERE area IS NOT NULL ORDER BY area")
        if r["area"] not in surveyed]

    conn.execute("DELETE FROM constraint_bindings WHERE constraint_id = ?", (ZERO,))
    conn.executemany(
        "INSERT INTO constraint_bindings (constraint_id, grain, grain_kind) "
        "VALUES (?, ?, 'path')", [(ZERO, area) for area in remaining])
    return len(remaining)


def is_onboarded(conn: sqlite3.Connection) -> bool:
    return bool(conn.execute(
        "SELECT 1 FROM code_index LIMIT 1").fetchone())
