"""
Frame 324, the general build: every door reads the ruled partition through
one reader, `areas.kind_of`, and the listing shows it.

Roman ruled on 2026-10-26 at 20:21 and 20:37: the fix belongs where the
seat gets its information, and the build is general. On night 167, s280's
`[code.callables]` showed `examples/termui/termui.py::clear` first with no
kind, and the seat respecified tk_3 to that full path. The partition in
`frame_rulings` marked `examples` attached and `src` program
(plans/frame324-gather-2026-10-26.md, section 1).

c_1 of night 165 and s199's turn are the red tests of pass 1, in
`test_frame324_program_rank.py`. This file holds s280's, and one test per
door where the old path pattern and the reader disagree.
"""
from __future__ import annotations

import types

import pytest

from rota.core.db import init_db
from rota.core.runner import disputed_paths
from rota.core.sandbox import build
from rota.onboarding import areas, boot
from rota.roles import api, prompts
from rota.testkit.fixtures import seed_provenance

EXAMPLE = "examples/termui/termui.py::clear"
LIBRARY = "src/click/termui.py::clear"

# s280's listing on night 167, in the index's order (the gathering record,
# section 1). Every row has a fan-in of 0.
S280_ROWS = [
    (EXAMPLE, "function"),
    ("src/click/_compat.py::_make_cached_stream_func", "function"),
    ("src/click/_compat.py::_is_jupyter_kernel_output", "function"),
    ("src/click/_compat.py::_make_text_stream", "function"),
    ("src/click/core.py::_check_iter", "function"),
    ("src/click/core.py::_FakeSubclassCheck", "class"),
    ("src/click/core.py::_check_nested_chain", "function"),
    ("src/click/decorators.py::make_pass_decorator", "function"),
    (LIBRARY, "function"),
    ("src/click/testing.py::make_input_stream", "function"),
    ("tests/test_arguments.py::test_nargs_star", "function"),
    ("tests/test_arguments.py::test_nargs_tup", "function"),
]
# m152's words, the hint of s280's wake (turn 1).
S280_HINT = ("Line 5 is wrong: the test expects a different escape sequence "
             "from the one clear already writes, and the output must not "
             "change, only the return value.")
NIGHT167_RULINGS = (("examples", "attached"), ("src", "program"),
                    ("tests", "attached"), ("docs", "attached"))


def _rule(conn, *rows):
    for prefix, kind in rows:
        conn.execute("INSERT INTO frame_rulings (id, kind) VALUES (?, ?)",
                     (prefix, kind))
    conn.commit()


def _index(conn, grains):
    for grain, sym in grains:
        path = grain.partition("::")[0]
        conn.execute("INSERT OR IGNORE INTO code_index (grain, grain_kind) "
                     "VALUES (?, 'path')", (path,))
    for grain, sym in grains:
        if "::" in grain:
            conn.execute("INSERT INTO code_index (grain, grain_kind, sym_kind, "
                         "fan_in) VALUES (?, 'symbol', ?, 0)", (grain, sym))
    conn.commit()


