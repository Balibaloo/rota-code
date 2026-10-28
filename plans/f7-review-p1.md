# F7 review, pass 1: commits 11d04b18, f7fa55b8, cdd02498 on f7root

The verdict is NOT READY. The review finds 5 high and 5 low findings. The touched test files give 160 passed. Worktree: `C:/Users/roman/rota_f7`. Line numbers are of `rota/roles/api.py` at cdd02498 unless the line names another file.

## (a) Verdicts on the points

1. The rewrite rule is wrong both ways. It misses 5 of 14 shapes and falsely flags 3 (findings 1, 2, 3, 4, 5).
2. Yes. The frame 140 refusal now fires on any unruled removal on the path, not on the note's own lines (finding 6).
3. The fold is as frame 286 built it, and a bare path no longer judges a removal. The offered calls do not land with two or more open rows (finding 7). A mistake row hides a later removal (finding 8).
4. Pass. The line has plain words, no key, and a bound of 3. It shows once per page and once per summary. A grant keeps a removal off both lines.
5. The change is small, STE, and keeps the Architect the only judge. The example copies night 171's case (finding 9).
6. The compare takes 28 to 53 ms on 300 lines with 20 changes. Git spawns cost about 0.45 s for each changed `.py` path (finding 10).

## (b) Findings

1. api.py 21578 (`_gone_statements`, called by `_unruled_gone` 21782). HIGH. CONFIRMED.
   - The line-count filter hides a compare find when its first line still shows elsewhere in the same definition.
   - Probe 13: an XDG-like `return os.path.join(` goes, and a new Windows `return os.path.join(` comes. The compare finds the return, and the filter drops it. No row is written.
   - Probe 12: an `else: v = 2` arm becomes an unconditional `v = 2`. The compare finds it, and the filter drops it.
   - Fix: skip the line-count filter for entries from `_removal_entry`, and keep it for the note-sourced entries only.
2. api.py 21417 and 21464 (`partner`, by order). HIGH. CONFIRMED.
   - When the block keeps as many statements of a kind, a removed branch pairs with a new branch of another condition.
   - Probe 7: `if sys.platform == "darwin": return mac()` becomes `if roaming: return win()`. The result is no removal.
   - This is the night 171 class with one more `if` in the new code.
   - Fix: pair by order only when the two first lines share a name word other than the keyword. Else, the old branch is lost.
3. api.py 21452 and 21464. LOW. CONFIRMED.
   - The rule flags three shapes that keep the behaviour.
   - Probe 3, a renamed local, gives a row for `tmp = compute()`.
   - Probe 4, `if a:` and `elif b:` with one body merged into `if a or b:`, gives a row for `elif b:`.
   - Probe 5, a deleted `if False:` branch, gives a row.
   - Each costs one judgement by the Architect and refuses nothing. A docstring change and a return moved into a new `with` give no row, which is correct.
   - Fix: pair a lost assignment with a new assignment whose value dump is the same.
4. api.py 21440 to 21470 (`_lost_in_block`, the kinds). LOW. CONFIRMED.
   - A removed `assert`, `import`, `del` or `global` is no kind that the rule reads, so it is never lost. Probe 9 gives no row.
   - `_binds_on_every_path` accepts a binding anywhere in the block. Probe 10 removes `total = 0` before a loop, and the later `total = round(total)` keeps it.
   - Fix: read `Assert`, `Import`, `ImportFrom` and `Delete` as kept by the same line key. Count a binding only before the first read of the name.
5. api.py 21407 to 21416 (`partner`, by words). LOW. CONFIRMED.
   - Probe 11 removes `if a:` and keeps a later `if a and b:`. The words of `if a:` pair it with `if a and b:`.
   - The row names `one()`, the body, and not the removed branch.
   - Fix: try the exact line key for every old statement first, and pair by words in a second pass.
