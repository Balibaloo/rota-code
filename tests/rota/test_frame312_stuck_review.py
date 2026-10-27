"""
Frame 312, pass 1: the stopped page and the shift page name a quarantined tick.

The rows come from night 160, read for `plans/frame312-provenance.md`,
section 6. m45 put "The team stopped work on this change." on bg_1, whose
35 tests passed and whose review landed no verdict after 3 attempts. The
shift page that m53 answered then said "What it waits on: nothing from
you." while the same review key stayed quarantined.
"""
from __future__ import annotations

import pytest

from rota.core.db import backfill_ruled_refs, init_db
from rota.roles.principal import render_page
from rota.testkit.fixtures import seed_provenance, seed_ref

S1 = ("Add an echo_json(obj) helper next to echo that prints an object as compact "
      "JSON on one line, followed by a newline.")
S2 = ("Let confirm() take a default_on_eof flag: when stdin is closed it returns "
      "the default instead of aborting.")
HEAD = "8877b1b8a3c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4"
REVIEW = "critic|tick:review|bg_1"
M45_REFS = ["bg_1", "echo_json", "echo_json_helper"]
SHIFT = "m_shift_echo_json_m_p2"


@pytest.fixture
def bg1(tmp_path):
    """Night 160 before m45: bg_1 running at its one head commit, 35 tests
    that pass, and its three expected files."""
    db = init_db(tmp_path / "rota.db")
    for sid, text in (("s1", S1), ("s2", S2)):
        db.execute("INSERT INTO entries (id, author, text, ts_order) VALUES "
                   "(?, 'principal', ?, 1)", (f"e_{sid}", text))
        db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
                   "text, status) VALUES (?, ?, 0, ?, ?, 'ratified')",
                   (sid, f"e_{sid}", len(text), text))
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version, "
               "priority, is_description) VALUES ('echo_json', ?, 'in_scope', "
               "'approved', 1, 1, 1, 0)", (S1,))
    seed_provenance(db, "items", "echo_json", "decided")
    seed_ref(db, "items", "echo_json", "statement", "s1")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_echo_json', "
               "'echo_json', 'the ticket')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('echo_json_helper', "
               "'tk_echo_json', 'The function `echo_json` must not print any "
               "additional text before or after the JSON output.')")
    db.execute("INSERT INTO batches (id, item_id, head_commit, status) VALUES "
               "('bg_1', 'echo_json', ?, 'running')", (HEAD,))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
               "('bg_1', 'tk_echo_json')")
    for path in ("src/click/utils.py", "tests/test_utils/test_echo.py"):
        db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind, confidence) "
                   "VALUES ('bg_1', ?, 'path', 'expected')", (path,))
        db.execute("INSERT INTO code_index (grain, grain_kind) VALUES (?, 'path')",
                   (path,))
    for k in range(35):
        db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                   "VALUES (?, 'bg_1', ?, 'tests/test_utils/test_echo.py', "
                   "'def test(): pass')",
                   (f"tst_{k}", "echo_json_helper" if k == 0 else None))
        db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result) "
                   "VALUES (?, 'bg_1', ?, ?, 'pass')", (f"tr_{k}", f"tst_{k}", HEAD))
    db.commit()
    return db


def _quarantine(db, key: str, attempts: int = 3) -> None:
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, reported) "
               "VALUES (?, ?, 1, 1)", (key, attempts))


def test_m45_names_the_review_with_no_verdict_and_its_attempts(bg1):
    _quarantine(bg1, REVIEW)
    page = render_page(bg1, "present", M45_REFS, stalled=[REVIEW])[0]
    assert "The team stopped work" not in page, page
    assert page.splitlines()[0] == (
        "The review of this change stopped after 3 attempts with no verdict. "
        "Its tests passed at the review's last attempt."), page
    assert "The team gave up: the review gave no verdict after 3 attempts." in page


def test_a_tester_tick_keeps_the_stopped_work_page(bg1):
    """Night 136's m96 shape: the Tester gave up on `tests_missing`."""
    key = "tester|tick:tests_missing|bg_1"
    _quarantine(bg1, key)
    page = render_page(bg1, "present", M45_REFS, stalled=[key])[0]
    assert page.startswith("The team stopped work on this change."), page
    assert "The team gave up: the team could not write the tests after 3 attempts." in page


