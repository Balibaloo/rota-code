"""
Frame 131: a test passes a plain function to `CliRunner.invoke`.

On nights 119, 122, 123, 125 and 126 the Tester s139 stored three tests that
pass the plain `echo_json` to `runner.invoke`. Each failed at `cli.name`
against the base, and the Developer turned the function into a command to
fit the tests. `tests.encode` now refuses a body that passes to a runner's
`.invoke` a name that the batch's worktree defines as a plain `def` with no
decorator. The refusal states the fact and names no call (Roman, 2026-09-15,
6b52a09d).

During a night the project root is clickI's `main`, which has no
`echo_json`. The Developer's first commit adds it in the batch's worktree.
The fixture keeps that shape (frame 131's review of af9db8a0, high 2).
"""
from __future__ import annotations

import ast
import collections
import shutil
import sqlite3
import subprocess
from pathlib import Path

import pytest

from rota.core import sandbox
from rota.core.db import init_db
from rota.core.sandbox import build
from rota.llm import toolproto
from rota.roles import api
from rota.roles.api import _plain_invoked
from rota.testkit.gitfixture import copy_template

NIGHTS = Path("D:/repos/rota/.rota")
CLICKI = Path("D:/repos/_AI/sample_repos/clickI")
EIGHT = range(119, 127)

# The root's `utils.py`: no `echo_json`, as on clickI's `main`.
ROOT_UTILS = '''\
import json


def echo(message=None):
    print(message)
'''

# The worktree's `utils.py` after the Developer's first commit.
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
            f"`echo_json` is a plain function in `src/click/utils.py`: "
            f"`CliRunner.invoke` takes a command")


def _utils(tree: Path) -> Path:
    return tree / "src" / "click" / "utils.py"


def _trees(base: Path) -> None:
    """Build the fixture `db`'s root and worktree under `base`."""
    root = base / "project"
    (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "__init__.py").write_bytes(b"")
    _utils(root).write_bytes(ROOT_UTILS.encode())
    (root / "src" / "click" / "core.py").write_bytes(CORE.encode())
    for cmd in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "base"]):
        subprocess.run(["git", "-C", str(root), *cmd], check=True,
                       capture_output=True)
    wt = base / "wt"
    shutil.copytree(root / "src", wt / "src")
    _utils(wt).write_bytes(UTILS.encode())


@pytest.fixture
def db(tmp_path):
    """A Tester's database. The project root is a git repository whose
    `src/click/utils.py` has no `echo_json` and whose `src/click/core.py`
    holds a command. Batch b1's worktree is a copy of the root whose
    `utils.py` adds a plain `echo_json`, the Developer's write."""
    # A copy of the two trees built once per process. The git calls per
    # test were the fixture's cost (frame 206's count, 2026-10-11).
    copy_template("invoke_door_db", _trees, tmp_path)
    root, wt = tmp_path / "project", tmp_path / "wt"
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
    conn.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES "
                 "('b1','i1','running',?)", (str(wt),))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b1','tk1')")
    conn.commit()
    return conn


def _root(db) -> Path:
    return Path(db.execute("SELECT value FROM config "
                           "WHERE key = 'project_root'").fetchone()[0])


def _wt(db) -> Path:
    return Path(db.execute("SELECT worktree FROM batches "
                           "WHERE id = 'b1'").fetchone()[0])


def _encode(db, test_id, path, body, batch_id="b1"):
    sb = build("tester", db, batch_id=batch_id, mode="tests_missing")
    sb.call("tests.triage", criterion_id="c1", verdict="encodable")
    return sb.call("tests.encode", id=test_id, criterion_id="c1",
                   path=path, body=body)


def _not_this_door(db, body, test_id="tst_new", path="tests/test_new.py",
                   batch_id="b1"):
    """The encode lands, or another door refuses it. This door stays shut."""
    try:
        _encode(db, test_id, path, body, batch_id=batch_id)
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


def test_a_local_plain_function_is_refused(db):
    """Frame 230: a local `def` with no decorator is a plain function too.
    Before frame 230 this test asserted that the body landed."""
    body = ("from click.testing import CliRunner\n\n\n"
            "def echo_json():\n"
            "    pass\n\n\n"
            "def test_local():\n"
            "    result = CliRunner().invoke(echo_json)\n"
            "    assert result.exit_code == 0\n")
    with pytest.raises(ValueError) as exc:
        _encode(db, "tst_local", "tests/test_local.py", body)
    assert str(exc.value).startswith(
        "the test tst_local passes `echo_json`, a plain function that the "
        "test defines, to `.invoke`")


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


