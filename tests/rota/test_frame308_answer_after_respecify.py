"""Frame 308, pass 2: the answer after a failed respecify.

Night 159 (`plans/frame306-w1-hop.md`, sections c and e). The principal said
"line 3 is wrong" about `ver_opt_show_py` five times. Each seat sent a
respecify and `msg.answer_tester` in one turn. The surface door refused the
respecify, and the answer went out with the old criterion by its ref. The
rows below are the night's, copied from `.rota/clickI_night159.db` on
2026-10-23, so the tests run in a checkout without the run's database.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import backfill_ruled_refs, init_db
from rota.core.sandbox import build
from rota.roles import prompts

ITEM = "version_option_show_python"
TICKET = "tk_1_version_option_show_python"
CR = "ver_opt_show_py"
SURFACE = "src/click/decorators.py::version_option"
A_TEST = "tests/test_basic.py::test_custom_version_option"

# `criteria` v6, written by s349.
V6 = ("The implementation of show_python must not alter the behavior of "
      "existing tests that verify version output format without the Python "
      "version string. When the --show-python flag is off (default), the "
      "command exits cleanly and prints nothing. The check should pass the "
      "version flag and expect the same message the option prints today, "
      "which is the program name, a comma, the word \"version\" and the "
      "version number. Also add a second check that turns the flag on and "
      "checks the message ends with the Python version from "
      "sys.version_info, written as major.minor.micro.")
# s398's turn 1 text: his words in place of "prints nothing".
S398_TEXT = ("The implementation of show_python must not alter the behavior of "
             "existing tests that verify version output format without the "
             "Python version string. When the --show-python flag is off "
             "(default), the command exits cleanly and prints the same version "
             "message as today, which is the program name, a comma, the word "
             "\"version\" and the version number. Also add a second check that "
             "turns the flag on and checks the message ends with the Python "
             "version from sys.version_info, written as major.minor.micro.")
# m224, the principal's words of r_03b3346468.
WORDS = ("Line 3 has to change: when the new flag is off, the command should "
         "print the same version message as today, not nothing, and the check "
         "should expect a clean exit and that exact message. Line 4 is wrong "
         "too: the flag should be off by default, so the Python version shows "
         "only when someone turns it on. Lines 1 and 2 are fine.")
VERDICT = {CR: "contest", "l_e49bfc5b82": "contest"}
PER_ITEM = {CR: "contest", "l_e49bfc5b82": "contest", ITEM: "approve",
            f"guess:{ITEM}": "approve"}
# The lines of the page m223 in the order m224 names them.
PAGE = [ITEM, f"guess:{ITEM}", CR, "l_e49bfc5b82"]

SURFACE_REFUSAL = "a test is not a surface"
ONE_ANSWER = "you have already sent answer to tester"


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES (?, 'Give version_option a show_python flag "
                 "that appends the running Python version to the message.', "
                 "'in_scope', 'approved', 3, 3)", (ITEM,))
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, ?, "
                 "'give version_option a show_python flag that appends the "
                 "running Python version to the message')", (TICKET, ITEM))
    conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs, "
                 "version) VALUES (?, ?, ?, ?, 6)",
                 (CR, TICKET, V6, json.dumps([SURFACE])))
    for grain, area in ((SURFACE, "src/click"), (A_TEST, ".")):
        conn.execute("INSERT INTO code_index (grain, grain_kind, area, "
                     "sym_kind) VALUES (?, 'symbol', ?, 'function')",
                     (grain, area))
    conn.execute("INSERT INTO batches (id, item_id, head_commit, status) "
                 "VALUES ('bg_4', ?, 'b5f0be71', 'deferred')", (ITEM,))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_4', ?)", (TICKET,))
    conn.commit()
    return conn


def _message(conn, mid, cause, sender, to, verb, refs, seq, text=None):
    conn.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
                 "to_role, verb, body_refs, body_text, seq) VALUES "
                 "(?, ?, 'm223', ?, ?, ?, ?, ?, ?)",
                 (mid, cause, sender, to, verb, json.dumps(refs), text, seq))


def _night159_relay(conn, verdict=VERDICT, text=V6) -> None:
    """The page m223, the reply m224, the verdict m225, the ruling, the relay
    m226 that woke s382."""
    _message(conn, "m223", None, "liaison", "principal", "present",
             [ITEM, CR], 226)
    _message(conn, "m224", "m223", "principal", "liaison", "converse",
             [ITEM, CR], 228, WORDS)
    _message(conn, "m225", "m223", "principal", "liaison", "verdict", [CR], 229)
    _message(conn, "m226", "m225", "liaison", "terminologist", "relay", [CR],
             230)
    conn.execute("INSERT INTO config (key, value) VALUES ('verdict:m225', ?)",
                 (json.dumps(verdict),))
    # The page m223 as he saw it at m224, as `principal.land` records it
    # since frame 272. His "Line 3 has to change" names ver_opt_show_py.
    conn.execute("INSERT INTO config (key, value) VALUES ('order:m224', ?)",
                 (json.dumps(PAGE),))
    conn.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, "
                 "status, verdict_id, texts) VALUES ('r_03b3346468', 'm223', "
                 "'m224', ?, ?, 'landed', 'm225', ?)",
                 (json.dumps(PER_ITEM), WORDS, json.dumps({CR: text})))
    backfill_ruled_refs(conn)
    conn.commit()


def _seat(conn, sid="s382", trigger="m226"):
    sb = build("terminologist", conn, mode="criterion_repair", session_id=sid,
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    sb.ctx.trigger = trigger
    sb.ctx.wake_kind = "message"
    return sb


def _answers(sb):
    return [m for m in sb.ctx.outbound
            if m["to_role"] == "tester" and m["verb"] == "answer"]


def _turn_1(sb, text):
    """The respecify of turn 1, with a test named as the surface."""
    with pytest.raises(ValueError) as refused:
        sb.call("criteria.respecify", id=CR, text=text,
                term_refs=["command", "option"], surface_refs=[A_TEST])
    return str(refused.value)


def _assert_refused_after(sb, surface_said):
    with pytest.raises(ValueError) as refused:
        sb.call("msg.answer_tester", refs=[CR], round_no=0)
    said = str(refused.value)
    assert CR in said, said
    assert f"No respecify of {CR} has landed" in said, said
    if surface_said is not None:
        assert surface_said in said, said
    assert "respecify" in said and "answer once" in said, said
    assert not _answers(sb)
    return said


def test_s382_turn_1_answer_after_the_refused_respecify_is_refused(db):
    """s382 turn 1, m226 to m227: the v6 text with a test as the surface."""
    _night159_relay(db)
    sb = _seat(db)
    surface_said = _turn_1(sb, V6)
    assert SURFACE_REFUSAL in surface_said, surface_said
    _assert_refused_after(sb, surface_said)


def test_s398_turn_1_his_words_with_a_test_surface_is_refused_the_same(db):
    """s398 turn 1: his words in the text, the same surface. The relay m242
    and its verdict m240 have the shape of m226 and m225."""
    _night159_relay(db)
    sb = _seat(db, sid="s398")
    surface_said = _turn_1(sb, S398_TEXT)
    assert SURFACE_REFUSAL in surface_said, surface_said
    said = _assert_refused_after(sb, surface_said)
    assert "criteria.respecify" in said, said


def test_the_respecify_lands_then_the_answer_is_admitted(db):
    _night159_relay(db)
    sb = _seat(db)
    _turn_1(sb, S398_TEXT)
    out = sb.call("criteria.respecify", id=CR, text=S398_TEXT,
                  term_refs=["command", "option"], surface_refs=[SURFACE])
    assert out.get("respecified"), out
    out = sb.call("msg.answer_tester", refs=[CR], round_no=0)
    assert out["to"] == "tester" and out["verb"] == "answer", out
    assert len(_answers(sb)) == 1


def test_an_answer_with_no_respecify_tried_is_refused(db):
    """Pass 2b: the key is the landed write, so an answer with no respecify
    at all is refused, and the text has no quote."""
    _night159_relay(db)
    sb = _seat(db)
    said = _assert_refused_after(sb, None)
    assert "was refused with" not in said, said


def test_s382_turn_2_same_words_after_the_surface_refusal_is_refused(db):
    """Review 2, F1: the seat corrects the surface and sends the v6 text. The
    same-words branch refuses it and names msg.answer_tester. The answer
    still carries the old text, so the door refuses it."""
    _night159_relay(db)
    sb = _seat(db)
    _turn_1(sb, V6)
    with pytest.raises(ValueError) as words:
        sb.call("criteria.respecify", id=CR, text=V6,
                term_refs=["command", "option"], surface_refs=[SURFACE])
    assert "msg.answer_tester" in str(words.value), str(words.value)
    _assert_refused_after(sb, str(words.value))


def test_an_argument_refusal_then_the_answer_is_refused(db):
    """Review 2, F2: a respecify with no `text` meets the argument check in
    `Sandbox.call`, before the respecify wrapper."""
    _night159_relay(db)
    sb = _seat(db)
    with pytest.raises(Exception) as args:
        sb.call("criteria.respecify", id=CR, surface_refs=[SURFACE])
    assert "missing required argument" in str(args.value), str(args.value)
    _assert_refused_after(sb, str(args.value))


def test_an_unchanged_return_then_the_answer_is_refused(db):
    """Review 2, F3: the ruling's contested text differs from the row, so the
    row's own words return `unchanged` and write nothing."""
    # A ruled row never changes, so the older text is seeded with the
    # ruling (the seam design, 1.1).
    _night159_relay(db, text="An older text of line 3.")
    sb = _seat(db)
    out = sb.call("criteria.respecify", id=CR, text=V6,
                  term_refs=["command", "option"], surface_refs=[SURFACE])
    assert out.get("unchanged"), out
    _assert_refused_after(sb, None)


