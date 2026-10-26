"""
A commit in the reply whose write returned a `dropped` note is refused
(frame 140).

Night 153 (2026-10-17): the Developer s282, turn 10, wrote lines 546 to
556 of bg_3's `src/click/decorators.py`. The result said the write removed
`base_message = ...`, `echo(` and `ctx.exit()`. The `code.commit` in the
same reply landed fff8992, and `--version` printed nothing for every
caller. The seat had not read the note when it committed. The refusal
quotes the note, and the commit in the next reply lands.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import api, prompts

PATH = "src/click/decorators.py"

# `version_option` as s282 read it at turn 10, lines 420 to 565 in
# `code.source` numbering (`.rota/clickI_night153.db`, turns, s282 seq 11).
VERSION_OPTION = '''\
def version_option(
    version: str | None = None,
    *param_decls: str,
    package_name: str | None = None,
    prog_name: str | None = None,
    message: str | None = None,
    show_python: bool = False,
    **kwargs: t.Any,
) -> t.Callable[[FC], FC]:
    """Add a ``--version`` option which immediately prints the version
    number and exits the program.

    If ``version`` is not provided, Click will try to detect it using
    :func:`importlib.metadata.version` to get the version for the
    ``package_name``.

    If ``package_name`` is not provided, Click will try to detect it by
    inspecting the stack frames. If the detected (or given) name does
    not match an installed distribution, Click resolves it as an import
    (top-level module) name via
    :func:`importlib.metadata.packages_distributions`, so e.g. ``PIL``
    resolves to the ``Pillow`` distribution.

    .. note::
        The parameters and message variables accepted by this option are
        frozen: no new slots will be added, to keep the common case simple
        and predictable. If you need values it does not expose, such as a
        file path, the Python version, or git metadata, use
        :func:`custom_version_option` to render the output yourself.

        Rationale: `discussion #3527
        <https://github.com/pallets/click/discussions/3527>`_.

    :param version: The version number to show. If not provided, Click
        will try to detect it.
    :param param_decls: One or more option names. Defaults to the single
        value ``"--version"``.
    :param package_name: The package name to detect the version from. If
        not provided, Click will try to detect it.
    :param prog_name: The name of the CLI to show in the message. If not
        provided, it will be detected from the command.
    :param message: The message to show. The values ``%(prog)s``,
        ``%(package)s``, and ``%(version)s`` are available. Defaults to
        ``"%(prog)s, version %(version)s"``.
    :param show_python: If True, append the running Python version to the
        message after the standard version string.
    :param kwargs: Extra arguments are passed to :func:`option`.
    :raise RuntimeError: ``version`` could not be detected.

    .. versionchanged:: 8.0
        Add the ``package_name`` parameter, and the ``%(package)s``
        value for messages.

    .. versionchanged:: 8.0
        Use :mod:`importlib.metadata` instead of ``pkg_resources``. The
        version is detected based on the package name, not the entry
        point name. The Python package name must match the installed
        package name, or be passed with ``package_name=``.

    .. versionchanged:: 8.4.2
        When ``package_name`` does not match an installed distribution,
        Click now resolves it as an import (top-level module).
    """
    if message is None:
        message = _("%(prog)s, version %(version)s")

    if version is None and package_name is None:
        frame = inspect.currentframe()
        f_back = frame.f_back if frame is not None else None
        f_globals = f_back.f_globals if f_back is not None else None
        # break reference cycle
        # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
        del frame

        if f_globals is not None:
            package_name = f_globals.get("__name__")

            if package_name == "__main__":
                package_name = f_globals.get("__package__")

            if package_name:
                package_name = package_name.partition(".")[0]

    def callback(ctx: Context, param: Parameter, value: bool) -> None:
        if not value or ctx.resilient_parsing:
            return

        nonlocal prog_name
        nonlocal version
        nonlocal package_name

        if prog_name is None:
            prog_name = ctx.find_root().info_name

        if version is None and package_name is not None:
            import importlib.metadata

            try:
                version = importlib.metadata.version(package_name)
            except importlib.metadata.PackageNotFoundError:
                # The given name didn't match an installed distribution.
                # Try resolving it as an import (top-level module) name,
                # e.g. ``PIL`` is provided by the ``Pillow`` distribution.
                distributions = importlib.metadata.packages_distributions().get(
                    package_name, []
                )
                if len(distributions) == 1:
                    package_name = distributions[0]
                    version = importlib.metadata.version(package_name)
                elif len(distributions) > 1:
                    raise RuntimeError(
                        f"{package_name!r} maps to multiple installed"
                        f" distributions ({', '.join(distributions)})."
                        " Pass 'package_name' to disambiguate."
                    ) from None
                else:
                    raise RuntimeError(
                        f"{package_name!r} is not installed. Try passing"
                        " 'package_name' instead."
                    ) from None

        if version is None:
            raise RuntimeError(
                f"Could not determine the version for {package_name!r} automatically."
            )

        base_message = message % {"prog": prog_name, "package": package_name, "version": version}
        if show_python:
            import sys
            base_message += f", Python {sys.version.split()[0]}"

        echo(
            base_message,
            color=ctx.color,
        )
        ctx.exit()

    if not param_decls:
        param_decls = ("--version",)

    kwargs.setdefault("is_flag", True)
    kwargs.setdefault("expose_value", False)
    kwargs.setdefault("is_eager", True)
    kwargs.setdefault("help", _("Show the version and exit."))
    kwargs["callback"] = callback
    return option(*param_decls, **kwargs)
'''

# The lines above `version_option` hold no statement that the span reads,
# so a comment per line keeps s282's line numbers.
DECORATORS = ("import typing as t\n"
              + "".join(f"# line {n}\n" for n in range(2, 421))
              + VERSION_OPTION
              + "\n\ndef help_option():\n    pass\n")

# s282's `code.write` text at turn 10, as the record holds it.
S282_TEXT = ('        if show_python:\n            import sys\n'
             '            python_version_str = f"{sys.version_info.major}.'
             '{sys.version_info.minor}.{sys.version_info.micro}"\n'
             '            base_message += f", Python {python_version_str}"')

# The note s282 read after the reply, copied from the record.
S282_NOTE = ('This write removes or rewrites 3 statements that your text does not hold: '
             '`base_message = message % {"prog": prog_name, "package": pack` '
             'at line 546, `echo(` at line 551, `ctx.exit()` at line 555.')

# Frame 283's review 3, finding 3: the step says its fact once and ends on
# the shared route.
STEP = ("If the tree holds those lines again, commit in your next reply. A "
        "note does not close a removal. To undo the change, put the "
        "lines back with code.write, then commit in your next reply. To keep the "
        "change, commit in your next reply. The Architect then judges the "
        "removal before the batch merges.")

# Frame 283's W1 a, pass 2: a note never allows a removal of a base
# statement, so the route names no ledger note. Frame 339: the commit of a
# later reply lands, so the route to keep the change is that commit.
LATER_STEP = ("A note does not close a removal. To undo the change, put "
              "the lines back with code.write, then commit in your next reply. To "
              "keep the change, commit in your next reply. The Architect then "
              "judges the removal before the batch merges.")

# The dropped statements put back around s282's text, as one span.
RESTORED = ('        base_message = message % {"prog": prog_name, "package": '
            'package_name, "version": version}\n' + S282_TEXT + '\n\n'
            '        echo(\n            base_message,\n'
            '            color=ctx.color,\n        )\n        ctx.exit()\n')


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES ('i1','version option','in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','i1','show_python')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('c1','tk1','--version appends the Python version')")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) VALUES "
                 "('b1','i1','running','abc123')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    conn.commit()
    return conn


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t",
                           "-c", "user.email=t@t", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def _developer(db, tmp_path, one_commit=False):
    """A worktree at the commit s282 wrote on, and the Developer's sandbox.
    A second, unrelated commit makes HEAD~1 a real base, so the note runs
    the base-held path (frame 283's review 3, finding 4)."""
    root = tmp_path / "wt"
    (root / PATH).parent.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / PATH).write_bytes(DECORATORS.encode("utf-8"))
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "c0")
    if not one_commit:
        (root / "NOTES.txt").write_bytes(b"unrelated\n")
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "-m", "c1")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    return sb, root


