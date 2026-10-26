"""Frame 335, pass 1, the escape level of a body in the call
(`plans/c2-escape-provenance.md`). Night 168: s146 stored a test with
`"AppData\\Roaming"` read as one backslash. Python reads `\\R` as no escape
and warns, so `tests.encode` stored the body. The project's pytest runs with
`filterwarnings = error` and stops at collection. The collection note then
copied pytest's `Did you mean "\\\\R"?`, which loses one level in the call.
The Developer s147 quoted the test as the `tests.load` view shows it, with
`\\\\` for one backslash, and the test half of `_cites` refused the quote.

Repair 1: the encode refuses an invalid escape and names the raw string
form with one backslash. The collection note names the same form. Repair 2:
the test half of `_cites` also reads each `\\\\` of a quote as one
backslash."""
from types import SimpleNamespace

import pytest

from rota.core import sandbox
from rota.core.sandbox import build
from rota.roles import api
from tests.rota.test_frame328_encode_note import C1_TEXT, S198_C1, db  # noqa: F401

CRIT = S198_C1["criterion_id"]
BS = "\\"


def _body(line: str) -> str:
    return ("from click.utils import format_filename\n\n"
            "def test_format_filename_keeps_a_windows_path():\n"
            f"    {line}\n"
            "    assert format_filename(path) == path\n")


def _no_run(monkeypatch):
    """A fake run, so that a body that lands writes nothing and runs
    nothing."""
    seen = []

    def fake(ctx, root, path, body):
        seen.append(path)
        return "pass", ""
    monkeypatch.setattr(api, "_encode_run", fake)
    return seen


def _encode(db, body):  # noqa: F811
    sb = build("tester", db, batch_id="bg_3", mode="tests_missing")
    sb.call("tests.triage", criterion_id=CRIT, verdict="encodable")
    return sb.call("tests.encode", id=S198_C1["id"], criterion_id=CRIT,
                   path="tests/test_windows_path.py", body=body)


# The brief's form, one backslash each: `\U` opens an escape of eight hex
# digits, so Python refuses the line. The record's form of s146 and of
# tst_c4 (s142 t2): `\R` and `\M` are no escape, so Python only warns.
@pytest.mark.parametrize("line, escape", [
    ('path = "C:' + BS + 'Users' + BS + 'x' + BS + 'AppData"', BS + "U"),
    ('path = "C:/AppData' + BS + 'Roaming"', BS + "R"),
    ('path = "C:' + BS + 'MockAppData"', BS + "M"),
], ids=["users", "s146_roaming", "tst_c4"])
def test_an_invalid_escape_is_refused_with_the_raw_string_form(
        db, monkeypatch, line, escape):  # noqa: F811
    seen = _no_run(monkeypatch)
    with pytest.raises(Exception) as err:
        _encode(db, _body(line))
    said = str(err.value)
    raw = "r" + line[len("path = "):]
    assert f"line 4 of the body, `{line}`, holds `{escape}`" in said
    assert f"Write the string as a raw string with one backslash: `{raw}`." \
        in said
    assert "not Python" not in said
    assert seen == []
    assert not db.execute("SELECT 1 FROM tests").fetchone()


def test_the_raw_string_form_lands(db, monkeypatch):  # noqa: F811
    seen = _no_run(monkeypatch)
    body = _body('path = r"C:' + BS + 'Users' + BS + 'x' + BS + 'AppData"')
    assert _encode(db, body) == {"id": S198_C1["id"]}
    assert seen == ["tests/test_windows_path.py"]


def test_a_body_that_is_not_python_meets_the_old_refusal(db, monkeypatch):  # noqa: F811
    seen = _no_run(monkeypatch)
    with pytest.raises(Exception) as err:
        _encode(db, "the test checks that a/b/c.txt is shown as c.txt\n")
    assert str(err.value) == (
        "the body is not Python (invalid syntax, line 1). A test is code the "
        "harness can execute -- def test_...(): with assertions, not a "
        "description of one")
    assert seen == []


# Pytest's output for s146's line on Python 3.14 with `filterwarnings =
# error`. The last `E ` line is the line the note copied on night 168, s128
# turn 2 and s146 turn 2.
COLLECT_SAID = (
    "=================================== ERRORS ====================================\n"
    "___________________ ERROR collecting tests/test_shorten.py ____________________\n"
    "..\\Lib\\site-packages\\_pytest\\assertion\\rewrite.py:357: in _rewrite_test\n"
    "    tree = ast.parse(source, filename=strfn)\n"
    "           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
    "E     File \"C:\\wt\\tests\\test_shorten.py\", line 4\n"
    "E       path = \"C:/AppData\\Roaming\"\n"
    "E                         ^^\n"
    "E   SyntaxError: \"\\R\" is an invalid escape sequence. Did you mean "
    "\"\\\\R\"? A raw string is also an option.\n"
    "=========================== short test summary info ===========================\n"
    "ERROR tests/test_shorten.py\n"
    "!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!\n")


def test_the_collection_note_gives_the_raw_string_form():
    ctx, notes = SimpleNamespace(), []
    api._note_collection_error(ctx, "bg_3", CRIT, "tests/test_shorten.py",
                               COLLECT_SAID, notes)
    note, = notes
    assert ("The run of this body on the batch's head errors when pytest "
            "collects `tests/test_shorten.py`: `SyntaxError: \"\\R\" is an "
            "invalid escape sequence.`") in note
    assert ("Write the string as a raw string with one backslash: "
            "`r\"C:/AppData\\Roaming\"`.") in note
    assert "Did you mean" not in note
    assert "\\\\R" not in note
    assert note.endswith("Encode it again with the same id.")


# The test row of night 168 as s146 stored it, one backslash. s147 quoted
# it with `\\` for that backslash, as the JSON of `tests.load` shows it.
TST_W2 = ("from click.utils import format_filename\n\n"
          "def test_format_filename_keeps_a_windows_path():\n"
          "    result = format_filename(\"C:/AppData" + BS + "Roaming\")\n"
          "    assert \"AppData" + BS + "Roaming\" in result\n")
TST_ID = "tst_crit_1"


@pytest.fixture
def cdb(db):  # noqa: F811
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES (?, 'bg_3', ?, 'tests/test_windows_path.py', ?)",
               (TST_ID, CRIT, TST_W2))
    db.commit()
    return db


def _challenge(db, test_quote):
    ctx = build("developer", db, batch_id="bg_3", mode="tests_failing").ctx
    return sandbox._challenge_evidence(ctx, "tester", [CRIT, TST_ID], "",
                                       quotes=[C1_TEXT, test_quote])


def test_a_quote_with_two_backslashes_for_one_passes_the_test_half(cdb):
    quote = "assert \"AppData" + BS * 2 + "Roaming\" in result"
    assert _challenge(cdb, quote) is None


def test_a_quote_on_neither_reading_is_refused_with_both_readings(cdb):
    quote = "assert \"AppData" + BS * 2 + "Local\" in result"
    with pytest.raises(ValueError) as err:
        _challenge(cdb, quote)
    said = str(err.value)
    assert said.startswith(
        f"quotes= holds `{quote}`, and it is not in the live text of "
        f"{TST_ID}. A comment of the test does not count.")
    assert ("The door also reads each `\\\\` as one backslash. Read that way, "
            "the quote is `assert \"AppData\\Local\" in result`, and the code "
            f"of {TST_ID} holds no such span.") in said
