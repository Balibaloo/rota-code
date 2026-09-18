"""
The term-collision loop on cold click nights (frame 34, 2026-09-17).

Nights 83 and 84 ran the same three sessions seventeen times. The
Terminologist woke on `tick:term_collision` and reported. The Liaison relayed
the principal's earlier words. The Terminologist called `glossary.adopt`, the
runner refused it for want of a landed ruling, and nothing was open when the
sessions ended, so the tick fired again.

Three defects, one cycle. A words-only reply landed a `rulings` row with an
empty `per_item` and no verdict anywhere. The relay's verdict lookup climbed
one cause hop. And `term_collision` counted a family as ruled through a
decision only, while `glossary.adopt` writes a `refs` row of kind `ruling`.

The rule the fix serves: the principal rules and the Liaison writes it, the
tool never rules for the principal, and every open obligation stays visible
until something discharges it.
"""
from __future__ import annotations

import json

from rota.core.db import init_db
from rota.core.predicates import (UNADDRESSED_ANSWER, Wake, outstanding,
                                  term_collision)
from rota.core.runner import _mode_key, resolve_inbound
from rota.roles import prompts
from rota.roles.principal import Answer, Ask, apply_rulings, land, parse_reply
from rota.testkit.fixtures import seed_provenance, seed_ref

import pytest


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _two_senses(db):
    """The night-84 family: `group` twice, both observed, nobody ruling."""
    db.execute("INSERT INTO glossary_terms (id, term, sense_short) "
               "VALUES ('g1','group','a set of related options')")
    seed_provenance(db, "glossary_terms", "g1", "observed")
    db.execute("INSERT INTO glossary_terms (id, term, sense_short) "
               "VALUES ('g2','group','a command that holds other commands')")
    seed_provenance(db, "glossary_terms", "g2", "observed")
    db.commit()


def _clarify(db):
    """The report, the clarify it became, and the clarify as an open ask."""
    refs = json.dumps(["g1", "g2"])
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m1','th','terminologist',"
               "'liaison','report',?,1,'answered')", (refs,))
    db.execute("INSERT INTO messages (id, cause_id, cause_kind, thread_id, "
               "from_role, to_role, verb, body_refs, body_text, seq, status) "
               "VALUES ('m2','m1','message','th','liaison','principal',"
               "'clarify',?,'Does group mean the options or the command?',"
               "2,'open')", (refs,))
    db.commit()
    return Ask(message_id="m2", verb="clarify", refs=["g1", "g2"])


def _answering(db, words):
    """The principal answers the clarify. The Liaison wakes in `answering`."""
    from rota.core.sandbox import build

    ask = _clarify(db)
    msg = land(db, ask, parse_reply(ask, words))
    db.commit()
    wake = Wake(role="liaison", kind="message", detail="converse",
                message_id=msg, refs=("g1", "g2"))
    assert _mode_key(wake, db) == "answering"
    sb = build("liaison", db, mode="normal", session_id="sess_answer",
               allow=prompts.mode_tools("liaison", "answering"))
    sb.ctx.trigger = msg
    return sb, msg


def _land_writes(db, ctx):
    """Commit what the session staged, the way the pipeline does."""
    for table, rid, row in ctx.writes:
        if table == "rulings":
            db.execute(
                "INSERT INTO rulings (id, ask_id, reply_id, per_item, words, "
                "status) VALUES (?,?,?,?,?,?)",
                (row["id"], row["ask_id"], row["reply_id"], row["per_item"],
                 row["words"], row["status"]))
        elif table == "ledger":
            db.execute(
                "INSERT OR REPLACE INTO ledger (id, about_ref, about_table, "
                "default_taken, kind, status, author) VALUES (?,?,?,?,?,?,?)",
                (rid, row["about_ref"], row["about_table"],
                 row["default_taken"], row["kind"], row["status"],
                 row["author"]))
        elif table == "refs":
            db.execute(
                "INSERT OR IGNORE INTO refs (src_table, src_id, kind, target) "
                "VALUES (?,?,?,?)",
                (row["src_table"], row["src_id"], row["kind"], row["target"]))
    ctx.writes.clear()
    db.commit()


def _relay(db, cause):
    """The relay the answering session sends, as `_bind_send` builds it."""
    db.execute("INSERT INTO messages (id, cause_id, cause_kind, thread_id, "
               "from_role, to_role, verb, body_refs, seq, status) "
               "VALUES ('m4',?,'message','th','liaison','terminologist',"
               "'relay',?,4,'open')", (cause, json.dumps(["g1", "g2"])))
    db.commit()
    return resolve_inbound(db, Wake(role="terminologist", kind="message",
                                    message_id="m4", detail="relay"))


