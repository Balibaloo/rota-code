# Frame 144, pass 2: the review's findings, and the fact check

Meta workflow. Pass 2 of frame 144, the night databases are not a test tier. The implementing agent on Opus wrote this record on 2026-10-05. Part A repairs the findings of the read-only review of c888968. Part B builds change 1(d) of `plans/frame144-design.md`, the fact check. No door changed, and no refusal text moved (observed: the gate's stale line is 0, 2026-10-05).

Commits: 652c3fd (part A), 8726a13 (part B).

## Part A, the review's points

1. **Fixed.** `follow` compares the door, not the text. The door is the statement that raised the refusal, from the traceback (`sandbox._raise_site`). An `AGAIN` step that meets the same raising statement counts as refused (observed: `sandbox.py`, 2026-10-05). The literal door's `owed[:6]` stays, because that sentence is frame 148's. The stricter check reports it as finding 4 below.
2. **Fixed.** Each entry of `KNOWN_REFUSED_OFFERS` names the test id and the first words of the second refusal. Any other refused offer fails its test (observed: `tests/rota/conftest.py`, 2026-10-05).
3. **Fixed.** The hook writes the log and computes the findings in a `finally`. A failing test keeps its own exception, and the findings go into its report section. A passing test fails on a finding.
4. **Fixed.** `_ctx_snapshot` takes one `copy.deepcopy` of all attributes except `conn`, and a shallow copy of each list, dict and set. `_ctx_restore` puts back each original element that compares equal to its deep copy, and the deep copy otherwise. An attribute of a mutable type that is not a list, a dict or a set raises `TypeError` before the dry run starts. `test_a_dry_run_puts_the_context_back` asserts that `ctx.writes[0]` keeps its identity.
5. **No change, by design.** An offer behind `_admits` is named only when the dry run admits it. So such an offer cannot fail the follow check, and pass 1's first proof could not go red by the follow check (reasoned: the follow check and `_admits` send the same call through the same doors).
6. **Fixed.** The three "To replace X whole" offers of `code.write` send the seat's own text when the text parses to exactly one definition of X. Any other text stays `INVENT`.
7. **Fixed.** The entry-point door, the drops door (both sentences), `_span_offer`'s spans, the unnamed-definition door and the parse refusal's "tail of the statement" record their offers with the text as `INVENT`.
8. **Fixed.** Every offer carries its fragment of the refusal. The three exits of the written-back sentence, the claim of `verdicts.emit` and A2 of `_span_lost_refusal` now record theirs. `verdicts.emit` records two offers, `encodes=True` then the call again, and `encodes=False`, as the sentence names both values. `follow` asserts that the refusal holds each fragment, and that each argument of each offer is a parameter of its op. Over the gate run, 0 fragments were missing and 0 arguments were unknown (observed: the log of the gate, 2026-10-05).
9. **Fixed.** `Sandbox.call` clears `ctx.offers` and `ctx.facts` before the argument check. `test_an_argument_error_leaves_no_offer_of_the_call_before` holds it.
10. **Fixed.** `rota_serial_plugin.py` holds the rule that the model tiers run on one worker (observed: `uses_a_model` and its docstring, 2026-10-05). The dead first `pytest_configure` in `tests/rota/conftest.py` is deleted.
11. **Fixed.** An ast count gives 45 offer sites at c888968, 42 in `api.py` and 3 in `sandbox.py`, and 11 tests. `plans/frame144-pass1.md` is corrected. At 8726a13 the count is 49 in `api.py` and 5 in `sandbox.py`. 2 of the sandbox sites are frame 132's, in 4968ea7.

**The review's proof, repeated.** The staged-log read of the literal door (`api.py`, from a15c92c) was replaced by `said = []` in a local edit, then restored. `tests/rota/test_night46_context.py::test_every_invented_literal_is_named_in_one_refusal` went red by the follow check alone: "second refusal: ValueError: the test chooses 'beta_corp', 'alpha_corp', ..." (observed: 2026-10-05). `git diff` shows no trace of the edit.

## The known findings after part A

Each is a strict xfail in `tests/rota/test_offers_followed.py` and lines in `KNOWN_REFUSED_OFFERS`.

1. The project-id door outside a challenge: the new id keeps the seat's path, and the clash door refuses it ("tests/test_utils/test_confirm.py is already inh_022b8a87's file; ..."). 3 existing tests.
2. The cut door's "To add after it send start=, end=": the seat's replacement text added after the def does not compile or defines the name twice. 3 existing tests.
3. The unimported-module wall: the encode with the added import meets the literal door ("the test chooses 'default_answer', ..."). `ACT-TS-give-the-prompt-a-stream`.
4. **New in pass 2.** The literal door names 6 of 8 owed literals. The named `ledger.log`, then the encode again, meets the same door: "the test chooses 'golf', 'hotel', ...". `test_the_literal_offer_is_admitted_when_eight_literals_are_owed` holds it. No existing test owes more than 6 literals (observed: no other test in the known list, 2026-10-05).

## Part B, the fact check

`api._fact(ctx, kind, value, **where)` returns `value` unchanged and appends an `api.Fact` to `ctx.facts`. `sandbox.check_facts(sb, facts)` checks each one against the state. The hook runs it on every refusal that records a fact or an offer.

The kinds and their checks (observed: `check_facts`, 2026-10-05):

- `row`: the id is a stored row (`api.ref_resolves`) or a staged write.
- `test_path`: the tests row is stored or staged at the path.
- `file`: the path is a file of the worktree, or with `absent`, is not.
- `lines`: the file has this many lines now.
- `line`: the number is inside the file now, or inside the `text` given.
- `line_text`: line `n` of that text starts with the quoted words.
- `span`: `(lo, hi)` lies inside that text.
- `arg`: the name is a parameter of the op. The offers carry their argument names, so `follow` checks them as `bad_args`, and no door records an `arg` fact yet.

Sites converted, 29 `_fact` calls in `api.py` (observed: the ast count, 2026-10-05):

- `code.write`: the absent file, the line count of a span that is not a span, the cut door's spans, quoted lines and decorator line, the other boundary's span, the text's first and last line, the `__future__` line, the docstring line, the cross-block door's quoted lines, the line of a compile refusal and of a parse refusal in the merged text, the tail statement's span, the two numbers of the defines-twice door, the line count of the entry-point and drops doors, the spans of `_span_offer`, and the insert point of the unnamed-definition door.
- `tests.encode`: the project-id door's row and path, the stored row and its path, the other batch's test and batch rows, and the clash rows and paths of the same-criterion door and the one-file door.

**Counts over one gate run** (observed: `ROTA_OFFER_LOG` on the gate at 8726a13, 2026-10-05): 250 facts in 81 tests. `line_text` 119 (109 true, 10 false), `span` 48, `test_path` 35, `row` 17, `line` 16, `lines` 13, `file` 2, all true except the 10. The same run followed 250 offers in 104 tests: 148 sent, 12 refused (all known), 102 not sent because the text is the seat's, 14 `AGAIN` steps met another door.

**False facts found:**

- `_code_write`, the defines-twice door: "m.py defines f twice (lines 4 and 7)" gives ast's numbers, which count from 1. `code.source` and every other refusal count from 0, so each number names the line below the def (observed: 10 false `line_text` facts in `test_a_file_defines_each_name_once`, `test_an_overload_stub_is_not_a_second_definition`, `L1-DV-take-a-mistake-out`, `L1-DV-give-the-new-parameters-defaults` and the direct xfail, 2026-10-05). `test_the_defines_twice_numbers_are_code_source_numbers` holds it. No door is fixed in this pass.
- `toolproto`, the unterminated-list refusal with no open argument: it names `text='''...'''` for a call of an op that has no `text` argument (frame 137's sign). `test_the_parser_names_only_arguments_of_the_called_op` holds it. The parser runs outside `Sandbox.call`, so the hook does not see it, and the direct test reads the refusal's prose.

**Sites left:**

- The parser's refusals. The parser has no `ctx` and no signatures. A fact there needs the signatures passed to `extract`.
- The quotes of `_span_lost_refusal` ("removes 'import inspect'") and the names it says the file still uses.
- The `_bind_send` doors: the ids of a repeated message, the quoted rows of `_challenge_evidence`, and the waiting message of the same-refs door. The same-refs door is frame 132's, and its review runs now.
- The other `tests.encode` walls: the names a test never imports, the module a test imports, and the surface a test never calls.
- Every op outside `code.write` and `tests.encode`.
- Out of reach: a claim about runs, such as the revert door's "the tests pass both ways".

## The suite

The touched files pass: `test_offers_followed.py` 12 passed and 6 xfailed. `test_desk_guards.py`, `test_t0_sandbox.py`, `test_night46_context.py`, `test_touch_divergence.py`, `test_developer.py` and the two L1 cases of the false fact: 434 passed, 6 xfailed, then the one new test fixed (observed: 2026-10-05).

The gate on 8726a13 (observed: 2026-10-05):

```
suite: 23 failed, 2749 passed, 27 skipped, 7 xfailed, 16 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 1156.4s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The three new reds are the ones that the judge expects. They fail the same way without frame 144's changes (copied: pass 1's record).
