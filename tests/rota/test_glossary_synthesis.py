"""
The third relation between two glossary rows.

Two senses that differ are a collision, kept apart. One sense written twice is a
duplicate, collapsed by `glossary.same`. Neither describes what a survey pass
actually produces, which is N sessions each seeing the word in one place:

    intent               [src]            note with properties and templates
    intent#src_intents   [src/intents]    custom actions in Obsidian
    intent#src_variables [src/variables]  function or action in a plugin
    intent#root          [.]              template with specific action

Not duplicates — no two say the same thing. Not a collision — there is one
intent in this codebase. Four fragments of one meaning, and the answer key's
sense of the word is in none of them.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.roles.api import glossary_synthesise
from rota.testkit.fixtures import seed_provenance


class Ctx:
    def __init__(self, conn, onboarding=True, wake_refs=()):
        # `onboarding` is the session fact: True on an onboarding tick.
        self.conn, self.onboarding = conn, onboarding
        self.role, self.area = "terminologist", None
        # The rows the wake named. `term_collision` is woken *about* specific
        # rows, and the real `Ctx` has carried them since a session woken for
        # `template` synthesised `tick` off the wake kind.
        self.wake_refs = tuple(wake_refs)
        self.batch_id = None      # `_worktree_of` reads it; a survey has none
        self.writes: list = []
        self.opened: set = set()

    def commit(self):
        """Land the buffered writes the way the sandbox would. The kept
        row inherits the refs of the rows it replaces, so a `refs` write is
        among them and the sandbox's own door lands it."""
        from rota.core.db import _apply_write
        from rota.core.runner import _as_write

        for w in self.writes:
            _apply_write(self.conn, _as_write(w))
        self.writes.clear()


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "s.db")
    rows = [
        ("intent", "intent", "note with properties and templates", "src"),
        ("intent#src_intents", "intents", "custom actions in Obsidian", "src/intents"),
        ("intent#src_variables", "intent", "function or action in a plugin", "src/variables"),
        ("intent#root", "intent", "template with specific action", "."),
    ]
    for id, term, short, area in rows:
        conn.execute(
            "INSERT INTO glossary_terms (id, term, sense_short, sense_body, "
            "area) VALUES (?,?,?,?,?)",
            (id, term, short, short + ", at length", area))
        seed_provenance(conn, "glossary_terms", id, "observed")
    return conn


IDS = ["intent", "intent#src_intents", "intent#src_variables", "intent#root"]
WHOLE = "a recipe for making a note, declared in another note's frontmatter"


def test_the_readings_compose_into_one_sense(db):
    """The sense none of the four holds, written from all of them."""
    ctx = Ctx(db)
    out = glossary_synthesise(ctx, ids=IDS, sense_short=WHOLE,
                              sense_body="Named under `intents_to`. It says what "
                                         "note to make, where, and what to ask for.")
    ctx.commit()

    assert out["id"] == "intent", "the family's own name survives"
    assert out["composed_from"] == sorted(i for i in IDS if i != "intent")

    live = [r["id"] for r in db.execute(
        "SELECT id FROM glossary_terms WHERE superseded_by IS NULL")]
    assert live == ["intent"], "one sense left standing"
    assert db.execute("SELECT sense_short FROM glossary_terms WHERE id='intent'"
                      ).fetchone()["sense_short"] == WHOLE


def test_the_partials_stay_readable(db):
    """
    Superseded, never deleted, on the same argument `glossary.same` makes: this
    is a judgement delegated to a session and it cannot be checked mechanically,
    so it stays reversible.
    """
    ctx = Ctx(db)
    glossary_synthesise(ctx, ids=IDS, sense_short=WHOLE, sense_body="...")
    ctx.commit()

    lost = db.execute("SELECT sense_short, sense_body, area FROM glossary_terms "
                      "WHERE id='intent#src_variables'").fetchone()
    assert lost["sense_short"] == "function or action in a plugin"
    assert lost["sense_body"], "the whole row carries forward, not just the flag"
    assert lost["area"] == "src/variables", "and the evidence it was written from"


def test_picking_one_of_the_readings_is_not_synthesis(db):
    """
    The failure this is most likely to produce: restating the row that reads
    best and superseding the rest. That is `glossary.same`, and it has its own
    guard.
    """
    ctx = Ctx(db)
    with pytest.raises(ValueError) as exc:
        glossary_synthesise(ctx, ids=IDS,
                            sense_short="note with properties and templates",
                            sense_body="as above")
    assert "word for word" in str(exc.value)
    assert "glossary.same" in str(exc.value), "and it names the call that was meant"


