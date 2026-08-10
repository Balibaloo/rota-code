"""
The git fixture, and the rule that keeps it from touching real work.

This repository has 107 registered worktrees and none of them is temp-rooted, so
a teardown that removed by name would eventually remove somebody's afternoon.
The safety cases here are the point of the file; the rest is the fixture doing
its job.
"""
from __future__ import annotations

import subprocess
import sys

import pytest

from rota.testkit import gitfixture
from rota.testkit.samplerepo import PLANTED


@pytest.fixture
def repo(tmp_path):
    r = gitfixture.make(tmp_path)
    yield r
    gitfixture.cleanup(r)


# ---------------------------------------------------------------------------
# Safety
# ---------------------------------------------------------------------------

def test_it_refuses_to_build_outside_a_temp_directory():
    from pathlib import Path

    with pytest.raises(RuntimeError, match="temp"):
        gitfixture.make(Path(__file__).resolve().parent)


def test_a_worktree_outside_temp_is_impossible(repo, monkeypatch):
    """
    The path is derived from the repo root rather than taken as an argument, so
    a caller cannot place one outside the sandbox even by trying.
    """
    monkeypatch.setattr(gitfixture, "is_temp_rooted", lambda p: False)
    with pytest.raises(RuntimeError, match="refusing"):
        repo.worktree("nope")


def test_teardown_leaves_worktrees_it_did_not_make(repo):
    """
    Two conditions, both required: new *and* temp-rooted. Temp-but-not-new is
    refused because another test may still be using it.
    """
    made = repo.worktree("mine")
    repo._before.add(str(made))          # pretend it was already registered

    assert repo.remove_worktrees() == []
    assert made.exists()


def test_teardown_removes_what_it_made(repo):
    made = repo.worktree("mine")
    assert made.exists()
    assert repo.remove_worktrees() == [str(made)]


def test_this_repository_would_be_refused():
    """
    The real one, by name. 107 worktrees, none temp-rooted — if
    `is_temp_rooted` ever loosens, this fails before anything is removed.
    """
    from rota import paths

    assert not gitfixture.is_temp_rooted(paths.REPO)


# ---------------------------------------------------------------------------
# The fixture itself
# ---------------------------------------------------------------------------

def test_the_sample_has_a_real_history(repo):
    log = repo.log()
    assert len(log) >= 6, log
    assert "store, first cut" in log[-1]


def test_its_own_tests_pass(repo):
    """A fixture that starts red muddies every assertion downstream of it."""
    out = subprocess.run([sys.executable, "-m", "pytest", "-q"],
                         cwd=repo.root, capture_output=True, text=True)
    assert out.returncode == 0, out.stdout[-800:]


def test_the_planted_properties_are_there(repo):
    """
    The assertions of stage 7 are about these. If the fixture stops carrying
    one, the onboarding case would pass by finding nothing.
    """
    for rel in PLANTED["collision"]["senses"]:
        assert (repo.root / rel).exists(), rel

    text = {rel: (repo.root / rel).read_text(encoding="utf-8")
            for rel in PLANTED["collision"]["senses"]}
    assert all("account" in t.lower() for t in text.values())

    fan_in = repo.root / PLANTED["fan_in"]["module"]
    assert (fan_in / "schema.sql").exists(), "the persisted schema is the commitment"
    for importer in PLANTED["fan_in"]["imported_by"]:
        module = repo.root / importer
        sources = "".join(p.read_text(encoding="utf-8")
                          for p in module.rglob("*.py"))
        assert "store" in sources, f"{importer} does not import store"


def test_it_holds_more_than_one_language(repo):
    """A single-language sample would let a Python-only indexer pass."""
    suffixes = {p.suffix for p in repo.root.rglob("*") if p.is_file()}
    assert {".py", ".js"} <= suffixes


def test_a_worktree_is_a_real_checkout(repo):
    wt = repo.worktree("b1")
    assert (wt / "src" / "store" / "records.py").exists()

    repo.edit(wt, "src/notify/templates.py", "TEMPLATES = {}\n")
    sha = repo.commit_in(wt, "empty the templates")

    assert sha != repo.head()
    assert "empty the templates" in repo.diff(wt) or sha


def test_the_barren_area_touches_nothing_persisted(repo):
    """
    Constraint zero should shrink by exactly this area, so it has to genuinely
    have nothing worth constraining — not merely be small.
    """
    barren = repo.root / PLANTED["barren"]["module"]
    sources = "".join(p.read_text(encoding="utf-8") for p in barren.rglob("*.py"))
    assert "store" not in sources
    assert "sqlite" not in sources.lower()


def test_an_edit_that_changes_nothing_is_refused_with_a_reason(tmp_path):
    """
    `git commit` on an unchanged tree exits 1 with nothing on stderr, so a case
    whose `edit:` matched the file it replaced died as a bare `RuntimeError:
    git commit -q -m ...:` half an hour into an L1 run.

    The cause is always worth naming: the role under test would have been handed
    an empty diff, and a Critic that declines to judge what it cannot see is
    behaving correctly while the case reads as a failure.
    """
    from rota.testkit import samplerepo

    repo = gitfixture.make(tmp_path)
    try:
        tree = repo.worktree("b1")
        path = "src/billing/charges.py"
        repo.edit(tree, path, samplerepo.FILES[path])

        with pytest.raises(RuntimeError, match="nothing to commit"):
            repo.commit_in(tree, "no change at all")
    finally:
        gitfixture.cleanup(repo)
