"""
A removal that no criterion, request or ruling asks for lands, and the
Architect judges it as a stray (frame 339).

Night 169 (2026-10-26): every criterion of batch_1 named
`src/click/utils.py::get_app_dir`. The Developers s122 to s136 rewrote the
fallback under `if folder is None:` and removed
`folder = os.path.expanduser("~")`. The removal door refused every commit,
the start key went to quarantine, and his answer m37, "You can remove the
line at 518 in get_app_dir ...", did not match the door's `line 518`. Law 12
says nothing rejects a diff for straying. His ruling of 2026-10-17 sends an
unexpected change to the Architect for sign-off.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from rota.core import lifecycle
from rota.core import predicates as P
from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import prompts

PATH = "src/click/utils.py"
GRAIN = f"{PATH}::get_app_dir"
# clickI's utils.py, the base of night 169's batch_1 in substance.
BASE = (Path(__file__).parent / "fixtures"
        / "night124_utils_617055787d.txt").read_bytes()
GONE = 'folder = os.path.expanduser("~")'
# s122's write of seq 4, `turns` of night 169, as a span over the
# `if folder is None:` block: lines 518 and 519 of the base, which
# code.source numbers 517 and 518. On the night it returned the note
# "This write removes or rewrites 1 statement ... at line 518".
FIX = ('        if folder is None:\n'
       '            appdata_roaming = os.path.join(os.path.expanduser("~"), '
       '"AppData", "Roaming")\n'
       '            appdata_local = os.path.join(os.path.expanduser("~"), '
       '"AppData", "Local")\n'
       '            if roaming:\n'
       '                folder = appdata_roaming\n'
       '            else:\n'
       '                folder = appdata_local')
MESSAGE = "Fix Windows get_app_dir to use AppData Roaming/Local"
# His m37, ruling r_58bf1e8c70 of night 169.
M37 = ("You can remove the line at 518 in get_app_dir that sets the folder to "
       "the bare home folder.")


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES ('get_app_dir_windows','use the AppData Roaming or AppData "
                 "Local folder instead of the bare home folder','in_scope',"
                 "'approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','get_app_dir_windows','the Windows fallback')")
    for n, text in enumerate((
            "With roaming True and APPDATA unset, the path is under AppData Roaming.",
            "With roaming False and LOCALAPPDATA unset, the path is under AppData Local.",
    ), 1):
        conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                     "VALUES (?, 'tk1', ?, ?)", (f"crit_{n}", text, json.dumps([GRAIN])))
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) VALUES "
                 "('batch_1','get_app_dir_windows','running','abc123')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('batch_1','tk1')")
    conn.execute("INSERT INTO code_index (grain, grain_kind, sym_kind) VALUES "
                 "(?, 'path', 'file')", (PATH,))
    conn.commit()
    return conn


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t",
                           "-c", "user.email=t@t", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def _developer(db, tmp_path):
    """batch_1's worktree: the base, then one batch commit, so the base is
    HEAD~1, and the Developer's `batch_start` sandbox."""
    root = tmp_path / "wt"
    (root / PATH).parent.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / PATH).write_bytes(BASE)
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    (root / "NOTES.md").write_text("batch_1\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "batch")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'batch_1'", (str(root),))
    db.commit()
    sb = build("developer", db, batch_id="batch_1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    return sb, root


def _strays(sb) -> list[tuple]:
    return [(w[2]["path"], w[2]["status"], w[2].get("note"))
            for w in sb.ctx.writes if w[0] == "touch_strays"]


def _write_then_commit(sb) -> dict:
    out = sb.call("code.write", path=PATH, start=517, end=519, text=FIX)
    assert GONE in out["dropped"], out
    sb.begin_reply()
    return sb.call("code.commit", message=MESSAGE)


def test_night_169s_rewrite_lands_with_one_open_stray(db, tmp_path):
    """The red case. On b889c93d the open-note door refused this commit:
    "a code.write in an earlier reply returned a note, and the tree still
    does not hold those lines". Now it lands, and one row asks the
    Architect, with the removed line in its note."""
    sb, root = _developer(db, tmp_path)
    out = _write_then_commit(sb)
    assert out["committed"] is True, out
    assert _git(root, "rev-parse", "HEAD") == out["head_commit"]
    rows = _strays(sb)
    assert len(rows) == 1, rows
    grain, status, note = rows[0]
    assert (grain, status) == (GRAIN, "open")
    assert note.startswith(f"removal: `{GONE}` at line "), note
    assert out["removals"] == [f"{GRAIN}: {note}"]
    assert "The Architect is asked" in out["removals note"]


def test_his_m37_words_are_no_permission_form_and_the_stray_stands(db, tmp_path):
    """m37 says "the line at 518". The `line N` match is gone, so no form
    of his words is needed. The commit lands, and the Architect judges."""
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_text, seq) VALUES ('m37','t1','principal','liaison','answer',"
               "'x',37)")
    db.execute("INSERT INTO rulings (id, ask_id, per_item, words, status) VALUES "
               "('r_58bf1e8c70','m37',?,?,'landed')",
               (json.dumps({"batch_1": "approve", "get_app_dir_windows": "approve"}), M37))
    db.commit()
    sb, _root = _developer(db, tmp_path)
    out = _write_then_commit(sb)
    assert out["committed"] is True, out
    assert [r[0] for r in _strays(sb)] == [GRAIN]


