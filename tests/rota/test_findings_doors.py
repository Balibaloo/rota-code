"""
Frame 178: three refusals at the door of `findings.find`.

Frame 170's merges read found three faults in one door
(`plans/frame170-merges-read.md`, sections 1, 3 and 5, 2026-10-07):

1. A second batch's Architect wrote `f1` again, and the first batch's row
   was replaced. Nights 120 and 128, 2 of 2 nights with two merges.
2. 7 of 18 finding rows named a file the diff does not change, each from
   the batch's `expected to touch` list.
3. Night 118's Architect filed `k0` on a file that 11 bound constraints
   reach, and checked none of them.

Each test sends the recorded call, verbatim from the turn in the night's
database (opened `mode=ro`, 2026-10-08), to the real door through the
sandbox. Each fixture rebuilds the batch's worktree with the files its diff
changed, so the door reads the diff from git as on the night.
"""
from __future__ import annotations

import subprocess

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.core.worktrees import GIT
from rota.llm import toolproto
from rota.roles import prompts

K0_HEAD = "this area has not been surveyed"

# Night 128, s196, turn 1 (`.rota/clickI_night128.db`). bg_1's `f1` stood,
# filed by s143, and this call wrote `f1` version 2 for bg_2.
S196_CALL = ('TOOL: findings.find(id="f1", batch_id="bg_2", constraint_id="k0", '
             'status="satisfied", grain="src/click/termui.py")')
# Night 114, s203, turn 4 (`.rota/clickI_night114.db`). bg_2's diff changes
# `src/click/termui.py` only.
S203_CALL = ('TOOL: findings.find(id="f2", batch_id="bg_2", constraint_id="k0", '
             'status="satisfied", '
             'grain="tests/test_defaults.py::test_lookup_default_returns_hides_sentinel")')
# Night 118, s145, turn 2 (`.rota/clickI_night118.db`). The diff changes
# `src/click/__init__.py` and `src/click/utils.py`.
S145_CALL = ('TOOL: findings.find(id="f2", batch_id="echo_json_group", '
             'constraint_id="k0", status="satisfied", grain="src/click/__init__.py")')

# Night 118's register: id, headline, bindings (observed: `constraints` and
# `constraint_bindings`, `.rota/clickI_night118.db`, 2026-10-08).
_INIT = "src/click/__init__.py"
_UTILS_ = "src/click/_utils.py"
_GLOBALS = "src/click/globals.py"
NIGHT118_CONSTRAINTS = [
    ("flag_needs_value", "FLAG_NEEDS_VALUE", (_INIT, _UTILS_)),
    ("get_current_context", "get_current_context", (_INIT, _GLOBALS)),
    ("k0", K0_HEAD, ()),
    ("pass_environment", "pass_environment",
     ("examples/complex/complex/commands/cmd_status.py",)),
    ("pop_context", "pop_context", (_INIT, _GLOBALS)),
    ("push_context", "push_context", (_INIT, _GLOBALS)),
    ("resolve_color_default", "resolve_color_default", (_INIT, _GLOBALS)),
    ("sentinel", "Sentinel", (_INIT, _UTILS_)),
    ("sentinel_flag_needs_value", "Sentinel.FLAG_NEEDS_VALUE", (_INIT, _UTILS_)),
    ("sentinel_unset", "Sentinel.UNSET", (_INIT, _UTILS_)),
    ("t_flag_needs_value", "T_FLAG_NEEDS_VALUE", (_INIT, _UTILS_)),
    ("t_unset", "T_UNSET", (_INIT, _UTILS_)),
    ("unset", "UNSET", (_INIT, _UTILS_)),
]
K0_ONLY = [("k0", K0_HEAD, ())]


def _git(path, *args) -> str:
    return subprocess.run([*GIT, "-C", str(path), *args], check=True,
                          capture_output=True, text=True).stdout


