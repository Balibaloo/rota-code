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
# do not hold the call. Frame 349 guarded each text with `api._holds`, so
# the table is empty. The lint reads the three guard forms of
# `_refusal_calls`. Its limits: it does not read a guard inside a helper,
# or a flag that the code arms outside `sandbox.build`. It reads
# `if "x.y" not in held:` around a text as a guard, which is the wrong
# polarity. It checks only the name of a text that a shared door reaches,
# so the follower tests below hold those texts.
KNOWN_UNHELD: dict[str, str] = {}


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


# --- the texts that a shared door reaches ----------------------------------
# The lint checks only the name of such a text (frame 349's read, places 7
# to 9). So each test builds the narrowed mode, raises the text, and holds
# its calls and its record to the mode.

def _narrowed(role: str, db, mode: str, **kw):
    from rota.roles import prompts
    return sandbox.build(role, db, mode=mode,
                         allow=prompts.mode_tools(role, mode), **kw)


def _unheld(sb, dotted: str, said: str) -> list[str]:
    """The calls that the text or its record names and the mode lacks."""
    _mode, held = sandbox.held_calls(sb)
    named = {c for c in re.findall(r"\b[a-z_]+\.[a-z_]+\b", said)
             if lint.exists(c)}
    recs = sandbox.follow(sb, dotted, {}, ValueError(said),
                          list(getattr(sb.ctx, "offers", None) or []))
    return sorted(named - held) + [c for r in recs for c in r["not_in_mode"]]


def _red_at_base(monkeypatch):
    from rota.core import harness
    monkeypatch.setattr(harness, "base_run", lambda conn, batch: {
        "inh_1": {"result": "fail", "output": "E   assert 1 == 2"}})
    # The repeat doors admit, so only the mode can drop the call. The mode
    # check sits in `_escalation_admitted` since frame 349's pass 2.
    monkeypatch.setattr(sandbox, "_same_refs_refusal",
                        lambda ctx, recipient, verb, refs: None)


def test_the_base_run_fact_names_no_escalation_in_answer(db, monkeypatch):
    """Place 7: a challenge in developer/answer meets the base run's fact,
    and answer lacks `msg.escalate_architect`. The text gives the fact and
    the end (the review of pass 1, finding 4)."""
    _red_at_base(monkeypatch)
    sb = _narrowed("developer", db, "answer", batch_id="b1")
    sb.ctx.offers = []
    said = sandbox.project_tests_fact(sb.ctx, ["inh_1"]) or ""
    assert "the fix is not yours. End the session with no call" in said, said
    assert "msg.escalate_architect" not in said, said
    assert "escalated these refs already" not in said, said
    assert _unheld(sb, "msg.challenge_tester", said) == []


def test_the_base_run_fact_names_the_escalation_where_held(db, monkeypatch):
    _red_at_base(monkeypatch)
    sb = _narrowed("developer", db, "tests_failing", batch_id="b1")
    sb.ctx.offers = []
    said = sandbox.project_tests_fact(sb.ctx, ["inh_1"]) or ""
    assert "Send msg.escalate_architect(refs=['inh_1'])" in said, said
    assert [o.op for o in sb.ctx.offers] == ["msg.escalate_architect"]


def _two_answers(db):
    # The rows of test_desk_guards' fixture that the refs door resolves.
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i1','closing keeps invoices','in_scope',"
               "'approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('tk1','i1','close an account')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c1','tk1','closing an account leaves its invoices in place')")
    db.execute("INSERT INTO batches (id, item_id, status, head_commit) VALUES "
               "('b1','i1','running','abc123')")
    m = ("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
         "body_refs, body_text, cause_id, seq, status) "
         "VALUES (?,?,?,?,?,?,?,?,?,?)")
    db.execute(m, ("q1", "t", "tester", "terminologist", "question", '["c1"]',
                   "what?", None, 1, "answered"))
    db.execute(m, ("a1", "t", "terminologist", "tester", "answer", '["g1"]',
                   None, "q1", 2, "answered"))
    db.execute(m, ("q2", "t", "tester", "terminologist", "question",
                   '["c1", "g1"]', "and?", None, 3, "answered"))
    db.execute(m, ("a2", "t", "terminologist", "tester", "answer", '["g1"]',
                   None, "q2", 4, "answered"))
    db.commit()


def test_a_third_question_in_answer_names_no_triage(db):
    """Place 8: tester/answer holds the questions and lacks `tests.triage`,
    so the third question meets the fact and the end."""
    _two_answers(db)
    sb = _narrowed("tester", db, "answer", batch_id="b1")
    sb.ctx.offers = []
    with pytest.raises(ValueError) as exc:
        sb.call("msg.question_terminologist", refs=["c1"],
                question="but really?")
    said = str(exc.value)
    assert "answered 2 questions of yours" in said, said
    assert said.endswith("The exit is end the session with no call"), said
    assert "tests.triage" not in said, said
    assert _unheld(sb, "msg.question_terminologist", said) == []


def test_a_third_question_in_tests_missing_names_the_triage(db):
    _two_answers(db)
    sb = _narrowed("tester", db, "tests_missing", batch_id="b1")
    with pytest.raises(ValueError, match="answered 2 questions.*tests.triage"):
        sb.call("msg.question_terminologist", refs=["c1"],
                question="but really?")


