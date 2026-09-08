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


def test_an_ask_reaches_the_owner_with_the_question_in_it(tmp_path):
    """
    The refs on an ask *are* the question, so they have to resolve.

    `msg.ask_*` carries no words -- law 2 -- and the entry id is the whole of
    how the principal's sentence reaches the owner. `_resolve_refs` had no
    `entries` row, so it resolved to nothing, and the owner woke holding a ref
    it could not follow. Entries were reachable only through `entry_for`, which
    looks up `e_{waking message id}`: true on the intake hop, where Liaison is
    woken by the message the entry belongs to, and false on every hop after it.

    Measured on the click database before this: Architect was woken by `m6` for
    entry `e_m5`, saw `refs: ["e_m5"]` and no question, and answered with a
    description of a three-layer architecture that click does not have.
    Answering from memory is what a role does when handed nothing, and from the
    outside it is indistinguishable from answering from the artefact.

    The message ids are deliberately unequal here. They were equal in the first
    fixture written for this and the bug hid behind that.
    """
    import json

    from rota.core.db import init_db
    from rota.core.predicates import Wake
    from rota.core.runner import resolve_inbound

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m5','principal','where does a user write a recipe?',1)")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('m6','t1','liaison','architect','ask',?,1)",
               (json.dumps(["e_m5"]),))
    db.commit()

    out = resolve_inbound(db, Wake(role="architect", kind="message",
                                   message_id="m6", detail="ask"))
    assert out["principal_said"] == "where does a user write a recipe?"
    assert out["entry_id"] == "e_m5"
    assert out["resolved_refs"]["e_m5"]["author"] == "principal"


def test_a_tick_woken_rung_replies_to_the_question_it_was_woken_for(tmp_path):
    """
    The `unresolved` ladder wakes a rung with a *tick*, not a message, and the
    question rides in `refs`. `ctx.trigger` was `wake.message_id` and nothing
    else, so every message that rung sent came out with no cause -- and the
    chain broke exactly where the register needs it. `schedule.reask` finds the
    question by following the answer's cause; with no cause it refuses ("the
    message that woke you is not a reply to a question you asked"), so the
    asker cannot say the second answer missed either and the ladder loops on
    one rung until quarantine.

    Measured on the click run twice: Vision Keeper, then Terminologist, each
    answering three times into a thread nobody could advance.

    Narrow on purpose -- only a ref that resolves to a message counts, and
    every other tick carries artefact ids.
    """
    import json

    from rota.core.db import init_db
    from rota.core.predicates import Wake
    from rota.core.runner import run_session
    from rota.llm.llm import Pins, ScriptedBackend

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m1','principal','what is a recipe here?',1)")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1','recipe','a note that seeds another','observed')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m6','t1','liaison','architect',"
               "'ask',?,1,'unresolved')", (json.dumps(["e_m1"]),))
    db.commit()

    out = run_session(
        db, Wake("terminologist", "tick:unresolved", refs=("m6",)),
        backend=ScriptedBackend(["TOOL: msg.answer_liaison(refs=['g1'])", "done"]),
        pins=Pins(model="stub", temperature=0.0),
        instructions="answer it")
    assert out.committed, out.errors

    row = db.execute("SELECT cause_id, thread_id FROM messages "
                     "WHERE from_role = 'terminologist'").fetchone()
    assert row["cause_id"] == "m6", "the rung's answer must name the question"
    assert row["thread_id"] == "t1", "and stay in the thread it was woken for"


def test_a_tick_carrying_artefact_ids_gains_no_cause(tmp_path):
    """
    The bound. Every other tick carries artefact ids in `refs`, and a session
    woken by one is not replying to anything -- giving it a cause would invent
    a conversation that did not happen.
    """
    from rota.core.db import init_db
    from rota.core.predicates import Wake
    from rota.core.runner import run_session
    from rota.llm.llm import Pins, ScriptedBackend

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('i1','close an account',"
               "'in_scope','decided','approved',1,1)")
    db.commit()

    out = run_session(
        db, Wake("vision_keeper", "tick:slicing", refs=("i1",)),
        backend=ScriptedBackend(["done"]),
        pins=Pins(model="stub", temperature=0.0), instructions="do nothing")
    assert out.committed, out.errors
    assert db.execute(
        "SELECT COUNT(*) n FROM messages").fetchone()["n"] == 0


