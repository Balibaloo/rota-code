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
