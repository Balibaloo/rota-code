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

import ast
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
    authored = {t for t in journals if dbm.author_column(db, t)}
    # Pass 1b: `messages` joins under `from_role`. `config_history` has no
    # row key, so the rule leaves it out by name (review of pass 1, 1).
    assert authored == {"entries", "ledger", "faults", "decisions",
                        "messages"}
    for table in journals:
        assert dbm.author_refusal(db, table, "x", "tester", {"text": "t"}) \
            is None
    assert dbm.journal_author(db, "items", "i1") is None


def test_a_write_that_names_another_author_is_refused(db):
    """Review of pass 1, 3: a tester inserted a decision under the author
    "principal". Law 6: nothing is written on the principal's behalf."""
    with pytest.raises(JournalAuthorError, match="the write names principal "
                       "as the author of decisions row d1, and you write as "
                       "tester"):
        _apply_write(db, Write("decisions", "d1", {"author": "principal",
                                                   "text": "x"}), "tester")


def test_a_frame_note_is_the_architects_row(db):
    """Review of pass 1, 2: `frame.assign` stamped the author "frame", so a
    second Architect session over the same row failed whole at commit."""
    from rota.roles import api

    src = Path(api.__file__).read_text(encoding="utf-8")
    assert '"author": "frame"' not in src
    _ledger(db, "frame_src", "architect")
    _apply_write(db, Write("ledger", "frame_src",
                           {"default_taken": "again", "author": "architect"}),
                 "architect")


def test_only_the_asker_says_the_answer_did_not_land(db):
    """Review of pass 1, 5: `schedule_reask` read the asker by hand. It
    reads the rule now, over the sender of the question."""
    from rota.core.sandbox import build

    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
               "to_role, verb, body_refs, seq, status) VALUES ('mq', NULL, "
               "'mq', 'developer', 'architect', 'question', '[]', 1, "
               "'answered')")
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, "
               "to_role, verb, body_refs, seq, status) VALUES ('ma', 'mq', "
               "'mq', 'architect', 'tester', 'answer', '[]', 2, 'open')")
    db.commit()
    sb = build("tester", db, mode="normal")
    sb.ctx.trigger = "ma"
    with pytest.raises(ValueError) as exc:
        api_reask = __import__("rota.roles.api", fromlist=["x"]).schedule_reask
        api_reask(sb.ctx, "the step")
    assert str(exc.value) == (
        "mq is a messages row by developer, and you write as tester. A "
        "journal row is its author's record. Only the role that asked can "
        "say that the answer did not land.")


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


# SQL that reads an `author` column: in a select list, or in a condition.
# The SQL of the package is upper case, so prose in a docstring is no match.
_SQL_AUTHOR = re.compile(r"(?s)\bSELECT\b[^;]*?\bauthor\b"
                         r"|\bauthor\s+(?:IS|IN)\b|\bauthor\s*(?:=|!=|<>)")


def _is_role(node) -> bool:
    return ((isinstance(node, ast.Attribute) and node.attr == "role")
            or (isinstance(node, ast.Name) and node.id == "role"))


def _is_author_key(node) -> bool:
    if isinstance(node, ast.Subscript):
        return (isinstance(node.slice, ast.Constant)
                and node.slice.value == "author")
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get" and bool(node.args)
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value == "author")


def _is_index(node) -> bool:
    return (isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, int))


def author_reads(source: str) -> list[tuple[int, str]]:
    """Each read of an author in `source`, as (line, enclosing function).
    A read is SQL over an `author` column, a comparison of an `author` key,
    or a comparison of a row index with a role."""
    tree = ast.parse(source)
    funcs = sorted(((n.lineno, n.end_lineno, n.name) for n in ast.walk(tree)
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))),
                   key=lambda f: f[1] - f[0])

    def owner(line):
        return next((name for a, b, name in funcs if a <= line <= b),
                    "<module>")

    found = []
    for node in ast.walk(tree):
        hit = False
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            hit = bool(_SQL_AUTHOR.search(node.value))
        elif isinstance(node, ast.Compare):
            sides = [node.left, *node.comparators]
            hit = (any(_is_author_key(s) for s in sides)
                   or (any(_is_role(s) for s in sides)
                       and any(_is_index(s) for s in sides)))
        if hit:
            found.append((node.lineno, owner(node.lineno)))
    return found


