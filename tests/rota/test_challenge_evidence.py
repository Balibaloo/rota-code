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
# The Developer's reason (frame 200, pass 5). Its head holds no verdict, so
# the verdict door of pass 5b admits it.
REASON = ("right code keeps the invoices, so the test must assert that "
          "invoices_for('a1') still holds them")
QUOTES = ["leaves its invoices in place", "assert invoices_for('a1') == []"]


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "rota.db")
    conn.execute("INSERT INTO items (id, text, kind, approval, "
                 "approval_ver, version) VALUES ('i1','account closure',"
                 "'in_scope','approved',1,1)")
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
    the contradiction is there.

    Frame 328: the ruling of 2026-08-26 asks for a contiguous span of the
    row, so each quote is a span. Prose around the spans is refused."""
    sb = _dev(db)
    with pytest.raises(ValueError, match="not in the live text of c1"):
        sb.call("msg.challenge_tester", refs=["c1", "ts1"],
                quotes="the criterion says 'leaves its invoices in place' and "
                       "the test asserts invoices_for('a1') == []", reason=REASON)
    sb.call("msg.challenge_tester", refs=["c1", "ts1"],
            quotes=["leaves its invoices in place",
                    "invoices_for('a1') == []"], reason=REASON)
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


def test_the_other_channels_hold_the_strict_form_of_the_rule(db):
    """Terminologist -> vision_keeper: each quote is a span of the disputed
    row, verbatim. Frame 333: the ruling of 2026-08-26 holds on all five
    channels, so prose around the span is refused here too."""
    sb = build("terminologist", db, mode="criterion_repair")
    with pytest.raises(ValueError, match="not a span of the live text of c1"):
        sb.call("msg.challenge_vision_keeper", refs=["c1"],
                quotes="the account-closing rule cannot be machine-checked")
    with pytest.raises(ValueError, match="not a span of the live text of c1"):
        sb.call("msg.challenge_vision_keeper", refs=["c1"],
                quotes="'leaves its invoices in place for seven years' names "
                       "no observable store")
    sb.call("msg.challenge_vision_keeper", refs=["c1"],
            quotes="'leaves its invoices in place for seven years'")
    assert sb.ctx.outbound


def test_a_quote_survives_the_line_wrap_it_was_copied_across(db):
    """Whitespace-normalised on both sides: a span copied across a wrap is
    still a quote."""
    sb = _dev(db)
    sb.call("msg.challenge_tester", refs=["c1", "ts1"],
            quotes=["leaves its invoices\n   in place",
                    "invoices_for('a1')\n== []"], reason=REASON)
    assert sb.ctx.outbound


def test_a_quote_under_the_floor_is_refused(db):
    """Frame 328, review 1, finding 2: `in` and `a1` are spans of the rows,
    and they pay no reading. A quote holds 12 characters or the whole row."""
    sb = _dev(db)
    with pytest.raises(ValueError, match="`in`, and it is shorter than 12 "
                                         "characters"):
        sb.call("msg.challenge_tester", refs=["c1", "ts1"],
                quotes=["in", "a1"], reason=REASON)
    with pytest.raises(ValueError, match="`invoices`, and it is shorter"):
        sb.call("msg.challenge_tester", refs=["c1", "ts1"],
                quotes=["invoices"], reason=REASON)
    assert not sb.ctx.outbound


def test_one_quote_never_stands_for_both_rows(db):
    """Frame 328, review 1, finding 2: the test's docstring holds the
    criterion's words, so one quote is a span of both rows."""
    db.execute("UPDATE tests SET body = ? WHERE id = 'ts1'", (
        'def test_close():\n    """closing an account leaves its invoices '
        'in place"""\n    close(\'a1\')\n    assert invoices_for(\'a1\') == []',))
    db.commit()
    sb = _dev(db)
    with pytest.raises(ValueError, match="as the quote of c1 and of ts1. "
                                         "Each row needs a quote of its own"):
        sb.call("msg.challenge_tester", refs=["c1", "ts1"],
                quotes=["closing an account leaves its invoices in place"],
                reason=REASON)
    sb.call("msg.challenge_tester", refs=["c1", "ts1"],
            quotes=["closing an account leaves its invoices in place",
                    "assert invoices_for('a1') == []"], reason=REASON)
    assert sb.ctx.outbound


def test_an_elided_quote_is_one_quote_and_no_span(db):
    """Frame 328, review 1, finding 5: the binder hands its list on, so the
    elision inside one string is not a join of two quotes."""
    sb = _dev(db)
    with pytest.raises(ValueError, match="not in the live text of c1"):
        sb.call("msg.challenge_tester", refs=["c1", "ts1"],
                quotes=["leaves its invoices in place ... "
                        "assert invoices_for('a1') == []"], reason=REASON)