def test_the_liaison_rules_the_reply_and_the_relay_carries_the_ruling(db):
    """
    The answer path, end to end: the words, the reading, the relay.

    The Liaison is the seat that reads the principal's words. In `answering`
    mode it held the three relay tools and nothing that could write what it
    read, so the reading existed in one session and nowhere after it. The
    relay then climbed one cause hop for a verdict that was never written.
    """
    _two_senses(db)
    sb, msg = _answering(
        db, "the first one. a group is the set of options, not the command")

    # Row ids, not line numbers. A clarify numbers no line, and the page the
    # door used to invent from the refs is a page the principal never saw.
    with pytest.raises(ValueError, match="not a row of this question"):
        sb.call("rulings.rule", rulings={"1": "approve", "2": "contest"},
                words="the first one")
    out = sb.call("rulings.rule",
                  rulings={"g1": "approve", "g2": "contest"},
                  words="the first one. a group is the set of options, "
                        "not the command")
    assert out["per_item"] == {"g1": "approve", "g2": "contest"}

    # The row lands through the one door. The clarify closed at the keypress,
    # so no second verdict message is written and the `rulings` row is the
    # record of the reading.
    _land_writes(db, sb.ctx)
    apply_rulings(db)
    row = db.execute("SELECT status, per_item FROM rulings WHERE reply_id = ? "
                     "AND per_item != '{}'", (msg,)).fetchone()
    assert row["status"] == "landed"

    inbound = _relay(db, msg)
    assert inbound["principal_verdict"] == {"g1": "approve", "g2": "contest"}, (
        "the owner reads the ruling in the field its brief names")
    assert inbound["principal_said"].startswith("the first one")


def test_an_answer_that_names_no_row_is_logged_and_parks_the_word(db):
    """
    Silence is not consent, and neither is an answer about something else.

    Night 84: the principal's words were a sentence about the project, and the
    Liaison relayed them three times verbatim. The Terminologist could do
    nothing with them, nothing was left open, and the tick fired again.
    """
    _two_senses(db)
    assert term_collision(db), "two live senses, nobody ruling"

    sb, _ = _answering(db, "ship the smallest thing that works")
    # The empty ruling the old door wrote is refused: a clarify numbers every
    # row it carries, and an unruled row cannot close as approved.
    with pytest.raises(ValueError, match="rulings is a map"):
        sb.call("rulings.rule", rulings={})

    for rid in ("g1", "g2"):
        sb.call("ledger.unaddressed", about_ref=rid,
                question="which sense of group the project means")
    assert not sb.ctx.outbound, "an answer about something else relays nothing"
    assert all(w[2]["kind"] == "unaddressed_answer"
               for w in sb.ctx.writes if w[0] == "ledger"), (
        "the door stamps the class; no predicate reads the prose")

    _land_writes(db, sb.ctx)
    assert term_collision(db) == [], (
        "the ledger row holds the word between cycles")

    # Parked, not discharged. The row is open, the register still carries it,
    # and the agenda puts it to the principal.
    assert db.execute("SELECT count(*) FROM ledger WHERE status = 'open'"
                      ).fetchone()[0] == 2
    assert outstanding(db), "a wake-suppression is not a discharge"


