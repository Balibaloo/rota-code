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

## Stack

### 15. The survey spike (Roman, 02:30)

- Why: the survey wrote 22 constraints named after directories, and
  everything downstream (the review filing against `termui`, the
  Developer unable to act, the escalation) inherited them. The brief
  asks "who outside this repository breaks" and rules importers out,
  which is the right question for an application and the wrong one for
  a library, whose outside is its importers. Is the wall the brief?
- How: five register cases on the sample repository, one kind each (a
  signature callers rely on, an exception contract, a patch seam, a
  shared helper, an exported name), scored on the surface named and a
  source line cited (`fields_nonempty: [source_refs]`, new in the
  harness). Wording A as shipped, then wording B (outside the area:
  callers, tests that patch, importers of the package; name the surface
  as path::symbol), both on one Titan load of qwen3:8b.
- Wording A, qwen3:8b: 0 of 5. src/catalog, src/notify, src/store: a
  constraint each, headline a bare name (all_products, money, applied),
  not the target symbol, and source_refs empty: noise by the spike's
  rule. src/billing: `MODEL: amend(` written as prose, nothing landed.
  src/auth: none found, as the wording asks. Two walls, then: the
  question, and the call format.
- Wording B, qwen3:8b, same load: 0 of 5 by the strict rule, and the
  content moved. The target surface is named in three of five areas
  (store: connect; billing: total_of among twelve; auth: register in a
  bundle) against none under A; the `MODEL: amend(` failure is gone.
  What neither wording gets: `source_refs` is empty in every constraint,
  both wordings, and B writes twelve constraints on billing. The brief
  moves the surfaces; the citation needs a door: a constraint cites a
  line from a file the session opened, or it is refused.
- Rescored: source_refs are reference ids, not source lines (the tool
  drops unknown ones by design); the source line is `bindings`, the
  grain a constraint governs. On bindings both wordings are 0 of 5:
  every constraint global, bound to nothing. With any called symbol of
  the area accepted as the surface, B names one in 5 of 5, A in 0 of 5.
- Door: a constraint written while surveying an area binds a grain of
  it, or model.amend refuses with the area's path shape (the brief said
  bind; the tool now says it). Tested. B + door recording on the Titan.
- Corrected 02:54: the harness cannot read constraint_bindings (no id
  column), so "bound to nothing" was the harness's blind spot. Scored
  on is_global, which the tool sets from bindings: wording A 3 of 5,
  wording B 4 of 5, same load; the model binds at file grain under
  both. B's miss is billing, twelve constraints against a cap of nine.
  A's misses: the `MODEL: amend(` prose on billing and none found on
  auth. The bindings door never fired and stays as a tool error for an
  amend that omits them.
- Night 73 onboarded on the SSD in 15 minutes (132 steps); night 70 on
  the HDD took 22 (135 steps). One sample each.
- Status 2026-09-15 02:54: B is the wording in the tree; the billing
  count is the open judgement (one constraint per commitment, not per
  function); Roman decides the wording.

### 14. The reply assertion (Roman, 02:20)

