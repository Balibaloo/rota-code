# F7 review p3: f6b0f41f on f7b, against 442e32b0

Verdict: NOT READY. The wake now shows the removed base lines. The case cannot tell a restore from a text that holds two words.

## (a) The verdict on each point

1. PASS. The bg_3 wake from the night's rows holds both lines in full. The block sits second, after `[batches.expect]`.
2. PASS WITH A RISK. An empty diff prints a true note. A non-removal row gets removals of other grains (finding 6).
3. FAIL. The sentence has 26 words and two instructions. It names `[removed lines]` correctly. It names a grain that the wake does not print (finding 3).
4. FAIL. The grader passes a docstring-only write, a comment-only write and a write to a wrong path. No existing key grades the text of a `code.write`, so a new key is needed. The key must grade the landed file (findings 1, 2).
5. PASS. A copy without `code.diff` in the tools file turns `test_the_restore_wake_shows_each_removed_base_line` red.
6. PASS. Five files, no CR bytes, no foreign hunk. The new grader key is outside section 6, and the case needs it.
7. `L1-DV-take-a-mistake-out` moves. It was stale at the parent already (probe 7). `L1-DV-put-back-a-removed-block` is new and unrecorded.

### Point 1: the block the seat now sees

The wake is 29,521 characters. `[code.diff]` starts at character 5,013, after `[batches.expect]` and before `[criteria.load]`. The `[removed lines]` block is 360 characters. The `[diff]` block after it is 1,287 characters.

```
[code.diff]
batch: bg_3

[removed lines]
src/click/utils.py:
-     if shorten:
-         filename = os.path.basename(filename)
-     else:
-     if isinstance(filename, bytes):
-         filename = filename.decode(sys.getfilesystemencoding(), "replace")
-     else:
-         filename = filename.encode("utf-8", "surrogateescape").decode(
-             "utf-8", "replace"
-         )
```

### Point 2: the two other shapes

- A head tree equal to the base: the block is `{"batch": "bg_3", "diff": "", "note": "this batch has no change since its fork: no commit and no uncommitted edit"}`. The note is true and does not mislead.
- A `mistake` row on an added `def extra()`: the block shows the `format_filename` removals, which the row does not judge. The block does not name the grain, so a seat can put back lines of another grain.

## (b) Findings

1. `rota/testkit/fixtures.py:1492-1510`, high, CONFIRMED. `_write_includes` reads the text of each `code.write` call and nothing else. Probe 4 passed three plants. The first holds the head body and `str.encode(` with `errors="surrogateescape"` in the docstring. The second holds the head body and a comment. The third writes `tests/x.py`. The grader also passes a write that the door refuses, because it reads the reply and not the result. The unit test grades an outcome with no run at all. Fix: grade the file at the batch head after the run, for the base lines inside the body of `format_filename`.
2. `tests/rota/cases/l1_touch.yaml:278`, high, CONFIRMED. The keys `.encode(` and `surrogateescape` grade the encode branch only. The read's section 7 records s243's restore with `basename` and no `surrogateescape`. The reverse half-restore, with the encode branch and no `basename`, passes this case. Fix: `write_includes: ['filename.encode("utf-8", "surrogateescape")', 'filename = os.path.basename(filename)']`, or the head-file check of finding 1.
3. `rota/roles/prompts/developer/touch_mistaken.md:14-15`, high, CONFIRMED. The sentence selects lines by "the grain the Architect judged". The wake prints neither the grain nor the `removal:` row. `batches.strays` takes a `batch_id` argument, so the generic push skips it. The wake head is "Refs: bg_3" only. Line 3 says "The wake names the batch and the paths", and the wake names the batch only. s264 and s267 did not call `batches.strays`. On bg_3 every removed line belongs to the judged grain, so the case does not show the gap. Fix: push the `mistake` rows at the head for the wake's batch, or add `tick:touch_mistaken` to `DETAIL_SHOWN`.
4. `rota/roles/api.py:18309`, low, CONFIRMED. The block omits `filename = os.fspath(filename)`, because the head keeps the same line in another branch. The block shows `else:` and then `if isinstance(...)`. A literal put-back of the block leaves an empty `else:`. The row's note names that line first. The `[diff]` block holds the line. Fix: tell the seat to take the base text of the judged definition from `[diff]`, and to use `[removed lines]` as the list of what went missing.
5. `rota/roles/prompts/developer/touch_mistaken.md:14`, low, CONFIRMED. The sentence has 26 words and two instructions. Line 15 is 117 characters and is not wrapped. Fix: "For a `removal:` row, put back the `[removed lines]` of the judged grain. Keep the rest of the file."
6. `rota/roles/api.py:18413`, low, CONFIRMED. A non-removal `mistake` row gets the removed lines of every grain in the batch (probe 2). Fix: the same as finding 3. Optionally filter the block to the spans of the judged grains in a `touch_mistaken` wake.

