"""Fact F28: the row order of a page as he saw it.

`principal.seen_order` is the one reader of the order he saw at a reply. The
record of `principal.land` comes first, and today's render is the fallback
(rule C76, the audit of 2026-10-27-b, F28).
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

from rota.core.db import init_db
from rota.core.runner import resolve_inbound
from rota.core.scheduler import Wake
from rota.roles import principal
from tests.rota.test_frame272_recent_chat_pages import M106, _msg, _notes

ROOT = Path(__file__).resolve().parents[2]
OLD = ["l_bg2", "l_echo", "l_bg3"]


def _night(tmp_path):
    """Page m105 and his reply through `land`. The row of his line 1 leaves
    the page after the reply, as on night 159 (frame 272)."""
    conn = init_db(tmp_path / "rota.db")
    _notes(conn, *OLD)
    _msg(conn, "m105", None, "liaison", "principal", "present", OLD, 1)
    conn.commit()
    (ask,) = principal.pending_asks(conn)
    reply = principal.land(conn, ask, principal.Answer(verb="reply", text=M106))
    conn.execute("DELETE FROM ledger WHERE id = 'l_bg2'")
    conn.commit()
    return conn, reply


def test_the_landing_wake_numbers_the_rows_he_saw(tmp_path):
    """The Liaison's landing lines name the row he saw on each line. The old
    rule numbered today's render, which lost line 1."""
    conn, reply = _night(tmp_path)
    assert principal.render_page(conn, "present", OLD, ask_id="m105")[1][0] != "l_bg2"
    wake = Wake(role="liaison", kind="message", message_id=reply, detail="converse")
    lines = resolve_inbound(conn, wake)["landing"]["lines"]
    assert lines["1"] == "l_bg2"


def test_the_record_comes_first_and_the_render_is_the_fallback(tmp_path):
    conn, reply = _night(tmp_path)
    row = conn.execute("SELECT * FROM messages WHERE id = 'm105'").fetchone()
    assert principal.seen_order(conn, reply, principal.page_ask(row)) == OLD
    render = principal.render_page(conn, "present", OLD, ask_id="m105")[1]
    assert principal.seen_order(conn, "m_none", principal.page_ask(row)) == render
    assert principal.seen_order(conn, "m_none", None) == []


def _calls(path: Path):
    tree = ast.parse(path.read_bytes().decode("utf-8"))
    spans = sorted(((n.lineno, n.end_lineno or n.lineno, n.name) for n in ast.walk(tree)
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))),
                   key=lambda s: s[1] - s[0])
    for node in ast.walk(tree):
        yield node, next((s[2] for s in spans if s[0] <= node.lineno <= s[1]), "<module>") \
            if hasattr(node, "lineno") else "<module>"


def _name(call: ast.Call) -> str:
    f = call.func
    return f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""


def test_one_reader_of_the_order_he_saw():
    """Only `seen_order` reads the `order:<reply>` record, and `land` alone
    writes it. In the role and core code, a render serves the page text,
    never the order: `render_page(...)[1]` and a tuple unpack of it are a
    second reader."""
    record, rendered = set(), set()
    for path in sorted((ROOT / "rota").rglob("*.py")):
        rel = path.relative_to(ROOT).as_posix()
        parents = {}
        nodes = list(_calls(path))
        for node, owner in nodes:
            for child in ast.iter_child_nodes(node):
                parents[id(child)] = node
            if isinstance(node, ast.JoinedStr) and node.values and isinstance(
                    node.values[0], ast.Constant) and node.values[0].value == "order:":
                record.add((rel, owner))
            if isinstance(node, ast.Call) and _name(node) == "door_rows" and any(
                    isinstance(a, ast.Constant) and a.value == "order" for a in node.args):
                record.add((rel, owner))
        for node, owner in nodes:
            if isinstance(node, ast.Call) and _name(node) == "render_page":
                up = parents.get(id(node))
                takes_text = (isinstance(up, ast.Subscript)
                              and isinstance(up.slice, ast.Constant) and up.slice.value == 0)
                if not takes_text and owner not in (
                        "pending_asks", "render_ask", "_shift_waits", "seen_order"):
                    rendered.add((rel, owner))
    assert record == {("rota/roles/principal.py", "seen_order"),
                      ("rota/roles/principal.py", "land")}
    assert rendered == set()
