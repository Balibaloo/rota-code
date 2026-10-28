"""Fact F5, the error line of a red run (plans/rootfix-audit-2026-10-27-a.md).

Fourteen functions read a run's output with four rules. A collection error
and a raise inside an imported file put a traceback frame first, and the
first `E ` line then named only the file and the line (frame 336, night
168's m53). A chained raise put the cause first (night 107, s151). Rule C76:
one reader, `harness.error_line`, and every reader of the line calls it.
"""
import ast
import re
from pathlib import Path
from types import SimpleNamespace

from rota.core import db as db_mod
from rota.core import harness
from rota.core.runner import _failed_before_assertion, _raising_line_head, arrange_fault
from rota.core.sandbox import _base_quote, _red_line_refusal, build
from rota.roles import api
from rota.roles.principal import _failure_line
from tests.rota.test_frame304_arrange_door import S189_CR1, S189_CR1_RUN
from tests.rota.test_night46_context import _termui_alias_batch, db  # noqa: F401

# The shape of a pytest collection error on an invalid escape (frame 335).
COLLECT = "\n".join([
    "==================================== ERRORS ====================================",
    "___________________ ERROR collecting tests/test_esc.py ___________________",
    "E     File \"C:\\w\\tests\\test_esc.py\", line 3",
    "E       x = \"\\R\"",
    "E           ^^^^",
    "E   SyntaxError: invalid escape sequence '\\R'",
    "=========================== short test summary info ===========================",
    "ERROR tests/test_esc.py",
    "1 error in 0.10s"])
COLLECT_ERROR = "SyntaxError: invalid escape sequence '\\R'"

# A test whose own line compiles a broken text: the frame comes first.
FRAME_BODY = ("def test_a():\n"
              "    x = compile(\"x = (\", \"<text>\", \"exec\")\n"
              "    assert f(x)\n")
FRAME_RUN = "\n".join([
    "_________________________________ test_a _________________________________",
    "",
    "    def test_a():",
    ">       x = compile(\"x = (\", \"<text>\", \"exec\")",
    "E         File \"<text>\", line 1",
    "E           x = (",
    "E               ^",
    "E       SyntaxError: '(' was never closed",
    "",
    "tests/test_a.py:2: SyntaxError",
    "FAILED tests/test_a.py::test_a",
    "1 failed in 0.01s"])
FRAME_ERROR = "SyntaxError: '(' was never closed"

NATIVE = "\n".join([
    "Traceback (most recent call last):",
    "  File \"C:\\w\\run.py\", line 3, in <module>",
    "    main()",
    "  File \"C:\\w\\run.py\", line 2, in main",
    "    raise ValueError(\"bad\")",
    "ValueError: bad"])


# --- the reader ---------------------------------------------------------------

def test_the_reader_takes_the_first_e_line_of_a_plain_red():
    run = "\n".join([">       assert f() == 2", "E       assert 1 == 2",
                     "E        +  where 1 = f()", "", "t.py:2: AssertionError"])
    assert harness.error_line(run) == "assert 1 == 2"


def test_the_reader_takes_the_last_e_line_of_a_collection_error():
    assert harness.error_line(COLLECT) == COLLECT_ERROR


def test_the_reader_takes_the_last_e_line_when_a_frame_comes_first():
    assert harness.error_line(FRAME_RUN) == FRAME_ERROR


def test_the_reader_takes_the_last_raise_and_carries_the_cause():
    # Frame 328, item 4: the last raise names the seat's own mistake.
    # Frame 317: the cause comes beside it.
    assert harness.error_line(S189_CR1_RUN).startswith("assert 'UsageError' in")
    assert harness.error_cause(S189_CR1_RUN) == (
        "AttributeError: 'FakeStdin' object has no attribute 'readline'")
    assert harness.error_cause(FRAME_RUN) == ""


def test_a_frame_first_block_ends_at_its_own_last_e_line():
    run = FRAME_RUN.replace("\n\ntests/test_a.py:2: SyntaxError", "\n\ntests/test_a.py:2: "
                            "SyntaxError\n\nDuring handling of the above exception, "
                            "another exception occurred:\n>       assert x\n"
                            "E       assert None")
    assert harness.error_line(run) == "assert None"
    assert harness.error_cause(run) == FRAME_ERROR


