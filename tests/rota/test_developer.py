"""
The Developer's hands, and the worktree they work in.

Before this the role had a namespace and nothing else: no worktree, no way to
change a file, and a `code.commit` that recorded a sha without running git. It
could read its tickets, ask questions, and then report a commit that never
happened.

The safety cases matter more here than anywhere else — this is the only place
the system touches the filesystem.
"""
from __future__ import annotations

import subprocess
import sys

import pytest

from rota.core import lifecycle, worktrees
from rota.core.db import init_db
from rota.core.sandbox import build
from rota.testkit import gitfixture


@pytest.fixture
def project(tmp_path):
    """A sample repo, and a rota database pointed at it."""
    repo = gitfixture.make(tmp_path)
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)",
               (str(repo.root),))
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) "
               "VALUES ('i1','stop double-charging','in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) "
               "VALUES ('tk1','i1','make prorate round half up')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) "
               "VALUES ('c1','tk1','prorate(999,1,3) returns 333')")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','pending')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','tk1')")
    yield db, repo
    gitfixture.cleanup(repo)


# ---------------------------------------------------------------------------
# The worktree belongs to the scheduler
# ---------------------------------------------------------------------------

def test_dispatch_creates_the_worktree(project):
    db, repo = project
    lifecycle.start(db, "b1")

    path = db.execute("SELECT worktree FROM batches WHERE id='b1'").fetchone()["worktree"]
    assert path, "a running batch with nowhere to work"
    assert (worktrees.Path(path) / "src" / "store" / "records.py").exists()


def test_the_developer_cannot_make_one(project):
    """
    Law 9 puts every decision about a worktree's life outside the role. A role
    that could create its own would be deciding where its work lives.
    """
    db, _ = project
    assert not [f for f in build("developer", db).functions()
                if "worktree" in f]


def test_a_deferred_batch_keeps_its_worktree_and_commits(project):
    """
    Commit-first is what bounds the loss on preemption: an uncommitted change
    never existed, and a committed one survives as deferred work.
    """
    db, _ = project
    lifecycle.start(db, "b1")
    tree = db.execute("SELECT worktree FROM batches WHERE id='b1'").fetchone()["worktree"]
    (worktrees.Path(tree) / "src" / "notify" / "templates.py").write_text(
        "TEMPLATES = {}\n", encoding="utf-8")
    sha = worktrees.commit(tree, "wip")

    lifecycle.defer(db, "b1")

    row = db.execute("SELECT status, worktree FROM batches WHERE id='b1'").fetchone()
    assert row["status"] == "deferred"
    assert row["worktree"] == tree
    assert worktrees.head(tree) == sha


def test_merging_removes_the_worktree_and_keeps_the_branch(project):
    db, repo = project
    lifecycle.start(db, "b1")
    lifecycle.merge(db, "b1")

    assert db.execute(
        "SELECT worktree FROM batches WHERE id='b1'").fetchone()["worktree"] is None
    branches = gitfixture.git(repo.root, "branch", "--list", "batch/b1")
    assert "batch/b1" in branches, "the record of what was built went with it"


def test_it_refuses_to_remove_a_worktree_outside_the_state_directory(project):
    """The only place the system can destroy something. 107 live worktrees in
    the repository this runs in."""
    db, repo = project
    db.execute("UPDATE batches SET worktree = ? WHERE id='b1'", (str(repo.root),))
    with pytest.raises(worktrees.WorktreeError, match="refusing"):
        worktrees.destroy(db, "b1")
    assert repo.root.exists()


# ---------------------------------------------------------------------------
# The hands
# ---------------------------------------------------------------------------

def test_the_developer_can_read_write_and_commit(project):
    db, _ = project
    lifecycle.start(db, "b1")
    sb = build("developer", db, batch_id="b1")

    before = sb.call("code.source", path="src/billing/charges.py")
    assert "def prorate" in before["text"]

    sb.call("code.write", path="src/billing/charges.py",
            text=before["text"].replace("return round(", "return int("))
    out = sb.call("code.commit", message="prorate rounds down")

    assert out["committed"] is True
    assert out["head_commit"]
    assert "src/billing/charges.py" in out["touched"]


def test_committing_nothing_says_so_rather_than_inventing_a_commit(project):
    """
    A session that read, reasoned and concluded the code was already right has
    nothing to commit. An empty commit invented to have something to report
    would be worse than saying so.
    """
    db, _ = project
    lifecycle.start(db, "b1")
    sb = build("developer", db, batch_id="b1")

    out = sb.call("code.commit", message="nothing to do")
    assert out["committed"] is False and "nothing changed" in out["why"]


def test_a_write_cannot_escape_the_worktree(project):
    db, _ = project
    lifecycle.start(db, "b1")
    sb = build("developer", db, batch_id="b1")

    with pytest.raises(ValueError, match="escapes"):
        sb.call("code.write", path="../../escaped.txt", text="no")


