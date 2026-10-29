"""
One record per ruling and ref (the seam design of 2026-10-26, pass 1).

A ruling named its rows inside the JSON map `rulings.per_item`, so no row
could be walked to the rulings on it (frame 300). The table `ruled_refs`
holds one row per ruling and ref, and `principal.ruling_rows` is its one
builder. The Liaison's `rulings.rule` stages the rows, and `land` and
`_land_shift` insert the rows of a verdict from the seat. The view
`ruled_refs_live` derives the status, the confirmation and the provenance.
"""
from __future__ import annotations

import json
import sqlite3

import pytest

from rota.core.db import _apply_write, backfill_ruled_refs, init_db
from rota.core.runner import _as_write
from rota.roles.principal import (Answer, apply_rulings, land, last_ruling_on,
                                  parse_reply, pending_asks, ruling_rows)

WORDS = ("3 is wrong: a fixed 15 percent, nobody types it. Remove the typed "
         "percentage.")
SPAN = "Remove the typed percentage."


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _page(db, refs=("calculate_tip", "s1", "l_1")):
    """A present of three lines: the request's words, its item, and the
    team's note. The page orders them s1, calculate_tip, l_1."""
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e1','principal','tip calculator pls',1)")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES ('s1','e1',0,18,'tip calculator pls',"
               "'ratified')")
    for iid, text in (("how_it_works", "The user types the bill and a percentage."),
                      ("calculate_tip", "The software calculates the tip.")):
        db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                   "version) VALUES (?, ?, 'in_scope', 'draft', 0, 1)",
                   (iid, text))
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "status, author) VALUES ('l_1', 'how_it_works', 'items', "
               "'the percentage is typed each time', 'open', 'vision_keeper')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m8', 'th', 'vision_keeper', "
               "'liaison', 'submit', '[]', 0, 'answered')")
    db.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, "
               "to_role, verb, body_refs, seq, status) VALUES ('m9', 'th', "
               "'m8', 'liaison', 'principal', 'present', ?, 1, 'open')",
               (json.dumps(list(refs)),))
    db.commit()
    return pending_asks(db)[0]


def _seat(db, ask, words=WORDS):
    from rota.core.sandbox import build
    from rota.roles import prompts

    reply = land(db, ask, parse_reply(ask, words))
    db.commit()
    sb = build("liaison", db, mode="normal", session_id="s_seam",
               allow=prompts.mode_tools("liaison", "landing"))
    sb.ctx.trigger = reply
    return sb, reply


def _commit(db, sb):
    for w in sb.ctx.writes:
        _apply_write(db, _as_write(w), sb.ctx.role)
    db.commit()


def _rows(db, ruling_id, source="landed"):
    """The rows of one ruling, less the `landed` rows of the verdict that
    `land` computed (fact F1). `source=None` keeps every row."""
    return [dict(r) for r in db.execute(
        "SELECT * FROM ruled_refs_live WHERE ruling_id = ? "
        "AND source IS NOT ? ORDER BY row_seq", (ruling_id, source))]


OBJECT = {"1": "approve", "2": "approve",
          "3": {"verdict": "contest", "act": "remove", "target": "how_it_works",
                "words": SPAN}}
FLAT = {"1": "approve", "2": "approve", "3": "contest"}
ACTS = {"3": {"act": "remove", "target": "how_it_works", "words": SPAN}}


def test_the_table_holds_one_row_per_ruling_and_ref_and_the_view_derives(db):
    cols = [r[1] for r in db.execute("PRAGMA table_info(ruled_refs)")]
    assert cols == ["id", "ruling_id", "ref", "line", "verdict", "act",
                    "target_kind", "target", "words", "words_from", "old_text",
                    "ref_version", "source", "derived_from"], cols
    view = [r[1] for r in db.execute("PRAGMA table_info(ruled_refs_live)")]
    for derived in ("status", "confirmed_by", "provenance", "ruling_status",
                    "ruling_seq", "reply_words"):
        assert derived in view, view
    index = db.execute("SELECT sql FROM sqlite_master WHERE type = 'index' "
                       "AND name = 'ruled_refs_by_ref'").fetchone()
    assert index and "(ref, ruling_id)" in index[0]


