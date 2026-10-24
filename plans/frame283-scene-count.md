# Frame 283, the scene count: dropped against rewritten statements

Reviewer: one Opus agent, read-only, worktree `C:/Users/roman/rota_p283b` at
28cb0d00. Written 2026-10-24 13:45. Nothing was built.

## Verdict

The candidate rule turns every scene red green, and it keeps s340 refused.
All 201 statements that the two scene files name keep the count of their
kind, so the rule reads them as rewritten. All 7 statements of s340 lose
their kind count, so the rule reads them as dropped. Four reds of
`test_developer.py` stay red, and they are right notes. Those tests write
`# emptied` over `formatting.py` on purpose, so each drops
`ELLIPSIS = chr(8230)` and loses the owners `plural` and `truncate`.

The counts, per refused write:

| Set | Dropped | Rewritten | Lost owner |
|---|---|---|---|
| `test_scene_review.py` (1 write, 34 reds) | 0 | 1 | 0 |
| `test_scene_large_module.py` (1 write, 18 reds) | 0 | 200 | 0 |
| `test_developer.py` (5 writes, 5 reds) | 4 | 1 | 12 |
| `test_night46_context.py` (1 red write) | 0 | 1 | 0 |
| s340, `version_option` | 7 | 0 | 0 |

The scene totals: 0 dropped, 201 rewritten, 0 lost owner. With
`test_developer.py` and night 46: 4 dropped, 203 rewritten, 12 lost owner.

The price: the rule admits any statement that the text replaces with one of
the same kind under the same owner. The probe shapes show three such
admissions. `ctx.exit()` replaced by `log(msg)` opens no note.
`return option(f, **kwargs)` replaced by `return None` opens no note. A
drop of `ctx.exit()` plus a new call anywhere in the same owner opens no
note. Of the 14 shapes of review 5, 2 become rewritten (`price` and
`price_recovery`), and each is an admitted edit, not a lost removal.

Recommendation: adopt the kind count, with two conditions. First, apply it
to the span branch too (finding 1). Second, accept the same-kind swap as the
known price, and record it in the frame. No rule in the data separates a
same-kind swap from a rewrite. The texts of both are new, and the kind and
the owner are the same.

## 1. The reds, classified

Runs: `test_developer.py` whole, `test_scene_review.py` whole and with
`-k a_right_call_lands_review`, `test_scene_large_module.py` whole and with
`-k calls_leave_the_scene`, and `test_night46_context.py` whole. A capture
plugin wrapped `_whole_lost` and recorded the old text, the new text and
each named line.

The scene files use a module-scoped fixture. One refused write fails every
test of the file. So 34 reds come from one write, and 18 reds from one
write.

| Test | File | Statement | Owner | Old count | New count | Class |
|---|---|---|---|---|---|---|
| `test_the_developer_can_read_write_and_commit` | `src/billing/charges.py` | `return round(amount_cents * days_used / days_in_period)`, new `return int(...)` | `prorate` | Return 1 | 1 | rewritten |
| `test_the_commit_stamps_the_batch_head`, `test_critic_sees_an_actual_diff`, `test_what_critic_sees_is_the_same_twice`, `test_a_batch_with_no_commit_says_so` (the same write) | `src/notify/formatting.py` | `ELLIPSIS = chr(8230)` | module | Assign 1 | 0 | dropped |
| the same four | the same | `return text if len(text) <= limit ...` | `truncate` | Return 1 | 0 | lost owner |
| the same four | the same | `if count == 1:` | `plural` | If 1 | 0 | lost owner |
| the same four | the same | `return f"{count} {plural_form or singular + 's'}"` | `plural` | Return 2 | 0 | lost owner |
| `test_scene_review.py`, all 34 | `src/billing/charges.py` | `return round(...)`, new `return amount_cents * days_used / days_in_period` | `prorate` | Return 1 | 1 | rewritten |
| `test_scene_large_module.py`, all 18 | the ledger module, 1002 lines | `return amount_cents * N // 1000`, new `... // 1000 + 1`, N from 1 to 199, and `late_fee` | `rate_001` to `rate_199`, `late_fee` | Return 1 each | 1 each | rewritten, 200 |
| `test_the_commit_records_an_unnamed_definition_as_a_stray_the_architect_judges` | `src/click/utils.py` | `sys.stdout.write(str(message))`, new `print(message)` | `echo` | Expr Call 1 | 1 | rewritten |

