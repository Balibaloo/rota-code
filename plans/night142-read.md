# Night 142 read, walks 2 and 3: the measure's batch loops at attempt 8

Rota workflow throughout, except where a line says meta workflow. Sources:
the copy `.rota/clickI_night142.db` opened read-only, `.rota/night142.log`
lines 182 to 332, `.rota/clickI_night142.principal.jsonl` (night 142 rows
only), the worktrees under `D:/repos/_AI/sample_repos/clickI/.rota/worktrees`,
and the tree at 6a80be2c. Read on Opus, 2026-10-12. Query scripts:
`q.py`, `q1.py` to `q5.py` in the holding session's scratchpad.

The facts that the brief gave were checked. All hold, with two corrections:
`batch_2` reached exhaustion, attempt 10 of 10, before m355; and the
Vision Keeper's answers are m391 and m397, to the Tester's questions m390
and m395.

## 1. The measure

**The ratio reads no merge in 10 attempts on `batch_2` and no merge in 8
attempts on `batch_3`.** Nights 138 and 139 read no merge in 8 and 7. The
target, a merge within 4, is not met (observed: `sessions.wake_detail`,
`batches`, log lines 255 to 332).

`test_runs` keeps only the last run of each test, so the per-attempt reds
come from the `[tests.load]` block that each Developer wake read (observed:
`q1.py` over the first turn of each `tick:tests_failing` session).

`batch_2_show_python_version_flag`. Commits 63b42de (06:47, "Add show_python
flag to version_option"), 7a8f3ef (06:57, "fallback to sys.version_info when
auto-detection fails"), 1fe0bdb (07:02, "Add sys import"). Head 1fe0bdb.

| Attempt | Wake | Harness line | Red test, first `E` line |
|---|---|---|---|
| 1 | s466 batch_start | 34, 0 | none |
| 2 | s468 | 35, 1 | tst_2: `KeyError: 'prog_name'` |
| 3 | s470 | 35, 1 | tst_2: `KeyError: 'prog_name'` |
| 4 | s472 | 35, 1 | tst_2: `TypeError: 'in <string>' requires string as left operand, not int` |
| 5 | s474 | 35, 1 | tst_2: `assert ('Python' in '' or '3' in '')` |
| 6 | s477 | 35, 1 | tst_2: same |
| 7, 8 | none (tests_missing wakes s478, s484, s485) | 35, 0 and 36, 0 | none |
| 9 | s491 | 37, 2 | tst_2 and tst_1: `assert ('3.12' in 'cli, version 3.14.2 (3.14.2)\n' or '3.11' in ... or '3.10' in ...)` |
| 10 | s493 exhausted | 37, 1 | tst_2, the same line (`test_runs` tr216 at 1fe0bdb) |

At attempt 10 the product printed `cli, version 3.14.2 (3.14.2)`, which is
what the request asks. The one red test, `tst_2_flag_triggers_version_string`
version 6, asserts one of three fixed Python versions (observed: tr216).

`batch_3_show_python_version_flag`. One commit, 8bb0841 (07:32, s520). Head
8bb0841 at every attempt (observed: `batches.head_commit`, `git log`).

| Attempt | Wakes | Harness line | Red tests, first `E` line |
|---|---|---|---|
| 1 | s520 batch_start | 34, 0 | none |
| 2 | Tester s521, s524, s526 | 38, 0 | none: four tests on `src/click/decorators.py::version_option` passed |
| 3 | s527, s529, s530, quarantined at s533 | 39, 5 | tst_4, 6, 7, 8, 9: `assert 1 == 0` (exit code 1) |
| 4 | s538 | 39, 5 | tst_4, 6, 7, 8: `ModuleNotFoundError: No module named 'PIL'`. tst_9: `assert 2 == 0` |
| 5 | s540, s545, s547 | 39, 5 | tst_4, 6, 7, 8: PIL. tst_9: `Command failed with exit code 2: Usage: dummy [OPTIONS]` |
| 6, 7 | s549; s555, s556 | 39, 5 | tst_4, 6, 7, 8: PIL. tst_9 changing |
| 8 | s563, s564, s565 | 39, 5 | tst_4, 7, 8: PIL at `examples\imagepipe\imagepipe.py:3`. tst_6: `ImportError while importing test module`. tst_9: `RuntimeError("'test_version_option_format' is not installed. Try passing 'package_name' instead.")` |

At attempt 2 the batch stood at 38 tests and 0 red, with the four Tester
tests on `version_option` (observed: log, s526 encodes admitted). The batch
did not merge there because tst_9 had no landed test yet (reasoned: s524
routed `c_show_python_version_format` to the Terminologist, and s526 landed
tst_9 last).

## 2. The surface refs

**Terminologist s536 wrote `examples/imagepipe/imagepipe.py::process_commands`
into four criteria at 08:01 or after, in criterion repair mode, on the relay
m378 of the principal's m376.** The fifth, `c_show_python_version_format`,
was refused as `unchanged` and keeps `src/click/decorators.py::version_option`
(observed: `tool_calls` s536 seq 15 to 19, turn 2 results, `criteria`).

1. The principal's page m375 showed five checks failing `assert 1 == 0`. The
   principal said at m376: "the tests don't run it on a real command" (observed:
   jsonl, `messages` m376).
2. The relay m378 carried `principal_verdict` contest on all five criteria.
3. The brief `rota/roles/prompts/terminologist/criterion_repair.md` lines 8 to
   12 says: "`surface_refs` naming the callable a test would exercise ... words
   alone are never the fix. `[code.callables]` lists the candidates the note's
   words touch". s536's turn 1 restates these lines and then writes the five
   respecify calls in the same reply (observed: s536 turn 1 completion).
4. The pre-run `[code.callables]` list has no hint and ranks by `fan_in`. Its
   first row is `examples/imagepipe/imagepipe.py::process_commands | function | 0`.
   `src/click/decorators.py::version_option` is further down the same list. s536
   took the first row (observed: s536 turn 1 user, rows 1 and 17 onward).
5. `criteria.respecify` admitted a surface in `examples/`, outside the batch's
   expected files, `src/click/decorators.py` and `tests/test_basic.py`, and a
   module whose third line imports `PIL` (observed: s536 results, `batches.expect`
   in s563).

Before s536, s519 (relay m368, from page m365) had set the surface of two
criteria to `src/click/decorators.py::version_option`, and s512 had written
the bare `version_option` (observed: `tool_calls` s512, s519).

The principal's pages on the files to touch:

- m326, 06:38, the batch_2 page: "expected to touch src/click/decorators.py,
  ...::custom_version_option, ...::version_option, tests/test_basic.py" and a
  long list of `tests/test_options.py` tests. The principal corrected lines 2
  and 3 only and did not name the files (observed: jsonl, night 142, m326).
- m365, 07:29, the batch_3 page: "expected to touch src/click/decorators.py,
  tests/test_basic.py; might touch custom_version_option, version_option". The
  principal corrected lines 2 and 4, help message against version message
  (observed: jsonl, m365).

No page showed the principal `examples/imagepipe` before the loop. The page
m375 shows checks and the touch line, and no surface ref (observed: jsonl m375).

**This is a new wall, not frame 202's.** Frame 202, "a criterion's text names
one callable and its surface ref names another", needs a callable named in
backticks in the text. Here the text names no callable, and the surface is the
first row of an unhinted candidate list, a callable that neither the request,
the text nor the batch's expected files name (reasoned: frame 202's ends-when
line 1 against the four criteria texts). Frame 202's door would not fire on
these rows.

