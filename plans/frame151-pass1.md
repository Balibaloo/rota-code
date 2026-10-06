# Frame 151, pass 1: a line break inside a triple-quoted value stays a line break

This record is about the rota workflow: the parser that reads a seat's tool calls. The implementer of pass 1 wrote it on 2026-10-05.

## What changed

- `rota/llm/toolproto.py`, `_escape_newlines_in_quotes`: the scan reads `'''` and `"""` as one token, as `_rescan_args` does. Inside a value, the scan closes only at the delimiter that opened it. A backslash still escapes the next character, as in Python.
- `tests/rota/fixtures/toolproto_fuzz_slice.json`: recorded again with `python -m probes.frame122.fuzz record`.
- `tests/rota/test_toolproto_triple.py`: a new test file. It holds 7 small inputs, a value that opens with four quotes, a call written one argument per line, the 8 night cuts, and a check of the night fixture.
- `tests/rota/fixtures/toolproto_triple_nights.json`: a new fixture. It holds the smallest faithful cut of each of the 12 night calls, as 8 cuts. Some calls repeat one text.

A cut keeps the call's head and tail as the seat wrote them. It keeps the first lines of the value, up to the first line at which Python parses the cut and the old parser reads it otherwise. The fixture's `args` are Python's read of the cut. The test reads each cut through `extract_lenient` with the registry's signatures, which is the runner's path.

## Ends-when 1: the scan

The scan treats a triple quote as one token (observed: the diff of `_escape_newlines_in_quotes`, 2026-10-05).

## Ends-when 2: the fuzz slice

The 82 triple cases read right. The triple slice went from 515 right to 597 right. The 3 cases that stay not right did not move (observed: `f151_moved.py` against the fixture, 2026-10-05).

90 cases of the fixture moved: 82 in the triple slice and 8 in the code-wide slice. No case is lost. The other six slices did not move.

The 8 code-wide cases each hold a `'''` token in the source, from the atoms `''` and `'`. So the scan now reads each one as a triple-quoted value. Python parses 6 of the 8, and the new read equals Python's read in each of the 6. For #1290, Python's read is the read of the first call. Python refuses #84 and #2416. In those 2, the new read keeps the line breaks that the old read joined (corrected in pass 2: observed, the review's `p2_fuzz.py` run again, 2026-10-06).

| case | before | after |
|---|---|---|
| code-1-2500-wide #4 | refused | read as Python reads it, still not the case's want |
| code-1-2500-wide #84 | wrong, a line break as a space | right |
| code-1-2500-wide #97 | wrong, two line breaks as spaces | equal to Python's read, still not the case's want |
| code-1-2500-wide #882 | wrong, a line break as a space | equal to Python's read, still not the case's want |
| code-1-2500-wide #1290 | wrong, a line break as a space | equal to Python's read, still not the case's want |
| code-1-2500-wide #1302 | wrong, a line break as a space | equal to Python's read, still not the case's want |
| code-1-2500-wide #1319 | wrong, a line break as a space | equal to Python's read, still not the case's want |
| code-1-2500-wide #2416 | wrong, a line break as a space in a single-quoted value after a triple token | the line break kept, still not the case's want |

The case's want is the fuzz generator's intent. In these 7 the source does not hold that intent, because the random atoms formed a triple quote.

## Ends-when 3: the night calls

On nights 113 to 124, the old parser and the repaired one read 12 of 1,719 `code.write` and `tests.encode` calls differently. In each of the 12, the two values differ only where the new value holds a line break and the old value holds a space. The other arguments are the same (observed: `f151_check2.py`, 2026-10-05).

Over every op, the count is the same 12. Nights 113 to 125 hold 41,026 calls, and 12 read differently. The cassette table holds 48,288 calls, and 0 read differently (observed: the review of e78545a, `p1_nights.py` and `p1_cassettes.py`, 2026-10-06; added in pass 2).

| night | session | seq | op | line breaks restored |
|---|---|---|---|---|
| 115 | s131 | 7 | tests.encode | 9 |
| 117 | s150 | 11 | code.write | 189 |
| 117 | s150 | 12 | code.write | 189 |
| 117 | s150 | 15 | code.write | 92 |
| 117 | s150 | 17 | code.write | 92 |
| 117 | s150 | 18 | code.write | 92 |
| 117 | s150 | 19 | code.write | 92 |
| 118 | s130 | 1 | tests.encode | 2 |
| 118 | s130 | 2 | tests.encode | 2 |
| 120 | s178 | 13 | code.write | 49 |
| 120 | s230 | 13 | code.write | 18 |
| 120 | s230 | 17 | code.write | 18 |

10 of the 12 new reads equal Python's read of the call. Night 117 s150 seq 11 and seq 12 do not, for a second fault: see "Seen and not fixed". The brief counted 11 clean calls. This pass counts 10 that equal Python, and 12 that keep every line break.

The test holds all 12 calls through the 8 cuts. The s150 seq 11 cut stops before the `pass` line, so Python's read is the oracle for every cut.

## Ends-when 4: each new test goes red without the repair

With the parser of HEAD, 18 tests failed and 2 passed (observed: `pytest tests/rota/test_toolproto_triple.py tests/rota/test_toolproto_fuzz.py -rA`, 2026-10-05).

