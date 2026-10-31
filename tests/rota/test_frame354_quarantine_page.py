"""
Frame 354: constraint zero settles, and a quarantine report is never an
empty page.

Two causes, measured on clickI in 7 of 7 runs. The constraint zero predicate
wanted every area of the index, and the refresh bound only areas with code.
Before the Architect's frame, `docs` and `docs/_static` held no symbol, so
the step fired with no refs until quarantine. The quarantine wake then
passed on no ref for that key, the door accepted a present with no refs,
and the principal saw m3, a page with no lines.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from rota.core import predicates as P
from rota.core.db import init_db
from rota.core.runner import run_session
from rota.llm.llm import Pins, ScriptedBackend
from rota.onboarding import boot
from rota.roles.principal import render_page

PINS = Pins(model="stub", temperature=0.0)
ZERO_KEY = "-|tick:constraint_zero|"
ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "t.db")


def _pre_frame_clicki(db) -> None:
    """The heuristic partition of clickI before the frame, as the read of
    frame 354 rebuilt it from `.rota/dry1.db`: two areas with code and two
    areas of prose."""
    rows = [("setup.py", "path", "."), ("setup.py::main", "symbol", "."),
            ("src/click/core.py", "path", "src/click"),
            ("src/click/core.py::Command", "symbol", "src/click"),
            ("docs/index.rst", "path", "docs"),
            ("docs/_static/click-icon.svg", "path", "docs/_static")]
    db.executemany("INSERT INTO code_index (grain, grain_kind, area) "
                   "VALUES (?, ?, ?)", rows)


def test_constraint_zero_is_quiet_on_the_pre_frame_partition(db):
    _pre_frame_clicki(db)
    boot.refresh_constraint_zero(db)
    bound = {r["grain"] for r in db.execute(
        "SELECT grain FROM constraint_bindings WHERE constraint_id = ?",
        (boot.ZERO,))}
    assert bound == {".", "src/click"}
    assert boot.coded_areas(db) == [".", "src/click"]
    assert P.constraint_zero(db) == [], (
        "a prose area binds nothing, so the predicate must not want it")


def test_coded_areas_is_the_one_place_the_area_filter_lives():
    # An area-level read of the index with the symbol filter is a second
    # copy of `coded_areas`. File-level readers of symbol grains differ.
    for name in ("rota/core/predicates.py", "rota/core/scheduler.py"):
        lines = (ROOT / name).read_bytes().decode("utf-8").splitlines()
        for n, line in enumerate(lines):
            if "grain_kind" in line and "symbol" in line:
                near = "\n".join(lines[max(0, n - 3):n + 1])
                assert not re.search(r"DISTINCT\s+area", near), (
                    f"{name}:{n + 1} copies the filter of boot.coded_areas")
    from rota.core import scheduler

    surveyed, left = scheduler.constraint_zero_area_coverage(_coverage_db())
    assert left == {"src"}


def _coverage_db():
    import sqlite3

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE code_index (grain TEXT, grain_kind TEXT, area TEXT)")
    conn.execute("CREATE TABLE survey_records (area TEXT)")
    conn.executemany("INSERT INTO code_index VALUES (?, ?, ?)",
                     [("src/a.py::f", "symbol", "src"), ("docs/x.md", "path", "docs")])
    return conn


def _quarantine_zero(db) -> None:
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
               "reported) VALUES (?, 3, 1, 0)", (ZERO_KEY,))


def test_a_rowless_quarantined_key_reaches_the_liaisons_wake_as_a_ref(db):
    _quarantine_zero(db)
    (wake,) = P.quarantined(db)
    assert wake.refs == (ZERO_KEY,)


def test_render_page_numbers_one_line_for_the_rowless_key(db):
    _quarantine_zero(db)
    page, order = render_page(db, "present", [ZERO_KEY], None, stalled=[ZERO_KEY])
    assert order == [ZERO_KEY]
    assert "  1. the team could not read the code first after 3 attempts" in page


def _sessions(db, wake, call: str):
    db.commit()
    return run_session(db, wake, backend=ScriptedBackend([call, "done"]),
                       pins=PINS, instructions="present")


def test_a_present_with_no_refs_is_refused_and_sends_nothing(db):
    from rota.core.scheduler import Wake

    wake = Wake("liaison", "tick:quarantined", refs=(), detail="1 abandoned")
    out = _sessions(db, wake, "TOOL: msg.present_principal(refs=[])")
    assert not db.execute(
        "SELECT 1 FROM messages WHERE verb = 'present'").fetchone()
    assert "You sent no refs" in json.dumps(out.__dict__, default=str)


def test_the_quarantine_present_carries_the_key_and_numbers_it(db):
    _quarantine_zero(db)
    (wake,) = P.quarantined(db)
    out = _sessions(db, wake, "TOOL: msg.present_principal(refs=[])")
    assert out.committed, out.errors
    (row,) = db.execute("SELECT id, body_refs FROM messages "
                        "WHERE verb = 'present'").fetchall()
    assert ZERO_KEY in json.loads(row["body_refs"])
    page, order = render_page(db, "present", json.loads(row["body_refs"]),
                              None, ask_id=row["id"])
    assert ZERO_KEY in order
    assert "the team could not read the code first after 3 attempts" in page


CRITIC_KEY = "critic|tick:challenge|@claim:constraints:command"


@pytest.mark.parametrize("sent", [
    ["critic", "tick:challenge", "@claim:constraints:command"], ["critic"]])
def test_a_key_split_on_its_bars_lands_as_the_key(db, sent):
    """Pass 4: the cold run's s58 split the wake's key on `|`, and the door
    refused 'critic'. The door reads a part with no row as the key, once."""
    from rota.core.scheduler import Wake
    from rota.roles.principal import _gave_up_words

    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
               "reported) VALUES (?, 3, 1, 0)", (CRITIC_KEY,))
    wake = Wake("liaison", "tick:quarantined", refs=(CRITIC_KEY,),
                detail="1 abandoned")
    out = _sessions(db, wake,
                    f"TOOL: msg.present_principal(refs={json.dumps(sent)})")
    assert out.committed, out.errors
    (row,) = db.execute("SELECT id, body_refs FROM messages "
                        "WHERE verb = 'present'").fetchall()
    assert json.loads(row["body_refs"]) == [CRITIC_KEY]
    page, order = render_page(db, "present", [CRITIC_KEY], None,
                              ask_id=row["id"])
    assert order == [CRITIC_KEY]
    assert f"  1. {_gave_up_words(db, [CRITIC_KEY])[0]}" in page


GROUP_KEY = "reconciler|tick:reconcile|docs/a.md,docs/b.md"


def _quarantine(db, key) -> None:
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
               "reported) VALUES (?, 3, 1, 0)", (key,))


def test_a_regrouped_reconcile_key_is_a_stall_to_no_reader(db):
    """Pass 5: the group's files wake alone, so the group key stops nothing.
    Review p3, findings 2 and 5, found three readers that said otherwise."""
    from rota.core.scheduler import regrouped_key, rowless_key
    from rota.roles import api

    _quarantine(db, GROUP_KEY)
    assert regrouped_key(GROUP_KEY)
    assert P.quarantined(db) == []
    facts = api.code_gaps(api.Ctx(conn=db, role="liaison"))["facts"]
    assert "docs/a.md" not in json.dumps(facts)
    assert not rowless_key(db, GROUP_KEY)
    assert not api.ref_resolves(api.Ctx(conn=db, role="liaison"), GROUP_KEY)


def _present_critic(db, sent=None):
    from rota.core.scheduler import Wake

    _quarantine(db, CRITIC_KEY)
    wake = Wake("liaison", "tick:quarantined", refs=(CRITIC_KEY,),
                detail="1 abandoned")
    out = _sessions(db, wake, "TOOL: msg.present_principal(refs=%s)"
                    % json.dumps(sent or [CRITIC_KEY]))
    assert out.committed, out.errors
    return db.execute("SELECT * FROM messages WHERE verb = 'present'").fetchone()


def test_a_key_part_that_names_a_row_lands_as_the_key_once(db):
    row = _present_critic(db, ["@claim:constraints:command"])
    assert json.loads(row["body_refs"]) == [CRITIC_KEY]


def _attempts(db):
    return db.execute("SELECT attempts, quarantined, reported FROM tick_attempts "
                      "WHERE tick_key = ?", (CRITIC_KEY,)).fetchone()


def test_a_contest_on_the_stalled_line_runs_the_step_again(db):
    from rota.roles.principal import Answer, land, page_ask

    row = _present_critic(db)
    mid = land(db, page_ask(row), Answer(
        verb="verdict", text="1 contest: try again",
        per_item={CRITIC_KEY: "contest"}))
    assert mid
    # The lift deletes the quarantined row: no attempts, no `reported` mark.
    assert _attempts(db) is None
    ruled = db.execute("SELECT verdict FROM ruled_refs WHERE ref = ? AND "
                       "source = 'landed'", (CRITIC_KEY,)).fetchall()
    assert [r["verdict"] for r in ruled] == ["contest"]


def test_ok_on_a_page_of_one_stalled_step_drops_it(db):
    from rota.core.scheduler import rowless_key
    from rota.roles.principal import Answer, land, page_ask

    row = _present_critic(db)
    mid = land(db, page_ask(row), Answer(verb="verdict", text="ok"))
    assert mid
    att = _attempts(db)
    assert (att["quarantined"], att["reported"]) == (1, 2)
    assert db.execute("SELECT status FROM messages WHERE id = ?",
                      (mid,)).fetchone()["status"] == "answered"
    assert db.execute("SELECT 1 FROM ruled_refs WHERE ref = ? AND "
                      "source = 'landed'", (CRITIC_KEY,)).fetchone()
    # The next page numbers no line for the dropped step.
    assert not rowless_key(db, CRITIC_KEY)
    assert P.quarantined(db) == []
    page, order = render_page(db, "present", [CRITIC_KEY], None,
                              stalled=[k for k in [CRITIC_KEY]
                                       if rowless_key(db, k)])
    assert CRITIC_KEY not in order


def test_a_page_of_stalled_steps_only_says_what_a_reply_does(db):
    row = _present_critic(db)
    page, order = render_page(db, "present", json.loads(row["body_refs"]),
                              None, ask_id=row["id"])
    assert order == [CRITIC_KEY]
    assert "'try again'" in page and "'ok' on it to drop it" in page
    assert "starts building" not in page
