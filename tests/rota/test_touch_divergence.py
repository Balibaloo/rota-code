"""
Detector two: the committed diff against the Architect's predicted touch set.

clickI night 32 (2026-09-13): `echo_json` merged in two files the prediction
never named, and nothing asked. First built 2026-09-03 on a branch the
history rewrite left behind; ported and given its wake and its merge hold.
"""
import subprocess

import pytest

from rota.core import lifecycle, predicates as P
from rota.core.db import init_db
from rota.core.divergence import stray_paths, under
from rota.core.sandbox import build
from rota.roles import prompts


def test_stray_paths_are_the_touched_paths_no_prediction_covers():
    assert under("src/notify/mail.py", "src/notify")
    assert under(r"src\notify\mail.py", "src/notify/")
    assert not under("src/notifyx/a.py", "src/notify")
    assert stray_paths(["src/a.py", "src/b.py"], ["src/a.py"]) == ["src/b.py"]
    assert stray_paths(["src/a.py", "src/n/x.py"], ["src/n", "src/a.py::login"]) == []
    assert stray_paths(["src/a.py"], []) == [], "nothing predicted, nothing strays"


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, provenance, approval, approval_ver, version) "
                 "VALUES ('i1','echo json','in_scope','decided','approved',1,1)")
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES ('b1','i1','running')")
    conn.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) VALUES ('b1','src/click/utils.py','path')")
    conn.commit()
    return conn


def _git(root, *args):
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                   check=True, capture_output=True)


def test_a_commit_outside_the_prediction_writes_a_stray_row_and_still_commits(db, tmp_path):
    root = tmp_path / "wt"; (root / "src" / "click").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "src" / "click" / "utils.py").write_text("def echo(x):\n    print(x)\n")
    _git(root, "add", "."); _git(root, "commit", "-q", "-m", "base")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    sb.call("code.write", path="src/echo_json.py", text="import json\n\ndef echo_json(o):\n    print(json.dumps(o))\n")
    out = sb.call("code.commit", message="echo_json beside echo")
    assert out["committed"], out
    assert out["outside_prediction"] == ["src/echo_json.py"]
    assert "never named" in out["note"]
    rows = [w for w in sb.ctx.writes if w[0] == "touch_strays"]
    assert [w[2]["path"] for w in rows] == ["src/echo_json.py"]
    assert rows[0][2]["status"] == "open" and rows[0][2]["commit_sha"] == out["head_commit"]


def test_an_open_stray_wakes_the_architect_and_holds_the_merge(db):
    db.execute("UPDATE batches SET head_commit = 'abc' WHERE id = 'b1'")
    db.execute("INSERT INTO touch_strays (batch_id, commit_sha, path) VALUES ('b1','abc','src/echo_json.py')")
    db.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result) VALUES ('v1','b1','abc','pass')")
    db.commit()
    wakes = P.touch_strayed(db)
    assert [(w.role, w.kind, w.refs, w.detail) for w in wakes] == \
        [("architect", "tick:touch_strayed", ("b1",), "src/echo_json.py")]
    assert P.touch_mistaken(db) == []
    assert lifecycle.mergeable(db, "b1") == "touch strayed, unjudged: src/echo_json.py"


