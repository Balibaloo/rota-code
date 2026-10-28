"""Frame 329, night 166's s194: a respecify that writes a twin.

The principal contested c_1 and c_2 of `tk_1_format_filename_example` with
one fact. s194 respecified both into one sentence in one session, and both
calls landed. `_near_twin` read a staged write's ticket from `ticket_id`, and
a respecify stages its write with no `ticket_id`. So the twin that the same
session had staged was invisible to the door.

The texts are copied from `.rota/clickI_night166.db`: c_1 and c_2 from the
relay m79 in s194's turn 1, c_3 from its row, and the new text from
`tool_calls` seq 12 and 13.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import prompts
from rota.testkit.fixtures import seed_verdict

TICKET = "tk_1_format_filename_example"
C1, C2, C3 = (f"c_{n}_format_filename_example" for n in (1, 2, 3))
BEFORE = {
    C1: "When shorten=True, format_filename strips the directory prefix "
        "from the path.",
    C2: "When shorten=True, format_filename returns only the basename of "
        "the provided path.",
    C3: "The docstring of format_filename must include an example "
        "demonstrating that with shorten=True, a/b/c.txt is displayed as "
        "c.txt.",
}
# tool_calls seq 12 and 13 of s194 sent this one text for c_1 and for c_2.
NEW = ("When shorten=True, the docstring of format_filename must include an "
       "example showing that a/b/c.txt is displayed as c.txt.")
SURFACE = ["src/click/utils.py::format_filename"]


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('format_filename_example', 'With shorten "
                 "set to True, the path a/b/c.txt shows as c.txt in the "
                 "docstring of format_filename.', 'in_scope', 'approved', 1, 1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, "
                 "'format_filename_example', 'with shorten set to true, the "
                 "path a/b/c.txt shows as c.txt in the docstring of "
                 "format_filename')", (TICKET,))
    for cid, text in BEFORE.items():
        conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                     "VALUES (?, ?, ?, ?)",
                     (cid, TICKET, text, '["src/click/utils.py::format_filename"]'))
    conn.commit()
    return conn


def _repair(db):
    return build("terminologist", db, mode="criterion_repair",
                 allow=prompts.mode_tools("terminologist", "criterion_repair"))


def _assert_the_way_out(said: str) -> None:
    """Repair R2: the refusal names the sibling and the two acts the mode
    holds. It names no retire, by law 6."""
    assert f"this says what {C1} says, in nearly the same words" in said
    assert "msg.challenge_vision_keeper" in said
    assert "a fact that this line alone holds" in said
    assert "retire" not in said


def test_a_twin_staged_in_the_same_session_is_refused(db):
    sb = _repair(db)
    out = sb.call("criteria.respecify", id=C1, text=NEW, surface_refs=SURFACE)
    assert out.get("respecified") is True
    with pytest.raises(ValueError) as caught:
        sb.call("criteria.respecify", id=C2, text=NEW, surface_refs=SURFACE)
    _assert_the_way_out(str(caught.value))


def test_a_twin_on_file_from_an_earlier_session_is_refused(db):
    first = _repair(db)
    assert first.call("criteria.respecify", id=C1, text=NEW,
                      surface_refs=SURFACE).get("respecified") is True
    # The first session's write, as its commit leaves the row.
    db.execute("UPDATE criteria SET text = ?, version = 2 WHERE id = ?",
               (NEW, C1))
    db.commit()
    with pytest.raises(ValueError) as caught:
        _repair(db).call("criteria.respecify", id=C2, text=NEW,
                         surface_refs=SURFACE)
    _assert_the_way_out(str(caught.value))


def test_a_sibling_s_old_words_refuse_no_right_call(db):
    """A staged text replaces the text on file for its id. c_1 moves off its
    old words, so c_2 may take words close to c_1's old ones."""
    sb = _repair(db)
    sb.call("criteria.respecify", id=C1, text=NEW, surface_refs=SURFACE)
    # The text names the docstring. The ticket's headline names a docstring,
    # so a text with no documentation word meets frame 322's door first.
    near_old_c1 = ("In the docstring, when shorten=True, format_filename "
                   "strips the directory prefix from the path.")
    out = sb.call("criteria.respecify", id=C2, text=near_old_c1,
                  surface_refs=SURFACE)
    assert out.get("respecified") is True


def test_a_staged_rewrite_of_a_retired_row_is_no_twin(db):
    db.execute("INSERT INTO criteria (id, ticket_id, text, retired_by) VALUES "
               "('c_9_format_filename_example', ?, 'format_filename keeps the "
               "path when shorten is False.', 'r_drop')", (TICKET,))
    db.commit()
    sb = _repair(db)
    sb.call("criteria.respecify", id="c_9_format_filename_example", text=NEW,
            surface_refs=SURFACE)
    out = sb.call("criteria.respecify", id=C1, text=NEW, surface_refs=SURFACE)
    assert out.get("respecified") is True


def test_a_specify_after_a_respecify_meets_the_exact_check(db):
    sb = build("terminologist", db, mode="normal",
               allow=prompts.mode_tools("terminologist", "criteria")
               + ["criteria.respecify"])
    sb.call("criteria.respecify", id=C1, text=NEW, surface_refs=SURFACE)
    with pytest.raises(ValueError) as caught:
        sb.call("criteria.specify", id="c_4_format_filename_example",
                ticket_id=TICKET, text=NEW, surface_refs=SURFACE)
    # The exact door's words, not the fuzzy door's.
    assert f"those are {C1}'s words already, on the same ticket" in str(
        caught.value)


