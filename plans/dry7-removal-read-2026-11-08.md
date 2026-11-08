# Frame 362, dry run 7, wall 1: his words on the removal reached no Developer push. The read, 2026-11-08

A read by `plans/method/reference.md` C76 step 3, from the brief `f362_removal_read_brief.md`. The read names the records and proposes. The session judges.

## Result

His words stopped at the Liaison's reading. The reading put "Do not remove that branch in _foldline" on no `ruled_refs` row. It put `approve` on `b1` with the words "Keep everything else as before.", and it relayed only to the owners of tests and criteria (observed: `ruled_refs` of `r_m42`, `messages` m44 to m48). The whole reply stays in `rulings.words` and `messages.body_text` of m42. The one push that shows his whole reply on a batch, `START_RULED_KEY`, fires on `tick:batch_start` only (observed: `rota_dry7/rota/core/runner.py` 4691 to 4705). The 3 `batch_start` sessions, s154 to s156, ran before m42 (observed: `sessions`). So 0 of 22 Developer sessions after `r_m42` landed carry his words, and 0 of 4 Architect `touch_strayed` sessions carry them (observed: `turns`, a search for "Do not remove" over every turn).

His words were not the only thing that the Developer lacked. The Architect's note told every Developer session the same thing, and every commit message of the 19 `touch_mistaken` sessions says "Restore" or "No changes needed" (observed: `tool_calls`). Two things stopped the restore. The first is the base text: `batches.expect` with 162 `inh_` rows filled 18,450 characters of the 20,000-character push, so `code.diff` and its `[removed lines]` block were cut (observed: s191's first push, "CUT your wake: 23,814 of 42,814 characters are not shown"; `runner.py` 1188 `PUSH_CHARS = 20000`). s191 wrote "I don't have the exact removed lines in my current view" (observed: s191 turn 11). The second is the model's text. The sessions that had the base text in hand concluded "the file is already in the correct state" and wrote nothing (observed: s193, s201, s203).

| Question | Answer | Source |
|---|---|---|
| A | His answer wrote `rulings` r_m42, 23 `ruled_refs` rows, messages m42 and m44, and the relays m46 to m48. The Developer push reads `batches.expect`, whose "the principal said" holds the request only | `rulings`, `ruled_refs`, `messages`, s191 push |
| B | `START_RULED_KEY` is frame 312's, 6785f35b4 of 2026-10-24, for the stopped page's promise on the start window. The stray note in the push is F7's, 001860090 of 2026-10-28, for night 172's s263 that read "Refs: bg_3" only | `git log -S`, the commit bodies |
| C | Not a contest. The removal line has no ref and no line number, and the reading put `approve` on `b1` | `principal.py` 2922 to 2934, `ruled_refs` |
| D | 8 commits by 7 sessions. One session, s204, came within one line of the base. Doors refused spans; the cut took the base text; the model then said nothing was owed; the attempt cap quarantined the key | `receipts`, `touch_strays`, `turns` |
| E | Whole reply in a Developer mode: 1 of 10 modes. His answer on a running batch reaches the acting seat's next fix wake: 0 of 4 page kinds | `runner.py`, `prompts/developer/*.tools` |
| F | Widen the gate of `START_RULED_KEY` to every Developer wake and the Architect's `touch_strayed` wake, about 2 cycles, no design page. The base-text cut is a second place, about 2 cycles. A keyed removal line is a design page | reasoned |

## 1. Question A: the path of his words

