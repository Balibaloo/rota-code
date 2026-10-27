"""
A contest can rest on an earlier answer of the exchange on the same page.

Night 168 (frame 337): m76 said "Line 5 is wrong", the Liaison asked m77
about line 6, and m78 named line 6 only. s193 contested line 5 on m78 and
the naming door refused it twice. s194 then approved line 5, the line he
called wrong. The door now reads the lines that his earlier answers to
the page name. The quotes are the record's, `plans/wb-naming-provenance.md`,
section 3.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db

from .test_frame234_verdict_lines import M131, S281, _rule11
from .test_principal_reply import _landing, _present


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


M76 = ("Line 5 is wrong: ... I don't understand line 6, so what is that "
       "ticket ... The other lines are fine.")
M78 = "... so line 6 is fine as it stands."
S193 = {"1": "approve", "2": "approve", "3": "approve", "4": "approve",
        "5": "contest", "6": "approve"}
REFUSAL = ("The words name line 6 and do not name line 5. A contest rests on "
           "the principal's words. Approve the lines the words do not name, or "
           "rule them as the words say.")


def _page6(db, earlier):
    """m75's page shape on the `_present` fixture: line 1 the request item,
    lines 2 to 4 its criteria, line 5 the note
    `challenge_items_clear_returns_status` and line 6 the note
    `l_c5331791cf`. Each text of `earlier` is his answer to the page, and
    the Liaison's question follows it, as m76 and m77 do."""
    from rota.roles.principal import pending_asks

    _present(db)
    for iid in ("c1", "c2", "c3"):
        db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                   "version) VALUES (?,?,'in_scope','draft',0,1)",
                   (iid, "criterion " + iid))
    for lid in ("challenge_items_clear_returns_status", "l_c5331791cf"):
        db.execute("INSERT INTO ledger (id, about_ref, about_table, "
                   "default_taken, status, author) VALUES (?,'how_it_works',"
                   "'items',?,'open','critic')", (lid, "note text " + lid))
    refs = ["calculate_tip", "c1", "c2", "c3",
            "challenge_items_clear_returns_status", "l_c5331791cf"]
    db.execute("UPDATE messages SET body_refs = ? WHERE id = 'm9'",
               (json.dumps(refs),))
    for k, text in enumerate(earlier):
        mid, qid = f"m7{6 + 2 * k}", f"m7{7 + 2 * k}"
        db.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, "
                   "to_role, verb, body_refs, body_text, seq, status) VALUES "
                   "(?,'th','m9','principal','liaison','converse','[]',?,?,"
                   "'answered')", (mid, text, 2 + 2 * k))
        db.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, "
                   "to_role, verb, body_refs, body_text, seq, status) VALUES "
                   "(?,'th',?,'liaison','principal','converse','[]',"
                   "'What is the ticket on line 6?',?,'answered')",
                   (qid, mid, 3 + 2 * k))
    db.commit()
    ask = pending_asks(db)[0]
    assert ask.order == refs, ask.order
    return ask


def _rule6(db, earlier, words=M78, rulings=S193):
    ask = _page6(db, earlier)
    sb, _ = _landing(db, ask, words)
    return sb.call("rulings.rule", rulings=rulings, words=words)


def test_s193s_contest_of_line_5_lands_on_m76_in_the_exchange(db):
    out = _rule6(db, [M76])
    assert out["per_item"]["challenge_items_clear_returns_status"] == "contest"


def test_s193s_contest_is_refused_with_no_earlier_answer(db):
    with pytest.raises(ValueError) as e:
        _rule6(db, [])
    assert str(e.value) == REFUSAL


def test_s281s_single_reply_stays_refused_with_the_same_text(db):
    with pytest.raises(ValueError) as e:
        _rule11(db, M131, S281)
    assert str(e.value) == (
        "The words name lines 3, 4 and 7 and do not name lines 5, 6 and 8 to "
        "11. A contest rests on the principal's words. Approve the lines the "
        "words do not name, or rule them as the words say.")


def test_an_earlier_answer_that_names_no_line_leaves_the_contest_refused(db):
    with pytest.raises(ValueError) as e:
        _rule6(db, ["I don't understand the ticket, so what is it?"])
    assert str(e.value).startswith(REFUSAL)


def test_the_refusal_says_that_it_read_the_earlier_answers(db):
    with pytest.raises(ValueError) as e:
        _rule6(db, ["I don't understand the ticket, so what is it?"])
    assert str(e.value) == (REFUSAL + " His earlier answers to this page do "
                            "not name line 5 either.")


# Review 1, finding 1: an earlier "Line 5 is fine" let the contest of line 5
# land against his word. The latest answer about a line wins.
def test_an_earlier_match_with_no_later_word_refuses_the_contest(db):
    with pytest.raises(ValueError) as e:
        _rule6(db, ["Line 5 is fine. What is the ticket on line 6?"])
    assert str(e.value).startswith("The words say line 5 matches what the "
                                   "principal asked for")


def test_a_later_fault_after_an_earlier_match_lands_the_contest(db):
    out = _rule6(db, ["Line 5 is fine. What is the ticket on line 6?",
                      "Line 5 is wrong after all."])
    assert out["per_item"]["challenge_items_clear_returns_status"] == "contest"


def test_s193s_row_on_line_5_takes_its_words_from_m76(db):
    """The seam design, pass 2: the row on line 5 records m76 as the source
    of its words, and the row on line 6 keeps the reply m78."""
    ask = _page6(db, [M76])
    sb, _ = _landing(db, ask, M78)
    sb.call("rulings.rule", rulings=S193, words=M78)
    rows = {w[2]["ref"]: w[2] for w in sb.ctx.writes if w[0] == "ruled_refs"}
    five = rows["challenge_items_clear_returns_status"]
    assert (five["line"], five["words_from"]) == (5, "m76")
    assert five["words"] == "Line 5 is wrong: ..."
    assert rows["l_c5331791cf"]["words_from"] == sb.ctx.trigger
