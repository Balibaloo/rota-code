# The `criteria.json` write of night 175: a read of the write door (2026-10-29)

Sprint 35 row 5. Read-only gather. The records are `.rota/clickI_night175.db` and `plans/night175-read.md`.

## 1. Provenance

Session s268, a Developer on qwen3.5:9b, woke on m111, the Architect's `answer` on bg_3 (observed: `sessions`, `messages`). Its calls: `code.probe`, `criteria.load`, `glossary.lookup`, then at seq 4 `code.write(end=-1, path='criteria.json', start=0, text='[{"id": "c_1_format_filename_example", "ticket_id": "t...')`, then at seq 5 `code.commit(message='Removed contested criteria c_2 and c_3 per principa...')`, commit 63bfc7b at 18:39 (observed: `tool_calls`; the read, section 0). The seat wrote the output of `criteria.load` to disk as a file of the project (reasoned: the text is a JSON list of criteria rows, and the message says what he ruled on c_2 and c_3).

The prediction of bg_3 is one grain, `src/click/utils.py`, kind path, confidence expected (observed: `batch_touch`). `code.commit` wrote one `touch_strays` row for `criteria.json`. s269, the Architect, woke on `tick:touch_strayed` and judged it a mistake with `batches.judge_touch(mistakes=['criteria.json'])`. s270 and s273, Developers on `tick:touch_mistaken`, wrote the file empty and committed. s273 then wrote it back twice, "Restore criteria.json with only c_1_format_filename", commit 803bb1fc at 18:43 (observed: `tool_calls`, `touch_strays`). So the stray route ran to its end, and the last Developer undid it.

## 2. The door

The Developer's writes pass `code.write` to `_code_write`, `rota/roles/api.py` 20920 and 21004 (observed). The one path fence is `_within(_batch_worktree(ctx), path)` at 21018: the resolved path must stay under the batch's worktree (observed: 20862). The other path doors read the name or the suffix only: a placeholder name at 21053, a new root `.py` module against the src package and the stdlib names at 21760 to 21775, the parse, drop and unnamed-definition doors for `.py` at 21716, 21781 and 25291, and `fence.check_manifest` for requirements files at `rota/core/fence.py` 123 (observed). `rota/core/sandbox.py` holds no path door: its one worktree path, line 1966, feeds a signature check (observed: grep).

No door of `code.write` reads `batch_touch`, the guess or the code index for a file that is not `.py` (observed). `criteria.json` is relative, under the worktree, not a placeholder, not `.py` and not a manifest, so it passed every door (reasoned from the doors above). This is the rule, not a gap: "law 12: the touch set is a prediction, never a permission" (observed: api.py 7695, 7806, `rota/core/divergence.py` 90 to 98). The prediction is read once, after the commit, by `_outside_prediction` at 24682 through `stray_paths` and `predicted_files`, and the Architect judges the row (observed). What no door knows is that `criteria.json` is rota's own record. The runtime has no name for a record of its own written as a project file (observed: grep for `criteria.json` in `rota/` finds no door).

## 3. Unbuilt solutions

`plans/wall-guide.md` has no wall on a write outside the prediction or on `criteria.json`. Its one line on the subject, 484, cites law 12 (observed: grep). `plans/stack.md` holds the lineage of the stray route and nothing on a record written as code (observed: grep). Frame 114's history read, 2026-10-17 17:04, holds the rule: law 12 and the composition's "A prediction never blocks", and two doors that refused were made to record, frame 286 and frame 220 (observed: stack.md 3655 and 3656, 1086 to 1092). Frame 286 is landed and measured at 0 on its third night (observed: stack.md 897). Frame 298 gave the Architect the guess, with `_refuse_stray_dirs` and `_refuse_unindexed_files` on the prediction (observed: api.py 7456, 7593). Night 175's W9 is the first sight of a rota record written into the project (observed: the read, line 65, names no earlier night). A fix that makes the write door refuse a path outside the guess departs from law 12 and from his ruling of frame 114, so it is a question to him first, and this read does not recommend it (reasoned).

## 4. Reach

The places that compare a path against the batch, the guess or the project (observed, file and function):

1. `rota/roles/api.py` `_within` 20862: the write path against the batch's worktree.
2. `rota/roles/api.py` `_code_write` 21760 to 21775: a new root `.py` against the project's package and the stdlib.
3. `rota/roles/api.py` `_changed_unnamed_defs` 25291 and `_unnamed_def_strays` 24700: `.py` definitions against the criteria names, at the write and at the commit.
4. `rota/roles/api.py` `_outside_prediction` 24682, with `rota/core/divergence.py` `stray_paths` 117 and `rota/core/lifecycle.py` `predicted_files` 510: the committed paths against the prediction.
5. `rota/roles/api.py` `_refuse_stray_dirs` 7456 and `_refuse_unindexed_files` 7593: a predicted path against the code index, for `batches.annotate` and `batches.guess`.
6. `rota/roles/api.py` `tests_encode` 9904 to 9911 and `_refuse_program_path` 7556: a test path against the project and its program files.
7. `rota/roles/api.py` `code_read` 19243 to 19268: the diff's definitions against the project root.
8. `rota/core/fence.py` `check_manifest` 123: a manifest path against the criteria.
9. `rota/roles/api.py` `_surface_outside_batch` 5589: a repair surface against the batch's files.

Nine places. The prediction has one reader, `predicted_files`, and places 4 and 5 use it (observed). No place reads "is this path rota's own record", so the missing reader is new, not a residue of one door among nine (reasoned).

**The price.** One reader, `_rota_record(path, text)` in `rota/roles/api.py`, called once in `_code_write` before `_within`, so `code.write` and its dry run `_admits` share it, and the `touch_strayed` wake detail names it. It serves 3 places: the write, the dry run and the stray note. It refuses a file whose name is a rota record (`criteria.json`, and the names of the other `*.load` outputs) when the code index lacks the path, with one fact and one step: the criteria are rota's, `criteria.load` reads them, and the change goes in the predicted file. It reads no prediction, so law 12 holds. The red test is s268's call: a Developer on a batch whose prediction is `src/click/utils.py` sends `code.write(path='criteria.json', start=0, end=-1, text='[{"id": "c_1_format_filename_example", ...}]')` and expects a refusal. About 25 lines of door, 1 test, 1 brief line (reasoned).
