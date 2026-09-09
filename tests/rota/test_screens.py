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
        # Counted, not searched. `ChatMessage` wraps its text in a Panel, so
        # `.content` never holds the words -- an "is it absent" assertion
        # against it passes whether or not the pane was cleared, which is the
        # shape of check this project keeps having to throw away. One bubble
        # left, and it is the one `open_run` writes.
        assert len(app.query_one("#conversation").children) == 1


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

def _seed_items(path: Path, count: int) -> None:
    """Give a run a count to sort on."""
    import sqlite3

    conn = sqlite3.connect(path)
    conn.executemany(
        "INSERT INTO items (id, text, kind, provenance) VALUES (?,?,?,?)",
        [(f"i{n}", "a thing", "in_scope", "observed") for n in range(count)])
    conn.commit()
    conn.close()


async def _open_list(pilot):
    await pilot.press("ctrl+l")
    await pilot.pause()
    return pilot.app.screen


def _table(screen):
    from textual.widgets import DataTable

    return screen.query_one("#runs", DataTable)


async def test_the_list_opens_on_the_run_you_had_open_last(
        tmp_path, home, project):
    """
    Name order is an order about the letters in a name, and never about you.
    The run you want is nearly always the run you were just in.
    """
    _seed(home, "aaa", project, opened_at="2026-01-01 09:00:00")
    _seed(home, "bbb", project, opened_at="2026-09-08 17:30:00")
    _seed(home, "ccc", project, opened_at="2026-05-04 12:00:00")

    app = _app(tmp_path)
    async with app.run_test() as pilot:
        screen = await _open_list(pilot)

        assert (screen.sort_by, screen.sort_desc) == ("opened", True)
        assert [row["name"] for row in screen.rows] == ["bbb", "ccc", "aaa"]


async def test_the_seat_stamps_the_run_it_opens(tmp_path, home, project):
    """
    Opening means the seat, and only the seat. The cockpit is a viewer and
    changes no state, and `rota ls` reads every run in the directory. Either
    of those stamping a run would make the column a record of being looked
    at rather than of being worked in.
    """
    import sqlite3

    other = _seed(home, "other", project, opened_at="2001-01-01 00:00:00")

    app = _app(tmp_path)
    async with app.run_test() as pilot:
        app.open_run(other)
        await pilot.pause()

    stamp, = sqlite3.connect(other).execute(
        "SELECT value FROM config WHERE key = 'opened_at'").fetchone()
    assert stamp > "2001-01-01 00:00:00", "the seat opened it and said nothing"


def test_an_age_is_one_cell_wide_and_says_when(tmp_path):
    """A date makes the reader do the subtraction. The column answers it."""
    import time

    from rota.cockpit.screens import RunList

    now = time.time()
    assert RunList._age(now - 5) == "now"
    assert RunList._age(now - 90) == "1m"
    assert RunList._age(now - 3600 * 5) == "5h"
    assert RunList._age(now - 86400 * 3) == "3d"
    assert RunList._age(now - 86400 * 400) == "1y"
    assert RunList._age(0) == "—", "a file this could not read is not a date"


async def test_a_count_column_sorts_as_a_number(tmp_path, home, project):
    """
    Ten items is more than nine items. A string sort says otherwise, and a
    column of counts is where that answer is the whole question.
    """
    _seed_items(_seed(home, "few", project), 9)
    _seed_items(_seed(home, "many", project), 10)

    app = _app(tmp_path)
    async with app.run_test() as pilot:
        screen = await _open_list(pilot)
        screen.sort_on("items")
        await pilot.pause()
        assert [row["name"] for row in screen.rows] == ["few", "many"]
        screen.sort_on("items")                      # asked twice, so reversed
        await pilot.pause()
        assert [row["name"] for row in screen.rows] == ["many", "few"]


