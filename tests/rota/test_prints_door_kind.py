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
from rota.testkit.gitfixture import copy_template

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
    # A copy of the two trees built once per process for these files. The
    # git calls per test were the file's cost (frame 206's count, 2026-10-11).
    key = ("door_kind_project", tuple(sorted(base.items())),
           tuple(sorted(work.items())))
    copy_template(key, lambda b: _build_project(b, base, work), tmp_path)
    return tmp_path / "project", tmp_path / "wt"


def _build_project(tmp_path: Path, base: dict, work: dict) -> None:
    """Build `_project`'s root and worktree under `tmp_path`."""
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


def _click_files(sha: str) -> dict:
    out = subprocess.run(["git", "-C", str(CLICKI), "ls-tree", "-r", "--name-only",
                          sha, "src/click"], capture_output=True, text=True,
                         check=True)
    return {p: _show(sha, p) for p in out.stdout.split()}


@pytest.fixture
def night128(tmp_path):
    """bg_3 on night 128: clickI's `main` as the root, the worktree's
    `src/click` at 191e47a6, and the six criteria and the ticket of s274's
    batch."""
    # The key is the two commits, so the clickI reads run once per process
    # too. They were 36 git calls a setup (frame 206's count, 2026-10-11).
    copy_template(("door_kind_night128", BASE, HEAD),
                  lambda b: _build_project(b, _click_files(BASE), _click_files(HEAD)),
                  tmp_path)
    root, wt = tmp_path / "project", tmp_path / "wt"
    conn = _night()
    try:
        rows = conn.execute("SELECT id, text, surface_refs FROM criteria WHERE "
                            "ticket_id = 'tk_1_version_option_show_python'").fetchall()
        ticket = conn.execute("SELECT text FROM tickets WHERE "
                              "id = 'tk_1_version_option_show_python'").fetchone()[0]
    finally:
        conn.close()
    return _db(tmp_path, root, wt, ticket, rows)


FACTORY = ("`version_option` is a decorator factory in `src/click/decorators.py`: "
           "it returns a decorator and prints nothing when it is called")


def test_the_factory_refusal_names_no_shape():
    """The fact and no shape (Roman, 2026-09-15, 6b52a09d). It says nothing
    of when a decorated command prints, because that differs per factory
    (frame 177's review of 5336f2a6)."""
    for word in ("CliRunner", "invoke", "result.output", "Decorate", "assert",
                 "message", "runs"):
        assert word not in FACTORY


needs_night = pytest.mark.skipif(
    not _HAVE_NIGHT, reason="night 128's database or clickI's commits are absent")


def _outcome(db, a: dict) -> str:
    try:
        _encode(db, a["id"], a["criterion_id"], a["path"], a["body"])
    except ValueError as exc:
        return str(exc)
    return "landed"


@needs_night
def test_s274s_turn_2_encodes_meet_the_factory_door(night128):
    """On night 128 the prints door refused 02 to 06 and admitted 01. Each
    of 01 and 03 to 06 asserts `in` on the decorator, so no code passes it,
    and the factory door now refuses it. 02 asserts `True` inside a `try`
    and reads nothing that the call returns, so this door admits it."""
    sent = {a["id"]: a for a in _s274_turn2()}
    assert len(sent) == 6
    got = {tid[-2:]: _outcome(night128, a) for tid, a in sorted(sent.items())}
    assert got == {"01": FACTORY, "02": "landed", "03": FACTORY,
                   "04": FACTORY, "05": FACTORY, "06": FACTORY}


def _stored_128() -> dict:
    conn = _night()
    try:
        return {r[0]: {"id": r[0], "criterion_id": r[1], "path": r[2], "body": r[3]}
                for r in conn.execute(
                    "SELECT id, criterion_id, path, body FROM tests "
                    "WHERE id LIKE 'tst_version_option_show_python_%'")}
    finally:
        conn.close()


