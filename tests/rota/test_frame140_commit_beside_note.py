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
S282_NOTE = ('This write removes 3 statements that your text does not hold: '
             '`base_message = message % {"prog": prog_name, "package": pack` '
             'at line 546, `echo(` at line 551, `ctx.exit()` at line 555.')

STEP = ("You sent this commit before you read this note. If the tree holds "
        "those lines again, commit in your next reply. If it does not, write "
        "the lines back, then commit in your next reply.")

# The refusal of a commit in a reply after the noted one (frame 283).
LATER = ("a code.write in an earlier reply returned a note, and the tree "
         "still does not hold those lines.")
LATER_STEP = ("Put the lines back with code.write, or log the removal with "
              "ledger.log naming the path and the lines, then commit in your "
              "next reply.")

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


def test_s388s_commit_in_the_next_reply_with_no_write_is_refused(db, tmp_path):
    """Frame 283. Night 154, s388: the commit beside the noted write was
    refused, and the commit in the next reply, with no write between, landed
    a90c7495 without `echo(version_msg)`. The note stays open until a write
    puts the lines back, so that commit is refused too."""
    sb, root = _developer(db, tmp_path)
    head = _git(root, "rev-parse", "HEAD")
    out = sb.call("code.write", path=PATH, start=546, end=556, text=S282_TEXT)
    assert out["dropped"] == S282_NOTE
    with pytest.raises(ValueError):
        sb.call("code.commit", message="micro")
    sb.begin_reply()
    with pytest.raises(ValueError) as err:
        sb.call("code.commit", message="Add show_python flag")
    msg = str(err.value)
    assert msg.startswith(LATER)
    assert f"{PATH}: {S282_NOTE}" in msg
    assert msg.endswith(LATER_STEP)
    assert _git(root, "rev-parse", "HEAD") == head


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


def test_s340s_commit_in_the_reply_after_the_unchanged_write_is_refused(db, tmp_path):
    """Frame 283, s340's own turns: turn 13 sent the same text alone, and
    turn 14 sent the commit alone. The commit of turn 14 is refused, and so
    is every commit after it while the lines are gone."""
    sb, root = _developer(db, tmp_path)
    head = _git(root, "rev-parse", "HEAD")
    noted = _noted_then_refused(sb, root)
    assert sb.call("code.write", path=PATH, text=noted)["dropped"] == S282_NOTE
    sb.begin_reply()
    for _ in range(2):
        with pytest.raises(ValueError) as err:
            sb.call("code.commit", message="Add show_python flag to version_option")
        assert str(err.value).startswith(LATER)
        assert f"{PATH}: {S282_NOTE}" in str(err.value)
        sb.begin_reply()
    assert _git(root, "rev-parse", "HEAD") == head


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


def test_a_ledger_note_that_names_every_dropped_statement_closes_the_note(db, tmp_path):
    """Frame 283's ends-when: a meant removal is committed after a landed
    note. The ledger note names the path and each of the three dropped
    statements, so the commit after it lands."""
    sb, root = _developer(db, tmp_path)
    _noted_then_refused(sb, root)
    lines = [x[1] for x in api._open_notes(sb.ctx)[PATH]["lines"]]
    assert [x[:60] for x in lines] == [BASE_HEAD, "echo(", "ctx.exit()"]
    sb.call("ledger.log", about_ref="c1", about_table="criteria", kind="default",
            assumption=f"The item asks for the removal: {PATH} no longer "
                       f"holds `{BASE_HEAD}`, `echo(` and `ctx.exit()`.")
    assert sb.call("code.commit", message="the removal")["committed"] is True


def test_a_ledger_note_that_names_one_shown_statement_closes_the_note(db, tmp_path):
    """Frame 283's review 3, finding 2: one line that the note shows closes
    the note. This replaces review 1's rule of every line, because the seat
    cannot quote a line the note never showed."""
    sb, root = _developer(db, tmp_path)
    _noted_then_refused(sb, root)
    sb.call("ledger.log", about_ref="c1", about_table="criteria", kind="default",
            assumption=f"{PATH} keeps one `echo(` call for the version.")
    assert sb.call("code.commit", message="the removal")["committed"] is True


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
    with pytest.raises(ValueError) as err:
        sb.call("code.commit", message="the removal")
    assert str(err.value).startswith(LATER)


