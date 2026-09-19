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

### 43. Review the context length management system (2026-09-18) (Roman) [4286e076]

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
- Ends when: a night runs from the frame's closing commit and its four
  context numbers beat night 86's, with zero sessions cut by the server.
  Night 86 is the baseline: 297 of 825 turns had their middle evicted, 86
  turns had the wake itself cut, 15 sessions were cut by the server, and
  179117 tokens were discarded (observed:
  `plans/archive/context-caps-design-2026-09-18.md`). Each line priced from
  the anchors in `plans/operating-facts.md`, walls counted apart:
  1. The window rises to 16384 for every wake, and a spill monitor reads
     `/api/ps` and warns with specifics until dismissed: 90k. Buys: Roman's
     ruling of 2026-09-19, with the evidence that it is not spilling.
  2. `code.probe` reaches the 14 reading modes, with a brief line that
     orders probe before source, and the touched modes re-recorded: 100k
     (the sweep 60k, the re-records 40k). Buys: a seat can find instead of
     dump, which is the fault that costs the most.
  3. The repeat memory is keyed by path and cleared by a write, then a
     third identical call is refused: 80k. Buys: a read after a write
     returns the file, and the 327-line loop ends.
  4. A per-turn cap on the total of results: 70k. Buys: two source reads
     cannot exceed what the session can hold.
  5. `_fit` trims turn 2 and caps the last two blocks: 70k. Buys: the
     backstop catches what the four above miss.
  6. A design review of the design record before any code: 80k.
  7. One diff review on a worktree at the commit: 70k.
  8. The gate before each commit, the stale line read: 36k.
  9. The night, and its four numbers beside night 86's: 20k in this
     context, about two hours wall.
  Total: 616k in agents, about 45k in this context. The scope is already
  spent: 536k in five agents.
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
- Status 2026-09-19 03:57 (rota-ff): **the design is settled and the frame
  is priced. No code is written.** The record is
  `plans/archive/context-caps-design-2026-09-18.md`. The scope cost 536k in
  five agents, 282 tool calls. Roman ruled twice on 2026-09-19: the higher
  window goes to every wake with a strict spill monitor, so the flag on
  `Wake` is dropped; and the symbol spans are a frame after frame 33.
  What the design found, against the frame's own first view: the page is
  not the problem. Turn 2 is. A seat asks for reads at turn 1, the results
  arrive at turn 2, and `_fit` returns early below four blocks, so turn 2
  is never trimmed. The cause upstream of that is that 14 reading modes
  hold `code.source` and no `code.probe`, so a seat that must find
  something can only dump files. Session s10 pulled eight files four times,
  63023 characters, to write two sentences citing one file.
  The window ceiling is measured on the night card at one slot: qwen3:8b
  fits at 20480 using 8.01 GB and spills by 0.62 GB at 24576. 16384 is the
  recommended number, which leaves the desktop 0.6 GB.
  **Two grill questions are unasked**, because the session reached its
  context bound: whether the four repairs are one frame or four, and
  whether the designed budget of section 7 becomes its own frame now. The
  peer that takes this frame asks them before it writes code.
