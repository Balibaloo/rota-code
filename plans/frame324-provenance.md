# Frame 324, the provenance: the surface door takes the first index symbol, and the Architect's bare symbol is refused with no way to choose

Provenance read, 2026-10-25, at HEAD 20d7e773. Databases night 150 to night 165, `?mode=ro`. No file but this one changed.

## The verdict

**The criterion door resolves a bare name to the first row of an
unordered scan, and the scan follows the indexer's sorted walk, so
`examples/` comes before `src/`. The project model already ranks the two:
the frame rulings of night 165 say `examples` is "attached" and `src` is
"program". Neither door reads them. No ruling of Roman's says what a
surface may name. The wall is a design departure, not a model fault.**

Two corrections to night 165's read. s214 sent `surface_refs=['clear']`,
and the door wrote `examples/termui/termui.py::clear` (observed:
`tool_calls` s214 seq 9 to 11). Six Architects sent the bare `clear`, s199
to s201 and s206 to s208. s330 guessed another item (observed).

## 1. The mechanism today

`criteria_specify`, api.py 5635 to 5819, calls
`_surface_names_what_the_item_names` at 5803 and `_vet_surface` at 5804.

- `_vet_surface`, api.py 5218 to 5306, runs
  `SELECT grain FROM code_index WHERE grain_kind='symbol' AND (grain = ? OR grain LIKE ?)`
  with `(ref, f"%::{ref}")` and takes `.fetchone()` (observed: 5246 to
  5248). The query has no `ORDER BY`. The plan is `SCAN code_index`, so
  the first row is the lowest rowid (observed: `EXPLAIN QUERY PLAN`,
  night 165). `examples/termui/termui.py::clear` is rowid 152 and
  `src/click/termui.py::clear` is rowid 335 (observed). The door then
  refuses a test path (5254 to 5262) and keeps the first row. A second
  row with the same name is never seen.
- `_surface_names_what_the_item_names`, 5536 to 5606, compares only the
  tail after `::` with the names the item gives. Both paths pass it.
- `code_index` is written by `rota/onboarding/indexer.py`. `walk` returns
  `sorted(root.rglob("*"))` (observed: indexer.py 345), and the refresh
  inserts the path rows and their symbols in that order (observed: 448 to
  461). So the rowid order is the alphabetical path order.

`batches_guess`, api.py 7170 to 7255, refuses any symbol without `::`
(observed: 7211 to 7223). The query is `... grain LIKE ? ORDER BY grain
LIMIT 3`, so the refusal also lists `examples/` first. The text of
night 165, verbatim:

```
clear names no path. A symbol is written path::name. The index holds examples/termui/termui.py::clear, src/click/termui.py::clear. Write the symbol that way, or leave symbols out
```

(observed: `turns` s199 seq 2). To pass, a seat writes
`src/click/termui.py::clear` or drops `symbols`. The seat's own `paths`
already held `src/click/termui.py` in every one of the 18 calls (observed:
`tool_calls`). In four sessions, s200, s201, s207 and s208, the third call
added `examples/termui/termui.py` to `paths`, after the refusal named it
first (observed).

## 2. The origin

- The lookup of `_vet_surface` is commit 395535da, 2026-08-27, "delivery
  hardened three ways": "Criteria carry their surface (vetted at both
  doors ...)" (observed: `git log -S`). DECISIONS.md 1058 records it:
  "vetted at both doors against the symbol index: a near-miss is refused"
  (observed). The design asked "does the name exist", never "which one".
- The test exclusion is cab4e499, 2026-09-09, "a test is not a surface",
  for tipsS (observed). `examples/` was never excluded or ranked at the
  surface door (observed: `grep` of api.py, the stack and its archive).
- The refusal of `batches.guess` is 7ec9b940, 2026-10-18, frame 298
  pass 1, after "the architect owns the guess" (ruled: Roman,
  2026-10-18, cited in the code). The `ORDER BY grain` and "The index
  holds" text came in the same commit, for a bare `line_total` on L1
  (observed: the comment at 7212 to 7214).
- The project model ranks `examples/`: `EXAMPLE_DIRS` and `is_attached` in
  `rota/onboarding/areas.py` 45 to 51 and 76 to 91, from b4d912eb,
  2026-08-24, and the frame's `frame_rulings` table, ca9c1ae9, 2026-08-24,
  "rulings outrank names" (observed).
