"""
Frame 255, pass 1: a files correction after the head commit lands.

The scene is night 149's bg_2 page m91, rebuilt inline from
`.rota/clickI_night149.db` at the night's end, read with `mode=ro` on
2026-10-15. bg_2 has a head commit and runs. The words are m92 and m105.
The maps are s199's and s212's first `rulings.rule` calls, which are the
same map. The scope read is `plans/frame255-scope.md`, sections 3, 5 and 6.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.runner import run_session
from rota.core.scheduler import open_tips
from rota.llm.llm import Pins, ScriptedBackend
from rota.roles.principal import land, parse_reply, pending_asks, render_page
from rota.testkit.fixtures import seed_provenance
from rota.roles.principal import verdict_for

PINS = Pins(model="stub", temperature=0.0)

ITEM = "confirm_default_on_eof"
TICKET = "tk_1_confirm_default_on_eof"
HEAD = "6ea9f9039c5f956f05d5e0f7a3db40eccc5630e1"
# The criteria at the night's end (night 149, `criteria`).
CRITERIA = (
    ("cr_1_confirm_default_on_eof",
     "When 'default_on_eof' is True and stdin is closed, confirm() returns the "
     "default passed to confirm itself instead of aborting."),
    ("cr_2_confirm_default_on_eof",
     "The 'default_on_eof' argument defaults to False; when it is True and stdin "
     "is closed, confirm() returns the default passed to confirm itself instead "
     "of aborting."),
    ("cr_3_confirm_default_on_eof",
     "When 'default_on_eof' is True and stdin is closed, confirm() returns the "
     "default passed to confirm itself (not an option's default)."),
    ("cr_4_confirm_default_on_eof",
     "The 'default_on_eof' parameter defaults to False; when it is True and "
     "stdin is closed, confirm() returns the default passed to confirm itself "
     "instead of aborting."),
    ("cr_5_confirm_default_on_eof",
     "When default_on_eof is True and stdin is closed (simulated by empty input "
     "in tests), confirm() returns the default passed to confirm itself instead "
     "of raising a UsageError."),
    ("cr_6_confirm_default_on_eof",
     "When default_on_eof is True and stdin is closed, confirm() returns the "
     "default passed to confirm itself instead of raising a UsageError."),
)
# bg_2's `batch_touch` rows at the night's end.
TOUCH = ("src/click/termui.py", "src/click/utils.py", "tests/test_defaults.py",
         "tests/test_utils/test_confirm.py")
# m92, the principal's reply to m91.
M92 = ("Please keep going rather than drop this; for lines 3 and 5, a simple check "
       "will do: run confirm through the test runner with empty input and the flag "
       "left off, and expect it to abort as it does today. Lines 2 through 7 still "
       "say confirm raises a usage error, but today it aborts. Line 8 should touch "
       "only the termui code and the existing termui tests, not utils, the defaults "
       "tests or a new test file.")
# m105, the principal's reply to m91 after the shift page. It names no line 8.
M105 = ("Lines 3 and 5 can be checked simply: call confirm without the flag while "
        "stdin is closed, and expect it to abort the same way it does today. Lines "
        "2, 3, 5, 6 and 7 are also wrong to say \"instead of raising a UsageError\", "
        "because confirm aborts on closed stdin and does not raise that error. "
        "Please fix those lines and keep going with the change, not drop it.")
# s199's call at turn 1 on m92, and s212's call at turn 1 on m105.
MAP = {"1": "approve", "2": "contest", "3": "contest", "4": "approve",
       "5": "contest", "6": "approve", "7": "approve", "8": "contest"}
# MAP approves lines 4, 6 and 7, and m92's "Lines 2 through 7 still say"
# faults them. Frame 250's door refuses that approve, so the line 8 tests
# rule lines 2 to 7 as the words say.
M92_MAP = dict(MAP, **{"4": "contest", "6": "contest", "7": "contest"})


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


@pytest.fixture
def m91(db):
    """bg_2 at its head commit, running, and the open page m91."""
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version, "
               "priority) VALUES (?, ?, 'in_scope', 'approved', 3, 3, 1)",
               (ITEM, "Let confirm() take a default_on_eof flag: when stdin is "
                      "closed it returns the default instead of aborting. The flag "
                      "default is passed to confirm itself."))
    seed_provenance(db, "items", ITEM, "decided")
    db.execute("INSERT INTO tickets (id, item_id, text, version, item_ver) "
               "VALUES (?, ?, ?, 1, 2)",
               (TICKET, ITEM, "let confirm() take a default_on_eof flag: when "
                              "stdin is closed it returns the default instead of "
                              "aborting"))
    for cid, text in CRITERIA:
        db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, ?, ?)",
                   (cid, TICKET, text))
    db.execute("INSERT INTO batches (id, item_id, head_commit, status, version) "
               "VALUES ('bg_2', ?, ?, 'running', 1)", (ITEM, HEAD))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('bg_2', ?)",
               (TICKET,))
    for grain in TOUCH:
        db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind, confidence) "
                   "VALUES ('bg_2', ?, 'path', 'expected')", (grain,))
        db.execute("INSERT INTO code_index (grain, grain_kind) VALUES (?, 'path')",
                   (grain,))
    refs = ["bg_2", ITEM] + [c for c, _ in CRITERIA]
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, status, seq) VALUES ('m91', 'm91', 'liaison', "
               "'principal', 'present', ?, 'open', 1)", (json.dumps(refs),))
    db.commit()
    return db


def _reply(db, words: str) -> str:
    (ask,) = [a for a in pending_asks(db) if a.message_id == "m91"]
    reply = land(db, ask, parse_reply(ask, words))
    db.commit()
    return reply


def _sandbox(db, trigger: str):
    from rota.core.sandbox import build
    from rota.roles import prompts

    sb = build("liaison", db, mode="landing", allow=prompts.mode_tools("liaison", "landing"))
    sb.ctx.trigger = trigger
    return sb


def test_the_page_numbers_bg_2_as_line_8(m91):
    _, order = render_page(m91, "present", json.loads(m91.execute(
        "SELECT body_refs FROM messages WHERE id = 'm91'").fetchone()["body_refs"]),
        ask_id="m91")
    assert order == [ITEM] + [c for c, _ in CRITERIA] + ["bg_2"]


def test_m92s_files_correction_lands_as_a_contest_of_bg_2(m91):
    """s199 on m92. The door refused line 8 three times, and the reply
    landed no ruling row (frame 255)."""
    sb = _sandbox(m91, _reply(m91, M92))
    out = sb.call("rulings.rule", rulings=M92_MAP, words=M92)
    assert out["per_item"]["bg_2"] == "contest"
    assert out["per_item"][ITEM] == "approve"


def test_land_keeps_bg_2_and_the_relay_reaches_the_architect(m91):
    """The row `rulings_rule` admits stays in the verdict after the head
    commit, and the relay takes bg_2 to the Architect (frame 255's scope,
    section 3)."""
    reply = _reply(m91, M92)
    (wake,) = [w for w in open_tips(m91) if w.message_id == reply]
    call = f"TOOL: rulings.rule(rulings={json.dumps(M92_MAP)}, words={M92!r})"
    out = run_session(m91, wake, backend=ScriptedBackend([call, "done"]),
                      pins=PINS, instructions="land")
    assert out.committed, out.errors
    verdict = m91.execute("SELECT id FROM messages WHERE cause_id = 'm91' "
                          "AND verb = 'verdict'").fetchone()
    assert verdict is not None
    ruled = verdict_for(m91, verdict['id'])
    assert ruled.get("bg_2") == "contest", ruled

    (wake,) = [w for w in open_tips(m91) if w.message_id == verdict["id"]]
    out = run_session(m91, wake, backend=ScriptedBackend(
        ['TOOL: msg.relay_architect(refs=["bg_2"])', "done"]), pins=PINS,
        instructions="relay")
    assert out.committed, out.errors
    relays = [json.loads(r["body_refs"]) for r in m91.execute(
        "SELECT body_refs FROM messages WHERE cause_id = ? AND verb = 'relay' "
        "AND to_role = 'architect'", (verdict["id"],))]
    assert relays == [["bg_2"]], relays


def test_m105_does_not_fault_line_8_and_is_still_refused(m91):
    """s212 on m105. The words fault lines 2, 3, 5, 6 and 7 and not line 8,
    so the contest of line 8 was the seat's error and the door holds."""
    sb = _sandbox(m91, _reply(m91, M105))
    with pytest.raises(ValueError) as refused:
        sb.call("rulings.rule", rulings=MAP, words=M105)
    assert str(refused.value) == (
        "line 8: the words do not fault bg_2's files. Approve line 8.")


def test_a_contest_at_a_list_item_s_range_passes_the_built_batch_filter():
    """Frame 282, review 1, finding 1: `land` keeps a contest of a built batch
    at lines 11 to 14 when the words fault them as a list item's range. The
    filter read line 10 alone before. Night 154's m175 and m176 hold the
    range but no fault cue after it, so the filter keeps none of their lines.
    The words here add the cue "wrong"."""
    from rota.roles.api import _line_reading, built_line_faulted

    words = "Notes 6, 7 and 10 to 14 are wrong for this change."
    order = [f"bg_{n}" for n in range(1, 15)]
    faulted = _line_reading(words)[0]
    kept = [ref for ref in order
            if built_line_faulted(words, order, ref, faulted)]
    assert kept == ["bg_6", "bg_7", "bg_10", "bg_11", "bg_12", "bg_13", "bg_14"]
