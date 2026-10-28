"""Frame 306, pass 1: a note about a check goes to the Tester, not into the
criterion.

Night 160, bg_2 (`plans/frame306-provenance.md`, section 2). His m76 faulted
only the checks of lines 3 and 4. s195 wrote his note as the text of cr_2
and cr_3, "Line 3's check must ...", and the door admitted both. s255 woke
on the relay m117 for his m115 and landed two more notes in turn 4. Roman's
ruling of 2026-10-08, point 2: the Tester rewrites the test from the ruled
words. The rows below are the night's, copied from
`.rota/clickI_night160.db` on 2026-10-24, so the tests run in a checkout
without the run's database.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import backfill_ruled_refs, init_db
from rota.testkit.fixtures import seed_acts
from rota.core.sandbox import build
from rota.roles import api, prompts
from rota.testkit.fixtures import seed_verdict

ITEM = "confirm_default_on_eof"
TICKET = "tk_1_confirm_default_on_eof"
CR1 = "cr_1_confirm_default_on_eof"
CR2 = "cr_2_confirm_default_on_eof"
CR3 = "cr_3_confirm_default_on_eof"
CONFIRM = "src/click/termui.py::confirm"
PAGE = [ITEM, CR1, CR2, CR3, "bg_2"]
PER_ITEM = {ITEM: "approve", CR1: "approve", CR2: "contest", CR3: "contest",
            "bg_2": "approve"}
VERDICT = {CR2: "contest", CR3: "contest"}

# r_42118c7554 on page m75: the texts he contested, and his words of m76.
M76_TEXTS = {
    CR2: "When 'default_on_eof' is True and stdin is closed, confirm() must "
         "not attempt to read further or wait for input; it immediately "
         "returns the default.",
    CR3: "The 'default_on_eof' flag must be documented in the help text of "
         "confirm() to indicate its purpose and effect on EOF behavior.",
}
M76 = ("I don't want to give up on this change, so please fix it and try "
       "again. Line 4's check only looks at the signature, but it should check "
       "that confirm's docstring explains the flag. Line 3's check should also "
       "close stdin first, because it doesn't show that confirm returns the "
       "default at end of input without waiting.")
# s195's two calls, `receipts` cr_2 v6 and cr_3 v7.
S195_CR2 = ("Line 3's check must close stdin first to show that confirm() "
            "returns the default at end of input without waiting.")
S195_CR3 = ("Line 4's check must verify that confirm()'s docstring explains the "
            "'default_on_eof' flag and its effect on EOF behavior.")

# r_44b442e2a3 on page m114: the texts he contested, and his words of m115.
M115_TEXTS = {
    CR2: "Line 3's check must give confirm an empty, closed input before "
         "calling it to show that confirm() returns the default at end of "
         "input without waiting. Its text should also say again that when the "
         "flag is on and stdin is closed, confirm returns the default right "
         "away without waiting for input.",
    CR3: "Line 4's check must verify that confirm()'s docstring explains the "
         "'default_on_eof' flag and its effect on EOF behavior, specifically "
         "that with the flag on and stdin closed, confirm returns the default "
         "right away without waiting.",
}
M115 = ("Line 3 is still wrong: its text is my note pasted in again, when it "
        "should just say that with the flag on and stdin closed, confirm "
        "returns the default right away without waiting. Its check still never "
        "gives confirm an empty, closed input before the call, and it should "
        "pass a default of True so we can tell the default really came back. "
        "Line 4's check only looks for the flag's name in the docstring, so it "
        "doesn't show that the docstring explains what happens at end of "
        "input.")
# s255's turn 4 calls, which landed as cr_2 v13 and cr_3 v14.
S255_CR2 = ("Line 3's check must close stdin first to give confirm an empty, "
            "closed input before calling it. Its text should say that with the "
            "flag on and stdin closed, confirm returns the default right away "
            "without waiting for input.")
S255_CR3 = ("Line 4's check must verify that confirm()'s docstring explains "
            "what happens at end of input, specifically that with the flag on "
            "and stdin closed, confirm returns the default right away without "
            "waiting.")
# The provenance's behaviour text, section 5.
BEHAVIOUR = ("With default_on_eof=True and stdin closed, confirm() returns the "
             "default without waiting for input.")

ROUTE = "msg.answer_tester"


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES (?, 'let confirm() take a default_on_eof "
                 "flag', 'in_scope', 'approved', 1, 1)", (ITEM,))
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, ?, "
                 "'let confirm() take a default_on_eof flag: when stdin is "
                 "closed it returns the default instead of aborting')",
                 (TICKET, ITEM))
    conn.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) VALUES "
                 "(?, 'symbol', 'function')", (CONFIRM,))
    conn.execute("INSERT INTO batches (id, item_id, head_commit, status) "
                 "VALUES ('bg_2', ?, 'f791bcbf', 'running')", (ITEM,))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_2', ?)", (TICKET,))
    conn.commit()
    return conn


def _message(conn, mid, cause, thread, sender, to, verb, refs, seq, text=None):
    conn.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
                 "to_role, verb, body_refs, body_text, seq) VALUES "
                 "(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 (mid, cause, thread, sender, to, verb, json.dumps(refs), text,
                  seq))


def _ruled(conn, rid, page, reply, verdict, relay, words, texts, seq, acts):
    """A page, his reply, the verdict, the ruling and the relay, with the
    criteria as they stood when he ruled."""
    for cid, text in ((CR1, "confirm() takes a default_on_eof flag."),
                      (CR2, texts[CR2]), (CR3, texts[CR3])):
        conn.execute("INSERT OR REPLACE INTO criteria (id, ticket_id, text, "
                     "surface_refs, version) VALUES (?, ?, ?, ?, 2)",
                     (cid, TICKET, text, json.dumps([CONFIRM])))
    _message(conn, page, None, page, "liaison", "principal", "present", PAGE,
             seq)
    _message(conn, reply, page, page, "principal", "liaison", "converse",
             PAGE, seq + 1, words)
    _message(conn, verdict, page, page, "principal", "liaison", "verdict",
             [CR2, CR3], seq + 2)
    _message(conn, relay, verdict, page, "liaison", "terminologist", "relay",
             [CR2, CR3], seq + 3)
    seed_verdict(conn, verdict, json.dumps(VERDICT))
    conn.execute("INSERT INTO config (key, value) VALUES (?, ?)",
                 (f"order:{reply}", json.dumps(PAGE)))
    conn.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, "
                 "status, verdict_id, texts) VALUES (?, ?, ?, ?, ?, 'landed', "
                 "?, ?)", (rid, page, reply, json.dumps(PER_ITEM), words,
                           verdict, json.dumps(texts)))
    backfill_ruled_refs(conn)
    # The Liaison's reading of his reply as the object form writes it: a
    # fault of the check alone keeps the words (the seam design, pass 4).
    seed_acts(conn, rid, acts)


KEEP = {"act": "keep", "target_kind": "check"}


def _s195(conn):
    _ruled(conn, "r_42118c7554", "m75", "m76", "m77", "m78", M76, M76_TEXTS,
           78, {CR2: KEEP, CR3: KEEP})
    return _seat(conn, "s195", "m78")


def _s255(conn):
    _ruled(conn, "r_44b442e2a3", "m114", "m115", "m116", "m117", M115,
           M115_TEXTS, 117, {CR2: {"act": "rewrite", "target_kind": "row"},
                             CR3: KEEP})
    return _seat(conn, "s255", "m117")


def _seat(conn, sid, trigger):
    sb = build("terminologist", conn, mode="criterion_repair", session_id=sid,
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    sb.ctx.trigger = trigger
    sb.ctx.wake_kind = "message"
    return sb


def _refused(sb, cid, text, term_refs):
    with pytest.raises(ValueError) as refused:
        sb.call("criteria.respecify", id=cid, text=text, term_refs=term_refs,
                surface_refs=[CONFIRM])
    assert not [w for w in sb.ctx.writes if w[0] == "criteria"]
    return str(refused.value)


# --- repair 1: a text that names a page line or a check ----------------------

@pytest.mark.parametrize("text", [S195_CR2, S195_CR3, S255_CR2, S255_CR3])
def test_a_note_about_a_line_check_is_not_a_behaviour(text):
    assert api._about_the_tests(text), text


def test_s195_notes_are_refused_with_the_tester_route_by_the_text_door(db):
    """The text door alone: no ruling is on file, so repair 2 is silent."""
    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs, "
               "version) VALUES (?, ?, ?, ?, 2)",
               (CR2, TICKET, M76_TEXTS[CR2], json.dumps([CONFIRM])))
    db.commit()
    # No wake: the sandbox's own mode names the tools it holds.
    sb = build("terminologist", db, mode="criterion_repair", session_id="s195",
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    said = _refused(sb, CR2, S195_CR2, ["line"])
    assert "names a page line or a check" in said, said
    assert ROUTE in said, said


def test_s255_cr_2_note_is_refused_by_the_text_door(db):
    """m115 says "Line 3 is still wrong", so cr_2's ruling asks new words.
    The note-shaped text then meets the text door."""
    sb = _s255(db)
    assert not api.ruling_asks_no_new_words(sb.ctx, CR2)
    said = _refused(sb, CR2, S255_CR2, ["default_on_eof"])
    assert "names a page line or a check" in said, said
    assert ROUTE in said, said


def test_a_text_that_opens_with_the_tests_keeps_db3b0944s_refusal():
    said = api._about_the_tests_refusal(
        None, "Unit tests must validate the script's behaviour", "Rewrite it.")
    assert "names the Tester's job" in said, said


@pytest.mark.parametrize("text", [
    BEHAVIOUR,
    # night 158's cr_2 "contain" shape (frame 306, first edition).
    'The output of show_python must contain the word "Python", followed by a '
    'space, then the version string in major.minor.micro format.',
    "Line 3 of the output shows the default.",
    "Run the command, then check the printed output ends with True.",
    "When default_on_eof is True and stdin is closed (simulated by empty "
    "input in tests), confirm() returns the default.",
])
def test_a_behaviour_text_passes_the_text_door(text):
    assert not api._about_the_tests(text), text


# --- repair 2: a ruling that faults only the check refuses any new text ------

@pytest.mark.parametrize("cid,text", [(CR2, S195_CR2), (CR3, S195_CR3)])
def test_s195_calls_are_refused_with_his_m76_words(db, cid, text):
    """m76 faults only the checks of lines 3 and 4. The door says that the
    criterion stands and routes his words to the Tester."""
    sb = _s195(db)
    said = _refused(sb, cid, text, ["line"])
    assert "The criterion stands" in said, said
    assert repr(M76) in said, said
    assert ROUTE in said, said


def test_s195_behaviour_text_under_a_check_ruling_is_refused_too(db):
    sb = _s195(db)
    said = _refused(sb, CR2, BEHAVIOUR, ["default_on_eof"])
    assert "a new text does not land" in said, said
    assert ROUTE in said, said


def test_s255_cr_3_call_is_refused_with_his_m115_words(db):
    sb = _s255(db)
    said = _refused(sb, CR3, S255_CR3, ["default_on_eof"])
    assert "The criterion stands" in said, said
    assert repr(M115) in said, said
    assert ROUTE in said, said


def test_the_refusal_counts_as_landed_for_the_answer(db):
    """The answer door reads `criterion_stands`, so the Tester route that
    the refusal names is open."""
    sb = _s195(db)
    _refused(sb, CR2, S195_CR2, ["line"])
    _refused(sb, CR3, S195_CR3, ["line"])
    out = sb.call("msg.answer_tester", refs=[CR2, CR3], round_no=0)
    assert out["to"] == "tester", out


def test_after_the_answer_the_refusal_names_no_answer_call(db):
    sb = _s195(db)
    _refused(sb, CR2, S195_CR2, ["line"])
    _refused(sb, CR3, S195_CR3, ["line"])
    sb.call("msg.answer_tester", refs=[CR2, CR3], round_no=0)
    said = _refused(sb, CR2, BEHAVIOUR, ["default_on_eof"])
    assert ROUTE not in said, said
    assert f"your work on {CR2} is done" in said, said


# --- controls -----------------------------------------------------------------

def test_a_behaviour_text_under_a_ruling_that_asks_new_words_lands(db):
    sb = _s255(db)
    out = sb.call("criteria.respecify", id=CR2, text=BEHAVIOUR,
                  term_refs=["default_on_eof"], surface_refs=[CONFIRM])
    assert out.get("respecified"), out


def test_the_rows_own_words_under_a_check_ruling_keep_the_same_words_branch(db):
    """The row's own note-shaped words write nothing. The same-words branch
    answers them, so the text door does not refuse them first."""
    sb = _s255(db)
    said = _refused(sb, CR3, M115_TEXTS[CR3], ["default_on_eof"])
    assert "The criterion stands" in said, said
    assert "rewrite the text" not in said, said


# --- pass 1b: the route exists in every mode that meets the refusal ----------

def _criteria_seat(conn):
    return build("terminologist", conn, mode="criteria",
                 allow=prompts.mode_tools("terminologist", "criteria"))


def test_the_criteria_mode_sends_the_note_after_the_behaviour_lands(db):
    """Review 1, finding 1: the criteria mode met the refusal and held no
    msg.answer_tester. The ruling of 2026-10-08, point 2, sends the note to
    the Tester."""
    sb = _criteria_seat(db)
    with pytest.raises(ValueError) as refused:
        sb.call("criteria.specify", id="cr_9", ticket_id=TICKET, text=S195_CR2,
                surface_refs=[CONFIRM])
    assert ROUTE in str(refused.value), str(refused.value)
    sb.call("criteria.specify", id="cr_9", ticket_id=TICKET, text=BEHAVIOUR,
            surface_refs=[CONFIRM])
    out = sb.call("msg.answer_tester", refs=["cr_9"], round_no=0)
    assert out["to"] == "tester", out


def _named_ops(said):
    import re
    return set(re.findall(r"\bmsg\.\w+|\bcriteria\.\w+", said))


def _refusals(db):
    """Each new refusal of frame 306, with the mode that meets it."""
    out = []
    sb = _criteria_seat(db)
    with pytest.raises(ValueError) as e:
        sb.call("criteria.specify", id="cr_9", ticket_id=TICKET, text=S195_CR3,
                surface_refs=[CONFIRM])
    out.append(("criteria", str(e.value)))
    sb = _s195(db)
    out.append(("criterion_repair",
                _refused(sb, CR2, S195_CR2, ["line"])))
    out.append(("criterion_repair",
                _refused(sb, CR2, M76_TEXTS[CR2], ["line"])))
    return out


def test_each_refusal_names_only_a_tool_its_mode_holds(db):
    """Frame 135's law, in the shape of frame 308's pass 1."""
    for mode, said in _refusals(db):
        held = set(prompts.mode_tools("terminologist", mode))
        assert _named_ops(said) <= held, (mode, said)


def test_a_mode_without_the_route_is_not_told_to_use_it(db, monkeypatch):
    monkeypatch.setattr(api, "_wake_mode_tools",
                        lambda ctx: ["criteria.specify"])
    sb = _criteria_seat(db)
    with pytest.raises(ValueError) as e:
        sb.call("criteria.specify", id="cr_9", ticket_id=TICKET, text=S195_CR3,
                surface_refs=[CONFIRM])
    assert ROUTE not in str(e.value), str(e.value)
    assert "Write the behaviour that the check must show" in str(e.value)
