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


# Pass 2 answers review 1 (`plans/f7-review-p1.md`). Each shape is a probe
# of `f7rev/shapes.py` or `f7rev/pipeline.py`, by its number there.
LOST_SHAPES = {
    # Finding 1, probe 13: a new return with the same first line hid the
    # removed XDG-like return.
    "13 return gone, a new one has its first line": (
        'def d(roaming):\n'
        '    if sys.platform == "darwin":\n'
        '        return os.path.join(\n'
        '            "a", "b")\n'
        '    return os.path.join(\n'
        '        "xdg", "c")\n',
        'def d(roaming):\n'
        '    if sys.platform == "darwin":\n'
        '        return os.path.join(\n'
        '            "a", "b")\n'
        '    if roaming:\n'
        '        return os.path.join(\n'
        '            "win", "c")\n'
        '    raise RuntimeError()\n',
        ["`return os.path.join(` at line 4"]),
    # Finding 1, probe 12: the `else` arm became an unconditional value.
    "12 else arm gone": (
        "def f(c):\n    if c:\n        v = 1\n    else:\n        v = 2\n    return v\n",
        "def f(c):\n    if c:\n        v = 1\n    v = 2\n    return v\n",
        ["`v = 2` at line 4"]),
    # Finding 2, probe 7: a branch on another condition is no partner.
    "7 branch on another condition": (
        'def f(roaming):\n    if sys.platform == "darwin":\n        return mac()\n'
        '    return xdg()\n',
        "def f(roaming):\n    if roaming:\n        return win()\n    return xdg()\n",
        ['`if sys.platform == "darwin":` at line 1']),
    # Finding 4, probe 9: an `import` and an `assert` are behaviour.
    "9 import and assert gone": (
        "import plugins\ndef f(x):\n    assert x > 0\n    go(x)\n",
        "def f(x):\n    go(x)\n",
        ["`import plugins` at line 0", "`assert x > 0` at line 2"]),
    # Finding 4, probe 10: a rebind after a read keeps no initial value.
    "10 init gone, a later rebind": (
        "def f(xs):\n    total = 0\n    for x in xs:\n        total += x\n"
        "    total = round(total)\n    return total\n",
        "def f(xs):\n    for x in xs:\n        total += x\n"
        "    total = round(total)\n    return total\n",
        ["`total = 0` at line 1"]),
    # Finding 5, probe 11: the exact match comes first, so `if a:` is lost
    # and its body `one()` is not named.
    "11 if gone, a wider if stays": (
        "def f(a, b):\n    if a:\n        one()\n    if a and b:\n        two()\n",
        "def f(a, b):\n    if a and b:\n        two()\n",
        ["`if a:` at line 1"]),
    # Probe 14: a guard gone, so the call runs on every path.
    "14 guard gone": (
        "def f(c):\n    if c:\n        go()\n    stop()\n",
        "def f(c):\n    go()\n    stop()\n",
        ["`if c:` at line 1"]),
}


@pytest.mark.parametrize("name", sorted(LOST_SHAPES))
def test_a_removed_statement_gets_named_after_the_line_filter(name):
    base, now, shown = LOST_SHAPES[name]
    e = api._removal_entry(base, now)
    assert e, name
    assert [g["shown"] for g in api._gone_statements(now, e)] == shown


