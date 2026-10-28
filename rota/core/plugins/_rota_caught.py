"""
A pytest plugin: report an exception that click's `CliRunner` caught.

Night 138 (frame 195): a commit used `sys.version` with no `import sys`.
The runner caught the `NameError`, the test asserted on the empty
`result.output`, and the red row showed the assertion alone for eight
attempts. The `Result` lives in the pytest child, so the report starts here.

The harness loads this module with `-p _rota_caught` and puts this
directory on `PYTHONPATH` (`rota/core/harness.py`). It runs under the
project's interpreter, so it imports nothing from rota and keeps old
syntax. The name starts with `_rota`, because `python -m pytest` puts the
working directory ahead of `PYTHONPATH` and a project file of the same
name would replace this one (frame 195, design review, point 1).

The plugin must never change a test's result. Every step that touches
the project's code sits in `try/except Exception` for that reason.
"""
import functools
import os
import sys
import traceback
import types
import warnings

import pytest

TITLE = "CliRunner caught an exception"
FINAL = "caught by CliRunner at "
_MARK = "_rota_caught_wrapped"
# The section must leave room for the test's assertion in the harness's
# 2000-character tail (frame 195, design review, point 4).
_LINE_CAP = 160
_EXC_CAP = 300

_state = {"root": None, "caught": []}


def _cut(text, cap):
    text = text.rstrip()
    if len(text) <= cap:
        return text
    return text[:cap - 3] + "..."


def _rel(path):
    root = _state["root"]
    if not root:
        return path
    try:
        return os.path.relpath(path, root)
    except ValueError:
        # Base Python sits on C: and the worktrees on D:, and `relpath`
        # refuses two drives (frame 195, design review, point 4).
        return path


def _entry(result):
    """The caught exception as text, or None. The text is formed now.

    The plugin keeps text and never `exc_info`, so no frame stays alive
    into the next test (frame 195, design review, point 3).
    """
    info = getattr(result, "exc_info", None)
    if not isinstance(info, tuple) or len(info) != 3:
        return None
    tp, val, tb = info
    if val is None or not isinstance(val, BaseException):
        return None
    # click exits with `SystemExit` on purpose.
    if isinstance(val, SystemExit):
        return None
    if tp is None:
        tp = type(val)
    frames = traceback.extract_tb(tb)[-3:] if tb is not None else []
    lines = []
    for fr in frames:
        lines.append(_cut('  File "%s", line %s, in %s'
                          % (_rel(fr.filename), fr.lineno, fr.name), _LINE_CAP))
        if fr.line:
            lines.append(_cut("    " + fr.line.strip(), _LINE_CAP))
    said = "".join(traceback.format_exception_only(tp, val))
    lines.append(_cut(said, _EXC_CAP))
    name = getattr(tp, "__name__", None) or type(val).__name__
    if frames:
        last = frames[-1]
        where = "%s:%s" % (_rel(last.filename), last.lineno)
    else:
        where = "<unknown>:0"
    try:
        output = getattr(result, "output")
        if isinstance(output, str):
            lines.append("output: empty" if output == ""
                         else "output: %d characters" % len(output))
    except Exception:
        pass
    return {"key": (name, where), "lines": lines,
            "final": "%s%s: %s" % (FINAL, where, name)}


def _keep(result):
    entry = _entry(result)
    if entry is not None:
        _state["caught"].append(entry)


def _wrapped(orig):
    # `functools.wraps` keeps `inspect.signature(CliRunner.invoke)` the
    # same, because a test that read it failed on `(self, *a, **k)`.
    @functools.wraps(orig)
    def invoke(self, *args, **kwargs):
        result = orig(self, *args, **kwargs)
        try:
            _keep(result)
        except Exception:
            pass
        return result

    setattr(invoke, _MARK, True)
    return invoke


def _is_testing(name):
    # F12's pass 1d: a runner is a class of a library's `testing` module, as
    # rota's `command_libraries` reads it. The plugin runs in the project's
    # interpreter and imports nothing from rota, so it holds the same rule.
    return isinstance(name, str) and "." in name and name.split(".")[-1] == "testing"


def _imported_packages(path):
    # The top packages that the test file imports, in the body too. F12's
    # review finding 2: the plugin touches only a library the test uses.
    import ast

    try:
        with open(path, encoding="utf-8") as handle:
            tree = ast.parse(handle.read())
    except Exception:
        return set()
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            out |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and not n.level and n.module:
            out.add(n.module.split(".")[0])
    return out


def _patch(mod):
    # Each class that the module defines and that has its own plain `invoke`
    # is a runner. The library names its runner, so the plugin reads no name.
    # A staticmethod or a classmethod is no runner method: a plain function
    # in its place changes the call (F12's review finding 2, probe 3).
    try:
        if mod.__name__.split(".")[0] not in _state.get("packages", ()):
            return
        for runner in list(vars(mod).values()):
            if not isinstance(runner, type):
                continue
            if getattr(runner, "__module__", None) != mod.__name__:
                continue
            orig = runner.__dict__.get("invoke")
            if type(orig) is not types.FunctionType or getattr(orig, _MARK, False):
                continue
            setattr(runner, "invoke", _wrapped(orig))
    except Exception:
        return