def test_the_writer_holds_the_stored_verdicts_and_a_row_never_changes(db):
    _page(db)
    db.execute("INSERT INTO rulings (id, ask_id) VALUES ('r1', 'm9')")
    for word in ("approve", "contest", "revise", "resume", "park", "now", "drop"):
        row = ruling_rows(db, "r1", [], {"s1": word})[0]
        assert row["verdict"] == word
    with pytest.raises(ValueError, match="not a stored verdict"):
        ruling_rows(db, "r1", [], {"s1": "later"})
    with pytest.raises(ValueError, match="not an act"):
        ruling_rows(db, "r1", [], {"s1": {"verdict": "contest", "act": "delete"}})
    db.execute("INSERT INTO ruled_refs (id, ruling_id, ref, verdict) "
               "VALUES ('rr_approve', 'r1', 's1', 'approve')")
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO ruled_refs (id, ruling_id, ref, verdict, act) "
                   "VALUES ('rr_y', 'r1', 'y', 'contest', 'delete')")
    with pytest.raises(sqlite3.IntegrityError, match="never changes"):
        db.execute("UPDATE ruled_refs SET verdict = 'contest' "
                   "WHERE id = 'rr_approve'")


@pytest.mark.skip(reason="re-pin to the menu form, frame 345: R2 word form")
def test_a_reply_that_rules_three_refs_stages_three_rows_after_its_ruling(db):
    ask = _page(db)
    sb, reply = _seat(db, ask)
    out = sb.call("rulings.rule", rulings=OBJECT, words=WORDS)
    # The result and `per_item` keep their shape, so the cases keep theirs.
    assert out["per_item"] == {"s1": "approve", "calculate_tip": "approve",
                               "l_1": "contest"}, out
    tables = [w[0] for w in sb.ctx.writes]
    assert tables == ["rulings", "ruled_refs", "ruled_refs", "ruled_refs"], tables
    _commit(db, sb)
    rows = _rows(db, out["id"])
    assert [(r["ref"], r["line"], r["verdict"]) for r in rows] == [
        ("s1", 1, "approve"), ("calculate_tip", 2, "approve"),
        ("l_1", 3, "contest")], rows
    contest = rows[2]
    assert (contest["act"], contest["target"], contest["words"],
            contest["words_from"]) == ("remove", "how_it_works", SPAN, reply)
    # A row with no words of its own carries the whole reply. No act is
    # granted on it, and null never reads as a permission.
    assert rows[0]["words"] == WORDS and rows[0]["act"] is None
    assert {r["source"] for r in rows} == {"reading"}
    assert {r["status"] for r in rows} == {"open"}
    assert {r["provenance"] for r in rows} == {"reasoned"}
    assert {r["confirmed_by"] for r in rows} == {None}
    apply_rulings(db)
    db.commit()
    assert {r["status"] for r in _rows(db, out["id"])} == {"landed"}
    # The reader keeps its answer: the verdict and the whole reply.
    assert last_ruling_on(db, "l_1") == {"id": out["id"], "verdict": "contest",
                                         "words": WORDS, "text": None}


@pytest.mark.skip(reason="re-pin to the menu form, frame 345: R2 word form")
def test_the_object_form_writes_the_rows_and_the_flat_form_is_refused(tmp_path):
    """Frame 345, pass 2: the one-word form replaced the flat `acts` map,
    and the object form stays."""
    conn = init_db(tmp_path / "object.db")
    ask = _page(conn)
    sb, _ = _seat(conn, ask)
    sb.call("rulings.rule", words=WORDS, rulings=OBJECT)
    written = [w[2] for w in sb.ctx.writes if w[0] == "ruled_refs"]
    conn.close()
    assert len(written) == 3 and written[2]["act"] == "remove"
    conn = init_db(tmp_path / "flat.db")
    ask = _page(conn)
    sb, _ = _seat(conn, ask)
    with pytest.raises(ValueError, match="takes no acts"):
        sb.call("rulings.rule", words=WORDS, rulings=FLAT, acts=ACTS)
    assert not sb.ctx.writes
    conn.close()


