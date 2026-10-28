"""Fact F23: a journal row has one author.

Law 1 says that a journal has "one author per entry". Roman ruled on
2026-10-27 14:47 that the author is the role: "any session of the same
role may change the entry, as today". The root-cause audit of 2026-10-27
counted four hand checks in two functions, all on `decisions`. The other
journal tables had no check, and `db._apply_write` overwrote any row.
These tests pin the one rule in `db.author_refusal`, which the commit and
the doors read.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from rota.core import db as dbm
from rota.core.db import (JournalAuthorError, SessionResult, Write,
                          _apply_write, init_db, session_commit)


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _ledger(db, rid="l1", author="developer"):
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "author) VALUES (?, 'i1', 'items', 'assumed soft delete', ?)",
               (rid, author))


def _decision(db, rid="d1", author="principal", text="keep the invoices"):
    db.execute("INSERT INTO decisions (id, author, text, refs) VALUES "
               "(?, ?, ?, '[]')", (rid, author, text))


def test_a_write_over_another_roles_ledger_row_is_refused(db):
    """The ledger had no author check. A second role re-staged the row and
    took its authorship."""
    _ledger(db)
    w = Write("ledger", "l1", {"about_ref": "i1", "about_table": "items",
                               "default_taken": "assumed hard delete",
                               "status": "open", "author": "architect"})
    with pytest.raises(JournalAuthorError) as exc:
        _apply_write(db, w, "architect")
    assert str(exc.value) == (
        "l1 is a ledger row by developer, and you write as architect. A "
        "journal row is its author's record.")
    row = db.execute("SELECT author, default_taken FROM ledger").fetchone()
    assert tuple(row) == ("developer", "assumed soft delete")


def test_a_status_move_on_another_roles_ledger_row_lands(db):
    """A decision of another role resolves a ledger row (test_laws). A status
    move is no new authorship."""
    _ledger(db)
    _apply_write(db, Write("ledger", "l1", {"status": "resolved"},
                           amends=False), "vision_keeper")
    row = db.execute("SELECT author, status FROM ledger").fetchone()
    assert tuple(row) == ("developer", "resolved")


def test_a_session_of_the_same_role_may_change_the_entry(db):
    """Roman, 2026-10-27 14:47: "any session of the same role may change the
    entry, as today"."""
    _decision(db, author="developer")
    _apply_write(db, Write("decisions", "d1", {"author": "developer",
                                               "text": "drop the invoices"}),
                 "developer")
    assert db.execute("SELECT text FROM decisions").fetchone()[0] == \
        "drop the invoices"


def test_the_commit_refuses_an_overwrite_of_his_decision(db):
    """Night 166 W-G: `decisions.author` on his decision. The commit is the
    last place that sees the write, so the rule holds there too."""
    _decision(db)
    db.commit()
    with pytest.raises(JournalAuthorError, match="d1 is a decisions row by "
                       "principal, and you write as vision_keeper"):
        session_commit(db, SessionResult(
            session_id="s1", role="vision_keeper",
            writes=[Write("decisions", "d1", {"author": "vision_keeper",
                                              "text": "it is fine"})]))
    row = db.execute("SELECT author, text FROM decisions").fetchone()
    assert tuple(row) == ("principal", "keep the invoices")


def test_a_new_row_and_a_row_with_no_author_land(db):
    db.execute("INSERT INTO decisions (id, author, text, refs) VALUES "
               "('d2', '', 'no author on file', '[]')")
    _apply_write(db, Write("decisions", "d1", {"author": "tester",
                                               "text": "new"}), "tester")
    _apply_write(db, Write("decisions", "d2", {"author": "tester",
                                               "text": "mine now"}), "tester")
    assert db.execute("SELECT COUNT(*) FROM decisions WHERE author = "
                      "'tester'").fetchone()[0] == 2


def test_the_rule_covers_every_journal_table_with_an_author_column(db):
    """identity.py declares the journal tables. The rule reads the author
    column of each one that has the column, not a hand list."""
    from rota.core.identity import NATURAL_KEYS

    journals = {t for t, (kind, _) in NATURAL_KEYS.items() if kind == "journal"}
    authored = {t for t in journals
                if any(r[1] == "author"
                       for r in db.execute(f"PRAGMA table_info({t})"))}
    assert authored == {"entries", "ledger", "faults", "decisions",
                        "config_history"}
    assert dbm.journal_author(db, "items", "i1") is None


def test_the_decision_door_names_both_roles(db):
    """The door reads the one rule, so the refusal of the call and of the
    commit name the same facts."""
    from rota.core.sandbox import build

    _decision(db)
    db.commit()
    vk = build("vision_keeper", db, mode="normal")
    with pytest.raises(ValueError) as exc:
        vk.call("decisions.author", id="d1", text="it is fine")
    assert str(exc.value) == (
        "d1 is a decisions row by principal, and you write as vision_keeper. "
        "A journal row is its author's record. Write yours under a new id.")
    assert not vk.ctx.writes


_ALLOWED = {Path("rota/core/db.py")}
_SECOND_READER = re.compile(
    r"SELECT\s+author\s+FROM|\[\s*['\"]author['\"]\s*\]\s*[!=]=\s*ctx\.role")


def test_no_second_reader_of_a_journal_author_exists():
    """One reader: `db.journal_author`, and the rule `db.author_refusal`
    over it. A later reader that queries an author by hand goes red here.
    Name it in `_ALLOWED` only with a reason in its comment."""
    root = Path(__file__).resolve().parents[2]
    found = []
    for path in sorted((root / "rota").rglob("*.py")):
        rel = path.relative_to(root)
        if rel in _ALLOWED:
            continue
        text = path.read_text(encoding="utf-8")
        for n, line in enumerate(text.splitlines(), start=1):
            if _SECOND_READER.search(line):
                found.append(f"{rel.as_posix()}:{n}: {line.strip()}")
    assert not found, found
