# Review of frame 348, commit 3e0b16ea on rota/foundation, pass 6

Verdict: not ready to close. Pass 7 fixes findings 1 and 2 of p5, and the suite holds. One new high comes from the subject test of `_verb_has_subject`. A pronoun subject such as "I" or "you" makes the head verb relate, so a fault or an instruction after it binds nothing. Counts: 1 high, 1 low.

Worktree: C:/Users/roman/rota_f348f at 3e0b16ea. The review also made C:/Users/roman/rota_f348f_a at 2ebd7f52 and C:/Users/roman/rota_f348f_b at b126acab for point 4. The review removed all three after the run.

## (a) Verdicts on the points

1. Fixed. On `_page6`, silent reply, all approve: the n175 reply text lands all approve. "Tell me why line 3 says line 2 is wrong." lands all approve. "Delete line 3 and tell me why it was there." refuses approve of line 3. At b126acab the first two refused line 3 and line 2.
2. No reading changes with the flag off. `_line_cues` without `asks` gives the same result at 3e0b16ea, b126acab and 2ebd7f52 on all 29 principal texts of l3_rulings.yaml. The new condition starts with `asks and`. The one caller with `asks=True` is the loop at `api.py:14324`.
3. Three texts bind as law 6 asks, and one binds by chance. "Please tell me why line 2 is wrong." binds line 2 as a fault, as the p4 precedent says. "Line 2 says X and line 3 says Y, tell me which is right." binds nothing. "Can you explain why line 4 fails?" binds line 4 as a fault on "fails", as at b126acab. "I think line 2 is wrong, so tell me what line 3 means." binds line 2 only because `page_clauses` cuts it into a clause with no question. The asks reading of the whole sentence faults nothing (finding 1).
4. One text differs. Three principal texts match `_is_question`. The n175 inbound text binds nothing at 2ebd7f52, line 3 as a fault at b126acab, and nothing at 3e0b16ea. The two texts that start "Line 7 is wrong" and "Line 2 is wrong" bind the same lines at all three commits.
5. No hunk falls outside the claim. The api.py diff adds `LineReading.strong`, `_verb_has_subject`, the `head = "none"` branch in `_line_cues` and the loop rule. The loop term `subject & (matched | faulted)` equals the old union, because `subject` is a subset of `c["lines"]`. The test file adds two parameters.
6. Confirmed. `test_frame337_earlier_answers.py` and `test_r1_menu_form.py` with `-n0`: 58 passed. The L3R replay with ROTA_DEV_DB on `f348r6rev_cass.db`: 2 failed, 23 passed. The reds are L3R-n171-m27-m28 and L3R-n172-m76-m77.

## (b) Findings

1. `rota/roles/api.py:13152-13167`, `_verb_has_subject`, with its use at `api.py:13211-13219`. Severity high. CONFIRMED.
   `_SUBJECTS` holds "i", "we" and "you", so any pronoun before the head verb sets the head to "none". The branch then skips the whole window of the reference, fault words included.
   "I think line 2 is wrong, so tell me why it is there." binds nothing. The word "wrong" is his verdict on line 2.
   "Could you remove line 4 and tell me why it was there." binds nothing. "Would you please remove line 4 ..." still binds line 4, because "please" ends the walk.
   Probe: each text as the one earlier answer on `_page6`, silent reply, all approve. At 3e0b16ea all approve lands for both. At b126acab the door refused line 2 and line 4.
   Law 6 says only his words choose a verdict. Here his words chose a fault, and the door lets approve land.
   No recorded text renders the path. A grep of `tests/rota/cases` for a pronoun, a verb and a line reference found none. Only constructed sentences render it.
   Fix: set "none" only when the subject is a line reference (`after_ref`). A pronoun subject keeps the reading of b126acab.
2. Outside the points. `page_clauses`, the clause line list, review p5 finding 3. Severity low. CONFIRMED, and older than pass 7.
   "Explain why line 2 is wrong and line 4 also fails." gives one clause with lines [2]. `_line_cues` faults line 4 on "fails", but the loop intersects with `c["lines"]`, so line 4 binds nothing.
   Only a constructed sentence renders the path.
   Fix: let `page_clauses` list every line that a clause names.

## (c) Probes

All probes ran from a worktree root with `ROTA_MODEL=qwen3:8b`. The review deleted each probe test before it removed the worktrees.

- `tests/rota/test_probe348p6.py`, 8 earlier answers on the `_page6` fixture, silent reply, all approve. It ran at 3e0b16ea and at b126acab. Each printed whether all approve landed or which line the door refused.
- `scratchpad/p6probe.py`, run in each of the three worktrees with PYTHONPATH on that root. It printed `_line_cues` with the flag off for the 29 principal texts of l3_rulings.yaml. It emulated each commit's loop on the 3 texts that `_is_question` matches. It printed the clauses, the subject lines, the cues and the binding of 12 edge texts. The outputs are `scratchpad/p6_a.json`, `p6_b.json` and `p6_f.json`.
- A grep of `tests/rota/cases` for a pronoun subject, a verb and a line reference.
- `test_frame337_earlier_answers.py` and `test_r1_menu_form.py` as is, with `-n0`.
- `test_l3_rulings.py` with `ROTA_DEV_DB` on `scratchpad/f348r6rev_cass.db`, a fresh copy of `D:/repos/rota/tests/rota/cassettes.db`.

The scratchpad is C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d5c14419-fc45-4e3f-b734-46fe335c298f/scratchpad.

## (d) Usage

Input tokens: about 45k. Output tokens: about 10k. Total: about 55k. The total is about 30k over the cap of 25k. The two extra worktrees for point 4 took most of the excess.
