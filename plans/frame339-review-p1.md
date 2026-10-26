# Frame 339, review 1 of c7264f5a: the removal door records a stray for the Architect

Reviewer: a read-only agent. Worktree `C:/Users/roman/rota_r339` at c7264f5a, parent b889c93d. No tracked file changed.

## Verdict

**Stands with fixes.** The removal now lands, and one open `touch_strays` row reaches the Architect. Two high findings stay open. First, a removal that the Architect judges a mistake is lost on the next commit, and the merge then goes on. Second, the two stray prompts do not say what a `removal:` row is. So the Developer prompt can tell the seat to revert the whole wanted rewrite.

Counts: 9 points answered. 8 findings: 2 high, 6 low. 6 CONFIRMED, 2 PLAUSIBLE.

## (a) The verdict on each point

1. CONFIRMED. The test is red on the `rota/` of b889c93d (6 failed, 1 passed) and green on c7264f5a (7 passed).
2. CONFIRMED. With the criteria, item and rulings of night 169, the commit of s122 lands with one open stray. So the right rewrite costs an Architect wake.
3. CONFIRMED for the Architect side and for `batches.strays`. The `touch_mistaken` mode of the Developer holds `batches.strays`, and the row note keeps the removed line.
4. CONFIRMED. The `later` branch refuses only an entry with no line and no definition. One `held` refusal names a route that the next reply refuses (finding 3).
5. CONFIRMED. The writer writes one row per commit. A judged grain is skipped on the next commit. A re-raise overwrites nothing. A `mistake` grain is skipped too (finding 1).
6. CONFIRMED. No reader of a deleted name is left. No old refusal text is left. One test name keeps "refused", and it is still correct.
7. CONFIRMED. A third door exists: `_silent_note_refusal` refuses `ledger.log` on an uncommitted removal (finding 4). `_drops_whole_line` is not a removal door.
8. CONFIRMED. No role prompt describes the old door. Neither `touch_strayed.md` nor `touch_mistaken.md` says what a `removal:` note means (finding 2).
9. CONFIRMED. Most removed assertions have a replacement. Finding 6 lists the dropped ones.

## (b) Findings

1. **A mistake verdict on a removal is lost on the next commit.** High. CONFIRMED.
   - Where: `rota/roles/api.py` about 20596 to 20599, the `judged` set of `_removal_strays`. Also `rota/core/lifecycle.py` 841, `mergeable`, and `rota/core/predicates.py` about 2400, `touch_mistaken`.
   - Probe P5m: commit 1 raised the stray. The Architect judged it a mistake at sha1. The Developer then changed line 1 only and committed sha2. The removed line stayed gone.
   - Result: no new row at sha2, `mergeable` returned `None`, and `touch_mistaken` returned `[]`. The merge went on with the removal that the Architect called a mistake.
   - The `judged` filter counts `status != 'open'`, so a `mistake` counts as judged. The definition strays of frame 286 have the same skip. Deviation 7 says that a removal stays raised until it is judged. That claim holds only for `foreseen`.
   - Fix: skip only `foreseen` grains in `_removal_strays`. Re-raise a `mistake` grain as a `mistake` row on the new head while the tree still lacks the line.
2. **The stray prompts do not explain a removal row.** High. PLAUSIBLE.
   - Where: `rota/roles/prompts/architect/touch_strayed.md` line 1 and lines 21 to 23. Also `rota/roles/prompts/developer/touch_mistaken.md` lines 10 to 12.
   - `touch_strayed.md` says that a stray is a path the prediction never named, or a definition that no criterion names. The `get_app_dir` of night 169 is predicted, and every criterion names it. Neither text applies to the row.
   - `touch_mistaken.md` says: "write the base source of that definition back over its span". For a removal grain, that step reverts the whole rewrite, not the one removed line.
   - Why PLAUSIBLE: no case renders either mode with a removal row. Open question 4 of the implementer names the same gap.
   - Fix: add one sentence to each prompt. In `touch_strayed.md`: a `removal:` note names a base line that the commit removed. In `touch_mistaken.md`: put back that line only, and keep the rest.