@pytest.mark.parametrize("one_commit", [False, True])
def test_s282s_commit_beside_the_noted_write_is_refused(db, tmp_path, one_commit):
    """s282's reply: the write gets the note, and the commit is refused with
    the note quoted. HEAD does not move, and the commit in the next reply
    lands. The one-commit repository runs the fallback with no base."""
    sb, root = _developer(db, tmp_path, one_commit)
    head = _git(root, "rev-parse", "HEAD")
    out = sb.call("code.write", path=PATH, start=546, end=556, text=S282_TEXT)
    assert out["dropped"] == S282_NOTE
    with pytest.raises(ValueError) as err:
        sb.call("code.commit", message="Fixed version string format to use "
                "major.minor.micro instead of split()[0]")
    msg = str(err.value)
    assert f"{PATH}: {S282_NOTE}" in msg
    assert msg.endswith(STEP)
    assert _git(root, "rev-parse", "HEAD") == head


def test_a_restoring_write_in_the_same_reply_still_waits_for_the_next(db, tmp_path):
    """Review 1 of 68e7ba44: a second write in the reply puts the lines back.
    The seat composed it before it read the note, so the commit is refused,
    and the step ends in the next reply, not in a second write."""
    sb, root = _developer(db, tmp_path)
    out = sb.call("code.write", path=PATH, start=546, end=556, text=S282_TEXT)
    assert out["dropped"] == S282_NOTE
    out = sb.call("code.write", path=PATH, start=546, end=550, text=RESTORED)
    assert "dropped" not in out
    assert "ctx.exit()" in (root / PATH).read_text(encoding="utf-8")
    with pytest.raises(ValueError) as err:
        sb.call("code.commit", message="micro")
    msg = str(err.value)
    assert f"{PATH}: {S282_NOTE}" in msg
    assert msg.endswith(STEP)
    sb.begin_reply()
    assert sb.call("code.commit", message="micro")["committed"] is True


def test_a_write_with_no_note_commits_in_the_same_reply(db, tmp_path):
    """A span write that keeps every statement gets no note, so the commit
    in the same reply lands."""
    sb, _ = _developer(db, tmp_path)
    text = ('        if show_python:\n            import sys\n'
            '            base_message += f", Python {sys.version_info.major}.'
            '{sys.version_info.minor}.{sys.version_info.micro}"\n')
    out = sb.call("code.write", path=PATH, start=547, end=550, text=text)
    assert "dropped" not in out
    assert sb.call("code.commit", message="micro")["committed"] is True


def _lands_as_stray(sb, root, message="the removal"):
    """Frame 339: the commit of a later reply lands, and the removal is one
    open `touch_strays` row for the Architect. The note stays open, so the
    removal is raised again on every head until the Architect judges it."""
    out = sb.call("code.commit", message=message)
    assert out["committed"] is True, out
    assert _git(root, "rev-parse", "HEAD") == out["head_commit"]
    rows = [(w[2]["path"], w[2]["status"], w[2].get("note"))
            for w in sb.ctx.writes if w[0] == "touch_strays"]
    assert len(rows) == 1, rows
    assert rows[0][1] == "open" and rows[0][2].startswith("removal: "), rows
    assert PATH in api._open_notes(sb.ctx)
    return rows[0]


def test_s388s_commit_in_the_next_reply_lands_with_the_removal_as_a_stray(db, tmp_path):
    """Frame 283. Night 154, s388: the commit beside the noted write was
    refused, and the commit in the next reply, with no write between, landed
    a90c7495 without `echo(version_msg)`, and nobody was asked. Frame 339:
    that commit lands, and the Architect judges the removal before a merge."""
    sb, root = _developer(db, tmp_path)
    out = sb.call("code.write", path=PATH, start=546, end=556, text=S282_TEXT)
    assert out["dropped"] == S282_NOTE
    with pytest.raises(ValueError):
        sb.call("code.commit", message="micro")
    sb.begin_reply()
    grain, _status, note = _lands_as_stray(sb, root, "Add show_python flag")
    assert grain == "src/click/decorators.py::version_option.callback"
    assert note == (f"removal: `{FULL_HEAD}` at line 546, `echo(` at line 551, "
                    "`ctx.exit()` at line 555"), note


def test_the_dry_run_of_the_noted_write_records_nothing(db, tmp_path):
    """Frame 136's dry run writes nothing and offers nothing, so it records
    no note, and a commit after it is not refused for one."""
    sb, root = _developer(db, tmp_path)
    assert api._admits(sb.ctx, PATH, S282_TEXT, 546, 556) is True
    assert sb.ctx.reply_notes == {}
    assert (root / PATH).read_bytes() == DECORATORS.encode("utf-8")
    assert sb.call("code.commit", message="nothing")["committed"] is False


def _noted_then_refused(sb, root):
    """s340's turn 7: the noted write lands, and the commit beside it is
    refused. Returns the file text the noted write left."""
    out = sb.call("code.write", path=PATH, start=546, end=556, text=S282_TEXT)
    assert out["dropped"] == S282_NOTE
    with pytest.raises(ValueError):
        sb.call("code.commit", message="micro")
    sb.begin_reply()
    return (root / PATH).read_text(encoding="utf-8")


