# Frame 360: why the Critic, told that no code changed, passes a false claim (2026-11-08)

The brief: `f360_critic_why_brief.md` in the scratchpad of session 0d047fa7.
Roman asked, 2026-11-08 07:56: "investigate why this is" (ruled: Roman, `plans/stack.md`, frame 360's status line of 07:56).

## Result

- **The Critic passes because on a claimed batch the structure gives it no way to check the claim, and every door on its path leads to a pass.** On a claimed batch the Critic can see only the criteria and the test bodies. The `test:` route of `verdicts.emit` lets a pass land when a test is bound to the criterion, is live and passed at the head. Nothing asks whether the test checks the criterion. A fail needs `verdicts.claim_encodes` first, and a pass needs nothing (observed: `rota/roles/api.py` `_route_fault` 19376 to 19435, `verdicts_emit` 18549 to 18686).
- **No tool of the Critic can tell a true claim from a false one when the tests are weak.** The Critic has 8 tools. 0 of 8 run code, read the code under test or write a probe. 1 of 8, `tests.load`, lets a reader see that a test is weak. It can show that the evidence is empty. It cannot show that the code is wrong (observed: `rota/roles/prompts/critic/review.tools`; reasoned).
- **The model did not read the tests in 4 of 5 samples and in s154.** In each of these sessions, the first act was a pass. Sample 4 read the test bodies against the criteria, found 2 of 3 tests weak, and challenged the Tester (observed: the turns of `s5/sample_<n>/dry6b.db`, session s164).
- **The count "0 of 5 challenged" in frame 360's status line of 07:54 is wrong. The right count is 2 of 5, and 1 of 5 stopped the pass.** The replay's query asked for `body_refs LIKE '%<batch id>%'`, and a challenge's refs are criterion ids and test ids. Sample 4 sent `m32`, a challenge to the Tester on `["c2", "tst_fold_c2"]`, and landed no verdict. Sample 5 passed, and then sent `m33`, a challenge to the Developer on `["c1", "c2", "c3"]` (observed: `messages` in each sample database; `replay_critic.py` lines 98 to 100). So the pass landed in 4 of 5 samples, not 4 of 4 plus one silent sample.
- **The replay's world is not s154's world.** The replay sets `project_root` to the clone, so `_batch_base` falls back to `HEAD~1`. `code.read` then shows the diff of the upstream commit 99619246, two docstring files, and not the empty diff of the live arm. That diff, 7,165 characters, explains the larger wake, 30,215 characters against 22,317. So the wake cut that frame 360 noted at 07:54 comes from the replay (observed: sample 5's `code.read` result, `touched: ['news/1591.documentation', 'src/icalendar/cal/alarm.py']`; `git diff f82f8606 99619246 | wc -c` = 7165; reasoned: 30,215 − 22,317 = 7,898).
- **One proposal, after a design page amendment:** shape E of `plans/design-false-claim-2026-11-06.md`. A claim cites a code line for each criterion, so the claim moves off the `test:` route and onto the `kept:` route, and frame 201's hold then asks about each cited line. The price is about 5 cycles (reasoned). Section H gives the details.

## A. What the Critic is for

The composition gives the Critic no name. It gives the rule that the Critic serves. "Every claim cites a source. A seat can check the claim against the source" (observed: `plans/composition.md`, Flows). "A weak model is trusted only as far as the loop that checks it is short" (observed: `plans/composition.md`, The ceiling). "Capability comes from wiring. No brief grants what is not wired" (observed: `plans/composition.md`, The parties).

The Developer's claim cites no source. "The claim carries the commit message only. It cites no line and no run" (observed: `plans/design-false-claim-2026-11-06.md` section 1, fact 1). s152's message: "No changes needed; existing implementation in string.py already meets criteria" (observed: the same). So the claim fails the composition's flow before any seat reads it (reasoned).

The brief, `rota/roles/prompts/critic/base.md`: "You judge whether a diff does what was asked." "You see the criteria, the tests, and the diff." "Dispute a test, don't work around it. If a test does not encode its criterion, challenge Tester. Do not re-derive the criterion yourself." "Do not invent objections. If the diff conforms, pass it." (observed).

The mode, `rota/roles/prompts/critic/review.md`, step by step (observed):

1. "That is everything you get, and it is everything you need — there is nothing to fetch".
2. Step 1: "For each criterion, find the added line of the diff that meets it". A kept criterion "is also met by `test: <the test id>`, its own passing test that step 2 finds encodes it." "A test that encodes nothing is a challenge in step 2, never a pass."
3. Step 2: "Read the test's assertion against the criterion's words. ... Then claim `encodes=False` and send `msg.challenge_tester`. Quote the test's line and the criterion's words, and stop. Emit no verdict in that session".
4. Step 3: a doubtful criterion goes to the Terminologist. Step 4: work nobody asked for.
5. Then `verdicts.emit`. "The tool refuses a pass with a criterion that has no value, or a value that the diff or the last test run does not hold."

**What the brief tells it about a claim: nothing.** `review.md` and `base.md` hold no sentence about a claim, a claimed batch or an empty diff (observed: `grep -i "claim\|no code\|empty"` finds only `verdicts.claim_encodes`). The word "claim" in the brief means the Critic's own `claim_encodes` answer. The note's "The Developer claims" uses the same word for another thing (reasoned: the one-word-one-meaning rule). The note "The tests are the only evidence" says what is true. It does not say what to do (observed: `CRITIC_CLAIM_NOTE`, `rota/roles/api.py` 23112).

The brief puts step 1 before step 2. On an empty diff, step 1 has one route left, `test:`, and that route refers forward to step 2. The model took "its own passing test" and left out "that step 2 finds encodes it" in 4 of 5 samples and in s154 (observed: section D).

## B. What the Critic can do

The review mode has 8 tools (observed: `review.tools`; `python -m rota.tools.map mode critic/review`).

| Tool | What it gives on a claimed batch | Does it tell a true claim from a false one? |
|---|---|---|
| `criteria.load` | The criterion words | No. It is half of a comparison. |
| `tests.load` | The bodies of the 3 team tests, and 89 rows of inherited tests as "N characters, passing, not shown" | Partly. A reader can see a weak test: `tst_fold_c3` folds the word "Short". It cannot see that the code is wrong. |
| `code.read` | The diff since the fork, empty on the live arm, and the claim note. "Critic's entire view of the implementation" | No. It shows no source of the code under test. |
| `verdicts.claim_encodes` | Records a boolean, checks nothing | No. 29 of 29 `True` on nights 114 to 128, and 3 of 3 `True` in sample 5. |
| `verdicts.emit` | The door. The `test:` route checks bound, live and passed at the head | No. On a claim, a passing test at the head is a test that passes on the old code. |
| `msg.challenge_tester` | The act for a weak test | No. It is an output, and it is the right act. |
| `msg.challenge_developer` | Asks the Developer | No. The Developer made the claim. |
| `msg.question_terminologist` | Asks about the criterion words | No. |

Sources: `rota/roles/api.py` `code_read` 24306 to 24356, `_route_fault` 19376 to 19435, `verdicts_claim_encodes` 18442 to 18494 (observed). The 29 of 29: `plans/frame170-merges-read.md` line 50 (observed).

**Count: 0 of 8 tools tell a true claim from a false one. 1 of 8, `tests.load`, read by step 2, tells a proven claim from an unproven one.** No tool runs a test, writes a probe, reads `_foldline`, or runs the old code (observed: the tool list). On a claim, the batch reaches review only when its tests pass at the fork. So a strong test makes a true claim, and a weak test leaves the claim unknown (reasoned: `plans/design-false-claim-2026-11-06.md` section 2, last bullet).

Calls per session. Calls 1 to 3 of each session are the wake's pushed reads, `code.read`, `criteria.load` and `tests.load` (observed: `tool_calls`).

| Session | Calls | `verdicts.emit` | `challenge_tester` | `challenge_developer` | `claim_encodes` | `code.read` called | `question_terminologist` | Outcome |
|---|---|---|---|---|---|---|---|---|
| s154, live, t 0 | 8 | 5 | 0 | 0 | 0 | 0 | 0 | pass at emit 3 |
| sample 1, t 0 | 8 | 5 | 0 | 0 | 0 | 0 | 0 | pass at emit 3 |
| sample 2, t 0.6 | 8 | 5 | 0 | 0 | 0 | 0 | 0 | pass at emit 3 |
| sample 3, t 0.6 | 10 | 7 | 0 | 0 | 0 | 0 | 0 | pass at emit 3 |
| sample 4, t 0.6 | 19 | 3 | 11 | 2 | 0 | 0 | 0 | challenge m32 lands, no verdict |
| sample 5, t 0.6 | 25 | 5 | 0 | 4 | 3 | 9 | 1 | pass at emit 3, then m32 question and m33 challenge |

The order in samples 1, 2, 3 and s154 is the same each time (observed): a pass on assertion lines, refused; a pass on `test:` values, held; the same pass, landed; repeats, refused as "already landed". Sample 4: two challenges to the Developer, refused; one challenge to the Tester refused for its refs and two for their quotes; c2's challenge landed at call 9; seven more refused as "already sent"; three passes refused because the Tester challenge stands. Sample 5: a pass refused; a challenge refused for its refs; a pass held; four `code.read` calls, refused after three; the pass landed at call 11; then three `claim_encodes True`, a refused pass, the question, a fail refused as "already landed", and a challenge that landed at call 23.

## C. What the doors said

Each distinct refusal is listed with the samples that met it, verbatim to the cut that `results.json` keeps (observed: `results.json`, `errors`; s154's turn 7).

| # | Refusal | Met by | Points toward |
|---|---|---|---|
| 1 | "verdicts.emit: the line for c1, '...', is not an added line of the diff of batch fold_long_lines_in_icalendar_batch. Copy one line of the [diff] block that starts with +, without the +, and send the pass again. If the change keeps what c1 asks and adds no line for it, send `kept: <a line of the [diff] block that starts with a space>` or `test: <the id of a test of c1 that passed>`. If no added line meets c1 and the change does not keep it, that is a fail on it: `verdicts.claim_encodes('c1', encodes=...)` first, as for any fail" | s154, samples 1, 2, 3, 5 | **Pass.** On an empty diff the only route it names that can hold is `test:`, and it asks only that the test "passed". Every seat that met it sent `test:` values next. |
| 2 | "HELD verdicts.emit: before the pass lands, answer for cw_41b4cb28dda6, cw_6a232f4ea912 and cw_99502ef494ad. Commitment cw_41b4cb28dda6 rests on src/icalendar/tests/test_icalendar.py line 9: \"_foldline,\". Does the diff keep that line and \"_foldline,\"? ... Say which in your own words, and in the same reply send the pass again or your own fail on the criterion or the commitment." | s154, samples 1, 2, 3, 5 | **Pass.** An empty diff keeps every line, so the answer is always "kept". The hold asks nothing about the criteria, because it skips `test:` values. |
| 3 | "verdicts.emit: your verdict on batch fold_long_lines_in_icalendar_batch at this commit already landed, and one commit gets one verdict: end the session" | s154, samples 1, 2, 3, 5 | Neither. The pass had landed. It also refused sample 5's late fail on c1. |
| 4 | "msg.challenge_developer: quotes= holds `No code changed on this batch. The Developer claims the criteria are met.`, and it is not a span of the live text of c1 or of c2 or of c3. Quote, not paraphrase" | sample 4, twice | **Away from a challenge of the claim.** The claim is no row, so a challenge cannot quote it. |
| 5 | "msg.challenge_developer: refs are ids and nothing else; you sent {'id': 'cw_41b4cb28dda6'}." | sample 5 | Neither. A form fault. |
| 6 | "msg.challenge_developer: quotes= holds `Criterion c1: 'The serialization of an iCalendar component produces lines no ...`, and it is not a span of the live text of c1 or of c2 or of c3." | sample 5 | Neither. A form fault. The next try landed. |
| 7 | "msg.challenge_tester: a challenge to the tester names both sides of the conflict in refs -- the criterion and the test -- and yours names no test. c2's test is tst_fold_c2: send refs=['c2', 'tst_fold_..." | sample 4 | **Challenge.** It names the next call. |
| 8 | "msg.challenge_tester: quotes= holds no span of the live text of tst_fold_c2. A comment of the test does not count. Quote, not paraphrase" (and the same for tst_fold_c3) | sample 4 | **Challenge.** A form fault with the fix named. |
| 9 | "msg.challenge_tester: you have already sent challenge to tester; saying it again with different refs is a second answer to one question, and the recipient has to reconcile them. Your work here is done" | sample 4, 7 times | **Against the second challenge.** c2's challenge landed, so c3's never did. c3 is the criterion that the code breaks ("splits a word in 8 of 12 sample texts"). |
| 10 | "verdicts.emit: you have already challenged the tester this session, and that is your judgement of this commit until the challenge lands." | sample 4, 3 times | **Challenge.** It kept the pass out. |
| 11 | "repeat refused: code.read asked three times this session and the answer has not changed" | sample 5, 3 times | Neither. |
| 12 | "verdicts.emit: missing required argument(s) ['batch_id']", "your reply was cut at the output budget", "wrote its own tool results", "the stream stopped at the invented result" | samples 4, 5 | Neither. Runner faults. |

**The door's code on a claimed batch, where the diff is empty** (observed: `rota/roles/api.py`):

- `_pass_lines_check` 19438 onward: a value is an added line, `kept: <line>` or `test: <id>`. On an empty diff no line is added or kept, so `test:` is the only route that can hold.
- `_route_fault`, the `test:` branch: the test exists in the batch, binds to the criterion, is not retired, and its latest run at the head is `pass`. It does not read `ctx.verdict_claims`. "The door checks a fact, never the seat's words."
- `_first_pass_hold` 19784 onward: "A `test:` value names a test, not a line, and the door checked that the test passed. So the hold's question about a line does not apply to it (sprint 35 row 4)." On a claim, the hold asks only about the pushed commitments, and the answer is "kept".
- `verdicts_emit`: a fail needs `claim_encodes(..., True)` first. A pass on `test:` needs nothing. On a claim, the cheap path is the pass (reasoned).
- `_claimed` and `critic_claim_note` change only the note. No door reads the claim, except the guard against a pass on another batch's claim (observed: `verdicts_emit`, the guard of 2026-11-06).

## D. What the Critic reasoned

**All 5 samples read the claim note.** Samples 1 to 4 quote it. Sample 5 paraphrases it (observed: the completions).

**4 of 5 samples, and s154, sent a pass as their first act, with no prose.** Each first completion is a single `TOOL: verdicts.emit(... result='pass' ...)` with the tests' assertion lines as values (observed: turn 1 of samples 1, 2, 3, 5 and of s154). Prose came only after the hold, and it answered the hold's question about the commitments, not the tests.

What they said about "no code changed" (observed: the turns named):

- Sample 1, turn 3: "The diff contains no changes (`No code changed on this batch`). Therefore, it keeps all existing lines and behaviors exactly as they were." Then: "All pushed commitments are satisfied by the lack of change. The tests for criteria c1, c2, and c3 all passed in the provided results (`last_result: \"pass\"`), satisfying the criteria via `test:` references."
- Sample 2, turn 3: "Since the code did not change, the criteria (which rely on the behavior of `_foldline` and the 75-octet limit logic) are satisfied by the unchanged implementation. The tests passed (`last_result: \"pass\"`)."
- Sample 3, turn 3: "Since the tests (`tst_fold_c1`, etc.) are listed in `[tests.load]` as passing (\"last_result\": \"pass\"), and they encode the criteria, I can use `test:` references." Its stored reason: "No code changes were made; existing lines referenced by commitments are kept."
- Sample 5, stored reason: "The diff is empty; no code changed. Therefore, the lines referenced by the commitments are kept ... The criteria c1-c3 are met by the existing passing tests."
- Sample 4, turn 1: "I cannot verify if the *current* code (which produced passing tests) meets the criteria without seeing the implementation or a diff showing the state." Turn 5: "`tst_fold_c3`: Uses a short string (\"Short\") which doesn't trigger folding." Turn 8 reason: "Challenges to tester were issued regarding c2 and c3 encoding, but the diff shows no code changes; thus no behavioral failure to report."

**Yes, the model took "no code changed" as a fact that supports a pass.** It did so in 4 of 5 samples, on two grounds. First, the hold asks "Does the diff keep that line?", and an empty diff keeps everything. Second, "the tests passed" reads as "the criteria are met". Sample 3 asserted "they encode the criteria" and read no test (reasoned: no test body is named in its prose). The one sample that read the test bodies, sample 4, is also the one that said it cannot see the code.

**Sample 5's late doubt came from the replay's wrong diff.** Its question to the Terminologist says: "the diff only modifies docstrings in `src/icalendar/cal/alarm.py` and adds a new documentation file." That diff is the upstream commit 99619246, not the batch (observed: section E).

## E. The prompt's shape

| | Live s154, turn 1 | Replay, turn 1 |
|---|---|---|
| Wake length | 22,317 characters | 16,429 shown, 30,215 before the cut |
| The claim note | absent; `code.read` said "no commit yet on this batch" | line 3, character 72, from `build_prompt` |
| `criteria.load` | at 190, about 550 characters | at 297 |
| Constraints | at 740, about 1,310 characters | at 847 |
| `tests.load` | at 2,051. Cut inside the result: "CUT the result: 34,747 of 54,747 characters are not shown" | at 2,158 |
| The team's 3 tests | about 2,200 characters | 2,211 characters |
| Inherited rows shown | 89 | 63 |
| `code.read` | at 22,191, last, 126 characters: `"diff": "", "touched": []` | cut. "CUT your wake: 13,904 of 30,215 characters are not shown." |

Sources: `turns` of s154 in `arm362/runs/dry6b.db` and of s164 in `s5/sample_1/dry6b.db`, read-only (observed).

**What filled it.** Inherited test rows fill about 18,000 of the 20,000 characters of `tests.load`. The batch's own tests are about 2,200 characters, about 10 per cent of the wake (observed: the offsets). Each inherited row says "N characters, passing, not shown", and none bears on the review (reasoned).

**What was cut in the replay.** About 5,990 characters of inherited rows and the whole `code.read` block, about 7,900 characters. The block held the copy of the claim note, `[removed lines]` and the upstream diff (reasoned: the offsets and the diff size). On the live arm, the same wake with the note is about 22,420 characters, and the live wake fit at 22,317. So the live wake with the note would not be cut (reasoned). Frame 360's line of 07:54, "cut ... by 60 inherited test rows", is half right. The cut exists only in the replay.

**The rules on size, and whether they were kept.** `PUSH_CHARS = 20000` caps a pushed read (`rota/core/runner.py` 1205), and `tests.load` was cut at it on both runs (observed). `_fit` gives the wake two thirds of the budget and cuts it with a note (runner.py about 1801 to 1833). The replay's cut at 16,311 characters keeps that rule (observed). Night 103 replaced a passing inherited body with its length (`api.py` about 13425), and that rule is kept. No rule limits the share of inherited rows in a review wake. No rule puts `code.read` before `tests.load`. So the Critic's one view of the implementation sits last, where any cut takes it first (reasoned). `plans/wall-guide.md` cause 2 says: "Check the eviction notices and the prompt's size against `num_ctx`".

## F. The register

The Critic has 11 case ids (observed: `tests/rota/cases/*.yaml`).

| Case | What it measures | Model | Pass rule | Gate of 2026-10-31 at 5bf28154 |
|---|---|---|---|---|
| ACT-CR-quote-the-tests-code | A test whose assertion contradicts its comment goes to the Tester as a challenge | gemma3:12b | 4 of 5 | passed |
| L1-CR-finish-the-review-with-the-answer-in-hand | A verdict after an answer arrives | default | | **FAILED** |
| L1-CR-pass-a-conforming-diff | A pass on a right diff | default | 4 of 5 | passed |
| L1-CR-fail-names-its-criterion | A fail on a diff that contradicts | default | | passed |
| L1-CR-a-purpose-in-a-docstring-is-not-a-fail | No fail on a docstring purpose | default | | passed |
| L1-CR-a-broken-pushed-commitment-is-a-fail | A fail on a broken commitment | default | | passed |
| L1-CR-a-kept-behaviour-passes-by-its-kept-line | A pass by `kept:` **or by `test:`** | default | 4 of 5 | **FAILED** |
| L1-CR-dismiss-a-finding-on-a-falsified-constraint | A finding on a falsified constraint | default | | passed |
| L1-CR-a-test-that-encodes-nothing-is-a-challenge | A vacuous test, `close_account('a1') is not None`, goes to the Tester. A verdict is forbidden | gemma3:12b | 3 of 5 | passed |
| L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist | A doubt goes to the Terminologist | qwen3:8b | | **FAILED** |
| L1-CR-challenge-a-claim | The challenge mode on an Architect constraint, not a Developer's claim | default | | passed |

Sources: the yaml files and `.rota-gate.json`, which holds 34 failed and 6,465 passed on qwen3:8b (observed). The gate in `.rota-gate.log` today is at 97 per cent at 08:05 and holds no `FAILED` line yet (observed).

**The recorded runs, by model** (observed: `case_runs` in `tests/rota/cassettes.db`, read-only, the sum of `passed` over the runs of each model at its latest prompt hash):

- `L1-CR-a-test-that-encodes-nothing-is-a-challenge`: gemma3:12b 65 of 114 at the current hash 8805d9c5. **qwen3.5:9b 0 of 20**, qwen3:8b 0 of 20, qwen2.5:14b 0 of 5, qwen3.5:4b 0 of 10, llama3.1:8b 0 of 15, all at older hashes.
- `ACT-CR-quote-the-tests-code`: gemma3:12b 95 of 95, qwen3.5:9b 5 of 5 at an older hash. This case's test contradicts its own comment, so a word match finds it.
- `L1-CR-a-kept-behaviour-passes-by-its-kept-line`: qwen3:8b 0 of 95. `L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist`: qwen3:8b 0 of 90.
- `L1-CR-fail-names-its-criterion`: qwen3:8b 95 of 95, and qwen3.5:9b 0 of 15 at an older hash.

`python -m rota.tools.casestatus`, read under qwen3:8b with the gemma3:12b pins kept, at the live records of 2026-11-04 (observed):

- FAIL 0 of 5: doubtful-criterion and kept-behaviour.
- PROV 4 of 5: broken-pushed-commitment and purpose-in-a-docstring. PROV 5 of 5: finish-the-review.
- Green: quote-the-tests-code 5 of 5. encodes-nothing 3 of 5, at its threshold. challenge-a-claim 5 of 5. dismiss-a-finding 4 of 5. fail-names-its-criterion 5 of 5. pass-a-conforming-diff 5 of 5.

**So the register has measured the dry runs' Critic model on the act of a vacuous test, and it failed 0 of 20.** The gate does not show that, because the case is pinned to gemma3:12b (reasoned). The 1 of 5 of sample 4 is the only right act of qwen3.5:9b on a weak test in these records (observed).

**Does a case measure a pass on a test that proves nothing? One measures the act, on another shape and another model.** `L1-CR-a-test-that-encodes-nothing-is-a-challenge` asks for the right act on a vacuous test. It has a diff, so the test is not the only evidence. It is pinned to gemma3:12b, and the dry runs' Critic is qwen3.5:9b. No case seeds a claim or an empty diff. The second look of pass 2 said so too: "no register case holds a claim" (observed: `plans/stack.md`, frame 360's line of 15:39). `L1-CR-a-kept-behaviour-passes-by-its-kept-line` pays for a `test:` pass, the route that s154 took. No case asks that the test encodes its criterion first (observed: its `expect`).

**Frame 201 is a different act in the same family.** Its heading: "Two Critic cases pass a criterion the diff contradicts". Its ends-when: "the seat reads a diff that contradicts a criterion as a question or a fail ... both cases at their threshold, 3 of 5 and 4 of 5". Its last status line: "2026-10-24 18:19 (rota-e9): Night 2. Not seen." (observed: `plans/stack.md` 5148 onward). Frame 201's act is a pass on an added line that contradicts its criterion. Its fix, the hold, turned the recorded case to a fail in 3 of 3 runs. The hold quotes the seat's line and asks the question. The hold skips `test:` values. So the false claim passes through the one route that frame 201's fix does not cover (observed: `_first_pass_hold`; reasoned).

## G. The explanation

**What the structure gives the Critic:**

1. **No instrument.** On a claim the diff is empty, and `code.read` is "Critic's entire view of the implementation". The Critic reads no source of the code under test, runs nothing and writes no probe. A true claim with weak tests and a false claim with weak tests give the same view (observed: section B; reasoned).
2. **A claim with no source.** "Every claim cites a source" (composition), and the Developer's claim cites none. The Critic has no line to check and no row to quote in a challenge (refusal 4).
3. **A door that leads to a pass.** The `test:` route asks bound, live and passed. Refusal 1 names that route and asks only "passed". The hold skips `test:` values, and its commitment question has one answer on an empty diff. A pass costs nothing extra, and a fail costs a `claim_encodes` call (observed: section C).
4. **A brief with no word for the case.** `review.md` says nothing of a claim or an empty diff. Step 1 comes before step 2, and the `test:` route depends on a step that comes later. The note states a fact and asks for no act (observed: section A).
5. **A register that does not measure the act on the seat's model.** No case has a claim. One case pays for a `test:` pass. The weak-test case is pinned to gemma3:12b, and its recorded runs on qwen3.5:9b gave 0 of 20 (observed: section F).
6. **A wake that puts the view last.** The inherited rows fill about 90 per cent of `tests.load`, and `code.read` sits last. On the live arm, no cut fell (observed: section E).

**What the model does with it:** in 4 of 5 samples and in s154, the model passed first and never read a test against its criterion. Sample 4, at 0.6, read the bodies and found the weak tests. So qwen3.5:9b can do step 2 with this view, at 1 of 5 at 0.6 and at 0 of 1 at temperature 0 (observed).

**What a stronger model would change:** how often step 2 runs before the pass. Frame 201's interview found qwen3:30b-a3b right where qwen3:8b was wrong, on one case (observed: `plans/stack.md`, frame 201's line of 2026-10-23 12:57). A stronger model could then challenge the weak tests more often. That stops a false claim that rests on weak tests. It also stops a true claim that rests on weak tests (reasoned).

**What no model can change:** with no source and no run, no reader can tell a true claim from a false one when its tests are weak. A strong model can only say "the evidence is empty" (reasoned: sections B and G item 1). The structure decides what follows from that sentence.

**Probes that would settle a point (none run):**

- P1. Replay s154 with `project_root` set to the arm's project, so that `code.read` shows `""` as on the live arm. 5 samples on qwen3.5:9b, about 7 minutes and no session context. It removes the replay's artefact and the wake cut from the count, with the replay's challenge query fixed to `from_role = 'critic' AND verb = 'challenge'`.
- P2. The same replay on a stronger model that is already on the machine, 5 samples, about 10 to 15 minutes. It settles the model's part: how many samples read step 2 before a pass.

## H. Doubt, and one proposal

**Doubt.**

- The sample is small: 1 live session and 5 replays of one batch on one model (observed).
- The replay differs from s154: a wrong base diff and a cut wake. Samples 1 to 3 never called `code.read`, so their view equals the live view plus the note, less the empty `code.read` block (reasoned). Sample 5's late doubt rests on the wrong diff (observed).
- The qwen3.5:9b counts of section F are at older prompt hashes, so they are stale for today's brief (observed: the hashes).
- Not counted: how many landed passes over the night databases used the `test:` route for every criterion. The reach below counts merges, not routes.
- The tests of the batch contradict each other: run 1's c1 and c3 contradict, so a right test of each fails on any code (observed: `plans/design-false-claim-2026-11-06.md`, shape F). A challenge that lands goes to a Tester who cannot write both right.

**Reach.** The claim path: 1 of 19 recorded merges, and 1 of 1 claims false. Weak-only evidence: 3 of 19 merges hold only tests that pass before the change, and 21 of 66 criterion tests pass at the fork (observed: `plans/arm-run1-merge-read-2026-11-06.md` line 14). On a change batch the Critic has the diff, and frame 201's hold asks about each line. On a claim the Critic has nothing to hold a line against. So the gap is the claim path, 1 of 19, and the `test:` route that it takes (reasoned).

**Proposal: shape E, a claim cites one code line for each criterion.** The place: `code_commit`'s claim branch, `rota/roles/api.py` about 26427 to 26448. A claim carries `evidence={<criterion>: 'kept: <one line>'}` for each live criterion, and the door checks each value with `_route_fault`'s `kept:` rules at the fork. `tests.load` and the claim note for the Critic show "c3: the Developer says this line does it: <line>". The Critic's pass on a claim then names `kept:` lines, and frame 201's hold quotes each line and asks the question. That hold turned the recorded case to a fail in 3 of 3 runs (observed: `_first_pass_hold`'s docstring). The design page's own rule for what comes next: "If D's replay shows the Critic claims `True` by rote, E is next, because a cited line is a source that a seat can check" (observed: `plans/design-false-claim-2026-11-06.md` line 165). E departs from no ruling and applies the composition's "Every claim cites a source" (observed: the same, shape E).

- **Price.** About 5 cycles: the design page amendment 1, the door, the Developer's brief and the Critic's lines 2, a review 1, and the replays of s152 and s154 1 (reasoned: shape F's cycles on the same files). To his attention: none.
- **How it fails.** A weak Developer cites a near line, for example the 75-octet line of `_foldline` for c3. A Developer that cannot cite falls back to an empty start, so dry2's stall can return (observed: shape E, "How it fails").
- **First.** E changes a door's result and a prompt's shape, so a design page amendment comes first, by C76 step 3b. P1 runs before the amendment, so that the amendment starts from a true count.

## Not read

- The gate in `.rota-gate.log`, which is still running.
- `s1/` was not opened apart from `s5/`, because `s5/sample_1` holds the same temperature 0 run.
- The landed passes over the night databases by route.

## Usage

About 115k of context, no sub-agent, no model run, no code edit (observed).