def test_an_adopted_sense_is_a_ruled_sense(db):
    """
    `glossary.adopt` writes a `refs` row of kind `ruling` and no decision.

    `term_collision` read `decisions.refs` only, so the family the principal
    settled kept firing. Plausible rather than observed on night 84, because
    no adopt ever landed there.

    The ruling has to name the row. A `ruling` ref is also what makes a row
    read as `decided`, and two decided senses are the collision this tick
    exists for: `L1-TE-put-a-word-with-two-senses-to-the-principal` seeds
    exactly that pair.
    """
    _two_senses(db)
    assert term_collision(db), "nobody has ruled yet"

    _clarify(db)
    db.execute("UPDATE messages SET status = 'answered' WHERE id = 'm2'")
    db.commit()
    assert term_collision(db), "an answered clarify parks nothing"

    # Decided, and about nothing: the shape a fixture seeds for provenance.
    db.execute("INSERT INTO rulings (id, ask_id, per_item, words, status) "
               "VALUES ('r0','m2','{}','seeded as decided','landed')")
    seed_ref(db, "glossary_terms", "g1", "ruling", "r0")
    seed_ref(db, "glossary_terms", "g2", "ruling", "r0")
    db.commit()
    assert term_collision(db), (
        "a ruling that names no row rules nothing; two decided senses still "
        "collide")

    # The ruling the principal gave on this word, adopted. It names one sense
    # of the two, so the other is still live and the word still collides.
    db.execute("INSERT INTO rulings (id, ask_id, per_item, words, status) "
               "VALUES ('r1','m2','{\"g1\": \"approve\"}','the options one',"
               "'landed')")
    seed_ref(db, "glossary_terms", "g1", "ruling", "r1")
    db.commit()
    assert term_collision(db), "one ruled sense beside one live sense collides"

    # The ruling on both senses. The second is contested, which is a ruling.
    db.execute("INSERT INTO rulings (id, ask_id, per_item, words, status) "
               "VALUES ('r2','m2','{\"g1\": \"approve\", \"g2\": \"contest\"}',"
               "'the options one, not the command','landed')")
    db.commit()

    assert db.execute("SELECT count(*) FROM decisions").fetchone()[0] == 0
    assert term_collision(db) == [], (
        "a row the ruling names is ruled, decision or no decision")


def test_a_contest_only_ruling_parks_the_family(db):
    """
    Finding 1 of the diff review of 6895000: a ruling is a ruling.

    The reviewer ruled every row `contest`. `glossary.adopt` skipped both
    rows, so no `refs` row of kind `ruling` was written, no ledger row
    existed, and the tick fired again on cycles two and three. Cycle two runs
    in `report` mode, whose tool list could write neither a ruling nor a
    reading.
    """
    _two_senses(db)
    sb, msg = _answering(db, "neither: a group is the folder on disk")
    out = sb.call("rulings.rule", rulings={"g1": "contest", "g2": "contest"},
                  words="neither: a group is the folder on disk")
    assert out["per_item"] == {"g1": "contest", "g2": "contest"}
    _land_writes(db, sb.ctx)
    apply_rulings(db)

    assert _relay(db, msg)["principal_verdict"] == {"g1": "contest",
                                                   "g2": "contest"}
    db.execute("UPDATE messages SET status = 'answered' WHERE status = 'open'")
    db.commit()
    assert db.execute("SELECT count(*) FROM refs WHERE kind = 'ruling' "
                      "AND src_table = 'glossary_terms'").fetchone()[0] == 0
    assert term_collision(db) == [], (
        "the principal ruled, so the word is settled for this cycle")


def test_a_clarify_takes_a_partial_map_and_logs_the_rest(db):
    """
    Finding 2: the door told the Liaison to approve a row the words never
    named.

    `order` was filled from the refs, which gave a clarify a numbered page the
    principal never saw. The door then refused a partial reading with "a line
    the reply does not contest is approve". Silence is not consent.
    """
    _two_senses(db)
    sb, _ = _answering(db, "the options one")
    out = sb.call("rulings.rule", rulings={"g1": "approve"},
                  words="the options one")
    assert out["per_item"] == {"g1": "approve"}, "one row, one verdict"
    assert out["parked"] == ["g2"], "the row the words missed is logged"

    _land_writes(db, sb.ctx)
    row = db.execute("SELECT about_ref, kind, status FROM ledger").fetchone()
    assert (row["about_ref"], row["kind"], row["status"]) == (
        "g2", "unaddressed_answer", "open")


def test_a_reply_that_names_no_row_lands_no_approve(db):
    """
    Finding 2, the second half: the reviewer landed two approves for the
    reply "what time is the meeting".

    The door cannot read the words, so it holds the two facts it can check.
    An empty map on a clarify is silence, not consent. A reading with no
    words on file has nothing behind it.
    """
    _two_senses(db)
    sb, _ = _answering(db, "what time is the meeting")
    with pytest.raises(ValueError, match="rulings is a map"):
        sb.call("rulings.rule", rulings={}, words="what time is the meeting")
    with pytest.raises(ValueError, match="words is empty"):
        sb.call("rulings.rule", rulings={"g1": "approve", "g2": "approve"})
    assert not [w for w in sb.ctx.writes if w[0] == "rulings"], (
        "no approve is on file for a reply that ruled nothing")


