"""
Frame 318: a head commit lifts a `tests_failing` key only when the red moves.

Night 162: the key `developer|tick:tests_failing|b_3` was quarantined after
s313. s315 committed b5edb9ac, two docstring lines, and the head write
deleted the key. The same test then failed with the same error, and s316 to
s318 spent three more ticks and 25 turns on it. A commit is progress only
when a red test passes at the new head, or the failing set or its first
error line changes.
"""
from __future__ import annotations

import pytest

from rota.core import harness
from rota.core.db import SessionResult, Write, init_db, session_commit
from rota.core.predicates import Wake
from rota.core.scheduler import note_dispatch, quarantine_stalled

KEY = "developer|tick:tests_failing|b1"
SAME = ("E       AssertionError: Expected output to end with 3.14.2, got: \n"
        "E       assert False\n")


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    wt = tmp_path / "wt"
    wt.mkdir()
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1','show the python version','in_scope',"
                 "'approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','i1','version_option shows python')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('c1','tk1','the message ends with the python version')")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit, "
                 "worktree) VALUES ('b1','i1','running','f64fd52', ?)", (str(wt),))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b1','tk1')")
    for tid in ("tst1", "tst2"):
        conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                     "VALUES (?, 'b1', 'c1', ?, 'def test_x():\n    pass\n')",
                     (tid, f"tests/test_{tid}.py"))
    conn.commit()
    return conn


def _run(conn, monkeypatch, said: dict[str, str]) -> None:
    """One harness run at the head. A test missing from `said` passes."""
    def one(root, path, timeout, runner=None, own=False):
        tid = path.split("test_")[-1].removesuffix(".py")
        out = said.get(tid)
        return ("fail", out) if out is not None else ("pass", "1 passed")

    # `harness.run` calls `_run_file`, which adds the red node ids (frame
    # 362, pass 5d). The stub names none.
    monkeypatch.setattr(harness, "_run_file", lambda *a, **k: (*one(*a, **k), []))
    harness.run(conn, "b1")
    conn.commit()


def _commit(conn, sha: str) -> None:
    session_commit(conn, SessionResult(
        session_id=f"s_{sha}", role="developer",
        writes=[Write("batches", "b1", {"head_commit": sha}, op="update",
                      amends=False)]))


def _key(conn, key: str = KEY):
    row = conn.execute("SELECT attempts, quarantined FROM tick_attempts "
                       "WHERE tick_key = ?", (key,)).fetchone()
    return (row["attempts"], row["quarantined"]) if row else None


def _quarantine(conn, key: str = KEY, attempts: int = 3, quarantined: int = 1):
    conn.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
                 "reported) VALUES (?, ?, ?, ?)",
                 (key, attempts, quarantined, quarantined))
    conn.commit()


def test_a_docstring_commit_keeps_the_quarantine_on_the_same_red(db, monkeypatch):
    """s315's shape: b5edb9ac changed two docstring lines, and the same test
    failed with the same first error line at the new head."""
    _run(db, monkeypatch, {"tst1": SAME})
    _quarantine(db)
    _commit(db, "b5edb9a")
    assert _key(db) == (3, 1), "a commit alone is not progress"
    _run(db, monkeypatch, {"tst1": SAME})
    assert _key(db) == (3, 1), "the red did not move"


def test_a_commit_that_turns_the_red_test_green_lifts_the_key(db, monkeypatch):
    _run(db, monkeypatch, {"tst1": SAME})
    _quarantine(db)
    _commit(db, "c0ffee1")
    _run(db, monkeypatch, {})
    assert _key(db) is None, "the red test passes at the new head"


def test_a_commit_after_which_another_test_fails_keeps_the_key(db, monkeypatch):
    """Review 3, high 1: a head that adds a new red is the Developer's own
    breakage, even when it cures the old red."""
    _run(db, monkeypatch, {"tst1": SAME})
    _quarantine(db)
    _commit(db, "c0ffee2")
    _run(db, monkeypatch, {"tst2": SAME})
    assert _key(db) == (3, 1), "the head broke another test"


def test_a_commit_after_which_the_first_error_line_changes_lifts_the_key(
        db, monkeypatch):
    _run(db, monkeypatch, {"tst1": SAME})
    _quarantine(db)
    _commit(db, "c0ffee3")
    _run(db, monkeypatch, {"tst1": "E   TypeError: 'NoneType' object is not callable\n"})
    assert _key(db) is None, "the same test raises another error"


