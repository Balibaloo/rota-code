# Night 159's read

Rota workflow, read by the meta workflow. Night 159 ran cold from
`C:/Users/roman/rota_night159` at 73a4801f, 15:29 to 17:36 on 2026-10-23,
on `D:/repos/_AI/sample_repos/clickI`, with the agent principal on Opus.
73a4801f is the branch head with frame 302 reverted. It holds frame 283's
door at a00baecb and not passes 4 to 4d (observed: `git merge-base
--is-ancestor`). Frames 302, 303 and 306 are not in the night's code
(ruled: the launch script and the brief). Records: `.rota/clickI_night159.db`
(opened read-only), `.rota/night159.log`, `.rota/night159_report.txt`,
`.rota/night159_truth.txt`, `.rota/clickI.principal.jsonl`, and the clickI
repository (git read-only, one run from a `git archive` copy). Read on
2026-10-23 by one agent on Opus with three extract agents on Opus. Their
extracts are in the scratchpad `n159/` directory: `a_bg2.md`,
`b_bg4_liaison.md`, `c_doors_merge.md`. The synthesising agent checked
the turns of s239, s240, s241, s366 and s367, the words of m117 and m118,
the stored body and run of the bg_4 red test, and the pages m105 and m212
as he saw them.

**The result.** One item merged, against 2 on night 158, and that merge
holds his change and nothing else: compact JSON from the standard `json`
module (observed: a run of ed8b021, section 2). The two other items died
in the test loop, and neither died for a code fault alone. bg_2's code was
right by his words at every commit, and its tests could not pass against
any code. bg_4's code was wrong, but its last test could not pass either,
and its one criterion holds a sentence of his that describes the old test
as a rule (observed: sections 2 W1 and W2). The night spent 40 of his
answers in the walks for 1 merge, against 22 for 2 on night 158. Frame
283's door and frame 304's door did not fire. So the night did not test
the first, and the sign of the second came back in a stub shape the door
does not read (reasoned: section 1).

## 0. The night in numbers

| Measure | Value |
|---|---|
| Phases | onboarding (107 steps, 3 asks), walk 1 (38 steps, 5 asks, merged bg_1), walk 2 (141 steps, 14 asks, quiet), walk 3 (206 steps, 21 asks, quiet) |
| Steps, asks | 492 steps, 43 asks, 40 of them in the walks (night 158: 348 steps, 25 asks, 22 in the walks) |
| Batches | 4: bg_1 `echo_json` merged at d58b48d4f2; bg_2 `confirm_default_on_eof` deferred twice ("its ladder is spent", walk 2 at c29d89dd, walk 3), resumed, `running` at 89da5b89fc with 1 test red; bg_3 `bg_2_summary` abandoned, "its item is no longer schedulable"; bg_4 `version_option_show_python` deferred at b5f0be71c3 with 1 test red |
| Merges | 1. "rota: deliver bg_1" ed8b021, tests 13ace86, code d58b48d (observed: `.rota/night159_truth.txt`). Night 158: 2 |
| Sessions | 413 sessions, 1897 turns (night 158: 291, 1354); Liaison 117, Vision Keeper 90, Terminologist 66, Architect 46, Tester 44, Developer 32, Critic 17, Researcher 1 |
| Batch sessions | bg_1 13, bg_2 44, bg_3 6, bg_4 56, no batch 294. By refs about 120 sessions touch bg_4 (observed: extract B, a refs filter) |
| Principal | 40 calls on Opus in the walks (5, 14 and 21), 4 onboarding calls replayed |
| Quarantines | constraint_zero (s1), and three bg_4 "The team stopped work" pages (s299, s330, s346); developer tests_failing on bg_4 quarantined once (observed: report, tick attempts) |
| CYCLE lines | 2: Liaison converse on page m116 (walk 2), Developer tick:tests_failing on bg_4 attempt 7 (walk 3) |
| Made up | 115 turns in 47 sessions; "ran anyway: 0 writes after an invention", 0 landed commits (night 158: 67 turns in 33 sessions) |
| Repeats | "15 wakes repeated, 44 sessions, 29 of them repeats" (night 158: 12, 38, 26) |
| Window | "dropped to fit the window" 198 turns in 33 sessions (night 158: 116 in 19); dangling pointers 72 turns in 14 sessions (s280 11, s123 10, s164 9) |
| After the end line | 212 turns in 96 sessions hold "Your work for this session is complete" (night 158: 129 in 54) |
| Rota failures | "Rota itself failed 17 times": 17 open `faults` rows (section 2 W8) |
| End lines | walk 1 "Done: 1 change built, tested and merged"; walk 3 "Stuck: bg_4 is parked" and "Stuck: the code is written, but 1 test is still failing" |