## 3. The Tester on the import

**The Tester dropped the `imagepipe` import 22 times after s536, and the
doors refused every one. It landed 15 encodes, all with the import**
(observed: `q4.py` over the encodes of tst_4, 6, 7, 8 in s537 to s562).

| Wake | Read | Encoded | Result |
|---|---|---|---|
| s537, m379 answer from s536, refs only | the new surface on the criteria | 4 with the import and `subprocess`; 4 without; 4 with; 12 without | 4 refused "one program, one name"; 4 refused by the NameError door "The criterion's surface is examples/imagepipe/imagepipe.py::process_commands: add `from examples.imagepipe.imagep...`"; 4 landed with the import; 8 refused by the surface door, 4 unanswered at the end |
| s539, m380 | tst_9's challenge | tst_9 | landed |
| s542, m382 | the PIL error | tst_4 without the import | refused by the surface door; answered m384 with the criterion's text |
| s546, s548 | tst_9's challenges | tst_9 only | s548 landed tst_9 |
| s552, m389 | the PIL error | tst_6, 7, 8 with the import; tst_4 without, then with | 4 landed with; 1 refused by the surface door; sent m390 to the Vision Keeper |
| s554, m391 | the Vision Keeper's answer | tst_4 with the import, `unchanged`; `ledger.log` kind `blocked` | logged as a fault, "No page shows it" |
| s558, m393 | the PIL error, `imagepipe.py` source | nothing | sent m395 to the Vision Keeper, m396 to the Developer |
| s562, m397 | the Vision Keeper's answer | 5 without the import, then with | 3 refused by the surface door, 1 by "collect nothing"; 6 landed with; 2 refused as not Python |

