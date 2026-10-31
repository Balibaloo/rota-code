"""Facts F20 and F21: one reader for quarantined keys, and words for a person.

The root-cause audit of 2026-10-27 counted ten readers that split a tick key
by their own rule, a lift that matched `_` as a wildcard, and raw ledger
writes that skipped the lift (frame 242). Night 170 ended with
`tester|tick:tests_missing|b_3` quarantined, and the principal's page said
"tests_missing for b_3".
"""
from __future__ import annotations

import pytest

from rota.core.db import Write, _lift_quarantines, init_db


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _quarantine(db, key: str, attempts: int = 3) -> None:
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
               "reported) VALUES (?, ?, 1, 0)", (key, attempts))


def _keys(db) -> set[str]:
    return {r["tick_key"] for r in db.execute("SELECT tick_key FROM tick_attempts")}


def test_night_170s_page_says_the_tests_missing_key_in_his_words(db):
    from rota.roles.principal import render_state

    _quarantine(db, "tester|tick:tests_missing|b_3")
    page = render_state(db)
    assert "tests_missing" not in page and "tick:" not in page, page
    assert ("Stuck: the team could not write the tests for "
            "b_3 after 3 attempts.") in page, page


def test_a_parked_ledger_entry_lifts_the_keys_about_it(db):
    """`park_merged` set a ledger status through a raw write, and the lift
    never ran (frame 242)."""
    from rota.core.lifecycle import park_merged

    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES ('i_1', 'the tool prints JSON', 'in_scope', 'approved', 1, 1)")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b_1', 'i_1', 'merged')")
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "author) VALUES ('l_1', 'i_1', 'items', 'JSON on stdout', 'architect')")
    _quarantine(db, "liaison|tick:agenda|l_1")
    assert park_merged(db, "b_1") == ["l_1"]
    assert "liaison|tick:agenda|l_1" not in _keys(db)


def test_the_lift_matches_a_ref_whole_and_never_as_a_pattern(db):
    """The LIKE of the lift read `_` as a wildcard and ignored case (frame
    242, a probe of frame 240's review)."""
    for ref in ("a_b", "aXb", "A_B"):
        _quarantine(db, f"vision_keeper|tick:contested|{ref}")
    _lift_quarantines(db, Write("items", "a_b", {"approval": "approved"},
                                op="update", amends=False), True)
    assert _keys(db) == {"vision_keeper|tick:contested|aXb",
                         "vision_keeper|tick:contested|A_B"}


def test_an_area_both_survey_roles_gave_up_on_is_settled_for_both(db):
    """`_survey_wakes` kept the given-up area in a map of area to role, so
    the second role's key hid the first role's."""
    from rota.core.scheduler import _survey_wakes

    db.execute("INSERT INTO code_index (grain, grain_kind, area) "
               "VALUES ('src/a.py', 'path', 'src')")
    _quarantine(db, "terminologist|tick:survey|src")
    _quarantine(db, "architect|tick:survey|src")
    assert _survey_wakes(db) == []


def test_the_keys_of_a_batch_are_its_one_ref_keys_and_a_page_reads_pairs(db):
    from rota.core.scheduler import given_up, key_parts, quarantined_keys

    assert key_parts("critic|tick:finding_review|b_1,f_2") == (
        "critic", "tick:finding_review", ("b_1", "f_2"))
    assert key_parts("-|tick:constraint_zero|") == ("-", "tick:constraint_zero", ())
    _quarantine(db, "developer|tick:tests_failing|b_1")
    _quarantine(db, "critic|tick:finding_review|b_1,f_2")
    _quarantine(db, "-|do:park|b_1")
    _quarantine(db, "-|tick:constraint_zero|")
    assert given_up(db, "b_1") == ["developer|tick:tests_failing|b_1"]
    assert quarantined_keys(db, ["b_1"], pairs=True, constraint_zero=False) == [
        "-|do:park|b_1", "critic|tick:finding_review|b_1,f_2",
        "developer|tick:tests_failing|b_1"]


