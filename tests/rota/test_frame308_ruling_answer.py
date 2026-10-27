"""Frame 308: the Terminologist's answer to a ruling relay carries every
ruled criterion.

Night 158 (`plans/frame304-s220-read.md`, sections 1 to 3). The principal's
ruling r_ce163d8060 marked cr_2 `revise` and cr_3 `contest`. The relay m101
woke s220 in mode `criterion_repair` with both. s220 answered with cr_3 alone
in turn 1, and the one-answer door of 2026-08-14 then refused every later
answer. cr_2's fix reached no seat. The rows below are the night's, copied
from `.rota/clickI_night158.db` on 2026-10-23, so the tests run in a checkout
without the run's database.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import backfill_ruled_refs, init_db
from rota.core.sandbox import build
from rota.roles import prompts

ITEM = "confirm_default_on_eof"
TICKET = "tk_1_confirm_default_on_eof"
CR1 = "cr_1_confirm_default_on_eof"
CR2 = "cr_2_confirm_default_on_eof"
CR3 = "cr_3_confirm_default_on_eof"
CONFIRM = "src/click/termui.py::confirm"

CR1_TEXT = ("confirm() has an optional default_on_eof argument that defaults to "
            "False. When True and stdin is closed, confirm() returns the "
            "provided default value instead of raising Abort.")
CR2_TEXT = ("When confirm() is called with default_on_eof=True and stdin is "
            "closed, it must attempt to read from stdin; if that read hits end "
            "of file, it returns the provided default value instead of raising "
            "an exception.")
CR3_TEXT = ("When confirm() returns the default value due to closed stdin "
            "(after attempting to read), it must not emit any prompt or error "
            "message to stdout.")
# m98, the principal's words of r_ce163d8060.
WORDS = ("Lines 1, 2, 3 and 6 to 8 are fine as written. Keep line 4, but fix "
         "its check so it fakes a closed input properly, because the failure "
         "comes from a broken test stub and not from the behaviour. Drop line "
         "5, because I never asked for the prompt to be hidden, so the prompt "
         "can show as usual before it falls back to the default.")
# `config` key `verdict:m99`.
VERDICT = {CR2: "revise", CR3: "contest", "command#root": "approve",
           "option#root": "approve", "parameter#root": "approve"}
PER_ITEM = {ITEM: "approve", f"guess:{ITEM}": "approve", CR1: "approve",
            CR2: "revise", CR3: "contest", "command#root": "approve",
            "option#root": "approve", "parameter#root": "approve"}
# The lines of the page m89 in the order m98 names them: 1 to 3 and 6 to 8
# are fine, line 4 is cr_2 and line 5 is cr_3.
PAGE = [ITEM, f"guess:{ITEM}", CR1, CR2, CR3, "command#root", "option#root",
        "parameter#root"]

ROUTE = "Send one msg.answer_tester with every ruled criterion in refs"
ONE_ANSWER = "you have already sent answer to tester"


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
    for cid, text, ver in ((CR1, CR1_TEXT, 3), (CR2, CR2_TEXT, 2),
                           (CR3, CR3_TEXT, 4)):
        conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs, "
                     "version) VALUES (?, ?, ?, ?, ?)",
                     (cid, TICKET, text, json.dumps([CONFIRM]), ver))
    conn.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) VALUES "
                 "(?, 'symbol', 'function')", (CONFIRM,))
    # bg_2 had its code at f791bcbf when s220 woke.
    conn.execute("INSERT INTO batches (id, item_id, head_commit, status) "
                 "VALUES ('bg_2', ?, 'f791bcbf', 'running')", (ITEM,))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_2', ?)", (TICKET,))
    conn.commit()
    return conn


def _message(conn, mid, cause, sender, to, verb, refs, seq, text=None):
    conn.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
                 "to_role, verb, body_refs, body_text, seq) VALUES "
                 "(?, ?, 'm89', ?, ?, ?, ?, ?, ?)",
                 (mid, cause, sender, to, verb, json.dumps(refs), text, seq))


def _night158_relay(conn) -> None:
    """The page m89, the reply m98, the verdict m99, the ruling, the relay m101."""
    _message(conn, "m89", None, "liaison", "principal", "present",
             [ITEM, CR1, CR2, CR3], 90)
    _message(conn, "m98", "m89", "principal", "liaison", "converse",
             [ITEM, CR1, CR2, CR3], 102, WORDS)
    _message(conn, "m99", "m89", "principal", "liaison", "verdict",
             [CR2, CR3, "command#root", "option#root", "parameter#root"], 103)
    _message(conn, "m101", "m99", "liaison", "terminologist", "relay",
             [CR2, CR3], 105)
    conn.execute("INSERT INTO config (key, value) VALUES ('verdict:m99', ?)",
                 (json.dumps(VERDICT),))
    # The page m89 as he saw it at m98, as `principal.land` records it since
    # frame 272. His words put cr_2 on line 4 and cr_3 on line 5.
    conn.execute("INSERT INTO config (key, value) VALUES ('order:m98', ?)",
                 (json.dumps(PAGE),))
    conn.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, "
                 "status, verdict_id, texts) VALUES ('r_ce163d8060', 'm89', "
                 "'m98', ?, ?, 'landed', 'm99', ?)",
                 (json.dumps(PER_ITEM), WORDS,
                  json.dumps({CR2: CR2_TEXT, CR3: CR3_TEXT})))
    backfill_ruled_refs(conn)
    conn.commit()


def _s220(conn, trigger="m101"):
    sb = build("terminologist", conn, mode="criterion_repair",
               session_id="s220",
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    sb.ctx.trigger = trigger
    sb.ctx.wake_kind = "message"
    return sb


def _answers(sb):
    return [m for m in sb.ctx.outbound
            if m["to_role"] == "tester" and m["verb"] == "answer"]


# m98's "Drop line 5" drops cr_3. No op of the Terminologist retires a
# criterion, and frame 192 owns the drop route, so cr_3's answer has no
# route here (frame 308, review 4, point 2).
DROPPED = f"The principal's ruling drops line 5, which is {CR3}"


def _cr3_out_of_the_relay(conn) -> None:
    """The relay rules cr_2 alone. A test of another door then gets an answer
    that lands, while frame 192 has no route for cr_3."""
    conn.execute("UPDATE messages SET body_refs = ? WHERE id = 'm101'",
                 (json.dumps([CR2]),))
    conn.execute("UPDATE config SET value = ? WHERE key = 'verdict:m99'",
                 (json.dumps({CR2: "revise"}),))
    conn.commit()


def test_s220_turn_1_answer_with_cr_3_alone_is_refused(db):
    """s220's turn 1, tool call seq 11: refs cr_3 alone. The ruling marks
    cr_2 `revise` too."""
    _night158_relay(db)
    sb = _s220(db)
    with pytest.raises(ValueError) as refused:
        sb.call("msg.answer_tester", refs=[CR3], round_no=0)
    said = str(refused.value)
    assert CR2 in said, said
    assert "ruling" in said, said
    # m98 drops cr_3's line, so the refusal names the drop and no call.
    assert DROPPED in said, said
    assert f"Do not rewrite {CR3}" in said, said
    assert "Respecify" not in said, said
    assert ROUTE not in said, said
    assert not _answers(sb)
    assert not [o for o in sb.ctx.offers if o.op == "msg.answer_tester"]
    for sentence in said.split(". "):
        assert len(sentence.split()) <= 20, sentence


def test_the_same_answer_with_cr_2_and_cr_3_names_the_drop_of_line_5(db):
    """The answer carries cr_3 as it stands, and m98 dropped its line. The
    refusal asks for no rewrite of cr_3 (review 4, point 2)."""
    _night158_relay(db)
    sb = _s220(db)
    with pytest.raises(ValueError) as refused:
        sb.call("msg.answer_tester", refs=[CR2, CR3], round_no=0)
    said = str(refused.value)
    assert DROPPED in said, said
    assert f"Do not rewrite {CR3}" in said, said
    assert "respecify" not in said.lower(), said
    assert not _answers(sb)


def test_a_session_with_no_ruling_relay_answers_one_criterion_as_today(db):
    """A Tester's question woke the session, and no ruling is on its chain."""
    _message(db, "m50", None, "tester", "terminologist", "question", [CR2], 50)
    db.commit()
    sb = _s220(db, trigger="m50")
    out = sb.call("msg.answer_tester", refs=[CR3], round_no=0)
    assert out["to"] == "tester", out
    assert len(_answers(sb)) == 1