@needs_night
def test_the_stdout_tests_stored_on_night_128_are_refused(night128):
    """01, 04 and 06 read `"Python"` in the stdout of a bare call and were
    red at 191e47a6. 03 and 05 read the same stdout and passed for nothing.
    02 swaps stdout and never reads it, so it meets no shape of this door."""
    stored = _stored_128()
    got = {tid[-2:]: _outcome(night128, a) for tid, a in sorted(stored.items())}
    for k in ("01", "03", "04", "05", "06"):
        assert got[k] == FACTORY, (k, got[k])
    assert got["02"] != FACTORY


def _turn_encodes(night: int, sid: str, seq: int) -> list[dict]:
    conn = sqlite3.connect(f"file:{(NIGHT.parent / f'clickI_night{night}.db').as_posix()}"
                           f"?mode=ro", uri=True)
    try:
        completion = conn.execute("SELECT completion FROM turns WHERE "
                                  "session_id = ? AND seq = ?", (sid, seq)).fetchone()[0]
    finally:
        conn.close()
    return [c.args for c in toolproto.extract(completion)
            if getattr(c, "name", None) == "tests.encode"]


def _lands_after_the_ledger(db, a: dict) -> bool:
    """The encode lands, or lands once the literal door's offered ledger
    line is logged. The literal door is another door, and its offer is the
    seat's next move on a night."""
    import re

    sb = build("tester", db, batch_id="b1", mode="tests_missing")
    sb.call("tests.triage", criterion_id=a["criterion_id"], verdict="encodable")
    args = dict(id=a["id"], criterion_id=a["criterion_id"], path=a["path"],
                body=a["body"])
    try:
        sb.call("tests.encode", **args)
        return True
    except ValueError as exc:
        m = re.search(r'assumption="(the test assumes [^"]+)"', str(exc))
        assert str(exc).startswith("the test chooses ") and m, str(exc)
    sb.call("ledger.log", about_ref=a["criterion_id"], about_table="criteria",
            assumption=m.group(1))
    return sb.call("tests.encode", **args) == {"id": a["id"]}


def _have_lifts() -> bool:
    return _HAVE_NIGHT and all(
        (NIGHT.parent / f"clickI_night{n}.db").is_file() for n in (119, 127))


# The criteria of night 128 that carry each lift's claim. The lifts were
# written for nights 119 and 127, whose criteria ids differ.
_ON_128 = {"c1_version_option_show_python": "c1_version_option_show_python",
           "c2_version_option_show_python": "c2_version_option_show_python",
           "c3_version_option_show_python": "c3_version_option_show_python",
           "cr_1_version_option_show_python_flag": "c2_version_option_show_python",
           "cr_2_version_option_show_python_false": "c5_version_option_show_python",
           "cr_3_version_option_show_python_true": "c4_version_option_show_python"}


@pytest.mark.skipif(not _have_lifts(), reason="the night databases are absent")
@pytest.mark.parametrize("night,sid,seq", [
    (119, "s247", 4), (119, "s247", 8), (127, "s267", 2), (127, "s267", 10),
], ids=["s247-decorates", "s247-is-not-none", "s267-is-not-none",
        "s267-decorates-and-invokes"])
def test_the_lifts_of_nights_119_and_127_still_land(night128, night, sid, seq):
    """s247 decorated a `def` and checked `opt is not None`. s267 checked
    `decorator is not None`, then decorated a command and invoked it with
    CliRunner. Each body is encoded against night 128's worktree."""
    sent = _turn_encodes(night, sid, seq)
    assert sent
    for a in sent:
        a = dict(a, criterion_id=_ON_128[a["criterion_id"]])
        assert _lands_after_the_ledger(night128, a), a["body"]


@needs_night
def test_a_test_that_decorates_a_command_and_invokes_it_lands(night128):
    body = ("from click.decorators import command, version_option\n"
            "from click.testing import CliRunner\n\n\n"
            "def test_python_in_version():\n"
            "    @command()\n"
            "    @version_option(show_python=True)\n"
            "    def cli():\n"
            "        pass\n\n"
            "    result = CliRunner().invoke(cli, ['--version'])\n"
            "    assert 'Python' in result.output\n")
    a = {"id": "tst_dec", "criterion_id": "c4_version_option_show_python",
         "path": "tests/test_dec.py", "body": body}
    assert _outcome(night128, a) == "landed"


