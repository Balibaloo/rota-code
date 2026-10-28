"""Frame 317, night 161 (2026-10-24): a Tester woken by an answer saw the
criteria and the Terminologist's words, and no test and no run. The runner
resolved a run only for a ref of `tests`, and an answer refs criteria only.
s364 removed s315's `package_name="click"` from tst_v6. s410 put
`package_name="test"` on a plain function (plans/night161-s309-interview.md).

The fixture holds night 161's rows in the same shape: m200 and m237, the
criteria they name, and the runs of attempts 8 and 12 word for word."""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.runner import build_prompt, resolve_inbound
from rota.core.sandbox import build
from rota.core.scheduler import Wake

C2 = "c_2_version_option_show_python_format"
C6 = "c_6_version_option_show_python_help"

# tst_v2_format at attempt 8: s309's shape, with no `package_name`.
TST_V2 = '''import sys
import click
from click.testing import CliRunner
from click.decorators import version_option


def test_version_option_show_python_format():
    @version_option(show_python=True)
    @click.command()
    def cli():
        pass
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    expected_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    assert expected_version in result.output
'''

# tst_v6_help at attempt 8: s320 kept s315's fix.
TST_V6 = '''import sys
import click
from click.testing import CliRunner
from click.decorators import version_option


def test_version_option_show_python_help():
    @version_option(show_python=True, package_name="click")
    @click.command()
    def cli_on():
        pass
    runner = CliRunner()
    result_on = runner.invoke(cli_on, ["--version"])
    expected_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    assert expected_version in result_on.output
'''

# The journal, seq 934: tst_v2_format at attempt 8.
RUN_V2 = r"""F                                                                        [100%]
================================== FAILURES ===================================
___________________ test_version_option_show_python_format ____________________

    def test_version_option_show_python_format():
        @version_option(show_python=True)
        @click.command()
        def cli():
            pass
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        expected_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
>       assert expected_version in result.output
E       assert '3.14.2' in ''
E        +  where '' = <Result RuntimeError("'test_version_option' is not installed. Try passing 'package_name' instead.")>.output

tests\test_version_option.py:14: AssertionError
------------------------ CliRunner caught an exception ------------------------
  File "src\click\core.py", line 3660, in process_value
    return super().process_value(ctx, value)
  File "src\click\core.py", line 2640, in process_value
    value = self.callback(ctx, self, value)
  File "src\click\decorators.py", line 538, in callback
    raise RuntimeError(
RuntimeError: 'test_version_option' is not installed. Try passing 'package_name' instead.
output: empty
caught by CliRunner at src\click\decorators.py:538: RuntimeError
=========================== short test summary info ===========================
FAILED tests/test_version_option.py::test_version_option_show_python_format
1 failed in 0.31s"""

# The journal, seq 938: tst_v6_help at attempt 8.
RUN_V6 = r"""F                                                                        [100%]
================================== FAILURES ===================================
____________________ test_version_option_show_python_help _____________________

    def test_version_option_show_python_help():
        @version_option(show_python=True, package_name="click")
        @click.command()
        def cli_on():
            pass
        runner = CliRunner()
        result_on = runner.invoke(cli_on, ["--version"])
        expected_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
>       assert expected_version in result_on.output
E       assert '3.14.2' in ''
E        +  where '' = <Result UnboundLocalError("cannot access local variable 'base_message' where it is not associated with a value")>.output

tests\test_version_option_help.py:14: AssertionError
------------------------ CliRunner caught an exception ------------------------
  File "src\click\core.py", line 3660, in process_value
    return super().process_value(ctx, value)
  File "src\click\core.py", line 2640, in process_value
    value = self.callback(ctx, self, value)
  File "src\click\decorators.py", line 546, in callback
    base_message += f" (Python {python_version})"
UnboundLocalError: cannot access local variable 'base_message' where it is not associated with a value
output: empty
caught by CliRunner at src\click\decorators.py:546: UnboundLocalError
=========================== short test summary info ===========================
FAILED tests/test_version_option_help.py::test_version_option_show_python_help
1 failed in 0.14s"""

# s410's tst_v6_help: two tests that decorate a plain `def`.
TST_V6_S410 = '''def test_version_message_with_show_python():
    from click.testing import CliRunner
    from click.decorators import version_option

    @version_option(show_python=True, package_name="test")
    def cmd():
        return "version: 3.10.5"

    runner = CliRunner()
    result = runner.invoke(cmd, ["--version"])
    assert "Python" in result.output


def test_version_message_without_show_python():
    # Test that when show_python is false or not passed, the version message stays exactly as it is today.
    from click.testing import CliRunner
    from click.decorators import version_option

    @version_option(show_python=False)
    def cmd():
        return "version: 3.10.5"

    runner = CliRunner()
    result = runner.invoke(cmd, ["--version"])
    assert "Python" not in result.output
'''

