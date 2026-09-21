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
7. Every frame carries a name of a few words in its heading, and every
   mention of it carries that name with the number. A number alone is an
   index into this file, so a reader who meets one has to open the file
   to learn what it means. That holds in a status line, in a commit
   message, in a message to a peer, and when you answer Roman (adopted
   from the kit on 2026-09-21, frame 52).
8. Every conclusion carries a mark with a headline-long reason:
   (observed: where and when), (reasoned: why), or (ruled: why). Say which
   workflow it is about, the meta workflow or the rota workflow (ruled
   2026-09-16: a ruling and a judgement looked the same in prose).
   An observation carries its date, because an observation ages. A check
   quoted without its date is a prediction that wears the word observed
   (adopted from the kit on 2026-09-20, frame 50).

## Stack

**Roman's order, ruled 2026-09-21 00:29.** 46, then 54, then the one read that
frames 47 and 53 share, then 48, then 55, then 49, then 45, 38, 37, 41, 42, 33,
4. Frame 52's port runs inside frame 46's tail, after line 5, so it is not in
this list. Frame 51 folds into 52 (ruled: Roman, asked with three other options
and this one recommended: the acceptance's own instruments come before the next
frame that is judged by them).
This replaces the order of 2026-09-20, which named 46, 47, 48, 45, 38, 37, 41,
42, 33, 4 and predates frames 51, 53, 54 and 55. **The file is not reordered to
match yet**, because rule 1 says top frame first and frame 46 is still open. The
next session to close 46 reorders the file to this list.

### 46. One designed budget for a prompt (2026-09-19) (Roman) [cb5428a2]

- Rota workflow. Today no single place answers the question "what may this
  prompt contain". The caps are per result, per push and per page. The trim
  is per transcript. The window is per session. Nothing sums them, and the
  one function that could sum them, `_fit`, is forbidden to touch the two
  blocks that are usually the problem (observed:
  `plans/archive/context-caps-design-2026-09-18.md`, section 7).
- Every guard in the system was added after a night failed, and each
  comment in the code names that night: the result cap, the source cap,
  the push cap, the wake cut, the middle eviction, the repeat line, the
  identical-turn stop, the index cut (observed: the same record, and the
  code's own comments). Each one is right about the night that caused it.
  **None of them was designed against the others.** Roman judged the
  system on 2026-09-18: "This seems quite undesigned" (ruled: Roman).
- The shape, in five parts (reasoned: the design record's section 7,
  written from the scope of 536k):
  1. One budget for a turn, derived from the window, in one place.
  2. The parts of a prompt declared in priority order: the brief, the
     wake line, the refs, the latest results, the older results.
  3. The budget is allocated down that order. A part that overruns takes
     from what is below it and never from what is above it.
  4. Every cut is announced in the same words, and the words name the
     tool that fetches the rest.
  5. One number a test can assert.
- Ends when: a test asserts that an assembled prompt is inside its
  budget, or that the runner named which part it cut and by how much.
  **Priced 2026-09-20 from the scope.** Each line carries a price from the
  anchors in `plans/operating-facts.md` and the behaviour it buys, walls
  counted apart:
  1. One place measures the assembled prompt before the send, and a test
     asserts the whole prompt is inside the budget: 90k (cold 75k, one
     resumed pass 15k). Buys: the system learns a prompt does not fit
     before it pays for the answer. Today the only whole-prompt
     measurement runs after the reply.
  2. **`decisions.search` gets a character budget**, at
     `rota/core/runner.py:1634-1644`: 80k plus 30k of re-records, 110k.
     Buys: the op that is 55.5 per cent of all pushed characters stops
     saturating `PUSH_CHARS` on nearly every push. It runs up to six
     queries and keeps every row, and `decisions_search` has no LIMIT.
     **`PUSH_CHARS` as a total is a separate and much smaller line**,
     worth at most 1605 characters on night 87's largest wake, and it
     waits on this one (repriced 2026-09-20 from the design review, which
     measured both).
  3. One wording for a cut, and every cut names the call that fetches the
     rest: 60k. Buys: a seat can always recover what it lost. Six
     wordings exist and four of eighteen strings name a recovery call.
     About 17 assertion sites in three test files, and no cassette in the
     register carries `TRUNCATED` or the ask-for-the-next-range line, so
     the re-record allowance moves to line 5.
  4. The eviction notice and the repeat line stop contradicting each
     other, with a named test: 40k plus 20k of re-records, 60k. Buys: 8
     of 8183 prompts stop telling a seat two opposite things.
  5. The silent cuts get a notice to the seat, and separately a recorded
     reason: 100k plus 20k of re-records, 120k, and it is two lines not
     one. Buys: the principal's ledger stops being shorter than the
     challenge row it derives from. 25 or more sites in
     `rota/roles/api.py` alone.
  6. A design review of the design record before any code: 80k.
  7. One diff review on a worktree at the commit: 90k.
  8. The gate before each commit, the stale line read: 36k.
  9. A walk, because the frame changes what a seat is told: 20k in this
     context, about nine hours wall.
  Total: 666k in agents after the reprice, about 45k in this context.
  **Already spent: the scope at 1206692 tokens in 12 agents, and the design
  review at 106746 tokens in 56 tool calls**, 1313438 in all. The scope is
  2.2 times frame 43's 536k on the same path, and the verify stage is where
  the excess went. Both stages earned it: 11 of 218 scope facts came back
  WRONG or UNVERIFIABLE, and the design review then broke three of the
  record's own claims with probes over night 87 and the register.
- Waits on: nothing. Frame 43 closed on 2026-09-20 and is in
  `plans/archive/stack-2026-09-20.md`. This is the top frame.
- Reasoning: `plans/archive/context-caps-design-2026-09-18.md`, section 7,
  and the scope it was written from,
  `plans/archive/context-caps-scope-2026-09-18.json`.
- Status 2026-09-19 04:14 (rota-65): pushed by 4286e076, unclaimed,
  unpriced. The frame exists so the obligation stays countable. The four
  repairs of frame 43 do not need it, and the design record says so. This
  is the design that stops the next fault. The four repairs stop the
  bleeding.
- Status 2026-09-20 03:00 (rota-52): **the wait is discharged. Night 87 ran
  and this frame can be priced.** The four numbers say how much of the
  bleeding the four repairs already stopped: the middle eviction fell from
  36.0 per cent of turns to 22.5, the wake cut from 10.4 per cent to 2.0, the
  sessions cut by the server from 15 of 203 to 0 of 746, and the tokens
  discarded from 179117 to 0. The largest prompt of 3599 turns was 8191
  tokens against a 16384 window, where night 86 sent one of 27155.
  **The number that argues for this frame is the one that got worse.** No
  prompt came near the window, and the reply cut still fired 140 times. A
  budget that is right per part and never summed is exactly the fault frame
  47 now carries a case of. The pricing grill is Roman's to call.
- Status 2026-09-20 03:35 (rota-52): **claimed by 0549dc76. Frame 43 is closed
  and the stack now reads in Roman's order** (ruled: Roman, 2026-09-20, "46,
  next just work your way down the table, in order"). The order is 46, 47, 48,
  45, 38, 37, 41, 42, 33, 4, and the file is reordered to match, because rule 1
  says top frame first. This replaces the order of 2026-09-18, which named 43,
  38, 37 and 33 and predates frames 45 to 48.
  **Frame 43 closed on Roman's order of the frame below it** (reasoned: the
  assistant; Roman read the frame's summary and named the next frame, which is
  the declaration the frame waited for). The frame moved verbatim to
  `plans/archive/stack-2026-09-20.md`, 1109 lines. Reopen it by moving it back
  if that reading is wrong.
  The scope runs now, because the frame is a shape with no price. Six
  read-only agents, one question each, and the price and the design record
  follow. Frame 43's own scope of the same path cost 536k in five agents, so
  that is the anchor.
- Status 2026-09-20 03:35 (rota-52): **the scope is in, the design record is
  written, and the frame is priced. No code is written.** The record is
  `plans/archive/prompt-budget-design-2026-09-20.md`. The evidence is
  `plans/archive/prompt-budget-scope-2026-09-20.json` and its digest beside
  it, both rescued into the repository, because a record's pointer never
  names a session scratchpad.
  **The frame's own premise is half wrong, and the half that is wrong is load
  bearing** (observed: the scope, verified). One budget already exists and
  already binds: `_fit_budget` caps the system string plus the user string at
  `max(2000, int(num_ctx / 2 * 3.97) - system_chars)`
  (`rota/core/runner.py:566`). Three caps derive from it rather than from a
  night, and `result_room` at `:2154` is an allocator in everything but name.
  The frame may not say that nothing sums.
  **What is actually wrong, in the order it costs.** Half of every window is
  unreachable by construction, so frame 43's rise from 12288 to 16384 bought
  the lower half only and a prompt can never pass 8192 tokens while the
  halving stands. Nothing measures the assembled prompt before the send, and
  the only whole-prompt measurement runs after the reply arrives. The system
  prompt is charged to the budget and never cut. `PUSH_CHARS` is applied per
  key and not as a total, so a wake can carry 80000 characters before `_fit`
  runs, and the pushed working set is the largest part of a
  90th-percentile prompt.
  **Three tests already assert three different numbers** (observed: three
  verifiers, each correcting its own scope), so the frame's fifth part is
  partly built and the design must pick which number is the promise.
  **The verify stage earned its cost.** 11 of 218 facts came back WRONG or
  UNVERIFIABLE, including a composition share the verifier reproduced at 58.6
  per cent against the scope's 48.3, and a claim that six caps exist and none
  derives from the others, which its own citation refutes twice over.
  The design review of ends-when line 6 runs now. It does not wait on the
  ruling below.
