# Frame 329, the provenance read: a respecify that writes a twin

Date: 2026-10-26. Read at commit e636b7b6 on `rota/foundation`. Night 166 ran
at 741d2d06, and `rota/roles/api.py` is the same at both commits in every line
this read names (observed: `git diff 741d2d06 HEAD -- rota/roles/api.py`, one
hunk at 14387, `code_probe`). Read-only: `.rota/clickI_night166.db` opened with
`mode=ro`. Two replays ran on a copy of the database in the session
scratchpad, and the copy is deleted. Rota workflow for the wall, meta workflow
for the read, by the rule of 2026-10-18 (provenance before a fix).

Sources:

- `plans/night166-read.md` lines 160 to 167 (walk 3), 212 (section 2, row
  W-D), 286 to 299 (the W-D candidate), 365 (section 5, sprint row 2).
- `plans/stack.md` lines 1097 to 1105 (frame 329), 1218 to 1232 (frame 322),
  1436 to 1437 (frame 306, W2 pass 1 and 1b).
- `.rota/clickI_night166.db`: `sessions` (s194), `turns` (s194 seq 1 to 4),
  `tool_calls` (every `criteria.*` call of the night), `criteria`, `tests`,
  `messages` m76 to m80, `artefact_versions`.
- `rota/roles/api.py`: `_twin_refusal` 5669 to 5691, `criteria_specify` 5695
  to 5879 (exact twin 5810 to 5827, cap 5843 to 5857), `_DROP_LINE` 5913 to
  5916, `ruling_drops_line` 6285 to 6294, `criteria_retire` 6367 to 6413,
  `_line_dropped_on` 6552 to 6560, `_near_twin` 6584 to 6612,
  `criteria_respecify` 6616 to 6844.
- `rota/core/runner.py` 279 to 300 (`_wake_allow`, `_page_act_lines`).
- `rota/core/identity.py` lines 1 to 30 and 51 to 53.
- `rota/roles/prompts/terminologist/criterion_repair.md` lines 22 to 31, and
  `criterion_repair.tools`.
- `rota/DECISIONS.md` lines 843 to 848 and 1005 to 1010. `rota/LAWS.md` 351
  to 384, law 14.
- `plans/frame306-review-w2.md` lines 52 and 90. `plans/wall-guide.md`,
  causes 8, 9 and 10.
- `git log -S` on `_twin_refusal`, "The same words are the same criterion",
  `@op("criteria", "respecify")`, `def _near_twin`, the respecify call of
  `_near_twin`, and `@op("criteria", "retire")`.

## The result

**Verdict: a departure, not a gap, and the wall is not the one the frame
names.** A design covers the case: law 14 and `identity.py` say "same
ticket, same words, one live row" for `criteria`, and frame 306's W2 pass of
2026-10-24 built `_near_twin` into `criteria.respecify` to hold that rule
(observed: `identity.py` 51 to 53; commit 468fec42). The build differs in one
place. `_near_twin` reads a staged write's ticket from `w[2]["ticket_id"]`,
and a respecify stages its write with no `ticket_id`. So a sibling that the
same session rewrote is invisible to the door (observed: `api.py` 6591 to 6593
and 6824 to 6825; replay 1 below). This is not a departure from a direct
ruling of Roman. Law 14 started as the trial he asked for, "ok lets test it
out", 2026-08-29, and became a law on 2026-09-01 (observed: `identity.py`
line 10; commit b72b76c9).

Three corrections to the night read and to the frame:

1. s194 did not write c_3's words. It wrote one new sentence into both c_1
   and c_2. So c_1 and c_2 are exact twins of each other. c_3 is a
   paraphrase at 9 of 11 prose words, 0.82, under the 0.85 line of
   `_near_twin` (observed: `criteria` rows; `_prose_words` on the three
   texts).
2. The exact-twin door `_twin_refusal` guards only `criteria.specify`, as the
   frame says. But since 2026-10-24 the fuzzy door `_near_twin` guards
   `criteria.respecify` too, and an exact twin of a row on file scores 1.0
   and is refused (observed: replay 2 below). The miss is the twin staged in
   the same session, not the absence of a door.
3. "The retire" that the frame's end names is not reachable on this wake.
   `criteria.retire` is offered only when his words drop a line, and its door
   refuses otherwise (observed: `runner.py` 290; `api.py` 6386 to 6390). "Not
   what I asked for" does not match `_DROP_LINE` (observed: `api.py` 5913 to
   5916). This is the open point below.

