"""
The refs relation (frame 21): what a row rests on, and the provenance the
view derives from it.

Every writer stages the refs rows its row rests on, and the `provenance`
view derives the three words from the rows. Every gate and every result
reads the view or the relation, and the cascade wake carries row ids. No
owner table carries a provenance column, a JSON ref column, or the old
`item_statements` table: the relation is the one record.
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
    db.execute("INSERT INTO items (id, text, kind) "
               "VALUES (?, 'x', 'in_scope')", (iid,))


def _term(db, gid):
    db.execute("INSERT INTO glossary_terms (id, term, sense_short) "
               "VALUES (?, ?, 'a sense')", (gid, gid))


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
    db.execute("INSERT INTO glossary_terms (id, term, sense_short) "
               "VALUES ('g1', 'tip', 'x')")
    db.execute("INSERT INTO constraints (id, headline) VALUES ('k1', 'x')")
    db.execute("INSERT INTO model_areas (id, account) VALUES ('src', 'x')")
    db.execute("INSERT INTO frame_rulings (id, kind) VALUES ('src', 'program')")
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
        writes=[Write("items", "i1", {"text": "x", "kind": "in_scope"}),
                _refs_write("items", "i1", "statement", "s1")]))
    assert version_of(db, "items") == 1
    receipts = db.execute("SELECT table_name, row_id, new_version FROM receipts "
                          "WHERE session_id = 's1'").fetchall()
    assert [(r["table_name"], r["row_id"], r["new_version"])
            for r in receipts] == [("items", "i1", 1)]
    assert version_of(db, "refs") == 0, "the relation carries no version of its own"


def test_a_refs_write_staged_before_its_row_bumps_the_version_once(db):
    """One bump per receipt key per commit, in any order of the writes."""
    _statement(db, "s1", "ratified")
    session_commit(db, SessionResult(
        session_id="s1", role="vision_keeper",
        writes=[_refs_write("items", "i1", "statement", "s1"),
                Write("items", "i1", {"text": "x", "kind": "in_scope"})]))
    assert version_of(db, "items") == 1
    receipts = db.execute("SELECT table_name, row_id, new_version FROM receipts "
                          "WHERE session_id = 's1'").fetchall()
    assert [(r["table_name"], r["row_id"], r["new_version"])
            for r in receipts] == [("items", "i1", 1)]


def test_the_same_refs_row_again_is_not_a_change(db):
    """A refs write whose row is on file, `resolves` and all, moves no
    version, writes no receipt and keeps the row's rowid. A write that
    flips `resolves` is a change, and the row keeps its rowid."""
    _item(db, "i1")
    _statement(db, "s1", "ratified")
    session_commit(db, SessionResult(
        session_id="s_first", role="vision_keeper",
        writes=[_refs_write("items", "i1", "statement", "s1")]))
    rowid = db.execute("SELECT rowid FROM refs").fetchone()[0]
    assert version_of(db, "items") == 1

    session_commit(db, SessionResult(
        session_id="s_again", role="vision_keeper",
        writes=[_refs_write("items", "i1", "statement", "s1")]))
    assert version_of(db, "items") == 1
    assert db.execute("SELECT COUNT(*) n FROM receipts "
                      "WHERE session_id = 's_again'").fetchone()["n"] == 0
    assert db.execute("SELECT rowid FROM refs").fetchone()[0] == rowid

    flipped = _refs_write("items", "i1", "statement", "s1")
    flipped.values["resolves"] = 0
    session_commit(db, SessionResult(
        session_id="s_flip", role="vision_keeper", writes=[flipped]))
    assert version_of(db, "items") == 2
    assert [(r["table_name"], r["row_id"]) for r in db.execute(
        "SELECT table_name, row_id FROM receipts WHERE session_id = 's_flip'")] \
        == [("items", "i1")]
    row = db.execute("SELECT rowid, resolves FROM refs").fetchone()
    assert (row[0], row["resolves"]) == (rowid, 0)


# --- the writers ------------------------------------------------------------

def test_problem_assert_writes_a_statement_ref_after_the_item(db):
    """The item's write carries no stamp and no junction row: the statement
    ref, staged after the item so the receipt lands under it, is the one
    record of what the item reads."""
    from rota.core.sandbox import build
    from rota.core.scheduler import Wake

    _statement(db, "s1", "ratified")
    sb = build("vision_keeper", db, mode="deliver",
               wake=Wake(role="vision_keeper", kind="message", refs=("s1",)))
    sb.call("problem.assert", id="i1", text="users can export invoices",
            kind="in_scope")
    staged = [(t, i) for t, i, *_ in sb.ctx.writes]
    assert staged == [("items", "i1"), ("refs", "items:i1:statement:s1")]
    item = next(w[2] for w in sb.ctx.writes if w[0] == "items")
    assert item == {"text": "users can export invoices", "kind": "in_scope",
                    "approval": "draft"}


def test_an_onboarding_wake_records_the_grains_it_opened(db):
    from rota.core.sandbox import build

    sb = build("vision_keeper", db, mode="survey", onboarding=True)
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
    _statement(db, "s1", "ratified")
    sb = build("vision_keeper", db, mode="deliver")
    assert not any(name.endswith(".cite") for name in sb.functions()), \
        "no session is offered the door"
    cite = api.REGISTRY[("problem", "cite")]
    cite(sb.ctx, id="i1", kind="statement", target="s1")
    assert sb.ctx.writes == [("refs", "items:i1:statement:s1", {
        "src_table": "items", "src_id": "i1", "kind": "statement",
        "target": "s1", "resolves": 1})]
    with pytest.raises(ValueError, match="not a row of problem"):
        cite(sb.ctx, id="nope", kind="statement", target="s1")
    with pytest.raises(ValueError, match="kind is one of"):
        cite(sb.ctx, id="i1", kind="wish", target="s1")
    # The target names a row of its kind, as the owner ops check.
    with pytest.raises(ValueError, match="names no statement: a statement ref "
                                         "targets a row of statements"):
        cite(sb.ctx, id="i1", kind="statement", target="s_none")
    with pytest.raises(ValueError, match="names no grain: a grain ref targets "
                                         "a grain of the index"):
        cite(sb.ctx, id="i1", kind="grain", target="src/nowhere.py")
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


def test_the_seat_verdict_lands_the_liaisons_open_row_and_writes_no_second(db):
    """A verdict from the seat on an ask the Liaison has read lands the
    Liaison's own row. `apply_rulings` then finds no open row: the ask ends
    with one landed row, and no `r_<msg>` beside it."""
    from rota.roles.principal import Answer, Ask, apply_rulings, land

    _item(db, "i1")
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m_ask', 't1', 'liaison', "
               "'principal', 'present', '[\"i1\"]', 1, 'open')")
    db.execute("INSERT INTO rulings (id, ask_id, per_item, words) "
               "VALUES ('r_li', 'm_ask', '{\"i1\": \"approve\"}', 'ok')")
    mid = land(db, Ask(message_id="m_ask", verb="present", refs=["i1"]),
               Answer(verb="verdict", per_item={"i1": "approve"}))
    assert mid
    assert apply_rulings(db) == []
    rows = db.execute("SELECT id, status, verdict_id FROM rulings").fetchall()
    assert [(r["id"], r["status"], r["verdict_id"]) for r in rows] == \
        [("r_li", "landed", mid)]


# --- the fixture loader -----------------------------------------------------

def test_the_loader_seeds_refs_in_place_of_the_columns(db):
    """Q9: `provenance:`, `source_refs:`, `term_refs:` and `item_statements:`
    seeds become refs rows, and the INSERT leaves the seeds out. The case
    files do not change."""
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


def test_the_seeded_ruling_is_a_record_the_audit_accepts(db):
    """A seeded `decided` row rests on the fixture ruling. The ruling's ask
    is answered and the verdict that answers it is on file, so the audit
    finds nothing. Nothing seeded is open."""
    from rota.testkit.fixtures import FIXTURE_ASK, FIXTURE_VERDICT, seed
    from rota.tools.audit import audit

    seed(db, {"items": [{"id": "i1", "text": "a", "kind": "in_scope",
                         "provenance": "decided"}]})
    assert audit(db) == []
    rows = db.execute("SELECT id, cause_id, status, to_role FROM messages "
                      "ORDER BY id").fetchall()
    assert [(r["id"], r["cause_id"], r["status"], r["to_role"]) for r in rows] == [
        (FIXTURE_ASK, None, "answered", "liaison"),
        (FIXTURE_VERDICT, FIXTURE_ASK, "answered", "liaison")]
    assert db.execute("SELECT verdict_id FROM rulings").fetchone()["verdict_id"] \
        == FIXTURE_VERDICT


# --- the readers (stage 2) --------------------------------------------------

def test_the_cascade_wake_carries_the_row_ids_from_the_relation(db):
    """Section H3: an amended statement wakes the owners of the rows that
    rest on it. The item and the term through their `statement` refs, the
    criterion one hop on through its `term` ref. A wake names its artefact
    first. An artefact the graph reaches with no row in the relation gets
    a wake that names the artefact alone."""
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

    named = sorted(w.refs for w in wakes if len(w.refs) > 1)
    assert named == [("criteria", "c1"), ("glossary", "g1"), ("problem", "i1")], wakes
    assert all(w.kind == "cascade" for w in wakes)
    assert not any("s1" in w.refs or "i_other" in w.refs for w in wakes)
    by_refs = {w.refs: w.role for w in wakes if len(w.refs) > 1}
    assert by_refs == {("problem", "i1"): "vision_keeper",
                       ("glossary", "g1"): "terminologist",
                       ("criteria", "c1"): "terminologist"}
    # The wake for an artefact the relation names nothing in carries the
    # artefact alone.
    assert any(w.role == "architect" and w.refs == ("model",) for w in wakes)


def test_found_never_overwrites_a_row_decided_by_a_ruling_ref_alone(db):
    """The guard at `problem.assert` reads the view. The ruling ref says
    decided, and an onboarding wake does not amend the row."""
    from rota.core.sandbox import build

    db.execute("INSERT INTO items (id, text, kind) "
               "VALUES ('i1', 'the bill is split', 'in_scope')")
    _ruling(db, "r1", "landed")
    _ref(db, "items", "i1", "ruling", "r1")
    assert _prov(db, "item_provenance", "i1") == ("decided", "ruling")

    sb = build("vision_keeper", db, mode="survey", onboarding=True)
    got = sb.call("problem.assert", id="i1", text="the program splits the bill",
                  kind="in_scope")
    assert "decided" in got.get("note", ""), got
    assert not [w for w in sb.ctx.writes if w[0] == "items"], \
        "an observation wrote over a decided row"


def test_the_same_words_on_a_row_observed_by_a_grain_ref_alone_are_refused(db):
    """The other guard at `problem.assert`. The grain ref says observed,
    and a delivery wake that repeats the words is refused."""
    from rota.core.sandbox import build

    text = "the toolkit parses a command into arguments and options"
    db.execute("INSERT INTO items (id, text, kind) "
               "VALUES ('parses', ?, 'in_scope')", (text,))
    _ref(db, "items", "parses", "grain", "src/parser.py")
    assert _prov(db, "item_provenance", "parses") == ("observed", "code")

    sb = build("vision_keeper", db, mode="deliver")
    with pytest.raises(ValueError, match="observed row"):
        sb.call("problem.assert", id="parses", text=text, kind="in_scope")


def test_tick_slicing_refuses_an_item_observed_by_a_grain_ref_alone(db):
    """The slicing predicate reads the view. The grain ref says observed,
    and an observed item is a record, not a build order. The item the
    ruling ref decides is sliced."""
    from rota.core.scheduler import tick_slicing

    for iid in ("seen", "asked"):
        db.execute("INSERT INTO items (id, text, kind, approval, "
                   "approval_ver, version) VALUES (?, 'x', 'in_scope', "
                   "'approved', 1, 1)", (iid,))
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
        _term(db, gid)
    db.execute("INSERT INTO constraints (id, headline) VALUES ('k_world', 'x')")
    _ref(db, "glossary_terms", "g_code", "grain", "src/app.py")
    _ref(db, "glossary_terms", "g_world", "reference", "ref1")
    _ref(db, "constraints", "k_world", "reference", "ref1")
    assert _prov(db, "term_provenance", "g_world") == ("observed", "world")

    wakes = observed_entries(db)
    assert [(w.role, w.kind, w.refs) for w in wakes] == \
        [("liaison", "tick:observed_entries", ("g_code",))]


# --- the writers (stage 3a) -------------------------------------------------

def _commit_sandbox(db, sb, session_id):
    """Land a sandbox's staged writes the way the runner does."""
    from rota.core.runner import _as_write

    session_commit(db, SessionResult(
        session_id=session_id, role=sb.ctx.role,
        writes=[_as_write(w) for w in sb.ctx.writes]))


