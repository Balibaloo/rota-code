# Frame 204, review 1g of 07b2cbcc

Read-only review on the worktree `C:/Users/roman/rota_rv204g` at 07b2cbcc (the meta workflow).
The reviewer ran no gate and re-recorded no case. Probes are dated 2026-10-12.

Verdict: one high finding. The pass does not hold point 1 at run time. Fix it before the walk.

## (a) Verdicts

1. FAILS. `ctx.mode` is never "reconcile" at run time, so the reconcile seat gets the `@prose` advice only for a ref that `_is_prose_ref` admits (H1).
2. HOLDS, with one gap. A Tester sends `about_table="criteria"` in most calls, and `criteria.load` is in the tools of `tests_missing`. A table name that the seat invented is copied into the advice without a check (L1).
3. HOLDS, with the same gap. The Developer on `tick:verdict_failed` reads the refusal for a commit sha. The new text is better than the README advice, but it names `criterion_deviation`, which is no table (L1).
4. HOLDS. The new checks fail on "never an item id" and pass on the composed brief.
5. HOLDS. The new door test fails at ba543e42 on the `@prose` assert and passes at 07b2cbcc.
6. HOLDS. The diff touches three files. It moves no brief and no op docstring. Only the case L3-a-failed-verdict-turns-into-a-fix holds the old text.

## (b) Findings

H1. `rota/roles/api.py:8227`, high, CONFIRMED.
The branch tests `ctx.mode == "reconcile"`. `session_mode` (`rota/core/runner.py:136-154`) returns "readonly" or "normal" only. The reconcile mode key goes to `_mode_key`, and it never reaches `ctx.mode`.
Nights 141 and 142 stored `mode='normal'` for every `tick:reconcile` session.
Probe p7 built the Vision Keeper with mode "normal" on an empty account. The ref `billing` and the ref `how_it_works` got "send the id of a row of items". With mode "reconcile", the same refs got `@prose`.
So the fix of VK4 is lost at run time for a non-prose ref. The three tests in `tests/rota/test_identity.py:148,161,170` build `mode="reconcile"`, which no night builds, so they stay green.
In nights 141 and 142, the reconcile seat sent 100 ledger.log calls. 61 of them used refs that `_is_prose_ref` misses: `how_it_works`, `executes_commands`, `handles_argument_parsing`, `defines_commands_and_options`. These refs resolved in the nights, and the seat met no ref refusal. VK4's refs on an empty account are of the same shape, a name and not a path.
Fix: test `ctx.wake_kind == "tick:reconcile"`, and build the tests with `wake_kind` set, not `mode="reconcile"`.

L1. `rota/roles/api.py:8231-8232`, low, CONFIRMED.
The new text copies `about_table` into the advice before the table check that follows the ref check.
The L3 cassettes show `about_table="criterion_deviation"`, so the re-record will tell the Developer to send "a row of criterion_deviation", and no such table exists.
Nights 141 and 142 hold 8 Tester or Terminologist calls with a table that does not exist: `batch_` (5), `confirm_default_on_eof` (1), and others.
Fix: name `about_table` only when it is in `_id_tables(ctx.conn)`. Otherwise name the wake's refs or the mode's load tools.

L2. `tests/rota/test_prompts.py:298-300`, low, PLAUSIBLE.
The new whole-word checks read `sentence` and `template` raw. A re-wrap that puts a line break inside "that item's id" or "the item id" breaks them. This is the same class as review 1f, L4. The pass normalised the triage check only.
Fix: join `sentence` and `template` on single spaces before the three asserts.

L3. `rota/roles/api.py:8150`, low, PLAUSIBLE.
`_is_prose_ref` admits any ref that starts with "readme" or "prose", for example a code file `readme_parser.py`. No night ref has this shape.
Fix: match `readme` with a dot or an end of string, and match `prose` only after the `@`.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d609cf11-e3b0-446b-b02a-29ab3633c919/scratchpad/rv204g/`. The databases there are copies.

- p1.py: ledger.log refs per role in n141.db and n142.db, with `_is_prose_ref`. Every session row has mode "normal".
- p2.py: the Vision Keeper refs by wake kind. Night 141 had 59 `tick:reconcile` calls, 39 non-prose. Night 142 had 41, 22 non-prose.
- p3.py: `ref_resolves` on the night refs at the end of each night. All resolved. `_declares_an_area` is true at the end.
- p4.py and an inline query: "names no row" in turns. The reconcile seat met 0 refusals in either night. The Liaison, the Architect and the Terminologist met them.
- p5.py and p6.py: cassettes.db. The reconcile cassettes hold 2 refusals on `billing`, on the area branch. The 4 old-text cassettes (gemma3:12b) are the Developer on `tick:verdict_failed`, ref `ba78d4568a7debeab04d6a8c133f4dd23fa4a323`, table `criterion_deviation`. The seat made no further ledger.log call and went to code.write.
- p7.py: the refusal for `billing`, `how_it_works` and `README.md` with mode "normal" and mode "reconcile". Output is quoted in H1. `session_mode` of a `tick:reconcile` wake prints "normal".
- p8.py: the L4 checks. The old check gives True on "never an item id". The new checks give (False, False, False) there, and (True, True, True) on the composed reconcile brief. The triage check passes normalised.
- old/: `git archive ba543e42` of `rota`, `tests/__init__.py`, `tests/rota/conftest.py`, with `test_identity.py` from 07b2cbcc. The result is "1 failed, 1 passed", the failure at line 194, the `@prose` assert. At 07b2cbcc, `test_identity.py` and `test_prompts.py` give "42 passed".
- Inline query: the old text is in 4 cassettes, and in case_runs only for `L3-a-failed-verdict-turns-into-a-fix`.

What the L3 re-record should show: the Developer reads "send the id of a row of criterion_deviation". After the L1 fix, it reads a table that exists or the criterion id from its wake. The case should still pass on the fix path.

## (d) Usage

The harness line holds the exact figures. Estimate: about 45k input tokens, about 9k output tokens, about 54k in all. That is above the 40k cap.
