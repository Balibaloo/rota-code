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

import json
import subprocess
import sys

import pytest

from rota.core import lifecycle, provision, worktrees
from rota.core.db import init_db
from rota.core.sandbox import build
from rota.testkit import gitfixture, venvtemplate


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A sample repo, and a rota database pointed at it."""
    # A batch's `.venv` is a copy of one built per worker. A venv and pip per
    # test held one xdist worker for 326s, the suite's tail (frame 206's count).
    monkeypatch.setattr(provision, "ensure_env", venvtemplate.ensure_env)
    repo = gitfixture.make(tmp_path)
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)",
               (str(repo.root),))
    db.execute("INSERT INTO items (id, text, kind, approval, "
               "approval_ver, version) "
               "VALUES ('i1','stop double-charging','in_scope','approved',1,1)")
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


def test_the_copied_venv_runs_pip_and_pytest_on_the_base_interpreter(project):
    """The batch's `.venv` is a copy of a template (frame 206). A copy that
    named the template's paths would run the template, or nothing."""
    db, _ = project
    lifecycle.start(db, "b1")
    root = worktrees.Path(
        db.execute("SELECT worktree FROM batches WHERE id='b1'").fetchone()["worktree"])
    note = db.execute("SELECT value FROM config WHERE key='env:b1'").fetchone()["value"]
    assert note == "made .venv; installed pytest", note
    py = provision.venv_python(root)
    for argv in (["-m", "pip", "--version"], ["-m", "pytest", "--version"]):
        out = subprocess.run([str(py), *argv], capture_output=True, text=True)
        assert out.returncode == 0, out.stderr
    prefix = subprocess.run([str(py), "-c", "import sys; print(sys.prefix)"],
                            capture_output=True, text=True).stdout.strip()
    assert worktrees.Path(prefix).resolve() == (root / ".venv").resolve(), prefix
    cfg = (root / ".venv" / "pyvenv.cfg").read_text(encoding="utf-8")
    home = next(line.split("=", 1)[1].strip() for line in cfg.splitlines()
                if line.startswith("home"))
    assert worktrees.Path(home).resolve() == worktrees.Path(sys.base_prefix).resolve(), home


def test_a_second_run_on_the_same_root_gets_a_fresh_worktree(project):
    """
    tipsP, 2026-09-09: two runs on one root named their first batch b_1.
    The second's `worktree add` failed on the first's directory, the failure
    was swallowed, and the Developer wrote and committed on master.
    """
    db, repo = project
    lifecycle.start(db, "b1")
    first = db.execute("SELECT worktree FROM batches WHERE id='b1'").fetchone()["worktree"]
    (worktrees.Path(first) / "left_behind.py").write_text("x = 1\n", encoding="utf-8")
    worktrees.commit(first, "the first run's work")
    # The next run: same root, same batch id, no worktree on record.
    db.execute("UPDATE batches SET worktree = NULL, status = 'pending' WHERE id='b1'")
    db.commit()
    lifecycle.start(db, "b1")
    second = db.execute("SELECT worktree FROM batches WHERE id='b1'").fetchone()["worktree"]
    assert second, "the second run has nowhere to work"
    assert not (worktrees.Path(second) / "left_behind.py").exists(), \
        "the second run started from the first run's branch"
    branches = subprocess.run(["git", "-C", str(repo.root), "branch", "--list", "batch/b1*"],
                              capture_output=True, text=True).stdout
    assert "batch/b1@" in branches, "the first run's branch is the record and must survive"


def test_a_batch_with_no_worktree_cannot_be_written_to(project):
    """The fallback to the project root is for reads. A write there is a
    change nobody reviewed on a branch nobody merged."""
    db, repo = project
    db.execute("UPDATE batches SET status = 'running' WHERE id='b1'")
    db.execute("INSERT INTO config (key, value) VALUES ('worktree:b1', 'no git here')")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="batch_start")
    with pytest.raises(ValueError, match="has no worktree \\(no git here\\)"):
        sb.call("code.write", path="new.py", text="def f():\n    return 1\n")
    with pytest.raises(ValueError, match="has no worktree"):
        sb.call("code.commit", message="nothing")
    assert not (repo.root / "new.py").exists()


