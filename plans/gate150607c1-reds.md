# The five reds of the gate at 150607c1

Read-only read of the register `C:/Users/roman/rota_g301/tests/rota/cassettes.db`, 2026-10-26. No model ran and no tracked file changed. The register times are local wall time. The clock went back one hour on 2026-10-25, so the commits before that day show `+0100` and the later commits show `+0000`.

| Case | Before (last pass) | After (gate at 150607c1) | Cause | Recommendation |
|---|---|---|---|---|
| L1-DV-a-wordless-answer-on-a-right-red-test-is-carried-on | 4/5 at pass 4, 2026-10-25 23:00, `eb168e091a115290`, `qwen3:8b@249023` | 3/5, 2026-10-26 01:25 refresh and plain, same hash, `@249024` | E: the new index feeds a code.write copy guard that refuses the file's own `truncate` | Fix the guard at `rota/roles/api.py:18766-18785`, then re-record |
| L1-DV-fix-what-the-verdict-names | 5/5 at pass 4, 2026-10-25 23:06, `f5028dad6c805474`, `@249023` | 3/5, 2026-10-26 01:30 and 01:31, same hash, `@249024` | A: the probe now returns the index rows, and the seat writes over the `def` line | Hold as a known red under frame 326 |
| L1-DV-give-the-new-parameters-defaults | 3/5 at pass 3, 2026-10-25 23:16, `ca0d36f5f4d5ba53`, `qwen3.5:9b@249023` | 2/5, 2026-10-26 01:39 and 02:00, same hash, `@249024` and `@249025` | D: run 5 answers an identical turn-2 prompt differently | Re-record once more on the main card, on qwen3.5:9b |
| L1-TS-apply-a-term-and-write-the-test | 5/5 at pass 4, 2026-10-24 23:01, `74a182670b527f79`, `@249011` | 3/5 replayed, not stale, 2026-10-26 01:08 and 02:00, `7489d3e4ff40f45f`, `@249024` and `@249025` | B: the Tester answer brief gained the `tests.retire` line (frame 306 row 2) | Hold as a known red with frame 281's Tester reds, under frame 306 |
| L1-DV-log-the-choice-the-criteria-did-not-make | Never green on qwen3:8b. Last pass on any model 2026-09-12, gemma3:12b `@248504` | 0/5, 2026-10-26 01:41, `94d2adc86774ac3a`, `@249024` | Red on qwen3:8b since the first recording | Hold as a known red. It is not a regression |

Two claims of the brief disagree with the register:

- The gate did not record `L1-DV-give-the-new-parameters-defaults` on qwen3:8b. The case pins `model: qwen3.5:9b` at `tests/rota/cases/l1_findings.yaml:83`. The register holds no qwen3:8b row for this case.
- Frame 323 did not measure this case at 0 of 5 on the text protocol. Its own status line of 2026-10-25 15:37 (`plans/stack.md:1210`) reads "4 of 5 against 3 of 5 on text" on qwen3.5:9b. The register agrees: the case replayed 3/5 (`00111`) on every gate from 2026-10-24 to 2026-10-25 23:16.

The prompt hash did not move on the three Developer cases. The cassette key moved because a tool result inside the session changed. `case_runs.prompt_hash` covers only the composed first prompt (`plans/operating-facts.md`, the line on `Pins.with_prompt`). The source of the changed tool result is frame 326's `index_batch: true` (commits 30abb274 and bc5e50a4). The fixture now indexes the batch tree, so `code.probe` and the copy check of `code.write` read rows where the index was empty before.

## 1. L1-DV-a-wordless-answer-on-a-right-red-test-is-carried-on

Case: `tests/rota/cases/l1_answers.yaml:176`, `pass: 4`, `expect: calls: [code.write, code.commit]`. Frame 326 commit bc5e50a4 added `index_batch: true` at line 188.

Before: every replay from 2026-10-21 to 2026-10-25 23:00 read `11011`. That is 4/5 at the threshold, so the case was green by one run. The last passing recording is the gate at cce18a2e, 2026-10-25 23:00:01, prompt hash `eb168e091a115290`, system hash `5eb91cf723d4f143`, load `qwen3:8b@249023`.

After: the refresh run at 01:25:02 (live) and the plain run at 01:25:52 read `11010`, same hashes, load `qwen3:8b@249024`. The replay at 01:59 reads the same.

Run 3 is not new. It fails the same way on every load since 2026-10-21: the seat calls `code.commit` and never calls `code.write`.

Run 5 is new. The first six turns of seq 560008 (old, pass) and seq 561629 (new, fail) are the same text. Both runs drop lines of `src/notify/formatting.py` with a partial write, then write the whole file back with `truncate` and `plural` kept. The two runs then get different tool results for that whole-file write:

- Old: the write passes. The seat calls `code.commit` three times, and the grader sees `code.write` and `code.commit`. Pass.
- New: the write returns "src/notify/formatting.py defines truncate, and the tree already defines truncate in web/format.js. A second definition of a name the project has once is a copy". The seat writes the same text three more times. It then says that it will not redefine `truncate`, and ends without `code.commit`. The grader reports "expected a call to code.commit". Fail.

The refusal comes from the copy guard at `rota/roles/api.py:18779-18803`. The guard has two gaps, and the new index exposes both:

1. `had_before` at lines 18766-18773 reads the file in the working tree at the time of the write. An earlier write in the same session removed `truncate`, so the guard treats the file's own committed `truncate` as a new definition. The fence below it (line 18806 and after) already takes the base commit as a baseline, and the copy guard does not.
2. The index query at lines 18779-18785 matches any symbol grain, in any language. `web/format.js::truncate` is a JavaScript export in the sample repository (`rota/testkit/samplerepo.py:645`, since 58642fc1, 2026-08-10). `_defined_in_tree` at line 22452 scans `*.py` only, so before frame 326 nothing matched.

Cause: E. Frame 326's fixture change (A) is the trigger, but the refusal is wrong for the project. A night with an indexed tree meets the same refusal.

Recommendation: fix the guard. Add the names that the file defines at the batch's base commit to `had_before`, and keep only grains in the same language as `path`. Then re-record the case. Do not amend the case.

## 2. L1-DV-fix-what-the-verdict-names

Case: `tests/rota/cases/l1_developer.yaml:534`, `pass: 4`, `expect: calls: [verdicts.load, code.write, code.commit]`. Commit bc5e50a4 added `index_batch: true` at line 543.

Before: 5/5 (`11111`) on every gate from 2026-10-21 to 2026-10-25 23:06, prompt hash `f5028dad6c805474`, system hash `3ddd541564364492`. The last passing recording is the gate at cce18a2e, 2026-10-25 23:06, load `qwen3:8b@249023`. The case was green on this hash from 2026-10-12.

After: the refresh run at 01:30 and the plain run at 01:31 read `11100`, same hashes, load `qwen3:8b@249024`. The replay at 01:59 reads the same.

The prompt diff is in the result of the seat's first call, `code.probe(pattern='src/notify/formatting.py')`. Cassette 58758 (old) against cassette 61272 (new), with the ids masked:

```
-OK code.probe -> []
+OK code.probe -> grain | grain_kind | area | fan_in | line_start | line_end
+src/notify/formatting.py::plural | symbol | src/notify | 0 | 7 | 11
+src/notify/formatting.py::truncate | symbol | src/notify | 0 | 3 | 5
+src/notify/formatting.py | path | src/notify | 0 | whole file |
```

The system text is the same. One more line differs, `"the principal said": ""` against `[]` in `[batches.expect]`. That line also differs in the old cassettes of the other cases, so it does not separate the two runs.

What the seat does in runs 4 and 5 (seq 561678): it reads the file with `end=-1`, then calls `code.write(start=3, end=5)` with one indented `return` line. Lines 3 to 5 are the whole `def truncate` span that the probe row names, so the write removes the `def` line. The tool refuses four times with "not valid Python (unexpected indent, line 3 in code.source numbering)". The session ends on the repeat, without `code.commit`. In the old run 4 (seq 560197) the probe was empty. The seat then read the file with `end=400`, wrote the whole file, and committed.

Cause: A. Frame 326's fixture now gives the seat the index that a night has, and the seat answers the new probe rows differently.

Recommendation: hold the case as a known red under frame 326. A re-record does not help: the refresh and the plain run read the same `11100` at temperature 0. The fixture is right as it stands. A door lead for a later frame: the refusal at the write could name the `def` line that the span removed.

## 3. L1-DV-give-the-new-parameters-defaults

Case: `tests/rota/cases/l1_findings.yaml:80`, `model: qwen3.5:9b` (line 83), `pass: 3`, `expect: calls: [findings.load, code.write, code.commit]`, architect forbidden. Commit 30abb274 or bc5e50a4 added `index_batch: true` at line 93 (frame 326, fault A).

Before: on qwen3.5:9b the case replayed `00111` on every gate from 2026-10-21 to 2026-10-25 23:16. That is 3/5 at the threshold. Runs 1 and 2 always fail, with an escalation to the Architect. The last passing recording is the gate at cce18a2e, 2026-10-25 23:16, prompt hash `ca0d36f5f4d5ba53`, system hash `6b4f4a55d662cdd3`, load `qwen3.5:9b@249023`. On 2026-10-25 between 03:40 and 11:30 the case read 0/2 and 0/4, partial replays that a re-record at 11:4 repaired.