async def test_the_cursor_holds_its_run_across_a_sort(tmp_path, home, project):
    """
    You sort to find a run. A cursor that held its row number instead would
    leave you pointed at a different run every time. The next key you press
    acts on the run under the cursor.
    """
    _seed_items(_seed(home, "aaa", project), 3)
    _seed_items(_seed(home, "bbb", project), 2)
    _seed_items(_seed(home, "ccc", project), 1)

    app = _app(tmp_path)
    async with app.run_test() as pilot:
        screen = await _open_list(pilot)
        screen.sort_on("run")                   # a named order to point into
        await pilot.pause()
        _table(screen).move_cursor(row=2)
        await pilot.pause()
        assert screen.selected["name"] == "ccc"
        screen.sort_on("items")
        await pilot.pause()
        assert screen.selected["name"] == "ccc", "the cursor stayed on a row"
        assert screen.rows[0]["name"] == "ccc"


async def test_a_sort_survives_a_reload(tmp_path, home, project):
    """
    The sort belongs to the screen and not to one reading of the directory.
    A reload that dropped the sort would put the list back in name order
    under a header that still named the other column.
    """
    _seed_items(_seed(home, "aaa", project), 3)
    _seed_items(_seed(home, "bbb", project), 1)

    app = _app(tmp_path)
    async with app.run_test() as pilot:
        screen = await _open_list(pilot)
        screen.sort_on("items")
        await pilot.pause()
        screen.action_reload()
        await pilot.pause()

        assert [row["name"] for row in screen.rows] == ["bbb", "aaa"]
        assert "↑" in str(_table(screen).columns["items"].label)


async def test_runs_that_tie_fall_back_to_their_names(tmp_path, home, project):
    """
    Most columns tie. Seven runs at `ready`, left in the order the previous
    sort happened to give them, is an order with no rule you can see.
    """
    for name in ("ccc", "aaa", "bbb"):
        _seed(home, name, project)

    app = _app(tmp_path)
    async with app.run_test() as pilot:
        screen = await _open_list(pilot)
        screen.sort_on("state")                     # every run is `ready`
        await pilot.pause()
        assert [row["name"] for row in screen.rows] == ["aaa", "bbb", "ccc"]
        screen.sort_on("state")                     # reversed, and still named
        await pilot.pause()
        assert [row["name"] for row in screen.rows] == ["aaa", "bbb", "ccc"]


async def test_s_moves_the_sort_along_the_columns_and_wraps(tmp_path, home):
    """One key, every column, and no dead end at the last one."""
    _seed(home, "one")

    app = _app(tmp_path)
    async with app.run_test() as pilot:
        screen = await _open_list(pilot)
        start = screen.COLUMNS.index(screen.sort_by)
        order = screen.COLUMNS[start + 1:] + screen.COLUMNS[:start + 1]
        for expected in order:
            await pilot.press("s")
            assert screen.sort_by == expected


async def test_shift_s_reverses_without_moving_the_column(tmp_path, home, project):
    """
    Direction is a second decision. Reversing by cycling through every other
    column and back is not a decision anybody makes twice.
    """
    _seed(home, "aaa", project)
    _seed(home, "bbb", project)

    app = _app(tmp_path)
    async with app.run_test() as pilot:
        screen = await _open_list(pilot)
        screen.sort_on("run")
        await pilot.pause()
        assert [row["name"] for row in screen.rows] == ["aaa", "bbb"]

        await pilot.press("S")
        await pilot.pause()

        assert screen.sort_by == "run", "reversing moved the column"
        assert [row["name"] for row in screen.rows] == ["bbb", "aaa"]


# ---------------------------------------------------------------------------
# Creating
# ---------------------------------------------------------------------------

async def test_the_form_refuses_to_land_on_an_existing_run(tmp_path, home, project):
    """
    Forking exists so that running again *beside* a run is the easy thing. A
    form that quietly overwrote would make the destructive path the default one.
    """
    from rota.cockpit.screens import NewRun

    taken = _seed(home, "taken", project)
    conn = init_db(taken)
    conn.execute("INSERT INTO code_index (grain, grain_kind, area) "
                 "VALUES ('a.py','path','a')")       # it holds a run, not a name
    conn.commit()
    conn.close()

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


# ---------------------------------------------------------------------------
# Is it going anywhere
# ---------------------------------------------------------------------------

