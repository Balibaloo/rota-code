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


def _wrap():
    # Import only when the test process already holds click. An import of
    # a broken `click.testing` turned a pass into a fail, and so did a
    # warning under `filterwarnings = error` (frame 195, review point 2).
    if "click" not in sys.modules:
        return
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import click.testing  # noqa: F401
        mod = sys.modules.get("click.testing")
        runner = getattr(mod, "CliRunner", None)
        orig = runner.__dict__.get("invoke") if runner is not None else None
        if orig is None or not callable(orig) or getattr(orig, _MARK, False):
            return
        setattr(runner, "invoke", _wrapped(orig))
    except Exception:
        return


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
