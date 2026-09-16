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
from rota.testkit.fixtures import seed_provenance


class Ctx:
    """The slice of a session context `glossary.amend` reads."""

    def __init__(self, conn, onboarding=True, read=None, area=None):
        self.conn = conn
        # The session fact: True on an onboarding tick.
        self.onboarding = onboarding
        # The area the session was surveying. Evidence for whether a second,
        # differing sense is one thing described twice or the word doing
        # different work somewhere else. `None` is how a non-survey mode runs.
        self.area = area
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
            if table == "refs":
                # The relation has no `id` column: the pair is the row.
                # A `retire` write removes the row, as `db._apply_ref` does.
                if cols.get("retire"):
                    self.conn.execute(
                        "DELETE FROM refs WHERE src_table = ? AND src_id = ? "
                        "AND kind = ? AND target = ?",
                        (cols["src_table"], cols["src_id"], cols["kind"],
                         cols["target"]))
                    continue
                self.conn.execute(
                    f"INSERT OR REPLACE INTO refs ({keys}) VALUES ({marks})",
                    tuple(cols.values()))
                continue
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
    # A survey session: the gate is scoped to the mode with code in front of
    # it. `deliver` wakes this role on a ratified statement with no codebase to
    # read, and refusing there refused the job.
    with pytest.raises(ValueError) as exc:
        glossary_amend(Ctx(db, area="src/intents", read=[]), term="intent",
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
    ctx = Ctx(db, area="src/intents", read=["intent", "frontmatter", "template"])

    out = glossary_amend(ctx, term="intent",
                         sense_body="a note-creation recipe declared under "
                                    "`intents_to` in a note's frontmatter",
                         sense_short="a recipe for making a note")
    assert out["id"] == "intent"

    with pytest.raises(ValueError) as exc:
        glossary_amend(ctx, term="selection",
                       sense_body="a range of text", sense_short="text range")
    assert "selection" in str(exc.value)


def test_a_differing_sense_from_another_area_is_a_second_row(db):
    """
    The collision the system was built to surface, and threw away as a duplicate.

    Both arrive in the same shape -- one word, written twice, by two sessions --
    and `INSERT OR REPLACE` on an id derived from the term kept the last. So
    `endpoint` written five times meaning the same thing, which the derivation
    exists to stop, was indistinguishable from `folder` written twice meaning two
    different things, which is what the repository actually does.

    Measured across two runs: the correct sense was written early and destroyed
    by a later session four times. `folder: "in the context of template
    variables"` overwritten by `"a directory where notes are stored"`. `intent:
    "a type of frontmatter that defines a template or action"` overwritten by
    `"a plugin for Obsidian"`. Half the bad glossary was answers the run already
    had.
    """
    a = Ctx(db, area="src/variables/providers", read=["folder", "variable"])
    glossary_amend(a, term="folder", sense_body="one of five prompt types",
                   sense_short="a variable type naming a folder")
    a.commit()

    b = Ctx(db, area="src/intents", read=["folder", "note"])
    out = glossary_amend(b, term="folder", sense_body="where notes are kept",
                         sense_short="a directory in the vault")
    b.commit()

    assert out["id"] != "folder", "the second sense must not land on the first"
    rows = {r["id"]: r["sense_short"] for r in db.execute(
        "SELECT id, sense_short FROM glossary_terms WHERE term = 'folder'")}
    assert len(rows) == 2, "both senses survive; neither wins silently"
    assert "a variable type naming a folder" in rows.values()


def test_the_same_area_saying_it_again_is_an_amendment(db):
    """
    Area is evidence, not a rule against writing twice. One session refining its
    own sense, or a later session in the same area, is one thing described twice
    -- which is what the derivation was built for and stays.
    """
    a = Ctx(db, area="src/variables/providers", read=["folder"])
    glossary_amend(a, term="folder", sense_body="a prompt type",
                   sense_short="names a folder")
    a.commit()

    b = Ctx(db, area="src/variables/providers", read=["folder"])
    out = glossary_amend(b, term="folder", sense_body="a prompt type, validated",
                         sense_short="names a folder, checked against filters")
    b.commit()

    assert out["id"] == "folder"
    assert db.execute("SELECT COUNT(*) n FROM glossary_terms "
                      "WHERE term = 'folder'").fetchone()["n"] == 1


def test_one_word_said_twice_can_finally_be_said_so(db):
    """
    `term_collision`'s brief has always named two outcomes -- "if they say the
    same thing, that is a duplicate and not a collision, and saying so is the
    answer" -- and its working set was `glossary.lookup`, `glossary.consult` and
    `msg.report_liaison`. The only way to say anything was to escalate. Three
    measured sessions looked the same two rows up eleven times each and ended
    with nothing they could do.

    Superseded rather than deleted: sameness is a judgement being delegated and
    cannot be checked mechanically, so the losing sense stays readable.
    """
    from rota.roles.api import glossary_same

    a = Ctx(db, area="src/intents", read=["note"])
    glossary_amend(a, term="note", sense_body="a file in the vault with frontmatter",
                   sense_short="a vault file")
    a.commit()
    b = Ctx(db, area="src", read=["note"])
    glossary_amend(b, term="note", sense_body="a document in Obsidian holding notes",
                   sense_short="an Obsidian document")
    b.commit()
    assert db.execute("SELECT COUNT(*) n FROM glossary_terms "
                      "WHERE term = 'note'").fetchone()["n"] == 2

    c = Ctx(db)
    out = glossary_same(c, keep="note", drop="note#src",
                        why="both say a file in the vault")
    c.commit()

    assert out["superseded"] == "note#src"
    live = [r["id"] for r in db.execute(
        "SELECT id FROM glossary_terms WHERE term='note' AND superseded_by IS NULL")]
    assert live == ["note"], "one live sense"
    lost = db.execute("SELECT sense_short, sense_body, area FROM glossary_terms "
                      "WHERE id='note#src'").fetchone()
    assert lost["sense_short"] and lost["sense_body"], (
        "the losing sense stays readable -- a partial write nulls the rest of "
        "the row, so supersede has to carry it forward whole")
    assert lost["area"] == "src", "and keeps the evidence it was written from"


def test_it_will_not_merge_two_different_words(db):
    """It says two rows are one word said twice. It is not for relating words."""
    from rota.roles.api import glossary_same

    a = Ctx(db, area="src", read=["note", "folder"])
    glossary_amend(a, term="note", sense_body="a vault file", sense_short="a file")
    glossary_amend(a, term="folder", sense_body="a prompt type", sense_short="a type")
    a.commit()

    with pytest.raises(ValueError) as exc:
        glossary_same(Ctx(db), keep="note", drop="folder", why="they are not")
    assert "different words" in str(exc.value)


def test_a_merge_repoints_what_referred_to_the_losing_sense(db):
    """
    The claim is that the two rows say the same thing, so a reference to one is
    a reference to the other. Leaving them is the quiet kind of wrong this whole
    change is against: `check_criteria_terms` validates against every row
    including superseded ones, so a stale ref stays green while naming the sense
    that was just declared redundant.
    """
    from rota.roles.api import glossary_same

    a = Ctx(db, area="src/intents", read=["note"])
    glossary_amend(a, term="note", sense_body="a file in the vault", sense_short="a vault file")
    a.commit()
    b = Ctx(db, area="src", read=["note"])
    glossary_amend(b, term="note", sense_body="a document in Obsidian", sense_short="a document")
    b.commit()

    db.execute("INSERT INTO items (id, text, kind, approval, "
               "approval_ver, version) VALUES "
               "('i1','make a note','in_scope','draft',1,1)")
    seed_provenance(db, "items", "i1", "observed")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','x')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c1','tk1','a note is created')")
    db.execute("INSERT INTO refs (src_table, src_id, kind, target) VALUES "
               "('criteria','c1','term','note#src')")

    c = Ctx(db)
    out = glossary_same(c, keep="note", drop="note#src", why="both say a vault file")
    c.commit()

    assert out["repointed"] == ["c1"]
    refs = [r["target"] for r in db.execute(
        "SELECT target FROM refs WHERE src_table = 'criteria' AND src_id = 'c1' "
        "AND kind = 'term' ORDER BY target")]
    # The ref to the losing sense is retired with the repoint.
    assert refs == ["note"], "the criterion now names the sense that survived"