The night 46 file has four other noted writes that do not fail. One of them
drops `sys.stdout.flush()` from `echo`, Expr Call 2 to 1, and the rule reads
it as dropped. That test expects a note, so it stays green.

## 2. The lost owners

`plural` and `truncate` are gone from the file. The write is `# emptied`
plus a newline. Nothing is renamed or moved. The test is plumbing, not a
scene with a task: "P1's whole mechanism: the gates fire on a commit they
have not judged" (`tests/rota/test_developer.py` line 264). The write
removes every definition on purpose. So the note is a right note by the
mechanism of the frame.

Before pass 5, this write opened no note. `_whole_drop` returns None when
the text keeps no old definition (`rota/roles/api.py` line 20685), and
`_tail_drop` gave none. So the four tests passed on a gap, not on a rule.
The repair belongs in the tests. They must write a text that keeps the old
statements, or read the note and send it on the escalate route.

## 3. s340

The premise of the brief needs one correction. Every s340 write to
`src/click/decorators.py` is a span write, not a whole-file write. Turn 7
writes `start=420, end=567`, turn 9 the same, and turns 13 and 19
`start=420, end=557` (`turns` and `tool_calls` of
`.rota/clickI_night154.db`). The span branch noted 7 statements at turn 7,
as `plans/night154-read.md` section 2 says.

The landed change is `git diff ee59f61 1e9925f` in
`D:/repos/_AI/sample_repos/clickI`, 10 lines deleted from the tail of
`version_option`. Read as a whole-file write, `_whole_lost` names the same 7
statements. The kind counts under the owner `version_option` fall:

| Statement | Kind | Old count | New count | Class |
|---|---|---|---|---|
| `if not param_decls:` (holds `param_decls = ("--version",)`) | If | 6 | 5 | dropped |
| `kwargs.setdefault("is_flag", True)` | Expr Call | 4 | 0 | dropped |
| `kwargs.setdefault("expose_value", False)` | Expr Call | 4 | 0 | dropped |
| `kwargs.setdefault("is_eager", True)` | Expr Call | 4 | 0 | dropped |
| `kwargs.setdefault("help", ...)` | Expr Call | 4 | 0 | dropped |
| `kwargs["callback"] = callback` | Assign | 9 | 7 | dropped |
| `return option(*param_decls, **kwargs)` | Return | 1 | 0 | dropped |

The owner `version_option.callback` does not change. The whole-file shape
of the frame, `ctx.exit()` dropped inside the kept callback, also stays
dropped: Expr Call 2 to 1 (probe `price.py`, case `drop_exit_only`).

## 4. The 14 shapes of review 5

The shapes are from `r5/test_p5r.py` of session f33f3f44.

| Shape | Named statement | Owner | Kind | Old | New | Class |
|---|---|---|---|---|---|---|
| `class_shared_line` | `return self.v` | `Box.a` | Return | 1 | 0 | dropped |
| `class_distinct_line` | `self.n = 1` | `Box.a` | Assign | 1 | 0 | dropped |
| `two_classes_same_method` | `go()` | `A.m` | Expr Call | 1 | 0 | dropped |
| `dup_inside_one_def` | `go()` | `f` | Expr Call | 2 | 1 | dropped |
| `nested_inner` | `stop()` | `f.inner` | Expr Call | 2 | 1 | dropped |
| `nested_inner_shared` | `stop()` | `f.inner` | Expr Call | 2 | 1 | dropped |
| `renamed_f_to_g` | lines 5 to 7, by `_whole_drop` | `f` | none | | | lost owner |
| `moved_under_class` | lines 5 to 7, by `_whole_drop` | `f` | none | | | lost owner |
| `toplevel_if_block` | `stop()` | module | Expr Call | 2 | 1 | dropped |
| `def_in_if_block` | `stop()` | `h` | Expr Call | 2 | 1 | dropped |
| `no_def_file` | `stop()` | module | Expr Call | 3 | 2 | dropped |
| `price` | `return x`, new `return x + 1` | `keep` | Return | 1 | 1 | rewritten |
| `price_recovery` | the same | `keep` | Return | 1 | 1 | rewritten |
| `span_after_whole`, write 1 | `stop()`, and `UNUSED = 1` by `_whole_drop` | `f` | Expr Call | 2 | 1 | dropped |

