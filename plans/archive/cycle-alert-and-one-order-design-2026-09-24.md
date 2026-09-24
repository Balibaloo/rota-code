# Frame 83, two orders disagree and a deferred batch restarts for ever

Design record, revision 1, 2026-09-24 19:55. Written by 8736e9fc, rota-95,
before any code. The design review on Opus 5.5 reads this record and the
sites it names, and its findings fold into revision 2.

## The fault (observed: `.rota/clickI_night92.db`, 2026-09-24 19:37 to 19:43)

Night 92 ran from a worktree at `40b4777`. Walk 1 merged `b_1`. Walk 2
ran `b_2`, "Let confirm() take a default_on_eof flag", to attempt 7 with 7
of 43 tests failing, and the key `developer|tick:tests_failing|b_2` was
quarantined and reported twice, `s243` and `s250`, a moved test between
them. The walk stuck. Walk 3 sliced `b_3`, whose item has priority 1
against `b_2`'s 0, and approved its touch note at `s282`. From `s283` to
`s300` the Developer woke on `tick:batch_start` for `b_2` eighteen times.
Each session made the same fifteen calls, read the code, found the flag
already there from attempt 7, called `code.write` and `code.commit`, got no
receipt, and ended with the runner's account "ended a tick with nothing
done". The counter `developer|tick:batch_start|b_2` read 1 at the stop.
`b_2` read `deferred` in the copy and `running` while a session ran.

The frontier on those rows, probed on a copy at 19:43 (observed): with
`b_2` deferred it offers `tick:batch_start` for `b_2`; with `b_2` running
it offers `do:preempt` with "b_3 outranks b_2". The walk prints
`do:harness` and `do:merge` only (`probes/walk.py:256-257`), so the
preempts left no line in the log.

## The cause (reasoned)

Three rules compose into the cycle.

1. **Two orders.** `tick_batch_start` (`rota/core/scheduler.py:369-378`)
   selects pending and deferred batches ordered by priority, then re-sorts
   them by `schedule_order`, a topological order over `batch_dep_facts`
   that falls back to id order when no facts exist. The re-sort discards
   the priority, so `b_2` ranks first. `preempt`
   (`rota/core/predicates.py:1232-1263`) ranks the challenger by priority,
   so `b_3` outranks the running `b_2`. `lifecycle.defer` has one caller,
   the preempt (`rota/core/loop.py:404-408`).
2. **A fresh start for a batch that has attempts behind it.** A deferred
   batch with a head commit is offered at `batch_start` like a new one. The
   Developer's start wake runs no tests and carries no attempt, so the seat
   reads the code, sees the flag, and finds nothing to do. The batch's
   `tests_failing` key is quarantined at attempt 7, so the wake that knows
   the attempt never fires.
3. **Counters erased on absence.** `quarantine_stalled`
   (`rota/core/scheduler.py:1525-1541`) deletes a counter whose key is
   absent from the ready list and not quarantined. The start's key is
   absent while its own session runs, because `running` hides it, and the
   preempt's key is absent at every start step. Each rule's step erases the
   other's count, so neither reaches the cap of three. The function's own
   comment records the same composition on icalendar, 131 sessions of one
   key.

Frame 80's revive rule is not in the chain: nothing wrote a row the
batch's refs name, and `_lift_quarantines` deletes quarantined rows only.
The `tests_failing` key stayed quarantined through the cycle (observed:
`tick_attempts` at the stop).

## The design

### Part A, the cycle alert (ruled: Roman, 2026-09-24 19:49, an alert first)

A function `cycle(conn, cap=16)` in a new module `rota/core/cycles.py`
reads the committed sessions in order and their receipts, and returns
`None` or a `Cycle(period, rounds, wakes)`.

- A wake's key for the comparison is `role|wake_kind|wake_refs`, and the
  detail is excluded, because the detail carries the attempt number and
  changes on every honest retry.
- For `n` from 1 to `cap`: round B is the last `n` committed sessions and
  round A is the `n` before them. The rounds repeat when the two key
  sequences are equal and no row moved in round B.
- A row moved in round B when a receipt of round B carries a
  `new_version` greater than the greatest version any receipt before
  round B carried for the same `table_name` and `row_id`. A new row,
  version 1 with no earlier receipt, is not a move, because night 91's
  rounds wrote a new `rulings` row each time and changed nothing the seats
  saw. A Developer's climbing commits bump the batch row's version each
  attempt, so an honest fix loop never reads as a round.
- The smallest `n` that repeats wins. The minimum is 1, night 92's period.
  Night 91's period was ten sessions. The cap is 16.
