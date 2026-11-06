"""Frame 362, the push of a ruling: a seat that acts on his ruling reads his
whole reply once, with a legend line for each page line it names.

Dry run 6b's s152 woke for b_1 after m27. Its start push held
`["Do not touch parameter.py or property.py.", "Line 2 is wrong."]`, the
row words, with no page and no line. Three Developers named property.py
and none opened string.py (`plans/f362-push-read-2026-11-06.md`, section 2).
The rows below are copied from the run databases that the read names.
"""
import json

from rota.core.db import backfill_ruled_refs, init_db
from rota.core import runner
from rota.core.runner import (RULED_KEY, START_RULED_KEY, _line_legend,
                              push_working_set)
from rota.core.sandbox import build
from rota.core.scheduler import Wake
from rota.roles import prompts
from rota.testkit.fixtures import seed_provenance

# Dry run 6b, `dry6b.db`.
ITEM6 = "folds_long_lines_in_icalendar"
ITEM6_TEXT = ("When icalendar writes a long line, fold it at a space where it can, "
              "so that a word is not split, and keep everything else as before.")
CRIT6 = {
    "c_1": "The serialized iCalendar output must fold lines at whitespace "
           "boundaries without splitting any word.",
    "c_2": "No line in the serialized output may contain a hyphenated word "
           "broken across two lines.",
    "c_3": "The folding behavior must not alter existing escape sequences or "
           "break them across lines.",
}
M27 = ("Line 2 is wrong. The fold is _foldline in src/icalendar/parser/string.py, "
       "and its tests are in src/icalendar/tests/test_icalendar.py. Do not touch "
       "parameter.py or property.py.")
M39 = ("Line 5 is wrong. The fold is _foldline in src/icalendar/parser/string.py, "
       "and its tests are in src/icalendar/tests/test_icalendar.py. Do not touch "
       "parameter.py or property.py.")
M40 = "Every content line that icalendar writes. Keep everything else as it is today."
NOT_THESE = "Do not touch parameter.py or property.py."
GUESS6 = ("The team's guess at the code this touches: src/icalendar/parser/property.py, "
          "src/icalendar/tests/prop/test_common_functionality.py, "
          "src/icalendar/tests/prop/test_crlf_in_values.py, "
          "src/icalendar/tests/rfc_7265_jcal/test_section_3_6_values.py. It might "
          "touch src/icalendar/parser/property.py::split_on_unescaped_comma, "
          "src/icalendar/parser/property.py::split_on_unescaped_semicolon.")
