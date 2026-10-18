"""
Frame 143: a door on `tests.encode` names a literal Python version back.

Night 156's Tester s292 read a criterion that says the version comes from
`sys.version_info` at runtime. It restated the rule, then asserted
`endswith("Python 3.10.0")`. The interview showed that a question that
named the literal moved the seat in one turn. So the door quotes the
literal and the criterion's words, and names `sys.version_info`.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build

ENV_TEXT = ("When the show_python flag is turned on, the Python version "
            "appended to the --version output is determined by inspecting "
            "sys.version_info at runtime.")


def _db(tmp_path, criterion_text):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, "
                 "approval_ver, version) VALUES ('i1','x','in_scope',"
                 "'approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('t1','i1','y')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('ver_opt_show_py_env','t1',?)", (criterion_text,))
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES "
                 "('b1','i1','running')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b1','t1')")
    conn.commit()
    return conn


def _encode(conn, body):
    sb = build("tester", conn, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id="ver_opt_show_py_env",
            verdict="encodable")
    return sb.call("tests.encode", id="ver_opt_show_py_env_test_fixed",
                   criterion_id="ver_opt_show_py_env",
                   path="tests/test_version_option_with_show_python_flag_source.py",
                   body=body)


# s292's turn 1 body for the criterion that names sys.version_info, as the
# night recorded it (`.rota/clickI_night156.db`, `turns`, s292 seq 1).
S292_BODY = '''def test_version_option_source_without_flag():
    from click.testing import CliRunner
    from src.click.decorators import version_option

    @version_option()
    def cli():
        pass

    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    # Without flag, no "Python X.Y.Z" appended
    assert "Python 3.10.0" not in result.output or result.output == "Python 3.10.0"

def test_version_option_source_with_flag():
    from click.testing import CliRunner
    from src.click.decorators import version_option

    @version_option(show_python=True)
    def cli():
        pass

    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    # With flag, output MUST end with "Python X.Y.Z" derived from sys.version_info
    assert result.output.endswith("Python 3.10.0")
'''

# The body s292 wrote once the interview named the literal (answer 2).
RIGHT_BODY = '''import sys
from click.testing import CliRunner
from src.click.decorators import version_option

def test_version_option_source_with_flag():
    @version_option(show_python=True)
    def cli():
        pass

    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    expected = f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    assert result.output.endswith(expected)
'''


def test_s292_literal_version_is_refused(tmp_path):
    conn = _db(tmp_path, ENV_TEXT)
    with pytest.raises(ValueError) as exc:
        _encode(conn, S292_BODY)
    text = str(exc.value)
    assert "the literal '3.10.0'" in text, text
    assert ENV_TEXT in text, text
    assert "Build the expected string from sys.version_info" in text, text
    assert "{sys.version_info.major}" in text, text


def test_a_literal_through_a_name_is_refused(tmp_path):
    conn = _db(tmp_path, ENV_TEXT)
    body = RIGHT_BODY.replace(
        'f"Python {sys.version_info.major}.{sys.version_info.minor}.'
        '{sys.version_info.micro}"', '"Python 3.10.0"')
    with pytest.raises(ValueError, match="the literal '3.10.0'"):
        _encode(conn, body)


def test_a_body_that_builds_from_sys_version_info_is_admitted(tmp_path):
    conn = _db(tmp_path, ENV_TEXT)
    assert _encode(conn, RIGHT_BODY) == {"id": "ver_opt_show_py_env_test_fixed"}


def test_a_literal_the_criterion_gives_is_admitted(tmp_path):
    # The criterion names the source and gives the value itself, so the
    # literal is the criterion's own and the test may assert it.
    text = (ENV_TEXT + " On the reference host the output ends with "
            "\"Python 3.10.0\".")
    conn = _db(tmp_path, text)
    body = S292_BODY.replace(
        '    assert "Python 3.10.0" not in result.output or '
        'result.output == "Python 3.10.0"\n',
        '    assert "Python" not in result.output\n')
    assert _encode(conn, body) == {"id": "ver_opt_show_py_env_test_fixed"}


def test_a_criterion_that_names_no_source_is_untouched(tmp_path):
    # Frame 147: the encode doors refuse too much, so a criterion that does
    # not name the interpreter as the source keeps the door shut.
    conn = _db(tmp_path, "The --version output ends with the Python version.")
    body = RIGHT_BODY.replace(
        'f"Python {sys.version_info.major}.{sys.version_info.minor}.'
        '{sys.version_info.micro}"', '"Python 3.10.0"')
    assert _encode(conn, body) == {"id": "ver_opt_show_py_env_test_fixed"}