def test_the_repositorys_own_tests_join_the_batch(project):
    """
    tipsY, 2026-09-09: the batch's tests were green, the Critic passed, and
    the merged program read the tip percentage and ignored it. The repo's
    own tip test was in the tree and never ran. A merge must not break
    what the tree already proved.
    """
    from rota.core import harness

    db, repo = project
    (repo.root / "tests").mkdir(exist_ok=True)
    (repo.root / "tests" / "test_existing.py").write_text(
        "from src.store.records import *\n\ndef test_existing():\n    assert 1 == 2\n",
        encoding="utf-8")
    subprocess.run(["git", "-C", str(repo.root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo.root), "-c", "user.name=t", "-c",
                    "user.email=t@t", "commit", "-qm", "an existing test"], check=True)
    lifecycle.start(db, "b1")
    row = db.execute("SELECT id, criterion_id, path FROM tests WHERE batch_id='b1' "
                     "AND path = 'tests/test_existing.py'").fetchone()
    assert row and row["criterion_id"] is None and row["id"].startswith("inh_")
    results = dict(harness.run(db, "b1"))
    assert results[row["id"]] in ("fail", "error"), "the existing test must run and be red"


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
    # And the item's delivered version is on record, so an amendment after
    # delivery is new work (tipsAH, 2026-09-09).
    assert db.execute("SELECT value FROM config WHERE key='delivered:i1'").fetchone()["value"] == "1"


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


def test_the_note_on_an_empty_commit_names_the_ending(project):
    """
    "Say so and finish" named no ending, and the seat picked the one tool it
    had. ACT-DV-edit-inside-the-function (2026-09-19): the Developer read this
    note, answered that the criteria were met, and sent `msg.challenge_tester`,
    the one message `developer/tests_failing.md` gives the mode. A mode with a
    single message tool reads an unnamed ending as that message.
    """
    db, _ = project
    lifecycle.start(db, "b1")
    sb = build("developer", db, batch_id="b1")

    note = sb.call("code.commit", message="nothing to do")["note"]
    assert "end the session" in note, note
    assert "no message to anybody" in note, note


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


def test_what_critic_sees_is_the_same_twice(project):
    """
    A prompt containing a path can never be replayed.

    `code.read` is pushed into Critic's working set without being asked for, and
    it was returning the batch row alongside the diff — including `worktree`, an
    absolute path, and `head_commit`, a fresh SHA. Both change every run. The
    prompt hash is a sha256 of the whole prompt, so every Critic and Developer
    session hashed differently from the last one, and their recordings could
    never be replayed: eight cases went STALE on every suite run, three of them
    recorded green half an hour earlier.

    That read as "a re-recording owed" for as long as anybody looked at it,
    which is the expensive part — a case that cannot replay is not slow to
    verify, it is unverified, and it says so in the same words as work in
    progress.

    The docstring already claimed this: the batch row "used to" be returned and
    the diff replaced it. The row never left.
    """
    db, _ = project
    lifecycle.start(db, "b1")
    dev = build("developer", db, batch_id="b1")
    dev.call("code.write", path="src/notify/formatting.py", text="# emptied\n")
    out = dev.call("code.commit", message="empty formatting")

    seen = build("critic", db, batch_id="b1").call("code.read")

    tree = db.execute(
        "SELECT worktree FROM batches WHERE id = 'b1'").fetchone()["worktree"]

    # Compared against the values, not a serialisation of them: the first
    # version of this test rendered the result with `json.dumps` and passed,
    # because a Windows path comes back with its separators escaped and the
    # raw string is not a substring of that.
    unstable = {k: v for k, v in seen.items()
                if isinstance(v, str) and (v == tree or v == out["head_commit"])}
    assert not unstable, (
        f"per-run values reach the prompt through code.read: {unstable}. "
        f"The prompt hash is a sha256 of the whole prompt, so this session can "
        f"never replay a recording made by any other.")