@pytest.fixture
def night167(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    _index(conn, S280_ROWS)
    _rule(conn, *NIGHT167_RULINGS)
    return conn


# -- the one reader -----------------------------------------------------------

def test_the_reader_reads_the_ruling_and_falls_back_to_the_heuristic(night167):
    assert areas.kind_of(night167, "examples/termui/termui.py") == "attached"
    assert areas.kind_of(night167, LIBRARY) == "program"
    # No ruling covers `scripts`, so `is_attached` decides.
    assert areas.kind_of(night167, "scripts/run.py") == "program"
    assert areas.kind_of(night167, "scripts/demo/run.py") == "attached"
    assert areas.kind_of(None, "examples/termui/termui.py") == "attached"
    _rule(night167, ("pyproject.toml", "surface"))
    assert areas.kind_of(night167, "pyproject.toml") == "surface"


def test_propose_keeps_a_judged_surface_out_of_the_areas(night167):
    """`propose` checked the value `boundary`, which `frame_rulings` cannot
    hold. A judged `surface` then fell through to the heuristic."""
    for p in ("tools/a.py", "tools/b.py", "tools/c.py"):
        night167.execute("INSERT INTO code_index (grain, grain_kind) VALUES "
                         "(?, 'path')", (p,))
    _rule(night167, ("tools", "surface"))
    assert "tools" not in set(areas.propose(night167).areas.values())


# -- s280: the listing and the probe -------------------------------------------

def _seat(conn, role="terminologist", mode="criterion_repair"):
    return build(role, conn, mode=mode, allow=prompts.mode_tools(role, mode))


def test_s280_listing_shows_the_programs_clear_first_with_its_kind(night167):
    rows = _seat(night167).call("code.callables", hint=S280_HINT)
    assert rows[0]["grain"] == LIBRARY
    assert list(rows[0]) == ["grain", "kind", "sym_kind", "fan_in"]
    assert rows[0]["kind"] == "program"
    kinds = [r["kind"] for r in rows]
    assert kinds == sorted(kinds, key=lambda k: k != "program")
    assert {r["grain"]: r["kind"] for r in rows}[EXAMPLE] == "attached"


def test_the_probe_lists_the_programs_rows_first_with_their_kind(night167):
    rows = _seat(night167, "developer", "tests_failing").call(
        "code.probe", pattern="clear")
    grains = [r["grain"] for r in rows]
    assert grains.index(LIBRARY) < grains.index(EXAMPLE)
    assert rows[0]["kind"] == "program"
    assert {r["grain"]: r["kind"] for r in rows}[EXAMPLE] == "attached"


def _tk3(night167):
    """Night 167's item, ticket tk_3 and its criterion on the library."""
    night167.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                     "version, priority) VALUES ('clear_screen', ?, 'in_scope', "
                     "'approved', 1, 1, 1)",
                     ("Make clear return whether it cleared the screen.",))
    seed_provenance(night167, "items", "clear_screen", "decided")
    night167.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                     "('tk_3', 'clear_screen', 'clear returns success')")
    night167.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                     "VALUES ('tk_3_c', 'tk_3', 'clear returns True.', ?)",
                     (f'["{LIBRARY}"]',))
    night167.commit()


def test_s280_full_example_path_is_refused_and_names_the_programs_clear(night167):
    """s280 seq 9 wrote `surface_refs=['examples/termui/termui.py::clear']`
    with a full path, and the door stored it."""
    _tk3(night167)
    with pytest.raises(ValueError) as refused:
        _seat(night167).call(
            "criteria.respecify", id="tk_3_c",
            text="When stdout is a terminal, clear() returns True.",
            surface_refs=[EXAMPLE])
    said = str(refused.value)
    assert "attached" in said and LIBRARY in said


def test_a_demo_callable_with_no_program_twin_is_not_refused_as_attached(night167):
    """The W5 read's negative: `read_config` lives in `examples/aliases`
    only, so the twin rule has nothing to offer and stays out of the way.
    Frame 215's wall decides it where a batch exists."""
    _index(night167, [("examples/aliases/aliases.py::read_config", "function")])
    _tk3(night167)
    out = _seat(night167).call(
        "criteria.respecify", id="tk_3_c",
        # Frame 202's request rule wants the new callable in backticks.
        text="When the file exists, `read_config` returns its values.",
        surface_refs=["examples/aliases/aliases.py::read_config"])
    assert out["respecified"]


