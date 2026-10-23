# Frame 304, review 2: pass 2 at 71bdd645

Verdict: do not accept the branch as it is. Two of the three forms refuse right tests. The `arrange` form refuses a test that imports a name the batch adds. The `stub` form refuses a right test whose stub is minimal, and a test that subclasses a project class. The `signature` form and the challenge door hold. Accept after the two fixes in section (b).

## (a) The claim and the verdict on each point

The claim: at encode the door runs the body on the batch's head and refuses three cases, `stub`, `arrange` and `signature`. A raise in the project's code or a failed assertion passes.

1. Point 1, the stored tests: 15 Tester bodies ran at their batch heads, 7 of night 158 and 8 of night 159. The door refused 1, night 158's `tst_confirm_eof_02` (tst_02 v3), by `arrange`. That test is wrong, so the refusal is right. The other 14 were admitted: 12 pass, 2 fail on project code or an assertion. 70 inherited rows never pass through `tests.encode`, so the door does not read them. The two red cases print the refusals in finding 5.
2. Point 2, the stub case: no rule in the traceback separates a stub the code must read from a stub it may read. The stub form must become a note to the Tester, not a refusal. Finding 2 and finding 3 show two right tests refused.
3. Point 3, the cost: one door run takes 0.60 s to 0.71 s on clickI, over 3 runs on each of 2 bodies. One run took 18.2 s, once, in 21 runs. Night 159 made 333 `tests.encode` calls, so the night pays at most about 4 minutes.
4. Point 4, nothing else changed: the diff is 4 files. The `_in_source` hunk is a move with no change of behaviour. The 4 pre-existing reds fail the same at `2d4fb5bb` and at `71bdd645`.

## (b) Findings

1. `rota/core/runner.py:2919-2948`, the `arrange` form. Severity: high for the night, high for the frame. CONFIRMED. A right test that imports a new surface inside its body is refused. Probe 7 ran `from click.utils import echo_pretty` at the bg_2 head. The run raised `ImportError: cannot import name 'echo_pretty'` at line 2. `arrange_fault` returned `rule: arrange`, so the Tester reads "no code can pass it". The import guard reads `ast.Name` and string constants only. It does not read an `ImportFrom` node on the raising line. Every Tester body of nights 158 and 159 for `confirm` imports the surface inside the test function. On a batch that adds a function, the door refuses each such test before the Developer writes the function. A module-level import gives a collection error, the word is `error`, and the door is silent. So two forms of one test get two answers. Fix: return None when the raising line holds an `Import` or `ImportFrom` node, or when the error is `ImportError` or `ModuleNotFoundError`.

2. `rota/core/runner.py:2852-2871`, the `stub` form. Severity: high for the night, high for the frame. CONFIRMED. A right test with a minimal stub is refused. Probe 3 encoded a test for `cr_2_confirm_default_on_eof` with a `ClosedStdin` class that holds `closed = True` and `isatty`, and no `readline`. The test asserts that `confirm("Go?", default=True, default_on_eof=True)` returns True. The door refused it: "Build the stub so that `readline` exists." A copy of the head that checks `sys.stdin.closed` before the read passes the same body. The stub form reads any `E` line on the test's class, also a raise inside the project's code. So the form breaks the claim that a raise in the project's code passes. At encode the head usually lacks the change, so the head's reads are no evidence of what the right code must read. Fix: make the stub form a note to the Tester that names the missing attribute, and admit the body.

3. `rota/core/runner.py:2857-2871`, the `stub` form on a subclass. Severity: high for the night, high for the frame. CONFIRMED. Probe 4 encoded `class MyCmd(click.Command): pass` and `assert cmd.aliases == []`. The door refused it with "Build the stub so that `aliases` exists." The class is not a stub. The attribute is the one the criterion adds, and the fix the door asks for makes the test empty. The form reads the class body and never reads its bases or the line that raised. Fix: if the stub form stays, skip a class with any base, and skip a raise on an `assert` line.