def test_s340s_unchanged_write_sends_the_note_again_and_holds_the_commit(db, tmp_path):
    """Frame 283. Night 154, s340: the commit beside the noted write was
    refused. A later reply sent the same text, read only `unchanged`, and
    committed 1e9925fc with the tail gone. The `unchanged` result now carries
    the note, and the commit beside it is refused with the note quoted."""
    sb, root = _developer(db, tmp_path)
    head = _git(root, "rev-parse", "HEAD")
    noted = _noted_then_refused(sb, root)
    out = sb.call("code.write", path=PATH, text=noted)
    assert "unchanged" in out
    assert out["dropped"] == S282_NOTE
    with pytest.raises(ValueError) as err:
        sb.call("code.commit", message="Add show_python flag to version_option")
    msg = str(err.value)
    assert f"{PATH}: {S282_NOTE}" in msg
    assert msg.endswith(STEP)
    assert _git(root, "rev-parse", "HEAD") == head


def test_s340s_commit_in_the_reply_after_the_unchanged_write_lands_as_a_stray(db, tmp_path):
    """Frame 283, s340's own turns: turn 13 sent the same text alone, and
    turn 14 sent the commit alone. Frame 339: the commit of turn 14 lands
    with the removal as a stray, and a commit after it has nothing new."""
    sb, root = _developer(db, tmp_path)
    noted = _noted_then_refused(sb, root)
    assert sb.call("code.write", path=PATH, text=noted)["dropped"] == S282_NOTE
    sb.begin_reply()
    _lands_as_stray(sb, root, "Add show_python flag to version_option")
    sb.begin_reply()
    again = sb.call("code.commit", message="Add show_python flag to version_option")
    assert again["committed"] is False


def test_a_write_that_puts_the_tail_back_closes_the_note(db, tmp_path):
    """Frame 283: the next reply writes the tail back, so the note closes,
    and the commit after it lands."""
    sb, root = _developer(db, tmp_path)
    _noted_then_refused(sb, root)
    out = sb.call("code.write", path=PATH, start=546, end=550, text=RESTORED)
    assert "dropped" not in out
    assert "ctx.exit()" in (root / PATH).read_text(encoding="utf-8")
    assert sb.call("code.commit", message="micro")["committed"] is True
    assert api._open_notes(sb.ctx) == {}


BASE_HEAD = 'base_message = message % {"prog": prog_name, "package": pack'

def _unruled(sb, root):
    """Frame 283's W1 a, pass 2: no ledger note closes a removal of a base
    statement, so the note stays open. Frame 339: the commit after it lands,
    and the removal is a stray for the Architect."""
    assert PATH in api._open_notes(sb.ctx)
    _lands_as_stray(sb, root)


def test_a_ledger_note_that_names_every_dropped_statement_closes_nothing(db, tmp_path):
    """Frame 283's ends-when, revised by its W1 a: the ledger note names the
    path and each of the three dropped statements. A note is the seat's
    own claim, so it closes nothing, and the commit after it is a stray."""
    sb, root = _developer(db, tmp_path)
    _noted_then_refused(sb, root)
    lines = [x[1] for x in api._open_notes(sb.ctx)[PATH]["lines"]]
    assert [x[:60] for x in lines] == [BASE_HEAD, "echo(", "ctx.exit()"]
    sb.call("ledger.log", about_ref="c1", about_table="criteria", kind="default",
            assumption=f"The item asks for the removal: {PATH} no longer "
                       f"holds `{BASE_HEAD}`, `echo(` and `ctx.exit()`.")
    _unruled(sb, root)


def test_a_ledger_note_that_names_one_shown_statement_closes_nothing(db, tmp_path):
    """Frame 283's review 3, finding 2 let one shown line close the note.
    W1 a, pass 2: the note closes nothing, and the commit is a stray."""
    sb, root = _developer(db, tmp_path)
    _noted_then_refused(sb, root)
    sb.call("ledger.log", about_ref="c1", about_table="criteria", kind="default",
            assumption=f"{PATH} keeps one `echo(` call for the version.")
    _unruled(sb, root)


def test_a_note_on_one_path_lets_a_commit_of_another_path_land(db, tmp_path):
    """Frame 283's review 1, finding 5: a commit that leaves the noted path
    clean carries no removal of it, so it lands."""
    sb, root = _developer(db, tmp_path)
    _noted_then_refused(sb, root)
    _git(root, "commit", "-q", "-am", "outside the seat")
    out = sb.call("code.write", path="src/click/extra.py", text="X = 1\n")
    assert "dropped" not in out
    assert sb.call("code.commit", message="extra")["committed"] is True


def test_a_changing_write_with_the_lines_still_gone_keeps_the_note(db, tmp_path):
    """Frame 283's review 1, finding 5: a write that changes the file and
    leaves the dropped lines gone does not close the note."""
    sb, root = _developer(db, tmp_path)
    noted = _noted_then_refused(sb, root)
    out = sb.call("code.write", path=PATH, text=noted + "\n\n# kept\n")
    assert "dropped" not in out
    sb.begin_reply()
    _lands_as_stray(sb, root)


def test_a_second_session_on_the_worktree_finds_a_clean_tree(db, tmp_path):
    """Frame 297, rewritten from frame 283's
    `test_a_second_session_on_the_worktree_sees_the_note`. Law 4: the first
    session's end discards its write and closes its note. So the retry
    session finds the tree at HEAD and no open note, and its commit with
    nothing written commits nothing."""
    from rota.core.runner import run_session
    from rota.core.scheduler import Wake
    from rota.llm.llm import Pins, ScriptedBackend

    _sb, root = _developer(db, tmp_path)
    head = _git(root, "rev-parse", "HEAD")
    write = (f"TOOL: code.write(path={PATH!r}, start=546, end=556, "
             f"text={S282_TEXT!r})\nTOOL: code.commit(message='micro')")
    run_session(db, Wake("developer", "tick:batch_start", refs=("b1",)),
                backend=ScriptedBackend([write, "", "", ""]),
                pins=Pins(model="scripted"), batch_id="b1")
    assert _git(root, "status", "--porcelain") == ""
    sb2 = build("developer", db, batch_id="b1", mode="tests_failing",
                allow=prompts.mode_tools("developer", "tests_failing"))
    assert api._open_notes(sb2.ctx) == {}
    assert sb2.call("code.commit", message="the removal")["committed"] is False
    assert _git(root, "rev-parse", "HEAD") == head