1. The seat signed m29 at the start of turn 6, not in turn 5 (observed: `t6.log` line 4, "== sign m29", "reply sent: m42"). The CLI wrote m42, `principal` to `liaison`, verb `converse`, with his whole words in `body_text` (observed: `messages`).
2. The Liaison s179, turn 6, read the reply in one call: `rulings.rule` with lines 1 to 15 (observed: `tool_calls` and `turns.completion` of s179). The page m29 numbers 15 lines. The removal line, "The change removes code that no answer of yours allowed: in _foldline, the branch ...", has no number (observed: `t5.log` lines 79 to 101).
3. The ruling r_m42 has `status` `landed` and `verdict_id` m44. Its `per_item` holds `"b1": "approve"`. Its 23 `ruled_refs` rows carry 4 sentences of his reply: "Keep everything else as before." on 9 approve rows, the `q_split` sentence on 4 rewrite rows, and "Lines 8, 10 and 11 are not my request." on 3 drop rows, each twice with the `landed` rows. "Do not remove that branch in _foldline." is on 0 rows. The `b1` row reads `approve`, act none, words "Keep everything else as before." (observed: `ruled_refs`, `ruling_id = 'r_m42'`).
4. The Liaison s181 woke on the verdict m44, whose refs are 5 test rows and 3 criteria. It relayed to the Vision Keeper (m46 from m43, and the tests) and to the Terminologist (m47, refs `c_1`, `c_2`, `c_3`, `c2`, `c3`) (observed: `messages`, `tool_calls` of s181). No relay went to the Architect from m44, and the Liaison's modes hold no relay to the Developer (observed: `rota_dry7/rota/roles/prompts/liaison/*.tools`, 8 relay lines, none to the Developer).
5. His words then reached the Terminologist s184 and the Tester s185 (observed: the search, 4 and 11 turns). On m56 the same holds: s212, s214, s215, s216 (observed).
6. The read-back on m51, line 9, says what the team read: "line 5 is wrong: rewrite; line 7 is wrong: rewrite; ... 6 lines approved". It names no removal (observed: `t6.log` line 409).

On m56, r_m56's `b1` row carries the whole reply in `words`, with "Do not remove the lines of _foldline that handle an escape." at its end, and the verdict `approve` (observed: `ruled_refs` `rr_fe0ba7a92133`). So on the second answer the words are on the `b1` row, and still no Developer push reads that row.

**What a Developer push reads, by file and line in `rota_dry7/rota/`:**

- `core/runner.py` 4691 to 4705: `_ruled_block(conn, api.batch_ruled_refs(conn, bid))`, under the key "the principal's words on this change, newest last". Condition: `role == "developer" and wake.kind == "tick:batch_start"`. It shows each whole reply on the batch, its tickets, its criteria, its item and `guess:<item>` (observed: `runner.py` 4436 to 4480, `roles/api.py` 27717 to 27727).
- `core/runner.py` 4676 to 4687: `_contest_block` after `criteria.load`, Developer and Tester, any wake. It reads contests on criteria only (`contests_on`, `runner.py` 848 to 863). An approve on `b1` never shows here.
- `core/runner.py` 1067 to 1072 with 498 to 507: `_mistake_rows`, the Architect's `mistake` rows at the head with their notes, on `tick:touch_mistaken`. This is the line that carried the Architect's note.
- `roles/api.py` `batches_expect`, its "the principal said" field. In every push of the 19 sessions it held the request text only (observed: s191, s201, s210, s220, s221).
- The commit door: `_ruling_texts` and `_unruled_gone`, `roles/api.py` 27692 to 27757. It reads his words through `ruled_words` and his grants through `granted(..., "remove", ...)`. It sends the Developer "[removals note] no criterion, request or ruling of the principal asks for this removal" (observed: s191 turn 13, s204 turn 6). It does not push his words.

**Where his words stopped:** at the reading of s179. The record there says that his words were for the tests on lines 5, 7, 9, 12 and the criteria on lines 8, 10, 11, and that `b1` is approved (observed: `ruled_refs`, `per_item`).

`D:/repos/rota` at head: the gate is unchanged at `runner.py` 4709, `_mistake_rows` is at 508, `removal_line` at `principal.py` 2995. The 3 rota commits after `dbd8d920` are frame 360's and touch none of these (observed: `git log dbd8d920..HEAD -- rota`).

## 2. Question B: the purpose and the provenance

