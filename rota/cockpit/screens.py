"""
The two screens that sit above a single run.

Everything the seat could already do was *within* a run. Creating one, choosing
one and forking one are operations *about* runs, and they had nowhere to live —
which is the whole reason they stayed as commands. These are that level.

They are screens pushed over the seat rather than a separate app, so the seat
remains what it was and opening the list is a thing you do from inside it. That
also means switching runs is the app rebinding its own database rather than a
process restart, which is what makes "look at that one instead" cheap enough to
do while thinking.

Confirmation comes from `src/ui/modals.py`, which has had `ConfirmationModal`,
`InputModal` and `ChoiceModal` since long before any of this. The level is set
by whether an action is reversible and whether it names a target:

  * **reversible** -> a yes/no modal. Quitting stops a run, and that is all.
  * **irreversible and aimed at one run** -> type the run's name. A button
    confirms "yes"; it never confirms "yes, *that* one", and wipe is the case
    where the difference is the whole point.
"""
from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Label, Static

from .. import cli


def _is_empty(path: Path) -> bool:
    """
    A file with no `code_index` rows is a name, not a run.

    Refusing an existing name is right when it holds a run and wrong when it
    holds a husk — and a husk is precisely what you reached this form from, via
    `onboard` on a run with no project. Emptiness is asked of what onboarding
    *writes* rather than of the file existing, because the file existing is the
    thing that is not informative.

    Unreadable counts as not empty: a database this cannot open is one it
    certainly must not overwrite.
    """
    import sqlite3

    from ..core.db import connect_readonly

    try:
        conn = connect_readonly(path)
    except sqlite3.Error:
        return False
    try:
        return conn.execute("SELECT COUNT(*) n FROM code_index").fetchone()[0] == 0
    except sqlite3.Error:
        return False
    finally:
        conn.close()


