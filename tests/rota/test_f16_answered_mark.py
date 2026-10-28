"""
Fact F16: a reply that landed nothing is not answered.

Night 170's W17 counted 21 sessions with no landed write and no message.
None of them woke on a question or an ask. s202 woke on an escalation,
which the parent already left unresolved (F16 review 1, finding 2). The
reach of the fact is the barren wake on an owed verb, as the 43 question
wakes of nights 143 to 165 that read answered (finding 3).

The rule goes by the kind of the trigger. A trigger whose verb is in
`db.OWED_A_REPLY`, as a `question` or an `ask`, is answered only by a reply
or a receipt. A session that landed nothing gives neither. A trigger that
asks for nothing, as an `answer`, a `deliver` or a `relay`, is answered by
its wake, as before. His request keeps frame 320's retry.

The mark has one writer, `db.mark_answered`. The last test pins it.
"""
from __future__ import annotations

import ast
import pathlib
import re

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
    assert "sent nothing" in row["unresolved_note"]


def test_fault_rows_alone_do_not_answer_a_fresh_request(db):
    """Frame 320's shape: his request, and a Liaison wake whose every call
    was refused. Only fault rows remain, and they land nothing.

    Night 170's W17 woke on no question and no ask (F16 review 1, finding
    2). Its night count is frame 320's, and F16 keeps frame 320's path.
    """
    result = _barren(
        "s145", "liaison", "m_p2", writes=[_fault("s145", "liaison")],
        refusals=[("msg.clarify_principal",
                   "quotes= is not a span of the live text", "ValueError")])
    session_commit(db, result)
    row = _status(db, "m_p2")
    assert row["status"] == "open"
    assert "not a span of the live text" in row["unresolved_note"]
    from rota.core.db import landed
    assert not landed(result)
    # The fault row itself still lands as the record of the refusal.
    assert db.execute("SELECT 1 FROM faults WHERE id = 'f_s145'").fetchone()


def test_a_reply_answers_a_question(db):
    """A session that replies answers its trigger, as before."""
    from rota.core.db import OutboundMessage

    session_commit(db, _barren(
        "s205", "terminologist", "m90",
        writes=[_fault("s205", "terminologist")],
        messages=[OutboundMessage(id="m94", to_role="developer",
                                  verb="answer", body_refs=["c_1"],
                                  cause_id="m90")]))
    assert _status(db, "m90")["status"] == "answered"


def test_a_row_that_cites_nothing_does_not_answer_a_question(db):
    """A question owes a reply or a receipt, as a challenge does (frame 174).

    A glossary row on another term is neither, so the question climbs.
    """
    session_commit(db, _barren(
        "s207", "terminologist", "m90",
        writes=[Write("glossary_terms", "g_1", {"term": "shorten",
                                                "sense_short": "cut the path"})]))
    row = _status(db, "m90")
    assert row["status"] == "unresolved"
    assert "no row that cites this message" in row["unresolved_note"]


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


def _seed(db, rows, status="open"):
    seq = db.execute("SELECT MAX(seq) FROM messages").fetchone()[0]
    for k, (mid, frm, to, verb, cause, refs) in enumerate(rows, start=1):
        db.execute(
            "INSERT INTO messages (id, cause_id, thread_id, from_role, "
            "to_role, verb, body_refs, seq, status, attempts) VALUES "
            "(?, ?, 't_r', ?, ?, ?, ?, ?, ?, 1)",
            (mid, cause, frm, to, verb, refs, seq + k,
             status if mid == rows[-1][0] else "answered"))
    db.commit()


