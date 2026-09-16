"""
Synthetic arc — composition evidence, with zero LLM judgement involved.

Each part of the machine passing does not prove the parts compose, and the
design's real composition evidence (T2 arcs) needs roles to exist. This closes
that gap early: canned completions stand in for every role and drive a full
lifecycle through the *real* scheduler, sandbox, bus and commit path.

What it exercises: frontier as tips ∪ predicates, the tick predicates firing in
sequence, claims, derived contacts, atomic commits, receipts, cascade, and the
revocation predicate. What it does not exercise: whether any role reasons well.
That is deliberate — this is the wiring test.
"""
from __future__ import annotations

import json

import pytest

from rota.design import graph as graph_mod
from rota.roles import validators as validators_mod
from rota.roles.principal import record_entry
from rota.core.db import init_db
from rota.llm.llm import Pins, ScriptedBackend
from rota.core.runner import run_session
from rota.roles import prompts as prompts_mod
from rota.core.scheduler import (
    Wake, cascade_wakes, frontier, is_quiescent, predicate_wakes, release,
)
from rota.testkit.fixtures import refs_from_columns


PINS = Pins(model="scripted", temperature=0.0, num_ctx=4096)


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def drive(conn, wake: Wake, script: list[str], **kw):
    """Run one session with canned completions and assert it committed."""
    outcome = run_session(conn, wake, backend=ScriptedBackend(script + ["done"]),
                          pins=PINS, **kw)
    assert outcome.committed, f"{wake} failed: {outcome.errors}"
    return outcome


# ---------------------------------------------------------------------------

def test_arc_understanding_loop_reaches_approved_item(db):
    """
    Principal entry -> statements -> ratification -> scope item -> approval.

    Every step is a real session through the real machine; only the completions
    are canned.
    """
    # --- intake: the entry arrives already recorded, Liaison segments ---
    # Recording is mechanical: the transcript is the one un-interpreted thing in
    # the system, so nothing retypes it. Liaison owns the judgement half.
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
               "VALUES ('m_intake','t1','principal','liaison','converse',1)")
    record_entry(db, "m_intake", "add a button so people can delete their account")

    drive(db, Wake("liaison", "message", "m_intake", detail="converse"), [
        "TOOL: brief.segment(id='s1', span_entry='e_m_intake', span_start=0, "
        "span_end=46, text='add a button so people can delete their account')",
        "TOOL: msg.confirm_principal(refs=['s1'])",
    ])

    assert db.execute("SELECT COUNT(*) n FROM entries").fetchone()["n"] == 1
    assert db.execute("SELECT status FROM statements WHERE id='s1'").fetchone()["status"] == "proposed"

    # The principal is not schedulable: a message to them waits, it does not wake.
    assert not [w for w in frontier(db) if w.role == "principal"]

    # --- ratification --------------------------------------------------------
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
               "VALUES ('m_ratify','t1','principal','liaison','verdict',3)")
    drive(db, Wake("liaison", "message", "m_ratify", detail="verdict"), [
        "TOOL: brief.ratify(id='s1')",
        "TOOL: msg.deliver_vision_keeper(refs=['s1'])",
        "TOOL: msg.deliver_terminologist(refs=['s1'])",
        "TOOL: msg.deliver_architect(refs=['s1'])",
    ])

    assert db.execute("SELECT status FROM statements WHERE id='s1'").fetchone()["status"] == "ratified"
    tips = {w.role for w in frontier(db) if w.kind == "message"}
    assert tips == {"vision_keeper", "terminologist", "architect"}, "broadcast did not reach three shape roles"

    # --- Vision Keeper asserts scope; Terminologist amends the glossary -------------------
    vision_keeper_msg = db.execute(
        "SELECT id FROM messages WHERE to_role='vision_keeper' AND verb='deliver'").fetchone()["id"]
    drive(db, Wake("vision_keeper", "message", vision_keeper_msg, detail="deliver"), [
        "TOOL: problem.assert(id='i1', text='users can delete their account', kind='in_scope')",
    ])

    terminologist_msg = db.execute(
        "SELECT id FROM messages WHERE to_role='terminologist' AND verb='deliver'").fetchone()["id"]
    drive(db, Wake("terminologist", "message", terminologist_msg, detail="deliver"), [
        "TOOL: glossary.amend(id='g1', term='account', sense_short='login identity')",
    ])

    # --- approval ------------------------------------------------------------
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
               "VALUES ('m_signoff','t1','liaison','vision_keeper','relay',20)")
    drive(db, Wake("vision_keeper", "message", "m_signoff", detail="relay"), [
        "TOOL: problem.set_approval(id='i1', approval='approved')",
    ])

    item = db.execute("SELECT approval, approval_ver, version FROM items WHERE id='i1'").fetchone()
    assert item["approval"] == "approved"
    assert item["approval_ver"] >= item["version"], "approval must postdate the last amendment"

    # --- and now residual work is *derived*, not remembered ------------------
    assert any(w.kind == "tick:slicing" for w in predicate_wakes(db)), \
        "an approved unsliced item should re-derive work with no message involved"


