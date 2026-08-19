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
    /* **Scoped to the seat's own input.** Bare `Input` reached every input in
       the app, including the one inside the shared `InputModal` -- docking it
       to the bottom of the *screen*, outside the dialog box that was supposed
       to contain it. So the wipe confirmation showed a label and two buttons
       with its text box somewhere else entirely, and what you typed went
       nowhere the modal could read. I scoped this for `#newrun_container` when
       I wrote that form and did not go back for the modal I had reused. */
    #say { dock: bottom; }
    #input_modal_container Input, #modal_input { dock: none; width: 100%; }
    #input_modal_container {
        background: $surface;
        border: thick $accent;
        padding: 1 2;
        width: 70;
        height: auto;
    }

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

    def __init__(self, db_path: Path | None, model: str,
                 root: Path | None = None) -> None:
        super().__init__()
        # **A seat with no run is a legal state**, and it is the one you are in
        # the first time you ever start this. Without it the run list was
        # reachable only from inside a run, so creating your first one was a
        # command — which is the exact trip to the terminal the list exists to
        # remove, surviving in the one case where it is least excusable.
        self.db_path = Path(db_path) if db_path else None
        if self.db_path is None:
            self.model = model
            self.root = None
            self.conn = None
            self._init_seat_state()
            return
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
        self._init_seat_state()

    def _init_seat_state(self) -> None:
        """Everything that belongs to the seat rather than to the run it holds.

        Called on construction and again on every switch, which is what makes
        `open_run` a rebinding rather than a restart: the seat's idleness, its
        pending question, and how long since anything was written are all about
        *this window looking at that run*, and none of them survives a change of
        run.
        """
        self.principal = QueuedPrincipal(self)
        self.driving = False
        # Watched rather than logged. A session that changed nothing is the
        # signal, and `Step.productive` has always said so — nothing was
        # reading it, so a run that had stopped getting anywhere looked exactly
        # like one that was working.
        self.last_productive: float | None = None
        self.barren_since = 0
        self.started = False
        self._pending_text = ""
        self._pending_root: Path | None = None
        self._pending_new: tuple[Path, Path] | None = None
        # Servers this seat started, kept so they can be stopped. A spawned
        # process with nothing holding it is the orphan `ENVIRONMENT.md` is
        # written about; holding the handle is what makes stopping it provable
        # rather than a port scan that might hit somebody else's.
        #
        # **Preserved across a run switch**, unlike everything else here, which
        # is why it reads its own previous value. A cockpit belongs to the seat
        # that started it and not to the run that was open at the time —
        # switching runs must not orphan one, and must not close a window you
        # are still reading.
        self.cockpits: list[tuple[subprocess.Popen, object]] = getattr(
            self, "cockpits", [])
        # What a destructive key has armed, and nothing else. `None` is the
        # ordinary state and the state a confirmation returns to either way.
        self.armed: str | None = None

    @property
    def run_name(self) -> str:
        """A run is its file's stem, the same identity `rota ls` prints."""
        return self.db_path.stem if self.db_path else ""

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield VerticalScroll(id="conversation")
            with Vertical(id="sidebar"):
                yield Static("[b]outstanding[/b]")
                yield Static(id="run_state")
                yield Static(id="pulse")
                yield Outstanding(id="owed")
                yield Static("[b]sessions[/b]", id="sessions_title")
                yield VerticalScroll(id="sessions")
        yield Input(placeholder="say what you want built…", id="say")
        yield Footer()

    def on_mount(self) -> None:
        self.retitle()
        # Drawn either way. Returning early here left the sidebar blank and made
        # the "no run open" branches inside each refresher unreachable — guards
        # that cannot fire, which is worse than no guard because they read as
        # handled. Dismiss the list and the seat behind it says what it is.
        self.refresh_run_state()
        self.refresh_owed()
        self.refresh_pulse()
        if self.conn is None:
            # Nothing to sit in front of, so go straight to the level above.
            # A screen rather than a message, because the answer to "no runs
            # yet" is the thing that makes one.
            self.call_after_refresh(self.action_runs)

    def retitle(self) -> None:
        """
        The run first, the project second.

        It used to be `rota — <project> — <model>`, which names everything
        except the thing you are about to wipe. Two runs against one checkout is
        the normal case — a branch against its main is the comparison the answer
        key exists for — so the project alone does not say which is on screen.
        """
        self.title = f"rota — {self.run_name}" if self.db_path else "rota"
        self.sub_title = (
            f"{self.root.name if self.root else 'no project'} — {self.model}"
            if self.db_path else "no run open — ctrl+l")

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

    def note_step(self, line: str, productive: bool = True) -> None:
        pane = self.query_one("#sessions", VerticalScroll)
        # A barren session is dimmed rather than dropped. Seeing that the crank
        # turned and produced nothing is the point; hiding it would leave a
        # livelock looking like a quiet patch.
        pane.mount(Static(line if productive else f"[dim]{line}[/dim]"))
        extra = len(pane.children) - self.SESSION_LINES
        for old in list(pane.children)[:max(extra, 0)]:
            old.remove()
        pane.scroll_end(animate=False)
        if productive:
            self.last_productive = datetime.now().timestamp()
            self.barren_since = 0
        else:
            self.barren_since += 1
        self.show_replies()
        self.refresh_owed()
        self.refresh_pulse()

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
        if self.conn is None:
            self.query_one("#run_state", Static).update("[dim]no run open[/dim]")
            return
        state = config.get(self.conn, "run_state")
        here = "driving" if self.driving else "idle"
        self.query_one("#run_state", Static).update(
            f"[b]run:[/b] {state}   [b]this seat:[/b] {here}")

    def refresh_owed(self) -> None:
        if self.conn is None:
            self.query_one("#owed", Outstanding).update("")
            return
        self.query_one("#owed", Outstanding).render_rows(self.conn)

    def refresh_pulse(self) -> None:
        """
        The two numbers that answer "is this going anywhere", which a log cannot.

        The livelock that took a long diagnosis looked *healthy* in the session
        ticker: every line was a different message, every line was new, and
        nothing about the shape of it said the same two roles had been handing
        one thing back and forth for twenty sessions.

        **Time since a productive session** is the cheapest honest indicator
        there is, and it needs no new state — `Step.productive` already says
        whether a session changed anything, and nothing was reading it here.

        **Chain depth** is `deepest_repeat`, which is what `quarantine_looping`
        computes and discards. Shown against its cap, so a climb is legible
        before the bound fires rather than after it has quarantined something.
        """
        from ..core.scheduler import deepest_repeat

        if self.conn is None:
            self.query_one("#pulse", Static).update("")
            return
        bits = []
        if self.last_productive is None:
            bits.append("[dim]nothing written yet[/dim]" if self.driving
                        else "[dim]idle[/dim]")
        else:
            gap = int(datetime.now().timestamp() - self.last_productive)
            barren = self.barren_since
            colour = "yellow" if barren >= 3 else "dim"
            bits.append(f"[{colour}]last wrote {gap}s ago"
                        + (f", {barren} barren since" if barren else "")
                        + f"[/{colour}]")
        try:
            count, edge, _ = deepest_repeat(self.conn)
            cap = config.get(self.conn, "loop_cap")
        except sqlite3.Error:
            count, edge, cap = 0, "", 0
        if count > 1:
            colour = "red" if count > cap * 0.5 else "yellow"
            bits.append(f"[{colour}]{edge} ×{count} of {cap}[/{colour}]")
        self.query_one("#pulse", Static).update("\n".join(bits))

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
        if not self._needs_run():
            return
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
        self.query_one("#say", Input).placeholder = f"type {self.run_name} to confirm…"

    def confirm(self, text: str) -> None:
        """
        One chance, then it is an ordinary line again.

        A prompt that stays open until you get it right turns the next
        unrelated sentence into a confirmation, which is a worse failure than
        making you press the key twice.
        """
        what, self.armed = self.armed, None
        self.query_one("#say", Input).placeholder = "say what you want built…"
        if text.strip() != self.run_name:
            self.say(f"{what} cancelled", "system", "blue")
            return
        if what == "rerun" and self.root is None:
            self.say("no project to rerun against: reopen with a root, or "
                     "`rota onboard <name> --root <checkout>`", "system", "red")
            return

        name, root = self.run_name, self.root
        removed = self.wipe_run(reopen=(what == "rerun"))
        self.say(f"wiped {name}: {len(removed['worktrees'])} worktree(s), "
                 f"{len(removed['pids'])} process(es)", "system", "blue")
        if what == "rerun":
            self._pending_root = root
            self.say(f"onboarding {root}…", "system", "blue")
            self.run_worker(self._do_onboard, thread=True)
        else:
            # The run is gone, so there is nothing to sit in front of. The
            # answer to "no run open" is the screen that opens or makes one.
            self.action_runs()

    def wipe_run(self, reopen: bool = False) -> dict:
        """
        Close, wipe, and by default do not put anything back.

        **Wipe means the run is gone**, and it did not. From the list it deleted
        the file and the run disappeared; from the seat it deleted the file and
        then `init_db` put an empty one in its place, so the run survived as a
        husk — no `project_root`, no `code_index`, opening happily and showing
        `no project` in the title bar. One word doing two things, and the second
        one manufactured a kind of row that should not exist. `ctn_v3` in
        `.rota/` is one; that is where it came from.

        Closing first is still the order that matters: Windows will not unlink
        an open file, so a wipe that skips it does not fail — it reports what it
        meant to do and removes nothing.

        `reopen` has exactly one caller. `rerun` is wipe-then-index and indexing
        needs somewhere to write, so it says so at the call rather than leaving
        the word ambiguous for everybody else.
        """
        from ..cli import wipe as wipe_path

        path = self.db_path
        if self.conn is not None:
            self.conn.close()
            self.conn = None
        removed = wipe_path(path)
        if reopen:
            self.conn = init_db(path)
        else:
            self.db_path = None
            self.root = None
        self._init_seat_state()
        self.retitle()
        self.refresh_run_state()
        self.refresh_owed()
        self.refresh_pulse()
        return removed

    def _needs_run(self) -> bool:
        """
        Said once, for every key that assumes a run.

        The empty seat is reachable two ordinary ways — the first time you ever
        start, and the moment after a wipe — and four of five keys assumed it
        could not happen. `alt+b` built `Path(None)`, `alt+p` read `config` off
        a closed connection, and the two destructive keys armed against the
        empty string, offering `type `` to confirm`, which cannot be typed: the
        seat stayed armed with no way out.

        One guard rather than four, because the answer is the same each time
        and because the next key added would have needed it too.
        """
        if self.conn is not None:
            return True
        self.say("no run open — ctrl+l to pick one or make one",
                 "system", "yellow")
        return False

    def action_wipe(self) -> None:
        if self._needs_run():
            self.arm("wipe", "its worktrees, its recorded processes, and the file")

    def action_rerun(self) -> None:
        if self._needs_run():
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
        self._init_seat_state()
        self.query_one("#conversation", VerticalScroll).remove_children()
        self.query_one("#sessions", VerticalScroll).remove_children()
        self.retitle()
        self.refresh_run_state()
        self.refresh_owed()
        self.refresh_pulse()
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

        if self.conn is None:
            self.exit()                 # nothing open, so nothing to lose
            return
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
        if self._needs_run():
            self.open_cockpit(self.db_path)

    def open_cockpit(self, db_path: Path) -> None:
        """
        A cockpit on one run, owned by the seat that started it.

        Three things this got wrong on the first version, and all three are the
        same mistake: a spawned process was treated as fire-and-forget.

        **Its output went to this terminal.** A child inherits stdout and
        stderr, so the server's own logging printed *into the middle of the
        TUI* -- text arriving from outside the widget tree, which Textual
        neither controls nor repaints. Sent to a file instead, so it is still
        readable when the server will not start.

        **It outlived the seat.** Nothing recorded it and nothing stopped it, so
        quitting left a server holding port 8899 and the next one refused to
        bind. This is the failure `ENVIRONMENT.md` is entirely about, arrived at
        by hand in the one place that spawns something outside the scheduler --
        so it obeys the same rule the reaper does: **stop only what this process
        started**, which is why the handles are kept rather than the port
        scanned.

        **`--no-reload`, and that is what fixed the logs at the source.** The
        reloading server re-executes itself in a grandchild on every source
        change, which no parent can reliably kill on Windows, and its "watching
        for changes" and "reload:" lines were most of what was landing on the
        screen. Reload exists for editing the cockpit's own code; a cockpit
        opened to look at a run does not want it.
        """
        log = paths.REPO / ".rota" / f"cockpit-{Path(db_path).stem}.log"
        argv = [sys.executable, "-m", "rota", "cockpit", str(db_path),
                "--open", "--no-reload"]
        try:
            log.parent.mkdir(parents=True, exist_ok=True)
            handle = log.open("ab")
            child = subprocess.Popen(argv, stdout=handle, stderr=handle,
                                     stdin=subprocess.DEVNULL)
        except OSError as exc:                                  # noqa: BLE001
            self.say(f"could not start the cockpit: {exc}", "system", "red")
            return
        self.cockpits.append((child, handle))
        self.say(f"cockpit for {Path(db_path).stem} at http://127.0.0.1:8899/"
                 f"\n[dim]log: {log}[/dim]", "system", "blue")

    def stop_cockpits(self) -> list[int]:
        """
        Stop the servers this seat started. Nothing else, and nothing it cannot
        claim.

        The same rule as `environments.teardown` and `worktrees.destroy`: the
        proof of ownership is that we hold the handle we created. A cockpit you
        started yourself in another terminal is not ours, is not looked for, and
        is not touched.
        """
        stopped = []
        for child, handle in self.cockpits:
            if child.poll() is None:
                try:
                    child.terminate()
                    child.wait(timeout=5)
                    stopped.append(child.pid)
                except (OSError, subprocess.TimeoutExpired):
                    try:
                        child.kill()
                        stopped.append(child.pid)
                    except OSError:
                        pass                # gone between the poll and the signal
            try:
                handle.close()
            except OSError:
                pass
        self.cockpits.clear()
        return stopped

    def on_unmount(self) -> None:
        """
        Every way out, not just the confirmed one.

        Quitting through the modal, `ctrl+c` at a moment the modal is not up, an
        exception that takes the app down -- all of them unmount, and only one
        of them goes through code I wrote. Teardown belongs on the path they
        share.
        """
        self.stop_cockpits()

    # -- input ---------------------------------------------------------------

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # A modal's submission is the modal's. Events bubble widget -> screen ->
        # app, and `InputModal` does not stop them, so a name typed to confirm a
        # wipe also arrived here and was sent to Liaison as a sentence.
        if getattr(event.input, "id", "") in ("modal_input", "newrun_name",
                                              "newrun_root"):
            return
        text = event.value.strip()
        if not text:
            return
        event.input.value = ""

        if self.armed:
            self.confirm(text)
            return
        if self.conn is None:
            self.say("no run open — ctrl+l to pick one or make one",
                     "system", "yellow")
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
        """
        Index the project this run is about, or ask which one it is.

        It used to say `onboarding None…` and then return silently from the
        worker: the message was written before the guard, and the guard said
        nothing. Two failures in three lines — a sentence that is not true, and
        a refusal you cannot see.

        A run with no project is exactly a run that needs one, so the useful
        answer is the form rather than an error.
        """
        from .screens import NewRun

        if self.root is None:
            self.push_screen(NewRun(name=self.run_name), self._from_run_list)
            return
        self.say(f"onboarding {self.root}…", "system", "blue")
        self._pending_root = self.root
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
            self._from_worker(self.note_step, f"· {step}"[:120],
                              bool(getattr(step, "productive", True)))

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
    # No default. `.rota/rota.db` meant every bare invocation created or opened
    # one particular run, silently, whatever you meant -- and there is now a
    # screen whose whole job is to ask which one.
    ap.add_argument("--db", default=None,
                    help="a run database; omit to open the run list")
    ap.add_argument("--model", default=llm.DEFAULT_MODEL)
    # No default. The working directory is *this* repository, and a rerun
    # against it would index the framework over the top of the wiped run it was
    # meant to redo. Omitted, the root comes from the database, which is the
    # only place that actually knows.
    ap.add_argument("--root", type=Path, default=None,
                    help="project root; omit to use the one the run records")
    args = ap.parse_args(argv)
    RotaApp(Path(args.db) if args.db else None, args.model, root=args.root).run()
    return 0


if __name__ == "__main__":                                 # pragma: no cover
    sys.exit(main())
