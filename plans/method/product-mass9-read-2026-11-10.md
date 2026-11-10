# Mass 9, the measures: a blind read of every instrument, 2026-11-10

Written by one reader for frame 364. The reader got no hypothesis. The page holds what exists and what the records show. It holds no cause and no fix.

`T` is `C:/Users/roman/AppData/Local/Temp/claude/`. `R` is the register, `tests/rota/cases/*.yaml` with `tests/rota/cassettes.db`. Scratch scripts are in `T/6d9eb18c9e6274ab/1efd37b1-058e-4b19-8ab1-e1a6c654a389/scratchpad/mass9/`.

## Result

No instrument has a person in the Principal seat, and no record shows a run with a person there (observed: every driver below has a script, an agent or the build session at the seat). The register holds 206 cases that the suite loads, and every one has one desk session or a chain of two as its input (observed: count script on the case files). No register case takes a whole request on a repository. Only the walks, the nights and the dry runs take a whole request, and they decide a result by a merge row or by a reading afterwards (observed: `probes/walk.py` 203-208, the dry run scripts). The nights merged on 47 of 93 recorded nights, all on clickI, and the last night is 175 on 2026-10-28 (observed: read-only queries of `.rota/clickI_night*.db`). The dry runs merged 3 times in 11 runs: once each on clickI, tipsI and icalendarI, and 0 times in the 7 runs of the fold sentence on icalendarI (observed: the 11 run databases). The last gate run on 2026-11-10 reports 30 reds and 36 stale cases, so the register is not green (observed: `.rota-gate.log` line 413). Of the 29 reds on model cases, 6 carry the word "attribut" in their case block (observed: a search of the case files). The blind test of 2026-11-03 asks for 72 runs with a key and an ablation, and one run exists: blind run 1, one task, with records only, no merge (observed: `plans/dry-blind1/`, the run's `turns/t4.txt`). Its score is not recorded. No instrument decides a result from the person's reading of the merged change, so P5 has no direct measure (reasoned: column 4 of the grid). P6 has measures only at the level of one desk, through reds by model (reasoned: the grid).

## Part A: what the design says the measures are

1. "The register measures both: 114 cases in `tests/rota/cases/*.yaml`, replayed from `tests/rota/cassettes.db` (git LFS) by `test_l1.py` and `test_l3.py`, recorded live with `ROTA_L1=1`" (`rota/MAP.md` 45-48).
2. "A red carries an attribution note in the case file or is owed a fix" (`rota/MAP.md` 48-49).
3. Every role test has one shape: "seed rows → inject message → run session → assert on deltas", and the assertions are structural, "never on prose content" (`rota/TESTS.md` 24-26, 70-72).
4. Every T1/T2 case declares `runs: N, pass: k`, and a drop from 5/5 to 3/5 "is a prompt regression signal" (`rota/TESTS.md` 61-64).
5. T2 arcs are "multi-session traces replaying the three stories end to end", with a scripted client and a per-step assertion (`rota/TESTS.md` 36, 529-547).
6. The register of open obligations is the second half of the system: "undischarged goals stay visible and countable" (`rota/REGISTER.md` 12-16).
7. "The walks measure the whole: `probes/walk.py` (one run, one sentence, a yes-only principal) ... Every walk writes a row to `tests/rota/walks.jsonl`" (`rota/MAP.md` 50-54).
8. "The register measures one desk, one turn. The walks measure the loop with a scripted principal ... Nothing asserts across pages" (`plans/seat-exchange.md` 3-5).
9. The seat exchange pins what it finds as page-sequence cases: "a sentence, the pages it produces, the words on each, in order" (`plans/seat-exchange.md` 26-28).
10. "Roman at the TUI with his own sentences is the final test, after click merges cold" (`plans/seat-exchange.md` 32-33).
11. The blind test scores "only what the person sees: the merged diff, the page and the result of hidden probes. The grader never reads the records" (`plans/understanding-test-blind-2026-11-03.md` 94).
12. Each task runs three times with the records and three times without, and "the understanding score is the score with records minus the score without records" (same page, 98).
13. Two key writers work independently before the first run, the SHA-256 of the key and the probes is committed before the run, and the key opens only after all runs end (same page, 104-108).
14. "A wrong merge on any promise task ... fails the whole test", and "the report names the highest tier the system passed" (same page, 112-116).
15. "Core is complete when every partial is built, click and two more lineage repositories merge cold, and the register is green or attributed on the shipped profile" (`rota/COMPLETION.md` 18-20).

## Part B: every instrument

Each entry gives input, Principal, output, decider, size, runs, last result, and the parts of the destination. The P lines are (reasoned) from the input and the decider.

### B1. The register, L1 (`tests/rota/test_l1.py`, `l*.yaml`)

1. Input: one session at one desk, on fixture rows and one inbound message or tick (observed: `test_l1.py` 81-91, 137-156). 76 of 170 cases also build a small git fixture repository (observed: `repo:` key count; `rota/testkit/fixtures.py` 975-992).
2. Principal: nobody. A fixture row stands for a Principal entry where a case needs one (observed: `l1_liaison.yaml` 27-31).
3. Output: a pass or a fail per case, and one `case_runs` row per sampled run in `tests/rota/cassettes.db` (observed: `test_l1.py` 163-174).
4. Decider: assertions on rows written, messages sent and tool calls, against `expect` and `forbidden`, with a threshold of k of N (observed: `test_l1.py` 222-225; 206 cases carry `forbidden`).
5. Size: 170 cases. By role: liaison 42, architect 32, developer 25, vision_keeper 22, terminologist 19, tester 17, critic 11, researcher 2. Tier labels: T1 165, T2 5. All 170 take one session (observed: count script).
6. Runs: `case_runs` holds 610,509 rows for 235 case ids. 439,414 carry a time, from 2026-09-23 05:13 to 2026-11-10 05:59. 8,886 rows are live model calls, and the rest are replays. The last live day is 2026-11-10, with 125 live rows on 20 cases (observed: read-only queries).
7. Last result: the gate run of 2026-11-10 reports 26 reds and 12 stale cases in `test_l1_case` (observed: `.rota-gate.log` 1-413).
8. P1 no, P2 no, P3 no (fixture rows and built repositories), P4 no (one desk), P5 no. P6 part: a red names a desk and a model, but a red cannot tell a model limit from a brief or a case fault without the attribution note (reasoned: `test_l1.py` 209-220).

### B2. The register, L3 chains (`tests/rota/test_l3.py`, `l3_handoffs.yaml`)

1. Input: a chain of two sessions. The second session wakes on the first session's own outbound row (observed: `test_l3.py` 2-13).
2. Principal: nobody.
3. Output: pass or fail, `case_runs` rows.
4. Decider: assertions on rows and messages, k of N with lower thresholds (observed: `test_l3.py` 92-97, 131-134).
5. Size: 6 chains. The pairs are liaison to terminologist 2, liaison to liaison 1, liaison to vision_keeper 1, vision_keeper to terminologist 1, terminologist to vision_keeper 1, critic to developer 1 (observed: count script; one of the 7 chain pairs is the G1 chain).
6. Runs: in the same `case_runs` table as B1.
7. Last result: 2 reds, `L3-a-challenge-reaches-the-role-that-can-answer-it` 1/5 and `L3-a-failed-verdict-turns-into-a-fix` 1/5 (observed: `.rota-gate.log` 193, 213).
8. P1 to P5 no. P6 part: a chain red names a hand-off, not a model limit alone (reasoned).

### B3. The register, L3 rulings (`tests/rota/test_l3_rulings.py`, `l3_rulings.yaml`)

1. Input: one Liaison session in `landing` mode, turn after turn, on one real page of nights 170 to 175 and the reply that the seat gave on that night (observed: `test_l3_rulings.py` 1-14).
2. Principal: a recorded reply. The replies of nights 170 to 175 came from the agent principal on `opus` (observed: `.rota/clickI_night170.principal.jsonl` to `175`, 1,328 to 1,429 rows with `"model": "opus"`). The case file calls them "his real replies" (observed: `l3_rulings.yaml` line 1).
3. Output: pass or fail, and a printed table.
4. Decider: the landed `ruled_refs` rows per line against the `expect` line of a judge, written beforehand in `cases/sources/l3_rulings_judged.yaml` (observed: `test_l3_rulings.py` 7-9; the source file holds 30 entries with a `judge` key).
5. Size: 25 cases, all on `gemma4:12b-it-qat`, runs 3, pass 2 (observed: count script).
6. Runs: in `case_runs`.
7. Last result: 24 of 25 stale, "no recording for the current prompt" (observed: `.rota-gate.log`, 24 STALE lines for `test_l3_rulings_case`).
8. P1 part: reply reading only. P2 to P4 no. P5 no. P6 part: a desk limit on reading replies (reasoned).

### B4. The register, G segments (`tests/rota/test_gauntlet.py`, `g1_segments.yaml`)

1. Input: 4 single sessions and 1 chain, on fixture rows (observed: count script).
2. Principal: nobody. A fixture holds the Principal's words.
3. Output, decider: as B1.
4. Size: 5 cases. `tests/rota/test_docs.py` 318-321 pins the count at 5.
5. Last result: 1 red, `G1-a-ratified-conflict-is-caught-by-the-owner` 0/5 (observed: `.rota-gate.log` 199).
6. P1 to P5 no. P6 part, as B1.

### B5. The gate (`rota/tools/gate.py`)

1. Input: the whole suite `tests/rota`, replay only, with the recording names dropped (observed: `gate.py` 53-67).
2. Principal: nobody.
3. Output: five lines, `.rota-gate.log`, and a baseline `.rota-gate.json`. A stale case is re-recorded after the run (observed: `gate.py` 1-12).
4. Decider: pytest pass or fail, compared with the baseline.
5. Size: the last run counted 7,300 passed, 66 failed, 49 skipped, 16 xfailed (observed: `.rota-gate.log` 413). The files hold 5,073 test functions in 328 files before parametrisation (observed: a grep count).
6. Runs: only the last run and one baseline are kept. The count of gate runs is not recorded. The baseline is 2026-11-08 17:34 at `33c1e697`: 33 failed, 7,311 passed, 0 stale (observed: `.rota-gate.json`).
7. Last result: 2026-11-10, before 05:31 (the `lastfailed` time). 30 reds: 29 model cases and `test_register_key.py::test_the_parameter_set_holds_the_shapes_that_would_break_it`. 36 stale: 12 L1, 24 L3R. The re-records after the run failed with "not found" for the L3R ids, because they named `test_l1.py` (observed: `.rota-gate.log` tail).
8. P1 to P5 no. P6 part, as B1.

### B6. The deterministic suite (T0, synthetic arcs, scenes, invariants)

1. Input: fixture rows, or a scene that code builds through `loop.step` with `ScriptedBackend` (observed: `rota/testkit/scenes.py` 88, 211). `test_arc_synthetic.py` drives a full lifecycle with canned completions. `test_arc_seam.py` takes one sentence to one merged batch (observed: docstrings; `test_arc_seam.py` 76, 242).
2. Principal: a fixed script (observed: `scenes.py` 221).
3. Output: pass or fail in the gate.
4. Decider: assertions on rows and states.
5. Size: 12 scene files with 23 test functions; `test_invariants.py` 21 tests; `test_t0_plumbing.py` 33; `test_delivery.py` 30 (observed: grep counts).
6. Runs: each gate run.
7. Last result: inside the gate figure. The one deterministic red is in `test_register_key.py`.
8. P4 part: merge mechanics only. P1 to P3, P5, P6 no.

### B7. Obligation and coverage checks (`rota/testkit/obligations.py`, `coverage.py`)

1. Input: the graph and the case set. 2. Principal: nobody. 3. Output: pass or fail. 4. Decider: every mode has an L1 case, and the obligation counts pass a floor (observed: `test_l1.py` 232-258). The full obligation check is skipped "the obligation set is not yet fully covered" (observed: `test_l1.py` 261). 5 to 7: inside the gate. 8. P1 to P6 no.

### B8. Readers of the register (`rota/tools/casestatus.py`, `triage.py`)

1. Input: the state of `cassettes.db`. 2. Principal: nobody. 3. Output: a printed report. 4. Decider: nothing. They print status and group failures (observed: docstrings). 5 to 7: no recorded output found. 8. As B1, through what they read.

### B9. The walks (`probes/walk.py`, `tests/rota/walks.jsonl`)

1. Input: a whole request on a repository, one sentence (observed: `walk.py` 1-8).
2. Principal: a fixed script that approves every confirm and present, and answers every clarify with one sentence. A variant contests one numbered line once (observed: `walk.py` 3-5, 61-77). `WALK_AGENT` puts an agent at the seat (B11).
3. Output: one row in `tests/rota/walks.jsonl` of the checkout the walk runs from (observed: `walk.py` 140-149).
4. Decider: the count of merged batches rises (observed: `walk.py` 203-208). Nothing reads the diff.
5. Size: 156 rows. Repositories: clickI 136, tipsI 20. 15 rows are back-filled (observed: count script).
6. Runs: 2026-09-09 to 2026-10-25. 154 rows are from September and 2 from October (observed: count script). The file has 45 commits, the last on 2026-10-26 with night 166's two rows (observed: `git log`).
7. Last result: 14 rows merged (clickI 9, tipsI 5). The last two rows, 2026-10-25, are clickI merges after 43 and 38 steps.
8. P4 yes. P3 part: prepared sample repositories. P1, P2, P5 no. P6 part: a "quiet" row says it stopped, not why.

### B10. The nights (`probes/gauntlet_click.sh`, `rota/tools/nightcount.py`, `nightreport.py`)

1. Input: three requests on clickI in one run (observed: `gauntlet_click.sh` 1-3, 29-60). The launch scripts of nights 100, 120, 133, 150 and 175 set `GAUNTLET_COLD=1`, and those of nights 130 and 132 do not (observed: a grep of 7 launch scripts).
2. Principal: a fixed script "yes that all looks right, go ahead" on nights 82 to 132. An agent, `GAUNTLET_AGENT=opus`, on 42 nights from 133 (observed: `gauntlet_click.sh` WALK_WORDS line; a grep of `.rota/launch_night*.sh`).
3. Output: the run database `.rota/clickI_nightN.db`, the night log, the four counters of `nightcount` at the night's end, 27 `nightN_report.txt` files and 6 `nightN_truth.txt` files of git state (observed: `.rota` listing; `gauntlet_click.sh` 141).
4. Decider: a merge row per sentence. The counters and reports decide nothing (observed: `nightreport.py` "The tool prints facts only").
5. Size: 93 distinct nights, 82 to 175, in 99 database files (observed: night script).
6. Runs: 2026-09-18 to 2026-10-28, by file time. The night walks ran in worktrees, so their walk rows did not reach the main `walks.jsonl` except night 166 (observed: `launch_night175.sh` lines 6-11; `git log` of `walks.jsonl`).
7. Last result: 47 of 93 nights merged at least one batch, 74 batches in all. Script nights 82 to 132: 20 of 51 nights, 25 batches. Agent nights 133 to 175: 27 of 42 nights, 49 batches, 5 nights with all 3. Night 175: 2 merged, the third sentence quiet after 180 steps. Its counters: made up 78 turns in 41 sessions, ran anyway 0 (observed: `.rota/night175_launch.log`).
8. P4 yes, on clickI only. P3 part: one prepared repository. P1 part: an agent from 133. P2 no: the brief carries a fact per change. P5 no: nothing reads the diff for the request. P6 part: the counters count fabrication by role.

### B11. The agent principal (`probes/agent_principal.py`, `probes/principal_brief*.md`)

1. Input: one page at a time, inside a walk (observed: `agent_principal.py` 1-8).
2. Principal: an agent. The Claude Code binary, headless, `--model opus`, one process per page (observed: line 83).
3. Output: words that land through the same doors, and `.rota/<run>.principal.jsonl` (observed: line 139).
4. Decider: nothing. It is a seat backend.
5. Size: 2 briefs. The brief tells the agent what it asked for and one fact per change (observed: `principal_brief.md` "What you know").
6. Runs: 42 nights. 11 stubbed tests in `test_agent_principal.py`.
7. Last result: not a result instrument.
8. P1 part: a model plays the person. P2 part: the brief holds facts. P3 to P6 no.

### B12. The seat driver (`probes/seat.py`)

1. Input: a whole request, page by page (observed: `seat.py` 1-17).
2. Principal: an agent or a file of replies (observed: `seat.py` 13-15).
3. Output: `page_NNN.md`, `reply_NNN.txt`, `exchange.md`, and a walk row (observed: `seat.py` 6-11; `plans/dry-blind1/recipe.md`, "Why this driver").
4. Decider: nothing. Findings are prose in `plans/seat-exchange.md`.
5. Size: 2 exchanges, seat1 on tipsI and seat2 on click, 2026-09-12 (observed: `plans/exchanges/`). One back-filled walk row says "seat walk", tipsAH, 2026-09-09 (observed: `walks.jsonl` line 2).
6. Runs: the last recorded exchange is 2026-09-12.
7. Last result: no merge in seat1 or seat2, 11 findings (observed: `plans/seat-exchange.md` 62-67, 70-91).
8. P1 part: an agent at the seat. P4 part: no merge reached. P2, P3, P5, P6 no.

### B13. The dry runs (scripts `dryN_start.sh`, `dryN_turn.sh`)

1. Input: a whole request on a repository, turn by turn. Turn 1 onboards, posts the sentence and runs to rest. Each later turn signs the open pages with `rota sign --say` and runs again (observed: `T/6d9eb18c9e6274ab/13b7eef8-9ba8-4251-a72e-fd3511e65682/scratchpad/dry8/dry8_start.sh`, `dry8_turn.sh`).
2. Principal: the build session. It writes the words of each `sign` (observed: the turn scripts take `<msg>=<words>` arguments; CLAUDE.md "The session is the Principal of every dry run until then", ruled 2026-10-31).
3. Output: the run database, a copy before each turn, turn logs, and read pages in `plans/` (observed: `plans/method/product-seat-population-2026-11-10.md`).
4. Decider: nothing mechanical. A reader reads the records afterwards.
5. Size: 10 runs, dry1 to dry8 with 6b and 6c (observed: the inventory page). Subjects: clickI 1, tipsI 1, icalendarI 8.
6. Runs: database times 2026-11-02 to 2026-11-08 (observed: dry script).
7. Last result: dry1 merged 1 batch on clickI. dry2 merged 1 on tipsI, with 1 abandoned. dry3 merged 1 on icalendarI. dry4 to dry8, 6b and 6c ran the same fold sentence on icalendarI and merged 0. Their batches end `running`, `deferred` or absent (observed: dry script).
8. P4 yes. P3 part: prepared forks. P1 part: the session as the person. P2 no: the session knows rota's code and rows. P5 part: a reader, not the person. P6 part: the reads, not a mechanism.

### B14. The blind run (`plans/dry-blind1/`, its scratchpad)

1. Input: a whole request on tipsI at `ff1f65f`: "Refuse a negative bill amount, the same way a bad tip percentage is refused." (observed: `plans/dry-blind1/request.md`).
2. Principal: an agent, headless `opus`, with no tools, the brief and the pages only. The build session runs the commands (observed: `plans/dry-blind1/recipe.md`, Result and Doubts).
3. Output: the run database, `seat/exchange.jsonl`, turn logs (observed: the scratchpad listing).
4. Decider: a key written before the run, `key.md`, with a hidden probe on the merged checkout and six classes. The key commit is 2026-11-10 00:53 (observed: `git log -- plans/dry-blind1`). The key has one writer (observed: recipe, Doubts).
5. Size: 1 run of 1 task, with records, once.
6. Runs: 4 turns, database time 2026-11-10 (observed: `turns/t1.txt` to `t4.txt`).
7. Last result: no commit above `ff1f65f` on tips (observed: `git -C .../blind1/tips log`). At the end of turn 4 one page is open and the Liaison asks "Does 'nothing is built' mean that the current state of the code is what you want to keep ...?" (observed: `turns/t4.txt`). No score is recorded.
8. P2 part: the seat has no rota knowledge. P4 yes. P5 part: a key, not the person. P6 yes: the key has an "Honest stop" class. P1 part. P3 part: a pinned sample.

### B15. The blind test design and dry run 9 (`plans/understanding-test-blind-2026-11-03.md`, `plans/dry9/`)

1. Input: 12 tasks in 3 tiers. 2. Principal: not named. 3. Output: a class per run and an understanding score. 4. Decider: two keys before the run, hidden probes, the merged diff and the page (Part A 11 to 14).
5. Size: 72 runs by design (reasoned: 12 tasks, 3 runs with records, 3 without).
6. Runs: blind run 1 only (B14). Dry run 9 has a key from two writers, reconciled and committed 2026-11-10 04:27, before the run (observed: `plans/dry9/request.md`, `git log`). Its `turns/` directory is empty and no run database exists (observed: `T/6d9eb18c9e6274ab/c1a39439-187d-42de-8729-9b9eddf4abd3/scratchpad/dry9`).
7. Last result: none.
8. By design: P4 yes, P5 part (probes and page), P6 yes (honest stop class). P1, P2 not named. P3 part (pinned forks).

### B16. The answer keys and the key scorer (`rota/ANSWER_KEY*.md`, `probes/*/answer_key.yaml`, `probes/cnt/score.py`)

1. Input: the state of a database after onboarding. 2. Principal: nobody.
3. Output: counts printed by `score.py`. The prose keys are read by a person or an agent.
4. Decider: a key written before the run (observed: `ANSWER_KEY.md` 1-6; `probes/ical/answer_key.yaml` 1-9).
5. Size: 3 prose keys (oauthlib, icalendar, ctn_v3) and 3 YAML keys (cnt, click, ical).
6. Runs: the last recorded run is 2026-11-03 on a copy of dry3 (observed: `plans/dry3-key-score-2026-11-03.md` 5, 9). The YAML key holds one earlier result, ical_v0 of 2026-08-24 (observed: `answer_key.yaml` 166-174).
7. Last result: 9 of 10 required terms, 0 of 7 trap hits, 0 of 2 required constraints, 0 of 3 expected constraints (observed: same page, 5).
8. P1 to P6 no. The keys measure capability 11, the model of the project, which is not one of P1 to P6 (reasoned).

### B17. The consult probe (`probes/consult.py`, `probes/*/questions.py`)

1. Input: the state of a database. 2. Principal: nobody. Read-only sessions of three owners answer fixed questions (observed: `consult.py` 1-22).
3. Output: answers printed beside the expected answer (observed: `consult.py` 193-197). 4. Decider: nothing mechanical. A reader compares.
5. Size: 8 icalendar questions (observed: `probes/ical/questions.py`).
6. Runs: no recorded output of a run. The code changed on 2026-08-24, 2026-08-26 and 2026-11-04 (observed: `git log`). On 2026-11-03 a reader scored the records by hand and did not run the probe (observed: `plans/dry3-key-score-2026-11-03.md` 40). `rota/COMPLETION.md` 120-121 says "two keys written as controls and never run in the loop" (read 2026-11-04).
7. Last result: the hand score, 0 answers whole, 5 partly, 3 missed (observed: the same line).
8. P1 to P6 no.

### B18. The benchmarks (`rota/llm/benchmarks.json`, `probes/bench/RESULTS.md`)

1. Input: the register's `case_runs` and the walk rows (observed: `rota/llm/benchmarks.py` 1-16).
2. Principal: nobody. 3. Output: 94 rows, model by capability with a score. 4. Decider: a share of cases passed.
5. Size: 81 register rows, 8 tool-check rows, 5 walk rows (observed: count).
6. Runs: every row has `recorded_on` 2026-09-12. The last commit on the file is 2026-09-12 (observed: `git log`). The bake-off page is 2026-08-25, with a row added 2026-09-23.
7. Last result: qwen3:8b `walk:merge` 0.048 of 62. No row names `gemma4:12b-it-qat`, the Liaison model of the profile `local` (observed: benchmarks models; `rota/llm/profiles/local.toml` 23).
8. P6 part: model by role, of 2026-09-12. P4 part: the walk share. P1 to P3, P5 no.

### B19. Audit, invariants and faults (`rota/tools/audit.py`, `invariants.py`, `faults.py`)

1. Input: the state of a database, read-only (observed: docstrings).
2. Principal: nobody.
3. Output: printed findings. `faults` writes `status` and `closed_by` on fault rows.
4. Decider: propositions over rows. I3 reads "a merged batch's latest run of each of its own tests at its head is a pass" (observed: `invariants.py` INVARIANTS).
5. Size: 10 invariants and more in `invariants.py`.
6. Runs: no file holds an audit or an invariants output. The scene tests run the invariants in each gate (observed: `test_invariants.py` docstring). Open fault rows: dry3 2, dry8 1, blind1 1, night 175 3 (observed: read-only queries).
7. Last result: not recorded for audit and invariants.
8. P4 part: I3 checks merge state. P1 to P3, P5, P6 no.

### B20. Other probes (`probes/s0_walk.py`, `partition_judge.py`, `downstream.py`, `probe_tools.py`, `onboard_run.py`, `rota/testkit/artefacts.py`)

1. Inputs: a greeter walk with a yes principal (`s0_walk.py`), a partition on six repositories (`partition_judge.py`), artefacts handed to one reader (`downstream.py`), one fixture per model for tool calls (`probe_tools.py`), and a real onboarding scored against `ANSWER_KEY.md` (`onboard_run.py`) (observed: docstrings).
2. Principal: nobody, or a yes script for `s0_walk.py`.
3. Output: printed lines, and the tool-check rows of B18.
6. Runs: no recorded output was found for this read, except the 8 tool-check rows of 2026-09-12.
8. P1 to P6 no, except `s0_walk.py` P4 part.

## Part C: the grid

| instrument | input unit | who plays the Principal | what decides the result | size | times run, last run | last result | P1 | P2 | P3 | P4 | P5 | P6 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Register L1 | one session at one desk | nobody, fixture rows | assertion on rows, calls, messages, k of N | 170 cases | 8,886 live rows, 601k replays; last 2026-11-10 | 26 red, 12 stale | no | no | no | no | no | part: desk by model |
| Register L3 chains | chain of two sessions | nobody | assertion on rows, k of N | 6 cases | in `case_runs`; 2026-11-10 | 2 red | no | no | no | no | no | part: hand-off only |
| Register L3R | one Liaison session, many turns | recorded agent reply | judge's expect line, written before | 25 cases | in `case_runs`; 2026-11-10 | 24 stale | part: reply reading only | no | no | no | no | part: desk by model |
| Register G1 | 4 sessions, 1 chain | nobody | assertion on rows | 5 cases | in `case_runs`; 2026-11-10 | 1 red | no | no | no | no | no | part: desk by model |
| Gate | the whole suite, replay | nobody | pytest against baseline | 7,431 items | count not kept; 2026-11-10 | 30 red, 36 stale | no | no | no | no | no | part: through the register |
| Deterministic suite | rows or scripted scenes | fixed script | assertion on rows | 5,073 functions | each gate; 2026-11-10 | 1 red | no | no | no | part: merge mechanics only | no | no |
| Obligation checks | graph and case set | nobody | case per mode | 2 active checks | each gate | green, full check skipped | no | no | no | no | no | no |
| Walks | whole request | yes script | merged count rises | 156 rows | 156; 2026-10-25 | 14 merged rows | no | no | part: prepared samples | yes | no | part: stop, no cause |
| Nights | three requests, clickI | yes script, then agent | merged row per sentence | 93 nights | 93; 2026-10-28 | 47 nights merged | part: agent from 133 | no | part: one prepared repo | yes | no | part: fabrication counters |
| Agent principal | one page | agent, opus | nothing | 2 briefs | 42 nights | not a result | part: model as person | part: brief holds facts | no | no | no | no |
| Seat driver | whole request, by page | agent or reply file | nothing, prose findings | 2 exchanges | 2; 2026-09-12 | no merge | part: agent at seat | no | no | part: no merge reached | no | no |
| Dry runs | whole request, by turn | the build session | reading afterwards | 10 runs | 10; 2026-11-08 | 3 merged, 7 fold runs 0 | part: session as person | no | part: prepared forks | yes | part: reader, not person | part: reads only |
| Blind run 1 | whole request, tipsI | agent, opus, no tools | key before run, probe | 1 run | 1; 2026-11-10 | no merge, unscored | part: model as person | part: session runs commands | part: pinned sample | yes | part: key, not person | yes |
| Blind test design | 12 tasks, 3 tiers | not named | two keys, probes, ablation | 72 runs designed | 1 of 72; dry9 key only | none | no | no | part: pinned forks | yes | part: probes and page | yes |
| Answer keys, `score.py` | database after onboarding | nobody | key before run | 6 keys | last 2026-11-03 | 9/10 terms, 0/2 constraints | no | no | no | no | no | no |
| Consult probe | database state | nobody | reader compares | 8 questions | no recorded run | hand score 0 whole of 8 | no | no | no | no | no | no |
| Benchmarks | register and walk rows | nobody | share passed | 94 rows | 1; 2026-09-12 | walk:merge 0.048 | no | no | no | part: walk share | no | part: model by role |
| Audit, invariants, faults | database state | nobody | propositions on rows | 10+ invariants | no output kept | not recorded | no | no | no | part: I3 merge state | no | no |
| `nightcount`, `nightreport` | a night database | nobody | nothing | 4 counters | each night; 2026-10-28 | night 175: 78 made-up turns | no | no | no | no | no | part: fabrication by role |

| part | instruments that can confirm or refute it | times those ran in total | last result that bears on it | what the completion line requires |
|---|---|---|---|---|
| P1 a careful person | none with a person. Part: agent principal, seat driver, dry runs, blind run 1, L3R | 42 agent nights, 2 exchanges, 10 dry runs, 1 blind run | blind run 1, 2026-11-10: one page open, no merge | nothing named. `plans/seat-exchange.md` 32-33 names Roman at the TUI as the final test |
| P2 alone | part: blind run 1, agent principal | 1 blind run, 42 nights | blind run 1: no merge, unscored | nothing named |
| P3 own repository | part: walks, nights, dry runs, blind run 1 | 156 walk rows, 93 nights, 10 dry runs, 1 blind run | all subjects are clickI, tipsI or icalendarI samples with earlier rota deliveries | "click and two more lineage repositories merge cold" (`COMPLETION.md` 19) |
| P4 a merged change | walks, nights, dry runs, blind run 1 | 156 + 93 + 10 + 1 | night 175, 2 of 3 merged; dry8 0; blind run 1 0 | click and two more lineage repositories merge cold |
| P5 they can read | part: dry run reads, blind run key | 10 dry runs, 1 blind run | blind run 1 has no merge to read | nothing named |
| P6 honest about the limit | yes: blind run 1 key. Part: register, gate, benchmarks, nightcount | gate each change, 1 blind run | 29 model reds, 6 with "attribut" in the case block | "the register is green or attributed on the shipped profile" (`COMPLETION.md` 19-20) |

The Part A statements against what exists:

| statement | state | evidence |
|---|---|---|
| 1. 114 cases, replayed from the cassettes | does not hold for the count. The replay holds | 206 cases load, plus 30 source entries (count script); `test_l1.py` 121-122 |
| 2. A red carries an attribution note or is owed a fix | cannot be told | 6 of 29 model reds have "attribut" in the case block. "Owed a fix" has no record per case |
| 3. One shape: rows, message, session, deltas, structural | holds | 206 cases carry `forbidden`, 205 `expect` (key count) |
| 4. runs N, pass k on every case | holds | (5,4) 112, (5,3) 52, (3,2) 25, (1,1) 17 |
| 5. T2 arcs replay the three stories | does not hold | no test file reads `STORIES` (grep). The T2 label marks 5 one-session cases. `test_vertical_slice.py` live variant is opt-in and stops at approval |
| 6. Open obligations stay visible and countable | holds in code | `predicates.py` 2484 `REGISTER_ENTRIES`, 2505 `outstanding` |
| 7. Every walk writes a row to `walks.jsonl` | holds in code, not in the main file | `walk.py` 148 writes to its own checkout. 93 nights ran, 156 rows exist, the last 2026-10-25 |
| 8. The register measures one desk, one turn | holds for L1. Not for L3R, many turns | 170 single cases, 7 chains, 25 L3R |
| 9. Page-sequence cases pin the exchange | does not hold | no case key or test name holds a page sequence (grep, 0 hits). L3R cases hold one page each |
| 10. Roman at the TUI is the final test | does not hold yet | no record of a person's run. CLAUDE.md, ruled 2026-10-31: "I will not sit in the seat untill it delivers multiple changes on multiple repos" |
| 11. Score only what the person sees | holds in the blind run 1 key. Scoring cannot be told | `key.md` field 6. No score is recorded |
| 12. Three runs with, three without | does not hold | 1 run of 1 task, with records only |
| 13. Two writers, hash before the run | partly | blind run 1: one writer, committed before the run. Dry run 9: two writers, committed 04:27, not run |
| 14. A wrong merge fails the test, report names the tier | cannot be told | no tier has run |
| 15. Click and two more merge cold, register green or attributed | partly | click merged on 47 nights. tipsI merged on 5 walk rows in September and in dry2. icalendarI merged once, in dry3, with the session at the seat. The register has 30 reds and 36 stale |

## Part D: what the grid does not cover

1. Every subject repository carries earlier rota deliveries. The blind page says so for the three pinned commits (observed: `plans/understanding-test-blind-2026-11-03.md` 15). The tipsI head of blind run 1 is `ff1f65f rota: deliver b_1` (observed: `git log` of its clone).
2. The "real replies" of the 25 L3R cases came from an `opus` agent at the seat on nights 170 to 175, not from a person (observed: `.rota/clickI_night170.principal.jsonl` to `175`; `l3_rulings.yaml` line 1).
3. The agent at the seat holds a brief that gives one fact per change and says what was asked (observed: `probes/principal_brief.md` "What you asked for", "What you know"). The blind run 1 brief says that the prompt already refuses a negative bill (observed: `plans/dry-blind1/recipe.md`, Doubts).
4. `case_runs` stores a row for each replay as well as each live call. 8,886 of 610,509 rows are live (observed: query). A row count is not a count of model runs.
5. The main `walks.jsonl` stops on 2026-10-25, while night databases run to 2026-10-28. The walks of the nights went to worktrees that no longer exist (observed: `launch_night175.sh` 6-11; `ls C:/Users/roman/rota_n*` finds only `rota_night`).
6. The benchmarks table is from 2026-09-12. The Liaison of the profile `local` runs `gemma4:12b-it-qat`, which has no row, and 66 register cases pin that model (observed: `benchmarks.json`; `local.toml` 23; count script).
7. The last gate re-record step named `test_l1.py` for L3R case ids, and every such re-record ended "not found", so the 24 L3R cases stayed stale (observed: `.rota-gate.log` tail).
8. Seven dry runs took the same fold sentence on the same fork `99619246`, and none merged (observed: dry script; `dry8_start.sh` 9). Dry run 9 has a key for the same sentence (observed: `plans/dry9/request.md`).
9. icalendarI appears in no walk row and no night. Its only merge is dry3 (observed: walk counts by repository; night files are clickI only).
10. Open fault rows stay open at the end of runs: dry3 2, dry8 1, blind1 1, night 175 3 (observed: queries of `faults`).

## Part E: limits

- The reader ran no test, no gate and no model, so the current register state is the last gate log of 2026-11-10, not a fresh count. `casestatus` opens the register read-write through `open_dev_db`, so the reader did not run it (observed: `casestatus.py` 498-501; `cassettes.py` 214-224).
- The latest result per case from `case_runs` mixes replays and live calls, so the reader used the gate log for the last result.
- The attribution count is a word search on the case block. A comment above a case can fall into the block of the case before it. The count of 6 is approximate in that way.
- The number of gate runs is not recorded. Only the last log and one baseline exist.
- The night count uses the files in `.rota`. Nights before 82 have no database there, and the walk rows of nights 90 to 165 are missing from the main file. Merge counts per night use the largest `merged` count across the files of one night.
- The reader did not read the dry run read pages, the blind run score, if any, or other readers' pages, by the brief. So the reader cannot say whether any merged change was what was asked.
- The reader did not open the 768 files of `.rota` one by one. Night logs before 175 were not read.
- `probes/frame*` directories, `probes/flowchart` and `rota/tools/regroup.py` and the rename tools were not read in depth. Their docstrings did not name a measure of rota's output.
- Dry run 1 holds four measures in one database. The reader counted it as one run.
