"""
Frame 362, shape layer pass S1: `code_calls`, the copies query and the guess
mark.

Steps 3 and 4 of `plans/design-onboarding-shape-2026-11-04.md`, section 6.2.
Dry run 4 matched the request's words to symbol names once, and the match
picked `q_split` while the fold code was `_foldline`
(`plans/dry4-read-2026-11-03.md`, section 8). The guess's rows now carry the
copies of a name and the entry point of a file, so the Architect sees the
shape before it binds the request.
"""
from __future__ import annotations

import io
import subprocess
import tarfile
from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.onboarding import harvest, indexer, shape
from rota.onboarding.areas import is_attached


def _tree(root: Path, files: dict[str, str]) -> Path:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    return root


def _calls(db) -> set[tuple[str, str]]:
    return {(r[0], r[1]) for r in db.execute("SELECT src, dst_grain FROM code_calls")}


# --- code_calls ----------------------------------------------------------------

CALLS = {
    "pkg/__init__.py": "from .core import helper\n",
    "pkg/core.py": ("def helper():\n    return inner()\n\n\n"
                    "def inner():\n    return 1\n"),
    "pkg/cli.py": ("from pkg import helper\n\n\n"
                   "def run():\n    return helper()\n"),
    "pkg/other.py": ("from . import core\n\n\n"
                     "def go():\n    return core.helper()\n"),
    "tests/test_core.py": ("from pkg.core import helper\n\n\n"
                           "def test_helper():\n    assert helper() == 1\n"),
}


def test_a_call_through_a_reexport_ends_at_the_defining_file(tmp_path):
    db = init_db(tmp_path / "run.db")
    report = indexer.build(db, _tree(tmp_path / "t", CALLS))
    rows = _calls(db)
    assert ("pkg/cli.py", "pkg/core.py::helper") in rows
    assert not any(dst.startswith("pkg/__init__.py") for _, dst in rows)
    assert report.calls == len(rows)


def test_a_call_through_a_module_alias_is_a_cross_file_row(tmp_path):
    db = init_db(tmp_path / "run.db")
    indexer.build(db, _tree(tmp_path / "t", CALLS))
    assert ("pkg/other.py", "pkg/core.py::helper") in _calls(db)


def test_a_same_file_call_writes_no_row(tmp_path):
    db = init_db(tmp_path / "run.db")
    indexer.build(db, _tree(tmp_path / "t", CALLS))
    assert not any(src == "pkg/core.py" for src, _ in _calls(db))


def test_a_test_file_call_stays_for_the_tester(tmp_path):
    """The Tester's witnesses of section 3.2 come from the same table, so a
    reader leaves the attached files out, not the indexer."""
    db = init_db(tmp_path / "run.db")
    indexer.build(db, _tree(tmp_path / "t", CALLS))
    assert _calls(db) == {("pkg/cli.py", "pkg/core.py::helper"),
                          ("pkg/other.py", "pkg/core.py::helper"),
                          ("tests/test_core.py", "pkg/core.py::helper")}


def test_a_new_build_replaces_the_calls(tmp_path):
    db = init_db(tmp_path / "run.db")
    root = _tree(tmp_path / "t", CALLS)
    indexer.build(db, root)
    (root / "pkg" / "cli.py").write_bytes(b"def run():\n    return 2\n")
    indexer.build(db, root)
    assert ("pkg/cli.py", "pkg/core.py::helper") not in _calls(db)


def test_the_calls_stay_out_of_the_edges(tmp_path):
    """`areas.propose` reads each edge as coupling, so a call row must not
    move the partition."""
    db = init_db(tmp_path / "run.db")
    indexer.build(db, _tree(tmp_path / "t", CALLS))
    edges = {(r[0], r[1]) for r in db.execute("SELECT src, dst FROM code_edges")}
    assert ("pkg/cli.py", "pkg/core.py") not in edges


# --- the copies query ------------------------------------------------------------

