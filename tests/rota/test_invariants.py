"""
The invariants of frame 144, item 4 (`rota/tools/invariants.py`).

Each test takes the end of the scene `merged_then_next`, a merged b1 and a
running b2, copies the database, changes one row, and asserts the finding
that the change adds. The scene's end breaks I4 today (frame 130), so each
test compares the copy with the scene and reads only what the change adds.
The scene tests run the same checker on every scene's end.
"""
from __future__ import annotations

import sqlite3

import pytest

from rota.core import harness, scheduler
from rota.testkit import scenes
from rota.tools import invariants


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    sc = scenes.build("merged_then_next", tmp_path_factory.mktemp("invariants"))
    yield sc
    sc.close()


def _copy(sc) -> sqlite3.Connection:
    copy = sqlite3.connect(":memory:")
    copy.row_factory = sqlite3.Row
    sc.conn.backup(copy)
    copy.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('project_root', ?)",
                 (str(sc.repo.root),))
    return copy


def added(sc, sql: str, args: tuple = ()) -> list[str]:
    """The findings that one changed row adds to the scene's end."""
    return added_all(sc, (sql, args))


def added_all(sc, *changes: tuple[str, tuple], check=None) -> list[str]:
    """The findings that several changed rows add to the scene's end. The
    `check` callable reads the copy first, so a test can prove its state."""
    before = {str(f) for f in invariants.check(sc.conn)}
    copy = _copy(sc)
    for sql, args in changes:
        copy.execute(sql, args)
    if check is not None:
        check(copy)
    return sorted(str(f) for f in invariants.check(copy) if str(f) not in before)


def test_the_scenes_end_breaks_only_the_known_invariant(built):
    found = {f.invariant for f in invariants.check(built.conn)}
    assert found == {"I4"}, [str(f) for f in invariants.check(built.conn)]


def test_i1_a_second_test_on_a_criterion(built):
    # In b2, which runs. A new test of the merged b1 has no run at its head,
    # and I3 finds that too.
    assert added(built, "INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                        "VALUES ('t9', 'b2', 'c1', 'test_nine.py', '')") == [
        "I1: criterion c1 holds 2 tests: t1,t9"]


def test_i2_an_inherited_row_with_a_criterion(built):
    # c2 has no test yet. On c1 the row would be t1's second, and I1 finds
    # that too.
    tid = harness.inherited_id("tests/test_charges.py")
    assert added(built, "UPDATE tests SET criterion_id = 'c2' WHERE id = ?", (tid,)) == [
        f"I2: {tid} holds criterion c2"]


def test_i2_an_inherited_row_whose_body_is_not_the_file(built):
    tid = harness.inherited_id("tests/test_charges.py")
    got = added(built, "UPDATE tests SET body = body || '# changed' WHERE id = ?", (tid,))
    assert len(got) == 1 and got[0].startswith(
        f"I2: {tid}: its body is not tests/test_charges.py at b2's base "), got


def test_i3_a_merged_batch_with_a_red_run_at_its_head(built):
    assert added(built, "UPDATE test_runs SET result = 'fail' WHERE rowid = ("
                        "SELECT MAX(r.rowid) FROM test_runs r JOIN batches b ON b.id = r.batch_id "
                        "WHERE r.test_id = 't1' AND r.commit_sha = b.head_commit)") == [
        "I3: merged b1: t1's latest run at its head is fail"]


def test_i4_a_run_of_another_batchs_test(built):
    # A run of b2 renamed to t1. Moving t1's own run to b2 would leave the
    # merged b1 with no run of t1 at its head, and I3 finds that too.
    assert added(built, "UPDATE test_runs SET test_id = 't1' WHERE rowid = ("
                        "SELECT MIN(rowid) FROM test_runs WHERE batch_id = 'b2')") == [
        "I4: 1 run(s) of b2 name t1, which is a test of b1"]


def test_i5_an_open_park_ask_on_a_batch_that_is_not_parked(built):
    ask = "m_park_0123456789_b2"
    assert added(built, "INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                        "body_refs, seq) VALUES (?, 't_park', 'liaison', 'principal', "
                        "'clarify', '[\"i2\"]', 9999)", (ask,)) == [
        f"I5: open park ask {ask} names b2, which owes no ask"]


