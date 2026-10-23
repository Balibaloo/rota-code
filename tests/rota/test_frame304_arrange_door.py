"""Frame 304, pass 2, night 159 (2026-10-23): bg_2's tests failed on a plain
`FakeStdin` class with no `readline` and on `confirm()` with no `text`.
Pass 1's door read a mock's spec only, and it fired 0 times. The challenge
door refused s185, the one Developer that named the stub. The rule: a red
test whose run never reaches an assertion of the surface's result cannot be
passed by any code. So the door at encode reads the body's run."""
import ast

import pytest

from rota.core.runner import arrange_fault
from rota.core.sandbox import _red_line_refusal, build
from rota.roles import api
from tests.rota.test_frame304_arrange_raises import S187_RUN, S187_TST02
from tests.rota.test_night46_context import _encode, _termui_alias_batch, db  # noqa: F401

# Word for word from .rota/clickI_night159.db: s189's turn 1 `tests.load`
# row of tst_cr1_default_off, its body and its run, and s185's first call.
S189_CR1 = 'from click.termui import confirm\nimport sys\n\ndef test_default_on_eof_is_off_by_default():\n    # default_on_eof should be off by default\n    # When stdin is closed and flag is False, it should abort (raise UsageError)\n    original_stdin = sys.stdin\n    class FakeStdin:\n        def isatty(self):\n            return False\n        @property\n        def closed(self):\n            return True\n    sys.stdin = FakeStdin()\n    \n    try:\n        confirm(text="yes", default="yes", default_on_eof=False)\n        assert False, "Should have raised UsageError"\n    except Exception as e:\n        # Should raise UsageError when stdin is closed and flag is off\n        assert "UsageError" in str(type(e))'
S189_CR1_RUN = '"""\n        stream = sys.stderr if err else sys.stdout\n    \n        # Look up ``should_strip_ansi`` on the module so that ``CliRunner``,\n        # which patches it there during test isolation, is honored.\n        if _compat.should_strip_ansi(stream, resolve_color_default()):\n            text = strip_ansi(text)\n    \n        if err:\n            with redirect_stdout(sys.stderr):\n                return func(text)\n        try:\n>           return func(text)\n                   ^^^^^^^^^^\nE           AttributeError: \'FakeStdin\' object has no attribute \'readline\'\n\nsrc\\click\\termui.py:106: AttributeError\n\nDuring handling of the above exception, another exception occurred:\n\n    def test_default_on_eof_is_off_by_default():\n        # default_on_eof should be off by default\n        # When stdin is closed and flag is False, it should abort (raise UsageError)\n        original_stdin = sys.stdin\n        class FakeStdin:\n            def isatty(self):\n                return False\n            @property\n            def closed(self):\n                return True\n        sys.stdin = FakeStdin()\n    \n        try:\n            confirm(text="yes", default="yes", default_on_eof=False)\n            assert False, "Should have raised UsageError"\n        except Exception as e:\n            # Should raise UsageError when stdin is closed and flag is off\n>           assert "UsageError" in str(type(e))\nE           assert \'UsageError\' in "<class \'AttributeError\'>"\nE            +  where "<class \'AttributeError\'>" = str(<class \'AttributeError\'>)\nE            +    where <class \'AttributeError\'> = type(AttributeError("\'FakeStdin\' object has no attribute \'readline\'"))\n\ntests\\test_utils\\test_confirm_default_off.py:21: AssertionError\n---------------------------- Captured stdout call -----------------------------\nyes [Y/n]: \n=========================== short test summary info ===========================\nFAILED tests/test_utils/test_confirm_default_off.py::test_default_on_eof_is_off_by_default\n1 failed in 0.14s'
S185_CALL = 'TOOL: msg.challenge_tester(refs=[\'cr_1_confirm_default_on_eof\', \'tst_cr1_default_off\'], quotes=["confirm() has a \'default_on_eof\' boolean flag which is off by default. When True and stdin is closed, confirm() returns its own default value (or the sentinel if none configured) instead of aborting or blocking.", "class FakeStdin:\\n            def isatty(self):\\n                return False\\n            @property\\n            def closed(self):\\n                return True\\n        sys.stdin = FakeStdin()\\n        confirm(text=\\"yes\\", default=\\"yes\\", default_on_eof=False)"], reason="The test\'s FakeStdin mock lacks the \'readline\' method required by confirm()\'s implementation, causing an AttributeError before the criterion\'s behavior can be tested. The test does not encode its criterion because it fails at a lower level (mock incompleteness).")'
CR1_TEXT = "confirm() has a 'default_on_eof' boolean flag which is off by default. When True and stdin is closed, confirm() returns its own default value instead of aborting or blocking."
S185_CR4 = 'from click.termui import confirm\nimport sys\n\ndef test_returns_own_default_when_stdin_closed():\n    # confirm is a plain function with its own default argument\n    class FakeStdin:\n        def isatty(self):\n            return False\n        @property\n        def closed(self):\n            return True\n    sys.stdin = FakeStdin()\n    \n    # When default_on_eof=True and stdin is closed, returns own default\n    result = confirm(default="yes", default_on_eof=True)\n    assert result == "yes"'
S185_CR4_RUN = 'F                                                                        [100%]\n================================== FAILURES ===================================\n_________________ test_returns_own_default_when_stdin_closed __________________\n\n    def test_returns_own_default_when_stdin_closed():\n        # confirm is a plain function with its own default argument\n        class FakeStdin:\n            def isatty(self):\n                return False\n            @property\n            def closed(self):\n                return True\n        sys.stdin = FakeStdin()\n    \n        # When default_on_eof=True and stdin is closed, returns own default\n>       result = confirm(default="yes", default_on_eof=True)\n                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nE       TypeError: confirm() missing 1 required positional argument: \'text\'\n\ntests\\test_utils\\test_confirm_plain.py:15: TypeError\n=========================== short test summary info ===========================\nFAILED tests/test_utils/test_confirm_plain.py::test_returns_own_default_when_stdin_closed\n1 failed in 0.14s'