COPIES = {
    "a.py": "def parse():\n    return 1\n\n\ndef __getattr__(name):\n    return name\n",
    "b.py": "def parse():\n    return 2\n\n\ndef __getattr__(name):\n    return name\n",
    "c.py": "class Reader:\n    def parse(self):\n        return 3\n",
    "tests/test_a.py": "def parse():\n    return 4\n",
}


def test_two_definitions_of_one_name_are_copies(tmp_path):
    db = init_db(tmp_path / "run.db")
    indexer.build(db, _tree(tmp_path / "t", COPIES))
    assert shape.copies(db) == {"parse": ["a.py", "b.py"]}


def test_a_method_a_test_file_and_a_dunder_stay_out(tmp_path):
    db = init_db(tmp_path / "run.db")
    indexer.build(db, _tree(tmp_path / "t", COPIES))
    got = shape.copies(db)
    assert "c.py" not in got.get("parse", [])
    assert "tests/test_a.py" not in got.get("parse", [])
    assert "__getattr__" not in got


# --- the guess mark -------------------------------------------------------------

GUESS = {
    "pyproject.toml": ('[project]\nname = "demo"\n\n'
                       '[project.scripts]\ndemo = "tipcalc.cli:main"\n'),
    "tipcalc/__init__.py": "",
    "tipcalc/cli.py": ("def main():\n    return split_line('a')\n\n\n"
                    "def split_line(text):\n    return text.split()\n"),
    "tipcalc/tool.py": ("def split_line(text):\n    return text.split(',')\n\n\n"
                     "if __name__ == \"__main__\":\n    split_line('a')\n"),
    "tipcalc/fold.py": "def fold_line(text):\n    return text\n",
}


@pytest.fixture
def guess_rows(tmp_path):
    root = _tree(tmp_path / "t", GUESS)
    db = init_db(tmp_path / "run.db")
    indexer.build(db, root)
    harvest.record(db, root, "c1")
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
               "('project_root', ?)", (str(root),))
    db.commit()
    sb = build("architect", db, mode="guess")
    rows = sb.call("code.callables", hint="split and fold the line")
    yield {r["grain"]: r for r in rows}
    db.close()


def test_a_copy_row_names_the_other_file(guess_rows):
    assert guess_rows["tipcalc/cli.py::split_line"]["copies"] == ["tipcalc/tool.py"]
    assert guess_rows["tipcalc/tool.py::split_line"]["copies"] == ["tipcalc/cli.py"]


def test_a_script_target_and_a_main_guard_are_entry_points(guess_rows):
    script = guess_rows["tipcalc/cli.py::split_line"]["entry_point"]
    assert script.startswith("script: ") and "tipcalc.cli:main" in script
    assert guess_rows["tipcalc/tool.py::split_line"]["entry_point"] == "__main__ guard"


def test_an_empty_field_stays_out_of_the_row(guess_rows):
    row = guess_rows["tipcalc/fold.py::fold_line"]
    assert "copies" not in row and "entry_point" not in row


def test_the_guess_prompt_says_what_the_fields_mean():
    text = (Path(__file__).resolve().parents[2] / "rota" / "roles" / "prompts"
            / "architect" / "guess.md").read_text(encoding="utf-8")
    assert "`copies`" in text and "`entry_point`" in text


def test_the_guess_prompt_says_which_copy_to_name():
    """Review of S1, medium 1: the sentence gives a step, not only a meaning."""
    text = (Path(__file__).resolve().parents[2] / "rota" / "roles" / "prompts"
            / "architect" / "guess.md").read_text(encoding="utf-8")
    assert ("When a row has `copies`, name the copy whose file has an "
            "`entry_point`,\nor name both copies.") in text


GUARDED = {
    "pkg/__init__.py": "",
    "pkg/impl.py": ("import sys\n\nif sys.platform == 'win32':\n"
                    "    def raw():\n        return 1\nelse:\n"
                    "    def raw():\n        return 2\n\n"
                    "try:\n    def fast():\n        return 3\n"
                    "except ImportError:\n    pass\n"),
    "pkg/ui.py": ("from .impl import fast\n\n\ndef raw():\n"
                  "    from .impl import raw as f\n    return f()\n\n\n"
                  "def go():\n    return fast()\n"),
    "pkg/sub/__init__.py": "from ..core import helper\n",
    "pkg/core.py": "def helper():\n    return 0\n",
}