@needs_night
def test_the_factory_refusal_states_a_fact_of_the_worktree(night128):
    from rota.core import sandbox

    a = {a["id"]: a for a in _s274_turn2()}["tst_version_option_show_python_04"]
    got = []
    prev, sandbox._ON_REFUSAL = sandbox._ON_REFUSAL, lambda *x: got.append(x)
    try:
        assert _outcome(night128, a) == FACTORY
    finally:
        sandbox._ON_REFUSAL = prev
    sb, name, args, exc, offers, facts = got[0]
    assert offers == [] and sandbox.follow(sb, name, args, exc, offers) == []
    checked = sandbox.check_facts(sb, facts)
    assert [(f["kind"], f["value"]) for f in checked] == [
        ("line_text", "def version_option")]
    assert all(f["ok"] for f in checked), checked


@pytest.mark.parametrize("body,shape", [
    ("r = f()\nassert 'x' in r\n", "return"),
    ("assert f() == 'x'\n", "return"),
    ("r = f()\nassert r\n", "return"),
    ("assert not f()\n", "return"),
    ("assert 'x' in str(f())\n", "return"),
    ("r = f()\nassert len(r) > 1\n", "return"),
    ("f()\nout = capsys.readouterr().out\nassert 'x' in out\n", "stdout"),
    ("sys.stdout = io.StringIO()\nf()\nassert 'x' in sys.stdout.getvalue()\n", "stdout"),
    ("r = f()\nassert r is not None\n", None),
    ("assert callable(f())\n", None),
    ("@f()\ndef g():\n    pass\n", None),
    ("cmd = command()(f()(g))\n", None),
    ("r = f()\nr = 1\nassert r == 1\n", None),
    ("r = f()\nfor r in [1]:\n    pass\nassert r == 1\n", None),
    ("r = f()\nwith open('a') as r:\n    pass\nassert r == 1\n", None),
    ("r = f()\nr += 1\nassert r == 1\n", None),
    ("f()\n", None),
    ("import click as c\nassert 'x' in c.f()\n", "return"),
    ("from click import decorators as d\nassert 'x' in d.f()\n", "return"),
    ("assert 'x' in other.f()\n", None),
], ids=["in", "eq", "bare-assert", "not", "str", "len", "capsys", "stringio",
        "is-not-none", "callable", "decorates", "applied", "rebound",
        "rebound-for", "rebound-with", "rebound-augassign", "no-read",
        "click-alias", "from-click", "other-object"])
def test_the_shapes_of_a_factory_misuse(body, shape):
    assert api._factory_misuse(ast.parse(body), "f") == shape


def test_a_regex_group_is_no_call_to_the_factory_group():
    """`m.group(1)` on a match object reads nothing that click's `group`
    returns (frame 177's review of 5336f2a6)."""
    body = ("import re\n\n\ndef test_x():\n"
            "    m = re.match('(a)', 'a')\n"
            "    assert m.group(1) == 'a'\n")
    assert api._factory_misuse(ast.parse(body), "group") is None


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
    "import click\n\ndef f(*decls, **kw):\n    return click.argument(*decls, **kw)\n",
    "def f(name):\n    return command(name)\n",
    "def f(name):\n    return group(name)\n",
    "import click\n\ndef f(name):\n    return click.Command(name)\n",
    "def f(name):\n    return Group(name)\n",
], ids=["inner-def", "option", "argument", "command", "group", "Command", "Group"])
def test_a_def_that_returns_a_decorator_or_a_command_is_a_factory(src):
    # F12's pass 1c: the attribute form reads the module's own imports, so
    # the two `click.` cases carry the module's `import click`.
    assert _returns_factory(ast.parse(src).body[-1], src)