def test_one_row_is_an_amendment(db):
    ctx = Ctx(db)
    with pytest.raises(ValueError) as exc:
        glossary_synthesise(ctx, ids=["intent"], sense_short="x", sense_body="y")
    assert "more than one reading" in str(exc.value)


def test_two_words_are_two_entries(db):
    """The family check, so a session cannot fold `template` into `intent`."""
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, sense_body, "
               "area) VALUES ('template','template','a pattern','x','src')")
    seed_provenance(db, "glossary_terms", "template", "observed")
    ctx = Ctx(db)
    with pytest.raises(ValueError) as exc:
        glossary_synthesise(ctx, ids=["intent", "template"],
                            sense_short="one thing", sense_body="y")
    assert "different words" in str(exc.value)


def test_a_body_and_a_short_are_both_required(db):
    ctx = Ctx(db)
    with pytest.raises(ValueError):
        glossary_synthesise(ctx, ids=IDS, sense_short=WHOLE, sense_body="  ")


def test_ids_off_the_wake_kind_are_refused_by_name(db):
    """
    Measured on `cnt_q`, the first run of this mode. The session was woken for
    `['template', 'template#src_intents', ...]`, read *"You were woken by:
    tick:term_collision"*, and called
    `glossary.synthesise(ids=['tick', 'tock'], sense_short='a unit of time')`.
    It defined `tick` — the wake kind — forty-two times.

    "is not a glossary id" was true and did not say which ids were. Same fix as
    `glossary.same`: name the set rather than reject the guess.
    """
    ctx = Ctx(db, wake_refs=tuple(IDS))
    with pytest.raises(ValueError) as exc:
        glossary_synthesise(ctx, ids=["tick", "tock"], sense_short="a unit of time",
                            sense_body="a short period")
    msg = str(exc.value)
    assert "not among the rows you were woken about" in msg
    assert "intent#src_variables" in msg, "and it names what they were"


def test_the_readings_arrive_without_being_asked_for(db):
    """
    `glossary.lookup` with no term returns the wake's rows, which is what makes
    it pushable — `push_working_set` sends every read callable with no
    arguments. Before this the senses the session exists to compose were
    reachable only by a call the model had to think of, and the only place the
    rows appeared was the `Refs:` line.
    """
    from rota.roles.api import glossary_lookup

    rows = glossary_lookup(Ctx(db, wake_refs=tuple(IDS)))
    assert {r["id"] for r in rows} == set(IDS)
    assert all(r["sense_short"] for r in rows), "with their senses, not just ids"
    assert {r["area"] for r in rows} == {"src", "src/intents", "src/variables", "."}, \
        "and the area each was read from, which is the evidence they differ"


def test_a_summary_of_the_readings_is_not_a_synthesis(db, tmp_path):
    """
    Measured on `cnt_r`, the first run where this verb worked at all. All three
    results were the readings welded together:

        templates <- 3   "customizable note or document structure"
        intent    <- 2   "template or instruction for organizing and processing notes"
        variable  <- 1   "template placeholder or variable used in templates"

    `templates` is arguably worse than one of its own partials, and `variable`
    is circular. None of the three carries one word from the concordance that
    was pushed into the prompt beside them — summing partial views of a word
    gives a vaguer word, not a truer one.
    """
    src = tmp_path / "intents"
    src.mkdir()
    (src / "frontmatter.ts").write_text(
        "const newIntents: Intent[] = (fm?.intents_to || []).map(\n"
        "  (iFm: any): Intent => parseIntentFrontmatter(app, iFm)\n"
        ");\n", encoding="utf-8")
    db.execute("INSERT OR REPLACE INTO config (key, value) VALUES "
               "('project_root', ?)", (str(tmp_path),))
    db.execute("INSERT INTO code_index (grain, grain_kind, area) VALUES "
               "('intents/frontmatter.ts','path','intents')")

    ctx = Ctx(db, wake_refs=tuple(IDS))
    with pytest.raises(ValueError) as exc:
        glossary_synthesise(ctx, ids=IDS,
                            sense_short="template or instruction for notes",
                            sense_body="a template or set of instructions for notes")
    msg = str(exc.value)
    assert "nothing the readings did not already say" in msg
    assert "code.concordance" in msg, "and it points at what would"
    assert "frontmatter" not in msg, (
        "and it does not list the words that would pass — `cnt_o` put a list of "
        "grains in a refusal and the session defined the list")

    out = glossary_synthesise(
        ctx, ids=IDS,
        sense_short="a recipe for a note, declared in frontmatter under intents_to",
        sense_body="Named under `intents_to`; it says what note to make.")
    assert out["id"] == "intent", "a sense carrying the evidence goes through"
