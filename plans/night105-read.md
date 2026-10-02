# Night 105, the read

Night 105 ran from a worktree at 4f56050, launched 2026-10-02 02:53, ended 04:03 with "Stuck. The team gave up on: tests_failing for bg_1." NIGHTCOUNT: 202 sessions, 672 turns. Read on Opus from `.rota/night105_report.txt` with 12 queries on `.rota/clickI_night105.db`, 94.8k on the harness line (observed: 2026-10-02 04:10). Rota workflow unless marked.

## 1. Frame 100, the window keeps reads

The phrase "dropped to fit the window" is in 43 turns in 7 sessions. The print says 20 turns in 7 sessions, which is wrong. Night 101 had 275 of 879.

| session | turns |
|---|---|
| `s131` developer | 14 |
| `s32` vision_keeper | 11 |
| `s24` vision_keeper | 8 |
| `s87` critic | 4 |
| `s171` architect | 3 |
| `s69` architect | 2 |
| `s40` | 1 |

No Developer read the same span more than twice.

| session | `code.source` calls | spans read more than once |
|---|---|---|
| `s131` | 10 | 1: `src/click/utils.py` 346–390, twice |
| `s141` | 6 | 0 |
| `s142` | 6 | 0 |
| `s143` | 6 | 0 |

`s141`, `s142` and `s143` made the same six reads in the same order, once each. "served three times this session" fired 0 times. A different door, "asked three times this session and the answer has not changed", fired in Vision Keeper sessions only: `s28`, `s32`, `s115`, `s151`.

## 2. Frame 106, the Architect's dead end

No Architect woke on an exhausted trigger. Six Architect message wakes: `s110`, `s125`, `s127` on a relay; `s150`, `s175`, `s200` on a deliver. `s150` and `s175` sent `msg.challenge_vision_keeper`. `s200` sent `msg.report_liaison` twice. The bg_1 dead end went by quarantine to the Liaison: `s144` presented it, `s145` recorded the approval. `s1` handled the other quarantined wake, "constraint_zero for the run, 3 attempts".

## 3. Frame 107, the Critic's doubt

No Critic sent a question to the Terminologist. No Critic emitted a verdict: all 16 Critic sessions woke on `tick:challenge`. Three sessions sent `challenge.break` twice: `s81`, `s174`, `s198`. `s174`'s first break returned ERROR. `s80` ended with no uphold and no break. `s198` read `items.py`, which does not exist.

## 4. The stall on bg_1

`s131` (developer, `tick:batch_start`): first `code.write` ERROR, the rewrite dropped `_get_binary_stream` and `_get_text_stream`; a span write landed; "OK code.commit -> committed: true, head_commit: 7fef346156"; a second commit "nothing changed"; a `code.write` to `tests/test_utils/test_echo.py` ERROR, a quote ended `path` early; ended with `code.commit('echo_json already meets criteria')`. Then "bg_1: 34 test(s), 0 not passing".

Testers `s132`, `s138`, `s140` encoded three tests. Then "bg_1: 37 test(s), 3 not passing".

`s141`, `s142`, `s143` (developer, `tick:tests_failing`, "attempt 2", refs `["bg_1"]`): 13 identical calls each, no write, no commit. Turns 4 to 7 of each tried `msg.challenge_tester` on `inh_echo_json_03`, and every try failed with "unterminated argument list: a quote inside a quoted argument ended the string early, or a bracket is unbalanced". The seat put the whole test body in `quotes=`, the body holds `'` inside `"`, and the string closed before `round_no=0` (observed: `s141` turn 4). The tick reached attempts=3, quarantined=1, and `s144` reported it.

The CYCLE line was a true repeat: the same wake key and the same tree at `7fef346`; the first prompts differ only in "attempt N of 3" and the CUT count. The print's "repeats: 0" is wrong.

The three failing tests, `inh_echo_json_01`, `_02`, `_03`, call `CliRunner().invoke(echo_json, ...)` on a plain function and fail with `KeyError: 'prog_name'`. No Developer opened the test files with `code.source`; the wake's `tests.load` carried the bodies, cut. Each Developer read `src/click/testing.py` 314–800 and `src/click/utils.py` 688–701. The brief says "Do not edit the test."

## 5. The "made up" count

The invented thing is a fake tool result: the model writes `OK <tool> -> ...` in its own completion. 12 Vision Keeper sessions: message wakes `s115`, `s161`, `s166`, `s177`, `s183`; `tick:reconcile` wakes `s22`, `s24`, `s28`, `s32`, `s33`, `s36`, `s43`.

| tool | fake lines |
|---|---|
| `code.probe` | 52 |
| `code.source` | 12 |
| `problem.assert` | 11 |
| `decisions.author` | 9 |
| `decisions.search` | 9 |
| `ledger.log` | 7 |
| `problem.prioritize` | 1 |

Main shape: the Vision Keeper copies the runner's de-duplication memo, "OK code.probe -> unchanged since you asked earlier this session." Second shape: success results with invented ids, "OK ledger.log -> {"id": "l_215b1f3307"}" in `s22`. Other roles with the sign: critic `s76`, `s80`, `s81`, `s174`; developer `s131`; terminologist `s168`, `s190`; architect `s128`, `s171`.

## 6. Past the completion line

20 sessions made turns at or after "Your work for this session is complete": liaison 10, terminologist 5, architect 3, tester 2. The print's capped list shows 10.

## 7. Other facts

bg_2 and bg_3 never started; walks 2 and 3 ended on the same bg_1 stall. `s170` (architect) grouped `confirm_with_default_on_eof` into bg_1 to bg_5; one `batches.group` returned "already batched as bg_2". Dangling pointers, 12 turns in 4 sessions, not traced.
