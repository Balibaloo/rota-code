"""
The frontier is one definition, and it is ordered.

Two properties, both of which were false until the predicates were declared.

**One definition.** It used to be `open_tips(conn) + predicate_wakes(...)` — the
∪ in "tips ∪ predicates" written literally, which put the frontier in two places
and made the tips half invisible to every check written against the other. The
terminal-state lint could not see that `messages.status = 'open'` had a way out,
because the way out was in a different function.

**Fix before start.** A failed verdict outranks a new batch. Every role is
single-instance, so starting new work is precisely how a fix gets starved.
"""
from __future__ import annotations

import pytest

from rota.core import predicates as P
from rota.core.db import init_db
from rota.core.scheduler import frontier


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


@pytest.fixture
def broken_and_ready(db):
    """
    Something known-wrong, and something ready to start.

    A contested item rather than a failed verdict, because `tick_batch_start`
    refuses outright while any batch is running — a *structural* fix-before-start
    that leaves nothing for the ordering to demonstrate. The contested item is
    the honest case: both predicates genuinely fire, and the order is what
    decides which is offered first.
    """
    db.execute("INSERT INTO items (id, text, kind, provenance, approval, "
               "approval_ver, version) VALUES "
               "('i1','the principal rejected this','in_scope','decided','contested',1,1), "
               "('i2','new work','in_scope','decided','approved',1,1)")
    db.execute("INSERT INTO tickets (id, item_id, text) VALUES ('t2','i2','build it')")
    db.execute("INSERT INTO batches (id, item_id, status) VALUES ('b_new','i2','pending')")
    return db


def test_the_frontier_is_every_predicate(db):
    """
    Not tips plus something else. If this ever splits again, the half that is
    not in the registry stops being checkable by the terminal-state lint.
    """
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
               "VALUES ('m1','t1','liaison','gatekeeper','deliver',1)")

    assert "message_tips" in P.REGISTRY
    assert ("messages", "status", "open") in P.drained_states()
    assert [w.message_id for w in frontier(db)] == ["m1"]


def test_fix_outranks_start(broken_and_ready):
    ready = frontier(broken_and_ready)
    kinds = [w.kind for w in ready]

    assert "tick:contested" in kinds, kinds
    assert "tick:batch_start" in kinds, kinds
    assert kinds.index("tick:contested") < kinds.index("tick:batch_start"), \
        "new work was offered before the principal's rejection was dealt with"


def test_traffic_outranks_everything(broken_and_ready):
    """
    A message is work already in flight with somebody waiting on the other end.
    It goes first — not because it is more important, but because it is already
    started, and the system's whole discipline is finishing before starting.
    """
    broken_and_ready.execute(
        "INSERT INTO messages (id, thread_id, from_role, to_role, verb, seq) "
        "VALUES ('m1','t1','liaison','gatekeeper','deliver',1)")

    assert frontier(broken_and_ready)[0].kind == "message"


def test_every_band_has_an_order():
    assert P.check_bands_are_declared() == []


def test_a_wake_target_is_a_role_or_says_why_not():
    """
    `wakes=""` used to mean both "computed per row" and "no role at all", so a
    lint over the field could not tell a typo from a deliberate blank. Now they
    are distinct sentinels and the check covers every predicate rather than
    skipping the empty ones.
    """
    assert P.check_predicates_wake_real_roles() == []
    assert P.REGISTRY["merge"].wakes == P.SCHEDULER
    assert P.REGISTRY["message_tips"].wakes == P.DERIVED


def test_a_typo_in_wakes_is_caught(monkeypatch):
    original = P.REGISTRY["contested"]
    monkeypatch.setitem(P.REGISTRY, "contested",
                        P.Predicate(name="contested", wakes="gatekeper",
                                    drains=original.drains, fn=original.fn))
    assert P.check_predicates_wake_real_roles()


def test_the_agenda_only_fires_when_the_principal_is_there(db):
    """Presenting an agenda to an empty room is not a wake, it is a no-op that
    keeps firing."""
    db.execute("INSERT INTO ledger (id, about_ref, about_table, default_taken, author) "
               "VALUES ('l1','i1','items','assumed soft delete','developer')")

    assert not [w for w in frontier(db, principal_present=False)
                if w.kind == "tick:agenda"]
    assert [w for w in frontier(db, principal_present=True)
            if w.kind == "tick:agenda"]


def test_a_broken_predicate_is_not_swallowed(db, monkeypatch):
    """
    `all_wakes` caught sqlite3.Error and carried on, for predicates over tables
    that did not exist yet. They all exist. A predicate silently contributing
    nothing now looks identical to one correctly finding nothing, which is the
    worst possible failure for something the frontier is derived from.
    """
    import sqlite3

    def explode(conn):
        raise sqlite3.OperationalError("no such table: imaginary")

    original = P.REGISTRY["contested"]
    monkeypatch.setitem(P.REGISTRY, "contested",
                        P.Predicate(name="contested", wakes=original.wakes,
                                    drains=original.drains, fn=explode))

    with pytest.raises(sqlite3.OperationalError):
        P.all_wakes(db)


# ---------------------------------------------------------------------------
# Bounded ticks — found by a real repository, not by inspection
# ---------------------------------------------------------------------------

