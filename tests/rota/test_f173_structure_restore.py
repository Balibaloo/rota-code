"""
The structure puts a removed statement back with no model (frame 173,
build 3).

Dry run 8: a Developer removed `assert "\\n" not in line` from `_foldline`
at 67e0b2d0. The Architect judged the removal a mistake at a585c4ea, and
`touch_mistaken` woke s198 on qwen3.5:9b. s198 put the line back, not byte
for byte, and two more commits broke two inherited files. Roman,
2026-11-08 10:23: a restore of a statement the fork holds is not a model
limitation.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from rota.core import predicates as P
from rota.core.db import init_db
from rota.core.restore import restore_stray, restore_wake

PATH = "src/icalendar/parser/string.py"
GRAIN = f"{PATH}::_foldline"
FIX = Path(__file__).parent / "fixtures"
# icalendar's string.py at the fork 99619246 and at the head a585c4ea.
FORK = (FIX / "dry8_string_99619246.txt").read_bytes()
A585 = (FIX / "dry8_string_a585c4ea.txt").read_bytes()
GONE = b'    assert "\\n" not in line\n'
NOTE = 'removal: `assert "\\n" not in line` at line 129'


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t",
                           "-c", "user.email=t@t", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture
def run(tmp_path):
    """bg_1: the fork, a project root at the fork, a running batch."""
    root = tmp_path / "wt"
    (root / PATH).parent.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / PATH).write_bytes(FORK)
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "fork")
    proj = tmp_path / "proj"
    subprocess.run(["git", "clone", "-q", str(root), str(proj)], check=True)
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES ('fold','fold long lines','in_scope','approved',1,1)")
    conn.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES "
                 "('bg_1','fold','running',?)", (str(root),))
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('project_root', ?)",
                 (str(proj),))
    conn.commit()
    return conn, root


def _head(conn, root: Path, text: bytes, status: str = "mistake") -> str:
    """Commit `text` as the head and write the stray row at that head."""
    (root / PATH).write_bytes(text)
    _git(root, "commit", "-qam", "head")
    sha = _git(root, "rev-parse", "HEAD")
    conn.execute("UPDATE batches SET head_commit = ? WHERE id = 'bg_1'", (sha,))
    conn.execute("INSERT INTO touch_strays (batch_id, commit_sha, path, status, note) "
                 "VALUES ('bg_1', ?, ?, ?, ?)", (sha, GRAIN, status, NOTE))
    conn.commit()
    return sha


def test_the_mistake_row_is_restored_by_the_structure(run):
    """67e0b2d0 removed the one line. The restore puts the fork bytes back,
    commits, and closes the row, so `touch_mistaken` wakes nobody."""
    conn, root = run
    old = _head(conn, root, FORK.replace(GONE, b"", 1))
    assert [w.kind for w in P.touch_mistaken(conn)] == ["tick:touch_mistaken"]
    done, reasons = restore_wake(conn, "bg_1")
    conn.commit()
    assert reasons == [] and len(done) == 1, (done, reasons)
    assert (root / PATH).read_bytes() == FORK
    new = _git(root, "rev-parse", "HEAD")
    assert new == done[0]["restored"] != old
    assert "restore" in _git(root, "log", "-1", "--format=%s")
    assert "the Architect's judgement" in _git(root, "log", "-1", "--format=%s")
    assert conn.execute("SELECT head_commit FROM batches").fetchone()[0] == new
    row = conn.execute("SELECT status, note FROM touch_strays WHERE commit_sha = ?",
                       (old,)).fetchone()
    assert row["status"] == "restored" and new[:8] in row["note"]
    assert P.touch_mistaken(conn) == []


def test_the_replay_of_a585c4ea_restores_the_line_and_keeps_the_rest(run):
    """a585c4ea also added an escape branch in the fold. The restore puts
    the assert back in its fork place. The diff against the fork is the
    escape branch and its comments only."""
    conn, root = run
    _head(conn, root, A585)
    done, reasons = restore_wake(conn, "bg_1")
    assert reasons == [] and done, reasons
    diff = _git(root, "diff", "-U0", "HEAD~2", "HEAD", "--", PATH)
    assert "assert" not in diff, diff
    lines = (root / PATH).read_bytes().splitlines(keepends=True)
    at = lines.index(b"    assert isinstance(line, str)\n")
    assert lines[at + 1] == GONE and lines[at + 2] == b"\n"


def test_a_head_with_no_context_returns_the_reason_and_the_wake_runs(run):
    """The lines around the statement are rewritten at the head. Nothing
    changes, the row stays `mistake`, and `touch_mistaken` still wakes."""
    conn, root = run
    gone = FORK.replace(GONE, b"", 1).replace(
        b"    assert isinstance(line, str)\n", b"    line = str(line)\n", 1).replace(
        b"    folded_lines: list[str] = []\n", b"    folded_lines = []\n", 1)
    old = _head(conn, root, gone)
    done, reasons = restore_wake(conn, "bg_1")
    assert done == [] and len(reasons) == 1, reasons
    assert "context" in reasons[0]
    assert _git(root, "rev-parse", "HEAD") == old
    assert conn.execute("SELECT status FROM touch_strays").fetchone()[0] == "mistake"
    assert [w.kind for w in P.touch_mistaken(conn)] == ["tick:touch_mistaken"]


def test_a_head_without_the_file_returns_the_reason(run):
    conn, root = run
    _git(root, "rm", "-q", PATH)
    _git(root, "commit", "-qm", "gone")
    sha = _git(root, "rev-parse", "HEAD")
    conn.execute("UPDATE batches SET head_commit = ? WHERE id = 'bg_1'", (sha,))
    out = restore_stray(conn, "bg_1", GRAIN, "r_m45")
    assert "gone at the head" in out["reason"]


# Pass 2: his keep, the closed restore wake, the stopped page, two rows.

def _keep(conn, sha: str) -> str:
    """His landed keep on the removal line, through the one row builder."""
    from rota.roles.principal import removal_key, ruling_rows
    key = removal_key("bg_1", GRAIN, 129)
    conn.execute("INSERT INTO messages (id, seq, thread_id, from_role, to_role, "
                 "verb, body_refs) VALUES ('m31', 1, 't1', 'liaison', 'principal', "
                 "'present', '[\"fold\"]')")
    conn.execute("INSERT INTO rulings (id, ask_id, status) VALUES ('r_m45', 'm31', 'landed')")
    rows = ruling_rows(conn, "r_m45", [key], {key: {
        "verdict": "approve", "act": "keep", "target_kind": "row",
        "target": key.split("|", 1)[1], "words": "keep the assert"}})
    for r in rows:
        conn.execute(f"INSERT INTO ruled_refs ({', '.join(r)}) VALUES "
                     f"({', '.join('?' * len(r))})", tuple(r.values()))
    conn.commit()
    return key


def test_the_removal_line_is_keyed_and_takes_keep(run):
    from rota.roles.api import line_menu, _REMOVAL_ROWS
    from rota.roles.principal import removal_key, render_page
    conn, root = run
    _head(conn, root, FORK.replace(GONE, b"", 1), status="open")
    page, order = render_page(conn, "present", ["fold"])
    key = removal_key("bg_1", GRAIN, 129)
    assert order[-1] == key, order
    assert f"  {len(order)}. The change removes code" in page, page
    # Review p2, low: the numbered line stands after the page's last line.
    assert page.splitlines()[-1].startswith(f"  {len(order)}. The change"), page
    assert line_menu(conn, key, order, page) == ("removal", ["keep", "approve"])
    assert _REMOVAL_ROWS["keep"] == ("approve", "keep", "row")


def test_his_keep_lands_as_an_act_and_the_tick_restores(run):
    from rota.core.restore import restore_kept
    conn, root = run
    old = _head(conn, root, FORK.replace(GONE, b"", 1), status="open")
    key = _keep(conn, old)
    row = conn.execute("SELECT act, target_kind, target, words FROM ruled_refs "
                       "WHERE ref = ?", (key,)).fetchone()
    assert (row["act"], row["target_kind"]) == ("keep", "row")
    assert row["target"] == f"bg_1|{GRAIN}|129" and row["words"] == "keep the assert"
    done, reasons = restore_kept(conn)
    conn.commit()
    assert reasons == [] and len(done) == 1, reasons
    assert (root / PATH).read_bytes() == FORK
    assert "his ruling r_m45" in _git(root, "log", "-1", "--format=%s")
    assert conn.execute("SELECT status FROM touch_strays WHERE commit_sha = ?",
                        (old,)).fetchone()[0] == "restored"
    assert restore_kept(conn) == ([], [])


def test_two_mistake_rows_at_one_head_both_read_restored(run):
    conn, root = run
    old = _head(conn, root, FORK.replace(GONE, b"", 1))
    other = "src/icalendar/parser/string.py::_escape_char"
    conn.execute("INSERT INTO touch_strays (batch_id, commit_sha, path, status, note) "
                 "VALUES ('bg_1', ?, ?, 'mistake', 'removal: x')", (old, other))
    lines = (root / PATH).read_bytes()
    # A second statement gone in a second grain, at the same head.
    import ast
    tree = ast.parse(FORK.decode())
    fn = next(n for n in tree.body if getattr(n, "name", "") == "_escape_char")
    one = next(n for n in fn.body[1:] if n.lineno == n.end_lineno)
    gone2 = FORK.splitlines(keepends=True)[one.lineno - 1]
    (root / PATH).write_bytes(lines.replace(gone2, b"", 1))
    _git(root, "commit", "-qam", "two")
    two = _git(root, "rev-parse", "HEAD")
    conn.execute("UPDATE batches SET head_commit = ?", (two,))
    conn.execute("UPDATE touch_strays SET commit_sha = ?", (two,))
    conn.commit()
    done, reasons = restore_wake(conn, "bg_1")
    conn.commit()
    assert reasons == [] and len(done) == 2, (done, reasons)
    assert (root / PATH).read_bytes() == FORK
    assert [r[0] for r in conn.execute("SELECT status FROM touch_strays")] == [
        "restored", "restored"]


def test_the_restore_commit_in_the_wake_says_the_wake_is_done(run):
    """The context is gone, so the wake runs. The Developer's commit that
    puts the statement back gets the next step: the wake is done."""
    from rota.roles.api import Ctx, code_commit
    conn, root = run
    gone = FORK.replace(GONE, b"", 1).replace(
        b"    assert isinstance(line, str)\n", b"    line = str(line)\n", 1)
    _head(conn, root, gone)
    assert restore_wake(conn, "bg_1")[0] == []
    (root / PATH).write_bytes(gone.replace(
        b"    line = str(line)\n", b"    line = str(line)\n" + GONE, 1))
    ctx = Ctx(conn=conn, role="developer", batch_id="bg_1",
              wake_kind="tick:touch_mistaken")
    out = code_commit(ctx, "put the assert back")
    assert out["committed"] is True, out
    assert "This wake is done" in out.get("next", ""), out


def test_the_stopped_page_names_run_6_and_fddff3af(run):
    from rota.roles.principal import _red_run_words
    conn, _root = run
    seq = 0
    for test in ("inh_7bed8d74", "inh_c55c4bf6"):
        for attempt, sha, result in [(1, "99619246", "pass"), (2, "99619246", "pass"),
                                     (3, "67e0b2d0", "pass"), (4, "a585c4ea", "pass"),
                                     (5, "a585c4ea", "pass"), (6, "fddff3af", "fail")]:
            seq += 1
            conn.execute("INSERT INTO test_run_journal (id, batch_id, test_id, "
                         "commit_sha, result, attempt) VALUES (?, 'bg_1', ?, ?, ?, ?)",
                         (f"tr{seq}", test, sha + "0" * 32, result, attempt))
    said = _red_run_words(conn, "bg_1", ["inh_7bed8d74", "inh_c55c4bf6"])
    assert said == ("They passed on runs 1 to 5 and failed first on run 6, "
                    "at fddff3af"), said
    assert "after the team stopped" not in said


# Pass 3: the four highs of the two reviews.

def test_an_untracked_file_stays_out_of_the_restore_commit(run):
    """Review p1, high 1: `add -A` put a Developer's new file in the
    structure's commit. The commit takes the restored path only."""
    conn, root = run
    _head(conn, root, FORK.replace(GONE, b"", 1))
    (root / "src" / "new_dev.py").write_bytes(b"x = 1\n")
    done, reasons = restore_wake(conn, "bg_1")
    assert reasons == [] and len(done) == 1, reasons
    assert _git(root, "show", "--name-only", "--format=", "HEAD").split() == [PATH]
    assert _git(root, "status", "--porcelain", "--", "src/new_dev.py") == \
        "?? src/new_dev.py"


