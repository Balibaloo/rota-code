# Night 103: the read

Night 103 ran on 2026-10-01 from a seam pair: night 101's database at
its end and batch `bg_1` at `e1f99723`. The launcher is
`.rota/launch_night103.sh`, the checkout `C:/Users/roman/rota_night103` at
`ae9abd0`. Run 1 at 09:48 stopped on a missing column, run 2 at 09:52
merged `bg_1` at 09:54. The database is `.rota/clickI_night103.db`, the
print `.rota/night103_report.txt`. The read ran on Opus from the print
with five queries, 55.2k on the harness line (observed: 2026-10-01).
Meta workflow throughout; the facts below are about the rota workflow.

## Sessions after the seam

- s170, Critic, `tick:review` at `e1f99723`, two turns. The wake pre-ran
  `code.read`, `criteria.load` and `tests.load`. The first prompt is
  22,729 characters, the system prompt 5,212. The markers stand in the
  order `[code.read]` at 161, `[criteria.load]` at 1762, `[tests.load]` at
  2589. The criteria are complete, three rows. The tests result is cut by
  the result cap: `CUT the result: 448,106 of 468,106 characters are not
  shown.` The string `echo_json` is absent from the visible tests part, so
  the rows `inh_023c4d91`, `92` and `93` never reached the Critic. The
  Critic claimed all three criteria encode and emitted `pass` (observed:
  `turns` and `tool_calls` of s170).
- The verdict row at `e1f99723`: `pass`, no failed criterion, an empty
  reason.
- s171, Architect, `tick:structural_review`. Calls: `batches.expect`,
  `code.diff`, `code.probe`, `findings.load`, `model.consult` twice,
  `findings.find` four times. Three findings f1 to f3 on `k0`, all
  satisfied. The fourth call repeated f1's grain and was refused as
  unchanged. At turn 5 the runner said the seat wrote tool results into
  its own reply. The session ended with that account. No finding blocked
  the merge.
- The merge: `bg_1` merged at `e1f99723`, 37 `test_runs` rows at that
  commit, all pass, attempt 14. Click's main is `a4dbf3f`.
- Neither s170 nor s171 ran past a completion line.

## What it says

- Frame 104 holds: the seam walk started one minute after launch.
- Frame 101 has a second cut beside the window's: the result cap on
  `tests.load` hides the batch's own tests behind 37 inherited ones.
- Frame 88's ruling was not exercised: the Critic passed without seeing
  the tests, so the letter of the criterion was never checked against a
  test.
- The Architect writing its own tool results is a shape frame 98's door
  does not cover. It cost one turn and no write.
