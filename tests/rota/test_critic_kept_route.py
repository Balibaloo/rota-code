"""
Sprint 35 row 4: the Critic's third route for a criterion that no added line
meets.

Night 174's `c_3_clear_prints_same` held because `clear()` still printed the
same output. The change added no line for it, and the door refused the
comment that stated it, so the seat failed it three times. A pass may now
name a kept line of the diff's context, `kept: <line>`, or the criterion's
passing test, `test: <id>`. The door checks each as a fact. The read is
`plans/critic-loop-read-2026-10-29.md`, section 4.

The exhaust half: night 175's Developer on `tick:exhausted` read passing
tests and no verdict, and wrote right code again. Its prompt now says that
the review is not done.
"""
from __future__ import annotations

import json
import subprocess

import pytest

from rota.core.db import init_db
from rota.core.runner import _review_pending_line, build_prompt
from rota.core.sandbox import build
from rota.core.scheduler import Wake
from rota.core.worktrees import GIT
from rota.roles import prompts

C1 = "c_1_clear_returns_bool"
C3 = "c_3_clear_prints_same"

_BEFORE = (
    "def clear():\n"
    "    # Clear the terminal screen.\n"
    "    if not isatty():\n"
    "        return\n"
    "    echo(\"CLEAR\", nl=False)\n"
)
_AFTER = (
    "def clear() -> bool:\n"
    "    # Clear the terminal screen.\n"
    "    if not isatty():\n"
    "        return False\n"
    "    echo(\"CLEAR\", nl=False)\n"
    "    return True\n"
)
KEPT = 'echo("CLEAR", nl=False)'


def _git(path, *args) -> str:
    return subprocess.run([*GIT, "-C", str(path), *args], check=True,
                          capture_output=True, text=True).stdout