def _deliver(db, to_role, refs, mid="m_deliver"):
    """A Liaison `deliver` message that names `refs`. A message wake
    carries its subject on the message, not on the wake."""
    import json

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES (?, 't1', 'liaison', ?, "
               "'deliver', ?, 1, 'open')", (mid, to_role, json.dumps(refs)))
    return mid


def _woken_by(role, db, mode, mid):
    """A sandbox for `role`, woken by message `mid`, as the runner wakes it."""
    from rota.core.sandbox import build
    from rota.core.scheduler import Wake

    sb = build(role, db, mode=mode,
               wake=Wake(role=role, kind="message", message_id=mid))
    sb.ctx.trigger = mid
    return sb


def test_a_delivery_wake_that_names_a_ratified_statement_writes_a_decided_term(db):
    """Stage 2 review, finding 1. `glossary.amend` on a wake that names a
    ratified statement stages a `statement` ref, and the term derives
    decided. The same write on a wake that names no statement derives
    reasoned: decided cascades from a ratified statement along the refs."""
    from rota.core.sandbox import build

    _statement(db, "s1", "ratified")
    sb = _woken_by("terminologist", db, "deliver",
                   _deliver(db, "terminologist", ["s1"]))
    sb.call("glossary.amend", term="account",
            sense_body="the customer's billing account",
            sense_short="a billing account")
    assert ("refs", "glossary_terms:account:statement:s1") in \
        [(t, i) for t, i, *_ in sb.ctx.writes]
    _commit_sandbox(db, sb, "s_te")
    assert _prov(db, "term_provenance", "account") == ("decided", "statement")

    bare = build("terminologist", db, mode="deliver")
    bare.call("glossary.amend", term="invoice",
              sense_body="the bill the program sends", sense_short="a bill")
    assert not [w for w in bare.ctx.writes if w[0] == "refs"]
    _commit_sandbox(db, bare, "s_te2")
    assert _prov(db, "term_provenance", "invoice") == ("reasoned", "none")