def test_a_merge_lists_the_repointed_rows_as_the_columns_did(db):
    """`repointed` keeps the order the columns gave: the criteria first,
    then the business rules, each in the order the refs were written. The
    relation walked the tables by name, which put the rules first."""
    from rota.roles.api import glossary_same

    a = Ctx(db, area="src/intents", read=["note"])
    glossary_amend(a, term="note", sense_body="a file in the vault", sense_short="a vault file")
    a.commit()
    b = Ctx(db, area="src", read=["note"])
    glossary_amend(b, term="note", sense_body="a document in Obsidian", sense_short="a document")
    b.commit()

    db.execute("INSERT INTO items (id, text, kind, approval, "
               "approval_ver, version) VALUES "
               "('i1','make a note','in_scope','draft',1,1)")
    seed_provenance(db, "items", "i1", "observed")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1','i1','x')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) VALUES "
               "('c1','tk1','a note is created')")
    db.execute("INSERT INTO business_rules (id, text) VALUES ('r1','a note is kept')")
    # The rule's ref is written first. The table order wins over the rowid.
    db.execute("INSERT INTO refs (src_table, src_id, kind, target) VALUES "
               "('business_rules','r1','term','note#src')")
    db.execute("INSERT INTO refs (src_table, src_id, kind, target) VALUES "
               "('criteria','c1','term','note#src')")

    c = Ctx(db)
    out = glossary_same(c, keep="note", drop="note#src", why="both say a vault file")
    c.commit()

    assert out["repointed"] == ["c1", "r1"]


