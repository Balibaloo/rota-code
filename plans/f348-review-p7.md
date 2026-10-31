# Review of frame 348, commit 9cb6df43 on rota/foundation, pass 7

Verdict: ready to close. Pass 8 fixes finding 1 of review p6, and the corpus and the two test files hold. Counts: 0 high, 0 low.

Worktree: C:/Users/roman/rota_f348g at 9cb6df43. The review removed the worktree after the run.

## (a) Verdicts on the points

1. Fixed. On `_page6`, silent reply, all approve: "I think line 2 is wrong, so tell me why it is there." refuses approve of line 2. "Could you remove line 4 and tell me why it was there." refuses line 4. "Tell me why line 3 says line 2 is wrong." lands all approve. "Delete line 3 and tell me why it was there." refuses line 3.
2. One text differs, and the difference is the intended one. Three of the 29 principal texts of l3_rulings.yaml match `_is_question`. The n175 inbound text binds line 3 as a fault at b126acab and nothing at 9cb6df43. The texts that start "Line 7 is wrong" and "Line 2 is wrong" bind the same lines at both commits. `_line_cues` with the flag off gives the same result at both commits on all 29 texts.
3. No hunk falls outside the claim. The api.py diff renames `_verb_has_subject` to `_verb_has_line_subject`, returns False without `after_ref`, and returns `k < 0` after the adverb walk. The one caller is in the `asks` branch of `_line_cues`. No caller of the old name remains. The test file turns one parameter list into pairs and adds the two texts of review p6, finding 1.
4. Confirmed. `test_frame337_earlier_answers.py` and `test_r1_menu_form.py` with `-n0`: 60 passed.

## (b) Findings

None.

## (c) Probes

All probes ran from the worktree root with `ROTA_MODEL=qwen3:8b`. The review deleted the probe test before it removed the worktree.

- `tests/rota/test_probe348p7.py`, the four texts of point 1 as the one earlier answer on the `_page6` fixture, silent reply, all approve. Each printed whether all approve landed or which line the door refused.
- `scratchpad/p6probe.py` with tag `g` and PYTHONPATH on the worktree root. It wrote `scratchpad/p6_g.json`. The loop emulation of tag `g` is the 3e0b16ea loop, and 9cb6df43 does not change the loop. A short script compared `p6_g.json` with `p6_b.json`, the b126acab output of review p6.
- A grep of the worktree for `_verb_has_subject`, `_verb_has_line_subject` and `_SUBJECTS`.
- `test_frame337_earlier_answers.py` and `test_r1_menu_form.py` as is, with `-n0`.

The scratchpad is C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d5c14419-fc45-4e3f-b734-46fe335c298f/scratchpad.

## (d) Usage

Input tokens: about 14k. Output tokens: about 3k. Total: about 17k. The total is about 2k over the cap of 15k.
