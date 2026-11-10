# The silent frames: a mark and a reason for each, draft of 2026-11-10

Frame 363, the put-down step. This page is a read. It moves no frame. The holding session judges it, and then Roman reads it.

## 1. Result

The script finds 88 open and silent frames, the same count as the read of 2026-11-10 (observed: `plans/method/meta-above-frame-read-2026-11-10.md` line 3). The marks:

| Mark | Frames |
|---|---|
| put down | 29 |
| cannot tell | 32 |
| done | 14 |
| stays | 7 |
| joins a live frame | 6 |

- 14 frames need a close line and not a put-down, because later work met their Ends when line (reasoned: this agent).
- 6 frames join a live frame: 331 joins 326, 275 joins 322, 291 joins 357, 172 joins 182, 148 joins 194, and 128 joins 114 (reasoned: this agent).
- 3 frames cannot leave the stack as they are. Debts in the suite name frames 130, 138 and 146, and the F33 test fails when a debt names a frame that is not open (observed: `tests/rota/test_f33_debts_name_open_frames.py`, its `debts()` reader).
- 17 of the 32 `cannot tell` frames show their sign again on a run after night 155 or on a dry run, and no open frame owns that sign (reasoned: this agent).
- No silent frame has a holder that the peers table marks `spent` (observed: `rota/tools/handover.py peers`, 2026-11-10).

The three frames where I am least sure:

1. Frame 266, `done`. Its pass was accepted and its count fell to 0, but night 165 found a residue at the same parser site (observed: its status lines of 2026-10-24 and 2026-10-25).
2. Frame 148, `joins 194`. The join rests on one sentence of the dry run 6c read that puts both frames in one class (observed: `plans/dry6c-tests-refused-read-2026-11-06.md` line 164).
3. Frame 57, `put down`. It is Roman's own ask, and the put-down rests on night 88's answer that nothing spills (observed: the frame's block).

Each mark and each reason is a judgement (reasoned: this agent). Each evidence cell is a place in the records (observed: that place). The marks follow the brief: a frame that later work met is `done`, and a frame whose only fact is its age is `cannot tell`.

## 2. The frames

The push date is the date of the first status line, and the last status is the date of the last status line in file order. The count of status lines uses the parser's pattern, `STATUS` in `rota/tools/state.py`, so a status line with no time does not count.

| Frame | Title | Pushed | Last status | Status lines | Spent holder | Mark | Reason (reasoned: this agent) | Evidence (observed) |
|---|---|---|---|---|---|---|---|---|
| 1 | The end state of the completion line | 2026-09-17 | 2026-09-17 | 1 | no | stays | It waits on the completion line, and the long term plan of 2026-10-31 carries that line as its destination, which the redirect of 2026-11-10 keeps. | `plans/stack.md`, the long term plan and the redirect |
| 2 | The gauntlet on the lineage repositories | 2026-09-17 | 2026-09-17 | 4 | no | stays | It waits on a walk of tips, click and icalendar, which is step 3 of the long term plan, and dry runs now walk icalendar. | `plans/stack.md`, the long term plan, step 3; `plans/dry6c-tests-refused-read-2026-11-06.md` |
| 4 | Roman's order of 2026-09-14 | 2026-09-17 | 2026-09-21 | 5 | no | stays | The long term plan says that frame 4 is the record of the order and closes with step 7, and the redirect keeps that plan. | `plans/stack.md`, the long term plan, step 7 |
| 33 | Code index refresh after a commit | 2026-09-17 | 2026-09-21 | 15 | no | cannot tell | The refresh is built and reviewed since 2026-09-18, and the fact that settles it is one merged run whose index lists the batch's new symbols. | `plans/forgotten-read-2026-10-31.md` line 73 |
| 42 | The designed principal and zero temperature | 2026-09-18 | 2026-09-18 | 1 | no | put down | It asks how to build a fixed principal by hand, and since 2026-10-31 the build session or an agent sits in that seat. | `plans/stack.md`, Sprint 35 amended 2026-10-31 00:58 |
| 45 | An abandoned tick reached the page | 2026-09-18 | 2026-10-08 | 3 | no | done | Frame 190's design covers the page half of this frame at the blindspot site, and frame 190 is closed. | `plans/frame190-design.md`, sections 1.7 and line 500 |
| 47 | The reply cut fires more often | 2026-09-20 | 2026-10-11 | 5 | no | cannot tell | The read of 2026-09-25 found the cut harmless to content and asked for an early stop on a repeat, and no record shows that stop. | `plans/archive/night88-cut-read-2026-09-25.md`; `REPEAT_END` in `rota/core/runner.py` |
| 53 | Does a prompt get half the window | 2026-09-20 | 2026-09-25 | 3 | no | done | Its own line says a harmless answer closes it, and the read of 2026-09-25 found that the cut lost no verdict, ruling or call. | `plans/archive/night88-cut-read-2026-09-25.md`; the frame's status of 2026-09-21 00:25 |
| 57 | Why anything spills into system RAM | 2026-09-21 | 2026-09-21 | 1 | no | put down | Night 88 answered his question, because both models fit the card with 0 GB in RAM, and no later run shows a spill. | `.rota/night88.log`, quoted in the frame's block |
| 84 | Two of ten reds outlive the baseline | 2026-09-25 | 2026-09-25 | 2 | no | put down | The ten reds of 2026-09-25 are not the gate's reds now, because frame 353 and the baseline of 2026-10-30 set a new count. | `plans/stack.md`, Sprint 35 amended 2026-10-31 and the long term plan, step 1 |
| 85 | A read cut names no next call | 2026-09-25 | 2026-09-25 | 1 | no | cannot tell | The block holds only its push, and no page cites the frame, so the settling fact is whether the cut notice names a call today. | the cite search of `plans/`, 0 pages |
| 98 | A seat writes after its session ends | 2026-09-30 | 2026-09-30 | 2 | no | cannot tell | Night 100 confirmed one session that wrote after its end line, and the settling fact is a count of such sessions on a dry run. | the frame's status of 2026-09-30 16:32 |
| 115 | The Architect answers an escalation with no words | 2026-10-02 | 2026-10-11 | 13 | no | cannot tell | The records say an answer carries refs only, and the settling fact is whether frame 200's second pass built the row route it waits on. | the frame's Waits on line; `plans/method/reference.md` line 567 |
| 116 | A Developer sends many challenges in one reply | 2026-10-03 | 2026-10-13 | 5 | no | cannot tell | The night 144 read proposes one challenge for each red test as the rule, against this frame's premise, so a ruling settles it. | the frame's status of 2026-10-13 05:47 |
| 117 | A stub of a long call stubs again | 2026-10-03 | 2026-10-04 | 4 | no | cannot tell | The count rose to 19 prompts on night 116, and the settling fact is a count of empty reply stubs on a recent run. | the frame's status of 2026-10-04 10:47 |
| 126 | The literal door offers a call the mode lacks | 2026-10-04 | 2026-10-04 | 1 | no | done | Frame 349's first pass makes each refusal name a call only where the seat's mode holds that call. | 81b85d3d, 2026-10-30 |
| 128 | A Tester's fix of an inherited test goes elsewhere | 2026-10-04 | 2026-10-08 | 2 | no | joins 114 | Frame 114 holds the route for a failing inherited test, the same rule on the project's tests, and the redirect orders it. | `plans/stack.md`, the redirect, item 4; this frame's Waits on line |
| 130 | The fix wake shows a red test as passing | 2026-10-04 | 2026-10-16 | 4 | no | stays | Three debts in the suite name this frame, so the F33 test fails if the frame leaves the stack. | the F33 reader `debts()`, `tests/rota/test_scene_two_batches.py` line 89 |
| 137 | Parser refusals still name a wrong argument | 2026-10-05 | 2026-10-08 | 4 | no | put down | Its own line rates it low because no session ends on these refusals, and no read after night 133 adds a case. | the frame's Waits on line and its status of 2026-10-08 19:36 |
| 138 | A new id lands a second test | 2026-10-05 | 2026-10-05 | 1 | no | stays | Two debts of the scene `challenged` name this frame, so the F33 test fails if the frame leaves the stack. | the F33 reader `debts()`, `scenes.challenged` |
| 139 | Two reads of one file evict each other | 2026-10-05 | 2026-10-05 | 1 | no | cannot tell | The night 162 read still names this frame among the window signs, and a count of evicted reads on a dry run settles it. | `plans/night162-read.md` line 335 |
| 140 | A span write drops its tail | 2026-10-05 | 2026-10-24 | 11 | no | done | The commit refusal beside a dropped note landed in 57df17fd, and the night 160 read counts 0 landed writes with a dropped note. | 57df17fd; `plans/night160-read.md`, section 1 |
| 141 | The surface door refuses an import through the package | 2026-10-05 | 2026-10-05 | 1 | no | put down | The dry run 6c read checked 7 refusals of an import from another module and found each one right. | `plans/dry6c-tests-refused-read-2026-11-06.md` line 168 |
| 146 | Write doors skip what a top level loads | 2026-10-05 | 2026-10-05 | 3 | no | stays | A debt of the scene `two_batches` names this frame, so the F33 test fails if the frame leaves the stack. | the F33 reader `debts()`, `scenes.two_batches` |
| 147 | The constant door refuses a right test | 2026-10-05 | 2026-10-17 | 4 | no | cannot tell | Nights 153 and 154 show wrong refusals, and dry run 6c shows the same class at the collect door, which has no owner. | `plans/dry6c-tests-refused-read-2026-11-06.md` line 165 |
| 148 | Three refusals name calls the doors refuse | 2026-10-05 | 2026-10-05 | 5 | no | joins 194 | The dry run 6c read puts this frame and frame 194 in one class, doors whose hints contradict each other, and frame 194 is open. | `plans/dry6c-tests-refused-read-2026-11-06.md` line 164 |
| 150 | A refused commit leaves its write behind | 2026-10-05 | 2026-10-05 | 1 | no | done | Frame 297 closed at c0549d84, and its read says the discard repair meets this frame's first Ends when branch. | `plans/frame297-discard-history.md`, section 4.4; 1faa5f45a |
| 154 | Six same-refs sentences state false facts | 2026-10-05 | 2026-10-05 | 1 | no | put down | Its own Ends when line says that no night held a case of these six review findings, so no run pays for them. | the frame's Ends when line |
| 156 | Adjacent string literals are joined and misread | 2026-10-06 | 2026-10-06 | 1 | no | put down | Five lists of nights 113 to 125 are its only cases, and the dry run 6c read checked the frame and found no match. | `plans/dry6c-wall5-backslash-read-2026-11-06.md` line 68 |
| 157 | The cockpit frontier skips the stall quarantine | 2026-10-06 | 2026-10-06 | 1 | no | done | Commit be53aee1 makes the read-only frontier drop the keys that the quarantine drops, so it matches the loop. | be53aee1, 2026-11-01; `frontier_readonly` in `rota/core/scheduler.py` |
| 158 | A test holds an escape in a plain string | 2026-10-06 | 2026-10-07 | 2 | no | cannot tell | The file `tests/rota/test_desk_guards.py` still fails a compile with warnings as errors, and the settling fact is whether the next Python version is in use. | a compile with `-W error::SyntaxWarning`, 2026-11-10 |
| 159 | The escalation door offers the end as a choice | 2026-10-06 | 2026-10-06 | 1 | no | put down | Nights 125 to 136 named the case, and no read after night 136 names it. | the cite search of `plans/` |
| 160 | The dots door and the owed-call nudge | 2026-10-06 | 2026-10-06 | 4 | no | put down | It holds review findings with no run case, and 0 of 551 stored ids hold a dot. | the frame's Site and Ends when lines |
| 161 | The revert door's tests leave mutants alive | 2026-10-06 | 2026-10-06 | 1 | no | put down | It asks for tests that kill mutants of the revert door, and no run case of a lost revert stands in its block. | the frame's Ends when line |
| 162 | Four refusals that frame 144 found | 2026-10-06 | 2026-10-06 | 1 | no | put down | Frame 349 covers its first item, and its other three are review findings with one case on night 145. | 81b85d3d; `plans/night145-read.md` line 483 |
| 163 | A Critic fails while its challenge is open | 2026-10-06 | 2026-10-06 | 1 | no | put down | A scene raised it as a question and not a run, and the night 155 read checked the frame and found no fit. | `plans/night155-cycle1.md` line 148 |
| 167 | The ladder's end relays a batch id | 2026-10-06 | 2026-10-06 | 1 | no | put down | Night 126 is its one case, and no read after night 133 names it. | the cite search of `plans/` |
| 168 | The same-refs step ends while a challenge lands | 2026-10-06 | 2026-10-06 | 1 | no | put down | Night 144 is the last read that names it, and no read of nights 145 to 175 or the dry runs adds a case. | `plans/night144-read.md` line 559 |
| 172 | A merge raises an error on an untested path | 2026-10-07 | 2026-10-11 | 4 | no | joins 182 | Frame 182 holds the same fact, a green batch with no test of its behaviour, and it is item 2 of the redirect's order. | frame 182's Waits on line, `plans/stack.md` line 3208 |
| 174 | An empty answer is stamped answered | 2026-10-07 | 2026-10-11 | 3 | no | cannot tell | The night 166 read placed a new case at this frame, and the settling fact is a count of such rows on a dry run. | `plans/night166-read.md` line 215 |
| 175 | The Tester fence nudge is spent on prose | 2026-10-07 | 2026-10-07 | 1 | no | put down | One of eight sessions on night 127 met it, and no later read names the case. | the frame's Site line; the cite search of `plans/` |
| 176 | The invoke door misses a local wrapper | 2026-10-07 | 2026-10-08 | 5 | no | put down | Its cases come from click's version flag item on nights 128 to 139, and the night 149 read names a different door. | `plans/night149-cycle1.md` line 125 |
| 179 | The survey binds no constraint to item files | 2026-10-07 | 2026-10-08 | 3 | no | cannot tell | The night 174 read shows the same survey rows and lists this frame as unplaced, and the settling fact is whether its read now runs. | `plans/night174-read.md` line 211 |
| 181 | A Critic emits again after its verdict | 2026-10-08 | 2026-10-08 | 3 | no | put down | Its own line rates it low because the cost is turns and no merge waits, and the count fell from 3 to 1. | the frame's Waits on line and its status of 2026-10-08 19:36 |
| 184 | The Liaison repeats its own ask-back | 2026-10-08 | 2026-10-08 | 1 | no | put down | Night 133 is its one case, and the night 155 read checked the frame and found no fit. | `plans/night155-cycle1.md` line 321 |
| 185 | A put-off request lands as a contest | 2026-10-08 | 2026-10-11 | 3 | no | done | Its own line closes it on the first night with a shift page, and nights 150 and 155 ran shift pages with later and park. | the frame's status of 2026-10-11 00:30; frames 265 and 292 |
| 188 | A self-relay wakes the Liaison with no mode | 2026-10-09 | 2026-10-09 | 1 | no | cannot tell | The night 171 read shows the hop again and calls the frame open, and the settling fact is whether a dry run shows it. | `plans/night171-how-it-works-read.md` line 27 |
| 192 | A principal's drop has no ruling word | 2026-10-09 | 2026-10-16 | 4 | no | done | The rulings now take `drop` as an act, and on night 139 the door mapped each sent `drop` to a contest. | `RULED_ACTS` in `rota/roles/principal.py` line 1362; the frame's status of 2026-10-11 00:30 |
| 196 | A should-not-edit sentence protects no file | 2026-10-10 | 2026-10-10 | 1 | no | cannot tell | The night 155 read leaves this sign open for a read, and a count of protected files that a batch kept settles it. | `plans/night155-read.md` line 125 |
| 203 | The gate's wall is process spawn | 2026-10-11 | 2026-10-23 | 16 | no | stays | Step 1 of the long term plan names frame 203's recurring flaky set as the next work on the instrument. | `plans/stack.md`, the long term plan, step 1 |
| 205 | Which defaults the Architect reads at opt-out | 2026-10-11 | 2026-10-11 | 1 | no | put down | It measures a rule of frame 204's pass 4, and frame 204 is parked, so the rule it would measure does not run. | frame 204 in the Parked section; the frame's Waits on line |
| 208 | The repeat refusal matches a short answer | 2026-10-11 | 2026-10-12 | 2 | no | cannot tell | The night 162 read still names this frame among the window signs, and the settling fact is a count of false repoint sentences. | `plans/night162-read.md` line 335 |
| 211 | The encode door offers a refused verdict | 2026-10-12 | 2026-10-12 | 1 | no | done | Frame 362's pass 4d built this frame's mechanism, a door that checks its offer before it offers it. | bed73e5f and a6d87a4d, frame 362's status of 2026-11-04 09:18 |
| 212 | The answer door steers the Architect wrong | 2026-10-12 | 2026-10-15 | 3 | no | cannot tell | The interview it asks for never ran, and the settling fact is the current mark of the case `L1-AR-route-an-escalation`. | the frame's Ends when line and its status of 2026-10-15 16:24 |
| 214 | The Liaison copies the brief's example ask | 2026-10-12 | 2026-10-18 | 5 | no | cannot tell | Night 155 shows the sign again, dry run 6c shows copied examples at the Tester, and the example line is still in `converse.md`. | `rota/roles/prompts/liaison/converse.md` line 106; `plans/dry6c-tests-refused-read-2026-11-06.md` line 166 |
| 216 | The Tester imports a name nobody named | 2026-10-12 | 2026-10-12 | 1 | no | cannot tell | The dry run 6c read names this frame as the class of 17 import refusals, and the settling fact is which frame takes that rank. | `plans/dry6c-tests-refused-read-2026-11-06.md` line 167 |
| 217 | The repair pre-run shows no expected files | 2026-10-12 | 2026-10-12 | 1 | no | cannot tell | The block holds only its push, and the settling fact is whether the repair mode's tools show the batch's expected files today. | the frame's Site line |
| 218 | The repair brief asks for a missing callable | 2026-10-12 | 2026-10-12 | 1 | no | put down | Frame 295 holds the same brief sentence and the same door, so one frame is enough for this fact. | `rota/roles/prompts/terminologist/criterion_repair.md` line 15; frame 295 |
| 224 | Three Developer cases dropped under pass 5 | 2026-10-12 | 2026-10-13 | 2 | no | put down | Frame 339's case read found a newer cause for these cases, the removals note, so the read this frame asks for is out of date. | `plans/frame339-cases-read.md`, the result |
| 247 | The glossary lookup matches the term's case | 2026-10-15 | 2026-10-15 | 2 | no | cannot tell | The lookup still matches the exact case of the term, and the settling fact is whether a dry run logs a miss on case alone. | `glossary_lookup` in `rota/roles/api.py` line 3819 |
| 248 | Kind door questions logged as notes | 2026-10-15 | 2026-10-15 | 1 | no | put down | Night 148 is its one case, and the night 153 read found no sign of it. | `plans/night153-read.md` line 664 |
| 249 | A criterion ruling ends in a glossary call | 2026-10-15 | 2026-10-17 | 2 | no | cannot tell | Nights 153 and 155 show the sign again, and the settling fact is whether a dry run shows a criterion ruling sent to the Terminologist. | `plans/night155-read.md` line 131 |
| 252 | The wall guide reviewed after use | 2026-10-15 | 2026-10-16 | 5 | no | cannot tell | He asked for this review, its three nights ran by 2026-10-16, and the settling fact is whether he still wants it after frame 341's revision. | `plans/method/meta-what-exists-read-2026-11-10.md` line 51 |
| 253 | A raw tick key reaches the principal | 2026-10-15 | 2026-10-16 | 5 | no | done | Commit ba128953 reads the quarantined keys through one reader and writes them in words, and a page never shows an `@`. | ba128953, 2026-10-27; `_ref_words` in `rota/roles/principal.py` |
| 259 | Seat work notes counted as rota faults | 2026-10-15 | 2026-10-17 | 4 | no | cannot tell | Night 169 still counts seat notes as fault rows, and the settling fact is whether a dry run log prints the same fault line. | `plans/night169-read.md` line 67; `rota/roles/principal.py` line 534 |
| 262 | A criterion names a surface the index lacks | 2026-10-16 | 2026-10-17 | 4 | no | cannot tell | Nights 151 to 153 show no case, but dry run 6c shows the class again, so the settling fact is which frame takes that rank. | `plans/dry6c-tests-refused-read-2026-11-06.md` line 167 |
| 265 | The word now on a shift page lands as later | 2026-10-16 | 2026-10-17 | 4 | no | cannot tell | The dry run 1 read found a new refusal of "1 now" in this family, and the owner of that refusal settles it. | `plans/dry1-fourth-wall-read-2026-11-01.md` line 10 |
| 266 | The parser blames the words for a missing quote | 2026-10-16 | 2026-10-25 | 28 | no | done | Its pass was accepted at ce658cdb and 0 Liaison sessions end on the refusal, but night 165 found a residue at `_missing_close`. | the frame's status of 2026-10-24 01:11 and 2026-10-25 03:32; `plans/dry6c-wall5-backslash-read-2026-11-06.md` line 68 |
| 268 | An approval reaches an item the ruling skips | 2026-10-16 | 2026-10-16 | 3 | no | put down | Frame 274's count found that another writer made the contest first, so this frame's site did not cause its own case. | the frame's status of 2026-10-16 22:42; `plans/frame274-count.md` |
| 269 | Encode doors admit a decorator called with text | 2026-10-16 | 2026-10-16 | 2 | no | cannot tell | Night 152 shows no case of the first shape, but night 157 adds a related case, so a count on a dry run settles it. | `plans/night157-read.md` line 200 |
| 270 | A whole-file write drops imported names | 2026-10-16 | 2026-10-16 | 2 | no | put down | Night 152 shows no such write and 4 right fires of the door, and the dry run 5 read names a different fault. | the frame's status of 2026-10-16 22:30; `plans/f362-dry5-walls-read.md` line 60 |
| 271 | A re-annotate leaves out the file he named | 2026-10-16 | 2026-10-16 | 2 | no | cannot tell | Night 152 shows 2 of 2 cases, night 155 leaves the sign open for a read, and a count on a dry run settles it. | `plans/night155-read.md` line 125 |
| 275 | The words door refuses another word form | 2026-10-16 | 2026-10-17 | 2 | no | joins 322 | A later read puts this frame at the door that frames 322 and 337 propose to read through one reader, and frame 322 is open. | `plans/closed-reach-c.md` lines 33 and 35 |
| 276 | A quarantine page shows another request | 2026-10-16 | 2026-10-16 | 1 | no | put down | Night 152 is its one case, and the dry run 1 read checked the frame and found a different fault. | `plans/dry1-turn17-read-2026-11-02.md` line 43 |
| 279 | Criteria drop compact and the code follows | 2026-10-17 | 2026-10-17 | 2 | no | cannot tell | The block is cut, because a status line of frame 278 splits its heading, and the settling fact is whether its interview ran. | `plans/facts-2026-10-27.md` line 7 |
| 284 | The raised-signature push misses pytest frames | 2026-10-17 | 2026-10-17 | 1 | no | cannot tell | The push still reads only the native traceback form, and the settling fact is whether a recent run shows a raise that gets no push. | `_TRACE_FRAME` in `rota/core/runner.py` line 3768 |
| 285 | The offered challenge call has no quotes | 2026-10-17 | 2026-10-17 | 1 | no | cannot tell | Night 168 shows the same first send with no quotes, and the settling fact is whether a dry run shows it. | `plans/night168-read.md` line 106 |
| 288 | The load check ignores an uninstalled package | 2026-10-17 | 2026-10-17 | 1 | no | put down | Its one case comes from a recorded case of parked frame 143, with 0 asks, and night 157 named a different cause. | the frame's Site line; `plans/night157-read.md` line 197 |
| 289 | The batch filter misses two contest phrasings | 2026-10-17 | 2026-10-17 | 2 | no | put down | Two later reads checked the frame against their walls and found that its cues are not their cause. | `plans/seam-night173-read.md` line 164; `plans/dry6c-wall2-correction-read-2026-11-06.md` line 42 |
| 291 | A contested statement is confirmed again | 2026-10-18 | 2026-10-18 | 1 | no | joins 357 | Frame 357's first pass built the end of a dropped statement, the withdrawal this frame asks for, and frame 357 is open. | `plans/dry1-turn17-read-2026-11-02.md` line 42 |
| 292 | The shift door checks the word first | 2026-10-18 | 2026-10-18 | 2 | no | cannot tell | The dry run 1 read places a new refusal in the family of frames 265 and 292, and its owner settles it. | `plans/dry1-fourth-wall-read-2026-11-01.md` line 10 |
| 294 | Four caps are literals outside the config | 2026-10-18 | 2026-10-18 | 2 | no | put down | The four caps are still literals in `rota/core/sandbox.py`, and its own line says the breach costs no run. | `rota/core/sandbox.py` lines 38, 2074 and 2558; the frame's Sprint line |
| 295 | The repair brief and the surface door disagree | 2026-10-18 | 2026-10-18 | 1 | no | cannot tell | The brief line is still there, and the settling fact is whether a recent run shows a repair refused for an intended name. | `rota/roles/prompts/terminologist/criterion_repair.md` line 15 |
| 300 | Rulings name their rows inside a JSON map | 2026-10-18 | 2026-10-18 | 1 | no | done | The rulings seam landed a `ruled_refs` table with one row for each ruling and ref, which is the join this frame asked for. | dfcffd40; `plans/rulings-seam-design-2026-10-26.md` lines 28 and 47 |
| 331 | Owed cases run on no fixture | 2026-10-26 | 2026-10-26 | 1 | no | joins 326 | The test file now names frame 326 as the owner of the owed set, and the set fell from 27 to 10 cases. | `tests/rota/test_case_reachability.py` lines 210 to 228 |
| 332 | Debts that name no frame leave the count | 2026-10-26 | 2026-10-26 | 1 | no | done | The F33 test refuses an xfail, an owed case or a refused offer that names no open frame, but not a comment or a commit. | 21b65280 and 4f44fe27, 2026-10-28 |
| 333 | Three channels keep the 12-character quote window | 2026-10-26 | 2026-10-26 | 1 | no | done | Commit 9a068333 gives every channel one quote reader, and its tests refuse a 12-character quote on each channel. | 9a068333, 2026-10-27; `tests/rota/test_frame333_quote_reader.py` |
| 334 | The Terminologist writes word senses by hand | 2026-10-26 | 2026-10-26 | 1 | no | put down | Its agency read finds that its wait was answered on 2026-09-12, and that the planned generator cannot turn its own red test green. | `plans/frame334-agency-read.md`, the result |

## 3. The classes of the reasons

I wrote each reason first and grouped the reasons after the last frame (reasoned: this agent).

**Put down, 29 frames:**

- A later read checked the frame against its own wall and found another cause, or found the door right: 10 frames, 141, 156, 163, 176, 184, 268, 270, 276, 288 and 289.
- The frame's own line rates it low, or it holds review findings with no case on a run: 7 frames, 137, 154, 160, 161, 162, 181 and 294.
- A ruling, a parked frame or a later read removed what the frame measures or asks: 6 frames, 42, 57, 84, 205, 224 and 334.
- One case or a few cases on a night, and no later read names the case: 5 frames, 159, 167, 168, 175 and 248.
- Another silent frame holds the same fact at the same site: 1 frame, 218, beside frame 295.

**Done, 14 frames:**

- The build of another frame or of a sprint row met the Ends when line: 9 frames, 45, 126, 150, 157, 211, 253, 300, 332 and 333.
- The frame's own fix landed and its count met the line, and no line closed the frame: 3 frames, 140, 192 and 266.
- A later run or read answered the frame's question: 2 frames, 53 and 185.

**Joins, 6 frames:** a live frame holds the same fact at the same site: 128, 148, 172, 275, 291 and 331.

**Stays, 7 frames:**

- The long term plan of 2026-10-31 names the frame or the line it waits on: 4 frames, 1, 2, 4 and 203.
- A debt in the suite names the frame, so the F33 test needs it open: 3 frames, 130, 138 and 146.

**Cannot tell, 32 frames:**

- The sign shows again on a later run, and no open frame owns it: 17 frames, 139, 147, 174, 179, 188, 196, 208, 214, 216, 249, 259, 262, 265, 269, 271, 285 and 292.
- The fault is still in the code, and no run counted it since the push: 4 frames, 158, 247, 284 and 295.
- An owed read, interview or ruling never ran, and the mark depends on it: 5 frames, 115, 116, 212, 252 and 279.
- The fix is built, and no run proves it: 2 frames, 33 and 47.
- The last count is old, and no later count exists: 2 frames, 98 and 117.
- The block holds only its push, and no page cites the frame: 2 frames, 85 and 217.

## 4. The frames in one list and not in the other

The read of 2026-11-10 gives the count 88 and no list of frame numbers (observed: `plans/method/meta-above-frame-read-2026-11-10.md`, sections 4 and 6). So I compare the count and the two facts that the read states about the 88.

- The count: 88 against 88. The script takes every frame of the stack file, leaves out the 20 frames in the Parked section or with `(parked)` in the heading, and keeps the frames with no status line on or after 2026-10-27 (observed: the script `silent.py`, 136 frames, 28 live, 20 parked).
- "36 of the 88 read 'Waits on: Roman's order'": my set gives 36 (observed: the script `table.py`).
- "38 have one status line, the push": my set gives 39 (observed: the script `table.py`). Frame 1 has a second status line, "Status 2026-09-16", with no time, and the parser's pattern does not count it. A looser pattern counts 2 lines for frame 1 and gives 38 (reasoned: this agent).

I cannot name a frame that is in one list and not in the other, because the other list is not written down.

## 5. What I could not see

- The holders. Three silent frames have a holder in the heading: 140, 203 and 266. The sessions 1cf2843b and b0dce033 have no row in the peers table. The session eefbf293 reads `holding` with frame 278, and frame 278 is not on the stack (observed: `rota/tools/handover.py peers`, 2026-11-10). So the `spent holder` column says no for all 88, but the table cannot prove that these holders are alive.
- "No later read names it" comes from a search of `plans/` for "frame <n>". A read that describes a sign and does not write the frame number is not in that search (reasoned: this agent).
- I did not read the transcripts, the night databases, the dry run databases or the cassette register. The current marks of the cases that frames 212 and 224 name are not on this page.
- My commit search matched the frame number in the subject line. A fix commit that names the frame only in its body is missed, for example the fixes of frame 140 (observed: `git log --grep="frame 140"`).
- Frame 279's block is cut. A status line of frame 278 stands inside its heading, so the parser reads the title as "Th" (observed: `plans/stack.md` lines 2669 to 2680).
- Frame 130 holds two status lines of 2026-10-16 that describe frame 129's pass and review. They may stand on the wrong block (observed: `plans/stack.md` lines 3589 to 3600).
- Frame 252 holds a "closed." line of 2026-10-15 13:10 and later lines that keep it open (observed: `plans/facts-2026-10-27.md` line 428).
- The three suite debts come from the F33 reader at the time of this read. Another agent edits `rota/tools/state.py` now, and that reader uses it.
- The evidence for `done` and `joins` is one or two searches for each frame. A `done` mark says that the part that matters is met, and it does not test every clause of the Ends when line.
