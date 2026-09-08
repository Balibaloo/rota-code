"""
The greenfield floor: A and B of the seat's menu, ruled 2026-08-28.

B: a project with no program is a *finished* onboarding, not a small one --
walked live, a one-line README put orient through three sessions of invented
scope and one sentence became five items. The index already knows the
difference; the phases close mechanically with one visible record.

A: the harness floor. `pytest <path> -q` from the worktree root is only
deterministic if testpaths and the import path are pinned; the scaffold lays
exactly that, only where nothing exists, commits it as the batch's first
commit, and leaves any repository with its own configuration entirely alone
(the seat's constraint: assume nothing about ground that has a shape).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.core import scaffold
from rota.core.scheduler import frontier, onboarding_phase


def _repo(tmp_path, files):
    root = tmp_path / "proj"
    root.mkdir()
    for rel, body in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    for cmd in (["git", "init", "-q"], ["git", "add", "-A"],
                ["git", "-c", "user.email=t@t", "-c", "user.name=t",
                 "commit", "-qm", "init"]):
        subprocess.run(cmd, cwd=root, check=True, capture_output=True)
    return root


def test_an_empty_program_is_a_finished_onboarding(tmp_path):
    from rota.onboarding import boot

    root = _repo(tmp_path, {"README.md": "# greeter\n"})
    db = init_db(tmp_path / "rota.db")
    boot.onboard(db, root)
    assert onboarding_phase(db) == "done"
    kinds = {w.kind for w in frontier(db)}
    assert not any(k.startswith("tick:orient") or k.startswith("tick:survey")
                   or k.startswith("tick:challenge") for k in kinds), kinds
    row = db.execute("SELECT outcome FROM survey_records "
                     "WHERE id='system:@empty'").fetchone()
    assert row and row["outcome"] == "none_found", \
        "the skip is a record, not a silence"


def test_a_real_program_still_onboards_in_phases(tmp_path):
    from rota.onboarding import boot

    root = _repo(tmp_path, {"README.md": "# x\n",
                            "src/app.py": "def run():\n    return 1\n"})
    db = init_db(tmp_path / "rota.db")
    boot.onboard(db, root)
    assert onboarding_phase(db) != "done", \
        "one real source file and the phases are back"


def test_the_floor_is_laid_only_where_nothing_exists(tmp_path):
    root = _repo(tmp_path, {"README.md": "# greeter\n"})
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('i1','x','in_scope','decided',"
               "'approved',1,1)")
    db.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES "
               "('b1','i1','running',?)", (str(root),))
    db.commit()

    made = scaffold.ensure_floor(db, "b1")
    assert "pyproject.toml" in made and "tests/" in made
    # The program floor. Ground with no Python gets an entry point that
    # starts, and a README that says how to run it (tips4, 2026-09-04: the
    # merged program had no way to run it).
    assert "main.py" in made and "README.md" in made
    main = (root / "main.py").read_text(encoding="utf-8")
    assert 'if __name__ == "__main__":' in main and "def main(" in main
    assert "python main.py" in (root / "README.md").read_text(encoding="utf-8")
    import subprocess, sys
    started = subprocess.run([sys.executable, "main.py", "--help"], cwd=root,
                             capture_output=True, text=True, timeout=30)
    assert started.returncode == 0, started.stderr
    body = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert 'testpaths = ["tests"]' in body and 'pythonpath = ["."]' in body
    log = subprocess.run(["git", "log", "--oneline"], cwd=root,
                         capture_output=True, text=True).stdout
    assert "the harness floor" in log, "commit-first bounds the loss"

    assert scaffold.ensure_floor(db, "b1") == [], "idempotent"


def test_a_shaped_repository_is_left_alone(tmp_path):
    """The seat's constraint, pinned: any existing test configuration means
    the project already chose, and the scaffold assumes nothing."""
    root = _repo(tmp_path, {"README.md": "# x\n",
                            "setup.cfg": "[metadata]\nname = theirs\n"})
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('i1','x','in_scope','decided',"
               "'approved',1,1)")
    db.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES "
               "('b1','i1','running',?)", (str(root),))
    db.commit()
    made = scaffold.ensure_floor(db, "b1")
    assert "pyproject.toml" not in made
    assert not (root / "pyproject.toml").exists()
    assert "main.py" not in made, "a tree with Python has its own shape"


def test_a_merged_batch_lands_on_the_base_branch(tmp_path):
    """Walk thirty-seven: the first batch the story ever delivered was
    marked merged, its worktree removed, and the main branch still held
    only the initial commit. The merge merges now."""
    from rota.core import lifecycle, worktrees

    root = _repo(tmp_path, {"README.md": "# greeter\n"})
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)",
               (str(root),))
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('i1','x','in_scope','decided',"
               "'approved',1,1)")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','pending')")
    db.commit()
    lifecycle.start(db, "b1")
    wt = Path(db.execute("SELECT worktree FROM batches WHERE id='b1'").fetchone()["worktree"])
    (wt / "script.py").write_text("print('Hello User!')\n", encoding="utf-8")
    worktrees.commit(wt, "the script")
    lifecycle.merge(db, "b1")
    assert (root / "script.py").exists(), "the deliverable is on the base branch"
    assert (root / ".gitignore").exists(), "the floor ignores caches"
    log = subprocess.run(["git", "log", "--oneline"], cwd=root,
                         capture_output=True, text=True).stdout
    assert "rota: deliver b1" in log
    assert db.execute("SELECT status FROM batches WHERE id='b1'").fetchone()["status"] == "merged"


def test_a_plain_folder_gets_a_repository_at_batch_start(tmp_path):
    """The principal's own first trial: a folder with no git repository.
    Onboarding tolerated it and batch start could not -- no worktree, no
    build, no harness, and nothing said so."""
    from rota.core import lifecycle, scaffold

    root = tmp_path / "plain"
    root.mkdir()
    (root / "README.md").write_text("# greeter\n", encoding="utf-8")
    assert not (root / ".git").exists()
    assert scaffold.ensure_repo(root) is True
    assert (root / ".git").exists()
    assert scaffold.ensure_repo(root) is False, "once"

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)",
               (str(root),))
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES ('i1','x','in_scope','decided',"
               "'approved',1,1)")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','pending')")
    db.commit()
    lifecycle.start(db, "b1")
    wt = db.execute("SELECT worktree FROM batches WHERE id='b1'").fetchone()["worktree"]
    assert wt and Path(wt).is_dir(), "the batch has somewhere to build"
