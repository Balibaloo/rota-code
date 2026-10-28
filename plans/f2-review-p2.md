# F2 review, pass 2: f53ff5b0 and 2a76ad46 on f2b, against 442e32b0

**Verdict: READY.** The three edits match the proposal. The replay of 240 calls turns 17 refusals into lands and 3 lands into refusals. All 20 new answers are right on his words. No finding inside the commits is high. Two low findings ask for one test and one rename.

## (a) Verdicts on the points

1. Match: yes. Edit 1, edit 2 and edit 3 do what section 6 says. Four changes outside the proposal's names are listed below.
2. Replay: 17 refusals become lands, and 3 lands become refusals. Each of the 20 new answers is right on his words.
3. Backtick and common word: both refuse the contest of line 4. A shared identifier spares the line in any sentence, an agreement included (finding 1).
4. Law 6: holds. The door takes his reply verbatim from `messages`. The door writes no verdict. It refuses or it lands the verdict of the seat.
5. Tests: the four changed tests encode the new shape rightly. A door that lands every call turns 4 of 7 tests red in `test_f2_rulings_words.py`. The sparing half of the name rule has no test (finding 2).
6. Foreign hunks: none. Each hunk is one of the three edits, the parameter `item_texts`, or a test of them.
7. Stale cases: casestatus in the worktree reports 0 stale and 166 never measured. The worktree has no measurement record, so the tool cannot name a stale case (finding 6).

### Point 1, the changes the proposal does not name

- Edit 1 also feeds his reply to every later reader of `words`. The files check, the batch check, the note revise span at api.py 13800 and `_shift_acts_conflict` at 13729 now read his reply. The replay shows the effect. s139 and s177 of night 171 moved from a files refusal to "lines N have no ruling". s171 moved from "words is empty" to the refusal of an approve on a faulted line. Each new text is right.
- Edit 1 makes the shift-page offer at api.py 14094 to 14106 unreachable for a reply with text. The f25 test now asserts no offer (finding 4).
- Edit 1 does not reach the early path for a page with no line, api.py 13567 to 13585. That path still stamps `words` empty (finding 5).
- Edit 3 also spares a line when the shared name sits in a sentence that agrees with the line (finding 1).

### Point 2, the replay table

The harness replays every `rulings.rule` call that `reach.run` extracts from the turns, 240 calls. Each call runs on an in-memory copy at the state of its trigger. The parent tree is an export of 442e32b0. 214 of 240 parent results agree with the recorded result. The rest differ by the state after an earlier land in the same session.

| Night, session, calls | His reply | Parent | 2a76ad46 | Right? |
|---|---|---|---|---|
| 170 s113, 3 calls, m28 | line 3 "is vague ... replace it with the actual rule: use Roaming ..." | words is empty | lands, line 3 contest, rewrite on that span | yes |
| 170 s228 call 3, m103 | "please drop line 6. Line 8 misread me on line 3" | words is empty | lands, drop on line 6, remove on line 8, each on his span | yes |
| 171 s180, 3 calls, m70 | "Line 2 quotes an answer ... I never gave, so please drop line 2." | words is empty | lands, line 2 contest, drop on "Drop line 2" | yes |
| 171 s210, 3 calls, m95 | lines 2, 3 and 5 faulted, lines 1 and 4 right | words is empty | lands, 2, 3, 5 contest, 1, 4 approve | yes |
| 172 s119 call 3, m34 | lines 2, 3, 4, 6, 7, 10 wrong, lines 8 and 9 right | words is empty | lands, those six lines contest | yes |
| 172 s271, 3 calls, m129 | "Line 11 is wrong ... keep line 4 as it is" | words is empty | lands, line 11 contest, remove on his span | yes |
| 172 s275, 3 calls, m132 | "Delete lines 9 to 15 ... Correct line 18" | words is empty | lands, drops on 9 to 15, rewrite on 18 | yes |
| 170 s215 call 5, m91 | line 6 "quotes an empty answer I never gave" | lands, line 6 act removes a test, on the whole reply | refused, the act of line 3 has no span | yes, the act of line 6 is not his ask |
| 170 s222 call 4, m97 | "please drop all three formatting tests" | lands, acts on lines 2, 5, 9 with no span | refused, the act of line 2 has no span | yes, the seat must copy his span, one more turn |
| 172 s258 call 8, m121 | "put back the two removed lines" | lands, line 4 contest and remove on line 12 | refused, the act of line 12 has no span | yes, the target case |

