"""
Frame 362, pass 1: the three doors that hand understanding to delivery.

On three merged dry runs no delivery seat acted on an understanding row
(`plans/onboarding-demand-read-2026-11-03.md`, sections 2 and 3). Three of
the four doors were broken in the wiring. The design page, section 3.A,
repairs them with today's records (`plans/design-onboarding-2026-11-03.md`).

- Door 1: the pushed `glossary.lookup` read the wake's refs, such as `bg_1`,
  as glossary ids, and said "the rows this wake named are gone."
- Door 2: the Developer and the Tester got no constraint, because no read
  pushed one and `model.load` needs ids the seat never saw.
- Door 3: once every area has a survey, `k0` has no binding, and the
  fail-safe loaded it as global with a false headline.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.core.runner import BOUND_KEY, build_prompt, push_working_set, session_sandbox
from rota.core.scheduler import Wake, constraints_for_grains
from rota.onboarding.boot import ZERO, refresh_constraint_zero
from rota.roles import api

# The dry3w7 copy of session ce483c7b. The test copies it and never opens
# the original for writing.
DRY3W7 = Path("C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/"
              "ce483c7b-be58-4d58-bfc4-db1081518842/scratchpad/dry3w7")
GONE = "the rows this wake named are gone."
CASELESS = "src/icalendar/caselessdict.py"


@pytest.fixture
def dry3(tmp_path):
    """A writable copy of dry3w7, with its `-wal` and `-shm`."""
    if not (DRY3W7 / "dry3.db").is_file():
        pytest.skip(f"the dry3w7 copy is not at {DRY3W7}")
    for suffix in ("", "-wal", "-shm"):
        src = DRY3W7 / f"dry3.db{suffix}"
        if src.is_file():
            shutil.copyfile(src, tmp_path / f"dry3.db{suffix}")
    db = init_db(tmp_path / "dry3.db")
    yield db
    db.close()


def _first_prompt(db, role, kind, batch="bg_1"):
    """The wake's pushed set and its user prompt, as the runner builds them."""
    wake = Wake(role, kind, refs=(batch,))
    sb = session_sandbox(db, wake, batch_id=batch)
    pushed = push_working_set(role, sb, wake)
    _, user = build_prompt(role, sb, wake, pushed, instructions="")
    return pushed, user


# ---------------------------------------------------------------------------
# Door 1: the pushed lookup reads the criteria's term_refs
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("role, kind", [("developer", "tick:batch_start"),
                                        ("tester", "tick:tests_missing")])
def test_door1_the_pushed_lookup_holds_the_criteria_term(dry3, role, kind):
    """dry3's `bg_1` has criteria c1 to c3, each with `term_refs`
    `["canonical_order"]`. The control before the frame: "gone"."""
    pushed, user = _first_prompt(db=dry3, role=role, kind=kind)
    rows = pushed["glossary.lookup"]
    assert isinstance(rows, list), rows
    assert [r["id"] for r in rows] == ["canonical_order"]
    assert rows[0]["sense_short"]
    assert GONE not in user
    assert '"canonical_order"' in user


def test_door1_criteria_with_no_term_get_a_note_and_not_gone(dry3):
    """A batch whose criteria name no term says so in one sentence."""
    dry3.execute("DELETE FROM refs WHERE src_table = 'criteria' AND kind = 'term'")
    dry3.commit()
    pushed, user = _first_prompt(dry3, "developer", "tick:batch_start")
    assert pushed["glossary.lookup"] == {
        "note": "The criteria of bg_1 name no glossary term."}
    assert GONE not in user


def test_door1_the_typed_lookup_is_unchanged(dry3):
    wake = Wake("developer", "tick:batch_start", refs=("bg_1",))
    sb = session_sandbox(dry3, wake, batch_id="bg_1")
    rows = sb.call("glossary.lookup", term="canonical_order")
    assert [r["id"] for r in rows] == ["canonical_order"]
    miss = sb.call("glossary.lookup", term="no_such_word")
    assert miss["senses"] == []


