"""
Frame 362, shape layer pass S2: the `entry_point` and `contribution` kinds,
and the harvest again after a merge.

Section 3.4 of `plans/design-onboarding-shape-2026-11-04.md` defines the two
kinds. The design names the second one `intake`, and that word is a mode of
the brief role, so the kind is `contribution`. Section 6.1 sets the guard
filter: a fuzz harness or a module demo under `__main__` is not an entry
point. Section 6.2, step 2, runs `harvest.record` in the refresh of main.
"""
from __future__ import annotations

import io
import json
import sqlite3
import subprocess
import tarfile
from pathlib import Path

import pytest

from rota.core import lifecycle
from rota.core.db import init_db
from rota.onboarding import boot, harvest, indexer, shape
from rota.testkit import gitfixture


def _tree(root: Path, files: dict[str, str]) -> Path:
    for rel, body in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body.encode("utf-8"))
    return root


def _rows(db, kind):
    return [dict(r) for r in db.execute(
        "SELECT * FROM commitment_candidates WHERE kind = ? ORDER BY path, line",
        (kind,))]


def _bound(db, cid):
    return {r[0]: r[1] for r in db.execute(
        "SELECT path, rule FROM candidate_bindings WHERE witness_id = ?", (cid,))}


def _form(row) -> str:
    return json.loads(row["detail"])["form"]


# --- the entry_point kind ---------------------------------------------------------

ENTRY = {
    "pyproject.toml": ('[project]\nname = "demo"\n\n[project.scripts]\n'
                       'demo = "demo.cli:main"\n\n'
                       '[project.entry-points."demo.plugins"]\n'
                       'extra = "demo.cli:main"\n'),
    "README.md": ("# demo\n\nRun it: `python run.py`\n\n"
                  "Or try `python missing.py` from the docs.\n"),
    "run.py": ("def main():\n    return 1\n\n\n"
               "if __name__ == \"__main__\":\n    main()\n"),
    "demo/__init__.py": "",
    "demo/__main__.py": "\nfrom demo.cli import main\n\nmain()\n",
    "demo/cli.py": ('def main():\n    """Print the demo report."""\n    return 0\n\n\n'
                    "if __name__ == '__main__':\n    raise SystemExit(main())\n"),
    # A module demo: the guard calls an imported name and a name it defines
    # in the guard, as `cal/lazy.py` of icalendar does.
    "demo/lazy.py": ("import timeit\n\n\nclass Lazy:\n    pass\n\n\n"
                     "if __name__ == \"__main__\":\n    def bench():\n"
                     "        return Lazy.__name__\n    print(timeit.timeit(bench))\n"),
    # A fuzz harness by its import, and one by its directory.
    "demo/fuzz_one.py": ("import atheris\n\n\ndef main():\n    atheris.Fuzz()\n\n\n"
                         "if __name__ == \"__main__\":\n    main()\n"),
    "demo/fuzzing/two.py": ("def main():\n    pass\n\n\n"
                            "if __name__ == \"__main__\":\n    main()\n"),
    "tests/test_cli.py": ("def test_main():\n    pass\n\n\n"
                          "if __name__ == \"__main__\":\n    test_main()\n"),
}


@pytest.fixture
def entry_db(tmp_path):
    root = _tree(tmp_path / "t", ENTRY)
    db = init_db(tmp_path / "run.db")
    indexer.build(db, root)
    harvest.record(db, root, "c1")
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
               "('project_root', ?)", (str(root),))
    db.commit()
    yield db, root
    db.close()


def test_a_script_row_is_an_entry_point_with_its_new_id(entry_db):
    db, _ = entry_db
    scripts = [r for r in _rows(db, "entry_point") if _form(r) == "script"]
    assert [(r["line"], json.loads(r["detail"])["group"]) for r in scripts] == [
        (5, "scripts"), (8, "entry-points.demo.plugins")]
    first = scripts[0]
    assert first["id"] == harvest.candidate_id("entry_point", "pyproject.toml", 5,
                                               'demo = "demo.cli:main"')
    assert json.loads(first["detail"])["doc"] == "Print the demo report."
    assert _bound(db, first["id"]) == {"demo/cli.py": "entry_point",
                                       "pyproject.toml": "entry_point"}
    assert not [r for r in _rows(db, "metadata")
                if json.loads(r["detail"]).get("field") == "script"]


