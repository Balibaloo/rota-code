# Night 168, the read: no merge of three, because one stuck batch held the only seat for the whole night

Meta workflow, read on 2026-10-26 at 18:02. Night 168 ran cold from
`C:/Users/roman/rota_n168` at e03b1098, 09:13 to 10:05, on the items of nights
163 to 167 rotated as on nights 166 and 167: `get_app_dir`, `clear`,
`format_filename`. The profile was `local-gemma-cr-ts`: `gemma4:12b-it-qat` in
the Critic and Tester seats, `qwen3.5:9b` in the Developer and Terminologist
seats, `qwen3:8b` in every other seat, and the agent principal on Opus. It
exited 0 with GAUNTLET-DONE (observed: `.rota/night168.log` lines 1, 4, 9 and
120). Sources: `.rota/clickI_night168.db` opened `?mode=ro`,
`.rota/night168.log`, `.rota/night168.err`, the night 168 rows of
`.rota/clickI_night168.principal.jsonl`, `.rota/clickI_warm.db` for the end of
onboarding, `.rota/clickI_night166.db` and `.rota/clickI_night167.db` opened
`?mode=ro`, the commit d607d440 in `D:/repos/_AI/sample_repos/clickI`, the
source at e03b1098, and the stack blocks. One agent on Opus. No model ran and
no pytest ran.

**The result. 0 merges of 3 items, the same as night 167, against 2 of 3 on
night 166.** Walk 1 ended stuck after 81 steps: the Developer's commit
d607d440 is right, and two Gemma tests error at collection on a backslash
that the call strips. Walks 2 and 3 ended quiet after 30 and 39 steps with
no batch started, because the stuck `batch_1` keeps the only batch seat: its
`tests_failing` key is quarantined at 3 sessions, and the ladder and the park
fire only at `loop_cap` 10 run attempts. **So the night is one wall, rota's,
with a Gemma seat's reading under it.** The Gemma Tester wrote one test that
is green on the right code, tst_crit_3 v3, one turn after frame 328's new
collection note, and it had 0 reply cuts in 9 sessions. The Gemma Critic
again reached no review, and he called 2 of its 3 item challenges wrong.

## 0. The night in numbers

| Measure | Value |
|---|---|
| Phases | onboarding 09:14 to 09:27, 109 steps, 3 asks, 4 replayed calls; walk 1 09:27 to 09:58, 81 steps, 7 asks, quiet and stuck; walk 2 09:58 to 10:01, 30 steps, 5 asks, quiet and stuck; walk 3 10:01 to 10:05, 39 steps, 7 asks, quiet with `clear` waiting behind `format_filename` |
| Asks | 20 live calls: 0, 7, 6 and 7 (night 167: 35; night 166: 13) |
| Principal | 20 live calls on Opus, 1.88 dollars: 0.71, 0.54 and 0.63 by walk (night 167: 3.52; night 166: 1.04). He read 20.0k characters of pages and wrote 3.9k (night 167: 46.4k and 9.0k; night 166: 8.65k and 2.25k) |
| Batches | 3. `batch_1` `get_app_dir_windows` running at d607d440, 37 tests, 2 errors at collection. `batch_2` `clear_returns_status` and `batch_3` `format_filename_example` pending, never started, no worktree. 4 tickets, 6 criteria. 3 park rows, all shift: 2 `now` for `get_app_dir`, 1 `park` for `clear` |
| Merges | 0 of 3 (night 167: 0 of 3; night 166: 2 of 3) |
| Verdicts | 0 rows. The Critic woke 17 times, all on `tick:challenge`, 14 in onboarding and 3 on items, and 0 times on `tick:review` (night 167: 16 and 0; night 166: 3 passes, 3 review wakes) |
| Sessions | 226 sessions, 888 turns (night 167: 344 and 1518; night 166: 213 and 832). Liaison 64, Vision Keeper 58, Terminologist 33, Architect 27, Developer 18, Critic 17, Tester 9 |
| By walk | onboarding s1 to s101, 361 turns; walk 1 s102 to s169, 363 turns; walk 2 s170 to s194, 77 turns; walk 3 s195 to s226, 87 turns |
| Commits | 24 `code.commit` calls, 1 landed: d607d440 (s126). The note door refused 6 calls in s122 to s124. 1 `drop_notes` row, `restored` |
| Quarantines at the end | `-|tick:constraint_zero|` at 3; `developer|tick:tests_failing|batch_1` at 3 |
| Faults | 0 rows (night 167: 3; night 166: 2) |
| CYCLE lines | 2: walk 1, `developer|tick:tests_failing|attempt 3|["batch_1"]`; walk 2, `liaison|message|converse|[]` (night 167: 1; night 166: 1) |
| `nightcount` | 226 sessions, 888 turns; made up 22 turns in 10 sessions; 0 writes after an invention; 11 dangling-pointer turns in 5 sessions, most s24 (7); 6 wakes repeated, 22 sessions, 16 of them repeats (night 167: 68 in 38; 87 in 10; 15, 52, 37) |
| err file | 134 lines after the worktree lines, every one a `SyntaxWarning` for `"\R"` or `"\L"` from `<unknown>`, and no traceback. The last line is at 09:57 |

