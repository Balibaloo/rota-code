"""
F7: the commit compares the base with the tree, a removal row needs a
judgement that names it, and an ungranted removal shows on his page.

Night 171 (2026-10-27): s164's commits a46638f3 and 62199a7b removed the
macOS branch and the XDG return of `get_app_dir`. The write's note named
the darwin line only, s172 judged the bare file path foreseen, and the
fold of frame 286 carried that judgement onto the removal. No page that he
saw showed the removal (`plans/night171-w4-read.md`).
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import api, prompts
from rota.roles.principal import (insert_ruling_rows, removal_line, render_page,
                                  render_state, ruling_rows)

PATH = "src/click/utils.py"
GRAIN = f"{PATH}::get_app_dir"
FIX = Path(__file__).parent / "fixtures"
# clickI at 2c8cd3a, the base of night 171's bg_1, and s164's two heads.
BASE = (FIX / "night171_utils_base_2c8cd3a.txt").read_bytes()
HEADS = {sha: (FIX / f"night171_utils_{sha}.txt").read_bytes()
         for sha in ("a46638f3", "62199a7b")}
DARWIN = '`if sys.platform == "darwin":` at line 522'
XDG = "`return os.path.join(` at line 526"
NOTE = f"removal: {DARWIN}, {XDG}"
# night124's utils.py: `folder = os.path.expanduser("~")` is line 518 in
# code.source numbering, the line of night 170's s128.
N124 = (FIX / "night124_utils_617055787d.txt").read_bytes().decode("utf-8")
S128_GONE = 'folder = os.path.expanduser("~")'


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES ('get_app_dir_windows','In get_app_dir on Windows, when "
                 "APPDATA or LOCALAPPDATA is not set, use the AppData Roaming or "
                 "AppData Local folder','in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','get_app_dir_windows','the Windows fallback')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) VALUES "
                 "('c_1','tk1','With APPDATA unset, the path is under AppData "
                 "Roaming.',?)", (json.dumps([GRAIN]),))
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES "
                 "('bg_1','get_app_dir_windows','running')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('bg_1','tk1')")
    conn.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) VALUES "
                 "('bg_1', ?, 'path')", (PATH,))
    conn.commit()
    return conn


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t",
                           "-c", "user.email=t@t", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def _commit_head(db, tmp_path, text: bytes):
    """bg_1's worktree at the base, the project root kept there, and the
    Developer's commit of `text` with no write before it."""
    root = tmp_path / "wt"
    (root / PATH).parent.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / PATH).write_bytes(BASE)
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    proj = tmp_path / "proj"
    subprocess.run(["git", "clone", "-q", str(root), str(proj)], check=True)
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'bg_1'", (str(root),))
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('project_root', ?)",
               (str(proj),))
    db.commit()
    sb = build("developer", db, batch_id="bg_1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    (root / PATH).write_bytes(text)
    return sb, sb.call("code.commit", message="Fix path separator normalization")


@pytest.mark.parametrize("sha", ["a46638f3", "62199a7b"])
def test_s164s_commit_finds_the_darwin_branch_and_the_xdg_return(db, tmp_path, sha):
    """The write's note named the darwin line only. The compare of the base
    with the tree names both removals in one row of the definition."""
    _sb, out = _commit_head(db, tmp_path, HEADS[sha])
    assert out["committed"] is True, out
    assert out["removals"] == [f"{GRAIN}: {NOTE}"], out


def _open_row(db, status: str = "open", note: str = NOTE) -> None:
    db.execute("UPDATE batches SET head_commit = 'h1', status = 'deferred' "
               "WHERE id = 'bg_1'")
    db.execute("INSERT INTO touch_strays (batch_id, commit_sha, path, status, note) "
               "VALUES ('bg_1', 'h1', ?, ?, ?)", (GRAIN, status, note))
    db.commit()


def test_a_bare_path_judgement_leaves_the_removal_row_open(db):
    """s172 sent `foreseen=["src/click/utils.py"]`. The fold of frame 286
    no longer covers a removal row, so the call is refused, and the
    refusal names the row and the two calls that judge it."""
    _open_row(db)
    arch = build("architect", db, mode="touch_strayed",
                 allow=prompts.mode_tools("architect", "touch_strayed"))
    with pytest.raises(ValueError) as err:
        arch.call("batches.judge_touch", batch_id="bg_1", foreseen=[PATH],
                  reason="aligns with the prediction")
    msg = str(err.value)
    assert msg.startswith("this removal is still unjudged, because a file path "
                          "does not judge a removal."), msg
    assert f"{GRAIN} ({NOTE})" in msg
    assert f"foreseen=['{GRAIN}'], mistakes=[]) if the work needed" in msg
    assert f"foreseen=[], mistakes=['{GRAIN}']) if it did not" in msg
    assert not [w for w in arch.ctx.writes if w[0] == "touch_strays"]


def test_a_judgement_that_names_the_removal_lands(db):
    _open_row(db)
    arch = build("architect", db, mode="touch_strayed",
                 allow=prompts.mode_tools("architect", "touch_strayed"))
    out = arch.call("batches.judge_touch", batch_id="bg_1", mistakes=[GRAIN],
                    reason="his request names Windows only")
    assert out["mistakes"] == [GRAIN]


def test_the_page_about_the_item_shows_both_removals_in_one_line(db):
    """The Architect judged the row foreseen. The shift page of night 171
    still shows the removal, in plain words, with no key and no row id."""
    _open_row(db, "foreseen", f"{NOTE} aligns with the prediction")
    page, order = render_page(db, "present", ["get_app_dir_windows"],
                              ask_id="m_shift_get_app_dir_windows_m_p2")
    lines = [ln for ln in page.split("\n") if "removes code" in ln]
    assert lines == [
        "The change removes code that no answer of yours allowed: in "
        'get_app_dir, the branch `if sys.platform == "darwin":` and the '
        "return `return os.path.join(`."], page
    assert "bg_1" not in lines[0] and "::" not in lines[0]
    assert order == ["get_app_dir_windows"]


def test_ten_removals_take_one_line(db):
    pieces = ", ".join(f"`call_{n}()` at line {n}" for n in range(10))
    _open_row(db, "open", f"removal: {pieces}")
    line = removal_line(db, ["get_app_dir_windows"])
    assert line == ("The change removes code that no answer of yours allowed: in "
                    "get_app_dir, the call `call_0()` and the call `call_1()` and "
                    "the call `call_2()`, and 7 more."), line


def _grant(db, rid: str, ref: str, target: str, seq: int) -> None:
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_text, seq) VALUES (?,'t1','principal','liaison','answer','x',?)",
               (f"m{seq}", seq))
    db.execute("INSERT INTO rulings (id, ask_id, per_item, words, status) VALUES "
               "(?,?,?,'You can remove it.','landed')",
               (rid, f"m{seq}", json.dumps({ref: "approve"})))
    insert_ruling_rows(db, ruling_rows(
        db, rid, [ref], {ref: {"verdict": "approve", "act": "remove",
                               "target": target}}, words="You can remove it."))
    db.commit()


