# Momentum note of session b3bc8a66, peer name rota-33

Message rota-33 for anything this note withholds or you doubt. I keep the last of my context to answer, and I stop when you message the word released. Written on 2026-10-28 at 00:2x, amended at 00:5x at 345k with five agents live. Read `CLAUDE.md` first, then `python -m rota.tools.state --sid <your sid>`, then this note, then the stack's head down to Sprint 28 and frame 344's status lines of 2026-10-27 19:41 onward. Meta workflow.

## Roman's ask

Every fix of sprints 28 to 31, W3 and the `how_it_works` cause lands before night 172, with a gate on each (ruled: 2026-10-26 23:4x and 2026-10-27 19:32, on frame 344). The gate is the only check besides a review. No night runs until the head holds them all.

## The gate rule, ruled 2026-10-28 00:5x

Partial gates on the touched test files per land, one full gate on the head before night 172 (ruled: Roman, in the terminal). The gate on 695e3beb is the last full gate until that one.

## What is on the head, amended 2026-10-28 01:3x

`rota/foundation` at 475e083b holds F19, F20 with F21, F31, F25, F37, W3, F7 with W4, F23, F4, F5, F16, the `how_it_works` gate and heading, W8 and F1. 18 of 37 facts. The five pin files pass on the head, 71 of 71. F6 is closed by a probe. Frame 344's status lines from 2026-10-27 19:41 to 2026-10-28 01:3x hold each build, review and land.

## Left in worktrees

- F22, `f22root` at 794c2b01, PARTIAL: the ast pin lists 22 functions nobody has read, under a pass 2 note in `ALLOWED` of `tests/rota/test_f22_table_of.py`. Pass 2 reads them, moves or justifies each, then F22 lands on touched files.
- The land gate worktree `C:/Users/roman/rota_g328`, branch `land28` at 1fab56ca, is behind the head by F1. Sync it before the full gate.
- Six recorded cases owe a re-record on their recorded model before the full gate: ACT-DV-edit-inside-the-function, L1-AR-judge-a-stray-foreseen-or-a-mistake, L1-CR-fail-names-its-criterion, L1-CR-finish-the-review-with-the-answer-in-hand, L1-DV-a-wordless-answer-on-a-right-red-test-is-carried-on, L1-DV-fix-the-code-not-the-test. The gate re-records on qwen3:8b, and the Critic and Developer cases are recorded on qwen3.5:9b, so run their re-record with `ROTA_MODEL=qwen3.5:9b`.

## Not started

F2 with F3 (the `_line_reading` seam, after F25 lands, same door), F15 (`request_of`, a seam, what owns a description needs a decision), F35 (`predicted_files`, after F7 lands), F8 to F14, F18, F24, F26 to F29, F32, F33 and frame 233's `done_reason` residue. Each has a proposal in `plans/rootfix-audit-2026-10-27-a.md` or `-b.md`. Price them from there. Every build owes a one-reader pin test, by the status line of 19:4x on frame 344.

## What I believe, and what to doubt

Doubt first the land order: ten branches touch `rota/roles/api.py`, so each land after the first needs a rebase and a gate, and a gate takes 15 to 50 minutes under load. Doubt second F1: its seeds moved 26 test files by a sweep, and the night tools read the verdict rows now. Doubt third my own verification of the day: half b's scores used total readers, so F2 and F4 are the biggest gaps by own-rule readers, and F2 is still unbuilt. Doubt fourth the `how_it_works` gate: the read's doubt 3 asks whether Roman wants the account to grow with each request. No is the recommended answer, and the question is not yet put to him.

## Questions for Roman, not yet asked

1. The account row: should a later request be allowed to reword the approved account, or does it stay as onboarding wrote it until he changes it? Recommended: it stays. Part A of the `how_it_works` build enforces that.

## First after the take

Read `gate_657c559c.txt`. If the F25 gate is clean, fast-forward `rota/foundation` to the land28 merge and land the next branch. Then collect each in-flight report as it arrives, review what has no review, and land in the order above.
