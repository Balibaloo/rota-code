"""Frame 306, pass 1b: his drops and his added line on a criteria page land.

Night 163's m111 listed the criteria of `clear()`. His reply m112 said to
delete line 5, change line 6, delete line 7 and add a line. Six rounds
changed nothing: no op retired a criterion, and no route added one. The rows
below are the night's, copied from `.rota/clickI_night163.db`.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import SessionResult, backfill_ruled_refs, init_db, session_commit
from rota.testkit.fixtures import seed_acts
from rota.core.runner import _as_write, _page_act_lines, _wake_allow
from rota.core.sandbox import build
from rota.core.scheduler import Wake
from rota.roles import prompts
from rota.roles.principal import request_rows
from rota.testkit.fixtures import seed_verdict

ITEM = "clear_returns_bool"
TICKET = "tk_1_clear_returns_bool"
CRITERIA = {
    "c1_clear_terminal": "clear() returns True if the screen was cleared, "
                         "False otherwise.",
    "c1_clear_terminal_check": "clear() returns True if and only if the "
                               "current stdout is a terminal.",
    "c2_non_terminal_false": "clear() returns False when stdout is not a "
                             "terminal.",
    "c3_no_terminal_true": "clear() returns False when stdout is not a "
                           "terminal.",
    "c3_terminal_check": "clear() determines terminal status by inspecting "
                         "the underlying stream object passed to it.",
    "c3_terminal_failure_true": "clear() returns False when the clear "
                                "operation fails, provided no exception is "
                                "raised.",
    "c3_terminal_true": "clear() returns True when the current stdout is a "
                        "terminal and the clear operation succeeds.",
}
PAGE = [ITEM, *CRITERIA, "bg_2"]
WORDS = ("Please delete line 5, because it repeats line 4. Change line 6 to "
         "say that clear() checks the current stdout, since nothing is passed "
         "to it, and delete line 7, since a failed clear is not part of what I "
         "asked for. Also add a line that says the output stays exactly the "
         "same as today, and the rest is fine.")
CONTESTED = ["c3_no_terminal_true", "c3_terminal_check",
             "c3_terminal_failure_true"]
VERDICT = {"c3_no_terminal_true": "contest", "c3_terminal_check": "revise",
           "c3_terminal_failure_true": "contest"}
ADDED = "the output stays exactly the same as today"


def _message(conn, mid, cause, sender, to, verb, refs, seq, text=None):
    conn.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
                 "to_role, verb, body_refs, body_text, seq) VALUES "
                 "(?, ?, 'm111', ?, ?, ?, ?, ?, ?)",
                 (mid, cause, sender, to, verb, json.dumps(refs), text, seq))


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES (?, 'clear() returns True when it cleared "
                 "the screen and False when stdout is not a terminal.', "
                 "'in_scope', 'approved', 1, 1)", (ITEM,))
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, ?, "
                 "'clear returns a bool')", (TICKET, ITEM))
    for cid, text in CRITERIA.items():
        conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                     "(?, ?, ?)", (cid, TICKET, text))
    refs = ["bg_2", *CRITERIA, ITEM]
    _message(conn, "m111", None, "liaison", "principal", "present", refs, 111)
    _message(conn, "m112", "m111", "principal", "liaison", "converse", refs,
             112, WORDS)
    _message(conn, "m113", "m111", "principal", "liaison", "verdict",
             CONTESTED, 113)
    _message(conn, "m114", "m113", "liaison", "terminologist", "relay",
             CONTESTED, 114)
    seed_verdict(conn, "m113", json.dumps(VERDICT))
    conn.execute("INSERT INTO config (key, value) VALUES ('order:m112', ?)",
                 (json.dumps(PAGE),))
    per_item = {r: VERDICT.get(r, "approve") for r in PAGE}
    conn.execute("INSERT INTO rulings (id, ask_id, reply_id, per_item, words, "
                 "status, verdict_id, texts) VALUES ('r_fae8c0a559', 'm111', "
                 "'m112', ?, ?, 'landed', 'm113', ?)",
                 (json.dumps(per_item), WORDS,
                  json.dumps({c: CRITERIA[c] for c in CONTESTED})))
    backfill_ruled_refs(conn)
    # The Liaison's reading of m112 as the object form writes it: lines 5
    # and 7 drop, line 6 is rewritten, and the ticket gets the added line
    # (the seam design, pass 4).
    seed_acts(conn, "r_fae8c0a559", {
        "c3_no_terminal_true": {"act": "drop", "target_kind": "row"},
        "c3_terminal_check": {"act": "rewrite", "target_kind": "row"},
        "c3_terminal_failure_true": {"act": "drop", "target_kind": "row"},
        TICKET: {"verdict": "revise", "act": "add", "target": TICKET,
                 "words": ADDED}})
    return conn


def _repair(conn):
    sb = build("terminologist", conn, mode="criterion_repair",
               session_id="s226", allow=_wake_allow(_wake(), conn))
    sb.ctx.trigger = "m114"
    return sb


def _wake():
    return Wake("terminologist", "message", message_id="m114",
                refs=tuple(CONTESTED), detail="relay")


def _commit(conn, sb, sid):
    session_commit(conn, SessionResult(
        session_id=sid, role="terminologist",
        writes=[_as_write(w) for w in sb.ctx.writes]))


def test_his_drop_of_lines_5_and_7_retires_both_rows(db):
    sb = _repair(db)
    sb.call("criteria.retire", id="c3_no_terminal_true")
    sb.call("criteria.retire", id="c3_terminal_failure_true")
    _commit(db, sb, "s226")
    rows = dict(db.execute("SELECT id, retired_by FROM criteria").fetchall())
    assert rows["c3_no_terminal_true"] == "r_fae8c0a559"
    assert rows["c3_terminal_failure_true"] == "r_fae8c0a559"
    assert rows["c3_terminal_check"] is None, "line 6 is a rewrite, no drop"
    shown = request_rows(db, [ITEM])
    assert "c3_no_terminal_true" not in shown
    assert "c3_terminal_failure_true" not in shown
    assert "c3_terminal_check" in shown


def test_a_criterion_he_did_not_drop_is_not_retired(db):
    sb = _repair(db)
    with pytest.raises(ValueError, match="no ruling of the principal drops"):
        sb.call("criteria.retire", id="c3_terminal_check")
    with pytest.raises(ValueError, match="no ruling of the principal drops"):
        sb.call("criteria.retire", id="c1_clear_terminal")


def test_six_criteria_with_one_retired_admit_a_seventh(db):
    """Six rows of which one is retired are five live criteria. The cap
    refuses a seventh live criterion, so it still counts live rows only."""
    db.execute("DELETE FROM criteria WHERE id = 'c3_terminal_true'")
    db.execute("UPDATE criteria SET retired_by = 'r_fae8c0a559' "
               "WHERE id = 'c3_no_terminal_true'")
    db.commit()
    live = db.execute("SELECT COUNT(*) FROM criteria WHERE ticket_id = ? AND "
                      "retired_by IS NULL", (TICKET,)).fetchone()[0]
    assert live == 5
    sb = build("terminologist", db, mode="criteria",
               allow=prompts.mode_tools("terminologist", "criteria"))
    sb.call("criteria.specify", id="c8_output_same", ticket_id=TICKET,
            text="The output of clear() stays exactly the same as today.")


def test_the_relay_wake_offers_specify_and_names_the_added_sentence(db):
    allow = _wake_allow(_wake(), db)
    assert "criteria.specify" in allow
    assert "criteria.retire" in allow
    lines = "\n".join(_page_act_lines(_wake(), db))
    assert ADDED in lines and TICKET in lines
    assert "c3_no_terminal_true" in lines and "c3_terminal_failure_true" in lines


def test_a_relay_with_no_drop_and_no_added_line_keeps_the_mode_tools(db):
    """A ruling whose only act is a rewrite drops and adds nothing, so the
    wake keeps the mode's tools (pass 4: the act decides, not the words)."""
    db.execute("DELETE FROM ruled_refs WHERE ref = ?", (TICKET,))
    seed_acts(db, "r_fae8c0a559", {
        "c3_no_terminal_true": {"act": None},
        "c3_terminal_failure_true": {"act": None}})
    assert _wake_allow(_wake(), db) == prompts.mode_tools(
        "terminologist", "criterion_repair")
    assert _page_act_lines(_wake(), db) == []


