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
    # A retried step gets a second page, and the first page is answered
    # (review p5 of frame 354, finding 4).
    return db.execute("SELECT * FROM messages WHERE verb = 'present' "
                      "ORDER BY seq DESC").fetchone()


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
    assert "'try again'" in page and "'drop' on it to stop it" in page
    assert "starts building" not in page


def _rule_on_line(db, option, text="1 try again", row=None, rulings=None):
    """Pass 6: the Liaison path. The menu call of `rulings.rule` stages the
    ruling and its rows, and `apply_rulings` lands them."""
    from tests.rota.test_principal_reply import _landing
    from rota.roles.principal import apply_rulings, page_ask

    row = row or _present_critic(db)
    sb, _ = _landing(db, page_ask(row), text)
    out = sb.call("rulings.rule", rulings=rulings or {"1": option})
    for table, _op, values, *_ in sb.ctx.writes:
        if table in ("rulings", "ruled_refs"):
            cols = [c for c in values
                    if c in {r[1] for r in db.execute(
                        f"PRAGMA table_info({table})")}]
            db.execute(f"INSERT INTO {table} ({', '.join(cols)}) VALUES "
                       f"({', '.join('?' * len(cols))})",
                       [values[c] for c in cols])
    apply_rulings(db)
    return out, sb.ctx.writes


def test_drop_on_the_stalled_line_marks_the_step_ruled(db):
    """Review p4, findings 1 to 4: 'drop' ran the step again, 'Stuck' stayed
    for ever, and every ruling staged a false fault."""
    from rota.roles import api
    from rota.roles.principal import render_state

    out, writes = _rule_on_line(db, "drop", "1 drop it")
    assert out["per_item"] == {CRITIC_KEY: "approve"}
    att = _attempts(db)
    assert (att["quarantined"], att["reported"]) == (1, 2)
    assert not [w for w in writes if w[0] in ("faults", "fault")]
    assert db.execute("SELECT COUNT(*) FROM ruled_refs WHERE ref = ? AND "
                      "source = 'landed'", (CRITIC_KEY,)).fetchone()[0] == 1
    assert "Stuck" not in render_state(db)
    facts = api.code_gaps(api.Ctx(conn=db, role="liaison"))["facts"]
    assert "could not check" not in json.dumps(facts)


def test_try_again_on_the_stalled_line_lifts_the_step(db):
    out, writes = _rule_on_line(db, "try again")
    assert out["per_item"] == {CRITIC_KEY: "contest"}
    assert _attempts(db) is None
    assert not [w for w in writes if w[0] in ("faults", "fault")]


@pytest.mark.parametrize("option", ["contest", "approve"])
def test_the_stalled_line_takes_only_its_two_words(db, option):
    with pytest.raises(ValueError) as err:
        _rule_on_line(db, option)
    assert "takes try again; drop." in str(err.value)


def test_the_next_page_of_a_retried_step_reads_the_retry_back(db):
    """Review p5, findings 1, 3 and 4: the second page read his retry back
    as 'line 1 is wrong'. Review p7, finding 1: pass 8 read it back as
    'line 2 runs again' on a page whose line 2 was the read-back line. The
    step's own line carries the read-back, so the page has one line."""
    from rota.roles.principal import readings_owed

    _rule_on_line(db, "try again")
    (owed,) = readings_owed(db)
    # The step stalls again after his retry, and the Liaison presents it.
    row = _present_critic(db)
    page, order = render_page(db, "present", json.loads(row["body_refs"]),
                              None, ask_id=row["id"])
    assert order == [CRITIC_KEY]
    assert page.count("You asked me to try it again once before") == 1
    assert "as the team read it" not in page and "runs again" not in page
    assert "is wrong" not in page
    assert "'drop' on it to stop it" in page
    # His repeat on the step line rules the step anew, so the earlier
    # reading's row is superseded and owed no more.
    out, _ = _rule_on_line(db, "try again", row=row)
    assert out["per_item"] == {CRITIC_KEY: "contest"}
    assert owed not in readings_owed(db)