def test_a_second_answer_after_the_first_lands_meets_the_one_answer_door(db):
    _night158_relay(db)
    _cr3_out_of_the_relay(db)
    sb = _s220(db)
    sb.call("msg.answer_tester", refs=[CR2, CR3], round_no=0)
    with pytest.raises(ValueError) as refused:
        sb.call("msg.answer_tester", refs=[CR3], round_no=0)
    assert ONE_ANSWER in str(refused.value)
    assert len(_answers(sb)) == 1


def _respecify_cr2(sb):
    """s220's turn 4 call, tool call seq 16: cr_2 with its own words."""
    with pytest.raises(ValueError) as refused:
        sb.call("criteria.respecify", id=CR2, text=CR2_TEXT,
                term_refs=["default_on_eof"], surface_refs=[CONFIRM])
    return str(refused.value)


def test_the_cr_2_refusal_before_the_answer_names_the_answer_route(db):
    """The door is open, so the text stays as night 158 showed it."""
    _night158_relay(db)
    said = _respecify_cr2(_s220(db))
    assert "faulted the check" in said, said
    assert ("Send his words about the check to the Tester with "
            "msg.answer_tester, with this criterion in refs") in said, said


def test_the_cr_2_refusal_after_the_answer_landed_names_no_refused_call(db):
    _night158_relay(db)
    _cr3_out_of_the_relay(db)
    sb = _s220(db)
    sb.call("msg.answer_tester", refs=[CR2, CR3], round_no=0)
    said = _respecify_cr2(sb)
    assert "faulted the check" in said, said
    assert "msg.answer_tester" not in said, said
    assert "carries this criterion" in said, said