(observed: `night168.log` lines 1 to 121, `night168.err`, `sessions`,
`turns`, `tool_calls`, `receipts`, `batches`, `tests`, `test_run_journal`,
`verdicts`, `faults`, `drop_notes`, `tick_attempts`, `item_parks`, the jsonl
rows with `night` 168, and `.rota/clickI_warm.db` at 101 sessions,
2026-10-26.)

## 1. The walks

**Walk 1, `get_app_dir`. The wall is the call's escape level, candidate C2,
and the walk ends at the `tests_failing` quarantine.** The batch_start
sessions s122 to s124 committed nothing, because the note door refused 6
commits that rewrote `return os.path.join(folder, app_name)`, and it was right
(observed: the refusals; d607d440 keeps the line). s126 then landed d607d440:
when the variable is `None`, the folder is AppData Roaming or AppData Local
under the home folder. That is the item (observed: `git show d607d440`). The
Gemma Tester typed `"AppData\\Roaming"` and `"C:\\Users\\"` in its calls. The
call parser keeps one backslash, so 11 encodes were refused as "the body is
not Python", and 6 landed encodes hold `"AppData\Roaming"` or
`"AppData\Local"` (observed: s115, s127, s142 refusals; `tests` rows; s146's
call against its stored body). Rota's `_ast.parse` admits `\R` with a warning,
which is the err file. Click's `filterwarnings = ["error"]` makes it a
SyntaxError at collection (observed: `pyproject.toml` at 2c8cd3a, journal seq
69 and 174). Frame 328's collection note fired on all 6 (section 3). The
Developer's challenges failed on the same escape and on a stale criterion
text, the CYCLE at s134 to s136 (question 4). His pages m47 and m53 asked to
fix two tests, and the relay reached a Terminologist mode with no call that
reaches the Tester (W4). Candidate C2, with C3 and frame 328 beside it.

**Walk 2, `clear()`. The wall is the batch seat, candidate C4.** The item,
its tickets, its two criteria, `batch_2` and its touch note all landed, and he
answered "Ok, go ahead" on m73. `batch_2` never started (observed: `batches`,
status `pending`, no worktree). `batch_start` refuses while a batch runs, and
`batch_1` stays `running`. Its `tests_failing` key is quarantined at 3
sessions, the `exhausted` ladder and the `do:park` deferral read run attempts
against `loop_cap` 10, and the newest attempt is 6 (observed:
`predicates.py` `exhausted` and `preempt`, `scheduler.py` `parked`,
`config.py` line 59, `test_run_journal`). No preempt fires either, because
every item holds priority 1. On the shift page m_p2 he chose "Now, please"
for `get_app_dir` (observed: `item_parks` ip_797c3c03f0). The walk's CYCLE is
in the converse of m76 and m78 (question 5). Candidate C4; the CYCLE is W-B of
night 166.

**Walk 3, `format_filename`. The wall is the same seat, C4.** `batch_3`
landed its criterion and touch note and never started (observed: `batches`).
He chose "Now, please" for `get_app_dir` again and "Later" for `clear` on
the shift pages of m_p3 (observed: log lines 98 and 99, `item_parks`). The
walk ended quiet with `clear` waiting behind `format_filename` (observed: log
line 109). The Gemma Critic broke the item's claim with a quote from another
docstring, and he called it wrong on m101 (W6). Frame 322's door had no case
to fire on (question 6). Candidate C4.

## 2. The walls