## Mechanism 1: the twin door, its ruling and its build

1. **The exact-twin door.** Commit 395535da of 2026-08-27 14:17 added the
   check to `criteria_specify` with the comment "Same ticket, same words, one
   row; a session that wants a second criterion writes a second sentence"
   (observed: `git show 395535da`, the hunk at `criteria_specify`). The
   commit carries a Fable co-author line. It was the build session, before
   the stack labelled frames by workflow (observed: the commit). The record
   is `rota/DECISIONS.md` 843 to 848, "A fourth organ, and its guard,
   2026-08-28": "same ticket, same words, one row".
2. **The ruling behind it.** No ruling of Roman names this door. The rule
   is the identity rule, which the principal asked to trial on 2026-08-29
   and which became law 14 on 2026-09-01 (observed: `identity.py` line 10;
   `LAWS.md` 351; commit b72b76c9). Law 14 says "Exact match at the door;
   fuzzy behind named guards" (observed: `LAWS.md` 369 to 372).
3. **The declaration names one writer.** `identity.py` declares criteria as
   "criteria.specify: same ticket, same words, one live row" (observed:
   `identity.py` 51 to 53). `criteria.respecify` also writes the table, and
   the declaration does not name it (observed: the map, `writes criteria
   (pipeline)` for both ops).
4. **`_twin_refusal` is frame 322's text.** Commit bf300ce4 of 2026-10-25
   00:49 moved the refusal text into `_twin_refusal` and made it name an
   empty sibling ticket (observed: `git log -S _twin_refusal`; `api.py` 5669
   to 5691). The door's predicate is unchanged since 395535da, except the
   retired-row clause of frame 306 (observed: `api.py` 5821 to 5824).
5. **The fuzzy door reached respecify on 2026-10-24.** Commit 468fec42 of
   2026-10-24 18:43, frame 306 W2 pass 1, moved the overlap check into
   `_near_twin` and called it from both ops (observed: the commit body,
   "criteria.respecify meets the near-duplicate check of specify"; `api.py`
   5834 and 6817). Its test seeds two rows on file and respecifies one into
   the other's words. No test stages two respecifies in one session
   (observed: `tests/rota/test_frame306_respecify_twin.py` lines 18 to 72).
   The W2 review did not test that case either (observed:
   `plans/frame306-review-w2.md` lines 52 and 90).

## Mechanism 2: what `criteria.respecify` is for, and the retire

1. **Its design.** Commit fd788bd1 of 2026-08-26 15:24 built
   `criteria.respecify` for one case: a Tester's unresolved question about a
   criterion wakes its writer in `criterion_repair`, "once per question"
   (observed: the commit body; DECISIONS.md 1005 to 1010). The docstring
   still says "Rewrite a criterion that was discovered unencodable or wrong"
   (observed: `api.py` 6620).
2. **The respecify existed before the twin door.** fd788bd1 is one day older
   than 395535da. The twin door went into `specify` only, and no record says
   why respecify was left out (observed: both commits; no DECISIONS line).
   Judged: an omission, not a decision (reasoned: no comment, ruling or test
   names the choice, and frame 306 later treated the missing check as a
   defect).
3. **The contest route.** Commit b0a2086e of 2026-10-09 00:48 sent a
   contest of a criterion row on his page to the Terminologist in
   `criterion_repair` (observed: the commit body). Roman ruled on 2026-10-08
   that the park ask is a page with rows. The route to respecify is the
   build's choice in that commit, not his words (reasoned: the body quotes
   his ruling on the page only). The brief then says "For each criterion
   with contest or revise, rewrite it with `criteria.respecify` to say what
   the words say. Write the criterion in the principal's words" (observed:
   `criterion_repair.md` 22 to 31).
4. **The retire route.** Commit 2a67f47b of 2026-10-24 19:04, frame 306
   pass 1b, added `criteria.retire` at `api.py` 6367 to 6413 (observed:
   `git log -S`). The session judged it in design by the composition line
   "Only a ratified amendment to something approved revokes work
   downstream" (observed: `plans/stack.md` 1437, marked "assumed";
   `plans/composition.md` 71 to 72). The runner offers the op only when
   `criteria_page_acts` finds a drop (observed: `runner.py` 279 to 292). The
   door then needs `ruling_drops_line`, which needs a `_DROP_LINE` match,
   "drop", "remove" or "delete" a line, or "line N should go" (observed:
   `api.py` 6285 to 6294, 6386 to 6390, 5913 to 5916). Otherwise it says
   "Only his ruling retires a criterion. Rewrite it with
   criteria.respecify instead" (observed: `api.py` 6387 to 6390).
