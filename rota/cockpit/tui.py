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


from .. import paths
from ..core import loop as loop_mod
from ..core.db import connect, init_db
from ..core.predicates import outstanding
from ..llm import llm
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
    """
    BINDINGS = [("ctrl+c", "quit", "quit")]

    def __init__(self, db_path: Path, model: str) -> None:
        super().__init__()
        self.db_path = db_path
        self.model = model
        self.conn = init_db(db_path)
        self.principal = QueuedPrincipal(self)
        self.started = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield VerticalScroll(id="conversation")
            with Vertical(id="sidebar"):
                yield Static("[b]outstanding[/b]")
                yield Outstanding(id="owed")
                yield Static("[b]sessions[/b]", id="sessions_title")
                yield VerticalScroll(id="sessions")
        yield Input(placeholder="say what you want built…")
        yield Footer()

    def on_mount(self) -> None:
        self.title = f"rota — {self.model}"
        self.refresh_owed()

    # -- the two things the worker thread is allowed to do -------------------

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

    def refresh_owed(self) -> None:
        self.query_one("#owed", Outstanding).render_rows(self.conn)

    # -- input ---------------------------------------------------------------

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return
        event.input.value = ""
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
            self.run_worker(self._open_then_turn, thread=True, text=text)
        else:
            self.run_worker(self._turn_the_crank, thread=True)

    def _open_then_turn(self, text: str) -> None:
        """Write the follow-up message from the worker thread, then run."""
        conn = connect(self.db_path)
        try:
            open_with(conn, text)
        finally:
            conn.close()
        self._turn_the_crank()

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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="rota, with a face")
    ap.add_argument("--db", default=".rota/rota.db")
    ap.add_argument("--model", default=llm.DEFAULT_MODEL)
    args = ap.parse_args(argv)
    RotaApp(Path(args.db), args.model).run()
    return 0


if __name__ == "__main__":                                 # pragma: no cover
    sys.exit(main())