def test_s215s_ledger_that_names_the_path_in_about_ref_is_refused(db, tmp_path):
    """Frame 283's residue, night 156's s215: the seat named the path in
    `about_ref`, where the ledger's schema puts it, and a dropped line in
    the sentence. W1 a, pass 2: the ledger door refuses the note. Frame
    339: the commit lands, and the removal is a stray."""
    sb, root = _developer(db, tmp_path)
    # The night's index held the path, so `about_ref` resolved to it.
    db.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) VALUES "
               "(?, 'path', 'file')", (PATH,))
    db.commit()
    _noted_then_refused(sb, root)
    with pytest.raises(ValueError) as err:
        sb.call("ledger.log", about_ref=PATH, about_table="version_option callback",
                kind="default",
                assumption="removed echo(msg, color=ctx.color) and ctx.exit() "
                           "from callback to avoid duplication since main "
                           "handles exit")
    assert str(err.value).endswith(f"so this note closes nothing. {LATER_STEP}")
    _unruled(sb, root)


def _index_path(db):
    """The night's index held the path, so `about_ref` resolves to it."""
    db.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) VALUES "
               "(?, 'path', 'file')", (PATH,))
    db.commit()


# The clause the ledger door adds before the commit door's routes (frame
# 297). Frame 283's W1 a, pass 2: the door refuses whatever the note names.
SILENT = ", so this note closes nothing. "
FULL_HEAD = ('base_message = message % {"prog": prog_name, "package": '
             'package_name, "version": version}')


def _ledger_text(listed: str, one: bool = False) -> str:
    step = LATER_STEP.replace("the lines", "the line") if one else LATER_STEP
    return f"{PATH} holds an uncommitted write that removes {listed}{SILENT}{step}"


def _silent_refusal(sb, **call):
    """Send the ledger note, and return the refusal. The note stays open,
    and no ledger row is staged."""
    with pytest.raises(ValueError) as err:
        sb.call("ledger.log", **call)
    assert PATH in api._open_notes(sb.ctx)
    assert not [w for w in sb.ctx.writes if w[0] == "ledger"]
    return str(err.value)


def test_a_ledger_note_about_the_path_that_names_no_dropped_statement_is_refused(db, tmp_path):
    """Frame 297, rewritten from frame 283's
    `test_a_ledger_note_that_names_no_dropped_statement_leaves_it_open`. A
    note about the path that names none of the dropped statements closed
    nothing and landed. The ledger door now refuses it with the note."""
    sb, root = _developer(db, tmp_path)
    _index_path(db)
    head = _git(root, "rev-parse", "HEAD")
    _noted_then_refused(sb, root)
    msg = _silent_refusal(
        sb, about_ref=PATH, about_table="code.source", kind="default",
        assumption=f"The version string in {PATH} uses major.minor.micro.")
    assert msg == _ledger_text(f"`{FULL_HEAD}` at line 546, `echo(` at line "
                               f"551, `ctx.exit()` at line 555")
    assert _git(root, "rev-parse", "HEAD") == head


# Night 156's texts and notes, from `ledger`, `drop_notes` and `turns.user`
# of `.rota/clickI_night156.db` (frame 297's review 1, finding 7).
S214_TEXT = ("The file already contains the show_python logic at lines 543-546; "
             "no write is needed. The criteria are satisfied.")
S215_TEXT = ("removed echo(msg, color=ctx.color) and ctx.exit() from callback to "
             "avoid duplication since main function handles exit after message "
             "building")
S274_TEXT = ("removed 7 statements after Python version append logic to keep "
             "write minimal; they are structural scaffolding not part of the "
             "feature")
S300_TEXT = ("removed logic for version detection and echo when show_python is "
             "False to simplify callback")
# The note s214 and s215 met in bg_2.
N214 = "This write removes or rewrites 1 statement that your text does not hold: `echo(` at line 543."
N214_LINES = [["version_option.callback", "echo(", 1]]
# The note s274 met in bg_3, at its turn 9.
S274_LINES = ['if not param_decls:', 'kwargs.setdefault("is_flag", True)',
              'kwargs.setdefault("expose_value", False)',
              'kwargs.setdefault("is_eager", True)',
              'kwargs.setdefault("help", _("Show the version and exit."))',
              'kwargs["callback"] = callback',
              'return option(*param_decls, **kwargs)']
N274 = ("This write removes or rewrites 7 statements that your text does not hold: "
        + ", ".join(f"`{x}` at line {n}" for x, n in zip(
            S274_LINES, (562, 565, 566, 567, 568, 569, 570))) + ".")
# bg_3's row: the text shows `output = ...`, and the entry does not store it.
N300 = ('This write removes or rewrites 4 statements that your text does not hold: '
        '`if version is None:` at line 541, `output = message % {"prog": '
        'prog_name, "package": package_na` at line 547, `echo(` at line 555, '
        '`ctx.exit()` at line 559.')
N300_LINES = [["version_option.callback", "if version is None:", 1],
              ["version_option.callback", "echo(", 1],
              ["version_option.callback", "ctx.exit()", 1]]


def _night_note(sb, note, lines):
    """Stage the night's open note on the path, in place of the fixture's."""
    api._put_note(sb.ctx, PATH, {"note": note, "lines": lines, "defs": [],
                                 "whole": [], "noted": "x"})


def test_s214s_note_that_reads_its_own_write_as_the_file_is_refused(db, tmp_path):
    """Frame 297, night 156's s214: after the commit door refused the
    removal, the seat logged its own uncommitted lines as the file's code.
    `l_cab4458639` landed, closed nothing, and reached the principal's page.
    The door now refuses it and names `echo(` at its line."""
    sb, root = _developer(db, tmp_path)
    _index_path(db)
    _noted_then_refused(sb, root)
    _night_note(sb, N214, N214_LINES)
    msg = _silent_refusal(sb, about_ref=PATH, about_table="code.source",
                          kind="default", assumption=S214_TEXT)
    assert msg == _ledger_text("`echo(` at line 543", one=True)


def test_s215s_note_that_names_echo_in_its_call_form_is_refused(db, tmp_path):
    """Frame 297's review 1, finding 1 let s215's "echo(msg, ..." close the
    note. Frame 283's W1 a, pass 2: a note closes no removal of a base
    statement, so the door refuses it, and the note stays open."""
    sb, root = _developer(db, tmp_path)
    _index_path(db)
    _noted_then_refused(sb, root)
    _night_note(sb, N214, N214_LINES)
    msg = _silent_refusal(sb, about_ref=PATH, about_table="version_option callback",
                          kind="default", assumption=S215_TEXT)
    assert msg == _ledger_text("`echo(` at line 543", one=True)


