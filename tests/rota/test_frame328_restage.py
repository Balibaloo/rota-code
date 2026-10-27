"""Frame 328, pass 3, night 167 (2026-10-26): two walls behind the clear()
item of bg_5.

1. The Gemma Tester s271 got the encode note on tst_tk3 in turn 3 and sent
   a passing tst_tk3 with the same id in turns 4, 5 and 6. The one-test
   guard read only the stored rows, and the session's own first encode was
   only staged. Each re-encode came back unchanged, and version 1 landed.
2. The Developer s284 (seq 16 and 17) and s286 (seq 2) quoted the live
   criterion verbatim and tst_tk3's line with `\\x1b` and `\\u001b`. The
   row holds the raw ESC byte, so the quote check refused the test half.

The fixtures come from `plans/night167-walk2-read.md`, sections 2 and 3.
The record elides the middle of tk_3's text and gives no whole body, so
the parts it does not quote are a reconstruction around its quotes."""
import pytest

from rota.core import sandbox
from rota.core.db import init_db
from rota.core.sandbox import build

HEAD = "40b16f78" + "0" * 32
CRIT = "tk_3_clear_returns_true"
TEST = "tst_tk3"
PATH = "tests/test_termui_clear.py"
# The record's quote: "When stdout is a terminal, clear() must emit the
# exact ANSI escape sequence it currently writes ... then return True." The
# old quotes ended "corner." where the live text goes on ", then return
# True." The middle is a reconstruction.
TK3_LIVE = ("When stdout is a terminal, clear() must emit the exact ANSI escape "
            "sequence it currently writes to clear the screen and move the "
            "cursor to the top-left corner, then return True.")
# Version 1 said "the standard ANSI escape sequence" (s276's quote).
TK3_V1 = ("When stdout is a terminal, clear() must emit the standard ANSI "
          "escape sequence to clear the screen and move the cursor to the "
          "top-left corner, then return True.")
# tst_tk3 version 1. The record quotes `result is True` and the line
# `assert "\x1b[2J\x1b[H" in sys.stdout.getvalue()`, held as raw ESC bytes.
TST_TK3_V1 = (
    "import sys\n"
    "from io import StringIO\n"
    "from unittest.mock import patch\n"
    "\n"
    "from click.termui import clear\n"
    "\n"
    "\n"
    "def test_tk3_clear_screen_return_success():\n"
    "    with patch(\"click.termui.isatty\", return_value=True):\n"
    "        with patch(\"sys.stdout\", new_callable=StringIO):\n"
    "            result = clear()\n"
    "            assert result is True\n"
    "            assert \"\x1b[2J\x1b[H\" in sys.stdout.getvalue()\n")
# s271 turn 3's re-encode: `assert "\x1b[2J" in output` and
# `assert "\x1b[1;1H" in output or "\x1b[H" in output`, which passes.
TST_TK3_S271 = (
    "import sys\n"
    "from io import StringIO\n"
    "from unittest.mock import patch\n"
    "\n"
    "from click.termui import clear\n"
    "\n"
    "\n"
    "def test_tk3_clear_screen_return_success():\n"
    "    with patch(\"click.termui.isatty\", return_value=True):\n"
    "        with patch(\"sys.stdout\", new_callable=StringIO):\n"
    "            result = clear()\n"
    "            output = sys.stdout.getvalue()\n"
    "    assert result is True\n"
    "    assert \"\\x1b[2J\" in output\n"
    "    assert \"\\x1b[1;1H\" in output or \"\\x1b[H\" in output\n")
# The code at the head writes `echo("\033[2J\033[1;1H", nl=False)`.
TERMUI = r'''import sys


def isatty(stream):
    try:
        return stream.isatty()
    except Exception:
        return False


def clear():
    if not isatty(sys.stdout):
        return False
    sys.stdout.write("\033[2J\033[1;1H")
    return True
'''
# test_run_journal seq 213: the run of version 1 at the head.
RUN_213 = (
    "    def test_tk3_clear_screen_return_success():\n"
    "        with patch(\"click.termui.isatty\", return_value=True):\n"
    "            with patch(\"sys.stdout\", new_callable=StringIO):\n"
    "                result = clear()\n"
    "                assert result is True\n"
    ">               assert \"\x1b[2J\x1b[H\" in sys.stdout.getvalue()\n"
    "E               AssertionError: assert '\\x1b[2J\\x1b[H' in "
    "'\\x1b[2J\\x1b[1;1H'\n"
    "1 failed in 0.12s")
