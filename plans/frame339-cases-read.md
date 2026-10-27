# Frame 339: the two Developer cases red after the re-record on d495db74

Result first. `ACT-DV-edit-inside-the-function` is red because of the new door text. The commit now lands and returns the `[removals note]`, and 2 of 5 runs read that note as a reason to challenge the test (reasoned, from turn 2 below). `L1-DV-a-wordless-answer-on-a-right-red-test-is-carried-on` is red because of qwen3:8b on a new model load. Every failed run parts from the passing runs before the seat reads any door text that frame 339 changed (reasoned, from turn 0 below).

Sources (observed): a copy of `C:/Users/roman/rota_g328/tests/rota/cassettes.db` (mtime 2026-10-27 00:19) at `scratchpad/f339_cassettes.db`. The `case_runs` rows are from 2026-10-27 00:17 and 00:18, load `@249036`. The passing runs for comparison are from 2026-10-26 21:36 and 21:47, load `@249034`, with the same `system_hash`. The diff is `git diff b889c93d d495db74 -- rota/roles/api.py`.

## Case 1: ACT-DV-edit-inside-the-function

### What the case asserts

- Observed: `tests/rota/cases/l1_acts.yaml:184`. The base holds `confirm()` with no `default_on_eof` branch. The test `tests/test_confirm_eof.py` is red with `SystemExit: 1`.
- Observed: `expect: calls: [code.write, code.commit]`. `forbidden: writes: [tests, criteria]` and `calls: [msg.challenge_tester]`. The pass line is 4 of 5.
- Observed: the case pins `model: qwen3.5:9b`, and the register holds its runs under `qwen3.5:9b`. The case does not run on qwen3:8b. The gate's header line "on qwen3:8b" names the gate default, not this case.

### The 5 runs

- Observed: in all 5 runs, turns 0 and 1 have the same text as the passing runs of 2026-10-26 21:47. Turn 0 sends `code.write(path='src/ui.py', text="\n\ndef confirm(... default_on_eof=False): ... if default_on_eof:\n return default ...", start=7, end=-1)`. That write also drops `style` and `echo`. Turn 1 sends `code.commit(message='Fix EOF handling ...')`. Both expected calls are made by turn 1.
- Observed, the old door (21:47): the turn 1 commit was refused with "code.commit: a code.write in an earlier reply returned a note, and the tree still does not hold those lines. src/ui.py: This write drops 4 lines ...". The seat stayed on `code.write` and `code.commit`. 4 of 5 passed, and only run 3 sent `msg.challenge_tester`, after three refusals.
- Observed, the new door (00:17): the turn 1 commit lands. All 5 runs read this result before turn 2:

  > OK code.commit -> committed: True, head_commit: ..., touched: ['src/ui.py'], removals: ['src/ui.py::style: removal: `def style(text, fg=None):`, ...', 'src/ui.py::echo: removal: `def echo(message):`, ...']
  >
  > [removals note]
  > no criterion, request or ruling of the principal asks for these removals. The commit stands. The Architect is asked whether the removal was foreseen or a mistake before the batch merges; if you know it was a mistake, put the line back and commit

- Observed: the text comes from `code_commit` in `rota/roles/api.py`, `out["removals note"]`, added in frame 339. The `_note_routes` refusal did not fire in any run, because the commit came in the reply after the write and now lands.
- Observed, run 1 (pass), turn 2: "The code write dropped `style` and `echo` definitions which were not requested by the criterion or test. This is a mistake. I need to restore them". Then `code.write` and `code.commit`.
- Observed, run 3 (pass), turn 2: "I need to restore them to avoid unintended side effects, then re-run the test". Then `code.write`.
- Observed, run 2 (fail), turn 2: `msg.challenge_tester(refs=['c_c2d836', 'tst_22d54a'], ..., reason="the line `assert confirm(...) is True` of `tst_22d54a` fails with SystemExit(1), raised in `confirm()` at the `raise SystemExit(1)` statement")`. The reason quotes the wake's red result, which the commit result does not replace.
- Observed, run 5 (fail), turn 2: `msg.challenge_tester(..., quotes=[..., "def style(text, fg=None): ..."], reason="the line `def style(text, fg=None):` of `src/ui.py` was removed by the commit, but no criterion or test requested this removal")`. The seat sent its own removal to the Tester as a dispute.
- Observed, run 4 (fail), turns 2 and 3: "This is a mistake that needs correction" and `code.source`. Turn 4: "The current `src/ui.py` ... only contains the `confirm` function ... the file currently return[s]". Turn 5 sends `msg.escalate_architect`, and turn 6 sends `msg.challenge_tester`.
- Reasoned: all 5 runs part at turn 2, and turn 2 is the first reply after the new commit result. The old door kept the seat in a write loop, so the challenge route was rarely reached. The new door ends the commit with a note that names a judgement and a doubt, and it says nothing about the red test that the wake showed.

