"""
A silent cut says so, in the result and in the record.

A cut that writes no string at all leaves a seat unable to tell a short answer
from a shortened one, and leaves a reader of the record unable to count either.
Frame 46's design record, section 2.7: the principal's ledger row can be
shorter than the challenge row it derives from, and nothing said so.
"""
import re

import pytest

from rota.core import sandbox as sandbox_mod
from rota.core.db import init_db
from rota.core.runner import run_session
from rota.core.scheduler import Wake
from rota.llm.llm import Pins, ScriptedBackend
from rota.testkit.fixtures import seed_provenance

FORM = re.compile(r"CUT [^:]+: [\d,]+ of [\d,]+ characters are not shown\. \S")


@pytest.fixture
def db(tmp_path):
    """A Vision Keeper with one message to answer, as `test_runner.py` seeds it."""
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                 "VALUES ('u1','principal','let users delete their account',1)")
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
                 "VALUES ('m1','t1','liaison','vision_keeper','deliver',1)")
    return conn


def _critic(tmp_path, name="s1"):
    """A Critic woken for one claim, with the claim's file already opened."""
    db = init_db(tmp_path / f"rota_{name}.db")
    db.execute("INSERT INTO constraints (id, headline, text) VALUES "
               "('k1', 'the schema is silent on unknown keys', 'no warning exists')")
    seed_provenance(db, "constraints", "k1", "observed")
    db.commit()
    sb = sandbox_mod.build("critic", db, session_id=name, mode="challenge",
                           area="@claim:constraints:k1")
    sb.ctx.wake_refs = ("@claim:constraints:k1",)
    sb.ctx.opened.add("src/parser.ts")          # what `challenge.load` opens
    return db, sb


def test_a_verdict_says_what_the_row_did_not_keep(tmp_path):
    """
    One site, both ways. A `why` the row keeps whole says nothing, and a `why`
    the row shortens says so in the wording every cut uses. `challenge.uphold`
    stores 300 characters of each field and stored them in silence.
    """
    _db, sb = _critic(tmp_path, "whole")
    kept = sb.call("challenge.uphold", citation="src/parser.ts",
                   quote="export function parse", why="the parser warns")
    assert kept["verdict"] == "stands"
    assert "not_shown" not in kept, "a result that fits must say nothing"
    assert not sb.ctx.cuts, "nothing was cut, so nothing is recorded"

    _db2, sb2 = _critic(tmp_path, "cut")
    long_why = "the parser warns on an unknown key, and here is why. " * 20
    shortened = sb2.call("challenge.uphold", citation="src/parser.ts",
                         quote="export function parse", why=long_why)
    notice = shortened["not_shown"]
    assert FORM.search(notice), notice
    whole = len(long_why.strip())                # the row stores the stripped text
    assert f"{whole - 300:,} of {whole:,} characters" in notice, notice
    assert "the challenge row's why" in notice, notice
    assert "Nothing returns the words the row did not keep" in notice, notice
    assert any("the challenge row's why" in c for c in sb2.ctx.cuts), sb2.ctx.cuts


def test_the_principals_ledger_row_is_cut_on_the_record_with_no_notice(tmp_path):
    """
    The two outputs are independent. A break stores 460 characters of its `why`
    on the Critic's own row and 160 on the principal's ledger row, so a `why` of
    300 characters reaches the Critic whole and the principal shortened. The
    Critic has no call that changes the principal's row, so that cut carries no
    notice, and the record carries the reason instead.
    """
    _db, sb = _critic(tmp_path, "ledger")
    why = ("the parser warns on an unknown key. " * 9).strip()
    assert 300 < len(why) < 460, len(why)

    out = sb.call("challenge.break", citation="src/parser.ts",
                  quote="export function parse", why=why)

    assert out["verdict"] == "falsified"
    assert "not_shown" not in out, "the Critic's own row kept every word"
    ledger = [c for c in sb.ctx.cuts if "ledger" in c]
    assert ledger == [f"cut the principal's ledger row, from this verdict's "
                      f"why: {len(why) - 160} of {len(why)} characters not "
                      f"stored"], sb.ctx.cuts
    assert not any("CUT" in c for c in sb.ctx.cuts), \
        "a recorded reason is not a seat's notice"


def test_a_recorded_cut_reaches_the_session_record(db, monkeypatch):
    """
    The record's half survives the session. `session_note` writes the runner's
    account as the last turn, so a reader counts what the system shortened
    without replaying a prompt. The seat is shown nothing here, which is the
    point: the two outputs travel apart.
    """
    from rota.roles import api

    def shortened(ctx, query):
        api._cut(ctx, "the rulings' text", 200, 900, "characters")
        return [{"id": "d1", "headline": "a ruling"}]

    monkeypatch.setitem(api.REGISTRY, ("decisions", "search"), shortened)
    backend = ScriptedBackend(["TOOL: decisions.search(query='scope')", "Done."])
    outcome = run_session(db, Wake(role="vision_keeper", kind="message",
                                   message_id="m1", detail="deliver"),
                          backend=backend, pins=Pins(model="scripted"))

    assert outcome.committed, outcome.errors
    reason = "cut the rulings' text: 700 of 900 characters not stored"
    assert reason in outcome.errors, outcome.errors
    said = db.execute(
        "SELECT completion FROM turns WHERE session_id = ? ORDER BY seq DESC",
        (outcome.result.session_id,)).fetchone()[0]
    assert reason in said, "the record does not carry the reason"
    assert "CUT" not in backend.calls[-1][1], "the seat was sent a notice too"
