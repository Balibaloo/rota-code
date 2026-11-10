"""Frames 183 and 114, build 2: three pages of dry run 8 that a row answered.

The rows are dry run 8's, copied by id from `dry8/copies/final.db` of
session 13b7eef8 (plans/f183-114-clarify-read-2026-11-10.md).
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.runner import resolve_inbound
from rota.core.sandbox import build
from rota.core.scheduler import Wake
from rota.roles import prompts

M30 = ("The requirement for folding long lines in icalendar specifies folding at "
       "a space to avoid splitting words. Does this rule apply to all lines "
       "regardless of length, or is there a minimum character threshold before "
       "folding is triggered?")
M52 = ("The requirement for folding long lines in icalendar specifies folding at "
       "a space to avoid splitting words. The current code folds lines longer "
       "than 75 octets and ensures the line does not already contain a newline. "
       "Does the requirement to fold at a space apply only to these lines longer "
       "than 75 octets, or should it be applied to all lines regardless of length?")
R_M45 = ("Fold only a line longer than 75 octets, as the code does today, and keep "
         "the line assert \"\\n\" not in line in _foldline.")


def _msg(conn, mid, seq, from_role, to_role, verb, refs, text=None, cause=None,
         thread=None, status="answered"):
    conn.execute(
        "INSERT INTO messages (id, thread_id, cause_id, from_role, to_role, verb, "
        "body_refs, body_text, status, seq) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (mid, thread or mid, cause, from_role, to_role, verb, json.dumps(refs),
         text, status, seq))


@pytest.fixture
def w3(tmp_path):
    """m30, his reply m45, r_m45_2 and rr_997d2888b831, and the report m51."""
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval) VALUES "
                 "('folds_long_lines', 'When icalendar writes a long line, fold "
                 "it at a space.', 'in_scope', 'approved')")
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES "
                 "('bg_1', 'folds_long_lines', 'running')")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_1', "
                 "'folds_long_lines', 'fold long lines in the _foldline function "
                 "at src/icalendar/parser/string.py')")
    _msg(conn, "m30", 30, "liaison", "principal", "clarify", ["bg_1"], M30,
         thread="m29")
    _msg(conn, "m45", 45, "principal", "liaison", "converse", ["bg_1"],
         cause="m30", thread="m29")
    conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                 "VALUES ('e_m45', 'principal', ?, 45)", (R_M45,))
    conn.execute(
        "INSERT INTO rulings (id, ask_id, reply_id, per_item, words, status) "
        "VALUES ('r_m45_2', 'm30', 'm45', '{\"bg_1\": \"approve\"}', ?, 'landed')",
        (R_M45,))
    conn.execute(
        "INSERT INTO ruled_refs (id, ruling_id, ref, verdict, words, words_from, "
        "source) VALUES ('rr_997d2888b831', 'r_m45_2', 'bg_1', 'approve', ?, "
        "'m45', 'reading')", (R_M45,))
    _msg(conn, "m51", 51, "vision_keeper", "liaison", "report", ["bg_1", "tk_1"])
    conn.commit()
    return conn


def _liaison(conn, sid="s187"):
    wake = Wake("liaison", "message", refs=("bg_1", "tk_1"), message_id="m51")
    sb = build("liaison", conn, mode="normal", session_id=sid, wake=wake,
               allow=prompts.mode_tools("liaison", "report"))
    sb.ctx.trigger = "m51"
    return sb


def test_a_clarify_on_rows_he_ruled_meets_his_words_first(w3):
    """W3. s187 call 4 sent m52 on bg_1 and tk_1, and r_m45_2 held his answer."""
    sb = _liaison(w3)
    with pytest.raises(ValueError) as got:
        sb.call("msg.clarify_principal", refs=["bg_1", "tk_1"], question=M52)
    said = str(got.value)
    assert "r_m45_2 on bg_1, approve" in said
    assert "Fold only a line longer than 75 octets, as the code does today" in said
    assert sb.ctx.outbound == []
    # The second call names the ruling it read, and it lands.
    sb.call("msg.clarify_principal", refs=["bg_1", "tk_1", "r_m45_2"],
            question=M52)
    assert [m["verb"] for m in sb.ctx.outbound] == ["clarify"]


def test_the_refusal_fires_once_per_session_per_ruling(w3):
    sb = _liaison(w3)
    with pytest.raises(ValueError, match="r_m45_2"):
        sb.call("msg.clarify_principal", refs=["bg_1", "tk_1"], question=M52)
    sb.call("msg.clarify_principal", refs=["bg_1", "tk_1"], question=M52)
    assert len(sb.ctx.outbound) == 1


def test_a_clarify_on_rows_with_no_landed_ruling_lands_at_once(w3):
    sb = _liaison(w3)
    sb.call("msg.clarify_principal", refs=["tk_1"], question=M52)
    assert len(sb.ctx.outbound) == 1
    # A ruling that has not landed covers nothing.
    w3.execute("UPDATE rulings SET status = 'open' WHERE id = 'r_m45_2'")
    other = _liaison(w3, sid="s188")
    other.call("msg.clarify_principal", refs=["bg_1"], question=M52)
    assert len(other.ctx.outbound) == 1


def test_a_liaison_tick_that_can_clarify_sees_his_answers(w3):
    """W3's reach: s190 on `tick:unresolved` had no `prior_answers`."""
    _msg(w3, "m34", 34, "developer", "architect", "escalate", ["bg_1"])
    wake = Wake("liaison", "tick:unresolved", refs=("m34",))
    got = resolve_inbound(w3, wake)
    assert got["prior_answers"][0]["question"] == M30


