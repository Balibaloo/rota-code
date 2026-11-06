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
# The claimed line of the false claim design, Revision R3 item 1.
CLAIMED_LINE = "no code changed. The team says the code already does this."

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
    # The gate now waits on the Tester, the next step of the claim (review
    # p1, F4).
    assert lifecycle.mergeable(db, "b_2") == "criteria without a test: c_10, c_5"


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


# ---------------------------------------------------------------------------
# Pass 1b: the findings of review p1 (plans/f360-review-p1.md)
# ---------------------------------------------------------------------------

# The fixture's `formatting.py` with one line inside `plural` changed, as in
# `test_developer.py`, so the commit drops nothing.
REWRITTEN = '''ELLIPSIS = chr(8230)


def truncate(text, limit=72):
    return text if len(text) <= limit else text[: limit - 1] + ELLIPSIS


def plural(count, singular, plural_form=None):
    if count == 1:
        return "1 " + singular
    return f"{count} {plural_form or singular + 's'}"
'''


def test_the_shift_page_does_not_call_a_claim_built(project):
    """F1: before the merge, the shift page said "The change b1 is built"
    for a claim. The ruling puts "No code changed" in front of the seat."""
    from rota.roles.principal import _shift_where

    db, _ = project
    sb = build("developer", db, batch_id="b1")
    sb.call("code.commit", message="the criteria are met")
    _land(db, sb)

    said = _shift_where(db, "i1")

    assert "built" not in said, said
    assert "no code" in said.lower(), said
    assert "tests check the claim" in said, said


def test_a_refused_test_write_does_not_block_the_claim(project):
    """F2: a write to a test file that the parse door refuses carries other
    words than the test-file refusal. The path decides the side, so the
    session still claims."""
    db, _ = project
    sb = build("developer", db, batch_id="b1")
    with pytest.raises(ValueError):
        sb.call("code.write", path="tests/test_formatting.py",
                text="def test_x(: pass")
    assert sb.ctx.refusals and "test file" not in sb.ctx.refusals[-1][1]

    out = sb.call("code.commit", message="the criteria are met")

    assert CLAIM_NOTE in out["note"], out
    assert len(_heads(sb)) == 1


def test_a_real_commit_after_a_claim_clears_the_mark(project):
    """F7: the claim went red and the Developer changed the code. The batch
    is a change now, so the mark goes."""
    db, _ = project
    sb = build("developer", db, batch_id="b1")
    sb.call("code.commit", message="the criteria are met")
    _land(db, sb, sid="s_claim")
    assert db.execute("SELECT claimed_head FROM batches WHERE id = 'b1'"
                      ).fetchone()[0]

    sb = build("developer", db, batch_id="b1")
    sb.call("code.write", path="src/notify/formatting.py", text=REWRITTEN)
    out = sb.call("code.commit", message="the change")
    assert out["committed"] is True
    _land(db, sb, sid="s_change")

    row = db.execute("SELECT head_commit, claimed_head FROM batches "
                     "WHERE id = 'b1'").fetchone()
    assert row["head_commit"] == out["head_commit"]
    assert row["claimed_head"] is None


def test_the_notes_tail_does_not_join_the_claimed_line(tmp_path):
    """F3: the notes tail appended to the claimed line read "These tests
    ... They carry". The claimed line stands as its own line."""
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind) VALUES ('i1','x','in_scope')")
    db.execute("INSERT INTO batches (id, item_id, status, head_commit, "
               "claimed_head) VALUES ('b1', 'i1', 'merged', 'bbb', 'bbb')")
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, "
               "status, author) VALUES ('l1', 'i1', 'items', 'the team chose', "
               "'parked', 'developer')")
    db.commit()

    lines = render_state(db).splitlines()

    claimed = [line for line in lines if CLAIMED_LINE in line]
    assert claimed and "carries" not in claimed[0], lines
    assert any("carries 1 choice" in line for line in lines), lines