def test_the_modes_own_name_is_not_a_reason(db):
    """
    The first version required `why` to be non-empty, which is not the same as
    requiring it to say anything. The measured run answered `why="term_collision"`
    -- the name of the mode it was woken in -- three times, and the merge went
    through each time. A guard that accepts any non-empty string is a guard
    against forgetting, and forgetting was not the risk.

    The check is that the reason shares a content word with one of the two
    senses. A reason about neither of them is a reason about something else.
    """
    from rota.roles.api import glossary_same

    a = Ctx(db, area="src/intents", read=["note"])
    glossary_amend(a, term="note", sense_body="a file in the vault",
                   sense_short="a vault file")
    a.commit()
    b = Ctx(db, area="src", read=["note"])
    glossary_amend(b, term="note", sense_body="a document in Obsidian",
                   sense_short="an Obsidian document")
    b.commit()

    with pytest.raises(ValueError) as exc:
        glossary_same(Ctx(db), keep="note", drop="note#src", why="term_collision")
    assert "does not mention anything either sense says" in str(exc.value)

    assert db.execute(
        "SELECT COUNT(*) n FROM glossary_terms "
        "WHERE term='note' AND superseded_by IS NULL").fetchone()["n"] == 2, (
        "both senses are still live -- the merge did not happen")


def test_a_reason_they_differ_is_not_a_reason_they_are_the_same(db):
    """
    Measured twice: `why="different provenance"`, merging two rows while stating
    a reason they are not the same. Two senses that differ go to the principal;
    this call is for two rows that say one thing. The vocabulary for arguing
    difference is small and unambiguous, so it is checked for directly.
    """
    from rota.roles.api import glossary_same

    a = Ctx(db, area="src/intents", read=["note"])
    glossary_amend(a, term="note", sense_body="a file in the vault",
                   sense_short="a vault file")
    a.commit()
    b = Ctx(db, area="src", read=["note"])
    glossary_amend(b, term="note", sense_body="a document in Obsidian",
                   sense_short="an Obsidian document")
    b.commit()

    with pytest.raises(ValueError) as exc:
        glossary_same(Ctx(db), keep="note", drop="note#src",
                      why="different provenance")
    msg = str(exc.value)
    assert "not* the same" in msg
    assert "report_liaison" in msg, "and it says where a differing sense goes"


def test_the_root_areas_second_sense_has_a_name(db):
    """
    Both id branches build `slug#tag`, and both could produce a bare trailing
    `#`. Area `.` -- the root area, which every repository has -- slugifies to
    nothing, so the second sense of a word written there became `intent#`.

    Measured on cnt: the `term_collision` wake for that row looked the id up as
    a *term* twice, called `glossary.same(keep='both')`, reported to the Liaison
    and discharged nothing. An id nobody can type is an id nobody can discharge.
    """
    a = Ctx(db, area="src/intents", read=["intent"])
    glossary_amend(a, term="intent", sense_body="a recipe declared in frontmatter",
                   sense_short="a note-creation recipe")
    a.commit()

    b = Ctx(db, area=".", read=["intent"])
    out = glossary_amend(b, term="intent", sense_body="what the plugin runs",
                         sense_short="the unit the plugin executes")
    b.commit()

    assert out["id"] == "intent#root"
    assert not out["id"].endswith("#"), "an id nobody can type"
    assert db.execute("SELECT area FROM glossary_terms WHERE id='intent#root'"
                      ).fetchone()["area"] == ".", "and it still says where it came from"