BASE_RED = ["inh_16dcb40b", "inh_70337a4f", "inh_e2eb1d19"]
PATHS = {"inh_16dcb40b": "src/icalendar/tests/test_issue_1445.py",
         "inh_70337a4f": "src/icalendar/tests/test_rfc_6868.py",
         "inh_e2eb1d19": "src/icalendar/tests/test_time.py",
         "inh_02554f55": "src/icalendar/tests/test_other.py"}


@pytest.fixture
def w5(w3):
    """The config row `base_run:bg_1` with its three red tests, and one test
    that the base run found green."""
    for tid, path in PATHS.items():
        w3.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                   "VALUES (?, 'bg_1', NULL, ?, '')", (tid, path))
    base = {t: {"result": "fail", "output": "F [100%]"} for t in BASE_RED}
    base["inh_02554f55"] = {"result": "pass", "output": ". [100%]"}
    w3.execute("INSERT INTO config (key, value) VALUES ('base_run:bg_1', ?)",
               (json.dumps(base),))
    w3.commit()
    return w3


def _developer(conn):
    return build("developer", conn, mode="tests_failing", batch_id="bg_1",
                 session_id="s_dev",
                 allow=prompts.mode_tools("developer", "tests_failing"))


def test_an_escalation_of_tests_red_at_the_base_ends_the_session(w5):
    """W5. m34 named the three tests red at bg_1's base and climbed to m54."""
    from rota.core.predicates import unresolved
    from rota.roles import api

    sb = _developer(w5)
    with pytest.raises(api.EndRefusal) as got:
        sb.call("msg.escalate_architect", refs=BASE_RED)
    assert "found inh_16dcb40b, inh_70337a4f, inh_e2eb1d19 red" in str(got.value)
    assert sb.ctx.outbound == []
    # No m34, so no rung and no Liaison wake comes from it.
    assert unresolved(w5) == []


def test_a_mixed_escalation_climbs_without_the_tests_red_at_the_base(w5):
    sb = _developer(w5)
    with pytest.raises(ValueError) as got:
        sb.call("msg.escalate_architect", refs=["inh_16dcb40b", "inh_02554f55"])
    assert "Send msg.escalate_architect(refs=['inh_02554f55'])" in str(got.value)
    assert [o.args for o in sb.ctx.offers
            if o.op == "msg.escalate_architect"] == [{"refs": ["inh_02554f55"]}]
    sb.call("msg.escalate_architect", refs=["inh_02554f55"])
    assert [m["body_refs"] for m in sb.ctx.outbound] == [["inh_02554f55"]]


def test_a_test_not_red_at_the_base_still_climbs(w5):
    from rota.core.predicates import unresolved

    _msg(w5, "m60", 60, "developer", "architect", "escalate", ["inh_02554f55"],
         status="unresolved")
    w5.commit()
    assert [(w.role, w.refs) for w in unresolved(w5)] == [
        ("architect", ("m60",))]


