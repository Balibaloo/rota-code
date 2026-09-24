# Design record: the exhaustion ladder never climbs past the Developer (frame 79)

Written by the assistant, session 4fe8b80c, on 2026-09-24 10:21, for a
design review before any code, and for the grill question the frame's
ends-when line names. Meta workflow for the build. Rota workflow for the
fault. The tree is `96a2ae4`.

## The fault (observed: `.rota/clickI_night91_walk1.db`, 2026-09-24 10:17)

- Eight sessions woke on `tick:exhausted`, and every one is the Developer:
  `s169`, `s170`, `s173` at attempt 10 of 10; `s176`, `s177`, `s180` at
  attempt 11 of 10; `s189`, `s190` at attempt 12 of 10. Every row carries
  `wake_refs` `["bg_1"]`, `trigger_msg` NULL and `committed` 1.
- The Developer sent eight messages: four `challenge` to the Tester
  (`m65`, `m66`, `m67`, `m70`), two `escalate` to the Architect (`m68`,
  `m76`) and two `question` to the Vision Keeper (`m72`, `m74`). Every
  `body_refs` lists criteria and test ids. None lists `bg_1`. Every
  `cause_id` is NULL and every `thread_id` is the message's own id. A
  tick has no trigger message, so the send writes `cause_id: ctx.trigger`
  as None (`rota/core/sandbox.py:1785-1793`).
- Three messages name `bg_1`, and all three come before the cap: `m57`,
  the Architect's report to the Liaison on the batch's cut, at seq 57;
  `m61`, the Liaison's present; `m62`, the principal's converse. The first
  exhausted wake is `s169`.
- `_next_rung` (`rota/core/predicates.py:906-920`) reads `sent`, the
  `from_role` of every message whose `body_refs` contains the batch id.
  On night 91 that set is architect, liaison and principal. The first
  role in `LADDER` not in the set is the Developer, on every pass.

## Why the reader never climbs (reasoned: from the rows above)

Two faults sit in one query.

1. **The writer stamps what the model passes.** `body_refs` at the send is
   the model's `refs` argument (`sandbox.py:1790`). The Developer's
   exhausted brief (`rota/roles/prompts/developer/exhausted.md`) tells the
   seat to name the rows of its block, the criterion and the test, and it
   never names the batch. One door demands the batch id, and it covers
   `report` only (`sandbox.py:1247-1255`, measured on `AR-a-dead-end`,
   2026-09-01). So the reader keys on a field this seat never writes.
2. **The reader reads the batch's whole history, not the exhaustion.** Had
   `m68` carried `bg_1`, `sent` would hold the Architect as well, from
   `m57`, and the next rung would be the Vision Keeper. A report on the
   cut, sent 112 sessions before the cap, would count as the Architect's
   answer to the exhaustion. A fix to the writer alone skips one rung.

This is the shape of batch A's key: the writer and the reader name
different fields. The field the runner stamps by construction is
`sessions.wake_refs`. `rota/core/runner.py:3120` passes `list(wake.refs)`
and `rota/core/db.py:896-900` stores it, and all eight rows carry it. Two
readers in the tree already ask "was this rung asked" from that column:
`_repair_attempted` (`predicates.py:1039-1042`) and the batch-start stall
guard (`rota/core/scheduler.py:322-326`). Both read `wake_kind`,
`committed = 1` and `wake_refs LIKE`.

The briefs already read the ladder this way. The Architect's exhausted
brief opens with "Developer has already been asked and had nothing to
route, which is itself the finding" (`prompts/architect/exhausted.md`).
Asked means woken at the cap. It does not mean "sent a message that names
the batch".

## The two routes of the ends-when line

### Route A, the writer: a message from a batch-held seat carries the batch id by construction

At the send (`sandbox.py:1785`), when `ctx.batch_id` is in
`ctx.wake_refs` and the verb climbs (`escalate`, `question`, `challenge`,
`report`), add `ctx.batch_id` to `body_refs`. Stamp, and never refuse: a
refusal of an argument loops a 9B seat (observed: frame 81, `c5da552`).

- What it buys: `_next_rung` stays as it is. Messages about a batch are
  findable by the batch id. The report door becomes a stamp too.
- What it costs: fault 2 stays. On night 91's rows the climb skips the
  Architect, so the reader changes anyway. `body_refs` has 99 readers, and
  three duplicate guards compare refs (`sandbox.py:1233`, `:1278`,
  `:1453`). A stamped batch id on every climbing message makes "exactly
  these refs" collide across one session's messages, unless the stamp is
  excluded from each comparison. The test fixtures that seed messages
  need the id. The write pipeline is touched, so the diff review must
  probe the guards.
