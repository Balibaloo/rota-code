# The task stack

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

## Stack

### 9. Finding 66 door: `tests.load` names the files changed since the red run

- Why: the 9B wrote the fix, loaded the tests, read the run from before
  its write as its fix failing, and restarted until the loop cut it. A
  mechanical fact, so a door.
- State: built. `worktrees.changed_since(path, sha)` and the row field
  "changed since this run, not run" in `tests.load`, materialised test
  files excluded as furniture. Unit test green (the test lands the
  batch head the way a session does; `code.commit` stages that write).
  Uncommitted, measured by the replay of frame 7.
- Ends when: the replay says green or stale only where the tool's output
  changed; then act 3 re-recorded on the 9B; commit.
- Status 2026-09-14 17:16: waiting on the replay.

### 8. Click night 61: gemma-4 at the Developer's desk, sentence two

- Why: the benchmark says the 9B does four acts of five in isolation and
  gemma-4 does all five; only the Developer's act 3 separates them. One
  night with gemma-4 at that desk and the small models elsewhere keeps
  the measured control and decides which limit we face: a merge means
  route act 3 and ship; a stall means the wakes are the limit and the
  strong model's transcripts say where. Roman asked not to run every
  desk on gemma-4; the mixed profile needed per-model endpoints, added.
- How: profile `local-gemma-dev` (Ollama desks as `local-gemma-critic`,
  the Developer on `openai/gemma-4-...` through the llama-server on
  8080, thinking off in the endpoint's extra_body), cold,
  `GAUNTLET_FROM=2`, `ROTA_LLM_TIMEOUT=900`.
- Ends when: the night prints done and its sessions are read.
- Status 2026-09-14 17:25: launched.

### 7. Register hygiene after today's fixes

- Why: the first scoring fix (91f1928) was wrong in the other direction.
  `_bind` logs a tool call before its guards, `stage` logged a send after
  its guards; counting every logged call as landed turned every refused
  generic call into a red. The replay on qwen3:8b showed 38 reds, 15 new,
  all of that kind. Fixed the other way: `stage` logs before its guards,
  the subtraction returns. The 14B's act 3 stays 0/5 under it.
- Also: the Titan re-record put the stream act at 0/5 on qwen3.5:9b, the
  model that was 5/5 on the 3080 load. Per-load determinism: the 9B's
  four acts are not a stable fact yet. The outside-fact Tester case is a
  known red on qwen3:8b under every prompt it ever had.
- Ends when: the replay after the symmetric fix reads 23 known reds and
  no stale (the door of frame 9 may stale the act 3 cassettes, expected),
  the stream act re-recorded on the 3080 after night 61, the peer told
  cassettes is quiet.
- Status 2026-09-14 17:16: replay running.

### 6. The harness false pass

- `check()` subtracted refused calls from a log of landed calls; the
  14B's forbidden challenge scored as none. Fixed 91f1928. Act 3
  re-scored: 9B 0/5, 14B 0/5, gemma-4 5/5. Findings 65 to 67. The 14B
  routing reverted 430ddea.
- Status: closed 2026-09-14 16:35.

### 5. The five-act benchmark (Roman's plan, step 1)

- Three columns: gemma-4 via llama.cpp, qwen3.5:9b, qwen2.5:14b. Acts
  1, 2, 4, 5 are 5/5 everywhere. Act 3 only gemma-4. In COMPLETION.md,
  "The order from here", step 1.
- Status: closed 2026-09-14 16:13. Answer: the 9B is nearly perfect on
  the acts as cased; act 3 is capacity; click-size context is frame 8.

### 4. Roman's plan for sentence two (2026-09-14 12:58) (Roman)

- Stop band-aiding the stdin door. Steps: 1 benchmark, 2 route a larger
  model where it passes, 3 language seam, 4 breadth (two lineage repos
  cold, then a non-Python repo), 5 long-run noise test after sentence
  three merges, 6 ship the loop. Do not: rewrite the core, lower the
  cap, more nights on sentence two as if doors were the answer.
- Status: step 1 done; frame 8 decides step 2.

### 3. Click sentence two (nights 50 to 60)

- Every night stuck; each became a door or a brief line (findings 36 to
  64). Night 60: the 14B Developer timed out at its first wake; sentence
  three then ran once, quiet, no merge.
- Ends when: one night merges sentence two.
- Status: behind frame 4.

### 2. The gauntlet on the lineage (goals 3 and 10)

- Three lineage repos, three sentences each, unattended. Click sentence
  one merges (nights 49, 50). Sentences two and three do not yet.
- Ends when: the lineage is walked and every fault is a door or a case.

### 1. The end state (plan agreed 2026-09-10)

- A careful person runs rota alone on a small Python repository and
  gets a merged change they can read. Honest about where small models
  stop. Ten goals in COMPLETION.md: 1, 2, 7, 9 done; 4 and 8 measured
  and ongoing; 3 and 10 are frame 2; 5 and 6 fed by it.

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
