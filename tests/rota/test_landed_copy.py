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

import json

import pytest

from rota.core.db import COPIES_END, init_db
from rota.core.predicates import Wake
from rota.core import runner
from rota.core.runner import run_session
from rota.llm.llm import Pins, ScriptedBackend
from rota.roles import api

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


@pytest.fixture
def doors(monkeypatch):
    """The names of the calls that reached `sb.call`, in order."""
    seen: list[str] = []
    real = runner.session_sandbox

    def sandbox(*a, **kw):
        sb = real(*a, **kw)
        call = sb.call

        def logged(name, *pos, **args):
            seen.append(name)
            return call(name, *pos, **args)
        sb.call = logged
        return sb

    monkeypatch.setattr(runner, "session_sandbox", sandbox)
    return seen


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
DONE = f"It stands, and {api.LANDED_STANDS}."


def _run(db, replies: list[str], wake: Wake = WAKE, **kw):
    backend = ScriptedBackend(replies)
    outcome = run_session(db, wake, backend=backend, pins=PINS, **kw)
    return outcome, [c[1] for c in backend.calls]


def _results(prompt: str) -> str:
    """The results block the seat read last: the text after its last reply."""
    return prompt.rsplit("TOOL: ", 1)[-1]


def test_s117_a_resent_batch_answers_the_landed_criteria_as_done(db, doors):
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
    assert doors.count("criteria.specify") == 4
    assert COPIES_END not in outcome.errors
    assert outcome.committed, outcome.errors
    assert sorted(r[0] for r in db.execute("SELECT id FROM criteria")) == [
        "c_1", "c_3"]


def test_s117_turn_3_a_new_id_on_the_seats_own_words_is_told_it_stands(db):
    """Night 171, s117 turn 3: the seat sent c_1's words under c_a. The twin
    is the seat's own row from this session, so the refusal says it landed
    and stands, and names the runner's step for a copy."""
    outcome, prompts = _run(db, [_spec("c_1", ROAMING), _spec("c_a", ROAMING),
                                 "done"])
    line = _results(prompts[2])
    assert ("ERROR criteria.specify: those are c_1's words already, on the "
            "same ticket. c_1 is your criterion from this session. It landed "
            "and stands, and nothing more is needed for it.") in line
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


# Night 171's s222, turns 1 to 6, word for word from the register.
S222_ITEM = "format_filename_example"
S222_TICKET = "tk_1_format_filename_example"
S222_DETAIL = ("No criterion yet: tk_1_format_filename_example (add one example "
               "to the docstring of the file name function that shows the path "
               "a/b/c.txt as c.txt when shorten is set to).")
S222_C1 = ('TOOL: criteria.specify(id="c_1_format_filename_example_docstring", '
           'ticket_id="tk_1_format_filename_example", text="The docstring of '
           'the file name function must include an example demonstrating that '
           'when shorten is set to True, the path a/b/c.txt shows as c.txt.", '
           'term_refs=["format_filename"], surface_refs=["format_filename"])')
S222_LOOKUP = "TOOL: glossary.lookup(term='format_filename')"
S222_NOTE = ('TOOL: ledger.log(about_ref="c_1_format_filename_example_docstring", '
             'about_table="criteria", assumption="The criterion relies on a '
             "term 'format_filename' that does not exist in the glossary, but "
             'the code source uses it. This is an observed usage from the '
             'codebase.", kind="reasoned")')
S222 = [
    S222_C1,
    S222_LOOKUP,
    S222_NOTE + "\n\n" + S222_C1 + "\n\nOK criteria.specify ->",
    S222_C1 + "\n\n" + S222_LOOKUP,
    S222_C1 + "\n\n" + S222_LOOKUP,
    "The criterion `c_1_format_filename_example_docstring` was already "
    "specified in this session. No further specification is possible for "
    "this ticket. The work is done.\n\n" + S222_C1 + "\n\n" + S222_LOOKUP,
]


@pytest.fixture
def s222_db(tmp_path):
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES (?, 'Give format_filename one example in its "
               "docstring: with shorten set to True, the path a/b/c.txt shows "
               "as c.txt.', 'in_scope', 'approved', 2, 2)", (S222_ITEM,))
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, ?, 'add one "
               "example to the docstring of the file name function that shows "
               "the path a/b/c.txt as c.txt when shorten is set to True')",
               (S222_TICKET, S222_ITEM))
    db.commit()
    return db


