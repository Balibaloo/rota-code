# The context length management system: what exists, and what to change

Rota workflow. Frame 43. The design record. Roman ruled the design at the grill
of 2026-09-18. This record checks that design against the code, and it puts
back the parts the code answers differently.

The scope is five read-only agents, 536k in agents, 282 tool calls, every claim
carried with a file and a line (observed: the harness usage and
`plans/archive/context-caps-scope-2026-09-18.json`, the five agents'
reports, kept for the implementer).

The scope report was written to a session scratchpad, which is deleted with
the session. Session 9108c499 ended and its inbox is gone. The file was
copied into the archive on 2026-09-19 (observed: session 4286e076 found the
pointer dead from its own checkout and the file alive in the dead session's
temp directory). **A record's pointer never names a session scratchpad.**

## 1. What exists today

Three mechanisms already manage context, and they do not know about each other.

**The window.** `num_ctx` starts at 12288 in the code and in every shipped
profile (observed: `rota/llm/llm.py:40`, `rota/llm/profiles/local.toml:12`). It
travels as one field of `Pins`. One function can change it per session:
`routed_pins` (observed: `rota/core/runner.py:103-131`). That function reads
`prof.context[wake.role]`, a per-role window that one shipped profile already
uses, `developer = 16384` (observed:
`rota/llm/profiles/local-gemma-critic.toml:32`).

**The prompt budget.** `_fit_budget(num_ctx, system_chars)` gives a session half
its window at 3.97 characters to the token, less the system prompt, floored at
2000 (observed: `rota/core/runner.py:462-472`). `_fit` trims the transcript to
that budget and says it trimmed.

**The per-part caps.** `RESULT_CHARS` 6000, `SOURCE_CHARS` 14000, `PUSH_CHARS`
20000, `LANDING_ROWS_CHARS` 6000 (observed: `rota/core/runner.py:390-448`).
Each carries the measurement that set it. Each cut says so.

**The index cut, built three times.** When a wake is too large, three sites
already replace rows with a shorter form and name what is missing:
`tick:slicing` and `tick:agenda` shrink the pushed working set (observed:
`rota/core/runner.py:1458-1481`), and the landing path replaces the rows behind
a page with a numbered map plus a note naming the tool that fetches one
(observed: `rota/core/runner.py:950-962`). All three exist because a measured
night blew the window.

## 2. The measurement that settles the first question

The same page reached a Liaison seat on both nights (observed: the `turns` rows
of both run databases, measured on qwen3:8b):

| | night 85, s110 | night 86, s121 |
| --- | ---: | ---: |
| the page, in tokens | 3019 | 2993 |
| the whole prompt, in tokens | 17195 | 5248 |
| tool calls the seat made | 0 | 1 |
| rows ruled | 0 | 67 |

Night 85 carried the resolved rows twice, 21402 characters each way, under
`resolved_refs` and under `landing.line_rows`. Night 86 carried the line map
and the note. The page did not change. The prompt around it fell by three
quarters, and the seat then ruled all 67 rows.

**The seat did not need the rows.** It needed the page, its brief, and a way to
fetch a row. A live seat ruled 77 lines correctly from 5565 tokens at `num_ctx`
12288 (observed: the diff review of 8ebbae1, recorded at
`rota/core/runner.py:936`).

## 2b. The overflow that actually happens, and it is not the page

Roman corrected the assistant on 2026-09-18: paging means OS paging, so the
second window exists to keep the model inside RAM. The measurement below was
taken after that correction, and it moves the frame's target.

**The frequent overflow is turn 2 of an ordinary seat.** A seat asks for reads
at turn 1. The results arrive at turn 2. `_fit` cannot trim turn 2, because it
returns early when the transcript holds fewer than four blocks (observed:
`rota/core/runner.py:511-512`). At turn 2 the transcript holds three: the wake,
the reply, the results. The wake-alone cut above it trims `transcript[0]` only
(observed: `rota/core/runner.py:500-503`), and the oversized block at turn 2 is
the last one, not the first.

The recorded prompts are the trimmed ones, because `turns.user` is written
after `_fit` runs (observed: `rota/core/runner.py:1807-1815`). So these are
what the server received:

| | night 85 | night 86 |
| --- | ---: | ---: |
| turns over the `_fit` budget | 86 of 366 | 57 of 825 |
| the largest prompt, in characters | 110250 | 103645 |
| its budget, in characters | 20230 | 20230 |
| the seat and wake | architect, `tick:survey`, turn 2 | the same |

