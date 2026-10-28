"""Fact F1: his verdict is one record, the rows of `ruled_refs`.

The root-cause audit of 2026-10-27 found a second store, the `config` key
`verdict:<message>`. Five readers read it before or beside `ruled_refs`, so
the two stores could disagree. Law 11: provenance derives from the refs.
`land` writes the verdict it computed as `landed` rows on every path, and
each landed row names the keypress or reading row it derives from.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from rota.core.db import init_db
from rota.core.scheduler import verdict_rows
from rota.roles.api import _principal_relay
from rota.roles.principal import (Answer, Ask, chain_verdict, granted, land,
                                  verdict_for)


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind) VALUES ('i1', 'a', 'in_scope')")
    conn.execute("INSERT INTO items (id, text, kind) VALUES ('i2', 'b', 'in_scope')")
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "body_refs, seq, status) VALUES ('m1', 'th', 'liaison', "
                 "'principal', 'present', ?, 1, 'open')", (json.dumps(["i1", "i2"]),))
    return conn


def _keypress(db, ref: str, verdict: str, rid: str = "r_m2") -> None:
    db.execute("INSERT INTO ruled_refs (id, ruling_id, ref, verdict, source) "
               "VALUES (?, ?, ?, ?, 'keypress')", (f"rr_{rid}_{ref}", rid, ref, verdict))


def _verdict_m2(db) -> None:
    """His verdict m2 on page m1, and the Liaison's relay m3 of it, with
    keypress rows and no `config` key."""
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_refs, seq, status) VALUES ('m2', 'm1', 'th', "
               "'principal', 'liaison', 'verdict', ?, 2, 'open')",
               (json.dumps(["i1", "i2"]),))
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_refs, seq, status) VALUES ('m3', 'm2', 'th', "
               "'liaison', 'architect', 'relay', ?, 3, 'open')",
               (json.dumps(["i2"]),))
    db.execute("INSERT INTO rulings (id, ask_id, status, verdict_id) "
               "VALUES ('r_m2', 'm1', 'landed', 'm2')")
    _keypress(db, "i1", "approve")
    _keypress(db, "i2", "contest")


def test_verdict_for_reads_the_keypress_rows(db):
    _verdict_m2(db)
    assert verdict_for(db, "m2") == {"i1": "approve", "i2": "contest"}


def test_chain_verdict_reads_the_keypress_rows(db):
    """A stale `verdict:` key of config disagrees with the rows. The rows
    win, so the parent, which read the key, goes red here."""
    _verdict_m2(db)
    db.execute("INSERT INTO config (key, value) VALUES ('verdict:' || 'm2', ?)",
               (json.dumps({"i1": "contest"}),))
    assert chain_verdict(db, "m3")[:2] == ("m2", {"i1": "approve", "i2": "contest"})


def test_verdict_rows_reads_the_keypress_rows(db):
    _verdict_m2(db)
    assert verdict_rows(db, "m2") == ["i2"]


def test_the_relay_reads_the_keypress_rows(db):
    _verdict_m2(db)
    ctx = SimpleNamespace(conn=db, trigger="m3")
    assert _principal_relay(ctx) == (["i2"], {"i1": "approve", "i2": "contest"})


def test_an_approve_that_closed_a_ledger_row_is_no_relay(db):
    """A taken default needs no relay, as the old map dropped it."""
    _verdict_m2(db)
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "status, author) VALUES ('L1', 'i1', 'items', 'x', 'resolved', "
               "'architect')")
    _keypress(db, "L1", "approve")
    assert verdict_for(db, "m2") == {"i1": "approve", "i2": "contest"}


def test_the_keypress_lands_beside_the_liaisons_reading(db):
    """The Liaison read his reply first and holds an open ruling. His
    keypress then lands that ruling, and the keypress is the verdict."""
    db.execute("INSERT INTO rulings (id, ask_id, per_item, status) VALUES "
               "('r_l', 'm1', ?, 'open')", (json.dumps({"i1": "approve", "i2": "approve"}),))
    db.execute("INSERT INTO ruled_refs (id, ruling_id, ref, verdict, source) "
               "VALUES ('rr_l1', 'r_l', 'i1', 'approve', 'reading'), "
               "('rr_l2', 'r_l', 'i2', 'approve', 'reading')")
    ask = Ask(message_id="m1", verb="present", refs=["i1", "i2"])
    mid = land(db, ask, Answer(verb="verdict",
                               per_item={"i1": "approve", "i2": "contest"}))
    assert mid
    assert verdict_for(db, mid) == {"i1": "approve", "i2": "contest"}
    assert {r["ref"]: r["verdict"] for r in db.execute(
        "SELECT ref, verdict FROM ruled_refs WHERE ruling_id = 'r_l' "
        "AND source = 'keypress'")} == {"i1": "approve", "i2": "contest"}


def _reading(db, rid: str, ref: str, verdict: str, act=None, kind=None):
    db.execute("INSERT INTO ruled_refs (id, ruling_id, ref, verdict, act, "
               "target_kind, source) VALUES (?, ?, ?, ?, ?, ?, 'reading')",
               (f"rr_{rid}_{ref}", rid, ref, verdict, act, kind))


def _landed(db, rid: str) -> dict:
    return {r["ref"]: r for r in db.execute(
        "SELECT * FROM ruled_refs_live WHERE ruling_id = ? AND source = "
        "'landed'", (rid,))}


def test_the_keypress_keeps_the_act_of_the_reading(db):
    """The open-row path: the Liaison read "drop line 2" before his
    keypress. The landed row carries the act, so `grant` takes back
    nothing, and it derives from the keypress row, so it is decided."""
    db.execute("INSERT INTO rulings (id, ask_id, per_item, status) VALUES "
               "('r_l', 'm1', ?, 'open')",
               (json.dumps({"i1": "approve", "i2": "contest"}),))
    _reading(db, "r_l", "i1", "approve")
    _reading(db, "r_l", "i2", "contest", act="drop", kind="row")
    assert granted(db, "i2", "drop") is False, "an open ruling grants nothing"
    ask = Ask(message_id="m1", verb="present", refs=["i1", "i2"])
    mid = land(db, ask, Answer(verb="verdict",
                               per_item={"i1": "approve", "i2": "contest"}))
    assert granted(db, "i2", "drop")
    rows = _landed(db, "r_l")
    assert rows["i2"]["act"] == "drop"
    assert rows["i2"]["provenance"] == "decided"
    assert db.execute("SELECT source FROM ruled_refs WHERE id = ?",
                      (rows["i2"]["derived_from"],)).fetchone()[0] == "keypress"
    assert verdict_for(db, mid) == {"i1": "approve", "i2": "contest"}


def test_a_ruling_from_his_words_lands_rows_with_no_keypress(db):
    """The `apply_rulings` path: no key was pressed. The landed rows derive
    from the reading's rows and stay reasoned (law 11)."""
    db.execute("INSERT INTO rulings (id, ask_id, per_item, status) VALUES "
               "('r_w', 'm1', ?, 'open')",
               (json.dumps({"i1": "approve", "i2": "contest"}),))
    _reading(db, "r_w", "i1", "approve")
    _reading(db, "r_w", "i2", "contest", act="drop", kind="row")
    ask = Ask(message_id="m1", verb="present", refs=["i1", "i2"])
    mid = land(db, ask, Answer(verb="verdict",
                               per_item={"i1": "approve", "i2": "contest"}),
               ruling_id="r_w")
    db.execute("UPDATE rulings SET status = 'landed', verdict_id = ? "
               "WHERE id = 'r_w'", (mid,))
    assert not db.execute("SELECT 1 FROM ruled_refs WHERE source = 'keypress'"
                          ).fetchone()
    rows = _landed(db, "r_w")
    assert {ref: r["derived_from"] for ref, r in rows.items()} == {
        "i1": "rr_r_w_i1", "i2": "rr_r_w_i2"}
    assert {r["provenance"] for r in rows.values()} == {"reasoned"}
    assert rows["i2"]["act"] == "drop" and granted(db, "i2", "drop")
    assert verdict_for(db, mid) == {"i1": "approve", "i2": "contest"}


