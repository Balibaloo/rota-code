"""
The cycle alert: committed sessions that repeat a round and move nothing.

Night 92 (2026-09-24) woke the Developer on `tick:batch_start` for `b_2`
nineteen times, and night 91 ran a round of ten sessions. No count saw
either. Frame 83's revision 2 rules the alert: three equal rounds, or two for
a period of one past the tick cap. It reads rows and writes none.
"""
from __future__ import annotations

from rota.core.cycles import cycle, walk_lines
from rota.core.db import init_db
from tests.rota.fixtures.extract_night import load

B2_START = 'developer|tick:batch_start||["b_2"]'


def test_night92_repeats_one_session_from_s285():
    """Pin 1. `s283` and `s284` are two rounds at a count of three, which is
    the cap and not past it. `s285` is the third round."""
    conn = load(92)

    assert cycle(conn, last="s284") is None
    found = cycle(conn, last="s285")
    assert found is not None
    assert (found.period, found.keys) == (1, (B2_START,))


def test_night91_repeats_a_round_of_ten_and_reports_it_once():
    """Pin 2. The round is ten sessions. The rule of three rounds finds it at
    `s270`, and every rotated round after it has the same identity."""
    conn = load(91)

    assert cycle(conn, last="s269") is None
    first = cycle(conn, last="s270")
    assert first is not None and first.period == 10

    identities = {cycle(conn, last=f"s{n}").identity for n in range(270, 279)}
    assert identities == {first.identity}, "a rotated round is the same cycle"


def _night(sessions: list[tuple[str, str, list[tuple[str, str]]]]):
    """A synthetic night: (wake_kind, wake_detail, receipts) per session."""
    conn = init_db(":memory:")
    conn.execute("PRAGMA foreign_keys = OFF")
    version = 0
    for n, (kind, detail, wrote) in enumerate(sessions, 1):
        conn.execute("INSERT INTO sessions (id, role, committed, seq, wake_kind, "
                     "wake_detail, wake_refs) VALUES (?, 'developer', 1, ?, ?, ?, "
                     "'[\"b1\"]')", (f"s{n}", n, kind, detail))
        for table, row_id in wrote:
            version += 1
            conn.execute("INSERT INTO receipts (session_id, table_name, row_id, "
                         "new_version) VALUES (?, ?, ?, ?)",
                         (f"s{n}", table, row_id, version))
    return conn


def test_an_honest_fix_loop_is_no_cycle():
    """Pin 3. Each attempt after a commit carries the next attempt number in
    its detail, so the keys differ and no round repeats."""
    conn = _night([("tick:tests_failing", f"attempt {n}",
                    [("batches", "b1"), ("test_runs", f"tr{n}")])
                   for n in range(1, 7)])

    assert cycle(conn) is None


def test_a_new_row_each_round_is_no_move():
    """Pin 4. A new row of the same table each round is not a move, as night
    91's new `rulings` rows were not. Two rounds are not enough, three are."""
    rounds = [("tick:challenge", "", [("rulings", f"r{n}")]) for n in range(1, 4)]

    assert cycle(_night(rounds[:2])) is None
    found = cycle(_night(rounds))
    assert found is not None and found.period == 1


def test_a_committing_round_with_no_attempt_in_its_key_is_no_cycle():
    """The diff review of frame 83. `tick:touch_mistaken` carries a path and
    no attempt, so its key stays equal across commits. Each commit updates
    the batch row, and that update is a move."""
    conn = _night([("tick:touch_mistaken", "src/x.py",
                    [("batches", "b1"), ("ledger", f"l{n}")]) for n in range(1, 5)])

    assert cycle(conn) is None


def test_honest_firings_spread_over_a_night_do_not_shorten_the_rule():
    """The diff review of frame 83. Four firings of one key with other work
    between them are not a stall. Two equal sessions at the end need a third."""
    start = ("tick:batch_start", "", [])
    other = [("tick:review", "", []), ("tick:criteria", "", []), ("tick:signoff", "", [])]
    conn = _night([start, other[0], start, other[1], start, other[2], start, start])

    assert cycle(conn) is None


def test_the_walk_prints_every_action_and_each_cycle_once():
    """Pin 9. Night 92's preempts left no line in the log. The walk now
    prints every `do:` note, and the cycle line once per identity."""
    from rota.core.loop import Step
    from rota.core.predicates import SCHEDULER
    from rota.core.scheduler import Wake
    from rota.roles.principal import render_state

    seen: set = set()
    preempt = Step(wake=Wake(SCHEDULER, "do:preempt", refs=("b_2", "b_3"),
                             detail="b_3 outranks b_2"),
                   note="deferred b_2; b_3 outranks it")
    assert walk_lines(preempt, seen) == ["  do:preempt: deferred b_2; b_3 outranks it"]

    conn = _night([("tick:batch_start", "", [])] * 4)
    lines = []
    for n in range(1, 5):
        lines += walk_lines(Step(wake=Wake("developer", "tick:batch_start",
                                           refs=("b1",)),
                                 cycle=cycle(conn, last=f"s{n}")), seen)
    cycles = [x for x in lines if x.startswith("CYCLE:")]
    assert cycles == ['CYCLE: period 1, rounds 3, wakes: '
                      'developer|tick:batch_start||["b1"]'], lines

    assert "CYCLE: period 1" in render_state(conn), \
        "a cold cockpit reads the cycle from the rows"