**The stray note path.** `predicates.touch_strayed` and `touch_mistaken` came with cf067ce46 of 2026-09-13, "the committed diff is checked against the prediction, and the Architect judges the strays", for clickI night 32, where `echo_json` merged in two files outside the touch set (observed: `predicates.py` 2662 to 2712 docstring, `git log -S`). The case is a path that strayed from a prediction, law 12, "the touch set is a prediction, never a permission". Frame 339 added the removed line to the note (observed: the docstring). The note in the Developer's wake body came with 001860090 of 2026-10-28, F7 review p3b finding 8: the notes left the cycle key, and "the runner now prints each mistake row at the batch head with its note in the wake body, so the seat still reads the row it acts on" (observed: the commit body). The case was night 172's s263, which read "Refs: bg_3" only (observed: `runner.py` 1068 to 1071).

**The removal line on his page.** `removal_line`, `principal.py` 2922 to 2934, came with F7, 11d04b18f of 2026-10-27, for night 171's s164, which removed the macOS branch and the XDG return of `get_app_dir` while the Architect judged them foreseen (observed: the docstring). Its docstring says "The line is information, not a gate ... it names no row and no key" (observed). So the page asks nothing of him on that line, by design.

**The carrier of his words.** `START_RULED_KEY` came with 6785f35b4 of 2026-10-24, frame 312: "The stopped page says that his answer starts the team once more and that the team reads his words. The re-check of review w5 found that no push of the Developer's batch_start window held them" (observed: the commit body). Frame 362 moved it to the front after dry run 6b's cut, and made it show whole replies (observed: `runner.py` 4699 to 4704, the status of 2026-11-06 06:58). The case was a stopped batch that restarts on `batch_start`. In dry run 7 no `batch_start` followed his answer: after m42 and after m56 the next Developer wakes were `touch_mistaken` (observed: `sessions`).

**Did the build meet its own case?** The stopped page m51 says "The team stopped work on this change", and frame 312's promise is that his answer reaches the team. On this run the answer went to the Liaison's reading and the stray wake ran first. So the promise held for a start, and the build did not test a stopped batch whose next wake is a fix wake (reasoned).

## 3. Question C: a contest under the design?

No. The design of `plans/design-contested-record-2026-11-06.md` says: "A contest or revise of his on ref X, with ruling V, stays owed until a row of X's owner rests on V" (observed: Result). Three facts make his line no contest.

1. The removal line has no ref and no line number. `removal_line` "names no row and no key" (observed: `principal.py` 2928 to 2932, `t5.log` line 80). So the Liaison had no ref to put a contest on.
2. The reading put `approve` on `b1` (observed: `ruled_refs`). The nearest kind in the design's table is kind 2, the batch line `b_<n>`, owned by the Architect through `batch_touch` (observed: section 1, row 2). A contest there asks the Architect for a new touch set, not the Developer for the base lines.
3. The removed code is in no table. The owner lookup is the single-writer law (`sandbox.py` 963 to 985), and the Developer writes code, not a ruled row. The design's section 3 records "A batch-line contest on a running batch" as "No change in slice 1. Recorded as open" (observed).

The record holds a form for his line, and nothing writes it: `ruled_refs.act` allows `keep` and `target_kind` allows `source_line`, and 0 rows of the run use either (observed: `ruled_refs`, a group by act and kind: 35 none, 3 add, 6 drop, 14 rewrite). The removal door reads only a `remove` grant (`api.py` 27707). So a `keep` on a source line would be read by no door today (reasoned).

## 4. Question D: the Developer's 19 sessions

The 19 sessions are s191, s193 to s197, s201 to s204, s206, s207, s209, s210, s217 to s221 (observed: `sessions.wake_kind`). s217 to s219 have 1 turn each and `committed` 0. Every one of the other 16 got the same first push shape: the wake line with the Architect's note, then `[batches.expect]` at 18,450 characters, then "CUT your wake" (observed: the first `turns.user` of each; 25 of the 35 Developer first pushes of the run are cut).