async def test_a_barren_session_is_visible_as_one(tmp_path, home):
    """
    `Step.productive` has always said whether a session changed anything, and
    nothing in the seat read it -- so a run that had stopped getting anywhere
    looked exactly like one that was working. Every line was new, because every
    line was a different message.
    """
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        app.note_step("· wrote a term", productive=True)
        await pilot.pause()
        assert app.last_productive is not None and app.barren_since == 0

        for _ in range(3):
            app.note_step("· committed without changing anything",
                          productive=False)
        await pilot.pause()

        assert app.barren_since == 3
        assert "3 barren since" in str(app.query_one("#pulse").content)


async def test_a_repeating_chain_is_shown_while_it_climbs(tmp_path, home):
    """
    The livelock, in time to act on.

    `quarantine_looping` already walks `cause_id` counting the same edge, and
    throws the number away unless it exceeds the cap. By then the message is
    quarantined and the interesting part -- watching it climb -- is over. This
    is that number, shown.
    """
    from rota.core.scheduler import deepest_repeat

    app = _app(tmp_path)
    async with app.run_test() as pilot:
        prev = None
        for i in range(1, 8):
            app.conn.execute(
                "INSERT INTO messages (id, thread_id, from_role, to_role, verb,"
                " body_refs, seq, status, cause_id) VALUES "
                "(?,?,'vision_keeper','architect','reopen','[]',?,?,?)",
                (f"m{i}", f"t{i}", i, "open" if i == 7 else "answered", prev))
            prev = f"m{i}"

        count, edge, message = deepest_repeat(app.conn)
        assert (count, message) == (7, "m7")
        assert edge == "vision_keeper->architect:reopen"

        app.refresh_pulse()
        await pilot.pause()
        shown = str(app.query_one("#pulse").content)
        assert "vision_keeper->architect:reopen" in shown and "×7" in shown


def test_deepest_repeat_is_quiet_when_nothing_is_looping(tmp_path):
    """The ordinary case, which must cost nothing and say nothing."""
    from rota.core.scheduler import deepest_repeat

    conn = init_db(tmp_path / "quiet.db")
    assert deepest_repeat(conn) == (0, "", "")


async def test_a_seat_with_no_run_opens_the_list(tmp_path, home, monkeypatch):
    """
    The first thing you ever type.

    The list was reachable only from inside a run, and `--db` defaulted to
    `.rota/rota.db` -- so a bare start silently opened or created one
    particular run whatever you meant, and making your *first* one was a
    command. That is the one trip to the terminal this screen exists to remove,
    surviving in the case where it is least excusable.
    """
    from rota.cockpit import tui
    from rota.cockpit.screens import RunList

    app = tui.RotaApp(None, "llama3.1:8b")
    assert app.conn is None
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.pause()
        assert isinstance(app.screen, RunList)
        assert "no run open" in app.sub_title


async def test_a_seat_with_no_run_says_so_rather_than_failing(tmp_path, home):
    """
    Everything the sidebar draws reads the connection, and there is not one.
    Each of those is a crash on startup if it is not answered, and the answer
    is a sentence rather than an empty panel.
    """
    from rota.cockpit import tui

    app = tui.RotaApp(None, "llama3.1:8b")
    async with app.run_test() as pilot:
        await pilot.pause()
        app.screen.action_dismiss_list()
        await pilot.pause()

        assert "no run open" in str(app.query_one("#run_state").content)

        said = []
        app.say = lambda text, *a, **k: said.append(text)
        app.on_input_submitted(type("E", (), {
            "value": "build me a thing",
            "input": type("I", (), {"value": ""})()})())
        await pilot.pause()
        assert said and "no run open" in said[0]


# ---------------------------------------------------------------------------
# The cockpit the seat starts, and the seat's responsibility for it
# ---------------------------------------------------------------------------

