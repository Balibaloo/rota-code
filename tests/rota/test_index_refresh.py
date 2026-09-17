"""
The code index after a commit (frame 33, finding 42).

click night 46, session 155: a Developer probed for `echo_json`, a symbol its
own batch had committed, and got nothing. The index was built once at
onboarding and nothing after a commit touched it.

Two trees, two contracts. Between the commit and the merge the index describes
the batch's worktree, and the area hashes do not move, so the batch's own work
reopens no survey. When the batch stops running the index describes main again
and each touched area reopens once.
"""
import pytest

from rota.core import lifecycle, runner
from rota.core.db import SessionResult, init_db
from rota.core.sandbox import build as build_sandbox
from rota.core.scheduler import tick_survey
from rota.onboarding import boot, indexer
from rota.roles import prompts
from rota.roles.api import area_content_hash
from rota.testkit import gitfixture

NEW_FILE = "src/echo/json_echo.py"
NEW_BODY = "import json\n\n\ndef echo_json(obj):\n    print(json.dumps(obj))\n"
SURVEY_ROLES = ("terminologist", "architect", "vision_keeper")


@pytest.fixture
def world(tmp_path):
    """An onboarded sample project, one running batch, one worktree."""
    db = init_db(tmp_path / "rota.db")
    repo = gitfixture.make(tmp_path, name="index_refresh")
    boot.onboard(db, repo.root)            # writes project_root and the index
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i1','echo json','in_scope','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('t1','i1','print the object as json')")
    tree = repo.worktree("b1")
    db.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES "
               "('b1','i1','running',?)", (str(tree),))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
               "('b1','t1')")
    db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) VALUES "
               "('b1','src/auth','path')")
    db.commit()
    yield db, repo, tree
    gitfixture.cleanup(repo)


def _commit_the_new_function(db):
    """One Developer session: write the file, commit it, land the session."""
    sb = build_sandbox("developer", db, batch_id="b1", mode="batch_start",
                       allow=prompts.mode_tools("developer", "batch_start"))
    sb.call("code.write", path=NEW_FILE, text=NEW_BODY)
    out = sb.call("code.commit", message="echo_json")
    assert out["committed"], out
    result = SessionResult(session_id="s1", role="developer",
                           writes=[runner._as_write(w) for w in sb.ctx.writes])
    runner.after_landing(db, result)
    return out


def _probe(db, pattern, **kwargs):
    sb = build_sandbox("developer", db, mode="tests_failing",
                       allow=prompts.mode_tools("developer", "tests_failing"),
                       **kwargs)
    return sb.call("code.probe", pattern=pattern)


def _close_every_area(db):
    """A survey record per area per role, stamped at the tree as it stands."""
    from rota.core import config

    config.set(db, "onboarding_phases", "survey")
    areas = [r["area"] for r in db.execute(
        "SELECT DISTINCT area FROM code_index WHERE area IS NOT NULL "
        "AND area != ''")]
    for area in areas:
        for role in SURVEY_ROLES:
            db.execute("INSERT OR REPLACE INTO survey_records "
                       "(id, area, outcome, area_hash) VALUES (?,?,'none_found',?)",
                       (f"{role}:{area}", area, area_content_hash(db, area)))
    db.commit()
    assert tick_survey(db) == [], "the world starts closed"
    return areas


def test_the_batch_sees_the_symbol_it_committed(world):
    """Finding 42. The probe that returned nothing now returns the grain."""
    db, repo, tree = world
    assert not _probe(db, "echo_json", batch_id="b1"), \
        "the index describes main, which has no echo_json yet"

    _commit_the_new_function(db)

    grains = {r["grain"] for r in _probe(db, "echo_json", batch_id="b1")}
    assert f"{NEW_FILE}::echo_json" in grains, \
        "the symbol the batch committed is in the index it reads"
    row = db.execute("SELECT sym_kind, area FROM code_index WHERE grain = ?",
                     (f"{NEW_FILE}::echo_json",)).fetchone()
    assert row["sym_kind"] == "function"
    assert row["area"], "a new grain carries an area, or no area-scoped read sees it"

    from rota.roles.principal import near_code

    assert NEW_FILE in near_code(db, "echo the json of an object"), \
        "the signoff page's prediction reads the same index"

    # The directory the batch made is now a directory the tree has, so the
    # Architect can predict a second file beside the first.
    sb = build_sandbox("architect", db, mode="annotate", batch_id="b1",
                       allow=prompts.mode_tools("architect", "annotate"))
    out = sb.call("batches.annotate", batch_id="b1",
                  paths=["src/echo/json_echo.py", "src/echo/second.py"])
    assert out["grains"] == 2


def test_after_the_merge_the_index_describes_main(world):
    """The batch is over. Every session reads main, at main's new head."""
    db, repo, tree = world
    _commit_the_new_function(db)
    lifecycle.merge(db, "b1")

    grains = {r["grain"] for r in _probe(db, "echo_json")}
    assert f"{NEW_FILE}::echo_json" in grains, \
        "the merged symbol is in the index a session with no batch reads"
    at = db.execute("SELECT value FROM config WHERE key = 'project_commit'"
                    ).fetchone()["value"]
    assert at == repo.head(), "the index names the commit main now carries"


