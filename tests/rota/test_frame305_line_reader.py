"""
A fault cue binds to the subject of a relating clause, and the re-present
names the principal's own line or none.

Night 158 (frame 305): m105 said "Line 7 just repeats line 3 ... so drop it".
`_line_cues` gave the drop to line 3, the repeated line, and frame 250's door
forced a contest of line 3. The re-present of m122 then told him his words
about line 1 made no ruling, and his words named no line. Both texts are
build designs, frames 234 and 267 (`plans/frame305-provenance.md`).
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.roles.api import _line_cues
from rota.roles.principal import returned_line


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


# Night 158's m105, verbatim from `messages` of `.rota/clickI_night158.db`.
M105 = ("Line 2 is wrong because Click has no options file: the version option "
        "lives in the decorators file, so the change belongs there, with its "
        "tests in the options tests. Line 8 needs one more detail: take the "
        "Python version from the running interpreter's version info and write "
        "it as major.minor.micro. Line 7 just repeats line 3 and isn't really an "
        "assumption, so drop it.")


def test_m105s_drop_lands_on_the_repeating_line():
    faulted, _ = _line_cues(M105)
    assert faulted[7][0] == "drop"
    assert 3 not in faulted
    assert faulted[2][0] == "wrong"


def test_a_drop_before_the_reference_lands_on_that_reference():
    faulted, _ = _line_cues("Drop line 3, because it repeats line 7.")
    assert faulted[3][0].lower() == "drop"
    assert 7 not in faulted


def test_two_references_with_no_relating_verb_keep_todays_reading():
    faulted, matched = _line_cues("Line 2 is fine but line 3 is wrong.")
    assert set(faulted) == {3}
    assert faulted[3][0] == "wrong"
    assert matched == {2}


# The other relating sentences of `plans/frame305-provenance.md`, section 5,
# verbatim from `messages` of each night's database.
@pytest.mark.parametrize("words, repeating, repeated", [
    # night 140, m56
    ("Lines 3 and 7 are wrong: Click's core code builds the command-line "
     "interface and parses the arguments and options, then runs the matching "
     "function. Please drop those two claims. Line 4 repeats line 2, so please "
     "remove it, and the other lines are fine.", 4, 2),
    # night 142, m7
    ("Line 41 repeats line 37 word for word, so please drop it. The rest reads "
     "fine to me.", 41, 37),
    # night 147, m87
    ("Line 6 needs to say that the flag defaults to False, so nothing changes "
     "for people who already call confirm(). Line 7 just repeats line 2 and "
     "isn't really an assumption, so you can drop it.", 7, 2),
])
def test_each_drop_lands_on_the_repeating_line(words, repeating, repeated):
    faulted, _ = _line_cues(words)
    assert repeating in faulted
    assert repeated not in faulted


def _returned_page(db, note: str, reply: str) -> str:
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status, unresolved_note) VALUES "
               "('m122','t9','liaison','principal','present','[]',122,'open',?)",
               (note,))
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
               "to_role, verb, body_text, seq, status) VALUES "
               "('m123','m122','t9','principal','liaison','converse',?,123,"
               "'answered')", (reply,))
    db.commit()
    return returned_line(db, "m122")


NO_LINE = ("Your last answer to this page did not reach the team. The team "
           "could not turn your words into a ruling. Answer the page again, "
           "and say for each line you want changed what to do with it.")


def test_m122s_re_present_names_no_line(db):
    # Night 158's m122 note and m123 reply, verbatim.
    line = _returned_page(
        db,
        "m123: rulings.rule: The words name no line and agree with the page, "
        "so their instruction is about the request, line 1. Approve line 2, "
        "and rule line 1 as the words say.",
        "Ok, I approve this page. Please remember that the flag is off by "
        "default, and the version comes from the running interpreter's version "
        "info, written as major.minor.micro after the word \"Python\".")
    assert line == NO_LINE


def test_a_reply_that_names_one_line_gets_that_line(db):
    line = _returned_page(
        db, "m123: rulings.rule: The words name line 2 and do not name line 5.",
        "Line 4 is wrong, the flag is off by default.")
    assert "about line 4 into a ruling" in line
    assert "line 2" not in line and "line 5" not in line


def test_a_reply_that_names_two_lines_gets_no_number(db):
    line = _returned_page(
        db, "m123: rulings.rule: The words do not name line 5.",
        "Lines 2 and 4 are wrong.")
    assert line == NO_LINE


def test_the_re_present_reads_a_bare_number_after_a_full_stop(db):
    # Review 1, finding 1: the reader of `rulings.rule` names lines 2 and 3.
    line = _returned_page(
        db, "m123: rulings.rule: The words do not name line 5.",
        "Line 2 is fine. 3 is wrong.")
    assert line == NO_LINE


def test_a_negated_cue_faults_no_line():
    # Review 1, finding 2: his words keep both lines.
    faulted, _ = _line_cues("Line 7 repeats line 3, but do not drop it.")
    assert faulted == {}


def test_a_verb_with_its_own_object_makes_no_pair():
    # Review 1, finding 8: night 142's m102, verbatim from `messages` of
    # `.rota/clickI_night142.db`. "repeat" takes "what I asked for".
    faulted, _ = _line_cues(
        "Lines 8 to 14 repeat what I asked for, so they are not assumptions, "
        "and line 1 should point only at the echo tests, not the termui or "
        "context tests.")
    assert faulted[1][0] == "should"


def test_both_binds_the_cue_to_the_relating_pair():
    # Review 1, finding 3: his words fault lines 3 and 7.
    faulted, _ = _line_cues("Line 7 repeats line 3, so drop both.")
    assert set(faulted) == {3, 7}
    assert faulted[3][0] == faulted[7][0] == "drop"


# Pass 2: the reader is inverted. An agreement first in the clause matches
# its line, and any other clause with a verb faults it. Night 159's m117,
# m118 and m185, verbatim from `messages` of `.rota/clickI_night159.db` and
# from `.rota/clickI.principal.jsonl`.
M117 = ("Line 7 should go, because confirm has no option or sentinel. Lines 3, "
        "4 and 6 are off: confirm aborts today and doesn't raise a usage error, "
        "and its default is true or false, not \"yes\". The line 8 check needs "
        "prompt text like \"Continue?\" with a default of true, and I already "
        "answered line 14 earlier.")
M118 = ("Please delete line 7, since confirm has no option or sentinel, and "
        "delete line 14, since I already said to use the prompt text "
        "\"Continue?\" and to return confirm's own default when the flag is on "
        "and stdin is closed. In lines 3 and 4, replace \"raises a usage error\" "
        "with \"aborts\", because that is what confirm does today when stdin "
        "closes and the flag is off. In lines 6 and 8, change the checks so they "
        "pass the prompt text \"Continue?\" and a default of true instead of "
        "\"yes\", and give the fake stdin a way to read a line so the checks can "
        "run.")
M185 = ("I want this fixed, not dropped. The test on line 2 is right and should "
        "stay as it is: with the flag off, the command should exit cleanly and "
        "print the same version message as today. The failing exit shows the "
        "new flag breaks the plain case, so make the flag off by default and "
        "change the message only when it is on, with the full major.minor.micro "
        "Python version from sys.version_info.")


@pytest.mark.parametrize("words, faulted, matched", [
    (M118, {3, 4, 6, 7, 8, 14}, set()),
    (M117, {3, 4, 6, 7, 8, 14}, set()),
    (M185, set(), {2}),
    (M105, {2, 7, 8}, set()),
    ("Line 2 is right, but line 3 is wrong.", {3}, {2}),
    # A verb directly before the reference governs it, as "delete line 7"
    # does. His m117 asks for line 14 to go for this reason.
    ("I already answered line 14 earlier.", {14}, set()),
    ("See line 3.", set(), set()),
    ("Write the check as in line 2.", set(), set()),
    ("Line 3 is not wrong.", set(), {3}),
    ("Keep line 3.", set(), {3}),
    ("Do not change line 3.", set(), set()),
])
def test_the_inverted_reader(words, faulted, matched):
    cues, got = _line_cues(words)
    assert (set(cues), got) == (faulted, matched)


def test_each_fault_names_the_verb_that_governs_it():
    cues, _ = _line_cues(M118)
    assert cues[7][0] == cues[14][0] == "delete"
    assert cues[3][0] == cues[4][0] == "replace"
    assert cues[6][0] == cues[8][0] == "change"
    cues, _ = _line_cues(M117)
    assert cues[14][0] == "answered"


# The recorded replies of nights 140 to 159 that the first draft of the
# inverted reader misread, verbatim or cut to the sentence that names the
# lines (`.rota/clickI.principal.jsonl`).
@pytest.mark.parametrize("words, faulted, matched", [
    # night 159, m212: the verb before line 3 governs line 3 only.
    ("Lines 1, 2 and 4 are fine as they are, but please rewrite line 3.",
     {3}, {1, 2, 4}),
    # night 158, m89: a keep with a correction after it faults the line.
    ("Keep line 4, but fix its check so it fakes a closed input properly.",
     {4}, set()),
    # night 142, m290: the possessive is no verb.
    ("Line 2's check crashes before it tests anything.", {2}, set()),
    # night 140, m142: a line in a reason clause takes no direction.
    ("Please remove it, since line 1 now says the flag is off by default.",
     set(), {1}),
    # night 145, m11: a line in an object phrase takes no direction.
    ("Line 4 is wrong because it just repeats the summary from line 1 and "
     "calls it a quote from the README and the code.", {4}, set()),
    # night 144, m19: the object of a relating verb with no line subject.
    ("Each of them either repeats line 1 or pastes a README sentence next to "
     "an unrelated line.", set(), set()),
    # night 149, m57: a question asks and does not instruct.
    ("And what does line 3 mean by \"assumes name\"?", set(), set()),
    # night 142, m128: "keep only" asks for a cut.
    ("Lines 10 and 11 should keep only their first sentence.", {10, 11},
     set()),
    # night 151, m177: "never" after the reference describes the line.
    ("Lines 2 and 3 never turn the flag on.", {2, 3}, set()),
    # night 158, m122: "including" points at the line.
    ("Ok, I approve the page and every line on it stays as written, "
     "including line 1.", set(), set()),
])
def test_the_inverted_reader_on_recorded_replies(words, faulted, matched):
    cues, got = _line_cues(words)
    assert (set(cues), got) == (faulted, matched)