def test_a_delivery_wake_that_names_a_ratified_statement_writes_a_decided_constraint(db):
    """The same rule at `model.amend`."""
    _statement(db, "s1", "ratified")
    sb = _woken_by("architect", db, "deliver", _deliver(db, "architect", ["s1"]))
    out = sb.call("model.amend",
                  headline="closing an account keeps the billing account",
                  text="the billing account outlives the user account, and "
                       "finance reads it")
    _commit_sandbox(db, sb, "s_ar")
    assert _prov(db, "constraint_provenance", out["id"]) == ("decided", "statement")


def _old_database(path):
    """A run database from before the refs relation: the owner tables with
    their provenance columns, no `refs`, no marker."""
    import sqlite3
    import subprocess

    from rota import paths

    old_sql = subprocess.run(
        ["git", "show", "ac1b83e~1:rota/core/schema.sql"], cwd=paths.REPO,
        capture_output=True, text=True, check=True).stdout
    raw = sqlite3.connect(path)
    raw.executescript(old_sql)
    raw.close()
    return path


def test_a_run_database_from_before_the_refs_relation_is_refused(tmp_path):
    """Stage 2 review, finding 2. A database with the owner tables and no
    schema marker opened with an empty relation, and every gate read
    reasoned. `init_db` refuses it with one sentence, `rota ls` shows the
    same sentence, and a fresh database opens and carries the marker. A
    database that carries the marker and a provenance column, from the
    stages that wrote the column beside the relation, is refused too."""
    from rota import cli

    old = _old_database(tmp_path / "old.db")
    with pytest.raises(RuntimeError, match="predates the refs relation"):
        init_db(old)
    assert "predates the refs relation" in cli._read(old, ask_git=False)["error"]

    fresh = tmp_path / "fresh.db"
    conn = init_db(fresh)
    assert conn.execute("SELECT value FROM config WHERE key = 'schema'"
                        ).fetchone()["value"] == "refs"
    conn.close()
    init_db(fresh).close()          # the same run, opened again

    marked = tmp_path / "marked.db"
    conn = init_db(marked)
    conn.execute("ALTER TABLE items ADD COLUMN provenance TEXT")
    conn.close()
    with pytest.raises(RuntimeError, match="predates the refs relation"):
        init_db(marked)