# --- review 1 of fact F1, findings 1 to 6 -----------------------------------

def _night171(tmp_path, key: str):
    """Night 171's shape: page m65, his words m80, the Liaison's open
    reading r_m80 "contest, rewrite format_filename:42", then his key."""
    c = init_db(tmp_path / "n171.db")
    c.execute("INSERT INTO items (id, text, kind) VALUES ('how_it_works', "
              "'Click is a CLI kit', 'in_scope')")
    c.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
              "body_refs, seq, status) VALUES ('m65', 't', 'liaison', "
              "'principal', 'present', '[\"how_it_works\"]', 68, 'open')")
    c.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
              "to_role, verb, body_refs, body_text, seq, status) VALUES "
              "('m80', 'm65', 't', 'principal', 'liaison', 'converse', "
              "'[\"how_it_works\"]', 'Line 1 describes Click, so replace it', "
              "84, 'answered')")
    c.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, "
              "status) VALUES ('r_m80', 'm65', 'm80', ?, 'replace it', 'open')",
              (json.dumps({"how_it_works": "contest"}),))
    c.execute("INSERT INTO ruled_refs (id, ruling_id, ref, verdict, act, "
              "target_kind, target, words, source) VALUES ('rr_how', 'r_m80', "
              "'how_it_works', 'contest', 'rewrite', 'source_line', "
              "'format_filename:42', 'replace it', 'reading')")
    ask = Ask(message_id="m65", verb="present", refs=["how_it_works"],
              order=["how_it_works"])
    mid = land(c, ask, Answer(verb="verdict", per_item={"how_it_works": key}))
    return c, mid


