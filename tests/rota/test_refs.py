"""
The refs relation (frame 21): what a row rests on, and the provenance the
view derives from it.

Stage 1 is additive. Every writer stages a refs row beside the column or the
stamp it writes today, and the `provenance` view derives the same three
words from the rows. Stage 2 moves the readers: every gate and every result
reads the view or the relation, and the cascade wake carries row ids. The
columns stay until stage 3 and nothing reads them.
"""
from __future__ import annotations

import pytest

from rota.core.db import (ARTEFACT_OF_TABLE, SessionResult, Write, init_db,
                          session_commit, version_of)


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


# --- seeds ------------------------------------------------------------------

def _item(db, iid):
    db.execute("INSERT INTO items (id, text, kind, provenance) "
               "VALUES (?, 'x', 'in_scope', 'decided')", (iid,))


def _term(db, gid):
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES (?, ?, 'a sense', 'decided')", (gid, gid))


def _criterion(db, cid):
    db.execute("INSERT OR IGNORE INTO tickets (id, item_id, text) "
               "VALUES ('tk1', 'i1', 'a ticket')")
    db.execute("INSERT INTO criteria (id, ticket_id, text) "
               "VALUES (?, 'tk1', 'a criterion')", (cid,))


def _statement(db, sid, status):
    db.execute("INSERT OR IGNORE INTO entries (id, author, text, ts_order) "
               "VALUES ('e1', 'principal', 'words', 1)")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, "
               "text, status) VALUES (?, 'e1', 0, 5, 'words', ?)", (sid, status))


def _ruling(db, rid, status):
    db.execute("INSERT OR IGNORE INTO messages (id, thread_id, from_role, "
               "to_role, verb, seq, status) VALUES ('m_ask', 't1', 'liaison', "
               "'principal', 'present', 1, 'answered')")
    db.execute("INSERT INTO rulings (id, ask_id, status) VALUES (?, 'm_ask', ?)",
               (rid, status))


def _reference(db, rid):
    db.execute("INSERT INTO references_ (id, url, claim, asked_by) "
               "VALUES (?, 'https://example.test', 'a claim', 'architect')", (rid,))


def _ref(db, src_table, src_id, kind, target, resolves=1):
    db.execute("INSERT INTO refs (src_table, src_id, kind, target, resolves) "
               "VALUES (?, ?, ?, ?, ?)", (src_table, src_id, kind, target, resolves))


def _prov(db, view, rid):
    row = db.execute(f"SELECT provenance, basis FROM {view} WHERE id = ?",
                     (rid,)).fetchone()
    return (row["provenance"], row["basis"])


def _derived(db, src_table, src_id):
    row = db.execute("SELECT provenance, basis FROM provenance "
                     "WHERE src_table = ? AND src_id = ?",
                     (src_table, src_id)).fetchone()
    return (row["provenance"], row["basis"]) if row else ("reasoned", "none")


# --- the view ---------------------------------------------------------------

def test_the_view_returns_the_three_words_from_three_seeded_refs(db):
    """A landed ruling gives decided. A grain gives observed. No ref gives
    reasoned. The basis says which source did it."""
    for iid in ("i_ruled", "i_found", "i_bare"):
        _item(db, iid)
    _ruling(db, "r1", "landed")
    _ref(db, "items", "i_ruled", "ruling", "r1")
    _ref(db, "items", "i_found", "grain", "src/app.py")

    assert _prov(db, "item_provenance", "i_ruled") == ("decided", "ruling")
    assert _prov(db, "item_provenance", "i_found") == ("observed", "code")
    assert _prov(db, "item_provenance", "i_bare") == ("reasoned", "none")


def test_every_owner_table_has_a_view(db):
    db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
               "VALUES ('g1', 'tip', 'x', 'observed')")
    db.execute("INSERT INTO constraints (id, headline, provenance) "
               "VALUES ('k1', 'x', 'observed')")
    db.execute("INSERT INTO model_areas (id, account) VALUES ('src', 'x')")
    db.execute("INSERT INTO frame_rulings (id, kind, provenance) "
               "VALUES ('src', 'program', 'observed')")
    for view, rid in (("term_provenance", "g1"), ("constraint_provenance", "k1"),
                      ("area_provenance", "src"), ("frame_provenance", "src")):
        assert _prov(db, view, rid) == ("reasoned", "none"), view


