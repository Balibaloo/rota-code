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

### 12. Night 71 on the SSD

- Why: Roman saw no GPU use during night 70's onboarding. The click
  checkout, the worktree, the index and the run database's WAL all sit
  on the D: HDD (13 fsyncs a second; C: does 279). Roman: move them for
  the next night, not this one.
- How: `ROTA_RUNS=C:/Users/roman/rota_night/state` (the runs directory:
  run db, warm snapshot, live file) and
  `CLICK_ROOT=C:/Users/roman/rota_night/clickI` (a clone of the sample
  repo, made 00:40). The first night there is cold.
- Ends when: night 71 runs there and its onboarding time is read
  against night 70's.
- Warm start hardened for the move (Roman's briefing 00:45): the check
  goes cold when the snapshot's routing differs from the named profile's
  (night 62's wrong-model start), and a `relocate` step rewrites the
  snapshot's project_root to CLICK_ROOT on restore, so a moved night is
  warm. Night 70's snapshot (00:54) copied to C:; night 71 starts warm.
  Left for later: the hard set keyed on whole files (graph.json forced
  night 70 cold for a non-onboarding edge) and the blind 4-night cap.
- The run progress file (Roman, 01:10): one block, rewritten each step
  by the walk, at <runs dir>/progress_clickI.md: phase, the stage from
  the tick that fired last, wakes so far against the previous night's
  count for the same phase and outcome, minutes so far against that
  night's minutes, the last page, the last wake, and the attempts on
  the frontier tick. Night 70 seeded the reference: onboarding 135
  wakes in 22 minutes, sentence two 42 in 10 (merged), sentence three
  44 in 12 (stuck). probes/progress.py, tested.
- .rota tidied on Roman's word (01:25): 337 run databases and WAL files
  from August to the tips walks deleted, 302 MB. Kept: night 70's
  database as clickI_n70_merged.db, clickI_n42, the warm snapshot, the
  register backup of 02:00 until the pack is verified, and the six tips
  walks COMPLETION.md cites.
- Night 71 (01:19, warm on C:): the relocate pointed the snapshot at the
  C: checkout and sentence two MERGED in 42 steps, 33 sessions, 10.5
  minutes, the same time as on the HDD: the sentence phase is the
  model's, the disk's cost sits in onboarding, unmeasured tonight
  (warm). Sentence three runs now against night 70's 44-step stuck.
- Status 2026-09-15 01:31: sentence three on C:.

### 11. Nights 64 to 70: the shipped profile with the doors, on click

- Night 70 (00:32 to 01:04, cold): MERGED. Sentence two on the shipped
  profile: onboarding 22 minutes on the HDD, then 42 steps in 10
  minutes. The Developer built and committed at batch_start, the tests
  went green, the Critic passed, the structural review filed one finding
  against `termui`, the Developer escalated it, the Architect answered
  and set it satisfied (finding 72's branch), the batch merged at
  3c17d35 and click's main carries "rota: deliver bg_1".
- The road: nights 64 to 69 each stuck one step further, and each step
  was a missing fact or a missing tool, findings 69 to 73. None was
  the model.
- Status: closed 2026-09-15 01:06. Sentence three runs to GAUNTLET-DONE;
  then frame 12.

### 10. Night 63: the 9B Developer with both doors, on click

- Read: the Developer committed at batch_start, the fix loop converged,
  both batch tests and the inherited suite green at 96bad2c. Then the
  Tester looped on the third criterion ("confirm() accepts a boolean
  argument named default_on_eof"): its try/except test was refused as
  "every assertion on a constant", it triaged `cannot`, the hint said
  ask the Terminologist, the message door refused a third question,
  three identical sessions, quarantined. Stuck at 19:00 (finding 69).
- Fixed, uncommitted: the `cannot` hint climbs to the Vision Keeper once
  the Terminologist has answered twice, and a body that raises
  AssertionError or uses pytest.raises counts as a check.
- Status: closed 2026-09-14 19:46; frame 11 reruns it warm.

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

- Read: two Developer sessions on gemma-4. s139 implemented confirm()
  right at turn 9, then fifteen turns on the project's test file, no
  commit (finding 68, door 1682628). s140 found the edit in the
  worktree, re-read it until the repeat cut, no commit. Both without
  the door, which landed after the process started. Killed 18:13.
- What it says: a strong model needs the same worktree facts as the
  small one; the wake, not the model, was the limit in both sessions.
- Status: closed 2026-09-14 18:14; frame 10 runs the shipped profile
  with the doors. gemma-4 stays the control to rerun if the 9B stalls.

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
- Replay after the finding 68 door (18:11 to 18:20): 17 reds, all
  known, and 10 stale: seven Developer cases (code.write's result
  changed) and three Tester cases (the triage refusal's wording
  changed). Re-recording the ten on the Titan.
- Replay after the re-records (18:55 to 19:00): 20 reds, all known, no
  stale. The peer re-packs from that file.
- The pack: the peer session that re-packs is offline since about
  19:00, so the release pointer still carries the 17:56 file.
- Status: closed 2026-09-14 19:52; the re-pack waits on the peer.

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
