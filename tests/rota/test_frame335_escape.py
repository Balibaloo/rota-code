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
    slash = line[len("path = "):].replace(BS, "/")
    assert f"line 4 of the body, `{line}`, holds `{escape}`" in said
    # Pass 2, review 1, finding 2: a path takes forward slashes first.
    assert said.endswith(
        f"Write the path with forward slashes: `{slash}`. The raw string "
        f"`{raw}`, with one backslash, also comes through the call "
        f"unchanged.")
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
    assert ("Write the path with forward slashes: `\"C:/AppData/Roaming\"`. "
            "The raw string `r\"C:/AppData\\Roaming\"`, with one backslash, "
            "also comes through the call unchanged.") in note
    assert "Did you mean" not in note
    assert "\\\\R" not in note
    assert note.endswith("Encode it again with the same id.")


def test_an_import_error_keeps_the_advice_of_pytest():
    """Pass 2, review 1, finding 1: Python's `Did you mean:` of a misspelt
    name is right, and the note keeps it with no word on escapes."""
    said = COLLECT_SAID.replace(
        COLLECT_SAID[COLLECT_SAID.index("E     File"):
                     COLLECT_SAID.index("=========================== short")],
        "E   ImportError: cannot import name 'format_filenme' from "
        "'click.utils'. Did you mean: 'format_filename'?\n")
    notes = []
    api._note_collection_error(SimpleNamespace(), "bg_3", CRIT,
                               "tests/test_shorten.py", said, notes)
    note, = notes
    assert ("collects `tests/test_shorten.py`: `ImportError: cannot import "
            "name 'format_filenme' from 'click.utils'. Did you mean: "
            "'format_filename'?`. No test in the body runs.") in note
    assert "raw string" not in note and "forward slashes" not in note


# Pass 2, review 1, finding 2: probe `probe_p2.py` of the review. The raw
# form of `\Users` with one backslash holds on both parse paths. In
# `\Roaming\new` the strict path turns `\n` into a line break. In
# `\Roaming\temp` it turns `\t` into a TAB. So those two get the forward
# slashes only.
@pytest.mark.parametrize("text, advice", [
    ("C:" + BS + "Users" + BS + "x" + BS + "AppData" + BS + "Roaming",
     'Write the path with forward slashes: `"C:/Users/x/AppData/Roaming"`. '
     'The raw string `r"C:' + BS + 'Users' + BS + 'x' + BS + 'AppData' + BS
     + 'Roaming"`, with one backslash, also comes through the call '
     'unchanged.'),
    ("C:" + BS + "Roaming" + BS + "new",
     'Write the path with forward slashes: `"C:/Roaming/new"`. For a '
     'criterion about a backslash, write `"C:" + chr(92) + "Roaming" + '
     'chr(92) + "new"`. That form keeps a real backslash on both parse '
     'paths.'),
    ("C:" + BS + "Roaming" + BS + "temp",
     'Write the path with forward slashes: `"C:/Roaming/temp"`. For a '
     'criterion about a backslash, write `"C:" + chr(92) + "Roaming" + '
     'chr(92) + "temp"`. That form keeps a real backslash on both parse '
     'paths.'),
    # Pass 2b, review 2, point 3: `\U` fails the strict path and `\n` the
    # fallback, so no raw form of `C:\Users\new` comes through.
    ("C:" + BS + "Users" + BS + "new",
     'Write the path with forward slashes: `"C:/Users/new"`. For a '
     'criterion about a backslash, write `"C:" + chr(92) + "Users" + '
     'chr(92) + "new"`. That form keeps a real backslash on both parse '
     'paths.'),
], ids=["users", "roaming_new", "roaming_temp", "users_new"])
def test_the_advice_gives_a_form_that_the_call_keeps(
        db, monkeypatch, text, advice):  # noqa: F811
    _no_run(monkeypatch)
    with pytest.raises(Exception) as err:
        _encode(db, _body(f'path = "{text}"'))
    assert str(err.value).endswith(advice)


def test_an_invalid_octal_escape_meets_the_escape_refusal(db, monkeypatch):  # noqa: F811
    """Pass 2, review 1, finding 3: Python 3.14 calls `\\777` an invalid
    octal escape sequence."""
    seen = _no_run(monkeypatch)
    line = 'path = "' + BS + '777"'
    with pytest.raises(Exception) as err:
        _encode(db, _body(line))
    said = str(err.value)
    assert said.startswith(f"line 4 of the body, `{line}`, holds `{BS}777`")
    assert "not Python" not in said and "Did you mean" not in said
    # Pass 2b, review 2, point 4: `"\777"` is no path, and the strict path
    # reads its raw form as one character. So the advice names no form.
    assert said.endswith(
        "No form of this string with a backslash comes through the call "
        "unchanged. Write the value with no backslash.")
    assert seen == []


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


def _challenge(db, test_quote, crit_quote=C1_TEXT):
    ctx = build("developer", db, batch_id="bg_3", mode="tests_failing").ctx
    return sandbox._challenge_evidence(ctx, "tester", [CRIT, TST_ID], "",
                                       quotes=[crit_quote, test_quote])


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
    assert ("The door also reads the quote as the call stores it from your "
            "text, with each escape read as Python reads it. Read that way, "
            "the quote is `assert \"AppData\\Local\" in result`, and the code "
            f"of {TST_ID} holds no such span.") in said


def test_the_criterion_half_reads_two_backslashes_by_the_same_rule(cdb):
    """Pass 2: a criterion row with one backslash, quoted with two as the
    test row is, passes the criterion half too."""
    text = ("When shorten=False, format_filename keeps the path C:/AppData"
            + BS + "Roaming as it is.")
    cdb.execute("UPDATE criteria SET text = ? WHERE id = ?", (text, CRIT))
    cdb.commit()
    one = "the path C:/AppData" + BS + "Roaming as it is"
    two = one.replace(BS, BS * 2)
    test_quote = "assert \"AppData" + BS * 2 + "Roaming\" in result"
    assert _challenge(cdb, test_quote, crit_quote=two) is None
    assert _challenge(cdb, test_quote, crit_quote=one) is None