def test_a_viewer_opens_an_old_run_read_only_with_the_sentence(tmp_path):
    """The cockpit is how an old night run is read. `open_for_viewing`
    gives a read-only connection and the sentence as the note, and the
    server's drift carries the sentence instead of raising. A current run
    opens as `init_db` opens it, with no note. Only a run refuses."""
    import sqlite3

    from rota.cockpit import server
    from rota.core.db import open_for_viewing

    old = _old_database(tmp_path / "old.db")
    conn, note = open_for_viewing(old)
    assert "predates the refs relation" in note
    with pytest.raises(sqlite3.OperationalError):
        conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                     "VALUES ('e1', 'principal', 'x', 1)")
    conn.close()
    assert any("predates the refs relation" in d for d in server._bring_up(old))

    conn, note = open_for_viewing(tmp_path / "fresh.db")
    assert note is None
    conn.execute("INSERT INTO entries (id, author, text, ts_order) "
                 "VALUES ('e1', 'principal', 'x', 1)")
    conn.close()


def test_state_json_answers_for_an_old_run_with_the_sentence(tmp_path):
    """The cockpit's `/state.json` on a run from before the refs relation.
    The predicates read the provenance views, an old run has none, and
    `snapshot` answered 500. Served read-only, the page answers with an
    empty frontier and the sentence in `stale` and in `drift`, which the
    header wears."""
    import json
    import sqlite3
    import subprocess
    import threading
    from http.server import ThreadingHTTPServer
    from urllib.request import urlopen

    from rota import paths
    from rota.cockpit import server

    old = tmp_path / "old.db"
    old_sql = subprocess.run(
        ["git", "show", "e63762c:rota/core/schema.sql"], cwd=paths.REPO,
        capture_output=True, text=True, check=True).stdout
    raw = sqlite3.connect(old)
    raw.executescript(old_sql)
    raw.close()

    assert server.prepare_db(db=old) == old          # served, not refused
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.make_handler(old))
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        with urlopen(f"http://127.0.0.1:{httpd.server_address[1]}/state.json",
                     timeout=20) as resp:
            assert resp.status == 200
            snap = json.loads(resp.read())
    finally:
        httpd.shutdown()
        httpd.server_close()

    assert "predates the refs relation" in snap["stale"]
    assert any("predates the refs relation" in d for d in snap["drift"])
    assert snap["frontier"] == {"tips": [], "predicates": []}


