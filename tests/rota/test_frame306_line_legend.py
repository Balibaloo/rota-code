"""
Frame 306, W-A of night 165: a line legend beside his words.

His page line numbers reached seats that never saw the page. s132 woke on
the repair of c1, got all three sentences of r_ee6e30a55d and wrote
"Delete lines 5 and 6" into c1. s359 read "remove both lines" of
r_39fbc7b24e as docstring lines and cut 17 of them. `principal.land`
records the page order at his reply as `order:<reply id>`. The wakes now
read that order and name each line his words name.
"""
from __future__ import annotations

import json

from rota.core.db import init_db
from rota.core.predicates import Wake
from rota.core.runner import (CONTESTS_KEY, _contest_block, build_prompt,
                              push_working_set)
from rota.core.sandbox import build
from rota.roles import prompts

# --- night 165, walk 1: s132 and r_ee6e30a55d ----------------------------------

ITEM_A = "get_app_dir_windows"
ORDER_M37 = [ITEM_A, "c1", "c2", "c3", "c4", "c6", "c8", "bg_1"]
TEXTS_M37 = {
    "c1": ("When get_app_dir is invoked on Windows and the APPDATA environment "
           "variable is not set, it must return a path under the user's AppData "
           "Roaming folder."),
    "c2": ("When get_app_dir is invoked on Windows and the LOCALAPPDATA "
           "environment variable is not set, it must return a path under the "
           "user's AppData Local folder."),
    "c3": ("When get_app_dir is invoked on Windows and both APPDATA and "
           "LOCALAPPDATA are not set, it must fall back to the user's home "
           "folder."),
    "c4": ("When get_app_dir is invoked on Windows and APPDATA is set, it must "
           "return a path under the APPDATA folder regardless of roaming "
           "preference."),
    "c6": ("When get_app_dir is invoked on Windows and APPDATA is set but "
           "LOCALAPPDATA is not, it must return a path under the APPDATA "
           "folder."),
}
S1_M37 = ("Change line 2 so it applies only when the roaming flag is True, and "
          "change line 3 so it applies only when the roaming flag is False.")
S2_M37 = ("Delete line 4, because an unset variable should always fall back to "
          "AppData Roaming or AppData Local under the home folder and never to "
          "the bare home folder.")
S3_M37 = ("Delete lines 5 and 6, because the roaming flag decides which folder "
          "to use and line 7 already says that.")
WORDS_M37 = f"{S1_M37} {S2_M37} {S3_M37}"


def _seed_m37(tmp_path):
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES (?, 'AppData folders on Windows', 'in_scope', "
               "'approved', 1, 1)", (ITEM_A,))
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_1', ?, "
               "'AppData folders')", (ITEM_A,))
    for cid, text in TEXTS_M37.items():
        db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                   "(?, 'tk_1', ?)", (cid, text))
    per_item = {r: "contest" for r in TEXTS_M37}
    per_item.update({ITEM_A: "approve", "c8": "approve", "bg_1": "approve"})
    for mid, verb in (("m35", "present"), ("m37", "reply")):
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                   "verb, body_refs, seq) VALUES (?, 'm35', 'liaison', "
                   "'principal', ?, ?, 1)", (mid, verb, json.dumps(ORDER_M37)))
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, "
               "status, texts) VALUES ('r_ee6e30a55d', 'm35', 'm37', ?, ?, "
               "'landed', ?)", (json.dumps(per_item), WORDS_M37,
                                json.dumps(TEXTS_M37)))
    db.execute("INSERT INTO config (key, value) VALUES ('order:m37', ?)",
               (json.dumps(ORDER_M37),))
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m60', 'm60', 'tester', "
               "'terminologist', 'question', ?, 2, 'unresolved')",
               (json.dumps(["c1"]),))
    db.commit()
    return db


