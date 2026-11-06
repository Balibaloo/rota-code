"""
Frame 362, slice 1: a contest of his on the code line stays owed until a row
of the line's owner carries the ruling.

The design is `plans/design-contested-record-2026-11-06.md`, revision 2. The
rows are dry run 6b's m26 to m29 and m31 to m45, copied as literals from
`dry6b.db` read with `immutable=1` on 2026-11-06. No test reads a run
database. He called the guess wrong on m27, s145 wrote nothing, s150 copied
the old guess into `batch_touch`, and three Developers started on it.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import SessionResult, init_db, ruled_ref_id, session_commit
from rota.core.runner import _as_write, _guess_seed, resolve_inbound
from rota.core.sandbox import build
from rota.core.scheduler import (Wake, next_batch, owed, owed_key, owed_park,
                                 park_rows, parked)
from rota.roles import prompts

ITEM = "folds_long_lines_in_icalendar"
KEY = f"guess:{ITEM}"
TEXT = ("When icalendar writes a long line, fold it at a space where it can, so "
        "that a word is not split, and keep everything else as before.")
# m27, his reply to the sign-off page m26 (dry 6b, `messages`).
M27 = ("Line 2 is wrong. The fold is _foldline in src/icalendar/parser/string.py, "
       "and its tests are in src/icalendar/tests/test_icalendar.py. Do not touch "
       "parameter.py or property.py.")
M39 = M27.replace("Line 2", "Line 5")
# The Architect's sign-off guess, all `ruling_id` '' (dry 6b, `touch_guesses`).
GUESS = (
    ("src/icalendar/parser/property.py", "path", "expected"),
    ("src/icalendar/tests/prop/test_common_functionality.py", "path", "expected"),
    ("src/icalendar/tests/prop/test_crlf_in_values.py", "path", "expected"),
    ("src/icalendar/tests/rfc_7265_jcal/test_section_3_6_values.py", "path", "expected"),
    ("src/icalendar/parser/property.py::split_on_unescaped_comma", "symbol", "possible"),
    ("src/icalendar/parser/property.py::split_on_unescaped_semicolon", "symbol", "possible"),
)
HIS = ["src/icalendar/parser/string.py", "src/icalendar/tests/test_icalendar.py"]


def _msg(db, mid, frm, to, verb, refs, cause=None, status="answered", seq=0):
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_refs, seq, status) VALUES (?, ?, 't', ?, ?, ?, ?, ?, ?)",
               (mid, cause, frm, to, verb, json.dumps(refs), seq, status))


def _ruling(db, rid, reply, verdict, per_item, words, rows=()):
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, status, "
               "verdict_id) VALUES (?, ?, ?, ?, ?, 'landed', ?)",
               (rid, reply, reply, json.dumps(per_item), words, verdict))
    for ref, line, verb in rows:
        db.execute("INSERT INTO ruled_refs (id, ruling_id, ref, line, verdict, act, "
                   "target_kind, words, source) VALUES (?, ?, ?, ?, ?, 'rewrite', "
                   "'row', ?, 'landed')",
                   (ruled_ref_id(rid, ref), rid, ref, line, verb, words.split(".")[0] + "."))
    if verdict:
        db.execute("INSERT INTO config (key, value) VALUES (?, ?)",
                   (f"entry:{verdict}", json.dumps(words)))


@pytest.fixture
def db(tmp_path):
    """Dry 6b after s149: r_m27 landed, m29 answered, b_1 pending."""
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES (?, ?, 'in_scope', 'approved', 1, 1)", (ITEM, TEXT))
    for grain, kind, _ in GUESS + tuple((p, "path", "expected") for p in HIS):
        conn.execute("INSERT OR IGNORE INTO code_index (grain, grain_kind) VALUES (?, ?)",
                     (grain, kind))
    for grain, kind, conf in GUESS:
        conn.execute("INSERT INTO touch_guesses (item_id, item_ver, grain, grain_kind, "
                     "confidence) VALUES (?, 1, ?, ?, ?)", (ITEM, grain, kind, conf))
    _msg(conn, "m26", "liaison", "principal", "present", [ITEM, KEY], seq=26)
    _msg(conn, "m27", "principal", "liaison", "converse", [ITEM, KEY], "m26", seq=27)
    _msg(conn, "m28", "principal", "liaison", "verdict", [ITEM, KEY], "m26", seq=28)
    _msg(conn, "m29", "liaison", "architect", "relay", [KEY], "m28", seq=29)
    _ruling(conn, "r_m27", "m27", "m28", {KEY: "contest", ITEM: "approve"}, M27,
            rows=[(KEY, 2, "contest")])
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES ('b_1', ?, 'pending')",
                 (ITEM,))
    conn.commit()
    return conn


def _s150(db, ruling=""):
    """s150's write: the old guess copied whole into `batch_touch`."""
    for grain, kind, conf in GUESS:
        db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind, confidence, "
                   "ruling_id) VALUES ('b_1', ?, ?, ?, ?)", (grain, kind, conf, ruling))
    db.commit()


