"""
Frame 362, slice pass 1: the harvest of commitment witnesses, and its record.

Design B step 2 of `plans/design-onboarding-2026-11-03.md`: a deterministic
tool writes the witness lines of a project's outside commitments at boot,
and the rule of step 4 binds each one to source files by its kind. The key
of `rota/ANSWER_KEY_icalendar.md` names five commitments, and each one must
have a witness a person can check. The deep dive of the same date found 5
of 5 with a prototype. This module is the product of that prototype.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.onboarding import harvest
from rota.onboarding.boot import onboard

ICAL = Path("D:/tmp/rota-live/icalendar")
ICAL_COMMIT = "99619246"
# The dry3w7 copy of session ce483c7b, a run database from before the table.
DRY3W7 = Path("C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/"
              "ce483c7b-be58-4d58-bfc4-db1081518842/scratchpad/dry3w7")


def _head(root: Path) -> str:
    got = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                         capture_output=True, text=True)
    return got.stdout.strip() if got.returncode == 0 else ""


@pytest.fixture(scope="module")
def ical_db(tmp_path_factory):
    """A fresh run database with the icalendar harvest at `99619246`. The
    icalendar tree is read only."""
    head = _head(ICAL)
    if not head.startswith(ICAL_COMMIT):
        pytest.skip(f"icalendar is not at {ICAL_COMMIT} under {ICAL}")
    db = init_db(tmp_path_factory.mktemp("harvest") / "run.db")
    RUN["written"] = harvest.record(db, ICAL, head)
    RUN["head"] = head
    db.commit()
    yield db
    db.close()


# A connection takes no attribute, so the fixture's facts live here.
RUN: dict = {}


def _rows(db, sql, *args):
    return [dict(r) for r in db.execute(sql, args).fetchall()]


def _one(db, where, *args):
    rows = _rows(db, f"SELECT * FROM commitment_candidates WHERE {where}", *args)
    assert rows, where
    return rows


def _bound(db, cid):
    return {r["path"]: r["rule"] for r in _rows(
        db, "SELECT path, rule FROM candidate_bindings WHERE witness_id = ?", cid)}


# ---- the five key commitments ---------------------------------------------------

def test_the_fold_witness_is_the_75_octets_line(ical_db):
    """rfc_5545_conformance, prediction 3: `_foldline` and "75 octets"."""
    row = _one(ical_db, "path = 'src/icalendar/parser/string.py' AND line = 122 "
                        "AND kind = 'numeric_default'")[0]
    assert "75 octets" in row["text"]
    assert row["symbol"] == "_foldline"
    detail = json.loads(row["detail"])
    assert detail["signature_line"] == 119 and detail["value"] == 75


def test_the_rfc_5545_description_is_a_candidate(ical_db):
    row = _one(ical_db, "path = 'pyproject.toml' AND kind = 'metadata' "
                        "AND text LIKE '%description%'")[0]
    assert "RFC 5545 compatible" in row["text"] and row["line"] == 42


def test_the_import_surface_has_requires_python_and_all(ical_db):
    """the_pypi_package_and_import_surface: `requires-python` and `__all__`."""
    req = _one(ical_db, "path = 'pyproject.toml' AND text LIKE 'requires-python%'")[0]
    assert req["line"] == 58 and ">=3.10" in req["text"]
    exp = _one(ical_db, "kind = 'export'")
    # One candidate for each top-level `__init__.py`, not one for each name.
    assert len(exp) == 1
    assert exp[0]["path"] == "src/icalendar/__init__.py" and exp[0]["line"] == 101
    assert "__all__" in exp[0]["text"]
    assert "vBroken" in json.loads(exp[0]["detail"])["names"]


def test_the_dependencies_are_candidates(ical_db):
    """tzdata_and_dateutil_are_load_bearing."""
    deps = {json.loads(r["detail"])["dep"]: r for r in _one(
        ical_db, "path = 'pyproject.toml' AND detail LIKE '%\"dependency\"%'")}
    assert {"python-dateutil", "tzdata"} <= set(deps)
    assert deps["python-dateutil"]["line"] == 77
    assert deps["tzdata"]["line"] == 80


def test_the_entry_point_is_a_candidate(ical_db):
    """the_cli_preview_entry_point: the `[project.scripts]` line."""
    row = _one(ical_db, "path = 'pyproject.toml' AND detail LIKE '%\"script\"%'")[0]
    assert row["line"] == 140 and "icalendar.cli:main" in row["text"]


def test_the_round_trip_witness_names_vbroken(ical_db):
    """unknown_content_survives_round_trip: the docs sentence at 47 says
    "This preserves", and its subject `vBroken` is at 46. The candidate
    quotes the paragraph, so the witness holds both."""
    row = _one(ical_db, "path = 'docs/how-to/parse-errors.rst' "
                        "AND kind = 'preservation' AND text LIKE '%vBroken%'")[0]
    assert row["line"] == 46 and "preserves the raw value" in row["text"]


def test_75_octets_and_75_characters_contradict(ical_db):
    """The review's finding 5: both sides stay, and each names the other."""
    octets = _one(ical_db, "path = 'src/icalendar/parser/string.py' AND line = 122")[0]
    chars = _one(ical_db, "text LIKE '%75 characters%'")
    assert {(r["path"], r["line"]) for r in chars} == {
        ("docs/explanation/api-design.rst", 61),
        ("src/icalendar/parser/content_line.py", 285)}
    assert set(json.loads(octets["contradicts"])) == {r["id"] for r in chars}
    for r in chars:
        assert json.loads(r["contradicts"]) == [octets["id"]]


