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
    "ENVIRONMENT.md": "the 3Bd proposal; its claims about what exists are "
                      "asserted below and go red when the stage is built",
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


def test_no_question_channel_is_unanswerable():
    """
    SYSTEM.md gap 3, closed. This asserted the gap was still open — one
    unanswerable channel, `architect → terminologist` — and went red the moment
    it was drawn, which is what it was for. It now asserts the property instead
    of the hole, and `test_laws.py` carries the general form.
    """
    g = graph_mod.load()
    asks = {(e.s, e.t) for e in g.of_type("messages") if e.v == "question"}
    answers = {(e.s, e.t) for e in g.of_type("messages") if e.v == "answer"}
    assert {(s, t) for s, t in asks if (t, s) not in answers} == set()


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


# ---------------------------------------------------------------------------
# ENVIRONMENT.md's claims about what exists, as assertions.
#
# It is a proposal, and a proposal about unbuilt work rots faster than anything
# else in this repository: the moment somebody writes the spawner, every "does
# not exist yet" in it becomes a lie told confidently. Same treatment as
# SYSTEM.md's gaps -- each claim fails here when it stops being true, and the
# document has to be corrected to make the suite green.
# ---------------------------------------------------------------------------

def test_nothing_spawns_a_process_yet():
    """
    ENVIRONMENT.md's premise. `runtime_processes` has a reaper and no writer,
    which is the safe order to have built them in and the reason nothing has
    been orphaned so far. Write the spawner and this goes red, which is the
    moment the rest of that document needs re-reading rather than trusting.
    """
    writers = [py.name for py in paths.PACKAGE.rglob("*.py")
               if "__pycache__" not in py.parts
               and "INSERT INTO runtime_processes" in py.read_text(encoding="utf-8")]
    assert writers == [], (
        f"{writers} spawns into runtime_processes now; ENVIRONMENT.md still "
        f"says nothing does, and its risk ordering assumed that")


def test_the_reaper_still_identifies_a_process_by_pid_alone():
    """
    The one defect ENVIRONMENT.md names in *shipped* code, pinned so that fixing
    it is visible and so the document cannot go on claiming it afterwards.

    `boot.reap_processes` sends SIGTERM to every recorded pid. A pid is reused
    by the operating system, so after a crash and a reboot a recorded pid very
    likely belongs to something else entirely -- and the only thing between that
    and a kill is an `except` treating "not ours" and "already gone" as the same
    outcome. A second fact that survives a restart, the start time or the
    command line, is what would make the identification real.

    Asserted against the reaper's query rather than its prose: the query is what
    decides, and the table is what would have to grow a column.
    """
    src = (paths.PACKAGE / "core" / "boot.py").read_text(encoding="utf-8")
    assert "SELECT pid FROM runtime_processes" in src,         "the reaper's query moved; ENVIRONMENT.md quotes this one"

    schema = paths.SCHEMA.read_text(encoding="utf-8")
    table = schema.split("CREATE TABLE IF NOT EXISTS runtime_processes")[1]
    table = table.split(");")[0]
    assert "started_at" not in table and "start_time" not in table,         ("runtime_processes now records something beyond the pid — "
         "ENVIRONMENT.md's first build step is done and the document must "
         "stop calling it the cheapest fix on the page")


def test_no_role_can_reach_an_environment_yet():
    """
    The toolkit ENVIRONMENT.md proposes does not exist, so nothing in it can be
    stale in the other direction: a role holding `env.start` before the four
    questions are answered is the failure that document is trying to prevent.
    """
    g = graph_mod.load()
    env_edges = sorted({f"{e.s}.{e.v}" for e in g.edges
                        if str(getattr(e, "t", "")).startswith("env")
                        or str(getattr(e, "v", "")).startswith("env")})
    assert env_edges == [], f"environment verbs exist now: {env_edges}"
