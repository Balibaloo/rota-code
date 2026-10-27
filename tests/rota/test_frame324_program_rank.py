"""
Frame 324, pass 1: one resolver ranks the program's row for a bare name, at
both doors.

Night 165's item names the library's `clear`. The code index holds
`examples/termui/termui.py::clear` before `src/click/termui.py::clear`, and
the frame rulings mark `examples` attached and `src` program. s214 sent the
bare `clear` to `criteria.specify`, and the door stored the example's path.
s199 sent `symbols=["clear"]` to `batches.guess` with `src/click/termui.py`
in its paths, and the refusal named the example first
(plans/frame324-provenance.md, sections 1 and 5).
"""
from __future__ import annotations

import json

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import prompts
from rota.testkit.fixtures import seed_provenance

ITEM = "clear_screen_return_status"
EXAMPLE = "examples/termui/termui.py::clear"
LIBRARY = "src/click/termui.py::clear"


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version, priority) VALUES (?, ?, 'in_scope', 'approved', 1, 1, 1)",
                 (ITEM, "Make clear return whether it cleared the screen."))
    seed_provenance(conn, "items", ITEM, "decided")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('t1', ?, 'clear returns a status')", (ITEM,))
    for path in ("examples/termui/termui.py", "src/click/termui.py",
                 "src/click/_compat.py", "examples/other/other.py"):
        conn.execute("INSERT INTO code_index (grain, grain_kind) "
                     "VALUES (?, 'path')", (path,))
    # The indexer's sorted walk puts `examples/` before `src/` (night 165).
    for grain in (EXAMPLE, LIBRARY, "src/click/_compat.py::echo_via",
                  "src/click/termui.py::echo_via",
                  "examples/other/other.py::alone"):
        conn.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) "
                     "VALUES (?, 'symbol', 'function')", (grain,))
    conn.execute("INSERT INTO frame_rulings (id, kind, reason) VALUES "
                 "('examples', 'attached', 'Contains example code')")
    conn.execute("INSERT INTO frame_rulings (id, kind, reason) VALUES "
                 "('src', 'program', 'Source code for the main package')")
    conn.commit()
    return conn


def _specify(db, ref):
    sb = build("terminologist", db, mode="criteria")
    sb.call("criteria.specify", id="c_1", ticket_id="t1", text="x",
            surface_refs=[ref])
    return json.loads(sb.ctx.writes[-1][2]["surface_refs"])


def _guess(db, paths, symbols):
    sb = build("architect", db, mode="guess", session_id="s199",
               allow=prompts.mode_tools("architect", "guess"))
    sb.call("batches.guess", item_id=ITEM, paths=paths, symbols=symbols)
    return [w[2]["grain"] for w in sb.ctx.writes
            if w[0] == "touch_guesses" and "grain" in w[2]]


def test_s214_bare_clear_stores_the_programs_row(db):
    assert _specify(db, "clear") == [LIBRARY]


def test_s199_bare_clear_with_its_own_path_writes_a_guess(db):
    assert _guess(db, ["src/click/termui.py"], ["clear"]) == [
        "src/click/termui.py", LIBRARY]


def test_the_frame_ranks_when_the_paths_hold_neither_row(db):
    assert _guess(db, ["src/click/_compat.py"], ["clear"]) == [
        "src/click/_compat.py", LIBRARY]


def test_two_program_rows_are_refused_with_the_program_first(db):
    db.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) VALUES "
               "('examples/termui/termui.py::echo_via', 'symbol', 'function')")
    db.commit()
    with pytest.raises(ValueError) as e:
        _specify(db, "echo_via")
    text = str(e.value)
    assert text.index("src/click/_compat.py::echo_via") < text.index(
        "src/click/termui.py::echo_via") < text.index(
        "examples/termui/termui.py::echo_via")
    with pytest.raises(ValueError) as g:
        _guess(db, ["examples/other/other.py"], ["echo_via"])
    assert str(g.value).startswith(text)
    assert str(g.value).endswith("Or leave symbols out")


def test_a_qualified_example_with_a_program_twin_is_refused_at_the_surface(db):
    """The general build of 2026-10-26 20:37: the surface door reads the
    frame's kind, so an attached `clear` with a program twin is refused.
    The guess keeps a qualified path as written."""
    with pytest.raises(ValueError, match=LIBRARY):
        _specify(db, EXAMPLE)
    assert _guess(db, ["src/click/termui.py"], [EXAMPLE]) == [
        "src/click/termui.py", EXAMPLE]


def test_a_single_row_name_is_unchanged_at_both_doors(db):
    """The text and the stored grain are those of 23588406."""
    assert _specify(db, "alone") == ["examples/other/other.py::alone"]
    with pytest.raises(ValueError) as e:
        _guess(db, ["src/click/termui.py"], ["alone"])
    assert str(e.value) == (
        "alone names no path. A symbol is written path::name. The index "
        "holds examples/other/other.py::alone. Write the symbol that way, "
        "or leave symbols out")


def test_with_no_frame_the_example_is_attached(db):
    db.execute("DELETE FROM frame_rulings")
    db.commit()
    assert _specify(db, "clear") == [LIBRARY]


def test_a_class_of_another_case_is_not_the_bare_name(db):
    """Review 1, finding 1: LIKE ignores case, so `clear` found `Clear`."""
    db.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) VALUES "
               "('src/click/_compat.py::Clear', 'symbol', 'class')")
    db.commit()
    assert _specify(db, "clear") == [LIBRARY]
    assert _guess(db, ["src/click/_compat.py"], ["clear"]) == [
        "src/click/_compat.py", LIBRARY]


def test_the_frame_ruling_outranks_is_attached(db):
    """Review 1, finding 2: the ruling decides where the heuristic differs."""
    db.execute("DELETE FROM frame_rulings")
    db.execute("INSERT INTO frame_rulings (id, kind, reason) VALUES "
               "('examples', 'program', 'The examples are the product')")
    db.execute("INSERT INTO frame_rulings (id, kind, reason) VALUES "
               "('src', 'attached', 'Vendored')")
    db.commit()
    assert _specify(db, "clear") == [EXAMPLE]


def test_a_bare_name_and_its_qualified_form_write_one_grain(db):
    """Review 1, finding 3."""
    assert _guess(db, ["src/click/termui.py"], ["clear", LIBRARY]) == [
        "src/click/termui.py", LIBRARY]