def test_a_second_session_on_the_worktree_sees_the_note(db, tmp_path):
    """Frame 283's review 1, finding 6: the note lives per batch and path in
    `drop_notes`, so a retry session's commit is refused too."""
    sb, root = _developer(db, tmp_path)
    head = _git(root, "rev-parse", "HEAD")
    _noted_then_refused(sb, root)
    # The rows the first session's commit lands, as `session_commit` does.
    for table, _rid, values in [w[:3] for w in sb.ctx.writes]:
        if table == "drop_notes":
            cols = ", ".join(values)
            db.execute(f"INSERT OR REPLACE INTO drop_notes ({cols}) VALUES "
                       f"({', '.join('?' for _ in values)})", list(values.values()))
    db.commit()
    sb2 = build("developer", db, batch_id="b1", mode="tests_failing",
                allow=prompts.mode_tools("developer", "tests_failing"))
    with pytest.raises(ValueError) as err:
        sb2.call("code.commit", message="the removal")
    assert str(err.value).startswith(LATER)
    assert _git(root, "rev-parse", "HEAD") == head


def test_a_ledger_note_that_names_no_dropped_statement_leaves_it_open(db, tmp_path):
    """Frame 283: a ledger note that names the path and none of the dropped
    statements does not close the note, so the commit is refused."""
    sb, root = _developer(db, tmp_path)
    head = _git(root, "rev-parse", "HEAD")
    _noted_then_refused(sb, root)
    sb.call("ledger.log", about_ref="c1", about_table="criteria", kind="default",
            assumption=f"The version string in {PATH} uses major.minor.micro.")
    with pytest.raises(ValueError) as err:
        sb.call("code.commit", message="the removal")
    assert str(err.value).startswith(LATER)
    assert str(err.value).endswith(LATER_STEP)
    assert _git(root, "rev-parse", "HEAD") == head


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


def test_a_ledger_word_that_holds_the_line_as_a_substring_closes_nothing(db, tmp_path):
    """Frame 283's review 2, finding 3: "bypass" does not name `pass`."""
    sb, _root = _developer(db, tmp_path)
    api._put_note(sb.ctx, "src/m.py", {"note": "`pass` at line 1", "lines": [["", "pass", 1]],
                                       "defs": [], "whole": [], "noted": ""})
    api._close_logged_notes(sb.ctx, "src/m.py: the bypass is kept")
    assert "src/m.py" in api._open_notes(sb.ctx)
    api._close_logged_notes(sb.ctx, "src/m.py: the removal of `pass` is meant")
    assert api._open_notes(sb.ctx) == {}


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


def test_a_ledger_that_names_the_shown_line_of_a_whole_file_note_closes_it(db, tmp_path):
    """Probe R3d: the whole-file note of three module lines shows `X = 5`
    alone, and a ledger that names `X = 5` closes the note."""
    sb, _root = _developer(db, tmp_path)
    before = ("X = 5\n\n\ndef a():\n    return 1\n\n\n"
              "if __name__ == '__main__':\n    a()\n")
    noted = "def a():\n    return 1\n"
    drop: list = []
    note = api._whole_drop(before.splitlines(), noted, gone_out=drop)
    entry = api._note_entry(note, before, noted, drop)
    assert len(entry["lines"]) == 3 and "`X = 5`" in note
    api._put_note(sb.ctx, M, entry)
    api._close_logged_notes(sb.ctx, f"{M}: the removal of `X = 5` and the main block is meant")
    assert api._open_notes(sb.ctx) == {}


def test_a_ledger_closes_a_span_note_only_on_a_line_the_note_shows(db, tmp_path):
    """A span note of ten lines shows eight. The ninth line closes nothing,
    because the seat never saw it. The first line closes the note."""
    sb, _root = _developer(db, tmp_path)
    lost = [(i, f"value_{i} = compute({i})") for i in range(1, 11)]
    note = f"This write removes 10 statements: {api._lost_sentence(lost)}."
    assert "value_9" not in note and "value_8" in note
    api._put_note(sb.ctx, M, {"note": note, "lines": [["f", h, 1] for _i, h in lost],
                              "defs": [], "whole": [], "noted": ""})
    api._close_logged_notes(sb.ctx, f"{M}: the removal of `value_9 = compute(9)` is meant")
    assert M in api._open_notes(sb.ctx)
    api._close_logged_notes(sb.ctx, f"{M}: the removal of `value_1 = compute(1)` is meant")
    assert api._open_notes(sb.ctx) == {}


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


def test_a_note_that_shows_no_stored_line_closes_on_the_path_alone(db, tmp_path):
    """Pass 4b: the seat saw no line to quote, so the path is enough."""
    sb, _root = _developer(db, tmp_path)
    api._put_note(sb.ctx, M, {"note": "This write drops 4 lines after it.",
                              "lines": [["f", "value = compute(1)", 1]],
                              "defs": [], "whole": [], "noted": ""})
    api._close_logged_notes(sb.ctx, "other.py: nothing is meant")
    assert M in api._open_notes(sb.ctx)
    api._close_logged_notes(sb.ctx, f"{M}: the tail removal is meant")
    assert api._open_notes(sb.ctx) == {}
