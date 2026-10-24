# Frame 306, review 3: pass 2 at feb198eb, the shape detector

Read-only review on Opus, 2026-10-24, from `C:/Users/roman/rota_r306b` at
feb198eb. Probes are in
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/f33f3f44-c058-42c9-90d1-bfcf8f3dafaa/scratchpad/r3/`.

**Verdict: not accepted as is. One high in the pass needs one fix before a
night. The other high is outside the pass and belongs to frame 283.** The
five probes of the report hit. The rules match section 7.2 of the design.

## (a) The verdict on each point

1. The rules: the code matches section 7.2 and option (e) on all seven shapes. Two design prices show (L1, L3).
2. The name check is a word match, as the design asks. `file` against "filename" and `nl` against "newline" raise rows.
3. A second commit writes a new row on the new sha, not the same row. A judged hunk grain hides later removals in that hunk (H1).
4. No batch of nights 160 and 161 is skipped. Night 161 b_1 and b_3 hold a prediction. Count: 0 of 8.
5. The filter skips no file of click's source. `src/click/testing.py` is not a test path and is read.
6. At 214d22d0 the door does not refuse the drop. Frame 283's mechanism is not met (H2). Shape 2 now holds the merge.
7. All five probes hit, six cases in total.
8. Cost: about 0.08 s for `shape_grains` on `core.py`, 3800 lines, and 0.07 s for one `git diff`.

## (b) Findings

1. **H1. A judged hunk grain hides a later removal in the same hunk.**
   `rota/roles/api.py` 19793 to 19796 and 19675. Severity high.
   CONFIRMED: `p3_hunk.py`. Commit 1 edits a docstring line, grain
   `f:L2`. Commit 2 also removes `ctx.exit()` in the same hunk. The
   cumulative diff gives the grain `f:L2` again. `_shape_strays` drops
   it as judged, so the removed statement gets no row. Point 6 shows that
   a whole-file write opens no note for it either, so nothing holds it.
   Fix: key the shape 2 grain per removed line, or re-raise a judged hunk
   when its removed set grows.
2. **H2 (outside the pass, frame 283). The note door reads only notes.**
   `rota/roles/api.py` 18848 `_unruled_removal` reads `_closed_notes`,
   and 20843 `_whole_drop` sees top-level lines only. Severity high for
   frame 283. CONFIRMED: `p6_door.py`, run on a `git archive` of
   214d22d0 and on feb198eb. A whole-file write that drops `bar(x)` from
   inside a kept definition returns no `dropped` key. The commit lands at
   214d22d0 with no hold. At feb198eb the same commit lands with the row
   `echo:L3`, so the merge waits for the Architect. A drop of a
   top-level `if` block opens a note, and the door refuses it. Frame
   283's mechanism, "a commit whose tree removes a statement that no
   landed note names is refused whatever reply wrote it", is not met.
   Shape 2 is a hold that `foreseen` releases, not a refusal. Fix: let
   the door diff the base statements against the tree at the commit.
3. **L1. Rule 3 hides a short removed statement under a longer added
   line.** `rota/roles/api.py` 19791. Severity low. CONFIRMED:
   `p1_rules.py` case H2. A removed `ctx.exit()` beside the added line
   `ctx.exit_code = context.exit_hint()` raises nothing. Case H, a removed
   `return x` beside `return_value = max(x)`, raises nothing. Section 7.1
   says shape 2 covers the statements that the door reads as changed.
   Rule 3 makes it blind to those when the new line is longer.
   Fix: apply rule 3 only when the added line starts with the removed
   line's first token, or state the price in the design.
4. **L2 (outside, inherited from the route). A `mistake` releases the
   merge after any later commit.** `rota/core/lifecycle.py` 764 and
   `rota/roles/api.py` 19638. Severity low. CONFIRMED: a `mistake` row on
   sha1 with the head at sha2 gives `mergeable` None. `_shape_strays`
   does not raise the judged grain on sha2, even if the line is still
   there. Fix: raise a `mistake` grain again on the new head while the
   diff still holds it.
5. **L3. A new or renamed definition raises one row for each defaulted
   parameter.** `rota/roles/api.py` 19771. Severity low. CONFIRMED:
   case I raises `g(b)` and `g(c)` for a new `def g(a, b=1, c=2)`. A
   renamed parameter raises a shape 1 row and a shape 2 row. The design
   says "any definition", so the code matches. The price in Architect
   wakes on a feature that adds a function is not measured. Fix: count
   the rows in the next night's measure.
6. **L4. Shape 1 skips `**kwargs` and a parameter that gains a
   default.** `rota/roles/api.py` 19693 and 19771. Severity low.
   CONFIRMED: cases F3 and F4 raise nothing. Both make a call optional
   that was not optional. Fix: count `**kwargs` and a new default as
   shape 1, or name the gap in section 7.
7. **L5. `_is_test_path` skips a source module named `test_*.py`.**
   `rota/roles/api.py` 21249. Severity low. CONFIRMED:
   `src/click/test_utils.py` gives True. Click has no such module. Fix:
   none for this frame. Name the rule in the brief.

## (c) Point answers

1. Moved line: no row. Rule 2 matches. Re-indent only: no row, also for a
   line moved into an `if` body. Rule 2 strips, so the design says the
   same. Removed blank line: no row, rule 1. Parameter renamed with a
   default: `echo(fp)` and `echo:L1`. Renamed without a default: `f:L1`.
   Parameter added without a default: no row. The old line is a
   subsequence, and shape 1 reads defaults only. The design says the
   same. `*args`: no row. A keyword-only parameter with a default:
   `f(flag)`, as the design asks. A removed line inside a module string
   that spans lines: `module:L2`, as section 7.1 asks.
2. The pattern rejects a letter, a digit or an underscore on each side of
   the name, over each criterion text and surface ref. It is a word
   match. "filename", "file_path" and "newline" raise rows. "the file
   argument", "file-like" and a surface `utils.py::echo(file)` silence
   `file`. Section 7.2 asks for a token match, so the code agrees.
3. The key is `batch:sha:grain`, so commit 2 writes a second row and
   does not overwrite. `mergeable` and `touch_strayed` read only the
   rows of the head, so the sha1 row has no effect. An open grain is
   raised again on sha2. A judged grain is not raised again.
   `judge_touch` reads only the open rows of the head. `_covers` folds
   `path::def(param)` and `path::def:Lnnn` under the bare path and
   `./path`, per the pass's test. The defect is H1.
4. The rule: `_shape_strays` returns nothing when `_predicted_touch` is
   empty, that is no `path` grain and no `symbol` grain with `::`. Night
   160 has 3 batches and night 161 has 5. Each holds 2 to 5 such grains.
   The `annotate` predicate writes the touch set while a batch is
   pending, so it lands before the first commit of the Developer
   (PLAUSIBLE, the sessions table holds no batch id). No batch is
   skipped. Night 161 b_1 and b_3 are not skipped. The red tests are met
   on a night.
5. A test path is a path under `tests/` or a `/tests/` directory, a name
   that starts with `test_` or ends with `_test.py`, or `conftest.py`.
   `src/click/testing.py` is not a test path, so the detector reads it.
6. See H2. The door refuses only through an open or restored note. A
   whole-file write opens a note for top-level lines only. The pass's
   shape 2 raises the removal as a row, so the merge holds where the door
   did not refuse. The frame 283 mechanism is not met at 214d22d0 or at
   feb198eb.
7. Night 161 b_1: `utils.py::echo_json(file)`, hit. Night 161 b_3:
   `termui.py::confirm:L319`, hit. Night 158 bg_3: `version_option:L467`
   and `version_option.callback:L548`, hit. Night 154 b1:
   `echo_json(file)` and `echo_json(nl)`, hit. Night 159 bg_1 and night
   156 bg_1: none, hit. The probe script reads the words directly and
   skips the prediction gate, so point 4 covers that gate.
8. One synthetic commit on `core.py` gave `Context.__init__:L359` in
   0.076 s per call, with 0.067 s for the diff. `_shape_strays` adds one
   `git cat-file` and `_base_text`, so the cost stays below 0.3 s per file.

## (d) Probes

- `r3/p1_rules.py`: `shape_grains` on 16 synthetic diffs from `git diff --no-index -U0`.
- `r3/p3_hunk.py`: two cumulative commits in one hunk, H1.
- `r3/p4_pred.py`: `batch_touch` and `touch_strays` of nights 160 and 161, read-only.
- `r3/p6_door.py`: the Developer's `code.write` and `code.commit` through the sandbox, at feb198eb and at a `git archive` of 214d22d0 in `r3/at214`.
- Inline: the word match on seven texts, a `mergeable` call on a `mistake` row, the timing on click's `core.py` at 2c8cd3ac, and the report's probe script pointed at `rota_r306b`.

## (e) Usage

About 80k input tokens and 12k output tokens, about 92k in total. These are estimates from the context.

## High 2, pinned

Follow-up on Opus, 2026-10-24, at feb198eb. The door code is identical at 214d22d0, because `git diff --stat 214d22d0 feb198eb` names only additions of the shape detector.

1. Frame 283's tests are green. `tests/rota/test_frame140_commit_beside_note.py` and `tests/rota/test_frame283_removal_on_ruling.py` gave 110 passed. The s340 cases are `test_s340s_unchanged_write_sends_the_note_again_and_holds_the_commit` and `test_s340s_commit_in_the_reply_after_the_unchanged_write_is_refused`.
2. The test opens its note with a span write. `_noted_then_refused` (test line 343) calls `code.write(start=546, end=556)`. The span branch, `rota/roles/api.py` 17458, calls `_drop_note`, and `_drop_note` (21204) calls `_lost_statements`, which names each statement of the span that the text does not hold. The whole-file resend of the test only repeats the open note (18262 to 18264, `_open_notes`, `held["noted"] == text`). My probe makes the drop with a whole-file write as its first write. The whole-file branch, 18279, calls only `_whole_drop` or `_tail_drop`. `_whole_drop` counts top-level lines outside the kept definitions, and `_tail_drop` counts lines after the last terminator. Neither calls `_lost_statements`, so a statement removed from inside a kept definition opens no note. The owner is nested in both cases, the path form is the same relative form, and both use the fixture's base commit. The difference is the write form, not the setup.
3. The night 158 refusals of `ctx.exit()` fit the same split. Section 7.1 of the design reads that note as a span write note (PLAUSIBLE, I did not read s279's call).
4. The gap is a shape that frame 283 never covered, not a regression. `git log -S` puts the whole-file branch at 3b4b9238 (2026-09-30) and 791da68d, before frame 283, and no commit since 2026-10-23 changes it.
5. Fix: in the whole-file branch at 18279, also call `_lost_statements(old, 0, len(old), text)` and store each lost base statement in the note, as `_drop_note` does for a span.

The fix line is CONFIRMED in part. `_lost_statements(old, 0, len(old), text)` on the probe's whole-file write returns `[(2, 'bar(x)')]`. The note text and the stored lines are not probed.

## Pass 2b re-probe

Read-only re-probe on Opus, 2026-10-24, of 11e031c0. I did not check out the commit, because a checkout changes the worktree. I ran the probes on a `git archive` of 11e031c0 in `scratchpad/r3/at11e`.

**Verdict: accepted. H1 is fixed. L1 is fixed in part, and the residue stays low.**

- H1, fixed. CONFIRMED: `p3_hunk.py` gives `f:L2` on commit 1 and `f:L2`, `f:L3` on commit 2. The judged line no longer hides the removal of `ctx.exit()`.
- L1, fixed in part. CONFIRMED: `return x` beside `return_value = max(x)` now raises `f:L3`. `ctx.exit()` beside `ctx.exit_code = context.exit_hint()` still raises nothing. The added line starts with `ctx.exit` and ends with `()`, so `_is_widening` reads one insertion. This is the class that the implementer names with `ctx.exit_code = f()`. Fix, if it is wanted: let the inserted run start only after an open bracket or a comma in the removed text.
- The five probes of the report still hit. Night 158 bg_3 now gives 12 rows, one for each removed docstring line plus `ctx.exit()`, and no row for the `message %` line. One bare-path judgement closes them all.
- The three test files, `test_touch_divergence.py`, `test_desk_guards.py` and `test_shape_strays.py`, give 383 passed.

## Pass 3 review

Read-only review on Opus, 2026-10-24, of 237d4fb6 on a `git archive` copy in `scratchpad/r3/at237`. Probe: `scratchpad/r3/p9_notice.py`, a database with eleven `touch_strays` rows of each status on a merged batch and a running batch.

**Verdict: accepted, with two lows on the words and one gap to record. No high.**

1. The filter is right. CONFIRMED: a `foreseen` row from the shape detector, `echo_json(file)`, and one from the definition detector, `echo_json`, show. The `mistake` row and the `open` row do not show. The running batch's `foreseen` row does not show. Rows on two commits of one batch fold into one line.
2. The words read as a notice and end with no question. They carry no batch id and no sha, and they quote the Architect's note. Two lows:
   - Low A. Each removed line is one sentence. Five docstring lines give five sentences, and each repeats the path and the note. Night 158 bg_3 would give eleven. Fix: fold the consecutive lines of one definition into one range, "lines 467 to 471", with the note once.
   - Low B. "Line 319 of `confirm` ... removed" names an edited line as removed. Night 161 b_3 changed the line. The reader cannot tell a deletion from an edit. Fix: say "changed or removed" when the hunk adds lines.
3. Low C, the deviation. A whole-file stray judged foreseen merges with no notice. That change is invisible to him, and "no work stays invisible" covers it. One line for it: `In "echo json": src/click/extra.py changed, a file the plan did not name (the Architect: helper).` Fix: let `_grain_words` give that sentence for a grain with no `::`.
4. Confirmed at 214d22d0. `batches_strays`, at line 19694, reads only `commit_sha = head_commit`. Its one reader is the Developer's `touch_mistaken` brief. That brief reads it while the head is still the judged commit, so the reader is right today. After a later commit, the view is empty. This is the same mechanism as L2, where a `mistake` row stays behind on the old head. It is worth one line on the frame that takes L2, not a frame of its own.
5. The three pass 2 files, the five `render_state` files, `test_frame307_night_counters.py`, `test_nightreport.py`, `test_frame309_test_run_journal.py` and `test_verdict_lines.py` give 658 passed and 1 skipped.

Outside: the notice drops `mistake` rows because "a mistake row names a change taken out". L2 shows that a `mistake` can merge after any later commit. Such a change then shows nowhere. The fix for L2 also closes this gap.
