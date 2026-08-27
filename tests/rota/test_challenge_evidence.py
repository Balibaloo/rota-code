"""
A challenge quotes the thing it disputes.

Challenging costs one call carrying an id; fixing costs reading, writing and
committing. When two outcomes cost that differently, which one you get is
decided by noise -- measured when `L1-DV-fix-the-code-not-the-test` went 5/5
to 0/5 on a prompt perturbation, every run emitting the challenge and the fix
in one turn, the right thing behind the wrong thing.

So the challenge pays its reading up front. The rule is `challenge.uphold`'s,
one loop later: either verdict carries the line it stands on. And it is one
meaning per word: `challenge` carries `quotes=` on all five of its channels,
strictest on developer->tester where both sides of the claimed conflict must
be named and quoted. What none of this decides is whether the contradiction
is real -- a session that has copied out both spans has, by then, done the
reading that would show it the test is right.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.sandbox import build

CRIT = "closing an account leaves its invoices in place for seven years"
TEST = "def test_close():\n    close('a1')\n    assert invoices_for('a1') == []"


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, provenance, approval, "
                 "approval_ver, version) VALUES ('i1','account closure',"
                 "'in_scope','decided','approved',1,1)")
    conn.execute("INSERT INTO tickets (id, item_id, text) VALUES "
                 "('t1','i1','close the account')")
    conn.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
                 "('c1','t1',?)", (CRIT,))
    conn.execute("INSERT INTO batches (id, item_id, status) VALUES "
                 "('b1','i1','running')")
    conn.execute("INSERT INTO batch_tickets (batch_id, ticket_id) VALUES "
                 "('b1','t1')")
    conn.execute("INSERT INTO tests (id, batch_id, criterion_id, path, body) "
                 "VALUES ('ts1','b1','c1','tests/test_close.py',?)", (TEST,))
    conn.commit()
    return conn


def _dev(db):
    return build("developer", db, batch_id="b1", mode="tests_failing")


def test_a_challenge_quoting_both_sides_lands(db):
    """The legitimate sibling survives easily: quoting both is trivial when
    the contradiction is there."""
    sb = _dev(db)
    sb.call("msg.challenge_tester", refs=["c1", "ts1"],
            quotes="the criterion says 'leaves its invoices in place' and "
                   "the test asserts invoices_for('a1') == []")
    assert sb.ctx.outbound, "the challenge staged"


def test_a_paraphrase_is_refused_naming_the_fix(db):
    sb = _dev(db)
    with pytest.raises(ValueError, match="verbatim"):
        sb.call("msg.challenge_tester", refs=["c1", "ts1"],
                quotes="the criterion wants invoices kept but the test "
                       "wants them gone")


def test_a_challenge_naming_no_test_is_refused(db):
    """One call carrying an id was the whole cost; now the pair is the price
    of entry."""
    sb = _dev(db)
    with pytest.raises(ValueError, match="no test"):
        sb.call("msg.challenge_tester", refs=["c1"],
                quotes="leaves its invoices in place")


def test_a_challenge_with_no_words_is_refused_by_the_channel(db):
    sb = _dev(db)
    with pytest.raises(ValueError, match="quotes"):
        sb.call("msg.challenge_tester", refs=["c1", "ts1"], quotes="")


def test_a_foreign_criterion_is_not_this_batchs_fight(db):
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES "
               "('t2','i1','other work')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c2','t2','something about a different ticket entirely')")
    db.commit()
    sb = _dev(db)
    with pytest.raises(ValueError, match="not a criterion of this batch"):
        sb.call("msg.challenge_tester", refs=["c2", "ts1"],
                quotes="something about a different ticket entirely, and "
                       "assert invoices_for('a1') == []")


def test_the_other_channels_hold_the_looser_form_of_the_rule(db):
    """Terminologist -> vision_keeper: quote the disputed row, whichever
    text-bearing row the refs name."""
    sb = build("terminologist", db, mode="criterion_repair")
    with pytest.raises(ValueError, match="verbatim, not a paraphrase"):
        sb.call("msg.challenge_vision_keeper", refs=["c1"],
                quotes="the account-closing rule cannot be machine-checked")
    sb.call("msg.challenge_vision_keeper", refs=["c1"],
            quotes="'leaves its invoices in place for seven years' names no "
                   "observable store")
    assert sb.ctx.outbound


def test_a_quote_survives_the_line_wrap_it_was_copied_across(db):
    """Whitespace-normalised on both sides: a span copied across a wrap is
    still a quote."""
    sb = _dev(db)
    sb.call("msg.challenge_tester", refs=["c1", "ts1"],
            quotes="it says 'leaves its invoices\n   in place' yet asserts "
                   "invoices_for('a1')\n== []")
    assert sb.ctx.outbound


def test_a_contradicting_twin_constraint_is_refused_toward_the_challenge(db):
    """The wrong door, measured: handed a ratified statement conflicting with
    a decided constraint, the Architect recorded the conflict as a second
    constraint five runs of five -- once inventing an attribution to justify
    it -- and never challenged. Two constraints about one subject saying
    different things is incoherence whatever the intent, so the amend door
    refuses the twin and names the challenge as the exit."""
    db.execute("INSERT INTO constraints (id, headline, provenance) VALUES "
               "('cn1','invoices are kept seven years after account closure',"
               "'decided')")
    db.commit()
    sb = build("architect", db, mode="deliver")
    with pytest.raises(ValueError, match="challenge_vision_keeper"):
        sb.call("model.amend", headline="Invoices deleted with accounts",
                text="closing an account deletes its invoices")
    out = sb.call("model.amend", headline="exports stream in constant memory",
                  text="csv exports never buffer the whole set")
    assert out["id"] == "exports_stream_in_constant_memory",         "a genuinely distinct commitment still lands"
