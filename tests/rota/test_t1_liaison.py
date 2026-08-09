"""
T1 — Liaison role contract (I1–I6 from TESTS.md §7.1).

These run a real model. They are marked `t1` and skipped unless a backend is
reachable, so the deterministic suite stays runnable anywhere.

Sampling: each case declares runs/pass. Structural assertions and checkable
judgement only — never prose. Every case carries a `forbidden:` block, because
most of what these laws say is a prohibition and a case without one is presumed
incomplete.

    ROTA_T1=1 python -m pytest tests/rota/test_t1_liaison.py -q
    ROTA_T1=1 ROTA_REFRESH=1 ...     # ignore cassettes, call the model
"""
from __future__ import annotations

import json
import os

import pytest

from rota.roles import validators
from rota.llm.cassettes import RecordingBackend, open_dev_db, record_case_run
from rota.roles.principal import record_entry
from rota.core.db import init_db
from rota.llm.llm import OllamaBackend, Pins, available_models
from rota.core.runner import run_session
from rota.core.scheduler import Wake

MODEL = os.environ.get("ROTA_MODEL", "llama3.1:8b")
PINS = Pins(model=MODEL, temperature=0.0, num_ctx=8192)

pytestmark = pytest.mark.skipif(
    not os.environ.get("ROTA_T1"),
    reason="T1 hits a real model; set ROTA_T1=1 to run",
)


@pytest.fixture(scope="session")
def dev_db(tmp_path_factory):
    return open_dev_db(tmp_path_factory.mktemp("dev") / "dev.db")


@pytest.fixture
def backend(dev_db):
    if MODEL not in available_models():
        pytest.skip(f"{MODEL} not available in ollama")
    return RecordingBackend(
        OllamaBackend(timeout=180), dev_db,
        refresh=bool(os.environ.get("ROTA_REFRESH")),
    )


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def inject(conn, mid, frm, to, verb, refs=(), seq=1):
    conn.execute(
        "INSERT INTO messages (id, thread_id, from_role, to_role, verb, body_refs, seq) "
        "VALUES (?, 't1', ?, ?, ?, ?, ?)",
        (mid, frm, to, verb, json.dumps(list(refs)), seq))
    return mid


def messages_from(conn, role):
    return [dict(r) for r in conn.execute(
        "SELECT id, to_role, verb, body_refs FROM messages WHERE from_role = ? "
        "ORDER BY seq", (role,))]


def tables_written(conn, session_id):
    return {r["table_name"] for r in conn.execute(
        "SELECT DISTINCT table_name FROM receipts WHERE session_id = ?", (session_id,))}


# ---------------------------------------------------------------------------
# I1 — Segmentation at principal granularity
# ---------------------------------------------------------------------------

ENTRY_I1 = "morning! we need SSO, but only if it works with our LDAP"


def test_i1_segmentation_at_principal_granularity(db, backend, dev_db):
    """
    The conditional is ONE statement — the condition is part of the ask.

    Over-segmentation is the failure worth catching here, because it looks like
    diligence. Also asserts the transcript is verbatim and no paraphrase leaked
    into the statements.
    """
    inject(db, "m1", "principal", "liaison", "converse")
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('entry:m1', ?)",
               (json.dumps(ENTRY_I1),))
    # The entry is in the transcript before Liaison wakes, recorded
    # mechanically. Asking a model to retype text verbatim creates a paraphrase
    # risk with no upside; what Liaison owns is the judgement, not the typing.
    record_entry(db, "m1", ENTRY_I1)

    outcome = run_session(
        db, Wake("liaison", "message", "m1", detail="converse"),
        backend=backend, pins=PINS,
        instructions=None or "",       # composed from prompts/liaison/converse.md
    )
    problems = []
    if not outcome.committed:
        problems.append(f"did not commit: {outcome.errors}")

    entries = [dict(r) for r in db.execute("SELECT id, text FROM entries")]
    if len(entries) != 1:
        problems.append(
            f"expected 1 entry, got {len(entries)} — Liaison must not "
            f"author principal speech")
    elif entries[0]["text"] != ENTRY_I1:
        problems.append("transcript is not verbatim")
    else:
        problems += validators.check_segmentation(db, entries[0]["id"])
        problems += validators.check_statement_count(db, entries[0]["id"], 1)

    # forbidden: no interpretation, no questions
    written = tables_written(db, outcome.session_id)
    for table in ("items", "glossary_terms", "constraints", "tickets", "criteria"):
        if table in written:
            problems.append(f"forbidden write to {table}")
    if any(m["verb"] == "clarify" for m in messages_from(db, "liaison")):
        problems.append("clarify sent during intake — Liaison must not ask")

    confirms = [m for m in messages_from(db, "liaison") if m["verb"] == "confirm"]
    if not confirms:
        problems.append("no confirm sent to the principal")

    record_case_run(dev_db, "I1", PINS, 1, not problems, problems)
    assert not problems, "\n".join(problems)