def test_no_owner_table_carries_the_old_columns(db):
    """The frame's ends-when. The five provenance columns, the five JSON
    ref columns and the `item_statements` table are gone from a fresh
    database: the relation is the one record of what a row rests on."""
    def columns(table):
        return {r[1] for r in db.execute(f"PRAGMA table_info({table})")}

    for table in ("items", "glossary_terms", "constraints", "model_areas",
                  "frame_rulings"):
        assert "provenance" not in columns(table), table
    for table in ("glossary_terms", "constraints", "model_areas"):
        assert "source_refs" not in columns(table), table
    for table in ("criteria", "business_rules"):
        assert "term_refs" not in columns(table), table
    tables = {r["name"] for r in db.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert "item_statements" not in tables
    assert not columns("item_statements")


def test_a_cascade_wake_names_its_artefact_first(db):
    """One wake per (owner, artefact), as before the relation, with the
    artefact as the first ref. With no row resting on what changed, the
    artefact is the only ref."""
    from rota.core.scheduler import cascade_order, cascade_wakes
    from rota.design import graph as graph_mod

    g = graph_mod.load()
    db.execute("INSERT INTO sessions (id, role, mode, committed, seq) "
               "VALUES ('s1', 'architect', 'normal', 1, 1)")
    db.execute("INSERT INTO receipts (session_id, table_name, row_id, new_version) "
               "VALUES ('s1', 'constraints', 'k1', 2)")
    wakes = cascade_wakes(db, "s1", g)

    # The set before stage 2: every artefact downstream of `model` on the
    # graph's refs edges, once per writer.
    dependents: dict[str, set[str]] = {}
    for e in g.of_type("refs"):
        dependents.setdefault(e.t, set()).add(e.s)
    affected, queue = set(), ["model"]
    while queue:
        for dep in dependents.get(queue.pop(), ()):
            if dep not in affected:
                affected.add(dep)
                queue.append(dep)
    expected = {(owner, a) for a in cascade_order(g) if a in affected
                for owner in g.writer_of(a)}
    assert expected, "the model has dependents"
    assert {(w.role, w.refs[0]) for w in wakes} == expected
    assert len(wakes) == len(expected)
    assert all(w.refs == (w.refs[0],) for w in wakes), "no row rests on k1"


def test_a_retire_of_a_row_that_is_not_on_file_is_not_a_change(db):
    _item(db, "i1")
    _criterion(db, "c1")
    session_commit(db, SessionResult(
        session_id="s_r", role="terminologist",
        writes=[Write("refs", "criteria:c1:term:g9", {
            "src_table": "criteria", "src_id": "c1", "kind": "term",
            "target": "g9", "retire": True})]))
    assert db.execute("SELECT COUNT(*) n FROM receipts WHERE session_id = 's_r'"
                      ).fetchone()["n"] == 0


def test_glossary_same_retires_the_ref_to_the_dropped_term(db):
    """The retire door. `glossary.same` repoints a criterion at the kept
    term and retires its ref to the dropped one, so the relation and
    `criteria.load` list the kept id only. The retire is a change,
    receipted under the criterion."""
    import json

    from rota.core.sandbox import build
    from rota.roles.api import Ctx, criteria_load, glossary_same

    for gid, area in (("note", ""), ("note#src", "src")):
        db.execute("INSERT INTO glossary_terms (id, term, sense_short, sense_body, "
                   "area) VALUES (?, 'note', 'a vault file', "
                   "'a file in the vault', ?)", (gid, area))
    _item(db, "i1")
    _criterion(db, "c1")
    _ref(db, "criteria", "c1", "term", "note#src")

    sb = build("terminologist", db, mode="deliver")
    glossary_same(sb.ctx, keep="note", drop="note#src", why="both say a vault file")
    _commit_sandbox(db, sb, "s_same")

    assert [r["target"] for r in db.execute(
        "SELECT target FROM refs WHERE src_table = 'criteria' AND src_id = 'c1' "
        "AND kind = 'term'")] == ["note"]
    assert ("criteria", "c1") in {
        (r["table_name"], r["row_id"]) for r in db.execute(
            "SELECT table_name, row_id FROM receipts WHERE session_id = 's_same'")}
    loaded = criteria_load(Ctx(conn=db, role="tester", wake_refs=("note",)))
    assert [(r["id"], json.loads(r["term_refs"])) for r in loaded] == [("c1", ["note"])]


def _relayed_ruling(db):
    """A present, the principal's verdict on it, and the Liaison's relay
    to the Terminologist, as the runner leaves them. No `rulings` row."""
    import json

    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, "
               "body_refs, seq, status) VALUES ('m_present', 't1', 'liaison', "
               "'principal', 'present', '[\"g1\"]', 1, 'answered')")
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_refs, seq, status) VALUES ('v1', 'm_present', 't1', "
               "'principal', 'liaison', 'verdict', '[\"g1\"]', 2, 'answered')")
    db.execute("INSERT INTO config (key, value) VALUES ('verdict:v1', ?)",
               (json.dumps({"g1": "approve"}),))
    db.execute("INSERT INTO messages (id, cause_id, thread_id, from_role, to_role, "
               "verb, body_refs, seq, status) VALUES ('m_relay', 'v1', 't1', "
               "'liaison', 'terminologist', 'relay', '[\"g1\"]', 3, 'open')")