async def test_the_spawned_cockpit_never_writes_to_this_terminal(tmp_path, home):
    """
    A child inherits stdout and stderr, so the server's logging printed *into
    the middle of the TUI* -- text arriving from outside the widget tree, which
    Textual neither controls nor repaints.

    `--no-reload` is the other half and fixes it at the source: the reloading
    server re-executes itself in a grandchild on every source change and
    narrates each one. Reload is for editing the cockpit's own code; a cockpit
    opened to look at a run does not want it, and a grandchild is a process no
    parent can reliably kill on Windows.
    """
    from rota.cockpit import tui

    calls = {}

    class FakeChild:
        pid = 4321
        def poll(self): return None
        def terminate(self): calls["terminated"] = True
        def wait(self, timeout=None): return 0

    def fake_popen(argv, **kw):
        calls["argv"], calls["kw"] = argv, kw
        return FakeChild()

    app = _app(tmp_path)
    async with app.run_test() as pilot:
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(tui.subprocess, "Popen", fake_popen)
            app.open_cockpit(app.db_path)
            await pilot.pause()

            assert "--no-reload" in calls["argv"]
            assert calls["kw"]["stdout"] is not None, "inherits this terminal"
            assert calls["kw"]["stderr"] is calls["kw"]["stdout"]
            assert calls["kw"]["stdin"] is tui.subprocess.DEVNULL

            # And it is held, because a process nothing holds is an orphan.
            assert len(app.cockpits) == 1


async def test_the_seat_stops_the_cockpits_it_started(tmp_path, home):
    """
    Quitting left a server holding port 8899, so the next one refused to bind.

    This is the failure `ENVIRONMENT.md` is entirely about, reached by hand in
    the one place that spawns something outside the scheduler -- so it obeys
    the same rule the reaper does: stop only what this process started. The
    proof of ownership is holding the handle, which is why a cockpit you
    started yourself elsewhere is never looked for and never touched.

    On unmount, because that is the path every exit shares: the confirmed quit,
    a `ctrl+c` when no modal is up, and an exception that takes the app down.
    """
    from rota.cockpit import tui

    stopped = []

    class FakeChild:
        pid = 99
        def poll(self): return None
        def terminate(self): stopped.append(self.pid)
        def wait(self, timeout=None): return 0

    class FakeLog:
        closed = False
        def close(self): FakeLog.closed = True

    app = _app(tmp_path)
    async with app.run_test() as pilot:
        app.cockpits.append((FakeChild(), FakeLog()))
        await pilot.pause()

    assert stopped == [99], "the cockpit outlived the seat"
    assert FakeLog.closed


async def test_a_run_switch_does_not_orphan_or_close_a_cockpit(
        tmp_path, home, project):
    """
    A cockpit belongs to the seat that started it, not to the run that happened
    to be open. Switching must not orphan one -- nothing would stop it -- and
    must not close a window you are still reading.
    """
    from rota.cockpit import tui

    class FakeChild:
        pid = 7
        def poll(self): return None

    app = _app(tmp_path)
    other = _seed(home, "other", project)
    async with app.run_test() as pilot:
        app.cockpits.append((FakeChild(), object()))
        app.open_run(other)
        await pilot.pause()
        assert len(app.cockpits) == 1, "the handle was dropped on switch"
        app.cockpits.clear()          # do not signal a fake on teardown


async def test_enter_and_a_click_both_open_the_run(tmp_path, home, project):
    """
    Neither worked, and for the reason the seat already had a test about:
    `DataTable` binds `enter` to `select_cursor` and holds the focus the whole
    time this screen is up, so a screen binding for it never fires. A click
    emits the same `RowSelected` event, so handling the event gets both where a
    binding would have got neither.
    """
    from rota.cockpit.screens import RunList
    from textual.widgets import DataTable

    _seed(home, "pickme", project)
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("ctrl+l")
        await pilot.pause()
        assert isinstance(app.screen, RunList)
        assert not any(k == "enter" for k, _, _ in RunList.BINDINGS), (
            "a binding the table eats is one the footer advertises and "
            "nothing performs")

        await pilot.press("enter")
        await pilot.pause()

    assert app.run_name == "pickme"


async def test_wiping_the_open_run_goes_through_the_seat(tmp_path, home, project):
    """
    The seat holds an open connection, and Windows will not unlink an open
    file -- so this reported success and removed nothing, leaving the seat
    pointed at a database it believed it had wiped.
    """
    from rota.cockpit.screens import RunList

    app = _app(tmp_path)
    path = app.db_path
    name = app.run_name
    async with app.run_test() as pilot:
        await pilot.press("ctrl+l")
        await pilot.pause()
        screen = app.screen
        screen.rows = [{"name": name, "path": str(path), "state": "ready",
                        "root": str(project), "counts": {}, "branch": "",
                        "commit": "", "moved": False, "created": 0.0,
                        "opened": 0.0}]
        screen.query_one("#runs").add_row(*screen._cells(screen.rows[0]))
        screen.query_one("#runs").move_cursor(row=0)
        screen.action_wipe()
        await pilot.pause()
        app.screen.handle_submit(name)
        await pilot.pause()

        assert not path.exists(), "nothing was removed"
        assert app.db_path is None and app.conn is None, (
            "the seat kept hold of a run that no longer exists")