def test_one_row_that_cannot_go_back_holds_the_whole_head(run):
    """Review p1, high 2: a partial restore moved the head and left the
    other `mistake` row on the old head. Now no commit is made, both rows
    keep `mistake`, and the row that failed holds the reason."""
    conn, root = run
    old = _head(conn, root, FORK.replace(GONE, b"", 1))
    conn.execute("INSERT INTO touch_strays (batch_id, commit_sha, path, status, note) "
                 "VALUES ('bg_1', ?, 'src/missing.py::f', 'mistake', 'removal: y')",
                 (old,))
    done, reasons = restore_wake(conn, "bg_1")
    conn.commit()
    assert done == [] and len(reasons) == 1, (done, reasons)
    assert _git(root, "rev-parse", "HEAD") == old
    assert conn.execute("SELECT head_commit FROM batches").fetchone()[0] == old
    assert (root / PATH).read_bytes() == FORK.replace(GONE, b"", 1)
    got = {r["path"]: (r["status"], r["note"]) for r in conn.execute(
        "SELECT path, status, note FROM touch_strays")}
    assert got[GRAIN] == ("mistake", NOTE)
    assert got["src/missing.py::f"] == (
        "mistake", "removal: y restore: the fork does not hold src/missing.py")
    assert [w.refs for w in P.touch_mistaken(conn)] == [("bg_1",)]