# ---------------------------------------------------------------------------
# Frame 97: the batch's diff runs from its fork, and names what it removed
# ---------------------------------------------------------------------------

_WRAP = "def wrap(v):\n    rv = [v]\n    return rv\n"


def _batch_with_wrap(project):
    """The root holds `src/wrap.py` before the batch forks, so the batch can
    remove a line of the project's own."""
    db, repo = project
    (repo.root / "src" / "wrap.py").write_text(_WRAP, encoding="utf-8")
    gitfixture.git(repo.root, "add", "src/wrap.py")
    gitfixture.git(repo.root, "commit", "-q", "-m", "wrap")
    lifecycle.start(db, "b1")
    tree = worktrees.Path(db.execute(
        "SELECT worktree FROM batches WHERE id='b1'").fetchone()["worktree"])
    return db, repo, tree


def _add_unrelated_line(tree):
    """One added line and no removed one, so only `src/wrap.py` can remove."""
    target = tree / "src" / "notify" / "formatting.py"
    target.write_text(target.read_text(encoding="utf-8") + "\nUNRELATED = 1\n",
                      encoding="utf-8")


def test_critic_sees_every_commit_since_the_fork_and_the_removed_line(project):
    """Night 98 (2026-09-29): s183 lost 13 lines to an earlier commit, and
    HEAD~1 hid that commit from every later reader."""
    db, _, tree = _batch_with_wrap(project)
    (tree / "src" / "wrap.py").write_text("def wrap(v):\n    rv = [v]\n", encoding="utf-8")
    worktrees.commit(tree, "drop the return")
    _add_unrelated_line(tree)
    worktrees.commit(tree, "an unrelated change")

    seen = build("critic", db, batch_id="b1").call("code.read")
    assert "-    return rv" in seen["diff"], seen["diff"]
    assert "src/notify/formatting.py" in seen["diff"]
    assert "src/wrap.py" in seen["touched"]
    assert seen["removed lines"] == "src/wrap.py:\n-     return rv", seen


def test_a_moved_line_is_not_a_removed_line(project):
    db, _, tree = _batch_with_wrap(project)
    (tree / "src" / "wrap.py").write_text(
        "def wrap(v):\n    return rv\n    rv = [v]\n", encoding="utf-8")
    worktrees.commit(tree, "move a line")
    _add_unrelated_line(tree)
    worktrees.commit(tree, "an unrelated change")

    seen = build("critic", db, batch_id="b1").call("code.read")
    assert "src/wrap.py" in seen["touched"], "the move is in the batch's diff"
    assert "removed lines" not in seen, seen["removed lines"]


def test_the_developer_diff_is_not_empty_when_the_tree_equals_head_1(project):
    """Night 100 (2026-09-30): bg_2's tidy-up commit added a stray line and
    the next write removed it. Three sessions read `"diff": ""`."""
    db, _, tree = _batch_with_wrap(project)
    (tree / "src" / "wrap.py").write_text("def wrap(v):\n    rv = [v]\n", encoding="utf-8")
    worktrees.commit(tree, "the batch's real change")
    (tree / "src" / "wrap.py").write_text(
        "def wrap(v):\n    rv = [v]\n# stray\n", encoding="utf-8")
    worktrees.commit(tree, "tidy up")
    (tree / "src" / "wrap.py").write_text("def wrap(v):\n    rv = [v]\n", encoding="utf-8")

    out = build("developer", db, batch_id="b1").call("code.diff")
    assert out["diff"], out
    assert "-    return rv" in out["diff"], out["diff"]
    assert "# stray" not in out["diff"]
    assert out["removed lines"] == "src/wrap.py:\n-     return rv", out