def test_the_guard_filter_keeps_a_program_and_drops_a_demo_and_a_fuzzer(entry_db):
    db, _ = entry_db
    guards = {r["path"] for r in _rows(db, "entry_point") if _form(r) == "guard"}
    assert guards == {"run.py", "demo/cli.py"}


def test_a_main_module_and_a_readme_run_line_are_entry_points(entry_db):
    db, _ = entry_db
    rows = {(_form(r), r["path"]): r for r in _rows(db, "entry_point")}
    main = rows[("main_module", "demo/__main__.py")]
    assert main["line"] == 2 and _bound(db, main["id"]) == {
        "demo/__main__.py": "entry_point"}
    readme = rows[("readme", "README.md")]
    assert readme["line"] == 3 and _bound(db, readme["id"]) == {"run.py": "entry_point"}
    # A run line of a file the tree does not hold is an example.
    assert len([k for k in rows if k[0] == "readme"]) == 1


def test_the_guess_mark_follows_the_guard_filter(entry_db):
    db, root = entry_db
    got = shape.entry_points(db, root, {"demo/lazy.py", "demo/fuzz_one.py",
                                        "run.py", "demo/cli.py"})
    assert got["demo/cli.py"].startswith("script: ")
    assert got["run.py"] == "__main__ guard"
    assert "demo/lazy.py" not in got and "demo/fuzz_one.py" not in got
    # With no harvest, the file read applies the same rule.
    db.execute("DELETE FROM candidate_bindings")
    got = shape.entry_points(db, root, {"demo/lazy.py", "run.py"})
    assert got == {"run.py": "__main__ guard"}


# --- the contribution kind --------------------------------------------------------

def test_testpaths_binds_the_test_files_it_collects(tmp_path):
    root = _tree(tmp_path / "t", {
        "pyproject.toml": ('[tool.pytest.ini_options]\ntestpaths = [\n'
                           '    "src/pkg/tests",\n]\n'),
        "src/pkg/__init__.py": "",
        "src/pkg/tests/test_a.py": "def test_a():\n    pass\n",
        "tests/test_other.py": "def test_b():\n    pass\n",
    })
    db = init_db(tmp_path / "run.db")
    harvest.record(db, root, "c1")
    [row] = _rows(db, "contribution")
    assert row["line"] == 2 and row["text"] == 'testpaths = [\n    "src/pkg/tests",\n]'
    assert json.loads(row["detail"]) == {"form": "testpaths", "paths": ["src/pkg/tests"]}
    assert _bound(db, row["id"]) == {"src/pkg/tests/test_a.py": "contribution"}


def test_a_towncrier_rule_binds_its_fragments_and_hides_the_change_log(tmp_path):
    root = _tree(tmp_path / "t", {
        "pyproject.toml": ('[tool.towncrier]\ndirectory = "news/"\n'
                           'filename = "CHANGES.rst"\n'),
        "news/123.bugfix": "Fixed it.\n",
        "CHANGES.rst": "Change log\n==========\n\n1.0 (unreleased)\n----------------\n",
        "tox.ini": "[pytest]\ntestpaths = tests\n",
        "tests/test_a.py": "def test_a():\n    pass\n",
    })
    db = init_db(tmp_path / "run.db")
    harvest.record(db, root, "c1")
    rows = {_form(r): r for r in _rows(db, "contribution")}
    assert set(rows) == {"news_fragment", "testpaths"}
    news = rows["news_fragment"]
    assert news["text"] == 'directory = "news/"'
    # The old fragments are files no change touches (review of S2, low 3).
    assert _bound(db, news["id"]) == {"CHANGES.rst": "contribution"}
    assert rows["testpaths"]["path"] == "tox.ini"