# Pass 1c: no seat that judges, tests or merges reads a retired criterion.
RETIRED = "c3_no_terminal_true"


def _batch(conn):
    conn.execute("INSERT INTO batches (id, item_id, head_commit, status) "
                 "VALUES ('bg_2', ?, 'abc123', 'running')", (ITEM,))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_2', ?)", (TICKET,))
    for n, cid in enumerate(c for c in CRITERIA if c != RETIRED):
        conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, "
                     "body) VALUES (?, 'bg_2', ?, 'tests/test_clear.py', "
                     "'assert True')", (f"tst{n}", cid))
    conn.execute("UPDATE criteria SET retired_by = 'r_fae8c0a559' WHERE id = ?",
                 (RETIRED,))
    conn.commit()


def test_a_retired_criterion_holds_no_merge(db):
    from rota.core.lifecycle import mergeable

    _batch(db)
    assert "criteria without a test" not in (mergeable(db, "bg_2") or "")


def test_the_critics_load_shows_no_retired_line(db):
    _batch(db)
    sb = build("critic", db, batch_id="bg_2", mode="review",
               allow=prompts.mode_tools("critic", "review"))
    ids = {r["id"] for r in sb.call("criteria.load")}
    assert RETIRED not in ids and "c3_terminal_check" in ids


