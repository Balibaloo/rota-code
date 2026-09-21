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
42, 33, 4 and predates frames 51, 53, 54 and 55.

**The file is reordered to that list on 2026-09-21 10:30, when frame 46, one
designed budget for a prompt, closed.** Six frames are below it and the ruling
does not name them, because all six were pushed after 00:29: 56, 603 recorded
prompts exceed the budget `_fit` promises. 57, why anything spills into system
RAM. 58, a retried tick re-runs the identical session. 59, the ledger row is
shorter than the reasoning it rules from. 60, the re-record command the suite
prints uses the wrong model. 61, an unmet obligation is visible only while
something points back at it. They sit after the ordered list in number order,
which is not a claim that they rank below it (reasoned: the assistant, placing
what Roman has not yet ordered rather than guessing an order for it). **Frame
57 is Roman's own ask and it is the one most likely misplaced here.**

**Roman ruled twice on 2026-09-21 13:40.** Frame 60, the re-record command the
suite prints uses the wrong model, moves below frame 54, the register's match
is narrower than the cassette key (ruled: Roman, asked with the reason that an
instrument fault ranks where the instrument ranks). And **the next session
starts with frame 62, batch the open frames, before it takes any of them**
(ruled: Roman, "make the next session start with a batching frame that
organises the current frames"). So the placement note above is superseded for
every frame frame 62 batches.

## The batches

Frame 62, batch the open frames, produced this table on 2026-09-21. Four
batches hold 13 of the 21 open frames. Eight frames belong to no batch, and
each one says why in its own first line. **A batch is one read, one repair or
one walk, and never a subject.** Every frame carries its batch in its first
line, so a session that opens one frame reads the batch before the work.

| Batch | Frames, in order | The one thing they share |
| --- | --- | --- |
| A, the cassette key | 54, 60, 55, 49 | One repair: the key that names a recording. The writer and the reader must name the same fields. |
| B, what a seat lost on night 88 | the read, then 59, 61, then 47, 53 | One read: `.rota/clickI_night88.db`, the `turns` table's `system`, `user` and `completion` columns. |
| C, the night's stall | 58, 38, 37 | One read: what the Developer was given and what it answered, across the three nights on disk. |
| D, the principal seam | 41, 42 | One repair site: `probes/walk.py:84-87`, `class Principal` and its `respond(ask)`. |
| none | 48, 56, 57, 45, 33, 4, 2, 1 | Nothing. Each frame's first line says what it shares and what it does not. |

**Batch A is one fault in two places, and the second is a cause of a third**
(observed: `rota/tools/casestatus.py:75-82`, 2026-09-21). The report matches a
recording on the case id, the prompt hash and the model. Frame 60 says a
re-record outside the gate takes `llama3.1:8b` while the gate takes
`qwen3:8b`. So such a row is written under a model the report never asks for,
and the case reads STALE. **That makes frame 60 a producer of frame 49's 72**,
and not only an instrument fault. The file's own comment at `:60-61` states the
intent the fault breaks: a qwen-held green must not render as a llama STALE.

**Batch B is one query, not four** (observed: the night 88 schema and its 738
turns, 2026-09-21). The cut writes its own size into the turn text, in the
form `CUT the result: 2,257 of 16,257 characters are not shown`, and it names
the call that returns the rest. 95 turns carry a cut in `user`, 39 in `system`
and 20 in `completion`. So one pass over three columns answers all four
frames: what was removed, from which block, and whether it was a verdict, a
ruling, a tool call or an open obligation. The batch's order puts frames 59
and 61 before 47 and 53, because those two have repairs priced already and
these two need the read before they can be priced at all.

**Batch C's order is set by what a retry means.** Frame 58 runs first because
it changes what frames 38 and 37 see. A stall of ten attempts is not ten
attempts if the retries are one session repeated, and frame 58 measured 12 of
night 88's 191 sessions as four sessions run three times.

**Two gains that are not batches, and are lost if the order ignores them.**
First, **one walk can serve four frames**: 45, 58, 59 and 61 all repair the
write path and all four price a full night. One night proves all four if the
repairs land together, which saves about 60k in this context. Second, **frame
57 should be scheduled next to batch B**, because it reads the same night for
a different question and the night is then opened once.

**Three ordering facts that the batches expose** (reasoned: the batching pass,
2026-09-21):

1. **Batch C is the only batch that unblocks frame 33.** That frame's code is
   built, reviewed twice and gated at 457k, and it has never walked, because a
   walk needs a merge and a merge waits on frame 37. No other frame on this
   stack releases it.
2. **Frame 56 gates frame 53's ruling.** No fraction of the window can be
   ruled while 603 recorded prompts say `_fit`'s promise does not hold. Frame
   56 also needs one finding from frame 54: `_fit_budget` is a function of
   `num_ctx`, and every cassette was recorded at 12288 or 8192, so the 603
   must be counted against each cassette's own window.
3. **Batch A and frame 48 restore the acceptance's two lines.** Batch A
   restores "zero stale" and frame 48 restores "zero new reds". Neither line
   can gate today, and every frame that closes after them is accepted on a
   line that can fail. That is a shared purpose and not a shared read, so the
   frames stay apart and are ordered together.

### 62. Batch the open frames (2026-09-21) (Roman) [75f21e35]

- Meta workflow. **Roman's ask, 2026-09-21 13:40**: the next session starts
  with a frame that organises the current frames into batches. This frame is
  that. It is the first thing the session holding the stack does, and it takes
  no other frame until this one closes.
- **The stack is 21 frames and it is worked one at a time.** Today two of them
  turned out to be one fault in two places, and the second was found only
  because the first was being worked (observed: this session, 2026-09-21).
  Frame 54, the register's match is narrower than the cassette key, says the
  report matches on too little. Frame 60, the re-record command the suite
  prints uses the wrong model, says the recorder writes under a key the report
  cannot see. Neither is complete without the other.
- **Candidates a batching pass should test, not adopt** (reasoned: this
  session, from what it read while holding frame 46, one designed budget for a
  prompt). Each is a guess with a reason, and the pass must confirm or break it
  by reading the frames:
  - **The register's truth**: 54, the register's match is narrower than the
    cassette key. 60, the re-record command the suite prints uses the wrong
    model. 55, a recorded green does not reproduce live. 49, the register is 72
    cases stale and no frame owns it. All four answer one question: what does a
    green in the register mean? 49 already waits on 54.
  - **The night's stall**: 37, the Developer exhausts ten attempts on the
    tests. 38, the regression between night 70 and night 86. 58, a retried tick
    re-runs the identical session. Night 89 showed all three alive on
    2026-09-21, with 3 developer sessions of 191 and a NULL `head_commit` on
    every batch.
  - **What a seat is told**: 59, the ledger row is shorter than the reasoning
    it rules from. 61, an unmet obligation is visible only while something
    points back at it. 47, the reply cut fires thirty times more often. All
    three are about a seat losing something it needed.
  - **The window's size**: 53, does a prompt get more than half the window. 56,
    603 recorded prompts exceed the budget `_fit` promises. Roman already ruled
    that 47 and 53 share one read, so a batch may cross these groups.
  - **Unbatched so far**: 45, an abandoned tick reached the page as a finding.
    48, `tests/rota/test_screens.py` is flaky. 41, a sub-agent drives the walk
    as the principal. 42, the designed principal, and whether zero temperature
    is consistent. 33, finding 42, the code index refreshed after a commit. 57,
    why anything spills into system RAM. 4, Roman's order from here. 2, the
    gauntlet on the lineage. 1, the end state.
- **A batch is not a folder.** A batch earns its name only if its frames share
  one first read, or one repair, or one walk. Two frames that merely sound
  alike are two frames. The pass must say, for each batch, what the single
  shared thing is, and must leave a frame alone when it shares nothing.
- Ends when: every open frame names the batch it belongs to or says it belongs
  to none, each batch names the one thing its frames share and the order inside
  it, and Roman has ruled the order of the batches. Priced from the anchors:
  one read over the open frames that proposes the batches, 60k. Buys an order
  that is worked in shared reads instead of one frame at a time. The ruling and
  the rewrite of this file, 20k in the holding session.
- Waits on: nothing. It is the top frame and Roman put it there.
- Reasoning: this file, and frame 46's closing status in
  `plans/archive/stack-2026-09-21.md`, which is where the 54-and-60 pair was
  found.
- Status 2026-09-21 13:40 (rota-e7): **pushed by 0f086f93 on Roman's ask, and
  handed rather than held.** This session is past the mark where its brief
  stops it taking a frame, so it pushes this frame, stops, and gives the stack
  to the free standby. **Do not take a second frame before this one closes.**
  Roman's words were that the next session starts with it.
  **One warning from today, so the pass does not repeat it.** Read each frame
  before you place it. Two frames that both mention the register are not
  automatically one batch, and the pair that was real, 54 and 60, looked
  unrelated until the recorder's key was read against the report's match.
- Status 2026-09-21 13:43 (rota-e7): **handed to session 75f21e35, peer name
  rota-36, and the take never came.** Meta workflow. The `hand` command posted
  the claim at 13:41:03 at stack commit `10e382c` and exited 4 after 90
  seconds. That session holds the claim and has not taken it.
  **The claim returns to the queue by itself at about 13:56**, so the frame
  moves again with nobody driving it. A later standby takes it then.
  **A message went to rota-36 on the second route**, telling it to run
  `take --sid 75f21e35`. That is the only route the brief allows after a 4,
  and it is used once.
  **Do not read this as messaging being broken.** The claim was posted and it
  is on disk. The watcher for 75f21e35 did not wake inside 90 seconds, and the
  reason is not known from here.
- Status 2026-09-21 13:52 (rota-36): **taken and worked. The batches are in
  the section above, and the frame waits on Roman for one ruling.** Meta
  workflow. Session 75f21e35 took the claim at 13:46 on the message route, so
  the hand-off cost one message and no session. **The watcher's own record says
  why the take was late**: the first arm exited 3, its wait ran out before the
  claim was posted, and the re-arm then took the waiting claim at once. So the
  watcher did not fail. It was between waits.
- Status 2026-09-21 13:52 (rota-36): **the pass read all 21 frames and then
  read code for the three claims it adds beyond them.** The warning on this
  frame was that the real pair looked unrelated until the code was read, so
  each new link was checked and not reasoned:
  `rota/tools/casestatus.py:75-82` for the model in the match,
  `.rota/clickI_night88.db`'s schema and cut text for batch B's one query, and
  `probes/walk.py:84-87` for batch D's seam. All three hold.
  **Four batches of 13 frames, and eight frames left alone.** Three candidate
  groupings from the frame's own list were broken by the reading. The
  register's truth stays whole as batch A, and it gained a mechanism: frame 60
  produces frame 49's stale count. The window's size breaks: frames 53 and 56
  read different databases, so frame 56 gates frame 53's ruling and joins no
  batch. What a seat is told breaks the other way and grows: frames 47, 53, 59
  and 61 are one query over one night, which the frame's candidate did not see
  because it had frames 53 and 56 together.
  **What is left for Roman**: the order of the batches. This frame cannot close
  until that is ruled, and the recommendation is below.
- **The recommended order, 2026-09-21 (reasoned: the batching pass).** Eight
  steps. Two rules set it: an instrument is repaired before the work it
  accepts, and a shared walk is not split.
  1. **Batch A**, frames 54, 60, 55, 49, with **frame 48** beside it. The two
     lines of every acceptance come back. Nothing below this step can be
     accepted honestly until it lands.
  2. **Batch C**, frames 58, 38, 37. This step releases frame 33 and step 4 of
     Roman's order in frame 4. It is second and not first because frame 58
     ships code, and code closed before step 1 is accepted on a line that
     cannot fail.
  3. **Frame 56**. It sits here because it needs frame 54's window finding
     from step 1, and it gates the ruling in step 4.
  4. **Batch B**, the one read, then frames 59 and 61, then 47 and 53, with
     **frame 57** beside it on the same night.
  5. **Frame 45**. It lands here so its walk joins the next step.
  6. **One night**, proving frames 58, 59, 61 and 45 together. About 20k in
     this context against about 80k for four nights.
  7. **Batch D**, frames 41 and 42.
  8. **Frame 33's walk**, then the remaining steps of frame 4.
  **The one place this order is weak**: frame 33 holds 457k of built, reviewed
  and gated code that has never run on a night, and this order reaches it at
  step 2 for the unblock and step 8 for the walk. An order that put batch C
  first would release it sooner and would accept frame 58's code on a line
  that cannot fail.

### 54. The register's match is narrower than the cassette key (2026-09-20) (Roman)

- **Batch A, the cassette key. First of four.** The batch's one shared thing is the key that names a recording. This frame is the reader's half: `casestatus` matches on three fields and the cassette key covers more. Frame 60, the re-record command the suite prints uses the wrong model, is the writer's half and runs next.

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

### 60. The re-record command the suite prints uses the wrong model (2026-09-21)

- **Batch A, the cassette key. Second of four.** This frame is the writer's half of the same fault. `casestatus` matches `model` as well as the case id and the prompt hash (observed: `rota/tools/casestatus.py:75-82`, 2026-09-21), so a case re-recorded outside the gate writes a row under `llama3.1:8b` that the report, asking for `qwen3:8b`, cannot see. **That makes this frame a producer of frame 49's stale count**, and not only an instrument fault.

- Meta workflow. `tests/rota/test_l1.py:34` reads
  `MODEL = os.environ.get("ROTA_MODEL", "llama3.1:8b")`. The gate sets
  `ROTA_MODEL` to `qwen3:8b` at `rota/tools/gate.py:76`. A direct `pytest` run
  sets nothing (observed: both files, 2026-09-21).
- **The suite's own STALE message tells you to re-earn a case with
  `ROTA_L1=1 python -m pytest tests/rota/test_l1.py -q`**, at
  `tests/rota/test_l1.py:167` and `tests/rota/test_l3.py:106`. That command
  names no model. **So following the repository's own instruction re-records
  the register against a model the register does not hold**, for every case
  whose file pins none.
- **The cost is measured, not predicted** (observed: the same 20 case ids run
  twice, 2026-09-21 05:16 and 05:33). Without `ROTA_MODEL`: 16 pass, 4 fail.
  With `ROTA_MODEL=qwen3:8b`: 18 pass, 2 fail.
  `L2-DV-name-the-block-rather-than-retry` and
  `L1-VK-the-account-before-the-behaviours` flip from fail to pass on the
  model alone. Both scored 0 of 5 on the wrong model.
- **This session followed the instruction and read two false regressions from
  it** (observed: this session, 2026-09-21). A diagnosis at 132970 tokens was
  spent, and it found the cause. The frame exists so the next session does not
  spend it again.
- Ends when: the message names a model, the two test files agree on which
  model a direct run uses, and a test asserts that a run outside the gate does
  not silently take a different model from the register's. Priced from the
  anchors: one door and one test, 30k.
- Waits on: nothing. Roman orders it.
- Reasoning: frame 46's status line of 2026-09-21 05:21, and the diagnosis of
  the two case regressions.
- Status 2026-09-21 05:34 (rota-e7): pushed by 0f086f93, unclaimed, priced.
  **This is not a model question and it is not frame 55's.** Frame 55 says a
  recorded green does not reproduce live on one model. This says two commands
  that both claim to re-earn a case use two different models. This session
  holds frame 46 and takes no new frame.

### 47. The reply cut fires thirty times more often (2026-09-20)

- **Batch B, what a seat lost on night 88. First of four.** The batch's one shared thing is one read of `.rota/clickI_night88.db`, over the `turns` table's `system`, `user` and `completion` columns (observed: the table's schema and 738 rows, 2026-09-21). The cut states its own size in the text, so one query counts every cut site and what it removed: 95 turns carry a cut in `user`, 39 in `system` and 20 in `completion`. This frame owns the `completion` side.

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

### 53. Does a prompt get more than half the window? (2026-09-20) [unruled]

- **Batch B, what a seat lost on night 88. Second of four.** This frame owns the `system` and `user` side of the same read, which is the denied demand. Roman already ruled that this frame and frame 47 share one read, and the batch widens that read to frames 59 and 61 rather than adding one. **The ruling on the fraction still waits on frame 56**, because no fraction can be ruled while 603 recorded prompts say the promise does not hold.

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

### 48. `tests/rota/test_screens.py` is flaky (2026-09-20)

- **No batch.** It shares no read, no repair and no walk with any open frame. **It is ordered beside batch A for a different reason**: batch A restores the acceptance line "zero stale" and this frame restores "zero new reds". The two lines are in every acceptance this repository writes, and neither can gate today. That is a shared purpose and not a shared read, so the frames stay apart.

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

### 55. A recorded green does not reproduce live (2026-09-20)

- **Batch A, the cassette key. Third of four.** This frame's two unknowns are the batch's two halves. "The model behind the tag changed" is frame 60's question. "A fresh run builds a prompt the cassette key does not capture" is frame 54's. So frames 54 and 60 answer this frame's diagnosis first, and the 40k probe runs only if they do not.

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

- **Batch A, the cassette key. Fourth of four, and the batch's output.** The true stale count is what the batch exists to produce. Both frames above move the count: frame 54 by widening the match, frame 60 by stopping a write under an unpinned model. This frame re-records what is left. It already waits on frame 54, and it now waits on frame 60 for the same reason.

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

### 45. An abandoned tick reached the page as a finding (2026-09-18)

- **No batch.** Its first read is a scope report over `tick:blindspot`'s write path, which no other frame reads. **Its walk can be shared**: this frame, frame 58, frame 59 and frame 61 all repair the write path and all four price a full night. One night proves all four if the repairs land together, which saves about 60k in this context. That is a scheduling gain and not a batch.

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

- **Batch C, the night's stall. Second of three.** This frame's read of `.rota/clickI_n70_merged.db` against `.rota/clickI_night86.db` is the batch's read. It must be run after frame 58's finding is known, so a repeated session is not counted as a second attempt.

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

- **Batch C, the night's stall. Third of three.** Already waits on frame 38, and its first read is the same read. **Batch C is the only batch that unblocks frame 33**, whose code is built, reviewed twice and gated at 457k and has never walked, because a walk needs a merge and a merge waits here.

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

- **Batch D, the principal seam. First of two.** The batch's one shared thing is one repair site: `probes/walk.py:84-87`, `class Principal` and its `respond(ask)` method (observed: the file, 2026-09-21). This frame puts a sub-agent behind it. Frame 42 puts a designed principal behind the same method.

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

- **Batch D, the principal seam. Second of two.** Already waits on frame 41. **Frame 58 partly discharges this frame's first line.** That frame measured 12 sessions of night 88 as four sessions run three times, hashing the same for all ten turns, so a zero-temperature model repeats an identical prompt exactly. What this frame still needs is the spread over a *similar* problem, which that measurement does not give.

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

- **No batch, and it is the prize.** It is validating, not building. Its walk waits on a merge, a merge waits on frame 37, and frame 37 is the tail of batch C. So batch C is the only work on this stack that releases it.

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

- **No batch. It is the order itself**, and the batches are an ordering inside its step 3 and beyond. It closes when step 7 ships.

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

### 56. 603 recorded prompts exceed the budget `_fit` promises (2026-09-21)

- **No batch, and it gates one.** Its read is over `tests/rota/cassettes.db` and not over a night, so it shares no read with batch B. **It gates frame 53's ruling**, because the fraction `_fit` uses cannot be ruled while 603 recorded prompts say `_fit`'s promise does not hold. **And it needs one finding from frame 54**: every cassette was recorded at `num_ctx` 12288 or 8192, and `_fit_budget` is a function of `num_ctx`, so the 603 must be counted against each cassette's own recorded window and not against 16384.

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

### 57. Why anything spills into system RAM, and whether it is avoidable (2026-09-21) (Roman)

- **No batch. It shares an input and not a read.** Its statistics pass reads the same night as batch B, and it asks a different question of it: what a prompt costs in bytes of GPU memory, not what it carried in characters. Sharing a file is not sharing a read. **Schedule it next to batch B** so the night is opened once.

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

### 58. A retried tick re-runs the identical session (2026-09-21)

- **Batch C, the night's stall. First of three.** The batch's one shared thing is one read of what the Developer was given and what it answered, across the three nights on disk. This frame runs first because it changes what the other two see: a stall of ten attempts is not ten attempts if the retries are one session repeated.

- Rota workflow. A tick that fails is retried up to three times, and **the retry
  is the same prompt at temperature zero, so it is the same session again**
  (observed: night 88's turns, hashed per turn, 2026-09-21).
- **Twelve of night 88's 191 sessions are four sessions run three times.**
  `s137`, `s138` and `s139` share `prompt_hash` `cc8400014e1b2c48` and hash the
  same for all ten turns. `s78/s79/s80`, `s94/s95/s96` and `s162/s163/s164` are
  the same shape.
- **The code states the opposite of what it does.** `rota/core/scheduler.py`, in
  `tick_batch_start`, says "the attempt count is a fact of this table and the
  wake carries it, as tests_failing does, so the second session is not the first
  one verbatim". `rota/core/runner.py:239` is `DETAIL_SHOWN = {"tick:tests_missing"}`,
  so `tick:batch_start` writes a detail the prompt never shows, and
  `tick:boundary` and `tick:challenge` write none at all.
- **What it costs**: every retry of a failing tick spends a full session to
  reproduce a failure byte for byte. On night 88 that is 12 sessions of 191, and
  the three walks each ended stuck on items whose retries could never differ.
- Ends when: a retried tick's prompt differs from the first attempt's, a test
  asserts the difference for each of the four wake kinds, and one night shows a
  retry reaching a different call. Priced: the door is one line plus a detail
  sentence for boundary and challenge, 40k with its tests. The re-records are
  frame 54's problem and not this frame's, because the prompt text moves.
- Waits on: nothing. Roman orders it. It is cheap and it makes every other
  stall-shaped frame cheaper to read, because a stall stops being three
  identical sessions.
- Reasoning: frame 46's status line of 2026-09-21 04:20, finding 2 of the night
  88 diagnosis, and `.rota/clickI_night88.db`.
- Status 2026-09-21 04:20 (rota-02): pushed by cb5428a2, unclaimed, priced.
  Found by the diagnosis of frame 46's walk. It is pre-existing and it is not
  frame 46's.

### 59. The ledger row is shorter than the reasoning it rules from (2026-09-21)

- **Batch B, what a seat lost on night 88. Third of four.** The ledger row's cut is one of the cut sites the batch's read counts, and this frame owns the question of whether that site may cut at all. The read is shared. The repair, 60k, is this frame's alone.

- Rota workflow. The principal's ledger row loses 36 to 225 characters of the
  Critic's reasoning on most falsifications, and the ledger row is what the
  principal rules from (observed: 13 of 191 sessions of night 88 carry a
  `cut ...` error, 2026-09-21).
- **The count exists because frame 46's line 5 made it countable**, which was
  that line's purpose. The design record's named consequence was that the
  ledger row is shorter than the verdict it derives from and nothing says so.
  Line 5 added the notice and the recorded reason. **The count now says the
  loss is routine, not rare.**
- **This is not the cut's fault and it is not a wording fault.** The cut is
  doing what it was built to do. The question is whether a challenge row is
  the right block to cut, when the principal rules from it and cannot ask for
  the rest.
- Ends when: the cause is named in a record, and either the ledger row is
  exempt from the cut with a test that holds it, or the principal is given the
  call that fetches the rest and a test asserts the notice names it. Priced
  from the anchors: one read that groups the 13 by role and mode and measures
  what was lost, 40k. Buys the difference between a tidy notice and a ruling
  made on half a verdict. The repair and its test, 60k.
- Waits on: nothing. Roman orders it.
- Reasoning: frame 46's status line of 2026-09-21 04:20, and the design record
  `plans/archive/context-caps-design-2026-09-18.md`, which names the ledger row
  as line 5's reason.
- Status 2026-09-21 05:10 (rota-e7): pushed by 0f086f93, unclaimed, priced.
  Frame 46 named this finding and did not push it. Pushed here so the
  obligation stays countable. This session holds frame 46 and takes no new
  frame.

### 61. An unmet obligation is visible only while something points back at it (2026-09-21)

- **Batch B, what a seat lost on night 88. Fourth of four.** This frame's priced read is "how many refusals go unmet in a night", and it reads the same three columns of the same 738 turns. So it joins the batch's read and pays nothing for it. The repair, 80k, is this frame's alone.

- Rota workflow. A seat's unmet obligation sits in a refusal, in a block that
  the prompt's tail soon buries. Nothing restates it. The seat finds it again
  only if some later line sends it back up its own prompt.
- **Measured on one case, five wordings** (observed: frame 46's re-earning
  pass, 2026-09-21 08:30). In `ACT-TS-five-criteria-one-per-reply` the Tester
  is refused at turn 9: two tests may not share one file. At turn 11 the
  refusal is two blocks above the tail. The old repeat line ended with the
  word `above`, the seat scanned back, found the refusal and wrote the fifth
  test. Four replacements that point outside the prompt all score 0 of 5, and
  the seat writes a prose summary that lists the refused write as done.
- **So the case measured the backward pointer and not the repeat notice**
  (reasoned: the same pass, which removed the settled tone three ways and
  still closed the session). A wording fix cannot keep it, because this
  frame's constraint forbids any claim about where a thing sits in the prompt.
- **The seat does not know its own obligation is open.** It reports as done a
  write the runner refused. That is the fault, and the repeat line was
  covering it by accident.
- Ends when: an unmet obligation is restated where the seat will read it, and
  a test asserts that a refused write is not reported as done. Priced from the
  anchors: one read that counts how many refusals go unmet in a night, 40k.
  Buys the size of the fault. The repair and its test, 80k.
- Waits on: nothing. Roman orders it.
- Reasoning: frame 46's status line of 2026-09-21 08:36, and the re-earning
  pass that produced the five scores.
- Status 2026-09-21 08:36 (rota-e7): pushed by 0f086f93, unclaimed, priced.
  **The lever the pass names**: the refusal could restate the unmet obligation
  at the tail, rather than relying on a repeat line to send the seat back.
  This session holds frame 46 and takes no new frame.

### 2. The gauntlet on the lineage (goals 3 and 10)

- **No batch.** It waits on frame 4, whose step 5 is this frame's breadth.

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

- **No batch.** It is the bottom frame and it waits on frame 2.

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