KEPT_SHAPES = {
    # Finding 3, probe 3: a renamed local keeps its value.
    "3 renamed local": ("def f():\n    tmp = compute()\n    return tmp\n",
                        "def f():\n    result = compute()\n    return result\n"),
    # Finding 3, probe 4: two arms with one body merged into one branch.
    "4 merged elif": ("def f(a, b):\n    if a:\n        run()\n    elif b:\n        run()\n",
                      "def f(a, b):\n    if a or b:\n        run()\n"),
    # Finding 3, probe 5: a branch that never runs.
    "5 dead branch": ("def f():\n    if False:\n        run()\n    go()\n",
                      "def f():\n    go()\n"),
    "6 docstring": ('def f():\n    """Old words."""\n    go()\n',
                    'def f():\n    """New words."""\n    go()\n'),
    "8 return in a new with": ("def f():\n    x = load()\n    return x\n",
                               "def f():\n    with lock:\n        x = load()\n        return x\n"),
    # Review 2, finding 4: a move into a new block that runs on every path.
    "2a under if True": ("def f(x):\n    go(x)\n    stop()\n",
                         "def f(x):\n    if True:\n        go(x)\n    stop()\n"),
    "2b under a local set True": ("def f(x):\n    debug = True\n    go(x)\n",
                                  "def f(x):\n    debug = True\n    if debug:\n        go(x)\n"),
    "2c under a guard true by its own code": (
        "def f(items=None):\n    items = items or []\n    run(items)\n",
        "def f(items=None):\n    items = items or []\n    if items is not None:\n"
        "        run(items)\n"),
    "2e in a loop over one item": ("def f(p):\n    go(p)\n",
                                   "def f(p):\n    for q in [p]:\n        go(q)\n"),
    "2f in both arms of a new if and else": (
        "def f(c):\n    go()\n",
        "def f(c):\n    if c:\n        log()\n        go()\n    else:\n        go()\n"),
    # Review 2, finding 3: a renamed local that is used, and a bound result.
    "5a2 call result now bound": ("def f(a):\n    go(a)\n    stop()\n",
                                  "def f(a):\n    res = go(a)\n    stop()\n"),
    "5c renamed local, method call": ("def f(p):\n    tmp = open(p)\n    tmp.close()\n",
                                      "def f(p):\n    fh = open(p)\n    fh.close()\n"),
    "5c2 renamed loop target": (
        "def f(xs):\n    total = 0\n    for x in xs:\n        total += x\n    return total\n",
        "def f(xs):\n    total = 0\n    for item in xs:\n        total += item\n"
        "    return total\n"),
    "5c3 renamed local in a test": (
        "def f(p):\n    tmp = load(p)\n    if tmp:\n        go()\n",
        "def f(p):\n    data = load(p)\n    if data:\n        go()\n"),
    "5c4 renamed accumulator": (
        "def f(xs):\n    acc = 0\n    for x in xs:\n        acc += x\n    return acc\n",
        "def f(xs):\n    total = 0\n    for x in xs:\n        total += x\n    return total\n"),
}


# Review 2, finding 1: a removed definition whose name stays in the file.
# Each is lost by its `def` line, and its row is the definition's own.
DEF_SHAPES = {
    "o1 property setter gone": (
        "class C:\n    @property\n    def x(self):\n        return self._x\n\n"
        "    @x.setter\n    def x(self, v):\n        self._x = v\n",
        "class C:\n    @property\n    def x(self):\n        return self._x\n",
        ("C.x", "`def x(self, v):` at line 6")),
    "o2 property getter gone, setter kept": (
        "class C:\n    @property\n    def x(self):\n        return self._x\n\n"
        "    @x.setter\n    def x(self, v):\n        self._x = v\n",
        "class C:\n    @x.setter\n    def x(self, v):\n        self._x = v\n",
        ("C.x", "`def x(self):` at line 2")),
    "o3 platform def in an else arm gone": (
        'if sys.platform == "darwin":\n    def home():\n        return mac_home()\n'
        "else:\n    def home():\n        return xdg_home()\n",
        'if sys.platform == "darwin":\n    def home():\n        return mac_home()\n',
        ("home", "`def home():` at line 4")),
}


@pytest.mark.parametrize("name", sorted(DEF_SHAPES))
def test_a_removed_definition_whose_name_stays_gets_its_own_row(name):
    base, now, (owner, shown) = DEF_SHAPES[name]
    e = api._removal_entry(base, now)
    assert e, name
    assert [(g["owner"], g["shown"]) for g in api._gone_statements(now, e)] == [
        (owner, shown)]


def test_a_move_into_a_loop_that_can_skip_it_stays_a_removal():
    """Review 2, shape 2g: a loop over many items can run zero times."""
    base, now = "def f(ps):\n    go(ps[0])\n", "def f(ps):\n    for p in ps:\n        go(p)\n"
    e = api._removal_entry(base, now)
    assert [g["shown"] for g in api._gone_statements(now, e)] == ["`go(ps[0])` at line 1"]


@pytest.mark.parametrize("name", sorted(KEPT_SHAPES))
def test_a_rewrite_that_keeps_the_behaviour_is_no_removal(name):
    base, now = KEPT_SHAPES[name]
    assert api._removal_entry(base, now) is None


def test_s164s_widened_branch_is_kept_and_its_two_removals_are_named():
    """Night 171's case at the compare: `if folder is None:` widened, and
    the darwin branch and the XDG return gone. Each one is named."""
    base = BASE.decode("utf-8")
    for text in HEADS.values():
        e = api._removal_entry(base, text.decode("utf-8"))
        assert [g["shown"] for g in api._gone_statements(text.decode("utf-8"), e)] == [
            DARWIN, XDG]


