"""
Frame 142, pass 1: the park ask is a page with rows (ruled: Roman,
2026-10-08, `rota/DECISIONS.md`, "The park ask is a page with rows").

Each test rebuilds one night's rows inline, from the night databases read
with `mode=ro&immutable=1` on 2026-10-08: night 132's bg_2 (four own tests
red), night 133's bg_2 (only the project's tests red) and night 121's bg_2
(five own tests red). The night databases are ignored by git.
"""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from rota.core import predicates as P
from rota.core.db import _lift_quarantines, init_db
from rota.core.scheduler import (
    open_tips, park_ask_id, park_reds, park_rests, park_rows,
)
from rota.llm.llm import Pins, ScriptedBackend
from rota.roles.principal import (
    Answer, Ask, check_line, land, parse_reply, pending_asks, render_state,
)
from rota.tools import invariants
from rota.roles.principal import verdict_for

ITEM_132 = "confirm_with_default_on_eof"
ITEM_TEXT = ("Let confirm() take a default_on_eof flag: when stdin is closed it "
             "returns the default instead of aborting.")
HEAD_132 = "d2b12ea153afea03b02f8e8c644a180e234ffb8d"
KEY = "developer|tick:tests_failing|bg_2"
# The walk's stock sentence of night 132 (`plans/night132-read.md`).
WALK = "yes that all looks right, go ahead"


def _body(name: str, call: str, expects: str, comment: str = "") -> str:
    lines = ["from click.termui import confirm", "import sys", "import io", "",
             f"def test_{name}(monkeypatch):",
             '    monkeypatch.setattr("sys.stdin", io.StringIO(""))',
             f"    {call}"]
    if comment:
        lines.append(f"    # {comment}")
    lines.append(f"    assert {expects}")
    return "\n".join(lines) + "\n"


def _run(name: str, line: str, error: str) -> str:
    """A pytest output whose `FAILED` line is cut to the terminal width, as
    night 132's run tr248 is."""
    return (f"F    [100%]\n=== FAILURES ===\n___ test_{name} ___\n\n"
            f">       assert {line}\nE       {error}\n\n"
            f"=== short test summary info ===\n"
            f"FAILED tests/test_{name}.py::test_{name} - assert F...\n1 failed in 0.12s\n")


# Night 132's bg_2: (criterion, its text, its test, the test's body, red).
N132 = [
    ("cr_1_confirm_eof_default",
     "confirm() must accept an optional 'default_on_eof' boolean argument. When "
     "True and stdin is closed (EOF), confirm() returns the provided default "
     "value instead of raising an exception or aborting.",
     "tst_confirm_eof_default",
     _body("confirm_eof_default", 'result = confirm("y/n", default_on_eof=True)',
           "result == True"), True),
    ("cr_2_confirm_eof_behavior",
     "When 'default_on_eof' is True and stdin reaches EOF, confirm() must not "
     "attempt to read further or wait for input; it immediately returns the "
     "default value.",
     "tst_confirm_eof_behavior",
     _body("confirm_eof_behavior", 'result = confirm("y/n", default_on_eof=True)',
           "result == True",
           "If it waited, this would hang. Since it returned, behavior is correct."),
     True),
    ("cr_3_confirm_eof_default_value",
     "The default value returned by confirm() on EOF must be the same value "
     "passed to confirm() as the 'default' argument, or a sentinel if no "
     "default was provided.",
     "tst_confirm_eof_default_value",
     _body("confirm_eof_default_value",
           'result = confirm("y/n", default_on_eof=True, default=False)',
           "result == False"), False),
    ("cr_4_confirm_eof_input_handling",
     "When 'default_on_eof' is True, confirm() must detect the EOF condition on "
     "stdin and treat it as a valid input state that triggers the default "
     "return path, rather than treating it as an error or blocking wait.",
     "tst_confirm_eof_input_handling",
     _body("confirm_eof_input_handling", 'result = confirm("y/n", default_on_eof=True)',
           "result == True",
           "If it treated EOF as error, it would raise. Since it returned, "
           "handling is correct."), True),
    ("cr_5_confirm_eof_no_side_effects",
     "Upon returning the default value due to EOF with 'default_on_eof' "
     "enabled, confirm() must not perform any cleanup operations, logging, or "
     "state changes that would differ from a normal successful return.",
     "tst_confirm_eof_no_side_effects",
     _body("confirm_eof_no_side_effects", 'result = confirm("y/n", default_on_eof=True)',
           "result == True",
           "Check that no exception was raised and no unexpected state changes "
           "occurred."), True),
    ("cr_6_confirm_eof_default_map_consistency",
     "The behavior of confirm() with 'default_on_eof' must be consistent "
     "regardless of whether the default value is provided via a direct "
     "argument or resolved from the context's default map.",
     "tst_confirm_eof_default_map_consistency",
     _body("confirm_eof_default_map_consistency",
           'result_direct = confirm("y/n", default_on_eof=True, default=False)',
           "result_direct == False"), False),
]
PROJECT = [("inh_022b8a87", "tests/test_utils/test_confirm.py",
            "E       assert not SystemExit(1)"),
           ("inh_51d478df", "tests/test_termui.py", "")]