@pytest.mark.parametrize("recv,head", [
    ("ctx", "    ctx = make_context()\n"),
    ("click_ctx", ""),
    ("self.runner", ""),
], ids=["context", "other-name", "attribute"])
def test_an_invoke_on_no_runner_is_admitted(recv, head):
    """Click's `Context.invoke` takes a plain callback, so `ctx.invoke(f)`
    is right (frame 131's review of af9db8a0, low 3)."""
    body = ("from src.click.utils import echo_json\n\n\n"
            f"def test_x(click_ctx):\n{head}"
            f"    assert {recv}.invoke(echo_json, []) is None\n")
    assert _plain_invoked(ast.parse(body), "tests/test_x.py",
                          _reader({"src/click/utils.py": UTILS})) is None


@pytest.mark.parametrize("recv,head", [
    ("runner", ""),
    ("r", "    r = CliRunner()\n"),
    ("r", "    r = testing.CliRunner(mix_stderr=False)\n"),
    ("CliRunner()", ""),
], ids=["runner", "bound", "bound-dotted", "inline"])
def test_an_invoke_on_a_runner_is_read(recv, head):
    body = ("from click import testing\n"
            "from click.testing import CliRunner\n"
            "from src.click.utils import echo_json\n\n\n"
            f"def test_x(runner):\n{head}"
            f"    assert {recv}.invoke(echo_json, []).exit_code == 0\n")
    got = _plain_invoked(ast.parse(body), "tests/test_x.py",
                         _reader({"src/click/utils.py": UTILS}))
    assert got is not None and got[2:4] == ("src/click/utils.py", 8)


def test_the_root_without_the_name_and_the_worktree_with_a_command_admits(db):
    """The root lacks `echo_json`, the worktree has it decorated: the test
    runs against a command."""
    _utils(_wt(db)).write_bytes(
        (ROOT_UTILS + "\n\n@command()\ndef echo_json(obj):\n    pass\n").encode())
    body = ("from click.testing import CliRunner\n"
            "from src.click.utils import echo_json\n\n\n"
            "def test_x():\n"
            "    result = CliRunner().invoke(echo_json, [])\n"
            "    assert result.exit_code == 0\n")
    assert _encode(db, "tst_x", "tests/test_x.py", body) == {"id": "tst_x"}


def test_the_worktree_is_read_and_not_the_root(db):
    """The fixture's root has no `echo_json`, so a reader of the root admits
    s139's body. The door refuses it, so it read the worktree."""
    assert "echo_json" not in _utils(_root(db)).read_text()
    with pytest.raises(ValueError, match="is a plain function"):
        _encode(db, *S139[0])


def test_an_uncommitted_write_in_the_worktree_is_read(db):
    """The worktree's working file, not a commit: the Developer's write
    before `code.commit` is the file the test runs against."""
    wt = _wt(db)
    for cmd in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "work"]):
        subprocess.run(["git", "-C", str(wt), *cmd], check=True, capture_output=True)
    _utils(wt).write_bytes(ROOT_UTILS.encode())
    _not_this_door(db, S139[0][2], *S139[0][:2])


def test_a_session_with_no_batch_reads_the_root(db):
    db.execute("UPDATE batches SET worktree = NULL")
    db.commit()
    # Frame 204 pass 1 (b00aaa59): the literal door stages its row and
    # refuses no encode. The root has no `echo_json`, so the body is admitted.
    _not_this_door(db, S139[0][2], batch_id=None)
    _utils(_root(db)).write_bytes(UTILS.encode())
    with pytest.raises(ValueError) as exc:
        _encode(db, *S139[0], batch_id=None)
    assert str(exc.value) == _said(S139[0][0])