def test_tipsal_s75_the_handback_reopen_owes_no_reply(db):
    """tipsAL's s75 woke on m37, a reopen caused by the elect m36.

    The reopen hands the batch back, and the Developer builds and sends
    nothing. Its receipt was `batches b1`, a row that cites nothing of m37.
    Before the exemption, m37 went unresolved, the ladder woke the Liaison,
    and the merge held on "waiting on liaison" (F16 review 1, finding 1).
    """
    from rota.core import lifecycle

    _seed(db, [("m35", "vision_keeper", "developer", "reopen", None, '["i_1"]'),
               ("m36", "developer", "vision_keeper", "elect", "m35", '["i_1"]'),
               ("m37", "vision_keeper", "developer", "reopen", "m36",
                '["i_1", "b1"]')])
    session_commit(db, _barren(
        "s75", "developer", "m37",
        writes=[Write("glossary_terms", "g_1", {"term": "shorten",
                                                "sense_short": "cut the path"})]))
    assert _status(db, "m37")["status"] == "answered"
    assert lifecycle.waiting_on_a_seat(db, "b1") is None


def test_the_revocation_reopen_still_owes_an_elect(db):
    """A reopen with no elect for a cause asks the Developer to elect."""
    _seed(db, [("m35", "vision_keeper", "developer", "reopen", None, '["i_1"]')])
    session_commit(db, _barren("s74", "developer", "m35"))
    assert _status(db, "m35")["status"] == "unresolved"


@pytest.mark.parametrize("frm,to,verb", [
    ("liaison", "architect", "ask"),
    ("architect", "vision_keeper", "propose"),
    ("vision_keeper", "liaison", "submit"),
    ("vision_keeper", "developer", "reopen"),
    ("developer", "vision_keeper", "elect"),
])
def test_an_open_owed_message_about_the_batch_holds_its_merge(db, frm, to, verb):
    """Every verb of `OWED_A_REPLY` holds the merge of the batch it names
    (F16 review 1, finding 4). The addressee owes the reply."""
    from rota.core import lifecycle

    _seed(db, [("m50", frm, to, verb, None, '["b1"]')])
    assert lifecycle.waiting_on_a_seat(db, "b1") == f"waiting on {to}: m50"


def test_the_developer_waits_on_its_own_open_elect(db):
    """An open elect filters the Developer's ticks until the reopen comes."""
    from rota.core import scheduler

    _seed(db, [("m51", "developer", "vision_keeper", "elect", None, '["b1"]')])
    assert "m51" in scheduler.waiting_on(db, "developer")
    assert "m51" not in scheduler.waiting_on(db, "vision_keeper")


def _site(parents: dict, node: ast.AST, rel: str) -> str:
    """The file and the innermost function of a node."""
    while node in parents:
        node = parents[node]
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return f"{rel}:{node.name}"
    return f"{rel}:<module>"


def _parents(tree: ast.AST) -> dict:
    return {c: p for p in ast.walk(tree) for c in ast.iter_child_nodes(p)}


_LITERAL_MARK = re.compile(r"\bset\b[^;]*\bstatus\s*=\s*'answered'", re.I)
_BOUND_MARK = re.compile(r"\bupdate\s+messages\s+set\b[^;]*\bstatus\s*=\s*\?", re.I)


def _answered_writes(tree: ast.AST, rel: str = "") -> list[str]:
    """The sites whose strings set the answered mark.

    A site sets the literal status in any spacing, or binds the status as a
    parameter and passes the word 'answered' in the same call (F16 review 1,
    finding 5).
    """
    parents = _parents(tree)
    found = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and _LITERAL_MARK.search(node.value)):
            found.append(_site(parents, node, rel))
        elif isinstance(node, ast.Call):
            words = [c.value for c in ast.walk(node)
                     if isinstance(c, ast.Constant) and isinstance(c.value, str)]
            if "answered" in words and any(_BOUND_MARK.search(w) for w in words):
                found.append(_site(parents, node, rel))
    return found


def test_the_writer_pin_sees_every_form():
    """The four forms of the review's probe 4."""
    for src in [
            "def f(c): c.execute(\"UPDATE messages SET status = 'answered' WHERE id = ?\")",
            "def f(c): c.execute(\"UPDATE messages SET status='answered' WHERE id = ?\")",
            "def f(c): c.execute('UPDATE messages SET status = ? WHERE id = ?', ('answered', 1))",
            "conn.execute(\"UPDATE messages SET status = 'answered'\")"]:
        assert _answered_writes(ast.parse(src)), src


