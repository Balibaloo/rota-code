"""
A session's end discards its uncommitted writes (frame 297, law 4).

Night 156 (2026-10-18): s214 wrote `src/click/decorators.py` in bg_2's
worktree, its commits were refused, and the session ended with the write
in the tree. s215, the next attempt, found the write and its open note,
and was refused for a cut it never made. Its wake said that the last
session ended with nothing written. Law 4, ratified on 2026-09-16: "A
worktree with uncommitted changes at session end is a fault. The
uncommitted change never existed."
"""
from __future__ import annotations

import pytest

from rota.core import boot as boot_mod
from rota.core.runner import run_session
from rota.core.scheduler import Wake, tick_batch_start
from rota.llm.llm import Pins, ScriptedBackend
from tests.rota.test_frame140_commit_beside_note import (  # noqa: F401
    DECORATORS, PATH, S282_NOTE, S282_TEXT, _developer, _git, db)

# The account's line and the wake's words share one sentence (frame 297).
GONE = "discarded at the session's end, no commit held them: "


def _write(path: str, text: str, start: int | None = None,
           end: int | None = None) -> str:
    span = "" if start is None else f", start={start}, end={end}"
    return f"TOOL: code.write(path={path!r}{span}, text={text!r})"


COMMIT = "TOOL: code.commit(message='Add show_python flag to version_option')"


def _run(db, script: list[str]):
    """One Developer session on b1's batch start, with the scripted replies."""
    return run_session(db, Wake("developer", "tick:batch_start", refs=("b1",)),
                       backend=ScriptedBackend(script), pins=Pins(model="scripted"),
                       batch_id="b1")


def _account(db) -> str:
    """The runner's account of the last session: its last turn."""
    row = db.execute(
        "SELECT t.completion FROM turns t JOIN sessions s ON s.id = t.session_id "
        "ORDER BY s.seq DESC, t.seq DESC LIMIT 1").fetchone()
    return row[0] if row else ""


def test_s214s_end_discards_the_write_and_closes_the_note(db, tmp_path):
    """s214's shape: the write drops lines, the commit beside it is refused,
    and the session ends. The tree is back at HEAD, the account names the
    path, the note is closed, and the next start says the write went."""
    _sb, root = _developer(db, tmp_path)
    # An LF tree, so the bytes below do not depend on the system config.
    _git(root, "config", "core.autocrlf", "false")
    head = _git(root, "rev-parse", "HEAD")
    _run(db, [_write(PATH, S282_TEXT, 546, 556) + "\n" + COMMIT, "", "", ""])
    assert _git(root, "status", "--porcelain") == ""
    assert _git(root, "rev-parse", "HEAD") == head
    assert (root / PATH).read_bytes() == DECORATORS.encode("utf-8")
    assert GONE + PATH in _account(db)
    assert [r[0] for r in db.execute(
        "SELECT status FROM drop_notes WHERE batch_id = 'b1'")] == ["restored"]
    db.execute("UPDATE batches SET head_commit = NULL WHERE id = 'b1'")
    wake = tick_batch_start(db)[0]
    assert wake.detail.endswith(f"the last session ended with no commit. Its "
                                f"writes were {GONE}{PATH}")
    assert "nothing written" not in wake.detail


def test_a_commit_stays_and_the_later_write_is_discarded(db, tmp_path):
    """Law 4 names the tree at the end, not the count of commits. The commit
    holds the first write, and the write after it is discarded."""
    _sb, root = _developer(db, tmp_path)
    _git(root, "config", "core.autocrlf", "false")
    extra = "src/click/extra.py"
    _run(db, [_write(extra, "X = 1\n"), COMMIT, _write(extra, "X = 2\n"), "", "", ""])
    assert _git(root, "show", f"HEAD:{extra}") == "X = 1"
    assert (root / extra).read_bytes() == b"X = 1\n"
    assert _git(root, "status", "--porcelain") == ""
    assert GONE + extra in _account(db)


