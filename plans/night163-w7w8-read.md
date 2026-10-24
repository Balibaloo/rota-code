# Night 163, W7 and W8: the provenance read

Reader on Opus, read only, 2026-10-24. Data: `.rota/clickI_night163.db`
read-only, `.rota/night163_principal.jsonl`, the night read section 2
rows W7 and W8, the wall guide sections 2 and 4, frame 319 in the stack.

## 0. The two causes

W7 is **cause 9**: the criteria wake fires per item and never names the
ticket that has no criterion, and the twin door tells the seat to write "a
second sentence", so three attempts wrote new cases on the wrong ticket
and the third put an inverted case on the empty one (reasoned: section 1).
W8 is **not a separate wall**: `tests_missing` waits for `head_commit` by
design, and bg_2 never had a commit, which is W1 and frame 283 (observed:
section 2).

## 1. W7, the trail

**The count.** The page m101 held 7 criteria on lines 3 to 9, not 9. The
9 is the count of m101's `body_refs`: 7 criteria, the item and a guess
(observed: `messages` m101, jsonl line 3532). The night read's "9
criteria" is wrong by 2.

**Why two tickets.** s198, Vision Keeper on `tick:slicing`, cut item 3 into
`tk_1_clear_returns_bool` ("returns True when it cleared the screen") and
`tk_2` ("returns False when stdout is not a terminal"), one ticket per
clause (observed: `receipts` s198, `tickets`). The cut follows the item's
two clauses (reasoned).

**Each criterion, by seat, wake and source.** All three seats are the
Terminologist on `tick:criteria`, refs `clear_returns_bool` (observed:
`sessions`).

| Page line | Criterion | Ticket | Seat, turn | From what in the window |
|---|---|---|---|---|
| 4 | c1_clear_terminal_check, "iff the current stdout is a terminal" | tk_1 | s199 t2, attempt 1 | the item, restated |
| 5 | c2_non_terminal_false, "False when stdout is not a terminal" | **tk_1** | s199 t2 | tk_2's own headline, placed on tk_1 |
| 9 | c3_terminal_true, "terminal and the clear succeeds" | tk_1 | s199 t2 | the item, restated |
| 8 | c3_terminal_failure_true, "clear operation fails, provided no exception is raised" | tk_1 | s199 t6 | invented after 4 turns of the exact-twin refusal "it needs a second sentence" |
| 3 | c1_clear_terminal, "True if cleared, False otherwise" | tk_1 | s200 t2, attempt 2 | the item, restated |
| 7 | c3_terminal_check, "the underlying stream object passed to it" | tk_1 | s200 t2 | the glossary row `stream` ("An I/O object") and `raw_terminal` from the pushed callables |
| 6 | c3_no_terminal_true, "True ... even when stdout is not a terminal" | **tk_2** | s202 t1, attempt 3 | none, an inversion of tk_2's headline |

