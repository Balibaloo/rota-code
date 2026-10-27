# Night 170, the read: two merges of three, and a stop at the test door on a docstring item

Meta workflow, read on 2026-10-27 at 13:34, HEAD 860ab697. Night 170 ran cold from `C:/Users/roman/rota_n170` at 26a44700, 10:51 to 11:36, profile `local`: `qwen3.5:9b` in the Critic, Developer, Terminologist and Tester seats, `qwen3:8b` in every other seat, the agent principal on Opus. Items in order: `get_app_dir`, `clear`, `format_filename` (observed: `.rota/night170_launch.log` lines 1 to 12). Sources: `.rota/clickI_night170.db` opened `?mode=ro`, `.rota/clickI_night170.principal.jsonl` rows with `night` 170, `.rota/night170_launch.log`, the clickI commit 54173e6a, `plans/night169-read.md`, `plans/night168-read.md`, the stack blocks of the twelve frames, and `plans/facts-2026-10-27.md`. One agent on Opus. No model ran and no pytest ran. No code was edited.

**The result. 2 merges of 3, against 0 of 3 on nights 168 and 169.** Walk 1 merged `get_app_dir` and walk 2 merged `clear` (observed: the log, "MERGED (1 total)" and "MERGED (2 total)"). Walk 3 built the right docstring change at 2d391b66 with 41 of 41 tests green, and stopped because no seat could land a test for its one criterion (observed: `batches` b_3 `running`, `test_run_journal`). **So the night is one wall: the test door asks for a test file, the path the Tester is told to use is taken, and his words "no new test is needed" reach no row.** The removal door of night 169 did not fire: s128's commit removed line 518 and landed on its first commit call (observed: clickI 54173e6a, the turns of s128).

## 0. The night in numbers

| Measure | Night 170 | Night 169 | Night 168 |
|---|---|---|---|
| Walks | Onboarding 10:52 to 11:00, s1 to s105; walk 1 11:00 to 11:10, s106 to s136, merged; walk 2 11:10 to 11:21, s137 to s168, merged; walk 3 11:21 to 11:36, s169 to s230, quiet and stuck | 1, partial | 3 |
| Sessions, turns | 230, 915. By phase: 105 and 388, 31 and 126, 32 and 142, 62 and 259 | 153, 657 | 226, 888 |
| Walk 3 by seat | Liaison 21, Architect 13, Vision Keeper 9, Terminologist 8, Tester 5, Developer 4, Critic 2 | | |
| Principal calls | 17 live on Opus, 1 replayed, 1.52 dollars: 0.30, 0.34, 0.25 and 0.63 by phase. He read 23.7k characters of pages and wrote 3.9k | 7 live, 4 replayed | 20 live, 4 replayed |
| Pages in the walks | W1 m20, m27, m32, m35; W2 m42, m54, m58; W3 m60, m69, m74, m85, m90, m96, m102. m90 is the stop page | 7 | 20 |
| Batches | 3: b_1 merged at be1852fe, b_2 merged at d6c347c3, b_3 `running` at 2d391b66 | 1 | 3 |
| Merged | 2 of 3 | 0 of 3 | 0 of 3 |
| Verdicts | 2, both pass: b_1 (s135), b_2 (s167). The Critic did not wake on b_3 | 0 | 0 |
| Commits | 7 `code.commit` calls, 4 landed: 54173e6a and be1852fe (s128), d6c347c3 (s165), 2d391b66 (s195) | 52 calls, 0 landed | 24 calls, 1 landed |
| Tests | 41 `tests.encode` calls: 16, 6 and 19 by walk. 9 landed, 0 in walk 3. 272 journal rows, 3 red, all AssertionError on b_1, 0 collection errors | 12 calls, 0 landed | 61 calls, 6 erred at collection |
| Faults | 4 rows: s187, s188 twice, s201 | 17 | 0 |
| Quarantines at the end | `tester|tick:tests_missing|b_3` at 3; `-|tick:constraint_zero|` at 3 | `developer|tick:batch_start|batch_1` 3 times; constraint_zero | `developer|tick:tests_failing|batch_1`; constraint_zero |
| CYCLE lines | 1: walk 3, `tester|tick:tests_missing|without a test: c_1_format_filename_example|["b_3"]` | 0 | 2 |
| `nightcount` | Made up 51 turns in 25 sessions; 0 writes after an invention; 19 dangling-pointer turns in 5 sessions; 3 wakes repeated, 7 sessions, 4 repeats; "Rota itself failed 4 times" | | made up 22 in 10 |
| Log | 0 `SyntaxWarning` lines | 112 | 134 in the err file |