def test_precedence_is_decided_over_observed_over_reasoned(db):
    """The rule of section H2. A ruling outranks a statement, a statement
    outranks the world, the world outranks the code, and a grain that no
    longer resolves is no basis at all."""
    for iid in ("i_all", "i_cited", "i_world", "i_gone"):
        _item(db, iid)
    _ruling(db, "r1", "landed")
    _statement(db, "s1", "ratified")
    _reference(db, "ref1")

    _ref(db, "items", "i_all", "ruling", "r1")
    _ref(db, "items", "i_all", "statement", "s1")
    _ref(db, "items", "i_all", "reference", "ref1")
    _ref(db, "items", "i_all", "grain", "src/app.py")
    assert _prov(db, "item_provenance", "i_all") == ("decided", "ruling")

    _ref(db, "items", "i_cited", "statement", "s1")
    _ref(db, "items", "i_cited", "reference", "ref1")
    assert _prov(db, "item_provenance", "i_cited") == ("decided", "statement")

    _ref(db, "items", "i_world", "reference", "ref1")
    _ref(db, "items", "i_world", "grain", "src/app.py")
    assert _prov(db, "item_provenance", "i_world") == ("observed", "world")

    _ref(db, "items", "i_gone", "grain", "src/gone.py", resolves=0)
    assert _prov(db, "item_provenance", "i_gone") == ("reasoned", "none")


def test_a_ruling_that_is_not_landed_decides_nothing(db):
    _item(db, "i1")
    _ruling(db, "r_open", "open")
    _ref(db, "items", "i1", "ruling", "r_open")
    assert _prov(db, "item_provenance", "i1") == ("reasoned", "none")


def test_a_criterion_reaches_the_statement_through_its_term(db):
    """Two hops: the criterion rests on a term, the term on a statement."""
    _item(db, "i1")
    _term(db, "g1")
    _criterion(db, "c1")
    _statement(db, "s1", "ratified")
    _ref(db, "criteria", "c1", "term", "g1")
    _ref(db, "glossary_terms", "g1", "statement", "s1")

    assert _derived(db, "criteria", "c1") == ("decided", "statement")
    assert _prov(db, "term_provenance", "g1") == ("decided", "statement")


def test_a_statement_that_leaves_ratified_drops_the_rows_that_cite_it(db):
    """The cascade is the relation: nothing is rewritten, the next read says
    reasoned. Through a term too."""
    _item(db, "i1")
    _term(db, "g1")
    _criterion(db, "c1")
    _statement(db, "s1", "ratified")
    _ref(db, "items", "i1", "statement", "s1")
    _ref(db, "glossary_terms", "g1", "statement", "s1")
    _ref(db, "criteria", "c1", "term", "g1")
    assert _prov(db, "item_provenance", "i1") == ("decided", "statement")
    assert _derived(db, "criteria", "c1") == ("decided", "statement")

    db.execute("UPDATE statements SET status = 'superseded' WHERE id = 's1'")

    assert _prov(db, "item_provenance", "i1") == ("reasoned", "none")
    assert _prov(db, "term_provenance", "g1") == ("reasoned", "none")
    assert _derived(db, "criteria", "c1") == ("reasoned", "none")


# --- law 1 on one table -----------------------------------------------------

def _refs_write(src_table, src_id, kind, target):
    return Write("refs", f"{src_table}:{src_id}:{kind}:{target}", {
        "src_table": src_table, "src_id": src_id, "kind": kind,
        "target": target, "resolves": 1})


def test_a_refs_write_is_receipted_under_the_source_artefact(db):
    """Q7: the receipt names the source row, so the cascade sees the source
    artefact and never the relation."""
    from rota.core.scheduler import cascade_wakes

    _item(db, "i1")
    _statement(db, "s1", "ratified")
    session_commit(db, SessionResult(
        session_id="s_refs", role="vision_keeper",
        writes=[_refs_write("items", "i1", "statement", "s1")]))

    receipts = [(r["table_name"], r["row_id"]) for r in db.execute(
        "SELECT table_name, row_id FROM receipts WHERE session_id = 's_refs'")]
    assert receipts == [("items", "i1")]
    assert ARTEFACT_OF_TABLE[receipts[0][0]] == "problem"
    assert db.execute("SELECT 1 FROM refs WHERE src_table = 'items' "
                      "AND src_id = 'i1' AND kind = 'statement' "
                      "AND target = 's1'").fetchone()

    # The same wakes as a write to the item itself.
    session_commit(db, SessionResult(
        session_id="s_item", role="vision_keeper",
        writes=[Write("items", "i1", {"text": "y"})]))
    by_refs = [(w.role, w.refs) for w in cascade_wakes(db, "s_refs")]
    by_row = [(w.role, w.refs) for w in cascade_wakes(db, "s_item")]
    assert by_refs and by_refs == by_row


