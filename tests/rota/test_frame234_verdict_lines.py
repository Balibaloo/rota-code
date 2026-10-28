"""
The verdict's contest lands only on a line the words fault.

Night 146 (frame 234): nine of 22 Liaison verdicts on numbered pages
contested lines the principal's words never faulted. s427 contested lines 1
to 4 when the words said they match, and s122 contested line 1, the request,
when the words faulted lines 3 and 5. Each cancelled a batch. The door
`rulings.rule` now reads the words for line references with a direction.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db

from .test_principal_reply import _landing, _present
from .test_request_page import bg2  # noqa: F401  (a fixture, night 136's page)


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


S122_SHAPE = ("Line 3 isn't right: the user should not type the bill at all. "
              "Line 4 also goes too far, because I didn't ask for a typed "
              "percentage, so please drop it.")
# The same shape on the request page, which has three lines.
S122_ON_REQUEST = ("Line 2 isn't right: the user should not type the bill at "
                   "all. Line 3 also goes too far, because I didn't ask for a "
                   "typed percentage.")


def _rule(db, words, rulings):
    ask = _present(db)
    sb, _ = _landing(db, ask, words)
    return sb.call("rulings.rule", rulings=rulings, words=words)


def _request_page(db, verb="present"):
    """The present page without the quoted statement: line 1 is the request
    item calculate_tip, line 2 how_it_works, line 3 the note l_1."""
    from rota.roles.principal import pending_asks

    _present(db)
    db.execute("UPDATE messages SET body_refs = ?, verb = ? WHERE id = 'm9'",
               (json.dumps(["calculate_tip", "how_it_works", "l_1"]), verb))
    db.commit()
    return pending_asks(db)[0]


def _rule_request(db, words, rulings, verb="present"):
    ask = _request_page(db, verb)
    if verb == "present":
        assert ask.order == ["calculate_tip", "how_it_works", "l_1"], ask.order
    sb, _ = _landing(db, ask, words)
    return sb.call("rulings.rule", rulings=rulings, words=words)


def test_a_contest_on_lines_the_words_say_match_is_refused(db):
    words = "Ok, go ahead. Lines 1 to 4 match what I asked for."
    with pytest.raises(ValueError) as e:
        _rule(db, words, {"1": "contest", "2": "contest", "3": "contest",
                          "4": "contest"})
    assert "lines 1 to 4" in str(e.value) and "reverses" in str(e.value)
    assert "Approve lines 1 to 4." in str(e.value)


def test_the_refusal_names_only_the_matched_lines_contested(db):
    words = "Ok, go ahead. Lines 1 to 4 match what I asked for."
    with pytest.raises(ValueError, match=r"Approve lines 1 to 3\.$"):
        _rule(db, words, {"1": "contest", "2": "contest", "3": "contest",
                          "4": "approve"})


def test_a_contest_on_the_request_line_the_words_do_not_fault_is_refused(db):
    with pytest.raises(ValueError) as e:
        _rule_request(db, S122_ON_REQUEST,
                      {"1": "contest", "2": "contest", "3": "contest"})
    text = str(e.value)
    assert text.startswith("line 1: the words do not fault the request. "
                           "They fault lines 2 and 3.")
    assert "Rule lines 2 and 3 as the words say, and approve line 1." in text


def test_the_same_words_land_when_line_1_is_approved(db):
    out = _rule_request(db, S122_ON_REQUEST,
                        {"1": "approve", "2": "contest", "3": "contest"})
    assert out["per_item"] == {"calculate_tip": "approve",
                               "how_it_works": "contest", "l_1": "contest"}


def test_a_page_that_opens_with_a_quote_takes_a_contest_on_line_1(db):
    # Line 1 is the statement s1, not a request item (review 1, finding 1).
    out = _rule(db, S122_SHAPE, {"1": "contest", "2": "approve", "3": "contest",
                                 "4": "contest"})
    assert out["per_item"]["s1"] == "contest"


def test_a_reference_to_line_1_with_no_cue_lets_it_be_contested(db):
    words = ("Line 1 isn't a request, so please take it off the page. Line 2 "
             "is also wrong.")
    out = _rule_request(db, words, {"1": "contest", "2": "contest", "3": "approve"})
    assert out["per_item"]["calculate_tip"] == "contest"


def test_a_sentence_with_no_line_number_lets_line_1_be_contested(db):
    words = ("Line 2 is wrong because the bill is typed once. Also, take the "
             "tip in cents.")
    out = _rule_request(db, words, {"1": "contest", "2": "contest", "3": "approve"})
    assert out["per_item"]["calculate_tip"] == "contest"


def test_a_bare_agreement_is_no_correction_of_the_request(db):
    words = "Ok, go ahead. Line 2 is wrong because the bill is typed once."
    with pytest.raises(ValueError, match="the words do not fault the request"):
        _rule_request(db, words, {"1": "contest", "2": "contest", "3": "approve"})


def test_a_quote_of_line_1_inside_the_door_lets_it_be_contested(db):
    with pytest.raises(ValueError, match="the words do not fault the request"):
        _rule_request(db, "Line 2 is wrong, and the tip is wrong too.",
                      {"1": "contest", "2": "contest", "3": "approve"})


def test_the_quote_branch_lands(tmp_path):
    db = init_db(tmp_path / "rota.db")
    words = "Line 2 is wrong, and the software calculates the tip wrong too."
    out = _rule_request(db, words, {"1": "contest", "2": "contest", "3": "approve"})
    assert out["per_item"]["calculate_tip"] == "contest"


def test_a_fault_past_the_end_of_the_page_refuses_nothing(db):
    # Review 1, finding 7: the refusal names lines, so it needs one.
    out = _rule_request(db, "Line 9 is wrong.",
                        {"1": "contest", "2": "approve", "3": "approve"})
    assert out["per_item"]["calculate_tip"] == "contest"


def test_a_fault_after_a_match_in_one_clause_lands_the_contest(db):
    words = "Line 2's text is right now, but its check still types the bill."
    out = _rule_request(db, words, {"1": "approve", "2": "contest", "3": "approve"})
    assert out["per_item"]["how_it_works"] == "contest"


def test_a_negated_match_lands_the_contest(db):
    out = _rule_request(db, "Line 2 doesn't match what I asked for.",
                        {"1": "approve", "2": "contest", "3": "approve"})
    assert out["per_item"]["how_it_works"] == "contest"


def test_a_clarify_is_not_read_for_lines(db):
    # A contest needs words that back it, so the words fault (review p7 p1,
    # finding 1). Words that agree back no contest.
    words = "Lines 1 to 4 are wrong."
    out = _rule_request(db, words, {"calculate_tip": "contest",
                                    "how_it_works": "contest"}, verb="clarify")
    assert out["per_item"]["calculate_tip"] == "contest"


def test_a_page_with_no_numbered_line_takes_the_empty_ruling(db):
    # The touch note numbers no line, so `order` is empty and the door
    # acknowledges the reply.
    from rota.roles.principal import pending_asks

    _present(db)
    db.execute("UPDATE messages SET body_refs = '[]' WHERE id = 'm9'")
    db.commit()
    ask = pending_asks(db)[0]
    words = "Lines 1 to 4 match what I asked for."
    sb, _ = _landing(db, ask, words)
    out = sb.call("rulings.rule", rulings={}, words=words)
    assert out["per_item"] == {}


# Night 143 and 144: four right verdicts that review 1 found refused by the
# pass 1 door. Verbatim from the `rulings` table of each night's database.
RIGHT_143_144 = {
    "144 m193": ("Line 1 isn't a request, so please take it off the page. It was "
                 "only my note on the scope of the JSON helper. Line 2 is also "
                 "wrong because it says the pager test file must stay untouched, "
                 "but I said the team may make the smallest fix there if the new "
                 "helper is what broke those tests, and should leave the file "
                 "alone otherwise.", {"1": "contest", "2": "contest", "3": "approve"}),
    "143 m263": ("Line 3 is wrong because the flag should be off by default, so the "
                 "Python version shows only when someone turns it on. Also, take the "
                 "version from the running interpreter's version info, written as "
                 "major.minor.micro.", {"1": "contest", "2": "approve", "3": "contest"}),
    "143 m339": ("Line 2's text is right now, but its check still passes a show "
                 "python switch on the command line, and no such switch exists. The "
                 "check should call each command with its normal version switch. "
                 "Then it should confirm that the word Python appears only for the "
                 "command that turned the flag on.",
                 {"1": "approve", "2": "contest", "3": "approve"}),
}


@pytest.mark.parametrize("night_ask", sorted(RIGHT_143_144))
def test_a_right_verdict_of_nights_143_and_144_lands(db, night_ask):
    words, rulings = RIGHT_143_144[night_ask]
    out = _rule_request(db, words, rulings)
    assert sorted(k for k, v in rulings.items() if v == "contest") == sorted(
        str(["calculate_tip", "how_it_works", "l_1"].index(r) + 1)
        for r, v in out["per_item"].items() if v == "contest")


# Night 144, m236. The words fault only the test files under line 1, so the
# files cue of frame 298, design 3.3, refuses a contest of line 1.
M236 = ("Line 12 is wrong: I never overruled the helper. I still want it "
        "added next to echo, and my note about line 1 was only about which "
        "test files it points at. On line 1, the echo tests are right, but "
        "the termui and context test files don't belong there.")


def test_m236_a_contest_of_the_request_is_refused_with_the_key_named(db):
    with pytest.raises(ValueError, match=(
            r"line 1 is the request, and the words fault only the code it "
            r"touches\. The team has not guessed that code yet\. Rule the key "
            r"guess:calculate_tip contest with the words, and approve line 1\.")):
        _rule_request(db, M236, {"1": "contest", "2": "approve", "3": "approve"})


def test_m236_the_moved_reading_lands_with_the_item_approved(db):
    out = _rule_request(db, M236, {"guess:calculate_tip": "contest", "1": "approve",
                                   "2": "approve", "3": "approve"})
    assert out["per_item"]["calculate_tip"] == "approve"
    assert out["per_item"]["guess:calculate_tip"] == "contest"


def test_words_that_fault_line_1_land_a_contest_on_it(db):
    words = "1 is wrong: the request should say json, not yaml"
    out = _rule(db, words, {"1": "contest", "2": "approve", "3": "approve",
                            "4": "approve"})
    assert out["per_item"]["s1"] == "contest"


def test_an_approval_and_a_named_fault_land_as_before(db):
    out = _rule(db, "fine", {"1": "approve", "2": "approve", "3": "approve",
                             "4": "approve"})
    assert set(out["per_item"].values()) == {"approve"}


def test_a_named_fault_on_line_4_lands(tmp_path):
    db = init_db(tmp_path / "rota.db")
    out = _rule(db, "4 is wrong", {"1": "approve", "2": "approve",
                                   "3": "approve", "4": "contest"})
    assert out["per_item"]["l_1"] == "contest"


def test_a_quote_of_line_1_lets_the_request_be_contested():
    from rota.roles.api import _quotes_line

    page = ('1. "Add an echo_json helper that prints compact JSON"\n'
            "2. The helper writes one newline.\n")
    assert _quotes_line("Please change add an echo_json helper that prints "
                        "pretty JSON instead.", page, 1)
    assert not _quotes_line("Line 2 is wrong.", page, 1)


# The recorded replies of night 146, verbatim from the `messages` table of
# `.rota/clickI_night146.db`.
RECORDED = {
    "s427": ("Ok, go ahead. Lines 1 to 4 match what I asked for, and the files "
             "in line 5 look reasonable for the change.",
             set(), {1, 2, 3, 4, 5}),
    "s122": ("Line 3 isn't right: I don't want any special conversion, so "
             "objects should go straight to the standard library json module "
             "and fail with its usual error when they can't be serialized. "
             "Line 5 also goes too far, because I didn't ask for anything about "
             "the pager, so please drop the pager test and keep the new test in "
             "the existing echo tests file.",
             {3, 5}, set()),
    "s245": ("Line 2 is wrong because the helper should write the compact JSON "
             "and one newline to the stream the way echo does, and return "
             "nothing. Line 4 is wrong because the helper should not catch "
             "errors and should let the usual json error through when an object "
             "can't be serialized. Line 5 names the wrong files, since shell "
             "completion has nothing to do with this, and the helper belongs in "
             "the utils module next to echo, with its test in the existing utils "
             "tests rather than in new files.",
             {2, 4, 5}, set()),
    "s307": ("Line 1 names the context, formatting and termui test files, but "
             "only the utils module and the existing echo tests file should "
             "change. Line 9 is wrong because the helper prints the compact JSON "
             "with one newline and does not return a string. Line 10 is also "
             "wrong because the helper should let the usual json error through, "
             "not return an error string.",
             {1, 9, 10}, set()),
    "s221": ("Line 1 names the wrong files. The context and formatting tests "
             "have nothing to do with this, and the new test belongs in the "
             "existing echo tests file, next to the helper in utils. Line 1 also "
             "no longer says to use only the standard library json module, or "
             "that the helper fails with the usual json error when it can't "
             "serialize an object, so please put both back.",
             {1}, set()),
    "143 m339": (RIGHT_143_144["143 m339"][0], {2}, set()),
    "a negated match": ("Line 4 doesn't match what I asked for.", {4}, set()),
}


@pytest.mark.parametrize("session", sorted(RECORDED))
def test_the_reader_on_the_recorded_replies(session):
    from rota.roles.api import _line_reading

    words, faulted, matched = RECORDED[session]
    assert _line_reading(words) == (faulted, matched)


def test_a_sentence_that_only_agrees_is_a_bare_agreement():
    """Frame 234, review 2, findings 1 and 2: an agreeing sentence with no line
    number corrects nothing, so it does not open the line-1 door."""
    from rota.roles.api import _BARE_AGREEMENT

    for s in ("Ok, go ahead.", "Yes.", "Looks good to me.", "Approved, thanks.",
              "The rest of the page looks fine to me.", "Everything else is fine."):
        assert _BARE_AGREEMENT.fullmatch(s), s
    for s in ("Fine, but line 3 is wrong.", "Take the version from the interpreter.",
              "Also drop the pager test."):
        assert not _BARE_AGREEMENT.fullmatch(s), s


# Night 147 (frame 234, pass 2): s281 contested six lines the words never
# name, and approved line 7, which the words fault as "Note 7". The contest
# of lines 5 and 6 went to the Vision Keeper and cost bg_2. Verbatim from
# the `rulings` table of `.rota/clickI_night147.db`.
M131 = ("Line 4 is wrong: it has to say the flag defaults to False so current "
        "callers still get an abort on closed stdin, and that can be tested by "
        "calling confirm without the flag. Note 7 was wrong to drop it. Line 3 "
        "also needs a check for the False case, and its True check currently "
        "crashes with an unbound variable error, so please fix that crash.")
M65 = ("Line 2's check is wrong because it compares against the default spaced "
       "output, so it should check that the whole output equals the compact "
       "string with one newline at the end. Line 8 is wrong because there "
       "should be no pickle check and no str conversion, so the standard json "
       "module's own TypeError stands. For the same reason, line 7 should not "
       "expect a custom \"Cannot serialize\" message.")


def _refusal(words, contested, size, batch_lines=frozenset(),
             item_lines=frozenset({1, 2, 3, 4}), request_lines=frozenset(),
             request_texts=(), faulted_texts=()):
    """The door's reading of a page of `size` lines that opens with a request
    item, as `rulings_rule` calls it. Lines 1 to 4 are the request and its
    criteria on m131's and m65's pages. `faulted_texts` are the texts that
    the caller reads for the faulted lines."""
    from rota.roles.api import _line_reading, _line_refusal

    faulted, matched = _line_reading(words)
    kw = {"request_lines": frozenset(request_lines)} if request_lines else {}
    if request_texts:
        kw["request_texts"] = tuple(request_texts)
    if faulted_texts:
        kw["faulted_texts"] = tuple(faulted_texts)
    return _line_refusal(words, set(contested), faulted, matched, size, True,
                         False, frozenset(batch_lines), frozenset(item_lines),
                         **kw)


def test_s281s_contest_of_lines_the_words_do_not_name_is_refused():
    out = _refusal(M131, {3, 4, 5, 6, 8, 9, 10, 11}, 11)
    assert out == ("The words name lines 3, 4 and 7 and do not name lines 5, 6 "
                   "and 8 to 11. A contest rests on the principal's words. "
                   "Approve the lines the words do not name, or rule them as "
                   "the words say.")


@pytest.mark.parametrize("contested", [{3, 4, 7}, {3, 4}])
def test_m131s_words_land_a_contest_on_the_lines_they_name(contested):
    # {3, 4} is the ruling with line 7 `revise`, which is no contest.
    assert _refusal(M131, contested, 11) is None


def test_a_note_number_is_a_line_reference():
    from rota.roles.api import _line_reading

    assert _line_reading("Note 7 was wrong to drop it.") == ({7}, set())
    # Night 146's words: "Please drop note 8. Note 9 is fine." A verb
    # directly before the reference governs it, so "drop note 8" faults
    # note 8 (frame 305, pass 2).
    assert _line_reading("Please drop note 8. Note 9 is fine.") == ({8}, {9})
    assert _line_reading("Notes 5 to 6 are fine.") == (set(), {5, 6})


def test_through_reads_as_a_range():
    from rota.roles.api import _line_reading

    # Night 149's m96, its first sentence. The reader read line 2 alone, so
    # the Liaison's contest of lines 3 to 7 met the door (frame 256).
    m96 = ("Lines 2 through 7 still say confirm raises a usage error, but "
           "today it aborts, so please fix that wording.")
    assert _line_reading(m96) == (set(range(2, 8)), set())
    assert _line_reading("notes 8 through 11 are fine") == (
        set(), set(range(8, 12)))


def test_s171s_contest_of_a_line_the_words_do_not_name_is_refused():
    out = _refusal(M65, {2, 3, 7, 8}, 9)
    assert out is not None
    assert out.startswith("The words name lines 2, 7 and 8 and do not name "
                          "line 3.")


def test_a_sentence_with_no_line_number_lets_an_unnamed_line_be_contested(db):
    # Night 143's m263: such a sentence can correct a line it never numbers.
    words = ("Line 3 is wrong because the tip is rounded. Also, take the tip "
             "in cents.")
    out = _rule(db, words, {"1": "approve", "2": "contest", "3": "contest",
                            "4": "approve"})
    assert out["per_item"]["how_it_works"] == "contest"


def test_a_contest_of_a_batch_line_is_left_to_the_batch_door():
    # Night 136's m85 said "Line 2" for a line of the batch's prediction, and
    # the right ruling contested the batch line 5 (`test_request_page.py`).
    from rota.roles.api import _line_reading, _line_refusal

    words = ("Line 2 names the wrong tests: the confirm prompt's tests live in "
             "the terminal UI test file, not the defaults test file. Everything "
             "else looks right.")
    faulted, matched = _line_reading(words)
    assert _line_refusal(words, {5}, faulted, matched, 5, True, False,
                         frozenset({5})) is None
    assert _line_refusal(words, {3, 5}, faulted, matched, 5, True, False,
                         frozenset({5})).startswith(
        "The words name line 2 and do not name line 3.")


def test_a_bare_agreement_names_no_line(db):
    with pytest.raises(ValueError) as e:
        _rule(db, "Line 3 is wrong. The rest looks fine.",
              {"1": "approve", "2": "contest", "3": "contest", "4": "approve"})
    assert str(e.value).startswith("The words name line 3 and do not name "
                                   "line 2.")


# Frame 234, pass 2b (review 3, finding 1): one sentence with no line number
# silenced the refusal on m131. Such a sentence can correct an item line, as
# night 143's m263 did, but never a team note.
UNNUMBERED = " Please also keep the tests small."
S281 = {str(n): ("contest" if n in (3, 4, 5, 6, 8, 9, 10, 11) else "approve")
        for n in range(1, 12)}


def _page11(db):
    """m131's page shape on the `_present` fixture: line 1 the request item,
    lines 2 to 4 its criteria, lines 5 to 11 seven team notes."""
    from rota.roles.principal import pending_asks

    _present(db)
    for iid in ("c1", "c2", "c3"):
        db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                   "version) VALUES (?,?,'in_scope','draft',0,1)",
                   (iid, "criterion " + iid))
    for k in range(2, 8):
        db.execute("INSERT INTO ledger (id, about_ref, about_table, "
                   "default_taken, status, author) VALUES (?,'how_it_works',"
                   "'items',?,'open','critic')", (f"l_{k}", f"note text {k}"))
    refs = ["calculate_tip", "c1", "c2", "c3"] + [f"l_{k}" for k in range(1, 8)]
    db.execute("UPDATE messages SET body_refs = ? WHERE id = 'm9'",
               (json.dumps(refs),))
    db.commit()
    ask = pending_asks(db)[0]
    assert ask.order == refs, ask.order
    return ask


def _rule11(db, words, rulings):
    ask = _page11(db)
    sb, _ = _landing(db, ask, words)
    return sb.call("rulings.rule", rulings=rulings, words=words)


@pytest.mark.parametrize("extra", ["", UNNUMBERED])
def test_s281s_call_is_refused_through_the_door(db, extra):
    with pytest.raises(ValueError) as e:
        _rule11(db, M131 + extra, S281)
    assert str(e.value).startswith("The words name lines 3, 4 and 7 and do not "
                                   "name lines 5, 6 and 8 to 11.")


def test_an_unnumbered_sentence_spares_a_line_of_the_request(db):
    # m263's shape: a numbered fault and an unnumbered correction. The
    # fixture's criteria are items of the request, so line 4 is a request
    # line, and its contest lands (the F2 review of pass 2, finding 3).
    words = ("Line 3 is wrong because the tip is rounded. Also, take the tip "
             "in cents.")
    rulings = {str(n): "approve" for n in range(1, 12)}
    rulings.update({"3": "contest", "4": "contest"})
    out = _rule11(db, words, rulings)
    assert out["per_item"]["c3"] == "contest"


def test_an_unnumbered_sentence_never_spares_a_note_line(db):
    words = ("Line 3 is wrong because the tip is rounded. Also, take the tip "
             "in cents.")
    rulings = {str(n): "approve" for n in range(1, 12)}
    rulings.update({"3": "contest", "4": "contest", "6": "contest"})
    with pytest.raises(ValueError) as e:
        _rule11(db, words, rulings)
    assert str(e.value).startswith("The words name line 3 and do not name "
                                   "line 6.")


def test_a_batch_line_the_words_never_name_lands_its_contest(bg2):
    """Review 3, finding 2, through the door: night 136's page with bg_2
    unbuilt on line 5. The words number line 2 and nothing else, and the
    contest of line 5 lands, because the batch door rules a batch line. The
    contest reaches the verdict before the build."""
    from .test_request_page import ITEM_136, P, _dispatch, _reply, _verdict
    from .test_request_page import _landing as _land_session

    (wake,) = P.REGISTRY["touch_note"].fn(bg2)
    mid = _dispatch(bg2, wake,
                    f'TOOL: msg.present_principal(refs=["bg_2", "{ITEM_136}"])')
    words = "Line 2 names the wrong tests. Everything else looks right."
    reply = _reply(bg2, mid, words)
    _land_session(bg2, reply, {"1": "approve", "2": "contest", "3": "approve",
                               "4": "approve", "5": "contest"}, words)
    _, ruled = _verdict(bg2, mid)
    assert ruled.get("bg_2") == "contest", ruled


@pytest.mark.parametrize("words, contested, batch, asked", [
    # m28 s112: no line reference, and the page shows no request line, so
    # the door has no line to send the instruction to. With the request on
    # line 1 the same words are refused (frame 258, below).
    ("ok. Please use only the standard library json module for this, with no "
     "new dependency.", {2, 3}, frozenset(), frozenset()),
    # m181 s343, "Ok, go ahead." on the batch line, is refused since frame
    # 258's pass 2: agreement alone admits no contest (below).
])
def test_words_that_name_no_line_refuse_nothing(words, contested, batch,
                                                asked):
    assert _refusal(words, contested, 3, batch, frozenset({1}), asked) is None


def test_a_range_of_notes_names_each_note():
    words = "Line 3 is wrong. Notes 8 to 11 are wrong too."
    assert _refusal(words, {3, 8, 9, 10, 11}, 11) is None
    assert _refusal(words, {3, 5, 8}, 11).startswith(
        "The words name lines 3 and 8 to 11 and do not name line 5.")


# Frame 258: a contest on a line no sentence names. Verbatim from the
# `rulings` table of `.rota/clickI_night150.db`.
M25 = ("Ok, this matches what I asked for. Please build it with the standard "
       "library json module only.")
M37 = ("Line 1 is wrong, because I never asked for anything to be built without "
       "Click. What I asked for is an echo_json helper inside Click, next to "
       "echo, that uses the standard library json module to print an object as "
       "compact JSON on one line, followed by a newline. Lines 2 through 5 come "
       "from that misreading, so please drop them.")
M316 = ("Lines 4 to 8 are wrong. They repeat the confirm() flag five times, and "
        "they should state what the version flag must do: the show_python flag "
        "adds the running Python version to the version message as "
        "major.minor.micro from sys.version_info. Line 1 also does not belong "
        "on this page, because I put the confirm() change aside until this "
        "change is merged.")


def test_m25s_contest_of_the_description_row_is_refused(db):
    """Night 150's m24 page: line 1 the request echo_json, line 2
    how_it_works, line 3 a note. m25 was ruled a contest of how_it_works,
    and the contested wake made the item json_only from his words. The
    `_request_page` fixture has the same three kinds of line."""
    with pytest.raises(ValueError) as e:
        _rule_request(db, M25, {"1": "approve", "2": "contest", "3": "approve"})
    assert str(e.value) == (
        "The words name no line and agree with the page, so their instruction "
        "is about the request, line 1. Approve line 2, and rule line 1 as the "
        "words say.")


@pytest.mark.parametrize("verb", ["contest", "revise"])
def test_m25s_instruction_lands_on_the_request_line(db, verb):
    out = _rule_request(db, M25, {"1": verb, "2": "approve", "3": "approve"})
    assert out["per_item"] == {"calculate_tip": verb, "how_it_works": "approve",
                               "l_1": "approve"}


@pytest.mark.parametrize("words", [
    # Night 121's m119 and night 139's m132, verbatim from the `rulings`
    # table of each night's db. One sentence agrees, and none follows it.
    "yes that all looks right, go ahead",
    "ok, this matches what I asked for, so go ahead.",
])
def test_a_plain_approval_lands_and_its_contest_is_refused(words):
    # Frame 258, pass 2: each reply contested a batch line on its night,
    # and agreement alone admits no contest. The approve call lands.
    assert _refusal(words, set(), 3, frozenset(), frozenset({1}),
                    frozenset({1})) is None
    assert _refusal(words, {2}, 3, frozenset(), frozenset({1}),
                    frozenset({1})) == (
        "The words agree with the page and name no line, so every line is "
        "approved. Approve lines 1 to 3.")


# Frame 258, pass 2, W1: agreement alone, verbatim from the `rulings` table
# of each night's db, with the lines the seat contested.
@pytest.mark.parametrize("words, contested, size, batch", [
    ("ok", {2, 3}, 3, frozenset()),                # night 151 m23, s106
    ("Ok, go ahead.", {3}, 3, frozenset({3})),     # night 147 m182, s343
    ("ok", {1}, 1, frozenset()),                   # night 138 m161, s296
])
def test_agreement_alone_admits_no_contest(words, contested, size, batch):
    out = _refusal(words, contested, size, batch, frozenset({1}),
                   frozenset({1}))
    assert out is not None and out.startswith(
        "The words agree with the page and name no line, so every line is "
        "approved.")


def test_m23s_contest_of_lines_2_and_3_is_refused(db):
    """Night 151's m22 page: line 1 the request echo_json, line 2
    how_it_works, line 3 a note. s106 ruled lines 2 and 3 contest on "ok",
    and the contested wakes cost 2 asks and 11 sessions. The
    `_request_page` fixture has the same three kinds of line."""
    with pytest.raises(ValueError) as e:
        _rule_request(db, "ok", {"1": "approve", "2": "contest",
                                 "3": "contest"})
    assert str(e.value) == ("The words agree with the page and name no line, "
                            "so every line is approved. Approve lines 1 to 3.")


def test_m23s_approve_call_lands(db):
    out = _rule_request(db, "ok", {"1": "approve", "2": "approve",
                                   "3": "approve"})
    assert set(out["per_item"].values()) == {"approve"}


# Frame 258, pass 2, W2: a line-1 contest under sentences about the batch.
# Verbatim from the `rulings` table of each night's db. Night 151's m45 page:
# line 1 the request echo_json, line 2 its criterion, line 3 bg_1.
M46 = ("Please don't drop this change. I'd rather you try again and fix the "
       "failing tests. Lines 2 and 3 now say what I want, and the fix should "
       "still use only the standard json module.")
ECHO_JSON = ("echo_json", "Add an echo_json(obj) helper next to echo that "
             "prints an object as compact JSON on one line, followed by a "
             "newline.")
M167 = ("Please don't give up on this change. Have the team fix the failing "
        "tests and keep going. Line 5 still lists the pager test file, and I "
        "asked to leave that file alone, so the work should touch only utils "
        "and the echo tests.")


def test_m46s_lines_2_and_3_match():
    # Frame 305, pass 2: "Lines 2 and 3 now say what I want" agrees. The
    # old reader faulted both lines on "should" and "still", which belong to
    # "the fix should still use only the standard json module".
    from rota.roles.api import _line_reading

    assert _line_reading(M46) == (set(), {2, 3})


@pytest.mark.parametrize("texts", [(), ECHO_JSON])
def test_m46s_contest_of_the_request_line_is_refused(texts):
    out = _refusal(M46, {1}, 3, frozenset({3}), frozenset({1, 2}),
                   frozenset({1}), texts)
    # Frame 305, review 2: the words fault no line and ask to keep the
    # change, so a line-1 contest would cancel what he asked to keep.
    assert out == ("The words do not fault line 1, and they ask to keep the "
                   "change. Approve line 1.")


# Night 151's m64, verbatim from `.rota/clickI.principal.jsonl`.
M64 = ("Please don't drop this change. Write the missing test for line 2 "
       "again: print a small dict and check that the output is exactly the "
       "compact JSON followed by one newline. Lines 2 and 3 say what I want, "
       "and the code should still use only the standard json module.")


@pytest.mark.parametrize("texts", [(), ECHO_JSON])
def test_m64s_contest_of_the_request_line_is_refused(texts):
    out = _refusal(M64, {1}, 3, frozenset({3}), frozenset({1, 2}),
                   frozenset({1}), texts)
    assert out == ("The words do not fault line 1, and they ask to keep the "
                   "change. Approve line 1.")


def test_m167s_contest_of_the_request_line_is_refused():
    # Night 144's m167 on m166: line 1 echo_json, line 5 bg_1's prediction.
    # The words fault line 5 only, a batch line. The caller reads no text
    # for a batch line, so the faulted texts hold one empty text.
    out = _refusal(M167, {1}, 5, frozenset({5}), frozenset({1, 2, 3, 4}),
                   frozenset({1}), ECHO_JSON, ("",))
    assert out is not None and "the words do not fault the request" in out


def test_m359s_contest_of_the_request_line_is_refused():
    """Night 143's m359 on m358 asks to keep the change, and line 5 takes
    the fault. The line-1 contest abandoned bg_6, the change that he asked
    to keep. Pass 2 asserted that the contest lands. Review 2 found that
    wrong, and frame 258's pass 3 review agreed
    (`plans/frame258-review-2.md`, point 6 and finding 2)."""
    words = ("Please keep going with a fix and don't drop this change. Line 5 "
             "is wrong because it still touches the Command class in core.py, "
             "and the flag belongs only to the version option in "
             "decorators.py. Keep the change there and add the Python version "
             "to the end of the message only when the flag is on.")
    show_python = ("version_option_show_python", "The `version_option` "
                   "includes a `show_python` flag that, when set to True, "
                   "causes the command to display the running Python version "
                   "in the message.")
    out = _refusal(words, {1}, 5, frozenset({5}), frozenset({1, 2, 3, 4}),
                   frozenset({1}), show_python)
    assert out == ("line 1: the words do not fault the request. They fault "
                   "line 5. Rule line 5 as the words say, and approve line 1.")


def test_m25s_words_with_a_batch_line_contested_are_still_refused():
    out = _refusal(M25, {2}, 3, frozenset(), frozenset({1}), frozenset({1}))
    assert out is not None and out.startswith("The words name no line")


def test_m28s_words_with_the_request_on_line_1_are_refused():
    # Night 147's m29 on m28: the words of night 150's m25, one night before.
    words = ("ok. Please use only the standard library json module for this, "
             "with no new dependency.")
    out = _refusal(words, {2, 3}, 3, frozenset(), frozenset({1}),
                   frozenset({1}))
    assert out is not None and out.startswith("The words name no line")
    assert "Approve lines 2 and 3, and rule line 1" in out


def test_words_that_name_a_line_by_a_word_are_left_alone():
    # Night 133's m68 named the batch line as "the pager tests" and wrote
    # "One small note". The door cannot read which line a word names.
    words = ("ok. One small note: the pager tests should not need any change "
             "for this helper, so leave them alone unless something there "
             "really breaks.")
    assert _refusal(words, {2}, 2, frozenset({2}), frozenset({1}),
                    frozenset({1})) is None


@pytest.mark.parametrize("batch_ruling, refused", [("contest", True),
                                                   ("approve", False)])
def test_m37s_contest_of_the_running_batch_line_is_refused(bg2, batch_ruling,
                                                          refused):
    """Night 150's m37 page: line 1 the request, lines 2 to 5 its criteria,
    line 6 batch_1, running with no commit. The words name lines 1 to 5,
    and the ruling contested batch_1 too, which cost an Architect relay.
    Night 136's page with a fourth criterion has the same shape."""
    from .test_request_page import ITEM_136, P, _dispatch, _reply, _verdict
    from .test_request_page import _landing as _land_session

    bg2.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                "('cr_4_extra', 'tk_1_confirm_with_default_on_eof', "
                "'A fourth criterion.')")
    bg2.execute("UPDATE batches SET status = 'running' WHERE id = 'bg_2'")
    (wake,) = P.REGISTRY["touch_note"].fn(bg2)
    mid = _dispatch(bg2, wake,
                    f'TOOL: msg.present_principal(refs=["bg_2", "{ITEM_136}"])')
    reply = _reply(bg2, mid, M37)
    ruling = {str(n): "contest" for n in range(1, 6)}
    ruling["6"] = batch_ruling
    out = _land_session(bg2, reply, ruling, M37)
    said = " ".join(out.errors)
    assert ("The words name lines 1 to 5 and do not name line 6." in said) \
        is refused, out.errors
    if not refused:
        _, ruled = _verdict(bg2, mid)
        assert ruled.get("bg_2") != "contest", ruled
        assert ruled.get(ITEM_136) == "contest", ruled