def test_the_reader_takes_the_native_form():
    assert harness.error_line(NATIVE) == "ValueError: bad"
    assert harness.error_line("") == ""
    assert harness.error_line("1 passed in 0.01s") == ""


def test_the_reader_takes_the_first_failed_test_of_two():
    two = "\n".join(["____ test_a ____", ">       assert 1 == 2", "E       assert 1 == 2",
                     "t.py:2: AssertionError", "____ test_b ____",
                     ">       assert 3 == 4", "E       assert 3 == 4", "t.py:5: AssertionError"])
    assert harness.error_line(two) == "assert 1 == 2"


# --- the recorded runs of review 1 (pytest -q --no-header --tb=auto) ----------

RUNS = Path(__file__).parent / "fixtures" / "f5_runs"


def _run(name: str) -> str:
    return (RUNS / name).read_bytes().decode("utf-8")


def test_the_recorded_runs_give_their_error_lines():
    expect = {
        "assert.out": ("AssertionError: assert {'a': 1, 'b':... 'c': 'hello'} == "
                       "{'a': 1, 'b':... 'c': 'hello'}", ""),
        "chain.out": ("app.ConfigError: the config is bad", "KeyError: 'prog_name'"),
        "chain2.out": ("AssertionError: the fallback must hold 5", "KeyError: 'missing'"),
        "collect.out": ("ModuleNotFoundError: No module named 'nosuchmodule_xyz'", ""),
        "syntax.out": ("SyntaxError: '(' was never closed", ""),
        "fixture.out": ("KeyError: 'host'", ""),
        "internal.out": ("RuntimeError: the hook broke", ""),
        "conf.err": ("ModuleNotFoundError: No module named 'nosuch_conf_mod'", ""),
    }
    got = {n: (harness.error_line(_run(n)), harness.error_cause(_run(n))) for n in expect}
    assert got == expect


def test_a_fixture_error_never_gives_the_progress_line():
    """Review 1, finding 1: a one-test file that errors in a fixture
    prints `E` and `[100%]` first."""
    run = _run("fixture.out")
    assert db_mod._first_error(run) == "KeyError: 'host'"
    assert _failure_line(run) == "KeyError: 'host'"
    assert _base_quote(run) == "KeyError: 'host'"
    long = run.replace("test_f.py:6: KeyError", "\n".join(
        f"log line {n:04d}" for n in range(300)) + "\ntest_f.py:6: KeyError")
    assert harness.error_line(harness._tail(long)) == "KeyError: 'host'"


def test_a_caught_raise_then_a_failed_assert_gives_the_assert():
    """Review 1, finding 2: every reader names the last raise."""
    run = _run("chain2.out")
    said = "AssertionError: the fallback must hold 5"
    assert db_mod._first_error(run) == said
    assert _failure_line(run) == said
    assert _base_quote(run) == said
    reds = api._own_reds("", "test_c2.py", run)
    assert [r["error"] for r in reds] == [said]


def test_the_raise_from_run_gives_one_line_to_every_reader():
    """Review 1, finding 3: the check row and the encode note named two
    errors for one run."""
    run = _run("chain.out")
    said = "app.ConfigError: the config is bad"
    assert _failure_line(run) == said
    assert [r["error"] for r in api._own_reds("", "test_c.py", run)] == [said]


def test_the_head_shows_the_cause_and_the_last_raise_outside_the_tail():
    run = _run("chain2.out").replace("test_c2.py:6: AssertionError", "\n".join(
        f"log line {n:04d}" for n in range(80)) + "\ntest_c2.py:6: AssertionError")
    head = _raising_line_head(run)
    assert head.index("KeyError: 'missing'") < head.index("AssertionError: the fallback")


def test_tail_keeps_the_cause_and_the_last_raise():
    run = _run("chain.out").replace("test_c.py:4: ", "\n".join(
        f"log line {n:04d}" for n in range(300)) + "\ntest_c.py:4: ")
    cut = harness._tail(run)
    assert harness.error_line(cut) == "app.ConfigError: the config is bad"
    assert harness.error_cause(cut) == "KeyError: 'prog_name'"