(observed: `sessions`, `turns`, `tool_calls`, `receipts`, `batches`, `verdicts`, `tests`, `test_run_journal`, `faults`, `tick_attempts`, the jsonl rows with `night` 170, the launcher log; the columns of nights 169 and 168 from their reads, section 0.)

## 1. The walks by seq

| Seq | Seat | Call | What came back |
|---|---|---|---|
| 106 to 117 | Liaison, Vision Keeper, Architect | m20 confirm, r_m21, ratify; `batches.guess`; m27 present; r_m28; slicing | m28: "line 3 is vague ... use Roaming when the roaming flag is on, and Local otherwise". s110 sent a bare `get_app_dir` once, was refused, and landed the qualified symbol. s113 was refused twice on empty `words` |
| 118 | Terminologist | 10 `criteria.specify` | c_1 to c_5 landed. 4 twin refusals on c_6 and a repeat of c_4, 7 `ledger.log` refusals |
| 119 to 127 | Architect, Liaison | `batches.group` b_1; m32 clarify on k0; m35 touch page; r_m36; annotate | m36: "Line 7 is wrong because this change should only touch the utils module and the new test file". s127 cut the touch list to 3 grains |
| 128 | Developer | `code.write`, `code.commit` | 54173e6a landed on the first commit call. It removes `folder = os.path.expanduser("~")`. No removal-door refusal. A test-file write was refused: "tests/test_utils/test_get_app_dir.py is a test file, and the tests are the Tester's" |
| 129 | Tester | 10 `tests.encode` | 5 refused at the encode run: "The run of this body on the batch's head raises at line 18, ... `TypeError: get_app_dir() missing 1 required positional argume...`". The re-encode landed 5 tests |
| 130 to 134 | Developer, Tester | 2 `tick:tests_failing` challenges, m39 and m41; 2 rewrites | tst_c1 and tst_c2_win_local asserted `AppData/Roaming` with a forward slash against a Windows path. Each rewrite to v2 went green |
| 135, 136 | Critic, Architect | `verdicts.emit` pass; `findings.find` | b_1 merged |
| 137 to 159 | Liaison, Terminologist, Architect, Vision Keeper | m42 confirm, deliver, surveys, item `clear_screen_return`, m54, slicing | s144: 20 `model.amend` refusals in the survey. s148 landed challenge m49 |
| 160 to 168 | Terminologist, Architect, Liaison, Developer, Tester, Critic | criteria, b_2, m58, r_m59, commit d6c347c3, 2 tests, pass | s160: 5 twin and id refusals. s166: 3 test-file refusals, then 2 tests landed. b_2 merged |
| 169 to 186 | Liaison, Terminologist, Architect, Critic, Vision Keeper | m60 confirm, surveys, item `format_filename_example`, m69, slicing | m70: "Only the docstring changes and the code stays the same." s174: 20 `model.amend` refusals |
| 187 | Terminologist | `criteria.specify` c_1_format_filename_example, `msg.answer_tester` m73 | The criterion landed. 3 twin refusals on its own id. m73 woke a Tester before b_3 existed |
| 188 | Tester | 3 encodes, 3 retires, 4 reasks | "c_1_format_filename_example exists and belongs to no batch, and this session was not woken for one". 2 fault rows |
| 189 to 194 | Architect, Liaison | group b_3; annotate 6 grains; m74 touch page; r_m75; relay; annotate 5 grains | m75: "please remove the five formatting tests from what you expect to touch". r_m75 named one of the five |
| 195 | Developer | `code.write`, `code.commit` | 2d391b66 landed: the docstring example. 41 of 41 green |
| 196 to 230 | every seat | the stop, section 3 | b_3 stays `running`. The walk ends quiet after 70 steps |

