"""
A document is load-bearing when something checks it. Everything else is prose.

This repository's most expensive recurring lesson is that prose does not
arbitrate: a rule written down and not enforced is a rule the system is free to
break, and six measured attempts have not moved a case by rewording it. The
corollary nobody applied to the documents themselves is that an unchecked
document is not a weaker version of a check. It is sediment, and it accumulates
faster than anybody reads it -- thirty thousand words at the point this was
written, of which a fifth was doing work.

So the set is pinned the same way the predicate classification is pinned: a new
document must be checked, read by code, or declared narrative with a reason.
There is no fourth option and no way to add one quietly.
"""
from __future__ import annotations

from pathlib import Path

from rota import paths
from rota.design import graph as graph_mod


# Narrative, deliberately: read by people, enforced by nothing, and each one
# says why it earns the exception.
NARRATIVE = {
    "README.md": "the way in; a reader who needs a test to trust it is lost already",
    "LAWS.md": "the constraints in prose. Each with a structural consequence is "
               "asserted in test_laws.py; this is where they are argued",
    "SYSTEM.md": "the derivation, and the open design gaps. Its factual claims "
                 "about the graph are asserted below",
    "DECISIONS.md": "rulings and their consequences, so a settled question is "
                    "not re-argued from scratch",
    "HARDWARE_GUIDE.md": "operational, and dated -- a snapshot of what runs on "
                         "the target box rather than a claim about the system",
    "TOOLCALLING.md": "a measurement result. Evidence keeps its value without "
                      "anything asserting it",
    "ANSWER_KEY.md": "grading data for onboarding runs, written before the "
                     "first session ran",
    "ANSWER_KEY_icalendar.md": "the same, for the second repository",
}

# Checked by a test, or read by code at runtime.
LOAD_BEARING = {
    "ROLES.md": "test_roles_doc.py",
    "REGISTER.md": "test_roles_doc.py, predicate classification",
    "MILESTONE.md": "cockpit/progress.py reads it at runtime",
}


def test_every_document_is_checked_or_declared_narrative():
    """
    The lint. A document that is neither is one nobody has decided about, which
    is how fifteen files became thirty thousand words.
    """
    present = {p.name for p in paths.PACKAGE.glob("*.md")}
    accounted = set(NARRATIVE) | set(LOAD_BEARING)

    unaccounted = sorted(present - accounted)
    assert not unaccounted, (
        f"{unaccounted} is neither checked nor declared narrative. Give it a "
        f"test, have code read it, or add it to NARRATIVE with the reason it "
        f"earns an exception")

    missing = sorted(accounted - present)
    assert not missing, f"{missing} is declared here and does not exist"


# ---------------------------------------------------------------------------
# SYSTEM.md's claims about the graph, as assertions.
#
# The document names gaps. A gap that gets fixed while the document still claims
# it is a reader misled by something that was true when written -- so each claim
# fails here the moment it stops being true, and the document has to be updated
# to make the suite green again.
# ---------------------------------------------------------------------------

def test_critic_still_cannot_ask_anything():
    """SYSTEM.md gap 2. Critic is starved of the model on purpose and cannot
    ask a question either, which was not the intent. Fix the gap and this test
    fails, which is the point: the document must stop claiming it."""
    g = graph_mod.load()
    verbs = {e.v for e in g.of_type("messages") if e.s == "critic"}
    assert verbs == {"challenge"}, (
        f"Critic's vocabulary is now {sorted(verbs)}. If it can ask, "
        f"SYSTEM.md gap 2 is closed and must say so")


def test_one_question_channel_still_has_no_reply_edge():
    """SYSTEM.md gap 3. Every question channel but one can be answered."""
    g = graph_mod.load()
    asks = {(e.s, e.t) for e in g.of_type("messages") if e.v == "question"}
    answers = {(e.s, e.t) for e in g.of_type("messages") if e.v == "answer"}
    mute = {(s, t) for s, t in asks if (t, s) not in answers}
    assert mute == {("architect", "terminologist")}, (
        f"the unanswerable question channels are now {sorted(mute)}; "
        f"SYSTEM.md names exactly one")


def test_the_toolkit_narrows_to_the_role_that_asked(tmp_path):
    """
    SYSTEM.md gap 1, closed. This was a staleness check asserting the gap was
    still open, and it went red the moment the gap was fixed, which is what it
    was for. Replaced by the behaviour it now guarantees.

    Gatekeeper can answer Developer and Tester, so `unresolved` mode carries
    both channels. Woken to a thread between Tester and Terminologist it
    answered Developer five runs out of five. Developer is not in the thread.
    The asker is on the wake, so the other channel is not a temptation to
    resist; it is a capability with no situation.
    """
    from rota.core.db import init_db
    from rota.core.predicates import Wake
    from rota.core.sandbox import build

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
               "verb, body_refs, body_text, seq, status) VALUES "
               "('m1','t1','tester','terminologist','question','[]','?',1,"
               "'unresolved')")

    allow = ["msg.answer_developer", "msg.answer_tester", "msg.submit_liaison"]
    wake = Wake("gatekeeper", "tick:unresolved", refs=("m1",))

    wide = build("gatekeeper", db, mode="normal", allow=allow)
    assert "msg.answer_developer" in wide.functions()

    narrow = build("gatekeeper", db, mode="normal", allow=allow, wake=wake)
    assert "msg.answer_tester" in narrow.functions(), "the asker must be reachable"
    assert "msg.answer_developer" not in narrow.functions(), \
        "Developer is not in this thread and did not ask"
    assert "msg.submit_liaison" in narrow.functions(), \
        "narrowing the answer channel must not close the way upward"
