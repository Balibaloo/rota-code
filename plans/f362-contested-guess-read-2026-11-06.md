# Frame 362, a read before any fix: he calls the team's guess wrong, and the batch still starts on it, 2026-11-06

Scratch directory: `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/029756dd-9273-4a54-95d8-2da05a2bfe52/scratchpad/guess_read/` (below: `GR`). The run's database is `dry6b.db` at `immutable=1` (below: the run). Finished 09:58 (observed: `date`).

## Result

- **His correction stopped at the Architect's guess relay, s145, before any Developer woke.** s145 woke in mode `guess` on m29, read `string.py` and `test_icalendar.py`, wrote the end line "guessed folds_long_lines_in_icalendar" twice, and never called `batches.guess` (observed: s145 `turns.completion` 1 and 2, `tool_calls` 1 to 7). The commit marked m29 `answered`, because a relay owes no reply (observed: `messages` m29; `rota/core/db.py` 1505 to 1528, `OWED_A_REPLY` and the comment "a relay ... carry information, so the wake answers them").
- **The guess was made again about 43 s of model time later (reasoned: section 1) from the Architect's own sign-off guess, and from no words of his.** The annotate seat s150 got `the item's guess` from `runner._guess_seed`, which reads the newest `touch_guesses` set. That set was still the sign-off set with `ruling_id` '' (observed: `touch_guesses`, 6 rows, all `ruling_id` ''; s150 first `turns.user`). s150 copied it into `batch_touch` verbatim (observed: s150 `batches.annotate` call, receipts).
- **No predicate or door reads the landed contest after the relay.** The `guess` predicate sees a set at the item's version. `batch_start` never reads a contest. `disputed_paths` drops a path only on an `exclude` act, and the Liaison keyed `rewrite` on line 2 and `add` on line 1 (observed: `predicates.py` 320 to 343, `scheduler.tick_batch_start`, `runner.py` 2111 to 2125, `ruled_refs` of `r_m27`).
- **The touch set is the lever, not the words.** FIXED, the wake of s152 with his whole reply and the touch set and bound block of his files, built by the code's builders: 3 of 3 first replies open `string.py` first. The same reply is byte for byte the recorded first reply of s173 (observed: `GR/raw/FIXED_0*.txt`, md5, compare with `turns.completion` of s173 seq 1). One extra call, OLD's 65-character words with the fixed touch set, also opens `string.py` (observed: `GR/raw/OLDFIX_01.txt`). NEW, with his whole reply and the old touch set, opened `property.py` 10 of 10 (observed: `f362-push-measure-2026-11-06.md`).
- **Reach: 5 replies contested a guess line on dry runs 3 to 6c and night 166. In 4 the Architect wrote a new set, and the next batch start read it. In 1, m27, it did not, and three Developers started on the old guess.** 6 more replies contested or revised a touch line, and every one with file words was rewritten by `batches.annotate` (observed: `GR/reach.py`, `GR/reach.json`).
- **No open frame holds this cause.** Frame 320 is the nearest mechanism, on a new request and not on a relay (observed: `plans/stack.md` headings, frame 320's Ends-when). The wall guide places it under cause 8, "A prose answer is called answered", and cause 12, two records of one fact (reasoned: section 6).

The rule for every project (reasoned: section 8): a landed contest on the code line is an owed write, not an answered message. Until the code line's record rests on that ruling, the item gets no batch prediction and no batch start.

## 1. The path of the contested guess, from m27 to the wake of s152

Times: the turn log gives 06:08:17 for the run start and 06:17:12 for its end (observed: `dry6b/t6.log`). Sessions carry no clock. Each time below is the run start plus the model time of the sessions before it, so each is a lower bound (reasoned: the sum of `turns.ms` is 288 s against 533 s of wall time).

| # | Time, at or after | Row | Function | What happened to his correction |
|---|---|---|---|---|
| 1 | 06:08:17 | `messages` m27, his reply to page m26 | `rota sign` | 3 sentences: "Line 2 is wrong. The fold is _foldline in src/icalendar/parser/string.py, and its tests are in src/icalendar/tests/test_icalendar.py. Do not touch parameter.py or property.py." (observed) |
| 2 | 06:08:17 | `rulings` r_m27, `per_item` `{"guess:...": "contest", item: approve, l_50364e0e61: approve}`; `ruled_refs` rr_841b13920355 line 2 `contest` `rewrite` "Line 2 is wrong."; rr_a5d98837ad02 line 1 `approve` `add` "Do not touch parameter.py or property.py." | s143 Liaison, `rulings.rule`, `api.menu_ruling` | The contest landed on `guess:folds_long_lines_in_icalendar`. No row has the act `exclude`, so no path is disputed (observed: `ruled_refs`; reasoned: `disputed_paths` reads `exclude` only) |
| 3 | 06:08:22 | m28 verdict, m29 relay to the Architect, refs `guess:...`; `config` `entry:m28` holds his whole reply; `guess_target:m28` is `[1, ""]` | s144 Liaison, `msg.relay_architect`, the `GUESS_RELAY` split in `sandbox.py` | The relay carried his whole reply (observed: s145 first `turns.user`, `principal_said`) |
| 4 | 06:08:24 | s145, mode `guess` | `runner._mode_key` through `scheduler.guess_relay`; `runner.resolve_inbound` 2356 to 2378 | The inbound showed `guess` with the 6 old grains and `disputed: []` (observed). Turn 1 sent 4 reads of `string.py` and `test_icalendar.py` and the end line "guessed folds_long_lines_in_icalendar" in the same reply. Turn 2, 26,696 characters, sent the end line again and no call (observed: s145 turns) |
| 5 | about 06:08:44 | m29 `status` `answered`, `unresolved_note` null; 0 `touch_guesses` rows under m28 | `db.session_commit`, `_owes_a_reply` | **His correction stopped here.** A relay is not in `OWED_A_REPLY`, so a session that wrote nothing still answered it (observed: the code at `db.py` 1505 to 1528 and 2044 to 2062; `messages` m29) |
| 6 | 06:08:44 to 06:09:00 | m30 to the Vision Keeper, s146 to s148, s149 writes `batches` b_1 | `predicates.guess`, `predicates.grouping` | `guess` stays false, because a set exists at `item_ver` 1 (observed: `predicates.py` 336 to 337). The ticket, the criteria and the batch form on the item (observed: receipts) |
| 7 | 06:09:07 | s150, `tick:annotate`, pushed key `the item's guess`; `batch_touch` b_1, 4 paths and 2 symbols of `property.py` and its tests | `predicates.annotate`, `runner._guess_seed` 4262 to 4286, `api.batches_annotate` | **The guess was made again here.** The seed was the newest set by rowid, the sign-off set with `ruling_id` '', so the key carried no "the principal said" (observed: s150 first `turns.user`, line 45). `annotate.md` line 6 tells the seat that this key is "what the principal corrected" (observed). s150 read `property.py` and sent the seed back whole (observed: s150 `tool_calls` 7, 8, 15) |
| 8 | 06:09:11 | s151, `tick:touch_note`, "expected 4, possible 2"; page m31, line 5 "expected to touch src/icalendar/parser/property.py" | `predicates.touch_note` | The page went to him. `batch_start` does not wait on it, "Non-blocking by R7" (observed: the docstring at `predicates.py` 1059 to 1066, `t6.log`) |
| 9 | 06:09:20 | s152, `tick:batch_start`, refs b_1 | `scheduler.tick_batch_start`; `api.batches_expect` through `lifecycle.predicted_rows`; `api.bound_constraints` through `_bound_rows` | `batches.expect` read "expected to touch" `property.py` and its 3 tests, and "might touch" two `property.py` symbols. The bound block read `cw_985d42272f1e` and four `property.py` symbols. `predicted_rows` dropped nothing, because `disputed_paths` found no `exclude` (observed: s152 first `turns.user`; the builders reproduce both lines byte for byte, `GR/build_fixed.py`) |
| 10 | 06:09:51, 06:09:59 | s155, s156 | the same | The same touch set. s156 wrote `property.py` whole and the door refused it (observed: `tool_calls`; `dry6c-read-2026-11-06.md`) |