def test_the_criteria_wake_names_the_programs_clear_and_keeps_testing_py(night167):
    """The review of f57eb508, finding 2: `_named_callables` decided by file
    name. On night 167 it listed the demo's `clear` first, and it dropped
    `src/click/testing.py`."""
    ctx = types.SimpleNamespace(conn=night167)
    assert api._named_callables(
        ctx, "clear returns True if it cleared the screen") == [LIBRARY]
    assert api._named_callables(ctx, "make_input_stream feeds stdin") == [
        "src/click/testing.py::make_input_stream"]
    assert api._named_callables(ctx, "test_nargs_star") == []


def test_the_one_program_door_refuses_an_import_from_the_src_folder(tmp_path):
    """The review of f57eb508, finding 1: `from src.click.termui import
    clear` beside tests that import `click` is a second name for the
    program, and d495db74 refused it. `src` is a folder, not a module."""
    root = tmp_path / "wt"
    _write(root, {"src/click/__init__.py": "", "src/click/termui.py": ""})
    conn = _encode_db(tmp_path, ["src/click/__init__.py", "src/click/termui.py"],
                      "from click.termui import clear\ndef test_c():\n"
                      "    assert clear() is None\n", worktree=root)
    said = _encode(conn, "from src.click.termui import clear\ndef test_s():\n"
                         "    assert clear() is None\n")
    assert "a second module is a second program" in said


# -- one test per door where the pattern and the reader disagree --------------

def _encode_db(tmp_path, paths, body, surface="[]", worktree=None):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1', 'charge an account', 'in_scope', "
                 "'approved', 1, 1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1', 'i1', 'charge an account')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                 "VALUES ('c1', 'tk1', 'an account is charged', '[]')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                 "VALUES ('c2', 'tk1', 'a charge is billed once', ?)", (surface,))
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit, "
                 "worktree) VALUES ('b1', 'i1', 'running', 'abc123', ?)",
                 (str(worktree) if worktree else None,))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b1', 'tk1')")
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                 "VALUES ('tst1', 'b1', 'c1', 'tests/test_charge.py', ?)", (body,))
    for p in paths:
        conn.execute("INSERT INTO code_index (grain, grain_kind) VALUES "
                     "(?, 'path')", (p,))
    conn.commit()
    return conn


def _encode(conn, body, path="tests/test_bill.py"):
    sb = build("tester", conn, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id="c2", verdict="encodable")
    try:
        sb.call("tests.encode", id="tst_new", criterion_id="c2", path=path,
                body=body)
    except Exception as e:                                   # noqa: BLE001
        return str(e)
    return ""


def _write(root, files):
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(text.encode())


def place_surface(tmp_path):
    """`_vet_surface`: a test under `test/` is attached by the reader, and the
    pattern read only the folder name `tests`."""
    conn = init_db(tmp_path / "rota.db")
    _index(conn, [("test/helpers.py::make_account", "function"),
                  ("src/bank/core.py::open_account", "function")])
    sb = build("terminologist", conn, mode="criteria")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version, priority) VALUES ('i1', 'make an account', "
                 "'in_scope', 'approved', 1, 1, 1)")
    seed_provenance(conn, "items", "i1", "decided")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('t1', 'i1', 'make_account makes an account')")
    conn.commit()
    try:
        sb.call("criteria.specify", id="c_1", ticket_id="t1", text="x",
                surface_refs=["test/helpers.py::make_account"])
    except ValueError as e:
        return "a test is not a surface" in str(e)
    return False


def place_program_path(tmp_path):
    """`_test_dirs` and `_refuse_program_path`: `src` is ruled program, so a
    test-shaped file in `src/bank` makes no test folder there."""
    conn = init_db(tmp_path / "rota.db")
    for p in ("src/bank/core.py", "src/bank/test_helpers.py",
              "tests/test_core.py"):
        conn.execute("INSERT INTO code_index (grain, grain_kind) VALUES "
                     "(?, 'path')", (p,))
    _rule(conn, ("src", "program"))
    try:
        api._refuse_program_path(conn, "src/bank/core.py")
    except ValueError:
        return True
    return False