def test_a_review_beside_a_failing_tick_keeps_the_stopped_work_page(bg1):
    keys = [REVIEW, "developer|tick:tests_failing|bg_1"]
    for key in keys:
        _quarantine(bg1, key)
    page = render_page(bg1, "present", M45_REFS, stalled=keys)[0]
    assert page.startswith("The team stopped work on this change."), page


def test_a_batch_with_no_quarantined_key_is_the_touch_note(bg1):
    page = render_page(bg1, "present", M45_REFS, stalled=[])[0]
    assert page.startswith("Before I build this"), page


def _shift_rows(db) -> list[str]:
    lines = render_page(db, "present", ["echo_json", "s2"], ask_id=SHIFT)[0].splitlines()
    return [ln.strip() for ln in lines if ln.strip().startswith(("Where", "What"))]


def test_m53_names_the_stuck_review_and_never_nothing_from_you(bg1):
    _quarantine(bg1, REVIEW)
    bg1.execute("UPDATE batches SET status = 'deferred' WHERE id = 'bg_1'")
    where, waits = _shift_rows(bg1)
    assert where == (
        "Where it stands: approved. The change bg_1 is built, and all 35 of its "
        "tests pass. Its review stopped after 3 attempts with no verdict.")
    assert "nothing from you" not in waits, waits
    assert waits == "What it waits on: a new start of its review."


def test_a_shift_row_with_no_quarantined_key_renders_as_before(bg1):
    where, waits = _shift_rows(bg1)
    assert where == ("Where it stands: approved. The change bg_1 is built, and "
                     "all 35 of its tests pass.")
    assert waits == "What it waits on: nothing from you."


def test_the_park_scenes_shift_row_shows_no_tick_name(tmp_path):
    """Review 1, finding 1: the park scene's row said "a new start of
    tests_failing", and night 160's copy said "a new start of do:preempt"."""
    from rota.roles.principal import _shift_waits, _shift_where
    from rota.testkit.scenes import park

    sc = park(tmp_path)
    sc.conn.execute("INSERT OR REPLACE INTO tick_attempts (tick_key, attempts, "
                    "quarantined, reported) VALUES ('-|do:preempt|b1,b2', 3, 1, 1)")
    row = _shift_where(sc.conn, "i1") + " " + _shift_waits(sc.conn, "i1")
    for name in ("tests_failing", "do:", "preempt", "tick", "_"):
        assert name not in row, row
    assert "the tests still fail" in row, row
    assert "the change was set aside" in row, row


START ="developer|tick:batch_start|bg_1"
NOTE = ("This write removes or rewrites 1 statement that your text does not "
        "hold: `return` at line 609.")


def _refused_start(db) -> None:
    """Night 163's m115 shape: three Developer attempts on the start tick
    wrote `termui.py`, the note door refused each commit at line 609, and
    nothing was committed. The `drop_notes` row is the door's own record."""
    db.execute("UPDATE batches SET head_commit = NULL WHERE id = 'bg_1'")
    for k, sid in enumerate(("s221", "s229", "s238")):
        db.execute("INSERT INTO sessions (id, role, seq, wake_kind, wake_refs) "
                   "VALUES (?, 'developer', ?, 'tick:batch_start', '[\"bg_1\"]')",
                   (sid, k + 1))
        db.execute("INSERT INTO tool_calls (session_id, fn, args_summary, seq) "
                   "VALUES (?, 'code.write', ?, 13)",
                   (sid, "end=613, path='src/click/termui.py', start=601, "
                         "text='def clear() -> bool:"))
        db.execute("INSERT INTO tool_calls (session_id, fn, args_summary, seq) "
                   "VALUES (?, 'code.commit', 'message=''Implement clear()''', 14)",
                   (sid,))
    # s254's write: the bare `return` under the isatty check became
    # `return False`, which the criteria ask for (review w5, finding 1).
    db.execute("INSERT INTO drop_notes (batch_id, path, status, note, lines, noted) "
               "VALUES ('bg_1', 'src/click/termui.py', 'restored', ?, "
               "'[[\"clear\", \"return\", 1]]', ?)", (NOTE, NOTED))
    _quarantine(db, START)


NOTED = ("import sys\n\n\ndef clear() -> bool:\n"
         "    if not isatty(sys.stdout):\n        return False\n"
         "    sys.stdout.write('\\033[2J')\n    return True\n")


