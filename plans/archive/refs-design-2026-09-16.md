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
