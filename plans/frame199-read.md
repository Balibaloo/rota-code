# Frame 199 read: the four reds at HEAD (2026-10-11 01:40)

## 1. `L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist`

- Red since: 376321b0, 2026-10-01 15:43, frame 107 pass 1, which added the case. The case was never green. On qwen3:8b the register holds 0 passes in all rows at both prompt hashes, e9fb76b1 (from 2026-10-02 02:21) and 47f78c38 (from 2026-10-07 09:34). The pin moved to qwen3:8b at aa34fc66, 2026-10-02 02:20.
- Cause: the case expects a pass verdict and one `msg.question_terminologist` that names `<c1>`, because the code comment says that the invoices survive and the criterion says that they go. `critic/review.md` step 3 tells the seat to send the question before the verdict. In every run the seat claims `encodes=True` and emits a pass in turn 1. It never sends the question.
- Owner: none open. Frame 107, "the Critic's doubt has no route to the Terminologist", closed 2026-10-02 04:08 with this case as a known red by design (`plans/archive/stack-2026-10-02.md`).
- Re-record: 0/5 -> 0/5. All five runs were live (`live=1`, load `qwen3:8b@248844`, 16 recorded in 51.5s), with five distinct transcripts.
- (observed: `case_runs` queries, `git log -S`, the re-record at 01:34)

## 2. `L1-CR-fail-names-its-criterion`

- Red since: 2026-10-07, frame 170. The case dates from 2026-08-10. It was 5/5 on every recording up to 2026-10-07 03:36, 390 of 390 rows at e9fb76b1. The first red was at c038ea3e, 10:37, pass 2: the lines door refused a block, and the seat looped to no verdict. That run read 3/5 under the old count (needs 4). Then 5116b49b (10:56) and 1409e251 (11:58) tightened the expectation. The case now asks for a fail on `<c1>`, or a challenge to the Tester with no verdict.
- Cause: the diff deletes the invoices, and the criterion keeps them. The seat claims `encodes=True` and emits a pass that names the delete lines as a 3-line value. The `verdicts.emit` lines door refuses that value, and the seat resends it. 2 of 5 runs land a wrong pass on one line, and 3 of 5 end with no verdict and no message. The old case counted any one verdict, so for 390 runs it admitted the wrong pass.
- Owner: none open. Frame 170, "a merge's review leaves no trace", closed 2026-10-08 01:53 and named this case its known red (`plans/archive/stack-2026-10-08.md`).
- Re-record: 0/5 -> 0/5. All five runs were live (22 recorded in 66.4s), with five distinct transcripts. Runs 2 and 3 wrote a pass verdict, and runs 1, 4 and 5 wrote nothing.
- (observed: `case_runs` by load and run, `git show` of the two case commits, the re-record at 01:35)

## 3. `L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner`

- Red since: ab70f47a, 2026-10-02 14:42, frame 110 pass 1, which added the case with no recording. The first recording was at 14:54, 0/5. The case never reached its threshold of 4. The best read is 1/5, from the live green run of 2026-10-06 17:29 that later replays copy.
- Cause: the case expects one `tests.encode` whose body carries `echo_json({` and no runner form. `tester/challenge.md` line 1 tells the seat to read the failure and the code, and then to fix the call line. The seat reads both and names the fault correctly in prose. Then it asks the Vision Keeper whether the function is async, or it ends in prose. In this re-record, run 5 called `tests.encode`, and the door refused the body as "not Python (invalid syntax, line 5)" on the escaped quotes.
- Owner: none open. Frame 110, "the Tester re-wraps a plain function for a runner", closed 2026-10-02 18:35 with the case red by design. Frame 131 (closed 2026-10-07) shares the mechanism but did not take this case. Its 2026-10-07 02:21 status says that this red is not its door's. Frame 200, the build loop design, lists the Tester's brief and doors among its sites, but it does not name the case (reasoned: frame 200's sites line).
- Re-record: 1/5 -> 0/5. All five runs were live (16 recorded in 53.2s), with five distinct transcripts: 3 asked the Vision Keeper, 2 ended in prose, and 1 encode was refused.
- (observed: `case_runs`, `git log -S`, the archive, the re-record at 01:37)

## 4. `tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line`

- Red since: 376321b0, 2026-10-01 15:43, frame 107 pass 1. That commit added `msg.answer_critic` to `rota/roles/prompts/terminologist/unresolved.tools`.
- Cause: `map mode terminologist/unresolved` prints 10 entries. These are the 4 ops and 6 `msg.` lines, one per line of the `.tools` file. The test still expects 9 entries and 5 `msg.` lines. `msg.answer_critic` is the tenth op. The test's number is stale, and the map tool is correct. The assertion at line 183 (`len(messages) == 5`) is stale for the same reason.
- Owner: none. Frame 199 only names the red. The archive called it "the flaky map family" on 2026-10-02, but the red is deterministic.
- Re-record: not applicable, because this test has no recording.
- (observed: the map output, the `.tools` file, `git show 376321b0`, pytest on the test, 2026-10-11)

## Closing line

No red is a real regression of a product change since 2026-09-27, with one exception. Frame 170's lines door at c038ea3e made the fail-names seat loop to no verdict in some runs, and frame 170 tightened that case on the same day to expose a wrong pass that is older than the baseline. Red 4, test_map, is a stale expectation. Reds 1 and 3 are cases that were added red by design on 2026-10-01 and 2026-10-02, after the baseline, and they were never green. The baseline of 658abb6 does not contain these cases, so the gate shows them as new.

Note: the three re-records wrote 15 live rows into `tests/rota/cassettes.db` on prompt hashes that are already current. `git status` shows no change to a tracked file.
