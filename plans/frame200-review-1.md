# Frame 200 review of 2e6afd1c, pass 1, Opus, 2026-10-11

The reviewer's report, from `rv200p1/report.md` under session be3ef742's scratchpad. 153.9k on the harness line against 100k. Rota workflow.

# Review of 2e6afd1c, frame 200 (the build loop), pass 1

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_rv200` at 2e6afd1c. Date: 2026-10-11. Rota workflow.

## (a) Verdicts

1. Not met. The door refuses 3 right shapes and 1 aliased form (findings 1 and 5). The 4 named shapes, `test_right_meta.py` and the 3 admitted test shapes land.
2. Met, with a condition. The door refuses 12 of 12 at the tree each session saw. At the batch head 5b04c4a it refuses only 7 of 12 (finding 2).
3. The v12 shape lands. The smallest predicate that refuses it refuses no right test that the probe found.
4. Partly met. No refusal carries a shape or an example call. Two forms state a false fact (findings 1 and 4).
5. Met. The two records are one list with one filter. No role except the Developer can reach `code.write`.
6. Yes, a false note. A Developer that sends a scope question in `batch_start` reads "end the session" on an empty commit (finding 6).
7. Partly met. Both named refusals give `END_STEP` and `END_FORM`. The escalation door still tells the seat to write after a challenge (finding 3).
8. No new test checks nothing. 4 tests pass on 586730c1, and each one is an admission guard by design.

## (b) Findings

1. `rota/roles/api.py:5873-5874` and the loop at 5882-5893, `is_fn_arg`. Severity: high. CONFIRMED.
   - The door refuses a factory call whose positional argument is a call. A command object built inline is such an argument.
   - Probe `p1_shapes.py` refused 3 right tests with "calling it never runs the option":
     - `version_option(show_python=True)(command()(hello))`
     - `version_option(show_python=True)(make_cli())`
     - `opt = version_option(...)`, then `opt(command()(hello))`
   - Real click 8.5 runs that form. Probe `p1_click.py` printed exit 0 and the output "x, version 9.9".
   - The refusal text is then false, so point 4 fails for these shapes.
   - Fix: refuse the "inline" and "decorator" kinds only when the call has no positional argument at all.
2. `rota/roles/api.py:5791-5793`, `_adds_option`. Severity: high. CONFIRMED.
   - The predicate reads `return option(...)` only. It misses `def decorator(f): return option(...)(f)`, which is the shape commit 5b04c4a gave `custom_version_option` on night 139.
   - Probe `p3_adds.py` showed `_adds_option` True at 342e24e, af5b2a7 and 9af3bea, and False at 5b04c4a.
   - Probe `p2_night.py` at the head 5b04c4a admits 5 of the 12 bodies: s251 t6, s251 t7 c1, s275 t1, s275 t2, s277 t1 and s279 t3, which are 5 distinct bodies. At 9af3bea it refuses all 12.
   - Change 2 does not stop that fit. s282 wrote 5b04c4a in a session with no challenge.
   - Fix: also accept a `Return` whose value is a call chain with an inner `.func` named `option` or `argument`.
3. `rota/core/sandbox.py:1726-1743`, the escalate branch of `_same_refs_refusal`. Severity: high. CONFIRMED.
   - Step 1: a Developer challenges the test.
   - Step 2: in the same session, it escalates on refs where an earlier escalation was answered.
   - Result: the door says "code.source those rows, write the change they call for, and commit", or "make one real change to the code the test calls".
   - Next, `code.write` refuses with `EndRefusal`. Probe `test_p5_escalate.py` printed both texts in sequence.
   - This is the contradiction between two doors that the design review named in section 2. The "answered" branch of the challenge door offers this same escalation (`test_p7_stage.py`).
   - The path is live. 6 sessions on nights 138 and 139 called `msg.escalate_architect` after `msg.challenge_tester`: s166, s388, s257, s274, s280 and s283.
   - Fix: when `_sent_this_session(ctx, "tester", "challenge")` holds, both texts give `_Ending(fact + END_STEP + _end_form)`.
4. `rota/roles/api.py:6866`, "the option that criterion {criterion_id} names". Severity: low. CONFIRMED.
   - The c3 criteria of nights 138 and 139 name no option. The s379 refusal names c3_show_python_version.
   - n139 c1 and c2 name `show_python`, which is a factory parameter and not an option. A seat can read the sentence as a request for a `--show-python` option.
   - Fix: name the factory, for example "never runs the option that `{orig}` adds".
5. `rota/roles/api.py:5868-5871`, `plain_def`. Severity: low. CONFIRMED.
   - `from click.decorators import command as make_command` with `@make_command()` reads as a plain function. The probe refused that right test.
   - Fix: resolve `ImportFrom` aliases of `command` and `group` before the name check.
6. `rota/roles/api.py:12888-12892`, the empty-commit note. Severity: low. CONFIRMED.
   - Probe `test_p6_note.py` ran a `batch_start` Developer that sent `msg.question_vision_keeper` and then an empty `code.commit`. It read "You have sent your message: end the session".
   - `batch_start.md:36-50` says that the scope question never ends the session, and the ticket is still owed.
   - The runner line at `runner.py:4217-4221` already says the same to every sender. So the note repeats that runner line and does not add a new fact.
   - Fix: limit the branch to a sent challenge or escalation, as `_refuse_after_challenge` reads it.

## Point detail

- Point 1 admitted:
  - the `group`-decorated function
  - `command()(version_option(...)(hello))`
  - the method on a class
  - `@version_option` on a def that `command()(hello)` wraps later
  - `test_right_meta.py`
- Point 1, the nested command in a group: this door admits it (`_plain_decorated` returned None). The ledger door then refused the literal "sub", and that door is outside this frame.
- Point 2 conditions:
  - Each body used its own `criterion_id`, with the criterion text and `surface_refs` that the night recorded, through `tests.encode` in `tests_missing`.
  - The tree was clickI at 9af3bea for night 139. Sessions s275 to s279 ran before s282 wrote 5b04c4a.
  - The tree was 3eebc90 for night 138, where `version_option` reads the same at every commit.
  - Every refusal of the 12 came from the new door, with no earlier door.
- Point 3:
  - The predicate: the factory return, as a call or as a name bound only to that call, is a positional or keyword argument of another call. The name must not also be a function parameter.
  - Probe `p4_arg.py` found 3 hits in the clickI suite, all `echo(testoption)`, where `testoption` is a parameter. With the parameter rule, the count is 0. It refuses `re.search(..., result)` in v12.
  - It does not refuse the right shapes of point 1 (reasoned: in those shapes the factory return is the called function, and never an argument).
- Point 5:
  - `_refuse_after_challenge` filters `ctx.outbound` on `to_role == "tester"`, `verb == "challenge"`, and route not triage. `_sent_this_session` uses the same filter on the same list.
  - Both see a staged challenge before the session commit lands it.
  - Only a question carries the triage route (`api.py:5268`).
  - The graph gives the Developer one challenge edge, to the Tester.
  - An escalation counts in neither record.
  - `critic/review.tools` holds `msg.challenge_tester` and no `code.write`. Only Developer modes hold `code.write` or `code.commit`.
- Point 7:
  - `test_p7_stage.py` sent a second challenge through `stage`. On an open prior it raised `EndRefusal`, with `END_STEP` and `END_FORM`. On an answered prior it offered `msg.escalate_architect`, which leads to finding 3.
  - The runner line is now at `runner.py:4217-4221`. It agrees with `END_STEP`.
- Point 8:
  - Probe `parent/` ran the two new test files on the 586730c1 tree: 9 failed and 78 passed.
  - These new tests pass on the parent: `test_pass_meta_key_on_a_local_function_lands`, `test_a_command_with_the_option_lands`, `test_a_factory_return_applied_to_a_command_lands` and `test_a_session_with_no_challenge_still_writes`.
  - Each one guards an admission, so a pass before the change is correct.
  - No test covers finding 3 or finding 6.

## (c) Probes

All probes are in the directory `rv200p1` of the session scratchpad named in the brief.

- `p1_shapes.py`: runs 10 right shapes through `tests.encode` on the DECOS tree of `test_prints_door_kind.py`.
- `p1_click.py`: runs real click 8.5 on `version_option(...)(command()(hello))`.
- `p2_night.py`: runs the night bodies through `tests.encode` with the criterion and surface refs of each night. It ran first at the batch head, and then at 9af3bea through an inline override.
- `p3_adds.py`: runs `_returns_factory` and `_adds_option` on `decorators.py` of clickI at 7 commits.
- `p4_arg.py`: runs the argument-use predicate over the clickI test suite.
- `test_p5_escalate.py`, `test_p7_stage.py`, `test_p6_note.py`: for each run, the reviewer copied the file into `tests/rota/` as `zz_probe_*.py`, ran it with `-n0`, and then deleted it. Each run ended with a clean `git status`.
- `parent/`: an extract by `git archive` of 586730c1, with the two new test files of 2e6afd1c. The reviewer ran pytest there.
- The reviewer did not run the gate. The points did not need the full suite.

## (d) Usage

Input about 120k tokens, output about 18k tokens, total about 138k. This is an estimate from the context counter, and it is above the 100k cap. Read the harness line for the exact count.

One more pass: 3 high findings, 3 low findings.


# The second look on dd583398, pass 1b, Opus, 2026-10-11

From `rv200p1b/report.md` under session be3ef742's scratchpad. 171.7k cumulative on the harness line, about 17.8k for the look.

# Second look at dd583398, frame 200 (the build loop), pass 1b

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_rv200` at dd583398. Date: 2026-10-11. Rota workflow.