def test_a_blank_sense_tag_is_no_tag(db):
    """
    `sense="  "` is truthy and slugifies to nothing. It asked for a second sense
    and named none, which is the amendment it should have been.
    """
    a = Ctx(db, read=["nonce"])
    glossary_amend(a, term="nonce", sense_body="checked once, then discarded",
                   sense_short="a replay guard")
    a.commit()

    out = glossary_amend(a, term="nonce", sense_body="checked once and discarded",
                         sense_short="a replay guard", sense="  ")
    a.commit()

    assert out["id"] == "nonce"
    assert db.execute("SELECT COUNT(*) n FROM glossary_terms "
                      "WHERE term='nonce'").fetchone()["n"] == 1


def test_the_frame_you_were_woken_in_is_not_a_sense(db):
    """
    `sense` names a meaning, and in twelve runs it never once did. Every
    non-empty value ever passed, counted across every cnt database: `area` x24,
    `code.area()` x5, `repository` x3, `data storage` x3, `survey` x2,
    `error` x1, and three whole sentences that swallowed `, sense_body=` into
    themselves. Nine runs carry a row with a bogus tag — `templates#area`,
    `templates#survey`, `github#repository`, `workflow#code_area_`.

    Not carelessness. Asked for a word naming which sense this is, a session
    reaches for the most available noun, and the most available nouns are the
    mode it was woken in and the tool it just called.
    """
    ctx = Ctx(db, read=["template"])
    glossary_amend(ctx, term="template", sense_body="a note used as a pattern",
                   sense_short="a note used as a pattern")
    ctx.commit()

    # Ignored, not refused. Refusing produced a session that re-sent the
    # identical call twelve times: `cnt_m`'s `.github` sessions sent
    # `sense='survey'` and landed nothing at all. Dropping it is the right
    # reading anyway — the tag carries no information worth preserving — and the
    # call becomes the plain amend it should have been.
    for bad in ("survey", "area", "repository"):
        ctx = Ctx(db, read=["template"])
        out = glossary_amend(ctx, term="template",
                             sense_body="something else entirely",
                             sense_short="a different thing", sense=bad)
        ctx.commit()
        assert out["id"] == "template", f"{bad}: amends, never `template#{bad}`"
        assert "frame you were woken in" in out["note"], bad

    assert db.execute("SELECT COUNT(*) n FROM glossary_terms "
                      "WHERE term='template'").fetchone()["n"] == 1, (
        "one row, not four")


def test_a_tool_call_is_not_a_sense(db):
    """`code.area()` was passed five times. It is where the session had just
    been, which is not a meaning of anything."""
    ctx = Ctx(db, read=["workflow"])
    glossary_amend(ctx, term="workflow", sense_body="a CI job", sense_short="a CI job")
    ctx.commit()

    ctx2 = Ctx(db, read=["workflow"])
    out = glossary_amend(ctx2, term="workflow", sense_body="another thing",
                         sense_short="another thing", sense="code.area()")
    ctx2.commit()
    assert out["id"] == "workflow", "the tool name is dropped, the write lands"
    assert "is a call, not a meaning" in out["note"]


def test_a_sentence_belongs_in_the_body(db):
    """
    Three runs passed a whole sentence and one of them swallowed the next
    argument's name into it. A tag is a word or two; the explanation has a
    field of its own.
    """
    ctx = Ctx(db, read=["issue", "template"])
    glossary_amend(ctx, term="issue_template", sense_body="a bug form",
                   sense_short="a bug form")
    ctx.commit()

    ctx2 = Ctx(db, read=["issue", "template"])
    out = glossary_amend(ctx2, term="issue_template",
                         sense_body="the other form", sense_short="the other form",
                         sense="refers to the template used for feature requests")
    ctx2.commit()
    assert out["id"] == "issue_template", (
        "the sentence is dropped rather than slugified into an id — "
        "`issue_template#refers_to_the_template_used_for_feature_requests` is a "
        "real id two runs actually produced")
    assert "sense_body" in out["note"]