# s185's msg.challenge_tester on tst_cr1, its arguments as the night stored
# them.
S185_ARGS = {k.arg: ast.literal_eval(k.value) for k in ast.parse(
    S185_CALL[len("TOOL: msg."):]).body[0].value.keywords}


def _git_batch(db, tmp_path):
    _termui_alias_batch(db, tmp_path)
    (tmp_path / "wt" / ".git").mkdir()


def _ran(monkeypatch, output, verdict="fail"):
    seen = []

    def fake(ctx, root, path, body):
        seen.append(path)
        return verdict, output
    monkeypatch.setattr(api, "_encode_run", fake)
    return seen


def _encode_at(sb, path, body):
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    return sb.call("tests.encode", id="tst_new", criterion_id="c1",
                   path=path, body=body)


def test_s189_tst_cr1_lands_with_a_note_on_its_minimal_stub(
        db, tmp_path, monkeypatch):
    """Review 2, finding 2: a right test can hold a minimal stub on purpose,
    so the stub is a note and the body lands."""
    _git_batch(db, tmp_path)
    seen = _ran(monkeypatch, S189_CR1_RUN)
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    out = _encode_at(sb, "tests/test_utils/test_confirm_default_off.py", S189_CR1)
    assert seen and out["id"] == "tst_new"
    note = out["note"]
    assert "Line 8, `class FakeStdin:`" in note
    assert "`readline`" in note
    assert "the code may need to read" in note


def test_a_body_local_import_of_a_name_the_item_names_lands(
        db, tmp_path, monkeypatch):
    """Review 2, finding 1: the batch adds `echo_pretty`, so a test that
    imports it inside its body is right before the Developer writes it."""
    _git_batch(db, tmp_path)
    path = "tests/test_pretty.py"
    body = ("def test_x():\n    from click.utils import echo_pretty\n"
            "    assert echo_pretty('a') == 'a'\n")
    run = ("    def test_x():\n>       from click.utils import echo_pretty\n"
           "E       ImportError: cannot import name 'echo_pretty' from "
           "'click.utils'\n\ntests\\test_pretty.py:2: ImportError\n"
           "1 failed in 0.1s")
    _ran(monkeypatch, run)
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    # Pass 2c: a failed import line is no fault of the test, so the body
    # lands although no row of the batch names the name.
    assert api._arrange_run_refusal(sb.ctx, "b1", "c1", path, body) is None
    db.execute("UPDATE items SET text = 'add echo_pretty to click.utils' "
               "WHERE id = 'i1'")
    db.commit()
    assert api._arrange_run_refusal(sb.ctx, "b1", "c1", path, body) is None


def _import_run(path, line):
    return (f"    def test_close():\n>       {line}\n"
            "E       ModuleNotFoundError: No module named 'billing'\n\n"
            f"{path.replace('/', chr(92))}:2: ModuleNotFoundError\n"
            "1 failed in 0.1s")


@pytest.mark.parametrize("line", [
    "from billing.accounts import close_account",
    "import billing_compat",
])
def test_a_failed_import_line_lands_whatever_the_name(
        db, tmp_path, monkeypatch, line):
    """Pass 2c, the L1 case encode-a-criterion-the-principal-corrected: the
    seat imports a module that the head lacks. The Developer or an install
    adds the module, and the same import at module level is a collection
    error where the door is silent. So the import line lands, with no
    note, whether or not a row names the module."""
    _git_batch(db, tmp_path)
    path = "tests/test_close.py"
    body = (f"def test_close():\n    {line}\n"
            "    assert close_account(1) is None\n")
    run = _import_run(path, line)
    assert arrange_fault(body, path, run, {"close_account"}, "",
                         str(tmp_path / "wt")) is None
    _ran(monkeypatch, run)
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    notes = []
    assert api._arrange_run_refusal(sb.ctx, "b1", "c1", path, body,
                                    notes) is None
    assert notes == []