class RunList(ModalScreen):
    """
    Every run, and what state each is in. `rota ls` with a cursor.

    The columns are chosen to answer the question you open this to ask, which
    is never "how many rows are in it" -- it is *which of these is the one I
    meant*. Hence the branch and commit beside the project: two runs against one
    checkout is the normal case, and until this was recorded they were
    indistinguishable.
    """

    # No `enter` here. `DataTable` binds it to `select_cursor` and the table
    # has the focus the whole time this screen is up, so a screen binding for
    # it never fires -- the same way `ctrl+w` never reached the seat. Enter
    # arrives as `RowSelected` instead, which is also what a mouse click emits,
    # so handling the event gets both and a binding would have got neither.
    BINDINGS = [
        ("escape", "dismiss_list", "back"),
        ("n", "new", "new"),
        ("f", "fork", "fork"),
        ("w", "wipe", "wipe"),
        ("c", "cockpit", "cockpit"),
        ("d", "diff", "diff"),
        ("r", "reload", "reload"),
    ]

    # The run marked as the left-hand side of a comparison. Two presses of `d`
    # rather than a multi-select, because marking one and then choosing the
    # other is what you are actually doing, and a mode you can forget you are
    # in is worse than a second keystroke.
    marked: str | None = None

    COLUMNS = ("run", "state", "source", "terms", "cons", "items", "sess")

    def compose(self) -> ComposeResult:
        with Vertical(id="runlist_container"):
            yield Label("runs", id="runlist_title")
            yield DataTable(id="runs", cursor_type="row")
            yield Static("", id="runlist_note")

    def on_mount(self) -> None:
        table = self.query_one("#runs", DataTable)
        table.add_columns(*self.COLUMNS)
        self.reload()
        table.focus()

    # -- data ----------------------------------------------------------------

    def reload(self) -> None:
        table = self.query_one("#runs", DataTable)
        cursor = table.cursor_row
        table.clear()
        self.rows = cli.runs()
        for row in self.rows:
            table.add_row(*self._cells(row))
        if self.rows:
            table.move_cursor(row=min(cursor, len(self.rows) - 1))
        self.query_one("#runlist_note", Static).update(
            "enter open · n new · f fork · w wipe · c cockpit · esc back"
            if self.rows else
            f"no runs in {cli.RUNS} — press n")

    @staticmethod
    def _cells(row: dict) -> tuple[str, ...]:
        counts = row["counts"]
        if row["branch"]:
            source = f"{row['branch']}@{row['commit'][:7]}"
            if row["moved"]:
                # The same comparison `reconcile_worktrees` makes for a batch.
                # A run whose tree moved is not wrong, it is *about* something
                # that no longer exists in that shape, and comparing it to a
                # fresh one is comparing two different sources.
                source += " · moved"
        else:
            source = Path(row["root"]).name if row["root"] else "—"
        return (
            row["name"],
            row["state"] or "—",
            source,
            str(counts.get("glossary_terms", "")),
            str(counts.get("constraints", "")),
            str(counts.get("items", "")),
            str(counts.get("sessions", "")),
        )

    @property
    def selected(self) -> dict | None:
        table = self.query_one("#runs", DataTable)
        if not self.rows or table.cursor_row is None:
            return None
        if not 0 <= table.cursor_row < len(self.rows):
            return None
        return self.rows[table.cursor_row]

    # -- actions -------------------------------------------------------------

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Enter and click, which are the same intent and neither was handled."""
        self.action_open()

    def action_reload(self) -> None:
        self.reload()

    def action_dismiss_list(self) -> None:
        self.dismiss(None)

    def action_open(self) -> None:
        row = self.selected
        if row is None:
            return
        if row["state"] == "stale":
            # Refuse rather than open onto a database whose panels will each
            # fail separately. `ls` already says why; opening would turn one
            # clear sentence into eight empty boxes.
            self.query_one("#runlist_note", Static).update(
                f"[red]{row['name']} is behind the schema and cannot be "
                f"opened. Wipe it, or keep it as a record.[/red]")
            return
        self.dismiss(("open", row))

    def action_new(self) -> None:
        self.app.push_screen(NewRun(), self._made)

    def action_fork(self) -> None:
        row = self.selected
        if row is None or not row["root"]:
            return
        self.app.push_screen(
            NewRun(name=f"{row['name']}-2", root=row["root"]), self._made)

    def _made(self, result) -> None:
        """
        Hand the form's answer *up*, do not absorb it.

        This reloaded the table and dropped the result, so `n` opened the form,
        the form validated, and nothing was ever onboarded — the one path the
        screen exists for, silently doing nothing. Onboarding is slow and
        belongs to the app's worker thread, not to a modal that is about to
        close, so the list closes too and passes the request on.
        """
        if result:
            self.dismiss(result)
        else:
            self.reload()

    def action_wipe(self) -> None:
        row = self.selected
        if row is None:
            return
        from src.ui.modals import InputModal

        def confirmed(value) -> None:
            if (value or "").strip() != row["name"]:
                self.query_one("#runlist_note", Static).update(
                    "wipe cancelled" if value is None else
                    f"[yellow]that is not {row['name']} — not wiped[/yellow]")
                return
            # **Through the app when it is the app's own run.** The seat holds
            # an open connection to it, and Windows will not unlink an open
            # file -- so wiping the run you are sitting in from here would
            # report success, remove nothing, and leave the seat pointed at a
            # database it thinks it wiped. `wipe_run` closes first and reopens
            # after, which is what makes the seat sittable afterwards.
            # Resolved on both sides. `ls` hands back whatever string the row
            # holds and the seat holds whatever was passed on the command line,
            # so a relative and an absolute spelling of one run compared
            # *unequal* — sending the seat's own database down the branch that
            # cannot close it first, straight into the refusal below.
            here = Path(self.app.db_path).resolve() if self.app.db_path else None
            if here is not None and Path(row["path"]).resolve() == here:
                if self.app.driving:
                    self.query_one("#runlist_note", Static).update(
                        f"[yellow]{row['name']} is running in this seat — "
                        f"pause it first[/yellow]")
                    return
                self.app.wipe_run()
            else:
                try:
                    cli.wipe(Path(row["path"]))
                except cli.WipeRefused as exc:
                    # Said in the screen, not raised through it. Whatever holds
                    # the file is something you close from a window that has to
                    # still be open to close it.
                    self.query_one("#runlist_note", Static).update(
                        f"[yellow]{exc}[/yellow]")
                    return
                except Exception as exc:                       # noqa: BLE001
                    self.query_one("#runlist_note", Static).update(
                        f"[red]{type(exc).__name__}: {exc}[/red]")
                    return
            self.reload()

        self.app.push_screen(InputModal(
            "wipe", f"its worktrees, its processes and the file. "
                    f"Type {row['name']} to confirm.", callback=confirmed))

    def action_diff(self) -> None:
        """
        Mark one, then pick the other. The step the loop ends in.

        A comparison needs two runs and the list is where both are visible, so
        this is its home rather than the seat's. Marking is shown in the note
        line, because a mode nothing displays is a mode you act inside without
        knowing.
        """
        row = self.selected
        if row is None:
            return
        note = self.query_one("#runlist_note", Static)
        if self.marked is None:
            self.marked = row["path"]
            note.update(f"[b]{row['name']}[/b] marked — press d on another run "
                        f"to compare, or d again to unmark")
            return
        if self.marked == row["path"]:
            self.marked = None
            note.update("unmarked")
            return
        left, self.marked = self.marked, None
        self.dismiss(("diff", left, row["path"]))

    def action_cockpit(self) -> None:
        row = self.selected
        if row is not None:
            self.app.open_cockpit(Path(row["path"]))


class NewRun(ModalScreen):
    """
    The form, which exists because starting a run needs two names at once.

    Drawing it is what found the hole it now closes: a run recorded its project
    root and nothing else, so two runs against one checkout on different
    branches were, on the record, about the identical thing. The form has to
    show the branch to be usable, and showing it means recording it.
    """

    BINDINGS = [("escape", "cancel", "cancel")]

    def __init__(self, name: str = "", root: str = "") -> None:
        super().__init__()
        self._name, self._root = name, root

    def compose(self) -> ComposeResult:
        with Vertical(id="newrun_container"):
            yield Label("new run", id="newrun_title")
            yield Label("name")
            yield Input(value=self._name, placeholder="ctn_v3", id="newrun_name")
            yield Label("repo")
            yield Input(value=self._root, placeholder="path to a checkout",
                        id="newrun_root")
            yield Static("", id="newrun_detected")
            with Horizontal():
                yield Button("onboard", id="newrun_go", variant="primary")
                yield Button("cancel", id="newrun_cancel")

    def on_mount(self) -> None:
        self.query_one("#newrun_name", Input).focus()
        self.detect()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "newrun_root":
            self.detect()

    def detect(self) -> None:
        """What the repo box currently points at, said before you commit to it."""
        root = self.query_one("#newrun_root", Input).value.strip()
        note = self.query_one("#newrun_detected", Static)
        if not root:
            note.update("")
            return
        path = Path(root).expanduser()
        if not path.is_dir():
            note.update("[yellow]no such directory[/yellow]")
            return
        branch, commit = cli.checkout_of(path)
        if not commit:
            note.update("[yellow]not a git checkout — the run will describe a "
                        "tree, not a commit[/yellow]")
            return
        note.update(f"{branch} · {commit[:7]}")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "newrun_name":
            self.query_one("#newrun_root", Input).focus()
        else:
            self.go()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "newrun_go":
            self.go()
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def go(self) -> None:
        name = self.query_one("#newrun_name", Input).value.strip()
        root = self.query_one("#newrun_root", Input).value.strip()
        note = self.query_one("#newrun_detected", Static)
        if not name or not root:
            note.update("[yellow]both a name and a repo[/yellow]")
            return
        path = cli.resolve(name)
        if path.exists() and not _is_empty(path):
            # Never silently over the top of a run that holds something.
            # Forking exists precisely so that running again beside one is the
            # easy thing.
            note.update(f"[red]{name} already exists — pick another name, "
                        f"or fork it[/red]")
            return
        if not Path(root).expanduser().is_dir():
            note.update("[red]no such directory[/red]")
            return
        self.dismiss(("onboard", name, str(Path(root).expanduser().resolve())))