def test_a_counting_key_on_an_unchanged_red_reaches_the_cap(db, monkeypatch):
    """Law 6 bounds the loop. A commit on the same red keeps the count, so
    the next dispatch reaches the cap and the key is quarantined."""
    _run(db, monkeypatch, {"tst1": SAME})
    _quarantine(db, attempts=2, quarantined=0)
    _commit(db, "b5edb9a")
    _run(db, monkeypatch, {"tst1": SAME})
    assert _key(db) == (2, 0), "the count holds"
    wake = Wake("developer", "tick:tests_failing", refs=("b1",))
    assert note_dispatch(db, wake) == 3
    assert quarantine_stalled(db, [wake]) == []
    assert _key(db) == (3, 1)


def test_a_commit_keeps_the_park_and_missing_keys_and_resets_the_rest(
        db, monkeypatch):
    """The other branches behave as before: the park and `tests_missing`
    keep their counts, and a quarantined key of another tick lifts."""
    _run(db, monkeypatch, {"tst1": SAME})
    _quarantine(db, "-|do:park|b1", attempts=2, quarantined=0)
    _quarantine(db, "tester|tick:tests_missing|b1", attempts=2, quarantined=0)
    _quarantine(db, "critic|tick:review|b1", attempts=2, quarantined=0)
    _quarantine(db, "critic|tick:verdict_failed|b1")
    _commit(db, "c0ffee4")
    assert _key(db, "-|do:park|b1") == (2, 0)
    assert _key(db, "tester|tick:tests_missing|b1") == (2, 0)
    assert _key(db, "critic|tick:review|b1") is None, "a commit resets the rest"
    assert _key(db, "critic|tick:verdict_failed|b1") is None, "a commit revives"


def test_a_commit_on_a_parked_batch_still_lifts_the_key(db, monkeypatch):
    """Frame 87: the commit is the way out the park ask names. The harness
    tests running batches only, so no run follows the commit to compare."""
    _run(db, monkeypatch, {"tst1": SAME})
    _quarantine(db)
    db.execute("UPDATE batches SET status = 'deferred' WHERE id = 'b1'")
    db.commit()
    _commit(db, "f1x")
    assert _key(db) is None


def test_a_second_run_at_one_head_on_the_same_red_keeps_the_key(db, monkeypatch):
    """Review 1, finding 1: a re-run at one head compared with the commit
    before, so a moved red then a quarantine lifted again on a re-run."""
    _run(db, monkeypatch, {"tst1": SAME})
    _commit(db, "b5edb9a")
    _run(db, monkeypatch, {"tst2": SAME})
    _quarantine(db)
    _run(db, monkeypatch, {"tst2": SAME})
    assert _key(db) == (3, 1), "the run before is the run at this head"


def test_a_run_with_no_worktree_keeps_the_key(db, monkeypatch):
    """Review 1, finding 4: no code ran, so the red did not move."""
    _run(db, monkeypatch, {"tst1": SAME})
    _quarantine(db)
    db.execute("UPDATE batches SET worktree = 'missing' WHERE id = 'b1'")
    _commit(db, "c0ffee5")
    harness.run(db, "b1")
    assert _key(db) == (3, 1)


def test_a_long_output_keeps_its_first_error_line(tmp_path, monkeypatch):
    """Review 1, finding 2: the output keeps a 2000-character tail, and the
    first `E ` line of the tail was not the run's."""
    from types import SimpleNamespace

    from rota.core import execute, provision
    from rota.core.db import _first_error

    text = ("E   AssertionError: the first error\n"
            + "".join(f"E   line {i} of a long diff\n" for i in range(200))
            + "1 failed in 0.12s\n")
    assert len(text) > 2000
    monkeypatch.setattr(provision, "python_for", lambda root: "python")
    monkeypatch.setattr(execute, "run", lambda *a, **k: SimpleNamespace(
        stdout=text, stderr="", returncode=harness.EXIT_FAILED, error=None))
    verdict, said = harness._run_one(tmp_path, "tests/test_x.py", 10)
    assert verdict == "fail"
    assert _first_error(said) == "AssertionError: the first error"
    assert said.endswith("1 failed in 0.12s")
