"""
The TUI as the thing you drive, not just the thing you talk to.

It could already onboard, pause and resume. What it could not do is the loop
that an evaluation actually consists of -- **run, look, wipe, run again** --
which meant leaving it, remembering a path, typing a module name, and coming
back. Four steps of friction on the one action you take most.

Three things are added here and each has a reason it is *here* rather than in
the CLI.

**The run has a name in the title.** The window said `rota — <root> — <model>`,
which is the project and not the run, and two runs against the same checkout is
the normal case rather than an odd one. A face that cannot tell you which of
them you are looking at is where a wipe goes to the wrong one.

**A destructive key is armed, not fired.** `alt+w` does not wipe. It arms, and
the confirmation is typing the run's name into the input you are already in --
the same rule the CLI uses, for the same reason, and it reuses the widget tree
rather than introducing a modal that would need its own tests.

**A wipe closes the connection first.** The app holds the database open, and on
Windows an open file cannot be unlinked. The failure mode without this is not a
crash; it is a wipe that reports success and removes nothing.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from rota.core.db import init_db


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    (root / "pkg").mkdir(parents=True)
    (root / "pkg" / "thing.py").write_text("def go():\n    return 1\n")
    return root


def _app(tmp_path, project, name="ctn_v3"):
    from rota.cockpit import tui

    return tui.RotaApp(tmp_path / f"{name}.db", "llama3.1:8b", root=project)


# ---------------------------------------------------------------------------
# Which run am I in
# ---------------------------------------------------------------------------

async def test_the_title_names_the_run_and_not_only_the_project(tmp_path, project):
    """
    Two runs against one checkout is the normal case -- a branch and its main
    is the comparison the answer key exists for -- so the project alone does
    not identify what is on screen.
    """
    app = _app(tmp_path, project)
    async with app.run_test():
        assert "ctn_v3" in app.title
        assert project.name in app.sub_title


# ---------------------------------------------------------------------------
# Wiping, from the seat
# ---------------------------------------------------------------------------

async def test_the_wipe_key_arms_and_does_not_wipe(tmp_path, project):
    """A destructive action one keystroke deep is a destructive action."""
    app = _app(tmp_path, project)
    async with app.run_test() as pilot:
        await pilot.press("alt+w")
        assert app.armed == "wipe"
        assert app.db_path.exists(), "armed is not fired"


async def test_typing_the_name_wipes_and_leaves_a_usable_app(tmp_path, project):
    """
    The connection goes first. An open SQLite file cannot be unlinked on
    Windows, and the failure that produces is silent: the wipe reports what it
    meant to do and the file is still there.
    """
    app = _app(tmp_path, project)
    async with app.run_test() as pilot:
        app.conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                         "VALUES ('e1','principal','something',1)")
        await pilot.press("alt+w")
        app.confirm("ctn_v3")

        # Gone, and rebuilt: the seat is still sittable afterwards.
        assert app.armed is None
        assert app.conn.execute(
            "SELECT COUNT(*) n FROM entries").fetchone()["n"] == 0


async def test_a_wrong_confirmation_disarms_rather_than_retrying(tmp_path, project):
    """
    A prompt that stays open until you get it right turns the next unrelated
    sentence into a confirmation. One chance, then it is an ordinary line
    again.
    """
    app = _app(tmp_path, project)
    async with app.run_test() as pilot:
        app.conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                         "VALUES ('e1','principal','something',1)")
        await pilot.press("alt+w")
        app.confirm("yes")

        assert app.armed is None
        assert app.conn.execute(
            "SELECT COUNT(*) n FROM entries").fetchone()["n"] == 1


# ---------------------------------------------------------------------------
# Rerunning
# ---------------------------------------------------------------------------

async def test_rerun_is_wipe_then_onboard_then_crank(tmp_path, project):
    """
    The order is the whole content of the action. Onboarding an already
    onboarded database indexes on top of itself, which is not a rerun -- it is
    the previous run plus a second opinion about the same files.
    """
    app = _app(tmp_path, project)
    order: list[str] = []
    app.run_worker = lambda fn, thread=True: order.append(fn.__name__)

    async with app.run_test() as pilot:
        app.conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                         "VALUES ('e1','principal','something',1)")
        await pilot.press("alt+r")
        app.confirm("ctn_v3")

        assert app.conn.execute(
            "SELECT COUNT(*) n FROM entries").fetchone()["n"] == 0
        assert order == ["_do_onboard"]
        assert app._pending_root == project


async def test_rerun_needs_a_project_to_rerun_against(tmp_path):
    """
    `--root` defaults to the working directory, so a run opened without one
    would happily reindex *this* repository over the top of the wipe. Refuse
    what cannot be a rerun.
    """
    from rota.cockpit import tui

    app = tui.RotaApp(tmp_path / "ctn_v3.db", "llama3.1:8b", root=None)
    async with app.run_test() as pilot:
        await pilot.press("alt+r")
        assert app.armed == "rerun"
        app.confirm("ctn_v3")
        assert app.db_path.exists()


# ---------------------------------------------------------------------------
# Depth, when the register is not enough
# ---------------------------------------------------------------------------

async def test_the_cockpit_key_opens_this_run_and_no_other(tmp_path, project, monkeypatch):
    """
    The register answers "what is owed". It cannot answer "what was that role
    shown" or "what caused this" -- those are the prompt and the causal chain,
    and they are the cockpit's. Handing it the path rather than a project root
    is the fix that made a named run viewable at all.
    """
    from rota.cockpit import tui

    calls = []
    monkeypatch.setattr(tui.subprocess, "Popen", lambda argv, **kw: calls.append(argv))

    app = _app(tmp_path, project)
    async with app.run_test() as pilot:
        await pilot.press("alt+b")

    assert calls, "nothing was launched"
    assert str(app.db_path) in calls[0]
    assert "cockpit" in calls[0]


async def test_every_binding_survives_the_input_having_focus(tmp_path, project):
    """
    A key the input eats is a key the footer advertises and nothing performs.

    `ctrl+w` was the first spelling of the wipe binding and it did nothing at
    all: the input has the focus the whole time you are sitting here, a widget
    binding beats an app one, and `ctrl+w` is its delete-word. Nothing failed --
    the footer offered it, the key was pressed, and the action was never
    called, which is the same silent shape as a cockpit booting a database it
    could not find.

    So the check is not "is this key free today" but "does every key this app
    claims still arrive", asked of the real widget tree.
    """
    from textual.widgets import Input

    app = _app(tmp_path, project)
    fired = []
    async with app.run_test() as pilot:
        assert isinstance(app.focused, Input), "the input holds the focus"
        for key, action, _ in app.BINDINGS:
            if action == "quit":
                continue                     # would end the test, not the point
            setattr(app, f"action_{action}",
                    lambda action=action: fired.append(action))
            await pilot.press(key)

    claimed = [a for _, a, _ in app.BINDINGS if a != "quit"]
    assert fired == claimed, f"swallowed: {sorted(set(claimed) - set(fired))}"
