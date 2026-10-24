"""
Frame 306's case: a file that holds no code is no evidence and no foreseen stray.

Night 162 (2026-10-24), b_2. The Developer s203 wrote
`criteria/c1_confirm_default_on_eof`, seven lines of the criteria rows, and
committed it alone as 8717098. The Architect s239 judged the stray
`foreseen`. The Critic s247 passed the batch on six lines of that file.
A criterion is met by code or by a test, not by a note.
"""
import subprocess

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import prompts
from rota.testkit import samplerepo

NOTE = "notes/c1_work_flag"
HELPER = "src/helper.py"
# Pass 1b: prose that a plan can foresee, in a directory the base holds.
CHANGES = "CHANGES.rst"
DOC = "docs/flag.rst"
CHANGE_LINE = "-   ``work()`` takes a ``flag`` argument."
# Pass 1c: an empty package file, and data of a kind the base tree holds.
PACKAGE = "src/flags/__init__.py"
DATA = "data/x.json"

BASE = "def work(x):\n    return x\n"
HEAD = ('def work(x, flag=False):\n'
        '    """Do the work.\n'
        '\n'
        '    The flag makes the work return None.\n'
        '    """\n'
        '    if flag:\n'
        '        return None\n'
        '    return x\n')
TEST = ("from src.work import work\n\n\n"
        "def test_flag():\n"
        "    assert work(1, flag=True) is None\n")
# s203's shape: the criteria rows as prose, in a new directory.
PROSE = ("c1 | work() accepts an optional flag that defaults to False.\n"
         "c2 | With the flag on, work() gives back None.\n")

C1, C2, C3 = "c1_flag", "c2_flag_none", "c3_flag_doc"
TEXTS = {C1: "work() accepts an optional flag that defaults to False",
         C2: "with the flag on, work() returns None",
         C3: "the docstring of work() says what the flag does"}


def _git(root, *args) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, text=True).stdout


def _repo(tmp_path, monkeypatch, extra: dict[str, str]) -> tuple[str, str]:
    """A worktree whose last commit changes `src/work.py` and adds `extra`."""
    for k, v in samplerepo.GIT_ENV.items():
        monkeypatch.setenv(k, v)
    root = tmp_path / "wt"
    (root / "src").mkdir(parents=True)
    _git(tmp_path, "init", "-q", str(root))
    (root / "src" / "work.py").write_bytes(BASE.encode())
    (root / "docs").mkdir()
    (root / "docs" / "index.rst").write_bytes(b"Work\n====\n")
    (root / "CHANGES.rst").write_bytes(b"Version 1.0\n-----------\n")
    (root / "src" / "schema.json").write_bytes(b"{}\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    (root / "src" / "work.py").write_bytes(HEAD.encode())
    for rel, text in extra.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(text.encode())
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "the batch")
    return str(root), _git(root, "rev-parse", "HEAD").strip()


@pytest.fixture
def batch(tmp_path, monkeypatch):
    tree, head = _repo(tmp_path, monkeypatch,
                       {"tests/test_work.py": TEST, NOTE: PROSE,
                        HELPER: "def help_work():\n    return 1\n",
                        CHANGES: "Version 1.0\n-----------\n" + CHANGE_LINE + "\n",
                        DOC: "The flag\n--------\n",
                        PACKAGE: "", DATA: '{"flag": false}\n'})
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1','the item','in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','i1','the ticket')")
    for cid, text in TEXTS.items():
        conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                     "(?, 'tk1', ?)", (cid, text))
    conn.execute("INSERT INTO batches (id, item_id, status, worktree, "
                 "head_commit) VALUES ('b_2', 'i1', 'running', ?, ?)",
                 (tree, head))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b_2', 'tk1')")
    # The prediction before the commit names the source file only.
    conn.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind) "
                 "VALUES ('b_2', 'src/work.py', 'path')")
    conn.commit()
    return conn


def _pass(conn, lines):
    sb = build("critic", conn, batch_id="b_2", mode="review")
    # The first-pass hold of frame 201 is not this door.
    sb.ctx.pass_held = True
    return sb, lambda: sb.call("verdicts.emit", batch_id="b_2",
                               result="pass", lines=lines)


SOURCE = {C1: "def work(x, flag=False):", C2: "return None",
          C3: "The flag makes the work return None."}