def test_a_contradicting_twin_constraint_is_refused_toward_the_challenge(db):
    """The wrong door, measured: handed a ratified statement conflicting with
    a decided constraint, the Architect recorded the conflict as a second
    constraint five runs of five -- once inventing an attribution to justify
    it -- and never challenged. Two constraints about one subject saying
    different things is incoherence whatever the intent, so the amend door
    refuses the twin and names the challenge as the exit."""
    db.execute("INSERT INTO constraints (id, headline) VALUES "
               "('cn1','invoices are kept seven years after account closure')")
    db.commit()
    sb = build("architect", db, mode="deliver")
    with pytest.raises(ValueError, match="challenge_vision_keeper"):
        sb.call("model.amend", headline="Invoices deleted with accounts",
                text="closing an account deletes its invoices")
    out = sb.call("model.amend", headline="exports stream in constant memory",
                  text="csv exports never buffer the whole set")
    assert out["id"] == "exports_stream_in_constant_memory",         "a genuinely distinct commitment still lands"


def test_the_refusal_writes_the_repair_out_when_it_can(db):
    """S0 walk four: the Developer chose the right door with the right
    quotes three sessions running and died on refs=['t1','t1'] every time.
    A test knows its own criterion, so the refusal names the exact call --
    satisfiable by copying, the strongest refusal shape this repo has."""
    sb = _dev(db)
    with pytest.raises(ValueError, match=r"send refs=\['c1', 'ts1'\]"):
        sb.call("msg.challenge_tester", refs=["ts1", "ts1"],
                quotes="leaves its invoices in place ... invoices_for('a1')")


# ---------------------------------------------------------------------------
# Frame 200, pass 5 (rota workflow): the reason of a Developer's challenge
# travels as the Developer's own `decisions` row, and the message refs it.
# Night 143's bg_5: 0 of 6 challenges carried a reason, and 0 of 6 Tester
# bodies reached the code (`plans/night143-cycle-bg5.md`, section 2). The
# numbers below are the tests of `plans/frame200-pass5-design.md`.
# ---------------------------------------------------------------------------

def _reason_id(text, crit="c1", test="ts1"):
    import hashlib
    return "d_" + hashlib.sha256(f"{text}|{crit}|{test}".encode()).hexdigest()[:10]


def _refused_reason(sb, **kwargs):
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", refs=["c1", "ts1"], quotes=QUOTES,
                **kwargs)
    return str(exc.value)


_CALL = ("Send msg.challenge_tester(refs=['c1', 'ts1'], reason=\"<the error, "
         "the test, the line, and the call that takes the argument>\") with "
         "the same "
         "quotes.")
_SAID = ("reason= names the test by its id, the error it got and the line "
         "of the test that raises it. It is the one part of a challenge "
         "the Tester cannot read in the test.")


def test_the_tool_line_shows_the_reason_slot_and_not_none(db):
    """Frame 200, pass 5b, item 2: `reason=None` reads as optional."""
    [line] = [s for s in _dev(db).signatures()
              if s.startswith("msg.challenge_tester(")]
    assert ('reason="<the error, the test, the line, and the call that '
            'takes the argument>"') in line
    assert "reason=None" not in line


def test_20_the_reason_slot_names_the_test_beside_the_line(db):
    """Frame 200, pass 5g: night 144's reasons named a function that both
    test files hold, and the Tester fixed the sibling test. The slot asks
    for the test, so the row names the challenged one."""
    from rota.core.sandbox import REASON_SLOT
    assert REASON_SLOT == ('reason="<the error, the test, the line, and the '
                           'call that takes the argument>"')
    [line] = [s for s in _dev(db).signatures()
              if s.startswith("msg.challenge_tester(")]
    assert REASON_SLOT in line


def test_1_a_challenge_with_no_reason_is_refused_with_the_call_written_out(db):
    sb = _dev(db)
    said = _refused_reason(sb)
    assert said == ("a challenge to the tester carries reason=, and yours has "
                    "none. " + _SAID + " " + _CALL)
    assert not sb.ctx.outbound and not sb.ctx.writes
    [offer] = [o for o in sb.ctx.offers if o.op == "msg.challenge_tester"]
    assert offer.args["refs"] == ["c1", "ts1"] and "reason" in offer.args


def test_2_a_reason_of_five_words_is_refused_with_the_six_word_sentence(db):
    said = _refused_reason(_dev(db), reason="the test is simply wrong")
    assert said == ("a challenge to the tester carries a reason= of 6 words or "
                    "more, and yours has 5. " + _SAID + " " + _CALL)


