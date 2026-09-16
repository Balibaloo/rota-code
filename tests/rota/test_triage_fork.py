"""
The mandatory fork: a judgment that cannot be skipped.

The principal's question set the experiment: "are we sure we framed the
escalation correctly to the roles?" We were not. The three-way routing had
been in the Tester's brief the whole time, as prose under a production
headline -- and headline-following is exactly what both models do, measured
across all three routing reds. So the judgment becomes an act: every
criterion gets a `tests.triage` verdict before it gets anything else, and an
encode is only legal for a criterion claimed `encodable`. Both doors are
completions.

The verdict collapsed to two-way 2026-09-01, on the fork's own measurement:
can/cannot arrives at 14B, the word/sentence/fact taxonomy is beyond every
local tier tested -- and the taxonomy only ever picked a desk, which the
`unresolved` ladder and `criterion_repair` pick mechanically. `cannot` goes
to the nearest desk and climbs; the three named kinds survive as sharper
claims for a model that genuinely holds the distinction.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.sandbox import ArgumentError, build


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, "
                 "approval_ver, version) VALUES ('i1','x','in_scope',"
                 "'approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('t1','i1','y')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('c1','t1','register(u) stores the email lowercased')")
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES "
                 "('b1','i1','running')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b1','t1')")
    conn.commit()
    return conn


def _tester(db):
    return build("tester", db, batch_id="b1", mode="tests_missing")


def test_an_encode_with_no_branch_claim_is_refused(db):
    """The gate arms with the mode, not with usage: the very first encode of
    a session that never triaged anything is the case that matters most."""
    sb = _tester(db)
    with pytest.raises(ValueError, match="triage verdict"):
        sb.call("tests.encode", id="ts1", criterion_id="c1", path="t.py",
                body="assert True")


def test_a_claimed_criterion_encodes(db):
    sb = _tester(db)
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    out = sb.call("tests.encode", id="ts1", criterion_id="c1",
                  path="test_register.py",
                  body="def test_lowercase():\n"
                       "    from app import register, lookup\n"
                       "    register('u1','A@B.co')\n"
                       "    assert lookup('u1').email == 'a@b.co'")
    assert out["id"] == "ts1"


def test_each_cannot_verdict_names_its_owner(db):
    sb = _tester(db)
    owners = {
        "ambiguous_word": "terminologist",
        "no_machine_check": "vision_keeper",
        "outside_fact": "researcher",
    }
    for verdict, owner in owners.items():
        out = sb.call("tests.triage", criterion_id="c1", verdict=verdict)
        assert owner in out["next"], (verdict, out)


def test_a_routing_verdict_does_not_license_an_encode(db):
    """Claiming 'no_machine_check' and then encoding anyway is the exact
    both-doors-in-one-turn disease, refused."""
    sb = _tester(db)
    sb.call("tests.triage", criterion_id="c1", verdict="no_machine_check")
    with pytest.raises(ValueError, match="triage verdict"):
        sb.call("tests.encode", id="ts1", criterion_id="c1", path="t.py",
                body="assert True")


def test_the_verdict_vocabulary_is_closed(db):
    sb = _tester(db)
    with pytest.raises(ArgumentError, match="not one of"):
        sb.call("tests.triage", criterion_id="c1", verdict="maybe")


def test_a_bare_cannot_is_a_complete_verdict_at_the_nearest_desk(db):
    """The collapse: no diagnosis owed. The next-step names the Terminologist
    and says the climb is mechanical, and the criterion is exactly as
    encode-blocked as under any sharp verdict."""
    sb = _tester(db)
    out = sb.call("tests.triage", criterion_id="c1", verdict="cannot")
    assert "terminologist" in out["next"], out
    assert "climbs" in out["next"], "the promise is the point: no diagnosis owed"
    with pytest.raises(ValueError, match="triage verdict"):
        sb.call("tests.encode", id="ts1", criterion_id="c1", path="t.py",
                body="def test_x():\n    assert True")


def test_a_criterion_already_questioned_is_not_asked_again(db):
    """`tests_missing` fires per batch while any criterion lacks a test, so a
    routed criterion meets the mode again on the next wake. The triage's
    next-step deflects, and the send guard makes the deflection unskippable
    -- one open question per criterion, in both statuses the ladder owns."""
    for status in ("open", "unresolved"):
        db.execute("DELETE FROM messages")
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                   "verb, body_refs, seq, status) VALUES ('m1','th1','tester',"
                   "'terminologist','question','[\"c1\"]',1,?)", (status,))
        db.commit()
        sb = _tester(db)
        out = sb.call("tests.triage", criterion_id="c1", verdict="cannot")
        assert "already asked" in out["next"], (status, out)
        with pytest.raises(ValueError, match="already has your open question"):
            sb.call("msg.question_terminologist", refs=["c1"],
                    question="what does easy mean")


def test_an_answered_question_frees_the_criterion(db):
    """The guard reads the thread's state, not its history: an answered
    question is a finished conversation, and a new one is legal."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
               "verb, body_refs, seq, status) VALUES ('m1','th1','tester',"
               "'terminologist','question','[\"c1\"]',1,'answered')")
    db.commit()
    sb = _tester(db)
    out = sb.call("tests.triage", criterion_id="c1", verdict="cannot")
    assert "already asked" not in out["next"], out
    sb.call("msg.question_terminologist", refs=["c1"],
            question="the answer did not cover the export format")


