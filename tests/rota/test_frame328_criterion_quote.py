"""Frame 328, the residue, night 167 walk 3 (2026-10-26): the criterion
half refused a quote with one unpaired outer quote mark.

The Developer sessions s327 and s336 to s338 quoted the live text of
c_1_format_filename_example. Each quote started with one `'` and ended
with `.` or `''.`, and the seat's call syntax sent `\\'` inside it.
`_span_of` strips an outer quote only as a pair, so 12 of 13 challenges
were refused. m189 passed because its quote also ended in `'`.

The quote strings, the criterion texts, the test body and the run output
are copied from `.rota/clickI_night167.db`: `turns` of s336 seq 5 and
s327 seq 3, `messages` m189, `criteria`, `tests` and `test_runs` tr110.
The test body is version 4. It holds the line that every challenge
quoted on the test half."""
import pytest

from rota.core import sandbox
from rota.core.db import init_db
from rota.core.sandbox import build
from rota.roles import api

HEAD = "fa4e8230683d1c96b6db942d7e2294b088090050"
CRIT = "c_1_format_filename_example"
TEST = "tst_c1_format_filename_example"
PATH = "src/click/utils.py"
# The live text from s316 to s342, as `criteria.load` showed it.
CRIT_LIVE = "When shorten=True, format_filename(a/b/c.txt) returns 'c.txt'."
# The live text from s342, version 2 of the row.
CRIT_V2 = ("The docstring for format_filename must show that when "
           "shorten=True, the path 'a/b/c.txt' is displayed as 'c.txt'. This "
           "change applies only to the docstring; the function's return value "
           "and implementation code must remain unchanged.")
TST_BODY = (
    "import click\n"
    "import inspect\n"
    "\n"
    "from click.utils import format_filename\n"
    "\n"
    "def test_format_filename_docstring():\n"
    "    doc = inspect.getdoc(format_filename)\n"
    "    assert \"format_filename(a/b/c.txt) returns 'c.txt' when "
    "shorten=True\" in doc\n"
    "    assert format_filename(\"a/b/c.txt\", shorten=True) == \"c.txt\"\n"
    "    assert format_filename(\"a/b/c.txt\", shorten=False) == "
    "\"a/b/c.txt\"\n")
# test_runs tr110, the collection error at the head, shortened to the
# lines that name the failing import.
RUN_110 = (
    "_____________________ ERROR collecting src/click/utils.py "
    "_____________________\n"
    "src\\click\\utils.py:4: in <module>\n"
    "    from click.utils import format_filename\n"
    "E   ImportError: cannot import name 'format_filename' from partially "
    "initialized module 'click.utils' (most likely due to a circular "
    "import)\n"
    "ERROR src/click/utils.py\n"
    "1 error in 0.27s")
TEST_LINE = "from click.utils import format_filename"
# s336 seq 5, verbatim from the completion: one `'` opens, `''.` ends.
S336 = "'When shorten=True, format_filename(a/b/c.txt) returns \\'c.txt\\''."
# s327 seq 3, verbatim from the completion: one `'` opens, `.` ends.
S327 = "'When shorten=True, format_filename(a/b/c.txt) returns \\'c.txt\\'."
# m189, the challenge that passed: the outer quote is a pair.
M189 = "'When shorten=True, format_filename(a/b/c.txt) returns \\'c.txt\\'.'"
REASON = ("the line 'from click.utils import format_filename' of "
          "tst_c1_format_filename_example fails with ImportError 'cannot "
          "import name \\'format_filename\\' from partially initialized "
          "module \\'click.utils\\'', raised in <module>")


@pytest.fixture
def db(tmp_path):
    """Batch bg_6 at the night's head, with tst_c1 red at collection."""
    root = tmp_path / "wt"
    (root / ".git").mkdir(parents=True)
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1','format_filename example',"
                 "'in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk_1_format_filename_example','i1',"
                 "'format_filename shows an example')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                 "VALUES (?, 'tk_1_format_filename_example', ?, ?)",
                 (CRIT, CRIT_LIVE, '["src/click/utils.py::format_filename"]'))
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit, "
                 "worktree) VALUES ('bg_6','i1','running',?,?)",
                 (HEAD, str(root)))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_6','tk_1_format_filename_example')")
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                 "VALUES (?, 'bg_6', ?, ?, ?)", (TEST, CRIT, PATH, TST_BODY))
    conn.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
                 "result, output, attempt) VALUES ('tr110', 'bg_6', ?, ?, "
                 "'error', ?, 4)", (TEST, HEAD, RUN_110))
    conn.commit()
    return conn


def _challenge(db, quote):
    sb = build("developer", db, batch_id="bg_6", mode="tests_failing")
    out = sb.call("msg.challenge_tester", refs=[CRIT, TEST],
                  quotes=[quote, TEST_LINE], reason=REASON)
    return [m for m in sb.ctx.outbound if m["id"] == out["id"]]


@pytest.mark.parametrize("quote", [S336, S327, M189],
                         ids=["s336", "s327", "m189"])
def test_the_seat_form_of_the_live_criterion_is_delivered(db, quote):
    sent = _challenge(db, quote)
    assert sent and sent[0]["to_role"] == "tester"
    assert sent[0]["verb"] == "challenge"


@pytest.mark.parametrize("quote", [S336, S327, CRIT_LIVE],
                         ids=["s336", "s327", "bare"])
def test_a_quote_of_the_older_criterion_text_is_still_refused(db, quote):
    db.execute("UPDATE criteria SET text = ? WHERE id = ?", (CRIT_V2, CRIT))
    db.commit()
    with pytest.raises(ValueError) as exc:
        _challenge(db, quote)
    assert str(exc.value).startswith(f"quotes= holds `{quote}`, and it is "
                                     f"not in the live text of {CRIT}.")


def test_the_refusal_names_the_form_the_door_read(db):
    db.execute("UPDATE criteria SET text = ? WHERE id = ?", (CRIT_V2, CRIT))
    db.commit()
    with pytest.raises(ValueError) as exc:
        _challenge(db, S336)
    assert (
        "The door also reads the quote as the call stores it from your text, "
        "with each escape read as Python reads it. It drops one outer quote "
        "mark at each end, and a `.` after the closing quote mark. Read "
        "that way, the quote is `When shorten=True, format_filename(a/b/c.txt) "
        "returns 'c.txt'`, and the live text of c_1_format_filename_example "
        "holds no such span.") in str(exc.value)


@pytest.mark.parametrize("quote", ["'\\'c.txt\\''.", "'c.txt'."],
                         ids=["escaped", "plain"])
def test_a_quote_shorter_than_the_floor_is_still_refused(db, quote):
    with pytest.raises(ValueError, match="^quotes= holds `"):
        _challenge(db, quote)


def _stored(quote):
    """F19: the value that the strict path of the call stores."""
    return api._call_values(quote)[0]


def test_the_seat_forms_keep_the_whole_text_and_drop_only_the_outer_marks():
    assert sandbox._outer_marks(_stored(S327))[0] == CRIT_LIVE
    assert sandbox._outer_marks(_stored(S336))[0] == CRIT_LIVE[:-1]
    assert sandbox._outer_marks(_stored(M189))[0] == CRIT_LIVE
    assert sandbox._outer_marks(CRIT_LIVE) == []
    assert CRIT_LIVE in sandbox._quote_forms(S327)[1]
