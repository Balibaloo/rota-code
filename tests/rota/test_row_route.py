"""
Frame 115's row route, design 200 change 4 (rota workflow).

Law 2 keeps words off the Architect's answer to the Developer. On nights 138
and 139, 10 of 10 such answers carried refs alone. The route stays inside law
2: the Architect writes a decision row, the answer refs it, the Developer's
wake shows the row's text, and a challenge that carries the row reaches the
Tester past the cap (ruled: Roman, 2026-10-11 06:30). No model runs here.
"""
from __future__ import annotations

import json

import pytest

from rota.core import sandbox as sandbox_mod
from rota.core.db import init_db
from rota.core.predicates import Wake
from rota.core.sandbox import build
from rota.roles import prompts


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _rows(db):
    db.execute("INSERT INTO items (id, text, kind, approval) "
               "VALUES ('i1','x','in_scope','approved')")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','x')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c1','tk1',"
               "'When `version_option` is invoked with `show_python=True`, the "
               "output appends the Python version')")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','running')")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst1','b1','c1','tests/test_v.py','def test_v(): pass')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m155','th','developer',"
               "'architect','escalate','[\"c1\", \"tst1\"]',1,'open')")
    db.commit()


def _architect(db):
    sb = build("architect", db, mode="escalate",
               allow=prompts.mode_tools("architect", "escalate"),
               wake=Wake("architect", "message", message_id="m155"))
    sb.ctx.trigger = "m155"
    return sb


ROWLESS = ("refs=['c1', 'tst1'] add no row to the refs of m155, so the "
           "Developer gets back the rows it sent. Write what you found with "
           "decisions.author, then send msg.answer_developer with the "
           "decision's id in refs.")


def test_an_answer_that_hands_back_the_escalations_rows_is_refused(db):
    """Night 139's m156 answered m155 with m155's own refs and no words."""
    _rows(db)
    sb = _architect(db)
    with pytest.raises(ValueError) as exc:
        sb.call("msg.answer_developer", refs=["c1", "tst1"])
    assert str(exc.value) == ROWLESS
    assert not sb.ctx.outbound


def test_an_answer_with_a_decision_row_lands(db):
    _rows(db)
    sb = _architect(db)
    sb.call("decisions.author", id="d_tst1_line",
            text="c1 holds. tst1 calls the decorated plain function, so no "
                 "command runs the option.", refs=["c1", "tst1"])
    sb.call("msg.answer_developer", refs=["c1", "tst1", "d_tst1_line"])
    assert [m["body_refs"] for m in sb.ctx.outbound] == \
        [["c1", "tst1", "d_tst1_line"]]


def test_an_answer_on_a_row_this_session_amended_lands(db):
    """The amend branch of `escalate.md` answers on the row it amended, which
    can be a row of the escalation."""
    _rows(db)
    db.execute("INSERT INTO constraints (id, headline, text, is_global) "
               "VALUES ('k1','h','t',1)")
    db.execute("UPDATE messages SET body_refs = '[\"c1\", \"k1\"]' WHERE id = 'm155'")
    db.commit()
    sb = _architect(db)
    sb.ctx.writes.append(("constraints", "k1", {"text": "t2"}))
    sb.call("msg.answer_developer", refs=["k1"])
    assert len(sb.ctx.outbound) == 1


def test_the_developers_wake_shows_a_decision_rows_text(db):
    from rota.core.runner import _resolve_refs

    db.execute("INSERT INTO decisions (id, author, text, refs) VALUES "
               "('d1','architect','tst1 line 9 calls a plain function','[]')")
    db.commit()
    shown = _resolve_refs(db, ["d1"], role="developer", detail="answer")
    assert shown["d1"] == {"id": "d1", "author": "architect",
                           "text": "tst1 line 9 calls a plain function",
                           "table": "decisions"}
    assert _resolve_refs(db, ["d1"]) == {}, "a page keeps its text"


