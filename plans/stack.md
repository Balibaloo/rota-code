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
   (observed: where and when), (reasoned: why), or (ruled: why). Say which
   workflow it is about, the meta workflow or the rota workflow (ruled
   2026-09-16: a ruling and a judgement looked the same in prose).
   An observation carries its date, because an observation ages. A check
   quoted without its date is a prediction that wears the word observed
   (adopted from the kit on 2026-09-20, frame 50).

## Stack

### 46. One designed budget for a prompt (2026-09-19) (Roman) [0549dc76]

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
  **One finding is parked, not actioned**: `_fit`'s promise is not a
  theorem. A fuzz of 4000 transcripts broke it 1540 times, on a two-block
  transcript and at the `max(2000, ...)` floor. The runner reaches neither
  today, because it appends a reply and a results block every turn. Line 1's
  test states the precondition rather than closing the hole.

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
- Reasoning: `plans/archive/context-caps-design-2026-09-18.md`, section 9.6,
  and the gate baseline at `.rota-gate.json`.
- Status 2026-09-20 03:10 (rota-52): pushed by 0549dc76, unclaimed, unpriced.
  Roman orders it. It sits here because it was found here, and not because it
  outranks frame 45. **The reason it is a frame at all**: "zero stale" is a
  line in every acceptance this repository writes, and a line that reads 72
  cannot gate anything. An acceptance that nobody can fail is not an
  acceptance.

### 51. `holding --frame none` writes a row that lies (2026-09-20)

- Meta workflow. The command sets a session's state back to `standby` when
  the session names no frame. It does not check that a watcher is running.
  A session that finishes a frame and clears its column is then printed as a
  standby with a dead heartbeat, and the table's own rule says STALE means
  dead for a `standby` row (observed: session 0f086f93 at 2026-09-20 15:56,
  immediately after it closed frame 50).
- **The row is safe and it is still false.** A sender never offers it,
  because `free` needs a live beat. The fault is that the table says a live
  session died, which is the same fault class the `held` beat was written to
  fix. The session left the reserve with `release` to make its row honest.
- **This is a finding from running the port on live state, not from reading
  it** (observed: the live table, 2026-09-20 15:56). The kit's own four
  findings came the same way, from frame 43.
- Ends when: a session that clears its frame is not printed as a live
  standby, and a test asserts it. The kit hears the finding either way,
  because the kit owns `cmd_holding`. Not priced. This is a one-line door
  plus one test, so the anchor is 20k.
- Waits on: nothing. It is small and it can wait behind Roman's order.
- Reasoning: the closing status of frame 50 in
  `plans/archive/stack-2026-09-20.md`, and the peers-table rules in
  `plans/operating-facts.md`.
- Status 2026-09-20 15:56 (rota-e7): pushed by 0f086f93, unclaimed. Pushed so
  the obligation stays countable. It sits below Roman's ordered frames,
  because it does not outrank them. **Two candidate fixes, and the choice is
  a design question for the kit**: clear the frame and leave the state alone,
  or set the state from the beat. The second reads the truth and the first
  writes less.

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
- Waits on: frame 46's line 1, and Roman's word. Roman orders it.
- Reasoning: `plans/archive/prompt-budget-design-2026-09-20.md`, section 5,
  and the design review's finding 6.
- Status 2026-09-20 16:45 (rota-52): pushed by 0549dc76, unclaimed, unruled.
  Split out so a capacity question stops gating a coherence frame.

### 52. Take the kit's release into rota (2026-09-20) [unruled]

- Meta workflow. Seven commits in the kit repository since rota's port at
  `58f7960`. A peer says Roman is releasing them (observed:
  `meta-workflow-46`, 2026-09-20). **Not ruled. Roman assigns.** The last
  relay of his word was true and the check still stands, because the tool
  never treats a report of consent as consent.
- **Two change behaviour and are read before the frame is priced properly.**
  - `aec98ba`, the hand-off order. The oldest free standby **under a 300k
    ceiling**, so a loaded session is used up before a fresh one is spent.
    This answers the fault written into `CLAUDE.md` at `d43cb14`, where the
    queue ranked on arm time alone and could hand a frame to a 152k seat
    beside a clean 20k one. A reserve whose standbys are all past the
    ceiling is a drought and says so, which is a different report from an
    empty reserve. A session past the ceiling is refused the arm, because a
    seat no hand-off can use makes the reserve read larger than it is.
  - `80bd49e`, the context count. **The hook reads the harness's own usage
    instead of scaling transcript bytes, and the shipped 0.6 factor read 8
    per cent low.** So every count in rota rises on the day this installs,
    and a session near a threshold crosses it on the install and not on
    growth. Read a jump as a correction, never as growth.
- The rest, as the peer describes them and not as this session has read the
  diffs: `b057b0d` carries the `spent` fix, so frame 51 closes by porting
  rather than by designing, and it states the rule this session wrote at
  `ca8beb8`. `b0cfb92` records the three rows-that-lie as one fault and adds
  that a standby is not a correspondent. `6b66648` rules that a frame carries
  a name and the name travels with the number. `3dd823d` says copying a claim
  never observes it. `707fcac` fixes three defects in the install procedure.
- **Frame 51 folds into this one if it is ruled**, because `b057b0d` carries
  the fix that frame 51 would otherwise design.
- Ends when: rota carries the seven commits, the touched tests pass, the gate
  is green with the stale line read, and `peers` refuses to arm a session
  past the ceiling. About 110k: one implementer pass at the 75k anchor, a
  gate run, and a read of the two behaviour-changing commits before the port.
  The install is a fresh clone to `meta-update`, the "Update an installation"
  section, then delete the clone.
- Waits on: **Roman's word, direct and not relayed.**
- Reasoning: frame 50's port at `58f7960`, and the seat fault recorded in
  `CLAUDE.md` at `d43cb14`.
- Status 2026-09-20 16:20 (rota-52): pushed by 0549dc76, unclaimed, unruled.
  Pushed so the obligation stays countable, and named to Roman rather than
  taken. This session holds frame 46 and takes no new frame.

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

### 33. Finding 42: the code index refreshed after a commit (Roman, 2026-09-17) [9108c499]

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

### 4. Roman's order from here (2026-09-14 12:58) (Roman) [9108c499]

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
