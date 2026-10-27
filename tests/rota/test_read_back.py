"""
The read-back line: every page shows him his last answer as the team read
it (the seam design of 2026-10-26, 2.3, pass 5).

Roman ruled on 2026-10-26 at about 22:5x that the Liaison's reading of his
reply is shown back to him every time: "No it should be every time no? Why
not". The code writes the line from the `ruled_refs` columns. His approve of
the line confirms every row of the reply. His contest makes new rows, and
the next page reads those back once. A reply that leaves the line out
confirms nothing, because silence is not consent (the review, finding 1).
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import _apply_write, init_db
from rota.core.runner import _as_write
from rota.roles.api import _table_of_ref
from rota.roles.principal import (READING_REF, _page_body, apply_rulings, land,
                                  parse_reply, pending_asks, readings_owed)

WORDS = ("3 is wrong: a fixed 15 percent, nobody types it. Remove the typed "
         "percentage.")
THREE = {"1": "approve", "2": "approve",
         "3": {"verdict": "contest", "act": "remove", "target": "how_it_works",
               "words": "Remove the typed percentage."}}


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _seed(db):
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e1','principal','tip calculator pls',1)")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES ('s1','e1',0,18,'tip calculator pls',"
               "'ratified')")
    for iid, text in (("how_it_works", "The user types the bill and a percentage."),
                      ("calculate_tip", "The software calculates the tip.")):
        db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                   "version) VALUES (?, ?, 'in_scope', 'draft', 0, 1)",
                   (iid, text))
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "status, author) VALUES ('l_1', 'how_it_works', 'items', "
               "'the percentage is typed each time', 'open', 'vision_keeper')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m8', 'th', 'vision_keeper', "
               "'liaison', 'submit', '[]', 0, 'answered')")


def _present(db, mid, refs, seq):
    db.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, "
               "to_role, verb, body_refs, seq, status) VALUES (?, 'th', "
               "'m8', 'liaison', 'principal', 'present', ?, ?, 'open')",
               (mid, json.dumps(list(refs)), seq))
    db.commit()
    return next(a for a in pending_asks(db) if a.message_id == mid)


def _answer(db, ask, words, rulings):
    """His words to `ask`, the Liaison's reading, and the landing."""
    from rota.core.sandbox import build
    from rota.roles import prompts

    reply = land(db, ask, parse_reply(ask, words))
    db.commit()
    sb = build("liaison", db, mode="normal", session_id=f"s_{reply}",
               allow=prompts.mode_tools("liaison", "landing"))
    sb.ctx.trigger = reply
    out = sb.call("rulings.rule", rulings=rulings, words=words)
    for w in sb.ctx.writes:
        _apply_write(db, _as_write(w))
    db.commit()
    apply_rulings(db)
    db.commit()
    return reply, out


def _confirmed(db, reply):
    return {r["ref"]: r["confirmed_by"] for r in db.execute(
        "SELECT ref, confirmed_by FROM ruled_refs_live WHERE reply_id = ? "
        "AND substr(ref, 1, 8) != 'reading:'", (reply,))}


def _first_reply(db):
    _seed(db)
    ask = _present(db, "m9", ("calculate_tip", "s1", "l_1"), 1)
    return _answer(db, ask, WORDS, THREE)


def test_a_reply_that_rules_three_refs_gives_one_line_last_with_three_clauses(db):
    reply, _ = _first_reply(db)
    owed = readings_owed(db)
    assert owed == [READING_REF + reply]
    page, order = _page_body(db, "present", ["calculate_tip", "s1"] + owed,
                             ask_id="m_p2")
    lines = page.splitlines()
    assert order[-1] == READING_REF + reply
    last = lines[-1]
    assert last.startswith(f"  {len(order)}. Your answer \"3 is wrong")
    assert last.endswith("Say ok, or say what we misread.")
    told = last.split("as the team read it: ")[1]
    clauses = told[:-len(". Say ok, or say what we misread.")].split("; ")
    assert clauses == ["line 3 is wrong: remove how_it_works",
                       "2 lines approved"], clauses
    assert len(clauses) <= 3
    assert sum(1 for l in lines if "as the team read it" in l) == 1
    # The confirm page takes the line as well.
    page, order = _page_body(db, "confirm", ["s1"] + owed)
    assert order[-1] == READING_REF + reply
    assert "as the team read it" in page.splitlines()[-1]


