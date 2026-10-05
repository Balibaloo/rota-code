# Night 121 read

Night 121 ran cold from `C:/Users/roman/rota_night121` at 8151d87, 2026-10-05 05:35 to 09:05. It holds 382 sessions, 1,979 turns and 3 batches. Rota workflow throughout, except where a line says meta workflow. Database `.rota/clickI_night121.db`, log `.rota/night121.log`, report `.rota/night121_report.txt`. Scripts: the scratchpad folder `n121` of session 5101d8d0. The read called no model and ran no test. The numbers of nights 119 and 120 in sections 1 and 4 come from the same scripts on those databases, (observed: 2026-10-05). A number that another record gave is marked (copied) and keeps that record's mark.

8151d87 holds frame 121's change to the runner's notes. It does not hold frame 135's door on `tests.encode`, a71951a. So this night is the walk of frame 121 and a second baseline for frame 135.

Summary:

- Frame 121, two runner notes say what happened: the turns show no false claim in a note. The cut line is true in 36 of 36 cut events. The new serve cap sentence for a call with no bound met 0 turns, so the night does not measure that sentence.
- The serve cap refusal on `code.source`, whose bytes did not change, is followed by the same call in 8 of 13 refusals. The cause is a read loop of two spans in a full window, and the refusal's claim is true each time.
- No batch merged. bg_1 was parked past the attempt cap, bg_2 was given up on `tests_failing`, and bg_3 stood `running` at 7 of 40 red when the walk went quiet.
- bg_1 repeats night 119: a test passes a plain function to `CliRunner.invoke`, and the Developer made `echo_json` a command. That is frame 131.
- bg_2 broke at its first commit. A span write ended before the function's end and dropped 13 lines of `confirm()`. The write's `dropped` note came back in the same results block as the commit. Then 16 of 16 fix wakes of bg_2 showed the two red project tests as passing, frame 130.
- bg_3 broke when the Developer made `version_option` return an `Option` to fit four tests that call `.callback` on a decorator. A door refused the Tester's repair three times.
- The `CYCLE: period 5` line is a park ask that the walk's principal answered with a sentence of another request. The Liaison asked three times and made three equal statements.
- The night parts from night 120 at s24, turn 2, on the new cut line. The cause is the code change this time, and not the model's variation.

## 1. Frame 121, two runner notes say what happened

**Verdict: no. The turns of night 121 show no false claim in the serve cap refusal or in a cut line. Each session that repeats a call after a note has a cause that is not the note's claim.**

### Measure 1, the serve cap refusal

A refusal is fresh when it stands in the results part that follows the seat's last reply (observed: `servecap.py 119 120 121`, 2026-10-05).

| | Night 119 | Night 120 | Night 121 |
|---|---|---|---|
| Turns whose prompt holds the refusal | 24 | 7 | 21 |
| Fresh refusals, sessions | 7, s260 and s261 | 3, s221 | 13, in 7 sessions |
| Refused call | `tests.load` 5, `criteria.load` 2 | `code.source` 3 | `code.source` 13 |
| Text of the step | old: `Ask tests.load for a narrower span`, false, the call takes no span | `Ask code.source for a narrower span`, true | `Ask code.source for a narrower span`, the same bytes |
| Reply sends the same call again | 0 of 7 | 1 of 3 | 8 of 13 |
| Reply sends the same function with another span | 0 | 1 | 3 |
| Reply sends another call | 7 | 1 | 2 |
| Reply sends no call | 0 | 0 | 0 |

- The new sentence, `Your prompt does not hold this result, and the window cannot hold it. Act without it, or finish.`, stands in 0 prompts of night 121. `a smaller limit` stands in 0 prompts. No session met the serve cap on a call with no span (observed: `grepc.py`, 2026-10-05). Night 122 runs the same code and is the next chance.
- Same call again, by session, night 121: s306 2 of 2, s307 2 of 2, s315 2 of 2, s308 1 of 3, s323 1 of 2, s305 0 of 1, s249 0 of 1. All seven are Developer `tests_failing` sessions, six on bg_3.
- On night 119, s261 came back to `tests.load` at turn 23 after the refusals of turns 10 and 12. The count above reads only the reply that follows each refusal.

