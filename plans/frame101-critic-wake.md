# Frame 101: the Critic's wake keeps the criteria and the batch's own tests

Design record. Written by d2cc277a on 2026-10-01 after the design read of
`rota/core/runner.py` (`_fit`, `_render_cut`, the pushed working set) and
`rota/roles/api.py` (`tests_load`). Rota workflow for the facts, meta
workflow for the build.

## The two cuts

1. The window's cut. `_fit` keeps the wake to two thirds of the budget and
   `_render_cut` keeps the front, `text[:limit]`. The pushed reads render
   in `sb.functions()` order: `code.read`, `criteria.load`, `tests.load`.
   A long diff fills the front, and the criteria and tests fall off the
   end (observed: frame 97's review of `ff0f692`, probe p3, 2026-09-30).
2. The result cap. `tests.load` returns every `tests` row of the batch with
   its whole body, in insertion order. On night 101 `bg_1` held 34
   inherited tests, 460,000 characters, before its own three, 2,716
   characters. The push renders through `PUSH_CHARS`, 20,000, so the
   batch's own tests were behind the cut: `CUT the result: 448,106 of
   468,106 characters are not shown` (observed: night 103, s170,
   `plans/night103-read.md`).

## The design

- `tests_load` orders the batch's own tests first, the rows whose
  `criterion_id` is set, then the inherited rows. An inherited row whose
  last result is `pass` or has no run carries no `body`: the key reads
  `body: <n> characters, passing, not shown; the file is at <path>`. A red
  inherited row keeps its body, because the Developer reads it in
  `tests_failing`. The op's signature does not change, so no tool line
  moves (frame 103's shape).
- The pushed working set renders `code.read` last. After the push loop
  builds `pushed`, the key `code.read` moves to the end when present. The
  criteria and the tests then sit in the front the cut keeps.
- One runner test per cut: a pushed wake with a diff longer than the
  wake's room renders `[criteria.load]` and `[tests.load]` before
  `[code.read]`, and both survive `_render_cut` at the room; `tests_load`
  on a fixture with thirty large green inherited rows and one own row
  returns the own row first and no inherited body.
- The Critic's cases re-record by count, because the pushed prompt moves.

## What the night proves

A seam night from night 101's pair, `GAUNTLET_SEAM_DB=.rota/clickI_night101.db`
and `GAUNTLET_SEAM_COMMIT=e1f99723`: the Critic's first prompt holds the
three `echo_json` test rows and no cut on `tests.load`.
