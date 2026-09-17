# The task stack

> Read what the model sent before trusting any number about it. What it
> lacked is a fact, which becomes a tool result, or a judgement, which
> becomes a measurement brought with a wording. The model is the last
> suspect (Roman, 2026-09-15).

The open work, in order, in one file that survives a context compaction
(Roman, 2026-09-14). Top frame first. A frame changes by push, pop, or a
status line. "Where are we" is answered from this file.

Rules:

1. Push a frame before starting it. Pop it when its "ends when" holds.
2. Write the status line with the date at every change and before any
   compaction.
3. Frames are mine to open, order and close. Roman's asks are frames too,
   marked "(Roman)". Roman can pop or reorder anything.
4. Linear. A frame that waits on another says which.
5. A frame is five lines: what, ends when, waits on, a pointer to the
   reasoning, and a dated status. The status line carries the peer name.
6. The session that holds a frame writes the first eight characters of
   its session id in the heading. A popped frame moves verbatim to
   `plans/archive/stack-<date>.md`.
7. Every conclusion carries a mark with a headline-long reason:
   (observed: where), (reasoned: why), or (ruled: why). Say which
   workflow it is about, the meta workflow or the rota workflow (ruled
   2026-09-16: a ruling and a judgement looked the same in prose).

## Stack

### 33. Finding 42: the code index refreshed after a commit (Roman, 2026-09-17) [3b4093c6]

- Rota workflow. Step 3 of the order. The code index is built at
  onboarding and never refreshed after a commit, so a batch's own
  symbols are invisible to later probes, and the touch prediction and
  sentence three's first prediction read a stale index (ruled: Roman,
  2026-09-17: the next frame; reasoned: `rota/COMPLETION.md`, "The order
  from here", step 3, a core fact that lands before breadth).
- Ends when, each line priced from the anchors, walls apart:
  1. A scope report names the index's writers and readers, what a
     commit changes, and the hook points for a refresh: 50k. Buys: the
     design names real paths, not guessed ones.
  2. A design record, reviewed before any code: 80k (the review 70k,
     the record 8k). Buys: the refresh's contract, per run or per
     worktree, is fixed before an implementer reads it.
  3. The refresh is built with a pinned test: after a commit, the
     index lists the batch's new symbols and a probe finds them: 110k
     (cold 80k, one resumed pass 30k). Buys: a batch's own symbols are
     visible to later probes and to the touch prediction.
  4. A diff review on a worktree at the commit, its fixes in: 110k
     (review 65k, second look 20k, fix pass 25k). Buys: the write
     pipeline change is read by a context that never wrote it.
  5. The gate green before each commit, the stale line read: 12k.
     Buys: no new red and no stale case hides behind the change.
  6. A full night on click from a worktree at the closing commit, its
     summary read: 20k in this context, about two hours wall. Buys:
     the seats on the delivery path see the refreshed index.
  Total: 382k in agents, about 120k in this context.
- Waits on: nothing. The scope agent runs now.
- Reasoning: `rota/COMPLETION.md`, "The order from here", step 3. The
  design record will be `plans/archive/index-refresh-design-2026-09-17.md`.
- Status 2026-09-17 14:25 (rota-02): pushed. The scope report is out to a
  reviewer-type agent, read-only, cap 60k.
- Status 2026-09-17 14:52 (rota-02): the scope report is in, 76k on the
  harness line against 50k priced and a 60k cap, 52 tool calls
  (observed: the harness usage). Saved as
  `plans/archive/index-refresh-scope-2026-09-17.md`. The design record
  is written: one refresh function with a main flag, three hooks, the
  freshness comparison skipped while a batch runs, five pinned tests.
  The judgement call, the skip against an area_hashes table, is in the
  record for Roman's read. Design review out, cap 80k.
- Status 2026-09-17 15:18 (rota-02): design review in, 78k on the harness
  line against 70k priced, 34 tool calls, eight points and three
  findings outside them. Two parts of the design overturned (observed:
  the reviewer's probes, recorded in the design record's last section):
  the freshness skip breaks an existing test and lifts on abandon, so
  an `area_hashes` table replaces it; no cancel path destroys a
  worktree, so hook 3 keys on abandon and defer. One high defect caught
  before code: `walk` tests the absolute path against `SKIP_DIRS`, so a
  worktree under `.rota` walks to nothing and the first commit would
  have emptied the index. Implementer out, pass 1, cap 120k, on Opus.