def test_a_shift_page_and_a_clarify_carry_no_line(db):
    reply, _ = _first_reply(db)
    ref = READING_REF + reply
    from rota.roles.principal import SHIFT_ASK

    page, order = _page_body(db, "present", ["calculate_tip", "s1", ref],
                             ask_id=SHIFT_ASK + "x")
    assert ref not in order and "as the team read it" not in page
    page, order = _page_body(db, "clarify", ["s1", ref], "Which tip?")
    assert ref not in order and "as the team read it" not in page


def test_ok_confirms_every_row_of_that_reply(db):
    reply, _ = _first_reply(db)
    ref = READING_REF + reply
    assert set(_confirmed(db, reply).values()) == {None}
    ask = _present(db, "m_p2", ["calculate_tip", "s1", ref], 5)
    assert ask.order[-1] == ref
    ok, _ = _answer(db, ask, "ok", {str(i + 1): "approve"
                                    for i in range(len(ask.order))})
    assert set(_confirmed(db, reply).values()) == {ok}
    provenance = {r["provenance"] for r in db.execute(
        "SELECT provenance FROM ruled_refs_live WHERE reply_id = ?", (reply,))}
    assert provenance == {"decided"}
    # The confirmed reply is owed no more. The "ok" is the next reading.
    assert readings_owed(db) == [READING_REF + ok]
    # The verdict relays no read-back ref to an owner.
    verdict = db.execute("SELECT body_refs FROM messages WHERE cause_id = 'm_p2' "
                         "AND verb = 'verdict'").fetchone()
    assert ref not in json.loads(verdict["body_refs"])


def test_a_contest_supersedes_and_the_next_page_reads_the_new_rows_once(db):
    reply, _ = _first_reply(db)
    ref = READING_REF + reply
    ask = _present(db, "m_p2", ["calculate_tip", "s1", "l_1", ref], 5)
    line = ask.order.index(ref) + 1
    assert line == 4
    words = "4 is wrong. 2 is wrong: the software does not calculate the tip."
    rulings = {"1": "approve", "2": "contest", "3": "approve", "4": "contest"}
    again, _ = _answer(db, ask, words, rulings)
    # The contest confirms nothing, and the new row on the item supersedes.
    assert set(_confirmed(db, reply).values()) == {None}
    old = db.execute("SELECT status FROM ruled_refs_live WHERE reply_id = ? "
                     "AND ref = 'l_1'", (reply,)).fetchone()
    assert old["status"] == "superseded"
    # The next page reads back the new reply once and the contested one no more.
    owed = readings_owed(db)
    assert owed == [READING_REF + again]
    page, order = _page_body(db, "present", ["calculate_tip", "s1"] + owed,
                             ask_id="m_p3")
    assert sum(1 for l in page.splitlines() if "as the team read it" in l) == 1
    assert "line 2 is wrong; 2 lines approved." in page.splitlines()[-1]
    # A row on a read-back ref is never read back.
    assert "line 4" not in page.splitlines()[-1]


def test_a_reply_that_ignores_the_line_confirms_nothing(db):
    reply, _ = _first_reply(db)
    ref = READING_REF + reply
    ask = _present(db, "m_p2", ["calculate_tip", "s1", ref], 5)
    assert len(ask.order) == 3
    # The every-line rule asks no ruling of the read-back line.
    words = "2 is fine, and 1 is fine as well."
    again, out = _answer(db, ask, words, {"1": "approve", "2": "approve"})
    assert ref not in out["per_item"]
    assert set(_confirmed(db, reply).values()) == {None}
    assert READING_REF + reply in readings_owed(db)


def test_basis_ruled_counts_a_confirmed_reading_only(db):
    reply, out = _first_reply(db)
    db.execute("INSERT INTO refs (src_table, src_id, kind, target) VALUES "
               "('items', 'calculate_tip', 'ruling', ?)", (out["id"],))
    db.commit()
    prov = lambda: db.execute("SELECT provenance FROM item_provenance "  # noqa: E731
                              "WHERE id = 'calculate_tip'").fetchone()[0]
    assert prov() == "reasoned"
    ask = _present(db, "m_p2", ["calculate_tip", "s1", READING_REF + reply], 5)
    _answer(db, ask, "ok", {str(i + 1): "approve"
                            for i in range(len(ask.order))})
    assert prov() == "decided"