5. **What a contest was meant to do.** A contest asks new words for the
   row, and the respecify writes them (reasoned: the brief and frame 243's
   record shape, `plans/stack.md` 2041 to 2042). No design names the case
   where his words leave a row with no fact of its own, because a sibling
   already holds it (observed: no such line in the brief, the docstrings or
   DECISIONS).

## Mechanism 3: what s194 read and did

s194 is a Terminologist on `qwen3.5:9b`, woken by the relay m79, wake
`message`/`relay`, four turns (observed: `sessions`, `turns`).

1. **Turn 1, the prompt.** The wake holds his words of m77, "Lines 2 and 3
   are not what I asked for. They make rules for how the function behaves,
   but only the docstring changes and the code stays the same." It names
   line 2 as c_1, "strips the directory prefix", and line 3 as c_2,
   "returns only the basename" (observed: s194 turn 1 `user`). The pre-run
   `criteria.consult` shows c_3, "The docstring of format_filename must
   include an example demonstrating that with shorten=True, a/b/c.txt is
   displayed as c.txt" (observed: the same text). The tools are
   `criteria.respecify`, `msg.answer_tester` and
   `msg.challenge_vision_keeper`, with no `criteria.retire` and no
   `criteria.specify` (observed: s194 turn 1 `system`, the TOOL list).
2. **Turn 1, the reply.** "I will rewrite both criteria to focus on the
   docstring content." It sends `criteria.respecify` for c_1 and c_2 with one
   text, "When shorten=True, the docstring of format_filename must include an
   example showing that a/b/c.txt is displayed as c.txt.", and a test as the
   surface, then `msg.answer_tester` (observed: tool_calls seq 9 to 11).
3. **Turn 2, the doors.** Both respecifies get the surface refusal, "'...
   test_truncating_docstring' is a test ..., and a test is not a surface".
   The answer gets "no change built from this criterion has a commit yet"
   (observed: s194 turn 2 `user`). The seat sends the same two calls with
   `src/click/utils.py::format_filename` (observed: tool_calls seq 12 and
   13, turn 2 `completion`). This is "s194 seq 2", the turn, not the
   tool_calls seq.
4. **Turn 3, the result.** "OK criteria.respecify -> {"id":
   "c_1_format_filename_example", "respecified": true}" and the same for
   c_2. No twin door spoke (observed: s194 turn 3 `user`). The seat closes:
   "Both criteria now specify that the docstring must include an example"
   (observed: turn 3 `completion`).
5. **The rows.** c_1 and c_2 hold the one text at row version 2, and c_3
   holds its own text at version 1. The criteria counter in
   `artefact_versions` stands at 11 (observed: `criteria`,
   `artefact_versions`). "v10 and v11" is that counter, not a row field
   (reasoned: no column of `criteria` holds 10 or 11). The night ends with 1
   ticket of 3 that holds two live criteria of one text, and three tests,
   `tst_c1` to `tst_c3` (observed: a group-by on `criteria`; `tests`).
6. **What in the prompt led to the copy.** The brief asks one rewrite "for
   each criterion with contest", "in the principal's words" (observed:
   `criterion_repair.md` 24 to 26). His words hold one fact for two rows, so
   two rewrites in his words give one text twice (reasoned: turn 1's reply
   names "both criteria" and one focus). The mode offers no act that drops a
   row, so a rewrite was the only act on each line (reasoned: cause 10, the
   TOOL list). The seat did not copy c_3. It wrote the fact again, near
   c_3's words, because c_3 already held it (reasoned: 0.82 overlap).
7. **Replay 1.** On a copy of the database with c_1 and c_2 set back to
   their texts before s194, the current code took both calls of seq 2 with
   "respecified": true. The staged writes hold only `text` and
   `surface_refs` (observed: the replay's output).
8. **Replay 2.** With c_1 holding the new text on file, a respecify of c_2
   into it got "this says what c_1_format_filename_example says, in nearly
   the same words" (observed: the replay's output). So the door works across
   sessions and fails inside one.

## The repairs

Repair R, the favoured one: the staged-twin read, about 4 to 8 lines of code
in `rota/roles/api.py`, plus one test file of about 40 lines.

1. In `_near_twin` at 6591 to 6593, read the ticket of a staged criteria
   write from the row on file when the write carries no `ticket_id`. A staged
   text also replaces the text on file for its id in the list at 6595 to
   6597, so a sibling's old words do not refuse a right call (reasoned: the
   DB list today holds the old text of a row that the session rewrites).