The earlier reads saw step 4 and not steps 5 and 7. `dry6c-read-2026-11-06.md`, wall 4, says "s145 ... read `string.py` and `test_icalendar.py` and then emitted no call" (observed). The wall 2 read and the push read followed the words, not the touch set (observed: their sections 1).

## 2. The design: what must happen when he contests a guess line

Frame 298 built the guess line and its contest (observed: `plans/frame298-design.md`, its title "the Architect owns the scope guess at sign-off, and the Liaison relays its correction"). The ruling it builds (observed: the design, lines 12 to 14): "Remove the mechanical guess, the architect owns the guess", and "The Liaison relays, the Architect rewrites" (ruled: Roman, 2026-10-18 about 12:05, in the terminal).

The commits (observed: `git log`):

- `7ec9b940`, 2026-10-18 13:06, "the Architect writes a scope guess per request before sign-off, as touch_guesses rows with their own op, predicate and mode".
- `30c4a121`, 2026-10-18 13:33, "a correction of the scope guess relays to the Architect".
- `1869cab4`, 15:04, the stamp of the guess on the page. `f9f5cd19`, 15:26, the guess brief "decides its one call first".

What the code and the briefs do on a contest of the guess line (observed: the design 3.4 and 4.1, and the code):

1. **The record.** `land` keeps the `guess:<item>` key with contest or revise, and writes no `items` row (design 3.2). The row is `ruled_refs` line 2 `contest`.
2. **The seat.** The Liaison relays to the Architect. `guess_relay` keys the mode `guess` (`runner.py` 405 to 414). The inbound holds `principal_said`, `guess` and `disputed` (`resolve_inbound`).
3. **The write.** `guess.md`: "Start from the paths the words name ... Drop every path of `guess` the words call wrong. Then stop. After the call, end the session with one line: "guessed <item>."" `batches.guess` writes a new set with `ruling_id` set to the verdict (`api.py`, `batches_guess`).
4. **The seed.** `annotate` reads the newest set through `_guess_seed`, with his words when the set rests on a ruling (design 1.3).
5. **The predicate.** `guess` fires only when no set exists at the item's version (design 4.1). An amended item fires it again. A contest does not.
6. **The gate on a batch start.** None. Design 4.3: "**Nothing new** (copied: P4, "Non-blocking by R7"; reasoned: a prediction never blocks)". Design 3.4 point 9: "No new predicate ... the touch note ... shows the batch's plan that started from the corrected guess (1.3). R7 holds." Design 4.2: "Relay loop. One ruling makes one relay. The principal's replies bound the loop."

