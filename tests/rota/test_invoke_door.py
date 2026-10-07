"""
Frame 131: a test passes a plain function to `CliRunner.invoke`.

On nights 119, 122, 123, 125 and 126 the Tester s139 stored three tests that
pass the plain `echo_json` to `runner.invoke`. Each failed at `cli.name`
against the base, and the Developer turned the function into a command to
fit the tests. `tests.encode` now refuses a body that passes to `.invoke` a
name that the project's base defines as a plain `def` with no decorator. The
refusal states the fact and names no call (Roman, 2026-09-15, 6b52a09d).
"""
from __future__ import annotations

import ast
import sqlite3
import subprocess
from pathlib import Path

import pytest

from rota.core import sandbox
from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import api
from rota.roles.api import _plain_invoked

NIGHTS = Path("D:/repos/rota/.rota")
CLICKI = Path("D:/repos/_AI/sample_repos/clickI")
# The project's head when each night's batch bg_1 started, at the
# Developer's s130 (plans/frame131-read.md, the read's `door.py`).
S130 = {119: "8b19b7f648", 123: "4e6e9150f8", 125: "bbef965850",
        126: "972e707141"}

UTILS = '''\
import json


def echo(message=None):
    print(message)


def echo_json(obj: object) -> None:
    echo(json.dumps(obj, separators=(",", ":")))
'''

CORE = '''\
from .decorators import command


@command()
def hello():
    pass
'''

# s139's three bodies on night 126, read from `.rota/clickI_night126.db`:
# turn 5 for inh_echo_json_01 and inh_echo_json_02, turn 4 for
# inh_echo_json_03. s139 sent the same bodies on nights 119, 122, 123 and
# 125 (plans/frame131-read.md, the first paragraph).
S139_01 = r"""def test_echo_json_compact():
    from click.testing import CliRunner
    from src.click.utils import echo_json

    runner = CliRunner()
    result = runner.invoke(echo_json, ['{"key": "value"}'], catch_exceptions=False)
    assert result.exit_code == 0
    assert result.output.strip() == '{"key": "value"}'
    # Check for single newline at end
    assert result.output.endswith('\n')
    # Check no extra newlines
    assert result.output.count('\n') == 1"""

S139_02 = r"""def test_echo_json_no_ansi():
    from click.testing import CliRunner
    from src.click.utils import echo_json

    runner = CliRunner()
    result = runner.invoke(echo_json, ['{"key": "value"}'], catch_exceptions=False)
    assert result.exit_code == 0
    # Ensure no ANSI escape sequences are present
    assert '\x1b' not in result.output
    assert '\u001b' not in result.output"""

S139_03 = r"""def test_echo_json_non_serializable():
    from click.testing import CliRunner
    from src.click.utils import echo_json

    runner = CliRunner()
    # Pass a non-serializable object (e.g., a custom class instance without __dict__ or __repr__ that JSON can't handle)
    class BadObj:
        def __init__(self):
            self.value = "test"

    result = runner.invoke(echo_json, [str(BadObj())], catch_exceptions=False)
    # It should raise TypeError because json.dumps cannot serialize it
    assert result.exit_code != 0
    assert 'TypeError' in result.output"""

# Each blank line of the three bodies holds four spaces. An editor strips
# trailing spaces from a source file, so the literals hold empty lines and
# the spaces go back here. No body holds an empty line of its own.
S139 = [(tid, path, body.replace("\n\n", "\n    \n")) for tid, path, body in [
    ("inh_echo_json_01", "tests/test_utils/test_echo_json_compact.py", S139_01),
    ("inh_echo_json_02", "tests/test_utils/test_echo_json_no_ansi.py", S139_02),
    ("inh_echo_json_03", "tests/test_utils/test_echo_json.py", S139_03),
]]

DOOR = "to `.invoke`"


def _said(test_id: str) -> str:
    return (f"the test {test_id} passes `echo_json` to `.invoke`, and "
            f"`echo_json` is a plain function in `src/click/utils.py` at "
            f"line 8: `CliRunner.invoke` takes a command")


