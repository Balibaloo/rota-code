"""
Night 171: a deliver wake rewrote the approved account row.

s152, a Vision Keeper, was woken by m53, a Liaison deliver that named the
ledger row l_0cfe6f462c and no statement. It asserted `how_it_works` with
new words three times, and every door let the text pass. The doors compare
words only, and nothing checked whether the wake may change the row
(plans/night171-how-it-works-read.md, sections 1 and 6, Part A).
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.predicates import Wake
from rota.core.sandbox import build
from rota.roles import prompts
from rota.testkit.fixtures import seed_provenance

# The account on file before s152, taken to be s98's text (the read, doubt 2).
V2 = ("Click is a Python toolkit for building command-line interfaces. Users "
      "write scripts that define commands and options, and Click turns what "
      "the user types into calls to those functions.")
# s152's text, seq 6, 10 and 11.
S152 = ("The program is a command-line interface toolkit called Click. Users "
        "write scripts that define commands and options, and Click parses "
        "command-line arguments and options, then executes the corresponding "
        "Python functions with the provided inputs.")
# The deliver brief's route, word for word.
ROUTE = ("Assert it as its own item, with an id that names the behaviour, "
         "one `problem.assert` per distinct thing.")


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version, is_description) VALUES ('how_it_works', ?, "
                 "'in_scope', 'approved', 2, 2, 1)", (V2,))
    seed_provenance(conn, "items", "how_it_works", "observed")
    conn.commit()
    return conn


def _m53(conn):
    """s152's wake: a Liaison deliver that names a ledger row only."""
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                 "verb, body_refs, seq) VALUES ('m53', 't53', 'liaison', "
                 "'vision_keeper', 'deliver', ?, 53)",
                 (json.dumps(["l_0cfe6f462c"]),))
    conn.commit()
    sb = build("vision_keeper", conn, mode="deliver",
               allow=prompts.mode_tools("vision_keeper", "deliver"),
               wake=Wake("vision_keeper", "message", message_id="m53",
                         detail="deliver"))
    sb.ctx.trigger = "m53"
    return sb


def _items(sb):
    return [w for w in sb.ctx.writes if w[0] == "items"]


def test_s152_a_deliver_wake_keeps_the_observed_account(db):
    sb = _m53(db)
    with pytest.raises(ValueError) as err:
        sb.call("problem.assert", id="how_it_works", kind="in_scope",
                text=S152)
    msg = str(err.value)
    assert ROUTE in msg
    assert "Amend the account" not in msg
    assert not _items(sb)


def test_an_onboarding_wake_amends_the_observed_account(db):
    sb = build("vision_keeper", db, mode="reorient", onboarding=True,
               allow=prompts.mode_tools("vision_keeper", "reorient"))
    out = sb.call("problem.assert", id="how_it_works", kind="in_scope",
                  text=S152)
    assert out["id"] == "how_it_works"
    assert [w[2]["text"] for w in _items(sb)] == [S152]


def test_the_account_door_no_longer_invites_an_amendment(db):
    # The door's last sentence came from a fix commit, not a ruling
    # (the read, section 6, Part A). A reasoned account still meets the door.
    db.execute("UPDATE items SET is_description = 0 WHERE id = 'how_it_works'")
    db.execute("DELETE FROM refs WHERE src_table = 'items' "
               "AND src_id = 'how_it_works'")
    db.commit()
    sb = _m53(db)
    with pytest.raises(ValueError, match="account of the whole program") as err:
        sb.call("problem.assert", id="how_it_works", kind="in_scope",
                text="The software exports every recipe as a csv file.")
    assert "Amend the account" not in str(err.value)