| # | Wall and sign | Sessions | Cause by `plans/wall-guide.md` | Frame |
|---|---|---|---|---|
| W1 | **A body's backslash loses one escape level in the call, and the encode door admits the invalid escape that the project's pytest refuses.** 11 encodes refused as not Python; 6 landed encodes error at collection; 134 warning lines in the err file | s115, s127, s128, s133, s141, s142, s143, s146 | Cause 4 at the seat, the call form needs two escape levels; cause 8 at `tests.encode`, its parse check is not the project's collection rule. Cause 9 behind it: the collection note quotes pytest's `Did you mean "\\R"?`, and that form loses its level again in the call | candidate C2 |
| W2 | **The quote check refuses a quote of the test on the backslash form.** 16 of 19 test-half refusals and 5 of 18 criterion-half refusals hold `\\` where the row holds one backslash | s144, s145, s147, s149, s150, s167 | Cause 7: one call reads `\\` as one backslash in `body` and as two in `quotes` (observed: s146's stored body, s147's refusal text); cause 8 at the door | candidate C2, the quote face |
| W3 | **The Developer quotes a superseded criterion text.** crit_3 v1, "under C:\Users\<user>\.config.", in every challenge of the CYCLE; the first call of each of s134 to s136 lacked `quotes` | s129, s130, s134 to s136 | The door held, frame 328's second clause. The missing `quotes` is frame 285's sign. Where the seat read v1 is not read | 328, held; 285 parked |
| W4 | **His corrections of two tests reach a Terminologist mode that cannot act.** m50 and m57 carry `principal_test_verdict` revise for tst_crit_1 and tst_crit_2, with refs crit_1 to crit_3. `park_criterion_relay` needs every ref to be a ruled criterion, crit_3 is not, so the mode is the glossary `relay`, which holds `glossary.adopt` only | s156 to s157, s165 to s166 | Cause 6, the mode key reads a ref set wider than the ruling; cause 11 behind it, what is his does not reach the seat. In s140 the same route with one ref reached `criterion_repair`, and the Tester fixed tst_crit_3 | candidate C3; frame 306's sign, frame 278 parked beside it |
| W5 | **A running batch whose `tests_failing` key is quarantined below `loop_cap` keeps the only batch seat.** No ladder, no park, no preempt; `batch_2` and `batch_3` never start | after s154, walks 2 and 3 | Cause 12: the tick key counts 3 sessions and the ladder counts 10 run attempts, and no rule reconciles the two. The shift page offers "now: answer its open page first" when no page is open | candidate C4 |
| W6 | **The Gemma Critic breaks an item's claim on the fact the change will change, or on another function's docstring.** s189 cites `def clear() -> None:`; s220 quotes the `LANG=C.UTF-8` docstring. He called both wrong, m75 line 5 and m101 line 4 | s189, s220 | Cause 5, the seat reads the fact and judges wrong | 323 |
| W7 | **The naming door refuses a contest that rests on his earlier answer in the exchange, and the ruling then approves the line he called wrong.** m76 says "Line 5 is wrong"; m78 names line 6 only; s193 is refused twice and s194 lands r_448c39118c with line 5 `approve` | s191 to s194 | Cause 2, the door reads his last words and not `earlier_exchange` | W-B of night 166, in its read; candidate |
| W8 | **The page's check line shows the file and the line of a red, and not its error.** m47 and m53 show "Fails: File ... line 13"; he read a wrong cause, "doesn't clear both variables" | m39, m47, m53 | Cause 11, what reaches him is not the fact | candidate C5 |
| W9 | **The Liaison's ruling on m53 fails, and the page goes back to him once.** s162 sent 8 calls and s163 ended on a parse refusal | s162, s163 | Cause 7 and the coverage door's refusal; s104 also ended on a parse refusal | 266 |
| W10 | **The note door refuses 6 batch_start commits, each right.** Three sessions commit nothing before s126 | s122 to s124 | No fault; the door held | 283, measured |
| W11 | **The constraint tick quarantines at onboarding**, as on nights 164 to 167 | s1 | Not read | none |

(observed: `tool_calls`, `turns`, `receipts`, `tests`, `test_run_journal`,
`messages`, `item_parks`, the jsonl pages m39, m47, m53, m_p2, m75 and m101,
and the code at e03b1098.)

## 3. The frames measured