def test_a_relay_with_no_ruled_criterion_admits_the_answer(db):
    """The verdict approves the criterion, so the relay rules none."""
    _night159_relay(db, verdict={CR: "approve"})
    sb = _seat(db)
    _turn_1(sb, S398_TEXT)
    out = sb.call("msg.answer_tester", refs=[CR], round_no=0)
    assert out["to"] == "tester", out


def test_a_wake_with_no_relay_admits_the_answer(db):
    _message(db, "m50", None, "tester", "terminologist", "question", [CR], 50)
    db.commit()
    sb = _seat(db, trigger="m50")
    _turn_1(sb, S398_TEXT)
    out = sb.call("msg.answer_tester", refs=[CR], round_no=0)
    assert out["to"] == "tester", out


def test_the_refusal_sentences_keep_to_twenty_words_outside_the_quote(db):
    _night159_relay(db)
    sb = _seat(db)
    surface_said = _turn_1(sb, V6)
    said = _assert_refused_after(sb, surface_said)
    own = said.replace(surface_said, "")
    for sentence in own.split(". "):
        assert len(sentence.split()) <= 20, sentence


# --- pass 3, the words that drop, rewrite or change a line --------------------

# The ruling words of each wake, from `rulings` of nights 158 and 159.
S370_WORDS = ("Lines 1, 2 and 4 are fine as they are, but please rewrite line 3. "
              "Where it says the command prints nothing when the new flag is off, "
              "change it to say the command prints the same version message as "
              "today. Also change the check so it runs the real command that has "
              "the version option on it, not the empty helper function, and "
              "expects a clean exit and that exact message.")