def test_a_change_log_with_an_unreleased_heading_is_the_rule(tmp_path):
    root = _tree(tmp_path / "t", {
        "CHANGES.md": "## Version 2.0\n\nUnreleased\n\n- A change.\n",
        "HISTORY.rst": "Old\n===\n\n1.0\n---\n",
    })
    db = init_db(tmp_path / "run.db")
    harvest.record(db, root, "c1")
    [row] = _rows(db, "contribution")
    assert (row["path"], row["line"], row["text"]) == ("CHANGES.md", 1, "## Version 2.0")
    assert _bound(db, row["id"]) == {"CHANGES.md": "contribution"}


def test_an_older_database_takes_the_new_kinds(tmp_path):
    """The CHECK of a database from before pass S2 refuses the new kinds, so
    `init_db` builds both tables again and keeps their rows."""
    path = tmp_path / "run.db"
    db = init_db(path)
    old_kinds = ("'metadata','doc_claim','preservation','numeric_default',"
                 "'issue_comment','export','test_witness'")
    db.executescript(f"""
        PRAGMA foreign_keys = OFF;
        DROP TABLE candidate_bindings;
        DROP TABLE commitment_candidates;
        CREATE TABLE commitment_candidates (id TEXT PRIMARY KEY, kind TEXT NOT NULL
            CHECK (kind IN ({old_kinds})), path TEXT NOT NULL, line INTEGER NOT NULL,
            text TEXT NOT NULL, symbol TEXT NOT NULL DEFAULT '',
            detail TEXT NOT NULL DEFAULT '{{}}', contradicts TEXT NOT NULL DEFAULT '[]',
            commit_sha TEXT NOT NULL DEFAULT '');
        CREATE TABLE candidate_bindings (witness_id TEXT NOT NULL
            REFERENCES commitment_candidates(id), path TEXT NOT NULL,
            rule TEXT NOT NULL CHECK (rule IN ('entry_point','project_wide')),
            PRIMARY KEY (witness_id, path));
        INSERT INTO commitment_candidates (id, kind, path, line, text)
            VALUES ('cc_old', 'metadata', 'pyproject.toml', 1, 'name = "x"');
        INSERT INTO candidate_bindings VALUES ('cc_old', 'a.py', 'project_wide');
    """)
    db.commit()
    db.close()
    db = init_db(path)
    db.execute("INSERT INTO commitment_candidates (id, kind, path, line, text) "
               "VALUES ('cc_new', 'contribution', 'tox.ini', 2, 'testpaths = t')")
    db.execute("INSERT INTO candidate_bindings VALUES ('cc_new', 't/a.py', "
               "'contribution')")
    assert db.execute("SELECT kind FROM commitment_candidates WHERE id = 'cc_old'"
                      ).fetchone()[0] == "metadata"
    assert db.execute("SELECT COUNT(*) FROM candidate_bindings").fetchone()[0] == 2
    db.close()


# --- the harvest again after a merge -----------------------------------------------

def _candidates(db) -> dict[tuple, str]:
    return {(r["kind"], r["path"], r["text"]): r["commit_sha"] for r in db.execute(
        "SELECT kind, path, text, commit_sha FROM commitment_candidates")}


def test_a_merge_moves_the_rows_to_the_new_commit(tmp_path):
    db = init_db(tmp_path / "rota.db")
    repo = gitfixture.make(tmp_path, name="shape_s2")
    repo.edit(repo.root, "tool.py", "def main():\n    pass\n\n\n"
              "if __name__ == \"__main__\":\n    main()\n")
    repo.edit(repo.root, "old.py", "def main():\n    pass\n\n\n"
              "if __name__ == \"__main__\":\n    main()\n")
    first = repo.commit_in(repo.root, "add two tools")
    boot.onboard(db, repo.root)
    db.commit()
    guards = {k[1]: v for k, v in _candidates(db).items() if k[0] == "entry_point"}
    assert guards == {"tool.py": first, "old.py": first}

    (repo.root / "old.py").unlink()
    repo.edit(repo.root, "new.py", "def run():\n    pass\n\n\n"
              "if __name__ == \"__main__\":\n    run()\n")
    second = repo.commit_in(repo.root, "replace a tool")
    done = indexer.refresh(db, repo.root, main=True)
    db.commit()
    assert done.warnings == []
    rows = _candidates(db)
    guards = {k[1]: v for k, v in rows.items() if k[0] == "entry_point"}
    # The row found again takes the new commit. The row of the gone file
    # keeps its old commit and loses its binding.
    assert guards == {"tool.py": second, "old.py": first, "new.py": second}
    bound = {r[0] for r in db.execute(
        "SELECT c.path FROM candidate_bindings b JOIN commitment_candidates c "
        "ON c.id = b.witness_id WHERE c.kind = 'entry_point'")}
    assert bound == {"tool.py", "new.py"}
    assert harvest.latest_commit(db) == second
    # A refresh at the same commit writes nothing.
    assert harvest.record(db, repo.root, second) == 0