6. api.py 21142 to 21162 (`_unread_drop_refusal`). HIGH. PLAUSIBLE.
   - Before 11d04b18, a note of this reply held the commit only when its own lines were unruled and gone.
   - Now the note holds the commit when the compare finds any unruled removal on the same path.
   - Case: an earlier reply removed Y and committed it. This reply removes X, which a criterion asks for, and commits. The commit landed before. Now the refusal fires and names X, not Y.
   - The ruling of 2026-10-17 forbids a new refusal of a commit. The probe did not run, because the door needs a live worktree and reply notes.
   - Fix: hold the note only when the compare's removals on the path share a line with the note's own `lines`.
7. api.py 22366 to 22383 (`batches_judge_touch`, the new refusal). HIGH. CONFIRMED.
   - Each offered call names the row under test and the rows already judged. It leaves the other open rows out.
   - Probe `offer.py`: two removal rows and one file row. The first offered call is refused again, with a new pair of calls.
   - Frame 135's law says that a refusal names only a call that the door admits. A small model also repeats a refused call.
   - Fix: build each offered call with every open row. Put the other unnamed rows into the same list as the row under test.
8. api.py 21227 (`_removal_strays`, the mistake branch). HIGH. CONFIRMED. Outside the points in part.
   - A mistake judgement covers every later removal in the same definition. The foreseen branch at 21233 has a coverage check, and the mistake branch has none.
   - Probe `mistake.py`: the darwin and XDG lines are back, and a new call is gone. The result carries the old note as a mistake. No row names the new removal.
   - Effect: his page names lines that are back and hides the new removal. The Developer is told to restore lines that are present. The merge holds.
   - Fix: apply the coverage check of 21233 to the mistake branch. A removal that the note lacks makes the grain unjudged with the new note.
9. `rota/roles/prompts/architect/touch_strayed.md` 34 to 37. LOW. CONFIRMED.
   - The example is night 171's case: the request text, `src/click/utils.py::get_app_dir`, and the darwin line.
   - The fixture item in `test_f7_removal_compare.py` holds the same words. A replay of night 171 then measures the example, not the rule.
   - The paragraph itself is general, STE, and adds no door.
   - Fix: use an example from another domain, with no click names and no platform branch.
10. api.py 22024 to 22062 (`_base_text`) and `_base_removals`. LOW. CONFIRMED.
    - The compare takes 28 to 53 ms on a 300-line file with 20 changes. The 688-line night 171 file takes 31 to 51 ms.
    - One git spawn takes about 100 ms on this machine. `_base_text` spawns four for each path: `rev-parse HEAD`, `merge-base`, `rev-parse --verify` and `cat-file`.
    - `_compare_tells` spawns four more for each note path that the diff does not name. A commit with 10 changed `.py` paths costs about 4.5 s.
    - Fix: compute the fork once for each commit, and read all base blobs with one `git cat-file --batch`.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/6d9cf7e1-0faa-4156-bacb-f95ee6e7ec4f/scratchpad/f7rev/`. Each probe ran from `C:/Users/roman/rota_f7` with `D:/repos/rota/.venv/Scripts/python.exe`.

- `shapes.py`: 12 shapes through `_removal_entry`, the compare stage only.
- `pipeline.py`: the 12 shapes and 2 more through `_removal_entry` and `_gone_statements`. The findings use this result.
- `offer.py`: the fixture database of `test_f7_removal_compare.py` with two removal rows and one file row. It calls `batches.judge_touch` with a bare path, then with the first offered call.
- `mistake.py`: a mistake row on `get_app_dir`, then `_removal_strays` with a new removal that the note lacks.
- `timing.py`: `_removal_entry` on 300 lines with 20 changes and on the night 171 fixture, 20 runs each. It also times one `git show` and one `git diff --name-only`.
- The suite: `pytest` on the five touched test files gives 160 passed in 112 s.

## (d) Usage

The harness does not show exact counts. The estimate is about 60k input tokens in context and about 14k output tokens, a total of about 74k.