(observed: `sessions`, the turns of each session, `receipts`, `messages`, `rulings`, the jsonl pages and words.)

## 2. The walls

A wall here is one of four signs from the brief. The counts are night totals. The first seq is the first session with the sign.

| # | Wall and sign | Count | First seq | Fact (question 4) |
|---|---|---|---|---|
| W1 | **The test-file door refuses every path the Tester sends for the docstring criterion, and the key quarantines.** The brief tells the Tester to use a path under `touch`, and every touch test path is a project test's file | 12 "is already inh_..'s file" refusals in s196, s197, s198 and s200; 10 of them repeats. 1 `::` path refusal, 2 unterminated bodies. Quarantine `tester|tick:tests_missing|b_3` at 3. The same door text 15 times on the night | s166 for the text; s196 in walk 3 | F35, the touch paths his words declined, with F31, a criterion about a docstring |
| W2 | **His "no new test is needed" reaches no row, and the quarantine never lifts.** m91, m97 and m103 say the check is the docstring. After m91, no criterion, test or tick row changes | 3 answers, 0 rows; the key is quarantined at the end | s215 | F20, the lift when the subject moves; F3 beside it |
| W3 | **The give-up ladder wakes four seats, and none lands a row on b_3.** s201's challenge text names a break that the runs do not show: inh_fe7f4bfc passed 7 of 7 runs | 4 ladder wakes, s201, s205, s210, s214; 0 receipts from them. s202 sent nothing and woke `tick:unresolved` s212 | s201 | F4 for s201's text; F16 for s202 to s212 |
| W4 | **A door's text makes the Liaison contest a criterion he did not fault.** "The words fault line 3, "can simply be" ... It takes no approve." r_m97 contests c_1, and s226 then tries to rewrite it as "does not require an example" | 1 ruling. 13 refusals in s226: 4 no surface, 2 unknown symbol, 4 `msg.answer_tester`, 3 `ledger.log`; 0 landed. m103: "I did not call it wrong" | s222 | F2 |
| W5 | **The Liaison's acts name fewer tests than he asked to remove, and the read-back shows the shortfall to him.** r_m75 names 1 of 5. s215's `acts` holds the key "3" twice, so r_m91 lands 3 of 4, two of them on read-back lines | 2 rulings; m90 line 5 and m96 line 9 misread him, and he corrected both | s192 | F3, with F35 |
| W6 | **The Liaison's `rulings.rule` is refused before it lands** | 29 refusals in 11 sessions: 8 read-back line, 5 "words fault line", 4 naming, 3 empty words, 3 "have no ruling", 2 acts key, 2 fields of a line's object, 1 act words, 1 two verdicts | s92 | F2 |
| W7 | **A Tester wakes on the Terminologist's answer before its batch exists**, as night 169's W3 | 1 session, 10 refusals, 2 fault rows | s188 | F25 |
| W8 | **The Terminologist re-sends a landed criterion with its own id and words** | 9 twin refusals in s118, s160 and s187, each 3 times; 1 fault row | s118 | F17 |
| W9 | **The Tester rewrites a right failure, as built.** The encode run refused 5 bodies that cannot pass, and the Tester re-sent them once unchanged | 5 refusals, 4 repeats | s129 | F14. The door held |
| W10 | **The survey Architect repeats `model.amend` on a subject another constraint governs** | 38 "already governs this subject" refusals in s144 and s174, 19 each; 27 "you have not read" refusals in s72 | s72 | none |
| W11 | **Seats repeat a call after "Your work here is done"** | 24 "already sent" or "every owner" refusals; 14 sessions ended on a verbatim repeat | s7 | none |
| W12 | **Onboarding repeats of reads and notes** | 65 `code.source` repeat refusals in 4 Vision Keeper sessions, 63 of them in s23 and s28; 74 `ledger.log` refusals in Vision Keeper sessions | s12 | none |
| W13 | **Argument form and id refusals that a seat repeated** | s211 `msg.relay_vision_keeper` 3, round_no as words; s209 `model.adopt` 3 on b_3; s200 `tests.encode` on tst_c1, a b_1 id | s200 | F19 for s211; F22 for s209 and s200 |
| W14 | **The constraint tick quarantines at onboarding.** s1's page call is refused 3 times on the ref 'tick: quarantined' | 1 key at 3; 5 refusals in s1 | s1 | F21 |
| W15 | **The pages after the stop say "check: none yet"** on the criterion whose tests the team gave up | m96, m102 | m96 | F21 |
| W16 | **Fault rows** | 4: s187 "This criterion duplicates c_1"; s188 twice "Cannot encode test without a valid batch"; s201 "broke an existing passing test (inh_fe7f4bfc)" | s187 | F17, F25, F25, F4 |
| W17 | **Sessions that end with no landed write and no message** | 21: onboarding s1, s30, s36, s92, s95, s105; W1 s113, s122, s132; W2 s150; W3 s188, s196, s197, s200, s202, s204, s209, s211, s213, s226, s230 | s1 | under the wall each belongs to |

