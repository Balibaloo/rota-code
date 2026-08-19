"""
Talking to rota, with the roles' work visible while it happens.

    python -m rota.cockpit.tui --db run.db

Built from the existing TUI's widgets rather than beside them: `ChatMessage` is
the same bubble the chat app uses, and `Collapsible` is the same disclosure. The
point of reuse here is not saving work -- it is that a session's tool calls and
an assistant turn are the same *kind* of thing to look at, and giving them two
appearances would be a claim that they are not.

Two panes, because there are two things happening and only one of them is a
conversation.

**Left: what you and Liaison said.** Your sentence, and every question that
comes back. This is the whole of the principal's interface -- words out, words
in, plus approve, contest and defer.

**Right: what the system owes.** `predicates.outstanding()`, refreshed after
every session. Sixteen register predicates folded into one list: an obligation,
who owns discharging it, and what it is about. This is the pane that did not
exist in any form until today, and it is the one worth watching -- the roles'
sessions scroll past and are gone, and what is *outstanding* is the state.

The loop runs in a worker thread. Everything it does lands through
`call_from_thread`, so the widget tree is only ever touched from one place.
"""
from __future__ import annotations

import argparse
import sqlite3
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Input, Static

# Run as a file, not as a module: `python rota/cockpit/tui.py` is what a person
# types, and relative imports die on it with a traceback that names none of the
# three ways to fix it. Re-enter as the module instead, from the repository root
# put on the path. An entry point is the one place worth this, because it is the
# only file whose reader has not read the file.
if __package__ in (None, ""):                              # pragma: no cover
    import runpy
    import sys as _sys
    from pathlib import Path as _Path

    _sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))
    runpy.run_module("rota.cockpit.tui", run_name="__main__")
    raise SystemExit(0)


from .. import cli, paths
from ..core import config, loop as loop_mod
from ..core.db import connect, init_db
from ..core.predicates import outstanding
from ..llm import llm
from ..onboarding import boot
from ..roles.principal import Answer, Ask, pending_replies
from ..tools.talk import open_with

# The repo root again, for the chat app's widgets, which live outside the
# package. Taken from the anchor rather than counted out of this module's own
# path a second time: by here `rota` is imported and `paths` is the thing that
# knows where it is. The shim above is the one place that cannot ask it,
# because it runs before there is a package to ask.
sys.path.insert(0, str(paths.REPO))
from src.ui.widgets import ChatMessage                      # noqa: E402


def _now() -> str:
    return datetime.now().strftime("%H:%M:%S")


class QueuedPrincipal:
    """
    The principal, answering from the UI instead of from stdin.

    Same protocol as `ConsolePrincipal` and `ScriptedPrincipal` -- receive
    confirm/clarify/present, emit converse/verdict, defer by returning None. The
    seam was built so a backend could be a person, a script or a widget without
    any of them knowing about the others, and this is the third one.

    Deferral is the default and costs nothing: an unanswered ask stays open and
    comes back on the agenda, so a principal who is reading rather than
    answering does not block the loop.
    """

    name = "queued"

    def __init__(self, app: "RotaApp") -> None:
        self.app = app
        self.pending: list[Ask] = []
        self.answers: dict[str, Answer] = {}
        self._lock = threading.Lock()

    def respond(self, ask: Ask) -> Answer | None:
        with self._lock:
            answer = self.answers.pop(ask.message_id, None)
            known = any(p.message_id == ask.message_id for p in self.pending)
            if answer is None and not known:
                self.pending.append(ask)
        if answer is not None:
            with self._lock:
                self.pending = [p for p in self.pending
                                if p.message_id != ask.message_id]
            return answer
        if not known:
            self.app.call_from_thread(self.app.show_ask, ask)
        return None                       # deferred until the UI answers

    def submit(self, text: str) -> Ask | None:
        """Turn the user's reply to the oldest visible ask into an Answer."""
        with self._lock:
            ask = self.pending[0] if self.pending else None
            if ask is None:
                return None
            self.answers[ask.message_id] = self._answer_for(ask, text)
        return ask

    @staticmethod
    def _answer_for(ask: Ask, text: str) -> Answer:
        raw = text.strip()
        if ask.verb in ("confirm", "present"):
            if raw.lower() in ("lgtm", "ok", "yes", "approve", "approved"):
                return Answer(verb="verdict",
                              per_item={ref: "approve" for ref in ask.refs})
            per_item = {}
            for part in raw.replace(",", " ").split():
                if "=" in part:
                    ref, ruling = part.split("=", 1)
                elif ":" in part:
                    ref, ruling = part.split(":", 1)
                else:
                    continue
                if ref in ask.refs and ruling in ("approve", "contest", "revise"):
                    per_item[ref] = ruling
            if not per_item:
                raise ValueError(
                    "reply with 'lgtm' or rulings such as 's1=approve'")
            return Answer(verb="verdict", per_item=per_item)
        return Answer(verb="converse", text=raw)