def test_the_tester_encodes_only_live_criteria(db):
    _batch(db)
    db.execute("DELETE FROM tests")
    db.commit()
    sb = build("tester", db, batch_id="bg_2", mode="challenge",
               allow=prompts.mode_tools("tester", "challenge"))
    ids = {r["id"] for r in sb.call("criteria.load")}
    assert RETIRED not in ids
    with pytest.raises(ValueError, match="is retired"):
        sb.call("tests.encode", id="tst_x", criterion_id=RETIRED,
                path="tests/test_clear.py", body="def test_x():\n    pass\n")


# Pass 2: the findings of the review of 1464cfb7.
ADDED_SENTENCE = "The output of clear() stays exactly the same as today."


def test_one_relay_session_retires_rewrites_and_adds(db):
    """Finding 1: the cap counts the retires staged in the same session."""
    sb = _repair(db)
    sb.call("criteria.retire", id="c3_no_terminal_true")
    sb.call("criteria.retire", id="c3_terminal_failure_true")
    sb.call("criteria.respecify", id="c3_terminal_check",
            text="clear() determines terminal status by inspecting the "
                 "current sys.stdout.")
    sb.call("criteria.specify", id="c8_output_same", ticket_id=TICKET,
            text=ADDED_SENTENCE)
    _commit(db, sb, "s226")
    shown = [r for r in request_rows(db, [ITEM]) if r in CRITERIA
             or r == "c8_output_same"]
    assert len(shown) == 6 and "c8_output_same" in shown


def test_a_retire_moves_no_version(db):
    """Finding 3: the park ask id reads the versions, so a retire keeps them."""
    sb = _repair(db)
    sb.call("criteria.retire", id="c3_no_terminal_true")
    _commit(db, sb, "s226")
    assert db.execute("SELECT version FROM criteria WHERE id = "
                      "'c3_no_terminal_true'").fetchone()[0] == 1


def test_a_red_test_of_a_retired_criterion_holds_no_merge_and_no_park(db):
    """Finding 2: the readers of a red test skip a retired criterion."""
    from rota.core.lifecycle import mergeable
    from rota.core.scheduler import park_criteria, park_reds, park_rows

    _batch(db)
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst_old', 'bg_2', ?, 'tests/test_clear.py', "
               "'assert 0')", (RETIRED,))
    db.execute("INSERT INTO test_runs (test_id, batch_id, result, output, "
               "commit_sha) VALUES ('tst_old', 'bg_2', 'fail', 'E boom', "
               "'abc123')")
    # A passing verdict takes `mergeable` past its earlier holds to the reds.
    db.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result) "
               "VALUES ('v1', 'bg_2', 'abc123', 'pass')")
    db.commit()
    own, _ = park_reds(db, "bg_2")
    assert own == []
    assert park_rows(db, "bg_2") == ["bg_2"]
    assert RETIRED not in park_criteria(db, "bg_2")
    assert "not passing" not in (mergeable(db, "bg_2") or "")
    assert db.execute("SELECT 1 FROM tests WHERE id = 'tst_old'").fetchone()


@pytest.mark.parametrize("acts, texts", [
    ({TICKET: {"verdict": "revise", "act": "add", "words": "X stays"}},
     ["X stays"]),
    ({"c3_no_terminal_true": {"act": "add", "words": "Y holds"}}, ["Y holds"]),
    ({TICKET: {"verdict": "revise", "act": "add"}}, [WORDS]),
    ({TICKET: {"verdict": "revise", "words": "X stays"}}, []),
])
def test_the_added_lines_are_the_add_rows(db, acts, texts):
    """Pass 4, P8: a line he adds is the act `add` of a row on the criterion
    or its ticket, with the row's words as the line. A row with no act adds
    nothing, whatever its words say."""
    from rota.roles.api import criteria_page_acts

    db.execute("DELETE FROM ruled_refs WHERE ref = ?", (TICKET,))
    seed_acts(db, "r_fae8c0a559", acts)
    out = criteria_page_acts(db, CONTESTED)
    assert [s for _, s in out["add"]] == texts
    assert all(t == TICKET for t, _ in out["add"])