def test_a_root_that_moved_on_is_not_the_batch_s_removal(project):
    """The base is the fork, so a later commit on the root never reads as
    a line the batch removed."""
    db, repo, tree = _batch_with_wrap(project)
    fork = gitfixture.git(repo.root, "rev-parse", "HEAD").strip()
    (tree / "src" / "wrap.py").write_text(_WRAP + "\n\ndef unwrap(v):\n    return v[0]\n",
                                          encoding="utf-8")
    worktrees.commit(tree, "add unwrap")
    _add_unrelated_line(tree)
    worktrees.commit(tree, "an unrelated change")
    # The root moves on after the fork: a line the batch never touched goes.
    (repo.root / "src" / "wrap.py").write_text("def wrap(v):\n    return [v]\n", encoding="utf-8")
    gitfixture.git(repo.root, "commit", "-q", "-am", "the root moves on")

    assert worktrees.base(tree, repo.root) == fork
    seen = build("critic", db, batch_id="b1").call("code.read")
    assert "def unwrap" in seen["diff"], "the batch's first commit is in its diff"
    assert "removed lines" not in seen, seen["removed lines"]
    out = build("developer", db, batch_id="b1").call("code.diff")
    assert "def unwrap" in out["diff"] and "removed lines" not in out, out


def test_a_long_removal_leaves_the_diff_in_the_rendered_result(project):
    """The diff review of 4876aae: a dict of removed lines went on the
    runner's head line, 45,415 characters, and the cut showed no diff."""
    from rota.core.runner import _render

    db, repo = project
    big = "".join(f"VALUE_{i:04d} = 'a line long enough to fill the whole diff past sixty thousand characters'\n"
                  for i in range(700))
    (repo.root / "src" / "big.py").write_text(big, encoding="utf-8")
    gitfixture.git(repo.root, "add", "src/big.py")
    gitfixture.git(repo.root, "commit", "-q", "-m", "big")
    lifecycle.start(db, "b1")
    tree = worktrees.Path(db.execute(
        "SELECT worktree FROM batches WHERE id='b1'").fetchone()["worktree"])
    (tree / "src" / "big.py").unlink()
    worktrees.commit(tree, "drop big")

    seen = build("critic", db, batch_id="b1").call("code.read")
    assert len(seen["diff"]) >= 60000, len(seen["diff"])
    removed = seen["removed lines"]
    assert len(removed) <= 2100 and removed.endswith(" more lines"), removed[-200:]
    # The review of a6bed3b: the block after a long diff was cut at both
    # limits, so the removed lines render first.
    for limit in (6000, 20000):
        shown = _render(seen, limit)
        assert "[removed lines]" in shown, (limit, shown[:300])
        assert len(shown.splitlines()[0]) < 1000, shown.splitlines()[0][:300]
    assert "[diff]" in _render(seen, 20000)


_DEDENT_AND_DOUBLE = """diff --git a/src/f.py b/src/f.py
--- a/src/f.py
+++ b/src/f.py
@@ -1,6 +1,4 @@
 def f(x):
-    if x:
-        do()
+    do()
-    y = 1
-    y = 1
+    y = 1
     return x
"""


def test_a_dedent_and_a_double_removal_are_removed_lines():
    """Indentation counts, and one added line answers one removed line."""
    from rota.roles.api import _removed_lines

    assert _removed_lines(_DEDENT_AND_DOUBLE) == (
        "src/f.py:\n-     if x:\n-         do()\n-     y = 1")


