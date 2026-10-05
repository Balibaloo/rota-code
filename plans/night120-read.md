# Night 120 read

Night 120 ran cold from `C:/Users/roman/rota_night120` at be1eb5c, 2026-10-05 03:04 to 04:52. It holds 249 sessions, 1,060 turns and 3 batches. The night was not paused. Rota workflow throughout, except where a line says meta workflow. Database `.rota/clickI_night120.db`, log `.rota/night120.log`, report `.rota/night120_report.txt`. Scripts: the scratchpad folder `n120` of session e6218d79. Night 119's numbers are copied from `plans/night119-read-fable.md` and keep that record's mark, (observed: 2026-10-05).

be1eb5c holds frame 122's change to the parser's refusal text. It does not hold frame 121's change to the runner's notes, e54007d and later. So this night is a baseline for frame 121.

Summary:

- Two batches merged where night 119 merged one. The cause is the model's variation between two loads, and no code change. The two nights are equal byte for byte through 136 sessions. They part at the Tester s137, turn 3, where two completions differ on an equal prompt at temperature 0.
- The Tester of night 120 wrote no test that calls a plain function as a Click command for bg_1 or bg_2. It wrote two such tests for bg_3.
- bg_3 was given up for a new cause. The Developer s227 sent a span write that replaced five import lines with `import sys`, and every test went to `error` at import. Three later commits kept the package broken.
- Before that commit, bg_3 was red for the Developer's own missing `import sys`. Five of nine fix wakes showed that red project test as passing. That is frame 130.
- Frame 122's residue: 0 sessions end on a parser refusal with the frame's cause. The refusal for a value that never ends still names a wrong word in 18 refusals of 5 sessions.
- Frame 121's baseline: 3 of 9 Developer `tests_failing` sessions call `tests.load`, 0 turns hold a cut note on a reply, 7 turns hold the serve cap refusal, and 4 of 16 cut replies end on a whole call.
- A Tester stored a test under the id of a project test, and the project test did not run in the batch that merged. This is new wall 1.

## 1. Why two batches merged where night 119 merged one

**Answer: the model's variation between two loads. The Tester of night 120 wrote no test that calls a plain function as a command for bg_1 or bg_2, and the first difference between the nights is one completion on an equal prompt.**

Where the nights part (observed: `diverge.py 1 140`, 2026-10-05):

- Sessions s1 to s136 have equal prompts and equal completions on both nights, with two exceptions, s45 and s130. Neither changes a later prompt of a Tester. The nights part at s137.
- s45, turn 4: the prompt differs only in the parser's refusal text, `a quote inside about_ref ended it early and the arguments after it` on night 119 and `a quote inside assumption ended it early, and the text after that quote is not an argument` on night 120. Both sessions attested `none_found` at turn 4.
- s130, the Developer of bg_1, turn 11: the prompt differs only in the commit hash, `8b19b7f648` against `a60ed772f8`. The session has 25 turns on night 119 and 19 on night 120.
- s137, a Tester on `tick:tests_missing` for bg_1, turn 3: the completions differ at character 21 on an equal system text and an equal prompt. Both sessions ran `qwen3.5:9b` at temperature 0.0 with an equal `prompt_hash` and an equal `briefs_hash`.
- The code between 1e87855 and be1eb5c changed `rota/llm/toolproto.py` and its test files only (observed: `git diff --stat 1e87855 be1eb5c`, 2026-10-05). No prompt of a Tester before s137's turn 3 holds a parser refusal on either night.

What followed from s137's turn 3 (observed: `fresh.py`, `messages`, `tests`, 2026-10-05):

