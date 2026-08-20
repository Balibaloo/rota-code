"""
Challenging a test costs one call; fixing the code costs three. So it challenges.

`L1-DV-fix-the-code-not-the-test` went 5/5 to 0/5 when eight exported JS symbols
entered the index — symbols in a directory the case never touches. Nothing about
what the Developer can see of its own task changed: `probe('pricing')` still
returns five hits, none from `web/`, with the right file first.

So the case flipped on a prompt *perturbation*, and what that measures is that
the choice is not robust. Every run emits, in one turn:

    TOOL: msg.challenge_tester(refs=['tst_6719e7'], round_no=0)
    TOOL: code.write(path='src/catalog/pricing.py', ...)

It is trying to do the right thing behind the wrong thing. The case file has
named the reason since long before this: challenging is *"the escape hatch being
used as a door: cheaper than fixing the code and indistinguishable from
progress."*

**Cheaper** is the whole of it, and it is `none_found` one artefact along. That
one was closed by making both outcomes cite what was read. This closes the same
way: a challenge names the criterion it says the test contradicts, and quotes
both. The graph's own noun for the edge is already *"test disputes criterion"* —
so requiring both is reading the edge rather than inventing a rule.

It does not decide whether the contradiction is *real*. `validators.py` draws
that line: "None of these say the choice was good. They say it was legal." What
it removes is the asymmetry — a session that must read both rows before
challenging has, by then, done the reading that would show it the test is right.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build


CRITERION = "closing an account marks it closed and leaves its invoices in place"
TEST_BODY = "assert invoices_for(account_id) == []"


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "ch.db")
    conn.execute("INSERT INTO items (id, text, kind, provenance) "
                 "VALUES ('i1','close an account','in_scope','decided')")
    conn.execute("INSERT INTO tickets (id, item_id, text) "
                 "VALUES ('tk1','i1','close an account')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text, term_refs) "
                 "VALUES ('c1','tk1',?,'[]')", (CRITERION,))
    conn.execute("INSERT INTO batches (id, item_id, status) "
                 "VALUES ('b1','i1','running')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) "
                 "VALUES ('b1','tk1')")
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                 "VALUES ('tst1','b1','c1','test_close.py',?)", (TEST_BODY,))
    return conn


def _dev(conn):
    return build("developer", conn, session_id="s1", batch_id="b1")


def test_a_challenge_with_only_the_test_is_refused(db):
    """
    The shape the model actually emits, and the one that made the escape hatch
    cheaper than the work: one call, one id, no reason.

    Refused by the *signature*, which is better than the runtime check this was
    written to expect. The model is shown exactly what it may pass — that is
    why `_bind_send` builds two signatures rather than advertising `**kwargs` —
    so a challenge that carries no reason is now a call that does not exist,
    rather than one that exists and is turned away.
    """
    from rota.core.sandbox import ArgumentError

    with pytest.raises((ArgumentError, ValueError)) as exc:
        _dev(db).call("msg.challenge_tester", refs=["tst1"])

    assert "reason" in str(exc.value).lower()


def test_a_challenge_must_name_a_criterion_that_exists_in_this_batch(db):
    """
    An id nobody can follow is not a citation. The criterion has to be one this
    batch is actually working to, or the challenge is about something else.
    """
    db.execute("INSERT INTO tickets (id, item_id, text) "
               "VALUES ('tk9','i1','somewhere else')")
    db.execute("INSERT INTO criteria (id, ticket_id, text, term_refs) "
               "VALUES ('c9','tk9','unrelated','[]')")

    with pytest.raises(ValueError) as exc:
        _dev(db).call("msg.challenge_tester", refs=["tst1", "c9"],
                      reason=f"the criterion says {CRITERION!r} but the test "
                             f"says {TEST_BODY!r}")

    assert "c9" in str(exc.value)


def test_the_reason_must_quote_the_criterion_and_the_test(db):
    """
    Quoted, not paraphrased — the rule `check_segmentation` already holds
    Liaison to. A paraphrase is a claim about two rows; a quote is the rows.
    """
    with pytest.raises(ValueError) as exc:
        _dev(db).call("msg.challenge_tester", refs=["tst1", "c1"],
                      reason="the test contradicts the criterion")

    assert "quote" in str(exc.value).lower()


def test_a_challenge_that_quotes_both_goes_through(db):
    """
    The legitimate sibling, and it is easy when the contradiction is real: the
    criterion says the invoices stay, the test asserts they are gone.
    """
    got = _dev(db).call(
        "msg.challenge_tester", refs=["tst1", "c1"],
        reason=f"the criterion requires that it "
               f"'leaves its invoices in place', and the test asserts "
               f"'{TEST_BODY}', which is the opposite")

    assert got["to"] == "tester"


def test_quoting_is_insensitive_to_whitespace_only(db):
    """
    The one liberty, and the same one segmentation takes. Re-wrapping a quote
    is not paraphrasing it; changing a word is.
    """
    sb = _dev(db)
    got = sb.call(
        "msg.challenge_tester", refs=["tst1", "c1"],
        reason="criterion: 'leaves its\n  invoices in place'; "
               f"test: '{TEST_BODY}'")
    assert got["to"] == "tester"


def test_the_gate_does_not_judge_whether_the_test_is_actually_wrong(db):
    """
    The line `validators.py` draws, kept. A Developer can quote both rows about
    a test that faithfully encodes its criterion and the message will send —
    what it cannot do is send *without having read them*, which is the whole
    difference in cost this exists to remove.
    """
    got = _dev(db).call(
        "msg.challenge_tester", refs=["tst1", "c1"],
        reason=f"'{CRITERION}' versus '{TEST_BODY}'")

    assert got["to"] == "tester", "the gate is about evidence, not correctness"


def test_the_quote_check_is_linear_in_the_text_it_reads():
    """
    The first version enumerated every run of consecutive words in the source
    and normalised each — quadratic, so a 250-word test body built 30,876
    strings and a longer one made the call look like a hang with no GPU in
    sight. A gate that can stall a session is worse than the cheapness it was
    added to remove.

    Bounded rather than merely faster: five thousand words, and the assertion
    is a wall-clock ceiling because that is the failure being prevented.
    """
    import time

    from rota.core.sandbox import _quotes

    source = " ".join(f"w{i}" for i in range(5000))

    start = time.perf_counter()
    assert _quotes(source, "nothing of the sort appears here", 4) is False
    assert _quotes(source, "and then w10 w11 w12 w13 appears", 4) is True
    assert time.perf_counter() - start < 1.0, "the quote check is not linear"


def test_a_quote_shorter_than_the_run_still_counts_when_the_row_is_short(db):
    """
    A criterion of three words cannot yield a four-word run, and refusing it
    would make the gate impossible to satisfy rather than expensive — which is
    the failure mode every gate in this repository is one mistake away from.
    """
    from rota.core.sandbox import _quotes

    assert _quotes("invoices stay put", "it says 'invoices stay put'", 4) is True
    assert _quotes("invoices stay put", "it says something else", 4) is False


def test_a_dict_shaped_ref_is_answered_by_the_guard_that_knows_it(db):
    """
    Ordering, and it cost the legitimate case five runs out of five.

    Models offer `refs=[{"id": "tst_1", "criterion_id": "c_1"}]` — reasonable
    looking, and `stage` has carried a message earned for exactly it since long
    before this gate existed. Placed first, this gate answered that shape with
    a complaint about the criterion, so a session that *had* named one was told
    to name one, could not see the real defect, and repeated the same shape
    until its turns ran out.

    A new check that speaks over an older and better one makes the system less
    diagnosable than it was.
    """
    from rota.core.sandbox import ArgumentError

    with pytest.raises((ArgumentError, ValueError)) as exc:
        _dev(db).call(
            "msg.challenge_tester",
            refs=[{"id": "tst1", "criterion_id": "c1"}, {"id": "c1"}],
            reason=f"'{CRITERION}' versus '{TEST_BODY}'")

    # Matched on the guard's own words rather than on the absence of
    # "criterion" — the refused dict carries a `criterion_id` key, so it is
    # echoed back in the message and a naive absence check fails on the
    # *correct* behaviour.
    said = str(exc.value).lower()
    assert "refs are ids and nothing else" in said, (
        f"the criterion gate spoke over the refs guard: {said}")