def test_a_removed_line_names_its_file_whatever_its_path_or_length():
    """The review of a6bed3b: git ends a header path that holds a space with
    a tab, and one long first line left a tail that named no file."""
    from rota.roles.api import _removed_lines

    spaced = ("diff --git a/src/my file.py b/src/my file.py\n"
              "--- a/src/my file.py\t\n+++ b/src/my file.py\t\n"
              "@@ -1,1 +0,0 @@\n-x = 1\n")
    assert _removed_lines(spaced) == "src/my file.py:\n- x = 1"

    long = ("diff --git a/src/g.py b/src/g.py\n--- a/src/g.py\n+++ b/src/g.py\n"
            "@@ -1,2 +0,0 @@\n-" + "x" * 3000 + "\n-y = 2\n")
    text = _removed_lines(long)
    assert (text.startswith("src/g.py:\n- xxx") and len(text) <= 2100
            and text.endswith("\n... and 1 more line")), text[:40] + text[-40:]


def test_a_batch_with_no_commit_says_so(project):
    db, _ = project
    lifecycle.start(db, "b1")
    seen = build("critic", db, batch_id="b1").call("code.read")
    assert seen["diff"] == "" and seen["note"] == "no commit yet on this batch", seen
    # Frame 106 (2026-10-01): `code.diff` says the same fact. An Architect
    # read a bare empty diff and answered the Developer three times.
    dev = build("developer", db, batch_id="b1")
    diff = dev.call("code.diff")
    assert diff["diff"] == "" and diff["note"] == (
        "this batch has no change since its fork: "
        "no commit and no uncommitted edit"), diff

    dev.call("code.write", path="src/notify/formatting.py", text="# emptied\n")
    # An uncommitted edit is a change, and its own entry names it.
    diff = dev.call("code.diff")
    assert "note" not in diff and diff["not committed"], diff
    dev.call("code.commit", message="empty formatting")
    assert "note" not in build("critic", db, batch_id="b1").call("code.read")
    assert "note" not in dev.call("code.diff")


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

    # The fixture repo's own tests join the batch too (tipsY); this test is
    # about the batch's own test.
    results = [r for r in harness.run(db, "b1") if not r[0].startswith("inh_")]
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
    db.execute("INSERT INTO items (id, text, kind) "
               "VALUES ('i1','x','in_scope')")
    db.execute("INSERT INTO batches (id, item_id) VALUES ('b1','i1')")

    with pytest.raises(worktrees.WorktreeError, match="project_root"):
        worktrees.create(db, "b1")


def test_starting_without_a_root_does_not_touch_any_repository(tmp_path):
    """`lifecycle.start` swallows the error so a batch can still run — but it
    must not have created anything on the way past."""
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind) "
               "VALUES ('i1','x','in_scope')")
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


def test_a_test_run_keeps_what_the_harness_said(project):
    """
    The word `fail` was all that survived, so the role woken to fix a red test
    could read what the test *asserts* and had to guess what red looked like.
    Two L1 cases turn on exactly that judgement — is the code wrong or is the
    test wrong — and answered it in precisely opposite directions, which is the
    right outcome for a question nobody had given them the evidence for.
    """
    from rota.core import harness
    from rota.core.sandbox import build

    db, _ = project
    lifecycle.start(db, "b1")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst1','b1','c1','test_prorate.py',?)",
               ("from src.billing.charges import prorate\n\n"
                "def test_rounds():\n    assert prorate(999, 1, 3) == 12345\n",))
    build("developer", db, batch_id="b1").call("code.commit", message="baseline")

    assert [r for r in harness.run(db, "b1") if not r[0].startswith("inh_")] == [("tst1", "fail")]

    said = db.execute(
        "SELECT output FROM test_runs WHERE test_id='tst1'").fetchone()["output"]
    assert "333" in said and "12345" in said, said

    # And it reaches the role, on the read the mode actually makes.
    loaded = build("developer", db, batch_id="b1").call("tests.load")
    mine = next(r for r in loaded if r["id"] == "tst1")
    assert mine["last_result"] == "fail"
    assert "12345" in mine["said"]


