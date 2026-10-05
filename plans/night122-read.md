# Night 122 read

Night 122 ran cold from `C:/Users/roman/rota_night122` at a71951a, 2026-10-05 09:06 to 09:54. It holds 206 sessions, 742 turns and 3 batches. Rota workflow throughout. Database `.rota/clickI_night122.db`, log `.rota/night122.log`, report `.rota/night122_report.txt`. Scripts: the scratchpad folder `n122` of session 5101d8d0, copies of `n121` and `q1.py`, `q2.py`, `q3.py`, `calls.py` and `pred.py`. `pred.py` runs the predicates on a copy of the database. The read called no model and ran no test.

Summary:

- The night stopped because bg_1 held the Developer's one seat as `running` at attempt 5 of 10, with its `tests_failing` key quarantined. No predicate wakes a seat on such a batch, and `tick_batch_start` starts nothing while a batch runs. That is frame 87's open finding of night 100, and not a new wall.
- bg_1 went red from the Tester's tests and not from a commit. The one red at the end is `inh_echo_json_01`, version 2. It expects `{"key": "value"}` with a space, and the criterion gives `separators=(",", ":")`.
- Frame 135's door had no case: 0 encodes under a project test's id. Frame 121's notes: 8 cut events, 0 false claims.

## 1. Why the night ended after one batch

**Cause: bg_1 stands `running` at attempt 5, below `loop_cap` 10, and its key `developer|tick:tests_failing|bg_1` is quarantined at 3 attempts. Every path that frees the seat reads the attempt cap or a deferral, and bg_1 meets neither.**

1. The Developer sessions s148, s149 and s150 woke on `tick:tests_failing`, detail `attempt 5`, and wrote no code. The attempt does not move without a new commit or a new test, so the same wake ran three times. The log printed `CYCLE: period 1, rounds 3`, and the key went to `attempts=3, quarantined=1` (observed: `sessions`, `tick_attempts`, 2026-10-05).
2. The Liaison s151 woke on `tick:quarantined`, `1 abandoned: tests_failing for bg_1 (developer), 3 attempts`. It sent `msg.present_principal(refs=['bg_1'])`. The page was the touch page, `Before I build this, here is what I expect to touch`, m69, with no park and no stop. The principal approved, s152, and nothing changed (observed: turns of s151 and s152, 2026-10-05).
3. On the end state, `pred.py` gives these results (observed: `pred.py` on a copy, 2026-10-05). The code of both files is the same at a71951a and at HEAD (observed: `git diff`, 2026-10-05).
   - `tests_failing` offers bg_1 at attempt 5, and the key is quarantined, so the loop does not dispatch it.
   - `exhausted` gives nothing, because 5 is less than `loop_cap` 10, `rota/core/predicates.py:918`.
   - `preempt` gives nothing. `parked(bg_1)` is false, because bg_1 is not deferred and 5 is less than the cap, `rota/core/scheduler.py:1487`. bg_2 and bg_3 have priority 1 and echo_json has 5, and a lower priority never preempts, `rota/core/predicates.py:1395`.
   - `park_ask` reads deferred batches only, so no park ask fires.
   - `tick_batch_start` returns no wake while a running batch has a head commit, `rota/core/scheduler.py:336`. `next_batch` holds bg_2 and bg_3, both `pending`.
4. Walks 2 and 3 made bg_2 and bg_3. The principal approved each touch note, s180 and s201, and the batches stayed `pending` with no worktree. Each walk then went quiet, because no wake was due.

Night 121 differs in two facts. Its Developers committed until bg_1 reached attempt 10, so `do:park` fired. bg_2 was deferred by a priority preempt, bg_3 at 1 over bg_2 at 0 (observed: `night121.log` lines 85 and 140, `batches`, 2026-10-05). Night 122 had neither exit.

Known frame: frame 87. Its pass 1 status says "a running batch below its cap with a quarantined key still holds the seat", left open. Its night 100 status says "bg_2 was quarantined at attempt 3, and the Liaison's quarantined wake ... presented a build plan page ... with no park or stop option" (copied: `plans/stack.md`, frame 87, 2026-09-30). Night 122 is the same sign. Frame 86 is the path past the cap, and frame 142 is a park ask, which never fired here.

The escalate refusal adds a false claim: `The attempt cap carries this batch to the ladder: make one real change ... or end the session with no call`, `rota/core/sandbox.py:1369`. The seats s148, s149 and s150 met it, and the tick cap ended the batch before the attempt cap could (reasoned: three wakes on one attempt quarantine the key at attempt 5).

## 2. bg_1