def _architect(db, mode, wake, trigger=None):
    sb = build("architect", db, mode=mode, session_id="s1", wake=wake,
               allow=prompts.mode_tools("architect", mode))
    sb.ctx.trigger = trigger
    return sb


def _commit(db, sb, kind, refs):
    session_commit(db, SessionResult(
        session_id="s1", role="architect", wake_kind=kind, wake_refs=refs,
        writes=[_as_write(w) for w in sb.ctx.writes]))


def _second_contest(db, verdict="m40", per=None):
    """A later contest of his on the code line, as r_m39 on dry 6b."""
    _msg(db, "m31", "liaison", "principal", "present", ["b_1", ITEM], seq=31)
    _msg(db, verdict, "principal", "liaison", "verdict", ["b_1"], "m31", seq=40)
    _ruling(db, "r_m39", "m31", verdict, per or {"b_1": "contest"}, M39,
            rows=[("b_1", 5, "contest")])
    db.commit()


# ---------------------------------------------------------------------------
# The fact
# ---------------------------------------------------------------------------

def test_the_contest_on_the_guess_line_is_owed_with_no_rewrite(db):
    found = owed(db, ITEM)
    assert (found["ruling"], found["verdict"], found["verb"], found["line"],
            found["ref"]) == ("r_m27", "m28", "contest", "guess", KEY)
    assert owed(db, KEY) == found and owed(db, "b_1") == found


def test_the_copy_of_the_old_set_discharges_nothing(db):
    _s150(db)
    assert owed(db, ITEM)["verdict"] == "m28"


def test_a_set_that_carries_the_verdict_discharges_it(db):
    db.execute("INSERT INTO touch_guesses (item_id, item_ver, ruling_id, grain, "
               "grain_kind) VALUES (?, 1, 'm28', ?, 'path')", (ITEM, HIS[0]))
    assert owed(db, ITEM) is None


def test_a_stamped_batch_set_discharges_it(db):
    _s150(db, ruling="m28")
    assert owed(db, ITEM) is None


def test_a_revise_is_owed_and_an_approve_or_no_verdict_is_not(db):
    db.execute("UPDATE rulings SET per_item = ?", (json.dumps({KEY: "revise"}),))
    assert owed(db, ITEM)["verb"] == "revise"
    db.execute("UPDATE rulings SET verdict_id = NULL")
    assert owed(db, ITEM) is None
    db.execute("UPDATE rulings SET verdict_id = 'm28', per_item = ?",
               (json.dumps({KEY: "approve"}),))
    assert owed(db, ITEM) is None


