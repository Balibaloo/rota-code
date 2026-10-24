# Night 163's read

Rota workflow, read by the meta workflow. Night 163 ran cold from
`C:/Users/roman/rota_n163` at 5758cc46, launched 16:33 on 2026-10-24, on
`D:/repos/_AI/sample_repos/clickI` at 2c8cd3a, with the agent principal on
Opus and `GAUNTLET_ITEMS=163` (observed: `.rota/launch_night163.sh`, the
log). The session stopped the night at 18:05 in walk 3. The launcher wrote
no report file and no truth file. Records: `.rota/clickI_night163.db`
(opened `?mode=ro`), `.rota/night163.log`, `.rota/night163_principal.jsonl`,
the clickI repository and the worktree source at 5758cc46. Read on
2026-10-24 by one agent on Opus, with no extract agents and no interviews.
Walk 1 and the start of walk 3 are read in `plans/night163-walk1-read.md`
(17:35). This read cites it and does not redo it.

**The result.** 0 merges of 2 batches, against 2 of 3 on night 162. Item 1,
the docstring example, died on a behaviour criterion that no docstring can
meet (frame 306, the walk 1 read). Item 2, `get_app_dir`, died at its first
Liaison session and never became a statement (W6, new). Item 3, `clear()`,
had right code written in 13 sessions and committed 0 times in 40 tries.
The note door reads `return` to `return False` as an unruled rewrite, and
its only route to keep the change names `msg.escalate_architect`. The
Developer's `batch_start` mode does not hold that tool (W1, frame 283).
Around that loop, his four corrections to the criteria came back six times
unchanged (W2, frame 306). The death moved from the test to the commit door
and to his words.

## 0. The night in numbers

| Measure | Value |
|---|---|
| Phases | onboarding 16:34 (109 steps, 3 asks, 4 replayed calls); walk 1 16:48 (53 steps, 5 asks, quiet, "Stuck. The team gave up on: verdict_failed for bg_1"); walk 2 17:28 (1 step, 0 asks, quiet, the same line); walk 3 17:28 to 18:05, stopped by the session, 21 asks, no step count printed |
| Asks | 26 live in the walks: 5, 0 and 21 (night 162: 28) |
| Batches | 2: bg_1 `format_filename_example` abandoned at 40480656, 34 of 34 tests passing; bg_2 `clear_returns_bool` running, no head commit, 0 tests for its criteria. 3 tickets: tk_1, tk_1_clear_returns_bool, tk_2. 1 cancel (bg_1) |
| Merges | 0 of 2. No report file and no truth file exist (night 162: 2 of 3) |
| Sessions | 265 sessions, 1224 turns (night 162: 422, 2128). Liaison 84, Vision Keeper 68, Terminologist 42, Developer 29, Architect 20, Critic 17, Tester 5 |
| By walk | onboarding s1 to s98; walk 1 s99 to s144; walk 2 s145; walk 3 s146 to s265, 120 sessions, 640 turns |
| Principal | 30 calls on Opus: 4 replayed at onboarding, 5 in walk 1, 21 in walk 3; 2.45 dollars |
| Verdicts | 3 fails, 0 passes, all bg_1 on c_1 (night 162: 0 fails, 2 passes) |
| Commits | bg_1: 3 heads from s126 to s144. bg_2: 40 `code.commit` calls in 13 Developer sessions, 0 landed |
| Wrote own tool results | 38 of 265 sessions (frame 113 below) |
| Faults | 10 open rows, all bg_2 Developers, s221 to s254, 9 on the note at line 609 and 1 on c3_terminal_check's surface |
| Quarantines at the end | `-|tick:constraint_zero|`, `vision_keeper|tick:contested|format_filename_example`, `terminologist|tick:criteria|clear_returns_bool`, all at 3; `developer|tick:batch_start|bg_2` at 1 after the last lift |

(observed: `.rota/night163.log`, `sessions`, `turns`, `tool_calls`,
`batches`, `verdicts`, `faults`, `tick_attempts`, the jsonl, 2026-10-24.)

## 1. The held frames