def test_a_real_second_sense_is_still_one_argument(db):
    """The hatch stays open — this is the case it exists for, unchanged."""
    ctx = Ctx(db, read=["nonce"])
    glossary_amend(ctx, term="nonce", sense_body="checked once, then discarded",
                   sense_short="a replay guard")
    ctx.commit()

    out = glossary_amend(ctx, term="nonce", sense_body="issued with the session",
                         sense_short="a session binding", sense="binding")
    ctx.commit()
    assert out["id"] == "nonce#binding"


def test_the_fold_up_bucket_does_not_raise_a_collision(db):
    """
    `tick_survey` says what `.` is, in its own words: *"what did not belong
    anywhere else by construction — `areas.py` folds small directories up into
    it. So it is the one area whose vocabulary is least likely to be the
    project's."*

    The second-row rule is justified by the opposite claim — "two senses from
    different areas are the word doing different work in two places" — and that
    does not hold for a bucket. `.` is not a place.

    Measured across `cnt_i` and `cnt_j`: two of five and two of four distinct
    collisions were a `#root` row against a real area's. Each cost up to three
    sessions and two exhausted the attempt bound, in runs that then had no
    budget left to reach the Architect.

    The row is still written and still readable. What is withdrawn is the claim
    that a person must rule on it.
    """
    a = Ctx(db, area="src/variables", read=["variable"])
    glossary_amend(a, term="variable", sense_body="a value gathered from the user",
                   sense_short="a prompted value")
    a.commit()
    b = Ctx(db, area=".", read=["variable"])
    glossary_amend(b, term="variable", sense_body="something that varies",
                   sense_short="a changing thing")
    b.commit()

    live = [r["id"] for r in db.execute(
        "SELECT id FROM glossary_terms WHERE term='variable' "
        "AND superseded_by IS NULL ORDER BY id")]
    assert live == ["variable", "variable#root"], "both rows exist and stay readable"
    assert term_collision(db) == [], "and nobody is woken to rule on the bucket"


def test_two_real_areas_still_collide(db):
    """The rule is about the bucket, not about second senses."""
    a = Ctx(db, area="src/variables", read=["variable"])
    glossary_amend(a, term="variable", sense_body="a value gathered from the user",
                   sense_short="a prompted value")
    a.commit()
    b = Ctx(db, area="src/intents", read=["variable"])
    glossary_amend(b, term="variable", sense_body="a placeholder in a template",
                   sense_short="a template placeholder")
    b.commit()

    assert term_collision(db), "two real areas disagreeing is still a question"


def test_the_mode_you_are_in_is_not_a_word_the_project_uses(db):
    """
    `d`'s brief asks for "the words your account needed", and the account gets
    written in the frame's words because the prompt is: *"MODE: survey — this
    area's code"*, *"what this area does"*.

    Measured on `cnt_k`: all three terminologist sessions on `.github` opened
    with *"This area appears to be a survey of the `.github` directory"* and
    then tried to define `survey` and `area`. The read gate refused them with
    "nothing you read this session says 'survey'" — true, and it reads as *read
    more*. So they read more, tried again, and the area was quarantined on the
    third attempt. `.github` has almost no project vocabulary; `none_found` was
    the right ending the whole time and nothing pointed at it.
    """
    for word in ("survey", "area", "mode"):
        with pytest.raises(ValueError) as exc:
            glossary_amend(Ctx(db, area=".github", read=[word, "template"]),
                           term=word, sense_body="what this session is doing",
                           sense_short="a look at one directory")
        msg = str(exc.value)
        assert "frame you were woken in" in msg, word
        assert "none_found" in msg, "and it names the ending that was available"


def test_a_real_word_that_happens_to_be_read_still_lands(db):
    """The list is the frame, not a banned-words list for the project."""
    ctx = Ctx(db, area="src/intents", read=["intent"])
    out = glossary_amend(ctx, term="intent",
                         sense_body="a recipe for a note, declared in frontmatter",
                         sense_short="a note-creation recipe")
    ctx.commit()
    assert out["id"] == "intent"


