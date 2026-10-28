# Momentum note of session b3bc8a66, peer name rota-33

Message rota-33 for anything this note withholds or you doubt. I keep the last of my context to answer, and I stop when you message the word released. Written on 2026-10-28 at 00:2x, drafted at about 300k with eleven agents live. Read `CLAUDE.md` first, then `python -m rota.tools.state --sid <your sid>`, then this note, then the stack's head down to Sprint 28 and frame 344's status lines of 2026-10-27 19:41 onward. Meta workflow.

## Roman's ask

Every fix of sprints 28 to 31, W3 and the `how_it_works` cause lands before night 172, with a gate on each (ruled: 2026-10-26 23:4x and 2026-10-27 19:32, on frame 344). The gate is the only check besides a review. No night runs until the head holds them all.

## What is on the head

`rota/foundation` at d267b8cc holds F19, F20 with F21, F31. F6 closed by a probe, `plans/f6-probe-2026-10-27.md`. Frame 280 has a close line under the F23 ruling.

## Built, waiting for a land gate, by worktree and branch

Each has a review or a pass in flight. The land order is the order below, one at a time in `C:/Users/roman/rota_g328` on branch `land28`, with `python -m rota.tools.gate --rerecord-now`. The gate on 657c559c (F25 pass 1e merged) was running from 23:28, output to `gate_657c559c.txt` in this session's scratchpad. Read it first. Do not land 2bbace14 alone, land 657c559c.

- F25, `f25root` at 6a5d0850 (pass 1e). Reviews p1 and p2 in `plans/f25-review-p1.md`. One regression at the last gate: `L1-LI-a-separate-request-is-later` 4/5 to 1/5. Pass 1e answered it. The gate decides.
- F37 residue, `f37root` at ea00492f. Reviewed, `plans/f37-review-p1.md`. Lands with a gate that re-records the Critic cases.
- W3, `w3root` at 6a4a5396 (pass 1b closed all four findings). Ready.
- F7 with W4, `f7root` at aae59d4b (pass 2). Review p2 in flight to `plans/f7-review-p2.md`. Stale: `L1-AR-judge-a-stray-foreseen-or-a-mistake`.
- F23, `f23root` at 6e9a9f76, pass 1b in flight on the review's 1 high and 7 low (`plans/f23-review-p1.md`).
- F22, `f22root` at e33bc142, pass 1b in flight on 2 high and 4 low (`plans/f22-review-p1.md`): `table_of` returns every table that holds an id, callers narrow by scope.
- F4, `f4root` at b2003ad9, pass 1b in flight on 1 high and 4 low (`plans/f4-review-p1.md`): no DROP VIEW outside a transaction.
- F5, `f5root` at 461cc04b. Review p1 in flight to `plans/f5-review-p1.md`.
- F16, `f16root` at 7da194de, pass 1c in flight: one list of the verbs that owe a reply. Needs a review after.
- F1 with the F20 residue, `f1root`: c41cdffb (F20 residue, green, two pin tests) and WIP 11ead50f (F1), pass 1b in flight fixes 58 test seeds. Needs a review after.
- `how_it_works`, `hiwroot` at 2fb92e9c, the build of `plans/night171-how-it-works-read.md` section 6, report pending. Needs a review.
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
