# Frame 100, the window drops earlier reads: design record, revision 2

Rota workflow (the seats). Design reader, 2026-10-01. Lines at commit 02df37c.
Revision 2 folds the design review's findings 1 to 8.

## Mechanism

### How `_fit` evicts (`rota/core/runner.py`)

1. Block 0 of the transcript is the wake. After it, the runner appends pairs:
   the reply, then the results (`:2935`, `:2986`; also `:2376` to `:2461`).
2. `_fit_budget` (`:649`) gives 26,309 characters for s132. `_fit` (`:665`)
   returns a list that fits unchanged (`:682`). Else it cuts the wake to two
   thirds of the budget (`:692`). Below four blocks it caps the last exchange.
3. Else it keeps the wake and the last two blocks, and packs the middle from
   the newest back (`:714`). The loop `break`s at the first block that does
   not fit, so every older block goes too, even a small one.
4. `:722` returns when nothing is dropped. `:723` inserts `_dropped_note`
   (`:581`) at index 1: "[N earlier exchange(s) dropped to fit the window.
   Your instructions and your latest results are intact; re-read anything
   you still need.]".
5. N counts dropped blocks (`:719`), and an earlier notice is one of them.
6. The caller stores `_fit`'s output at `:2309`, so an eviction or a stub is
   permanent. `_fit` cannot see what a block holds, only its age.

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
5. The reason is false for s132: results of 2,186 to 8,642 characters in a
   26,309 budget. The other blocks took the room.

`code.source` (`rota/roles/api.py:8183`) returns `{path, start, end, text,
lines}`, plus `defs` and a `note` (about 700 characters in s132).

## Evidence

All counts are (observed: the named database, 2026-10-01). Calls count only the
`TOOL:` lines before a reply's first invented result, because the runner drops
the rest (`FABRICATED_RESULT`, `:526`, rule 1 at `:2537`).

s132 (`.rota/clickI_night99.db`, Developer, qwen3.5:9b, `src/click/utils.py`,
688 lines) is a cassette replay, identical on nights 98 to 101 (completions
hash 8e8d3651d6). "N" is each notice in the prompt.

| seq | N | call(s) that ran | span (read count) |
|----|----|----|----|
| 1 | - | model.load, code.probe, code.source | 0-400 (1) |
| 2, 3, 4 | -, -, - | code.source each | 346-390 (1), 390-450 (1), 450-688 (1) |
| 5, 6 | 2, 2 | code.source each; 5 invented results | 251-346 (1), 680-688 (1) |
| 7, 8 | 3, 3 | code.source each; 8 invented results | 346-390 (2), 346-390 (3) |
| 9, 10 | 4, 4 | model.load; code.source | 251-346 (2) |
| 11 | 4 | code.write, whole file, refused: drops 8 names | - |
| 12 | 2 | code.source, result cut at line 457 | 0-688 (1) |
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
- The 0-688 read at turn 12 was itself cut: "7,545 of 21,545 characters are
  not shown. The cut fell at line 457". So the seat never held 457-688 from
  that read, which is part of why it asked again.
- Reply blocks as stored in the transcript: turn 13 21,121 (observed by the
  review; cut from 30,894), turn 19 8,173, turn 21 7,373 (both whole).
- The room for exchanges is about 21,500 (26,309 less a 4,743 wake).

Four nights. `sessions.committed` is 1 for every session, so the proxy for a
code commit is "a prompt of the session holds `OK code.commit`".

| night | sessions with 3+ runs of one (file, span) | of them Developers | Developers with `OK code.commit` |
|----|----|----|----|
| 98 | 9 | 7 | 3 |
| 99 | 5 | 3 | 0 |
| 100 | 9 | 7 | 2 |
| 101 | 9 | 7 | 5 |

Deduplicated by completion hash: 22 sessions, 20 Developers, 10 with `OK
code.commit`. Eviction turns: 216/1,001, 115/716, 253/1,089, 275/879. Turns
with "served three times this session": 29, 7, 18, 6.

`tests/rota/cassettes.db` today: 545 of 24,703 cassettes carry "dropped to
fit the window". 3,587 carry "You wrote tool results into your own reply".

## Options

### A. Keep the newest read of each file

Pass 1 reserves the newest results block with a `code.source` result per
path. Pass 2 packs the rest, newest first, with `continue` for `break`.

