"""
Frame 361: `lazy` is the default, and the lazy path gets its exit.

Roman ruled on 2026-11-03 at about 01:05 (ruling 1 on
`plans/design-onboarding-2026-11-03.md`): `lazy` is the default where he has
not chosen, and his choice overrides it. The deep dive's section 4 traced the
lazy path on dry3w7. The election deferred 240 rows to the ledger, and the
agenda then paged the same 7 rows on every answer, because no code read a
deferred row at a touch. Here the rows wait without a page, the state view
counts them in one sentence, and the touch note shows the rows bound to its
ground once.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from rota.core import predicates as P
from rota.core.db import init_db
from rota.core.lifecycle import first_touch_rows
from rota.core.loop import _perform
from rota.core.predicates import LAZY_WORDS, lazy_count, observed_entries
from rota.core.scheduler import tick_agenda
from rota.roles.principal import render_state, touch_words

# The dry3w7 copy of session ce483c7b. The test copies it and never opens
# the original for writing.
DRY3W7 = Path("C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/"
              "ce483c7b-be58-4d58-bfc4-db1081518842/scratchpad/dry3w7")
PROMPT = (Path(__file__).resolve().parents[2]
          / "rota/roles/prompts/liaison/observed_entries.md")
PATH = "src/icalendar/caselessdict.py"


@pytest.fixture
def dry3(tmp_path):
    """A writable copy of dry3w7 with the eager path undone, as the deep
    dive's probe `lazy_trace.py` undoes it: no principal page, no ledger."""
    if not (DRY3W7 / "dry3.db").is_file():
        pytest.skip(f"the dry3w7 copy is not at {DRY3W7}")
    for suffix in ("", "-wal", "-shm"):
        src = DRY3W7 / f"dry3.db{suffix}"
        if src.is_file():
            shutil.copyfile(src, tmp_path / f"dry3.db{suffix}")
    db = init_db(tmp_path / "dry3.db")
    db.execute("PRAGMA foreign_keys=OFF")
    db.execute("DELETE FROM messages WHERE to_role = 'principal'")
    db.execute("DELETE FROM ledger")
    db.commit()
    yield db
    db.close()


def _elect(db, choice):
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
               "('baseline_election', ?)", (json.dumps(choice),))
    db.commit()


def _drain(db):
    """Run the clerk's wakes of `observed_entries` until a seat's wake or
    nothing is left. Return the last wakes."""
    for _ in range(6):
        wakes = observed_entries(db)
        if not wakes or wakes[0].role != P.SCHEDULER:
            return wakes
        for w in wakes:
            _perform(db, w)
    return wakes


def _present(db, mid, refs, status="open"):
    seq = db.execute("SELECT COALESCE(MAX(seq), 0) + 1 FROM messages").fetchone()[0]
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, body_text, seq, status) VALUES "
               "(?, ?, 'liaison', 'principal', 'present', ?, 'note', ?, ?)",
               (mid, mid, json.dumps(refs), seq, status))
    db.commit()


def _batch(db, bid):
    item = db.execute("SELECT item_id FROM batches LIMIT 1").fetchone()["item_id"]
    db.execute("INSERT INTO batches (id, item_id, status) VALUES (?, ?, 'pending')",
               (bid, item))
    db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind, confidence) "
               "VALUES (?, ?, 'path', 'expected')", (bid, PATH))
    db.commit()
    return item


def test_with_no_election_the_predicate_takes_the_lazy_branch(dry3):
    # Control on 12c26a46: no election read as eager, a page of 240 rows.
    _drain(dry3)
    assert lazy_count(dry3) == 223
    assert not any(w.kind == "tick:observed_entries" for w in observed_entries(dry3))


def test_with_eager_elected_the_page_is_as_today(dry3):
    _elect(dry3, "eager")
    wakes = _drain(dry3)
    assert [w.kind for w in wakes] == ["tick:observed_entries"]
    # The run's page held 235 rows. The copy has no present, so all 240
    # rows of the probe's deferral are fresh.
    assert len(wakes[0].refs) == 240
    assert lazy_count(dry3) == 0