The Vision Keeper's answers carry no words.

- m391, s553: `msg.answer_tester` with refs `c_show_python_version` and
  `tst_4_version_option_has_python`, no text. s553 sent the same call three
  times and the repeat door ended it (observed: `messages` m391, s553 turns 1 to 4).
- m397, s560: refs `c_show_python_version` and `tk_2`, no text. s560's reply
  text, which no seat receives, says "The test environment does not need to
  include PIL because the criterion ... is not about image processing" (observed:
  s560 last turn).

After m391 the Tester kept the import and logged a fault. After m397 it
tried to drop the import and the surface door made it put the import back
(observed: s554, s562).

**The surface door of `tests.encode` keeps the import**: `rota/roles/api.py`
lines 6812 to 6818 at 6a80be2c and at HEAD, "the surface {surface[0]!r} lives
in {...}.py and this test imports from {...}. Import the surface from its own
module". The NameError door at lines 6423 to 6429 adds the same import line.
The surface door checks that a test imports the module of the surface. It does
not check that the module loads in the sandbox (observed: `sed` of the file;
reasoned: the door code, lines 6630 to 6687, checks only that the top module
name exists in the tree).

## 4. The Developer under frame 200's doors

**The Developer wrote no landed code after 8bb0841. It challenged at almost
every wake, and the repeat door sent it to "Make one real change to the code
the test calls" 7 times.** Head 8bb0841 holds from attempt 1 to 8 (observed:
`q5.py` over s520 to s565, `batches.head_commit`).

| Wake | Calls that matter | Door said |
|---|---|---|
| s527, 529, 530 (att. 3) | 8 writes to `version_option`'s package lookup; m373 challenge | span and syntax refusals; s527 cut at the output budget; quarantined after 3 wakes at s533 |
| s532 (m374) | writes to the Tester's test file | "the tests are the Tester's" |
| s538 (att. 4) | m380 challenge on tst_9 | repeat sends: "you have already sent challenge" |
| s540 (att. 5) | m381 escalate on 4 tests; m382 challenge; `ledger.log` kind `dependency_gap` | kind refused, then a fault "No page shows it" |
| s544 (m384) | `requirements.txt` "Pillow"; `schedule.reask` | "requirements.txt is a dependency manifest ... No criterion of this batch names a dependency" |
| s545, s547 (att. 5) | m385, m386 challenges on tst_9 | repeat refusals |
| s549 (att. 6) | m387 escalate on tst_9 | "3 times already (m380, m385, m386) ... Send msg.escalate_architect", then twice "Make one real change to the code the test calls." |
| s551 (m388) | 9 challenge attempts; m389 landed | bare-string refs, no criterion, paraphrased quotes |
| s555, s556 (att. 7) | m392 escalate; m393 challenge; 3 writes | "Make one real change" twice; spans refused; one write `unchanged` |
| s561 (m396) | `requirements.txt` "Pillow>=10.0.0" | the dependency door |
| s563, 564, 565 (att. 8) | m398 escalate; s563 a write to `examples/imagepipe/imagepipe.py` | "Make one real change" 4 times; "3 times already (m373, m382, m393) ... Send msg.escalate_architect"; the imagepipe write cut at the output budget, not run |

Counts on `batch_3` (observed: `messages` m373 to m398):

- Challenges landed: 7, m373, m380, m382, m385, m386, m389, m393.
- Escalations landed: 4, m381, m387, m392, m398.
- Answers to the Developer: 4. With words: 2, m384 and m396 from the Tester,
  each the criterion's text and nothing more. With refs alone: 2, m374 and m388
  from the Architect. The `[tests.load]` block shows m373 as "answered with no
  words" and m381 as "closed (answered) with no answer row".

Fit to a test: the writes at attempt 3 changed the package-name lookup so a
command with no installed package would not raise, which fits tst_9's command
and not the request. The write at s563 added `version_option` to
`imagepipe.py`, which fits the surface ref. None landed (reasoned: s527 turn 11
text "when `show_python=True` and we can't detect a package version, we should
still show something"; s563 turn 22).

Frame 200's mechanisms on this batch:

- Fired: the decorator-factory door refused 5 Tester encodes at s521 and 3 at
  s526 that read `.callback` or called a plain function. The repeat bound sent
  three challenges then the escalation, at s549 and s565. The `[tests.load]`
  block named each answer with no words. The test-file door kept the Developer
  off the Tester's files.
- Did not move the batch: "Make one real change to the code the test calls"
  points at `version_option`, which was already right, while four reds sit in
  an import the product cannot change. Answers with words stayed at 2 of 4, and
  the Vision Keeper's 2 answers to the Tester had none (reasoned: the reds are
  in `examples/imagepipe/imagepipe.py:3`, not in the code the step names).

