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

from rich.text import Text
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
        # Screen bindings shadow the app's — the app's own `ctrl+c` means
        # "quit", which is the wrong verb here: nothing is running yet, there
        # is only a scan of `RUNS` this screen is waiting on, and "cancel"
        # is that scan's own word for "back".
        ("ctrl+c", "dismiss_list", "cancel"),
        ("n", "new", "new"),
        ("f", "fork", "fork"),
        ("w", "wipe", "wipe"),
        ("c", "cockpit", "cockpit"),
        ("d", "diff", "diff"),
        ("r", "reload", "reload"),
        # Two keys, because a sort is two decisions. `s` chooses the
        # column. `S` chooses the direction. One key for both would make you
        # step through every other column to reverse the column you are on.
        ("s", "sort", "sort"),
        ("S", "sort_reverse", "reverse"),
    ]

    # The run marked as the left-hand side of a comparison. Two presses of `d`
    # rather than a multi-select, because marking one and then choosing the
    # other is what you are actually doing, and a mode you can forget you are
    # in is worse than a second keystroke.
    marked: str | None = None

    COLUMNS = ("run", "state", "source", "terms", "cons", "items", "sess",
               "created", "opened")

    # What each column sorts on. The counts sort as numbers, because a
    # string sort puts 10 before 9. A run this could not read holds no
    # counts. Such a run sorts as -1, so the unreadable runs gather at one
    # end instead of scattering through the numbers.
    SORT_KEYS = {
        "run": lambda row: row["name"].casefold(),
        "state": lambda row: (row["state"] or "").casefold(),
        "source": lambda row: RunList._source(row).casefold(),
        "terms": lambda row: row["counts"].get("glossary_terms", -1),
        "cons": lambda row: row["counts"].get("constraints", -1),
        "items": lambda row: row["counts"].get("items", -1),
        "sess": lambda row: row["counts"].get("sessions", -1),
        "created": lambda row: row["created"],
        "opened": lambda row: row["opened"],
    }

    # The list opens on the run you had open last.
    #
    # Name order was the order of the directory, which is an order about the
    # letters in a name and never about you. The run you want is nearly always
    # the run you were just in, and the one before it is the one you were in
    # before that. This is the one sort that starts descending. Every other
    # column starts ascending, as `sort_on` says.
    sort_by = "opened"
    sort_desc = True

    def compose(self) -> ComposeResult:
        with Vertical(id="runlist_container"):
            yield Label("runs", id="runlist_title")
            with Vertical(id="runlist_loading"):
                yield Static(f"reading {cli.RUNS}…", id="runlist_loading_text")
                yield Button("cancel", id="runlist_cancel")
            yield DataTable(id="runs", cursor_type="row")
            yield Static("", id="runlist_note")

    def on_mount(self) -> None:
        self._cancelled = False
        self.rows: list[dict] = []
        table = self.query_one("#runs", DataTable)
        for name in self.COLUMNS:
            table.add_column(self._header(name), key=name)
        self.reload()

    def _header(self, name: str) -> str:
        """
        The column label, with the arrow of the sort when the sort is on it.

        A `DataTable` measures a column when the column is added. It does not
        measure the column again when the label changes. The suffix is
        therefore one character wide in every state, the unsorted one
        included. A later arrow has the room it needs and no column moves.

        One character and not two. Nine columns pay for this space whether or
        not they are the sorted one, and the list is a modal over a seat that
        has its own panes to fit.
        """
        if name != self.sort_by:
            return f"{name} "
        return name + ("↓" if self.sort_desc else "↑")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "runlist_cancel":
            self.action_dismiss_list()

    # -- data ----------------------------------------------------------------

    def reload(self) -> None:
        """
        `cli.runs()` opens and reads every `.db` in `RUNS` -- one seek apiece
        on a slow disk, which is nothing on the command line where the
        process exits either way, and is the screen sitting frozen with no
        cursor and no way out when it runs on the UI thread here instead. So
        it runs on a worker thread, same as a session's own turn, and the
        loading placeholder plus its cancel button are what the screen shows
        instead of nothing while that thread is still working.

        Only shown when there is nothing to show yet: a manual reload with
        rows already on screen leaves them up rather than blanking a table
        that was doing no harm.
        """
        if not self.rows:
            self.query_one("#runlist_loading", Vertical).display = True
            self.query_one("#runs", DataTable).display = False
            self.query_one("#runlist_cancel", Button).focus()
        self.run_worker(self._fetch, thread=True, exclusive=True)

    def _fetch(self) -> None:
        try:
            rows = cli.runs()
        except Exception as exc:                            # noqa: BLE001
            self.app.call_from_thread(self._fetch_failed, exc)
            return
        self.app.call_from_thread(self._fetch_done, rows)

    def _fetch_done(self, rows: list[dict]) -> None:
        # The screen this was reading for may already be gone -- cancelled
        # out from under it by the same key that would once have just sat
        # there unresponsive. Nothing left to post the result to.
        if self._cancelled:
            return
        table = self.query_one("#runs", DataTable)
        # Read out of the rows that are still on screen, before the new ones
        # replace them. A reload that found the same runs leaves the cursor
        # on the run you were looking at.
        keep = self.selected["name"] if self.selected else None
        self.rows = rows
        self._draw(keep)
        self.query_one("#runlist_loading", Vertical).display = False
        table.display = True
        table.focus()
        self.query_one("#runlist_note", Static).update(
            "enter open · n new · f fork · w wipe · c cockpit · "
            "s sort · esc back"
            if self.rows else
            f"no runs in {cli.RUNS} — press n")

    def _draw(self, keep: str | None) -> None:
        """
        Put `self.rows` in the sort order, then draw them.

        `self.rows` holds the drawn order, not the read order. The cursor row
        is an index into the table. `selected` reads the same index out of
        `self.rows`. One list in one order is what keeps the cursor and the
        run under it the same run.

        The cursor holds its **run**, not its row number. `keep` names that
        run. You sort to find a run. A cursor that stayed on row 4 would put
        a different run under you at every press of the key.
        """
        table = self.query_one("#runs", DataTable)
        # Where the reader had scrolled sideways to. `DataTable.clear` sets
        # `scroll_x` to zero, so sorting on a column you had to scroll right
        # to reach threw away the view of the column you sorted on.
        scroll_x = table.scroll_x
        # Two sorts, because most columns tie. Seven runs at `ready` in the
        # order the last sort left them is an order with no rule you can see.
        # A Python sort is stable, so the name sort underneath is the rule the
        # ties fall back to, and it holds in both directions.
        self.rows.sort(key=self.SORT_KEYS["run"])
        if self.sort_by != "run":
            self.rows.sort(key=self.SORT_KEYS[self.sort_by],
                           reverse=self.sort_desc)
        elif self.sort_desc:
            self.rows.sort(key=self.SORT_KEYS["run"], reverse=True)
        table.clear()
        for row in self.rows:
            table.add_row(*self._cells(row))
        for name in self.COLUMNS:
            table.columns[name].label = Text(self._header(name))
        table.refresh()
        if not self.rows:
            return
        names = [row["name"] for row in self.rows]
        table.move_cursor(row=names.index(keep) if keep in names else 0)
        # After the cursor, not before it. Moving the cursor scrolls to it,
        # and the horizontal half of that is what put the view back at the
        # left edge in the first place.
        table.scroll_to(x=scroll_x, y=table.scroll_y, animate=False)

    def _fetch_failed(self, exc: Exception) -> None:
        if self._cancelled:
            return
        self.query_one("#runlist_loading_text", Static).update(
            f"[red]{type(exc).__name__}: {exc}[/red]")

    @staticmethod
    def _source(row: dict) -> str:
        """
        The source cell, which the source sort also reads.

        One function serves the cell and the sort key. A column that sorts on
        something other than what it shows is a column you cannot read.
        """
        if row["branch"]:
            source = f"{row['branch']}@{row['commit'][:7]}"
            if row["moved"]:
                # The same comparison `reconcile_worktrees` makes for a batch.
                # A run whose tree moved is not wrong, it is *about* something
                # that no longer exists in that shape, and comparing it to a
                # fresh one is comparing two different sources.
                source += " · moved"
            return source
        return Path(row["root"]).name if row["root"] else "—"

    @staticmethod
    def _cells(row: dict) -> tuple[str, ...]:
        counts = row["counts"]
        source = RunList._source(row)
        return (
            row["name"],
            row["state"] or "—",
            source,
            str(counts.get("glossary_terms", "")),
            str(counts.get("constraints", "")),
            str(counts.get("items", "")),
            str(counts.get("sessions", "")),
            RunList._age(row["created"]),
            RunList._age(row["opened"]),
        )

    @staticmethod
    def _age(when: float) -> str:
        """
        How long ago, in one cell.

        An age, not a date. The question the column answers is "which of these
        did I touch last", and a date makes the reader do the subtraction. A
        date is also 10 characters wide in a table that already has seven
        columns.

        A run with no answer shows a dash. `_file_times` means that is rare,
        so a dash here says the file itself could not be read.
        """
        if not when:
            return "—"
        import time

        gap = time.time() - when
        if gap < 60:
            return "now"
        if gap < 3600:
            return f"{int(gap // 60)}m"
        if gap < 86400:
            return f"{int(gap // 3600)}h"
        if gap < 86400 * 365:
            return f"{int(gap // 86400)}d"
        return f"{int(gap // (86400 * 365))}y"

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

    def on_data_table_header_selected(
            self, event: DataTable.HeaderSelected) -> None:
        """
        A click on a column header sorts on that column.

        The second click on the same header reverses the sort. Every other
        table does this. The keyboard gains nothing if the mouse cannot.
        """
        self.sort_on(self.COLUMNS[event.column_index])

    def action_sort(self) -> None:
        """`s` moves the sort to the next column, and wraps at the end."""
        following = (self.COLUMNS.index(self.sort_by) + 1) % len(self.COLUMNS)
        self.sort_on(self.COLUMNS[following], toggle=False)

    def action_sort_reverse(self) -> None:
        """`S` reverses the sort that is on."""
        self.sort_desc = not self.sort_desc
        self._resort()

    def sort_on(self, column: str, toggle: bool = True) -> None:
        """
        Sort on one column. Asking again for the same column reverses the sort.

        A new column always starts ascending. One direction for every column
        is the direction you can predict. `S` gives you the other direction
        in one key.
        """
        if column not in self.SORT_KEYS:
            return
        if column == self.sort_by and toggle:
            self.sort_desc = not self.sort_desc
        else:
            self.sort_by = column
            self.sort_desc = False
        self._resort()

    def _resort(self) -> None:
        """
        Draw again in the new order, and hold the cursor on its run.

        An empty list still redraws. The header arrow moves, so the sort you
        chose is the sort the next reload lands in.
        """
        self._draw(self.selected["name"] if self.selected else None)

    def action_dismiss_list(self) -> None:
        self._cancelled = True
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
