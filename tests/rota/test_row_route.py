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
               "('d1','architect','tst1 does not encode c1','[\"tst1\"]')")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="answer",
               allow=prompts.mode_tools("developer", "answer"))
    assert sandbox_mod._challenge_cap_refusal(sb.ctx, [], ["c1", "tst1"])
    assert sandbox_mod._challenge_cap_refusal(
        sb.ctx, [], ["c1", "tst1", "d1"]) is None


def _capped(db):
    """Three landed challenges on c1, and an older decision that cites no
    test of them, as a decision id reaches the Developer by `rulings_line`."""
    _rows(db)
    for n in range(3):
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                   "verb, body_refs, seq, status) VALUES (?, 'tc', 'developer', "
                   "'tester', 'challenge', ?, ?, 'answered')",
                   (f"mc{n}", json.dumps(["c1", "tst1"]), 10 + n))
    db.execute("INSERT INTO decisions (id, author, text, refs) VALUES "
               "('d_old','vision_keeper','an older ruling','[\"c9\"]')")
    db.commit()


def test_an_unrelated_decision_does_not_pass_the_cap(db):
    """The review of 8d090e2e, finding 7: the exemption holds for the
    decision the challenge carries, not for any decision id."""
    _capped(db)
    sb = build("developer", db, batch_id="b1", mode="answer",
               allow=prompts.mode_tools("developer", "answer"))
    assert sandbox_mod._challenge_cap_refusal(sb.ctx, [], ["c1", "tst1", "d_old"])


def test_a_decision_the_trigger_answer_carries_passes_the_cap(db):
    """The decision is a ref of the answer that woke the session."""
    _capped(db)
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
               "to_role, verb, body_refs, seq, status) VALUES ('m156','m155',"
               "'th','architect','developer','answer','[\"c1\", \"d_old\"]',20,"
               "'open')")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="answer",
               allow=prompts.mode_tools("developer", "answer"))
    sb.ctx.trigger = "m156"
    assert sandbox_mod._challenge_cap_refusal(
        sb.ctx, [], ["c1", "tst1", "d_old"]) is None


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


# The review of 8d090e2e, findings 3, 9 and 5 (2026-10-11).

def test_an_amend_then_an_answer_on_the_escalations_rows_is_offered_the_row(db):
    """Finding 3, probe `p5.py` line 1: the escalate brief says "model.amend,
    and say so with msg.answer_developer". The answer carried the
    escalation's refs, and the refusal named decisions.author. It now names
    the row the session wrote, and the doors admit the offered answer."""
    from rota.core.sandbox import dry_run

    _rows(db)
    sb = _architect(db)
    sb.ctx.writes.append(("constraints", "k_new", {"text": "t2"}))
    with pytest.raises(ValueError) as exc:
        sb.call("msg.answer_developer", refs=["c1", "tst1"])
    assert str(exc.value) == (
        "refs=['c1', 'tst1'] add no row to the refs of m155, so the Developer "
        "gets back the rows it sent. This session wrote k_new. Send "
        "msg.answer_developer(refs=['k_new']).")
    offers = [o for o in sb.ctx.offers if o.op == "msg.answer_developer"]
    assert [o.args for o in offers] == [{"refs": ["k_new"]}]
    assert dry_run(sb, offers[0].op, offers[0].args).admitted


def test_an_answer_with_words_is_not_called_wordless(db):
    """Finding 9: m64 and m137 carried text. The refusal says "no words" only
    when the answer's text is empty."""
    from rota.roles import api

    sb = _answered(db)
    db.execute("UPDATE messages SET body_text = 'the test calls the command' "
               "WHERE id = 'm156'")
    db.commit()
    with pytest.raises(api.EndRefusal) as exc:
        sb.call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)
    said = str(exc.value)
    assert said.startswith(
        "no ref of this answer is a decision row. If you still read the test "
        "as wrong, say so in one sentence and end. End the session with no "
        "call."), said
    assert "no words" not in said


def test_a_criterion_as_a_finding_on_an_escalated_test_routes_to_a_decision(db):
    """Finding 5: failing Architect runs 1 and 5 met this refusal in the turn
    before a wrong challenge to the Vision Keeper. The escalation holds a
    test and no finding, so the refusal names decisions.author."""
    _rows(db)
    sb = _architect(db)
    with pytest.raises(ValueError) as exc:
        sb.call("findings.find", id="f1", batch_id="b1", constraint_id="c1",
                status="violated", grain="tests/test_v.py")
    assert str(exc.value) == (
        "'c1' is a row of criteria, not a constraint. A finding names a "
        "constraint from model.consult. The escalation m155 is about the test "
        "tst1 and carries no finding. If tst1 does not encode its criterion, "
        "write a decision with decisions.author, refs=['tst1'], that names the "
        "line of tst1 that does not encode it. Then send msg.answer_developer "
        "with the decision's id in refs.")
    assert [o.op for o in sb.ctx.offers] == ["decisions.author"]


# The review of pass 2c, finding 3 (2026-10-11), probe `r5.py` shape one.

def test_an_amend_with_a_binding_is_offered_the_constraint_alone(db):
    """Finding 3: `model.amend` stages a `constraint_bindings` row whose id
    names no row a ref can cite. The offer keeps the constraint only."""
    from rota.core.sandbox import dry_run

    _rows(db)
    sb = _architect(db)
    sb.ctx.writes.extend([
        ("constraints", "k_new", {"headline": "h", "text": "t",
                                  "is_global": 0}),
        ("constraint_bindings", "k_new:src/x.py",
         {"constraint_id": "k_new", "grain": "src/x.py",
          "grain_kind": "path"}),
        ("refs", "rf1", {"src_table": "constraints", "src_id": "k_new"})])
    with pytest.raises(ValueError):
        sb.call("msg.answer_developer", refs=["c1", "tst1"])
    offers = [o for o in sb.ctx.offers if o.op == "msg.answer_developer"]
    assert [o.args for o in offers] == [{"refs": ["k_new"]}]
    assert dry_run(sb, offers[0].op, offers[0].args).admitted