def test_m37s_words_spare_a_batch_line_only_with_files_or_tests():
    assert _refusal(M37, {1, 2, 3, 4, 5, 6}, 6, frozenset({6}),
                    frozenset({1, 2, 3, 4, 5})).startswith(
        "The words name lines 1 to 5 and do not name line 6.")
    assert _refusal(M37, {1, 2, 3, 4, 5}, 6, frozenset({6}),
                    frozenset({1, 2, 3, 4, 5})) is None


def test_m316s_contest_of_lines_3_and_9_is_refused():
    """Night 150's m316 page: lines 1 and 2 statements, line 3 the request
    json_only, lines 4 to 8 its criteria, line 9 how_it_works, lines 10 to
    12 the account. "They repeat ..." goes on about lines 4 to 8, so it
    spares no line. Before frame 258 the caller counted line 9 as an item
    line, so `item_lines` holds it here."""
    out = _refusal(M316, {1, 3, 4, 5, 6, 7, 8, 9}, 12, frozenset(),
                   frozenset(range(3, 10)))
    assert out is not None and out.startswith(
        "The words name lines 1 and 4 to 8 and do not name lines 3 and 9.")
    assert _refusal(M316, {1, 4, 5, 6, 7, 8}, 12, frozenset(),
                    frozenset(range(3, 10))) is None


