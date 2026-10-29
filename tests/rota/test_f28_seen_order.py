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
from rota.core.predicates import Wake as PWake
from rota.core.runner import resolve_inbound
from rota.core.sandbox import build
from rota.core.scheduler import Wake
from rota.roles import principal, prompts
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


def _liaison(conn, reply):
    sb = build("liaison", conn, mode="landing",
               allow=prompts.mode_tools("liaison", "landing"),
               wake=PWake("liaison", "message", message_id=reply))
    sb.ctx.trigger = reply
    return sb


def test_the_landing_wake_names_the_line_whose_row_is_gone(tmp_path):
    """The row of his line 1 left the tables. The landing block names the
    line, so the Liaison rules the other lines (the F26 review, finding 1)."""
    conn, reply = _night(tmp_path)
    wake = Wake(role="liaison", kind="message", message_id=reply, detail="converse")
    landing = resolve_inbound(conn, wake)["landing"]
    assert set(landing["gone_lines"]) == {"1"}
    assert "l_bg2" in landing["gone_lines"]["1"]


def test_a_line_whose_row_is_gone_takes_no_ruling(tmp_path):
    """The every-line check skips a line whose row no table holds. The old
    door refused every ruling, and only an ask to him landed."""
    conn, reply = _night(tmp_path)
    out = _liaison(conn, reply).call(
        "rulings.rule", rulings={"2": "contest", "3": "approve"}, words=M106)
    assert out["per_item"] == {"l_echo": "contest", "l_bg3": "approve"}


def test_his_verdict_on_a_gone_row_stays_in_per_item_with_a_fault(tmp_path):
    """A ruling on the gone line keeps his verdict in `per_item`. The row
    has no `ruled_refs` row, so a fault names the gap (no work stays
    invisible)."""
    conn, reply = _night(tmp_path)
    sb = _liaison(conn, reply)
    out = sb.call("rulings.rule", words=M106,
                  rulings={"1": "contest", "2": "contest", "3": "approve"})
    assert out["per_item"] == {"l_bg2": "contest", "l_echo": "contest",
                               "l_bg3": "approve"}
    staged = {t: [w for k, _, w in sb.ctx.writes if k == t]
              for t in ("ruled_refs", "faults")}
    assert {r["ref"] for r in staged["ruled_refs"]} == {"l_echo", "l_bg3"}
    assert [f["text"] for f in staged["faults"]] == [
        principal.unheld_text(out["id"], "l_bg2")]


def test_rulings_line_reads_the_row_he_saw(tmp_path):
    """The record and today's render disagree on line 1. The old rule read
    the render and gave l_echo (the F26 review, finding 3)."""
    conn, reply = _night(tmp_path)
    assert _liaison(conn, reply).call("rulings.line", line="1")["ref"] == "l_bg2"


def test_land_reads_the_order_he_saw_when_the_ask_carries_none(tmp_path):
    """`land` with no order on the ask reads the record. The record is the
    render reversed, so his line 1 is b2. The old rule sent b1 (the F26
    review, finding 3)."""
    conn = init_db(tmp_path / "rota.db")
    for i in ("i1", "i2"):
        conn.execute("INSERT INTO items (id, text, kind, approval) "
                     "VALUES (?, 'x', 'in_scope', 'approved')", (i,))
    for b, i, sha in (("b1", "i1", "abc1234"), ("b2", "i2", "abc5678")):
        conn.execute("INSERT INTO batches (id, item_id, status, head_commit) "
                     "VALUES (?, ?, 'running', ?)", (b, i, sha))
    _msg(conn, "m1", None, "liaison", "principal", "present", ["b1", "b2"], 1)
    conn.commit()
    (ask,) = principal.pending_asks(conn)
    render = principal.render_page(conn, "present", ask.refs, ask_id="m1")[1]
    assert render == ["b1", "b2"]
    seen = list(reversed(render))
    _msg(conn, "m2", "m1", "principal", "liaison", "converse", [], 2, "words")
    conn.execute("INSERT INTO config (key, value) VALUES ('order:m2', ?)",
                 (json.dumps(seen),))
    conn.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, "
                 "status) VALUES ('r1', 'm1', 'm2', '{}', '', 'open')")
    conn.commit()
    bare = principal.Ask(message_id="m1", verb="present", refs=list(ask.refs),
                         order=[])
    sent = principal.land(conn, bare, principal.Answer(
        verb="verdict", text="Line 1 is wrong, the files are not right",
        per_item={"b1": "contest", "b2": "contest"}), ruling_id="r1")
    row = conn.execute("SELECT verb, body_refs FROM messages WHERE id = ?",
                       (sent,)).fetchone()
    assert (row["verb"], json.loads(row["body_refs"])) == ("verdict", ["b2"])


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


# These tests pin the doors of the word form of a page call. Pass R2
# retires the doors and these pins (frame 345, the R1 brief, step 5).
import pytest  # noqa: E402

pytestmark = pytest.mark.usefixtures("old_page_form")