def test_the_answer_mode_holds_the_challenge(db):
    assert "msg.challenge_tester" in prompts.mode_tools("developer", "answer")


def test_a_challenge_that_carries_a_decision_row_passes_the_cap(db):
    """Three landed challenges on c1 stop a fourth. The fourth that carries
    the Architect's decision row is the row's route to the Tester."""
    _rows(db)
    for n in range(3):
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                   "verb, body_refs, seq, status) VALUES (?, 'tc', 'developer', "
                   "'tester', 'challenge', ?, ?, 'answered')",
                   (f"mc{n}", json.dumps(["c1", "tst1"]), 10 + n))
    db.execute("INSERT INTO decisions (id, author, text, refs) VALUES "
               "('d1','architect','tst1 does not encode c1','[]')")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="answer",
               allow=prompts.mode_tools("developer", "answer"))
    assert sandbox_mod._challenge_cap_refusal(sb.ctx, [], ["c1", "tst1"])
    assert sandbox_mod._challenge_cap_refusal(
        sb.ctx, [], ["c1", "tst1", "d1"]) is None


# Design 200 pass 2b: the interviews of the two cases at 0 of 5,
# `plans/frame200-interviews.md`.

def _answered(db):
    _rows(db)
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
               "to_role, verb, body_refs, seq, status) VALUES ('m156','m155',"
               "'th','architect','developer','answer','[\"c1\", \"tst1\"]',2,"
               "'open')")
    db.commit()
    sb = build("developer", db, batch_id="b1",
               allow=prompts.mode_tools("developer", "answer"),
               wake=Wake("developer", "message", message_id="m156",
                         detail="answer"))
    sb.ctx.trigger = "m156"
    return sb


QUOTES = ["When `version_option` is invoked with `show_python=True`",
          "def test_v(): pass"]


def test_an_answer_wakes_challenge_with_no_decision_row_is_refused(db):
    """The s282 case's seat sent the challenge on refs that showed
    `table: criteria` and `table: tests`, and no decision row."""
    from rota.roles import api

    sb = _answered(db)
    with pytest.raises(api.EndRefusal) as exc:
        sb.call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)
    said = str(exc.value)
    assert said.startswith(
        "no ref of this answer is a decision row. The answer carries the rows "
        "you sent back and no words. If you still read the test as wrong, say "
        "so in one sentence and end. End the session with no call."), said
    assert not sb.ctx.outbound


def test_an_answer_wakes_challenge_with_a_decision_row_passes_the_door(db):
    sb = _answered(db)
    db.execute("INSERT INTO decisions (id, author, text, refs) VALUES "
               "('d1','architect','tst1 calls a plain function','[]')")
    db.commit()
    assert sandbox_mod._answer_mode_challenge_refusal(
        sb.ctx, ["c1", "tst1", "d1"]) is None
    assert sandbox_mod._answer_mode_challenge_refusal(sb.ctx, ["c1", "tst1"])


def test_the_wake_of_an_answer_names_what_it_answers(db):
    from rota.core.runner import _answer_cause_line

    _answered(db)
    wake = Wake("developer", "message", message_id="m156", detail="answer")
    assert _answer_cause_line(db, wake) == \
        "This answers your escalation m155 about c1, tst1"
    other = Wake("tester", "message", message_id="m156", detail="answer")
    assert _answer_cause_line(db, other) == "", "only the asker's own message"


def test_a_criterion_in_resolves_ledger_is_refused_with_the_fact(db):
    """An Architect run sent `resolves_ledger=["c_459e6e"]`, a criterion."""
    _rows(db)
    sb = _architect(db)
    with pytest.raises(ValueError) as exc:
        sb.call("decisions.author", id="d_x", text="tst1 misses c1",
                refs=["c1", "tst1"], resolves_ledger=["c1"])
    assert str(exc.value) == (
        "c1 is a criterion, and resolves_ledger takes the id of a ledger row. "
        "Send decisions.author again without resolves_ledger.")
