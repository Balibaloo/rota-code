# Design record: a quarantined criteria tick wakes again for ever (frame 80)

Written by the assistant, session a664990b, on 2026-09-24 12:41, for a
design review before any code. Revision 2 at 12:44 folds the design
review's ten answers and nine findings (observed: the reviewer on Opus
5.5, 120.4k on the harness line, 49 tool calls, 6.5 minutes; its probes
are `p1.py` to `p5.py` in this session's scratchpad). Meta workflow for
the build. Rota workflow for the fault. The tree is `3a98180`.

## The fault (observed: `.rota/clickI_night91.db`, 2026-09-24 12:30)

- The item `bg_1_summary` was written by the Vision Keeper in `s207`,
  woken by the Architect's `propose` `m92` in the thread of the
  Developer's `escalate` `m91` on `bg_1`. The seat called
  `problem.assert` twice, first with `id='bg_1'` and then with
  `id='bg_1_summary'`. Only the second landed: the `receipts` table holds
  `s207`, `items`, `bg_1_summary` and no `items` row `bg_1`. The text is
  a summary of Click with one sentence on `echo_json`. The principal
  approved it at `m103` to `m105` (`rulings` `r_a66b9db45a`). The slicing
  tick `s228` wrote its one ticket, `tk_1_bg_1_summary`: "the software is
  a command-line interface toolkit called Click".
- `tick_criteria` (`rota/core/scheduler.py:286-299`) wakes the
  Terminologist per item whose ticket has no criteria. The key is
  `terminologist|tick:criteria|bg_1_summary`. Each session sends one
  `challenge` to the Vision Keeper and writes no criterion (`m121`,
  `m122`, `m123`; the third says `criteria.specify` refused
  `surface_refs=[echo_json]`; the first two name `tk_1` and `echo_json`,
  not the summary ticket). At `tick_attempt_cap` 3, `quarantine_stalled`
  (`scheduler.py:1489`) sets `quarantined` 1.
- `quarantined` (`rota/core/predicates.py:1316`) wakes the Liaison with
  the detail `1 abandoned: criteria for bg_1_summary (terminologist), 3
  attempts`. `rota/core/loop.py:330` then sets `reported` 1 on every
  quarantined key. The Liaison presents the item (`m124`), the principal
  converses and gives a verdict (`m125`, `m126`), the Liaison's converse
  and verdict sessions write a `rulings` row (`r_7d997870c7`,
  `bg_1_summary: approve`) and relay to the Vision Keeper (`m127`).
- The relay session `s258` calls `problem.set_approval`,
  `problem.prioritize` and `problem.set_approval` again. Each is a write
  to `items` row `bg_1_summary` with `amends` False
  (`rota/roles/api.py:908-932`). The row's own `version` stays 1. The
  receipt's `new_version` 27 is the table counter
  (`rota/core/db.py:322-331`), not the row's.
- `session_commit` (`db.py:566-595`) calls `_lift_quarantines` for every
  write that is not a refs write. Its first statement (`db.py:500-503`)
  deletes every quarantined key whose refs name the written row id,
  `%|bg_1_summary`. The criteria key is gone, and the next pass produces
  the wake at attempts 1. The cycle ran five rounds of ten sessions,
  `s229` to `s278`: three `tick:criteria` sessions, three challenge
  answers, the Liaison's report, converse and verdict sessions, and the
  relay (observed: the review's probe `p2.py`; the frame's status of
  11:02 counted three rounds of nine from `s251`). The counter read
  attempts 1 at the stop.
