# Night 167, the read: no merge of three, and two of the three walls are rota's doors

Rota workflow, read by the meta workflow on 2026-10-26 at 07:28. Night 167 ran
cold from `C:/Users/roman/rota_n167g` at 40b16f78, 04:47 to 07:12:58, on the
items of nights 163 to 166 rotated as on night 166: `get_app_dir`, `clear`,
`format_filename`. The profile was `local-gemma-cr-ts`: `gemma4:12b-it-qat` in
the Critic and Tester seats with think off, `qwen3.5:9b` in the Developer and
Terminologist seats, `qwen3:8b` in every other seat, and the agent principal
on Opus. It exited 0 with GAUNTLET-DONE (observed: `.rota/night167.log` lines
1, 6 and 211). Sources: `.rota/clickI_night167.db` opened `?mode=ro`,
`.rota/night167.log`, `.rota/clickI_night167.principal.jsonl`,
`.rota/clickI_night166.db` and the databases of nights 163 to 165 opened
`?mode=ro`, the source at 40b16f78 and 4bb2656b, and the stack blocks. The
three reads of the night are the input: `plans/night167-walk1-loop.md`,
`plans/night167-walk2-read.md` and `plans/night167-cycle1.md`. This read cites
them and does not repeat them. One agent on Opus. No model ran and no pytest
ran. The replays below call the door functions of the working tree at
4bb2656b on rows read from the database. They write nothing.

**The result. 0 merges of 3 items, against 2 of 3 on night 166.** Walk 1
ended quiet after 174 steps on frame 315's line-1 loop. Walk 2 ended quiet
after 59 steps on frame 328's one-test guard, which dropped the Gemma Tester's
right fix. Walk 3 ended at the night's end in a CYCLE on a wall that no frame
holds: the Tester's test path `src/click/utils.py` replaces the module under
test. **Two of the three walls are rota's doors, and the third is upstream of
the Gemma seats.** So the night measures the doors more than the model. The
Gemma Critic reached no review on any walk. The Gemma Tester had 10 reply cuts
in 14 sessions, where night 166's qwen3.5:9b Tester had 0 in 12.

## 0. The night in numbers

| Measure | Value |
|---|---|
| Phases | onboarding 04:47 to 05:15, 110 steps, 3 asks, 1 replayed call; walk 1 05:15 to 06:09, 174 steps, 20 asks, quiet and stuck; walk 2 06:09 to 06:32, 59 steps, 7 asks, quiet and stuck; walk 3 06:32 to 07:12, 5 asks, no step line, bg_6 running at the end |
| Asks | 35 live calls: 3, 20, 7 and 5 (night 166: 13) |
| Principal | 35 live calls on Opus, 3.52 dollars: 0.32, 2.10, 0.65 and 0.45 by phase (night 166: 1.04). He read 46.4k characters of pages and wrote 9.0k (night 166: 8.65k and 2.25k). One more row at 04:46:53, 0.08 dollars, is the first launch that was killed, and this read does not count it |
| Batches | 6. bg_1 to bg_4 `get_app_dir_windows`, all abandoned; bg_1 has the only head, 5c8c80b5. bg_5 `clear_screen_return` deferred at 57f75f44, 36 tests, 1 red. bg_6 `format_filename_example` running at fa4e8230, 35 tests, 35 errors. 5 tickets. 2 park rows, both shift pages |
| Merges | 0 of 3 (night 166: 2 of 3, and the third passed review) |
| Verdicts | 0 rows. The Critic woke 16 times, all on `tick:challenge`, and 0 times on `tick:review` (night 166: 3 passes, 3 review wakes, 14 challenge wakes) |
| Sessions | 344 sessions, 1518 turns (night 166: 213, 832). Liaison 105, Vision Keeper 88, Architect 48, Terminologist 42, Developer 31, Critic 16, Tester 14 |
| By walk | onboarding s1 to s102, 357 turns; walk 1 s103 to s248, 627 turns; walk 2 s249 to s297, 235 turns; walk 3 s298 to s344, 299 turns |
| Commits | 35 `code.commit` calls, 3 landed: 5c8c80b5 (s125), 57f75f44 (s268), fa4e8230 (s323). The note door refused 19 calls: 9 on bg_5 and 10 on bg_6. 2 `drop_notes` rows, both `restored` |
| Quarantines at the end | `-|tick:constraint_zero|` at 3; `developer|tick:tests_failing|bg_1` at 3; `vision_keeper|tick:contested|get_app_dir_windows` at 3; `developer|tick:tests_failing|bg_5` at 3 |
| Faults | 3 open rows: f_8dbbafc92c (s217), f_098219b558 (s319), f_50b9259087 (s343) (night 166: 2) |
| CYCLE lines | 1, at walk 3: period 1, 3 rounds of `developer|tick:tests_failing|attempt 4|["bg_6"]` (night 166: 1) |
| `nightcount` | 344 sessions, 1518 turns; made up 68 turns in 38 sessions; 0 writes after an invention; 87 dangling-pointer turns in 10 sessions, most s338 (16); 15 wakes repeated, 52 sessions, 37 of them repeats (night 166: 30 in 16; 15 in 5; 3 wakes, 9 sessions, 6 repeats) |