- Why: finding 73 was data without an assertion. Every asking edge in
  the graph now carries `expects`: `answer` (a message back), `commit`
  (the Developer's challenge brief: the answer is the next commit) or
  `decision` (the Vision Keeper's: amend, or author a decision).
  tests/rota/test_graph_reply.py checks each: the answer edge back and
  msg.answer_<sender> in the receiving mode's list, or the tool that
  makes the reply. It names the three edges finding 73 belongs to on
  first run; two of them were the briefs' design, not gaps.
- Left: graph.json is in the warm stamp's hard set, so the next night
  is cold for a metadata field.
- Status: closed 2026-09-15 02:25.

### 13. Sentence three on click

- Why: sentence two merges (nights 70 and 71). Sentence three, the
  show_python flag on version_option, stuck in the fix loop on both
  nights at the same shape: the 9B cannot insert an import into a
  623-line file (finding 74).
- Night 72 (01:59, warm on C:, sentence three only) was launched by the
  peer session and runs the tree as of 01:59; I watch it.
- Door: the drops refusal names the insert-at-top span beside the
  append span. Measured on the next sentence-three run.
- Door committed (ef06e79); the register after it: 20 reds, all known,
  no stale (02:07).
- Night 72 (01:59 to 02:36, the peer's, sentence three, tree of 01:59
  without the door): stuck at the fix loop after 87 steps. Night 73
  launched 02:38 on sentence three with the door, cold on C: (the graph
  changed), which also measures onboarding on the SSD.
- Night 73 (02:38 to 03:00, cold on C:, onboarding 15 minutes): sentence
  three stuck at batch_start, earlier than 70 to 72. Three identical
  22-turn Developer sessions: decorators.py read twenty times, no write,
  two ledger calls refused with the exact fix, the verbatim-repeat cut.
  At temperature zero a re-fired tick with the same wake is the same
  session; tests_failing carries "attempt N" in its wake, batch_start
  carries nothing (finding 76, next).
- Register after the survey wording (02:54 to 03:00): 20 reds, no stale;
  the old survey case is 5 of 5 on qwen3:8b now (it was the MODEL: amend
  prose red), and the spike's billing case is the twentieth.
- Door (finding 76): a re-fired batch_start wake carries "attempt N of
  3: the last session ended with nothing written and nothing committed",
  from tick_attempts, as tests_failing does. Night 74 launched 03:03 on
  sentence three, cold (survey.md and scheduler.py are in the warm
  stamp's hard set).
- Night 74 (03:03 to 03:25, cold on C:, onboarding 15 minutes again):
  stuck at batch_start as night 73. The attempt line reached the wake
  ("attempt 2 of 3: the last session ended with nothing written") and
  the sessions kept their shape: 22 turns, version_option (207 lines,
  420 to 627) read six times, a fabricated copy of it in the reply, no
  write. Sentence two's function was 65 lines and it wrote at turn 9.
  Reading whether code.source cuts the span.
- Found: a tool result is cut at 6000 characters and the note said "ask
  for the next range" with no number. version_option is 8692
  characters; the 9B saw the same first 6000 six times and never the
  line it had to change (finding 77). Door: the note names the line the
  cut fell at and the call that fetches the rest. Night 75 launched
  warm on C: to measure it.
- Night 75 (03:28 to 03:44, warm): one step further. The cut-line door
  moved the build: show_python added, the version appended, committed
  at 755b6e9, right. The five tests fail inside click's own test runner
  (src/click/testing.py:387, AttributeError: a bare function has no
  name), because the Tester invoked a function, not a command. The
  Developer in the fix loop read version_option seven times and never
  challenged. Missing fact: where the traceback raised and whether the
  diff touched that file (finding 78, next).
- Door (finding 78): tests.load says where a red run raised and
  whether the diff touched that file. Night 76 launched warm on C:.
- Register after the raised-at field (03:48 to 03:55): 20 reds, all
  known, no stale.
- Night 76 (03:47 to 04:05, warm): the raised-at fact reached the wake
  and the fix sessions kept their shape, ten turns, no write, no
  challenge. Then the cause: Ollama truncates the prompt at 6146
  tokens (num_ctx 12288 split over two parallel slots), 208 times in
  its log; the fix sessions run 7 to 12 thousand tokens and lose the
  brief (finding 79). The wall of nights 73 to 76 is the server.
- Fixed 04:10: OLLAMA_NUM_PARALLEL=1 as a user environment variable,
  the 3080's Ollama app restarted, the 9B loads with context_length
  12288; the Titan launcher pins one slot too. The runner's truncation
  flag now also fires when the prompt's estimated tokens exceed
  num_ctx, so a cut session says so instead of running headless. A
  session over 12k tokens still loses its head: the fix wake with five
  red tests ran 12.6k on one turn; num_ctx or the pushes budget is
  Roman's call. Night 77 launched warm on C: with the full window.
- The register too: 603 of 17966 cassettes hold prompts over the
  halved window (llama 264, qwen3:4b 253, the 9B 41, the 8B 23), so
  some known reds are recordings of headless sessions. The Titan's
  server went down with the 3080's restart and is back with one slot;
  the twenty reds re-record on it with ROTA_REFRESH=1.
- Night 77 (04:08 to 04:32, warm, one slot): the behaviour changed. The
  Developer took the challenge exit twice with the raised-at fact in
  front of it, the Tester fixed one of the five tests (tst_c1 green),
  and the fix loop reached its third attempt with four tests still
  wrong. Stuck on attempts, not on a loop: one test fixed per round,
  three rounds. The last Developer session judged the code already
  satisfies the criteria and committed nothing, which is right.
- The Tester's side of night 77: with five criteria it writes twenty
  to sixty encode and triage calls in one reply and the reply is cut at
  the output budget, so one test lands per session at most. The
  register's act case has three criteria and passes; five is a
  different shape (finding 80). Judgement: the brief's one-criterion-
  per-reply line against five, and the fix loop's cap of three attempts
  while the Tester repairs one test a round. Both for Roman.
- The reds re-recorded with the full window (04:11 to 05:09): 17 red,
  3 green. The three were headless recordings: the survey spike's
  billing case, DV-give-the-new-parameters-defaults and
  TE-challenge-an-unusable-item. The register holds at 17 known reds.
- Finding 80 measured: a five-criteria act case (one per reply) is 5 of
  5 on the 9B in isolation, beside the three-criteria one on the same
  load. The count is not the wall; night 77's flood comes from the
  wake's content on click. Reading what that wake carries.
- Night 77's Tester wake replayed verbatim: on the Titan ten calls in
  2,900 characters, three times identical; on the 3080's fresh load six
  calls in 2,400; the night's own reply on the 04:10 load was 37,518
  characters of prose with no call. One prompt, three loads, three
  behaviours at temperature zero. The wake is 3.3k tokens and holds
  the case's blocks plus the expect page and 34 inherited tests. The
  flood is the load, not the brief; reading whether the 3080 offloads
  the 9B partially and differently each time.
- Isolated (05:25): through the runner's own backend the 3080 floods
  (34k characters, no call, twice) and the Titan answers (five calls,
  294 characters, twice). On the 3080 the knob is `think: false`: with
  it, prose; with thinking on, ten calls. On the Titan `think: false`
  works. The loads differ in flash attention, auto on the 3080 and
  disabled on the Titan; testing with it off on the 3080 (finding 81).
- Status 2026-09-15 05:26: the 3080's server restarting with flash
  attention off.

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
- Night 71 (01:19, warm on C:): sentence two MERGED again at 302f8be,
  42 steps and 33 sessions in 10.5 minutes, the one finding escalated
  and satisfied as on night 70. Two samples on the shipped profile.
  Sentence two is model-bound, so the SSD gained nothing there; the
  onboarding gain is measured on the next cold night on C:.
- The reference file counts sessions, not the log's steps; night 71's
  33 replaces the seeded 42 for sentence two.
- Sentence three's first wall (night 70, 44 steps): the criteria named
  custom_version_option as their surface while the item and their own
  text say version_option, and the duplicate-name door refused the
  Developer's right change (finding 74). Door built and committed
  (43b0322): criteria authoring refuses a surface on another existing
  callable when the item names one the index holds. Night 71's
  sentence three carries the same criteria and will stick the same
  way; night 72 measures the door.
- Register after the surface door (01:34 to 01:39): 20 reds, all known,
  no stale; the Critic answer mode's new case recorded 5/5 (cb53120).
- Night 71's sentence three (01:30 to 01:58): the Developer escalated,
  the Vision Keeper was challenged and proposed, the Architect relayed,
  and the criteria kept custom_version_option; the fix loop ended
  quarantined at 76 steps (night 70: 44). The wrong surface is the
  wall; finding 74's door is the fix.
- Night 72 launched 01:59, warm on C:, sentence three only
  (GAUNTLET_FROM=3), to measure the door.
- Night 72 (01:59 to 02:36, warm on C:, sentence three only): the surface
  door held, two of three tests green, the third is a test that cannot
  run (a bare function invoked as a click command), defended by the
  Tester, with no desk able to rule on it; quarantined at 87 steps
  (finding 75, judgement, for Roman).
- A night 73 started at 02:36 on C:, cold, not launched by me; asked
  the peer. Night 72's data is in clickI_prev.db on C:.
- Night 73 (02:36 to 03:00, cold: the graph changed under the peer's
  survey spike, frame 15) was the peer's; its sentence three stuck at
  batch_start, the Developer looping on a ledger.log refusal without a
  write. Finding 75's mechanical half is in: the tool-call scanner
  reads triple quotes as one token on a second pass, so the form the
  refusal recommends parses with a lone quote inside.
- Register after the parser rescan (03:03 to 03:09): 20 reds, all known,
  no stale, 97 green (the peer's survey cases are in the count now).
- Status 2026-09-15 03:10: no night running; waiting on the peer's word
  about the 3080 and the C: runs directory.

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