def test_a_refs_write_beside_the_row_bumps_the_version_once(db):
    _statement(db, "s1", "ratified")
    session_commit(db, SessionResult(
        session_id="s1", role="vision_keeper",
        writes=[Write("items", "i1", {"text": "x", "kind": "in_scope",
                                      "provenance": "decided"}),
                _refs_write("items", "i1", "statement", "s1")]))
    assert version_of(db, "items") == 1
    receipts = db.execute("SELECT table_name, row_id, new_version FROM receipts "
                          "WHERE session_id = 's1'").fetchall()
    assert [(r["table_name"], r["row_id"], r["new_version"])
            for r in receipts] == [("items", "i1", 1)]
    assert version_of(db, "refs") == 0, "the relation carries no version of its own"


# --- the writers ------------------------------------------------------------

def test_problem_assert_writes_a_statement_ref_beside_item_statements(db):
    from rota.core.sandbox import build
    from rota.core.scheduler import Wake

    _statement(db, "s1", "ratified")
    sb = build("vision_keeper", db, mode="deliver",
               wake=Wake(role="vision_keeper", kind="message", refs=("s1",)))
    sb.call("problem.assert", id="i1", text="users can export invoices",
            kind="in_scope")
    staged = [(t, i) for t, i, *_ in sb.ctx.writes]
    assert ("item_statements", "i1:s1") in staged
    assert ("refs", "items:i1:statement:s1") in staged
    assert staged.index(("items", "i1")) < staged.index(("refs", "items:i1:statement:s1"))


def test_an_onboarding_wake_records_the_grains_it_opened(db):
    from rota.core.sandbox import build

    sb = build("vision_keeper", db, mode="survey", provenance="observed",
               onboarding=True)
    sb.ctx.opened.update({"src/b.py", "src/a.py"})
    sb.call("problem.assert", id="i1", text="the program reads two numbers",
            kind="in_scope")
    grains = [w[2]["target"] for w in sb.ctx.writes
              if w[0] == "refs" and w[2]["kind"] == "grain"]
    assert grains == ["src/a.py", "src/b.py"]

    plain = build("vision_keeper", db, mode="deliver")
    plain.ctx.opened.add("src/a.py")
    plain.call("problem.assert", id="i2", text="users can export invoices",
               kind="in_scope")
    assert not [w for w in plain.ctx.writes if w[0] == "refs"], \
        "a delivery wake records no grain: the row is reasoned, not observed"


def test_the_advertised_signatures_are_unchanged(db):
    """The signature of every offered tool is in the prompt, and the prompt
    keys the recordings. A new parameter on `problem.assert` or
    `glossary.amend` waits for the re-record (Q11)."""
    from rota.core.sandbox import build

    vk = build("vision_keeper", db, mode="deliver")
    te = build("terminologist", db, mode="deliver")
    sigs = vk.signatures() + te.signatures()
    assert any(s.startswith("problem.assert(id, text, kind='in_scope')") for s in sigs), sigs
    assert not any("source_refs" in s and s.startswith(("problem.assert", "glossary.amend"))
                   for s in sigs), sigs


def test_criteria_write_term_refs_to_the_relation(db):
    from rota.core.sandbox import build

    _item(db, "i1")
    _term(db, "g1")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('tk1', 'i1', 'x')")
    sb = build("terminologist", db, mode="criteria")
    sb.call("criteria.specify", id="c1", ticket_id="tk1", text="it works",
            term_refs=["g1"], surface_refs=["run"])
    assert ("refs", "criteria:c1:term:g1") in [(t, i) for t, i, *_ in sb.ctx.writes]


def test_the_cite_door_stages_a_ref_for_a_row_of_its_artefact(db):
    """The graph's `cite` edges are `actor: system`: a door the system
    stages through, offered to no session."""
    from rota.core.sandbox import build
    from rota.roles import api

    _item(db, "i1")
    sb = build("vision_keeper", db, mode="deliver")
    assert "cite" not in (sb.functions() if callable(getattr(sb, "functions", None))
                          else []), "no session is offered the door"
    cite = api.REGISTRY[("problem", "cite")]
    cite(sb.ctx, id="i1", kind="statement", target="s1")
    assert sb.ctx.writes == [("refs", "items:i1:statement:s1", {
        "src_table": "items", "src_id": "i1", "kind": "statement",
        "target": "s1", "resolves": 1})]
    with pytest.raises(ValueError, match="not a row of problem"):
        cite(sb.ctx, id="nope", kind="statement", target="s1")
    with pytest.raises(ValueError, match="kind is one of"):
        cite(sb.ctx, id="i1", kind="wish", target="s1")
    # The schema carries no CHECK for the two columns; the door holds it.
    with pytest.raises(ValueError, match="not a table that carries refs"):
        api.stage_ref(sb.ctx, "tickets", "tk1", "term", "g1")