- `loop.step` calls `cycle` after a committed session and writes the
  result on `Step.cycle`. The walk prints one line,
  `CYCLE: period n, rounds 2, wakes: <the n keys>`, once per distinct
  cycle, not once per step. `render_state` shows the same line under what
  is stuck, read from the rows, so a cold cockpit sees it.
- The alert quarantines nothing and writes no row. It is for the session
  that watches the night, so the false positives can be read and tuned
  before the alert gates (ruled: Roman, 2026-09-24 19:49).

### Part B, one order (reasoned: the assistant's reading, checked with Roman at 19:50)

One function `next_batch(conn)` in `rota/core/scheduler.py` returns the
schedulable batches in one order: the highest priority first among the
batches whose `batch_dep_facts` predecessors are merged, and the schedule
order breaks ties. `tick_batch_start`'s candidate path and `preempt` both
read it. Priority chooses, and the schedule constrains.

A deferred batch that has a head commit is not a candidate for
`tick:batch_start`. It carries attempts, so a fresh start is the wrong wake
for it. It resumes on `tick:tests_failing` at the attempt it left, once a
move revives that key. While the key is quarantined the batch rests,
reported once by `tick:quarantined`. The review checks one point here:
whether `tests_failing` offers a deferred batch at all
(`rota/core/predicates.py:808-835`). If it reads running batches only, the
revive of the key sets the batch running again, in `_lift_quarantines`,
because a revived key is the batch resuming.

On night 92's rows from `s282`, this offers `b_3` at the start and nothing
at the preempt while `b_3` runs, and `b_2` rests.

### Part C, a counter is erased on a move and never on absence alone

`quarantine_stalled` stops deleting a counter because its key is absent
from the ready list. A counter is deleted when its subject moved, which is
the rule `_lift_quarantines` already applies to quarantined keys, and now
applies to every key. A wake hidden by the loop's own state, `running`
during its session, keeps its count. A wake that is never produced again
keeps a row that costs nothing.

The review checks one point here: the comment at `scheduler.py:1525-1535`
says a deleted quarantined row put the wake back at one attempt, and that
rule stays as it is. This part changes the non-quarantined branch only.

## Pins

1. `cycle` on night 92's wakes and receipts from `s282` to `s300` returns
   period 1 after `s284`. The fixture is the `sessions` and `receipts` rows
   of those sessions, extracted by a script from
   `.rota/clickI_night92.db` into `tests/rota/fixtures/night92_cycle.json`.
2. `cycle` on night 91's rows from `s229` to `s278` returns a period of
   ten at the end of the second round. The fixture comes the same way from
   `.rota/clickI_night91.db`.
3. `cycle` on a Developer loop of five `tests_failing` wakes whose batch
   row's version climbs each attempt returns `None`.
4. `cycle` on a round whose second pass writes a new row at version 1 and
   nothing else returns the period, because a new row is not a move.
5. `next_batch` on night 92's rows at `s282` returns `b_3` first, and
   `tick_batch_start` offers `b_3` while `b_2` is deferred with a head
   commit.
6. `preempt` on those rows with `b_3` running returns nothing.
7. `quarantine_stalled` keeps a non-quarantined counter whose wake is
   absent, and deletes it after a move of its subject.
8. A loop replay from `s282` on the fixture, with the scripted backend that
   writes nothing, dispatches `b_3` and never dispatches `b_2`'s start.
9. The walk prints the `CYCLE` line once for a period-1 cycle of four
   sessions, and `render_state` carries the line.

## Out of scope, for later frames

- `frontier_readonly` never drops a quarantined wake, so a cockpit reads
  `tests_failing` at attempt 7 as ready while the loop does not.
- `nightcount` can call `cycle` after the fact and count the rounds; not
  in this frame.
- The `LIKE` without quotes in `tick_batch_start`'s stalled branch is
  quoted; the same pattern in three other predicates is frame 79's note.

## The walk

One night from a worktree at this frame's closing commit. The lines: walk 3
starts `b_3` after `b_2` rests, the log carries no eighteen-fold start, and
the `CYCLE` line appears on any cycle the night runs, with its period read
against the sessions by hand. Frame 79 closes on the same night if it
reaches exhaustion.

## The price, from the anchors of `plans/operating-facts.md`

Design review on Opus about 70k to 110k. Build on Opus: one cold pass for
the three parts and nine pins, about 80k to 120k, one resume about 30k.
Diff review on Fable about 100k, because the frame touches the scheduler
and a predicate. Two gates here, about 16 minutes of GPU. The night, about
30k here and two to four hours of GPU.