So the design holds one assumption with no check: the relay session writes the set (reasoned: point 9 says the plan "started from the corrected guess", and nothing makes it so). The loop cap of 4.2 covers `tick:guess` only. A relay that writes nothing leaves no state true (observed: 4.2; `_owes_a_reply`).

R7 is a ruling on his reaction, not on the team's work. P4 says "Non-blocking by R7: nothing waits on the principal's reaction" (observed: `plans/archive/p4-scope-disclosure.md` 5 to 6, ruled R16/R17, 2026-09-03). After m27 his reaction exists. What is missing is the team's owed write (reasoned). The "a prediction never blocks" part is the design session's reasoning, not words of his (observed: design 4.3 marks it "reasoned").

The batch relay has a form the guess relay lacks. `_files_contest_block` puts his words in a block under the touch list with "Leave them out." (observed: `runner.py` 953 to 997). Frame 244's try 2 measured it: "moved s152 in 5 of 5 and s119 in 3 of 5" (observed: the docstring). The block needs `touch` in the inbound, so a guess relay never gets it (observed: line 975). s171, with that block, sent `batches.annotate` with his two files in its first reply (observed: s171 `turns.completion` 1).

## 3. What changed by s173

The touch set changed in turn 7 (observed: `t7.log`, 06:19:08 to 06:35:07). He answered the touch page m31 with m39, the same three sentences with "Line 5" (observed: `messages` m39). r_m39 landed `b_1` `contest` `rewrite` on line 5 (observed: `ruled_refs`). The Liaison s168 relayed m45 to the Architect. `batch_relay` keyed the mode `annotate` (observed: `runner.py` 413 to 414). s171 called `batches.annotate(batch_id="b_1", paths=["src/icalendar/parser/string.py", "src/icalendar/tests/test_icalendar.py"], new_files=[])` in its first reply (observed: s171 completion 1, receipts `batch_touch:b_1:*`). s172 did the same on m46, the relay of r_m41 (observed). So he had to say it twice, on two pages, before the record moved (observed: the two rulings).

