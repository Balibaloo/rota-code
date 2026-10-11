"""
The night report prints the rows a night's read asks for.

The build session read each night's run database on an agent for 85k to
103k tokens (observed: frame 105's brief, 2026-10-01). These pins hold the
lines that the read leans on: the batch and its head history, one wake line
per session, the head verdict apart from the old one, and a door phrase
counted once per turn whose newest feedback holds it. The frame 105 diff
review (2026-10-01) added the pins for absent tables, receipt sessions, runs
that hide a session, and the completion line's first turn.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.tools import nightreport

OLD = "a" * 40
HEAD = "b" * 40
CALL = "TOOL: code.commit()"


def _feedback(sha: str) -> str:
    return f'OK code.commit -> {{"committed": true, "head_commit": "{sha}", "touched": ["x.py"]}}'


def _session(conn, sid, role, seq, kind, refs="[]", committed=1):
    conn.execute("INSERT INTO sessions (id, role, committed, seq, wake_kind, wake_refs) "
                 "VALUES (?, ?, ?, ?, ?, ?)", (sid, role, committed, seq, kind, refs))


def _turn(conn, sid, seq, user, completion, system="sys"):
    conn.execute("INSERT INTO turns (session_id, seq, system, user, completion) "
                 "VALUES (?, ?, ?, ?, ?)", (sid, seq, system, user, completion))


def _night(tmp_path):
    conn = init_db(tmp_path / "night.db")
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("INSERT INTO items (id, text, kind) VALUES ('it_1', ?, 'in_scope')",
                 ("Add an echo_json helper " + "that prints compact JSON " * 6,))
    conn.execute("INSERT INTO batches (id, item_id, head_commit, status) "
                 "VALUES ('bg_1', 'it_1', ?, 'running')", (HEAD,))
    _session(conn, "s1", "developer", 1, "tick:batch_start", '["bg_1"]')
    _session(conn, "s2", "tester", 2, "tick:tests_missing", '["bg_1"]', committed=0)
    # The prompt repeats the earlier turns, and each turn's prompt holds the
    # previous completion. Turn 2's newest feedback holds no copy of the phrase.
    p1 = "wake. dropped to fit the window"
    p2 = p1 + "\n\n" + CALL + "\n\n" + _feedback(OLD)
    p3 = p2 + "\n\n" + CALL + "\n\n" + _feedback(HEAD) + "\ndropped to fit the window"
    for seq, user in ((1, p1), (2, p2), (3, p3)):
        _turn(conn, "s1", seq, user, CALL)
    _turn(conn, "s2", 1, "", "SESSION FAILED: the model returned no call", system="")
    conn.execute("INSERT INTO tool_calls (session_id, fn, args_summary, seq) "
                 "VALUES ('s1', 'code.commit', 'message=''add echo_json''', 1)")
    conn.execute("INSERT INTO receipts (session_id, table_name, row_id, new_version) "
                 "VALUES ('s1', 'batches', 'bg_1', 2)")
    # s3 wrote the batch row and names no batch in its wake.
    _session(conn, "s3", "architect", 3, "tick:grouping", '["tk_1"]')
    conn.execute("INSERT INTO receipts (session_id, table_name, row_id, new_version) "
                 "VALUES ('s3', 'batches', 'bg_1', 1)")
    # s5 names the batch in a call only, and sits between two Liaison messages.
    _session(conn, "s4", "liaison", 4, "message")
    _session(conn, "s5", "tester", 5, "message")
    conn.execute("INSERT INTO tool_calls (session_id, fn, args_summary, seq) "
                 "VALUES ('s5', 'tests.encode', 'batch_id=''bg_1''', 1)")
    _session(conn, "s6", "liaison", 6, "message")
    _session(conn, "s7", "liaison", 7, "message")
    # The runner puts the completion line in the feedback of turn 2, and the
    # model replies in turns 2 and 3. Turn 4 is the runner's own note.
    _session(conn, "s8", "vision_keeper", 8, "message")
    u1 = "wake"
    u2 = u1 + "\n\nTOOL: a()\n\nOK a -> x. Your work for this session is complete."
    u3 = u2 + "\n\nTOOL: b()\n\nOK b -> y"
    _turn(conn, "s8", 1, u1, "TOOL: a()")
    _turn(conn, "s8", 2, u2, "TOOL: b()")
    _turn(conn, "s8", 3, u3, "done")
    _turn(conn, "s8", 4, "", "SESSION ENDED. The runner's account:\n- you named an act and "
                             "did not perform it", system="")
    conn.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result, reason) "
                 "VALUES ('v_old', 'bg_1', ?, 'fail', 'the separators are not compact')", (OLD,))
    conn.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result) "
                 "VALUES ('v_head', 'bg_1', ?, 'pass')", (HEAD,))
    conn.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined) "
                 "VALUES ('developer|tick:batch_start|bg_1', 3, 1)")
    conn.execute("INSERT INTO findings (id, batch_id, constraint_id, commit_sha, status, grain) "
                 "VALUES ('f_1', 'bg_1', 'k0', ?, 'violated', 'x.py')", (HEAD,))
    conn.execute("INSERT INTO finding_rulings (id, finding_id, commit_sha, ruling, reason, at) "
                 "VALUES ('r_1', 'f_1', ?, 'upheld', 'the grain breaks k0', "
                 "'2026-10-01 10:00:00')", (HEAD,))
    conn.commit()
    conn.close()
    return tmp_path / "night.db"


def _report(path, **kw) -> list[str]:
    conn = nightreport.open_ro(path)
    try:
        return nightreport.build(conn, **kw)
    finally:
        conn.close()


def _section(lines: list[str], name: str) -> list[str]:
    start = next(i for i, l in enumerate(lines) if l.startswith(f"== {name}"))
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("== ")),
               len(lines))
    return lines[start + 1:end]


def test_the_report_holds_the_rows_a_read_asks_for(tmp_path):
    lines = _report(_night(tmp_path))
    text = "\n".join(lines)

    batch = next(l for l in lines if l.startswith("bg_1 status="))
    assert "status=running" in batch and f"head={HEAD[:10]}" in batch
    assert "commits=2" in batch
    assert f"  s1 {OLD[:10]} {HEAD[:10]}" in lines

    s1 = next(l for l in lines if l.startswith("s1 developer"))
    assert "tick:batch_start" in s1 and "t=3 c=1" in s1 and "last=code.commit(" in s1
    s2 = next(l for l in lines if l.startswith("s2 tester"))
    assert "c=0" in s2 and "error=the model returned no call" in s2
    assert all(len(l) <= 120 for l in (s1, s2))

    old = next(l for l in lines if l.startswith("v_old "))
    head = next(l for l in lines if l.startswith("v_head "))
    assert " old " in old and "reason=the separators are not compact" in old
    assert " head " in head

    assert "'dropped to fit the window': turns=2 sessions=1" in lines
    assert "developer|tick:batch_start|bg_1 attempts=3 quarantined=1 reported=0" in lines
    assert "s2 tester tick:tests_missing: SESSION FAILED: the model returned no call" in lines
    for name in ("batches", "wakes", "verdicts", "test runs", "findings and rulings",
                 "tick attempts", "quarantine and deferral", "messages",
                 "window and door phrases", "failures"):
        assert f"== {name}" in text
    assert len(lines) < 200


def test_the_report_counts_open_faults_per_refused_call(tmp_path):
    """Frame 204's design, section 7, reader 2: the build session reads a
    night's fault reports here, counted per refused call."""
    path = _night(tmp_path)
    conn = init_db(path)
    rows = (("f_1", "glossary.adopt", "fault", "open"), ("f_2", "glossary.adopt", "fault", "open"),
            ("f_3", "glossary.adopt", "fault", "resolved"), ("f_4", "model.adopt", "blocked", "open"))
    for seq, (fid, call, kind, status) in enumerate(rows, start=1):
        conn.execute("INSERT INTO faults (id, call, text, kind, author, seq, status) "
                     "VALUES (?, ?, 'the door refused it', ?, 'architect', ?, ?)",
                     (fid, call, kind, seq, status))
    conn.close()
    assert _section(_report(path), "open faults") == ["glossary.adopt fault 2",
                                                      "model.adopt blocked 1"]
    assert _section(_report(_night(tmp_path / "empty")), "open faults") == ["(none)"]