def _repair_prompt(db) -> str:
    sb = build("terminologist", db, mode="criterion_repair",
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    wake = Wake("terminologist", "tick:criterion_repair", refs=("m60",))
    _system, user = build_prompt("terminologist", sb, wake, {},
                                 "MODE: criterion_repair")
    return user


def test_s132_repair_wake_quotes_the_line_2_sentence_with_its_legend(tmp_path):
    """s132 woke for c1 and copied lines 5 and 6 into c1. The wake now holds
    the sentence on line 2, and the legend names line 2 as c1."""
    user = _repair_prompt(_seed_m37(tmp_path))
    assert (f"The principal's last word on this criterion, c1 "
            f"(ruling r_ee6e30a55d, contest):\n{S1_M37}\n") in user
    assert f"On his page, line 2 was c1: {TEXTS_M37['c1']}" in user
    # The kept sentence also names line 3, so the seat learns it is c2.
    assert f"On his page, line 3 was c2: {TEXTS_M37['c2']}" in user
    assert "Write the behaviour his words ask for. His line numbers name " \
           "lines of his page, listed above." in user
    assert "Write the criterion in the principal's words." not in user
    for gone in (S2_M37, S3_M37, "lines 5 and 6", "line 4 was",
                 "line 5 was", "line 6 was", "line 7 was"):
        assert gone not in user, gone


# --- night 165, walk 3: s359 and r_39fbc7b24e -----------------------------------

ITEM_C = "format_filename_docstring_example"
CRIT_1 = "crit_1_format_shorten_true"
CRIT_2 = "crit_2_format_invalid_bytes"
CRIT_3 = "crit_3_format_default_full_path"
ORDER_M201 = [ITEM_C, CRIT_1, CRIT_2, CRIT_3, "bg_3"]
TEXT_1 = ("When shorten=True, format_filename returns only the basename of "
          "the path.")
TEXTS_M201 = {
    CRIT_2: ("format_filename replaces invalid bytes or surrogate escapes with "
             "the replacement character."),
    CRIT_3: ("When shorten=False (default), format_filename returns the full "
             "path string."),
}
WORDS_M201 = ("Lines 3 and 4 aren't part of what I asked for. This change only "
              "adds the one example to the docstring and the code stays the "
              "same, so please remove both lines. Lines 1, 2 and 5 are fine.")
WORDS_NO_LINE = ("These two aren't part of what I asked for. This change only "
                 "adds the one example to the docstring.")


def _seed_m201(tmp_path, words: str = WORDS_M201, order: bool = True):
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES (?, 'Add an example to the docstring of "
               "format_filename', 'in_scope', 'approved', 1, 1)", (ITEM_C,))
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('bg_3', ?, "
               "'running')", (ITEM_C,))
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_1', ?, "
               "'the docstring example')", (ITEM_C,))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
               "('bg_3', 'tk_1')")
    for cid, text in ((CRIT_1, TEXT_1), *TEXTS_M201.items()):
        db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                   "(?, 'tk_1', ?)", (cid, text))
    per_item = {ITEM_C: "approve", CRIT_1: "approve", CRIT_2: "contest",
                CRIT_3: "contest", "bg_3": "approve"}
    for mid, verb in (("m200", "present"), ("m201", "reply")):
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                   "verb, body_refs, seq) VALUES (?, 'm200', 'liaison', "
                   "'principal', ?, ?, 1)", (mid, verb, json.dumps(ORDER_M201)))
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, "
               "status, texts) VALUES ('r_39fbc7b24e', 'm200', 'm201', ?, ?, "
               "'landed', ?)", (json.dumps(per_item), words,
                                json.dumps(TEXTS_M201)))
    if order:
        db.execute("INSERT INTO config (key, value) VALUES ('order:m201', ?)",
                   (json.dumps(ORDER_M201),))
    db.commit()
    return db


def _developer_block(db) -> str:
    sb = build("developer", db, batch_id="bg_3", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    pushed = push_working_set("developer", sb,
                              Wake("developer", "tick:batch_start",
                                   refs=("bg_3",)))
    return pushed[CONTESTS_KEY]


def test_s359_developer_block_names_lines_3_and_4_as_crit_2_and_crit_3(tmp_path):
    """s359 read "remove both lines" as two docstring lines. The block now
    says which criteria lines 3 and 4 were, under his verbatim words."""
    block = _developer_block(_seed_m201(tmp_path))
    assert f"He said: {WORDS_M201}\n" in block
    assert f"On his page, line 3 was {CRIT_2}: {TEXTS_M201[CRIT_2]}" in block
    assert f"On his page, line 4 was {CRIT_3}: {TEXTS_M201[CRIT_3]}" in block
    assert f"On his page, line 2 was {CRIT_1}: {TEXT_1}" in block
    assert block.index("line 3 was") > block.index("He said:")


def test_a_check_line_is_named_as_the_check_of_its_criterion(tmp_path):
    """A check line holds a test id in the page order. His "line 4" there
    means the test of the criterion above it."""
    db = _seed_m201(tmp_path, words="Line 4 is wrong. Drop it.", order=False)
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('t_2', 'bg_3', ?, 'tests/test_x.py', 'def test(): pass')",
               (CRIT_2,))
    db.execute("INSERT INTO config (key, value) VALUES ('order:m201', ?)",
               (json.dumps([ITEM_C, CRIT_1, CRIT_2, "t_2", CRIT_3]),))
    db.commit()
    block = _contest_block(db, [{"id": CRIT_2}])
    assert block.endswith(f"On his page, line 4 was the check of {CRIT_2}.")


# The block of 03f6e900 for a ruling that names no line, with the page
# order recorded. A legend there would make every recorded case stale.
BLOCK_NO_LINE_03F6E900 = (
    b"ruling r_39fbc7b24e:\n"
    b"He contested crit_2_format_invalid_bytes, "
    b"crit_3_format_default_full_path.\n"
    b"crit_2_format_invalid_bytes: He contested this text: format_filename "
    b"replaces invalid bytes or surrogate escapes with the replacement "
    b"character.\n"
    b"crit_3_format_default_full_path: He contested this text: When "
    b"shorten=False (default), format_filename returns the full path string.\n"
    b"He said: These two aren't part of what I asked for. This change only "
    b"adds the one example to the docstring.")


def test_a_ruling_with_no_line_number_keeps_the_block_of_03f6e900(tmp_path):
    block = _developer_block(_seed_m201(tmp_path, words=WORDS_NO_LINE))
    assert block.encode("utf-8") == BLOCK_NO_LINE_03F6E900
    assert "On his page" not in block


def test_no_recorded_order_gives_no_legend(tmp_path):
    """A database from before frame 272 holds no order. Today's render can
    differ from his page, so the block names no line."""
    block = _developer_block(_seed_m201(tmp_path, order=False))
    assert "On his page" not in block
    assert block.endswith(f"He said: {WORDS_M201}")
