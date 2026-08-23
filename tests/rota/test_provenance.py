"""
Why is this row here — backwards, from the artefact to the sentence.

The cockpit could already show every piece of this and no path through them.
Both times I have had to answer the question for real — the intake bug, and
then "what is a survey session actually shown" — the method was a throwaway
script joining four tables by hand. This is that join, kept.

The chain: **row -> the session that wrote it -> what that session was shown
and did -> what woke it -> what caused that**, back to a tick or to your own
sentence.

Almost all of it was already recorded and unjoined. `receipts` has carried
`(session_id, table_name, row_id)` on every commit since Law 4, which is the
link nobody was following. One link was genuinely missing and is added here:
a session woken by a *tick* recorded nothing about what woke it, because
`trigger_msg` is null for anything that is not a message — and in an onboarding
run that is every session. The chain would have stopped one step short of the
answer in exactly the case it exists for.
"""
from __future__ import annotations

import pytest

from rota.cockpit import inspect_api
from rota.core.db import SessionResult, Write, init_db, session_commit


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "prov.db")


def _session(conn, sid, role, *, writes, wake_kind="", wake_detail="",
             wake_refs=(), trigger=None, calls=()):
    session_commit(conn, SessionResult(
        session_id=sid, role=role, trigger_msg=trigger,
        wake_kind=wake_kind, wake_detail=wake_detail, wake_refs=tuple(wake_refs),
        writes=list(writes), tool_calls=list(calls),
        pins={"model": "llama3.1:8b", "prompt_hash": "abc123"}))


# ---------------------------------------------------------------------------
# The link that existed
# ---------------------------------------------------------------------------

def test_a_row_names_the_session_that_wrote_it(db):
    """
    `receipts` has recorded this on every commit since Law 4 and nothing read
    it back. The first link of the chain was never missing — it was unjoined.
    """
    _session(db, "s1", "terminologist", wake_kind="tick:survey",
             wake_detail="rota/core",
             writes=[Write("glossary_terms", "g_intent", {
                 "id": "g_intent", "term": "intent",
                 "sense_short": "a specific action or task",
                 "provenance": "observed"})])

    got = inspect_api.provenance(db, "glossary_terms", "g_intent")

    assert got["found"]
    assert got["row"]["term"] == "intent"
    assert got["session"]["id"] == "s1"
    assert got["session"]["role"] == "terminologist"
    assert got["session"]["model"] == "llama3.1:8b"


def test_an_amendment_shows_the_session_that_last_touched_it(db):
    """
    A row is written more than once. The question is nearly always about what
    it says *now*, so the latest receipt leads — and the earlier ones stay,
    because "who changed this and when" is the other half of the same question.
    """
    _session(db, "s1", "terminologist", wake_kind="tick:survey",
             writes=[Write("glossary_terms", "g1", {
                 "id": "g1", "term": "intent", "sense_short": "first",
                 "provenance": "observed"})])
    _session(db, "s2", "terminologist", wake_kind="tick:collision",
             writes=[Write("glossary_terms", "g1", {
                 "id": "g1", "term": "intent", "sense_short": "second",
                 "provenance": "decided"})])

    got = inspect_api.provenance(db, "glossary_terms", "g1")

    assert got["session"]["id"] == "s2"
    assert [h["session"] for h in got["history"]] == ["s1", "s2"]
    assert [h["version"] for h in got["history"]] == [1, 2]


def test_a_row_nothing_claims_says_so(db):
    """
    Onboarding writes `code_index` and constraint zero without a session, so
    "no receipt" is an ordinary answer and not a broken one. Saying nothing
    wrote it beats implying something did.
    """
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1','orphan','no session wrote me','observed')")

    got = inspect_api.provenance(db, "glossary_terms", "g1")

    assert got["found"] and got["session"] is None
    assert "no session" in got["note"].lower()


def test_a_row_that_does_not_exist_is_not_an_error(db):
    got = inspect_api.provenance(db, "glossary_terms", "nope")
    assert not got["found"] and got["session"] is None


# ---------------------------------------------------------------------------
# The link that was missing
# ---------------------------------------------------------------------------

def test_a_tick_session_records_what_woke_it(db):
    """
    The gap this file was written to close.

    `sessions.trigger_msg` is null for anything that is not a message, and in
    an onboarding run *every* session is a tick — 24 of 24 on the last real
    one. So the chain stopped at "terminologist wrote this" and could not say
    "because a survey tick fired on this area", which is the whole of the
    question for the case it exists for.
    """
    _session(db, "s1", "terminologist", wake_kind="tick:survey",
             wake_detail="rota/core",
             writes=[Write("glossary_terms", "g1", {
                 "id": "g1", "term": "grain", "sense_short": "a unit",
                 "provenance": "observed"})])

    got = inspect_api.provenance(db, "glossary_terms", "g1")

    assert got["woken_by"]["kind"] == "tick:survey"
    assert got["woken_by"]["detail"] == "rota/core"
    assert got["woken_by"]["message"] is None