M54 = ("The roles are struggling to reconcile the behavior of 'unknown' values "
       "and parameters across RFC 7265 and RFC 6868. Can you clarify the "
       "priority?")
M57 = ("Criterion c3 requires lines to be at most 75 octets, but the current "
       "implementation of folding (cw_7039d1d2d899) fails to meet this limit "
       "when processing multi-byte unicode characters (as shown in tst_c3). If "
       "we strictly enforce the 75-octet limit, some words may be split.")
M58 = ("Does \"keep everything else as before\" mean that the resulting folded "
       "output must maintain the exact same character sequence (including "
       "newlines and spaces) as the original, with the only change being the "
       "insertion of newlines at spaces?")


@pytest.fixture
def w7(w5):
    """The five open pages of dry run 8 at the stop, with bg_1 `deferred`."""
    w5.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c1', 'tk_1', "
               "'The _foldline function must not split a word at any point.')")
    w5.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c3', 'tk_1', "
               "'Every line is at most 75 octets long.')")
    w5.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst_c3', 'bg_1', 'c3', 'tests/test_c3.py', '')")
    w5.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m1', 'principal', 'Fold long lines at a space, and keep "
               "everything else as before.', 1)")
    _msg(w5, "m44", 44, "architect", "vision_keeper", "propose", ["bg_1"])
    _msg(w5, "m52", 52, "liaison", "principal", "clarify", ["bg_1", "tk_1"], M52,
         cause="m51", thread="m51", status="open")
    _msg(w5, "m54", 54, "liaison", "principal", "clarify", BASE_RED, M54,
         thread="m34", status="open")
    _msg(w5, "m57", 57, "liaison", "principal", "clarify",
         ["c3", "cw_7039d1d2d899", "tst_c3", "d_57ad7f6b9b"], M57,
         thread="m39", status="open")
    _msg(w5, "m58", 58, "liaison", "principal", "clarify", ["e_m1"], M58,
         cause="m44", thread="m44", status="open")
    _msg(w5, "m59", 59, "liaison", "principal", "present",
         ["bg_1", "folds_long_lines", "c1", "c3"], status="open")
    w5.execute("UPDATE batches SET status = 'deferred' WHERE id = 'bg_1'")
    w5.commit()
    return w5


def test_every_page_of_the_parked_batch_has_a_tie_to_it(w7):
    from rota.roles.principal import batch_of_page

    assert {m: batch_of_page(w7, m) for m in ("m52", "m54", "m57", "m58", "m59")} == {
        m: "bg_1" for m in ("m52", "m54", "m57", "m58", "m59")}
    assert batch_of_page(w7, "m30") == "bg_1"
    assert batch_of_page(w7, "m45") == "bg_1"
    # A criterion of the batch's item is the third tie.
    _msg(w7, "m61", 61, "liaison", "principal", "clarify", ["c1"], "Which?",
         status="open")
    assert batch_of_page(w7, "m61") == "bg_1"


def test_an_open_page_on_a_parked_batch_waits_with_the_batch(w7):
    """W7. At the stop he had five pages, and four were on the parked bg_1."""
    from rota.roles.principal import pending_asks

    asks = pending_asks(w7)
    assert [a.message_id for a in asks] == ["m59"]
    page = asks[0].rendered
    for mid, said in (("m52", M52.split(". ")[0] + "."),
                      ("m54", M54.split(". ")[0] + "."),
                      ("m57", M57.split(". ")[0] + "."),
                      ("m58", M58)):
        assert f"\n  {mid}: {said}" in page, page
    # The held pages stay open, so no write is needed when the batch resumes.
    assert {r[0] for r in w7.execute(
        "SELECT id FROM messages WHERE status = 'open'")} == {
        "m52", "m54", "m57", "m58", "m59"}
    w7.execute("UPDATE batches SET status = 'running' WHERE id = 'bg_1'")
    asks = pending_asks(w7)
    assert [a.message_id for a in asks] == ["m52", "m54", "m57", "m58", "m59"]
    assert all("These pages wait" not in a.rendered for a in asks)


def test_a_parked_batch_with_no_open_park_page_holds_no_page(w7):
    from rota.roles.principal import pending_asks

    w7.execute("UPDATE messages SET status = 'answered' WHERE id = 'm59'")
    assert [a.message_id for a in pending_asks(w7)] == ["m52", "m54", "m57", "m58"]