| | Night 119 | Night 120 |
|---|---|---|
| s137, turn 3 | triaged all three criteria `cannot` and asked the Terminologist, m62: "Cannot test echo_json_compact because the criterion says it prints to stdout, but I cannot capture stdout with my tools." | sent the third encode again, logged an assumption, triaged only `echo_json_compact_3` as `cannot`, and asked m62: "how should I express \"raises TypeError\" in a body that pytest can collect?" |
| The next Tester sessions | s139, on the answer m63, stored three tests | s140 stored the test of criterion 3. s143 asked m68: "I do not know whether echo_json writes to a stream or returns a string". s145, on the answer m69, stored two tests |
| Test of `echo_json_compact` | `inh_echo_json_01`: `runner.invoke(echo_json, ['{"key": "value"}'], catch_exceptions=False)` | `test_echo_json_compact_format`: sets `sys.stdout` to a `StringIO`, calls `echo_json({"key": "value", "num": 123})`, and compares the text |
| Test of `echo_json_compact_2` | `inh_echo_json_02`: `runner.invoke(echo_json, [...])` | `tst_echo_json_compact_2`: the same `StringIO` form |
| Test of `echo_json_compact_3` | `inh_echo_json_03`: wraps `echo_json` in `@command` | `inh_022b8a87`: `with pytest.raises(TypeError)` on a direct call |
| The batch | parked at 37 of 37 red after the Developer made `echo_json` a command | merged at a60ed772f8, 36 of 36 pass |

The criteria of `echo_json` are equal on both nights, three rows with equal text (observed: `criteria`, 2026-10-05). The door `the test uses what echo_json returns, and the criterion echo_json_compact says it prints` fired in both nights. On night 119 the seat answered it with `CliRunner`. On night 120 the seat answered it with a `StringIO` on `sys.stdout`.

bg_2: neither night holds a test that passes a plain function to `CliRunner.invoke`. Night 119 stored four tests that call `confirm` directly, and night 120 stored three (observed: `tests`, 2026-10-05). bg_2 merged on both nights. The criteria differ in id and text, because the nights had parted before the criteria wake.

bg_3 on night 120 holds the frame 131 sign. `tst_version_option_show_python_c2_fixed` and `tst_version_option_show_python_c3_fixed` decorate a plain function with `@version_option(...)` and call `runner.invoke(cmd, ["--help"])`. Both fail with `AttributeError: 'function' object has no attribute 'name'` at `src\click\testing.py:387` (observed: `test_runs` at 6ae763f0ac, 2026-10-05). Version 1 of `tst_version_option_show_python_c1_fixed` had the same form.

What one night's merge count means (reasoned: the two nights share 136 sessions and part on one completion with no input change):

- The count moved from 1 to 2 with no change in any input of the seat that made the difference. A single night's merge count does not measure a code change.
- The frame 131 behaviour is still present: 1 of 3 batches holds such a test on night 120, against 2 of 3 on night 119.
- A frame's measure on a night needs its own sign in the turns, as the ends-when lines of the stack rule. The merge count is not that sign.

## 2. bg_3, given up

**Cause: the Developer s227 replaced the first five lines of `src/click/decorators.py` with `import sys`, and the commit a3352d90e3 made 43 of 43 tests `error` at import. The commits cfed9d8e5d and 128f6e4967 removed more of the header. At attempt 6 three seats named the right line, `import typing as t`, and no write of the three landed.**

In order (observed: `fresh.py`, `writes.py`, `wake120.py`, `messages`, `test_runs`, 2026-10-05):