| Commit | Session | What the push said about the stray | What it read and wrote | What the doors refused | The stray rows after |
|---|---|---|---|---|---|
| 2d20cc90 | s191 | the `if` line at 140 and "should be preserved" | read 118 to 200 of the head four times; wrote `text=''` twice, then the whole `_foldline` | span door 3 times: "end=165 falls inside expression", "crosses from one block to another" | 7 statements removed, `mistake` (s192) |
| aba4c0a2 | s195 | the 7 statements of s192's note | read the head; wrote `_foldline` whole twice | 1 kind of write refusal | 7 statements, `mistake` |
| 40778404 | s196 | the same | wrote `_foldline` whole once | none | 7 statements, `mistake` |
| c85fe55f | s202 | the same | wrote 138 to 165 five times, then `_foldline` whole | 4 kinds of write refusal | 7 statements, `mistake` |
| 3d20a228 | s204 | the same | wrote `_foldline` whole | 2 kinds of write refusal | only the `if` at 140 removed, `open`: the closest to the base |
| 17ed55ce | s204 | the same, in the same session | wrote 118 to 196 | | 7 statements and `foldline = deprecate_for_version_8(_foldline)` at 158, `mistake` |
| 49e0fc1a | s207 | the 7 statements and the alias | wrote 158 to 160 `text=''`, then `_foldline` whole | 1 kind | the same two rows, `mistake` |
| 21bbe661 | s209 | the 7 statements | wrote `_foldline` whole and the alias line 4 times | 1 kind | 7 statements, `mistake` |

Sources: `receipts` for the session of each commit, `touch_strays` for the rows, `tool_calls` and `turns.user` for the reads, the writes and the refusals (observed). The write refusals are counted as distinct `ERROR code.write` texts in the session.

**Did any session try to restore the removed statements?** Yes, 2 sessions wrote the removed statements by name. s203 sent the 6 statement texts at lines 141 to 149, and the span door refused: "start=141 falls inside if (lines 139 to 158 ...)". The line numbers of the note are the base's, and the head had moved (observed: s203 turn 2). s203 then wrote "The file currently contains the correct code ... no changes are needed" (observed: s203 turn 6). s204's first commit, 3d20a228, put back the 7 statements and left out the `if` at 140 (observed: `touch_strays`). Its next write in the same session removed them again (observed: 17ed55ce).

**What the base text was.** Only `code.diff` shows the base lines, in `[removed lines]`, and the push cut it in every session (observed: 0 of the 16 first pushes hold "[removed lines]"). 8 sessions asked for it by name later: s191, s193, s195, s196, s201, s202, s207, s210 hold the block in some turn (observed: a count over `turns.user`). In s193 the block holds 10 lines, the 1501 comment and the 7 statements, and not the `if` line at 140 (observed: s193 turn 5). `api.py` 22246 says the block holds "the removed lines that no added line of the same file carries" (observed). Whether an added line carries the `if` text: not read.

**What stopped it, in one sentence:** the push lost the base text to the cut, the span door refused the writes at the base's line numbers, the sessions that then held the base text wrote "no changes are needed", and the attempt cap of 3 quarantined `developer|tick:touch_mistaken|b1` (observed: `tick_attempts`, `turns`).

**The register case `L1-DV-put-back-a-removed-block`** (`tests/rota/cases/l1_touch.yaml` lines 101 to 300). It asks the Developer, woken on `touch_mistaken` with one `mistake` row, to write back two base lines of `format_filename`, graded by `write_includes`. Its fixture is one function in one file, with no inherited tests and no ruling of his (observed). So the case measures the same act, the restore from the base, and its push is never cut. This run's pushes asked the same act and gave the Developer neither the base text nor his words. The case's own comment says "The wake now pushes `code.diff`, so `[removed lines]` shows the base body" (observed: line 107). On icalendar that is not true past 162 inherited rows (reasoned).

## 5. Question E: the reach

**Readers of his words into a seat's push, in `rota_dry7/rota/core/runner.py`: 12.**