def test_a_retire_needs_the_relay_wake(db):
    """Finding 5: the door checks the wake as well as the ruling."""
    sb = _repair(db)
    sb.ctx.trigger = "m112"
    with pytest.raises(ValueError, match="relay"):
        sb.call("criteria.retire", id="c3_no_terminal_true")


def test_a_retired_rows_words_may_return_under_a_new_id(db):
    """Finding 6: same ticket, same words, one live row."""
    db.execute("UPDATE criteria SET retired_by = 'r_fae8c0a559' WHERE id = ?",
               (RETIRED,))
    db.execute("DELETE FROM criteria WHERE id IN ('c2_non_terminal_false', "
               "'c3_terminal_true')")
    db.commit()
    sb = build("terminologist", db, mode="criteria",
               allow=prompts.mode_tools("terminologist", "criteria"))
    sb.call("criteria.specify", id="c9_back", ticket_id=TICKET,
            text=CRITERIA[RETIRED])


# Pass 2b: a red test of a retired criterion wakes no fix and no ladder.
def _old_red(conn, attempt):
    _batch(conn)
    for n, cid in enumerate(c for c in CRITERIA if c != RETIRED):
        conn.execute("INSERT INTO test_runs (test_id, batch_id, result, "
                     "commit_sha, attempt) VALUES (?, 'bg_2', 'pass', "
                     "'abc123', ?)", (f"tst{n}", attempt))
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                 "VALUES ('tst_old', 'bg_2', ?, 'tests/test_clear.py', "
                 "'assert 0')", (RETIRED,))
    conn.execute("INSERT INTO test_runs (test_id, batch_id, result, output, "
                 "commit_sha, attempt) VALUES ('tst_old', 'bg_2', 'fail', "
                 "'E boom', 'abc123', ?)", (attempt,))
    conn.commit()


def test_a_retired_red_wakes_no_developer_and_no_ladder(db):
    from rota.core import harness
    from rota.core.predicates import exhausted, harness as owed, tests_failing
    from rota.core.scheduler import failing_attempt

    _old_red(db, 1)
    assert not [w for w in tests_failing(db) if "bg_2" in w.refs]
    assert failing_attempt(db, "bg_2") == 0
    assert not [w for w in owed(db) if "bg_2" in w.refs]
    assert "tst_old" not in {t["id"] for t in harness.live_tests_for(db, "bg_2")}
    db.execute("UPDATE test_runs SET attempt = 99")
    db.commit()
    assert not [w for w in exhausted(db) if "bg_2" in w.refs]


def test_the_tester_triages_no_retired_criterion(db):
    _batch(db)
    sb = build("tester", db, batch_id="bg_2", mode="tests_missing",
               allow=prompts.mode_tools("tester", "tests_missing"))
    with pytest.raises(ValueError, match="is retired"):
        sb.call("tests.triage", criterion_id=RETIRED, verdict="encodable")


# Night 164's W-C: bg_1 was green at 37 of 37 from 21:41. His m37 retired
# c3, c4 and c6. `review` still counted them as owed a test, so no Critic woke.
def _green_with_retired(conn, untested=()):
    conn.execute("INSERT INTO batches (id, item_id, head_commit, status) "
                 "VALUES ('bg_2', ?, 'abc123', 'running')", (ITEM,))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_2', ?)", (TICKET,))
    live = [c for c in CRITERIA if c not in CONTESTED and c not in untested]
    for n, cid in enumerate(live):
        conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, "
                     "body) VALUES (?, 'bg_2', ?, 'tests/test_clear.py', "
                     "'assert True')", (f"tst{n}", cid))
        conn.execute("INSERT INTO test_runs (test_id, batch_id, result, "
                     "commit_sha, attempt) VALUES (?, 'bg_2', 'pass', "
                     "'abc123', 1)", (f"tst{n}",))
    conn.executemany("UPDATE criteria SET retired_by = 'r_2131db161c' "
                     "WHERE id = ?", [(c,) for c in CONTESTED])
    conn.commit()


def test_three_retired_criteria_hold_no_review(db):
    from rota.core.predicates import review, tests_missing

    _green_with_retired(db)
    assert not [w for w in tests_missing(db) if "bg_2" in w.refs]
    assert [w.kind for w in review(db) if "bg_2" in w.refs] == ["tick:review"]


def test_a_live_criterion_with_no_test_still_holds_review(db):
    from rota.core.predicates import review

    _green_with_retired(db, untested=("c1_clear_terminal",))
    assert not [w for w in review(db) if "bg_2" in w.refs]
