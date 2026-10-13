"""Frames 226 and 227: the criterion repair keeps the principal's words.

Night 144, walk 3, the rota workflow (`plans/night144-read.md`, sections
1.3, 1.4 and 8). The principal contested `ver_opt_show_py` with ruling
r_c4bf70291d. s537 respecified it in his words. s546 then woke on the
Tester's question m379 with no word of the ruling, and put back the
`--show-python` flag he had contested. Later relays sent the contested
sentence back, and the door answered `unchanged` with a note that did
not name his contest. The texts below are the night's.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.predicates import Wake
from rota.core.runner import build_prompt
from rota.core.sandbox import build
from rota.roles import prompts

from tests.rota.test_park_page import (  # noqa: F401
    ITEM_132, _landing, _liaison_presents, _reply, n132)

CID = "ver_opt_show_py"
SURFACE = "src/click/decorators.py::version_option"
# Version 14, the text on page m374 when the principal contested line 2.
V14 = ("The `version_option` callable appends the running Python version "
       "string (major.minor.micro) to the output message when invoked with "
       "the `--show-python` flag.")
# Version 15, s537's respecify on the relay m378.
V15 = ("The `version_option` callable appends the running Python version "
       "string (major.minor.micro) to the output message when invoked with "
       "the `show_python` parameter set to True.")
# Version 16, s546's respecify on `tick:criterion_repair`, and s583's call.
V16 = ("The command decorated with `version_option` must be invoked via "
       "`CliRunner` with the flag that enables Python version display (e.g., "
       "`--show-python`). The resulting output must contain the running "
       "Python version string formatted as major.minor.micro.")
# r_c4bf70291d, the reply to page m374.
WORDS_374 = ("Line 2 is wrong because it treats show_python as a new "
             "command-line option that users type. I asked for a parameter "
             "that the developer passes to version_option. When the developer "
             "sets it, the normal version output adds the Python version as "
             "major.minor.micro.")
# r_a9d56cfc45, the reply to page m403, which the relay m407 carried to s583.
WORDS_403 = ("Line 2 is still wrong because show_python is a setting the "
             "developer passes to the decorator, so the test should call the "
             "normal version flag and expect the Python version at the end of "
             "the output. Lines 6 and 9 make the same mistake about a separate "
             "flag, and line 5 is about the first change and does not belong "
             "on this page.")


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('version_option_show_python', 'Give "
                 "version_option a show_python parameter', 'in_scope', "
                 "'approved', 1, 1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk_1', 'version_option_show_python', 'show_python on "
                 "version_option')")
    conn.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) VALUES "
                 "(?, 'symbol', 'function')", (SURFACE,))
    conn.commit()
    return conn


def _criterion(conn, text: str) -> None:
    conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                 "VALUES (?, 'tk_1', ?, ?)", (CID, text, json.dumps([SURFACE])))
    conn.commit()


def _ruling(conn, rid: str, ask: str, verdict: str, words: str,
            contested: str | None) -> None:
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                 "verb, body_refs, seq) VALUES (?, ?, 'liaison', 'principal', "
                 "'present', ?, 1)", (ask, ask, json.dumps([CID])))
    texts = {CID: contested} if contested is not None else {}
    conn.execute("INSERT INTO rulings (id, ask_id, per_item, words, status, "
                 "texts) VALUES (?, ?, ?, ?, 'landed', ?)",
                 (rid, ask, json.dumps({CID: verdict}), words, json.dumps(texts)))
    conn.commit()


def _respecify(conn, text: str) -> dict:
    sb = build("terminologist", conn, mode="criterion_repair",
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    return sb.call("criteria.respecify", id=CID, text=text,
                   surface_refs=[SURFACE])


# --- frame 226, the door ----------------------------------------------------

def test_a_repair_that_puts_back_a_contested_flag_is_refused(db):
    """s546's call: version 15 is current, and version 14 is the text the
    principal contested. The flag `--show-python` comes back."""
    _criterion(db, V15)
    _ruling(db, "r_c4bf70291d", "m374", "contest", WORDS_374, V14)
    with pytest.raises(ValueError) as refused:
        _respecify(db, V16)
    said = str(refused.value)
    assert "--show-python" in said
    assert WORDS_374 in said


def test_a_repair_that_changes_other_words_is_admitted(db):
    """The same contest, and a rewrite that keeps the flag out."""
    _criterion(db, V15)
    _ruling(db, "r_c4bf70291d", "m374", "contest", WORDS_374, V14)
    out = _respecify(db, "The command decorated with `version_option` and "
                         "`show_python=True` prints the running Python version "
                         "as major.minor.micro at the end of the normal "
                         "version message.")
    assert out["respecified"]


def test_any_repair_is_admitted_when_no_ruling_contested_the_criterion(db):
    """No ruling names the criterion, so s546's text lands as today."""
    _criterion(db, V15)
    assert _respecify(db, V16)["respecified"]


