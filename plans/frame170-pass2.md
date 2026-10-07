# Frame 170, pass 2: the pass refuses a block, and the third-refusal note names the routes

**Record of 2026-10-07 10:36, meta workflow. The pass repairs the review of 845e0b80 on the Critic's door, which is the rota workflow.**

The pass repairs the two mediums and the two lows of the review. The gate shows one new red, `L1-CR-fail-names-its-criterion`, at 3 of 5. The block refusal causes it, and the case's green before was a wrong pass in every run (observed: the case's runs, 2026-10-07 10:35). Section 3 holds the read.

## 1. What changed

- `rota/core/runner.py`. The third identical refusal of `verdicts.emit` prints a note that names the two routes that land, in the words of the review. Every other op keeps the general note. The fourth turn still ends the session.
- `rota/roles/api.py`. `_pass_lines_check` refuses a value of more than `_LINE_PARTS_MAX = 2` parts, in the words of the review. The check runs after the unnamed-criterion check and before the diff check. A value of 2 parts still lands.
- `tests/rota/test_verdict_lines.py`, 5 new tests: a 4-line block for s279's three criteria is refused with the words; a 2-line value lands; `lines={cid: ''}` gets the unnamed words; a batch of two commits with a configured project root lands a line of the first commit, which the diff from HEAD~1 holds only as context; a Critic session that sends one refused pass in six turns reads the new note on its fourth prompt and ends after four turns.
- `plans/frame170-pass1.md`. The two gemma3:12b cases read 390 of 390 before. The first query read the wrong model.

## 2. Deviations from the brief

1. The new note fires for every third identical refusal of `verdicts.emit`, on a pass or on a fail. The words name both routes, so they hold for both.
2. The block refusal records no offer. Its words name no call that the doors admit, so frame 144's law asks for none.

## 3. The new red, `L1-CR-fail-names-its-criterion`

- The case expects `verdicts: {count: 1}` and no result. Its diff deletes the invoices, and its criterion says that the invoices stay. So a fail is the right verdict (observed: `tests/rota/cases/l1_judgement.yaml:70`, 2026-10-07).
- On the main checkout the case is 390 of 390 green, and each run of the last ten is a pass (observed: `case_runs`, prompt hash e9fb76b1, 2026-10-07 02:27 and 03:36). The green counts a wrong verdict.
- After pass 1 the seat named a 3-line block, `from ..store.records import delete` and the two `delete(...)` lines, and the pass landed.
- After this pass, runs 2 and 4 send the same block in four turns. Each turn meets the block refusal. The third-refusal note fires, the seat sends the same block again, and the runner ends the session on "repeated its previous turn verbatim twice". No verdict lands. (Corrected in pass 4: this line first said that the note could not fire. The note is in the prompts of runs 1, 2, 4 and 5, so it fired in 4 of 5 runs and moved 0 of 4 to the fail route. Observed: the `cassettes` prompts, 2026-10-07 11:12.)
- Runs 1, 3 and 5 cut the block to 2 lines or fewer, for example `delete("invoices", account_id)`, and land a pass. These are wrong passes that name true added lines. That is the gap that design section 2 names: the door cannot see whether a line meets its criterion.
- The pass does not change the case. The choice is the assistant's: the case can expect `result: fail`, and then it is red on main too; or the block limit can move.

## 4. The gate

```
suite: 27 failed, 3220 passed, 35 skipped, 17 xfailed, 18 warnings (baseline: 29 failed, 3207 passed, 35 skipped, 17 xfailed, 18 warnings)
new reds (1): tests/rota/test_l1.py::test_l1_case[L1-CR-fail-names-its-criterion]
reds gone (0): none
stale (0): none
time: 796.1s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline fb0cee1 2026-10-07 09:48
```

The baseline is the one that pass 1's gate stored on its uncommitted tree. The gate re-recorded 3 stale cases, five runs each:

| Case | Before, pass 1 | After |
|---|---|---|
| `L1-CR-a-test-that-encodes-nothing-is-a-challenge`, gemma3:12b | 5 of 5 | 5 of 5 |
| `L1-CR-fail-names-its-criterion` | 5 of 5 | 3 of 5 |
| `L1-CR-finish-the-review-with-the-answer-in-hand` | 5 of 5 | 5 of 5 |

## 5. Pass 3: the fail case expects a fail

**Decided by the assistant, 2026-10-07, after section 3: the case expects what its name says.** Its diff deletes the invoices, and its criterion keeps them. So the one right verdict is a fail that names the criterion. A pass is a wrong verdict, and the case admitted it 390 times. The block limit stays at 2.

- The case's `expect` now reads `verdicts: {count: 1, text_includes: ['"result": "fail"', '"failed_criterion": "<c1>"']}`. `text_includes` is the key that `fixtures.check` reads on a written row (observed: `rota/testkit/fixtures.py:504-534`, 2026-10-07).
- The re-record by exact id on qwen3:8b, 5 live runs, is **0 of 5** (observed: `case_runs`, live at 2026-10-07 10:40:54, and the plain replay after it). This is a known red that frame 170 names. It is not a failure of the pass.
- Runs 1, 3 and 5 land a pass. Runs 2 and 4 land no verdict: each sends a 3-line block in four turns, and the runner ends the session on the verbatim repeat. The third-refusal note reached runs 1, 2, 4 and 5 first, and moved none of them to a fail (corrected in pass 4). No run sends a fail.
- The live runs repeat the transcripts of pass 2 to the batch id. The model runs at temperature 0, so the re-record cannot move the count.
- The gate at 10:56 lists the case as its one new red, 0 of 5. Its suite line is `25 failed, 3222 passed`.

