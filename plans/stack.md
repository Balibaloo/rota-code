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

### 36. The present page is larger than the window (2026-09-18) [75d12c2b]

- Rota workflow. On night 85 the Liaison presented a page of 77
  numbered lines. The prompt reached 64381 characters against a 12288
  token window. The two sessions that had to answer it made no tool
  call and answered as generic assistants. The present `m27` stayed
  `open`, so the items stayed at approval `draft`, nothing sliced, and
  the night ended with zero batches (observed: night 85's run database
  and turns, recorded in `plans/archive/night85-2026-09-18.md`). This
  wall is upstream of frames 33, 34 and 35 on the delivery path. A cold
  click night cannot reach a batch while the page is larger than the
  window.
- Ends when, each line priced from the anchors, walls apart:
  1. A reviewer settles what bounds the page today, the page's measured
     token count, and whether the 6146 figure is a halved window or a
     misreported count: 60k. Buys: a cause from a measurement, not from
     the character count. Running now.
  2. Roman rules the shape of the fix: 0k, one question with a
     recommended answer. Buys: the page's contract is Roman's, since
     `plans/composition.md` forbids the tool ruling for the Principal
     and forbids silence as consent.
  3. The fix is built with a pinned test that a page of 77 lines is
     answerable at the shipped window: 110k (cold 80k, one resumed pass
     30k). Buys: a cold night gets past the present.
  4. A diff review on a worktree at the commit, its fixes in: 90k.
     Buys: a write-pipeline change is read by a context that never
     wrote it.
  5. The gate green, the stale line read: 12k.
  6. Night 86 cold from a worktree at the closing commit reaches a
     batch: 20k here, about 40 minutes wall at night 85's rate.
  Total: 292k in agents, about 80k in this context.
- Waits on: the frame 34 implementer, which holds the same four files in
  the main checkout. Roman's ruling on paging is a separate line and
  does not block the fitting fix.
- Reasoning: `plans/archive/night85-2026-09-18.md`.
- Status 2026-09-18 03:05 (rota-dc): pushed. The reviewer runs, cap 60k.
  The frame is Roman's to reorder. It is above frames 33, 34 and 35
  because none of their fixes can be walked until a night gets past the
  present (reasoned: night 85 never reached the term-collision tick).