def place_free_call_scan(tmp_path):
    """The free-call scan of `tests.encode`: an example file that reads
    input() is not the program's code."""
    root = tmp_path / "wt"
    _write(root, {"examples/demo/ask.py": "def ask():\n    return input('? ')\n",
                  "src/bank/__init__.py": ""})
    conn = _encode_db(tmp_path, ["examples/demo/ask.py", "src/bank/__init__.py"],
                      "from bank import charge\ndef test_c():\n    charge()\n",
                      worktree=root)
    said = _encode(conn, "from bank import ask\ndef test_a():\n"
                         "    assert ask() == 'y'\n")
    return "reads input() internally" not in said


def place_known_modules(tmp_path):
    """The import check of `tests.encode`: the program's package lives under
    `python/`, not `src/` or `lib/`."""
    root = tmp_path / "wt"
    _write(root, {"python/bank/__init__.py": "",
                  "python/bank/core.py": "def charge():\n    return 1\n"})
    conn = _encode_db(tmp_path, ["python/bank/__init__.py", "python/bank/core.py"],
                      "from bank.core import charge\ndef test_c():\n"
                      "    assert charge() == 1\n",
                      surface='["python/bank/core.py::charge"]', worktree=root)
    said = _encode(conn, "from bank.core import charge\ndef test_b():\n"
                         "    assert charge() == 1\n")
    return "no module of" not in said


def place_defined_in_tree(tmp_path):
    """`_defined_in_tree`: a demo's definition is no name the test reaches."""
    root = tmp_path / "wt"
    _write(root, {"examples/demo/app.py": "def charge():\n    pass\n",
                  "src/bank/core.py": "def other():\n    pass\n"})
    conn = _encode_db(tmp_path, [], "", worktree=root)
    ctx = types.SimpleNamespace(conn=conn, batch_id="b1")
    return api._defined_in_tree(ctx, "charge", "") == set()


def place_disputed(tmp_path):
    """`disputed_paths`: the record decides, and a batch with no landed
    ruling that removes a path disputes none, whatever a bare word says."""
    conn = init_db(tmp_path / "rota.db")
    _rule(conn, *NIGHT167_RULINGS)
    return disputed_paths(conn, "b1", ["examples/termui/termui.py"]) == []


def place_root_source(tmp_path):
    """`boot.stresses`: a ruled `attached` root outranks the heuristic."""
    conn = init_db(tmp_path / "rota.db")
    for i in range(21):
        conn.execute("INSERT INTO code_index (grain, grain_kind, area) VALUES "
                     "(?, 'path', '.')", (f"tool_{i}.py",))
    for i in range(21):
        _rule(conn, (f"tool_{i}.py", "attached"))
    report = types.SimpleNamespace(
        index=types.SimpleNamespace(languages={}, files=21), areas=2)
    return not any("root catch-all" in s for s in boot.stresses(conn, report))


def place_one_program(tmp_path):
    """The one-program door: `store` and `billing` are two packages of one
    program in a src layout, and neither is at the root."""
    root = tmp_path / "wt"
    _write(root, {"src/store/__init__.py": "", "src/billing/__init__.py": ""})
    conn = _encode_db(tmp_path, ["src/store/__init__.py", "src/store/core.py",
                                 "src/billing/__init__.py",
                                 "src/billing/charge.py"],
                      "from store import close_account\ndef test_c():\n"
                      "    assert close_account(1)\n", worktree=root)
    said = _encode(conn, "from billing import charge\ndef test_b():\n"
                         "    assert charge(1)\n")
    return "second program" not in said


@pytest.mark.parametrize("place", [
    place_surface, place_program_path, place_free_call_scan,
    place_known_modules, place_defined_in_tree, place_disputed,
    place_root_source, place_one_program,
], ids=lambda f: f.__name__)
def test_the_door_reads_the_reader_where_the_pattern_disagrees(tmp_path, place):
    assert place(tmp_path)