def test_a_wrong_id_is_told_which_ids_exist(db):
    """
    The old refusal named where the ids came from — "both ids come from the wake
    that woke you, spelled as they were given" — and a session that has already
    lost track of them cannot act on that.

    Measured on `cnt_k`: woken for `template, template#src_variables_providers`,
    three sessions called `glossary.same(drop='templatevariable',
    keep='intent#src_variables_providers')` — the wrong term, and an id that does
    not exist — identically each time. The collision was quarantined on the
    third.

    The open collisions are derivable at the point of refusal: two live rows
    sharing a term is what the predicate means by one.
    """
    from rota.roles.api import glossary_same

    a = Ctx(db, area="src/intents", read=["template"])
    glossary_amend(a, term="template", sense_body="a note used as a pattern",
                   sense_short="a note pattern")
    a.commit()
    b = Ctx(db, area="src/variables", read=["template"])
    glossary_amend(b, term="template", sense_body="the text a variable fills in",
                   sense_short="fillable text")
    b.commit()

    with pytest.raises(ValueError) as exc:
        glossary_same(Ctx(db), keep="intent#nowhere", drop="templatevariable",
                      why="both are patterns")
    msg = str(exc.value)
    assert "'template'" in msg, "it names the word that actually collides"
    assert "template#src_variables" in msg, "and the ids to use"


def test_a_plural_amends_the_singular(db):
    """
    The id derivation promises that writing a word twice amends it —
    "accidental duplication is impossible", earned on oauthlib where twelve
    sessions wrote `endpoint` five times. It was never true across a plural: the
    slug is not stemmed, while `_words_in` is.

    Measured on `cnt_l`: the session for `src/intents` — the area that declares
    what an Intent *is* — wrote `intents`, `templates` and `variables`, three
    new rows beside `intent`, `template` and `variable`, saying the same things
    about the same code. Three of the eight terms that run wrote which are not
    in the key at all are exactly these.
    """
    a = Ctx(db, area="src/intents", read=["intent"])
    glossary_amend(a, term="intent", sense_body="a recipe declared in frontmatter",
                   sense_short="a note-creation recipe")
    a.commit()

    b = Ctx(db, area="src/intents", read=["intent"])
    out = glossary_amend(b, term="intents", sense_body="custom actions in Obsidian",
                         sense_short="custom actions")
    b.commit()

    assert out["id"] == "intent", "the plural amends the row that exists"
    assert db.execute("SELECT COUNT(*) n FROM glossary_terms").fetchone()["n"] == 1


def test_a_plural_with_no_singular_is_its_own_word(db):
    """
    This declines to create a second row when the first exists. It does not rule
    that English plurals are never distinct — with nothing to amend, the word
    the session used is the word.
    """
    ctx = Ctx(db, read=["setting"])
    out = glossary_amend(ctx, term="settings", sense_body="the plugin's stored options",
                         sense_short="stored options")
    ctx.commit()
    assert out["id"] == "settings"


def test_one_session_cannot_split_a_word_across_its_own_writes(db):
    """Pending writes count, the same as everywhere else in this file."""
    ctx = Ctx(db, area="src/intents", read=["template"])
    glossary_amend(ctx, term="template", sense_body="a note used as a pattern",
                   sense_short="a note pattern")
    out = glossary_amend(ctx, term="templates",
                         sense_body="pre-defined note structures",
                         sense_short="note structures")
    ctx.commit()

    assert out["id"] == "template"
    assert db.execute("SELECT COUNT(*) n FROM glossary_terms "
                      "WHERE term LIKE 'template%'").fetchone()["n"] == 1


def test_the_plural_arriving_first_does_not_split_the_word(db):
    """
    The first version of this mapped plural onto singular and only that, so it
    depended on which spelling arrived first.

    Measured on `cnt_n`: the `src/intents` session wrote `variables` before
    `variable`. There was no `variable` row to amend, so both landed — same
    `sense_short`, "data types for storing values in intents", same area, same
    reading. The row that exists keeps its spelling whichever one it is; the
    second amends it.
    """
    a = Ctx(db, area="src/intents", read=["variable"])
    glossary_amend(a, term="variables", sense_body="values stored in intents",
                   sense_short="data types for storing values")
    a.commit()

    b = Ctx(db, area="src/intents", read=["variable"])
    out = glossary_amend(b, term="variable", sense_body="a value gathered from the user",
                         sense_short="a prompted value")
    b.commit()

    assert out["id"] == "variables", "first spelling to arrive keeps the row"
    assert db.execute("SELECT COUNT(*) n FROM glossary_terms").fetchone()["n"] == 1
    assert db.execute("SELECT sense_short FROM glossary_terms").fetchone()[
        "sense_short"] == "a prompted value", "and the later reading amends it"
