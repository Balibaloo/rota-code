"""Wall W7 of night 172: one reader of his words of a message.

On night 172 five pages read back `Your answer "", as the team read it` on
his clarify answers, and he contested each line. A clarify answer lands on
the verdict path of `land`, which writes no `body_text`. His words are in
`entries` as `e_<message>`. Nine readers read `body_text` alone
(`plans/f1-f15-f21-night172-read.md`, sections 1, 2, 4 and 6, P7).
"""
from __future__ import annotations

import ast
import json
import re
import shutil
import sqlite3
from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.roles.principal import (READ_BACK_WORDS, Answer, Ask, land,
                                  reading_line, said)

_WORDS = ("Yes, use the AppData Roaming folder under the home folder when "
          "the roaming flag is on, and the AppData Local folder otherwise.")
_REGISTER = Path("D:/repos/rota/.rota/clickI_night172.db")
_PKG = Path(__file__).resolve().parents[2] / "rota"


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    for i in ("i1", "i2"):
        conn.execute("INSERT INTO items (id, text, kind) VALUES (?, 'a', "
                     "'in_scope')", (i,))
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "body_refs, body_text, seq, status) VALUES ('m30', 'th', "
                 "'liaison', 'principal', 'clarify', ?, 'Which folder?', 1, "
                 "'open')", (json.dumps(["i1", "i2"]),))
    return conn


def _clarify_answer(db) -> str:
    """His answer to the clarify m30, landed by `land`, with the reading's
    approve rows that the Liaison's ruling writes, as r_m31_2 of night 172."""
    mid = land(db, Ask("m30", "clarify", ["i1", "i2"]),
               Answer(verb="converse", text=_WORDS))
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, status) "
               "VALUES (?, 'm30', ?, 'landed')", (f"r_{mid}_2", mid))
    for ref in ("i1", "i2"):
        db.execute("INSERT INTO ruled_refs (id, ruling_id, ref, verdict, "
                   "words_from, source) VALUES (?, ?, ?, 'approve', ?, "
                   "'reading')", (f"rr_{ref}", f"r_{mid}_2", ref, mid))
    return mid


def test_the_read_back_line_quotes_his_clarify_answer(db):
    mid = _clarify_answer(db)
    # The shape of night 172: the verdict path keeps no body.
    assert db.execute("SELECT body_text FROM messages WHERE id = ?",
                      (mid,)).fetchone()["body_text"] is None
    quote = " ".join(_WORDS.split()[:READ_BACK_WORDS]) + " ..."
    assert reading_line(db, f"reading:{mid}") == (
        f'Your answer "{quote}", as the team read it: 2 lines approved. '
        "Say ok, or say what we misread.")


@pytest.mark.skipif(not _REGISTER.exists(), reason="night 172's register")
def test_night_172s_m33_line_10_quotes_m31(tmp_path):
    # The read opens a copy, because an open in place writes the night's -shm.
    copy = tmp_path / "night172.db"
    shutil.copyfile(_REGISTER, copy)
    conn = sqlite3.connect(copy)
    conn.row_factory = sqlite3.Row
    assert reading_line(conn, "reading:m31") == (
        'Your answer "Yes, use the AppData Roaming folder under the ...", as '
        "the team read it: 6 lines approved. Say ok, or say what we misread.")


def test_that_is_fine_is_an_approval():
    """Pass 1c: "That is fine." approves, by the agreement reader."""
    from rota.roles.api import _AGREES

    assert _AGREES.match("That is fine.")
    assert not _AGREES.match("what time is the meeting")


def test_said_falls_back_to_the_body_of_a_message_with_no_entry(db):
    assert said(db, "m30") == "Which folder?"
    assert said(db, "m99") == ""
    assert said(db, None) == ""


def test_his_earlier_clarify_answer_reaches_the_earlier_reading(db):
    """Site 7: the earlier answers to a page filtered `body_text IS NOT
    NULL`, so a clarify answer on the verdict path was skipped."""
    from rota.roles.api import _earlier_answers

    mid = _clarify_answer(db)
    assert _earlier_answers(db, "m30", "m_later") == [(_WORDS, mid)]


# Each of these reads the body of a seat's message, not his words.
_SEAT_BODIES = {
    ("rota/core/sandbox.py", "_quoted_body_gone"): "the Tester's quoted body",
    ("rota/roles/principal.py", "seen_order"): "the Liaison's page text",
}


def _functions():
    for path in sorted(_PKG.rglob("*.py")):
        rel = path.relative_to(_PKG.parent).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                yield rel, node