(observed: `receipts` versions 4 to 10, `tool_calls` of s199, s200, s202,
the turns' completions.)

**What each window held.** Every turn pushed the same block: the callables
list, the glossary, the two ticket headlines, and "the item" with "the
principal said" holding s2 only (observed: s202 turn 1 user text). The
statements s3 ("print exactly what it prints today ... the only
difference is the return value") and s4 ("confirm that the output stays the
same") are ratified, but the item's `refs` row names s2 only. So the push
at `rota/core/runner.py` 4262 to 4271 never shows them (observed: `refs`,
`statements`). The fact "the output does not change, only the return
value" was in a record and not in the window.

**Why the wake ran three times.** `tick_criteria` fires per item while any
ticket of the item has no criterion, and its wake carries the item id only
(observed: `rota/core/scheduler.py`, `tick_criteria`). s199 and s200 wrote
every criterion on tk_1, so tk_2 stayed empty and the wake stayed live
(observed: `receipts`). The retry text at `rota/core/runner.py` 756 says
"Do something the earlier attempt did not" and does not name tk_2 (observed:
s200 and s202 turn 1). s200 hit the six cap on tk_1 at turn 4 (observed:
s200's turn 4 refusals). s202, on attempt 3, wrote the first criterion
tk_2 ever had, and the only new sentence left was the inverse (reasoned:
its turn 1 completion).

**Which door admitted line 6.** `criteria_specify` in `rota/roles/api.py`
5610 onward runs the exact twin (about 5730), `_near_twin` (about 6425),
the six cap (about 5754), the surface doors, and
`_exception_from_a_source`. All twin doors compare within one ticket, and
tk_2 held nothing, so all passed (observed: the code). No door compares a
criterion with its ticket headline. A door that judged contradiction would
read a meaning, which the rule of 2026-09-09 forbids (reasoned).

**Frame 319's door.** The door refuses an exception identifier that no
source holds. None of the 7 texts names an exception identifier. Line 8
says "exception" as a common word. The door refuses none of the 7 and lets
all through (reasoned: the texts above against the door's predicate in the
frame 319 record).

**Cause.** Guide section 4. Step 1: no open frame names this mechanism.
Frame 319 is an exception-name door, frame 306 is a page reply to a
criterion, frame 315 is a re-slice. Step 3: the page shows criteria his
words never held, so the hop is the criteria writer. Step 4: the twin door
fired right, and its text and the retry text point the seat to a new
sentence and not to the empty ticket. That is **cause 9**, the refusal's
text, or a runner note, points the seat wrong. **Cause 2** contributes:
s3 and s4 hold the "output unchanged" fact and the criteria wake lacks
them. The night read placed W7 at cause 1. This read takes the seat's
rewrite as the effect and the pointer as the cause.

## 2. W8, the trail

**The predicate.** The Tester wakes on `tick:tests_missing`, not
`tick:tests`. `tests_missing` in `rota/core/predicates.py` about 810 to 845
selects criteria of a running batch with no test of that batch. It fires
only when `b.head_commit IS NOT NULL AND b.head_commit != ''` (observed:
the code). The docstring states the design: the Tester waits for the
Developer's commit, and "`batch_start` needs no tests, so nothing
deadlocks" (observed: the docstring, measured 2026-09-04).

**What bg_1 had and bg_2 lacked.** On bg_1, s121, Developer on
`batch_start`, wrote `head_commit` (receipt v2), and s122 woke on
`tests_missing` and wrote 2 tests (observed: `receipts`, `tests`). On bg_2,
`head_commit` is NULL at the night's end (observed: `batches`). Its 34 test
rows are all `inh_` rows, the repository's own tests, with `criterion_id`
NULL (observed: `tests`).

**When the batch formed.** s211, Architect on `tick:grouping`, opened bg_2
with both tickets, after s202 gave tk_2 a criterion (observed: `receipts`
v5 to v7). 18 Developer sessions, s220 to s261, woke on `batch_start` for
bg_2. Their commit calls never landed a commit (observed: `tool_calls`,
and W1's row: 40 commit calls, 0 landed).

**By design or a gap.** By design. The Developers of bg_2 started with no
tests because no Developer starts with tests. The Tester never woke
because no commit landed. "check: none yet" on every page line is true.
The sign is W1's, read at a second place (reasoned: the predicate and the
rows).

**Cause.** Guide section 4, step 1: the sign is an open frame's sign. W1 is
cause 8 and cause 9 at the note door, frame 283. No new frame.

## 3. The candidate frames

**W7, a new frame.** "The criteria wake names the item and not the ticket
that has no criterion, and the twin refusal says to write a second
sentence, so three attempts wrote invented cases and the third inverted
the empty ticket's headline."

- Site: `tick_criteria` in `rota/core/scheduler.py`, the retry line at
  `rota/core/runner.py` 756, the exact-twin text at `rota/roles/api.py`
  5743 to 5745, and the item push at `runner.py` 4262 to 4271.
- Ends when: first, the mechanism: the criteria wake names each ticket
  with no criterion and its headline, the twin refusal names that ticket
  in place of "a second sentence", and the item push shows every ratified
  statement of the item's entries; second, on a night, criteria that a
  page reply calls wrong or unclear, from 3 of 7 on item 3 toward 0 over
  the next 3 nights; third, 0 refusals of a right criterion on the
  recorded criteria cases.
- Red test: s199's state after its turn 2, tk_1 with three criteria and
  tk_2 with none. The wake must name `tk_2` and its headline. The
  exact-twin refusal of c2_non_terminal_false must name `tk_2`.
- Rule check: each change names a row state, not a meaning. A stronger
  model is refused nothing (reasoned: the rule of 2026-09-09).

**W7 and frame 319.** Frame 319 does not cover W7. Its ends-when gains
nothing from W7, because none of the 7 names an exception (reasoned:
section 1).

**W8.** Frame 283 (W1) covers W8. Frame 283's second clause, on a night,
gains one sign: a running batch with no `head_commit` after its
`batch_start` sessions, read beside 0 `tests_missing` wakes.

## 4. What to doubt

1. The statement link. Why the item's `refs` row names s2 and not s3 or s4
   is not read. s3 and s4 came from entries e_m65 and e_m84 after the item,
   and no amend linked them. That hop may be frame 306's or frame 315's
   and not this frame's (reasoned).
2. s202's completion holds no reasoning. The inversion may come from the
   retry text alone, without the empty ticket (reasoned).
3. `rota/core/boot.py` 163 writes `head_commit` from the worktree's HEAD
   when the two differ. Why bg_2's NULL survived is not read (observed:
   the code; reasoned: no boot may have run after s211).
4. Frame 319's door was not on the branch on night 163. Its verdict here
   is by its predicate, not by a replay (reasoned).

## Usage

One reader on Opus, no model run, no sub-agent. About 80k tokens in and
9k out, estimated.