def test_a_tick_that_cannot_drain_is_eventually_quarantined(tmp_path):
    """
    Law 4 bounds failure and bounded only messages. The first foreign repository
    found the hole in six sessions: a survey session read its area, wrote three
    glossary terms, and never called `surveys.attest`. `tick_survey` drains on
    `survey_records`, so nothing drained, so the identical wake was produced
    again — same role, same area, forever.

    It never looked broken. The system was busy, committing, and writing
    artefacts, and it would never have reached area two of twelve. That is worse
    than a dead end: a dead end at least reports quiescence.
    """
    from rota.core import config
    from rota.core.db import init_db
    from rota.core.scheduler import Wake, frontier, note_dispatch

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO entries (id, author, ts_order, text) "
               "VALUES ('e1','principal',1,'x')")
    db.execute("INSERT INTO statements (id, span_entry, span_start, span_end, text, "
               "status) VALUES ('s1','e1',0,1,'x','contradicted')")

    stuck = [w for w in frontier(db) if w.kind == "tick:contradiction"]
    assert stuck, "the fixture should produce a tick that nothing here will drain"
    wake = stuck[0]

    cap = config.get(db, "tick_attempt_cap")
    for _ in range(cap):
        assert any(w == wake for w in frontier(db)), \
            "a tick under the cap must keep being offered"
        note_dispatch(db, wake)

    assert not any(w == wake for w in frontier(db)), \
        "past the cap it should stop being dispatched"

    # And on every later call, which is the half that was missing. Asking once
    # cannot tell a wake that is gone from a wake that is about to come back.
    for _ in range(3):
        assert not any(w == wake for w in frontier(db)), \
            "an abandoned tick came back: quarantine is not terminal"


    # A contradiction tick keeps being *produced* while the statement stands, so
    # it stays in the ready list and its count is never forgotten. A survey tick
    # does not — `tick_survey` reads the quarantine table and stops producing
    # what it finds there, which is the case that breaks. See
    # `test_quarantine_does_not_erase_its_own_evidence` in test_onboarding.


def test_abandoning_a_tick_is_never_silent(tmp_path):
    """Quiescence means "no predicate fires". A tick quietly dropped would make
    the system report itself finished with the work undone, which is the one
    failure this whole design is arranged against."""
    from rota.core import predicates as P
    from rota.core.db import init_db

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined) "
               "VALUES ('terminologist|tick:survey|.', 9, 1)")

    assert P.REGISTRY["quarantined"].fn(db), \
        "an abandoned tick must reach the principal, like an abandoned message"


def test_a_tick_that_keeps_making_progress_is_never_bounded(tmp_path):
    """The bound is on dispatch *without* progress. A Developer bouncing on a red
    harness is the loop working, and the counter resets the moment the wake stops
    being produced — which is what draining looks like from out here."""
    from rota.core import config
    from rota.core.db import init_db
    from rota.core.scheduler import Wake, frontier, note_dispatch

    db = init_db(tmp_path / "rota.db")
    wake = Wake("developer", "tick:tests_failing", refs=("b1",))

    # Under the bound, which is the state this test is about. It used to dispatch
    # nine times against a cap of three -- a state the scheduler cannot reach,
    # since `quarantine_overrun` fires at the cap on the next frontier call. It
    # passed only because the count was then deleted regardless of quarantine,
    # which was the bug: a wake abandoned at three and one that drained at two
    # both left an empty table, so the table could not tell them apart.
    for _ in range(config.get(db, "tick_attempt_cap") - 1):
        note_dispatch(db, wake)

    frontier(db)          # the wake is no longer produced, so the count clears

    assert not db.execute("SELECT 1 FROM tick_attempts").fetchone(), \
        "a wake that stopped being produced should leave no debt behind"


def test_an_abandoned_area_lets_the_role_move_on(tmp_path):
    """
    Eleven of twelve areas surveyed and the frontier went empty. The twelfth was
    quarantined by the attempt bound, which left it permanently *outstanding* --
    so the Terminologist never finished, and the Architect never started.

    Abandonment has to be terminal, not an invisible hole. It is recorded, it is
    reported to the principal, and the work behind it carries on.
    """
    from rota.core.db import init_db
    from rota.core.scheduler import SURVEY_ORDER, tick_survey

    db = init_db(tmp_path / "rota.db")
    for area in ("a", "b"):
        db.execute("INSERT INTO code_index (grain, grain_kind, area) "
                   "VALUES (?, 'path', ?)", (f"{area}/x.py", area))
    first = SURVEY_ORDER[0]
    db.execute("INSERT INTO survey_records (id, area, outcome) VALUES (?, 'b', "
               "'none_found')", (f"{first}:b",))
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined) "
               "VALUES (?, 9, 1)", (f"{first}|tick:survey|a",))

    roles = {w.role for w in tick_survey(db)}
    assert first not in roles, "an abandoned area must not hold its role open"
    assert roles == {SURVEY_ORDER[1]}, "the next role should have started"


def test_telling_the_principal_discharges_the_telling(tmp_path):
    """
    `tick_quarantined` counted abandoned things and nothing cleared the count, so
    it fired every pass forever -- and on the first foreign repository it was
    bounded by the very mechanism it exists to report, three sessions in.

    A report that cannot be discharged is not a report, it is an alarm nobody can
    switch off.
    """
    from rota.core import predicates as P
    from rota.core.db import init_db

    db = init_db(tmp_path / "rota.db")
    db.execute("INSERT INTO tick_attempts (tick_key, attempts, quarantined) "
               "VALUES ('terminologist|tick:survey|a', 9, 1)")

    assert P.REGISTRY["quarantined"].fn(db), "it should fire while undischarged"

    db.execute("UPDATE tick_attempts SET reported = 1")

    assert not P.REGISTRY["quarantined"].fn(db), \
        "once the principal has been told, it must stop firing"
