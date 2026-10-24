# Night 164's read

Rota workflow, read by the meta workflow. Night 164 ran cold from
`C:/Users/roman/rota_n164` at 5592de6f, launched 21:02 on 2026-10-24, on
`D:/repos/_AI/sample_repos/clickI` at 2c8cd3a, with the agent principal on
Opus and the items of night 163 in a new order: `get_app_dir` first, then
`format_filename`'s docstring example, then `clear()` (observed:
`.rota/night164.log`, lines 1 to 3). The session stopped the night at 22:42
in walk 2, by the rule of 2026-10-09, after five rounds of one cycle on
bg_2. Records: `.rota/clickI_night164.db` (a copy opened `?mode=ro`),
`.rota/night164.log`, `.rota/clickI_night164.principal.jsonl`, the clickI
repository and the source at 5592de6f. The first launch at 20:53 was a
launch defect, not rota's. Its records are read for the count of principal
calls only. Read on 2026-10-24 by one agent on Opus, with no extract agents
and no interviews.

**The result.** 0 merges of 2 batches, the same as night 163. Item 3,
`clear()`, never ran. **bg_1, `get_app_dir`, was right and green at 37 of
37 tests at 21:41, and no Critic ever woke for it (W-C, new).** The
`review` predicate counts the three criteria that he retired at m37 as
criteria that owe a test. `tests_missing` skips them since frame 306's
pass 1b, and `review` does not. Walk 1 then read quiet. In walk 2 he set
bg_1 aside behind the new request, as the shift page offered. bg_2 had the
right docstring at abc65adb and died on one wrong test. The encode door
refused a return-value test five times because the criterion says "shows"
(W-A1). So the Tester wrote a test that reads printed output. He asked
four times to remove that check. Each ruling landed on the criterion row,
and no route reaches a test row (W-A). Each new passing test lifted the
quarantine on the same red (W-B). The death moved from the commit door to
the review gate and to the test row.

## 0. The night in numbers

| Measure | Value |
|---|---|
| Phases | onboarding 21:02 (107 steps, 3 asks, 4 replayed calls); walk 1 21:04 to 21:42 (74 steps, 8 asks by the log, quiet, "Building: 1 change in progress."); walk 2 21:42 to 22:42, stopped by the session, no step count printed |
| Asks | 24 live calls: 9 in walk 1 and 15 in walk 2. Three pages went out twice, m37, m46 and m101 (night 163: 26) |
| Batches | 2: bg_1 `get_app_dir_windows` deferred at 7de95b64, 37 of 37 passing; bg_2 `format_filename_example` running at abc65adb, 36 of 37 passing. 2 tickets, tk_1 and tk_1_format_filename_example. 0 cancels. 1 park row, `get_app_dir_windows` behind s2 at m68 |
| Merges | 0 of 2. 0 verdicts in the database (night 163: 0 of 2) |
| Sessions | 261 sessions, 1114 turns (night 163: 265, 1224). Liaison 74, Vision Keeper 58, Terminologist 41, Tester 27, Developer 26, Architect 20, Critic 14, Researcher 1 |
| By walk | onboarding s1 to s99, 342 turns; walk 1 s100 to s156, 255 turns; walk 2 s157 to s261, 517 turns |
| Principal | 24 live calls on Opus, 2.31 dollars, and 4 replayed. The failed launch at 20:53 spent 21 live calls, 1.93 dollars: 20 confirms and 1 converse on the wrong request page |
| Verdicts | 0 fails, 0 passes. The Critic woke twice, both `tick:challenge` (s135, s200) |
| Commits | bg_1: 1 head, 7de95b64, s128. bg_2: 4 heads, df8ded4e s182, e9bb7c1c s220, 63c65435 s229, abc65adb s233. 4 commit refusals by the note door, all bg_2 |
| Wrote own tool results | 24 of 261 sessions (frame 113 below) |
| Faults | 3 open rows, all Testers, s193, s209 and s213, on `tests.encode` |
| Quarantines at the end | `-|tick:constraint_zero|` at 3, `developer|tick:tests_failing|bg_2` at 3; `-|do:preempt|bg_1,get_app_dir_windows`, `liaison|tick:quarantined|bg_2` and one agenda key at 1 |

(observed: `.rota/night164.log`, `sessions`, `turns`, `tool_calls`,
`batches`, `tests`, `test_runs`, `verdicts`, `faults`, `tick_attempts`,
`item_parks`, the jsonl, `python -m rota.tools.nightcount`, 2026-10-24.)

## 1. The held frames

