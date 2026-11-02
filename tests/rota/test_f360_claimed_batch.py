"""
Frame 360: an unchanged tree at the start of a batch is a claim, and the
tests prove it.

On dry run 2 the item `returns_tip_as_before` had criteria that the code
already passed. Three Developer sessions called `code.commit` on an
unchanged tree and said that the criteria are met. The door wrote nothing,
the stall rule counted three failed starts, and the stopped page said "The
team gave up" (`plans/dry2-wall1-read-2026-11-02.md`, section 1).

Roman ruled shape A on 2026-11-02 at 17:14
(`plans/design-item-already-held-2026-11-02.md`, section 3 A). The door
writes the fork commit as the batch's head, with a mark that the head is a
claim. The Tester, the harness, the Critic and the merge then prove the
claim with tests, and the page says "No code changed".
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from rota.core import lifecycle, provision, worktrees
from rota.core.db import SessionResult, init_db, session_commit
from rota.core import predicates
from rota.core.runner import _as_write
from rota.core.sandbox import build
from rota.core.scheduler import tick_batch_start
from rota.roles.principal import render_state
from rota.testkit import gitfixture, venvtemplate

# The words of the ruling, to the letter (design page, section 3 A).
CLAIM_NOTE = "You claimed the criteria are met. The Tester's tests check the claim."
CLAIMED_LINE = "No code changed. These tests show the code already does this."

# The dry2w3 copy of session 208997ee, and the tips project it ran on. The
# measure of the design page reads both. The test never opens either one
# for writing: it copies the database and clones the project.
DRY2W3 = Path("C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/"
              "208997ee-71a2-496f-83aa-e1425ff49524/scratchpad/dry2w3")
TIPS = Path("D:/repos/_AI/sample_repos/tipsI")
FORK = "ff1f65f"


def _git(at, *args):
    return subprocess.run(["git", "-C", str(at), *args], capture_output=True,
                          text=True).stdout.strip()


def _land(db, sb, sid="s_f360"):
    """Commit the session's staged writes, as the runner does at its end."""
    session_commit(db, SessionResult(
        session_id=sid, role="developer", wake_kind="tick:batch_start",
        wake_refs=(sb.ctx.batch_id,),
        writes=[_as_write(w) for w in sb.ctx.writes]))
    db.commit()


def _heads(sb):
    return [w for w in sb.ctx.writes if w[0] == "batches"
            and "head_commit" in w[2]]


# ---------------------------------------------------------------------------
# The measure of the design page, section 3 A, on the dry2w3 copy
# ---------------------------------------------------------------------------

@pytest.fixture
def dry2w3(tmp_path):
    """A writable copy of dry2w3, and a clone of the tips project at the fork.

    The worktree of `b_2` belongs to the live tips project, so the test
    gives `b_2` a worktree of its own clone at the same fork."""
    if not (DRY2W3 / "dry2.db").is_file():
        pytest.skip(f"the dry2w3 copy is not at {DRY2W3}")
    if _git(TIPS, "cat-file", "-t", FORK) != "commit":
        pytest.skip(f"the tips project at {TIPS} does not hold {FORK}")
    for suffix in ("", "-wal", "-shm"):
        src = DRY2W3 / f"dry2.db{suffix}"
        if src.is_file():
            shutil.copyfile(src, tmp_path / f"dry2.db{suffix}")
    clone = tmp_path / "tipsI"
    subprocess.run(["git", "clone", "-q", "--no-checkout", str(TIPS), str(clone)],
                   check=True, capture_output=True)
    subprocess.run(["git", "-C", str(clone), "checkout", "-q", FORK],
                   check=True, capture_output=True)
    exclude = clone / ".git" / "info" / "exclude"
    exclude.parent.mkdir(parents=True, exist_ok=True)
    exclude.write_text(".rota/\n", encoding="utf-8", newline="\n")
    repo = gitfixture.SampleRepo(root=clone)
    repo._before = gitfixture.registered_worktrees(clone)
    tree = repo.worktree("b_2")
    db = init_db(tmp_path / "dry2.db")
    db.execute("DELETE FROM tick_attempts "
               "WHERE tick_key = 'developer|tick:batch_start|b_2'")
    db.execute("UPDATE config SET value = ? WHERE key = 'project_root'",
               (str(clone),))
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b_2'", (str(tree),))
    db.commit()
    yield db, tree
    db.close()
    gitfixture.cleanup(repo)


