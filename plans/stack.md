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

### 10. Night 63: the 9B Developer with the door, on click

- Why: with the door of finding 66 the 9B does act 3 in isolation 5/5,
  the right loop, committed. The shipped profile `local-gemma-critic`
  with the door is now the thing to measure on click sentence two.
- Waits on: night 62 (the 3080).
- Status 2026-09-14 17:40: queued behind frame 8.

### 9. Finding 66 door: `tests.load` names the files changed since the red run

- Built (178b255) and measured: the 9B on the fix case 0/5 before, 5/5
  after, on one Titan load, first matching band, committed, no
  challenge. The recordings went to a stray file (ROTA_DEV_DB pointed at
  .rota/cassettes.db; the register is tests/rota/cassettes.db) and were
  merged into the register at 17:40.
- Re-recorded into the register on a second Titan load 17:35 to 17:56:
  5/5 again, the same loop, and it replays green.
- Status: closed 2026-09-14 17:57.

### 8. Click night 62: gemma-4 at the Developer's desk, sentence two

- Why: the benchmark says the 9B does four acts of five in isolation and
  gemma-4 does all five; only the Developer's act 3 separates them. One
  night with gemma-4 at that desk and the small models elsewhere keeps
  the measured control and decides which limit we face: a merge means
  route act 3 and ship; a stall means the wakes are the limit and the
  strong model's transcripts say where. Roman asked not to run every
  desk on gemma-4; per-model endpoints were added for it (02a16d3).
- Night 61 (17:18 to 17:23): died at the Developer's first wake, LiteLLM
  "Missing credentials" at the local server. Fixed: a local endpoint
  gets a placeholder key. Its onboarding snapshot is warm and carries
  the routing, so night 62 starts warm at sentence two.
- How: profile `local-gemma-dev`, `GAUNTLET_WARM=1`, `GAUNTLET_FROM=2`,
  `ROTA_LLM_TIMEOUT=900`.
- Ends when: the night prints done and its sessions are read.
- Night 62's first start (17:24) was warm from a stale snapshot of 12:14
  with the Developer on qwen3.5:9b: cold nights never replaced the
  snapshot on disk. Killed. walk.py now overwrites the snapshot after a
  cold onboarding. Relaunched cold at 17:26.
- Status 2026-09-14 17:33: night 62 onboarding, cold.

### 7. Register hygiene after today's fixes

- The scoring fix is symmetric now (8effc28). Replay on qwen3:8b: 22
  reds, the known set; the 14B's act 3 stays 0/5.
- The stream act attributed: on the same Titan load, qwen3.5:9b is 5/5
  under the old brief line ("do not patch `builtins.input`") and 0/15
  under the reword ("the built-in `input`"). The reword did it, not the
  load. Reverted; the prompt test that rejected `builtins.input` as a
  function the mode does not offer now counts only the tool's own
  functions. The triage refusal no longer says "branch claim" (8efa18c):
  the 9B read it as a missing field and asked the Vision Keeper.
- Open: ACT-CR on gemma3:12b and act 3 with the door, recording on the
  Titan; the peer told quiet after.
- Status 2026-09-14 17:33: Titan recording.

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