# s284 seq 16: the test half as the seat typed it, `\x1b` as four
# characters. s286 seq 2 wrote `\u001b`.
LINE_X = 'assert "\\x1b[2J\\x1b[H" in sys.stdout.getvalue()'
LINE_U = 'assert "\\u001b[2J\\u001b[H" in sys.stdout.getvalue()'
REASON = ("tst_tk3 asserts \\x1b[H, and tk_3 asks for the sequence that "
          "clear() currently writes, \\x1b[2J\\x1b[1;1H.")


@pytest.fixture
def db(tmp_path):
    """Batch bg_5 at the night's head, with a worktree whose `clear` writes
    the sequence of the head. The encode run is real."""
    root = tmp_path / "wt"
    (root / ".git").mkdir(parents=True)
    (root / "src" / "click").mkdir(parents=True)
    (root / "src" / "click" / "__init__.py").write_bytes(b"")
    (root / "src" / "click" / "termui.py").write_bytes(TERMUI.encode("utf-8"))
    # The worktree's `click` must win over the `click` that rota's
    # interpreter holds.
    (root / "pytest.ini").write_bytes(b"[pytest]\npythonpath = src\n")
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, approval_ver, "
                 "version) VALUES ('i1','clear() returns a bool',"
                 "'in_scope','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('tk1','i1','clear() returns True on a terminal')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text, surface_refs) "
                 "VALUES (?, 'tk1', ?, ?)",
                 (CRIT, TK3_LIVE, '["src/click/termui.py::clear"]'))
    conn.execute("INSERT INTO batches (id, item_id, status, head_commit, "
                 "worktree) VALUES ('bg_5','i1','running',?,?)",
                 (HEAD, str(root)))
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('bg_5','tk1')")
    # s268's `code.commit` on bg_5, the batch's own commit.
    conn.execute("INSERT INTO sessions (id, role, seq, committed) VALUES "
                 "('s268','developer',268,1)")
    conn.execute("INSERT INTO receipts (session_id, table_name, row_id, "
                 "new_version) VALUES ('s268','batches','bg_5',4)")
    conn.commit()
    return conn


def _tester(db):
    sb = build("tester", db, batch_id="bg_5", mode="tests_missing")
    sb.call("tests.triage", criterion_id=CRIT, verdict="encodable")
    return sb


def _encode(sb, body):
    return sb.call("tests.encode", id=TEST, criterion_id=CRIT, path=PATH,
                   body=body)


def _commit(db, sb):
    from rota.core.db import SessionResult, session_commit
    from rota.core.runner import _as_write
    session_commit(db, SessionResult(
        session_id="s271", role="tester",
        writes=[_as_write(w) for w in sb.ctx.writes], messages=[]))
    return db.execute("SELECT version, body FROM tests WHERE id = ?",
                      (TEST,)).fetchone()


def test_s271_re_encode_after_the_note_lands_as_version_2(db):
    sb = _tester(db)
    first = _encode(sb, TST_TK3_V1)
    assert "Encode it again with the same id." in first["note"]
    second = _encode(sb, TST_TK3_S271)
    assert "unchanged" not in second
    assert second["version"] == 2
    assert second["note"].startswith(
        "tst_tk3 replaces the version this session encoded before the note, "
        "and it lands as version 2 when the session commits.")
    staged = [w for w in sb.ctx.writes if w[0] == "tests"]
    assert len(staged) == 1 and staged[0][2]["body"] == TST_TK3_S271
    row = _commit(db, sb)
    assert (row["version"], row["body"]) == (2, TST_TK3_S271)


def test_the_same_body_again_after_the_note_is_unchanged(db):
    sb = _tester(db)
    _encode(sb, TST_TK3_V1)
    again = _encode(sb, TST_TK3_V1 + "\n")
    assert again["unchanged"] is True
    assert again["id"] == TEST
    row = _commit(db, sb)
    assert (row["version"], row["body"]) == (1, TST_TK3_V1)


