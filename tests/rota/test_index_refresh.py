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

    # The index line left the sign-off page (frame 298's design, 2.2), so
    # the pin reads the index straight.
    assert db.execute("SELECT 1 FROM code_index WHERE grain = ? AND grain_kind = 'path'",
                      (NEW_FILE,)).fetchone(), "the index holds the file the batch made"

    # The directory the batch made is now a directory the tree has, so the
    # Architect can predict a second file beside the first. Frame 302: the
    # call names the second file as new.
    sb = build_sandbox("architect", db, mode="annotate", batch_id="b1",
                       allow=prompts.mode_tools("architect", "annotate"))
    out = sb.call("batches.annotate", batch_id="b1",
                  paths=["src/echo/json_echo.py", "src/echo/second.py"],
                  new_files=["src/echo/second.py"])
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


# --- the symbol spans (frame 43, pass 3) ------------------------------------
#
# The index knew where every definition was and threw it away one line after
# the parser found it, so a seat that probed a name could only read the file
# four hundred lines at a time.


def test_a_probe_returns_the_span_of_the_definition(world):
    """
    The two numbers are `code.source(path, start, end)`'s own arguments, so the
    seat reads the function and not the file. 0-based, and the end is one line
    past the definition.
    """
    db, repo, tree = world
    _commit_the_new_function(db)

    row = [r for r in _probe(db, "echo_json", batch_id="b1")
           if r["grain"] == f"{NEW_FILE}::echo_json"][0]
    start, end = row["line_start"], row["line_end"]
    lines = NEW_BODY.splitlines()
    assert lines[start].startswith("def echo_json"), lines[start]
    assert end == len(lines), (start, end)

    sb = build_sandbox("developer", db, batch_id="b1", mode="tests_failing",
                       allow=prompts.mode_tools("developer", "tests_failing"))
    out = sb.call("code.source", path=NEW_FILE, start=start, end=end)
    assert out["text"].startswith("def echo_json"), out["text"]
    assert "print(json.dumps(obj))" in out["text"], "the span stops short of the body"


def test_a_path_grain_carries_no_span(world):
    """A file is not a definition. Path grains take the column's default, and
    they carry it rather than omitting it: a ragged row set drops `_as_table`
    back to JSON, which costs more than the two cells."""
    db, repo, tree = world
    spans = {(r["line_start"], r["line_end"]) for r in db.execute(
        "SELECT line_start, line_end FROM code_index WHERE grain_kind = 'path'")}
    assert spans == {(0, 0)}, spans


def test_a_refresh_keeps_the_span_of_a_symbol_the_batch_added(world):
    """
    `refresh` writes one column of its own, `area`. Every other column comes
    from the `build` it calls first, so the spans are current by construction.
    Pinned because frame 43 changed what `build` writes and frame 33 owns this
    path.
    """
    db, repo, tree = world
    _commit_the_new_function(db)
    grain = f"{NEW_FILE}::echo_json"
    before = db.execute(
        "SELECT line_start, line_end FROM code_index WHERE grain = ?",
        (grain,)).fetchone()
    assert (before["line_start"], before["line_end"]) == (3, 5), dict(before)

    indexer.refresh(db, tree, main=False, batch_id="b1")

    after = db.execute(
        "SELECT line_start, line_end, area FROM code_index WHERE grain = ?",
        (grain,)).fetchone()
    assert (after["line_start"], after["line_end"]) == (3, 5), dict(after)
    assert after["area"], "the refresh restores the area over the rebuilt row"


def test_a_database_from_before_the_spans_gains_the_columns(tmp_path):
    """
    `executescript` adds a table, never a column, and a run database under
    `.rota/` outlives the schema. The columns arrive on the next open and the
    rows already there are left where they are.
    """
    path = tmp_path / "rota.db"
    db = init_db(path)
    # The table as it stood before this change, written out. `DROP COLUMN`
    # cannot make it: SQLite re-parses the stored CREATE text and the schema's
    # comments leave a trailing comma behind the dropped column.
    db.execute("DROP TABLE code_index")
    db.execute("CREATE TABLE code_index ("
               "grain TEXT PRIMARY KEY, "
               "grain_kind TEXT NOT NULL CHECK (grain_kind IN "
               "('path','symbol','table','route')), "
               "area TEXT, fan_in INTEGER NOT NULL DEFAULT 0, "
               "sym_kind TEXT NOT NULL DEFAULT '', "
               "content_hash TEXT NOT NULL DEFAULT '')")
    db.execute("INSERT INTO code_index (grain, grain_kind) VALUES ('src/a.py','path')")
    db.commit()
    db.close()

    again = init_db(path)
    have = {r[1] for r in again.execute("PRAGMA table_info(code_index)")}
    assert {"line_start", "line_end"} <= have, have
    rows = [tuple(r) for r in again.execute(
        "SELECT grain, line_start, line_end FROM code_index")]
    assert rows == [("src/a.py", 0, 0)], rows
    again.close()


