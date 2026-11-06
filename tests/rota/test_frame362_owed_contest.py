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
    assert owed(db, ITEM)["verdict"] == "m28"
    db.execute("INSERT INTO touch_guesses (item_id, item_ver, ruling_id, grain, "
               "grain_kind) VALUES (?, 1, 'm28', ?, 'path')", (ITEM, HIS[0]))
    assert owed(db, ITEM) is None


def test_a_stamped_batch_set_discharges_it(db):
    _s150(db)
    assert owed(db, ITEM)["verdict"] == "m28"
    db.execute("UPDATE batch_touch SET ruling_id = 'm28'")
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
    assert owed(db, ITEM)["verdict"] == "m28"
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
    assert owed(db, ITEM)["verdict"] == "m28"
    sb.call("batches.guess", item_id=ITEM, paths=HIS)
    _commit(db, sb, "tick:guess", wake.refs)
    assert sorted(tuple(r) for r in db.execute(
        "SELECT grain, ruling_id FROM touch_guesses WHERE ruling_id != ''")) == [
        (HIS[0], "m28"), (HIS[1], "m28")]
    assert owed(db, ITEM) is None


def test_a_plain_tick_write_carries_no_verdict(db):
    # A tick with no verdict in its refs writes no stamp, also while his
    # contest is owed, so the fact stays.
    _second_contest(db)
    wake = Wake("architect", "tick:annotate", refs=("b_1",))
    sb = _architect(db, "annotate", wake)
    sb.call("batches.annotate", batch_id="b_1", paths=HIS)
    _commit(db, sb, "tick:annotate", wake.refs)
    assert sorted(tuple(r) for r in db.execute(
        "SELECT grain, ruling_id FROM batch_touch")) == [(HIS[0], ""), (HIS[1], "")]
    assert owed(db, ITEM)["verdict"] == "m40"


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
    assert owed(db, ITEM)["verb"] == "revise"
    out = sb.call("batches.guess", item_id=ITEM,
                  paths=[g for g, k, _ in GUESS if k == "path"],
                  symbols=[g for g, k, _ in GUESS if k == "symbol"])
    assert out["grains"] == 6
    _commit(db, sb, "tick:guess", (ITEM, "m28"))
    assert {r[0] for r in db.execute("SELECT ruling_id FROM touch_guesses "
                                     "WHERE rowid > 6")} == {"m28"}


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
    db.execute("UPDATE messages SET status = 'answered' WHERE id = 'm29'")
    db.execute("UPDATE messages SET status = 'open' WHERE id = 'm28'")
    assert _guess_wakes(db) == []
    db.execute("UPDATE messages SET status = 'answered' WHERE id = 'm28'")
    assert _guess_wakes(db) == [("architect", "tick:guess", (ITEM, "m28"))]


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
    _woke(db)
    text, order = _park_page(db, "b_1", [ITEM, KEY])
    assert order == [ITEM, KEY]
    assert text.splitlines() == PAGE


# The park page of an owed guess line. It shows no contested set, and it
# asks for no files that his reply named already (pass 2, finding 5). The
# count is the relay and the three ticks of `_woke` (pass 3, item 2).
PAGE = [
    "This change waits before it starts.",
    "You corrected the team's guess at the code this request touches. The team "
    "tried 4 times, and it did not rewrite the guess.",
    f'You said: "{M27}"',
    "You asked:",
    f"  1. {TEXT}",
    "  2. The code this request touches. It waits for the team's rewrite.",
    "Reply to line 2 to say again what to change, and the team tries again. Or "
    "say that you give the request up.",
    "Nothing else waits on you. The other requests go on.",
]


def test_a_second_contest_gets_a_fresh_key_and_ends_the_park(db):
    _spend(db, f"architect|tick:guess|{ITEM},m28")
    assert parked(db, "b_1")
    _second_contest(db, per={KEY: "contest"})
    assert not parked(db, "b_1")
    assert _guess_wakes(db) == [("architect", "tick:guess", (ITEM, "m40"))]


# ---------------------------------------------------------------------------
# Pass 2: the review of 36a2edd2
# ---------------------------------------------------------------------------