The next four are the Vision Keeper on `tick:reconcile`, at 99999, 75687, 73037
and 70557 characters, every one of them at turn 2 (observed: both databases).
Those two wakes are the most frequent seat wakes of a night: 38 reconcile and 5
survey sessions each night.

**So the window is not what fails.** 14 of 38 reconcile sessions on night 85
and 12 of 38 on night 86 lost their brief this way (observed: the `turns` rows
carrying "prompt did not fit"). The observed entries page did it once on night
85 and never on night 86. The frequent fault is a hundred times the size of the
rare one and it is in the trim, not in the cap.

### What `_fit` guarantees, and why that is the fault

`_fit` keeps three things and evicts the rest of the middle: the first block,
which is the wake, and the last two blocks, which are the latest exchange
(observed: `rota/core/runner.py:514-528`). The wake alone is capped at two
thirds of the budget. **The last two blocks are not capped, and their sum is
not checked.** So the trim cannot get under budget when the latest exchange is
itself over budget, and it does not try.

Two faults follow, and they are different:

1. **Turn 2 is never trimmed at all.** The eviction needs four blocks and turn
   2 holds three (observed: `rota/core/runner.py:511-512`). Turn 2 is the
   largest bucket of over-budget turns on both nights: 24 of 86 on night 85, 27
   of 57 on night 86.
2. **After turn 2 the eviction runs and still cannot win.** The remaining
   over-budget turns are spread from turn 3 to turn 23 (observed: both
   databases). The middle is already gone, and what is left is the wake plus
   the latest exchange.

### The extreme case, which is a different fault again

Session s71, the Architect on `tick:survey`, on both nights (observed: the
`turns` rows of both databases):

| turn | prompt | the seat's reply |
| ---: | ---: | --- |
| 1 | 20183 chars, of which a 19994-char `[source]` push | 25585 chars, **331 tool calls** |
| 2 | 110250 chars | 2332 chars, no call |

The runner answered all 331 calls. It already de-duplicates the content: 327 of
the answers read "OK code.source -> unchanged since you asked earlier this
session; the answer is above." It de-duplicates the answer and not the line, so
the whole exchange, about 90000 characters of repeated calls and repeated
one-line answers, became turn 2's prompt.

The server then cut that prompt to 6146 tokens and kept the tail. The tail is
the 327 "unchanged" lines. So the seat's second turn held no brief and 327
lines telling it that it had already asked.

A runaway reply is rare and its cost is extreme: three replies of 20 calls or
more on each night, and they produce the two largest prompts of the night
(observed: both databases). A repeated call is common: 44 of 366 turns on night
85 and 105 of 825 on night 86 carry at least one "unchanged" line.

**A bigger window makes this case worse, not better.** At 32768 the seat would
have read all 327 lines instead of half of them.

### Is the explosion required? No. The seat has no way to search

Session s10 is the ordinary case, and it answers the question (observed: its
`tool_calls` and `receipts` rows).

The session made 45 calls. Calls 6 to 38 are 33 `code.source` calls over the
same eight paths, cycled four times: `core.py`, `utils.py`, `commands.py`,
`options.py`, `parameters.py`, `exceptions.py`, `help.py`, `termui.py`. Every
one asked for `start=0, end=400`, the largest span. The first cycle returned
52865 characters of source. The rest returned "unchanged since you asked
earlier".

**Its entire output is two ledger rows**, and they cite one document and one
file:

- "the README describes advanced features of Click, including callbacks,
  validation, parameter modifications, and token normalization"
- "the code implements terminal user interface utilities for Click, including
  prompting, confirmation, pager support, and terminal utilities"

So 63023 characters of results bought two sentences that use neither
`core.py`, nor `utils.py`, nor `exceptions.py`, nor any of the eight files the
seat pulled four times.

**The cause is the shape of the mode's tools.** The reconcile mode holds six
ops: `code.prose`, `problem.baseline`, `problem.consult`, `code.source`,
`ledger.log`, `surveys.attest` (observed: `python -m rota.tools.map mode
vision_keeper/reconcile`). Exactly one of them looks at code, and it is a
whole-span dump. The mode has no search. A seat that must find where a claim
lives can only pull spans and read them, so it pulls the largest span it is
allowed, from every file whose name it can guess.

