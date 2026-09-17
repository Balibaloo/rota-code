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

### 27. Opus 5 on frame 21's agent types (Roman, 2026-09-17) [32a42b78]

- Meta workflow. Opus 5 at high effort redoes three parts of frame 21
  with the same briefs, in parallel: the review of 948c436 (reviewer),
  stage 1 from e63762c in a worktree (implementer), the 48-file sweep from
  b4dc845 as a script (sweeper). Opus is cheap; Fable is the scarce
  resource. A Fable peer reads each output in full, the diff, the report,
  the findings, and never the transcript or the reasoning. It judges by
  working back from the output: the suite on the commits, the findings
  against the ten found and the two that mattered. No scoring apparatus
  (ruled: Roman, 2026-09-17).
- Ends when: three verdicts on the stack, one per agent type, each with
  the Fable tokens spent judging it.
- Waits on: the end of the post-mortem grill, then the two Opus agents.
- Reasoning: the post-mortem conversation of 2026-09-17; frame 26 for the
  agent types; `plans/archive/refs-design-2026-09-16.md` and the frame 21
  reviews in it for the known-good run.
- Status 2026-09-17 01:34 (rota-b9): pushed by Roman, unclaimed.
- Status 2026-09-17 01:36 (rota-b9): claimed; Roman raised this session's
  limit to 400k because the context holds the known-good run. Worktrees
  are ready at 948c436 and e63762c; the Opus agents start after the
  post-mortem grill ends. The sweeper part has no clean ground truth (observed:
  the sweep and the drop share commit 056995d); it folds into frame 24
  as the sweep tool's first use.

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
- Waits on: Roman's read of the lines, and the billing basis of the
  reported usage (context growth, or the prefix billed each turn).
- Reasoning: `plans/archive/postmortem-frame21-2026-09-16.md`, change 1.
- Status 2026-09-17 01:17 (rota-b9): queued by Roman, unclaimed.

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
- Waits on: Roman's read of the lines.
- Reasoning: `plans/archive/postmortem-frame21-2026-09-16.md`, change 1,
  and the post-mortem conversation of 2026-09-17.
- Status 2026-09-17 01:22 (rota-b9): queued by Roman, unclaimed.

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
- Waits on: Roman's read of the lines.
- Reasoning: `plans/archive/postmortem-frame21-2026-09-16.md`, change 3,
  and the post-mortem conversation of 2026-09-17.
- Status 2026-09-17 01:26 (rota-b9): queued by Roman, unclaimed.

### 26. Agent types with the tools they use (Roman, 2026-09-17)

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
- Waits on: nothing.
- Reasoning: the post-mortem conversation of 2026-09-17, the `/context`
  reading of frame 21's session.
- Status 2026-09-17 01:28 (rota-b9): queued by Roman, unclaimed.

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