def _refs(words: str) -> list[set[int]]:
    from rota.roles.api import _LINE_REF, _ref_lines

    return [_ref_lines(r) for r in _LINE_REF.finditer(words)]


def test_a_range_on_the_last_number_reads_as_a_range():
    # Night 154, s334's turn 1, the principal's words of m175 and m176. The
    # reader read lines 6, 7 and 10, so the unnamed-contest door refused
    # s334's ruling of lines 11 to 14 (frame 282).
    m175 = ("Notes 6, 7 and 10 to 14 have nothing to do with this change, so "
            "leave that code alone.")
    m176 = ("Please remove lines 6, 7 and 10 to 14 from the page, because "
            "they have nothing to do with this change.")
    want = {6, 7, 10, 11, 12, 13, 14}
    assert _refs(m175) == [want]
    assert _refs(m176) == [want]


def test_a_range_after_a_list_reads_as_a_range():
    # Night 133's m304 and night 142's m291 hold the same shape (frame 282).
    assert _refs("lines 2, 3 and 5 to 7 are wrong") == [{2, 3, 5, 6, 7}]
    assert _refs("lines 5, 6 and 8 through 11 are wrong") == [
        {5, 6, 8, 9, 10, 11}]


def test_a_range_in_the_middle_of_a_list_reads_as_a_range():
    assert _refs("lines 1 to 3, 5 and 8 are fine") == [{1, 2, 3, 5, 8}]
    assert _refs("lines 1-3, 5 and 8 are fine") == [{1, 2, 3, 5, 8}]


