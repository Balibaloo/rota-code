"""Frame 258: a contest of the request line under a correction of its criteria.

Night 161, walk 2, page m66. Line 1 is the item confirm_default_on_eof,
lines 2 to 4 its criteria cr_1 to cr_3, and line 5 the batch b_2 with a
head commit. s181 ruled lines 1 to 4 contest on m67's words, and the door
admitted the line-1 contest. The words fault lines 2 to 4 only. Their
unnumbered sentences share "closed", "stdin", "default", "true" and "false"
with the request, and every one of those words is in cr_1 to cr_3
(`plans/frame258-provenance.md`, sections 1 and 5). The texts are verbatim
from `.rota/clickI.db`.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db

from .test_request_page import (
    P, _criteria, _dispatch, _item, _landing, _reply, _statement, _verdict,
)

ITEM = "confirm_default_on_eof"
TEXT = ("Let confirm() take a default_on_eof flag: when stdin is closed it "
        "returns the default (True or False) instead of aborting.")
CRIT = [
    ("cr_1_confirm_default_on_eof",
     "confirm() accepts a new boolean flag 'default_on_eof' that defaults to "
     "False. When this flag is True and stdin is closed (EOF), confirm() "
     "returns the provided default value instead of raising an exception or "
     "aborting."),
    ("cr_2_confirm_default_on_eof",
     "When default_on_eof is True and stdin is closed, confirm() must not "
     "raise UsageError or any other exception."),
    ("cr_3_confirm_default_on_eof",
     "The default value passed to confirm() is returned when default_on_eof "
     "is True and stdin is closed, regardless of the prompt text."),
]
KEEP = "I don't want to drop this change, so please fix it and try again."
REST = ("The checks on lines 2, 3 and 4 look wrong: the default for confirm is "
        "yes or no as true or false, not the word \"yes\". The error also "
        "suggests the test's fake closed stdin is broken, so it doesn't test "
        "real end-of-input. Please give the tests a proper closed stdin and "
        "have them expect a true or false default.")
M67 = f"{KEEP} {REST}"
# `_line_set` writes a run of three or more lines as a range.
REFUSAL = ("line 1: the words do not fault the request. They fault lines 2 to "
           "4. Rule lines 2 to 4 as the words say, and approve line 1.")


@pytest.fixture
def page(tmp_path):
    """m66: the item, its three criteria and b_2 with a head commit. The
    touch note sends the page while b_2 is pending, then b_2 is built."""
    db = init_db(tmp_path / "rota.db")
    _statement(db, "s2", TEXT)
    _item(db, ITEM, TEXT, version=1, statement="s2")
    _criteria(db, ITEM, "tk_1_confirm_default_on_eof", CRIT)
    db.execute("INSERT INTO batches (id, item_id, status) VALUES "
               "('b_2', ?, 'pending')", (ITEM,))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
               "('b_2', 'tk_1_confirm_default_on_eof')")
    db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind, "
               "confidence) VALUES ('b_2', 'src/click/termui.py', 'path', "
               "'expected')")
    db.commit()
    (wake,) = P.REGISTRY["touch_note"].fn(db)
    mid = _dispatch(db, wake,
                    f'TOOL: msg.present_principal(refs=["b_2", "{ITEM}"])')
    db.execute("UPDATE batches SET status = 'running', head_commit = "
               "'395e26487ca1f5864ae5750bcf3a5e371cc3e3bf' WHERE id = 'b_2'")
    db.commit()
    return db, mid


def _rule(page, words, ruling):
    db, mid = page
    reply = _reply(db, mid, words)
    out = _landing(db, reply, ruling, words)
    landed = db.execute("SELECT 1 FROM messages WHERE cause_id = ? AND verb = "
                        "'verdict'", (mid,)).fetchone()
    return " ".join(out.errors), _verdict(db, mid)[1] if landed else {}


def _approval(page) -> str:
    return page[0].execute("SELECT approval FROM items WHERE id = ?",
                           (ITEM,)).fetchone()[0]


def test_the_page_is_night_161s_m66(page):
    from rota.roles.principal import pending_asks

    db, mid = page
    (ask,) = [a for a in pending_asks(db) if a.message_id == mid]
    assert ask.order == [ITEM] + [c for c, _ in CRIT] + ["b_2"]


def test_the_refusal_is_under_50_words():
    assert len(REFUSAL.split()) < 50


def test_the_map_with_line_1_approved_lands(page):
    # The menu form (frame 345, R6): clause c3 names lines 2 to 4, and the
    # clauses that name no line rule nothing.
    said, ruled = _rule(page, M67, {
        "c3": "rewrite", **{f"c{k}": "none" for k in (1, 2, 4, 5, 6)},
        "rest": "approve"})
    assert not said, said
    assert ruled.get(ITEM, "approve") == "approve", ruled
    assert _approval(page) == "approved"
    for cid, _ in CRIT:
        assert ruled.get(cid) == "contest", ruled


@pytest.mark.parametrize("words", [
    KEEP,
    "I don't want to drop it.",
    "Please keep the change and fix the tests.",
])
def test_the_keep_rule_reads_the_new_shapes(words):
    from rota.roles.api import _KEEP_CHANGE

    assert _KEEP_CHANGE.search(words)


def test_m25_keeps_its_path():
    """Night 149's m25 names no line, so `_agreed_contest` reads it before
    the line-1 test. Its two results are in `test_frame234_verdict_lines.py`
    (`test_m25s_contest_of_the_description_row_is_refused` and
    `test_m25s_instruction_lands_on_the_request_line`). Here the reader shows
    that m25 faults no line, so the new subtraction has no text to take."""
    from rota.roles.api import _line_reading

    m25 = ("ok, this matches what I asked for. Please keep it to the standard "
           "library json module")
    assert _line_reading(m25)[0] == set()
