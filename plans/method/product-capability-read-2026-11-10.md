# The capabilities of COMPLETION.md against the code and the runs, 2026-11-10

A blind read for the product review. The reader read `rota/COMPLETION.md`, `plans/composition.md`, the code under `rota/`, and 110 run databases read-only. The reader read no product, map, design or meta page of the review.

## Result

1. The page is not a status record by its own rule. It "takes no status update after 2026-09-17" (observed: COMPLETION.md 11 to 12). Ten of its eleven states are the reading of 2026-09-12 and 2026-09-13.
2. Marks: 3 true, 6 stale, 1 contradicted, 1 not testable. No capability is done by the page or by the code.
3. Each lineage repository merged once from zero: clickI in dry run 1, tipsI in dry run 2, icalendarI in dry run 3, all on 2026-11-02 (observed: `batches`, git). Since 2026-11-03, 8 runs gave 0 merges.
4. Each of those three merges breaks a promise of its repository, by the blind test page (observed: `plans/understanding-test-blind-2026-11-03.md` lines 15 to 17, the commits 4fcd6d7 and 08aab3c8).
5. The completion line cannot hold by its letter today. G1 and the principal's flow are not built, F1 is parked, and the gate baseline holds 33 reds (observed: `.rota-gate.json`).
6. If the line held, the destination still would not. No condition of the line and no capability measures "a careful person", "alone" or "they can read" (reasoned: section 3).
7. Every run had a model or the build session in the Principal seat, never a person (observed: the dry run recipes, `plans/dry-blind1/recipe.md`).

## 1. The capabilities

Counts are over 110 databases: 12 dry and blind runs and 98 click nights, 2026-09-18 to 2026-11-10 (observed: `scratchpad/capability/survey.tsv`, `detail.tsv`). "Dry" below means the 12 dry and blind runs.

