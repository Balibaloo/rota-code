"""Frame 333 and frame 328 item 2: one quote reader on every channel.

Roman ruled on 2026-08-26 that `challenge` carries `quotes=` on all five
channels, and that a quote is "a contiguous span of the disputed row,
verbatim" (`DECISIONS.md` 1290 to 1297). The build of 2026-08-27 kept a
window of 12 characters on four sites: the challenge channels other than
the Tester's, the Tester's answer, and the red-line door. So a quote of
any 12 characters with prose around them passed. Each refusal below is
red on d495db74 and green after the reader.
"""
from __future__ import annotations

import pytest

from rota.core import sandbox
from rota.core.db import init_db
from rota.core.predicates import Wake
from rota.core.sandbox import build
from rota.roles import prompts

CRIT = "closing an account leaves its invoices in place for seven years"
TEST = "def test_close():\n    close('a1')\n    assert invoices_for('a1') == []"
STATEMENT = "invoices are kept for seven years after the account is closed"
# Twelve characters of the row, and prose that is not on the row.
OFF_CRIT = "'leaves its invoices' names no observable store"
OFF_STATEMENT = "'invoices are kept' cannot hold with the export constraint"
REASON = ("right code keeps the invoices, so the test must assert that "
          "invoices_for('a1') still holds them")


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, "
                 "approval_ver, version) VALUES ('i1','account closure',"
                 "'in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('t1','i1','close the account')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('c1','t1',?)", (CRIT,))
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES "
                 "('b1','i1','running')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b1','t1')")
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                 "VALUES ('ts1','b1','c1','tests/test_close.py',?)", (TEST,))
    conn.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
                 "('e1','principal',1,'how long do we keep invoices?')")
    conn.execute("INSERT INTO statements (id, span_entry, span_start, "
                 "span_end, text, status) VALUES ('s1','e1',0,10,?,"
                 "'ratified')", (STATEMENT,))
    conn.commit()
    return conn


# --- the Ends-when of frame 333: one refusal per channel ---------------------

def test_terminologist_to_vision_keeper_refuses_a_window_quote(db):
    sb = build("terminologist", db, mode="criterion_repair")
    with pytest.raises(ValueError, match="not a span of the live text of c1"):
        sb.call("msg.challenge_vision_keeper", refs=["c1"], quotes=OFF_CRIT)
    sb.call("msg.challenge_vision_keeper", refs=["c1"],
            quotes="leaves its invoices in place for seven years")
    assert sb.ctx.outbound


def test_architect_to_vision_keeper_refuses_a_window_quote(db):
    """Frame 333, item 2: a statement is a quotable row now. On d495db74
    the door read no statement, so any quote went through."""
    sb = build("architect", db, mode="deliver")
    with pytest.raises(ValueError, match="not a span of the live text of s1"):
        sb.call("msg.challenge_vision_keeper", refs=["s1"],
                quotes=OFF_STATEMENT)
    sb.call("msg.challenge_vision_keeper", refs=["s1"],
            quotes="invoices are kept for seven years")
    assert sb.ctx.outbound


def test_critic_to_developer_refuses_a_window_quote(db):
    sb = build("critic", db, batch_id="b1", mode="review")
    with pytest.raises(ValueError, match="not a span of the live text of c1"):
        sb.call("msg.challenge_developer", refs=["c1"], quotes=OFF_CRIT)
    sb.call("msg.challenge_developer", refs=["c1"],
            quotes=["leaves its invoices in place"])
    assert sb.ctx.outbound


def test_each_quotable_row_of_refs_needs_its_own_quote(db):
    """Frame 333, item 1: each quotable row of refs has a quote."""
    sb = build("terminologist", db, mode="criterion_repair")
    with pytest.raises(ValueError, match="no span of the live text of t1"):
        sb.call("msg.challenge_vision_keeper", refs=["c1", "t1"],
                quotes=["leaves its invoices in place"])
    sb.call("msg.challenge_vision_keeper", refs=["c1", "t1"],
            quotes=["leaves its invoices in place", "close the account"])
    assert sb.ctx.outbound


