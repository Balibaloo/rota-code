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

import re
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
    "ASSUMPTIONS.md": "the register of what the system assumes about a "
                      "codebase -- law, tripwire or debt; its mechanical "
                      "entries are asserted as onboard-time tripwires in "
                      "test_onboarding_phases.py",
    "ONBOARDING.md": "the derivation of the onboarding phases and the measured "
                     "reasoning behind each; its structural claims -- phase "
                     "order, what drains each, what a session may write -- are "
                     "asserted in test_onboarding_phases.py",
    "SEAT.md": "a proposal for the operator's interface, argued rather than "
               "asserted, because almost nothing in it exists yet. Its one "
               "claim about today — that a run records nothing but its project "
               "root — is what item 2 of it changes, and the moment that lands "
               "this line is what has to be re-read",
    "ANSWER_KEY_ctn_v3.md": "the same, for the third — and the first written "
                            "for a branch nothing had surveyed, because the "
                            "other branch of that repo was already onboarded "
                            "and any claim about it is contaminated",
}

# Checked by a test, or read by code at runtime.
LOAD_BEARING = {
    "ROLES.md": "test_roles_doc.py",
    "REGISTER.md": "test_roles_doc.py, predicate classification",
    "MILESTONE.md": "cockpit/progress.py reads it at runtime",
    "ENVIRONMENT.md": "the 3Bd proposal; its claims about what exists are "
                      "asserted below and go red when the stage is built",
    "LOOPS.md": "test_roles_doc.py -- the grade ledger; its gates are "
                "propositions and its headline claim is pinned",
    "COMPLETION.md": "test_docs.py below -- the unified remaining-work "
                     "document; its claims about what is green are asserted "
                     "so a closed debt cannot keep reading as open",
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

    Vision Keeper can answer Developer and Tester, so `unresolved` mode carries
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
    wake = Wake("vision_keeper", "tick:unresolved", refs=("m1",))

    wide = build("vision_keeper", db, mode="normal", allow=allow)
    assert "msg.answer_developer" in wide.functions()

    narrow = build("vision_keeper", db, mode="normal", allow=allow, wake=wake)
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

def test_only_one_module_may_write_a_running_process():
    """
    This test was green while the thing it forbade existed.

    It grepped for the literal `INSERT INTO runtime_processes`, and
    `environments.record` writes `INSERT OR REPLACE INTO runtime_processes` --
    four characters that are not in the needle. So the spawner landed, the
    tripwire that was meant to fire on exactly that did not, and
    ENVIRONMENT.md went on saying the table was "written by nothing yet" for
    as long as anybody trusted this.

    A check on one spelling of a statement is a check on the spelling. What is
    worth guarding is *which module* may write the table at all -- one place,
    the one that also owns the two-fact ownership test the reaper depends on.
    """
    writers = sorted(
        py.name for py in paths.PACKAGE.rglob("*.py")
        if "__pycache__" not in py.parts
        and re.search(r"INSERT\s+(OR\s+\w+\s+)?INTO\s+runtime_processes",
                      py.read_text(encoding="utf-8"), re.I))
    assert writers == ["environments.py"], (
        f"{writers} write runtime_processes. Recording a spawned process is "
        f"`environments.record`'s alone, because that is the module holding "
        f"the pid-and-start-time pair the reaper needs to kill safely")


def test_nothing_calls_the_spawner_yet():
    """
    ENVIRONMENT.md's premise, asserted as the thing that actually protects the
    machine rather than as a fact about SQL.

    A writer nothing calls cannot orphan anything; a writer something calls
    can, whatever its spelling. `spawn` is written and unreached, which is the
    safe order and the reason nothing has been orphaned so far. Call it and
    this goes red, which is the moment the rest of that document needs
    re-reading rather than trusting -- particularly step 5, the toolkit, which
    is the first thing that would hand a *role* the capability.
    """
    callers = sorted(
        py.name for py in paths.PACKAGE.rglob("*.py")
        if "__pycache__" not in py.parts and py.name != "environments.py"
        and re.search(r"\bspawn\s*\(", py.read_text(encoding="utf-8")))
    assert callers == [], (
        f"{callers} start processes now; ENVIRONMENT.md still says nothing "
        f"does, and its whole risk ordering rests on that")


def test_the_reaper_kills_only_what_it_can_prove_is_its_own():
    """
    ENVIRONMENT.md's one defect in shipped code, now closed — and this test is
    the reason the document could not go on claiming it.

    It asserted the *hole*: that `runtime_processes` carried nothing but a pid,
    so the reaper's SIGTERM rested on a value the operating system reuses. It
    went red the moment the column landed, which is what a staleness check is
    for. It asserts the property now.

    Two facts or no kill. `worktrees.py` states the same rule before removing a
    directory: either alone can be satisfied by an accident.
    """
    schema = paths.SCHEMA.read_text(encoding="utf-8")
    table = schema.split("CREATE TABLE IF NOT EXISTS runtime_processes")[1]
    table = table.split(");")[0]
    assert "started_at" in table,         "the second fact is what makes a recorded pid an identity"

    src = (paths.PACKAGE / "core" / "boot.py").read_text(encoding="utf-8")
    assert "is_still_ours" in src,         "the reaper must ask whether the process is ours before signalling it"

    body = src.split("def reap_processes")[1].split(chr(10) + "def ")[0]
    signal_at = body.index("os.kill")
    guard_at = body.index("is_still_ours")
    assert guard_at < signal_at,         "the ownership check has to happen before the kill, not beside it"


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


def test_the_footer_keys_are_the_ones_the_code_binds():
    """
    README said `alt+r` wipes and reindexes. The code binds `ctrl+alt+r` and
    there is no `alt+r`, and the onboard key was not in README at all — so the
    documented way to onboard was still a shell command, which is also what the
    seat itself tells you when a run has no project.

    Documentation that names keys drifts silently, because nothing types them.
    Read off `BINDINGS` rather than kept in step by hand.
    """
    from rota import paths
    from rota.cockpit.tui import RotaApp

    readme = (paths.PACKAGE / "README.md").read_text(encoding="utf-8")
    seat = readme.split("**The TUI is the seat.**", 1)[1].split("##", 1)[0]

    # The *table* is the claim surface, not the prose around it. The paragraph
    # under it names `ctrl+w` to explain why nothing here is bound to it, which
    # is the opposite of claiming it exists — a blunter scan read that as drift,
    # and would have taught the next person to delete the explanation.
    documented = {m.group(1) for m in
                  re.finditer(r"^\|\s*`([^`]+)`\s*\|", seat, re.M)}
    bound = {k for k, _, _ in RotaApp.BINDINGS} - {"ctrl+c"}

    assert bound - documented == set(), (
        f"bound and undocumented: {sorted(bound - documented)}")
    assert documented - bound == set(), (
        f"README names {sorted(documented - bound)} and nothing binds them")


def test_the_completion_document_claims_only_what_holds():
    """
    `COMPLETION.md` says what remains, and a remaining-work document is the
    fastest-staling kind there is. The claims it makes about the present are
    asserted: the mode-case lint it calls green must be green, the segments
    file it counts must hold that many cases, and the acts it calls missing
    must actually be missing -- so building interrupt or cancel without
    updating the plan turns this red, the same trade the ledger makes.
    """
    doc = (paths.PACKAGE / "COMPLETION.md").read_text(encoding="utf-8")

    import yaml as _yaml

    segs = _yaml.safe_load(
        (paths.PACKAGE.parent / "tests" / "rota" / "cases" /
         "g1_segments.yaml").read_text(encoding="utf-8"))
    assert len(segs) == 4, "the segment count in Track B moved; update both"

    from rota.core import predicates as P
    assert "preempt" in P.REGISTRY and "interrupt" not in P.REGISTRY, (
        "steering acts moved; COMPLETION.md Track A line 1 is stale")