def _night(conn, *, item: str, text: str, head: str, rows, attempt: int,
           project=PROJECT, status: str = "deferred", own_red=None,
           version: int = 1) -> None:
    """One batch `bg_2` of a night, its item, its criteria, its tests and the
    newest run of each, and its quarantined `tests_failing` key."""
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES (?, ?, 'in_scope', 'approved', ?, ?)",
                 (item, text, version, version))
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_1', ?, 'the ticket')",
                 (item,))
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) "
                 "VALUES ('bg_2', ?, ?, ?)", (item, status, head))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('bg_2', 'tk_1')")
    n = 0
    for crit, crit_text, test, body, red in rows:
        n += 1
        conn.execute("INSERT INTO criteria (id, ticket_id, text, version) "
                     "VALUES (?, 'tk_1', ?, 1)", (crit, crit_text))
        conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body, version) "
                     "VALUES (?, 'bg_2', ?, ?, ?, 1)",
                     (test, crit, f"tests/test_{test[4:]}.py", body))
        if red is None:
            continue
        name = test[4:]
        output = (_run(name, body.strip().splitlines()[-1].strip()[7:],
                       red if isinstance(red, str) else "assert False == True")
                  if red else "1 passed")
        conn.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, "
                     "output, attempt) VALUES (?, 'bg_2', ?, ?, ?, ?, ?)",
                     (f"tr{n}", test, head, "fail" if red else "pass", output, attempt))
    for test, path, error in project:
        n += 1
        conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body, version) "
                     "VALUES (?, 'bg_2', NULL, ?, '', 1)", (test, path))
        conn.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, "
                     "output, attempt) VALUES (?, 'bg_2', ?, ?, 'fail', ?, ?)",
                     (f"tr{n}", test, head, f"FAILED {path}\n{error}\n", attempt))
    conn.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, reported) "
                 "VALUES (?, 3, 1, 1)", (KEY,))
    conn.commit()


