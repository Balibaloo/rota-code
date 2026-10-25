# Frame 306: the two Tester reds, read without a model (2026-10-25)

## Verdict

Neither red comes from frame 306 row 2 or frame 318. The two cases fail the same
way at 1d53d881 and at 18e0df6b. Both commits compose byte-equal prompts, system
and user, and both replay the same cassettes to 3 of 5 and 0 of 5. The register
holds no pass of either case at 1d53d881. The reds began on 2026-10-24 at 14:08
with the three Tester prompt commits 05f562e1, eac24df0 and d392053a (base.md,
challenge.md, tests_missing.md). Those edits moved the instruction hashes, the
suite re-recorded the cases live at 18:28 and 19:32, and the new recordings fail.
This is not variance: the replay is deterministic.

## What the probes showed

1. Cases: `tests/rota/cases/l1_acts.yaml:131` (tick tests_missing, expects 5 tests
   writes, pass 4 of 5) and `tests/rota/cases/l1_tester.yaml:551` (challenge m291,
   expects a tests write with a `version_option(` span, pass 3 of 5). `test_l1.py`
   composes the brief, pins `qwen3.5:9b`, runs `run_sampled`, and records each
   run against `pins.with_prompt(instructions)`.
2. System text (`fixtures.system_text_for`) at both commits: sha1 951d16c40d and
   c091afb881. Equal. Turn-1 user text (a capture backend under `run_case`):
   sha1 7436b1957b and fffa722133. Equal. Every cassette key hits a recording.
3. Replay through `run_case` with `ReplayOnlyBackend` at both commits: five-criteria
   runs 1 and 3 fail with "got 2" and "got 4", 3 of 5. The challenge case fails
   5 of 5: the test body has no `version_option(version=` span. Identical at both.
4. Register history (`case_runs`, live = 0 on every row since the re-record):
   five-criteria 5 of 5 under hash 0f282ba9 until 2026-10-21, then fed271d1 from
   2026-10-24 18:28 at 3 of 5 on every run. Challenge 4 of 5 under a145776f until
   2026-10-21, then df4e4d60 from 2026-10-24 19:32 at 0 of 5 on every run.
5. The diffs 1d53d881..18e0df6b touch `tests.retire`, `live_tests`, the SQL of
   `tests_missing`, the done check of `tests_triage`, `red_before`, and the page
   numbering. None touches `tests.encode`, the two wakes, or the two mode files.
   `answer.md` and `answer.tools` changed, and neither mode reads them.

## Cause and fix

- Five-criteria: the Tester prompt edit of 2026-10-24 14:08 (base.md and
  tests_missing.md). Under the new words the model calls `tests.triage` on one
  criterion in two runs of five.
- Challenge: the same edit (base.md and challenge.md). Under the new words the
  model keeps the night's test shape in all five runs.
- Fix: open the reds on the 14:08 frame, not on 306 or 318. Read the two
  transcripts under the new words, revise the prompt or the case, then re-record
  live. The claim "pass at 1d53d881" has no row in the register.

## Probes

`sys_render.py`, `user_render.py`, `replay.py`, `hashes.py`, `old/`, `new/` in
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/48122667-6b95-4100-a43b-30ec9c6540dd/scratchpad/`. Register read-only. No model ran.