def test_arc_delivery_loop_slices_batches_and_tests(db):
    """Approved item -> tickets -> criteria -> batch -> tests -> verdict."""
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver, version) "
               "VALUES ('i1','users can delete their account','in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1','account','login identity','decided')")

    # Vision Keeper slices, woken by a predicate rather than a message.
    slicing = [w for w in predicate_wakes(db) if w.kind == "tick:slicing"]
    assert slicing, "slicing predicate did not fire for an approved item"
    drive(db, slicing[0], [
        "TOOL: tickets.slice(id='tk1', item_id='i1', text='add delete button')",
    ])

    # Terminologist writes criteria — woken by the criteria predicate.
    crit = [w for w in predicate_wakes(db) if w.kind == "tick:criteria"]
    assert crit, "criteria predicate did not fire for a ticket with no criteria"
    drive(db, crit[0], [
        "TOOL: criteria.specify(id='c1', ticket_id='tk1', "
        "text='deleting tombstones the account', term_refs=['g1'])",
    ])

    refs = [r["target"] for r in db.execute(
        "SELECT target FROM refs WHERE src_table = 'criteria' AND src_id = 'c1' "
        "AND kind = 'term'")]
    assert refs == ["g1"], "criteria must be written in glossary terms"

    # Architect groups tickets into batches. Its own tick, not the `deliver`
    # message: grouping is a different job from reading new statements, and the
    # mode's tool list says so -- the first version of this arc grouped in
    # `deliver` mode and the narrowing refused it, which is the narrowing working.
    grouping = [w for w in predicate_wakes(db) if w.kind == "tick:grouping"]
    assert grouping, "tickets with criteria never became a batch"
    drive(db, Wake("architect", "tick:grouping", refs=grouping[0].refs), [
        "TOOL: batches.group(id='b1', item_id='i1', ticket_ids=['tk1'])",
    ])

    # Tester writes from criteria — and cannot see a diff, because none exists.
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
               "VALUES ('m_test','t1','liaison','tester','question',60)")
    drive(db, Wake("tester", "message", "m_test", detail="tick"), [
        "TOOL: tests.triage(criterion_id='c1', verdict='encodable')",
        "TOOL: tests.encode(id='t1', batch_id='b1', criterion_id='c1', "
        "path='test_delete.py', body='from seam import tombstoned, account\ndef test_it():\n    assert tombstoned(account)')",
    ], batch_id="b1")

    assert db.execute("SELECT COUNT(*) n FROM tests").fetchone()["n"] == 1

    # Critic judges the diff given the tests, and emits a verdict.
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
               "VALUES ('m_review','t1','liaison','critic','challenge',70)")
    drive(db, Wake("critic", "message", "m_review", detail="review"), [
        "TOOL: criteria.load(batch_id='b1')",
        "TOOL: tests.load(batch_id='b1')",
        "TOOL: verdicts.claim_encodes(criterion_id='c1', encodes=True)",
        "TOOL: verdicts.emit(batch_id='b1', result='fail', failed_criterion='c1')",
        "TOOL: msg.challenge_developer(refs=['c1'])",
    ], batch_id="b1")

    # One verdict, and its id is derived rather than named: a judgement is by
    # one role, on one batch, at one commit, which is the triple `review` gates
    # on. Asserting on the row rather than on an id the model chose.
    verdict = db.execute(
        "SELECT result, failed_criterion FROM verdicts WHERE batch_id='b1'").fetchone()
    assert verdict["result"] == "fail" and verdict["failed_criterion"] == "c1", \
        "a failing verdict must name the criterion"

    # Critic's trace touched criteria, tests and its own write — nothing else.
    calls = {r["fn"] for r in db.execute(
        "SELECT fn FROM tool_calls WHERE session_id = "
        "(SELECT id FROM sessions WHERE role='critic')")}
    assert calls <= {"criteria.load", "tests.load", "code.read",
                     "verdicts.claim_encodes", "verdicts.emit",
                     "msg.challenge_developer"}, calls


def test_arc_revocation_stops_the_batch(db):
    """Amending an approved item drops it to pending and stops its batches."""
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver, version) "
               "VALUES ('i1','x','in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','pending')")

    from rota.core.scheduler import tick_batch_start
    assert tick_batch_start(db), "approved item should schedule its batch"

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
               "VALUES ('m_ch','t1','architect','vision_keeper','challenge',1)")
    drive(db, Wake("vision_keeper", "message", "m_ch", detail="challenge"), [
        "TOOL: problem.assert(id='i1', text='x, but only for unverified accounts', kind='in_scope')",
    ])

    assert db.execute("SELECT approval FROM items WHERE id='i1'").fetchone()["approval"] == "draft"
    assert not tick_batch_start(db), "an amended item must stop its batches"