(observed: `night167.log` lines 1 to 211, `sessions`, `turns`, `tool_calls`,
`receipts`, `batches`, `tests`, `test_run_journal`, `verdicts`, `faults`,
`drop_notes`, `tick_attempts`, `item_parks`, the jsonl, and
`.rota/clickI_warm.db` for the end of onboarding at s102, 2026-10-26.)

## 1. The walks

**Walk 1, `get_app_dir`. The wall is frame 315's site.** s161, the Vision
Keeper on `tick:contested`, appended his m57 sentence about the test to the
item text: "Its check calls the function without an app name, so it fails
before it tests anything." His next replies asked six times to remove it. No
role holds a call that removes it, the contested tick quarantined after s233,
and the walk ended at its quiet bound after 174 steps and 20 asks
(`night167-walk1-loop.md`, sections 1 to 3). Two more faults sit under the
loop. The Gemma Tester wrote `"C:\\MockAppData"` inside the call's body
string, the call parser read one escape level, and the stored body held
`"C:\MockAppData"`, a SyntaxError at collection. tst_c4 and the first
version of `'tst_c5` were red on any code (observed: s126 and s142
completions, `test_run_journal` seq 35 and 143). The encode run of frame 328
saw the error and did not return it, because it returns only a `fail`
verdict (observed: `api.py` about 17411 at 4bb2656b). Frame 315; the escape
level is candidate C2.

**Walk 2, `clear()`. The wall is frame 328's one-test guard.** s271 stored
tst_tk3 red on any right code, got the encode note, and sent a passing test
with the same id. The guard returned it "unchanged", because the session's
own test was staged and not stored. Frame 328's strict quote check then
refused all of the Developer's challenges, and s280 moved tk_3's surface to
`examples/termui/termui.py::clear`, so that two doors refused each other in
s281 and s283 (`night167-walk2-read.md`, sections 2 and 3). Frame 328, with
frame 324 behind it. Pass 3, 45541e92, is on the branch for the guard.

**Walk 3, `format_filename`. The wall is in no frame.** The Gemma Tester put
`tst_c1_format_filename_example` at `path='src/click/utils.py'` in all four
versions. The harness writes the test over the module, every test errors on
a circular import, and the right docstring commit fa4e8230 cannot go green.
Three Developer rounds, s336 to s338, made the CYCLE line
(`night167-cycle1.md`, the result and section 1). He read the circular
import as a code change and asked to "put the code back as it was" (m195).
Candidate C1. Frame 322's sign showed again: the first criterion named
behaviour on the docstring ticket (section 3, frame 322).

## 2. The walls