def test_a_mistake_does_not_cover_a_removal_its_note_lacks(db):
    """Finding 8: the darwin and XDG lines are back, and another call is
    gone. The grain opens again with the new note, so his page names the
    new removal and not lines that are back."""
    from types import SimpleNamespace
    _open_row(db, "mistake", f"{NOTE} his request names Windows only")
    new = "`_posixify(app_name)` at line 530"
    gone = {PATH: [{"shown": new, "line": "_posixify(app_name)",
                    "owner": "get_app_dir", "no": "530", "def": False}]}
    ctx = SimpleNamespace(conn=db, batch_id="bg_1")
    unjudged, mistaken, foreseen = api._removal_strays(ctx, None, gone)
    assert (unjudged, mistaken, foreseen) == ({GRAIN: f"removal: {new}"}, {}, {})
    darwin = {PATH: [{"shown": DARWIN, "line": 'if sys.platform == "darwin":',
                      "owner": "get_app_dir", "no": "522", "def": False}]}
    assert api._removal_strays(ctx, None, darwin)[1] == {
        GRAIN: f"{NOTE} his request names Windows only"}


def test_each_offered_call_lands_with_two_removal_rows_and_a_file_row(db):
    """Finding 7: each call that the refusal offers names every open row,
    so the door admits it as sent (frame 135)."""
    import ast as _ast
    import re as _re
    _open_row(db)
    db.execute("INSERT INTO touch_strays (batch_id, commit_sha, path, status, note) "
               "VALUES ('bg_1','h1',?,'open','removal: `return x` at line 40')",
               (f"{PATH}::_posixify",))
    db.execute("INSERT INTO touch_strays (batch_id, commit_sha, path, status) "
               "VALUES ('bg_1','h1','CHANGES.rst','open')")
    db.commit()

    def arch():
        return build("architect", db, mode="touch_strayed",
                     allow=prompts.mode_tools("architect", "touch_strayed"))
    with pytest.raises(ValueError) as err:
        arch().call("batches.judge_touch", batch_id="bg_1",
                    foreseen=[PATH, "CHANGES.rst"], reason="r")
    calls = _re.findall(r"batches\.judge_touch\(batch_id='bg_1', foreseen=(\[.*?\]), "
                        r"mistakes=(\[.*?\])\)", str(err.value))
    assert len(calls) == 2, str(err.value)
    for fs, ms in calls:
        out = arch().call("batches.judge_touch", batch_id="bg_1",
                          foreseen=_ast.literal_eval(fs),
                          mistakes=_ast.literal_eval(ms), reason="r")
        assert set(out["foreseen"]) | set(out["mistakes"]) >= {
            GRAIN, f"{PATH}::_posixify", "CHANGES.rst"}, out


def test_the_compare_reads_every_base_text_with_one_git_spawn(db, tmp_path, monkeypatch):
    """Finding 10: four spawns for each changed path took about 0.45 s.
    The spawns of the compare do not grow with the count of paths."""
    def spawns(n: int) -> tuple[int, int]:
        root = tmp_path / f"wt{n}"
        root.mkdir()
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        for i in range(n):
            (root / f"m{i}.py").write_text("def f():\n    a()\n    b()\n", newline="")
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "-m", "base")
        _git(root, "commit", "-q", "--allow-empty", "-m", "head")
        for i in range(n):
            (root / f"m{i}.py").write_text("def f():\n    a()\n", newline="")
        db.execute("UPDATE batches SET worktree = ? WHERE id = 'bg_1'", (str(root),))
        db.commit()
        sb = build("developer", db, batch_id="bg_1", mode="batch_start",
                   allow=prompts.mode_tools("developer", "batch_start"))
        count = []
        real = subprocess.run
        monkeypatch.setattr(subprocess, "run",
                            lambda *a, **k: count.append(1) or real(*a, **k))
        found, _told = api._base_removals(sb.ctx, root)
        monkeypatch.setattr(subprocess, "run", real)
        return len(found), len(count)
    one, ten = spawns(1), spawns(10)
    assert (one[0], ten[0]) == (1, 10)
    assert ten[1] == one[1], (one, ten)


def test_one_compare_gives_the_removal_rows():
    """The one-reader property of F7: the commit takes the removal fact
    from one compare of the base with the tree. A second caller of the
    compare outside these sites is a second reader, and this test goes
    red."""
    import ast as _ast
    allowed = {"_removal_entry": {"_base_removals"},
               "_base_removals": {"_unruled_removals"},
               "_unruled_removals": {"code_commit", "_removal_strays"},
               "_removal_strays": {"code_commit"}}
    found: dict[str, set] = {k: set() for k in allowed}
    pkg = Path(api.__file__).resolve().parents[1]
    for path in pkg.rglob("*.py"):
        tree = _ast.parse(path.read_text(encoding="utf-8"))
        for fn in _ast.walk(tree):
            if not isinstance(fn, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
                continue
            for node in _ast.walk(fn):
                if (isinstance(node, _ast.Call) and isinstance(node.func, _ast.Name)
                        and node.func.id in allowed):
                    found[node.func.id].add(fn.name)
    assert found == allowed