def test_the_batchs_own_commit_reopens_nothing_and_the_merge_reopens_once(world):
    """Loop 5's rule, against a batch's own work.

    A Developer commit moves the worktree, not main, and a survey that has
    seen main is still current. The merge is what moves main, and it reopens
    the areas it moved -- once, not once per commit the batch made.
    """
    db, repo, tree = world
    _close_every_area(db)
    before = dict(db.execute("SELECT area, hash FROM area_hashes").fetchall())

    _commit_the_new_function(db)

    assert dict(db.execute("SELECT area, hash FROM area_hashes").fetchall()) \
        == before, "a batch's commit does not restamp main"
    assert [w for w in tick_survey(db)] == [], \
        "no survey reopens for work that has not landed on main"

    lifecycle.merge(db, "b1")

    reopened = {w.refs[0] for w in tick_survey(db)}
    assert reopened, "the merge moved main, so the areas it moved come back"
    touched = db.execute("SELECT area FROM code_index WHERE grain = ?",
                         (NEW_FILE,)).fetchone()["area"]
    assert reopened == {touched}, "and only the area the merge moved"


def test_an_abandoned_batch_leaves_the_index_at_main(world):
    """The worktree survives the abandonment; the index must not follow it."""
    db, repo, tree = world
    _commit_the_new_function(db)
    assert _probe(db, "echo_json", batch_id="b1"), "the batch's tree is indexed"

    lifecycle.abandon(db, "b1")

    assert _probe(db, "echo_json") == [], \
        "an abandoned batch's symbols are not in main and not in the index"
    assert db.execute("SELECT 1 FROM code_index WHERE grain = ?",
                      (NEW_FILE,)).fetchone() is None


def test_a_worktree_walks_as_its_own_root(world):
    """`.rota` is skipped inside a root, not above it.

    The skip tested the absolute path, so every file of a worktree at
    `<project>/.rota/worktrees/<batch>` was skipped and the walk returned
    nothing. A refresh of one would have emptied the index.
    """
    db, repo, tree = world
    inside = indexer.walk(tree)
    assert inside, "a worktree walked as its own root lists its files"
    assert all(".rota" not in p.relative_to(tree).parts for p in inside)

    outside = {p.relative_to(repo.root).as_posix() for p in indexer.walk(repo.root)}
    assert outside, "the project still walks"
    assert not [p for p in outside if p.startswith(".rota/")], \
        "the state directory stays out of the project's own index"


def test_a_refresh_that_cannot_read_the_tree_keeps_the_old_index(world, tmp_path):
    """The swap deletes first, so a refusal has to come before it."""
    db, repo, tree = world
    before = {r["grain"] for r in db.execute("SELECT grain FROM code_index")}

    with pytest.raises(indexer.IndexRefreshError):
        indexer.refresh(db, tmp_path / "gone", main=False)
    assert {r["grain"] for r in db.execute("SELECT grain FROM code_index")} \
        == before, "a missing tree leaves the index whole"

    # A root git lists files for, whose walk returns none: everything it holds
    # is under a skipped directory name.
    hidden = tmp_path / "hidden"
    (hidden / "dist").mkdir(parents=True)
    (hidden / "dist" / "app.py").write_text("def main():\n    pass\n",
                                            encoding="utf-8")
    gitfixture.git(hidden, "init", "-q", ".")
    gitfixture.git(hidden, "add", "-A")
    gitfixture.git(hidden, "commit", "-q", "-m", "only generated files")
    with pytest.raises(indexer.IndexRefreshError):
        indexer.refresh(db, hidden, main=True)
    assert {r["grain"] for r in db.execute("SELECT grain FROM code_index")} \
        == before, "an empty walk of a tracked tree leaves the index whole"


def test_the_stamped_area_hash_is_the_aggregate_it_replaced(world):
    """The table holds what `area_content_hash` used to compute live."""
    import hashlib

    db, repo, tree = world
    stamped = dict(db.execute("SELECT area, hash FROM area_hashes").fetchall())
    assert stamped, "onboarding stamps every area"

    live = {}
    for area in {r["area"] for r in db.execute(
            "SELECT DISTINCT area FROM code_index WHERE area IS NOT NULL")}:
        rows = [f"{r['grain']}={r['content_hash']}" for r in db.execute(
            "SELECT grain, content_hash FROM code_index WHERE grain_kind = "
            "'path' AND area = ? AND content_hash != '' ORDER BY grain", (area,))]
        if rows:
            live[area] = hashlib.sha256("|".join(rows).encode()).hexdigest()[:16]
    assert stamped == live
    for area, digest in live.items():
        assert area_content_hash(db, area) == digest
    assert area_content_hash(db, "src/nowhere") == "", \
        "an area with no stamp reads as view unknown, never as fresh"