def test_frame300_a_ruling_on_a_ref_no_table_holds_is_refused(db):
    """Frame 300's red test: a ruling on a ref no table holds is refused at
    write time. `_table_of_ref` holds none of it, and nor does any other
    home of a page line."""
    from rota.roles.api import _table_of_ref

    _page(db)
    assert _table_of_ref(db, "c_gone") is None
    with pytest.raises(ValueError, match="no table holds"):
        ruling_rows(db, "r_x", ["s1", "c_gone"],
                    {"s1": "approve", "c_gone": "contest"}, words="no")
    rows = ruling_rows(db, "r_x", ["s1"], {"s1": "approve"}, words="ok")
    assert [(r["ref"], r["line"], r["ref_version"]) for r in rows] == [
        ("s1", 1, 1)]


def test_a_keypress_verdict_lands_its_rows_and_reads_decided(db):
    ask = _page(db)
    mid = land(db, ask, Answer(verb="verdict", text="", per_item={
        "s1": "approve", "calculate_tip": "approve", "l_1": "approve"}))
    db.commit()
    rows = _rows(db, f"r_{mid}")
    assert [r["ref"] for r in rows] == ["s1", "calculate_tip", "l_1"], rows
    assert {(r["source"], r["status"], r["provenance"]) for r in rows} == {
        ("keypress", "landed", "decided")}


def test_the_shift_answer_lands_its_rows_through_the_same_builder(db):
    """The review's finding 6: `_land_shift` writes a `rulings` row, so it
    writes its rows too. The stored word is `park`, and a key that no table
    holds gets no row while the answer lands."""
    from rota.roles.principal import SHIFT_ASK, Ask

    _page(db)
    sid = f"{SHIFT_ASK}calculate_tip_m_p2"
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES (?, ?, 'liaison', 'principal', "
               "'present', '[\"calculate_tip\"]', 30, 'open')", (sid, sid))
    db.commit()
    mid = land(db, Ask(message_id=sid, verb="present", refs=["calculate_tip"]),
               Answer("verdict", text="later",
                      per_item={"calculate_tip": "park", "gone_item": "park"}))
    db.commit()
    rows = _rows(db, f"r_{mid}")
    assert [(r["ref"], r["verdict"], r["source"], r["words"]) for r in rows] == [
        ("calculate_tip", "park", "keypress", "later")], rows


@pytest.mark.skip(reason="re-pin to the menu form, frame 345: R2 word form")
def test_the_view_supersedes_outdates_and_confirms(db):
    ask = _page(db)
    sb, reply = _seat(db, ask)
    first = sb.call("rulings.rule", rulings=OBJECT, words=WORDS)["id"]
    _commit(db, sb)
    apply_rulings(db)
    # A newer landed ruling on calculate_tip supersedes the first one there.
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('m20', 'm20', 'liaison', 'principal', "
               "'present', '[\"calculate_tip\"]', 20)")
    db.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, "
               "to_role, verb, body_refs, body_text, seq) VALUES ('m21', "
               "'m20', 'm20', 'principal', 'liaison', 'converse', '[]', 'ok', "
               "21)")
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, status) "
               "VALUES ('r_new', 'm20', 'm21', 'landed')")
    for row in ruling_rows(db, "r_new", ["calculate_tip"],
                           {"calculate_tip": "approve",
                            f"reading:{reply}": "approve"}, words="ok"):
        _apply_write(db, _as_write(("ruled_refs", row["id"], row)),
                     "liaison")
    # An amended item moves its version past the version he ruled on.
    db.execute("UPDATE items SET version = 2 WHERE id = 'calculate_tip'")
    db.commit()
    status = {r["ref"]: r for r in _rows(db, first)}
    assert status["calculate_tip"]["status"] == "superseded"
    assert status["s1"]["status"] == "landed"
    # His approve of the read-back line confirms every row of the reply.
    assert {r["confirmed_by"] for r in status.values()} == {"m21"}
    assert {r["provenance"] for r in status.values()} == {"decided"}
    newest = {r["ref"]: r for r in _rows(db, "r_new")}
    assert newest["calculate_tip"]["status"] == "outdated"