def test_no_project_root_admits(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    ctx = type("C", (), {"conn": conn, "batch_id": None})()
    in_batch, read = api._run_tree_reader(ctx)
    assert not in_batch and read("x.py") is None


def test_the_refusal_goes_through_the_follow_and_fact_checks(db):
    """The path of frame 144's dry run, as `test_scalar_door._refused` takes
    it: the refusal names no call, so nothing is followed. The one fact it
    quotes is the `def` line, and the check reads it in the worktree."""
    def refused():
        got = []
        prev, sandbox._ON_REFUSAL = sandbox._ON_REFUSAL, lambda *a: got.append(a)
        try:
            with pytest.raises(ValueError):
                _encode(db, *S139[0])
        finally:
            sandbox._ON_REFUSAL = prev
        assert len(got) == 1, "the refusal reached no follow check"
        return got[0]

    sb, name, args, exc, offers, facts = refused()
    assert offers == []
    assert sandbox.follow(sb, name, args, exc, offers) == []
    checked = sandbox.check_facts(sb, facts)
    assert [(f["kind"], f["value"], f["where"]) for f in checked] == [
        ("line_text", "def echo_json", {"n": 7, "path": "src/click/utils.py"})]
    assert all(f["ok"] for f in checked), checked
    # The check reads the file the seat sees, so a moved line fails it.
    _utils(_wt(db)).write_bytes(("\n" + UTILS).encode())
    assert not any(f["ok"] for f in sandbox.check_facts(sb, facts))


def _git_reader(sha: str):
    seen: dict = {}

    def read(path: str):
        if path not in seen:
            out = subprocess.run(["git", "-C", str(CLICKI), "show", f"{sha}:{path}"],
                                 capture_output=True, text=True, encoding="utf-8",
                                 errors="replace")
            seen[path] = out.stdout if out.returncode == 0 else None
        return seen[path]
    return read


def _night(n: int) -> tuple[sqlite3.Connection, str]:
    """A night's database, read-only, and the batch's base: the commit of
    the night's first test run, the Developer's first commit, which adds
    `echo_json` (frame 131's review of af9db8a0).

    `mode=ro` alone: `immutable=1` ignores the WAL file, and rows in a WAL
    would then be missing from the counts (the second look at d8dd62cd)."""
    conn = sqlite3.connect(
        f"file:{(NIGHTS / f'clickI_night{n}.db').as_posix()}?mode=ro", uri=True)
    sha = conn.execute("SELECT commit_sha FROM test_runs WHERE commit_sha IS NOT "
                       "NULL ORDER BY rowid LIMIT 1").fetchone()[0]
    return conn, sha


def _have_nights() -> bool:
    """The eight databases, and each night's base commit in the clickI
    clone. A clone without the night commits gives no base to read."""
    if not ((CLICKI / ".git").exists() and all(
            (NIGHTS / f"clickI_night{n}.db").is_file() for n in EIGHT)):
        return False
    for n in EIGHT:
        try:
            conn, sha = _night(n)
            conn.close()
        except (sqlite3.Error, TypeError):
            return False
        if subprocess.run(["git", "-C", str(CLICKI), "cat-file", "-e",
                           f"{sha}^{{commit}}"], capture_output=True).returncode:
            return False
    return True


_HAVE_NIGHTS = _have_nights()


@pytest.mark.skipif(not _HAVE_NIGHTS,
                    reason="the night databases or their commits in clickI are absent")
def test_the_stored_rows_of_eight_nights():
    """Every stored test with an `.invoke` call on nights 119 to 126, against
    the batch's base: 186 rows, 10 refused, each a test of s139."""
    rows, refused = 0, []
    for night in EIGHT:
        conn, sha = _night(night)
        try:
            stored = conn.execute("SELECT id, path, body FROM tests").fetchall()
        finally:
            conn.close()
        read = _git_reader(sha)
        for test_id, path, body in stored:
            try:
                tree = ast.parse(body or "")
            except SyntaxError:
                continue
            if not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                       and n.func.attr == "invoke" for n in ast.walk(tree)):
                continue
            rows += 1
            got = _plain_invoked(tree, path, read)
            if got:
                refused.append((night, test_id, got[2], got[3]))
    assert rows == 186
    assert sorted(refused) == sorted(
        [(n, f"inh_echo_json_{k}", "src/click/utils.py", 689) for n, k in [
            (119, "01"), (119, "02"), (121, "01"), (123, "01"), (123, "03"),
            (124, "01"), (124, "02"), (124, "03"), (126, "01"), (126, "02")]])


@pytest.mark.skipif(not _HAVE_NIGHTS,
                    reason="the night databases or their commits in clickI are absent")
def test_the_tester_encodes_of_eight_nights():
    """Every Tester encode on nights 119 to 126, against the batch's base:
    78 refused, 70 of s139 and 8 on night 121. Night 120 holds no
    refusal of s139. s229 invokes `confirm` and
    s302 and s312 invoke `version_option`, both plain functions there."""
    refused: collections.Counter = collections.Counter()
    names: set = set()
    for night in EIGHT:
        conn, sha = _night(night)
        try:
            turns = conn.execute(
                "SELECT t.session_id, t.completion FROM turns t JOIN sessions s "
                "ON s.id = t.session_id WHERE s.role = 'tester'").fetchall()
        finally:
            conn.close()
        read = _git_reader(sha)
        for sid, completion in turns:
            for call in toolproto.extract(completion or ""):
                args = getattr(call, "args", None)
                if (getattr(call, "name", None) != "tests.encode"
                        or not isinstance(args, dict) or "body" not in args):
                    continue
                try:
                    tree = ast.parse(str(args["body"]))
                except SyntaxError:
                    continue
                got = _plain_invoked(tree, str(args.get("path", "")), read)
                if got:
                    refused[(night, sid)] += 1
                    names.add(got[1])
    assert sum(refused.values()) == 78
    assert {k: v for k, v in refused.items() if k[1] != "s139"} == {
        (121, "s229"): 1, (121, "s302"): 3, (121, "s312"): 4}
    assert {k: v for k, v in refused.items() if k[1] == "s139"} == {
        (n, "s139"): 10 for n in EIGHT if n != 120}
    assert names == {"echo_json", "confirm", "version_option"}