def test_3_a_reason_that_copies_a_quote_is_refused(db):
    said = _refused_reason(_dev(db), reason="assert invoices_for('a1') == []")
    assert said.startswith(
        "a challenge to the tester carries a reason= of 6 words or more")
    said = _refused_reason(
        _dev(db), reason="closing an account leaves its invoices in place")
    assert said == ("reason= copies the quotes or the criterion. The quotes "
                    "already travel, and reason= names the error the test "
                    "got, the test's id, and the line of the test that raises "
                    "it. " + _CALL)


def test_4_an_admitted_challenge_stages_the_reason_as_the_developers_row(db):
    import json
    sb = _dev(db)
    out = sb.call("msg.challenge_tester", refs=["c1", "ts1"], quotes=QUOTES,
                  reason=REASON)
    rid = _reason_id(REASON)
    assert sb.ctx.writes == [("decisions", rid, {
        "author": "developer", "text": REASON, "refs": json.dumps(["c1", "ts1"]),
        "supersedes": None, "resolves_ledger": None})]
    [msg] = sb.ctx.outbound
    assert msg["body_refs"] == ["c1", "ts1", rid]
    assert msg["body_text"] == " ... ".join(QUOTES), "the message keeps no new words"
    assert out == {"id": msg["id"], "to": "tester", "verb": "challenge"}


def test_5_the_same_reason_on_the_same_refs_is_one_row(db):
    first, second = _dev(db), _dev(db)
    for sb in (first, second):
        sb.call("msg.challenge_tester", refs=["ts1", "c1"], quotes=QUOTES,
                reason=REASON)
    assert first.ctx.writes[0][1] == second.ctx.writes[0][1] == _reason_id(REASON)


@pytest.mark.parametrize("author", ["principal", "vision_keeper"])
def test_6_a_derived_id_of_another_author_is_refused_and_the_row_stays(db, author):
    rid = _reason_id(REASON)
    db.execute("INSERT INTO decisions (id, author, text, refs) VALUES (?, ?, "
               "'keep the invoices', '[]')", (rid, author))
    db.commit()
    sb = _dev(db)
    said = _refused_reason(sb, reason=REASON)
    # Fact F23: the door reads the commit's rule, so the text names both roles.
    assert said == (f"the reason's id {rid} is a decisions row by {author}, "
                    f"and you write as "
                    f"developer. A journal row is its author's record. Write "
                    f"the reason in your own words.")
    assert not sb.ctx.writes and not sb.ctx.outbound
    row = db.execute("SELECT author, text FROM decisions WHERE id = ?", (rid,)).fetchone()
    assert tuple(row) == (author, "keep the invoices")


def test_9_a_critics_challenge_takes_no_reason_and_stages_no_row(db):
    import inspect
    sb = build("critic", db, batch_id="b1", mode="review")
    fn = sb["msg"].challenge_tester
    assert "reason" not in inspect.signature(fn).parameters
    sb.call("msg.challenge_tester", refs=["c1", "ts1"], quotes=QUOTES)
    assert [m["body_refs"] for m in sb.ctx.outbound] == [["c1", "ts1"]]
    assert not [w for w in sb.ctx.writes if w[0] == "decisions"]


def test_10_the_testers_challenge_wake_shows_the_reason_row(db):
    """End to end through the binder and the commit: the Tester's wake on
    the challenge resolves the reason ref to the row's author and text."""
    from rota.core.db import OutboundMessage, SessionResult, session_commit
    from rota.core.runner import _as_write, resolve_inbound
    from rota.core.scheduler import Wake

    sb = _dev(db)
    out = sb.call("msg.challenge_tester", refs=["c1", "ts1"], quotes=QUOTES,
                  reason=REASON)
    session_commit(db, SessionResult(
        session_id="s1", role="developer",
        writes=[_as_write(w) for w in sb.ctx.writes],
        messages=[OutboundMessage(id=m["id"], to_role=m["to_role"], verb=m["verb"],
                                  body_refs=m["body_refs"], body_text=m["body_text"])
                  for m in sb.ctx.outbound]))
    inbound = resolve_inbound(db, Wake("tester", "message", message_id=out["id"],
                                       detail="challenge"))
    rid = _reason_id(REASON)
    assert inbound["resolved_refs"][rid] == {
        "id": rid, "author": "developer", "text": REASON, "table": "decisions"}