| # | Wall and sign | Sessions | Cause by `plans/wall-guide.md` | Frame |
|---|---|---|---|---|
| W1 | **Line 1 holds a sentence he asks to remove, and no role can remove it.** 6 removal requests, 4 clarify pages, the contested tick at 3 | s161 to s235, 20 asks | Cause 10, the mode lacks the route; cause 9 behind it, the step offered only an amend (`night167-walk1-loop.md`, section 1) | 315 |
| W2 | **A body's backslash loses one escape level in the call.** tst_c4 and `'tst_c5` v1 are SyntaxErrors at collection. The Developer then quoted `"C:\\MockAppData"` and the row holds one backslash, so 11 challenges were refused | s126, s142, s143, s146, s147 | Cause 4 at the seat, the call form needs two escape levels; cause 8 at the encode run, a collection error is not a red | candidate C2 |
| W3 | **The one-test guard drops the re-encode that the encode note asks for** | s271 | Cause 8, the guard reads stored rows and not staged ones (`night167-walk2-read.md`, section 2) | 328, pass 3 on the branch |
| W4 | **The quote check refuses a verbatim quote of the test on the ESC byte form** | s284, s286 | Cause 8 | 328, pass 3 and 3b on the branch |
| W5 | **The surface door and the one-program door refuse each other's remedy** after s280 moved the surface to `examples/` | s280, s281, s283, 8 refusals | Cause 9, each refusal points to the other door's refusal; the surface sign is frame 324's | 324 |
| W6 | **The Developer rewrites right code to fit a wrong test.** The note door refused 19 commits on bg_5 and bg_6, each right | s272 to s284, s319 to s322 | No fault; the door held | 283, measured |
| W7 | **The Tester's test path replaces the module under test.** 15 of 62 encodes name `src/click/utils.py`; 35 of 35 tests error at fa4e8230 | s324 to s343, s327 to s344 | Cause 8: `tests.encode` checks only that the path ends in `.py`, and the encode run is silent on a collection error. Cause 9 behind it: s329's refusal named the surface and not the path | candidate C1 |
| W8 | **The criterion half refuses a quote with one unpaired outer `'`.** 12 of 13 refusals in walk 3 | s327, s336 to s338, s344 | Cause 8: `_span_of` strips an outer quote only as a pair. m189 passed because its quote ended in `'` as well | 328, a residue |
| W9 | **A docstring item gets a behaviour criterion first.** c_1 v1 "returns 'c.txt'"; m180 and m195 called it wrong | s312, s318, s342 | Cause 5, the headline names the docstring (`night167-cycle1.md`, section 2) | 322, 7d37adcd on the branch |
| W10 | **The Gemma seats cut their replies at the output budget.** 15 cuts in 14 of 30 Gemma sessions | Tester 10 of 14, Critic 4 of 16 | Cause 13, the serving shape with think off (`plans/frame323-gemma-interview.md`) | 323 |
| W11 | **The shift page m_p2 says "What it waits on: nothing from you" while the item's contested tick is quarantined** | m_p2, after s235 | Cause 11, what is his does not reach him | 312, second half |
| W12 | **The constraint tick quarantines at onboarding**, as on nights 164 to 166 | s1 | Not read | none |

(observed: `tool_calls`, `turns`, `receipts`, `tests`, `test_run_journal`,
`criteria`, `tick_attempts`, the jsonl pages, and the code at 40b16f78 and
4bb2656b.)

## 3. The frames measured

| Frame | Ends-when clause | What night 167 read |
|---|---|---|
| 328 | First: a test written on a batch with a head runs at encode, and a red goes back to the Tester | Fired: s142's three refusals at encode and s271's note. Silent on 3 collection errors, tst_c4, `'tst_c5` v1 and tst_c1 v1 to v4 (W2, W7) |
| 328 | Second: a challenge quote must be in the live criterion text | Held: 0 challenges passed on an old text. 55 calls, 5 delivered. The live text was also refused on two forms the seat cannot type (W4, W8) |
| 328 | Third: Developer ticks on a test the Tester later rewrites, from 5 of 5 toward 0 over 3 nights | Night 1 of 3 at 13: 10 in walk 2 and 3 before versions 2 to 4 in walk 3 (`night167-cycle1.md`, the night-read list) |
| 329 | Second: tickets with two criteria of one text, from 1 of 3 toward 0 | 0 of 5 tickets. 0 twin refusals on `criteria.respecify` in 21 calls. Night 1 of 3 |
| 323 | Fourth: the seats where it is better, one profile line per seat and one night, and Roman rules the switch | The night ran. Section 4 is the measure, and section 5 holds the question |
| 322 | Second: criteria that a page reply calls wrong, from 3 of 7 on item 3 toward 0 | Item 3: 1 of 1 called wrong, twice, m180 and m195. Item 1: m105, m118 and m124 call criteria lines of tk_3 wrong, not mapped to rows here |
| 315 | Second: batches that run with no criterion that holds his landed correction, from 1 of 5 toward 0 | 0 of 3 batches with a head. The sign moved to the item text: 6 removal requests for one sentence (W1) |
| 306 | Third: merged changes that hold a line his words refused, from 2 of 2 toward 0 | No merge, no sample. First half: m180's words reached c_1 at s342 only, after the CYCLE |
| 311 | Third: review ticks quarantined with the code right, from 1 of 2 toward 0 | No review ran. No sample |
| 312 | Third: pages that say the team stopped work while a tick is quarantined, from 2 toward 0 | 5 stop pages, each after a `tests_failing` quarantine, each naming 3 attempts. The shift page m_p2 hides the quarantined contested tick (W11) |
| 318 | Second: tick sessions after a quarantine on an unchanged red, from 3 toward 0 | Not this frame's case. bg_6 ran attempts 2 to 5 on 35 unchanged errors, and the tick row reads 1 attempt. Each re-encode moved the test body, and the lift rule was not read |
| 321 | Third: return-value tests refused on a criterion about text, from 5 of 5 toward 0 | 0 prints-door refusals in 62 `tests.encode` calls. Night 2 of 3 |
| 324 | Second: criteria whose surface names `examples/` where the item names the library, from 2 of 3 on `clear` toward 0 | 1 of 2 on `clear`: s280's respecify. s318 tried `examples/completion/completion.py::show_env`, refused by the touch set. Architect repeats not read |
| 325 | Second: page lines his reply asks to remove as a seat's account, from 3 toward 0 | 0 in the log's 35 replies. The pages were not read line by line |
| 283 | Second: batches whose first red project test follows an unnoted removal, from 1 of 4 toward 0 | 0 of 3 batches with a head. 19 note-door refusals, all right: the `echo` line of `clear` and the 3 statements of `format_filename` stayed. Night 2 of 3 |
| 140 | A batch whose first red follows a landed write with a dropped note | 0. Both `drop_notes` rows are `restored` |
| 266 | Second: Liaison sessions that end on a repeated parse refusal, from 1 of 81 toward 0 | 0 of 105. 22 parse refusals in 9 sessions, 17 of them in 6 Gemma Tester sessions, 10 in s126 |
| 316 | Second: agenda pages that carry another item's rows, from 5 toward 0 | The agenda page m162 carries `clear`'s rows only. 1 page read |
| 319 | Second: criteria that name an exception from no source, from 2 of 6 toward 0 | 0 of 16 criteria name an exception |

