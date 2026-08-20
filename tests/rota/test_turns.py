"""
What the model was actually shown, and what it actually said.

The provenance panel had to admit this: *"the working set pushed into this
prompt is not retained; the brief and toolkit below are rebuilt from the current
prompts and graph, which may have changed since this session ran."* A
reconstruction is not the prompt. It is how "the sentence was in there, so the
role ignored it" survives for a week — and the intake bug was the opposite, the
sentence was absent, and only printing the real prompt showed it.

Twice more this session the same gap cost real time. `L1-DV-fix-the-code` was
reported fixed while the model's tool call was being discarded as malformed;
only reading the recorded completion showed it. And the Developer "choosing to
stop" after five calls was diagnosed through three dead hypotheses that a
transcript would have settled in one look.

`tool_calls` records what a session *did*. `turns` records what it was told and
what it said — one row per model round-trip, which is what a session is a
conversation of.

The cassettes have carried exactly this for the test corpus all along, keyed by
prompt hash. What was missing is the same thing for a *run*, where there is no
case id and the question is about this project rather than about a prompt.
"""
from __future__ import annotations

import pytest

from rota.core.db import SessionResult, Turn, Write, init_db, session_commit


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "t.db")


def test_a_session_records_what_it_was_shown_and_what_it_said(db):
    """The whole point: the exact context and the exact response."""
    session_commit(db, SessionResult(
        session_id="s1", role="terminologist", wake_kind="tick:survey",
        turns=[Turn(1, "you are terminologist", "survey src/auth",
                    "TOOL: code.survey()"),
               Turn(2, "you are terminologist", "survey src/auth\n\nRESULT: ...",
                    "TOOL: glossary.amend(term='hold')")],
        writes=[Write("glossary_terms", "g1", {
            "id": "g1", "term": "hold", "sense_short": "a reservation",
            "provenance": "observed"})]))

    rows = db.execute(
        "SELECT seq, system, user, completion FROM turns "
        "WHERE session_id = 's1' ORDER BY seq").fetchall()

    assert len(rows) == 2
    assert rows[0]["user"] == "survey src/auth"
    assert rows[0]["completion"] == "TOOL: code.survey()"
    assert "RESULT" in rows[1]["user"], "the growing context is the point"


def test_turns_die_with_the_session_that_did_not_commit(db):
    """
    Law 4: a session's writes, messages and receipt commit together or not at
    all. A transcript that outlived a rolled-back session would be a record of
    something that did not happen — and it is the *most* convincing kind of
    record, because it reads like an eyewitness.
    """
    with pytest.raises(Exception):
        session_commit(db, SessionResult(
            session_id="s1", role="terminologist",
            turns=[Turn(1, "sys", "user", "reply")],
            writes=[Write("glossary_terms", "g1", {"id": "g1"})]))  # no NOT NULLs

    assert db.execute("SELECT COUNT(*) n FROM turns").fetchone()["n"] == 0


def test_the_provenance_chain_serves_the_real_prompt_when_it_has_one(db):
    """
    The admission gets to go away. `shown` stops being a rebuild of today's
    brief and becomes what that session read, which is the question people
    actually open the panel to ask.
    """
    from rota.cockpit import inspect_api

    session_commit(db, SessionResult(
        session_id="s1", role="terminologist", wake_kind="tick:survey",
        wake_refs=("src/auth",),
        turns=[Turn(1, "SYSTEM TEXT HERE", "USER TEXT HERE", "TOOL: x()")],
        writes=[Write("glossary_terms", "g1", {
            "id": "g1", "term": "hold", "sense_short": "a reservation",
            "provenance": "observed"})]))

    shown = inspect_api.provenance(db, "glossary_terms", "g1")["shown"]

    assert shown["turns"], "the recorded turns were not served"
    assert shown["turns"][0]["system"] == "SYSTEM TEXT HERE"
    assert shown["turns"][0]["user"] == "USER TEXT HERE"
    assert "not retained" not in shown["note"].lower(), (
        "the panel still apologises for something it now has")


def test_a_session_recorded_before_turns_existed_still_explains_itself(db):
    """
    Every database written before this column is one where the honest answer is
    the reconstruction plus the admission. Losing that fallback would make old
    runs less inspectable than they were.
    """
    from rota.cockpit import inspect_api

    session_commit(db, SessionResult(
        session_id="s1", role="terminologist", wake_kind="tick:survey",
        writes=[Write("glossary_terms", "g1", {
            "id": "g1", "term": "hold", "sense_short": "a reservation",
            "provenance": "observed"})]))

    shown = inspect_api.provenance(db, "glossary_terms", "g1")["shown"]

    assert shown["turns"] == []
    assert shown["brief"], "the rebuilt brief is the fallback"
    assert "not retained" in shown["note"].lower()
