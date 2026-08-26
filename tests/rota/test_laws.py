"""
The law amendments, as checks.

Each of these was a sentence in a design document that the code either agreed
with or quietly did not. A law that only exists in prose is a law the system is
free to break, so the ones with a structural consequence are asserted here.
"""
from __future__ import annotations

import pytest

from rota.design import graph as graph_mod
from rota.core.db import init_db
from rota.core.sandbox import build


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


@pytest.fixture
def g():
    return graph_mod.load()


# ---------------------------------------------------------------------------
# Law 1 — priority is a property of the item
# ---------------------------------------------------------------------------

def test_batches_have_exactly_one_writer(g):
    """
    Vision Keeper wrote priority onto batches, so batches had two writers and law 1
    held only in the weaker per-row reading. Moving priority to the item — which
    is what the principal actually ordered — makes the strong reading true.
    """
    assert g.writer_of("batches") == {"architect"}


def test_priority_lives_on_the_item(db):
    cols = {r[1] for r in db.execute("PRAGMA table_info(items)")}
    assert "priority" in cols
    cols = {r[1] for r in db.execute("PRAGMA table_info(batches)")}
    assert "priority" not in cols, "two priorities can disagree; one cannot"


def test_prioritizing_is_not_an_amendment(db):
    """
    Law 9: priority alters no approved content, so it must not trip revocation.
    `amends=False` is what makes that structural rather than a promise.
    """
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) "
               "VALUES ('i1','x','in_scope','decided','approved',1,1)")
    sb = build("vision_keeper", db)
    sb.call("problem.prioritize", id="i1", priority=5)

    write = sb.ctx.writes[-1]
    assert write[0] == "items"
    assert write[3] is False, "priority bumped the version and revoked the approval"


# ---------------------------------------------------------------------------
# Law 3 — contact lists are derived, with nothing left over
# ---------------------------------------------------------------------------

def test_law_3_now_derives_every_message_edge(g):
    """
    `architect -> critic: finding` was the system's only declared exception, and
    it was underivable by construction: Critic must not read the model, so the
    conclusion had to be *pushed* to it. Flipping the review order makes
    Architect's judgement a gate rather than an input, so it has nobody to tell.
    """
    assert g.contact_exceptions == []
    assert graph_mod.check_contacts(g) == []


def test_critic_is_still_starved(g):
    """The whole reason the exception existed. Removing it must not have been
    achieved by giving Critic the model."""
    assert "model" not in g.read_set("critic")
    assert "decisions" not in g.read_set("critic")
    assert "transcript" not in g.read_set("critic")


def test_findings_are_rows_not_messages(db, g):
    """
    Architect's structural verdict lands on its own artefact. The merge
    predicate reads it, and the scheduler is not a role — so nothing about
    Critic's starvation had to be relaxed.
    """
    assert "finding" not in g.message_verbs()
    cols = {r[1] for r in db.execute("PRAGMA table_info(findings)")}
    assert {"constraint_id", "status", "grain"} <= cols


def test_a_finding_carries_no_reasoning(db):
    """Law 2: conclusions travel, reasoning stays home. There is no `why`."""
    cols = {r[1] for r in db.execute("PRAGMA table_info(findings)")}
    assert not (cols & {"why", "reason", "rationale", "text", "notes"})


# ---------------------------------------------------------------------------
# The touch set — a prediction, not a permission
# ---------------------------------------------------------------------------

def test_architect_can_record_what_a_batch_should_touch(db):
    db.execute("INSERT INTO items (id, text, kind, provenance) "
               "VALUES ('i1','x','in_scope','decided')")
    db.execute("INSERT INTO batches (id, item_id) VALUES ('b1','i1')")

    sb = build("architect", db)
    out = sb.call("batches.annotate", batch_id="b1",
                  paths=["src/auth.py"], symbols=["login"])
    assert out["grains"] == 2

    kinds = {w[2]["grain_kind"]: w[2]["confidence"] for w in sb.ctx.writes}
    assert kinds == {"path": "expected", "symbol": "possible"}, \
        "symbols are the uncertain half; the confidence must say so"


def test_the_touch_set_gates_nothing(db):
    """
    A prediction that could block work would quietly become a permission system
    nobody designed. Committing a change to a grain outside the set must be an
    ordinary commit, not a refusal.
    """
    from rota.core.db import SessionResult, Write, session_commit

    db.execute("INSERT INTO items (id, text, kind, provenance) "
               "VALUES ('i1','x','in_scope','decided')")
    db.execute("INSERT INTO batches (id, item_id) VALUES ('b1','i1')")
    db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) "
               "VALUES ('b1','src/auth.py','path')")

    session_commit(db, SessionResult(
        session_id="s1", role="terminologist",
        writes=[Write("glossary_terms", "g1", {
            "term": "session", "sense_short": "a login",
            "provenance": "decided"})]))

    assert db.execute(
        "SELECT COUNT(*) n FROM glossary_terms").fetchone()["n"] == 1