def test_the_cr_2_refusal_after_an_answer_without_it_says_the_answer_is_closed(db):
    """A wake whose chain holds the ruling, with no relay: the first-answer
    door does not apply, so an answer can leave cr_2 out."""
    _night158_relay(db)
    _message(db, "m120", "m99", "tester", "terminologist", "question", [CR3],
             120)
    db.commit()
    sb = _s220(db, trigger="m120")
    sb.call("msg.answer_tester", refs=[CR3], round_no=0)
    said = _respecify_cr2(sb)
    assert "msg.answer_tester" not in said, said
    assert "closed" in said, said


def test_s220_turn_1_with_its_refused_cr_3_respecify_asks_the_respecify_first(db):
    """Pass 2: s220's real turn 1 sent a cr_3 respecify with `prompt` as the
    surface before the answer. The surface door refused it, so the answer
    would carry the contested cr_3 text. Since pass 3b the refusal names
    the drop of cr_3's line and asks no rewrite (review 4, point 2)."""
    _night158_relay(db)
    sb = _s220(db)
    with pytest.raises(ValueError) as surface:
        sb.call("criteria.respecify", id=CR3,
                text="When confirm() shows its prompt and attempts to read "
                     "from stdin, if that read hits end of file, it must "
                     "return the provided default value without emitting "
                     "any error message.",
                term_refs=["default_on_eof"],
                surface_refs=["src/click/termui.py::prompt"])
    with pytest.raises(ValueError) as refused:
        sb.call("msg.answer_tester", refs=[CR3], round_no=0)
    said = str(refused.value)
    # Pass 3b: m98 faults line 4's check, so cr_2 stands. "Drop line 5"
    # drops cr_3, and frame 192 owns that route. The refusal names the drop
    # and asks no rewrite. The full answer would still carry cr_3, so the
    # refusal offers no call (frame 135).
    assert str(surface.value)
    assert f"Your answer leaves out {CR2}" in said, said
    assert DROPPED in said, said
    assert "No respecify of" not in said, said
    assert not [o for o in sb.ctx.offers if o.op == "msg.answer_tester"]
    assert not _answers(sb)