- Waits on: **nothing. The ruling this frame waited for was never this
  frame's question** (ruled: Roman, 2026-09-20, by sending the assistant
  back to what the frame says it is for).
  **This frame is a design frame and not a capacity frame.** Its own first
  three lines say so: nothing sums the caps, none was designed against the
  others, and Roman judged the system undesigned. All five parts are
  structural, and the ends-when is a test asserting an invariant, not a
  night showing bigger prompts. Nothing in the frame is about giving a seat
  more room.
  **The half-window question is a capacity question and it is now frame 53.**
  This session found it while scoping and then let it gate a frame it does
  not belong to. The halving stands here, because this frame was never about
  changing it. Build lines 1 to 5 as priced.
  The question that moved to frame 53, kept here for the reasoning: does the
  prompt budget stay at half the window? The
  budget is half because ollama collapses a prompt over `num_ctx` to
  `num_ctx / 2 + 2` and keeps the tail, which cuts the brief off the front
  (observed: the docstring at `rota/core/runner.py:566`, finding 79). Keeping
  the halving is safe and permanent: a 16384 window carries at most 8192
  tokens of prompt for ever, and frame 43's rise is worth half of what it
  reads as. Raising it needs the assembled prompt measured before the send,
  which is ends-when line 1 and does not exist today, plus a margin for the
  chat template that nobody has measured, and it re-keys the register where
  the stale line cannot see it.
  **Recommended answer: keep the halving, and spend the frame on line 2
  first.** The recommendation survives the design review and the reason
  changed. The denied demand is real and large: on night 87 the cut notices
  account for 8784628 characters denied against 6946907 delivered, so the
  caps removed 1.26 times what they delivered. **But the demand is denied
  upstream by `decisions.search` saturating `PUSH_CHARS` on nearly every
  push, and not by the half-window ceiling.** Raising the ceiling would not
  deliver one character more while that op is unbudgeted.
- Status 2026-09-20 04:20 (rota-52): **the design review is in and it broke
  three of the record's claims with probes. The record and the price are
  corrected. Still no code.** 106746 tokens against 80k priced, 56 tool
  calls, 8 minutes. The overrun went into the three probes that produced the
  findings, which is the same trade frame 43's design review made.
  **The record named the wrong ops.** It said `code.area`, `code.front` and
  `code.boundary` fill the wake. They fire in 10 pushes of 463 on night 87.
  `decisions.search` is 55.5 per cent of all pushed characters, has no LIMIT
  and no budget, and its median pushed size is 20105 characters, which is
  `PUSH_CHARS` plus the notice.
  **The record's headline number was a theoretical maximum that never
  happens.** It said four pushed reads can put 80000 characters into a wake.
  Night 87's largest pushed block is 21605, and capping the block once would
  remove at most 1605 characters.
  **A whole-prompt check placed where the existing one sits would be dead to
  every recorded case**, because `truncated` is assigned only in
  `OllamaBackend` and the suite replays through `ReplayOnlyBackend`. That is
  frame 43's `graph.json` shape again, caught before any code this time. The
  check goes in `run_session` beside `_fit`.
  **The halving is Ollama-specific**, so the ruling is now "half the window
  on Ollama". `LiteLLMBackend` never sends the window, so on those profiles
  the halving discards half the budget and defends against nothing.
  Also corrected: two caps derive from the budget and not three.
  `TURN_RESULT_CHARS` is two night constants and does not move with
  `num_ctx`. Lines 2, 4 and 5 re-key the register and now carry re-record
  allowances, 326 of 18435 cassettes for line 2 alone. Line 3 is 30k cheaper
  and line 5 is 50k dearer and is two lines.
  **HAND-OFF at 16:50.** Session 0549dc76 releases the whole stack and
  stops. Roman ordered the hand-off so frame 46's implementer pass runs in
  a fresh context instead of starting near this session's limit.
  **What the next session picks up, in order.**
  1. Frame 46 waits on nothing. Build the five priced lines, starting with
     line 2, the `decisions.search` budget, which is the one the design
     review named as the real repair.
  2. Line 1's check goes in `run_session` beside `_fit` at
     `rota/core/runner.py:1972`, above every backend. Placed where the
     existing one sits it would be dead to every recorded case.
  3. Two frames are pushed and unruled, and Roman assigns them: 52, the
     kit's release, and 53, the half-window capacity question. Frame 51
     folds into 52 if 52 is ruled.
  4. Frame 49, the 72 stale cases, still has no owner and no cause.
  5. Frames 33 and 4 still carry session 9108c499's claim, and that session
     has ended. Releasing another session's claim is Roman's word.
  **Read before trusting**: the design record's sections 2.4 and 5 were
  rewritten after the design review measured them wrong. Read the record as
  it stands, not the commit that first wrote it.
  **Session cb5428a2 holds frame 46 and the stack.** The hand exited 0 and
  printed CONFIRMED 6 seconds after the claim, at stack commit 88f476a. The
  seat was named rather than left to the queue, because the queue ranks on
  arm time and the other free standby held 152k against this one's 20k. The
  queue and the rule agreed today, and naming it cost nothing.
  **A small finding for the kit** (observed: 2026-09-20 16:51): `--to` takes
  a session id and refuses a peer name, while `peers` prints the name in the
  column a reader would copy. The refusal is loud and lists the ids, so it
  costs one retry and nothing worse.
  **One finding is parked, not actioned**: `_fit`'s promise is not a
  theorem. A fuzz of 4000 transcripts broke it 1540 times, on a two-block
  transcript and at the `max(2000, ...)` floor. The runner reaches neither
  today, because it appends a reply and a results block every turn. Line 1's
  test states the precondition rather than closing the hole.