def test_arc_global_negative_no_undeclared_contacts(db):
    """
    Across a whole arc: zero messages between non-derived contacts.

    Asserted against the graph rather than a hand-written list, so the check
    cannot drift from the wiring.
    """
    test_arc_understanding_loop_reaches_approved_item(db)
    g = graph_mod.load()

    for r in db.execute("SELECT from_role, to_role, verb FROM messages WHERE from_role != 'principal'"):
        assert g.may_message(r["from_role"], r["to_role"], r["verb"]), \
            f"undeclared contact: {r['from_role']} -> {r['to_role']} ({r['verb']})"


def test_arc_global_negative_no_writes_by_non_owners(db):
    """Every receipt must belong to a role the graph says may write that artefact."""
    test_arc_delivery_loop_slices_batches_and_tests(db)

    from rota.core.db import ARTEFACT_OF_TABLE
    g = graph_mod.load()

    for r in db.execute(
        "SELECT s.role AS role, rc.table_name AS tbl FROM receipts rc "
        "JOIN sessions s ON s.id = rc.session_id"
    ):
        artefact = ARTEFACT_OF_TABLE.get(r["tbl"])
        assert artefact, f"receipt on unmapped table {r['tbl']}"
        assert r["role"] in g.writer_of(artefact), \
            f"{r['role']} wrote {artefact}, which it does not own"


def test_arc_quiescence_means_no_predicate_fires(db):
    """
    The universal invariant. Every residual-work bug — unsliced items,
    criteria-less tickets, deferred batches nobody resumed — violates this one
    assertion, which is worth more than most individual cases.
    """
    test_arc_delivery_loop_slices_batches_and_tests(db)

    # Drain the remaining message tips the way the loop would.
    for _ in range(20):
        tips = [w for w in frontier(db) if w.kind == "message"]
        if not tips:
            break
        db.execute("UPDATE messages SET status='answered' WHERE id=?", (tips[0].message_id,))

    remaining = predicate_wakes(db)
    # A batch that is still pending legitimately keeps two predicates firing:
    # it has not started, and it has no expected touch set yet. Both are real
    # residual work. Every *other* predicate must be silent.
    pending_batch = {"tick:batch_start", "tick:annotate"}
    unexpected = [w for w in remaining if w.kind not in pending_batch]
    assert not unexpected, f"work left undone at quiescence: {unexpected}"


def test_arc_global_invariants_hold_over_the_finished_database(db):
    """
    The whole-database checks in `validators`, asserted where a whole database
    exists.

    Five of these were never called from anywhere, and the question that looked
    obvious -- "what write causes this to run?" -- is the wrong shape for them.
    They take a connection and scan every row, so they are not per-write guards
    and could not be: at `surveys.attest` time the only survey that matters is
    the one being attested, and a global scan would fail on somebody else's bad
    row. The three that *are* live (`check_segmentation`,
    `check_statement_count`, `check_messages_carry_refs`) are called from a
    test, after a session, which is the idiom. These were simply never given
    one.

    So this is the enforcement point, and the arc is the right database for it:
    a full lifecycle through the real scheduler, sandbox, bus and commit path,
    with only the completions canned.
    """
    test_arc_delivery_loop_slices_batches_and_tests(db)

    # An invariant over an empty table passes and means nothing, which is the
    # failure this suite keeps finding elsewhere. So the rows are asserted
    # first: if the arc stops producing criteria, this test says so instead of
    # quietly going vacuous.
    populated = {t: db.execute(f"SELECT COUNT(*) n FROM {t}").fetchone()["n"]
                 for t in ("items", "tickets", "criteria", "glossary_terms")}
    assert all(populated.values()), f"nothing to check: {populated}"

    problems: list[str] = []
    problems += validators_mod.check_criteria_terms(db)
    # Law 13 has no other enforcement anywhere. Named tables rather than every
    # table, because the runtime bookkeeping is full of legitimate durations.
    problems += validators_mod.check_no_time_content(
        db, ["statements", "items", "tickets", "criteria", "glossary_terms",
             "constraints", "decisions"])

    assert not problems, "global invariants violated:\n  " + "\n  ".join(problems)


# `check_bindings_resolve` and `check_survey_citations` are deliberately absent
# above. This arc produces no constraint bindings and no survey records, so
# asserting them here would be two green checks over empty tables -- worse than
# no check, because it would read as covered. They belong wherever a survey has
# actually run; `test_onboarding` is the database that has those rows, and they
# now live there. `check_bindings_resolve` was wrong the whole time it had no
# home: it rejected every binding of constraint zero, which is the one
# constraint the system writes for itself.


