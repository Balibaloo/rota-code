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

### 29. The map: a query tool over the code (Roman, 2026-09-17) [90522022]

- Meta workflow. `rota/tools/map.py`: an `ast` pass over `rota/` plus a
  regex over the SQL literals, joined with `graph.json` and the `.tools`
  files, cached under `.rota/` by the tree's hash, never committed. It
  answers `fn`, `table`, `mode` and `file` queries in a few lines each:
  file and line, callers, writers and readers per column, ops per mode.
  Separate from the onboarding indexer. One line in the assistant's brief:
  ask the map before you grep (ruled: Roman queued it; observed: the scope
  agent made 96 tool calls, most of them finding where things were, and
  every later agent found them again).
- Ends when: the tool exists with tests that pin known facts (the writers
  of `refs`, the readers of `item_provenance`), the line is in `CLAUDE.md`,
  and one frame's agents have used it with their tool-call counts on the
  stack beside frame 21's.
- Waits on: frame 27's verdict for who builds it. Session B.
- Reasoning: `plans/tooling-flow.md` first, the plan and the chain's
  rules. Then `plans/archive/refs-scope-2026-09-16.md` as the ground truth.
- Status 2026-09-17 01:45 (rota-b9): queued by Roman, unclaimed.
- Status 2026-09-17 09:52 (rota-51): claimed by hand-off from 32a42b78 at
  f9ac0da. Frame 27's verdict is in: the implementer type on Opus builds,
  the reviewer type on Opus reads the design. Prices from the anchors
  (reasoned: frame 30's harness lines): design review 70k; first
  implementer pass 90k for the tool and its tests; one fix pass 40k; the
  brief line costs no agent; the tool-call count comes from frame 24's
  agents. Estimate 200k, walls apart.
- Status 2026-09-17 10:01 (rota-51): unclaimed (ruled: Roman, 2026-09-17:
  session fa029276 loaded the agent types before their edits, so its
  agents run stale prompts). The prices stand for the next claimant.
- Status 2026-09-17 10:09 (rota-99): claimed at 9baf02d. Roman assigned it through
  session 32a42b78, relayed by rota-5d (ruled: Roman, 2026-09-17: 28's
  anchors first, then 29, then 24). This session started after 6140848
  and holds the types. rota-51's prices stand: 200k, walls apart.
- Status 2026-09-17 10:10 (rota-99): a no-tool reviewer quoted e407e5d's command
  line, so a type's body is live at spawn and only the type list is
  fixed at session start (observed: the probe, 9.6k). The unclaim reason
  of 10:01 does not hold for body edits. Scope report requested from a
  reviewer on Opus, cap 80k; the design record follows it.
- Status 2026-09-17 10:22 (rota-99): scope report in, 125k against the 80k cap and
  83 tool calls (observed: the harness line; the cap did not hold because
  the agent counted output only). Fifteen findings, four change the
  design. Design record: `plans/archive/map-design-2026-09-17.md`. One
  deviation from the frame's words: no cache, a full parse costs 0.47 s
  and the obvious key misses unstaged edits (observed: the report's
  probes). Tool-call baseline beside the 96: frame 30's agents made 31,
  36, 30, 7, 23 and 9 calls (observed: the harness lines). The 96 is
  unsourced in the tree. Design review next.
- Status 2026-09-17 10:31 (rota-99): design review in, 78k and 31 tool calls
  (observed: the harness line), thirteen findings, three high: a
  verb-prefix gate misses a reader the tests pin, one of three dicts is
  a comprehension with artefact values, and 119 `msg.*` tool lines join
  to the graph's message edges and not to the registry. The record is
  amended. Implementer next.
- Status 2026-09-17 11:09 (rota-99): the map is in (33dbaa3), 14 tests, `table refs`
  0.87 s and `fn stage_ref` 0.93 s (observed: the implementer's `time`).
  The brief line is in `CLAUDE.md` and the three definitions (128c68c).
  Implementer pass: 114k, 55 tool calls (observed: the harness line).
  The assistant's gate run before the commit: zero new reds, 1844
  passed, 491.8 s. Tool-call counts beside the unsourced 96: scope 83,
  design review 31, implementer 55. `table refs` answers in 28 lines
  and shows both write paths. Diff review on a worktree at 33dbaa3 next.
- Status 2026-09-17 11:25 (rota-99): diff review in, 74k and 25 tool calls, eight
  findings, two high: the five `cite` ops joined no definition, and a
  qualified `fn` query printed zero callers. Fix pass by the resumed
  implementer: 46k, 36 tool calls, 22 tests, the gate zero new reds,
  1852 passed, 483.5 s (observed: the harness lines and the gate). Fix
  commit c780a6f. `mode` now 0.15 s. Second look on a worktree at
  c780a6f next.
- Status 2026-09-17 11:28 (rota-99): second look in, 23k and 10 tool calls: all
  eight fixes confirmed, the false reader count is 0, no false site from
  `rota/tools/`. Three low residuals: a shared name repeats its caller
  list, the op join by line admits no miss, the record said 68 files.
  The first two go to the implementer as a short pass, the record is
  amended. After the commit the frame goes to validating: the last
  ends-when line, agents using the map with their counts, is measured
  by frame 24's agents.
- Status 2026-09-17 11:31 (rota-99): validating. The tool is in (33dbaa3, c780a6f,
  387c7f7), 22 tests, the line is in `CLAUDE.md` and the three
  definitions (128c68c). Estimate against actual, walls apart: 200k
  estimated; scope 125k, design review 78k, implementer 173k over three
  passes (114k, 46k, 13k), diff review 97k over two (74k, 23k), the
  assistant's gate run 6k: 479k (observed: the harness lines). The
  estimate missed the scope report and the second passes. Tool calls
  beside the unsourced 96: 83, 31, 55, 25, 36, 10, 14. Waits on: frame
  24's agents using the map, with their counts.
- Status 2026-09-17 11:44 (rota-99): no cache (ruled: Roman, 2026-09-17: no cache is
  good if it is so cheap). The deviation from the frame's words is
  closed. A cache is its own frame if a query ever passes two seconds.

### 24. Scripts for mechanical work, and a sweep tool (Roman, 2026-09-17) [90522022]

- Meta workflow. Two lines in the assistant's brief: a change that is the
  same edit in more than three files is a script, written with the Write
  tool, run, its touched files printed, and the diff read once for the
  judgement cases; a sub-agent only when the brief allows it, with a token
  cap and its usage in the report. One tool: `rota/tools/sweep.py`, a glob
  plus a regex or a `libcst` transform, bytes with each file's own line
  endings, a diff stat out (ruled: Roman queued it from the post-mortem;
  observed: 48 test files were swept by hand through four sub-agents).
- Ends when: the lines are in `CLAUDE.md`, the tool exists with a test that
  a CRLF file and an LF file keep their endings, and one frame's sweep ran
  through it.
- Waits on: frame 32 for the lines; frame 27's verdict for who builds
  the tool. Session B, after 29.
- Reasoning: `plans/tooling-flow.md` first, the plan and the chain's
  rules. Then `plans/archive/postmortem-frame21-2026-09-16.md`, change 1.
- Status 2026-09-17 01:22 (rota-b9): queued by Roman, unclaimed.
- Status 2026-09-17 11:31 (rota-99): claimed at 387c7f7 (ruled: Roman, 2026-09-17,
  24 after 29). Both waits discharged: the lines landed in frame 32, the
  verdict is in. Prices from the anchors: design review 75k, implementer
  130k over two passes, diff review 95k over two, the assistant's gate
  run 6k: 310k, walls apart. The last ends-when line, one frame's sweep
  through it, is measured by the first sweep after the tool. Design
  record: `plans/archive/sweep-design-2026-09-17.md`. libcst is not
  installed (observed: `pip show`), so the transform path is a hook, not
  a dependency.
- Status 2026-09-17 11:40 (rota-99): design review in, 66k and 23 tool calls, ten
  findings, six high: `fnmatch` lets `*` cross `/`, the mixed-ending
  rule contradicted itself, a class check passes on a corrupt file, the
  hook's LF contract was unenforced, the replacement template eats a
  backslash, and the sample repo is CRLF. The record is amended. First
  map use by an agent: 5 map calls against 4 greps (observed: the
  reviewer's count; frame 29's last line). Implementer next.

### 23. Resume one implementing agent per frame (Roman, 2026-09-17)

- Meta workflow. Five lines in the assistant's brief: one implementing
  agent per frame, resumed by message; the resume carries the tree's delta
  and a required re-read of the files to edit; the writer never reviews;
  a cap near 350k with a where-things-are note for a fresh agent; each
  pass's tokens in the status line beside today's cold cost, about 300k,
  and the rule stops if a resumed pass costs as much (ruled: Roman queued
  it from the post-mortem; reasoned: the peer hand-off applied to an agent).
- Ends when: the lines are in `CLAUDE.md`, Roman has read them, and one
  frame has run under them with its per-pass tokens on the stack.
- Waits on: frame 32 for the lines; ends on the first frame that runs
  under them, frame 4.
- Reasoning: `plans/archive/postmortem-frame21-2026-09-16.md`, change 1.
- Status 2026-09-17 01:17 (rota-b9): queued by Roman, unclaimed.

### 25. Two reviews per frame: the design, then the diff (Roman, 2026-09-17)

- Meta workflow. Two lines in the assistant's brief: a design review on
  the scope report and the design record before any code, about 100k,
  and one read-only diff review at the frame's end on a worktree at the
  commit, before the walk, for a frame that touches the write pipeline,
  the schema or a predicate; fewer, sharper points per review (ruled:
  Roman queued it; observed: three diff reviews cost 731k and two of 25
  findings mattered; reasoned: the saving is about 350k a frame, the
  smallest of the post-mortem's changes).
- Ends when: the lines are in `CLAUDE.md`, Roman has read them, and one
  frame has run under them with both reviews' tokens on the stack.
- Waits on: frame 32 for the lines; measured by frame 4.
- Reasoning: `plans/archive/postmortem-frame21-2026-09-16.md`, change 3,
  and the post-mortem conversation of 2026-09-17.
- Status 2026-09-17 01:26 (rota-b9): queued by Roman, unclaimed.

### 28. A price on every ends-when line (Roman, 2026-09-17)

- Meta workflow. One line in the assistant's brief: at the grill, each
  ends-when line carries a token price from the anchors and the behaviour
  it buys; a line with a price and no behaviour becomes its own frame
  below; the closing status writes the actual beside the estimate, walls
  counted apart. Six anchor rows in `plans/operating-facts.md`, dated by
  frame, re-derived from the last three frames whenever a frame that
  changed the workflow closes (ruled: Roman queued it; observed: frame 21's
  drop cost about a million and bought no behaviour, unpriced).
- Ends when: the line is in `CLAUDE.md`, the anchors are in the facts,
  and one frame has closed with actual beside estimate.
- Waits on: frame 32 for the line; measured by frame 4.
- Reasoning: `plans/archive/postmortem-frame21-2026-09-16.md`, change 2,
  and the post-mortem conversation of 2026-09-17.
- Status 2026-09-17 01:42 (rota-b9): queued by Roman, unclaimed.
- Status 2026-09-17 10:09 (rota-99): the six anchor rows are in the register
  section of `plans/operating-facts.md` (bbb2f1d or its amend), from
  frames 26 and 30. Frame 30 closed with actual beside estimate. The
  frame stays open until frame 4 runs under the line (ruled: Roman,
  `plans/tooling-flow.md`, the measuring frames close on frame 4).

### 31. A walk closes a frame that touches the seats (Roman, 2026-09-17)

- Meta workflow. Two lines in the assistant's brief: a frame that touches
  the seats, the briefs, the write pipeline or a predicate ends on a walk
  that covers the phases it touched, onboarding for an onboarding change,
  a full night for the delivery path or when in doubt; the walk runs from
  a worktree at the frame's closing commit, since briefs are read at every
  wake, and the frame stays open as validating while the next frame
  starts in the main checkout (ruled: Roman, 2026-09-17; observed: frame
  21 passed every suite run and the walk found a seventy-night defect).
- Ends when: the lines are in `CLAUDE.md` and one frame has closed on a
  walk with its result, steps and asks, on the stack.
- Waits on: frame 32 for the lines; measured by frame 4.
- Reasoning: `plans/archive/postmortem-frame21-2026-09-16.md`, change 4,
  and the post-mortem conversation of 2026-09-17.
- Status 2026-09-17 01:52 (rota-b9): queued by Roman, unclaimed.

### 4. Roman's plan for sentence two (2026-09-14 12:58) (Roman)

- (ruled: Roman's plan) Stop band-aiding the stdin door. Steps: 1 benchmark, 2 route a larger
  model where it passes, 3 language seam, 4 breadth (two lineage repos
  cold, then a non-Python repo), 5 long-run noise test after sentence
  three merges, 6 ship the loop. Do not: rewrite the core, lower the
  cap, more nights on sentence two as if doors were the answer.
- Ends when: step 6 ships the loop.
- Waits on: the frames above it, one per step.
- Reasoning: `rota/COMPLETION.md`, "The order from here", and frames 5
  to 15 in `plans/archive/stack-2026-09-16.md`.
- Status 2026-09-14: step 1 done; frame 8 decides step 2. Frames 5 to
  15 are in the archive.

### 3. Click sentence two (nights 50 to 60)

- (observed: nights 50 to 60, findings 36 to 64) Every night stuck; each became a door or a brief line (findings 36 to
  64). Night 60: the 14B Developer timed out at its first wake; sentence
  three then ran once, quiet, no merge.
- Ends when: one night merges sentence two.
- Waits on: frame 4.
- Reasoning: findings 36 to 64, and frames 8 to 13 in
  `plans/archive/stack-2026-09-16.md`.
- Status 2026-09-14: behind frame 4.

### 2. The gauntlet on the lineage (goals 3 and 10)

- (ruled: goals 3 and 10 of the plan) Three lineage repos, three sentences each, unattended. Click sentence
  one merges (nights 49, 50). Sentences two and three do not yet.
- Ends when: the lineage is walked and every fault is a door or a case.
- Waits on: frame 3.
- Reasoning: `rota/COMPLETION.md`, goals 3 and 10.
- Status 2026-09-16: open behind frame 3. The latest nights are frames
  11 to 13 in `plans/archive/stack-2026-09-16.md`.

### 1. The end state (plan agreed 2026-09-10)

- (ruled: the destination, agreed 2026-09-10) A careful person runs rota alone on a small Python repository and
  gets a merged change they can read. Honest about where small models
  stop. Ten goals in COMPLETION.md: 1, 2, 7, 9 done; 4 and 8 measured
  and ongoing; 3 and 10 are frame 2; 5 and 6 fed by it.
- Ends when: the destination holds and Roman declares finished.
- Waits on: frame 2.
- Reasoning: `rota/COMPLETION.md`, and `plans/composition.md`, Purpose.
- Status 2026-09-16: the bottom frame. Open.

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
