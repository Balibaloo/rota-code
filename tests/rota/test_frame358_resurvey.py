"""
A re-survey after a merge goes to the ledger and not to a page (frame 358).

dry1 merged bg_1, and the merge re-indexed main. The Architect re-surveyed
`src/click` and `.` in sessions s273 and s274. `observed_entries` then put
the 15 new constraints to the principal as m145, with a footer that said
'ok' starts building. No item was open, so nothing could start
(`plans/dry1-turn17-read-2026-11-02.md`, sections 3, 4 and 6). The rows
below are the dry1w10 copy's, read before m145.
"""
from __future__ import annotations

import json

import pytest

from rota.core import predicates as P
from rota.core.db import init_db
from rota.core.scheduler import frontier
from rota.roles.principal import render_page, render_state

ITEM = "click_pause_returns_true_on_key"
ITEM_TEXT = ("Make click.pause() return True when it waited for a key and "
             "False when it skipped because stdin or stdout is not a terminal.")
HEAD = "4fcd6d73f6fc05cdcb9fda0770f6cb6928335956"
# The m145 constraints: the id, the headline and the session that wrote it.
RESURVEY = [
    ("click_format_filename", "click.format_filename", "s274"),
    ("flag_needs_value", "FLAG_NEEDS_VALUE", "s273"),
    ("get_best_encoding", "get_best_encoding", "s273"),
    ("get_current_context", "get_current_context", "s273"),
    ("helpformatter", "HelpFormatter", "s273"),
    ("is_ascii_encoding", "is_ascii_encoding", "s273"),
    ("make_text_stream", "make_text_stream", "s273"),
    ("parametersource", "ParameterSource", "s273"),
    ("pop_context", "pop_context", "s273"),
    ("push_context", "push_context", "s273"),
    ("resolve_color_default", "resolve_color_default", "s273"),
    ("sentinel", "Sentinel", "s273"),
    ("t_flag_needs_value", "T_FLAG_NEEDS_VALUE", "s273"),
    ("t_unset", "T_UNSET", "s273"),
    ("unset", "UNSET", "s273"),
]
REFS = [c for c, _, _ in RESURVEY]
SESSIONS = [
    ("s4", "vision_keeper", 4, "tick:orient", "@program"),
    ("s83", "architect", 83, "tick:survey", "src/click"),
    ("s140", "architect", 140, "tick:grouping", ""),
    ("s145", "developer", 145, "tick:batch_start", "bg_1"),
    ("s273", "architect", 273, "tick:survey", "src/click"),
    ("s274", "architect", 274, "tick:survey", "."),
]


def _seed(conn, *, merged: bool = True, writer: dict | None = None) -> None:
    """The rows `observed_entries` reads. `writer` moves a constraint's
    receipt to another session, for the onboarding case."""
    for sid, role, seq, kind, ref in SESSIONS:
        conn.execute("INSERT INTO sessions (id, role, committed, seq, wake_kind, "
                     "wake_refs) VALUES (?, ?, 1, ?, ?, ?)",
                     (sid, role, seq, kind, json.dumps([ref] if ref else [])))
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version, "
                 "priority) VALUES (?, ?, 'in_scope', 'approved', 1, 1, 1)",
                 (ITEM, ITEM_TEXT))
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version, "
                 "priority) VALUES ('how_it_works', 'Click builds command line "
                 "interfaces.', 'in_scope', 'approved', 1, 1, 1)")
    conn.execute("INSERT INTO refs (src_table, src_id, kind, target, resolves) "
                 "VALUES ('items', 'how_it_works', 'grain', 'pyproject.toml', 1)")
    conn.execute("INSERT INTO receipts (session_id, table_name, row_id, new_version) "
                 "VALUES ('s4', 'items', 'how_it_works', 1)")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) "
                 "VALUES ('bg_1', ?, ?, ?)",
                 (ITEM, "merged" if merged else "running", HEAD))
    for sid, version in (("s140", 1), ("s145", 2)):
        conn.execute("INSERT INTO receipts (session_id, table_name, row_id, "
                     "new_version) VALUES (?, 'batches', 'bg_1', ?)", (sid, version))
    if merged:
        conn.execute("INSERT INTO config (key, value) VALUES (?, '1')",
                     (f"delivered:{ITEM}",))
    for area in ("src/click", "."):
        conn.execute("INSERT INTO survey_records (id, area, outcome, refs, area_hash, "
                     "commit_sha, version) VALUES (?, ?, 'found', '[]', 'h', ?, 2)",
                     (f"architect:{area}", area,
                      "09c82f3b6c24fbe4c770f356a78102a6fdd16cf2"))
    for n, (cid, headline, sid) in enumerate(RESURVEY, 8):
        conn.execute("INSERT INTO constraints (id, headline, text, is_global, version) "
                     "VALUES (?, ?, ?, 0, 1)",
                     (cid, headline, f"Any code that uses `{headline}` would break."))
        conn.execute("INSERT INTO refs (src_table, src_id, kind, target, resolves) "
                     "VALUES ('constraints', ?, 'grain', 'src/click/core.py', 1)", (cid,))
        conn.execute("INSERT INTO receipts (session_id, table_name, row_id, new_version) "
                     "VALUES (?, 'constraints', ?, ?)",
                     ((writer or {}).get(cid, sid), cid, n))
    # The onboarding page of the account, answered with a verdict.
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "body_refs, seq, status) VALUES ('m7', 'm7', 'liaison', 'principal', "
                 "'present', '[\"how_it_works\"]', 6, 'answered')")
    conn.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
                 "verb, body_refs, seq, status) VALUES ('m10', 'm7', 'm7', 'principal', "
                 "'liaison', 'verdict', '[]', 9, 'answered')")
    conn.commit()