@pytest.fixture
def db(tmp_path):
    """Night 174's bg_2 in small: `clear()` returns a bool, and its printed
    output stays the same."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    (repo / "termui.py").write_bytes(_BEFORE.encode())
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    (repo / "termui.py").write_bytes(_AFTER.encode())
    _git(repo, "commit", "-q", "-am", "the batch")
    head = _git(repo, "rev-parse", "HEAD").strip()
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1','the item','in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','i1','the ticket')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, 'tk1', "
                 "'clear() returns True when it clears the screen')", (C1,))
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, 'tk1', "
                 "'The output printed by clear() remains exactly the same')",
                 (C3,))
    conn.execute("INSERT INTO batches (id, item_id, status, worktree, "
                 "head_commit) VALUES ('bg_2', 'i1', 'running', ?, ?)",
                 (str(repo), head))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_2', 'tk1')")
    for tid, cid in (("tst_c1", C1), ("tst_c3", C3)):
        conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, "
                     "body) VALUES (?, 'bg_2', ?, 'tests/test_t.py', 'x')",
                     (tid, cid))
        _run(conn, tid, "pass", head)
    conn.commit()
    return conn


def _run(conn, tid: str, result: str, sha: str) -> None:
    n = conn.execute("SELECT COUNT(*) FROM test_runs").fetchone()[0]
    conn.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
                 "result) VALUES (?, 'bg_2', ?, ?, ?)",
                 (f"r{n}", tid, sha, result))


def _head(conn) -> str:
    return conn.execute("SELECT head_commit FROM batches").fetchone()[0]


def _critic(conn):
    return build("critic", conn, batch_id="bg_2", mode="review")


def _refused(sb, lines) -> str:
    with pytest.raises(ValueError) as exc:
        sb.call("verdicts.emit", batch_id="bg_2", result="pass", lines=lines)
    assert not [w for w in sb.ctx.writes if w[0] == "verdicts"]
    return str(exc.value)


def _land(sb, lines, held=True) -> dict:
    if held:
        with pytest.raises(ValueError, match="before the pass lands"):
            sb.call("verdicts.emit", batch_id="bg_2", result="pass",
                    lines=lines)
    sb.call("verdicts.emit", batch_id="bg_2", result="pass", lines=lines)
    (_, _, row), = [w for w in sb.ctx.writes if w[0] == "verdicts"]
    return row


def _forms_named(said: str) -> None:
    assert f"A value for {C3} takes one of three forms." in said
    assert "`kept: <a line of the [diff] block that starts with a space>`" in said
    assert f"`test: <the id of a test of {C3} that passed on the last run>`" in said


def test_a_kept_context_line_lands_and_the_row_records_the_route(db):
    lines = {C1: "return True", C3: f"kept: {KEPT}"}
    row = _land(_critic(db), lines)
    assert json.loads(row["lines"]) == lines
    assert json.loads(row["routes"]) == {C1: "added", C3: "kept"}


def test_a_kept_line_that_is_no_context_line_is_refused(db):
    said = _refused(_critic(db), {C1: "return True",
                                  C3: 'kept: echo("CLEAR")'})
    assert said.startswith(
        f"the kept line for {C3}, 'echo(\"CLEAR\")', is not a context line "
        f"of the diff of batch bg_2.")
    _forms_named(said)


def test_a_kept_added_line_is_refused(db):
    said = _refused(_critic(db), {C1: "return True", C3: "kept: return True"})
    assert "is an added line of the diff. Send it without `kept:`." in said
    _forms_named(said)


def test_a_kept_comment_is_refused(db):
    """The comment rule holds on the kept side too: a comment states the
    behaviour, and it does not do it."""
    said = _refused(_critic(db), {C1: "return True",
                                  C3: "kept: # Clear the terminal screen."})
    assert "is a comment. A docstring or comment line counts only" in said
    _forms_named(said)


def test_a_passing_bound_test_lands_with_no_hold_on_it(db):
    lines = {C1: "return True", C3: "test: tst_c3"}
    sb = _critic(db)
    with pytest.raises(ValueError) as exc:
        sb.call("verdicts.emit", batch_id="bg_2", result="pass", lines=lines)
    assert C1 in str(exc.value) and "test: tst_c3" not in str(exc.value)
    row = _land(sb, lines, held=False)
    assert json.loads(row["routes"]) == {C1: "added", C3: "test"}


def test_a_failed_test_is_refused(db):
    _run(db, "tst_c3", "fail", _head(db))
    said = _refused(_critic(db), {C1: "return True", C3: "test: tst_c3"})
    assert said.startswith("the last run of the test tst_c3 gave fail, not pass.")
    _forms_named(said)


def test_a_test_of_another_criterion_is_refused(db):
    said = _refused(_critic(db), {C1: "return True", C3: "test: tst_c1"})
    assert said.startswith(
        f"the test tst_c1 is a test of {C1}, not of {C3}. "
        f"The tests of {C3} are tst_c3.")
    _forms_named(said)


def test_an_unknown_test_is_refused(db):
    said = _refused(_critic(db), {C1: "return True", C3: "test: tst_c9"})
    assert said.startswith("'tst_c9' is not a test of batch bg_2.")
    _forms_named(said)


def test_a_bare_kept_line_names_the_kept_route(db):
    """A kept line sent with no prefix is refused as before, and the refusal
    says from the diff that the line is a context line."""
    said = _refused(_critic(db), {C1: "return True", C3: KEPT})
    assert f"{KEPT!r} is a context line of the diff" in said
    assert f"send `kept: <a line of the [diff] block" in said


def _exhausted_prompt(conn) -> str:
    sb = build("developer", conn, batch_id="bg_2", mode="exhausted",
               allow=prompts.mode_tools("developer", "exhausted"))
    wake = Wake("developer", "tick:exhausted", refs=("bg_2",),
                detail="the review gave no verdict after 3 attempts")
    return build_prompt("developer", sb, wake, {}, "MODE: exhausted")[1]


EXHAUST = ("The tests of batch bg_2 pass at its head commit. The Critic's "
           "review of that commit is not done, and it gave no verdict. Do not "
           "change the code for the review.")


def test_the_exhaust_line_shows_when_tests_pass_and_no_verdict(db):
    assert _review_pending_line(db, "bg_2") == EXHAUST
    assert EXHAUST in _exhausted_prompt(db)


def test_no_exhaust_line_when_a_test_fails(db):
    _run(db, "tst_c1", "fail", _head(db))
    db.commit()
    assert _review_pending_line(db, "bg_2") == ""
    assert EXHAUST not in _exhausted_prompt(db)


def test_no_exhaust_line_when_a_verdict_exists(db):
    db.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result, "
               "failed_criterion) VALUES ('critic:bg_2:x', 'bg_2', ?, "
               "'fail', ?)", (_head(db), C3))
    db.commit()
    assert _review_pending_line(db, "bg_2") == ""
