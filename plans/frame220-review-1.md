# Frame 220, review 1 of pass 1: the fence's baseline holds the base commit

Worktree `C:/Users/roman/rota_r283old` at 21f0e7b0, read-only. Reviewer: Opus agent, 2026-10-17.

Verdict: the pass stands. No finding is high. Two low findings sit on the points, and three low findings sit outside them.

## (a) Verdicts on the points

1. `_base_held` keeps its behaviour. Frame 283's three files give 74 passed at the parent and 74 passed at HEAD. CONFIRMED.
2. Every shape is accepted. A list, one tree, `None` and a list with `None` inside it all work. An empty list refuses every reach, as `None` did. CONFIRMED.
3. A path that the base lacks gives `""`. The fence then uses the working file alone, and no error occurs. CONFIRMED.
4. When the base text fails to parse, the baseline holds the working tree only. The write is refused only when it adds a new reach. That fails closed, and it is right. CONFIRMED.
5. At the parent, the new restore test fails with the fence's own refusal ("reaches the dynamic at line 1 (import importlib.metadata)"). The companion test passes. CONFIRMED.
6. No script is in `f220/`. My recount gives 19 by the implementer's method. It gives 21 by the sum of increments, which is also a floor. Night 154 gives 11 or 13, never 16. Neither count is exact. The ratio holds: every fire except `import pickle` restores a base line. PLAUSIBLE.
7. No record expects the fence to refuse a restore of a dynamic reach. `rota/DECISIONS.md` line 1509 names frame 220's fix as "the fence's baseline is the batch's base commit". CONFIRMED.

## (b) Findings

1. Point 6, low, PLAUSIBLE. The count 18 of 19 takes the largest count of refusals in one turn of each session. `turns.user` drops older refusals as the history is cut. The sum of positive deltas per turn gives night 154 13, not 11. The total is then 21. Night154-read's 16 does not come from `turns.user`: the text "line 49" occurs 6 times, and "line 100" occurs 16 times. Fix: count the refusals per turn from deltas, keep the script in `f220/`, and write "at least 20 of 21".
2. Point 6, low, CONFIRMED. The brief names "the implementer's script in the `f220/` folder", but the folder holds only the briefs and `pass1-report.md`. Fix: save the count's SQL beside the report so a review can run it again.
3. Outside, `rota/roles/api.py` 16193, low, CONFIRMED. `_batch_base` sits outside the `try` of `_base_text`. A `project_root` failure that is not `WorktreeError` now propagates on every fence write. Before the pass, this path ran only on the commit door. My probe raised `sqlite3.OperationalError: no such table: config` from `_base_text`. A live database holds `config`, so the risk is small. Fix: move the `_batch_base` call inside the `try` and return `None` on any error.
4. Outside, `rota/roles/api.py` 15009, low, CONFIRMED. An absolute path gives `""` from `git show <fork>:<abs>`. The fence then falls back to the working file, and the restore is refused again. `./a.py` and a relative path work. Fix: make `wpath` relative to `_root` before the call, when it is under the root.
5. Outside, `tests/rota/test_desk_guards.py` 4815 to 4861, low, PLAUSIBLE. The new test's repo is not the project root. So `worktrees.base` returns `HEAD~1`, and HEAD~1 here is the base by construction. No case covers a batch with two or more commits through the `merge-base` route. A batch commit can then shadow the fork. Fix: add one case with two batch commits and a project root set in `config`.

Not a finding: each write now runs `rev-parse` and `show`, two more git calls. The implementer named this cost in the pass report.

## (c) Probes

- Frame 283's files at HEAD: `pytest tests/rota/test_frame140_commit_beside_note.py tests/rota/test_revert_door.py tests/rota/test_seam_start.py`, which gave 74 passed.
- The parent tree went through `git archive HEAD~1` into `scratchpad/f220/r1parent`, with HEAD's `test_desk_guards.py`. The same three files gave 74 passed. The new tests gave 1 failed (the fence refusal) and 2 passed. The worktree was not checked out.
- `scratchpad/f220/r1_probe3.py`: `_base_text` with an absent path, a present path, root `None`, an absolute path and a `./` path. `fence.check` with `[]`, `None`, one tree, and `[None, tree]`. `ast.parse` on bad syntax and on a null byte. Both parse failures raise `SyntaxError`, which the pass catches.
- Inline SQL, read-only, over `D:/repos/rota/.rota/clickI_night140.db` to `clickI_night154.db`: the developer refusals per session as the maximum and as the sum of deltas. A second query counted `reaches the dynamic at line` by line number on night 154.
- Grep: `rota/LAWS.md` (law 12 is "Constraints protect external commitments only", and the text "prediction, never a permission" is at line 339), `rota/DECISIONS.md` lines 1498 to 1512, and `rota/roles/briefs`, which gave no fence match.

All scratch paths are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0162323a-8602-4856-80d2-0fa70223b3b2/scratchpad/`.

## (d) Usage

The harness gives the exact count. My estimate is about 60k input, 9k output, and 69k in total.
