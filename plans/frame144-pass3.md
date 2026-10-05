# Frame 144, pass 3: the delta review's findings, and the parser fuzz in the gate

Meta workflow. Pass 3 of frame 144, the night databases are not a test tier. The implementing agent on Opus wrote this record on 2026-10-05. Part A repairs the findings of the read-only review of 8726a13, two highs and four lows. Part B moves frame 122's fuzz and comparison into `probes/frame122/`, and puts a fixed-seed slice of the fuzz in the gate. The tree is left uncommitted on ba369f4 for the holding session.

## What changed, by file

- `rota/roles/api.py`, +90 -15.
  - `_code_write._whole` catches every `Exception` of `ast.parse`, not only `SyntaxError` (high 1). It is the one change that a seat can meet.
  - `door_of(frames)` is new. `_offer` records the door as a chain of frames, from the statement up to the op (low 4).
  - The span facts of the cut door (three sites) and of the tail statement name their statement by `node` and `name`. The kept spans of the drops door name the definition. The insert point of the unnamed-definition door names `end_of` (high 2).
  - The line facts carry the line's text from the tree or the parser, never from the number: the decorator line (`quote='@dec'`), the docstring line (`docstring=True` and the docstring's first words), and the two parse and compile refusals (`quote=exc.text`) (high 2).
- `rota/core/sandbox.py`, +178 -11.
  - `_raise_site` uses `api.door_of` on the traceback (low 4).
  - `_IMMUTABLE` holds `PurePath` and `sqlite3.Row`. `_deep` copies a leaf of `_LEAVES` as it is at any depth. `_same` compares an object of a type with the default `==` by its attributes (low 5).
  - `_span_as_it_is` and the branch in `follow` send the span of an unsent `code.write` offer with the lines that it holds now (low 6). The record has `span_only`.
  - `_line_holds`, `_stmt_span` and `_span_holds` check a `line` against its quote and a `span` against the tree's span of the statement it names (high 2).
- `tests/rota/conftest.py`, +32. The hook stores its findings on the item. A `pytest_runtest_makereport` wrapper, `tryfirst`, turns an xfailed report red when the hook found a finding that no list names (low 3). Finding 6 is a new line in `KNOWN_REFUSED_OFFERS`.
- `tests/rota/test_offers_followed.py`, +132, 8 tests: one per item of part A, and a strict xfail for finding 6.
- `probes/frame122/fuzz.py`, new, 270 lines. Frame 122's code fuzz and prose fuzz, draw for draw, the outcome classes, the gate's slice and the `record` command. `--against REV` compares with the parser at a git revision.
- `probes/frame122/compare.py`, new, 91 lines. Frame 122's comparison of two parsers over the completions of a night database or a cassette database.
- `tests/rota/test_toolproto_fuzz.py`, new, 55 lines, 2 tests. `tests/rota/fixtures/toolproto_fuzz_slice.json`, new, the slice's outcomes.

## Part A, the review's points

1. **High 1, done.** A text of 200000 nested minus signs crashed the cut door with `MemoryError` in `_whole`. The parent of c888968 gave the cut refusal. The refusal now has the same bytes as on the parent (observed: the probe on a worktree at 10a50ed and on this tree, 2026-10-05). The probe also sent `(` * 200000 and a null byte, and both gave the same refusal. `test_a_text_that_breaks_the_parser_gets_the_cut_refusal` asserts the bytes and that the offer's text is `INVENT`.
2. **High 2, done.** A span now names its statement, and the check finds a statement of that type and name with that span in the file now. A line carries its text from the tree or the parser, and the check finds that text in the line. `test_the_fact_check_reads_a_span_and_a_line_against_the_tree` holds both checks directly. The 10 false `line_text` facts of the defines-twice door are still the only false facts, and their strict xfail stays. No door's text changed.
3. **Low 3, done.** A strict xfail no longer hides a new finding. `unhide` in `conftest.py` turns the report red. `test_a_new_finding_in_an_xfail_test_turns_its_report_red` holds the function.
4. **Low 4, done.** The door identity is the chain of frames from the statement to the op's function or `_code_write`. The walk stops before a frame of `call`, `dry_run`, `follow` or a file outside `api.py` and `sandbox.py`, so a seat's call and a dry run give the same chain. `test_a_helper_of_two_doors_gives_two_door_identities` holds it with `_end_offer`, which serves the cut door and the cross-block door.
5. **Low 5, done.** `test_a_dry_run_keeps_an_unchanged_object_of_an_unknown_type` and `test_a_dry_run_restores_a_path_a_row_and_the_working_set` hold the three repairs and frame 132's `ctx.working_set`. A top-level attribute of an unknown mutable type still raises `TypeError`, by pass 2's rule.
6. **Low 6, done.** An unsent `code.write` offer with a span goes to the doors with the lines that the span holds now. A door that judges the span alone reads it. The text is the seat's, so the check says nothing about the text. `test_an_unsent_offer_sends_its_span_with_the_lines_it_holds` holds it, and one line more is refused.