def test_a_faulted_check_refusal_then_the_answer_is_admitted(db):
    """Pass 2b, review 2's fix: "The criterion stands" says that the ruling
    asked for no new words, so it counts as landed for cr_2."""
    _night158_relay(db)
    db.execute("UPDATE messages SET body_refs = ? WHERE id = 'm101'",
               (json.dumps([CR2]),))
    db.execute("UPDATE config SET value = ? WHERE key = 'verdict:m99'",
               (json.dumps({CR2: "revise"}),))
    db.commit()
    sb = _s220(db)
    said = _respecify_cr2(sb)
    assert "The criterion stands" in said, said
    out = sb.call("msg.answer_tester", refs=[CR2], round_no=0)
    assert out["to"] == "tester", out


# --- pass 1b, review 1 --------------------------------------------------------

def test_the_route_offers_no_dangling_ref(db):
    """Review 1, F1: refs with `cr_9_nothing` drew a route that the dangling
    guard of `_bind_send` then refused."""
    _night158_relay(db)
    _cr3_out_of_the_relay(db)
    sb = _s220(db)
    with pytest.raises(ValueError) as refused:
        sb.call("msg.answer_tester", refs=[CR3, "cr_9_nothing"], round_no=0)
    said = str(refused.value)
    assert "cr_9_nothing" not in said.split("refs:", 1)[1], said
    [offer] = [o for o in sb.ctx.offers if o.op == "msg.answer_tester"]
    assert sorted(offer.args["refs"]) == sorted([CR2, CR3])
    out = sb.call("msg.answer_tester", **offer.args, round_no=0)
    assert out["to"] == "tester", out


def test_the_closed_text_names_the_criterion_whose_work_is_done(db):
    """Review 1, F3: another ruled criterion can still wait for its rewrite,
    so the closed text ends the work on this criterion only."""
    _night158_relay(db)
    _cr3_out_of_the_relay(db)
    sb = _s220(db)
    sb.call("msg.answer_tester", refs=[CR2, CR3], round_no=0)
    said = _respecify_cr2(sb)
    assert f"your work on {CR2} is done" in said, said
    assert "your work here is done" not in said.lower(), said


def test_an_approved_criterion_with_a_ruled_test_counts_among_the_ruled(db):
    """Review 1, F4: the verdict approves cr_1 and contests its test. The
    first answer carries cr_1 beside cr_2. The relay leaves cr_3 out,
    because frame 192 owns the route of its dropped line."""
    _night158_relay(db)
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst_confirm_eof_01', 'bg_2', ?, 'tests/t.py', 'x')",
               (CR1,))
    db.execute("UPDATE messages SET body_refs = ? WHERE id = 'm101'",
               (json.dumps([CR1, CR2, "tst_confirm_eof_01"]),))
    db.execute("UPDATE config SET value = ? WHERE key = 'verdict:m99'",
               (json.dumps({CR1: "approve", CR2: "revise",
                            "tst_confirm_eof_01": "contest"}),))
    db.commit()
    sb = _s220(db)
    with pytest.raises(ValueError) as refused:
        sb.call("msg.answer_tester", refs=[CR2, CR3], round_no=0)
    assert CR1 in str(refused.value), str(refused.value)
    out = sb.call("msg.answer_tester", refs=[CR1, CR2, CR3], round_no=0)
    assert out["to"] == "tester", out


def test_the_brief_asks_one_answer_for_a_ruled_test(db):
    """Review 1, F4 and F6: the test paragraph names the same one answer,
    and the plural referent reads `them`."""
    from pathlib import Path

    text = (Path(__file__).resolve().parents[2] / "rota" / "roles" / "prompts"
            / "terminologist" / "criterion_repair.md").read_text(encoding="utf-8")
    flat = " ".join(text.split())
    assert "in the same one answer" in flat, flat
    assert "has no test of them yet" in flat, flat
    assert "has no test of it yet" not in flat, flat


# --- pass 3, the ruling read per criterion on the page he saw ----------------