3. **A held refusal of a note with no line names a route that the next reply refuses.** Low. CONFIRMED.
   - Where: `rota/roles/api.py` 20565, `write_only=bool(later)`, and `_note_routes` 21186 to 21195.
   - Probe P4: a note with `lines=[]` and `defs=[]` in the notes of the reply.
   - The first refusal says: "To keep the change, commit in your next reply. The Architect then judges the removal". The commit of the next reply then gets: "Put the lines back with code.write, then commit in your next reply."
   - On b889c93d, `batch_start` got the undo route alone, so this text is new in the pass. The law of frame 135 says that a route names only a call that the door admits.
   - Fix: pass `write_only=True` when every entry, held or later, has no line and no definition.
4. **A third door on the removal path: the ledger door.** Low. CONFIRMED.
   - Where: `rota/roles/api.py` 21259 to 21263, `_silent_note_refusal`. `ledger_log` calls it at 13173.
   - Probe P7: a write that removes the line, then `ledger.log` about the path. The call is refused: "holds an uncommitted write that removes `folder = ...` at line 518, so this note closes nothing."
   - The door refuses a write, not a commit. Its route now ends on the commit route, so the seat can go on. The Reach line "2 doors of 2" does not count this door.
   - The route still opens with "A note does not allow a removal or a rewrite." That sentence now contradicts the next sentence of the same route, because the commit of the next reply lands.
   - Fix: count the door in the Reach line, and decide if it stays. Change the first route sentence to "A note does not close a removal."
5. **The words of night 169 still miss the matcher.** Low. CONFIRMED.
   - Where: `rota/roles/api.py` 20813 to 20828, `_asks_removal`.
   - Probe P2: crit_1 to crit_3, the item text and all rulings, copied from `f339_clickI_copy.db`. The commit lands with one open stray, `removal: ... at line 518`.
   - The deciding text: m36 (`r_58bf1e8c70`) and m40 (`r_62dd42ab85`) say "remove the line at 518 in get_app_dir that sets the folder to the bare home folder". The `per_item` keys of both rulings hold `batch_1`, so both texts reach `_ruling_texts`.
   - The matcher needs the full statement text in the removal span. An assignment has no call head, because the head regex needs a name with `(` directly after it. The item says "instead of the bare home folder", and that names no statement.
   - So the explicit ask of the principal costs one Architect wake. Law 12 allows this cost. With finding 2, that wake can also revert the fix.
   - Fix: none owed in this frame. Record the cost in the status line of the frame.
6. **Assertions dropped without a replacement.** Low. CONFIRMED by the diff.
   - `test_frame283_removal_on_ruling.py`: the replay test no longer pins the ledger door at seq 17 and seq 23. It no longer pins that the seq 20 fault note lands in `faults` (review 2, finding 1). Only the night database test at line 210 still pins `LEDGER`.
   - `test_frame312_stuck_review.py`: three tests are deleted. `test_a_ruling_that_allows_the_removal_shows_no_refusal` pinned that a ruled removal gives no page refusal. `test_a_note_whose_line_the_write_kept_shows_no_refusal` pinned that a kept line gives no refusal. `test_two_notes_get_one_ask_each` pinned one sentence to copy per note. All three read `_refused_commit`, and that function is deleted.
   - The m115 test lost two more pins: `"check: none yet." not in page`, the `bare_checks` suppression, and the line "Your answer to this page starts the team once more". The lift in `land` stays, but no page line now tells the principal about it.
   - The frame 140 file and the frame 283 rewrite, signature and whole-file files: each removed refusal assertion has a replacement on the landed commit and the stray row.
   - Fix: add one assertion that the seq 20 fault of the s279 replay still lands in `faults`.
7. **Outside: a test docstring names a call that the test does not make.** Low. CONFIRMED by a read.
   - Where: `tests/rota/test_frame339_removal_stray.py` lines 198 to 200.
   - The docstring says that `batches.strays` shows the removed line. The test reads the staged write and `touch_mistaken` only.
   - Fix: call `batches.strays` in the `touch_mistaken` mode, and assert that the note holds the line.
8. **Outside: a removal in an unpredicted file can give two rows.** Low. PLAUSIBLE.
   - Where: `rota/roles/api.py` about 20504 to 20507, `if path in removals: continue`.
   - `strays` holds path grains, and `removals` holds `path::owner` grains. The skip matches a module-level removal only.
   - So a removal inside a definition of an unpredicted file writes a path row and a grain row. The Architect then judges both. Why PLAUSIBLE: a read only, no probe.
   - Fix: skip the path row when a key of `removals` starts with `path::`, and keep the note on the grain row.

