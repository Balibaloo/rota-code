"""Frame 328, night 166 (2026-10-25): the Developer s208 sent m88 on c_1 and
tst_c1. Its criterion quote was c_1's contested old text, and its test quote
was a line of an older version of the test. The door read 12-character
windows of each row anywhere in the joined quotes, so "When shorten" and
" format_file" let m88 through. The ruling of 2026-08-26 asks for "a
contiguous span of the disputed row, verbatim, whitespace-normalised", and
Roman confirmed it on 2026-10-25. So each quote must stand inside its own
row's live text."""
import pytest

from rota.core import sandbox
from rota.core.db import init_db
from rota.core.sandbox import build

# Word for word from .rota/clickI_night166.db, read with mode=ro.
# The live texts of the criteria, version 2 for c_1 and c_2.
C1_TEXT = ("When shorten=True, the docstring of format_filename must include an "
           "example showing that a/b/c.txt is displayed as c.txt.")
C2_TEXT = C1_TEXT
C3_TEXT = ("The docstring of format_filename must include an example "
           "demonstrating that with shorten=True, a/b/c.txt is displayed as "
           "c.txt.")
# tst_c1 as s202 stored it, the version that s208 had in front of it.
TST_C1_S202 = 'from click.utils import format_filename\n\ndef test_format_filename_docstring_shorten_example():\n    # Criterion c_1: When shorten=True, the docstring must include an example showing that a/b/c.txt is displayed as c.txt.\n    docstring = format_filename.__doc__\n    assert "a/b/c.txt" in docstring\n    assert "c.txt" in docstring'
# tst_c2 as s198 stored it, the version that s203 had in front of it.
TST_C2_S198 = 'from click.utils import format_filename\n\ndef test_format_filename_docstring_basename_example():\n    # Criterion c_2: When shorten=True, the docstring must include an example showing that a/b/c.txt is displayed as c.txt.\n    result = format_filename("a/b/c.txt", shorten=True)\n    assert "c.txt" in result\n    assert "a/b/c.txt" in result'
# m88: s208's turn 1 call, and the message's stored body_text.
M88_REFS = ["c_1_format_filename_example", "tst_c1_format_filename_example"]
M88_QUOTES = ["When shorten=True, format_filename strips the directory prefix from the path.",
              "assert \"a/b/c.txt\" in result"]
M88_TEXT = 'When shorten=True, format_filename strips the directory prefix from the path. ... assert "a/b/c.txt" in result'
# m85: s203's message, its stored body_text.
M85_REFS = ["c_2_format_filename_example", "tst_c2_format_filename_example"]
M85_TEXT = 'When shorten=True, the docstring of format_filename must include an example showing that a/b/c.txt is displayed as c.txt. ... assert "a/b/c.txt" in result'


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1','document format_filename',"
                 "'in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','i1','an example in the docstring of format_filename')")
    for cid, text in (("c_1_format_filename_example", C1_TEXT),
                      ("c_2_format_filename_example", C2_TEXT),
                      ("c_3_format_filename_example", C3_TEXT)):
        conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                     "(?, 'tk1', ?)", (cid, text))
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit) "
                 "VALUES ('bg_3','i1','running',"
                 "'a0295dffd730b5d6d14813fded003472c8e5ed21')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_3','tk1')")
    for tid, cid, n, body in (
            ("tst_c1_format_filename_example", "c_1_format_filename_example",
             1, TST_C1_S202),
            ("tst_c2_format_filename_example", "c_2_format_filename_example",
             2, TST_C2_S198)):
        conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                     "VALUES (?, 'bg_3', ?, ?, ?)",
                     (tid, cid, f"tests/test_utils/test_format_filename_c{n}.py",
                      body))
    conn.commit()
    return conn


def _ctx(db):
    return build("developer", db, batch_id="bg_3", mode="tests_failing").ctx


