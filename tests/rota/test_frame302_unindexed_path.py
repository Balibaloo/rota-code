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
# Two of the night's symbol grains: the one the item names, and one that
# sorts after the cap of eight (night 157, `code_index`).
SYMBOLS = ["src/click/decorators.py::version_option",
           "src/click/termui.py::confirm"]
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
    for grain in SYMBOLS:
        conn.execute("INSERT INTO code_index (grain, grain_kind) VALUES (?, 'symbol')",
                     (grain,))
    conn.execute("INSERT INTO batches (id, item_id, status) "
                 "VALUES ('bg_2', ?, 'pending')", (ITEM,))
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


# ---------------------------------------------------------------------------
# Pass 1b: review 1 of frame 302
# ---------------------------------------------------------------------------

def test_a_path_symbol_entry_is_checked_by_its_file_half(db):
    """Review 1, finding 1: 58 annotate calls of nights 150 to 157 wrote
    path::symbol in `paths`, and each landed on its night."""
    sb = _annotate(db)
    out = sb.call("batches.annotate", batch_id="bg_2",
                  paths=["src/click/decorators.py::version_option"])
    assert out["grains"] == 1
    sb = _guess(db)
    out = sb.call("batches.guess", item_id=ITEM,
                  paths=["src/click/decorators.py::version_option"])
    assert out["grains"] == 1


def test_a_symbol_never_passes_as_a_new_file(db):
    """Review 1, finding 1: a symbol named in `new_files` is no new file."""
    sb = _annotate(db)
    with pytest.raises(ValueError, match="src/click/options.py is not a file "
                                         "the index holds"):
        sb.call("batches.annotate", batch_id="bg_2",
                paths=["src/click/options.py::show_python"],
                new_files=["src/click/options.py::show_python"])


def _listed(words: str) -> list[str]:
    return words.split(": ", 1)[1].split(". Write", 1)[0].split(", ")


def test_the_file_the_item_names_a_symbol_of_comes_first(db):
    """Review 1, finding 2: decorators.py was in the list by its sort order
    alone. The item names version_option, and the index holds it there."""
    sb = _guess(db)
    with pytest.raises(ValueError) as err:
        sb.call("batches.guess", item_id=ITEM, paths=S274)
    assert _listed(str(err.value))[0] == "src/click/decorators.py"
    sb = _annotate(db)
    with pytest.raises(ValueError) as err:
        sb.call("batches.annotate", batch_id="bg_2", paths=S274)
    assert _listed(str(err.value))[0] == "src/click/decorators.py"


def test_the_file_the_call_names_a_symbol_of_comes_first(db):
    """termui.py sorts past the cap of eight. The call's symbol names
    confirm, and the index holds it in termui.py."""
    sb = _annotate(db)
    with pytest.raises(ValueError) as err:
        sb.call("batches.annotate", batch_id="bg_2", paths=S274,
                symbols=["confirm"])
    listed = _listed(str(err.value))
    assert listed[:2] == ["src/click/decorators.py", "src/click/termui.py"]
    assert len(listed) == 8


def test_a_guess_symbol_on_an_unindexed_file_meets_the_door(db):
    """Review 1, finding 4: a symbol's file half meets the door as a path."""
    sb = _guess(db)
    with pytest.raises(ValueError, match="src/click/options.py is not a file "
                                         "the index holds"):
        sb.call("batches.guess", item_id=ITEM, paths=["src/click/decorators.py"],
                symbols=["src/click/options.py::show_python"])
    sb = _guess(db)
    out = sb.call("batches.guess", item_id=ITEM, paths=["src/click/decorators.py"],
                  symbols=["src/click/options.py::show_python"],
                  new_files=["src/click/options.py"])
    assert out["grains"] == 2


@pytest.mark.parametrize("mode", ["guess", "annotate"])
def test_the_brief_names_the_new_files_argument(mode):
    """Review 1, finding 3: the seat read new_files only in the signature
    and in the refusal."""
    from pathlib import Path

    brief = (Path(prompts.__file__).parent / "prompts" / "architect" / f"{mode}.md"
             ).read_text(encoding="utf-8")
    assert "new_files=[...]" in brief


# s169, turn 14 (night 154, `turns`): one entry holds a single colon.
S169 = ["src/click/termui.py::confirm", "src/click/termui.py::_format_default",
        "src/click/termui.py::_readline_prompt", "src/click/termui.py::_build_prompt",
        "src/click/termui.py::_mask_hidden_input",
        "src/click/termui.py:hidden_prompt_func"]


def test_a_single_colon_path_symbol_is_read_by_its_path_half(db):
    """Frame 302, pass 1c: night 154's s169 typed path:symbol with one
    colon, and the call landed on its night."""
    sb = _annotate(db)
    out = sb.call("batches.annotate", batch_id="bg_2", paths=S169)
    assert out["grains"] == 6
    sb = _annotate(db)
    with pytest.raises(ValueError, match="src/click/options.py is not a file "
                                         "the index holds"):
        sb.call("batches.annotate", batch_id="bg_2",
                paths=["src/click/options.py:show_python"])
