"""
A removal of a base statement lands on a ruling, never on a note alone
(frame 283, W1 a).

Night 158 (2026-10-21): the Developer s279 of batch bg_3 wrote lines 540
to 555 of `src/click/decorators.py`, and the write dropped `ctx.exit()`
from the callback of `version_option`. The commit door refused. The seat
then logged "ctx.exit() at line 550 was unreachable after echo() call",
the note closed the `drop_notes` row as `restored`, and bb7c4492 landed
the removal. `echo` returns, so `--version` then ran the command body. A
note is the seat's own claim. Only a criterion, the request or the
principal's words admit the removal.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import api, prompts

PATH = "src/click/decorators.py"

# The file at 7856ed8, the head s279 wrote on, and at 75cf8ed, the commit
# bg_3 forked from. Both from `D:/repos/_AI/sample_repos/clickI` by
# `git show <sha>:src/click/decorators.py`.
BASE = (Path(__file__).parent / "fixtures"
        / "night158_decorators_7856ed8.txt").read_bytes()
FORK = (Path(__file__).parent / "fixtures"
        / "night158_decorators_75cf8ed.txt").read_bytes()

# s279's texts, from `tool_calls` and `turns` of `.rota/clickI_night158.db`.
ECHO = ('        echo(\n'
        '            message % {"prog": prog_name, "package": package_name, '
        '"version": version} + (f" Python {python_version}" if python_version '
        'else ""),\n'
        '            color=ctx.color,\n'
        '        )')
BACK = ('        if version is None:\n'
        '            raise RuntimeError(\n'
        '                f"Could not determine the version for {package_name!r} '
        'automatically."\n'
        '            )\n'
        '\n'
        '        # Append Python version if show_python is True\n'
        '        python_version = ""\n'
        '        if show_python:\n'
        '            import sys\n'
        '            python_version = f"{sys.version_info.major}.'
        '{sys.version_info.minor}.{sys.version_info.micro}"\n'
        '\n' + ECHO + '\n'
        '        ctx.exit()\n')
NOTE = "removed ctx.exit() at line 550 which was unreachable after echo()"
SCOPE = "ctx.exit() at line 550 was unreachable after echo() call, removed in write"
MESSAGE = ("Fix show_python output format to include 'Python' prefix and "
           "restore ctx.exit()")

REFUSAL = ("src/click/decorators.py: this commit removes `ctx.exit()` at line "
           "550, and no criterion, request or ruling of the principal names it. "
           "The team's note does not discharge a removal. Put the line back "
           "with code.write and commit, or send msg.escalate_architect and name "
           "the removal.")


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES ('version_option_show_python','version_option shows the "
                 "Python version','in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','version_option_show_python','show_python')")
    # cr_3 of bg_3, as night 158 holds it in substance.
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('cr_3','tk1','Without show_python, the option must behave "
                 "exactly as it does today.')")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) VALUES "
                 "('bg_3','version_option_show_python','running','abc123')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('bg_3','tk1')")
    # The night's index held the path, so `about_ref` resolves to it.
    conn.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) VALUES "
                 "(?, 'path', 'file')", (PATH,))
    conn.commit()
    return conn


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t",
                           "-c", "user.email=t@t", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def _developer(db, tmp_path):
    """bg_3's worktree: the fork 75cf8ed, then the batch's head 7856ed8 as
    one commit, and the Developer's sandbox. With no project root the base
    is HEAD~1, the fork, so the batch's own duplicate lines open no note."""
    root = tmp_path / "wt"
    (root / PATH).parent.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / PATH).write_bytes(FORK)
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "75cf8ed")
    (root / PATH).write_bytes(BASE)
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "7856ed8")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'bg_3'", (str(root),))
    db.commit()
    sb = build("developer", db, batch_id="bg_3", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    return sb, root


def _call(sb, fn, **args):
    """One call of the record. A refusal is a result, as the seat read it."""
    try:
        return sb.call(fn, **args)
    except ValueError as err:
        return {"refused": str(err)}


def _replay(sb):
    """s279's tool calls, seq 15 to 26, one reply per turn of the record.
    Returns the result of the last commit, seq 26.

    The record's three writes back, seq 18, 24 and 25, were refused at the
    span and changed nothing. The replay leaves them out: their "To add
    after it" offer fails the follow check of frame 144, the cut door's
    finding 2, which is not this frame's door."""
    out = _call(sb, "code.write", path=PATH, start=540, end=555, text=ECHO)
    assert out["dropped"] == ("This write removes 1 statement that your text "
                              "does not hold: `ctx.exit()` at line 550.")
    sb.begin_reply()
    assert "refused" in _call(sb, "code.commit", message=MESSAGE)
    sb.begin_reply()
    log = {"about_ref": PATH, "about_table": "version_option callback"}
    _call(sb, "ledger.log", kind="assumption", assumption=NOTE, **log)
    assert "refused" in _call(sb, "code.commit", message=MESSAGE)
    sb.begin_reply()
    _call(sb, "ledger.log", kind="fault", assumption=NOTE, **log)
    sb.begin_reply()
    _call(sb, "ledger.log", kind="scope", assumption=SCOPE, **log)
    sb.begin_reply()
    return _call(sb, "code.commit", message=MESSAGE)


def _row(sb) -> dict:
    """The last staged `drop_notes` value of the path."""
    return [w[2] for w in sb.ctx.writes
            if w[0] == "drop_notes" and w[2]["path"] == PATH][-1]


def test_s279s_commit_after_its_false_note_is_refused(db, tmp_path):
    """s279's sequence: the scope note closes the row as `restored`, and the
    tree still lacks `ctx.exit()`. bb7c4492's commit is refused."""
    sb, root = _developer(db, tmp_path)
    head = _git(root, "rev-parse", "HEAD")
    out = _replay(sb)
    assert _row(sb)["status"] == "restored"
    assert "ctx.exit()" not in (root / PATH).read_text(encoding="utf-8").split(
        "def custom_version_option")[0].split("color=ctx.color,")[-1]
    assert out == {"refused": REFUSAL}
    assert _git(root, "rev-parse", "HEAD") == head


def test_the_removal_lands_when_a_criterion_names_it(db, tmp_path):
    """The same removal, where a criterion of the batch names `ctx.exit()`:
    the criterion is a ruling, so the commit lands."""
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('cr_4','tk1',"
               "'After --version, the callback no longer calls ctx.exit(), so "
               "the command body runs.')")
    db.commit()
    sb, _root = _developer(db, tmp_path)
    assert _replay(sb)["committed"] is True


def test_the_removal_lands_when_the_principal_names_the_line(db, tmp_path):
    """The same removal, where a landed ruling of the principal names the
    line: his words are a ruling, so the commit lands."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_text, seq) VALUES ('m1','t1','principal','liaison','answer',"
               "'x',1)")
    db.execute("INSERT INTO rulings (id, ask_id, words, status) VALUES "
               "('r1','m1','Take ctx.exit() out of the version callback.','landed')")
    db.commit()
    sb, _root = _developer(db, tmp_path)
    assert _replay(sb)["committed"] is True


def test_a_restored_row_with_the_line_gone_from_the_tree_is_refused(db, tmp_path):
    """The door reads the tree, not the row. A landed row at `restored`
    with `ctx.exit()` absent from the uncommitted tree refuses the commit."""
    sb, root = _developer(db, tmp_path)
    text = BASE.decode("utf-8")
    gone = text.replace("        )\n        ctx.exit()\n", "        )\n", 1)
    assert gone != text
    (root / PATH).write_bytes(gone.encode("utf-8"))
    db.execute("INSERT INTO drop_notes (batch_id, path, status, note, lines, defs, "
               "whole, noted) VALUES ('bg_3', ?, 'restored', ?, ?, '[]', '[]', ?)",
               (PATH, "This write removes 1 statement that your text does not "
                "hold: `ctx.exit()` at line 550.",
                json.dumps([["version_option.callback", "ctx.exit()", 1]]), gone))
    db.commit()
    sb = build("developer", db, batch_id="bg_3", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    head = _git(root, "rev-parse", "HEAD")
    with pytest.raises(ValueError) as err:
        sb.call("code.commit", message="micro")
    assert str(err.value) == REFUSAL
    assert _git(root, "rev-parse", "HEAD") == head


def test_a_restored_row_with_the_line_in_the_tree_lets_the_commit_land(db, tmp_path):
    """A row at `restored` whose line the tree holds blocks nothing."""
    sb, root = _developer(db, tmp_path)
    (root / PATH).write_bytes(BASE + b"\n# kept\n")
    db.execute("INSERT INTO drop_notes (batch_id, path, status, note, lines, defs, "
               "whole, noted) VALUES ('bg_3', ?, 'restored', '', ?, '[]', '[]', '')",
               (PATH, json.dumps([["version_option.callback", "ctx.exit()", 1]])))
    db.commit()
    sb = build("developer", db, batch_id="bg_3", mode="tests_failing",
               allow=prompts.mode_tools("developer", "tests_failing"))
    assert sb.call("code.commit", message="micro")["committed"] is True
