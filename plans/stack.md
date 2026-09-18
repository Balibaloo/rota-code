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

### 43. Review the context length management system (2026-09-18) (Roman)

- Rota workflow. Today one window size, 12288, serves every wake, and a
  prompt that exceeds it collapses to half and loses its brief from the
  front. Seven wakes build their refs from a whole query result with no
  cap (observed: `rota/core/predicates.py`, the `refs=tuple(...)` sites
  for `awaiting_confirm`, `contradiction`, `term_collision`, `grouping`,
  `defer_baseline` twice, `observed_entries`, `quarantined` and
  `constraint_zero`). The observed-entries page already broke a night at
  79 refs.
- **Three of those nine are not model turns at all** (observed:
  `rota/core/predicates.py:57`, `SCHEDULER = "-"`, with the comment "no
  role: the scheduler does this itself"). The two `do:defer_baseline`
  wakes and `tick:constraint_zero` never become a prompt, so no set size
  can overflow a window there. Six remain.
- The assistant's first view of the six, read from the call sites and
  not measured (reasoned: the gate is Roman's, required quality, so each
  row asks whether the seat needs the whole set to answer well):

  | wake | needs whole set | grows with | view |
  | --- | --- | --- | --- |
  | `tick:observed_entries` | yes, it is the whole project view | repository size | unbounded, higher cap |
  | `tick:grouping` | yes, it cannot group what it cannot see | work in flight | unbounded, rarely exercised |
  | `tick:term_collision` | yes, the senses rule against each other | senses of one word, 2 to 3 | unbounded, rarely exercised |
  | `tick:awaiting_confirm` | no, each confirm is independent | backlog | bounded |
  | `tick:quarantined` | no, a count plus specifics suffices | refs of one tick | bounded |
  | `tick:contradiction` | no, resolved one at a time | backlog | bounded |

  Of the three that need the whole set, **only `observed_entries` grows
  with the repository**. The other two are bounded by things the system
  already controls. So the higher cap has one hard customer today, and
  it is the page that broke night 85. The claim most likely to be wrong
  is that grouping stays small, and frame 40 tests it.
- Roman's design, ruled at the grill 2026-09-18:
  1. Each wake carries a flag saying whether its refs are bounded or
     unbounded.
  2. An unbounded wake gets a **second, higher context cap**, whose only
     purpose is to avoid paging. The whole page is kept and the cost is
     paid in turn speed.
  3. **The gating factor is required quality, not low frequency**
     (ruled: Roman, 2026-09-18, correcting the assistant's
     recommendation). A wake gets the higher cap when it needs the whole
     page to answer well. The flag is hand-set (ruled: Roman,
     2026-09-18, after the assistant proposed measuring it with a
     register case per wake; a register case is hard to build and the
     assistant did not price that, where a hand toggle costs nothing and
     changes when evidence argues otherwise).
  4. When a spill is happening, warn about turn speed with specifics.
     The warning stays visible and is not hidden until dismissed.
  5. The cap derives from the model configuration system that tracks
     system RAM. How the two interact is open and needs architecture
     planning.
- The cost that is not turn time (observed: `plans/operating-facts.md`):
  a changed `num_ctx` re-allocates the KV cache, which in practice costs
  a model reload in each direction. The measured spill penalty is not
  gradual: qwen3:8b fits fully at 12.5 s a turn, a 27 per cent spill
  takes over 100 s, 75 per cent on the GPU takes 153 s, and a model over
  by 8 GB takes minutes. The practical budget is about 8 GB of the 10,
  because the desktop takes 2.
- Where the flag lives (observed: `rota/core/scheduler.py:32`, the
  `Wake` frozen dataclass): `Wake` holds five fields, `role`, `kind`,
  `message_id`, `refs` and `detail`, under a one-line class docstring.
  **Only `kind` is documented**, by an inline comment naming its values.
  The other four carry nothing, so no per-field convention exists to
  follow. The flag would be the sixth field and the second with a
  comment. Document every field when the frame runs, because the
  structure is small and the flag's meaning is not obvious from its
  name.
- **The flag is not a boolean** (reasoned: the assistant, at the grill;
  a boolean loses the reason and the reason is what a later reader
  needs). Each unbounded wake is unbounded in a different dimension:
  `observed_entries` in repository size, `grouping` in work in flight,
  `term_collision` in the senses of one word. A short string naming the
  growth dimension carries the same decision and keeps the why. It also
  answers the question the flag raises, which is "bounded by what".
- **Open, for the architecture planning**: the flag must reach the
  runner, which sizes the prompt. A field on `Wake` is the natural home.
  It is not traced whether the runner sees the `Wake` object where it
  chooses the context size, or only the stored `wake_kind` and
  `wake_detail` columns. If the columns are all it sees, the flag
  travels as a third column or is looked up from the tick name. Ask
  `python -m rota.tools.map` before grepping.
- Ends when: not priced. Architecture planning comes first, because
  Roman holds the interaction with the RAM tracking open. Roman is also
  questioning whether the frequent wakes should keep the single cap, so
  the review covers every wake, not only the unbounded ones.
- Waits on: nothing now. Frame 40 closed on 2026-09-18 with
  `plans/archive/principal-pages-2026-09-18.md`. It measured the pages the
  principal was shown, not the ticks, so the claim that grouping stays
  small is still untested. What it does give this frame: the observed
  entries page is 3019 tokens on night 85 and 2993 on night 86, and the
  same page landed a ruling on one night and not the other. The seat
  prompt around it was 17195 tokens on night 85 and 5248 on night 86, so
  the cap belongs on the session's working set and not on the page.
- Reasoning: the grill of 2026-09-18, and
  `plans/archive/night85-2026-09-18.md` for the overflow rule.
- Status 2026-09-18 08:30 (rota-dc): pushed, unclaimed, unpriced. The
  paging question of frame 36 folds into this frame (ruled: Roman, the
  higher cap exists to avoid paging), so paging is no longer a separate
  blocked question.
- Status 2026-09-18 19:27 (rota-ff): claimed by 9108c499. Roman ordered 43
  first, then 38, 37 and 33, with 41 and 42 as needed. The frame stays
  unpriced until the scope is in, because Roman's design point 5 holds the
  interaction with the RAM tracking open. Five read-only agents run now,
  one per question: where the context size is chosen and whether the
  `Wake` reaches it, how the model configuration tracks RAM, what fills a
  seat prompt beside the page, what each wake's ref set does as the work
  grows, and where a spill warning can be shown. The design record and the
  price follow the scope.

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
