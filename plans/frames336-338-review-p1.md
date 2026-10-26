# Frames 336, 337 and 338, review of pass 1

Date: 2026-10-26 19:57. The worktree is C:/Users/roman/rota_r336, detached at 7121f613 on the base 07c34293. The commits are 3380cebf and 04fd2bfa (frame 336), 6876a7e5 (frame 338) and 7121f613 (frame 337). The review is read-only. No model call and no replay case ran.

## (a) The verdict

- Frame 336: **Stands, because `_failure_line` returns the error on a collection red and the first line on every other red, and the strip removes one period only.**
- Frame 338: **Stands, because the split drops an approved test row, keeps a contested or revised one, and keeps frame 213's route with no verdict.**
- Frame 337: **Held, because an earlier answer that says a line is fine now lets a contest of that line land against his word (finding 1).**

## (b) Findings

1. `rota/roles/api.py:12173`, the `unnamed` set in `_unnamed_contest`. Severity high. CONFIRMED. The door now subtracts every line that an earlier answer names, and it does not read what the earlier answer says about the line. The reversal guard at `rota/roles/api.py:11794` reads `matched` from the last reply only. Probe `test_x_earlier_approve_admits_contest`: the earlier answer "Line 5 is fine. What is the ticket on line 6?", the reply M78 and the map S193 with `5: contest`. The contest of line 5 lands. Probe `test_x_last_reply_approve_refuses_contest`: the same contest with "Line 5 is fine." in the last reply is refused with "The words say line 5 matches what the principal asked for". On 07c34293 the earlier-answer case is refused by the naming door, so the commit opens a law 6 path. The outcome is the mirror of night 168: a ruling against his own word. Fix: read the earlier texts with the match reader too, and add the lines they call fine to `matched` before the reversal check, or keep those lines out of `earlier_lines`.
2. `rota/roles/principal.py:524`, the first-line path of `_failure_line`. Severity low. CONFIRMED. An assertion red whose first `E` line ends with a period keeps the period, and `check_line` adds a second one. Probe `test_p1_one_e_line`: "E   AssertionError: boom." returns "AssertionError: boom.", so the page reads "Fails: AssertionError: boom..". The commit says the first-line case does not change, so this is outside the frame's scope. Fix: apply `removesuffix(".")` to both returns.
3. `tests/rota/test_frame338_test_row_relay.py:62-68`, the fixture of night 168. Severity low. CONFIRMED. The docstring says the rows copy m47 and m49. In `.rota/clickI_night168.db`, m47 holds `batch_1`, the item and three criteria, and m49 holds the three test rows only, with a verdict map of test rows only. The fixture puts six rows on both and adds three criterion approves. Probe `test_p3_night_shape` seeds the night's shape and gets the same relay, crit_1 and crit_2, keyed `criterion_repair`. The test result holds, but the claim "copies the rows" is not exact. Fix: seed m47 and m49 with the night's refs, or reword the docstring.
4. `rota/core/sandbox.py:4496-4500`, the off-park filter. Severity med. CONFIRMED, outside this frame's change. An approved item row on a page that is not a park page goes to the Vision Keeper as a relay, on 07c34293 and on 7121f613. Probe `test_p4_item_row_on_page`: the relay gives `terminologist ["crit_1", "crit_2"]` and `vision_keeper ["version_option_show_python"]`. The park branch at line 4491 drops every approved row. The off-park filter drops an approved criterion only, by the scope of frame 190's design, 2.F, amendment 1. The comment at lines 4477-4485 calls the same item relay a fault on the park page (the delta review of 4ef3bd9f, finding 2). Fix: off the park page, drop every ref of a page line that the verdict does not contest or revise, as the park branch does.

## (c) The points

1. Holds. The probes give the assertion line, the SyntaxError line, the ModuleNotFoundError line and the single line. A single frame line returns itself.
2. Holds. "wait.." becomes "wait." and "A raw string is also an option." loses one period. The first-line path strips nothing (finding 2).
3. Holds. A contested test row sends crit_1, an approved one sends nothing, and the night's shape keys `criterion_repair`. With no verdict, `ruled` is None and the new guard does not run. A converse wake has no relay call, so the probe proves the no-verdict route by the code only.
4. The approved item goes to the Vision Keeper on HEAD and after, by the off-park filter of frame 190's design, amendment 1. Frame 213 rules test rows only. The outcome is a pre-existing fault and not this frame's (finding 4).
5. Holds. Probe `test_p5_scope` adds a Liaison converse, a Critic converse, a principal converse on another page and a principal verdict on the page. `_earlier_lines` returns `{5}`, from the principal converse of the page only.
6. Holds. The single reply gives the exact text of 07c34293. The refusal after an earlier answer adds "His earlier answers to this page do not name line 5 either."
7. Q1, no seq bound: agree, keep it, low, because the door then reads what the seat reads. Q2, a reply that names no line: agree, wait for a night, low. Q3, an approve of a faulted line still lands: med, and finding 1 is the same gap in the other direction, so fix both in one pass. Q4, no batch lift on earlier answers: agree, keep it, low.
8. No CR byte in any diff or changed file. No print and no bare except. No other helper reads the principal rows of a page. The frame numbers in the comments and docstrings are correct. The citation of DECISIONS 1473 matches its text. The three changed test files pass, 32 of 32.

Probes: `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/ac089aa1-c627-4128-af45-c49f490f4a93/scratchpad/r336probe/test_probe_r336.py` (points 1, 2, 5, 6 and finding 1, 15 tests) and `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/ac089aa1-c627-4128-af45-c49f490f4a93/scratchpad/r336probe/test_probe_r338.py` (points 3 and 4, 6 tests). Both ran with pytest from the worktree root, and `rota.__file__` pointed into rota_r336. A read-only query of `.rota/clickI_night168.db` read m47, m49, m50 and m74 to m80.

## (d) Usage

The harness counter went from 15,000,000 to about 14,929,000 tokens left, so the review used about 71k tokens in all. The harness shows no split between input and output tokens. The output is about 15k by estimate. No sub-agent ran.