def test_a_tick_woken_rung_is_shown_the_question(tmp_path):
    """
    The other half of the same fault: the rung could not *read* what it was
    woken to answer.

    `resolve_inbound` returned `{}` for any wake with no `message_id`, so a rung
    on the `unresolved` ladder saw the message id in `refs` and nothing else --
    no `principal_said`, no resolved rows, no text. Measured on the click run:
    Terminologist and Vision Keeper each answered with `refs: ["m6"]`, the id of
    the question itself, because it was the only thing in front of them. An
    answer naming a message names nothing the asker can relay, and Liaison
    rightly refused to put it in front of the principal.

    Same `trigger_message` the outbound cause uses, so the prompt and the
    causal chain cannot disagree about what this session is replying to.
    """
    import json

    from rota.core.db import init_db
    from rota.core.predicates import Wake
    from rota.core.runner import resolve_inbound

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m5','principal','where does a user write a recipe?',1)")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m6','t1','liaison','architect',"
               "'ask',?,1,'unresolved')", (json.dumps(["e_m5"]),))
    db.commit()

    out = resolve_inbound(db, Wake("terminologist", "tick:unresolved",
                                   refs=("m6",)))
    assert out["principal_said"] == "where does a user write a recipe?"
    assert out["from"] == "liaison" and out["verb"] == "ask"
    assert out["refs"] == ["e_m5"], "the question's refs, not the question's id"


def test_a_tick_carrying_artefact_ids_resolves_to_nothing(tmp_path):
    """The bound, on the prompt side: a survey tick is not replying to anyone."""
    from rota.core.db import init_db
    from rota.core.predicates import Wake
    from rota.core.runner import resolve_inbound

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('i1','close an account',"
               "'in_scope','decided','approved',1,1)")
    db.commit()
    assert resolve_inbound(db, Wake("vision_keeper", "tick:slicing",
                                    refs=("i1",))) == {}


def test_the_question_matched_push_needs_both_glossary_reads(tmp_path):
    """
    The bodies are looked up by term and the terms are enumerated from the
    index, so a mode holding one read and not the other cannot do it.

    Architect's `unresolved` mode has `glossary.lookup` and no
    `glossary.consult`. Enumerating unguarded raised `NotInWorkingSet` -- which
    is raised rather than returned, and the push runs before the model sees
    anything, so the whole session died before its first turn.
    `L1-AR-a-dead-answer-is-a-question-about-the-model` went from green to 0/5,
    with the failure reported as "none of the permitted answers was given".
    """
    import json

    from rota.core.db import init_db
    from rota.core.predicates import Wake
    from rota.core.sandbox import build
    from rota.core.runner import push_working_set
    from rota.design import graph as graph_mod
    from rota.roles import prompts

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m1','principal','what is a template here?',1)")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, sense_body, "
               "provenance) VALUES ('g1','template','a seed note','the body',"
               "'observed')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('m1','t1','developer','architect',"
               "'question',?,1)", (json.dumps([]),))
    db.commit()

    g = graph_mod.load()
    wake = Wake("architect", "tick:unresolved", refs=("m1",))
    sb = build("architect", db, mode="normal", session_id="s1", g=g,
               allow=prompts.mode_tools("architect", "unresolved"), wake=wake)
    assert "glossary.lookup" in sb.functions()
    assert "glossary.consult" not in sb.functions()

    # The point: this must return rather than raise.
    pushed = push_working_set("architect", sb, wake, g,
                              asked="what is a template here?")
    # `glossary.lookup` is still pushed by the no-argument rule -- as the miss
    # for the empty term, which is what it has always been here. What must not
    # happen is the question-matched form, which is keyed by term and needs the
    # index this mode cannot read.
    assert "template" not in (pushed.get("glossary.lookup") or {})


def test_a_resolved_ref_carries_the_body_not_a_summary(tmp_path):
    """
    A ref is a pointer to the thing, and `_resolve_refs` exists to follow it.

    `tests` has carried its body since a Tester was woken to defend a test it
    was never shown -- "resolving a pointer to everything except the thing is
    what this function is for". The two artefacts the inquiry route runs on
    were still resolving to a summary: `glossary_terms` without `sense_body`,
    `constraints` without `text`.

    That is where the answers were being lost. The owner reads the full sense,
    refs the term, and Liaison -- which writes the words the principal actually
    reads -- was handed one line. Measured on the eight maintainer questions:
    every reply came out as a string of one-line definitions, because that is
    all that survived the hop.
    """
    import json

    from rota.core.db import init_db
    from rota.core.predicates import Wake
    from rota.core.runner import resolve_inbound

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, sense_body, "
               "provenance) VALUES ('g1','template','a seed note',"
               "'a note whose contents seed the new note, named by an intent',"
               "'observed')")
    db.execute("INSERT INTO constraints (id, headline, text, provenance) VALUES "
               "('k1','the vault is the store',"
               "'every note lives in the user vault and nowhere else','observed')")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('m1','t1','terminologist','liaison',"
               "'answer',?,1)", (json.dumps(["g1", "k1"]),))
    db.commit()

    out = resolve_inbound(db, Wake("liaison", "message", message_id="m1",
                                   detail="answer"))
    assert "seed the new note" in out["resolved_refs"]["g1"]["sense_body"]
    assert "nowhere else" in out["resolved_refs"]["k1"]["text"]