**Frame 283, the noted write. Past its night 3. Met in the wrong
direction: the door refused a wanted rewrite 40 times.** Item 2, the
replaced statement, was the frame's planned sample, and item 2 never ran
(W6). Item 3 met the door in its place. The base `clear()` has a bare
`return` at line 609. Each bg_2 Developer wrote `return False` there,
which is the item's own ask. The span note said "This write removes or
rewrites 1 statement that your text does not hold: `return` at line 609"
(observed: s221 t6 to t16). The route says "To keep the change, send
msg.escalate_architect" (observed: `_note_routes`, `api.py` about 19685 at
5758cc46). `batch_start.tools` does not list that tool, so s252's escalate
was refused: "'msg.escalate_architect' is not in this role's working set"
(observed). No criterion, item text or ruling names the line, so
`_unruled_gone` never admits it (observed: `_ruling_texts`, the criteria
and the rulings). 25fa18ef made the whole-file note skip a rewritten
statement. The span note did not get the same change (reasoned from the
commit subject and s221's span write). W1.

**Frame 281, the Tester and a fixed version. Night 1 after the build. Not
exercised: 0 Tester sessions on bg_2, and no item needs a version.** The 5
Tester sessions all served bg_1's c_1 and c_2: s122 and s124 in walk 1,
then s158, s178 and s197 in walk 3, after bg_1 was abandoned. s197 wrote
two tests on the dead batch (observed: `receipts` on `tests`).

**Frame 304, the encode door. Past its night 3. Not exercised: 0 arrange
refusals.** The encode refusals are 23 lines in 4 sessions, all on bg_1
(observed: the runner accounts). No item had a raising arrange step.

**Frame 317, the Tester woken by an answer. Night 2. Met in a new form:
two answer wakes went to a dead batch.** m76 and m98 woke s178 and s197 on
c_1 and c_2 after bg_1's cancel. s197 re-encoded both tests. No run
followed, so the frame's own sign, a fix undone, did not occur (observed).

**Frame 318, the quarantine lift. Night 1 after the build. The head lift
was not exercised, because bg_2 never got a head. The criteria lift fired
on each round of a loop that no criterion move could change.** Each
Terminologist respecify of c3_no_terminal_true or c3_terminal_failure_true
moved a criteria row of bg_2. The batch-wide lift deleted the `batch_start`
key, and three more Developers met the same note (observed:
`_lift_quarantines`, `db.py` 583 to 660 at 5758cc46, receipts v11 to v22).
This is the frame's third clause in reverse: a lift on a move that does
not touch the cause (reasoned). Part of W1's cost.

**Frame 316, the agenda page and the park. Night 2. Not met.** Item 1's
rows reached clear's page m48 by the submit path (the walk 1 read, section
3). Then the dead item reached him as a page of its own. m70 and m92 came
after his confirms m66 and m85 of the clear request. Each showed item 1
with his own refusal sentence as line 1, and its guess, c_1 and c_2 as
lines 2 to 4 (observed: the jsonl). Doubt 1: 0 parked rows reached him,
`item_parks` is empty, and no page holds "park", "shipped" or "merged",
because nothing merged (observed). The park at the merge has no sample. W3.

**Frame 303, the textless propose. Past its night 3. Not exercised: 0
propose calls** (observed: `tool_calls`).

**Frame 306, his words and the criterion. Night 3. Met twice on the first
half.** Item 1's c_1 says `returns os.path.basename(path)` on a docstring
item, and his "the code does not change" at m24 and m29 did not reach it
(the walk 1 read, section 1). On item 3, his corrections of m111 to m139
never reached the criteria (W2). The second half, a change outside the
criteria that merges, has no sample, because nothing merged.

**Frame 305, the line reader. Night 2. 0 wrong placements on the clear
pages, 1 wrong approve.** At m111 to m139, "delete line 5", "change line
6" and "delete line 7" landed as contest, revise and contest on the right
rows (observed: `rulings`, the m111 page). At m85 he wrote "The first
sentence ... please leave it out ... so ok". The ruling approved statement
s4 whole, with the remark in it (observed: `r_92c4fcb7b5`, `statements`).

**Frame 311, the docstring refusal. Night 3. Met: 0 refused docstring
lines of 3** (the walk 1 read, section 1).

**Frame 312, the page after a stop. Night 3. Met and widened twice.** In
walk 1, the all-approve at m35 landed no verdict and no lift (the walk 1
read, section 2). In walk 3, six pages, m115 to m139, said "The team gave
up: the change could not start after 3 attempts" over 8 lines of "check:
none yet". No page named the note at line 609 or the code already written
(observed: the jsonl). So he answered the criteria each time, and the
cause sat in a door he never saw (reasoned).

**Frame 313, the span door. Night 3. Not met: 0 boundaries inside a
docstring.** 3 block-crossing refusals, s126 twice and s243. bg_1's
docstring write landed at df80e1c3 (observed).

**Frame 257, one id. Night 3. Met: 0 second texts under one id.** 8 ids
were sent twice in one session, in s114, s199 and s202. Each repeat was
refused as the same words, the same id or a near duplicate (observed). The
near-duplicate check did not run on `criteria.respecify`. s209 to s265
rewrote c3_terminal_failure_true into c2_non_terminal_false's words on the
same ticket, and c3_no_terminal_true into c1_clear_terminal_check's words
(observed: the m111 and m139 pages, receipts). W2.