def test_the_measure_on_dry2w3(dry2w3):
    """The design page's measure: an unchanged tree on `b_2` becomes a head
    at the fork ff1f65f, the stall rule is quiet, the Tester wakes and the
    merge gate no longer says "nothing committed"."""
    db, tree = dry2w3
    fork = worktrees.head(tree)
    assert fork.startswith(FORK)
    # Control: the code before the frame.
    assert db.execute("SELECT head_commit FROM batches WHERE id = 'b_2'"
                      ).fetchone()[0] is None
    assert [w.refs for w in tick_batch_start(db)] == [("b_2",)]
    assert "b_2" not in [w.refs[0] for w in predicates.tests_missing(db)]
    assert lifecycle.mergeable(db, "b_2") == "nothing committed"
    assert ("b_2",) not in [w.refs for w in predicates.harness(db)]

    sb = build("developer", db, batch_id="b_2")
    out = sb.call("code.commit", message="the criteria are met")
    assert CLAIM_NOTE in out["note"], out
    _land(db, sb)

    row = db.execute("SELECT head_commit, claimed_head FROM batches "
                     "WHERE id = 'b_2'").fetchone()
    assert row["head_commit"] == fork
    assert row["claimed_head"] == fork
    assert tick_batch_start(db) == []
    assert [w for w in predicates.tests_missing(db) if w.refs == ("b_2",)], \
        "the Tester is not woken for the claimed batch"
    # The four inherited tests of b_2 are owed a run at the claimed head.
    assert ("b_2",) in [w.refs for w in predicates.harness(db)]
    assert lifecycle.mergeable(db, "b_2") != "nothing committed"


# ---------------------------------------------------------------------------
# The door, on the sample project
# ---------------------------------------------------------------------------

@pytest.fixture
def project(tmp_path, monkeypatch):
    """A sample repo, a rota database pointed at it, and a running batch."""
    monkeypatch.setattr(provision, "ensure_env", venvtemplate.ensure_env)
    repo = gitfixture.make(tmp_path)
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)",
               (str(repo.root),))
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i1','keep prorate','in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) "
               "VALUES ('tk1','i1','prorate stays as it is')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) "
               "VALUES ('c1','tk1','prorate(999,1,3) returns 333')")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','pending')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    db.commit()
    lifecycle.start(db, "b1")
    yield db, repo
    gitfixture.cleanup(repo)


def test_an_unchanged_tree_with_no_head_is_a_claim(project):
    db, _ = project
    sb = build("developer", db, batch_id="b1")
    tree = db.execute("SELECT worktree FROM batches WHERE id = 'b1'").fetchone()[0]
    fork = worktrees.head(tree)

    out = sb.call("code.commit", message="the criteria are met")

    assert out["committed"] is False and "nothing changed" in out["why"]
    assert CLAIM_NOTE in out["note"], out
    staged = _heads(sb)
    assert len(staged) == 1
    assert staged[0][2] == {"head_commit": fork, "claimed_head": fork}
    assert staged[0][3] is False, "a claim is not an amendment of the batch"


def test_a_batch_with_a_head_gets_no_claim(project):
    """A head on record is a change or a claim already. An unchanged tree
    on top of it claims nothing new."""
    db, _ = project
    db.execute("UPDATE batches SET head_commit = 'abc' WHERE id = 'b1'")
    db.commit()
    sb = build("developer", db, batch_id="b1")

    out = sb.call("code.commit", message="nothing to do")

    assert _heads(sb) == []
    assert CLAIM_NOTE not in out["note"]


def test_the_escalation_branch_writes_no_head(project):
    db, _ = project
    sb = build("developer", db, batch_id="b1")
    sb.ctx.outbound.append({"id": "m_x", "to_role": "architect",
                            "verb": "escalate", "body_refs": ["c1"]})

    out = sb.call("code.commit", message="nothing to do")

    assert out["note"] == ("the tree is exactly as you found it. You have "
                           "sent your message: end the session")
    assert _heads(sb) == []


