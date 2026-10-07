"""
Frame 177: the prints door reads the kind of the function it guards.

On night 128 the prints door of `tests.encode` refused 5 encodes of the
Tester s274 at turn 2, verbatim: `the test uses what version_option returns,
and the criterion c2_version_option_show_python says it prints`.
`version_option` is a decorator factory. The `--version` callback of the
command it decorates prints, and the factory itself prints nothing. The seat
then stored 3 tests that read the stdout of `version_option(show_python=True)`,
which no code can pass, and bg_3 ended `Stuck` (plans/night128-read.md,
section 3).

The door now reads the definition of the name in the batch's worktree, as
frame 131's door does. A `def` that returns a decorator or a command is not
refused. A refusal on a plain function names that kind.
"""
from __future__ import annotations

import ast
import shutil
import sqlite3
import subprocess
from pathlib import Path

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.llm import toolproto
from rota.roles import api
from rota.roles.api import _returns_factory

NIGHT = Path("D:/repos/rota/.rota/clickI_night128.db")
CLICKI = Path("D:/repos/_AI/sample_repos/clickI")
# clickI's `main` on night 128, and the worktree's last commit before s274
# woke: s264's 191e47a6, where `version_option` returns an inner `def`.
BASE, HEAD = "39fbe93", "191e47a6"
DECORATORS = "src/click/decorators.py"


def _show(sha: str, path: str) -> str | None:
    out = subprocess.run(["git", "-C", str(CLICKI), "show", f"{sha}:{path}"],
                         capture_output=True, text=True, encoding="utf-8",
                         errors="replace")
    return out.stdout if out.returncode == 0 else None


def _night() -> sqlite3.Connection:
    """`mode=ro` alone: `immutable=1` ignores the WAL file."""
    return sqlite3.connect(f"file:{NIGHT.as_posix()}?mode=ro", uri=True)


def _have_night() -> bool:
    if not (NIGHT.is_file() and (CLICKI / ".git").exists()):
        return False
    return _show(BASE, DECORATORS) is not None and _show(HEAD, DECORATORS) is not None


_HAVE_NIGHT = _have_night()


def _s274_turn2() -> list[dict]:
    """s274's six encodes at turn 2, as the seat sent them."""
    conn = _night()
    try:
        completion = conn.execute("SELECT completion FROM turns WHERE "
                                  "session_id = 's274' AND seq = 2").fetchone()[0]
    finally:
        conn.close()
    return [c.args for c in toolproto.extract(completion)
            if getattr(c, "name", None) == "tests.encode"]


def _project(tmp_path: Path, base: dict, work: dict) -> tuple[Path, Path]:
    """A git root holding `base`, and a worktree that is a copy of the root
    with `work` written over it."""
    root = tmp_path / "project"
    for rel, text in base.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(text.encode())
    for cmd in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "base"]):
        subprocess.run(["git", "-C", str(root), *cmd], check=True,
                       capture_output=True)
    wt = tmp_path / "wt"
    shutil.copytree(root / "src", wt / "src")
    for rel, text in work.items():
        (wt / rel).parent.mkdir(parents=True, exist_ok=True)
        (wt / rel).write_bytes(text.encode())
    return root, wt


def _db(tmp_path: Path, root: Path, wt: Path, ticket: str,
        criteria: list[tuple[str, str, str]]) -> sqlite3.Connection:
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
                 "('project_root', ?)", (str(root),))
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1','the item','in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1',?)",
                 (ticket,))
    for cid, text, refs in criteria:
        conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                     "VALUES (?,'tk1',?,?)", (cid, text, refs))
    conn.execute("INSERT INTO batches (id, item_id, status, worktree) VALUES "
                 "('b1','i1','running',?)", (str(wt),))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b1','tk1')")
    conn.commit()
    return conn


def _encode(db, test_id, criterion_id, path, body):
    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id=criterion_id, verdict="encodable")
    return sb.call("tests.encode", id=test_id, criterion_id=criterion_id,
                   path=path, body=body)


@pytest.fixture
def night128(tmp_path):
    """bg_3 on night 128: clickI's `main` as the root, the worktree at
    191e47a6, and the six criteria and the ticket of s274's batch."""
    root, wt = _project(
        tmp_path,
        {"src/click/__init__.py": "", DECORATORS: _show(BASE, DECORATORS)},
        {DECORATORS: _show(HEAD, DECORATORS)})
    conn = _night()
    try:
        rows = conn.execute("SELECT id, text, surface_refs FROM criteria WHERE "
                            "ticket_id = 'tk_1_version_option_show_python'").fetchall()
        ticket = conn.execute("SELECT text FROM tickets WHERE "
                              "id = 'tk_1_version_option_show_python'").fetchone()[0]
    finally:
        conn.close()
    return _db(tmp_path, root, wt, ticket, rows)


@pytest.mark.skipif(not _HAVE_NIGHT,
                    reason="night 128's database or clickI's commits are absent")
def test_s274s_turn_2_encode_on_a_decorator_factory_lands(night128):
    """`tst_version_option_show_python_04` is the encode on c4, refused on
    night 128 by this door. Its body reads what `version_option` returns."""
    sent = {a["id"]: a for a in _s274_turn2()}
    assert len(sent) == 6
    a = sent["tst_version_option_show_python_04"]
    assert "result_true = version_option(show_python=True)" in a["body"]
    got = _encode(night128, a["id"], a["criterion_id"], a["path"], a["body"])
    assert got == {"id": a["id"]}