### Measure 2, the cut events

A cut event is a fresh `ERROR reply cut` line. The truth test reads the cut reply with the parser of the tree and reads the `OK`, `ERROR` and `NOT RUN` lines that follow the line (observed: `cut.py 121 v`, 2026-10-05). On night 121 every reply of 15,000 characters or more that has a cut line in the next prompt is an event.

| | Night 119 | Night 120 | Night 121 |
|---|---|---|---|
| Cut events, sessions | 19 in 14, and 2 more replies of s263 not classed | 19 in 8 | 36 in 22 |
| Form `The cut fell after the last call` | old line | old line | 22, last call whole in 22 |
| Form `The cut fell inside the last call` | old line | old line | 5, last call broken in 5 |
| Form `It held no whole call` with `CUT your reply` | 2, old words | 0 | 9, no call parsed in 9 |
| The line's claim is false | 13 of 17, `the last call did not run` on a whole call | 5 of 19: s32 three, s175, s229 | 0 of 36 |
| Next reply repeats a whole call of the cut reply | 5 of 19: s32 two, s187 two, s243 | 2 of 18 read: s32 two | 5 of 36 |
| Next reply repeats a call that the line says ran | not said by the old line | not said | 3 of 36 |

- Night 120's record counts 16 events and 4 false (copied: `plans/night120-read.md`, section 4, observed 2026-10-05). This read finds 19, because it reads the fresh results part and not the count of lines. s229's event is taken from that record.
- In the 22 `after` events at least one result line follows the cut line. In 4 of them a `NOT RUN` line stands for calls after a made-up result, so `the calls that ran` is the true form.
- After the 9 `CUT your reply` notes, 9 of 9 next replies hold one call. On night 119, s247 sent three calls and s263 sent no call and then two more replies past 36,000 characters.
- The closing account of a session keeps the old sentence, `so the last call did not run and nothing was written`, in 22 sessions of night 121. 0 prompts hold it, so no seat read it (observed: `turns`, 2026-10-05).

### Measure 3, each session that repeats after a note

| Session | Note | What it repeated | Cause | False claim in the note |
|---|---|---|---|---|
| s306, s307, s308, s315, s323 | serve cap on `code.source`, span text | `code.source(path='src/click/decorators.py', start=420, end=580)` or `end=514`, 8 times | a read loop. The fix wake takes 18,182 to 25,637 of 27,094 characters and is cut, `CUT your wake`. The seat reads lines 0 to 400 and then lines 420 to 580. Each read drops the other, `the earlier answer was dropped to fit the window ... ran again`, three times, and then the cap refuses. The prompt holds no result of the refused span in 13 of 13 refusals | no. The sentence is true, and the step is real: s305 and s308 took a narrower span in 3 of 13 |
| s40, Vision Keeper | cut line, `inside` | `code.source(path='docs/testing.md', start=6000, end=6400)`, call 21 of 304 | the result line of that call says `ran, and this turn has no room left for its result (20,000 characters of results already). Ask for it again in your next turn, on its own`. The seat did so | no |
| s163, Developer, turn 22 | cut line, `inside` | `code.source(path='src/click/utils.py', start=688, end=705)` | the call did not run: `NOT RUN, because you wrote a tool result of your own ahead of them`. The note says to send the rest again | no |
| s209, s222, s327 | cut line, `after` | the one whole call of the cut reply, a `code.source` | the reply held made-up result lines, frame 113. The line `You wrote tool results into your own reply ... Those did not come from me and nothing behind them ran` stands between the cut line and the real result. In s222 the real result was an empty text, `"start": 49, "end": 49`. Each repeat cost one turn, `unchanged since you asked earlier` | no, for the cut line. What the seat read in the made-up-result line is not known (reasoned: three of three repeats hold that line, no interview) |