- Status 2026-09-20 16:52 (rota-02): **session cb5428a2 takes frame 46 and the
  stack.** The take exited 0 at stack commit 88f476a, 6 seconds after the
  claim (observed: the watcher's output, 2026-09-20 16:51). Meta workflow.
  This context is clean at 23k, so the implementer pass starts here. Roman
  ordered the hand-off for that reason.
  **The build starts at line 2, the `decisions.search` character budget.** The
  design review named that op as the real repair, and line 1's check goes in
  `run_session` beside `_fit`.
  **Four questions wait on Roman and none of them gates this frame** (observed:
  the stack as it stands, 2026-09-20 16:52): frames 52 and 53 are unruled,
  frame 49 has no owner, and frames 33 and 4 carry the claim of session
  9108c499, which has ended.
  **One cross-project hand-off reached this session before the rota claim and
  was retracted by its sender** (observed: two peer messages, 2026-09-20).
  Nothing of that frame was claimed, and this stack never carried it.
- Status 2026-09-20 17:19 (rota-02): **ends-when line 2 is built, judged and
  committed at `6364927`.** Rota workflow. The pushed `decisions.search` block
  now spends one budget of its own, `DECISIONS_PUSH_CHARS`, 6000 characters.
  The rows go round robin by row, so every word that matched keeps a row. One
  wording names the call that returns a cut word's rows.
  **The measurement on the test's data: 13542 characters before the budget and
  5989 after** (observed: the pass's own test, 2026-09-20). The op in
  `rota/roles/api.py` is unchanged, so a seat that asks for it keeps today's
  contract. `PUSH_CHARS` is unchanged.
  **Price against the estimate: 70491 tokens in one agent pass against 110k
  priced, and the 30k re-record allowance was not spent** (observed: the
  harness's usage line, and `casestatus` before and after). The register reads
  72 stale both sides of the change, so this line staled nothing. The gate
  reads 22 failed against a baseline of 22, one red gone, and zero new stale.
  The estimate assumed the push is in a cassette key. It is not.
  **Three design points were open in the record and this session ruled them**
  (ruled: the assistant, 2026-09-20, because the record priced the line and
  named no numbers): the budget is 6000 because that is `RESULT_CHARS`, what
  one asked-for result may cost. The allocation is round robin because word
  order is the order the subject happened to speak. The op keeps its contract
  because a seat's own call is the recovery the notice names.
  **One wording defect is recorded and not fixed.** The notice promises "all
  N" rows, and the recovery call cuts at `RESULT_CHARS` when a word matches
  more rows than 6000 characters hold (reasoned: the caps are both 6000, and a
  wide word overruns the asked result too). Line 3 rewrites every cut wording,
  so the promise is corrected there and not in a pass of its own.
  **A second test file flakes, and it is not the one frame 48 names**
  (observed: the gate at `a6e0d5c`, and five runs of the test alone,
  2026-09-20 17:10). `tests/rota/test_handover.py::test_a_newer_watcher_retires_the_older_one`
  was the gate's one new red. It passes 5 of 5 alone in 3.3 seconds each, so
  the suite's fan-out is the trigger. It touches no code of this pass.
  Line 1 runs now, in the same agent, resumed by message.
- Status 2026-09-20 17:41 (rota-02): **ends-when line 1 is built, judged and
  committed at `cb0649c`.** Rota workflow. `_prompt_overrun` runs in
  `run_session`, beside `_fit` and above every backend, so a cassette
  exercises it. Two tests assert the invariant on the replay path.
  **The brief's arithmetic was wrong and the agent's reading is right** (ruled:
  the assistant, 2026-09-20, from `_fit_budget`'s own docstring).
  `_fit_budget` charges the system prompt already, so the whole prompt's room
  is the budget plus the system prompt. The brief's literal wording charged the
  system prompt twice and would have fired on nearly every healthy turn.
  **The overrun line reaches the record and fails no case** (observed: this
  session's read of `rota/core/db.py:907` and `rota/testkit/fixtures.py:914`,
  2026-09-20 17:30). `session_note` writes `outcome.errors` as one more turn.
  The fixtures count an error as a refused call only when the text before the
  first colon holds a dot, and this line's prefix holds none.
  **One blind spot of the invariant, recorded and not fixed.** At the
  `max(2000, ...)` floor the limit is the system prompt plus 2000, which can
  exceed half the window. So the check cannot see a system prompt that
  overruns the window on its own. The test's own case shows it: 9231
  characters against a window half of about 1016, and the line reported 322.
  The window question is frame 53.
  **The suite holds a strict and a slack version of one promise** (observed:
  the agent's four verified sites, 2026-09-20).
  `tests/rota/test_runner.py:634` permits a 50 per cent overrun of `_fit`'s
  number, where three other tests assert it exactly. Line 3's pass tightens
  it, and a red there is a defect of `_fit` and not a test to bend.
  **Price: 61021 tokens for the resumed pass, against 90k priced for line 1**
  (observed: the harness usage line, 131512 cumulative for the agent minus
  70491 at pass 1). Cold pass 1 cost 70491. **Both passes are far under the
  300k cold anchor, so the resume rule holds** (observed: two passes,
  2026-09-20).
  Line 3 runs now, one wording for every cut, in the same agent.
- Status 2026-09-20 18:59 (rota-02): **ends-when line 3 is built, judged and
  committed at `8681667`. The gate's new red is not this frame's, and the proof
  cost four re-records.** Rota workflow. `cut_note` owns the wording at six
  sites, and seven strings folded into one form. Ten strings remain, each for a
  named reason. Two sites keep their old wording on purpose: the landing page's
  `rows_not_shown`, which sits inside a recorded prompt, and the eviction notice
  and repeat line, which are line 4.
  **`L1-TE-survey-an-area-for-its-terms` is a pre-existing regression that the
  register was hiding** (observed: four re-records of five runs each,
  2026-09-20 17:50 to 18:30). The bisect, in order: the new wording 0/5, the
  imperative restored 0/5, `code.area`'s old wording back 0/5, the whole of
  pass 3 reverted 0/5, and the two source files at `88f476a` 0/5. So no line of
  this frame causes it. The seat calls `code.area` and never `code.source`,
  identically in all 20 runs, so it is a stable behaviour and not noise.
  **The register held a green that the live model does not reproduce** (observed:
  the register's own rows, 2026-09-20 18:40). Load `qwen3:8b@248599` gave the
  case 10 of 10. It replayed green twice today, then failed 20 of 20 on fresh
  recordings at the same model, the same 12288 window and temperature zero. A
  cassette is a record of what a model once said. A replay of it is not evidence
  that the model still says it.
  **The green recordings are recoverable and this session is not restoring
  them.** `.rota/cassettes_backup_2026-09-19-frame43-closing.db` holds them.
  Restoring them would hide a real regression behind a cassette. So the gate now
  reads 23 known reds where it read 22, and the 23rd is named and owned by frame
  55.
  **One record of this session was wrong and is corrected in place** (ruled: the
  assistant, 2026-09-20): a comment and a test docstring claimed the imperative
  in a cut sentence was load bearing, from the first re-record alone. The bisect
  disproved it. Both now say the imperative follows the rule in `CLAUDE.md`, and
  that no case measures the difference.
  **The register runs at 12288 and the nights run at 16384** (observed: every
  cassette's `num_ctx`, 2026-09-20). No cassette in the register was ever
  recorded at 16384. So the register does not measure the window frame 43
  shipped. That is a finding for frame 54 and not a line of this frame.
  Price: the agent's pass cost is unread for line 3 alone, because the harness
  reports the agent cumulatively. Cumulative after three passes: 205227 tokens.
  Line 4 runs next, the eviction notice against the repeat line.
- Status 2026-09-21 00:17 (rota-02): **ends-when line 4 is built, judged and
  committed at `27d0de8`. No wording moved, and the cassette counts are why.**
  Rota workflow. A repeated call is suppressed only while the transcript still
  holds its answer. After an eviction the runner serves the result again and
  says the earlier answer was dropped.
  **The measurement that shaped the fix** (observed: the agent's count over
  18435 cassettes, 2026-09-20): the repeat line is in 4907 cassettes, its pushed
  twin in 572, the eviction notice in 270, and the refusal in 20. So a wording
  change here would have re-keyed 5779 recordings. The new sentence is in none.
  168 cassettes carry the eviction notice and the repeat line together, and the
  gate moved none of them.
  **The deviation is accepted and it is the better reading** (ruled: the
  assistant, 2026-09-21): the brief said the line tells the seat to call again,
  and the agent serves the result instead. The runner holds it at that moment,
  and a seat whose window has just overflowed should not spend a turn fetching
  what is in hand.
  **The gate carries one new red and it is frame 55's**, named and not chased:
  22 failed against a baseline of 22, one red gone, zero new stale.
  **One risk is open and recorded**: after an eviction two consecutive repeats of
  one key are each served whole before the refusal fires. The storm the refusal
  exists for is a single-turn shape, so it is unaffected.
  Line 5 runs next, the silent cuts, and it is the last build line. The port of
  frame 52 follows it on Roman's order.
- Status 2026-09-21 00:41 (rota-02): **all five build lines are built, judged and
  committed. Line 5 is at `0cc624b`.** Rota workflow. A silent cut now has two
  outputs: a notice to the seat through `cut_note`, and a reason on the session's
  own account through `Ctx.cuts` and `session_note`. No new table.
  **Four sites of sixty are converted, and the choice is measured** (observed: the
  agent's count over 18435 cassettes, 2026-09-21). Three are the challenge rows,
  which are the design record's named consequence: the principal's ledger row was
  shorter than the verdict it derives from and nothing said so. The fourth is the
  batch's diff at 20000 characters. The other fifty-six are listed by family with
  a reason, in the pass's report: headline projections, code-view snippets,
  samples inside a view, ids, existence probes, quotes inside a refusal, and two
  that already say "(first part only)".
  **One latent trap is closed by a door** (observed: this session's read of
  `rota/testkit/fixtures.py:914`, 2026-09-21). The fixtures read the text before
  an error's first colon as a refused call whenever it holds a dot. Every
  recorded cut's prefix is prose today, so nothing is miscounted. `_cut`'s
  docstring now says to keep a dot out of `what`.
  **A third test file flakes** (observed: the gate at line 5, 2026-09-21).
  `tests/rota/test_arc_synthetic.py` the gate itself declared flaky, and
  `tests/rota/test_handover.py::test_one_claim_wakes_exactly_one_standby` passes
  47 of 47 three times alone. With `test_screens.py` that is three files, and the
  finding is on frame 48.
  **Price for the five lines: 297433 tokens cumulative in one resumed agent,
  against 666k priced for the whole frame** (observed: the harness usage line).
  The five build lines were priced at 440k of that. No pass reached its cap.
  **The diff review of ends-when line 7 runs now**, read-only on a worktree at
  `0cc624b`, priced 90k. The port of frame 52 waits on one fact: the kit
  repository's path is in no rota record, so this session asked the peer that
  reported the release.
- Status 2026-09-21 00:59 (rota-02): **the diff review of line 7 is in. It
  confirmed a high-severity regression in line 4 and four small defects, and it
  paid for itself twice over.** 135663 tokens against 90k priced, 61 tool calls,
  on a worktree at `0cc624b`. Rota workflow.
  **Line 4's fix defeats the repeat guard for two identical calls in one reply**
  (observed: the review's probe A6, 2026-09-21, CONFIRMED). An answer produced in
  the current turn is never in the current turn's prompt, so after any eviction
  every repeat of one key takes the serve-again branch. The eviction notice is
  sticky, because `_fit` writes it back into the transcript. One reply with three
  identical reads produced 14189 characters, three full results and zero
  refusals, where the same reply before line 4 produced 242 characters, one line
  and one refusal. **That is the s71 storm shape the refusal exists to stop, so
  it is a regression and not a trade.** The repair is in pass 6 now: record the
  turn a key was answered in, and call it evicted only when that turn is earlier
  than this one.
  **Four small defects, all CONFIRMED, all in pass 6**: the at-least-one-row
  guarantee sits outside the budget check, so a 9000-character row renders a
  block at 6123 against 6000 and the seat reads two cuts for one block. The
  overrun limit is the transcript budget and not the window's half, which differs
  at the `max(2000, ...)` floor. `loop.py:53` prints the first error, so an
  overrun line can hide a failed session's reason. `code.diff`'s new notice names
  `code.source`, which `architect/escalate` and `architect/exhausted` do not
  grant, which is the fault this line set out to remove.
  **One records fault of this session is cleared in the same pass**: a comment at
  `rota/roles/api.py:6141-6155` existed twice, one copy carrying the retracted
  claim about the imperative. A reader must not get two answers to one question.
  **One finding is recorded and not fixed, because it is dormant** (observed: the
  review's finding 7, PLAUSIBLE): `backend.complete` also sends
  `tools=schemas`, 13350 characters for `architect/unresolved`, and no budget
  charges it. `native_tools = true` exists in
  `rota/llm/profiles/local-openai-native.toml` and no production caller passes
  it. The frame's premise survives here: two numbers can still add past the
  budget with nothing saying so, and this is the pair.
  **The review's own measurement opened a frame: 603 of 18435 recorded prompts
  exceed the budget `_fit` promises, the worst by 67295 characters.** That is
  frame 56. It unparks the fuzz finding this frame shelved, which said the runner
  reaches no breaking shape today.
- Status 2026-09-21 01:13 (rota-02): **every review finding is repaired and
  committed at `5849bec`, and two doors follow at `1bc8623`.** Rota workflow.
  The repeat guard now records the turn a key was answered in. Measured on the
  review's own shape: one result and one refusal, 6409 characters, against the
  review's 14189 characters and no refusal.
  **One deviation is accepted and it is stricter than the brief asked.** A row
  wider than the whole budget drops every seed rather than keeping one, so the
  block becomes its notices alone. Keeping one seed would let a single giant row
  be cut twice, which was the defect.
  **The two doors carry the knowledge whose absence caused both findings**
  (reasoned: the implementer's where-things-are note, 2026-09-21). The repeat
  machinery has five keys that move together, and both findings it has ever
  produced came from changing one alone. `outcome.errors` has three readers, so
  a line added there is three statements at once.
  **Price so far: 348313 tokens cumulative in the implementer, 135663 in the
  diff review, against 666k priced for the whole frame.** Six passes, none at
  its cap, and the implementer is now past the 350k mark where a fresh agent
  takes over. Its note is in the record above and in the two doors.
  **What is left of this frame**: ends-when line 8, the gate, which runs once
  after frame 52's port lands, and ends-when line 9, the walk. The walk runs from
  a worktree at the closing commit and the frame stays open as validating while
  the next frame starts, because a walk is about nine hours wall.
  **The reserve is checked, at 261k** (observed: `peers`, 2026-09-21 01:13). One
  standby is free at 156k, under the 300k ceiling the port has already installed,
  so a hand-off at 400k has somewhere to go.
- Status 2026-09-21 04:05 (rota-02): **the walk ran and it did not validate the
  frame. Night 88 stalled three times and the frame stays open.** Rota workflow.
  The night ran 02:51 to 04:03 from a worktree at `d192b62`, exit 0,
  `GAUNTLET-DONE`.
  **The size against the night before it** (observed: both databases, 2026-09-21
  04:05): night 88 ran **738 turns in 191 sessions**, where night 87 ran **4062
  turns in 746 sessions**. Night 88 had **3 developer sessions of 191**.
  **All three walks ended on the same report** (observed: `.rota/night88.log`):
  the team gave up on `boundary for @surface:.readthedocs.yaml`, `challenge for
  @claim:items:defines_commands_and_options`, `batch_start for bg_1`, and
  `challenge for @claim:items:default_on_eof`. The walks were quiet after 35, 27
  and 26 steps.
  **So this frame cannot close on this walk.** The walk exists to catch exactly
  this, and it caught something. Whether it caught this frame's own fault is not
  yet known: frame 37 records that the Developer exhausts ten attempts, and frame
  38 records a regression between nights 70 and 86, so a stall may be the
  standing condition. **What this frame changed is the last suspect and not the
  first** (ruled: the brief).
  **The diagnosis runs now, read-only, on the archived night.** The night's
  database was not named by the driver, so this session archived it as
  `.rota/clickI_night88.db`, 738 turns, before the next night could overwrite
  `.rota/clickI.db`. The agent reads the turns of the failing sessions first,
  because a cause goes on the stack only after those turns are read.
  **One finding of the walk is already in hand and it belongs to frame 57**
  (observed: `.rota/night88.log`, 2026-09-21): rota prints its own spill
  measurement, and **nothing spilled**. Every line reads `0.00 GB in RAM`, 16 for
  `qwen3:8b` at 6.89 GB resident and 12 for `qwen3.5:9b` at 5.50 GB resident, at
  a 16384 window. **The two together are 12.39 GB against a 10240 MiB card**, so
  the night swaps models rather than holding both, and the swap is a reload and
  not a spill. That is the shape frame 57 must price.

### 57. Why anything spills into system RAM, and whether it is avoidable (2026-09-21) (Roman)

- Rota workflow, and the meta workflow's own sessions are in scope. **Roman's ask,
  2026-09-21**: find every path by which running rota puts data in system RAM
  instead of GPU memory, say why each one spills, and say whether each is
  avoidable. A seat's wake and a session's whole conversation are two causes of
  one effect, and both count. Analyse all wakes and give summary statistics.
- **Three numbers are already in hand and they set the shape** (observed:
  `nvidia-smi` and the environment during night 88, 2026-09-21 02:54):
  - The 3080 holds 10240 MiB and 8218 are in use with `qwen3:8b` at a 16384
    window. **So the headroom is about 2000 MiB, which is 20 per cent.**
  - The second card is a GTX Titan X of 12288 MiB, idle. It is the register
    recorder's card, and a night does not use it.
  - `OLLAMA_NUM_PARALLEL=1`, so ollama does not multiply the window by a
    parallel count. That removes the largest single multiplier before anybody
    looks for it.
- **Why the question is not already answered by frames 46, 53 and 56.** Those
  three ask what a prompt may contain and what it costs in tokens. This frame
  asks what a prompt costs in bytes of GPU memory, and what happens when the
  bytes do not fit. A prompt inside every token budget can still push the KV
  cache past the card.
- The causes to enumerate, so the next session does not re-derive the list. Each
  needs a measured size and an avoidable-or-not verdict: the model's own weights
  at their quantisation, the KV cache at 16384 and what it costs per token, a
  second model loaded beside the first, ollama's keep-alive holding a model after
  a run, the growth of a session's transcript inside one night, the wake's own
  parts as frame 46 now budgets them, and anything the harness's own sessions
  put on the same machine while a night runs.
- Ends when: one record names every path, its measured size, why it spills and
  whether it is avoidable, with summary statistics over every wake of night 88.
  Priced from the anchors, and it is a fan-out because Roman asked for sub-agents:
  1. Four read-only agents, one cause-family each, 40k apiece, 160k. Buys four
     independent readings that do not see each other's answers.
  2. One agent over night 88's wakes for the statistics: size, parts, duration
     and throughput per wake, 60k. Buys the distribution and the cliff, if there
     is one.
  3. One synthesis in this context, 40k. Buys one record instead of five.
  Total about 260k. **The read of ollama's own offload lines is the load-bearing
  half**: a spill is a fact the server states, so the report must quote it and
  never infer it from a slow wake.
- **Night 88 answers the headline question already, and it reprices the frame**
  (observed: `.rota/night88.log`, 2026-09-21 04:05). rota prints its own spill
  measurement on every model load, and **nothing spilled**: 16 lines read `CARD
  FITS qwen3:8b at 16384: 6.89 GB resident, 0.00 GB in RAM` and 12 read `CARD
  FITS qwen3.5:9b at 16384: 5.50 GB resident, 0.00 GB in RAM`.
  **So the frame's question turns from "why does it spill" into "what is the
  margin, and what would spend it".** Three facts bound the answer. The two
  models are 12.39 GB together against a 10240 MiB card, so the night swaps them
  rather than holding both, and a swap is a reload cost and not a spill. The
  night uses two models by profile: `qwen3:8b` by default and `qwen3.5:9b` for
  critic, developer, terminologist and tester. And the idle 12288 MiB Titan X
  could hold the second model, which is the obvious lever nobody has priced.
  **The reprice: the four cause-family agents drop to two**, 80k, because the
  measurement that would have taken two of them is already printed. The
  statistics pass over night 88's wakes stays at 60k, and the synthesis at 40k.
  Total about 180k, from 260k. The first question for the statistics pass is how
  often the night swapped models and what each swap cost in wall time.
- Waits on: **nothing. Night 88 is in, archived as `.rota/clickI_night88.db`**,
  738 turns and 191 sessions. It is the only night with frame 46's
  budgets in place, and its wakes are the input. The frame also shares that night
  with frames 47 and 53, so one night answers three frames.
- Reasoning: Roman's ask of 2026-09-21, the anchors above, and
  `plans/operating-facts.md`, the GPU and night sections.
- Status 2026-09-21 02:54 (rota-02): pushed by cb5428a2, unclaimed, priced.
  **This session is at 328k and takes no new frame**, so the frame is written to
  be runnable in one step rather than started. Roman asked for it after the walk,
  and the walk ends after this session's hand-off point of 400k, so a fresh
  context runs it. Roman orders it against 54, the shared read, 48, 55 and 49.

### 47. The reply cut fires thirty times more often (2026-09-20)

- Rota workflow. The window rose to 16384 in frame 43 and the reply cap did
  not. So a seat writes a longer reply, and the reply cut now bites where it
  did not before (reasoned: frame 43's closing read of its own night; the
  wider budget is the only input that changed).
- The measurement, which separates the two callers of `_render_cut` (observed:
  `probes/frame43/`, the cross-check run against `.rota/clickI_night87.db` and
  `.rota/clickI_night86.db`): the reply cut fired 140 times of 3599 turns on
  night 87, 3.9 per cent, against once of 825 on night 86, 0.1 per cent.
- The finding is not in frame 43's four numbers and does not change them
  (observed: the same probe). The probe counts a wake cut by its offset, not
  by its words, so a trimmed reply never entered the four rates. Frame 43's
  ends-when is met whatever this frame finds.
- **What is not yet known**: whether a trimmed reply loses content the records
  need. A cut reply that only loses a repeated sentence costs nothing. A cut
  reply that loses a verdict or a tool call is a correctness fault, and frame
  45 is the standing example of a page that named a verdict no row held.
- Two candidate fixes are named on frame 43's record and neither is chosen:
  the reply cap scales with the window, or a seat that writes past the cap is
  told before it is trimmed.
- Ends when: not priced. The first read names the reply cap's site, counts how
  many of the 140 cuts lost a verdict, a ruling or a tool call, and returns a
  category: cosmetic, or on the delivery path. The price follows the category.
- Waits on: nothing. Roman orders it against 46, 48, 45, 41, 42, 38 and 37.
- Waits on: **nothing, and it shares its first read with frame 53**, added
  2026-09-21 00:25 by cb5428a2. The two frames ask one question of the same
  night: of the denied characters and the 140 trimmed replies, how many lost a
  verdict, a ruling or a tool call? One read answers both, about 60k, on frame
  46's walk night rather than on night 87.
- Reasoning: `probes/frame43/README.md`, which says which probe measures
  which finding, and the two night databases it reads.
- Status 2026-09-20 03:00 (rota-52): pushed by 0549dc76, unclaimed, unpriced.
  The frame exists so the obligation stays countable. It was found by the
  frame that caused it, on the night that proved that frame.

### 48. `tests/rota/test_screens.py` is flaky (2026-09-20)

- Meta workflow. One test file gives a new red that the gate itself re-runs
  green. Six flakes on 2026-09-19 across five different tests of that one
  file, with and without machine load, and `test_arc_synthetic.py` flaked once
  (observed: `plans/operating-facts.md`, the flaky-file line, which names
  three of the six by test and by time).
- The read on the record (reasoned: frame 43's implementer): both files run a
  whole screen or a whole arc, and a flake that moves around a file is usually
  shared state, not one bad assertion.
- **The cost is the acceptance line, not the tests.** Every gate run of frame
  43 needed a judgement by hand on a red the gate had already re-run green.
  "Zero new reds" is the stale line's companion in every acceptance this
  repository writes, and it is weakened for as long as one file answers
  differently on two runs of one commit.
- Ends when: the cause is named in a record, and `tests/rota/test_screens.py`
  runs twenty times in a row with zero failures, once on a quiet machine and
  once under a fan-out of agents. Not priced. The first read is what the file's
  tests share: a screen object, a database, a temporary directory or a clock.
- Waits on: nothing. Roman orders it against 46, 47, 45, 41, 42, 38 and 37.
- Reasoning: `plans/operating-facts.md`, the line that says the file is flaky
  and that load is not the cause, with the three named cases and their times.
- Status 2026-09-20 03:00 (rota-52): pushed by 0549dc76, unclaimed, unpriced.
  An earlier version of the operating fact blamed machine load, from one case.
  The second case had no load, so load is not the cause and the file is the
  suspect.
- Status 2026-09-20 17:19 (rota-02): **a second file flakes the same way, and
  the frame does not own it yet** (observed: the gate at `a6e0d5c`, and five
  runs of the test alone, 2026-09-20 17:10).
  `tests/rota/test_handover.py::test_a_newer_watcher_retires_the_older_one` was
  the gate's one new red under frame 46's line 2. It passes 5 of 5 alone, at
  3.3 seconds each, and the pass touched no handover code. So the suite's
  fan-out is the trigger and the file is the second suspect.
  **The line is added here and not to frame 46, because this frame owns the
  fault class.** The frame is unclaimed, so no session's frame is edited. The
  ends-when still names one file. Widening it to two is Roman's order to give.
  **The reading this adds: the shared state is not a screen.** A watcher
  timing test and a screen test have nothing in common but the suite they run
  in, so the suspect moves from what the file's tests share to what the run
  shares.
- Status 2026-09-21 00:41 (rota-02): **a third file flakes, and two of the three
  are wall-clock tests** (observed: the gate at frame 46's lines 2 and 5,
  2026-09-21). `tests/rota/test_arc_synthetic.py::test_arc_delivery_loop_slices_batches_and_tests`
  came up red under the gate and the gate re-ran it green itself.
  `tests/rota/test_handover.py` has now given two different reds under the gate,
  `test_a_newer_watcher_retires_the_older_one` and
  `test_one_claim_wakes_exactly_one_standby`, and the whole file passes 47 of 47
  three times alone.
  **So the ends-when's one file is now three**, and widening it is still Roman's
  order to give. The first read changes with the evidence: `test_handover.py`'s
  two reds both sleep and both hold a deadline, so the suspect is a deadline
  measured against a machine that is running sixteen agents, and not shared
  state.
  **The cost is now counted.** Four of frame 46's five gate runs needed a
  judgement by hand on a red the gate had already re-run green, or on a red in a
  file the pass never touched.

### 56. 603 recorded prompts exceed the budget `_fit` promises (2026-09-21)

- Rota workflow. `_fit` promises that a turn's transcript fits
  `_fit_budget(num_ctx, len(system))`. **603 of 18435 cassettes hold a prompt
  that does not, and the worst exceeds it by 67295 characters** (observed: frame
  46's diff review, read-only SQL over `tests/rota/cassettes.db`, 2026-09-21).
- **This unparks a finding frame 46 shelved.** That finding said `_fit`'s promise
  is not a theorem, a fuzz of 4000 transcripts broke it 1540 times, and **the
  runner reaches neither breaking shape today**. The register says the runner
  reaches some shape, 603 times.
- **What is not known**: whether the 603 are historical, recorded before a cap
  that now holds, or whether a live path builds a prompt without `_fit`. Frame
  46's line 1 measures only what `run_session` assembles, so a path that does not
  go through `run_session` is still unmeasured.
- **Why it matters beyond tidiness**: a prompt over `num_ctx` is collapsed by
  ollama to `num_ctx / 2 + 2` with the tail kept, which cuts the brief off the
  front. That is the fault the halving exists to prevent, and these 603 prompts
  are the shape that reaches it.
- Ends when: the cause is named in a record, and either the 603 are shown to be
  historical with the reason, or the live path that overruns is named and a test
  holds the line. Priced: one read that groups the 603 by role, mode and date,
  and checks whether each came through `run_session`, 40k. Buys the difference
  between an old scar and an open wound. The repair's price follows the cause.
- Waits on: nothing. Roman orders it. It sits above 54 only in the file, and
  Roman's order of 2026-09-21 does not name it yet.
- Reasoning: frame 46's status line of 2026-09-21 00:59, and the parked finding
  in frame 46's status line of 2026-09-20 16:50.
- Status 2026-09-21 01:00 (rota-02): pushed by cb5428a2, unclaimed, priced. Found
  by the diff review while probing a different point, which is the second finding
  this frame's reviews produced that its tests could not.

### 54. The register's match is narrower than the cassette key (2026-09-20) (Roman)

- Meta workflow. `rota/tools/casestatus.py:77` matches a recording on case id,
  `prompt_hash` and model. The cassette key covers more than that: the prompt's
  text, the mode prompt and `num_ctx` (observed: the file's own comment at
  `:71-77`, and the cassette table's columns, 2026-09-20).
- **One narrow key gives two opposite symptoms.** A `num_ctx` change leaves no
  row at the current hash, so the case reads stale, and that is frame 49's 72. A
  prompt-text change leaves the hash alone, so the rows still match and the case
  reads green while the suite cannot replay it (observed: frame 46's line 3,
  2026-09-20, where the gate said STALE and `casestatus` said 72 before and 72
  after).
- **So "zero stale" cannot gate.** It is a line in every acceptance this
  repository writes, frame 46's included, and the true count is unknown.
- **A second finding for the same frame: the register runs at 12288 and the
  nights run at 16384** (observed: every cassette's `num_ctx`, 2026-09-20). No
  cassette was ever recorded at 16384, so the register does not measure the
  window frame 43 shipped.
- Ends when: `casestatus` matches everything the cassette key covers, a test
  asserts that a prompt-text change makes a case read stale, and the true count
  is measured and recorded. Priced from the anchors: the first read names the
  key's fields against the report's match, 20k. Buys the number nobody has. The
  repair and its test, 80k. Buys an acceptance line that can fail. The true
  count then replaces 72 in frame 49, and the re-records are frame 49's work and
  not this frame's.
- Waits on: nothing. **Roman ruled it a frame of its own, above 49, on
  2026-09-20** (ruled: Roman, asked with three other options and the fold into
  49 recommended).
- Reasoning: frame 46's status line of 2026-09-20 18:59, and the comment at
  `rota/tools/casestatus.py:71-77`, which names the fault and predates the frame.
- Status 2026-09-20 19:00 (rota-02): pushed by cb5428a2, unclaimed, priced. The
  frame exists so the obligation stays countable. This session holds frame 46
  and takes no new frame.

### 55. A recorded green does not reproduce live (2026-09-20)

- Meta workflow. `L1-TE-survey-an-area-for-its-terms` has 10 of 10 green on load
  `qwen3:8b@248599`. It replayed green twice on 2026-09-20, then failed 20 of 20
  on four fresh recordings at the same model, the same 12288 window and
  temperature zero (observed: the register's own rows and four re-records,
  2026-09-20 17:50 to 18:40).
- **The failure is stable, so it is not noise.** In all 20 runs the seat calls
  `code.area`, `glossary.amend`, `glossary.consult`, `problem.baseline`,
  `surveys.attest` and `surveys.consult`, and never `code.source`, which the case
  requires.
- **No line of frame 46 causes it** (observed: the bisect in frame 46's status
  line of 18:59). The two source files at `88f476a`, before the frame's first
  commit, record 0/5.
- **What is not known**: whether the model behind the tag changed, or whether a
  fresh run builds a prompt that differs from the recording in a way the
  cassette key does not capture. The green recordings are in
  `.rota/cassettes_backup_2026-09-19-frame43-closing.db`.
- **This is the 23rd known red, and it is not restored to green.** Restoring the
  backup's cassettes would hide a regression behind a cassette. Every acceptance
  that says "zero new reds" now counts 23 and names this frame for the 23rd.
- Ends when: the cause is named in a record, and the case is either re-earned
  green or written off with a reason. Priced: one probe that sends the backup's
  recorded prompt to the live model at the same pins and compares the completion,
  40k. Buys the answer to whether a cassette is still evidence. The repair's
  price follows the cause.
- Waits on: nothing. Roman orders it.
- Reasoning: frame 46's status line of 2026-09-20 18:59, which carries the
  bisect, and the backup named above.
- Status 2026-09-20 19:00 (rota-02): pushed by cb5428a2, unclaimed. Found while
  judging frame 46's line 3. The re-records that found it were run on the
  standing rule that a re-record is cheap. **The rule holds on tokens and it is
  wrong about consequence**: a re-record spends a green that the live model may
  not give back.
- Status 2026-09-21 00:17 (rota-02): **Roman ruled the re-record rule stands**
  (ruled: Roman, 2026-09-20, asked with a snapshot-first option recommended).
  A re-record runs without asking. A spent green is the price of the truth, and
  the truth is what an acceptance needs. **So this frame is a finding and not a
  loss**, and the sentence above is the assistant's reading, now overruled on
  what to do about it. The register holds what the model still does.
  The cause is still unnamed, so the frame stays open on its own ends-when.

### 49. The register is 72 cases stale and no frame owns it (2026-09-20)

- Meta workflow. A stale case is unmeasured, not bad. It means the composed
  prompt moved and nobody has re-earned the result since. Today 72 of 128
  model-facing cases are stale, against 47 green and 9 failing (observed:
  `python -m rota.tools.casestatus`, run 2026-09-20 03:10).
- **The obligation belongs to nobody.** Frame 43 is closed. Its record said in
  advance that the stale line could not accept it, because `num_ctx` and a
  mode prompt are in the cassette key and not in `rota/tools/casestatus.py`'s
  match (observed:
  `plans/archive/context-caps-design-2026-09-18.md`, section 9.6). So the
  frame closed on its night, correctly, and the register was left where it
  was.
- **When the 72 appeared is not known, and the record disagrees with itself**
  (observed: two sources). The gate's stored baseline at f3a7e41, 2026-09-19
  05:22, holds `"stale": 0`. Frame 43's status of 15:38 on the same day reads
  the gate whole at 6408b64 and says zero stale. Every commit after 6408b64
  touched only `plans/`, `.claude/` and `probes/`, and none of those composes a
  prompt. Night 87 ran after that gate. The first read is therefore whether a
  night writes the register, and what a case's prompt hash is taken over.
- **This frame stales nothing of its own** (observed: this session's own
  check, 2026-09-20 03:10). The count is 72 with the handover fix in the tree
  and 72 without it, so the door of `f06ffbf` is not a cause.
- Ends when: the cause is named in a record, the 72 are re-recorded or
  written off case by case with a reason, and `casestatus` reads zero stale.
  Not priced. A re-record is cheap and needs a quiet machine, so the price is
  mostly wall time and not tokens (observed: the standing guidance that a
  re-record runs without asking).
- Waits on: a quiet machine. The scope of frame 46 is running now, and the
  register's re-record contends with it for the GPU.
- Waits on: frame 54, added 2026-09-20 19:00 by cb5428a2. **The 72 is not the
  count.** The report's match is narrower than the cassette key, so a case whose
  prompt text moved reads green here. Re-recording 72 cases before the count is
  right would re-earn the wrong set. Frame 55 adds the second reason: a
  re-record can spend a green the live model does not give back.
- Reasoning: `plans/archive/context-caps-design-2026-09-18.md`, section 9.6,
  and the gate baseline at `.rota-gate.json`.
- Status 2026-09-20 03:10 (rota-52): pushed by 0549dc76, unclaimed, unpriced.
  Roman orders it. It sits here because it was found here, and not because it
  outranks frame 45. **The reason it is a frame at all**: "zero stale" is a
  line in every acceptance this repository writes, and a line that reads 72
  cannot gate anything. An acceptance that nobody can fail is not an
  acceptance.

### 53. Does a prompt get more than half the window? (2026-09-20) [unruled]

- Rota workflow. A capacity question, split out of frame 46 on 2026-09-20
  because frame 46 is a design frame and this is not its question.
- `_fit_budget` gives a turn `max(2000, int(num_ctx / 2 * 3.97) - system)`
  characters (observed: `rota/core/runner.py:566`). The halving exists
  because ollama collapses a prompt over `num_ctx` to `num_ctx / 2 + 2` and
  keeps the tail, which cuts the brief off the front. **So a 16384 window
  carries at most 8192 tokens of prompt, and frame 43's rise bought the
  lower half only** (observed: night 87's largest prompt was 8191 tokens,
  two characters under exactly half).
- **The halving is Ollama-specific** (observed: `rota/llm/llm.py:443`).
  `LiteLLMBackend` never sends the window, so on those profiles the halving
  discards half the declared budget and defends against nothing. The
  fraction belongs to the backend, not to "the window".
- The number that argues for the frame: night 87's cuts denied 8784628
  characters against 6946907 delivered, so the caps removed 1.26 times what
  they delivered (observed: frame 46's design review, probe 4).
- **The number is not yet an argument for raising anything**, because
  nothing says the denied characters were load bearing. A denied repeat
  costs nothing. A denied verdict or tool call is a correctness fault. Frame
  47 asks the same question about trimmed replies, so the two share a first
  read.
- Ends when: not priced. The first read says how much of the denied demand
  was load bearing, and only then does the fraction become a ruling. Raising
  it needs frame 46's line 1 first, because nothing measures the assembled
  prompt before the send.
- Waits on: **frame 46's walk, not its line 1** (reasoned: the assistant,
  2026-09-21, recommending to Roman). Line 1 is built and committed at
  `cb0649c`, so the measurement this frame needed exists. The number it needs
  does not. The 8784628 denied characters are night 87's, and night 87 ran
  before `decisions.search` had a budget. The design review named that op as
  55.5 per cent of all pushed characters and the upstream cause of the denial,
  and line 2 capped it at 6000 characters on 2026-09-20. So the denial figure
  has moved and nobody knows by how much. Frame 46's ends-when line 9 already
  pays for a walk, so the fresh number costs this frame nothing.
- Reasoning: `plans/archive/prompt-budget-design-2026-09-20.md`, section 5,
  and the design review's finding 6.
- Status 2026-09-20 16:45 (rota-52): pushed by 0549dc76, unclaimed, unruled.
  Split out so a capacity question stops gating a coherence frame.
- Status 2026-09-21 00:25 (rota-02): **the halving stays, and the frame waits for
  one shared read** (reasoned: the assistant's recommendation to Roman,
  2026-09-21; Roman asked for it rather than picking from four). The read is one
  question for this frame and frame 47 together: of the denied characters and the
  140 trimmed replies, how many lost a verdict, a ruling or a tool call? About
  60k. A cosmetic answer closes both frames. An answer on the delivery path
  prices both.
  **Two options are recorded as rejected, with the reason** (reasoned: the same
  recommendation). Making the fraction the backend's is right in principle and
  ships unmeasured: no cassette covers a `LiteLLMBackend` profile and nothing
  runs one today, so the shape is recorded and the work waits for a profile that
  uses it. Raising it on Ollama needs a margin for the chat template that nobody
  has measured, and a miss cuts the brief off the front, which is the fault the
  halving exists to prevent.
  **A third finding of 2026-09-20 belongs to this frame's evidence, not its
  ends-when**: every cassette in the register was recorded at `num_ctx` 12288 or
  8192, so no recording measures the 16384 window the nights run at. Frame 54
  owns the repair.

### 45. An abandoned tick reached the page as a finding (2026-09-18)

- Rota workflow. Night 86's pages m24 and m27 told the principal that five
  claims about constraints are falsified: format_filename, paramtype,
  intrange, floatrange and float. The Critic falsified none of them
  (observed: `plans/archive/principal-pages-2026-09-18.md`, fact 7). The
  `challenges` table holds seven rows and none for the five. The
  `tick_attempts` table holds all five Critic challenge ticks, each
  quarantined at three attempts. One Liaison session, s103, woken on
  `tick:blindspot`, wrote all five `ledger` rows. The principal approved
  all five, so the record says a person retired five stability constraints
  on public names of click on the strength of a verdict that does not
  exist.
- Ends when, each line priced from the anchors, walls apart:
  1. A scope report names what `tick:blindspot` writes, where the wording
     comes from, and what the write path allows: 40k. Buys: the fix hits
     the real writer, not the page.
  2. The fix with a pinned test, so a quarantined tick cannot reach a page
     as a finding: 90k (cold 70k, one resumed pass 20k). Buys: the page
     cannot name a verdict that no row holds.
  3. A diff review on a worktree at the commit: 65k. Buys: a write path
     change is read by a context that never wrote it.
  4. The gate green before the commit, the stale line read: 12k.
  Total: 207k in agents. A walk is due, because the frame touches the write
  pipeline. The walk is a full night, about 20k in this context.
- Waits on: nothing. Roman orders it against frames 41, 42 and 43.
- Reasoning: `plans/archive/principal-pages-2026-09-18.md`, fact 7, and the
  parked item of frame 34's fix pass, which says a door that lands a ruling
  cannot read the words.
- Status 2026-09-18 19:11 (rota-ff): pushed by 9108c499 from frame 40's
  record, unclaimed. The fault is on the delivery path and the fix is
  cheap.
- Status 2026-09-18 19:27 (rota-ff): renumbered from 44 to 45. Session
  0ca1c29e claimed the number 44 for the meta transfer two minutes after
  this frame was pushed. The frame is otherwise unchanged.

### 38. The regression between night 70 and night 86 (2026-09-18) (Roman)

- Rota workflow. Sentence two merged cold on night 70. On night 86 the
  same sentence cut a batch, committed, and the Developer then exhausted
  ten attempts on its tests (observed: `plans/archive/night86-2026-09-18.md`).
  Either something regressed, or the night 70 merge was luck read as
  capability. Roman ruled the investigation at the grill, 2026-09-18.
- Ends when: the cause is categorised and on the stack as one of two
  (ruled: Roman, 2026-09-18, "what went wrong is either in the model
  context, meaning data, tooling or environment, or in the model
  itself, so we need to categorize that"):
  1. **Model context**: what the Developer was given differs between the
     two nights. The data, the tooling, the environment, the prompt.
  2. **The model itself**: the Developer was given the same thing and
     answered worse.
  The read is direct, because both run databases are on disk:
  `.rota/clickI_n70_merged.db` and `.rota/clickI_night86.db`. Compare
  what the Developer was shown, what it called, what came back, and what
  the test failures were. 90k in agents. Buys: a category, which decides
  whether step 2 of the order returns.
- Waits on: nothing.
- Reasoning: `plans/archive/night86-2026-09-18.md`, and frame 4, step 2
  of the order, ruled not needed on 2026-09-15.
- Status 2026-09-18 08:05 (rota-dc): pushed, unclaimed. If the category
  is the model itself, step 2 of the order returns and a larger
  Developer is back on the table. If it is the model context, the fix is
  cheaper and step 2 stays closed.

### 37. The Developer exhausts ten attempts on the tests (2026-09-18)

- Rota workflow. Night 86 cut a batch, took a worktree and committed at
  `da5e7e8`. The Developer then woke on `tick:tests_failing` nine times
  and on `tick:exhausted` at attempt 10 of 10. Every session committed.
  The batch stayed `running`, with 37 test runs and no verdict of any
  result. The Critic woke 22 times on `tick:challenge` only and never on
  a review tick, because a review needs a batch whose tests pass
  (observed: night 86's run database, recorded in
  `plans/archive/night86-2026-09-18.md`). The wall is no longer in the
  records path. It is in the work.
- Ends when: not priced. The frame needs a grill with Roman first,
  because the question is where a 9B model stops, and that is the
  composition's own question. Sentence two merged cold on night 70 at an
  older commit, so this is not a permanent ceiling. The first read is
  what changed between night 70 and night 86.
- Waits on: frame 38, which categorises the cause.
- Reasoning: `plans/archive/night86-2026-09-18.md`, and frame 13 in
  `plans/archive/stack-2026-09-16.md`, where night 82 was stuck on
  `exhausted` at sentence three.
- Status 2026-09-18 07:35 (rota-dc): pushed, unclaimed, unpriced. The
  same wall now stands one sentence earlier than on night 82, because
  sentence two's earlier walls are gone.
- Status 2026-09-18 07:40 (rota-dc): the night ended at GAUNTLET-DONE,
  203 sessions. **Sentence three cut a batch too**, `bg_2` for
  `show_python_version`, its own request, after 23 steps and 4 asks
  (observed: the final run database; both statements are `ratified`).
  Sentence three has never merged cold and night 82 was stuck on
  `exhausted` at 80 steps. The records path now carries both sentences
  to a batch, and both stop at this frame's wall. `bg_2` is `pending`
  with no commit, because the night ended first.

### 41. A sub-agent drives the walk as the principal (2026-09-18) (Roman)

- Rota workflow. `probes/walk.py` has the seam already: `class
  Principal` with one method, `respond(ask)`, which receives the
  rendered page and returns words or a per-item verdict. A sub-agent
  slots in there. It is a diagnostic, not a replacement (ruled: Roman,
  2026-09-18). Its output is understanding, which then builds the
  deterministic principal of frame 42, or it shows where the system
  fails and needs fixing. Underlying assumption, ruled by Roman: the
  agent principal gives only reasonable answers.
- Ends when: a night runs with an agent principal and its record says,
  per page, what the agent answered and what the system did with it. It
  must exercise at least one path the yes-only principal never reaches,
  the term-collision tick being the known one, which frame 34's fix has
  still never walked. Not priced until frame 40's record exists. Opus is
  allowed and cost is not a constraint (ruled: Roman, 2026-09-18).
- Waits on: nothing now. Frame 40 closed on 2026-09-18 with
  `plans/archive/principal-pages-2026-09-18.md`. It names the four page
  kinds, the ten pages whose reply was not fully reasonable, and the paths
  no principal has walked: nothing was contested on either night.
- Reasoning: `probes/walk.py:81-110`, the `Principal` class and the
  existing `WALK_CONTEST` principal by moment, which is the half-built
  form of this idea.
- Status 2026-09-18 08:05 (rota-dc): pushed, unclaimed, unpriced.

### 42. The designed principal, and whether zero temperature is consistent (2026-09-18) (Roman)

- Rota workflow. A deterministic principal built by hand to represent a
  careful person, option B of the grill (ruled: Roman, 2026-09-18). It
  keeps nights comparable, which an agent principal cannot.
  **The concern on the record** (reasoned: the assistant raised it and
  Roman accepted the underlying assumption): a principal tuned until the
  run passes is a test that always passes. The principal encodes what a
  plausible person would say. A run that still fails is then a finding,
  not a tuning target.
  **The assumption to validate** (ruled: Roman, 2026-09-18): that a
  zero-temperature model is consistent enough to give similar responses
  to the same problem set. Nothing measures that today.
- Ends when: two lines. First, the consistency assumption is measured:
  the same problem set replayed N times at temperature zero, with the
  spread reported. Second, the designed principal exists and a night
  runs on it. Not priced until frame 40's record exists.
- Waits on: frame 41. Frame 40 closed on 2026-09-18 with
  `plans/archive/principal-pages-2026-09-18.md`. A designed principal needs
  an answer for four page kinds, and the understand kind is 23 of the 32
  pages.
- Reasoning: the grill of 2026-09-18.
- Status 2026-09-18 08:05 (rota-dc): pushed, unclaimed, unpriced.

### 33. Finding 42: the code index refreshed after a commit (Roman, 2026-09-17)

- Rota workflow. Step 3 of the order. The code index is built at
  onboarding and never refreshed after a commit, so a batch's own
  symbols are invisible to later probes, and the touch prediction and
  sentence three's first prediction read a stale index (ruled: Roman,
  2026-09-17: the next frame; reasoned: `rota/COMPLETION.md`, "The order
  from here", step 3, a core fact that lands before breadth).
- Ends when, each line priced from the anchors, walls apart:
  1. A scope report names the index's writers and readers, what a
     commit changes, and the hook points for a refresh: 50k. Buys: the
     design names real paths, not guessed ones.
  2. A design record, reviewed before any code: 80k (the review 70k,
     the record 8k). Buys: the refresh's contract, per run or per
     worktree, is fixed before an implementer reads it.
  3. The refresh is built with a pinned test: after a commit, the
     index lists the batch's new symbols and a probe finds them: 110k
     (cold 80k, one resumed pass 30k). Buys: a batch's own symbols are
     visible to later probes and to the touch prediction.
  4. A diff review on a worktree at the commit, its fixes in: 110k
     (review 65k, second look 20k, fix pass 25k). Buys: the write
     pipeline change is read by a context that never wrote it.
  5. The gate green before each commit, the stale line read: 12k.
     Buys: no new red and no stale case hides behind the change.
  6. A full night on click from a worktree at the closing commit, its
     summary read: 20k in this context, about two hours wall. Buys:
     the seats on the delivery path see the refreshed index.
  Total: 382k in agents, about 120k in this context.
- Waits on: nothing. The scope agent runs now.
- Reasoning: `rota/COMPLETION.md`, "The order from here", step 3. The
  design record will be `plans/archive/index-refresh-design-2026-09-17.md`.
- Status 2026-09-17 14:25 (rota-02): pushed. The scope report is out to a
  reviewer-type agent, read-only, cap 60k.
- Status 2026-09-17 14:52 (rota-02): the scope report is in, 76k on the
  harness line against 50k priced and a 60k cap, 52 tool calls
  (observed: the harness usage). Saved as
  `plans/archive/index-refresh-scope-2026-09-17.md`. The design record
  is written: one refresh function with a main flag, three hooks, the
  freshness comparison skipped while a batch runs, five pinned tests.
  The judgement call, the skip against an area_hashes table, is in the
  record for Roman's read. Design review out, cap 80k.
- Status 2026-09-17 15:18 (rota-02): design review in, 78k on the harness
  line against 70k priced, 34 tool calls, eight points and three
  findings outside them. Two parts of the design overturned (observed:
  the reviewer's probes, recorded in the design record's last section):
  the freshness skip breaks an existing test and lifts on abandon, so
  an `area_hashes` table replaces it; no cancel path destroys a
  worktree, so hook 3 keys on abandon and defer. One high defect caught
  before code: `walk` tests the absolute path against `SKIP_DIRS`, so a
  worktree under `.rota` walks to nothing and the first commit would
  have emptied the index. Implementer out, pass 1, cap 120k, on Opus.
- Status 2026-09-17 15:24 (rota-02): implementer pass 1 in, 125k on the
  harness line against 80k priced and a 120k cap, 96 tool calls, 32
  minutes (observed: the harness usage). Twelve files, 322 insertions,
  seven pinned tests in `tests/rota/test_index_refresh.py`. Six
  deviations, all accepted (reasoned: each stated with its cause in the
  report): the missing-root refusal sits in `build`, two CLI tests
  create their directory first, `identity.py` declares the new table,
  `project_commit` is written only when non-empty, the area set comes
  from the pre-build snapshot. Gate by the implementer and by the
  assistant on the same tree: zero new reds, zero stale, 1886 passed,
  531 s each. Committed at 01b1d4b. Diff review next, on a worktree at
  that commit.
- Status 2026-09-17 15:30 (rota-02): diff review in on a worktree at
  01b1d4b, 91k on the harness line against 65k priced, 27 tool calls,
  eight points confirmed and seven findings, two high (observed: the
  reviewer's probes): a conflicted merge re-raises before the main
  refresh, so the index keeps describing a deferred worktree; and the
  three refresh helpers catch two exception types only, so a foreign
  error after a landed session runs session_fail on rows that are on
  record. Five low: the CLI traceback on a missing root, an empty
  area_hashes table reads as fresh after init_db on an old database,
  the failure record has no reader, the fixture records a gitlink, a
  duplicated helper. Fix pass sent to the same implementer, cap 60k,
  with four pinned tests and a gate run at its end.
- Status 2026-09-17 16:17 (rota-02): fix pass in, 44k for the pass on the
  harness line (169k cumulative for the agent), 52 tool calls, 38
  minutes (observed: the harness usage). All seven findings fixed, four
  pinned tests, eleven in the file. One deviation accepted (reasoned:
  the fixture's `.gitignore` reaches nine L1 prompts and turned them
  stale, so the exclude lives in `.git/info/exclude`, outside the
  tree). Gate by the implementer and by the assistant on the same tree:
  zero new reds, zero stale, 1890 passed. Committed at 3ab5c73. Actual so
  far against the 382k estimate, walls apart: scope 76k, design review
  78k, implementer 169k over two passes, diff review 91k, the
  assistant's gate runs 12k: 426k. Walls: none. Second look by the
  reviewer on the fix commit, then the walk: night 83 on click from the
  worktree at 3ab5c73, shipped profile.
- Status 2026-09-17 16:20 (rota-02): validating. Second look in, 11k for
  the pass on the harness line: six findings fixed, one partly, two new
  lows (observed: the reviewer's probe E and its read): the failure row
  `index:<batch>` is never cleared after a good refresh and the runner
  never writes it, and `--force` wipes the run before the root check.
  Neither is on the delivery path (reasoned: one is a note's wording,
  one is CLI ordering), so night 83 runs now from the worktree at
  3ab5c73 while pass 3 fixes the two lows in the main checkout, cap
  25k. The closing commit will be pass 3's; the walk's commit is
  3ab5c73, a stated deviation from the brief's line. The walk's
  summary must show a Developer probe after a commit that finds the
  batch's symbol, and the survey sessions per merge.
- Status 2026-09-17 16:53 (rota-02): pass 3 in, 14k for the pass on the
  harness line (183k cumulative for the agent), 20 tool calls. Both
  lows fixed, two pinned tests, no deviation. Gate by the implementer
  and by the assistant: zero new reds, zero stale, 1892 passed. The
  closing commit is 7e53796. Actual against the 382k estimate, walls
  apart: scope 76k, design review 78k, implementer 183k over three
  passes, diff review 102k over two, the assistant's gate runs 18k:
  457k. Walls: none. Night 83 runs at 3ab5c73: onboarded 16:19 to
  16:50, sentence one from 16:50. The frame closes on the walk's
  result.
- Status 2026-09-17 18:22 (rota-02): night 83 killed at 18:20. It looped
  on sentence one before any batch: 144 wakes in 84 minutes, no batch,
  no commit, so nothing of this frame ran (observed: the run database,
  sessions s232 to s243, one three-session cycle four times). The loop
  is on frame 2. Night 84 relaunched from the same worktree at 3ab5c73
  from sentence two, which merged cold on night 70 and exercises the
  commit hook and the merge hook. Night 83's database is kept as
  `clickI_prev.db` in the night state directory.
- Status 2026-09-17 20:40 (rota-02): night 84 looped the same way from
  sentence two, 307 sessions, no batch (observed: the run database).
  Killed at 20:39. The wall is frame 34. The walk waits on it and runs
  as night 85 from a worktree at frame 34's closing commit.
- Status 2026-09-18 02:13 (rota-dc): claimed by 75d12c2b. The frame
  stays validating. Its walk is night 85, which waits on frame 34's
  diff review.
- Status 2026-09-18 08:40 (rota-dc): **hand-off.** Session 75d12c2b
  releases this frame at the stack commit below. The frame is unchanged
  and unwalked. Its code is built, reviewed twice and gated. It needs a
  merge, and a merge waits on frame 37, which waits on frame 38. A fresh
  peer claims it.
- Status 2026-09-18 07:55 (rota-dc): the frame stays open and unwalked.
  Night 86 got further than any night of this series, to two batches and
  one commit, and still never merged, so the refresh hook never fired
  (observed: `config.project_commit` still names the base `2c8cd3a` at
  the end of the night). The code is built, reviewed twice, gated and
  unproven on a night. The walk needs a merge, and a merge waits on
  frame 37.
  The gate holds at 8b15af8 on a quiet machine: zero new reds, zero
  stale, 1915 passed, 509 s (observed: the gate's own summary). That is
  the trusted number. The earlier run beside night 86 gave three reds,
  all three named flaky and all three green on its own re-run.
- Status 2026-09-18 17:07 (rota-ff): claimed by 9108c499 at the hand-off.
  The frame stays validating and unwalked. It cannot advance today. The
  walk needs a merge, a merge waits on frame 37, and frame 37 waits on
  frame 38.
- Status 2026-09-21 00:20 (rota-02): **the claim of session `9108c499` is
  released on Roman's word** (ruled: Roman, 2026-09-21, asked with three other
  options). That session has ended, so the id in the heading named a seat no
  message could reach. The frame is unclaimed, it keeps its place in Roman's
  order, and it stays validating. Nothing else about it changed.

### 4. Roman's order from here (2026-09-14 12:58) (Roman)

- (ruled: Roman's order, `rota/COMPLETION.md`, "The order from here") The
  road to the loop that merges cold on click. Steps: 1 the benchmark, 2
  routing a larger model, 3 finding 42, the code index refreshed after a
  commit, 4 the language seam, 5 breadth, the other two lineage
  repositories cold and then a non-Python repository, 6 the long-run
  noise test after sentence three merges, 7 ship the loop. Do not:
  rewrite the core, lower the cap, more nights on sentence two as if
  doors were the answer.
- Ends when: step 7 ships the loop.
- Waits on: the frames above it, one per step. Step 5 is frame 2's work.
- Reasoning: `rota/COMPLETION.md`, "The order from here", and frames 5
  to 15 in `plans/archive/stack-2026-09-16.md`.
- Status 2026-09-14: step 1 done; frame 8 decides step 2. Frames 5 to
  15 are in the archive.
- Status 2026-09-17 12:37 (rota-19): claimed by cc3d4e4e at 94511e3 for the
  grill with Roman, the first frame under the tooling chain. Step 2 is not
  needed (reasoned: `rota/COMPLETION.md`, update 2026-09-15 01:10, the 9B
  merged sentence two on night 70 with the doors of findings 66 to 73).
  Sentence three is unmerged: night 82 stuck on exhausted, 80 steps
  (observed: frame 13's close in `plans/archive/stack-2026-09-16.md`).
  The next step is Roman's ruling at the grill: finding 42, the seam, or
  breadth. Recommended: finding 42.
- Status 2026-09-17 13:52 (rota-02): claimed by 3b4093c6, the same session forked (ruled:
  Roman, 2026-09-17). The one order: seven steps as COMPLETION.md gives
  them, with finding 42 as step 3 (observed: the stack's list had six).
  Step 1 done, step 2 not needed. The next frame is step 3 on Roman's
  word at the grill. Frames 23, 24, 25, 28 and 31 closed by ruling; the
  first build frame's closing status carries their measurements.
- Status 2026-09-18 02:13 (rota-dc): claimed by 75d12c2b. Step 3 runs
  now as frames 33, 34 and 35. Step 4 and step 5 wait on night 85.
- Status 2026-09-18 17:07 (rota-ff): claimed by 9108c499 at the hand-off.
  Step 3's code is built, reviewed twice and gated, and it stays
  unwalked. Frame 38 decides whether step 2 returns.
- Status 2026-09-21 00:20 (rota-02): **the claim of session `9108c499` is
  released on Roman's word** (ruled: Roman, 2026-09-21, asked with three other
  options, one of which was to close this frame). That session has ended. **The
  frame stays open and is not discharged**: Roman's order of 2026-09-20 named
  frame 46 and then the table in order, which is an order inside this frame's
  step list and not a replacement for it. Steps 4 to 7 are still unbuilt.
  The frame is unclaimed and keeps its place at the bottom of the stack.

### 2. The gauntlet on the lineage (goals 3 and 10)

- (ruled: goals 3 and 10 of the plan) Three lineage repos, three sentences each, unattended. Click sentence
  one merges (nights 49, 50). Sentences two and three do not yet.
- Ends when: the lineage is walked and every fault is a door or a case.
- Waits on: frame 4, whose step 5 is this frame's breadth.
- Reasoning: `rota/COMPLETION.md`, goals 3 and 10.
- Status 2026-09-16: open behind frame 3. The latest nights are frames
  11 to 13 in `plans/archive/stack-2026-09-16.md`.
- Status 2026-09-17 13:52 (rota-02): sentence two merged on night 70. Sentence three is
  unmerged: night 82 stuck on exhausted at 80 steps (observed: frame 13's
  close). Three partials ride the gauntlet, A7, D3 and A1's cold walks
  (ruled: Roman, 2026-09-17). The night summary owes three lines for
  them: a stray touch judged, a failed verdict chained, a contest
  landed. A small frame on the night script, priced when the order's
  frames run.
- Status 2026-09-17 14:12 (rota-02): D3's owed night does not exist yet
  (observed: a reviewer probe of the night databases, 24k). Nights 81
  and 82 hold no verdicts row of any result: the Critic woke on the
  challenge tick only and never reached the review tick, and the
  Developer read an empty verdicts table three times on night 82. Rota
  workflow. The "failed verdict chained" line of the night summary is
  the measurement that is missing.
- Status 2026-09-17 14:25 (rota-02): the lineage is tips, click and icalendar
  (ruled: Roman, 2026-09-17). Step 5 of the order, breadth cold, walks
  tips and icalendar with what exists.
- Status 2026-09-17 18:22 (rota-02): a fault from night 83, sentence one
  cold (observed: the run database's sessions s232 to s243 and
  `live_click.md`). The term collision `group` against `Group` loops:
  the Liaison asks the principal, the yes-only principal answers with
  the constraint text, the Liaison relays, and the Terminologist logs
  every cycle that the relayed message m107 carries no principal
  verdict in its resolved refs, so it cannot adopt the observed senses
  without a ruling. The term-collision tick re-fires. Every session
  commits, so no attempt cap fires; the walk ends at its step cap
  only. Rota workflow. Sentence one had not run cold since night 50.
  The cause goes on the stack after the turns are read: what the
  Liaison relayed, what the Terminologist read, what each committed.
  Not frame 33's.

### 1. The end state (plan agreed 2026-09-10)

- (ruled: the destination, agreed 2026-09-10) A careful person runs rota alone on a small Python repository and
  gets a merged change they can read. Honest about where small models
  stop. Ten goals in COMPLETION.md: 1, 2, 7, 9 done; 4 and 8 measured
  and ongoing; 3 and 10 are frame 2; 5 and 6 fed by it.
- Ends when: every partial in COMPLETION.md's core section is built,
  click and two more lineage repositories merge cold, the register is
  green or attributed on the shipped profile, and Roman declares
  finished (ruled: Roman, 2026-09-17: the core section stays the
  definition of core).
- Waits on: frame 2.
- Reasoning: `rota/COMPLETION.md`, and `plans/composition.md`, Purpose.
- Status 2026-09-16: the bottom frame. Open.
- Status 2026-09-17 13:52 (rota-02): the partials are banded in COMPLETION.md's core
  section (ruled: Roman, 2026-09-17). Four small frames and two
  campaigns push above this frame when frame 2 closes. B5 struck as
  built, F1 parked.

## Parked

- (observed: `git worktree list`, 2026-09-19) Four worktrees of two ended
  sessions are still registered and still on disk, 583 files each:
  `wt-33` of session 3b4093c6, and `wt-34`, `wt-36` and `wt-86` of session
  75d12c2b. Both sessions are gone. The directories live under the
  sessions' temp directories, so they break the moment temp is cleaned.
  Meta workflow. `git worktree remove` each, or `git worktree prune` after
  the directories go. Not removed by 4286e076, because another session's
  worktree is not its to delete.

- From frame 43's pass 2 (observed: the implementer's measurement):
  `code.write`'s result embeds `written, not committed`, which lists what
  differs between HEAD and the tree (`rota/roles/api.py:8435-8446`). So a
  write's answer depends on what else is uncommitted, and two identical
  writes that span a commit can never compare equal. Under repair 2 that is
  honest, and it means a Developer that repeats one write across commits
  keeps paying full freight. The fix, if it is ever wanted, is to move that
  field out of the write's result and into the commit's. Rota workflow. Not
  frame 43's.
- From the same pass (observed: the implementer's count): 231 recorded
  prompts still carry the old empty-commit note, across five models. Only 8
  were reached by the live L1 and L3 replay under the current pins, and
  those 8 were re-earned. The rest are not replayed by any live suite, so
  they cost nothing today (reasoned: the assistant, from the price agent's
  finding that 14971 of 18270 rows carry superseded instructions). They go
  stale the day a frame widens the replay to those models. Rota workflow.

- (observed: a read-only agent read of this session's own workflow
  artifacts, 2026-09-18) `.claude/settings.local.json` still allows two
  paths under the pre-split checkout `d--repos--AI-Custom-AI-TUI`. The
  file is untracked, so it survived the split by hand. Meta workflow. A
  one-line door.
- (observed: the same read) The Stop hook
  `.claude/hooks/really_blocked.py` is inert. It reads an allowlist file
  that does not exist, so it never fires, and its message still names
  `rota/COMPLETION.md`. Meta workflow. Either delete the hook or give it
  the allowlist. Roman's call.

- From frame 36's fix pass two (observed: the implementer's measurement):
  `PUSH_CHARS` is 20000 and the new `_fit` budget for a 12288 window is
  20258 characters, so a maximal push now meets the cut where it used to
  sit under it. `PUSH_CHARS` was set against the old two-thirds budget
  and may want the same half-window treatment. Two cases went stale and
  re-recorded green, so nothing is red today. Rota workflow. Night 86
  measures it.
- From frame 36's diff review, F5 (reasoned: unreachable today, latent
  tomorrow): a present that renders no numbered line still asks for a
  ruling, and `rulings.rule` then approves every ref with "the page had
  no line to rule on; acknowledged". The state is unreachable from a
  live predicate today. The narrow door, if it is ever wanted, is
  "refuse a present that numbers no line while its refs hold rulable
  rows", not "refuse an empty order". Rota workflow.
- From frame 34's fix pass (reasoned: the implementer's third open
  question): the door that lands a ruling cannot read the principal's
  words, so a Liaison that carries the true words with an invented map
  still lands a ruling. Only a seat check catches it. A register case
  for "the reply is about something else", under the answering mode, is
  the measurement. Rota workflow. A small frame, not yet pushed.
- From night 85 (observed: the run database at 02:55): the Critic's
  challenge tick reached three attempts on `@claim:constraints:
  unprocessed` and `@claim:constraints:format_filename` and quarantined,
  and `tick:constraint_zero` reached three attempts. Rota workflow. Not
  diagnosed, and not on the term-collision path.
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