# The one reader, and every other read with its reason. A new read of an
# author goes red until it reads `db.journal_author` or earns a line here.
_ALLOWED = {
    ("rota/core/db.py", "journal_author"): "the one reader",
    # Each read below loads the author to show it, and decides nothing.
    ("rota/cockpit/server.py", "snapshot"): "the operator's view",
    ("rota/core/runner.py", "_decisions_in"): "a row shown to a seat",
    ("rota/core/runner.py", "_resolve_refs"): "a row shown to a seat",
    ("rota/core/runner.py", "resolve_inbound"): "his decision shown first",
    ("rota/core/runner.py", "_thread_on_tests"): "the thread shows a row "
                                                 "under the role that wrote it",
    ("rota/roles/api.py", "decisions_search"): "a row shown to a seat",
    ("rota/roles/api.py", "ledger_list"): "a row shown to a seat",
    ("rota/roles/api.py", "transcript_quote"): "a row shown to a seat",
    # `config_history` has no row key, and the rule leaves it out.
    ("rota/core/config.py", "history"): "the history of a setting",
    # The author of an entry is the speaker. These read his words.
    ("rota/core/sandbox.py", "stage"): "his words",
    ("rota/roles/api.py", "repeated_sentence"): "his words",
    ("rota/roles/api.py", "_reply_sentence_fault"): "his words",
    ("rota/roles/api.py", "_material_words"): "his words",
    ("rota/roles/api.py", "_added_sentences"): "his words",
    ("rota/roles/api.py", "_principal_cause"): "his words",
    # Residue of pass 1b: a decision of one role, found by a filter on the
    # author. The report names both.
    ("rota/core/sandbox.py", "_carries_decision"): "residue",
    ("rota/core/sandbox.py", "architect_decision_on"): "residue",
}

# The reviewer's nine shapes of a second reader (review of pass 1, 6).
_PROBES = [
    'conn.execute("SELECT author FROM ledger WHERE id = ?", (r,))',
    'conn.execute("SELECT id, author FROM ledger WHERE id = ?", (r,))',
    'conn.execute("SELECT 1 FROM decisions WHERE id = ? AND author IS NOT ?", (r, role))',
    '"SELECT author "',
    'if row["author"] != ctx.role:\n    pass',
    'if row["author"] != role:\n    pass',
    'if ctx.role != row["author"]:\n    pass',
    'if row.get("author") != ctx.role:\n    pass',
    'if row[0] != ctx.role:\n    pass',
]


@pytest.mark.parametrize("shape", _PROBES)
def test_the_pin_sees_each_shape_of_a_second_reader(shape):
    assert author_reads(shape), shape


def test_the_pin_passes_a_read_that_is_no_author():
    assert not author_reads('if m["to_role"] == ctx.role:\n    pass\n'
                            '"INSERT INTO decisions (id, author) VALUES (?, ?)"')


def test_no_second_reader_of_a_journal_author_exists():
    """One reader: `db.journal_author`, and the rule `db.author_refusal`
    over it. The walk covers every module of the package."""
    root = Path(__file__).resolve().parents[2]
    found = set()
    for path in sorted((root / "rota").rglob("*.py")):
        rel = path.relative_to(root).as_posix()
        for line, func in author_reads(path.read_text(encoding="utf-8")):
            if (rel, func) not in _ALLOWED:
                found.add(f"{rel}:{line} {func}")
    assert not found, sorted(found)