In s307 and s308 the cut replies are one `code.source` call and 36,000 characters of prose that say the same thought again. Those replies fill the window and add to the loop (observed: `v.py 121 s307 4`, 2026-10-05).

### The old measure's baselines

| Count | Night 119 | Night 120 | Night 121 |
|---|---|---|---|
| Developer `tests_failing` sessions that call `tests.load` after the wake | 12 of 20, 33 turns (copied) | 3 of 9, 3 turns (copied) | 17 of 39, 38 turns |
| Turns with `The answer is in this prompt.` beside the eviction notice | 56 in 12 sessions (copied) | 14 in 4 sessions (copied) | 105 in 26 sessions |

(observed: `base121.py`, `counts.py`, 2026-10-05; the copied numbers are from `plans/night120-read.md`, sections 4.)

## 2. The batches

**bg_1, `echo_json`: parked past the attempt cap at 3 of 37 red. Cause: frame 131. One of three tests passes a plain function to `CliRunner.invoke`, a second wraps it with `command(echo_json)`, and the Developer made the function a command.**

1. s130 added `echo_json` as a plain function at ea0ce5f5a6 (observed: `trace.py`, 2026-10-05).
2. The Tester s139 stored three tests. `inh_echo_json_01` calls `runner.invoke(echo_json, ['{"key": "value"}'], catch_exceptions=False)` and fails with `KeyError: 'prog_name'`. `inh_echo_json_02` calls `runner.invoke(command(echo_json), ...)`.
3. s140 and s142 challenged tests 03 and 01, m64 and m65. The Tester s141 replaced test 03. The Tester s143 sent `inh_echo_json_01_fixed` four times, each refused, and answered with the criterion. Test 01 stayed at version 1.
4. s144, turn 16, committed ee54cc18a1, `Make echo_json a Click command to fix CliRunner.invoke compatibility`. No commit broke a project test. The batch was red from its tests.
5. Nine more commits by s152, s153, s156 and s163 kept 3 of 37 red to the head f21ce69fc2. The log printed `do:park: deferred bg_1; its ladder is spent`.

**bg_2, `confirm_default_on_eof`: given up on `tests_failing` at 7 of 40 red. Cause: the first commit dropped the end of `confirm()`, the fix wakes hid the two project tests it broke, and four tests of the Tester assert a default that the function does not have.**

1. First break: s212, turn 3, sent `code.write(path='src/click/termui.py', text='def confirm(...', start=288, end=345)` and `code.commit(message='Add default_on_eof flag to confirm()')` in one reply. The text ended at `raise Abort() from None`. The results came back together: `OK code.write -> {... "dropped": "This write drops 13 lines that came after `raise Abort() from None`, from `if value in (\"y\", \"yes\"):`." ...}` and `OK code.commit -> {"committed": true, "head_commit": "52862f7ad4..."}`. The project tests `inh_022b8a87` and `inh_51d478df` went red, `assert not SystemExit(1)` (observed: `writes.py`, `test_runs`, 2026-10-05).
2. What the seat was shown: the wakes of s213 and s214 hold 34 rows, each `passing, not shown | pass`. s213 sent no write. s214 wrote "all tests in `tests.load` show as \"passing\". This is contradictory to the wake message" and challenged `inh_022b8a87`. The door answered `it is the project's own test and it passed before this batch. A challenge has no side there. Read code.diff and restore what your change broke`.
3. s214 escalated, m120. The Architect answered with refs and no words, m121. s216 wrote four lines at `start=340, end=341` and committed d6cb46cf4c. Both project tests then ended `timed out after 120s`.
4. s219 landed a second write with the note, `This write drops 3 lines`, in bd44b84493. No commit put the 13 lines back. The two project tests are red at all five heads.
5. The Tester s245 stored five tests. Four call `confirm("Yes or no?", default_on_eof=True)` and hold `assert result is True  # Default value for yes/no is True/False`. The default is `False`, so the four fail with `assert False is True`.
6. s246 challenged `tst_confirm_eof_cr3`, m139. The Tester s247 named the fault and wrote the right body in prose, `default=False` and `assert result is False`. It sent no call, and the session has one turn. That is frame 132.
7. The key `developer|tick:tests_failing|bg_2` stands at `attempts=3, quarantined=1`. The Principal approved three quarantine pages before that.

