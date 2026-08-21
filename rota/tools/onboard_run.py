"""
Drive a real onboarding to quiescence and report what came out.

Not a test. The suite proves the machine does what it says; this watches it meet
a repository nobody here wrote, which is the only thing that can answer whether
the artefacts are worth having. The predictions it is scored against are in
`ANSWER_KEY.md` and were written before the first session ran.

    python -m rota.tools.onboard_run --db .rota/oauthlib.db --root <checkout>
    python -m rota.tools.onboard_run --db .rota/oauthlib.db --report

Survey wakes only. `--all` lifts that, but the delivery loop on a foreign
checkout wants an environment that spawns and dies, and that is not built.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import time
from pathlib import Path

from .. import paths
from ..core import loop as loop_mod
from ..core.db import connect, init_db
from ..llm.llm import Pins, default_backend
from ..onboarding import boot


def onboard(db_path: str, root: str) -> None:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    conn = init_db(path)
    report = boot.onboard(conn, root)
    conn.commit()
    print(f"{report.areas} areas, {report.unsurveyed} under constraint zero, "
          f"{len(report.leaky)} leaky")


def drive(db_path: str, model: str, limit: int, survey_only: bool = True) -> None:
    conn = connect(db_path)
    backend, pins = default_backend(), Pins(model=model, temperature=0.0)
    started = time.time()

    for n in range(1, limit + 1):
        # Peek before stepping, so a non-survey wake can be reported rather than
        # silently run. On a foreign checkout the delivery loop needs an
        # environment that spawns and dies, and that is stage 3Bd.
        from ..core.scheduler import frontier

        ready = frontier(conn, principal_present=False)
        if not ready:
            print(f"\nquiescent after {n - 1} sessions "
                  f"({time.time() - started:.0f}s)")
            return
        # The terminologist's phase includes disambiguating the terms it wrote.
        #
        # `term_collision` now holds while the survey pass is running and fires
        # the moment it finishes -- which is exactly the moment this used to
        # return. Every run ended "no survey wakes left" with the collisions
        # still unexamined, so the phase stopped one step before the step that
        # cleans up after it.
        PHASE = {"tick:survey", "tick:term_collision", "message",
                 "tick:quarantined", "tick:constraint_zero"}
        if survey_only and not any(w.kind in PHASE for w in ready):
            print(f"\nno survey wakes left; frontier holds "
                  f"{sorted({w.kind for w in ready})}")
            return

        step = loop_mod.step(conn, backend=backend, pins=pins,
                             principal_present=False)
        conn.commit()
        wake = step.wake
        counts = _counts(conn)
        print(f"  {n:3d}  {str(wake):58s} "
              f"terms={counts['glossary_terms']:3d} "
              f"cons={counts['constraints']:3d} "
              f"items={counts['items']:3d} "
              f"surveys={counts['survey_records']:3d} "
              f"refs={counts['references_']:3d}"
              + (f"  [{step.note}]" if step.note else ""))
        if not step.productive and not step.wake:
            print(f"       idle: {step.note}")
            return

    print(f"\nstopped at the {limit}-session limit")


def _counts(conn: sqlite3.Connection) -> dict[str, int]:
    out = {}
    for table in ("glossary_terms", "constraints", "items", "survey_records",
                  "references_"):
        try:
            out[table] = conn.execute(
                f"SELECT COUNT(*) n FROM {table}").fetchone()["n"]
        except sqlite3.Error:
            out[table] = 0
    return out


def audit(db_path: str, root: str | None = None) -> int:
    """
    The mechanical half of scoring a run.

    The answer key measures recall — did it find what is actually there — and
    that needs a person who knows the repository. This measures precision, and
    every check in it comes from a fabrication that got past a reader on the
    first foreign repository. Returns the number of findings so a run can be
    judged without anybody reading it.
    """
    from ..roles import prompts
    from ..testkit import artefacts

    conn = connect(db_path)
    root = root or _root_of(conn)
    brief = prompts.piece("architect", "survey")
    findings = artefacts.audit(conn, Path(root), brief=brief)

    print("=" * 72)
    print(f"AUDIT — {len(findings)} finding(s)")
    if not findings:
        print("  nothing mechanical to object to. Recall is still the answer "
              "key's question, and this says nothing about it.")
    for f in findings:
        print(f"  {f}")
    return len(findings)


def _root_of(conn) -> str:
    from ..core.worktrees import project_root

    return str(project_root(conn))


def report(db_path: str) -> None:
    """Everything a person needs to score the run against the answer key."""
    conn = connect(db_path)

    print("=" * 72)
    print("SURVEYS")
    for r in conn.execute(
            "SELECT id, area, outcome FROM survey_records ORDER BY area, id"):
        print(f"  {r['outcome']:18s} {r['area']:34s} {r['id']}")

    print("\nGLOSSARY")
    for r in conn.execute(
            "SELECT term, sense_short, provenance, source_refs FROM glossary_terms "
            "ORDER BY term, id"):
        cited = " [cited]" if r["provenance"] == "cited" else ""
        print(f"  {r['term']:24s} {r['sense_short'][:90]}{cited}")

    print("\nCONSTRAINTS")
    for r in conn.execute(
            "SELECT id, headline, provenance FROM constraints ORDER BY id"):
        print(f"  {r['provenance']:9s} {r['headline'][:100]}")

    print("\nREFERENCES")
    for r in conn.execute(
            "SELECT url, claim, asked_by FROM references_ ORDER BY id"):
        print(f"  {r['asked_by']:14s} {r['url']}")
        print(f"                 {r['claim'][:100]}")

    print("\nCOUNTS", json.dumps(_counts(conn)))
    print()
    audit(db_path)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=str(paths.REPO / ".rota" / "oauthlib.db"))
    ap.add_argument("--root", help="checkout to onboard; omit to drive an existing db")
    ap.add_argument("--model", default="llama3.1:8b")
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--all", action="store_true", help="do not stop at survey wakes")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--audit", action="store_true",
                    help="the mechanical checks alone, no dump")
    args = ap.parse_args(argv)

    if args.root:
        onboard(args.db, args.root)
    if args.audit:
        return 1 if audit(args.db) else 0
    if args.report:
        report(args.db)
    elif not args.root or args.root:
        drive(args.db, args.model, args.limit, survey_only=not args.all)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
