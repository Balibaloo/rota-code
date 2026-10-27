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


DROP_WORDS = "please drop line 3, the rest is fine"


def test_the_offer_of_stray_fields_carries_every_line_of_the_page(tmp_path):
    """L1-LI-a-dropped-line-is-a-contest: the seat sent line 3 alone with
    the act's fields beside it. The offer moved the fields into line 3 and
    left lines 1 and 2 with no ruling, so the next door refused it. The
    offer now gives a line the reply does not contest its approve."""
    first = ('TOOL: rulings.rule(rulings={"3": "contest", "act": "drop", '
             f'"target_kind": "row"}}, words="{DROP_WORDS}")')
    calls = []

    def pick(found):
        calls.extend(found)
        return found[0]

    seat = _Follower(first, pick)
    r = _run(_case("L1-LI-a-dropped-line-is-a-contest"), seat, tmp_path)
    assert len(calls) == 1, calls
    offered = json.loads(re.search(r"rulings=(\{.*\}), words=",
                                   calls[0]).group(1))
    assert offered == {"1": "approve", "2": "approve",
                       "3": {"verdict": "contest", "act": "drop",
                             "target_kind": "row", "words": DROP_WORDS}}
    assert r.passed, r.problems


def test_the_offer_gives_no_approve_to_a_line_his_words_fault(tmp_path):
    """Law 6: only his words choose a verdict. His reply faults line 2, and
    the seat left line 2 out. The refusal names line 2 and offers no call,
    because no call the door can write is his ruling of line 2 (the review
    of f4951389, finding 3)."""
    words = "please drop line 3, and line 2 is wrong too"
    case = _case("L1-LI-a-dropped-line-is-a-contest")
    case["inbound"]["body_text"] = words
    first = ('TOOL: rulings.rule(rulings={"3": "contest", "act": "drop", '
             f'"target_kind": "row"}}, words="{words}")')
    seen = []

    def pick(found):
        seen.append(found)
        return "Done."

    seat = _Follower(first, pick)
    _run(case, seat, tmp_path)
    error = _last_error(seat.users[1])
    assert '"2": "approve"' not in error, error
    assert '"1": "approve"' in error, error
    assert "Line 2 also has no ruling, and his words fault it" in error, error


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


def test_the_offer_of_stray_fields_on_the_shift_page_takes_its_verdicts(tmp_path):
    """L1-LI-a-separate-request-is-later: the page orders two requests, and
    the seat sent contest with the act drop. The offer kept contest, and the
    shift page takes later, now or drop. The offer now names each verdict
    of that page with no act, and the seat's pick of later lands as park."""
    calls = []

    def pick(found):
        calls.extend(found)
        return next(c for c in found if '"later"' in c)

    seat = _Follower(_shift_first("contest"), pick)
    r = _run(_case("L1-LI-a-separate-request-is-later"), seat, tmp_path)
    maps = [json.loads(re.search(r"rulings=(\{.*?\})(, words=|\))", c).group(1))
            for c in calls]
    assert maps == [{"1": "later"}, {"1": "now"}, {"1": "drop"}], calls
    assert r.passed, r.problems


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
