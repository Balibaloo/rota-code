"""
F25: the calls a mode offers against the doors that refuse them.

The audit of 2026-10-27, F25: `sandbox.follow` sent each offer through the
real doors and never checked that the seat's mode holds the offered call.
A refusal that names a call outside `api._offer` was never followed at all.
Frame 135's law: a refusal names only a call the doors admit.

The two cases of the `_stray_act_fields` door come from the gate on
9827e38a: its offer left lines with no ruling, and on the page that orders
requests it kept a verdict that page refuses.
"""
from __future__ import annotations

import json
import re

import pytest

from rota import paths
from rota.core import sandbox
from rota.core.db import init_db
from rota.llm.llm import Completion, Pins
from rota.roles import api
from rota.testkit import fixtures


# --- the offer of the stray act fields, on the two cases of the gate -------

class _Follower:
    """A scripted seat: it sends `first`, then the offered call that `pick`
    takes from the refusal of the turn before."""

    name = "follower"
    misses = 0

    def __init__(self, first: str, pick):
        self.first, self.pick, self.users = first, pick, []

    def complete(self, system, user, pins, tools=None):
        self.users.append(user)
        if len(self.users) == 1:
            text = self.first
        elif len(self.users) == 2:
            text = "TOOL: " + self.pick(_offered_calls(_last_error(user)))
        else:
            text = "Done."
        return Completion(text=text, pins=pins, backend=self.name)


def _last_error(user: str) -> str:
    lines = [ln for ln in user.splitlines() if ln.startswith("ERROR ")]
    assert lines, user[-2000:]
    return lines[-1]


def _offered_calls(text: str) -> list[str]:
    """Each `rulings.rule(...)` call of a refusal, with its brackets
    balanced and its JSON strings skipped."""
    out, start = [], 0
    while (at := text.find("rulings.rule(", start)) >= 0:
        depth, quoted, i = 0, False, at + len("rulings.rule")
        while i < len(text):
            ch = text[i]
            if quoted:
                if ch == "\\":
                    i += 1
                elif ch == '"':
                    quoted = False
            elif ch == '"':
                quoted = True
            elif ch in "({[":
                depth += 1
            elif ch in ")}]":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        out.append(text[at:i + 1])
        start = i + 1
    return out


def _case(case_id: str) -> dict:
    case = next(c for c in fixtures.load_case(paths.CASES / "l1_landing.yaml")
                if c["id"] == case_id)
    return fixtures.for_run(case, 1)


def _run(case: dict, seat, tmp_path):
    return fixtures.run_case(case, tmp_path / "c.db", seat,
                             pins=Pins(model="scripted"),
                             instructions=fixtures.instructions_for(case))


def test_the_offer_of_stray_fields_records_no_call_for_a_faulted_line(db):
    """The door records no offer when his words fault a line the map left
    out, so the follower holds no call the next door refuses."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
               "verb, body_text, seq) VALUES ('m1', 'm1', 'principal', "
               "'liaison', 'converse', 'please drop line 3, and line 2 is "
               "wrong too', 1)")
    sb = sandbox.build("liaison", db, mode="landing")
    sb.ctx.trigger = "m1"
    sb.ctx.offers = []
    said = api._stray_act_fields(
        sb.ctx, {"3": "contest", "act": "drop"}, "", ["a", "b", "c"])
    assert "Line 2 also has no ruling" in said, said
    assert sb.ctx.offers == [], sb.ctx.offers


SEPARATE = ("They're independent. The confirm change is a separate request "
            "I'll take up on its own, so leave it out of this one. This change "
            "only adds an optional flag to the version option, off by default, "
            "that puts the running Python version from the interpreter's "
            "version info, written as major.minor.micro, at the end of the "
            "version message.")


def _shift_first(verdict: str) -> str:
    return (f'TOOL: rulings.rule(rulings={{"1": "{verdict}", "act": "drop"}}, '
            f'words={json.dumps(SEPARATE)})')


def test_stray_fields_against_his_shift_word_get_no_call(tmp_path):
    """L1-LI-a-separate-request-is-later: the seat sent contest with the act
    drop, and his words say "a separate request". The land gate of
    2bbace14, run 5: the seat took the drop offer of three. The refusal now
    names his word and the page's map, and shows no call (law 6)."""
    calls = []

    def pick(found):
        calls.extend(found)
        return "Done."

    seat = _Follower(_shift_first("contest"), pick)
    _run(_case("L1-LI-a-separate-request-is-later"), seat, tmp_path)
    error = _last_error(seat.users[1])
    assert "His words say 'separate'" in error, error
    assert calls == [], calls