def test_a_second_contest_replaces_the_first(db):
    _second_contest(db)
    found = owed(db, ITEM)
    assert (found["ruling"], found["verdict"], found["line"], found["ref"]) == (
        "r_m39", "m40", "batch", "b_1")
    # A late write under the first verdict discharges nothing.
    db.execute("INSERT INTO touch_guesses (item_id, item_ver, ruling_id, grain, "
               "grain_kind) VALUES (?, 1, 'm28', ?, 'path')", (ITEM, HIS[0]))
    assert owed(db, ITEM)["verdict"] == "m40"


# ---------------------------------------------------------------------------
# The stamp and the clear
# ---------------------------------------------------------------------------

def test_the_relay_write_carries_the_verdict(db):
    db.execute("UPDATE messages SET status = 'open' WHERE id = 'm29'")
    sb = _architect(db, "guess", Wake("architect", "message", message_id="m29"),
                    trigger="m29")
    sb.call("batches.guess", item_id=ITEM, paths=HIS)
    _commit(db, sb, "message", (KEY,))
    assert {r[0] for r in db.execute("SELECT ruling_id FROM touch_guesses "
                                     "WHERE grain IN (?, ?)", HIS)} == {"m28"}
    assert owed(db, ITEM) is None


def test_the_tick_write_carries_the_verdict(db):
    wake = Wake("architect", "tick:guess", refs=(ITEM, "m28"))
    sb = _architect(db, "guess", wake)
    sb.call("batches.guess", item_id=ITEM, paths=HIS)
    _commit(db, sb, "tick:guess", wake.refs)
    assert owed(db, ITEM) is None


def test_a_plain_tick_write_carries_no_verdict(db):
    db.execute("UPDATE rulings SET per_item = ?", (json.dumps({KEY: "approve"}),))
    wake = Wake("architect", "tick:annotate", refs=("b_1",))
    sb = _architect(db, "annotate", wake)
    sb.call("batches.annotate", batch_id="b_1", paths=HIS)
    _commit(db, sb, "tick:annotate", wake.refs)
    assert {r[0] for r in db.execute("SELECT ruling_id FROM batch_touch")} == {""}


def test_a_tick_rewrite_of_the_batch_line_clears_the_set_and_stamps_it(db):
    _s150(db)
    _second_contest(db)
    wake = Wake("architect", "tick:annotate", refs=("b_1", "m40"))
    sb = _architect(db, "annotate", wake)
    sb.call("batches.annotate", batch_id="b_1", paths=HIS)
    _commit(db, sb, "tick:annotate", wake.refs)
    rows = sorted(tuple(r) for r in db.execute(
        "SELECT grain, ruling_id FROM batch_touch"))
    assert rows == [(HIS[0], "m40"), (HIS[1], "m40")]
    assert owed(db, ITEM) is None


# ---------------------------------------------------------------------------
# The equal-set door
# ---------------------------------------------------------------------------

def test_the_door_refuses_the_contested_set_under_a_contest(db):
    sb = _architect(db, "guess", Wake("architect", "tick:guess", refs=(ITEM, "m28")))
    with pytest.raises(Exception, match="the same set"):
        sb.call("batches.guess", item_id=ITEM,
                paths=[g for g, k, _ in GUESS if k == "path"],
                symbols=[g for g, k, _ in GUESS if k == "symbol"])


def test_the_door_admits_the_same_set_under_a_revise(db):
    db.execute("UPDATE rulings SET per_item = ?", (json.dumps({KEY: "revise"}),))
    sb = _architect(db, "guess", Wake("architect", "tick:guess", refs=(ITEM, "m28")))
    out = sb.call("batches.guess", item_id=ITEM,
                  paths=[g for g, k, _ in GUESS if k == "path"],
                  symbols=[g for g, k, _ in GUESS if k == "symbol"])
    assert out["grains"] == 6


# ---------------------------------------------------------------------------
# The tick and its inbound
# ---------------------------------------------------------------------------

def _guess_wakes(db):
    from rota.core.predicates import guess
    return [(w.role, w.kind, w.refs) for w in guess(db)]


