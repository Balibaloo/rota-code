"""
Four guards from one re-record (2026-09-01), each attributed from a transcript.

The register's reds after the triage collapse split cleanly into "the role
found the right act and misaddressed it": a Critic quoting the vacuous test
at the Developer, an Architect reporting the constraint instead of the batch,
a Vision Keeper minuting its own edit under a prefixed id the previous guard
coached it into, a Critic judging what it had just put in dispute, and a
Tester woken about a term with no criterion in view at all. Each is refused
or supplied where the state already says what is right.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.core.predicates import Wake


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, provenance, approval, "
                 "approval_ver, version) VALUES ('i1','closing keeps invoices',"
                 "'in_scope','decided','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','i1','close an account')")
    conn.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
                 "VALUES ('g1','account','the billing entity','decided')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text, term_refs) VALUES "
                 "('c1','tk1','closing an account leaves its invoices in place',"
                 "'[\"g1\"]')")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) VALUES "
                 "('b1','i1','running','abc123')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b1','tk1')")
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                 "VALUES ('tst1','b1','c1','test_close.py',"
                 "\"assert close_account('a1') is not None\")")
    conn.commit()
    return conn


def test_a_quoted_test_is_the_testers_dispute(db):
    sb = build("critic", db, batch_id="b1", mode="review")
    with pytest.raises(ValueError, match=r"challenge_tester\(refs=\['c1', 'tst1'\]"):
        sb.call("msg.challenge_developer", refs=["c1", "tst1"],
                quotes=["closing an account leaves its invoices in place",
                        "assert close_account('a1') is not None"])
    # The same evidence on the right channel goes through.
    sb.call("msg.challenge_tester", refs=["c1", "tst1"],
            quotes=["closing an account leaves its invoices in place",
                    "assert close_account('a1') is not None"])


def test_a_challenge_is_the_sessions_verdict_until_it_lands(db):
    sb = build("critic", db, batch_id="b1", mode="review")
    sb.call("msg.challenge_tester", refs=["c1", "tst1"],
            quotes=["closing an account leaves its invoices in place",
                    "assert close_account('a1') is not None"])
    with pytest.raises(ValueError, match="already challenged the tester"):
        sb.call("verdicts.emit", batch_id="b1", result="fail",
                failed_criterion="c1")


def test_a_report_from_a_batch_wake_names_the_batch(db):
    wake = Wake("architect", "tick:exhausted", refs=("b1",))
    sb = build("architect", db, batch_id="b1", mode="exhausted", wake=wake)
    db.execute("INSERT INTO constraints (id, headline, text, provenance) VALUES "
               "('cn1','exports never buffer','memory stays flat','decided')")
    db.commit()
    with pytest.raises(ValueError, match="add 'b1' to refs"):
        sb.call("msg.report_liaison", refs=["cn1"])
    sb.call("msg.report_liaison", refs=["cn1", "b1"])


def test_a_prefixed_item_id_is_still_a_minute(db):
    from rota.roles import prompts
    sb = build("vision_keeper", db, mode="message",
               allow=prompts.mode_tools("vision_keeper", "message"))
    sb.call("problem.assert", id="i1", text="users can close their account",
            kind="in_scope")
    with pytest.raises(ValueError, match="row you wrote this session"):
        sb.call("decisions.author", id="i1", text="the principal rejected it")
    with pytest.raises(ValueError, match="minuting your own edit"):
        sb.call("decisions.author", id="c_i1", text="the principal rejected it")


def test_a_tester_woken_about_a_term_sees_the_criteria_that_use_it(db):
    db.execute("UPDATE batches SET status = 'pending'")
    db.commit()
    wake = Wake("tester", "message", refs=("g1",))
    sb = build("tester", db, mode="answer", wake=wake)
    rows = sb.call("criteria.load")
    assert [r["id"] for r in rows] == ["c1"], rows