def test_a_call_reaches_a_definition_under_a_module_if_or_try(tmp_path):
    """Review of S1, medium 2: the resolver reads the definitions that the
    index holds, and a function-local import binds its own function."""
    root = _tree(tmp_path / "t", GUARDED)
    db = init_db(tmp_path / "run.db")
    indexer.build(db, root)
    assert {("pkg/ui.py", "pkg/impl.py::raw"),
            ("pkg/ui.py", "pkg/impl.py::fast")} <= _calls(db)
    # Review of S1, low 7: a two-dot relative re-export binds its target.
    assert harvest._reexported(harvest.Tree(root), "pkg/sub/__init__.py") == {
        "pkg/core.py"}


# --- the pinned counts ------------------------------------------------------------

SAMPLES = Path("D:/repos/_AI/sample_repos")

# The design's numbers, sections 3.1 and 3.2, on the blind test's pins. The
# helper columns are the resolved cross-file targets and those that two or
# more files call, program files only. The click copies are 4, not the
# design's 1: the index holds the defs under a module `if WIN:` block, and the
# probe read the module body only. Pass S3 resolves the definitions under
# that block and the function-local imports, so click has 56 targets, not
# the design's 54: `raw_terminal` and `get_pager_file` of `_termui_impl.py`.
PINS = {
    "tipsI": ("ff1f65f", 0, 0, {"calculate_tip": ["main.py", "tip_calculator.py"],
                                "display_results": ["main.py", "tip_calculator.py"]}),
    "clickI": ("09c82f3", 56, 13, {
        "_get_windows_console_stream": ["src/click/_compat.py",
                                        "src/click/_winconsole.py"],
        "get_pager_file": ["src/click/_termui_impl.py", "src/click/termui.py"],
        "getchar": ["src/click/_termui_impl.py", "src/click/termui.py"],
        "raw_terminal": ["src/click/_termui_impl.py", "src/click/termui.py"]}),
    "icalendarI": ("4f12af1e", 65, 34, {"main": [
        "src/icalendar/cli.py", "src/icalendar/fuzzing/ical_fuzzer.py",
        "src/icalendar/timezone/equivalent_timezone_ids.py"]}),
}


def _pinned(repo: str, commit: str, into: Path) -> Path:
    """The pinned commit, read out with `git archive`, so the sample tree and
    its checkout stay as they are."""
    src = SAMPLES / repo
    if not (src / ".git").exists():
        pytest.skip(f"{repo} is not on this machine under {SAMPLES}")
    got = subprocess.run(["git", "-C", str(src), "archive", commit],
                         capture_output=True)
    if got.returncode != 0:
        pytest.skip(f"{repo} holds no commit {commit}")
    with tarfile.open(fileobj=io.BytesIO(got.stdout)) as tar:
        tar.extractall(into, filter="data")
    return into


@pytest.mark.parametrize("repo", sorted(PINS))
def test_the_counts_on_the_pinned_trees(repo, tmp_path):
    commit, targets, shared, copies = PINS[repo]
    root = _pinned(repo, commit, tmp_path / repo)
    db = init_db(tmp_path / "run.db")
    indexer.build(db, root)
    callers: dict[str, set[str]] = {}
    for src, grain in _calls(db):
        if not is_attached(src) and not is_attached(grain.split("::")[0]):
            callers.setdefault(grain, set()).add(src)
    assert len(callers) == targets
    assert sum(len(v) >= 2 for v in callers.values()) == shared
    assert shape.copies(db) == copies
    # The resolver sees each copy that the index holds (review of S1, medium 2).
    tree = harvest.Tree(root)
    assert all(tree.definer(p, name) == p for name, ps in copies.items() for p in ps)
    if repo == "clickI":
        assert {("src/click/termui.py", "src/click/_termui_impl.py::raw_terminal"),
                ("src/click/termui.py", "src/click/_termui_impl.py::get_pager_file")
                } <= _calls(db)