2. Keep `_near_twin`'s refusal text. The W2 test pins it equal to
   `criteria.specify`'s (observed: `test_frame306_respecify_twin.py` 51 to
   56). Do not route respecify through `_twin_refusal`: its tail, "it needs a
   second sentence" or an empty ticket, speaks to a new criterion, and a
   respecify rewrites one (reasoned: cause 9).
3. The same staged read in `criteria_specify`'s exact check at 5815 to 5824
   is one line (reasoned: a specify after a respecify in one session meets
   the same blindness). It is optional for this frame.
4. The red test: s194's state before seq 2, tk_1_format_filename_example
   with the three texts before s194, then the two calls of tool_calls seq 12
   and 13 in one sandbox. The first lands and the second is refused with
   "this says what c_1_format_filename_example says". A second test: the
   same two calls in two sessions, refused today, stays refused.
5. **Frame 322 shares the function and not the lines.** Frame 322 changed
   `_twin_refusal` 5669 to 5691 and the criteria wake (observed: `stack.md`
   1218 to 1232; bf300ce4). Repair R changes 6591 to 6597 and, at most,
   5815 to 5824. No line of frame 322 moves (reasoned: the two ranges do not
   meet). Frame 322 is on the branch and validating, so the implementer
   starts at the head with 322's passes in it (observed: `stack.md` 1232).
6. Size: 1 cycle, as priced, if the refusal names no retire (reasoned: one
   predicate on a held site, two tests).

Repair R2, the frame's second clause: the refusal of a twin on a contest wake
names a route. Its text depends on the open point below. If the answer is
"his ruling only", the refusal names the sibling and the two acts the mode
holds: write a fact this line alone holds, or send
`msg.challenge_vision_keeper` with the criterion. About 6 lines and one more
test, and 1 more cycle.

## Open points

1. **"Names the retire" crosses law 6.** The frame's end asks that the
   refusal "names the retire for a contest that says 'not what I asked
   for'". The retire door says "Only his ruling retires a criterion", and
   law 6 says nothing is ruled on his behalf (observed: `api.py` 6386 to
   6390). To name the retire here, a seat or a predicate must read "not what
   I asked for" as a drop. That is a ruling on his words. Recommended: keep
   the retire for his drop words only, and change the frame's end to "names
   the sibling and the acts the mode holds". The question goes to Roman only
   if the session wants the wider retire, by the rule that a question that
   crosses the composition is his.
2. **The 0.85 line and c_3.** Repair R leaves c_1 at 0.82 of c_3, so the
   night would still hold c_1 and c_3 for one fact. Lowering the line to
   0.8 reopens the L3 case that set 0.85 (observed: `api.py` 6602 to 6606).
   Recommended: leave the line, and count paraphrase pairs at or above 0.8
   on nights 160 to 166 before any change.
3. **The frame's second clause counts exact text.** "Tickets with two
   criteria of one text" counts c_1 and c_2 on night 166 and does not count
   c_1 against c_3. Keep the count exact, and report the 0.8 pairs beside it
   (reasoned: an exact key is a value no seat can vary, cause 8's cheap
   fix).

## Other inconsistencies met on the way

- `plans/night166-read.md` line 212 and the frame's site line say "into
  c_3's words" and "three identical criteria". The rows show two identical
  criteria and a paraphrase.
- The frame's pointer "`criteria` v10 and v11" names no row field. The rows
  carry version 2, and 11 is the table counter in `artefact_versions`.
- "s194 seq 2" is the turn seq. The calls are tool_calls seq 12 and 13, and
  tool_calls seq 2 is `criteria.consult`.
- `identity.py` names only `criteria.specify` as the writer of the criteria
  rule, while `criteria.respecify` writes the same table.
- The respecify docstring still names only the Tester's repair case, and
  since 2026-10-09 the op also carries his contest.
- `criteria_specify`'s cap at 5848 and exact check at 5815 to 5824 also read
  `ticket_id` from staged writes. A staged respecify is invisible to both.
- s194 sent `msg.answer_tester` twice before any commit, against the brief's
  "When the change has a commit". The door refused it both times with a
  right text (observed: turns 2 and 3). This is W-C's area and costs one
  turn.