def test_a_granted_removal_shows_no_line(db):
    _open_row(db, "foreseen")
    _grant(db, "r_1", "bg_1", "get_app_dir:522", 1)
    assert removal_line(db, ["get_app_dir_windows"]) == (
        "The change removes code that no answer of yours allowed: in "
        "get_app_dir, the return `return os.path.join(`.")
    _grant(db, "r_2", "get_app_dir_windows", "get_app_dir:526", 2)
    assert removal_line(db, ["get_app_dir_windows"]) == ""


def test_a_merged_change_shows_no_line(db):
    _open_row(db, "foreseen")
    db.execute("UPDATE batches SET status = 'merged' WHERE id = 'bg_1'")
    db.commit()
    assert removal_line(db, ["get_app_dir_windows"]) == ""


def _merged(db) -> None:
    """bg_1 merged under `merge_gate=auto` with s164's two removals open."""
    _open_row(db, "open")
    db.execute("UPDATE batches SET status = 'merged' WHERE id = 'bg_1'")
    db.commit()


def test_the_summary_after_an_auto_merge_names_both_removals(db):
    """Pass 1b: under `merge_gate=auto` nothing holds the merge, so the
    summary that he reads after it names s164's two removals once."""
    _merged(db)
    state = render_state(db)
    assert state.split("\n")[:2] == [
        "Done: 1 change built, tested and merged.",
        "The merged changes removed code that no answer of yours allowed: in "
        'get_app_dir, the branch `if sys.platform == "darwin":` and the return '
        "`return os.path.join(`."], state
    assert state.count("darwin") == 1
    assert "bg_1" not in state.split("\n")[1]


def test_a_granted_removal_is_not_in_the_summary(db):
    _merged(db)
    _grant(db, "r_1", "bg_1", "get_app_dir:522", 1)
    assert "darwin" not in render_state(db)
    _grant(db, "r_2", "get_app_dir_windows", "get_app_dir:526", 2)
    assert "removed code" not in render_state(db)


def test_s128s_same_target_rewrite_is_no_removal():
    """Night 170's s128 gave `folder` a new value in place. The statement
    still binds `folder` on its path, so the compare finds no removal."""
    new = N124.replace(S128_GONE, 'folder = os.path.join(os.path.expanduser("~"), '
                       '"AppData", "Roaming" if roaming else "Local")', 1)
    assert new != N124
    assert api._removal_entry(N124, new) is None


def test_a_value_in_one_arm_only_is_a_removal():
    """The same target in one arm of a new `if` leaves the other path with
    no value: the statement's behaviour went."""
    new = N124.replace(S128_GONE, "if roaming:\n                folder = 'r'", 1)
    e = api._removal_entry(N124, new)
    assert e is not None and [x[1] for x in e["lines"]] == [S128_GONE]


def test_a_rewritten_return_and_a_widened_branch_are_no_removal():
    base = "def f(x):\n    if x is None:\n        return 1\n    return x\n"
    new = "def f(x):\n    if x is None or x == '':\n        return 2\n    return x + 1\n"
    assert api._removal_entry(base, new) is None
    gone = "def f(x):\n    if x is None or x == '':\n        return 2\n"
    e = api._removal_entry(base, gone)
    assert [x[1] for x in e["lines"]] == ["return x"]