# Pass 1b: the review of pass 1, `plans/f20-review-p1.md`.

def _night_170_batch(db, status: str = "running") -> None:
    """b_3 of night 170: a batch whose Tester key gave up on its tests."""
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
               "VALUES ('format_filename_example', 'show an example', 'in_scope', "
               "'approved', 1, 1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('tk_3', 'format_filename_example', 'the docstring shows it')")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES "
               "('b_3', 'format_filename_example', ?)", (status,))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b_3', 'tk_3')")
    for key in ("tester|tick:tests_missing|b_3", "developer|tick:tests_failing|b_3",
                "-|do:park|b_3"):
        _quarantine(db, key)


def _touch(db) -> None:
    # s217's write: the Architect's touch set of b_3, as `session_commit`
    # applies it.
    from rota.core.db import _apply_write, batch_reads, lift_moved_reads

    w = Write("batch_touch", "b_3:src/click/utils.py",
              {"batch_id": "b_3", "grain": "src/click/utils.py",
               "grain_kind": "path", "confidence": "expected"})
    before = batch_reads(db, [w])
    _apply_write(db, w, "architect")
    lift_moved_reads(db, before)


def test_s217s_touch_write_lifts_the_testers_key_of_b_3(db):
    """Night 170's s217 rewrote b_3's touch set, and the Tester's key stayed.
    Frame 318 keeps the Developer's red key, and the park key waits for a
    commit (frame 86)."""
    _night_170_batch(db)
    _touch(db)
    assert _keys(db) == {"developer|tick:tests_failing|b_3", "-|do:park|b_3"}


def test_two_identical_touch_writes_lift_once(db):
    """A rewrite of the same row changes nothing stored, so it lifts
    nothing, as frame 318 rules for a commit (F20 pass 1c)."""
    _night_170_batch(db)
    _touch(db)
    _quarantine(db, "tester|tick:tests_missing|b_3")
    _touch(db)
    assert "tester|tick:tests_missing|b_3" in _keys(db)


def test_a_touch_write_on_a_deferred_batch_lifts_nothing(db):
    """A deferred batch's given-up key waits for the principal (frame 87,
    ruled 2026-09-27)."""
    _night_170_batch(db, status="deferred")
    _touch(db)
    assert "tester|tick:tests_missing|b_3" in _keys(db)


def test_a_criterion_write_of_the_batch_lifts_the_testers_key(db):
    _night_170_batch(db)
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c_1', 'tk_3', 'the docstring shows a/b/c.txt as c.txt')")
    _lift_quarantines(db, Write("criteria", "c_1", {"text": "x"}), True)
    assert "tester|tick:tests_missing|b_3" not in _keys(db)


def test_a_landed_ruling_on_the_batchs_item_lifts_the_testers_key(db):
    """m103 of night 170 ruled on b_3's item, and the key stayed."""
    import json

    from rota.roles.principal import Answer, land, pending_asks

    _night_170_batch(db)
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m9','th','liaison','principal',"
               "'present',?,1,'open')", (json.dumps(["format_filename_example"]),))
    db.commit()
    (ask,) = pending_asks(db)
    assert land(db, ask, Answer(verb="verdict",
                                per_item={"format_filename_example": "approve"}))
    assert _keys(db) == {"developer|tick:tests_failing|b_3", "-|do:park|b_3"}


def test_a_kind_with_no_words_keeps_a_verb_and_no_internal_ref(db):
    from rota.roles.api import Ctx, code_gaps

    _quarantine(db, "vision_keeper|tick:orient|@program")
    _quarantine(db, "architect|tick:frame|@frame")
    facts = code_gaps(Ctx(conn=db, role="liaison"))["facts"]
    assert facts[:2] == [
        "The team could not finish a step for the whole program after 3 attempts",
        "The team could not finish a step after 3 attempts"], facts


