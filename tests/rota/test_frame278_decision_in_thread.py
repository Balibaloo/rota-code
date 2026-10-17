"""
Frame 278, pass 1: the thread view shows the Architect's decision, and the
same-refs step offers the challenge that carries it.

The rows are copied from `.rota/clickI_night153.db`, read-only on 2026-10-17,
at s283's `tick:tests_failing` wake, and rebuilt inline. The Architect s277
wrote `dec_1_tst_ver_opt_show_py` and answered m143 with m144, which held the
decision ref and no words. s283 read m143 as "answered with no words", and its
challenge without the decision id met the step toward the code.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from rota.core import runner, sandbox
from rota.core.db import init_db

TEST = "tst_ver_opt_show_py"
CRIT = "ver_opt_show_py"
DEC = "dec_1_tst_ver_opt_show_py"
DEC_TEXT = ("The test tst_ver_opt_show_py does not encode its criterion "
            "ver_opt_show_py.")


def _night153(db, author="architect", dec_refs=f'["{TEST}"]'):
    """s283's thread: m143 to the Architect, m144 back with the decision."""
    db.execute("PRAGMA foreign_keys = OFF")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES (?, 'bg_3', ?, 'tests/test_version_option.py', 'x')",
               (TEST, CRIT))
    db.execute("INSERT INTO decisions (id, author, text, refs) VALUES (?, ?, ?, ?)",
               (DEC, author, DEC_TEXT, dec_refs))
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m143', 'bg_3', 'developer', "
               "'architect', 'escalate', ?, 143, 'answered')",
               (f'["{CRIT}", "{TEST}"]',))
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
               "to_role, verb, body_refs, seq, status) VALUES ('m144', 'm143', "
               "'bg_3', 'architect', 'developer', 'answer', ?, 144, 'answered')",
               (f'["{CRIT}", "{TEST}", "{DEC}"]',))
    db.commit()


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _ctx(db):
    return SimpleNamespace(conn=db, role="developer", offers=[], trigger=None,
                           working_set=None, outbound=[])


def test_thread_shows_the_decision_in_place_of_no_words(db):
    _night153(db)
    sb = SimpleNamespace(ctx=_ctx(db))
    thread = runner._thread_on_tests(sb, [{"id": TEST}])
    assert [t["id"] for t in thread] == ["m143"]
    # Before frame 278 the answer was the string "answered with no words".
    assert thread[0]["answer"] == {"id": DEC, "author": "architect",
                                   "text": DEC_TEXT, "table": "decisions"}


def test_an_echoed_reason_row_of_the_asker_keeps_no_words(db):
    # Night 153: m143's refs held no reason row, but the Developer's other
    # escalations did, and an answer echoes the asker's refs.
    _night153(db)
    db.execute("UPDATE messages SET body_refs = ? WHERE id IN ('m143', 'm144')",
               (f'["{CRIT}", "{TEST}", "{DEC}"]',))
    db.commit()
    thread = runner._thread_on_tests(SimpleNamespace(ctx=_ctx(db)), [{"id": TEST}])
    assert thread[0]["answer"] == "answered with no words"


def test_the_decision_is_found_on_the_table_the_author_and_the_test(db):
    _night153(db)
    assert sandbox.architect_decision_on(db, "developer", [TEST]) == (DEC, TEST, CRIT)


@pytest.mark.parametrize("author, refs", [("developer", f'["{TEST}"]'),
                                          ("architect", '["other_test"]')])
def test_no_architect_decision_on_the_test_finds_none(db, author, refs):
    _night153(db, author=author, dec_refs=refs)
    assert sandbox.architect_decision_on(db, "developer", [TEST]) is None