def test_the_batch_test_files_survive_the_discard(db, tmp_path):
    """The batch's materialised test files are the harness's furniture, as
    `_uncommitted` counts them, so the discard leaves them."""
    _sb, root = _developer(db, tmp_path)
    test = "tests/test_version.py"
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body, version) "
               "VALUES ('t1', 'b1', 'c1', ?, 'def test_v():\n    pass\n', 1)", (test,))
    db.commit()
    (root / "tests").mkdir()
    (root / test).write_bytes(b"def test_v():\n    pass\n")
    new = "src/click/extra.py"
    _run(db, [_write(new, "X = 1\n"), "", "", ""])
    assert (root / test).read_bytes() == b"def test_v():\n    pass\n"
    assert not (root / new).exists()
    assert GONE + new in _account(db)
    assert test not in _account(db)


class _Dies(ScriptedBackend):
    """A backend that dies after its script, so the session fails."""

    def complete(self, system, user, pins, tools=None):
        if not self.script:
            raise RuntimeError("the stream died")
        return super().complete(system, user, pins, tools)


def test_a_failed_session_discards_its_write(db, tmp_path):
    """The failed session's handler ends a session too, so it discards."""
    _sb, root = _developer(db, tmp_path)
    run_session(db, Wake("developer", "tick:batch_start", refs=("b1",)),
                backend=_Dies([_write(PATH, S282_TEXT, 546, 556)]),
                pins=Pins(model="scripted"), batch_id="b1")
    assert _git(root, "status", "--porcelain") == ""
    assert GONE + PATH in _account(db)


def test_the_boot_discards_the_tree_of_a_running_batch(db, tmp_path):
    """A runner that dies ends no session in code, so the boot discards the
    tree of each running batch and closes its notes."""
    _sb, root = _developer(db, tmp_path)
    (root / PATH).write_bytes((DECORATORS + "# left\n").encode("utf-8"))
    db.execute("INSERT INTO drop_notes (batch_id, path, status, note, lines, defs, "
               "whole, noted) VALUES ('b1', ?, 'open', ?, '[]', '[]', '[]', '')",
               (PATH, S282_NOTE))
    db.commit()
    assert boot_mod.discard_running(db) == [("b1", [PATH])]
    assert _git(root, "status", "--porcelain") == ""
    assert [r[0] for r in db.execute(
        "SELECT status FROM drop_notes WHERE batch_id = 'b1'")] == ["restored"]


def test_the_boot_discards_the_tree_of_a_deferred_batch(db, tmp_path):
    """A deferred batch's last session ended too, so the boot discards its
    uncommitted writes by the same rule (ruled: the coordinator, pass 4)."""
    _sb, root = _developer(db, tmp_path)
    db.execute("UPDATE batches SET status = 'deferred' WHERE id = 'b1'")
    db.commit()
    (root / PATH).write_bytes((DECORATORS + "# left\n").encode("utf-8"))
    assert boot_mod.discard_running(db) == [("b1", [PATH])]
    assert _git(root, "status", "--porcelain") == ""


@pytest.mark.parametrize("autocrlf, eol", [("true", b"\r\n"), ("false", b"\n")])
def test_the_discard_gives_the_file_back_as_the_tree_checks_it_out(
        db, tmp_path, autocrlf, eol):
    """The discard uses the tree's own `core.autocrlf`, so a CRLF tree gets
    CRLF back and an LF tree gets LF (ruled: the coordinator, pass 4b)."""
    _sb, root = _developer(db, tmp_path)
    _git(root, "config", "core.autocrlf", autocrlf)
    (root / PATH).write_bytes((DECORATORS + "# left\n").encode("utf-8"))
    assert boot_mod.discard_running(db) == [("b1", [PATH])]
    assert (root / PATH).read_bytes() == DECORATORS.replace("\n", "\r\n" if eol == b"\r\n" else "\n").encode("utf-8")
    assert _git(root, "status", "--porcelain") == ""