# ---------------------------------------------------------------------------
# Door 2: the constraints that bind the batch's files, pushed
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("role, kind", [("developer", "tick:batch_start"),
                                        ("tester", "tick:tests_missing")])
def test_door2_the_push_on_dry3_is_empty_and_says_so(dry3, role, kind):
    """No constraint binds `caselessdict.py` on dry3, the design's failure
    case of 3.A. The push holds a note and no row, and no false `k0`."""
    pushed, user = _first_prompt(dry3, role, kind)
    bound = pushed[BOUND_KEY]
    assert bound == {"note": "No constraint binds the files of this "
                             f"batch: {CASELESS}."}
    assert f"[{BOUND_KEY}]" in user


def _fixture_db(tmp_path):
    """Two areas, one constraint bound to a file of area `src/a`."""
    db = init_db(tmp_path / "rota.db")
    for grain, kind, area in (("src/a/one.py", "path", "src/a"),
                              ("src/a/one.py::f", "symbol", "src/a"),
                              ("src/b/two.py", "path", "src/b"),
                              ("src/b/two.py::g", "symbol", "src/b")):
        db.execute("INSERT INTO code_index (grain, grain_kind, area) "
                   "VALUES (?, ?, ?)", (grain, kind, area))
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES ('it', 'change f', 'in_scope', 'approved', 1, 1)")
    db.execute("INSERT INTO batches (id, item_id) VALUES ('b1', 'it')")
    db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) "
               "VALUES ('b1', 'src/a/one.py', 'path')")
    db.execute("INSERT INTO constraints (id, headline, text, is_global) VALUES "
               "('wire_format', 'the output format is fixed', "
               "'Programs outside read the output of f.', 0)")
    db.execute("INSERT INTO constraint_bindings (constraint_id, grain, grain_kind) "
               "VALUES ('wire_format', 'src/a/one.py', 'path')")
    db.commit()
    return db


def _survey(db, *areas):
    for area in areas:
        db.execute("INSERT INTO survey_records (id, area, outcome) "
                   "VALUES (?, ?, 'none_found')", (f"sv_{area}", area))
    refresh_constraint_zero(db)
    db.commit()


def test_door2_a_bound_constraint_is_pushed_with_its_text(tmp_path):
    db = _fixture_db(tmp_path)
    _survey(db, "src/a", "src/b")
    ctx = api.Ctx(conn=db, role="developer", batch_id="b1")
    assert api.bound_constraints(ctx, "b1") == [
        {"id": "wire_format", "headline": "the output format is fixed",
         "text": "Programs outside read the output of f."}]


def test_door2_an_unsurveyed_area_keeps_k0_in_the_push(tmp_path):
    db = _fixture_db(tmp_path)
    _survey(db, "src/b")
    ctx = api.Ctx(conn=db, role="developer", batch_id="b1")
    assert [r["id"] for r in api.bound_constraints(ctx, "b1")] == [
        ZERO, "wire_format"]


# ---------------------------------------------------------------------------
# Door 3: k0 leaves constraints_for_grains once the areas are surveyed
# ---------------------------------------------------------------------------

def test_door3_full_survey_on_dry3_drops_k0(dry3):
    """All 22 areas of the dry3w7 index have a survey record, 16 of them with
    code. Control before the frame: `k0` only."""
    areas = {r[0] for r in dry3.execute(
        "SELECT DISTINCT area FROM code_index WHERE area IS NOT NULL")}
    surveyed = {r[0] for r in dry3.execute("SELECT DISTINCT area FROM survey_records")}
    assert len(areas) == 22 and areas <= surveyed
    grains = [r[0] for r in dry3.execute(
        "SELECT grain FROM code_index WHERE grain = ? OR grain LIKE ?",
        (CASELESS, CASELESS + "::%"))]
    assert len(grains) > 1
    assert ZERO not in constraints_for_grains(dry3, grains)