def test_his_key_after_a_landed_ruling_on_the_ask_is_the_verdict(db):
    """Finding 1: his words landed r2 with a contest, then his key approved.
    The key lands a ruling of its own, so the relay carries the approve."""
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
               "to_role, verb, body_refs, body_text, seq, status) VALUES "
               "('m6', 'm1', 'th', 'principal', 'liaison', 'converse', '[]', "
               "'two changes', 2, 'answered')")
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, "
               "status) VALUES ('r2', 'm1', 'm6', ?, 'two changes', 'landed')",
               (json.dumps({"i1": "contest"}),))
    _reading(db, "r2", "i1", "contest")
    ask = Ask(message_id="m1", verb="present", refs=["i1"], order=["i1"])
    mid = land(db, ask, Answer(verb="verdict", per_item={"i1": "approve"}))
    assert verdict_for(db, mid) == {"i1": "approve"}
    assert chain_verdict(db, mid)[1] == {"i1": "approve"}


@pytest.mark.parametrize("key", ["contest", "approve"])
def test_the_read_back_line_reads_the_reading_and_not_his_key(tmp_path, key):
    """Finding 2: the line says how the team read his words, so his key and
    the landed row are no row of it, whether the key agrees or not."""
    from rota.roles.principal import read_back_rows, reading_line

    c, _ = _night171(tmp_path, key)
    rows = read_back_rows(c, "m80")
    assert [(r["source"], r["verdict"], r["act"]) for r in rows] == [
        ("reading", "contest", "rewrite")]
    assert "rewrite format_filename:42" in reading_line(c, "reading:m80")


def test_the_last_ruling_reads_his_key_over_the_reading(tmp_path):
    """Finding 3: his key approves over the reading's contest. The respecify
    door and the ratify door read the approve."""
    from rota.roles.principal import contested_statement, last_ruling_on

    c, _ = _night171(tmp_path, "approve")
    assert last_ruling_on(c, "how_it_works")["verdict"] == "approve"
    assert contested_statement(c, "how_it_works") is None
    agree = tmp_path / "agree"
    agree.mkdir()
    c, _ = _night171(agree, "contest")
    assert last_ruling_on(c, "how_it_works")["verdict"] == "contest"
    assert contested_statement(c, "how_it_works") == "r_m80"


def test_the_seed_of_a_verdict_on_a_ruling_from_his_words_keeps_that_ruling():
    """Finding 4: the case's verdict lands its rows under the ruling r2 that
    his words landed, as `land` does on the `apply_rulings` path, and writes
    no keypress row and no ruling `r_<verdict>`."""
    from rota.testkit import fixtures

    path = Path(__file__).parent / "cases" / "l1_liaison2.yaml"
    (case,) = [c for c in fixtures.load_case(path)
               if c["id"] == "L1-LI-a-contested-statement-is-not-delivered"]
    conn = init_db(":memory:")
    fixtures.seed(conn, case["fixture"])
    mid = fixtures.seed_inbound(conn, case)
    (ruling,) = conn.execute("SELECT id, verdict_id FROM rulings").fetchall()
    assert ruling["verdict_id"] == mid
    assert {r["source"] for r in conn.execute(
        "SELECT source FROM ruled_refs")} == {"backfill", "landed"}


def test_the_owner_view_and_the_rows_agree_on_his_key(tmp_path):
    """Finding 5: on the open-row path his key decides the ruling, in the
    owner `provenance` view as in `ruled_refs_live` (law 11)."""
    c, _ = _night171(tmp_path, "contest")
    c.execute("INSERT INTO items (id, text, kind) VALUES ('i9', 'x', 'in_scope')")
    c.execute("INSERT INTO refs (src_table, src_id, kind, target) VALUES "
              "('items', 'i9', 'ruling', 'r_m80')")
    assert c.execute("SELECT provenance FROM item_provenance WHERE id = 'i9'"
                     ).fetchone()[0] == "decided"
    assert {r[0] for r in c.execute("SELECT provenance FROM ruled_refs_live "
                                    "WHERE source = 'landed'")} == {"decided"}


def test_the_night_report_reads_a_ruling_as_verdict_for_does(db):
    """Finding 6: an old night with no landed row. A `reading:` ref and an
    approve of a resolved ledger row are no verdict, as in `verdict_for`."""
    from rota.tools.nightreport import Night, _ruled_rows

    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "status, author) VALUES ('L1', 'i1', 'items', 'x', 'resolved', "
               "'architect')")
    db.execute("INSERT INTO rulings (id, ask_id, status) VALUES "
               "('r_old', 'm1', 'landed')")
    for ref, verdict in (("i2", "contest"), ("L1", "approve"),
                         ("reading:m9", "approve")):
        _reading(db, "r_old", ref, verdict)
    assert _ruled_rows(Night(db), "r_old") == {"i2": "contest"}


def test_no_function_reads_a_verdict_key_of_config():
    """The one-reader pin of fact F1. A string that starts a `config` key
    `verdict:`, or names it in SQL, turns this red (rule C76)."""
    pkg = Path(__file__).resolve().parents[2] / "rota"
    found = []
    for path in sorted(pkg.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                    and (node.value.startswith("verdict:")
                         or "'verdict:" in node.value)):
                found.append(f"{path.relative_to(pkg.parent).as_posix()}:"
                             f"{node.lineno}")
    assert found == []
