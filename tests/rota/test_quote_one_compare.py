"""F18: one reader compares a quote with the live text it must match.

`sandbox._quote_reads` is the reader. The rule is "a contiguous span of
the disputed row, verbatim" (ruled: Roman, 2026-08-26). Before F18 the red
line door compared the quote with the failing line by its own compare, and
`_quoted_body_gone` compared the prior's line with the live body by a bare
substring test (plans/rootfix-audit-2026-10-27-a.md, F18).
"""
from __future__ import annotations

import ast
from pathlib import Path

from rota.core import sandbox
from rota.core.db import init_db

ROOT = Path(__file__).resolve().parents[2] / "rota"
OLD = "    assert result.output == 'hello world from the test'"
NEW = '    assert result.output == "hello world from the test"'


def _prior(tmp_path, shown=None, quote=None, live=None):
    shown = shown if shown is not None else "def test_x():\n" + OLD + "\n"
    quote = quote if quote is not None else OLD.strip()
    live = live if live is not None else "def test_x():\n" + NEW + "\n"
    conn = init_db(tmp_path / "rota.db")
    # The door reads these rows alone, so the rows they point at stay out.
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("INSERT INTO sessions (id, role, seq) VALUES ('s1','developer',1)")
    conn.execute("INSERT INTO sessions (id, role, seq, trigger_msg) VALUES "
                 "('s2','tester',2,'m1')")
    conn.execute("INSERT INTO turns (session_id, seq, system, user, completion) "
                 "VALUES ('s1',1,'',?, '')", (shown,))
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "seq, body_text) VALUES ('m1','m1','developer','tester',"
                 "'challenge',1,?)", (quote,))
    conn.execute("INSERT INTO tests (id, batch_id, path, body) VALUES "
                 "('t1','b1','tests/test_x.py',?)", (live,))
    conn.execute("INSERT INTO receipts (session_id, table_name, row_id, "
                 "new_version) VALUES ('s2','tests','t1',2)")
    conn.commit()
    return conn


def test_a_body_that_still_reads_the_quote_keeps_the_prior(tmp_path):
    """The one reader reads `'` and `"` as one mark (night 126's s172). So
    the live body holds the prior's line, and the prior keeps counting."""
    assert sandbox._quoted_body_gone(_prior(tmp_path), "m1", ["t1"]) is False


HEAD = ("def test_confirm_returns_default_when_eof():\n"
        "    import io\n"
        "    from unittest.mock import patch\n"
        "    # Simulate EOF by replacing stdin with an empty stream\n"
        "    with patch(\"sys.stdin\", io.StringIO(\"\")):\n")


def test_a_comment_inside_a_quote_cuts_one_line_and_not_the_rest(tmp_path):
    """Night 161 m100's shape: the quote is a whole test with a comment in
    it, and the Tester rewrote the code after the comment. The comment
    cut works per line, so the quote's last line is read, and no live body
    holds it (review of F18 pass 1, finding 1)."""
    shown = HEAD + "        assert confirm(\"go\", default=True) is True\n"
    live = HEAD + "        assert confirm(\"go\", default_on_eof=True) is True\n"
    conn = _prior(tmp_path, shown=shown, quote=shown.strip(), live=live)
    assert sandbox._quoted_body_gone(conn, "m1", ["t1"]) is True


def _calls(fn: ast.AST) -> set[str]:
    return {n.func.id for n in ast.walk(fn)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def test_the_quote_compares_go_through_the_one_reader():
    """`_span_of` and `_quote_pairs` are the reader's own parts. No door
    calls them, and each named door calls `_quote_reads`."""
    tree = ast.parse((ROOT / "core" / "sandbox.py").read_text(encoding="utf-8"))
    fns = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    own = {"_span_of", "_quote_pairs"}
    found = sorted(f"{name} calls {c}" for name, fn in fns.items()
                   if name != "_quote_reads" for c in _calls(fn) & own)
    assert found == []
    for door in ("_red_line_refusal", "_quoted_body_gone"):
        assert "_quote_reads" in _calls(fns[door]), door
