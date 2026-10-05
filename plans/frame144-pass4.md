# Frame 144, pass 4: the delta review of fed7c58

Meta workflow. Pass 4 of frame 144, the night databases are not a test tier. The implementing agent on Opus wrote this record on 2026-10-05. It repairs the findings of the read-only review of fed7c58: one high that a seat can meet, and ten lows of the instruments. The reviewer's probes are in the scratch area of session 3f72d9cb, `review144c/`. The tree is left uncommitted on a994576 for the holding session.

## What changed, by file

- `rota/roles/api.py`, +62 -20.
  - The decorator line's quote comes from the decorator's own line, `lines[d0.lineno - 1]`, and not from `ast.unparse` (high 1).
  - `RECORD` is new and is False. `_offer` and `_fact` return at once when it is off (low 2).
  - `Offer` holds the raw `frames`, and its `site` property calls `door_of` (low 2). `door_of` skips the library frames below the first frame of `api.py` or `sandbox.py` (low 5).
  - `_head_of` is new. The four span facts that name a statement carry its first line as `head` (low 10). The tail statement's `holder` keeps its node for that.
  - The docstring's first words stop before an escape, where the value and the source differ.
- `rota/core/sandbox.py`, +97 -22, all below line 2480.
  - `_deep` rebuilds a namedtuple and the attributes of a plain object itself. `_slots` is new, and `_same` reads `__slots__` (low 8).
  - `follow` keeps a crash of one offer's dry run as that offer's record (low 9).
  - `_line_holds` matches the quote at the start of the stripped line, up to a word boundary. A docstring's quote follows the opening quotes (low 4).
  - `_compiled_line` is new. A `line` fact with a `text` is checked by compiling the text (low 3).
  - `_span_holds` compares `head` (low 10).
- `tests/rota/conftest.py`, +38 -14. It sets `api.RECORD`. `KNOWN_FALSE_FACTS` keys on words of the refusal's sentence, and the hook adds the sentence to each fact record (low 11). `unhide` turns a skipped report red too (low 9). Five new lines in `KNOWN_REFUSED_OFFERS` name the findings that the new tests meet: the three decorator cases and the session test meet finding 2's door, and the crash test meets finding 6.
- `tests/rota/test_offers_followed.py`, +163, 12 tests and 3 cases of a parametrized test.
- `probes/frame122/fuzz.py`, +170 -23. Four shape generators. `outcome` gives right or not and a digest. `slice_changes` is new. Four new slices.
- `tests/rota/test_toolproto_fuzz.py` and the fixture: the test reads the digests.

## The repairs

