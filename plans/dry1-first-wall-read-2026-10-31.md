# dry1: the first wall, read before a fix (2026-10-31)

## Result

1. Reconcile is not a loop. The predicate wakes one session for each prose file, clickI has 39, and the dry run cap is 40 steps.
2. Constraint zero is quarantined because the predicate wants every area, and the refresh binds only areas that hold symbols (reasoned, not replayed).
3. The page m3 is empty. The Liaison sent `msg.present_principal(refs=[])`, and the tool accepted it. The renderer drops nothing.

Numbering: the brief counts 40 steps. The db holds 37 sessions (s1 to s37) and 3 scheduler steps. Brief session 8 = s5, 9 = s6, 20 = s17, 40 = s37.

## 1. The reconcile phase

- Code: `reconcile` (rota/core/predicates.py:1936) calls `_reconcile_wakes` (rota/core/scheduler.py:764). It gives one wake for each area of `prose_areas`: `@prose` and each `docs/*.md|rst|txt`. An area leaves the list when a `survey_records` row has its area name.
- The predicate holds again after each session because each session closes only its own file. The next file is still open. On the copy, `tick_reconcile` now returns the 6 files from `unicode-support.md` to `wincmd.md`. That matches the agenda's `n=6`.
- s5 (README): 36 calls. It read README.md in 400-character pages, then read 0 to 12000 three times. It wrote no row and no receipt.
- s6 (README again): 690 calls, 671 of them `code.source`, 217 s. It wrote `@prose` (found) and one ledger row.
- s17 (docs/contributing.md): 17 calls. It logged 4 `conflict` calls about the 4 items, then attested `none_found`. The receipts show only the survey row, so the conflicts did not land.
- s37 (docs/testing.md): 18 calls. It attested `found` twice. The row reads `none_found`.
- Quality: 28 of the 33 doc surveys are `none_found`. s29 logged 4 conflicts that say "the code shows the same". s34 logged 4 rows whose text is the brief's own words, "the README is stale; the code has a bug".
- Reach: nights 170 to 175 ran 40, 40, 39, 39, 39, 39 `tick:reconcile` sessions. The nights have no 40-step cap, so they pass the phase. 7 of 7 runs carry the shape. The cap is `max_steps=40` in `loop.run` (rota/core/loop.py).
- Frame: grep found no `reconcile` in a heading of plans/stack.md or plans/archive/stack-2026-10-*.md. Frame 204, from the brief, rebuilt this half of A5.

## 2. The constraint zero quarantine

- No session ran. The tick is a scheduler step, key `-|tick:constraint_zero|`, row (3, 1, 1). The db keeps no refusal text for it.
- Code: the predicate (predicates.py:1880) sets `want` to every area of `code_index` without a survey. `refresh_constraint_zero` (rota/onboarding/boot.py:224) binds only areas with `grain_kind = 'symbol'`.
- An area with no symbols makes `want` larger than `bound`. The refresh cannot close that gap. So the same step fires 3 times and is quarantined. The empty key agrees: the refs are `bound - want`, and they are empty when `want` holds more.
- The ticks ran before the Architect's `tick:frame`. The Architect's survey cites top-level grains such as `devcontainer` and `github`, which hold no Python. After the frame, `.` and `src/click` both hold symbols, and the predicate is quiet on the copy. The pre-frame partition is reasoned, not measured.
- Reach: all 6 nights 170 to 175 hold the same row (3, 1, 1). rota/testkit/scenes.py says the same for nights 119 to 121: "the step that wrote it was not found". 7 of 7 runs, plus 3 older nights.

## 3. The empty page m3

- Row m3: liaison to principal, `present`, `body_refs = []`, `body_text = NULL`, open. The build session answered it with m5: "The page shows me no lines."
- s2 woke on `tick:quarantined` with `wake_refs = []`. Its first turn said: "I do not have access to the `refs`". Its only call was `msg.present_principal(refs=[], round_no=0)`, and the tool accepted it.
- `render_page(conn, 'present', [], None, ask_id='m3')` on the copy returns the header and the reply line, with an empty order. `_page_body` (rota/roles/principal.py:2661) numbers lines only from refs. The page is empty. The renderer drops nothing.
- Reach: the empty page occurs in dry1 only. The cause occurs in all 6 nights. Each night's s1 woke on the same quarantine, called `present_principal(refs=['tick: quarantined'])` 3 times, and got refused 3 times. Nights 173 and 175 repeat this at s84 for a Critic quarantine. The scheduler already has words for the key: `"constraint_zero": "the team could not read the code first"` (principal.py:2167).

## The fix line for each

1. Reconcile: one wake reads a group of prose files that fits the context. 39 sessions become about 8. Reach 7 of 7 runs. 2 cycles. Raising the dry run cap only moves the wall.
2. Constraint zero: the predicate and the refresh use one definition of "an area with code" (the `symbol` filter in both). Confirm first with one onboarding replay of clickI at 2c8cd3a that reads the areas before the frame. Reach 7 of 7 runs. 1 cycle.
3. Empty page: `msg.present_principal` refuses an empty refs list, and the quarantine wake carries the tick key as a ref that the page renders with the `_gave_up_words` text. Reach: 1 empty page and 7 of 7 runs with a refused or empty quarantine report. 1 to 2 cycles.

## Usage

About 65k tokens, 22 tool calls. Read only. The db copies are in the scratchpad. This file is the only edit.
