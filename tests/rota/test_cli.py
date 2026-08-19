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
    conn.execute("INSERT INTO items (id, text, kind, provenance) "
                 "VALUES ('i1','x','in_scope','decided')")
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