## The proofs by removal

Each mutant was a one-line edit by a byte script, run, then reverted. `git diff` shows none of them (observed: the reverts, 2026-10-05).

1. **The span check.** The cut door's span fact `(lo, hi)` became `(lo, hi - 1)`. On `test_offers_followed.py` and `test_desk_guards.py`, 25 tests went red, 23 by the fact check, for example `test_a_span_that_cuts_a_statement_is_told_where_the_boundaries_are`: "fact span (0, 3) {'name': 'a', 'node': 'FunctionDef', ...}: the statement named has the spans [(0, 4)]". The bounds-only check of pass 2 keeps this mutant green.
2. **The line check.** The parse refusal's line fact `(exc.lineno or 1) - 1` became `(exc.lineno or 1)`, which counts from 1. 4 tests went red by the fact check, for example `test_an_indented_span_that_does_not_parse_is_told_its_own_line`: "fact line 5 {'quote': '    z = ('}: the line is 'return out', not 'z = ('".
3. **The span of an unsent offer.** `_end_offer`'s "To stop where the {block} of {X} ends" sent `end=x + 1` and kept its text. 4 tests went red by the follow check, for example `test_a_moved_end_in_a_try_body_stops_before_the_finally_header`: "second refusal: ValueError: start=2, end=4 crosses from one block to another".
4. **A new finding in a strict xfail.** The line of `test_the_add_after_offer_of_a_cut_span_is_admitted` in `KNOWN_REFUSED_OFFERS` was removed. The test went from xfailed to failed: "the follow check found, in a test marked xfail". The same proof shows in the span mutant above, which turned that xfail test red.
5. **The identity of an object of an unknown type.** The branch `if type(a).__eq__ is object.__eq__:` became `if False:`. `test_a_dry_run_keeps_an_unchanged_object_of_an_unknown_type` went red.

## Part B, the parser fuzz

Frame 122's instruments were in the scratch area of session 419281dc: `review122b/fuzz.py`, `review122c/fuzz.py`, `fuzzc.py`, `prose.py` and `p4b.py` (copied: `plans/operating-facts.md`, the line on `rota/llm/toolproto.py`). The probes read a copy of the old parser, `toolproto_old.py`, and a checkout at `C:/Users/roman/rota_review122`. The new probes read the old parser from git at a revision, and the current one from this checkout.

- `probes/frame122/fuzz.py code|prose` runs the fuzz. It draws in the same order as frame 122's scripts, so a seed gives the same sources.
- `probes/frame122/compare.py --against REV DB...` reads every completion of a night database or a cassette database with both parsers. On night 118 against fb1bdba^: 1044 completions, 2836 old calls, 3 errors to calls, 0 read differently (observed: 2026-10-05).

**The oracle.** Each case knows the arguments that it wrote. A case is `right` when the parser reads exactly them, `wrong` when it reads a call with other arguments, and `refused` otherwise. The fuzz's sources are often ambiguous: Python itself reads `' ''s'` as two joined strings. So the current parser reads many cases wrong by this oracle: 12482 of 200000 on the narrow code fuzz, seed 1, and 56060 on the wide one (observed: 2026-10-05). Frame 122 counted only the cases that the change moved. The transitions from fb1bdba^ to the current parser, 20000 cases each (observed: 2026-10-05):

| Fuzz | right to right | refused to right | refused to wrong | wrong to wrong | refused to refused |
|---|---|---|---|---|---|
| code, narrow | 6508 | 0 | 0 | 1606 | 11886 |
| code, wide | 1703 | 19 | 2 | 7587 | 10689 |
| prose, inject | 1376 | 1725 | 40 | 574 | 16285 |

No case went from right to anything else.

**The slice in the gate.** `test_the_parser_keeps_its_reads_on_the_fuzz_slice` runs four slices, 7500 cases: code narrow seed 1 (1500), code wide seed 1 (2500), prose inject seed 1 (2500), prose plain seed 2 (1000). It takes about one second, with no model. The fixture holds the indices of the right and the wrong cases. A right case must stay right, and a case may read wrong only when the fixture names it. A refused case may become right. A crash of the parser fails the test. `python -m probes.frame122.fuzz record` writes the fixture again and prints the gained and lost counts. `test_the_slice_holds_frame_122s_prose_with_apostrophes` checks that a right prose case holds an apostrophe.

**The proof by removal.** fb1bdba's third reading in `toolproto.extract`, `third = _third_reading(text, args_start)`, became `third = None`. Both tests of `test_toolproto_fuzz.py` went red: "350 cases no longer read right, 0 cases read wrong", the first `code-1-2500-wide #669 "TOOL: rulings.rule(words='=#\")s'don')" -> []` (observed: 2026-10-05). The restore left `toolproto.py` with no diff.

## The counts over one gate run

`ROTA_OFFER_LOG` on the second gate of this pass, on the final tree (observed: 2026-10-05). The first gate gave the same counts.

- 268 facts in 86 tests: `line_text` 130 (10 false), `span` 51, `test_path` 37, `row` 19, `line` 16, `lines` 13, `file` 2. Every `span` and every `line` now passes the tree check. The 10 false facts are the defines-twice door's, in the five known tests.
- 269 offers in 116 tests. 161 sent, 12 refused, all 12 known. 108 not sent because the text is the seat's, and all 108 had their span sent, with 0 refused. 14 `AGAIN` steps met another door. 0 fragments were missing and 0 arguments were unknown.
- 1 crash record, finding 6 below.

## The suite

The touched files pass: `test_offers_followed.py`, `test_desk_guards.py`, `test_t0_sandbox.py`, `test_night46_context.py`, `test_toolproto_fuzz.py`, `test_toolproto_quotes.py` and `test_touch_divergence.py`, 459 passed and 7 xfailed. Then `test_viewer.py` with the fix of `door_of` (observed: 2026-10-05).

The gate on the final tree, uncommitted on ba369f4 (observed: `python -m rota.tools.gate`, 2026-10-05):

```
suite: 23 failed, 2771 passed, 27 skipped, 8 xfailed, 16 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 766.2s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The xfailed count went from 7 to 8. The added xfail is finding 6.

## The known findings after this pass

Findings 1 to 5 are pass 2's, unchanged. One is new.

6. **New in pass 3.** `code.write` at an insert: a text that `ast.parse` cannot hold raises `MemoryError` from `_future_door`, and the session crashes where a refusal belongs. The cut door's "To add after it" offer of such a text meets it in `test_a_text_that_breaks_the_parser_gets_the_cut_refusal`. `test_an_insert_of_a_text_that_breaks_the_parser_is_refused` holds it as a strict xfail. The door is older than c888968: the parent crashes on the same insert (reasoned: `_future_door` catches `SyntaxError` only on both trees).

## Deviations

- The gate ran twice. The first run found a red of this pass, `test_viewer.py::test_no_module_computes_its_own_location`: `door_of` read `__file__`, and only `rota/paths.py` may do so. `door_of` now reads `rota.paths.PACKAGE`.
- Item 2's span check covers the spans that name a statement. A span fact with no `node`, `name` or `end_of` keeps the bounds check. After this pass every span site names one.
- Item 6 checks the span of an unsent offer through the real doors with the lines the span holds now, not by a structural rule. A door that judges the text can still refuse the seat's own text later.
- Part B's gate slice compares against a recorded fixture, not against an older parser. A comparison with the old parser cannot see a lost fix, because without the fix the two parsers agree.

## Seen and not fixed

- Finding 6: `_future_door` and `_parse_compile` in `_code_write` catch `SyntaxError` only, so the text of high 1 still crashes an insert and a merged parse. It is the same class as high 1 and a seat meets it. The brief keeps this pass's seat-facing change to `_whole`.
- The fuzz oracle cannot tell a wrong read from an ambiguous source. The slice holds 1139 wrong cases as recorded, and the fixture is the judge. A fixture written after a parser change must be read by its gained and lost counts.
- `compare.py` reads the cassette table by its schema in `rota/llm/cassettes.py`. It was run on night 118 only, not on a cassette database.
- The gate's three known new reds are frame 148's (copied: the brief).