(observed: `.rota/night159.log`, `.rota/night159_report.txt`, `sessions`,
2026-10-23.)

## 1. The held frames

**Frame 283, the removal door at a00baecb. 0 of 9 and 0 of 1, but the door
never fired, so the night did not test it.** `_unruled_removal` ("No
criterion, request or ruling of the principal names") fired 0 times
(observed: extract C section 1, the turns and the log). No landed commit
removes a base statement. The nine commits change base line 105 of
`termui.py` inside a `try` and base line 545 of `decorators.py` with a
suffix, and both statements stay (observed: `git diff 2c8cd3a <sha>` for
each). Commits that land a removal of a base statement with a note as the
discharge: 0 of 9 (night 158: 1 of 10). Merged changes that hold a removed
base statement no ruling names: 0 of 1 (night 158: 1 of 2). The route
sentence "A note does not allow a removal" came 4 times from the other
commit door, `_unread_drop_refusal`. s164's fire was right: its write
removed two base statements of `_readline_prompt`. s188's three fires
protected `return default`, the batch's own earlier line and not a base
statement (observed: `drop_notes.lines`). No seat took the ledger route,
and the runner discarded both writes (observed). Passes 4 to 4d were not
in the night's code (observed).

**Frame 304, the arrange door. 1 batch of 4 deferred with the code right,
the same as night 158's 1 of 3, and the door fired 0 times.** bg_2's code
was right by his words at 1a674dd204, 0f6e3e013b, c29d89dd77 and
89da5b89fc: the flag is off by default, the call returns `default` when the
flag is on and stdin is closed, and it raises `Abort` when the flag is off
(observed: extract A section 1, the diffs). The three red tests at the
walk-2 park could not pass against any code. Two used a plain `class
FakeStdin` with no `readline`, and one called `confirm()` with no `text`
(observed: s185 turn 1 and s189 turn 1, `tests.load`). The door reads the
spec of a mock, so a plain class stub is outside its predicate (reasoned:
`api.py` 14850 to 14876). No body was refused, so no refused test could
have passed. By the frame's third clause this is the frame's own sign with
a new stub shape: the predicate is not the fact "no code can pass this
test", cause 8 (reasoned: W2). bg_4 is not counted here, because its code
was wrong (observed: W1).

**Frame 305, the line reader and the re-present. Not met on either count:
2 wrong line-reader refusals (from 1), and 4 Liaison sessions that end on a
repeated right refusal of a line-2 contest (from 2).**

- **s241 on m118.** His words: "Please delete line 7 ... and delete line
  14 ... In lines 3 and 4, replace "raises a usage error" with "aborts" ...
  In lines 6 and 8, change the checks". The door said "The words fault
  lines 6 and 8. ... Rule lines 6 and 8, and approve the rest." four times
  (observed: s241 turns 2 to 5). The reader cued "In lines 6 and 8, change"
  and missed "delete line N" and "In lines N and M, replace". So the door
  told the seat to approve four lines he asked to change (reasoned). The
  cycle 1 page reads this right.
- **s331 on m185.** His words: "The test on line 2 is right and should stay
  as it is". The door said "The words fault line 2, "should"", so the
  ruling r_773e018bed marks the criterion `revise` against his words
  (observed: extract B section 2).
- **The four line-2 sessions.** s239 and s240 (m117), and s366 and s367
  (m213). Each refusal was right. In each, `recent_chat` held an earlier
  page's reply with line numbers. s239's held m106, "Line 1 is wrong ...
  Line 2 should say", and s366's held m164 "For the check on line 2" and
  m196 "line 2 is what needs correcting" (observed: turn 1 `user` of each).
  So all four are frame 272's cause, as the frame's status of 14:08
  already judged (reasoned).
- **The re-present.** m116's re-present named no line, and m212's named
  "line 3", the line his words were about (observed: the pages). The text
  held.

So the frame's own texts held, and both wrong refusals come from the
reader's cue set, one word or phrase per night: "drop" on night 158,
"delete" and "replace" here, and "should" inside "is right and should
stay" (reasoned). This is the shape that frame 283's review 6 called "a
fit and not a rule", where the verb list leaked a word at every review.

**Frame 308, the ruling-answer door. 0 partial answers of 12, night 1 of
3, and the door fired 0 times.** 15 Terminologist sessions woke on a relay
whose ruling marks a criterion `contest` or `revise`. 12 answers landed,
and all 12 carried every ruled criterion (observed: extract B section 5).
The count is met. But 5 of the 12 (m218, m227, m232, m243, m256) went out
after the session's respecify was refused, so the Tester got the
criterion unchanged. The door checks the refs and not the change, and
that hop is bg_4's wall (reasoned: W1).

**Frame 201, the hold on a Critic's first pass. 0 wrong passes, 0 Critic
sessions with no verdict after the hold, night 2 of 3, on one verdict.**
The hold fired 2 times, both in s128, both on a right pass of bg_1. The
seat answered "does what the criterion says" and the pass landed (observed:
extract C section 3). s127 ended with no verdict before any hold, because
frame 180's door refused `import json` as a plain import four times, and
that check runs first (observed). The sample is one verdict in the night.
After its verdict s128 sent the pass three more times and the runner
refused each, "one commit gets one verdict" (observed).

**Frame 301, the encode stdin door. 0 of 12, night 2 of 3.** 12 refusals
held the stdin text: s170 4, s253 3, s278 2, s406 3 (observed: extract A
section 5). No refused body ran `confirm()` inside a click command under
`CliRunner().invoke(..., input=...)`. s253's three bodies used
`runner.invoke(lambda: confirm(...))`, which is not a click command, so
each refusal was right (reasoned). The NameError guard fired about 30
times in 12 Tester sessions, a lower bound (observed).

**Frame 297, the discard. 0 confirmed page notes that cite uncommitted
lines, 0 inherited writes found, 2 discards, night 2 of 3.** The runner
discarded `termui.py` at the end of s164 and s188, with 0 "could not put
back" (observed: extract C section 4). One ledger note, l_a2e4f4d756 on
bg_4, says the show_python logic "was not committed because the file was
unchanged". Its tree state is not proven. s158 and s314 end on a write
with no discard line, also not proven (observed). The launch script calls
this the frame's first night, and night 158's read counts night 1 there,
so this is night 2 (observed: the two records).

**Frame 258, at its residue row: 0 page contests on a line no sentence
names.** Two contests landed from words with no line word: m22 contested
the request line from "use only the json module", which is the frame's own
mechanism, and m61 answered a clarify, which has no lines (observed:
`rulings`). Read lightly.

**Frame 143, at its residue row: 2 of 8 stored tests assert a value the
criterion does not give.** `tst_cr1_default_off` v4 asserts `False` when
the flag is off and stdin closes, and base `confirm` aborts there. The
`echo_json` test asserts the compact form, which bg_1's one criterion does
not name, and that is borderline (observed: extract C section 6). The
first one's cause is a criterion that never states the flag-off case,
because "aborts" never reached a criterion (W2). That is not an unread
default, so by its close clause it is not this frame (reasoned).

**Frame 140: 0.** No landed write carries a dropped note, and no project
test went red in 287 runs (observed: extract C section 6).

**Frame 272: 2 first sessions of 2, unbuilt, expected.** s239 took m106's
line numbers onto page m116, and s366 took m164 and m196's onto page m212.
Their repeats s240 and s367 also ended on it (observed: above). Cycle 1
and the two lost m212 sessions come from this cause.

**Frame 266: 0 Liaison sessions end on a repeated parse refusal.** 16 end
accounts across roles name a parse refusal. In the Liaison's s239 and s241
the parse refusal sat between door refusals, and each session ended on the
door (observed: the end accounts). Read lightly.

**Frames 302, 303 and 306, not in the night's code. All three signs show.**

- 302: 6 rows name a grain not in `code_index`, all on bg_4: the guesses
  `src/click/options.py` and `tests/test_version_option.py`, and the
  touch rows `version_option` and `test_version_option` (observed: extract
  C section 5).
- 303: 1. The Architect s189 sent a `propose` on bg_2. The Vision Keeper
  s190 then asserted `bg_2_summary`, a description of Click with both
  changes in it, as an in-scope item. Page m105 showed it as line 1 under
  "You asked", and batch bg_3 was built for it (observed: page m105,
  extract A section 2). He refused it at m106, and bg_3 was abandoned.
- 306: 3. "Aborts, not a usage error" (m46, m50, m83, m93, m112, m118)
  reached no criterion of bg_2. bg_4's criterion took his m196 sentence
  "prints nothing" as a rule, and his "line 3 is wrong" at m212, m223,
  m228, m238 and m251 never changed it (observed: W1 and W2).

## 2. Every wall the night met

**The test loop killed both unmerged items, and in each the loop could not
end by any code** (reasoned: W1 and W2). This is night 158's W2 again, on
the same item, with a stub shape the new door does not read. The night
merged 1 of 3 real items in 413 sessions, against 2 of 3 in 291 on night
158. The one merge is right (observed: section 0).

| # | Wall and sign | Sessions | Asks | Place by section 4 |
|---|---|---|---|---|
| W1 | **bg_4's criterion holds his words as pasted text, and no hop can change it.** (a) s349 put his m196 sentence "The check runs the command without the version flag, so the command does its normal work and prints nothing" into `ver_opt_show_py` as a rule: "When the --show-python flag is off (default), the command exits cleanly and prints nothing". The same criterion holds "expect the same message the option prints today" and his m164 second check, so it contradicts itself (observed: page m212 line 3). (b) He said "line 3 is wrong" five times. Each ruling landed and each relay carried his words. s382, s387, s398 and s412 re-sent the old text, and s370 kept "prints nothing". The surface door refused each respecify for an unrelated reason (a test named as a surface, a file outside the batch, an unknown symbol), and each session's answer to the Tester still went out (observed: extract B section 2). (c) The code appends " (Python 3.14)", with parentheses and no micro part, and the Developers s317 to s319 sent challenges, not a write (observed: cycle 2 page). (d) The last test, v8, asserts `output.endswith("3.14.2")` on output that ends with a newline, so no code passes it (observed: tests v8, tr288). (e) s331's wrong line-reader refusal made m185 a `revise` (frame 305). (f) s363's `model.adopt('bg_4')` was refused, "'bg_4' is not a row of model_areas", on the ladder's last rung (observed) | 56 batch, about 120 by refs | 16 (m136 to m251) | (a) and (b) are **cause 1**, his words change on a hop, at the Terminologist: the sentence that describes a test became a rule, and a respecify with his words never landed. The answer after a failed respecify is frame 308's residue, **cause 8**: the door's predicate is "the refs carry the criterion", and the fact is "the criterion carries the ruling". Frame 306's repair 1 is the open home, and it validates on night 160 first. Read whether it changes s382's hop before a new frame, 1 cycle. (c) is the cycle 2 page's new Developer route, **cause 5**, an interview of s317, 1 cycle. (d) is the same as W2's test that no code passes. (f) is not read |
| W2 | **bg_2's tests could not pass, and the one seat that saw why was refused.** The code was right at every commit (section 1, frame 304). At the walk-2 park the three red tests failed on `FakeStdin` with no `readline` and on `confirm()` with no `text` (observed: s185 and s189 turn 1). The Developer s185 found both causes and logged them. The challenge door refused its 9 `msg.challenge_tester` calls, because the quote was the arrange line and the door wants the line the run fails at (observed: extract A section 2). The rungs s189 to s196 then spent the ladder on `bg_2_summary`, the echo_json question m77 and four `model.adopt` calls, and no rung named the stub (observed). In walk 3 bg_2 resumed and parked again, then resumed. It ends with `tst_cr1_default_off` v4 red: the test asserts `False` with the flag off, and the code aborts, as he said six times (observed: tr325, section 1 frame 306). The passing cr4 and cr6 tests run with the flag off and `input='y'`, so they test nothing their criteria say (observed: extract A section 6) | 44 | about 19 (14 in walk 2, 5 in walk 3) | Three causes. The stub is **cause 8 on frame 304's door**: its predicate reads a mock's spec, and the fact is "no code can pass this test". A case on frame 304 with s189's `tst_cr1` as the red test, priced below. The refused challenge is **cause 8 on the challenge door**: a right diagnosis that quotes the arrange line is refused. No open frame holds it. A case on frame 304, which owns the arrange step, 1 cycle. "Aborts" never reaching a criterion is **cause 1**, frame 306's sign. The ladder spent on the summary is W3 |
| W3 | **A team row became a request, and its page fed the Liaison's line numbers for a cycle.** s189 proposed on bg_2, and s190 asserted `bg_2_summary` in scope. Page m105 showed it as line 1 under "You asked", and batch bg_3 was built for it (observed: page m105). His m106 "Line 1 is wrong ... Line 2 should say ..." refused it. Then `recent_chat` carried m106 with its line numbers to page m116, and s239 and s240 contested lines 1 to 3 of m116 from it, cycle 1 (observed: s239 turns 1 and 7). s241 then met the wrong line-reader refusal. In walk 3 the same pair recurs: s359 asserted `bg_4_summary` ("does not provide a graphical user interface"), which rode onto page m212 as line 4, and s366 and s367 contested line 2 of m212 from m164 and m196 (observed) | bg_3 6, cycle 1 3, s366 and s367 2, about 11 | about 6 (m101, m105, m117, m118, and two on m212) | Three frames, each with a fix built or named. The team row is **frame 303's sign**, cause 11, and its door is on the branch for night 160. The line numbers are **frame 272's cause**, cause 2, with its 2-cycle fix unheld. The reader is W4 |
| W4 | **The line reader's cue set leaks a word per night.** s241: "delete line N" and "In lines N and M, replace" read as nothing. s331: "is right and should stay" read as a fault. Night 158: "drop" placed on the wrong line | 2 (s241, s331) and the cycle round after s241 | 2 (m118 then m120; m185's revise) | **Cause 8 on the line reader**, frame 305's site, with a cause its texts do not hold. By the residue rule a case on frame 305, priced as a rule and not a word: invert the cue set as frame 283's pass 4d did, so a clause names a line and the reader then asks what the clause does to it, with m118, m185 and night 158's m104 as the red tests. 2 cycles |
| W5 | The guess and touch rows name grains not in `code_index`: `src/click/options.py`, `tests/test_version_option.py`, `version_option` | 3 (s265, s269, s273) | 1 (m136) | **Frame 302's sign**. Its door is on the branch, and it validates on night 160 |
| W6 | Frame 304's door and frame 283's door did not fire. The night cannot say whether either predicate is right on a live seat | 0 | 0 | Not a wall. Both stay validating (reasoned) |
| W7 | The instruments: section 12's M0 reads 6 of 7, and the report counts `test_runs` per commit with 35 runs where the log shows "39 test(s), 3 not passing" in walk 2. Extract A found no criterion-test run of walk 2 in `test_runs` (observed). Not reconciled | 0 | 0 | **Cause 13**, before a ratio rests on `test_runs`. 1 cycle |
| W8 | The 17 faults: 6 from confirm criteria that assumed options and sentinels against his ruling (s182 5, s180), 4 in the Tester's own tests or the turn limit (s125, s185 2, s303), 4 at the surface and glossary doors (s214 2, s116 2), 2 on bg_4 (s279, s292), 1 at the exact-words door (s405) | 13 | 0 | Mostly W1 and W2 seen from the seat. Not placed apart |
| W9 | Turns after "Your work for this session is complete" (212 turns, 96 sessions), window drops (198 turns, 33 sessions), dangling pointers (72 turns, 14 sessions), made up (115 turns, 47 sessions), repeats (29 sessions) | about 150 | 0 | All up by half or more on night 158 with 42% more sessions. Frames 139 and 208 hold the window signs. Not read |
| W10 | constraint_zero quarantine at s1 in onboarding | 1 | 0 | Not placed. Fourth night with the same page |