| # | Capability, and its state on the page | Measure on the page, and the latest result | Code today | Runs | Mark | Destination |
|---|---|---|---|---|---|---|
| 1 | A1, the interview. Partial, read 2026-09-12. | No count. Owed: a brief re-record, the Researcher route, two cold walks. The walks ran: 12 dry runs from zero (observed: `sessions` with `tick:survey` in all 12). The Researcher case `L1-VK-an-outside-fact-is-the-researchers` is red at 2026-11-10 07:19 (observed: `.rota-gate.json`). | Built and used: the signoff gate (`predicates.py` 362), the contest loop, the identical-clarify refusal (`sandbox.py` 3754). The Researcher edges are in `rota/design/graph.json`. | 58 Researcher sessions, 0 `references_` rows in 110 runs (observed). Dry run 9 asked 3 repeated questions (observed: `plans/dry9-read-2026-11-10.md` count 4). | stale | a careful person, alone |
| 2 | A7, cost before commitment. Partial, lines of 2026-09-12 and 2026-09-13. | No count. "Night 38 is the first honest walk". The bands rule says the night summary reports a stray judged. `nightreport.py` has a contest line and no stray line (observed: grep). | Built and used: `touch_strays`, `touch_strayed` and `touch_mistaken` (`predicates.py` 2850 to 2896), the merge hold (`lifecycle.py` 1196 to 1203), `restore.py`. The page calls the Architect's judged guess "for later". It is built: `touch_guesses`, ruled 2026-10-18 (observed: `schema.sql` 403 to 417). | 73 stray rows: 29 mistake, 9 foreseen, 35 open. 24 `touch_strayed` and 57 `touch_mistaken` sessions (observed). Dry run 9: 0 of 2 restores by the structure. Night 118 merged `echo_json_group` with an open stray on a commit that is not the head (observed: the gate reads the head only). | stale | they can read |
| 3 | E1, amendment. Partial, 2026-09-12. | No count. Owed: one pinned test for the merged half, two tipsI walks. The test exists since 2026-09-12: `test_an_amended_delivered_item_owes_new_tickets_and_keeps_its_merged_batch` (observed: `tests/rota/test_steering.py` 270, a0a276db). No tipsI walk amended an item: dry run 2 and blind run 1 hold 0 items above version 1 (observed). | Built: `cancel` (`predicates.py` 1975), slicing on a risen version. | Nights: 49 abandoned batches, 291 items above version 1. 0 batches in 110 runs start on an item after its merged batch (observed). The merged half never ran in a run. | stale | a careful person |
| 4 | A5, conflicting sources. Partial, 2026-09-12. | No count. Owed: a re-record, a walk on a repository seeded with one conflict. No seeded repository is among the 4 run repositories (observed: `config`). The case `G1-a-ratified-conflict-is-caught-by-the-owner` is red at 2026-11-10 (observed). | Built and used: the reconcile phase (`predicates.py` 2390). | 329 reconcile sessions in dry runs. 127 `conflict` ledger rows in dry runs, 7 on a page, all 7 in dry run 1. Dry runs 2 to 9: 0 of 120 on a page, all open at the end (observed). Six sampled rows of dry run 9 restate the README and agree with the code (observed: `ledger`). | contradicted | a careful person |
| 5 | B5, questions at any time. Struck as built, 2026-09-17. | None. | Built: `rulings.rule(ask=...)` (`api.py` 16450 to 16843). | 0 replies with a question mark in 173 landed rulings of dry runs. 27 in 3,541 night rulings (observed). The reader could not tie an answer to each question from the rows (reasoned). | not testable | alone |
| 6 | D3, hollow verification. Partial, 2026-09-12. | Owed: "a click night on that profile". 82 walks ran on `local-gemma-critic`, 2026-09-13 to 2026-09-16, 7 merged (observed: `walks.jsonl`). The case `L3-a-failed-verdict-turns-into-a-fix` is red at 2026-11-10 (observed). | Built: `local-gemma-critic.toml`. The default profile is `local` (`profile.py` 271), and its Critic is `qwen3.5:9b` since 2026-09-09 (`local.toml`). The case comment says the local Critic is gemma3:12b (`l1_judgement.yaml` 520), which `local.toml` contradicts. | The Critic ran on qwen3.5:9b in 104 of 110 runs, gemma3:12b in 3 (observed). 18 fail verdicts in nights, 8 then passed. 0 fail verdicts in dry runs. Dry run 2 merged tests with `assert True` after each block (observed: `plans/dry2-wall1-read-2026-11-02.md` 52). | stale | a merged change, honest about where small models stop |
| 7 | G1, dynamic stacks. Partial, "largest unbuilt piece", 2026-09-12. | Needs a sample repository per language. None ran (observed). | Not built. The indexer reads 7 languages (`languages.py` 38 to 80). The provisioner is "Python only" (`provision.py` 17). The harness reads pytest output (`harness.py`). | 4 repositories, all Python (observed: `config`). | true | none: the destination names Python |
| 8 | F1, budgets. Parked until a remote provider, 2026-09-17. | None. | Turn caps built (`loop.py` 223). `budget_usd` is read in `profile.py` 59, 102 and 144 and nowhere else (observed: grep). | All 110 runs on local Ollama (observed: `config`). The 40-session cap ended 4 of 7 turns of dry run 9 (observed: the dry run 9 read, D9-10). | true | none |
| 9 | The seat as an exchange. Partial, 2026-09-12. | Owed: first exchanges on tipsI and click, and their cases. They ran: dry run 1 on clickI (41 pages), dry run 2 and blind run 1 on tipsI (observed: `messages`). | `probes/seat.py` is built and unused since 2026-09-15 (observed: git log). The dry runs land replies by `rota sign --say` (observed: `dry9_turn.sh`). | 25 page-and-reply cases, all from nights 170 to 175 (observed: `l3_rulings.yaml`). 0 cases come from a dry-run page (observed: grep). Only blind run 1 keeps each page whole. | stale | alone |
| 10 | The principal's flow. Partial, 2026-09-13. Gated on click's first cold merge. | Defaults ship "after Roman drives one batch on each path at the TUI". Roman refuses the seat until rota delivers (ruled: 2026-10-31 00:58). | Not built. `batches.depend` has no tool, and no code writes `batch_dep_facts` (observed: grep). `scheduler.py` 1862 reads the table. | 0 `batch_dep_facts` rows in 110 runs. All 77 merged batches hold one ticket (observed). Its gate opened on 2026-11-02, dry run 1 (observed). | true | alone, they can read |
| 11 | The structure's model of the project. Partial, read 2026-11-04. | Three measures. Answers: the consult set scored 2.5 of 8 by hand on dry run 3, 2026-11-03, not by the probe (observed: `plans/dry3-key-score-2026-11-03.md` 40). Future work: 1 of 12 trap tasks ran once, blind run 1, records not withheld, no merge (observed). Operation: no record counts it. | Built since the read: the commitment columns `party`, `behaviour`, `witness` (`schema.sql` 242 to 264), the pushes (`runner.py` 4568 to 4578), `failed_commitment`, the shape module (`shape.py`, 2026-11-04). | 189 candidates per icalendarI run from dry run 5. 20 to 32 stated commitments. Dry run 9: 3 of 6 criteria keep a commitment. 0 tests and 0 verdicts name a commitment in any run. A proxy for operation: the bound block reaches 1 of 4 delivery sessions in dry run 9 (observed). | stale | a merged change, honest about where small models stop |