# (id, ask, reply, per_item, words, rows, order of the reply, code stamp of the ask)
# A row is (ref, line, verdict, act, words, source).
RULINGS6 = (
    ("r_m27", "m26", "m27",
     {ITEM6: "approve", f"guess:{ITEM6}": "contest", "l_50364e0e61": "approve"}, M27,
     ((ITEM6, 1, "approve", "add", NOT_THESE, "reading"),
      (f"guess:{ITEM6}", 2, "contest", "rewrite", "Line 2 is wrong.", "reading"),
      ("l_50364e0e61", 3, "approve", None, M27, "reading"),
      (ITEM6, 1, "approve", "add", NOT_THESE, "landed"),
      (f"guess:{ITEM6}", 2, "contest", "rewrite", "Line 2 is wrong.", "landed")),
     [ITEM6, f"guess:{ITEM6}", "l_50364e0e61", "reading:m5"],
     {f"guess:{ITEM6}": {"guess": [1, ""]}}),
    ("r_m39", "m31", "m39",
     {ITEM6: "approve", "c_1": "approve", "c_2": "approve", "c_3": "approve",
      "b_1": "contest"}, M39,
     ((ITEM6, 1, "approve", "add", NOT_THESE, "reading"),
      ("c_1", 2, "approve", None, M39, "reading"),
      ("c_2", 3, "approve", None, M39, "reading"),
      ("c_3", 4, "approve", None, M39, "reading"),
      ("b_1", 5, "contest", "rewrite", "Line 5 is wrong.", "reading"),
      ("b_1", 5, "contest", "rewrite", "Line 5 is wrong.", "landed")),
     [ITEM6, "c_1", "c_2", "c_3", "b_1", "reading:m5", "reading:m27"], None),
    ("r_m40_2", "m37", "m40", {"b_1": "revise"}, M40,
     (("b_1", None, "revise", "rewrite", M40, "reading"),), None, None),
    ("r_m41", "m38", "m41",
     {ITEM6: "approve", "c_1": "approve", "c_2": "approve", "c_3": "approve",
      "b_1": "contest"}, M39,
     ((ITEM6, 1, "approve", "add", NOT_THESE, "reading"),
      ("c_1", 2, "approve", None, M39, "reading"),
      ("c_2", 3, "approve", None, M39, "reading"),
      ("c_3", 4, "approve", None, M39, "reading"),
      ("b_1", 5, "contest", "rewrite", "Line 5 is wrong.", "reading"),
      ("b_1", 5, "contest", "rewrite", "Line 5 is wrong.", "landed")),
     [ITEM6, "c_1", "c_2", "c_3", "b_1", "reading:m5", "reading:m27"], None),
)
GUESSES6 = (
    ("src/icalendar/parser/property.py", "path"),
    ("src/icalendar/tests/prop/test_common_functionality.py", "path"),
    ("src/icalendar/tests/prop/test_crlf_in_values.py", "path"),
    ("src/icalendar/tests/rfc_7265_jcal/test_section_3_6_values.py", "path"),
    ("src/icalendar/parser/property.py::split_on_unescaped_comma", "symbol"),
    ("src/icalendar/parser/property.py::split_on_unescaped_semicolon", "symbol"),
)

# Dry run 4, `.rota/dry4.db`.
ITEM4 = "folds_long_lines"
CRIT4 = ("c1", "c2", "c3", "c4", "c5", "c7")
M50 = ("Only a line longer than the limit the code already uses is folded; a "
       "short line stays as it is.")
M51 = ("The content stays identical and only the fold is inserted, so a reader "
       "joins the lines back to the original.")
M58 = ("Line 8: the fold lives in src/icalendar/parser/string.py, in _foldline, "
       "and parameter.py and property.py are not it.")
PAGE4 = [ITEM4, *CRIT4, "bg_1", "reading:m35"]
ALL4 = {ITEM4: "approve", **{c: "approve" for c in CRIT4}, "bg_1": "approve",
        "reading:m35": "approve"}


def _rows4(words, verdicts, source="reading"):
    return tuple((ref, n, verdicts.get(ref, "approve"), None, words, source)
                 for n, ref in enumerate(PAGE4, 1) if ref in verdicts)


RULINGS4 = (
    ("r_m35", "m34", "m35",
     {ITEM4: "approve", f"guess:{ITEM4}": "approve", "l_1fc52314aa": "approve",
      "reading:m5": "approve"}, "ok",
     ((ITEM4, 1, "approve", None, "ok", "reading"),
      (f"guess:{ITEM4}", 2, "approve", None, "ok", "reading"),
      ("l_1fc52314aa", 3, "approve", None, "ok", "reading"),
      ("reading:m5", 4, "approve", None, "ok", "reading"),
      (ITEM4, 1, "approve", None, "ok", "landed")),
     [ITEM4, f"guess:{ITEM4}", "l_1fc52314aa", "reading:m5"],
     {f"guess:{ITEM4}": {"guess": [1, ""]}}),
    ("r_m49", "m40", "m49", ALL4, "ok", _rows4("ok", ALL4), PAGE4, None),
    ("r_m50_2", "m44", "m50", {"bg_1": "revise"}, M50,
     (("bg_1", None, "revise", None, M50, "reading"),), None, None),
    ("r_m51_2", "m46", "m51", {"bg_1": "approve"}, M51,
     (("bg_1", None, "approve", None, M51, "reading"),), None, None),
    ("r_m52", "m47", "m52", ALL4, "ok", _rows4("ok", ALL4), PAGE4, None),
    ("r_m58", "m57", "m58", {**{k: "approve" for k in (ITEM4, *CRIT4)}, "bg_1": "contest"},
     M58,
     tuple((ref, n, "approve", None, M58, "reading")
           for n, ref in enumerate(PAGE4[:7], 1))
     + (("bg_1", 8, "contest", "exclude", M58, "reading"),
        ("bg_1", 8, "contest", "exclude", M58, "landed")),
     [*PAGE4[:8], "reading:m52"], None),
)


