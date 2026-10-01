# Frame 100, the window drops earlier reads: design record, revision 1

Rota workflow (the seats). Design reader, 2026-10-01. Lines at commit 02df37c.

## Mechanism

### How `_fit` evicts (`rota/core/runner.py`)

1. Block 0 of the transcript is the wake. After it, the runner appends pairs:
   the reply, then the results (`:2935`, `:2986`; also `:2376` to `:2461`).
2. `_fit_budget` (`:649`) is `int(num_ctx / 2 * 3.97) - len(system)`: 26,309
   characters for s132 (num_ctx 16384, system 6,213).
3. `_fit` (`:665`) returns a list that fits unchanged (`:682`). Else it cuts the
   wake to two thirds of the budget (`:692`). Below four blocks it only caps
   the latest exchange (`:702`).
4. Else it keeps the wake and the last two blocks, and packs the middle from
   the newest back (`:714`). The loop `break`s at the first block that does
   not fit, so every older block goes too, even a small one.
5. `_dropped_note` (`:581`) goes in at index 1 (`:722`): "[N earlier
   exchange(s) dropped to fit the window. Your instructions and your latest
   results are intact; re-read anything you still need.]".
6. The caller (`:2309`) stores the result. An eviction is permanent, and the
   old notice is a middle block on the next turn. N counts blocks, so
   "2 earlier exchange(s)" is one reply and one results block (`:719`).
7. `_fit` cannot see what a block holds. An 8,000-character reply and a
   2,000-character `code.source` result differ to it only by age.

### How the repeat door counts and refuses

1. The key is `sb.call_key(name, pos, args)` (`:2605`, `rota/core/sandbox.py:345`):
   (path, start, end) with defaults filled in. `answered`, `answered_at` and
   `served` live for the session (`:2245` to `:2258`).
2. A repeat is `evicted` when the prompt has the eviction phrase, an earlier
   turn answered the key, and that answer is not in the prompt (`:2715`).
3. An evicted repeat is served again with the prefix "the earlier answer was
   dropped to fit the window, so this prompt does not hold it" (`:2886`), and
   `served[key]` goes up by one (`:2883`).
4. At `served[key] >= SERVE_CAP` (3, `:578`) the door refuses (`:2758`):
   "served three times this session and the result does not fit the room
   this seat has; not served again. Ask code.source for a narrower span, or
   finish without it."
5. The refusal's reason is false for s132. Its results were 2,081 to 8,643
   characters in a 26,309 budget (observed: `.rota/clickI_night99.db`,
   2026-10-01). The other blocks took the room, not the result.

### The `code.source` op (`rota/roles/api.py:8183`)

It returns `{path, start, end, text, lines}`, plus `defs` and a `note` for a
`.py` file longer than the span. In s132 `defs` and the note are about 700
characters on every read (observed: s132 prompts, 2026-10-01).

## Evidence

All counts are (observed: the named database, 2026-10-01). Calls count only the
`TOOL:` lines before a reply's first invented result, because the runner drops
the rest (`FABRICATED_RESULT`, `:526`, rule 1 at `:2537`).

s132 is identical on all four nights: the completions hash to 8e8d3651d6 on
nights 98, 99, 100 and 101. s132 is a replay from the cassettes, not a night 99
event alone.

s132, `.rota/clickI_night99.db`, Developer, qwen3.5:9b, file
`src/click/utils.py` (688 lines). "N" is each notice in the prompt.

| seq | N | call(s) that ran | span (read count) |
|----|----|----|----|
| 1 | - | model.load, code.probe, code.source | 0-400 (1) |
| 2, 3, 4 | -, -, - | code.source each | 346-390 (1), 390-450 (1), 450-688 (1) |
| 5, 6 | 2, 2 | code.source each; 5 invented results | 251-346 (1), 680-688 (1) |
| 7, 8 | 3, 3 | code.source each; 8 invented results | 346-390 (2), 346-390 (3) |
| 9, 10 | 4, 4 | model.load; code.source | 251-346 (2) |
| 11 | 4 | code.write, whole file, refused: drops 8 names | - |
| 12 | 2 | code.source | 0-688 (1) |
| 13, 14 | 6, 10 | code.write in a 30,894-character reply, cut; code.probe | - |
| 15 to 18 | 2 each | code.source each | 251-346 (3), 346-390 (4), 390-450 (2), 450-688 (2) |
| 19, 20, 21 | 2, 8, 5 | code.source each; 19 and 21 invented results | 346-390 (5), 251-346 (4), 346-390 (6) |
| 22 | 2 | code.source x3; refusal in prompt | 346-390 (7), 390-450 (3), 450-688 (3) |
| 23, 24 | 4, 2 | code.source each; 23 invented results; refusal in prompt | 346-390 (8), 251-346 (5) |
| 25 | - | session end | - |

- 22 `code.source` calls ran. 15 repeat an earlier (file, span). Span 346-390
  ran 8 times.
