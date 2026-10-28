"""
A seat sends again a call that landed earlier in its session.

Night 170's W8 (`plans/night170-w8-read.md`): 37 refusals in 27 sessions on
night 170 and 32 in 20 on night 171 answered a copy of a landed call. The
twin door told the seat that its own row's words were "already" there and
asked for "a second sentence". s117 of night 171 read that as a rejection
and logged five faults. The runner now answers a copy of a landed write
with the turn and the earlier answer, and a reply of copies alone ends the
session. Each test replays a register's call shape with a scripted seat.
"""
from __future__ import annotations

import pathlib

import pytest

from rota.core.db import COPIES_END, init_db
from rota.core.predicates import Wake
from rota.core.runner import run_session
from rota.llm.llm import Pins, ScriptedBackend

PINS = Pins(model="stub", temperature=0.0)
WAKE = Wake("terminologist", "tick:criteria", refs=("i1",), detail="criteria")


@pytest.fixture
def db(tmp_path):
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i1','get_app_dir falls back to AppData',"
               "'in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('tk_1','i1','the AppData fallback')")
    db.commit()
    return db


def _spec(cid: str, text: str) -> str:
    return (f"TOOL: criteria.specify(id='{cid}', ticket_id='tk_1', "
            f'text="{text}", surface_refs=[\'get_app_dir\'])')


ROAMING = ("When get_app_dir is invoked on Windows with roaming=True and "
           "APPDATA or LOCALAPPDATA are unset, the returned path must be under "
           "the user's AppData Roaming folder rather than the bare home folder.")
LOCAL = ("When get_app_dir is invoked on Windows with roaming=False and "
         "APPDATA or LOCALAPPDATA are unset, the returned path must be under "
         "the user's AppData Local folder rather than the bare home folder.")
NO_RAISE = ("The get_app_dir function must not raise an exception when APPDATA "
            "or LOCALAPPDATA environment variables are unset on Windows.")
DOCSTRING = ("The docstring for format_filename must include an example "
             "demonstrating that when shorten=True, the path a/b/c.txt is "
             "displayed as c.txt.")
LOOKUP = "TOOL: glossary.lookup(term='format_filename')"
DONE = "It stands, and nothing more is needed for it."


def _run(db, replies: list[str]):
    backend = ScriptedBackend(replies)
    outcome = run_session(db, WAKE, backend=backend, pins=PINS)
    return outcome, [c[1] for c in backend.calls]


def _results(prompt: str) -> str:
    """The results block the seat read last: the text after its last reply."""
    return prompt.rsplit("TOOL: ", 1)[-1]


def test_s117_a_resent_batch_answers_the_landed_criteria_as_done(db):
    """Night 171, s117 turn 2: c_1 and c_3 landed, c_2 was refused as a near
    twin, and the seat sent the whole batch again. The two landed calls are
    answered as done at turn 1, and c_2 goes to its door again."""
    batch = "\n".join(["TOOL: glossary.consult(terms=['appdata', 'roaming'])",
                       _spec("c_1", ROAMING), _spec("c_2", LOCAL),
                       _spec("c_3", NO_RAISE)])
    outcome, prompts = _run(db, [batch, batch, "done"])
    assert len(prompts) == 3, outcome.errors
    turn_2 = _results(prompts[1])
    assert "ERROR criteria.specify(id='c_2'): this says what c_1 says" in turn_2
    turn_3 = _results(prompts[2])
    assert ('OK criteria.specify -> done at turn 1 of this session: '
            '{"id": "c_1"}. ' + DONE) in turn_3
    assert ('OK criteria.specify -> done at turn 1 of this session: '
            '{"id": "c_3"}. ' + DONE) in turn_3
    # A copy of a refused call is no copy, and the door answers it again.
    assert "ERROR criteria.specify(id='c_2'): this says what c_1 says" in turn_3
    assert "c_1's words already" not in turn_3
    assert "c_3's words already" not in turn_3
    assert COPIES_END not in outcome.errors
    assert outcome.committed, outcome.errors
    assert sorted(r[0] for r in db.execute("SELECT id FROM criteria")) == [
        "c_1", "c_3"]


def test_s117_turn_3_a_new_id_on_the_seats_own_words_is_told_it_stands(db):
    """Night 171, s117 turn 3: the seat sent c_1's words under c_a. The twin
    is the seat's own row from this session, so the refusal says it landed
    and stands, and asks for no second sentence."""
    outcome, prompts = _run(db, [_spec("c_1", ROAMING), _spec("c_a", ROAMING),
                                 "done"])
    line = _results(prompts[2])
    assert ("ERROR criteria.specify: those are c_1's words already, on the "
            "same ticket. c_1 is your criterion from this session. It landed "
            "and stands.") in line
    assert "second sentence" not in line
    assert [r[0] for r in db.execute("SELECT id FROM criteria")] == ["c_1"]


