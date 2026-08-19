"""
The level above one run: choosing, creating, forking, and leaving.

These three operations are the ones that had no home. Everything *within* a run
already had a key; creating one, picking one and running one again beside itself
are operations *about* runs, and the seat had no screen where a run was a thing
you could point at -- which is the whole reason they stayed as commands.

What is asserted here is mostly refusal. A run list that opens the wrong run, a
form that silently lands on top of an existing one, or a quit that stops
forty sessions without asking are each cheap to write and expensive once.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from rota import cli
from rota.core.db import init_db


@pytest.fixture
def home(tmp_path, monkeypatch):
    runs = tmp_path / "runs"
    runs.mkdir()
    monkeypatch.setattr(cli, "RUNS", runs)
    return runs


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    (root / "pkg").mkdir(parents=True)
    (root / "pkg" / "thing.py").write_text("def go():\n    return 1\n")
    return root


def _seed(home: Path, name: str, root: Path | None = None, **config) -> Path:
    path = home / f"{name}.db"
    conn = init_db(path)
    if root is not None:
        config.setdefault("project_root", str(root))
    for key, value in config.items():
        conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                     (key, value))
    conn.commit()
    conn.close()
    return path


def _app(tmp_path, name="seat"):
    from rota.cockpit import tui

    return tui.RotaApp(tmp_path / f"{name}.db", "llama3.1:8b")


# ---------------------------------------------------------------------------
# Choosing
# ---------------------------------------------------------------------------

async def test_the_list_shows_every_run_and_which_source_it_is_about(
        tmp_path, home, project):
    """
    The column that decides whether the screen is usable at all.

    Two runs against one checkout is the normal case -- a branch against its
    main is the comparison an answer key exists for -- so the project name
    alone never said which was which. Until the commit was recorded they were
    indistinguishable, and the list is where that stops being tolerable.
    """
    _seed(home, "ctn_main", project, project_branch="main",
          project_commit="a41f2ee0000000000000000000000000000000000")
    _seed(home, "ctn_v3", project, project_branch="v3",
          project_commit="766c9e30000000000000000000000000000000000")

    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("ctrl+l")
        await pilot.pause()
        sources = {r[0]: r[2] for r in map(app.screen._cells, app.screen.rows)}

    assert sources["ctn_main"] == "main@a41f2ee"
    assert sources["ctn_v3"] == "v3@766c9e3"


async def test_a_run_whose_tree_moved_says_so(tmp_path, home, project):
    """
    The same comparison `boot.reconcile_worktrees` makes for a batch, one level
    up: a recorded commit against the real HEAD. A run whose tree moved is not
    wrong -- it is about something that no longer exists in that shape, and
    comparing it to a fresh run compares two different sources.
    """
    from rota.testkit import gitfixture

    repo = gitfixture.make(tmp_path)
    _seed(home, "moved", repo.root, project_branch="main",
          project_commit="0" * 40)

    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("ctrl+l")
        await pilot.pause()
        cells = {r[0]: r[2] for r in map(app.screen._cells, app.screen.rows)}

    assert "moved" in cells["moved"]


async def test_opening_a_stale_run_is_refused_with_the_reason(tmp_path, home):
    """
    Seven of eight existing runs are behind the schema. Opening one turns a
    single clear sentence in the list into eight empty panels in the seat,
    each failing separately and none of them saying why.
    """
    path = _seed(home, "old")
    conn = init_db(path)
    conn.execute("DROP TABLE survey_records")
    conn.commit()
    conn.close()

    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("ctrl+l")
        await pilot.pause()
        assert app.screen.rows[0]["state"] == "stale"
        app.screen.action_open()
        await pilot.pause()
        assert app.screen.__class__.__name__ == "RunList", "it opened anyway"
        assert "behind the schema" in str(app.screen.query_one("#runlist_note").content)


async def test_choosing_a_run_rebinds_the_seat_to_it(tmp_path, home, project):
    """
    Switching is the app rebinding its own database, not a restart. And the
    conversation goes with it: one run's words above another run's register is
    the single thing this screen exists to prevent.
    """
    other = _seed(home, "other", project)

    app = _app(tmp_path)
    async with app.run_test() as pilot:
        app.say("something said in the first run", "you", "green")
        await pilot.pause()
        app.open_run(other)
        await pilot.pause()

        assert app.db_path == other
        assert app.run_name == "other"
        assert app.root == project
        bubbles = app.query_one("#conversation").children
        assert all("first run" not in str(getattr(b, "content", ""))
                   for b in bubbles)


# ---------------------------------------------------------------------------
# Creating
# ---------------------------------------------------------------------------

async def test_the_form_refuses_to_land_on_an_existing_run(tmp_path, home, project):
    """
    Forking exists so that running again *beside* a run is the easy thing. A
    form that quietly overwrote would make the destructive path the default one.
    """
    from rota.cockpit.screens import NewRun

    _seed(home, "taken", project)
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        app.push_screen(NewRun(name="taken", root=str(project)))
        await pilot.pause()
        app.screen.go()
        await pilot.pause()

        assert app.screen.__class__.__name__ == "NewRun", "it dismissed anyway"
        assert "already exists" in str(app.screen.query_one("#newrun_detected").content)


async def test_the_form_says_what_the_repo_box_points_at(tmp_path, home):
    """
    Detecting the branch is what closes the hole that drawing this form found:
    a run recorded its project root and nothing else. It has to be shown to be
    useful, and showing it is what makes recording it obvious.
    """
    from rota.cockpit.screens import NewRun
    from rota.testkit import gitfixture

    repo = gitfixture.make(tmp_path)
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        app.push_screen(NewRun(root=str(repo.root)))
        await pilot.pause()
        shown = str(app.screen.query_one("#newrun_detected").content)

    branch, commit = cli.checkout_of(repo.root)
    assert commit[:7] in shown and branch in shown


async def test_a_directory_that_is_not_a_checkout_is_a_warning_not_a_refusal(
        tmp_path, home, project):
    """
    A tree can be onboarded without being a repository. The run then honestly
    describes a tree rather than a commit, and that is worth saying at the
    moment you press the button rather than when a comparison disagrees later.
    """
    from rota.cockpit.screens import NewRun

    app = _app(tmp_path)
    async with app.run_test() as pilot:
        app.push_screen(NewRun(name="plain", root=str(project)))
        await pilot.pause()
        assert "not a git checkout" in str(
            app.screen.query_one("#newrun_detected").content)
        app.screen.go()
        await pilot.pause()
        assert app.screen.__class__.__name__ != "NewRun", "a warning blocked it"


async def test_fork_offers_a_new_name_against_the_same_source(
        tmp_path, home, project):
    """
    §3 of SEAT.md: a rerun over the top destroys the run you wanted to compare
    against. Fork is the same source under another name, which is what makes
    "did that brief edit help" answerable at all.
    """
    from rota.cockpit.screens import RunList

    _seed(home, "ctn_v3", project)
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("ctrl+l")
        await pilot.pause()
        assert isinstance(app.screen, RunList)
        app.screen.action_fork()
        await pilot.pause()

        assert app.screen.__class__.__name__ == "NewRun"
        assert app.screen.query_one("#newrun_name").value == "ctn_v3-2"
        assert app.screen.query_one("#newrun_root").value == str(project)


# ---------------------------------------------------------------------------
# Leaving
# ---------------------------------------------------------------------------

async def test_quitting_asks_first_and_can_be_told_no(tmp_path, home):
    """
    Quitting stops the run -- the loop is the app's worker thread and there is
    no headless continuation. Cheap to resume and still never something to do
    by accident forty sessions in.

    The confirmation has to be able to say *no*, which is why the exit happens
    inside the callback rather than beside it. A modal that fires a callback
    while the quit proceeds is decoration.
    """
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("ctrl+c")
        await pilot.pause()
        assert app.screen.__class__.__name__ == "ConfirmationModal"

        app.screen.query_one("#modal_cancel").press()
        await pilot.pause()
        assert app.is_running, "cancel quit anyway"


async def test_the_confirmation_is_visible(tmp_path, home):
    """
    `#confirmation_container` had no rule anywhere in the repository while both
    its siblings carried the same four, so the dialog rendered as a bare label
    over the dimmed backdrop -- which looks like the modal never appearing, and
    quit is the worst place to learn that.
    """
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("ctrl+c")
        await pilot.pause()
        box = app.screen.query_one("#confirmation_container")
        assert box.styles.background.a > 0, "no background: invisible over the app"
        assert box.styles.border_top[0], "no border"


# ---------------------------------------------------------------------------
# The correction underneath all of it
# ---------------------------------------------------------------------------

def test_opening_a_seat_does_not_stop_a_run_somebody_else_is_driving(tmp_path):
    """
    `__init__` wrote `run_state = "stopping"` unconditionally and `loop.step`
    reads it every session, so opening a second seat silently halted the loop
    the first was driving -- and the first went on displaying `running`,
    because it refreshes that label on mount and on the pause key, never on a
    timer.

    A fresh seat starting paused is a fact about the seat, not about the run.
    """
    from rota.core import config
    from rota.cockpit import tui

    first = tui.RotaApp(tmp_path / "shared.db", "llama3.1:8b")
    config.resume(first.conn)
    assert config.get(first.conn, "run_state") == "running"

    tui.RotaApp(tmp_path / "shared.db", "llama3.1:8b")

    assert config.get(first.conn, "run_state") == "running", (
        "the second seat stopped the first one's run")


async def test_creating_a_run_from_the_list_actually_onboards_it(
        tmp_path, home, project, monkeypatch):
    """
    The path the whole screen exists for, and the one that silently did
    nothing.

    `RunList` opened the form with a callback that reloaded the table and
    dropped the result, so `n` worked, the form validated, and no run was ever
    made. Nothing errored -- which is the shape this project keeps finding, and
    the reason a screen gets driven end to end rather than unit-tested per
    widget.
    """
    from rota.cockpit.screens import RunList

    app = _app(tmp_path)
    started: list = []
    monkeypatch.setattr(app, "run_worker",
                        lambda fn, thread=True: started.append(fn.__name__))

    async with app.run_test() as pilot:
        await pilot.press("ctrl+l")
        await pilot.pause()
        assert isinstance(app.screen, RunList)

        app.screen.action_new()
        await pilot.pause()
        app.screen.query_one("#newrun_name").value = "fresh"
        app.screen.query_one("#newrun_root").value = str(project)
        app.screen.go()
        await pilot.pause()

    assert started == ["_do_new_run"], "the form's answer never reached the app"
    assert app._pending_new == (cli.resolve("fresh"), project)