**Frame 258, the line-1 contest. Night 2. 0 wrong contests of line 1.**
m70 and m92 named line 1 and contested item 1, which was right by his
words (observed: `r_d04fd2afc2`, `r_00866dd481`). 0 line-1 refusals.

**Frame 201, the hold. Night 2. Not seen.** No runner account holds the
hold's text, and 0 passes landed (observed). The 3 fails came from the
lines check on c_1 (the walk 1 read).

**Frame 315, the re-slice. Night 2. No re-slice, and one new case: the
words door made the item text his refusal.** s167, the Vision Keeper on
`tick:contested` at attempt 3 of 3, first asserted "The docstring of
format_filename accurately reflects ..." for item 1. The door refused it:
"format_filename_example is the principal's own words. The new text says
`accurately`, `reflects`, `behavior`, and the principal said ..." (observed:
s167 t1 and t6). At t4 the seat copied the first sentence of his m61 answer
verbatim, "I don't know whether that example is there, and it doesn't
matter here ...". That text landed as the item at v18 (observed:
receipts). So a door that keeps his words verbatim stored a sentence that
rejects the item as the item (reasoned). Frame 315's pass 1 carries the
clarify's words into the wake, which put m61 in reach (reasoned: the 06:21
status line).

**Frame 113, parked. 38 of 265 sessions wrote their own tool results.**
Developer 13 of 29 (qwen3.5:9b), Vision Keeper 12 of 68, Liaison 6 of 84,
Architect 3 of 20 (qwen3:8b), Critic 2 of 17, Terminologist 2 of 42
(observed: the "wrote its own tool results" line in each runner account).
Night 162's read holds no count. The same count on its database is 48 of
422: Developer 13 of 56, Vision Keeper 9, Architect 8, Terminologist 7,
Tester 5, Liaison 4, Critic 2 (observed). The Developer share doubled,
from 23% to 45%. On bg_2, 7 of 13 such Developers stopped at "OK
code.source ->" and wrote nothing (observed). The rise follows the note
loop: a seat that meets the same refusal again reads ahead (reasoned).

**Frame 319 is not on this head** (doubt 3 in section 2).

## 2. Every wall the night met