(observed: the stack blocks by `grep -n "^### <n>\. "`, the tables named in
section 2, the jsonl pages m_p2, m_p3, m42, m149 and m162, 2026-10-26.)

**Question 3. Frame 328 after pass 3 and 3b, 4bb2656b. 6 refused challenges
of 50 and 1 dropped re-encode of 6 pass the new code, all in walk 2.** The
replay read each challenge from the completions and ran `_span_of` and
`_unescaped` of `rota/core/sandbox.py` at 4bb2656b against the rows (observed:
the replay, `tool_calls`, `turns`). The counts:

1. Let through: s284's calls at turns 17, 19 and 20 and s286's at turns 2, 3
   and 5. Each quotes the live tk_3 text verbatim and the test line as
   `\x1b` or `\u001b`. The test half now reads the escape as the ESC byte.
   The first call of each ref set would deliver. The later calls hold the
   same refs on an unchanged tst_tk3, so they meet the repeat door (reasoned:
   `_same_refs_refusal`, its threshold not read). A Tester woken after s280
   then meets W5's two doors, as s281 and s283 did (observed).
2. Not let through, walk 1: 11 calls in s143, s146 and s147 quote
   `mock_appdata = "C:\\MockAppData"` and the row holds one backslash. The
   unescape reads control escapes only (W2).