def test_a_receipt_session_joins_its_batch(tmp_path):
    lines = _report(_night(tmp_path))
    wakes = _section(lines, "wakes")
    loose = wakes.index(next(l for l in wakes if l.startswith("-- no batch")))
    s3 = next(i for i, l in enumerate(wakes) if l.startswith("s3 architect"))
    s5 = next(i for i, l in enumerate(wakes) if l.startswith("s5 tester"))
    assert s3 < loose and s5 < loose
    # s3 wrote the batch row with no commit line, so the history keeps it.
    assert "  s3 no commit line" in _section(lines, "batches")


def test_a_run_never_hides_a_session_between(tmp_path):
    """The default print groups by role and kind, and names its first and last session only."""
    wakes = _section(_report(_night(tmp_path)), "wakes")
    assert "liaison message x3 t=0 c=3 first=s4 last=s7" in wakes
    assert "vision_keeper message x1 t=3 c=1 first=s8 last=s8" in wakes
    # s5 sits between s4 and s6, and prints under its batch, not in the group.
    assert any(l.startswith("s5 tester message") for l in wakes)
    assert not any(".." in l.split(" ")[0] for l in wakes)


def test_full_prints_one_line_per_session(tmp_path):
    wakes = _section(_report(_night(tmp_path), full=True), "wakes")
    for sid in ("s4", "s6", "s7"):
        assert any(l.startswith(f"{sid} liaison message [] t=0 c=1") for l in wakes)
    assert not any(" first=" in l for l in wakes)


