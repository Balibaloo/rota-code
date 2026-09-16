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

### 21. Provenance by reference (Roman, 2026-09-16) [32a42b78]

- Rota workflow. Roman ruled 2026-09-16 (ruled: a ratified statement's
  approval reaches what cites it): `decided` originates in a ratified
  statement and cascades along the refs to the rows that cite it, and the
  cascade is a relationship in the SQL. The five JSON ref columns
  (`source_refs`, `term_refs`) become one refs relation, as
  `item_statements` already is. Provenance is derived from it: reach a
  `references_` row, observed; reach a ratified statement or a ruling,
  decided; neither, reasoned. The five `provenance` columns go. Law 11
  and the revocation walk in law 9 read the same relation (reasoned: the
  assistant's design of the frame).
- Ends when: no owner table stores a provenance stamp or a JSON ref
  column, the walk and the view share one relation, `tests/rota/` passes,
  and the touched cases re-record.
- Waits on: a fresh session. Not this one.
- Reasoning: `plans/archive/reasoned-scope-2026-09-16.md`, the patch
  beside it, and this conversation's Q1 and Q2 in frame 20's status.
- Status 2026-09-16 06:55 (rota-bc): pushed, unclaimed. Frame 20 folds in.
- Status 2026-09-16 07:25 (rota-bc): handed to peer rota-b9 by message,
  stack commit 56ae78b. Session 836a1517 ends at 272k.
- Status 2026-09-16 12:57 (rota-b9): claimed by session 32a42b78. A
  scope agent reads the tree for the refs relation and writes
  `plans/archive/refs-scope-2026-09-16.md`. No code touched yet.
- Status 2026-09-16 13:20 (rota-b9): scope report (86af8ce) and design
  record (402df39) in `plans/archive/`. Four stages, each at a tested
  boundary. Stage 1 (additive) is with an agent. Three design lines
  Roman can overrule (reasoned: the page says observed covers the code
  and the world): a `grain` kind carries the code half of observed;
  `frame_rulings.provenance` folds in; `land()` writes a `rulings` row
  on every verdict so a ruling ref has a target.
- Status 2026-09-16 14:05 (rota-b9): stage 1 landed (ac1b83e). Replay:
  22 failed as the baseline, 16 new tests pass, STALE 0 before and
  after. Q11 moves to stage 4 (observed: a signature is in the prompt
  and re-keys the cases). Deviations are in the design record. A
  read-only review of ac1b83e and stage 2 (readers and the walk) are out.
- Status 2026-09-16 14:47 (rota-b9): stage 2 landed (948c436). Replay:
  22 failed as the baseline, 21 refs tests pass, STALE none. The stage 1
  review found eight fixes (design record, dd8c093). A fix agent and a
  stage 2 review are out. Stage 3 (the drop) follows.
- Status 2026-09-16 15:12 (rota-b9): the eight fixes landed (8614d46),
  22 failed as the baseline. The stage 2 review found two high items in
  the writers (design record, f87feab): a delivery wake stages no
  statement ref, and an old run database regresses silently. Stage 3
  splits: 3a writer semantics (out now), 3b the drop. One cut Roman
  may move: the audit's rule 5 now exempts a principal's verdict
  (reasoned: `land()` writes a settled verdict that nothing relays).
- Status 2026-09-16 15:42 (rota-b9): stage 3a landed (HEAD before this
  commit). 22 failed as the baseline, no STALE case, 10 new tests.
  Every run database in `.rota/` now refuses to open until re-created
  (observed: the agent's report; 14 files). Stage 3b, the drop, is out.
- Status 2026-09-16 16:25 (rota-b9): stage 3b landed. No owner table
  carries a stamp or a JSON ref column; `item_statements` is gone;
  22 failed as the baseline, no STALE case, 1794 passed. The ends-when
  test is in `tests/rota/test_refs.py`. Out now: a review of 3a and 3b,
  the docs (K.9), and the re-record of 14 cases on the 3080 with the
  warm snapshot on the Titan. Q11 (the `source_refs` parameter on two
  ops) is parked: it re-keys every Vision Keeper and Terminologist case
  (reasoned: outside the ends-when; land it with the next brief change).

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