3. Not let through, walk 2: 14 calls. Quotes wrapped in `'` that end at
   "corner.", the v1 text, a prose string, the Developer's own `echo` line,
   and two calls with no quotes. The criterion half is unchanged since
   40b16f78 (observed: `diff` of `_span_of`).
4. Not let through, walk 3: all 13. The 12 criterion-half refusals start with
   one `'` and end with `.` or `''.`, so the outer quote is no pair, and the
   decoded text keeps a leading `'` (W8). One quotes the request in place of
   the criterion.
5. Dropped re-encodes: the guard returned "already has a test this session"
   6 times, s126 once, s142 four times and s271 once. At 4bb2656b the guard
   opens only for a test that got the encode note in the session
   (`encode_noted`, `api.py` 17447 and 10703). The note fired in s271 only.
   So s271's passing tst_tk3 lands as version 2, and bg_5 goes green at
   57f75f44. Walk 2's 10 Developer sessions and pages m149 and m158 then had
   no cause (reasoned). s329's "identical to what is already on file" is
   right, and the call-cache returns in s126, s271, s333 and s343 are not the
   guard.

**Question 4. Frame 315 after 01c0f5fa. Yes, at s161, and not by the removal
route.** The new page-sentence check refuses an assert that adds his sentence
about the page, and `_item_sentences` reads "Its check calls the function
..." of e_m58 as a page sentence (observed: the function at 4bb2656b on the
entry's text; `api.py` about 1896). So s161 seq 9 is refused, the step says
to keep the item and send `msg.report_liaison`, and line 1 keeps its one
sentence (reasoned). The removal route alone gives no exit on these rows.
The door accepts a drop of the added sentence, and `_added_sentences` names
it (observed: the sentence copies e_m58, and no statement holds it). But the
step shows only in a refusal, and no assert in s176 to s233 met one: s176,
s212, s226, s231 and s233 got `unchanged`, and s187 and s199 landed
(observed: the results of `problem.assert`). s187's appended sentence does
not match his page sentences at 0.8, so the page check does not refuse it
(observed: the replay). The first exit by removal would need a seat that
sends the first sentence alone, and none did.

**Question 5. Frame 322 after 7d37adcd. The door refuses 1 landed criterion
and 3 repeat calls, all on item 3, and his replies agree.** Only
`tk_1_format_filename_example` names "docstring" as a whole word in its
headline (observed: `tickets`). The door refuses c_1 v1 at s312 turn 1,
"When shorten=True, format_filename(a/b/c.txt) returns 'c.txt'.", and the 3
later `criteria.specify` calls of the same words in s312 (reasoned: the
predicate at 4bb2656b). It admits s318's four docstring texts, which the
surface door refused, and s342's v2. It does not fire on the 15 criteria of
items 1 and 2. His m180 says "Line 2 is about what the function returns ...
the code itself must not change", and m195 says "Line 2 still talks about
what the function returns". Both call wrong the one criterion the door
refuses, and both ask for the text that v2 holds. No page showed v2 before
the night ended.

## 4. The Gemma measure

The measure is per seat, against night 166's qwen3.5:9b in the same seat, on
the same items in the same order. Each row is a count, not a score.