- The same wall had a narrower fix before. Frame 215, f3de0534,
  2026-10-12, night 142: s536 took `examples/imagepipe/imagepipe.py::
  process_commands` from "the first row of an unhinted callable list".
  The fix, `_surface_outside_batch`, runs at `criteria.respecify` only
  (observed: api.py 5309 to 5376, callers 6618 and 6736).

No ruling of Roman's covers what a surface may name (observed:
DECISIONS.md, LAWS.md, `plans/stack.md`).

## 3. The design's own condition

"**The project** is the codebase the work is about. The structure holds a
model of its shape, terms, boundaries" (ruled: `plans/composition.md` 40
to 42). The frame classifies the tree "program / attached / ignore /
boundary" (observed: ONBOARDING.md 1099 to 1102). An example "exercises
the package the way a test does: authored, indexed, findable, never an
area of its own" (observed: areas.py 45 to 50). The surface is "a
callable a test would exercise" (observed: api.py 5277 to 5278). So a surface is a
`program` grain in the model's own words (reasoned).

Night 165 holds `('examples', 'attached', 'Contains example code')` and
`('src', 'program', 'Source code for the main package')` in
`frame_rulings` (observed). The code departs from the design: both doors
read the index, which "is trusted for existence claims only" (paraphrased:
ONBOARDING.md 1098), and use it to choose.

## 4. The count

Over nights 150 to 165, 16 databases, 152 criteria at their current
version (observed: a script over `criteria`, `tickets`, `items`,
`code_index`, `tool_calls`, `touch_guesses`, `batches`).

| Measure | Count | Where |
|---|---|---|
| Criteria whose surface is under `examples/` or `tests/` while the item names a library symbol | 6 of 152 | all `clear`: night 163 four, night 165 two (c_1, c_3) |
| Of those, from a bare name the door resolved | 6 of 6 | n163 s199, s202; n165 s214 |
| `criteria.specify` or `respecify` calls with a bare name of two index rows | 30 | 28 had `examples/` first |
| Architect sessions with a bare symbol in `batches.guess` | 27 | nights 157 to 165 |
| Of those, repeated the bare symbol after the refusal | 13 | 7 on an ambiguous name, 6 on a unique name |
| Of the 13, no own guess written and a batch started | 6 | n165 s199 to s208, one key, one batch bg_2 |

The 6 repeats on a unique name all wrote a guess on a later call. Of the 7
on `clear`, n163 s150 qualified on call 3 to `src/click/termui.py::clear`.
The six of night 165 never did, `architect|tick:guess|clear_screen_return_status`
quarantined at 3 attempts, and bg_2 ran with no guess (observed). On
night 163 two `clear` criteria reached `src/` only at version 10 and 11
(observed). No current criterion names a `tests/` path.

## 5. The repair's shape

- **Candidate R, the program rank.** One resolver serves both doors. A
  bare name with several index rows resolves to the one row whose frame
  kind is `program`, through `ruling_for`, with `is_attached` as the
  fallback when no frame exists. At `batches.guess` a row inside the
  seat's own `paths` wins first. Zero or two `program` rows refuse, with
  the rows listed `program` first and the qualified form to copy. A
  qualified path is kept as written. Red tests: c_1 of night 165, bare
  `clear` from s214, must store `src/click/termui.py::clear`; s199 seq 1,
  with `paths` holding `src/click/termui.py`, must write a guess.
- **Candidate Q, refuse every ambiguous name.** Both doors refuse a bare
  name of two rows and list them `program` first. The seat must copy the
  path. Red tests: the same two calls must be refused, `src/` first.
  Night 165 shows six sessions that read a refusal naming both paths and
  never copied one. Q puts the choice on the seat that failed it.

The page favours R. The project model already holds the answer, so the
door reads a fact and the seat makes no choice. R is not fitted to
click: `EXAMPLE_DIRS` and the frame were measured on click and icalendar
and apply to any tree (reasoned: areas.py 45 to 50, ASSUMPTIONS.md 32 to
40). One door serves both ops, through one shared function. The frame's
first end condition asks for the refusal "otherwise". R keeps that
refusal for the case of zero or two `program` rows. A qualified
`examples/` path from a seat, as s426 sent, stays outside R. Frame 215's
repair-only door covers it at `respecify` (reasoned: section 2).

Usage: about 70k on the counter, against a cap of 60k.
