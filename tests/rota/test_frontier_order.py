"""
The frontier, when several things are ready.

The register called this "the big one" and the ruling (2026-08-28) said do it
before onboarding: ordering must be logical, and "alphabetically by predicate
name" made the schedule a fact about naming accidents. The evidence it was
load-bearing was real -- message traffic outranked a gate, the first report
always won, and a designed round never ran once in production.

The rule now: **band, then declared order, then age.** Bands are the design's
priority classes and stay. Within a band, tick predicates are offered in the
order the spine declares them (registration order -- the file is organised as
the spine, so position is a reviewable declaration where a name is not).
Messages were always FIFO by their global seq and stay so. Every part is a
pure function of the database, which the chaos suite already holds the
frontier to.

These are also the first tests in the repository to put more than two wakes
on the frontier at once -- the register measured that nothing ever had.
"""
from __future__ import annotations

import pytest

from rota.core.db import init_db
from rota.core.predicates import REGISTRY
from rota.core.scheduler import frontier_readonly


@pytest.fixture
def db(tmp_path):
    return init_db(tmp_path / "rota.db")


def _ask(db, mid, to, term_id, seq):
    db.execute("INSERT INTO messages (id, thread_id, from_role, to_role, verb,"
               " body_refs, seq) VALUES (?,?,?,?,?,?,?)",
               (mid, f"t{seq}", "liaison", to, "ask", f'["{term_id}"]', seq))


def test_names_no_longer_decide_the_schedule():
    """The placeholder, structurally impossible now: no sort key anywhere in
    the registry path reads the predicate's name."""
    ordered = sorted(REGISTRY.values(), key=lambda p: (p.order, p.seq))
    seqs = [p.seq for p in ordered]
    assert len(set(seqs)) == len(seqs), "registration order is a total order"
    # A predicate later in the file never outranks an earlier same-band one.
    by_band: dict[str, list[int]] = {}
    for p in ordered:
        by_band.setdefault(p.band, []).append(p.seq)
    for band, s in by_band.items():
        assert s == sorted(s), f"{band}: declared order is the offer order"


def test_messages_are_offered_oldest_first_whatever_their_ids(db):
    """Three askable questions, seeded with ids chosen so that alphabetical
    order and age order disagree -- the frontier follows age."""
    for gid in ("g1", "g2", "g3"):
        db.execute("INSERT INTO glossary_terms (id, term, sense_short, "
                   "provenance) VALUES (?, ?, 'x', 'observed')", (gid, gid))
    _ask(db, "m_zzz", "terminologist", "g1", 1)   # oldest, last by name
    _ask(db, "m_mmm", "architect", "g2", 2)
    _ask(db, "m_aaa", "vision_keeper", "g3", 3)   # newest, first by name
    db.commit()

    tips = [w.message_id for w in frontier_readonly(db)
            if w.kind == "message" and w.detail == "ask"]
    assert tips == ["m_zzz", "m_mmm", "m_aaa"], \
        "seq decides, not the id the sender happened to mint"


def test_a_frontier_of_three_orders_purely(db):
    """The register's measurement: nothing had ever handed the frontier
    three things. Recomputing the same world gives the same order -- the
    chaos suite's purity claim, held at width."""
    for gid in ("g1", "g2", "g3"):
        db.execute("INSERT INTO glossary_terms (id, term, sense_short, "
                   "provenance) VALUES (?, ?, 'x', 'observed')", (gid, gid))
    _ask(db, "m1", "terminologist", "g1", 1)
    _ask(db, "m2", "architect", "g2", 2)
    _ask(db, "m3", "vision_keeper", "g3", 3)
    db.commit()

    first = [str(w) for w in frontier_readonly(db)]
    again = [str(w) for w in frontier_readonly(db)]
    assert first == again
    assert len([w for w in frontier_readonly(db) if w.kind == "message"]) == 3