def test_i5_a_batch_parked_on_a_quarantined_key_with_no_ask(built):
    assert added_all(built,
                     ("UPDATE batches SET status = 'deferred' WHERE id = 'b2'", ()),
                     ("INSERT INTO tick_attempts (tick_key, attempts, quarantined, reported) "
                      "VALUES ('developer|tick:tests_failing|b2', 3, 1, 1)", ())) == [
        "I5: b2, parked and given up on, holds 0 open park asks"]


def test_i5_a_batch_past_the_loop_cap_with_a_red_head_owes_an_ask(built):
    # A loop-cap park with a red run at its head owes the park page, point 3
    # of the ruling of 2026-10-08, since frame 330's pass 3. Dry1 turn 14's
    # bg_1 is this park. Before that pass the park climbed the ladder and owed
    # no ask (the delta review of b43b99d6, night 126's bg_1).
    def is_parked_with_no_key(copy):
        assert scheduler.parked(copy, "b2") and not scheduler.given_up(copy, "b2")
        assert scheduler.gave_up(copy, "b2")

    assert added_all(built,
                     ("UPDATE batches SET status = 'deferred' WHERE id = 'b2'", ()),
                     ("UPDATE test_runs SET result = 'fail', attempt = 10, commit_sha = "
                      "(SELECT head_commit FROM batches WHERE id = 'b2') "
                      "WHERE rowid = (SELECT MAX(rowid) FROM test_runs WHERE batch_id = 'b2')",
                      ()),
                     check=is_parked_with_no_key) == [
        "I5: b2, parked and given up on, holds 0 open park asks"]


def test_i5_a_batch_past_the_loop_cap_with_a_green_head_owes_no_ask(built):
    # Past the cap with every run at the head green, the batch is not parked
    # (review p3 of frame 330, point 4), so no ask is owed.
    def is_not_parked(copy):
        assert not scheduler.parked(copy, "b2") and not scheduler.gave_up(copy, "b2")

    assert added_all(built,
                     ("UPDATE batches SET status = 'deferred' WHERE id = 'b2'", ()),
                     ("UPDATE test_runs SET result = 'pass', attempt = 10, commit_sha = "
                      "(SELECT head_commit FROM batches WHERE id = 'b2') "
                      "WHERE batch_id = 'b2'", ()),
                     check=is_not_parked) == []


def test_i6_a_quarantined_key_on_a_merged_batch(built):
    assert added(built, "INSERT INTO tick_attempts (tick_key, attempts, quarantined, reported) "
                        "VALUES ('developer|tick:tests_failing|b1', 3, 1, 1)") == [
        "I6: quarantined developer|tick:tests_failing|b1 names merged b1"]


def test_i7_two_batches_run(built):
    assert added(built, "INSERT INTO batches (id, item_id, status) "
                        "VALUES ('b9', 'i1', 'running')") == [
        "I7: 2 batches run: ['b2', 'b9']"]


def test_i8_two_open_batches_on_one_item(built):
    assert added(built, "INSERT INTO batches (id, item_id, status) "
                        "VALUES ('b9', 'i2', 'pending')") == [
        "I8: item i2 has 2 open batches: b2,b9"]


def test_i9_an_answered_question_with_no_answer(built):
    assert added(built, "INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                        "body_refs, seq, status) VALUES ('m_q', 't_q', 'tester', "
                        "'terminologist', 'question', '[\"c1\"]', 9999, 'answered')") == [
        "I9: m_q, tester to terminologist question, is answered and nothing answers it"]


def test_i9_a_relay_needs_no_answer_row(built):
    # A relay carries material, so the session that reads it answers it.
    assert added(built, "INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                        "body_refs, seq, status) VALUES ('m_r', 't_r', 'liaison', "
                        "'vision_keeper', 'relay', '[\"i1\"]', 9999, 'answered')") == []