def test_s274s_scope_note_that_counts_the_removed_statements_is_refused(db, tmp_path):
    """Frame 297, night 156's s274: "removed 7 statements" with kind
    `scope` names no line, so it closed nothing. The door refuses it and
    names the seven lines."""
    sb, root = _developer(db, tmp_path)
    _index_path(db)
    # s274's write: the tail of `version_option` is gone from the tree.
    cut = DECORATORS.index("    if not param_decls:")
    tail = DECORATORS.index("\n\ndef help_option")
    (root / PATH).write_bytes((DECORATORS[:cut] + "    return None"
                               + DECORATORS[tail:]).encode("utf-8"))
    _night_note(sb, N274, [["version_option", x, 1] for x in S274_LINES])
    msg = _silent_refusal(sb, about_ref=PATH,
                          about_table="version_option callback body",
                          kind="scope", assumption=S274_TEXT)
    for x, n in zip(S274_LINES, (562, 565, 566, 567, 568, 569, 570)):
        assert f"`{x}` at line {n}" in msg


def test_s300s_note_is_refused_with_the_stored_lines(db, tmp_path):
    """Frame 297, night 156's s300, a message wake on bg_3: "removed logic
    for version detection and echo" names no line. The refusal lists the
    three stored lines, not the `output = ...` line the text showed
    (review 1, finding 4)."""
    sb, root = _developer(db, tmp_path)
    _index_path(db)
    _noted_then_refused(sb, root)
    _night_note(sb, N300, N300_LINES)
    msg = _silent_refusal(sb, about_ref=PATH, about_table="decisions",
                          kind="invented", assumption=S300_TEXT)
    # Pass 2 of frame 283's W1 a: the tree holds `if version is None:`, so
    # the refusal lists only the stored lines the tree lacks.
    assert msg == _ledger_text("`echo(` at line 555, `ctx.exit()` at line 559")
    assert "output = message" not in msg


# bg_2's row on night 156: eight stored lines, and a text that shows six.
BG2_KWARGS = ['kwargs.setdefault("is_flag", True)',
              'kwargs.setdefault("expose_value", False)',
              'kwargs.setdefault("is_eager", True)',
              'kwargs.setdefault("help", _("Show the version and exit."))',
              'kwargs["callback"] = callback',
              'return option(*param_decls, **kwargs)']
BG2_NOTE = ("This write removes or rewrites 6 statements that your text does not hold: "
            + ", ".join(f"`{x}` at line {n}" for x, n in zip(BG2_KWARGS, range(559, 565)))
            + ".")
BG2_LINES = ([["version_option.callback", "echo(", 1],
              ["version_option.callback", "ctx.exit()", 1]]
             + [["version_option", x, 1] for x in BG2_KWARGS])


def test_bg2s_eight_line_row_lists_the_stored_lines_the_tree_lacks(db, tmp_path):
    """Frame 297's review 2, finding 6: the replay of bg_2's row with s214's
    text. Frame 283's W1 a, pass 2: the refusal lists the stored lines the
    tree lacks, and no note closes the row, whatever line it names."""
    sb, root = _developer(db, tmp_path)
    _index_path(db)
    _noted_then_refused(sb, root)
    _night_note(sb, BG2_NOTE, BG2_LINES)
    for text in (S214_TEXT, "The write removes `echo(` on purpose.",
                 'The write removes `kwargs["callback"] = callback` on purpose.'):
        msg = _silent_refusal(sb, about_ref=PATH, about_table="code.source",
                              kind="default", assumption=text)
        assert msg == _ledger_text("`echo(`, `ctx.exit()`")


def test_a_nine_line_refusal_lists_the_lines_the_tree_lacks(db, tmp_path):
    """Frame 297's review 2, finding 4 listed the shown lines only. Pass 2
    of frame 283's W1 a: no line closes the note, so the refusal lists each
    stored line the tree lacks, `value_8` too."""
    sb, root = _developer(db, tmp_path)
    _index_path(db)
    _noted_then_refused(sb, root)
    lost = [(i, f"value_{i} = compute({i})") for i in range(1, 9)] + [
        (9, "return value_9")]
    note = f"This write removes or rewrites 9 statements: {api._lost_sentence(lost)}."
    _night_note(sb, note, [["f", h, 1] for _i, h in lost])
    shown = api._shown_lines(api._open_notes(sb.ctx)[PATH])
    assert "value_8 = compute(8)" not in shown and len(shown) == 8
    for text in (S214_TEXT, "The write removes `return value_9` on purpose."):
        msg = _silent_refusal(sb, about_ref=PATH, about_table="code.source",
                              kind="default", assumption=text)
        assert "`value_8 = compute(8)`" in msg and "`return value_9` at line 9" in msg
        assert msg.endswith(f"{SILENT}{LATER_STEP}")


def test_a_ledger_note_closes_no_restored_note_early(db, tmp_path):
    """Frame 297's review 2, finding 3, probe Q2b. A write puts the lines
    back, and a ledger note on another path lands. A silent whole-file write
    then takes `ctx.exit()` out. The note stays open, so the commit lands
    with the removal as a stray (frame 339). The other path's `x = 1` is
    gone too, so it is a second stray."""
    other = "src/click/other.py"
    sb, root = _developer(db, tmp_path)
    _index_path(db)
    db.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) VALUES "
               "(?, 'path', 'file')", (other,))
    db.commit()
    head = _git(root, "rev-parse", "HEAD")
    _noted_then_refused(sb, root)
    sb.call("code.write", path=PATH, start=546, end=550, text=RESTORED)
    sb.begin_reply()
    api._put_note(sb.ctx, other, {"note": "This write removes or rewrites 1 statement that "
                                  "your text does not hold: `x = 1` at line 1.",
                                  "lines": [["", "x = 1", 1]], "defs": [],
                                  "whole": [], "noted": "y"})
    (root / other).write_bytes(b"y = 2\n")
    # Frame 283's W1 a, pass 2: the note on the other path is refused too,
    # because it closes no removal of a base statement.
    with pytest.raises(ValueError):
        sb.call("ledger.log", about_ref=other, about_table="code.source",
                kind="default", assumption="other.py drops `x = 1` on purpose.")
    assert PATH in api._open_notes(sb.ctx)
    now = (root / PATH).read_text(encoding="utf-8")
    gone = "\n".join(ln for ln in now.split("\n") if ln.strip() != "ctx.exit()")
    sb.call("code.write", path=PATH, text=gone)
    sb.begin_reply()
    assert _git(root, "rev-parse", "HEAD") == head
    out = sb.call("code.commit", message="drop again")
    assert out["committed"] is True, out
    rows = [(w[2]["path"], w[2]["status"], w[2].get("note"))
            for w in sb.ctx.writes if w[0] == "touch_strays"]
    assert rows == [
        ("src/click/decorators.py::version_option.callback", "open",
         "removal: `ctx.exit()` at line 556"),
        ("src/click/other.py", "open", "removal: `x = 1` at line 1")], rows