def test_the_guess_tick_carries_the_item_and_the_verdict(db):
    assert _guess_wakes(db) == [("architect", "tick:guess", (ITEM, "m28"))]


def test_the_guess_tick_waits_behind_an_open_relay(db):
    db.execute("UPDATE messages SET status = 'open' WHERE id = 'm29'")
    assert _guess_wakes(db) == []


def test_the_tick_inbound_holds_his_words_and_verdict_and_no_old_set(db):
    inbound = resolve_inbound(db, Wake("architect", "tick:guess", refs=(ITEM, "m28")))
    assert inbound["principal_said"] == M27
    assert inbound["principal_verdict"] == {KEY: "contest"}
    assert inbound["disputed"] == []
    assert inbound["item"]["id"] == ITEM
    assert "guess" not in inbound


def test_the_seed_under_an_owed_ruling_is_his_words_and_no_path(db):
    assert _guess_seed(db, "b_1") == {"paths": [], "symbols": [],
                                      "the principal said": M27}


# ---------------------------------------------------------------------------
# The readers that start work
# ---------------------------------------------------------------------------

def test_annotate_does_not_fire_while_the_guess_line_is_owed(db):
    from rota.core.predicates import annotate
    assert annotate(db) == []
    db.execute("INSERT INTO touch_guesses (item_id, item_ver, ruling_id, grain, "
               "grain_kind) VALUES (?, 1, 'm28', ?, 'path')", (ITEM, HIS[0]))
    assert [w.refs for w in annotate(db)] == [("b_1",)]


def test_touch_note_and_next_batch_leave_the_owed_batch_out(db):
    from rota.core.predicates import touch_note
    _s150(db)
    assert touch_note(db) == []
    assert next_batch(db) == []
    db.execute("UPDATE batch_touch SET ruling_id = 'm28'")
    assert [r["id"] for r in next_batch(db)] == ["b_1"]
    assert [w.refs for w in touch_note(db)] == [("b_1", ITEM)]


# ---------------------------------------------------------------------------
# The park, its page and the second contest
# ---------------------------------------------------------------------------

def _spend(db, key):
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined) "
               "VALUES (?, 3, 1)", (key,))
    db.commit()


def test_a_spent_key_parks_the_item_and_owes_the_page(db):
    from rota.core.predicates import park_ask
    from rota.roles.principal import _park_page

    key = owed_key(owed(db, ITEM))
    assert key == f"architect|tick:guess|{ITEM},m28"
    assert not parked(db, "b_1")
    _spend(db, key)
    assert owed_park(db, "b_1") == key and parked(db, "b_1")
    # The spent key wakes nothing more, so another item's wake can come.
    assert _guess_wakes(db) == []
    assert [w.refs for w in park_ask(db)] == [(ITEM, "b_1")]
    assert park_rows(db, "b_1") == [ITEM, KEY]
    text, order = _park_page(db, "b_1", [ITEM, KEY])
    assert order == [ITEM, KEY]
    assert text.splitlines() == [
        "This change waits before it starts. You corrected the team's guess at "
        "the code it touches, and the team did not write a new one in 3 attempts.",
        f'You said: "{M27}"',
        "You asked:",
        f"  1. {TEXT}",
        "  2. The team's guess at the code this touches: "
        + ", ".join(g for g, k, _ in GUESS if k == "path")
        + ". It might touch " + ", ".join(g for g, k, _ in GUESS if k == "symbol") + ".",
        "Name the files on line 2 again, and the team writes the plan from your "
        "words. Or say that you give the request up.",
        "Nothing else waits on you. The other requests go on.",
    ]


def test_a_second_contest_gets_a_fresh_key_and_ends_the_park(db):
    _spend(db, f"architect|tick:guess|{ITEM},m28")
    assert parked(db, "b_1")
    _second_contest(db, per={KEY: "contest"})
    assert not parked(db, "b_1")
    assert _guess_wakes(db) == [("architect", "tick:guess", (ITEM, "m40"))]
