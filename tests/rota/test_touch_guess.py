"""
The Architect's guess of the code one request item touches.

Frame 298's design (sections 1 and 4.1, ruled: Roman, 2026-10-18, "the
architect owns the guess"). The `guess` predicate wakes the Architect once per
request item and item version. The `batches.guess` op writes the guess set
into `touch_guesses`. Pass 1 builds the row, the op and the predicate. No page
shows the rows yet.
"""
from __future__ import annotations

import pytest

from rota.core.db import SessionResult, init_db, session_commit
from rota.core.sandbox import build
from rota.testkit.fixtures import seed_provenance

ITEM = "echo_json"
TEXT = "Add an echo_json helper next to echo that prints a value as JSON."


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval) "
                 "VALUES (?, ?, 'in_scope', 'draft')", (ITEM, TEXT))
    for grain, kind in (("src/click/utils.py", "path"),
                        ("src/click/utils.py::echo", "symbol"),
                        ("tests/test_utils.py", "path")):
        conn.execute("INSERT INTO code_index (grain, grain_kind) VALUES (?, ?)",
                     (grain, kind))
    conn.commit()
    return conn


def _fires(db) -> list:
    from rota.core.predicates import guess
    return [(w.role, w.kind, w.refs) for w in guess(db)]


def _guess_row(db, ver: int = 1, grain: str = "src/click/utils.py") -> None:
    db.execute("INSERT INTO touch_guesses (item_id, item_ver, grain, grain_kind) "
               "VALUES (?, ?, ?, 'path')", (ITEM, ver, grain))
    db.commit()


# ---------------------------------------------------------------------------
# The predicate
# ---------------------------------------------------------------------------

def test_the_predicate_fires_on_a_draft_request_item(db):
    assert _fires(db) == [("architect", "tick:guess", (ITEM,))]


def test_the_predicate_fires_on_an_approved_request_item(db):
    db.execute("UPDATE items SET approval = 'approved', approval_ver = 1")
    db.commit()
    assert _fires(db) == [("architect", "tick:guess", (ITEM,))]


def test_the_predicate_names_one_item_at_a_time_by_id(db):
    db.execute("INSERT INTO items (id, text, kind) VALUES "
               "('a_first', 'Add a flag.', 'in_scope')")
    db.commit()
    assert _fires(db) == [("architect", "tick:guess", ("a_first",))]


def test_a_parked_item_owes_no_guess(db):
    db.execute("INSERT INTO item_parks (id, item_id, kind, by, cause_id, seq) "
               "VALUES ('p1', ?, 'park', 'shift', 'm1', 1)", (ITEM,))
    db.commit()
    assert _fires(db) == []


def test_a_contested_item_owes_no_guess(db):
    db.execute("UPDATE items SET approval = 'contested'")
    db.commit()
    assert _fires(db) == []


def test_an_observed_item_owes_no_guess(db):
    seed_provenance(db, "items", ITEM, "observed")
    db.commit()
    assert _fires(db) == []


def test_the_account_owes_no_guess(db):
    db.execute("DELETE FROM items")
    db.execute("INSERT INTO items (id, text, kind) VALUES "
               "('how_it_works', 'What the code does.', 'in_scope')")
    db.commit()
    assert _fires(db) == []


def test_a_live_batch_with_a_prediction_owes_no_guess(db):
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1', ?, 'running')",
               (ITEM,))
    db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) "
               "VALUES ('b1', 'src/click/utils.py', 'path')")
    db.commit()
    assert _fires(db) == []


def test_a_live_batch_with_no_prediction_still_owes_the_guess(db):
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1', ?, 'pending')",
               (ITEM,))
    db.commit()
    assert _fires(db) == [("architect", "tick:guess", (ITEM,))]


def test_an_empty_index_owes_no_guess(db):
    db.execute("DELETE FROM code_index WHERE grain_kind = 'path'")
    db.commit()
    assert _fires(db) == []


def test_a_guess_at_the_items_version_drains_it_and_an_amendment_reopens_it(db):
    _guess_row(db, ver=1)
    assert _fires(db) == []
    db.execute("UPDATE items SET version = 2")
    db.commit()
    assert _fires(db) == [("architect", "tick:guess", (ITEM,))]


# ---------------------------------------------------------------------------
# The op
# ---------------------------------------------------------------------------

def _architect(db, session: str = "s1"):
    from rota.roles import prompts
    return build("architect", db, mode="guess", session_id=session,
                 allow=prompts.mode_tools("architect", "guess"))


def test_the_op_writes_paths_expected_and_symbols_possible(db):
    from rota.core.runner import _as_write
    db.execute("UPDATE items SET version = 3")
    db.commit()
    sb = _architect(db)
    out = sb.call("batches.guess", item_id=ITEM,
                  paths=["src/click/utils.py", "tests/test_utils.py"],
                  symbols=["src/click/utils.py::echo"])
    assert out == {"item_id": ITEM, "grains": 3}
    session_commit(db, SessionResult(
        session_id="s1", role="architect", wake_kind="tick:guess",
        wake_refs=(ITEM,),
        writes=[_as_write(w) for w in sb.ctx.writes]))
    rows = [tuple(r) for r in db.execute(
        "SELECT item_id, item_ver, ruling_id, grain, grain_kind, confidence "
        "FROM touch_guesses ORDER BY grain")]
    assert rows == [
        (ITEM, 3, "", "src/click/utils.py", "path", "expected"),
        (ITEM, 3, "", "src/click/utils.py::echo", "symbol", "possible"),
        (ITEM, 3, "", "tests/test_utils.py", "path", "expected"),
    ]
    assert _fires(db) == []


def test_the_op_refuses_an_item_that_is_no_request(db):
    seed_provenance(db, "items", ITEM, "observed")
    db.commit()
    with pytest.raises(ValueError, match="is not a request item"):
        _architect(db).call("batches.guess", item_id=ITEM,
                            paths=["src/click/utils.py"])


def test_the_op_refuses_an_empty_guess(db):
    with pytest.raises(ValueError, match="a guess names at least one path. "
                                         "A new file goes beside the files that exist"):
        _architect(db).call("batches.guess", item_id=ITEM, paths=[])


def test_the_op_refuses_a_path_under_a_directory_the_index_lacks(db):
    with pytest.raises(ValueError, match="src/json/echo.py is under a directory "
                                         "the tree does not have"):
        _architect(db).call("batches.guess", item_id=ITEM,
                            paths=["src/json/echo.py"])


def test_the_op_refuses_a_symbol_with_no_path(db):
    with pytest.raises(ValueError, match="echo_json names no path"):
        _architect(db).call("batches.guess", item_id=ITEM,
                            paths=["src/click/utils.py"], symbols=["echo_json"])


def test_the_op_refuses_a_second_guess_for_one_item_in_one_session(db):
    sb = _architect(db)
    sb.call("batches.guess", item_id=ITEM, paths=["src/click/utils.py"])
    with pytest.raises(ValueError, match="already guessed in this session"):
        sb.call("batches.guess", item_id=ITEM, paths=["tests/test_utils.py"])


def test_the_op_admits_a_guess_for_another_item_in_the_same_session(db):
    db.execute("INSERT INTO items (id, text, kind) VALUES "
               "('show_python', 'Add a show_python flag.', 'in_scope')")
    db.commit()
    sb = _architect(db)
    sb.call("batches.guess", item_id=ITEM, paths=["src/click/utils.py"])
    out = sb.call("batches.guess", item_id="show_python",
                  paths=["src/click/utils.py"])
    assert out == {"item_id": "show_python", "grains": 1}