def test_the_completion_line_counts_from_its_first_turn(tmp_path):
    phrases = _section(_report(_night(tmp_path)), "window and door phrases")
    assert "  s8 first_turn=2 turns_from=2" in phrases
    act = next(l for l in phrases if l.startswith("'named an act"))
    assert "(runner)" in act and "turns=1 sessions=1" in act


def test_an_absent_table_or_column_prints_as_absent(tmp_path):
    """An old night lacks a table, and a zero from it must not read as a fact."""
    path = _night(tmp_path)
    conn = sqlite3.connect(path)
    conn.execute("DROP TABLE turns")
    conn.execute("DROP TABLE finding_rulings")
    conn.execute("ALTER TABLE sessions DROP COLUMN wake_kind")
    conn.commit()
    conn.close()
    lines = _report(path)
    assert lines[0].startswith("night report: 8 sessions, ? turns")
    # Without turns, the history cannot say whether a commit line exists.
    assert "  s3 sha=?" in _section(lines, "batches")
    assert "absent: turns" in _section(lines, "window and door phrases")
    assert "'CUT the result': turns=? sessions=?" in lines
    assert "absent: finding_rulings" in _section(lines, "findings and rulings")
    wakes = _section(lines, "wakes")
    assert "absent: sessions.wake_kind" in wakes
    assert any(l.startswith("s1 developer ? [bg_1] t=? c=1") for l in wakes)
    # Without the wake kind, no group forms, and each session keeps its line.
    assert not any(" first=" in l for l in wakes)
    assert any(l.startswith("s4 liaison ? []") for l in wakes)


def test_the_eviction_notice_counts_in_each_prompt_that_holds_it(tmp_path):
    """
    `_fit` writes the notice before the newest feedback, so the whole prompt is read.

    Turns 2, 3 and 4 hold the notice with one count. `_fit` writes the same
    count after a new drop, so a repeated count is still a cut. Turn 4's
    prompt holds no copy of turn 3's completion, so its CUT line counts nothing.
    """
    conn = init_db(tmp_path / "evict.db")
    _session(conn, "s1", "developer", 1, "tick:batch_start")
    notice = "[2 earlier exchange(s) dropped to fit the window. Re-read anything you need.]"
    u2 = f"wake\n\n{notice}\n\nTOOL: a()\n\nOK a -> x"
    u3 = f"wake\n\n{notice}\n\nTOOL: b()\n\nOK b -> y"
    u4 = f"wake\n\n{notice}\n\nTOOL: z()\n\nOK z -> CUT the result"
    _turn(conn, "s1", 1, "wake", "TOOL: a()")
    _turn(conn, "s1", 2, u2, "TOOL: b()")
    _turn(conn, "s1", 3, u3, "TOOL: c()")
    _turn(conn, "s1", 4, u4, "TOOL: d()")
    conn.commit()
    conn.close()
    phrases = _section(_report(tmp_path / "evict.db"), "window and door phrases")
    assert "'dropped to fit the window': turns=3 sessions=1" in phrases
    assert "'CUT the result': turns=0 sessions=0" in phrases
    assert "prompts holding no copy of the previous completion: 1" in phrases


NIGHT105 = Path(__file__).resolve().parents[2] / ".rota" / "clickI_night105.db"


@pytest.mark.skipif(not NIGHT105.exists(), reason="night 105's run database is absent")
def test_night_105_counts_every_prompt_that_holds_the_notice():
    """
    The count by a new N read 20 turns, and the prompts hold 43 notices (frame 105, pass 5).

    s131 holds a notice of 2 in turns 5 to 11, and `_fit` writes 2 after each
    new drop of one block.
    """
    assert "'dropped to fit the window': turns=43 sessions=7" in _report(NIGHT105)


def test_since_reads_a_t_as_the_stored_space(tmp_path):
    path = _night(tmp_path)
    kept = _section(_report(path, since="2026-10-01T09:00"), "findings and rulings")
    assert any("ruling=upheld" in l for l in kept)
    gone = _section(_report(path, since="2026-10-01T11:00"), "findings and rulings")
    assert any("ruling=-" in l for l in gone)


def test_main_prints_the_report(tmp_path, capsys):
    assert nightreport.main([str(_night(tmp_path))]) == 0
    assert "== failures" in capsys.readouterr().out