- Status 2026-09-18 03:13 (rota-dc): line 1 is in, 88k on the harness
  line against 60k priced and a 60k cap, 70 tool calls. The cause is
  measured, not guessed (observed: the reviewer's tokeniser and replay
  probes, recorded in `plans/archive/night85-2026-09-18.md`). Five high
  findings. The first: `_fit` at `rota/core/runner.py:469` returns early
  while a transcript holds fewer than four blocks, so an oversized wake
  is never cut, and turns one to three hold one to three blocks. The
  third: the landing wake carries the same 79 rows twice, byte-identical
  at 21402 characters each, and dropping one cuts the prompt from 17220
  to 11337 tokens. The fifth: `ref_resolves` accepts any string starting
  with `@`, so a tick name became a ledger row and then a decision with
  a dangling ref.
  The 6146 question is settled and finding 79's cause was wrong. Ollama
  collapses any prompt over `num_ctx` to `num_ctx/2 + 2` and keeps the
  tail, at one slot, on both servers, at three window sizes. The brief
  sits at the front, so the brief is what dies. `plans/operating-facts.md`
  is corrected. Plan against `num_ctx/2`.
  The signoff reading of the night 85 record is withdrawn (observed:
  `principal.land` refuses an empty reply with "Silence is not
  consent"). Forty-five of the 46 decisions are the intended discharge
  of an assumption under Law 11. The 46th is the dangling ref of finding
  5. The diff review's finding 3 of frame 34 stays a probe result, not a
  field observation.
  New ends-when lines, priced: 3a, the fitting fix, findings 1, 3, 5, 7
  and 8 plus the wake built from the page and the line map, measured at
  5438 tokens against the 12288 window: 110k. 3b, paging the present:
  held for Roman, below.
- **Blocked on Roman.** Question: does the present page get paged, N
  lines at a time? Paging is the only shape the reviewer measured that
  stays bounded as a repository grows, and it breaks the tipsK ruling
  and `observed_entries.md:14-16`, "One page, not several". The `asked`
  guard at `rota/core/predicates.py:648-651` would have to count one
  page-set as one ask. Recommended answer: not now. Build the fitting
  fix first, which needs no ruling and gets click to 5438 tokens, then
  push paging as its own frame before step 5 of the order, breadth,
  where a larger repository forces it (reasoned: the page is 3039 tokens
  for 77 lines on click and scales linearly, so breadth meets this wall
  again). A per-page default verdict is not available at any time
  (ruled: `plans/composition.md`, the tool never rules for the
  Principal).
- Status 2026-09-18 03:47 (rota-dc): line 3a is out to a fresh
  implementer at a268266, priced 90k, cap 110k. The brief carries seven
  items, the measured target of 6100 tokens for a 77-reference landing
  wake, and the schema mark carried from frame 34's pass. The
  implementer must measure with the real tokeniser, not by a character
  count, and must find every site by its content, because a268266 moved
  the lines the review named.
- Status 2026-09-18 05:05 (rota-dc): the fix pass is in, about 105k of
  new content on the implementer's own estimate against 90k priced and
  a 110k cap, 243 tool calls (observed: the implementer's report; the
  harness counter it quotes measures replayed context, not spend).
  Fifteen files, 428 insertions. Committed at 8ebbae1.
  **The page fits.** Night 85's own 79-line present, rebuilt under the
  new code, measures 17220 tokens before and **5593 after**, against a
  6146 budget (observed: the implementer's tokeniser probe against
  qwen3:8b with a nonce). A 77-line synthetic present measures 16138
  before and 4592 after.
  The shape: `_fit` cuts on every turn, since the early return moved
  below the wake cut; a landing wake above `LANDING_ROWS_CHARS = 6000`
  carries a line map of number to `id (table)` and a note, and drops
  the duplicate rows; a new op `rulings.line` resolves the row behind
  one numbered line; `ref_resolves` sends every `@` ref through an area
  check; `SCHEMA_MARK` moves to `ledger-kind`.
  Six deviations, all accepted, and two are measurements that overturn
  the brief (reasoned: the implementer measured rather than argued).
  Dropping the duplicate rows on every page, as the brief said, cost
  two register cases 5/5 to 0/5 on five runs each, because the seat
  rules from the repeated row. The cut is by size instead. Naming the
  new op inside the ask paragraph cost another case 5/5 to 0/5, so the
  sentence sits in the opening paragraph.
  Gate by the implementer: one new red, the parked flaky screens case,
  green on the gate's own re-run, 1908 passed. Register: stale 7 to 0,
  green 102 to 106. Gate by the assistant is running. The diff review
  is out on a worktree at 8ebbae1, cap 65k, nine points.
  `plans/operating-facts.md` is corrected for the moved mark and for
  the warm snapshot, which is now behind it (observed: the
  implementer's first open question).
- **The paging question sharpens.** Night 85's real page lands at 5593
  tokens against 6146, so a small library leaves 550 tokens of headroom
  and the page text alone is 3039 (observed: the implementer's
  measurement). The recommendation is unchanged and the trigger is now
  measured: paging is a frame before step 5 of the order, breadth,
  where tips, icalendar and a non-Python repository each exceed this
  headroom.

### 35. The observed-entries page is quarantined on cold click (2026-09-17) [75d12c2b]

- Rota workflow. On night 84 `tick:observed_entries` ran three sessions,
  s96 to s98, each with no parsable tool call, and was quarantined. The
  glossary and the model rows were never presented, so nights 83 and
  84 have no glossary ruling, where night 82 at d4bf679 landed one
  through that tick (observed: the agent's read of the three run
  databases, recorded in `plans/archive/term-collision-2026-09-17.md`).
  A wall on the delivery path behind frame 34's. Frame 33's walk waits
  on it too.
- Ends when: the turns of s96 to s98 are read and the cause is on the
  stack (20k, the same agent resumed); then a fix priced from the cause.
- Waits on: nothing.
- Reasoning: `plans/archive/term-collision-2026-09-17.md`, the second
  wall.
- Status 2026-09-17 20:48 (rota-02): pushed. The reviewer that read
  frame 34's turns is resumed on s96 to s98, cap 20k.
- Status 2026-09-17 20:51 (rota-02): validating. The cause is a
  one-character door (observed: the agent's probe, 8k for the pass on
  the harness line: the three sessions sent the same call with 56 bare
  refs, the bare-list rewrite's id class lacks `#`, so
  `argument#src_click` never matched and the lenient parser refused
  the present; the same text without the hash rewrites to a list; the
  prompt was 2.5k tokens against a 12288 window; the parser files did
  not change since d4bf679). Not the model, not the brief. The door is
  in at 65ca902, one pinned test, landed by the assistant (ruled: the
  brief, a one-line door is the exception). The common root with frame
  34: the second-sense rows are new in night 84's data, and two code
  paths had never seen them. Walked by night 85 with frames 33 and 34.
- Status 2026-09-18 02:13 (rota-dc): claimed by 75d12c2b. The peer that
  held the frame was killed before it handed over (observed: Roman's
  word and the session list, where the peer name is gone). The frame is
  unchanged. It still closes on night 85.
- Status 2026-09-18 02:55 (rota-dc): the door works on a live night
  (observed: night 85's run database at 02:55, `tick:observed_entries`
  ran one session, s109, which committed and presented
  `glossary_terms:20, constraints:57, model`; the glossary holds 21
  rows). Night 84 ran three sessions on the same tick with no parsable
  tool call and quarantined it, and nights 83 and 84 landed no glossary
  ruling. Night 85 also cleared onboarding in 35 minutes, from 02:16 to
  02:51, where night 84 stuck in onboarding. The frame stays validating
  until the night ends.
- Note, not this frame (observed: the same database): a different tick
  quarantined, `challenge for @claim:constraints`, two sessions, and
  `tick_attempts` shows the Critic's challenge tick at three attempts on
  two constraint claims, with `constraint_zero` at three. Rota workflow.
  It is parked below, not diagnosed.
- Status 2026-09-18 03:05 (rota-dc): closed by the night, on the
  evidence of the whole run (observed: night 85 ran the tick once, the
  session committed, the glossary holds 21 rows, and onboarding
  completed in 35 minutes where night 84 stuck). The night's own wall
  was frame 36, not this one. This frame's five lines move to
  `plans/archive/stack-2026-09-18.md` at the next pop.

### 34. The term-collision loop on click, cold (2026-09-17) [75d12c2b]

- Rota workflow. On a cold click night the Terminologist wakes on
  `tick:term_collision` for `group` and `Group`, the Liaison asks the
  principal, the yes-only principal answers with the constraint text,
  the Liaison relays, the Terminologist logs that the relayed message
  carries no principal verdict in its resolved refs and cannot adopt
  the senses, and the tick re-fires. Every session commits, so no
  attempt cap fires (observed: nights 83 and 84, 144 and 200 wakes, no
  batch; the run databases are copied to the session scratchpad as
  `clickI_night83.db` and `clickI_night84.db`, beside night 82's, which
  reached batches at d4bf679). A wall on the delivery path. Frame 33's
  walk waits on it.
- Ends when, each line priced from the anchors, walls apart:
  1. The turns of one cycle are read by an agent and the cause is on
     the stack with its evidence: 60k. Buys: a cause from the turns,
     not from a guess.
  2. The fix is built by a fresh implementer with a pinned test that
     the Terminologist's wake after the principal's answer carries what
     the brief tells it to read, and the tick does not re-fire: 90k
     (cold 80k, one resumed pass 10k). Buys: a cold night reaches a
     batch.
  3. The gate green, the stale line read: 6k.
  4. Night 85 from a worktree at the closing commit reaches a batch
     and a commit: 20k here, about two hours wall. This night is frame
     33's walk too (reasoned: the worktree carries both frames' code;
     a stated deviation from one walk per frame).
  Total: 176k in agents, about 60k in this context.
- Waits on: nothing.
- Reasoning: the three night databases above. The cause and the fix
  brief go in `plans/archive/term-collision-2026-09-17.md`.
- Status 2026-09-17 20:40 (rota-02): pushed. Night 84 killed at 20:39.
  A reviewer-type agent reads one cycle's turns on night 84, the same
  path on night 82, and the commits between d4bf679 and 3ab5c73 on the
  relay, the predicate and the resolved refs, cap 60k.
- Status 2026-09-17 20:48 (rota-02): the turns are read, 109k on the
  harness line against 60k priced and a 60k cap, 29 tool calls. The
  cause is three linked defects on the answer path, none a regression
  of the day's commits (observed: the turns of s270 to s272 and the
  code at d4bf679; recorded with marks in
  `plans/archive/term-collision-2026-09-17.md`): a words-only reply to
  a clarify lands a ruling with no per-item verdict and the Liaison in
  `answering` mode has no tool to write its reading; the relay's
  verdict lookup climbs one cause hop, to the report; and the
  predicate cannot see an adopted family or park a logged one. Night
  82 never entered the path: its survey found one `group`. The fix
  brief is in the record. A fresh implementer, cap 100k, with three
  pinned tests and the touched register cases re-recorded. Frame 35 is
  the second wall behind this one.