def _approve_batch(db):
    """r_m54 of dry 6b: his approve of the batch line on page m53."""
    _msg(db, "m53", "liaison", "principal", "present", ["b_1", ITEM], seq=53)
    _msg(db, "m55", "principal", "liaison", "verdict", ["b_1"], "m53", seq=55)
    _ruling(db, "r_m54", "m53", "m55", {"b_1": "approve", ITEM: "approve"},
            "Line 6 is right.")
    db.commit()


def test_a_newer_approve_of_the_batch_line_ends_nothing(db):
    # Finding 1: only a row that carries the ruling, or a newer contest or
    # revise of his, ends an owed contest.
    _approve_batch(db)
    assert owed(db, ITEM)["ruling"] == "r_m27"


def _old_file(tmp_path):
    """A run file from before the column: s171's relay rewrite of b_1 under
    m42, and s150's tick copy, both with no stamp."""
    from rota.core.db import init_db as _init

    path = tmp_path / "old.db"
    conn = _init(path)
    conn.execute("INSERT INTO items (id, text, kind, approval) VALUES (?, ?, "
                 "'in_scope', 'approved')", (ITEM, TEXT))
    conn.execute("INSERT INTO batches (id, item_id) VALUES ('b_1', ?)", (ITEM,))
    _msg(conn, "m31", "liaison", "principal", "present", ["b_1"], seq=31)
    _msg(conn, "m42", "principal", "liaison", "verdict", ["b_1"], "m31", seq=42)
    _msg(conn, "m45", "liaison", "architect", "relay", ["b_1"], "m42", seq=45)
    _ruling(conn, "r_m39", "m31", "m42", {"b_1": "contest"}, M39)
    for sid, seq, trigger, grains in (("s150", 150, None, ["src/icalendar/parser/property.py"]),
                                      ("s171", 171, "m45", HIS)):
        conn.execute("INSERT INTO sessions (id, role, seq, trigger_msg) VALUES "
                     "(?, 'architect', ?, ?)", (sid, seq, trigger))
        for n, g in enumerate(grains):
            conn.execute("INSERT INTO receipts (session_id, table_name, row_id, "
                         "new_version) VALUES (?, 'batch_touch', ?, ?)",
                         (sid, f"b_1:{g}", seq + n))
    for g in HIS + ["src/icalendar/tests/other.py"]:
        conn.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) "
                     "VALUES ('b_1', ?, 'path')", (g,))
    conn.commit()
    conn.execute("ALTER TABLE batch_touch DROP COLUMN ruling_id")
    conn.commit()
    conn.close()
    return path


def _stamps(conn):
    return sorted(tuple(r) for r in conn.execute(
        "SELECT grain, ruling_id FROM batch_touch"))


def test_the_migration_stamps_a_relay_rewrite_from_the_receipts(tmp_path):
    # Finding 2: dry 6b at s173 owed r_m41 again after the migration.
    conn = init_db(_old_file(tmp_path))
    assert _stamps(conn) == [(HIS[0], "m42"), ("src/icalendar/tests/other.py", ""),
                             (HIS[1], "m42")]
    assert owed(conn, "b_1") is None


def test_connect_adds_the_column_and_its_stamps(tmp_path):
    # Finding 8: `connect` gives an older file the late columns.
    from rota.core.db import connect

    conn = connect(_old_file(tmp_path))
    assert _stamps(conn)[0] == (HIS[0], "m42")


def test_one_page_for_each_owed_key(db):
    # Finding 5: an item with two pending batches gets one page.
    from rota.core.predicates import park_ask

    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b_2', ?, 'pending')",
               (ITEM,))
    _spend(db, f"architect|tick:guess|{ITEM},m28")
    assert parked(db, "b_2")
    assert [w.refs for w in park_ask(db)] == [(ITEM, "b_1")]


def test_the_seed_keeps_the_guess_under_a_batch_line_contest(db):
    # Finding 6: he contested the batch's plan, not the guess.
    _second_contest(db)
    seed = _guess_seed(db, "b_1")
    assert seed["paths"] == [g for g, k, _ in GUESS if k == "path"]


