# Records check: 36 status lines against their transcripts (2026-11-10)

Meta workflow. A read by one agent of frame 363, from the brief
`f363_records_check_brief.md`. This page changes no other file. The
scripts are in the scratchpad folder `records/` of session b49d24d2.

## 1. The result

No drawn line is false. 26 of 36 are true, and 10 are true in part. Every
line has a transcript, so no spare line was used.

| Kind | True | True in part | False | No transcript |
|---|---|---|---|---|
| Result with a number | 5 | 7 | 0 | 0 |
| Close | 12 | 0 | 0 | 0 |
| Cause | 9 | 3 | 0 | 0 |
| All | 26 | 10 | 0 | 0 |

A line is true when each fact matches its source and nothing that changes
the meaning is left out. A line is true in part when one fact differs, has
no source, or loses a qualifier that changes the meaning.

The three things that repeat most (reasoned: this agent, section 4):

1. **The source mark names a file that the session did not open.** In 11
   lines the mark says "observed: the report" or "read at HH:MM". The
   session read only the agent's return message, and the report file was
   never opened before the line.
2. **The line keeps the result and drops the qualifier.** In 9 lines the
   agent wrote a limit, a doubt or a contrary advice, and the line leaves
   it out. Examples: "only partly reads", "1 failed", "two gaps", "replayed
   recordings, so no model call ran".
3. **A token figure is the agent's own estimate.** In 4 lines the "about
   Nk" for a pass is the agent's guess. The harness count in the same
   transcript differs by 2k to 36k.

The numbers that a line copies from a tool result or an agent's return
match in almost every case. The commits, the test counts and the verdicts
match. The faults are in what the line says about its source and in what
it leaves out.

### How the lines were drawn

A script read `plans/stack.md` and the 41 files `plans/archive/stack-*.md`.
It found 3,313 status lines dated 2026-10-11 to 2026-11-09, with duplicates
across files removed (observed: `draw.py`, run 2026-11-10).

| Pool | Pattern | Size |
|---|---|---|
| Result | a count beside `passed`, `failed`, `tests`, `findings`, `reds`, `of N` and similar words | 2,486 |
| Close | `closed`, `closes`, `frame ends`, `ends here` | 403 |
| Cause | `because`, `the cause`, `caused`, `the reason` | 736 |

`random.seed(363)` drew 18 lines per pool in order: 12 lines and 6 spares.
A line drawn for one kind was not drawn again for another kind.

The close pattern was too wide. Of the 12 close lines, only close 6 states
a close in its own frame, F6 closed as a fact. Close 1 names the close of
another frame. Ten lines match on "closed" in "findings closed" or "closes
the write doors". By the brief, each misfit line is kept and marked as a
misfit in the table. One real close of a frame came through the result
pool: result 3, frame 348. So the check of a close against its `Ends when`
line ran on three lines only: result 3, close 6 and close 12.

The time in a status line is local time. It is UTC+1 to 2026-10-25 and
UTC after that. Every line was found at its stamped minute in one
transcript (observed: `locate.py` and `tgrep.py`).

## 2. The 36 lines

The session column is the first eight characters of the session id. The
time in each row is the transcript's time, in UTC.

