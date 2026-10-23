# Frame 304, review 3: pass 2b at 426a2b70

Verdict: accept the branch. Pass 2b answers review 2's findings 1 and 2. The 15 night bodies keep review 2's outcomes. Two low findings stay open, and each has a one-line fix. The worst word of the whole-word match is `click`, because a missing project submodule always matches it.

## (a) The claim and the verdict on each point

The claim: the `stub` form is now a note and the body lands. The `arrange` form admits a missing name that the batch's rows name as a whole word. The form still refuses tst_02 v3. The `signature` form and the challenge door do not change.

1. Point 1 holds. Of 15 bodies, the door refuses 1 by `arrange`, 0 by `signature`, lands 0 with a stub note and 14 with no note. No body changes outcome from review 2.
2. Point 2 holds with one low finding. The rows hold 11 project words and 13 standard words. Two kinds admit a wrong test: the package word `click` and the module word `sys`.
3. Point 3: finding 3 stands as a note, low. Finding 4 stands, low. Finding 6 stands, low. Night 159 holds 1 batch with a head and no worktree, bg_1, merged.
4. Point 4 holds. The diff has 3 files, and every hunk serves findings 1 and 2. The 4 old reds fail the same. The 2 frame test files pass, 23 tests.

Point 1, what the door prints now:

- tst_02 v3, night 158 bg_2: refused by `arrange`. The text: "raises at line 6, `mock_stdin.read.return_value = ""  # Empty read implies EOF`: `AttributeError: Mock object has no attribute 'read'`. ... no code can pass it. Fix line 6 so that it runs."
- s189's tst_cr1 at 159 bg_2: lands with the note "Line 8, `class FakeStdin:`, defines a stub, and the run on the batch's head raises `AttributeError: 'FakeStdin' object has no attribute 'readline'`. The stub lacks `readline`, and the code may need to read it. Give the stub `readline` if the right code reads it."
- Review 2's probe 3, the `ClosedStdin` stub: lands with the same note on line 5 and `readline`.
- Review 2's probe 4, the `MyCmd(click.Command)` subclass: lands with the note "Line 3, `class MyCmd(click.Command):`, defines a stub ... Give the stub `aliases` if the right code reads it."
- Probe 7's `echo_pretty` import at 159 bg_2: refused by `arrange`, because no row of bg_2 names `echo_pretty`. The door text is "Fix line 2 so that it runs." With the criterion text as `adds`, `arrange_fault` returns None. That is the claim.
- s185's cr4 at 159 bg_2: refused by `signature`, as before. The text: "Call `confirm` with `text`, because its signature requires it."

Point 2, the words of the rows that are also Python names. The rows are the item text, the criteria and the touch rows of each batch.

| Night, batch | Project words | Standard words |
|---|---|---|
| 158 bg_1 | click, echo, echo_json, utils | json, next, object, print |
| 158 bg_2 | Abort, argument, click, confirm, prompt, termui | False, True, any |
| 158 bg_3 | click, decorators, version_option | any, format, set, string |
| 159 bg_1 | click, echo, echo_json, utils | any, next, object, print |
| 159 bg_2 | UsageError, argument, click, confirm, option, termui | True, open |
| 159 bg_3 | command, confirm, echo_json, prompt | code, object, print |
| 159 bg_4 | click, command, decorators, option, version_option | format, string, sys |

- `click`, in 6 of 7 batches: a wrong admit, CONFIRMED. The match splits a dotted module name, so `No module named 'click.termui_compat'` matches the word `click`. Every typo of a project submodule lands.
- `sys`, in 159 bg_4: a wrong admit, CONFIRMED. A body that uses `sys.argv` with no `import sys` lands.
- `json`, in 158 bg_1: a wrong admit by the same path as `sys`. Night 159 bg_1 does not hold the word, and the probe there refused, as it should.
- `utils`, `termui`, `decorators`: a wrong admit for a missing deeper module such as `click.utils.x`, through the same dotted split.
- `echo`, `confirm`, `prompt`, `option`, `command`, `Abort`, `UsageError`, `argument`: a missing import of one of these lands. The admit is wrong only for a name the head already exports. A body that calls a surface name raises at the call line, and the door admitted that line before pass 2b.
- `True`, `False`, `any`, `next`, `object`, `print`, `open`, `set`, `format`: a builtin never raises a NameError, so these words admit nothing.
- `string`, `code`: these modules always import, so these words admit nothing.

Severity for the night: low. Before frame 304 every such body landed. So a wrong admit only gives back the old behaviour. No body of nights 158 and 159 is one.

## (b) Findings