_CHALLENGE = ("INSERT INTO messages (id, thread_id, from_role, to_role, verb, body_refs, "
              "seq, status) VALUES ('m_c', 't_c', 'critic', 'tester', 'challenge', "
              "'[\"c1\", \"t1\"]', 9999, 'answered')", ())


def test_i9_a_challenge_on_a_test_replaced_before_it(built):
    # t1 is at version 2 from an earlier replace, and nothing follows the
    # challenge. The review's tamper X2 of b43b99d6 survived this.
    assert added_all(built, ("UPDATE tests SET version = 2 WHERE id = 't1'", ()),
                     _CHALLENGE) == [
        "I9: m_c, critic to tester challenge, is answered and nothing answers it"]


def _session(sid: str, trigger: str | None, seq: int) -> tuple[str, tuple]:
    return ("INSERT INTO sessions (id, role, trigger_msg, committed, seq) "
            "VALUES (?, 'tester', ?, 1, ?)", (sid, trigger, seq))


def _receipt(sid: str, test: str, new_version: int) -> tuple[str, tuple]:
    return ("INSERT INTO receipts (session_id, table_name, row_id, new_version) "
            "VALUES (?, 'tests', ?, ?)", (sid, test, new_version))


def test_i9_a_challenge_answered_by_the_replace_it_woke(built):
    # s_a stored t1 first, and s_c, which the challenge woke, replaced it.
    assert added_all(built, ("UPDATE tests SET version = 2 WHERE id = 't1'", ()),
                     _CHALLENGE, _session("s_a", None, 9998), _receipt("s_a", "t1", 9000),
                     _session("s_c", "m_c", 9999), _receipt("s_c", "t1", 9001)) == []


def test_i9_a_woken_session_that_writes_no_receipt_on_the_test(built):
    # The session ran and committed, and wrote nothing on t1. A session
    # alone is no replace (the review of 96fe3425, its second low).
    assert added_all(built, ("UPDATE tests SET version = 2 WHERE id = 't1'", ()),
                     _CHALLENGE, _session("s_c", "m_c", 9999)) == [
        "I9: m_c, critic to tester challenge, is answered and nothing answers it"]


def test_i9_a_woken_session_that_creates_the_test_does_not_replace_it(built):
    # s_c, which the challenge woke, created t9 at version 1. s_d replaced
    # it later, so t9 stands at version 2, and the woken write was no
    # replace (the review of 96fe3425, its fourth low).
    challenge = ("INSERT INTO messages (id, thread_id, from_role, to_role, verb, body_refs, "
                 "seq, status) VALUES ('m_c', 't_c', 'critic', 'tester', 'challenge', "
                 "'[\"c2\", \"t9\"]', 9999, 'answered')", ())
    assert added_all(built, challenge,
                     ("INSERT INTO tests (id, batch_id, criterion_id, path, body, version) "
                      "VALUES ('t9', 'b2', 'c2', 'test_nine.py', '', 2)", ()),
                     _session("s_c", "m_c", 9999), _receipt("s_c", "t9", 9000),
                     _session("s_d", None, 10000), _receipt("s_d", "t9", 9001)) == [
        "I9: m_c, critic to tester challenge, is answered and nothing answers it"]


def test_i10_a_word_in_an_integer_column(built):
    # Night 126's s249 wrote this through `problem.prioritize`, and the next
    # `loop.step` crashed in `next_batch` (frame 164).
    rowid = built.conn.execute("SELECT rowid FROM items WHERE id = 'i2'").fetchone()[0]
    assert added(built, "UPDATE items SET priority = 'high' WHERE id = 'i2'") == [
        f"I10: items.priority rowid {rowid} holds text 'high'"]


def test_a_night_is_checked_by_path_and_left_as_it_was(built, tmp_path, capsys):
    path = tmp_path / "night.db"
    disk = sqlite3.connect(path)
    built.conn.backup(disk)
    disk.close()
    before = path.read_bytes()
    assert invariants.main([str(path)]) == 1
    out = capsys.readouterr().out
    assert "I4" in out and out.rstrip().endswith("finding(s)"), out
    assert path.read_bytes() == before
    assert sorted(p.name for p in tmp_path.iterdir()) == ["night.db"]