**bg_3, `version_option_show_python`: not merged, not parked. It stands `running` at 62e1a9fb1f with 7 of 40 red. Cause: the Developer changed what `version_option` returns to fit a wrong test, and the Tester's repair did not land.**

1. s297 committed 974060bedb, and 34 of 34 tests passed.
2. The Tester s300 stored four tests that call `.callback` on what `version_option(...)` returns: `AttributeError: 'function' object has no attribute 'callback'`, 4 of 38 red.
3. First break: s305, turn 8, wrote lines 571 to 581 and committed e098fe9daf, `Fix version_option to return an Option object directly instead of a decorator`. The project test `inh_dcc9ea38`, `tests/test_basic.py`, went red and stayed red at each of the 7 later heads that ran. s305's wake showed the `callback` error and a `code.source` block.
4. s303 challenged `vopt_cr1`, m198. The Tester s304 sent a body with `@click.command()` and `@click.version_option(version="1.0", show_python=False)` three times. The door refused each: `the surface 'src/click/decorators.py::version_option' lives in decorators.py and this test imports from click. Import the surface from its own module`. The seat answered with the criterion's text. New wall 2.
5. The six tests at the night's end import `version_option` alone, decorate a plain function with it, and call `runner.invoke(cli, ["--help"])`. Each asserts on a `Usage:` line. That is frame 131's sign in 6 of 6 tests.
6. Eight more commits followed, and 7 of 40 stayed red from d71fdc875e. The errors moved from `Name '{name}' defined twice` to `'Option' object has no attribute 'name'` to `UnboundLocalError: cannot access local variable 'message'` at the head.
7. The ladder ran: s329, s333 and s338 on `tick:exhausted`. s342 then committed 62e1a9fb1f on a message wake. The harness printed 7 not passing, no wake followed, and `tick_attempts` holds no key of bg_3.

## 3. The cycle on the park ask

**Cause: the walk's principal answered the park ask of bg_2 with the stock sentence of walk 3, which names neither option. The wake did not clear, and the Liaison took the sentence as a new request each time.**

Each of the three rounds has five wakes (observed: the turns of s277 to s291, `messages`, 2026-10-05):

1. `tick:park_ask`, s277, s282, s287: `msg.clarify_principal(refs=["confirm_default_on_eof"], question="The change on bg_2 is parked. ... Do you want a commit that fixes the change, or a contest of confirm_default_on_eof?")`. The second and third wake say `This is attempt 2 of 3 on this wake ... Do something the earlier attempt did not`, and the seat sent the same question.
2. The principal answered "the Python version comes from sys.version_info as major.minor.micro". s278, s283 and s288 sent `rulings.rule(ask="The page asks about two options: ...")`, m167, m175, m183. s278 first sent eight approvals, refused: `this page is a park ask, and it has no line to rule`.
3. The principal sent the same sentence again. s279, s284 and s289 called `brief.intake(verdict='work')`, `brief.segment(...)` and `msg.confirm_principal`. They committed the statements `s4`, `s5` and `s6`, all with that one sentence.
4. The principal said "yes that all looks right, go ahead". s280, s285 and s290 stored a ruling each.
5. On the verdict, s281, s286 and s291 ratified the statement and delivered it to the Vision Keeper, the Terminologist and the Architect.

Count: 15 sessions, 3 park asks, 3 re-asks, 3 equal statements ratified, 3 rulings, 9 deliveries. The key `liaison|tick:park_ask|confirm_default_on_eof,bg_2` stands at `attempts=3, quarantined=1`. The reports on `s4`, `s5` and `s6` are open at the night's end, and `liaison|tick:round_close|t_p1` is quarantined too.

