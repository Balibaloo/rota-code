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


def test_the_principals_ledger_row_keeps_the_whole_why(tmp_path):
    """
    The principal rules from the ledger row, so the row keeps the finding.
    The Critic writes the claim first and the finding second. On night 88 a
    160-character why lost the finding on 4 of 8 falsified rows (frame 59).
    The quote stays at 160 characters, and that cut carries no notice. The
    Critic has no call that changes the principal's row.
    """
    _db, sb = _critic(tmp_path, "ledger")
    claim = ("the claim says the schema is silent on an unknown key, and "
             "that no warning exists anywhere in the parse path. " * 2)
    finding = "but parser.ts line 42 calls warnUnknownKey for each key it drops"
    why = f"{claim}{finding}"
    assert 280 < len(why) < 460, len(why)
    quote = ("export function parse(input) { for (const key of keys) "
             "warnUnknownKey(key); } " * 3).strip()
    assert len(quote) > 160, len(quote)

    out = sb.call("challenge.break", citation="src/parser.ts",
                  quote=quote, why=why)

    assert out["verdict"] == "falsified"
    ledger = [fields for table, _id, fields in sb.ctx.writes if table == "ledger"]
    assert len(ledger) == 1, sb.ctx.writes
    taken = ledger[0]["default_taken"]
    assert f"-- {why}. The claim stands" in taken, taken
    assert finding in taken, "the ledger row lost the finding"
    assert f"\"{quote[:160]}\"" in taken, taken
    assert quote[:161] not in taken, "the quote is not capped at 160"
    cuts = [c for c in sb.ctx.cuts if "ledger" in c]
    assert cuts == [f"cut the principal's ledger row, from this verdict's "
                    f"quote: {len(quote) - 160} of {len(quote)} characters "
                    f"not stored"], sb.ctx.cuts
    assert not any("CUT" in c for c in sb.ctx.cuts), \
        "a recorded reason is not a seat's notice"


def test_the_vacuous_ledger_row_keeps_the_whole_why(tmp_path):
    """
    The vacuous verdict's ledger row keeps the why as the challenge row keeps
    it. A 200-character cap dropped the finding the Critic writes after the
    claim (frame 59). The ledger row has no cut of its own to record.
    """
    _db, sb = _critic(tmp_path, "vacuous")
    claim = ("the claim says the schema is silent on an unknown key, and "
             "that no warning exists anywhere in the parse path. " * 2)
    finding = "but the claim names no behaviour a line could show or deny"
    why = f"{claim}{finding}"
    assert 200 < len(why) < 300, len(why)

    out = sb.call("challenge.vacuous", why=why)

    assert out["verdict"] == "unfounded"
    assert "not_shown" not in out, "the Critic's own row kept every word"
    ledger = [fields for table, _id, fields in sb.ctx.writes if table == "ledger"]
    assert len(ledger) == 1, sb.ctx.writes
    taken = ledger[0]["default_taken"]
    assert f"unfounded: {why}. An empty claim" in taken, taken
    assert finding in taken, "the ledger row lost the finding"
    assert not sb.ctx.cuts, sb.ctx.cuts


def test_a_recorded_cut_reaches_the_session_record(db, monkeypatch):
    """
    The record's half survives the session. `session_note` writes the runner's
    account as the last turn, so a reader counts what the system shortened
    without replaying a prompt. The seat is shown nothing here, which is the
    point: the two outputs travel apart.
    """
    from rota.roles import api

    def shortened(ctx, query):
        api._cut(ctx, "the rulings' text", 200, 900, "characters", stored=False)
        return [{"id": "d1", "headline": "a ruling"}]

    monkeypatch.setitem(api.REGISTRY, ("decisions", "search"), shortened)
    backend = ScriptedBackend(["TOOL: decisions.search(query='scope')", "Done."])
    outcome = run_session(db, Wake(role="vision_keeper", kind="message",
                                   message_id="m1", detail="deliver"),
                          backend=backend, pins=Pins(model="scripted"))

    assert outcome.committed, outcome.errors
    reason = "cut the rulings' text: 700 of 900 characters not shown"
    assert reason in outcome.errors, outcome.errors
    said = db.execute(
        "SELECT completion FROM turns WHERE session_id = ? ORDER BY seq DESC",
        (outcome.result.session_id,)).fetchone()[0]
    assert reason in said, "the record does not carry the reason"
    assert "CUT" not in backend.calls[-1][1], "the seat was sent a notice too"


def test_a_capped_candidate_list_records_its_reason_and_shows_no_notice(tmp_path):
    """
    A real op on the read side, not a monkeypatched one. `code.callables` hands
    back twenty of however many symbols the index holds, and nothing said so.
    The seat picks one name from the list and cannot act on the count, so the
    reason is recorded and the result carries no notice.
    """
    db = init_db(tmp_path / "rota.db")
    for i in range(30):
        db.execute("INSERT INTO code_index (grain, grain_kind, sym_kind, fan_in) "
                   "VALUES (?, 'symbol', 'function', ?)",
                   (f"src/pkg/mod_{i:02d}.py::render_{i:02d}", i))
    db.commit()
    sb = sandbox_mod.build("terminologist", db, session_id="s_cand", mode="criteria")

    rows = sb.call("code.callables")
    assert len(rows) == 20, len(rows)
    assert sb.ctx.cuts == ["cut the candidate symbols: 10 of 30 rows not shown"], \
        sb.ctx.cuts
    assert not any("CUT" in str(r) for r in rows), "a row carried a notice"


def test_no_recorded_reason_reads_as_a_refused_call(tmp_path):
    """
    `rota/testkit/fixtures.py:913` reads the text before a line's first colon as
    a thrown-out call whenever that text holds a dot, and counts it against the
    case's forbidden calls. A recorded reason that named `code.diff` would cost
    every cutting case a refusal it never made.
    """
    _db, sb = _critic(tmp_path, "dots")
    sb.call("challenge.break", citation="src/parser.ts",
            quote="export function parse",
            why=("the parser warns on an unknown key. " * 20).strip())
    db2 = init_db(tmp_path / "callables.db")
    for i in range(30):
        db2.execute("INSERT INTO code_index (grain, grain_kind, sym_kind, fan_in) "
                    "VALUES (?, 'symbol', 'function', ?)",
                    (f"src/pkg/mod_{i:02d}.py::render_{i:02d}", i))
    db2.commit()
    sb2 = sandbox_mod.build("terminologist", db2, session_id="s_dots", mode="criteria")
    sb2.call("code.callables", hint="render the pages")

    every = list(sb.ctx.cuts) + list(sb2.ctx.cuts)
    assert every, "no reason was recorded, so this proves nothing"
    for line in every:
        assert "." not in line.split(":", 1)[0], line