def test_a_retry_that_runs_through_reads_back_by_the_steps_words(db):
    """Review p7, finding 1: the next page of other work does not show the
    step, so a line number of the earlier page names nothing there."""
    from rota.roles.principal import readings_owed

    _rule_on_line(db, "try again")
    (owed,) = readings_owed(db)
    _seed_item(db, "I2", "the tool reads yaml")
    page, order = render_page(db, "present", ["I2", owed], None)
    assert order == ["I2", owed]
    assert ('  2. Your answer "1 try again", as the team read it: the step '
            'for the team could not check a claim for command runs '
            'again.') in page
    assert "line 1 runs again" not in page


def _seed_item(db, iid="I1", text="the tool prints json"):
    db.execute("INSERT INTO items (id, text, kind) VALUES (?, ?, 'in_scope')",
               (iid, text))


def test_a_stalled_again_step_after_a_mixed_reply_reads_its_retry_back(db):
    """Review p6, finding 1, probe p1: after '1 ok 2 try again' the next
    page read back '1 line approved' only."""
    from rota.roles.principal import read_back_rows, reading_line

    _seed_item(db)
    row = _present_critic(db, [CRITIC_KEY, "I1"])
    _, order = render_page(db, "present", json.loads(row["body_refs"]), None,
                           ask_id=row["id"])
    assert order == ["I1", CRITIC_KEY]
    out, _ = _rule_on_line(db, None, "1 ok 2 try again", row=row,
                           rulings={"1": "ok", "2": "try again"})
    assert out["per_item"] == {"I1": "approve", CRITIC_KEY: "contest"}
    row = _present_critic(db)
    page, order = render_page(db, "present", json.loads(row["body_refs"]),
                              None, ask_id=row["id"])
    assert order[0] == CRITIC_KEY and len(order) == 2
    # The step's line carries the retry, so the read-back line reads back
    # the other line only (review p7, finding 1).
    line = reading_line(db, order[1], order)
    assert "as the team read it: 1 line approved." in line
    assert "runs again" not in line
    assert line in page and page.count("as the team read it") == 1
    assert page.count("You asked me to try it again once before") == 1
    # The landing wake and the line read the same rows (review p6, finding 3).
    reply = order[1][len("reading:"):]
    assert {r["ref"] for r in read_back_rows(db, reply, order)} == {"I1"}
    assert {r["ref"] for r in read_back_rows(db, reply)} == {"I1", CRITIC_KEY}


@pytest.mark.parametrize("verdict", ["drop", "try again"])
def test_a_scripted_step_verdict_stages_no_fault(db, verdict):
    """Review p6, finding 2: the lift ran before the keypress rows, so the
    rows found no home and a fault said no table holds the step."""
    assert _land_script(db, verdict)
    assert db.execute("SELECT COUNT(*) FROM faults").fetchone()[0] == 0
    assert db.execute("SELECT COUNT(*) FROM ruled_refs WHERE ref = ? AND "
                      "source = 'keypress'", (CRITIC_KEY,)).fetchone()[0] == 1


def test_a_ruling_on_a_page_with_no_line_closes_the_ask(db):
    """dry1's rerun, turn 3: the present m3 had no line, and the door
    refused 'rest' three times. So the page never closed."""
    from tests.rota.test_principal_reply import _landing
    from rota.roles.principal import apply_rulings, page_ask

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m3', 'th', 'liaison', "
               "'principal', 'present', '[]', 1, 'open')")
    row = db.execute("SELECT * FROM messages WHERE id = 'm3'").fetchone()
    sb, _ = _landing(db, page_ask(row), "ok")
    out = sb.call("rulings.rule", rulings={"rest": "approve"})
    assert out["per_item"] == {}
    assert "no line" in out["note"] and "nothing is ruled" in out["note"]
    for table, _op, values, *_ in sb.ctx.writes:
        if table == "rulings":
            cols = [c for c in values if c in {r[1] for r in db.execute(
                "PRAGMA table_info(rulings)")}]
            db.execute(f"INSERT INTO rulings ({', '.join(cols)}) VALUES "
                       f"({', '.join('?' * len(cols))})",
                       [values[c] for c in cols])
    apply_rulings(db)
    assert db.execute("SELECT status FROM messages WHERE id = 'm3'"
                      ).fetchone()["status"] == "answered"
    assert db.execute("SELECT COUNT(*) FROM ruled_refs").fetchone()[0] == 0