## Points in detail

### Point 1, the red test. CONFIRMED.

The scratch copy holds the tree of c7264f5a with `rota/` from b889c93d. On b889c93d, 6 tests fail and 1 passes. The red test fails with "a code.write in an earlier reply returned a note, and the tree still does not hold those lines". The criterion-asked case passes on both commits. On c7264f5a, all 7 tests pass.

The red test asserts these facts:
- The commit landed: `committed` is True, and HEAD equals `head_commit`.
- Exactly one staged row exists.
- The grain is `src/click/utils.py::get_app_dir`.
- The status is `open`.
- The note starts with ``removal: `folder = os.path.expanduser("~")` at line ``.
- `out["removals"]` gives the grain and the note again, and `out["removals note"]` names the Architect.

### Point 2, the criterion-asked case. CONFIRMED.

The commit lands with one stray, not without one. Finding 5 names the deciding texts. The right rewrite does cost an Architect wake here.

### Point 3, night 158 and touch_mistaken. CONFIRMED.

`test_s279s_removal_reaches_the_architect_as_an_open_stray_before_a_merge` passes. It asserts the open row, `mergeable` == "touch strayed, unjudged: ...", and the wake detail `path (removal: ...)`.

The mode of the Architect holds `batches.judge_touch` (`architect/touch_strayed.tools`). `judge_touch` keeps the `removal:` note in front of the reason.

The mode of the Developer holds `batches.strays` (`developer/touch_mistaken.tools`). `batches_strays` returns `path, status, note` for the head commit, and `judge_touch` writes the mistake row at the head. So the Developer can read the line. The prompt then gives the wrong step (finding 2). After the next commit the row is not at the head, and finding 1 applies.

### Point 4, `_unread_drop_refusal`. CONFIRMED.

- The `later` branch now refuses only an entry with no line and no definition. `test_an_entry_with_no_stored_line_names_the_write_route_only` still pins the write-only route.
- The `held` branch reads `ctx.reply_notes`. The sandbox resets these on `begin_reply`. The unchanged-write path (about 19981) sets them again, and that is a write in the same reply. So the branch refuses only a commit in the reply of the write.
- One refusal names a route that its door then refuses (finding 3).

### Point 5, deviation 7. CONFIRMED.

- Probe P5: two commits of one batch, with no judgement between them, give two rows. The keys are `batch_1:acbfb588...:...::get_app_dir` and `batch_1:faf8ddc3...:...::get_app_dir`. Both rows are `open` and hold the same note.
- The key holds the commit sha, so a re-raise overwrites no note and no status. An old open row stays on an old head. Every reader filters on the head or on `status != 'open'`, so the old row has no effect.
- `test_a_judged_removal_is_not_raised_again` confirms that a `foreseen` grain is skipped.
- A `mistake` grain is skipped too (finding 1).

### Point 6, deleted names. CONFIRMED.

A grep of `rota/`, `tests/` and `probes/` finds no reader of `_unruled_removal`, `_head_text`, `_removing_commit`, `_refused_commit`, `_times`, `bare_checks` or `FIRST`. `docs/` does not exist. "No criterion, request or ruling" occurs only in the new `removals note` of `code_commit` (about 20490). That text is new and correct. No sentence to copy, "remove the ...", is left in code or prompts. The other hits are unrelated test words and comments. `test_the_refused_commit_names_both_routes_for_a_rewrite` (whole-file file, line 261) is still correct, because the held branch still refuses.

### Point 7, a third door. CONFIRMED.

The map lists 3 callers of `_unruled_gone`: `_unread_drop_refusal` 20561, `_removal_strays` 20610 and `_silent_note_refusal` 21259. The third caller is the door of finding 4. `_drops_whole_line` (6179) reads the page lines of a ruling, not code, so it is not a removal door. `tests_encode` (9223) calls no removal helper. `_gone_statements` has one caller only.

### Point 8, role prompts. CONFIRMED.

A grep of `rota/roles/prompts` for removal, note and route words finds no text about the old door. The gaps are in `touch_strayed.md` line 1 and lines 21 to 23, and in `touch_mistaken.md` lines 3 to 4 and 10 to 12 (finding 2).

### Point 9, weakened assertions. CONFIRMED.

Finding 6 lists the assertions dropped without a replacement. Of the four frame 312 page tests, the one that stays checks that no old page sentence shows.