**Frame 283, the note door, sprint 20 row 1. Not measured on its sample:
item 3 never ran.** The night produced 4 commit refusals by the note door,
all on bg_2 and 0 on bg_1. s220 had 1. Its write dropped `return filename`
at line 484. s229 had 3. Its write dropped `if shorten:`, `if
isinstance(filename, bytes):` and `return filename` (observed: s220 t10,
s229 t13 and t14). Each refusal was right to fire, because each write
removed the function's body. The `drop_notes` table holds 1 row, bg_2
`src/click/utils.py`, status `restored`, on the three statements of s229.
bg_1 has 0 rows (observed). **One removal passed the door.** s229's
commit 63c65435 removed the parameter `shorten: bool = False` from the
signature of `format_filename`. The harness then read 5 tests red, and s233
put the parameter back at abc65adb (observed: `git show 63c65435`, the
log). The note reads statements, and a parameter is not one (reasoned).
W-D.

**Frame 306, his words and the criterion, row 2. Retire works on a
numbered criterion line. A correction of a check line is lost every time.
The retire broke the review gate (W-C).** Each correction, traced to the
rows (observed: `rulings`, `receipts`, `criteria`, `tests`):

| Page | His correction | Ruling | Rows |
|---|---|---|---|
| m37, 1st | lines 2 to 6 wrong | none: the Liaison contested line 7, which his words do not name, and the door refused | returned |
| m37, 2nd | change lines 2 and 3, delete lines 4 to 6 | c1, c2 revise; c3, c4, c6 contest | **landed**: c1, c2 at v2 in his words (s127). **retired**: c3, c4, c6 by r_2131db161c |
| m46, 1st | the checks of lines 3 to 5 are weak | none: a quoting error in the call | returned |
| m46, 2nd | change the checks of lines 3, 4, 5 | c1, c2, c8 contest | **landed on the tests**: s144 re-encoded tst_c1 and tst_c2 |
| m56 | change line 5's check; delete empty lines 6, 7 | c8 contest; two `l_` lines contest | **landed**: s156 re-encoded tst_c8. The `l_` lines are not read |
| m80 | cut lines 3 to 7 to one | cr_1 to cr_6 contest | **respecified**: s181 moved all six |
| m95, stop | cut lines 3 to 7 | cr_2 to cr_6 contest | **lost**: s199 sent 20 respecifies, and no row moved |
| m101, 1st | line 4 wrong, cut 5 to 8 | none: a quoting error in the call | returned |
| m101, 2nd | remove lines 4 to 8 | cr_2 to cr_6 contest | **retired**: s208, by r_a49ac88def |
| m114, stop | line 2's check reads output, change it | cr_1 revise, text unchanged | **added**: s228 wrote a docstring test. The output test stayed |
| m121, stop | remove the second check under line 2 | cr_1 contest | **lost, and added**: s244 wrote a copy of the docstring test |
| m125 | line 5 wrong; remove the second check under line 3 | `l_ee6db6b2cf` contest; cr_1 approve | **landed** on the note line. **Lost** on the check |
| m129, stop | remove the copy and the output check | cr_1 revise, text unchanged | **lost**: s252 re-encoded the copy |
| m134, stop | keep only the first check | cr_1 contest | **lost**: s260 encoded twice, and no row moved |
| m139 | the same | not answered: the night stopped | open |

Five numbered-line corrections landed, two were retires, one was lost
(m95), and three answers returned because of the Liaison's call. All six
check-line corrections were lost or became added rows. In walk 1, a check
correction landed, because each criterion had one test and the Tester
re-encoded that id. In walk 2, cr_1 had three tests, and the Tester added
ids. The second half of the frame, a change outside the criteria that
merges, has no sample. bg_2's diff holds two such changes: four blank lines
removed, and `�` written as `\ufffd` in the docstring (observed: `git diff
2c8cd3a abc65adb`).

**Frame 312, the stop page, row 5 not in the head. Met on the cause and
not on the landing.** Five stop pages on bg_2 (observed: the jsonl):

1. m95, after `tests_missing for bg_2 (tester), 3 attempts` (s196). Each
   of lines 2 to 7 said "check: none. The team gave up writing it after 3
   tries." The cause line said "the team could not write the tests after 3
   attempts".
2. m114, m121, m129 and m134, after `tests_failing for bg_2 (developer), 3
   attempts` (s224, s237, s248, s256). Each named the failing check, "calls
   output = f.getvalue(), expects output.strip() == "c.txt". Fails:
   AssertionError: assert '' == 'c.txt'", under criterion line 2.