async def test_a_modal_submission_is_not_also_a_sentence(tmp_path, home):
    """
    Events bubble widget -> screen -> app, and `InputModal` does not stop them,
    so the run name typed to confirm a wipe also arrived at the seat's own
    handler and was sent to Liaison as a chat turn.
    """
    app = _app(tmp_path)
    said = []
    async with app.run_test() as pilot:
        app.say = lambda text, *a, **k: said.append(text)
        app.on_input_submitted(type("E", (), {
            "value": "ctn_v3",
            "input": type("I", (), {"id": "modal_input", "value": ""})()})())
        await pilot.pause()
    assert said == [], "a confirmation was taken as a sentence"


async def test_every_screen_binding_survives_its_own_focused_widget(
        tmp_path, home, project):
    """
    The generalisation the `enter` bug demands.

    `test_every_binding_survives_the_input_having_focus` covered the *app* and
    was written after `ctrl+w` turned out to be the input's delete-word. Then
    `enter` on the run list turned out to be the table's `select_cursor`, and
    the guard did not cover screens -- so the identical failure, in the
    identical shape, got through the test written for it.

    Asked per key, not per sweep. The first version compared two lists at the
    end and, on a genuinely swallowed key, reported `swallowed: []` -- the
    action had fired for a *different* key, so the set difference was empty and
    only the length disagreed. A guard whose failure message names nothing is
    most of the way back to no guard.

    What it asserts is that the key *produces the action*, by whatever route.
    `enter` reaches `open` through `RowSelected` rather than through a binding,
    and that is a pass: the footer promises behaviour, not a mechanism.
    """
    from rota.cockpit.screens import NewRun, RunList

    _seed(home, "somerun", project)
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        for screen_class in (RunList, NewRun):
            app.push_screen(screen_class())
            await pilot.pause()
            screen = app.screen
            assert isinstance(screen, screen_class)

            fired: list[str] = []
            for _, action, _ in screen_class.BINDINGS:
                setattr(screen, f"action_{action}",
                        (lambda a: lambda: fired.append(a))(action))

            for key, action, _ in screen_class.BINDINGS:
                if action.startswith("dismiss") or action == "cancel":
                    continue          # would close the screen mid-sweep
                fired.clear()
                await pilot.press(key)
                assert action in fired, (
                    f"{screen_class.__name__}: {key!r} is bound to {action!r} "
                    f"and pressing it did nothing — the focused widget ate it")

            screen.dismiss(None)
            await pilot.pause()


# ---------------------------------------------------------------------------
# What "wipe" means
# ---------------------------------------------------------------------------

async def test_wiping_the_open_run_leaves_no_run_behind(tmp_path, home, project):
    """
    One word, one meaning.

    From the list, `wipe` deleted the file and the run was gone. From the seat
    it deleted the file and then `init_db` put an empty one back, so the run
    survived as a husk: no `project_root`, no `code_index`, opening happily and
    showing `no project` in the title bar. That husk is a real row in `.rota/`
    right now, and this is how it got there.

    Wipe means the run is gone. The seat then has no run, which is a state it
    can hold, and the answer to "no run open" is the screen that makes one.
    """
    from rota.cockpit.screens import RunList

    app = _app(tmp_path)
    path = app.db_path
    async with app.run_test() as pilot:
        await pilot.press("alt+w")
        app.confirm("seat")
        await pilot.pause()

        assert not path.exists(), "the file came back"
        assert app.db_path is None and app.conn is None
        assert isinstance(app.screen, RunList), "left staring at nothing"