def test_the_counts_on_icalendar(ical_db):
    """Measured at `99619246`. The deep dive's prototype counted 302: 7
    metadata, 60 doc claims, 33 preservation, 1 numeric default, 13 issue
    comments, 84 exports and 104 test witnesses. The product counts one
    export for each `__init__.py`, ties a test witness to a module-level
    symbol named in code, reads the Sphinx `:rfc:` role as a standard, keeps
    issue citations in comments only, and adds the two "75 characters"
    lines as candidates."""
    counts = dict(ical_db.execute(
        "SELECT kind, COUNT(*) FROM commitment_candidates GROUP BY kind").fetchall())
    assert counts == {"metadata": 7, "doc_claim": 94, "preservation": 33,
                      "numeric_default": 3, "issue_comment": 12, "export": 1,
                      "test_witness": 35}
    assert sum(counts.values()) == 185 == RUN["written"]


def test_every_id_derives_from_the_content(ical_db):
    for r in _rows(ical_db, "SELECT * FROM commitment_candidates"):
        assert r["id"] == harvest.candidate_id(r["kind"], r["path"], r["line"],
                                               r["text"])
        assert r["commit_sha"] == RUN["head"]


# ---- the bindings -----------------------------------------------------------------

def test_the_fold_candidate_binds_its_file(ical_db):
    row = _one(ical_db, "path = 'src/icalendar/parser/string.py' AND line = 122")[0]
    assert _bound(ical_db, row["id"]) == {"src/icalendar/parser/string.py": "source"}


def test_the_entry_point_binds_its_module_and_pyproject(ical_db):
    row = _one(ical_db, "path = 'pyproject.toml' AND detail LIKE '%\"script\"%'")[0]
    assert _bound(ical_db, row["id"]) == {"src/icalendar/cli.py": "entry_point",
                                          "pyproject.toml": "entry_point"}


def test_the_rfc_5545_claim_binds_the_files_that_cite_it(ical_db):
    row = _one(ical_db, "path = 'pyproject.toml' AND text LIKE '%description%'")[0]
    bound = _bound(ical_db, row["id"])
    assert bound["src/icalendar/parser/string.py"] == "standard"
    silent = [rel for rel in harvest.Tree(ICAL).source()
              if "5545" not in (ICAL / rel).read_text(encoding="utf-8")]
    assert silent
    assert not set(silent) & set(bound)


