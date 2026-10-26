"""
Frame 338: an approved test row adds no criterion to the relay.

The rows copy night 168's m47, m49 and m50 as `plans/c3-relay-provenance.md`
quotes them, question 3. His verdict m49 revises `tst_crit_1` and
`tst_crit_2`, approves `tst_crit_3` and approves every criterion. s156 sent
`msg.relay_architect(["tst_crit_1", "tst_crit_2"])`. The split took crit_3
through the approved `tst_crit_3`, and s157 woke in `relay`, where no call
reaches the Tester.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.runner import _mode_key, run_session
from rota.core.scheduler import Wake, open_tips, park_criterion_relay
from rota.llm.llm import Pins, ScriptedBackend
from rota.testkit.fixtures import seed_provenance

PINS = Pins(model="stub", temperature=0.0)

ITEM = "version_option_show_python"
CRITERIA = ("crit_1", "crit_2", "crit_3")
TESTS = ("tst_crit_1", "tst_crit_2", "tst_crit_3")
TERM = "g_show_python"


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _message(db, mid: str, sender: str, to: str, verb: str, refs, cause=None,
             status: str = "answered") -> None:
    seq = db.execute("SELECT COALESCE(MAX(seq), 0) + 1 n FROM messages").fetchone()["n"]
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, verb, "
               "body_refs, status, seq) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
               (mid, cause, cause or mid, sender, to, verb, json.dumps(refs), status, seq))


def _night168(db, ruling: dict, extra=()) -> None:
    """The request, its three criteria and their tests, the page m47 and
    his verdict m49 with `ruling` as `config` `verdict:m49`."""
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version, "
               "priority, is_description) VALUES (?, 'the request', 'in_scope', "
               "'approved', 1, 1, 1, 0)", (ITEM,))
    seed_provenance(db, "items", ITEM, "decided")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_1', ?, 'the ticket')",
               (ITEM,))
    db.execute("INSERT INTO batches (id, item_id, status, head_commit) VALUES "
               "('bg_1', ?, 'running', 'aa28d1d')", (ITEM,))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('bg_1', 'tk_1')")
    for cid, tid in zip(CRITERIA, TESTS):
        db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, 'tk_1', ?)",
                   (cid, f"the words of {cid}"))
        db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body, version) "
                   "VALUES (?, 'bg_1', ?, 'tests/test_x.py', 'def test_x(): pass', 1)",
                   (tid, cid))
    # The record quotes the criteria and test rows of m49 and no item row.
    lines = [*CRITERIA, *TESTS, *extra]
    _message(db, "m47", "liaison", "principal", "present", lines)
    _message(db, "m49", "principal", "liaison", "verdict", lines, cause="m47",
             status="open")
    db.execute("INSERT INTO config (key, value) VALUES ('verdict:m49', ?)",
               (json.dumps(ruling),))
    db.commit()


def _relay(db, call: str) -> list[tuple[str, str, list[str]]]:
    """s156: the Liaison's relay of m49, run with a scripted model."""
    (wake,) = [w for w in open_tips(db) if w.message_id == "m49"]
    out = run_session(db, wake, backend=ScriptedBackend([call, "done"]),
                      pins=PINS, instructions="relay")
    assert out.committed, out.errors
    return [(r["id"], r["to_role"], json.loads(r["body_refs"])) for r in db.execute(
        "SELECT id, to_role, body_refs FROM messages WHERE cause_id = 'm49' "
        "AND verb = 'relay' ORDER BY seq")]


def _terminologist_mode(db, relay_id: str) -> str:
    return _mode_key(Wake("terminologist", "message", refs=(), detail="relay",
                          message_id=relay_id), db)


def test_night168_m50_carries_the_revised_tests_criteria_only(db):
    """Red on 07c34293: m50 carried crit_1, crit_2 and crit_3, and s157
    keyed `relay`."""
    ruling = {"tst_crit_1": "revise", "tst_crit_2": "revise",
              "tst_crit_3": "approve",
              **{c: "approve" for c in CRITERIA}}
    _night168(db, ruling)
    relays = _relay(db, 'TOOL: msg.relay_architect(refs=["tst_crit_1", "tst_crit_2"])')
    assert [(to, refs) for _, to, refs in relays] == [
        ("terminologist", ["crit_1", "crit_2"])]
    assert park_criterion_relay(db, relays[0][0])
    assert _terminologist_mode(db, relays[0][0]) == "criterion_repair"


def test_a_relay_of_a_contested_criterion_alone_keys_criterion_repair(db):
    """A contest of one criterion line and approves of the rest keep the
    route of frame 190's design, 2.2.7."""
    ruling = {"crit_1": "contest",
              **{c: "approve" for c in CRITERIA[1:]},
              **{t: "approve" for t in TESTS}}
    _night168(db, ruling)
    relays = _relay(db, 'TOOL: msg.relay_terminologist(refs=["crit_1"])')
    assert [(to, refs) for _, to, refs in relays] == [("terminologist", ["crit_1"])]
    assert park_criterion_relay(db, relays[0][0])
    assert _terminologist_mode(db, relays[0][0]) == "criterion_repair"


def test_a_relay_of_a_term_and_no_ruled_criterion_keys_relay(db):
    """A term needs `glossary.adopt`, which the repair mode lacks (the diff
    review of b0a2086e, finding 1)."""
    db.execute("INSERT INTO glossary_terms (id, term, sense_short) VALUES "
               "(?, 'show_python', 'the flag that prints the interpreter version')",
               (TERM,))
    _night168(db, {TERM: "contest"}, extra=(TERM,))
    _message(db, "m50", "liaison", "terminologist", "relay", [TERM], cause="m49",
             status="open")
    db.commit()
    assert not park_criterion_relay(db, "m50")
    assert _terminologist_mode(db, "m50") == "relay"