@pytest.fixture
def db(tmp_path):
    """A Tester's database whose project is a git repository with a plain
    `echo_json` in `src/click/utils.py` and a command in `src/click/core.py`."""
    root = tmp_path / "project"
    (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "__init__.py").write_bytes(b"")
    (root / "src" / "click" / "utils.py").write_bytes(UTILS.encode())
    (root / "src" / "click" / "core.py").write_bytes(CORE.encode())
    for cmd in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "base"]):
        subprocess.run(["git", "-C", str(root), *cmd], check=True,
                       capture_output=True)
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
                 "('project_root', ?)", (str(root),))
    conn.execute("INSERT INTO items (id, text, kind, approval, "
                 "approval_ver, version) VALUES ('i1','echo json',"
                 "'in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','i1','add an echo_json helper')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('c1','tk1','echo_json writes an object as compact JSON')")
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES "
                 "('b1','i1','running')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b1','tk1')")
    conn.commit()
    return conn


def _encode(db, test_id, path, body):
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    return sb.call("tests.encode", id=test_id, criterion_id="c1",
                   path=path, body=body)


def _not_this_door(db, body, test_id="tst_new", path="tests/test_new.py"):
    """The encode lands, or another door refuses it. This door stays shut."""
    try:
        _encode(db, test_id, path, body)
    except ValueError as exc:
        assert DOOR not in str(exc), str(exc)


@pytest.mark.parametrize("test_id,path,body", S139, ids=[t for t, _, _ in S139])
def test_s139s_bodies_are_refused(db, test_id, path, body):
    with pytest.raises(ValueError) as exc:
        _encode(db, test_id, path, body)
    assert str(exc.value) == _said(test_id)
    assert not isinstance(exc.value, api.Wall)
    assert not db.execute("SELECT 1 FROM tests WHERE id = ?", (test_id,)).fetchone()


def test_the_refusal_names_no_call_and_no_recipe(db):
    with pytest.raises(ValueError) as exc:
        _encode(db, *S139[0])
    said = str(exc.value)
    for word in ("capsys", "def test", "(", "tests.", "msg."):
        assert word not in said


def test_a_decorated_command_is_admitted(db):
    body = ("from click.testing import CliRunner\n"
            "from src.click.core import hello\n\n\n"
            "def test_hello():\n"
            "    runner = CliRunner()\n"
            "    result = runner.invoke(hello, [])\n"
            "    assert result.exit_code == 0\n")
    assert _encode(db, "tst_hello", "tests/test_hello.py", body) == {"id": "tst_hello"}


def test_a_local_function_is_admitted(db):
    body = ("from click.testing import CliRunner\n\n\n"
            "def echo_json():\n"
            "    pass\n\n\n"
            "def test_local():\n"
            "    result = CliRunner().invoke(echo_json)\n"
            "    assert result.exit_code == 0\n")
    assert _encode(db, "tst_local", "tests/test_local.py", body) == {"id": "tst_local"}


@pytest.mark.parametrize("arg,head", [
    ("utils.echo_json", "from src.click import utils\n"),
    ("make()", "from src.click.utils import echo_json\n\n\n"
               "def make():\n    return echo_json\n"),
    ("'echo_json'", ""),
], ids=["attribute", "call", "string"])
def test_an_invoke_of_no_bare_name_is_admitted(db, arg, head):
    body = (f"from click.testing import CliRunner\n{head}\n\n"
            f"def test_x():\n"
            f"    result = CliRunner().invoke({arg})\n"
            f"    assert result.exit_code == 0\n")
    assert _plain_invoked(ast.parse(body), "tests/test_x.py",
                          lambda p: UTILS if p == "src/click/utils.py" else None) is None
    _not_this_door(db, body)


def _reader(files: dict):
    return lambda p: files.get(p)


def _invoked(base: str, imp: str = "from src.click.utils import echo_json",
             path: str = "tests/test_x.py", files=None):
    body = (f"{imp}\n\n\ndef test_x():\n"
            f"    assert runner.invoke(echo_json).exit_code == 0\n")
    return _plain_invoked(ast.parse(body), path,
                          _reader(files or {"src/click/utils.py": base}))


@pytest.mark.parametrize("base", [
    "@command()\ndef echo_json(obj):\n    pass\n",
    "@pass_context\ndef echo_json(obj):\n    pass\n",
    "class echo_json:\n    pass\n",
    "def echo_json(obj):\n    pass\n\n\necho_json = command()(echo_json)\n",
    "def echo(obj):\n    pass\n",
    "from .core import echo_json\n",
], ids=["command", "other-decorator", "class", "wrapped-by-assignment",
        "not-found", "re-export"])
def test_a_name_that_is_not_a_plain_def_is_admitted(base):
    assert _invoked(base) is None