- The same rule revived the exhausted key at every head commit on night
  91 (observed: frame 79's record, the route B section).

## Why the tick wakes again (reasoned: from the rows and the code above)

The rule's docstring says what it means: "A quarantine holds while its
subject is unchanged; a write that changes the subject is the exit." The
code keys on any write to the row, and never asks whether the subject
changed. The tree already distinguishes the two. `Write.amends`
(`db.py:245-252`) says that approval, priority and status transitions are
state changes and not content changes, and `_apply_write` moves the
row's `version` on an amendment only (`db.py:430-433`).

So the two halves of the design compose into a cycle. The quarantine
reports itself once. The report ends in a verdict. The verdict's relay
writes the subject's row with values that change nothing. The write
revives the tick. Nothing in the loop changes the subject, and the
composition says a question changes nothing: only a ratified amendment
to something approved revokes work downstream.

The obligation is real. The ticket has no criteria, and no criterion can
be written for a summary. The abandonment was said out loud once, which
is what `quarantined` exists for. Re-deriving the same debt after a
verdict that changed nothing is the fault, and it is the only fault this
frame repairs. Where the summary item came from is out of scope, below.

No ruled sentence promises the revive or describes the exit (observed:
the review's read of `rota/LAWS.md`). Law 6 says "The attempt caps and
the ladder bound a cycle." Night 91 breaks that sentence, and the route
restores it. The route changes no law.

## The route: a revive keys on a move of the subject, not on any write

`session_commit` reads the row's `version` and `approval` before
`_apply_write`, computes `moved` after it, and passes it to
`_lift_quarantines(conn, w, moved)`. `moved` is a required parameter,
so no caller can forget it. A write moves its subject when one of these
holds:

1. The row did not exist before the write. A new row is a new version.
2. The table has a `version` column, and the version after the write
   differs from the version before. That is an amendment, or a write
   that carries `version` in its values. Every artefact table with an
   `id` column has one (observed: the review's schema probe).
3. The table has an `approval` column, and the approval after the write
   differs from the approval before. The principal's ruling on the row
   moved. `reopen` (`predicates.py:855-863`) keys a Developer tick on
   the batch and the item and reads the item's approval, so a withdrawal
   or a re-approval revives that key (the review's finding 8). An
   approval written over the same approval, night 91's case, moves
   nothing.
4. The table is `batches` and `head_commit` is in the values. A new head
   commit is progress, the docstring's own case (`db.py:504-508`). The
   pipeline writes an existing `batches` row through `code.commit`
   alone (`api.py:9038`); `batches.group` refuses an existing id, and the
   status writers in `lifecycle.py` and `boot.py` write raw SQL outside
   `session_commit` (observed: the review's point 3). So rule 4 keeps
   every `batches` revive that exists today.
5. A junction write is a move. Its `row_id` is a label such as
   `bg_1:tk_1`, which no tick key holds, so the branch is inert today
   and stays inert (observed: the review's point 4). `code_index` and
   `claims` are not in `ARTEFACT_TABLES`, so `_lift_quarantines` never
   runs for them.

In `_lift_quarantines`, the first `DELETE` (`db.py:500-503`) and the
criteria-and-tests branch (`db.py:521-535`) run only when `moved` holds.
The `tests_failing` reset on a head commit (`db.py:512-514`) and the
`test_runs` reset on a body write (`db.py:509-511`) stay unconditional.
Their pins in `tests/rota/test_desk_guards.py:479-513` call
`_lift_quarantines(db, W)` with two arguments and gain `moved=True`.

One pattern changes in the first `DELETE`. `%,{row_id}%` has no end
anchor, so a write to `c_1` revives a key whose refs hold `,c_10`. It
becomes `%,{row_id}` and `%,{row_id},%`, as the `|` patterns already
are (the review's finding 7, PLAUSIBLE by reading; no night 91 key shows
it).

One flag changes beside it. `criteria.respecify`
(`rota/roles/api.py:3560-3621`) rewrites a criterion's text and surface
refs with `amends` False, so under rule 2 a repaired criterion would move
nothing, and the Tester that gave up on it would never wake. That is the
case the rule was written for (`tests/rota/test_steering.py:108-135`).
The flag was set False by `fd788bd` on 2026-08-26 with no reason in the
commit, and no reader in `rota/` reads a criterion's row `version`
(observed: the review's point 5). The route sets `amends` True on the
respecify write, so the repair moves the version. Of the seven pipeline
writes with `amends` False, it is the only content change; the others
are approval, priority, a statement's status, a ledger's status, a
message, and the head commit (observed: the review's point 2).

What the route buys, on night 91's own rows: the three writes of `s258`
move nothing, the key stays quarantined 1 and reported 1, `tick_criteria`
still produces the wake and `quarantine_stalled` still drops it, and the
frontier is quiet on the item (observed: the review's probe `p5.py`
replayed `s258` through `session_commit` with the route patched in, and
the key survived at 3, 1, 1). An amendment of the item, `problem.assert`
with new text, moves the version to 2 and revives the key.
`tick_slicing` already treats a new version as new debt under its own
key (`scheduler.py:270-284`), so the two rules agree.

What the route does not do: it does not discharge the obligation. The
ticket keeps no criteria, the key stays quarantined, and the count in
`quarantined` is one abandoned tick, reported. A verdict that changes
the approval is a move under rule 3 and revives the debt. A verdict that
approves what is approved is the report's end and changes nothing about
the quarantine, because the tool never closes an assumption for the
principal (the composition, Flows). The frame's ends-when line says "the
principal's verdict or a new version discharges it", and this is the
route's reading of it. That reading is the grill's one question.

## The pinned tests

In `tests/rota/test_steering.py`, beside
`test_a_quarantine_lifts_when_its_subject_moves`:

1. `test_a_verdict_that_changes_nothing_revives_nothing`, the cycle once:
   seed the item `bg_1_summary` approved at version 1, its ticket with no
   criteria, and the key `terminologist|tick:criteria|bg_1_summary` at
   attempts 3, quarantined 1, reported 1. Commit one Vision Keeper
   session through `session_commit` with the three writes of `s258`,
   `amends` False. The key survives with its counts, and `frontier`
   inside a rolled-back transaction holds no `tick:criteria` wake with
   refs `bg_1_summary`. `frontier_readonly` never calls
   `quarantine_stalled`, so it lists the wake and is the wrong reader
   (the review's finding 1). The steering fixture's `t1` has no criteria
   either, so the assertion filters by refs. Then commit an amendment of
   the item's text, `amends` True. The key is gone, and the wake is back.
2. The existing pin, `test_a_quarantine_lifts_when_its_subject_moves`,
   calls `_lift_quarantines(db, W)` with a bare class. It becomes a
   commit of a respecify-shaped write, `criteria` `c1` with new text
   through `session_commit`, and its two assertions stay.
3. `test_a_head_commit_still_revives_the_batchs_keys`: a quarantined
   `critic|tick:review|b1` and a `batches` write carrying `head_commit`
   with `amends` False. The key is gone.
4. `test_an_approval_change_moves_the_item`: a quarantined
   `developer|tick:reopen|b1,i1`. A `set_approval` write of `approved`
   over `approved` leaves it. A write of `contested` removes it.
5. `test_a_respecified_criterion_moves_its_version`, beside the op's
   other pins: the op's write reaches `session_commit` with `amends`
   True and the row's version moves.
6. One assertion for the anchor: a write to `c_1` leaves a quarantined
   key whose refs end in `,c_10`, and removes one whose refs hold `,c_1`.

The pins seed rows by SQL and commit through `session_commit` with
`SessionResult` and `Write`, as `tests/rota/test_refs.py` does. A
session row needs `id`, `role` and `seq`; `session_commit` writes them.

## The walk

One warm night, `GAUNTLET_NIGHT=92`, from a worktree at this frame's
closing commit, by the shape of `.rota/launch_night91.sh`, with
`ROTA_REPO` at `C:/Users/roman/rota_night92` and `ROTA_RUNS` at the main
checkout's `.rota`. Frames 81, 79 and 80 close on that night, each on
the line its record's walk section names. This frame's line: after the
Liaison's `tick:quarantined` session on `bg_1_summary`, no further
`tick:criteria` session for `bg_1_summary` runs while the item's version
and approval stay, so the Terminologist's sessions on that key number at
most three in the night.

The night's second observation, not a gate: what the run does once the
summary ticket is quiet, because night 91 never got there. On night 91's
rows with the route in place, the frontier's next wakes are the
Architect on `tick:exhausted` for `bg_1` (frame 79's field), the Tester
on `tick:tests_missing` for `bg_1`, and two Critic `tick:challenge`
wakes, one on `@claim:items:bg_1_summary` (observed: the review's
point 9). That Critic wake is the next seat that can contest the
summary.

## Out of scope, recorded for the next frame that meets them

- The summary item. A seat asserted a summary of the software as an
  in-scope item, the designed principal approved it, and slicing gave it
  a ticket no criterion fits. Under a real principal the present at
  `m103` is where it is contested. That is the seat's judgement and the
  principal seam of batch D, frames 41 and 42.
- The `tick:criteria` key names the item, and the debt belongs to the
  ticket. An amendment of `tk_1_bg_1_summary` matches no pattern, so it
  revives nothing today and nothing under the route (the review's
  finding 9). One line in `tick_criteria` or in the revive, for the
  frame that next touches the criteria tick.
- The Liaison's `quarantined` brief (`rota/roles/prompts/liaison/
  quarantined.md`) describes the message case only: "a message failed too
  many times", "infrastructure failing, not anybody's judgement". A tick
  quarantined on a seat's refusal to write is a judgement. A brief change
  re-records the Liaison's quarantined cases, so it waits for a frame on
  that brief.
- A quarantined key whose wake is no longer produced stays in
  `tick_attempts` for ever. `quarantine_stalled` forgets a key only while
  `quarantined` is 0. Cosmetic, and the count stays honest.
- Frame 79's notes carry over: three predicates match a batch id without
  quotes; the Architect's exhausted brief opens with a sentence route B
  makes imprecise; a tick as a message cause. The review saw the
  Architect's `tick:exhausted` wake read "attempt 12 of 10" with no
  Architect exhausted session on file, on night 91's rows; that is frame
  79's field and its night.
- The gate's stored baseline is `b82565d` of 2026-09-21. Roman's call.

## Price (reasoned: frame 79's actuals, in its status of 12:24)

Design review: 120.4k on Opus, actual, against 95k estimated. Build 60k
to 80k on Opus: two functions in `db.py`, one flag in `api.py`, six pins
(frame 79: 86.6k over three passes, on a larger surface). Diff review
about 100k on Fable (frame 79: 112.8k); the write pipeline is touched,
so the review probes every branch of `_lift_quarantines`. Gate 15k here,
one run. The night: about three hours of GPU (night 91 ran 3 hours 16
minutes to the stop) and about 30k of this context to read it and close
three frames, an estimate with no anchor in the register. About 250k in
agents after the review, walls apart.
