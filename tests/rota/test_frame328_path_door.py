"""Frame 328, pass 4, night 167 (2026-10-25): the Gemma Tester encoded its
test at `path='src/click/utils.py'` 15 times, the module under test. Night
166's qwen Tester did the same 14 times. `tests.encode` admitted any `.py`
path, and the harness wrote the test over the module. The run at encode then
errored at collection on a circular import, the door read only `fail`, and
the Tester heard nothing. The Developer got `tick:tests_failing` four times
on the right commit fa4e8230.

Repair 1: the door refuses a program file of the code index outside the
test folders. Repair 2: after the Developer's commit, a collection error at
encode is the test's red, and the Tester gets the encode note."""
import pytest

from rota.core.sandbox import build
from rota.roles import api
from tests.rota.test_frame302_unindexed_path import SRC, TESTS
from tests.rota.test_frame328_encode_note import S198_C1, db  # noqa: F401

CRIT = S198_C1["criterion_id"]

# s326 turn 3's call, from `night167-cycle1.md` section 1: `import inspect`,
# `from click.utils import format_filename`, and an assert on the docstring
# of `format_filename`. The words of the assert are the record's quote.
S326_BODY = ("import inspect\n"
             "from click.utils import format_filename\n\n"
             "def test_format_filename_docstring_example():\n"
             "    doc = inspect.getdoc(format_filename)\n"
             "    assert \"format_filename(a/b/c.txt) returns 'c.txt'\" in doc\n")

# Pass 2c's shape on bg_3: a module-level import of a project module that the
# head does not hold. Pytest stops at collection, the exit is 2, and the
# harness word is `error`.
COLLECT_BODY = ("from click.utils import format_filename\n"
                "import click.shorten\n\n"
                "def test_shorten_keeps_the_basename():\n"
                "    name = format_filename(\"a/b/c.txt\")\n"
                "    assert click.shorten.basename(name) == \"c.txt\"\n")
# tst_c4's shape, s142 t2, from `night167-read.md`: the stored body held
# `"C:\MockAppData"` with one backslash. The project's `filterwarnings =
# error` makes the invalid escape a SyntaxError at collection.
TST_C4_BODY = ("from click.utils import format_filename\n\n"
               "def test_format_filename_keeps_a_windows_path():\n"
               "    mock_appdata = \"C:\\MockAppData\"\n"
               "    assert format_filename(mock_appdata) == mock_appdata\n")


# The re-encode after the collection note: the same id, a body that runs.
FIXED_BODY = ("from click.utils import format_filename\n\n"
              "def test_format_filename_shortens():\n"
              "    assert format_filename(\"a/b/c.txt\", shorten=True) == \"c.txt\"\n")


@pytest.fixture
def idb(db):  # noqa: F811
    """bg_3 of frame 328's encode note, with night 157's `code_index` path
    grains of the click sample repository."""
    for grain in SRC + TESTS:
        db.execute("INSERT INTO code_index (grain, grain_kind) "
                   "VALUES (?, 'path')", (grain,))
    db.commit()
    return db


def _encode(db, path, body):
    sb = build("tester", db, batch_id="bg_3", mode="tests_missing")
    sb.call("tests.triage", criterion_id=CRIT, verdict="encodable")
    return sb.call("tests.encode", id=S198_C1["id"], criterion_id=CRIT,
                   path=path, body=body)


def _spy(monkeypatch):
    real, seen = api._encode_run, []

    def spy(*args):
        ran = real(*args)
        seen.append(ran)
        return ran
    monkeypatch.setattr(api, "_encode_run", spy)
    return seen


def test_s326_encode_at_the_module_under_test_is_refused(idb, monkeypatch):
    seen = _spy(monkeypatch)
    with pytest.raises(Exception) as err:
        _encode(idb, "src/click/utils.py", S326_BODY)
    said = str(err.value)
    assert "'src/click/utils.py' is a program file of the project" in said
    assert "a test folder of the index: tests." in said
    assert "path='tests/test_utils.py'" in said
    # The door refuses before the run, so the module is never overwritten.
    assert seen == []
    assert not idb.execute("SELECT 1 FROM tests").fetchone()


def _no_run(monkeypatch):
    """A fake run, so that a door that misses a path writes nothing on disk
    outside the worktree."""
    seen = []

    def fake(ctx, root, path, body):
        seen.append(path)
        return "pass", ""
    monkeypatch.setattr(api, "_encode_run", fake)
    return seen


def test_a_dot_spelling_of_the_module_meets_the_same_door(idb, monkeypatch):
    """Review of pass 4, finding 1: probe P5 encoded at
    `./src/click/utils.py`, the run wrote over the module, and the test
    landed."""
    seen = _no_run(monkeypatch)
    with pytest.raises(ValueError) as err:
        _encode(idb, "./src/click/utils.py", S326_BODY)
    assert "'src/click/utils.py' is a program file of the project" in str(
        err.value)
    assert seen == []