`code.probe(pattern)` already exists and does the other thing: it returns up to
200 index rows of grain, kind, area and fan-in for a name (observed:
`rota/roles/api.py:5659-5684`). It is not in this mode's tool list.

So the explosion is a tool-shape fault first, a budget fault second, and a
window fault last.

### What an over-budget turn costs, stated exactly

The `_fit` budget is half the window, because half is what survives a server
cut. Being over the budget is therefore a warning, not a cut. Being over the
whole window is the cut.

- Night 85: 86 turns over the budget, in 32 sessions. 19 sessions were actually
  cut by the server.
- Night 86: 57 turns over the budget, in 36 sessions. 15 sessions were cut.
- Every session the server cut had an over-budget turn first, on both nights.

So the budget is a true early warning and nothing reads it.

**The window change is cheap, and that is not the question.** If the three
unbounded wakes took a second window, a night would change window twice on
night 85 and six times on night 86, because only one session on night 85 and
three on night 86 ran on such a wake (observed: the `sessions` table). A few
model reloads a night is not a cost worth designing around.

## 3. The five faults the scope found

1. **The window is chosen before the prompt exists.** `routed_pins` runs at
   `rota/core/runner.py:1637`. The prompt is built at `:1723`, about 85 lines
   later. Nothing feeds the prompt's size back. The runner can cut a prompt and
   can never widen a window (observed: the scope of the sizing path).
2. **One cap is larger than the whole budget.** `PUSH_CHARS` is 20000
   characters. `_fit_budget(12288, 6000)` is 18391 characters. The cap is also
   per key, not per push, so a mode with six no-argument reads can ship six
   such blocks. Nothing sums them (observed: `rota/core/runner.py:366`,
   `:409`).
3. **A cut prompt changes nothing.** The runner appends one sentence to
   `outcome.errors` and carries on. There is no retry, no re-fit, no window
   bump, and the answer is used as if the seat had been briefed (observed:
   `rota/core/runner.py:1825-1837`). The sentence then reaches no live surface.
   It is buried in a `turns` row by `session_note`, and it is lost altogether
   when the session later fails (observed: `rota/core/runner.py:2376`,
   `:2381`).
4. **The two cuts are opposite cuts.** `_render_cut` keeps the front and drops
   the tail (observed: `rota/core/runner.py:456`). Ollama keeps the tail and
   drops the front. So the runner's own trim protects the wake and kills the
   pushes, and the server's trim kills the brief.
5. **The attempt bound never bites on a growing ref set.** `tick_key` is
   `role|kind|` plus every ref joined (observed:
   `rota/core/scheduler.py:1333-1334`). One ref more or less is a new key at
   attempt 1. A wake whose refs grow can repeat without limit.

Two more faults are outside this frame and are parked below: the LiteLLM
provider never sends `num_ctx` and never reports a cut prompt, and the setup
screen writes a profile without its `[context]` table.

## 4. The design

In the order that buys the most for the fewest tokens. Lines 1 to 3 hold
whether or not Roman keeps the second window.

1. **Say it where a person is.** Route the cut-prompt account to a live
   surface. The TUI pulse line is already a warning slot with colour levels, so
   a second line costs one entry in its `bits` list (observed:
   `rota/cockpit/tui.py:502-543`). The `rota run` driver never fires `on_step`,
   so it needs the same line by its own route (observed:
   `rota/tools/onboard_run.py:91`). The warning stays until it is dismissed,
   which is Roman's design point 4.
2. **Make every cap derive from the window.** `PUSH_CHARS`, `RESULT_CHARS` and
   `LANDING_ROWS_CHARS` become fractions of `_fit_budget`, and the push cap
   sums across keys. No cap may exceed the budget it is spent inside.
3. **One index cut, not three.** A single helper takes a set of rows, a budget
   and the name of the tool that fetches one row. It returns the rows while
   they fit, and a numbered index plus a note when they do not. The three
   existing sites call it. Any wake that overflows gets it for free.
4. **The second window, only where a seat cannot work from an index.**
   `routed_pins` already holds the whole `Wake` object, with `kind`, `refs` and
   `detail` live and unused (observed: `rota/core/runner.py:103-131`). So a
   per-wake-kind window is a table in the profile beside `[context]` and one
   more line in that function. The plumbing question of the frame is closed:
   nothing needs to be threaded.