def test_the_code_step_becomes_the_challenge_with_the_decision(db, monkeypatch):
    _night153(db)
    ctx = _ctx(db)
    monkeypatch.setattr(sandbox, "_escalation_admitted", lambda c, r: False)
    said = sandbox._escalation_or_step(ctx, [CRIT, TEST], "fact.",
                                       sandbox._code_step(ctx))
    # Before frame 278 the step was "Make one real change to the code the
    # test calls."
    assert sandbox.CODE_STEP not in said
    assert f"Send msg.challenge_tester(refs={[CRIT, TEST, DEC]!r}" in said


def _answered_decision_challenge(db):
    """Review 1 of frame 278, finding 1: the Developer sent the decision
    challenge (m150), and the Tester answered it (m151)."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m150', 'bg_3', 'developer', "
               "'tester', 'challenge', ?, 150, 'answered')",
               (f'["{CRIT}", "{TEST}", "{DEC}"]',))
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
               "to_role, verb, body_refs, body_text, seq, status) VALUES "
               "('m151', 'm150', 'bg_3', 'tester', 'developer', 'answer', ?, "
               "'The test holds.', 151, 'answered')",
               (f'["{CRIT}", "{TEST}"]',))
    db.commit()


def test_an_answered_decision_challenge_gets_no_offer_of_itself(db, monkeypatch):
    _night153(db)
    _answered_decision_challenge(db)
    ctx = _ctx(db)
    monkeypatch.setattr(sandbox, "_escalation_admitted", lambda c, r: False)
    said = sandbox._escalation_or_step(ctx, [CRIT, TEST, DEC], "fact.",
                                       sandbox._code_step(ctx))
    assert said == "fact. " + sandbox.CODE_STEP


def test_after_these_offers_the_decision_challenge(db):
    _night153(db)
    said = runner._after_these(SimpleNamespace(ctx=_ctx(db)), [{"id": TEST}])
    assert f"Send msg.challenge_tester(refs={[CRIT, TEST, DEC]!r}" in said
    assert "Make one real change" not in said


def test_after_these_keeps_the_code_step_once_the_tester_answered(db):
    _night153(db)
    _answered_decision_challenge(db)
    said = runner._after_these(SimpleNamespace(ctx=_ctx(db)), [{"id": TEST}])
    assert said == ("A listed message that is answered or closed is refused if "
                    "sent again on these refs. Make one real change to the "
                    "code the test calls, or end the session with no call.")


def test_a_row_of_another_author_is_not_the_answer(db):
    # Review 1, finding 3: the answer adds a Developer row from another
    # message, and the view showed it as the Architect's answer.
    _night153(db)
    db.execute("INSERT INTO decisions (id, author, text, refs) VALUES "
               "('d_dev', 'developer', 'a reason', '[]')")
    db.execute("UPDATE messages SET body_refs = ? WHERE id = 'm144'",
               (f'["{CRIT}", "{TEST}", "d_dev"]',))
    db.commit()
    thread = runner._thread_on_tests(SimpleNamespace(ctx=_ctx(db)), [{"id": TEST}])
    assert thread[0]["answer"] == "answered with no words"


@pytest.mark.parametrize("refs, op", [([TEST], "msg.challenge_tester"),
                                      ([CRIT, TEST], "msg.escalate_architect")])
def test_a_challenge_on_the_test_alone_gets_the_decision_first(db, monkeypatch,
                                                               refs, op):
    # Review 1, finding 2: after m143 on [crit, test], a challenge on [test]
    # met a second escalation offer.
    _night153(db)
    ctx = _ctx(db)
    monkeypatch.setattr(sandbox, "_escalation_admitted", lambda c, r: True)
    said = sandbox._escalation_or_step(ctx, refs, "fact.", sandbox._code_step(ctx))
    assert op in said


def test_the_code_step_stays_with_no_architect_decision(db, monkeypatch):
    _night153(db, author="developer")
    ctx = _ctx(db)
    monkeypatch.setattr(sandbox, "_escalation_admitted", lambda c, r: False)
    said = sandbox._escalation_or_step(ctx, [CRIT, TEST], "fact.",
                                       sandbox._code_step(ctx))
    assert said == "fact. " + sandbox.CODE_STEP