def test_s185_challenge_that_quotes_the_stub_is_admitted(db, tmp_path):
    _termui_alias_batch(db, tmp_path)
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst_cr1_default_off','b1','c1',"
               "'tests/test_utils/test_confirm_default_off.py',?)", (S189_CR1,))
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
               "result, output, attempt) VALUES ('tr1','b1',"
               "'tst_cr1_default_off','abc123','fail',?,1)", (S189_CR1_RUN,))
    db.commit()
    ctx = build("developer", db, batch_id="b1", mode="tests_failing").ctx
    refs = ["c1", "tst_cr1_default_off"]
    assert _red_line_refusal(ctx, refs, " ... ".join(S185_ARGS["quotes"])) is None
    # A quote of the criterion alone still misses the line the run fails at.
    said = _red_line_refusal(ctx, refs, S185_ARGS["quotes"][0])
    assert said and "names the line it fails at" in said


def test_night158_tst02_v3_is_refused_by_its_run(db, tmp_path, monkeypatch):
    _git_batch(db, tmp_path)
    path = "tests/test_utils/test_confirm_no_read.py"
    fault = arrange_fault(S187_TST02, path, S187_RUN, {"confirm"}, "",
                          str(tmp_path / "wt"))
    assert fault["rule"] == "arrange" and fault["line"] == 6
    _ran(monkeypatch, S187_RUN)
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    said = api._arrange_run_refusal(sb.ctx, "b1", "c1", path, S187_TST02)
    assert said.startswith("The run of this body on the batch's head raises "
                           "at line 6, `mock_stdin.read.return_value = \"\"  "
                           "# Empty read implies EOF`")
    assert "The test fails in its own arrange step, and no code can pass it." in said


ASSERTS = ("from click.utils import shout\n\n\ndef test_x():\n"
           "    assert shout('ok') == 'OK'\n")


def _shout_batch(db, tmp_path):
    # A surface that reads no stdin, so the stdin door stays silent.
    _git_batch(db, tmp_path)
    (tmp_path / "wt" / "src" / "click" / "utils.py").write_text(
        "def shout(text):\n    return text\n")
    db.execute("UPDATE criteria SET surface_refs = ? WHERE id = 'c1'",
               ('["src/click/utils.py::shout"]',))
    db.commit()


def test_a_test_that_fails_on_an_assertion_is_admitted(db, tmp_path, monkeypatch):
    _shout_batch(db, tmp_path)
    run = ("    def test_x():\n>       assert shout('ok') == 'OK'\n"
           "E       AssertionError: assert 'ok' == 'OK'\n\n"
           "tests\\test_greet.py:5: AssertionError\n1 failed in 0.1s")
    seen = _ran(monkeypatch, run)
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    assert _encode(sb, ASSERTS)["id"] == "tst_new"
    assert seen == ["tests/test_greet.py"]


def test_a_test_that_raises_inside_the_project_code_is_admitted(
        db, tmp_path, monkeypatch):
    _shout_batch(db, tmp_path)
    run = ("    def test_x():\n>       assert shout('ok') == 'OK'\n\n"
           "tests\\test_greet.py:5: \n_ _ _ _\n\n"
           "    def shout(text):\n"
           ">       return text.uper()\n"
           "E       AttributeError: 'str' object has no attribute 'uper'\n\n"
           "src\\click\\utils.py:2: AttributeError\n1 failed in 0.1s")
    _ran(monkeypatch, run)
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    assert _encode(sb, ASSERTS)["id"] == "tst_new"


def test_a_call_with_no_required_argument_is_refused_unless_the_criterion_names_it():
    path = "tests/test_utils/test_confirm_plain.py"
    fault = arrange_fault(S185_CR4, path, S185_CR4_RUN, {"confirm"}, CR1_TEXT)
    assert fault["rule"] == "signature" and fault["attr"] == ["text"]
    assert fault["quote"] == 'result = confirm(default="yes", default_on_eof=True)'
    assert arrange_fault(S185_CR4, path, S185_CR4_RUN, {"confirm"},
                         "confirm() takes no text, and text defaults to ''") is None


def test_the_door_runs_the_body_on_the_head_and_leaves_no_file(db, tmp_path):
    """One real run: the body raises TypeError at the surface call."""
    root = tmp_path / "wt"
    (root / ".git").mkdir(parents=True)
    (root / "src" / "askpkg").mkdir(parents=True)
    (root / "src" / "askpkg" / "__init__.py").write_text("")
    (root / "src" / "askpkg" / "termui.py").write_text(
        "def confirm(text, default=None, default_on_eof=False):\n"
        "    return default\n")
    (root / "pyproject.toml").write_text(
        "[tool.pytest.ini_options]\npythonpath = [\"src\"]\n")
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'", (str(root),))
    db.execute("UPDATE criteria SET surface_refs = ? WHERE id = 'c1'",
               ('["src/askpkg/termui.py::confirm"]',))
    db.commit()
    body = ("from askpkg.termui import confirm\n\n\ndef test_x():\n"
            "    result = confirm(default=True, default_on_eof=True)\n"
            "    assert result is True\n")
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    said = api._arrange_run_refusal(sb.ctx, "b1", "c1", "tests/test_ask.py", body)
    assert said and "line 5" in said and "missing 1 required positional" in said
    assert not (root / "tests" / "test_ask.py").exists()
