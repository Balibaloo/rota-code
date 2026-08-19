"""
The unresolved counter, which could not do the job its docstring assigns it.

`indexer.py` opens: *"An index that quietly loses a third of its edges partitions
the codebase wrongly and gives no sign."* The counter is the sign. On the clean
synthetic fixture it read 25 unresolved against 30 edges — and of those 25,
seventeen were stdlib or external and correctly not edges, eight were phantoms,
and the number of actually-missed internal edges was zero.

A tripwire that reads 45% when the truth is 0% is one nobody believes the day it
is right.

The phantoms came from `export_statement` being listed as an import node for
JS and TS. `export function money() {}` has no `source`, so `_targets` fell
through `MODULE_FIELDS`, recursed into the declaration, and returned the
exported symbol's own name as an import target. Three files containing no import
statement whatsoever reported three unresolved imports.

It never fabricated an edge, which is the thing the module says is worse than a
missing one: `resolve`'s tail matches `/name` and `/name/__init__.py` and never
tries file suffixes, so a bare JS name stays unresolved rather than binding to
something. Noise, not corruption.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.onboarding import indexer


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "web"
    root.mkdir()
    return root


def _build(tmp_path, root):
    return indexer.build(init_db(tmp_path / "idx.db"), root)


def test_a_repository_with_no_imports_reports_none_unresolved(tmp_path, project):
    """The measurement that opened this: three files, no imports, three phantoms."""
    (project / "a.js").write_text("export function money() { return 1; }\n")
    (project / "b.js").write_text("export const rate = 2;\nexport class Bill {}\n")
    (project / "c.ts").write_text("export type Id = string;\n"
                                  "export interface Row { id: Id }\n")

    report = _build(tmp_path, project)

    assert report.files == 3
    assert report.unresolved == 0, "an export of a local symbol is not an import"


def test_a_re_export_is_still_an_import(tmp_path, project):
    """
    The half that must survive. `export { x } from "./y"` names another module
    and is a real dependency edge — the distinction is the `source` field, which
    only the re-exporting form has.
    """
    (project / "y.js").write_text("export const x = 1;\n")
    (project / "index.js").write_text('export { x } from "./y";\n')

    report = _build(tmp_path, project)

    assert report.edges >= 1, "a re-export is a dependency and must be an edge"
    assert report.unresolved == 0


def test_an_export_of_a_local_symbol_still_indexes_the_symbol(tmp_path, project):
    """
    Skipping the node as an import must not skip it as a definition. The
    exported function is exactly the kind of grain a survey cites.
    """
    (project / "a.js").write_text(
        "export function money() { return 1; }\n"
        "export class Bill { total() { return 2; } }\n")

    conn = init_db(tmp_path / "idx.db")
    indexer.build(conn, project)

    symbols = {r["grain"] for r in conn.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'symbol'")}
    assert any(g.endswith("::money") for g in symbols), sorted(symbols)
    assert any(g.endswith("::Bill") for g in symbols), sorted(symbols)


def test_an_unresolved_import_is_still_counted(tmp_path, project):
    """
    The tripwire has to keep working. An import of something that is not in the
    tree is exactly what it exists to notice — the fix removes phantoms, not the
    signal.
    """
    (project / "a.js").write_text('import { thing } from "./nowhere";\n')

    assert _build(tmp_path, project).unresolved == 1


# ---------------------------------------------------------------------------
# What counts as authored
# ---------------------------------------------------------------------------

def test_gitignored_files_are_not_indexed(tmp_path):
    """
    The design story says the index respects `.gitignore` throughout, *"so build
    artefacts, dependencies, and the framework's own state folder never enter
    it"*. The implementation was a hardcoded eleven-name `SKIP_DIRS`, so any
    project with generated or vendored code outside those names had it indexed,
    partitioned and surveyed as if a person had written it.

    Asked of git rather than reimplemented: `.gitignore` has globs, negations,
    per-directory files and a global excludes file, and a partial parser is the
    kind of thing that looks right on the repository it was written against.
    """
    from rota.testkit import gitfixture

    repo = gitfixture.make(tmp_path)
    root = repo.root
    (root / "generated").mkdir(exist_ok=True)
    (root / "generated" / "schema_pb2.py").write_text("class Wire: pass\n")
    (root / "vendored.py").write_text("class Copied: pass\n")
    (root / "mine.py").write_text("class Written: pass\n")
    (root / ".gitignore").write_text("generated/\nvendored.py\n")

    conn = init_db(tmp_path / "idx.db")
    indexer.build(conn, root)
    grains = {r["grain"] for r in conn.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'path'")}

    assert "mine.py" in grains
    assert not [g for g in grains if "generated" in g], sorted(grains)
    assert "vendored.py" not in grains


def test_a_tree_that_is_not_a_checkout_still_indexes(tmp_path):
    """
    Falling back rather than refusing. A directory can be onboarded without
    being a repository, and the indexer is not the place to start caring about
    version control.
    """
    root = tmp_path / "plain"
    root.mkdir()
    (root / "a.py").write_text("class A: pass\n")
    (root / "node_modules").mkdir()
    (root / "node_modules" / "dep.py").write_text("class Dep: pass\n")

    conn = init_db(tmp_path / "plain.db")
    report = indexer.build(conn, root)

    grains = {r["grain"] for r in conn.execute(
        "SELECT grain FROM code_index WHERE grain_kind = 'path'")}
    assert grains == {"a.py"}, "SKIP_DIRS is still the floor without git"
    assert report.files == 1


def test_our_own_state_directory_is_never_indexed(tmp_path):
    """
    `.rota/` is our state directory inside somebody else's project: untracked,
    and nothing obliges them to have ignored it — so git lists it and
    `SKIP_DIRS` has to stay a floor even when git answers.
    """
    from rota.testkit import gitfixture

    repo = gitfixture.make(tmp_path)
    (repo.root / ".rota").mkdir(exist_ok=True)
    (repo.root / ".rota" / "leak.py").write_text("class Leak: pass\n")

    conn = init_db(tmp_path / "idx2.db")
    indexer.build(conn, repo.root)

    grains = {r["grain"] for r in conn.execute("SELECT grain FROM code_index")}
    assert not [g for g in grains if ".rota" in g], sorted(grains)