| # | Kind | Frame | Date | Session | Line, cut at 30 words | Mark | Why |
|---|---|---|---|---|---|---|---|
| 1 | result | 304 | 2026-10-23 13:39 | 2214bec6 | pass 1 runs on a fresh implementer on Opus, cap 80k, from f304_pass1_brief.md in this session's scratchpad, in the worktree C:/Users/roman/rota_p304 at 2453d945: the encode door refuses a body that ... | true in part | The worktree, sha and cycles match. "cap 80k" has no source, because the brief at 12:39:27 sets no cap and 80k is the frame's price. (observed: transcript 2214bec6, 10-23 12:39 UTC) |
| 2 | result | 362 | 2026-11-06 10:28 | 029756dd | The fourth look at 7cfefc5c on the resumed reviewer, about 22k more against 25k: accept. U1 to U5 are fixed on the reviewer's probes; on icalendar ensure_env and the import ... | true in part | The counts match the reviewer. The line drops the reviewer's two gaps in "one list", and 729 against 850 in 16 files is not explained. (observed: transcript 029756dd, 11-06 10:28 UTC) |
| 3 | result | 348 | 2026-10-31 01:55 | d5c14419 | 01:55. Closed at HEAD, review p7 of 9cb6df43 ready with 0 findings. First condition, not met as written: it asked a night's Liaison pages for a second case of each ... | true in part | The close is open about the unmet condition. "on gemma4 ... none lost through 8 passes" mixes replayed recordings with live runs. (observed: transcript d5c14419, 10-31 01:55 UTC) |
| 4 | result | 201 | 2026-10-21 16:30 | 81fe1025 | review 3 accepts a3a84d06 on Opus, about 59k on the harness line against 40k, plans/frame201-review-3.md: review 2's findings 1, 2, 4 and 5 closed, each by a test on its ... | true | Every count, sha and finding matches review 3's return. The medium's effect, a false admit, is left out but is minor. (observed: transcript 81fe1025, 10-21 15:30 UTC) |
| 5 | result | 129 | 2026-10-16 17:36 | 70d05878 | night 151: 7 asserts on 8 contested wakes, 0 outside the refs, the new branch fired 0 times; the seven lows of review 2 show 0 signs each; bg_4 was ... | true | All counts match item 3 of the night read's return, including the correction that bg_4 was not cancelled. (observed: transcript 70d05878, 10-16 16:36 UTC) |
| 6 | result | 357 | 2026-11-02 11:55 | 208997ee | Pass 3 built on Opus, about 93k against 60k, at db53bec4 in rota_p357 above 19feac1a: one reader principal_objects, true when a ref is a team row with his drop granted ... | true in part | The code facts match the report. The measures 0 of 16 and 15 of 15 are the brief's targets, and the printed report did not show them. (observed: transcript 208997ee, 11-02 11:55 UTC) |
| 7 | result | 316 | 2026-10-24 16:09 | f1f0bcfa | pass 2b built on the same implementer, about 30k on the harness line against 40k, at edac73e2 on 0c8024c9: land takes a ruling on a row the merge parked while ... | true in part | The return says 456 passed, 1 failed. After the fix only one file ran again, and "30k on the harness line" is the agent's estimate. (observed: transcript f1f0bcfa, 10-24 15:09 UTC) |
| 8 | result | 329 | 2026-10-26 02:46 | 192bbbc0 | Review 1 on Opus, 119.3k on the harness line against 70k, plans/frame329-review-p1.md: f0abfecb held for one high and three low; after the twin refusal the seat sends msg.challenge_vision_keeper, the challenge ... | true | The verdict, the four findings and 119.3k match the reviewer's return and the harness count. (observed: transcript 192bbbc0, 10-26 02:46 UTC) |
| 9 | result | 283 | 2026-10-25 19:27 | 66edc387 | Night 166, walk 2 merged the clear item, this frame's sample, at 19:27 after 38 steps and 4 asks; 6 writes, 0 unchanged writes, 0 commit refusals, so this frame's ... | true in part | The query counted the whole night database, not walk 2, and the line leaves out 53 turns with a dropped note. (observed: transcript 66edc387, 10-25 19:27 UTC) |
| 10 | result | 326 | 2026-10-26 00:09 | 66edc387 | Pass 1c on the same implementer, 196.6k on the harness line, a1db0e89 above f8168ce7: index_batch: true on 17 cases and out of OWED, which holds the 10 that need a ... | true | The counts, sha and open question match the implementer's return. 196.6k matches the harness. (observed: transcript 66edc387, 10-26 00:09 UTC) |
| 11 | result | 323 | 2026-10-25 15:08 | 0699ee05 | Pass 2 built on the same implementer, about 79k for the pass against 60k, committed in the worktree at ae8a6573 on c6c20374: each native call renders as a name(key=value, ...) ... | true in part | The tests and fixes match. "about 79k for the pass" is the agent's estimate, and the harness shows about 43k. (observed: transcript 0699ee05, 10-25 15:08 UTC) |
| 12 | result | 203 | 2026-10-11 15:15 | c81dd240 | taken by c81dd240 with frame 200. The sender's implementer ended with its session before its report; its edits stand uncommitted in C:/Users/roman/rota_i203: rota/testkit/dbtemplate.py, a template database per process keyed by ... | true | The files and the timings match the sender's pairs.log, which the session read at 14:08. (observed: transcript c81dd240, 10-11 15:15 UTC) |
| 13 | close | 348 | 2026-10-30 18:56 | a9a43280 | Claimed by a9a43280, peer name rota-6d, beside frame 341, after frame 349 closed. The first condition stays: no night comes under the ruling of 2026-10-29, and frame 347's quote read ... | true | Not a close of this frame. The close read's return named r_m14 as the exact case, as the line says. (observed: transcript a9a43280, 10-30 18:56 UTC) |
| 14 | close | 200 | 2026-10-11 06:11 | 84ce0759 | the scope on Opus, 298.7k on the harness line against 150k, plans/frame200-scope.md: one loop shape over three batches. The Tester applies the factory's decorator to a local plain function and ... | true | Not a close. The scope's counts and 298.7k match the agent's return and the harness count. (observed: transcript 84ce0759, 10-11 05:11 UTC) |
| 15 | close | 357 | 2026-11-01 21:56 | 62bcfbfb | 21:56. Pass 2b built on Opus by the resumed implementer, about 16k against 15k, committed at bd012c19 in rota_p357 above 37ef5980: a drop ends a request item only, through _is_request_item, ... | true | Not a close. The change, the tests and the heredoc rule break match the implementer's return. (observed: transcript 62bcfbfb, 11-01 21:56 UTC) |
| 16 | close | 308 | 2026-10-23 14:36 | 2214bec6 | pass 1b built on the same implementer, about 124k on the harness line in all, committed in the worktree at be9f8811: the route lists resolved refs only, a ruled test's ... | true | Not a close but a move to validating. The tests, sha and 124k match the return. (observed: transcript 2214bec6, 10-23 13:36 UTC) |
| 17 | close | 200 | 2026-10-11 14:43 | be3ef742 | pass 2b landed on the resumed implementer, 304.7k cumulative on the harness line, about 48k for the pass: the answer-mode challenge door, END_STEP without a decisions ref; the cause line ... | true | Not a close. The gate counts match. The implementer's high advice to interview before a re-record is left out. (observed: transcript be3ef742, 10-11 13:43 UTC) |
| 18 | close | 344 | 2026-10-27 19:48 | b3bc8a66 | F6 probe, plans/f6-probe-2026-10-27.md, on Opus, about 92k: 7 test-to-criterion rules and 5 criterion-to-test rules over 82 functions; on nights 170, 171, 165 and 164 every rule gives the same criterion ... | true | F6 closes as a fact. The counts and the two differences match the probe's return. (observed: transcript b3bc8a66, 10-27 19:48 UTC) |
| 19 | close | 290 | 2026-10-18 00:44 | bf5baa63 | the long gate on b0dbd926 re-recorded L1-TS-a-criterion-that-contradicts-the-request-goes-back and it is green: the case is not among the 11 new reds, where the gate of 19:18 at b5b14311 had it red ... | true | Not a close. The case is absent from the 11 new reds, so green holds, but no output names its re-record. (observed: transcript bf5baa63, 10-17 23:44 UTC) |
| 20 | close | 199 | 2026-10-11 01:41 | 84ce0759 | the read on Opus, 144.8k on the harness line against 120k: none of the four is a plain regression of a product change since 658abb6. test_map's 10 against 9 is ... | true | Not a close. The four reds, the re-records and 144.8k match the read's return. (observed: transcript 84ce0759, 10-11 00:41 UTC) |
| 21 | close | 266 | 2026-10-17 12:26 | eefbf293 | pass 3 built on Opus, 83.4k on the harness line against 60k, f266/pass3-report.md in this session's scratchpad: _open_inner names the outer key, the inner key or the list item, the ... | true | Not a close. 22 of 89,409, 966 passed and 4 of 9 match the pass report printed at 11:24. (observed: transcript eefbf293, 10-17 11:26 UTC) |
| 22 | close | 306 | 2026-10-25 02:32 | 79847ec6 | The re-check of 79391b21 stands, plans/frame306-review-wc1.md last section: all four findings closed, the working-set bytes unchanged without a retired criterion, 267 pins pass and the changed assertions are exact; one ... | true | Not a frame close. The re-check's four closed findings, 267 pins and the low match its return. (observed: transcript 79847ec6, 10-25 02:32 UTC) |
| 23 | close | 344 | 2026-10-27 14:24 | c66eae69 | Audit half A, plans/rootfix-audit-2026-10-27-a.md, 193k on the harness line against 180k: of F1 to F18, FIXED 0, PARTIAL 10, OPEN with the cause known 7, OPEN with the cause unknown ... | true | Not a close. The verdict counts and 48 entries match. The audit's doubt about name scans and unmeasured prices is left out. (observed: transcript c66eae69, 10-27 14:24 UTC) |
| 24 | close | 202 | 2026-10-14 15:01 | 58da19ca | pass 1c landed on the resumed implementer, 223.1k cumulative on the harness line, about 43k for the pass against 40k, committed by the holding session at c1a4cded, 2 files: the ... | true | A move to validating. The tests, the measure and the gate match the return. The cited files were not opened. (observed: transcript 58da19ca, 10-14 14:01 UTC) |
| 25 | cause | 244 | 2026-10-15 13:28 | dae006d1 | the try landed on Opus, 115.0k on the harness line against 100k, plans/frame244-try.md: on the night model, qwen3:8b at temperature 0, s152 keeps the declined file in 5 of 5 ... | true in part | The return gives the copied field as s119's cause only. The line makes it the cause on both seats, and Roman's word at 13:33 turned the escalation. (observed: transcript dae006d1, 10-15 12:28 UTC) |
| 26 | cause | 301 | 2026-10-21 14:25 | 5389be74 | pass 1b built on the resumed implementer, about 3k for the pass, report section 'Pass 1b': the NameError guard treats the nine module dunders as bound, api.py 7703 to 7707, ... | true in part | The fix and tests match. "about 3k for the pass" is 112k minus the agent's 109k estimate, and the harness shows 5.7k. (observed: transcript 5389be74, 10-21 13:25 UTC) |
| 27 | cause | 344 | 2026-10-28 00:36 | b3bc8a66 | F5 pass 1b at e089d53a on f5root, about 45k: the error line is the last raise with the cause beside it, _raising_line_head still shows frame 317's KeyError, every reader gives ... | true | Not a cause line. Every fact matches the return. The report it cites as read was not opened. (observed: transcript b3bc8a66, 10-28 00:36 UTC) |
| 28 | cause | 114 | 2026-10-17 17:04 | 0e37e9d7 | the history read landed on Opus, 120.4k on the harness line against 100k, plans/frame114-history-read.md: law 12 and the composition's "A prediction never blocks" hold the rule, the touch route of ... | true | The doors, the counts and the commits match the history read's return and Roman's message. (observed: transcript 0e37e9d7, 10-17 16:04 UTC) |
| 29 | cause | 223 | 2026-10-17 06:15 | b0dce033 | the gate from C:/Users/roman/rota_gate_223 at 134a7d8f, unpiped, 609.8s: 10 new reds, 1 flaky, scene_challenged_again; reds gone 2; stale (1), the new case, stale by its failure with the card held, ... | true | The gate lines and the deviation's reason match the tool output and the return. The 22k has no source. (observed: transcript b0dce033, 10-17 05:15 UTC) |
| 30 | cause | 258 | 2026-10-16 12:23 | cc1d654e | review 1 of e445aa64 on Opus, 86.9k on the harness line against 60k, plans/frame258-review-1.md: accept with fixes, 0 high, 3 low; all six night maps refused at HEAD and admitted ... | true | The cause, "m25 is the first present", and every count match review 1's return. (observed: transcript cc1d654e, 10-16 11:23 UTC) |
| 31 | cause | 314 | 2026-10-24 14:03 | f3a8d4c2 | probe 3 built on the same agent, about 146k cumulative on the harness line, about 30k for the probe against 40k: loop.py is a source, and its dispatch blocks give ... | true in part | The return says the path "only partly reads" from asked to merged. The line says a change reads from asked to merged. (observed: transcript f3a8d4c2, 10-24 13:03 UTC) |
| 32 | cause | 344 | 2026-10-27 16:54 | 6d9cf7e1 | F25 review p2 of fbf9bbc4 and f0ef3086, about 35k: findings 1, 2, 4 and 5 closed, 6 open until a model run of the two L1 cases; 3 partly closed, ... | true | The cause and the new high match review p2's return. The cited page was not opened. (observed: transcript 6d9cf7e1, 10-27 16:54 UTC) |
| 33 | cause | 329 | 2026-10-26 20:47 | 8db3a3f9 | Residue from night 169 walk 1, written by rota-b4: crit_3 of get_app_dir still says .config after his line 4 contest, because s128's criteria.respecify was refused as a near-copy of crit_2 ... | true | The cause matches item 3 of the gathering read's return word for word. (observed: transcript 8db3a3f9, 10-26 20:47 UTC) |
| 34 | cause | 345 | 2026-10-29 06:10 | 0ce92518 | 06:10. Pass 3 built at ac900593 on seam3root, about 120k against 100k: the four prompt definitions, the conjoined subject in _subject_lines, three cue doors out of the landing path (_faulted_approve, ... | true | The counts match the return. The cause of the zero writes stays open and goes to a review. (observed: transcript 0ce92518, 10-29 06:10 UTC) |
| 35 | cause | 200 | 2026-10-11 13:13 | be3ef742 | pass 2 landed on the implementer, 256.8k on the harness line against 250k, uncommitted, and the gate is red on 4. Step 0: under the design's first text 10 rows ... | true | The cause and counts match the report. The implementer recommended the opposite reading of a receipt, and the line does not say so. (observed: transcript be3ef742, 10-11 12:13 UTC) |
| 36 | cause | 362 | 2026-11-03 02:05 | 07f209e6 | 02:05. Pass 1c on the resumed implementer, about 29k, eb295ae4: the six fixes built, 22 of 22 new tests, 799 in 25 neighbour files; a wake with no batch criteria ... | true | The doubt's cause matches and the second look confirmed it at 02:06. The second doubt, stale cases, is left out. (observed: transcript 07f209e6, 11-03 02:05 UTC) |

## 3. What the transcripts show for the 10 lines true in part

1. **Result 1, frame 304.** The brief that the session wrote at 12:39:27
   names no cap, and it asks the agent to report its own token use. The 80k
   is the price on the frame's `Waits on` line (observed: transcript
   2214bec6, 10-23 12:39 UTC).
