"""
Frame 356, pass 1: the vet resolves a dotted surface ref to its index row.

dry1's Terminologist s139 sent `surface_refs=['click.pause']` to
`criteria.specify`. The index held `src/click/termui.py::pause` and
`examples/termui/termui.py::pause`, and no grain `click.pause`. The vet kept
the ref as written. The encode door then refused every test body, because no
test calls a name `click.pause` (plans/dry1-third-wall-read-2026-11-01.md,
sections 1, 2 and 5).
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.testkit.fixtures import seed_provenance

ITEM = "pause_waits_for_a_key"
EXAMPLE = "examples/termui/termui.py::pause"
LIBRARY = "src/click/termui.py::pause"


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version, priority) VALUES (?, ?, 'in_scope', 'approved', 1, 1, 1)",
                 (ITEM, "Make click.pause() wait for a key."))
    seed_provenance(conn, "items", ITEM, "decided")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk_1', ?, 'click.pause() waits for a key')", (ITEM,))
    for path in ("examples/termui/termui.py", "src/click/termui.py"):
        conn.execute("INSERT INTO code_index (grain, grain_kind) "
                     "VALUES (?, 'path')", (path,))
    # dry1's index lists the example's row first, as the sorted walk does.
    for grain in (EXAMPLE, LIBRARY, "src/click/testing.py::_pause_echo"):
        conn.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) "
                     "VALUES (?, 'symbol', 'function')", (grain,))
    conn.execute("INSERT INTO frame_rulings (id, kind, reason) VALUES "
                 "('examples', 'attached', 'Contains example code')")
    conn.execute("INSERT INTO frame_rulings (id, kind, reason) VALUES "
                 "('src', 'program', 'Source code for the main package')")
    conn.commit()
    return conn


def _vet(db, ref):
    from rota.roles.api import _vet_surface

    ctx = build("terminologist", db, mode="criteria").ctx
    return _vet_surface(ctx, [ref], required=False, ticket_id="tk_1")


def _specify(db, ref):
    sb = build("terminologist", db, mode="criteria")
    sb.call("criteria.specify", id="c_1", ticket_id="tk_1", text="x",
            surface_refs=[ref])
    return json.loads(sb.ctx.writes[-1][2]["surface_refs"])


def test_s139_dotted_click_pause_stores_the_programs_row(db):
    assert _vet(db, "click.pause") == [LIBRARY]
    assert _specify(db, "click.pause") == [LIBRARY]


def test_the_bare_name_stores_the_same_row(db):
    assert _vet(db, "pause") == [LIBRARY]


def test_a_dotted_ref_with_no_row_stays_as_written(db):
    assert _vet(db, "click.nothing_here") == ["click.nothing_here"]


def test_a_dotted_method_ref_finds_its_qualified_row(db):
    """The index writes a method as `path::Class.name`, so the longer
    suffix is tried before the last segment."""
    db.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) VALUES "
               "('src/click/core.py::Context.invoke', 'symbol', 'method')")
    db.commit()
    assert _vet(db, "click.Context.invoke") == [
        "src/click/core.py::Context.invoke"]
