"""
F12 of the root-fix audit of 2026-10-27: the runner target in a test body.

`runner_invokes` is the one reader of a body's `.invoke` calls on a runner.
Before it, `_plain_invoked`, `_callable_invoked` and `_plain_decorated` each
held a nested copy of the runner rule and bound runners by their own rule.
Each test below is one place where an old rule and the reader disagree.
"""
from __future__ import annotations

import ast
import pathlib
import textwrap

OPTION_ONLY = textwrap.dedent('''
    import click
    from click.testing import CliRunner

    def test_x():
        @click.option("--n")
        def f(n):
            click.echo(n)
        with CliRunner() as r:
            r.invoke(f)
''')


def test_a_with_bound_runner_runs_the_plain_decorated_function():
    """`_plain_decorated` missed a runner bound by `with ... as r`."""
    from rota.roles.api import _plain_decorated

    found = _plain_decorated(ast.parse(OPTION_ONLY), "option")
    assert found and found[0] == "f" and found[2] == "plain"


def test_an_annotated_runner_runs_the_plain_decorated_function():
    """`_plain_decorated` bound an annotated runner to nothing."""
    from rota.roles.api import _plain_decorated

    body = OPTION_ONLY.replace("    with CliRunner() as r:\n        r.invoke(f)",
                               "    r: CliRunner = CliRunner()\n    r.invoke(f)")
    found = _plain_decorated(ast.parse(body), "option")
    assert found and found[0] == "f"


def test_a_with_bound_runner_invoking_a_lambda_is_a_plain_callable():
    """`_callable_invoked` missed a runner bound by `with ... as r`
    (frame 230's lambda)."""
    from rota.roles.api import _callable_invoked

    body = textwrap.dedent('''
        from click import confirm
        from click.testing import CliRunner

        def test_x():
            with CliRunner() as r:
                r.invoke(lambda: confirm("go"))
    ''')
    found = _callable_invoked(ast.parse(body))
    assert found is not None and found[0] is None


def test_a_with_bound_runner_invoking_an_imported_plain_function_is_named():
    """`_plain_invoked` missed a runner bound by `with ... as r` (frame 131)."""
    from rota.roles.api import _plain_invoked

    body = textwrap.dedent('''
        from click.testing import CliRunner
        from app.cli import echo_json

        def test_x():
            with CliRunner() as r:
                r.invoke(echo_json, ["x"])
    ''')
    files = {"app/cli.py": "def echo_json(obj):\n    return obj\n"}
    found = _plain_invoked(ast.parse(body), "tests/test_cli.py",
                           lambda p: files.get(p))
    assert found is not None and found[0] == "echo_json"


def _constants(path):
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    out = {}
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for n in ast.walk(fn):
                if isinstance(n, ast.Constant) and n.value == "CliRunner":
                    out.setdefault(fn.name, 0)
    return set(out)


# The readers of the runner literal that this pass leaves, by name. A new
# function that compares a node to "CliRunner" makes the pin red. The
# report of F12's pass 1 names each one and why it stays.
RESIDUE = {"_invoked_commands", "_invoked_command_calls", "_outside_commands_step",
           "_arrange_run_refusal", "_spec_mock_raise", "tests_encode",
           "tests_load", "_refusal", "_unbound_name_hint"}


def test_runner_receivers_is_the_one_runner_rule_of_the_moved_readers():
    """The pin of F12. The nested copies are gone, and no function outside
    `_runner_receivers` and the named residue holds the runner literal."""
    api = pathlib.Path(__file__).resolve().parents[2] / "rota" / "roles" / "api.py"
    holders = _constants(api)
    assert "_is_runner_call" not in holders
    for moved in ("_plain_invoked", "_callable_invoked", "_plain_decorated"):
        assert moved not in holders, moved
    # `is_runner_call` is the nested predicate inside `_runner_receivers`.
    assert holders - RESIDUE <= {"_runner_receivers", "is_runner_call"}, (
        holders - RESIDUE)