def test_the_exports_bind_init_and_the_reexported_modules(ical_db):
    row = _one(ical_db, "kind = 'export'")[0]
    bound = _bound(ical_db, row["id"])
    assert set(bound.values()) == {"exports"}
    assert {"src/icalendar/__init__.py", "src/icalendar/prop/__init__.py",
            "src/icalendar/cal/__init__.py"} <= set(bound)


def test_a_docs_claim_that_cites_no_standard_binds_no_file(ical_db):
    """README.rst 9 says "supports" and names no standard. The review's low
    3: 56 such rows reached every source file and gave `parser/string.py`
    7,096 characters of push. The row stays for the Architect only."""
    row = _one(ical_db, "path = 'README.rst' AND kind = 'doc_claim' "
                        "AND text LIKE '%supports multiple timezone%'")[0]
    assert _bound(ical_db, row["id"]) == {}


def test_a_claim_with_no_rule_binds_project_wide(ical_db):
    """`requires-python` matches no placed rule, so it binds every source
    file. The project-wide set was 73 candidates before the low 3 fix."""
    row = _one(ical_db, "path = 'pyproject.toml' AND text LIKE 'requires-python%'")[0]
    bound = _bound(ical_db, row["id"])
    assert set(bound.values()) == {"project_wide"}
    assert set(bound) == set(harvest.Tree(ICAL).source())
    wide = ical_db.execute("SELECT COUNT(DISTINCT witness_id) FROM candidate_bindings "
                           "WHERE rule = 'project_wide'").fetchone()[0]
    assert wide == 17


def test_a_dependency_binds_its_importers(ical_db):
    row = _one(ical_db, "path = 'pyproject.toml' AND line = 77")[0]
    bound = _bound(ical_db, row["id"])
    assert set(bound.values()) == {"dependency"}
    assert "src/icalendar/cal/timezone.py" in bound


# ---- the record -------------------------------------------------------------------

def test_a_second_run_at_the_same_commit_writes_nothing(ical_db):
    before = ical_db.total_changes
    assert harvest.record(ical_db, ICAL, RUN["head"]) == 0
    assert ical_db.total_changes == before


def _small_tree(root: Path, a_imports: bool = False) -> Path:
    """The review's fixture: one dependency that no file imports at first."""
    (root / "pkg").mkdir(parents=True, exist_ok=True)
    (root / "pyproject.toml").write_bytes(
        b'[project]\nname = "pkg"\ndependencies = ["foolib"]\n')
    (root / "pkg" / "__init__.py").write_bytes(b"X = 1\n")
    (root / "pkg" / "a.py").write_bytes(
        (b"import foolib\n" if a_imports else b"") + b"Y = 2\n")
    # A definition, so the area is coded and constraint zero binds it.
    (root / "pkg" / "b.py").write_bytes(b"def z():\n    return 3\n")
    return root


def _count(db, table):
    return db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_a_fault_in_the_record_leaves_nothing(tmp_path, monkeypatch):
    """The review's high 1: a fault part way kept the rows before it, stamped
    with the commit, so the next run at that commit wrote nothing for good."""
    root = _small_tree(tmp_path / "proj")
    db = init_db(tmp_path / "run.db")
    real, calls = harvest.bind, [0]

    def flaky(tree, c):
        calls[0] += 1
        if calls[0] == 2:
            raise RuntimeError("probe fault")
        return real(tree, c)
    monkeypatch.setattr(harvest, "bind", flaky)
    try:
        with pytest.raises(RuntimeError):
            harvest.record(db, root, "A")
        assert _count(db, "commitment_candidates") == 0
        assert _count(db, "candidate_bindings") == 0
        monkeypatch.setattr(harvest, "bind", real)
        assert harvest.record(db, root, "A") == 2
    finally:
        db.close()