| Frame | Ends-when clause | What night 168 read |
|---|---|---|
| 328 | First: a test written on a batch with a head runs at encode, and a red goes back to the Tester | Fired: 6 collection notes on 6 landed encodes, s128, s133, s141, s143 twice, s146. 0 path-door refusals; 0 of 61 encodes under `src/`. The re-encode after the note landed as tst_crit_3 v3 in s141, green |
| 328 | Second: a challenge quote must be in the live criterion text | Held: 0 challenges passed on an old text. 51 calls, 2 delivered, m44 and m45. The door also refused 21 quotes on the backslash form (W2) |
| 328 | Third: Developer ticks on a test the Tester later rewrites, from 5 of 5 toward 0 over 3 nights | Night 2 of 3 at 7: s129, s130 and s134 to s136 on tst_crit_3 v1 and v2, s144 and s145 on tst_crit_1 v1 (night 167: 13) |
| 329 | Second: tickets with two criteria of one text, from 1 of 3 toward 0 | 0 of 4 tickets. The twin door refused 1 `criteria.specify` at s184, right. 0 twin refusals in 3 respecify calls. Night 2 of 3 |
| 323 | Fourth: the seats where it is better, one profile line per seat and one night, and Roman rules the switch | The night ran on his word of 09:01. Section 4 is the measure, and section 5 holds the question |
| 322 | Second: criteria that a page reply calls wrong, from 3 of 7 on item 3 toward 0 | Item 3: 0 of 1. The door fired 0 times: c_1 v1 named the docstring on the first call. His m101 says "Lines 1 to 3 are fine", and line 3 is c_1. Item 1: crit_3 v1 called wrong on m30, ".config", respecified at s121 |
| 315 | Second: batches that run with no criterion that holds his landed correction, from 1 of 5 toward 0 | 0 of 1 batch with a head: crit_3 v2 holds m24 and m30. 0 line-1 removal requests |
| 306 | Third: merged changes that hold a line his words refused, from 2 of 2 toward 0 | No merge, no sample. First half's sign twice: W4, his test words reach no Tester; W7, s194 approves a line m76 calls wrong |
| 311 | Third: review ticks quarantined with the code right, from 1 of 2 toward 0 | No review ran. No sample |
| 312 | Third: pages that say the team stopped work while a tick is quarantined, from 2 toward 0 | 2 stop pages, m39 and m47, each after a `tests_failing` quarantine, each naming 3 attempts (night 167: 5). The shift page m_p2 names `batch_1`'s 2 failing tests and the 3 attempts, so night 167's W11 did not show |
| 318 | Second: tick sessions after a quarantine on an unchanged red, from 3 toward 0 | 0. The lift after s137 followed a changed failing set: tst_crit_3 v3 green, tst_crit_1 and tst_crit_2 new. After s154 no Developer tick ran |
| 321 | Third: return-value tests refused on a criterion about text, from 5 of 5 toward 0 | 0 prints-door refusals in 61 `tests.encode` calls. Night 3 of 3 at 0, after 0 of 51 and 0 of 62, so the clause reads met (reasoned) |
| 324 | Second: criteria whose surface names `examples/` where the item names the library, from 2 of 3 on `clear` toward 0 | 0 of 2 on `clear`, 0 of 6 overall. s121 tried `examples/aliases/aliases.py::read_config` on crit_3, refused by the touch door. Architect repeats not read |
| 325 | Second: page lines his reply asks to remove as a seat's account, from 3 toward 0 | 1 line: m53 line 9, "The implementation already handles this correctly", asked twice because the page was sent twice. In onboarding m13 asks to drop m11 line 2 if it is not the README check |
| 283 | Second: batches whose first red project test follows an unnoted removal, from 1 of 4 toward 0 | 0 of 1 batch with a head; 35 of 35 project tests pass at d607d440. 6 note-door refusals, all right. Night 3 of 3 at 0, so the clause reads met (reasoned) |
| 140 | A batch whose first red follows a landed write with a dropped note | 0. The one `drop_notes` row is `restored` |
| 266 | Second: Liaison sessions that end on a repeated parse refusal, from 1 of 81 toward 0 | 2 of 64: s104 and s163 (night 167: 0 of 105). s163 cost a resend of m53 (W9) |
| 316 | Second: agenda pages that carry another item's rows, from 5 toward 0 | 0 of 3: m53, m75 and m101 each carry their own item's rows only |
| 319 | Second: criteria that name an exception from no source, from 2 of 6 toward 0 | 0 of 6 criteria name an exception |
| 326 | First: every case the per-model table counts can pass on its fixture; the residue on the head is the copy guard of `code.write` | 0 copy-guard refusals in 29 `code.write` calls. The clauses are register measures, and a night does not read them |

