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

### 26. Agent types with the tools they use (Roman, 2026-09-17) [90522022]

- Meta workflow. Three definitions in `.claude/agents/`: implementer
  (Read, Edit, Write, Bash, Grep, Glob), reviewer (Read, Bash, Grep, Glob),
  sweeper (Bash, Write, Read), each with its model and a standing prompt
  that carries the repo's rules: line endings, the suite command, the
  report shape (ruled: Roman queued it; observed: a general-purpose agent
  starts near 50k of schemas, fourteen of them a day; reasoned: about 400k
  a day at that count, more with a cheaper model on the sweeper).
- Ends when: the three files exist, one agent of each type has run a
  trivial task and its reported floor is on the stack beside the 50k of
  the general-purpose type, and one frame has used them.
- Waits on: nothing. Session A, after 32.
- Reasoning: the post-mortem conversation of 2026-09-17, the `/context`
  reading of frame 21's session.
- Status 2026-09-17 01:28 (rota-b9): queued by Roman, unclaimed.
- Status 2026-09-17 03:16 (rota-8c): claimed. Models from frame 27's verdict:
  Opus for the implementer and the sweeper, the reviewer inherits Fable
  and takes Opus per call when the points are sharp.
- Status 2026-09-17 03:21 (rota-8c): the three files are in (6140848). Wall:
  the Agent tool loads its type list at session start, so this session
  cannot spawn the new types (observed: the tool's error names only the six
  built-in types). Anchor measured today: a general-purpose agent on Haiku
  with one tool call cost 33,741 tokens (observed: the harness usage line).
  Next: a fresh `claude -p` process from the repo root, if the CLI is on
  this box, else the floors wait for the next fresh session.
- Status 2026-09-17 03:25 (rota-8c): floors measured (observed: the modelUsage
  rows of five fresh `claude.exe -p` runs, a Haiku main that calls the
  Agent tool once; the typed agent's first-turn cache creation is its
  floor). General-purpose on Opus: 38.3k. Implementer: 11.4k. Reviewer:
  13.3k, of which about 2.5k is the file it read. Sweeper: 8.9k. The
  types start at a quarter to a third of the general-purpose cost
  (reasoned: 9k to 13k against 38k). The CLI is the VS Code extension's
  `resources/native-binary/claude.exe`, version 2.1.258. Open: one frame
  has to use the types, and that needs a session started after 6140848.
- Status 2026-09-17 03:29 (rota-8c): Roman started session 90522022 after
  6140848, so its Agent tool holds the types. Frames 26 and 30 go to it by
  hand-off: 30 builds the gate through the implementer type, and that run
  closes 26 (ruled: Roman, 2026-09-17, the new session is the answer to
  the blocked question).
- Status 2026-09-17 03:34 (rota-99): claimed by hand-off from fa029276 at be4f512.
  Frame 30 is the first frame to use the types: a reviewer pass on the
  design record, one implementer pass, a reviewer pass on the commit.

### 30. The gate: the suite in five lines (Roman, 2026-09-17) [90522022]

- Meta workflow. `rota/tools/gate.py`: runs the suite with `--tb=no -rf`,
  stores a baseline once with its commit hash, and prints five lines: the
  summary, new reds, reds gone, the STALE set, the run time; a traceback
  only for a new red; a note when the tree has moved past the baseline.
  Temp databases on the SSD through one setting in the gate. Two lines in
  the assistant's brief: the touched test files first, the gate once at
  the end of a pass; the assistant runs the gate itself before a commit
  (ruled: Roman queued it; observed: twelve runs of about 25k tokens each
  read 22 known tracebacks, one FAILED-list compare missed a STALE case,
  and three quarters of a seven-minute run is fixture IO on the HDD).
- Ends when: the tool exists, one frame's agents used it, the assistant
  checked one acceptance with it, and a run's time on the SSD is on the
  stack beside 414 s.
- Waits on: frame 27's verdict for who builds it. Session A, after 26.
- Waits on: a session started after 6140848, for the typed agents.
- Reasoning: `plans/archive/postmortem-frame21-2026-09-16.md`, changes 5
  and 7, and the post-mortem conversation of 2026-09-17.
- Status 2026-09-17 01:48 (rota-b9): queued by Roman, unclaimed.
- Status 2026-09-17 03:34 (rota-99): claimed by hand-off at be4f512. Both waits are
  discharged: frame 27's verdict is in (489db3a), and this session started
  after 6140848. Estimate: design review 40k, one implementer pass 100k,
  diff review 60k, the assistant's own gate run 5k (reasoned: the floors on
  frame 26, two new files of about 300 lines, one suite run read as five
  lines). Design record: `plans/archive/gate-design-2026-09-17.md`.

### 29. The map: a query tool over the code (Roman, 2026-09-17)

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
- Reasoning: the post-mortem conversation of 2026-09-17, and
  `plans/archive/refs-scope-2026-09-16.md` as the ground truth.
- Status 2026-09-17 01:45 (rota-b9): queued by Roman, unclaimed.

### 24. Scripts for mechanical work, and a sweep tool (Roman, 2026-09-17)

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
- Reasoning: `plans/archive/postmortem-frame21-2026-09-16.md`, change 1,
  and the post-mortem conversation of 2026-09-17.
- Status 2026-09-17 01:22 (rota-b9): queued by Roman, unclaimed.

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
