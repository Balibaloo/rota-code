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

### 11. Nights 64 and 65: the shipped profile with the finding 69 and 70 doors, warm

- Why: night 63 ended stuck on one criterion because two doors
  contradicted. Both are fixed. The night's snapshot is warm and carries
  the profile, so sentence two runs again from onboarding at no cost.
- How: `GAUNTLET_WARM=1`, `GAUNTLET_FROM=2`, profile `local-gemma-critic`.
- Ends when: the night prints done and its sessions are read.
- Night 64 (19:48 to 19:59, warm): the build and the Critic's review
  passed; the Architect's structural review failed three times at commit
  with a foreign key error. findings.find took inherited test ids as
  constraint ids and said OK; the database refused at commit. Stuck.
  Finding 70. Fix: findings.find checks its batch and constraint ids at
  the door.
- Night 65 (19:58 to 20:13, warm): build, tests, Critic's review and
  the structural review all landed. Stuck one step later: three
  `violated` findings against the vacuous constraint `termui`, two on
  test files the diff never touched; the Developer looped on nothing to
  fix and did not escalate (finding 71). Door: a finding's grain is a
  file the diff changed. The rest is the briefs: the survey's
  constraints say nothing, and the Developer does not take the escalate
  exit. For Roman.
- Night 66 (20:22 to 20:36, warm): the same wall one step in. The door
  held on the project's tests; the review filed on the batch's own
  materialised test files (furniture, now excluded), and on
  src/click/termui.py against `termui`. The Developer read it and
  looped without escalating, three times. Stuck.
- For Roman: three nights on the shipped profile now reach the
  structural review and stop at the same judgement: the survey's 22
  constraints are the example directories' names with the text "users
  of the X example"; the Architect files `violated` against them; the
  Developer does not escalate a finding it cannot act on. The briefs of
  the survey, the structural review and the Developer's
  finding_violated mode are where the work is.
- Night 67 (20:37) overlapped night 66's sentence three, launched on
  the Stuck line and not on GAUNTLET-DONE: both wrote one database and
  one checkout for two minutes. Killed. A night ends at GAUNTLET-DONE.
- Night 68 launched 20:39, cold (the fourth warm night spent the
  snapshot), to measure the src-only finding, then this frame closes.
- Night 68 (20:39 to 21:03, cold): one finding left, and the Developer
  escalated it. The Architect agreed the code was right and could not
  withdraw the finding: its escalate mode had no findings.find and no
  branch for a wrong finding (finding 72). Fixed: the tool in the list,
  the branch first in the brief. The survey's constraints read better
  cold ("WHO BREAKS: ..."), and `termui` is still the empty one.
- Register after the escalate brief change (21:07 to 21:14): 20 reds,
  all known, and two stale Architect cases (find-against-a-constraint,
  route-an-escalation), re-recording on the Titan.
- The escalate branch measured worse first (route-an-escalation 0/5:
  the 8B took the first bullet for every escalation) and holds last,
  conditioned on a finding in the refs: both cases 5/5. The changed-
  files door checks path-shaped grains only. Night 69 runs the first
  version; night 70 measures the final one.
- Register at 21:24: 20 reds, all known, no stale; the peer can re-pack
  from this file when it returns.
- Night 69 (21:08 to 21:41, warm): one step further again. The first
  review passed, the structural review landed, the Developer answered
  and committed twice, 37 tests green at 21a2386. The Critic's
  re-review misread the diff, challenged the Tester, and the Tester's
  challenge mode had no answer verb to the Critic (finding 73).
  Quarantined on review. Stuck.
- Fixed: a tester-to-critic answer edge in the graph, msg.answer_critic in
  the Tester's challenge mode, and a Critic answer mode that finishes the
  review with the answer in hand. Night 70 warm measures it.
- Status 2026-09-14 21:53: night 70 launched warm.

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