# The journal, seq 1110: tst_v6_help at attempt 12. The harness keeps the
# last 2000 characters, so the text starts inside a line.
RUN_V6_S410 = r'''")
                            ^^^^^^^^^^^^^^^^^^^^^^
E               KeyError: 'prog_name'

src\click\testing.py:682: KeyError

During handling of the above exception, another exception occurred:

    def test_version_message_without_show_python():
        # Test that when show_python is false or not passed, the version message stays exactly as it is today.
        from click.testing import CliRunner
        from click.decorators import version_option

        @version_option(show_python=False)
        def cmd():
            return "version: 3.10.5"

        runner = CliRunner()
>       result = runner.invoke(cmd, ["--version"])
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_version_option_help.py:24:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
C:\Users\roman\rota_n161\rota\core\plugins\_rota_caught.py:111: in invoke
    result = orig(self, *args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^
src\click\testing.py:684: in invoke
    prog_name = self.get_default_prog_name(cli)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <click.testing.CliRunner object at 0x000002700DBD1F90>
cli = <function test_version_message_without_show_python.<locals>.cmd at 0x000002700DE0C720>

    def get_default_prog_name(self, cli: Command) -> str:
        """Given a command object it will return the default program name
        for it.  The default is the `name` attribute or ``"root"`` if not
        set.
        """
>       return cli.name or "root"
               ^^^^^^^^
E       AttributeError: 'function' object has no attribute 'name'

src\click\testing.py:387: AttributeError
=========================== short test summary info ===========================
FAILED tests/test_version_option_help.py::test_version_message_with_show_python
FAILED tests/test_version_option_help.py::test_version_message_without_show_python
2 failed in 0.16s'''


@pytest.fixture
def night(tmp_path):
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
               "version) VALUES ('i1','show the Python version','in_scope',"
               "'approved',1,1)")
    for tk in ("tk_2_version_option_show_python", "tk_2"):
        db.execute("INSERT INTO tickets (id, item_id, text) VALUES (?,'i1',?)",
                   (tk, tk))
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?,?,?)",
               (C2, "tk_2_version_option_show_python",
                "The appended Python version string must be formatted as "
                "major.minor.micro using sys.version_info."))
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES (?,?,?)",
               (C6, "tk_2_version_option_show_python",
                "When show_python is true, the version message includes the "
                "appended Python version string; when show_python is false "
                "or not passed, the version message stays exactly as it is "
                "today."))
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('cr_1',"
               "'tk_2','confirm returns the default on EOF')")
    for b in ("b_3", "b_5"):
        db.execute("INSERT INTO batches (id, item_id, status) VALUES "
                   "(?,'i1','running')", (b,))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
               "('b_5','tk_2_version_option_show_python')")
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
               "('b_3','tk_2')")
    for tid, bid, cid, path, body in (
            ("tst_v2_format", "b_5", C2, "tests/test_version_option.py",
             TST_V2),
            ("tst_v6_help", "b_5", C6, "tests/test_version_option_help.py",
             TST_V6),
            ("tst_4_confirm_default_on_eof", "b_3", "cr_1",
             "tests/test_utils/test_confirm_default_on_eof.py",
             "def test_confirm():\n    assert True\n")):
        db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                   "VALUES (?,?,?,?,?)", (tid, bid, cid, path, body))
    for rid, bid, tid, result, out in (
            ("tr376", "b_5", "tst_v2_format", "fail", RUN_V2),
            ("tr380", "b_5", "tst_v6_help", "fail", RUN_V6),
            ("tr299", "b_3", "tst_4_confirm_default_on_eof", "pass",
             "1 passed in 0.10s")):
        db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
                   "result, attempt, output) VALUES (?,?,?,'a6ed3278',?,8,?)",
                   (rid, bid, tid, result, out))
    for mid, to, refs in (
            ("m200", "tester", f'["{C2}", "{C6}"]'),
            ("m200d", "developer", f'["{C2}", "{C6}"]'),
            ("m237", "tester", f'["{C6}", "cr_1"]')):
        db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, "
                   "verb, body_refs, seq) VALUES (?,'m191','terminologist',?,"
                   "'answer',?,203)", (mid, to, refs))
    db.commit()
    return db


def _user(db, role, message_id):
    wake = Wake(role=role, kind="message", message_id=message_id,
                detail="answer")
    sb = build(role, db, batch_id="b_5")
    _system, user = build_prompt(role, sb, wake, {}, "MODE: answer",
                                 resolve_inbound(db, wake))
    return user


def test_s364_sees_each_criterion_test_and_its_failed_run(night):
    user = _user(night, "tester", "m200")
    head = user.index("[last run of tst_v2_format: failed]")
    assert head < user.index("The message that woke you:")
    block = user[head:user.index("[last run of tst_v6_help")]
    assert ("is not installed. Try passing 'package_name' instead."
            in block), block
    # The body s364 removed the fix from, with the fix in it.
    v6 = user[user.index("[last run of tst_v6_help"):]
    assert '@version_option(show_python=True, package_name="click")' in v6
    # Pass 1b: a test with a block shows once, not again in the JSON.
    assert user.count("def test_version_option_show_python_format():") == 1
    assert '"tst_v2_format": {' not in user