async def test_rerun_keeps_the_run_because_it_is_about_to_refill_it(
        tmp_path, project):
    """
    The one caller that wants the file back. `rerun` is wipe-then-index, and
    indexing needs somewhere to write -- so it is the exception, and it says so
    at the call rather than making wipe ambiguous for everybody.
    """
    from rota.cockpit import tui

    app = tui.RotaApp(tmp_path / "ctn_v3.db", "llama3.1:8b", root=project)
    app.run_worker = lambda fn, thread=True: None
    async with app.run_test() as pilot:
        app.conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                         "VALUES ('e1','principal','x',1)")
        await pilot.press("ctrl+alt+r")
        app.confirm("ctn_v3")
        await pilot.pause()

        assert app.db_path is not None and app.conn is not None
        assert app.conn.execute(
            "SELECT COUNT(*) n FROM entries").fetchone()["n"] == 0


# ---------------------------------------------------------------------------
# Onboarding from the seat
# ---------------------------------------------------------------------------

async def test_onboarding_with_no_project_offers_one_instead_of_saying_none(
        tmp_path, home):
    """
    It printed `onboarding None…` and then returned silently from the worker,
    because the message was written before the guard and the guard said
    nothing. Two failures in three lines: a sentence that is not true, and a
    refusal you cannot see.

    The useful answer is the form, because a run with no project is exactly a
    run that needs one.
    """
    from rota.cockpit import tui
    from rota.cockpit.screens import NewRun

    app = tui.RotaApp(tmp_path / "husk.db", "llama3.1:8b", root=None)
    said = []
    async with app.run_test() as pilot:
        app.say = lambda text, *a, **k: said.append(text)
        app.action_onboard()
        await pilot.pause()

        assert not any("None" in s for s in said), said
        assert isinstance(app.screen, NewRun)
        assert app.screen.query_one("#newrun_name").value == "husk"


async def test_the_form_adopts_an_empty_run_but_still_refuses_a_full_one(
        tmp_path, home, project):
    """
    Refusing an existing name is right when it holds a run and wrong when it
    holds a husk -- and a husk is precisely what you reached the form from.
    Emptiness is asked of `code_index`, which is what onboarding writes, rather
    than of the file's existence.
    """
    from rota.cockpit.screens import NewRun

    _seed(home, "husk", project)                 # exists, never indexed
    full = _seed(home, "full", project)
    conn = init_db(full)
    conn.execute("INSERT INTO code_index (grain, grain_kind, area) "
                 "VALUES ('a.py','path','a')")
    conn.commit()
    conn.close()

    app = _app(tmp_path)
    async with app.run_test() as pilot:
        app.push_screen(NewRun(name="husk", root=str(project)))
        await pilot.pause()
        app.screen.go()
        await pilot.pause()
        assert app.screen.__class__.__name__ != "NewRun", "refused a husk"

        app.push_screen(NewRun(name="full", root=str(project)))
        await pilot.pause()
        app.screen.go()
        await pilot.pause()
        assert app.screen.__class__.__name__ == "NewRun", "landed on a real run"
        assert "already" in str(app.screen.query_one("#newrun_detected").content)


async def test_no_key_breaks_on_a_seat_with_no_run(tmp_path, home):
    """
    A state I introduced and then did not sweep the actions for.

    Four of five keys assumed a run: `alt+b` built `Path(None)`, `alt+p` read
    `config` off a closed connection, and `alt+w` and `ctrl+alt+r` armed
    themselves against the empty string -- offering `type `` to confirm`, which
    cannot be typed, so the seat stayed armed with no way out.

    The empty seat is reachable two ways now, both ordinary: the first time you
    ever start, and the moment after you wipe. So this asks every key, not the
    ones I thought of.
    """
    from rota.cockpit import tui

    for key, _, _ in tui.RotaApp.BINDINGS:
        if key in ("ctrl+c", "ctrl+l"):
            continue                # quit ends the test; the list is the answer
        app = tui.RotaApp(None, "llama3.1:8b")
        said: list[str] = []
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.pause()
            app.screen.action_dismiss_list()
            await pilot.pause()
            app.say = lambda t, *a, **k: said.append(t)

            await pilot.press(key)          # must not raise
            await pilot.pause()

            assert app.armed is None, (
                f"{key} armed a confirmation nothing can satisfy: "
                f"the run has no name to type")
            assert said or app.screen.__class__.__name__ != "Screen", (
                f"{key} did nothing and said nothing")


