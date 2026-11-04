"""
Frame 360, dry run 4's walls 8 and 14: the count a stall page names.

Wall 14: s213 quarantined `developer|tick:touch_mistaken|bg_1` at 3
attempts, and the Liaison sent m63 with the key in `stalled:m63`. A later
commit moved the head of bg_1, and `_lift_quarantines` deleted the row.
m63 renders at each read, so it then said "could not put back code it was
not asked to change after 0 attempts". The send door now records the
count beside the keys, as `attempts:<id>`, and the page reads the record.

Wall 8: s178 to s180 and s199 to s201 started bg_1, wrote no code and
called no commit, so they claimed nothing (657cf1a8). The start wake stayed
ready after each one, so none of them drained (0b90f02b). Each start counts.
"""
from __future__ import annotations

import json

from rota.core.db import write_state
from rota.core.scheduler import Wake, quarantine_stalled, tick_batch_start
from rota.roles.principal import pending_asks, render_page
from tests.rota.test_frame312_stuck_review import M45_REFS, bg1  # noqa: F401
from tests.rota.test_request_page import (  # noqa: F401 -- the fixtures
    ITEM_136, _dispatch, bg2, db)

TOUCH = "developer|tick:touch_mistaken|bg_2"
TOUCH_BG1 = "developer|tick:touch_mistaken|bg_1"
START_BG1 = "developer|tick:batch_start|bg_1"


def _sent_page(bg2, key: str) -> str:
    """bg_2 with a head and `key` quarantined at 3, and a present the send
    door records. Returns the page's id."""
    bg2.execute("UPDATE batches SET head_commit = 'aa28d1d' WHERE id = 'bg_2'")
    bg2.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, reported) "
                "VALUES (?, 3, 1, 0)", (key,))
    bg2.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, status, "
                "author) VALUES ('l_1', 'src/click/termui.py', 'items', 'The prompt "
                "reads one line from stdin.', 'open', 'architect')")
    bg2.commit()
    wake = Wake("liaison", "tick:agenda", refs=("l_1",), detail="ledger=1")
    return _dispatch(bg2, wake, f'TOOL: msg.present_principal(refs=["l_1", "{ITEM_136}", '
                                '"bg_2"])')


def _lift_by_a_commit(conn) -> None:
    """A new head on bg_2, as the commit after s213 moved bg_1 on dry4."""
    write_state(conn, "batches", "bg_2",
                "UPDATE batches SET head_commit = 'bb39e2e' WHERE id = 'bg_2'",
                fields={"head_commit": "bb39e2e"})


def _rendered(conn, mid: str) -> str:
    (ask,) = [a for a in pending_asks(conn) if a.message_id == mid]
    return ask.rendered


def test_the_send_door_records_the_count_beside_the_keys(bg2):
    mid = _sent_page(bg2, TOUCH)
    assert json.loads(bg2.execute("SELECT value FROM config WHERE key = ?",
                                  (f"attempts:{mid}",)).fetchone()["value"]) == {TOUCH: 3}


def test_a_stalled_touch_mistaken_page_names_the_real_count(bg2):
    """Wall 14: the page keeps its count after a commit lifts the key."""
    mid = _sent_page(bg2, TOUCH)
    _lift_by_a_commit(bg2)
    assert not bg2.execute("SELECT 1 FROM tick_attempts WHERE tick_key = ?",
                           (TOUCH,)).fetchone()
    page = _rendered(bg2, mid)
    assert ("could not put back code it was not asked to change after 3 attempts"
            in page), page
    assert "after 0 attempts" not in page, page


def test_a_given_up_test_line_keeps_its_count_after_the_lift(bg2):
    """The check line of a `tests_missing` key reads the same record."""
    mid = _sent_page(bg2, "tester|tick:tests_missing|bg_2")
    _lift_by_a_commit(bg2)
    page = _rendered(bg2, mid)
    assert "gave up writing it after 3 tries" in page, page
    assert "after 0" not in page, page


def test_a_page_with_no_recorded_count_never_says_after_0_attempts(bg1):
    """A page sent before the record, with its key lifted: the page names
    the step and no count. The stall key exists in `stalled:m63`."""
    bg1.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
                "body_refs, seq, status) VALUES ('m63', 't1', 'liaison', "
                "'principal', 'present', ?, 64, 'open')", (json.dumps(M45_REFS),))
    bg1.execute("INSERT INTO config (key, value) VALUES ('stalled:m63', ?)",
                (json.dumps([TOUCH_BG1]),))
    page = render_page(bg1, "present", M45_REFS, ask_id="m63")[0]
    assert "could not put back code it was not asked to change." in page, page
    assert "after 0 attempts" not in page, page


def test_an_empty_start_counts_toward_the_stall(bg1):
    """Wall 8: a start that wrote nothing, asked nothing and claimed nothing
    leaves the start wake ready. It is no drained start, so it counts, and
    the cap quarantines the key (law 4, 0b90f02b)."""
    from rota.core import config

    bg1.execute("UPDATE batches SET head_commit = NULL WHERE id = 'bg_1'")
    bg1.execute("INSERT INTO sessions (id, role, committed, seq, wake_kind, wake_refs) "
                "VALUES ('s180', 'developer', 1, 180, 'tick:batch_start', '[\"bg_1\"]')")
    cap = config.get(bg1, "tick_attempt_cap")
    bg1.execute("INSERT INTO tick_attempts (tick_key, attempts) VALUES (?, ?)",
                (START_BG1, cap - 1))
    (wake,) = tick_batch_start(bg1)
    assert wake.detail.startswith(f"attempt {cap} of {cap}: the last session ended "
                                  "with nothing written"), wake.detail
    assert quarantine_stalled(bg1, [wake]) == [wake]
    bg1.execute("UPDATE tick_attempts SET attempts = attempts + 1 WHERE tick_key = ?",
                (START_BG1,))
    assert quarantine_stalled(bg1, tick_batch_start(bg1)) == []
    assert bg1.execute("SELECT quarantined FROM tick_attempts WHERE tick_key = ?",
                       (START_BG1,)).fetchone()["quarantined"] == 1