def test_s410_sees_the_keyerror_of_tst_v6(night):
    night.execute("UPDATE tests SET body = ? WHERE id = 'tst_v6_help'",
                  (TST_V6_S410,))
    night.execute("UPDATE test_runs SET output = ?, attempt = 12 "
                  "WHERE id = 'tr380'", (RUN_V6_S410,))
    night.commit()
    user = _user(night, "tester", "m237")
    head = user.index("[last run of tst_v6_help: failed")
    block = user[head:user.index("The message that woke you:")]
    assert "KeyError: 'prog_name'" in block, block
    # Pass 1b: the tail stays 700 characters, and the raising line with its
    # two neighbours comes once before it.
    head_lines = ("                            ^^^^^^^^^^^^^^^^^^^^^^\n"
                  "E               KeyError: 'prog_name'\n...\n")
    assert head_lines + RUN_V6_S410[-700:] in block, block
    assert block.count("KeyError: 'prog_name'") == 1
    # Pass 1b: cr_1's test sits in b_3, not in the wake's batch b_5.
    assert "tst_4_confirm_default_on_eof" not in user
    assert "tst_v2_format" not in user


def test_a_test_in_the_refs_resolves_once(night):
    night.execute("UPDATE messages SET body_refs = ? WHERE id = 'm200'",
                  (f'["{C2}", "tst_v2_format"]',))
    night.commit()
    wake = Wake(role="tester", kind="message", message_id="m200",
                detail="answer")
    refs = resolve_inbound(night, wake)["resolved_refs"]
    assert list(refs) == [C2, "tst_v2_format"]
    user = _user(night, "tester", "m200")
    assert user.count("[last run of tst_v2_format") == 1


def test_a_developer_wake_on_the_same_answer_is_unchanged(night):
    wake = Wake(role="developer", kind="message", message_id="m200d",
                detail="answer")
    refs = resolve_inbound(night, wake)["resolved_refs"]
    assert list(refs) == [C2, C6]
    user = _user(night, "developer", "m200d")
    assert "[last run of" not in user and "tst_v2_format" not in user


def test_a_retired_ticket_s_test_does_not_travel(night):
    """Review 1, F2: a newer slice of the item retires the ticket, and
    `tests_missing` asks no test of it. Its test does not travel either."""
    night.execute("UPDATE tickets SET item_ver = 1 "
                  "WHERE id = 'tk_2_version_option_show_python'")
    night.execute("INSERT INTO tickets (id, item_id, text, item_ver) "
                  "VALUES ('tk_3','i1','the newer slice',2)")
    night.execute("INSERT INTO batch_tickets (batch_id, ticket_id) "
                  "VALUES ('b_5','tk_3')")
    night.commit()
    user = _user(night, "tester", "m200")
    assert "[last run of" not in user and "tst_v2_format" not in user


# Night 160, seq 243: a source line above the error holds "UsageError".
RUN_N160 = ('        original_stdin = sys.stdin\n'
            '        try:\n'
            '            sys.stdin = io.StringIO("")\n'
            '            try:\n'
            '                confirm("Are you sure?", default_on_eof=False)\n'
            '                assert False, "Expected UsageError on EOF with '
            'default_on_eof=False"\n'
            '            except Exception as e:\n'
            '>               assert "UsageError" in str(type(e)) or "EOF" in '
            'str(e), f"Unexpected error type: {type(e)}"\n'
            "E               AssertionError: Unexpected error type: "
            "<class 'click.exceptions.Abort'>\n"
            "E               assert ('UsageError' in \"<class "
            "'click.exceptions.Abort'>\" or 'EOF' in '')\n"
            + "x" * 800)


def test_the_raising_line_is_the_first_e_line_not_a_source_line():
    """Review 1, F3: the word "Error" picked the source line on night 160."""
    from rota.core.runner import _raising_line_head

    head = _raising_line_head(RUN_N160)
    lines = head.splitlines()
    assert lines[1].startswith("E               AssertionError: Unexpected")
    assert lines[0].startswith(">               assert") and lines[-1] == "..."
    # No `E ` line: the native error line (fact F5), and none inside the tail.
    native = ('Traceback (most recent call last):\n  File "r.py", line 1, in <module>\n'
              '    raise KeyError("k")\nKeyError: \'k\'\n')
    assert _raising_line_head(native + "x" * 800).startswith(
        '    raise KeyError("k")\nKeyError: \'k\'\n')
    assert _raising_line_head("x" * 800 + "\nE   KeyError: 'k'\n") == ""