def test_under_lazy_the_state_names_the_count_and_the_agenda_pages_none(dry3):
    _elect(dry3, "lazy")
    _drain(dry3)
    assert dry3.execute("SELECT COUNT(*) FROM ledger WHERE status = 'open'"
                        ).fetchone()[0] == 223
    assert ("The team read the project and recorded 223 notes. "
            "Ask me to show them.") in render_state(dry3)
    # Control on 12c26a46: the same 7 rows on each of three wakes.
    for i in range(3):
        wakes = tick_agenda(dry3, principal_present=True)
        assert wakes == [], wakes
        _present(dry3, f"mprobe{i}", [], status="answered")


def test_the_first_touch_shows_the_bound_rows_once(dry3):
    _drain(dry3)
    before = lazy_count(dry3)
    item = _batch(dry3, "bg_t1")
    bound = first_touch_rows(dry3, "bg_t1")
    assert bound, "the area src/icalendar holds notes"
    tables = {r["about_table"] for r in dry3.execute(
        f"SELECT about_table FROM ledger WHERE id IN ({','.join('?' * len(bound))})",
        bound)}
    assert "model_areas" in tables and "glossary_terms" in tables

    assert [w.kind for w in P.touch_note(dry3)] == ["tick:touch_note"]
    _present(dry3, "mt1", ["bg_t1", item])
    words = touch_words(dry3, "bg_t1")
    assert "notes the team recorded about this ground" in words
    first = dry3.execute("SELECT default_taken FROM ledger WHERE id = ?",
                         (bound[0],)).fetchone()[0].removeprefix(LAZY_WORDS)
    assert first in words

    # The clerk takes the shown rows out of the open set.
    wakes = P.touch_note(dry3)
    assert [w.kind for w in wakes] == ["do:first_touch"]
    _perform(dry3, wakes[0])
    assert lazy_count(dry3) == before - len(bound)
    assert {r[0] for r in dry3.execute(
        f"SELECT status FROM ledger WHERE id IN ({','.join('?' * len(bound))})",
        bound)} == {"parked"}
    # The note reads the same after its rows left the open set.
    assert touch_words(dry3, "bg_t1") == words
    assert P.touch_note(dry3) == []

    # A second note on the same path names none of them.
    _batch(dry3, "bg_t2")
    assert first_touch_rows(dry3, "bg_t2") == []
    _present(dry3, "mt2", ["bg_t2", item])
    assert "notes the team recorded" not in touch_words(dry3, "bg_t2")
    assert P.touch_note(dry3) == []


def test_the_touch_note_names_ten_and_counts_the_rest(dry3):
    _drain(dry3)
    item = _batch(dry3, "bg_t3")
    # Bind twelve more notes to the touched area.
    rows = [r["id"] for r in dry3.execute(
        "SELECT id FROM glossary_terms WHERE area != 'src/icalendar' "
        "ORDER BY id LIMIT 12")]
    dry3.executemany("UPDATE glossary_terms SET area = 'src/icalendar' "
                     "WHERE id = ?", [(r,) for r in rows])
    dry3.commit()
    n = len(first_touch_rows(dry3, "bg_t3"))
    assert n > 10
    _present(dry3, "mt3", ["bg_t3", item])
    assert touch_words(dry3, "bg_t3").endswith(f"; and {n - 10} more")


def test_the_eager_prompt_names_the_first_id_and_the_door_adds_the_rest(tmp_path):
    text = PROMPT.read_text(encoding="utf-8")
    assert "**the first id in your wake's refs only**" in text
    assert "the door adds every row of the wake" in text
    assert "every id in your wake's refs" not in text

    from rota.llm.llm import Pins, ScriptedBackend
    from rota.core.runner import run_session
    from rota.testkit.fixtures import seed_provenance

    db = init_db(tmp_path / "rota.db")
    for i in range(1, 6):
        db.execute("INSERT INTO glossary_terms (id, term, sense_short) "
                   "VALUES (?, ?, 'a note')", (f"g{i}", f"word{i}"))
        seed_provenance(db, "glossary_terms", f"g{i}", "observed")
    _elect(db, "eager")
    wakes = observed_entries(db)
    assert [w.kind for w in wakes] == ["tick:observed_entries"]
    out = run_session(
        db, wakes[0],
        backend=ScriptedBackend([
            f"TOOL: msg.present_principal(refs=[\"{wakes[0].refs[0]}\"])", "done"]),
        pins=Pins(model="stub", temperature=0.0), instructions="present them")
    assert out.committed, out.errors
    sent = db.execute("SELECT body_refs FROM messages WHERE verb='present'").fetchone()
    assert sorted(json.loads(sent["body_refs"])) == sorted(wakes[0].refs)