- Status 2026-09-17 21:42 (rota-02): implementer pass 1 in, 169k on the
  harness line against 90k priced and a 100k cap, 124 tool calls, 43
  minutes (observed: the harness usage). Seven files, 182 insertions,
  three pinned tests. Six deviations, all accepted (reasoned: each
  stated with its cause): `ledger.log` joins the answering tools since
  the brief's own text needs it; a ruled id is one a landed ruling
  names, since a bare `ruling` ref is what reads as decided and two
  pinned cases seed that; `rulings.rule` accepts a clarify as the page;
  the chain walk lives in `principal.py`. The one prompt-changing
  register case, `L1-LI-a-reply-reaches-the-desk-that-asked`, was
  re-earned 5/5 before the GPU pause, after a first brief draft scored
  0/5 and was rewritten; four cases replayed byte-identical. Gate by
  the implementer: zero new reds, zero stale, 1896 passed. Gate by the
  assistant: one new red, the parked flaky arc case, green on the
  re-run (observed: the gate's flaky line). Committed at 6895000. Open
  for the diff review, from the implementer's report: the observed
  cycle's later turns run through `report` mode, whose prior-answers
  branch relays without ruling; a ruling on a clarify lands no verdict
  message; a ruling that names one of two senses discharges the family;
  the parking sentence is matched as a substring. Diff review next, on
  the worktree at 6895000. The walk, night 85, waits on the GPU (ruled:
  Roman, 2026-09-17, all GPU work paused).
- Status 2026-09-18 02:13 (rota-dc): claimed by 75d12c2b after the
  holding peer was killed before it handed over. No work is lost
  (observed: the tree is clean at 8d581e9 and the worktree at 6895000
  survives the dead session). The GPU pause is lifted (ruled: Roman,
  2026-09-18, the cards are free). The diff review is out to a
  reviewer on the worktree at 6895000, read-only, cap 65k, on eight
  numbered points: the four parts of the fix brief, the six accepted
  deviations, the four items the implementer left open, the write
  pipeline, and whether the loop breaks on a cold cycle.
- Status 2026-09-18 02:19 (rota-dc): the cards are in work mode, 320 W
  on the 3080 and 200 W on the Titan, set through the
  `rota-gpu-power-work` scheduled task (observed: nvidia-smi after the
  task; a raw `-pl` raise needs admin and would put the pair above the
  RM850's budget). Both ollama servers answer and
  `OLLAMA_NUM_PARALLEL=1` holds. Night 85 runs now from a second
  worktree at 6895000, cold, from sentence two, beside the diff review
  on the same commit. A stated deviation from the brief's closing-commit
  line (reasoned: the review spends tokens and the night spends GPU
  hours, so the two run at once; the night runs again at the closing
  commit if the review's fixes touch the delivery path). The run
  databases of nights 82, 83 and 84 are copied to `.rota/` (observed:
  the only copies were in the dead peer's temporary directory, and the
  night script overwrites `clickI_prev.db`).
- Status 2026-09-18 02:37 (rota-dc): the diff review is in, 112k on the
  harness line against 65k priced and a 65k cap, 49 tool calls. Eight
  points answered, five high findings and four lows. The loop still
  closes on one common answer (observed: the reviewer built the night-84
  fixture, ruled both rows `contest`, and the tick fired on cycles two
  and three). The fix of 6895000 breaks the loop only when the ruling
  approves at least one row. Part B and the write pipeline hold. One
  deviation fails at its boundary: a clarify has no numbered page, so
  the new door tells the Liaison to approve a row the words never named,
  and the reviewer landed an approve on both rows for an unrelated
  reply. Three more highs: a signoff on the parking row discharges the
  collision for good, a paraphrase of the parking sentence never parks
  and grows the ledger without bound, and no door holds the ruling
  before the relay. The findings are in
  `plans/archive/term-collision-2026-09-17.md`. A fresh implementer has
  findings 1, 2, 3, 4, 5, 8 and 9 with seven pinned tests, priced 90k,
  cap 110k (reasoned: a stated deviation from one implementer per frame,
  since the agent that wrote 6895000 died with its session). Findings 6
  and 7 stay out, low and off the delivery path. A new ends-when line:
  the review's fixes are in and the gate is green, 90k. Night 85 keeps
  running at 6895000 (reasoned: the yes-only principal's words test the
  approve path, which 6895000 does break, so the night measures the
  common path while the fix pass makes the other paths safe).
- Status 2026-09-18 03:05 (rota-dc): night 85 is in, and it does not
  measure this frame. The night ended at GAUNTLET-DONE in 39 minutes,
  125 sessions, zero batches, and **the term-collision tick never
  fired** (observed: the run database; recorded in
  `plans/archive/night85-2026-09-18.md`). The night stopped on a new
  wall, frame 36: a present page of 77 lines against a 12288 token
  window. The loop of nights 83 and 84 did not happen, but the night
  never reached the path this frame fixes, so the fix is unwalked. The
  diff review's finding 3 is confirmed in the wild: 46 decisions on
  night 85 begin `default taken at signoff:`, one of them discharging a
  tick that gave up at its attempt bound. The fix pass runs on, because
  the seven findings stand whatever stops the night. This frame's walk
  moves behind frame 36.
- Status 2026-09-18 03:35 (rota-dc): the fix pass is in, 144k on the
  harness line against 90k priced and a 110k cap, 141 tool calls, about
  60 minutes (observed: the harness usage). Twelve files, 474
  insertions, seven pinned tests and three older ones updated. All seven
  findings fixed, each proved on a copy of the reviewer's own probes
  (observed: the implementer's report; the reviewer's `p_ab.py` now
  stops at "'1' is not a row of this question", which is finding 2's fix
  showing itself). The shape: a `kind` column on `ledger` with a two
  value check, a new op `ledger.unaddressed` that composes the parking
  sentence machine-side, a partial map accepted on a clarify with each
  unnamed ref parked, `term_collision` reading `per_item` for a named id
  and going quiet only when every id of the family is ruled, and a relay
  refused in `sandbox.py` while no ruling or ledger row is staged.
  Eight deviations, all accepted (reasoned: each stated with its cause).
  The notable ones: report mode holds `ledger.unaddressed` alone, since
  `rulings.rule` there can only refuse and a tool that only refuses is a
  trap; the parking class is `default`, not `assumption`, since
  `test_vocabulary.py` refuses a word with two jobs; the relay guard
  sits at the call in `sandbox.py`, not after it in `runner.py`. Gate by
  the implementer: zero new reds, zero stale, 1903 passed, 506 s. An
  earlier run showed four new reds, all the implementer's own, all
  fixed. Committed at a268266. Gate by the assistant is running.
  Rulings on the implementer's three open questions (ruled: the
  assistant, in the smart zone): the schema mark moves, so an old run
  database refuses a run instead of failing on its first ledger write,
  which follows the precedent of the `provenance` refusal in
  `plans/operating-facts.md`; the parking op stays on the Liaison's
  chain, and another seat parking a word is a new frame, not this one;
  a register case for a reply that is about something else is worth
  recording, as its own small frame, since the door cannot read the
  words and only the seat can. The schema mark goes into frame 36's
  pass, which touches the same files.
- Status 2026-09-18 03:47 (rota-dc): gate by the assistant at a268266,
  on the same tree and independent of the implementer's run: zero new
  reds, zero stale, 1903 passed, 504 s (observed: the gate's own
  summary). The implementer's numbers hold. Ends-when lines 2 and 3 are
  done, priced 90k and 6k against 144k and 12k actual. The frame stays
  open for its walk, which is now night 86 behind frame 36.

### 33. Finding 42: the code index refreshed after a commit (Roman, 2026-09-17) [75d12c2b]

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

### 4. Roman's order from here (2026-09-14 12:58) (Roman) [75d12c2b]

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
