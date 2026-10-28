# Momentum note of session 6d9cf7e1, peer name rota-ba

Message rota-ba for anything this note withholds or you doubt. I keep the last of my context to answer, and I stop when you message the word released. Three of my agents still run, and I send you each result when it arrives. Read `CLAUDE.md` first, then `python -m rota.tools.state --sid <your sid>`, then this note, then the stack's head down to Sprint 26. Written on 2026-10-27 at 19:40, after night 171's read. Meta workflow.

## What happened, in rota's terms

Night 171 merged 1 of 3, from 2 of 3 on night 170 (`plans/night171-read.md`). Frame 343's fix held: `format_filename` merged. Walk 1 failed three ways. The Critic could not pass an `if`/`else` (F37 residue, `plans/night171-critic-read.md`). Rota's escape advice told the Tester to write "AppData/Local", so the test could not pass on Windows (W3). A Developer then deleted the darwin and XDG branches, and the Architect judged the bare file foreseen (W4, `plans/night171-w4-read.md`). Walk 2 went quiet: `rulings.rule` refused 75 of 92 calls, his words reached no ruling (F2).

Roman ruled three times today. First, on the reviewer: "That workflow is fine, I don't mind that it merged because the model approved, I want to trust the reviewer ... Yeah I'm for a small prompt change in this case". So no citation check and no hold on a merge; the Architect's prompt asks, for a removal, whether his request or an approved criterion asks for that behaviour to go. Second, he asked "are we not doing all the fixes before the next night?". His ruling of 2026-10-26 23:4x applies: night 172 runs after every known fix of sprints 28 to 31 is built and landed, plus W3 and the how_it_works cause. Third, earlier, his questions "Do we need to?" and "Am I understanding?" are recorded on frame 339; they are questions, not rulings.

## What is on the head

`rota/foundation` holds f20root (82d426c4), f19root (f8955d32) and f31root (e42d13d1). Each land gate in `C:/Users/roman/rota_g328` showed the 11 known reds of 9827e38a and no new red, after re-records. The gate worktree sits on branch `land28` at 2bbace14, which adds f25root on top of the head. Do not land 2bbace14.

## In flight, by branch

- F25, `f25root` at 6a5d0850 (passes 1b to 1e, reviews p1 and p2 in `plans/f25-review-p1.md`). The land gate on 2bbace14 found one regression, `L1-LI-a-separate-request-is-later` at 1/5. Pass 1e fixed it, and the case re-recorded green 5/5 on the merge 657c559c in `rota_g328`. The land gate on 657c559c runs to `gate_657c559c.txt` in my scratchpad. Land f25root when it shows the 11 known reds and no new red.
- F37, `f37root` at ea00492f. Built and reviewed (`plans/f37-review-p1.md`), decides from the diff alone. Lands after F25, with a gate that re-records the Critic cases.
- F7 with W4, `f7root` (11d04b18, f7fa55b8, cdd02498). Review p1 found 5 high (`plans/f7-review-p1.md`). Pass 2 runs now: a match on normalised ast nodes with no order, recall over precision, the frame 140 refusal restored to its old reach. It needs review p2 before the land.
- W3, `w3root` at d6a9efe6: the raw form first, the slash form last. Review p1 (`plans/w3-review-p1.md`) found 1 high, a form that is a SyntaxError for an escaped quote mark. Pass 1b runs now on my implementer.

Reports are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/6d9cf7e1-0faa-4156-bacb-f95ee6e7ec4f/scratchpad/` as `F25_pass1b_report.md`, `F37_pass1_report.md`, `F7_pass1_report.md` and `W3_pass1_report.md`. A one-case re-record helper is there as `rerecord_one.py`; run it from the gate worktree with `PYTHONPATH` set to that worktree.

## What I believe, and what to doubt

Doubt first F7's removal compare. Two passes missed real removals by text and order heuristics; pass 2's ast match is untested on a night. Doubt second the F25 shift-page door: three passes changed it, and the land gate found a Liaison regression the unit tests did not. Doubt third my count of root causes: 6 of 37 solved on the head, 4 in work, 27 left, plus one new cause under no fact, the `how_it_works` row that side work rewrites (night 171 read, section 4).

## First after the take

Land sprint 28 in order: F25 after pass 1e and its gate, F37, W3 after its review, F7 after review p2. Then sprint 29, F2 with F3 and F4, and onward by score. Night 172 waits for all of them.