def test_modes_without_the_fork_are_untouched(db):
    """The gate exists only where the mode offers the claim: the Tester's
    answer/repair flow re-encodes against new words without a triage door,
    and arming the gate there would refuse a flow that has no key."""
    from rota.roles import prompts

    sb = build("tester", db, batch_id="b1", mode="answer",
               allow=prompts.mode_tools("tester", "answer"))
    assert not hasattr(sb.ctx, "triaged"), \
        "no triage in the mode, no gate on the encode"

def test_cannot_climbs_once_the_terminologist_has_answered_twice(db):
    """
    Night 63 (2026-09-14): the Tester triaged `cannot`, was told to ask the
    Terminologist, was refused a third question because two were answered,
    triaged `cannot` again, three sessions. The rung is a fact of the message
    log, so the hint climbs with it.
    """
    import json
    refs = json.dumps(["c1"])
    for n in (1, 2):
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                   "body_refs, status, round_no, seq) VALUES (?, 'th1', 'tester', "
                   "'terminologist', 'question', ?, 'answered', 0, ?)",
                   (f"q{n}", refs, 2 * n - 1))
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                   "body_refs, status, round_no, seq, cause_id) VALUES (?, 'th1', "
                   "'terminologist', 'tester', 'answer', ?, 'answered', 0, ?, ?)",
                   (f"a{n}", refs, 2 * n, f"q{n}"))
    db.commit()
    out = _tester(db).call("tests.triage", criterion_id="c1", verdict="cannot")
    assert "vision_keeper" in out["next"] and "terminologist has answered 2" in out["next"]


def test_a_check_by_raise_is_a_check(db):
    """A try/except that re-raises as AssertionError, ended on `assert True`,
    checks something; the constant-assertion wall must not take it."""
    sb = _tester(db)
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    body = """from app import register

def test_register_accepts_lowercase():
    try:
        register('U@X')
    except TypeError as e:
        raise AssertionError(str(e)) from e
    assert True
"""
    try:
        sb.call("tests.encode", id="ts_raise", criterion_id="c1", path="tests/test_r.py", body=body)
    except ValueError as exc:
        assert "on a constant" not in str(exc), exc

def test_an_answer_to_a_challenge_quotes_the_criterion_or_is_the_fix(db):
    """
    Night 80 (2026-09-15): the Tester's answer to the Developer's challenge said
    the developer is right and kept the test; the Developer bent the code to it.
    An answer that keeps the test carries the criterion's words; a concession is
    tests.encode (Roman)."""
    from rota.roles import prompts
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES ('ts1','b1','c1','tests/test_r.py','def test_x(): assert 1')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, body_refs, status, round_no, seq) "
               "VALUES ('m1','th1','developer','tester','challenge','[\"c1\", \"ts1\"]','open',0,1)")
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="normal",
               allow=prompts.mode_tools("tester", "challenge"))
    sb.ctx.trigger = "m1"
    with pytest.raises(ValueError, match="carries the criterion's words"):
        sb.call("msg.answer_developer", refs=["c1", "ts1"], round_no=0,
                quotes="the developer is right, the test asserts more than the criterion asks")
    out = sb.call("msg.answer_developer", refs=["c1", "ts1"], round_no=0,
                  quotes="the assertion comes from: stores the email lowercased")
    assert out["to"] == "developer"
