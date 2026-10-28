"""
Wall W12 of night 172: the stopped page names the red test.

Pages m120 and m127 said "The team gave up: the tests still fail after 3
attempts" while every check line said "Passes". The red test was the
project's `tests/test_types.py`, with no criterion, so no page line named it.
m127 also showed the fallback words for `touch_mistaken`. The rows below
copy the shape of bg_3 at 128bec7e (`plans/f1-f15-f21-night172-read.md`).
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.roles.principal import (_gave_up_words, _stalled_words, render_page,
                                  render_state)

HEAD = "128bec7ef05a42cb75d9e936e148381bf46efe88"
ITEM = "format_filename_example"
FAILING = "developer|tick:tests_failing|bg_3"
MISTAKEN = "developer|tick:touch_mistaken|bg_3"
REFS = ["bg_3", ITEM, "cr_1"]
RED = ("    def test_file_error_surrogates():\n"
       "E       AssertionError: Regex pattern did not match.\n"
       "E         Expected regex: \"No such file\"\n"
       "\n"
       "tests/test_types.py:288: AssertionError\n"
       "FAILED tests/test_types.py::test_path_surrogates - AssertionError: Regex patt...\n"
       "4 failed, 39 passed, 2 skipped in 0.50s\n")


@pytest.fixture
def bg3(tmp_path):
    """bg_3 running at its head, its own check green, and one project test
    red with no criterion."""
    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO items (id, text, kind, approval, approval_ver, version, "
               "priority, is_description) VALUES (?, 'With shorten set to True, "
               "the path a/b/c.txt is displayed as c.txt.', 'in_scope', "
               "'approved', 1, 1, 1, 0)", (ITEM,))
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk_1', ?, "
               "'the ticket')", (ITEM,))
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES ('cr_1', 'tk_1', "
               "'format_filename shortens a/b/c.txt to c.txt.')")
    db.execute("INSERT INTO batches (id, item_id, head_commit, status) VALUES "
               "('bg_3', ?, ?, 'running')", (ITEM, HEAD))
    db.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES ('bg_3', 'tk_1')")
    db.execute("INSERT INTO batch_touch (batch_id, grain, grain_kind, confidence) "
               "VALUES ('bg_3', 'src/click/utils.py', 'path', 'expected')")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
               "('t_own', 'bg_3', 'cr_1', 'tests/test_utils.py', "
               "'def test_shorten():\n    result = format_filename(\"a/b/c.txt\", "
               "shorten=True)\n    assert result == \"c.txt\"')")
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
               "('inh_137414af', 'bg_3', NULL, 'tests/test_types.py', "
               "'def test_file_error_surrogates(): pass')")
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result) "
               "VALUES ('tr_1', 'bg_3', 't_own', ?, 'pass')", (HEAD,))
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, "
               "output) VALUES ('tr_2', 'bg_3', 'inh_137414af', ?, 'fail', ?)",
               (HEAD, RED))
    for key in (FAILING, MISTAKEN):
        db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
                   "reported) VALUES (?, 3, 1, 1)", (key,))
    db.commit()
    return db


def test_m120_names_the_red_test_and_its_error_line(bg3):
    page = render_page(bg3, "present", REFS, stalled=[FAILING])[0]
    assert page.startswith("The team stopped work on this change."), page
    assert ("The team gave up: tests/test_types.py still fails after 3 attempts: "
            "AssertionError: Regex pattern did not match.") in page, page
    assert "the tests still fail" not in page, page


def test_the_red_test_gets_no_numbered_line(bg3):
    """The principal never rules on a test (ruled: Roman, 2026-10-08)."""
    page, order = render_page(bg3, "present", REFS, stalled=[FAILING])
    assert "inh_137414af" not in order, order
    numbered = [x for x in page.splitlines() if x.strip()[:2].rstrip(".").isdigit()]
    assert not any("test_types" in x for x in numbered), numbered


def test_m127_says_touch_mistaken_in_words(bg3):
    page = render_page(bg3, "present", REFS, stalled=[FAILING, MISTAKEN])[0]
    assert "could not finish a step" not in page, page
    # One sentence per key, each under 25 words (review of pass 1, finding 1).
    assert ("still fails after 3 attempts: AssertionError: Regex pattern did not "
            "match. The team gave up: the team could not put back code it was not "
            "asked to change after 3 attempts.") in page, page
    assert all(len(s.split()) < 25 for s in _gave_up_sentences(page)), page


def _gave_up_sentences(page: str) -> list[str]:
    """Each sentence of the page that starts "The team gave up:"."""
    return ["The team gave up:" + s for line in page.splitlines()
            for s in line.split("The team gave up:")[1:]]


def test_a_green_batch_keeps_the_kinds_words(bg3):
    bg3.execute("UPDATE test_runs SET result = 'pass'")
    assert _stalled_words(bg3, [FAILING]) == "the tests still fail after 3 attempts"


def _red(db, n: int, path: str, output: str = "E       KeyError: 'name'") -> None:
    db.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) VALUES "
               "(?, 'bg_3', NULL, ?, 'def test(): pass')", (f"inh_{n}", path))
    db.execute("INSERT INTO test_runs (id, batch_id, test_id, commit_sha, result, "
               "output) VALUES (?, 'bg_3', ?, ?, 'fail', ?)",
               (f"tr_{n + 10}", f"inh_{n}", HEAD, output))


def test_two_red_files_are_named_with_one_error_line(bg3):
    _red(bg3, 2, "tests/test_core.py")
    assert _stalled_words(bg3, [FAILING]) == (
        "tests/test_types.py and tests/test_core.py still fail after 3 attempts: "
        "AssertionError: Regex pattern did not match")


def test_a_third_red_file_is_one_more_test_file(bg3):
    """Review of pass 1, finding 4: "1 more test files"."""
    _red(bg3, 2, "tests/test_core.py")
    _red(bg3, 3, "tests/test_utils.py")
    assert _stalled_words(bg3, [FAILING]).startswith(
        "tests/test_types.py, tests/test_core.py and 1 more test file still fail")
    _red(bg3, 4, "tests/test_main.py")
    assert "and 2 more test files still fail" in _stalled_words(bg3, [FAILING])


def test_a_long_error_line_is_cut_on_the_page(bg3):
    """Review of pass 1, finding 5: the page's sentence is the span."""
    long = "E       AssertionError: " + " ".join(f"w{k}" for k in range(40))
    bg3.execute("UPDATE test_runs SET output = ? WHERE id = 'tr_2'", (long,))
    for n in range(2, 6):
        _red(bg3, n, f"tests/test_{n}.py", long)
    page = render_page(bg3, "present", REFS, stalled=[FAILING])[0]
    (sentence,) = _gave_up_sentences(page)
    assert sentence.rstrip().endswith("..."), sentence
    assert len(sentence.split()) < 25, sentence