# ---------------------------------------------------------------------------
# The ledger resolves by decision, never by itself
# ---------------------------------------------------------------------------

def test_there_is_no_way_to_resolve_a_ledger_entry_directly(db):
    sb = build("developer", db)
    assert not [f for f in sb.functions() if f.startswith("ledger.resolve")]


def test_a_decision_resolves_its_ledger_entry_in_the_same_commit(db):
    """
    Self-resolution would void "no milestone with open assumptions", which is
    the only thing making the ledger more than a list of regrets.
    """
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, author) "
               "VALUES ('l1','i1','items','assumed soft delete','developer')")

    sb = build("vision_keeper", db)
    sb.call("decisions.author", id="d1", text="soft delete it is",
            resolves_ledger="l1")

    tables = {w[0]: w for w in sb.ctx.writes}
    assert "ledger" in tables, "the decision did not close the entry it claimed to"
    assert tables["ledger"][2] == {"status": "resolved"}
    assert tables["ledger"][3] is False, "resolving is not an amendment"


def test_a_decision_without_a_ledger_ref_touches_no_ledger(db):
    sb = build("vision_keeper", db)
    sb.call("decisions.author", id="d1", text="just a decision")
    assert {w[0] for w in sb.ctx.writes} == {"decisions"}


# ---------------------------------------------------------------------------
# P3 — owners read what they own
# ---------------------------------------------------------------------------

def test_owners_can_read_what_they_own(g):
    """
    Four roles could write an artefact and not read it. Liaison could not quote
    the transcript it owns — while three roles that never speak to the principal
    could — nor read the brief it segments; Architect could not search the
    decision record it writes to.

    Critic not reading its own verdicts is the one deliberate case: a judge that
    remembers its prior objection is anchored, and cold re-judgement is the
    property worth having.
    """
    DELIBERATE = {("critic", "verdicts")}

    blind = {(w, a) for a in g.artefacts for w in g.writer_of(a)
             if a not in g.read_set(w)} - DELIBERATE
    # Ledger writers read nothing; `ledger.log` derives its id instead, so a
    # repeat is an upsert and there is nothing to check for first.
    blind -= {(w, "ledger") for w in g.writer_of("ledger")}
    # `schedule.reask` is the same case for the same reason: the row it
    # writes is the question this session's own trigger replies to, derived from
    # the causal chain rather than chosen. A role cannot name the wrong one, so
    # there is nothing it would read the schedule to find out. Reading it would
    # also be the wrong grant -- the frontier is the scheduler's, and a role that
    # could see what it is about to be offered could work to be offered it.
    blind -= {(w, "schedule") for w in g.writer_of("schedule")}
    assert not blind, sorted(blind)


# ---------------------------------------------------------------------------
# 1.7 — the rulings
# ---------------------------------------------------------------------------

def test_everyone_who_can_assume_can_log_it(g):
    """
    Terminologist picking one sense of a colliding term, and Tester deciding
    what an untestable criterion must have meant, are assumptions in exactly law
    11's sense. They were the only two makers of that choice who could not
    record it.
    """
    assert {"terminologist", "tester"} <= g.writer_of("ledger")


def test_everyone_who_writes_decided_can_author_the_reason(g):
    """
    Law 11: a `decided` entry has its reason on file, written by the decider in
    the same session. Terminologist marks glossary rows `decided` and could not
    write the reason that makes them so.
    """
    for role, artefact in (("terminologist", "glossary"),
                           ("architect", "model"),
                           ("vision_keeper", "problem")):
        assert artefact in g.write_set(role)
        assert "decisions" in g.write_set(role), \
            f"{role} writes `decided` rows into {artefact} and cannot say why"


def test_logging_the_same_assumption_twice_is_one_entry(db):
    """
    No writer can read the ledger, so a cold session retrying the same gap has
    no way to know it already logged this. A milestone is quiescence with an
    *empty* ledger, so duplicates make the principal resolve one assumption
    three times.
    """
    first = build("developer", db).call(
        "ledger.log", about_ref="i1", about_table="items",
        default_taken="assumed soft delete")
    again = build("terminologist", db).call(
        "ledger.log", about_ref="i1", about_table="items",
        default_taken="assumed soft delete")

    assert first["id"] == again["id"], \
        "the same assumption reached twice must be one entry"

    different = build("developer", db).call(
        "ledger.log", about_ref="i1", about_table="items",
        default_taken="assumed hard delete")
    assert different["id"] != first["id"]