@pytest.fixture
def n132(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    _night(conn, item=ITEM_132, text=ITEM_TEXT, head=HEAD_132, attempt=6,
           rows=[(c, t, tid, b, red) for c, t, tid, b, red in N132])
    return conn


def _liaison_presents(conn, item: str) -> str:
    """The `park_ask` wake, run as a Liaison session with a scripted model.
    The session types the item and the batch, as the brief shows."""
    from rota.core.runner import run_session

    (wake,) = P.REGISTRY["park_ask"].fn(conn)
    conn.commit()
    call = f'TOOL: msg.present_principal(refs=["{item}", "bg_2"])'
    out = run_session(conn, wake, backend=ScriptedBackend([call, "done"]),
                      pins=Pins(model="stub", temperature=0.0), instructions="ask")
    assert out.committed, out.errors
    (row,) = conn.execute("SELECT id FROM messages WHERE substr(id, 1, 7) = 'm_park_'"
                          ).fetchall()
    return row["id"]


def _reply(conn, mid: str, text: str) -> str:
    (ask,) = [a for a in pending_asks(conn) if a.message_id == mid]
    answer = parse_reply(ask, text)
    assert answer.verb == "reply"
    reply = land(conn, ask, answer)
    conn.commit()
    return reply


def _landing(conn, reply: str, call: str):
    from rota.core.runner import run_session

    (wake,) = [w for w in open_tips(conn) if w.message_id == reply]
    return run_session(conn, wake, backend=ScriptedBackend([call, "done"]),
                       pins=Pins(model="stub", temperature=0.0), instructions="land")


def test_the_park_ask_is_a_page_with_the_item_and_the_criteria_each_with_its_check(n132):
    """Night 132, m117 on `m_park_3b5cf1bd9b_bg_2`: the park ask was a
    clarify with the item alone, and its answer had no row to land on."""
    own, project = park_reds(n132, "bg_2")
    assert sorted(r["criterion_id"] for r in own) == [
        "cr_1_confirm_eof_default", "cr_2_confirm_eof_behavior",
        "cr_4_confirm_eof_input_handling", "cr_5_confirm_eof_no_side_effects"]
    assert [r["test_id"] for r in project] == ["inh_022b8a87", "inh_51d478df"]
    (wake,) = P.REGISTRY["park_ask"].fn(n132)
    assert wake.refs == (ITEM_132, "bg_2")
    assert wake.detail == ("bg_2 is parked. The team gave up on: tests_failing for "
                           "bg_2. It is a page.")

    expected = park_ask_id(n132, "bg_2")
    mid = _liaison_presents(n132, ITEM_132)
    assert mid == expected
    row = n132.execute("SELECT verb, status, body_refs FROM messages WHERE id = ?",
                       (mid,)).fetchone()
    assert (row["verb"], row["status"]) == ("present", "open")
    assert json.loads(row["body_refs"]) == [ITEM_132] + [c[0] for c in N132]
    assert P.REGISTRY["park_ask"].fn(n132) == []

    (ask,) = pending_asks(n132)
    page = ask.rendered
    assert ask.order == [ITEM_132] + [r for c in N132 for r in (c[0], c[2])]
    assert page.startswith("This change stopped. The team tried 6 times, and 4 of "
                           "its 6 checks still fail.")
    assert f"  1. {ITEM_TEXT}" in page and "  12. The behavior of confirm()" in page
    assert page.count("Fails:") == 4 and page.count("Passes.") == 2
    assert ('check: confirm eof default, calls result = confirm("y/n", '
            'default_on_eof=True), expects result == True. Fails: assert False '
            '== True.') in page
    assert "The last attempt: tests/test_confirm_eof_behavior.py failed: " in page
    assert "Reply 'ok' if every line says what you want." in page


PAGE_132 = [
    "This change stopped. The team tried 6 times, and 4 of its 6 checks still fail.",
    "You asked:",
    "  1. Let confirm() take a default_on_eof flag: when stdin is closed it returns "
    "the default instead of aborting.",
    "It must:",
    "  2. confirm() must accept an optional 'default_on_eof' boolean argument. When "
    "True and stdin is closed (EOF), confirm() returns the provided default value "
    "instead of raising an exception or aborting.",
    '     3. check: confirm eof default, calls result = confirm("y/n", default_on_eof=True), '
    "expects result == True. Fails: assert False == True.",
    "  4. When 'default_on_eof' is True and stdin reaches EOF, confirm() must not "
    "attempt to read further or wait for input; it immediately returns the default value.",
    '     5. check: confirm eof behavior, calls result = confirm("y/n", default_on_eof=True), '
    "expects result == True. Fails: assert False == True.",
    "  6. The default value returned by confirm() on EOF must be the same value passed "
    "to confirm() as the 'default' argument, or a sentinel if no default was provided.",
    '     7. check: confirm eof default value, calls result = confirm("y/n", '
    "default_on_eof=True, default=False), expects result == False. Passes.",
    "  8. When 'default_on_eof' is True, confirm() must detect the EOF condition on "
    "stdin and treat it as a valid input state that triggers the default return path, "
    "rather than treating it as an error or blocking wait.",
    '     9. check: confirm eof input handling, calls result = confirm("y/n", '
    "default_on_eof=True), expects result == True. Fails: assert False == True.",
    "  10. Upon returning the default value due to EOF with 'default_on_eof' enabled, "
    "confirm() must not perform any cleanup operations, logging, or state changes that "
    "would differ from a normal successful return.",
    '     11. check: confirm eof no side effects, calls result = confirm("y/n", '
    "default_on_eof=True), expects result == True. Fails: assert False == True.",
    "  12. The behavior of confirm() with 'default_on_eof' must be consistent regardless "
    "of whether the default value is provided via a direct argument or resolved from "
    "the context's default map.",
    "     13. check: confirm eof default map consistency, calls result_direct = "
    'confirm("y/n", default_on_eof=True, default=False), expects result_direct == '
    "False. Passes.",
    "The last attempt: tests/test_confirm_eof_behavior.py failed: assert False == True. "
    "tests/test_confirm_eof_default.py failed: assert False == True.",
    "Reply 'ok' if every line says what you want. The team then stops here and tells you.",
    "Name a line to correct only that line. Ask, if something here is unclear.",
]


def test_the_park_page_renders_word_for_word_through_the_request_block(n132):
    """Frame 190's design, 2.1, point 3: the park page renders its request
    lines through `request_block`, the helper every present now shares. The
    page of night 132's m117 stays as frame 142 landed it, word for word."""
    _liaison_presents(n132, ITEM_132)
    (ask,) = pending_asks(n132)
    assert ask.rendered.splitlines() == PAGE_132


@pytest.mark.skip(reason="frame 345 R2: word form, re-pin on the menu form")
def test_a_contest_of_a_criterion_line_lands_an_open_verdict_that_names_it(n132):
    """Night 132, s218, the other way: line 3 is cr_2, and its contest goes
    to the criterion's writer through `verdict_signoff`."""
    from rota.core.runner import _mode_key
    from rota.core.sandbox import _owner_of_ref

    mid = _liaison_presents(n132, ITEM_132)
    reply = _reply(n132, mid, "line 4 is wrong: it must not hang")
    ruling = {str(n): "approve" for n in (1, 2, 4, 6, 8, 10, 12)}
    ruling["4"] = "contest"
    out = _landing(n132, reply, f"TOOL: rulings.rule(rulings={json.dumps(ruling)}, "
                                "words='line 4 is wrong: it must not hang')")
    assert out.committed, out.errors
    (verdict,) = n132.execute("SELECT id, status FROM messages WHERE cause_id = ? "
                              "AND verb = 'verdict'", (mid,)).fetchall()
    assert verdict["status"] == "open"
    held = verdict_for(n132, verdict['id'])
    assert held["cr_2_confirm_eof_behavior"] == "contest"
    # The contest rests the page: no second page on the same rows before
    # the respecify (the diff review of b0a2086e, finding 2).
    assert park_rests(n132, "bg_2")
    assert P.REGISTRY["park_ask"].fn(n132) == []
    assert invariants.i5(n132) == []
    assert "The team rewrites the lines you corrected" in render_state(n132)
    (wake,) = [w for w in open_tips(n132) if w.message_id == verdict["id"]]
    assert _mode_key(wake, n132) == "verdict_signoff"
    # The relay door routes the park's criteria to their writer, whatever
    # owner the session names.
    from rota.core.sandbox import build
    from rota.roles import prompts

    sb = build("liaison", n132, mode="normal", session_id="s219", wake=wake,
               allow=prompts.mode_tools("liaison", "verdict_signoff"))
    sb.ctx.trigger = verdict["id"]
    sb.call("msg.relay_vision_keeper", refs=[ITEM_132])
    routed = {m["to_role"]: m["body_refs"] for m in sb.ctx.outbound}
    # The approved criteria stay out (the diff review of 0baacf55, finding
    # 2), and the item is no row of the page, so no Vision Keeper relay
    # carries it (the delta review of 4ef3bd9f, finding 2).
    assert routed == {"terminologist": ["cr_2_confirm_eof_behavior"]}
    assert _owner_of_ref(n132, "cr_2_confirm_eof_behavior") is None

    # The respecify moves cr_2's version and lifts the key. The re-park asks
    # again under a new id.
    n132.execute("UPDATE criteria SET version = 2 WHERE id = 'cr_2_confirm_eof_behavior'")
    _lift_quarantines(n132, SimpleNamespace(table="criteria", row_id="cr_2_confirm_eof_behavior",
                                            op="update", values={"text": "x"}), True)
    n132.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, reported) "
                 "VALUES (?, 3, 1, 1)", (KEY,))
    assert park_ask_id(n132, "bg_2") != mid
    assert len(P.REGISTRY["park_ask"].fn(n132)) == 1


@pytest.mark.skip(reason="frame 345 R2: word form, re-pin on the menu form")
@pytest.mark.parametrize("call", [
    "done", f'TOOL: msg.relay_vision_keeper(refs=["{ITEM_132}"])',
    'TOOL: msg.relay_vision_keeper(refs=["cr_1_confirm_eof_default", '
    '"cr_2_confirm_eof_behavior"])'])
