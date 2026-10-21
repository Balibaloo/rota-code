# Frame 301, review 1 of c8f2fa5c

Verdict: accept c8f2fa5c. One high and one medium need a pass 2 before the frame closes. The commit meets its condition: the hop is admitted, the NameError guard speaks first, 138 of 138 wrong bodies of nights 136 to 157 stay refused, and the gate shows 0 new reds.

Reviewer: Opus, session 5389be74, 2026-10-21. Worktree `C:/Users/roman/rota_r301` at c8f2fa5c, parent 571755f4 from `scratchpad/f301/redcheck`. Counts: high 1, medium 1, low 5.

## (a) The verdict on each point

1. The count reproduces: 231 bodies, 106 refused before, 106 after, 88 stdin and 18 NameError. 17 of the 18 name a truly unbound name. 1 names `__builtins__`, which every module binds. That one is a wrong refusal, finding 1.
2. The pass admits a helper defined after the command, a nested def, a call under `if`, two commands with one caller, and a helper nested in the test function. It misses a helper called through an alias and a method of a class. No night body holds a missed shape.
3. The order sends no recorded body the wrong way. s266, s351 seq 5 and s245 seq 4 each get a true NameError text, and the stdin text follows when the name is bound.
4. The offer is right for two commands with one caller, for an invoke with no `input=`, and for a bare call. It is wrong for an alias-called helper, finding 3.
5. The six tests are red at 571755f4 for the reasons the brief names, 4 failed and 2 passed. The s258 test asserts the right line. The clause "imports from click" is a residue, finding 7.
6. Two live runs of `L1-TS-assert-the-value-the-surface-returns` key on the moved text. The "0 stale" of the implementer did not measure this, finding 2.
7. The residues and their cycles are in section (e).

## (b) Findings

### High

1. `rota/roles/api.py` 7703 to 7706, the NameError guard refuses `__builtins__` and `__file__`. CONFIRMED: `hasattr(builtins, "__builtins__")` and `hasattr(builtins, "__file__")` are both False, so the guard treats a name every module binds as unbound. Probe `dunder.py` at both commits: a test that reads `__file__` gets "the test uses __file__ and never imports or defines it". Night 144, s471 seq 5, moves from the stdin text to "the test uses __builtins__ and never imports or defines it" under this commit. The body is wrong by other means, so the count holds, but the text now sends the seat to define a name that exists. The guard is older than the frame. The new order makes it the first voice for this body. Fix: add `__builtins__`, `__file__`, `__name__`, `__doc__` and `__spec__` to the names the guard accepts, with the body of s471 as the red test.

### Medium

2. `tests/rota/cases/l1_tester.yaml` 1495, the case `L1-TS-assert-the-value-the-surface-returns` runs on qwen3.5:9b, and two of its live runs carry the moved text. CONFIRMED: probe `cases3.py` replayed the 59 distinct encode bodies of the 26 live case runs that hold "stdin is captured" at both commits. Two bodies change, both of this case: run 3 at prompt hash e989058e, turn 2, `t_3_return_default_no_side_effects`, and run 4 at prompt hash 44640edd, turn 0, `test_confirm_returns_default_no_side_effects`. Each moves from the stdin text to "the test uses confirm and never imports or defines it". The next user turn changes, so the cassette key misses, and the run cannot replay. `casestatus` composes the system text only, so its "0 stale" did not see this. The gate from the worktree printed "stale: the register is absent", because `tests/rota/cassettes.db` is not tracked. `ACT-TS-give-the-prompt-a-stream` is unchanged, 0 of its bodies move. Fix: run the gate from the checkout with the register present, and re-record the two runs under qwen3.5:9b before the frame closes.

### Low

