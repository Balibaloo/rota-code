"""
`sense` bought a second row, and the row meant what the first one meant.

`glossary.amend` derives the id from the term, so writing a word twice amends
it and accidental duplication is impossible — that was earned on oauthlib,
where twelve sessions wrote `endpoint` five times. The escape hatch is `sense=`,
and its docstring is confident about the cost: *"deliberate duplication costs
one argument."*

The icalendar run paid it by accident. One survey session wrote `Alarm`. A later
one wrote `alarm` with `sense="observed"` — the word its own brief puts in front
of it twice on the same page, *"everything you write here is `observed`, not
`decided`"* — and got `alarm#observed`, whose `sense_short` was
character-for-character what `alarm` already said. Three words: alarm, calendar,
component. Six rows for three meanings.

Then `term_collision` did its job on the result. It raises on two rows sharing a
term with nobody ruling, so it raised three obligations, woke the Terminologist
for each, and put three ambiguities on the register that did not exist in the
codebase or in anybody's head.

The brief had already ruled: **"the same sense twice is not two senses"**, and a
`sense` you have not actually distinguished *"puts a collision in the record
that does not exist"*. Right, in bold, on the page the session was reading, and
enforced by nothing — the fourth time in one sitting that the prose was correct
and no structure held it.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.predicates import term_collision
from rota.roles.api import glossary_amend


class Ctx:
    """The slice of a session context `glossary.amend` reads."""

    def __init__(self, conn, provenance="observed", read=None):
        self.conn = conn
        self.provenance = provenance
        self.writes: list = []
        self.role = "terminologist"
        self.opened: set = set()
        # `read=` seeds the words `code.source` would have recorded, so a test
        # about the *sense* rules does not have to stage a file read to reach
        # them. `None` leaves the attribute off entirely, which is how the
        # older cases in this file run: the read gate is a separate subject and
        # has its own two below.
        if read is not None:
            self.read_words = set(read)

    def commit(self):
        """Land the buffered writes the way the sandbox would."""
        for table, id, cols in self.writes:
            keys = ", ".join(cols)
            marks = ", ".join("?" * len(cols))
            self.conn.execute(
                f"INSERT OR REPLACE INTO {table} (id, {keys}) "
                f"VALUES (?, {marks})", (id, *cols.values()))
        self.writes.clear()


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "s.db")


ALARM = "an event that triggers an action"
ALARM_BODY = "a VALARM inside a VEVENT; fires relative to the event"


def test_the_icalendar_duplicate_is_refused(db):
    """The exact pair the run produced, in the order it produced them."""
    first = Ctx(db)
    glossary_amend(first, term="Alarm", sense_body=ALARM_BODY, sense_short=ALARM)
    first.commit()

    with pytest.raises(ValueError) as exc:
        glossary_amend(Ctx(db), term="alarm", sense_body=ALARM_BODY,
                       sense_short=ALARM, sense="observed")

    assert "already means that" in str(exc.value)


def test_the_refusal_says_what_sense_is_for(db):
    """
    A guard that only says no teaches the session to try another word. This one
    has to name the confusion it is catching: `sense` names *which meaning*, and
    provenance is not a meaning.
    """
    first = Ctx(db)
    glossary_amend(first, term="Calendar", sense_body="the VCALENDAR object",
                   sense_short="a collection of events and components")
    first.commit()

    with pytest.raises(ValueError) as exc:
        glossary_amend(Ctx(db), term="calendar", sense_body="the VCALENDAR object",
                       sense_short="A collection of events and components.",
                       sense="observed")

    msg = str(exc.value)
    assert "provenance" in msg, "the mis-fill it is actually catching"
    assert "Drop `sense`" in msg, "and the call that was meant"


def test_a_genuine_second_sense_still_costs_one_argument(db):
    """
    The escape hatch stays open — this is the case it was built for. `nonce` is
    a replay guard in one module and a session binding in another, and both rows
    have to exist.
    """
    ctx = Ctx(db)
    glossary_amend(ctx, term="nonce", sense_body="checked once, then discarded",
                   sense_short="a replay guard")
    ctx.commit()

    out = glossary_amend(ctx, term="nonce", sense_body="issued with the session",
                         sense_short="a session binding", sense="binding")
    ctx.commit()

    assert out["id"] == "nonce#binding"
    assert db.execute("SELECT COUNT(*) n FROM glossary_terms "
                      "WHERE term = 'nonce'").fetchone()["n"] == 2


def test_amending_a_second_sense_is_not_a_collision_with_itself(db):
    """
    Filling in the body of an existing second sense keeps its `sense_short`, and
    the row it matches is the row it is replacing. A guard that cannot tell
    those apart makes the second sense un-amendable the moment it exists.
    """
    ctx = Ctx(db)
    glossary_amend(ctx, term="nonce", sense_body="checked once, then discarded",
                   sense_short="a replay guard")
    glossary_amend(ctx, term="nonce", sense_body="issued with the session",
                   sense_short="a session binding", sense="binding")
    ctx.commit()

    glossary_amend(ctx, term="nonce",
                   sense_body="bound at issue, checked at redemption",
                   sense_short="a session binding", sense="binding")
    ctx.commit()

    rows = db.execute("SELECT sense_body FROM glossary_terms "
                      "WHERE id = 'nonce#binding'").fetchall()
    assert rows[0]["sense_body"].startswith("bound at issue")


def test_one_session_cannot_do_it_to_itself(db):
    """
    The measured case was two sessions, but nothing made it two: the writes are
    buffered until the turn lands, so a session that wrote the word a minute ago
    cannot see it in the table. Pending writes have to count.
    """
    ctx = Ctx(db)
    glossary_amend(ctx, term="Component", sense_body="VEVENT, VTODO, VALARM",
                   sense_short="a part of a calendar")

    with pytest.raises(ValueError):
        glossary_amend(ctx, term="component", sense_body="VEVENT, VTODO, VALARM",
                       sense_short="a part of a calendar", sense="observed")


def test_the_phantom_collisions_are_gone(db):
    """
    The point of the guard, measured where it was felt. Six rows for three
    meanings woke the Terminologist three times over ambiguities that did not
    exist; the refusal is worth having because this is what it prevents.
    """
    ctx = Ctx(db)
    for term, short in (("Alarm", ALARM),
                        ("Calendar", "a collection of events and components"),
                        ("Component", "a part of a calendar")):
        glossary_amend(ctx, term=term, sense_body=f"the {term} object", sense_short=short)
    ctx.commit()

    for term, short in (("alarm", ALARM),
                        ("calendar", "a collection of events and components"),
                        ("component", "a part of a calendar")):
        with pytest.raises(ValueError):
            glossary_amend(ctx, term=term, sense_body=f"the {term} object",
                           sense_short=short, sense="observed")
    ctx.commit()

    assert term_collision(db) == [], "no word carries two senses, so none is owed"


def test_a_label_is_not_a_meaning(db):
    """
    What 57 calls on the Obsidian plugin actually produced.

        term='github'      sense_short='repository'    sense_body='a collection of files…'
        term='repository'  sense_short='data storage'

    github is a repository, repository is data storage. A taxonomy, not a
    meaning -- and the definition pushed into the body, where the index never
    shows it. The field was asked for first and called "short", and a short
    field asked for before any explanation exists reads as a request for a
    label.

    This cannot assert that a summary is good; it asserts that the body is
    obtained first and that neither field can be skipped, which is what stops
    the short one being written in a vacuum.
    """
    with pytest.raises(ValueError) as exc:
        glossary_amend(Ctx(db), term="github", sense_short="repository")

    assert "sense_body" in str(exc.value), "it must name the field it wants"


def test_a_blank_index_line_is_refused(db):
    """
    A body with no summary is not a cheaper term, it is an invisible one.

    `sense_short` is the only column the glossary index carries, so every
    session after this one sees a blank row and nothing else. On the measured
    run two of eleven terms were like this.

    It is also what the second-sense check compares. An empty one has no
    counterpart in `seen` -- the code pops the empty key before looking -- so it
    walked straight past the guard that exists to stop exactly the row it was
    creating, and `github#repository` was written in silence.
    """
    with pytest.raises(ValueError) as exc:
        glossary_amend(Ctx(db), term="github",
                       sense_body="a repository on GitHub")

    msg = str(exc.value)
    assert "sense_short" in msg
    assert "index" in msg, "say why it matters, not just that it is missing"


def test_the_measured_second_row_can_no_longer_be_written(db):
    """
    The exact call that minted `github#repository`, and cost 44 turns of one run.

        s7  term='github'  sense='repository'  sense_short=''  sense_body='a repository on GitHub'
    """
    ctx = Ctx(db)
    glossary_amend(ctx, term="github", sense_body="where this project is hosted",
                   sense_short="the remote holding this repository")
    ctx.commit()

    with pytest.raises(ValueError):
        glossary_amend(Ctx(db), term="github", sense="repository",
                       sense_short="", sense_body="a repository on GitHub")

    assert db.execute("SELECT COUNT(*) n FROM glossary_terms "
                      "WHERE term = 'github'").fetchone()["n"] == 1


def test_a_word_you_never_read_cannot_be_defined(db):
    """
    The one artefact write in the system with no read requirement.

    `model.amend` has refused to bind a constraint to an unread grain since law
    12; `surveys.attest` refuses a citation for a grain nobody opened. The
    glossary -- which every role downstream inherits as fact -- had neither.

    Measured on the Obsidian plugin: a session woken for `src/intents` called
    `code.source` exactly once, on the directory, which returns a listing and
    deliberately leaves `opened` untouched because listing is not reading. It
    then wrote `intent`, `note` and `template`. `intent` came out as "a specific
    action or goal" -- the English meaning, on a plugin where an intent is a
    note-creation recipe declared in a note's frontmatter. Its brief said, in
    bold, "open a grain before you define a word in it".
    """
    with pytest.raises(ValueError) as exc:
        glossary_amend(Ctx(db, read=[]), term="intent",
                       sense_body="a specific action or goal",
                       sense_short="specific action or goal")

    msg = str(exc.value)
    assert "nothing you read" in msg
    assert "opened nothing" in msg, "say what it did, not only what it did not"


def test_reading_a_file_that_uses_the_word_is_enough(db):
    """
    The gate is on the word, not on reading in general, and it takes its words
    from the same decomposition `code.vocabulary` ranks by -- so the block
    cannot offer a word this then refuses. Opening one file and defining eight
    words off it is the shape it stops.
    """
    ctx = Ctx(db, read=["intent", "frontmatter", "template"])

    out = glossary_amend(ctx, term="intent",
                         sense_body="a note-creation recipe declared under "
                                    "`intents_to` in a note's frontmatter",
                         sense_short="a recipe for making a note")
    assert out["id"] == "intent"

    with pytest.raises(ValueError) as exc:
        glossary_amend(ctx, term="selection",
                       sense_body="a range of text", sense_short="text range")
    assert "selection" in str(exc.value)