## Outside

Findings 7 and 8 are outside the points. In addition, the 3 stale cases of the implementer come from the new route text in `_note_routes`. The fixes of findings 3 and 4 change that text again. So re-record those cases once, after both fixes.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/e03f97fc-cdd4-4daa-864c-2ca4d7ef42a5/scratchpad/`. Each ran from the worktree root with `-p no:cacheprovider -p no:xdist`.

- `r339old/`: a `git archive` of c7264f5a, with `rota/` replaced by `git archive b889c93d rota`. It ran `tests/rota/test_frame339_removal_stray.py`: 6 failed, 1 passed.
- `r339_click.db`: a fresh copy of `f339_clickI_copy.db`. `r339_crit.py` read the criteria, items, rulings and strays from it.
- `r339p/test_r339_probe.py` imports the fixtures of the frame 339 test.
  - `p2` used the criteria and rulings of the night, and gave one open stray.
  - `p5` ran two commits and gave two rows, one per sha.
  - `p5m` judged a mistake, then committed with the line still gone. `mergeable` returned `None`.
  - `p7` called `ledger.log` after the removal, and the door refused the call.
- `r339p/test_r339_probe4.py`: a held note with no line. The first refusal names the keep route. The commit of the next reply is refused with the write route.

## (d) Usage

No meter is visible to the reviewer. These are estimates.

- Input tokens: about 100,000.
- Output tokens: about 16,000.
- Total: about 116,000.

## Pass 1b

**Does not stand.** Commit a0b0b6ae on `f339` in `C:/Users/roman/rota_p339` was read-only probed. The fix for finding 1 works. The fix for finding 8 opens a hole in the sign-off that law 12 requires: in an unpredicted file, a change outside the removal grain reaches no row, and the merge goes on.

1. **Finding 1: CONFIRMED fixed.** Probe `p5m` was re-run, and the staged rows were landed.
   - After a mistake verdict, a commit that leaves the line gone writes a `mistake` row at the new head (`batch_1:d3b4e2d2...::get_app_dir`).
   - `mergeable` then returns "touch strayed, a mistake still in the head commit: src/click/utils.py::get_app_dir", and `touch_mistaken` wakes the Developer.
   - Probe `p1b` put the line back under `if folder is None:` and committed. The commit wrote no row. `mergeable` returned `None`, and `touch_mistaken` returned `[]`.
   - Caution for the next probe: a whole-file restore of the base is refused by the door "you are undoing yourself". Only a line restore reaches the stray code.
2. **Finding 8: the fix lets a change escape the sign-off. High. CONFIRMED.**
   - Where: `rota/roles/api.py` 20517 to 20523, `if path in held or any(g.startswith(path + "::") for g in held): continue`.
   - Probe `p2b`: the prediction names only `src/click/core.py`. One commit rewrites `get_app_dir` and also changes line 1 of `src/click/utils.py`, which is module level and outside the grain. The diff of HEAD shows both changes.
   - The commit returns `outside_prediction: ['src/click/utils.py']`. It writes one row only, `src/click/utils.py::get_app_dir`, open, with the removal note.
   - `_unnamed_def_strays` skips a path that is a stray as a whole (`rel in path_strays`), so no other row exists for the file.
   - The wake detail names the grain and the removal only. The Architect judged the grain `foreseen`, and `mergeable` then returned `None`. The line 1 change merged with no judgement.
   - Fix: keep the path row whenever the commit changes the file outside the removal grains. Or keep the path row always, and let `judge_touch` judge the path and the grain together. Then pin the line 1 case in `test_a_removal_in_an_unpredicted_file_writes_one_row`.
3. **Route texts: no sentence contradicts another. CONFIRMED.** The full texts at a0b0b6ae are:
   - Commit door, held, with a line: "... If the tree holds those lines again, commit in your next reply. A note does not close a removal. To undo the change, put the lines back with code.write, then commit in your next reply. To keep the change, commit in your next reply. The Architect then judges the removal before the batch merges."
   - Commit door, a held or later entry with no line: "... If the tree holds those lines again, commit in your next reply. Put the lines back with code.write, then commit in your next reply." The next reply gives the same write route. So finding 3 is fixed.
   - Ledger door: "... so this note closes nothing. A note does not close a removal. To undo the change, put the line back with code.write, then commit in your next reply. To keep the change, commit in your next reply. The Architect then judges the removal before the batch merges."
   - Two sentences say the same thing, and neither is false. In the commit door, "If the tree holds those lines again, commit in your next reply" now adds nothing, because the commit of the next reply lands either way. In the ledger door, "this note closes nothing" and "A note does not close a removal" say one fact twice. Low. Fix: drop the conditional sentence when the keep route follows it.
4. **The prompt sentences: each one is true for some rows only. Low. CONFIRMED by a read and by the probes.**
   - `touch_strayed.md`: "A `removal:` note names a base line that the commit removed, inside a definition the prediction named." This is false in three cases that the code writes:
     - In probe `p2b`, the prediction did not name the file or the definition.
     - A module-level removal has the path as its grain, with no definition. Frame 140 pins `("src/click/other.py", "open", "removal: `x = 1` at line 1")`.
     - A removed definition has the grain `path::<the def line>` (api.py 20641). The removed text is then a definition, not a line inside one.
     - Also, the prediction usually names files, and the criteria name definitions. One note can also name more than one line.
   - `touch_mistaken.md`: "For a `removal:` row, put back that line only, and keep the rest of the definition." This is true for one removed line inside a definition. It is wrong in number when the note names more lines, as the frame 140 note does with three statements. It names no definition for a module-level row. The note of a `mistake` row also ends with the reason of the Architect, so "that line" is the quoted text only.
   - Fix: in `touch_strayed.md`, write "A `removal:` note quotes each base line that the commit removed." In `touch_mistaken.md`, write "put back each quoted line only, and keep the rest of the file."

Probes for pass 1b, in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/e03f97fc-cdd4-4daa-864c-2ca4d7ef42a5/scratchpad/r339p/`:
- `test_r339_probe_1b.py`: `p5m`, `p1b`, `p2b` and `p7`, run against `rota_p339`.
- `test_r339_probe4_1b.py`: `p4`, run against `rota_p339`.
- No tracked file changed. Usage for pass 1b is about 30,000 input tokens and 5,000 output tokens.

