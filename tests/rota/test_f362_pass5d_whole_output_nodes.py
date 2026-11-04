"""
Frame 362, pass 5d: the review of pass 5c, findings 12 and 13.

Finding 12: the subset rule read the red nodes from the stored output,
which keeps its last 2,000 characters. A file with 40 failures lost its
first FAILED lines, so a new failure that ran first was excused. The names
now come from the whole output, and the base record and the run row store
them. Finding 13: a green grouped call with no summary gave every file a
pass with no proof that it ran.
"""
from __future__ import annotations

from types import SimpleNamespace

from rota.core import execute, harness

from .test_f362_pass5b_base_red_gates import PROJECT, db  # noqa: F401
from .test_f362_pass5c_grouped_run import FILES, _stub, conn  # noqa: F401

INH = harness.inherited_id(PROJECT)


def _summary(names):
    return "".join(f"FAILED {PROJECT}::{n} - AssertionError: {'x' * 60}\n"
                   for n in names) + f"{len(names)} failed\n"


def test_a_new_failure_that_runs_first_holds_the_gates(db, tmp_path, monkeypatch):
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(tmp_path),))
    old = [f"test_{i:02d}" for i in range(40)]
    said = {"now": _summary(old)}
    monkeypatch.setattr(execute, "run", lambda root, argv, **k: SimpleNamespace(
        error=None, stderr="", returncode=harness.EXIT_FAILED
        if PROJECT in argv else harness.EXIT_OK,
        stdout=said["now"] if PROJECT in argv else "1 passed"))
    harness.record_base_run(db, "b1", tmp_path, [INH])
    assert len(harness._tail(said["now"])) < len(said["now"])
    said["now"] = _summary(["test_00new"] + old)
    harness.run(db, "b1")
    assert harness.reds_that_hold(db, "b1", "h1") == [INH]


def test_a_green_call_with_no_summary_runs_each_file_alone(conn, monkeypatch):
    calls = _stub(monkeypatch, (harness.EXIT_OK, ""),
                  {f: (harness.EXIT_OK, "1 passed") for f in FILES})
    harness.run(conn, "b1")
    assert sorted(calls) == sorted([list(FILES)] + [[f] for f in FILES])