def _challenge_db(db):
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES (?, 'bg_5', ?, ?, ?)", (TEST, CRIT, PATH, TST_TK3_V1))
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
               "result, output, attempt) VALUES ('tr213', 'bg_5', ?, ?, "
               "'fail', ?, 3)", (TEST, HEAD, RUN_213))
    db.commit()
    return build("developer", db, batch_id="bg_5", mode="tests_failing")


@pytest.mark.parametrize("line", [LINE_X, LINE_U], ids=["s284", "s286"])
def test_the_live_criterion_and_an_escaped_test_line_are_delivered(db, line):
    sb = _challenge_db(db)
    out = sb.call("msg.challenge_tester", refs=[CRIT, TEST],
                  quotes=[TK3_LIVE, line], reason=REASON)
    sent = [m for m in sb.ctx.outbound if m["id"] == out["id"]]
    assert sent and sent[0]["to_role"] == "tester"
    assert sent[0]["verb"] == "challenge"


def test_an_older_criterion_text_is_still_refused(db):
    sb = _challenge_db(db)
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", refs=[CRIT, TEST],
                quotes=[TK3_V1, LINE_X], reason=REASON)
    assert str(exc.value).startswith(
        f"quotes= holds `{TK3_V1[:77]}...`, and it is not in the live text "
        f"of {CRIT}.")


def test_a_wrong_test_line_names_the_form_the_door_compared(db):
    sb = _challenge_db(db)
    wrong = 'assert "\\u001b[2J\\u001b[1;1H" in sys.stdout.getvalue()'
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", refs=[CRIT, TEST],
                quotes=[TK3_LIVE, wrong], reason=REASON)
    assert (
        "The door also reads the quote as the call stores it from your text, "
        "with each escape read as Python reads it. Read that way, the "
        "quote is `assert \"\\x1b[2J\\x1b[1;1H\" in sys.stdout.getvalue()`, "
        "and the code of tst_tk3 holds no such span.") in str(exc.value)


# The review of pass 3, finding 1: the reviewer's probe P3W. The test holds
# a raw literal, so its escape is four characters and not ESC.
RAW_LINE = 'assert r"\\x1b[2J" in sys.stdout.getvalue()'
RAW_QUOTE = 'assert r"\\033[2J" in sys.stdout.getvalue()'


def test_a_raw_literal_quote_with_another_escape_is_refused(db):
    sb = _challenge_db(db)
    db.execute("UPDATE tests SET body = ? WHERE id = ?",
               (TST_TK3_V1.replace(
                   "            assert \"\x1b[2J\x1b[H\" in "
                   "sys.stdout.getvalue()\n", f"            {RAW_LINE}\n"),
                TEST))
    db.commit()
    with pytest.raises(ValueError, match="not in the live text of tst_tk3"):
        sandbox._challenge_evidence(sb.ctx, "tester", [CRIT, TEST],
                                    f"{TK3_LIVE} ... {RAW_QUOTE}")


def test_a_quote_is_read_through_the_call_once():
    """F19: `api._call_values` reads the quote, so each escape is read as
    the call reads it. A bytes quote with another escape is no span."""
    assert sandbox._quote_reads('x = "\\x1b[2J\\u001b[H\\033"',
                                'x = "\x1b[2J\x1b[H\x1b"', "tests")
    assert not sandbox._quote_reads('x = b"\\x1b[2J" + y',
                                    'x = b"\\u001b[2J" + y', "tests")
    # The strict path stores `A` from the seat's `\x41`, so the door reads
    # the kept text the same way. Pass 3's review had refused this form.
    assert sandbox._quote_reads('x = "\\x41BCDEF"', 'x = "ABCDEF"', "tests")


def test_the_failing_line_shows_the_escape_and_not_the_raw_byte(db):
    """The review of pass 3, finding 3: the red-line refusal showed raw ESC
    bytes, so the seat read `assert "[2J[H"`."""
    sb = _challenge_db(db)
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", refs=[CRIT, TEST],
                quotes=[TK3_LIVE, "assert result is True"],
                reason="tst_tk3 asserts a sequence that clear() never writes.")
    said = str(exc.value)
    assert "\x1b" not in said
    assert said.startswith(
        "tst_tk3 is red, and its run names the line it fails at: "
        "`assert \"\\x1b[2J\\x1b[H\" in sys.stdout.getvalue()`")