def test_the_commit_stamps_the_batch_head(project):
    """P1's whole mechanism: the gates fire on a commit they have not judged."""
    db, _ = project
    lifecycle.start(db, "b1")
    sb = build("developer", db, batch_id="b1")
    sb.call("code.write", path="src/notify/formatting.py", text="# emptied\n")
    out = sb.call("code.commit", message="empty formatting")

    staged = [w for w in sb.ctx.writes if w[0] == "batches"]
    assert staged and staged[-1][2]["head_commit"] == out["head_commit"]
    assert staged[-1][3] is False, "a commit is not an amendment of the batch"


# ---------------------------------------------------------------------------
# And the diff Critic was supposed to be reading
# ---------------------------------------------------------------------------

def test_critic_sees_an_actual_diff(project):
    """
    `code.read` was documented as "Critic's entire view of the implementation"
    and returned three identifiers. The role whose whole job is judging a diff
    was being handed ids.
    """
    db, _ = project
    lifecycle.start(db, "b1")
    dev = build("developer", db, batch_id="b1")
    dev.call("code.write", path="src/notify/formatting.py", text="# emptied\n")
    dev.call("code.commit", message="empty formatting")

    seen = build("critic", db, batch_id="b1").call("code.read")
    assert "src/notify/formatting.py" in seen["diff"]
    assert seen["touched"] == ["src/notify/formatting.py"]


def test_the_harness_runs_in_the_batch_worktree(project):
    """The tests Tester wrote, against the code Developer committed, in the
    worktree that holds both."""
    from rota.core import harness

    db, _ = project
    lifecycle.start(db, "b1")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst1','b1','c1','test_prorate.py',?)",
               ("from src.billing.charges import prorate\n\n"
                "def test_rounds():\n    assert prorate(999, 1, 3) == 333\n",))
    dev = build("developer", db, batch_id="b1")
    dev.call("code.commit", message="baseline")

    results = harness.run(db, "b1")
    assert results == [("tst1", "pass")], results


def test_a_missing_project_root_is_refused_not_guessed(tmp_path):
    """
    `project_root` fell back to `Path(".")` — the working directory — so a
    session run without config created a git worktree in whatever repository
    the process was started from. It did: a `batch/b1` worktree appeared inside
    this repo, beside the 107 real ones.

    Creating a worktree is not the kind of operation that gets to guess.
    """
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, provenance) "
               "VALUES ('i1','x','in_scope','decided')")
    db.execute("INSERT INTO batches (id, item_id) VALUES ('b1','i1')")

    with pytest.raises(worktrees.WorktreeError, match="project_root"):
        worktrees.create(db, "b1")


def test_starting_without_a_root_does_not_touch_any_repository(tmp_path):
    """`lifecycle.start` swallows the error so a batch can still run — but it
    must not have created anything on the way past."""
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, provenance) "
               "VALUES ('i1','x','in_scope','decided')")
    db.execute("INSERT INTO batches (id, item_id) VALUES ('b1','i1')")

    lifecycle.start(db, "b1")

    row = db.execute("SELECT status, worktree FROM batches WHERE id='b1'").fetchone()
    assert row["status"] == "running"
    assert row["worktree"] is None


# ---------------------------------------------------------------------------
# Which worktree the session works in
# ---------------------------------------------------------------------------

def test_a_fix_wake_resolves_its_batch(project):
    """
    `batch_id` was read as `refs[0] if kind == "tick:batch_start"`, so only the
    mode that *creates* a worktree got one. Developer woken by `tests_failing`
    or `verdict_failed` — both of which name the batch in `refs` — arrived with
    nothing to work in, and Critic, whose entire job is reading a diff, arrived
    the same way.
    """
    from rota.core.loop import _batch_of
    from rota.core.scheduler import Wake

    db, _ = project
    lifecycle.start(db, "b1")

    for kind in ("tick:tests_failing", "tick:verdict_failed", "tick:review"):
        wake = Wake(role="developer", kind=kind, refs=("b1",))
        assert _batch_of(db, wake) == "b1", kind


def test_a_message_wake_lands_in_the_running_batch(project):
    """A challenge from Critic names a finding, not a batch. There is only ever
    one batch running — `batch_start` refuses while anything else is — so the
    answer is unambiguous without the role choosing it."""
    from rota.core.loop import _batch_of
    from rota.core.scheduler import Wake

    db, _ = project
    lifecycle.start(db, "b1")

    assert _batch_of(db, Wake(role="developer", kind="message", refs=("f1",))) == "b1"


def test_with_nothing_running_there_is_no_batch(project):
    from rota.core.loop import _batch_of
    from rota.core.scheduler import Wake

    db, _ = project
    assert _batch_of(db, Wake(role="developer", kind="message")) is None