**bg_1 broke on the Tester's tests. The test of frame 131's sign was repaired, and its repair asserts a wrong literal. The door then refused four correct challenges of that new version.**

1. s130, `tick:batch_start`, committed 76f10ae13f at turn 10. The harness then printed `34 test(s), 0 not passing`. Three later commits got `nothing changed`. No other commit landed on bg_1 (observed: `calls.py s130`, the log, 2026-10-05).
2. The Tester s139 stored three tests with ids it made, `inh_echo_json_01` to `_03`. Version 1 of `_01` called `runner.invoke(echo_json, ["{\"key\": \"value\"}"], catch_exceptions=False)`, frame 131's sign. The harness gave 3 of 37 red.
3. s140, attempt 2, challenged `_03`, m64. The Tester s141 replaced `_03`, 2 red. s142 answered m65 with `code.commit` three times, `committed: False, why: nothing changed`.
4. s143, attempt 3, wrote "`echo_json` is just a plain function" and challenged `_01`, m66. The Tester s144 replaced `_01` with version 2 at turn 6. It calls `echo_json({"key": "value"})` with `sys.stdout` on a `StringIO`. It asserts `output.getvalue() == "{\"key\": \"value\"}\n"`. s144 wrote "The output is compact JSON (no spaces after colons/commas)". Still 2 red.
5. s145, attempt 4, quoted the new assert and the criterion's `separators=(",", ":")`. The door answered `on exactly these refs already (m66) and they answered`. s145 escalated, m67, and the Architect s146 answered with `code.diff` and no words. s145 then sent six challenges in one reply and two in each of three turns. One landed, m68 on `_02`. The Tester s147 wrapped `_02` in `@command()`, 1 red.
6. s148, s149 and s150, attempt 5, each sent the same challenge on `_01`, then `msg.escalate_architect`. Both were refused. Then each sent empty `TOOL:` lines, `ERROR TOOL:: no function name after TOOL:`. No session wrote code after s130.

The red test at the end: `inh_echo_json_01`, version 2, `assert '{"key":"value"}\n' == '{"key": "value"}\n'`. The code is right and the test contradicts its criterion (observed: `test_runs`, `tests`, 2026-10-05). The stack's status of 09:45 on frame 131 says "the test did not change". It changed at s144, after the challenge m66.

## 3. Frame 135's door

- 41 `tests.encode` calls carry an id. 0 send the id of a project row, and 0 send `inh_` with eight hex characters (observed: `q3.py`, 2026-10-05).
- 0 prompts hold `is the id of the project's test`. The door has no case on this night.
- Stored tests: 37 of 37 ids start with `inh_`. 34 are project rows of the form `inh_` plus eight hex characters. 3 are the Tester's own ids, `inh_echo_json_01` to `_03`.
- Criteria that hold two stored tests: 0 of 3 that hold a test, 11 criteria in all.

## 4. Frame 121's notes

- `Your prompt does not hold this result, and the window cannot hold it.`: 0 prompts. The serve cap refusal: 0 turns. The new sentence has no case on two nights (observed: `grepc.py`, `servecap.py 122`, 2026-10-05).
- `ERROR reply cut`: 8 fresh events in 6 sessions. 4 are `inside`, last call broken. 4 are `after`, last call whole. The claim is true in 8 of 8 (observed: `cut.py 122 v`, 2026-10-05).
- The next reply repeats a whole call of the cut reply in 3 of 8 events. s40 repeats `code.source(path='docs/testing.md', start=6000, end=6400)`. Its result line says `ran, and this turn has no room left for its result ... Ask for it again in your next turn`, as on night 121. s178 and s199 repeat calls that the prompt marks `NOT RUN, because you wrote a tool result of your own ahead of them`, frame 113. So 1 of 8 repeats a call that the line says ran, and the result line asked for it.
- `CUT your reply`: 0 prompts.
- s70's closing account keeps the old sentence `so the last call did not run`. No seat reads a closing account.

## New walls

1. **The same-refs door ignores a new version of the test.** Sign: `ERROR msg.challenge_tester: you sent challenge to tester on exactly these refs already (m66) and they answered.` after `inh_echo_json_01` went from version 1 to version 2. Count: 4 Developer sessions, s145 and s148 to s150, refused on a correct challenge of version 2. Near frame 132, which covers a challenge closed with no call, and not a changed test (reasoned: frame 132's ends-when names the prose case only).

## Not read

- Why s139 made ids with the prefix `inh_`, and why s144 wrote a space that its own reply says is absent. No interview ran.
- The sessions of walks 2 and 3 past their wakes, and bg_2's and bg_3's criteria.
- The 56 made-up-result turns of the night count, frame 113.