## 5. `batch_2`'s end at m355

**`batch_2` was exhausted at attempt 10 of 10 before the page, and the
cancel then abandoned it on a contest of its item.** It would not have merged
at a next attempt (observed: s493, s494, s499 `tick:exhausted attempt 10 of
10`; log `do:cancel` after m355).

1. Exhaustion: s493 Developer, s494 Architect, s499 Vision Keeper, then s502
   `tick:agenda` sent the page m355 (observed: `sessions`).
2. The page showed line 3's check failing on the fixed versions, and the
   principal's words: "Line 3's check is wrong because it expects one of a few
   fixed Python versions ... Line 2's check is too weak ... put the version
   option on a real command" (observed: jsonl, m355, 07:23).
3. The ruling: s503 `rulings.rule` line 1 `approve`, then `revise`; lines 2 and
   3 `contest` (observed: `tool_calls` s503).
4. The relay s506 set the item `show_python_version_flag` to `contested`,
   `approved`, `contested`. The cancel then logged "abandoned
   batch_2_show_python_version_flag: its item is no longer schedulable"
   (observed: `tool_calls` s506, log).
5. Next attempt: none was left, and the red test asserts '3.12', '3.11' or
   '3.10' against a 3.14.2 interpreter. Only a rewritten test could pass it
   (observed: tr216).

This is frame 185's mechanism, a correction of a check line ruled as a
contest on the item, which abandons the batch. It is not frame 213's own sign:
the abandoned test did not stay on later pages as a check, because batch_3's
criteria are new rows `c_show_python_version*` (observed: `criteria`, page
m365 "check: none yet"). The batch itself died of a wrong Tester test held
through 10 attempts, which is frame 200's named cause one (reasoned: the
product output met the request at attempt 10).

## 6. Walk 2

`batch_1_confirm_default_on_eof` ended at 4 red after 168 steps because two
of its Tester checks stayed broken through four principal corrections. One
check never turns the flag on, and one check's call is cut off (observed: log
lines 182 to 254, the principal's words at m277, m284, m290 and m296, and
frame 200's status of 07:51). The five contested items at the end,
`how_it_works`, `echo_json_newline`, `defines_commands_and_options`,
`handles_argument_parsing` and `executes_commands`, are not the confirm item.
They are the night's survey and walk 1 items, carried as contested (observed:
the log's "Stuck" line). This read did not open walk 2's turns, so the cause
is reasoned, not observed: the broken checks are frame 200's wrong-test cause
on a second batch, and the contested carry is frames 187 and 213's shape. No
new frame is proposed from walk 2 without a turn read.

## 7. The residue rule

**The loop on `batch_3` belongs to no cause that frame 200's design named.**
The cause is a criterion repair that put the surface ref on the first row of an
unhinted candidate list, an example module that imports `PIL`, and an encode
door that forces that import and never checks that the module loads (reasoned:
sections 2 to 4). By the residue rule this batch does not hold frame 200 open,
and its cause is a new frame. The nearest open frames are 202, which names a
different sign, and 146, which checks module loads for `code.write` only.

The measure still did not see a clean run of frame 200's path. `batch_2` died
at attempt 10 on a Tester test that asserts fixed versions, frame 200's named
cause one, after 4 challenges and an escalation (observed: section 1, m331 to
m334, m348). So frame 200 does not close on night 142. One batch looped on a
new cause, and the other ran out on a named cause, at 10 attempts against the
target of 4 (reasoned: the residue rule as frame 193 wrote it).

Proposed new frame (reasoned): "A criterion repair names an example module
that does not load as the surface, and the encode door forces its import".
Site: `criterion_repair.md` lines 8 to 12, the `criteria.respecify` door, and
the surface door at `rota/roles/api.py:6812-6818`. Ends when: a respecify whose
surface is outside the item's expected files and named by no word of the
request is refused with the expected files named; the encode door refuses a
surface whose module fails to import in the sandbox and routes to the
Terminologist.

Register lines written: 0. Meta workflow.