| # | Wall and sign | Sessions | Asks | Place |
|---|---|---|---|---|
| W1 | **The note door refuses the rewrite the item asks for, and its keep route names a tool the seat lacks.** `return` to `return False` at line 609 of `src/click/termui.py`. The code in s221 t6 is right by his words and by c2_non_terminal_false. 40 commit calls, 0 landed. s237, s243 and s246 restored the bare `return` and wrote again. s252 tried the escalate and was refused. 9 faults name the note "phantom" or "stale" (observed) | 20 Developers, s220 to s261, and 6 quarantine Liaisons | 6, m115 to m139 | **Cause 8**, wrong to fire: a rewrite that the item's criterion names is read as an unruled removal. **Cause 9**: the route names `msg.escalate_architect`, absent from `batch_start.tools` and `verdict_failed.tools`. Frame 283 |
| W2 | **His corrections to the criteria come back unchanged.** m111 asked: delete line 5, a repeat; delete line 7, "a failed clear is not part of what I asked for"; change line 6 to "the current stdout"; add "the output stays exactly the same". Each ruling landed. A contest relays to the Terminologist, which can only respecify, so both rows stayed and became duplicates. s226's revise of c3_terminal_check was refused twice on its surface (`get_text_stdout` "lives in src/click/_compat.py") and never sent again. No route adds a criterion from a page. m139's page is m111's page (observed) | 6 Terminologists, s226 to s265, 12 receipts | the same 6 | **Cause 12**: "delete" has no act on a criterion. **Cause 8**, not firing: respecify skips the near-duplicate check. Frame 306, first half |
| W3 | **Item 1 outlived its cancel.** m48's "take lines 3 to 6 off" contested item 1 (the walk 1 read, section 4). Six Vision Keeper `tick:contested` sessions, s159 to s189, kept it alive. The Liaison asked about format_filename at m56, m60 and m78. s167 stored his m61 refusal as the item text. Pages m70 and m92 showed that text as "You asked" after he confirmed the clear request twice (observed) | about 50, s146 to s198 | 6: m48, m56, m60, m70, m78, m92 | **Cause 11**: what reaches him is not his. Frame 316, widened from the submit path to the contested path. The verbatim store is frame 315 |
| W4 | **bg_1: a behaviour criterion on a docstring item** (the walk 1 read, section 1) | 3 Critics, 7 Developers | 4, m24 to m39 | **Cause 1** at the criteria writer. Frame 306 |
| W5 | **The stuck after an all-approve, and stop pages that hide the cause.** Walks 1 and 2 ended on "verdict_failed for bg_1" (the walk 1 read, section 2). The six bg_2 stop pages said "could not start after 3 attempts" (frame 312's section) | walk 2's 1 step | m35, and W1's 6 in part | **Cause 6** at `land`. Frame 312 |
| W6 | **Item 2 died at its first Liaison session.** s145 woke on m_p2 with his `get_app_dir` sentence. It sent `msg.clarify_principal` four times, each a paste of his sentence, and the door refused each: "is the principal's own sentence, pasted back to them". The session ended with no statement and no page. Nothing retried the message, and walk 2 went quiet after 1 step. Entry e_p2 stands with no statement, no item and no message after it (observed: `entries`, `statements`, s145) | 1 | 0 | **Cause 6**: a message wake that ends with nothing done is not retried, and the walk reads quiet. A new frame. Doubt 2 below |
| W7 | **The criteria writer invents cases.** One sentence got 9 criteria on two tickets. m101 lines 6 and 8: "returns True ... even when stdout is not a terminal" and "returns True if ... the clear operation fails, provided no exception is raised". Line 7: "the underlying stream object passed to it", though `clear()` takes no argument. Surfaces name `examples/termui/termui.py::clear` and `raw_terminal` (observed: `criteria`, the m101 page) | s199, s200, s202 | m101 | **Cause 1**. Frame 319's kin, doubt 3 |
| W8 | **bg_2 started with no tests.** 0 Tester sessions on bg_2 and 0 `tick:tests` wakes in walk 3. Every page line says "check: none yet" (observed). The cause is not read | 0 | 0 | Not placed. Read before a frame |
| W9 | Onboarding: s5 and s6 died on the server, "LLMUnavailable('ollama at http://127.0.0.1:11434: no answer in 300s')". s7 went on and m2 was presented (observed) | 2 | 0 | Doubt 4 below |

(observed: `turns`, `tool_calls`, `receipts`, `rulings`, `criteria`,
`messages`, `entries`, `statements`, the jsonl, the worktree source,
2026-10-24.)

**The bg_2 loop, one round.** The round ran six times from s220 to s262
(observed):

1. Three Developers on `tick:batch_start` read `clear()`, write the right
   code with `code.write` on the span 601 to 613, and commit in the same
   reply. The note refuses each commit.
2. The key `developer|tick:batch_start|bg_2` reaches 3 and quarantines.
3. A Liaison on `tick:quarantined` presents "The team stopped work on this
   change." with the criteria lines.
4. He asks for the same four corrections. The ruling lands contest, revise
   and contest.
5. The Terminologist respecifies the two contested rows. The move lifts the
   quarantine (frame 318), and step 1 runs again.

**The sender's four doubts.**

1. Frame 316's park: no parked row reached him, and no shipped line showed
   a count, because nothing merged and `item_parks` is empty (observed).
2. Item 2 under `if WIN`: the agenda and the slicing never saw it. It
   stopped at the Liaison before a statement existed (W6). The walk 3
   statement s2, from e_p3, was stored with `supersedes` s1, the
   format_filename statement (observed: `statements`). Not read further.
3. Frame 319's residue: 0 criteria name an exception identifier, by the
   102 specify and respecify calls and the current criteria (observed; the
   call summaries cut the text at about 55 characters). One criterion text
   named an exception in a negation: c3_terminal_failure_true on m101 and
   m111, "provided no exception is raised" (observed: the pages). It names
   no identifier, so frame 319's door would not fire on it (reasoned).
4. Ollama 0.33.3: two sessions died on the server, s5 and s6, both at
   onboarding on m1. No session died on the server in the walks (observed:
   the log; `sessions.committed` is 0 for those two only).

## 3. The request line

**The request line held, and the death came after it.** The line-1 calls
on m70 and m92 were right (frame 258). Three faults sit around the line:

1. **His confirm of a new request did not reach a page of it.** m66 and m85
   confirmed the clear request, and the next pages, m70 and m92, presented
   the dead item 1 (W3).
2. **A remark he asked to leave out stayed in.** m85's approve stored s4
   with "I don't have exact code to give you" (frame 305's section).
3. **A request sentence can vanish.** Item 2 never became a statement (W6).

## 4. The agent principal's asks and tokens

30 calls on Opus: 4 replayed at onboarding (3 pages, 1 conversation), then
5 in walk 1 (4 pages, 1 confirm) and 21 in walk 3 (12 pages, 6 clarify, 3
confirms) (observed: the jsonl). He read 30.4k characters of pages and
wrote 7.1k characters of answers, about 7.6k and 1.8k tokens at four
characters a token (night 162: 46.3k and 8.0k characters). Walk 3 took
20.3k characters in 21 calls, and the six stop pages were about 1.3k each
(observed). The cost was 2.45 dollars, 2.00 of it in walk 3. No merge, so
no asks per merge. Of walk 3's 21 asks, 6 went to item 1 after he asked to
drop it (W3), and 6 repeated one correction (W2). His answers were right
each time the records can check them: "the code does not change" (m24,
m29), "only the return value changes" (m48 to m108), "clear() takes no
stream" (m101), and the duplicates at m111 (observed). He could not answer
the cause of the stop, because no page named it (frame 312).

## 5. What the next night should be held on

**Hold the next night on the commit door: a Developer's right code lands
when the item asks for the rewrite, and the seat always holds the tool
that a refusal names** (reasoned: W1). Night 163 merged nothing. W1 spent
the most sessions and asks, and its cause is two doors, not a model limit.
W2 is second, and it is the larger breach of purpose: his words landed six
times and changed nothing. The order, priced by the rule that a door
predicate or a text is 2 cycles and about 60k on Opus:

| Rank | Row | Frame | Site | Red test | Cycles |
|---|---|---|---|---|---|
| 1 | **The keep route names a tool the seat holds, and a rewrite that a criterion names is not an unruled removal** (W1) | 283 | `_note_routes` and `_unruled_gone` in `rota/roles/api.py`, about 19685 and 19060; `rota/roles/prompts/developer/batch_start.tools` and `verdict_failed.tools` | s221 t6 to t16, the span write of `return False` at line 609; s252's escalate refusal | 1 for a provenance read of pass 5c, 2 for the tool set and the route text, 2 for the predicate |
| 2 | **"Delete" on a criterion line removes the row, respecify meets the near-duplicate check, and a page can add a criterion** (W2) | 306 | the contest relay in `land` (`rota/roles/principal.py`); `criteria.respecify` in `api.py` | m111 to m139; the respecifies of s209 to s265; s226's surface refusal | 2 to 4 |
| 3 | **A contest on another item's rows does not keep that item alive or re-present it to him** (W3) | 316, with 315 | the signoff submit refs; the `tick:contested` wake; the words door of `problem.assert` | m48, s159 to s189, s167 t4, m70, m92 | 2 |
| 4 | **A Liaison message wake that ends with nothing done is retried or reported, and the walk does not read quiet** (W6) | a new frame | the message dispatch in `rota/core/loop.py`; the quiet test in `probes/walk.py` | s145 on m_p2 | 1 to read, 2 to fix |
| 5 | **A stop page names the refused door and the code already written** (W5) | 312 | the "stopped work" text in `rota/roles/principal.py` | m115 to m139 | 2 |
| 6 | **A criteria move lifts only the keys it can change** (W1's cost) | 318 | `_lift_quarantines`, `db.py` about 650 | the lifts after s226 to s265 against an unchanged note | 2 |
| 7 | **The criteria writer's invented cases** (W7), and bg_2 with no tests (W8), read first | 319 kin; W8 unplaced | s199 to s202; the Tester tick | m101 lines 6 to 8 | 1 for the read |

**Night 164 can run from the branch head, but it should not run before
row 1 lands.** The head carries frame 319's door, 21551df8 and 9c4f02d9,
on top of 5758cc46 (observed: `git log`). That door acts on
`criteria.specify`. It does not touch the note door, the contest relay or
the Liaison retry (reasoned). So night 164 from the head would meet W1
again on item 3 and spend its walk the same way. Run it after row 1, with
the same three items: item 2 then gives frame 283 its sample, item 3 gives
the rewrite, and item 1 gives frame 306 again (reasoned). If row 1 cannot
land first, run the head with item 2 first. Item 2 is the one item that no
wall of this night measured (reasoned).

The next night then measures frames 283, 306 and 312 on the commit and the
page, frames 258, 305, 316 and 317 on their night 3, frames 281 and 318 on
their night 2, frame 315's words door, and frame 113's Developer share
against 45%.

## Usage

One agent on Opus, no extract agents and no interviews. About 120k tokens
in and 16k out, estimated. Not read: the Tester tick's rule for bg_2 (W8),
why statement s2 supersedes s1, the m_p2 dispatch code (W6), the full
contexts of s145 and s252, and the turns of the 38 sessions that wrote
their own tool results.