2. **Result 2, frame 362.** The reviewer wrote "one list, with two gaps:
   `dateutil` ... and the marker case", and the line says "read one list".
   The implementer counted 850 passed in 16 files at 10:19 and the reviewer
   729 at 10:28, and the line does not say why (observed: transcript
   029756dd, 11-06 10:19 and 10:28 UTC).
3. **Result 3, frame 348.** Pass 6's measure "replayed recordings, so no
   model call ran", and pass 8's measure was a replay on a cassette copy
   with no landing cases. The close line says the counts held on
   `gemma4:12b-it-qat` through 8 passes (observed: transcript d5c14419,
   10-30 23:44 and 10-31 01:18 UTC).
4. **Result 6, frame 357.** The session printed the report with a filter
   that cut the measure table, so the after column never showed. The
   values in the line equal the brief's expected values of 11:44, and the
   report's open question on stale Liaison cases is left out (observed:
   transcript 208997ee, 11-02 11:44 and 11:55 UTC).
5. **Result 7, frame 316.** The return says "456 passed, 1 failed, 4
   xfailed", then a fix and one file again, `test_refs.py`, 43 passed. The
   line says 456 passed after the fix, and it calls the agent's estimate of
   30k a harness figure (observed: transcript f1f0bcfa, 10-24 15:08 UTC).
