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
    assert "Line 1 is the request" in text
    assert text.startswith("The words fault lines 2 and 3.")
    assert "Rule lines 2 and 3, and approve the rest." in text


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
    with pytest.raises(ValueError, match="Line 1 is the request"):
        _rule_request(db, words, {"1": "contest", "2": "contest", "3": "approve"})


def test_a_quote_of_line_1_inside_the_door_lets_it_be_contested(db):
    with pytest.raises(ValueError, match="Line 1 is the request"):
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
    words = "Lines 1 to 4 match what I asked for."
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
    "144 m236": ("Line 12 is wrong: I never overruled the helper. I still want it "
                 "added next to echo, and my note about line 1 was only about which "
                 "test files it points at. On line 1, the echo tests are right, but "
                 "the termui and context test files don't belong there.",
                 {"1": "contest", "2": "approve", "3": "approve"}),
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
             item_lines=frozenset({1, 2, 3, 4})):
    """The door's reading of a page of `size` lines that opens with a request
    item, as `rulings_rule` calls it. Lines 1 to 4 are the request and its
    criteria on m131's and m65's pages."""
    from rota.roles.api import _line_reading, _line_refusal

    faulted, matched = _line_reading(words)
    return _line_refusal(words, set(contested), faulted, matched, size, True,
                         False, frozenset(batch_lines), frozenset(item_lines))


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
    # Night 146's words: "Please drop note 8. Note 9 is fine." The reader
    # reads a cue after a reference only, so "drop note 8" takes no direction.
    assert _line_reading("Please drop note 8. Note 9 is fine.") == (set(), {9})
    assert _line_reading("Notes 5 to 6 are fine.") == (set(), {5, 6})


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


def test_an_unnumbered_sentence_spares_a_criterion_line(db):
    # m263's shape: a numbered fault and an unnumbered correction. The
    # contest of the unnamed criterion line 4 lands.
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


@pytest.mark.parametrize("words, contested, batch", [
    # m28 s112: no line reference, so the words name nothing.
    ("ok. Please use only the standard library json module for this, with no "
     "new dependency.", {2, 3}, frozenset()),
    # m181 s343: a bare agreement and a contest of the batch line.
    ("Ok, go ahead.", {3}, frozenset({3})),
])
def test_words_that_name_no_line_refuse_nothing(words, contested, batch):
    assert _refusal(words, contested, 3, batch, frozenset({1})) is None


def test_a_range_of_notes_names_each_note():
    words = "Line 3 is wrong. Notes 8 to 11 are wrong too."
    assert _refusal(words, {3, 8, 9, 10, 11}, 11) is None
    assert _refusal(words, {3, 5, 8}, 11).startswith(
        "The words name lines 3 and 8 to 11 and do not name line 5.")
