"""
Invariants over the world, not the write.

    python -m rota.tools.audit            # every run in the runs directory
    python -m rota.tools.audit NAME       # one run

The guards check transitions -- this call, this row, refused or landed. A
bug that only shows with extended use lives in what *accumulates*: a ref
that pointed at a row a later session superseded, twin rows written before
their guard existed, a state two writers left half-agreed. No transition
check can see those, because every individual write looked fine.

So the laws run here as propositions over any database, read-only, any time
-- including the 58 historical runs, which are the extended-use corpus the
worry is about. A finding in an old run is not an alarm; it is the system's
own history showing which invariant was worth writing down.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

# id-bearing tables, harvested once per db; every JSON ref column is checked
# against the union, because a ref is a promise that a row exists somewhere.
# Labels older composers wrote into body_refs before their fixes: the
# quarantine report used to name the mechanism ('tick.quarantined',
# 'work_stalled') and the observed-entries present used to name categories
# ('observed_terms'). Both composers carry real artefact ids now -- the wake
# carries the payload, not the envelope -- so these are declared as history,
# not exempted as acceptable: a NEW label joining this set is a regression
# and must argue its case here.
LEGACY_LABELS = {
    "tick.quarantined", "work_stalled", "observed_terms",
    "observed_constraints", "observed_behaviours", "scope_term",
    "constraints",
}

REF_COLUMNS = [
    ("messages", "body_refs"),
    ("criteria", "term_refs"),
    ("criteria", "surface_refs"),
    ("statements", "span_entry"),
    ("ledger", "about_ref"),
]


def _ids(conn: sqlite3.Connection) -> set[str]:
    out: set[str] = set()
    tables = [r["name"] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")]
    for t in tables:
        cols = {r["name"] for r in conn.execute(f"PRAGMA table_info({t})")}
        if "id" in cols:
            out.update(r["id"] for r in conn.execute(f"SELECT id FROM {t}"))
        if t == "code_index":
            out.update(r["grain"] for r in conn.execute(
                "SELECT grain FROM code_index"))
        if t == "glossary_terms" and "term" in cols:
            out.update(r["term"] for r in conn.execute(
                "SELECT term FROM glossary_terms"))
    return out


def _rows(conn, sql, args=()):
    try:
        return conn.execute(sql, args).fetchall()
    except sqlite3.OperationalError:
        return []          # a run from before the column existed


def audit(conn: sqlite3.Connection) -> list[str]:
    """Every violated invariant, one line each. Empty is the claim."""
    findings: list[str] = []
    ids = _ids(conn)

    # 1. Every ref resolves. The one FKs cannot see: refs travel as JSON.
    for table, col in REF_COLUMNS:
        for r in _rows(conn, f"SELECT rowid, {col} AS v FROM {table} "
                             f"WHERE {col} IS NOT NULL AND {col} != ''"):
            raw = r["v"]
            try:
                refs = json.loads(raw) if raw.startswith("[") else [raw]
            except (json.JSONDecodeError, AttributeError):
                findings.append(f"{table}.{col} rowid {r['rowid']}: not JSON")
                continue
            for ref in refs:
                if not isinstance(ref, str):
                    findings.append(
                        f"{table}.{col} rowid {r['rowid']}: non-string ref "
                        f"{ref!r}")
                elif ref in LEGACY_LABELS:
                    continue      # the before-photo of a fixed composer
                elif ref not in ids and not ref.startswith(("@", "e_")):
                    findings.append(
                        f"{table}.{col} rowid {r['rowid']}: dangling {ref!r}")

    # 2. The identity invariants, as world-states. The guards enforce these
    #    at the door now; rows from before a guard existed are exactly the
    #    latent kind of bug this audit exists to surface.
    for r in _rows(conn, "SELECT ticket_id, lower(trim(text)) AS words, "
                         "COUNT(*) AS n FROM criteria "
                         "GROUP BY ticket_id, words HAVING n > 1"):
        findings.append(f"criteria: {r['n']} rows say {r['words'][:50]!r} "
                        f"on ticket {r['ticket_id']}")
    for r in _rows(conn, "SELECT item_id, COUNT(*) AS n FROM batches "
                         "WHERE status IN ('pending','running','deferred') "
                         "GROUP BY item_id HAVING n > 1"):
        findings.append(f"batches: item {r['item_id']} has {r['n']} open "
                        f"batches")
    for r in _rows(conn, "SELECT lower(trim(text)) AS words, COUNT(*) AS n "
                         "FROM tickets GROUP BY words HAVING n > 1"):
        findings.append(f"tickets: {r['n']} rows say {r['words'][:50]!r}")

    # 2b. An artefact id is unique across artefact tables (Law 14 at the
    #     id level). Walked live before the guard existed: tickets, criteria
    #     and tests sharing t1/t2/t3 made every ref ambiguous, and a correct
    #     challenge resolved its test to a criterion.
    id_tables = ["statements", "items", "tickets", "criteria", "tests",
                 "batches"]
    seen: dict[str, str] = {}
    for t in id_tables:
        for r in _rows(conn, f"SELECT id FROM {t}"):
            if r["id"] in seen and seen[r["id"]] != t:
                findings.append(f"id {r['id']!r} lives in both "
                                f"{seen[r['id']]} and {t}")
            seen.setdefault(r["id"], t)

    # 3. Cardinality the scheduler assumes.
    running = _rows(conn, "SELECT id FROM batches WHERE status='running'")
    if len(running) > 1:
        findings.append(f"batches: {len(running)} running at once "
                        f"({[r['id'] for r in running]})")

    # 4. Chains close. A superseded_by that points nowhere strands the trail.
    for r in _rows(conn, "SELECT id, superseded_by FROM glossary_terms "
                         "WHERE superseded_by IS NOT NULL"):
        if r["superseded_by"] not in ids:
            findings.append(f"glossary {r['id']}: superseded_by dangles "
                            f"({r['superseded_by']!r})")

    # 5. Answered means an answer exists.
    for r in _rows(conn, "SELECT m.id AS mid FROM messages m "
                         "WHERE m.status = 'answered' AND NOT EXISTS "
                         "(SELECT 1 FROM messages a WHERE a.cause_id = m.id)"):
        findings.append(f"messages: {r['mid']} is 'answered' and nothing "
                        f"answers it")

    return findings


def orphaned_grain_refs(conn: sqlite3.Connection) -> list[str]:
    """Rows that point at grains the index no longer holds.

    The index is a function of a commit and rebuilds outright -- correct, and
    it means a refresh can strand every reference to a grain that vanished
    upstream: a constraint binding whose tripwire is gone, a batch touch set
    predicting files that no longer exist, a criterion whose surface was
    renamed. None of that is the refresh's to *fix* (rebinding is the owner's
    judgement) but all of it is the refresh's to report, because a silently
    disarmed tripwire is the extended-use bug class in its purest form.
    """
    grains = {r["grain"] for r in conn.execute("SELECT grain FROM code_index")}
    out: list[str] = []
    for r in _rows(conn, "SELECT constraint_id, grain FROM constraint_bindings"):
        if r["grain"] not in grains:
            out.append(f"constraint {r['constraint_id']}: bound grain "
                       f"{r['grain']!r} is gone")
    for r in _rows(conn, "SELECT batch_id, grain FROM batch_touch"):
        if r["grain"] not in grains:
            out.append(f"batch {r['batch_id']}: predicted touch "
                       f"{r['grain']!r} is gone")
    for r in _rows(conn, "SELECT id, surface_refs FROM criteria "
                         "WHERE surface_refs != '[]'"):
        try:
            refs = json.loads(r["surface_refs"] or "[]")
        except json.JSONDecodeError:
            continue
        for ref in refs:
            if isinstance(ref, str) and "::" in ref and ref not in grains:
                out.append(f"criterion {r['id']}: surface {ref!r} is gone")
    return out


def main(argv: list[str]) -> int:
    from ..cli import RUNS, require
    from ..core.db import connect_readonly

    paths = ([require(argv[0])] if argv
             else sorted(RUNS.glob("*.db")))
    total = 0
    for p in paths:
        try:
            conn = connect_readonly(p)
            found = audit(conn)
        except sqlite3.Error as e:
            print(f"{p.stem:22} unreadable: {e}")
            continue
        total += len(found)
        if found:
            print(f"{p.stem:22} {len(found)} finding(s)")
            for f in found[:6]:
                print(f"    {f}")
            if len(found) > 6:
                print(f"    ... {len(found) - 6} more")
    print(f"\n{len(paths)} run(s) audited, {total} finding(s)")
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))