def test_an_en_dash_is_a_range_word():
    assert _refs("lines 2, 4\u20136 are fine") == [{2, 4, 5, 6}]


def test_a_range_ends_at_the_page_s_last_line():
    # A range past the page faulted lines the words never named, and "3 to
    # 2026" read 2024 lines (frame 282, review 1, finding 2).
    from rota.roles.api import _line_reading

    assert _line_reading("lines 2 and 3 to 2026 are wrong", 14) == (
        set(range(2, 15)), set())


# Frame 258, pass 3: night 155's line-1 contests under a reply whose first
# sentence names the batch line. Verbatim from `rulings` r_ecf6706174,
# r_c797b602d8 and r_6c141a0f5c of `.rota/clickI_night155.db`. Each contest
# cancelled a live batch (`plans/night155-read.md`, section 3).
M62 = ("Line 3 is still wrong. echo_json is a new function next to echo, so "
       "the work should only add it to utils.py and add new tests in the echo "
       "test file. It shouldn't change echo itself, the pager, the testing "
       "pause code or the pager tests. Line 2 is fine.")
M93 = ("Line 5 is still wrong. It should only add echo_json next to echo in "
       "utils.py and add new tests in the echo test file, and it should not "
       "touch echo itself, the pager, the testing pause code or the pager "
       "tests. Lines 2, 3 and 4 are fine.")