The Developer after the change: s173, the only Developer session after s171 (observed: `sessions` s173 to s195). Its prompt said "expected to touch" `string.py` and `test_icalendar.py`, with no "might touch" (observed). What it did (observed: s173 `tool_calls` and `turns`):

1. Turn 1: `code.probe` `string.py`, `code.source` `string.py` 0 to 400, `code.source` `test_icalendar.py` 0 to 100.
2. Turns 2 to 4: more reads of `string.py`, lines 289 to 600 and 118 to 156.
3. Turn 5: `criteria.load`, `model.load(ids=['b_1'])`, `glossary.lookup('fold')`, then `code.write` of a new `_foldline` at `string.py` 118 to 156, `code.write` of `test_icalendar.py` 0 to 100, and `code.commit`.
4. The door refused the test write: "end=100 falls inside IcalendarTestCase (lines 16 to 296 ...)". The session ended at turn 6.

No commit landed. `batches.head_commit` is the base `99619246`, every `test_runs` row is at that commit, and the worktree holds no change in `string.py` (observed: `batches`, `test_runs`, `git status` in the b_1 worktree). Why the `string.py` write left no trace is not read (reasoned: a refused call in the same reply, or the discard at the park, both unproven). After s173 the batch went to the Tester, who quarantined at `tests_missing` (observed: `dry6c-read-2026-11-06.md`, row 8).

## 4. The bound constraint `cw_985d42272f1e`