(observed: extracts A, B and C, `turns`, `tool_calls`, `rulings`, `tests`,
`test_runs`, `criteria`, the pages in `.rota/clickI.principal.jsonl`, the
clickI repository, 2026-10-23.)

**Walk 2's deferral, rung by rung.** The batch reached attempt 11 against
`loop_cap` 10 at c29d89dd (observed: the cycle 1 page, the log line 99).

1. The three red tests: `tst_cr1_default_off` (FakeStdin has no
   `readline`, then an assertion of `UsageError` against his "aborts"),
   `tst_cr4_plain_function_default` (no `text` in s185's copy, FakeStdin in
   s189's), `tst_cr6_simple_default_return` (`confirm() missing 1
   required positional argument: 'text'`) (observed: s185 and s189 turn
   1). The cycle 1 page names the right three. Its source `test_runs` does
   not hold them. The reds are in the `tests.load` prompts (observed:
   extract A section 1).
2. Developer s185, "attempt 10 of 10": three right `ledger.log` faults,
   nine refused challenges, one question to the Vision Keeper (m73), a
   commit with no code change (observed).
3. Architect s189, "attempt 11 of 10": loads, then `msg.propose_vision_keeper`
   on bg_2, m75 (observed).
4. Vision Keeper s190: asserted `bg_2_summary` in scope and reported m76.
   The Liaison s191 asked him m77 about echo_json and confirm. He answered
   "There's no conflict", and s192 approved bg_2. The Architects s193 and
   s196 called `model.adopt` on bg_2 four times (observed).
5. Vision Keeper s194, "attempt 11 of 10": reported m80, and the Liaison
   s195 relayed it. Then `do:park` (observed).

**His words against the criteria.** "Default off" reached cr_1. "No option
or sentinel" reached cr_4, and cr_5 only after m233. "Aborts, not a usage
error" reached no criterion: cr_2 still says "without raising UsageError".
"Continue?" is in no test body. "Give the fake stdin a way to read a line"
reached no criterion, but the walk-3 bodies moved to `StringIO('')`
(observed: extract A section 3). The walk-3 ruling r_84b69b4f0d contested
cr_1 and changed none of its words (observed).

## 3. The request line

**The request line killed no batch for the fourth batch in a row. One team
row reached it, and his refusal of that row then cost a cycle** (observed:
W3). The costs left on the line:

1. **A team row under "You asked".** Page m105 showed `bg_2_summary`, a
   Vision Keeper's description with both changes in it, as line 1 of a
   touch page. Frame 303's door would refuse the assert, and it is on the
   branch (observed: page m105; ruled: the brief, not in the night's code).
2. **His line numbers outlive their page.** m106 answered m105, and two
   sessions on m116 used its numbers. m164 and m196 answered earlier pages,
   and two sessions on m212 used theirs. Four sessions, two of them a
   CYCLE (observed: section 1, frame 305).
3. **The reader misses whole verbs.** m118 asked for two deletions and a
   replacement by line number, and the door told the seat to approve those
   lines (observed: W4).
4. **The guess line held.** Line 2 of each page is "The team's plan of the
   code this touches", by design. His one files correction, m136 "line 2
   is wrong because version_option lives in src/click/decorators.py",
   landed on the guess (observed: the hand list in the report).

## 4. The agent principal's asks and tokens

44 calls on Opus: 4 onboarding calls replayed, then 5, 14 and 21 by walk
(observed: the log's `principal:` lines and `.rota/clickI.principal.jsonl`).
The 40 live calls are 24 pages, 13 clarify questions and 3 confirms
(night 158: 23 calls, 15 pages, 3 clarify, 4 confirm, 1 converse). He read
56.7k characters of pages and wrote 10.7k characters of answers, about
14k and 3k tokens at four characters a token (night 158: 25.7k and 5.0k
characters) (observed: the jsonl; reasoned: the ratio). The harness gives
no token count. Asks per merge: 40 for 1 merge, against 11 each on night
158. bg_4 took 16 of his answers and bg_2 about 19, and neither merged.
bg_4 took 5 answers that each said line 3 was wrong (observed: W1).

## 5. What the next night should be held on

**Hold the next night on the test loop: a batch must not die on a test
that no code can pass, and a criterion must hold his ruled words and not a
sentence that describes a test** (reasoned: W1 and W2). The request line
and the merged content held. The loop between Terminologist, Tester and
Developer is where both deaths happened, for the second night on bg_2. In
order:

1. **Frame 304's case, priced as the rule and not the stub**, 2 cycles:
   a red test whose run never reaches an assertion of the surface's result
   (an error raised in the test's own stub or a `TypeError` on the
   surface's signature) is refused at encode with the raising line, and
   the challenge door admits a quote of that line. s189's `tst_cr1`,
   s185's refused challenge and night 158's tst_02 v3 are the red tests. A
   door that reads one stub shape per night is the fit W4 names for the
   reader (reasoned).
2. **Frame 306's repair 1 at night 160, with W1's hop as its first read**,
   1 cycle: did the respecify of s382 take his "line 3" words. If not, a
   case on frame 308 for an answer after a failed respecify, 1 cycle.
3. **W4, the line reader's cue set inverted**, 2 cycles, with m118, m185
   and m104 as the red tests.
4. **Frame 272's fix**, 2 cycles, unheld: each `recent_chat` reply carries
   its page id or no line numbers. It caused both line-2 losses and cycle
   1 on this night.
5. **W7, the `test_runs` count**, 1 cycle, beside the fixes.

Night 160 then measures frames 302, 303 and 306 on their first night,
frame 283's door, which this night did not exercise, frames 201, 301 and
297 on their night 3 of 3, and frame 308 on its night 2. The branch head
after the night holds the commits of frames 302, 303, 306 and 283's passes
4 to 4d, and its gate is the launch's condition (observed: frame 283's
status of 17:37).

## Usage

The three extract agents ran on Opus, each with a cap of 60k tokens, and
each went past it: A 137.4k, B 119.5k, C 106.2k by the harness counter
(observed: the harness usage lines). A did not finish its check of the
cycle 1 page, and B did not count frames 258, 272, 266 and 303 or check the
cycle 2 page. The synthesising agent did those reads itself (observed:
this page, section 1). The extracts left helper scripts in the scratchpad
`n159/` directory, and B overwrote one of A's once, which A rewrote
(observed: their reports). The synthesising agent used about 150k of its
150k cap. Not read on this night: the turns of W9, the walk-3 resume rule
of bg_2, s358's invented results, s363's refused adopt, and whether
cycle 2's "his second check reached no criterion" holds. Page m212 shows
that check inside line 3, so that claim of the cycle 2 page is wrong at
m212 (observed: page m212).