| Measure | Tester, Gemma, n167 | Tester, qwen3.5:9b, n166 | Critic, Gemma, n167 | Critic, qwen3.5:9b, n166 |
|---|---|---|---|---|
| Sessions, turns | 14, 109 | 12, 73 | 16, 82 | 17, 82 |
| Wakes | 4 `tests_missing`, 10 message | 4 `tests_missing`, 8 message | 16 `tick:challenge`, 0 review | 14 challenge, 3 review |
| Encodes or verdicts | 62 `tests.encode`, 13 test receipts | 51, 11 | 0 `verdicts.emit`, 14 upholds, 0 breaks | 13 `verdicts.emit`, 3 passes, 14 upholds, 1 break |
| Reads | 21 `code.source` | 18 | 314 `code.source` | 18 |
| Refusals, new ERROR lines | 91, of them 10 cuts and 17 parse refusals | 72, 0 cuts | 10, of them 5 cuts | 57, 0 cuts |
| Tests red on any right code | 4 tests in 7 landed versions: tst_c4 v1, `'tst_c5` v1, tst_tk3 v1, tst_c1 v1 to v4 | 3 tests, s198's tst_c1 to tst_c3 (night 166 W-A) | none to judge | none |
| Right fixes | 3: `'tst_c5` v2 (s141), tst_c1 to tst_c3 (s142 t4), tst_tk3 (s271, dropped) | the W-A rewrites | | |

(observed: `sessions`, `turns`, `tool_calls`, `receipts`, `verdicts`,
`test_run_journal` of both nights, the cut and refusal counts by the delta of
"ERROR" lines between consecutive prompts.)

The confounders, named:

1. **Both walls that stopped the walks the Gemma seats reached were rota's
   doors.** In walk 2 the one-test guard dropped the fix (W3). In walk 3 no
   door reads the test path (W7). The `src/` path is not Gemma's alone:
   night 166's qwen3.5:9b Tester sent 16 encodes at `src/click/utils.py`,
   s117 to s121, and the fence refused them for another reason (observed:
   section 5, C1).
2. **The one-test guard dropped the Gemma Tester's right fix.** s271 wrote a
   passing tst_tk3 one turn after the note. With pass 3 on the head, walk 2
   would likely have reached the Critic (reasoned: question 3, item 5).
3. The Critic's trial score, 0.79 against 0.40, has no night measure. No
   batch reached a review on night 167, so the Gemma Critic only upheld
   claims, with 17 times the reads of night 166's Critic.
4. Walk 1's two red tests are the call's escape level (W2), not the test's
   logic, and walk 1's stop is upstream of both seats (W1).

**Question 6. The reply cuts: 15 cuts in 14 of 30 Gemma sessions, and a cut
precedes 2 of the 7 wrong encodes.** By seat: Tester 10 cuts in 10 of 14
sessions, Critic 5 cuts in 4 of 16. The qwen seats of the same night: 9 cuts
in 314 sessions. Night 166's qwen3.5:9b in the same two seats: 0 cuts in 29
sessions (observed: the delta of "ERROR reply cut" in consecutive prompts).
The cuts match the serving shape that the interview read found with think
off (reasoned: `plans/frame323-gemma-interview.md`). The wrong encodes that
landed, in order:

| Encode | Session, turn | Cut before it in the session |
|---|---|---|
| `'tst_c5` v1 | s126 t2 | no |
| tst_c4 v1 | s142 t2 | no |
| tst_tk3 v1 | s271 t2 | no, the cut is at t4 |
| tst_c1 v1 | s326 t3 | yes, t2 |
| tst_c1 v2 | s333 t4 | no |
| tst_c1 v3 | s335 t4 | yes, t2 |
| tst_c1 v4 | s343 t2 | no |

So a cut does not explain the wrong tests. The wrong path is in all four
versions, with and without a cut (reasoned).

## 5. The recommendation