def test_m98_reads_cr_2_as_standing_and_cr_3_as_asking_new_words(db):
    """m98: "Keep line 4, but fix its check" is cr_2's line, and "Drop line
    5" is cr_3's line. One ruling, two readings, on the `order:m98` record."""
    from rota.roles import api

    _night158_relay(db)
    sb = _s220(db)
    assert api.ruling_asks_no_new_words(sb.ctx, CR2)
    assert not api.ruling_asks_no_new_words(sb.ctx, CR3)


def test_a_reply_with_no_order_record_reads_todays_render(db):
    """A database from before frame 272 holds no `order:` record. Today's
    render of m89 puts cr_2 on line 3, so line 4's check is not cr_2's."""
    from rota.roles import api

    _night158_relay(db)
    db.execute("DELETE FROM config WHERE key = 'order:m98'")
    sb = _s220(db)
    assert not api.ruling_asks_no_new_words(sb.ctx, CR2)


# --- pass 3b, review 4: a colon keeps a line's body with its line -----------

# r_4a62d8a771 of night 157, at the reply m212 to the page m210.
N157_WORDS = ("Line 3: keep the requirement, but change its check so it asks "
              "for the version with the setting left off and confirms the "
              "Python version is not in that message, rather than looking at "
              "the help output. Line 5: keep it as written, but fix the code so "
              "that asking for the version with the setting on prints the exact "
              "major.minor.micro from sys.version_info, because the output is "
              "empty right now. Lines 1, 2, 4 and 6 to 8 are fine as they are.")
N157_PAGE = ["show_python", "guess:show_python", "crit_show_python_default",
             "crit_show_python_help", "crit_show_python_version",
             "l_a479b2bd45", "l_25d965403f", "l_b86fa66c6d"]
# r_m144 of night 142, at the reply m144: a negated removal of a range.
N142_WORDS = ("Yes, put the echo_json tests next to the existing echo tests in "
              "the utils tests. Fix line 7 so it compares the whole output with "
              "the compact JSON plus one newline, and strip nothing first. Don't "
              "remove lines 8 to 14 as a block: remove only line 8, which "
              "repeats line 1, cut lines 10 and 11 back to their first sentence, "
              "and drop line 13.")


def _ruled_page(conn, rid, ask, reply, words, page) -> dict:
    """A ruling on the page `ask`, with his reply `reply` and its record."""
    _message(conn, ask, None, "liaison", "principal", "present", page, 1)
    _message(conn, reply, ask, "principal", "liaison", "converse", page, 2,
             words)
    conn.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, "
                 "status) VALUES (?, ?, ?, '{}', ?, 'landed')",
                 (rid, ask, reply, words))
    backfill_ruled_refs(conn)
    conn.execute("INSERT INTO config (key, value) VALUES (?, ?)",
                 (f"order:{reply}", json.dumps(page)))
    conn.commit()
    return {"id": rid, "words": words}


def test_a_line_label_before_a_colon_keeps_its_body_on_its_line(db):
    """Review 4, finding 1: the split on ":" sent line 3's "change its check"
    to crit_show_python_version on line 5."""
    from rota.roles import api

    ruled = _ruled_page(db, "r_4a62d8a771", "m210", "m212", N157_WORDS,
                        N157_PAGE)
    five = api._ruling_words_on(db, ruled, "crit_show_python_version")
    assert "change its check" not in five, five
    assert "fix the code" in five, five
    three = api._ruling_words_on(db, ruled, "crit_show_python_default")
    assert "change its check" in three, three
    assert "fix the code" not in three, three


def test_a_negated_removal_asks_no_new_words_of_its_lines(db):
    """Review 4, finding 3: "Don't remove lines 8 to 14 as a block" asks
    nothing of line 9. "drop line 13" asks new words of line 13 alone."""
    from rota.roles import api

    page = [f"row_{n}" for n in range(1, 15)]
    ruled = _ruled_page(db, "r_m144", "m142", "m144", N142_WORDS, page)
    assert not api._words_fault_on(db, ruled, "row_9")
    assert api._words_fault_on(db, ruled, "row_13")
    assert api._line_dropped_on(db, ruled, "row_13") == 13
    assert api._line_dropped_on(db, ruled, "row_9") is None