def test_m88_quoting_the_contested_old_text_is_refused(db):
    ctx = _ctx(db)
    with pytest.raises(ValueError) as exc:
        sandbox._challenge_evidence(ctx, "tester", M88_REFS, M88_TEXT)
    said = str(exc.value)
    assert said.startswith(
        "quotes= holds `When shorten=True, format_filename strips the directory "
        "prefix from the path.`, and it is not in the live text of "
        "c_1_format_filename_example.")
    assert sandbox._challenge_admitted(ctx, M88_REFS, M88_QUOTES) is False


def test_m88_test_quote_alone_names_the_test_row(db):
    """With a true span of c_1, the test quote of an older version is refused
    on its own row."""
    ctx = _ctx(db)
    with pytest.raises(ValueError, match="not in the live text of "
                       "tst_c1_format_filename_example. A comment of the test"):
        sandbox._challenge_evidence(ctx, "tester", M88_REFS,
                                    f"{C1_TEXT} ... {M88_QUOTES[1]}")


def test_m85_quoting_true_spans_of_the_live_rows_passes(db):
    ctx = _ctx(db)
    assert sandbox._challenge_evidence(ctx, "tester", M85_REFS, M85_TEXT) is None
    assert sandbox._challenge_admitted(ctx, M85_REFS, M85_TEXT.split(" ... "))


# Word for word from .rota/clickI_night144.db, read with mode=ro: m153 and
# m159, both from the Developer, and the two rows they name.
N144_CRIT = "The function must print a JSON representation of an object, letting the standard json module raise its own error if the object cannot be serialized."
N144_TEST = 'import json\nfrom click.utils import echo\nimport traceback\n\ndef test_echo_raises_on_unserializable():\n    """Test that echo lets the standard json module raise errors on unserializable objects."""\n    class Unserializable:\n        def __reduce__(self):\n            raise TypeError("Cannot serialize")\n    \n    obj = Unserializable()\n    try:\n        echo(obj)\n        assert False, "Expected TypeError to be raised"\n    except TypeError as e:\n        # Verify it is the standard json module error\n        tb = traceback.format_exc()\n        assert "json" in tb.lower(), f"Exception not from json module: {tb}"'
N144_REFS = ["cj_serializable", "tst_serializable_01"]
M153_TEXT = "The function must print a JSON representation of an object, letting the standard json module raise its own error if the object cannot be serialized. ... echo(obj)"
M159_TEXT = M153_TEXT


@pytest.mark.parametrize("text", [M153_TEXT, M159_TEXT], ids=["m153", "m159"])
def test_the_register_quotes_under_the_floor_are_refused(db, text):
    """Frame 328, review 1, finding 2: over the register the floor refuses
    two quotes that the span check admits, `echo(obj)` of night 144."""
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('cj_serializable', 'tk1', ?)", (N144_CRIT,))
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst_serializable_01', 'bg_3', 'cj_serializable', "
               "'tests/test_serializable.py', ?)", (N144_TEST,))
    db.commit()
    with pytest.raises(ValueError, match="`echo\\(obj\\)`, and it is shorter "
                                         "than 12 characters"):
        sandbox._challenge_evidence(_ctx(db), "tester", N144_REFS, text)


def test_a_decoded_line_break_meets_only_a_line_break():
    """Frame 328, review 1, finding 4: the JSON escape stands for a line
    break of the row, never for a plain space. F19 pass 1b: the call
    decodes the escape, so the rule is read through `_quote_reads`."""
    two_lines = 'assert r.exit_code != 0\n    assert "a" in r.output'
    assert sandbox._quote_reads(
        'assert r.exit_code != 0\\n    assert "a" in r.output', two_lines)
    assert not sandbox._quote_reads('assert r == "a\\nb is the text"',
                                    'assert r == "a b is the text"')
    assert sandbox._quote_reads('assert r == "a b is the text"',
                                'assert r == "a b is the text"')