Two workflows meet here. The scripted principal is the meta workflow, and its script holds no answer to a park ask. The Liaison's acts are the rota workflow: an answer that names no option is asked again with the same words, and a sentence that the brief already holds becomes a new statement. The log holds four more `CYCLE: period 1, rounds 3` lines, all on `developer|tick:tests_failing`. They are the three attempts of one fix wake, and they were not read as cycles.

## 4. Where this night parts from night 120

The two nights are equal byte for byte through s23. They part at s24, a Vision Keeper on `tick:reconcile`, turn 2. The prompts differ at character 17,710, where night 120 holds `so the last call did not run and nothing was written` and night 121 holds `The cut fell inside the last call, so that call did not run. The results of the calls before it that ran follow.` The same difference stands in s32, s40 and s70. s24 has 11 turns on night 120 and 9 on night 121, and s40's second reply is `ledger.log` on night 120 and `code.source` on night 121. The ledger rows of those sessions differ, so every Liaison agenda from s88 differs, 52 open rows against 56. So the cause of the parting is frame 121's change, and not the model's variation on an equal prompt as between nights 119 and 120 (observed: `diverge.py 1 150 120 121`, 2026-10-05). After s88 the two nights are different nights. A count of this night against night 120 is two samples and not a measure of the change (reasoned: the prompts differ from s88 on, so the later sessions do not pair).

## 5. Counts the open frames track