def a_night(tmp_path, batch_id: str, changed: list[str], constraints,
            others=()):
    """A project root, one batch worktree whose commit changes `changed`,
    and the register `constraints`. `others` are further batches with no
    worktree, as a merged batch has on the night."""
    root = tmp_path / "root"
    root.mkdir()
    _git(root, "init", "-q")
    every = {"src/click/termui.py", "src/click/utils.py", _INIT, _UTILS_,
             _GLOBALS, "tests/test_defaults.py"}
    for rel in sorted(every):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(b"x = 1\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "click")
    tree = tmp_path / "batch"
    _git(root, "worktree", "add", "-q", "-b", f"batch/{batch_id}", str(tree))
    for rel in changed:
        (tree / rel).write_bytes(b"x = 2\n")
    _git(tree, "commit", "-q", "--allow-empty", "-am", "the batch")
    head = _git(tree, "rev-parse", "HEAD").strip()
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO config (key, value) VALUES ('project_root', ?)",
                 (str(root),))
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1','the item','in_scope','approved',1,1)")
    conn.execute("INSERT INTO batches (id, item_id, status, worktree, "
                 "head_commit) VALUES (?, 'i1', 'running', ?, ?)",
                 (batch_id, str(tree), head))
    for other in others:
        conn.execute("INSERT INTO batches (id, item_id, status, head_commit) "
                     "VALUES (?, 'i1', 'merged', 'cb31ea31')", (other,))
    for cid, headline, grains in constraints:
        conn.execute("INSERT INTO constraints (id, headline) VALUES (?, ?)",
                     (cid, headline))
        for grain in grains:
            conn.execute("INSERT INTO constraint_bindings (constraint_id, grain, "
                         "grain_kind, resolves) VALUES (?, ?, 'path', 1)",
                         (cid, grain))
    conn.commit()
    return conn


def _architect(conn, batch_id):
    return build("architect", conn, batch_id=batch_id, mode="normal",
                 allow=prompts.mode_tools("architect", "structural_review"))


def _args(text: str) -> dict:
    (call,) = toolproto.extract(text)
    assert call.name == "findings.find"
    return call.args


def _refused(sb, **kwargs) -> str:
    with pytest.raises(ValueError) as exc:
        sb.call("findings.find", **kwargs)
    assert not [w for w in sb.ctx.writes if w[0] == "findings"], \
        "a refused finding stages no row"
    return str(exc.value)


@pytest.fixture
def night128(tmp_path):
    """Night 128: bg_1 merged with its `f1`, and bg_2 changes termui.py."""
    conn = a_night(tmp_path, "bg_2", ["src/click/termui.py"], K0_ONLY,
                   others=("bg_1",))
    conn.execute("INSERT INTO findings (id, batch_id, constraint_id, commit_sha, "
                 "status, grain) VALUES ('f1', 'bg_1', 'k0', 'cb31ea31', "
                 "'satisfied', 'src/click/utils.py')")
    conn.commit()
    return conn


@pytest.fixture
def night114(tmp_path):
    return a_night(tmp_path, "bg_2", ["src/click/termui.py"], K0_ONLY)


@pytest.fixture
def night118(tmp_path):
    return a_night(tmp_path, "echo_json_group", [_INIT, "src/click/utils.py"],
                   NIGHT118_CONSTRAINTS)


# Check 1: an id that another batch's row holds.

def test_s196_f1_held_by_bg_1_is_refused(night128):
    said = _refused(_architect(night128, "bg_2"), **_args(S196_CALL))
    assert said == (
        "finding id 'f1' is held by batch bg_1, and this call would replace "
        "that batch's finding. A finding id names one row across every batch. "
        "Send the finding again with id='f2', which no batch holds")
    row = night128.execute("SELECT batch_id, version FROM findings "
                           "WHERE id = 'f1'").fetchone()
    assert tuple(row) == ("bg_1", 1)


def test_s196_with_the_free_id_lands(night128):
    out = _architect(night128, "bg_2").call(
        "findings.find", **{**_args(S196_CALL), "id": "f2"})
    assert out == {"id": "f2", "status": "satisfied"}


def test_the_free_id_skips_every_held_id(night128):
    night128.execute("INSERT INTO findings (id, batch_id, constraint_id, "
                     "commit_sha, status, grain) VALUES ('f2', 'bg_1', 'k0', "
                     "'cb31ea31', 'satisfied', 'src/click/utils.py')")
    night128.commit()
    said = _refused(_architect(night128, "bg_2"), **_args(S196_CALL))
    assert "with id='f3', which no batch holds" in said


def test_an_id_with_no_number_gets_one(night128):
    night128.execute("UPDATE findings SET id = 'fnd' WHERE id = 'f1'")
    night128.commit()
    said = _refused(_architect(night128, "bg_2"),
                    **{**_args(S196_CALL), "id": "fnd"})
    assert "with id='fnd_2', which no batch holds" in said


def test_the_seats_own_id_stays_a_new_version(night128):
    """A seat that names its own batch's id keeps today's behaviour: the
    pipeline writes a new version of its own row."""
    night128.execute("INSERT INTO findings (id, batch_id, constraint_id, "
                     "commit_sha, status, grain) VALUES ('f7', 'bg_2', 'k0', "
                     "'old', 'satisfied', 'src/click/termui.py')")
    night128.commit()
    out = _architect(night128, "bg_2").call(
        "findings.find", **{**_args(S196_CALL), "id": "f7"})
    assert out == {"id": "f7", "status": "satisfied"}


