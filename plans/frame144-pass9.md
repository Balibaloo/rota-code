# Frame 144, pass 9: scene 6, the invariants, and three rows of night 126

Meta workflow. Pass 9 of frame 144, the night databases are not a test tier. An implementing agent on Opus wrote this record on 2026-10-06, on the branch `f144p9` in the worktree `C:/Users/roman/rota_f144p9`, from cc506d32. No file under `rota/` outside `rota/testkit` and `rota/tools/invariants.py` changed.

Commit: 1383bd2a (code and tests). This record is the next commit.

## The design

The pass builds three parts of the design (`plans/frame144-design.md`, section 1):

1. Change 3, scene S6: the large module, and item 5's rule on four delivery wakes at `num_ctx` 16384.
2. Change 2, the invariants I1 to I9, as one checker. The checker runs on every scene's end in the gate, and on a night's database by path.
3. Three catalogue rows from night 126 (`plans/night126-read.md`, sections 5, 6 and 9). Two are built. One is skipped, for the reason under "The catalogue rows".

Every scene runs as pass 8 made it: each step is one iteration of `probes/walk.py`. The new scene adds no seam.

## The scene

`scenes.large_module` builds S6 through the real ops. Its steps are the walk's steps (observed: the probe `p9/s6probe.py`, 2026-10-06):

1. `_commit_ledger` commits two files on the scene's copy of the sample repository before the onboarding reads it. `src/billing/ledger.py` holds 1,000 lines, a `__future__` header, 199 rate functions, and `late_fee` at line 900. `tests/test_ledger.py` is a project test of two rates. The template does not change, so no recorded case of the sample goes stale.
2. The survey, then item 1, "charge a fee on a late payment", to batch b1 with one criterion on `late_fee`.
3. `developer|tick:batch_start|b1` writes the module whole with a wrong fee and a cent added to every rate, and commits. The project test goes red. The diff holds 199 changed lines.
4. Three empty fix sessions quarantine the fix key, and the Liaison reports it. The loop picks the fix wake before the Tester's wake, as night 121 did (scene `two_batches`).
5. `tester|tick:tests_missing|b1` encodes `test_late_fee.py`. Its new row lifts the key, and the harness runs it red.
6. `developer|tick:tests_failing|b1` is the fix wake that frame 134 names: the batch's red test, the project's red test and the large diff. The Developer writes the rates back and the right fee. The harness runs green.
7. The Critic claims that the test encodes c1 and fails the batch. `developer|tick:verdict_failed|b1` ends with nothing done. The scene ends there.

Every session of the scene runs at 16384 (`Scene.pins`, `NIGHT_PINS`). `scenes.wake_prompt` reads the first turn of the last session on a wake: the prompt that the runner gave the seat, after the cut. `scenes.blocks` reads the pushed blocks of a prompt. A block is whole when a header follows it, or when no cut note ends the wake.

The four wakes on today's tree (observed: `p9/s6probe.py`, 2026-10-06):

| Wake | Uncut, characters | Budget | Cut | Blocks after the cut |
|---|---|---|---|---|
| `batch_start` | 1,142 | 26,309 | no | `batches.expect`, `criteria.load`, `glossary.lookup`, `tickets.load` |
| `tests_missing` | 1,435 | 26,185 | no | `batches.expect`, `criteria.load`, `glossary.lookup`, `references.load`, `tests.consult`, `tickets.load` |
| `tests_failing`, the last | 28,399 | 27,096 | at 18,064 | `batches.expect`, `code.diff`, part of the diff. Lost: `criteria.load`, `references.load`, `tests.load`, `code.source` |
| `verdict_failed` | 1,353 | 28,732 | no | `batches.expect`, `criteria.load`, `verdicts.load` |

So the fix wake at 16384 loses its red rows and its source to the diff block, as night 119's s259 did. `test_the_fix_wake_keeps_its_blocks_at_16384` is a strict xfail held by frame 134. The other three wakes are far below their budget on this scene, and their tests pass.

The proofs ran in memory through `p9/s6proof.py`, which changes `runner.push_working_set` for one build and restores it (observed: `p9/s6proof.out`, 2026-10-06):