**Question 1, frame 323's fourth clause.** The provenance first. Roman asked
on 2026-10-25 at 01:40 to test `gemma4:12b-it-qat` on the recorded cases and
to switch where it is better (ruled: Roman, frame 323's site line). The trial
gave Gemma 0.79 at the Critic against 0.40 and 0.73 at the Tester against
0.53, and lower at the Developer and the Terminologist. The interview found
a serving fault with think off (observed: frame 323, status lines of 11:27,
12:20 and 04:48). He ruled at 18:57 that the Gemma night runs after frame
327's fix, and night 167 ran it in the Critic and Tester seats (ruled: Roman,
2026-10-25 18:57). The question he rules on:

> Keep qwen3.5:9b in the Critic and Tester seats, and give Gemma one more night only after the path door and frame 328's pass 3 are on the night's head? I recommend yes: rota's doors stopped walks 2 and 3, the Critic reached no review, and Gemma's 10 Tester cuts match the serving fault.

**The order of the next sprint, largest wall first.** The economy is 20 live
of 10, so each candidate is placed and not pushed.

| Rank | Row | Frame | Site | Red test | Price |
|---|---|---|---|---|---|
| 1 | The gate at 4bb2656b, so that pass 3 of 328, 01c0f5fa of 315 and 7d37adcd of 322 are on night 168's head | 328, 315, 322 | the branch | the gate's known reds | 1 gate, about 15k of context |
| 2 | **A test path that is a program file is refused, and a collection error at encode goes back to the Tester** (W7, W2's second half) | C1, after 328 | `tests.encode` path check, `_encode_run` | s326 t3; s142 t2 tst_c4 | 1 read, about 40k; 2 build, about 60k and a review |
| 3 | The criterion half reads an unpaired outer quote and `\'` as the seat's call syntax | 328, residue | `_span_of`, `rota/core/sandbox.py` | s336 t5; s327 t3 | 1 cycle, about 40k and a review |
| 4 | A qualified `examples/` surface on a respecify, and the two doors that refuse each other | 324 | `criteria.respecify` and the surface door | s280; s281 turns 2 and 3 | its pending read, about 60k; 2 build |
| 5 | The shift page names a quarantined tick of the parked item | 312, second half | the shift page's rows | m_p2 | 1 cycle, with the frame's lever |
| 6 | Roman rules the switch | 323 | the profile | the question above | his answer only |
| 7 | The call's escape level of a body | C2 | the encode door and the call parser | s142 t2's body | 1 read, about 40k |

The next night: the same three items in the same order, on the head of rank
1, with the profile Roman rules. Rank 2 is the only wall with no frame that
stopped a walk, and without it item 3 meets the same path (reasoned).

**The candidates not on the stack:**

- C1, the test path that replaces the module. Ends when: first,
  `tests.encode` refuses a path that is a file of the code index outside the
  test folders and names a test path, with s326 t3 and night 166's s117 as
  the red tests; second, an encode whose run errors at collection goes back
  to the Tester, with s326 t3 and s142 t2; third, on a night, encodes at a
  path under `src/`, from 15 of 62 toward 0 over the next 3 nights. The count
  over nights 163 to 167: 0, 0, 0, 16 and 15 encodes; night 166's 16 were
  qwen3.5:9b and none stored, night 167's 15 were Gemma and 4 versions
  stored (observed: `tool_calls` and `tests` of the five databases).
- C2, the escape level of a body in the call. Ends when: a body that holds
  an invalid escape is refused at encode with the raw string form named,
  with s142 t2 as the red test, and on a night, Tester sessions with a
  SyntaxError at collection from 2 toward 0 over the next 3 nights.

## Usage

One agent on Opus, no extract agents and no interviews. About 235k tokens on
the harness counter, over the 120k cap. Not read: the repeat door's threshold
for the walk 2 replay; the lift rule behind bg_6's tick row (frame 318); the
Architect's bare-symbol repeats (frame 324); the walk pages line by line for
frame 325; the mapping of m105, m118 and m124 to criterion rows (frame 322);
the constraint_zero tick (W12).