def test_a_rewrite_then_a_retire_of_a_sibling_is_no_twin(db):
    """Review 1, finding 3: a row that the session retires is no twin, even
    when the session rewrote it first and the row on file is still live."""
    sb = _repair(db)
    sb.call("criteria.respecify", id=C2, text=NEW, surface_refs=SURFACE)
    # The write that the retire op stages for a ruled drop.
    sb.ctx.writes.append(("criteria", C2, {"retired_by": "r_drop"}, False))
    out = sb.call("criteria.respecify", id=C1, text=NEW, surface_refs=SURFACE)
    assert out.get("respecified") is True


# Night 166's rows around s194's wake: the page m76, his words m77, the
# verdict m78 and the relay m79, with the batch bg_3 that held the ticket.
WORDS = ("Lines 2 and 3 are not what I asked for. They make rules for how "
         "the function behaves, but only the docstring changes and the code "
         "stays the same.")
PAGE = ["bg_3", "format_filename_example", C1, C2, C3]
ORDER = ["format_filename_example", C1, C2, C3, "bg_3"]


def _night166_relay(conn) -> None:
    rows = (("m76", None, "liaison", "principal", "present", PAGE, None, 79),
            ("m77", "m76", "principal", "liaison", "converse", PAGE, WORDS, 80),
            ("m78", "m76", "principal", "liaison", "verdict", [C1, C2], None,
             81),
            ("m79", "m78", "liaison", "terminologist", "relay", [C1, C2],
             None, 82))
    for mid, cause, sender, to, verb, refs, text, seq in rows:
        conn.execute("INSERT INTO messages (id, cause_id, thread_id, "
                     "from_role, to_role, verb, body_refs, body_text, seq) "
                     "VALUES (?, ?, 'm76', ?, ?, ?, ?, ?, ?)",
                     (mid, cause, sender, to, verb, json.dumps(refs), text, seq))
    conn.execute("INSERT INTO config (key, value) VALUES ('order:m77', ?)",
                 (json.dumps(ORDER),))
    per_item = {C1: "contest", C2: "contest", C3: "approve",
                "format_filename_example": "approve", "bg_3": "approve"}
    conn.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, "
                 "status, verdict_id) VALUES ('r_a5e4b30470', 'm76', 'm77', ?, "
                 "?, 'landed', 'm78')", (json.dumps(per_item), WORDS))
    # The verdict m78 on the landed ruling, the old `verdict:m78` map (fact F1).
    seed_verdict(conn, "m78", json.dumps({C1: "contest", C2: "contest"}),
                 ruling="r_a5e4b30470")
    conn.execute("INSERT INTO batches (id, item_id, head_commit, status) "
                 "VALUES ('bg_3', 'format_filename_example', "
                 "'a0295dffd730b5d6d14813fded003472c8e5ed21', 'running')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_3', ?)", (TICKET,))
    conn.commit()


def _s194(db):
    _night166_relay(db)
    sb = build("terminologist", db, mode="criterion_repair", session_id="s194",
               allow=prompts.mode_tools("terminologist", "criterion_repair"))
    sb.ctx.trigger = "m79"
    sb.ctx.wake_kind = "message"
    return sb


def _challenge(sb, refs):
    # Frame 333: each row of refs has a quote, and each quote is a span.
    sb.call("msg.challenge_vision_keeper", refs=refs,
            quotes=[BEFORE[r] for r in refs])


def _answer_refused(sb) -> str:
    with pytest.raises(ValueError) as caught:
        sb.call("msg.answer_tester", refs=[C1, C2], round_no=0)
    assert not [m for m in sb.ctx.outbound
                if m["to_role"] == "tester" and m["verb"] == "answer"]
    return str(caught.value)


def test_a_challenge_with_no_rewrite_lets_no_answer_out(db):
    """Review 1b, finding 5, scenario C: a challenge in place of a rewrite
    counts as no write. The Tester would read the words he contested, the
    fault of night 159 that frame 308 closed."""
    sb = _s194(db)
    _challenge(sb, [C1, C2])
    said = _answer_refused(sb)
    assert f"No respecify of {C1}, {C2} has landed in this session" in said


def test_a_challenge_of_an_untried_criterion_lets_no_answer_out(db):
    """Review 1b, finding 5, scenario D: c_1's rewrite lands, and c_2 is
    challenged with no try at c_2. c_2 still has no write."""
    sb = _s194(db)
    sb.call("criteria.respecify", id=C1, text=NEW, surface_refs=SURFACE)
    _challenge(sb, [C2])
    said = _answer_refused(sb)
    assert f"No respecify of {C2} has landed in this session" in said


def test_a_challenge_after_the_twin_refusal_lets_the_answer_out(db):
    """Review 1, finding 1: the twin refusal sends the seat to the Vision
    Keeper. A criterion that the session challenged after its twin refusal
    counts as written, so the answer with c_1's rewrite reaches the Tester."""
    sb = _s194(db)
    sb.call("criteria.respecify", id=C1, text=NEW, surface_refs=SURFACE)
    with pytest.raises(ValueError):
        sb.call("criteria.respecify", id=C2, text=NEW, surface_refs=SURFACE)
    _challenge(sb, [C2])
    sb.call("msg.answer_tester", refs=[C1, C2], round_no=0)
    assert [m["body_refs"] for m in sb.ctx.outbound
            if m["to_role"] == "tester" and m["verb"] == "answer"] == [[C1, C2]]
