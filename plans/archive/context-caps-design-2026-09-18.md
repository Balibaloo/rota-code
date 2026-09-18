# The context length management system: what exists, and what to change

Rota workflow. Frame 43. The design record. Roman ruled the design at the grill
of 2026-09-18. This record checks that design against the code, and it puts
back the parts the code answers differently.

The scope is five read-only agents, 536k in agents, 282 tool calls, every claim
carried with a file and a line (observed: the harness usage and
`scratchpad/frame40/scope43.json`, kept for the implementer).

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
tokens. That doubles the KV cache for every turn of the night to carry results
the seat asked for and can ask for again. The trim fix is three lines: run the
middle eviction with fewer than four blocks, and cut the last block when it
alone exceeds the budget, saying so, as every other cut here says so.

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
