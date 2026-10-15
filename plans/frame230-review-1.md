# Frame 230, review 1 of 0d0f4771

Reviewer: an Opus agent, read-only, on the worktree `C:/Users/roman/rota_r230` at 0d0f4771 (observed: 2026-10-15).

Verdict: ACCEPT. The door refuses s154's lambda and admits every command shape the brief names. The five points hold. Three low findings stay open, and none blocks the pass.

## (a) Verdicts

1. The predicate: CONFIRMED. HEAD refuses s154's turn-2 lambda, and the parent admits it. All three command shapes land at HEAD.
2. The changed test: CONFIRMED right. The old test passed a plain `def echo_json(): pass` with no decorator, so the door is right.
3. The helper's reach: a decorated group, a `click.Group` object and `module.cmd` are admitted, which is right. `hello.main` is admitted, which is a miss (low).
4. The refusal text: CONFIRMED within STE limits. The fact comes first and the step second. One low note on "or".
5. The test file: CONFIRMED. Nine tests are red on the parent code and green at HEAD. `test_a_session_with_no_batch_reads_the_root` fails at both.

## Point 1, the predicate

- s154's literal first `tests.encode` call is in turn 1. Its body holds a local `mycmd` under `@command()`. Both HEAD and the parent admit it, which is right.
- s154's first lambda call is in turn 2, `runner.invoke(lambda: confirm("y", default_on_eof=True))`. HEAD refuses it with the brief's exact text. The parent admits it.
- The parent was emulated by `monkeypatch` of `api._callable_invoked` to return None. The api.py diff holds only the helper and its one call, so the emulation is exact.
- At HEAD, a local `@click.command()` def, the surface's `hello`, and frame 176's bare `@click.command` wrapper each land, `{'id': 'tst_x'}`.

## Point 2, the changed test

The parent's `test_a_local_function_is_admitted` (from 68d1f6eb, frame 131) passed `def echo_json(): pass`, with no decorator. That function is a plain function. Frame 131 admitted it only because its door left a local name to the test (`plans/frame131-pass1.md` line 24). It did not claim that the call works. `CliRunner.invoke` calls `get_default_prog_name(cli)` outside its own try, so a plain function always errors. The new expectation is right.

## Point 3, the helper's reach

- `runner.invoke(cli)`, `cli` under `@click.group()`: admitted. Right, because the decorator list is not empty.
- `cli = click.Group('cli')`, then `runner.invoke(cli)`: admitted. Right.
- `runner.invoke(hello.main)`: admitted. Wrong, because a bound method has no `.name` either. See finding 1.
- `runner.invoke(core.hello)`: admitted. Right, because an attribute is never read as plain.

## Point 4, the refusal text

- Sentence 1 has 18 words, under the 25-word limit for a description. The local-def form has 24 words.
- Sentence 1 joins two facts with "and": what the seat passed, and what `invoke` takes. Frame 131's refusal uses the same shape, so the reviewer keeps it.
- Sentence 2 is the instruction, 14 words, under 20. It comes after the fact.
- Sentence 2 gives two alternatives joined by "or". STE asks one instruction per sentence. See finding 3.

## Point 5, the nine tests

- HEAD test file on parent code (a `git archive` copy of the parent in the scratchpad): 10 failed, 36 passed. The ten are the nine new or changed tests and `test_a_session_with_no_batch_reads_the_root`.
- HEAD test file at HEAD: 1 failed, 45 passed. The one red is `test_a_session_with_no_batch_reads_the_root`, "DID NOT RAISE ValueError". That test is unchanged by the diff and red at the parent too.
- The new test `test_a_command_the_test_defines_or_the_surface_holds_is_admitted` is green at both, as an admission test must be.

## (b) Findings

1. `rota/roles/api.py`, `_callable_invoked`, the `plain` function (diff line about 6358). Low. CONFIRMED: `runner.invoke(hello.main, [])` and `CliRunner().invoke(functools.partial(confirm, 'y'))` both land at HEAD. Each fails on `.name` as s154 did. No night body in the scan used the shapes. Fix: leave the shapes out until a night shows one, and record the reach in the docstring.
2. `rota/roles/api.py`, `_callable_invoked`, the receiver set `runners = {"runner"}`. Low. CONFIRMED: `self.runner = CliRunner()` then `self.runner.invoke(lambda: 1)` lands at HEAD. The receiver check reads only a `Name` target. Fix: also accept an `Attribute` receiver whose attr is in `runners`, when a night shows the shape.
3. `rota/roles/api.py`, the refusal in `tests_encode` (diff line about 7688). Low. PLAUSIBLE: "Pass a function that `@click.command` decorates, or call the function without a runner." is two instructions in one sentence. STE asks one instruction a sentence. Fix: keep it, because the two are alternatives to one step, or split it in two sentences.
4. Outside: the scan coverage. Low. CONFIRMED: over 72 night databases, the helper reads 1,153 encode bodies with `.invoke(` and flags 67. Every flagged body passes a lambda or an undecorated local def, for example night 86's `dummy_cmd` and night 147's `run_confirm_with_default`. So the scan shows 0 false refusals. The probe could not parse 691 tool lines that span many lines, so those bodies are not counted. Fix: none for the pass. Say the 1,153 denominator where the frame records the rate.
5. Outside: `local, _line = made` in `tests_encode`. Low. CONFIRMED by reading: `_line` is never used, and the refusal names no line. Fix: none needed.

## (c) Probes

All probes ran in the worktree `C:/Users/roman/rota_r230` with the venv Python. The night databases were opened read-only, `file:...?mode=ro`.

- `probe_r230_s154.py`, `probe_r230_s154b.py`: read s154's turns from `clickI_night148.db` and printed turns 1 and 2.
- `probe_r230_test.py`: pytest probe with the test file's `db` fixture. It ran each s154 encode call at HEAD and at the emulated parent, and eleven shapes at HEAD. It ran first under `tests/rota/` and now sits in the scratchpad, `f230/probe_r230_test.py`. Its log is `probe_r230.log` in the worktree root.
- `probe_r230_scan.py`: ran `_callable_invoked` on every single-line `tests.encode` body in `D:/repos/rota/.rota/*night*.db`.
- `probe_r230_d.py`: printed the two flagged bodies that pass a named local def.
- The parent run: `git archive 0d0f4771^` into the scratchpad `f230/r1parent`, with the HEAD test file copied in. Then pytest on `tests/rota/test_invoke_door.py` there and in the worktree.

## (d) Usage

The harness line carries the exact count. The reviewer's estimate: about 45k input tokens, about 9k output tokens, about 54k total.
