"""
Fact F16: a reply that landed nothing is not answered.

Night 170's W17 counted 21 sessions with no landed write and no message.
s202, Architect, met three refusals and wrote only fault rows. The old rule
in `session_commit` marked each trigger answered, because a fault row read
as a write and a barren session on an open trigger read as an answer.

The rule goes by the kind of the trigger. A trigger that asks for a reply,
a `question` or an `ask` (`api.ASKING_VERBS`), is answered only by a landed
row or a message. A trigger that asks for nothing, as an `answer`, a
`deliver` or a `relay`, is answered by its wake, as before. His request
keeps frame 320's retry.

The mark has one writer, `db.mark_answered`. The last test pins it.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

from rota.core.db import SessionResult, Write, init_db, session_commit

ROOT = pathlib.Path(__file__).resolve().parents[2] / "rota"

# (id, from, to, verb, cause)
_ROWS = [
    ("m82", "architect", "developer", "answer", None),
    ("m90", "developer", "terminologist", "question", None),
    ("m91", "liaison", "architect", "ask", None),
    ("m92", "liaison", "vision_keeper", "deliver", None),
    ("m93", "liaison", "terminologist", "relay", None),
    ("m_p2", "principal", "liaison", "converse", None),
]


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    for seq, (mid, frm, to, verb, cause) in enumerate(_ROWS, start=80):
        conn.execute(
            "INSERT INTO messages (id, cause_id, thread_id, from_role, "
            "to_role, verb, body_refs, seq, status, attempts) VALUES "
            "(?, ?, ?, ?, ?, ?, '[\"c_1\"]', ?, 'open', 1)",
            (mid, cause, f"t_{mid}", frm, to, verb, seq))
    conn.commit()
    return conn


def _status(db, mid):
    return db.execute("SELECT status, unresolved_note FROM messages "
                      "WHERE id = ?", (mid,)).fetchone()


def _fault(sid, role="architect"):
    return Write("faults", f"f_{sid}", {
        "session_id": sid, "call": "msg.answer_developer",
        "text": "quotes= is not a span of the live text", "kind": "fault",
        "author": role, "seq": 1, "status": "open"})


def _barren(sid, role, trigger, **kw):
    return SessionResult(session_id=sid, role=role, trigger_msg=trigger,
                         wake_kind="message", wake_detail="", **kw)


def test_a_question_with_no_call_stays_unresolved(db):
    """A question owes a reply. A wake with no call did not give one."""
    session_commit(db, _barren("s204", "terminologist", "m90"))
    row = _status(db, "m90")
    assert row["status"] == "unresolved"
    assert "landed no row" in row["unresolved_note"]


def test_fault_rows_alone_do_not_answer_an_ask(db):
    """s202's shape: every call was refused, and only fault rows remain."""
    result = _barren(
        "s202", "architect", "m91", writes=[_fault("s202")],
        refusals=[("msg.answer_liaison",
                   "quotes= is not a span of the live text", "ValueError")])
    session_commit(db, result)
    row = _status(db, "m91")
    assert row["status"] == "unresolved"
    assert "not a span of the live text" in row["unresolved_note"]
    from rota.core.db import landed
    assert not landed(result)
    # The fault row itself still lands as the record of the refusal.
    assert db.execute("SELECT 1 FROM faults WHERE id = 'f_s202'").fetchone()


def test_a_landed_row_answers_a_question(db):
    """A session that lands a row answers its trigger, as before."""
    session_commit(db, _barren(
        "s205", "terminologist", "m90",
        writes=[_fault("s205", "terminologist"),
                Write("glossary_terms", "g_1", {"term": "shorten",
                                                "sense_short": "cut the path"})]))
    assert _status(db, "m90")["status"] == "answered"


@pytest.mark.parametrize("mid,role", [("m82", "developer"),
                                      ("m92", "vision_keeper"),
                                      ("m93", "terminologist")])
def test_a_trigger_that_asks_nothing_is_answered_by_its_wake(db, mid, role):
    """An answer, a deliver and a relay owe no reply. The wake answers them."""
    session_commit(db, _barren("s206", role, mid, writes=[_fault("s206", role)]))
    assert _status(db, mid)["status"] == "answered"


def test_a_fresh_request_that_lands_nothing_is_not_answered(db):
    """Frame 320's case: his request, and a Liaison wake that lands nothing.

    The request stays open for frame 320's retry, with the reason as its
    note. The F16 rule does not mark it answered.
    """
    session_commit(db, _barren("s145", "liaison", "m_p2"))
    row = _status(db, "m_p2")
    assert row["status"] == "open"
    assert row["unresolved_note"]


def _answered_writes(tree: ast.AST) -> list[str]:
    """The functions whose string constants set the answered mark."""
    found = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for node in ast.walk(fn):
            if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                    and "set status = 'answered'" in node.value.lower()):
                found.append(fn.name)
    return found


def test_the_mark_has_one_writer():
    """Only `db.mark_answered` writes the mark outside the test kit.

    A second writer decides by its own rule whether a message is answered.
    That is the gap of fact F16. Add a site here only with its landed fact.
    """
    writers = {}
    for path in ROOT.rglob("*.py"):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(("testkit/", "tools/")):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for name in _answered_writes(tree):
            writers.setdefault(f"{rel}:{name}", 0)
            writers[f"{rel}:{name}"] += 1
    assert set(writers) == {"core/db.py:mark_answered"}, writers
