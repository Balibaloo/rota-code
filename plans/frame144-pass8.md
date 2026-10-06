# Frame 144, pass 8: each scene is a run of the night's walk

Meta workflow. Pass 8 of frame 144, the night databases are not a test tier. An implementing agent on Opus wrote this record on 2026-10-06, on the branch `f144p8` in the worktree `C:/Users/roman/rota_f144p8`, from 7a056ce0. An earlier agent started the pass and was stopped. This agent continued from the edits that it left in the tree. The pass repairs the 2 medium and 6 low findings of the delta review of pass 7. No file under `rota/` outside `rota/testkit` changed.

Commit: aa275754 (code and tests). This record is the next commit.

## The design

A step of a scene is now one iteration of `probes/walk.py` (observed: each build, 2026-10-06):

1. The principal answers every open ask through `principal.pump`. An ask that the script leaves open fails the build, because the walk answers every ask before it steps.
2. The walk answers every Liaison sentence that has no page (`principal.pending_replies`). `scenes.answer_replies` holds the walk's own SQL, so the new turn has the walk's ids, `e_p<n>` and `m_p<n>`.
3. One `loop.step` runs with no principal, as the walk calls it.

A sentence of the principal fails the build unless the step before it was quiet or merged a batch. A walk says one sentence when it starts, and the gauntlet's walk before it stops at quiet or at a merge (`probes/walk.py`, the default `WALK_STOP_AT_MERGE=1`). Nights 119, 120 and 121 show both stops in their logs.

## The eight findings

1. **MED. Three scenes said a sentence mid-run.** Repaired. Each scene now starts at quiet after the survey, and says each later sentence at quiet or right after a merge. The seats that the loop then picks are seated: the Tester in S1, the surveys in S2.
   - S1: the order of night 121 from s212 to s297. b1's key is quarantined, the Tester's wake lifts it, and it is quarantined again. The loop is then quiet, and item 2 comes. The preempt follows the grouping, three park asks follow, then b2 starts.
   - S2: item 2 comes right after the merge. The Terminologist and the Architect survey `src/billing` and the root again, as night 120 did at s155 to s158. A new test asserts the four surveys between the merge and b2's start.
   - The park: item 2 comes at quiet, and the scene ends at the open park ask, as night 121 stood at s277. No third item: in the night's order a third sentence comes only at the next quiet, after b2 has run.
2. **MED. No scene held the answered park ask.** Repaired in S1. The walk answers each park ask with its stock sentence, which names no option. The loop then wakes the Liaison on the words. The door `rulings.rule` refuses a ruling on a park ask, so the Liaison sends the principal one sentence. The walk answers that sentence, and the Liaison takes the answer in as a new statement. The park ask then comes again. After the third ask the key is at (3, 1, 1), and the Liaison reports it. Night 121 did the same at s277, s282, s287 and s292. A new test asserts this order, and warns with the open question, held by frame 142.
3. **LOW. The question row's comment.** Repaired. Night 120's s146 holds the challenge and the fail in one session, so the comment cites it for the `critic` row. The comment now says that the review's state needs the Tester's session on the challenge to fail or to be skipped. After the Critic's challenge lands, the frontier is `['tester|challenge|c1,t1', 'critic|tick:review|b1']` (observed: `p8/lands8.py`, 2026-10-06).
4. **LOW. A removed answer passed.** Repaired twice. The build fails when an ask stays open after the principal's turn. `make` asserts the open asks at the end of every scene.
5. **LOW. Two holes in the unused check.** Repaired. A function of `every` that the loop never calls fails the build. `land_all` seats the landings of one scene only, and runs the unused check after the last land.
6. **LOW. The end frontier was the cockpit's view.** Repaired. `end_frontier` reads `scheduler.frontier` inside a savepoint that rolls back. The connection is in autocommit mode, so a plain `rollback` undoes nothing. The two views differ at S1's end: the cockpit's view holds `liaison|tick:park_ask|i1,b1`, whose key is quarantined, and the loop drops it. The build's error text uses the loop's frontier too.
7. **LOW. The differences from a night.** Named in the module's docstring. One named difference is not one:
   - `ROTA_ONESHOT`: the gauntlet clears it at line 12, so a night runs each session turn by turn, as a scene does. Night 121's sessions hold 5.2 turns on average and 25 at most (observed: `turns`, 2026-10-06).
   - The night's principal answers a confirm or a present in words, and a Liaison session lands the verdict (night 121, s197 then s198). The difference stays: words on every page add a Liaison session to each ask, about one step in four.
   - `-|tick:constraint_zero|` at (3, 1, 1) on nights 119, 120 and 121. The difference stays: the row names no area, and the night's end holds no unbound area that explains it, so the step that wrote it was not found.
   - `twin7.txt` lists five scenes, not six. Pass 7's record said six. This pass's twin check covers all six, and the two landed builds.