def test_stray_fields_with_no_shift_word_in_his_reply_get_three_calls(db):
    """A reply with no shift word leaves the choice open: the refusal shows
    later, now and drop, each with its meaning, and picks none."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
               "verb, body_text, seq) VALUES ('m1', 'm1', 'principal', "
               "'liaison', 'converse', 'They are independent.', 1)")
    sb = sandbox.build("liaison", db, mode="landing")
    sb.ctx.trigger, sb.ctx.offers = "m1", []
    api._stray_act_fields(sb.ctx, {"1": "contest", "act": "drop"}, "w",
                          ["a"], shift=True)
    assert [o.args["rulings"] for o in sb.ctx.offers] == [
        {"1": "later"}, {"1": "now"}, {"1": "drop"}]


def test_a_later_with_no_words_lands_on_his_reply(tmp_path):
    """The land gate of 2bbace14, runs 1, 2 and 4: the seat sent later with
    his words in acts and no words, and the bare words door moved it off
    later. Since F2 pass 2 the door reads his reply, whole, when the call
    passes no words, so the first call lands as park with no offer. Frame
    345's pass 2 refuses the flat `acts` map, so the call is one word."""
    first = 'TOOL: rulings.rule(rulings={"1": "later"})'
    calls = []

    def pick(found):
        calls.extend(found)
        return found[0]

    seat = _Follower(first, pick)
    r = _run(_case("L1-LI-a-separate-request-is-later"), seat, tmp_path)
    assert calls == [], calls
    assert r.passed, r.problems


def test_a_now_with_no_words_gets_no_call_against_separate(tmp_path):
    """The seat's now does not mean what "separate" means, so the words
    door shows no call (law 6)."""
    calls = []

    def pick(found):
        calls.extend(found)
        return "Done."

    seat = _Follower('TOOL: rulings.rule(rulings={"1": "now"})', pick)
    _run(_case("L1-LI-a-separate-request-is-later"), seat, tmp_path)
    assert calls == [], calls


def test_a_shift_word_beside_stray_fields_is_offered_alone(tmp_path):
    """A seat that gave the shift page's own word keeps it: the offer drops
    the act's fields and names no other verdict."""
    calls = []

    def pick(found):
        calls.extend(found)
        return found[0]

    seat = _Follower(_shift_first("later"), pick)
    r = _run(_case("L1-LI-a-separate-request-is-later"), seat, tmp_path)
    assert len(calls) == 1 and '{"1": "later"}' in calls[0], calls
    assert r.passed, r.problems


def test_a_shift_word_is_read_by_the_word_door_match(tmp_path):
    """"later please" is later by the first-word match of `_ruling_word`,
    so the offer names later alone (the review of f4951389, finding 4)."""
    calls = []

    def pick(found):
        calls.extend(found)
        return found[0]

    seat = _Follower(_shift_first("later please"), pick)
    r = _run(_case("L1-LI-a-separate-request-is-later"), seat, tmp_path)
    assert len(calls) == 1 and '{"1": "later"}' in calls[0], calls
    assert r.passed, r.problems


NIGHT171 = ("Later for line 1: put the screen-clearing change aside until the "
            "docstring example is merged, then pick it up again. I still want "
            "it, so please do not drop it.")


def test_acts_on_the_shift_page_is_refused_with_the_one_word_form(tmp_path):
    """Night 171's s200, after m88: the call kept approve and keep in
    `acts`. Frame 345's pass 2 removed the flat `acts` map, so the door now
    refuses it with one sentence that names the one-word form, and it
    offers no call (law 6). The shift door of pass 1c went with the map."""
    case = _case("L1-LI-a-separate-request-is-later")
    case["inbound"]["body_text"] = NIGHT171
    # The case's own expectations read its own words, not his.
    case["expect"], case["forbidden"] = {}, {}
    first = ('TOOL: rulings.rule(rulings={"1": "later"}, acts={"1": '
             '{"verdict": "approve", "act": "keep", "target_kind": "request", '
             '"words": "Make clear() return True when it cleared the screen '
             'and False when stdout is not a terminal."}})')
    calls = []

    def pick(found):
        calls.extend(found)
        return found[0] if found else "Done."

    seat = _Follower(first, pick)
    _run(case, seat, tmp_path)
    error = _last_error(seat.users[1])
    assert "rulings.rule takes no acts" in error, error
    assert calls == [], calls


def test_a_question_back_beside_stray_fields_keeps_its_own_call(db):
    """`ask` on the shift page is a question back. The refusal offers the
    ask call and no verdict (the review of f4951389, finding 4)."""
    sb = sandbox.build("liaison", db, mode="landing")
    sb.ctx.offers = []
    said = api._stray_act_fields(sb.ctx, {"1": "ask", "act": "drop"}, "",
                                 ["a"], shift=True)
    assert 'rulings.rule(ask="<one sentence about line 1>")' in said, said
    assert [(o.op, o.args) for o in sb.ctx.offers] == [
        ("rulings.rule", {"ask": "<one sentence about line 1>"})]


# --- the follower checks the seat's mode -----------------------------------