def test_a_boot_reconcile_keeps_the_claim_over_its_tests_commit(world):
    """F6: the merge commits the tests in the worktree, a conflict defers
    the batch, and the boot then writes that commit as the head. The tests
    commit changes no code, so the claim moves with the head."""
    from rota.core.boot import reconcile_worktrees

    db, repo, tree = world
    sb = build("developer", db, batch_id="b1")
    sb.call("code.commit", message="the criteria are met")
    _land(db, sb)
    db.execute("INSERT INTO tests (id, batch_id, path, body) VALUES "
               "('tst1','b1','tests/test_probe_f360.py','def test_x(): pass')")
    db.execute("UPDATE batches SET status = 'deferred' WHERE id = 'b1'")
    db.commit()
    repo.edit(tree, "tests/test_probe_f360.py", "def test_x(): pass\n")
    tests_commit = repo.commit_in(tree, "rota: tests of b1")

    reconcile_worktrees(db)

    row = db.execute("SELECT head_commit, claimed_head FROM batches "
                     "WHERE id = 'b1'").fetchone()
    assert row["head_commit"] == tests_commit
    assert row["claimed_head"] == tests_commit


# ---------------------------------------------------------------------------
# Slice 1 of the false claim design: the Tester's tests decide a claim
# (plans/design-false-claim-2026-11-06.md, Revision R2 F and R4)
# ---------------------------------------------------------------------------

# The words of the design, R2 F, to the letter.
CLAIM_DETAIL = ("No code changed on this batch. The Developer claims that the "
                "code as it is already meets each criterion. Your tests decide "
                "the claim.")
S153_BATCH = "fold_long_lines_in_icalendar_batch"
S153_FORK = "99619246f9c685ff407ab2559a12c18f6dbec9de"


def _tester_detail(db, bid):
    wakes = [w for w in predicates.tests_missing(db) if w.refs == (bid,)]
    assert len(wakes) == 1, wakes
    return wakes[0].detail


@pytest.fixture
def s153_rows(tmp_path):
    """The rows of dry6b.db at the wake of s153: the claimed batch is
    running, its head is the fork, and c1 to c3 have no test yet. The probe
    of the report reads the same wake from a copy of dry6b.db itself."""
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('folds_long_lines_in_icalendar','fold a long "
               "line at a space','in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('t1','folds_long_lines_in_icalendar','fold at a space')")
    for cid in ("c1", "c2", "c3"):
        db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?, 't1', ?)",
                   (cid, f"criterion {cid}"))
    db.execute("INSERT INTO batches (id, item_id, status, head_commit, "
               "claimed_head) VALUES (?, 'folds_long_lines_in_icalendar', "
               "'running', ?, ?)", (S153_BATCH, S153_FORK, S153_FORK))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES (?, 't1')",
               (S153_BATCH,))
    db.commit()
    yield db
    db.close()


def test_the_wake_of_s153_carries_the_claim(s153_rows):
    """R4 control 4: s153 read only "without a test: c1, c2, c3" and wrote
    three tests that pass on the code as it was (the read, section 1)."""
    detail = _tester_detail(s153_rows, S153_BATCH)

    assert detail.splitlines()[0] == "without a test: c1, c2, c3", detail
    assert CLAIM_DETAIL in detail, detail


def test_a_change_batch_gets_no_claim_detail(s153_rows):
    """A real commit is a change, and so is a claim that a later commit
    replaced (review p1, F7). Neither wake says that no code changed."""
    db = s153_rows
    for claim in (None, "an_older_head"):
        db.execute("UPDATE batches SET claimed_head = ? WHERE id = ?",
                   (claim, S153_BATCH))
        db.commit()

        detail = _tester_detail(db, S153_BATCH)

        assert detail == "without a test: c1, c2, c3", detail
        assert "claim" not in detail


def _claim_in_world(db):
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c1','t1','plural(2, \"cat\") returns \"2 cats\"')")
    db.commit()
    sb = build("developer", db, batch_id="b1")
    sb.call("code.commit", message="the criteria are met")
    _land(db, sb, sid="s_claim")
    assert CLAIM_DETAIL in _tester_detail(db, "b1")


