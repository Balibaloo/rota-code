"""
A batch delivers exactly one approved item, and the door says so.

Measured on a cold walk (tipsE, 2026-09-08): the Architect grouped two tickets
from two items under an invented item id. The existence check refused the id
and listed the items that exist. Nothing said the rule or how to split. Three
tries, then quarantine, then the seat said "nothing is building".
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.predicates import Wake
from rota.core.runner import run_session
from rota.llm.llm import Pins, ScriptedBackend
from rota.roles.principal import render_state

PINS = Pins(model="stub", temperature=0.0)


@pytest.fixture
def db(tmp_path):
    db = init_db(tmp_path / "rota.db")
    for iid in ("calculate_tip", "display_results"):
        db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
                   "approval_ver, version) VALUES (?, ?, 'in_scope', 'decided', "
                   "'approved', 1, 1)", (iid, iid.replace("_", " ")))
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_1','calculate_tip','calc')")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_2','display_results','show')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c_1','tk_1','it calculates')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('c_2','tk_2','it shows')")
    db.commit()
    return db


def test_an_invented_item_id_is_refused_with_the_rule_and_the_split(db):
    bad = ("TOOL: batches.group(id='batch_1', "
           "item_id='calculate_tip_and_display_results', ticket_ids=['tk_1','tk_2'])")
    out = run_session(db, Wake("architect", "tick:grouping", refs=("tk_1", "tk_2")),
                      backend=ScriptedBackend([bad, "done"]), pins=PINS,
                      instructions="group")
    err = next((e for e in out.errors if "exactly one approved item" in e), "")
    assert err, out.errors
    assert "item_id='calculate_tip' with ticket_ids=['tk_1']" in err
    assert "item_id='display_results' with ticket_ids=['tk_2']" in err
    assert "Do not invent an item id" in err


def test_one_batch_per_item_lands(db):
    good = ("TOOL: batches.group(id='batch_1', item_id='calculate_tip', ticket_ids=['tk_1'])\n"
            "TOOL: batches.group(id='batch_2', item_id='display_results', ticket_ids=['tk_2'])")
    out = run_session(db, Wake("architect", "tick:grouping", refs=("tk_1", "tk_2")),
                      backend=ScriptedBackend([good, "done"]), pins=PINS,
                      instructions="group")
    assert out.committed, out.errors
    assert db.execute("SELECT COUNT(*) FROM batches").fetchone()[0] == 2


def test_the_state_names_what_the_team_gave_up_on(db):
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined) VALUES "
               "('architect|tick:grouping|tk_1,tk_2', 3, 1)")
    db.commit()
    state = render_state(db)
    assert state.startswith("Stuck before building."), state
    assert "grouping for tk_1,tk_2" in state
    assert "Tell me what to change." in state
