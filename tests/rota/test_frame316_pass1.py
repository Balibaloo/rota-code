"""
Frame 316, pass 1: `land` finds a note's owner through the items it reaches.

Night 161 (2026-10-24) put notes about the merged confirm and echo_json
items on the version page. He asked four times to take them off the page.
The Liaison read each ask as a contest, and the carrier contested the
note's `about_ref`. `request_of` reads an item id only, so a note about a
criterion or a ticket had no owner, and the skip of frame 274 never fired.
s409 then respecified the merged confirm item's `cr_1` five times
(`plans/frame316-provenance.md`, repair 1, red tests 1 to 4).

The fixture has the shape of night 161's rows: three requests, two merged
items, and the criteria and tickets that the notes name.
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.roles.principal import Answer, land, pending_asks, verdict_for
from rota.testkit.fixtures import seed_provenance, seed_ref

VERSION = "version_option_show_python"
CRITERIA = [f"c_{n}_{VERSION}_{tail}" for n, tail in
            ((2, "format"), (3, "source"), (4, "impl"), (5, "context"), (6, "help"))]


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    for n, (entry, order, item, approval) in enumerate((
            ("e_p1", 8, "echo_json", "approved"),
            ("e_p2", 16, "confirm_default_on_eof", "approved"),
            ("e_p3", 24, VERSION, "draft")), start=1):
        conn.execute("INSERT INTO entries (id, author, ts_order, text) VALUES "
                     "(?, 'principal', ?, ?)", (entry, order, f"request {item}"))
        conn.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
                     "text, status) VALUES (?, ?, 0, 10, ?, 'ratified')",
                     (f"s{n}", entry, f"request {item}"))
        conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                     "version) VALUES (?, ?, 'in_scope', ?, 1, 1)",
                     (item, f"the {item} change", approval))
        seed_ref(conn, "items", item, "statement", f"s{n}")
        seed_provenance(conn, "items", item, "decided")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) "
                 "VALUES ('bg_1', 'echo_json', 'merged', '0d65f7b9')")
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) "
                 "VALUES ('bg_3', 'confirm_default_on_eof', 'merged', '7c1e2a40')")
    # The bare ticket names went to the first slicer. Night 161's `tk_2`
    # is the confirm item's, and `c_2` is echo_json's.
    for ticket, item in (("tk_1", "echo_json"), ("tk_2", "confirm_default_on_eof"),
                         ("tk_1_confirm_default_on_eof", "confirm_default_on_eof"),
                         (f"tk_2_{VERSION}", VERSION)):
        conn.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, ?, 'a ticket')",
                     (ticket, item))
    for crit, ticket in ([("c_2", "tk_1"), ("c_3", "tk_1"), ("cr_1", "tk_2")]
                         + [(f"cr_{n}_confirm_default_on_eof",
                             "tk_1_confirm_default_on_eof") for n in (1, 2, 3)]
                         + [(c, f"tk_2_{VERSION}") for c in CRITERIA]):
        conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                     "VALUES (?, ?, 'a criterion', '[]')", (crit, ticket))
    conn.execute("INSERT INTO tests (id, batch_id, path, body) VALUES "
                 "('tst_4_confirm_default_on_eof', 'bg_3', 'tests/test_confirm.py', '')")
    conn.commit()
    return conn


def _notes(db, rows):
    for ledger_id, about in rows:
        db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
                   "kind, status, author) VALUES (?, ?, 'criteria', 'a note', "
                   "'default', 'open', 'terminologist')", (ledger_id, about))
    db.commit()


def _page(db, refs):
    # The sign-off page: a present caused by the Vision Keeper's `submit`.
    for mid, cause, frm, to, verb, seq, status in (
            ("m8", None, "vision_keeper", "liaison", "submit", 0, "answered"),
            ("m9", "m8", "liaison", "principal", "present", 1, "open")):
        db.execute("INSERT INTO messages (id, thread_id, cause_id, from_role, to_role, "
                   "verb, body_refs, seq, status) VALUES (?, 'th', ?, ?, ?, ?, ?, ?, ?)",
                   (mid, cause, frm, to, verb, json.dumps(refs), seq, status))
    db.commit()
    return pending_asks(db)[0]


def _land(db, notes, ruling, said):
    _notes(db, notes)
    page = [VERSION] + CRITERIA + [n for n, _ in notes]
    ask = _page(db, page)
    per_item = {VERSION: "approve", **{c: "approve" for c in CRITERIA}, **ruling}
    mid = land(db, ask, Answer(verb="verdict", text=said, per_item=per_item))
    db.commit()
    body = json.loads(db.execute("SELECT body_refs FROM messages WHERE id = ?",
                                 (mid,)).fetchone()["body_refs"])
    return set(body) | set(verdict_for(db, mid))


def _approval(db, item):
    return db.execute("SELECT approval FROM items WHERE id = ?", (item,)
                      ).fetchone()["approval"]


def test_m233_takes_the_confirm_criterion_off_the_page_and_keeps_line_7(db):
    """Red test 1: r_810ee68dc8, ask m233 and reply m234. The verdict m235
    held `cr_1`, and the relay m236 woke s409 on it."""
    notes = [("l_351d4a85ff", "cr_1"), ("l_5a9aa1ed3c", "cr_1"),
             ("l_ad1be36933", "cr_1"), ("l_839776f2d8", "cr_1"),
             ("l_8fd20d7618", "tst_4_confirm_default_on_eof")]
    refs = _land(db, notes, {CRITERIA[-1]: "contest", **{n: "contest" for n, _ in notes}},
                 "Lines 8 to 12 are about the confirm change, not this one, so "
                 "please take them off this page. Line 7's check expects a fixed "
                 "Python version.")
    assert f"c_6_{VERSION}_help" in refs
    assert "cr_1" not in refs, sorted(refs)
    assert _approval(db, "confirm_default_on_eof") == "approved"
    # A note about a test reaches no item, so the carrier keeps it. The
    # provenance names this gap out of scope: frame 204's pass 3 owns it.
    assert "tst_4_confirm_default_on_eof" in refs


def test_m225_takes_the_confirm_ticket_and_criteria_off_the_page(db):
    """Red test 2: r_288739e866, ask m225 and reply m226."""
    notes = [("l_128876ab6c", "tk_2"),
             ("l_40c47f5e2d", "cr_2_confirm_default_on_eof"),
             ("l_838e6d859c", "cr_1_confirm_default_on_eof"),
             ("l_868c65d8c4", "cr_3_confirm_default_on_eof"),
             ("l_8941e4a7f7", "cr_2_confirm_default_on_eof"),
             ("l_b5af776341", "cr_3_confirm_default_on_eof")]
    refs = _land(db, notes + [("l_14b6f22c97", f"c_6_{VERSION}_help")],
                 {CRITERIA[-1]: "contest", "l_14b6f22c97": "approve",
                  **{n: "contest" for n, _ in notes}},
                 "Lines 8 and 10 to 14 are about the confirm change, not this one, "
                 "so please take them off this page.")
    assert "tk_2" not in refs, sorted(refs)
    for n in (1, 2, 3):
        assert f"cr_{n}_confirm_default_on_eof" not in refs, sorted(refs)
    assert f"c_6_{VERSION}_help" in refs


def test_m218_takes_the_confirm_rows_off_and_contests_its_own_criterion(db):
    """Red test 3: r_40c94b2c6d, ask m218 and reply m219. The note about
    the page's own `c_2_..._format` still contests that criterion."""
    notes = [("l_2d8cfe55d7", "cr_1_confirm_default_on_eof"),
             ("l_843f17e810", "tk_1_confirm_default_on_eof"),
             ("l_7b7a3bfff9", CRITERIA[0])]
    refs = _land(db, notes, {CRITERIA[-1]: "revise", **{n: "contest" for n, _ in notes}},
                 "Lines 10 and 12 belong to the confirm change, not this one, so "
                 "please take them off this page.")
    assert "cr_1_confirm_default_on_eof" not in refs, sorted(refs)
    assert "tk_1_confirm_default_on_eof" not in refs, sorted(refs)
    assert f"c_6_{VERSION}_help" in refs


def test_m191_takes_the_echo_json_criterion_off_and_keeps_a_note_of_no_item(db):
    """Red test 4: r_e1e0b9a1d8, ask m191 and reply m194. `r_a1ca6cbbe0`
    reaches no item, so the carrier keeps it."""
    notes = [("l_511c47ccd1", "c_2"), ("l_ed04dbc3f3", "c_2"),
             ("l_d7cdbc51dc", "r_a1ca6cbbe0")]
    refs = _land(db, notes + [("l_01d2b707a4", "c_3")],
                 {"l_01d2b707a4": "approve", **{n: "contest" for n, _ in notes}},
                 "Change the test to use click directly instead of a separate "
                 "test package.")
    assert "c_2" not in refs, sorted(refs)
    assert "r_a1ca6cbbe0" in refs
    assert _approval(db, "echo_json") == "approved"