## Pass 1c

**Stands.** Commit 7f263584 on `f339` in `C:/Users/roman/rota_p339` closes the escape found in pass 1b. One low prompt gap remains. No tracked file changed.

1. **Finding 8 re-probe: CONFIRMED fixed.** The probes are `p2b` and `p2c` in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/e03f97fc-cdd4-4daa-864c-2ca4d7ef42a5/scratchpad/r339p/test_r339_probe_1c.py`.
   - Line 1 changed plus the removal in `get_app_dir`, in a file that the prediction does not name: the commit writes two open rows, `src/click/utils.py::get_app_dir` with the removal note and `src/click/utils.py` with no note. The wake detail names both rows.
   - The removal alone, in the same unpredicted file: the commit writes one row, `src/click/utils.py::get_app_dir`.
   - A `foreseen` judgement of the grain alone cannot free the merge. `batches.judge_touch` refuses it: "src/click/utils.py is still unjudged. Every open stray is foreseen or a mistake; say which". The path row stays open at the head, so `mergeable` keeps "touch strayed, unjudged".
2. **Prompt sentences for a removal in an unpredicted file.**
   - `touch_strayed.md` lines 25 to 26: "A `removal:` note quotes each base line that the commit removed. A quoted `def` or `class` line stands for the whole definition." Both sentences hold. They say nothing about the prediction.
   - `touch_mistaken.md` lines 14 to 16: "For a `removal:` row, put back each quoted base line only, and keep the rest of the file. For a quoted `def` or `class` line, put back the whole definition from the base." Both sentences hold for the grain row.
   - Low, CONFIRMED by a read: two older sentences do not hold for this case.
     - `touch_strayed.md` lines 21 to 23 say that a definition stray occurs "when your prediction named the file". In `p2b` the grain row is a definition in a file that the prediction did not name.
     - `touch_mistaken.md` lines 4 to 6 tell the Developer to restore a stray file "as it stood before the batch". If the Architect judges the path row of `p2b` a mistake and the grain foreseen, that step also reverts the foreseen rewrite of `get_app_dir`.
   - Fix: in `touch_strayed.md`, add "or the file is a stray and a removal sits in the definition". In `touch_mistaken.md`, add "keep any definition judged foreseen".

Usage for pass 1c is about 9,000 input tokens and 2,000 output tokens.