def test_17_the_evidence_doors_hint_names_the_reason(db):
    """Fix 2: the hint writes reason= as the slot, and copies a reason that
    the refused call carried."""
    sb = _dev(db)
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", refs=["ts1", "ts1"], quotes=QUOTES)
    assert str(exc.value).endswith(
        "send refs=['c1', 'ts1'], reason=\"<the error, the test, the line, "
        "and the call that takes the argument>\"")
    with pytest.raises(ValueError) as exc:
        sb.call("msg.challenge_tester", refs=["ts1"], quotes=QUOTES, reason=REASON)
    assert str(exc.value).endswith(f"send refs=['c1', 'ts1'], reason={REASON!r}")


def test_17_the_owner_route_of_a_conflict_about_a_test_names_the_reason(db):
    from rota.roles import api
    sb = _dev(db)
    with pytest.raises(ValueError) as exc:
        sb.call("ledger.log", about_ref="ts1", about_table="tests",
                assumption="the criterion keeps the invoices and the test "
                           "asserts that they are gone", kind="conflict")
    assert ("Send msg.challenge_tester(refs=['c1', 'ts1'], reason=\"<the "
            "error, the test, the line, and the call that takes the "
            "argument>\") with "
            "quotes= copied from c1 and from "
            "ts1") in str(exc.value)
    [offer] = [o for o in sb.ctx.offers if o.op == "msg.challenge_tester"]
    assert offer.args["reason"] is api.INVENT


def test_18_the_slot_text_sent_back_unchanged_is_refused(db):
    from rota.core.sandbox import REASON_SLOT
    # Pass 5e: the briefs' slot, copied as a reason, is the slot text too.
    for sent in (REASON_SLOT.split("=", 1)[1].strip('"'),
                 REASON_SLOT.split("=", 1)[1].strip('"<>'),
                 "<the error, the test, the line, and the call that takes "
                 "the argument>",
                 # Pass 5h: the slot before pass 5g, which night 144's hints
                 # hold (review 5g, finding 2).
                 "the error, the line, and the call that takes the argument",
                 "<the error, the line, and the call that takes the "
                 "argument>"):
        said = _refused_reason(_dev(db), reason=sent)
        assert said == ("reason= is still the slot text. Name the error the "
                        "test got, the test's id, and the line of the test "
                        "that raises it. " + _CALL), sent


def test_19_a_reason_that_says_the_test_passes_is_refused(db):
    """Frame 200, pass 5b: a verdict is no fact. The door reads the head of
    the reason's first sentence for "passes", "is met" and "is correct"."""
    for sent in ("the test passes on the code as it stands today",
                 "The criterion is met by the code, so nothing changes",
                 "the test is correct and the code raises an error",
                 # Pass 5g: review 5e's low 3 found four verdicts that the
                 # lookahead admitted. The review's "it passes in CI
                 # already" has 5 words, so "the test" puts it past the
                 # word door.
                 "the test passes for me on the current code",
                 "the test passes with the current code",
                 "the test passes in CI already",
                 "the test passes cleanly against the code"):
        said = _refused_reason(_dev(db), reason=sent)
        assert said.startswith("reason= says the test passes or the "
                               "criterion is met."), sent
    # The same words past the head are a fact, and the door admits them. So
    # is "passes" with an object (review 5b, finding 1).
    for fact in ("the test calls runner.invoke with package_name, and "
                 "invoke has no such argument, so it never passes",
                 "the test passes package_name to invoke",
                 "The test passes package_name to runner.invoke, and invoke "
                 "raises TypeError on it",
                 "The test passes `package_name` to `runner.invoke`, and "
                 "`invoke` raises TypeError on it",
                 "runner.invoke(package_name=...) passes an argument invoke "
                 "does not take, TypeError",
                 # Pass 5h: a preposition after "passes" starts a fact too
                 # (review 5g, finding 3).
                 "the test passes in the args list to runner.invoke and "
                 "invoke raises TypeError",
                 "tst_v1 passes with package_name missing to version_option, "
                 "RuntimeError"):
        sb = _dev(db)
        sb.call("msg.challenge_tester", refs=["c1", "ts1"], quotes=QUOTES,
                reason=fact)
        assert sb.ctx.outbound, fact


def test_a_reason_past_600_characters_is_cut_and_admitted(db):
    sb = _dev(db)
    long = REASON + " " + "and the body must call it with the account id " * 20
    out = sb.call("msg.challenge_tester", refs=["c1", "ts1"], quotes=QUOTES,
                  reason=long)
    text = sb.ctx.writes[0][2]["text"]
    assert text.startswith(" ".join(long.split())[:600] + "\nCUT the reason: ")
    assert out["note"].startswith("CUT your reason: ")