`price` and `price_recovery` become rewritten. Each is an admitted edit,
the same kind with new text. No removal is lost in either.

## Findings

1. **The span branch notes a rewrite, so a whole-file rule alone splits
   the door.** `rota/roles/api.py` line 20997 keeps a statement only when
   its line key is in the text. `_drop_note` on `return x` to `return x + 1`
   names `return x`, for a span of the whole function and for a span of one
   line. If only `_whole_lost` adopts the kind count, a seat that meets the
   note on a span can send the same change as a whole file and pass.
   Severity high. CONFIRMED by a `python -c` probe of `_drop_note`. Fix:
   apply the same kind count to `_lost_statements`, or keep both branches
   strict.
2. **The rule cannot say which statement of a kind went.** When the count
   falls from 2 to 1, the rule knows that one statement is gone, not which
   one. The night 46 write that drops `sys.stdout.flush()` has two
   candidates. Severity low. CONFIRMED by the capture: both lines of `echo`
   classify as dropped. Fix: name the shortfall per owner and kind, and
   name the old statements whose line key the text no longer holds.
3. **The same-kind swap is the price.** A swap of `ctx.exit()` for another
   call, or of `return option(...)` for `return None`, opens no note.
   Severity high for the case class of the frame, because the lost
   `return` of s386 broke 37 tests (`rota/roles/api.py` line 21017).
   CONFIRMED by probe `price.py`. Fix: record the price in the frame. Keep
   the Return and Raise kinds on the present line-key rule if the
   Architect wants that case closed.
4. **The developer reds are a test gap, not a rule gap.** The four tests
   that empty `formatting.py` passed before pass 5 only because
   `_whole_drop` returns None when no definition stays
   (`rota/roles/api.py` line 20685). Severity low. CONFIRMED by the capture
   and the source. Fix: change the four tests, not the rule.
5. Outside the points. **The note names a 0-based index as a line.**
   `_lost_sentence` writes `at line {i}` with the list index
   (`rota/roles/api.py` line 21029). The refusal says `ELLIPSIS = chr(8230)`
   is "at line 0", and `return round(...)` "at line 17", which is line 18
   of the file. Severity low. PLAUSIBLE, because
   `tests/rota/test_frame140_commit_beside_note.py` pins the present
   numbers, so the base can be a choice. Fix: write `i + 1`, or name the
   base in the sentence.

## Probes

All probes are in
`C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/f3a8d4c2-cdca-42d3-8f1d-12549648d58a/scratchpad/p283c/`.
None is in the worktree, and `git status` of the worktree is clean.

- `p283_capture.py`: a pytest plugin, loaded with `-p p283_capture`. It
  wraps `api._whole_lost` and writes each named line with its owner, kind
  and counts to `cap.jsonl` (the point 1 runs) and `cap_full.jsonl` (the
  whole files).
- `summ.py`: prints the classes from a capture file.
- `s340.py`: reads `dec_old.py` (ee59f61) and `dec_new.py` (1e9925f), and
  runs `_whole_lost` and the kind count under `version_option`.
- `shapes.py`: the 14 shapes of review 5, through `_whole_drop`,
  `_tail_drop` and `_whole_lost`, then the kind count.
- `price.py`: four shapes on a small `version_option`: a swapped call, a
  `return None`, a drop plus a new call, and a drop alone.
- A `python -c` probe of `_drop_note` on `return x` to `return x + 1`.
- Read-only SQL on `.rota/clickI_night154.db`, tables `turns` and
  `tool_calls`, session `s340`.

Test times: `test_developer.py` 171 s (5 failed, 32 passed).
`test_scene_review.py -k a_right_call_lands_review` 11 s.
`test_scene_large_module.py -k calls_leave_the_scene` 18 s. Whole files:
`test_scene_review.py` 17 s (31 failed, 3 errors),
`test_scene_large_module.py` 14 s (12 failed, 6 errors),
`test_night46_context.py` 19 s (1 failed, 53 passed).

## Usage

About 95k tokens in total, above the cap of 60k in the brief. This agent
cannot see the split between input and output. Output is about 15k of the
total.