def test_m115_offers_no_sentence_to_copy(bg1):
    """Frame 339: the commit door no longer refuses a removal, so no stop
    comes from one, and the page asks him for no permission. Night 169's
    m36 offered "To allow that, say so, as ...", and his m37 did not copy
    it. The page shows the stop and the checks as for any other stop."""
    _refused_start(bg1)
    page = render_page(bg1, "present", M45_REFS, stalled=[START])[0]
    assert "The team gave up: the change could not start after 3 attempts." in page
    for gone in ("A check refused", "To allow that, say so",
                 "the runner put the file back"):
        assert gone not in page, page
    for name in ("drop_notes", "code.write", "tick", "note door"):
        assert name not in page, page


def test_an_answer_to_the_page_lifts_the_start_key_once(bg1):
    """Finding 2: a landed answer on the stopped page lifts the quarantined
    Developer start key, and only that key."""
    import json

    from rota.roles.principal import Answer, Ask, land

    _refused_start(bg1)
    other = "tester|tick:tests_missing|bg_1"
    _quarantine(bg1, other)
    for mid in ("m115", "m116"):
        bg1.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                    "body_refs, seq, status) VALUES (?, 't1', 'liaison', "
                    "'principal', 'present', ?, ?, 'open')",
                    (mid, json.dumps(M45_REFS), int(mid[1:])))
        bg1.execute("INSERT INTO config (key, value) VALUES (?, ?)",
                    (f"stalled:{mid}", json.dumps([START, other])))
    answer = Answer(verb="verdict", text="Remove the return at line 609 in clear().",
                    per_item={"echo_json_helper": "approve"})
    # An all-approve on a stopped page returns None, as m35 did, and still
    # closes the page.
    land(bg1, Ask(message_id="m115", verb="present", refs=M45_REFS), answer)
    assert bg1.execute("SELECT status FROM messages WHERE id = 'm115'"
                       ).fetchone()["status"] == "answered"
    keys = {r["tick_key"] for r in bg1.execute("SELECT tick_key FROM tick_attempts")}
    assert keys == {other}, keys
    # The key quarantines again, and a second answer to the same page lands
    # nothing, so it lifts nothing.
    _quarantine(bg1, START)
    assert land(bg1, Ask(message_id="m115", verb="present", refs=M45_REFS),
                answer) is None
    assert bg1.execute("SELECT 1 FROM tick_attempts WHERE tick_key = ?",
                       (START,)).fetchone()


def test_a_start_with_no_refused_write_keeps_the_stopped_work_page(bg1):
    """A start tick whose attempts wrote nothing shows no refusal lines."""
    _quarantine(bg1, START)
    page = render_page(bg1, "present", M45_REFS, stalled=[START])[0]
    assert page.startswith("The team stopped work on this change."), page
    assert "A check refused" not in page, page


def test_the_next_start_window_holds_his_answer(bg1):
    """Review w5, re-check: the page says the team reads his words, so the
    Developer's next start window holds the landed ruling's words."""
    import json

    from rota.core.runner import START_RULED_KEY, push_working_set
    from rota.core.sandbox import build
    from rota.core.scheduler import Wake
    from rota.roles import prompts
    from rota.roles.principal import apply_rulings

    _refused_start(bg1)
    words = "Remove the return at line 609 in clear(). It returns False there."
    bg1.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                "body_refs, seq, status) VALUES ('m115', 't1', 'liaison', "
                "'principal', 'present', ?, 115, 'open')", (json.dumps(M45_REFS),))
    bg1.execute("INSERT INTO config (key, value) VALUES ('stalled:m115', ?)",
                (json.dumps([START]),))
    # His reply reaches the Liaison, whose `rulings.rule` stages the row,
    # and `apply_rulings` lands it through `land`.
    bg1.execute("INSERT INTO rulings (id, ask_id, per_item, words, status) VALUES "
                "('r_m115', 'm115', '{\"echo_json_helper\": \"approve\"}', ?, "
                "'open')", (words,))
    backfill_ruled_refs(bg1)
    apply_rulings(bg1)
    assert not bg1.execute("SELECT 1 FROM tick_attempts WHERE tick_key = ?",
                           (START,)).fetchone()
    sb = build("developer", bg1, batch_id="bg_1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    pushed = push_working_set("developer", sb,
                              Wake("developer", "tick:batch_start", refs=("bg_1",)))
    assert words in str(pushed.get(START_RULED_KEY)), list(pushed)