# ---------------------------------------------------------------------------
# A question that cannot be answered
# ---------------------------------------------------------------------------

ASKING_VERBS = {"question", "ask", "challenge", "escalate", "deliver", "propose"}


def test_every_question_can_be_answered(g):
    """
    An edge that only goes one way is a role talking into a wall.

    Law 3 derives who may message whom, and it is symmetric in the sense that
    matters -- if you may ask the writer of an artefact you read, that writer
    reads something of yours or you would not have been given the question. It
    says nothing about the *verbs*, and the verbs are drawn by hand.

    So `architect -> terminologist: question` was drawn and
    `terminologist -> architect: answer` was not. Architect could ask about a
    sense and the reply had nowhere to go: the Terminologist session would be
    woken by the question, would find no function to answer with, and the
    escalation ladder would eventually abandon the message. Every other
    question in the system pairs -- developer, tester and researcher all have
    theirs -- which is what made the single missing one invisible.

    The mirror does not hold: an `answer` without a `question` is normal,
    because `ask`, `deliver`, `challenge` and `escalate` are all answerable
    too. Only the unanswerable question is a fault.
    """
    questions = {(e.s, e.t) for e in g.edges
                 if e.type == "messages" and e.v == "question"}
    answers = {(e.s, e.t) for e in g.edges
               if e.type == "messages" and e.v == "answer"}

    deaf = sorted(f"{s} -> {t} asks, {t} cannot answer"
                  for s, t in questions if (t, s) not in answers)
    assert not deaf, deaf


def test_every_answer_replies_to_something(g):
    """
    The other half, stated so the pairing rule cannot be satisfied by drawing
    answers nobody asked for. An `answer` edge needs an inbound verb that opens
    something: `question`, `ask`, `challenge`, `escalate`, `deliver`, `propose`.
    """
    inbound: dict[tuple[str, str], set[str]] = {}
    for e in g.edges:
        if e.type == "messages":
            inbound.setdefault((e.s, e.t), set()).add(e.v)

    orphans = sorted(
        f"{s} -> {t} answers nothing {t} can send"
        for (s, t), verbs in inbound.items()
        if "answer" in verbs and not (inbound.get((t, s), set()) & ASKING_VERBS))
    assert not orphans, orphans


# ---------------------------------------------------------------------------
# Law 10 -- inquiry is free
# ---------------------------------------------------------------------------

def test_an_ask_wakes_a_session_that_cannot_write(g):
    """
    The law's guarantee is structural: a readonly sandbox is built without
    writers, so a model reaching for one gets an ordinary tool error rather
    than a refusal at commit time. Nothing derived the mode, so no session the
    loop ever dispatched was readonly -- `loop.run` takes the `run_session`
    default and the default was `"normal"`.

    Asserted on the wake rather than on the sandbox, because the sandbox was
    never the part that was wrong.
    """
    from rota.core.predicates import Wake
    from rota.core.runner import session_mode

    for edge in g.of_type("messages"):
        if edge.v != "ask":
            continue
        wake = Wake(role=edge.t, kind="message", message_id="m1", detail="ask")
        assert session_mode(wake) == "readonly", f"{edge.s} -> {edge.t}"


def test_a_readonly_owner_is_built_with_no_writers(db, g):
    """
    The other half, on the sandbox itself: the three owners an inquiry reaches
    hold no write function at all in the mode the ask puts them in.

    `ask.tools` narrows each of them to reads already, which is why the missing
    derivation was invisible -- the law held because three hand-maintained
    lists agreed with it. This asserts it without them.
    """
    for role in ("vision_keeper", "terminologist", "architect"):
        sb = build(role, db, mode="readonly", g=g)
        writes = {f"{e.t}.{e.v}" for e in g.edges
                  if e.s == role and e.type == "writes" and e.model_callable}
        assert writes, f"{role} writes nothing even in normal mode"
        assert not (set(sb.functions()) & writes), sb.functions()


def test_an_answer_is_not_read_only(g):
    """
    The verb names the conversation, not the permission. A Developer woken by
    a Terminologist's answer writes code with it, so `answer` is deliberately
    outside `READONLY_VERBS` even though it is the reply half of the route
    whose asking half is inside it.
    """
    from rota.core.predicates import Wake
    from rota.core.runner import session_mode

    wake = Wake(role="developer", kind="message", message_id="m1", detail="answer")
    assert session_mode(wake) == "normal"
