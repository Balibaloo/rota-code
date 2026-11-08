"""
Frame 362, slice 2: a criterion rests on the ruled set it was written from.

Dry run 7: his m22 called the guess wrong, and s147 wrote the set of m26 with
`_foldline`. The Terminologist s150 then wrote c1 to c3 with the surface
`parameter.py::q_split`, and the surface door refused the Tester's 13
encodes on `_foldline`. The rows below copy `w5.db` of dry run 7 as
literals. One test reads that copy and skips when the file is absent.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from rota.core import predicates
from rota.core.db import (SessionResult, commitment_columns, init_db,
                          session_commit)
from rota.core.runner import _as_write, _mode_key, _owed_criterion_lines
from rota.core.sandbox import build
from rota.core.scheduler import Wake, criterion_owed, owed
from rota.roles import prompts

ITEM = "folds_long_lines"
OLD = "src/icalendar/parser/parameter.py::q_split"
NEW = ("src/icalendar/parser/string.py", "src/icalendar/tests/test_icalendar.py",
       "src/icalendar/parser/string.py::_foldline")
# m24, his words on the plan page m22 (dry 7, `rulings.words`).
WORDS = ("Line 2 is wrong. The fold is _foldline in src/icalendar/parser/string.py, "
         "and its tests are in src/icalendar/tests/test_icalendar.py. Do not touch "
         "parameter.py or property.py.")
TEXT = "Folding a long line keeps every character of the line."
# The worktree's copy, or the run's own file, so a review worktree finds it.
COPY = next((p for p in (
    Path(__file__).resolve().parents[2] / "scratch" / "dry7_w5.db",
    Path("C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/"
         "8b2312ef-0b14-4322-a20c-908058cac23b/scratchpad/dry7/copies/w5.db"))
    if p.exists()), Path("dry7_w5.db"))


@pytest.fixture
def db(tmp_path):
    """Dry 7 before s147: the Architect's own guess, c1 on its surface, b1
    running with a head."""
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES (?, 'fold long lines', 'in_scope', 'approved', 1, 1)", (ITEM,))
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_1', ?, 'fold')",
                 (ITEM,))
    conn.execute("INSERT INTO touch_guesses (item_id, item_ver, grain, grain_kind) "
                 "VALUES (?, 1, ?, 'symbol')", (ITEM, OLD))
    conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) VALUES "
                 "('c1', 'tk_1', ?, ?)", (TEXT, json.dumps([OLD])))
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) VALUES "
                 "('b1', ?, 'running', 'abc')", (ITEM,))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1', 'tk_1')")
    conn.commit()
    return conn


def _correct(db):
    """His m24 lands as ruling r_m24, and s147 writes the set of m26."""
    for mid, frm, to, verb, cause, seq in (("m22", "liaison", "principal", "present", None, 22),
                                      ("m24", "principal", "liaison", "converse", "m22", 24),
                                      ("m26", "principal", "liaison", "verdict", "m22", 26)):
        db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
                   "verb, body_refs, seq, status) VALUES (?, ?, 't', ?, ?, ?, ?, ?, 'answered')",
                   (mid, cause, frm, to, verb, json.dumps([f"guess:{ITEM}"]), seq))
    db.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, status, "
               "verdict_id) VALUES ('r_m24', 'm22', 'm24', ?, ?, 'landed', 'm26')",
               (json.dumps({f"guess:{ITEM}": "contest"}), WORDS))
    for grain in NEW:
        db.execute("INSERT INTO touch_guesses (item_id, item_ver, ruling_id, grain, "
                   "grain_kind) VALUES (?, 1, 'm26', ?, ?)",
                   (ITEM, grain, "symbol" if "::" in grain else "path"))
    db.commit()


def _respecify(db, refs, **args):
    wake = Wake("terminologist", "tick:criterion_owed", refs=refs)
    sb = build("terminologist", db, mode="criterion_repair", session_id="s1",
               wake=wake, allow=prompts.mode_tools("terminologist", "criterion_repair"))
    out = sb.call("criteria.respecify", id="c1", text=TEXT, **args)
    session_commit(db, SessionResult(
        session_id="s1", role="terminologist", wake_kind=wake.kind,
        wake_refs=refs, writes=[_as_write(w) for w in sb.ctx.writes]))
    return out


def test_a_criterion_of_the_architects_own_set_is_never_owed(db):
    assert criterion_owed(db, "c1") is None
    assert [w.refs for w in predicates.tests_missing(db)] == [("b1",)]
    assert predicates.criterion_owed(db) == []


def test_a_newer_ruled_set_makes_the_criterion_owed(db):
    _correct(db)
    found = criterion_owed(db, "c1")
    assert found["verdict"] == "m26" and found["line"] == "guess"
    assert set(found["grains"]) == set(NEW)
    # The code line itself is not owed: s147's set carries the verdict.
    assert owed(db, ITEM) is None
    assert predicates.tests_missing(db) == []
    wakes = predicates.criterion_owed(db)
    assert [(w.role, w.kind, w.refs) for w in wakes] == [
        ("terminologist", "tick:criterion_owed", ("c1", "m26"))]
    assert _mode_key(wakes[0]) == "criterion_repair"
    lines = "\n".join(_owed_criterion_lines(db, wakes[0]))
    assert "string.py::_foldline" in lines and WORDS in lines and OLD in lines


def test_the_respecify_on_the_owed_wake_ends_the_fact(db):
    _correct(db)
    out = _respecify(db, ("c1", "m26"))
    assert out == {"id": "c1", "kept": True, "rests_on": "m26"}
    assert db.execute("SELECT guess_ruling FROM criteria WHERE id = 'c1'"
                      ).fetchone()[0] == "m26"
    assert db.execute("SELECT 1 FROM refs WHERE src_table = 'criteria' AND "
                      "src_id = 'c1' AND kind = 'ruling' AND target = 'r_m24'"
                      ).fetchone()
    assert criterion_owed(db, "c1") is None
    assert predicates.criterion_owed(db) == []
    assert [w.refs for w in predicates.tests_missing(db)] == [("b1",)]


def test_a_respecify_on_another_wake_stamps_nothing(db):
    _correct(db)
    out = _respecify(db, ("c1", "m99"))
    assert out.get("unchanged") is True
    assert criterion_owed(db, "c1") is not None


def test_a_test_row_follows_its_criterion(db):
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
               "('tst_c1', 'b1', 'c1', 'tests/test_c1.py', 'def test(): pass')")
    db.commit()
    assert criterion_owed(db, "tst_c1") is None
    _correct(db)
    assert criterion_owed(db, "tst_c1")["criterion"] == "c1"
    _respecify(db, ("c1", "m26"))
    assert criterion_owed(db, "tst_c1") is None


def test_a_retired_criterion_is_not_owed(db):
    _correct(db)
    db.execute("UPDATE criteria SET retired_by = 'r_x' WHERE id = 'c1'")
    db.commit()
    assert criterion_owed(db, "c1") is None


@pytest.mark.skipif(not COPY.exists(), reason="dry run 7's w5 copy is absent")
def test_dry_run_7_c1_to_c3_are_owed_after_s147():
    src = sqlite3.connect(f"file:{COPY.as_posix()}?immutable=1", uri=True)
    conn = sqlite3.connect(":memory:")
    src.backup(conn)
    conn.row_factory = sqlite3.Row
    commitment_columns(conn)
    for cid in ("c1", "c2", "c3"):
        # Slice 1's reader does not see the criterion.
        assert owed(conn, cid) is None
        found = criterion_owed(conn, cid)
        assert found["verdict"] == "m26"
        assert "src/icalendar/parser/string.py::_foldline" in found["grains"]


def _encode(db, body):
    sb = build("tester", db, mode="tests_missing", session_id="s2", batch_id="b1",
               wake=Wake("tester", "tick:tests_missing", refs=("b1",)),
               allow=prompts.mode_tools("tester", "tests_missing"))
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    return sb.call("tests.encode", id="tst_c1", criterion_id="c1",
                   path="tests/test_c1.py", body=body)


BODY = "from nowhere import calculate_tip\n\ndef test_tip():\n    assert calculate_tip(10) == 1\n"


def test_an_encode_of_an_owed_criterion_is_refused_first(db):
    """The review of pass 1, finding 1: the open import door let this
    body land on an owed criterion."""
    _correct(db)
    with pytest.raises(Exception) as caught:
        _encode(db, BODY)
    assert str(caught.value).endswith(
        "criterion c1 rests on a guess of the code that the principal "
        "corrected. The Terminologist rewrites it first. Wait for your next "
        "wake, and do not encode c1 now")


def test_an_encode_of_a_criterion_not_owed_meets_the_old_doors(db):
    with pytest.raises(Exception) as caught:
        _encode(db, BODY)
    assert "rests on a guess" not in str(caught.value)
    assert "nowhere" in str(caught.value) or "q_split" in str(caught.value)


def test_an_amended_item_leaves_the_old_ruled_set_behind(db):
    """The review of pass 1, finding 6: the ruled set of version 1 is no
    basis for the criteria of version 2."""
    _correct(db)
    assert criterion_owed(db, "c1") is not None
    db.execute("UPDATE items SET version = 2, approval_ver = 2 WHERE id = ?", (ITEM,))
    db.commit()
    assert criterion_owed(db, "c1") is None
    db.execute("UPDATE items SET version = 1, approval_ver = 1 WHERE id = ?", (ITEM,))
    db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind, ruling_id) "
               "VALUES ('b1', 'src/icalendar/parser/string.py', 'path', 'm26')")
    db.execute("DELETE FROM touch_guesses WHERE ruling_id = 'm26'")
    db.commit()
    assert criterion_owed(db, "c1")["line"] == "batch"
    db.execute("UPDATE batches SET status = 'abandoned' WHERE id = 'b1'")
    db.commit()
    assert criterion_owed(db, "c1") is None


def _specify(db, cid, surface):
    """A `tick:criteria` session of the Terminologist that writes `cid`."""
    for grain in NEW:
        db.execute("INSERT OR IGNORE INTO code_index (grain, grain_kind) VALUES (?, ?)",
                   (grain, "symbol" if "::" in grain else "path"))
    db.commit()
    wake = Wake("terminologist", "tick:criteria", refs=(ITEM,))
    sb = build("terminologist", db, mode="criteria", session_id="s3", wake=wake,
               allow=prompts.mode_tools("terminologist", "criteria"))
    sb.call("criteria.specify", id=cid, ticket_id="tk_1",
            text="Folding a long line never splits a word.", surface_refs=surface)
    session_commit(db, SessionResult(
        session_id="s3", role="terminologist", wake_kind=wake.kind,
        wake_refs=wake.refs, writes=[_as_write(w) for w in sb.ctx.writes]))
    return sb, wake


def test_a_criterion_written_after_his_set_rests_on_it(db):
    """The review of pass 1, finding 3: the push shows his set, and the
    criterion written from it is not owed."""
    _correct(db)
    from rota.core.runner import CODE_LINE_KEY, push_working_set

    sb, wake = _specify(db, "c4", ["src/icalendar/parser/string.py::_foldline"])
    shown = push_working_set("terminologist", sb, wake)[CODE_LINE_KEY]
    assert shown["files and functions"] == list(NEW)
    assert shown["the principal said"] == WORDS
    assert db.execute("SELECT guess_ruling FROM criteria WHERE id = 'c4'"
                      ).fetchone()[0] == "m26"
    assert criterion_owed(db, "c4") is None
    # c1 was written before his set, so it stays owed.
    assert criterion_owed(db, "c1")["verdict"] == "m26"


def test_a_criterion_written_with_no_ruled_set_rests_on_nothing(db):
    from rota.core.runner import CODE_LINE_KEY, push_working_set

    sb, wake = _specify(db, "c4", None)
    assert CODE_LINE_KEY not in push_working_set("terminologist", sb, wake)
    assert db.execute("SELECT guess_ruling FROM criteria WHERE id = 'c4'"
                      ).fetchone()[0] == ""


def test_a_spent_rewrite_names_the_check_and_keeps_the_encode_shut(db):
    """The review of pass 1, finding 4: the page said "c1, m26" and
    "nothing moves until that is cleared", and the batch went on."""
    from rota.core.scheduler import criterion_owed_key
    from rota.roles.principal import _render_state

    _correct(db)
    key = criterion_owed_key(criterion_owed(db, "c1"))
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined) "
               "VALUES (?, 3, 1)", (key,))
    db.commit()
    assert predicates.tests_missing(db) == []
    page = _render_state(db)
    assert (f'Stuck: the team could not rewrite the check "{TEXT}" for the code '
            f"you corrected after 3 attempts. Nothing waits on you. The change "
            f"goes on, and no test is written for that check until it is "
            f"rewritten. Tell me what to change.") in page, page
    assert "c1, m26" not in page
    with pytest.raises(Exception, match="The Terminologist rewrites it first"):
        _encode(db, BODY)


def test_a_spent_rewrite_leaves_only_the_owed_check_out(db):
    """The second look at slice 2, finding 7: after a spent key the Tester
    was woken for the owed check, which `_refuse_owed` refuses."""
    from rota.core.scheduler import criterion_owed_key

    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs, guess_ruling) "
               "VALUES ('c2', 'tk_1', 'An empty line stays empty.', '[]', 'm26')")
    _correct(db)
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined) "
               "VALUES (?, 3, 1)", (criterion_owed_key(criterion_owed(db, "c1")),))
    db.commit()
    (wake,) = predicates.tests_missing(db)
    assert wake.refs == ("b1",) and wake.detail.startswith("without a test: c2")
    assert "c1" not in wake.detail