Totals: 17 refusals to lands, 3 lands to refusals, 13 refusal texts changed, 0 errors.

## (b) Findings

1. **api.py 13160 to 13164, low. CONFIRMED.** The name rule spares a criterion line when an unnumbered sentence shares a name, whatever the sentence says. On m121 with the last sentence "The `format_filename` docstring is fine as it is.", a contest of line 4 lands. "Everything about format_filename is fine." also lands it. The same name also spares line 3. The parent spared every criterion line on any sentence, so this is narrower and not a regression. No call of nights 170 to 172 reaches it. Fix: spare only when the sentence with the name is not an agreement, by `_BARE_AGREEMENT` or a matched reading.
2. **tests/rota/test_f2_rulings_words.py, low. CONFIRMED.** No test pins the sparing half of edit 3. A mutant that passes `item_texts={}` keeps 331 of 331 tests green in the 11 test files that reach the naming door. Fix: add one test where an unnumbered sentence names a criterion line by its identifier and the contest lands.
3. **tests/rota/test_frame234_verdict_lines.py 481, low. CONFIRMED.** `test_an_unnumbered_sentence_spares_a_criterion_line` passes with no call to `_unnamed_contest`. A spy saw zero calls. Its name states a rule it does not reach. The proposal named this test to change, and the diff leaves it. Fix: rename the test, or rewrite it on the shape of finding 2.
4. **api.py 14089 to 14109, low. CONFIRMED by the f25 test change.** The shift-page offer fires only when the body of the trigger is empty, and then `_his_shift_words` finds nothing. The branch is dead. Fix: delete the offer branch and keep the plain refusal for an empty reply.
5. **api.py 13567 to 13585, low. PLAUSIBLE.** The path for a page with no line runs before edit 1 and stamps `words` empty. Every other ruling now stamps his reply. A reader of `rulings.words` sees two shapes. Fix: move edit 1 above line 13567.
6. **Point 7, low. PLAUSIBLE.** casestatus cannot judge staleness in the worktree. `L1-LI-a-separate-request-is-later` changes shape, because the f25 test now asserts no offer. Fix: run the gate on 2a76ad46 with a baseline at 442e32b0.
7. **tests/rota/test_f2_rulings_words.py 19 to 22, low. CONFIRMED by reading.** The file skips when `clickI_night172.db` is absent. The register is not tracked, so a clean clone runs none of the 7 tests. Fix: say so in the docstring, or copy the two pages into a fixture.

### Outside the points

8. **api.py 14008 and 14059, high, outside, pre-existing. CONFIRMED.** The naming door reads the `words` of the seat, not his reply. With his reply m121 as recorded, the words of the seat plus "Line 4 is wrong too." land a contest of line 4. The parent does the same. The comment at 13761 says that the `words` argument proves nothing. Fix: refuse passed `words` that `_words_from` cannot find in his reply, or read `his` in `_line_refusal`.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/2568e043-732b-4ab6-9d66-bc0069e83123/scratchpad/rv2/`.

- `parent/`: `git archive 442e32b0 rota`, the parent tree.
- `replay_all.py`: replays 240 calls on in-memory copies at the parent and at the head. The output is in `par.json` and `new.json`.
- `plant.py`: six planted last sentences on m121, with and without the `words` argument, at the head and at the parent (point 3).
- `plant2.py`: his recorded reply, with one extra sentence in the `words` of the seat (finding 8).
- `mutant_land.py`: a pytest plugin with a door that lands every call. 4 of 7 tests fail.
- `run_tests_at.py`: runs the new test file on the parent code with no pytest. 5 of 7 fail.
- `spy_unnamed.py`: a spy on `_unnamed_contest` in the frame 234 test. Zero calls.
- `mut_noname.py`: a mutant with no name spare. 331 passed in 11 files.
- At the head, the 7 new tests pass. The four changed files and frame 234 give 180 passed and 11 xfailed.
- casestatus in the worktree gives 0 stale and 166 never measured.

## (d) Usage

Input about 80k tokens, output about 15k tokens, about 95k in total. These are estimates. The cap was 80k, and the replay and the probes used the rest.