# Check 2: a satisfied or k0 grain the diff does not touch.

def test_s203_grain_off_the_diff_is_refused(night114):
    said = _refused(_architect(night114, "bg_2"), **_args(S203_CALL))
    assert said == (
        "the batch's diff does not touch 'tests/test_defaults.py'; it changed "
        "['src/click/termui.py']. A finding names a file the diff changed, and "
        "a file the batch was expected to touch is not one. Send the finding "
        "again with one of ['src/click/termui.py'] as the grain")


def test_s203_with_a_grain_in_the_diff_lands(night114):
    out = _architect(night114, "bg_2").call(
        "findings.find", **{**_args(S203_CALL), "grain": "src/click/termui.py"})
    assert out == {"id": "f2", "status": "satisfied"}


def test_a_satisfied_row_off_the_diff_on_a_bound_constraint_is_refused(night114):
    """The check reads the status, not constraint zero alone."""
    night114.execute("INSERT INTO constraints (id, headline) VALUES "
                     "('k1', 'one rule')")
    night114.commit()
    said = _refused(_architect(night114, "bg_2"), id="f9", batch_id="bg_2",
                    constraint_id="k1", status="satisfied",
                    grain="src/click/utils.py")
    assert said.startswith("the batch's diff does not touch 'src/click/utils.py'")


# Check 3: k0 on a file that a bound constraint reaches.

def test_s145_k0_beside_eleven_bound_constraints_is_refused(night118):
    said = _refused(_architect(night118, "echo_json_group"), **_args(S145_CALL))
    assert said == (
        "k0 is for a file that no constraint reaches, and 11 constraints reach "
        "'src/click/__init__.py': 'flag_needs_value' (FLAG_NEEDS_VALUE), "
        "'get_current_context' (get_current_context), 'pop_context' "
        "(pop_context), 'push_context' (push_context), 'resolve_color_default' "
        "(resolve_color_default), 'sentinel' (Sentinel), "
        "'sentinel_flag_needs_value' (Sentinel.FLAG_NEEDS_VALUE), "
        "'sentinel_unset' (Sentinel.UNSET), 't_flag_needs_value' "
        "(T_FLAG_NEEDS_VALUE), 't_unset' (T_UNSET), 'unset' (UNSET). Check "
        "each of them against the diff, and file one finding for each, "
        "satisfied or violated, with 'src/click/__init__.py' as the grain")


def test_s145_k0_on_an_unreached_file_lands(night118):
    """s145's turn 1: `src/click/utils.py` is in the diff, and no bound
    constraint reaches it."""
    out = _architect(night118, "echo_json_group").call(
        "findings.find", **{**_args(S145_CALL), "id": "f1",
                            "grain": "src/click/utils.py"})
    assert out == {"id": "f1", "status": "satisfied"}


def test_s145_a_bound_constraint_on_the_file_lands(night118):
    out = _architect(night118, "echo_json_group").call(
        "findings.find", **{**_args(S145_CALL), "constraint_id": "sentinel"})
    assert out == {"id": "f2", "status": "satisfied"}


def test_a_long_headline_shows_its_first_words(night118):
    night118.execute("UPDATE constraints SET headline = 'a write goes through "
                     "one connection so a migration sees it' WHERE id = 'unset'")
    night118.commit()
    said = _refused(_architect(night118, "echo_json_group"), **_args(S145_CALL))
    assert "'unset' (a write goes through one connection ...)" in said


# Pass 2: the findings of the diff review of af2ee732.

def test_a_staged_id_of_another_batch_is_refused(night128):
    """Finding 4: a row staged in this session holds its id as a stored
    row does, because the pipeline writes it at commit."""
    night128.execute("DELETE FROM findings")
    night128.commit()
    sb = _architect(night128, "bg_2")
    sb.call("findings.find", id="f1", batch_id="bg_1", constraint_id="k0",
            status="satisfied", grain="src/click/utils.py")
    with pytest.raises(ValueError) as exc:
        sb.call("findings.find", **_args(S196_CALL))
    assert str(exc.value).startswith("finding id 'f1' is held by batch bg_1")
    assert "with id='f2', which no batch holds" in str(exc.value)


@pytest.mark.parametrize("held,named,free", [
    ("fnd_001", "fnd_001", "fnd_002"),
    ("fnd_", "fnd_", "fnd_2"),
    ("fnd", "fnd", "fnd_2"),
])
def test_the_free_id_keeps_the_seats_form(night128, held, named, free):
    """Finding 5: the padding width and the separator stay the seat's."""
    night128.execute("UPDATE findings SET id = ? WHERE id = 'f1'", (held,))
    night128.commit()
    said = _refused(_architect(night128, "bg_2"),
                    **{**_args(S196_CALL), "id": named})
    assert f"with id={free!r}, which no batch holds" in said