# --- pass 3c: a dropped line needs no answer, and a kept line stands ---------

def test_an_answer_with_cr_2_and_no_cr_3_is_admitted(db):
    """m98 drops line 5, so cr_3 needs no answer. The answer with cr_2 alone
    is the session's one answer (frame 308, pass 3c, point 1)."""
    _night158_relay(db)
    sb = _s220(db)
    out = sb.call("msg.answer_tester", refs=[CR2], round_no=0)
    assert out["to"] == "tester" and out["verb"] == "answer", out
    [sent] = _answers(sb)
    assert sent["body_refs"] == [CR2]


def test_a_kept_line_with_a_code_fault_asks_no_new_words(db):
    """r_4a62d8a771, line 5: "keep it as written, but fix the code". The
    words are approved, so the criterion stands (pass 3c, point 2)."""
    from rota.roles import api

    ruled = _ruled_page(db, "r_4a62d8a771", "m210", "m212", N157_WORDS,
                        N157_PAGE)
    assert api._keeps_words_on(db, ruled, "crit_show_python_version")
    assert not api._words_fault_on(db, ruled, "crit_show_python_version")


# --- pass 3d: a drop is the whole line, and a keep yields to new words -------

PAGE5 = [f"row_{n}" for n in range(1, 6)]


@pytest.mark.parametrize("line, words", [
    (3, "Line 3 should go back to how you had it."),
    (5, "Remove line 5's last clause about the prompt."),
    (5, "Line 5 should go further and name the default."),
])
def test_a_revert_or_a_partial_edit_is_no_drop(db, line, words):
    """Review 5, finding 2: night 140's r_4dfcbd586b said "Line 3 should go
    back to how you had it". A drop removes the whole line, so these words
    ask new words of the line and drop nothing."""
    from rota.roles import api

    ruled = _ruled_page(db, "r_p3d", "m300", "m301", words, PAGE5)
    assert api._line_dropped_on(db, ruled, f"row_{line}") is None
    assert api._words_fault_on(db, ruled, f"row_{line}")


@pytest.mark.parametrize("words", [
    "Drop line 5.",
    "Please delete line 5 because it repeats line 4.",
    "Line 5 should go, and line 4 should say that confirm returns the default.",
    # Nights 143 and 144: words after the line that keep the whole line.
    "Line 8 asks again, so please remove lines 2 to 5 as I asked before.",
    "Please drop lines 2 to 5 again.",
])
def test_a_removal_of_the_whole_line_is_a_drop(db, words):
    """The removal verb's object is the line itself, and nothing after it
    narrows the removal (frame 283's clause reading)."""
    from rota.roles import api

    ruled = _ruled_page(db, "r_p3d", "m300", "m301", words, PAGE5)
    assert api._line_dropped_on(db, ruled, "row_5") == 5


@pytest.mark.parametrize("words", [
    "Line 4: keep the requirement, but it should say that confirm returns "
    "the default.",
    "Keep line 4 as it is, but change it to say that confirm returns the "
    "default.",
    "Line 4 should say that confirm returns the default, and keep it as "
    "written otherwise.",
    "Line 4 should say that confirm returns the default. Keep it as it is "
    "for the rest.",
])
def test_a_keep_yields_to_a_request_for_new_words(db, words):
    """Review 5, finding 1: a keep in the same sentence as a request for new
    words, or a keep that names no line, cancels no request."""
    from rota.roles import api

    ruled = _ruled_page(db, "r_p3d", "m300", "m301", words, PAGE5)
    assert api._words_fault_on(db, ruled, "row_4")


def test_a_keep_of_one_line_stands_beside_new_words_on_another(db):
    """A keep that names line 3 still keeps line 3, and the words request on
    line 4 bears on line 4 only."""
    from rota.roles import api

    words = ("Keep line 3 as it is. Line 4 should say that confirm returns "
             "the default.")
    ruled = _ruled_page(db, "r_p3d", "m300", "m301", words, PAGE5)
    assert not api._words_fault_on(db, ruled, "row_3")
    assert api._keeps_words_on(db, ruled, "row_3")
    assert api._words_fault_on(db, ruled, "row_4")