S250_WORDS = ("Line 3's check should expect closed stdin to abort with Abort as it "
              "does today when the flag is off, not to raise a UsageError. Lines 6 "
              "and 8 should pass a boolean default such as True and expect True "
              "back, and line 8 also needs a prompt text, while line 7 should go "
              "because confirm has no option or sentinel, and the simple choice is "
              "to return False when there is no default. Drop line 14, because any "
              "short prompt text works and confirm only needs to return its own "
              "boolean default when the flag is on and stdin is closed.")
S220_WORDS = ("Lines 1, 2, 3 and 6 to 8 are fine as written. Keep line 4, but fix "
              "its check so it fakes a closed input properly, because the failure "
              "comes from a broken test stub and not from the behaviour. Drop line "
              "5, because I never asked for the prompt to be hidden, so the prompt "
              "can show as usual before it falls back to the default.")
S274_WORDS = ("Line 3's check is wrong. It looks for the version inside "
              "parentheses, but I asked for the word \"Python\", a space, and then "
              "the version as major.minor.micro. Please fix that check and keep "
              "working on the change rather than dropping it.")


@pytest.mark.parametrize("words", [S370_WORDS, S250_WORDS, S220_WORDS, WORDS],
                         ids=["s370", "s250", "s220", "s382"])
def test_a_ruling_that_drops_or_rewrites_a_line_asks_new_words(words):
    from rota.roles import api

    assert api._WORDS_FAULT.search(words), words


@pytest.mark.parametrize("words", [S274_WORDS], ids=["s274"])
def test_a_ruling_that_faults_only_the_check_asks_no_new_words(words):
    from rota.roles import api

    assert api._CHECK_FAULT.search(words), words
    assert not api._WORDS_FAULT.search(words), words


def test_line_3_has_to_change_asks_new_words_on_its_own_line(db):
    """m224's "Line 3 has to change" names ver_opt_show_py on the page he
    saw. The check words that follow it do not make the criterion stand."""
    from rota.roles import api

    _night159_relay(db)
    assert not api.ruling_asks_no_new_words(_seat(db).ctx, CR)
