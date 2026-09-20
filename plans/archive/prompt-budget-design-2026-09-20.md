# One designed budget for a prompt: the scope, and what it overturns

Frame 46. Rota workflow. Written 2026-09-20 by session 0549dc76 from a scope
of six questions, each verified adversarially against the code it cites.

Evidence: `plans/archive/prompt-budget-scope-2026-09-20.json`, the full
return of twelve agents, and `plans/archive/prompt-budget-scope-2026-09-20-digest.txt`,
the summaries, the refusals, the surprises and the misses. The scope cost
1206692 tokens in 12 agents, 459 tool calls, 19.2 minutes.

## 1. The frame's premise is half wrong, and the half that is wrong is load bearing

The frame says no single place answers "what may this prompt contain", and
that nothing sums the caps. **One budget already exists and already binds**
(observed: `rota/core/runner.py:566`, and the night 87 measurement).

```
_fit_budget(num_ctx, system_chars) = max(2000, int(num_ctx / 2 * 3.97) - system_chars)
```

It caps the system string plus the user string. Night 87's largest prompt of
3599 was 8191 tokens against a 16384 window, which is two characters under
exactly half (observed: the distribution scope, cross-checked by its
verifier).

Two caps derive from that budget rather than from a night, and a third is
only checked against it (corrected by the design review, 2026-09-20, finding
9):

- `TURN_RESULT_CHARS = SOURCE_CHARS + RESULT_CHARS` **does not derive from
  the budget.** It is two night constants and it does not move when
  `num_ctx` moves (observed: `rota/core/runner.py:430`). Its comment reasons
  against `_fit_budget(12288, 4000)` and computes nothing from it, so it now
  binds well below the 16384 budget.
- `wake_room = (budget * 2) // 3` (observed: `rota/core/runner.py:596`).
- `result_room` charges the turn's results against the wake and the reply,
  and is decremented again inside the turn for each refusal line (observed:
  `rota/core/runner.py:2154-2157` and `2347-2348`). **This is an allocator in
  everything but name.**

So the design does not start from nothing. It starts from one budget, one
derived allocation, and a priority order that `_fit` already keeps: the head
and the last two blocks are never dropped, and the middle is evicted
newest-first.

## 2. What is actually wrong, in the order it costs

### 2.1 Half of every window is unreachable, by construction

The budget is half the window because ollama collapses a prompt over
`num_ctx` to `num_ctx / 2 + 2` and keeps the tail, which cuts the brief off
the front (observed: the docstring at `rota/core/runner.py:566`, finding 79).
Halving is the defence against that collapse.

