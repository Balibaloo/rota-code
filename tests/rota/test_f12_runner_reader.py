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
                if isinstance(n, ast.Constant) and n.value in ("CliRunner", "click"):
                    out.setdefault(fn.name, 0)
    return set(out)


# Pass 1d leaves no reader of a library literal. A function that compares a
# node to "CliRunner" or "click" makes the pin red. Messages that name click
# are text for the seat, not readers, and the pin does not count them.
RESIDUE: set[str] = set()


def test_the_plugin_holds_no_library_literal():
    """The plugin's rule is `_is_testing`. Its `TITLE` and `FINAL` are the
    text that `tests_load` parses, so the pin counts function bodies only."""
    plugin = (pathlib.Path(__file__).resolve().parents[2] / "rota" / "core"
              / "plugins" / "_rota_caught.py")
    tree = ast.parse(plugin.read_text(encoding="utf-8"))
    held = {fn.name for fn in ast.walk(tree)
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))
            for n in ast.walk(fn)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
            and (n.value in ("CliRunner", "click") or n.value.startswith("click."))}
    assert held == set(), held


def test_runner_receivers_is_the_one_runner_rule_of_the_moved_readers():
    """The pin of F12. The nested copies are gone, and no function outside
    `_runner_receivers` and the named residue holds the runner literal."""
    api = pathlib.Path(__file__).resolve().parents[2] / "rota" / "roles" / "api.py"
    holders = _constants(api)
    assert "_is_runner_call" not in holders
    assert "def _click_names" not in api.read_text(encoding="utf-8")
    for moved in ("_plain_invoked", "_callable_invoked", "_plain_decorated",
                  "_invoked_commands", "_returns_factory", "_adds_option",
                  "_factory_misuse", "_import_bound", "command_libraries"):
        assert moved not in holders, moved
    # Pass 1b: the one reader reads the body's imports, so it holds no
    # runner literal. Only the named residue still holds one.
    assert holders - RESIDUE == set(), holders - RESIDUE


def test_a_typer_runner_is_a_runner():
    """Pass 1b's ruling: the library is what the body imports. The old rule
    read the literal "CliRunner" by name, so it found typer's by luck and
    missed a runner imported under another name."""
    from rota.roles.api import runner_invokes

    body = textwrap.dedent('''
        from typer.testing import CliRunner as TyperRunner
        from app.main import app

        def test_x():
            r = TyperRunner()
            r.invoke(app, ["hello"])
    ''')
    assert len(runner_invokes(ast.parse(body))) == 1


def test_a_class_named_like_a_runner_outside_a_testing_module_is_no_runner():
    """The other side of the ruling: a project class named `CliRunner` that
    no `testing` module gives is not the library's runner."""
    from rota.roles.api import runner_invokes

    body = textwrap.dedent('''
        from app.jobs import CliRunner

        def test_x():
            job = CliRunner()
            job.invoke(lambda: None)
    ''')
    assert runner_invokes(ast.parse(body)) == []


# Pass 1c: the readers of the command names. Each body takes its library
# from typer, so the old literal "click" read no name of it.

def test_invoked_commands_reads_the_library_of_a_typer_runner():
    from rota.roles.api import _invoked_commands

    body = textwrap.dedent('''
        import typer
        from typer.testing import CliRunner

        app = typer.Typer()

        @app.command()
        def ask():
            typer.confirm("ok?")

        def test_x():
            CliRunner().invoke(app, input="y")
    ''')
    assert [f.name for f in _invoked_commands(ast.parse(body))] == ["ask"]


def test_factory_misuse_reads_a_typer_import():
    from rota.roles.api import _factory_misuse

    body = "import typer as t\nassert 'x' in t.f()\n"
    assert _factory_misuse(ast.parse(body), "f") == "return"


def test_plain_decorated_reads_a_typer_import():
    from rota.roles.api import _plain_decorated

    body = textwrap.dedent('''
        import typer as t
        from typer.testing import CliRunner

        def test_x():
            @t.version_option()
            def f():
                pass
            CliRunner().invoke(f)
    ''')
    found = _plain_decorated(ast.parse(body), "version_option")
    assert found is not None and found[0] == "f"


def test_returns_factory_reads_a_typer_import():
    from rota.roles.api import _returns_factory

    src = "import typer as t\n\ndef deco():\n    return t.command()\n"
    assert _returns_factory(ast.parse(src).body[1], src) is True


def test_adds_option_reads_a_typer_import():
    from rota.roles.api import _adds_option

    src = "import typer as t\n\ndef opt():\n    return t.option('--n')\n"
    assert _adds_option(ast.parse(src).body[1], src) is True


# Pass 1d: the command library of a body, for the stdin route of
# `tests_encode`, `_arrange_run_refusal` and `_spec_mock_raise`.

def test_command_libraries_reads_a_typer_runner_and_a_typer_command():
    from rota.roles.api import command_libraries

    runner = "from typer.testing import CliRunner\n"
    command = "import typer as t\n\n@t.command()\ndef f():\n    pass\n"
    bare = "import typer\n"
    assert command_libraries(ast.parse(runner)) == {"typer"}
    assert command_libraries(ast.parse(command)) == {"typer"}
    assert command_libraries(ast.parse(bare)) == set()


def test_the_plugin_wraps_a_typer_runner(tmp_path):
    """The plugin read `click.testing` by name. A typer runner caught the
    error, and the plugin printed no section."""
    import os
    import subprocess
    import sys

    from rota.core import harness
    from tests.rota.test_caught import TESTING

    files = {"pytest.ini": "[pytest]\n", "typer/__init__.py": "",
             "typer/testing.py": TESTING,
             "tests/test_t.py": ("from typer.testing import CliRunner\n\n"
                                 "def boom():\n    raise NameError('x')\n\n"
                                 "def test_x():\n"
                                 "    assert CliRunner().invoke(boom).exception is None\n")}
    for rel, text in files.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text, encoding="utf-8")
    env = {k: v for k, v in os.environ.items()
           if k not in ("PYTEST_ADDOPTS", "PYTHONPATH")}
    env["PYTHONPATH"] = str(harness.PLUGIN_DIR)
    out = subprocess.run([sys.executable, "-m", "pytest", "tests/test_t.py", "-q",
                          "-p", "no:cacheprovider", "-p", harness.PLUGIN],
                         cwd=tmp_path, capture_output=True, text=True,
                         timeout=120, env=env)
    assert "CliRunner caught an exception" in out.stdout, out.stdout