(observed: the result lines of every turn, collected by `results.py` in this session's scratchpad; `receipts`; `faults`; `tick_attempts`; `test_run_journal` for inh_fe7f4bfc. A repeat is a call refused with the same text twice or more in one session: 274 such calls in 44 sessions, 24 of them in the walks.)

W1 and W2 stopped the walk. W3 to W5 ran inside the stop. W6 to W17 slowed walks and did not stop one (reasoned: walks 1 and 2 merged with W6 to W12 present).

## 3. The stop, question 1

**The criterion.** c_1_format_filename_example v1, landed by s187: "The docstring for format_filename must include an example demonstrating that when shorten=True, the path a/b/c.txt is displayed as c.txt." Its surface is `src/click/utils.py::format_filename` (observed: `criteria`). The wake of s196 says "without a test: c_1_format_filename_example" (observed: `sessions.wake_detail`).

**What he said about tests for this item**, in order (observed: the jsonl):

- m70, 11:23: "Only the docstring changes and the code stays the same."
- m75, 11:25: "Line 3 is wrong because only the docstring in the utils file changes, so please remove the five formatting tests from what you expect to touch."
- m86, 11:31: "one short example line in the docstring, with no change to the code. The list still names four formatting tests. Please remove them".
- m91, 11:32, on the stop page: "I want a fix, not to give up: only the docstring changes, so no new test is needed, and the check can simply be that the docstring shows the example."
- m97, 11:33: "please drop all three formatting tests ... the check on line 3 can simply be that the docstring shows the example."
- m103, 11:36: "I did not call it wrong, I only said its check can be that the docstring shows the example."

**What each seat did, from the first wake to the end.**

1. s196, s197, s198, Tester, `tick:tests_missing`. Each sent `tests.triage` with `verdict='encodable'`, 7 calls in all, and no other verdict (observed: `tool_calls`). The encodes went to `tests/test_formatting.py`, the file of the touch list, and then to `tests/test_utils/test_format_filename.py`. The door refused: "tests/test_formatting.py is already inh_6acc723a's file; two tests in one file overwrite each other on disk. Name this one for its own criterion -- tests/test_<what it checks>.py". It refused the other path the same way for inh_fe7f4bfc, and "path 'tests/test_formatting.py::test_truncating_docstring' is not a Python file". No Tester sent a new file name (observed). The Tester's brief says "A path under `touch` is the file the principal expects your tests in. Use it." (observed: s196's system prompt). At s196 the touch list still held four `tests/test_formatting.py` entries that m75 had declined (observed: s196's `batches.expect`).
2. s198 asked the Vision Keeper, m78. s199 answered with refs only, m79. s200 sent `tests.retire` on tst_c1, refused: "no ruling of the principal names tst_c1. Only his ruling that drops the check line retires a test." Its encodes were refused on `from src.click`, on the b_1 id tst_c1, and on the two taken files.
3. The key `tester|tick:tests_missing|b_3` reached 3 attempts and quarantined (observed: `tick_attempts`). The launcher printed the CYCLE line at "period 1, rounds 3".
4. s201, Developer, `tick:exhausted`, "the team could not write the tests after 3 attempts". Its challenge was refused: "inh_fe7f4bfc has no criterion: it is the project's own test and it passed before this batch. A challenge has no side there. Read code.diff and restore what your change broke". inh_fe7f4bfc passed 7 of 7 runs, and b_3 has 0 red runs (observed: `test_run_journal`). s201 sent `msg.escalate_architect` m80, a fault row, and m81 to the Vision Keeper.
5. s202, Architect, on m80. Three `msg.challenge_vision_keeper` calls were refused: "quotes= holds `assert click.format_filename("/x/\ufffd.txt", shorten=True) == "\ufffd.txt"`, and it is not a span of the live text of c_1_format_filename_example or of inh_fe7f4bfc." It sent nothing.
6. s204 and s213, Developer, on the answers m82 and m89. Each made no call: "The code already satisfies the criterion; no changes are needed." and "The test passes and the criterion is satisfied by the existing implementation."
7. s205, Architect, `tick:exhausted`: m83 to the Vision Keeper. s206 and s210, Vision Keeper: reports m84 and m88. s207, Liaison: clarify m85. s208 landed r_m86_2, `b_3` approve. s209, Architect: `model.adopt` refused 3 times, "'b_3' is not a row of model_areas". s211, Liaison: `msg.relay_vision_keeper` refused 3 times on its argument form.
8. s214, Liaison, `tick:quarantined`, "1 abandoned: tests_missing for b_3 (tester), 3 attempts": page m90, "The team stopped work on this change." Line 2 reads "check: none. The team gave up writing it after 3 tries."
9. s215 landed r_m91 on the fifth call. c_1 is approve, and three test paths carry `remove`. No act or row records "no new test is needed" (observed: `ruled_refs`). s217 cut the touch list to 4 grains.
10. s222 landed r_m97 with c_1 contest, after the door text of W4. s224 cut the touch list to `src/click/utils.py` alone. s226, Terminologist, landed nothing on c_1 (W4). s228 landed r_m103. s229 relayed line 6 to the Terminologist, and s230 made no call.

**What refused or gave up.** The test-file door at `tests.encode` refused 12 encodes (observed). The map tool places `tests.encode` at `tests_encode`, `rota/roles/api.py` 9159 (observed: `map mode tester/tests_missing`). The tick key gave up at 3 attempts, and the ladder's four wakes landed no row on b_3. After m91 nothing re-woke the Tester, and c_1 stayed with no test (observed: `tests`, `sessions` s215 to s230). Whether `tests_missing` reads a ruling that a criterion needs no test is not in the records.

## 4. The frames measured, question 3

| Frame | Ends-when measure | Night 168 | Night 169 | Night 170 | Moved |
|---|---|---|---|---|---|
| 339 | Developer sessions refused at the removal door after a grant, from 7 of 7 | not counted, the frame is younger | 7 of 7 | 0. No removal-door refusal in 3 Developer `batch_start` sessions. s128 removed line 518 with no grant and landed on its first commit | Yes, with no grant in the sample |
| 330 | Walks that end with a pending batch and a quarantined running one, from 2 of 3 | 2 of 3 | not reached, one batch only | 0 of 3. Walk 3 ends with b_3 quarantined and no pending batch. The ladder woke its rungs: `tick:exhausted` 3 seats, then `tick:quarantined` | Yes. The shape cannot occur on the last item (reasoned) |
| 324 | Criteria whose surface names `examples/` on `clear`, from 2 of 3; Architect sessions that repeat a bare symbol, from 7 | 0 of 2; repeats not read | not in the read | 0 of 2 on `clear`, 0 of 8 overall; 0 of 3 guess sessions repeat a bare symbol, s110 sent one once | Yes |
| 335 | Landed encodes that error at collection on an escape, from 6 of 7; quotes refused on `\\`, from 14 of 24 | 6 of 7; 21 quotes | not reached | 0 of 9 landed encodes; 0 quote refusals on `\\` in 2 landed challenges. tst_c1 v2 and tst_c2_win_local v2 hold a backslash and pass | Yes, night 1 of 3 |
| 336 | Pages whose check row shows a red with no error text, from 3 of 3 | 3 of 3 | not reached | not reached. The 3 red runs fell on b_1 after m35, and no page showed a check row while a run was red | No sample |
| 337 | Naming-door refusals on a line his earlier answer in the exchange names, from 2 of 2; rulings that approve a line he called wrong, from 1 | 2 of 2; 1 | first half not reached; 0 of 8 | First half not reached: 4 naming refusals, s93, s215 twice, s222, each on a page with one answer. Second half 0 of 14 walk rulings | Second half held at 0 |
| 338 | Relays of a ruled test row that end with no acting call, from 2 of 2 | 2 of 2 | not reached | not reached. No page held a test row | No sample |
| 333 | Each of three challenge channels reads its quote as a span of its row | not counted, the frame is younger | 0 challenges | A unit-test measure, not a night count. The night shows the Vision Keeper channel refusing 3 quotes as "not a span of the live text", s202 and s226 | n/a |
| 328 | First: a test on a batch with a head runs at encode, and a red goes back | Fired 6 times | not reached | Fired 5 times in s129, and the re-encode landed 5 tests | Held |
| 328 | Second: a challenge quote must be in the live text | Held | not reached | Held: m39 and m41 landed on live v1 texts; 0 respecify landed | Held |
| 328 | Third: Developer ticks on a test the Tester later rewrites, from 5 of 5 | 7, night 2 of 3 | 0, no sample | 2: s130 and s133. Both tests were wrong, and both v2 went green | Yes, 7 to 2 |
| 322 | Criteria a page reply calls wrong or unclear, from 3 of 7 on item 3 | 0 of 1 | not reached | 0 of 1 on item 3; 0 of 8 overall | Held at 0 |
| 315 | Batches that run with no criterion that holds his landed correction, from 1 of 5 | 0 of 1 | not in the read | 0 of 3 by criterion text. b_2's "keep what clear() prints" and b_3's "no new test is needed" are in no criterion | Held, with two words outside any criterion |
| 329 | Tickets with two criteria of one text, from 1 of 3 | 0 of 4 | 0 of 1 | 0 of 3. The twin door fired 9 times at `criteria.specify`. 0 respecify landed | Held at 0, a fourth night |

(observed: the stack blocks by `grep -n "^### <n>\. "`, the tables named in sections 0 to 3, `plans/night168-read.md` and `plans/night169-read.md` section 3.)

**Night 170 is night 1 of 3 for 330, 335, 337 and 339 on their reached halves**, and it gives no sample for 336 and 338 (reasoned: a clause whose case did not occur has no sample). Frame 328's third clause reads 2 on its third night, so it does not reach 0 (reasoned).

## 5. Placement, question 4

| Fact | Walls | Count of walls |
|---|---|---|
| F2, the page lines his words name | W4, W6 | 2 |
| F3, what his words ask of a target | W5, W2 beside | 2 |
| F4, the newest run of a test | W3 (s201), W16 (s201's fault) | 2 |
| F14, whether an assert can fail | W9 | 1 |
| F16, a reply that landed nothing | W3 (s202 to s212) | 1 |
| F17, the criteria a session holds now | W8, W16 (s187) | 2 |
| F19, the call text and call form | W13 (s211) | 1 |
| F20, a quarantined key and the lift | W2 | 1 |
| F21, a tick key in words | W14, W15 | 2 |
| F22, the table an id lives in | W13 (s209, s200) | 1 |
| F25, the calls a mode offers against the doors | W7, W16 (s188) | 2 |
| F31, what a criterion's prose is about | W1 | 1 |
| F35, the predicted files less the paths he declined | W1, W5 | 2 |
| none | W10, W11, W12 | 3 |

(reasoned: the sign of each wall against the Fact row of each F; no code was read for this table.) Code sites by the records: `tests.encode` at `tests_encode`, `rota/roles/api.py` 9159, for W1, by the map tool. The records name no other function.

## 6. The rulings seam, question 5

**Counts.** 21 `rulings` rows, all `landed` (observed: `rulings`). 97 `ruled_refs` rows. 12 carry an act: `remove` 7, `drop` 3, `keep` 1, `rewrite` 1. 85 carry none (observed: `ruled_refs` grouped by act). 47 `rulings.rule` calls, 29 refused (observed: `tool_calls`, the result lines).

**Every refusal text of `rulings.rule`**, with its sessions (observed: the result lines):

- 8, s103, s156, s164, s192, s215, s222, s228: "line N is his read-back line, and only his words confirm it. His reply does not say that line N is right, and it does not approve the whole page. Leave line N out of the ruling". N is 4 three times, 5 twice, 6, 7 and 8 once each.
- 5, s92 and s93 four times, s222 once: "The words fault line 1, "are fine". An approve keeps the line as it is, and his words reach nobody. Rule line 1 contest or revise, as the words say, and pass the words. It takes no approve." s222's text names line 3 and "can simply be".
- 4, s93, s215 twice, s222: "The words name lines 3, 5 and 6 and do not name line 4. A contest rests on the principal's words. Approve the lines the words do not name, or rule them as the words say." The line numbers differ by page.
- 3, s113 twice, s228: "a contest carries the principal's words to the row's owner, and words is empty. Pass the reply, whole".
- 3, s92 and s93: "lines 1, 2, 3, ... 17 have no ruling. Every line of the page takes one: the ask closes when the ruling lands. A line the reply does not contest is approve".
- 2, s164 and s215: "acts has the key '6', and rulings has no such key. Each key of acts is a key of rulings". s215's names '4'.
- 2, s138 and s228: "rulings.rule: `act`, `target`, `words` are fields of line 6's object, not lines of the page. Put them inside line 6: rulings.rule(rulings={... "6": {"verdict": "contest", "act": "drop", "target": "l_f6c70e12e3", "words": "drop line 6"}}, words="drop line 6")".
- 1, s92: "line 18: the act drop rests on 'Drop lines 18 to 28', and his words do not hold it. Copy the words of his reply that ask for the change, or leave the act out".
- 1, s164: "line 4: acts and rulings give two verdicts. Give the verdict in rulings only".

**Did the Liaison copy an example's form?**

- `keep` on an approve: yes in form. r_m59 lands b_2 `approve` with `keep`, `target_kind` row, words "keep what clear() prints exactly as it is now" (observed: `ruled_refs`). The brief's example for "keep" is a `revise` on a check, and its example for "the output stays exactly the same as today" is `add` (observed: s164's system prompt). The Liaison took the act from his word "keep" (reasoned). The landed act sits on line 4, the line number of the brief's keep example. Whether the number came from the example is not in the records.
- `drop` for a later request: no. No page asked which request goes first, and no ruling carries `later` (observed). r_m43 and r_m103 use `drop` on page lines that his words ask to drop, as the brief's "Drop line 5" example does. In s138 and s228 the first call put `act`, `target` and `words` flat in `rulings`. The refusal text then printed the nested form, and the next call copied it word for word (observed: s138 and s228 turns 1 and 2).
- `remove` on test paths: the Liaison used `target_kind` `source_line` for test files four times, where the brief's example for test files is `path` (observed: r_m75, r_m91; the brief's "`path` is a file of the guess"). r_m97 used `path` once. r_m103 line 8 carries `remove` with target "line 3", which is no target kind of the brief (observed).
- The landed acts name fewer targets than his words: r_m75 one of five tests, r_m91 three of four, because s215's `acts` held the key "3" twice (observed: s215's calls, W5).

## 7. Usage

One agent on Opus, no sub-agents, no probe of rota code beyond two map calls. About 260k tokens on the harness counter at the write, over the 150k cap. The bulk was the session dumps of walk 3 and the Liaison prompt reads. Not read: why the removal door did not fire on s128's commit; whether `tests_missing` can take a "no test needed" ruling; the cause of the `\ufffd` in s202's quote; the four failures that the launcher counts as "Rota itself failed".