def test_an_architects_note_on_the_noted_path_lands_and_closes_nothing(db, tmp_path):
    """Frame 297's review 1, finding 2: a message wake gives every role the
    running batch. Only the Developer holds code.write, so the door and the
    close fire for the Developer only."""
    sb, root = _developer(db, tmp_path)
    _index_path(db)
    _noted_then_refused(sb, root)
    for table, _rid, values in [w[:3] for w in sb.ctx.writes]:
        if table == "drop_notes":
            cols = ", ".join(values)
            db.execute(f"INSERT OR REPLACE INTO drop_notes ({cols}) VALUES "
                       f"({', '.join('?' for _ in values)})", list(values.values()))
    db.commit()
    arch = build("architect", db, batch_id="b1")
    out = arch.call("ledger.log", about_ref=PATH, about_table="code.source",
                    kind="default", assumption="The batch drops `ctx.exit()` "
                    "from the callback, which a reader may miss.")
    assert "id" in out
    assert PATH in api._open_notes(arch.ctx)


def test_a_note_after_a_restoring_write_lands(db, tmp_path):
    """Frame 297's review 1, finding 3, probe P3b: the write puts the lines
    back, so the door does not fire, and the honest note lands. The door
    only reads, so the commit door alone closes the note (review 2,
    finding 3)."""
    sb, root = _developer(db, tmp_path)
    _index_path(db)
    _noted_then_refused(sb, root)
    sb.call("code.write", path=PATH, start=546, end=550, text=RESTORED)
    sb.begin_reply()
    out = sb.call("ledger.log", about_ref=PATH, about_table="code.source",
                  kind="default", assumption="The callback appends the Python "
                  "version only when show_python is set.")
    assert "id" in out
    assert PATH in api._open_notes(sb.ctx)
    assert sb.call("code.commit", message="micro")["committed"] is True
    assert PATH not in api._open_notes(sb.ctx)


def test_a_note_after_the_committed_text_is_sent_again_lands(db, tmp_path):
    """Frame 297's review 1, finding 3, probe P3: the write sends the
    committed text again. The ledger door and the commit door give one
    answer: no note holds the path."""
    sb, root = _developer(db, tmp_path)
    _index_path(db)
    _noted_then_refused(sb, root)
    sb.call("code.write", path=PATH, text=DECORATORS)
    sb.begin_reply()
    out = sb.call("ledger.log", about_ref=PATH, about_table="code.source",
                  kind="default", assumption="The callback in version_option "
                  "prints the message and exits.")
    assert "id" in out
    assert sb.call("code.commit", message="none")["committed"] is False
    assert PATH not in api._open_notes(sb.ctx)


def test_an_entry_with_no_stored_line_names_the_write_route_only(db, tmp_path):
    """Frame 297's review 1, finding 6: no ledger note closes an entry with
    no line and no definition, so the commit door names code.write only."""
    sb, root = _developer(db, tmp_path)
    now = DECORATORS + "\n# dirty\n"
    (root / PATH).write_bytes(now.encode("utf-8"))
    api._put_note(sb.ctx, PATH, {"note": "This write drops 2 lines.", "lines": [],
                                 "defs": [], "whole": [], "noted": now})
    with pytest.raises(ValueError) as err:
        sb.call("code.commit", message="x")
    assert str(err.value).endswith(
        "Put the lines back with code.write, then commit in your next reply.")
    assert "ledger.log" not in str(err.value)


def test_a_held_entry_with_no_line_names_the_route_the_next_reply_takes(db, tmp_path):
    """Frame 339's review 1, finding 3, probe P4: the note of this reply
    holds no line and no definition. The next reply's commit is refused
    with the write route, so the first refusal names that route only."""
    sb, root = _developer(db, tmp_path)
    now = DECORATORS + "\n# dirty\n"
    (root / PATH).write_bytes(now.encode("utf-8"))
    note = "This write drops 2 lines."
    api._put_note(sb.ctx, PATH, {"note": note, "lines": [], "defs": [],
                                 "whole": [], "noted": now})
    sb.ctx.reply_notes[PATH] = note
    route = "Put the lines back with code.write, then commit in your next reply."
    with pytest.raises(ValueError) as first:
        sb.call("code.commit", message="x")
    assert str(first.value).startswith("your code.write in this reply"), first.value
    assert str(first.value).endswith(route), first.value
    assert "To keep the change" not in str(first.value)
    sb.begin_reply()
    with pytest.raises(ValueError) as later:
        sb.call("code.commit", message="x")
    assert str(later.value).endswith(route), later.value


def test_a_write_note_shows_only_the_lines_its_entry_stores(db, tmp_path):
    """Frame 297's review 1, finding 4: the filters keep a changed line out
    of the entry, so the note text no longer shows it."""
    sb, root = _developer(db, tmp_path)
    text = ('        if version is None and not show_python:\n'
            '            raise RuntimeError("no version")\n\n'
            '        base_message = message % {"prog": prog_name, "package": '
            'package_name, "version": version}\n'
            '        echo(\n            base_message,\n            color=ctx.color,\n'
            '        )')
    out = sb.call("code.write", path=PATH, start=541, end=556, text=text)
    stored = [x[1] for x in api._open_notes(sb.ctx)[PATH]["lines"]]
    assert "if version is None:" not in stored
    assert "ctx.exit()" in stored
    assert "`if version is None:`" not in out["dropped"]
    assert "`ctx.exit()`" in out["dropped"]


@pytest.mark.parametrize("autocrlf, eol", [("false", b"\n"), ("true", b"\r\n")])
def test_a_new_file_gets_the_line_ending_git_checks_out(db, tmp_path, autocrlf, eol):
    """Frame 297's review 2, finding 1: a new file gets the line ending a
    checkout of that tree gives, CRLF under `core.autocrlf=true`."""
    sb, root = _developer(db, tmp_path)
    _git(root, "config", "core.autocrlf", autocrlf)
    sb.call("code.write", path="src/click/extra.py", text="X = 1\nY = 2\n")
    assert (root / "src/click/extra.py").read_bytes() == b"X = 1" + eol + b"Y = 2" + eol