1. **High 1, done.** `p1b_unparse.py` on this tree and on a worktree at b2ed55b gives the same refusal hash for all 12 rows: six decorators, two starts each (observed: 2026-10-05). `test_a_cut_at_deep_decorators_gets_the_refusal_of_b2ed55b` asserts the bytes of b2ed55b for `@dec(` with 400 minus signs, a chain of 2000 attributes, and `@ dec . more(1)`, at start 1 and start 2. The mutant that puts `ast.unparse` back turns all three cases red. The two deep ones crash, and the spaced one reads its line fact false.
2. **Low 2, done.** A session records no offer and no fact. Avoiding the append costs the tests nothing, because the conftest turns `RECORD` on for the test process. A probe outside pytest that needs offers sets `api.RECORD = True`. `test_a_session_records_no_offer_and_a_test_records_frames` holds both halves.
3. **Low 3, done.** `test_the_line_of_a_compile_refusal_is_read_by_compiling_the_text` uses a `__future__` import below a statement, which is a compile-stage error. Line 1 is true, and lines 2 and 0 are false.
4. **Low 4, done.** `test_a_line_quote_starts_the_line_at_a_word_boundary`. The false red of `@ dec . more(1)` is gone with repair 1, and the spaced case of repair 1's test proves it.
5. **Low 5, done.** A surrogate in the text makes `ast.parse` raise `UnicodeEncodeError` in `ast.py`. The identity now starts at `_parse_compile` and ends at `_code_write`. `test_a_refusal_raised_in_a_library_names_its_door`.
6. **Low 6, done.** Right is the exact list of calls and no refusal. The fixture holds a digest of six hex digits for every case. The digest covers each call with its arguments and positions, each refusal sentence, and each start offset. A moved digest is red, unless the case now reads right and did not before. The reviewer's four parsers move 597, 1192, 5054 and 4855 cases (the list below).
7. **Low 7, done.** Four generators: `bare_calls`, `path_calls`, `triple_calls`, which covers both the triple-quoted body and dc34dcd's list of quotes, and `model_calls`. Each removal is in the list below. b79882e's carried write line is in `rota/tools/nightcount.py` and not in the parser, so the test's docstring names it as out of reach.
8. **Low 8, done.** `test_a_dry_run_keeps_slots_and_copies_a_row_inside_a_tuple_or_object`.
9. **Low 9, done.** The crash that drops the other records is confirmed: the known `MemoryError` refusal has two offers, and pass 3's `follow` let the crash out of the loop. The hook then kept one crash record and dropped the other offer's record (observed: pass 3's gate log holds three facts and one crash record for `test_a_text_that_breaks_the_parser_gets_the_cut_refusal`, and no record of its "To replace a whole" offer, 2026-10-05). `test_a_crash_of_one_offer_keeps_the_records_of_the_others` and `test_a_skip_after_a_new_finding_turns_the_report_red`.
10. **Low 10, done.** `test_a_nested_statement_of_the_same_type_does_not_stand_in`.
11. **Low 11, done.** The key is words of the refusal's sentence, " twice (lines ". `test_a_known_false_fact_is_known_by_its_sentence`.

## The proofs by removal

Part A, each a one-line mutant by a byte script, run on `test_offers_followed.py`, then restored (observed: `mutant4.py` in the scratch area, 2026-10-05). Each turned red only the test named.

| Mutant | Red |
|---|---|
| 1, `ast.unparse` head back | the three cases of `test_a_cut_at_deep_decorators_gets_the_refusal_of_b2ed55b` |
| 2, `_offer` records in a session | `test_a_session_records_no_offer_and_a_test_records_frames` |
| 3, no compile check | `test_the_line_of_a_compile_refusal_is_read_by_compiling_the_text` |
| 4, the quote anywhere and no boundary | `test_a_line_quote_starts_the_line_at_a_word_boundary` |
| 5, stop at a library frame | `test_a_refusal_raised_in_a_library_names_its_door` |
| 8a, no namedtuple branch; 8b, no slots; 8c, no object branch | `test_a_dry_run_keeps_slots_and_copies_a_row_inside_a_tuple_or_object` |
| 9a, `unhide` ignores a skip | `test_a_skip_after_a_new_finding_turns_the_report_red` |
| 9b, a crash leaves `follow` | `test_a_crash_of_one_offer_keeps_the_records_of_the_others` |
| 10, no head | `test_a_nested_statement_of_the_same_type_does_not_stand_in` |
| 11, any sentence is known | `test_a_known_false_fact_is_known_by_its_sentence` |

Part B, each removal in `rota/llm/toolproto.py` by bytes, counted by `fuzz.slice_changes`, the function that `test_the_parser_keeps_its_reads_on_the_fuzz_slice` asserts on, then restored (observed: `removals.py` in the scratch area, 2026-10-05):

| Removal | Cases that move |
|---|---|
| fb1bdba, the third reading (`third = None`) | 355: prose 352, code 3 |
| 65ca902, `#` out of the bare-id pattern | 144: bare 143, code 1 |
| 2b07533, the `_bare_path` branch | 400: path 400 |
| cf0aecb, `_namespace_labels` returns the text | 160: model 160 |
| b79882e, a lost call placed at its rewritten offset | 160: model 160 |
| dc34dcd with 3b92f9e, `_rescan_args` returns None | 342: triple 325, code 17 |
| every second call of a reply dropped | 597 |
| each wrong read turned into another wrong read | 1192 |
| every refusal sentence deleted | 5054 |
| every call read twice | 4855 |

`git diff rota/llm/toolproto.py` is empty after the removals.

**The slice.** Eight slices, 9300 cases: code narrow 1500, code wide 2500, prose inject 2500, prose plain 1000, bare 400, path 400, triple 600, model 400. The main test takes 1.14 s (observed: `--durations`, 2026-10-05). The fixture is 67 KB. Right cases: 494, 218, 386, 212, 400, 400, 515, 160.

## Item 1: the statements of passes 2 to 4 that a seat runs

Each statement below was added since c888968 to a function that runs in a session. Each one cannot raise on a seat's text or file, for the reason given. `_fact` and `_offer` now return before any work in a session, but their arguments are still evaluated, so the arguments are listed too.

- `_offer` and `_fact`: `if not RECORD: return`. A module flag read.
- `_offer`, under pytest only: a frame walk and an append. `_fact`, under pytest only: `sorted(where.items())` sorts on unique keys, so it never compares the values.
- `_whole`: `ast.parse` inside `except Exception`, then `getattr`, `len`, `isinstance`. Pass 3's repair.
- The cut door's span facts: `type(x).__name__`, `getattr(x, "name", None)`, and `_head_of`. `_head_of` checks that the line number is an `int` inside the list before it indexes, and `str()` of a line is a str.
- The decorator line: `min(n.decorator_list, key=lambda d: d.lineno)` runs only under `if getattr(n, "decorator_list", None)`, so the list is not empty, and every expression node has `lineno`. The head indexes `lines` only inside its bounds, and the rest are str methods.
- The docstring line: `ns[0].value.value` is a str, because `_docs` admits only such a node. `str`, `split`, `strip`, slicing, `enumerate`, `isprintable` and `next` with a default cannot raise on a str.
- The `line_text` facts of the cut, cross-block and text-line sentences index `lines` and `body` under the bounds checks that the sentences themselves use, from before c888968.
- The two parse and compile line facts: `(exc.lineno or 1) - 1` is the sentence's own expression, and `exc.text` is an attribute that every `SyntaxError` has.
- The tail statement's `holder` tuple now holds its node. Tuple building and unpacking only.
- The defines-twice facts: a str built from `node.name`, which is a str.
- The drops door and the unnamed-definition door: `_send` with numbers the sentences use, and `changed[0] in spans`, a dict test on a str.
- `tests.encode` and `verdicts.emit`: f-strings and `repr` of values that the sentences already format.
- `_admits`: `len(facts)` and `del facts[fmark:]` on a list or under `if facts is not None`.
- `Sandbox.call`: `del offers[:]` and `del facts[:]` under `is not None`. The `_ON_REFUSAL` branch is dead when the hook is None.
- `build`: `ctx.working_set` is frame 132's, not this frame's.

## The counts over one gate run

`ROTA_OFFER_LOG` on the gate of this pass (observed: 2026-10-05).

- 303 facts in 92 tests: `line_text` 149 (10 false), `span` 59, `test_path` 38, `line` 22, `row` 20, `lines` 13, `file` 2. The 10 false facts are the defines-twice door's, in the five known tests. Every `span` passes the head check, and every `line` passes the start-of-line quote and, with a text, the compile check.
- 294 offers in 123 tests. 177 sent, 21 refused. All 21 are known: pass 3's 12 and its crash, 6 of the decorator test's three cases (the add-after offer meets finding 2's door), 1 of the session test (finding 2), and the crash of the new crash test (finding 6). A crash is now an offer's own record, so 0 crash records stand apart.
- 117 not sent because the text is the seat's. All 117 had their span sent, and 0 were refused.
- 14 `AGAIN` steps met another door. 0 fragments were missing and 0 arguments were unknown.

## The suite

The touched and nearby files pass: `test_offers_followed.py`, `test_desk_guards.py`, `test_t0_sandbox.py`, `test_night46_context.py`, `test_toolproto_fuzz.py`, `test_toolproto_quotes.py`, `test_viewer.py`, `test_t0_parser.py` and `test_touch_divergence.py`, 541 passed and 7 xfailed (observed: 2026-10-05).

The gate on the final tree, uncommitted on a994576 (observed: `python -m rota.tools.gate`, 2026-10-05):

```
suite: 23 failed, 2783 passed, 27 skipped, 8 xfailed, 16 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 689.7s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

## Deviations

- Item 6: the fixture holds a digest of every case, not only of the wrong reads and the refusals. One rule then covers the four changed parsers and the six removals, and the only allowed move is a gain to right.
- Item 2: the append is gone in a session too, by the `RECORD` flag, as the brief allowed.
- Item 7's triple shape holds dc34dcd's own form, a list of quotes, inside the same generator, so the shapes are four generators and not five.

## Seen and not fixed

- **The parse sites that catch `SyntaxError` only on a seat's text** (copied: the review of fed7c58, at fed7c58's line numbers). They crash on both trees, and a seat meets each crash. Each one raises `MemoryError` on a text that is too deep for the parser, such as 200000 nested minus signs, and `RecursionError` on some deep but shorter ones.
  - 9732 `_future_door`: an insert, start equal to end, with such a text (observed: `test_an_insert_of_a_text_that_breaks_the_parser_is_refused`, the strict xfail of pass 3).
  - 9907 and 9918 `_parse_compile`: every `.py` write whose merged text holds such a text. A surrogate gives `UnicodeEncodeError`, which is a `ValueError`, so the seat meets a refusal with Python's words and not a crash (observed: `p4b_site.py`, 2026-10-05).
  - 9990 `_code_write`, the fragment's own parse after a parse refusal of a span.
  - 10253 `_code_write`, `ast.parse(tbody)`.
  - 11335 `_def_sources`, 11507 `_span_lost`, 11574 `_span_lost_refusal`, 11609 `_future_order`, 11734 `_parse_view`, 11761 `_repair_broken_strings`, 10664 `params`.
  - 4876 `tests_encode`, `ast.parse(body)` on the seat's test body.
  For the sites after 9918, the text first passes `_parse_compile` or reaches them on another path. This pass did not trace the input that reaches each one.
- **The parser joins some lines of a triple-quoted value.** The triple shape reads 82 of 600 cases wrong. For example `body='''=don't(Roman's,Roman's\n==assertRoman'sa assert'''` reads the line break as a space. That is a wrong write of a test body, and a seat can meet it. The fixture records the 82 as they read now.
- The model shape refuses 240 of 400 cases. Most have the label inside a line, where `_namespace_labels` reads nothing by design.
