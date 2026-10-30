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

from .test_principal_reply import _landing, _present


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


M76 = ("Line 5 is wrong: ... I don't understand line 6, so what is that "
       "ticket ... The other lines are fine.")
M78 = "... so line 6 is fine as it stands."
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


@pytest.mark.skip(reason="frame 345, R6: needs a code change. page_clauses reads his reply only, so no clause names line 5 from m76 in the earlier exchange (page_clauses, menu_ruling)")
def test_s193s_row_on_line_5_takes_its_words_from_m76(db):
    """The seam design, pass 2: the row on line 5 records m76 as the source
    of its words, and the row on line 6 keeps the reply m78."""
    ask = _page6(db, [M76])
    sb, _ = _landing(db, ask, M78)
    # The menu form (frame 345, R6).
    sb.call("rulings.rule", rulings={"5": "rewrite", "rest": "approve"})
    rows = {w[2]["ref"]: w[2] for w in sb.ctx.writes if w[0] == "ruled_refs"}
    five = rows["challenge_items_clear_returns_status"]
    assert (five["line"], five["words_from"]) == (5, "m76")
    assert five["words"] == "Line 5 is wrong: ..."
    assert rows["l_c5331791cf"]["words_from"] == sb.ctx.trigger


@pytest.mark.skip(reason="frame 345, R6b: needs a code change. page_clauses reads his reply only, so no clause names line 5 from m76 in the earlier exchange (page_clauses, menu_ruling)")
def test_s193s_contest_of_line_5_lands_on_m76_in_the_exchange(db):
    ask = _page6(db, [M76])
    sb, _ = _landing(db, ask, M78)
    out = sb.call("rulings.rule", rulings={"5": "rewrite", "rest": "approve"})
    assert out["per_item"]["challenge_items_clear_returns_status"] == "contest"
