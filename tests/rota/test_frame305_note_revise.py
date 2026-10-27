"""
A sentence that asks to change a team's note is a revise of the note.

Night 161, s357 (frame 305): the principal wrote "On line 11, use click
directly in the test instead of installing a separate package." Line 11 was
a ledger row, a team's note. s357 ruled it `revise`, and the door refused:
"line 11 is the team's note, not your request. To drop the note, contest
it." The door fired five times that night, on s156, s356, s357, s358 and
s392. s357 then spent one of the principal's answers on a question back.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db

from .test_frame234_verdict_lines import _request_page
from .test_principal_reply import _landing


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


# Line 11 of s357's page, verbatim (`.rota/clickI_night161.db`, turns).
NOTE_11 = ("the answer did not address the question: The test for the "
           "version_option show_python flag is failing because the "
           "'test_version_option' package is not installed. Should the test be "
           "modified to use 'click' directly instead of 'test_version_option', "
           "or should the package be installed to resolve the issue?")
# A note that holds a drop word of its own. Line 13 of the same page.
NOTE_OWN = "ensure_ascii=False was removed per ruling, keeping json.dumps defaults"


def _page(db, last: str = NOTE_11):
    """The request page of frame 234 with eight more notes: line 11 is a note."""
    ask = _request_page(db)
    notes = [f"l_{k}" for k in range(2, 10)]
    for k, lid in enumerate(notes):
        text = last if lid == "l_9" else f"the team assumed default {k}"
        db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
                   "status, author) VALUES (?, 'how_it_works', 'items', ?, 'open', "
                   "'vision_keeper')", (lid, text))
    db.execute("UPDATE messages SET body_refs = ? WHERE id = 'm9'",
               (json.dumps(ask.order + notes),))
    db.commit()
    from rota.roles.principal import pending_asks

    ask = pending_asks(db)[0]
    assert ask.order[10] == "l_9", ask.order
    return ask


def _rule(db, words, line_11: str, last: str = NOTE_11, **more):
    ask = _page(db, last)
    sb, _ = _landing(db, ask, words)
    rulings = {str(n): "approve" for n in range(1, 12)}
    rulings["11"] = line_11
    rulings.update(more)
    return sb.call("rulings.rule", rulings=rulings, words=words)


def _act(act: str, words: str) -> dict:
    """The object form of a revise of line 11 with its act (pass 4, P11)."""
    return {"verdict": "revise", "act": act, "target_kind": "row",
            "words": words}


def test_s357s_words_revise_the_note_and_land(db):
    words = "On line 11, use the normal test runner"
    out = _rule(db, words, _act("rewrite", words))
    assert out["per_item"]["l_9"] == "revise"


def test_s357s_whole_reply_revises_line_11(db):
    words = ("Lines 10, 13 and 14 are about the echo json change, not this one, "
             "so please take them off this page. On line 11, use click directly "
             "in the test instead of installing a separate package. The rest is "
             "fine.")
    # The page has 11 lines, so line 10 is the one note of the three on it.
    out = _rule(db, words, _act("rewrite", "On line 11, use click directly in "
                                "the test instead of installing a separate "
                                "package."), **{"10": "contest"})
    assert out["per_item"]["l_9"] == "revise"
    assert out["per_item"]["l_8"] == "contest"


@pytest.mark.parametrize("words", ["Drop line 11", "take line 11 off"])
def test_a_drop_of_the_note_is_still_told_to_contest(db, words):
    with pytest.raises(ValueError) as refused:
        _rule(db, words, _act("drop", words))
    text = str(refused.value)
    assert text.startswith("line 11 is the team's note, not your request. "
                           "To drop the note, contest it.")
    assert "To change the note" not in text


@pytest.mark.parametrize("words", ["Drop line 11", "take line 11 off"])
def test_the_contest_of_a_dropped_note_lands(db, words):
    out = _rule(db, words, "contest")
    assert out["per_item"]["l_9"] == "contest"


def test_a_revise_with_no_act_names_both_routes(db):
    """Pass 4: the door reads the act, not a drop word. A revise with no
    act says no route, so the refusal names both."""
    with pytest.raises(ValueError) as refused:
        _rule(db, "Line 11: keep it removed", "revise", last=NOTE_OWN)
    text = str(refused.value)
    assert "To change the note, revise it" in text
    assert "To drop the note, contest it." in text


def test_a_sentence_that_only_describes_the_note_is_no_revise(db):
    with pytest.raises(ValueError) as refused:
        _rule(db, "Line 11 is about the echo json change.", "revise")
    assert str(refused.value).startswith("line 11 is the team's note")


def test_a_question_about_the_note_is_no_revise(db):
    with pytest.raises(ValueError):
        _rule(db, "Should line 11 use click directly?", "revise")


# Pass 2: the review of dcf7a6e3 (`plans/frame305-review-teamnote.md`).

@pytest.mark.parametrize("ruling", ["contest", "revise"])
def test_a_keep_of_the_note_refuses_a_revise_as_it_refuses_a_contest(db, ruling):
    # Finding 1: the keep door read contests only, and a revise slipped by.
    with pytest.raises(ValueError):
        _rule(db, "Leave line 11 as it is.", ruling)


@pytest.mark.parametrize("words", [
    "I don't understand line 11.",                    # night 160, m11
    "Line 11 and its check now say what I want.",     # night 160, m45
    "Line 11: no.",
    "Line 11 is wrong.",
])
def test_words_with_no_change_are_no_revise(db, words):
    # Finding 2: a confusion, an agreement or a bare fault asks no change.
    with pytest.raises(ValueError) as refused:
        _rule(db, words, "revise")
    assert str(refused.value).startswith("line 11 is the team's note")


@pytest.mark.parametrize("words", [
    "Line 11 should say that callers don't need to change anything.",
    "Line 11 should say the escaping is not needed.",
])
def test_a_change_that_holds_a_need_word_is_a_revise(db, words):
    # Finding 4: "don't need" and "not needed" are no drop words. The act
    # `rewrite` says the change (pass 4).
    out = _rule(db, words, _act("rewrite", words))
    assert out["per_item"]["l_9"] == "revise"


def test_a_plain_drop_of_a_note_that_holds_the_word_is_a_drop(db):
    # Finding 5: the note holds "removed", and "Remove" is another word.
    with pytest.raises(ValueError) as refused:
        _rule(db, "Remove line 11.", _act("drop", "Remove line 11."),
              last=NOTE_OWN)
    assert "To change the note" not in str(refused.value)


def test_the_refusal_says_the_words_must_name_the_line(db):
    # Finding 3: the door reads a reference by number only.
    with pytest.raises(ValueError) as refused:
        _rule(db, "Use click directly in the test.", "revise")
    assert "words that name line 11 by number" in str(refused.value)


# Pass 4b: the review of pass 4, P4-1. The door checks an act against his
# words. Red on fbce68db, where a rewrite act landed on any words.

@pytest.mark.parametrize("words", [
    "I don't understand line 11.",                    # night 160, m11
    "Line 11 and its check now say what I want.",     # night 160, m45
    "Line 11 is wrong.",
])
def test_a_rewrite_act_on_words_that_ask_no_change_is_refused(db, words):
    with pytest.raises(ValueError) as refused:
        _rule(db, words, _act("rewrite", words))
    assert str(refused.value).startswith("line 11 is the team's note")


def test_s357s_plain_revise_with_no_act_lands_as_on_the_parent(db):
    out = _rule(db, "On line 11, use the normal test runner", "revise")
    assert out["per_item"]["l_9"] == "revise"


def test_an_act_on_words_he_did_not_say_is_refused(db):
    with pytest.raises(ValueError, match="his words do not hold it"):
        _rule(db, "Line 11 is fine.",
              _act("rewrite", "On line 11, use the normal test runner"))