def test_the_architect_judges_every_stray_foreseen_or_mistake(db):
    db.execute("UPDATE batches SET head_commit = 'abc' WHERE id = 'b1'")
    db.execute("INSERT INTO touch_strays (batch_id, commit_sha, path) VALUES ('b1','abc','src/echo_json.py')")
    db.execute("INSERT INTO touch_strays (batch_id, commit_sha, path) VALUES ('b1','abc','src/click/main.py')")
    db.commit()
    sb = build("architect", db, mode="touch_strayed",
               allow=prompts.mode_tools("architect", "touch_strayed"))
    with pytest.raises(ValueError, match="still unjudged"):
        sb.call("batches.judge_touch", batch_id="b1", foreseen=["src/echo_json.py"])
    out = sb.call("batches.judge_touch", batch_id="b1", foreseen=["src/other.py"],
                  mistakes=["src/echo_json.py", "src/click/main.py"])
    assert out["mistakes"] == ["src/echo_json.py", "src/click/main.py"] and "src/other.py" in out["ignored"]
    sb.ctx.writes.clear()
    out = sb.call("batches.judge_touch", batch_id="b1", foreseen=["src/echo_json.py"],
                  mistakes=["src/click/main.py"], reason="the helper is new; main.py is a second copy")
    assert {k: v for k, v in out.items() if k != "next"} == {
        "batch": "b1", "foreseen": ["src/echo_json.py"], "mistakes": ["src/click/main.py"]}
    assert "End with one sentence" in out["next"], "tipsBH s59: the judgement is done; say so"
    touch = [w for w in sb.ctx.writes if w[0] == "batch_touch"]
    assert [w[2]["grain"] for w in touch] == ["src/echo_json.py"], "a foreseen path joins the touch set"
    statuses = {w[2]["path"]: w[2]["status"] for w in sb.ctx.writes if w[0] == "touch_strays"}
    assert statuses == {"src/echo_json.py": "foreseen", "src/click/main.py": "mistake"}


def test_a_mistake_wakes_the_developer_and_a_new_head_leaves_it_behind(db):
    db.execute("UPDATE batches SET head_commit = 'abc' WHERE id = 'b1'")
    db.execute("INSERT INTO touch_strays (batch_id, commit_sha, path, status) "
               "VALUES ('b1','abc','src/click/main.py','mistake')")
    db.execute("INSERT INTO verdicts (id, batch_id, commit_sha, result) VALUES ('v1','b1','abc','pass')")
    db.commit()
    assert [(w.role, w.kind) for w in P.touch_mistaken(db)] == [("developer", "tick:touch_mistaken")]
    assert P.touch_strayed(db) == []
    assert lifecycle.mergeable(db, "b1").startswith("touch strayed, a mistake still in the head commit")
    db.execute("UPDATE batches SET head_commit = 'def' WHERE id = 'b1'")
    db.commit()
    assert P.touch_mistaken(db) == []
    assert not (lifecycle.mergeable(db, "b1") or "").startswith("touch strayed")


def test_a_judged_path_is_not_raised_again_by_the_next_commit(db, tmp_path):
    """The Developer's commit that takes a mistake out touches the same path."""
    root = tmp_path / "wt"; (root / "src" / "click").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "src" / "click" / "utils.py").write_text("def echo(x):\n    print(x)\n")
    (root / "src" / "click" / "main.py").write_text("x = 1\n")
    _git(root, "add", "."); _git(root, "commit", "-q", "-m", "base")
    db.execute("UPDATE batches SET worktree = ?, head_commit = 'abc' WHERE id = 'b1'", (str(root),))
    db.execute("INSERT INTO touch_strays (batch_id, commit_sha, path, status) "
               "VALUES ('b1','abc','src/click/main.py','mistake')")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="touch_mistaken",
               allow=prompts.mode_tools("developer", "touch_mistaken"))
    assert sb.call("batches.strays", batch_id="b1") == [
        {"path": "src/click/main.py", "status": "mistake", "note": None}]
    sb.call("code.write", path="src/click/main.py", text="x = 2\n")
    out = sb.call("code.commit", message="take the copy out")
    assert out["committed"] and "outside_prediction" not in out


def test_a_second_definition_of_a_name_the_tree_has_once_is_refused(db, tmp_path):
    """clickI night 35 (2026-09-13): `src/click/main.py` with its own `def echo`
    beside `echo_json`, when `src/click/utils.py::echo` is the function the
    ticket said "next to". A unique name defined again elsewhere is a copy."""
    root = tmp_path / "wt"; (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "utils.py").write_text("def echo(x):\n    print(x)\n")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    for grain in ("src/click/utils.py::echo", "src/click/core.py::main", "scripts/run.py::main",
                  "tests/test_utils/test_echo.py::test_echo"):
        db.execute("INSERT INTO code_index (grain, grain_kind) VALUES (?, 'symbol')", (grain,))
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    with pytest.raises(ValueError, match="already defines echo in src/click/utils.py"):
        sb.call("code.write", path="src/click/main.py",
                text="def echo(o):\n    print(o)\n\ndef echo_json(o):\n    print(o)\n")
    assert sb.call("code.write", path="src/click/main.py",
                   text="def main():\n    pass\n\ndef echo_json(o):\n    print(o)\n")["bytes"], \
        "a name the tree has in several modules is a convention"
    assert sb.call("code.write", path="src/click/utils.py",
                   text="def echo(x):\n    print(x)\n\ndef echo_plain(o):\n    print(o)\n")["bytes"], \
        "the module that owns the name may change it"