## 2. The completion line

"Core is complete when every partial is built, click and two more lineage repositories merge cold, and the register is green or attributed on the shipped profile." Ruled 2026-09-12 and confirmed by Roman that day (observed: COMPLETION.md 18 to 21).

1. **Every partial is built.** No. G1 and the principal's flow are not built. F1 is parked by ruling, so this condition fails by its letter while F1 stays on the partial list (reasoned).
2. **Click and two more lineage repositories merge cold.** Held once, by its letter, if a dry run counts as cold. The runs onboard from zero (observed: 8, 4 and 50 survey sessions).
   - clickI: dry run 1, 4fcd6d7, `click.pause()` returns a bool. The blind page finds no CHANGES.md line and no `versionchanged` note (observed: the blind page line 17).
   - tipsI: dry run 2, e40742e merged as ff1f65f. The guard sits in both copies of `calculate_tip`, and the tests carry `assert True` (observed: the dry run 2 read).
   - icalendarI: dry run 3, merged as 4f12af1e. Its tests sit in a top-level `tests/` outside `testpaths` (observed: the blind page line 15, commit 08aab3c8).
   - After 2026-11-02: dry runs 4 to 9 and blind run 1 merged nothing (observed). The nights merged 74 batches on clickI, 2026-09-18 to 2026-10-28 (observed). The reader did not check whether a night started from zero.
3. **The register is green or attributed on the shipped profile.** No. The gate baseline of 2026-11-10 07:19 at d856c51d says "33 failed, 7369 passed, 49 skipped, 16 xfailed", model `qwen3:8b` (observed: `.rota-gate.json`). The 16 xfailed carry a `red:` mark, and that mark is an attribution (observed: `test_l1.py` 209 to 220). The 33 carry none (observed). "The shipped profile" names no file: the default is `local`, and the page names `local-gemma-critic` (observed).

If the line held, the destination would not follow from it. The line counts merges, not merges that keep a promise, and the three merges above each break one (reasoned). It says nothing of a person in the seat, of a read of the change, or of a stop the person sees (reasoned).

## 3. The parts of the destination

| Part | Capabilities that serve it | Condition of the line | Covered by a measure that a run gives |
|---|---|---|---|
| a careful person | A1, E1, A5 | none | no. No run had a person in the seat (observed) |
| alone | A1, B5, 9, 10 | none | no. The build session ran every command, blind run 1 included (observed: its recipe) |
| a small Python repository | all but G1 | "lineage repositories" | yes. 4 small Python repositories (observed) |
| a merged change | D3, 11 | "merge cold" | yes, the merge count. Not the promise kept (reasoned) |
| they can read | A7, 10 | none | no. No capability names a read of the merged change as its measure (reasoned) |
| honest about where small models stop | D3, 11 | "green or attributed" | in part. The register attributes 16 reds. Of 11's trap tasks, 1 of 12 ran. The dry run 9 stop scored 0 as an honest stop (observed: the dry run 9 read, result 2) |

Parts with no capability measure: "a careful person", "alone" and "they can read". Two capabilities serve no part: G1 and F1 (reasoned).

## 4. The counts of the marks

- true: 3 (G1, F1, the principal's flow)
- stale: 6 (A1, A7, E1, D3, the seat as an exchange, the structure's model)
- contradicted: 1 (A5)
- not testable: 1 (B5)

## 5. Limits

- Only capability 11 names a count that a run can give. The other ten name owed work, not a count. So "stale" means the owed work moved, and it does not mean the capability is done (reasoned).
- The A5 mark rests on the `ledger` kind `conflict`. The sampled rows do not disagree, so the rows may be mislabelled and not lost conflicts (reasoned).
- "Cold" is not defined on the page. The reader took onboarding in the run as cold (reasoned).
- The night databases are a copy at the end of each night. A row that a later step overwrote is not seen (reasoned).
- The reader did not run the gate, `casestatus` or any probe. The register state is the stored baseline of 2026-11-10 07:19 (observed).
- The B5 questions were not followed to their answer pages. The proxy, a message caused by the reply, found 2 of 27 (observed). The proxy can miss an answer that a page carries.
- The operation measure of 11 has no defined query. The reader's proxy is the bound-constraints block in the first prompt of `batch_start`, `tests_missing` and `review` sessions. That block is a push, not a citation (reasoned).
- The reader did not read `plans/stack.md`. A frame there can close an owed item that this read calls open.
- The scripts and the tables are in `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/1efd37b1-058e-4b19-8ab1-e1a6c654a389/scratchpad/capability/`.
