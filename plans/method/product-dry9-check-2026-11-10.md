# Dry run 9 against the product map, 2026-11-10

## Result

1. Dry run 9 does not break the map's skeleton, and it disagrees with three of its statements. The corrected C4, revised point 5 and the gemma line of the model read do not fit the run.
2. The stop by the last act is a known class: the Developer gave up with code still red, and the batch parked. The stop by the root is a new class: a made function name that the doors then enforce.
3. The map has no place for five things: a made surface, a stop word that is no act, a check that no code passes, a drop that does not reach its test, and a page that says "Before I build this" while the build runs.
4. The person was an Opus session with the key closed, so the run tests no person (observed: the read page, line 3).

## 1. Dry run 9 in ten lines

1. Date: 2026-11-10, 07:20:02 to 10:01:03, seven turns (observed: `turns/t1.txt` to `t7.txt`, `config.created_at` 07:20:21).
2. Repository: icalendarI, a clone of `D:/tmp/rota-live/icalendar` reset to `99619246`. Three of its tests were red at the base (observed: `dry9_start.sh`, m62 line 10).
3. Request: "When icalendar writes a long line, fold it at a space where it can, so that a word is not split, and keep everything else as before." (observed: `messages` m1).
4. Models: Developer, Tester, Terminologist and Critic ran qwen3.5:9b. Architect and Vision Keeper ran qwen3:8b. Liaison ran gemma4:12b-it-qat (observed: `sessions.model`, `config.model_routing`).
5. Seat: session c1a39439 as the Principal, with the key closed (observed: the read page, line 3). The seat never typed `_foldline`. It described the function in words (observed: m24, m44).
6. Pages: 13 to the person, 11 answered, m55 and m82 open at the end (observed: `messages`, to_role principal).
7. Batches: 1, bg_1 on `folds_long_lines`. Sessions: 236, of which 17 are Developer sessions (observed: `batches`, `sessions`).
8. Merge: none. bg_1 is `deferred` at `68e894aa`. Attempt 10 has 6 of 166 tests red (observed: `batches`, `test_run_journal`).
9. Stop: at the Developer, `do:park` "bg_1 is past its cap and its ladder is spent" after `tests_failing` was quarantined at 3 attempts (observed: t6 lines 41 and 45).
10. The run went on after the park. The seat's "stop here" landed as a contest, and the Terminologist's 4 `criterion_owed` keys then quarantined at 3 attempts (observed: t7 line 41, `tick_attempts`).

The database and the read page agree on every count I checked, except one. The read page says "30 exclude rows of m24". The database holds 29 per source, 29 `reading` and 29 `landed` (observed: `ruled_refs` r_m24). The read page's "9 approve rows" for "ok" is the count per source, and the table holds 18 (observed: r_m63).

## 2. The claims and the readings against dry run 9

Corrected claims of "Step 5: the break test":

- **C1 agrees.** Each named criterion changed: cr_1 and cr_2 went to v2, and cr_4 and cr_5 were retired by r_m44. The guess changed to the m26 rows. The glossary revise r_m15_2 left `parameter#src_icalendar` at v1 (observed: `criteria`, `touch_guesses`, `glossary_terms`). New detail: the guess kept 2 of the 29 excluded paths, and the drop of cr_4 and cr_5 did not retire their tests. `retired_by` stays null on both (observed: `tests`, `faults` f_1b281f9bec, f_c7ca9c5e50).
- **C2 says nothing on the merge.** No batch merged, and `verdicts` holds 0 rows. All 15 Critic sessions are onboarding `tick:challenge` (observed). The soft input agrees: tests ran to v5 and v4 after 12 challenges, and two checks pass on code that does not fold (observed: `tests.version`, `challenges`, m62 lines 7 and 9).
- **C3 agrees.** Onboarding wakes are 100 of the 158 sessions before the first Developer session, 122 with the Critic challenges and term collisions. Those wakes take about 30% of the model time (observed: `sessions.wake_kind`, `turns.ms`; the class set is reasoned). A constraint or glossary text reaches 18 of 35 Developer and Tester first prompts (observed).
- **C4 as corrected disagrees.** No criterion names `_foldline`, and no commit goes to `string.py`. The criteria name `src/icalendar/parser/property.py::fold_long_lines`, and the commits go to `parser/__init__.py` and `parser/property.py` (observed: `criteria.surface_refs`, `tool_calls` code.write). The original C4, "a fact that the person gave and that did not arrive", fits better (reasoned).
- **C5 agrees in part.** m82 names the wake that failed, "the team could not rewrite the check ... after 3 attempts", and not the rule behind it (observed: t7 lines 50 to 53). The park page names the cap, "The team tried 10 times", so the limit does show there (observed: t6 line 104). The one unresolved question, m19, did not climb. The 6 open faults show on no page (observed: `messages`, `faults`).

First reading, "The reading at this resolution":

