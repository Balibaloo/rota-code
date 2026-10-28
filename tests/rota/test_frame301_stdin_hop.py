"""Frame 301, night 157 (2026-10-21): the Tester wrote the right test for
bg_1's `default_on_eof` criterion twice, and the stdin door of
`tests.encode` refused it six times with an offer of the shape the body
already had."""
import pytest

from rota.core.sandbox import build
from rota.roles.api import _INVOKE_ROUTE
from tests.rota.test_night46_context import _encode, _termui_alias_batch, db  # noqa: F401

STDIN = "where stdin is captured"

# s266's turn 4 body, word for word. It uses `click.command` and imports no
# `click`, so `click` is unbound when the test runs.
S266_TURN4 = (
    'def test_default_on_eof_returns_true():\n'
    '    from click.testing import CliRunner\n'
    '    from click.termui import confirm\n'
    '    @click.command()\n'
    '    def cli_main():\n'
    '        confirm("test", default=True, default_on_eof=True)\n'
    '    runner = CliRunner()\n'
    '    result = runner.invoke(cli_main, input="")\n'
    '    assert result.exit_code == 0\n'
    '    assert result.output.endswith("True")')

# s258's turn 3 body of `tst_confirm_eof`, word for word. The command `cmd`
# calls the helper `confirm_cmd`, and the helper calls confirm().
S258_TURN3 = (
    'import click\n'
    'from click.testing import CliRunner\n'
    '\n'
    'def confirm_cmd():\n'
    '    from src.click.termui import confirm\n'
    '    return confirm("Test", default=True, default_on_eof=True)\n'
    '\n'
    '@click.command()\n'
    'def cmd():\n'
    '    confirm_cmd()\n'
    '\n'
    'def test_default_on_eof_flag():\n'
    '    runner = CliRunner()\n'
    '    result = runner.invoke(cmd, input="")\n'
    '    assert result.exit_code == 0\n'
    '    assert "True" in result.output\n'
    '\n'
    'def test_default_on_eof_off_aborts():\n'
    '    from src.click.termui import confirm\n'
    '    @click.command()\n'
    '    def cmd_abort():\n'
    '        confirm("Test", default=False, default_on_eof=False)\n'
    '    runner = CliRunner()\n'
    '    result = runner.invoke(cmd_abort, input="")\n'
    '    assert result.exit_code == 2')


def _refusal(db, body):
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    with pytest.raises(ValueError) as ex:
        _encode(sb, body)
    return str(ex.value)


def test_a_body_that_never_imports_click_is_told_so_before_the_stdin_text(db, tmp_path):
    """s266 turn 4: the stdin text offered the shape the body had. The fault
    is the unbound `click`, so the NameError guard speaks first."""
    _termui_alias_batch(db, tmp_path)
    msg = _refusal(db, S266_TURN4)
    assert "click" in msg and "never imports" in msg, msg
    assert STDIN not in msg, msg
    assert _INVOKE_ROUTE not in msg, msg


def test_the_same_body_with_import_click_is_admitted(db, tmp_path):
    _termui_alias_batch(db, tmp_path)
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    assert _encode(sb, "import click\n" + S266_TURN4)["id"] == "tst_new"


def test_a_prompt_in_a_helper_that_the_command_calls_is_admitted(db, tmp_path):
    """s258 turn 3: the helper runs inside the runner's isolation, so its
    confirm() reads the runner's stream."""
    _termui_alias_batch(db, tmp_path)
    # The body imports the surface from `src.click.termui`. The surface door
    # refuses that import, a fault of its own that the stdin text hid.
    msg = _refusal(db, S258_TURN3)
    assert STDIN not in msg, msg
    assert "`from click.termui import confirm`" in msg, msg
    # With the surface's own module, the body is admitted.
    fixed = S258_TURN3.replace("from src.click.termui import", "from click.termui import")
    assert fixed.count("from click.termui import") == 2
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    assert _encode(sb, fixed)["id"] == "tst_new"


def test_a_prompt_in_a_helper_the_command_does_not_call_names_the_helper(db, tmp_path):
    """The body has the invoke shape, so the route is no step. The refusal
    names the function that holds the call."""
    _termui_alias_batch(db, tmp_path)
    body = S258_TURN3.replace("def cmd():\n    confirm_cmd()\n",
                              "def cmd():\n    click.echo('no')\n")
    assert body != S258_TURN3
    msg = _refusal(db, body)
    assert STDIN in msg, msg
    assert "no command that CliRunner().invoke runs calls confirm_cmd()" in msg, msg
    assert _INVOKE_ROUTE not in msg, msg


def test_a_prompt_two_hops_from_the_command_stays_refused(db, tmp_path):
    """One hop only: the admission does not follow a helper's own calls."""
    _termui_alias_batch(db, tmp_path)
    body = S258_TURN3.replace(
        "@click.command()\ndef cmd():\n    confirm_cmd()\n",
        "def middle():\n    confirm_cmd()\n\n@click.command()\ndef cmd():\n    middle()\n")
    assert body != S258_TURN3
    msg = _refusal(db, body)
    assert STDIN in msg, msg
    assert "no command that CliRunner().invoke runs calls confirm_cmd()" in msg, msg
    assert _INVOKE_ROUTE not in msg, msg


def test_a_bare_prompt_with_no_cliRunner_keeps_the_route(db, tmp_path):
    # F12's pass 1d: the body takes `command` from click, so click is its
    # command library. The literal "click" of frame 301 is gone.
    _termui_alias_batch(db, tmp_path)
    msg = _refusal(db, "from click.termui import confirm\nfrom click import command\n\n"
                       "def test_x():\n    assert confirm('ok?', default=True) is True")
    assert STDIN in msg, msg
    assert _INVOKE_ROUTE in msg, msg


def test_a_bare_unused_import_gives_no_route(db, tmp_path):
    # F12's pass 1d: a bare import that the body never uses names no
    # command library, so the route is not offered.
    _termui_alias_batch(db, tmp_path)
    msg = _refusal(db, "from click.termui import confirm\nimport click\n\n"
                       "def test_x():\n    assert confirm('ok?', default=True) is True")
    assert STDIN in msg, msg
    assert _INVOKE_ROUTE not in msg, msg


def test_a_typer_runner_import_gives_the_route(db, tmp_path):
    # F12's pass 1d: the old rule read the literal "click", so a typer body
    # got no route.
    _termui_alias_batch(db, tmp_path)
    msg = _refusal(db, "from typer import confirm\nfrom typer.testing import CliRunner\n\n"
                       "def test_x():\n    assert confirm('ok?', default=True) is True")
    assert STDIN in msg, msg
    assert _INVOKE_ROUTE in msg, msg


def test_a_body_that_reads_module_dunders_is_not_refused_by_the_name_guard(db, tmp_path):
    """Frame 301's review 1, finding 1: every module binds `__file__` and
    `__builtins__`. Night 144's s471 was told to define `__builtins__`."""
    _termui_alias_batch(db, tmp_path)
    body = ("from click.termui import confirm\n\n"
            "def test_x(monkeypatch):\n"
            "    assert __file__.endswith('.py')\n"
            "    assert __builtins__ is not None\n"
            "    monkeypatch.setattr('click.termui.visible_prompt_func', lambda _='': 'y')\n"
            "    assert confirm('ok?') is True")
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    assert _encode(sb, body)["id"] == "tst_new"