M179 = ("On line 5, tests/test_utils.py is not a new file, because it already "
        "exists and already holds the echo tests. The new tests go into that "
        "existing file. The list should also name src/click/utils.py, because "
        "the new function goes there next to echo.")
ECHO_JSON_TESTS = ("echo_json_tests", "Put the new tests in the utils test "
                   "file, where the existing echo tests already live, and "
                   "leave every other test file alone.")


@pytest.mark.parametrize("words, contested, size, batch, items, texts, line", [
    # s158 on m61: line 1 echo_json, line 2 its criterion, line 3 bg_2.
    (M62, {1, 3}, 3, {3}, {1, 2}, ECHO_JSON, 3),
    # s193 on m92: line 1 echo_json, lines 2 to 4 criteria, line 5 bg_3.
    (M93, {1, 5}, 5, {5}, {1, 2, 3, 4}, ECHO_JSON, 5),
    # s283 on m178: line 1 echo_json_tests, lines 2 to 4 criteria, line 5
    # bg_4, ruled revise by s283.
    (M179, {1, 5}, 5, {5}, {1, 2, 3, 4}, ECHO_JSON_TESTS, 5),
], ids=["m62", "m93", "m179"])
def test_night155s_contest_of_the_request_line_is_refused(
        words, contested, size, batch, items, texts, line):
    # The faulted line is the batch line, so the caller passes its empty
    # text. Line 2 of m62 is fine, so no criterion is faulted.
    out = _refusal(words, contested, size, frozenset(batch), frozenset(items),
                   frozenset({1}), texts, ("",))
    assert out == (f"line 1: the words do not fault the request. They fault "
                   f"line {line}. Rule line {line} as the words say, and "
                   f"approve line 1.")