def test_the_door_relays_a_park_verdicts_contested_criteria_to_the_terminologist(n132, call):
    """The delta review of 172b373b, finding 1: `verdict_signoff.md` says a
    criterion has no relay, so a session that obeys it sends none. The door
    relays the contested criterion whatever the session sent, and once. The
    diff review of 0baacf55, finding 2: the relay holds the contested
    criterion alone, and no approved one, whatever refs the session named."""
    from rota.core.runner import run_session

    mid = _liaison_presents(n132, ITEM_132)
    reply = _reply(n132, mid, "line 4 is wrong: it must not hang")
    ruling = {str(n): "approve" for n in (1, 2, 4, 6, 8, 10, 12)}
    ruling["4"] = "contest"
    out = _landing(n132, reply, f"TOOL: rulings.rule(rulings={json.dumps(ruling)}, "
                                "words='line 4 is wrong: it must not hang')")
    assert out.committed, out.errors
    (verdict,) = n132.execute("SELECT id FROM messages WHERE cause_id = ? "
                              "AND verb = 'verdict'", (mid,)).fetchall()
    (wake,) = [w for w in open_tips(n132) if w.message_id == verdict["id"]]
    out = run_session(n132, wake, backend=ScriptedBackend([call, "done"]),
                      pins=Pins(model="stub", temperature=0.0), instructions="relay")
    assert out.committed, out.errors
    rows = n132.execute("SELECT id, body_refs FROM messages WHERE cause_id = ? AND "
                        "verb = 'relay' AND to_role = 'terminologist'",
                        (verdict["id"],)).fetchall()
    assert len(rows) == 1
    refs = json.loads(rows[0]["body_refs"])
    assert refs == ["cr_2_confirm_eof_behavior"]
    # No relay of the item to the Vision Keeper (the delta review of
    # 4ef3bd9f, finding 2).
    assert n132.execute("SELECT 1 FROM messages WHERE cause_id = ? AND verb = 'relay' "
                        "AND to_role != 'terminologist'", (verdict["id"],)).fetchone() is None
    from rota.core.scheduler import park_criterion_relay

    assert park_criterion_relay(n132, rows[0]["id"])


@pytest.mark.skip(reason="frame 345 R2: word form, re-pin on the menu form")
def test_the_door_drops_an_approved_criterion_from_a_held_terminologist_relay(n132):
    """The diff review of 0baacf55, finding 2: `stage_park_relay` widened a
    held relay and kept every criterion in it. One contest and two approves
    leave the contested criterion alone, and no other ref (the delta review
    of 4ef3bd9f, finding 2)."""
    from rota.core.sandbox import build, stage_park_relay
    from rota.roles import prompts

    mid = _liaison_presents(n132, ITEM_132)
    reply = _reply(n132, mid, "line 4 is wrong: it must not hang")
    ruling = {str(n): "approve" for n in (1, 2, 4, 6, 8, 10, 12)}
    ruling["4"] = "contest"
    out = _landing(n132, reply, f"TOOL: rulings.rule(rulings={json.dumps(ruling)}, "
                                "words='line 4 is wrong: it must not hang')")
    assert out.committed, out.errors
    (verdict,) = n132.execute("SELECT id FROM messages WHERE cause_id = ? "
                              "AND verb = 'verdict'", (mid,)).fetchall()
    sb = build("liaison", n132, mode="normal", session_id="s_held",
               allow=prompts.mode_tools("liaison", "verdict_signoff"))
    sb.ctx.trigger = verdict["id"]
    sb.ctx.outbound.append({
        "id": "m_held", "to_role": "terminologist", "verb": "relay",
        "body_refs": ["cr_1_confirm_eof_default", "cr_3_confirm_eof_default_value",
                      "@term:stdin"],
        "body_text": None, "round_no": 0, "cause_id": verdict["id"],
        # The door keys the criteria relay apart, and the key finds it (the
        # delta review of 2c602d1b, finding 6).
        "split": "terminologist:criteria"})
    stage_park_relay(sb.ctx)
    (held,) = sb.ctx.outbound
    assert held["body_refs"] == ["cr_2_confirm_eof_behavior"]


@pytest.mark.skip(reason="frame 345 R2: word form, re-pin on the menu form")
@pytest.mark.parametrize("call", [
    f'TOOL: msg.relay_vision_keeper(refs=["{ITEM_132}"])',
    'TOOL: msg.relay_terminologist(refs=["cr_2_confirm_eof_behavior"])'])
def test_a_contest_of_the_item_line_relays_the_item_to_the_vision_keeper(n132, call):
    """Line 1 of a park page is the item (frame 142's design, 2.A). A
    contest of it is a contest of a row of the page. After pass 2c the split
    relayed nothing on it and refused with a false sentence."""
    from rota.core.runner import run_session

    mid = _liaison_presents(n132, ITEM_132)
    reply = _reply(n132, mid, "line 1 is wrong: it must not abort")
    ruling = {str(n): "approve" for n in (1, 2, 4, 6, 8, 10, 12)}
    ruling["1"] = "contest"
    out = _landing(n132, reply, f"TOOL: rulings.rule(rulings={json.dumps(ruling)}, "
                                "words='line 1 is wrong: it must not abort')")
    assert out.committed, out.errors
    (verdict,) = n132.execute("SELECT id FROM messages WHERE cause_id = ? "
                              "AND verb = 'verdict'", (mid,)).fetchall()
    (wake,) = [w for w in open_tips(n132) if w.message_id == verdict["id"]]
    out = run_session(n132, wake, backend=ScriptedBackend([call, "done"]),
                      pins=Pins(model="stub", temperature=0.0), instructions="relay")
    assert out.committed, out.errors
    relays = [(r["to_role"], json.loads(r["body_refs"])) for r in n132.execute(
        "SELECT to_role, body_refs FROM messages WHERE cause_id = ? AND verb = 'relay'",
        (verdict["id"],))]
    assert relays == [("vision_keeper", [ITEM_132])]