def test_door3_one_unsurveyed_area_keeps_k0(tmp_path):
    db = _fixture_db(tmp_path)
    _survey(db, "src/a", "src/b")
    db.execute("DELETE FROM constraint_bindings WHERE constraint_id = 'wire_format'")
    db.commit()
    # Every area surveyed: k0 is unbound and leaves the result.
    assert ZERO not in constraints_for_grains(db, ["src/a/one.py::f", "src/b/two.py"])
    # One grain of an area with no survey record: k0 stays.
    db.execute("DELETE FROM survey_records WHERE area = 'src/b'")
    db.execute("DELETE FROM constraint_bindings WHERE constraint_id = ?", (ZERO,))
    db.commit()
    assert ZERO in constraints_for_grains(db, ["src/a/one.py::f", "src/b/two.py"])
    # A grain the index does not know keeps k0, by the fail-safe.
    db.execute("INSERT INTO survey_records (id, area, outcome) "
               "VALUES ('sv9', 'src/b', 'none_found')")
    db.commit()
    assert ZERO in constraints_for_grains(db, ["users_table"])


def test_door3_a_partial_survey_adds_k0_until_the_area_has_a_record(tmp_path):
    """Pass 1b: `k0` binds the area name `src/b`, and the exact match on
    `src/b/two.py` missed it. Control before the pass: no `k0`."""
    db = _fixture_db(tmp_path)
    _survey(db, "src/a")
    assert ZERO in constraints_for_grains(db, ["src/b/two.py"])
    assert ZERO not in constraints_for_grains(db, ["src/a/one.py"])
    _survey(db, "src/b")
    assert ZERO not in constraints_for_grains(db, ["src/b/two.py"])


def _structural_k0(db, monkeypatch, files):
    from rota.core import worktrees

    monkeypatch.setattr(worktrees, "batch_files", lambda conn, bid: list(files))
    wake = Wake("architect", "tick:structural_review", refs=("bg_1",))
    sb = session_sandbox(db, wake, batch_id="bg_1")
    pushed = push_working_set("architect", sb, wake)
    return [r for r in pushed["model.consult"] if r["id"] == ZERO]


def test_door3_the_structural_review_k0_row_is_true_on_dry3(dry3, monkeypatch):
    """The diff of `bg_1` is `caselessdict.py`, and its area has a survey
    record. Control before the pass: "this area has not been surveyed".
    The worktree of `bg_1` is gone, so the test gives the diff's files."""
    rows = _structural_k0(dry3, monkeypatch, [CASELESS])
    assert len(rows) == 1
    assert rows[0]["headline"] == "every touched area has a survey record"
    assert "unsurveyed areas" not in rows[0]
    stored = dry3.execute("SELECT headline FROM constraints WHERE id = ?",
                          (ZERO,)).fetchone()[0]
    assert stored == "this area has not been surveyed"


def test_door3_the_structural_k0_row_names_the_unsurveyed_area(dry3, monkeypatch):
    dry3.execute("DELETE FROM survey_citations WHERE survey_id IN (SELECT id "
                 "FROM survey_records WHERE area = 'src/icalendar')")
    dry3.execute("DELETE FROM survey_records WHERE area = 'src/icalendar'")
    dry3.commit()
    rows = _structural_k0(dry3, monkeypatch, [CASELESS])
    assert rows[0]["headline"] == "this area has not been surveyed"
    assert rows[0]["unsurveyed areas"] == ["src/icalendar"]


# ---------------------------------------------------------------------------
# Pass 1c: the review of passes 1 and 1b (plans/f362-review-p1.md)
# ---------------------------------------------------------------------------

NEW_TEST = "src/icalendar/tests/test_new_thing.py"