@pytest.mark.skipif(not _HAVE_NIGHT,
                    reason="night 128's database or clickI's commits are absent")
def test_no_encode_of_s274s_turn_2_meets_the_prints_door(night128):
    """The five that the door refused on night 128. Another door may still
    refuse one of them, and that door is not this frame's."""
    for a in _s274_turn2():
        try:
            _encode(night128, a["id"], a["criterion_id"], a["path"], a["body"])
        except ValueError as exc:
            assert "returns, and the criterion" not in str(exc), str(exc)


# A worktree whose `echo_json` is a plain function that prints.
UTILS = '''\
import json


def echo(message=None):
    print(message)


def echo_json(obj: object) -> None:
    echo(json.dumps(obj))
'''

PLAIN_BODY = ("from click.utils import echo_json\n\n\n"
              "def test_x():\n"
              "    result = echo_json({'a': 1})\n"
              "    assert result.startswith('{')\n")


def test_a_refusal_on_a_plain_function_names_the_kind(tmp_path):
    root, wt = _project(tmp_path, {"src/click/__init__.py": "",
                                   "src/click/utils.py": "import json\n"},
                        {"src/click/utils.py": UTILS})
    db = _db(tmp_path, root, wt, "add an echo_json helper",
             [("c1", "echo_json prints the object as JSON",
               '["src/click/utils.py::echo_json"]')])
    with pytest.raises(ValueError) as exc:
        _encode(db, "tst_x", "c1", "tests/test_x.py", PLAIN_BODY)
    assert str(exc.value) == (
        "the test uses what echo_json returns, and the criterion c1 says it "
        "prints: `echo_json` is a plain function in `src/click/utils.py`")
    assert not isinstance(exc.value, api.Wall)


def test_the_kind_is_a_fact_that_the_check_reads_in_the_worktree(tmp_path):
    """The one fact the clause quotes is the `def` line, as frame 131's
    door quotes it, and the check reads it in the worktree."""
    from rota.core import sandbox

    root, wt = _project(tmp_path, {"src/click/__init__.py": "",
                                   "src/click/utils.py": "import json\n"},
                        {"src/click/utils.py": UTILS})
    db = _db(tmp_path, root, wt, "add an echo_json helper",
             [("c1", "echo_json prints the object as JSON",
               '["src/click/utils.py::echo_json"]')])
    got = []
    prev, sandbox._ON_REFUSAL = sandbox._ON_REFUSAL, lambda *a: got.append(a)
    try:
        with pytest.raises(ValueError):
            _encode(db, "tst_x", "c1", "tests/test_x.py", PLAIN_BODY)
    finally:
        sandbox._ON_REFUSAL = prev
    assert len(got) == 1
    sb, _name, _args, _exc, _offers, facts = got[0]
    checked = sandbox.check_facts(sb, facts)
    assert [(f["kind"], f["value"], f["where"]) for f in checked] == [
        ("line_text", "def echo_json", {"n": 7, "path": "src/click/utils.py"})]
    assert all(f["ok"] for f in checked), checked


@pytest.mark.parametrize("files,body", [
    ({}, PLAIN_BODY),
    ({"src/click/utils.py": "import json\n"}, PLAIN_BODY),
    ({"src/click/utils.py": "from .core import echo_json\n"}, PLAIN_BODY),
    ({"src/click/utils.py": UTILS},
     "def echo_json(obj):\n    return obj\n\n\n"
     "def test_x():\n    assert echo_json(1) == 1\n"),
], ids=["no-file", "no-binding", "re-export", "the-tests-own"])
def test_no_definition_leaves_the_door_as_before(files, body):
    """No definition to read: the door neither lifts nor names a kind. The
    import door refuses a name the worktree lacks before this door runs,
    so this reads the helper and not an encode."""
    got = api._definition_of(ast.parse(body), "tests/test_x.py", "echo_json",
                             ["src/click/utils.py::echo_json"], files.get)
    assert got is None


def test_a_surface_ref_finds_a_name_the_test_reaches_by_attribute():
    body = "import click\n\n\ndef test_x():\n    assert click.echo_json(1)\n"
    got = api._definition_of(ast.parse(body), "tests/test_x.py", "echo_json",
                             ["src/click/utils.py::echo_json"],
                             {"src/click/utils.py": UTILS}.get)
    assert got is not None and got[:2] == ("echo_json", "src/click/utils.py")


def _def(src: str):
    return ast.parse(src).body[0]


@pytest.mark.parametrize("src", [
    "def f():\n    def decorator(g):\n        return g\n    return decorator\n",
    "def f(*decls, **kw):\n    return option(*decls, **kw)\n",
    "def f(*decls, **kw):\n    return click.argument(*decls, **kw)\n",
    "def f(name):\n    return command(name)\n",
    "def f(name):\n    return group(name)\n",
    "def f(name):\n    return click.Command(name)\n",
    "def f(name):\n    return Group(name)\n",
], ids=["inner-def", "option", "argument", "command", "group", "Command", "Group"])
def test_a_def_that_returns_a_decorator_or_a_command_is_a_factory(src):
    assert _returns_factory(_def(src))


@pytest.mark.parametrize("src", [
    "def f(obj):\n    print(obj)\n",
    "def f(obj):\n    return str(obj)\n",
    "def f():\n    def g():\n        return option()\n    return g()\n",
    "class f:\n    pass\n",
    "f = 1\n",
], ids=["prints", "returns-a-value", "inner-return-only", "class", "assignment"])
def test_any_other_binding_is_not_a_factory(src):
    assert not _returns_factory(_def(src))