def test_a_relay_two_hops_below_a_park_verdict_is_no_criterion_repair(n132):
    """The delta review of 172b373b, finding 3: a walk of four hops keyed a
    repair on a relay whose chain reached a park page through a clarify."""
    from rota.core.scheduler import park_criterion_relay

    page = park_ask_id(n132, "bg_2")
    crs = ["cr_2_confirm_eof_behavior"]
    for mid, cause, frm, to, verb, seq in [
            (page, None, "liaison", "principal", "present", 1),
            ("m_v", page, "principal", "liaison", "verdict", 2),
            ("m_c", "m_v", "liaison", "principal", "clarify", 3),
            ("m_a", "m_c", "principal", "liaison", "converse", 4),
            ("m_r", "m_a", "liaison", "terminologist", "relay", 5),
            ("m_r1", "m_v", "liaison", "terminologist", "relay", 6)]:
        n132.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, to_role, "
                     "verb, body_refs, status, seq) VALUES (?, 't', ?, ?, ?, ?, ?, "
                     "'open', ?)", (mid, cause, frm, to, verb, json.dumps(crs), seq))
    assert not park_criterion_relay(n132, "m_r")
    assert park_criterion_relay(n132, "m_r1")


def test_a_criterion_move_ends_the_rest_and_a_bare_lift_keeps_it(n132):
    """Night 132's bg_2 rows, cr_2 respecified. A lift with nothing moved
    keeps the rest, and a criterion move asks again (frame 142's design,
    2.F, amendment 2, after frame 87's review of 4a0ab5c)."""
    mid = _liaison_presents(n132, ITEM_132)
    land(n132, Ask(message_id=mid, verb="present", refs=[ITEM_132] + [c[0] for c in N132]),
         Answer(verb="verdict", per_item={r: "approve" for r in [ITEM_132] + [c[0] for c in N132]},
                text=WALK))
    assert park_rests(n132, "bg_2")

    # A bare lift: the key goes and comes back, and nothing moved.
    n132.execute("DELETE FROM tick_attempts WHERE tick_key = ?", (KEY,))
    n132.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, reported) "
                 "VALUES (?, 3, 1, 1)", (KEY,))
    assert park_ask_id(n132, "bg_2") == mid
    assert P.REGISTRY["park_ask"].fn(n132) == []

    # The Terminologist respecifies cr_2. The move lifts the key, and the
    # re-park asks again under a new id.
    n132.execute("UPDATE criteria SET version = 2 WHERE id = 'cr_2_confirm_eof_behavior'")
    _lift_quarantines(n132, SimpleNamespace(table="criteria", row_id="cr_2_confirm_eof_behavior",
                                            op="update", values={"text": "x"}), True)
    assert P.REGISTRY["park_ask"].fn(n132) == [], "the move ends the park"
    n132.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, reported) "
                 "VALUES (?, 3, 1, 1)", (KEY,))
    assert park_ask_id(n132, "bg_2") != mid
    assert [w.refs for w in P.REGISTRY["park_ask"].fn(n132)] == [(ITEM_132, "bg_2")]


def test_an_empty_ruling_never_rests(n132):
    """Night 132's three `{}` rulings closed three asks. An empty map
    approves no row, so the close counts as a past park."""
    mid = _liaison_presents(n132, ITEM_132)
    n132.execute("UPDATE messages SET status = 'answered' WHERE id = ?", (mid,))
    n132.execute("INSERT INTO rulings (id, ask_id, per_item, words, status) "
                 "VALUES ('r_x', ?, '{}', ?, 'landed')", (mid,  WALK))
    assert not park_rests(n132, "bg_2")
    assert park_ask_id(n132, "bg_2") != mid
    assert len(P.REGISTRY["park_ask"].fn(n132)) == 1


def test_the_check_line_takes_fails_from_the_e_line_adds_the_call_and_strips_comments(n132):
    """Night 132's run tr248 cuts its `FAILED` line to `assert F...`. Night
    121's tst_confirm_eof_cr3 carries a comment on its assert."""
    assert check_line(n132, "tst_confirm_eof_behavior") == (
        'confirm eof behavior, calls result = confirm("y/n", default_on_eof=True), '
        "expects result == True. Fails: assert False == True.")
    assert check_line(n132, "tst_confirm_eof_default_value") == (
        'confirm eof default value, calls result = confirm("y/n", '
        "default_on_eof=True, default=False), expects result == False. Passes.")
    body = ('from click.termui import confirm\nimport sys\nimport io\n\n'
            'def test_confirm_returns_default_when_stdin_closed_and_flag_true():\n'
            '    """Test that confirm() returns default when stdin is closed and flag is True (cr_3)."""\n'
            '    original_stdin = sys.stdin\n    try:\n'
            '        sys.stdin = io.StringIO("")  # Empty stream simulates EOF\n'
            '        result = confirm("Yes or no?", default_on_eof=True)\n'
            '        assert result is True  # Default value for yes/no is True/False\n'
            '    finally:\n        sys.stdin = original_stdin\n')
    n132.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
                 "('tst_confirm_eof_cr3', 'bg_2', 'cr_3_confirm_eof_default_value', "
                 "'tests/test_utils/test_confirm_eof_return.py', ?)", (body,))
    assert check_line(n132, "tst_confirm_eof_cr3") == (
        "confirm returns default when stdin closed and flag true, calls result = "
        'confirm("Yes or no?", default_on_eof=True), expects result is True. Not run yet.')
    n132.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, output) "
                 "VALUES ('tr434', 'bg_2', 'tst_confirm_eof_cr3', 'h', 'fail', ?)",
                 (">           assert result is True\nE           assert False is True\n",))
    assert check_line(n132, "tst_confirm_eof_cr3").endswith(
        "expects result is True. Fails: assert False is True.")
    # An assertion message with its own period keeps one period on the page.
    n132.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, output) "
                 "VALUES ('tr435', 'bg_2', 'tst_confirm_eof_cr3', 'h', 'fail', ?)",
                 (">           assert result is True\nE           AssertionError: no default.\n",))
    assert check_line(n132, "tst_confirm_eof_cr3").endswith(
        "expects result is True. Fails: AssertionError: no default.")