def test_a_red_run_names_the_files_changed_since_it(project):
    """
    Finding 66 (2026-09-14). The 9B wrote the band loop, loaded the tests,
    and read the run from before its write as the present: the fix had
    failed, so it started over, until the verbatim-repeat cut ended it. A
    run is a statement about one commit, and the files changed since are
    a fact of the worktree.
    """
    from rota.core import harness
    from rota.core.sandbox import build

    db, _ = project
    lifecycle.start(db, "b1")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst1','b1','c1','test_prorate.py',?)",
               ("from src.billing.charges import prorate\n\n"
                "def test_rounds():\n    assert prorate(999, 1, 3) == 12345\n",))
    # `code.commit` moves the batch's head when the session lands; a direct
    # sandbox call lands nothing, so the test moves it the way the session
    # would. The harness records a run against that commit.
    wt = db.execute("SELECT worktree FROM batches WHERE id='b1'").fetchone()["worktree"]

    def land_head():
        db.execute("UPDATE batches SET head_commit = ? WHERE id = 'b1'",
                   (worktrees.head(wt),))

    build("developer", db, batch_id="b1").call("code.commit", message="baseline")
    land_head()
    harness.run(db, "b1")

    def load():
        loaded = build("developer", db, batch_id="b1").call("tests.load")
        return next(r for r in loaded if r["id"] == "tst1")

    # Finding 78: where the red run raised, a fact of the output.
    raised = load()["raised at"]
    assert "test_prorate.py" in raised and "the test's own assertion" in raised, raised

    # Nothing changed: the row says nothing about it.
    assert "changed since this run, not run" not in load()

    sb = build("developer", db, batch_id="b1")
    src = sb.call("code.source", path="src/billing/charges.py", start=0, end=400)
    wrote = sb.call("code.write", path="src/billing/charges.py",
                    text=src["text"] + "\n\nCHANGED_SINCE_THE_RUN = True\n", start=0, end=-1)
    # Finding 68: a landed write is not a commit, and both the write's
    # result and the diff say which files wait for one.
    assert wrote["written, not committed"] == ["src/billing/charges.py"]
    assert sb.call("code.diff")["not committed"] == ["src/billing/charges.py"]
    row = load()
    assert "changed since this run, not run" in row, (wrote, row, db.execute(
        "SELECT worktree FROM batches WHERE id='b1'").fetchone()["worktree"], db.execute(
        "SELECT test_id, result, commit_sha FROM test_runs").fetchall())
    assert row["changed since this run, not run"] == ["src/billing/charges.py"]

    # Committed and still not run: the fact stays until the harness runs.
    sb.call("code.commit", message="a change the tests have not seen")
    land_head()
    assert load()["changed since this run, not run"] == ["src/billing/charges.py"]

    harness.run(db, "b1")
    assert "changed since this run, not run" not in load()


def test_a_passing_test_says_nothing(project):
    """Green output is noise in the scarcest context there is."""
    from rota.core import harness
    from rota.core.sandbox import build

    db, _ = project
    lifecycle.start(db, "b1")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst1','b1','c1','test_prorate.py',?)",
               ("from src.billing.charges import prorate\n\n"
                "def test_rounds():\n    assert prorate(999, 1, 3) == 333\n",))
    build("developer", db, batch_id="b1").call("code.commit", message="baseline")
    harness.run(db, "b1")

    loaded = build("developer", db, batch_id="b1").call("tests.load")
    assert loaded[0]["last_result"] == "pass" and loaded[0]["said"] is None


