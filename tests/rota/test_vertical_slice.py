"""
The understanding loop, end to end (HANDOFF §8 step 5).

One principal sentence -> transcript -> statements -> L1 ratification -> scope items
-> Signoff -> approval. Liaison plus the shape roles, no Developer.

Two variants of the same arc:

  * scripted roles — deterministic, runs everywhere, proves the *loop* composes
    (gates pause it, the principal pump resumes it, quiescence is reached);
  * live roles — the same arc against a real model, opt-in via ROTA_T1.

Splitting them matters: when the live one fails, the scripted one tells you
whether the machine or the model broke.
"""
from __future__ import annotations

import json
import os

import pytest

from rota import loop
from rota.principal import Answer, ScriptedPrincipal, TranscriptPrincipal, record_entry
from rota.db import init_db
from rota.llm import Pins, ScriptedBackend
from rota.scheduler import frontier

ENTRY = "add a button so people can delete their account"


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute(
        "INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
        "VALUES ('m_in','t1','principal','liaison','converse',1)")
    record_entry(conn, "m_in", ENTRY)
    return conn


class RoleScript:
    """
    A backend that answers per role+mode rather than per call.

    The loop decides who wakes and when; a flat script would have to guess that
    order, and would then be testing my prediction of the loop rather than the
    loop.
    """

    name = "rolescript"

    def __init__(self, table: dict[str, list[str]]):
        self.table = table
        self.seen: list[str] = []

    def complete(self, system: str, user: str, pins, tools=None):
        from rota.llm import Completion

        key = next((k for k in self.table if _matches(k, system, user)), None)
        self.seen.append(key or "UNMATCHED")
        script = self.table.get(key) or []
        text = script.pop(0) if script else ""
        return Completion(text=text, pins=pins, backend=self.name)


def _matches(key: str, system: str, user: str) -> bool:
    """
    Match a role and, optionally, a mode.

    The mode needs a boundary after it. Without one, `verdict` matches
    `MODE: verdict_signoff` -- and since the first matching key wins, the
    ratification script was handed to the signoff session. Prefix collisions
    between mode names are exactly as invisible here as they were in the
    vocabulary.

    The header alone decides. There used to be an `or mode in user` fallback for
    modes whose prompt did not name them; every piece names its mode now, and the
    fallback matched `verdict` against the word "verdict" in the message body,
    which put the two signoff modes back into collision by a different route.
    """
    import re

    role, _, mode = key.partition(":")
    if f"You are {role}" not in system:
        return False
    return not mode or bool(re.search(rf"MODE: {re.escape(mode)}\b", system))


def test_understanding_loop_scripted(db):
    """
    The whole arc with canned roles: does the loop compose, pause at gates, and
    settle?
    """
    backend = RoleScript({
        "liaison:converse": [
            "TOOL: brief.segment(id='s1', span_entry='e_m_in', span_start=0, "
            f"span_end={len(ENTRY)}, text='{ENTRY}')",
            "TOOL: msg.confirm_principal(refs=['s1'])",
        ],
        "liaison:verdict": [
            "TOOL: brief.ratify(id='s1')",
            "TOOL: msg.deliver_gatekeeper(refs=['s1'])",
            "TOOL: msg.deliver_terminologist(refs=['s1'])",
            "TOOL: msg.deliver_architect(refs=['s1'])",
        ],
        "gatekeeper:deliver": [
            "TOOL: problem.assert(id='i1', text='users can delete their account', kind='in_scope')",
        ],
        "gatekeeper:signoff": [
            "TOOL: msg.submit_liaison(refs=['i1'])",
        ],
        "liaison:submit": [
            "TOOL: msg.present_principal(refs=['i1'])",
        ],
        "liaison:verdict_signoff": [
            "TOOL: msg.relay_gatekeeper(refs=['i1'])",
        ],
        "gatekeeper:relay": [
            "TOOL: problem.set_approval(id='i1', approval='approved')",
        ],
        "gatekeeper:slicing": [
            "TOOL: tickets.slice(id='tk1', item_id='i1', text='add a delete button')",
        ],
        "terminologist:criteria": [
            "TOOL: criteria.specify(id='c1', ticket_id='tk1', "
            "text='deleting tombstones the account', term_refs=['g1'])",
        ],
        "terminologist": [
            "TOOL: glossary.amend(id='g1', term='account', sense_short='login identity')",
        ],
        # The understanding loop ends where the delivery loop begins, and the
        # handover is Architect grouping tickets into batches. Before `grouping`
        # existed the two loops did not meet: criteria were written and nothing
        # ever turned them into a batch.
        "architect:grouping": [
            "TOOL: batches.group(id='b1', item_id='i1', ticket_ids=['tk1'])",
        ],
        "architect:annotate": [
            "TOOL: batches.annotate(batch_id='b1', paths=['src/account.py'])",
        ],
        "tester:tests_missing": [
            "TOOL: tests.author(id='tst1', batch_id='b1', criterion_id='c1', "
            "path='test_delete.py', body='assert tombstoned(account)')",
        ],
        "gatekeeper": [""],
        "architect": [""],
        "tester": [""],
        "critic": [""],
        "developer": [""],
    })

    # The principal ratifies, then approves. Anything else it defers.
    principal = TranscriptPrincipal({
        "confirm": Answer(verb="verdict", per_item={"s1": "approve"}),
        "present": Answer(verb="verdict", per_item={"i1": "approve"}),
        "clarify": Answer(verb="converse", text="yes, soft delete is fine"),
    })

    trace = loop.run(db, backend=backend, pins=Pins(model="scripted"),
                     principal=principal, max_steps=25)

    print("\n" + trace.render())

    # --- the arc happened ---------------------------------------------------
    assert db.execute("SELECT COUNT(*) n FROM entries").fetchone()["n"] == 1
    ratified = db.execute(
        "SELECT COUNT(*) n FROM statements WHERE status='ratified'").fetchone()["n"]
    assert ratified == 1, "L1 did not ratify"

    item = db.execute("SELECT approval, approval_ver, version FROM items").fetchone()
    assert item is not None, "no scope item was asserted"
    assert item["approval"] == "approved", f"Signoff did not approve: {item['approval']}"
    assert item["approval_ver"] >= item["version"], \
        "approval must postdate the last amendment or nothing can ever schedule"

    # --- and it settled ------------------------------------------------------
    assert trace.steps[-1].quiescent, f"loop did not settle: {trace.steps[-1]}"
    assert not trace.failures, f"failed sessions: {[str(s) for s in trace.failures]}"


