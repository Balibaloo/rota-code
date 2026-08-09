"""
T0 — plumbing. Deterministic, mock LLM, exact-match asserts.

Case ids trace to TESTS.md §6. Where a case's assertion here differs from the
spec, the divergence is stated in the docstring — never quietly weakened.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

from rota import graph as graph_mod
from rota.boot import (
    boot, quarantine_exhausted, reap_claims, reap_processes, reconcile_worktrees,
)
from rota.db import (
    ConsultWriteError, OutboundMessage, SessionResult, Write, init_db,
    session_commit, version_of,
)
from rota.scheduler import (
    RoleBusy, Wake, cascade_order, cascade_wakes, claim, constraints_for_grains,
    constraint_zero_area_coverage, frontier, is_quiescent, open_tips,
    predicate_wakes, rebuild_schedule, schedule_order, sweep_checkpoints,
    tick_agenda, tick_batch_start, tick_criteria, tick_slicing,
    UnsatisfiableSchedule,
)


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def seed_item(conn, item_id="i1", approval="approved", version=1, approval_ver=1):
    conn.execute(
        "INSERT INTO items (id, text, kind, provenance, approval, approval_ver, version) "
        "VALUES (?, 'let users delete their account', 'scope', 'decided', ?, ?, ?)",
        (item_id, approval, approval_ver, version),
    )


def seed_batch(conn, batch_id="b1", item_id="i1", status="pending", worktree=None):
    conn.execute(
        "INSERT INTO batches (id, item_id, status, worktree) VALUES (?, ?, ?, ?)",
        (batch_id, item_id, status, worktree),
    )


# ---------------------------------------------------------------------------
# T0-S1  Atomic session commit
# ---------------------------------------------------------------------------

def test_s1_atomic_commit_all_or_nothing(db):
    """A failing write inside a session leaves zero rows from that session."""
    db.execute("INSERT INTO utterances (id, author, text, ts_order) VALUES ('u1','client','x',1)")

    bad = SessionResult(
        session_id="s1", role="interface",
        writes=[
            Write("statements", "st1", {
                "span_utterance": "u1", "span_start": 0, "span_end": 1,
                "text": "x", "status": "proposed"}),
            # violates the CHECK constraint: the whole session must roll back
            Write("statements", "st2", {
                "span_utterance": "u1", "span_start": 0, "span_end": 1,
                "text": "y", "status": "nonsense"}),
        ],
        messages=[OutboundMessage(id="m1", to_role="client", verb="confirm")],
    )

    with pytest.raises(Exception):
        session_commit(db, bad)

    assert db.execute("SELECT COUNT(*) n FROM statements").fetchone()["n"] == 0
    assert db.execute("SELECT COUNT(*) n FROM sessions").fetchone()["n"] == 0
    assert db.execute("SELECT COUNT(*) n FROM messages").fetchone()["n"] == 0
    assert db.execute("SELECT COUNT(*) n FROM receipts").fetchone()["n"] == 0
    assert version_of(db, "statements") == 0, "version bumped by a session that never happened"


def test_s1_committed_session_produces_receipt_per_write(db):
    db.execute("INSERT INTO utterances (id, author, text, ts_order) VALUES ('u1','client','x',1)")
    session_commit(db, SessionResult(
        session_id="s1", role="interface",
        writes=[Write("statements", "st1", {
            "span_utterance": "u1", "span_start": 0, "span_end": 1,
            "text": "x", "status": "proposed"})],
    ))
    receipts = db.execute("SELECT * FROM receipts WHERE session_id='s1'").fetchall()
    assert len(receipts) == 1
    assert receipts[0]["table_name"] == "statements"
    assert receipts[0]["new_version"] == version_of(db, "statements") == 1


def test_s1_kill_between_tool_calls_leaves_nothing(tmp_path):
    """
    Kill the runner mid-session: zero rows from that session, trigger still open.

    Uses a real subprocess killed with SIGKILL rather than a simulated failure —
    the point of the case is that an *un*graceful death is safe.
    """
    dbpath = tmp_path / "rota.db"
    conn = init_db(dbpath)
    conn.execute(
        "INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
        "VALUES ('m1','t1','interface','vision','brief',1)"
    )
    conn.close()

    script = f'''
import sys, os, time
sys.path.insert(0, {str(tmp_path.parents[0] / "x")!r})
sys.path.insert(0, {os.getcwd()!r})
from rota.db import connect
conn = connect({str(dbpath)!r})
conn.execute("BEGIN IMMEDIATE")
conn.execute("INSERT INTO sessions (id, role, trigger_msg, mode, committed, seq) "
             "VALUES ('s_dead','vision','m1','normal',1,1)")
conn.execute("INSERT INTO items (id, text, kind, provenance) "
             "VALUES ('i_dead','half written','scope','decided')")
print("READY", flush=True)
time.sleep(30)
'''
    proc = subprocess.Popen([sys.executable, "-c", script],
                            stdout=subprocess.PIPE, text=True)
    assert proc.stdout.readline().strip() == "READY"
    proc.kill()
    proc.wait(timeout=10)

    conn = init_db(dbpath)
    assert conn.execute("SELECT COUNT(*) n FROM sessions").fetchone()["n"] == 0
    assert conn.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 0
    tips = open_tips(conn)
    assert [w.message_id for w in tips] == ["m1"], "trigger message left the frontier"


# ---------------------------------------------------------------------------
# T0-S2  Frontier correctness
# ---------------------------------------------------------------------------

def test_s2_frontier_returns_open_tips_and_batch_root(db):
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq, status) "
               "VALUES ('m_open','t1','interface','vision','brief',1,'open')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq, status) "
               "VALUES ('m_done','t1','interface','domain','brief',2,'answered')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq, status) "
               "VALUES ('m_client','t1','interface','client','clarify',3,'open')")
    seed_item(db)
    seed_batch(db)

    tips = open_tips(db)
    assert [w.message_id for w in tips] == ["m_open"], "answered or client-bound tips leaked in"

    wakes = frontier(db)
    assert Wake("developer", "tick:batch_start", refs=("b1",)) in wakes


def test_s2_quiescence_is_empty_frontier(db):
    assert is_quiescent(db)
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
               "VALUES ('m1','t1','interface','vision','brief',1)")
    assert not is_quiescent(db)


def test_s2_residual_work_is_derived_not_remembered(db):
    """
    The point of predicates-as-state: an approved item with no tickets is not a
    message, so nothing would ever wake Vision for it. It must be re-derived.
    """
    seed_item(db)
    assert any(w.kind == "tick:slicing" for w in frontier(db))

    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('t1','i1','delete button')")
    assert not any(w.kind == "tick:slicing" for w in frontier(db))
    # ... and now criteria are missing, so the next predicate fires instead.
    assert any(w.kind == "tick:criteria" for w in frontier(db))


# ---------------------------------------------------------------------------
# T0-S3  Scheduler disposability
# ---------------------------------------------------------------------------

def test_s3_scheduler_disposability(tmp_path):
    """
    Compute the frontier, kill the whole process, restart cold, recompute:
    identical.

    A fresh interpreter is the only honest version of this test — reloading the
    module in-process would rebind its classes and prove nothing about state.
    The scheduler has no instance to kill, which is the property under test:
    restarting it is re-running pure functions against the same rows.
    """
    dbpath = tmp_path / "rota.db"
    conn = init_db(dbpath)
    seed_item(conn)
    seed_batch(conn)
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
                 "VALUES ('m1','t1','interface','vision','brief',1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('t1','i1','x')")
    conn.close()

    probe = (
        "import sys; sys.path.insert(0, %r)\n"
        "from rota.db import connect\n"
        "from rota.scheduler import frontier\n"
        "conn = connect(%r)\n"
        "print('|'.join(str(w) for w in frontier(conn)))\n"
    ) % (os.getcwd(), str(dbpath))

    def run_cold() -> str:
        out = subprocess.run([sys.executable, "-c", probe],
                             capture_output=True, text=True, timeout=60)
        assert out.returncode == 0, out.stderr
        return out.stdout.strip()

    first = run_cold()
    second = run_cold()
    assert first == second, "a restarted scheduler produced a different frontier"
    assert first, "frontier was empty; the test proves nothing"


# ---------------------------------------------------------------------------
# T0-S4  Revocation predicate
# ---------------------------------------------------------------------------

def test_s4_amendment_makes_batches_unschedulable(db):
    seed_item(db, approval="approved", version=3, approval_ver=3)
    seed_batch(db)
    assert tick_batch_start(db), "approved item with current approval should schedule"

    db.execute("UPDATE items SET version = 4 WHERE id='i1'")     # amended
    assert not tick_batch_start(db), "amendment did not stop the batch"

    db.execute("UPDATE items SET approval_ver = 5, version = 5 WHERE id='i1'")  # re-approved
    assert tick_batch_start(db), "re-approval did not restore schedulability"


def test_s4_running_batch_blocks_others(db):
    seed_item(db)
    seed_batch(db, "b1", status="running")
    seed_batch(db, "b2", status="pending")
    assert not tick_batch_start(db), "developer is single-instance"


# ---------------------------------------------------------------------------
# T0-S5  Binding intersection
# ---------------------------------------------------------------------------

def _constraint(conn, cid, grains=(), is_global=0, resolves=1):
    conn.execute(
        "INSERT INTO constraints (id, headline, provenance, is_global) VALUES (?,?,?,?)",
        (cid, f"headline {cid}", "decided", is_global),
    )
    for g in grains:
        conn.execute(
            "INSERT INTO constraint_bindings (constraint_id, grain, grain_kind, resolves) "
            "VALUES (?,?,?,?)", (cid, g, "path", resolves),
        )


def test_s5_binding_intersection_selects_touched(db):
    _constraint(db, "c1", grains=["src/billing.py"])
    _constraint(db, "c2", grains=["src/ui.py"])
    assert constraints_for_grains(db, ["src/billing.py"]) == ["c1"]


def test_s5_global_binding_triggers_always(db):
    _constraint(db, "c_global", is_global=1)
    _constraint(db, "c1", grains=["src/billing.py"])
    assert "c_global" in constraints_for_grains(db, ["unrelated.py"])


def test_s5_unbound_means_global_never_invisible(db):
    """Missing bindings must always mean 'always visible'."""
    _constraint(db, "c_unbound", grains=[])
    assert "c_unbound" in constraints_for_grains(db, ["anything.py"])


def test_s5_unresolvable_bindings_promote_to_global(db):
    """
    A binding naming a grain that no longer exists promotes its constraint back
    to global until someone re-binds it. Degradation lands on 'expensive',
    never on 'wrong'.
    """
    _constraint(db, "c_stale", grains=["src/deleted.py"], resolves=0)
    assert "c_stale" in constraints_for_grains(db, ["unrelated.py"])


# ---------------------------------------------------------------------------
# T0-S6  Constraint-zero shrink
# ---------------------------------------------------------------------------

def test_s6_none_found_counts_as_surveyed(db):
    for grain, area in [("a/x.py", "auth"), ("b/y.py", "billing")]:
        db.execute("INSERT INTO code_index (grain, grain_kind, area) VALUES (?,?,?)",
                   (grain, "path", area))
    surveyed, residue = constraint_zero_area_coverage(db)
    assert residue == {"auth", "billing"}

    db.execute("INSERT INTO survey_records (id, area, outcome) VALUES ('s1','auth','none_found')")
    surveyed, residue = constraint_zero_area_coverage(db)
    assert surveyed == {"auth"} and residue == {"billing"}

    db.execute("INSERT INTO survey_records (id, area, outcome) "
               "VALUES ('s2','billing','constraints_found')")
    _, residue = constraint_zero_area_coverage(db)
    assert residue == set(), "full coverage should empty constraint zero"


# ---------------------------------------------------------------------------
# T0-S7  Checkpoint invalidation
# ---------------------------------------------------------------------------

def test_s7_disjoint_receipt_keeps_checkpoint_valid(db):
    db.execute("INSERT INTO sessions (id, role, mode, committed, seq) "
               "VALUES ('s1','developer','normal',1,1)")
    db.execute("INSERT INTO artefact_versions (table_name, version) VALUES ('constraints', 4)")
    db.execute("INSERT INTO checkpoints (session_id, role, working_set, valid) "
               "VALUES ('s1','developer',?,1)", (json.dumps([["constraints", 4]]),))

    db.execute("INSERT INTO artefact_versions (table_name, version) VALUES ('glossary_terms', 9)")
    assert sweep_checkpoints(db) == []
    assert db.execute("SELECT valid FROM checkpoints WHERE session_id='s1'").fetchone()["valid"] == 1


def test_s7_overlapping_receipt_invalidates(db):
    db.execute("INSERT INTO sessions (id, role, mode, committed, seq) "
               "VALUES ('s1','developer','normal',1,1)")
    db.execute("INSERT INTO artefact_versions (table_name, version) VALUES ('constraints', 4)")
    db.execute("INSERT INTO checkpoints (session_id, role, working_set, valid) "
               "VALUES ('s1','developer',?,1)", (json.dumps([["constraints", 4]]),))

    db.execute("UPDATE artefact_versions SET version = 5 WHERE table_name='constraints'")
    assert sweep_checkpoints(db) == ["s1"]
    assert db.execute("SELECT valid FROM checkpoints WHERE session_id='s1'").fetchone()["valid"] == 0


# ---------------------------------------------------------------------------
# T0-S8  Consult isolation
# ---------------------------------------------------------------------------

def test_s8_consult_write_is_refused_and_bumps_nothing(db):
    """
    Spec note: TESTS.md words this as a 'hard error'. Implemented as an ordinary
    refusal — the write is *unavailable*, not session-fatal. Consult sandboxes do
    not export writers at all; this is the belt to that braces.
    """
    before = version_of(db, "items")
    with pytest.raises(ConsultWriteError):
        session_commit(db, SessionResult(
            session_id="s_consult", role="vision", mode="consult",
            writes=[Write("items", "i1", {
                "text": "x", "kind": "scope", "provenance": "decided"})],
        ))
    assert version_of(db, "items") == before
    assert db.execute("SELECT COUNT(*) n FROM items").fetchone()["n"] == 0


def test_s8_consult_may_read_and_answer(db):
    session_commit(db, SessionResult(
        session_id="s_consult", role="vision", mode="consult",
        messages=[OutboundMessage(id="m_ans", to_role="interface", verb="answer")],
        tool_calls=[("problem.consult", "")],
    ))
    assert db.execute("SELECT COUNT(*) n FROM messages WHERE verb='answer'").fetchone()["n"] == 1
    assert db.execute("SELECT COUNT(*) n FROM receipts").fetchone()["n"] == 0


# ---------------------------------------------------------------------------
# T0-S11  Cascade order
# ---------------------------------------------------------------------------

def test_s11_cascade_walks_refs_dag_developer_never_first(db):
    g = graph_mod.load()
    db.execute("INSERT INTO sessions (id, role, mode, committed, seq) "
               "VALUES ('s1','architect','normal',1,1)")
    db.execute("INSERT INTO receipts (session_id, table_name, row_id, new_version) "
               "VALUES ('s1','constraints','c1',2)")

    wakes = cascade_wakes(db, "s1", g)
    roles = [w.role for w in wakes]
    assert roles, "a receipt on constraints should cascade"
    assert roles[0] != "developer", "developer woken first by the cascade"
    assert all(w.kind == "cascade" for w in wakes)


def test_s11_cascade_produces_zero_role_messages(db):
    """Wakes are scheduler events carrying receipts — never role-to-role messages."""
    db.execute("INSERT INTO sessions (id, role, mode, committed, seq) "
               "VALUES ('s1','architect','normal',1,1)")
    db.execute("INSERT INTO receipts (session_id, table_name, row_id, new_version) "
               "VALUES ('s1','constraints','c1',2)")
    before = db.execute("SELECT COUNT(*) n FROM messages").fetchone()["n"]
    cascade_wakes(db, "s1")
    assert db.execute("SELECT COUNT(*) n FROM messages").fetchone()["n"] == before


# ---------------------------------------------------------------------------
# T0-S12  Contact enforcement
# ---------------------------------------------------------------------------

def test_s12_graph_is_self_consistent():
    """The boot assertion: derived contacts agree with declared message edges."""
    graph_mod.assert_consistent()


def test_s12_non_derived_recipients_are_rejected():
    g = graph_mod.load()
    assert not g.may_message("developer", "client", "converse"), \
        "developer must not reach the client"
    assert not g.may_message("developer", "planner", "order"), \
        "dispatch is a query; no role asks what to work on"
    assert g.may_message("developer", "architect", "escalate")
    assert g.may_message("developer", "tester", "challenge"), \
        "a developer disputing a test must reach the test's owner"


def test_s12_verb_vocabulary_is_closed():
    g = graph_mod.load()
    verbs = g.message_verbs()
    assert "escalate" in verbs and "finding" in verbs and "challenge" in verbs
    assert "order" not in verbs, "planner's verb should have left with the role"


# ---------------------------------------------------------------------------
# T0-S13 / roles are single-instance
# ---------------------------------------------------------------------------

def test_s13_role_cannot_hold_two_sessions(db):
    db.execute("INSERT INTO sessions (id, role, mode, committed, seq) VALUES ('s1','vision','normal',0,1)")
    db.execute("INSERT INTO sessions (id, role, mode, committed, seq) VALUES ('s2','vision','normal',0,2)")
    claim(db, "vision", "s1")
    with pytest.raises(RoleBusy):
        claim(db, "vision", "s2")


# ---------------------------------------------------------------------------
# Ordering (formerly Planner's P1) — now scheduler code
# ---------------------------------------------------------------------------

def test_ordering_is_a_valid_topological_sort(db):
    seed_item(db)
    for b in ("b1", "b2", "b3", "b4"):
        seed_batch(db, b)
    db.execute("INSERT INTO batch_dep_facts (before_batch, after_batch) VALUES ('b1','b2')")

    order = rebuild_schedule(db)
    assert order.index("b1") < order.index("b2")
    assert set(order) == {"b1", "b2", "b3", "b4"}


def test_ordering_cycle_is_raised_not_guessed(db):
    seed_item(db)
    seed_batch(db, "b1")
    seed_batch(db, "b2")
    db.execute("INSERT INTO batch_dep_facts (before_batch, after_batch) VALUES ('b1','b2')")
    db.execute("INSERT INTO batch_dep_facts (before_batch, after_batch) VALUES ('b2','b1')")
    with pytest.raises(UnsatisfiableSchedule):
        schedule_order(db)


def test_ordering_contains_no_time(db):
    """Time is not a concept: no date/duration fields anywhere in the schedule."""
    cols = [r[1] for r in db.execute("PRAGMA table_info(schedule_deps)")]
    banned = ("date", "time", "deadline", "duration", "eta", "due")
    assert not [c for c in cols if any(b in c.lower() for b in banned)]


# ---------------------------------------------------------------------------
# Boot sequence
# ---------------------------------------------------------------------------

def test_boot_reaps_stale_claim(db):
    db.execute("INSERT INTO sessions (id, role, mode, committed, seq) VALUES ('s1','vision','normal',0,1)")
    claim(db, "vision", "s1")
    assert reap_claims(db) == ["vision:s1"]
    assert db.execute("SELECT COUNT(*) n FROM claims").fetchone()["n"] == 0


def test_boot_keeps_suspended_claim(db):
    """A suspended session (checkpoint on file) legitimately still holds its claim."""
    db.execute("INSERT INTO sessions (id, role, mode, committed, seq) VALUES ('s1','developer','normal',1,1)")
    db.execute("INSERT INTO checkpoints (session_id, role, working_set, valid) "
               "VALUES ('s1','developer','[]',1)")
    claim(db, "developer", "s1")
    assert reap_claims(db) == []
    assert db.execute("SELECT COUNT(*) n FROM claims").fetchone()["n"] == 1


def test_boot_reaps_orphan_processes(db):
    seed_item(db)
    seed_batch(db)
    db.execute("INSERT INTO runtime_processes (pid, batch_id, command) VALUES (999999,'b1','serve')")
    assert reap_processes(db, kill=False) == [999999]
    assert db.execute("SELECT COUNT(*) n FROM runtime_processes").fetchone()["n"] == 0


def test_boot_quarantines_exhausted_message(db):
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq, attempts) "
               "VALUES ('m1','t1','interface','vision','brief',1,10)")
    assert quarantine_exhausted(db, cap=10) == ["m1"]
    assert open_tips(db) == [], "a quarantined message must leave the frontier"


def test_boot_full_sequence_on_empty_project(tmp_path):
    conn, report = boot(tmp_path, kill_processes=False)
    assert report.onboarding is True, "absent state folder means onboarding initiation"
    assert (tmp_path / ".rota" / "rota.db").exists()

    conn2, report2 = boot(tmp_path, kill_processes=False)
    assert report2.onboarding is False, "second boot is not onboarding"


def test_boot_detects_worktree_divergence(db, tmp_path):
    """
    Git commits are outside the transaction, so the DB lags the codebase. Boot
    must notice rather than let a cold Developer duplicate finished work.
    """
    wt = tmp_path / "wt"
    wt.mkdir()
    subprocess.run(["git", "init", "-q", str(wt)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(wt), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(wt), "config", "user.name", "t"], check=True)
    (wt / "f.txt").write_text("x")
    subprocess.run(["git", "-C", str(wt), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(wt), "commit", "-q", "-m", "work"],
                   check=True, capture_output=True)

    seed_item(db)
    db.execute("INSERT INTO batches (id, item_id, status, worktree, head_commit) "
               "VALUES ('b1','i1','running',?,'0000000')", (str(wt),))

    diverged = reconcile_worktrees(db)
    assert len(diverged) == 1
    assert diverged[0][0] == "b1"
    assert diverged[0][1] == "0000000" and len(diverged[0][2]) == 40