### Cause

- Reasoned: the red is the new door text, the `[removals note]` of the landed commit. The fixture is not the cause. The fixture builds a red test and a base file, and it does not depend on the old refusal. The seat's write that drops `style` and `echo` is its own act in both the old and the new runs.
- Reasoned: the model's reading has a part. 2 of 5 runs read the same note correctly. But the note gives the seat two facts with no step for the red test, and a 9b model fills the gap with the challenge route.

### What the sentence needs to say

- Observed, the text the seat read: "no criterion, request or ruling of the principal asks for these removals. The commit stands. The Architect is asked whether the removal was foreseen or a mistake before the batch merges; if you know it was a mistake, put the line back and commit".
- Reasoned, one sentence: the note must say that the commit holds the seat's fix and the test runs on it after the session, that the removal is the seat's own write and no fault of the test, and that the only next step is to put the lines back and commit or to end the session.

## Case 2: L1-DV-a-wordless-answer-on-a-right-red-test-is-carried-on

### What the case asserts

- Observed: `tests/rota/cases/l1_answers.yaml:176`. A Terminologist answer with no words wakes the Developer. The answer carries the glossary term "display currency", "always US dollars, with a leading $ and two decimals". The test asserts `format_amount(1234) == "$12.34"` and is red.
- Observed: `expect: calls: [code.write, code.commit]`. `forbidden: calls: [msg.challenge_tester]` and `writes: [criteria, glossary_terms, tests]`. The pass line is 4 of 5. The case runs on qwen3:8b.

### The 5 runs

- Observed: the three recording passes on load `@249036` (00:07, 00:08, 00:18) give the same pattern, `00011`. The six passes on loads `@249032` to `@249034` (2026-10-26 17:55 to 21:36) give `11011`. All nine passes have `system_hash` `5eb91cf723d4f143`.
- Observed, runs 1 and 3 (fail), turn 0: `TOOL: code.commit(message="The criteria and glossary term 'display currency' have been resolved. No code changes are needed.")`. Turn 1 ends the session. No write is made.
- Observed: the turn 0 user text of run 1 (cassette row 62808) and run 3 (row 62818) is the same text. It holds the wake, `criteria.load` and `glossary.lookup`. It holds no door text of frame 339. Run 1 in the 21:36 pass read the same system text and sent `code.source` at turn 0, and it passed.
- Reasoned: the cassette family of run 1 holds one turn 0 row, and the re-record wrote it over the old row. So the input at turn 0 did not change, and the output changed with the model load.
- Observed, run 2 (fail): turns 0 to 4 are the same as run 5 (pass). Turn 4 writes `format_amount` alone with `start=0, end=-1`. The write returns "[dropped] This write drops 7 lines of the old file, from `ELLIPSIS = chr(8230)`; write the whole file again with those lines kept." This write note is not changed by frame 339.
- Observed, run 2, turns 5 to 7: three identical `code.write` calls with `singular + 's'` inside a single-quoted `text`. Each returns "a quote inside text ended it early ... Put the value of text between triple quotes". The runner ends the session with "repeated its previous turn verbatim twice; ended". No `code.commit` is sent, so the commit door is not reached.
- Observed, run 5 (pass), turn 6: the same write with `singular + \"s\"`, then `code.commit` at turn 7.
- Reasoned: run 2 parts from run 5 at turn 6 on a quoting slip of the model. The seat read no text that frame 339 changed before it parted.

### Cause

- Reasoned: the red is the model, qwen3:8b on load `@249036`. Runs 1 and 3 part at turn 0 on an input that is the same as the input of the passing runs. Run 2 parts at turn 6 on the quoting refusal and never reaches the commit door. The new route text is not read in any failed run, and the fixture did not change.
- Reasoned: question 3 does not apply to this case.