def test_the_challenge_branch_writes_no_head(project):
    """A challenge ends the session before the commit (frame 200), so no
    claim can follow it."""
    db, _ = project
    sb = build("developer", db, batch_id="b1")
    sb.ctx.outbound.append({"id": "m_x", "to_role": "tester",
                            "verb": "challenge", "body_refs": ["c1"]})

    with pytest.raises(Exception, match="you sent challenge to tester"):
        sb.call("code.commit", message="nothing to do")
    assert _heads(sb) == []


def test_a_refused_code_write_is_not_a_claim(project):
    """Night 163's bg_2: the doors refused the writes, and the session then
    found its tree unchanged. That session meant a change, so it claims
    nothing (design page, section 3 A, "a second failure")."""
    db, _ = project
    sb = build("developer", db, batch_id="b1")
    with pytest.raises(ValueError, match="the name of the argument"):
        sb.call("code.write", path="path", text="x = 1\n")

    out = sb.call("code.commit", message="the criteria are met")

    assert _heads(sb) == []
    assert CLAIM_NOTE not in out["note"]
    assert "the change comes first" in out["note"]


# ---------------------------------------------------------------------------
# The merge and the page
# ---------------------------------------------------------------------------

@pytest.fixture
def world(tmp_path):
    """The designer's merge probe: the sample project onboarded, one item
    and one running batch `b1` with a worktree at the fork."""
    from rota.onboarding import boot

    db = init_db(tmp_path / "rota.db")
    repo = gitfixture.make(tmp_path, name="f360")
    boot.onboard(db, repo.root)
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i1','as before','in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('t1','i1','x')")
    tree = repo.worktree("b1")
    db.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES "
               "('b1','i1','running',?)", (str(tree),))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','t1')")
    db.commit()
    yield db, repo, tree
    gitfixture.cleanup(repo)


def test_a_claimed_batch_merges_its_tests_and_the_page_says_no_code_changed(world):
    db, repo, tree = world
    base = repo.head()
    sb = build("developer", db, batch_id="b1")
    sb.call("code.commit", message="the criteria are met")
    _land(db, sb)
    assert db.execute("SELECT head_commit FROM batches WHERE id = 'b1'"
                      ).fetchone()[0] == base
    db.execute("INSERT INTO tests (id, batch_id, path, body) VALUES "
               "('tst1','b1','tests/test_probe_f360.py',"
               "'def test_x():' || char(10) || '    assert True' || char(10))")
    db.commit()

    lifecycle.merge(db, "b1")

    assert db.execute("SELECT status FROM batches WHERE id = 'b1'"
                      ).fetchone()[0] == "merged"
    new_head = repo.head()
    parents = _git(repo.root, "rev-list", "--parents", "-n", "1", new_head).split()
    assert len(parents) - 1 == 2
    assert _git(repo.root, "diff", "--name-only", base, new_head).splitlines() \
        == ["tests/test_probe_f360.py"]
    page = render_state(db)
    assert CLAIMED_LINE in page, page
    assert "built" not in page, page


def test_the_page_counts_a_claimed_batch_apart(tmp_path):
    """A built batch keeps its words, which recorded cases carry. A claimed
    batch has its own line. A claim that a later commit replaced is a
    change."""
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind) VALUES ('i1','x','in_scope')")
    for bid, head, claim in (("b1", "aaa", None), ("b2", "bbb", "bbb"),
                             ("b3", "ccc", "old")):
        db.execute("INSERT INTO batches (id, item_id, status, head_commit, "
                   "claimed_head) VALUES (?, 'i1', 'merged', ?, ?)",
                   (bid, head, claim))
    db.commit()

    page = render_state(db)

    assert "Done: 2 changes built, tested and merged." in page, page
    assert CLAIMED_LINE in page, page


def test_an_older_database_gains_the_mark(tmp_path):
    """A run database outlives the schema, so `init_db` adds the column in
    place, and every older batch reads as no claim."""
    db = init_db(tmp_path / "rota.db")
    db.execute("ALTER TABLE batches DROP COLUMN claimed_head")
    db.execute("INSERT INTO items (id, text, kind) VALUES ('i1','x','in_scope')")
    db.execute("INSERT INTO batches (id, item_id, status, head_commit) "
               "VALUES ('b1','i1','merged','aaa')")
    db.commit()
    db.close()

    db = init_db(tmp_path / "rota.db")

    assert db.execute("SELECT claimed_head FROM batches WHERE id = 'b1'"
                      ).fetchone()[0] is None
    assert "Done: 1 change built, tested and merged." in render_state(db)
