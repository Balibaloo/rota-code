# Frame 283, review 5: pass 5 at 05fd6976

**Verdict: not accepted.** The red case is fixed, and the four test files give 475 passed. The frame's mechanism is still not met. `_whole_lost` reads each kept top-level definition against one set of lines. So a line held anywhere else in the same definition hides the drop. This is the pass's own deviation 1, one level down. Read-only review on Opus, 2026-10-24, in `C:/Users/roman/rota_r283b` at 05fd6976.

## (b) Findings

### High

1. `rota/roles/api.py:21054-21080` `_whole_lost`, high, CONFIRMED (probe `r5/test_p5r.py`). The scope of the held set is the whole top-level definition, not the owner of the line. Three probes drop a statement, see no note, and the commit lands:
   - `class_shared_line`: `return self.v` dropped from `Box.a`, and `Box.b` holds `return self.v`.
   - `nested_inner_shared_with_outer`: `stop()` dropped from `f.inner`, and `f` holds `stop()`.
   - `dup_inside_one_def`: one of two `go()` lines in `f` dropped.
   Click's classes, such as `Context` and `Command`, repeat lines such as `return rv` across methods. Fix: for each old statement line, compare its count under its qualified owner in the old text and in the new text, as `_restored` does with `_def_spans` and `_def_lines`.
2. `rota/roles/api.py:18279-18283`, the whole-file branch, high, CONFIRMED (probe `r5/test_p5r.py`). A statement outside every kept definition and below a kept top-level line opens no note. Three probes land the commit:
   - `toplevel_if_block_nested`: `stop()` dropped inside a top-level `if sys.argv:` block. `_whole_drop` keeps the block on its header line.
   - `def_inside_if_block`: `stop()` dropped inside `def h()` under a top-level `if`.
   - `no_def_file_middle`: `stop()` dropped from a file with no definition. `_kept_spans` is empty, so `_whole_drop` and `_whole_lost` return nothing, and `_tail_drop` reads the tail only.
   The gap is older than the pass. It still leaves the mechanism unmet. Fix: the owner-count walk of finding 1 over the whole file, with owner `""` for module-level lines, covers these too.

### Low

3. `rota/roles/api.py:18323-18328` with `_stored_note`, low, CONFIRMED (probe `moved_under_class`). A definition moved under a class stores `defs: ["f"]`, but the note text names only `go()` and `stop()`. The Developer cannot restore by putting those lines in `C.f`, because `_restored` needs a top-level `f`. The cause is older than the pass. Fix: name each dropped definition in the text that `_stored_note` builds.
4. The note text for a changed line, low, CONFIRMED (probe `price_flow`). The note says "removes" and "Put the line back" for an edit of `return x` to `return x + 1`. The restore undoes the edit, so the escalation is the only route. Fix: say "changes or removes" when the owner holds a new line at the same place.

## (a) The points

1. Met. CONFIRMED by the new test file and by the full run. The first whole-file write that drops `ctx.exit()` in `version_option` gives one note, "`ctx.exit()` at line 550". `custom_version_option` still holds `ctx.exit()`. The next commit is refused with `FIRST`. The restore write gives a `restored` row. The restore test asserts only that the commit is not `True`, which is weak but correct.
2. Probe results for each shape:
   - A renamed definition (`f` to `g`): a note opens through `_whole_drop`, with 3 lines and `defs: ["f"]`. The commit is refused.
   - A definition moved under a class: a note opens with `go()` and `stop()`, and the commit is refused. See finding 3.
   - A nested function: a note opens for `stop()` under owner `f.inner`. If the outer body holds the same line, no note opens (finding 1).
   - Two classes with method `m`: a note opens for `go()` under `A.m`. The scope by top-level name keeps `B.m` out.
   - A method in a kept class: a distinct line opens a note under `Box.a`. A line that another method holds opens none (finding 1).
   The `_base_held` exact-name finding of review 3 does not return. `_base_held` at 19399 reads the base lines under any owner, and the renamed and moved cases store and refuse.