def test_a_stamped_guess_rewrite_clears_the_old_batch_plan(db):
    # Finding 7: a batch annotated before his contest keeps no old plan.
    from rota.core.predicates import annotate

    _s150(db)
    wake = Wake("architect", "tick:guess", refs=(ITEM, "m28"))
    sb = _architect(db, "guess", wake)
    sb.call("batches.guess", item_id=ITEM, paths=HIS)
    _commit(db, sb, "tick:guess", wake.refs)
    assert _stamps(db) == []
    assert [w.refs for w in annotate(db)] == [("b_1",)]


# The six branches that the review's mutations left green (finding 4).

def test_an_owed_batch_line_wakes_annotate_with_the_verdict(db):
    from rota.core.predicates import annotate

    _s150(db)
    _second_contest(db)
    assert [(w.kind, w.refs) for w in annotate(db)] == [
        ("tick:annotate", ("b_1", "m40"))]


def test_the_batch_line_tick_waits_behind_an_open_relay(db):
    from rota.core.predicates import annotate

    _s150(db)
    _second_contest(db)
    _msg(db, "m45", "liaison", "architect", "relay", ["b_1"], "m40", status="open",
         seq=45)
    assert annotate(db) == []


def test_the_annotate_door_refuses_the_contested_plan(db):
    _s150(db)
    _second_contest(db)
    sb = _architect(db, "annotate", Wake("architect", "tick:annotate",
                                         refs=("b_1", "m40")))
    with pytest.raises(Exception, match="the same set"):
        sb.call("batches.annotate", batch_id="b_1",
                paths=[g for g, k, _ in GUESS if k == "path"],
                symbols=[g for g, k, _ in GUESS if k == "symbol"])


def test_a_contest_on_a_closed_batch_owes_nothing(db):
    # A set under m28 ends the guess contest first, so only the batch
    # contest is left to owe (pass 3, item 1).
    db.execute("INSERT INTO touch_guesses (item_id, item_ver, ruling_id, grain, "
               "grain_kind) VALUES (?, 1, 'm28', ?, 'path')", (ITEM, HIS[0]))
    _second_contest(db)
    assert owed(db, ITEM)["ref"] == "b_1"
    db.execute("UPDATE batches SET status = 'merged' WHERE id = 'b_1'")
    assert owed(db, ITEM) is None


def test_the_spent_owed_key_is_given_up_for_the_batch(db):
    from rota.core.scheduler import given_up

    assert given_up(db, "b_1") == []
    _spend(db, f"architect|tick:guess|{ITEM},m28")
    assert given_up(db, "b_1") == [f"architect|tick:guess|{ITEM},m28"]


def test_the_owed_park_ask_stays_open_until_the_park_ends(db):
    from rota.core.scheduler import close_stale_park_asks, park_ask_id

    _spend(db, f"architect|tick:guess|{ITEM},m28")
    mid = park_ask_id(db, "b_1")
    _msg(db, mid, "liaison", "principal", "present", [ITEM, KEY], status="open", seq=60)
    assert close_stale_park_asks(db) == 0
    db.execute("DELETE FROM tick_attempts")
    assert close_stale_park_asks(db) == 1


# ---------------------------------------------------------------------------
# Pass 3: the second look at 822311e0
# ---------------------------------------------------------------------------

def _run(db, wake, call, instructions):
    from rota.core.runner import run_session
    from rota.llm.llm import Pins, ScriptedBackend

    out = run_session(db, wake, backend=ScriptedBackend([call, "done"]),
                      pins=Pins(model="stub", temperature=0.0),
                      instructions=instructions)
    assert out.committed, out.errors
    return out


def _parked_page(db):
    """The owed park page, presented by a Liaison session and open to him."""
    from rota.core.predicates import park_ask
    from rota.roles.principal import pending_asks

    _spend(db, f"architect|tick:guess|{ITEM},m28")
    (wake,) = park_ask(db)
    db.commit()
    _run(db, wake, f'TOOL: msg.present_principal(refs=["{ITEM}", "b_1"])', "ask")
    (ask,) = [a for a in pending_asks(db) if a.message_id.startswith("m_park_")]
    return ask


