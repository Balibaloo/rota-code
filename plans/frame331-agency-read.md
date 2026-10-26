# Frame 331, the agency read: a fixture per owed case, or the night's world by default

Date: 2026-10-26. Read at 46e5c88b on `rota/foundation`. Read only. The register is read from a copy, `reg331.db` in session 8db3a3f9's scratchpad, taken from `tests/rota/cassettes.db` at 18:18.

## The result

The frame's fix sits at one door of 33. It gives a repository to the 10 cases in `OWED`. The cause by the code is one level up: the case kit builds a night's world only from the keys each case declares, and a night always has the repository, `project_root`, the index and the delivery state (observed: `fixtures.py` 846 "Requested rather than automatic", 1371 to 1372 `if case.get("repo")`; `frame326-provenance.md` result 8). Two of the frame's three premises are stale. `OWED` holds 10, not 19, and the guard reads 10, not 27, since bc5e50a4 of 2026-10-25 23:57 (observed: `test_case_reachability.py` 211 to 228). `index_batch` is already a key a case names, `repo.index_batch`, read at `fixtures.py` 898 (observed). The fourth Tester case is recorded: 1030 runs on qwen3.5:9b, newest 2026-10-26 18:16, 0 of 5 on its last replay (observed: `case_runs` in the copy).

## 1. The purpose

- `OWED` and `OWED_CEILING` came with fd1ee7a0 (2026-10-25 19:11) and 14bf6317 (23:39), frame 326 passes 1 and 1b. The lint closes faults A and B of frame 323's native trial: an empty index under a probe and no `project_root` under `code.source`. `OWED` excuses the cases the lint found and could not fix in one YAML line (observed: the commits; `frame326-provenance.md`, faults A and B).
- `index_batch` came with 30abb274 (2026-10-25 23:38) from review 1, finding 1: `onboard: true` indexes main before the batch edit exists. 38e142b0 (2026-10-26 00:35) added `_delivery_index` from review 1b, finding 1, so the run ends in a night's delivery state (observed: the commits; the frame 326 status lines of 23:32 and 00:28).
- The opt-in itself is 0aaedc04 of 2026-08-10: the index "costs a tree-sitter parse of the whole checkout, and only three modes need it" (observed: `fixtures.py` 842 to 845).
- No ruling of Roman's made any of these. Each one is a build decision of the meta workflow (observed: `frame326-provenance.md` result 8 and its rulings search). Frame 331 itself rests on Roman's "ok" of 2026-10-25 23:21 to three recommended frames (ruled: Roman, transcript 66edc387 at 23:21).

## 2. What exists

| Thing | Where | What it does |
|---|---|---|
| The repository builder | `rota/testkit/fixtures.py` 819 to 901, `_with_repo` | Sample repo, `project_root`, worktree, edit commit, `onboard`, `index_batch` |
| The call sites | `fixtures.py` 1371, 1462 | Run `_with_repo` only when the case has `repo:` |
| The delivery state | `fixtures.py` 904 to 966, `_delivery_index` | Writes each onboarding phase's end by hand. Four tables differ from a night (observed: review 1c) |
| The night's re-index | `rota/core/lifecycle.py` 58, `_reindex_batch`; `rota/core/runner.py` 6615, `_refresh_index` | The product path a night runs after a Developer commit |
| Onboarding | `rota/onboarding/boot.py` 92, `boot.onboard` | Writes `project_root`, the index, the areas, constraint zero |
| A keyed template cache | `rota/testkit/gitfixture.py` 149, `template(key, build)`; 178, `copy_template` | Builds a repository once per process per key and copies it (frame 203) |
| A seat-derived tool set | `tests/rota/test_case_reachability.py` 236 to 268, `_code_problems` | Reads each seat's tools from `prompts.mode_tools`, and from the sandbox when no file exists |
| A hand list of code tools | `test_case_reachability.py` 202, `CODE_READS` | Three tools: `code.source`, `code.probe`, `code.read` |
| Hand-seeded index rows | 6 cases: `l1_architect.yaml` 107, 142, 498; `l1_surface.yaml` 25; `l1_tester.yaml` 1432, 1683 | Stand-ins for the night's index |
| Inline Click source | 3 cases: `l1_tester.yaml` 268, 787, 1569 to 1653 | Copies of the night's files, about 640 lines at 787 |
| The night's source | `D:/repos/_AI/sample_repos/clickI`, restored before each night; `.rota/clickI_night<N>.db` | The base checkout and each night's register (observed: `operating-facts.md` 52, 183) |

## 3. The reach

The gap: a seat holds a tool that reads the repository or the index, and the case's world holds neither, or holds a hand copy of the night's. The count comes from `reach331.py` in this session's scratchpad, which reuses `_seats` and `prompts.mode_tools` (observed).