@pytest.mark.parametrize("src", [
    "def f(obj):\n    print(obj)\n",
    "def f(obj):\n    return str(obj)\n",
    "def f():\n    def g():\n        return option()\n    return g()\n",
    "class f:\n    pass\n",
    "f = 1\n",
    "def f(s):\n    m = re.match('(a)', s)\n    return m.group(1)\n",
    "def f(self):\n    return self.command()\n",
], ids=["prints", "returns-a-value", "inner-return-only", "class", "assignment",
        "regex-group", "method"])
def test_any_other_binding_is_not_a_factory(src):
    assert not _returns_factory(_def(src))


@pytest.mark.parametrize("head,call,factory", [
    ("import click as c\n", "c.group()", True),
    ("from click import decorators as d\n", "d.command()", True),
    ("import click.decorators\n", "click.command()", True),
    ("import re\n", "re.group()", False),
    ("from .core import thing\n", "thing.command()", False),
], ids=["click-alias", "from-click", "click-submodule", "other-module", "relative"])
def test_the_attribute_form_counts_on_a_click_name_only(head, call, factory):
    src = f"{head}\n\ndef f():\n    return {call}\n"
    assert _returns_factory(ast.parse(src).body[-1], src) is factory


def _echo_db(tmp_path, utils: str, criterion: str, ticket: str = "add an echo_json helper",
             batch: bool = True):
    root, wt = _project(tmp_path, {"src/click/__init__.py": "",
                                   "src/click/utils.py": utils if not batch else "import json\n"},
                        {"src/click/utils.py": utils})
    db = _db(tmp_path, root, wt, ticket,
             [("c1", criterion, '["src/click/utils.py::echo_json"]')])
    if not batch:
        db.execute("UPDATE batches SET worktree = NULL")
        db.commit()
    return db


def _refused(db, body, batch_id="b1"):
    from rota.core import sandbox

    got = []
    prev, sandbox._ON_REFUSAL = sandbox._ON_REFUSAL, lambda *x: got.append(x)
    try:
        sb = build("tester", db, batch_id=batch_id, mode="tests_missing")
        sb.call("tests.triage", criterion_id="c1", verdict="encodable")
        with pytest.raises(ValueError) as exc:
            sb.call("tests.encode", id="tst_x", criterion_id="c1",
                    path="tests/test_x.py", body=body)
    finally:
        sandbox._ON_REFUSAL = prev
    # The hook fires only on a refusal with an offer or a fact.
    return str(exc.value), got[0][5] if got else []


def test_the_offer_refusal_carries_the_kind_clause(tmp_path):
    """The criterion's own words do not say it prints, and the ticket's do.
    So the door offers the ledger line, and the sentence names the kind."""
    db = _echo_db(tmp_path, UTILS, "the helper formats the object as JSON",
                  ticket="add a helper that prints an object as JSON")
    said, _facts = _refused(db, PLAIN_BODY)
    assert said == (
        "the test uses what echo_json returns, and the criterion, its ticket "
        "or the principal's words say it prints: `echo_json` is a plain "
        "function in `src/click/utils.py`; nothing says it returns anything. "
        "That is an assumption, and it is logged where it is made: "
        "ledger.log(about_ref='c1', about_table='criteria', assumption=\"the "
        "test assumes echo_json returns what it prints\", kind='default') -- "
        "then send this encode again unchanged. Or assert on what it prints")


def test_a_refusal_with_no_batch_records_no_fact(tmp_path):
    """With no batch the door reads the root, and the fact check reads the
    worktree. So the clause stays and no fact is recorded, as in frame
    131's door."""
    db = _echo_db(tmp_path, UTILS, "echo_json prints the object as JSON",
                  batch=False)
    said, facts = _refused(db, PLAIN_BODY, batch_id=None)
    assert said.endswith(": `echo_json` is a plain function in `src/click/utils.py`")
    assert facts == []


def test_a_decorated_def_gets_no_kind_clause(tmp_path):
    utils = UTILS.replace("def echo_json", "@pass_context\ndef echo_json")
    db = _echo_db(tmp_path, utils, "echo_json prints the object as JSON")
    said, _facts = _refused(db, PLAIN_BODY)
    assert said == ("the test uses what echo_json returns, and the criterion "
                    "c1 says it prints")