So 5 of 5 named the cause, and 4 of 5 named the failing check with its
assertion. He read each one right: the check is wrong, and the code must
not change. Each ruling landed, and 0 of 5 moved the row he named. m95's
contest moved nothing until he repeated it on m101. The other four landed
on cr_1, and the output test stayed at v2 from s216 to the end (W-A).

**Frame 258, the line-1 contest. Night 3. Met: 0 wrong contests of line
1** in every page ruling of the night. Line 2, the code guess, was contested at m24 and
m70, both right by his words (observed: `r_26c534fcc9`, `r_5e124c68d0`).

**Frame 305, the line reader. Night 3. 0 wrong placements on numbered
lines. 6 check-line corrections had no line to land on (W-A).** The check
lines on a page carry no number and no ref, so "the second check under line
2" can only land on line 2 (observed: `_page_body`, `principal.py` 1248
to 1262 at 5592de6f). Three first answers returned (W-E).

**Frame 316, the agenda page and the park. Night 3. Met on the park, not
on the merge.** "Later" on the shift page landed as `park` at m68 (observed:
`r_d42980ab22`, `item_parks`). 0 later pages named `get_app_dir` (observed:
the jsonl after 21:44). Nothing merged, so the park at the merge has no
sample.

**Frame 317, the Tester woken by an answer. Night 3. Met: 0 fixes
undone** in 10 answer wakes of the Tester, s144 to s260. New form: an
answer-woken Tester adds a test beside the wrong one and does not replace
it (s228, s244, W-A).

**Frame 281, the Tester and a fixed version. Night 2. Not exercised.** 27
Tester sessions, and no item needs a version.

**Frame 318, the quarantine lift. Night 2. Passes 2 and 2b are not in the
head.** Pass 1 is in the head. Two head commits reset the
`tests_failing` key by a red move: s229's broken commit, from 1 red test to
5, and s233's repair, back to 1. Three test moves lifted the quarantine.
W-B holds the count.

**Frame 315, the words door. Night 2. Met: 1 refusal, right, and 0
refusals stored as item text.** s115's `problem.assert` on
`get_app_dir_windows` was refused as "the principal's own words". Both item
texts are his sentences (observed: `items`). 0 re-slices.

**Frame 113, parked. 24 of 261 sessions wrote their own tool results,
against 38 of 265.** Vision Keeper 7, Developer 4 of 26, Liaison 4, Tester
4, Terminologist 3, Critic 2 (observed: `nightcount`). The Developer share
fell from 45% to 15%. No note loop ran, so the night supports night 163's
reading that the loop drives the share (reasoned).

**Frame 320, the request that lands nothing. Not in the head. 0 of 2.**
s100 on m_p1 and s157 on m_p2 each reached a confirm page, m17 and m61
(observed).

**bg_1 in walk 1 and walk 2.** At 21:41, bg_1 stood at 7de95b64 with 37
of 37 tests passing at the head, tests for c1, c2 and c8, and no verdict.
`review` (`predicates.py` 1353 at 5592de6f) wakes the Critic only when
every criterion of the batch's tickets has a test of the batch. Its query
has no `retired_by` filter, so c3, c4 and c6, retired at m37, count as
criteria with no test (observed: the query on the copy). `tests_missing`
has the filter at line 836 (frame 306, pass 1b). So no tick fired, and
walk 1 read quiet with "Building: 1 change in progress." In walk 2, the
shift page m_shift said "The change bg_1 is built, and all 37 of its tests
pass. What it waits on: nothing from you." He answered "Later", and
`do:preempt` deferred bg_1 behind s2. s2 never merged, so bg_1 stayed
deferred. **This is a wall, not a rule: W-C, cause 6.** The head 3df18241
has the same `review` query (observed: `git show`). bg_2 has the same
debt: cr_2 to cr_6 are retired with no test, so bg_2 could not reach the
Critic either, even with a green harness (reasoned).

## 2. Every wall the night met

