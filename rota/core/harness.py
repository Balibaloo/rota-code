"""
Running the tests. The one gate in the system with no judgement in it at all.

It is deliberately the cheapest thing in the delivery loop and deliberately
first: a test costs a subprocess, a Critic session costs a model call, and a
structural review costs a model call over source. Ordering them by cost is not
an optimisation — it is what keeps `loop_cap` bounces affordable enough to be
the normal way a batch converges.

Nothing here interprets. The test said what it said; recording that through a
model would introduce a paraphrase risk over a boolean.
"""
from __future__ import annotations

import shlex
import sqlite3
import subprocess
import sys
from pathlib import Path

from . import lifecycle
from .runner import new_id

# pytest's contract, and the reason the three-way result exists: a test that
# fails is information about the code, a test that errors is usually information
# about the test.
EXIT_OK, EXIT_FAILED = 0, 1


def tests_for(conn: sqlite3.Connection, batch_id: str) -> list[dict]:
    return [dict(r) for r in conn.execute(
        "SELECT id, path, body FROM tests WHERE batch_id = ? ORDER BY id",
        (batch_id,))]


def worktree_of(conn: sqlite3.Connection, batch_id: str) -> str | None:
    row = conn.execute(
        "SELECT worktree FROM batches WHERE id = ?", (batch_id,)).fetchone()
    return row["worktree"] if row else None


def materialise(worktree: Path, tests: list[dict]) -> list[Path]:
    """
    Write each test to its declared path.

    Tester owns the test *bodies*; the worktree is Developer's. Writing them out
    at run time rather than committing them keeps that ownership intact — the
    tests are not part of the diff under review, which is what stops a batch
    from passing by editing its own criteria.
    """
    written = []
    for t in tests:
        target = worktree / t["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(t["body"], encoding="utf-8")
        written.append(target)
    return written


def run(conn: sqlite3.Connection, batch_id: str,
        *, timeout: int = 120) -> list[tuple[str, str]]:
    """
    Run every test for one batch, record each result, return them.

    A batch with no worktree runs nothing and records nothing — that is a batch
    that has not started, not a batch whose tests all pass, and the difference
    matters to every predicate downstream.
    """
    tests = tests_for(conn, batch_id)
    worktree = worktree_of(conn, batch_id)
    if not tests or not worktree or not Path(worktree).is_dir():
        return []

    root = Path(worktree)
    materialise(root, tests)
    attempt = lifecycle.next_attempt(conn, batch_id)

    results: list[tuple[str, str]] = []
    for t in tests:
        results.append((t["id"], _run_one(root, t["path"], timeout)))

    head = lifecycle.head_of(conn, batch_id)
    for test_id, result in results:
        lifecycle.record_test_run(conn, new_id("tr"), batch_id, test_id,
                                  result, attempt, commit_sha=head)
    return results


def _run_one(root: Path, path: str, timeout: int) -> str:
    """
    One test file, one word.

    Every non-pass outcome that is not an ordinary failure — a timeout, a
    collection error, an interpreter that would not start — is `error` rather
    than `fail`. They are different things to a Developer: `fail` says the code
    is wrong, `error` says the test could not answer.
    """
    # `sys.executable`, not "python". The first version used the latter and every
    # test came back `fail` — the interpreter on PATH had no pytest, so the exit
    # code was 1 and 1 means "tests failed". A missing harness reporting as a red
    # test suite is the worst available failure: it looks like the Developer's
    # problem and it is not.
    try:
        out = subprocess.run(
            [sys.executable, "-m", "pytest", shlex.quote(path), "-q", "--no-header"],
            cwd=root, capture_output=True, text=True, timeout=timeout)
    except (subprocess.TimeoutExpired, OSError):
        return "error"

    if out.returncode == EXIT_OK:
        return "pass"
    if out.returncode == EXIT_FAILED and "No module named pytest" not in out.stderr:
        return "fail"
    return "error"
