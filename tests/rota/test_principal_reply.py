"""
The page and the input are one contract.

Measured as the principal (2026-09-04): the page had stopped showing ids, the
parser still demanded them, and the page promised "say what's wrong in your
own words" while no input could carry words with a verdict. The only reply
that worked was "lgtm". `render_page` numbers the rulable rows and returns
their order; `parse_reply` reads a reply against that order. Both seats use
them.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.roles.principal import Ask, parse_reply, pending_asks


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _present(db):
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e1','principal','tip calculator pls',1)")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, "
               "status) VALUES ('s1','e1',0,18,'tip calculator pls','ratified')")
    for iid, kind, text in (
        ("how_it_works", "in_scope", "The user types the bill and a percentage."),
        ("calculate_tip", "in_scope", "The software calculates the tip."),
    ):
        db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
                   "approval_ver, version) VALUES (?,?,?,'decided','draft',0,1)",
                   (iid, text, kind))
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, status, "
               "author) VALUES ('l_1','how_it_works','items',"
               "'the percentage is typed each time','open','vision_keeper')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m9','th','liaison','principal',"
               "'present',?,1,'open')",
               (json.dumps(["calculate_tip", "how_it_works", "s1", "l_1"]),))
    db.commit()
    return pending_asks(db)[0]


def test_the_page_numbers_its_rows_in_the_order_it_shows_them(db):
    ask = _present(db)
    page = ask.rendered
    assert '1. "tip calculator pls"' in page
    assert "2. The user types the bill" in page
    assert "3. The software calculates the tip." in page
    assert "4. the percentage is typed each time" in page
    assert ask.order == ["s1", "how_it_works", "calculate_tip", "l_1"], ask.order
    assert "Reply '2: <words>' to correct line 2 only." in page
    assert "how_it_works" not in page and "l_1" not in page


def test_ok_approves_everything(db):
    ask = _present(db)
    for word in ("ok", "OK", "yes", "lgtm", "approve", "Fine."):
        a = parse_reply(ask, word)
        assert a.verb == "verdict"
        assert set(a.per_item.values()) == {"approve"}
        assert a.text == ""


def test_a_number_and_words_contest_that_line_and_carry_the_words(db):
    ask = _present(db)
    a = parse_reply(ask, "4: no, a fixed 15 percent, nobody types it")
    assert a.per_item["l_1"] == "contest"
    assert a.per_item["s1"] == "approve"
    assert a.per_item["how_it_works"] == "approve"
    assert a.text == "no, a fixed 15 percent, nobody types it"

    b = parse_reply(ask, "2, 4: both wrong")
    assert b.per_item["how_it_works"] == "contest"
    assert b.per_item["l_1"] == "contest"
    assert b.per_item["calculate_tip"] == "approve"
    assert b.text == "both wrong"


def test_a_sentence_alone_contests_the_page_with_that_sentence(db):
    ask = _present(db)
    a = parse_reply(ask, "no service quality. just bill and a percent")
    assert set(a.per_item.values()) == {"contest"}
    assert a.text == "no service quality. just bill and a percent"


def test_scripts_still_rule_by_id(db):
    ask = _present(db)
    a = parse_reply(ask, "s1=approve how_it_works=contest")
    assert a.per_item == {"s1": "approve", "how_it_works": "contest"}


def test_a_clarify_reply_is_the_answer(db):
    ask = Ask(message_id="m1", verb="clarify", refs=["c_1"])
    a = parse_reply(ask, "exactly what the criteria say")
    assert a.verb == "converse" and a.text == "exactly what the criteria say"
