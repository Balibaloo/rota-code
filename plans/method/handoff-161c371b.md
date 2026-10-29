# Momentum note of session 161c371b, peer name rota-62

Message rota-62 for anything this note withholds or you doubt. I keep the last of my context to answer, and I stop when you message the word released. Written on 2026-10-29 at about 01:30, near 300k, amended at 04:55 near 345k. Read `CLAUDE.md` first, then `python -m rota.tools.state --sid <your sid>`, then this note, then sprint 35 at the top of `plans/stack.md` and the status lines of frames 344 and 345 of 2026-10-29. Meta workflow.

## What this session did

Took frame 344 from rota-99 at 00:11 with frames 340, 324 and 341, and took frame 345 at 00:17 on the sender's plan and Roman's go of 2026-10-28 14:45.

- Night 175 read: `plans/night175-read.md`. 2 of 3 merged. Walk 3 stopped by rule: his five deletes of c_2 and c_3 landed as rulings, none retired a criterion. Two causes, both read: the one reader `_dropped_line` read the act `drop` only (W14), and the door `_faulted_approve` refused 12 right calls of 16 on five nights, each ending in a ruling against his words (`plans/w14-faulted-approve-read-2026-10-29.md`).
- W14 landed on `rota/foundation` at 5bc46206: `landing.md` says a delete of a page line is `drop` with kind `row`; `_dropped_line` reads `remove` with kind `row` as a drop, and a clarify drop with no line as the row itself. Reviews p1 to p3 in `plans/w14-review-p1.md`, READY. The three new `l1_landing` cases are unrecorded.
- Frame 345 landed at 0b7fcc3b: 24 real pages with his real replies, judged in the Fable seat (`plans/l3-rulings-cases-2026-10-29.md`, his read owed), the case file `tests/rota/cases/l3_rulings.yaml`, the source `tests/rota/cases/sources/l3_rulings_judged.yaml`, the runner `tests/rota/test_l3_rulings.py`. Reviews in `plans/f345-review-p1.md`, READY at p2. **The baseline on the head: 24 of 24 cases wrong, 71 of 72 runs, 199 refusals** (`l3r_baseline.txt` in my scratchpad, the histogram on frame 345's status line of 01:2x). The register that holds the 92 runs is the worktree `rota_f345`'s `tests/rota/cassettes.db`, not the main one.
- Sprint 35 is at the stack's head, seven rows.

## Roman's ruling of 2026-10-29 01:5x, the plan

"Instead of faffing with nights try to develop the right behaviour in the liaison with test cases, and maybe a Gemma trial." Nights stop. The 24 cases are the loop; sprint 35 is amended to it at the stack's head. He also ruled that his read of the 24 judged lines is not a condition ("Can you not judge it?"). The general solution is read, `plans/seam-general-solution-2026-10-29.md`, option (d): code matches each page line to the words of his that name it and shows the match to the seat; the seat gives one word per line; code fills the quoted words and the kind. Frame 345 pass 2 builds it in `rota_seam2` on branch `seam2root`, brief `seam2_pass1_brief.md` in my scratchpad. Its measure: the 24 cases before and after, 1 of 24 today. The Gemma trial, `gemma4:12b-it-qat` forced on the 24 cases, writes `l3r_gemma.txt` in my scratchpad; the count beside qwen3:8b's decides the seat's model.

## Results of 04:5x, after the plan

- **Gemma trial: 6 of 24 right**, qwen3:8b 1 of 24 on the same head (`l3r_gemma.txt`, frame 345 status of 04:51). Gemma writes long and the output budget cut many replies. The model is half the answer; a Gemma seat with the seam build is the next measure to run.
- **Pass 2 built at 27291602 on `seam2root`** in `rota_seam2`: 1 of 24 to 3 of 24, runs 3 of 72 to 8 of 72, n174-m53-m55 fell to 2 of 3 and stays right (frame 345 status of 04:52). The review p3 runs on Opus to `plans/f345-review-p3.md`. Land it if READY: merge `seam2root` into `rota/foundation`, then the touched files in replay, then re-record the 12 `l1_landing` cases. After the land, the leading refusals are revise-rewrites 33 and read-back 28, both meaning checks; the next pass removes them and measures again. The open questions the build raised: `remove` on a page row stays `remove` (W14 reads it as a drop, so the ruling lands right); the revise example may cause the top refusal; m80's "I never gave an answer about lines 1 to 5" is matched to "drop it".

## In flight at the hand-off

- **Pass 2b of frame 345** builds in `rota_seam2` on `seam2root` from 27291602, after review p3 found the match wrong in 4 of 24 replies and the lost run caused by the one-word form (`plans/f345-review-p3.md`, frame 345 status of 04:5x). Its brief and its report are `seam2_pass2b_brief.md` and `seam2b_report.md` in my scratchpad, `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/161c371b-f6a2-4d73-aebc-bae776885ab7/scratchpad/`. Land when its 24-case count is at or above 3 of 24 with n174-m53-m55 back at 3 of 3: review the fix commit on Opus against the review's points 1 to 4, merge `seam2root` into `rota/foundation`, run the touched files in replay, re-record the 12 `l1_landing` cases live. Then the next pass takes the revise-rewrites and read-back checks out and measures. Then the Gemma seat on the seam build, the same 24 cases.
- **The door-off experiment** runs in `rota_f345x` on branch `f345x`: `_faulted_approve` skipped, the 24 cases live, the comparison to `plans/f345-faulted-approve-off-2026-10-29.md`. Its result decides whether the door goes: cases right up, no right run lost. If it reads better, the removal is a pass on a branch from head with the three right catches of the door (night 170 s222, night 174 s100 and s93, see the reach read question 2) as the risk, then the 24 cases again.
- **The main register holds none of the 24 L3R recordings and none of the three new landing cases.** A live re-record in `D:/repos/rota`: `ROTA_L1=1 ROTA_MODEL=qwen3:8b ROTA_NUM_CTX=12288 python -m pytest tests/rota/test_l3_rulings.py -q -s -n0`, 15 minutes, with no `ROTA_PROFILE`, which is what `gate.py` replays. Then the gate with re-records for the landing cases, in `rota_g328` moved to head.
- The touched-file run after the two lands runs in the main repository (background task of this session; its result is on frame 344's next status line, or run it again: the test files that name `_dropped_line`, `criteria_page_acts`, `criteria_retire`, `tests_retire`, `landing`, `run_sampled`, `page_lines` or `test_l3_rulings`). One known red, `test_scene_two_batches.py::test_a_right_call_lands[...test_templates.py as an encode]`, red before the lands.
- **Night 176** after the gate: night 1 for W14, night 2 for the seam, W11 and W10. Launch from a copy of `.rota/launch_night175.sh` with the night label changed to 176; its read copies `n175_read_brief.md` in my scratchpad.
- Frames 340 and 341: their mechanisms are at head; only their count clauses are open, 341's over two weeks from 2026-10-27. Frame 324: the first half holds at 0 on four nights; the second half, the Architect's bare symbol, is sprint 35 row 6.

## What I believe, and what to doubt

- I believe the 24 judgements are right on his words, and I wrote them alone. Doubt them where a case expects an act kind: `exclude` of a path for "remove the tests from what you expect to touch", `rewrite` for "has to touch X", `drop` for a criterion he deletes. A seat may read those right and still miss my kind. The cases that read wrong with zero refusals (the clarify, m75-m77 run 3) show the seat's own reading differs, not only the doors.
- Doubt my brief's own-id guard on W14: the reach read's section 1.5 reasoned it, I wrote it as a fact, and the review found it blocked the night's real rows. The land has no guard on the target.
- Doubt the order of removal: `_faulted_approve` goes first by the night count, 12 wrong of 16, but in the baseline the read-back door (28) and the act-span door (45) refused more. Roman's direction says fewer meaning doors and deeper cases; it does not name which door.
- The times inside my status bodies come from `date` in the same command; the tool's stamps agree.

## Worktrees

`rota_f345` holds the 92-run register, keep it until the main register is re-recorded. `rota_f345x` is the experiment. `rota_w14` is landed and can go. `rota_n175` holds night 175's untracked files and can go with `--force`. I removed `rota_w11`, `rota_rw11`, `rota_w10`, `rota_rw10` and `rota_n174` at 00:20.