def test_gate_pauses_the_loop_and_the_principal_resumes_it(db):
    """
    A gate is what the loop looks like while the principal has not answered.

    Deferral must be survivable: the loop settles cleanly, says *why* it is idle,
    and picks up exactly where it left off once an answer arrives.
    """
    backend = RoleScript({
        "liaison:converse": [
            "TOOL: brief.segment(id='s1', span_entry='e_m_in', span_start=0, "
            f"span_end={len(ENTRY)}, text='{ENTRY}')",
            "TOOL: msg.confirm_principal(refs=['s1'])",
        ],
        "liaison:verdict": [
            "TOOL: brief.ratify(id='s1')",
            "TOOL: msg.deliver_gatekeeper(refs=['s1'])",
        ],
        "gatekeeper": [""],
        "terminologist": [""],
        "architect": [""],
    })

    deferring = ScriptedPrincipal([None])          # sees the ask, declines to answer

    trace = loop.run(db, backend=backend, pins=Pins(model="scripted"),
                     principal=deferring, max_steps=10)

    last = trace.steps[-1]
    assert last.quiescent
    assert "gate" in last.note, f"idle for the wrong reason: {last.note!r}"
    assert loop.gates_open(db), "no gate recorded while waiting on the principal"
    assert deferring.seen, "the principal was never offered the ask"

    # ... and now they answer.
    answering = TranscriptPrincipal({"confirm": Answer(verb="verdict",
                                                    per_item={"s1": "approve"})})
    trace2 = loop.run(db, backend=backend, pins=Pins(model="scripted"),
                      principal=answering, max_steps=10)

    assert db.execute(
        "SELECT status FROM statements WHERE id='s1'").fetchone()["status"] == "ratified"
    assert trace2.committed >= 1, "answering the gate did not resume the loop"


def test_loop_is_idempotent_when_quiescent(db):
    """Turning the crank on a settled system must not invent work."""
    backend = RoleScript({"liaison:converse": [""], "gatekeeper": [""]})
    loop.run(db, backend=backend, pins=Pins(model="scripted"), max_steps=5)

    before = db.execute("SELECT COUNT(*) n FROM sessions").fetchone()["n"]
    trace = loop.run(db, backend=backend, pins=Pins(model="scripted"), max_steps=5)
    after = db.execute("SELECT COUNT(*) n FROM sessions").fetchone()["n"]

    assert trace.steps[0].quiescent or after == before, \
        "a quiescent system produced new sessions"


@pytest.mark.skipif(not os.environ.get("ROTA_T1"),
                    reason="live arc hits a real model; set ROTA_T1=1")
def test_understanding_loop_live(db):
    """The same arc, real model, real prompts. The slice, for real."""
    from rota.llm import OllamaBackend, available_models

    model = os.environ.get("ROTA_MODEL", "llama3.1:8b")
    if model not in available_models():
        pytest.skip(f"{model} unavailable")

    principal = TranscriptPrincipal({
        "confirm": Answer(verb="verdict", per_item={"s1": "approve"}),
        "present": Answer(verb="verdict", per_item={}),
        "clarify": Answer(verb="converse", text="soft delete is fine"),
    })

    trace = loop.run(db, backend=OllamaBackend(timeout=180),
                     pins=Pins(model=model, temperature=0.0, num_ctx=8192),
                     principal=principal, max_steps=14)
    print("\n" + trace.render())

    # More than one entry is legitimate — the principal answers questions. A
    # role *authoring* one is not, and that is the thing worth asserting.
    # Liaison has no callable transcript write at all now; this is the
    # end-to-end proof of it.
    authors = {r["author"] for r in db.execute("SELECT DISTINCT author FROM entries")}
    assert authors <= {"principal"}, f"a role authored principal speech: {authors}"

    assert db.execute(
        "SELECT COUNT(*) n FROM statements").fetchone()["n"] >= 1, "no segmentation"
    assert trace.committed >= 2, f"too little happened:\n{trace.render()}"

    # The loop must settle rather than spin. Today it does not: Liaison
    # re-clarifies without limit because the principal-touch cap is not built. That
    # cap is a real design law (2 consecutive non-closing touches per blocker in
    # steady state), and this assertion is the thing that will hold it honest.
    assert trace.stuck is None, f"livelocked: {trace.stuck}"
