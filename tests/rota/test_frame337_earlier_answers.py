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


def test_s193s_row_on_line_5_takes_its_words_from_m76(db):
    """The seam design, pass 2: the row on line 5 records m76 as the source
    of its words, and the row on line 6 keeps the reply m78."""
    ask = _page6(db, [M76])
    sb, _ = _landing(db, ask, M78)
    # The menu form (frame 345, R6). Frame 347, pass 3: m76 names line 5,
    # and the reply m78 names line 6, so the call keys both.
    sb.call("rulings.rule", rulings={"5": "rewrite", "6": "approve",
                                     "rest": "approve"})
    rows = {w[2]["ref"]: w[2] for w in sb.ctx.writes if w[0] == "ruled_refs"}
    five = rows["challenge_items_clear_returns_status"]
    assert (five["line"], five["words_from"]) == (5, "m76")
    assert five["words"] == "Line 5 is wrong: ..."
    assert rows["l_c5331791cf"]["words_from"] == sb.ctx.trigger


def test_s193s_contest_of_line_5_lands_on_m76_in_the_exchange(db):
    ask = _page6(db, [M76])
    sb, _ = _landing(db, ask, M78)
    out = sb.call("rulings.rule", rulings={"5": "rewrite", "6": "approve",
                                           "rest": "approve"})
    assert out["per_item"]["challenge_items_clear_returns_status"] == "contest"


def test_his_latest_earlier_answer_on_a_line_wins(db):
    """Frame 347, pass 3b, review p3 probe A2: his later "Line 5 is fine."
    wins over his first "Line 5 is wrong". Frame 337 pass 2 ruled that his
    latest answer about a line wins. Line 5 takes the words of m78, the
    second earlier answer of `_page6`. The menu reads no polarity, so a
    contest of line 5 is the seat's to refuse, not the door's."""
    ask = _page6(db, ["Line 5 is wrong.", "Line 5 is fine."])
    sb, _ = _landing(db, ask, M78)
    out = sb.call("rulings.rule", rulings={"5": "approve", "6": "approve",
                                           "rest": "approve"})
    assert out["per_item"]["challenge_items_clear_returns_status"] == "approve"
    rows = {w[2]["ref"]: w[2] for w in sb.ctx.writes if w[0] == "ruled_refs"}
    five = rows["challenge_items_clear_returns_status"]
    assert (five["words"], five["words_from"]) == ("Line 5 is fine.", "m78")


def test_an_answer_to_a_second_page_of_the_thread_names_no_line(db):
    """Review p3, low 2: his answer to a second page of the Liaison in the
    same thread is no earlier answer to this page."""
    from rota.roles.api import _earlier_answers

    ask = _page6(db, [M76])
    db.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, "
               "to_role, verb, body_refs, seq, status) VALUES ('m90','th',"
               "'m77','liaison','principal','present','[]',10,'answered')")
    db.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, "
               "to_role, verb, body_refs, body_text, seq, status) VALUES "
               "('m91','th','m90','principal','liaison','converse','[]',"
               "'Line 2 is wrong.',11,'answered')")
    db.commit()
    sb, _ = _landing(db, ask, M78)
    assert _earlier_answers(sb.ctx, ask.message_id) == (M76,)


def test_his_earlier_wrong_binds_a_line_that_the_reply_does_not_name(db):
    """Frame 348, L3R-n175-m11-m14: m12 said "Line 2 is wrong", and the
    reply m14 named no line. The reply's fallback covered line 2, and the
    seat approved it. The earlier answer now binds line 2, so the menu
    refuses approve there, and the row takes the earlier words."""
    ask = _page6(db, ["Line 2 is wrong."])
    sb, _ = _landing(db, ask, SILENT)
    keys = {"1": "approve", "3": "approve", "4": "approve", "5": "approve",
            "6": "approve"}
    with pytest.raises(ValueError, match=r"line 2 takes no approve"):
        sb.call("rulings.rule", rulings={**keys, "2": "approve"})
    out = sb.call("rulings.rule",
                  rulings={**keys, "2": "other Line 2 is wrong."})
    assert out["per_item"]["c1"] == "contest"
    assert out["per_item"]["calculate_tip"] == "approve"
    rows = {w[2]["ref"]: w[2] for w in sb.ctx.writes if w[0] == "ruled_refs"}
    assert (rows["c1"]["words"], rows["c1"]["words_from"]) == (
        "Line 2 is wrong.", "m76")


ALL_APPROVE = {str(n): "approve" for n in range(1, 7)}
# A reply that names no line and asks nothing. "Please tell me where ..."
# is a request for facts since frame 348, pass 3.
SILENT = "I had another look at the page."


def test_a_bare_mention_in_the_reply_keeps_the_earlier_fault(db):
    """Frame 348, review p1, high 1: "I looked at line 2 again." has line 2
    as no subject and carries no verdict, so it does not re-open the line
    that his earlier answer called wrong."""
    ask = _page6(db, ["Line 2 is wrong."])
    sb, _ = _landing(db, ask, "I looked at line 2 again.")
    with pytest.raises(ValueError, match=r"line 2 takes no approve"):
        sb.call("rulings.rule", rulings=ALL_APPROVE)


