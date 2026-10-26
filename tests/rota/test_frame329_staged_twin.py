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

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import prompts

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
    near_old_c1 = ("When shorten=True, format_filename strips the directory "
                   "prefix from the given path.")
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