# Frame 230: s154's bodies on night 148, read from `.rota/clickI_night148.db`,
# `turns.completion` of s154. Turn 2 holds s154's first call with a lambda,
# and turn 5's first call is the version that landed in bg_2. Each stayed
# red on `'function' object has no attribute 'name'`.
S154_T2 = ('from click.testing import CliRunner\nfrom click.termui import confirm\n'
           'import io\n\ndef test_confirm_eof_returns_default():\n'
           '    runner = CliRunner()\n    with runner.isolated_filesystem():\n'
           '        # Test that when stdin is closed (EOF), confirm returns the default\n'
           '        result = runner.invoke(lambda: confirm("y", default_on_eof=True))\n'
           '        assert result.exit_code == 0')
S154_T5 = ('from click.testing import CliRunner\nfrom click.termui import confirm\n'
           'import io\n\ndef test_confirm_eof_returns_default(monkeypatch):\n'
           '    runner = CliRunner()\n    with runner.isolated_filesystem():\n'
           '        # Test that when stdin is closed (EOF), confirm returns the default\n'
           '        monkeypatch.setattr("sys.stdin", io.StringIO(""))\n'
           '        result = runner.invoke(lambda: confirm("y", default_on_eof=True))\n'
           '        assert result.exit_code == 0')


@pytest.mark.parametrize("body", [S154_T2, S154_T5], ids=["turn2", "turn5"])
def test_s154s_lambda_is_refused_and_named(db, body):
    """The refusal says what the seat passed and names a click command as
    what `invoke` takes, in one sentence. A second sentence gives the step."""
    with pytest.raises(ValueError) as exc:
        _encode(db, "tst_confirm_eof_returns_default",
                "tests/test_confirm_eof.py", body)
    assert str(exc.value) == (
        "the test tst_confirm_eof_returns_default passes a lambda to "
        "`.invoke`, and `CliRunner.invoke` takes a click command, not a "
        "plain function. Pass a function that `@click.command` decorates, "
        "or call the function without a runner.")
    assert not isinstance(exc.value, api.Wall)


def test_a_command_the_test_defines_or_the_surface_holds_is_admitted(db):
    """A local `def` under `@command()` and the surface's `hello`, a
    command in `core.py`, both stay admitted."""
    body = ("from click import command\n"
            "from click.testing import CliRunner\n"
            "from src.click.core import hello\n\n\n"
            "@command()\n"
            "def cli():\n"
            "    pass\n\n\n"
            "def test_x():\n"
            "    runner = CliRunner()\n"
            "    assert runner.invoke(cli, []).exit_code == 0\n"
            "    assert runner.invoke(hello, []).exit_code == 0\n")
    assert _encode(db, "tst_x", "tests/test_x.py", body) == {"id": "tst_x"}


@pytest.mark.parametrize("body,want", [
    ("f = lambda: 1\n\ndef test_x():\n    runner.invoke(f)\n", ("f", 4)),
    # F12's pass 1b: a runner is a class the body imports from a library's
    # `testing` module, so the body imports it.
    ("from click.testing import CliRunner\n\n"
     "def test_x():\n    CliRunner().invoke(cli=lambda: 1)\n", (None, 4)),
    ("def f():\n    pass\n\nf = command()(f)\n\n"
     "def test_x():\n    runner.invoke(f)\n", None),
    ("def test_x(f):\n    runner.invoke(f)\n", None),
    ("def test_x(ctx):\n    ctx.invoke(lambda: 1)\n", None),
], ids=["bound-lambda", "keyword", "wrapped", "parameter", "context"])
def test_the_callable_reader(body, want):
    assert api._callable_invoked(ast.parse(body)) == want


def test_s291s_version_option_keeps_frame_131s_refusal():
    """Night 145's s291 passed the imported `version_option` to `.invoke`.
    Frame 131's door reads it, and frame 230's door does not."""
    body = ("from click.testing import CliRunner\n"
            "from click.decorators import version_option\n\n"
            "def test_custom_version_option_receives_context():\n"
            "    runner = CliRunner()\n"
            "    result = runner.invoke(version_option)\n"
            '    assert "Python" not in result.output')
    tree = ast.parse(body)
    got = _plain_invoked(tree, "tests/test_v.py", _reader(
        {"src/click/decorators.py": "def version_option(*a, **k):\n    pass\n"}))
    assert got is not None and got[:3] == (
        "version_option", "version_option", "src/click/decorators.py")
    assert api._callable_invoked(tree) is None


