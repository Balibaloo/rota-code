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

STEP = ("You sent this commit before you read this note. If the tree now "
        "holds what the item asks for, commit in your next reply. If it does "
        "not, write the lines back, then commit in your next reply.")

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


def _developer(db, tmp_path):
    """A worktree at the commit s282 wrote on, and the Developer's sandbox."""
    root = tmp_path / "wt"
    (root / PATH).parent.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / PATH).write_bytes(DECORATORS.encode("utf-8"))
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "c0")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    return sb, root


def test_s282s_commit_beside_the_noted_write_is_refused(db, tmp_path):
    """s282's reply: the write gets the note, and the commit is refused with
    the note quoted. HEAD does not move, and the commit in the next reply
    lands."""
    sb, root = _developer(db, tmp_path)
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
    sb.begin_reply()
    assert sb.call("code.commit", message="the removal")["committed"] is True


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


def test_the_commit_in_the_reply_after_the_noted_write_lands(db, tmp_path):
    """The seat read the note before its next reply, so that commit lands."""
    sb, _ = _developer(db, tmp_path)
    out = sb.call("code.write", path=PATH, start=546, end=556, text=S282_TEXT)
    assert out["dropped"] == S282_NOTE
    sb.begin_reply()
    assert sb.call("code.commit", message="the removal")["committed"] is True


def test_the_dry_run_of_the_noted_write_records_nothing(db, tmp_path):
    """Frame 136's dry run writes nothing and offers nothing, so it records
    no note, and a commit after it is not refused for one."""
    sb, root = _developer(db, tmp_path)
    assert api._admits(sb.ctx, PATH, S282_TEXT, 546, 556) is True
    assert sb.ctx.reply_notes == {}
    assert (root / PATH).read_bytes() == DECORATORS.encode("utf-8")
    assert sb.call("code.commit", message="nothing")["committed"] is False