## (a) Verdicts

1. The counts match the implementer report.
   - `p1_shapes.py`: 9 of the 10 earlier right shapes land. The ledger door refuses the tenth, the nested command, on the literal "sub". The frame 200 door admits it (`_plain_decorated` returns None).
   - `p2_night.py` at the heads 5b04c4a and 3eebc90: the door refuses 12 of 12 night bodies and the v12 body (s377 t4 c3), 13 refusals in total.
   - `p4_door.py` runs the door with no surface limit, over all 7 factories that add an option. It refuses 0 of 25 clickI test files.
2. Yes, one exists. The argument kinds refuse a factory return that a local helper applies to a command (finding 1). Of the other named forms:
   - `callable(deco)`, `isinstance(...)` and `functools.wraps(deco)` refuse.
   - A list and `cli.add_command(...)` land. The ledger door refused the `add_command` body on the literal "sub", and the frame 200 door admits it.
   - `callable` and `isinstance` never run the option, so they are not right tests of an option criterion.
   - The `wraps` body that applies the wrapped decorator is a right test, and it is refused.
3. Partly. No form carries a shape or an example call. In the forms of finding 1, "passing it to a call never runs the option" is false. In the other probed forms, every text is true.
4. Yes. `test_p5_escalate.py` reads `END_STEP` and `END_FORM` in both escalate branches, and the class is `EndRefusal`. `test_p6_note.py` reads "the change comes first: code.write, then commit" after a scope question.