EXTRA = '''\
import click as c


def name_option(*decls, **kw):
    return c.option(*decls, **kw)
'''


def test_a_factory_through_an_aliased_click_import_meets_the_door(tmp_path):
    """The definition returns `c.option(...)` with `import click as c`, so
    the door reads the module's own imports to know the call is click's."""
    root, wt = _project(tmp_path, {"src/click/__init__.py": "",
                                   "src/click/extra.py": "import json\n"},
                        {"src/click/extra.py": EXTRA})
    db = _db(tmp_path, root, wt, "add a name_option helper",
             [("c1", "name_option adds a --name option to a command",
               '["src/click/extra.py::name_option"]')])
    body = ("from click.extra import name_option\n\n\n"
            "def test_x():\n"
            "    deco = name_option('--name')\n"
            "    assert '--name' in deco\n")
    said, facts = _refused(db, body)
    assert said == ("`name_option` is a decorator factory in `src/click/extra.py`: "
                    "it returns a decorator and prints nothing when it is called")
    assert [(f.kind, f.value) for f in facts] == [("line_text", "def name_option")]


# Frame 200: the factory door reads the call shape. A clickI-like tree in
# which `version_option` and `custom_version_option` add an option, and
# `pass_meta_key` returns a decorator that adds none.
DECOS = '''\
def _param_memo(f, param):
    if not hasattr(f, "__click_params__"):
        f.__click_params__ = []
    f.__click_params__.append(param)


def option(*param_decls, **attrs):
    def decorator(f):
        _param_memo(f, (param_decls, attrs))
        return f

    return decorator


def command(name=None, **attrs):
    def decorator(f):
        return f

    return decorator


def version_option(version=None, *param_decls, show_python=False, **kwargs):
    if not param_decls:
        param_decls = ("--version",)
    return option(*param_decls, **kwargs)


def custom_version_option(callback, *param_decls, **kwargs):
    if not param_decls:
        param_decls = ("--version",)
    return option(*param_decls, **kwargs)


def pass_meta_key(key, *, doc_description=None):
    def decorator(f):
        def new_func(*args, **kwargs):
            return f(*args, **kwargs)

        return new_func

    return decorator
'''

TESTING = '''\
class CliRunner:
    def invoke(self, cli, args=None):
        return cli
'''

# Night 139's c1 and c2, verbatim from `n139.db` (frame 200's scope, 2).
C1_TEXT = ("When `version_option` is invoked with `show_python=True`, the output "
           "message must append the running Python version formatted exactly as "
           "`{major}.{minor}.{micro}` (e.g., '3.10.4'), derived from "
           "`sys.version_info`.")
C2_TEXT = ("The `show_python` flag must be a boolean parameter that controls "
           "whether the Python version is appended to the standard version "
           "message, defaulting to False when not explicitly set.")


def _decos_db(tmp_path, text: str, surface: str):
    root, wt = _project(tmp_path, {"src/click/__init__.py": "",
                                   "src/click/decorators.py": DECOS,
                                   "src/click/testing.py": TESTING}, {})
    return _db(tmp_path, root, wt,
               "give version_option a show_python flag that appends the "
               "running Python version to the message",
               [("c1", text, f'["src/click/decorators.py::{surface}"]')])


# s251's `tst_version_option_flag_is_boolean` v1, the call form.
S251_CALL_FORM = '''\
from click.decorators import version_option

def test_version_option_flag_is_boolean():
    # Create a simple function to decorate
    def cmd():
        return "version"

    # Apply decorator with show_python=True
    decorated_true = version_option(show_python=True)(cmd)

    # Apply decorator with show_python=False
    decorated_false = version_option(show_python=False)(cmd)

    # Call both and verify they produce different outputs
    result_true = decorated_true()
    result_false = decorated_false()
    assert result_true != result_false
'''