# --- frame 227, the silent unchanged note --------------------------------------

def test_the_contested_sentence_sent_back_is_refused(db):
    """s583's call on the relay m407: version 16 is current, the principal
    contested version 16 on page m403, and the call sends version 16."""
    _criterion(db, V16)
    _ruling(db, "r_a9d56cfc45", "m403", "contest", WORDS_403, V16)
    with pytest.raises(ValueError) as refused:
        _respecify(db, V16)
    said = str(refused.value)
    assert "the principal contested these words" in said
    assert WORDS_403 in said
    assert "Write what he asked for" in said


def test_the_same_words_with_no_contest_keep_the_unchanged_note(db):
    _criterion(db, V16)
    out = _respecify(db, V16)
    assert out["unchanged"]
    assert "those are the criterion's own words" in out["note"]


# --- frame 226, the wake ----------------------------------------------------

def test_the_repair_wake_carries_the_principals_last_word(db):
    """s546's wake: the Tester's question m379 names the criterion, and the
    prompt now quotes the ruling r_c4bf70291d word for word."""
    _criterion(db, V15)
    _ruling(db, "r_c4bf70291d", "m374", "contest", WORDS_374, V14)
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status, unresolved_note) VALUES ('m379', "
               "'m379', 'tester', 'terminologist', 'question', ?, 2, "
               "'unresolved', 'the answer did not change the criterion; "
               "encoding it still parrots')", (json.dumps([CID]),))
    db.commit()
    sb = build("terminologist", db, mode="criterion_repair",
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    wake = Wake("terminologist", "tick:criterion_repair", refs=("m379",),
                detail="the answer did not change the criterion; encoding it "
                       "still parrots")
    _system, user = build_prompt("terminologist", sb, wake, {},
                                 "MODE: criterion_repair")
    assert (f"The principal's last word on this criterion, {CID} "
            f"(ruling r_c4bf70291d, contest):\n{WORDS_374}") in user
    assert "Do not send the sentence he contested." in user


def test_a_repair_wake_with_no_ruling_keeps_todays_prompt(db):
    _criterion(db, V15)
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m379', 'm379', 'tester', "
               "'terminologist', 'question', ?, 2, 'unresolved')",
               (json.dumps([CID]),))
    db.commit()
    sb = build("terminologist", db, mode="criterion_repair",
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    wake = Wake("terminologist", "tick:criterion_repair", refs=("m379",))
    _system, user = build_prompt("terminologist", sb, wake, {},
                                 "MODE: criterion_repair")
    assert "last word" not in user


# --- frame 226, the store -----------------------------------------------------

def test_a_contest_of_a_criterion_line_keeps_the_text_it_contested(n132):  # noqa: F811
    """The ruling keeps the text the principal read, because a criterion
    keeps no history. Night 132's page, line 3 is `cr_2`."""
    mid = _liaison_presents(n132, ITEM_132)
    reply = _reply(n132, mid, "line 3 is wrong: it must not hang")
    ruling = {str(n): "approve" for n in range(1, 8)}
    ruling["3"] = "contest"
    text = n132.execute("SELECT text FROM criteria WHERE id = "
                        "'cr_2_confirm_eof_behavior'").fetchone()["text"]
    out = _landing(n132, reply, f"TOOL: rulings.rule(rulings={json.dumps(ruling)}, "
                                "words='line 3 is wrong: it must not hang')")
    assert out.committed, out.errors
    (row,) = n132.execute("SELECT texts FROM rulings WHERE ask_id = ?",
                          (mid,)).fetchall()
    assert json.loads(row["texts"]) == {"cr_2_confirm_eof_behavior": text}
