"""
Frame 316, pass 2: an agenda page carries the open rows of one item.

Night 162 (2026-10-24) put rows of the merged echo_json and confirm items
on the pages of the version item: m217 carried 6 of 7, m223, m232 and m237
carried 7 of 7, and m244 carried 1 of 3. `tick_agenda` selected every open
row of the night, with no item filter. His drops on m237 ended in s417's
change of a version test (`plans/night162-read.md`, W3).

The rule: a row belongs to the items its `about_ref` reaches, a test
through its criterion or its batch, and else to the item of its writer's
batch. The page takes the live batch's item first. A merged item's open
rows park at the merge, and the shipped line counts them (frame 204's
design, section 4).
"""
from __future__ import annotations

import pytest

from rota.core import lifecycle
from rota.core.db import init_db
from rota.core.scheduler import tick_agenda
from rota.roles.principal import render_state
from rota.testkit.fixtures import seed_provenance, seed_ref

ECHO, CONFIRM, VERSION = "echo_json", "confirm_default_on_eof", "version_option_show_python"


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    for n, (entry, order, item) in enumerate((
            ("e_p1", 8, ECHO), ("e_p2", 16, CONFIRM), ("e_p3", 24, VERSION)), start=1):
        conn.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
                     "(?, 'principal', ?, ?)", (entry, order, f"request {item}"))
        conn.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
                     "text, status) VALUES (?, ?, 0, 10, ?, 'ratified')",
                     (f"s{n}", entry, f"request {item}"))
        conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                     "version) VALUES (?, ?, 'in_scope', 'approved', 1, 1)",
                     (item, f"the {item} change"))
        seed_ref(conn, "items", item, "statement", f"s{n}")
        seed_provenance(conn, "items", item, "decided")
        conn.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, ?, 'a ticket')",
                     (f"tk_{n}", item))
        conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                     "VALUES (?, ?, 'a criterion', '[]')", (f"c_{n}", f"tk_{n}"))
    conn.commit()
    return conn


def _batch(db, batch_id, item, status):
    db.execute("INSERT INTO batches (id, item_id, status) VALUES (?, ?, ?)",
               (batch_id, item, status))
    if status == "merged":
        db.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, '1')",
                   (f"delivered:{item}",))
    db.commit()


def _notes(db, rows):
    for ledger_id, about in rows:
        db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
                   "kind, status, author) VALUES (?, ?, 'criteria', 'a note', "
                   "'default', 'open', 'developer')", (ledger_id, about))
    db.commit()


def _review(db):
    """The review gate, so a default row past intent still wakes a page."""
    from rota.core import config

    config.set(db, "merge_gate", "review")


def _page(db):
    wakes = tick_agenda(db, principal_present=True)
    return list(wakes[0].refs) if wakes else []


def _night162(db):
    """Night 162 at m217: b_1 and b_2 merged before the park existed, b_3
    runs. The echo and confirm rows are older than the version rows."""
    _batch(db, "b_1", ECHO, "merged")
    _batch(db, "b_2", CONFIRM, "merged")
    _batch(db, "b_3", VERSION, "running")
    echo = [(f"l_e{n}", "c_1") for n in range(4)]
    confirm = [(f"l_c{n}", "c_2") for n in range(4)]
    version = [("l_v0", "c_3"), ("l_v1", "tk_3")]
    _notes(db, echo + confirm + version)
    return [r for r, _ in version]


def test_m217_the_page_of_the_live_item_carries_only_its_rows(db):
    """The m217 shape: the version page carried 6 echo_json rows of 7."""
    # Through `merge_gate = review`: under `auto` a default row past
    # intent wakes no page (frame 204's design, section 5; frame 325).
    _review(db)
    own = _night162(db)
    assert _page(db) == own


def test_a_test_row_reaches_its_item_through_its_criterion(db):
    """s331's l_71e52c9d0a was about `tst_c2_version_on`. A test reaches no
    item through `_items_reached`, so its criterion names the item."""
    # Through `merge_gate = review`: under `auto` a default row past
    # intent wakes no page (frame 204's design, section 5; frame 325).
    _review(db)
    own = _night162(db)
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
               "('tst_c2', 'b_3', 'c_3', 'tests/test_version.py', '')")
    _notes(db, [("l_t0", "tst_c2")])
    assert _page(db) == own + ["l_t0"]