3. No double note. CONFIRMED (probe `span_after_whole`). A top-level and a nested drop give one note with `UNUSED = 1` and `stop()`, each once. A whole-file write that repeats the open note returns the same `dropped` text by the unchanged path and stages no new row. A later span write on the same path adds `go()` to the one entry, and no line repeats.
4. The price holds, CONFIRMED. By the frame's words, a whole-file write is "whatever reply wrote it", so the same rule applies as for a span write. `return x` to `return x + 1` opens "This write removes 1 statement that your text does not hold: `return x` at line 2." The next commit is refused with "A note does not allow a removal. Put the line back with code.write, then commit in your next reply. Or send msg.escalate_architect and name the removal." The Developer keeps the edit only by the escalation. The recovery costs one reply for the refused commit, one reply for the escalation, one Architect turn and one reply for the commit, so three Developer replies and one Architect turn at the least. The pass counted zero such cases on nights 160 and 161.
5. Confirmed. `_drop_note(old, 0, 2, new)` and `_whole_lost` on the test's text both give "This write removes 1 statement that your text does not hold: `return x` at line 1."
6. `test_frame140_commit_beside_note.py`, `test_frame283_removal_on_ruling.py`, `test_frame283_whole_file_drop.py` and `test_desk_guards.py` give 475 passed. Those files hold all of the span and whole-file write tests that a grep for `_whole_drop`, `_tail_drop` and `_drop_note` finds. `tests/rota/test_shape_strays.py` does not exist at 05fd6976. The probe file gives 14 passed, because the probe prints its results and asserts nothing.

## (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/f33f3f44-c058-42c9-90d1-bfcf8f3dafaa/scratchpad/r5/test_p5r.py`: 14 cases through the Developer sandbox, `code.write` then `code.commit`, on a small two-commit worktree. Run from the worktree root with pytest `-s`.
- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/f33f3f44-c058-42c9-90d1-bfcf8f3dafaa/scratchpad/r5/p5_span.py`: `_drop_note` against `_whole_lost` on the desk guard's text.
- The four test files with pytest, from the worktree root.

## (d) Usage

About 50k input tokens, 10k output tokens, 60k in total. These are estimates from the context.

## Pass 5b re-probe

Read-only re-probe on Opus, 2026-10-24, of 3a1f8112, on a `git archive` copy in `scratchpad/r5/at3a1`.

**Verdict: accepted.** The 14 probe cases each give a note and a refused commit. The four test files give 483 passed.

- High 1, fixed. CONFIRMED: `class_shared_line` names `return self.v` under `Box.a`. `nested_inner_shared_with_outer` names `stop()` under `f.inner`. `dup_inside_one_def` names `go()` with count 2. Each commit is refused.
- High 2, fixed. CONFIRMED: the top-level `if` block names `stop()` under owner `""`. The def under the `if` names `stop()` under `h`. The file with no definition names `stop()` under `""`. Each commit is refused.
- Low 3, fixed. CONFIRMED: `moved_under_class` now adds "The file no longer defines `f` by that name. The note closes when it does again."
- Low 4, fixed in part. The note for `return x` to `return x + 1` is now "This write removes or rewrites 1 statement that your text does not hold: `return x` at line 2." The refusal is "A note does not allow a removal or a rewrite. Put the line back with code.write, then commit in your next reply. Or send msg.escalate_architect and name the change." The text still sends an edit to "Put the line back", which undoes the edit.
- The route still exists. `msg.escalate_architect` is in the Developer's `tests_failing` tools. "Name the change" asks for an escalation message, not a ledger note, so it does not point at the close that pass 2 removed. The recovery cost of point 4 stays the same: three Developer replies and one Architect turn at the least.
- Tests: the four files give 483 passed at 3a1f8112. `tests/rota/test_shape_strays.py` is still absent.