def _encode(db, body):
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst1','b1','c1','tests/test_probe_f360.py', ?)", (body,))
    db.commit()


def test_a_red_test_disproves_a_claim_and_the_batch_runs_the_loop(world):
    """R4 control 5: a criterion test red at the fork wakes the Developer
    on `tests_failing`. A real commit then ends the claim, and the merge
    shows the Done line and no claimed line."""
    db, repo, tree = world
    base = repo.head()
    _claim_in_world(db)
    _encode(db, "def test_x():\n    assert False\n")
    lifecycle.record_test_run(db, "r1", "b1", "tst1", "fail", commit_sha=base)
    db.commit()

    woken = [w for w in predicates.tests_failing(db) if w.refs == ("b1",)]
    assert [(w.role, w.kind) for w in woken] == [("developer", "tick:tests_failing")]

    sb = build("developer", db, batch_id="b1")
    sb.call("code.write", path="src/notify/formatting.py", text=REWRITTEN)
    out = sb.call("code.commit", message="the change")
    assert out["committed"] is True, out
    session_commit(db, SessionResult(
        session_id="s_change", role="developer", wake_kind="tick:tests_failing",
        wake_refs=("b1",), writes=[_as_write(w) for w in sb.ctx.writes]))
    db.commit()
    row = db.execute("SELECT head_commit, claimed_head FROM batches "
                     "WHERE id = 'b1'").fetchone()
    assert row["head_commit"] == out["head_commit"]
    assert row["claimed_head"] is None
    assert ("b1",) in [w.refs for w in predicates.harness(db)]

    lifecycle.record_test_run(db, "r2", "b1", "tst1", "pass",
                              commit_sha=out["head_commit"])
    db.commit()
    assert [w for w in predicates.tests_failing(db) if w.refs == ("b1",)] == []
    lifecycle.merge(db, "b1")

    page = render_state(db)
    assert "Done: 1 change built, tested and merged." in page, page
    assert CLAIMED_LINE not in page, page


def test_a_true_claim_whose_tests_pass_merges_as_before(world):
    db, repo, tree = world
    base = repo.head()
    _claim_in_world(db)
    _encode(db, "def test_x():\n    assert True\n")
    lifecycle.record_test_run(db, "r1", "b1", "tst1", "pass", commit_sha=base)
    db.commit()

    assert [w for w in predicates.tests_failing(db) if w.refs == ("b1",)] == []
    lifecycle.merge(db, "b1")

    assert db.execute("SELECT status FROM batches WHERE id = 'b1'"
                      ).fetchone()[0] == "merged"
    assert CLAIMED_LINE in render_state(db)


# ---------------------------------------------------------------------------
# Pass 2: the review of 8d384ed6 (plans/f360-claim-review-2026-11-06.md),
# the ruling of 2026-11-06 and the lines that the principal reads
# ---------------------------------------------------------------------------

CRITIC_CLAIM = ("No code changed on this batch. The Developer claims the "
                "criteria are met. The tests are the only evidence.")
NL = chr(10)
RED_BODY = ("from src.notify.formatting import plural" + NL + NL
            + "def test_plural_two():" + NL
            + "    assert plural(2, 'cat') == '2 cats!'" + NL)


def _tools(mode):
    text = Path(f"rota/roles/prompts/{mode}.tools").read_text(encoding="utf-8")
    return [ln.strip() for ln in text.splitlines()
            if ln.strip() and not ln.startswith("#")]


def _red_at_fork(db, repo):
    """A claim with one criterion test `tst1` red at the fork."""
    _claim_in_world(db)
    _encode(db, RED_BODY)
    lifecycle.record_test_run(db, "r1", "b1", "tst1", "fail",
                              commit_sha=repo.head())
    db.commit()


