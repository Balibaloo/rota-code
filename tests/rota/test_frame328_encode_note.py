"""Frame 328, night 166 (2026-10-25): s195 and s197 committed the right
docstring at a0295dff before the Tester s198 woke. s198 stored three tests
that fail at their own assertion on that head. The encode door stored them
by frame 304's rule, and the red woke only the Developer. The Tester never
saw its own run. Repair 1: the encode result carries a note with the failing
assertion line, and the door still refuses nothing."""
import ast

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import api

# Word for word from .rota/clickI_night166.db, read with mode=ro: s198's turn
# 6 completion, the call stored at tool_calls seq 31.
S198_C1_CALL = """TOOL: tests.encode(id='tst_c1_format_filename_example', criterion_id='c_1_format_filename_example', path='tests/test_utils/test_format_filename_c1.py', body='from click.utils import format_filename\\n\\ndef test_format_filename_docstring_shorten_example():\\n    # Criterion c_1: When shorten=True, the docstring must include an example showing that a/b/c.txt is displayed as c.txt.\\n    result = format_filename("a/b/c.txt", shorten=True)\\n    assert "c.txt" in result\\n    assert "a/b/c.txt" in result')"""
S198_C1 = {k.arg: ast.literal_eval(k.value) for k in ast.parse(
    S198_C1_CALL[len("TOOL: tests."):]).body[0].value.keywords}
C1_TEXT = ("When shorten=True, the docstring of format_filename must include an "
           "example showing that a/b/c.txt is displayed as c.txt.")
HEAD = "a0295dffd730b5d6d14813fded003472c8e5ed21"

# Word for word from `git show a0295dff:src/click/utils.py`, lines 442 to
# 484, in the night's sample repository clickI.
FORMAT_FILENAME = '''def format_filename(
    filename: str | bytes | os.PathLike[str] | os.PathLike[bytes],
    shorten: bool = False,
) -> str:
    """Format a filename as a string for display. Ensures the filename can be
    displayed by replacing any invalid bytes or surrogate escapes in the name
    with the replacement character ``�``.

    Invalid bytes or surrogate escapes will raise an error when written to a
    stream with ``errors="strict"``. This will typically happen with ``stdout``
    when the locale is something like ``en_GB.UTF-8``.

    Many scenarios *are* safe to write surrogates though, due to PEP 538 and
    PEP 540, including:

    -   Writing to ``stderr``, which uses ``errors="backslashreplace"``.
    -   The system has ``LANG=C.UTF-8``, ``C``, or ``POSIX``. Python opens
        stdout and stderr with ``errors="surrogateescape"``.
    -   None of ``LANG/LC_*`` are set. Python assumes ``LANG=C.UTF-8``.
    -   Python is started in UTF-8 mode  with  ``PYTHONUTF8=1`` or ``-X utf8``.
        Python opens stdout and stderr with ``errors="surrogateescape"``.

    :param filename: formats a filename for UI display.  This will also convert
                     the filename into unicode without failing.
    :param shorten: this optionally shortens the filename to strip of the
                    path that leads up to it.

    Example:
        >>> format_filename("a/b/c.txt", shorten=True)
        "c.txt"
    """
    if shorten:
        filename = os.path.basename(filename)
    else:
        filename = os.fspath(filename)

    if isinstance(filename, bytes):
        filename = filename.decode(sys.getfilesystemencoding(), "replace")
    else:
        filename = filename.encode("utf-8", "surrogateescape").decode(
            "utf-8", "replace"
        )

    return filename
'''


@pytest.fixture
def db(tmp_path):
    """Batch bg_3 at the night's head, with a worktree that holds the
    docstring of a0295dff. The run is real, not a recording."""
    root = tmp_path / "wt"
    (root / ".git").mkdir(parents=True)
    (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "__init__.py").write_bytes(b"")
    (root / "src" / "click" / "utils.py").write_bytes(
        ("import os\nimport sys\n\n\n" + FORMAT_FILENAME).encode("utf-8"))
    # The worktree's `click` must win over the `click` that rota's
    # interpreter holds.
    (root / "pytest.ini").write_bytes(b"[pytest]\npythonpath = src\n")
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1','document format_filename',"
                 "'in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','i1','an example in the docstring of format_filename')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                 "VALUES ('c_1_format_filename_example','tk1',?,?)",
                 (C1_TEXT, '["src/click/utils.py::format_filename"]'))
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit, "
                 "worktree) VALUES ('bg_3','i1','running',?,?)",
                 (HEAD, str(root)))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_3','tk1')")
    # s195's `code.commit` of the docstring: the batch's own commit, as the
    # night's `receipts` table holds it.
    conn.execute("INSERT INTO sessions (id, role, seq, committed) VALUES "
                 "('s195','developer',195,1)")
    conn.execute("INSERT INTO receipts (session_id, table_name, row_id, "
                 "new_version) VALUES ('s195','batches','bg_3',6)")
    conn.commit()
    return conn