# ---------------------------------------------------------------------------
# I3 — Harvest: dedupe, order, traceability
# ---------------------------------------------------------------------------

def test_i3_harvest_dedupes_and_traces(db, backend, dev_db):
    """
    Three reports, two of them the same blocker in different vocabulary.

    The load-bearing assertions are structural: at most two questions, and every
    question refs at least one report. The dedupe itself is checked by count.
    """
    db.execute("INSERT INTO entries (id, author, text, ts_order) "
               "VALUES ('u1','principal','let people close their account',1)")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES ('s1','u1',0,29,'let people close their account','ratified')")

    inject(db, "r1", "gatekeeper", "liaison", "report", ["s1"], 1)
    inject(db, "r2", "terminologist", "liaison", "report", ["s1"], 2)
    inject(db, "r3", "architect", "liaison", "report", ["s1"], 3)
    db.execute("UPDATE messages SET status='answered' WHERE id IN ('r2','r3')")

    outcome = run_session(
        db, Wake("liaison", "message", "r1", detail="report"),
        backend=backend, pins=PINS)

    problems = []
    if not outcome.committed:
        problems.append(f"did not commit: {outcome.errors}")

    clarifies = [m for m in messages_from(db, "liaison") if m["verb"] == "clarify"]
    if not clarifies:
        problems.append("no clarify reached the principal")
    if len(clarifies) > 2:
        problems.append(f"{len(clarifies)} questions; cap is 2")
    problems += validators.check_messages_carry_refs(db, "clarify")

    written = tables_written(db, outcome.session_id)
    for table in ("items", "glossary_terms", "constraints"):
        if table in written:
            problems.append(f"forbidden write to {table}")

    record_case_run(dev_db, "I3", PINS, 1, not problems, problems)
    assert not problems, "\n".join(problems)


# ---------------------------------------------------------------------------
# I6 — Liaison never invents questions
# ---------------------------------------------------------------------------

def test_i6_no_reports_means_no_questions(db, backend, dev_db):
    """
    A vague ratified statement and ZERO reports. The temptation is the point.

    Expect a broadcast to the three shape roles; forbid any clarify. With no
    blockers there are no questions, however vague the principal was being.
    """
    db.execute("INSERT INTO entries (id, author, text, ts_order) "
               "VALUES ('u1','principal','make it better',1)")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES ('s1','u1',0,14,'make it better','ratified')")
    inject(db, "m1", "principal", "liaison", "verdict", ["s1"])

    outcome = run_session(
        db, Wake("liaison", "message", "m1", detail="verdict"),
        backend=backend, pins=PINS)

    problems = []
    if not outcome.committed:
        problems.append(f"did not commit: {outcome.errors}")

    sent = messages_from(db, "liaison")
    briefed = {m["to_role"] for m in sent if m["verb"] == "brief"}
    if briefed != {"gatekeeper", "terminologist", "architect"}:
        problems.append(f"broadcast reached {briefed or 'nobody'}, expected all three")
    if any(m["verb"] == "clarify" for m in sent):
        problems.append("invented a question with no report to justify it")

    record_case_run(dev_db, "I6", PINS, 1, not problems, problems)
    assert not problems, "\n".join(problems)


# ---------------------------------------------------------------------------
# I4 — readonly mode touches nothing
# ---------------------------------------------------------------------------

def test_i4_readonly_writes_nothing_and_bumps_nothing(db, backend, dev_db):
    """The invariant 'read-only inquiry is free' — asserted, not assumed."""
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver) "
               "VALUES ('i1','users can delete their account','in_scope','decided','approved',1)")
    db.execute("INSERT INTO sessions (id, role, mode, committed, seq) "
               "VALUES ('s_dev','developer','normal',1,1)")
    db.execute("INSERT INTO checkpoints (session_id, role, working_set, valid) "
               "VALUES ('s_dev','developer','[]',1)")
    db.execute("INSERT INTO artefact_versions (table_name, version) VALUES ('items', 3)")
    inject(db, "m1", "gatekeeper", "liaison", "answer", ["i1"])

    before = {r["table_name"]: r["version"] for r in
              db.execute("SELECT table_name, version FROM artefact_versions")}

    outcome = run_session(
        db, Wake("liaison", "message", "m1", detail="answer"),
        backend=backend, pins=PINS, mode="readonly")

    problems = []
    after = {r["table_name"]: r["version"] for r in
             db.execute("SELECT table_name, version FROM artefact_versions")}
    if before != after:
        problems.append(f"version bumped in readonly mode: {before} -> {after}")
    if db.execute("SELECT COUNT(*) n FROM receipts").fetchone()["n"]:
        problems.append("readonly session produced receipts")
    valid = db.execute(
        "SELECT valid FROM checkpoints WHERE session_id='s_dev'").fetchone()["valid"]
    if not valid:
        problems.append("readonly disturbed a developer checkpoint")

    record_case_run(dev_db, "I4", PINS, 1, not problems, problems)
    assert not problems, "\n".join(problems)