QUIET = ("quiet_flag", "Add a quiet flag so the command doesn't print "
         "anything, and don't write the log.")


@pytest.mark.parametrize("sentence, texts, line", [
    # A sentence about the batch that names tests, beside a fault of the
    # batch line. The files rule skips it before `_names_request` runs, so
    # the case proves the files rule and not the build-verb branch (pass 3b
    # review, finding 3).
    ("Please make sure the tests pass.", ECHO_JSON, 3),
    # A build verb opens a sentence about the batch (review 2, finding 1).
    # The build-verb branch still spares line 1 there.
    pytest.param("Please make sure it works.", ECHO_JSON, 2,
                 marks=pytest.mark.xfail(strict=True, reason=(
                     "held by frame 344: residue: a build verb at the start of a sentence about "
                     "the batch spares line 1 (review 2, finding 1; pass 3b "
                     "review, finding 3)")), id="build_verb"),
    # The sentence names the request's subject and asks to keep the change
    # (review 2, finding 2).
    ("Please don't drop the JSON change.", ECHO_JSON, 2),
    # The same with a curly apostrophe (pass 3 review, finding 3).
    ("Please don’t drop the JSON change.", ECHO_JSON, 2),
    # A reply that asks to keep the request (pass 3 review, finding 4). The
    # keep rule leaves "change" out, because "Do not change echo itself" is
    # a files correction and the rule reads the whole reply.
    pytest.param("Don't change the echo_json helper.", ECHO_JSON, 2,
                 marks=pytest.mark.xfail(strict=True, reason=(
                     "held by frame 344: residue: \"don't change\" takes the object the sentence "
                     "names, so the keep rule cannot read it (pass 3b review, "
                     "finding 1)")), id="dont_change"),
    # The token "don" from "don't" in the reply and the request text
    # (review 2, finding 3).
    ("Please don't stop now.", QUIET, 2),
], ids=["tests_word", "build_verb", "subject", "curly", "dont_change", "don"])
def test_a_sentence_about_the_batch_does_not_let_line_1_be_contested(
        sentence, texts, line):
    # The m46 page: line 1 the request, line 2 its criterion, line 3 bg_1.
    out = _refusal(f"{sentence} Line {line} is wrong.", {1, line}, 3,
                   frozenset({3}), frozenset({1, 2}), frozenset({1}), texts)
    assert out == (f"line 1: the words do not fault the request. They fault "
                   f"line {line}. Rule line {line} as the words say, and "
                   f"approve line 1.")


