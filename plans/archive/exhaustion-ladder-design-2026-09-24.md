# Design record: the exhaustion ladder never climbs past the Developer (frame 79)

Written by the assistant, session 4fe8b80c, on 2026-09-24 10:21, for a
design review before any code. Revision 2 at 10:28 folds the design
review's nine points and four findings (observed: the reviewer on Opus
5.5, 94.7k on the harness line, 35 tool calls, 3.6 minutes). Meta
workflow for the build. Rota workflow for the fault. The tree is
`48713eb`.

## The fault (observed: `.rota/clickI_night91_walk1.db`, 2026-09-24 10:17)

- Eight sessions woke on `tick:exhausted`, and every one is the Developer.
  `s169`, `s170` and `s173` woke at attempt 10 of 10. `s176`, `s177` and
  `s180` woke at attempt 11 of 10. `s189` and `s190` woke at attempt 12
  of 10. Every row carries `wake_refs` `["bg_1"]`, `trigger_msg` NULL and
  `committed` 1.
- The Developer sent eight messages: four `challenge` to the Tester
  (`m65`, `m66`, `m67`, `m70`), two `escalate` to the Architect (`m68`,
  `m76`) and two `question` to the Vision Keeper (`m72`, `m74`). Every
  `body_refs` lists criteria and test ids. None lists `bg_1`. Every
  `cause_id` is NULL and every `thread_id` is the message's own id. A
  tick has no trigger message, so the send writes `cause_id: ctx.trigger`
  as None (`rota/core/sandbox.py:1785-1793`). The `tool_calls` table maps
  the sends to `s169`, `s170`, `s177`, `s180` and `s189`, all exhausted
  sessions (observed: the design review's probe).
- Three messages name `bg_1`, and all three come before the cap. `m57` is
  the Architect's report to the Liaison on the batch's cut, at message
  seq 58. `m61` is the Liaison's present. `m62` is the principal's
  converse. Messages and sessions count on separate sequences.
- `_next_rung` (`rota/core/predicates.py:906-920`) reads `sent`, the
  `from_role` of every message whose `body_refs` contains the batch id.
  On night 91 that set is architect, liaison and principal. The first
  role in `LADDER` not in the set is the Developer, on every pass.
- The `LIKE '%bg_1%'` at `predicates.py:915` has no quotes, so it also
  matches `bg_10` to `bg_19` (observed: the review's probe, `'["bg_10"]'
  LIKE '%bg_1%'` returns 1). The precedents quote the id.

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
   `m57`, and the next rung would be the Vision Keeper (observed: the
   review's ladder probe on the night's rows). A report on the cut, sent
   before the cap, would count as the Architect's answer to the
   exhaustion. A fix to the writer alone skips one rung.

This is the shape of batch A's key: the writer and the reader name
different fields. The field the runner stamps by construction is
`sessions.wake_refs`. The committed row is written at
`rota/core/runner.py:3053` and `rota/core/db.py:552-562`, with
`committed` 1. A failed session writes its row at `runner.py:3120` and
`db.py:896-900`, with `committed` 0. All eight night-91 rows carry the
batch id. Two readers in the tree already ask "was this rung asked" from
that column: `_repair_attempted` (`predicates.py:1039-1042`) and the
batch-start stall guard (`rota/core/scheduler.py:322-326`). Both read
`wake_kind`, `committed = 1` and a quoted `wake_refs LIKE`.

The briefs read the ladder as "asked". The Architect's exhausted brief
opens with "Developer has already been asked and had nothing to route,
which is itself the finding" (`prompts/architect/exhausted.md`). No brief
ties the climb to a message (observed: the review's read of the three
`exhausted.md` briefs).

**One ruled sentence promises the message reader.** Law 6 in
`rota/LAWS.md:197-199`: "The rung is derived from what has already been
sent about the batch, not stored: a stored rung is a second record that
can disagree with the messages that *are* the escalation." The
`exhausted` docstring at `predicates.py:879-881` says the same. Route B
changes that sentence, so route B is a ruling for Roman.

## The two routes of the ends-when line

### Route A, the writer: a message from a batch-held seat carries the batch id by construction

At the send (`sandbox.py:1785`), when `ctx.batch_id` is in
`ctx.wake_refs` and the verb climbs (`escalate`, `question`, `challenge`,
`report`), add `ctx.batch_id` to `body_refs`. Stamp, and never refuse: a
refusal of an argument loops a 9B seat (observed: frame 81, `c5da552`).

- What it buys: `_next_rung` and Law 6 stay as they are. Messages about
  a batch are findable by the batch id. The report door becomes a stamp.
- What it costs, from the review's reads:
  - Fault 2 stays. On night 91's rows the climb skips the Architect and
    wakes the Vision Keeper, so the reader changes anyway.
  - The Architect's usual exit is `model.amend` then `msg.answer_developer`.
    `answer` is not a climbing verb, so the Architect never enters `sent`
    and is woken again until the tick cap (PLAUSIBLE, the review's
    finding 2).
  - The duplicate guard at `sandbox.py:1278` goes blind. The stamp lands
    after the guard, so a stored `body_refs` holds the batch id and the
    new refs do not, and the exact-equality test never matches again. On
    night 91 `s189` sent `escalate_architect` twice on the same refs, and
    this guard is what stops that (CONFIRMED, the review's point 7). The
    overlap guard at `:1309-1318` reads prior refs too. `:1233` and
    `:1453` do not change.
  - `finding_violated` (`predicates.py:1181-1183`) and `touch_mistaken`
    (`:1919-1921`) go quiet while an open Developer `escalate` carries the
    batch id. A stamp on every escalate from an exhausted session quiets
    both (CONFIRMED by reading, the review's finding 3).
  - `body_refs` has 99 readers (observed: the map tool, 2026-09-24 10:18).
    The write pipeline is touched, so the diff review must probe the
    guards. The fixtures that seed messages need the id.
- Price: build about 140k on Opus (frame 81's cold pass in the same file,
  137k), diff review about 110k on Fable.

### Route B, the reader: `_next_rung` reads the sessions the exhaustion opened

`_next_rung` derives `asked` from `sessions`: the roles with a row whose
`wake_kind` is `tick:exhausted`, `committed` is 1 and `wake_refs` holds
the quoted batch id, `'%"bg_1"%'`. The first role in `LADDER` not in
`asked` is the rung. The docstring's question, "who has not yet been
asked about this batch", becomes literal. Law 6's sentence and the two
docstrings change to say the sessions, after Roman's ruling.

- What it buys: both faults close at the one site the frame names. The
  climb is one committed exhausted session per rung: Developer,
  Architect, Vision Keeper, then quiet at the top. There the Vision
  Keeper's exhausted mode reports to the Liaison, and the report door
  demands the batch id, unchanged. No brief changes, so no case
  re-records (reasoned: the stale line keys on the briefs a case reads).
  The Architect's report on the cut no longer counts as its answer.
- The claim holds the seat until it commits. `loop.step`
  (`rota/core/loop.py:275-279`) skips a role that holds a claim, and
  `run_session` runs in the foreground inside `step`, so no frontier is
  computed while a session runs (CONFIRMED, the review's point 2).
- A session that fails writes `committed` 0 and releases the claim, and
  the next pass wakes the same rung again under the key
  `developer|tick:exhausted|bg_1`. `quarantine_stalled`
  (`scheduler.py:1489`) sets `quarantined` on that key at
  `tick_attempt_cap`, 3, and the count resets when the wake leaves the
  frontier (observed: the review's read). A quarantined key is deleted
  when a commit writes a row its refs name (`db.py:500`). That revive is
  why night 91 shows 3, 3 and 2 wakes across attempts 10, 11 and 12: each
  new head commit revived the key (reasoned: the rule and the counts; the
  night's counter ends at attempts 3, quarantined 0). Under route B the
  first committed Developer session moves the rung, so the counter no
  longer decides the climb.
- A rung that fails three times sticks. No committed row exists, the key
  is quarantined, and `quarantined` reports it to the Liaison, as Law 6
  allows. Today's reader behaves the same (PLAUSIBLE, the review's
  finding 4). No code change.
- A Developer that was asked and kept editing counts as asked. The
  brief's last line already says "Do not spend another attempt on the
  code".
- **The open-answer gap, and a guard.** Nothing quiets `exhausted` while
  an answer about the batch is open (CONFIRMED, the review's point 3).
  After the Architect amends and answers the Developer, the next pass
  wakes the Vision Keeper while the answer is still open, under a brief
  that says "Architect could not place it". Today's reader does the same
  when the Architect's message carries the batch id. The Vision Keeper's
  brief offers `problem.assert`, which drops the approval and stops the
  batch. So the guard is part of route B: `exhausted` returns no wake
  while a message to the Developer is open (reasoned: the Developer is
  single-instance and one batch runs, so an open message to it is the
  batch's, and the seat acts on it before the ladder climbs). An open
  message drains, because it wakes the Developer, and a message past its
  attempt cap is quarantined and no longer open, so the guard cannot hold
  the ladder for ever.
- A message alone no longer climbs the ladder. A Developer that
  escalates with the batch id in refs and no exhausted session has not
  been asked at the cap. That is the semantic change Law 6's amendment
  states.
- Price: build 60k to 80k on Opus (one query, one guard, two pins
  flipped, three added, two docstrings), diff review about 90k on Fable,
  gate 15k.

### Recommended: route B, with Law 6 amended (reasoned: it closes both faults at the one site the frame names, and it changes no brief)

Route A leaves fault 2 open, stalls at the Architect because `answer` is
not stamped, blinds one duplicate guard and quiets two predicates. Route B
reads the field the runner stamps by construction, with two precedents in
the tree and the briefs' own wording. The review built route B too.

### The ruling (for Roman)

Law 6's sentence, "The rung is derived from what has already been sent
about the batch, not stored: a stored rung is a second record that can
disagree with the messages that *are* the escalation", becomes: "The rung
is derived from the sessions the exhaustion has opened, not stored: a
stored rung is a second record that can disagree with the wakes that
*are* the escalation." The reason the sentence gives, no second record,
stays true. The record it names changes from the messages to the
sessions, because the sessions carry the batch id by construction and
the messages carry what the model passed.

## The pinned tests (route B), in `tests/rota/test_delivery.py`

A session row needs `id`, `role`, `seq`, `wake_kind`, `wake_refs` and
`committed` set (observed: `rota/core/schema.sql`, the review's point 6;
`committed` defaults to 0). The pattern is `tests/rota/test_predicates.py:1741`.

1. `test_the_ladder_climbs_one_rung_at_a_time`: seed a committed Developer
   session with `wake_kind` `tick:exhausted` and `wake_refs` `["b1"]`, and
   the frontier reads `["architect"]`. Seed the Architect's, and it reads
   `["vision_keeper"]`.
2. `test_the_ladder_stops_at_vision_keeper`: three sessions, one per rung,
   and no `tick:exhausted` wake.
3. New, night 91's shape: one committed Developer session on exhausted,
   one `escalate` message with refs `["c_1", "tst_x"]` and no `b1`, and
   one Architect `report` carrying `b1` from before the cap, each message
   seeded as `test_delivery.py:382` does. The frontier reads
   `["architect"]`. This pins fault 1 and fault 2 together.
4. New: a Developer session on exhausted with `committed` 0, and the
   frontier still reads `["developer"]`.
5. New: a committed Developer session on exhausted and one open message
   to the Developer, and the frontier holds no `tick:exhausted` wake.
   Mark the message answered, and it reads `["architect"]`.
6. New: a committed Developer session on exhausted for `b10`, and the
   frontier for `b1` still reads `["developer"]`. This pins the quoted
   `LIKE`.

## The walk

One warm night with frames 81 and 80, from a worktree at frame 80's
closing commit. This frame's line in that night: `tick:exhausted` reaches
the Architect on the first tick after the Developer's exhausted session
commits, the Developer acts on the Architect's answer before any higher
rung wakes, and the Vision Keeper wakes after the Architect's session
when the batch still fails.

## Out of scope, recorded for the next frame that meets them

- Every message a tick-woken session sends has `cause_id` NULL and its
  own `thread_id`. No thread joins the exhaustion to what the seats said
  about it, so `unresolved`'s climb, which reads a thread, cannot see it
  either. The schema allows a `tick` root (`rota/core/schema.sql:606`).
  A tick as a cause is a write-pipeline change and a frame of its own.
- The Developer at the cap on night 91 kept editing for 25 turns in
  `s190`, against its brief's last line. A stall bound was dropped at
  frame 37's grill (05:15). Not this frame.
- The revive rule at `db.py:500` deletes a quarantined tick when any
  commit writes a row its refs name. On night 91 it revived the exhausted
  key at every head commit, and it revives the criteria key that frame 80
  is about. Frame 80's read.
- Three other predicates match a batch id without quotes, so `b1`
  matches `b10`: `reopen` (`predicates.py:861`), `finding_violated`
  (`:1195`) and `touch_mistaken` (`:1933`), each with
  `m.body_refs LIKE '%' || b.id || '%'` (observed: the diff review of
  `a75206d`, by reading, 2026-09-24). `tests_missing` at `:701` quotes
  the id. One line each, and a pin, for the frame that next touches
  those predicates.
- The Architect's exhausted brief opens with "Developer has already been
  asked and had nothing to route". Under route B the Developer may have
  routed, received an answer and tried it, and the batch still stands at
  the cap. The sentence is imprecise and not false to the seat's action.
  A brief change re-records the Architect's exhausted cases, so it waits
  for a frame that touches that brief (reasoned: the diff review's
  finding 4, low).
- The window before the Architect's answer: with the Developer's
  exhausted session committed and its `escalate` open, the Architect's
  message tip and its `tick:exhausted` wake are ready in one pass. The
  tip runs first by band, traffic before fix, and the Architect's claim
  blocks the tick during that session (observed: the diff review, by
  reading). Pass 3 pins that order.

## Price (reasoned: frame 81's actuals, in its status of 10:14)

Design review: 94.7k on Opus, actual. Build 60k to 80k on Opus for
route B. Diff review about 90k on Fable. Gate 15k. The night is shared
with frame 80 and priced there. About 200k in agents after the review,
walls apart.
