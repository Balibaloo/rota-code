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
                if isinstance(n, ast.Constant) and isinstance(n.value, str) and (n.value in ("CliRunner", "click", "typer") or n.value.endswith("Runner")):
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


# Pass 1e: the review of 25d82d33.

def test_command_libraries_reads_the_library_of_a_called_callable():
    """Finding 1: s187's body (frame 304) imports confirm from click.termui
    and calls it, with no runner, command or group."""
    from rota.roles.api import command_libraries
    from tests.rota.test_frame304_arrange_raises import S187_TST02

    assert command_libraries(ast.parse(S187_TST02)) == {"click"}
    assert command_libraries(ast.parse("import pytest\nimport re\n\n"
                                       "def test_x():\n    pytest.raises(re.error)\n")) == set()


def test_command_libraries_reads_the_indexed_project_package_under_src():
    from rota.roles.api import command_libraries

    body = "from src.acme.termui import ask\n\ndef test_x():\n    ask()\n"
    assert command_libraries(ast.parse(body), {"acme"}) == {"acme"}


PROJ3 = {
    "mylib/__init__.py": "",
    "mylib/testing.py": (
        "class Harness:\n    @staticmethod\n    def invoke(x):\n        return x * 2\n\n"
        "class Factory:\n    @classmethod\n    def invoke(cls, x):\n"
        "        return cls.__name__ + str(x)\n"),
    "tests/test_p3.py": (
        "from mylib.testing import Harness, Factory\n\n"
        "def test_static_on_instance():\n    assert Harness().invoke(2) == 4\n\n"
        "def test_classmethod():\n    assert Factory.invoke(1) == 'Factory1'\n"),
}


def test_the_plugin_leaves_a_staticmethod_and_a_classmethod_invoke_alone(tmp_path):
    """Finding 2, the reviewer's proj3: the wrap turned a staticmethod into a
    plain function, and `Harness().invoke(2)` raised a TypeError."""
    import os
    import subprocess
    import sys

    from rota.core import harness

    files = {"pytest.ini": "[pytest]\n", **PROJ3}
    for rel, text in files.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text, encoding="utf-8")
    env = {k: v for k, v in os.environ.items()
           if k not in ("PYTEST_ADDOPTS", "PYTHONPATH")}
    env["PYTHONPATH"] = str(harness.PLUGIN_DIR)
    out = subprocess.run([sys.executable, "-m", "pytest", "tests/test_p3.py", "-q",
                          "-p", "no:cacheprovider", "-p", harness.PLUGIN],
                         cwd=tmp_path, capture_output=True, text=True,
                         timeout=120, env=env)
    assert out.returncode == 0, out.stdout


ACME = textwrap.dedent('''
    import acme
    from acme.testing import Harness

    @acme.command()
    def ask():
        acme.confirm("ok?")

    def test_x():
        Harness().invoke(ask, input="y")
''')


def test_the_pin_reads_a_library_with_no_known_name():
    """Finding 4: the pin is behaviour. A library and a runner that no
    literal names, as `acme` and `Harness`, reach every moved reader. A
    reader by `endswith("Runner")` or by the name "typer" goes red here."""
    from rota.roles import api

    tree = ast.parse(ACME)
    assert len(api.runner_invokes(tree)) == 1
    assert [f.name for f in api._invoked_commands(tree)] == ["ask"]
    assert api.command_libraries(tree) == {"acme"}
    route = api._invoke_route(tree, api.command_libraries(tree))
    assert "command of acme" in route and "Harness().invoke(cmd" in route, route
    assert "click" not in route and "CliRunner" not in route, route


def test_the_route_texts_name_the_body_library_and_runner():
    """Finding 5: the texts named click's decorator and runner for any body."""
    from rota.roles import api

    tree = ast.parse("from typer.testing import CliRunner as R\nimport typer\n")
    text = api._empty_stdin_route(tree, {"typer"})
    assert "command of typer" in text and "R().invoke(cmd, input='')" in text, text


from tests.rota.test_frame304_arrange_door import db  # noqa: E402,F401


def test_the_spec_mock_site_gives_s187_the_route_of_its_library(db, tmp_path):
    """Finding 1, probe 4a: s187's body lost the route at 25d82d33."""
    from tests.rota.test_frame304_arrange_raises import S187_TST02, _refusal

    text = _refusal(db, S187_TST02)
    assert "For an empty stdin, call the surface inside a command of click" in text, text


def test_the_arrange_site_gives_s185_the_route_of_its_library(db, tmp_path, monkeypatch):
    """Finding 1, probe 4b: s185's body lost the route at 25d82d33."""
    from rota.core.sandbox import build
    from rota.roles import api
    from tests.rota.test_frame304_arrange_door import S185_CR4, S185_CR4_RUN, _git_batch, _ran

    _git_batch(db, tmp_path)
    _ran(monkeypatch, S185_CR4_RUN)
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    text = api._arrange_run_refusal(sb.ctx, "b1", "c1",
                                    "tests/test_utils/test_confirm_plain.py", S185_CR4)
    assert text is not None and "command of click" in text, text