def test_adopt_rests_the_row_on_the_landed_ruling_or_refuses(db):
    """`_adopt_rows` reads the view and writes the ruling ref. With no
    landed `rulings` row on the cause chain, adopt refuses: the row would
    have nothing to rest on."""
    db.execute("INSERT INTO glossary_terms (id, term, sense_short) "
               "VALUES ('g1', 'recipe', 'a seed note')")
    _ref(db, "glossary_terms", "g1", "grain", "src/app.py")
    _relayed_ruling(db)

    with pytest.raises(ValueError, match="landed ruling"):
        _woken_by("terminologist", db, "relay", "m_relay").call(
            "glossary.adopt", ids=["g1"])
    assert _prov(db, "term_provenance", "g1") == ("observed", "code")

    db.execute("INSERT INTO rulings (id, ask_id, status, verdict_id) "
               "VALUES ('r1', 'm_present', 'landed', 'v1')")
    sb = _woken_by("terminologist", db, "relay", "m_relay")
    assert sb.call("glossary.adopt", ids=["g1"]) == {"adopted": ["g1"]}
    _commit_sandbox(db, sb, "s_adopt")
    assert _prov(db, "term_provenance", "g1") == ("decided", "ruling")
    assert ("glossary_terms", "g1", "ruling", "r1") in {
        (r["src_table"], r["src_id"], r["kind"], r["target"])
        for r in db.execute("SELECT * FROM refs")}


