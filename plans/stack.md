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
- State: half-built in `rota/roles/api.py` and `rota/core/worktrees.py`,
  uncommitted; the unit test in `tests/rota/test_developer.py` fails
  after `code.write` (the field is absent). Materialised test files are
  excluded as furniture.
- Ends when: the unit test passes, the register replays green or stale
  only where the tool's output changed, act 3 re-recorded on the 9B.
- Waits on: nothing, but runs beside frame 8 on CPU only.
- Status 2026-09-14 17:05: paused; frame 8 first.

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

- Why: my full replay ran without `ROTA_MODEL=qwen3:8b` and reported 85
  meaningless failures (no junk rows were written: a stale case records
  nothing). Two Tester cases showed red on qwen3:8b after a wording-only
  brief reword: the outside-fact case is red on qwen3:8b under every
  prompt it ever had, a known red; the stream act had never been
  recorded on qwen3:8b. Neither is the reword. The four act cases are
  now held by the desks' models (b80742c).
- Ends when: the replay on qwen3:8b is read, the four act cases are
  re-recorded on their models, the peer is told cassettes is quiet.
- Status 2026-09-14 17:30: replay running; Titan re-record launched.

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
