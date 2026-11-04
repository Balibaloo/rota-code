"""
Frame 362, shape layer pass S5: `model.shape` for the Architect's ask.

Step 6 of `plans/design-onboarding-shape-2026-11-04.md`, section 6.2. The
`ask` has no code read, and Q5 of the icalendar set names `from_ical`, a name
the Architect could not look up (section 3.5, item 2). The op answers where a
name lives, every copy, who calls it and whether it is public.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.onboarding import harvest, indexer

SHAPE = {
    "pyproject.toml": ('[project]\nname = "demo"\n\n'
                       '[project.scripts]\ndemo = "pkg.cli:main"\n'),
    "pkg/__init__.py": ('from .cal import Calendar\nfrom .fold import fold_line\n\n'
                        '__all__ = ["Calendar", "fold_line"]\n'),
    "pkg/cal.py": ("class Calendar:\n    @classmethod\n"
                   "    def from_ical(cls, text):\n        return cls()\n"),
    "pkg/fold.py": "def fold_line(text):\n    return text\n",
    "pkg/legacy.py": "def fold_line(text):\n    return text[:75]\n",
    "pkg/attr.py": "def _get_links():\n    return []\n",
    "pkg/cli.py": ("from pkg.cal import Calendar\nfrom pkg.fold import fold_line\n\n\n"
                   "def main():\n    fold_line('a')\n    return Calendar.from_ical('x')\n"),
    "tests/test_fold.py": ("from pkg.fold import fold_line\n\n\n"
                           "def test_fold():\n    assert fold_line('a') == 'a'\n"),
}


@pytest.fixture
def index(tmp_path):
    root = tmp_path / "t"
    for rel, text in SHAPE.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    db = init_db(tmp_path / "run.db")
    indexer.build(db, root)
    harvest.record(db, root, "c1")
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
               "('project_root', ?)", (str(root),))
    db.commit()
    yield db
    db.close()


@pytest.fixture
def ask(index):
    return build("architect", index, mode="ask")


def test_a_hit_carries_its_file_copies_callers_and_export(ask):
    rows = {r["grain"]: r for r in ask.call("model.shape", name="fold_line")}
    live = rows["pkg/fold.py::fold_line"]
    assert live["path"] == "pkg/fold.py"
    assert (live["start"], live["end"]) == (0, 2)
    assert live["copies"] == ["pkg/legacy.py"]
    assert live["callers"] == ["pkg/cli.py"]
    assert live["test_callers"] == ["tests/test_fold.py"]
    assert live["exported"] == ["pkg/__init__.py"]
    # The bound export candidate picks the copy that `__all__` re-exports.
    dead = rows["pkg/legacy.py::fold_line"]
    assert dead["copies"] == ["pkg/fold.py"]
    assert "exported" not in dead and "callers" not in dead


def test_a_hit_in_a_script_file_carries_the_entry_point(ask):
    rows = {r["grain"]: r for r in ask.call("model.shape", name="main")}
    assert rows["pkg/cli.py::main"]["entry_point"].startswith("script: ")


def test_a_command_name_leads_with_the_function_it_runs(ask):
    """Section 4.1, Q8: a person names the command, not the function."""
    rows = ask.call("model.shape", name="demo")
    assert rows[0]["grain"] == "pkg/cli.py::main"
    assert rows[0]["command"] == "demo"


def test_a_name_with_no_hit_returns_the_note(ask):
    rows = ask.call("model.shape", name="zebra_crossing")
    assert len(rows) == 1 and set(rows[0]) == {"note"}
    assert "zebra_crossing" in rows[0]["note"]


def test_a_class_method_name_matches_the_class_row(ask):
    """The index holds no method, so the class that holds it stands in."""
    rows = ask.call("model.shape", name="Calendar.from_ical")
    assert rows[0]["grain"] == "pkg/cal.py::Calendar"
    assert rows[0]["exported"] == ["pkg/__init__.py"]


def test_an_export_grain_alone_is_its_own_row(tmp_path):
    root = tmp_path / "t"
    for rel, text in {"pkg/__init__.py": ('VERSION_TAG = "1"\n'
                                          '__all__ = ["VERSION_TAG"]\n')}.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    db = init_db(tmp_path / "run.db")
    indexer.build(db, root)
    sb = build("architect", db, mode="ask")
    rows = sb.call("model.shape", name="version_tag")
    db.close()
    assert [r["grain"] for r in rows] == ["pkg/__init__.py::VERSION_TAG"]
    assert rows[0]["exported"] == ["pkg/__init__.py"]


def test_the_ask_mode_offers_the_op():
    tools = (Path(__file__).resolve().parents[2] / "rota" / "roles" / "prompts"
             / "architect" / "ask.tools").read_text(encoding="utf-8")
    assert "model.shape" in tools.split()


# --- the consult probe -----------------------------------------------------------

def test_the_probe_block_names_the_command_and_its_function(index):
    """Section 4.1 and step 7: the consult probe's Architect sees the shape."""
    from probes.consult import SHAPE_HEAD, shape_for

    block = shape_for(index, "What does the `demo` command do?")
    lines = block.splitlines()
    assert lines[0] == SHAPE_HEAD
    assert lines[1].startswith("- pkg/cli.py::main (function, lines 5-7)")
    assert "the command `demo` runs it" in lines[1]


def test_a_question_with_no_hit_adds_no_block(index):
    from probes.consult import shape_for

    assert shape_for(index, "Why zebra crossings?") == ""


# --- S5b: the probe block keeps the names the question names whole ------------

def _grains(block: str) -> list[str]:
    return [line[2:].split(" ", 1)[0] for line in block.splitlines()
            if line.startswith("- ")]


def test_the_block_keeps_a_whole_name_and_drops_a_word_hit(index):
    """Q1 on dry run 5: `get` matched the `_get_*` helpers of `attr.py`."""
    from probes.consult import shape_for

    block = shape_for(index, "How do they get a Calendar object back?")
    assert _grains(block) == ["pkg/cal.py::Calendar"]
    assert "pkg/attr.py::_get_links" not in block
    assert block.splitlines()[-1].startswith("and ")
    assert block.splitlines()[-1].endswith(" more rows match a word of the question")


def test_the_block_keeps_a_class_method_and_its_class(index):
    """Q5: the dotted name gives the class and the method name whole."""
    from probes.consult import shape_for

    block = shape_for(index, "A maintainer renames Calendar.from_ical. Who notices?")
    assert "pkg/cal.py::Calendar" in _grains(block)


def test_the_block_keeps_the_command_row(index):
    """Q8: the command row stays, with the function it runs."""
    from probes.consult import shape_for

    block = shape_for(index, "What does the `demo` command a user gets do?")
    assert _grains(block)[0] == "pkg/cli.py::main"
    assert "the command `demo` runs it" in block


def test_everyday_words_with_no_whole_name_get_no_block(index):
    from probes.consult import shape_for

    assert shape_for(index, "How do the links get their line?") == ""