def test_a_line_key_on_a_page_with_no_line_owes_a_read_back(db):
    """Review p7, finding 5: his "1 drop" on a page with no line closed the
    ask, and nothing told him that his word ruled nothing."""
    from tests.rota.test_principal_reply import _landing
    from rota.roles.principal import (READ_BACK_ASK, apply_rulings, page_ask,
                                      reading_line, readings_owed)

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m3', 'th', 'liaison', "
               "'principal', 'present', '[]', 1, 'open')")
    row = db.execute("SELECT * FROM messages WHERE id = 'm3'").fetchone()
    sb, reply = _landing(db, page_ask(row), "1 drop")
    out = sb.call("rulings.rule", rulings={"1": "drop"})
    assert out["per_item"] == {}
    assert "nothing is ruled" in out["note"]
    for table, _op, values, *_ in sb.ctx.writes:
        if table in ("rulings", "ruled_refs"):
            cols = [c for c in values if c in {r[1] for r in db.execute(
                f"PRAGMA table_info({table})")}]
            db.execute(f"INSERT INTO {table} ({', '.join(cols)}) VALUES "
                       f"({', '.join('?' * len(cols))})",
                       [values[c] for c in cols])
    apply_rulings(db)
    assert db.execute("SELECT status FROM messages WHERE id = 'm3'"
                      ).fetchone()["status"] == "answered"
    assert db.execute("SELECT COUNT(*) FROM faults").fetchone()[0] == 0
    assert readings_owed(db) == [f"reading:{reply}"]
    assert reading_line(db, f"reading:{reply}") == (
        'Your answer "1 drop", as the team read it: the page had no line, so '
        'your answer landed on no line.' + READ_BACK_ASK)


def test_a_bare_number_on_a_step_beside_a_criterion_names_the_step(db):
    """Review p6, finding 4: 'N try again' named every line of the page, so
    the door asked for an option on the criterion too."""
    _seed_item(db)
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('T1', 'I1', 'print json')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('C1', 'T1', 'the output parses as json')")
    row = _present_critic(db, [CRITIC_KEY, "C1"])
    _, order = render_page(db, "present", json.loads(row["body_refs"]), None,
                           ask_id=row["id"])
    assert "C1" in order
    n = order.index(CRITIC_KEY) + 1
    out, _ = _rule_on_line(db, None, f"{n} try again", row=row,
                           rulings={str(n): "try again"})
    assert out["per_item"][CRITIC_KEY] == "contest"
    assert {v for k, v in out["per_item"].items() if k != CRITIC_KEY} == {
        "approve"}


def _land_script(db, verdict):
    """A script that copies the page's word into `per_item`."""
    from rota.roles.principal import Answer, land, page_ask

    row = _present_critic(db)
    return land(db, page_ask(row), Answer(
        verb="verdict", text=f"1 {verdict}", per_item={CRITIC_KEY: verdict}))


def test_a_scripted_drop_on_a_step_marks_it_ruled(db):
    """Review p5, finding 2: a scripted 'drop' closed the ask and left the
    step at 'Stuck'."""
    from rota.roles.principal import render_state

    assert _land_script(db, "drop")
    att = _attempts(db)
    assert (att["quarantined"], att["reported"]) == (1, 2)
    assert "Stuck" not in render_state(db)


def test_a_scripted_step_verdict_off_its_menu_is_refused(db):
    with pytest.raises(ValueError) as err:
        _land_script(db, "park")
    assert "try again; drop" in str(err.value)
    assert db.execute("SELECT COUNT(*) FROM messages WHERE verb = 'present' "
                      "AND status = 'open'").fetchone()[0] == 1