def test_a_red_file_at_the_root_keeps_its_case(bg3):
    """Review of pass 1, finding 2: `code_gaps` printed "Test_types.py"."""
    from rota.roles.api import Ctx, code_gaps

    bg3.execute("UPDATE tests SET path = 'test_types.py' WHERE id = 'inh_137414af'")
    facts = code_gaps(Ctx(conn=bg3, role="liaison"))["facts"]
    assert any(f.startswith("test_types.py still fails") for f in facts), facts


def test_two_stuck_batches_never_print_one_clause_twice(bg3):
    """Review of pass 1, finding 3: "no verdict ...; no verdict ..."."""
    bg3.execute("INSERT INTO batches (id, item_id, head_commit, status) VALUES "
                "('bg_4', ?, ?, 'running')", (ITEM, HEAD))
    keys = ["critic|tick:review|bg_3", "critic|tick:review|bg_4"]
    for key in keys:
        bg3.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined, "
                    "reported) VALUES (?, 3, 1, 1)", (key,))
    assert _gave_up_words(bg3, keys) == [
        "the review gave no verdict after 3 attempts, on 2 changes"]


def test_the_gave_up_words_print_no_batch_id(bg3):
    """Section 4, items 3 and 5: `render_state` and `code_gaps` said "for bg_3"."""
    from rota.roles.api import Ctx, code_gaps

    assert _gave_up_words(bg3, [FAILING, MISTAKEN]) == [
        "tests/test_types.py still fails after 3 attempts: AssertionError: "
        "Regex pattern did not match",
        "the team could not put back code it was not asked to change after 3 attempts"]
    facts = code_gaps(Ctx(conn=bg3, role="liaison"))["facts"]
    assert ("tests/test_types.py still fails after 3 attempts: AssertionError: "
            "Regex pattern did not match") in facts, facts
    assert not any("bg_3" in f for f in facts), facts
    assert "bg_3" not in "\n".join(x for x in render_state(bg3).splitlines()
                                   if "attempts" in x)


def test_the_wake_detail_names_the_red_test(bg3):
    """Section 4, item 4: `stop_detail` reads the same helper."""
    from rota.core.scheduler import stop_detail

    bg3.execute("DELETE FROM tick_attempts WHERE tick_key = ?", (MISTAKEN,))
    assert stop_detail(bg3, "bg_3") == (
        "tests/test_types.py still fails after 3 attempts: AssertionError: "
        "Regex pattern did not match")
