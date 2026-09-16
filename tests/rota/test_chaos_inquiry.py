"""
Chaos, loop 2: inquiry, hurt the ways operations would hurt it.

`LOOPS.md` names two injuries for this loop. An owner killed mid-round: the
principal asked, Liaison fanned out, one owner's answer session dies after
staging its answer -- and the round must still end in one composed reply,
not a reply written by whichever owner survived. And a corrupted answer must
not reach the principal: a message whose refs do not parse used to raise
where it was read -- inside the compose session as "session failed", retried
to quarantine with the round never composed; inside `open_reports` as the
frontier itself, the scheduler dead on one bad row, every tick. A corrupted
message says nothing now (`db.refs_of`), the compose proceeds on the sound
material, and the audit names the row.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.predicates import Wake
from rota.core.runner import resolve_inbound, run_session
from rota.core.scheduler import frontier_readonly
from rota.llm.llm import Pins, ScriptedBackend
from rota.testkit.fixtures import seed_provenance

PINS = Pins(model="stub", temperature=0.0)


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


class DiesMidSession:
    """Answers once, then dies the way a network does."""

    name = "chaos"

    def __init__(self, first: str):
        self.first = first
        self.calls = 0

    def complete(self, system, user, pins):
        self.calls += 1
        if self.calls == 1:
            from rota.llm.llm import Completion

            return Completion(text=self.first)
        raise ConnectionError("the model went away mid-session")


def _a_fan_out(db):
    """One question, asked of two owners, each holding a row to answer with."""
    db.execute("INSERT INTO glossary_terms (id, term, sense_short) "
               "VALUES ('g1','recipe','a seed note')")
    seed_provenance(db, "glossary_terms", "g1", "observed")
    db.execute("INSERT INTO items (id, text, kind, approval, "
               "approval_ver, version) VALUES ('t1',"
               "'users can write a recipe','in_scope','draft',0,1)")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m2','th','liaison',"
               "'terminologist','ask',?,1,'open')", (json.dumps(["g1"]),))
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m3','th','liaison',"
               "'vision_keeper','ask',?,2,'open')", (json.dumps(["t1"]),))
    db.commit()


def _answer_wakes(db):
    return [w for w in frontier_readonly(db)
            if w.role == "liaison" and w.kind == "message" and w.detail == "answer"]


def test_an_owner_killed_mid_round_and_the_harvest_still_composes(db):
    """
    The first owner answers. The second stages its answer and dies. Nothing
    may tip to Liaison on a half round: the dead owner's ask is still open,
    and an answer to an ask is addressed to a harvest, not a session. The
    retry lands the second answer, exactly one answer tips carrying the
    round, and Liaison composes from both.
    """
    _a_fan_out(db)

    first = run_session(
        db, Wake("terminologist", "message", message_id="m2", detail="ask"),
        backend=ScriptedBackend(["TOOL: msg.answer_liaison(refs=['g1'])", "done"]),
        pins=PINS, instructions="answer it")
    assert first.committed

    dead = run_session(
        db, Wake("vision_keeper", "message", message_id="m3", detail="ask"),
        backend=DiesMidSession("TOOL: msg.answer_liaison(refs=['t1'])"),
        pins=PINS, instructions="answer it")
    assert not dead.committed
    row = db.execute("SELECT status, attempts FROM messages WHERE id='m3'").fetchone()
    assert row["status"] == "open" and row["attempts"] == 1, (
        "the dead owner's ask survives, and the death was counted")
    assert _answer_wakes(db) == [], (
        "nothing tips to Liaison while a sibling ask is still open")
    assert any(w.message_id == "m3" for w in frontier_readonly(db)), (
        "the dead owner is offered its ask again")

    retry = run_session(
        db, Wake("vision_keeper", "message", message_id="m3", detail="ask"),
        backend=ScriptedBackend(["TOOL: msg.answer_liaison(refs=['t1'])", "done"]),
        pins=PINS, instructions="answer it")
    assert retry.committed

    tips = _answer_wakes(db)
    assert len(tips) == 1, "exactly one answer tips, carrying the round"
    inbound = resolve_inbound(db, tips[0])
    heard = set(inbound["refs"]) | {
        r for sib in inbound.get("other_answers", [])
        for r in json.loads(sib["body_refs"] or "[]")}
    assert heard == {"g1", "t1"}, "the whole round is in front of the composer"

    composed = run_session(
        db, tips[0],
        backend=ScriptedBackend([
            "TOOL: msg.converse_principal(refs=['g1', 't1'], reply='both owners')",
            "done"]),
        pins=PINS, instructions="compose it")
    assert composed.committed
    replies = db.execute("SELECT body_refs FROM messages WHERE verb='converse' "
                         "AND to_role='principal'").fetchall()
    assert len(replies) == 1, "one reply, not one per owner"
    assert set(json.loads(replies[0]["body_refs"])) >= {"g1", "t1"}


def test_a_corrupted_answer_is_set_aside_and_never_reaches_the_principal(db):
    """
    Both owners answered; the second answer's refs do not parse. The compose
    session must not die on it -- that was the old shape, "session failed"
    to quarantine and the round never composed -- and nothing of it may be
    what the principal reads. The sound answer composes; the audit names the
    row.
    """
    from rota.tools.audit import audit

    _a_fan_out(db)
    db.execute("UPDATE messages SET status='answered' WHERE id IN ('m2','m3')")
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_refs, seq, status) VALUES ('m4','m2','th',"
               "'terminologist','liaison','answer',?,3,'open')",
               (json.dumps(["g1"]),))
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_refs, seq, status) VALUES ('m5','m3','th',"
               "'vision_keeper','liaison','answer',?,4,'open')",
               ("%% not json at all %%",))
    db.commit()

    tips = _answer_wakes(db)
    assert [w.message_id for w in tips] == ["m5"], "the latest answer tips"
    inbound = resolve_inbound(db, tips[0])
    assert inbound["refs"] == [], "the corrupted answer says nothing"
    assert [s["id"] for s in inbound["other_answers"]] == ["m4"]
    assert "g1" in inbound["resolved_refs"], "the sound answer is in view"

    composed = run_session(
        db, tips[0],
        backend=ScriptedBackend([
            "TOOL: msg.converse_principal(refs=['g1'], reply='from the sound one')",
            "done"]),
        pins=PINS, instructions="compose it")
    assert composed.committed, composed.errors
    assert not any("session failed" in e for e in composed.errors)
    reply = db.execute("SELECT body_refs, body_text FROM messages "
                       "WHERE verb='converse' AND to_role='principal'").fetchone()
    assert json.loads(reply["body_refs"]) == ["g1"]
    assert "not json" not in (reply["body_text"] or "")

    assert any("m5" in f and "do not parse" in f for f in audit(db)), audit(db)


def test_a_corrupted_report_does_not_kill_the_frontier(db):
    """
    The same corruption on a report, where the reader is the frontier itself:
    `tick_round_close` loads every report's refs to ask whether the round is
    settled, and one bad row used to raise out of `predicate_wakes` on every
    tick. The frontier derives; the report is open with nothing in it -- the
    one that most needs a person -- so the round closes to Liaison.
    """
    from rota.tools.audit import audit

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m1','th','liaison',"
               "'terminologist','deliver',?,1,'answered')", (json.dumps(["s1"]),))
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_refs, seq, status) VALUES ('m2','m1','th',"
               "'terminologist','liaison','report',?,2,'open')",
               ("{broken",))
    db.commit()

    wakes = frontier_readonly(db)
    assert any(w.kind == "tick:round_close" and "th" in w.refs for w in wakes), (
        [str(w) for w in wakes])
    assert any("m2" in f and "do not parse" in f for f in audit(db))
