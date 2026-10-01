"""
The night report prints the rows a night's read asks for.

The build session read each night's run database on an agent for 85k to
103k tokens (observed: frame 105's brief, 2026-10-01). These pins hold the
lines that the read leans on: the batch and its head history, one wake line
per session, the head verdict apart from the old one, and a door phrase
counted once per turn that adds it.
"""
from __future__ import annotations

from rota.core.db import init_db
from rota.tools import nightreport

OLD = "a" * 40
HEAD = "b" * 40


def _feedback(sha: str) -> str:
    return f'OK code.commit -> {{"committed": true, "head_commit": "{sha}", "touched": ["x.py"]}}'


def _night(tmp_path):
    conn = init_db(tmp_path / "night.db")
    conn.execute("INSERT INTO items (id, text, kind) VALUES ('it_1', ?, 'in_scope')",
                 ("Add an echo_json helper " + "that prints compact JSON " * 6,))
    conn.execute("INSERT INTO batches (id, item_id, head_commit, status) "
                 "VALUES ('bg_1', 'it_1', ?, 'running')", (HEAD,))
    conn.execute("INSERT INTO sessions (id, role, committed, seq, wake_kind, wake_refs) "
                 "VALUES ('s1', 'developer', 1, 1, 'tick:batch_start', '[\"bg_1\"]')")
    conn.execute("INSERT INTO sessions (id, role, committed, seq, wake_kind, wake_refs) "
                 "VALUES ('s2', 'tester', 0, 2, 'tick:tests_missing', '[\"bg_1\"]')")
    # The prompt repeats the earlier feedback, so turn 3 adds one more copy
    # of the phrase and turn 2 adds none.
    p1 = "wake. dropped to fit the window"
    p2 = p1 + "\n" + _feedback(OLD)
    p3 = p2 + "\n" + _feedback(HEAD) + "\ndropped to fit the window"
    for seq, user in ((1, p1), (2, p2), (3, p3)):
        conn.execute("INSERT INTO turns (session_id, seq, system, user, completion) "
                     "VALUES ('s1', ?, 'sys', ?, 'TOOL: code.commit()')", (seq, user))
    conn.execute("INSERT INTO turns (session_id, seq, system, user, completion) "
                 "VALUES ('s2', 1, '', '', 'SESSION FAILED: the model returned no call')")
    conn.execute("INSERT INTO tool_calls (session_id, fn, args_summary, seq) "
                 "VALUES ('s1', 'code.commit', 'message=''add echo_json''', 1)")
    conn.execute("INSERT INTO receipts (session_id, table_name, row_id, new_version) "
                 "VALUES ('s1', 'batches', 'bg_1', 2)")
    conn.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result, reason) "
                 "VALUES ('v_old', 'bg_1', ?, 'fail', 'the separators are not compact')", (OLD,))
    conn.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result) "
                 "VALUES ('v_head', 'bg_1', ?, 'pass')", (HEAD,))
    conn.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined) "
                 "VALUES ('developer|tick:batch_start|bg_1', 3, 1)")
    conn.commit()
    conn.close()
    return tmp_path / "night.db"


def _report(path) -> list[str]:
    conn = nightreport.open_ro(path)
    try:
        return nightreport.build(conn)
    finally:
        conn.close()


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


def test_the_report_opens_a_night_without_a_newer_table(tmp_path):
    """An old night lacks a table, and the report must still open the night."""
    import sqlite3

    path = _night(tmp_path)
    conn = sqlite3.connect(path)
    conn.execute("DROP TABLE finding_rulings")
    conn.commit()
    conn.close()
    assert "== findings and rulings" in _report(path)


def test_main_prints_the_report(tmp_path, capsys):
    assert nightreport.main([str(_night(tmp_path))]) == 0
    assert "== failures" in capsys.readouterr().out