Edit sites: `_fit` `:665` to `:723` gains `keep: set[int]` from `:2309`. Risk:
in s132 A keeps 0-688, which is cut at line 457, and the seat still asks for
346-390, a different key. Prose: 545 cassettes miss.

### B. Serve the span again, compact, in place of the refusal

At `:2758`, serve `text` only, without `defs` and `note`, against a second
cap. Edit sites: `:2751` to `:2775`, and a compact renderer beside `_render`.
Risk: B does not stop the eviction, so s132 reads until its turns end.
Prose: only turns where the door fires change (60 on the four nights).

### C. Evict by kind and by span (recommended)

`_fit` drops in tiers, oldest first inside each tier:

1. Old replies become a stub: their `TOOL:` lines, each cut to 200
   characters, or "[your reply of an earlier turn]" if none.
2. A results block whose spans a newer block re-read or covers goes first
   (de-duplication by span). Then the oldest results blocks go.
3. The newest results block with a `code.source` result per path goes last.

Why tier 2 de-duplicates first. At s132 turn 19 the tail is 8,173 plus about
2,200, so the middle has about 11,100. A tier that protects only the newest
read per path pins 450-688 (8,642), and 251-346 and 390-450 go. Turn 20 then
re-reads 251-346 (reasoned: the review's arithmetic on s132, 2026-10-01). With
de-duplication, the older copies of 346-390 go before any distinct span.

Kinds come from a parallel `kinds` list. The runner appends a kind ("wake",
"reply", "results", "notice") with each block, and `_fit` returns both lists.
Parity from index 2 is false after the first eviction: s132 turns 9, 10, 11
and 13 hold a results block after the notice, and turns 15 to 19 an "ERROR
reply cut" block (observed by the review). Parity from the end also depends
on every append being a pair. A kinds list states the kind and does not
infer it, so a new append site cannot break it silently.

- Edit sites: `_fit` `:665` to `:723` takes and returns `kinds`. `:2172` starts
  `kinds = ["wake"]`. Every append pair (`:2376` to `:2461`, `:2935`, `:2986`)
  goes through one helper that appends to both lists. `:2309` stores both.
- The refusal at `:2764` becomes: "served three times this session, and the
  window took it each time; not served again. Ask code.source for a narrower
  span, or finish without it." Both grepped phrases stay
  (`rota/tools/nightreport.py:58`).
- `tests/rota/test_runner.py:902` asserts "does not fit the room". Change the
  assertion to the new reason.
- Tests (`tests/rota/test_runner.py`):
  1. A wake, a 2,000 source result, three 8,000 replies: replies stubbed.
  2. The post-eviction shape: wake, notice, a results block first, an older
     2,000-character source result, a newer 8,000-character reply, and a
     budget that forces one out. The reply is stubbed and the result survives.
  3. A tail reply that is large and holds an invented result. The tail is
     capped as today, and the budget promise holds.
  4. Two results blocks of the same span: the older goes first.
  5. The kinds list matches the transcript after `_fit`, with and without a
     notice.
- Risk: a stub drops the seat's prose plan and any write body. The results
  say whether the write ran.
- Brief: no developer prompt tells the seat to carry notes in replies (observed: grep, 2026-10-01).
- Prose: 545 cassettes miss. The door's turns change.

### The invented-result cut: a separate frame

Storing a reply cut at its first invented result would remove text the runner
never ran (s132 turns 5, 8, 19, 21 and 23). The edit site is the append at
`:2935`: append `completion.text[:fabricated.start()]`, with `fabricated` from
`FABRICATED_RESULT` (`:526`) as rule 1 uses it (`:2530` to `:2537`).
Recommended: a separate frame. It changes every turn after an invented
result, so 3,587 cassettes miss against C's 545, and one frame's walk then
cannot tell which change moved a case.

## Recommendation

Build C. s132's results were small and its replies large, so the order of
eviction is the defect. C fixes the order, drops repeated spans first, and
meets the ends-when "the eviction keeps the last read of each file".

## Open questions (answered by the coordinator, 2026-10-01)

1. Re-record: only the cases whose cassettes carry "dropped to fit the
   window" (545 today).
2. The night's measure: any Developer session at the closing commit, with 3
   or fewer repeats of one span. s132 re-records by itself when its first
   evicted prompt changes.
3. `SERVE_CAP` stays 3. Only the reason text changes.