@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _offer_of(op: str, said: str):
    return api.Offer(op, {"refs": ["x1"]}, (), (), said)


def test_an_offer_outside_the_mode_fails_the_follower(db):
    """The landing mode holds `rulings.rule` and `rulings.line`. The
    Liaison's graph holds its sends too, so the dry run alone admits a send
    that the landing seat never sees."""
    sb = sandbox.build("liaison", db, mode="landing")
    said = "Send msg.converse_principal with the row."
    exc = ValueError(f"rulings.rule: {said}")
    [rec] = sandbox.follow(sb, "rulings.rule", {}, exc,
                           [_offer_of("msg.converse_principal", said)])
    assert rec["mode"] == "landing"
    assert rec["not_in_mode"] == ["msg.converse_principal"]
    from .conftest import _problems
    [line] = [p for p in _problems("t", [rec]) if "does not hold" in p]
    assert "msg.converse_principal" in line and "'landing'" in line
    assert line.startswith(f"door {rec['door']}:")


def test_an_offer_inside_the_mode_passes_the_mode_check(db):
    sb = sandbox.build("liaison", db, mode="landing")
    said = "Send rulings.rule with every line."
    [rec] = sandbox.follow(sb, "rulings.rule", {}, ValueError(said),
                           [_offer_of("rulings.rule", said)])
    assert rec["not_in_mode"] == []


def test_an_offer_of_the_refused_op_is_held(db):
    """The runtime refuses an op outside the seat's list before any door,
    so an offer of the refused op is held. The sandbox here keys `deliver`,
    which lacks `ledger.log` (the review of f4951389, finding 2)."""
    sb = sandbox.build("terminologist", db, mode="deliver")
    mode, held = sandbox.held_calls(sb)
    assert "ledger.log" not in held, (mode, sorted(held))
    said = "Send ledger.log with the row."
    [rec] = sandbox.follow(sb, "ledger.log", {}, ValueError(said),
                           [api.Offer("ledger.log", {}, (), (), said)])
    assert rec["not_in_mode"] == []


def test_a_skipped_offer_is_still_held_to_the_mode(db):
    """`code.commit` never reaches the doors of a dry run, so only the mode
    check reads it."""
    sb = sandbox.build("developer", db, mode="reopen")
    mode, held = sandbox.held_calls(sb)
    assert "code.commit" not in held, (mode, sorted(held))
    said = "Send code.commit."
    [rec] = sandbox.follow(sb, "code.write", {}, ValueError(said),
                           [api.Offer("code.commit", {"message": "m"}, (), (),
                                      said)])
    assert rec["skipped"] and rec["not_in_mode"] == ["code.commit"]


# --- the lint over the refusal texts that name a call ----------------------

from . import _refusal_calls as lint  # noqa: E402

# The named calls that break frame 135's law today, by the static reading.
# One line each: the door, the call, and the modes that meet the text and
# do not hold the call. The lint reads the three guard forms of
# `_refusal_calls`. Its limits: it does not read a guard inside a helper,
# for example `_escalation_admitted`, or a flag that the code arms outside
# `sandbox.build`. It reads `if "x.y" not in held:` around a text as a
# guard, which is the wrong polarity. The two cases of `_stray_act_fields` name
# `rulings.rule`, which their mode holds, so the lint passes them, and the
# follower caught their arguments.
KNOWN_UNHELD = {
    "glossary_amend:surveys.attest":
        "terminologist/answer and deliver hold glossary.amend, not surveys.attest",
    "surveys_attest:problem.assert":
        "seven survey modes hold surveys.attest, not problem.assert",
    "tests_encode:schedule.reask":
        "tester/challenge and tests_missing hold tests.encode, not schedule.reask",
    "tests_encode:ledger.log":
        "tester/challenge holds tests.encode, not ledger.log",
    "ledger_log:surveys.attest":
        "22 modes hold ledger.log, not surveys.attest",
    "_revert_refusal:msg.challenge_tester":
        "5 developer modes hold code.commit, not msg.challenge_tester",
    "_revert_refusal:msg.escalate_architect":
        "4 developer modes hold code.commit, not msg.escalate_architect",
}


def _keys() -> list[str]:
    return sorted({n.key for n in lint.named_calls()})


@pytest.mark.parametrize("key", [
    pytest.param(k, marks=pytest.mark.xfail(strict=True, reason=KNOWN_UNHELD[k]))
    if k in KNOWN_UNHELD else k for k in _keys()])
def test_a_refusal_names_a_call_its_modes_hold(key):
    """Each `artefact.verb(` that a refusal text of `api.py` or the sandbox
    names exists, and every mode that can meet the text holds it."""
    assert key not in lint.findings(), lint.findings()[key]


def test_the_table_names_only_keys_the_lint_reads():
    assert set(KNOWN_UNHELD) <= set(_keys())