def test_a_quote_under_the_floor_is_refused_on_every_channel(db):
    sb = build("critic", db, batch_id="b1", mode="review")
    with pytest.raises(ValueError, match="shorter than 12 characters"):
        sb.call("msg.challenge_developer", refs=["c1"], quotes=["invoices"])


# --- frame 328, item 2: the views the seat was shown ------------------------

def test_a_quote_copied_from_the_json_form_is_read(db):
    """The prompt's JSON shows each backslash of the row as two. A seat
    that copies that form quotes the row it was shown."""
    db.execute("UPDATE criteria SET text = ? WHERE id = 'c1'",
               ("an export to C:\\temp\\new keeps every invoice",))
    db.commit()
    sb = build("terminologist", db, mode="criterion_repair")
    sb.call("msg.challenge_vision_keeper", refs=["c1"],
            quotes=["export to C:\\\\temp\\\\new keeps"])
    assert sb.ctx.outbound
    with pytest.raises(ValueError, match="not a span"):
        sb.call("msg.challenge_vision_keeper", refs=["c1"],
                quotes=["export to D:\\\\temp\\\\new keeps"])


def test_the_views_hold_the_raw_row_and_its_json_form():
    views = sandbox._shown_views("a\\b\nc")
    assert "a\\b\nc" in views
    assert "a\\\\b\\nc" in views


# --- frame 333, item 3: the Tester's answer and the red-line door -----------

def _challenged_tester(db):
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m1','th','developer','tester',"
               "'challenge','[\"c1\", \"ts1\"]',1,'open')")
    db.commit()
    sb = build("tester", db, batch_id="b1", mode="challenge",
               allow=prompts.mode_tools("tester", "challenge"),
               wake=Wake("tester", "message", message_id="m1", refs=("m1",)))
    # The runner sets the trigger from the wake (`run_session`).
    sb.ctx.trigger = "m1"
    return sb


def test_the_testers_answer_refuses_a_window_quote(db):
    sb = _challenged_tester(db)
    with pytest.raises(ValueError, match="carries the criterion's words"):
        sb.call("msg.answer_developer", refs=["c1", "ts1"],
                quotes="the criterion says 'leaves its invoices' and the "
                       "test asserts that")
    sb.call("msg.answer_developer", refs=["c1", "ts1"],
            quotes="leaves its invoices in place")
    assert sb.ctx.outbound


def test_the_testers_answer_refuses_a_quote_off_its_rows(db):
    sb = _challenged_tester(db)
    with pytest.raises(ValueError, match="not a span of the live text"):
        sb.call("msg.answer_developer", refs=["c1", "ts1"],
                quotes=["leaves its invoices in place", "the test is right"])


def test_the_red_line_door_wants_the_whole_line(db):
    """Night 142's m83 quoted part of the line and left out what made it
    red. The window of 12 characters passed a part of the line."""
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
               "result, attempt, output) VALUES ('r1','b1','ts1','abc123',"
               "'fail',1,?)",
               (">       assert invoices_for('a1') == []\n"
                "E       assert ['inv1'] == []",))
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="tests_failing")
    with pytest.raises(ValueError, match="its run names the line it fails at"):
        sb.call("msg.challenge_tester", refs=["c1", "ts1"],
                quotes=["leaves its invoices in place", "invoices_for('a1')"],
                reason=REASON)
    sb.call("msg.challenge_tester", refs=["c1", "ts1"],
            quotes=["leaves its invoices in place",
                    "assert invoices_for('a1') == []"], reason=REASON)
    assert sb.ctx.outbound


def test_the_window_is_gone():
    assert not hasattr(sandbox, "_quotes_span")


# --- pass 1b: one reader decides on every channel ---------------------------

