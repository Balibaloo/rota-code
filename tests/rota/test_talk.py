"""
The talking seam.

`ConsolePrincipal` has existed since the principal seam was written and was
wired to nothing, called by nothing, and covered by nothing. A capability
nobody can reach is indistinguishable from one that does not work, so these
cover the join rather than the parts: intake lands where the system looks for
it, and a principal backend reaches the loop.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.tools import talk


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "talk.db")


def test_the_first_sentence_lands_as_an_entry_and_a_message(db):
    """
    Both, and for different reasons: the entry is the record Liaison segments
    statements out of, and every statement keeps a span back into it. The
    message is the only thing that wakes anybody.
    """
    msg_id = talk.open_with(db, "let people export their invoices")

    entry = db.execute("SELECT id, author, text FROM entries").fetchone()
    assert entry["author"] == "principal"
    assert entry["text"] == "let people export their invoices"

    msg = db.execute("SELECT * FROM messages WHERE id = ?", (msg_id,)).fetchone()
    assert (msg["from_role"], msg["to_role"], msg["verb"]) == \
        ("principal", "liaison", "converse")
    assert msg["status"] == "open", "intake that wakes nobody is a transcript"
    assert json.loads(msg["body_refs"]) == [entry["id"]], \
        "the words and the record of them must point at each other"


def test_intake_puts_liaison_on_the_frontier_in_converse(db):
    """
    The join that matters. A `converse` message is what makes Liaison's intake
    mode the next thing the system does, and if it did not, talking to rota
    would be typing into a table.
    """
    from rota.core.scheduler import frontier

    talk.open_with(db, "invoices should be exportable as CSV")

    wakes = [w for w in frontier(db) if w.role == "liaison"]
    assert wakes, "the principal spoke and nobody was woken"
    assert any(w.detail == "converse" for w in wakes), \
        f"woken in the wrong mode: {[w.detail for w in wakes]}"


def test_a_second_sentence_is_a_second_entry_in_order(db):
    """Intake is append-only and ordered; a conversation is a transcript."""
    talk.open_with(db, "first thing")
    talk.open_with(db, "second thing")

    rows = db.execute("SELECT text FROM entries ORDER BY ts_order").fetchall()
    assert [r["text"] for r in rows] == ["first thing", "second thing"]


def test_the_console_principal_answers_the_verbs_it_is_offered(monkeypatch):
    """
    The human end of the seam, driven without a human.

    `confirm` and `present` take a per-item ruling; anything else is answered in
    words. That split is the whole protocol, and it was never exercised.
    """
    from rota.roles.principal import Ask, ConsolePrincipal

    monkeypatch.setattr("builtins.input", lambda *a: "lgtm")
    answer = ConsolePrincipal().respond(
        Ask(message_id="m1", verb="confirm", refs=["s1", "s2"]))
    assert answer.verb == "verdict"
    assert answer.per_item == {"s1": "approve", "s2": "approve"}

    monkeypatch.setattr("builtins.input", lambda *a: "s1=approve s2=contest")
    answer = ConsolePrincipal().respond(
        Ask(message_id="m2", verb="confirm", refs=["s1", "s2"]))
    assert answer.per_item == {"s1": "approve", "s2": "contest"}

    monkeypatch.setattr("builtins.input", lambda *a: "a purchase, not a sequence")
    answer = ConsolePrincipal().respond(
        Ask(message_id="m3", verb="clarify", refs=["g1"]))
    assert answer.verb == "converse"
    assert answer.text == "a purchase, not a sequence"


def test_deferral_is_always_allowed(monkeypatch):
    """
    Blank is not a non-answer. A deferred ask stays open and comes back on the
    agenda, which is why deferring costs nothing now and reappears later.
    """
    from rota.roles.principal import Ask, ConsolePrincipal

    monkeypatch.setattr("builtins.input", lambda *a: "")
    assert ConsolePrincipal().respond(
        Ask(message_id="m1", verb="confirm", refs=["s1"])) is None