def test_s187_turn_6_a_landed_criterion_beside_a_new_note(db):
    """Night 170, s187 turn 6: c_1 landed at turn 1, and the seat sent it
    again beside a new `ledger.log`. The copy is answered as done, and the
    note goes to its door, so the session goes on."""
    note = ("TOOL: ledger.log(about_ref='tk_1', about_table='tickets', "
            "assumption='This criterion captures the documentation "
            "requirement.', kind='default')")
    outcome, prompts = _run(db, [_spec("c_1", DOCSTRING),
                                 _spec("c_2", DOCSTRING),
                                 _spec("c_1", DOCSTRING) + "\n" + note,
                                 "done"])
    assert len(prompts) == 4, outcome.errors
    turn_2 = _results(prompts[2])
    assert "c_1 is your criterion from this session" in turn_2
    turn_3 = _results(prompts[3])
    assert ('OK criteria.specify -> done at turn 1 of this session: '
            '{"id": "c_1"') in turn_3
    assert "OK ledger.log -> " in turn_3
    assert "c_1's words already" not in turn_3
    assert COPIES_END not in outcome.errors


def test_s222_a_reply_of_copies_alone_ends_the_session(db):
    """Night 171, s222: c_1 landed at turn 1. At turn 3 the seat sent a
    refused note and c_1 again, then c_1 with a read, then c_1 alone. The
    copy is answered as done each time, and the reply of copies alone ends
    the session in place of a fourth twin refusal."""
    bad_note = ("TOOL: ledger.log(about_ref='c_1', about_table='criteria', "
                "assumption='The term is in the code.', kind='reasoned')")
    outcome, prompts = _run(db, [_spec("c_1", DOCSTRING), LOOKUP,
                                 bad_note + "\n" + _spec("c_1", DOCSTRING),
                                 _spec("c_1", DOCSTRING) + "\n" + LOOKUP,
                                 _spec("c_1", DOCSTRING),
                                 _spec("c_1", DOCSTRING)])
    turn_3 = _results(prompts[3])
    assert "ERROR ledger.log(about_ref='c_1'): kind='reasoned'" in turn_3
    assert ('OK criteria.specify -> done at turn 1 of this session: '
            '{"id": "c_1"') in turn_3
    assert "words already" not in turn_3
    assert len(prompts) == 5
    assert outcome.iterations == 5
    assert outcome.errors[-1] == COPIES_END
    assert outcome.committed, outcome.errors
    assert [r[0] for r in db.execute("SELECT id FROM criteria")] == ["c_1"]


def test_a_journal_call_said_twice_goes_to_its_door_twice(db):
    """Law 14: a journal records events, and saying a thing twice is two
    events. A copy of `ledger.log` keeps today's path, so no copy line
    answers it and no reply of journal copies ends the session."""
    note = ("TOOL: ledger.log(about_ref='tk_1', about_table='tickets', "
            "assumption='The ticket names one fallback.', kind='default')")
    outcome, prompts = _run(db, [note, note, "done"])
    assert len(prompts) == 3, outcome.errors
    assert "done at turn" not in _results(prompts[2])
    assert COPIES_END not in outcome.errors


def test_a_later_write_to_the_same_row_drops_the_copy(db, monkeypatch):
    """A copy changes nothing only while the rows it wrote are as it left
    them. Here a later call stages c_1's row again, as a retire does, so the
    next copy of the specify goes to its door and no copy line answers it.
    The criteria mode offers no call that writes c_1 again, so the note's
    door stages the row in this test."""
    from rota.core import runner

    real = runner.session_sandbox

    def sandbox(*a, **kw):
        sb = real(*a, **kw)
        call = sb.call

        def with_retire(name, *pos, **args):
            out = call(name, *pos, **args)
            if name == "ledger.log":
                sb.ctx.writes.append(("criteria", "c_1", {"retired_by": "r9"},
                                      False))
            return out
        sb.call = with_retire
        return sb

    monkeypatch.setattr(runner, "session_sandbox", sandbox)
    note = ("TOOL: ledger.log(about_ref='tk_1', about_table='tickets', "
            "assumption='The ticket names one fallback.', kind='default')")
    outcome, prompts = _run(db, [_spec("c_1", DOCSTRING), note,
                                 _spec("c_1", DOCSTRING), "done"])
    assert len(prompts) == 4, outcome.errors
    assert "done at turn" not in _results(prompts[3])
    assert COPIES_END not in outcome.errors


def test_the_copy_line_has_one_writer():
    """The one-reader pin of night 170's W8. The runner alone answers a copy
    of a landed call. A second door that writes the line goes red here."""
    root = pathlib.Path(__file__).resolve().parents[2] / "rota"
    found = sorted(str(p.relative_to(root)).replace("\\", "/")
                   for p in root.rglob("*.py")
                   if "-> done at turn" in p.read_text(encoding="utf-8"))
    assert found == ["core/runner.py"], found
    source = (root / "core" / "runner.py").read_text(encoding="utf-8")
    assert source.count("-> done at turn") == 1