# Night 168's tr35, word for word: a collection error of tst_crit_1 at
# d607d440 (`plans/c5-check-line-provenance.md`, question 2).
TR35 = r"""=================================== ERRORS ====================================
________ ERROR collecting tests/test_utils/test_get_app_dir_roaming.py ________
.venv\Lib\site-packages\_pytest\python.py:508: in importtestmodule
    mod = import_path(
.venv\Lib\site-packages\_pytest\pathlib.py:596: in import_path
    importlib.import_module(module_name)
C:\Users\roman\AppData\Local\Python\pythoncore-3.14-64\Lib\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1398: in _gcd_import
    ???
<frozen importlib._bootstrap>:1371: in _find_and_load
    ???
<frozen importlib._bootstrap>:1342: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:938: in _load_unlocked
    ???
.venv\Lib\site-packages\_pytest\assertion\rewrite.py:179: in exec_module
    source_stat, co = _rewrite_test(fn, self.config)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv\Lib\site-packages\_pytest\assertion\rewrite.py:348: in _rewrite_test
    tree = ast.parse(source, filename=strfn)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\roman\AppData\Local\Python\pythoncore-3.14-64\Lib\ast.py:46: in parse
    return compile(source, filename, mode, flags,
E     File "D:\repos\_AI\sample_repos\clickI\.rota\worktrees\batch_1\tests\test_utils\test_get_app_dir_roaming.py", line 13
E       assert "AppData\Roaming" in result
E                      ^^
E   SyntaxError: "\R" is an invalid escape sequence. Did you mean "\\R"? A raw string is also an option.
=========================== short test summary info ===========================
ERROR tests/test_utils/test_get_app_dir_roaming.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.30s"""
TST_CRIT_1 = ('import os\nimport pytest\nfrom click.utils import get_app_dir\n\n'
              'def test_crit_1():\n    if os.name != "nt":\n'
              '        pytest.skip("Windows only")\n    \n'
              '    os.environ["APPDATA"] = ""\n    os.environ["LOCALAPPDATA"] = ""\n    \n'
              '    result = get_app_dir(app_name="test_app", roaming=True)\n'
              '    assert "AppData\\Roaming" in result')


def _seed_batch_1(conn, result: str, output: str) -> None:
    """Night 168's tst_crit_1 of batch_1 and one run of it."""
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) "
                 "VALUES ('batch_1', ?, 'running', 'd607d440')", (ITEM_132,))
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body, version) "
                 "VALUES ('tst_crit_1', 'batch_1', NULL, "
                 "'tests/test_utils/test_get_app_dir_roaming.py', ?, 2)", (TST_CRIT_1,))
    conn.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, "
                 "output, attempt) VALUES ('tr35', 'batch_1', 'tst_crit_1', 'd607d440', "
                 "?, ?, 6)", (result, output))


def test_the_check_line_of_a_collection_error_ends_with_the_error_not_the_frame(n132):
    """Night 168's m53 line 4 read `Fails: File "...", line 13.`, and he
    read a wrong cause from it (frame 336)."""
    _seed_batch_1(n132, "error", TR35)
    assert check_line(n132, "tst_crit_1") == (
        'crit 1, calls result = get_app_dir(app_name="test_app", roaming=True), '
        'expects "AppData\\Roaming" in result. Fails: SyntaxError: "\\R" is an '
        'invalid escape sequence. Did you mean "\\\\R"? A raw string is also an option.')


def test_the_check_line_of_an_assertion_red_keeps_the_first_e_line(n132):
    """An assertion red puts the assertion first, and pytest's `where` lines
    after it."""
    output = ('>       assert "AppData\\Roaming" in result\n'
              "E       AssertionError: assert 'AppData\\\\Roaming' in 'C:\\\\Users\\\\r'\n"
              "E        +  where 'C:\\\\Users\\\\r' = get_app_dir()\n")
    _seed_batch_1(n132, "fail", output)
    assert check_line(n132, "tst_crit_1").endswith(
        "Fails: AssertionError: assert 'AppData\\\\Roaming' in 'C:\\\\Users\\\\r'.")


def test_the_check_line_of_a_green_run_passes(n132):
    _seed_batch_1(n132, "pass", "1 passed in 0.05s")
    assert check_line(n132, "tst_crit_1") == (
        'crit 1, calls result = get_app_dir(app_name="test_app", roaming=True), '
        'expects "AppData\\Roaming" in result. Passes.')


# Night 133's bg_2 at 79870bfc: its own tests green, the project's two red.
N133 = [("cr_1_confirm_eof_default", "When confirm() receives default_on_eof=True and "
         "stdin reaches EOF, it must return the provided default value rather than "
         "raising an exception or aborting.", "tst_confirm_eof_default_1",
         _body("confirm_eof_default_1", 'result = confirm("y/n", default_on_eof=True)',
               "result == True"), False),
        ("cr_2_confirm_eof_stdin_state", "The confirm() function must detect stdin "
         "closure (EOF) when default_on_eof=True and treat this state as a valid input "
         "condition equivalent to user acceptance of the default.",
         "tst_confirm_eof_stdin_state_1",
         _body("confirm_eof_stdin_state_1", 'result = confirm("y/n", default_on_eof=True)',
               "result == True"), False),
        ("cr_3_confirm_eof_no_abort", "When stdin is closed with default_on_eof=True, "
         "confirm() must not trigger an abort or error state; it must complete the "
         "confirmation flow by returning the default.", "tst_confirm_eof_no_abort_1",
         _body("confirm_eof_no_abort_1", 'result = confirm("y/n", default_on_eof=True)',
               "result == True"), False)]
