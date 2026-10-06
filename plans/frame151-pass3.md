# Frame 151, pass 3: the three findings of the review of 9cb2bcbc

This record is about the rota workflow: the parser that reads a seat's tool calls. The implementer of passes 2 and 3 wrote it on 2026-10-06. The probes are in the session scratchpad, `p2/`, beside the review's `review151b/`. P0 is 75918de, P1 is d446483, P2 is 9cb2bcbc.

## What changed

- `rota/llm/toolproto.py`: the guard of pass 2, which counted triple quotes, is gone. `_refuse_joined_strings` now refuses a strict read when the escaped text holds two string literals side by side, and Python refuses the list as written. `_adjacent_strings` reads the tokens with `tokenize`. The guard raises `JoinedStrings`, a subclass of `ValueError`.
- `rota/llm/toolproto.py`, `_rescan_args`: when the guard refuses the rescan's candidate, the refusal goes into a list that `extract` passes.
- `rota/llm/toolproto.py`, `extract`: when the rescan's candidate was refused by the guard, the seat reads the guard's reason. Before, the seat read the hint that a value never ends.
- `tests/rota/test_toolproto_triple.py`: the stray-quote test runs over both kinds and checks the reason that `extract_lenient` sends. The six shapes of finding 1 are a parametrised test. Two new tests hold the raw test and the lenient path.
- `tests/rota/fixtures/toolproto_fuzz_slice.json`: recorded again, because 42 cases moved.

## Finding 1: the count refused six right reads

The six shapes of the review now read as P1 reads them (observed: `p2/six.py`, 2026-10-06). Each is a test:

- `a="x ''' y` LF `z"`
- `a='x """ y` LF `z'`
- `result=pass, note="x ''' y"`
- `a="x ''' y` CRLF `z"`
- `a='''x """ y''', b='p` LF `q'`
- `a='''x """ y''', result=pass`

The pass-2 input is still refused, for both kinds of triple quote. Without the guard, both read a call with `, c=` inside `a` (observed: `p2/p6_pass3.py`, mutant G1, 2026-10-06).

On the 120,000 inputs of `p2/variants.py` (observed: `p2/f3_fuzz.py`, 2026-10-06):

| parser | equal to Python | right reads lost | calls on text that Python refuses | values that swallow `c=s` |
|---|---|---|---|---|
| P1 | 51,743 | - | 23,156 | 1,543 |
| P2 | 51,915 | - | 16,550 | 656 |
| pass 3 | 51,915 | 0 against P1, 0 against P2 | 18,551 | 0 |

On real text, pass 3 reads every turn as P1 and P2 read it. Nights 113 to 125: 14,124 turns and 41,026 calls, 0 turns differ, and the guard fires on 0 lists. Cassettes: 26,677 completions and 48,288 calls, 0 differ, and the guard fires on 0 lists (observed: `p2/p3_corpus.py`, 2026-10-06).

The fuzz slice moved 42 cases against the fixture of 9cb2bcbc. No right read is lost, and no read is gained (observed: `p2/slice3.py`, 2026-10-06).

- Wrong to refused, 30 cases:
  - code-1-1500-plain #74, #156, #257, #285, #338, #385, #430, #484, #488, #517, #571, #789, #873, #1036, #1059, #1071, #1077, #1203, #1252, #1305
  - code-1-2500-wide #17, #335, #371, #725, #1222, #1435, #1697, #2295, #2319, #2416
- Refused to refused with the guard's new reason, 12 cases:
  - code-1-1500-plain #440, #518, #1421, #1435
  - code-1-2500-wide #424, #525, #884, #1580, #2013, #2114, #2231, #2347

## Finding 2: no test held an unpaired `"""`

The stray-quote test now runs for `'''` and for `"""`. The named case for the lenient path is the slice's prose-2-1000-plain #522, `message='order(I'm can't,' ': that 'yes', it a.'`. A guard before the lenient fall refuses it, because its escaped text holds two string literals side by side.

The review's mutant M2 counted `'''` only. That code is gone, so the mutants of this pass test the new lines. A further test holds the raw test: `a='code.surface(hint='')'` reads as Python reads it, the shape of the four cassette calls of `criteria.specify` that the review found.

## Finding 3: the seat never read the guard's reason

The review placed the loss at `first_exc` in `extract`. The trace shows a different place. The first scan does not close the list, so `_rescan_args` runs first. It calls `parse_args` on its candidate, catches the guard's error, and returns None. `extract` then builds the `_open_argument` hint (observed: `p2/dbg3.py`, 2026-10-06).

So `_rescan_args` now puts a `JoinedStrings` refusal into a list, and `extract` sends that reason. The seat now reads "could not parse arguments: a quote inside a value closed it early, and the text after that quote was read as a second string. Remove the extra quote. Open and close each value with the same three quotes". The test checks the sentence through `extract_lenient`, for both kinds.

## Mutants

`p2/p6_pass3.py` runs the two touched test files in one process, with functions swapped into the live module (observed: `p2/p6_out.txt`, 2026-10-06).

- The worktree: 33 passed.
- The functions of 75918de: 22 failed. Of d446483: 20 failed. Of 9cb2bcbc: 9 failed, the six shapes, the two stray-quote tests and the slice.
- 15 mutants of the lines of passes 2 and 3: all 15 die. G5, the guard with no raw test, dies by the new named test and the slice test.

## The tests

The 7 test files that import `toolproto`: 514 passed, 7 xfailed (observed: 2026-10-06).

## Deviations

- Finding 3's repair is in `_rescan_args` and in the branch of `extract` with no list end, not at `first_exc`. The trace shows that the guard's error never reaches `first_exc` on the review's input.
- The guard raises its own class, `JoinedStrings`, so `_rescan_args` can tell its refusal from the others.
- The mutant script is new, `p2/p6_pass3.py`. The review's `p6_tests.py` mutates the lines of the count, which this pass removed.

## Seen and not fixed

- The review's fact for a new frame stands. Five real lists hold two literals side by side that Python joins, and the read drops a quote. The raw test keeps them, so the guard does not reach them.
- `_quote_bare_keywords` still counts each quote alone, as pass 1 recorded.

## The gate

The gate ran once in the worktree, with the code and the tests of this pass in the tree (observed: ended 2026-10-06 14:01).

```
suite: 23 failed, 2855 passed, 30 skipped, 8 xfailed, 16 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 881.0s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The gate also printed "note: the tree moved past the baseline (658abb6 -> ed88acc)", and "exit 1: 3 new reds, 0 of them flaky".

The 3 new reds and the 3 reds gone are the same as at the gates of passes 1 and 2. Pass 3 reads every cassette call as P1 and P2 read it, so the parser does not move them (observed: `p2/p3_corpus.py`, 2026-10-06). The summary line holds `failed`. The brief asks for the commits, so this pass committed.