def _wrap():
    # The second route, for a `testing` module imported before the finder
    # was installed. The plugin imports no module itself. An import of a
    # broken `click.testing` turned a pass into a fail, and so did a warning
    # under `filterwarnings = error` (frame 195, review point 2).
    try:
        for name, module in list(sys.modules.items()):
            if _is_testing(name) and module is not None:
                _patch(module)
    except Exception:
        return


def _exec_wrapped(orig):
    @functools.wraps(orig)
    def exec_module(module):
        # The real import runs first and unchanged. Its exception goes to
        # the importer as it is.
        orig(module)
        try:
            if _is_testing(getattr(module, "__name__", None)):
                _patch(module)
        except Exception:
            pass

    setattr(exec_module, _MARK, True)
    return exec_module


class _Finder(object):
    """Wrap `CliRunner.invoke` right after `click.testing` executes.

    The review of 878c2352 counted 66 of 104 Tester bodies that import
    click inside the test body. The call-time wrap needs click in
    `sys.modules` first, so those tests got no section. The finder answers
    for `click.testing` alone and returns the spec the other finders give.
    A reload finds the spec again, so the new class is wrapped again.
    """

    def find_spec(self, name, path=None, target=None):
        if not _is_testing(name):
            return None
        try:
            spec = None
            for finder in list(sys.meta_path):
                if isinstance(finder, _Finder):
                    continue
                find = getattr(finder, "find_spec", None)
                if find is None:
                    # Python 3.11 and older ask a `find_module` finder in its
                    # place. When it gives a loader, None leaves it its turn
                    # (frame 195, review of 89fd9027, finding 1). Python 3.12
                    # and later ignore such a finder, so the loop goes past it.
                    # A None there loaded `click.testing` with no wrap (frame
                    # 195, review of 969b76a2).
                    legacy = getattr(finder, "find_module", None)
                    if legacy is not None and sys.version_info < (3, 12):
                        if legacy(name, path) is not None:
                            return None
                    continue
                spec = find(name, path, target)
                if spec is not None:
                    break
            loader = getattr(spec, "loader", None)
            orig = getattr(loader, "exec_module", None)
            # A loader that is a class serves every module it loads, so a
            # patch on it would reach them all.
            if orig is None or isinstance(loader, type):
                return spec
            if not getattr(orig, _MARK, False):
                loader.exec_module = _exec_wrapped(orig)
            return spec
        except Exception:
            # None sends the import on to the next finder, as if the
            # finder were absent.
            return None


_finder = _Finder()


def _install():
    try:
        if not any(isinstance(f, _Finder) for f in sys.meta_path):
            sys.meta_path.insert(0, _finder)
    except Exception:
        pass


def _remove():
    try:
        sys.meta_path[:] = [f for f in sys.meta_path if not isinstance(f, _Finder)]
    except Exception:
        pass


# At load, because pytest imports a `-p` plugin before any conftest, and a
# conftest can import `click.testing`.
_install()


def _section():
    entries = []
    keys = set()
    for entry in _state["caught"]:
        if entry["key"] in keys:
            continue
        keys.add(entry["key"])
        entries.append(entry)
    if not entries:
        return None
    # One entry, and a count for the rest. Four raising calls pushed the
    # assertion out of the 2000-character tail (frame 195, review point 4).
    first = entries[0]
    lines = list(first["lines"])
    more = len(_state["caught"]) - 1
    if more:
        other = len([e for e in _state["caught"] if e["key"] != first["key"]])
        lines.append("and %d more in this test, %d of them at another place"
                     % (more, other))
    # The final line is the last line of the section, and the harness
    # reads it with its own pattern (`tests.load`, rota/roles/api.py).
    lines.append(first["final"])
    return "\n".join(lines)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    try:
        _state["caught"] = []
        if _state["root"] is None:
            config = item.config
            root = getattr(config, "rootpath", None) or getattr(config, "rootdir", None)
            _state["root"] = str(root) if root is not None else ""
        _state["packages"] = _imported_packages(
            str(getattr(item, "path", None) or getattr(item, "fspath", "")))
        _wrap()
    except Exception:
        pass
    yield


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    # An exception here gave INTERNALERROR and exit 3, which the harness
    # records as `error` (frame 195, design review, point 4).
    try:
        if call.when != "call":
            return
        report = outcome.get_result()
        if report.failed:
            text = _section()
            if text:
                report.sections.append((TITLE, text))
        _state["caught"] = []
    except Exception:
        pass


def pytest_unconfigure(config):
    _remove()