def _seed(db, rulings, *, upto=None):
    """Land the rulings of the tuple, copied row by row, up to `upto`."""
    for rid, ask, reply, per_item, words, rows, order, stamp in rulings:
        for mid in (ask, reply):
            db.execute("INSERT OR IGNORE INTO messages (id, thread_id, from_role, "
                       "to_role, verb, seq) VALUES (?, 't1', 'liaison', "
                       "'principal', 'ask', ?)", (mid, int(mid[1:])))
        db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, status) "
                   "VALUES (?, ?, ?, ?, ?, 'landed')",
                   (rid, ask, reply, json.dumps(per_item), words))
        for n, (ref, line, verdict, act, said, source) in enumerate(rows):
            db.execute("INSERT INTO ruled_refs (id, ruling_id, ref, line, verdict, "
                       "act, words, source) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (f"rr_{rid}_{n}", rid, ref, line, verdict, act, said, source))
        if order is not None:
            db.execute("INSERT INTO config (key, value) VALUES (?, ?)",
                       (f"order:{reply}", json.dumps(order)))
        if stamp is not None:
            db.execute("INSERT INTO config (key, value) VALUES (?, ?)",
                       (f"code:{ask}", json.dumps(stamp)))
        if rid == upto:
            break
    db.commit()


def _change(db, item, text, crit, bid):
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES (?, ?, 'in_scope', 'approved', 1, 1)", (item, text))
    seed_provenance(db, "items", item, "decided")
    db.execute("INSERT INTO tickets (id, item_id, text, item_ver) VALUES "
               "('tk_1', ?, ?, 1)", (item, text))
    for cid, ctext in crit.items():
        db.execute("INSERT INTO criteria (id, ticket_id, text, version) VALUES "
                   "(?, 'tk_1', ?, 1)", (cid, ctext))
    db.execute("INSERT INTO batches (id, item_id, status) VALUES (?, ?, 'running')",
               (bid, item))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES (?, 'tk_1')", (bid,))


def _dry6b(tmp_path, upto=None):
    db = init_db(tmp_path / "rota.db")
    _change(db, ITEM6, ITEM6_TEXT, CRIT6, "b_1")
    for grain, kind in GUESSES6:
        db.execute("INSERT INTO touch_guesses (item_id, item_ver, ruling_id, grain, "
                   "grain_kind) VALUES (?, 1, '', ?, ?)", (ITEM6, grain, kind))
    _seed(db, RULINGS6, upto=upto)
    return db


def _start(db, bid):
    sb = build("developer", db, batch_id=bid, mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    return push_working_set("developer", sb,
                            Wake("developer", "tick:batch_start", refs=(bid,)))


def test_s152s_start_push_holds_his_reply_m27_and_the_legend_of_line_2(tmp_path):
    """Red on fe0dc136: the push held the row words of lines 1 and 2, 65
    characters, and not the sentence that names string.py."""
    db = _dry6b(tmp_path, upto="r_m27")
    assert _start(db, "b_1")[START_RULED_KEY] == (
        f'His answer m27 to page m26: "{M27}"\n'
        f"On his page, line 2 was {GUESS6}")


def test_s147_and_s148_item_pushes_hold_the_same_reply(tmp_path):
    """The slicing push of s147 and the criteria push of s148 held the same
    two row texts under the item key (the read, section 2)."""
    db = _dry6b(tmp_path, upto="r_m27")
    sb = build("terminologist", db, mode="criteria",
               allow=prompts.mode_tools("terminologist", "criteria"))
    pushed = push_working_set("terminologist", sb,
                              Wake("terminologist", "tick:criteria", refs=(ITEM6,)))
    assert M27 in pushed["the item"][RULED_KEY]
    assert f"On his page, line 2 was {GUESS6}" in pushed["the item"][RULED_KEY]


def test_s173s_start_push_holds_m40(tmp_path):
    """Red on fe0dc136: `RULED_CAP` kept three row texts, and r_m40_2 was
    not among them (the read, section 6)."""
    db = _dry6b(tmp_path)
    block = _start(db, "b_1")[START_RULED_KEY]
    assert f'His answer m40 to page m37: "{M40}"' in block
    # Each ruling once, oldest first, and none left out.
    heads = [line.split(":")[0] for line in block.split("\n")
             if line.startswith("His answer")]
    assert heads == ["His answer m27 to page m26", "His answer m39 to page m31",
                     "His answer m40 to page m37", "His answer m41 to page m38"]
    assert "older answer" not in block
    # A batch line keeps its id: its readers render today's touch set.
    assert "On his page, line 5 was b_1." in block


def test_dry4_s206s_start_push_holds_r_m50_2(tmp_path):
    """Red on fe0dc136: the cap cut r_m35, r_m49 and r_m50_2, and the "ok"
    of r_m52 took a place."""
    db = init_db(tmp_path / "rota.db")
    _change(db, ITEM4, ITEM6_TEXT, {c: f"criterion {c}" for c in CRIT4}, "bg_1")
    _seed(db, RULINGS4)
    block = _start(db, "bg_1")[START_RULED_KEY]
    assert M50 in block
    assert M51 in block and M58 in block


# Night 166, `clickI_night166.db`. The run database is behind the schema,
# so its rows come from the back-fill rule, as the read emulated them.
DOC_ITEM = "format_filename_example"
M69 = ("Line 2 is wrong: the change goes in the docstring of the function "
       "itself, not in a test file, and only the docstring changes while the "
       "code stays the same.")


def test_s185s_criteria_push_holds_the_code_stays_the_same_and_line_2(tmp_path):
    """Frame 322's case. Red on fe0dc136 for the legend: "Line 2" pointed
    at nothing, and line 2 was the guess at a test file."""
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES (?, 'With shorten set to True, the path a/b/c.txt shows as "
               "c.txt in the docstring of format_filename.', 'in_scope', "
               "'approved', 1, 1)", (DOC_ITEM,))
    seed_provenance(db, "items", DOC_ITEM, "decided")
    db.execute("INSERT INTO tickets (id, item_id, text, item_ver) VALUES "
               "('tk_1_doc', ?, 'the docstring example', 1)", (DOC_ITEM,))
    for mid, seq in (("m68", 68), ("m69", 69)):
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
                   "VALUES (?, 't1', 'liaison', 'principal', 'ask', ?)", (mid, seq))
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, status) "
               "VALUES ('r_1ec1beb146', 'm68', 'm69', ?, ?, 'landed')",
               (json.dumps({f"guess:{DOC_ITEM}": "contest", DOC_ITEM: "approve",
                            "l_bc0aded511": "approve"}), M69))
    db.execute("INSERT INTO config (key, value) VALUES ('order:m69', ?)",
               (json.dumps([DOC_ITEM, f"guess:{DOC_ITEM}", "l_bc0aded511"]),))
    db.execute("INSERT INTO config (key, value) VALUES ('code:m68', ?)",
               (json.dumps({f"guess:{DOC_ITEM}": {"guess": [1, ""]}}),))
    # The guess he saw, and the set that his ruling m70 wrote later.
    for ruling, grain, kind in (("", "tests/test_utils/test_format_filename.py", "path"),
                                ("m70", "src/click/utils.py", "path"),
                                ("m70", "src/click/utils.py::format_filename", "symbol")):
        db.execute("INSERT INTO touch_guesses (item_id, item_ver, ruling_id, grain, "
                   "grain_kind) VALUES (?, 1, ?, ?, ?)", (DOC_ITEM, ruling, grain, kind))
    backfill_ruled_refs(db)
    db.commit()
    sb = build("terminologist", db, mode="criteria",
               allow=prompts.mode_tools("terminologist", "criteria"))
    pushed = push_working_set("terminologist", sb,
                              Wake("terminologist", "tick:criteria", refs=(DOC_ITEM,)))
    assert pushed["the item"][RULED_KEY] == (
        f'His answer m69 to page m68: "{M69}"\n'
        "On his page, line 2 was The team's guess at the code this touches: "
        "tests/test_utils/test_format_filename.py.")