def test_the_mark_has_one_writer():
    """Only `db.mark_answered` writes the mark outside the test kit.

    A second writer decides by its own rule whether a message is answered.
    That is the gap of fact F16. Add a site here only with its landed fact.
    """
    writers = set()
    for path in ROOT.rglob("*.py"):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(("testkit/", "tools/")):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        writers |= set(_answered_writes(tree, rel))
    assert writers == {"core/db.py:mark_answered"}, writers


# A Developer disputes a test with a challenge or an escalation. The answer
# cause line, the thread on tests, the decision reader and the same-refs door
# name that pair. The pair is a different fact from the verbs that owe a
# reply, so the pin allows it at these four sites only (review 1, finding 5).
_DISPUTE = {"challenge", "escalate"}
_DISPUTE_SITES = {"core/runner.py:_answer_cause_line",
                  "core/runner.py:_thread_on_tests",
                  "core/sandbox.py:architect_decision_on",
                  "core/sandbox.py:stage"}


def _owed_lists(tree: ast.AST, rel: str = "") -> list[str]:
    """The sites that name two owed verbs or more as a list.

    A list is a literal, a SQL `IN` list, a SQL `OR` chain of `verb =`, or
    a Python `or` chain of `==` tests.
    """
    from rota.core.db import OWED_A_REPLY
    from rota.design import graph as graph_mod

    owed = set(OWED_A_REPLY)
    verbs = {e.v for e in graph_mod.load().of_type("messages")}
    parents = _parents(tree)
    found = []

    def check(node, words: set[str]) -> None:
        # A list with a word that is no message verb, as the register's
        # entry names, is a list of something else.
        if not (words <= verbs and len(words & owed) >= 2):
            return
        site = _site(parents, node, rel)
        if words & owed == _DISPUTE and site in _DISPUTE_SITES:
            return
        found.append(site)

    sql_list = re.compile(r"IN\s*\(([^)]*)\)", re.IGNORECASE)
    sql_eq = re.compile(r"\bverb\s*=\s*'(\w+)'", re.IGNORECASE)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            check(node, {e.value for e in node.elts
                         if isinstance(e, ast.Constant) and isinstance(e.value, str)})
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            for m in sql_list.finditer(node.value):
                check(node, set(re.findall(r"'(\w+)'", m.group(1))))
            eqs = set(sql_eq.findall(node.value))
            if " or " in node.value.lower():
                check(node, eqs)
        elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
            check(node, {c.comparators[0].value for c in node.values
                         if isinstance(c, ast.Compare)
                         and isinstance(c.ops[0], ast.Eq)
                         and isinstance(c.comparators[0], ast.Constant)
                         and isinstance(c.comparators[0].value, str)})
    return found


def test_the_list_pin_sees_every_form():
    """The forms of the review's probe 3 that name two owed verbs."""
    for src in ["X = ('question', 'ask')",
                "q = \"SELECT 1 FROM messages WHERE verb IN ('reopen', 'elect')\"",
                "X = frozenset({'submit', 'propose'})",
                "q = \"WHERE verb = 'question' OR verb = 'ask'\"",
                "ok = verb in ('question', 'ask')",
                "ok = verb == 'question' or verb == 'ask'",
                "WAIT = ('challenge', 'escalate')",
                "def waiting_on(): return ('challenge', 'escalate')"]:
        assert _owed_lists(ast.parse(src), "core/x.py"), src


def test_the_owed_verbs_have_one_list():
    """Only `db.OWED_A_REPLY` names the verbs that owe a reply.

    Pass 1c of F16 found three lists of this fact, and they disagreed:
    `OWED_A_REPLY`, `lifecycle.OWED_VERBS` and `api.ASKING_VERBS`. The
    Developer's wait in `scheduler.waiting_on` and a SQL string in
    `session_commit` named the verbs inline too. A second list goes red here.
    """
    found = set()
    for path in ROOT.rglob("*.py"):
        rel = path.relative_to(ROOT).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        found |= set(_owed_lists(tree, rel))
    assert found == {"core/db.py:<module>"}, found