def _his_reply(db, ask, text, ruling):
    """His reply lands through the Liaison's landing session (`rulings.rule`)."""
    from rota.core.scheduler import open_tips
    from rota.roles.principal import land, parse_reply

    answer = parse_reply(ask, text)
    reply = land(db, ask, answer)
    db.commit()
    (wake,) = [w for w in open_tips(db) if w.message_id == reply]
    _run(db, wake, f"TOOL: rulings.rule(rulings={json.dumps(ruling)})", "land")
    db.commit()
    (verdict,) = db.execute("SELECT id FROM messages WHERE cause_id = ? AND verb = "
                            "'verdict'", (ask.message_id,)).fetchall()
    return verdict["id"]


AGAIN = ("Line 2 is still wrong. Only string.py and test_icalendar.py change, "
         "nothing in property.py.")


def test_his_contest_of_line_2_lands_a_new_ruling_and_wakes_the_owner(db):
    # Item 3: the page says "Reply to line 2 ... and the team tries again".
    from rota.core.scheduler import open_tips

    ask = _parked_page(db)
    assert ask.refs[:2] == [ITEM, KEY]
    verdict = _his_reply(db, ask, AGAIN, {"1": "approve", "2": "rewrite", "c2": "none"})
    found = owed(db, ITEM)
    assert (found["verdict"], found["line"], found["ref"]) == (verdict, "guess", KEY)
    assert owed_key(found) != f"architect|tick:guess|{ITEM},m28"
    assert not parked(db, "b_1")
    # The Liaison relays the verdict, and the relay wakes the Architect.
    (wake,) = [w for w in open_tips(db) if w.message_id == verdict]
    _run(db, wake, f'TOOL: msg.relay_architect(refs=["{KEY}"])', "relay")
    db.commit()
    (relay,) = db.execute("SELECT id FROM messages WHERE cause_id = ? AND verb = "
                          "'relay' AND to_role = 'architect'", (verdict,)).fetchall()
    assert [w.role for w in open_tips(db) if w.message_id == relay["id"]] == ["architect"]
    # The tick waits behind the relay, then carries the new verdict.
    assert _guess_wakes(db) == []
    db.execute("UPDATE messages SET status = 'answered' WHERE id = ?", (relay["id"],))
    assert _guess_wakes(db) == [("architect", "tick:guess", (ITEM, verdict))]


GIVE_UP = "I give the request up."


@pytest.mark.parametrize("line_1", ["drop", f"other {GIVE_UP}"])
def test_he_gives_the_request_up_and_the_team_stops(db, line_1):
    # Item 4: the page says "Or say that you give the request up." A drop
    # ends the owed fact. A contest of line 1 keeps it, because the request
    # comes back, but the team stops all the same (pass 3b, finding 1).
    from rota.core.predicates import park_ask
    from rota.core.scheduler import frontier

    ask = _parked_page(db)
    _his_reply(db, ask, GIVE_UP, {"1": line_1, "2": "approve"})
    if line_1 == "drop":
        assert owed(db, ITEM) is None and owed(db, "b_1") is None
    else:
        assert owed(db, ITEM)["ruling"] == owed(db, "b_1")["ruling"] == "r_m27"
    assert ("do:cancel", ("b_1",)) in [(w.kind, w.refs) for w in frontier(db)]
    assert park_ask(db) == [] and _guess_wakes(db) == []
    assert db.execute("SELECT status FROM messages WHERE id = ?",
                      (ask.message_id,)).fetchone()["status"] == "answered"


@pytest.mark.parametrize("status", ["merged", "abandoned"])
def test_a_contest_on_a_closed_batch_leaves_the_guess_contest_owed(db, status):
    # Item 1: a ruling on a closed batch that no row carries replaces nothing.
    _second_contest(db)
    db.execute("UPDATE batches SET status = ? WHERE id = 'b_1'", (status,))
    assert owed(db, ITEM)["ruling"] == "r_m27"