1. s213 committed 6ae763f0ac. The code uses `sys.version_info` and the file does not import `sys`. The project test `inh_dcc9ea38`, `tests/test_basic.py`, went red: `NameError("name 'sys' is not defined")`. The harness printed `bg_3: 40 test(s), 1 not passing`. The batch had no test of its own yet.
2. Attempt 1, s214, s215 and s217. The wake's `tests.load` block shows 40 rows, each `passing, not shown | pass`, and the row of `inh_dcc9ea38` is one of them. All three seats sent `msg.challenge_tester(refs=['c1_version_option_show_python', 'inh_dcc9ea38'], ...)` at turn 1. The door answered `inh_dcc9ea38 has no criterion: it is the project's own test and it passed before this batch. A challenge has no side there. Read code.diff and restore what your change broke`. No seat changed the code. s215 asked the Researcher, m117: "The harness reports \"tests_failing\" but tests.load shows all 36 tests passing."
3. The key was quarantined at 3 attempts. The Liaison s218 paged the Principal, and the Principal approved.
4. The Tester s220 stored three tests. All three passed a plain decorated function to `runner.invoke(..., ["--help"])`. The harness printed `bg_3: 43 test(s), 4 not passing`.
5. Attempt 2, s221 and s224. The wake shows the three red tests of the batch and `"passing, not shown": "40 test(s)"`. The red project test is counted with the 40. s221 called `code.source` in 14 turns, met the serve cap, and escalated, m120. s224 challenged `tst_version_option_show_python_c1_fixed`, m122, and escalated on all three tests, m123.
6. m120: the Architect s222 sent it to the Vision Keeper, m121. The Vision Keeper s223 authored the decision `d_1234567890`, then met three refusals on `msg.reopen_developer`, `problem.describe` and `problem.assert` with the test's id. Nothing came back to the Developer. The later wakes list m120 as `closed (answered) with no answer row`.
7. m122: the Tester s225 replaced the test under its id at turn 1, `OK tests.encode -> {"id": "tst_version_option_show_python_c1_fixed"}`. Version 2 adds `@click.command()`. It still asserts that the output of `--help` holds `Python` and a version number. s225 then answered with the criterion's text, m124.
8. m123: the Architect s226 filed the finding `fnd_version_option_show_python_c1` as satisfied and answered with refs and no words, m125.
9. s227, woken by m124, read the file and wrote at turn 4: "`sys` is not imported. That's the problem." The same reply sent `code.write(path='src/click/decorators.py', text='import sys\n', start=0, end=5)`. The result was `OK code.write`. The span held `from __future__ import annotations`, `import inspect`, `import typing as t` and `from functools import update_wrapper`. The commit is a3352d90e3. Every test went to `error`: `src\click\decorators.py:3: in <module>`, `R = t.TypeVar("R")`, `E   NameError: name 't' is not defined`.
10. s228, woken by m125, wrote `import sys`, `from typing import TypeVar, Callable, Any, Concatenate`, `t = TypeVar` over `start=0, end=15`. The span removed the imports from `.core`, `.globals` and `.utils`. The commit is cfed9d8e5d, with the message `Fix missing typing imports in decorators.py`. The error became `AttributeError: type object 'typing.TypeVar' has no attribute 'TypeVar'`.
11. Attempt 5, s229. The wake holds the traceback 4 times, the group block with `"count": 40`, and a `[removed lines]` part that lists `- import typing as t` and 15 more header lines. s229 named `import typing as t` in 0 replies. It wrote the same eight lines again and committed 128f6e4967. The error did not change.
12. Attempt 6, s230, s231 and s232. All three named `import typing as t`, in 10, 6 and 5 replies. No write landed in a commit:
    - s230 sent the whole file three times, turns 1 to 3. Each reply was cut at the output budget, 29,663, 25,814 and 25,793 characters. It then met `this rewrite of src/click/decorators.py drops argument, command, ...` 6 times, for a header text with `start=0, end=-1`.
    - s231 sent the whole file. The parser refused 2 calls, section 3. The third call parsed, and a door refused it 3 times: `src/click/decorators.py reaches the dynamic at line 220 (from importlib.metadata import ...)`. The seat's own text held that line.
    - s232 sent a text of `text` with no closing quote 3 times, section 3. Its commit was then refused 2 times: `this commit puts the tree back where it stood before your last commit: you are undoing yourself. The tests pass both ways`.
13. The log printed `CYCLE: period 1, rounds 3, wakes: developer|tick:tests_failing|attempt 6|["bg_3"]`. The key `developer|tick:tests_failing|bg_3` stands at `attempts=3, quarantined=1`.

Which tests are right:

- `inh_dcc9ea38`, the project's test: right. It was red for the Developer's own missing import.
- `tst_version_option_show_python_c2_fixed` and `tst_version_option_show_python_c3_fixed`: wrong. A plain function goes to `CliRunner.invoke`. No challenge on them landed, because s224's second and third challenge met `you have already sent challenge to tester; saying it again with different refs is a second answer to one question`.
- `tst_version_option_show_python_c1_fixed`, version 2: wrong against the request and right against its criterion. The criterion `c1_version_option_show_python` says "When `version_option` is invoked with `--help` or when the version flag is triggered". The ticket says "give version_option a show_python flag that appends the running Python version to the message". The output of `--help` never holds the version message.

So bg_3 does not go green when the header is put back. Three tests stay red for a cause outside the code (reasoned: the three bodies above, no run on a worktree).

Against night 119's bg_3:

| Part | Night 119 | Night 120 | Frame |
|---|---|---|---|
| A test calls a plain function as a command | `tst_v1`, `tst_v3` | 2 of 3 tests at the end, 3 of 3 at the start | 131 |
| The Developer changes the product to fit such a test | s258 made `version_option` return a `Command` | no such commit | 131, not met |
| A Tester answers a challenge in prose | s249, and the door then closed the route | not met: s225 replaced the test at turn 1. The refusal `you sent challenge to tester on exactly these refs already (m122) and they answered` in s229 and s230 is true | 132, not met |
| The Architect's answer carries no words | m142, m143 | m125. m120 got no answer row | 115 |
| A large diff block removes the source | 6 of 6 wakes at attempts 4 and 5 | 0 of 9. The diff block is at most 3,290 characters | 134, not met |
| The wake shows a red project test as passing | the other direction, 4 wakes | 5 of 9 wakes hide the one red project test | 130 |
| The fix wake's source is `CliRunner` | 10 of 10 bg_1 wakes | 6 of 6 wakes that hold a source block | wall 3 of night 119, no frame yet |
| A span write removes import lines | not met | s227 and s228, 2 commits, 43 of 43 `error` | new wall 2 |
| A criterion adds a behaviour that the request does not hold | not met | `--help` in `c1_version_option_show_python` | new wall 3 |
| The right fix is named and no write lands | s157 and s162 wrote the line back | 3 of 3 seats at attempt 6, each stopped by a cut, a door or the parser | 133 in part, new wall 2 |

Frame 114, a failing inherited test has no route: the door's answer in step 2 follows the ruling that a broken project test is the Developer's own regression (copied: `CLAUDE.md`, ruled 2026-10-03). The door named `code.diff`. The wake did not show the test as red or its output, so the seat had the door's word and no `NameError` (observed: the wake of s214, 2026-10-05).

Correction, 2026-10-05: item 10 is wrong about the `.core`, `.globals` and `.utils` imports. s227's repeated writes at turns 6, 7 and 9 removed them, uncommitted, and s228's commit cfed9d8e5d carried them. s228's 0..15 replaced its own insert and the `R` to `FC` lines (observed: `plans/frame136-design.md`, 2026-10-05).

## 3. Frame 122's residue

**The frame closed on this night. This read finds no session that ends on a parser refusal with the frame's cause, a quote inside a quote. It finds a wrong name or a wrong step in the refusal for a value that never ends.**

The measure (observed: `look120.py`, 2026-10-05):

- Parser refusals stand fresh in 13 of 249 sessions: 24 with the sign `unterminated argument list`, 4 with the new text `the text after that quote is not an argument`, 1 with the text `were read as part of`.
- Sessions with 3 fresh refusals or more: 2 of 249, s158 and s232. Night 119 had 2 of 291.
- Sessions whose last working turn is a fresh refusal: 0. s45, s80, s106 and s159 each sent a call that parsed at the next turn, and each holds a receipt (observed: `sum.py`, `receipts`, 2026-10-05).

| Session | Role, wake | Call sent, cut | Argument that never ends | Fresh refusals | Cause | Did the refusal name a step the seat could take |
|---|---|---|---|---|---|---|
| s158 | architect, `tick:survey` | `surveys.attest(outcome="none_found", citations=["examples/complex/complex/commands/cmd_status.py", ...` and then file names that repeat, `"tests/test_utils/test__lazyfile.py", "tests/test_utils/test__sentinel.py", "tests/test_utils/test__expand_args.py", "tests/test_utils/test__format_filename.py"`, to the end of the reply | `citations`, a list | 13, over 8 turns | a repetition loop that ran to the output budget in 7 replies of 33,099 to 33,296 characters. In turns 2 and 10 the seat copied the runner's line `CUT this exchange: ...` into its own call | no. The text is `a quote inside a quoted argument ended the string early, or a bracket is unbalanced. Source has quotes of its own: put it between triple quotes, text='''...'''`. The call holds no `text` and no stray quote. The line `ERROR reply cut: ... Send less in one reply` in the same result names the step. The seat sent the long list in 7 more turns, and attested with a short list of real paths at turn 15 |
| s231 | developer, `tick:tests_failing` attempt 6 | turn 1: `code.write(path='src/click/decorators.py', text='from __future__ import annotations\n\nimport inspect\n...` ending `return decorator', start=0, end=-1)`. Turn 2: the same file as `text="""from __future__ ...""", start=0, end=-1)` | `text` | 2, turns 1 and 2 | turn 1: the docstring line `append the running Python interpreter\\'s` has two backslashes before the quote, so the quote closes the value. Turn 2: the file holds `"""` 16 times, and the first docstring closes the value | in part. The text names triple quotes and writes `text='''...'''`, and it does not name the argument at fault. The seat took three double quotes. At turn 3 it removed every docstring from its text, and the call parsed |
| s232 | developer, `tick:tests_failing` attempt 6 | turn 1: `code.write(path='src/click/decorators.py', text='from __future__ import annotations\n...` ending `:return: A new function that receives the context as first argument.\n    """,\nstart=0, end=-1)`. Turns 2 and 3: the same with `text='''from __future__ ...` and the same end | `text` | 3, turns 1 to 3 | the value has no closing quote. The seat ends the value with the docstring's `"""` and writes `,` and `start=0, end=-1)` after it. The text also stops inside `pass_context`, 996 characters | in part. The text is `the value of text never ends. Either a quote inside text closed it early, or its closing quote has a backslash before it. Put a value ... between triple quotes`. It names `text`. Neither cause it names is the cause. The seat opened with three single quotes at turn 2 and did not close with them. At turn 4 it left the write and read the source |

Notes:

- s231 and s232 are in wall 8 of night 119, a Developer's `code.write` that never ends for a cause that is not a quote in a quote. Night 120 adds two causes: two backslashes before a quote, and a value with no closing quote.
- s143, a Tester, turn 3: the first `tests.encode` of the reply has a `body` with no closing quote, and a second `TOOL: tests.encode(` line follows. The refusal is `unterminated argument list: the value of parsed never ends`, with the form `parsed='''the text, with its quotes and line breaks as they are'''`. `parsed` is a variable in the body of the second call. It is no parameter of `tests.encode` (observed: the completion and the next prompt, 2026-10-05). The seat stored the first test at a later turn.
- The old text with no argument's name stands in 17 refusals of 4 sessions: s106 1, s158 13, s223 1, s231 2. In s106 one list item lacks its closing quote, and in s223 a positional string lacks it. Both seats sent a whole call at the next turn or the turn after.

s146, the Critic on `tick:review` of bg_1 (observed: `sum.py s146 s147 s148`, `verdicts`, 2026-10-05):

1. Turn 1 sent three calls. `verdicts.claim_encodes(criterion_id='echo_json_compact_3', encodes=False)` landed. `msg.challenge_tester(refs=['inh_022b8a87'], ...)` was refused, because the refs named no criterion. `verdicts.emit(batch_id='bg_1', result='fail', failed_criterion='echo_json_compact_3', reason='The criterion ... behavior "consistent with ... The test passes, but the criterion's specific wording ...` met the new text: `a quote inside reason ended it early, and the text after that quote is not an argument. Put the value of reason between triple quotes`.
2. The argument at fault is `reason`, and the refusal names it. The stray quote is the apostrophe in `criterion's`.
3. Turn 2 sent `reason='''...'''`, and the call parsed. The challenge landed first, m70, and a door then refused the verdict: `you have already challenged the tester this session, and that is your judgement of this commit until the challenge lands`.
4. The batch got its verdict from another session. The Tester s147 answered the challenge, m71. The Critic s148, woken by m71, stored `critic:bg_1:a60ed772f8...` with `pass` at turn 1.
5. The refusal cost no turn and no outcome. Turn 2 was owed for the refused challenge. Without the refusal, the `fail` verdict lands at turn 1 on a test that the same Critic disputes (reasoned: the challenge of turn 1 did not land, so the door of step 3 does not fire).

The new text that names the argument moved the seat in 4 of 4 sessions that met it: s45, s130, s146 and s178 each sent a call that parsed at the next turn, or left the call (observed: `look120.py`, 2026-10-05).

## 4. Frame 121's baseline on this night

The definitions are those of `scratchpad/f121p1/baseline.py`. The script `base121.py` gives night 119's numbers again when it reads night 119's database: 12 of 20 and 33 turns, 8 turns in 2 sessions, 24 turns (observed: 2026-10-05).

| Count | Night 119 | Night 120 |
|---|---|---|
| Developer `tests_failing` sessions that call `tests.load` after the wake | 12 of 20, in 33 turns | 3 of 9, in 3 turns: s215, s221, s232 |
| Turns whose prompt holds a cut note on a reply, `CUT your wake` and then `ERROR reply cut:` | 8 turns, 2 sessions, 0 end within two turns | 0 turns, 0 sessions |
| Turns whose prompt holds `served three times this session` | 24 turns, `tests.load` 23 and `criteria.load` 6, s260 and s261 | 7 turns, all `code.source`, all in s221 |
| Turns whose prompt holds `ERROR reply cut` | not counted in that record | 35 turns in 8 sessions |

Details (observed: `base121.py`, 2026-10-05):

- `tests.load`: s215's call did not run, `NOT RUN, because you wrote a tool result of your own ahead of them`. s221's call returned the rows with their bodies and took the room of `criteria.load` in that turn. s232 called it at turn 22.
- The serve cap in s221: `ERROR code.source: served three times this session, and the window took it each time; not served again. Ask code.source for a narrower span, or finish without it.` `code.source` takes a span, so the sentence names a real step. The seat sent the same span at turns 11 and 12, and then sent `start=420, end=500` at turn 13, which was served. e54007d leaves this sentence as it is for `code.source` (copied: frame 121's status of 2026-10-05 03:51).
- The count `CUT your wake` past turn 1 gives 1 turn, in s158. It is a cut of the wake that moved in the prompt. It is not a note on a reply.
- `ERROR reply cut`: the 35 turns hold 16 fresh cut events, and all 16 are the form for a reply with calls. The last parsed call of the cut reply was whole in 4: s32 turn 5 and turn 10, s175 turn 7, s229 turn 15. It was broken in 12: s24 2, s40 1, s70 1, s158 7, s230 1. The old line says `the last call did not run` in all 16, so it is false in 4 of 16. The parser of the tree at f23d0c6 read the replies.
- The old measure, the repeat answer beside the eviction notice: 14 turns in 4 sessions, against 56 turns in 12 sessions on night 119.

## 5. Counts the other frames track

- Frame 113: `made up: 85 turns, 38 sessions (architect 5, critic 3, developer 11, terminologist 3, tester 4, vision_keeper 12)`. `ran anyway: 0 writes after an invention (4 turns with a write result), 6 with a landed commit, shas 6ae763f0 a3352d90 cfed9d8e` (observed: the log, 2026-10-05). Night 119: 119 turns, 53 sessions, developer 22.
- Frame 115: 1 of 1 Architect answers to a Developer has no text, m125. The other escalation, m120, got no answer row. Night 119: 6 of 6 (observed: `messages`, 2026-10-05).
- Frame 116: 1 of 9 `tests_failing` sessions sent more than one challenge in a reply, s224, with 2 at turn 5 and 3 at turn 8. 0 of 9 had a challenge refused `on exactly these refs already` three times or more. Night 119: 5 of 20 and 5 of 20 (observed: `counts.py`, 2026-10-05).
- Frame 117: 52 turns in 13 sessions hold `[your reply of an earlier turn]`, a count of the sign only. Night 119: 51 turns in 14 sessions.
- Frame 126: 0 of 2 Tester challenge sessions end on the literal door, s147 and s225. The door fired in 4 Tester sessions, s137, s140, s143 and s145, all in modes that hold `ledger.log`. Night 119: 0 of 5.
- Frame 127: 3 of 9 Developer `tests_failing` wakes hold no `code.source` block, s214, s215 and s217. The cause is not the size of the red rows. Those wakes are 11,234 to 11,396 characters, are not cut, and show no red row, which is frame 130. Night 119: 6 of 20 (observed: `wake120.py`, 2026-10-05).
- Frame 128: 0 Tester challenge sessions on a project test. s147 worked on `inh_022b8a87`, which then held the Tester's own test under a project test's id, new wall 1. Night 119: 0.
- Frame 129: 4 of 4 Vision Keeper challenge sessions call `problem.assert` after `decisions.author`: s163, s197, s205, s223. 0 of 4 leave a new in-scope item, and `receipts` holds no `items` row from the four. Night 119: 5 of 6 and 1 of 6.
- Frame 130: 3 of 9 Developer `tests_failing` wakes show no red row, s214, s215 and s217, while `inh_dcc9ea38` is red. 2 more, s221 and s224, count that test in `"passing, not shown": "40 test(s)"`. Night 119: 0 of 20 by this sign, and 4 wakes with the fault in the other direction. The cause is another batch's run (reasoned: `test_runs` holds a `pass` of `inh_dcc9ea38` in bg_1 at attempt 4 and in bg_2 at attempt 2, and the wake shows the test as red only from bg_3's attempt 5).
- Frame 131: 0 of 3 batches were parked or given up after a Developer commit that turns a function into a command. Night 119: 2 of 3. The tests are present: 2 of 3 tests of bg_3, and bg_3 is the batch given up. Its cause is not such a commit, section 2.
- Frame 132: 1 of 2 Tester challenge sessions end with no encode after a reply that holds a test body, s147. Night 119: 1 of 5. s147 answered a Critic. It judged the test right, and the Critic s148 then passed the batch. 0 Developer refusals cite a challenge that closed with no call.
- Frame 133: 0 commits say that they remove a line and keep it. The night did not meet the frame. Night 119: 10 of 10 on bg_1. A near case: s229 had `- import typing as t` in its wake and named the line in 0 replies.
- Frame 134: 0 of 9 Developer `tests_failing` wakes hold no source for a cut that falls before `tests.load` ends. The `code.diff` block is 1,862 to 3,290 characters. Night 119: 6 of 20.

## 6. New walls

Each wall was checked against the open frames 113 to 134 and against the eleven walls of `plans/night119-read-fable.md`. Three signs of that record stand again and are not listed as new: the fix wake's source is `CliRunner` in 6 of 6 wakes that hold a source block, wall 3; a Developer's `code.write` never ends for a cause that is not a quote in a quote, s231 and s232, wall 8; a Critic stored `falsified` with no line quoted, `items:confirm_with_default_on_eof`, "The claimed function confirm() does not exist in the codebase", as s192 did.

1. **A Tester stores its test under the id of a project test, and the project test's row is replaced.** Sign: `tests.encode(id='inh_022b8a87', criterion_id='echo_json_compact_3', path='tests/test_utils/test_echo_json.py', ...)` and `OK tests.encode -> {"id": "inh_022b8a87"}` in s140, turn 5. `inh_022b8a87` is the row of `tests/test_utils/test_confirm.py`. The harness count stayed at `bg_1: 34 test(s)` after the encode. The run of `inh_022b8a87` in bg_1 says `1 passed`, and in bg_2 it says `2 passed`. So the project's test did not run under its row in the batch that merged. s140 had sent `id='inh_01fdb170'`, another project test's id, in 4 calls before. Count: 1 session, 1 row, 1 merged batch. Night 119 held the prefix alone, as a note. Proposed ends-when: `tests.encode` refuses an id that is a row with no criterion, with one sandbox test on s140's call, and encodes that land on such an id fall from 1 of 10 stored tests.
2. **A span write that adds one line removes the import lines of the span, and the door admits it.** Sign: `code.write(path='src/click/decorators.py', text='import sys\n', start=0, end=5)` and `OK code.write` in s227, turn 4, then `NameError: name 't' is not defined` in 43 of 43 runs at a3352d90e3. s228 did the same with `start=0, end=15`. At attempt 6, 3 of 3 seats named `import typing as t` and 0 writes landed: the door `this rewrite of src/click/decorators.py drops argument, command, ...` fired at least 11 times in s228 to s232, most for a header text sent with `end=-1`. Count: 2 commits, 1 batch given up. Proposed ends-when: a write whose result leaves a module-level name with no binding, where the file bound it before, is refused with the lines it removes, and batches red at import after a landed write fall from 1 of 3.
3. **A criterion holds a behaviour that the request does not hold.** Sign: "invoked with `--help` or when the version flag is triggered" in `c1_version_option_show_python`, against the ticket "appends the running Python version to the message". The test `tst_version_option_show_python_c1_fixed` asserts on the output of `--help` in both versions. Two escalations on the test returned no words. Count: 1 criterion, 1 test that no code makes pass. Proposed ends-when: the cause is read from s204's turns, and criteria that name an invocation the ticket does not name fall from 1 of 9.
4. **The refusal for a value that never ends names a word that is no parameter, or names `text` for a call with no `text`.** Sign: `the value of parsed never ends` on `tests.encode` in s143, and `put it between triple quotes, text='''...'''` on `surveys.attest`, `msg.present_principal` and `decisions.author`. Count: 18 refusals in 5 sessions: s106 1, s143 1, s158 13, s223 1, s231 2. Proposed ends-when: the refusal names only a parameter of the called function, and it says that the reply was cut when the output budget ended the call; sessions that send the same call after it fall from 2 of 5, s158 and s231.
5. **The revert door says that the tests pass both ways when every test is in error.** Sign: `this commit puts the tree back where it stood before your last commit: you are undoing yourself. The tests pass both ways, so the disagreement is not in the code` in s232, turns 13 and 15, while 43 of 43 runs are `error` at cfed9d8e5d and at 128f6e4967. The tree that s232 tried to commit held s230's write, which no commit held. Count: 2 refusals, 1 session. Proposed ends-when: the door's sentence follows the runs of the two commits, and a commit that goes back from a red-at-import head is not refused; one api test.

One note, not a wall: the Developer's first fix wakes on bg_3 ran before the batch had a test. Three attempts and one page to the Principal were spent on one project test that the wake showed as passing. Frame 130 holds the cause.

## Not read

- Why the parser gave the old text with no argument's name for s231's turn 1, where the value opens as `text='`. The naming function was not run on the reply.
- Whether bg_3 goes green when the header is put back and `import sys` is added. No test ran on a worktree. The claim that three tests stay red is reasoned from their bodies.
- The criteria wake s204 past its call list: why `--help` entered `c1_version_option_show_python`.
- Whether the Developer's code of bg_1 differs between the nights after s130. The first difference in s130 is the commit hash, and the later turns were not compared.
- Why `tests.load` and the wake rank another batch's run above bg_3's. The claim in section 5 is reasoned from `test_runs`, and the query was not run.
- Frames 117 and 121's old measure: the counts are of the sign. Whether each stubbed reply held a call, and whether each seat repeated its call, are not read.
- The Researcher s216's answer to m117, the Architect sessions s210 and s226 past their call lists, and the Developer s229's turns 8 to 15.
- bg_2's Developer s178 past its call list. It sent `code.write(path='tests/test_defaults.py', ...)` three times, and each was refused for a cause other than the test-file door.
- Whether the Critic's `falsified` on `items:confirm_with_default_on_eof` changed anything after bg_2 merged.