def _crlf_checkout(root):
    """The worktree as a night holds it: `core.autocrlf=true` and a CRLF
    checkout of an LF commit (review 2, probe Q1d)."""
    _git(root, "config", "core.autocrlf", "true")
    (root / PATH).unlink()
    _git(root, "checkout", "--", PATH)
    assert b"\r\n" in (root / PATH).read_bytes()


def test_a_write_into_a_crlf_file_keeps_crlf(db, tmp_path):
    """Frame 297's review 2, finding 1: the LF write made `_uncommitted` list
    a file that equals HEAD. The write keeps the file's own line ending."""
    sb, root = _developer(db, tmp_path)
    _crlf_checkout(root)
    changed = DECORATORS.replace("ctx.exit()", "ctx.exit()  # x", 1)
    sb.call("code.write", path=PATH, text=changed)
    raw = (root / PATH).read_bytes()
    assert raw.count(b"\r\n") == raw.count(b"\n")
    sb.call("code.write", path=PATH, text=DECORATORS)
    assert api._uncommitted(sb.ctx, root) == []


def test_a_one_line_change_in_a_crlf_file_is_a_one_line_diff(db, tmp_path):
    """Frame 297's review 2, finding 2, probe Q1b: a file committed with CRLF
    blobs. The LF write changed every line, and the diff is one line now."""
    sb, root = _developer(db, tmp_path)
    _git(root, "config", "core.autocrlf", "false")
    (root / PATH).write_bytes(DECORATORS.replace("\n", "\r\n").encode("utf-8"))
    _git(root, "commit", "-q", "-am", "crlf blobs")
    sb.call("code.write", path=PATH,
            text=DECORATORS.replace("ctx.exit()", "ctx.exit()  # x", 1))
    assert _git(root, "diff", "--numstat", "HEAD").split()[:2] == ["1", "1"]


def test_a_write_into_an_lf_file_keeps_lf(db, tmp_path):
    """Frame 297's review 2, finding 1: an LF file stays LF, whatever the
    tree's `core.autocrlf` says."""
    sb, root = _developer(db, tmp_path)
    _git(root, "config", "core.autocrlf", "true")
    sb.call("code.write", path=PATH,
            text=DECORATORS.replace("ctx.exit()", "ctx.exit()  # x", 1))
    assert b"\r" not in (root / PATH).read_bytes()


def test_a_note_about_a_criterion_that_mentions_the_path_lands(db, tmp_path):
    """Frame 297: the door reads `about_ref` only. A note about a criterion
    whose text mentions the noted path lands, and the note stays open, so
    the commit carries the removal as a stray (frame 339)."""
    sb, root = _developer(db, tmp_path)
    _noted_then_refused(sb, root)
    out = sb.call("ledger.log", about_ref="c1", about_table="criteria", kind="default",
                  assumption=f"The version string in {PATH} uses major.minor.micro.")
    assert "id" in out
    assert PATH in api._open_notes(sb.ctx)
    _lands_as_stray(sb, root)


def test_a_dropped_line_counts_only_inside_its_definition():
    """Frame 283's review 1, finding 2: `return x` dropped from `a` and
    written into `b` does not put the line back."""
    before = "def a():\n    x = 1\n    return x\n\n\ndef b():\n    return x\n"
    noted = "def a():\n    x = 1\n\n\ndef b():\n    return x\n"
    entry = api._note_entry("note", before, noted, [2])
    assert entry["lines"] == [["a", "return x", 1]]
    assert not api._restored(noted.replace("    return x\n", "    return x\n    return x\n"), entry)
    assert api._restored(before, entry)


def test_a_whole_file_note_closes_when_the_definitions_return():
    """Frame 283's review 1, finding 3: a whole-file note with no line holds
    the dropped definitions by name, and a comment does not close it."""
    before = "def a():\n    return 1\n\n\ndef b():\n    return 2\n"
    noted = "def a():\n    return 1\n"
    entry = api._note_entry("note", before, noted, [])
    assert entry["defs"] == ["b"]
    assert not api._restored(noted + "# b\n", entry)
    assert api._restored(before, entry)


def test_a_whole_file_drop_of_module_lines_stores_the_lines():
    """Frame 283's review 2, finding 2: a whole-file write that drops only
    module-level lines stores them, so a comment does not close the note."""
    before = ("X = 5\n\n\ndef a():\n    return 1\n\n\n"
              "if __name__ == '__main__':\n    a()\n")
    noted = "def a():\n    return 1\n"
    drop: list = []
    note = api._whole_drop(before.splitlines(), noted, gone_out=drop)
    assert note
    entry = api._note_entry(note, before, noted, drop)
    assert [x[1] for x in entry["lines"]] == [
        "X = 5", "if __name__ == '__main__':", "a()"]
    assert not api._restored(noted + "# kept\n", entry)
    assert api._restored(before, entry)


def test_a_dropped_definition_the_batch_added_opens_no_note(db, tmp_path):
    """Frame 283, pass 3: a line that the batch's base does not hold is no
    loss of the project's code. The result still says what the write
    removed, and the commit in the next reply lands."""
    sb, root = _developer(db, tmp_path)
    # A second change, so the write does not put the base back whole.
    added = "# batch\n" + DECORATORS + "\n\ndef added_here() -> int:\n    return 1\n"
    (root / PATH).write_bytes(added.encode("utf-8"))
    _git(root, "commit", "-q", "-am", "the batch adds a definition")
    n = len(DECORATORS.splitlines()) + 1
    out = sb.call("code.write", path=PATH, start=n, end=n + 4, text="\n")
    assert "added_here" in out["dropped"]
    # Review 6, finding 1: the result says the commit is not held.
    assert out["dropped"].endswith("No note is open, and the commit is not held.")
    assert api._open_notes(sb.ctx) == {}
    sb.begin_reply()
    assert sb.call("code.commit", message="take it out")["committed"] is True


# Frame 283's review 3: probes C, E, F and R3d, and the count's s192.
M = "m.py"
M_BASE = """def f():
    x = 1
    echo(x)
    return x


def keep():
    return 2
"""


def _module_repo(db, tmp_path, texts):
    """A worktree with one commit per text of `m.py`, and the sandbox."""
    root = tmp_path / "wt"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    for i, t in enumerate(texts):
        (root / M).write_bytes(t.encode("utf-8"))
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "-m", f"c{i}")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    return sb, root


def _opens_and_refuses(sb, out):
    assert out.get("dropped")
    assert M in api._open_notes(sb.ctx)
    with pytest.raises(ValueError):
        sb.call("code.commit", message="the removal")