def test_the_batch_own_tests_come_first_and_green_inherited_bodies_stay_out(project):
    """
    Night 103, s170: 34 inherited bodies, 460,000 characters, came before
    the batch's own three tests, and the push cap cut the own tests off.
    The frame 101 rule puts the own tests first and leaves out green
    inherited bodies.
    """
    db, _ = project
    lifecycle.start(db, "b1")
    big = "x" * 10_000
    for i in range(30):
        db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                   "VALUES (?, 'b1', NULL, ?, ?)", (f"f101_g{i:02d}", f"tests/test_g{i}.py", big))
        db.execute("INSERT INTO test_runs (id, batch_id, test_id, result, output) "
                   "VALUES (?, 'b1', ?, 'pass', '')", (f"f101_rg{i:02d}", f"f101_g{i:02d}"))
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('f101_red', 'b1', NULL, 'tests/test_red.py', 'def test_red(): RED_BODY')")
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, result, output) "
               "VALUES ('f101_rr', 'b1', 'f101_red', 'fail', 'assert 1 == 2')")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('f101_own', 'b1', 'c1', 'test_own.py', 'def test_own(): OWN_BODY')")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('f101_norun', 'b1', NULL, 'tests/test_norun.py', 'def test_n(): NORUN')")
    db.commit()

    loaded = build("critic", db, batch_id="b1").call("tests.load")
    assert loaded[0]["id"] == "f101_own"
    assert loaded[0]["body"] == "def test_own(): OWN_BODY"
    red = next(r for r in loaded if r["id"] == "f101_red")
    assert red["body"] == "def test_red(): RED_BODY"
    green = [r for r in loaded if r["id"].startswith("f101_g")]
    assert len(green) == 30
    for r in green:
        assert r["body"] == "10000 characters, passing, not shown", r["body"]
    norun = next(r for r in loaded if r["id"] == "f101_norun")
    assert norun["body"] == f"{len('def test_n(): NORUN')} characters, not run yet, not shown"
    # The Critic has no read for a file path, so no hidden body points at one.
    assert not any("the file is at" in (r["body"] or "") for r in loaded)


def test_a_finding_names_a_file_the_diff_changed(project):
    """
    Night 65 (2026-09-14): the structural review filed violated findings on
    two test files the batch's diff never touched. The Developer read them,
    found nothing to fix, and looped. The changed files are a fact of the
    worktree, so the finding's grain is checked against them.
    """
    db, _ = project
    lifecycle.start(db, "b1")
    db.execute("INSERT INTO constraints (id, headline) VALUES ('k1','charges stay')")
    db.commit()
    sb = build("developer", db, batch_id="b1")
    src = sb.call("code.source", path="src/billing/charges.py", start=0, end=400)
    sb.call("code.write", path="src/billing/charges.py", text=src["text"] + "# touched" + chr(10), start=0, end=-1)
    # The batch's own materialised test file is furniture, not the diff.
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
               "('tst1','b1','c1','tests/test_prorate.py','def test_x(): assert 1')")
    db.commit()
    from rota.core import harness
    harness.run(db, "b1")
    arch = build("architect", db, batch_id="b1")
    with pytest.raises(ValueError, match="does not touch"):
        arch.call("findings.find", id="f1", batch_id="b1", constraint_id="k1",
                  status="violated", grain="tests/test_charges.py")
    with pytest.raises(ValueError, match="does not touch"):
        arch.call("findings.find", id="f1", batch_id="b1", constraint_id="k1",
                  status="violated", grain="tests/test_prorate.py")
    out = arch.call("findings.find", id="f1", batch_id="b1", constraint_id="k1",
                    status="violated", grain="src/billing/charges.py::total_of")
    assert out["status"] == "violated"

def test_the_drops_refusal_names_the_insert_at_top_span(project):
    """
    Finding 74, nights 70 and 71: the 9B sent `import sys` as a whole-file
    write of a 623-line module, five times. The refusal named the append
    span and not the insert-at-top span an import needs.
    """
    db, _ = project
    lifecycle.start(db, "b1")
    sb = build("developer", db, batch_id="b1")
    with pytest.raises(ValueError, match="start=0, end=0"):
        sb.call("code.write", path="src/billing/charges.py", text="import sys", start=0, end=-1)
