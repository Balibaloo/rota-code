"""Frame 328, night 166 (2026-10-25): the Developer s201 sent m83 and s208
sent m88, both on tst_c1, while tst_c1's last run at the batch's head
a0295dff passed. The Tester s202 then rewrote a green test, and the red
tests tst_c2 and tst_c3 waited. Repair 3: a Developer challenge on a test
that passes at the head is refused, with the test's name and its green run."""
import pytest

from rota.core import sandbox
from rota.core.sandbox import build
from tests.rota.test_frame328_challenge_quote import (  # noqa: F401
    C1_TEXT, M85_REFS, M85_TEXT, M88_QUOTES, M88_REFS, M88_TEXT, db)

HEAD = "a0295dffd730b5d6d14813fded003472c8e5ed21"
# Word for word from .rota/clickI_night166.db, read with mode=ro.
# tst_c1 as s200 stored it, the version that s201 had in front of it.
TST_C1_S200 = 'from click.utils import format_filename\n\ndef test_format_filename_docstring_shorten_example():\n    # Criterion c_1: When shorten=True, the docstring must include an example showing that a/b/c.txt is displayed as c.txt.\n    result = format_filename("a/b/c.txt", shorten=True)\n    assert "c.txt" in result  # The function returns only the basename\n    assert "a/b/c.txt" not in result  # The function strips the directory prefix\n\n    docstring = format_filename.__doc__\n    assert "a/b/c.txt" in docstring\n    assert "c.txt" in docstring'
TST_C3_S198 = 'from click.utils import format_filename\n\ndef test_format_filename_docstring_demonstration_example():\n    # Criterion c_3: The docstring must include an example demonstrating that with shorten=True, a/b/c.txt is displayed as c.txt.\n    result = format_filename("a/b/c.txt", shorten=True)\n    assert "c.txt" in result\n    assert "a/b/c.txt" in result'
# m83: s201's turn 2 call, and the message's stored body_text.
M83_QUOTES = [C1_TEXT, 'assert "a/b/c.txt" in result']
M83_TEXT = 'When shorten=True, the docstring of format_filename must include an example showing that a/b/c.txt is displayed as c.txt. ... assert "a/b/c.txt" in result'
# m88's reason, from s208's turn 1 call.
M88_REASON = "the line `assert \"a/b/c.txt\" in result` of `tst_c1_format_filename_example` fails with AssertionError 'assert \\'a/b/c.txt\\' in \\'c.txt\\'', raised in `test_format_filename_docstring_demonstration_example()`."
# The stored runs at the head: test_run_journal seq 262 to 264 (attempt 3,
# before m83) and seq 344 to 346 (attempt 5, before m88).
PASS_3 = ".                                                                        [100%]\n1 passed in 0.04s"
PASS_5 = ".                                                                        [100%]\n1 passed in 0.07s"
FAIL = ("F                                                                        [100%]\n"
        "1 failed in 0.14s")


def _runs(db, attempt, results):
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
               "VALUES ('tst_c3_format_filename_example','bg_3',"
               "'c_3_format_filename_example',"
               "'tests/test_utils/test_format_filename_c3.py',?)", (TST_C3_S198,))
    for n, (result, output) in enumerate(results, 1):
        db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, "
                   "result, output, attempt) VALUES (?, 'bg_3', ?, ?, ?, ?, ?)",
                   (f"tr11{n + 2}", f"tst_c{n}_format_filename_example", HEAD,
                    result, output, attempt))
    db.commit()


def _ctx(db, role="developer", mode="tests_failing"):
    return build(role, db, batch_id="bg_3", mode=mode).ctx