| # | Place | Seat and wake | What it carries | Reaches the acting seat of a running batch |
|---|---|---|---|---|
| 1 | 4691 to 4705, `START_RULED_KEY` | Developer, `batch_start` | each whole reply on the batch's refs | at the start only |
| 2 | 4676 to 4687, `_contest_block` | Developer and Tester, any wake with `criteria.load` | contests on criteria | only a criterion contest, and only when the push is not cut |
| 3 | 1067 to 1072, `_mistake_rows` | Developer, `touch_mistaken` | the Architect's note, not his words | no |
| 4 | 1112 to 1114, `_relay_contest_block` | Terminologist, relay | contests on criteria | not the Developer |
| 5 | 1100, `_files_contest_block` | relay recipient, a touch-list contest | his words on the touch list | the Architect, on a contest of the batch line |
| 6 | 2246 to 2249, `entry_for(trigger)` | any seat woken by a relay | `principal_said` | not the Developer: no relay goes to it |
| 7 | 2770 to 2781, the owed guess | Architect, `tick:guess` | `principal_said` | before a batch |
| 8 | 4818, `_item_ruled` | Terminologist, `tick:criteria` | his words on the item | not the Developer |
| 9 | 4909 to 4919, `_item_ruled` | Vision Keeper, `tick:slicing` | the same | not the Developer |
| 10 | 595, `_last_word_lines` | `tick:criterion_repair` | last ruling per criterion | not the Developer |
| 11 | 640 to 652, the repair contest block | repair wake | contests on rows | not the Developer |
| 12 | 2477 to 2480, `prior_answers` | Liaison | earlier answers | not an acting seat |

The seats that act on a running batch's code are the Developer, which writes, and the Architect, which judges each stray on `touch_strayed` (reasoned: `predicates.py` 2662 to 2712). Of the 12 places, 1 gives the Developer his whole reply, and on its start wake only. 0 give the Architect his words on `touch_strayed` (observed: s190, s192, s205, s208, 0 turns with "Do not remove").

**Developer modes:** 10 (`answer`, `batch_start`, `challenge`, `exhausted`, `finding_violated`, `findings_exhausted`, `reopen`, `tests_failing`, `touch_mistaken`, `verdict_failed`), all with `criteria.load` in their `.tools` (observed: `prompts/developer/`). His whole reply reaches **1 of 10** (place 1).

**Page kinds on which he answers about a batch: 4.** Touch (m29, refs `b1`), stopped (m51, m61, refs `b1`), clarify (m40, refs `b1`, `tk_1`), park (`m_park_12fb7720e8_b1`, refs not read) (observed: `messages.body_refs`). Each ruling lands on `b1` or its criteria, so place 1 would show it. On a running batch, the next Developer wake is a fix wake. His answer reaches the acting seat's next wake as words on **0 of 4** kinds, and as a criterion contest on 4 of 4 only when his line names a criterion line (reasoned). In this run: **0 of 22** Developer sessions after `r_m42` landed, and **0 of 4** Architect stray judgements (observed).

**The second gap, the cut of the base text:** 25 of 35 Developer first pushes are cut, and 0 of the 16 `touch_mistaken` first pushes that ran hold `[removed lines]` (observed). Older frames match by symptom: 127, "The fix wake's red rows carry whole test bodies, and the cut then removes the source", and 134, "A large diff block removes the source from the Developer's fix wake" (observed: `plans/stack.md` headings 3391 and 3351). Their state is not read.

## 6. Question F: proposal