- All 17 tests of the new file that read a call failed: 7 small inputs, the four-quote opening, the call written one argument per line, and the 8 night cuts.
- `test_the_parser_keeps_its_reads_on_the_fuzz_slice` failed.
- `test_the_fixture_holds_the_twelve_night_calls` passed. It checks the fixture's shape and reads no call.
- `test_the_slice_holds_frame_122s_prose_with_apostrophes` passed. It is frame 144's test, and this pass did not change it.

With the repair, the two files pass: 20 passed.

## Ends-when 5: what the doors answered

The door's answer is the result line in the next turn's prompt (observed: `turns.user` of the next seq, 2026-10-05). The last column says whether the answer came from the join. The read parsed the old value and the new value with `ast` (observed: `f151_parse.py`, 2026-10-05).

- Night 115 s131 seq 7, `tests.encode`: "the body is not Python (unexpected character after line continuation character, line 1)". Not from the join. The new value also fails at line 1. The seat opened the body with four quotes, so the value starts with a stray quote.
- Night 117 s150 seq 11, `code.write`: "src/click/utils.py is not valid Python (unterminated string literal (detected at line 112)". Not from the join. The new value fails at the same line.
- Night 117 s150 seq 12, `code.write`: the same refusal at line 112, after a call that the seat followed with results it wrote itself. Not from the join.
- Night 117 s150 seq 15, `code.write`: "not valid Python (unterminated string literal (detected at line 113)". Not from the join. The new value fails at the same line.
- Night 117 s150 seq 17, `code.write`: the same refusal at line 113. Not from the join.
- Night 117 s150 seq 18, `code.write`: the same refusal at line 113, and "NOTE code.write has been refused the same way in three turns and will not be accepted again". Not from the join.
- Night 117 s150 seq 19, `code.write`: no door answered. The runner ended the session: "repeated its previous turn verbatim twice; ended".
- Night 118 s130 seq 1, `tests.encode` of `tst_echo_json_compact_3`: "the body is not Python (expected an indented block after 'except' statement on line 15, line 16)". **From the join.** The new value parses.
- Night 118 s130 seq 2, `tests.encode` of `tst_echo_json_compact_3`: the same refusal. **From the join.** The new value parses.
- Night 120 s178 seq 13, `code.write`: "tests/test_defaults.py is not valid Python (unterminated f-string literal (detected at line 259)". Not from the join. The new value fails at line 299, where the seat broke an f-string across two lines.
- Night 120 s230 seq 13, `code.write`: "this write changes pass_obj, make_pass_decorator, ... and no criterion of this batch names them". A scope door, not from the join. The joined value parses, so without that door a file with 18 joined lines would have landed.
- Night 120 s230 seq 17, `code.write`: no door answered. The call came after a `code.source` result that the seat wrote itself, so the runner held it: "The real results of the calls that did run follow. Send the rest again with those results in view."

So the join cost two refused test bodies on night 118. No joined value was written to the tree in these 12 calls.

## Deviations

- The fixture moved 90 cases, not 82. The 8 extra cases are in the code-wide slice, and each holds a `'''` token in its source. The brief says to stop when a case outside the triple-quoted values moves. This pass judged these 8 cases inside that scope, because each one moves at a triple token and no line break outside a value moves. The reviewer must confirm that judgement.
- The brief counted 11 clean night calls. The test holds all 12, because each keeps every line break. The s150 seq 11 and 12 cut stops before the second fault.
- The first draft of the small-input test held 8 control cases, a lone quote of the other character or an escaped quote. They passed without the repair, so ends-when 4 removed them.
- The gate ran past the 600-second limit of a foreground command, and the harness moved it to the background. This pass waited for it before the commit.
- The gate's summary line holds `failed`. The brief asks for the commits, and each red also fails or passes the same way with the parser of HEAD. So this pass committed.

## Seen and not fixed

- **`_quote_bare_keywords` has the same parity fault.** It counts each quote alone, so after a lone quote in a triple-quoted value it reads `pass` as a bare keyword and writes `'pass'`. Night 117 s150 seq 11 and 12 show it: a `pass` statement in `src/click/utils.py` reads `'pass'` (observed: `f151_check2.py`, 2026-10-05). The value is two characters longer than Python's read. The fault is a wrong write of code that a seat can meet. It is a new frame.
- The docstring of `triple_calls` in `probes/frame122/fuzz.py` says the first scan counts quotes by parity. After this pass, that is true for `_quote_bare_keywords` only. The file is outside the brief.
- `frame144-pass4.md` says the fixture records the 82 cases as they read now. After this pass the fixture records them as right.

## The gate

The gate ran once in the worktree, with the repair and the new tests in the tree (observed: 2026-10-05 22:31).

```
suite: 24 failed, 2841 passed, 30 skipped, 8 xfailed, 31 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (4): tests/rota/test_arc_synthetic.py::test_arc_delivery_loop_slices_batches_and_tests, tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 1183.5s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The gate also printed "note: the tree moved past the baseline (658abb6 -> 75918de)", and it marked `test_arc_delivery_loop_slices_batches_and_tests` as flaky.

None of the movement is from this pass. The 3 new reds that are not flaky also fail with the parser of HEAD. The 3 reds gone also pass with the parser of HEAD (observed: each run by exact id, the repair taken out and put back, 2026-10-05).