def test_the_legend_names_a_guess_line_by_the_text_he_saw(tmp_path):
    """The read, section 3: `_line_legend` gave `guess:<item>.` and no text."""
    db = _dry6b(tmp_path, upto="r_m27")
    assert _line_legend(db, "r_m27", M27) == [f"On his page, line 2 was {GUESS6}"]


NOTE6 = ("The software must fold long lines in iCalendar output at spaces to "
         "avoid splitting words, as per the ratified statement.")


def test_the_legend_names_a_team_note_by_its_text(tmp_path):
    """Line 3 of page m26 was the team note l_50364e0e61, under "Where you
    did not say, I assumed:". The legend reads its `default_taken`."""
    db = _dry6b(tmp_path, upto="r_m27")
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, kind, "
               "status, author) VALUES ('l_50364e0e61', ?, 'items', ?, 'default', "
               "'resolved', 'vision_keeper')", (ITEM6, NOTE6))
    assert _line_legend(db, "r_m27", "Line 3 is right.") == [
        f"On his page, line 3 was the team's assumption: {NOTE6}"]


# The budget. Each reply is about 1,000 characters, so two fit in
# `runner.RULED_CHARS` and three do not.
LONG = "Keep the fold at a space and keep each word whole on its line. " * 16


def _long_rulings(tmp_path, n, words=LONG):
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES ('it', 'the item', 'in_scope', 'approved', 1, 1)")
    seed_provenance(db, "items", "it", "decided")
    _seed(db, tuple(
        (f"r_{k}", f"m{2 * k}", f"m{2 * k + 1}", {"it": "contest"}, f"Answer {k}. {words}",
         (("it", None, "contest", None, f"Answer {k}. {words}", "reading"),), None, None)
        for k in range(1, n + 1)))
    return db


def test_a_window_over_the_budget_keeps_whole_rulings_the_newest(tmp_path):
    db = _long_rulings(tmp_path, 5)
    block = runner._ruled_block(db, ["it"])
    lines = block.split("\n")
    assert lines == [f'His answer m9 to page m8: "Answer 4. {LONG.strip()}"',
                     f'His answer m11 to page m10: "Answer 5. {LONG.strip()}"',
                     "This block does not show 3 older answers of the principal."]
    assert len(block) <= runner.RULED_CHARS


def test_a_window_inside_the_budget_shows_no_count_line(tmp_path):
    db = _long_rulings(tmp_path, 2)
    assert "older answer" not in runner._ruled_block(db, ["it"])


def test_the_newest_ruling_stays_whole_when_it_alone_is_over_the_budget(tmp_path):
    """No push stops quietly: a window with no word of his newest ruling is
    frame 312's fault again."""
    db = _long_rulings(tmp_path, 2, words=LONG * 4)
    lines = runner._ruled_block(db, ["it"]).split("\n")
    assert lines == [f'His answer m5 to page m4: "Answer 2. {(LONG * 4).strip()}"',
                     "This block does not show 1 older answer of the principal."]
