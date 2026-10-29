# Momentum note of session 0ce92518, peer name rota-21

Message rota-21 for anything this note withholds or you doubt. I keep the last of my context to answer, and I stop when you message the word released. Written on 2026-10-29 at about 09:00, near 270k, amended at the hand-off. Read `CLAUDE.md` first, then `python -m rota.tools.state --sid <your sid>`, then this note, then sprint 35 at the top of `plans/stack.md` and the status lines of frame 345 of 2026-10-29. Meta workflow.

## What this session did, 04:58 to the hand-off

Took frames 344, 345, 340, 324 and 341 from rota-62 at 04:58 on a clean context. Roman's ruling of 01:53 stands: nights stop, the 24 L3R cases are the loop, "maybe a Gemma trial".

- **The seam, frame 345.** Five passes landed on `rota/foundation`: df4b89b9 (passes 2 to 2c: the seat gets his words per line and gives one word, the revise and read-back cue doors read the match), ce02c29a (passes 3 and 3b: the word definitions, the conjoined subject, three cue doors out, `remove` on a page line lands as drop, `fixtures.capture` counts `ruled_refs`), dfec94a6 (pass 4: the Liaison seat on `gemma4:12b-it-qat`), c1e222b2 (pass 5: `keep` lands as approve, the landing writes one row per page line of a ref). The 24 cases: 1 of 24 on qwen at 00:00, 7 of 24 on qwen and 12 on Gemma at 08:00, 13 on Gemma at 08:5x, 12 to 13 at 7e11cd39 with the safe exclude form; refusals 199 to about 22. Reviews p3 to p7 in `plans/f345-review-p*.md`. The reads: `plans/seam-words-read-2026-10-29.md` (qwen), `plans/seam-words-gemma-read-2026-10-29.md` (Gemma), `plans/l1-landing-after-seam-2026-10-29.md`.
- **The model.** Gemma 6 against qwen's 1 before the seam build, 7 against 4 at df4b89b9, 12 against 7 at ce02c29a, and 35 of 41 Liaison L1 cases on both. The `local` profile's Liaison row and the Liaison case pins are Gemma. Roman can reverse it with one line in `rota/llm/profiles/local.toml`.
- **Closed on the records:** frame 340 (no pass line without a Reach line since the ruling of 2026-10-26), frame 324 (the partition is at head, the residue is the door refusing a bare first guess once), W5 (one reader `kind_of` serves both doors). Blocks in `plans/archive/stack-2026-10-29.md`.
- **Sprint 35 row 3 landed** at 346b266c: the three delete cases carry `expect_retired`, and the runner checks the retire.
- **Reads done, builds priced:** the Critic's review loop (`plans/critic-loop-read-2026-10-29.md`, 2 cycles, row 4), the `criteria.json` write (`plans/criteria-json-write-read-2026-10-29.md`, frame 346, waits on Roman).

## In flight at the hand-off, amended 10:2x

- **Passes 6 and 7 are done.** Pass 6 (a touch-line word becomes exclude of the one path his words name) was not landed: on "keep line 5 to X" it excludes the path he keeps. Pass 7 landed at 7e11cd39: the seat writes `exclude` with its paths, code checks each against the line, one landed row per path. The count tied at 12 to 13 of 24 and the ground was safety. The scratchpad holds `seam6_brief.md`, `seam7_brief.md` and the reports `seam6_report.md`, `seam7_report.md`, `seam7b_report.md`, `seam7c_report.md`.
- **The main register's re-record at 7e11cd39** runs from 10:2x: `l3r_main_7.txt` and `l1_landing_main_7.txt` in my scratchpad `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0ce92518-cd4c-46c5-8db2-374566fad335/scratchpad/`, with `rerecord7_start.txt` naming the exit codes when it ends. Its counts go on frame 345's status line; if that line is missing, read the two logs and write it. Re-record with `ROTA_L1=1 ROTA_NUM_CTX=12288` and `ROTA_MODEL` unset so the pins rule.
- **The next levers**, in order: fewer words in the table where his words make no split, revise against rewrite against contest (the Gemma words read, pair 4, and m61-m62's swings); `add` never given where no words reach the line (m58-m59, m75-m76, m47-m48); the team's note door, 5 refusals a run; a sentence-level matcher that binds each sentence to the numbers it holds, measured against the clause rules of `line_words` on the same 24. Then the Critic loop build, sprint 35 row 4. Each pass: branch from head, copy the register into the worktree, build, replay tests, the 24 and the 12 landing cases live on Gemma, review on Opus, land, re-record.
- **Variance.** A 3-run case at temperature 0 diverges only after a refusal, so a case swings 3, 0, 3 across passes on one refusal's timing (m44-m46, m136-m138, m61-m62). Read a fall against the earlier pass's runs before you call it the change's.

## What I believe, and what to doubt

- The measure is sound: cassette keys hash the system prompt, so a prompt change runs live; runs 2 and 3 at temperature 0 replay run 1 unless a refusal diverges them. A run of 20 seconds on a changed prompt means the pins were not forced: `ROTA_MODEL_FORCE=1` overrides a case's pin, and with `ROTA_MODEL` unset the pins rule.
- The 29 Liaison L1 cases outside landing replay at every head since their prompts did not change; a prompt change elsewhere makes them stale and the gate shows it.
- Frame 346's question to Roman is a departure from his ruling of 2026-10-17 that doors record; I recommend the refusal because the file is a fact, not a prediction. Do not build it before his word.
- The two expectations I re-judged (m53-m58 ask, m58-m59 add) stand; the status line of 08:3x holds the reasoning.
- Frame 341's count runs to 2026-11-10. Frame 344 is the umbrella of the root fixes and closes when sprint 35's rows do.

## Worktrees

No seam worktree stays. `rota_f345`, `rota_seam2`, `rota_f345x`, `rota_seam3`, `rota_seam4`, `rota_seam5`, `rota_seam6`, `rota_seam7`, `rota_w14`, `rota_w14c`, `rota_n175` are removed. `rota_seam` (seamroot, landed before this session) and `rota_g328` can go.
