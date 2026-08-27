"""
The identity registry's trial run.

The principal's caution, verbatim: "the approach needs designing here, be
careful" -- and then "ok lets test it out". So the rule runs as an ordinary
test before it is a law: every table in the schema declares its sameness
rule, a new table fails the build until classified, and `unkeyed` is a legal
answer that stays visible instead of a gap that stays invisible. LAWS.md is
untouched; if this lint lives quietly, the law is just naming a fact.
"""
from __future__ import annotations

import re

from rota import paths
from rota.core.identity import NATURAL_KEYS

KINDS = {"words", "span", "term", "slug", "relation", "supersede", "content",
         "keyed", "journal", "ephemeral", "unkeyed"}


def _schema_tables() -> set[str]:
    sql = paths.SCHEMA.read_text(encoding="utf-8")
    return set(re.findall(r"CREATE TABLE IF NOT EXISTS (\w+)", sql))


def test_every_table_declares_what_makes_two_rows_the_same():
    """A new table fails here until it answers the question the four healed
    organs each learned by incident."""
    tables = _schema_tables()
    missing = sorted(tables - set(NATURAL_KEYS))
    assert not missing, (
        f"{missing} declare no sameness rule. Add each to NATURAL_KEYS -- "
        f"'unkeyed' with a reason is a legal answer; silence is not")


def test_the_registry_names_no_phantom_tables():
    stray = sorted(set(NATURAL_KEYS) - _schema_tables())
    assert not stray, f"NATURAL_KEYS classifies tables that do not exist: {stray}"


def test_every_kind_is_from_the_declared_vocabulary():
    bad = sorted((t, k) for t, (k, _) in NATURAL_KEYS.items() if k not in KINDS)
    assert not bad, bad


def test_every_entry_says_where_or_why():
    """A classification with no enforcement note is a label; the registry's
    value is that each row points at the door that holds its rule."""
    empty = sorted(t for t, (_, why) in NATURAL_KEYS.items()
                   if len(why.strip()) < 10)
    assert not empty, empty


def test_the_unkeyed_column_is_small_and_named():
    """The honest column stays visible: today it is exactly the two tables
    that have never produced an over-production incident. If this list grows,
    a new table took the easy answer -- make it argue its case here."""
    unkeyed = sorted(t for t, (k, _) in NATURAL_KEYS.items() if k == "unkeyed")
    assert unkeyed == ["business_rules", "items"], unkeyed


def test_the_lint_can_fail():
    """A fabricated table must trip the coverage check."""
    tables = _schema_tables() | {"widgets"}
    missing = sorted(tables - set(NATURAL_KEYS))
    assert "widgets" in missing
