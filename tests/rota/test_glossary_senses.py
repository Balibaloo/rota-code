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

    def __init__(self, conn, provenance="observed"):
        self.conn = conn
        self.provenance = provenance
        self.writes: list = []
        self.role = "terminologist"

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


def test_the_icalendar_duplicate_is_refused(db):
    """The exact pair the run produced, in the order it produced them."""
    first = Ctx(db)
    glossary_amend(first, term="Alarm", sense_short=ALARM)
    first.commit()

    with pytest.raises(ValueError) as exc:
        glossary_amend(Ctx(db), term="alarm", sense_short=ALARM,
                       sense="observed")

    assert "already means that" in str(exc.value)


def test_the_refusal_says_what_sense_is_for(db):
    """
    A guard that only says no teaches the session to try another word. This one
    has to name the confusion it is catching: `sense` names *which meaning*, and
    provenance is not a meaning.
    """
    first = Ctx(db)
    glossary_amend(first, term="Calendar",
                   sense_short="a collection of events and components")
    first.commit()

    with pytest.raises(ValueError) as exc:
        glossary_amend(Ctx(db), term="calendar",
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
    glossary_amend(ctx, term="nonce", sense_short="a replay guard")
    ctx.commit()

    out = glossary_amend(ctx, term="nonce",
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
    glossary_amend(ctx, term="nonce", sense_short="a replay guard")
    glossary_amend(ctx, term="nonce", sense_short="a session binding",
                   sense="binding")
    ctx.commit()

    glossary_amend(ctx, term="nonce", sense_short="a session binding",
                   sense_body="bound at issue, checked at redemption",
                   sense="binding")
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
    glossary_amend(ctx, term="Component", sense_short="a part of a calendar")

    with pytest.raises(ValueError):
        glossary_amend(ctx, term="component", sense_short="a part of a calendar",
                       sense="observed")


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
        glossary_amend(ctx, term=term, sense_short=short)
    ctx.commit()

    for term, short in (("alarm", ALARM),
                        ("calendar", "a collection of events and components"),
                        ("component", "a part of a calendar")):
        with pytest.raises(ValueError):
            glossary_amend(ctx, term=term, sense_short=short, sense="observed")
    ctx.commit()

    assert term_collision(db) == [], "no word carries two senses, so none is owed"
