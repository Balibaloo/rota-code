"""
One way in, and a run you can name.

Everything here already existed and was reachable by four different module
paths with three different ideas of where the database is. `onboard_run`
defaults to `<repo>/.rota/oauthlib.db`, the TUI to `.rota/rota.db`, and the
cockpit **cannot be pointed at a file at all** -- it derives one from a project
root and boots an empty one when it is missing.

That last one is the defect these tests were written for. Every foreign-repo run
so far went to a name (`ctn_v3.db`), and the cockpit could not open any of them;
pointed at the checkout it would create a fresh empty database and serve *that*,
which renders as a system that ran and produced nothing. A viewer that invents
what it is showing is worse than one that refuses.

So: a run has a name, the root it is about is recorded inside it rather than
supplied alongside it, and anything that reads refuses what it cannot find.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from rota import cli
from rota.core.db import init_db


@pytest.fixture
def home(tmp_path, monkeypatch):
    """A runs directory of our own, so a test never lists the real ones."""
    runs = tmp_path / "runs"
    runs.mkdir()
    monkeypatch.setattr(cli, "RUNS", runs)
    return runs


def _run(home: Path, name: str, root: Path | None = None) -> Path:
    path = home / f"{name}.db"
    conn = init_db(path)
    if root is not None:
        conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
                     "('project_root', ?)", (str(root),))
    conn.commit()
    conn.close()
    return path


# ---------------------------------------------------------------------------
# Naming
# ---------------------------------------------------------------------------

def test_a_name_is_a_run_and_a_path_is_a_path(home):
    """
    Both spellings have to work, because both are already in use: every
    recorded invocation in the docs passes `--db .rota/something.db`, and
    nobody wants to type that twice a day forever.
    """
    assert cli.resolve("ctn_v3") == home / "ctn_v3.db"
    assert cli.resolve("some/where/else.db") == Path("some/where/else.db")


def test_a_reader_refuses_a_run_that_is_not_there(home):
    """
    The cockpit defect, stated once for everything that reads.

    Booting an empty database in place of the one you asked for does not
    degrade gracefully -- it answers a different question with the same
    confidence, and the answer looks like "the run produced nothing".
    """
    with pytest.raises(SystemExit) as exc:
        cli.require("never_ran")
    assert "never_ran" in str(exc.value)


def test_a_reader_names_the_runs_that_do_exist(home):
    """A refusal that does not say what *is* there sends you to `ls` and back."""
    _run(home, "ctn_v3")
    _run(home, "icalendar")
    with pytest.raises(SystemExit) as exc:
        cli.require("ctn_v2")
    assert "ctn_v3" in str(exc.value) and "icalendar" in str(exc.value)


# ---------------------------------------------------------------------------
# Listing
# ---------------------------------------------------------------------------

def test_ls_reports_the_root_each_run_is_about(home, tmp_path):
    """
    The inversion this file is built on: a database records the project it is
    about, so nothing downstream has to be told twice and the two cannot
    disagree.
    """
    _run(home, "ctn_v3", root=tmp_path / "checkouts" / "ctn")
    rows = {r["name"]: r for r in cli.runs()}
    assert rows["ctn_v3"]["root"] == str(tmp_path / "checkouts" / "ctn")


def test_ls_survives_a_database_it_cannot_read(home):
    """
    `.rota/` accumulates: eleven files in it today, several written against a
    schema that has since moved. A lister that dies on the oldest one is a
    lister that stops being run.
    """
    (home / "broken.db").write_bytes(b"not a database at all")
    _run(home, "fine")
    names = {r["name"] for r in cli.runs()}
    assert {"broken", "fine"} <= names
    assert next(r for r in cli.runs() if r["name"] == "broken")["error"]


def test_ls_asks_each_checkout_once_and_not_each_run(home, tmp_path, monkeypatch):
    """
    What listing costs. Reading 67 runs took 6.5 seconds and 6.2 of them were
    `git`: two processes per run, about 45ms each to start on Windows.

    A tree has one HEAD, so 55 runs against 24 checkouts is 24 questions.
    Asked once per run, the answers were identical and the wait was tenfold.
    """
    asked = []

    def counted(root):
        asked.append(str(root))
        return "main", "b" * 40

    monkeypatch.setattr(cli, "checkout_of", counted)
    for name in ("one", "two", "three"):
        path = _run(home, name, root=tmp_path / "shared")
        conn = sqlite3.connect(path)
        conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
                     "('project_commit', ?)", ("a" * 40,))
        conn.commit()
        conn.close()

    rows = {r["name"]: r for r in cli.runs()}

    assert asked == [str(tmp_path / "shared")], "one tree, one question"
    assert all(rows[n]["moved"] for n in ("one", "two", "three")),         "every run against that tree is behind it"


def test_ls_reports_when_a_run_was_made_and_when_it_was_last_opened(
        home, tmp_path):
    """
    Two dates the run keeps about itself. The list sorts on the second one,
    so a run that never recorded either would sit wherever the sort put it
    and say nothing about why.
    """
    from rota.core.db import mark_opened
    from rota.onboarding import boot

    path = home / "fresh.db"
    conn = init_db(path)
    boot.onboard(conn, tmp_path / "empty")
    mark_opened(conn)
    conn.close()

    row = next(r for r in cli.runs() if r["name"] == "fresh")
    stamped = {key for key, in sqlite3.connect(path).execute(
        "SELECT key FROM config WHERE key IN ('created_at', 'opened_at')")}
    assert stamped == {"created_at", "opened_at"}
    assert row["created"] > 0 and row["opened"] > 0


def test_a_second_onboarding_does_not_move_the_creation_date(home, tmp_path):
    """
    Onboarding runs again on a run that already exists. A run onboarded twice
    is still one run, so the date it was made must not move.
    """
    from rota.onboarding import boot

    conn = init_db(home / "twice.db")
    boot.onboard(conn, tmp_path / "empty")
    first = conn.execute(
        "SELECT value FROM config WHERE key = 'created_at'").fetchone()["value"]
    conn.execute("UPDATE config SET value = '2001-01-01 00:00:00' "
                 "WHERE key = 'created_at'")
    boot.onboard(conn, tmp_path / "empty")
    again = conn.execute(
        "SELECT value FROM config WHERE key = 'created_at'").fetchone()["value"]
    conn.close()

    assert first, "onboarding recorded nothing"
    assert again == "2001-01-01 00:00:00", "the second onboarding overwrote it"


def test_a_run_older_than_the_stamps_answers_with_its_file(home):
    """
    Every run in `.rota/` today was made before either stamp existed. A column
    of dashes for all of them would make the list's own default order useless
    on the day it ships, so the file answers when the run cannot.
    """
    _run(home, "old")
    row = next(r for r in cli.runs() if r["name"] == "old")

    assert row["created"] > 0 and row["opened"] > 0


# ---------------------------------------------------------------------------
# Wiping
# ---------------------------------------------------------------------------

def test_wipe_takes_the_journal_with_it(home):
    """
    A WAL outlives the database it belongs to. `connect` turns WAL on for every
    run, so `rm run.db` leaves `run.db-wal` and `run.db-shm` behind, and the
    next run of that name reopens a file with somebody else's uncommitted tail
    -- which is a wipe that did not wipe.
    """
    path = _run(home, "ctn_v3")
    for suffix in ("-wal", "-shm"):
        path.with_name(path.name + suffix).write_bytes(b"")

    cli.wipe(path)

    assert not path.exists()
    assert not path.with_name(path.name + "-wal").exists()
    assert not path.with_name(path.name + "-shm").exists()


def test_wipe_destroys_the_worktrees_before_the_file_that_names_them(home, tmp_path):
    """
    The whole reason this is a command and not `rm`.

    A worktree lives in the *project*, not beside the database, and the only
    record that it is ours is a row in the database. Delete the file first and
    the directory is unreachable by anything that checks ownership -- it stays
    on disk forever, because nothing left can prove it may be removed.
    """
    root = tmp_path / "project"
    (root / ".rota" / "worktrees" / "b1").mkdir(parents=True)
    tree = root / ".rota" / "worktrees" / "b1"

    path = _run(home, "ctn_v3", root=root)
    conn = sqlite3.connect(path)
    conn.execute("INSERT INTO items (id, text, kind) "
                 "VALUES ('i1','x','in_scope')")
    conn.execute("INSERT INTO batches (id, item_id, worktree) VALUES "
                 "('b1','i1',?)", (str(tree),))
    conn.commit()
    conn.close()

    removed = cli.wipe(path)

    assert not tree.exists(), "the worktree outlived the only thing that owned it"
    assert not path.exists()
    assert "b1" in removed["worktrees"]


def test_wipe_says_no_to_a_run_that_is_not_there(home):
    """Nothing here guesses, and a wipe least of all."""
    with pytest.raises(SystemExit):
        cli.main(["wipe", "never_ran", "--yes"])


# ---------------------------------------------------------------------------
# The cockpit, pointed at a file
# ---------------------------------------------------------------------------

def test_the_cockpit_opens_the_database_it_was_given(home):
    """It could not, before this. That is the whole of the defect."""
    from rota.cockpit import server

    path = _run(home, "ctn_v3")
    assert server.prepare_db(db=path) == path


def test_the_cockpit_refuses_to_invent_one(home):
    """
    Boot-if-missing is right for a project root and wrong for a named file.
    A root can legitimately have no run yet; a name you typed cannot.
    """
    from rota.cockpit import server

    with pytest.raises(SystemExit):
        server.prepare_db(db=home / "never_ran.db")


def test_wipe_removes_a_real_git_worktree_and_deregisters_it(tmp_path, home):
    """
    The other wipe test proves the *order*; this one proves the removal works
    on the thing it will actually meet.

    That test used a plain directory, which `shutil.rmtree` clears whether or
    not `git worktree remove` did anything -- so it could have passed with the
    git half broken, leaving the repository holding a registration for a path
    that is gone. `git worktree list` is the fact that distinguishes them, and
    it is the one a stale registration corrupts: the next batch of that id
    cannot create its worktree, and the error names a directory nobody can see.
    """
    from rota.core import worktrees
    from rota.testkit import gitfixture

    repo = gitfixture.make(tmp_path)
    path = _run(home, "ctn_v3", root=repo.root)

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("INSERT INTO items (id, text, kind) "
                 "VALUES ('i1','x','in_scope')")
    conn.execute("INSERT INTO batches (id, item_id) VALUES ('b1','i1')")
    tree = worktrees.create(conn, "b1")
    conn.commit()
    conn.close()

    assert tree.is_dir()
    assert any("b1" in w for w in gitfixture.registered_worktrees(repo.root))

    removed = cli.wipe(path)

    assert removed["worktrees"] == ["b1"]
    assert not tree.exists()
    assert not any("b1" in w for w in gitfixture.registered_worktrees(repo.root)), \
        "git still holds a registration for a directory that is gone"


def test_wiping_a_run_that_is_open_elsewhere_changes_nothing(home, monkeypatch):
    """
    You will do this: a seat is open on a run and you wipe it from a terminal.

    Windows refuses to unlink an open file, and the old order made that a
    *partial* wipe -- worktrees and processes were torn down first, then the
    unlink raised, so the run lost the things only it could prove it owned and
    kept the file that recorded them. The traceback was the polite part.

    So the lock is tested before anything is destroyed, by renaming the file
    aside and back. On Windows that fails exactly when another process holds
    it; on POSIX it succeeds, which is correct there because the unlink would
    have succeeded too.
    """
    import os

    path = _run(home, "held")
    torn = []
    monkeypatch.setattr(cli, "_teardown", lambda conn: torn.append(True))

    real_rename = os.rename

    def locked(src, dst):
        if str(src) == str(path):
            raise PermissionError(32, "used by another process")
        return real_rename(src, dst)

    monkeypatch.setattr(cli.os, "rename", locked)

    # `WipeRefused`, not `SystemExit`: this is a library call and only one of
    # its two callers is a shell. See the class docstring for what the wrong
    # type cost.
    with pytest.raises(cli.WipeRefused) as exc:
        cli.wipe(path)

    assert "open" in str(exc.value).lower()
    assert path.exists(), "removed while another process held it"
    assert not torn, "tore down what it could not then finish removing"


def test_wipe_refuses_with_an_exception_a_caller_can_catch(home, monkeypatch):
    """
    `SystemExit` is a command-line answer, not a library one.

    Raised from `cli.wipe`, it travelled out of a Textual callback, through the
    message pump and asyncio, and killed the seat: "Task exception was never
    retrieved ... SystemExit". The user was told the run was open in another
    process *and* lost the window they would have closed it from.

    `SystemExit` also inherits from `BaseException`, so every ordinary
    `except Exception` between here and the top — including the ones that exist
    to keep a UI alive — lets it straight through by design.
    """
    import os

    path = _run(home, "held")
    real_rename = os.rename
    monkeypatch.setattr(cli.os, "rename", lambda s, d: (
        (_ for _ in ()).throw(PermissionError(32, "in use"))
        if str(s) == str(path) else real_rename(s, d)))

    with pytest.raises(cli.WipeRefused) as exc:
        cli.wipe(path)

    assert not isinstance(exc.value, SystemExit)
    assert isinstance(exc.value, Exception), "a caller must be able to catch it"
    assert path.exists()


def test_the_command_line_still_exits_rather_than_tracebacks(home, monkeypatch):
    """
    The refusal must still read as a refusal at a shell prompt. Moving the
    exception type must not turn a sentence into a stack trace.
    """
    import os

    path = _run(home, "held")
    real_rename = os.rename
    monkeypatch.setattr(cli.os, "rename", lambda s, d: (
        (_ for _ in ()).throw(PermissionError(32, "in use"))
        if str(s) == str(path) else real_rename(s, d)))

    with pytest.raises(SystemExit) as exc:
        cli.main(["wipe", "held", "--yes"])

    assert "open in another process" in str(exc.value)


def test_agenda_and_sign_are_the_principals_seat(tmp_path, monkeypatch, capsys):
    """
    Loop 3 needs a principal present, and this is the seat that exists now:
    `agenda` prints the open gates and the register's outstanding fold, and
    `sign` answers one gate through the same `pump` every principal backend
    goes through -- so the CLI cannot invent a second way of recording a
    ruling. What lands is exactly what the scripted arc and the live drive
    consume: the verdict message, and `verdict:<id>` in config.
    """
    import json

    from rota import cli
    from rota.core.db import init_db
    from rota.testkit.fixtures import seed_provenance

    monkeypatch.setattr(cli, "RUNS", tmp_path)
    db = init_db(tmp_path / "run.db")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short) "
               "VALUES ('g1','recipe','a seed note')")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short) "
               "VALUES ('g2','intent','a config')")
    seed_provenance(db, "glossary_terms", "g1", "observed")
    seed_provenance(db, "glossary_terms", "g2", "observed")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('p1','t1','liaison','principal',"
               "'present','[\"g1\",\"g2\"]',1)")
    db.commit()
    db.close()

    assert cli.main(["agenda", "run"]) == 0
    out = capsys.readouterr().out
    assert "[p1] present" in out and "recipe" in out

    assert cli.main(["sign", "run", "p1", "--approve", "g1",
                     "--contest", "g2"]) == 0
    capsys.readouterr()

    from rota.core.db import connect_readonly

    conn = connect_readonly(tmp_path / "run.db")
    assert conn.execute("SELECT status FROM messages WHERE id='p1'"
                        ).fetchone()["status"] == "answered"
    verdict = conn.execute("SELECT id FROM messages WHERE verb='verdict'"
                           ).fetchone()["id"]
    ruling = json.loads(conn.execute(
        "SELECT value FROM config WHERE key=?",
        (f"verdict:{verdict}",)).fetchone()["value"])
    assert ruling == {"g1": "approve", "g2": "contest"}

    # A ruling on rows the gate does not ask about is refused before anything
    # is written.
    import pytest as _pytest

    with _pytest.raises(SystemExit, match="not an open gate"):
        cli.main(["sign", "run", "p1", "--approve", "g1"])
