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

Three caps derive from that budget rather than from a night:

- `TURN_RESULT_CHARS = SOURCE_CHARS + RESULT_CHARS` is derived by
  construction (observed: `rota/core/runner.py:430`, and the arithmetic in
  the comment at 420-429).
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

`PUSH_CHARS = 20000` is applied **per pushed key and not as a total**
(observed: `rota/core/runner.py:366`). A role with four pushed reads can put
80000 characters into the wake block before `_fit` runs. A cap named as a
total and applied as a per-item limit is exactly the fault the frame
describes, and it is the one cap that matches the frame's own wording.

The ops budget themselves upstream and know nothing of `_fit_budget`:
`code.area` 10000, `code.front` 5200 or 7000, `code.boundary` 12000
(observed: `rota/roles/api.py:6024`, `6222`, `7319`).

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

**Does the prompt budget stay at half the window?**

Keeping it: safe against the collapse, and a 16384 window carries at most
8192 tokens of prompt for ever. Frame 43's window rise is then worth half of
what it reads as.

Raising it: needs the assembled prompt measured before the send, which
nothing does today, plus a margin for the chat template that nobody has
measured. It also re-keys the register, which the stale line cannot see.

That is a ruling, not a judgement. It goes to Roman.