def test_a_relay_carries_the_principal_ruling_from_its_cause(tmp_path):
    """
    The ruling travels on the cause chain, and for one owner it did not arrive.

    A principal's verdict is keyed to the message they answered (principal ->
    liaison), but the owner who must act on it is woken by a different message:
    Liaison's relay, whose cause is that verdict. `verdict_for` and `entry_for`
    looked up the trigger alone, so the relay carried no ruling and no reason.
    Measured on the tips run: the principal contested "service quality" on t1,
    Vision Keeper was shown t1 at draft and nothing else, set it approved, and
    the build shipped the contested thing.

    One hop, relay only, and only the rows this relay carries -- a ruling fans
    out one relay per owner, and each owner sees its own subset.
    """
    import json

    from rota.core.db import init_db
    from rota.core.predicates import Wake
    from rota.core.runner import resolve_inbound

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m10','principal','no service quality. just bill + tip %',1)")
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('t1',"
               "'Calculate tips based on bill amount and service quality',"
               "'in_scope','decided','draft',0,1)")
    db.execute("INSERT INTO config (key, value) VALUES ('verdict:m10', ?)",
               (json.dumps({"t1": "contest", "s1": "approve"}),))
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('m10','th','principal','liaison',"
               "'verdict',?,1)", (json.dumps(["t1", "s1"]),))
    # The owner's relay: cause is the verdict, refs are only the rows it holds.
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, cause_id) VALUES ('m11','th','liaison',"
               "'vision_keeper','relay',?,2,'m10')", (json.dumps(["t1"]),))
    # A second owner's relay for a row the ruling never named: nothing to carry.
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, cause_id) VALUES ('m12','th','liaison',"
               "'architect','relay',?,3,'m10')", (json.dumps(["k0"]),))
    db.commit()

    out = resolve_inbound(db, Wake(role="vision_keeper", kind="message",
                                   message_id="m11", detail="relay"))
    assert out["verb"] == "relay"
    assert out["principal_verdict"] == {"t1": "contest"}, (
        "the owner sees its own rows' ruling, not the whole fan-out")
    assert out["principal_said"] == "no service quality. just bill + tip %"

    other = resolve_inbound(db, Wake(role="architect", kind="message",
                                     message_id="m12", detail="relay"))
    assert "principal_verdict" not in other
    assert "principal_said" not in other


def test_a_contested_tick_carries_the_reason_it_was_contested_for(tmp_path):
    """
    A contested item wakes its owner by tick, and the tick carried the item id
    and nothing else. The owner's brief says `transcript.quote` for what they
    actually said -- and the owner had no way to know where that was: it saw
    the verdict in the relay session, and sessions have no memory. Measured on
    the tips run: woken cold, Vision Keeper quoted `entry_id="t1"`, the item id,
    read nothing, and reported it could not tell what was objected to. Liaison
    asked the principal what they had already said; the tick fired again; the
    same question came back verbatim.

    The latest verdict that contested the item is the one that stands, and its
    entry is the reason. An item nothing contested resolves to nothing.
    """
    import json

    from rota.core.db import init_db
    from rota.core.predicates import Wake
    from rota.core.runner import resolve_inbound

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('t1',"
               "'Calculate tips based on bill amount and service quality',"
               "'in_scope','decided','contested',0,1)")
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('t2','unrelated',"
               "'in_scope','decided','contested',0,1)")
    # An earlier contest, then the item was amended, re-presented, contested
    # again with a different reason. The later one is the one that stands.
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m10','principal','old reason',1)")
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m20','principal','no service quality. just bill + tip %',2)")
    db.execute("INSERT INTO config (key, value) VALUES ('verdict:m10', ?)",
               (json.dumps({"t1": "contest"}),))
    db.execute("INSERT INTO config (key, value) VALUES ('verdict:m20', ?)",
               (json.dumps({"t1": "contest", "s1": "approve"}),))
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('m10','th','principal','liaison',"
               "'verdict',?,1)", (json.dumps(["t1"]),))
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq) VALUES ('m20','th','principal','liaison',"
               "'verdict',?,2)", (json.dumps(["t1", "s1"]),))
    db.commit()

    out = resolve_inbound(db, Wake("vision_keeper", "tick:contested",
                                   refs=("t1",)))
    assert out["principal_verdict"] == {"t1": "contest"}
    assert out["principal_said"] == "no service quality. just bill + tip %", (
        "the latest contest's reason, not the first")
    assert out["entry_id"] == "e_m20"
    assert out["resolved_refs"]["t1"]["approval"] == "contested"

    # Contested in the table but no verdict ever named it: nothing to carry.
    assert resolve_inbound(db, Wake("vision_keeper", "tick:contested",
                                    refs=("t2",))) == {}