# s279's `tst_version_option_shows_python`, the factory's return called with
# no function argument.
S279_NO_ARGUMENT = '''\
from click.decorators import version_option, custom_version_option
import sys

def test_version_option_shows_python_when_flag_true():
    # Create a simple function to decorate
    def cmd():
        return "version"

    # Apply decorator with show_python=True
    decorated = custom_version_option(cmd, show_python=True)

    # Call the decorated function and check output includes Python version
    result = decorated()
    expected = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    assert expected in result
'''

# The `@` form of the same body, as night 138's s379 wrote it.
AT_FORM = '''\
from click.decorators import version_option

def test_version_option_flag_is_boolean():
    @version_option(show_python=True)
    def cmd():
        return "version"

    assert cmd() != "version"
'''


# s277's turn 1, the factory's return called inline with no function.
S277_INLINE = S279_NO_ARGUMENT.replace(
    "custom_version_option(cmd, show_python=True)",
    "custom_version_option(cmd)(show_python=True)")


# Night 138's `tst_v3` v12 by s377: the factory's return read by another
# call (frame 200's scope, section 1). The review of 2e6afd1c, point 3.
V12_BOUND = '''\
import re
from click.decorators import version_option

def test_v3():
    result = version_option(show_python=True)
    assert re.search(r"Python", result)
'''

V12_INLINE = '''\
import re
from click.decorators import version_option

def test_v3():
    assert re.search(r"Python", version_option(show_python=True))
'''

PASSING = "passing it to a call"

# Night 140's s325 `tst_v1_show_python` v1 and `tst_v3_show_python` v1,
# verbatim from `clickI_night140.db`. Each reads `.callback` on the
# factory's return, and the door admitted both (night 140's read, 2).
N140_V1 = '''\
from click.decorators import version_option
import sys

def test_custom_version_option():
    # Arrange
    def cmd(ctx, param, value):
        return value
    option = version_option(show_python=True)
    # Act
    result = option.callback(None, None, True)
    # Assert
    assert "Python" in result or sys.version_info[0] in result
'''

N140_V3 = '''\
from click.decorators import version_option
import sys

def test_version_option_ambiguous_import_name_errors():
    # Arrange
    def cmd(ctx, param, value):
        return value
    option = version_option(show_python=False)
    # Act
    result = option.callback(None, None, False)
    # Assert
    assert "Python" not in result
'''

READING = "reading `.callback` on it"

# Frame 200's review of pass 3, probe P3a: the inline form of the same read.
P3A_INLINE_CALLBACK = '''\
from click.decorators import command, version_option
from click.testing import CliRunner


def test_v():
    result = version_option(show_python=True).callback(None, None, True)
    assert "Python" in result
'''


@pytest.mark.parametrize("body,text,surface,fact,verb", [
    (S251_CALL_FORM, C2_TEXT, "version_option",
     "`decorated_true` is a plain function", "calling it"),
    (AT_FORM, C2_TEXT, "version_option", "`cmd` is a plain function",
     "calling it"),
    (S279_NO_ARGUMENT, C1_TEXT, "custom_version_option",
     "`decorated` is the decorator that `custom_version_option` returns",
     "calling it"),
    (S277_INLINE, C1_TEXT, "custom_version_option",
     "`custom_version_option(...)` returns a decorator", "calling it"),
    (V12_BOUND, C2_TEXT, "version_option",
     "`result` is the decorator that `version_option` returns", PASSING),
    (V12_INLINE, C2_TEXT, "version_option",
     "`version_option(...)` returns a decorator", PASSING),
    (N140_V1, C1_TEXT, "version_option",
     "`option` is the decorator that `version_option` returns", READING),
    (N140_V3, C2_TEXT, "version_option",
     "`option` is the decorator that `version_option` returns", READING),
    (P3A_INLINE_CALLBACK, C1_TEXT, "version_option",
     "`version_option(...)` returns a decorator", READING),
], ids=["call-form", "at-form", "no-argument", "inline", "v12-bound",
        "v12-inline", "n140-v1-callback", "n140-v3-callback",
        "p3a-inline-callback"])