def test_a_test_file_is_never_a_stray(db, tmp_path):
    """clickI night 41 (2026-09-13): the harness commits the Tester's tests
    into the batch, and six test files were raised as the Developer's strays."""
    root = tmp_path / "wt"; (root / "src" / "click").mkdir(parents=True); (root / "tests").mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "src" / "click" / "utils.py").write_text("def echo(x):\n    print(x)\n")
    _git(root, "add", "."); _git(root, "commit", "-q", "-m", "base")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    (root / "tests" / "test_echo_json.py").write_text("def test_x():\n    assert True\n")
    sb.call("code.write", path="src/click/utils.py", start=2, end=2, text="\n\ndef echo_json(o):\n    print(o)\n")
    out = sb.call("code.commit", message="the helper, and the Tester's file beside it")
    assert out["committed"] and "outside_prediction" not in out, out


def test_a_name_the_batch_itself_defined_is_seen_without_the_index(db, tmp_path):
    """clickI night 42 (2026-09-13): `echo_json` landed in utils.py by this
    batch's own commit, and a second `echo_json` in a new module passed the
    index, which was built at onboarding. The worktree is the fact."""
    root = tmp_path / "wt"; (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "utils.py").write_text("def echo(x):\n    print(x)\n\n\ndef echo_json(o):\n    print(o)\n")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    with pytest.raises(ValueError, match="already defines echo_json in src/click/utils.py"):
        sb.call("code.write", path="src/click/echo_json_impl.py",
                text="import json\n\ndef echo_json(o, indent=2):\n    print(json.dumps(o, indent=indent))\n")


def test_a_file_may_keep_a_name_it_already_defined(db, tmp_path):
    """tipsBF (2026-09-13): tipsI defines calculate_tip in main.py and in
    tip_calculator.py; a whole-file rewrite of main.py that kept it was
    refused as a copy. The tree's own duplicate is not this change's."""
    root = tmp_path / "wt"; root.mkdir()
    (root / "main.py").write_text("def calculate_tip(t, p):\n    return t * p / 100\n")
    (root / "tip_calculator.py").write_text("def calculate_tip(t, p):\n    return t * p / 100\n")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    out = sb.call("code.write", path="main.py",
                  text="def calculate_tip(t, p):\n    return t * p / 100\n\n\ndef ask_people_count():\n    return 2\n")
    assert out["bytes"]
    with pytest.raises(ValueError, match="already defines ask_people_count in main.py"):
        sb.call("code.write", path="tip_calculator.py",
                text="def calculate_tip(t, p):\n    return t * p / 100\n\n\ndef ask_people_count():\n    return 3\n")


def test_a_placeholder_path_and_an_empty_write(db, tmp_path):
    """tipsBG (2026-09-14): `code.write(path=path, ...)` made a file called
    `path`, and the Developer took a mistake out by writing the file empty."""
    root = tmp_path / "wt"; root.mkdir()
    (root / "main.py").write_text("def main():\n    pass\n")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("INSERT INTO code_index (grain, grain_kind) VALUES ('main.py', 'path')")
    db.commit()
    sb = build("developer", db, batch_id="b1", mode="batch_start",
               allow=prompts.mode_tools("developer", "batch_start"))
    with pytest.raises(ValueError, match="name of the argument"):
        sb.call("code.write", path="path", text="x = 1\n")
    sb.call("code.write", path="extra.py", text="x = 1\n")
    out = sb.call("code.write", path="extra.py", text="")
    assert out.get("removed") == "extra.py" and not (root / "extra.py").exists()
    with pytest.raises(ValueError, match="the tree had before the batch stays"):
        sb.call("code.write", path="main.py", text="")
