"""
Config remembers what it displaced.

`config` is deliberately the principal's direct-edit space -- the registry's
own words: "Configuration rather than an artefact, so the principal sets it
directly and 'humans do not edit artefacts' never comes under pressure." The
interview (2026-08-27) kept that position and added the missing half: a knob
that forgets its past turns "why is the challenge phase off on this run?"
into archaeology. So `config.set` appends a history row whenever a declared
setting actually changes -- who, what it displaced, and the cause the calling
code path already knows. Roles stay config-blind and config-mute; this is not
a tool, and no history is readable from any session.
"""
from __future__ import annotations

import pytest

from rota.core import config
from rota.core.db import init_db


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def test_a_first_set_records_that_there_was_nothing_before(db):
    config.set(db, "challenge", "off")
    (row,) = config.history(db, "challenge")
    assert row["old_value"] is None
    assert row["new_value"] == '"off"'
    assert row["author"] == "principal"


def test_a_change_records_what_it_displaced(db):
    config.set(db, "challenge", "off")
    config.set(db, "challenge", "full")
    newest = config.history(db, "challenge")[0]
    assert newest["old_value"] == '"off"'
    assert newest["new_value"] == '"full"'
    assert config.get(db, "challenge") == "full"


def test_writing_the_same_value_is_not_a_change(db):
    config.set(db, "challenge", "off")
    config.set(db, "challenge", "off")
    assert len(config.history(db, "challenge")) == 1, \
        "history records changes, not writes"


def test_an_undeclared_key_is_still_refused(db):
    with pytest.raises(config.UnknownSetting):
        config.set(db, "chalenge", "off")


def test_the_election_is_a_declared_setting_with_history(db):
    """`rota elect` used to write past the registry with raw SQL; the ruling
    the whole entry was about had the least-guarded write path in the file."""
    config.set(db, "baseline_election", "cnt_v2r")
    config.set(db, "baseline_election", "cnt_v3")
    rows = config.history(db, "baseline_election")
    assert [r["new_value"] for r in rows] == ['"cnt_v3"', '"cnt_v2r"']
    assert rows[1]["old_value"] is None, "the first election displaced nothing"


def test_a_run_from_before_the_table_reads_as_empty_history(db):
    db.execute("DROP TABLE config_history")
    assert config.history(db) == []