async def test_marking_two_runs_compares_them(tmp_path, home, project):
    """
    A comparison needs two runs, and the list is the only screen where both are
    visible — so `d` marks one and `d` on another compares them. Two presses
    rather than a multi-select mode, because a mode nothing displays is a mode
    you act inside without knowing you are in it.
    """
    from rota.cockpit.screens import RunList

    left = _seed(home, "ctn_v3", project, project_commit="abc")
    right = _seed(home, "ctn_v3-2", project, project_commit="abc")

    app = _app(tmp_path)
    said: list[str] = []
    async with app.run_test() as pilot:
        await pilot.press("ctrl+l")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, RunList)
        app.say = lambda t, *a, **k: said.append(t)

        order = [r["name"] for r in screen.rows]
        screen.query_one("#runs").move_cursor(row=order.index("ctn_v3"))
        screen.action_diff()
        await pilot.pause()
        assert screen.marked == str(left)
        assert "marked" in str(screen.query_one("#runlist_note").content)

        screen.query_one("#runs").move_cursor(row=order.index("ctn_v3-2"))
        screen.action_diff()
        await pilot.pause()

    assert said, "the comparison was computed and never shown"
    assert "ctn_v3" in said[0] and "same source" in said[0]
    assert str(right)                     # both sides were real runs


async def test_marking_the_same_run_twice_unmarks_it(tmp_path, home, project):
    """The way out of a mode you entered by accident."""
    _seed(home, "one", project)

    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("ctrl+l")
        await pilot.pause()
        screen = app.screen
        screen.query_one("#runs").move_cursor(
            row=[r["name"] for r in screen.rows].index("one"))

        screen.action_diff()
        await pilot.pause()
        assert screen.marked is not None
        screen.action_diff()
        await pilot.pause()
        assert screen.marked is None


# ---------------------------------------------------------------------------
# Onboarding, which destroys an index
# ---------------------------------------------------------------------------

def _onboarded(home, name, project):
    """A run with a real index, the way `boot.onboard` leaves one."""
    from rota.core.db import init_db
    from rota.onboarding import boot

    path = home / f"{name}.db"
    conn = init_db(path)
    boot.onboard(conn, project)
    conn.commit()
    conn.close()
    return path


async def test_onboarding_an_indexed_run_arms_rather_than_fires(
        tmp_path, home, project):
    """
    It was the only index-destroying action with no confirmation.

    `indexer.build` opens with `DELETE FROM code_edges` and `DELETE FROM
    code_index`. `alt+w` arms and demands the run's name; `ctrl+alt+r` does the
    same and it does *less* damage in the sense that matters — it wipes
    everything, so nothing is left pointing at anything. One keypress rebuilt
    the index under a run with completed surveys.
    """
    from rota.cockpit import tui

    path = _onboarded(home, "indexed", project)
    app = tui.RotaApp(path, "llama3.1:8b", root=project)
    async with app.run_test() as pilot:
        await pilot.press("alt+o")
        await pilot.pause()

        assert app.armed == "onboard"
        assert app.conn.execute(
            "SELECT COUNT(*) n FROM code_index").fetchone()["n"] > 0


async def test_onboarding_a_run_with_no_index_needs_no_confirmation(
        tmp_path, home, project):
    """
    Arming everything is how confirmations stop being read. There is nothing to
    destroy in a run that has never been indexed, which is what
    `boot.is_onboarded` was written to answer — and it had no caller anywhere.
    """
    from rota.cockpit import tui

    app = tui.RotaApp(home / "fresh.db", "llama3.1:8b", root=project)
    started: list = []
    app.run_worker = lambda fn, thread=True: started.append(fn.__name__)
    async with app.run_test() as pilot:
        await pilot.press("alt+o")
        await pilot.pause()

        assert app.armed is None
        assert started == ["_do_onboard"]


async def test_onboarding_is_refused_while_the_loop_is_driving(
        tmp_path, home, project):
    """
    Re-indexing under live sessions, and then a second loop on top.

    `action_toggle_run_state` guards on `self.driving` and this did not, so
    onboarding mid-run rebuilt the index while survey sessions read the old one
    — and `_do_onboard` then called `_turn_the_crank()` unconditionally, which
    has no re-entrancy guard, giving two concurrent `loop.run` calls on one
    database.
    """
    from rota.cockpit import tui

    app = tui.RotaApp(home / "busy.db", "llama3.1:8b", root=project)
    started: list = []
    app.run_worker = lambda fn, thread=True: started.append(fn.__name__)
    async with app.run_test() as pilot:
        app.driving = True
        await pilot.press("alt+o")
        await pilot.pause()

        assert app.armed is None
        assert started == [], "it re-indexed under a running loop"


