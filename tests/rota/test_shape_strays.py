"""
The shape detector in the stray route (frame 306, option e).

Night 161 (2026-10-23): b_1 merged `echo_json(file=None)` and b_3 merged a
docstring edit, "``err``" to "`err`". No criterion named either, and both
sat inside a definition a criterion named, so no stray row held them. The
detector raises a new optional parameter and a removed line as rows.
"""
import json
import subprocess

import pytest

from rota.core import lifecycle
from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import prompts
from rota.testkit import samplerepo

PATH = "src/click/utils.py"


@pytest.fixture
def db(tmp_path, monkeypatch):
    for k, v in samplerepo.GIT_ENV.items():
        monkeypatch.setenv(k, v)
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version) "
                 "VALUES ('i1','echo json','in_scope','approved',1,1)")
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','running')")
    conn.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) "
                 "VALUES ('b1','src/click/utils.py','path')")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('t1','i1','echo json')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('b1','t1')")
    conn.commit()
    return conn


def _criterion(db, text, surfaces):
    db.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) VALUES (?,?,?,?)",
               (f"c{db.execute('SELECT COUNT(*) FROM criteria').fetchone()[0] + 1}",
                "t1", text, json.dumps(surfaces)))
    db.commit()


def _commit(db, tmp_path, base, head, crit="echo prints its value", **span):
    """Commit `base`, then write and commit `head` through the Developer.
    `span` gives `start` and `end` for a span write."""
    root = tmp_path / "wt"; (root / "src" / "click").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / PATH).write_bytes(base.encode())
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "base"], check=True)
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    if crit is not None:
        _criterion(db, crit, [f"{PATH}::echo"])
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    sb.call("code.write", path=PATH, text=head, **span)
    return sb, sb.call("code.commit", message="the change")


def _shape_rows(sb):
    return [w[2]["path"] for w in sb.ctx.writes
            if w[0] == "touch_strays" and ("(" in w[2]["path"] or ":L" in w[2]["path"])]


BASE = 'def echo(x):\n    """Print ``x``."""\n    # say it\n    foo(x)\n    return x\n'


def test_an_unnamed_optional_parameter_raises_one_row(db, tmp_path):
    head = BASE.replace("def echo(x):", "def echo(x, file=None):")
    sb, out = _commit(db, tmp_path, BASE, head)
    assert out["committed"], out
    assert _shape_rows(sb) == [f"{PATH}::echo(file)"]
    row = [w for w in sb.ctx.writes if w[0] == "touch_strays"][0][2]
    assert row["status"] == "open" and row["commit_sha"] == out["head_commit"]


def test_a_parameter_a_criterion_names_raises_nothing(db, tmp_path):
    head = BASE.replace("def echo(x):", "def echo(x, file=None):")
    sb, out = _commit(db, tmp_path, BASE, head, crit="echo writes to the given file")
    assert out["committed"] and _shape_rows(sb) == []


def test_a_signature_line_added_alone_is_shape_one_only(db, tmp_path):
    """Night 161 b_3: `@@ -295,0 +296,1 @@` adds one parameter line and
    removes nothing, so shape 2 has no removed line to raise."""
    base = "def echo(\n    x,\n):\n    return x\n"
    head = "def echo(\n    x,\n    flag: bool = False,\n):\n    return x\n"
    sb, out = _commit(db, tmp_path, base, head)
    assert out["committed"] and _shape_rows(sb) == [f"{PATH}::echo(flag)"]


def test_a_docstring_rewrite_raises_one_removed_line_row(db, tmp_path):
    head = BASE.replace("``x``", "`x`")
    sb, out = _commit(db, tmp_path, BASE, head)
    assert out["committed"] and _shape_rows(sb) == [f"{PATH}::echo:L2"]


def test_a_widened_line_raises_nothing(db, tmp_path):
    head = BASE.replace("foo(x)", "foo(x, y)")
    sb, out = _commit(db, tmp_path, BASE, head)
    assert out["committed"] and _shape_rows(sb) == []