ITEM_133 = "confirm_default_on_eof"
HEAD_133 = "79870bfc46776ca13000b2cdcd6629e8aa9337ce"


@pytest.fixture
def n133(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    _night(conn, item=ITEM_133, text=ITEM_TEXT + " The flag is optional and defaults "
           "to False.", head=HEAD_133, attempt=2, rows=N133, status="running", version=8)
    return conn


def test_a_park_with_only_project_reds_is_a_closed_note_that_pump_never_asks(n133):
    """Night 133, s319's dispatch. bg_2 was `running` at s319. The test sets
    it `deferred`, the one field a park needs, so the park's own path runs."""
    n133.execute("UPDATE batches SET status = 'deferred' WHERE id = 'bg_2'")
    assert park_reds(n133, "bg_2")[0] == []
    assert park_rows(n133, "bg_2") == ["bg_2"]
    (wake,) = P.REGISTRY["park_ask"].fn(n133)
    assert wake.detail.endswith("It is a note.")

    mid = _liaison_presents(n133, ITEM_133)
    row = n133.execute("SELECT verb, status, body_refs FROM messages WHERE id = ?",
                       (mid,)).fetchone()
    assert (row["verb"], row["status"], json.loads(row["body_refs"])) == (
        "present", "answered", ["bg_2"])
    assert pending_asks(n133) == []
    assert P.REGISTRY["park_ask"].fn(n133) == []
    assert invariants.i5(n133) == []
    assert ("Stuck: bg_2 stops here. It breaks tests/test_termui.py, "
            "tests/test_utils/test_confirm.py. A new commit on the change starts "
            "it again.") in render_state(n133)
    # The key is the note's to say, so the quarantined wake skips it.
    n133.execute("UPDATE tick_attempts SET reported = 0 WHERE tick_key = ?", (KEY,))
    assert P.REGISTRY["quarantined"].fn(n133) == []


def test_a_quarantined_key_of_a_running_batch_still_wakes_the_liaison(n133):
    """Night 133, s319: bg_2 was `running` with its key quarantined. A
    running batch has no park, so the quarantined wake says the key."""
    n133.execute("UPDATE tick_attempts SET reported = 0 WHERE tick_key = ?", (KEY,))
    (wake,) = P.REGISTRY["quarantined"].fn(n133)
    assert wake.refs == ("bg_2",)
    n133.execute("UPDATE batches SET status = 'deferred' WHERE id = 'bg_2'")
    assert P.REGISTRY["quarantined"].fn(n133) == []


M198 = ("I can't approve this yet, because line 2 names the wrong tests: the file "
        "of default tests and the four tests in it cover option defaults and "
        "default maps, not confirm.")


def _touch_reply(conn):
    """Night 133's m197, the touch note on bg_2, and m198, the reply to it."""
    from rota.core.sandbox import build
    from rota.roles import prompts

    conn.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) "
                 "VALUES ('bg_2', 'src/click/termui.py', 'path')")
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "body_refs, status, seq) VALUES ('m197', 'm197', 'liaison', "
                 "'principal', 'present', ?, 'open', 197)",
                 (json.dumps(["bg_2", ITEM_133]),))
    conn.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, to_role, "
                 "verb, body_refs, body_text, status, seq) VALUES ('m198', 'm197', "
                 "'m197', 'principal', 'liaison', 'converse', ?, ?, 'open', 198)",
                 (json.dumps(["bg_2", ITEM_133]), M198))
    conn.commit()
    sb = build("liaison", conn, mode="normal", session_id="s313",
               allow=prompts.mode_tools("liaison", "landing"))
    sb.ctx.trigger = "m198"
    return sb


@pytest.mark.skip(reason="frame 345 R2: word form, re-pin on the menu form")
def test_a_files_correction_of_a_built_batch_line_is_admitted(n133):
    """Night 133, s313: r_2e20813fbe contested bg_2, landed, and moved
    nothing. The principal's words reached no seat. M198 faults line 2, the
    batch line, so the contest is admitted (frame 255). Before frame 255 the
    door refused it. `land` keeps the contest for the Architect: see
    `test_frame255_files_correction.py::
    test_land_keeps_bg_2_and_the_relay_reaches_the_architect`. M198 does not
    fault line 1, so a contest of the item is refused (frame 255, review 1,
    finding 1). The files cue of frame 298, design 3.3, fires before the
    frame 255 door on this page, so the refusal is the cue's text 2."""
    from rota.core.sandbox import build
    from rota.roles import prompts

    sb = _touch_reply(n133)
    out = sb.call("rulings.rule", rulings={ITEM_133: "approve", "bg_2": "contest"},
                  words=M198)
    assert out["per_item"] == {ITEM_133: "approve", "bg_2": "contest"}
    sb = build("liaison", n133, mode="normal", session_id="s313",
               allow=prompts.mode_tools("liaison", "landing"))
    sb.ctx.trigger = "m198"
    with pytest.raises(ValueError, match=(
            r"line 1 is the request, and the words fault only the code it "
            r"touches\. That code is line 2, the change's plan\. Rule line 2 "
            r"contest with the words, and approve line 1\.")):
        sb.call("rulings.rule", rulings={ITEM_133: "contest", "bg_2": "approve"},
                words=M198)