def test_the_encode_note_on_a_claim_says_no_code_changed(world):
    """Review finding 1: the note said "The batch's head holds the
    Developer's commit" on a claim, and it asked for a re-encode."""
    db, repo, tree = world
    _claim_in_world(db)
    tb = build("tester", db, batch_id="b1", allow=_tools("tester/tests_missing"))
    tb.call("tests.triage", criterion_id="c1", verdict="encodable")

    out = tb.call("tests.encode", id="tst_c1", criterion_id="c1",
                  path="tests/test_plural_claim.py", body=RED_BODY)

    said = " ".join(out.get("notes") or [out.get("note") or ""])
    assert "Developer's commit" not in said, out
    assert "No code changed on this batch" in said, out
    assert "goes to the Developer" in said, out


def test_a_replace_of_the_red_test_of_a_claim_names_the_claim(world):
    """Review finding 2: a same-id encode from the challenge mode replaced
    the red test with no word. The first replace names the claim."""
    db, repo, tree = world
    _red_at_fork(db, repo)
    tb = build("tester", db, batch_id="b1", allow=_tools("tester/challenge"))
    green = RED_BODY.replace("'2 cats!'", "'2 cats'")

    with pytest.raises(ValueError, match="no code changed on this batch"):
        tb.call("tests.encode", id="tst1", criterion_id="c1",
                path="tests/test_probe_f360.py", body=green)
    # Second look, S2: a second send replaced the red test, and the claim
    # merged with no word of the red run. The test stands on every try.
    with pytest.raises(ValueError, match="The test stands"):
        tb.call("tests.encode", id="tst1", criterion_id="c1",
                path="tests/test_probe_f360.py", body=green)


def test_a_challenge_by_the_developer_lets_the_tester_replace_the_red_test(world):
    """Second look, S2: only a challenge of the test by the Developer opens
    the replace. The Critic then reads that a red test was replaced."""
    from rota.roles.api import critic_claim_note

    db, repo, tree = world
    _red_at_fork(db, repo)
    db.execute("INSERT INTO messages (id, thread_id, seq, from_role, to_role, "
               "verb, body_refs, body_text, status) VALUES ('m_ch', 'th_ch', 50, "
               "'developer', 'tester', 'challenge', '[\"tst1\", \"c1\"]', "
               "'the test asks for 2 cats!', 'open')")
    db.commit()
    tb = build("tester", db, batch_id="b1", allow=_tools("tester/challenge"))
    tb.ctx.trigger = "m_ch"
    green = RED_BODY.replace("'2 cats!'", "'2 cats'")

    out = tb.call("tests.encode", id="tst1", criterion_id="c1",
                  path="tests/test_probe_f360.py", body=green)
    assert out.get("id") == "tst1", out
    session_commit(db, SessionResult(
        session_id="s_tst", role="tester", wake_kind="message",
        wake_refs=("b1",), writes=[_as_write(w) for w in tb.ctx.writes]))
    lifecycle.record_test_run(db, "r2", "b1", "tst1", "pass",
                              commit_sha=repo.head())
    db.commit()

    assert critic_claim_note(db, "b1") == (
        CRITIC_CLAIM + " A test of this batch failed on the code as it is, "
        "and the Tester replaced it.")
    assert build("critic", db, batch_id="b1").call("code.read")["note"]         == critic_claim_note(db, "b1")


@pytest.mark.parametrize("role,words", [("tester", CLAIM_DETAIL),
                                        ("critic", CRITIC_CLAIM)])
def test_every_wake_of_a_claimed_batch_says_the_claim(world, role, words):
    """Review finding 2 and item 6: the `challenge` and `answer` wakes of
    the Tester and the review wake of the Critic say the claim."""
    from rota.core.runner import build_prompt
    from rota.core.scheduler import Wake

    db, repo, tree = world
    _claim_in_world(db)
    sb = build(role, db, batch_id="b1")
    kinds = ([("message", "challenge"), ("message", "answer")] if role == "tester"
             else [("tick:review", "")])
    for kind, detail in kinds:
        wake = Wake(role, kind, refs=("b1",), detail=detail)
        _, user = build_prompt(role, sb, wake, {}, "")
        assert user.count(words) == 1, user
    db.execute("UPDATE batches SET claimed_head = NULL WHERE id = 'b1'")
    _, user = build_prompt(role, sb, Wake(role, kinds[0][0], refs=("b1",),
                                          detail=kinds[0][1]), {}, "")
    assert words not in user, user