- Status 2026-09-17 15:24 (rota-02): implementer pass 1 in, 125k on the
  harness line against 80k priced and a 120k cap, 96 tool calls, 32
  minutes (observed: the harness usage). Twelve files, 322 insertions,
  seven pinned tests in `tests/rota/test_index_refresh.py`. Six
  deviations, all accepted (reasoned: each stated with its cause in the
  report): the missing-root refusal sits in `build`, two CLI tests
  create their directory first, `identity.py` declares the new table,
  `project_commit` is written only when non-empty, the area set comes
  from the pre-build snapshot. Gate by the implementer and by the
  assistant on the same tree: zero new reds, zero stale, 1886 passed,
  531 s each. Committed at 01b1d4b. Diff review next, on a worktree at
  that commit.
- Status 2026-09-17 15:30 (rota-02): diff review in on a worktree at
  01b1d4b, 91k on the harness line against 65k priced, 27 tool calls,
  eight points confirmed and seven findings, two high (observed: the
  reviewer's probes): a conflicted merge re-raises before the main
  refresh, so the index keeps describing a deferred worktree; and the
  three refresh helpers catch two exception types only, so a foreign
  error after a landed session runs session_fail on rows that are on
  record. Five low: the CLI traceback on a missing root, an empty
  area_hashes table reads as fresh after init_db on an old database,
  the failure record has no reader, the fixture records a gitlink, a
  duplicated helper. Fix pass sent to the same implementer, cap 60k,
  with four pinned tests and a gate run at its end.

### 4. Roman's order from here (2026-09-14 12:58) (Roman) [3b4093c6]

- (ruled: Roman's order, `rota/COMPLETION.md`, "The order from here") The
  road to the loop that merges cold on click. Steps: 1 the benchmark, 2
  routing a larger model, 3 finding 42, the code index refreshed after a
  commit, 4 the language seam, 5 breadth, the other two lineage
  repositories cold and then a non-Python repository, 6 the long-run
  noise test after sentence three merges, 7 ship the loop. Do not:
  rewrite the core, lower the cap, more nights on sentence two as if
  doors were the answer.
- Ends when: step 7 ships the loop.
- Waits on: the frames above it, one per step. Step 5 is frame 2's work.
- Reasoning: `rota/COMPLETION.md`, "The order from here", and frames 5
  to 15 in `plans/archive/stack-2026-09-16.md`.
- Status 2026-09-14: step 1 done; frame 8 decides step 2. Frames 5 to
  15 are in the archive.
- Status 2026-09-17 12:37 (rota-19): claimed by cc3d4e4e at 94511e3 for the
  grill with Roman, the first frame under the tooling chain. Step 2 is not
  needed (reasoned: `rota/COMPLETION.md`, update 2026-09-15 01:10, the 9B
  merged sentence two on night 70 with the doors of findings 66 to 73).
  Sentence three is unmerged: night 82 stuck on exhausted, 80 steps
  (observed: frame 13's close in `plans/archive/stack-2026-09-16.md`).
  The next step is Roman's ruling at the grill: finding 42, the seam, or
  breadth. Recommended: finding 42.
- Status 2026-09-17 13:52 (rota-02): claimed by 3b4093c6, the same session forked (ruled:
  Roman, 2026-09-17). The one order: seven steps as COMPLETION.md gives
  them, with finding 42 as step 3 (observed: the stack's list had six).
  Step 1 done, step 2 not needed. The next frame is step 3 on Roman's
  word at the grill. Frames 23, 24, 25, 28 and 31 closed by ruling; the
  first build frame's closing status carries their measurements.

### 2. The gauntlet on the lineage (goals 3 and 10)

- (ruled: goals 3 and 10 of the plan) Three lineage repos, three sentences each, unattended. Click sentence
  one merges (nights 49, 50). Sentences two and three do not yet.
- Ends when: the lineage is walked and every fault is a door or a case.
- Waits on: frame 4, whose step 5 is this frame's breadth.
- Reasoning: `rota/COMPLETION.md`, goals 3 and 10.
- Status 2026-09-16: open behind frame 3. The latest nights are frames
  11 to 13 in `plans/archive/stack-2026-09-16.md`.
- Status 2026-09-17 13:52 (rota-02): sentence two merged on night 70. Sentence three is
  unmerged: night 82 stuck on exhausted at 80 steps (observed: frame 13's
  close). Three partials ride the gauntlet, A7, D3 and A1's cold walks
  (ruled: Roman, 2026-09-17). The night summary owes three lines for
  them: a stray touch judged, a failed verdict chained, a contest
  landed. A small frame on the night script, priced when the order's
  frames run.
- Status 2026-09-17 14:12 (rota-02): D3's owed night does not exist yet
  (observed: a reviewer probe of the night databases, 24k). Nights 81
  and 82 hold no verdicts row of any result: the Critic woke on the
  challenge tick only and never reached the review tick, and the
  Developer read an empty verdicts table three times on night 82. Rota
  workflow. The "failed verdict chained" line of the night summary is
  the measurement that is missing.
- Status 2026-09-17 14:25 (rota-02): the lineage is tips, click and icalendar
  (ruled: Roman, 2026-09-17). Step 5 of the order, breadth cold, walks
  tips and icalendar with what exists.

### 1. The end state (plan agreed 2026-09-10)

- (ruled: the destination, agreed 2026-09-10) A careful person runs rota alone on a small Python repository and
  gets a merged change they can read. Honest about where small models
  stop. Ten goals in COMPLETION.md: 1, 2, 7, 9 done; 4 and 8 measured
  and ongoing; 3 and 10 are frame 2; 5 and 6 fed by it.
- Ends when: every partial in COMPLETION.md's core section is built,
  click and two more lineage repositories merge cold, the register is
  green or attributed on the shipped profile, and Roman declares
  finished (ruled: Roman, 2026-09-17: the core section stays the
  definition of core).
- Waits on: frame 2.
- Reasoning: `rota/COMPLETION.md`, and `plans/composition.md`, Purpose.
- Status 2026-09-16: the bottom frame. Open.
- Status 2026-09-17 13:52 (rota-02): the partials are banded in COMPLETION.md's core
  section (ruled: Roman, 2026-09-17). Four small frames and two
  campaigns push above this frame when frame 2 closes. B5 struck as
  built, F1 parked.

## Parked

- From frame 27: `rota/core/sandbox.py` keys `_CALL_LOG` by `id(ctx)` and
  drains it on commit only, so a dead address reused by CPython can flip
  `test_arc_global_negative_no_writes_by_non_owners`. Whether a refs-only
  write lifts a quarantine (it does not today).
- From frame 30's design review (observed: the reviewer's read of
  `tests/rota/conftest.py`): the file defines `pytest_configure` twice,
  the second at line 45 shadows the first at line 25, so the serial
  guard in the first is dead. `rota_serial_plugin` still enforces it.
  Meta workflow. Not in frame 30.
- From frame 30: the suite's temp root was on C: before the gate, so
  the SSD setting moved nothing. The remaining HDD reader is
  `tests/rota/cassettes.db` on D:. A read-only copy on C: for replay is
  the next lever, untested. Meta workflow.
- From frame 29's scope report (observed: `rota/onboarding/boot.py:241`,
  `:262`, `:265`): `refresh_constraint_zero` writes `refs` as raw SQL at
  boot, outside `stage_ref` and the write pipeline: no receipt, no version
  bump. Rota workflow. The refs-scope report predicted the path.
- From the same report (observed: `rota/testkit/obligations.py:59-105`):
  `l2()` names 73 modes and 80 `.tools` files exist; `terminologist/
  unresolved` runs in a recorded case and is in no L2 row. Rota workflow.
- From frame 29's design review (observed: `graph.json` and `REGISTRY`):
  `batches.judge_touch` is the one registered verb with an underscore;
  `problem.set approval` and `verdicts.claim encodes` carry a space. Rota
  workflow.
- From frame 29's second look (observed: `rota/tools/talk.py:72`, `:80`):
  `talk.py` writes `entries` and `messages` with raw SQL on the run
  database, outside `ctx.writes`, no receipt. A third raw write path
  beside `refresh_constraint_zero`. Rota workflow.
- Finding 42: the code index is never refreshed after a commit.
- Finding 64: vacuous ratified constraints at the structural review.
- Finding 67: a wrong fix passes the fix case; the case checks the act,
  not the test's verdict.
- The DECISIONS rulings draft waits on Roman's read.
- The cassette publish is Roman's, held. The staged snapshot of 16:13
  carries the false 5/5 rows; the next pack replaces it.
- The Ollama 300 s timeout on the 14B if it returns to a desk.
- Post-core list in COMPLETION.md.
- From the lost-work audit (`plans/archive/lost-work-audit.md`, rows at
  lines 20 and 34): the reference drift predicate that DECISIONS.md
  promises and no code reads, and the law-13 schema test that finds no
  date column. Neither is in COMPLETION.md.