S222_WAKE = Wake("terminologist", "tick:criteria", refs=(S222_ITEM,),
                 detail=S222_DETAIL)


def test_s222_replayed_the_copies_are_done_and_the_reads_keep_the_session(
        s222_db, doors):
    """Night 171, s222, turns 1 to 6 as recorded. c_1 lands at turn 1, and
    every later copy of it is answered as done without its door. Turns 4 to
    6 pair the copy with a repeated `glossary.lookup`. A read is a call, so
    COPIES_END does not fire there. The repeat door refuses the read at
    turns 5 and 6, and the session runs until the seat sends no call (the W8
    review, finding 3)."""
    outcome, prompts = _run(s222_db, S222 + ["done"], wake=S222_WAKE)
    assert outcome.iterations == 7 and len(prompts) == 7
    assert doors.count("criteria.specify") == 1
    for k in (3, 4, 5):
        shown = _results(prompts[k])
        assert ("OK criteria.specify -> done at turn 1 of this session: "
                '{"id": "c_1_format_filename_example_docstring"') in shown, k
        assert "words already" not in shown, k
    assert "kind='reasoned' is no word this mode offers" in _results(prompts[3])
    assert COPIES_END not in outcome.errors
    assert outcome.errors[-1] == ("repeat refused: glossary.lookup asked three "
                                  "times this session and the answer has not "
                                  "changed; not answered again")
    assert outcome.committed, outcome.errors
    assert [r[0] for r in s222_db.execute("SELECT id FROM criteria")] == [
        "c_1_format_filename_example_docstring"]


def test_s222_without_the_read_a_reply_of_copies_alone_ends_the_session(
        s222_db, doors):
    """s222's turn 6 without the read: c_1 alone, after it landed at turn 1.
    The reply holds copies alone, so the session ends on COPIES_END and
    commits c_1."""
    outcome, prompts = _run(s222_db, [S222_C1, S222_C1, S222_C1],
                            wake=S222_WAKE)
    assert len(prompts) == 2
    assert doors.count("criteria.specify") == 1
    assert outcome.errors[-1] == COPIES_END
    assert outcome.committed, outcome.errors
    assert [r[0] for r in s222_db.execute("SELECT id FROM criteria")] == [
        "c_1_format_filename_example_docstring"]


def test_a_held_call_that_lands_on_the_stand_by_is_a_landed_call(db, doors):
    """A fresh read holds the writes behind it. The seat stands by them, the
    held calls run, and one is refused, so the seat gets one retry turn. It
    sends the batch again, the s117 shape. The held call that landed is a
    copy there, and its door does not run again (the W8 review, finding 7)."""
    read = "TOOL: code.source(path='src/click/utils.py')"
    bad = ("TOOL: criteria.specify(id='c_9', ticket_id='tk_9', "
           "text='the fallback is never the bare home folder')")
    batch = "\n".join([read, _spec("c_1", DOCSTRING), bad])
    outcome, prompts = _run(db, [batch, "I stand by them.",
                                 "\n".join([_spec("c_1", DOCSTRING), bad]),
                                 "done"])
    assert "NOT RUN" in _results(prompts[1])
    assert "The calls you stood by ran, and these were refused" in prompts[2]
    shown = _results(prompts[3])
    assert ('OK criteria.specify -> done at turn 2 of this session: '
            '{"id": "c_1"') in shown
    assert "c_1's words already" not in shown
    assert doors.count("criteria.specify") == 3


def test_a_journal_call_said_twice_goes_to_its_door_twice(db, doors):
    """Law 14: a journal records events, and saying a thing twice is two
    events. A copy of `ledger.log` keeps today's path, so no copy line
    answers it and no reply of journal copies ends the session."""
    note = ("TOOL: ledger.log(about_ref='tk_1', about_table='tickets', "
            "assumption='The ticket names one fallback.', kind='default')")
    outcome, prompts = _run(db, [note, note, "done"])
    assert len(prompts) == 3, outcome.errors
    assert doors.count("ledger.log") == 2
    assert "done at turn" not in _results(prompts[2])
    assert COPIES_END not in outcome.errors


