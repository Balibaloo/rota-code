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
    if not tests:
        return []
    worktree = worktree_of(conn, batch_id)
    if not worktree or not Path(worktree).is_dir():
        # Could not run is a result, and it is recorded as one. This returned
        # [] -- "a batch that has not started, not a batch whose tests all
        # pass" -- which is the right distinction with the wrong consequence:
        # the harness predicate fires on "this commit has no test_runs row",
        # so a batch with tests and no worktree was re-offered every pass,
        # forever. Measured live on cnt_v2r: forty harness actions printing
        # "0 test(s)" while a 91-row ruling sat undispatched behind them.
        #
        # An error row per test is the drain the predicate already declares
        # -- drains=[("test_runs", "result", "error")] -- and it flows into
        # `tests_failing`, where a Developer is woken to a batch whose state
        # says exactly what is wrong.
        head = lifecycle.head_of(conn, batch_id)
        attempt = lifecycle.next_attempt(conn, batch_id)
        said = (f"the batch has no worktree at {worktree!r}; nothing can run. "
                f"The tests exist and were not attempted")
        results = [(t["id"], "error") for t in tests]
        for test_id, result in results:
            lifecycle.record_test_run(conn, new_id("tr", conn), batch_id,
                                      test_id, result, attempt,
                                      commit_sha=head, output=said)
        return results

    root = Path(worktree)
    materialise(root, tests)
    attempt = lifecycle.next_attempt(conn, batch_id)

    results: list[tuple[str, str]] = []
    output: dict[str, str] = {}
    for t in tests:
        verdict, said = _run_one(root, t["path"], timeout)
        results.append((t["id"], verdict))
        output[t["id"]] = said

    head = lifecycle.head_of(conn, batch_id)
    for test_id, result in results:
        lifecycle.record_test_run(conn, new_id("tr", conn), batch_id, test_id,
                                  result, attempt, commit_sha=head,
                                  output=output.get(test_id, ""))
    return results


def _run_one(root: Path, path: str, timeout: int) -> tuple[str, str]:
    """
    One test file: one word, and what the harness actually said.

    The word alone was all that was kept, and it left the Developer in
    `tests_failing` reading the test *body* and guessing what red looked like —
    the assertion that fired, the value it got, the traceback. Two L1 cases
    turned on exactly that judgement and produced precisely swapped answers,
    because from a criterion and a test body there is nothing to tell "the code
    is wrong" from "the test is wrong".

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
    except subprocess.TimeoutExpired:
        return "error", f"timed out after {timeout}s"
    except OSError as exc:
        return "error", str(exc)

    # Tail rather than head: pytest puts the summary and the failing assertion
    # at the end, and the beginning is collection chatter.
    said = (out.stdout or out.stderr or "")[-2000:].strip()
    if out.returncode == EXIT_OK:
        return "pass", said
    if out.returncode == EXIT_FAILED and "No module named pytest" not in out.stderr:
        return "fail", said
    return "error", said
