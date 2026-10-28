"""F24: one reader says what this session sent to a role.

`sandbox._sent_this_session` is the reader. The triage verdict's row is the
op's row and not the model's send (frame 81), so the reader leaves it out.
Before F24 the Critic's verdict door and the Developer's write door each
filtered `ctx.outbound` by their own rule, and the verdict door kept the
triage row (plans/rootfix-audit-2026-10-27-b.md, F24).
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from rota.core import sandbox
from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import api

ROOT = Path(__file__).resolve().parents[2] / "rota"

#: The functions that may filter `outbound` by recipient and verb.
#: `stage_park_relay` edits the staged relay rows. It asks no question
#: about what the session sent.
ALLOWED = {("core/sandbox.py", "_sent_this_session"),
           ("core/sandbox.py", "stage_park_relay")}


def _triage(to_role: str, verb: str, refs=("c1",)) -> dict:
    return {"id": "m9", "to_role": to_role, "verb": verb,
            "body_refs": list(refs), "route": "triage"}


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1','closing keeps invoices','in_scope',"
                 "'approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','i1','close an account')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('c1','tk1','closing an account leaves its invoices in place')")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) VALUES "
                 "('b1','i1','running','abc123')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b1','tk1')")
    conn.commit()
    return conn


def test_a_triage_challenge_is_no_verdict_of_the_critic(db):
    sb = build("critic", db, batch_id="b1", mode="review")
    sb.ctx.outbound.append(_triage("tester", "challenge"))
    try:
        sb.call("verdicts.emit", batch_id="b1", result="fail",
                failed_criterion="c1")
    except Exception as exc:  # another door may speak, this one must not
        assert "already challenged the tester" not in str(exc)


def test_a_triage_answer_carries_no_criterion():
    ctx = api.Ctx.__new__(api.Ctx)
    ctx.outbound = [_triage("tester", "answer")]
    assert "carries this criterion" not in api._closed_answer_note(ctx, "c1")


def test_the_reader_returns_the_sent_rows_oldest_first():
    ctx = api.Ctx.__new__(api.Ctx)
    first = {"id": "m1", "to_role": "tester", "verb": "challenge"}
    last = {"id": "m2", "to_role": "tester", "verb": "challenge"}
    ctx.outbound = [first, _triage("tester", "challenge"), last]
    assert sandbox._sent_this_session(ctx, "tester", "challenge") == [first, last]


def _names(node) -> set[str]:
    return {n.value for n in ast.walk(node)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)}


def _reads_outbound(node) -> bool:
    return any((isinstance(n, ast.Attribute) and n.attr == "outbound")
               or (isinstance(n, ast.Constant) and n.value == "outbound")
               for n in ast.walk(node))


def test_one_function_filters_the_sent_rows_by_recipient_and_verb():
    found = []
    for path in sorted(ROOT.rglob("*.py")):
        rel = path.relative_to(ROOT).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if (rel, fn.name) in ALLOWED:
                continue
            for comp in ast.walk(fn):
                if not isinstance(comp, (ast.ListComp, ast.SetComp,
                                         ast.GeneratorExp, ast.DictComp)):
                    continue
                gens = comp.generators
                if not any(_reads_outbound(g.iter) for g in gens):
                    continue
                conds = [c for g in gens for c in g.ifs]
                if any({"to_role", "verb"} <= _names(c) for c in conds):
                    found.append(f"{rel}:{comp.lineno} {fn.name}")
    assert sorted(set(found)) == []