@pytest.mark.parametrize("path", ["../x.py", "C:/x.py", "/x.py",
                                  "tests/../../x.py"])
def test_a_path_outside_the_project_is_refused(idb, monkeypatch, path):
    seen = _no_run(monkeypatch)
    with pytest.raises(ValueError) as err:
        _encode(idb, path, S326_BODY)
    said = str(err.value)
    assert "is outside the project" in said
    assert said.endswith("Name the file tests/test_<thing>.py")
    assert seen == []


def test_an_encode_under_the_test_folder_lands(idb):
    out = _encode(idb, "tests/test_utils.py", S326_BODY)
    assert out["id"] == S198_C1["id"]


def test_an_unindexed_path_outside_the_test_folders_meets_the_old_door(idb):
    path = "src/click/new_helper.py"
    body = ("from click.utils import format_filename\n\n"
            "def test_shortens():\n"
            "    assert format_filename(\"a/b/c.txt\", shorten=True) == \"c.txt\"\n")
    assert _encode(idb, path, body)["id"] == S198_C1["id"]
    with pytest.raises(ValueError) as err:
        api._refuse_unindexed_files(idb, [path], None)
    said = str(err.value)
    assert said.startswith(
        "src/click/new_helper.py is not a file the index holds. The index "
        "holds these files in src/click: src/click/__init__.py, ")
    assert said.endswith(
        "A new test file beside the indexed tests needs no `new_files`")


@pytest.mark.parametrize("body, raised", [
    (COLLECT_BODY, "ModuleNotFoundError: No module named 'click.shorten'"),
    (TST_C4_BODY, "SyntaxError: "),
], ids=["module", "tst_c4"])
def test_a_collection_error_after_the_developer_commit_is_noted(
        idb, monkeypatch, body, raised):
    root = idb.execute("SELECT worktree FROM batches WHERE id = 'bg_3'"
                       ).fetchone()["worktree"]
    from pathlib import Path
    Path(root, "pytest.ini").write_bytes(
        b"[pytest]\npythonpath = src\nfilterwarnings =\n    error\n")
    seen = _spy(monkeypatch)
    sb = build("tester", idb, batch_id="bg_3", mode="tests_missing")
    sb.call("tests.triage", criterion_id=CRIT, verdict="encodable")
    out = sb.call("tests.encode", id=S198_C1["id"], criterion_id=CRIT,
                  path="tests/test_shorten.py", body=body)
    assert [v for v, _ in seen] == ["error"]
    assert "error during collection" in seen[0][1]
    note = out["note"]
    assert ("The run of this body on the batch's head errors when pytest "
            "collects `tests/test_shorten.py`: `" + raised) in note
    # Review of pass 4, finding 2: the hedge of the `fail` note, word for
    # word.
    assert note.endswith(
        "The test is stored. The batch's head holds the Developer's commit. "
        "If the criterion's words give the value that the run shows, the "
        "test is wrong. Encode it again with the same id.")
    # Review of pass 4, finding 3: the note's re-encode with the same id
    # replaces the staged test.
    again = sb.call("tests.encode", id=S198_C1["id"], criterion_id=CRIT,
                    path="tests/test_shorten.py", body=FIXED_BODY)
    assert "unchanged" not in again
    assert again["version"] == 2
    staged = [w for w in sb.ctx.writes if w[0] == "tests"]
    assert len(staged) == 1 and staged[0][2]["body"] == FIXED_BODY


def test_a_collection_error_before_the_developer_commit_stays_silent(
        idb, monkeypatch):
    """Pass 2c: before the Developer's commit, an import of a project name
    that is not written yet is right, and the door says nothing."""
    idb.execute("DELETE FROM receipts")
    idb.commit()
    seen = _spy(monkeypatch)
    out = _encode(idb, "tests/test_shorten.py", COLLECT_BODY)
    assert [v for v, _ in seen] == ["error"]
    assert out == {"id": S198_C1["id"]}


PATH_LINE = ("The path of `tests.encode` is a test file, "
             "`tests/test_<thing>.py`, and never the file of the code under "
             "test.")


@pytest.mark.parametrize("mode", ["answer", "challenge"])
def test_the_brief_names_the_test_path_form_once(mode):
    """All 31 encodes at a `src/` path on nights 166 and 167 came in the
    `answer` and `challenge` modes, and neither brief named a path form."""
    from pathlib import Path
    text = (Path(api.__file__).parent / "prompts" / "tester"
            / f"{mode}.md").read_bytes().decode("utf-8")
    assert text.count(PATH_LINE) == 1