def test_a_harvest_fault_is_a_warning_and_the_refresh_goes_on(tmp_path, monkeypatch):
    db = init_db(tmp_path / "rota.db")
    repo = gitfixture.make(tmp_path, name="shape_s2_fault")
    boot.onboard(db, repo.root)
    db.commit()

    def broken(*args, **kwargs):
        raise sqlite3.OperationalError("disk I/O error")

    monkeypatch.setattr(harvest, "record", broken)
    done = indexer.refresh(db, repo.root, main=True)
    assert done.commit and done.index.files
    [line] = done.warnings
    assert "OperationalError: disk I/O error" in line

    # After a merge the warning is a record that outlives the index note
    # (review of S2, medium 1), and a harvest that works clears it.
    def note(key):
        row = db.execute("SELECT value FROM config WHERE key = ?", (key,)).fetchone()
        return row[0] if row else None

    lifecycle._reindex_main(db, "b1")
    assert note("index:b1") is None
    assert "OperationalError: disk I/O error" in note("harvest:b1")
    monkeypatch.undo()
    lifecycle._reindex_main(db, "b2")
    assert note("harvest:b1") is None


def test_the_guard_reads_a_class_a_relative_import_and_the_reversed_test(tmp_path):
    """Review of S2, low 2."""
    root = _tree(tmp_path / "t", {
        "pkg/__init__.py": "", "pkg/cli.py": "def main():\n    pass\n",
        "pkg/app.py": ("class App:\n    def run(self):\n        pass\n\n\n"
                       "if '__main__' == __name__:\n    App().run()\n"),
        "pkg/launch.py": ("from .cli import main\n\n"
                          "if __name__ == '__main__':\n    main()\n")})
    got = {c.path for c in harvest.harvest(root) if c.kind == "entry_point"}
    assert got == {"pkg/app.py", "pkg/launch.py"}


# --- the counts on the pinned trees ----------------------------------------------

SAMPLES = Path("D:/repos/_AI/sample_repos")

# The forms per tree, measured at the pins. Section 3.4 counts 0 testpaths on
# tips, and the tree holds `testpaths = ["tests"]`. It counts 4 guards on
# icalendar, and the filter keeps `cli.py` and `equivalent_timezone_ids.py`.
PINS = {
    "tipsI": ("ff1f65f", {("readme", "README.md"), ("guard", "main.py")},
              {("testpaths", "pyproject.toml")}),
    "clickI": ("09c82f3", set(),
               {("testpaths", "pyproject.toml"), ("change_log", "CHANGES.md")}),
    "icalendarI": ("4f12af1e", {
        ("script", "pyproject.toml"), ("guard", "src/icalendar/cli.py"),
        ("guard", "src/icalendar/timezone/equivalent_timezone_ids.py")},
        {("testpaths", "pyproject.toml"), ("news_fragment", "pyproject.toml")}),
}


def _pinned(repo: str, commit: str, into: Path) -> Path:
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
    commit, entries, contributions = PINS[repo]
    root = _pinned(repo, commit, tmp_path / repo)
    got = harvest.harvest(root)
    assert {(c.detail["form"], c.path) for c in got if c.kind == "entry_point"} == entries
    assert {(c.detail["form"], c.path) for c in got
            if c.kind == "contribution"} == contributions