## (b) Findings

1. `rota/roles/api.py`, the argument loop in `_plain_decorated`, kinds "decorator-argument" and "inline-argument". Severity: low. CONFIRMED.
   - The loop refuses a factory return that is an argument of any call. A call to a local helper can apply that return to a command.
   - Probe `p1_shapes.py` refused two right tests:
     - `cli = build(version_option(show_python=True))`, where `build(extra)` puts `@command()` and `@extra` on a def.
     - `opt = version_option(...)`, then `cli = build(opt)`.
   - Probe `p1_shapes.py` also refused a `functools.wraps(deco)` wrapper that applies `deco`.
   - Probe `p5_click.py` ran the helper form and the `wraps` form on real click 8.5. Both exited 0 and printed "x, version 9.9". So the refusal text is false for these forms.
   - The severity is low: 0 of 25 clickI files and 0 of 537 recorded bodies, as the implementer reports, have this form. A Tester rarely writes a helper.
   - Fix: skip the two argument kinds when the receiving call is a name that the test defines with `def`, or `functools.wraps`.

## (c) Probes

All probes are in `rv200p1b` under the session scratchpad. The second-look probes are:

- `p1_shapes.py`: the 10 earlier shapes, and 7 new shapes for point 2, through `tests.encode`.
- `p5_click.py`: the helper form and the `wraps` form on real click 8.5.
- `p2_night.py`: a copy of the pass 1 probe, which runs at the batch heads 5b04c4a and 3eebc90.
- `p4_door.py`: `_plain_decorated` over the clickI test suite, for every factory that adds an option.

The reviewer ran `test_p5_escalate.py` and `test_p6_note.py` from `rv200p1` the same way as in pass 1. For each run, the reviewer copied the file into `tests/rota/` as `zz_probe_*.py`, ran it with `-n0`, and then deleted it. Each run ended with a clean `git status`. The reviewer did not run the gate.

## (d) Usage

This second look used about 30k input tokens and about 6k output tokens, about 36k in total. This is an estimate from the context counter. Read the harness line for the exact count.

Stands: 0 high findings, 1 low finding.