def test_a_factory_that_adds_an_option_on_a_plain_function_is_refused(
        tmp_path, body, text, surface, fact, verb):
    """The sentence names the factory and not the criterion: night 138's
    c3 names no option (the review of 2e6afd1c, finding 4)."""
    db = _decos_db(tmp_path, text, surface)
    said, facts = _refused(db, body)
    assert said == (f"{fact}, and {verb} never runs the option that "
                    f"`{surface}` adds")
    assert [(f.kind, f.value) for f in facts] == [("line_text", f"def {surface}")]


# The review of 2e6afd1c, finding 1: a factory call whose positional
# argument is a call may decorate a command. Click 8.5 runs these.
CMD_HEAD = ("from click.decorators import command, version_option\n"
            "from click.testing import CliRunner\n\n\n")
OPTION_ON_COMMAND_OBJECT = CMD_HEAD + '''def test_v():
    def hello():
        pass

    cli = version_option(show_python=True)(command()(hello))
    result = CliRunner().invoke(cli, ["--version"])
    assert "Python" in result.output
'''
OPTION_ON_HELPER_RETURN = CMD_HEAD + '''def make_cli():
    @command()
    def cli():
        pass

    return cli


def test_v():
    cli = version_option(show_python=True)(make_cli())
    result = CliRunner().invoke(cli, ["--version"])
    assert "Python" in result.output
'''
BARE_THEN_COMMAND_ARG = CMD_HEAD + '''def test_v():
    def hello():
        pass

    opt = version_option(show_python=True)
    cli = opt(command()(hello))
    result = CliRunner().invoke(cli, ["--version"])
    assert "Python" in result.output
'''
# The review of 2e6afd1c, finding 5: an aliased `command` is a command.
ALIASED_COMMAND = '''\
from click.decorators import command as make_command, version_option
from click.testing import CliRunner


def test_v():
    @make_command()
    @version_option(show_python=True)
    def cli():
        pass

    result = CliRunner().invoke(cli, ["--version"])
    assert "Python" in result.output
'''
# A parameter is the caller's value, as clickI's `echo(testoption)`.
PARAMETER_ARG = '''\
from click.decorators import version_option


def show(testoption):
    return repr(testoption)


def test_v():
    testoption = version_option(show_python=True)
    assert show(testoption)
'''
# Frame 200's review of pass 3, probe P2d: the option runs through the
# runner, and the test also reads an attribute of the factory's return.
P2D_ATTR_BESIDE_RUNNER = CMD_HEAD + '''def test_v():
    def hello():
        pass

    opt = version_option(show_python=True)
    cli = command()(opt(hello))
    result = CliRunner().invoke(cli, ["--version"])
    assert "Python" in result.output
    assert opt.__name__ == "decorator"
'''


@pytest.mark.parametrize("body", [
    OPTION_ON_COMMAND_OBJECT, OPTION_ON_HELPER_RETURN, BARE_THEN_COMMAND_ARG,
    ALIASED_COMMAND, PARAMETER_ARG, P2D_ATTR_BESIDE_RUNNER,
], ids=["command-object", "helper-return", "bare-then-command", "aliased",
        "parameter", "p2d-attr-beside-runner"])
def test_a_factory_on_a_command_lands(tmp_path, body):
    db = _decos_db(tmp_path, C2_TEXT, "version_option")
    _encode(db, "tst_x", "c1", "tests/test_x.py", body)


def test_a_factory_that_returns_a_chain_on_option_adds_an_option():
    """Night 139's commit 5b04c4a made `custom_version_option` return an
    inner `def` that returns `option(...)(f)` (the review of 2e6afd1c,
    finding 2)."""
    src = ("from .decorators import option\n\n\n"
           "def custom_version_option(callback, *param_decls, **kwargs):\n"
           "    def decorator(f):\n"
           "        return option(*param_decls, **kwargs)(f)\n\n"
           "    return decorator\n")
    node = ast.parse(src).body[1]
    assert api._returns_factory(node, src)
    assert api._adds_option(node, src)


def test_the_call_shape_refusal_names_no_shape(tmp_path):
    """The fact and no shape (Roman, 2026-09-15, 6b52a09d)."""
    db = _decos_db(tmp_path, C2_TEXT, "version_option")
    said, _facts = _refused(db, S251_CALL_FORM)
    for word in ("CliRunner", "invoke", "command", "Decorate", "assert", "--"):
        assert word not in said