def test_an_internal_error_gives_its_raise():
    """Review 1, finding 5: each frame carries the `INTERNALERROR>` mark."""
    run = _run("internal.out")
    assert "the hook broke" in _raising_line_head(run + "\n" + "x" * 800)


# --- one test per moved reader, red on the parent ----------------------------

def test_first_error_reads_the_error_of_a_collection_error():
    assert db_mod._first_error(COLLECT) == COLLECT_ERROR


def test_tail_keeps_a_native_error_that_the_cut_drops():
    text = NATIVE + "\n" + "\n".join(f"log line {n:04d}" for n in range(400))
    assert "ValueError: bad" in harness._tail(text)
    assert harness.error_line(harness._tail(text)) == "ValueError: bad"


def test_tail_keeps_the_error_line_of_a_long_collection_error():
    text = COLLECT.replace("E     File", "\n".join(
        f"src/m.py:{n}: in <module>" for n in range(300)) + "\nE     File")
    assert harness.error_line(harness._tail(text, 500)) == COLLECT_ERROR


def test_raising_line_head_shows_the_error_of_a_collection_error():
    run = COLLECT + "\n" + "\n".join(f"log line {n:04d}" for n in range(80))
    assert "SyntaxError" in _raising_line_head(run)


def test_arrange_fault_quotes_the_error_under_the_frame():
    fault = arrange_fault(FRAME_BODY, "tests/test_a.py", FRAME_RUN, {"f"})
    assert fault and fault["rule"] == "arrange"
    assert fault["error"] == FRAME_ERROR


def test_failed_before_assertion_reads_the_last_section():
    # The reader and the old rule agree on every real form, so this pins it.
    assert _failed_before_assertion(S189_CR1, S189_CR1_RUN) is False


def test_base_quote_reads_the_error_of_a_collection_error():
    assert _base_quote(COLLECT) == COLLECT_ERROR


def test_own_reds_quote_the_error_under_the_frame():
    reds = api._own_reds(FRAME_BODY, "tests/test_a.py", FRAME_RUN)
    assert [r["error"] for r in reds] == [FRAME_ERROR]


def test_the_collection_note_quotes_the_error():
    notes = []
    ctx = SimpleNamespace()
    api._note_collection_error(ctx, "b1", "c1", "tests/test_esc.py", COLLECT, notes)
    assert f"`{COLLECT_ERROR}`" in notes[0]


def test_failure_line_reads_the_error_of_a_collection_error():
    # Frame 336 gave this reader the rule first, so this pins it.
    assert _failure_line(COLLECT) == COLLECT_ERROR.removesuffix(".")


def test_red_line_refusal_names_the_error_under_the_frame(db, tmp_path):
    _termui_alias_batch(db, tmp_path)
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst_a','b1','c1','tests/test_a.py',?)", (FRAME_BODY,))
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
               "result, output, attempt) VALUES ('tr1','b1',"
               "'tst_a','abc123','fail',?,1)", (FRAME_RUN,))
    db.commit()
    ctx = build("developer", db, batch_id="b1", mode="tests_failing").ctx
    said = _red_line_refusal(ctx, ["tst_a"], "f takes the compiled text")
    assert f"`{FRAME_ERROR}`" in said


def test_the_unchanged_note_quotes_the_error_under_the_frame(db, tmp_path):
    import subprocess
    root = tmp_path / "wt"; root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "m.py").write_bytes(b"def f(x):\n    return x\n")
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t",
                    "commit", "-q", "-m", "a"], check=True)
    sha = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                         capture_output=True, text=True, check=True).stdout.strip()
    db.execute("UPDATE batches SET worktree = ?, head_commit = ? WHERE id = 'b1'",
               (str(root), sha))
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, "
               "attempt, output) VALUES ('r1','b1','tst1',?,'fail',1,?)", (sha, FRAME_RUN))
    db.commit()
    ctx = SimpleNamespace(conn=db, batch_id="b1")
    note = api._unchanged_note(ctx, root, "m.py", [])
    assert f"pytest said `{FRAME_ERROR}`" in note