def test_s247_a_line_of_a_prose_file_is_refused_and_names_the_file(batch):
    """s247's verdict on 8717098: each line sits in the criteria file."""
    sb, send = _pass(batch, {
        C1: "c1 | work() accepts an optional flag that defaults to False.",
        C2: "c2 | With the flag on, work() gives back None.",
        C3: SOURCE[C3]})
    with pytest.raises(ValueError) as exc:
        send()
    msg = str(exc.value)
    assert NOTE in msg, msg
    assert "by code or by a test, not by a note" in msg, msg
    assert not [w for w in sb.ctx.writes if w[0] == "verdicts"]


def test_a_source_line_passes(batch):
    sb, send = _pass(batch, dict(SOURCE))
    assert send()["result"] == "pass"


def test_a_test_line_passes(batch):
    sb, send = _pass(batch, {**SOURCE,
                             C2: "assert work(1, flag=True) is None"})
    assert send()["result"] == "pass"


def test_a_docstring_line_on_a_docstring_criterion_passes(batch):
    """Frame 311's door admits the line, and the source file holds code."""
    sb, send = _pass(batch, {**SOURCE, C3: '"""Do the work.'})
    assert send()["result"] == "pass"


def _strays(conn, *paths):
    head = conn.execute("SELECT head_commit FROM batches").fetchone()[0]
    for p in paths:
        conn.execute("INSERT INTO touch_strays (batch_id, commit_sha, path) "
                     "VALUES ('b_2', ?, ?)", (head, p))
    conn.commit()
    return build("architect", conn, mode="touch_strayed",
                 allow=prompts.mode_tools("architect", "touch_strayed"))


def test_s239_foreseen_on_a_file_no_plan_named_and_with_no_code_is_refused(batch):
    """s239: the plan named the file only after the write, in the judgement."""
    sb = _strays(batch, NOTE)
    with pytest.raises(ValueError) as exc:
        sb.call("batches.judge_touch", batch_id="b_2", foreseen=[NOTE])
    msg = str(exc.value)
    assert NOTE in msg and "did not name the file before the write" in msg, msg
    assert "mistakes=" in msg, msg
    assert not [w for w in sb.ctx.writes if w[0] in ("batch_touch", "touch_strays")]


def test_foreseen_on_a_grain_of_a_file_predicted_before_the_commit_lands(batch):
    sb = _strays(batch, "src/work.py::work(flag)")
    out = sb.call("batches.judge_touch", batch_id="b_2",
                  foreseen=["src/work.py::work(flag)"])
    assert out["foreseen"] == ["src/work.py::work(flag)"], out


def test_foreseen_on_a_new_source_file_still_lands(batch):
    """The ruled route for a helper the plan missed stays."""
    sb = _strays(batch, HELPER)
    out = sb.call("batches.judge_touch", batch_id="b_2", foreseen=[HELPER])
    assert out["foreseen"] == [HELPER], out


def test_mistake_lands_either_way(batch):
    sb = _strays(batch, NOTE, HELPER)
    out = sb.call("batches.judge_touch", batch_id="b_2",
                  mistakes=[NOTE, HELPER])
    assert out["mistakes"] == [NOTE, HELPER], out


# Pass 1b (the coordinator's answers to the report's open questions).

def test_a_changelog_line_on_a_criterion_that_asks_for_the_changelog_passes(batch):
    """A criterion that names the changelog reads a changelog line as work."""
    batch.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                  "('c4_changelog', 'tk1', 'the changelog names the new flag')")
    batch.commit()
    sb, send = _pass(batch, {**SOURCE, "c4_changelog": CHANGE_LINE})
    assert send()["result"] == "pass"


def test_a_changelog_line_on_a_behaviour_criterion_is_still_refused(batch):
    sb, send = _pass(batch, {**SOURCE, C2: CHANGE_LINE})
    with pytest.raises(ValueError) as exc:
        send()
    assert CHANGES in str(exc.value), str(exc.value)


@pytest.mark.parametrize("path", [CHANGES, DOC])
def test_foreseen_on_prose_in_a_directory_the_base_held_lands(batch, path):
    """A changelog entry or a new docs page is work a plan can foresee."""
    sb = _strays(batch, path)
    out = sb.call("batches.judge_touch", batch_id="b_2", foreseen=[path])
    assert out["foreseen"] == [path], out


# Pass 1c (frame 306's review 3: one high, low B).

@pytest.mark.parametrize("path", [PACKAGE, DATA])
def test_foreseen_on_a_package_file_or_known_data_in_a_new_directory_lands(batch, path):
    """An empty `__init__.py` is code. A `.json` file in a tree that holds
    `.json` files is a kind of file a plan can foresee."""
    sb = _strays(batch, path)
    out = sb.call("batches.judge_touch", batch_id="b_2", foreseen=[path])
    assert out["foreseen"] == [path], out