def test_the_call_shape_through_a_runner_is_refused(tmp_path):
    db = _decos_db(tmp_path, C2_TEXT, "version_option")
    body = ("from click.decorators import version_option\n"
            "from click.testing import CliRunner\n\n\n"
            "def test_x():\n"
            "    @version_option(show_python=True)\n"
            "    def cli():\n"
            "        pass\n\n"
            "    result = CliRunner().invoke(cli, ['--version'])\n"
            "    assert 'Python' in result.output\n")
    said, _facts = _refused(db, body)
    assert said.startswith("`cli` is a plain function")


# The review's `test_right_meta.py` (frame 200's design review, section 1):
# a right test that calls a plain function `pass_meta_key` decorates.
RIGHT_META = '''\
import click
from click.decorators import pass_meta_key


def test_pass_meta_key_wrapper_reads_meta():
    @pass_meta_key("v")
    def f(v):
        return v

    @click.command()
    def c():
        pass

    ctx = click.Context(c)
    ctx.meta["v"] = 1
    with ctx:
        assert f() == 1
'''


def test_pass_meta_key_on_a_local_function_lands(tmp_path):
    """`pass_meta_key` adds no option, so its wrapper is right to call."""
    db = _decos_db(tmp_path, "`pass_meta_key` passes the meta value under the "
                   "key to the decorated function", "pass_meta_key")
    _encode(db, "tst_x", "c1", "tests/test_x.py", RIGHT_META)


def test_a_command_with_the_option_lands(tmp_path):
    db = _decos_db(tmp_path, C2_TEXT, "version_option")
    body = ("from click.decorators import command, version_option\n"
            "from click.testing import CliRunner\n\n\n"
            "def test_python_in_version():\n"
            "    @command()\n"
            "    @version_option(show_python=True)\n"
            "    def cli():\n"
            "        pass\n\n"
            "    result = CliRunner().invoke(cli, ['--version'])\n"
            "    assert 'Python' in result.output\n")
    _encode(db, "tst_x", "c1", "tests/test_x.py", body)


def test_a_factory_return_applied_to_a_command_lands(tmp_path):
    db = _decos_db(tmp_path, C2_TEXT, "version_option")
    body = ("from click.decorators import command, version_option\n"
            "from click.testing import CliRunner\n\n\n"
            "def test_python_in_version():\n"
            "    def cli():\n"
            "        pass\n\n"
            "    cmd = command()(version_option(show_python=True)(cli))\n"
            "    result = CliRunner().invoke(cmd, ['--version'])\n"
            "    assert 'Python' in result.output\n")
    _encode(db, "tst_x", "c1", "tests/test_x.py", body)


# The second look at dd583398, finding 1: the argument kinds refused a
# factory's return passed to a helper the test defines, or to
# `functools.wraps`. Click 8.5 ran both forms and printed the version.
HELPER_FORM = '''\
from click.decorators import command, version_option
from click.testing import CliRunner


def build(extra):
    @command()
    @extra
    def cli():
        pass

    return cli


def test_v():
    cli = build(version_option(show_python=True))
    result = CliRunner().invoke(cli, ["--version"])
    assert "Python" in result.output
'''

WRAPS_FORM = '''\
import functools

from click.decorators import command, version_option
from click.testing import CliRunner


def test_v():
    deco = version_option(show_python=True)

    @functools.wraps(deco)
    def wrapper(f):
        return deco(f)

    cli = command()(wrapper(lambda: None))
    result = CliRunner().invoke(cli, ["--version"])
    assert "Python" in result.output
'''


@pytest.mark.parametrize("body", [HELPER_FORM, WRAPS_FORM],
                         ids=["helper", "wraps"])
def test_a_factory_return_a_helper_applies_lands(tmp_path, body):
    db = _decos_db(tmp_path, C2_TEXT, "version_option")
    _encode(db, "tst_x", "c1", "tests/test_x.py", body)