def test_a_conflicted_merge_leaves_the_index_at_main(world):
    """The batch stopped running, so the index stops describing its worktree.

    The conflict re-raises before the merge finishes, and the refresh used to
    sit after the raise: every reader stayed on a worktree whose batch was
    deferred while main sat at its old head.
    """
    from rota.core import worktrees

    db, repo, tree = world
    repo.edit(tree, NEW_FILE, NEW_BODY)
    repo.edit(tree, "src/auth/accounts.py", "def whoami():\n    return 'batch'\n")
    repo.commit_in(tree, "the batch's work")
    indexer.refresh(db, tree, main=False)
    assert db.execute("SELECT 1 FROM code_index WHERE grain = ?",
                      (NEW_FILE,)).fetchone(), "the index is on the worktree"

    repo.edit(repo.root, "src/auth/accounts.py", "def whoami():\n    return 'main'\n")
    repo.commit_in(repo.root, "main moved the same line")

    with pytest.raises(worktrees.WorktreeError):
        lifecycle.merge(db, "b1")

    assert db.execute("SELECT status FROM batches WHERE id = 'b1'"
                      ).fetchone()["status"] == "deferred"
    assert db.execute("SELECT 1 FROM code_index WHERE grain = ?",
                      (NEW_FILE,)).fetchone() is None, \
        "a conflict leaves the index on main, not on the paused worktree"


def test_a_refresh_that_raises_anything_keeps_the_session_and_the_merge(
        world, monkeypatch):
    """The refresh is best effort, and best effort means every exception.

    The session's writes are committed before the refresh runs, so anything
    that escapes fails a session whose rows are already on record. In the
    merge it would escape after `status` says merged.
    """
    db, repo, tree = world

    def boom(*args, **kwargs):
        raise RuntimeError("the indexer went away")

    monkeypatch.setattr(indexer, "refresh", boom)
    out = _commit_the_new_function(db)

    assert db.execute("SELECT head_commit FROM batches WHERE id = 'b1'"
                      ).fetchone()["head_commit"] == out["head_commit"], \
        "the session's writes landed"
    assert db.execute("SELECT 1 FROM sessions WHERE id = 's1'").fetchone()
    last = db.execute("SELECT completion FROM turns WHERE session_id = 's1' "
                      "ORDER BY seq DESC LIMIT 1").fetchone()["completion"]
    assert "the code index still describes" in last, \
        "the failure is in the session's record, not in an exception"

    lifecycle.merge(db, "b1")

    assert db.execute("SELECT status FROM batches WHERE id = 'b1'"
                      ).fetchone()["status"] == "merged"
    assert db.execute("SELECT value FROM config WHERE key = 'index:b1'"
                      ).fetchone()["value"], "the reason is recorded"


def test_a_run_from_before_the_table_is_stamped_when_it_opens(tmp_path):
    """An empty `area_hashes` reads as "every area is still current".

    `init_db` creates the table on any database it opens, so a run onboarded
    before this table would have gone quiet: no survey could ever be reopened
    until the first refresh of main.
    """
    from rota.core import boot as core_boot

    repo = gitfixture.make(tmp_path, name="old_run")
    (repo.root / ".rota").mkdir(parents=True, exist_ok=True)
    db = init_db(repo.root / ".rota" / "rota.db")
    boot.onboard(db, repo.root)
    stamped = dict(db.execute("SELECT area, hash FROM area_hashes").fetchall())
    assert stamped
    db.execute("DELETE FROM area_hashes")      # the shape of the older run
    db.commit()
    db.close()

    conn, _ = core_boot.boot(repo.root, kill_processes=False)
    try:
        assert dict(conn.execute("SELECT area, hash FROM area_hashes").fetchall()) \
            == stamped, "boot stamps the table from the index the run has"
        # And once: a second open must not move a stamp somebody attested at.
        conn.execute("UPDATE area_hashes SET hash = 'deadbeefdeadbeef'")
        conn.commit()
        assert core_boot.stamp_missing_area_hashes(conn) == 0
    finally:
        conn.close()
    gitfixture.cleanup(repo)


def test_an_empty_probe_says_when_the_index_is_behind(world):
    """The recorded reason reaches the role the stale index misleads."""
    db, repo, tree = world
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
               "('index:b1', 'no tree to index at /gone')")
    db.commit()

    out = _probe(db, "echo_json", batch_id="b1")
    assert len(out) == 1, out
    assert "no tree to index at /gone" in out[0]["note"]
    assert "read the file instead" in out[0]["note"]

    hits = _probe(db, "accounts", batch_id="b1")
    assert hits and all("note" not in row for row in hits), \
        "a probe that matches is a read, not a note"


def test_a_refresh_that_works_ends_the_note_the_failed_one_left(world):
    """Nothing cleared the row, so one failed resume told every later probe
    that the index was behind, long after a refresh had caught it up."""
    db, repo, tree = world
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
               "('index:b1', 'no tree to index at /gone')")
    db.commit()
    assert "note" in _probe(db, "echo_json", batch_id="b1")[0]

    indexer.refresh(db, tree, main=False, batch_id="b1")

    assert db.execute("SELECT 1 FROM config WHERE key = 'index:b1'"
                      ).fetchone() is None, "a refresh that worked clears it"
    assert _probe(db, "echo_json", batch_id="b1") == [], \
        "an empty probe with a current index is a read that found nothing"