@pytest.mark.parametrize("imp,files", [
    ("from src.click.utils import echo_json", {"src/click/utils.py": UTILS}),
    ("from click.utils import echo_json", {"src/click/utils.py": UTILS}),
    ("from click.utils import echo_json", {"click/utils.py": UTILS}),
    ("from src.click import echo_json", {"src/click/__init__.py": UTILS}),
    ("from ..src.click.utils import echo_json", {"src/click/utils.py": UTILS}),
], ids=["src", "installed-src", "root-package", "package-init", "relative"])
def test_each_import_form_resolves_to_the_base(imp, files):
    got = _invoked("", imp=imp, path="tests/test_x.py", files=files)
    assert got is not None and got[0] == "echo_json" and got[3] == 8


def test_an_imported_name_that_the_test_binds_again_is_the_tests_own():
    body = ("from click import command\n"
            "from src.click.utils import echo_json\n\n\n"
            "def test_x():\n"
            "    echo_json = command()(echo_json)\n"
            "    assert runner.invoke(echo_json).exit_code == 0\n")
    assert _plain_invoked(ast.parse(body), "tests/test_x.py",
                          _reader({"src/click/utils.py": UTILS})) is None


def test_a_test_module_of_the_project_is_not_the_product():
    files = {"tests/helpers.py": UTILS}
    assert _invoked("", imp="from tests.helpers import echo_json",
                    files=files) is None


def test_no_project_root_admits(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    assert api._base_reader(type("C", (), {"conn": conn})())("x.py") is None


def test_the_refusal_goes_through_the_follow_and_fact_checks(db):
    """The path of frame 144's dry run, as `test_scalar_door._refused` takes
    it: the refusal names no call, so nothing is followed, and the one fact
    it quotes, the `def` line in the base, holds."""
    got = []
    prev, sandbox._ON_REFUSAL = sandbox._ON_REFUSAL, lambda *a: got.append(a)
    try:
        with pytest.raises(ValueError):
            _encode(db, *S139[0])
    finally:
        sandbox._ON_REFUSAL = prev
    assert len(got) == 1, "the refusal reached no follow check"
    sb, name, args, exc, offers, facts = got[0]
    assert offers == []
    assert sandbox.follow(sb, name, args, exc, offers) == []
    checked = sandbox.check_facts(sb, facts)
    assert [(f["kind"], f["value"]) for f in checked] == [
        ("line_text", "def echo_json")]
    assert all(f["ok"] for f in checked), checked


def _git_reader(sha: str):
    def read(path: str):
        out = subprocess.run(["git", "-C", str(CLICKI), "show", f"{sha}:{path}"],
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace")
        return out.stdout if out.returncode == 0 else None
    return read


@pytest.mark.skipif(not (NIGHTS.is_dir() and (CLICKI / ".git").exists()),
                    reason="the night databases or the clickI repository are absent")
def test_the_stored_rows_of_four_nights():
    """Every stored test with an `.invoke` call on nights 119, 123, 125 and
    126, against the base at that night's s130: 90 rows, 6 refused, each a
    test of s139, and 0 others (plans/frame131-read.md, section 5)."""
    rows, refused = 0, []
    for night, sha in S130.items():
        read = _git_reader(sha)
        src = sqlite3.connect(
            f"file:{(NIGHTS / f'clickI_night{night}.db').as_posix()}"
            f"?mode=ro&immutable=1", uri=True)
        try:
            stored = src.execute("SELECT id, path, body FROM tests").fetchall()
        finally:
            src.close()
        for test_id, path, body in stored:
            try:
                tree = ast.parse(body or "")
            except SyntaxError:
                continue
            if not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                       and n.func.attr == "invoke" and n.args
                       for n in ast.walk(tree)):
                continue
            rows += 1
            got = _plain_invoked(tree, path, read)
            if got:
                refused.append((night, test_id, got[2], got[3]))
    assert rows == 90
    assert sorted(refused) == [
        (119, "inh_echo_json_01", "src/click/utils.py", 689),
        (119, "inh_echo_json_02", "src/click/utils.py", 689),
        (123, "inh_echo_json_01", "src/click/utils.py", 689),
        (123, "inh_echo_json_03", "src/click/utils.py", 689),
        (126, "inh_echo_json_01", "src/click/utils.py", 689),
        (126, "inh_echo_json_02", "src/click/utils.py", 689),
    ]