**The consequence nobody stated before this record**: frame 43 raised the
window from 12288 to 16384 and bought the lower half only. The reachable
budget went from 24391 to 32522 characters. A prompt can never exceed 8192
tokens on a 16384 window, whatever the design does, while the halving stands
(reasoned: the assistant, from `_fit_budget` and night 87's ceiling).

117 of 3599 turns sat within 520 characters of that ceiling, so it binds for
3.3 per cent of turns and is invisible for the rest (observed: the
distribution scope).

### 2.2 Nothing measures the assembled prompt before it is sent

One place holds the whole prompt: `payload["messages"]` in
`OllamaBackend.complete` (observed: `rota/llm/llm.py:355-358`). That place is
transport. It measures nothing and holds no budget.

The only whole-prompt measurement runs **after** the reply (observed:
`rota/llm/llm.py:415`). The system learns the prompt did not fit from the
answer it already paid for. The overflow detector is pure reporting: nothing
retries, widens or re-sends (observed: `rota/llm/llm.py:416`,
`rota/core/runner.py:1990-2001`).

This is the real gap. It is not assembly, and it is not the page.

**Where the check goes is a plumbing decision, and it decides whether any
recorded case can observe it** (observed: the design review, finding 4).
`rota/llm/llm.py:416` is the only assignment of `truncated` in the
repository. `LiteLLMBackend`, `ScriptedBackend`, `RoutedBackend`,
`RecordingBackend` and `ReplayOnlyBackend` never set it, and the suite
replays through `ReplayOnlyBackend`. **A whole-prompt check placed where the
existing one sits is dead to every recorded case.** That is the shape frame
43 met with `graph.json`: green, and a no-op for its own customer. The check
goes in `run_session` beside `_fit` at `rota/core/runner.py:1972`, above
every backend.

### 2.3 The system prompt is charged but never cut

`_fit_budget` subtracts `len(system)` and never trims it (observed:
`rota/core/runner.py:566`). An oversized brief plus an oversized signature
list drives the budget to its 2000-character floor, and the transcript pays
the whole price while the brief pays none. Night 87's largest system was
10141 characters, so the floor never bound, but nothing prevents it.

### 2.4 The pushed working set is the part that moves

At the 90th percentile the pushed working set is the largest part of the
prompt, and it is the largest single part in about two thirds of the turns in
the 85th to 95th percentile band (observed: the distribution scope; the
verifier reproduced the ordering and put the share at 58.6 per cent against
the report's 48.3, on a band of 423 turns).

**This section named the wrong ops and the wrong number. The design review
measured both** (observed: the review's probe 2 over night 87's 463 pushes,
2026-09-20, findings 1 and 2). The corrected text follows. The original
claimed that `code.area`, `code.front` and `code.boundary` fill the wake, and
that four pushed reads can put 80000 characters into it.

**The op that fills the wake is `decisions.search`, and it has no budget at
all.** Night 87's pushed characters split `decisions.search` 55.5 per cent,
`code.callables` 12.1, `problem.consult` 5.2, `glossary.consult` 5.1.
`code.area` appears in 4 pushes of 463, `code.front` in 1, `code.boundary` in
5. So the three ops this record first named fire in 10 pushes of 463, and
their upstream budgets are not the problem.

`push_working_set` runs up to six queries and keeps every matching row, and
`decisions_search` has no LIMIT (observed: `rota/core/runner.py:1634-1644`,
`rota/roles/api.py:5436-5440`). Its median pushed size is 20105 characters,
which is `PUSH_CHARS` plus the notice, **so it saturates the backstop on
nearly every push** and is then told to ask for the next range, which a push
cannot use.

**`PUSH_CHARS` as a total is worth 1605 characters, not 80000.** Night 87's
largest pushed block is 21605 characters. 95 of 463 pushes exceed a 20000
total, by 670 to 1605 characters each (observed: the review's probe 2, with
probe 3 proving these are pre-cut sizes: only 4 of 746 first wakes carry the
wake-cut note). Capping the block once would remove at most 1605 characters
from one wake, and it would cut `decisions.search` further while its
recovery sentence still names no usable call.

**The repair is a character budget for `decisions.search` at
`rota/core/runner.py:1634-1644`, before any change to `PUSH_CHARS`.**

### 2.5 The one assertable number already has a written-in hole

The first `code.source` of a turn takes `SOURCE_CHARS` whatever the turn's
room says, and the comment says `_cap_exchange` absorbs the overrun
(observed: `rota/core/runner.py:2303-2305`). So a turn can exceed
`TURN_RESULT_CHARS` by design, and a different cap with a different wording
then cuts the overrun.

### 2.6 Six wordings for one event, and three accounting contracts

There are six wordings, not five (observed: the wording scope, corrected by
its verifier at `rota/core/runner.py:709-720`). Only four of eighteen strings
name a call that fetches the rest. The wake cut, the exchange cut and the
middle eviction name nothing.

Three functions that do the same job keep three different contracts:
`_render_cut` and `_render` add the notice outside the limit, `_exchange_cut`
pays for it inside the limit, and a 300-character reserve at
`rota/core/runner.py:436` exists to compensate for the difference.

A pushed read cut at `PUSH_CHARS` is told to ask for the next range. A push
has no range (observed: `rota/core/runner.py:707`).

Two notices in one prompt contradict each other: the eviction notice says
re-read anything you still need, and the repeat line says the answer is
above. The code measures it at 8 of 8183 prompts and leaves it open on
purpose (observed: `rota/core/runner.py:2366-2386`). **The design must rule
on it rather than discover it.**

### 2.7 The silent cuts are many more than anybody counted

Record writes truncate at 160, 200, 300 and 460 characters with no notice at
all, so the principal's ledger can carry a shorter account than the challenge
row it derives from (observed: `rota/roles/api.py:7091-7097`). `code.diff`
cuts to 20000 silently and is pushed to the wake a seat uses to restore what
its diff broke (observed: `rota/roles/api.py:7556`,
`rota/core/runner.py:1619-1620`). The concordance view carries at least a
dozen more (observed: the wording verifier).

## 3. What the frame may not assume

- **Tests already assert three of these numbers.** `test_the_fit_budget_is_half_the_window`
  (`tests/rota/test_runner.py:660-678`), the turn total at `:1100-1113`, and
  `_fit`'s own promise at `:1251`. `tests/rota/test_profile.py:55-63` asserts
  that every shipped profile pins 16384. The frame's line five, "one number a
  test can assert", is partly built already (observed: the verifiers of the
  inventory, the fit and the staleness scopes, each correcting its own scope).
- **The tool schemas never leave the runner.** `schemas` is None unless
  `native_tools` is passed, and nothing in rota passes it (observed:
  `rota/core/runner.py:1879-1880`, `1748`, and `rota/core/loop.py:303-306`,
  the only production call site). Any design that budgets the schemas is
  budgeting a path that does not run today.
- **A window change re-keys the register and the stale line cannot see it.**
  A cassette key holds the model, the temperature, `num_ctx`, the protocol,
  the system text and the user text. `casestatus` matches on case id, prompt
  hash and model only (observed: the staleness scope). Frame 43 avoided the
  cost by raising the shipped profiles and leaving `DEFAULT_NUM_CTX` at
  12288, so the register now replays at 12288 while a night runs at 16384.
- **The live runner stamps `prompt_hash` over the whole prompt**, not over
  the instructions, so the instruction-only rule holds for the register path
  alone (observed: `rota/core/runner.py:1854`, correcting the staleness
  scope).

## 4. The design, in the frame's five parts, as the scope leaves them

1. **One budget for a turn, derived from the window.** Exists, at
   `_fit_budget`. What is missing is that it is computed once per session
   (`rota/core/runner.py:1965`) and covers only what the runner assembles.
2. **The parts in priority order.** Two of the frame's five named parts are
   not budget items: the wake line is 8 tokens at the median and the refs
   line 7. The real order by size is the pushed working set, the older
   results, the brief, the latest results, the older replies.
3. **Allocation down the order.** `_fit` and `result_room` already do this
   with fixed fractions. The change is to compute the numbers from what the
   ranked parts ask for, and to push the budget up to the ops that fill the
   wake.
4. **One wording.** Six exist. Four of eighteen strings name a recovery call.
   The eviction and the repeat line contradict each other on the record.
5. **One number a test can assert.** Three tests already assert three
   different numbers. The design must pick which one is the promise.

## 5. The question the design cannot answer for itself

**Does the prompt budget stay at half the window on Ollama?**

The backend is part of the question (observed: the design review, finding 5).
The collapse to `num_ctx / 2 + 2` that justifies the halving is an Ollama
behaviour, and `LiteLLMBackend` never sends the window at all (observed:
`rota/llm/llm.py:443`, "`num_ctx` is an Ollama option and stays as
provenance"). **On a LiteLLM profile the halving discards half the declared
budget and defends against nothing**, and nothing reports it. So the fraction
belongs to the backend, not to "the window".

**The cost of keeping it, priced against demand and not against prompts
sent** (observed: the design review's probe 4, correcting this record's own
first answer). This record first said the ceiling binds for 3.3 per cent of
turns and is invisible for the rest. That prices the half we keep against
what was delivered. Against what was asked for: on night 87 the cut notices
account for 8784628 characters denied, de-duplicated per session, against
6946907 characters in the 746 final prompts. **The caps removed 1.26 times
what they delivered.** The ceiling looks invisible only because the per-op
and per-push caps already removed the demand upstream.

Keeping it: safe against the collapse on Ollama, and a 16384 window carries
at most 8192 tokens of prompt for ever.

Raising it: needs the assembled prompt measured before the send, which is
line 1 and does not exist today, plus a margin for the chat template that
nobody has measured. It also re-keys the register, where the stale line
cannot see it.

That is a ruling, not a judgement. It goes to Roman.

**The recommendation, after the review**: keep the halving, and spend the
frame on the per-op budget of section 2.4 first. The denied demand is real,
but it is denied upstream by `decisions.search` saturating `PUSH_CHARS` on
nearly every push, and not by the half-window ceiling. Raising the ceiling
would not deliver one character more while that op is unbudgeted.