def test_the_critic_reads_the_claim_in_the_code_read(world):
    """Item 6: s154 read "no commit yet on this batch" on a claim."""
    db, repo, tree = world
    _claim_in_world(db)
    cb = build("critic", db, batch_id="b1")

    out = cb.call("code.read")

    assert out["note"] == CRITIC_CLAIM, out


def test_a_pass_on_a_claim_comes_from_its_own_session(world):
    """Item 6: a Critic session of another batch was not shown the claim,
    so its pass on the claimed batch is refused."""
    db, repo, tree = world
    _claim_in_world(db)
    cb = build("critic", db, batch_id="b_other")

    with pytest.raises(ValueError, match="holds a claim"):
        cb.call("verdicts.emit", batch_id="b1", result="pass")


def test_a_second_claim_against_a_red_test_is_not_a_claim(world):
    """Review finding 3: the note said "If the criteria are already met,
    say so". The wake then repeats with the same key until the dispatch
    count reaches `tick_attempt_cap`, and the key is quarantined."""
    from rota.core import config
    from rota.core.scheduler import note_dispatch, quarantine_overrun, tick_key

    db, repo, tree = world
    _red_at_fork(db, repo)
    sb = build("developer", db, batch_id="b1")

    out = sb.call("code.commit", message="the criteria are met")

    assert out["committed"] is False, out
    assert "If the criteria are already met" not in out["note"], out
    assert "tst1 fails on the code as it is" in out["note"], out
    assert "not a claim" in out["note"], out
    assert _heads(sb) == []
    wake = next(w for w in predicates.tests_failing(db) if w.refs == ("b1",))
    for _ in range(config.get(db, "tick_attempt_cap")):
        note_dispatch(db, wake)
    assert quarantine_overrun(db) == 1
    assert db.execute("SELECT quarantined FROM tick_attempts WHERE tick_key = ?",
                      (tick_key(wake),)).fetchone()[0] == 1


def _ready_claim(db, repo):
    """A claimed batch at the merge gate: its test passes at the fork, and
    the Critic passed it there."""
    _claim_in_world(db)
    _encode(db, "def test_x():\n    assert True\n")
    head = repo.head()
    lifecycle.record_test_run(db, "r1", "b1", "tst1", "pass", commit_sha=head)
    db.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result) "
               "VALUES (?, 'b1', ?, 'pass')", (f"critic:b1:{head}", head))
    # The world has no constraints, so the Architect's one finding is on
    # the zero constraint that onboarding writes.
    from rota.onboarding.boot import ZERO
    db.execute("INSERT INTO findings (id, batch_id, commit_sha, constraint_id, "
               "status, grain) VALUES ('f1', 'b1', ?, ?, 'satisfied', 'b1')",
               (head, ZERO))
    db.commit()


def test_a_claim_waits_on_the_review_setting_as_every_batch_does(world):
    """Item 7, the ruling of 2026-11-06: a claim closes by itself only when
    `merge_gate` is `auto`."""
    db, repo, tree = world
    _ready_claim(db, repo)
    assert lifecycle.mergeable(db, "b1") is None

    db.execute("INSERT OR REPLACE INTO config (key, value) "
               "VALUES ('merge_gate', '\"review\"')")
    db.commit()

    assert lifecycle.mergeable(db, "b1") == "waiting on the principal's review"


# The refs of the real touch note m31 of dry6b.db, with the ids of this
# world: the batch, the item, the criteria and two readings (second look,
# S1).
M31_REFS = '["b1", "i1", "c1", "reading:m5", "reading:m27"]'