1. **Agrees.** The seat is a model with a closed key, and the repository is prepared (observed: the read page, `dry9_start.sh`).
2. **Agrees, with two gaps.** Each session has one wake, and the index holds `string.py::_foldline` (observed: `sessions`, `code_index`). The touch note m32 says "Before I build this", and the Developer began in the next session. ROLES.md says "nothing waits on the answer", so the design allows this, and the page words do not (observed: s158 `msg.present_principal`, t5 lines 23 to 25). The Liaison's reading approved lines the seat did not name: r_m64 approves cr_1, cr_2, cr_3 and cr_6 from "Line 10 is still wrong ... stop here", and r_m63 approves the two red checks (observed: `ruled_refs`).
3. **Says nothing on the trend.** The seat contested on m24, m44 and m64, and the run did not merge. This fits "the measures that show progress use a seat that says yes" (reasoned).
4. **The care loop disagrees in part.** No contest cancelled bg_1, and 3 of 13 pages repeat a question, not half (observed: the read page, count 4). **The judgement loop agrees** (see C2). **The cost loop agrees in part.** The 6 items repeat dry run 8's text word for word, 6 of 6, and the glossary shares 59 of 59 terms (observed: both databases). The seat answered 5 pages before the first Developer session, m2, m4, m14, m18 and m22, which is under "6 to 16" (observed: t1 to t5).
5. **Agrees in part.** The fold now merged 0 of 8. The Developer found `_foldline` in 4 sessions, and no commit changed it (observed: the read page D9-1, `tool_calls`). The batch stopped on removed imports and on checks that no code passes (observed: the read page D9-3 and D9-8).

Revised reading, "The reading, revised after these three reads":

1. **Agrees.** No person sat in the seat. Nothing merged, so no page could say what merged (observed).
2. **Disagrees as written, and agrees with the model read's correction.** The stop shows at the Developer. The cause sits upstream: s154 wrote the surface `fold_long_lines`, a name that is not in the index, and `criteria.specify` returned OK. The commit door then sent the Developer to that name (observed: `code_index`, the read page D9-1).
3. **Agrees.** Both stop pages name the step in plain words. Neither names the made name, the touch set or the owed criteria (observed: t6, t7). "wrote its own tool results" ended 7 of 17 Developer sessions, and 0 pages carry it (observed: `turns` last completion, `messages`).
4. **Says nothing.** No merge. The head touches files outside the landing set and adds no `news/` entry (observed: the read page, count 35).
5. **Disagrees in direction.** The seat's word did not destroy work. It could not stop work: after "stop here, I accept the stop", 31 sessions ran, and s223, s226 and s233 called `code.write` on the parked batch (observed: t7, `tool_calls`).

Model as a variable: the Developer ran qwen3.5:9b again (observed). 6 of 17 Developer sessions landed a commit, against 27% (observed: the read page, count 34). The Liaison ran gemma4:12b-it-qat on first prompts of about 1,300 to 7,400 tokens, and no session hung. This disagrees with "Gemma 12B hangs on it past 1,536 prompt tokens", if the model is the same (observed: `turns`, chars divided by 4; the identity of the model is reasoned). The read page tests three builds on one run, which the map says "cannot test a change" (reasoned: the read page, section 6).

## 3. The class of the stop

- By the last act of the batch: "The Developer gave up with code still red", one of the 46 (observed: t6 lines 41 and 45, `batches.status` deferred).
- By the last act of the run: the Terminologist's rewrite of the owed criteria quarantined after the seat's contest. The nearest class is "the seat's contest cancelled the batch after a give-up", and the batch was not cancelled (observed: `tick_attempts`, `batches`). The class does not fit.
- By the root: new. A role upstream of the Developer wrote a made surface, and three doors enforced it in a chain (observed: the read page D9-1). The stops read has no class for a wrong test or a door chain. Its own limit says "No query separates wrong code from a wrong test".

## 4. What the map has no place for

- A made surface. A criterion can name a function that the index does not hold, and the doors then make the team build that function (observed: D9-1, `code_index`).
- A stop word is no act. "stop here" landed as `contest` with `exclude`, made 4 criteria owed, and woke 31 sessions (observed: r_m64, t7).
- A check that no code can pass. test_fold_space asks for a cut at 75 and a space at 70, "assert 70 == 75" (observed: m62 line 3). The map has a test that is green on wrong code, and not a test that is red on any code.
- A drop that does not reach its test. `tests.retire` was refused 195 times, and the kept cr_4 test broke an inherited doctest (observed: the read page D9-9).
- A page that promises a build order or a stop that the run does not keep. These are "Before I build this" on m32 and "The team then stops here and tells you" on the park page (observed: t5 line 72, t6 line 117).
- The park page says "2 of its 6 checks still fail" and shows 4 checks, because the two dropped tests still count (observed: t6 line 104, `tests`).

## 5. What rota told the person at the stop

The park page, t6 lines 104 and 116 to 117:

> This change stopped. The team tried 10 times, and 2 of its 6 checks still fail.
> The last attempt: src/icalendar/tests/test_fold_no_space.py failed: AssertionError: assert '\n' in 'aaaa...'. src/icalendar/tests/test_fold.py failed: AssertionError: assert 70 == 75.
> Reply 'ok' if every line says what you want. The team then stops here and tells you.

The last page, m82, after "stop here, I accept the stop", t7 lines 49 to 54:

> The team gave up on a step:
>   2. the team could not rewrite the check "The one function that writes a content line out as text must cut at the last space before the limit when there is one." for the code you corrected after 3 attempts
> (lines 3 to 5 say the same for cr_2, cr_3 and cr_6)
> Reply 'try again' on a step to run it again. Reply 'drop' on it to stop it.

Neither page names `fold_long_lines` as a made name, the touch line, or "wrote its own tool results" (observed).