After: the refresh run at 01:39:39 (live) and the plain run at 01:39:59 read `00110`, same hashes, load `qwen3.5:9b@249024`. The replay at 02:00 on `@249025` reads the same.

Run 5 diverges at turn 2. Old run 5 (seq 560736) answered the `model.load` result with `code.probe(pattern='display_results')`, and it later wrote and committed. New run 5 (seq 561689) answers with `code.source(path='main.py')`, then calls `msg.escalate_architect`. The grader reports "expected a call to code.write" and "named an act and did not perform it".

The turn-2 prompt is the same. Cassette 60699 holds the old turn-3 prompt, and the new turn-2 prompt (cassette 61308) is that prompt without the old turn-2 exchange. The system text is the same. The temperature is 0.0. The refresh replaced the old turn-2 cassette under the same key, so the register holds no copy of it.

Why the case went stale: the old run 5 called `code.probe` in later turns and got `[]`. With the new index those calls return rows, so the old cassettes miss.

Cause: D. The prompt that decides run 5 is the same, and the model answers it differently on load `@249024`. Frame 326's index (A) made the case stale but did not change the turn that fails.

Recommendation: re-record once more on the main card, with the model `qwen3.5:9b` (the case pin sets it). The case passes on one run of margin, so one load decides it. If a second load also reads 2/5, hold the case as a known red under frame 323. Frame 323's native trial read 4/5 on the same model.

## 4. L1-TS-apply-a-term-and-write-the-test

Case: `tests/rota/cases/l1_answers.yaml:319`, role tester, `pass: 4`.

The suite replay did not fail. The case sat under its threshold. The gate replayed the case at 01:08 (`@249024`) and at 02:00 (`@249025`) with `live = 0` and read `11001`, 3/5 against 4. The register shows no stale miss.

Before: 5/5 (`11111`) on every gate from 2026-10-24 19:30 to 2026-10-24 23:01, prompt hash `74a182670b527f79`, system hash `ddaa9583ce064b5e`. The last passing recording is 2026-10-24 23:01, load `qwen3:8b@249011`. That state is the one in the f9f5cd1 baseline, which is why the gate calls the case a new red.

Change: from 2026-10-25 11:5x (`@249017`) the case has prompt hash `7489d3e4ff40f45f` and system hash `9856cea3908e33e8`, and it reads 3/5 on every gate since. The gate at cce18a2e also read 3/5, at 23:0 and 23:3. So the case was red before frames 326 and 327.

The prompt diff is in the system text only. The user text is the same (cassette 60229 against 60825):

```
+When `principal_test_verdict` names a test that his words drop, call `tests.retire` with that test id and encode nothing for it.
+  TOOL: tests.retire(id)
```

The lines come from frame 306 row 2: 896abeef (2026-10-24 23:32 +0100) offered `tests.retire` in `rota/roles/prompts/tester/answer.md` and `answer.tools`, and 43688cd5 (2026-10-25 00:59 +0100) cut the rule to one sentence, now `answer.md:15` and `answer.tools:10`.

What the seat does in runs 3 and 4 (seq 560874): the first `tests.encode` body holds `\\n`, an escaped backslash, where the old run 3 (seq 548304) held `\n`. The tool refuses three times with "the body is not Python (unexpected character after line continuation character)". The seat then attests and ends. The grader reports "expected writes to tests (1..1), got 0".

Cause: B. A door text changed, and the seat answers the new system text differently on its first reply.

Recommendation: hold the case as a known red with frame 281's Tester answer-wake reds, under frame 306 row 2. A re-record does not help, because the replay is stable at 3/5 across five loads.

## 5. L1-DV-log-the-choice-the-criteria-did-not-make

Case: `tests/rota/cases/l1_developer.yaml:52`, `pass: 3`, `expect: calls: [code.write, code.commit, ledger.log]` and one or two ledger writes. The case was never green on qwen3:8b: 3092 runs, 0 passed, from the first recording before September to 2026-10-26 01:41. It was green on llama3.1:8b (1355 of 1484, last pass seq 123684, load `@248498`, 2026-09-12 04:00 UTC) and on gemma3:12b (5 of 5, load `@248504`, 2026-09-12 16:00 UTC, prompt hash `24a548281bb37b85`). The gemma3:12b recording is the last pass on any model. The gate's runs (seq 561700 to 561704, prompt hash `94d2adc86774ac3a`, `@249024`) fail on `ledger.log`: the seat writes and commits in some runs, and it never logs the choice. The case is a model limit on qwen3:8b, not a regression of frame 326 or 327. Hold it as a known red.