def test_the_seat_verdict_lands_a_ruling_row_for_the_ref_to_target(db):
    """Q8: a verdict that comes straight from the seat has no Liaison row,
    so the door writes one, landed."""
    from rota.roles.principal import Answer, Ask, land

    _item(db, "i1")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m_ask', 't1', 'liaison', "
               "'principal', 'present', '[\"i1\"]', 1, 'open')")
    mid = land(db, Ask(message_id="m_ask", verb="present", refs=["i1"]),
               Answer(verb="verdict", per_item={"i1": "approve"}))
    assert mid
    row = db.execute("SELECT id, ask_id, status, verdict_id FROM rulings").fetchone()
    assert (row["ask_id"], row["status"], row["verdict_id"]) == ("m_ask", "landed", mid)


# --- the fixture loader -----------------------------------------------------

def test_the_loader_seeds_refs_beside_the_columns(db):
    """Q9: `provenance:`, `source_refs:`, `term_refs:` and `item_statements:`
    seeds become refs rows. The case files do not change."""
    from rota.testkit.fixtures import FIXTURE_RULING, seed

    seed(db, {
        "entries": [{"id": "e1", "author": "principal", "text": "w", "ts_order": 1}],
        "statements": [{"id": "s1", "span_entry": "e1", "span_start": 0,
                        "span_end": 1, "text": "w", "status": "ratified"}],
        "items": [
            {"id": "i1", "text": "a", "kind": "in_scope", "provenance": "decided"},
            {"id": "i2", "text": "b", "kind": "in_scope", "provenance": "observed"}],
        "item_statements": [{"item_id": "i1", "statement_id": "s1"}],
        "glossary_terms": [{"id": "g1", "term": "tip", "sense_short": "x",
                            "provenance": "observed", "source_refs": '["s1"]'}],
        "tickets": [{"id": "tk1", "item_id": "i1", "text": "t"}],
        "criteria": [{"id": "c1", "ticket_id": "tk1", "text": "c",
                      "term_refs": ["g1"]}],
    })
    rows = {(r["src_table"], r["src_id"], r["kind"], r["target"])
            for r in db.execute("SELECT * FROM refs")}
    assert ("items", "i1", "ruling", FIXTURE_RULING) in rows
    assert ("items", "i1", "statement", "s1") in rows
    assert ("items", "i2", "grain", "@fixture") in rows
    assert ("glossary_terms", "g1", "grain", "@fixture") in rows
    assert ("glossary_terms", "g1", "statement", "s1") in rows
    assert ("criteria", "c1", "term", "g1") in rows

    assert _prov(db, "item_provenance", "i1") == ("decided", "ruling")
    assert _prov(db, "item_provenance", "i2") == ("observed", "code")
    assert db.execute("SELECT status FROM rulings WHERE id = ?",
                      (FIXTURE_RULING,)).fetchone()["status"] == "landed"


def test_the_loader_seeds_nothing_for_a_fixture_with_no_refs(db):
    from rota.testkit.fixtures import seed

    seed(db, {"entries": [{"id": "e1", "author": "principal", "text": "w",
                           "ts_order": 1}]})
    assert db.execute("SELECT COUNT(*) n FROM refs").fetchone()["n"] == 0
    assert db.execute("SELECT COUNT(*) n FROM messages").fetchone()["n"] == 0


# --- the readers (stage 2) --------------------------------------------------