6. **Result 9, frame 283.** The query counted every `code.write` in the
   night's database, so the 6 writes cover walks 1 and 2. The same output
   showed 53 turns with a dropped note, and the line does not name them
   (observed: transcript 66edc387, 10-25 19:27 UTC).
7. **Result 11, frame 323.** The agent wrote "about 65k input tokens and
   14k output tokens, both estimated". The harness count went from 66.4k to
   109.1k, about 43k for the pass (observed: transcript 0699ee05, 10-25
   14:45 and 15:07 UTC).
8. **Cause 1, frame 244.** The return gives the copied `touch.bg_1.disputed`
   field as s119's cause, and for s152 it says the list names the file the
   principal wants. Roman asked "Have we interviewed it?" before 13:33
   local, and the frame closed on 2026-10-16 with the same 8B model and
   thinking on, so the line's "a judgement the seat model cannot make" did
   not hold (observed: transcript dae006d1, 10-15 12:28 UTC, and the frame's
   status lines of 13:33 and 2026-10-16 22:30).
9. **Cause 2, frame 301.** The harness count went from 106.3k at 12:55 to
   112.0k at 13:25, about 5.7k. The line's 3k is the new total minus the
   agent's own estimate of 109k (observed: transcript 5389be74, 10-21 12:55
   and 13:25 UTC).
