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


def test_the_code_step_stays_with_no_architect_decision(db, monkeypatch):
    _night153(db, author="developer")
    ctx = _ctx(db)
    monkeypatch.setattr(sandbox, "_escalation_admitted", lambda c, r: False)
    said = sandbox._escalation_or_step(ctx, [CRIT, TEST], "fact.",
                                       sandbox._code_step(ctx))
    assert said == "fact. " + sandbox.CODE_STEP