def _encode(db, body):
    sb = build("tester", db, batch_id="bg_3", mode="tests_missing")
    sb.call("tests.triage", criterion_id=S198_C1["criterion_id"],
            verdict="encodable")
    return sb.call("tests.encode", id=S198_C1["id"],
                   criterion_id=S198_C1["criterion_id"],
                   path=S198_C1["path"], body=body)


def test_s198_test_red_at_its_assertion_lands_with_the_failing_line(db):
    out = _encode(db, S198_C1["body"])
    assert out["id"] == "tst_c1_format_filename_example"
    note = out["note"]
    assert "`test_format_filename_docstring_shorten_example`" in note
    assert "line 7, `assert \"a/b/c.txt\" in result`" in note
    assert "AssertionError: assert 'a/b/c.txt' in 'c.txt'" in note
    assert "Encode it again with the same id." in note


def test_a_test_green_at_the_head_lands_with_no_note(db, monkeypatch):
    real, seen = api._encode_run, []

    def spy(*args):
        ran = real(*args)
        seen.append(ran[0])
        return ran
    monkeypatch.setattr(api, "_encode_run", spy)
    body = ("from click.utils import format_filename\n\n"
            "def test_format_filename_shortens_to_the_basename():\n"
            "    assert format_filename(\"a/b/c.txt\", shorten=True) == \"c.txt\"\n")
    out = _encode(db, body)
    # The run happened and passed, so the missing note is the rule's.
    assert seen == ["pass"]
    assert out == {"id": "tst_c1_format_filename_example"}


def test_a_base_head_after_a_boot_gives_no_note(db):
    """Review 1, finding 1: a boot writes the git head into `head_commit`
    with no session. With no `code.commit` of the batch, a test written
    before the code is red by design, so it lands with no note."""
    db.execute("DELETE FROM receipts")
    # The Architect's receipt on the batch row is no commit.
    db.execute("INSERT INTO sessions (id, role, seq, committed) VALUES "
               "('s187','architect',187,1)")
    db.execute("INSERT INTO receipts (session_id, table_name, row_id, "
               "new_version) VALUES ('s187','batches','bg_3',5)")
    db.commit()
    out = _encode(db, S198_C1["body"])
    assert out == {"id": "tst_c1_format_filename_example"}


def test_two_red_tests_in_one_body_each_name_their_own_line(db):
    """Review 1, finding 3: the note named the first test and quoted the
    second test's line."""
    body = ("from click.utils import format_filename\n\n"
            "def test_keeps_the_path():\n"
            "    assert format_filename(\"a/b/c.txt\", shorten=True) == \"a/b/c.txt\"\n\n"
            "def test_shortens():\n"
            "    assert format_filename(\"a/b/c.txt\", shorten=True) == \"c.txt\"\n\n"
            "def test_keeps_the_dir():\n"
            "    result = format_filename(\"a/b/c.txt\", shorten=True)\n"
            "    assert \"b/\" in result\n")
    note = _encode(db, body)["note"]
    first = ("The run of `test_keeps_the_path` on the batch's head fails at "
             "line 4, `assert format_filename(\"a/b/c.txt\", shorten=True) == "
             "\"a/b/c.txt\"`:")
    second = ("The run of `test_keeps_the_dir` on the batch's head fails at "
              "line 11, `assert \"b/\" in result`: `AssertionError: assert "
              "'b/' in 'c.txt'`.")
    assert first in note and second in note
    assert note.index(first) < note.index(second)
    assert "test_shortens" not in note


def test_a_raise_inside_the_code_after_the_commit_gets_a_note(db):
    """Frame 328, item 4: `arrange_fault` admits a raise inside the
    project's code, and on d495db74 the note read an `AssertionError` of
    the test's file only. Nights 163 to 168 held 3 such reds of 17."""
    body = ("from click.utils import format_filename\n\n"
            "def test_an_int_is_shown_as_text():\n"
            "    assert format_filename(123) == \"123\"\n")
    note = _encode(db, body)["note"]
    # The docstring of format_filename pushes the test's own frame out of
    # the run's tail, so the note names the place that raised.
    assert ("The run of `test_an_int_is_shown_as_text` on the batch's head "
            "raises `TypeError: expected str, bytes or os.PathLike object, "
            "not int` at src/click/utils.py line ") in note
    # Review of pass 1, finding 6: a raise names both causes.
    assert ("A raise can come from the Developer's code or from the test's "
            "own call.") in note
    assert "encode it again with the same id." in note


def test_a_raise_in_a_short_function_names_the_tests_line(db):
    root = db.execute("SELECT worktree FROM batches WHERE id = 'bg_3'"
                      ).fetchone()["worktree"]
    with open(f"{root}/src/click/utils.py", "ab") as fh:
        fh.write(b"\n\ndef double(x):\n    return x * 2 + None\n")
    body = ("from click.utils import double, format_filename\n\n"
            "def test_double():\n"
            "    assert format_filename(str(double(2))) == \"4\"\n")
    note = _encode(db, body)["note"]
    assert ("The run of `test_double` on the batch's head fails at line 4, "
            "`assert format_filename(str(double(2))) == \"4\"`: `TypeError: "
            "unsupported operand") in note
