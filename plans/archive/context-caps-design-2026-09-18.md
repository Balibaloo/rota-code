# The context length management system: what exists, and what to change

Rota workflow. Frame 43. The design record. Roman ruled the design at the grill
of 2026-09-18. This record checks that design against the code and the
measurements, and it puts back the questions the code answers differently.

Status: draft. The scope reports are not all in.

## What the frame assumed, and what the code holds

The frame said one window size serves every wake, and that a prompt over the
window collapses to half and loses its brief. Both are true. The frame then
read the fix as a second, higher cap for a wake whose refs are unbounded.

The code already holds a different fix, and it shipped between the two nights
(observed: `rota/core/runner.py:917-985`, the landing branch).

**The budget.** `_fit_budget(num_ctx, system_chars)` gives a session half its
window, at the measured ratio of 3.97 characters to the token, and charges the
system prompt against the same budget (observed: `rota/core/runner.py:462-470`).
Half, because half is what the server leaves when a prompt overflows. `_fit`
trims the transcript to that budget and says so.

**The per-part caps.** `RESULT_CHARS` is 6000, `SOURCE_CHARS` is 14000,
`PUSH_CHARS` is 20000, and `LANDING_ROWS_CHARS` is 6000 (observed:
`rota/core/runner.py:390-448`). Each carries the measurement that set it. Each
cut says it was cut.

**The degradation path for the landing wake.** When the rows behind a page do
not fit `LANDING_ROWS_CHARS`, the runner does not drop them silently and does
not raise the window. It replaces them with a numbered map of one line each,
and it tells the seat where to find a whole row (observed:
`rota/core/runner.py:950-962`):

    "lines": {"71": "unstyle (constraints)", ...}
    "rows_not_shown": "the 67 rows behind this page do not fit this window.
     Every line is on the page. `rulings.line` reads the row behind one line"

## The measurement that settles the first question

The same page, on two nights, in two prompts (observed: the `turns` rows of
both run databases, measured on qwen3:8b):

| | night 85, s110 | night 86, s121 |
| --- | ---: | ---: |
| the page, in tokens | 3019 | 2993 |
| the whole prompt, in tokens | 17195 | 5248 |
| the user part, in characters | 64381 | 15599 |
| tool calls the seat made | 0 | 1 |
| rows ruled | 0 | 67 |

Night 85 carried the resolved rows twice, once under `resolved_refs` and once
under `landing.line_rows`, 21402 characters each way (observed: the comment at
`rota/core/runner.py:922-936`, which records the same measurement). Night 86
carried the line map and the note. The page did not change. The prompt around
it fell by three quarters, and the seat then ruled all 67 rows.

**So the higher cap has no customer on this path.** The seat did not need the
rows. It needed the page, its brief, and a way to fetch a row if it wanted one.
A live seat ruled 77 lines correctly from 5565 tokens at `num_ctx` 12288
(observed: the diff review of 8ebbae1, recorded in the same comment).

## The questions this raises for Roman

These go back to Roman because they change his ruled design.

1. The design says an unbounded wake gets a second, higher cap, and that its
   only purpose is to avoid paging. The landing path already pages, and the
   paging works better than the whole rows did. Does the higher cap still
   apply, and to which wake?
2. If the answer is that paging is preferred wherever a seat can fetch a row,
   then the flag on `Wake` says something different from "bounded or
   unbounded". It says whether the seat can work from an index. Is that the
   flag?
3. The cost of the higher cap is measured and it is not small. A changed
   `num_ctx` re-allocates the KV cache, which costs a model reload in each
   direction, and a spill takes a turn from 12.5 s to over 100 s (observed:
   `plans/operating-facts.md`). Is a wake worth that, when the index cut costs
   one extra tool call?

The rest of this record waits on the scope reports.
