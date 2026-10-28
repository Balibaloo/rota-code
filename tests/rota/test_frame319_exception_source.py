"""Frame 319: a criterion names no exception that no source holds.

Night 162's Terminologist s157, on `tick:criteria` for b_2, wrote c2 with
"must raise UsageError if stdin is closed". His words said "instead of
aborting", and `confirm` runs `raise Abort() from None`. The name came from
the glossary row `usageerror`. The texts below are s157's turn 1, word for
word, from `plans/night162-s157-read.md` section 5.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.runner import RAISE_LINES_KEY, push_working_set
from rota.core.sandbox import build
from rota.core.scheduler import Wake
from rota.roles import prompts
from rota.testkit.fixtures import seed_ref

ITEM = "confirm_default_on_eof"
TICKET = "tk_1_confirm_default_on_eof"
SAID = ("Let confirm() take a default_on_eof flag: when stdin is closed it "
        "returns the default instead of aborting.")
ITEM_TEXT = SAID + " The flag defaults to False, so nothing changes for existing callers."
HEADLINE = ("let confirm() take a default_on_eof flag: when stdin is closed it "
            "returns the default instead of aborting")
C2 = ("When default_on_eof is False (the default), confirm() must raise "
      "UsageError if stdin is closed, preserving existing behavior.")
C3 = ("When default_on_eof is True and stdin is closed, confirm() must return "
      "the provided default value instead of raising an error.")

TERMUI = '''from .exceptions import Abort
from .exceptions import UsageError


def confirm(text, default=False):
    """Prompts for confirmation.

    If the user aborts the input by sending an interrupt signal this
    function will catch it and raise a :exc:`Abort` exception.
    """
    while True:
        try:
            value = input(text)
        except (KeyboardInterrupt, EOFError):
            raise Abort() from None
        if value in ("y", "n"):
            return value == "y"
    raise Abort()


def edit(text):
    raise UsageError("Editing failed")
'''

EXCEPTIONS = '''class ClickException(Exception):
    pass


class UsageError(ClickException):
    pass


class Abort(RuntimeError):
    pass
'''


@pytest.fixture
def db(tmp_path):
    root = tmp_path / "project"
    (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "termui.py").write_bytes(TERMUI.encode())
    (root / "src" / "click" / "exceptions.py").write_bytes(EXCEPTIONS.encode())
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('project_root', ?)",
                 (str(root),))
    # Spans are 0-based, and the end is one past the definition.
    for grain, kind, start, end in (
            ("src/click/termui.py::confirm", "function", 4, 18),
            ("src/click/termui.py::edit", "function", 20, 22),
            ("src/click/exceptions.py::ClickException", "class", 0, 2),
            ("src/click/exceptions.py::UsageError", "class", 4, 6),
            ("src/click/exceptions.py::Abort", "class", 8, 10)):
        conn.execute("INSERT INTO code_index (grain, grain_kind, sym_kind, line_start, "
                     "line_end) VALUES (?, 'symbol', ?, ?, ?)", (grain, kind, start, end))
    conn.execute("INSERT INTO entries (id, author, ts_order, text) VALUES ('e1','principal',1,?)",
                 (SAID,))
    conn.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, status) "
                 "VALUES ('s1','e1',0,?,?,'ratified')", (len(SAID), SAID))
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES (?, ?, 'in_scope', 'approved', 1, 1)", (ITEM, ITEM_TEXT))
    seed_ref(conn, "items", ITEM, "statement", "s1")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES (?, ?, ?)",
                 (TICKET, ITEM, HEADLINE))
    conn.execute("INSERT INTO glossary_terms (id, term, sense_short) VALUES "
                 "('usageerror', 'UsageError', 'exception for invalid user input')")
    conn.commit()
    return conn


def _seat(db):
    return build("terminologist", db, mode="criteria",
                 allow=prompts.mode_tools("terminologist", "criteria"))


def _specify(sb, cid, text, term_refs, surface_refs=("confirm",)):
    return sb.call("criteria.specify", id=cid, ticket_id=TICKET, text=text,
                   term_refs=term_refs, surface_refs=list(surface_refs))


def test_s157_c2_is_refused_with_the_raise_line_of_confirm(db):
    with pytest.raises(Exception) as err:
        _specify(_seat(db), "c2_confirm_default_on_eof_false", C2,
                 ["option", "usageerror"])
    said = str(err.value)
    assert "UsageError" in said
    assert "Abort" in said
    assert "line 15: raise Abort() from None" in said, said


def test_s157_c3_names_no_exception_and_lands(db):
    sb = _seat(db)
    assert _specify(sb, "c3_confirm_default_on_eof_true", C3, ["option"])["id"] \
        == "c3_confirm_default_on_eof_true"


def test_a_criterion_that_names_abort_lands(db):
    sb = _seat(db)
    text = ("When default_on_eof is False (the default), confirm() must raise "
            "Abort if stdin is closed.")
    assert _specify(sb, "c2", text, ["option"])["id"] == "c2"


def test_an_exception_his_statement_names_lands(db):
    words = "When the flag is off and stdin is closed, confirm raises UsageError."
    db.execute("INSERT INTO entries (id, author, ts_order, text) VALUES ('e2','principal',2,?)",
               (words,))
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, status) "
               "VALUES ('s2','e2',0,?,?,'ratified')", (len(words), words))
    seed_ref(db, "items", ITEM, "statement", "s2")
    db.commit()
    sb = _seat(db)
    assert _specify(sb, "c2", C2, ["option", "usageerror"])["id"] == "c2"


def test_a_surface_the_index_does_not_hold_leaves_the_door_silent(db):
    # F10: the item gives `confirm()`, so the surface door refuses the
    # invented name first. The exception door stays silent on it.
    sb = _seat(db)
    with pytest.raises(ValueError) as refused:
        _specify(sb, "c2", C2, ["option", "usageerror"],
                 surface_refs=("confirm_with_default_on_eof_flag",))
    assert "the item names confirm" in str(refused.value)
    assert "is in none of his words" not in str(refused.value)


def test_the_criteria_wake_shows_the_raise_line_of_confirm(db):
    pushed = push_working_set("terminologist", _seat(db),
                              Wake("terminologist", "tick:criteria", refs=(ITEM,)))
    block = pushed.get(RAISE_LINES_KEY) or {}
    assert "line 15: raise Abort() from None" in block.get(
        "src/click/termui.py::confirm", ""), pushed.keys()


def _many_callables(db, n=30):
    """More than the 20 rows `code.callables` pushes, all depended on more
    than `confirm`, so the named one sits past the cut (review 1, finding 1)."""
    for i in range(n):
        db.execute("INSERT INTO code_index (grain, grain_kind, sym_kind, fan_in) VALUES "
                   "(?, 'symbol', 'function', 5)", (f"src/click/aaa.py::default_{i:02d}",))
    db.commit()


def test_the_criteria_wake_holds_the_source_of_a_callable_past_twenty(db):
    _many_callables(db)
    pushed = push_working_set("terminologist", _seat(db),
                              Wake("terminologist", "tick:criteria", refs=(ITEM,)))
    source = (pushed.get("code.source") or {}).get("src/click/termui.py") or {}
    assert "raise Abort() from None" in str(source.get("text", "")), pushed.get("code.source")


def test_s157_c2_with_no_surface_reads_the_callables_the_headline_names(db):
    with pytest.raises(Exception) as err:
        _specify(_seat(db), "c2_confirm_default_on_eof_false", C2,
                 ["option", "usageerror"], surface_refs=())
    assert "line 15: raise Abort() from None" in str(err.value)