def test_a_broad_probe_is_capped_and_says_which_way_out(world):
    """
    A truncated probe is the worst of both: the seat pays for the rows and
    loses the tail without being told which. The cap is the op's, the note is
    the op's, and the note offers no next range because the op has no range.
    """
    from rota.core.runner import RESULT_CHARS, _render
    from rota.roles.api import PROBE_ROWS

    db, repo, tree = world
    for i in range(PROBE_ROWS + 40):
        db.execute("INSERT INTO code_index (grain, grain_kind, sym_kind, "
                   "line_start, line_end) VALUES (?, 'symbol', 'function', ?, ?)",
                   (f"src/pkg/module_{i:03d}.py::render_{i:03d}", i, i + 12))
    db.commit()

    total = db.execute("SELECT COUNT(*) n FROM code_index "
                       "WHERE grain LIKE '%render_%'").fetchone()["n"]
    hits = _probe(db, "render_", batch_id="b1")
    assert len(hits) == PROBE_ROWS + 1, "the cap, and one row saying so"
    assert "too broad" in hits[0]["grain"], hits[0]
    assert "next range" not in hits[0]["grain"], "this op has no range argument"
    assert f"{total} grains match" in hits[0]["grain"], hits[0]
    assert total > PROBE_ROWS, "the fixture did not overflow the cap"

    shown = _render(hits)
    assert len(shown) < RESULT_CHARS, len(shown)
    assert "CUT " not in shown, "the cap must land before the renderer's"


def test_a_broad_probe_answers_with_definitions_before_files(world):
    """
    `build` gives every symbol a fan-in of 0, so an order by fan-in alone put
    every matching path above every matching definition. With the 60-row cap a
    broad pattern could spend the whole cap on paths and hand back no span,
    which is the one thing the probe is now for.
    """
    from rota.roles.api import PROBE_ROWS

    db, repo, tree = world
    for i in range(PROBE_ROWS):
        db.execute("INSERT INTO code_index (grain, grain_kind, fan_in) "
                   "VALUES (?, 'path', ?)", (f"src/pkg/render_{i:03d}.py", 50 + i))
    db.execute("INSERT INTO code_index (grain, grain_kind, sym_kind, line_start, "
               "line_end) VALUES ('src/pkg/one.py::render_total','symbol',"
               "'function',10,20)")
    db.commit()

    hits = _probe(db, "render_", batch_id="b1")
    assert "too broad" in hits[0]["grain"], "the fixture did not overflow the cap"
    assert hits[1]["grain_kind"] == "symbol", \
        f"a definition sorts under {PROBE_ROWS} files: {[h['grain'] for h in hits[:3]]}"
    assert hits[1]["line_start"] == 10 and hits[1]["line_end"] == 20
    # The note says the order it used, and a path row says what to read rather
    # than a span of no lines: `code.source(path, 0, 0)` returns nothing, and
    # only a Python file has the `defs` map to rescue the seat.
    assert "definitions in name order" in hits[0]["grain"], hits[0]["grain"]
    paths = [r for r in hits if r["grain_kind"] == "path"]
    assert paths, "the fixture has no path rows to check"
    assert all(r["line_start"] == "whole file" and r["line_end"] == ""
               for r in paths), paths[0]


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


def test_a_probe_of_an_index_with_no_rows_says_the_index_is_empty(world):
    """Frame 326, fault A. A register case without `onboard: true` has an
    empty index, and a bare `[]` read as "the name is absent". The note
    names the empty index and the read that still works."""
    db, repo, tree = world
    db.execute("DELETE FROM code_index")
    db.commit()

    out = _probe(db, "line_total", batch_id="b1")
    assert out == [{"note": "the code index holds no code, so no pattern can "
                            "match, 'line_total' included. The empty result "
                            "says nothing about the tree. Read the file with "
                            "`code.source`."}], out


def test_the_empty_index_note_names_no_read_the_mode_lacks(world):
    """`architect/deliver` holds the probe and not `code.source`, so the note
    stops before the read (frame 326, review 1, finding 6)."""
    db, repo, tree = world
    db.execute("DELETE FROM code_index")
    db.commit()
    allow = prompts.mode_tools("architect", "deliver")
    assert "code.probe" in allow and "code.source" not in allow, allow

    sb = build_sandbox("architect", db, mode="deliver", allow=allow)
    out = sb.call("code.probe", pattern="line_total")
    assert out == [{"note": "the code index holds no code, so no pattern can "
                            "match, 'line_total' included. The empty result "
                            "says nothing about the tree."}], out


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


def test_index_batch_leaves_the_run_in_a_delivery_nights_state(tmp_path):
    """Frame 326, review 1b, finding 1. The batch index alone put every row
    in area `.` and left the phase at `frame`, which holds delivery. The
    fixture now writes the end state of a night's onboarding."""
    from rota.core import predicates, scheduler
    from rota.testkit import fixtures

    case = {"id": "index-batch", "repo": {
        "batch": "b1", "index_batch": True, "message": "close an account",
        "edit": {"src/billing/accounts.py":
                 "def close_account(account_id):\n    return account_id\n"}}}
    db = init_db(tmp_path / "case.db")
    fixtures.seed(db, {"items": [{"id": "i1", "text": "close an account",
                                  "kind": "in_scope", "approval": "approved",
                                  "approval_ver": 1, "version": 1}],
                       "batches": [{"id": "b1", "item_id": "i1",
                                    "status": "running"}]})
    repo = fixtures._with_repo(db, case, tmp_path / "case.db")
    try:
        row = db.execute("SELECT area, line_start FROM code_index WHERE grain = "
                         "'src/billing/accounts.py::close_account'").fetchone()
        assert row is not None, "the batch's own definition is indexed"
        assert row["area"] == "src/billing", row["area"]
        assert scheduler.onboarding_phase(db) == "done"
        assert predicates.frame(db) == []
        assert predicates.constraint_zero(db) == []
    finally:
        gitfixture.cleanup(repo)
