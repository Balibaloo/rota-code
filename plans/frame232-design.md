# Frame 232, the design read: where the stream stops on an invented result

Read-only design read on Opus, 2026-10-13 20:46. Meta workflow for this
read. The rule it designs is in the rota workflow, the stream reader of
every seat. Scripts: `scratchpad/f232/` of session b4070ef8 (`common.py`,
`night.py`, `register.py`, `parse_equiv.py`, `probe3.py`, `residual.py`,
`repeat.py`), outputs beside them as `*.out`.

## 0. The result

The stop rule: the stream ends at the first line whose head matches the
runner's `FABRICATED_RESULT` (`OK|ERROR <area>.<fn> ->|:`), once a `TOOL:`
marker stands earlier in the same reply, and keeps the text up to that
head (reasoned: sections 2 to 4; observed: the probes below).

- The 78 completions over 2,000 tokens: 20 fabricated after a `TOOL:` line,
  19 prose with no `TOOL:` line, 25 clean act bodies, 12 cycling replies
  the existing stop caught, 2 other (observed: `night.py`).
- The register: 32,510 recorded completions. The rule shortens 2,474. Each
  of the 2,474 already carries the runner's own "wrote its own tool results"
  sign, so 0 clean act bodies are shortened. The calls the runner runs are
  identical on the kept text in 2,473 of 2,474. The 1 difference is a parser
  quirk, section 3 (observed: `register.py`, `parse_equiv.py`).
- Savings on night 145: 158.0k tokens after the stop in 140 turns, against
  the 179k the investigation counted, about 39 card minutes pro rata. Turns
  over 60 seconds: 12 of 35 end on an invented result and fall under 60
  seconds, so 23 remain (observed: `night.py`).
- The ends-when's night numbers do not both pass with this rule alone:
  20.9k remains by the investigation's measure against "under 20k", and
  23 turns over 60 seconds against "under 10". Section 5 says why and
  proposes the line.

Data note: `.rota/clickI_night145.db` opened `immutable=1` skips its
`-wal` file and shows 1,896 of 1,915 live walk turns and 77 of the 78. This
read uses session e669185f's checkpointed copy,
`scratchpad/n145/clickI_night145.db` of that session, also opened
`mode=ro&immutable=1`. It gives 1,915 turns, 793k tokens and 78, the
investigation's numbers (observed: `night.py`, both files, 2026-10-13
20:40). Tokens are characters over 3.97, the investigation's ratio. Walk
turns are sessions with seq over 104, as in `r2_gen.py`.

## 1. The 78 shapes

Group rules, applied in this order (observed: `night.py`):

1. Fabricated after `TOOL:`: the stop rule fires inside the reply.
2. Prose, no `TOOL:`: no marker in the reply.
3. Clean act: a `TOOL:` marker and no `FABRICATED_RESULT` match anywhere.
4. Cycling caught: `_cycling` fires within the last 400 characters of the
   stored text, so the reply ends at the existing stop.
5. Other: the runner's regex matches, and the stop does not fire.