def test_a_rewritten_contest_on_a_closed_batch_owes_nothing(db):
    # Dry 6b's order: s172 stamped b_1 under his batch contest. A merge of
    # b_1 then must not bring back the guess contest that it replaced.
    _second_contest(db)
    _s150(db, ruling="m40")
    db.execute("UPDATE batches SET status = 'merged' WHERE id = 'b_1'")
    assert owed(db, ITEM) is None


def _woke(db):
    """The Architect's sessions on m28: s145 on the relay m29 and three
    ticks. Two other sessions woke on other things."""
    for sid, seq, trigger, kind, refs in (
            ("s145", 145, "m29", "message", [KEY]),
            ("s150", 150, None, "tick:guess", [ITEM]),
            ("s152", 152, None, "tick:guess", [ITEM, "m28"]),
            ("s155", 155, None, "tick:guess", [ITEM, "m28"]),
            ("s156", 156, None, "tick:guess", [ITEM, "m28"]),
            ("s160", 160, "m26", "message", [ITEM])):
        db.execute("INSERT INTO sessions (id, role, seq, trigger_msg, wake_kind, "
                   "wake_refs) VALUES (?, 'architect', ?, ?, ?, ?)",
                   (sid, seq, trigger, kind, json.dumps(refs)))
    db.commit()


def test_the_page_counts_each_session_that_woke_on_the_ruling(db):
    # Item 2: the relay was a try too, so the count is 4, not the 3 ticks.
    from rota.roles.principal import _park_page

    _woke(db)
    _spend(db, f"architect|tick:guess|{ITEM},m28")
    text, _ = _park_page(db, "b_1", [ITEM, KEY])
    assert text.splitlines()[1] == PAGE[1]
    db.execute("DELETE FROM sessions")
    text, _ = _park_page(db, "b_1", [ITEM, KEY])
    assert text.splitlines()[1] == ("You corrected the team's guess at the code this "
                                    "request touches. The team tried, and it did not "
                                    "rewrite the guess.")


# ---------------------------------------------------------------------------
# Pass 3b: the third look at 3ebc5ac5
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("approval", ["contested", "pending"])
def test_the_door_refuses_the_contested_set_while_the_request_is_out(db, approval):
    # Finding 1: the request comes back, so his contest of the guess holds.
    db.execute("UPDATE items SET approval = ?", (approval,))
    assert owed(db, ITEM)["verdict"] == "m28"
    sb = _architect(db, "guess", Wake("architect", "message", message_id="m29"),
                    trigger="m29")
    with pytest.raises(Exception, match="the same set"):
        sb.call("batches.guess", item_id=ITEM,
                paths=[g for g, k, _ in GUESS if k == "path"],
                symbols=[g for g, k, _ in GUESS if k == "symbol"])


ITEM2 = "keeps_crlf_in_values"
KEY2 = f"guess:{ITEM2}"


def test_each_page_counts_the_tries_of_its_own_request(db):
    # Finding 2: one reply contests the guess of two requests, so one
    # verdict, and each page counts only its own sessions.
    from rota.roles.principal import _park_page

    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES (?, 'Keep CRLF in values.', 'in_scope', 'approved', 1, 1)",
               (ITEM2,))
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b_2', ?, 'pending')",
               (ITEM2,))
    db.execute("UPDATE rulings SET per_item = ? WHERE id = 'r_m27'",
               (json.dumps({KEY: "contest", ITEM: "approve", KEY2: "contest"}),))
    _woke(db)
    for n in (1, 2, 3):
        db.execute("INSERT INTO sessions (id, role, seq, wake_kind, wake_refs) VALUES "
                   "(?, 'architect', ?, 'tick:guess', ?)",
                   (f"s2{n}", 200 + n, json.dumps([ITEM2, "m28"])))
    _spend(db, f"architect|tick:guess|{ITEM},m28")
    _spend(db, f"architect|tick:guess|{ITEM2},m28")
    assert "tried 4 times" in _park_page(db, "b_1", [ITEM, KEY])[0]
    assert "tried 3 times" in _park_page(db, "b_2", [ITEM2, KEY2])[0]