#: The five channels of `challenge`, as (role, mode, tool, extra arguments).
CHANNELS = [
    ("developer", "tests_failing", "msg.challenge_tester", {"reason": REASON}),
    ("critic", "review", "msg.challenge_tester", {}),
    ("terminologist", "criterion_repair", "msg.challenge_vision_keeper", {}),
    ("architect", "deliver", "msg.challenge_vision_keeper", {}),
    ("critic", "review", "msg.challenge_developer", {}),
]
CHANNEL_IDS = ["dev-tester", "critic-tester", "term-vk", "arch-vk",
               "critic-dev"]
RED_RUN = (">       assert invoices_for('a1') == []\n"
           "E       assert ['inv1'] == []")


def _send(db, channel, quotes):
    role, mode, tool, extra = channel
    sb = build(role, db, batch_id="b1", mode=mode,
               allow=prompts.mode_tools(role, mode))
    sb.call(tool, refs=["c1", "ts1"], quotes=quotes, **extra)
    return sb


def _red(db):
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
               "result, attempt, output) VALUES ('r1','b1','ts1','abc123',"
               "'fail',1,?)", (RED_RUN,))
    db.commit()


# Review of pass 1, findings 1 and 2: night 167 walk 3 sent one opening
# mark, and the seat's call syntax sends `\'` for each mark of the row.
SEAT_FORMS = ["'leaves its invoices in place",
              "assert invoices_for(\\'a1\\') == []"]
# Review of pass 1, finding 3: the run's `E` line is a view of the test.
E_LINE = ["leaves its invoices in place", "assert ['inv1'] == []"]


@pytest.mark.parametrize("channel", CHANNELS, ids=CHANNEL_IDS)
@pytest.mark.parametrize("quotes", [SEAT_FORMS, E_LINE],
                         ids=["seat-forms", "e-line"])
def test_one_quote_gets_one_answer_on_every_channel(db, channel, quotes):
    _red(db)
    assert _send(db, channel, quotes).ctx.outbound


@pytest.mark.parametrize("channel", CHANNELS, ids=CHANNEL_IDS)
def test_prose_around_a_span_is_refused_on_every_channel(db, channel):
    with pytest.raises(ValueError, match="not"):
        _send(db, channel, [OFF_CRIT, "assert invoices_for('a1') == []"])


def test_the_red_line_door_reads_the_escaped_marks(db):
    """Review of pass 1, finding 1: the evidence door admitted
    `assert invoices_for(\\'a1\\') == []`, and the red-line door then
    refused it with the same line."""
    _red(db)
    line = "assert invoices_for(\\'a1\\') == []"
    assert sandbox._quote_holds(line, "assert invoices_for('a1') == []")
    assert _send(db, CHANNELS[0], ["leaves its invoices in place", line]
                 ).ctx.outbound


def test_a_comment_of_the_test_is_no_quote_on_any_channel(db):
    """Review of pass 1, finding 7: a test row is its code."""
    db.execute("UPDATE tests SET body = ? WHERE id = 'ts1'",
               (TEST + "  # the account keeps nothing at all",))
    db.commit()
    with pytest.raises(ValueError):
        _send(db, CHANNELS[4], ["leaves its invoices in place",
                                "the account keeps nothing at all"])


def test_a_retired_criterion_says_so_in_the_contest_block(db):
    """Review of pass 1, finding 8: a retired row has no live text."""
    import json

    from rota.core.runner import _contest_block

    for mid, verb in (("m70", "present"), ("m71", "reply")):
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                   "verb, body_refs, seq) VALUES (?, 'm70', 'liaison', "
                   "'principal', ?, ?, 1)", (mid, verb, json.dumps(["c1"])))
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, "
               "status, texts) VALUES ('r1', 'm70', 'm71', ?, 'not this', "
               "'landed', ?)", (json.dumps({"c1": "contest"}),
                                json.dumps({"c1": "an older text of c1"})))
    db.execute("UPDATE criteria SET retired_by = 'r1' WHERE id = 'c1'")
    db.commit()
    block = _contest_block(db, [{"id": "c1"}], legend=False)
    assert ("c1: He contested this text, and the criterion is retired now: "
            "an older text of c1") in block
    assert "The live text is" not in block