def test_the_approve_refusal_fires_on_every_call(db):
    """Frame 348, review p2, high 1: a second approve still rules against
    his words, so it is refused again (law 6). The ask is the way out. The
    shared reader also faults "Line 2 was wrong before, now it is fine.",
    and that misread is a residue of `_line_reading`, not fixed here."""
    ask = _page6(db, ["Line 2 is wrong."])
    sb, _ = _landing(db, ask, SILENT)
    for _call in range(2):
        with pytest.raises(ValueError, match=r"line 2 takes no approve") as hit:
            sb.call("rulings.rule", rulings=ALL_APPROVE)
    # Review p1, low 4: the menu in the refusal leaves approve out.
    assert "takes approve" not in str(hit.value)
    assert "rulings.rule(ask=" in str(hit.value)


@pytest.mark.parametrize("earlier", [
    "Line 2 is wrong, and tell me where line 3 came from.",
    # One clause that faults and asks (review p2, high 2).
    "Line 2 is wrong and tell me where it came from.",
])
def test_an_earlier_fault_beside_an_ask_still_binds(db, earlier):
    """Review p2, high 2: the fault on line 2 binds, though the clause also
    asks. Line 3 has no verdict word, so the ask keeps it unbound."""
    ask = _page6(db, [earlier])
    sb, _ = _landing(db, ask, SILENT)
    with pytest.raises(ValueError, match=r"line 2 takes no approve"):
        sb.call("rulings.rule", rulings=ALL_APPROVE)
    out = sb.call("rulings.rule",
                  rulings={**ALL_APPROVE, "2": "other Line 2 is wrong"})
    assert out["per_item"]["c1"] == "contest"
    # Line 3 binds nothing: its row carries the reply's words.
    rows = {w[2]["ref"]: w[2] for w in sb.ctx.writes if w[0] == "ruled_refs"}
    assert rows["c2"]["words"] == SILENT


def test_a_line_his_earlier_answer_approves_stays_in_the_fallback(db):
    """Frame 348, review p1, low 3: "Line 2 is fine." faults nothing, so the
    reply's clause still covers line 2, and its clause key approves it."""
    ask = _page6(db, ["Line 2 is fine."])
    sb, _ = _landing(db, ask, SILENT)
    out = sb.call("rulings.rule", rulings={"c1": "approve"})
    assert out["per_item"]["c1"] == "approve"


@pytest.mark.parametrize("earlier, line, faulted", [
    ("Line 3 is unclear to me, so please say what it means.", "3", False),
    ("Line 2 is wrong and tell me where it came from.", "2", True),
])
def test_a_request_about_a_line_binds_no_fault(db, earlier, line, faulted):
    """Review p3: the reader faults a line on the verb of his request, as
    "say what it means". The fault is read with the request removed, so a
    request about line 3 binds nothing there. A fault beside the request
    still binds."""
    ask = _page6(db, [earlier])
    sb, _ = _landing(db, ask, SILENT)
    if faulted:
        with pytest.raises(ValueError, match=rf"line {line} takes no approve"):
            sb.call("rulings.rule", rulings=ALL_APPROVE)
    else:
        out = sb.call("rulings.rule", rulings=ALL_APPROVE)
        assert set(out["per_item"].values()) == {"approve"}


@pytest.mark.parametrize("earlier, line, ref", [
    ("Tell me what line 2 means, because it is wrong.", "2", "c1"),
    # The fault names line 4, so the request keeps line 2 unbound.
    ("Tell me what line 2 means, line 4 is wrong.", "4", "c3"),
    ("Please explain why line 2 is wrong.", "2", "c1"),
])
def test_a_fault_after_a_request_in_the_same_sentence_binds(db, earlier,
                                                           line, ref):
    """Review p4, finding 1: the request span ran to the sentence end and
    removed the fault after the request. Now a question clause faults a
    line on a fault word only, so the request binds nothing and the fault
    binds its line. Each other line still takes approve."""
    ask = _page6(db, [earlier])
    sb, _ = _landing(db, ask, SILENT)
    with pytest.raises(ValueError, match=rf"line {line} takes no approve"):
        sb.call("rulings.rule", rulings=ALL_APPROVE)
    out = sb.call("rulings.rule",
                  rulings={**ALL_APPROVE, line: f"other Line {line} is wrong."})
    assert out["per_item"][ref] == "contest"
    assert {r for r, v in out["per_item"].items() if v != "approve"} == {ref}


@pytest.mark.parametrize("earlier", [
    # L3R-n175-m11-m14's reply: "not" describes line 3, and "so I can tell
    # you if it is right" defers the verdict (review p5, finding 1).
    "I was asking you that, because line 3 only says the team could not "
    "check a claim about an argument and never says which claim. Please "
    "tell me what the claim says and where it came from, so I can tell you "
    "if it is right.",
    # He asks about a claim of line 3 and rules no line (review p5, finding 2).
    "Tell me why line 3 says line 2 is wrong.",
])
def test_a_line_a_request_names_in_passing_binds_no_fault(db, earlier):
    """Review p5: a question clause bound every faulted line it listed, so a
    negation cue or a relating verb bound a line he only described. Now a
    line that is no subject binds on a fault word only."""
    ask = _page6(db, [earlier])
    sb, _ = _landing(db, ask, SILENT)
    out = sb.call("rulings.rule", rulings=ALL_APPROVE)
    assert set(out["per_item"].values()) == {"approve"}