def _merged_claim_with_touch_note(db, repo):
    _ready_claim(db, repo)
    db.execute("UPDATE items SET text = 'keep plural as before' WHERE id = 'i1'")
    db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) "
               "VALUES ('b1', 'src/notify/formatting.py', 'path')")
    db.execute("INSERT INTO messages (id, thread_id, seq, from_role, to_role, "
               "verb, body_refs, status) VALUES ('m31', 'th31', 31, 'liaison', "
               "'principal', 'present', ?, 'open')", (M31_REFS,))
    db.commit()
    lifecycle.merge(db, "b1")


def test_the_state_after_a_claimed_merge(world):
    """R4 control 1: no "Waiting on you.", the touch line and the claimed
    line. Before, the touch note m31 hid every other line."""
    db, repo, tree = world
    _merged_claim_with_touch_note(db, repo)

    page = render_state(db)
    print(page)

    assert "Waiting on you." not in page, page
    assert page.splitlines() == [
        "keep plural as before: no code changed. The team says the code "
        "already does this. The only evidence is 1 test that the team wrote, "
        "and it passes on the code as it was. The reviewer passed it. Ask me "
        "to show it.",
        "The plan for keep plural as before reached you after its merge. Ask "
        "me to show it."], page
    # Second look, S3: the merge discharges the note, and a ledger row
    # says why. The loop does not wait on him for it.
    from rota.core.loop import _why_idle

    assert db.execute("SELECT status FROM messages WHERE id = 'm31'"
                      ).fetchone()[0] == "answered"
    assert db.execute("SELECT COUNT(*) FROM ledger WHERE status = 'resolved' "
                      "AND default_taken LIKE '%m31%'").fetchone()[0] == 1
    assert "waiting on the principal" not in _why_idle(db)


def test_a_touch_note_left_open_by_an_older_merge_asks_nothing(world):
    """Second look, S1 and S3: dry6b.db merged before the discharge, so
    m31 is still open there. No reader that the principal or the loop
    reads counts it as an ask."""
    from rota.core.loop import _why_idle
    from rota.roles.principal import pending_asks

    db, repo, tree = world
    _merged_claim_with_touch_note(db, repo)
    db.execute("UPDATE messages SET status = 'open' WHERE id = 'm31'")
    db.execute("DELETE FROM ledger WHERE default_taken LIKE '%m31%'")
    db.commit()

    assert pending_asks(db) == []
    assert "waiting on the principal" not in _why_idle(db)
    page = render_state(db)
    assert "Waiting on you." not in page, page
    assert page.count("reached you after its merge") == 1, page


def test_the_claimed_line_shows_once_under_a_waiting_ask(world):
    """R4 control 2: one more open ask to him. The state shows the ask,
    then the claimed line once."""
    db, repo, tree = world
    _merged_claim_with_touch_note(db, repo)
    db.execute("INSERT INTO messages (id, thread_id, seq, from_role, to_role, "
               "verb, body_refs, body_text, status) VALUES ('m40', 'th40', 40, "
               "'liaison', 'principal', 'question', '[]', "
               "'Which file holds the tips?', 'open')")
    db.commit()

    page = render_state(db)
    print(page)

    # The touch note about merged work is no ask. The question is the one.
    from rota.roles.principal import pending_asks

    asks = pending_asks(db)
    assert [a.message_id for a in asks] == ["m40"], asks
    head = "Waiting on you." + NL + asks[0].rendered + NL
    assert page.startswith(head), page
    assert page.count(CLAIMED_LINE) == 1, page
    assert CLAIMED_LINE in page[len(head):], page
    assert "reached you after its merge" not in page, page


def test_a_claimed_line_drops_what_the_rows_do_not_show(tmp_path):
    """Item 8: each sentence is true in every state that shows the line. A
    merge with no run and no verdict keeps only the first two sentences. A request
    that ends with a full stop gives no ".:" (second look, on dry6b.db)."""
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind) VALUES ('i1','x.','in_scope')")
    db.execute("INSERT INTO batches (id, item_id, status, head_commit, "
               "claimed_head) VALUES ('b1', 'i1', 'merged', 'bbb', 'bbb')")
    db.commit()

    assert render_state(db).splitlines() == [
        "x: no code changed. The team says the code already does this."]