def test_a_keep_sentence_anywhere_in_the_reply_refuses_line_1():
    # The keep sentence comes first, and a later sentence names the request
    # (pass 3 review, finding 2).
    words = ("Please keep going. Line 2 is wrong. The echo_json helper "
             "should print compact JSON.")
    out = _refusal(words, {1, 2}, 3, frozenset({3}), frozenset({1, 2}),
                   frozenset({1}), ECHO_JSON)
    assert out is not None and "the words do not fault the request" in out


@pytest.mark.parametrize("words", [
    # The m263 shape on a page with a batch line: the sentence names no file.
    "Line 3 is wrong. Also, print the JSON with sorted keys.",
    # The four corrections of the pass 3 review, finding 1.
    "Line 3 is wrong. Also, the echo_json helper must write to a file, not "
    "stdout.",
    "Line 2 is wrong. Also, the helper should take a file argument.",
    # A "do not change" sentence beside a correction (pass 3b review,
    # finding 1).
    "Line 3 is wrong. Do not change echo itself. Print the JSON with sorted "
    "keys.",
    pytest.param(
        "Line 3 is wrong. Also, add tests for echo_json with sorted keys.",
        marks=pytest.mark.xfail(strict=True, reason=(
            "held by frame 344: residue: the files rule swallows a sentence that names tests "
            "when the batch line is faulted (pass 3 review, finding 1)"))),
    pytest.param(
        "Line 3 is wrong. The helper should go in utils.py and print JSON "
        "with sorted keys.",
        marks=pytest.mark.xfail(strict=True, reason=(
            "held by frame 344: residue: the files rule swallows a sentence that names a .py "
            "path when the batch line is faulted (pass 3 review, finding "
            "1)"))),
], ids=["sorted_keys", "write_to_a_file", "file_argument", "do_not_change",
        "add_tests", "utils_py"])
def test_a_correction_of_the_request_beside_a_fault_lets_line_1_be_contested(
        words):
    faulted = 2 if words.startswith("Line 2") else 3
    assert _refusal(words, {1, faulted}, 3, frozenset({3}),
                    frozenset({1, 2}), frozenset({1}), ECHO_JSON) is None