def _own(fn):
    """The nodes of `fn` that no nested function holds."""
    stack = list(ast.iter_child_nodes(fn))
    while stack:
        node = stack.pop()
        yield node
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            stack.extend(ast.iter_child_nodes(node))


# A select that leads with `body_text`, as `_words_from` held before W7.
_LEADS = re.compile(r"SELECT body_text\b[\w, ]* FROM messages\b")
# A select of `body_text` that keeps his messages by `from_role`.
_HIS = re.compile(r"SELECT [\w, .]*\bbody_text\b[\w, .]*? FROM messages\b.*"
                  r"from_role = 'principal'")
# `earlier_exchange` selects the body for the Liaison's questions. His turns
# there read through `said`, and the subquery names `from_role`.
_LIAISON_BODIES = {("rota/core/runner.py", "resolve_inbound"):
                   "the Liaison's questions of a clarify thread"}


def _sql_readers(pattern):
    readers = set()
    for rel, fn in _functions():
        for node in _own(fn):
            if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                    and pattern.search(" ".join(node.value.split()))):
                readers.add((rel, fn.name))
    return readers


def test_only_said_reads_the_body_of_his_message():
    readers = _sql_readers(_LEADS)
    allowed = {("rota/roles/principal.py", "said"), *_SEAT_BODIES}
    assert readers - allowed == set()
    assert ("rota/roles/principal.py", "said") in readers


def test_no_reader_selects_the_body_of_his_messages():
    assert _sql_readers(_HIS) - set(_LIAISON_BODIES) == set()


def test_the_pins_catch_the_shapes_of_words_from_before_w7():
    assert _LEADS.search("SELECT body_text, thread_id FROM messages WHERE id = ?")
    assert _HIS.search("SELECT id, body_text FROM messages WHERE thread_id = ? "
                       "AND from_role = 'principal' AND id != ?")


# P7 pass 1d: a clause starts after a lead word, so a seat's quote of his
# clause without "please" matches (night 171's m70, "Drop line 2").
@pytest.mark.parametrize("his, span", [
    ("Please drop line 2.", "Drop line 2"),
    ("Also drop line 2.", "drop line 2"),
    ("Then drop line 2.", "drop line 2"),
    ("Now drop line 2.", "drop line 2"),
    ("And drop line 2.", "drop line 2"),
    ("So drop line 2.", "drop line 2"),
    ("Simply drop line 2.", "drop line 2"),
    ("So please drop line 2.", "drop line 2"),
], ids=["please", "also", "then", "now", "and", "so", "adverb-ly", "chain"])
def test_a_clause_starts_after_a_lead_word(his, span):
    from rota.roles.api import _holds_clauses

    assert _holds_clauses(his, span)


def test_a_lead_word_inside_a_clause_cuts_nothing():
    from rota.roles.api import _holds_clauses

    assert not _holds_clauses("Keep it as it is now please.", "please")
    assert not _holds_clauses("Line 4 is wrong too.", "wrong too")


_M80 = ("Line 1 describes Click as a whole and not my change, so replace it "
        "with this: add one example to the docstring of the function that "
        "formats a file name, showing that the path a/b/c.txt shows as c.txt "
        "when shorten is set to True. Only the docstring changes, and the "
        "code stays as it is.")


def test_night_171s_m80_contest_rests_on_the_calls_words():
    """P7 pass 1d: s193 contested line 1 with the span after "replace it
    with this:". The span names no line, and his reply names line 1."""
    from rota.roles.api import _unbacked_approve

    span = _M80.split(": ", 1)[1].split(". ")[0]
    shape = {"r1": {"verdict": "contest", "act": "rewrite", "words": span}}
    page = "1. Click is a package for command line interfaces."
    assert _unbacked_approve(None, _M80, {"r1": "contest"}, {"r1": "1"},
                             shape, ["r1"], page) is None
    assert _unbacked_approve(None, "", {"r1": "contest"}, {"r1": "1"},
                             shape, ["r1"], page) == (
        "His words neither fault nor name line 1, so line 1 takes no "
        f"contest: the words start {span!r}.")


def test_a_hedging_adverb_starts_no_clause():
    """Review p7 p2, finding p2-3: the seat cannot drop his hedge."""
    from rota.roles.api import _holds_clauses

    for hedge in ("Hardly", "Barely", "Scarcely", "Rarely", "Seldom", "Only"):
        assert not _holds_clauses(f"{hedge} any of line 3 is right.",
                                  "any of line 3 is right")