3. `rota/roles/api.py` 6667 to 6674, the hop follows a bare name only. CONFIRMED by `shapes.py`: shape d, `ask = helper` and the command calls `ask()`, is refused with "The confirm() call is in helper(), and no command that CliRunner().invoke runs calls helper()". The command calls it. Shape e, `Asker().ask()`, is refused with "Call ask() inside the command cmd()". The command does call it. No night body holds either shape: 106 of 106 remaining stdin refusals carry the route, and 0 carry the helper text. Fix: resolve a module-level alias to its def, and say "through a name the door does not follow" when the holder is a method.
4. `rota/roles/api.py` 6758 to 6789, the step names the first invoked command. CONFIRMED by `shapes.py` shape m: `other` runs with `input=""` and `cmd` runs without it, and `confirm()` sits in `cmd`. The text is "The confirm() call is in cmd(), and no command that CliRunner().invoke runs calls cmd(). Call cmd() inside the command other()". The right step is `input=` on the invoke of `cmd`. Fix: when the holder is a command the body invokes without `input=`, offer the keyword.
5. `rota/roles/api.py` 6662 to 6665, `defs` reads the whole tree. CONFIRMED by `shapes.py` shape h: a helper defined inside `test_x` and called from a module-level command is admitted. At run time the name is unbound in the command. The NameError guard reads def names without scope too, so the body reaches pytest. Not a night shape. Fix: none now. Note it in the wall guide under cause 8.
6. The commit message and the report say "the 106 wrong bodies of nights 136 to 157". CONFIRMED by `count2.py`: `count.py` reads nights 136 to 149 only, `range(136, 150)`. Nights 136 to 157 hold 315 distinct bodies in 44 sessions, 138 refused on the stdin branch before, 138 still refused, 106 on the stdin branch after, 32 moved to the NameError or surface text, and 0 newly admitted. The 14 extra moves of nights 150 to 157 each name a truly unbound name, `UsageError`, `cli`, `confirm`, `CliRunner`, `click`, or the module of the surface for s258. The claim is true by accident. Fix: write 138 of 138 and the range in the close line of the frame, and make `count.py` take the range.
7. `rota/roles/api.py` 8583 to 8588, the clause "this test imports from click" of the surface door names `sorted(imported_from)[0]`, not the wrong import. CONFIRMED by the s258 test: the body imports from `src.click.termui`, and the text blames `click`, which `click.testing` supplies. The line it offers, `from click.termui import confirm`, is right: `src.click.termui` loads a second copy that `CliRunner.isolation` never patches. The test asserts the line only, so it survives a text fix. Outside this frame. Fix: name the import whose module is not the module of the surface.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/5389be74-1e5e-433d-aa86-c4a8d594cb8e/scratchpad/f301_review/`.

- `door.py`: the `tests.encode` door of the rota root first on `sys.path`, against the `clickwt` tree of frame 254, the same fixture as the `count.py` of the implementer.
- `count2.py ROOT FIRST LAST OUT`: the count of frame 254 with the root and the night range as arguments. Ran for 136 to 157 at c8f2fa5c, `after_157.jsonl`, 2m15s, and at 571755f4, `before_157.jsonl`. The compare for 136 to 149 gives 231, 106, 106, 88, 18.
- `shapes.py ROOT`: 17 hop and offer shapes plus s266 turn 4 and three night bodies, at c8f2fa5c.
- `dunder.py ROOT`: `__file__` and `__builtins__` through the guard at both commits.
- `cases2.py`, `cases2_lib.py`, `cases3.py ROOT OUT`: the encode bodies of the case runs that carry the stdin text, from `case_runs.transcript`, replayed at both commits, `live_before.json` and `live_after.json`.
- The new test file: 6 passed at c8f2fa5c in 7.4s. At `scratchpad/f301/redcheck`, 4 failed and 2 passed, with `rota.__file__` confirmed in the copy.
- The gate from the worktree: 7 failed, 4158 passed, 207 skipped, 22 xfailed, new reds 0, reds gone 0, stale not measured, 320s. The gate stored its baseline at c8f2fa5.
- SQL on `tests/rota/cassettes.db`: "stdin is captured" is in 0 cassette completions, 55 cassette user texts and 661 `case_runs` transcripts of two cases.

## (d) Usage

About 130k input tokens and 15k output tokens, about 145k in total. Estimates, with no sub-agent.

## (e) What a night still needs

- Finding 1, the dunder names of the guard: half a cycle, with s471 seq 5 as the red test.
- Finding 2, the re-record of two runs under qwen3.5:9b: GPU time, no build cycle, before the close line.
- Findings 3 and 4, the alias, the method and the uninvoked command: 1 cycle, after a night shows one of the shapes. Today 0 of 106.
- Finding 6, the range of the count: in the close line, no cycle.
- Finding 7, the clause of the surface door: 1 cycle in its own frame, open question 1 of the implementer.