def test_an_agenda_key_shows_no_ledger_id_and_the_line_says_the_team_once(db):
    from rota.roles.principal import render_state

    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "author) VALUES ('l_c1e73d2ef4', 'x', 'items', 'y', 'architect')")
    _quarantine(db, "liaison|tick:agenda|l_c1e73d2ef4")
    page = render_state(db)
    assert "l_c1e73d2ef4" not in page, page
    assert page.startswith("Stuck: a question to you got no answer after 3 "
                           "attempts."), page
    assert "gave up: the team" not in page


def test_a_commit_forgets_the_red_key_of_its_batch_and_no_lookalike(db):
    """The deletes matched `%|tick:tests_failing|b_1`, so `_` was a wildcard."""
    from rota.core.db import write_state

    for b in ("b_1", "bX1"):
        db.execute("INSERT INTO items (id, text, kind) VALUES (?, 't', 'in_scope')",
                   (f"i{b}",))
        db.execute("INSERT INTO batches (id, item_id, status) VALUES (?, ?, 'deferred')",
                   (b, f"i{b}"))
        _quarantine(db, f"developer|tick:tests_failing|{b}")
    write_state(db, "batches", "b_1", "UPDATE batches SET head_commit = 'f1' "
                "WHERE id = 'b_1'", fields={"head_commit": "f1"})
    assert _keys(db) == {"developer|tick:tests_failing|bX1"}


def test_the_invariant_reads_a_pair_key_through_the_one_parse(db):
    from rota.tools.invariants import i6

    db.execute("INSERT INTO items (id, text, kind) VALUES ('i_1', 't', 'in_scope')")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b_1', 'i_1', 'merged')")
    _quarantine(db, "critic|tick:finding_review|b_1,f_2")
    assert [f.text for f in i6(db)] == [
        "quarantined critic|tick:finding_review|b_1,f_2 names merged b_1"]


# The one-reader pin of fact F20. A later session that reads a quarantine or
# splits a tick key by its own rule turns these tests red (rule C76).
import ast
from pathlib import Path

_PKG = Path(__file__).resolve().parents[2] / "rota"

# A write of the flag is not a read of the fact. Each site names its write.
_QUARANTINE_WRITES = {
    ("rota/core/db.py", "lift_keys"): "the one delete of a quarantined key",
    ("rota/core/db.py", "mark_ruled"): "marks the keys the principal answered",
    ("rota/core/loop.py", "step"): "marks the reported keys",
    ("rota/core/scheduler.py", "quarantine_overrun"): "sets the flag",
    ("rota/core/scheduler.py", "quarantine_stalled"): "sets the flag",
}

# These splits read no tick key. Each site names what it splits.
_PIPE_SPLITS = {
    ("rota/core/sandbox.py", "_scalar_kind"): "a type annotation union",
    ("rota/llm/toolproto.py", "_labelled"): "a markdown table row",
}


def _functions():
    for path in sorted(_PKG.rglob("*.py")):
        rel = path.relative_to(_PKG.parent).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                yield rel, node


def _own(fn):
    """The nodes of `fn` that no nested function holds."""
    stack = list(ast.iter_child_nodes(fn))
    while stack:
        node = stack.pop()
        yield node
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            stack.extend(ast.iter_child_nodes(node))


def test_only_quarantined_keys_reads_the_quarantine_flag():
    readers = set()
    for rel, fn in _functions():
        for node in _own(fn):
            if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                    and "quarantined = 1" in " ".join(node.value.split())):
                readers.add((rel, fn.name))
    allowed = {("rota/core/scheduler.py", "quarantined_keys"), *_QUARANTINE_WRITES}
    assert readers - allowed == set()
    assert ("rota/core/scheduler.py", "quarantined_keys") in readers


def test_only_key_parts_splits_a_tick_key():
    splitters = set()
    for rel, fn in _functions():
        for node in _own(fn):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr in ("split", "rsplit", "partition",
                                           "rpartition")
                    and node.args and isinstance(node.args[0], ast.Constant)
                    and node.args[0].value == "|"):
                splitters.add((rel, fn.name))
    allowed = {("rota/core/scheduler.py", "key_parts"), *_PIPE_SPLITS}
    assert splitters - allowed == set()
    assert ("rota/core/scheduler.py", "key_parts") in splitters