def test_the_loader_seeds_a_landed_ruling_for_a_seeded_verdict(db):
    """The adopt cases seed a `verdict:` key and the verdict message. The
    loader lands a `rulings` row for it, so the premise of the cases holds
    now that adopt needs one."""
    from rota.testkit.fixtures import seed

    seed(db, {
        "config": [{"key": "verdict:m_rule", "value": '{"g1": "approve"}'}],
        "glossary_terms": [{"id": "g1", "term": "recipe", "sense_short": "x",
                            "provenance": "observed"}],
        "messages": [
            {"id": "m_present", "thread_id": "t1", "from_role": "liaison",
             "to_role": "principal", "verb": "present", "body_refs": '["g1"]',
             "seq": 1},
            {"id": "m_rule", "cause_id": "m_present", "thread_id": "t1",
             "from_role": "principal", "to_role": "liaison", "verb": "verdict",
             "body_refs": '["g1"]', "seq": 2, "status": "answered"}],
    })
    row = db.execute("SELECT ask_id, per_item, status FROM rulings "
                     "WHERE verdict_id = 'm_rule'").fetchone()
    assert (row["ask_id"], row["per_item"], row["status"]) == \
        ("m_present", '{"g1": "approve"}', "landed")


def test_problem_consult_lists_statements_in_the_order_written(db):
    """`from_statements` follows `refs.rowid` within an item: the order the
    refs were written, not the order of the ids."""
    from rota.core.sandbox import build

    _item(db, "i1")
    for sid in ("s2", "s1"):
        _statement(db, sid, "ratified")
        _ref(db, "items", "i1", "statement", sid)
    rows = build("vision_keeper", db, mode="deliver").call("problem.consult")
    assert [r["from_statements"] for r in rows] == [["s2", "s1"]]