def test_a_keep_that_cannot_go_back_writes_the_reason_once(run):
    """Review p2, high 2: a keep whose restore had a reason wrote nothing
    and ran again on every tick. The reason goes on the row once, the row
    reads `mistake`, and `touch_mistaken` wakes one Developer with it."""
    from rota.core.restore import restore_kept
    conn, root = run
    gone = FORK.replace(GONE, b"", 1).replace(
        b"    assert isinstance(line, str)\n", b"    line = str(line)\n", 1).replace(
        b"    folded_lines: list[str] = []\n", b"    folded_lines = []\n", 1)
    old = _head(conn, root, gone, status="open")
    _keep(conn, old)
    first = restore_kept(conn)
    conn.commit()
    second = restore_kept(conn)
    conn.commit()
    assert first[0] == [] and len(first[1]) == 1 and "context" in first[1][0], first
    assert second == ([], []), second
    row = conn.execute("SELECT status, note FROM touch_strays").fetchone()
    assert row["status"] == "mistake"
    assert row["note"].count("restore: ") == 1 and "context" in row["note"], row["note"]
    assert _git(root, "rev-parse", "HEAD") == old
    wakes = P.touch_mistaken(conn)
    assert [w.refs for w in wakes] == [("bg_1",)]
    done, reasons = restore_wake(conn, "bg_1")
    assert done == [] and "context" in reasons[0], reasons
    assert conn.execute("SELECT note FROM touch_strays").fetchone()[0] == row["note"]



def test_a_file_red_on_run_2_of_3_gets_no_stopped_clause(run):
    """Review p2, high 1: the file passed on run 1 and failed on runs 2
    and 3 while the team still worked. The sentence names the runs only."""
    from rota.roles.principal import _red_run_words
    conn, _root = run
    for seq, (attempt, sha, result) in enumerate(
            [(1, "aaaaaaaa", "pass"), (2, "bbbbbbbb", "fail"),
             (3, "cccccccc", "fail")], 1):
        conn.execute("INSERT INTO test_run_journal (id, batch_id, test_id, "
                     "commit_sha, result, attempt) VALUES (?, 'bg_1', 'inh_1', ?, ?, ?)",
                     (f"tr{seq}", sha + "0" * 32, result, attempt))
    said = _red_run_words(conn, "bg_1", ["inh_1"])
    assert said == "It passed on run 1 and failed first on run 2, at bbbbbbbb", said
    assert "after the team stopped" not in said
