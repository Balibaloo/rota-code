"""
The page the principal sees is a message, not a list of ids.

Measured on the tips runs (2026-09-03), as the principal: every ask arrived as
a verb name and ids -- "confirm: s1: tip calculator pls", "present: k0:
Nobody has read this area yet...", "l_a69ad6edd4: assumed: ..." -- and a
newcomer could not tell what was being asked, what approving would start, or
which words were theirs. `render_ask` composes the page once, for every seat:
a frame per verb saying what the answer does, no ids in the prose, the
principal's words quoted as theirs, the account before the behaviours, what
was assumed in its own place, constraint zero in a sentence a person can act
on. The CLI keeps the ids in its header line for `rota sign`.
"""
from __future__ import annotations

import json
import re

import pytest

from rota.core.db import init_db
from rota.roles.principal import pending_asks, render_ask
from rota.testkit.fixtures import seed_provenance

RAW_ID = re.compile(r"\b(l_[0-9a-f]{6,}|s\d+|k0|t\d+|i_[0-9a-f]{6}|how_it_works|m\d+)\b")


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _ask(db, mid, verb, refs, text=None):
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, body_text, seq, status) VALUES (?, 'th', 'liaison', "
               "'principal', ?, ?, ?, 1, 'open')", (mid, verb, json.dumps(refs), text))
    db.commit()
    return next(a for a in pending_asks(db) if a.message_id == mid)


def test_a_confirm_asks_whether_it_heard_right_and_quotes_the_words(db):
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e1','principal','tip calculator pls',1)")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, "
               "status) VALUES ('s1','e1',0,18,'tip calculator pls','proposed')")
    db.commit()
    ask = _ask(db, "m1", "confirm", ["s1"])
    page = ask.rendered
    assert page.startswith("Did I hear you right?"), page
    assert "one request" in page
    assert '"tip calculator pls"' in page, "their words, quoted as theirs"
    assert "Reply 'ok' if that is what you meant" in page
    assert "before anything is written" in page, "what approving starts"
    assert not RAW_ID.search(page), page


def test_a_signoff_page_reads_as_one_page_in_order(db):
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e1','principal','tip calculator pls',1)")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, "
               "status) VALUES ('s1','e1',0,18,'tip calculator pls','ratified')")
    for iid, kind, text in (
        ("calculate_tip", "in_scope", "The software calculates the tip from the bill and a percentage."),
        ("how_it_works", "in_scope", "The user types the bill and a tip percentage; the program prints the tip."),
        ("no_gui", "out_of_scope", "No graphical interface."),
    ):
        db.execute("INSERT INTO items (id, text, kind, approval, "
                   "approval_ver, version) VALUES (?,?,?,'draft',0,1)",
                   (iid, text, kind))
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, status, "
               "author) VALUES ('l_a69ad6edd4','how_it_works','items',"
               "'the percentage is typed each time, not a fixed tier','open','vision_keeper')")
    db.commit()
    ask = _ask(db, "m9", "present", ["calculate_tip", "how_it_works", "s1", "l_a69ad6edd4", "no_gui"])
    page = ask.rendered
    assert page.startswith("Here is what I understand you want, on one page."), page
    order = [page.index(x) for x in (
        "You asked:", '"tip calculator pls"',
        "What we are building:", "The user types the bill",
        "It would:", "calculates the tip",
        "It would not:", "No graphical interface",
        "Where you did not say, I assumed:", "typed each time",
        "Reply in your own words.")]
    assert order == sorted(order), page
    assert "Name a line to correct only that line." in page
    assert not RAW_ID.search(page), page
    assert ": assumed:" not in page, "the old id-shaped rendering is gone from the page"


def test_constraint_zero_is_a_sentence_a_person_can_act_on(db):
    db.execute("INSERT INTO constraints (id, headline, text) VALUES "
               "('k0','this codebase is not yet understood',"
               "'Nobody has read this area yet, so what it is committed to is unknown.')")
    seed_provenance(db, "constraints", "k0", "observed")
    db.commit()
    ask = _ask(db, "m12", "present", ["k0"])
    page = ask.rendered
    assert page.startswith("Nothing here has been read yet"), page
    assert "That is normal for a new or unread project." in page
    assert "Reply 'ok' to go ahead" in page
    assert "committed to is unknown" not in page, "the doctrine's wording stays with the roles"
    assert "k0" not in page


def test_a_clarify_carries_the_question_its_context_and_the_bargain(db):
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('how_it_works','a tip calculator','in_scope',"
               "'approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text, version) VALUES "
               "('tk1','how_it_works','a ticket',1)")
    for cid, text in (("c_1", "The tip calculator must accept a total bill amount as input."),
                      ("c_2", "The tip calculator must accept a tip percentage as input.")):
        db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, 'tk1', ?)", (cid, text))
    db.commit()
    ask = _ask(db, "m18", "clarify", ["c_1", "c_2"],
               "What behaviour should these tests exercise?")
    page = ask.rendered
    assert page.startswith("I need one thing from you before I can continue."), page
    assert "What behaviour should these tests exercise?" in page
    assert "This is about:" in page and "accept a total bill amount" in page
    assert page.rstrip().endswith("Reply in a sentence. I take it from there.")
    assert "c_1" not in page and "c_2" not in page


def test_the_cli_header_keeps_the_ids_for_rota_sign(db):
    """The prose has no ids; `rota sign --approve <id>` still needs them."""
    from pathlib import Path
    src = (Path(__file__).resolve().parents[2] / "rota" / "cli.py").read_text(encoding="utf-8")
    assert "rule by id: {', '.join(a.refs)}" in src
