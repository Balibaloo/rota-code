# Design of the refs relation (frame 21)

Rota workflow. Written 2026-09-16 by session 32a42b78 (peer rota-b9) from
`plans/archive/refs-scope-2026-09-16.md`. The ruling (ruled 2026-09-16,
Roman): `decided` originates in a ratified statement and cascades along
the refs to the rows that cite it, and the cascade is a relation in the
SQL. Everything below the ruling is design (reasoned: the assistant's
answers to the scope report's questions; Roman can overrule any line).

## Answers to the scope report's questions

- Q1. A `grain` kind carries the code half of `observed` (reasoned: the
  page says observed covers the code and the world; the frame's wording
  named the world half only; without a code target every onboarding row
  derives as `reasoned` and slicing regresses). The wake kind decides
  which refs a write records. It travels as `ctx.onboarding`.
- Q2. Precedence: `decided` over `observed` over `reasoned`. The view
  returns `basis` too, so a reader keeps the world and the code apart.
- Q3. `frame_rulings.provenance` folds in. The judge writes a `grain`
  ref per prefix. A principal's ruling on a prefix writes a `ruling` ref.
- Q4. `cited` becomes `observed` with `basis = 'world'`. `observed_entries`
  drains `basis = 'code'` only, so today's behaviour holds.
- Q5. The `ratified` value of `model_areas` goes with the column.
- Q6. `item_statements` folds in as `kind = 'statement'`.
- Q7. One table. `ARTEFACT_OF_TABLE`, receipts, `cascade_wakes`,
  `RULED_TABLES` and `graph.check_writers` resolve a `refs` row by its
  `src_table`. The `Write` for a refs row carries `src_table` in `values`.
- Q8. A `ruling` ref targets `rulings.id` with `status = 'landed'`. Where a
  principal's verdict lands with no `rulings` row today, `land()` writes
  one. `_adopt_rows` writes the ref instead of the stamp.
- Q9. The fixture loader translates `provenance:`, `source_refs:`,
  `term_refs:` and `item_statements:` seeds into refs rows. Case files do
  not change. Rendered prompts stay byte-identical.
- Q10. Every op parameter name and result key stays. A parameter writes
  refs rows. A result reads the view.
- Q11. `glossary.amend` and `problem.assert` gain a `source_refs`
  parameter that writes `reference` refs.
- Q12. Frame 20's two brief lines (`terminologist/base.md:13-14`, `:36`)
  land in stage 4 with the three words of `rota/LAWS.md:279-285`.

## Stage 1 deviations (observed: the agent's report, commit ac1b83e)

- Q11 is parked, not in this frame. An op's signature is in the prompt,
  so a new parameter re-keys every Vision Keeper and Terminologist case
  (reasoned: outside the ends-when; land it with the next brief change
  to those roles, when their cases re-record anyway).
- `refs.src_table` and `refs.kind` carry no CHECK. The vocabulary lint
  reads every CHECK value as a state word. `api.stage_ref` refuses any
  other value. Stage 3 decides whether the CHECK lands with a lint exemption.
- `glossary.same` leaves the old `term` ref beside the repointed one.
  Stage 3 adds the delete door: a dropped row's refs go with it.
- `_adopt_rows` writes the ruling ref only when a landed `rulings` row
  exists on the cause chain. Stage 3 rules that adopt without one refuses.
- Two fixtures in `l1_liaison2.yaml` put statement ids in `source_refs`.
  The view says `decided` where the column says `observed`. Stage 2
  accepts the view and lists the cases that go STALE from it.
- `check_predicates_can_fire` flags a predicate that reads a view.
  Stage 2 adds a rule for views.
- In stage 2 a result renders `cited` for `basis = 'world'`, today's word,
  so prompts stay the same. Stage 4 decides the rendered word.

## Stage 1 review (observed: the reviewer's report on ac1b83e, probes in the session scratchpad)

The view agrees with the columns on every row of a copy of `clickI_n42.db`
(82 refs rows, 0 rows differ). A point lookup builds the whole view and
takes under 1 ms at that size. A cycle terminates. Fixes, in one brief
after stage 2 lands (reasoned: the fixes and stage 2 edit the same files):

1. `land()` writes a second landed `rulings` row when the Liaison's own
   row is open on the same ask (`principal.py:746-751`, `:779-784`).
   Fix: land the open Liaison row, and create `r_<msg>` only when no row
   exists for the ask.
2. The fixture ask `m_fixture_ruling` is `answered` with no answer, so
   `rota/tools/audit.py:143-147` flags every seeded database with a
   `decided` row. Fix: seed a record the audit accepts and no prompt,
   wake or predicate reads. The STALE set must stay empty.
3. A duplicate refs row written in a later session bumps the artefact
   counter and receipts the source row for no change (`db.py:279-287`,
   `:436-456`). Fix: a refs write that changes nothing is not a change.
4. A refs write staged before its source row's write bumps the counter
   twice (`db.py:441-450`). Fix: one bump per receipt key per commit.
5. `tests/rota/test_refs.py:298-299` asserts nothing: `"cite"` against
   dotted names. Fix: no offered name ends with `.cite`.
6. The `provenance` view reads `target` unqualified in three correlated
   subqueries (`schema.sql:131-138`). Fix: `reach.target`.
7. `artefact_of_write` (`db.py:97-101`) has no caller. Delete it.
8. The `cite` door (`api.py:511-524`) accepts a target that names no row.
   Fix: the door checks the target per kind, as the owner ops do.

Accepted as designed: `glossary.same` lifts the kept row to `decided`
when the dropped row rested on a ruling (ruled: decided cascades along
the refs). Stage 2 lists any case that goes STALE from it.

## Stage 2 review (observed: the reviewer's report on 948c436, probes in the session scratchpad)

Rendered words match the column for every row that has refs. Two high
findings, both in the writers, land in stage 3a:

1. `glossary.amend` and `model.amend` stage no `statement` ref on a
   delivery wake, so a row written for a ratified statement derives as
   `reasoned` (`api.py:1496-1508`, `:2238-2250`). Fix: both stage a
   `statement` ref for every statement the wake names, as `problem.assert`
   does with `named`. A row the wake ties to no statement is `reasoned`
   (ruled: decided cascades from a ratified statement along the refs).
   Cases whose later turn reads such a row back change prompt and re-record.
2. A run database from before stage 1 opens with an empty `refs` table
   and every gate reads `reasoned`: the guards pass, slicing offers
   observed items, a Tester sees `term_refs: []`. Fix: `init_db` refuses
   a database whose owner tables still carry a `provenance` column, with
   a sentence that says to start a fresh run (reasoned: a silent regression
   on every gate is worse than a refused open; run databases are throwaway).

Medium and low, also stage 3a: cascade wakes collapse to one `refs=()`
wake per owner (fix: `refs=(artefact, *row_ids)`, one wake per artefact
as before); `glossary.same` leaves the old `term` ref (fix: the delete
door, and the repoint replaces); `_adopt_rows` reads the column (fix:
the view, and adopt without a landed ruling refuses); `problem.consult`
orders `from_statements` by target (fix: rowid, the insertion order).

Accepted as designed: constraint zero leaves `observed_entries` once
every area is surveyed and its grain refs are cleared (reasoned: a row
that names no unsurveyed area has nothing to present). Noted, no change:
`cascade_rows` computes rows for `reference` and `ruling` receipts that
no graph edge carries; a real grain under a top-level `@` directory would
be skipped by `challenge.load` as a fixture sigil.

Stage 3 splits (reasoned: 3a changes prompts and lists them; 3b must not):

- 3a. Writer semantics: the six fixes above, and the refs CHECK question.
  Acceptance: FAILED equals the baseline plus the listed STALE cases,
  each with the reason.
- 3b. The drop: the five provenance columns, the five JSON columns,
  `item_statements`, `ctx.provenance`, every old write, the seed helper.
  Acceptance: no new STALE case.

## Stage 3 review (observed: the reviewer's report on b4dc845 and 056995d, probes in the session scratchpad)

Sound: a proposed statement's row flips to `decided` at ratification
with no write; adopt's two cases keep their premise; the loader and
`seed_provenance` agree by construction; ten sampled tests that lost a
`decided` seed still test what their names say. Four fixes land from the
review worktree on branch `frame21-fixes` (reasoned: the recorder holds
the main checkout): the cockpit's `/state.json` answers 500 on a run
database with no views; the seat writes an entry into a stale run before
it refuses; `glossary.same` orders `repointed` by table; two
`criteria.respecify` calls in one session union their lists.

Accepted, no change: a session that stages and retires one refs row
receipts its source for no change (no caller does this). Parked: three
`wake_refs` readers (`model.amend`, grouping, `code.concordance`) take
the first element as a row, and a cascade wake now leads with the
artefact; the loop schedules no cascade wake today, so the readers need
the artefact stripped when it does. The order of a criterion's `term`
refs is the rowid order, a set, not the list the column held.

## The walk that cycled (observed: the diagnosis agent's report on `.rota/clickI.db` and night 70's database)

The onboard-only walk of clickI after stage 4 cycled on the collision
`option` and `option#src_click`. No frame 21 change caused it: night 70
had no collision, and today's survey minted seven second senses under the
same brief and model (per-load variance). The `glossary.same` door refused
the merge 24 times on the word "distinct" inside a negation. The driver's
empty converse landed as a ruling of nothing through stage 1's `land()`
row, adopt refused, and `term_collision` re-fired because every message on
its path closed. Fixes (reasoned: silence is not consent): an empty answer
lands nothing and the ask stays open; the driver does not pump an open ask
twice; the door reads a negation.

Open, rota workflow, not this frame: `term_collision` counts an id as
ruled when a `decisions` row names it, not when a `ruling` ref rests on it.
Recommended: a `ruling` basis counts as ruled, since decided cascades from
a ruling. The old adopt stamped `decided` on an empty answer; the new one
refuses, which is the composition's rule.

## The shape

Section H of the scope report holds the SQL: the `refs` table, the
recursive `provenance` view, and one per-table view (`item_provenance`,
`term_provenance`, `constraint_provenance`, `area_provenance`,
`frame_provenance`) that coalesces a row with no refs to `reasoned`.

## Stages (reasoned: land at a tested boundary, commit each)

Each stage is one implementing agent, one review, one commit. The
acceptance for every stage: `tests/rota/` under `ROTA_MODEL=qwen3:8b`
with the recorder off passes with the baseline's reds only, and the
replay's `STALE` set is unchanged from the baseline.

1. Additive. Add the table and the views. Register the table. Resolve
   the Law 1 maps by `src_table`. Every writer writes refs rows beside the
   old column or stamp. `ctx.onboarding` joins `ctx.provenance`. The
   fixture loader seeds refs rows beside the old columns. `land()` writes
   the `rulings` row. New tests: the three values from seeded refs, the
   precedence, a statement that leaves `ratified` drops its rows to
   `reasoned`, a refs write is receipted under the source artefact.
   No reader changes.
2. Readers and the walk. Every reader in section C and K.4 reads the view
   or the relation. `cascade_wakes` carries row ids from the relation.
   Tests in G1 follow.
3. The drop. Delete the five provenance columns, the five JSON columns,
   `item_statements`, `ctx.provenance`, and every old write. Test seeds
   go through the loader's translation or a helper.
4. Briefs, docs, re-record. K.8 and K.9. Back up `tests/rota/cassettes.db`.
   Re-record the 13 Terminologist cases by exact id, then
   `L3-ratified-statement-becomes-a-term`. Re-create `.rota/clickI_warm.db`.