# --- the one-reader property ---------------------------------------------------

# A string that a search for the error line holds: a traceback word, an
# exception's `Error:`, or pytest's `E` marker as text or as a regex.
_MARK = re.compile(r"Traceback|Error:|^\^?E(?:\s|\\s|\+| \+)")
_STR_SEARCH = {"startswith", "endswith", "find", "rfind", "index", "rindex",
               "count", "split", "rsplit", "partition", "rpartition"}
_RE_CALL = {"match", "search", "fullmatch", "findall", "finditer", "compile",
            "sub", "subn", "split"}

# Each site names its file and its function or its module-level name.
_ALLOWED = {
    # The one reader of the error line.
    ("rota/core/harness.py", "_E_LINE"),
    ("rota/core/harness.py", "_E_FRAME"),
    # A search of every `E` line for one fixed shape of error, not the
    # error line. Night 159's chained run caught the stub's error.
    ("rota/core/runner.py", "_STUB_ERROR"),
    ("rota/core/runner.py", "_MISSING_ARGS"),
    # The source line under a collection error's frame, not the error line.
    ("rota/roles/api.py", "_note_collection_error"),
    # Every `>` and `E` line, the view that a quote may hold.
    ("rota/core/sandbox.py", "_run_view"),
}


def _strings(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        yield node.value
    elif isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        for elt in node.elts:
            yield from _strings(elt)


def _searched(node):
    """The strings that `node` searches a text for."""
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        name = node.func.attr
        on_re = isinstance(node.func.value, ast.Name) and node.func.value.id == "re"
        if name in _STR_SEARCH or (on_re and name in _RE_CALL):
            for arg in node.args[:1]:
                yield from _strings(arg)
    elif isinstance(node, ast.Compare) and any(
            isinstance(op, (ast.In, ast.NotIn, ast.Eq, ast.NotEq)) for op in node.ops):
        for side in [node.left, *node.comparators]:
            yield from _strings(side)


def _sites(root: Path):
    """Each search for the error line under root/rota: file, owner, line."""
    for path in sorted((root / "rota").rglob("*.py")):
        tree = ast.parse(path.read_bytes().decode("utf-8"))
        owners = [(n, n.name) for n in ast.walk(tree)
                  if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        owners += [(n, n.targets[0].id) for n in tree.body
                   if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)]
        for node in ast.walk(tree):
            if not any(_MARK.search(s) for s in _searched(node)):
                continue
            inner = [(o, nm) for o, nm in owners if o.lineno <= node.lineno <= o.end_lineno]
            name = min(inner, key=lambda x: x[0].end_lineno - x[0].lineno)[1] if inner else ""
            yield path.relative_to(root).as_posix(), name, node.lineno


def test_no_second_reader_of_the_error_line_exists():
    root = Path(__file__).resolve().parents[2]
    found = list(_sites(root))
    assert found, "the scan finds no site, so the scan is broken"
    extra = [f"{p}:{n} {name}" for p, name, n in found if (p, name) not in _ALLOWED]
    assert extra == [], ("a second reader of the error line: call "
                         "harness.error_line instead. " + "; ".join(extra))


def test_the_scan_finds_the_six_shapes_of_review_1(tmp_path):
    """Review 1, finding 4: the line scan found 1 of these 6 readers."""
    (tmp_path / "rota").mkdir()
    (tmp_path / "rota" / "fake.py").write_bytes("\n".join([
        "import re",
        "def a(lines): return [ln for ln in lines if 'Traceback' in ln]",
        "def b(lines): return [ln for ln in lines if re.match(r'[A-Za-z.]+Error: ', ln)]",
        "def c(lines): return [ln for ln in lines if ln[:2] == 'E ']",
        "def d(lines): return [ln for ln in lines if ln.startswith(('E ', 'X'))]",
        "def e(lines): return [ln for ln in lines if re.match('E +[^ ]', ln)]",
        "def f(lines): return [ln for ln in lines if ln.startswith('E ')]",
        ""]).encode("utf-8"))
    assert sorted(name for _p, name, _n in _sites(tmp_path)) == list("abcdef")