Columns: the turn as `s<session seq>#<turn seq>`, the seat, the wake kind
(every session's `mode` column reads `normal`), the token estimate, the
seconds, the line index of the first invented result line, the tokens
before and after the stop, and whether the session's account says "wrote
its own tool results". The account is per session, not per turn.

| group | turn | seat | wake | tokens | s | stop line | before | after | account | note |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 fabricated after TOOL | s117#4 | architect | tick:annotate | 8286 | 86 | 2 (last, unended) | 17 | 8269 | yes |  |
| 1 fabricated after TOOL | s121#5 | architect | message | 3298 | 39 | 2 | 17 | 3281 | yes |  |
| 1 fabricated after TOOL | s121#7 | architect | message | 7463 | 98 | 3 | 34 | 7429 | yes |  |
| 1 fabricated after TOOL | s123#12 | developer | tick:batch_start | 2463 | 37 | 2 | 26 | 2437 | yes |  |
| 1 fabricated after TOOL | s124#7 | developer | tick:batch_start | 4541 | 69 | 2 | 21 | 4520 | yes |  |
| 1 fabricated after TOOL | s142#20 | developer | tick:tests_failing | 7836 | 92 | 124 | 1985 | 5850 | yes |  |
| 1 fabricated after TOOL | s150#3 | architect | tick:exhausted | 2368 | 32 | 2 | 14 | 2354 | yes |  |
| 1 fabricated after TOOL | s150#4 | architect | tick:exhausted | 2391 | 34 | 2 | 9 | 2382 | yes |  |
| 1 fabricated after TOOL | s187#11 | architect | tick:annotate | 5585 | 101 | 2 | 17 | 5568 | yes |  |
| 1 fabricated after TOOL | s209#9 | developer | tick:tests_failing | 6437 | 93 | 2 | 21 | 6416 | yes |  |
| 1 fabricated after TOOL | s213#24 | developer | tick:tests_failing | 5226 | 82 | 2 | 21 | 5205 | yes |  |
| 1 fabricated after TOOL | s214#9 | developer | tick:tests_failing | 6399 | 92 | 2 | 21 | 6378 | yes |  |
| 1 fabricated after TOOL | s252#7 | terminologist | tick:criteria | 8891 | 122 | 11 | 447 | 8444 | yes |  |
| 1 fabricated after TOOL | s257#3 | architect | tick:annotate | 8454 | 112 | 2 | 18 | 8436 | yes |  |
| 1 fabricated after TOOL | s291#7 | tester | message | 3055 | 39 | 91 | 2910 | 145 | yes |  |
| 1 fabricated after TOOL | s340#3 | terminologist | message | 2748 | 33 | 20 | 1322 | 1426 | yes |  |
| 1 fabricated after TOOL | s347#3 | architect | tick:exhausted | 3189 | 47 | 2 | 14 | 3175 | yes |  |
| 1 fabricated after TOOL | s361#6 | terminologist | tick:criteria | 4029 | 46 | 81 | 1604 | 2425 | yes |  |
| 1 fabricated after TOOL | s367#4 | architect | tick:annotate | 12602 | 87 | 2 | 18 | 12583 | yes |  |
| 1 fabricated after TOOL | s371#6 | architect | message | 7403 | 94 | 2 | 29 | 7374 | yes |  |
| 2 prose, no TOOL | s128#2 | tester | tick:tests_missing | 8623 | 101 | - | 8623 | 0 | no |  |
| 2 prose, no TOOL | s138#1 | developer | tick:tests_failing | 8968 | 102 | - | 8968 | 0 | no |  |
| 2 prose, no TOOL | s141#1 | developer | tick:tests_failing | 8692 | 110 | - | 8692 | 0 | yes |  |
| 2 prose, no TOOL | s144#1 | developer | tick:tests_failing | 8374 | 102 | - | 8374 | 0 | no |  |
| 2 prose, no TOOL | s145#1 | developer | tick:tests_failing | 9267 | 101 | - | 9267 | 0 | yes |  |
| 2 prose, no TOOL | s145#10 | developer | tick:tests_failing | 3512 | 42 | - | 3512 | 0 | yes |  |
| 2 prose, no TOOL | s145#21 | developer | tick:tests_failing | 7873 | 96 | - | 7873 | 0 | yes |  |
| 2 prose, no TOOL | s145#8 | developer | tick:tests_failing | 7731 | 93 | - | 7731 | 0 | yes |  |
| 2 prose, no TOOL | s211#1 | tester | message | 9167 | 96 | - | 9167 | 0 | no |  |
| 2 prose, no TOOL | s214#18 | developer | tick:tests_failing | 8683 | 127 | - | 8683 | 0 | yes |  |
| 2 prose, no TOOL | s282#1 | tester | tick:tests_missing | 8472 | 130 | - | 8472 | 0 | no |  |
| 2 prose, no TOOL | s285#1 | tester | message | 8627 | 108 | - | 8627 | 0 | no |  |
| 2 prose, no TOOL | s297#1 | tester | message | 9857 | 110 | - | 9857 | 0 | no |  |
| 2 prose, no TOOL | s302#9 | developer | tick:tests_failing | 8438 | 109 | - | 8438 | 0 | yes |  |
| 2 prose, no TOOL | s304#1 | tester | message | 10203 | 117 | - | 10203 | 0 | no |  |
| 2 prose, no TOOL | s335#2 | terminologist | message | 8804 | 106 | - | 8804 | 0 | no |  |
| 2 prose, no TOOL | s378#1 | tester | message | 8878 | 102 | - | 8878 | 0 | no |  |
| 2 prose, no TOOL | s381#1 | tester | message | 9608 | 95 | - | 9608 | 0 | no |  |
| 2 prose, no TOOL | s396#1 | tester | message | 8607 | 109 | - | 8607 | 0 | no |  |
| 3 clean act | s117#20 | architect | tick:annotate | 7426 | 99 | - | 7426 | 0 | yes |  |
| 3 clean act | s135#1 | developer | tick:tests_failing | 2281 | 28 | - | 2281 | 0 | no |  |
| 3 clean act | s142#18 | developer | tick:tests_failing | 2333 | 29 | - | 2333 | 0 | yes |  |
| 3 clean act | s143#1 | developer | tick:tests_failing | 2124 | 26 | - | 2124 | 0 | no |  |
| 3 clean act | s146#14 | developer | tick:tests_failing | 2186 | 28 | - | 2186 | 0 | yes |  |
| 3 clean act | s146#18 | developer | tick:tests_failing | 3088 | 38 | - | 3088 | 0 | yes |  |
| 3 clean act | s182#7 | terminologist | tick:criteria | 8817 | 94 | - | 8817 | 0 | yes |  |
| 3 clean act | s262#16 | developer | tick:batch_start | 2571 | 41 | - | 2571 | 0 | yes |  |
| 3 clean act | s268#6 | tester | tick:tests_missing | 4013 | 54 | - | 4013 | 0 | no |  |
| 3 clean act | s275#2 | tester | message | 2260 | 31 | - | 2260 | 0 | yes |  |
| 3 clean act | s323#3 | developer | tick:tests_failing | 2184 | 26 | - | 2184 | 0 | yes |  |
| 3 clean act | s326#10 | developer | tick:tests_failing | 2510 | 32 | - | 2510 | 0 | no |  |
| 3 clean act | s342#1 | developer | tick:exhausted | 2971 | 36 | - | 2971 | 0 | no |  |
| 3 clean act | s376#2 | developer | tick:tests_failing | 8846 | 95 | - | 8846 | 0 | no |  |
| 3 clean act | s398#2 | developer | tick:tests_failing | 2095 | 27 | - | 2095 | 0 | no |  |
| 3 clean act | s404#2 | developer | tick:tests_failing | 2452 | 31 | - | 2452 | 0 | yes |  |
| 3 clean act | s405#20 | developer | tick:tests_failing | 2311 | 30 | - | 2311 | 0 | yes |  |
| 3 clean act | s405#21 | developer | tick:tests_failing | 2019 | 29 | - | 2019 | 0 | yes |  |
| 3 clean act | s422#3 | developer | message | 4237 | 58 | - | 4237 | 0 | no |  |
| 3 clean act | s422#4 | developer | message | 4022 | 57 | - | 4022 | 0 | no |  |
| 3 clean act | s422#5 | developer | message | 4049 | 57 | - | 4049 | 0 | no |  |
| 3 clean act | s422#6 | developer | message | 4124 | 58 | - | 4124 | 0 | no |  |
| 3 clean act | s423#12 | developer | tick:tests_failing | 7636 | 108 | - | 7636 | 0 | yes |  |
| 3 clean act | s423#17 | developer | tick:tests_failing | 2926 | 36 | - | 2926 | 0 | yes |  |
| 3 clean act | s438#2 | terminologist | message | 3148 | 38 | - | 3148 | 0 | no |  |
| 4 cycling caught | s143#2 | developer | tick:tests_failing | 2116 | 26 | - | 2116 | 0 | no |  |
| 4 cycling caught | s144#8 | developer | tick:tests_failing | 2378 | 28 | - | 2378 | 0 | no |  |
| 4 cycling caught | s191#1 | terminologist | message | 4048 | 57 | - | 4048 | 0 | no |  |
| 4 cycling caught | s201#10 | developer | tick:tests_failing | 3081 | 37 | - | 3081 | 0 | yes |  |
| 4 cycling caught | s226#10 | terminologist | message | 2030 | 30 | - | 2030 | 0 | no |  |
| 4 cycling caught | s252#10 | terminologist | tick:criteria | 2462 | 37 | - | 2462 | 0 | yes |  |
| 4 cycling caught | s266#5 | tester | tick:tests_missing | 2968 | 42 | - | 2968 | 0 | no |  |
| 4 cycling caught | s293#5 | tester | message | 6961 | 81 | - | 6961 | 0 | no |  |
| 4 cycling caught | s324#1 | tester | message | 2557 | 30 | - | 2557 | 0 | no |  |
| 4 cycling caught | s326#3 | developer | tick:tests_failing | 3751 | 42 | - | 3751 | 0 | no |  |
| 4 cycling caught | s394#3 | terminologist | message | 4663 | 48 | - | 4663 | 0 | no |  |
| 4 cycling caught | s396#4 | tester | message | 2245 | 29 | - | 2245 | 0 | no |  |
| 5 other | s117#19 | architect | tick:annotate | 3336 | 41 | - | 3336 | 0 | yes | open 1 |
| 5 other | s117#23 | architect | tick:annotate | 3408 | 45 | - | 3408 | 0 | yes | open 1 |

| group | turns | tokens | minutes | tokens after the stop |
|---|---|---|---|---|
| 1 fabricated after `TOOL:` | 20 | 113k | 23.9 | 104.1k |
| 2 prose, no `TOOL:` | 19 | 162k | 32.6 | 0 |
| 3 clean act | 25 | 93k | 19.8 | 0 |
| 4 cycling caught | 12 | 39k | 8.1 | 0 |
| 5 other | 2 | 7k | 1.4 | 0 |

Readings:

- In 15 of 20 fabricated turns, the invented line is line 2 or 3: one
  `TOOL:` line, a blank, then `OK <fn> -> ...` runs to the cap. 100 tokens
  or less come before the stop in 15 of them (observed: the table).
- s117#4 writes `OK code.source -> ["import click...` as one line that
  never ends, 8,269 tokens. A rule that waits for a complete line never
  fires there. The rule therefore tests the head of the line still in the
  buffer, and stops when the head matches (observed: `probe1.py`, s117#4).
- The two "other" turns, s117#19 and s117#23, write a `batches.annotate`
  call whose list string never closes, then `OK batches.annotate -> {...}`
  as the last line. The stop fires near the end at most, so the two cost
  nothing either way (observed: `probe1.py`).
- The investigation's 26 fabricated turns used `^(OK|ERROR|NOTE) `. The
  runner's regex does not match `ERROR tests.encode(id='...'): ...`, the
  runner's own feedback shape with the call's arguments. 4 of the 78 carry
  only that shape, s252#10, s266#5, s268#6 and s293#5, and the cycling stop
  caught all 4 (observed: `probe1.py`).
- Every fabricated turn's session carries the account line (20 of 20).

## 2. The stop line and the clean act bodies

The stop: on each piece, after the line split, take the current line head,
`line_buf` (the partial line) or the line that just completed. When
`saw_tool` is set and the head matches the anchored regex, stop (reasoned:
s117#4 needs the head, section 1).

Does the regex match a clean act body? Counts on the register,
`tests/rota/cassettes.db` (the file `rota/tools/gate.py` reads through
`paths.DEV_DB`, table `cassettes`), opened `mode=ro&immutable=1`
(observed: `register.py`, 2026-10-13 20:42):

| count | value |
|---|---|
| recorded completions | 32,510 |
| with a `TOOL:` marker | 27,690 |
| with an act call (`code.write`, `tests.encode`, `batches.annotate`, `code.edit`) | 4,014 |
| the runner's regex matches anywhere | 2,884 (539 with an act call) |
| the rule shortens | 2,474 (523 with an act call) |
| shortened and the runner does not flag | 0 |
| tokens after the stop | 886k |

- A shortened completion is by construction one the runner already flags
  "wrote its own tool results", so the rule cuts 0 clean act bodies, where
  clean means no invented result line (observed: the table).
- The stronger proof is the calls. For each shortened completion,
  `toolproto.extract_lenient` parses the full text and the kept text as
  `runner.py:3578` does, and the calls with a start before the match are
  compared. Night 145: 149 of 149 identical, all live turns. Register:
  2,473 of 2,474 identical, and the match offset never moves (observed:
  `parse_equiv.py`).
- The 523 shortened completions with an act call run the same act. The
  act stands before the invented line, and the runner already runs nothing
  after it (observed: `parse_equiv.py`).
- A quote guard is not needed. A rough open-string-or-paren test says the
  match line sits inside an open call in 237 register completions. In 175 of
  them the guard alone decides. An unguarded stop changes the runner's run
  calls in 0 of the 175 and in 0 of 2 on night 145 (observed: `probe3.py`).
  So the rule carries no guard, and the pass needs none (reasoned: a guard
  is state that no recorded case uses).
- The 1 register difference, completion with `l_3aea8c134c`: a qwen3
  `<think>` block holds a bare `code.write(...)` at a line start. On the
  full text, `extract_lenient` (`toolproto.py:1441-1446`) places a later
  marked `code.write` with the same raw at the first copy by
  `text.find(raw)`, so the bare one counts as "inside marked" and is
  skipped. On the kept text the later copy is gone, and the bare call runs
  by the documented rule. The runner's choice on the full text is the
  accident. `marked_starts` holds the true offsets (observed: `probe2.py`;
  reasoned: the code at `toolproto.py:1430-1446`). That is a parser defect
  for its own frame, not a wall of this one.

## 3. The kept text and the runner

With the stream ended at the head of the invented line, the runner still
acts the same (observed: `parse_equiv.py`; reasoned: the lines below):

- `runner.py:3578-3580`: `extract_lenient` parses the kept text. The calls
  before the head are complete lines, so they parse the same.
- `runner.py:3581`: the cut note reads `done_reason == "length"`. The new
  stop must set another value, or the seat gets a false cut note.
- `runner.py:3828`: `FABRICATED_RESULT.search(scanned)` finds the kept head,
  because the regex needs only `OK|ERROR <area>.<fn> ->|:`. The offset is the
  same as on the full text in 2,474 of 2,474.
- `runner.py:3829-3835`: the account line "wrote its own tool results"
  and the seat's feedback are unchanged.
- `runner.py:3836-3848`, rule 1: calls with `call_at[i] > fabricated.start()`
  are dropped. On the kept text no call follows the head, so the same calls
  run, every `TOOL:` call written before the line, however many.
- `rota/tools/nightcount.py:122,136` counts the sign with the same regex on
  the stored completion. The kept head still matches, so night 146's count
  of the sign is comparable (reasoned: the regex on the kept head).
- One side effect, small: the verbatim-repeat end (`runner.py:3776-3780`)
  compares whole completions. On night 145's recorded text the stop makes 4
  more consecutive turns identical, 132 against 128, and ends 1 session
  earlier (observed: `repeat.py`). On a live night the next prompt carries
  the kept text, so the next turns differ anyway (reasoned).
- Replay: `ReplayOnlyBackend` and `RecordingBackend` return
  `Completion(text=...)` with no `raw` (`cassettes.py:356-359`), so a replayed
  turn carries no `done_reason`. The runner's account words for the stop
  come from `raw` and so appear on a live turn only, the same as the
  `length` cut today (observed: `cassettes.py`).

## 4. The seam

Site: `rota/llm/llm.py:278-346`, `_consume_stream`, beside the cycling
check. The regex moves to `rota/llm/toolproto.py` beside `MARKER`, because
`runner.py` imports `llm.py` and `llm.py` cannot import the runner
(reasoned: the import order). `runner.py:655` keeps the name,
`FABRICATED_RESULT = toolproto.INVENTED_RESULT`, so `nightcount.py:71`
holds.

State: one flag, `saw_tool`, and no parser state.

1. After `line_buf += piece` and the split loop, set `saw_tool` when a
   completed line holds `MARKER`.
2. Test each completed line, then the remaining `line_buf`, against the
   anchored regex (no `re.MULTILINE`, `.match` on the line), only when
   `saw_tool` was set by an earlier line.
3. On a match: set `stopped = "invented"`, write the note to the live view,
   and `break`, as the cycling stop does.
4. At the end: `final["done_reason"] = "invented_result"` for this stop,
   `"repeating"` for the cycling one.

The note to the live view, in the shape of the two that exist:
`"\n[stopped: the reply wrote a tool result it was not given]\n"`.

The account: keep "wrote its own tool results" as its own line, unchanged,
so the count of 74 sessions stays comparable. When `raw["done_reason"] ==
"invented_result"`, the runner adds one more line beside it, at
`runner.py:3830`:

`the stream stopped at the invented result "OK code.source ->" on line 3 of the reply, so nothing after it was generated`

The quoted head and the line number come from the match on `scanned`
(reasoned: "where the stream stopped and why", the brief's question 4). The
seat's feedback is unchanged, because it already says the lines did not
come from the runner.

## 5. The savings, from night 145

| measure | complete-line rule | head rule (chosen) | the frame's target |
|---|---|---|---|
| live walk turns shortened | 122 | 140 | |
| tokens after the stop | 136.1k | 158.0k | 179k counted |
| card minutes, pro rata by tokens kept | 33.1 | 39.0 | |
| the 78: tokens after the stop | | 104.1k in 20 turns | |
| turns over 60 s shortened under 60 s | 11 | 12 | |
| turns over 60 s that remain | 24 | 23 | under 10 |

Observed: `night.py`, `residual.py`. The minutes are a pro-rata estimate,
`ms` times the share of characters cut (reasoned: generation dominates a
long turn, section 1.1 of the investigation).

Against the ends-when:

- Fabricated tokens: on the kept text, the investigation's own measure
  `^(OK|ERROR|NOTE) ` after `TOOL:` still finds 20.9k, against "under 20k".
  20.2k of that is the `ERROR <fn>(<args>): ...` shape, which the runner's
  regex does not match. 8 turns carry it with no runner match at all
  (observed: `residual.py`, `night.py`). By the
  runner's own regex the remainder is 0.6k, the kept heads.
- Turns over 60 seconds: of the 35, 12 end on an invented result and fall
  under 60 seconds. 18 have no `TOOL:` line, 4 are clean acts and 1 is a
  cycling reply, and the stop leaves all 23 (observed: `residual.py`). The
  "under 10" was option J's measure in the investigation, section 3, not
  option I's.

Proposed ends-when line for the holding session (reasoned: the counts
above): fabricated tokens by the runner's regex after a `TOOL:` line, 158k
on night 145 to under 20k; turns over 60 seconds that end on an invented
result, 12 to under 2. A widened regex for the `ERROR <fn>(<args>):` shape
changes the runner's rule 1 and its account count, so it is a separate
frame and not this pass (reasoned: the runner drops calls after any match).

## 6. The tests

Tests that cover `_consume_stream` today (observed: grep, 2026-10-13):

- `tests/rota/test_llm_stream.py`: `test_a_stream_within_its_deadline_is_joined`,
  `test_a_stream_past_its_deadline_is_a_timeout`,
  `test_a_cycle_of_lines_three_times_over_is_repeating`.
- `tests/rota/test_runner.py:1582`
  `test_the_streamed_chunks_join_into_the_old_body_and_feed_the_live_view`,
  and `:1640` `test_a_stream_that_repeats_the_same_line_three_times_is_stopped_there`.
- The runner's side of the sign: `test_runner.py:373, 390, 515, 537, 580`.

The three red-first tests, in `tests/rota/test_llm_stream.py`, on chunks in
the shape of `_chunks`, with a `pulled` list as in the cycling test:

1. A `TOOL: code.source("a.py", 0, 40)` line, a blank line, then
   `OK code.source -> [` and 200 more chunks of one unended line: the stream
   stops on the chunk that completes `->`, `done_reason` is
   `"invented_result"`, the content keeps the `TOOL:` line and the
   `OK code.source ->` head, and fewer than 10 chunks are pulled. The shape is
   s117#4.
2. A clean act body: `OK, the tests pass.` and `OK code.write -> done` lines
   with no `TOOL:` line before them, then 20 more lines and `done`: the
   stream runs to its end, and `done_reason` is not `"invented_result"`.
3. `TOOL: code.source(...)`, then `TOOL: code.probe(...)`, then
   `TOOL: tests.run(...)`, no result line, then `done`: the stream runs to its
   end with all three lines.

A fourth test for the runner, in `tests/rota/test_runner.py`: a scripted
completion with `raw={"done_reason": "invented_result"}` and a kept head
gives both account lines, and the call before the head runs.

## 7. The risk: long completions the stop does not shorten

Group 2, the prose runaways: 19 of the 78, 162k tokens, 32.6 minutes, each
18 of them 7,731 to 10,203 tokens, at or near the output cap, and s145#10
at 3,512 (observed: the table). 12 of the 19 are a session's first turn,
and 9 are Tester turns.
A cap or a stop on prose with no call stops them, which is option J or a
later frame, and not this one (reasoned: the rule needs a `TOOL:` line).

## 8. The pass brief, ten lines

1. Files: `rota/llm/toolproto.py` (`INVENTED_RESULT` beside `MARKER`), `rota/llm/llm.py` (`_consume_stream`), `rota/core/runner.py` (`:655` alias, `:3830` account), `tests/rota/test_llm_stream.py`, `tests/rota/test_runner.py`.
2. Rule: once a completed line holds `TOOL:`, the first line head that matches `INVENTED_RESULT` ends the stream. The head can be a partial line.
3. Keep the text up to and including the chunk that completed the match. Set `done_reason = "invented_result"`. Never `"length"`.
4. Live note: `[stopped: the reply wrote a tool result it was not given]`.
5. No quote or paren guard: 0 of 177 cases need one (`probe3.py`).
6. Runner: keep "wrote its own tool results" unchanged. On `done_reason == "invented_result"` add the line `the stream stopped at the invented result "<head>" on line <n> of the reply, so nothing after it was generated`.
7. Test 1, red first: `TOOL:` line, then an unended `OK code.source -> [...` line, stops under 10 chunks and keeps the head.
8. Test 2, red first: `OK`-like lines with no `TOOL:` line before them run to the end.
9. Test 3, red first: three `TOOL:` lines and no result run to the end. Then a runner test for the two account lines.
10. Prove on the register: `parse_equiv.py` in `scratchpad/f232/` must print 0 shortened that the runner does not flag, and run calls identical except the 1 known `l_3aea8c134c` case.

## 9. Register lines

None written (this read edits no tracked file but this report). One
candidate for `plans/operating-facts.md`, the sqlite section: sign
"1896 live walk turns" for night 145, cause: `immutable=1` skips the
`-wal` file, so read a checkpointed copy.