def test_table_of_ref_knows_a_reading_ref(db):
    reply, _ = _first_reply(db)
    assert _table_of_ref(db, READING_REF + reply) == "messages"
    assert _table_of_ref(db, READING_REF + "m_none") is None
    assert _table_of_ref(db, "calculate_tip") == "items"


def test_the_night_report_counts_the_rows_unconfirmed_at_the_end(db):
    from rota.tools.nightreport import Night, _unconfirmed_line

    _first_reply(db)
    assert _unconfirmed_line(Night(db)) == (
        "read-back: 3 rows of 1 replies unconfirmed at the night's end")


@pytest.mark.parametrize("verb, refs", [("present", ["calculate_tip"]),
                                        ("confirm", ["s1"])])
def test_the_send_door_writes_the_reading_ref_into_the_page(db, verb, refs):
    from rota.core.sandbox import build

    reply, _ = _first_reply(db)
    sb = build("liaison", db, mode="normal", session_id=f"s_send_{verb}")
    sb.ctx.trigger = "m8"
    sb.call(f"msg.{verb}_principal", refs=refs)
    sent = sb.ctx.outbound[-1]["body_refs"]
    assert sent[-1] == READING_REF + reply, sent


def test_a_contest_of_the_line_rules_a_row_the_new_page_does_not_hold(db):
    """The review of pass 5, finding 1: page 2 holds s1 and the line only."""
    reply, _ = _first_reply(db)
    ref = READING_REF + reply
    ask = _present(db, "m_p2", ["s1", ref], 5)
    assert ask.order == ["s1", ref]
    words = "2 is wrong: it was not a remove. Keep how_it_works."
    again, out = _answer(db, ask, words, {
        "1": "approve", "2": "contest",
        "l_1": {"verdict": "approve", "act": "keep", "target": "how_it_works"}})
    assert out["per_item"]["l_1"] == "approve", out
    old = db.execute("SELECT status FROM ruled_refs_live WHERE reply_id = ? "
                     "AND ref = 'l_1'", (reply,)).fetchone()
    assert old["status"] == "superseded"
    # The next page reads the corrected row back once.
    owed = readings_owed(db)
    assert owed == [READING_REF + again]
    page, _ = _page_body(db, "present", ["calculate_tip"] + owed, ask_id="m_p3")
    assert "keep how_it_works" in page.splitlines()[-1]


def test_a_row_of_the_earlier_answer_needs_his_contest_of_the_line(db):
    reply, _ = _first_reply(db)
    ask = _present(db, "m_p2", ["s1", READING_REF + reply], 5)
    with pytest.raises(ValueError, match="read-back line 2"):
        _answer(db, ask, "1 is fine. Keep how_it_works.",
                {"1": "approve", "2": "approve", "l_1": "approve"})


def test_only_his_words_confirm_the_line(db):
    """The review of pass 5, finding 2: words that skip line 3 approve
    lines 1 and 2, and the door refuses the approve of line 3."""
    reply, _ = _first_reply(db)
    ref = READING_REF + reply
    ask = _present(db, "m_p2", ["calculate_tip", "s1", ref], 5)
    with pytest.raises(ValueError, match="only his words confirm it"):
        _answer(db, ask, "2 is fine, and 1 is fine as well.",
                {"1": "approve", "2": "approve", "3": "approve"})
    assert set(_confirmed(db, reply).values()) == {None}


def test_a_page_that_holds_a_confirmed_ref_shows_no_line(db):
    """The review of pass 5, finding 4."""
    reply, _ = _first_reply(db)
    ref = READING_REF + reply
    _present(db, "m_p4", ["calculate_tip", ref], 4)
    ask = _present(db, "m_p2", ["calculate_tip", "s1", ref], 5)
    _answer(db, ask, "ok", {str(i + 1): "approve" for i in range(len(ask.order))})
    page, order = _page_body(db, "present", ["calculate_tip", ref], ask_id="m_p4")
    assert ref not in order and "as the team read it" not in page