def test_the_note_door_refuses_a_removed_statement_before_the_detector(db, tmp_path):
    """Night 158 bg_3 dropped `ctx.exit()`. The span write returns a note,
    and the door refuses the commit before the detector reads the diff."""
    base = "def echo(ctx):\n    print(ctx)\n    ctx.exit()\n\n\ndef other():\n    return 1\n"
    with pytest.raises(ValueError, match="ctx.exit()"):
        _commit(db, tmp_path, base, "    print(ctx)\n", start=2, end=3)
    assert db.execute("SELECT COUNT(*) FROM touch_strays").fetchone()[0] == 0


def test_a_removed_comment_raises_one_row(db, tmp_path):
    head = BASE.replace("    # say it\n", "")
    sb, out = _commit(db, tmp_path, BASE, head)
    assert out["committed"] and _shape_rows(sb) == [f"{PATH}::echo:L3"]


def test_an_open_shape_row_holds_the_merge_until_the_bare_path_is_judged(db):
    grain = f"{PATH}::echo:L3"
    db.execute("UPDATE batches SET head_commit = 'abc' WHERE id = 'b1'")
    db.execute("INSERT INTO touch_strays (batch_id, commit_sha, path) VALUES ('b1','abc',?)",
               (grain,))
    db.execute("INSERT INTO touch_strays (batch_id, commit_sha, path) VALUES ('b1','abc',?)",
               (f"{PATH}::echo(file)",))
    db.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result) VALUES ('v1','b1','abc','pass')")
    db.commit()
    assert lifecycle.mergeable(db, "b1").startswith("touch strayed, unjudged:")
    sb = build("architect", db, mode="touch_strayed",
               allow=prompts.mode_tools("architect", "touch_strayed"))
    out = sb.call("batches.judge_touch", batch_id="b1", foreseen=[PATH])
    assert sorted(out["foreseen"]) == sorted([grain, f"{PATH}::echo(file)"])
    for w in sb.ctx.writes:
        if w[0] == "touch_strays":
            db.execute("UPDATE touch_strays SET status = ? WHERE batch_id = 'b1' "
                       "AND commit_sha = 'abc' AND path = ?", (w[2]["status"], w[2]["path"]))
    db.commit()
    assert not (lifecycle.mergeable(db, "b1") or "").startswith("touch strayed")


def test_covers_matches_each_shape_grain_exactly(db):
    db.execute("UPDATE batches SET head_commit = 'abc' WHERE id = 'b1'")
    for g in (f"{PATH}::echo(file)", f"{PATH}::module:L9"):
        db.execute("INSERT INTO touch_strays (batch_id, commit_sha, path) VALUES ('b1','abc',?)", (g,))
    db.commit()
    sb = build("architect", db, mode="touch_strayed",
               allow=prompts.mode_tools("architect", "touch_strayed"))
    out = sb.call("batches.judge_touch", batch_id="b1", foreseen=[f"./{PATH}::echo(file)"],
                  mistakes=[f"{PATH}::module:L9"])
    assert out["foreseen"] == [f"{PATH}::echo(file)"]
    assert out["mistakes"] == [f"{PATH}::module:L9"]


def test_a_judged_line_does_not_hide_a_later_removal_in_its_hunk(db, tmp_path):
    """Review 3, high: a docstring edit judged at `f:L2` hid `ctx.exit()`
    that a later commit removed in the same hunk. One row per removed line."""
    base = 'def echo(ctx):\n    """Print ``ctx``."""\n    ctx.exit()\n'
    head = 'def echo(ctx):\n    """Print `ctx`."""\n'
    db.execute("INSERT INTO touch_strays (batch_id, commit_sha, path, status) "
               "VALUES ('b1','old',?,'foreseen')", (f"{PATH}::echo:L2",))
    db.commit()
    sb, out = _commit(db, tmp_path, base, head)
    assert out["committed"] and _shape_rows(sb) == [f"{PATH}::echo:L3"]


def test_a_short_removed_statement_beside_a_longer_added_line_raises(db, tmp_path):
    """Review 3, low: `ctx.exit()` is a character subsequence of the added
    line, but the added line does not hold it, so it is a removal."""
    base = "def echo(ctx):\n    ctx.exit()\n"
    head = "def echo(ctx):\n    ctx.text_exit_value(1)\n"
    sb, out = _commit(db, tmp_path, base, head)
    assert out["committed"] and _shape_rows(sb) == [f"{PATH}::echo:L2"]
