# Frame 326, the provenance read: cases red by construction

Date: 2026-10-25. Read at commit 681d8467 on `rota/foundation`. Read-only, by the rule of 2026-10-18.

Sources:

- `f323_native_read.md` in session 0699ee05's scratchpad, sections 1, 2, 5 and 6.
- The register copy `C:/Users/roman/rota_cassettes_f323.db`, read-only: `case_runs` grouped by case and model, and cassette 62685 (the Tester's native system prompt).
- `rota/tools/map` on `code_probe`, `code_source` and `rota/testkit/fixtures.py`; the code of `code_probe` (`rota/roles/api.py` 14326 to 14390), `_with_repo` (`fixtures.py` 805 to 880), the asker filter (`rota/core/sandbox.py` 655 to 692), and the refusal at `rota/core/worktrees.py` 61.
- The four cases: `tests/rota/cases/l1_developer.yaml` 232, `l1_findings.yaml` 79, `l1_generators.yaml` 9, `l1_tester.yaml` 51.
- `git log -S` and `git show` on the commits named below.
- `plans/stack.md`, the blocks of frames 323 and 326 only; `plans/frame110-design.md`; `plans/wall-guide.md` section 4; `plans/operating-facts.md`, the register section.
- `python -m rota.tools.rulings` on the register, the index, `project_root`, the withdrawal and `answer_critic`. No ruling of Roman's covers any of the four mechanisms (observed: the searches).

## The result

1. Only one of the four cases is red by construction: `L1-TE-log-the-word-you-took-one-way`. The other three can pass on the fixture as built, and the register shows them passing (observed: `case_runs`).
2. The frame's premise is wrong in two places. In the native trial qwen3.5:9b passed `L1-DV-give-the-new-parameters-defaults` 4 of 5 and `L1-TS-fix-a-test-that-asserts-more-than-its-criterion` 5 of 5. `qwen3:8b` passed `L1-DV-challenge-a-test-that-contradicts-its-criterion` 1765 of 1765 since 2026-10-01, all with the empty index (observed: `case_runs`, `at > 2026-10-25T15:07` and `at > 2026-10-01`).
3. The empty index, the missing `project_root` and the `msg.answer_critic` line are measurement faults. Each one gives a seat a read that returns nothing, or a refusal, or a verb it does not have. Each one costs more on a model that leans on reads, which is Gemma (reasoned: section 1 of the trial read).
4. Fault A, the empty index, is unfinished. The fixture's index is opt-in since 2026-08-10, and `code.probe` has no text for an index that holds nothing.
5. Fault B, no `project_root`, is unfinished. Frame 110 gave the Tester's challenge mode `code.source` on 2026-10-02 and gave a repository only to its new case.
6. Fault C, no `ledger.log`, is a design that was never finished. The build session withdrew the tool on 2026-09-12, owed a mode of its own, and marked the case red in a comment that no reader of the register sees.
7. Fault D, `msg.answer_critic` in the Tester brief, is a gap. The brief is static, the working set is derived per wake since 2026-08, and no check compares the two.
8. All four mechanisms were made by the meta workflow, in build sessions. Faults A, B and D show only in the register, because a night always onboards and always has `project_root` (reasoned: the onboarding path and `_with_repo`).
9. The repairs are a case marker, two fixture blocks, one door text and one brief sentence, each with its re-record. A lint that ties a mode's code tools to a `repo:` block generalises the fixture repairs.
10. No repair is a composition question for Roman. Whether to build the owed Terminologist mode or retire the case is an order question, and he re-orders the work himself.

## Fault A. The empty code index under the two Developer cases

- `_with_repo` builds the index only when the case's `repo:` block says `onboard: true`. The comment says "Requested rather than automatic -- it costs a tree-sitter parse of the whole checkout, and only three modes need it" (observed: `fixtures.py` 828 to 835). The option came with the indexer in 0aaedc04, 2026-08-10 (observed: `git log -S`).
- The same day, 7ce38363 put into `developer/tests_failing.md` the line "`code.probe` will find it by the name the test calls" (observed: `git log -S "will find it"`, 2026-08-10). The brief now relies on an index that the fixture of this mode builds only on request.
- `L1-DV-challenge-a-test-that-contradicts-its-criterion` was authored in 8d908e56 and got its `repo:` block in fe3d8ec7, both 2026-08-10, later edited in 2032ff76 (2026-08-28) and 376321b0 (2026-10-01). It never had `onboard: true` (observed: `git log -S`, the case at 232 to 302). Its sibling in the same mode, the "line totals" case, has `onboard: true` (observed: `l1_developer.yaml` 173).
- `L1-DV-give-the-new-parameters-defaults` came with 3d1252c8, 2026-09-10, the finding_violated mode. `finding_violated.tools` names `code.probe`, and the brief does not name it (observed: `grep -c`). The case has a `repo:` block and no `onboard` (observed: `l1_findings.yaml` 87 to 90).
- `code_probe` returns a note on an empty pattern, a note when `index:<batch>` records a failed refresh, and otherwise a bare `[]` (observed: `api.py` 14326 to 14390). The refresh note came with 3ab5c73c, 2026-09-17, the index-refresh design. That design covered an index a commit behind, not an index that holds nothing (observed: the comment at 14378 to 14383; reasoned: a night onboards before any Developer wakes, so an empty index has no night case).
- The design's own condition, "only three modes need it", was not met for the tests_failing mode once its brief said the probe "will find it" (reasoned: the two commits of 2026-08-10).
- Kind: unfinished. The fixture option and the probe were built for the night, and the register case of a probe-relying mode never got the option. No ruling of Roman's is involved (observed: the rulings search). Wall guide section 4, step 4: the probe answered right for its rows, and the step after it is wrong, so cause 9, a result that points the seat wrong (reasoned).
- Effect: not red by construction. `qwen3:8b` passes the challenge case without a probe hit, 3039 of 3044 in all and 1765 of 1765 since 2026-10-01 (observed: `case_runs`). qwen3.5:9b passes the defaults case 2488 of 3382 in all and 4 of 5 native (observed: `case_runs`). Gemma loops on the empty result (observed: the trial read, section 1).

## Fault B. No `project_root` under the Tester case

- `project_root` enters a register database only in `_with_repo`, which runs only when the case has a `repo:` block (observed: `fixtures.py` 825 to 826 and 1287 to 1288). `code.source` without it refuses with "no project_root in config: refusing to guess which repository to create a worktree in" (observed: `rota/core/worktrees.py` 61).
- The design condition is in the `_with_repo` docstring of 2026-08-10: "Critic reads a diff; Architect reads source; Developer writes files. A case for any of them against a database with no repository is a case where the role correctly declines to act, and reads as a failure" (observed: `fixtures.py` 807 to 813).
- The Tester gained `code.source` in its challenge mode in ab70f47a, 2026-10-02, frame 110 pass 1, under the ruling of 2026-09-24 21:20 that a test whose last run failed before any assertion needs the code it calls (observed: the commit; ruled: Roman, 2026-09-24 21:20, cited in `challenge.tools`).
- Frame 110's design added one new case with a repository and planned only re-records for "the two challenge cases" (observed: `plans/frame110-design.md` 79). Of the six Tester challenge cases, three have no `repo:` block, `L1-TS-fix-a-test-that-asserts-more-than-its-criterion` among them (observed: `l1_tester.yaml`).
- The build did not meet the docstring's condition for the older cases of the mode it widened (reasoned: the condition names any role that reads source).
- Kind: unfinished, by the meta workflow on 2026-10-02. The refusal also speaks of a worktree to a seat that asked to read a file, which is cause 9 in the register only (reasoned: wall guide section 4, step 4).
- Effect: not red by construction. The brief sends the Tester to `code.source` only when the last run failed before any assertion. This case seeds no test run, and `tests.consult` gives the body (observed: the case at 51 to 85). qwen3.5:9b passed 5 of 5 native, and `qwen3:4b`, `gemma3:12b` and `llama3.1:8b` passed on text (observed: `case_runs`).

## Fault C. No `ledger.log` in the Terminologist deliver working set

- c12ed6c2, 2026-09-09, added a word-sense paragraph and `ledger.log` to `terminologist/deliver`, and the case `L1-TE-log-the-word-you-took-one-way` measured it (observed: `git log -S`, the case comment).
- d207a0bd, 2026-09-12 14:48, withdrew both. `L3-ratified-statement-becomes-a-term` read 0 of 5 on both 8B models with them. The message says "the generator is owed as a mode of its own keyed by its cause, and the L1 case that measured it is an attributed red until then" (observed: the commit). The case comment says "Red until that mode exists" and cites the memory `rota-tool-in-the-list` (observed: `l1_generators.yaml` 14 to 19). That memory is not in the archive under that name (observed: `memory/archive/`).
- The owed mode was never built. No frame on the current stack holds it (observed: grep of `plans/stack.md`).
- The case still expects `ledger: {count: "1..2"}` from a mode that has no tool to write the ledger (observed: the case at 36 to 37). The case schema has no field for "red by construction", and the loader reads none (observed: `load_case`, `fixtures.py` 302 to 339). So a comment is the only marker, and the per-model table of frame 323 counted the case as a model failure (observed: the frame 323 block, third end condition).
- 7ce38363's reachability lint of 2026-08-10 checks only the wake, and it declined to check a write's reachability on cost (observed: the commit message). That decision is why no check refuses a case that expects a write no tool in the mode can make (reasoned).
- Kind: a design that was never finished. The withdrawal was the right repair to the L3 red. The owed mode and the marker for the red case were both left as words (reasoned).
- Effect: red by construction on every model since 2026-09-12. `qwen3:8b` 0 of 2812, qwen3.5:9b 0 of 25, Gemma 0 of 10. `llama3.1:8b`'s 80 of 100 are undated rows, read as from before the withdrawal (observed: `case_runs`; proxy for the date).

## Fault D. The Tester brief names `msg.answer_critic`

- 7592f233, 2026-09-14, finding 73 of night 69, added a tester-to-critic answer edge to the graph, `msg.answer_critic` to `tester/challenge.tools`, and to the brief: "answer whoever disputed it, `msg.answer_developer` or `msg.answer_critic`" (observed: the commit).
- The working set keeps only the answer verb to the sender of the wake's message. The rule is in `sandbox.py` 655 to 692, with roots in c363b4f2 (2026-08-14) and 084731b6 (2026-08-18). Its comment says "Derived, there is nothing left to get right" (observed: the code and `git log -L`).
- So on a challenge from the Developer the working set lists `msg.answer_developer` and not `msg.answer_critic`, while the brief names both (observed: cassette 62685, the list "Your working set is exactly these functions").
- The Terminologist's question brief met the same tension with "exactly one of them is in front of you" (observed: `terminologist/question.md` 7 to 8). The Tester brief of 2026-09-14 did not take that form (reasoned).
- `test_a_brief_names_at_least_one_of_its_own_calls` compares a brief with its `.tools` file, not with the derived working set (observed: `tests/rota/test_prompts.py` 756 to 784).
- Kind: a gap. No design compares a static brief with a working set derived per wake (reasoned). Cause 10 in its shape, a call the text offers and the mode lacks, in wall guide section 4, step 4 (reasoned).
- Effect: small. Gemma sent `msg.answer_critic` once per run and was refused, then sent `msg.answer_developer` (observed: the trial read, section 1). The case still fails for Gemma on the branch it takes.

## The repairs

1. Fault C, a case marker. Add one field, for example `red: "<the reason and the owed mode>"`, to `L1-TE-log-the-word-you-took-one-way` in `tests/rota/cases/l1_generators.yaml`. Make the per-model table and `rota/tools/casestatus.py` list a marked case apart and count it in no pass rate. Size: one case line and about ten lines of reader, with one pin. The owed mode, or the retirement of the case, is a separate frame. Roman orders that frame, and it is not a composition question.
2. Fault A, a door text. On no match, when `code_index` holds no row at all, make `code_probe` in `rota/roles/api.py` say that the index holds no code and that `code.source` reads the file. Size: about eight lines and a red test on the two Developer cases, frame 326's second end condition. No re-record is needed, because the probe's result is a turn and not the prompt (reasoned).
3. Fault A, the fixture, optional. Add `onboard: true` to the two Developer cases. Size: one line each, plus re-records of both cases on every compared model. Caution: the sibling case went from 5 of 5 to 0 of 5 when its index changed, so treat the new numbers as a new record, not a continuation (observed: `l1_developer.yaml` 150 to 172).
4. Fault B, a fixture block. Give `L1-TS-fix-a-test-that-asserts-more-than-its-criterion` a `repo:` block with batch `<b1>` and a `truncate` source, and do the same for the two other Tester challenge cases without one. Size: about ten YAML lines per case, plus re-records.
5. Faults A and B, the general form. Extend `tests/rota/test_case_reachability.py`: a case whose mode's `.tools` names `code.source`, `code.probe` or `code.read` must declare `repo:`, and a mode whose brief relies on the probe must declare `onboard: true`. Size: about thirty lines. This repair fits the workflow and not one case (reasoned: the overfit rule of 2026-10-15).
6. Fault D, a brief sentence. Change the answer line of `rota/roles/prompts/tester/challenge.md` to answer the role that sent the challenge, with the one `msg.answer_` call the working set offers, in the form `terminologist/question.md` uses. Size: one sentence, plus re-records of the Tester challenge cases, whose prompt changes.
7. Frame 323's table, read again with fault C's case set apart and the three measurement faults named per case, frame 326's third end condition. Size: one read, no code.
