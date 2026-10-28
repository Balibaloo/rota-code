"""Fact F26: the guess stamp and the landed commit, for the night instruments.

`api.code_stamp` is the one reader of a page's `code:<message>` stamp, and
`nightcount.landed_heads` is the one reader of a landed commit in a prompt.
The night report and the night count read through them (rule C76, the
audit of 2026-10-27-b, F26).
"""
from __future__ import annotations

import ast
from pathlib import Path

from rota.core.db import connect_readonly, init_db
from rota.tools import nightcount, nightreport
from rota.tools.nightcount import count
from tests.rota.test_nightreport import GUESS, _guess_night, _night, _report, _section

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "rota"


def test_the_guess_section_reads_the_stamp_through_code_stamp(tmp_path, monkeypatch):
    """M0 counts the pages that `code_stamp` says carry a code line. The old
    rule read the `config` row by its own `_config` and ignored the reader."""
    from rota.roles import api

    path, _ = _guess_night(tmp_path)
    monkeypatch.setattr(api, "code_stamp",
                        lambda conn, mid: {"guess:it_1": {"guess": [1, ""]}})
    lines = _section(_report(path, log=tmp_path / "night200.log"), GUESS)
    assert "M0: 2 of 2 sign-off pages carry a code line" in lines


def test_the_batch_commits_read_the_landed_commit_through_landed_heads(tmp_path, monkeypatch):
    """The batch section lists the shas that `landed_heads` reads. The old
    rule read the feedback line by its own `COMMIT_RE`."""
    path = _night(tmp_path)
    monkeypatch.setattr(nightcount, "landed_heads", lambda text: [])
    batch = next(l for l in _report(path) if l.startswith("bg_1 status="))
    assert "commits=1" in batch


READ = 'OK code.status -> {"head_commit": "cccccccc1111", "dirty": []}'
LANDED = ('OK code.commit -> {"committed": true, "head_commit": '
          '"dddddddd2222", "touched": ["src/a.py"]}')
INVENTED = "TOOL: code.write(path='src/a.py', text='x')\n\nOK code.write ->"
FEEDBACK = ("You wrote tool results into your own reply -- the lines beginning "
            "`OK ...` or `ERROR ...`. Those did not come from me and nothing behind them ran.")


def test_a_read_that_names_a_head_is_not_a_landed_commit(tmp_path):
    """A tail with one landed commit and one read result names one sha. The
    old rule took every `head_commit` once any commit landed."""
    conn = init_db(tmp_path / "clickI.db")
    conn.execute("INSERT INTO sessions (id, role, wake_kind, wake_detail, committed, seq, "
                 "mode, model) VALUES ('s1', 'developer', 'tick:write', '', 1, 1, "
                 "'normal', 'm')")
    conn.execute("INSERT INTO turns (session_id, seq, system, user, completion, ms) "
                 "VALUES ('s1', 1, 'brief', 'the brief', ?, 0)", (INVENTED,))
    conn.execute("INSERT INTO turns (session_id, seq, system, user, completion, ms) "
                 "VALUES ('s1', 2, 'brief', ?, 'done', 0)",
                 ("\n\n".join(["the brief", INVENTED, FEEDBACK, READ, LANDED]),))
    conn.commit()
    conn.close()
    c = count(connect_readonly(tmp_path / "clickI.db"))
    assert c["ran_commits"] == 1 and c["shas"] == ["dddddddd"]


def _sources():
    for path in sorted(PACKAGE.rglob("*.py")):
        yield path, ast.parse(path.read_bytes().decode("utf-8"), filename=str(path))


def _sites(match) -> set[tuple[str, str]]:
    """The file and the innermost function of each node that matches."""
    found = set()
    for path, tree in _sources():
        rel = path.relative_to(ROOT).as_posix()
        spans = sorted(((n.lineno, n.end_lineno or n.lineno, n.name) for n in ast.walk(tree)
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))),
                       key=lambda s: s[1] - s[0])
        for node in ast.walk(tree):
            if match(node):
                name = next((s[2] for s in spans if s[0] <= node.lineno <= s[1]), "<module>")
                found.add((rel, name))
    return found


def _code_key(node) -> bool:
    if isinstance(node, ast.JoinedStr) and node.values:
        head = node.values[0]
        return isinstance(head, ast.Constant) and head.value == "code:"
    return isinstance(node, ast.Constant) and node.value == "code:"


def test_one_reader_of_the_code_stamp():
    """Only `code_stamp` builds the `code:<message>` key. A second reader of
    the stamp must call `code_stamp`, and this test goes red when it does not."""
    assert _sites(_code_key) == {("rota/roles/api.py", "code_stamp")}


def _commit_pattern(node) -> bool:
    return (isinstance(node, ast.Constant) and isinstance(node.value, str)
            and '"committed"' in node.value and '"head_commit"' in node.value)


def test_one_reader_of_the_landed_commit():
    """One pattern reads a landed commit's head, and only `landed_heads`
    reads the pattern."""
    assert _sites(_commit_pattern) == {("rota/tools/nightcount.py", "<module>")}
    users = _sites(lambda n: isinstance(n, ast.Name) and n.id == "COMMIT_HEAD")
    assert users == {("rota/tools/nightcount.py", "<module>"),
                     ("rota/tools/nightcount.py", "landed_heads")}