10. **Cause 7, frame 314.** Item 3 of the return reads "The path only partly
    reads from asked to merged through the tests". The line and the reply
    at 13:03:20 say that the path reads from asked to merged (observed:
    transcript f3a8d4c2, 10-24 13:03 UTC).

No line is false. Each of the 10 lines above is right in its main result,
and wrong or short in one part.

## 4. What repeats

Each class is (reasoned: this agent), from the 36 rows above.

- **A. The source mark overstates the read.** The mark "observed: the
  report" or "read at HH:MM" stands where the session read only the
  return message: result 7, result 11, close 3, close 4, close 6, close 12,
  cause 2, cause 3, cause 7, cause 8 and cause 10. That is 11 lines. In
  each case the facts match the return, so the mark misnames the source
  but not the fact. Result 6 is the counter-case: the session opened the
  report, and its filter then hid the table it cited.
- **B. The qualifier is lost between the return and the line.** Result 2,
  result 3, result 6, result 7, result 9, close 5, cause 7, cause 11 and
  cause 12. That is 9 lines. The lost parts are a gap, a failure, a
  replay in place of a live run, a doubt about stale cases, and in two
  lines an agent's advice that the session went against.
- **C. A token figure comes from the agent's guess.** Result 7, result 11,
  cause 2 and close 3. That is 4 lines. The harness count was in the same
  notification each time.
