# P4 — modification-scope disclosure (ruled R16/R17, design for the build)

The ruling (2026-09-03): time and effort are never considerations; the
principal needs the **modification scope** presented as a sense check —
**both** coarse (beside the items at signoff) and grounded (before a batch
builds). Non-blocking by R7: nothing waits on the principal's reaction; the
steering loop (cancel/preempt, already pinned) is the lever if the scope
smells wrong. A blocking variant, if ever wanted, is a config setting in the
`merge_gate` mould — trust should not change on a schedule.

## Piece 1 — grounded: the batch's touch set, shown before it builds

Nearly all machinery exists: `annotate` (architect, per batch, from source)
already writes `batch_touch` — paths always, symbols where confident,
prediction-never-permission. Missing: the presentation.

- **New predicate `touch_note`** (register-shaped: owed until presented):
  a batch with touch rows, not yet running, whose touch was never presented
  → wakes Liaison with the batch ref. Drains when the present lands.
- **Liaison mode `touch_note`**: present the batch's item, its expected
  paths, its `possible` rows flagged as guesses, and — the sense-check
  heart — any touched area that is **unsurveyed** (constraint-zero
  intersection) or bound to a **commitment** (constraint bindings). Refs:
  batch + item, mechanical (added-never-substituted, per the S1 rule).
- **The jam to avoid, named:** `tick_signoff` refuses to submit while any
  message with verb `submit`/`present` is open — so a touch present left
  unanswered would freeze future signoffs. The fix is to scope that guard
  to presents in the signoff's own cause-chain (its reason for existing is
  "don't double-submit an interpretation", not "no presents of any kind").
  This scoping must land WITH piece 1, or piece 1 jams the gate.
- `batch_start` does not wait on the presentation (R7). Frontier ordering
  already offers `annotate` before `batch_start` within the band.

### Piece 1 as built (2026-09-03)

- `touch_note` (predicates.py, register entry, band start, declared between
  `annotate` and `batch_start` so the file order offers it first) wakes
  Liaison with `(batch, item)`; presented is derived from the presents
  themselves. It fires for pending, deferred **and running** batches: the
  levers act on a running batch, so a note that lost its turn is still owed.
- `lifecycle.touch_set` computes the four parts; `resolve_inbound` pushes it
  as `touch`; `principal.touch_words` renders a batch ref inside
  `render_refs`, so the words reach the seat at the edge, Law 2 intact. The
  present's refs are added-never-substituted from the wake.
- The jam: rather than cause-chain scoping, `lifecycle.touch_notes` (a
  present carrying a batch ref -- derived, no flag) is set aside by
  `tick_signoff`, `tick_agenda` and `observed_entries` (both its `asked`
  guard and its limbo scan). Cause-chain scoping alone would have let
  signoff double-present observed items sitting in an open baseline present.
- The door: `principal.land` drops batch refs from a ruling; an all-approve
  answer to a note returns None (answered, no verdict message, nobody woken);
  a contest on the item lands as any ruling does.
- Pinned in `tests/rota/test_touch_note.py`; `test_delivery.py`'s dispatch
  test now steps through the note first. Case `L1-LI-present-the-touch`
  authored in `l1_liaison2.yaml`.

## Piece 2 — coarse: the Architect's guess beside the items at signoff

Harder, because at signoff nothing is sliced: the guess is model judgment
at the 8B tier and needs its own measurement.

- **Where the judgment runs:** the Architect's structure-read of ratified
  statements (deliver mode) — the designed moment where it already reads
  the same words against the model. One added duty: per statement, name the
  areas/commitments building it would plausibly touch.
- **Row home — a real decision, the ledger is wrong for it:** a ledger
  entry can only close by a decision naming it (law 11's note), so touch
  guesses would sit open forever and pollute quiescence. A new table
  (`touch_guesses`: statement_id, grains) needs the full ceremony — law 14
  identity (key: statement_id + grain), a graph writes-edge, sandbox op,
  push into the signoff present via `item_statements`, brief, case.
- **Feasibility unknown:** kin to the survey counterfactual (the system's
  best-performing judgment) but run before any code exists for the
  statement. Must be measured before it is trusted — a case with a
  preregistered expectation, runs on both models.

## Build order

1. Piece 1 with the signoff-guard scoping, one case
   (`L1-LI-present-the-touch`), re-record.
2. Piece 2 as its own measured change; if the 8B guess proves hollow, the
   honest fallback is mechanical only — `code.probe` hits for the
   statement's terms, labelled as hits, never as judgment.