| # | Wall and sign | Sessions | Asks | Place |
|---|---|---|---|---|
| W-C | **A batch with a retired criterion never reaches the Critic.** bg_1 green at 37 of 37 from 21:41, 0 `tick:review`, walk 1 quiet. bg_2 has the same debt on cr_2 to cr_6 | walk 1's end; then bg_1 deferred | 1, m_shift, which said it waits on nothing | **Cause 6**: `review` reads retired rows as live. Frame 306's own pass 1b left `review` out. Not fixed at 3df18241 |
| W-A | **His drop of a test lands on the criterion, and no route takes a test off.** The check lines have no number or ref (`_page_body`). `land` places "the second check under line 2" on cr_1 as revise or contest with the text unchanged. The Terminologist's respecify moves no row, and `msg.answer_tester` names cr_1 only. The Tester's modes hold `tests.encode` and no retire. So s228 and s244 added docstring tests, s252 re-encoded the copy and logged "dropped other checks that read printed output" as a default, and `tst_format_filename_shorten_example` stayed at v2. m139's line 4 then told him the checks were dropped, above the same three checks | Testers s228, s244, s252, s260; Terminologists s227, s240, s251, s259 | 6: m114, m121, m125, m129, m134, m139 | **Cause 1** at the first hop: his object is a test, and the ruling names a criterion. **Cause 10** behind it: no act retires a test on his words. Widen frame 306 to the check line. Not frame 114, whose tests are inherited |
| W-A1 | **The encode door reads "shows" as "prints".** cr_1 says "the path a/b/c.txt shows as c.txt" in the docstring. The door refused five return-value tests: "the test uses what format_filename returns, and the criterion ... says it prints" (s210 t4, s211 t3 and t4, s213 t2, s214 t3). s214 then wrote the output test and logged "format_filename prints to stdout and returns None" | s209 to s214, 3 faults | m125's line 5, in W-A's count | **Cause 8**, wrong to fire: the PRINTS word set holds "shows", and the criterion's subject is docstring text. `api.py` about 9821 to 9849. A new frame |
| W-B | **A new passing test lifts the quarantine on an unchanged red.** Lifts of `developer|tick:tests_failing|bg_2`: after s224, s228's new test; after s237, s244's new test; after s248, s252's re-encode of a passing test. Inside round 2, s229's commit 63c65435 grew the red from 1 to 5, and s233's commit returned it to 1. Both reset the key by a red move. 0 lifts came from a criteria move or a head that cured the red | 16 Developers on `tests_failing`, s215 to s255 | 4 stop pages | **Cause 6**: a tests move reads as progress on the red. Frame 318. Passes 2 and 2b would not have held: `_row_move_reaches` at 3df18241 still lets a tests move lift `tick:tests_failing`. A red that grows is also read as a move |
| W-D | **The note door misses a removed parameter.** 63c65435 dropped `shorten: bool = False`, landed, and 4 more tests failed | s229, s233 | 0 | **Cause 8**, wrong not to fire. Frame 283 |
| W-E | **His first answer returned three times.** m37: the Liaison contested line 7, which his words do not name. m46 and m101: the Liaison's `rulings.rule` call had a quote error, "unterminated argument list" (observed: `messages.unresolved_note`). Each verdict session ended after one refusal | 3 Liaison sessions | 3 | **Cause 7** or **9**, frame 266's kin. Read before a frame |
| W-F | The launch at 20:53 showed the second request on 20 confirms in a row | 0 | 0 of the night | Not rota's: the launch order. Read for the count only |

(observed: `turns`, `tool_calls`, `receipts`, `rulings`, `criteria`,
`tests`, `test_runs`, `messages`, `drop_notes`, the jsonl, the clickI
repository, the source at 5592de6f and 3df18241, 2026-10-24.)

**The bg_2 loop, one round.** The round ran four times from s215 to s260
(observed):

1. Three Developers on `tick:tests_failing` read the code and the red test.
   The docstring is right. The output test cannot pass unless the code
   prints, and his words forbid a code change.
2. The key reaches 3 and quarantines. A Liaison on `tick:quarantined`
   presents the stop page with the failing check.
3. He asks to remove the output check. The ruling lands on cr_1.
4. The Terminologist respecifies cr_1 to the same text, and no row moves.
   It sends `msg.answer_tester` on cr_1.
5. The Tester encodes a docstring test under a new id, or re-encodes that
   one. The tests move lifts the key, and step 1 runs again.

## 3. The request line

**The request line held.** m17 and m61 confirmed both requests. Line 2,
the code guess, was contested twice and right both times. "Later" landed as
a park on the right item (frame 316). Two faults sit near the line:

1. **The shift page said that bg_1 waits on nothing from him.** That was
   true. The page did not say that the batch could never reach the Critic
   (W-C), so his "Later" set aside the only change that was ready.
2. **A note line told him the opposite of the rows.** m139 line 4 said
   "dropped other checks that read printed output", and line 3 still listed
   them (W-A).

## 4. The agent principal's asks and tokens