def test_a_survey_wake_names_the_area_it_was_about(db):
    """
    Where the subject actually lives. A survey wake is
    `Wake(role, "tick:survey", refs=(area,))` — `detail` is empty and the area
    is in `refs`, so recording `detail` alone answered "a survey tick" and lost
    "of what", which is the half the question is about.

    Caught by reading a real run's chain and finding the area missing from it,
    not by reading the constructor.
    """
    _session(db, "s1", "terminologist", wake_kind="tick:survey",
             wake_refs=("src/icalendar",),
             writes=[Write("glossary_terms", "g1", {
                 "id": "g1", "term": "alarm", "sense_short": "an event",
                 "provenance": "observed"})])

    assert inspect_api.provenance(
        db, "glossary_terms", "g1")["woken_by"]["refs"] == ["src/icalendar"]


def test_a_message_session_walks_the_causal_chain_to_its_root(db):
    """
    The other half, which did work: a message wake follows `cause_id` back to
    whatever started it. This is the walk `edge_repeats` already does for the
    livelock bound, turned around and used to explain rather than to stop.
    """
    prev = None
    for i, (frm, to, verb) in enumerate([
            ("principal", "liaison", "converse"),
            ("liaison", "vision_keeper", "ratify"),
            ("vision_keeper", "terminologist", "define")], start=1):
        db.execute(
            "INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
            "body_refs, seq, status, cause_id) VALUES (?,?,?,?,?,'[]',?,?,?)",
            (f"m{i}", "t1", frm, to, verb, i, "answered", prev))
        prev = f"m{i}"

    _session(db, "s1", "terminologist", trigger="m3", wake_kind="message",
             writes=[Write("glossary_terms", "g1", {
                 "id": "g1", "term": "order", "sense_short": "a purchase",
                 "provenance": "decided"})])

    got = inspect_api.provenance(db, "glossary_terms", "g1")

    assert got["woken_by"]["message"] == "m3"
    assert [c["id"] for c in got["chain"]] == ["m3", "m2", "m1"]
    assert got["chain"][-1]["from_role"] == "principal"


def test_the_chain_cannot_loop_forever(db):
    """
    `cause_id` is data, and a database that has been edited by hand — or a bug
    — can point one at itself. A viewer that hangs on a malformed row is worse
    than one that shows a short chain.
    """
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status, cause_id) "
               "VALUES ('m1','t1','a','b','x','[]',1,'open','m1')")
    _session(db, "s1", "b", trigger="m1", wake_kind="message",
             writes=[Write("glossary_terms", "g1", {
                 "id": "g1", "term": "t", "sense_short": "s",
                 "provenance": "observed"})])

    got = inspect_api.provenance(db, "glossary_terms", "g1")
    assert [c["id"] for c in got["chain"]] == ["m1"]


# ---------------------------------------------------------------------------
# What the session was shown, and what is honestly not retained
# ---------------------------------------------------------------------------

def test_what_the_session_did_is_recorded_and_returned(db):
    """`tool_calls` is the record of what it actually reached for."""
    _session(db, "s1", "terminologist", wake_kind="tick:survey",
             calls=[("code.source", "rota/core/db.py"),
                    ("glossary.define", "grain")],
             writes=[Write("glossary_terms", "g1", {
                 "id": "g1", "term": "grain", "sense_short": "a unit",
                 "provenance": "observed"})])

    got = inspect_api.provenance(db, "glossary_terms", "g1")

    assert [c["fn"] for c in got["did"]] == ["code.source", "glossary.define"]
    assert got["did"][0]["args"] == "rota/core/db.py"


def test_the_brief_is_shown_and_the_working_set_is_admitted_missing(db):
    """
    The half that matters most and is only half available.

    The brief composes exactly — it is a function of role and mode — so it can
    be shown. What was *pushed* into the prompt is not retained anywhere; only
    `prompt_hash` is, and that hashes the whole prompt, so it cannot even
    confirm the brief alone is unchanged.

    Saying so is the point. A reconstruction presented as the real prompt is
    how "the sentence was in there, so the role must have ignored it" survives
    for a week — which is exactly what the intake bug turned out not to be.
    """
    _session(db, "s1", "terminologist", wake_kind="tick:survey",
             writes=[Write("glossary_terms", "g1", {
                 "id": "g1", "term": "grain", "sense_short": "a unit",
                 "provenance": "observed"})])

    shown = inspect_api.provenance(db, "glossary_terms", "g1")["shown"]

    assert shown["brief"], "the composed brief is reconstructible and was not shown"
    assert shown["tools"], "the toolkit is derived from the graph"
    assert shown["working_set"] is None
    assert "not retained" in shown["note"].lower()
    assert shown["prompt_hash"] == "abc123"