## 6. Pass 4: the note on the second refusal, and a fixture the predicate cannot reach

**Record of 2026-10-07 11:42, meta workflow.**

- The pass note now fires on the second identical refusal of a pass. A refused fail reads the general note. A test refuses a value of three lines (observed: `tests/rota/test_verdict_lines.py`, 2026-10-07).
- Section 3 and section 5 are corrected. In the recordings of passes 2 and 3, the three-turn note is in the prompts of runs 1, 2, 4 and 5. It fired in 4 of 5 runs, and it moved 0 of 4 to the fail route (observed: the `cassettes` prompts, 2026-10-07 11:12).
- **The fixture change was built, recorded and then held back.** The test asserted that the invoices stay, and its `test_runs` row read `fail`. The gate at 11:22 then named a new red, `test_case_reachability.py::test_a_tick_cases_fixture_would_actually_fire_that_predicate[L1-CR-fail-names-its-criterion]`: "tick:review produces no wake at all". `predicates.review` wakes the Critic only on a green harness (observed: `rota/core/predicates.py:1155-1186`, 2026-10-07). A test that encodes the criterion is red against this diff, so the review cannot arise. The patch is in the session scratchpad as `f170_pass4_fixture.patch`.
- The recording of that fixture, live at 11:10, was 0 of 5. Runs 2, 3 and 5 landed a pass. Runs 1 and 4 landed none. No run sent a fail.
- With the fixture of pass 3 and the new note, the gate's re-record at 11:42 is 0 of 5. Runs 2 and 3 land a pass. Runs 1, 4 and 5 land none. No run sends a fail.
- `L1-CR-a-test-that-encodes-nothing-is-a-challenge` went stale on the note and re-recorded 5 of 5. `L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist` re-recorded 0 of 5, the known red.

The gate at 11:42:

```
suite: 26 failed, 3224 passed, 35 skipped, 17 xfailed, 18 warnings (baseline: 29 failed, 3207 passed, 35 skipped, 17 xfailed, 18 warnings)
new reds (1): tests/rota/test_l1.py::test_l1_case[L1-CR-fail-names-its-criterion]
reds gone (0): none
stale (0): none
time: 657.9s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline fb0cee1 2026-10-07 09:48
```

## 7. Pass 5: the fail case accepts either right route

**Record of 2026-10-07 11:58, meta workflow. Decided by the assistant after section 6.**

- The review tick fires only on a green harness (observed: `rota/core/predicates.py:1155-1186`, 2026-10-07). So no reachable fixture holds a test that encodes the criterion against this diff, and the pass 3 fixture stays.
- The case's `expect` is an `any_of` of two branches. The first is one verdict whose row holds `"result": "fail"` and `"failed_criterion": "<c1>"`. The second is a challenge to the Tester whose refs include `<c1>` and `<tst1>`, with `verdicts: {count: 0}`, in the shape of `L1-CR-a-test-that-encodes-nothing-is-a-challenge`. A pass meets neither branch.
- The re-record by exact id on qwen3:8b, 5 live runs at 11:46:58, is **0 of 5**. This is the known red that frame 170 names.

| Run | Route |
|---|---|
| 1 | four passes, each refused as a 3-line block; no verdict, no message |
| 2 | passes refused, then a pass landed |
| 3 | passes refused, then a pass landed |
| 4 | three passes, each refused as a 3-line block; no verdict, no message |
| 5 | four passes, each refused as a 3-line block; no verdict, no message |

- No run sends a fail or a challenge. Every run claims `encodes=True` first and then sends a pass (observed: the runs' transcripts, 2026-10-07 11:46).
- The note keeps the words "in two turns", which match the count it fires on.

The gate at 11:58:

```
suite: 25 failed, 3225 passed, 35 skipped, 17 xfailed, 18 warnings (baseline: 29 failed, 3207 passed, 35 skipped, 17 xfailed, 18 warnings)
new reds (1): tests/rota/test_l1.py::test_l1_case[L1-CR-fail-names-its-criterion]
reds gone (0): none
stale (0): none
time: 595.0s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline fb0cee1 2026-10-07 09:48
```

## 8. Pass 6: the pass note follows the lines check only

**Record of 2026-10-07 12:17, meta workflow.**

- The runner gave the pass note to any refused `verdicts.emit` with `result='pass'`. So a landed pass sent again read "already landed" and then the pass note, which named routes that cannot land. Night 120's s148 and night 128's s142 and s195 each sent a landed pass again (the review of 9eaafc48, confirmed).
- The checks of `_pass_lines_check` now raise `api.LinesRefusal`, a subclass of `ValueError`. The runner keys the pass note on that class. Every other refusal of `verdicts.emit` reads the general note. `_verdict_result` is gone.
- A new test sends a landed pass again in five turns. It reads "already landed" and the general note, and never the pass note. It fails on the runner of 605b2e1e (observed: the test against the stashed change, 2026-10-07, before the gate of 12:17). The tests of the three checks still read the pass note on the second refusal.
- No recorded case went stale. `L1-CR-fail-names-its-criterion` stays the known red at 0 of 5.

The gate at 12:17:

```
suite: 25 failed, 3226 passed, 35 skipped, 17 xfailed, 18 warnings (baseline: 29 failed, 3207 passed, 35 skipped, 17 xfailed, 18 warnings)
new reds (1): tests/rota/test_l1.py::test_l1_case[L1-CR-fail-names-its-criterion]
reds gone (0): none
stale (0): none
time: 598.2s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline fb0cee1 2026-10-07 09:48
```