Outside the points: `test_roles_doc.py::test_a_verb_carries_words_or_does_not_regardless_of_recipient` is red at the parent and at f6b0f41f. The commit does not cause the red.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/2568e043-732b-4ab6-9d66-bc0069e83123/scratchpad`.

1. `f7r_p1.py` on `n172_f7r.db`, a copy of `clickI_night172.db`. It builds the `touch_mistaken` wake for bg_3 from the night's rows and the live bg_3 worktree at 128bec7e. The output is `f7r_wake.txt`.
2. `f7r_p2.py` reuses the unit test's fixture. Case (a) adds `def extra()` with a non-removal `mistake` row. Case (b) commits the base text back, so the head tree equals the base.
3. `f7r_p4.py` runs `_write_includes` on a docstring-only plant, a comment-only plant and a wrong-path plant. All three return `[]`.
4. `f7copy/`: `git archive` of f6b0f41f, with `code.diff` removed from the tools file. The unit test goes 1 failed, 1 passed.
5. Worktree: `test_f7_restore_wake.py` 2 passed. `test_frame339_removal_stray.py`, `test_frame330_stopped_bouncing.py`, `test_touch_divergence.py` and `test_roles_doc.py` give 63 passed and 1 failed.
6. Worktree: `test_l1.py -k` on the three touch cases. `L1-AR-judge-a-stray-foreseen-or-a-mistake` passes. `L1-DV-take-a-mistake-out` and `L1-DV-put-back-a-removed-block` are STALE. The run writes rows to the worktree's untracked `tests/rota/cassettes.db`.
7. `f7par/` and `f7par2/`: `git archive` of 442e32b0, with a backup copy of the cassettes. `L1-DV-take-a-mistake-out` is STALE at the parent, and the test_roles_doc test is red at the parent.

## (d) Usage

Input about 62k tokens, output about 9k tokens, total about 71k. This is over the 50k cap.

# F7 review p3b: e855bd79 on f7b, against f6b0f41f

Verdict: READY. The three high findings of p3 are closed. Two low findings remain. Each one is PLAUSIBLE, and the recorded case can measure both.

## (a) The verdict on each point

1. The grader plants: PASS. A docstring-only plant, a comment-only plant, a wrong-path plant and an uncommitted plant each fail. A committed restore of both base lines in the body passes (probe 8).
2. The wake detail: PASS. The bg_3 wake at 128bec7e prints the `mistake` row and its note in the head, before `[batches.expect]` and before `[removed lines]`.
3. The mode sentence: PASS. "For the `removal:` row in your wake, put back only its lines from `[removed lines]`." The sentence has 15 words and one instruction.
4. New behaviour beyond the three highs: the wake detail of `touch_mistaken` now holds each note. The cycle key holds that detail, and `live_detail` now rebuilds the detail of a case wake (finding 8).
5. Foreign hunks and CR bytes: none. All six files hold 0 CR bytes. Each hunk serves findings 1, 2 or 3 of p3.

### The detail the seat now sees

```
You were woken by: tick:touch_mistaken
Refs: bg_3
src/click/utils.py::format_filename (removal: `filename = os.fspath(filename)` at line 471, `if isinstance(filename, bytes):` at line 473 The removal of the old logic for handling bytes and encoding is a mistake. The request only asked for an example in the docstring, not a rewrite of the function. The removal touches a definition not named in the request or any criterion.)
```

The wake is 29,898 characters, and `[code.diff]` starts at character 5,390.

## (b) Findings

7. `rota/roles/prompts/developer/touch_mistaken.md:14`, low, PLAUSIBLE. "Put back only its lines" can read as "only the quoted lines". The note quotes two first lines, and the night's seats failed on that same reading. The note's first quoted line, `filename = os.fspath(filename)`, is not in `[removed lines]` (p3 finding 4). Fix: "For the `removal:` row in your wake, put back the whole block that `[removed lines]` shows for its grain."
8. `rota/core/predicates.py:2430`, low, PLAUSIBLE. The detail now holds each note, and `cycles._key` holds the detail. The Architect writes a new note on each new head, so a restore that bounces gives a new key each round. Then the cycle check cannot see the bounce. Before the change, the key held the path only. `test_cycles.py` and `test_frame330_stopped_bouncing.py` pass, and no test bounces a `touch_mistaken` wake. Fix: keep the notes in the shown detail, and keep the paths only in the cycle key. As an alternative, add a test that proves the bounce is still found.

Closed from p3: findings 1, 2, 3 and 5. Findings 4 and 6 stay low and open. The wake now names the judged grain, so finding 6 is smaller.

A dead-code plant after `return filename` passes the grader. A seat does not write dead code to pass a case, so this review does not count it as a finding.

## (c) Probes

8. `f7r_p3b.py` in the scratchpad reuses `_night172` and `_plant` of the unit test. Docstring-only, comment-only, wrong-path, uncommitted and string-literal plants FAIL. The committed restore PASSES, and the dead code after `return` PASSES.
9. `f7r_p1.py` on `n172_f7r_b.db`, a fresh copy of `clickI_night172.db`. It builds the bg_3 wake at e855bd79. The output is `f7r_wake_b.txt`.
10. Worktree: `test_f7_restore_wake.py`, `test_cycles.py`, `test_frame330_stopped_bouncing.py`, `test_frame339_removal_stray.py` and `test_touch_divergence.py` give 71 passed. In `test_l1.py -k` on the three touch cases, the Architect case passes. `L1-DV-take-a-mistake-out` and `L1-DV-put-back-a-removed-block` are STALE, as at f6b0f41f.

## (d) Usage

p3b: input about 15k tokens, output about 5k tokens, total about 20k, under the 30k cap.