1. `rota/core/runner.py:2961-2966`, the whole-word match. Severity: low for the night, low for the frame. CONFIRMED by probe 4c and probe 5c. The match splits a dotted module name and tests each part. So `No module named 'click.termui_compat'` matches `click`, and the body lands at 159 bg_2. The match also admits a forgotten standard import. `NameError: name 'sys' is not defined` lands at 159 bg_4, because a criterion says `sys`. With an empty `adds`, both bodies give `rule: arrange`. Fix: match a dotted module by its last part only, and skip a name in `sys.stdlib_module_names` or `builtins`.

2. `rota/roles/api.py:15082-15091` with `rota/core/runner.py:2863-2882`, finding 3 of review 2. Severity: low for the night, low for the frame. CONFIRMED by probe 2c. The subclass `MyCmd(click.Command)` now lands, and the note calls it a stub. The note says "Give the stub `aliases`". A Tester who obeys makes the test assert its own value. The body lands, so the harm is one bad note. No night body subclasses a project class. Fix: skip a class with a base other than `object` in the stub form.

3. `rota/roles/api.py:15093-15095`, finding 4 of review 2. Severity: low for the night, low for the frame. PLAUSIBLE, by reading. The `signature` and `arrange` text still says "no code can pass it". Probe 7 at bg_2 shows the `arrange` text on a right test whose name no row holds. Fix: say "the head cannot run this line" in place of "no code can pass it".

4. `rota/roles/api.py:15042-15049` with `rota/roles/api.py:14664-14682`, finding 6 of review 2. Severity: low for the night, low for the frame. CONFIRMED by a read-only query. Night 159's database holds bg_1 with a `head_commit`, no worktree and the status `merged`. Night 158 holds bg_1 and bg_3 in the same state, both `merged`. An encode on such a batch writes the body into the project's main checkout and runs it there. The run restores the file. A merged batch rarely takes an encode, so the risk for night 160 is small. Fix: return None when `batches.worktree` is empty, before the call to `_worktree_of`.

5. Outside the points. `rota/core/runner.py:2863-2882`, the order of the forms. Severity: low for the night, low for the frame. PLAUSIBLE, by reading. The stub form returns first, and it is now a note. So a body with a stub `E` line never reaches the `signature` or `arrange` form, and it lands. Before pass 2b the order did not matter, because every form refused. No night body shows both. Fix: on a stub match, keep the note and go on to the `signature` and `arrange` forms.

6. Outside the points. `rota/core/sandbox.py:1135-1153`, `_arrange_fault_of`. Severity: none. CONFIRMED by reading. The challenge door calls `arrange_fault` with no `adds`, so it admits the same quotes as before. The claim that the challenge door does not change holds. Fix: none.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b85289fd-418f-43a1-a641-15dad2620cfa/scratchpad/r304c/`. Each one imports `rota` from `C:/Users/roman/rota_r304` at 426a2b70. Each one runs on review 2's batch-head copies in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/1b2c3f89-168f-4708-a241-5ecb0a745d11/scratchpad/r304b/`. `n158.db` and `n159.db` are copies of review 2's copies, and each points `batches.worktree` at the head copies.

1. `probe1c.py`: `api._arrange_run_refusal` with `notes` on the 15 Tester bodies of nights 158 and 159. Result: 1 `arrange`, 14 landed, 0 notes.
2. `probe2c.py`: s189's tst_cr1, s185's cr4, review 2's probe 3 stub, probe 4 subclass and probe 7 import at 159 bg_2. Probe 7 also runs `arrange_fault` with and without `adds`.
3. `probe3c.py`: the words of each batch's rows, against click's exported names, the standard module names and the builtins.
4. `probe4c.py`: three wrong bodies through the door. A missing `import sys` lands at 159 bg_4. A missing submodule `click.termui_compat` lands at 159 bg_2. A missing `import json` gets a refusal at 159 bg_1.
5. `probe5c.py`: `arrange_fault` on the two landed bodies of probe 4c, with an empty `adds`. Both give `arrange`, so the match alone admits them.
6. A read-only query of `D:/repos/rota/.rota/clickI_night159.db` and `clickI_night158.db` for the `head_commit`, `worktree` and `status` of each batch. No `clickI_night160.db` exists.
7. `pytest -n 0` on `tests/rota/test_frame304_arrange_door.py` and `tests/rota/test_frame304_arrange_raises.py`: 23 passed. The 4 named reds of review 2 ran at 426a2b70 and in `r304b/parent`, an archive of 2d4fb5bb: 4 failed in each. The `E` lines, with paths and addresses removed, are the same. They are in `reds_rota_r304.txt` and `reds_parent.txt`.
8. `git diff 71bdd645 426a2b70`: 3 files, `rota/core/runner.py`, `rota/roles/api.py` and `tests/rota/test_frame304_arrange_door.py`. Every hunk serves review 2's findings 1 and 2.

## (d) Usage

The harness does not show the token counts of this agent. The estimate is about 70k input tokens, 10k output tokens, about 80k in total.
