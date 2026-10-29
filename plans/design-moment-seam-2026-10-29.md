# The design moment on the rulings seam, 2026-10-29

A design read on the worktree at 7df90d09 (2026-10-29 02:00), before the
decision of that moment. No code changed. The cause is
`plans/seam-general-solution-2026-10-29.md` sections 1 and 2, and the
provenance `plans/w14-faulted-approve-read-2026-10-29.md` and
`plans/paths-nights170-173.md` section 5.2.

## The result first

Recommend shape R: code offers each page line a menu of the readings its
row kind can take, the seat chooses one option per clause of his reply, and
code fills the span, the kind and the target from the choice. The seat's
job shrinks from five free fields per line to one choice per clause. Run
shape S1 (the cause read's own candidate) and S0 on Gemma against it.

## What is implemented, in four facts

1. One wake per page, one call. `rulings_rule` (`rota/roles/api.py` 14042)
   takes a map of line number to a verdict word or an object with
   `verdict`, `act`, `target_kind`, `target`, `words`, or an `ask`
   sentence (observed: the signature and `landing.md` lines 11 to 20). The
   payload (`rota/core/runner.py` 2409 to 2530) holds the page as he saw
   it, `line_rows` with a `table` label per row, and `read_back` rows. The
   ruling lands after the session through `apply_rulings` and `land`, and
   the next page shows it as a read-back line (observed: runner 6607).
2. The row kind already decides what an act can do. `drop` retires only
   through `_dropped_line` on a criterion or test row, `exclude` is read by
   `disputed_paths` on the touch line, `add` lands on the item (observed:
   W14 section 1.3, `RULED_ACTS` `principal.py` 1019). An act on the wrong
   row kind does nothing and can cancel an older `drop` (observed: W14 1.1).
3. The doors re-read his words with regex readers: `_cue_clauses` 13348,
   `_faulted_approve` 13471, `_unnamed_contest` 13564, the read-back check
   at 14344. On the nights they refused right calls 24 of 74 times
   (observed: paths 5.2).
4. The 24 cases: replies of 26 to 94 words, median 52. Pages of 2 to 68
   lines, median 6. 256 expected line rulings, 131 not approve. Every
   reply names lines by number, and four use an ordinal or "the rest"
   (observed: a probe over `l3_rulings.yaml`, and the 24 replies).

## The axes

Who binds his words to lines (code, the seat, or he does through a form).
Wakes per page (one call, one per clause, one per line). What the seat
answers (five fields, one word, a quote, a choice). Where the act kinds
come from (his verb, or the row kind of fact 2). What the page asks him,
whether a wrong reading is cheap to correct, and what his attention pays.

## The candidate shapes

### S0. Today's shape, the prompt edited, and a Gemma trial

No structure change. `landing.md` is trimmed, and gemma takes the seat.
Cost: one pass per prompt edit, one model run. Costs him nothing. Failure:
the 44 refusals of right readings and the "or leave the act out" exits
stay for any model (observed: the cause read, section 1). Measure: the 24
cases as they stand. Reach 1 to 3 on qwen3:8b (observed: W14 moved 0 to
1), Gemma unknown. The control.

### S1. Code binds, the seat gives one word per line (the cause read's d)

The payload carries, per line, the clause of his words that names it. The
seat answers one word per line, and code fills span and kind. Reuses
`_cue_clauses`, `_words_from`, the object form. Cost: one frame. Costs him
nothing. Failure: the binder is a regex, wrong on "the second line" and on
a clause that names two lines ("Line 7 is slightly off, because I approved
lines 1 and 4"). An `exclude` still needs a path from free text. Measure:
the 24 cases, unchanged. About 17 of 24 (reasoned: the cause read, 3d).

### R. A menu per line from the row kind, one choice per clause

The payload carries the clauses of his reply (from `_cue_clauses`), the
lines each one names, and for each line a menu that its row kind allows.
A criterion offers `approve`, `drop`, `rewrite`, `keep`. The touch line
offers `approve`, `exclude <path>` for each path it shows, `rewrite`. The
read-back line offers `ok`, `misread`, `misread, drop`, `slightly off`.
The request line offers `approve`, `add <quote>`. Every line offers
`other <quote>`, and the call offers `ask`. The seat answers one option
per clause, corrects the lines when the binder is wrong, and gives one
option for the lines no clause names ("the rest is fine" is `approve`).
Code writes the same `ruled_refs` rows as today: the span is the clause,
the kind and the target come from the option. Reuses the `table` label of
`line_rows`, `_shown_prediction` for the paths, `_cue_clauses`, `land`,
`apply_rulings`, every mechanical reader of fact 2. Removes the five-field
object, the `acts` form, the act name doors, the span door, and the four
reading doors (appendix D). The fact doors become list checks. Cost: two
frames. One for the menu builder and the call shape, one to re-record the
24 L3 and 12 L1 cases and retire the reading doors. Costs him nothing per
page. Failure: a menu that lacks his reading, met by `other <quote>` and
`ask`. A 68-line page carries 68 menus, met by one menu per row kind with
its lines listed under it (reasoned). The seat's own misreads stay:
"Removing lines 7 and 8 is right" and "not one" (observed: cause read,
section 2). Measure: the 24 cases, with the case runner taught the new
call, and the expected rows unchanged. Reach by construction: the act can
never be left out, named wrong, or put on a kind it cannot move
(reasoned: the menu holds only what fact 2 reads). About 20 of 24
(reasoned: S1's 17, plus the three cases that need a path or an ordinal).

### S3. One wake per line

The runner wakes the seat once per page line with the whole reply, the
page, and that line's menu from R. Cost: two frames, plus a ruling built
over many sessions, against the one-ruling law (observed: the docstring
of `rulings_rule`). Costs him nothing. Failure: 68 wakes on a 68-line
page, and the lines of one clause read apart, so "remove lines 7 and 8
and finish with line 2 alone" can land drop on 7 and keep on 8
(reasoned). Measure: the 24 cases. Reach near R on short pages (assumed).

### S4. The page asks a form

The page ends with the answer form: "ok", or per line "N: drop",
"N: rewrite <words>", "N: exclude <file>", and free words after. Code
reads the form, and only the free words go to the seat. Cost: one frame.
Costs him attention on every page. The docstring of `rulings_rule`
promises "no parser reads the words" (observed), and whether a ruling of
his forbids a form is not in the records this read saw (assumed).
Failure: he writes free words anyway. Measure: not on the 24, his replies
predate the form. It alone moves the ceiling, it removes the reading.

### S5. The acts wait for his read-back

The verdicts land at once, and an act with mechanics (`drop` retires,
`exclude` strips a path, a contest cancels work) waits until he approves
the read-back line of the next page. Reuses the read-back line and
`grant`. Cost: one frame in `principal.py`. Costs him one page turn of
delay per act. Failure: a page that never comes back holds the act open.
Measure: not on the 24, downstream of the reading. A wrong reading
becomes cheap, not rare, and S5 pairs with any shape above (reasoned).

## The recommendation

R, with S5 as the companion once R's measure is on record.

- The smallest job: a choice from a list, per clause. The field the 8B
  seat leaves out most is the act (observed: 241 landed rulings without
  an act). A menu cannot leave the act out.
- Meaning stays with the seat (ruled: 2026-10-28). Code offers facts, the
  clause and the menu, and reads no polarity.
- The act kinds come from the row kind, where the mechanics already read
  them (fact 2). Today they come from his verb, and his "remove" on a
  criterion lands a row that nothing reads (observed: W14, 12 of 15).
- Fewer doors: the four reading doors and the span door go (ruled: "less
  doors and more in depth test cases"). His attention cost is unchanged.

Run against R on the 24 cases: S1, one frame, to isolate the menu (if S1
reads 17 and R reads 20, the menu earned three cases), and S0 on Gemma,
to isolate the model. Commit to R when it holds on two full records.

## What the scope excluded

Each shape here changes a law or a page form the code holds, so a read
bounded by the code could not produce it:

- R's menu: the act list comes from the row kind, a new payload field, not
  from any reader of his words that exists. R's one choice per clause: the
  seat answers in units of his reply, not of the page map.
- S3: a ruling built across wakes, against "one ruling per session".
- S4: a change to what the page asks him, outside the seat and the doors.
- S5: a change to when an act fires, in `principal.py`, outside the seam.
  No record in scope treated the read-back line as the safety net.