def test_the_cascade_wake_carries_the_row_ids_from_the_relation(db):
    """Section H3: an amended statement wakes the owners of the rows that
    rest on it. The item and the term through their `statement` refs, the
    criterion one hop on through its `term` ref. An artefact the graph
    reaches with no row in the relation gets a wake with no refs."""
    from rota.core.scheduler import cascade_wakes

    _statement(db, "s1", "ratified")
    _item(db, "i1")
    _item(db, "i_other")
    _term(db, "g1")
    _criterion(db, "c1")
    _ref(db, "items", "i1", "statement", "s1")
    _ref(db, "glossary_terms", "g1", "statement", "s1")
    _ref(db, "criteria", "c1", "term", "g1")

    session_commit(db, SessionResult(
        session_id="s_amend", role="liaison",
        writes=[Write("statements", "s1", {
            "span_entry": "e1", "span_start": 0, "span_end": 5,
            "text": "other words", "status": "ratified"})]))
    wakes = cascade_wakes(db, "s_amend")

    named = sorted(w.refs for w in wakes if w.refs)
    assert named == [("c1",), ("g1",), ("i1",)], wakes
    assert all(w.kind == "cascade" for w in wakes)
    assert not any("s1" in w.refs or "i_other" in w.refs for w in wakes)
    by_refs = {w.refs: w.role for w in wakes if w.refs}
    assert by_refs == {("i1",): "vision_keeper", ("g1",): "terminologist",
                       ("c1",): "terminologist"}
    # The wake for an artefact the relation names nothing in carries nothing.
    assert any(w.role == "architect" and w.refs == () for w in wakes)


def test_found_never_overwrites_a_row_decided_by_a_ruling_ref_alone(db):
    """The guard at `problem.assert` reads the view. The stamp says observed,
    the ruling ref says decided, and the ruling wins."""
    from rota.core.sandbox import build

    db.execute("INSERT INTO items (id, text, kind, provenance) "
               "VALUES ('i1', 'the bill is split', 'in_scope', 'observed')")
    _ruling(db, "r1", "landed")
    _ref(db, "items", "i1", "ruling", "r1")
    assert _prov(db, "item_provenance", "i1") == ("decided", "ruling")

    sb = build("vision_keeper", db, mode="survey", provenance="observed",
               onboarding=True)
    got = sb.call("problem.assert", id="i1", text="the program splits the bill",
                  kind="in_scope")
    assert "decided" in got.get("note", ""), got
    assert not [w for w in sb.ctx.writes if w[0] == "items"], \
        "an observation wrote over a decided row"


def test_the_same_words_on_a_row_observed_by_a_grain_ref_alone_are_refused(db):
    """The other guard at `problem.assert`. The stamp says decided, the grain
    ref says observed, and a decided wake that repeats the words is refused."""
    from rota.core.sandbox import build

    text = "the toolkit parses a command into arguments and options"
    db.execute("INSERT INTO items (id, text, kind, provenance) "
               "VALUES ('parses', ?, 'in_scope', 'decided')", (text,))
    _ref(db, "items", "parses", "grain", "src/parser.py")
    assert _prov(db, "item_provenance", "parses") == ("observed", "code")

    sb = build("vision_keeper", db, mode="deliver")
    with pytest.raises(ValueError, match="observed row"):
        sb.call("problem.assert", id="parses", text=text, kind="in_scope")


def test_tick_slicing_refuses_an_item_observed_by_a_grain_ref_alone(db):
    """The slicing predicate reads the view. The stamp says decided, the
    grain ref says observed, and an observed item is a record, not a build
    order. The item the ruling ref decides is sliced, whatever its stamp."""
    from rota.core.scheduler import tick_slicing

    for iid, stamp in (("seen", "decided"), ("asked", "observed")):
        db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
                   "approval_ver, version) VALUES (?, 'x', 'in_scope', ?, "
                   "'approved', 1, 1)", (iid, stamp))
    _ruling(db, "r1", "landed")
    _ref(db, "items", "seen", "grain", "src/app.py")
    _ref(db, "items", "asked", "ruling", "r1")

    assert [w.refs for w in tick_slicing(db)] == [("asked",)]


def test_observed_entries_presents_the_code_and_not_the_world(db):
    """Q4: `observed_entries` drains `basis = 'code'` only. A row that rests
    on a reference is cited, and a cited row was never put to the
    principal. A row with no refs is reasoned and is not observed."""
    from rota.core.predicates import observed_entries

    _reference(db, "ref1")
    for gid in ("g_code", "g_world", "g_bare"):
        db.execute("INSERT INTO glossary_terms (id, term, sense_short, provenance) "
                   "VALUES (?, ?, 'a sense', 'observed')", (gid, gid))
    db.execute("INSERT INTO constraints (id, headline, provenance) "
               "VALUES ('k_world', 'x', 'cited')")
    _ref(db, "glossary_terms", "g_code", "grain", "src/app.py")
    _ref(db, "glossary_terms", "g_world", "reference", "ref1")
    _ref(db, "constraints", "k_world", "reference", "ref1")
    assert _prov(db, "term_provenance", "g_world") == ("observed", "world")

    wakes = observed_entries(db)
    assert [(w.role, w.kind, w.refs) for w in wakes] == \
        [("liaison", "tick:observed_entries", ("g_code",))]
