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

import json

import pytest

from rota.core import boot as boot_mod
from rota.core.runner import run_session
from rota.core.scheduler import Wake, tick_batch_start
from rota.llm.llm import Pins, ScriptedBackend
from tests.rota.test_frame140_commit_beside_note import (  # noqa: F401
    DECORATORS, PATH, S282_NOTE, S282_TEXT, _developer, _git, db)

# The account's line (frame 297's review 3, finding 7).
GONE = "The runner discarded the writes that no commit held: "


def _j(*paths: str) -> str:
    """The paths as the account stores them, a JSON list (review 4)."""
    return json.dumps(list(paths), ensure_ascii=False)


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
    assert GONE + _j(PATH) in _account(db)
    assert [r[0] for r in db.execute(
        "SELECT status FROM drop_notes WHERE batch_id = 'b1'")] == ["restored"]
    db.execute("UPDATE batches SET head_commit = NULL WHERE id = 'b1'")
    wake = tick_batch_start(db)[0]
    # Review 3, finding 7: the sentence in Simplified Technical English.
    assert wake.detail.endswith(f"the last session committed nothing. The "
                                f"runner discarded its writes to {PATH}.")
    assert "nothing written" not in wake.detail
    # Review 3, finding 1: attempt 2's seat reads the discard in the result
    # of `batches.expect`, the read the runner pushes first.
    backend = ScriptedBackend(["", "", ""])
    run_session(db, wake, backend=backend, pins=Pins(model="scripted"), batch_id="b1")
    first = backend.calls[0][1]
    assert '"discarded before you"' in first
    assert (f"{PATH}. No commit held them, so the tree is at HEAD.") in first


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
    assert GONE + _j(extra) in _account(db)


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
    assert GONE + _j(new) in _account(db)
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
    out = run_session(db, Wake("developer", "tick:batch_start", refs=("b1",)),
                      backend=_Dies([_write(PATH, S282_TEXT, 546, 556)]),
                      pins=Pins(model="scripted"), batch_id="b1")
    assert _git(root, "status", "--porcelain") == ""
    assert GONE + _j(PATH) in _account(db)
    # Review 3, finding 2: the loop prints the last error, so the failure
    # stays last, and the discard line comes before it.
    assert out.errors[-1].startswith("session failed:")
    assert GONE + _j(PATH) in out.errors


def test_a_note_whose_lines_head_holds_closes_at_the_end(db, tmp_path):
    """Frame 297's review 3, finding 3: the session wrote the HEAD text back
    and ended. The path is clean, so the discard does not name it. The note
    still closes, because the tree holds its lines."""
    _sb, root = _developer(db, tmp_path)
    _run(db, [_write(PATH, S282_TEXT, 546, 556), _write(PATH, DECORATORS), "", "", ""])
    assert _git(root, "status", "--porcelain") == ""
    assert [r[0] for r in db.execute(
        "SELECT status FROM drop_notes WHERE batch_id = 'b1'")] == ["restored"]


def test_a_non_ascii_path_is_put_back_beside_the_others(tmp_path):
    """Frame 297's review 3, finding 5, probe A: git quoted the non-ASCII
    name, and the checkout refused the whole list. Each path comes back."""
    from rota.core import worktrees

    root = tmp_path / "wt"
    root.mkdir()
    name = "src/café.py"
    (root / "src").mkdir()
    for p in ("a.py", name):
        (root / p).write_bytes(b"x = 1\n")
    _git(root, "init", "-q")
    _git(root, "config", "core.autocrlf", "false")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "c0")
    for p in ("a.py", name):
        (root / p).write_bytes(b"x = 2\n")
    assert worktrees.discard(root) == sorted(["a.py", name])
    assert (root / "a.py").read_bytes() == b"x = 1\n"
    assert (root / name).read_bytes() == b"x = 1\n"


def test_the_account_names_a_path_git_could_not_put_back(db, tmp_path, monkeypatch):
    """Frame 297's review 3, finding 5: the account names only the paths the
    checkout put back, and says which paths it could not put back."""
    from rota.core import worktrees

    _sb, root = _developer(db, tmp_path)
    real = worktrees._git_paths

    def refuse(root_, args, paths):
        if args[0] == "checkout" and PATH in paths:
            return False
        return real(root_, args, paths)
    monkeypatch.setattr(worktrees, "_git_paths", refuse)
    (root / "NOTES.txt").write_bytes(b"changed\n")
    _run(db, [_write(PATH, S282_TEXT, 546, 556), "", "", ""])
    account = _account(db)
    assert GONE + _j("NOTES.txt") in account
    assert "The runner could not put back these paths: " + _j(PATH) in account


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


def _expect(db) -> str:
    """The next Developer's `batches.expect` key, or "" when it is absent."""
    from rota.core.sandbox import build
    from rota.roles import prompts

    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    return sb.call("batches.expect").get("discarded before you", "")


def test_the_key_survives_a_landing_that_fails(db, tmp_path, monkeypatch):
    """Frame 297's review 4, finding 1, probe B3: the landing raised after
    the normal end's discard. The second discard found a clean tree, so the
    account held no line. The failed path now writes the line it holds."""
    from rota.core import runner

    _sb, root = _developer(db, tmp_path)

    def dies(conn, result):
        raise RuntimeError("landing died")
    monkeypatch.setattr(runner, "after_landing", dies)
    out = _run(db, [_write(PATH, S282_TEXT, 546, 556), "", "", ""])
    assert out.errors[-1].startswith("session failed:")
    assert _git(root, "status", "--porcelain") == ""
    assert _expect(db) == f"{PATH}. No commit held them, so the tree is at HEAD."


def test_the_key_names_a_path_that_stays(db, tmp_path, monkeypatch):
    """Frame 297's review 4, finding 2, probe B5: a refused checkout left the
    write in the tree. The key names that path, and never says the whole
    tree is at HEAD."""
    from rota.core import worktrees

    _sb, root = _developer(db, tmp_path)
    real = worktrees._git_paths

    def refuse(root_, args, paths):
        if args[0] == "checkout" and PATH in paths:
            return False
        return real(root_, args, paths)
    monkeypatch.setattr(worktrees, "_git_paths", refuse)
    (root / "NOTES.txt").write_bytes(b"changed\n")
    _run(db, [_write(PATH, S282_TEXT, 546, 556), "", "", ""])
    assert _expect(db) == (f"NOTES.txt. No commit held them. The runner could not "
                           f"put back: {PATH}. The tree is at HEAD for the others.")


def test_the_boot_discard_reaches_the_next_seat(db, tmp_path):
    """Frame 297's review 4, finding 3: a runner that died left the write.
    The boot's discard writes the account line to the batch's last
    Developer session, so the next seat's key names the path."""
    _sb, root = _developer(db, tmp_path)
    _run(db, ["", "", ""])
    (root / PATH).write_bytes((DECORATORS + "# left\n").encode("utf-8"))
    assert boot_mod.discard_running(db) == [("b1", [PATH])]
    assert _expect(db) == f"{PATH}. No commit held them, so the tree is at HEAD."


def test_a_path_with_a_comma_stays_one_path(db, tmp_path):
    """Frame 297's review 4, finding 4: the account joined the paths with
    ", ", and the reader split on it. The account stores a JSON list."""
    from rota.core import lifecycle

    _developer(db, tmp_path)
    odd = "src/click/a, b.py"
    _run(db, [_write(odd, "X = 1\n"), "", "", ""])
    assert lifecycle.last_discard(db, "b1") == ([odd], [])