- Frame 113, a Developer writes its own tool results: `made up: 163 turns, 74 sessions (architect 7, critic 2, developer 36, liaison 2, terminologist 3, tester 5, vision_keeper 19)`. `ran anyway: 2 writes after an invention (4 turns with a write result), 5 with a landed commit` (observed: the log, 2026-10-05). Night 120: 85 turns, 38 sessions, developer 11 (copied).
- Frame 115, the Architect's answer carries no words: 9 of 9 answers to a Developer have no text. Night 120: 1 of 1 (copied).
- Frame 116, one challenge per red test in a reply: 5 of 39 `tests_failing` sessions sent more than one challenge in a reply, s144, s153, s160, s163 and s303. s303 sent 13 in one reply. 4 of 39 met `on exactly these refs already` three times or more. Night 120: 1 of 9 and 0 of 9 (copied).
- Frame 117, a stub stubs again to no call: 93 turns in 27 sessions hold `[your reply of an earlier turn]`, a count of the sign only. Night 120: 52 in 13 (copied).
- Frame 126, the literal door in challenge mode: 0 of 7 Tester challenge sessions end on the literal door. The door fired in s137, s139, s226, s245, s300 and s321, none in challenge mode. Night 120: 0 of 2 (copied).
- Frame 127, red rows carry whole bodies: 17 of 39 Developer `tests_failing` wakes hold no `code.source` block. 9 are bg_3's wakes at attempts 4 to 9: the `tests.load` block is 11,189 to 11,613 characters and the wake is cut, 23,287 to 28,944 characters not shown. That is the frame's cause. 8 are bg_2's wakes at attempts 1 to 3, about 11,400 characters, not cut, with a `code.diff` block and no red row, which is frame 130's shape. Night 120: 3 of 9 (copied).
- Frame 128, a Tester fixes an inherited test: 0 Tester challenge sessions on a project test. The one challenge on a project test, s214's, was refused at the door. Night 120: 0 (copied).
- Frame 129, a Vision Keeper asserts after it authors: 8 of 8 challenge sessions call `problem.assert` after `decisions.author`: s147, s162, s187, s207, s238, s257, s275, s355. 0 of 8 leave a new in-scope item. One item came from a propose wake, `bg_1_summary` by s166, and the Liaison then asked the Principal about it, m212. Night 120: 4 of 4 and 0 of 4 (copied).
- Frame 130, a red project test shown as passing: 8 of 39 wakes show no red row, bg_2's attempts 1 to 3, while two project tests are red. The 8 later wakes of bg_2 count the two tests in `"passing, not shown": "34 test(s)"`. So 16 of 16 wakes of bg_2 hide them. bg_1's runs of both tests are `pass` at attempt 10, above bg_2's attempts 1 to 7 (observed: `test_runs`, 2026-10-05; the ranking by attempt is reasoned from those rows). Night 120: 3 of 9 and 2 more (copied).
- Frame 131, a plain function as a command: 1 of 3 batches was parked after a Developer commit that makes a function a command, bg_1. bg_3 holds the related act, a decorator changed to return an `Option`. 7 of 15 stored tests pass a function with no `@command` to `runner.invoke`: `inh_echo_json_01` and the six of bg_3. Night 120: 0 of 3 batches, 2 of 3 tests of bg_3 (copied).
- Frame 132, a Tester answers in prose: 2 of 7 Tester challenge sessions hold a test body in a reply and send no `tests.encode`, s247 and s331. 2 more sent the encode and every send was refused, s143 and s304. Night 120: 1 of 2 (copied).
- Frame 133, a line written back: 0 commits say that they remove a line and keep it. s332 sent `Fix TypeError by removing show_python from kwargs passed to Option` five times, and its diff was not read. Night 120: 0 (copied).
- Frame 134, a large diff block: 0 of 39 wakes. The `code.diff` block is at most 2,564 characters. Night 120: 0 of 9 (copied).
- Frame 135, an encode under a project test's id: 0 calls send an id of the form `inh_` and eight hex characters, and 0 project rows hold a Tester's body. 0 of 0 merged batches. This night gives the door of a71951a no case. 4 of 15 stored tests have an id that the Tester made with the prefix `inh_`: `inh_echo_json_01`, `_02`, `_03` and `inh_confirm_default_on_eof`. Night 120: 1 of 10 stored tests and 1 of 2 merged batches (copied).
- Frame 136, a span write removes import lines: 0 landed span writes start in the first 30 lines, and 0 runs are in `error` at import. The 2 `error` runs are the timeouts of bg_2. 0 of 2 stuck batches have that cause. Night 120: 1 of 1 (copied).
- Frame 137, parser refusals that name a wrong thing: 14 fresh refusals in 7 sessions, 12 with `unterminated argument list` and 2 with the new text. The 2 name `assumption` and `text`, and each call holds that argument. Whether the 12 name a word that the call lacks was not read line by line. Night 120: 18 of 29 (copied).
- Frame 138, two stored tests on one criterion: 0 of 15 criteria that hold a test hold two.
- Frame 86, a resumed batch past its attempt cap wakes nobody: bg_3 stood red and `running` with no wake after 62e1a9fb1f. The cause was not read, so the frame is named for the sign only (reasoned: the sign matches the frame's heading).

Three signs of earlier reads stand again and have no frame: a criterion holds words that the request does not hold, `usage string` in 6 of 6 criteria of bg_3, where the request says "message", night 120's wall 3; the revert door's `The tests pass both ways` in s144, turn 22, while 3 tests are red, night 120's wall 5, seen once and not counted; a Vision Keeper in propose mode makes an item, `bg_1_summary`, night 119's wall 9.

## 6. New walls

Each wall was checked against the open frames of `plans/stack.md` by its sign.

1. **A span write that ends before the function's end drops the tail, and the `dropped` note comes back beside the commit that lands it.** Sign: `"dropped": "This write drops 13 lines that came after `raise Abort() from None`, from `if value in (\"y\", \"yes\"):`."` and, in the same results block, `OK code.commit -> {"committed": true, "head_commit": "52862f7ad4...`, s212, turn 3. Count: 2 writes with the note, s212 and s219, 2 landed commits, 2 project tests red at 5 of 5 heads, 1 batch given up. Proposed ends-when. Mechanism: a `code.commit` in the reply that holds a write with a `dropped` note does not land, and its refusal quotes the dropped lines and the span that keeps them, with one sandbox test on s212's reply. Ratio: batches whose first red project test follows a landed write with the note fall from 1 of 3 on night 121. Residue: a batch that still breaks so is read, and the frame closes when its cause is not a dropped tail.
2. **The surface door refuses a test that reaches the surface through the package, and the Tester's repair is lost.** Sign: `ERROR tests.encode: the surface 'src/click/decorators.py::version_option' lives in decorators.py and this test imports from click. Import the surface from its own module: `from click.decorators import version_option``. Count: the sign stands in 5 Tester sessions of bg_3, s300, s302, s304, s312 and s321, at least 18 lines. s304 lost a body with `@click.command()` to it three times. 6 of 6 stored tests of bg_3 then hold no `@command`. Proposed ends-when. Mechanism: the cause is read from s300's and s304's turns first; then the door admits `click.<surface>` or says to add the import and keep `import click`, with one sandbox test on s304's call. Ratio: Tester challenge sessions whose encode this door refuses three times fall from 1 of 7 on night 121. Residue: a session that still loses its encode is read, and the frame closes when its cause is not this door.
3. **A park ask gets an answer that names neither option, the Liaison asks again with the same words, and the answer becomes a new statement.** Sign: `CYCLE: period 5, rounds 3, wakes: liaison|tick:park_ask|bg_2 is parked. ...` in the log, and `rulings.rule(ask="The page asks about two options: a commit that fixes the change or a contest of confirm_default_on_eof. Which one do you want?")`. Count: 1 park ask asked 3 times, 15 sessions, 3 equal statements ratified, 9 deliveries. Proposed ends-when. Mechanism: the walk's principal has an answer for a park ask, meta workflow; an answer that names no option clears the wake as no choice, and an intake of a sentence that a ratified statement already holds is refused, rota workflow; one case each. Ratio: park asks asked more than once fall from 1 of 1 on night 121. Residue: a park ask that still repeats is read, and the frame closes when its cause is not an answer with no option.
4. **A Tester's test asserts a default that the function does not have.** Sign: `result = confirm("Yes or no?", default_on_eof=True)` and `assert result is True  # Default value for yes/no is True/False`, in `tst_confirm_eof_cr3`, `_cr4`, `_cr5` and `_cr6`, with `E           assert False is True`. Count: 4 of 15 stored tests, 4 of 7 reds at bg_2's head, 1 session, s245. Proposed ends-when. Mechanism: the cause is read from s245's turns, what the seat knew of `default`; then a door or one brief line, with one sandbox test on s245's call. Ratio: stored tests that assert a value the criterion does not give fall from 4 of 15 on night 121. Residue: a test that still does so is read, and the frame closes when its cause is not an unread default.

## Not read

- The new serve cap sentence for a call with no bound: 0 turns met it. Frame 121's first measure has no case on this night.
- What each seat read in the note on made-up results before it repeated its call, s209, s222 and s327. No interview ran.
- Whether the 12 `unterminated argument list` refusals name an argument that the call lacks, frame 137.
- Why no wake came for bg_3 after 62e1a9fb1f, and why `tick_attempts` holds no key of bg_3.
- Why the `tests_failing` key of bg_2 was quarantined three times and paged three times before it was given up.
- s152's five commits on bg_1 and s313's to s332's writes on bg_3 past their call lists. The diffs of the commits were not read.
- The Tester sessions s137, s139, s245, s300 and s321 past their stored tests: why the tests took the forms they have.
- The criteria wake of bg_3: why `usage string` entered six criteria.
- The Architect sessions, the nine answers past their refs, and the Critic sessions. The night stored no verdict.
- `-|tick:constraint_zero|` and `liaison|tick:round_close|t_p1`, both quarantined at 3 attempts.
- Night 119's cut events past the script: two long replies of s263 were not classed.
- No test ran on a worktree. Every claim about what a test or a commit does is read from `test_runs` and the turns.