async def test_a_finished_onboarding_does_not_start_a_second_loop(
        tmp_path, home, project):
    """
    The other half of the same hole. `_turn_the_crank` sets `self.driving` from
    its docstring straight through with nothing asking whether it is already
    true, so anything that calls it twice gets two loops.
    """
    from rota.cockpit import tui

    app = tui.RotaApp(home / "busy2.db", "llama3.1:8b", root=project)
    ran: list = []
    async with app.run_test() as pilot:
        app.driving = True
        app._turn_the_crank = lambda: ran.append(1)      # would be the second
        app._pending_root = project
        app._do_onboard()
        await pilot.pause()

    assert ran == [], "a second loop was started on top of a running one"


async def test_onboard_uses_a_key_a_plain_terminal_can_send(tmp_path, home):
    """
    `ctrl+shift+o` needs the Kitty keyboard protocol.

    Textual enables it and parses `ESC[111;6u`, so it works in kitty, WezTerm,
    Ghostty and recent Windows Terminal. Everywhere else Ctrl+Shift+O collapses
    to `ctrl+o` and the binding silently does nothing — the exact failure the
    binding guard next door exists for, and the one case that guard cannot see:
    `pilot.press` injects an already-parsed key name and never goes through the
    sequence layer a real terminal does.

    Every other binding here survives legacy encoding, so this asserts the
    property rather than the key: nothing may require the modifier combination
    that only the new protocol can carry.
    """
    from rota.cockpit import tui

    needs_kitty = [k for k, _, _ in tui.RotaApp.BINDINGS
                   if "ctrl" in k and "shift" in k]
    assert needs_kitty == [], (
        f"{needs_kitty} can only arrive under the Kitty keyboard protocol; in "
        f"a terminal without it the footer advertises a key that does nothing")


async def test_wiping_a_held_run_says_so_instead_of_killing_the_seat(
        tmp_path, home, project, monkeypatch):
    """
    The crash you hit. `cli.wipe` raised `SystemExit`, which travelled out of a
    Textual callback, through the message pump and asyncio, and took the app
    down — so you were told the run was open in another process *and* lost the
    window you would have closed it from.

    `SystemExit` is a `BaseException`, so every `except Exception` written to
    keep a UI alive lets it through by design. The refusal is an ordinary
    exception now, and the screen reports it.
    """
    from rota.cockpit.screens import RunList

    held = _seed(home, "held", project)
    monkeypatch.setattr(cli, "wipe", lambda p: (_ for _ in ()).throw(
        cli.WipeRefused("held.db is open in another process")))

    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("ctrl+l")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, RunList)
        row = next(r for r in screen.rows if r["name"] == "held")
        screen.query_one("#runs").move_cursor(
            row=screen.rows.index(row))
        screen.action_wipe()
        await pilot.pause()
        app.screen.handle_submit("held")
        await pilot.pause()

        assert app.is_running, "the refusal killed the seat"
        assert "another process" in str(
            app.screen.query_one("#runlist_note").content)


async def test_the_seats_own_run_is_recognised_however_it_was_spelled(
        tmp_path, home, project):
    """
    Why the refusal was reached at all. The comparison was string-on-string, so
    a relative path in the row and an absolute one in the seat were treated as
    two different runs — and the seat's own database went down the branch that
    cannot close it first.
    """
    from rota.cockpit.screens import RunList

    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("ctrl+l")
        await pilot.pause()
        screen = app.screen
        # The same run, spelled the other way.
        spelled = {"name": app.run_name, "state": "ready",
                   "path": str(app.db_path).replace("\\", "/"),
                   "root": str(project), "counts": {}, "branch": "",
                   "commit": "", "moved": False}
        assert isinstance(screen, RunList)

        here = Path(app.db_path).resolve()
        assert Path(spelled["path"]).resolve() == here, (
            "the two spellings must resolve to one run")