def test_a_criterion_that_asks_for_the_removal_lands_with_no_stray(db, tmp_path):
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('crit_3','tk1',"
               "'Remove the folder = os.path.expanduser(\"~\") fallback from "
               "get_app_dir.')")
    db.commit()
    sb, _root = _developer(db, tmp_path)
    out = _write_then_commit(sb)
    assert out["committed"] is True, out
    assert _strays(sb) == []
    assert "removals" not in out


def test_the_commit_in_the_writes_own_reply_waits_for_the_read(db, tmp_path):
    """Frame 140's door stays: the seat reads the note first. The route
    names the commit of the next reply as the way to keep the change."""
    sb, root = _developer(db, tmp_path)
    head = _git(root, "rev-parse", "HEAD")
    sb.call("code.write", path=PATH, start=517, end=519, text=FIX)
    with pytest.raises(ValueError) as err:
        sb.call("code.commit", message=MESSAGE)
    msg = str(err.value)
    assert msg.startswith("your code.write in this reply returned a note"), msg
    assert msg.endswith("To keep the change, commit in your next reply. The "
                        "Architect then judges the removal before the batch "
                        "merges."), msg
    assert _git(root, "rev-parse", "HEAD") == head


def test_the_architect_reads_the_removed_line_and_the_merge_waits(db, tmp_path):
    """The row reaches `touch_strayed` as frame 286's rows do. The wake's
    detail holds the grain and the note, and `mergeable` holds the merge."""
    sb, _root = _developer(db, tmp_path)
    out = _write_then_commit(sb)
    sha = out["head_commit"]
    note = _strays(sb)[0][2]
    db.execute("UPDATE batches SET head_commit = ? WHERE id = 'batch_1'", (sha,))
    db.execute("INSERT INTO touch_strays (batch_id, commit_sha, path, status, note) "
               "VALUES ('batch_1', ?, ?, 'open', ?)", (sha, GRAIN, note))
    db.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result) VALUES "
               "('v1','batch_1',?,'pass')", (sha,))
    db.commit()
    wakes = P.touch_strayed(db)
    assert [(w.role, w.kind, w.refs, w.detail) for w in wakes] == [
        ("architect", "tick:touch_strayed", ("batch_1",), f"{GRAIN} ({note})")]
    assert lifecycle.mergeable(db, "batch_1") == (
        f"touch strayed, unjudged: {GRAIN}")


def test_a_mistake_keeps_the_line_for_the_developer(db, tmp_path):
    """The Architect calls it a mistake. `touch_mistaken` wakes the
    Developer, and `batches.strays` shows the removed line beside the
    reason, so the Developer knows which line to put back."""
    db.execute("UPDATE batches SET head_commit = 'abc' WHERE id = 'batch_1'")
    note = f"removal: `{GONE}` at line 519"
    db.execute("INSERT INTO touch_strays (batch_id, commit_sha, path, status, note) "
               "VALUES ('batch_1', 'abc', ?, 'open', ?)", (GRAIN, note))
    db.commit()
    arch = build("architect", db, mode="touch_strayed",
                 allow=prompts.mode_tools("architect", "touch_strayed"))
    out = arch.call("batches.judge_touch", batch_id="batch_1", mistakes=[GRAIN],
                    reason="the fallback must stay")
    assert out["mistakes"] == [GRAIN]
    rows = [w[2] for w in arch.ctx.writes if w[0] == "touch_strays"]
    assert [(r["status"], r["note"]) for r in rows] == [
        ("mistake", f"{note} the fallback must stay")]
    db.execute("UPDATE touch_strays SET status = 'mistake', note = ? "
               "WHERE batch_id = 'batch_1'", (rows[0]["note"],))
    db.commit()
    assert [(w.role, w.kind) for w in P.touch_mistaken(db)] == [
        ("developer", "tick:touch_mistaken")]


def test_a_judged_removal_is_not_raised_again(db, tmp_path):
    """Frame 286's rule: a grain judged either way is not raised again on a
    later commit of the batch."""
    sb, _root = _developer(db, tmp_path)
    db.execute("INSERT INTO touch_strays (batch_id, commit_sha, path, status) "
               "VALUES ('batch_1', 'old', ?, 'foreseen')", (GRAIN,))
    db.commit()
    out = _write_then_commit(sb)
    assert out["committed"] is True, out
    assert _strays(sb) == []