8. **LOW. The time.** Repaired in part. Each second build now has its own file, `test_scene_<name>_again.py`, so ten units share four workers. The two builds of a scene meet in a directory that the run's workers share, and the file that finishes second compares the rows. The times are below.

One more repair, found by the twin check: `finding_rulings.at` holds the clock, as `config_history.at` does. These are the two columns of the schema whose default is the clock. `scenes.CLOCKS` now names both.

## The scenes

"Steps that differ" and "tables that differ" are `p8/twin8.py`. It builds A by the scene's builder. It then builds B on a fresh repository, with a plain `loop.step` per step and no principal, a `ScriptedBackend` of A's lines chosen by the step's index alone, and no seam on `run_session`. Between two steps, B says A's sentences, pumps A's answers and answers a Liaison sentence as the walk does, from its own code. "Silent" counts the sentences that B says where the step before was not quiet and merged nothing (observed: `p8/twin/`, 2026-10-06).

| Scene | Steps | Differ | Tables differ | Sentences, silent | End frontier | `tick_attempts` at the end | Open asks | Proofs this pass, red |
|---|---|---|---|---|---|---|---|---|
| S1 `two_batches` | 90 | 0 | 0 of 46 | 2, 0 | `tester\|tick:tests_missing\|b2` | the fix key (3, 1, 1), the park ask (3, 1, 1), `quarantined\|b1` 1, `quarantined\|i1,b1` 1 | none | `ask_once`; `replies_unanswered`; `end_frontier_readonly` |
| S1 landed | 91 | 0 | 0 of 46 | 2, 0 | `\|do:harness\|b2`, `critic\|tick:review\|b2` | | | |
| S2 `merged_then_next` | 63 | 0 | 0 of 46 | 2, 0 | `tester\|tick:tests_missing\|b2` | none | none | `no_reindex_on_merge`; `say_mid_run` |
| S5 `challenged` | 43 | 0 | 0 of 46 | 1, 0 | `critic\|tick:review\|b1` | none | none | `asks_unchecked`; `answer_removed`; `every_unused` |
| park | 65 | 0 | 0 of 46 | 2, 0 | `architect\|tick:annotate\|b2`, `developer\|tick:batch_start\|b2` | the preempt 1, the fix key (3, 1, 1), the park ask 1, `quarantined\|b1` 1 | `clarify i1` | `next_batch_unparked` |
| `critic` | 43 | 0 | 0 of 46 | 1, 0 | `critic\|tick:review\|b1` | none | none | |
| `review` | 44 | 0 | 0 of 46 | 1, 0 | `architect\|tick:structural_review\|b1` | `critic\|tick:review\|b1` 1 | none | `landing_seat_unused` |
| `review` landed | 52 | 0 | 0 of 46 | 1, 0 | `developer\|tick:verdict_failed\|b1` | | | |

The proofs ran in memory through `p8/mut8.py`. Each run printed that the changed source reached the compiler and that each target file's bytes were the same after (observed: `p8/mut/`, 2026-10-06). What each proof changes, and what went red:

| Proof | The change | Red |
|---|---|---|
| `ask_once` | `predicates.park_ask` asks once a batch | S1's build: the loop never asks for the second and third park asks |
| `replies_unanswered` | the walk answers no Liaison sentence | S1's build: the loop never asks for the Liaison's reading of `e_p1` |
| `end_frontier_readonly` | `end_frontier` reads the cockpit's view | S1's end frontier, which then holds the quarantined park ask |
| `no_reindex_on_merge` | the merge does not re-index main | S2's new test: no survey after the merge |
| `say_mid_run` | S2 says item 2 when b1 exists, as pass 7 did | S2's build: "the walk says no sentence here" |
| `asks_unchecked` | the check after the pump is off, and S5's touch note is not read | S5's end: the open asks |
| `answer_removed` | S5's touch note is not read | S5's build: the script has no answer |
| `every_unused` | an `every` function that the loop never calls | S5's build |
| `landing_seat_unused` | a landing seat that the loop never picks | the review's second build, after the last land |
| `next_batch_unparked` | `next_batch` keeps a parked batch | the park's test: `['b2', 'b1']` |

## The counts

Against pass 7: the catalogue holds 14 rows, as before. The sweep holds 46 right calls, and 5 land through whole sessions, as before. 4 strict xfails, as before: S1's run test and the W146 row, held by frames 130 and 146, and the W138 and X7 rows, held by frame 138. The question row of the review still warns that the call lands. S1's new test adds one warning, the re-asked park ask.

## The times

`python -m pytest tests/rota/test_scene_*.py -n 4 -q`, pytest's own wall time. Other gates ran on the machine at the same time (observed: 2026-10-06, 13:06 to 13:15).

| Tree | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| 7a056ce0, five files, extracted by `git archive` | 91.4 s | 102.4 s | 82.2 s |
| aa275754, ten files | 67.5 s | 83.7 s | 78.9 s |

Two later runs of the ten files took 63.9 s and 61.9 s. The builds sum to about 172 s, so four workers cannot go much under 45 s. The slowest units are the park's first build, 23.5 s, and S1's first build, 22.1 s. The aim of about 60 s is reached on a quiet machine only.

## Deviations

- **The walk's answer to a Liaison sentence is in every scene.** The brief named the sentences and the asks. The walk also answers a Liaison sentence with no page, and on night 121 each such answer became a new statement. A scene without it ends with open replies that no night leaves. In S1 it adds 15 steps, five for each of three new statements: the Liaison's intake, its ratification and three deliveries.
- **The deliveries of the new statements run before the next park ask.** The loop's order in the scene gives this. On night 121 the deliveries of s4 to s6 waited until s346. The cause of the night's wait was not read.
- **The park holds no b3 and no answered ask.** The night's order gives no third item before b2 runs, and S1 holds the answered ask.
- **The re-asked park ask is a test that warns, and not a catalogue row.** The catalogue holds calls. The re-ask is the loop's act, so the question is a warning in S1's test, held by frame 142.
- **S2's priorities changed**, item 1 to 1 and item 2 to 2, as in S1 and the park. Item 2 now comes after the merge, so the order of the two items no longer matters.
- **The gate ran with its summary line at 23 failed.** The 23 are the baseline's reds, and the brief accepts the known three new reds. The agent's rule asks for no `failed` before a commit, so this commit goes against that rule on the brief's word.

## Seen and not fixed

- The cockpit's read-only frontier shows a wake whose key is quarantined, and the loop never picks it (S1's end, `liaison|tick:park_ask|i1,b1`). A person at the TUI sees a wake that does not come.
- The walk's answer to the Liaison's reply on a park ask becomes a new statement each time. On night 121 three statements, s4 to s6, hold the same sentence. This is the second half of frame 142's wall.
- The step that leaves `-|tick:constraint_zero|` at (3, 1, 1) on every night was not found.
- The gate shows 25 warnings, against 17 on pass 7's gate. One is S1's new warning. The other seven were not read.

## Report

**Commits on `f144p8`.** aa275754, the code and tests: 12 files, 568 insertions, 161 deletions. The record is the commit after it.

**The gate** (observed: `python -m rota.tools.gate` in the worktree, 2026-10-06):

```
suite: 23 failed, 2936 passed, 34 skipped, 12 xfailed, 25 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 857.9s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The three new reds are the three that pass 7's gate also showed.

**The probes** are in the session's scratchpad, `p8/`: `nightseq.py` reads a night's sessions, `explore.py` builds one scene, `twin8.py` with `twin/`, `mut8.py` with `mut/`, `lands8.py`, and `before/`, pass 7's tree for the times. The night databases are copies in `p8/nights/`.
