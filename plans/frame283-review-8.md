# Frame 283, review 8: pass 6 at f99cc25f

Reviewer: one Opus agent, read-only, worktree `C:/Users/roman/rota_r283b` at
f99cc25f. Written 2026-10-24. Nothing was built. `git status` of the worktree is clean.

## Verdict

Accept pass 6. The code matches the rule, s340 stays refused, and every scene file is green.
The four Developer tests still check the head stamp and the Critic diff.
The known price is real: a same-kind swap of a `return` or a call opens no note.
Night 163 cannot measure that price, because night 163 runs the 214d22d0 code.

## (a) Verdict per point

1. Pass. `_whole_lost` names a statement only when its (owner, kind) and its (owner, key) both fall. Probes A to D give the expected notes. One mis-name exists in a mixed shape (finding 2).
2. Pass. `test_frame283_whole_file_drop.py` is 17 passed. The s340 case names 8 statements and refuses the commit. The six shapes pass: `class_shared_line`, `def_inside_if_block`, `dup_inside_one_def`, `nested_inner_shared_with_outer`, `no_def_file_middle`, `toplevel_if_block`.
3. Pass. `test_scene_review.py` 34 passed. `test_scene_large_module.py` 19 passed, 2 skipped, 1 xfailed. `test_developer.py` 37 passed. The four tests keep their assertions unchanged, and only the written text changed.
4. Pass, with one note. `_whole_drop`, `_tail_drop` and `_unruled_removal` have no hunk. `_lost_statements` moved its key to `_line_key` with the same body. `_drop_note` moved its sentence to `_with_lost` with the same logic. The pinned texts changed beyond "removes or rewrites" in the route sentence (finding 4).
5. One realistic admitted edit exists: `validate(r)` replaced by `log.debug(r)` in `save`, Expr Call 2 to 2. Night 163 cannot measure it (finding 1).

## (b) Findings

1. **The same-kind swap opens no note.** `rota/roles/api.py` 21153-21159. Severity high for the case class of the frame. CONFIRMED: probe F (`ctx.exit()` to `log(msg)`), probe G (`return option(f, **kw)` to `return None`) and probe I (`validate(r)` to `log.debug(r)`) each return None. A guard `raise` changed to a `return` is still named (probe H), because the Raise count falls. Night 163 runs on b29b6d8b, the 214d22d0 code tree (`plans/stack.md` line 1547), so it holds no pass 6 code. A swap also writes no note row, so only a diff read of each whole-file write can find one. Night 162 saw 0 whole-file drop samples in 7 whole-file writes. Fix: record the price in the frame, or keep Return and Raise on the line-key rule.
2. **A rewritten sibling takes the shortfall of a statement inside a lost block.** `rota/roles/api.py` 21156-21162. Severity low. CONFIRMED: probe E drops `if q: return b` and rewrites `return a` to `return A`. The note names `return a` and `if q:`. The Return inside the lost block consumes no shortfall before `return a` does. The note still opens and the commit is still held. Fix: let a statement inside a key-short block take its kind's shortfall before a sibling outside the block.
3. **An assignment keys on its target, so the note can name the kept one of two assignments to one name.** `rota/roles/api.py` 21089-21091. Severity low. PLAUSIBLE: with old `x = 1` and `x = 2` and new `x = 1`, both counts fall by 1, and the file-order walk names `x = 1`. The `_owned_statements` docstring says that a new value is a new wording, but the target key makes the value invisible. Fix: key an assignment on its whole line, or correct the docstring.
4. **The pinned route sentence changed beyond "removes or rewrites".** `rota/roles/api.py` 19479-19487 (`_note_routes`, pass 5c), pinned in `test_frame140_commit_beside_note.py` and `test_frame283_removal_on_ruling.py`. Severity low. CONFIRMED by `git diff 214d22d0 f99cc25f`. The route now says "To undo the change ... To keep the change, send msg.escalate_architect and name the change to the Architect." `_code_write` 18331-18342 also adds the sentence "The file no longer defines ..." to a stored note on both branches (pass 5b). Both are intended by earlier passes. Fix: name both changes in the frame's closing record, so that night 163 and later reads do not take them for pass 6.
5. Outside the points. **The commit message of the four Developer tests still says "empty formatting".** `tests/rota/test_developer.py` 282, 303, 334, 535. Severity low. CONFIRMED by read. No assertion reads the message. Fix: none needed for behaviour.

## (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/f3a8d4c2-cdca-42d3-8f1d-12549648d58a/scratchpad/probe283r8.py`, run with `PYTHONPATH=.` from the worktree root. It calls `_whole_lost` on nine shapes. Results:
  - A, two Returns and the text keeps one: names `return a` only.
  - B, `return go()` becomes `go()`: names `return go()`.
  - C, nested `inner` renamed `inner2` with its lines intact: None.
  - D, `go()` moved from `f` to `g`: names `go()`, a drop under `f`.
  - E, a rewrite beside a dropped block: names `return a` and `if q:` (finding 2).
  - F, G, I, same-kind swaps: None (finding 1).
  - H, `raise ValueError(x)` becomes `return 0`: names the `raise`.
- One pytest run of `test_developer.py`, `test_scene_review.py`, `test_scene_large_module.py`, `test_frame283_whole_file_drop.py`, `test_frame140_commit_beside_note.py` and `test_frame283_removal_on_ruling.py` with `ROTA_MODEL=qwen3:8b`: 217 passed, 2 skipped, 1 xfailed in 165 s.
- `git diff 28cb0d00 f99cc25f` and `git diff 214d22d0 f99cc25f` on `rota/roles/api.py` and the five test files.
- A first copy of the probe under `tests/rota/` failed on the import path and was deleted. No gate ran.

## (d) Usage

About 75k input tokens and 9k output tokens, about 84k in total. This is an estimate, because the agent sees no exact count.