def test_p1c_a_new_file_in_a_surveyed_area_gets_no_k0(dry3, monkeypatch):
    """Finding 1, the review's probe: a file the index does not hold yet,
    under the surveyed area `src/icalendar/tests`. Control: `k0` with the
    stored headline."""
    assert ZERO not in constraints_for_grains(dry3, [NEW_TEST])
    assert ZERO not in constraints_for_grains(dry3, [NEW_TEST, CASELESS])
    dry3.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) "
                 "VALUES ('bg_1', ?, 'path')", (NEW_TEST,))
    dry3.commit()
    ctx = api.Ctx(conn=dry3, role="developer", batch_id="bg_1")
    bound = api.bound_constraints(ctx, "bg_1")
    assert isinstance(bound, dict) and ZERO not in str(bound), bound
    rows = _structural_k0(dry3, monkeypatch, [CASELESS, NEW_TEST])
    assert rows[0]["headline"] == "every touched area has a survey record"


def test_p1c_a_path_under_no_area_keeps_k0(tmp_path):
    db = _fixture_db(tmp_path)
    _survey(db, "src/a", "src/b")
    assert ZERO not in constraints_for_grains(db, ["src/a/new.py"])
    assert ZERO in constraints_for_grains(db, ["docs/new.rst"])


def test_p1c_the_k0_headline_is_true_beside_a_bound_constraint(dry3, monkeypatch):
    """Finding 2: a constraint bound to the diff stands beside `k0`."""
    dry3.execute("INSERT INTO constraints (id, headline, text, is_global) "
                 "VALUES ('wire', 'the wire format', 'Readers parse it.', 0)")
    dry3.execute("INSERT INTO constraint_bindings (constraint_id, grain, grain_kind) "
                 "VALUES ('wire', ?, 'path')", (CASELESS,))
    dry3.commit()
    rows = _structural_k0(dry3, monkeypatch, [CASELESS])
    assert rows[0]["headline"] == "every touched area has a survey record"


def test_p1c_an_empty_touch_set_says_nothing_was_checked(tmp_path):
    """Finding 3: with no file, no binding was checked."""
    db = _fixture_db(tmp_path)
    db.execute("DELETE FROM batch_touch")
    db.commit()
    ctx = api.Ctx(conn=db, role="developer", batch_id="b1")
    assert api.bound_constraints(ctx, "b1") == {
        "note": "The touch set of batch b1 is empty, so no binding was checked."}


@pytest.mark.parametrize("role, kind, refs", [
    ("terminologist", "tick:criteria", ("canonical_order_duplicate_keys",)),
    ("terminologist", "tick:criterion_repair", ("c1",)),
    ("architect", "tick:unresolved", ("m1",))])
def test_p1c_a_wake_with_no_batch_criteria_gets_no_pushed_lookup(
        dry3, role, kind, refs):
    """Finding 4: these wakes got a pushed order to call the lookup."""
    wake = Wake(role, kind, refs=refs)
    sb = session_sandbox(dry3, wake)
    if "glossary.lookup" not in sb.functions():
        pytest.skip(f"{kind} does not list glossary.lookup")
    pushed = push_working_set(role, sb, wake)
    assert "Call glossary.lookup" not in str(pushed.get("glossary.lookup", ""))
    assert GONE not in str(pushed.get("glossary.lookup", ""))


def test_p1c_an_answer_wake_with_a_batch_reads_the_criteria_terms(dry3):
    """Finding 7: a `message:answer` wake has a batch and no refs."""
    wake = Wake("developer", "message", refs=(), detail="answer")
    sb = session_sandbox(dry3, wake, batch_id="bg_1")
    rows = sb.call("glossary.lookup")
    assert [r["id"] for r in rows] == ["canonical_order"]


def test_p1c_the_constraint_key_follows_the_criteria_block(dry3):
    """Finding 6: the key was the last key, which a cut takes first."""
    pushed, _ = _first_prompt(dry3, "developer", "tick:batch_start")
    keys = list(pushed)
    assert keys[keys.index("criteria.load") + 1] == BOUND_KEY, keys