def test_the_decision_step_is_not_met_where_the_challenge_is_not_held(db):
    """Place 9: `_escalation_or_step` offers the challenge on the step toward
    the code. Only a `msg.challenge_tester` send and the two admitted asks
    reach it. developer/finding_violated and touch_mistaken lack that call,
    so the runtime refuses it before any door, and the revert door asks
    `_holds` first."""
    for mode in ("finding_violated", "touch_mistaken"):
        sb = _narrowed("developer", db, mode, batch_id="b1")
        _mode, held = sandbox.held_calls(sb)
        assert "msg.challenge_tester" not in held, (mode, sorted(held))
        assert not api._holds(sb.ctx, "msg.challenge_tester"), mode
        with pytest.raises(sandbox.NotInWorkingSet):
            sb.call("msg.challenge_tester", refs=["c1", "t1"], quotes=["a", "b"])


def _desk(db):
    """The rows of test_desk_guards' `db` fixture, which its helpers read."""
    for sql in (
            "INSERT INTO items (id, text, kind, approval, approval_ver, "
            "version) VALUES ('i1','closing keeps invoices','in_scope',"
            "'approved',1,1)",
            "INSERT INTO tickets (id, item_id, text) VALUES "
            "('tk1','i1','close an account')",
            "INSERT INTO glossary_terms (id, term, sense_short) "
            "VALUES ('g1','account','the billing entity')",
            "INSERT INTO criteria (id, ticket_id, text) VALUES "
            "('c1','tk1','closing an account leaves its invoices in place')",
            "INSERT INTO refs (src_table, src_id, kind, target) VALUES "
            "('criteria','c1','term','g1')",
            "INSERT INTO batches (id, item_id, status, head_commit) VALUES "
            "('b1','i1','running','abc123')",
            "INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
            "('b1','tk1')",
            "INSERT INTO tests (id, batch_id, criterion_id, path, body) "
            "VALUES ('tst1','b1','c1','test_close.py',"
            "\"assert close_account('a1') is not None\")"):
        db.execute(sql)
    db.commit()


def _woken(role: str, db, mode: str):
    """A seat with a live tick wake, as the runner builds it."""
    from rota.core.scheduler import Wake
    from rota.roles import prompts
    db.commit()
    return sandbox.build(role, db, batch_id="b1", mode="normal",
                         allow=prompts.mode_tools(role, mode),
                         wake=Wake(role, "tick:" + mode))


def test_the_challenge_cap_names_no_escalation_in_answer(db):
    """Finding 1 of the review of frame 349's pass 1: a challenge in
    developer/answer met the cap, and `_escalation_or_step` named
    `msg.escalate_architect`, which answer lacks."""
    from .test_desk_guards import QUOTES, REASON, _chain
    _desk(db)
    _chain(db, ("tst1",))
    db.execute("DELETE FROM test_runs")
    sb = _woken("developer", db, "answer")
    sb.ctx.offers = []
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", reason=REASON, refs=["c1", "tst1"],
                quotes=QUOTES)
    said = str(exc.value)
    assert "msg.escalate_architect" not in said, said
    assert _unheld(sb, "msg.challenge_tester", said) == []


def test_a_repeated_critic_challenge_names_no_escalation(db):
    """Finding 2 of the review of frame 349's pass 1: the same-refs door
    gave critic/review the Developer's rung, an escalation and a code
    change. The critic holds neither."""
    from .test_desk_guards import QUOTES, _msg
    _desk(db)
    _msg(db, "m1", "critic", "tester", "challenge", ["c1", "tst1"], 1,
         "answered")
    _msg(db, "m2", "tester", "critic", "answer", ["c1", "tst1"], 2,
         "answered", cause="m1")
    sb = _woken("critic", db, "review")
    sb.ctx.offers = []
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", refs=["c1", "tst1"], quotes=QUOTES)
    said = str(exc.value)
    assert "Act on the answer, or end the session with no call." in said, said
    assert _unheld(sb, "msg.challenge_tester", said) == []


def test_the_offer_gives_no_approve_to_a_line_his_words_fault(tmp_path):
    """Law 6: only his words choose a verdict. His reply faults line 2, and
    the seat left line 2 out. The refusal names line 2 and offers no call,
    because no call the door can write is his ruling of line 2 (the review
    of f4951389, finding 3)."""
    words = "please drop line 3, and line 2 is wrong too"
    case = _case("L1-LI-a-dropped-line-is-a-contest")
    case["inbound"]["body_text"] = words
    # The menu call of the seat keys line 3 alone (frame 345, R6b).
    first = 'TOOL: rulings.rule(rulings={"3": "drop"})'
    seen = []

    def pick(found):
        seen.append(found)
        return "Done."

    seat = _Follower(first, pick)
    _run(case, seat, tmp_path)
    error = _last_error(seat.users[1])
    assert "line 2: his words name the line, and the call gives it no " \
        "option" in error, error
    # Frame 135's law: the text shows no call that rules line 2 for him.
    assert _offered_calls(error) == [], error
    assert seen == [[]], seen