def test_a_signoff_on_a_parking_row_does_not_rule_the_word(db):
    """
    Finding 3: one keypress discharged the collision for good.

    The reviewer parked `group`, then approved the parking rows on the agenda
    page. `land` wrote a decision whose refs name the sense, and the tick
    read the sense as ruled. The word went silent with two live senses and no
    ruling. A keypress on a row that says the answer missed the question
    cannot answer the question.
    """
    _two_senses(db)
    sb, _ = _answering(db, "ship the smallest thing that works")
    for rid in ("g1", "g2"):
        sb.call("ledger.unaddressed", about_ref=rid,
                question="which sense of group the project means")
    _land_writes(db, sb.ctx)
    db.execute("UPDATE messages SET status = 'answered' WHERE status = 'open'")
    db.commit()
    assert term_collision(db) == [], "parked while the rows are open"

    rows = [r["id"] for r in db.execute("SELECT id FROM ledger "
                                        "WHERE status = 'open'")]
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m9','th2','liaison',"
               "'principal','confirm',?,9,'open')", (json.dumps(rows),))
    db.commit()
    land(db, Ask(message_id="m9", verb="confirm", refs=rows),
         Answer(verb="verdict", per_item={r: "approve" for r in rows},
                text="ok"))
    db.execute("UPDATE messages SET status = 'answered' WHERE status = 'open'")
    db.commit()

    assert db.execute("SELECT count(*) FROM decisions").fetchone()[0] == 2
    assert term_collision(db), (
        "the question comes back; the signoff discharged the ledger row and "
        "not the collision")


def test_a_paraphrased_parking_sentence_still_parks(db):
    """
    Finding 4: the predicate matched the parking sentence as a substring.

    The reviewer's paraphrase did not park, and the tick fired again. The
    ledger id was a hash of the text, so every paraphrase wrote a new row and
    the ledger grew every cycle. The class is on the row now.
    """
    _two_senses(db)
    sb, _ = _answering(db, "ship the smallest thing that works")
    for rid in ("g1", "g2"):
        sb.call("ledger.unaddressed", about_ref=rid,
                question="Which sense of group is meant, do you think?")
    _land_writes(db, sb.ctx)
    db.execute("UPDATE messages SET status = 'answered' WHERE status = 'open'")
    db.commit()
    assert term_collision(db) == [], "the class parks it, not the wording"
    assert db.execute("SELECT default_taken FROM ledger").fetchone()[0].startswith(
        UNADDRESSED_ANSWER), "the prose still reads as the sentence"

    # A second cycle in other words is the same row, not a second one.
    for rid in ("g1", "g2"):
        sb.call("ledger.unaddressed", about_ref=rid,
                question="said another way, which one is group")
    _land_writes(db, sb.ctx)
    assert db.execute("SELECT count(*) FROM ledger").fetchone()[0] == 2


def test_a_relay_before_the_ruling_is_refused(db):
    """
    Finding 5: nothing enforced the order the brief asks for.

    The runner breaks the session as soon as `ctx.outbound` is non-empty, so
    a session that relays first ends with no ruling and no ledger row. That
    is the night-84 end state. The order is the door's now.
    """
    _two_senses(db)
    sb, _ = _answering(db, "the options one")
    with pytest.raises(ValueError, match="read the reply before you relay"):
        sb.call("msg.relay_terminologist", refs=["g1", "g2"])

    sb.call("rulings.rule", rulings={"g1": "approve", "g2": "contest"},
            words="the options one")
    assert sb.call("msg.relay_terminologist", refs=["g1", "g2"]), (
        "the reading is on file, so the relay goes")


def test_one_adopted_sense_does_not_silence_a_live_sense(db):
    """
    Finding 9: the word still means two things.

    After the good path `g1` is adopted and `g2` stays live, observed and
    unruled. The tick read one ruled id as the whole family and never fired
    again, and the only other reader of that row is `observed_entries`,
    which is quarantined.
    """
    _two_senses(db)
    sb, msg = _answering(db, "the options one")
    sb.call("rulings.rule", rulings={"g1": "approve"},
            words="the options one")
    _land_writes(db, sb.ctx)
    apply_rulings(db)

    from rota.core.sandbox import build

    _relay(db, msg)
    term = build("terminologist", db, mode="normal", session_id="sess_adopt",
                 allow=["glossary.adopt"])
    term.ctx.trigger = "m4"
    assert term.call("glossary.adopt", ids=["g1", "g2"])["adopted"] == ["g1"]
    _land_writes(db, term.ctx)
    db.execute("UPDATE ledger SET status = 'resolved'")
    db.execute("UPDATE messages SET status = 'answered' WHERE status = 'open'")
    db.commit()

    assert term_collision(db), "one live sense is still a collision"
