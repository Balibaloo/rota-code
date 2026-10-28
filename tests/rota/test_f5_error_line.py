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


def test_the_reader_takes_the_cause_of_a_chained_raise():
    # Frame 317: night 160's tst_v6 hid its KeyError under a later error.
    assert harness.error_line(S189_CR1_RUN) == (
        "AttributeError: 'FakeStdin' object has no attribute 'readline'")


def test_a_frame_first_block_ends_at_its_own_last_e_line():
    run = FRAME_RUN + "\n\nDuring handling of the above exception, another " \
        "exception occurred:\n>       assert x\nE       assert None"
    assert harness.error_line(run) == FRAME_ERROR


def test_the_reader_takes_the_native_form():
    assert harness.error_line(NATIVE) == "ValueError: bad"
    assert harness.error_line("") == ""
    assert harness.error_line("1 passed in 0.01s") == ""


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

# A line that reads pytest's `E` marker. Only the sites below may hold one.
_E_RULE = re.compile(r"""startswith\(\s*["']E[ "']|["']\^?E\\s|["']E   ["']""")

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


def _sites(root: Path):
    for path in sorted((root / "rota").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        spans = [(n.lineno, n.end_lineno, n.name) for n in ast.walk(tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        spans += [(n.lineno, n.end_lineno, n.targets[0].id) for n in tree.body
                  if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)]
        for n, line in enumerate(text.splitlines(), 1):
            if not _E_RULE.search(line) or line.lstrip().startswith("#"):
                continue
            inner = [s for s in spans if s[0] <= n <= s[1]]
            name = min(inner, key=lambda s: s[1] - s[0])[2] if inner else ""
            yield path.relative_to(root).as_posix(), name, n


def test_no_second_reader_of_the_error_line_exists():
    root = Path(__file__).resolve().parents[2]
    found = list(_sites(root))
    assert found, "the scan finds no site, so the pattern is broken"
    extra = [f"{p}:{n} {name}" for p, name, n in found if (p, name) not in _ALLOWED]
    assert extra == [], ("a second reader of the error line: call "
                         "harness.error_line instead. " + "; ".join(extra))