4. `rota/roles/api.py:15074-15076`, the `signature` text. Severity: low for the night, low for the frame. PLAUSIBLE, by reading. The text says "no code can pass it". Code that gives `text` a default passes s185's cr4 body. The criterion guard covers a named argument only. Fix: say "the code at the head requires `text`" in place of "no code can pass it".

5. The two red cases, from probe 2 at the bg_2 head of night 159 and from probe 1 at the bg_2 head of night 158. Severity: none. CONFIRMED. s189's tst_cr1 prints: "The run of this body on the batch's head raises `AttributeError: 'FakeStdin' object has no attribute 'readline'`. Line 8, `class FakeStdin:`, defines that stub in the test. The test fails in its own arrange step, on its own stub. Build the stub so that `readline` exists." The refusal is right by the criterion, because the flag is off and the old read path stays. The test is also wrong on its assertion. It expects `UsageError`, and the criterion's word "aborting" is `click.Abort`. A Tester who adds `readline` gets an admitted test that is still wrong. Night 158's tst_02 v3 prints that the run raises at line 6, the `mock_stdin.read.return_value` line, with `AttributeError: Mock object has no attribute 'read'`, and that no code can pass it. That refusal is right. Fix: none for the door.

6. Outside the points. `rota/roles/api.py:14674-14678` with `rota/roles/api.py:15033-15039`. Severity: low for the night, low for the frame. PLAUSIBLE, by reading. `_worktree_of` returns the project root when the batch row has no worktree. Night 158's bg_1 and bg_3 hold a `head_commit` and no worktree. An encode on such a batch writes the body into the project's main checkout and runs pytest there. The run restores the file after it. Fix: return None when `batches.worktree` is empty, before the call to `_worktree_of`.

7. Outside the points. The night's current tst_cr1 v4 is a wrong test that the door admits. Severity: low for the night, none for the frame. CONFIRMED by probe 1. The body asserts `result == False` with the flag off and an empty stdin. The criterion keeps the old behaviour, which is `Abort`. The run raises `Abort` at `termui.py:344`, inside the project's code, so the door admits it by design. Fix: none in this frame. The case belongs to the challenge loop.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/1b2c3f89-168f-4708-a241-5ecb0a745d11/scratchpad/r304b/`. Each batch head is a `git archive` copy with `git init` and its own `.venv`, so the live worktrees stayed untouched. The night databases were copied, and each copy points `batches.worktree` at the scratch copy.

1. `probe1.py`: `api._encode_run` and `api._arrange_run_refusal` on the 15 Tester bodies of nights 158 and 159 at their heads.
2. `probe2.py`: s189's tst_cr1 body and s185's cr4 body from `tests/rota/test_frame304_arrange_door.py`, at the 159 bg_2 head. The cr4 body gets the `signature` refusal with "Call `confirm` with `text`".
3. `probe3.py`: a minimal `ClosedStdin` stub for cr_2, refused at the head. The same body passes on `159_bg_2x`, a copy whose `confirm` checks `sys.stdin.closed` first.
4. `probe4.py`: a subclass of `click.Command` that asserts a new attribute, refused as a stub.
5. `probe5.py`: 3 timed door runs on each of 2 bodies.
6. `probe6.py` and `probe7.py`: a body-local import of a new name. `echo_json` exists at the head, so probe 7 uses `echo_pretty`, refused by `arrange`.
7. The 4 named reds and the new test file, `pytest -n 0`, at `71bdd645`: 4 failed, 7 passed. The 4 reds are `test_invoke_door.py::test_a_session_with_no_batch_reads_the_root`, `test_fixtures.py::test_no_case_leaves_a_reference_unwrapped`, `test_pins.py::test_with_prompt_keeps_every_pin` and `test_roles_doc.py::test_a_verb_carries_words_or_does_not_regardless_of_recipient`. The same 4 fail in `r304b/parent`, an archive of `2d4fb5bb`.

## (d) Usage

The harness does not show this agent's token counts. The estimate is about 90k input tokens, 12k output tokens, about 102k in total.