- Price: build about 140k on Opus (frame 81's cold pass in the same file,
  137k), diff review about 110k on Fable.

### Route B, the reader: `_next_rung` reads the sessions the exhaustion opened

`_next_rung` derives `asked` from `sessions`: the roles with a row whose
`wake_kind` is `tick:exhausted`, `committed` is 1 and `wake_refs` holds
the batch id. The first role in `LADDER` not in `asked` is the rung.
Nothing else changes. The docstring's question, "who has not yet been
asked about this batch", becomes literal.

- What it buys: both faults close at the one site the frame names. The
  climb is one exhausted session per rung: Developer, Architect, Vision
  Keeper, then quiet at the top, where the Vision Keeper's exhausted mode
  reports to the Liaison and the report door demands the batch id,
  unchanged. No brief changes, so no case re-records. The Architect's
  report on the cut no longer counts as its answer.
- What it costs: a Developer that was asked and kept editing counts as
  asked. That is the docstring's meaning, and the brief's last line
  already says "Do not spend another attempt on the code". A session
  that did not commit does not count, and the tick quarantine bounds the
  repeat at three (observed: three wakes per attempt on night 91). The
  two pins in `tests/rota/test_delivery.py`,
  `test_the_ladder_climbs_one_rung_at_a_time` and
  `test_the_ladder_stops_at_vision_keeper`, seed messages to climb and
  flip to seed sessions. A message alone no longer climbs the ladder: a
  Developer that escalates with the batch id in refs and no exhausted
  session has not been asked at the cap. That is a semantic change and
  the review reads it as a point.
- Price: build 60k to 80k on Opus (one query, two pins flipped, two
  added), diff review about 90k on Fable, gate 15k.

### Recommended: route B (reasoned: it closes both faults at the one site the frame names, and it changes no brief)

Route A alone does not make night 91's ladder climb past the Architect,
and it touches the guards a 9B seat trips. Route B reads the field the
runner stamps by construction, with two precedents in the tree and the
briefs' own wording.

## The pinned tests (route B)

1. `test_the_ladder_climbs_one_rung_at_a_time`: seed a committed Developer
   session with `wake_kind` `tick:exhausted` and `wake_refs` `["b1"]`, and
   the frontier reads `["architect"]`. Seed the Architect's, and it reads
   `["vision_keeper"]`.
2. `test_the_ladder_stops_at_vision_keeper`: three sessions, one per rung,
   and no `tick:exhausted` wake.
3. New, night 91's shape: a committed Developer session on exhausted that
   sent an `escalate` with refs `["c_1", "tst_x"]` and no `b1`, plus an
   Architect `report` carrying `b1` from before the cap. The frontier
   reads `["architect"]`. This pins fault 1 and fault 2 together.
4. New: a Developer session on exhausted with `committed` 0, and the
   frontier still reads `["developer"]`. The seat is asked again, and the
   tick quarantine bounds it.
5. Seed rows as `tests/rota/test_predicates.py:1741` does, one `INSERT
   INTO sessions` with `wake_kind`, `wake_refs` and `committed`.

## The walk

One warm night with frames 81 and 80, from a worktree at frame 80's
closing commit. This frame's line in that night: `tick:exhausted` reaches
the Architect on the first tick after the Developer's exhausted session
commits, and the Vision Keeper after the Architect's.

## Out of scope, recorded for the next frame that meets them

- Every message a tick-woken session sends has `cause_id` NULL and its
  own `thread_id`. No thread joins the exhaustion to what the seats said
  about it, so `unresolved`'s climb, which reads a thread, cannot see it
  either. The schema allows a `tick` root (`rota/core/schema.sql:606`).
  A tick as a cause is a write-pipeline change and a frame of its own.
- The Developer at the cap on night 91 kept editing for 25 turns in
  `s190`, against its brief's last line. A stall bound was dropped at
  frame 37's grill (05:15). Not this frame.
- Three exhausted wakes per attempt at one rung (observed: night 91). The
  tick quarantine's cap, and not this frame.

## Price (reasoned: frame 81's actuals, in its status of 10:14)

Design review about 130k on Opus. Build 60k to 80k on Opus for route B.
Diff review about 100k on Fable. Gate 15k. The night is shared with frame
80 and priced there. About 320k in agents, walls apart.