| Proof | The change | Result |
|---|---|---|
| drop one block per wake | `tickets.load` from `batch_start`, `tests.consult` from `tests_missing`, `verdicts.load` from `verdict_failed` | each of the three tests red, naming the block |
| the diff last | `code.diff` moved to the end of the fix wake, a sketch of frame 134's repair | the fix wake's test green, so the strict xfail goes red when frame 134 lands |
| the diff last, and no source | the same, and `code.source` dropped from the fix wake | the fix wake's test red, naming `code.source` |

`test_the_fix_wake_holds_both_red_tests_and_the_diff` asserts the state from the rows, so the xfail cannot hide a scene that no longer holds frame 134's wake. `test_scene_large_module_again.py` builds S6 a second time, and the two builds give equal rows. S6 has no landings and no sweep yet.

## The invariants with the night 126 findings

`rota/tools/invariants.py` holds I1 to I9 of the design and one more, I10. `check(conn)` returns the findings. `python -m rota.tools.invariants PATH` opens a night's database with `mode=ro&immutable=1` and prints a count and five lines for each invariant. `--all` prints every line, and `--root` names the project for I2.

| Name | The proposition | How it reads |
|---|---|---|
| I1 | a criterion holds at most one test | `tests` grouped by criterion |
| I2 | an `inh_` row has no criterion, and its body is the project file at the batch's base | the base is the merge base of the batch's head with the project's HEAD, read through git. A merged batch's base is not read, and a database whose root is not a repository skips the bodies |
| I3 | a merged batch's latest run of each of its own tests at its head is a pass | a test with no run at the head is a finding too |
| I4 | a run row's test is a test of the run's batch | one line per test, run batch and test batch, with a count |
| I5 | a parked batch holds one open park ask, and an open park ask names a parked batch | `scheduler.parked` and the park ask's id |
| I6 | a quarantined key never names a merged or abandoned batch | every ref of the key |
| I7 | at most one batch runs | the audit's group 3 |
| I8 | one open batch per item | the audit's group 2 |
| I9 | an answered message has an answer, except the rows answered by design | the audit's group 5, less three kinds, below |
| I10 | an integer column holds integers | `typeof` on every column declared `INT` |

I9's rows answered by design, each with its source:

- A message whose verb carries material, `deliver`, `relay`, `converse`, `submit`, `answer`, `report` or `verdict`. The session that reads it answers it when it commits (`db.session_commit`).
- A present to the principal whose refs hold a batch. The principal's approve closes it at the keypress, and no verdict row follows (`principal.land`, "A touch note is read, not ruled on"). Every scene met this row, because a scene's principal lands its own verdicts.
- A challenge to the Tester whose refs name a test at version 2 or more. The replace is the answer (ruled: the judging session, 2026-10-05, frame 132's question 4).

On night 126 the audit's group 5 finds 54 rows. I9 finds 3 (observed: `audit` and the checker on `clickI_night126.db`, read-only, 2026-10-06).

The checker on night 126 (observed: `python -m rota.tools.invariants D:/repos/rota/.rota/clickI_night126.db --all`, 2026-10-06; I2 read clickI's HEAD of that hour):

| Invariant | Findings | What they are | Frame |
|---|---|---|---|
| I1 | 0 | | |
| I2 | 6 | `inh_echo_json_01`, `_02` and `_03` hold criteria `echo_json_compact`, `_2` and `_3`, and their paths are not in bg_1's base 2c8cd3ac95. A Tester stored its tests under ids with the inherited prefix | none found |
| I3 | 0 | bg_2's own tests all pass at its head | |
| I4 | 34 | 9 runs of bg_1 each name 34 project tests whose rows now say bg_2 | 130 |
| I5 | 1 | parked bg_1 holds 0 open park asks. `do:park` parked it at the loop cap, and no park ask opened | none found, see "Seen and not fixed" |
| I6 | 0 | | |
| I7 | 0 | | |
| I8 | 0 | | |
| I9 | 3 | m75, the Architect's propose to the Vision Keeper, and m79 and m105, the Architect's challenges to the Vision Keeper, are answered and nothing answers them | none found |
| I10 | 1 | `items.priority` rowid 8 holds the text `'high'`, `version_option_show_python` | 164 |

45 findings. The night's crash row is I10's one finding.

The checker on the scenes' ends (observed: the scene tests, 2026-10-06). Each scene file runs one test per invariant. Three are strict xfails, each with its frame:

| Scene | Breaks | Held by |
|---|---|---|
| `two_batches` | I4: b1's runs name the project's tests, whose rows now say b2 | frame 130 |
| `two_batches` | I5: parked b1 holds no open ask after the third park ask's key is quarantined | frame 142 |
| `merged_then_next` | I4: the merged b1's runs name the project's tests of b2 | frame 130 |
| `challenged`, `park`, `critic`, `review`, `large_module` | none | |

`tests/rota/test_invariants.py` builds `merged_then_next` once. Each test copies the database, changes one row, and asserts the one finding that the change adds. One test for each invariant, one more for I2's body, one for a relay that I9 reads as answered by design, and one that checks a database by path and leaves its bytes as they were. Three changes first broke two invariants, each one truly, so each test now changes a row that breaks one only.

## The catalogue rows

| Row | Scene and wake | Sent | Today | Known entry |
|---|---|---|---|---|
| a word for a priority | `park`, the Vision Keeper's relay of i2 | `problem.prioritize(id='i2', priority='high')`, then one `loop.step` on a copy | the call lands, and the step raises `TypeError: bad operand type for unary -: 'str'` | strict xfail, held by frame 164 |
| a body whose escaped quote breaks a line | `two_batches`, the Tester's `tests_missing` of b2 | night 126's s156 line, parsed by `toolproto.extract`: `rows = ["{\"key\": \"value\"}"]` in a single-quoted body | refused with `the body is not Python (invalid syntax. Is this intended to be part of the string?, line 5)`. The refusal holds neither the line nor `\"` | strict xfail, held by frame 166 |
| the relay of a batch id to the Vision Keeper | not built | | | frame 167 |

The first row asserts a refusal. When its call lands, `scenes.land_and_step` commits the call's writes on an in-memory copy, as `db.session_commit` commits a session, and runs one `loop.step`. The failure then carries what the step raised. The scene's own database does not move. The second row asserts the door, the first words and two parts that the refusal must hold, the broken line and the quote (`Call.holds`).

The third row is skipped. The park scene ends with b1 parked at attempt 5 of `loop_cap` 10, and `tick:exhausted` needs a failing attempt of 10 (`predicates.exhausted`). The count of steps from the park's end to the relay, at the least (reasoned: the scheduler's order and the scenes' own counts, 2026-10-06):

1. b1 leaves the park only by a head commit, and no wake gives the Developer b1 while b2 waits. So b2 starts first. A batch's path from its start to its merge is 7 steps in `merged_then_next`, b1's: the start, the harness, the Tester, the harness, the Critic, the structural review and the merge.
2. Five more failing attempts of b1, a commit and a harness run each, are 10 steps.
3. The ladder's three rungs, the Developer, the Architect and the Vision Keeper, are 3 steps. The Architect's proposal reaches the principal and comes back as a relay through the Liaison's submit and present, the principal's answer and the Liaison's relay, at least 3 steps.

That is at least 23 steps, against the bound of 20. A lower `loop_cap` would change the park scene, which the other rows read, so the pass does not lower it.

## The counts

Against pass 8: the catalogue holds 16 rows, 14 before. The sweep holds 46 right calls, as before. The scene files and `test_invariants.py` hold 10 strict xfails, 4 before: S1's run test and the W146 row, held by frames 130 and 146; the W138 and X7 rows, held by frame 138; and six new ones, held by frames 134, 130 twice, 142, 164 and 166. 70 new invariant tests run on the seven scene ends, ten on each, and 14 in `test_invariants.py`. The scene files, `test_invariants.py` and the S6 files gave 172 passed, 5 skipped and 10 xfailed (observed: `pytest tests/rota/test_scene_*.py tests/rota/test_invariants.py -n 4`, 2026-10-06).

## The times

- S6's first build took 33.6 s, its second build 33.6 s, and `test_invariants.py`'s build of `merged_then_next` 31.2 s, three builds side by side on three workers (observed: `--durations`, 2026-10-06 17:22). The main card was held by `qwen3.5:9b` from 17:01, so other work ran on the machine.
- The twelve scene files and `test_invariants.py` took 100.0 s on four workers (observed: 2026-10-06, before the gate).
- The gate took 1,102.6 s, against 857.9 s on pass 8. The machine was not quiet, and the added build of S6 twice and of `merged_then_next` once is about 100 s of worker time (reasoned: the builds above).

## Deviations

- **The priority row runs on the park scene, not on `two_batches`.** `next_batch` sorts only pending or deferred batches that are not parked. At `two_batches`'s end b1 is parked and b2 runs, so no step reads the word and nothing crashes. The park ends as walk 3 did, b1 parked and b2 pending.
- **The third row is not built.** The park's end is at least 23 steps from the relay, as counted above.
- **I10 is added.** The brief allowed an invariant with a name, and the design's nine find nothing in `items.priority`.
- **I9 removes three kinds of row, not one list from the inventory.** The inventory names 29 principal `converse` rows on night 119. The design asked for the by-design rows listed and removed, and the list above names each kind with its source.
- **I2's body check skips a merged batch.** A merged batch's head is on the project's HEAD, so its merge base is its head and not its base. On a night, I2 reads the project's HEAD at the hour of the check, not at the night's end.
- **S6 holds more than the design's text.** The design names a module, a criterion deep in the file and a red test. Frame 134's wake also needs a red project test and a large diff, so S6 adds `tests/test_ledger.py`, the rates' extra cent, and the three empty fix sessions with the Liaison's report that the night's order puts before the Tester.
- **The gate ran with its summary line at 23 failed.** The 23 are the baseline's reds, and the three new reds are the three that passes 7 and 8 showed. The commit goes against the agent's rule of no `failed` before a commit, on the brief's word that the gate holds.

## Seen and not fixed

- Night 126 holds three Tester tests under ids that start with `inh_`, `inh_echo_json_01` to `_03`, each with a criterion. Frame 135's door refuses only the exact id of a project test. `plans/stack.md` names these ids on 10 lines, as tests that a seat challenged or stored, and no frame names the prefix itself as the fault (observed: a grep for `inh_echo`, 2026-10-06).
- Night 126's bg_1 is parked by `do:park` at the loop cap with no open park ask. Frame 142 holds the re-asked park ask on a quarantine park. Whether a loop-cap park owes an ask was not read.
- Night 126's m79 and m105, the Architect's challenges to the Vision Keeper, and its proposal m75 are answered with no answer row. The sessions that closed them were not read.
- The audit's group 1 finds 12 dangling term refs on night 126's criteria, such as `confirm` and `version_option`. The checker does not repeat the audit's refs.
- `scenes.blocks` reads a header inside `code.diff`'s own text, `[removed lines]` and `[diff]`, as a block. No test names those keys, so no test reads them wrong.
- The gate shows 24 warnings, against 25 on pass 8. They were not read.

## Report

**Commits on `f144p9`.** 1383bd2a, the code and tests: 8 files, 846 insertions, 15 deletions. The record is the commit after it.

**The gate** (observed: `python -m rota.tools.gate` in the worktree, 2026-10-06, 17:01 to 17:22):

```
suite: 23 failed, 3087 passed, 35 skipped, 18 xfailed, 24 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 1102.6s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The gate printed one line before the five: `main card: held by qwen3.5:9b until 2026-10-06T17:01:16.2045127+01:00, re-records wait`. No case was stale, so no re-record waited.

**The probes** are in the session's scratchpad, `p9/`: `s6probe.py` builds S6 and writes each wake cut and uncut to `s6/`, `s6proof.py` with `s6proof.out` runs the block proofs, and `s156.txt` holds s156's encode turns from night 126.