def test_a_new_commit_replaces_the_bindings(tmp_path):
    """The review's high 2: at commit A the dependency binds every source
    file. At commit B `pkg/a.py` imports it, so it binds that file alone."""
    root = _small_tree(tmp_path / "proj")
    db = init_db(tmp_path / "run.db")
    try:
        harvest.record(db, root, "A")
        dep = db.execute("SELECT id FROM commitment_candidates "
                         "WHERE text LIKE '%foolib%'").fetchone()[0]
        assert set(_bound(db, dep).values()) == {"project_wide"}
        assert len(_bound(db, dep)) == 3
        _small_tree(root, a_imports=True)
        harvest.record(db, root, "B")
        assert _bound(db, dep) == {"pkg/a.py": "dependency"}
        # A candidate the new harvest does not find keeps no binding.
        (root / "pyproject.toml").write_bytes(b'[project]\nname = "pkg"\n')
        harvest.record(db, root, "C")
        assert _bound(db, dep) == {}
    finally:
        db.close()


def test_a_harvest_fault_does_not_stop_the_onboarding(tmp_path, monkeypatch):
    """The review's low 9: the harvest is advisory. A fault becomes a stress
    line, and constraint zero and the report still come."""
    root = _small_tree(tmp_path / "proj")
    db = init_db(tmp_path / "run.db")

    def boom(*args, **kwargs):
        raise RuntimeError("probe harvest fault")
    monkeypatch.setattr(harvest, "record", boom)
    try:
        report = onboard(db, root)
        assert report.candidates == 0
        assert any("probe harvest fault" in s for s in report.stresses)
        assert db.execute("SELECT 1 FROM constraints WHERE id = 'k0'").fetchone()
    finally:
        db.close()


def test_a_bare_tree_yields_no_candidate_and_no_error(tmp_path):
    """No README, no pyproject and no docs: the boot runs and writes none."""
    root = tmp_path / "bare"
    (root / "pkg").mkdir(parents=True)
    (root / "pkg" / "core.py").write_bytes(b"def add(a, b):\n    return a + b\n")
    db = init_db(tmp_path / "run.db")
    try:
        report = onboard(db, root)
        assert report.candidates == 0
        assert db.execute("SELECT COUNT(*) FROM commitment_candidates").fetchone()[0] == 0
        assert db.execute("SELECT COUNT(*) FROM candidate_bindings").fetchone()[0] == 0
    finally:
        db.close()


def test_the_boot_writes_the_candidates_once(tmp_path):
    """`onboard` runs the harvest after the indexer. The second onboard at
    the same commit writes no candidate."""
    root = tmp_path / "proj"
    (root / "src" / "proj").mkdir(parents=True)
    (root / "pyproject.toml").write_bytes(
        b'[project]\nname = "proj"\nrequires-python = ">=3.10"\n')
    (root / "src" / "proj" / "__init__.py").write_bytes(
        b'from proj.core import add\n\n__all__ = ["add"]\n')
    (root / "src" / "proj" / "core.py").write_bytes(b"def add(a, b):\n    return a + b\n")
    for args in (["init", "-q"], ["add", "."],
                 ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "x"]):
        subprocess.run(["git", "-C", str(root), *args], check=True,
                       capture_output=True)
    db = init_db(tmp_path / "run.db")
    try:
        assert onboard(db, root).candidates == 3
        assert onboard(db, root).candidates == 0
        export = db.execute("SELECT id FROM commitment_candidates "
                            "WHERE kind = 'export'").fetchone()[0]
        assert _bound(db, export) == {"src/proj/__init__.py": "exports",
                                      "src/proj/core.py": "exports"}
    finally:
        db.close()


def test_an_older_database_opens_and_gains_the_empty_tables(tmp_path):
    if not (DRY3W7 / "dry3.db").is_file():
        pytest.skip(f"the dry3w7 copy is not at {DRY3W7}")
    for suffix in ("", "-wal", "-shm"):
        src = DRY3W7 / f"dry3.db{suffix}"
        if src.is_file():
            shutil.copyfile(src, tmp_path / f"dry3.db{suffix}")
    probe = __import__("sqlite3").connect(tmp_path / "dry3.db")
    had = {r[0] for r in probe.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    probe.close()
    assert "commitment_candidates" not in had
    db = init_db(tmp_path / "dry3.db")
    try:
        for table in ("commitment_candidates", "candidate_bindings"):
            assert db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0
    finally:
        db.close()