- Status 2026-09-19 04:02 (rota-65): claimed by 4286e076 at 83d789a. The
  hand-off came as Roman's paste, not as a peer message (observed: Roman,
  2026-09-19, "session messaging for hand off is not working"). The two
  grill questions go to Roman now, with a third the claim read found.
  **The third: raising the window must not re-key the register.** The
  cassette key holds `pins.num_ctx` (observed:
  `rota/llm/cassettes.py:118`), and the register's `num_ctx` is unpinned,
  so it takes `DEFAULT_NUM_CTX`, 12288 (observed: `rota/llm/llm.py:43`,
  `tests/rota/test_l1.py:35`). An implementer that raises the constant
  turns every L1 and L3 recording stale in one edit, which the frame's
  90k does not carry. The window rises in the shipped profiles instead
  (observed: `rota/llm/profiles/local.toml:12`), and the register keeps
  its keys at zero cost. The implementer's brief must say so.
  The design review of ends-when line 6 is out, cap 80k, ten numbered
  points. It does not wait on either grill question, so it runs now.
  The 536k scope report is rescued into
  `plans/archive/context-caps-scope-2026-09-18.json` at b4396a2. The design
  record had pointed at session 9108c499's scratchpad, which is deleted
  with the session (observed: the pointer was dead from this checkout and
  the peer's inbox refused a message, so that session has ended). A
  record's pointer never names a session scratchpad.
  **The design review runs on Opus, a stated deviation from "Opus builds,
  Fable judges"** (observed: the first launch died at once with "You've
  reached your Fable limit", HTTP 429). Fable is unavailable today, and
  this session is itself Opus. The review's main lever is a context that
  never traced the code, and that lever survives the model change. Cross
  family judgement does not.
- Status 2026-09-19 04:12 (rota-65): **grill question 1 is ruled. The four
  repairs are one frame, four implementer passes, one night** (ruled:
  Roman, 2026-09-19, after he asked which four and read the list). The
  four are ends-when lines 2 to 5, in that order: `code.probe` to the 14
  reading modes, the repeat memory keyed by path and cleared by a write,
  a per-turn cap on the total of the results, and `_fit` trimming turn 2.
  Ends-when line 1, the window rise and the spill monitor, is Roman's
  ruling 1 of 2026-09-19 and is not one of the four.
  The reason on the record: this is one wall, and the repairs interact.
  Repair 1 changes what a seat pulls, which changes whether repairs 3 and
  4 ever fire, so four separate closes would not give four separate
  measurements.
  **Repair 1 ships weaker than the design record assumed** (reasoned: the
  assistant, reading ruling 2 against section 5 of the record). Ruling 2
  moved the symbol spans to a frame after frame 33, so `code.probe`
  returns the name, the kind and the area with no line numbers. A seat
  that probes still reads `code.source(path, 0, 400)`. The repair goes
  from dumping eight guessed files to dumping one found file, which is
  most of the saving. The spans frame later turns 400 lines into 40.
  **Repair 2 is a correctness fix, not a context fix**: the "unchanged
  since you asked earlier" line is sometimes false, and the runner
  discards the true answer on the way to saying it.
  Grill question 2 is ruled the same minute: the designed budget of
  section 7 is pushed as frame 46, unpriced, waiting on this frame's
  night (ruled: Roman, 2026-09-19). **Both grill questions are now
  closed, so the frame may write code once the design review returns.**
- Status 2026-09-19 04:17 (rota-65): design review in, 107763 tokens on the
  harness line against 80k priced, 78 tool calls, 8.5 minutes (observed:
  the harness usage). Fourteen findings, six high. The reviewer named the
  overrun's cause: the graph chase of its first finding, which the brief's
  points did not anticipate.
  **The finding that saves the frame: adding `code.probe` to a `.tools`
  file does nothing unless `rota/design/graph.json` grants the verb**
  (observed: the assistant's own read, `code.probe` appears twice in
  `graph.json`, for `architect` and for `developer`, and nowhere else).
  `rota/core/sandbox.py` drops a name the graph did not grant, in silence.
  So repair 1 as the design record briefed it would have been a no-op for
  `critic`, `terminologist` and `vision_keeper`. Session s10, the record's
  headline evidence for repair 1, is `vision_keeper/reconcile`. The repair
  would have shipped green and done nothing for its own main customer.
  No test asserts that a `.tools` name is graph-granted.
  The count is 19 `.tools` files and 3 graph edges, not the record's 14
  (observed: the reviewer's file scan). The architect's five modes are the
  cheapest, because the edge already exists.
  Four more that change the brief: the repeat branch runs for every op, so
  a `code.commit` was answered "unchanged since you asked earlier this
  session" on night 86 s145 and the seat then re-issued the same commit
  three times; `already_run` drives a call hold as well as the repeat
  render, so the record's "key it by path" would break the hold; a refusal
  that raises can end a session at the fourth refusal; and repair 4 makes
  repair 2's stale line fire far more often, so repair 2 must land first,
  which the ruled order already does.
  **One finding is not yet settled and it is the price**: the reviewer
  says all four repairs re-key the cassettes, and marked it PLAUSIBLE.
  The adversary is out now, as `plans/operating-facts.md:308` requires,
  with six refuters, one measurement of the re-record, and a completeness
  critic. The gate runs beside it on a quiet machine. The code tree has
  not moved since the trusted gate at 8b15af8.
- Status 2026-09-19 04:30 (rota-65): **the gate is green on this tree and
  the pre-code number is taken.** 23 failed, 1914 passed, 27 skipped,
  zero stale, 521.9 s (observed: the gate's own five lines). One new red,
  `test_screens.py::test_sorting_holds_the_view_you_had_scrolled_to`, and
  the gate named it flaky and re-ran it green in 2.27 s. So the real
  count is zero new reds and zero stale, which matches the trusted number
  at 8b15af8.
  **The flaky red has a cause, and it is mine** (reasoned: the gate ran
  from 04:14 to 04:23, the adversary's agents started at 04:16, so the
  two overlapped, and the test that flaked is a timing-sensitive TUI
  test). `plans/operating-facts.md` already says the gate beside a night
  flakes the timing cases. A fan-out of agents is the same load. The line
  is added there.
  The baseline in `.rota-gate.json` is still `e75e67d` from an
  uncommitted tree of 2026-09-17, so the gate says the compare is not
  commit to commit. It re-baselines on a quiet machine after the
  adversary returns, so that every later acceptance in this frame
  compares against a clean tree at a known commit.
- Status 2026-09-19 05:05 (rota-65): **the adversary is in and the design
  changed. The corrections are section 9 of the design record.** Eight
  agents, 740875 tokens, 302 tool calls, 46 minutes (observed: the harness
  usage). Six refuters, one measurement of the re-record, one completeness
  critic.
  All six findings came back REFUTED, which is itself a bias signal, so
  each is recorded by its evidence and not by its verdict. Two of the
  review's fix lines would have made the frame worse. The completeness
  critic found more than the review did.
  What changed, in the order that matters:
  1. **Repair 4 is half dead** (observed: the assistant's own read of
     `rota/core/runner.py:505-512`). At turn 2 the transcript holds three
     blocks and the middle eviction takes `transcript[1:-2]`, which is
     empty, so lowering the guard evicts nothing. The code's own comment
     already records that this fault was found after night 85 and fixed by
     moving the wake cut above the guard. Removing the guard makes head and
     tail overlap and turns `test_runner.py:657` red. Repair 4 reduces to
     capping the last two blocks. **This overturns section 2b, the
     record's headline diagnosis.**
  2. **Repair 1 costs about what it saves while the spans are parked.** A
     probe renders 5553 characters at the median, and 5 of the 15 commonest
     patterns hit the 200-row cap and truncate at 6084. Without the span
     columns a probe is still followed by `code.source(path, 0, 400)`. The
     open judgement: give `code.probe` a row limit, or hold its brief line
     until the spans land.
  3. **Repair 2 keeps its purpose and loses both proposed fixes.** The
     commit was not swallowed, `code.write` is affected in zero sessions,
     and the "six sessions" is one. The corrected fix registers the key
     after the call succeeds, stores the render, and answers "unchanged"
     only when the new render matches. That also fixes a defect no record
     saw: the key is added before the call, so a write that fails and then
     succeeds identically has its success swallowed.
  4. **The stale line cannot accept this frame** (observed:
     `rota/tools/casestatus.py:77-81` matches case, prompt hash and model,
     and `num_ctx` is in the cassette key and not in the match; the
     assistant read it). The gate reports zero stale after a change that
     re-keys 14757 of 18270 cassettes. Acceptance needs the replay suite's
     result, not the stale count.
  5. **The price is measured.** The four repairs stale 98 of 385 live
     recordings, 20 to 25 minutes. The window rise is four times all four
     together: the constant route stales all 396, about two hours, and the
     profile route stales none. The profile route is confirmed by
     measurement now, not reasoned.
  6. Three faults in the monitor that no record named: gemma3:12b already
     spills at 12288 and two of the eight raised profiles ship it, so a
     warn-until-dismissed monitor fires forever on the Critic's desk; the
     fit table cannot tell 12288 from 16384 for qwen3.5:9b, so design point
     5's guard is decoration for the routed model; and the monitor reads
     `localhost:11434` from a bare literal, so a Titan run measures the
     wrong card.
  7. **The register does not contain the fault this frame fixes.** The
     largest live L1 prompt is 31127 characters against night 85's 110250.
     The suite cannot show this frame worked. Only the night can, which is
     now measured rather than preferred.
  Next: the implementer's brief from section 9, then pass 1. The gate
  re-baselines first on a quiet machine.
- Status 2026-09-19 05:54 (rota-65): **the gate is re-baselined clean and
  pass 1 is in and accepted.**
  The baseline is now `f3a7e41`, a committed tree: 22 failed, 1915 passed,
  zero new reds, zero stale, 497.0 s (observed: the gate's five lines).
  That also confirms the flake of 04:30, because the same TUI test passes
  on a quiet machine, 1915 against 1914.
  **Roman ruled at 05:40: do the spans now** (ruled: Roman, 2026-09-19,
  reversing the timing of his ruling 2 of the same day, not its reason).
  The reason survives, because the spans do not edit frame 33's commit
  `7e53796`. They add a commit above it, so frame 33's two reviews and its
  gate stay valid for what they covered. The cost Roman accepted: the
  write path is `rota/onboarding/indexer.refresh`, which is frame 33's
  code, unwalked since 2026-09-17 (observed: `python -m rota.tools.map
  table code_index`, 9 writers, 6 in `indexer.py`). A fault there at the
  night is now harder to attribute between the two frames. The parser half
  is cheap: the tree-sitter node and its start and end points are in hand
  one line before the span is dropped (observed:
  `rota/onboarding/indexer.py:131`).
  The spans run as a pass inside frame 43, not as a new frame, because
  Roman ruled the repairs are one frame and one night measures the set.
  The order is now: repair 2 (done), the spans, repair 1 at ten times
  rather than five, repair 3, repair 4, one re-record, the night. The
  frame re-prices by about +110k in agents for the spans pass.
  **Pass 1, repair 2**: 136616 tokens on the harness line against a 120k
  cap, 68 tool calls, 30 minutes (observed: the harness usage). 103 lines
  in `rota/core/runner.py`, 152 in `tests/rota/test_runner.py`, five
  pinned tests. The implementer stashed its change and re-ran the five:
  three fail on the old runner, two pass as guards. Four deviations, all
  accepted (reasoned: each states its cause, and the first is the sharpest
  — the new refusal enters `sb.ctx.refusals` as `(name, why, "Repeat")`
  because `rota/core/db.py:736` keys a derived re-ask on `"Wall"`).
  Judged by spot reads from a context that never wrote the file: the key
  is registered after the call at `:2158`, `call_key` is still the lookup
  at both `:2116` and `:2137`, `by_path` only invalidates, the refusal is
  a `feedback` line with no raise, and both files are LF with zero CR
  bytes.
  **The gate proved section 9.6 the hard way.** 36 failed against the 22
  baseline, 14 new reds, and `stale (0): none`. Every one of the 14 is a
  STALE report in its own traceback. The arithmetic closes: 1915 plus 5
  new minus 14 staled is 1906. So the acceptance rule for this frame is to
  classify every new red from its traceback, never from the stale line.
  The 14 re-record now. Section 9.5 priced 18 to 47 recordings.
  Section 9.6's open number is resolved and the record says so: the price
  agent's 8 stale L1 cases do not reproduce under the gate's pins.
- Status 2026-09-19 06:21 (rota-65): **the re-record earned back 13 of the
  14, and the fourteenth is a real red that repair 2 caused.** The
  re-record wrote 27 cassettes in 2m42s and replayed 1833 (observed: the
  recorder's own line). The gate then found one new red, not flaky:
  `ACT-DV-edit-inside-the-function`, 0 of 5 runs, needing 4, with
  "forbidden call to `msg.challenge_tester`" on every run. A stale case
  reads as "no recording for the current prompt". This one answers and
  answers wrongly, so it is a behaviour change and not a missing cassette.
  The working hypothesis, not yet the cause: repair 2 refuses a third
  identical call with "asked three times this session and the answer has
  not changed; not answered again", and the Developer escalates to
  challenging the tester instead of finishing. A read-only agent is
  reading the newly recorded turns against the previous ones, because
  CLAUDE.md says a cause goes on the stack only after the failing
  session's turns are read.
  **The spans pass is cheaper than this session told Roman.** `refresh`
  does not write index rows. Both of its paths call `build` (observed:
  `rota/onboarding/indexer.py:559`, `:579`), and the only column `refresh`
  writes itself is `area`. Both `INSERT INTO code_index` statements are in
  `build`. So the span columns land in `build` and `refresh` inherits
  them. The entanglement with frame 33's unwalked code is much smaller
  than the reviewer's phrase "not cheap in the write path" implied, and
  this session passed that phrase on without checking which function
  writes. The migration pattern already exists at
  `rota/llm/cassettes.py:93-100`.
  A meta note for the next peer: do not pipe `python -m rota.tools.gate`
  through `tail`. This session did, and cut the five lines CLAUDE.md says
  to read (observed: the run at 06:05 kept only the traceback re-run).
- Status 2026-09-19 06:30 (rota-65): **the red is diagnosed and the cause
  is not the refusal. Repair 2 told the truth and the truth was bad
  advice.** A read-only agent read the failing session's turns, 60883
  tokens, 41 tool calls (observed: the harness usage). The assistant's own
  hypothesis, that the refusal wording made the seat escalate, is wrong:
  no refusal appears in any of the 15 failing rows.
  The turn-4 prompt moved by exactly two lines and nothing else in 8.6k
  moved (observed: a unified diff of the two recorded `user` fields, keys
  `78524f0c...` and `6787a79e...`). Where the seat used to read `OK
  code.commit -> unchanged since you asked earlier`, it now reads the real
  result, `{"committed": false, "why": "nothing changed", "note": "... If
  the criteria are already met, say so and finish ..."}`. The seat obeyed
  that note, said the criteria were met, and called
  `msg.challenge_tester`, which is the one message its mode names
  (observed: `rota/roles/prompts/developer/tests_failing.md:25`).
  **So repair 2 unmasked a pre-existing bad note.** The note at
  `rota/roles/api.py:8655-8659` is old. The old behaviour hid it behind a
  lie. The case passed 5 of 5 in all 23 earlier loads, 335 rows, and only
  the tree changed. This is the register earning its cost: no unit test
  would have caught a change in what a seat decides.
  Three defects go to pass 2, cap 60k. A commit forgets the write that
  landed it, because `forget(touched)` discards the write key the same
  reply registered. The note must name the ending instead of saying
  "finish". And the repeat refusal is scored as a call a guard threw out,
  because `outcome.errors` entries with a dotted prefix are subtracted at
  `rota/testkit/fixtures.py:615`, so a repeated forbidden call gets a
  silent discount.
  One fact for any later re-record: a case's pinned model wins over
  `ROTA_MODEL`. `ACT-DV-edit-inside-the-function` pins `qwen3.5:9b`
  (observed: `tests/rota/cases/l1_acts.yaml:187`), and the register holds
  zero rows for it under qwen3:8b.
- Status 2026-09-19 07:11 (rota-65): **repair 2 is committed at 7045226.
  The gate is clean on the assistant's own run: 22 failed, 1922 passed,
  zero new reds, zero reds gone, zero stale, 514.5 s.** The 22 are the
  baseline's own and 1915 passes plus 7 new tests is 1922 (observed: the
  gate's five lines, read whole and not piped). `ACT-DV-edit-inside-the-
  function` is green 5 of 5 on qwen3.5:9b, in the live re-record and in a
  replay after it.
  Pass 2 cost 33602 tokens against a 60k cap, 173771 cumulative for the
  agent over two passes, 27 tool calls. Two deviations, both accepted.
  **The first corrected this session's brief with evidence**: the
  write-commit-write case cannot be pinned, because `code.write`'s result
  embeds `written, not committed`, which a commit necessarily empties, so
  two identical writes spanning a commit never compare equal. The
  implementer pinned the observable write-then-write form instead and
  verified it fails on the pass 1 code. Its conclusion, which this session
  accepts: **defect 2, the note, was the whole of the red.**
  The register is backed up by the SQLite backup API, 722 MB in 14 s, to
  `.rota/cassettes_backup_2026-09-19-frame43-repair2.db`. The publish stays
  Roman's and is not done.
  A meta observation, not yet a fact: two different TUI screen tests
  flaked in this session, `test_sorting_holds_the_view_you_had_scrolled_to`
  at 04:30 under load, and `test_opening_a_stale_run_is_refused_with_the_
  reason` at 06:55 with nothing else running. The gate named both flaky and
  re-ran both green. The second one weakens this session's own line in
  `plans/operating-facts.md` that load is the cause. The screens suite may
  be flaky on its own.
  Actual against the 616k estimate, walls apart: design review 107763,
  adversary 740875 in eight agents, the red's diagnosis 60883, implementer
  173771 over two passes, the assistant's gate and re-record runs about
  30k: 1113k. The adversary is the overrun and it is not regretted, because
  it overturned the headline diagnosis and two of the review's fix lines.
  Next: the spans pass, then repair 1, then repairs 3 and 4.
- Status 2026-09-19 07:54 (rota-65): **pass 3, the symbol spans, is in.**
  50325 tokens against a 110k cap, 228483 cumulative for the agent over
  three passes, 40 tool calls (observed: the harness usage). Five files,
  189 insertions. The implementer's gate: 22 failed, 1927 passed, zero new
  reds, zero stale. The arithmetic closes, 1915 plus 7 plus 5 is 1927, and
  the 22 are the baseline's own. The assistant's own gate runs now.
  `code_index` gains `line_start` and `line_end`, the parser keeps the
  definition node's span at `rota/onboarding/indexer.py:131`, `build`
  writes them, the migration sits in `init_db` behind `_has_column`, and
  `code.probe` returns them capped at 60 rows with a note when the pattern
  matched more.
  Three deviations, all accepted. The sharpest: `SCHEMA_MARK` did not move,
  because the mark refuses a database outright and a migrated database is
  not behind the schema (reasoned: the implementer, and the comment in
  `init_db` states it).
  **The entanglement risk with frame 33 did not fire, and it is now
  measured** (observed: the implementer's read of
  `rota/onboarding/indexer.py:479-484`). The freshness aggregate reads
  `grain`, `area` and `content_hash` of path grains only, and a path
  grain's span is constant at 0, so no area hash moves and no attested
  survey reopens. `refresh` needs no change, because both of its paths call
  `build`, which deletes and rewrites every row. A test pins it.
  **One real finding inside frame 33's code, left unfixed on purpose**
  (observed: the implementer, `rota/onboarding/indexer.py:454` and the
  `stack.pop()` walk): `build` uses `INSERT OR IGNORE` and the parser does
  not visit definitions in source order, so a file that defines one name
  twice stores an arbitrary one of them. Before this pass that only decided
  `sym_kind`. Now it decides which lines a seat reads. The fix is a design
  choice between the first definition, the largest, or one grain per
  definition. It is frame 33's code and it is not this pass's to make.
  **A defect this pass introduced, folded into pass 4**: the probe orders
  by `fan_in DESC` and `build` gives every symbol a fan-in of 0, so every
  matching path sorts above every matching symbol. With the new 60-row cap
  a broad pattern can spend the whole cap on paths and return no definition
  at all, which defeats the probe's new purpose. Pass 4 orders symbols
  first, and pays one re-record for both changes instead of two.
- Status 2026-09-19 08:10 (rota-65): **the spans are committed at 9881938
  and pass 4, repair 1, is out, cap 120k.** The assistant's own gate: 23
  failed, 1926 passed, zero stale, 628.1 s (observed: the gate's five
  lines, read whole). The arithmetic closes: 1915 plus 12 new tests is
  1927, less one flake is 1926, and 22 baseline reds plus that flake is 23.
  **A correction to this session's own operating fact.** At 04:30 this
  session wrote that a fan-out of agents flakes the timing cases, from one
  case. Two more have since flaked in the same file, one of them with
  nothing else running. Three different tests of `tests/rota/test_screens.py`
  flaked across five gate runs today, and the gate named and re-ran all
  three green. So the file is flaky and load is not the cause. The line in
  `plans/operating-facts.md` is rewritten to say that, and it says what it
  used to claim.
  Pass 4 carries the trap that would have made repair 1 a silent no-op, the
  14 modes, the per-mode brief line rather than `base.md` at 4.5 times the
  re-record, the ordering fix from pass 3, and the guard that was missing:
  a test that every op named in every `.tools` file is granted by the
  graph.
- Status 2026-09-19 09:30 (rota-65): **pass 4 is in and the suite is one
  red better than the baseline.** 110691 tokens against a 120k cap, 331495
  cumulative over four passes, 91 tool calls, 75 minutes (observed: the
  harness usage). The implementer's gate: 21 failed, 1931 passed, zero new
  reds, zero stale, and **one red gone,
  `test_l1.py::test_l1_case[L1-VK-reconcile-the-readme]`**. That case is
  `vision_keeper/reconcile`, the mode of session s10, which is the session
  repair 1 exists for. The assistant's own gate runs now.
  **A correction this session owes, and it reverses its own headline**
  (observed: the assistant's read of `tests/rota/test_prompts.py:190`).
  The status of 04:17 said repair 1 "would have shipped green and done
  nothing" and that "no test asserts that a `.tools` name is graph-granted".
  The second half is false. `test_a_mode_narrowing_cannot_widen_the_role`
  walks every role, every mode and every `.tools` name against the graph's
  grant, and the implementer proved it by removing an edge and getting four
  failing lines. Repair 1 could not have shipped green. It would have gone
  red.
  What stands: `code.probe` was granted to `architect` and `developer` only,
  so the three edges were genuinely required and section 5 did not name
  them. The silent drop in `rota/core/sandbox.py` is real at runtime.
  The lesson is this session's. The finding had two halves, this session
  checked the half one grep settles and repeated the other on trust. A
  finding is not confirmed because part of it is. Section 9.1 of the design
  record carries the correction.
  **Three of the 14 modes are held out, each measured 0 of 5 with the
  probe** (observed: the implementer, three cases that were green at the
  baseline): `terminologist/criteria`, `terminologist/survey` and
  `architect/survey`. All three are already pushed the source they work
  from, `[code.area]` or the callables list. A mode whose prompt already
  carries the code does not need a search, and the paragraph offering one
  costs the mode its output. Eleven modes shipped.
  **The wording cost three cases and took three measured iterations.**
  "Probe for a name before you read a file" was read by an 8B as "instead
  of reading", and two survey cases went 0 of 5 by probing and never
  reading. Adding "The probe finds the lines. It never replaces the read."
  fixed that and exposed the next fault: the example `pattern='line_total'`
  was copied out of the brief into an artefact, and a constraint shipped
  with `line_total` as both its id and its headline. The line that shipped
  names no identifier.
  A fact worth keeping for any re-record: **reverting a prompt to its
  committed text restores its recordings.** A mode put back replayed 30
  cassettes, zero recorded, and went green (observed: the implementer, on
  `architect/survey`). 101 cassettes were recorded across three wordings
  and the register holds 18409 rows.
- Status 2026-09-19 09:45 (rota-65): **repair 1 is committed at 5241cb9.
  Pass 5 carries repairs 3 and 4, the last two, cap 110k.** The assistant's
  own gate: 22 failed, 1930 passed, zero stale, one red gone, one new red
  which is the screens flake re-run green (observed: the gate's five lines,
  read whole). The arithmetic closes: 1915 plus 16 new tests is 1931, less
  one flake is 1930. The screens diagnosis is settled, because the new red
  is the same test that flaked at 04:30: four flakes today across three
  tests of one file, with and without load.
  Pass 5's brief carries section 9.2 as a prohibition, not a suggestion.
  The guard must not go below three blocks, because the record's headline
  fix evicts nothing at turn 2 and makes head and tail overlap. Repair 4 is
  one thing, the cap on the last two blocks.
  **Frame state for a successor.** Repairs 2 and 1 and the spans are
  committed at 7045226, 9881938 and 5241cb9. Repairs 3 and 4 are out. What
  remains after them: one diff review on a worktree at the closing commit,
  one re-record, and the night against night 86's four numbers. The night
  is the only instrument that can show this frame worked, because the
  largest prompt in the whole register is 31127 characters against night
  85's 110250 (observed: section 9.8 of the design record).
- Status 2026-09-19 10:30 (rota-65): **all four repairs are built. Pass 5
  is in.** 61426 tokens against a 110k cap, 393346 cumulative over five
  passes, 54 tool calls (observed: the harness usage). The implementer's
  gate: 23 failed, 1935 passed, zero stale, one red gone, two new reds and
  **the implementer proved both flaky rather than taking the gate's word**:
  it ran the new `test_arc_synthetic` case four times over plus alone, and
  it never reproduced.
  The per-turn cap is `SOURCE_CHARS` plus `RESULT_CHARS`, 20000, and the
  arithmetic is the reason: one whole source read is 14000 and must not be
  bitten, because night 79 is the case where a cut span was re-asked five
  times and nothing was written; a 60-row probe plus a source read is 16200
  and must fit; two source reads are 28000 and must not. The room is also
  charged against the wake and the reply, so the cut falls where the
  sentence that names it is still useful.
  Repair 4 is the cap on the last two blocks and nothing else. The
  middle-eviction guard stays at four, `_cap_exchange` guards itself at
  three, and it is applied on all three of `_fit`'s returns (observed: the
  assistant's read of `rota/core/runner.py:599-614`).
  Repairs 3 and 4 cost two recordings and no case, against section 9.5's
  price of 0 to 2 and about 6. The register holds 18429 rows.
  **A parked finding worth a frame of its own** (reasoned: the
  implementer): `test_screens.py` flaked five times today across four
  different tests and `test_arc_synthetic` once. Both files run a whole
  screen or a whole arc. A flake that moves around a file is usually shared
  state, not one bad assertion.
- Status 2026-09-19 10:45 (rota-65): **all four repairs are committed. The
  frame's closing commit is 34c3e72 and the diff review is out.** The
  assistant's own gate on that tree: 22 failed, 1936 passed, zero stale,
  one red gone, one new red which is a fifth different screens test, re-run
  green (observed: the gate's five lines, read whole). 1915 plus 21 new
  tests is 1936.
  **The frame's four commits**, in order: 7045226 repair 2, 9881938 the
  spans, 5241cb9 repair 1, 34c3e72 repairs 3 and 4. Against the frame's
  base at 90cd57e: 37 files, 678 insertions, 28 deletions.
  The diff review runs read-only on a worktree at
  `C:/Users/roman/rota_review43`, detached at 34c3e72, cap 90k, eight
  numbered points. **Remove that worktree when the review closes**:
  `git worktree remove C:/Users/roman/rota_review43`.
  **What remains to close this frame**: the review's findings, then a
  night from a worktree at the closing commit, measured against night 86's
  four numbers. Night 86 is the baseline: 297 of 825 turns had their middle
  evicted, 86 turns had the wake itself cut, 15 sessions were cut by the
  server, 179117 tokens discarded. The night is the only instrument that
  can show this frame worked.
  **A note for the night's operator.** The window has NOT been raised. Ends
  when line 1 of this frame says the window rises to 16384 for every wake
  with a spill monitor, and no pass has done it. Section 9.5 says why it
  was left last: raising `DEFAULT_NUM_CTX` stales all 396 live recordings,
  about two hours, and raising the shipped profiles instead stales none.
  Section 9.7 carries three faults that must be fixed with it: gemma3:12b
  already spills at 12288 and two of the eight profiles ship it, the fit
  table cannot tell 12288 from 16384 for qwen3.5:9b, and the monitor reads
  a bare `localhost:11434` so a Titan run measures the wrong card.
- Status 2026-09-19 11:05 (rota-65): **the diff review found seven defects
  and one of them is an own-goal. A fix pass is out, cap 80k.** The review
  cost 130728 tokens against 90k priced, 61 tool calls, 12.7 minutes
  (observed: the harness usage). It probed by running code: 120000 random
  transcripts through `_fit`, every symbol of four real files against
  Python's `ast`, and a pre-change database through the new `init_db`.
  **F4 is the own-goal and only a diff review finds it.** The repeat
  refusal is about twice the length of the "unchanged" line it replaces,
  and repair 3 charges none of it against the turn. Measured at s71's 331
  calls, its 327 repeat lines become 329 longer ones, 48723 characters
  against 29430 for one op and 56571 against 28122 for another. **s71 is
  the session cited in repair 2's commit message and in repair 3's own
  comment, so the two repairs together grow the prompt they exist to
  shrink.** The fix is to emit the refusal once per key per turn.
  **F1, high**: a withheld result is registered as an answer, and every
  stub is byte-identical, so a seat is told "the answer is above" for a
  result it has never been shown, and four such turns end the session.
  **F2, high**: `result_room` is charged against the wake, and `_fit` lets
  the wake reach two thirds of the budget, so a source read can be cut to
  5191 characters. That is below the 6000 that night 79 records as the
  point where the 9B re-asked a cut span five times and never wrote. The
  review also corrects pass 3's own number: a 61-row probe renders 4415
  characters on a real 2871-symbol index, not the 2200 in the comment.
  F3 medium, `forget` clears `already_run` and so moves the read-hold that
  section 9.3 ruled must not move. F5 low, `_fit` overruns by its own
  notice, 116 characters. F6 low, a path grain says its span is 0 and 0 and
  the brief tells the seat to read it. F7 low, the note row names fan-in
  where the rule is now alphabetical.
  One limit of the review, stated: the spans are verified against Python
  only, 77 of 77 symbols matching `ast`. The other grammars in
  `languages.LANGUAGES` are unexercised.

  **HAND-OFF BLOCK, written 2026-09-19 11:20 by 4286e076 (rota-65).**
  Read this before you claim frame 43.

  1. **State, updated 11:55.** All four repairs and all seven diff-review
     fixes are committed. The tree is clean and the review worktree is
     removed. The frame's commits, in order: 7045226 repair 2, 9881938 the
     spans, 5241cb9 repair 1, 34c3e72 repairs 3 and 4, 8ca1028 the seven
     fixes. The register is backed up at
     `.rota/cassettes_backup_2026-09-19-frame43-closing.db`, 749 MB.
     The gate at 8ca1028, run by the assistant, not piped: **21 failed,
     1941 passed, zero new reds, zero stale, one red gone.** One better
     than the baseline and 26 tests richer.
  2. **What remains to close the frame.** Two things only. The window rise
     to 16384 with the spill monitor, which no pass has done. Then the
     night, from a worktree at the closing commit, against night 86's four
     numbers.
  3. **The window rise is the largest single cost in the frame and it has
     a fork.** Raise it in the shipped profiles, never in
     `DEFAULT_NUM_CTX`. The constant stales all 396 live recordings, about
     two hours of model time. The profiles stale none. This is measured,
     not reasoned. Section 9.7 carries three faults that must land with it.
  4. **You cannot resume this session's implementer.** Its six passes of
     context die with the session. Brief a fresh one from section 9 of the
     design record and from the findings in the statuses above.
  5. **The gate baseline is machine-local.** `.rota-gate.json` is
     gitignored and stands at f3a7e41: 22 failed, 1915 passed, zero stale.
     On another machine, re-baseline before you trust "zero new reds".
  6. **Acceptance for this frame does not use the stale line.** It is
     blind here: `num_ctx` and a mode prompt are in the cassette key and
     not in `rota/tools/casestatus.py`'s match. Classify every new red
     from its own traceback. Treat `test_screens.py` and
     `test_arc_synthetic.py` as flaky until a re-run says otherwise.
  7. **Clean up.** `git worktree remove C:/Users/roman/rota_review43`.
  8. **The probes are kept**, in `probes/frame43/`, with a README that
     says which finding each one measures. An agent's scratchpad dies with
     its session, and this frame already lost one pointer that way.

### 46. One designed budget for a prompt (2026-09-19) (Roman)

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
  Not priced. The price waits on night 87, because frame 43's four
  numbers say how much of the bleeding the four repairs already stopped
  (ruled: Roman, 2026-09-19, push it now and price it later).
- Waits on: frame 43, and on frame 43's night. Roman orders this frame
  against 45, 41, 42, 38 and 37.
- Reasoning: `plans/archive/context-caps-design-2026-09-18.md`, section 7,
  and the scope it was written from,
  `plans/archive/context-caps-scope-2026-09-18.json`.
- Status 2026-09-19 04:14 (rota-65): pushed by 4286e076, unclaimed,
  unpriced. The frame exists so the obligation stays countable. The four
  repairs of frame 43 do not need it, and the design record says so. This
  is the design that stops the next fault. The four repairs stop the
  bleeding.

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