1. **F1, his words to the acting seats.** Change the condition at `runner.py` 4691 to 4694 from `wake.kind == "tick:batch_start"` to every Developer wake that names a batch, through `wake.refs[0]` or `sb.ctx.batch_id`. Add the Architect's `tick:touch_strayed` wake on the same refs. The block, the key, the cap `RULED_CHARS` and the front position stay. This covers 10 of 10 Developer modes and the stray judge, and 4 of 4 page kinds, because each ruling lands on `batch_ruled_refs`. Price: about 2 cycles, a pass and a review (reasoned). It changes no mode text and no door. It adds an existing block to more wakes. So by C76 3b no design page is needed, and the session judges whether "a prompt's shape" covers a push block.
2. **F2, the base text in the restore wake.** On `touch_mistaken`, put `code.diff`'s `[removed lines]` before `batches.expect`, or show `batches.expect` without the `inh_` rows on that wake. F1 alone puts about 600 more characters at the front and cuts more of the rest (reasoned: m42 is 252 characters, the dry run 7 read count 9, and m56 is of the same order, not counted). Price: about 2 cycles. Reach: 25 of 35 cut pushes. Match frames 127 and 134 first, by C76 step 2. No design page.
3. **F3, a keyed removal line.** Give the removal line on his page a ref and a line, so that "Do not remove" lands as `keep` on a `source_line` target, and so that the removal door and the stray judge read a `keep`. This changes the page form, the ruling vocabulary in use and a door family. **A design page comes first** (C76 3b), and the contested record design's open row, "a batch-line contest on a running batch", is its seed.

**The measure.**

- The red test from this run's rows (F1): copy `copies/w6.db` to a temporary file. w6 is the database before turn 7: `r_m42` is `landed`, `b1` is `running` at 21bbe661, and 21bbe661 has a `mistake` row (observed). `w5.db` holds no answer of his, because m29 was signed after the copy (observed: `t6.log` lines 2 to 5). Build the Developer push for `Wake("developer", "tick:touch_mistaken", refs=("b1",))` with the runner's push assembly, `runner.py` about 4640 to 4705. Assert that the text holds "Do not remove that branch in _foldline". It fails today at the `batch_start` gate (reasoned). A second assertion on the same copy for the Architect's `touch_strayed` wake.
- For F2 on the same copy: assert that "[removed lines]" stands before "CUT your wake" in the `touch_mistaken` push.
- The next dry run: Developer pushes after a landed answer on a running batch that carry his words, from 0 of 22 to all. `mistake` stray rows at the quarantine, from 10 to 0. A head whose `_foldline` holds the 1501 branch.

## 7. Question G: doubt

- One run, one batch, one model, qwen3:8b, one removal. Every count in sections 4 and 5 rests on that one sample.
- His words may not move the Developer. The Architect's note said the same as his line, and 16 of 16 sessions that ran wrote "Restore" or "no changes needed" (observed). So F1 may move the push count and not the restore. A replay of s191 or s203 with his words at the front and the base block uncut, by the C33 interview, would show which input moves the seat. A night where the Architect judges a removal `foreseen` while he said keep, as night 171's W4, is where F1 alone decides the outcome (reasoned).
- The 8 sessions that held `[removed lines]` still wrote nothing or wrote the head's body. So F2 may not be enough without a door that compares the head with the base statements (F7's proposal in `plans/rootfix-audit-2026-10-27-a.md`).
- The base block of s193 lacks the `if` at 140. If an added line carries that text, the block hides the branch head by its own rule, and s204's 3d20a228 shows the cost (reasoned, not read).
- The brief puts the m29 answer in turn 5. It was signed in turn 6 (observed).

## Not read

- The park page's refs and its ruling.
- Whether an added line at the head carries the `if` text of line 140.
- The full turns of s194, s195, s196, s206, s209, s210, s220 and s221, beyond the tool calls and the counts.
- The state of frames 127, 134 and 173.
- The exact name of the push builder function for the red test.

## The path of the read

The brief, the dry run 7 read (Result, 2 C, 4), reference C76 and C64, the stack status lines of 15:45 and 16:40, `rulings`, `ruled_refs` and `messages` of m28 to m61, `t5.log` and `t6.log` pages, `principal.py` `removal_line` and `_removal_words`, `runner.py` `START_RULED_KEY`, `_ruled_block`, `_contest_block`, `_mistake_rows`, `PUSH_CHARS`, the first pushes of 6 named sessions and a search over every turn, the `tool_calls`, `receipts` and `touch_strays` of the 19 sessions, the turns of s191, s193, s201, s203 and s204, `git log -S` on four strings, the contested record design sections 1 and 3, and the register case in `l1_touch.yaml`.