def test_a_base_line_under_a_renamed_owner_opens_a_note(db, tmp_path):
    """Probe C: the batch renames `f` to `g`, and a write drops `echo(x)`."""
    sb, _root = _module_repo(db, tmp_path, [M_BASE, M_BASE.replace("def f", "def g")])
    out = sb.call("code.write", path=M, start=2, end=4, text="    return 1\n")
    _opens_and_refuses(sb, out)


def test_a_base_line_moved_into_a_nested_owner_opens_a_note(db, tmp_path):
    """Probe F: the batch nests `echo(x)` in `f.inner`, and a write drops it."""
    new = M_BASE.replace("    echo(x)", "    def inner():\n        echo(x)\n    inner()")
    sb, _root = _module_repo(db, tmp_path, [M_BASE, new])
    out = sb.call("code.write", path=M, start=3, end=4, text="        pass\n")
    _opens_and_refuses(sb, out)


def test_a_base_that_does_not_parse_keeps_every_line(db, tmp_path):
    """Probe E: the door cannot read the base, so the note opens."""
    sb, _root = _module_repo(db, tmp_path, [M_BASE + "def broken(:\n", M_BASE + "# c1\n"])
    out = sb.call("code.write", path=M, start=2, end=4, text="    return 1\n")
    _opens_and_refuses(sb, out)


def test_s192s_widened_except_tuple_is_no_dropped_line():
    """Night 149 s192: the write added `RuntimeError` to an `except` tuple.
    The new line holds every whole token of the old one, so it is kept."""
    entry = {"lines": [["run", "except (KeyboardInterrupt, EOFError):", 1]],
             "defs": [], "whole": []}
    text = ("def run():\n    try:\n        go()\n"
            "    except (KeyboardInterrupt, EOFError, RuntimeError):\n        stop()\n")
    assert api._changed_kept(entry, text) is False
    assert entry["lines"] == []


def test_a_line_whose_tokens_sit_across_two_lines_is_still_dropped():
    """The tokens of the old line must sit in one new line."""
    entry = {"lines": [["run", "except (KeyboardInterrupt, EOFError):", 1]],
             "defs": [], "whole": []}
    text = ("def run():\n    try:\n        go(KeyboardInterrupt)\n"
            "    except EOFError:\n        stop()\n")
    assert api._changed_kept(entry, text) is True
    assert len(entry["lines"]) == 1


def test_a_line_of_two_tokens_is_never_kept_by_the_subset_rule():
    """Pass 4b: `return x` dropped beside `return x + 1` is still a drop."""
    entry = {"lines": [["f", "return x", 1]], "defs": [], "whole": []}
    assert api._changed_kept(entry, "def f(x):\n    return x + 1\n") is True
    assert entry["lines"] == [["f", "return x", 1]]


def test_a_tail_note_shows_its_first_stored_line(db, tmp_path):
    """Review 4, finding 2: the refusal text always shows a stored line.
    Pass 3 of frame 283's W1 a deleted the close rule this test also held."""
    sb, _root = _module_repo(db, tmp_path, [M_BASE, M_BASE + "# c1\n"])
    out = sb.call("code.write", path=M, start=2, end=4, text="    return 1\n")
    entry = api._open_notes(sb.ctx)[M]
    shown = api._shown_lines(entry)
    assert shown and f"`{shown[0]}`" in out["dropped"]


def test_an_unchanged_line_does_not_hide_a_dropped_line():
    """Review 4, finding 1: click's lines 506 to 560 without `if version is
    None:`. The kept line `if version is None and package_name is not
    None:` is an old line, so it is no changed line, and the note opens."""
    old = DECORATORS.splitlines()
    i = old.index("        if version is None:")
    text = "\n".join(old[505:i] + old[i + 1:560]) + "\n"
    entry = {"lines": [["version_option.callback", "if version is None:", 1]],
             "defs": [], "whole": []}
    assert api._changed_kept(entry, text, DECORATORS) is True
    assert len(entry["lines"]) == 1


def test_a_repeated_word_does_not_meet_the_token_floor():
    """Review 4, finding 1: `x = int(x)` has two distinct tokens."""
    entry = {"lines": [["f", "x = int(x)", 1]], "defs": [], "whole": []}
    assert api._changed_kept(entry, "def f(x):\n    return int(x)\n") is True


def test_s192s_widened_tuple_through_code_write_commits_in_the_reply(db, tmp_path):
    """Review 4, finding 4: s192's shape end to end. The changed line is no
    dropped line, so no note opens, and the commit in the reply lands."""
    base = ("def run():\n    try:\n        go()\n"
            "    except (KeyboardInterrupt, EOFError):\n        stop()\n")
    sb, root = _module_repo(db, tmp_path, [base, base + "# c1\n"])
    out = sb.call("code.write", path=M, start=1, end=5, text=(
        "    try:\n        go()\n"
        "    except (KeyboardInterrupt, EOFError, RuntimeError):\n        stop()\n"))
    assert "RuntimeError" in (root / M).read_text(encoding="utf-8")
    # Review 5, finding 2: the seat is not told that it removed the line.
    assert "dropped" not in out
    assert api._open_notes(sb.ctx) == {}
    assert sb.call("code.commit", message="widen the except")["committed"] is True


def test_a_shown_line_with_a_backtick_gets_a_double_fence():
    """Review 5, finding 3: a backtick in the line cannot end the fence."""
    line = "return f'`{x}` \"q\"'"
    assert api._quote(line) == f"``{line}``"
    assert api._quote("return x") == "`return x`"
    # Review 6, finding 2: two backticks in a row get a fence of three.
    assert api._quote("return 'a``b'") == "```return 'a``b'```"
    assert api._quote("`x` = 1") == "`` `x` = 1 ``"
    entry = {"note": f"This write drops 1 line. It drops {api._quote(line)}.",
             "lines": [["f", line, 1]]}
    assert api._shown_lines(entry) == [line]


def test_tick_the_lost_sentence_fences_a_line_with_backticks():
    """Review 6, finding 3, probe TICK: the span sentence uses `_quote`."""
    line = 'log("a `b` c", x)'
    out = api._lost_sentence([(3, line)])
    assert out == f"``{line}`` at line 3"
    entry = {"note": out, "lines": [["f", line, 1]]}
    assert api._shown_lines(entry) == [line]


def test_t1_the_whole_file_sentence_fences_a_line_with_backticks():
    """Review 6, finding 3, probe T1: the whole-file sentence uses `_quote`."""
    line = 'log("a `b` c", x)'
    before = f"{line}\n\n\ndef a():\n    return 1\n"
    note = api._whole_drop(before.splitlines(), "def a():\n    return 1\n")
    assert f"from ``{line}``;" in note
