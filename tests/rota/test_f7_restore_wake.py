"""
The `touch_mistaken` wake shows the Developer the removed base lines (F7,
pass 3).

Night 172 (2026-10-28): bg_3 asked for one docstring example in
`format_filename`. The commit 128bec7e rewrote the body too, and the
Architect s262 judged the removal a mistake. The Developers s263, s264 and
s267 woke on `tick:touch_mistaken` to put the base lines back. The wake held
no base text and no diff, and the row's note named the lost block by its
first line only. Each seat wrote the head's own text, and each commit said
"nothing changed" (`plans/f7-night172-read.md`, sections 1 and 3).

The rows are copied from `.rota/clickI_night172.db`, read with `mode=ro`,
and rebuilt inline. The tree is rebuilt from a fixture, so the test does not
need the clickI checkout the night edited.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from rota.core import predicates as P
from rota.core.db import init_db
from rota.core.loop import _batch_of
from rota.core.runner import (build_prompt, push_working_set, resolve_inbound,
                              session_sandbox)

PATH = "src/click/utils.py"
GRAIN = f"{PATH}::format_filename"
# clickI's utils.py. Its `format_filename` is the same as at b8fd86b, the
# base of bg_3 on night 172.
BASE = (Path(__file__).parent / "fixtures"
        / "night124_utils_617055787d.txt").read_bytes().decode("utf-8")
# The end of the base docstring and the base body, lines 467 to 481.
BASE_BODY = '''\
                    path that leads up to it.
    """
    if shorten:
        filename = os.path.basename(filename)
    else:
        filename = os.fspath(filename)

    if isinstance(filename, bytes):
        filename = filename.decode(sys.getfilesystemencoding(), "replace")
    else:
        filename = filename.encode("utf-8", "surrogateescape").decode(
            "utf-8", "replace"
        )

    return filename
'''
# The same span at 128bec7e: the asked example, and the rewritten body.
HEAD_BODY = '''\
                    path that leads up to it.

    Example:
        >>> format_filename("a/b/c.txt", shorten=True)
        'c.txt'

    """
    # Convert bytes or PathLike to string if necessary
    if isinstance(filename, (bytes, bytearray)):
        try:
            filename = filename.decode(sys.getfilesystemencoding())
        except UnicodeError:
            filename = filename.decode("utf-8", "replace")
    elif hasattr(filename, "__fspath__"):
        filename = os.fspath(filename)

    # Handle shorten parameter
    if shorten and "/" in filename:
        filename = filename.split("/")[-1]

    return filename
'''
# The `mistake` row of night 172, at 128bec7e: s262's judgement.
NOTE = ("removal: `filename = os.fspath(filename)` at line 471, "
        "`if isinstance(filename, bytes):` at line 473 The removal of the old "
        "logic for handling bytes and encoding is a mistake. The request only "
        "asked for an example in the docstring, not a rewrite of the function. "
        "The removal touches a definition not named in the request or any "
        "criterion.")
ITEM = ("With shorten set to True, the path a/b/c.txt is displayed as c.txt "
        "in the docstring of format_filename.")
CRITERIA = (
    ("c_1_format_filename_example",
     'The docstring of format_filename must include an example demonstrating '
     'that when shorten=True, a path like "a/b/c.txt" is displayed as "c.txt".'),
    ("c_2_format_filename_example",
     "The docstring of format_filename must include an example that explicitly "
     "shows both the input path and the resulting shortened output to verify "
     "the behavior."),
    ("c_3_format_filename_example",
     'The docstring must include an example showing that when shorten=True, a '
     'path like "a/b/c.txt" is displayed as "c.txt".'),
)


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t",
                           "-c", "user.email=t@t", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def _night172(tmp_path: Path):
    """bg_3 at 128bec7e with s262's `mistake` row. The project root stays
    at the base, so the batch forks from the base commit."""
    assert BASE.count(BASE_BODY) == 1
    root = tmp_path / "wt"
    (root / PATH).parent.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / PATH).write_bytes(BASE.encode("utf-8"))
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    proj = tmp_path / "proj"
    subprocess.run(["git", "clone", "-q", str(root), str(proj)], check=True)
    (root / PATH).write_bytes(BASE.replace(BASE_BODY, HEAD_BODY).encode("utf-8"))
    _git(root, "commit", "-q", "-am",
         "Implement shorten=True logic in format_filename")
    head = _git(root, "rev-parse", "HEAD")

    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)",
                 (str(proj),))
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('format_filename_example', ?, 'in_scope', "
                 "'approved', 1, 1)", (ITEM,))
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk_1_format_filename_example', 'format_filename_example', ?)",
                 (ITEM.lower().rstrip("."),))
    for cid, text in CRITERIA:
        conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                     "VALUES (?, 'tk_1_format_filename_example', ?, ?)",
                     (cid, text, json.dumps([GRAIN])))
    conn.execute("INSERT INTO batches (id, item_id, status, worktree, "
                 "head_commit) VALUES ('bg_3', 'format_filename_example', "
                 "'running', ?, ?)", (str(root), head))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_3', 'tk_1_format_filename_example')")
    conn.execute("INSERT INTO touch_strays (batch_id, commit_sha, path, status, "
                 "note) VALUES ('bg_3', ?, ?, 'mistake', ?)", (head, GRAIN, NOTE))
    conn.commit()
    return conn


def _first_prompt(conn) -> str:
    """The wake's user prompt, composed the way `runner.run_session` does."""
    [wake] = P.touch_mistaken(conn)
    sb = session_sandbox(conn, wake, batch_id=_batch_of(conn, wake))
    pushed = push_working_set(wake.role, sb, wake)
    _, user = build_prompt(wake.role, sb, wake, pushed, "",
                           resolve_inbound(conn, wake))
    return user


def test_the_restore_wake_shows_each_removed_base_line(tmp_path):
    """The note names the lost block by its first line, and the head holds
    nearly the same line. The wake must show the lines to put back."""
    user = _first_prompt(_night172(tmp_path))
    assert "[code.diff]" in user
    assert 'filename.encode("utf-8", "surrogateescape")' in user
    assert "filename = os.path.basename(filename)" in user


def _written(text: str):
    from rota.core.runner import RunOutcome
    from rota.llm import toolproto
    call = toolproto.ToolCall("code.write", {"path": PATH, "start": 441,
                                             "end": 487, "text": text})
    return RunOutcome("s1", True, 1, completions=[""], system="",
                      native=[[call]], offered=["code.write"])


def test_the_case_grader_reads_the_text_of_each_write():
    """s264 and s267 sent the docstring, which holds `surrogateescape`, and
    the head's body. `L1-DV-put-back-a-removed-block` asks for the base
    body's `.encode(` too, so their writes stay red."""
    from rota.testkit import fixtures
    case = {"expect": {"write_includes": [".encode(", "surrogateescape"]}}
    docstring = '    """... with ``errors="surrogateescape"``.\n    """\n'
    assert fixtures._write_includes(case, _written(docstring + HEAD_BODY), 0)
    assert fixtures._write_includes(case, _written(docstring + BASE_BODY), 0) == []
    assert fixtures._write_includes({"expect": {}}, _written(""), 0) == []
