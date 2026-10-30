# Review of frame 348, commit 2ebd7f52 on rota/foundation, pass 4

Verdict: not ready to close. Pass 5 fixes the high of p3, and the suite holds. One new high comes from the fix. `_REQUEST_SPAN` removes text to the sentence end, so a fault after a request in the same sentence binds nothing. Counts: 1 high, 1 low.

Worktree: C:/Users/roman/rota_f348d at f1d92c64, the docs commit on 2ebd7f52. The review removed the worktree after the run.

## (a) Verdicts on the points

1. Fixed. Earlier "Line 3 is unclear to me, so please say what it means.", silent reply, all approve: the call landed. Earlier "Line 2 is wrong and tell me where it came from." still refuses approve of line 2. The comma form refuses too.
2. Yes, the span removes the fault. "Tell me what line 2 means, because it is wrong." binds nothing, and all approve lands. At 3422ecd1 the clause bound line 2 (finding 1).
3. Confirmed. The `_ASKS_FOR_FACTS` pattern and flags are equal at both commits. Over 3775 strings of l3_rulings.yaml, 57 of them principal texts, the match spans differ in none.
4. No hunk falls outside the claim. The api.py diff holds two hunks: the regex split at 14096-14107 and the re-read at 14269-14274. The re-read also sets the fault flag in `bound`, which the claim implies.
5. `test_frame337_earlier_answers.py` and `test_r1_menu_form.py`: 53 passed. The L3R replay with ROTA_DEV_DB on a scratchpad copy of cassettes.db: 2 failed, 23 passed. The two reds are L3R-n171-m27-m28 and L3R-n172-m76-m77, the same as p1 to p3.

## (b) Findings

1. `rota/roles/api.py:14107` and `14272-14273`, `_REQUEST_SPAN` with `[^.!?]*`. Severity high. CONFIRMED.
   The span runs from the ask verb to the sentence end, so it eats a verdict that follows the request.
   Probe: four earlier answers, silent reply, all approve. All four landed approve:
   - "Tell me what line 2 means, because it is wrong."
   - "Tell me what line 2 means, line 4 is wrong."
   - "Please explain why line 2 is wrong."
   - "Line 3 is unclear to me, so please say what it means." (correct)
   The function probe: `_line_reading` of the first clause faults {2}. With the span removed, the text is " ." and faults nothing.
   A semicolon or a full stop ends the damage. "Tell me what line 2 means; line 2 is wrong." still refuses approve of line 2.
   The l3_rulings corpus holds no clause where the removal drops a fault. No recorded case renders the path.
   Fix: end the span at the wh-clause verb or at the first comma or conjunction, and keep the text after it.
2. Outside the points. `page_clauses`, the clause line list. Severity low. CONFIRMED, and older than pass 5.
   "Line 6 is unclear and line 2 is wrong." gives one clause with lines [6] only. So line 2 is never a subject, and all approve lands.
   "Line 6 is odd and line 2 is wrong." gives lines [6] too, so the cause is not the ask.
   Fix: let `page_clauses` list every line that a clause names as a subject.

Outside the points: the review did not scan the run databases for the phrase of finding 1. The scan covered l3_rulings.yaml only.

## (c) Probes

All probes ran from the worktree root with `ROTA_MODEL=qwen3:8b`. The review deleted the probe test after the run.

- `tests/rota/test_probe348p4.py`, 10 earlier answers on the `_page6` and `_landing` fixtures, silent reply, all approve. Each printed LANDED or REFUSED.
- `scratchpad/p4lr.py`: `page_clauses`, `_is_question` and `_line_reading` on four texts, with and without `_REQUEST_SPAN`.
- `scratchpad/p4re.py`: the `_ASKS_FOR_FACTS` source of 3422ecd1 from `git show`, run beside HEAD over every string of l3_rulings.yaml. It also counted principal clauses where the span removes a fault.
- `test_frame337_earlier_answers.py` and `test_r1_menu_form.py` as is, with `-n0`.
- `test_l3_rulings.py` with `ROTA_DEV_DB` on `scratchpad/f348r4_cass.db`, a copy of `D:/repos/rota/tests/rota/cassettes.db`.

The scratchpad is C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/a9a43280-d634-4af9-9ae0-e50791297894/scratchpad.

## (d) Usage

Input tokens: about 17k. Output tokens: about 5k. Total: about 22k. The total is in the cap of 25k.