def test_the_backfill_gives_an_old_ruling_its_rows(tmp_path):
    path = tmp_path / "old.db"
    conn = init_db(path)
    # A database from before the table: no table, no view, and rulings with
    # a map only.
    conn.execute("DROP VIEW ruled_refs_live")
    conn.execute("DROP TABLE ruled_refs")
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                 "verb, body_refs, seq) VALUES ('m1', 'm1', 'liaison', "
                 "'principal', 'present', '[]', 1)")
    conn.execute(
        "INSERT INTO rulings (id, ask_id, per_item, words, status, texts) "
        "VALUES ('r_old', 'm1', ?, 'line 2 is wrong', 'landed', ?)",
        (json.dumps({"s_1": "approve", "c_1": "contest", "x": "later"}),
         json.dumps({"c_1": "The tip is rounded."})))
    conn.execute("INSERT INTO rulings (id, ask_id, status) "
                 "VALUES ('r_empty', 'm1', 'landed')")
    conn.commit()
    conn.close()
    conn = init_db(path)
    rows = [dict(r) for r in conn.execute(
        "SELECT ref, verdict, act, target, words, words_from, old_text, line, "
        "source FROM ruled_refs ORDER BY rowid")]
    assert rows == [
        {"ref": "s_1", "verdict": "approve", "act": None, "target": None,
         "words": "line 2 is wrong", "words_from": None, "old_text": None,
         "line": None, "source": "backfill"},
        {"ref": "c_1", "verdict": "contest", "act": None, "target": None,
         "words": "line 2 is wrong", "words_from": None,
         "old_text": "The tip is rounded.", "line": None, "source": "backfill"}]
    assert last_ruling_on(conn, "c_1") == {
        "id": "r_old", "verdict": "contest", "words": "line 2 is wrong",
        "text": "The tip is rounded."}
    # The back-fill runs at each open and writes a row once.
    assert backfill_ruled_refs(conn) == 0
    conn.close()


def test_an_acknowledge_with_a_gone_ref_lands_and_leaves_a_fault(db):
    """The review of pass 1, finding 1. The page numbers no line, and its
    one ref is gone. Red on 624621eb: rulings.rule refused `rulings={}` and
    told the Liaison to rule rows the page does not have."""
    ask = _page(db, refs=("x_gone",))
    assert not ask.order
    sb, _ = _seat(db, ask, words="ok")
    out = sb.call("rulings.rule", rulings={}, words="ok")
    assert out["per_item"] == {"x_gone": "approve"}
    faults = [w[2] for w in sb.ctx.writes if w[0] == "faults"]
    assert [f["call"] for f in faults] == ["rulings.rule"]
    assert faults[0]["text"].startswith("x_gone: no table holds this row")
    assert not [w for w in sb.ctx.writes if w[0] == "ruled_refs"]


def test_a_keypress_on_a_gone_ref_keeps_his_verdict_and_leaves_a_fault(db):
    """The review of pass 1, finding 2. Red on 624621eb: the verdict on
    r_gone left no row, no fault, and no key in the per_item of
    rulings_load."""
    from types import SimpleNamespace

    from rota.roles.api import rulings_load

    ask = _page(db)
    mid = land(db, ask, Answer(verb="verdict", text="", per_item={
        "s1": "approve", "calculate_tip": "approve", "l_1": "approve",
        "r_gone": "approve"}))
    db.commit()
    assert [r["ref"] for r in _rows(db, f"r_{mid}")] == ["s1", "calculate_tip", "l_1"]
    # The verdict that `land` computed keeps the gone ref, as the config map
    # kept it before fact F1.
    assert "r_gone" in {r["ref"] for r in _rows(db, f"r_{mid}", None)
                        if r["source"] == "landed"}
    (fault,) = db.execute("SELECT call, text FROM faults").fetchall()
    assert fault["call"] == "principal.land"
    assert fault["text"].startswith(f"r_gone: no table holds this row, so ruling r_{mid}")
    (reading,) = [r for r in rulings_load(SimpleNamespace(conn=db), ask.message_id)
                  if r["id"] == f"r_{mid}"]
    assert json.loads(reading["per_item"])["r_gone"] == "approve"