# Night 121's bg_2: five own tests red, cr_2's green.
N121 = [(f"cr_{n}", f"criterion {n} of confirm on a closed stdin", f"tst_confirm_eof_cr{n}",
         _body(f"confirm_eof_cr{n}", 'result = confirm("Yes or no?", default_on_eof=True)',
               "result is True"), n != 2) for n in range(1, 7)]


def test_a_terminologist_relay_of_a_criterion_runs_criterion_repair(n132):
    """Frame 142's design, 2.F, amendment 4: the relay of a criterion ruling
    keys the existing mode, which respecifies and tells the Tester. The
    answer to the Tester stands with no Tester question under it."""
    from rota.core.runner import _mode_key
    from rota.core.sandbox import build
    from rota.core.scheduler import Wake
    from rota.roles import prompts

    page = park_ask_id(n132, "bg_2")

    def msg(mid, cause, from_role, to_role, verb, refs, seq):
        n132.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, to_role, "
                     "verb, body_refs, status, seq) VALUES (?, 't', ?, ?, ?, ?, ?, "
                     "'open', ?)", (mid, cause, from_role, to_role, verb,
                                    json.dumps(refs), seq))

    crs = ["cr_2_confirm_eof_behavior"]
    msg(page, None, "liaison", "principal", "present", [ITEM_132] + crs, 1)
    msg("m_v", page, "principal", "liaison", "verdict", [ITEM_132] + crs, 2)
    msg("m_r", "m_v", "liaison", "terminologist", "relay", crs, 3)
    msg("m_g", None, "liaison", "terminologist", "relay", ["g_x"], 4)
    # Night 133's m327 shape: a contested ledger row became a criterion
    # contest through `about_ref` in `land`, on a page that is no park page.
    n132.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, status, "
                 "author) VALUES ('l_1', 'cr_1_confirm_eof_default', 'criteria', 'x', "
                 "'resolved', 'architect')")
    msg("m_p", None, "liaison", "principal", "present", ["l_1"], 5)
    msg("m_v2", "m_p", "principal", "liaison", "verdict", ["cr_1_confirm_eof_default"], 6)
    msg("m_327", "m_v2", "liaison", "terminologist", "relay", ["cr_1_confirm_eof_default"], 7)
    # Night 133's m88 shape: a term ref beside a criterion. The repair mode
    # has no `glossary.adopt`, so the mixed relay stays in `relay`.
    msg("m_88", "m_v", "liaison", "terminologist", "relay", ["@term:stdin"] + crs, 8)
    n132.commit()
    wake = Wake("terminologist", "message", refs=(), detail="relay", message_id="m_r")
    assert _mode_key(wake, n132) == "criterion_repair"
    other = Wake("terminologist", "message", refs=(), detail="relay", message_id="m_g")
    assert _mode_key(other, n132) == "relay"
    for mid in ("m_327", "m_88"):
        assert _mode_key(Wake("terminologist", "message", refs=(), detail="relay",
                              message_id=mid), n132) == "relay", mid

    # The wake narrows the answer to the reader of the ruled criterion. The
    # asker rule alone left the repair no answer: the relay's sender is the
    # Liaison, and the mode answers the Tester.
    sb = build("terminologist", n132, mode="normal", session_id="s_rep", wake=wake,
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    sb.ctx.trigger = "m_r"
    sb.call("criteria.respecify", id="cr_2_confirm_eof_behavior",
            text="When default_on_eof is True and stdin is at EOF, confirm() returns "
                 "the default without reading again.",
            surface_refs=["src/click/termui.py::confirm"])
    out = sb.call("msg.answer_tester", refs=["cr_2_confirm_eof_behavior"])
    assert out["to"] == "tester" and out["verb"] == "answer"
    # A relay of a term keeps the asker rule: the Tester did not ask.
    sb = build("terminologist", n132, mode="normal", session_id="s_rel", wake=other,
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    sb.ctx.trigger = "m_g"
    with pytest.raises(Exception, match="not in this role's working set"):
        sb.call("msg.answer_tester", refs=["cr_2_confirm_eof_behavior"])


def test_the_state_view_counts_open_faults_and_shows_no_rows(tmp_path):
    """Frame 204's design, section 7, reader 3: the principal sees that rota
    failed, at his altitude, and is asked nothing."""
    conn = init_db(tmp_path / "run.db")
    assert "Rota itself failed" not in render_state(conn)
    for fid, seq, status in (("f_1", 1, "open"), ("f_2", 2, "open"), ("f_3", 3, "resolved")):
        conn.execute("INSERT INTO faults (id, call, text, author, seq, status) VALUES "
                     "(?, 'glossary.adopt', 'the door refused a ruled row', "
                     "'terminologist', ?, ?)", (fid, seq, status))
    page = render_state(conn)
    assert page.endswith("Rota itself failed 2 times this run. The people who "
                         "build it have the list.")
    assert "glossary.adopt" not in page
    assert page.startswith("Nothing waits on you and nothing is building.")


def test_the_agenda_refuses_a_run_from_before_the_faults_table(tmp_path, monkeypatch):
    """Frame 204's review 1, finding L1: `rota agenda` read `faults` on an
    old run and raised `no such table: faults`."""
    from rota import cli
    from rota.core.db import SCHEMA_STALE

    monkeypatch.setattr(cli, "RUNS", tmp_path)
    conn = init_db(tmp_path / "run.db")
    conn.execute("DROP TABLE faults")
    conn.execute("UPDATE config SET value = 'ledger-kind' WHERE key = 'schema'")
    conn.commit()
    conn.close()
    with pytest.raises(SystemExit) as refused:
        cli.main(["agenda", "run"])
    assert str(refused.value) == f"run: {SCHEMA_STALE}"