class Outstanding(Static):
    """What the system owes, folded from the register."""

    def render_rows(self, conn: sqlite3.Connection) -> None:
        rows = outstanding(conn)
        if not rows:
            self.update("[dim]nothing outstanding[/dim]")
            return
        lines = []
        for r in rows:
            if r.get("error"):
                lines.append(f"[red]{r['obligation']}[/red]  {r['error']}")
                continue
            who = ", ".join(r["owners"]) or "—"
            refs = " ".join(r["refs"][:3])
            lines.append(f"[b]{r['obligation']}[/b] ×{r['count']}  "
                         f"[dim]{who}[/dim]\n  [dim]{refs}[/dim]")
        self.update("\n".join(lines))


class RotaApp(App):
    """The principal's seat."""

    CSS = """
    #conversation { width: 2fr; padding: 0 1; }
    #sidebar { width: 1fr; border-left: solid $accent; padding: 0 1; }
    #sessions { height: 40%; border-top: solid $accent; padding: 0 1; }
    Input { dock: bottom; }

    /* `#confirmation_container` had no rule anywhere in the repository, while
       both its siblings in `src/ui/modals.py` carry the same four. So the
       confirm dialog rendered as a bare label and two buttons over the dimmed
       backdrop -- which looks like the modal failing to appear, and quit is the
       worst place to learn that. */
    #confirmation_container, #runlist_container, #newrun_container {
        background: $surface;
        border: thick $accent;
        padding: 1 2;
        width: auto;
        height: auto;
    }
    #runlist_container { width: 90%; height: 80%; }
    #runs { height: 1fr; }
    #runlist_title, #newrun_title { text-style: bold; }
    #runlist_note, #newrun_detected { color: $text-muted; }
    #newrun_container { width: 70; }
    #newrun_container Input { dock: none; width: 100%; }
    """
    BINDINGS = [
        ("ctrl+shift+o", "onboard", "onboard"),
        ("alt+p", "toggle_run_state", "pause / resume"),
        # `alt+`, not `ctrl+`, and not by taste. The input has the focus
        # whenever you are sitting here, and a widget binding beats an app one:
        # `ctrl+w` is its delete-word and `ctrl+u`, `ctrl+k`, `ctrl+x` and
        # `ctrl+a` are equally spoken for. A binding the input eats is a
        # binding the footer advertises and nothing performs, which is why
        # `test_every_binding_survives_the_input_having_focus` exists.
        ("ctrl+l", "runs", "runs"),
        ("ctrl+alt+r", "rerun", "rerun over the top"),
        ("alt+w", "wipe", "wipe"),
        ("alt+b", "cockpit", "cockpit"),
        ("ctrl+c", "request_quit", "quit"),
    ]

    def __init__(self, db_path: Path, model: str, root: Path | None = None) -> None:
        super().__init__()
        self.db_path = Path(db_path)
        self.model = model
        # **No default.** It used to be `root or Path.cwd()`, which is the same
        # shape `worktrees.project_root` refuses by name: a run opened without a
        # project would reindex whichever repository the process was started
        # from, and a rerun would do it over the top of a wipe. A missing root
        # is a thing to say, not a thing to guess.
        self.root = Path(root) if root else None
        self.conn = init_db(self.db_path)
        # And if it was not passed, ask the run. `project_root` has been in
        # `config` since onboarding wrote it and nothing downstream read it
        # back, so the root was supplied twice and the two could disagree.
        # Derived beats declared here for the usual reason: there is no second
        # copy to be wrong.
        #
        # Read with plain SQL, not `config.get`: `project_root` is not a
        # declared setting — the principal does not own it, onboarding writes
        # it — so `config.get` would raise `UnknownSetting`, and the value is a
        # bare path rather than JSON. `worktrees.project_root` reads it exactly
        # this way, and this is the one place that may find it absent.
        if self.root is None:
            row = self.conn.execute(
                "SELECT value FROM config WHERE key = 'project_root'").fetchone()
            if row and (row["value"] or "").strip():
                self.root = Path(row["value"].strip().strip('"'))
        # **Read `run_state`; never impose it.** This wrote `"stopping"` on
        # every open, and `loop.step` reads that value every session -- so
        # opening a second seat silently halted the loop the first was driving,
        # while the first went on displaying `running` because it refreshes
        # that label on mount and on the pause key, never on a timer.
        #
        # A fresh seat starting idle is a fact about *the seat*, and it is held
        # as one: `self.driving` below. The run's state belongs to the run.
        self.principal = QueuedPrincipal(self)
        self.driving = False
        self.started = False
        self._pending_text = ""
        self._pending_root: Path | None = None
        self._pending_new: tuple[Path, Path] | None = None
        # What a destructive key has armed, and nothing else. `None` is the
        # ordinary state and the state a confirmation returns to either way.
        self.armed: str | None = None

    @property
    def run_name(self) -> str:
        """A run is its file's stem, the same identity `rota ls` prints."""
        return self.db_path.stem

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield VerticalScroll(id="conversation")
            with Vertical(id="sidebar"):
                yield Static("[b]outstanding[/b]")
                yield Static(id="run_state")
                yield Outstanding(id="owed")
                yield Static("[b]sessions[/b]", id="sessions_title")
                yield VerticalScroll(id="sessions")
        yield Input(placeholder="say what you want built…")
        yield Footer()

    def on_mount(self) -> None:
        self.retitle()
        self.refresh_run_state()
        self.refresh_owed()

    def retitle(self) -> None:
        """
        The run first, the project second.

        It used to be `rota — <project> — <model>`, which names everything
        except the thing you are about to wipe. Two runs against one checkout is
        the normal case — a branch against its main is the comparison the answer
        key exists for — so the project alone does not say which is on screen.
        """
        self.title = f"rota — {self.run_name}"
        self.sub_title = f"{self.root.name if self.root else 'no project'} — {self.model}"

    # -- the two things the worker thread is allowed to do -------------------

    def _from_worker(self, fn, *args) -> None:
        """
        Touch the widget tree from the loop thread, or do not touch it at all.

        `call_from_thread` raises `RuntimeError("App is not running")` outside a
        running app, and the loop outlives the app in two ordinary cases: the
        window is closed mid-session, and a test drives `_turn_the_crank`
        directly to check the threading. Neither is an error, and neither should
        surface as a thread exception nobody catches — there is simply no
        screen left to update.
        """
        if not self.is_running:
            return
        try:
            self.call_from_thread(fn, *args)
        except RuntimeError:
            pass                      # the app exited between the check and the call

    def say(self, text: str, sender: str, colour: str = "blue") -> None:
        pane = self.query_one("#conversation", VerticalScroll)
        pane.mount(ChatMessage(text, sender, _now(), border_color=colour))
        pane.scroll_end(animate=False)

    # A long run is dozens of sessions and the pane held every one of them, which
    # is a leak that looks like a feature until the fortieth. Bounded, and the
    # bound is not a loss: what happened is in the database, and what is
    # *outstanding* is the pane beside it. This one is a ticker.
    SESSION_LINES = 30

    def note_step(self, line: str) -> None:
        pane = self.query_one("#sessions", VerticalScroll)
        pane.mount(Static(line))
        extra = len(pane.children) - self.SESSION_LINES
        for old in list(pane.children)[:max(extra, 0)]:
            old.remove()
        pane.scroll_end(animate=False)
        self.show_replies()
        self.refresh_owed()

    def show_ask(self, ask: Ask) -> None:
        body = ask.rendered or "\n".join(f"- {r}" for r in ask.refs)
        self.say(f"**{ask.verb}**\n\n{body}", "liaison", "magenta")

    def show_replies(self) -> None:
        """Display Liaison conversational replies and mark them shown."""
        for ask in pending_replies(self.conn):
            self.say(ask.rendered or "", "liaison", "magenta")
            self.conn.execute(
                "UPDATE messages SET status = 'answered' WHERE id = ?",
                (ask.message_id,))

    def refresh_run_state(self) -> None:
        """
        Two facts, because they are two facts and one label was showing them as
        one.

        `run_state` is the *run's* — whether the principal has halted it — and
        it is shared by every seat and read by `loop.step`. Whether this window
        is currently turning the crank is the *seat's*, and nothing recorded it
        at all. Showing only the first meant `running` appeared over a seat that
        was doing nothing, and the fix for that used to be writing `stopping`
        into the run on open, which stopped anybody else's loop.
        """
        state = config.get(self.conn, "run_state")
        here = "driving" if self.driving else "idle"
        self.query_one("#run_state", Static).update(
            f"[b]run:[/b] {state}   [b]this seat:[/b] {here}")

    def refresh_owed(self) -> None:
        self.query_one("#owed", Outstanding).render_rows(self.conn)

    def action_toggle_run_state(self) -> None:
        """
        Play and pause, which is a question about *this seat*, not about the run.

        It used to flip `run_state` and start a worker on the way up. That was
        only ever coherent because the seat wrote `stopping` into the run when
        it opened, so the flag and the seat's idleness could not disagree.
        Without that write they can, and the toggle read the wrong one: on a
        fresh run — whose `run_state` defaults to `running` — pressing play
        would *pause* it.

        So it asks whether this window is driving. Stopping still sets the run's
        flag, because that is the only way to reach a loop already inside
        `loop.run`, and it is what the flag is for.
        """
        if self.driving:
            config.stop(self.conn)
            self.say("stopping — the current session finishes first",
                     "system", "blue")
        else:
            config.resume(self.conn)
            self.say("running", "system", "blue")
            self.run_worker(self._turn_the_crank, thread=True)
        self.refresh_run_state()

    # -- arming, and the one thing that fires ---------------------------------

    def arm(self, what: str, consequence: str) -> None:
        """
        A destructive key does not do the destructive thing.

        The confirmation is typing the run's name into the input you are
        already in, which is the rule `rota wipe` uses at the command line. It
        reuses the widget tree rather than introducing a modal screen, and it
        costs the one thing a modal cannot: you have to know which run you are
        in, which is exactly the mistake being guarded against.
        """
        self.armed = what
        self.say(f"**{what}** — {consequence}\n\n"
                 f"type `{self.run_name}` to confirm, anything else to cancel",
                 "system", "yellow")
        self.query_one(Input).placeholder = f"type {self.run_name} to confirm…"

    def confirm(self, text: str) -> None:
        """
        One chance, then it is an ordinary line again.

        A prompt that stays open until you get it right turns the next
        unrelated sentence into a confirmation, which is a worse failure than
        making you press the key twice.
        """
        what, self.armed = self.armed, None
        self.query_one(Input).placeholder = "say what you want built…"
        if text.strip() != self.run_name:
            self.say(f"{what} cancelled", "system", "blue")
            return
        if what == "rerun" and self.root is None:
            self.say("no project to rerun against: reopen with a root, or "
                     "`rota onboard <name> --root <checkout>`", "system", "red")
            return

        removed = self.wipe_run()
        self.say(f"wiped {self.run_name}: {len(removed['worktrees'])} worktree(s), "
                 f"{len(removed['pids'])} process(es)", "system", "blue")
        if what == "rerun":
            self._pending_root = self.root
            self.say(f"onboarding {self.root}…", "system", "blue")
            self.run_worker(self._do_onboard, thread=True)

    def wipe_run(self) -> dict:
        """
        Close, wipe, reopen. The order is the whole of it.

        The app holds the database open and Windows will not unlink an open
        file, so a wipe that does not close first does not fail — it reports
        what it meant to do and removes nothing, which is the shape of failure
        this system keeps having to be taught to refuse.

        Reopening is what makes the seat sittable afterwards. A wiped run that
        leaves you looking at a dead connection is a restart wearing a button.
        """
        from ..cli import wipe as wipe_path

        self.conn.close()
        removed = wipe_path(self.db_path)
        self.conn = init_db(self.db_path)
        self.principal = QueuedPrincipal(self)
        self.driving = False
        self.started = False
        self.refresh_run_state()
        self.refresh_owed()
        return removed

    def action_wipe(self) -> None:
        self.arm("wipe", "its worktrees, its recorded processes, and the file")

    def action_rerun(self) -> None:
        self.arm("rerun", f"wipe, then index {self.root or 'nothing'} again")

    # -- the level above one run ---------------------------------------------

    def action_runs(self) -> None:
        from .screens import RunList

        self.push_screen(RunList(), self._from_run_list)

    def _from_run_list(self, result) -> None:
        if not result:
            return
        verb, *rest = result
        if verb == "open":
            self.open_run(Path(rest[0]["path"]))
        elif verb == "onboard":
            name, root = rest
            self._pending_new = (cli.resolve(name), Path(root))
            self.say(f"onboarding {root} as {name}…", "system", "blue")
            self.run_worker(self._do_new_run, thread=True)

    def _do_new_run(self) -> None:
        path, root = self._pending_new
        self._pending_new = None
        try:
            report = cli.onboard(path, root)
        except Exception as exc:                                # noqa: BLE001
            self.call_from_thread(self.say, f"onboarding failed: {exc}",
                                  "system", "red")
            return
        self.call_from_thread(
            self.say, f"{path.stem}: {report.areas} areas, {report.unsurveyed} "
                      f"under constraint zero", "system", "blue")
        # Land in what you just made. Creating a run and then having to go and
        # find it is the friction this screen exists to remove.
        self.call_from_thread(self.open_run, path)

    def open_run(self, path: Path) -> None:
        """
        Point this seat at a different run.

        Switching is the app rebinding its own database rather than a restart,
        which is what makes "look at that one instead" cheap enough to do while
        thinking. The conversation pane is cleared because it belongs to the run
        that was open, and showing one run's words above another's register
        would be the one thing this screen exists to prevent.
        """
        if self.conn is not None:
            self.conn.close()
        self.db_path = Path(path)
        self.conn = init_db(self.db_path)
        self.root = None
        row = self.conn.execute(
            "SELECT value FROM config WHERE key = 'project_root'").fetchone()
        if row and (row["value"] or "").strip():
            self.root = Path(row["value"].strip().strip('"'))
        self.principal = QueuedPrincipal(self)
        self.started = False
        self.armed = None
        self.query_one("#conversation", VerticalScroll).remove_children()
        self.query_one("#sessions", VerticalScroll).remove_children()
        self.retitle()
        self.refresh_run_state()
        self.refresh_owed()
        self.say(f"opened {self.run_name}"
                 + (f" — {self.root}" if self.root else ""), "system", "blue")

    # -- leaving ---------------------------------------------------------------

    def action_request_quit(self) -> None:
        """
        Quitting stops the run, so it asks first.

        Cheap to resume — the frontier *is* the state, so there is nothing to
        lose but the time a session takes — and still never something to do by
        accident forty sessions in. The confirmation has to be able to say no,
        which is why the quit happens in the callback rather than beside it.
        """
        from src.ui.modals import ConfirmationModal

        def answered(confirmed: bool) -> None:
            if confirmed:
                self.exit()

        running = config.get(self.conn, "run_state") == "running"
        self.push_screen(ConfirmationModal(
            f"Quit {self.run_name}?" + (
                "  The run is running and will stop." if running else
                "  Nothing is running."),
            callback=answered))

    def action_cockpit(self) -> None:
        """
        Depth, in a browser, on *this* run.

        The register answers what is owed. It cannot answer what a role was
        shown or what caused a message, and those two are what a stuck run
        turns out to be about — so the cockpit is one keystroke away rather
        than a path to remember. The database is passed by path because a run
        is not identified by its project: several are about the same one.
        """
        self.open_cockpit(self.db_path)

    def open_cockpit(self, db_path: Path) -> None:
        """Also called from the run list, on whichever run the cursor is on."""
        argv = [sys.executable, "-m", "rota", "cockpit", str(db_path), "--open"]
        try:
            subprocess.Popen(argv)
        except OSError as exc:                                  # noqa: BLE001
            self.say(f"could not start the cockpit: {exc}", "system", "red")
            return
        self.say(f"cockpit starting for {Path(db_path).stem} at "
                 f"http://127.0.0.1:8899/", "system", "blue")

    # -- input ---------------------------------------------------------------

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return
        event.input.value = ""

        if self.armed:
            self.confirm(text)
            return

        self.say(text, "you", "green")
        self.started = True
        try:
            ask = self.principal.submit(text)
        except ValueError as exc:
            self.say(str(exc), "system", "red")
            return
        if ask is None:
            # No gate is open, so the user's sentence is a new chat turn to
            # Liaison rather than an answer to a question.
            # Use the worker connection so ids are counted after the worker's
            # own commits; the UI connection may lag uncommitted state.
            self._pending_text = text
            self.run_worker(self._open_then_turn, thread=True)
        else:
            self.run_worker(self._turn_the_crank, thread=True)

    def _open_then_turn(self) -> None:
        """Write the follow-up message from the worker thread, then run."""
        text = self._pending_text
        del self._pending_text
        conn = connect(self.db_path)
        try:
            open_with(conn, text)
        finally:
            conn.close()
        self._turn_the_crank()

    def action_onboard(self) -> None:
        """Start onboarding the root currently shown in the title bar."""
        root = self.root
        self.say(f"onboarding {root}…", "system", "blue")
        self._pending_root = root
        self.run_worker(self._do_onboard, thread=True)

    def _do_onboard(self) -> None:
        """Index the codebase and put every area under constraint zero."""
        root = self._pending_root
        self._pending_root = None
        if root is None:
            return
        conn = connect(self.db_path)
        try:
            report = boot.onboard(conn, root)
            conn.commit()
            self.call_from_thread(
                self.say,
                f"onboarded {root}: {report.areas} areas, "
                f"{report.unsurveyed} under constraint zero",
                "system", "blue")
            # Mechanical onboarding only prepares survey wakes. Continue into
            # the ordinary loop so the cockpit immediately shows the roles
            # studying the selected root.
            self._turn_the_crank()
        except Exception as exc:                            # noqa: BLE001
            self.call_from_thread(
                self.say, f"onboarding failed: {exc}", "system", "red")
        finally:
            conn.close()
        self.call_from_thread(self.refresh_owed)

    def _turn_the_crank(self) -> None:
        """
        The loop, on a connection this thread owns.

        `db.connect` does not pass `check_same_thread=False`, and should not: a
        connection shared across threads by default is a race nobody declared.
        So the worker opens its own rather than borrowing the one the sidebar
        and intake use, and the two see each other because the connections are
        autocommit and talking to the same file.

        Shipped without this and the first message died on
        "SQLite objects created in a thread can only be used in that same
        thread". Every test here claimed to cover the joins, and this is the
        join I did not cover: the thread boundary.
        """
        def on_step(step) -> None:
            self.call_from_thread(self.note_step, f"· {step}"[:120])

        self.driving = True
        self._from_worker(self.refresh_run_state)
        try:
            loop_mod.run(
                connect(self.db_path),
                backend=llm.OllamaBackend(),
                pins=llm.Pins(model=self.model, temperature=0.0),
                principal=self.principal,
                max_steps=40,
                on_step=on_step,
            )
        except Exception as exc:                            # noqa: BLE001
            self.call_from_thread(self.say, f"loop stopped: {exc}", "system", "red")
        finally:
            # In `finally` because "this seat is driving" must go false on the
            # error path too. A label that sticks on `driving` after the loop
            # died is the same lie the old one told, arrived at differently.
            self.driving = False
            self._from_worker(self.refresh_run_state)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="rota, with a face")
    ap.add_argument("--db", default=".rota/rota.db")
    ap.add_argument("--model", default=llm.DEFAULT_MODEL)
    # No default. The working directory is *this* repository, and a rerun
    # against it would index the framework over the top of the wiped run it was
    # meant to redo. Omitted, the root comes from the database, which is the
    # only place that actually knows.
    ap.add_argument("--root", type=Path, default=None,
                    help="project root; omit to use the one the run records")
    args = ap.parse_args(argv)
    RotaApp(Path(args.db), args.model, root=args.root).run()
    return 0


if __name__ == "__main__":                                 # pragma: no cover
    sys.exit(main())