- **What it is.** A stated commitment of the code, observed from source: party `parser`, behaviour "actual backslash escapes per :rfc:`5545`, not URL encoding. This preserves", witness `src/icalendar/parser/property.py` line 32 (observed: `constraints`, `provenance` `observed`/`code`). It has one binding, the path `src/icalendar/parser/property.py` (observed: `constraint_bindings`). Its ledger row is `parked` under the lazy election (observed: `l_fefb0d6297`).
- **Why the wake names `property.py`.** `bound_constraints` reads the files of `predicted_rows` and of the diff, and returns the constraints that bind them (observed: `api.py` 4750 to 4800). The touch set held `property.py`, so the constraint on `property.py` came with it (reasoned: the function).
- **Should a contested guess retire it?** No. The constraint is a true fact about `property.py`, and other batches can touch that file (reasoned: law "every record has one writer", and the row's writer is the survey). Only its push follows the touch set, and it follows by itself. With the fixed touch set the builder gives `cw_41b4cb28dda6`, `cw_6a232f4ea912` and `cw_99502ef494ad`, the three `_foldline` and 75-octet rows, byte for byte the block s173 got (observed: `GR/build_fixed.py`, compare with s173 first `turns.user`). So the fix is in the touch set, and the bound block needs no change (reasoned).

## 5. The reach

Databases: dry 3 and dry 4 in `.rota`, dry 5 and dry 6b/6c at `immutable=1`, a copy of dry 6a and of night 166, the night that the push read names (observed: `GR/reach.py`). Night 148 and 149 of frame 244 were not opened. A reply counts when its landed ruling keys a `guess:<item>` line or a batch line `contest` or `revise` (reasoned).

### 5.1 The guess line

| Run | Reply | His words name files | The relay's seat | New set written | Next batch start | It read |
|---|---|---|---|---|---|---|
| dry 5 | m37 | `string.py`, `test_icalendar.py`; not `parameter.py`, `property.py` | s199, `guess` | yes, `batches.guess`, set `m38` | s207 | the new set: `string.py`, `test_icalendar.py` |
| dry 6b | m27 | the same words | s145, `guess` | **no call** | s152, s155, s156 | **the old set**: `property.py` and 3 tests |
| night 166 | m28 | "only the utils file in click" | s113 | yes, set `m29` | s131, bg_1 | the new set: `utils.py` |
| night 166 | m53 | `termui.py`, `test_termui.py`; not `utils.py` | s153 | yes, set `m54` | s164, bg_2 | the new set |
| night 166 | m69 | "the docstring of the function itself, not in a test file" | s182 | yes, set `m70` | s195, bg_3 | the new set: `utils.py` |

(observed: `GR/reach.json`, `touch_guesses`, first `turns.user` of each start.)

So 4 of 5 contests moved the guess, and 1 of 5 started a batch on the guess he called wrong (observed). Dry run 5's m37 and dry 6b's m27 are the same words, the same model `qwen3:8b`, temperature 0, and the same brief hash `87ce7e0d59c62de8` (observed: `sessions`). s199 sent `batches.guess` in its first reply on a 6,245-character prompt. s145 sent reads first on a 9,781-character prompt, whose `the index's test files` key is 4,314 characters against 1 (observed). Which difference turned the seat is not measured (reasoned: one sample each).

### 5.2 The touch line

| Run | Reply | Verdict | His words name files | Seat | Rewritten | Next start read |
|---|---|---|---|---|---|---|
| dry 4 | m50 | revise | no | no relay | no | s199, the old set, with nothing to change |
| dry 4 | m58 | contest | `string.py`; not `parameter.py`, `property.py` | s205, `annotate` | yes | s206, the new set with `string.py` |
| dry 5 | m73 | contest | functions, no file | s265, `annotate` | yes | no later start |
| dry 6b | m39, m41 | contest | the m27 words | s171, s172, `annotate` | yes | s173, the new set |
| dry 6b | m40 | revise | no | no relay | no | s173 |

(observed: `GR/reach.json`.) Dry runs 3 and 6a hold none (observed).

In all, 11 replies contest or revise a guess or a touch line. 7 name files or code. 6 of the 7 rewrote the record in one relay, and the 7th is m27 (observed: the two tables). Every relay with a written set or touch set led to a start that read it (observed). This also settles the wall 2 read's open point. Dry 5's s207 got the same two words as s152, `["Do not touch parameter.py or property.py.", "Line 2 is wrong."]`, and wrote code, because its touch set was `string.py` (observed: wall 2 read section 1 and `GR/reach.json`).

## 6. The match against what is open

- `plans/stack.md` headings for "guess", "touch", "annotate", "predict", "contest", "relay", "seam" (observed: grep): 315, 322, 264, 268, 271, 276, 289, 291, 249, 188, 185, 167, 168. None names a relay session that writes nothing, or a batch start on a contested guess (observed: the headings and the Ends-when lines of 271, 299 and 320).
- Frame 271, "The re-annotate after a files contest leaves out the file he asked to add": the annotate route, after a write. Not this cause (observed: its heading).
- Frame 299, "A reply that faults both the files and the request's text loses its files words": the landing of the words. Here the words landed on the code line (observed: its Ends-when; `ruled_refs`).
- Frame 320, "A fresh request whose Liaison session lands nothing is marked answered": the same mechanism on another verb. Its Ends-when: "a new request whose session lands nothing stays open with its refusal as a note, wakes once more, and on the second miss reaches him". `_request_missed` covers a request with no `cause_id` only (observed: `db.py` 1586 to 1600). So frame 320 holds the pattern and not this cause (reasoned).
- Frame 322 is the criteria wake. The "guess-fired seam" is a survey seam in `plans/design-onboarding-deep-dive-2026-11-03.md`: "The guess-fired seam does not exist (section 4)". Both are near in name and not this cause (observed: line 151 of that page; the heading of 322).
- Frame 362, the onboarding frame, holds the push of `86ca7e23` and the bound push of door 2. Its Ends-when is the onboarding demand and supply, not the guess (observed: its block). This read was briefed under it.
- `plans/wall-guide.md`: cause 8, "A door's predicate is not its fact", lists "A prose answer is called answered" (observed: lines 461 to 463). The commit read s145's end line as an answer to m29. Cause 12, "Two records of one fact disagree, and no rule reconciles them": the landed contest on `guess:<item>` and the `touch_guesses` set disagree, and `_guess_seed` reads only the set (reasoned).

So no open frame holds this cause. It is a new frame, or a pass of frame 362 if the build session places it there (reasoned).

## 7. The measurement

The server was the 3080's Ollama 0.33.3 at `127.0.0.1:11434`, with no model loaded before the first call (observed: `/api/ps`, `/api/version`). The model and the options are the run's, from s152's `pins_json`: `qwen3.5:9b`, `think` false, temperature 0, `num_ctx` 16384, `num_predict` 8192, no tools (observed: `push_measure/call.py`). The pins hold `seed` null. Ollama takes `options.seed`, so the three calls carried seeds 1, 2 and 3 (observed: `GR/call_fixed.py`). 4 calls of the 6 allowed, in the foreground, one after another (observed).

### 7.1 How FIXED was built

`GR/build_fixed.py`, read only (observed):

1. Copy the rows of `dry6b/w7/dry6b.db`, the database as turn 7 started, at `immutable=1`, into an in-memory database. At that point `batch_touch` b_1 holds the 6 old grains, and s171 has not run (observed).
2. Run the code's builders at the checkout HEAD `6b40123a`: `api.batches_expect(ctx, "b_1")`, `api.bound_constraints(ctx, "b_1")`, `runner.bound_key`, and `runner._render(..., PUSH_CHARS)`. The builders did not change between the run's `3b209833` and HEAD (observed: `git diff`, no hunk in those functions or in `lifecycle.py`).
3. Check: on the unchanged copy, the builders give the `[batches.expect]` line, 18,223 characters, and the bound line, 1,113 characters, of NEW byte for byte (observed).
4. Change in memory one thing only: delete b_1's `batch_touch` rows, and insert `src/icalendar/parser/string.py` and `src/icalendar/tests/test_icalendar.py`, kind `path`, confidence `expected`. That is the set s171 wrote (observed).
5. Rebuild the two lines and put them in NEW at the same places. Nothing else changes. His whole reply and the legend of `86ca7e23` stay first (observed: `GR/fixed_diff.txt`).

The changes, NEW to FIXED (observed): "expected to touch" `property.py` and 3 tests becomes `string.py` and `test_icalendar.py`. "might touch" two `property.py` symbols becomes `[]`. The bound block `cw_985d42272f1e` and four `property.py` symbols becomes `cw_41b4cb28dda6`, `cw_6a232f4ea912` and `cw_99502ef494ad`, the `_foldline` rows of `test_icalendar.py`, `test_parsing.py` and `string.py`. The "tests" list is the same. The prompt goes from 21,227 to 21,112 characters. `property.py` goes from 7 to 2 mentions, his words and `test_issue_720_uid_property.py`. `string.py` goes from 2 to 5. Both the expect line and the bound line equal s173's recorded lines (observed).

### 7.2 The replies

| Prompt | Calls | First call | Opens `string.py` first | Source |
|---|---|---|---|---|
| OLD, recorded | 10 | `code.probe` `property.py` | 0 of 10 | `push_measure/raw/OLD_*` |
| NEW, his whole reply first | 10 | `code.probe` `property.py` | 0 of 10 | `push_measure/raw/NEW_*` |
| **FIXED, NEW with his files in the touch set** | **3** | **`code.probe` `string.py`** | **3 of 3** | `GR/raw/FIXED_01` to `03` |
| OLDFIX, OLD's 65 characters with his files in the touch set | 1 | `code.probe` `string.py` | 1 of 1 | `GR/raw/OLDFIX_01` |

(observed.) The FIXED reply, 215 characters, 72 tokens, `done_reason` stop: `code.probe(pattern='src/icalendar/parser/string.py')`, `code.source` `string.py` 0 to 400, `code.source` `test_icalendar.py` 0 to 100. The 3 replies are one reply, byte for byte, and equal s173's recorded first reply (observed: md5, the compare). So at temperature 0 the seeds did not vary the reply, and the 3 calls are one sample (reasoned). OLDFIX adds a read of `test_parsing.py` (observed). OLDFIX is beyond the three calls the brief named and inside its cap of 6 (observed).

What the measurement shows: with the touch set of his files, the first reply goes to his file, with his whole reply or with 2 of his 3 sentences. With the old touch set it does not, with either (observed: the four rows). What it cannot show: a whole session, or that the write in `string.py` lands (reasoned: s173 had this first reply and committed nothing, section 3).

## 8. The reading, in five lines

1. A principal's contest of a code-line record is an owed write, and the seat's session does not answer it until that write exists (reasoned: `OWED_A_REPLY` lacks `relay`, the s145 path).
2. A record that he contested and nobody rewrote is a stale record, and no reader may seed from it as though he approved it (reasoned: `_guess_seed` and `annotate.md` line 6).
3. A batch prediction and a batch start gate on that fact: no start while the newest landed contest on the item's code line has no record written under it (reasoned: composition, "Only a fact or a ruling gates"; R7 governs waits on his reaction, and here his reaction already exists).
4. The unanswered contest climbs as frame 320's shape does: one more wake of the owner, then one line to him that says the team did not rewrite what he corrected (reasoned: law 6 in `db.py`, frame 320's Ends-when).
5. Measure it on the touch set, not on the words: the words reached every Developer, and only the record moved the seat (observed: section 7, 4 of 4 with his files and 0 of 20 without).