@pytest.fixture
def dry1_turn17(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    _seed(conn)
    return conn


def _observed(wakes):
    return [w for w in wakes if w.kind == "tick:observed_entries"]


def test_the_re_survey_after_the_merge_pages_nothing_and_is_one_ledger_row(dry1_turn17):
    """Red at f0fb5b32: the runner's predicate pass woke the Liaison with the
    15 refs, and m145 followed. The pass now records one ledger row."""
    from rota.core.loop import step

    assert _observed(frontier(dry1_turn17)) == []
    result = step(dry1_turn17, principal_present=False)
    assert result.wake is not None and result.wake.kind == "do:resurvey_note"
    assert sorted(result.wake.refs) == REFS
    rows = dry1_turn17.execute(
        "SELECT about_ref, about_table, default_taken, kind, status FROM ledger"
    ).fetchall()
    assert len(rows) == 1
    (row,) = rows
    assert (row["about_ref"], row["about_table"], row["status"]) == (ITEM, "items",
                                                                     "parked")
    assert P.resurvey_noted(dry1_turn17) == set(REFS)
    # The pass owes nothing more: no page and no second row.
    again = frontier(dry1_turn17)
    assert _observed(again) == []
    assert not [w for w in again if w.kind == "do:resurvey_note"]
    assert P.REGISTRY["observed_entries"].fn(dry1_turn17) == []


def test_the_state_view_names_the_re_survey_notes_beside_the_done_line(dry1_turn17):
    from rota.core.loop import step

    step(dry1_turn17, principal_present=False)
    lines = render_state(dry1_turn17).splitlines()
    done = next(n for n, x in enumerate(lines) if x.startswith("Done: 1 change"))
    assert lines[done + 1] == ("After the merge the team re-read the project and "
                               "recorded 15 notes. Ask me to show them.")
    # The parked count of the Done line does not count the row again.
    assert "other note" not in lines[done]


def test_rows_written_before_the_merge_still_page_once(tmp_path):
    """The onboarding survey s83 wrote the rows, before bg_1 existed. The
    put-once rule stands: one page, then nothing."""
    conn = init_db(tmp_path / "rota.db")
    _seed(conn, writer={c: "s83" for c in REFS})
    (wake,) = P.REGISTRY["observed_entries"].fn(conn)
    assert wake.kind == "tick:observed_entries" and list(wake.refs) == REFS
    conn.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                 "body_refs, seq, status) VALUES ('m145', 'm145', 'liaison', "
                 "'principal', 'present', ?, 150, 'open')", (json.dumps(REFS),))
    conn.commit()
    assert P.REGISTRY["observed_entries"].fn(conn) == []
    assert conn.execute("SELECT COUNT(*) FROM ledger").fetchone()[0] == 0


def test_with_no_merged_batch_every_row_is_onboarding(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    _seed(conn, merged=False)
    (wake,) = P.REGISTRY["observed_entries"].fn(conn)
    assert wake.kind == "tick:observed_entries" and list(wake.refs) == REFS


M145_REFS = REFS + ["how_it_works"]


def test_a_page_with_no_open_item_does_not_promise_a_build(dry1_turn17):
    """Red at f0fb5b32: m145's footer said 'ok' starts building, and no
    item was open to build."""
    page, order = render_page(dry1_turn17, "present", M145_REFS, ask_id="m145",
                              returned=False)
    assert "starts building" not in page, page
    assert page.splitlines()[-1].startswith(
        "Reply in your own words. 'ok' approves this page, and nothing is built.")
    assert set(order) == set(M145_REFS)


def test_a_page_with_an_open_item_keeps_the_build_footer(dry1_turn17):
    dry1_turn17.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                        "version, priority) VALUES ('echo_flush', 'Make echo flush "
                        "stdout.', 'in_scope', 'pending', 0, 1, 2)")
    dry1_turn17.commit()
    page, _ = render_page(dry1_turn17, "present", ["echo_flush"] + M145_REFS,
                          ask_id="m146", returned=False)
    assert "'ok' approves all of this and starts building." in page, page
