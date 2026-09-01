"""
The mandatory fork: a judgment that cannot be skipped.

The principal's question set the experiment: "are we sure we framed the
escalation correctly to the roles?" We were not. The three-way routing had
been in the Tester's brief the whole time, as prose under a production
headline -- and headline-following is exactly what both models do, measured
across all three routing reds. So the judgment becomes an act: every
criterion gets a `tests.triage` verdict before it gets anything else, an
encode is only legal for a criterion claimed `encodable`, and each of the
three "cannot" verdicts names the owner the criterion goes to. Both doors
are completions.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.sandbox import ArgumentError, build


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, provenance, approval, "
                 "approval_ver, version) VALUES ('i1','x','in_scope',"
                 "'decided','approved',1,1)")
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
    with pytest.raises(ValueError, match="branch claim"):
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
    with pytest.raises(ValueError, match="branch claim"):
        sb.call("tests.encode", id="ts1", criterion_id="c1", path="t.py",
                body="assert True")


def test_the_verdict_vocabulary_is_closed(db):
    sb = _tester(db)
    with pytest.raises(ArgumentError, match="not one of"):
        sb.call("tests.triage", criterion_id="c1", verdict="maybe")


def test_modes_without_the_fork_are_untouched(db):
    """The gate exists only where the mode offers the claim: the Tester's
    answer/repair flow re-encodes against new words without a triage door,
    and arming the gate there would refuse a flow that has no key."""
    from rota.roles import prompts

    sb = build("tester", db, batch_id="b1", mode="answer",
               allow=prompts.mode_tools("tester", "answer"))
    assert not hasattr(sb.ctx, "triaged"), \
        "no triage in the mode, no gate on the encode"