def test_a_reply_to_a_clarify_says_who_asked_and_about_what(tmp_path):
    """
    A principal converse whose cause is a clarify is a reply. Liaison was shown
    the words and nothing about the question, so it segmented them as new work
    (tips5). `answering` carries who asked, what, and which rows.

    Two shapes. A desk's report caused the clarify: the desk and its refs. Or
    Liaison asked on its own, with no cause: then the clarify's own refs are
    what the reply is about (tipsF, 2026-09-08: two such replies re-entered as
    fresh requests because nothing here named a row).
    """
    import json

    from rota.core.db import init_db
    from rota.core.predicates import Wake
    from rota.core.runner import resolve_inbound

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m3','principal','both, show the tip and the total',1)")
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m6','principal','yes, that is right',2)")
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver, "
               "version) VALUES ('how_it_works','the account','in_scope','decided','draft',0,1)")
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, status, "
               "author) VALUES ('l_1','how_it_works','items','typed each time','open','vision_keeper')")
    m = ("INSERT INTO messages (id, thread_id, from_role, to_role, verb, body_refs, "
         "body_text, cause_id, seq) VALUES (?,?,?,?,?,?,?,?,?)")
    # Shape one: the Tester reported, Liaison clarified, the principal replied.
    db.execute(m, ("m1", "th", "tester", "liaison", "report", json.dumps(["c_1"]), None, None, 1))
    db.execute(m, ("m2", "th", "liaison", "principal", "clarify", json.dumps(["c_1"]),
                   "What should the tests exercise?", "m1", 2))
    db.execute(m, ("m3", "th", "principal", "liaison", "converse", json.dumps(["c_1"]), None, "m2", 3))
    # Shape two: Liaison asked on its own about an assumption; no cause.
    db.execute(m, ("m5", "th", "liaison", "principal", "clarify", json.dumps(["l_1"]),
                   "Is the assumption right?", None, 5))
    db.execute(m, ("m6", "th", "principal", "liaison", "converse", json.dumps(["l_1"]), None, "m5", 6))
    db.commit()

    one = resolve_inbound(db, Wake("liaison", "message", message_id="m3", detail="converse"))
    assert one["answering"] == {"question": "What should the tests exercise?",
                                "asked_by": "tester", "about": ["c_1"]}
    two = resolve_inbound(db, Wake("liaison", "message", message_id="m6", detail="converse"))
    assert two["answering"] == {"question": "Is the assumption right?",
                                "asked_by": "liaison", "about": ["l_1"]}


def test_a_report_about_rows_the_principal_already_answered_carries_the_answers(tmp_path):
    """
    A report about a row the principal has answered once is not a new question.
    On the tipsG walk (2026-09-09) one collision was reported eight times, each
    report became a clarify, and the principal gave the same answer eight
    times. The answers were on file; the harvest could not see them.
    `prior_answers` carries each earlier question and the principal's words,
    for the rows the report names.
    """
    import json

    from rota.core.db import init_db
    from rota.core.predicates import Wake
    from rota.core.runner import resolve_inbound

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) VALUES "
               "('g1','total','the bill before the tip','decided')")
    db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
               "('e_m3','principal','total means the bill plus the tip',1)")
    m = ("INSERT INTO messages (id, thread_id, from_role, to_role, verb, body_refs, "
         "body_text, cause_id, seq) VALUES (?,?,?,?,?,?,?,?,?)")
    db.execute(m, ("m1", "th", "terminologist", "liaison", "report", json.dumps(["g1"]), None, None, 1))
    db.execute(m, ("m2", "th", "liaison", "principal", "clarify", json.dumps(["g1"]),
                   "Does total include the tip?", "m1", 2))
    db.execute(m, ("m3", "th", "principal", "liaison", "converse", json.dumps(["g1"]), None, "m2", 3))
    # The same collision, reported again.
    db.execute(m, ("m4", "th", "terminologist", "liaison", "report", json.dumps(["g1"]), None, None, 4))
    # A report about a different row carries nothing.
    db.execute(m, ("m5", "th", "architect", "liaison", "report", json.dumps(["k9"]), None, None, 5))
    db.commit()

    again = resolve_inbound(db, Wake("liaison", "message", message_id="m4", detail="report"))
    assert again["prior_answers"] == [{"question": "Does total include the tip?",
                                       "principal_said": "total means the bill plus the tip",
                                       "about": ["g1"]}]
    other = resolve_inbound(db, Wake("liaison", "message", message_id="m5", detail="report"))
    assert "prior_answers" not in other