def test_a_row_of_a_path_goes_to_its_writers_batch(db):
    """A row about a path reaches no item. Its writer's batch names the item,
    frame 198's route through `receipts` and `checkpoints.batch_id`."""
    # Through `merge_gate = review`: under `auto` a default row past
    # intent wakes no page (frame 204's design, section 5; frame 325).
    _review(db)
    own = _night162(db)
    _notes(db, [("l_p0", "tests/test_utils/")])
    db.execute("INSERT INTO sessions (id, role, seq) VALUES ('s9', 'developer', 9)")
    db.execute("INSERT INTO checkpoints (session_id, role, batch_id, working_set) "
               "VALUES ('s9', 'developer', 'b_1', '[]')")
    db.execute("INSERT INTO receipts (session_id, table_name, row_id, new_version) "
               "VALUES ('s9', 'ledger', 'l_p0', 1)")
    db.commit()
    db.execute("UPDATE ledger SET status = 'resolved' WHERE id LIKE 'l_e%' "
               "OR id LIKE 'l_c%'")
    db.commit()
    assert _page(db) == own


def test_a_row_of_no_item_and_no_batch_stays_on_the_live_page(db):
    """A row with no item and no batch has no other page, so it rides on
    the page of the item the Liaison is about and is not lost."""
    # Through `merge_gate = review`: under `auto` a default row past
    # intent wakes no page (frame 204's design, section 5; frame 325).
    _review(db)
    own = _night162(db)
    _notes(db, [("l_n0", "f_3f3b740531")])
    assert _page(db) == own + ["l_n0"]


def test_the_rows_of_another_open_item_wait_for_its_page(db):
    """Two live items: the item of the oldest row no page has shown goes
    first. The other item's rows come on the next page, and no row is
    lost."""
    # Through `merge_gate = review`: under `auto` a default row past
    # intent wakes no page (frame 204's design, section 5; frame 325).
    _review(db)
    _batch(db, "b_3", VERSION, "running")
    _notes(db, [("l_c0", "c_2"), ("l_v0", "c_3"), ("l_c1", "tk_2"), ("l_v1", "c_3")])
    assert _page(db) == ["l_c0", "l_c1"]
    db.execute("UPDATE ledger SET status = 'resolved' WHERE id IN ('l_c0', 'l_c1')")
    db.commit()
    assert _page(db) == ["l_v0", "l_v1"]


def _shown(db, mid, refs):
    """A page that the principal answered and that left its rows open."""
    import json

    seq = db.execute("SELECT COALESCE(MAX(seq), 0) + 1 FROM messages").fetchone()[0]
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES (?, 'th', 'liaison', 'principal', "
               "'present', ?, ?, 'answered')", (mid, json.dumps(refs), seq))
    db.commit()


def test_a_queued_items_row_reaches_a_page_within_two_ticks(db):
    """Review 2, finding 3: the probe added a version row on each of 5
    ticks, and the confirm row l_c0 was on none of the 5 pages. Its batch
    then merged, and the row parked unseen."""
    # Through `merge_gate = review`: under `auto` a default row past
    # intent wakes no page (frame 204's design, section 5; frame 325).
    _review(db)
    _batch(db, "b_3", VERSION, "running")
    _notes(db, [("l_v0", "c_3"), ("l_c0", "c_2"), ("l_v1", "c_3")])
    first = _page(db)
    assert first == ["l_v0", "l_v1"]
    _shown(db, "m1", first)
    _notes(db, [("l_v2", "c_3")])
    assert _page(db) == ["l_c0"]


def test_m237_a_drop_on_the_live_page_has_no_foreign_row_to_reach(db):
    """The m237 shape: 7 of 7 confirm rows on the version page. A drop of
    them went to s415 and s417. With the page of the live item alone, the
    page holds no row that reaches another item's Developer. Pass 1's tests
    cover the landing."""
    from rota.core.lifecycle import ledger_items

    _night162(db)
    for ref in _page(db):
        assert ledger_items(db, ref) <= {VERSION}, ref


def _merge(db, monkeypatch, batch_id):
    from rota.core import environments, harness, worktrees

    monkeypatch.setattr(harness, "worktree_of", lambda conn, b: None)
    monkeypatch.setattr(worktrees, "integrate", lambda conn, b: None)
    monkeypatch.setattr(worktrees, "destroy", lambda conn, b: None)
    monkeypatch.setattr(environments, "teardown", lambda conn, b, **kw: None)
    monkeypatch.setattr(lifecycle, "_reindex_main", lambda conn, b: None)
    lifecycle.merge(db, batch_id)
    db.commit()