24 live calls on Opus: 9 in walk 1 (6 pages, 1 confirm, 1 converse, 1
clarify) and 15 in walk 2 (11 pages, 2 clarify, 1 confirm, 1 shift page),
2.31 dollars (observed: the jsonl). He read 29.8k characters of pages and
wrote 6.6k characters of answers, about 7.5k and 1.6k tokens at four
characters a token (night 163: 30.4k and 7.1k). No merge, so no asks per
merge. Of walk 2's 15 calls, 6 went to the one output check (W-A), and 1
re-sent m101 (W-E). His answers were right each time the records can check
them: "only the docstring changes", "format_filename prints nothing", and
"the flag picks which variable to read" (observed: `utils.py` at 2c8cd3a).
The failed launch spent 21 calls and 1.93 dollars before the session
stopped it.

## 5. What the next night should be held on

**Hold night 165 on the review gate: a green batch whose open criteria
all have tests reaches the Critic, whatever he retired** (reasoned: W-C).
Night 164 had one right, green change, and the gate never opened. Each of
his corrections that retires a criterion closes the gate on that batch for
good. He retired criteria on both batches of this night. W-A is second: it
spent the most sessions and asks, and its cause is two hops and a door, not
a model limit. The order, priced by the rule that a door predicate or a
text is 2 cycles and about 60k on Opus:

| Rank | Row | Frame | Site | Red test | Cycles |
|---|---|---|---|---|---|
| 1 | **`review` skips retired criteria and retired tickets, as `tests_missing` does** (W-C) | 306, pass 1b's residue | `review` in `rota/core/predicates.py` about 1353; `live_criteria` and `not_retired` in `scheduler.py`; a sweep of every other reader of `criteria` for the same filter | bg_1 at 7de95b64: c3, c4, c6 retired, tst_c1, tst_c2, tst_c8 green, 0 `tick:review` | 1 for the predicate, 1 for the sweep |
| 2 | **A check line under a criterion has a ref, his drop of it retires that test, and the Tester's wake names the test** (W-A) | 306, widened | `_page_body` in `rota/roles/principal.py` 1248 to 1262; `land`; a test retire act beside `criteria.retire` in `api.py`; `tester/answer.tools` | m121, m129, m134 on cr_1; `tst_format_filename_shorten_example` at v2 to the end | 2 to 3 |
| 3 | **The PRINTS door does not fire on a criterion about docstring text** (W-A1) | a new frame | the `uses_return` branch in `rota/roles/api.py` about 9821 to 9849; the PRINTS set | s210 t4, s211, s213, s214 t3 on cr_1 v2 | 1 for a provenance read, 2 for the predicate |
| 4 | **A tests move lifts `tests_failing` only when it moves or retires a test that is red at the head, and a red that grows resets nothing** (W-B) | 318 | `_row_move_reaches` and the tests branch of `_lift_quarantines` in `rota/core/db.py` about 640 to 700 at 3df18241; `lift_on_red_move` about 717 | the lifts after s228, s244, s252; s229's reset at 63c65435 | 2 |
| 5 | **His first answer returns because of the Liaison's call** (W-E), read first | 305 or 266 | the verdict mode's `rulings.rule`; the parser's quote refusal | m37, m46, m101 first answers | 1 to read |
| 6 | **The note door sees a removed parameter** (W-D) | 283 | the span note's statement reader in `api.py` | s229's write before 63c65435 | 2 |

**Night 165 should not run from 3df18241 before row 1 lands** (reasoned:
W-C). Without row 1, any batch whose criteria he corrects by "delete" stays
short of the Critic, and the night measures nothing past the harness. Row 1
is one query filter and one red test from this night's rows. Then run the
same three items in this order:

1. `get_app_dir` first. It reached green in 38 minutes on this night, so it
   measures row 1 and the merge quickly. A merge also gives frame 306's
   second half and frame 316's park at the merge their first samples.
2. `clear()` second. It is frame 283's planned sample, and it has not run
   since the fix of rows 1 to 6.
3. `format_filename` last. It is the item that looped on W-A and W-A1. Last
   in the order, it cannot starve the others if rows 2 and 3 are not in.

The next night then measures frames 283, 306 and 312 on the commit, the
check line and the page; frames 258, 305 and 316 past their night 3; frames
281 and 318 on their night 3; frame 320 on its night 1; and frame 113's
Developer share against 15%.

## Usage

One agent on Opus, no extract agents and no interviews. About 115k tokens
in and 14k out, estimated. Not read: what the two `l_` lines of m56 were
and whether they left the page; why s199's 20 respecifies moved no row;
which harness run reset the key inside round 1; the full contexts of the
Testers s228 to s260; and the other readers of `criteria` that row 1's
sweep must check.
