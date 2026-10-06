# Frame 151, pass 2: the four findings of the review of e78545a

This record is about the rota workflow: the parser that reads a seat's tool calls. The implementer of pass 2 wrote it on 2026-10-06. The probes are in the session scratchpad, `p2/` beside the review's `review151/`.

## What changed

- `rota/llm/toolproto.py`, `_rescan_args`: a backslash escapes the next character in a triple-quoted value too. Before, the scan skipped an escape only in a one-character quote.
- `rota/llm/toolproto.py`, `parse_args` and the new `_refuse_an_unpaired_triple_quote`: after a strict parse succeeds, the parser refuses the list when the escaped text holds an odd count of `'''` or `"""`, and Python refuses the list as written.
- `tests/rota/test_toolproto_triple.py`: 6 new tests, and the test of a line break between arguments now reads the escape's output.
- `tests/rota/fixtures/toolproto_fuzz_slice.json`: recorded again, because 11 cases moved from a wrong read to a refusal.
- `plans/frame151-pass1.md`: the table and the night count are corrected (finding 4).

## Finding 1: a stray triple quote read as a call with a wrong value

The input `TOOL: t.f(a='''it's'''` LF `''', c='''r's` LF `t''')` is now refused (observed: `test_a_stray_triple_quote_after_a_closed_value_is_refused`, 2026-10-06).

The review named the wrong path. The input never reaches the lenient read. The escaped text is `a='''it's''' ''', c='''r's\nt'''`, and Python parses it. The stray `'''` opens a string that holds `, c=`. Then `r's\nt'` is a raw string, and `''` is an empty string. Implicit concatenation joins all four to `a` (observed: `ast.dump` of the escaped text, 2026-10-06).

So the brief's fix, a guard before the lenient fall, does not refuse the input. This pass measured five places for the guard on the fuzz slice and on 120,000 inputs of the review's fuzz, seeds 151 and 152 (observed: `p2/variants.py`, 2026-10-06).

| guard | the input | slice: right reads lost | slice: cases moved | fuzz: right reads lost | fuzz: values that swallow `c=` |
|---|---|---|---|---|---|
| none (pass 1 with finding 2) | a call | 0 | 0 | 0 | 1,543 |
| the brief: odd count, before the lenient fall | a call | 47 | 284 | 0 | 1,555 |
| odd count, before the lenient fall, Python refuses the raw list | a call | 47 | 284 | 0 | 1,555 |
| odd count, after the strict parse, Python refuses the raw list | refused | 0 | 11 | 0 | 656 |
| odd count on both paths | refused | 47 | 295 | 0 | 660 |

This pass ships the fourth row. A guard on the lenient path refuses 47 reads that the slice holds as right. An example is code with a `'''` inside a value with single quotes, which the lenient read takes whole. The raw-list test keeps every list that Python reads as written, because a value can hold a triple quote of the other kind (observed: `test_a_triple_quote_inside_a_value_of_the_other_kind_still_reads`, 2026-10-06).

Against the per-input check of the brief: 0 of 120,000 inputs move from a right read to a refusal or a wrong read. The right reads stay 51,915 with the guard and without it (observed: `p2/variants.py`, 2026-10-06).

The 11 slice cases that moved each went from a wrong read to a refusal (observed: `p2/slice_moves.py`, 2026-10-06):

- code-1-1500-plain #440, #518, #1421, #1435
- code-1-2500-wide #424, #525, #1580, #2013, #2114, #2231, #2347

The real text did not move. Pass 2 reads each of the 41,026 calls of nights 113 to 125 and each of the 48,288 cassette calls as pass 1 reads it (observed: `p2/p2_corpus.py`, 2026-10-06).

## Finding 2: the second scan ignored a backslash in a triple value

Line 143 of `_rescan_args` no longer holds `and len(quote) == 1`. The new test reads `ledger.log(note='''can't \''' x''')` as Python does (observed: the test red with the old line and green with the new one, 2026-10-06).

`p4_agree.py` with its tracer updated to the new line: the newline escape and `_rescan_args` disagree on 0 of 60,148 inputs with a line break. Before, they disagreed on 245 of 61,403. Without backslashes, they disagree on 0 of 62,793, as before (observed: `p2/p4_post.txt`, 2026-10-06). The count of inputs changes, because the rescan now finds an end for different inputs.

No fuzz slice case moved for this change alone (observed: `p2/slice_moves.py`, 2026-10-06). So this change stays.

## Finding 3: the tests could not see three mutants

The test of a line break between arguments now asserts on the output of `_escape_newlines_in_quotes`. A new test holds a CRLF and a lone CR. A new test holds an escaped quote inside a triple value.

`p5_mutants.py`: all 11 mutants die, and the parent's function fails 20 of 25 tests (observed: `p2/p5_post.txt`, 2026-10-06). M7, no CR normalisation, dies by the CR test. M8, the escape ignored inside a value, dies by the escaped-quote test. M10, a line break outside a value stays a line break, dies by 2 tests.

## Finding 4: the record

`plans/frame151-pass1.md` now says that #1302 equals Python's read, and that Python parses 6 of the 8 code-wide cases, not 5. It also names the count over every op: 12 of 41,026 calls of nights 113 to 125, and 0 of 48,288 cassette calls (observed by the review of e78545a, 2026-10-06, and run again for #1302 by this pass).

## Each new test goes red without its repair

- Without the guard: `test_a_stray_triple_quote_after_a_closed_value_is_refused` and the fuzz slice test fail (observed: 2026-10-06).
- With the old line 143: `test_the_second_scan_honours_a_backslash_in_a_triple_quoted_value` fails (observed: 2026-10-06).
- With the parent's escape: 20 of 25 tests fail, as above.
- `test_a_triple_quote_inside_a_value_of_the_other_kind_still_reads` is a control. It passes without the guard, and it fails when the guard drops the raw-list test.

## The tests

The 7 test files that import `toolproto`: 506 passed, 7 xfailed (observed: 2026-10-06).

## Seen and not fixed

- **An even count of triple quotes can still join a stray quote to the next value.** The guard counts quotes, so two stray tokens pass it. With the guard, 656 of 120,000 fuzz inputs still read a value that swallows `, c=`. A guard that refuses two adjacent string literals in the strict read, when Python refuses the raw list, cuts that count to 0. It loses 0 right reads of the slice and of the fuzz, and it moves 42 slice cases (observed: `p2/variants.py`, 2026-10-06). That rule is wider than the brief, so this pass did not ship it.
- `_quote_bare_keywords` still counts each quote alone, as pass 1 recorded.

## Deviations

- The guard sits after the strict parse and not before the lenient fall. The brief's place does not refuse the input, and it loses 47 right reads of the slice.
- The guard also asks whether Python refuses the raw list. Without that test, a list that Python reads, such as a value with a triple quote of the other kind, is refused.
- The pass corrected `plans/frame151-pass1.md` in place, in the record commit.

## The gate

The gate ran once in the worktree, with the code and the tests of this pass in the tree (observed: ended 2026-10-06 13:14).

```
suite: 23 failed, 2847 passed, 30 skipped, 8 xfailed, 16 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 956.0s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The gate also printed "note: the tree moved past the baseline (658abb6 -> d446483)", and "exit 1: 3 new reds, 0 of them flaky".

The 3 new reds and the 3 reds gone are the same as at pass 1's gate. Pass 1 showed that each one fails or passes the same way with the parser of HEAD. Pass 2 reads every cassette call as pass 1 reads it, so the parser does not move them (observed: `p2/p2_corpus.py`, 2026-10-06). The summary line holds `failed`. The brief asks for the commits, so this pass committed.