5. **The RAM interaction.** `discover.recommend` and `setup.plan` compute the
   fit table at a literal 12288 (observed: `rota/llm/discover.py:240`,
   `rota/llm/setup.py:44`). A second window must be checked against the fit
   table at that window, or the machine spills and a turn goes from 12.5 s to
   over 100 s. So the higher window is allowed only when the fit table says the
   model still fits at it.

## 5. The grill, one question at a time

**Question 1. The measured overflow is turn 2, where the seat's own reads come
back, and `_fit` cannot trim turn 2. Do we fix the trim, or do we raise the
window to hold the results?**

Recommended: fix the trim. A window that holds 110250 characters is about 26000
tokens. That doubles the KV cache for every turn of the night, to carry results
the seat asked for and can ask for again, and in the worst case to carry 327
lines that each say "you already asked".

The fix is four parts, in the order that removes the most context. Only the
last two are about trimming.

1. **Give the reading modes a search, and give the search a place to read.**
   `code.probe` exists and returns index rows, not files. It is missing from 14
   modes (observed: every `.tools` file holding `code.source` and not
   `code.probe`).

   **A probe alone is not enough** (ruled: Roman, 2026-09-18, "a probe or
   overview would also tell you where lines are"). `code_index` holds `grain`,
   `grain_kind`, `area`, `fan_in`, `sym_kind` and `content_hash`. It holds **no
   line numbers** (observed: `rota/core/schema.sql:370-381`). So a seat that
   probes `confirm` learns the name, the kind and the area, and still has no
   way to read it except `code.source(path, 0, 400)`.

   The locate step must return a span. The indexer already parses each file to
   find its symbols, so the start and end lines are known at build time and
   thrown away. Two columns on `code_index`, returned by `code.probe`, turn a
   400-line dump into a 40-line read.

   **This collides with frame 33**, which rebuilt the index refresh path and is
   built, reviewed twice, gated and unwalked. Two new columns change what a
   refresh writes, so the two frames touch the same code. Order them, or merge
   the column change into frame 33's unwalked commit.
2. **Refuse the third identical call in a session, and fix the lie under it.**
   The runner already detects the repeat and answers "unchanged since you asked
   earlier this session; the answer is above". Today it answers that 327 times.

   **The answer is not always true, and that is a live fault** (observed:
   `rota/core/runner.py:1787`, `:2082-2083`). `already_run` is a set built once
   per session. Nothing clears it. `code.write` does not clear it and
   `code.commit` does not clear it. The repeated call still runs, at
   `rota/core/runner.py:2084`, and its result is then thrown away and replaced
   by the "unchanged" line. So a seat that reads a file, writes it, and reads
   it back is told the file is unchanged, and the new content is discarded on
   the way to it.

   That reaches the Developer's own loop. Night 86's s172 wrote
   `src/click/termui.py` and read it in the same session (observed: its tool
   calls). The fix is to key the repeat memory by path and clear the paths a
   write touches, before any refusal is added on top of it.
3. **Cap the results of one turn, not only each result.** `SOURCE_CHARS` is
   14000 and the budget is 21139, so two source reads in one turn exceed
   everything the session can hold. The per-turn total is the missing cap.
4. **Fix `_fit` as the backstop.** Run the middle eviction below four blocks,
   so turn 2 is trimmed, and cap the last two blocks the way the wake is
   capped, saying so.

Part 1 removes the need for the context. Part 2 removes the loop. Part 3 bounds
what one turn can pull. Part 4 catches what the first three miss. Trimming
alone is the worst of the four, because it throws away code the seat asked for
one turn earlier.

The later questions wait on the answer, and they are recorded so they are not
lost:

2. If the trim is fixed, what is the second window still for? Its remaining
   customer is a seat that must hold a whole page and has no tool to fetch one
   row.
3. Who picks the number? `discover.recommend` and `setup.plan` both compute the
   fit table at a literal 12288 (observed: `rota/llm/discover.py:240`,
   `rota/llm/setup.py:44`). A second window is only safe if the fit table is
   computed at that window, so the model still fits the card and the machine
   does not page.
4. `num_ctx` is part of the cassette key (observed: `rota/llm/cassettes.py:118`).
   A per-wake window re-keys every recording of the wakes that change. Do we
   pay that re-record, and for which wakes?

## 6. The price

From the anchors in `plans/operating-facts.md`, walls counted apart.

| line | price | buys |
| --- | ---: | --- |
| the scope, done | 536k | every claim carries a file and a line |
| this record and Roman's ruling | 25k in this context | the design is settled before code |
| a design review of this record | 80k | a context that never traced the code reads it |
| line 1, the warning reaches a person | 90k | a cut prompt stops being invisible |
| line 2, caps derive from the window | 70k | no cap exceeds the budget it spends |
| line 3, one index cut | 130k | the mechanism stops being copied per kind |
| a diff review on a worktree | 70k | the wake path is read by a context that never wrote it |
| the gate before each commit | 36k | no new red and no stale case hides |
| a full night from the closing commit | 20k in this context | the seats meet the new wake |

Total without the second window: 496k in agents and about 45k in this context,
plus about two hours of wall for the night. Line 4 adds about 90k and a
re-record of the affected register cases, and it runs only if Roman keeps it.

## Parked, from this scope

- The LiteLLM provider never sends `num_ctx` and never sets `truncated`
  (observed: `rota/llm/llm.py:441-446`, `:512-514`). Four shipped profiles use
  it. Any plan that sizes a prompt from the recorded pin is wrong for them.
- `Profile.to_toml` writes no `[context]` and no `[think]` (observed:
  `rota/llm/profile.py:303-320`). A profile written from `local-gemma-critic`
  loses the Developer's 16384 window.
- `Profile.pins_for(role)` applies a per-role window that no live caller ever
  reaches, because every caller passes `None` (observed: `rota/cli.py:612`,
  `rota/cockpit/tui.py:1163`, `probes/walk.py:122`,
  `rota/tools/onboard_run.py:51`). Two implementations of one rule, one dead.
- `Profile.keep_alive` is parsed, stored, and never sent (observed:
  `rota/llm/profile.py:48`).
- `tests_missing` puts its unbounded list in `detail`, not in `refs` (observed:
  `rota/core/predicates.py:707-709`). A cap on refs alone would not cap that
  prompt.
- `awaiting_confirm` carries a dead filter, `AND id NOT IN (SELECT value FROM
  config WHERE 0)`, marked "placeholder join" (observed:
  `rota/core/predicates.py:200-201`).
- `turns.ms` is a duration column in a schema whose header forbids durations,
  and the lint that enforces the rule matches `_ms$` and cannot see it
  (observed: `rota/core/schema.sql:767`, `:9-10`,
  `tests/rota/test_schema_has_no_clock.py:12`).
- `_vram_from_ollama` is a stub returning `(None, None)` (observed:
  `rota/llm/discover.py:186-188`). On a machine without `nvidia-smi` every
  model reads as spilling.

## 7. The judgement Roman made of this system

"This seems quite undesigned" (ruled: Roman, 2026-09-18). The record agrees,
and the evidence is in the code's own comments.

Every guard here was added after a night failed, and each comment names that
night: the result cap after a cut function made a Developer ask five more
times; the source cap after night 79; the push cap after a survey read a cut
working set and nobody said so; the wake cut after night 85's landing
sessions; the middle eviction after ten of twelve areas closed while two spun
for sixty sessions; the repeat line after a 14B re-sent the same batch eleven
times; the identical-turn stop after the same; the index cut after the
observed entries page.

Each one is right about the night that caused it. **None of them was designed
against the others, and no single place answers the question "what may this
prompt contain".** The caps are per result, per push, per page. The trim is per
transcript. The window is per session. Nothing sums, and the one function that
could sum, `_fit`, is forbidden to touch the two blocks that are usually the
problem.

A designed version has one shape:

1. One budget per turn, derived from the window, in one place.
2. The parts of a prompt declared in priority order: the brief, the wake line,
   the refs, the latest results, the older results.
3. The budget allocated down that order, so a part that overruns takes from
   what is below it and never from what is above it.
4. Every cut announced in the same words, with the tool that fetches the rest.
5. One number a test can assert: the assembled prompt is inside the budget, or
   the runner says which part it cut and by how much.

That is a frame of its own. It is larger than the four fixes above, and the
four fixes do not need it. They are the repairs that stop the bleeding, and
this is the design that stops the next one.

## 8. Roman's rulings of 2026-09-19, and the measurement that sets the number

**Ruling 1.** The higher window goes to every wake, not to a chosen few. The
system must monitor strictly when the higher window actually spills into RAM
(ruled: Roman, 2026-09-19). So the flag on `Wake` is dropped. There is one
window, it is higher, and a monitor watches the spill.

**Ruling 2.** The symbol spans on `code_index` are a frame after frame 33, not
a change to frame 33's unwalked commit (ruled: Roman, 2026-09-19).

**The monitor already exists.** Ollama's `/api/ps` reports `size` and
`size_vram` per loaded model. The difference is the spill, in bytes. No
instrumentation in the model path is needed.

**The ceiling, measured on the night card on 2026-09-19** (observed: the 3080
at one slot, idle, `/api/ps` after a one-token generate at each window):

| model | 12288 | 16384 | 20480 | 24576 |
| --- | ---: | ---: | ---: | ---: |
| qwen3:8b, the default | 6.79 GB | 7.40 GB | 8.01 GB | 9.04 GB, spills 0.62 |
| qwen3.5:9b, the routed model | 5.77 GB | 5.91 GB | 6.04 GB | not measured |

qwen3:8b costs 0.61 GB for each 4096 tokens of window. qwen3.5:9b costs 0.14
GB for the same, so the default model is the binding one.

**Recommended number: 16384.** 20480 fits at 8.01 GB, which is the whole
practical budget of a 10 GB card and leaves nothing for a busy desktop. 16384
leaves 0.6 GB of headroom and raises the planning budget from 6144 to 8192
tokens, which is a third more.

A note for the implementer: the Titan measures about double these numbers,
because it runs at two slots and allocates a KV cache for each. Read
`/api/ps` on the card the run uses, never on the other one.

## 9. What the adversary and the completeness critic corrected, 2026-09-19

Rota workflow. The design review of 2026-09-19 made fourteen findings. Six
went to an adversary, one per finding, each told to refute and each given the
materiality test of `plans/operating-facts.md:308`: a fault counts only if it
changes what a person does. A separate agent measured the re-record. A
completeness critic read the record and the scope and looked for what both
passes missed. Eight agents, 740875 tokens, 302 tool calls.

**All six findings came back REFUTED.** That number is itself a bias signal,
because an adversary told to default to refuted will refute, so each one is
recorded below by its evidence and not by its verdict. Four of the six carried
a corrected fix that is better than the review's, and two of the review's fix
lines would have made the frame worse.

The completeness critic found more than the review did. Its findings are the
ones that change this frame.

### 9.1 What survives from the design review

**The graph grant. This one is not refuted and it saves repair 1** (observed:
the assistant's own read of `rota/design/graph.json`, where `code.probe`
appears exactly twice, once for `architect` and once for `developer`).
`rota/core/sandbox.py:506-515` drops a name the graph did not grant, in
silence. So a `.tools` edit alone changes nothing for `critic`,
`terminologist` or `vision_keeper`. Session s10, this record's headline
evidence for repair 1, is `vision_keeper/reconcile`. Repair 1 as section 5
briefed it would have gone green and done nothing for its own main customer.
No test asserts that a `.tools` name is graph-granted.

The count is 19 `.tools` files, of which **14 are modes and 5 are A/B prompt
variants** selected by `ROTA_PROMPTS` (observed: `rota/roles/prompts.py:42-59`,
`:142-147`). A variant is not a mode, no case demands one, and zero of the
18270 cassette rows were recorded under a variant prompt. Editing those five
costs nothing. The record's 14 was the mode count and was right.

### 9.2 Repair 4 is half dead. The trim of turn 2 buys nothing

**This overturns section 2b, which is this record's headline diagnosis.**

At turn 2 the transcript holds exactly three blocks. The middle eviction takes
`transcript[1:-2]`, which on a three-element list is empty. So running the
eviction below four blocks evicts nothing at turn 2, whether or not the guard
at `rota/core/runner.py:512` returns early.

The code already says so, and this record missed the comment (observed:
`rota/core/runner.py:505-512`): "The cut above runs on every turn. It once sat
behind an early return on a transcript of fewer than four blocks... Night 85
(2026-09-18): two landing sessions were sent a 17,220 token wake into a 12,288
window... **Only the middle eviction below needs four.**"

The fault this record claims to have found was found already, after night 85,
and fixed by moving the wake-alone cut above the guard. What is left behind
the guard cannot help turn 2.

Removing the guard is worse than useless. `head = transcript[:1]` and `tail =
transcript[-2:]` overlap below three blocks, so the wake is emitted twice and
`dropped` goes negative. `tests/rota/test_runner.py:657` turns red on the
one-block and two-block cases.

**Repair 4 reduces to one thing: cap the last two blocks.** If the guard moves
at all it moves to three, never below.

### 9.3 Repair 2 keeps its purpose and loses both proposed fixes

The review said the repeat branch runs for every op, so a `code.commit` is
swallowed. The measurement refutes the example: night 86 s145's seq 32, 33 and
34 carry a **different** commit message from seq 19, so seq 32 is not a repeat,
and every commit that committed anything rendered in full. No side effect is
lost: every repeated non-read op in both nights is idempotent, and the
`decisions`, `messages` and `ledger` tables hold exactly one row each where a
seat called six times. `code.write` is not affected at all, in zero sessions on
either night, because a call that raises goes to the error branch at `:2115`
and never reaches the repeat line. The review's count of six sessions is one.

The review's fix, to scope the repeat branch to reads, would make repeated
commits and decisions render their full results again. That grows the prompt,
which is the fault this frame exists to remove.

The record's own instruction, "key the repeat memory by path", is also wrong as
written, for a different reason. `already_run` drives two jobs: `fresh_read` at
`rota/core/runner.py:2061`, which holds a write behind an unanswered read, and
the repeat render at `:2082`. A path key on the render suppresses 667 disjoint
paging reads across the two nights, against a false hold that costs 3 batches.
That is a factor of 222 in the wrong direction. Night 85's s17 walks click.py
in 400-line pages, and every page after the first would be answered "unchanged".

**The corrected fix, which closes the real case and adds no prompt:**

1. Register the key **after** the call succeeds, not before it. Today
   `rota/core/runner.py:2083` adds the key ahead of the call, so a write that
   fails and then succeeds with identical arguments has its success swallowed.
   Neither this record nor the review saw that.
2. Store the rendered result with the key, and answer "unchanged" only when the
   new render equals the stored one. The call already runs at `:2084`, so the
   comparison is free. This closes read-after-write without any read or write
   special case.
3. Keep `key = sb.call_key(...)` as the memory key at both `:2061` and `:2082`.
   Add a `by_path` index beside it for invalidation only, and discard a path's
   keys when `code.write` or `code.commit` touches it. The hold keeps today's
   semantics exactly.
4. The refusal of a third identical call is emitted inside the existing repeat
   branch, which is already a `feedback` site with no `raise` in it. Leave the
   refusal counted. Dropping it from `ctx.refusals` would disable the only
   guard that stops a seat ignoring a refusal while varying its reply.

The real case stands and is worth the repair: s145 read `termui.py` at 1014
lines, wrote and committed it, and was then told the file was unchanged, while
seq 27 proves it was 998 lines.

### 9.4 Repair 1 costs about as much as it saves, while the spans are parked

A probe is not cheap. Measured against the 1048-row `code_index` of night 86,
rendered through the runner's own `_render` at `RESULT_CHARS`: median 5553
characters, and 5 of the 15 most common identifier substrings hit the 200-row
cap at `rota/roles/api.py:5667` and truncate at 6084 characters.

Ruling 2 parks the span columns to a frame after frame 33. So in this frame a
probe is still followed by `code.source(path, 0, 400)`. Repair 1 therefore adds
about 5.5k characters to the turn-2 prompt it exists to shrink, and that lands
inside the per-turn total repair 3 introduces. `code.probe` has no limit
argument, so a seat cannot ask for a cheaper one.

This is the open judgement of the frame. Either `code.probe` gets a row limit
and renders well under `RESULT_CHARS`, or repair 1's brief line waits for the
span columns. Sizing repair 3's cap without counting a 5.5k probe per read will
make the cap bite the source read the seat actually needs, which is the exact
failure `rota/core/runner.py:393-397` records from night 79.

### 9.5 The price, measured

**The four repairs stale 98 of 385 live recordings, about 20 to 25 minutes of
model time.** Not a frame-sized cost. The review's finding 10 was right to
raise it and wrong about its size.

| change | recordings stale | model time |
| --- | ---: | ---: |
| 1, `code.probe` and 3 grants, brief line per mode | 49 | about 10 min |
| 1', the same with the brief line in the roles' `base.md` | 221 | about 46 min |
| 2, the repeat call | 18 to 47, by how far it re-keys | 5 to 12 min |
| 3, the per-turn cap | 0 to 2 | under 1 min |
| 4, the last-two-block cap | 6 | about 1.5 min |
| all four | 98 of 385 | 20 to 25 min |

Three facts the implementer needs.

- The `.tools` edit alone stales nothing. `allow` narrows and never widens, so
  no prompt changes until the three grant edges land.
- **Where the brief line goes is a 4.5 times difference**: 49 per mode against
  221 in the four roles' `base.md`.
- A re-record runs with `ROTA_L1=1` and **not** `ROTA_REFRESH=1`. Refresh forces
  a live call on every completion, 1795 calls and about six hours, against one
  live call per newly stale recording.

**The window rise is four times the four repairs put together, and the fork is
invisible in the frame's price table.** Raising `DEFAULT_NUM_CTX`
(`rota/llm/llm.py:43`) stales all 396 live recordings, about two hours of model
time. Raising the shipped profiles instead leaves the register untouched, which
is now measured and not reasoned. Take the profile route.

### 9.6 The stale line cannot accept this frame

**`python -m rota.tools.gate` reports zero stale after a `num_ctx` change that
re-keys 14757 of 18270 cassettes** (observed: `rota/tools/casestatus.py:77-81`
matches `case_id`, `prompt_hash` and `model`, and `num_ctx` is in the cassette
key at `rota/llm/cassettes.py:118` but not in the match; verified by the
assistant's own read). The same file's comment already records the same class
of hole for mode prompts: an edit that leaves `prompt_hash` untouched while
changing the cassette key "reads as a hard red".

CLAUDE.md says the stale line is part of every acceptance. For this frame the
stale line is partly blind. Acceptance needs the replay suite's own result, not
the stale count alone.

One number is unresolved. The price agent's replay reports 8 of 117 L1 cases
missing a recording under qwen3:8b, all Developer cases, each at a turn after
the first. The gate on the same tree at 04:30 reported zero stale and no red
among them. The gate is the instrument CLAUDE.md names, and the likely cause of
the difference is the probe's own pins, because `_think_for` reads
`ROTA_PROFILE` and a probe shell does not carry it. The implementer confirms
this before the baseline, or the 8 read as frame 43's damage.

### 9.7 The window rise and the monitor, corrected

- **gemma3:12b already spills at 12288**, needing 10.87 GB on a 10 GB card, and
  two of the eight profiles the frame raises ship it as the Critic
  (`rota/llm/profiles/local-gemma-critic.toml:19`, `local-gemma-dev.toml:24`).
  Section 8's ceiling table measured only qwen3:8b and qwen3.5:9b and called
  qwen3:8b "the binding one". That is false for the Critic's desk. A monitor
  that warns until dismissed would fire on every wake of a Critic run, for a
  2.7 GB spill this frame did not cause. Leave the two gemma profiles at 12288,
  or give the monitor a per-model baseline so it warns only when a spill grew.
- **The fit table cannot tell 12288 from 16384 for the routed model.**
  `_kv_meta` returns no `head_count_kv` for qwen3.5:9b, so `kv_cache_bytes`
  returns `None` and `fit_of` computes the need from weights alone (observed:
  `rota/llm/discover.py:132-144`). Design point 5 makes that table the guard,
  so the guard passes every window for qwen3.5:9b by construction. Feed
  `kv_cache_bytes` the loaded size from `/api/ps` for such models, or the guard
  is decoration.
- **The monitor reads the wrong server on a Titan run.**
  `rota/llm/discover.py:25` is a bare literal, `http://localhost:11434`, where
  `rota/llm/llm.py:44` is env-aware. The recorder runs on 11435. Both servers
  answer on this box, so the wrong reading looks plausible rather than failing.
  Pass the run's own endpoint into `loaded()`.
- **`{}` means two different things.** `rota/llm/discover.py:195-197` catches
  every exception and returns an empty dict, so an unreachable server and a
  card with nothing loaded are the same value, and the monitor stays silent
  instead of saying it cannot see. Return `None` on the failure path.
- `refresh_pulse` must not make an HTTP call. It is called from five places on
  the render path. Read `/api/ps` once per session in the run loop, write the
  spill to `config`, and let the pulse read the row.

### 9.8 What no record before this one said

**The register does not contain the fault this frame fixes.** The largest live
L1 prompt is 31127 characters. Night 85's largest is 110250. Of 241 live L1
turn-2-or-later prompts, 2 are over the `_fit` budget, 1 has a results block
over 6000 characters, and none has one over a budget-sized cap.

So the suite cannot show that this frame worked. Only the night can. That is
the reason the frame's ends-when is a night and not a test, and it is now a
measured statement rather than a preference.

A third suite replays the register besides L1 and L3: `tests/rota/test_gauntlet.py`.
It holds 11 live recordings, none in the 14 modes, and the four repairs cost it
nothing.
