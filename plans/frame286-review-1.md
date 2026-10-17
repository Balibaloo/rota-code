# Frame 286, review 1 of b0dbd926: the unnamed-definition door records a stray

Rota workflow. Read-only review on the worktree `C:/Users/roman/rota_r283old` at b0dbd926, 2026-10-18. The commit stands. No high finding. Three lows.

## (a) Verdict per point

1. CONFIRMED. The door sets `unnamed_note` in place of the `raise`, and the result carries it under `not named`. The parent's two refusal tests fail on HEAD code with "DID NOT RAISE".
2. CONFIRMED. The commit writes `src/click/utils.py::echo` open. A path-grain stray of the same commit gets the path row only. An earlier grain or bare path at `foreseen` or `mistake` is not raised again. An earlier `open` row on an old head is raised again, as at path grain.
3. CONFIRMED, no high. With no prediction, the commit writes no definition row, the same rule as `stray_paths` ("nothing predicted, nothing strays"). Night 154's batch b1 (s130) predicted `src/click/utils.py` at path grain, so the fix reaches the wall.
4. CONFIRMED with one low (finding 1). Exact `path::name` closes the row and writes `batch_touch` at `symbol`. A bare path closes every `path::*` row. `src/click/core.py::Click` maps to the open bare path, at `path`. An unknown grain refuses with the right text.
5. CONFIRMED by a run. `mergeable` returns "touch strayed, unjudged: src/click/utils.py::echo" for an open row, the mistake text for `mistake`, and None for `foreseen`.
6. CONFIRMED with one low (finding 2). The wake detail is `src/click/utils.py::echo`. The Architect sentence names no call. The Developer sentence has 22 words and two instructions.
7. CONFIRMED with one low (finding 3). `_batch_worktree` returns the worktree. A restore lands with no note and no stray, also with an absolute path. A ctx with no `batch_id` skips `_base_text` and reads the root file. A batch with no worktree loses the root fallback.
8. CONFIRMED. `sqlite3` is a module import (`api.py:32`), and `_wt` is a local import at the function top. `normpath` folds `src/x/../click/utils.py`. `../proj/...` returns None. `cat-file blob` returns the blob for a present path and `""` for an absent path, so a created file still reads as created. Frame 220's fix is not weaker.
9. CONFIRMED. The three new tests fail on parent code with the old ValueError (4 failed, with the renamed helper test). The five touched or named files pass 481 at HEAD: 52 + 360 + 12 + 36 + 21, as the report says. Test counts go 45 to 47 and 312 to 313. No test was deleted: two renames, three additions.
10. CONFIRMED. The diff removes the one write refusal. The one `raise ValueError` left in the diff's hunks is "cannot be both foreseen and a mistake" in `batches_judge_touch`, a check on the judgement, not on a write. The fence's criteria refusal is outside this diff, as section 4 of the history read plans.
11. CONFIRMED: 33 refusals on 20 nights. By a landed-write heuristic, 11 of 32 named refusal sessions later landed a write of the same file, and 21 did not.

## (b) Findings

1. `rota/roles/api.py:16446-16451` (`_covers`), low, CONFIRMED. A `path::name` grain with a `./` prefix matches no definition row. The probe judged `./src/click/utils.py::echo` against the open `src/click/utils.py::echo` and got the refusal. The bare `./src/click/utils.py` passes, because `_grain_path` folds it. Frame 228 saw the `./` shape from the Architect. Fix: compare `_grain_path(p) + "::" + p.split("::", 1)[1]` with `open_rows` before the bare-path fallback.
2. `rota/roles/prompts/architect/touch_strayed.md:21-22` and `rota/roles/prompts/developer/touch_mistaken.md:10-11`, low, CONFIRMED by reading. "Judge it the same way." names no call. The Developer sentence has 22 words and two instructions ("write ... and keep"), and it omits the `code.commit` step. Fix: "Judge it with `batches.judge_touch`." and split the Developer sentence in two, the second naming `code.commit`.
3. `rota/roles/api.py:16933-16937` (`_changed_unnamed_defs`), low, CONFIRMED. `_batch_worktree` raises ValueError for a batch row with no worktree. The broad except then sets `base = {}` and skips the root fallback, so a restore reads as a change. The probe gave `['echo']` where the root file held the base. Merged batches carry `worktree` NULL on night 154, and `code_diff` calls this function. Fix: catch the `_batch_worktree` error alone and fall through to the root read.
4. Outside, `rota/roles/api.py:16385-16388` and `rota/core/lifecycle.py:613-622`, low, PLAUSIBLE. A definition judged `mistake` is never checked again. Any new commit leaves the mistake row on the old head, and the grain is in `judged` for the next commit, so the merge hold clears without a restore. The path grain has the same rule by design (`test_a_mistake_wakes_the_developer_and_a_new_head_leaves_it_behind`). Fix: at commit, re-raise a `mistake` grain whose definition still differs from the base, or rule that the path rule is enough.
5. Outside, point 11's ratio, low, PLAUSIBLE. The heuristic counts any landed write of the refused file after the refusal. It cannot tell an append from a different edit. Its commit match found 1 later commit, and that match is not checked against the result format. The ratio is therefore an upper bound on "the seat appended". Fix: read the 11 sessions' landed writes for a `start=end` span before the frame's close cites the ratio.

## (c) Probes

All probe files are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/bf5baa63-e3e0-4611-8e8d-2e8c20403b25/scratchpad/f286/r1/`.

- `parent/` and `head/`: `git archive b0dbd926^` and `git archive b0dbd926` copies. In `parent/`, HEAD's `test_night46_context.py` ran as `test_night46_context_head.py -k "lands_with_a_note or records_an_unnamed or restores_the_base or helper_no_criterion"`: 4 failed, each on the old ValueError. In `head/`, the parent's file ran as `test_night46_context_parent.py -k "may_not_change_a_definition or keeps_its_source"`: 2 failed, "DID NOT RAISE".
- Worktree: `ROTA_MODEL=qwen3:8b pytest tests/rota/test_night46_context.py test_desk_guards.py test_touch_divergence.py test_frame140_commit_beside_note.py test_revert_door.py -q -p no:cacheprovider`: 481 passed in 138 s. Test names diffed with `git show <rev>:<file> | grep "^def test_"`.
- `probe.py`, run from the worktree root: a git project with a batch worktree, then P2a to P2c (commit rows), P3 (no prediction), P4i to P4viii (`judge_touch`), P5 (`mergeable` and the wake), P7 (restore base, no `batch_id`, no worktree), P8 (`_base_text` present, absent, directory, `..`, escape, outside absolute, root None).
- `q154.py`, `q154b.py`: read a scratch copy of `.rota/clickI_night154.db` and its WAL. Session s130 is a Developer on b1. b1's `batch_touch` holds `src/click/utils.py`, `tests/test_utils/test_echo.py`, `tests/test_utils/test_echo_via_pager.py`, all `path`. The night has 0 `touch_strays` rows.
- `../count.py`, run from `D:/repos/rota`: "total 33 nights 20".
- `ratio.py`, run from `D:/repos/rota`, `mode=ro`: per Developer session with the refusal, the refused name and path and whether a later `OK code.write` with `bytes` and no `unchanged` landed on the same path. 51 rows. 19 rows have no name, because the fence text shares the phrase "and no criterion of this batch names". The 32 named rows give 11 landed, 21 stuck.
- The worktree holds an untracked `tests/rota/test_r4_new.py` that the commit does not carry. This review did not read or run it.

## (d) Usage

About 95k input tokens and 14k output tokens, about 109k in all, from this agent's estimate. The harness line is the record. No sub-agent.