def test_a_later_write_to_the_same_row_drops_the_copy(db, monkeypatch):
    """A copy changes nothing only while the rows it wrote are as it left
    them. Here a later call stages c_1's row again, as a retire does, so the
    next copy of the specify goes to its door and no copy line answers it.
    The criteria mode offers no call that writes c_1 again, so the note's
    door stages the row in this test."""
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


# ---- the one-reader pin, by behaviour ------------------------------------
#
# Each non-journal write is sent twice through `run_session`. The copy must
# not reach its door, and the reply of the copy alone ends the session. A
# door that answers a copy in its own words fails here, because the door
# runs. The seat's own twin under a new id is checked by its answer.


def _vk_db(tmp_path):
    from rota.testkit.fixtures import seed_provenance

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('reads_flags','the program reads flags from "
               "the command line','in_scope','approved',1,1)")
    seed_provenance(db, "items", "reads_flags", "reasoned")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, body_text, seq) VALUES ('m1','t1','architect',"
               "'vision_keeper','challenge',?, 'the criteria do not match', 1)",
               (json.dumps(["reads_flags"]),))
    db.commit()
    return db, Wake("vision_keeper", "message", "m1", detail="challenge"), {}


def _architect_db(tmp_path):
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('calculate_tip','calculate tip','in_scope',"
               "'approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('tk_1','calculate_tip','calc')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c_1','tk_1','it calculates')")
    db.commit()
    return (db, Wake("architect", "tick:grouping", refs=("tk_1",)),
            {"instructions": "group"})


def _terminologist_db(tmp_path):
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i1','get_app_dir falls back to AppData',"
               "'in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('tk_1','i1','the AppData fallback')")
    db.commit()
    return db, WAKE, {}


WRITES = {
    "criteria.specify": (_terminologist_db, _spec("c_1", DOCSTRING)),
    "problem.assert": (_vk_db, "TOOL: problem.assert(id='reads_flags', "
                               "text='the program reads flags and options "
                               "from the command line', kind='in_scope')"),
    "batches.group": (_architect_db, "TOOL: batches.group(id='b_1', "
                                     "item_id='calculate_tip', "
                                     "ticket_ids=['tk_1'])"),
}


@pytest.mark.parametrize("name", sorted(WRITES))
def test_a_copy_of_a_landed_write_never_reaches_its_door(name, tmp_path, doors):
    seed, call = WRITES[name]
    db, wake, kw = seed(tmp_path)
    outcome, prompts = _run(db, [call, call, "done"], wake=wake, **kw)
    assert doors.count(name) == 1, outcome.errors
    assert outcome.errors[-1] == COPIES_END, outcome.errors


def test_the_seats_own_twin_ends_with_the_copy_step(tmp_path):
    """The criteria twin and the batch twin, on the seat's own row from this
    session, end with the runner's step for a copy. A batch is a staged
    relation and no journal, so its twin is answered, not refused."""
    from rota.core.sandbox import build
    from rota.roles import prompts

    db, _, _ = _terminologist_db(tmp_path)
    sb = build("terminologist", db, mode="normal",
               allow=prompts.mode_tools("terminologist", "criteria"))
    sb.call("criteria.specify", id="c_1", ticket_id="tk_1", text=DOCSTRING)
    with pytest.raises(ValueError) as twin:
        sb.call("criteria.specify", id="c_2", ticket_id="tk_1", text=DOCSTRING)
    assert str(twin.value).endswith(f"It landed and stands, and "
                                    f"{api.LANDED_STANDS}.")

    (tmp_path / "architect").mkdir()
    adb = _architect_db(tmp_path / "architect")[0]
    sb = build("architect", adb, mode="normal",
               allow=prompts.mode_tools("architect", "grouping"))
    sb.call("batches.group", id="b_1", item_id="calculate_tip",
            ticket_ids=["tk_1"])
    again = sb.call("batches.group", id="b_2", item_id="calculate_tip",
                    ticket_ids=["tk_1"])
    assert again["id"] == "b_1" and again["unchanged"] is True
    assert again["note"].endswith(f"It landed and stands, and "
                                  f"{api.LANDED_STANDS}.")
    assert [w[1] for w in sb.ctx.writes if w[0] == "batches"] == ["b_1"]