def test_m83_on_tst_c1_green_at_the_head_is_refused(db):
    db.execute("UPDATE tests SET body = ? WHERE id = "
               "'tst_c1_format_filename_example'", (TST_C1_S200,))
    _runs(db, 3, [("pass", PASS_3), ("fail", FAIL), ("fail", FAIL)])
    ctx = _ctx(db)
    assert sandbox._green_at_head_refusal(ctx, M88_REFS + ["d_29238279cd"]) == (
        "tst_c1_format_filename_example passes on the batch's head a0295dff: "
        "its last run there says `1 passed in 0.04s`. A challenge disputes a "
        "red test, and this test is green. The failing tests of this batch: "
        "tst_c2_format_filename_example (c_2_format_filename_example), "
        "tst_c3_format_filename_example (c_3_format_filename_example).")
    # m83's test quote is not a line of s200's version, so the quote door
    # refuses m83 first. With a true span of that version the challenge
    # passes the quote door, and the green door still refuses it.
    assert sandbox._challenge_admitted(ctx, M88_REFS, M83_QUOTES) is False
    true_spans = [C1_TEXT, 'assert "c.txt" in result']
    assert sandbox._challenge_evidence(
        ctx, "tester", M88_REFS, " ... ".join(true_spans)) is None
    assert sandbox._challenge_admitted(ctx, M88_REFS, true_spans) is False


def test_m88_on_tst_c1_green_at_the_head_is_refused(db):
    _runs(db, 5, [("pass", PASS_5), ("pass", PASS_5), ("fail", FAIL)])
    ctx = _ctx(db)
    said = sandbox._green_at_head_refusal(ctx, M88_REFS + ["d_626934fdb4"])
    assert said.startswith("tst_c1_format_filename_example passes on the "
                           "batch's head a0295dff: its last run there says "
                           "`1 passed in 0.07s`.")
    assert said.endswith("The failing tests of this batch: "
                         "tst_c3_format_filename_example "
                         "(c_3_format_filename_example).")
    assert sandbox._challenge_admitted(ctx, M88_REFS, M88_QUOTES) is False
    true_spans = [C1_TEXT, 'assert "a/b/c.txt" in docstring']
    assert sandbox._challenge_admitted(ctx, M88_REFS, true_spans) is False


def test_the_binder_refuses_a_green_test_with_true_spans(db):
    """The real door of `msg.challenge_tester`, with m88's reason and true
    spans of the rows."""
    _runs(db, 5, [("pass", PASS_5), ("pass", PASS_5), ("fail", FAIL)])
    sb = build("developer", db, batch_id="bg_3", mode="tests_failing")
    with pytest.raises(ValueError, match="tst_c1_format_filename_example "
                       "passes on the batch's head a0295dff"):
        sb.call("msg.challenge_tester", refs=M88_REFS,
                quotes=[C1_TEXT, 'assert "a/b/c.txt" in docstring'],
                reason=M88_REASON)


def test_m85_on_tst_c2_red_at_the_head_still_passes(db):
    _runs(db, 4, [("pass", PASS_3), ("fail", FAIL), ("fail", FAIL)])
    ctx = _ctx(db)
    assert sandbox._challenge_evidence(ctx, "tester", M85_REFS, M85_TEXT) is None
    assert sandbox._challenge_admitted(ctx, M85_REFS, M85_TEXT.split(" ... "))


def test_a_run_at_another_commit_is_no_green_at_the_head(db):
    """Only a run at the head commit says the test is green there."""
    _runs(db, 5, [("pass", PASS_5), ("pass", PASS_5), ("fail", FAIL)])
    db.execute("UPDATE batches SET head_commit = 'b' || head_commit "
               "WHERE id = 'bg_3'")
    db.commit()
    assert sandbox._green_at_head_refusal(_ctx(db), M88_REFS) is None


def test_a_critic_challenge_on_a_green_test_does_not_meet_the_door(db):
    """At review every test is green by construction, so the door is the
    Developer's only."""
    _runs(db, 5, [("pass", PASS_5), ("pass", PASS_5), ("pass", PASS_5)])
    assert sandbox._green_at_head_refusal(
        _ctx(db, role="critic", mode="review"), M88_REFS) is None