def test_the_free_id_skips_an_id_another_table_holds(night128):
    """Finding 5: the sandbox refuses an id that a criterion holds, so the
    free id skips it too."""
    night128.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                     "('tk1', 'i1', 'the ticket')")
    night128.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                     "('f2', 'tk1', 'a criterion')")
    night128.commit()
    said = _refused(_architect(night128, "bg_2"), **_args(S196_CALL))
    assert "with id='f3', which no batch holds" in said


def test_a_held_id_off_the_diff_gets_the_id_fix_first(night128):
    """Finding 6: two faults in one call. The id comes first, and the grain
    refusal follows on the next call with the free id."""
    sb = _architect(night128, "bg_2")
    said = _refused(sb, **{**_args(S196_CALL), "grain": "tests/test_defaults.py"})
    assert said.startswith("finding id 'f1' is held by batch bg_1")
    said = _refused(sb, **{**_args(S196_CALL), "id": "f2",
                           "grain": "tests/test_defaults.py"})
    assert said.startswith("the batch's diff does not touch 'tests/test_defaults.py'")


def test_a_directory_grain_that_holds_a_changed_file_lands(night114):
    """Finding 4: check 2 admits a directory of the diff."""
    out = _architect(night114, "bg_2").call(
        "findings.find", **{**_args(S203_CALL), "grain": "src/click"})
    assert out == {"id": "f2", "status": "satisfied"}


def test_a_directory_grain_off_the_diff_is_refused(night114):
    said = _refused(_architect(night114, "bg_2"),
                    **{**_args(S203_CALL), "grain": "src/other"})
    assert said.startswith("the batch's diff does not touch 'src/other'")


def test_k0_on_a_directory_reached_below_it_is_refused(night118):
    """Finding 1: `src/click` holds the changed `src/click/__init__.py`,
    which 11 constraints reach, so k0 on the directory is refused."""
    said = _refused(_architect(night118, "echo_json_group"),
                    **{**_args(S145_CALL), "grain": "src/click"})
    assert said.startswith("k0 is for a file that no constraint reaches, and "
                           "11 constraints reach 'src/click': ")


def test_k0_on_a_symbol_of_a_reached_file_is_refused(night118):
    """Finding 4: the symbol is judged by its file."""
    said = _refused(_architect(night118, "echo_json_group"),
                    **{**_args(S145_CALL), "grain": "src/click/__init__.py::echo"})
    assert said.startswith("k0 is for a file that no constraint reaches, and "
                           "11 constraints reach 'src/click/__init__.py': ")


def test_an_empty_diff_does_not_refuse_the_grain(tmp_path):
    """Finding 2: an empty list of files gives the seat no file to name, so
    the grain check stands down, as with no worktree."""
    conn = a_night(tmp_path, "bg_2", [], K0_ONLY)
    out = _architect(conn, "bg_2").call("findings.find", **_args(S203_CALL))
    assert out == {"id": "f2", "status": "satisfied"}


def test_a_test_file_the_seat_sees_in_the_diff_lands(tmp_path):
    """Finding 3: `code.diff` shows the batch's test file, so a grain on it
    lands, though `_diff_files` drops it as furniture."""
    conn = a_night(tmp_path, "bg_2", ["src/click/termui.py",
                                      "tests/test_defaults.py"], K0_ONLY)
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1', 'i1', 'the ticket')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('cr_1', 'tk1', 'a criterion')")
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                 "VALUES ('tst_1', 'bg_2', 'cr_1', 'tests/test_defaults.py', "
                 "'def test_x(): pass')")
    conn.commit()
    out = _architect(conn, "bg_2").call("findings.find", **_args(S203_CALL))
    assert out == {"id": "f2", "status": "satisfied"}


def test_an_untracked_file_the_seat_never_saw_is_refused(night114):
    """Finding 3: `code.diff` does not show an untracked file."""
    tree = night114.execute("SELECT worktree FROM batches WHERE id = 'bg_2'"
                            ).fetchone()[0]
    import pathlib
    (pathlib.Path(tree) / "src" / "click" / "scratch.py").write_bytes(b"y = 1\n")
    said = _refused(_architect(night114, "bg_2"),
                    **{**_args(S203_CALL), "grain": "src/click/scratch.py"})
    assert said.startswith("the batch's diff does not touch 'src/click/scratch.py'")