The measurement for a fix (reasoned): rebuild dry 6b's turn 6 on a copy, with s145's recorded reply, and count the starts on b_1 that read his files; today 0 of 3, and 4 of 4 on the other guess contests.

## 9. What is unproven

- Why s145 sent reads and not the call, when s199 sent the call on the same words (reasoned: one sample each, two prompts that differ in their test-file list).
- Why s173's `string.py` write left no trace in the worktree (section 3).
- That a gate on the batch start does not cross R7. P4's ruling text is "nothing waits on the principal's reaction", and the gate waits on the team (observed: P4). Design 4.3's "a prediction never blocks" is a design session's reasoning (observed). A build session that reads R7 more widely asks Roman first, with the ruling, its date and the departure (reasoned: the memory "provenance before a fix").
- The 5 times of section 1 are lower bounds (reasoned).

## 10. Usage

One Opus reader. All run databases were opened with `immutable=1`, or as a read-only copy for dry 6a and night 166. 4 model calls, about 15 s of card time (observed: `wall_s`). No suite, no gate, no rota run. The repository changed by this page only. The scripts are in `GR`: `db.py`, `s1.py` to `s6.py`, `reach.py`, `build_fixed.py`, `call_fixed.py`, `call_oldfix.py`, with `fixed_user.txt`, `oldfix_user.txt`, `fixed_diff.txt` and `raw/`.