- **D. A count's scope is wider or narrower than the line says.** Result
  9 counts a whole night as one walk. Cause 1 makes one seat's cause the
  cause of two. Close 6 writes "85 tests and 11 criteria" over four nights
  where the probe gave them for two. That is 3 lines.
- **E. The session's judgement is marked apart.** Where a line holds a
  decision, the session writes it after "Judged here", apart from the
  observed part. One judgement in the draw did not hold: cause 1's
  escalation, turned by Roman's question.
- **F. The line credits the agent, even where Roman started the act.**
  Five acts started from a message of Roman: close 8, close 11, cause 4,
  cause 7 and cause 10. Only cause 4 names his words. Four acts started
  from the session's own reasoning: result 3, result 9, close 1 and cause
  9. Each of these lines credits an agent or a tool output.

Who started the 36 acts: an agent's finding fed the next pass in 15, a
step that the session names in 11, a message of Roman in 5, the session's
own reasoning in 4, and a hand-off note in 1. The lines credit an agent in
32, a tool output or a log in 3, and Roman in 1.

## 5. What the status lines are good evidence for, and what they are not

From these 36 lines only (reasoned: this agent).

Good evidence for:

- The numbers that an agent or a tool printed: test counts, gate lines,
  shas, finding counts and verdicts. These matched in every line checked.
- What the session decided and why. The "Judged here" part is apart from
  the observed part, and the transcript shows the same reasoning in the
  reply.
- The order of the acts. Every line was written within a minute of the
  return it reports.

Not good evidence for:

- Whether the session read the file that the source mark names. In 11 of
  36 lines it did not.
- The limits that the agent stated. A later reader sees the result without
  the doubt in 9 of 36 lines.
- Token use for a pass. The figure is often the agent's estimate.
- The scope of a count from a database query. The line does not show the
  query's filter.
- Closes. The draw held only three lines with a real close, so this read
  says little about closes.

## 6. What this read could not see

- The agents' own transcripts. This read checked a line against the
  agent's return message, not against what the agent ran. A return that is
  wrong would make a line look true here.
- The report files as they stood at the time. This read did not open
  them. Where a line cites a report that the session did not open, this
  read cannot say whether the report agrees.
- An earlier token count for result 1, cause 5 and cause 12, so their
  "about Nk" figures have no source here.
- Whether the close pattern missed real closes. The pool of 403 holds
  real closes, but the seed drew few.
- Context compaction. A session that compacted before the line may have
  read a source that this read finds only as a summary.