- **10 cases in `OWED`** have no `repo:` (observed: `_code_problems` on each). Four cite Click source: `L1-AR-rewrite-the-guess-from-the-ruling`, `L1-AR-re-annotate-from-the-principals-correction`, `L1-DV-say-why-the-test-cannot-pass`, `L1-TS-act-on-the-reason-of-a-challenge`. Six cite none. Each of the 863 runs of the Developer case holds "no project_root" (observed: `case_runs`).
- **16 cases outside `OWED`** hold an index or worktree tool that `CODE_READS` does not list, with no repository and no index (observed: the script). Ten Vision Keeper cases hold `problem.assert`, whose grain refusal at `api.py` 2139 never fires on an empty index. Four Architect cases hold `model.amend`, whose stranger check at `api.py` 3827 runs only `if bindings and indexed`. Two of them also hold `code.diff`, which reads `project_root` at 16901. Two Terminologist `criterion_repair` cases hold `code.callables`, which returns a note at 16582. The lint passes all 16 (reasoned: rule 1 keys on three tools, rule 2 on one).
- **4 cases with a hand copy**: `L1-AR-guess-the-code-of-a-request` (seeded index), `L1-TS-pass-a-literal-value-for-a-name-looked-up-at-run-time` (inline `decorators.py` and seeded index), `L1-TS-assert-the-value-the-surface-returns` (three inline files and seeded index), `L1-TS-send-a-test-written-into-the-reply-as-tests-encode` (inline `utils.py`) (observed: the grep in section 2).
- **3 kit places**: the opt-in at `fixtures.py` 846 and 1371; the hand list `CODE_READS` of 3 tools, where about 21 tools read `code_index` or `project_root` in `api.py` (observed: a scan of `api.py` for those names); and `_delivery_index`, which writes onboarding's end state again by hand (observed: 904 to 966).

N = 33: 30 cases and 3 kit places (reasoned: the sum). The empty-index branches at `api.py` 3315, 3827, 5406, 7466, 14799 and 16582 are where the gap lands. They are right for a greenfield project, so they are not counted (reasoned).

## 4. The fix against the reach

The fix is proposed only. Its Ends-when and the 00:49 status line of frame 326 name `repo.edit_from`, one shared source file per case, for the owed cases (observed: the stack). It covers the 10 `OWED` cases if each gets a `repo:` block. It covers 11 if the sibling inline copy moves to the shared file (reasoned). It leaves the 16 unlinted cases, 3 of the 4 hand copies, the opt-in default, the hand list and `_delivery_index`. The next mode that gains a code tool opens the gap again, and the lint sees it only if the tool is one of three (reasoned: `CODE_READS`). Passes 1c and 1d already meet part of Ends-when 1 and all of Ends-when 3 (observed: the result above).

## 5. The proposal

Not the same fix. Put the night's world in the kit as the default, and let a case name only a departure:

1. Derive the repository from the seat: `run_case` and `run_chain` call `_with_repo` when any seat's tools read code, by the derivation `_code_problems` already makes (`test_case_reachability.py` 236; `fixtures.py` 1371, 1462).
2. Default to the delivery state: `_delivery_index` runs unless the case says `repo: {greenfield: true}`, so `index_batch` and its 17 lines go (`fixtures.py` 898 to 901; a build decision, no ruling).
3. Build one Click template, not one file per case: `repo: {project: click}` builds the night's base files the 7 Click cases cite through `gitfixture.template("click", ...)` (`gitfixture.py` 149), from the clickI checkout (`operating-facts.md` 52), with `edit:` as the batch's diff.
4. Replace `CODE_READS` and `OWED` with one rule: a case that leaves the default names its reason, in the form of the `red:` marker of frame 326 (`test_case_reachability.py` 202, 211).
5. Re-record the cases whose first prompt moves, about 30, in one gate (reasoned: re-records are cheap, the rule of 2026-09-20 cited at frame 326's 23:55 line).

Price: 4 cycles, an instrument fix of 3 and one gate with re-records (observed: `operating-facts.md` 239 to 252, "an instrument fix, 3"). The holder spends about 40k of context at 10k a cycle. Agents spend about 180k: a cold implementer pass 75k, a cold review 70k, a resumed pass 30k, the gate 6k (observed: the same anchors). The frame's own price is 2 to 3 cycles for 10 cases (observed: the stack).

## 6. The doubt

- The parse cost that made the index opt-in on 2026-08-10 is not measured here. A Click template on each code-reading case can slow the suite, and the template cache must hold the index as well as the tree (reasoned: `fixtures.py` 842).
- The 16 unlinted cases are counted by tool, not by effect. I did not read each case to show that its expected write depends on the index. The effect on the Vision Keeper cases is probably small (reasoned).
- I did not check that the clickI checkout still sits at the base commit the Click cases cite. I did not read `rota_p326` or a night register for the four tables that review 1c names.

## Verdict

`at one door of 33`: the fix covers 10 of 33, the `OWED` cases, or 11 with the sibling inline copy. It leaves 16 cases whose code tools the lint does not list, 3 hand copies of the night's source or index, the opt-in at `fixtures.py` 846 and 1371, `CODE_READS` at `test_case_reachability.py` 202, and `_delivery_index` at `fixtures.py` 904 (observed: sections 3 and 4).