def test_the_merge_parks_the_merged_items_open_rows(db, monkeypatch):
    """Frame 204's design, section 4: a park is not a close. The rows of
    the merged item leave the open set, and no decision is written."""
    # Through `merge_gate = review`: under `auto` a default row past
    # intent wakes no page (frame 204's design, section 5; frame 325).
    _review(db)
    _batch(db, "b_2", CONFIRM, "running")
    _batch(db, "b_3", VERSION, "running")
    _notes(db, [("l_c0", "c_2"), ("l_c1", "tk_2"), ("l_v0", "c_3"),
                ("l_n0", "f_3f3b740531")])
    decisions = db.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
    _merge(db, monkeypatch, "b_2")
    status = dict(db.execute("SELECT id, status FROM ledger").fetchall())
    assert status == {"l_c0": "parked", "l_c1": "parked", "l_v0": "open",
                      "l_n0": "open"}
    assert db.execute("SELECT COUNT(*) FROM decisions").fetchone()[0] == decisions
    assert _page(db) == ["l_v0", "l_n0"]


def test_the_shipped_line_counts_the_parked_rows_by_kind(db, monkeypatch):
    """Review 2, finding 2: 6 of night 162's 28 rows are `scope` rows, and
    a scope row is not a choice. The line offers the words, because
    `ledger.list(shipped=...)` now shows them."""
    _batch(db, "b_2", CONFIRM, "running")
    _notes(db, [("l_c0", "c_2"), ("l_c1", "tk_2"), ("l_c2", "c_2")])
    db.execute("UPDATE ledger SET kind = 'scope' WHERE id = 'l_c2'")
    db.commit()
    _merge(db, monkeypatch, "b_2")
    text = render_state(db)
    assert ("Done: 1 change built, tested and merged. It carries 2 choices the "
            "team made where you said nothing and 1 change of scope the team "
            "noted. Ask me to show them.") in text, text


def test_ledger_list_shows_a_shipped_items_parked_rows(db, monkeypatch):
    from rota.roles.api import Ctx, ledger_list

    _batch(db, "b_2", CONFIRM, "running")
    _batch(db, "b_3", VERSION, "running")
    _notes(db, [("l_c0", "c_2"), ("l_v0", "c_3")])
    _merge(db, monkeypatch, "b_2")
    ctx = Ctx(conn=db, role="liaison", session_id="s1")
    assert [r["id"] for r in ledger_list(ctx)] == ["l_v0"]
    shown = ledger_list(ctx, shipped=CONFIRM)
    assert [r["id"] for r in shown[f"open when {CONFIRM} shipped"]] == ["l_c0"]


def test_a_ruling_on_a_row_parked_while_its_page_was_open_lands(db, monkeypatch):
    """Review 2, finding 1: the page named l_c0, b_2 merged, and the
    contest wrote no decision. The row stayed parked."""
    import json

    from rota.roles.principal import Answer, land, pending_asks

    _batch(db, "b_2", CONFIRM, "running")
    _notes(db, [("l_c0", "c_2")])
    for mid, cause, frm, to, verb, seq, status in (
            ("m8", None, "vision_keeper", "liaison", "submit", 0, "answered"),
            ("m9", "m8", "liaison", "principal", "present", 1, "open")):
        db.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, to_role, "
                   "verb, body_refs, seq, status) VALUES (?, 'th', ?, ?, ?, ?, ?, ?, ?)",
                   (mid, cause, frm, to, verb, json.dumps([CONFIRM, "l_c0"]), seq,
                    status))
    db.commit()
    (ask,) = pending_asks(db)
    _merge(db, monkeypatch, "b_2")
    assert db.execute("SELECT status FROM ledger WHERE id = 'l_c0'"
                      ).fetchone()["status"] == "parked"
    land(db, ask, Answer(verb="verdict", text="no, the default is wrong",
                         per_item={CONFIRM: "approve", "l_c0": "contest"}))
    db.commit()
    assert db.execute("SELECT status FROM ledger WHERE id = 'l_c0'"
                      ).fetchone()["status"] == "resolved"
    assert db.execute("SELECT COUNT(*) FROM decisions WHERE resolves_ledger = 'l_c0'"
                      ).fetchone()[0] == 1


def test_the_park_drops_the_account_as_the_agenda_does(db, monkeypatch):
    """Review 2, finding 5: a row that reaches the merged item and the
    account stayed open at the merge."""
    from rota.testkit.fixtures import seed_ref as _ref

    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version, "
               "is_description) VALUES ('how_it_works', 'the account', 'in_scope', "
               "'approved', 1, 1, 1)")
    _ref(db, "items", "how_it_works", "statement", "s2")
    db.commit()
    _batch(db, "b_2", CONFIRM, "running")
    _notes(db, [("l_c0", "s2")])
    _merge(db, monkeypatch, "b_2")
    assert db.execute("SELECT status FROM ledger WHERE id = 'l_c0'"
                      ).fetchone()["status"] == "parked"
