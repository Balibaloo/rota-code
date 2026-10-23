"""Frame 304, night 158 (2026-10-22): s187 re-encoded tst_confirm_eof_02 with
a `mock_open` stub. The arrange line read `.read` from a mock that `open`
specs, so the test raised before `confirm()` ran. The run stored the raise
as `fail`, and the Architect read a tail that held no test line."""
import pytest

from rota.core.runner import _resolve_refs
from rota.core.sandbox import build
from tests.rota.test_night46_context import _encode, _termui_alias_batch, db  # noqa: F401

# s187's tst_confirm_eof_02 v3, word for word from the night database.
S187_TST02 = (
    'def test_confirm_handles_eof_gracefully():\n'
    '    from click.termui import confirm\n'
    '    from unittest.mock import patch, mock_open\n'
    '    # Arrange: stdin is closed\n'
    '    with patch("sys.stdin", new_callable=mock_open) as mock_stdin:\n'
    '        mock_stdin.read.return_value = ""  # Empty read implies EOF\n'
    '        # Act\n'
    '        result = confirm(text="Proceed?", default_on_eof=True)\n'
    '        # Assert: No exception is raised; returns the default value\n'
    '        assert result is False')

# The same body with a stub whose spec holds `read`.
HOLDS_READ = S187_TST02.replace(
    '    from unittest.mock import patch, mock_open\n',
    '    from unittest.mock import patch, MagicMock\n').replace(
    '    with patch("sys.stdin", new_callable=mock_open) as mock_stdin:\n',
    '    mock_stdin = MagicMock(spec=["read", "readline"])\n'
    '    with patch("sys.stdin", mock_stdin):\n')

# The night's last run of tst_confirm_eof_02 at f7bb9d5f, word for word.
S187_RUN = r"""F                                                                        [100%]
================================== FAILURES ===================================
_____________________ test_confirm_handles_eof_gracefully _____________________

    def test_confirm_handles_eof_gracefully():
        from click.termui import confirm
        from unittest.mock import patch, mock_open
        # Arrange: stdin is closed
        with patch("sys.stdin", new_callable=mock_open) as mock_stdin:
>           mock_stdin.read.return_value = ""  # Empty read implies EOF
            ^^^^^^^^^^^^^^^

tests\test_utils\test_confirm_no_read.py:6:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <MagicMock name='open' id='1594118293552'>, name = 'read'

    def __getattr__(self, name):
        if name in {'_mock_methods', '_mock_unsafe'}:
            raise AttributeError(name)
        elif self._mock_methods is not None:
            if name not in self._mock_methods or name in _all_magics:
>               raise AttributeError("Mock object has no attribute %r" % name)
E               AttributeError: Mock object has no attribute 'read'

C:\Users\roman\AppData\Local\Python\pythoncore-3.14-64\Lib\unittest\mock.py:696: AttributeError
=========================== short test summary info ===========================
FAILED tests/test_utils/test_confirm_no_read.py::test_confirm_handles_eof_gracefully
1 failed in 0.18s"""

LABEL = "the test failed before any assertion"


def _refusal(db, body):
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError) as ex:
        _encode(sb, body)
    return str(ex.value)


def test_s187_tst02_is_refused_with_its_raising_line_named(db, tmp_path):
    _termui_alias_batch(db, tmp_path)
    msg = _refusal(db, S187_TST02)
    assert "Line 6" in msg and "mock_stdin.read" in msg, msg
    assert "before the call under test" in msg, msg
    assert "drop the spec" in msg, msg


def test_the_same_body_with_a_stub_that_holds_read_is_admitted(db, tmp_path):
    _termui_alias_batch(db, tmp_path)
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    assert _encode(sb, HOLDS_READ)["id"] == "tst_new"


def test_a_spec_resolved_in_the_sandbox_is_read_by_dir(db, tmp_path):
    """`io.StringIO` loads in the sandbox. Its `dir()` holds `read` and no
    `fetch`."""
    _termui_alias_batch(db, tmp_path)
    body = HOLDS_READ.replace(
        '    from unittest.mock import patch, MagicMock\n',
        '    import io\n    from unittest.mock import patch, MagicMock\n').replace(
        'MagicMock(spec=["read", "readline"])', 'MagicMock(spec=io.StringIO)')
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    assert _encode(sb, body)["id"] == "tst_new"
    msg = _refusal(db, body.replace("mock_stdin.read.", "mock_stdin.fetch."))
    assert "mock_stdin.fetch" in msg and "drop the spec" in msg, msg


def test_a_spec_the_sandbox_cannot_import_leaves_the_door_silent(db, tmp_path):
    _termui_alias_batch(db, tmp_path)
    (tmp_path / "wt" / "src" / "click" / "broken.py").write_text(
        "raise RuntimeError('no import')\n\n\nclass Stream:\n    pass\n")
    body = HOLDS_READ.replace(
        '    from unittest.mock import patch, MagicMock\n',
        '    from click.broken import Stream\n'
        '    from unittest.mock import patch, MagicMock\n').replace(
        'MagicMock(spec=["read", "readline"])', 'MagicMock(spec=Stream)')
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    assert _encode(sb, body)["id"] == "tst_new"


def _red_row(db, tmp_path, output):
    db.execute("UPDATE batches SET worktree = ? WHERE id = 'b1'",
               (str(tmp_path / "wt"),))
    db.execute("UPDATE criteria SET surface_refs = ? WHERE id = 'c1'",
               ('["src/click/termui.py::confirm"]',))
    db.execute("UPDATE tests SET path = ?, body = ? WHERE id = 'tst1'",
               ("tests/test_utils/test_confirm_no_read.py", S187_TST02))
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
               "result, attempt, output) VALUES ('r1','b1','tst1','abc123',"
               "'fail',1,?)", (output,))
    db.commit()
    return _resolve_refs(db, ["tst1"], role="architect",
                         detail="escalate")["tst1"]["last_run"]


def test_a_raise_in_mock_py_from_a_test_line_shows_that_line_and_the_label(db, tmp_path):
    run = _red_row(db, tmp_path, S187_RUN)
    assert run["result"] == "fail"
    tail = run["output_tail"]
    assert tail.startswith('>           mock_stdin.read.return_value = ""'), tail
    assert "Mock object has no attribute 'read'" in tail
    assert run["label"] == LABEL


def test_a_raise_inside_the_project_source_keeps_todays_tail(db, tmp_path):
    output = S187_RUN.replace(
        r"C:\Users\roman\AppData\Local\Python\pythoncore-3.14-64\Lib\unittest\mock.py:696",
        r"src\click\termui.py:5")
    run = _red_row(db, tmp_path, output)
    assert run["output_tail"] == output[-700:]
    assert "label" not in run