def test_the_refs_check_refuses_a_source_or_a_kind_that_is_not_listed(db):
    """The CHECK on `src_table` and `kind`. The values are table names and
    nouns, and the vocabulary harvester and `schema_states` skip them."""
    import sqlite3

    from rota.core.predicates import schema_states
    from rota.tools import vocabulary

    _item(db, "i1")
    with pytest.raises(sqlite3.IntegrityError):
        _ref(db, "sessions", "i1", "statement", "s1")
    with pytest.raises(sqlite3.IntegrityError):
        _ref(db, "items", "i1", "cites", "s1")
    assert not [k for k in schema_states() if k[0] == "refs"]
    assert "schema.state" not in vocabulary.harvest()["items"].sources


def test_respecify_with_a_list_replaces_the_term_refs_on_file(db):
    """A `term_refs` list given to `criteria.respecify` replaces the list on
    file, as the column did: the refs not in the list are retired and the
    kept ones stay. No list leaves the refs as they are."""
    from rota.core.sandbox import build

    _item(db, "i1")
    for gid in ("g1", "g2", "g3"):
        _term(db, gid)
    _criterion(db, "c1")
    _ref(db, "criteria", "c1", "term", "g1")
    _ref(db, "criteria", "c1", "term", "g2")

    def terms():
        return [r["target"] for r in db.execute(
            "SELECT target FROM refs WHERE src_table = 'criteria' "
            "AND src_id = 'c1' AND kind = 'term' ORDER BY rowid")]

    sb = build("terminologist", db, mode="criterion_repair")
    sb.call("criteria.respecify", id="c1", text="the tip is a share of the bill",
            term_refs=["g2", "g3"], surface_refs=["run"])
    _commit_sandbox(db, sb, "s_re1")
    assert terms() == ["g2", "g3"]

    sb = build("terminologist", db, mode="criterion_repair")
    sb.call("criteria.respecify", id="c1", text="the tip is a share of the total",
            surface_refs=["run"])
    _commit_sandbox(db, sb, "s_re2")
    assert terms() == ["g2", "g3"], "no list given leaves the refs as they are"


def test_two_respecifies_in_one_session_land_the_second_list_only(db):
    """The second `term_refs` list of a session replaces the first: a ref
    the first call staged and the second does not name is retired before
    it lands. The two lists were unioned, because the retire loop read the
    file and not the session's own writes."""
    from rota.core.sandbox import build

    _item(db, "i1")
    for gid in ("g1", "g2", "g3"):
        _term(db, gid)
    _criterion(db, "c1")
    _ref(db, "criteria", "c1", "term", "g1")

    sb = build("terminologist", db, mode="criterion_repair")
    sb.call("criteria.respecify", id="c1", text="the tip is a share of the bill",
            term_refs=["g2"], surface_refs=["run"])
    sb.call("criteria.respecify", id="c1", text="the tip is a share of the total",
            term_refs=["g3"], surface_refs=["run"])
    _commit_sandbox(db, sb, "s_re3")

    assert [r["target"] for r in db.execute(
        "SELECT target FROM refs WHERE src_table = 'criteria' "
        "AND src_id = 'c1' AND kind = 'term' ORDER BY rowid")] == ["g3"]
