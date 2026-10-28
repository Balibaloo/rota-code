# Momentum note of session b3bc8a66, peer name rota-33

Message rota-33 for anything this note withholds or you doubt. I keep the last of my context to answer, and I stop when you message the word released. Written on 2026-10-28 at 00:2x, amended at 00:5x at 345k with five agents live. Read `CLAUDE.md` first, then `python -m rota.tools.state --sid <your sid>`, then this note, then the stack's head down to Sprint 28 and frame 344's status lines of 2026-10-27 19:41 onward. Meta workflow.

## Roman's ask

Every fix of sprints 28 to 31, W3 and the `how_it_works` cause lands before night 172, with a gate on each (ruled: 2026-10-26 23:4x and 2026-10-27 19:32, on frame 344). The gate is the only check besides a review. No night runs until the head holds them all.

## The gate rule, ruled 2026-10-28 00:5x

Partial gates on the touched test files per land, one full gate on the head before night 172 (ruled: Roman, in the terminal). The gate on 695e3beb is the last full gate until that one.

## What is on the head

`rota/foundation` at 552490b1 and after holds F19, F20 with F21, F31 and F25. F6 closed by a probe, `plans/f6-probe-2026-10-27.md`. Frame 280 has a close line under the F23 ruling.

## Built, waiting for a land gate, by worktree and branch

Each has a review or a pass in flight. The land order is the order below, one at a time in `C:/Users/roman/rota_g328` on branch `land28`, with `python -m rota.tools.gate --rerecord-now`. The gate on 7a6c5140 (land28 synced to 552490b1, plus f37root ea00492f and w3root 6a4a5396) runs from 00:33, output to `gate_7a6c5140.txt` in this session's scratchpad. Read it first. If clean, merge 7a6c5140 into rota/foundation with --no-ff. If red, bisect by branch.

- F37 residue and W3: on the running gate.
- F7 with W4, `f7root` at 30d0de73 (pass 2b, review p2 READY, `plans/f7-review-p2.md`). Ready for the gate. Stale: `L1-AR-judge-a-stray-foreseen-or-a-mistake`.
- F23, `f23root` at ecb413d8 (pass 1b closed the review). Ready for the gate.
- F22, `f22root` at 794c2b01 (pass 1b). PARTIAL: the ast pin lists 22 functions nobody has read, under a pass 2 note in `ALLOWED`. A pass 2 reads them before the land, or the land goes with the 22 named as residue.
- F4, `f4root` at e1cee346 (pass 1b closed the review). Ready for the gate.
- F5, `f5root` at e089d53a (pass 1b closed the review). Ready for the gate.
- F16, `f16root` at 99964faa, pass 1d in flight on review p1's 2 high and 4 low (`plans/f16-review-p1.md`). Its night count is frame 320's, not W17's.
- F1 with the F20 residue, `f1root`: c41cdffb (F20 residue, green) and 33e3ae49 (F1), pass 1c in flight: landed rows on every path under source `landed`. 9 reds to clear. Needs a review after.
- `how_it_works`, `hiwroot` at 575e09b5, pass 1c in flight on review p1 (`plans/hiw-review-p1.md`): a contested wake on the row he contested is exempt from the gate.
- W8, `w8root`, in build from `plans/night170-w8-read.md` section 6. Needs a review. F17 closes into it.

Reports are in this session's scratchpad, `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b3bc8a66-bd69-4749-a050-07bdd1893c24/scratchpad/`, as `F<n>_pass1_report.md` and the like. The common brief for every implementer is `common_brief.md` there. It forbids `git stash`: the stash is one list across worktrees, and three builders' pops crossed on 2026-10-27 night.

## Not started

F2 with F3 (the `_line_reading` seam, after F25 lands, same door), F15 (`request_of`, a seam, what owns a description needs a decision), F35 (`predicted_files`, after F7 lands), F8 to F14, F18, F24, F26 to F29, F32, F33 and frame 233's `done_reason` residue. Each has a proposal in `plans/rootfix-audit-2026-10-27-a.md` or `-b.md`. Price them from there. Every build owes a one-reader pin test, by the status line of 19:4x on frame 344.

## What I believe, and what to doubt

Doubt first the land order: ten branches touch `rota/roles/api.py`, so each land after the first needs a rebase and a gate, and a gate takes 15 to 50 minutes under load. Doubt second F1: its seeds moved 26 test files by a sweep, and the night tools read the verdict rows now. Doubt third my own verification of the day: half b's scores used total readers, so F2 and F4 are the biggest gaps by own-rule readers, and F2 is still unbuilt. Doubt fourth the `how_it_works` gate: the read's doubt 3 asks whether Roman wants the account to grow with each request. No is the recommended answer, and the question is not yet put to him.

## Questions for Roman, not yet asked

1. The account row: should a later request be allowed to reword the approved account, or does it stay as onboarding wrote it until he changes it? Recommended: it stays. Part A of the `how_it_works` build enforces that.

## First after the take

Read `gate_657c559c.txt`. If the F25 gate is clean, fast-forward `rota/foundation` to the land28 merge and land the next branch. Then collect each in-flight report as it arrives, review what has no review, and land in the order above.