- Result sizes in characters: 0-400 12,409, 0-688 14,179, 450-688 8,642,
  251-346 4,105, 390-450 2,811, 346-390 2,186.
- The working set 251-688 is about 17,700 characters. The room for exchanges
  is about 21,500 (26,309 less a 4,743 wake), shared with replies of 30,894
  (cut), 8,173 and 7,373.
- Five replies (turns 5, 8, 19, 21 and 23) invented tool results.

Four nights. `sessions.committed` is 1 for every session, so the proxy for a
code commit is "a prompt of the session holds `OK code.commit`".

| night | sessions with 3+ runs of one (file, span) | of them Developers | Developers with `OK code.commit` |
|----|----|----|----|
| 98 | 9 | 7 | 3 |
| 99 | 5 | 3 | 0 |
| 100 | 9 | 7 | 2 |
| 101 | 9 | 7 | 5 |

Deduplicated by completion hash, the four nights hold 22 distinct sessions:
20 Developers and 2 Vision Keepers. 10 of the 20 Developers reached an
`OK code.commit`. Turns with the eviction phrase: 216 of 1,001, 115 of 716,
253 of 1,089, 275 of 879. Turns with "served three times this session": 29,
7, 18, 6.

## Options

### A. Keep the newest read of each file

`_fit` packs in two passes. Pass 1 reserves the newest results block that
holds a `code.source` result for each path. Pass 2 packs the other middle
blocks from the newest back, with `continue` in place of `break`.

- Edit sites: `_fit` `:665` to `:722` gains `keep: set[int]`, the indices of
  the newest source block per path, which the runner computes at `:2309`.
- Test (`tests/rota/test_runner.py`): a wake, a source result of path P, three
  large replies. Assert the P block survives and the total fits the budget.
- Risk: a 14,000-character read pins most of the room. In s132 A keeps 0-688
  (14,179), and the seat still asks for 346-390, a different key.
- Prose: the notice text stays. Every evicted turn changes, so every cassette
  with the phrase misses: 270 of 18,435 (comment at `:568`, 2026-09-20).

### B. Serve the span again, compact, in place of the refusal

At `:2758`, when the cap is reached, serve `text` only, numbered, without
`defs` and `note`. Count compact serves against a second cap, then refuse
with a true reason.

- Edit sites: `:2751` to `:2775`, and a compact renderer beside `_render`.
  Test: evict one span four times; the fourth serve has no `defs`.
- Risk: B does not stop the eviction, so s132 reads until its turns end.
- Prose: only turns where the door fires change (60 on the four nights). Keep
  "served three times this session": `rota/tools/nightreport.py:58` greps it.

### C. Evict the seat's old replies before the results (recommended)

`_fit` drops in tiers, oldest first inside each tier:

1. Old replies become a stub: their `TOOL:` lines, each cut to 200
   characters, or "[your reply of an earlier turn]" if none.
2. Old results blocks go, except the newest block that holds a `code.source`
   result of each path.
3. Those newest source blocks go last.

- Kinds come from position: block 0 is the wake, index 1 with the eviction
  phrase is the notice, then reply and results alternate (every append is a
  pair). A test pins the parity, so a new single append fails.
- Edit sites: `_fit` `:705` to `:722`. `_dropped_note` (`:581`) keeps its text.
  The reason at `:2764` becomes true: "served three times this session, and
  the window took it each time". Keep the grepped phrase.
- Tests (`tests/rota/test_runner.py`): s132's shape (a wake, a 2,000 source
  result, three 8,000 replies; the result survives, the replies are stubs),
  the parity, and the budget promise.
- Risk: a seat loses its own old reply. The calls in it ran or were refused,
  and the results say which (reasoned: the stub keeps the `TOOL:` lines).
- Prose: prompts change on every evicted turn, as in A. The refusal text
  changes on the turns where the door fires.

## Recommendation

Build C. The results of s132 were small and its replies were large (45,000
raw characters in turns 13, 19 and 21), so the order of eviction is the
defect. C fixes the order without a new cap, and meets the ends-when "the
eviction keeps the last read of each file".

## Open questions

1. Q: C changes prompts on every evicted turn, about one turn in four on a
   night. Re-record the whole register, or only the cases that carry the
   phrase? Recommended: only the cases whose cassettes carry
   "dropped to fit the window", because no other prompt changes
   (reasoned: `_fit` returns the list unchanged below the budget, `:682`).
2. Q: The ends-when asks for a night where "a Developer session reads a span
   once". s132 replays from cassettes on every night. Is the measure s132's
   re-record, or any Developer on a fresh night? Recommended: s132 and its
   batch, re-recorded at the closing commit, with 3 or fewer repeats of one
   span.
3. Q: Keep SERVE_CAP at 3 once C lands? Recommended: yes. Change only the
   reason text, so the door still ends a loop that C does not prevent.
