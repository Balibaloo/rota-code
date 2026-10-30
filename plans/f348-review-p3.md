# Review of frame 348, commit 3422ecd1 on rota/foundation, pass 3

Verdict: not ready to close. Pass 4 fixes both highs of p2, and the suite holds. One new high comes from the fix of high 2. An earlier "Line 3 is unclear to me, so please say what it means." now binds line 3 as a fault. That phrase is in the corpus, on nights 174 and 175. Counts: 1 high, 3 low.

Worktree: C:/Users/roman/rota_f348c at e6e93208, the docs commit on 3422ecd1. The review removed the worktree after the run.

## (a) Verdicts on the points

1. Fixed. Earlier "Line 2 is wrong.", silent reply, all approve: the door refused three calls in a row. The refusal text names `rulings.rule(ask=...)` and leaves approve out of the menu.
2. Fixed. "Line 2 is wrong and line 6 is unclear." and "Line 2 is wrong, tell me where it came from." now refuse approve of line 2. The control "Line 2 is wrong and line 6 is odd." refuses too. The fix also binds clauses that pass 3 meant as pure asks (finding 1).
3. No mode lacks the ask. `ask` is a parameter of `rulings_rule` itself, so every seat with `rulings.rule` has it. An ask that repeats m77 meets `refuse_answered_question`. A reworded ask then lands, as m79. A line on a closed change takes approve only, so the ask or the end of the session is its only way out (finding 3).
4. No hunk falls outside the two claims. The api.py diff from a8ff05d4 holds two hunks, the earlier-answer loop at 14256-14268 and the refusal at 14482-14493. The `refused` parameter stays in use at four other places. The first hunk also reverses the skip of a question-mark clause that existed before pass 3 (finding 2).
5. `test_frame337_earlier_answers.py` and `test_r1_menu_form.py`: 51 passed. The L3R replay with ROTA_DEV_DB on a scratchpad copy of cassettes.db: 2 failed, 23 passed. The two reds are L3R-n171-m27-m28 and L3R-n172-m76-m77, the same as p1 and p2.

## (b) Findings

1. `rota/roles/api.py:14262-14266`, the question branch of the earlier-answer loop. Severity high. CONFIRMED.
   `_line_reading` reads "unclear" as a fault, so the intersection keeps the line that the ask names.
   Probe: earlier "Line 3 is unclear to me, so please say what it means.", silent reply, all approve. The door refused approve of line 3. At a8ff05d4 the call landed.
   The p2 scan found this phrase on night174 m25 and night175 m25. Pass 3 widened `_is_question` for these phrases. Pass 4 undoes that for them.
   The refusal fires on every call. The seat must then ask him again, or contest a line he only asked about. No recorded case renders the path.
   Fix: read the verdict from the clause with the `_ASKS_FOR_FACTS` span and "is unclear" blanked, and bind only the faults that remain.
2. `rota/roles/api.py:14265-14266`, the same branch, for a question mark. Severity low. CONFIRMED on constructed text, no corpus check.
   "Is line 2 wrong?", "Why is line 2 wrong?" and "Line 2 is wrong?" now bind line 2 as a fault. The door refuses approve on every call.
   Before pass 3, the loop skipped every clause with a question mark. "Is line 2 fine?" lands approve, which is correct.
   Fix: in a clause with a question mark, bind a fault only from a declarative part outside the question.
3. `rota/roles/api.py:14031-14033` and `14487-14493`, a line on a closed change. Severity low. CONFIRMED with a patched `line_menu`.
   `line_menu` gives a touch line of a merged or abandoned batch the menu `["approve"]` only, with no `other`.
   Probe: line 2 patched to that menu, earlier "Line 2 is wrong.". Two approves were refused with the text "takes . When no option". `other Line 2 is wrong` was refused as no option.
   The only ways out are a reworded ask to him and the end of the session. An approve on a closed change moves nothing, so the refusal protects nothing.
   Fix: skip the refusal when `others` is empty.
4. `tests/rota/test_frame337_earlier_answers.py:167-171`, the misread of "Line 2 was wrong before, now it is fine.". Severity low. CONFIRMED by reading.
   The docstring names the misread as a residue of `_line_reading`. With the every-call refusal, the misread now refuses approve on every call.
   The way out is `other`, which lands a contest against "now it is fine", or an ask to him. No test covers the misread now.
   Fix: teach `_line_reading` that "now it is fine" after "was wrong before" approves the line, and keep a test for it.

Outside the points: the commit claims two tests red at a8ff05d4. The review did not run the tests at a8ff05d4.

## (c) Probes

All probes ran from the worktree root with `ROTA_MODEL=qwen3:8b` and `-n0`. The review deleted the probe file after the run.

- `tests/rota/test_probe348p3.py`, 11 tests on the `_page6` and `_landing` fixtures:
  - three all-approve calls after "Line 2 is wrong.".
  - eight earlier answers beside an ask or a question mark, with all approve.
  - an ask that repeats m77, and a reworded ask.
  - line 2 patched to a closed-change menu: two approves, an `other`, and a repeated ask.
- `test_frame337_earlier_answers.py` and `test_r1_menu_form.py` as is.
- `test_l3_rulings.py` with `ROTA_DEV_DB` on `scratchpad/f348r3_cass.db`, a copy of `D:/repos/rota/tests/rota/cassettes.db`. The worktree holds no cassettes.db, because git does not track it.

The scratchpad is C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/a9a43280-d634-4af9-9ae0-e50791297894/scratchpad.

## (d) Usage

Input tokens: about 26k. Output tokens: about 7k. Total: about 33k. The total is over the cap of 30k because of the replay output.
