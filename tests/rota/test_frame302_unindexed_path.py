"""
Frame 302, pass 1: `batches.guess` and `batches.annotate` refuse a file the
index does not hold, unless the call names the file as new.

Night 157's s274 guessed `src/click/options.py` for `show_python`. The
directory `src/click` is indexed, so the 2026-09-12 door of 3c29d60b let the
path pass. The file is not in the index, and the seat had read index rows
that named `src/click/decorators.py::version_option` before the call
(plans/frame302-provenance.md, sections 2 and 6).

The scene is rebuilt inline from `.rota/clickI_night157.db`, read with
`mode=ro` on 2026-10-23: the 18 indexed paths under `src/click/`, the
top-level test files, and s274's call at turn 4.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import prompts
from rota.testkit.fixtures import seed_provenance

ITEM = "show_python"

# The night's `code_index` path grains under `src/click/` (night 157).
SRC = ["src/click/__init__.py", "src/click/_compat.py",
       "src/click/_termui_impl.py", "src/click/_textwrap.py",
       "src/click/_utils.py", "src/click/_winconsole.py", "src/click/core.py",
       "src/click/decorators.py", "src/click/exceptions.py",
       "src/click/formatting.py", "src/click/globals.py", "src/click/parser.py",
       "src/click/py.typed", "src/click/shell_completion.py",
       "src/click/termui.py", "src/click/testing.py", "src/click/types.py",
       "src/click/utils.py"]
# The night's top-level test files that s274's call names (night 157).
TESTS = ["tests/test_options.py", "tests/test_version_option.py"]
# s274, turn 4 (night 157, `turns`).
S274 = ["src/click/options.py", "tests/test_options.py",
        "tests/test_version_option.py"]


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version, priority) VALUES (?, ?, 'in_scope', 'approved', 1, 2, 1)",
                 (ITEM, "Give version_option a show_python flag that appends "
                        "the running Python version to the message."))
    seed_provenance(conn, "items", ITEM, "decided")
    for grain in SRC + TESTS:
        conn.execute("INSERT INTO code_index (grain, grain_kind) VALUES (?, 'path')",
                     (grain,))
    conn.commit()
    return conn


def _guess(db):
    return build("architect", db, mode="guess", session_id="s274",
                 allow=prompts.mode_tools("architect", "guess"))


def _annotate(db):
    return build("architect", db, mode="annotate", batch_id="bg_2",
                 allow=prompts.mode_tools("architect", "annotate"))


def _grains(sb, table: str) -> list[str]:
    return [w[2]["grain"] for w in sb.ctx.writes
            if w[0] == table and "grain" in w[2]]


def test_s274s_guess_is_refused_and_the_refusal_names_decorators(db):
    sb = _guess(db)
    with pytest.raises(ValueError) as err:
        sb.call("batches.guess", item_id=ITEM, paths=S274)
    words = str(err.value)
    assert words.startswith("src/click/options.py is not a file the index holds")
    assert "src/click/decorators.py" in words
    assert "new_files" in words
    assert not _grains(sb, "touch_guesses")


def test_s274s_guess_lands_when_the_file_is_named_as_new(db):
    sb = _guess(db)
    out = sb.call("batches.guess", item_id=ITEM, paths=S274,
                  new_files=["src/click/options.py"])
    assert out["grains"] == 3
    assert _grains(sb, "touch_guesses") == S274


def test_an_indexed_guess_lands_as_today(db):
    sb = _guess(db)
    out = sb.call("batches.guess", item_id=ITEM,
                  paths=["src/click/decorators.py", "tests/test_options.py"])
    assert out["grains"] == 2


def test_a_new_file_under_an_unindexed_directory_meets_the_directory_door(db):
    sb = _guess(db)
    with pytest.raises(ValueError, match="src/flags/options.py is under a "
                                         "directory the tree does not have"):
        sb.call("batches.guess", item_id=ITEM, paths=["src/flags/options.py"],
                new_files=["src/flags/options.py"])


def test_annotate_refuses_the_same_path_and_names_decorators(db):
    sb = _annotate(db)
    with pytest.raises(ValueError) as err:
        sb.call("batches.annotate", batch_id="bg_2", paths=S274)
    words = str(err.value)
    assert words.startswith("src/click/options.py is not a file the index holds")
    assert "src/click/decorators.py" in words
    assert not _grains(sb, "batch_touch")


def test_annotate_lands_when_the_file_is_named_as_new(db):
    sb = _annotate(db)
    out = sb.call("batches.annotate", batch_id="bg_2", paths=S274,
                  new_files=["src/click/options.py"])
    assert out["grains"] == 3
    assert _grains(sb, "batch_touch") == S274


def test_annotate_lands_an_indexed_path_as_today(db):
    sb = _annotate(db)
    out = sb.call("batches.annotate", batch_id="bg_2",
                  paths=["src/click/decorators.py"])
    assert out["grains"] == 1


def test_annotate_keeps_the_directory_door_for_a_new_file(db):
    sb = _annotate(db)
    with pytest.raises(ValueError, match="src/flags/options.py is under a "
                                         "directory the tree does not have"):
        sb.call("batches.annotate", batch_id="bg_2",
                paths=["src/flags/options.py"],
                new_files=["src/flags/options.py"])