(observed: the stack blocks by `grep -n "^### <n>\. "`, the tables named in
section 2, the jsonl pages, 2026-10-26.)

**Question 1. Why 52 minutes and 0 merged.** Walk 1 stopped at the
quarantine of `developer|tick:tests_failing|batch_1`. The code at d607d440 is
right, and tst_crit_1 v2 and tst_crit_2 v1 error at collection (observed:
journal seq 211 and 212). Walks 2 and 3 stopped because `batch_1` keeps the
only batch seat (W5). Each walk ended at its quiet bound in 3 to 31 minutes,
because no tick was left to wake. The stop is a rota door: the encode door
admits a body that the project's pytest refuses (W1), and two counters of one
fact keep the stuck batch running (W5). A seat's reading is under the first:
the Gemma Tester typed the escape at the wrong level in 6 of 7 landed encodes
(reasoned: W1). The harness is not the stop: the err file holds no
traceback, and the night has 0 fault rows (observed).

**Question 3. Frame 328 at e03b1098.** Path-door refusals: 0. Collection-error
notes: 6, on every landed encode that errored (observed: the note text "The
run of this body on the batch's head errors when pytest collects"). Encodes at
a path under `src/`: 0 of 61, against 15 of 62. Developer ticks on a test the
Tester later rewrote: 7, against 13. The one-test guard returned `unchanged`
once, at s128 turn 3, on a malformed id `'tst_crit_3` (observed). The note
reached the seat each time. It moved the seat once: in s141 the Tester typed
four backslashes, and v3 is green on the same commit (observed: s141 turn 2,
journal seq 139). In s143, s146 and s148 the Tester sent the same two-backslash
form, and the rows kept one (observed).

**Question 4. The walk 1 CYCLE, `developer|tick:tests_failing|attempt
3|batch_1`.** The test: tst_crit_3 v2, stored by s133, line 16 `assert
"AppData\Roaming" in path_roaming`, a SyntaxError at collection under
`filterwarnings = error`. The code: d607d440, right by the item. The test was
wrong by its escape and not by its logic: v3, the same body with `\\`, passes
on d607d440 (observed: journal seq 104 and 139). Each of s134, s135 and s136
sent a challenge with no `quotes` and then one that quotes crit_3 v1, and the
door refused both, right (observed). The fix came only after the quarantine
and his page m39, through the Terminologist's `msg.answer_tester` m43 to s141.
Candidate C2 holds the cause. Frame 328 held, and frame 285's sign is the
first refusal of each session.

**Question 5. The walk 2 CYCLE, `liaison|message|converse`. Yes, it is W-B of
night 166 by the rows, and it ends worse.** The page m75 put the Critic's
break on line 5. He answered m76: "Line 5 is wrong ... I don't understand line
6". s191 and s192 sent `{5: contest, 6: ask}`, refused as an ask in a ruling,
then asked m77. He answered m78, which names line 6 only. s193 sent line 5
`contest` twice: "The words name line 6 and do not name line 5". m76 is in the
prompt as `earlier_exchange`, and the door reads m78 alone (observed: s193's
prompt and refusals). This is W-B's cause, the door lacks a fact the prompt
holds. Night 166's third answer landed right. Here s194 landed
r_448c39118c with line 5 `approve`, a ruling against his words, with no resend
(observed: `rulings`). What the approve of `challenge_items_clear_returns_status`
does to the item is not read.

**Question 6. Frame 322 at e03b1098, on item 3.** The documentation door fired
0 times and refused nothing. s211 sent one `criteria.specify`, and c_1 v1
names the docstring: "The docstring of `format_filename` includes an example
demonstrating that when `shorten=True`, the path `a/b/c.txt` is displayed as
`c.txt`." (observed: s211, `criteria`). His four replies on item 3 agree:
m89 faults the touch plan, m95 answers a clarify, m99 is "ok", and m101 says
"Lines 1 to 3 are fine" and faults the Critic's line 4. The glossary door's
offer of 3b did not fire in the walks (reasoned: no `msg.answer_tester`
refusal in the Terminologist's walk sessions).

## 4. The Gemma measure

The measure is per seat, against night 166's `qwen3.5:9b` in the same seat
and night 167's Gemma, on the same items in the same order. Each row is a
count, not a score. Night 168 measured the Tester on one item only, because
only `batch_1` started.

| Measure | Tester, Gemma, n168 | Tester, Gemma, n167 | Tester, qwen3.5:9b, n166 | Critic, Gemma, n168 | Critic, Gemma, n167 | Critic, qwen3.5:9b, n166 |
|---|---|---|---|---|---|---|
| Sessions, turns | 9, 55 | 14, 109 | 12, 73 | 17, 84 | 16, 82 | 17, 82 |
| Wakes | 4 `tests_missing`, 5 message | 4 and 10 | 4 and 8 | 17 `tick:challenge`, 0 review | 16 challenge, 0 review | 14 challenge, 3 review |
| Encodes or verdicts | 61 `tests.encode`, 6 test receipts | 62, 13 | 51, 11 | 0 `verdicts.emit`; 13 upholds, 2 breaks | 0; 14 upholds, 0 breaks | 13 `verdicts.emit`, 3 passes; 14 upholds, 1 break |
| Reads | 10 `code.source` | 21 | 18 | 315 `code.source`, 46 `code.probe` | 314 | 18 |
| Refusals, new ERROR lines | 70: 11 not Python, 5 parse, 3 with no batch, 2 NameError, 2 one file | 91, of them 17 parse | 72 | 8 | 10 | 57 |
| Review wakes | none | none | none | 0 | 0 | 3 |
| Tests red on any right code | 2 of 3 final tests; 6 of 7 landed encodes error at collection; tst_crit_1 and tst_crit_2 set the variables to `""` and not unset, and tst_crit_2 calls with no app name | 4 tests in 7 versions | 3 tests, W-A | none to judge | none | none |
| Tests green on right code | tst_crit_3 v3, from s141 one turn after the note | 0 stored; s271's fix dropped | the `get_app_dir` tests, green on their first version | | | |
| Item challenges he called wrong | | | | 2 of 3: m75 line 5, m101 line 4 | not read | not read |
| Reply cuts | 0 in 9 sessions | 10 in 10 of 14 | 0 in 12 | 4 in 4 of 17, all onboarding | 4 in 4 of 16 | 0 |

(observed: `sessions`, `turns`, `tool_calls`, `receipts`, `verdicts`,
`test_run_journal` of the three nights; the cuts by turns whose next prompt
ends on "ERROR reply cut", the same method on nights 167 and 168; the refusals
by the delta of "ERROR" lines between consecutive prompts.)

The same item on the same call form, read across the three nights:

1. **The escape level is the Gemma Tester's on this item, and not
   qwen3.5:9b's.** Night 166's qwen Tester stored `"AppData\\Roaming"` and
   `"AppData\\Local"` with two backslashes on the first version, and both
   tests were green (observed: `tests` of night 166). Gemma met the escape on
   night 167, tst_c4 and `'tst_c5` v1, and on night 168, 6 of 7 landed
   encodes (observed). In one session of six it read the collection note and
   typed the right level (observed: s141).
2. **The cuts did not repeat at the Tester.** 0 in 9 sessions against 10 in 14.
   The Critic's 4 cuts are on onboarding constraint claims, as on night 167
   (observed).
3. **The Critic is still not measured at a review.** Two Gemma nights, 0 review
   wakes, because no batch went green (observed). On the 3 item claims, it
   upheld `get_app_dir` and broke `clear` and `format_filename`. He called
   both breaks wrong: "clear() returns nothing today, and that is exactly what
   this change fixes", and "the text it quotes comes from a different
   docstring" (observed: m75 line 5, m101 line 4).
4. **The confounder is rota's.** W5 stopped walks 2 and 3 before either Gemma
   seat had a batch, and W1's door half is the encode door's. With C2 on the
   head, the 6 landed encodes are refused at encode with the raw form named
   (reasoned). With C4, walks 2 and 3 start their batches (reasoned).

## 5. The recommendation

**Question 2, frame 323's fourth clause.** The provenance first. Roman asked
on 2026-10-25 at 01:40 to test `gemma4:12b-it-qat` on the recorded cases and
to switch where it is better (ruled: Roman, frame 323's site line). The trial
gave Gemma 0.79 at the Critic against 0.40, and 0.73 at the Tester against
0.53 (observed: frame 323, status line of 04:48). He ruled at 18:57 that the
Gemma night runs after frame 327's fix (ruled: Roman, 2026-10-25 18:57).
Night 167 ran it, and the Critic reached no review. He ruled on 2026-10-26 at
09:01: "If we didn't test Gemma then we haven't tested Gemma" (ruled: Roman,
in his words), and night 168 is that test. The question he rules on:

> Keep qwen3.5:9b in the Tester and Critic seats, and close frame 323 with no switch? I recommend yes: on the same item, the Gemma Tester wrote the backslash at the wrong level on both of its nights, where qwen3.5:9b wrote it right and went green on night 166, and in two Gemma nights the Critic reached no review and he called 2 of its 3 item challenges wrong.

**The order of the next sprint, largest wall first.** The economy is 20 live
of 10, so each candidate is placed and not pushed.

| Rank | Row | Frame | Site | Red test | Price |
|---|---|---|---|---|---|
| 1 | **A running batch whose `tests_failing` key is quarantined keeps no seat that another batch needs** (W5). The provenance first, by the rule of 2026-10-18: law 6's ladder, the tick key's 3 and `loop_cap` 10 | C4 | `predicates.py` `exhausted` and `preempt`, `scheduler.py` `parked` | night 168's rows after s154: `batch_2` starts | 1 read, about 60k; 2 build, about 60k and a review |
| 2 | **A body with an invalid escape is refused at encode with the raw string form named, and the quote check reads `\\` at the body's level** (W1, W2) | C2, sprint 24 row 7 | `tests.encode` parse check, the call parser, `_unescaped` in `sandbox.py` | s128 turn 2; s147 turn 4 | 1 read, about 40k; 1 to 2 build and a review |
| 3 | Roman rules the switch | 323 | the profile | the question above | his answer only |
| 4 | **A relay of his test verdict reaches the mode that can tell the Tester** (W4) | C3, beside 306 | `park_criterion_relay`, `runner.py` mode key | m50 at s157 | 1 cycle, about 40k and a review |
| 5 | The naming door reads `earlier_exchange` in the converse mode (W7) | W-B of night 166 | `_unnamed_contest` in `rota/roles/api.py` | s193 turn 1; night 166's s109 | 1 cycle, about 40k and a review |
| 6 | The page's check line shows the red's last `E ` line (W8) | C5 | the page's check row | m53 line 4 | 1 cycle, low |

The next night: the same three items in the same order, on the head of ranks 1
and 2, with the profile Roman rules. Ranks 1 and 2 are the only walls that
stopped a walk on night 168. Without rank 1, any stuck first batch ends the
night at its first walk (reasoned).

**The candidates not on the stack:**

- C2, the escape level of a body in the call (W1, W2). Ends when: a body that
  holds an invalid escape is refused at encode with the raw string form
  named, with s128 turn 2 and night 167's s142 turn 2 as the red tests, and on
  a night, landed encodes that error at collection on an escape, from 6 of 7
  toward 0 over the next 3 nights.
- C3, his test verdict reaches no Tester (W4). Ends when: a relay whose refs
  hold a criterion beside the ruled ones still takes the mode that holds
  `msg.answer_tester`, with m50 at s157 as the red test, and on a night,
  relays of a test verdict that end with no call, from 2 toward 0.
- C4, the stuck batch keeps the seat (W5). Ends when: first, the provenance
  names the rule that should free the seat; second, with night 168's rows
  after s154, a pending batch starts or the ladder wakes its first rung;
  third, on a night, walks that end with a pending batch and a quarantined
  running one, from 2 of 3 toward 0.
- C5, the check line on his page (W8). Ends when: a page's check row for a red
  test shows the run's last `E ` line, with m53 line 4 as the red test.

## Usage

One agent on Opus, no extract agents and no interviews. About 215k tokens on
the harness counter, over the 120k cap. Not read: where the Developer read
crit_3 v1's text (W3); what the approve of line 5 in r_448c39118c did to the
`clear` item (W7); the call parser's code for the two escape levels of `body`
and `quotes` (W2); the Architect's bare-symbol repeats (frame 324); the
constraint_zero tick (W11); the shift page m_p3 line by line.
