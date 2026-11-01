# Review p10 of frame 354: commit 3668fd4f, pass 11

Verdict: the claim holds on the three points. Counts: 0 high, 2 low (0 outside). The tests: 4 files green, `test_l3_rulings.py` 23 of 25, the same two reds as p6 to p9.

## (a) Verdicts on the points

1. Holds. On pages of two and three lines, "1 is not right 2 ok", "1 does not work 2 drop", "1 isn't what I asked 2 drop", "1 ok 2 drop" and "1 was fine 2 drop" bind line 1 to its own words and line 2 to its own words. Line 3 gets None. "1 try again" binds line 1 alone. "2 examples are too many 1 ok", "3 at most 2 drop", "2 lines are wrong", "I want 2 examples" and "Drop both of those examples" give every line the whole reply. `page_clauses` gives one clause per bound line, and one clause with every line for the whole-reply forms. "2 is right 1 ok" binds each line in either order. The fixed list misses common verb heads of a correction (finding 1).
2. None. The commit touches `rota/roles/api.py` and `tests/rota/test_r1_menu_form.py` only. Both hunks serve the claim. The commit message names a gate run with 5 new reds that it marks flaky. This review did not run the gate.
3. Holds. `-n0` runs: `test_r1_menu_form.py` 56 passed. `test_frame354_quarantine_page.py` 29 passed. `test_agent_principal.py` 11 passed. `test_runner.py` 137 passed. `test_l3_rulings.py` 2 failed, 23 passed. The reds are L3R-n171-m27-m28 and L3R-n172-m76-m77. No case moved off 23 of 25.

## (b) Findings

1. rota/roles/api.py 13710, low, CONFIRMED. `_LEAD_VERB` misses common verb heads of a correction. Probe p1: "1 can't be right 2 ok", "1 won't do 2 ok", "1 has a typo 2 ok", "1 needs a rewrite 2 ok", "1 misses the point 2 ok", "1 looks fine 2 drop", "1 did not run 2 ok", "1 were fine 2 drop" and "1 not right 2 ok" give every line the whole reply. This is the parent behaviour, so no regression. The most common misses are "needs", "has", "did", "can't" and "were". The list holds "was" and not "were". Fix: add "were", "has", "needs", "did", "can't", "won't" and "not" to `_LEAD_VERB`, with a test per word.
2. rota/roles/api.py 13710, low, PLAUSIBLE. A verb head that the list misses silently gives every line the whole reply. No read-back line tells him that the number did not name a line. A later pass may want the read-back to say that the whole reply landed on every line. Fix: none in this pass. Note the open list in the frame.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/393648aa-e5f9-4235-ad76-56489455e14e/scratchpad/f354p10r/`. They ran from `C:/Users/roman/rota_f354r` with `ROTA_MODEL=qwen3:8b`. No model call ran, and the gate did not run.

- `p1_binder.py`: `line_words` and `page_clauses` on the eleven forms of point 1 and fourteen more verb heads, on pages of two and three lines. The output is `p1_out.txt`.
- The point 3 runs used `-q -n0`. The L3R run read a copy of `D:/repos/rota/tests/rota/cassettes.db`. The copy is deleted, and `git status` in the worktree is clean.

## (d) Usage

The harness shows no exact counts, so these figures are estimates. Input: about 30k tokens of context at the end. Output: about 4k tokens. Total: about 34k. The brief's cap of 20k did not hold.