def test_observed_becomes_decided_where_they_said_so(tmp_path):
    """
    Validation 3's sentence, driven whole: onboarding found things nobody
    chose, the principal rules on them, and the rows the ruling approves leave
    `observed` -- by their owners' hands, because provenance is the owner's to
    write.

    Until this arc could run, the machinery existed for items only. The ruling
    path ended at `problem.set_approval`; glossary terms, constraints and model
    areas were presented and the ruling had nowhere to land -- no relay channel
    to their owners, no operation anywhere that wrote `provenance='decided'`.
    And once a present was answered, `observed_entries` saw the same observed
    rows and fired again: a state with no exit, re-presented forever.

    Canned completions, real scheduler, real commit path -- the same division
    the module docstring draws.
    """
    import json as _json

    from rota.core.predicates import observed_entries

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1','recipe','a note that seeds another','observed')")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g2','intent','a note-creation config','observed')")
    db.execute("INSERT INTO constraints (id, headline, text, provenance) VALUES "
               "('k1','frontmatter must match the schema','validateFmSchema',"
               "'observed')")
    refs_from_columns(db)
    db.commit()

    # 1. The register offers the observations to Liaison, once.
    wakes = observed_entries(db)
    assert [w.role for w in wakes] == ["liaison"]

    out = run_session(
        db, wakes[0],
        backend=ScriptedBackend(
            ["TOOL: msg.present_principal(refs=['g1','g2','k1'])", "done"]),
        pins=Pins(model="stub", temperature=0.0), instructions="present them")
    assert out.committed, out.errors
    assert observed_entries(db) == [], "an open present suppresses the tick"

    # 2. The principal rules: two approved, one contested. Recorded the way
    #    `principal.py` records it -- the verdict message plus the config row.
    present = db.execute("SELECT id FROM messages WHERE verb='present'").fetchone()["id"]
    db.execute("INSERT INTO messages (id, cause_id, cause_kind, thread_id, "
               "from_role, to_role, verb, body_refs, seq, status) "
               "SELECT 'v1', ?, 'message', thread_id, 'principal', 'liaison', "
               "'verdict', body_refs, 90, 'open' FROM messages WHERE id = ?",
               (present, present))
    db.execute("INSERT INTO config (key, value) VALUES ('verdict:v1', ?)",
               (_json.dumps({"g1": "approve", "k1": "approve",
                             "g2": "contest"}),))
    db.execute("UPDATE messages SET status='answered' WHERE id = ?", (present,))
    # `principal.land` writes the ruling row the adopted rows will rest on.
    db.execute("INSERT INTO rulings (id, ask_id, verdict_id, status) "
               "VALUES ('r1', ?, 'v1', 'landed')", (present,))
    db.commit()

    # 3. Liaison relays the ruling, split by owner.
    out = run_session(
        db, Wake(role="liaison", kind="message", message_id="v1", detail="verdict"),
        backend=ScriptedBackend(
            ["TOOL: msg.relay_terminologist(refs=['g1','g2'])\n"
             "TOOL: msg.relay_architect(refs=['k1'])", "done"]),
        pins=Pins(model="stub", temperature=0.0),
        instructions=prompts_mod.compose("liaison", "verdict_signoff"))
    assert out.committed, out.errors

    # 4. Each owner adopts what the ruling approves. The op checks the ruling
    #    off the cause chain, so the contested sense cannot slip through even
    #    though the relay names it.
    for role, call in (
            ("terminologist", "TOOL: glossary.adopt(ids=['g1','g2'])"),
            ("architect", "TOOL: model.adopt(ids=['k1'])")):
        relay = db.execute(
            "SELECT id FROM messages WHERE verb='relay' AND to_role=? ",
            (role,)).fetchone()["id"]
        out = run_session(
            db, Wake(role=role, kind="message", message_id=relay, detail="relay"),
            backend=ScriptedBackend([call, "done"]),
            pins=Pins(model="stub", temperature=0.0),
            instructions=prompts_mod.compose(role, "relay"))
        assert out.committed, out.errors

    # The view: an adopted row rests on the ruling, a contested one on the
    # code it was found in.
    rows = {r["id"]: r["provenance"] for r in db.execute(
        "SELECT id, provenance FROM term_provenance "
        "UNION ALL SELECT id, provenance FROM constraint_provenance")}
    assert rows == {"g1": "decided", "k1": "decided", "g2": "observed"}, rows

    # 5. And the register does not re-present what has been put to them: the
    #    contested sense stays observed, on file, without waking anybody.
    assert observed_entries(db) == []
