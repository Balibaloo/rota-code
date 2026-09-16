# Scope of the refs relation (frame 21)

Written 2026-09-16 by the scope agent. Read-only survey of the tree at
`e63762c` plus the uncommitted `tests/rota/walks.jsonl`. Frame 20 (the
`reasoned` rename, `plans/archive/reasoned-scope-2026-09-16.md`) has not
landed. `rota/core/schema.sql:54` still reads `('observed','decided','cited')`.
Frame 20 folds into this frame (`plans/stack.md:50`).

Summary: 5 JSON ref columns, confirmed. 7 code sites write a ref column and
11 write a provenance column. 13 code sites read a ref column and 21 read a
provenance column. 13 cases re-record on the recommended path (op names and
result shapes kept, the fixture loader translates a `provenance:` seed into
refs). The path without the loader translation re-records 43. The path that
changes the read shapes re-records 75. The one decision that most needs a
ruling: what an `observed` row reaches. The ruling names `references_`, and a
`references_` row is today's `cited` (the world). A row observed from the code
has no per-row target today, except `model_areas`. Without a `grain` kind in
the relation, every survey-written term and item derives as `reasoned`.

## A. Schema

### A1. The five JSON ref columns

The count is five. `grep -n "DEFAULT '\[\]'" rota/core/schema.sql` finds
eight other JSON list columns. They are not refs of an owner row to a source
and stay: `survey_records.refs` (:159), `code_lexicon.sources` (:305),
`criteria.surface_refs` (:336), `rulings.per_item` (:448), `decisions.refs`
(:462), `messages.body_refs` (:491), `sessions.pins_json` (:545),
`sessions.wake_refs` (:562).

Every element is a JSON string. No column holds an object.

| Column | file:line | one element | points at | writers | readers | run databases |
|---|---|---|---|---|---|---|
| `glossary_terms.source_refs` | `rota/core/schema.sql:84` | `"<s1>"` (`tests/rota/cases/l1_liaison2.yaml:122,124`), `'[]'` (`l1_researcher.yaml:160`) | a statement id in the fixtures; a `references_` id by the brief (`rota/roles/prompts/terminologist/answer.md:16`) | no op writes a value. `glossary.amend` has no refs parameter (`rota/roles/api.py:879-881`) and omits the column (`:1351-1356`), so an insert takes the default and an update leaves it. `glossary.synthesise` copies it forward on a superseded row (`:1541`). `glossary.same` copies it forward (`:1675`). `tests/rota/test_artefact_quality.py:40-44` seeds it | `rota/roles/api.py:1431`, `:1583` (the SELECT before the copy), `:6422` (`challenge.load`), `rota/testkit/artefacts.py:270-279`, `rota/tools/onboard_run.py:183` | 0 of 118 rows non-empty across 9 databases |
| `business_rules.term_refs` | `rota/core/schema.sql:112` | none on file | glossary ids by the column name | none. `rota/core/identity.py:112` calls the table "observed-era" | `rota/roles/api.py:1688-1705` (the repoint in `glossary.same`) | 0 rows in every database |
| `constraints.source_refs` | `rota/core/schema.sql:129` | a `references_` id | `references_.id` only: `model.amend` keeps the ids that exist (`rota/roles/api.py:2033-2036`) and drops the rest with a note (`:2073-2077`) | `model.amend`, `rota/roles/api.py:2063-2067`, `json.dumps(cited)`. `tests/rota/test_artefact_quality.py:30-34` seeds it | `rota/testkit/artefacts.py:270-279` (`unbacked_citations`). `challenge.load` reads `constraint_bindings` for a constraint, not this column (`rota/roles/api.py:6417-6419`) | 0 of 87 rows non-empty. No run database holds a `references_` row |
| `model_areas.source_refs` | `rota/core/schema.sql:141` | `"src/click/__init__.py"` (`.rota/clickI_n42.db`) | path grains the session opened: `sorted(ctx.opened)[:12]` | `model.describe`, `rota/roles/api.py:2174-2177` | `rota/roles/api.py:6422` (`challenge.load`), `tests/rota/test_onboarding_phases.py:1137` | 10 of 11 rows non-empty |
| `criteria.term_refs` | `rota/core/schema.sql:329` | `"<g1>"` (`tests/rota/cases/l1_answers.yaml:27`) | `glossary_terms.id` | `criteria.specify` (`rota/roles/api.py:3210-3214`), `criteria.respecify` (`:3263-3264`), the repoint in `glossary.same` (`:1688-1705`) | `rota/roles/validators.py:190-199`, `rota/core/scheduler.py:1244-1250`, `rota/roles/api.py:3277`, `:3296-3297`, `:3634-3646`, `rota/tools/audit.py:41` with `:80-97`, `rota/cockpit/inspect_api.py:30` | 24 of 24 rows non-empty |

Writer sites: 7 (`api.py:1541`, `:1675`, `:1688-1705`, `:2063-2067`,
`:2174-2177`, `:3210-3214`, `:3263-3264`). Reader sites: 13 (`api.py:1431`,
`:1583`, `:3277`, `:3296`, `:3634`, `:6422`, `validators.py:190`,
`scheduler.py:1244`, `artefacts.py:270`, `onboard_run.py:183`, `audit.py:41`,
`inspect_api.py:30`, and `api.py:1688` as a reader before it writes).

Two briefs name a parameter that no op has. `terminologist/answer.md:16`
says "Pass the reference id in `source_refs`" for `glossary.amend`.
`vision_keeper/answer.md:12-13` says "`problem.assert` with the reference id
in `source_refs`". `problem.assert` takes `id, text, kind`
(`rota/roles/api.py:445`). `items` has no `source_refs` column. The sandbox
refuses an unknown keyword as a tool error, "unexpected argument(s)"
(`rota/core/sandbox.py:173-183`). So the `cited` path exists for constraints
only.

### A2. The five provenance columns

| Column | file:line | CHECK | writers | run databases (rows by value) |
|---|---|---|---|---|
| `items.provenance` | `rota/core/schema.sql:54` | `('observed','decided','cited')` | `problem.assert` writes `ctx.provenance` (`rota/roles/api.py:664-666`). Nothing writes `cited` | clickI: 4 observed, 1-2 decided. tips: 4 observed, 0-2 decided |
| `glossary_terms.provenance` | `:83` | same | `glossary.amend` writes `ctx.provenance` (`:1353`). `glossary.synthesise` derives it (`:1528`). `glossary.same` copies it (`:1674`). `_adopt_rows` writes `decided` (`:842`). Nothing writes `cited` | clickI: 21-23 decided. tips: 4-8 rows, mixed |
| `constraints.provenance` | `:125` | same | `model.amend` writes `"cited" if cited else ctx.provenance` (`:2065`). `_adopt_rows` (`:842`). Constraint zero writes `'observed'` outside a session (`rota/onboarding/boot.py:244-246`) | clickI: 21 decided, 1 observed. No `cited` row anywhere |
| `model_areas.provenance` | `:142-143` | `DEFAULT 'observed'`, `('observed','decided','ratified')` | `model.describe` writes `ctx.provenance or "observed"` (`:2177`). `_adopt_rows` (`:842`). Nothing writes `ratified` | 1-2 rows, observed or decided |
| `frame_rulings.provenance` | `:725` | `('observed','decided')` | `frame.assign` writes `'observed'` (`:6727-6729`). No code writes `decided`. `grep -rn frame_rulings rota/` finds no principal path | 1-7 rows, all observed |

The one source of the session value is `rota/core/runner.py:1579`:
`"observed" if wake.kind in ONBOARDING_TICKS else "decided"`.
`ONBOARDING_TICKS` is `rota/core/scheduler.py:403-405`. `Ctx.provenance`
defaults to `"decided"` (`rota/roles/api.py:48`). `sandbox.build` defaults
to `"decided"` (`rota/core/sandbox.py:450`). `ENUMS["provenance"]` is dormant
(`rota/core/sandbox.py:80`). Provenance writer sites: 11.

### A3. The relations that exist

| Relation | file:line | key | writer | readers | registered |
|---|---|---|---|---|---|
| `item_statements` | `rota/core/schema.sql:68-72` | `(item_id, statement_id)`, both FK | `problem.assert`, `rota/roles/api.py:659-673`, from `ctx.wake_refs` and the trigger message's `body_refs`, statement ids only | `rota/roles/api.py:724-728` (`problem.consult`), `:8559-8562` (`batches.expect`), `rota/core/runner.py:907` (uncovered statements), `:1312-1315` (the criteria wake), `rota/core/sandbox.py:1498` | `rota/core/db.py:42` under `problem`, `:227` in `JUNCTION_TABLES`, `rota/core/identity.py:63` as `relation` |
| `references_` | `:207-216` | `id` | `references.record`, `rota/roles/api.py:8482-8520` | `references.load` `:8523-8533`, `model.amend` `:1930-1932`, `:2033`, `rota/testkit/artefacts.py:266` | `rota/core/db.py:72`, `identity.py:101` as `keyed` |
| `survey_citations` | `:184-188` | `(survey_id, grain)`, `resolves` | `surveys.attest`, `rota/roles/api.py:2639-2646`; `_derive_frame_record`, `rota/core/runner.py:2340-2367` | `rota/roles/validators.py:142-161` | `db.py:52`, `identity.py:91` as `journal` |
| `constraint_bindings` | `:147-152` | `(constraint_id, grain)`, `grain_kind`, `resolves` | `model.amend` `:2068-2070`; constraint zero `rota/onboarding/boot.py:253-256` | `rota/core/lifecycle.py:268-329`, `rota/core/scheduler.py:1647-1660`, `rota/roles/validators.py:132`, `rota/core/predicates.py:1351`, `rota/roles/api.py:6418`, `rota/testkit/artefacts.py:213`, `rota/tools/audit.py:176` | `db.py:44`, `identity.py:65` as `relation` |

`_apply_write` inserts a junction row with `INSERT OR REPLACE` over the
columns given (`rota/core/db.py:253-260`). A receipt is written per write
with `table_name` and `row_id` (`db.py:409-416`). `ARTEFACT_OF_TABLE` maps
each table to one artefact (`db.py:79-83`).

### A4. The sources of a ruling

| Source | file:line | writer | reader | note |
|---|---|---|---|---|
| `statements.status = 'ratified'` | `rota/core/schema.sql:33-44` | `brief.ratify`, `rota/roles/api.py:417-421`, the only writer of `ratified`. `brief.segment` writes `proposed` (`:411-413`) | `brief.list` `:437`, `runner.py:907`, `:1313`, `api.py:8561`, `sandbox.py:1498` | the survey found no writer of `superseded`, `contradicted` or `clarified` on statements. `rota/core/predicates.py:226-239` drains `contradicted`. `supersedes` (`:41`) has no writer |
| `rulings` | `:444-454` | `rulings.rule`, `rota/roles/api.py:4737`, `:4776`. `per_item` maps row ids to approve, contest or revise | `apply_rulings`, `rota/roles/principal.py:745-772`, lands each open row through `land()` and sets `landed` or `stale` | the record with a version that `plans/composition.md:62-63` names |
| `decisions` | `:456-464` | `decisions.author` by a seat (`api.py:4884-4959`); `land()` writes `author = 'principal'` rows (`principal.py:670-672`) | `decisions.search` `:4965` | `refs` is a JSON list (`:462`) |
| `frame_rulings` | `:718-728` | the judge only | `rota/onboarding/areas.py:62-69`, `rota/roles/api.py:6682`, `:6715-6716` | the schema comment at `:698-699` calls the two values `source='judge'` and `source='ruling'` |
| `items.approval` | `:55-57` | `land()`, `principal.py:699-701`; `problem.set_approval`, `api.py:676-686` | `scheduler.py:246-260`, `predicates.py:801`, `:1150-1154` | stays. Not a provenance stamp |
| `config` key `verdict:<msg>` | none | `land()`, `principal.py:725-728` | `verdict_for`, `principal.py:805-808`; `_ruled_ids`, `api.py:797-819` | "Rulings live in `config`... Law 11 has never been asked about it" (`rota/DECISIONS.md:897-899`) |

`_adopt_rows` (`api.py:822-849`) walks the trigger message's `cause_id`
chain to a `verdict:` key and stamps `decided` on the rows the verdict
approves. It is the only code that turns a ruling into a provenance value.
`tests/rota/test_arc_synthetic.py:318-404` drives it whole.

## B. The revocation walk of law 9

Law 9 is `rota/LAWS.md:241-249`. The enforcement table names
`scheduler.cascade_wakes` and `problem.prioritize` with `amends=False`
(`rota/LAWS.md:378`).

| Step | file:line | reads | note |
|---|---|---|---|
| the amendment moves a version | `rota/core/db.py:128-140`, `:274-276` | `Write.amends` | approval and priority do not move the version |
| the item leaves the schedule | `rota/core/scheduler.py:246-260` (`tick_slicing`), `rota/core/predicates.py:801` (`batch_start`) | `items.approval`, `approval_ver`, `version` | row-level, items only |
| the batch is abandoned | `rota/core/predicates.py:1135-1157` (`cancel`) | `batches.status`, the same three item columns | the scheduler acts. No session is woken |
| the cascade order | `rota/core/scheduler.py:1526-1556` (`cascade_order`) | `rota/design/graph.json` refs edges (`:947-1050`, `:1179-1190`, `:1461-1475`), `cascade: false` on `model -> code` (`:975-980`) | artefact level. `rota/design/graph.py:46-56` carries `Edge.cascade` |
| the cascade wakes | `rota/core/scheduler.py:1558-1600` (`cascade_wakes`) | `receipts.table_name` for the committed session, `ARTEFACT_OF_TABLE` (`db.py:79-83`) | wakes every writer of every downstream artefact with `refs=(artefact,)` (`:1596`). Row ids do not travel |
| the term walk | `rota/roles/api.py:1688-1705` (`glossary.same`) | `criteria.term_refs`, `business_rules.term_refs` by `LIKE` | the only row-level walk along a ref column in the tree. It repoints, it does not revoke |
| the term suppression | `rota/core/scheduler.py:1225-1250` (`resting_on_open_terms`) | `criteria.term_refs` against open `term_collision` wakes | holds a batch back. Not a revocation |

The walk reads neither `item_statements` nor a JSON ref column. It reads
receipts and the artefact graph. The statement to item hop is read only by
the pushers of text: `runner.py:907-910`, `:1312-1315`, `api.py:724-728`,
`:8559-8562`, `sandbox.py:1498`. No code reads "which items cite this
statement" to revoke them. A ratified statement that later changes status
changes nothing on its items today. "The walk and the view share one
relation" is new code, not a rewire.

## C. Law 11's view

Every reader of a provenance column that gates or routes, checked against
the tree. The last column says what the derived value must return for the
reader to keep its behaviour.

| Reader | file:line | today | the derived value must return | note |
|---|---|---|---|---|
| found never overwrites decided | `rota/roles/api.py:471-481` | an `observed` session refuses to amend an item `WHERE provenance = 'decided'` | `decided` for an item that reaches a ratified statement or a ruling | the session side, `ctx.provenance == "observed"`, is the wake kind. It stays a wake fact (`runner.py:1579`) or moves to `wake.kind in ONBOARDING_TICKS` |
| same words on an observed row | `rota/roles/api.py:487-500` | a non-observed session refuses to restate an `observed` item | `observed` for an item written by an onboarding wake | needs a code target on items (section D) |
| `problem.baseline` | `rota/roles/api.py:731-750` | `WHERE provenance = 'observed'` | `observed` for onboarding items | same |
| adopt moves observed only | `rota/roles/api.py:829-842` | reads the stamp, writes `decided` | replaced: adopt writes a ref to the ruling | the reader goes with the writer |
| `glossary.synthesise` | `rota/roles/api.py:1520-1533` | `decided` if any reading is `decided`, else `observed` | replaced: the composed row inherits the readings' refs | the comment at `:1527` states the precedence: decided over observed |
| slicing refuses observed | `rota/roles/api.py:2707-2719` | `== "observed"` raises | `observed` for onboarding items | `tests/rota/test_desk_guards.py:1365` matches `"is observed"` |
| frame ruling outranks | `rota/roles/api.py:6715-6716` | `== "decided"` refuses reassign | `decided` for a prefix that reaches a ruling | no writer of that row exists. Q3 |
| frame ruling depth tie | `rota/onboarding/areas.py:62-69` | `decided` outranks at equal depth | same | same |
| `LIFECYCLE_COLUMNS`, `TERMINAL` | `rota/core/predicates.py:127-129`, `:154-167` | the three provenance columns are lifecycle columns; `decided` and `cited` are terminal | delete the six entries and the three columns. `schema_states()` (`:1573-1590`) parses CHECKs from the schema, so a column that is gone is not asked about | `tests/rota/test_predicates.py:20-28` |
| `observed_entries` | `rota/core/predicates.py:486-491`, `:524-526`, `:562-566` | drains `observed` on four tables, presents the fresh ones | `observed` for onboarding rows on all four tables. `drains=` names a column that will not exist. No lint checks a drain against the schema (`check_terminal_states` iterates schema states, `:1597-1618`) | a `cited` row was never presented. Under the ruling a `references_` row is `observed`. Q4 |
| `tick_slicing` | `rota/core/scheduler.py:250` | `i.provenance != 'observed'` in SQL | the view must be joinable in this SQL | the tipsK and tipsT cases (`:236-239`) |
| observed item words | `rota/core/scheduler.py:600` | `WHERE provenance = 'observed'` | `observed` | |
| signoff page | `rota/roles/principal.py:317-326` | `observed` under "It does today" | `observed` | seat1 2026-09-12 (`:319-322`) |
| contest skips observed | `rota/roles/principal.py:660-668` | a contest on an `observed` item is not relayed | `observed` | seat2 2026-09-12 |
| `unbacked_citations` | `rota/testkit/artefacts.py:257-281` | `cited` with no `source_refs` or a dangling one | replaced by "a `reference` ref whose target is not in `references_`" | called from `artefacts.py:409` |
| wake refs render | `rota/core/runner.py:985-988` | `items` render `id, text, kind, approval, provenance` | join the view, same field name | the prompt text is the cassette key (section I) |
| consult and load return the column | `rota/roles/api.py:1743`, `:1749`, `:1777-1780`, `:2195-2200`, `:2211`, `:6682` | `SELECT ... provenance` | join the view, same field name | same |
| cockpit lists | `rota/cockpit/inspect_api.py:27-28` | column shown raw | join the view or drop | display |
| `onboard_run` print | `rota/tools/onboard_run.py:183-191` | `[cited]` tag, `provenance:9s` | the view's `basis` for the tag | tool |
| `_PROVENANCE_WORDS` | `rota/roles/api.py:5225`, `:5230` | refuses a sense named after the value | no change | words, not a column |
| `split_senses` | `rota/tools/split_senses.py:161-162` | historical rename table | no change | archive |

Readers of `ctx.provenance` as a session fact, not a column: `api.py:475`,
`:665`, `:1353`, `:2065`, `:2177`, `runner.py:1579-1583`,
`sandbox.py:450-467`. After the change the session fact is the wake kind.
Under the recommended design the fact decides which refs a write records.

## D. Onboarding evidence

An onboarding wake is one of `ONBOARDING_TICKS`
(`rota/core/scheduler.py:403-405`). The runner sets `ctx.provenance =
"observed"` for it (`rota/core/runner.py:1575-1579`). Every owner write
copies the stamp. The evidence of what the session read lives in different
places per table.

| Row | mode and brief | what the session reads | where the code it read is recorded |
|---|---|---|---|
| an item | `problem.baseline` (`rota/roles/api.py:731-750`) reads observed items. `problem.assert` writes them (`:664-666`). The Vision Keeper's `survey.md:7-11` and `orient.md` route every ending through `code.source` | `code.survey`, `code.source`; the paths land in `ctx.opened` | nowhere on the row. `items` has no ref column. `item_statements` is empty on a tick: `named` is the wake refs plus the trigger message's refs (`:659-667`), and a tick has neither. The survey record for the area (`surveys.attest`, `:2240-2653`) carries `survey_citations` under id `"<role>:<area>"` (`:2433`) |
| a term | `glossary.survey`, `glossary.define` (`terminologist/survey.md`, `define.md`) | `code.area`, `code.concordance`, `code.source` | nowhere on the row. `glossary.amend` writes `term, sense_short, sense_body, provenance, area` (`:1351-1356`). `area` (`schema.sql:85-98`) says which area, not which file. The survey record carries the citations |
| a constraint | `model.survey` (`architect/survey.md:28-34`: "cite the line that keeps it in `source_refs`") | `code.area`, `code.source` | `constraint_bindings` (`:2068-2070`), required by `model.amend` (`:2010-2014`). A delivery-loop constraint also binds, so a binding does not say "observed". `source_refs` takes `references_` ids only (`:2033-2036`), so the brief's "line" is dropped with a note. `plans/operating-facts.md:269` records the score that lied on this |
| an area account | `model.describe` (`:2148-2178`) | `code.area`, `code.source` | `model_areas.source_refs = sorted(ctx.opened)[:12]` (`:2176`). The one per-row code citation in the tree. `tests/rota/test_onboarding_phases.py:1128-1137` pins it |
| a frame ruling | `frame.assign` (`:6685-6744`) | `code.tree` | the id is the path prefix. `_derive_frame_record` (`runner.py:2340-2367`) writes one `survey_citations` row per prefix with the first indexed grain under it |
| constraint zero | `rota/onboarding/boot.py:232-257` | none, written outside a session | its bindings are the unsurveyed areas (`:249-256`) |

Findings, not decisions:

1. A `references_` row is the world, not the code. The composition says
   "observed from the code or the world" (`plans/composition.md:58-59`).
   `rota/LAWS.md:287-295` calls the world half `cited`. The ruling's
   "reach a `references_` row, observed" covers the world half only.
2. The code half has a per-row target on `model_areas` only. Items and terms
   carry none. A constraint's bindings do not distinguish a survey write
   from a delivery write.
3. The per-session evidence exists for every onboarding write:
   `survey_citations` under the survey record `"<role>:<area>"`. It is keyed
   to the session's area, not to the row.
4. `ctx.opened` holds the paths the session read on every wake
   (`api.py:2176`, `:2610`). `model.describe` already writes it as
   refs. The same line in `problem.assert` and `glossary.amend` would give
   items and terms a code target. On a delivery wake the same write would
   mark a reasoned row observed, so the write must stay conditional on the
   wake kind.
5. Two fixtures put statement ids in `glossary_terms.source_refs`
   (`tests/rota/cases/l1_liaison2.yaml:122-124`). The brief means reference
   ids. Neither reading is checked by any test or expect.

Three shapes cover the code half. A `grain` kind with the opened paths as
targets (precedent `model.describe`). A `survey` kind with the survey record
as the target (precedent `survey_citations`). A wake-kind fact kept outside
the relation. Section J recommends one.

## E. The cockpit provenance panel

`inspect_api.provenance` (`rota/cockpit/inspect_api.py:379-455`) walks:

1. the row, `SELECT * FROM {table} WHERE id = ?` (`:409-417`);
2. `receipts` joined to `sessions`, every session that touched the row,
   oldest first (`:423-431`);
3. the latest session's row (`:440-445`) and its wake (`:446-451`);
4. `tool_calls` for that session (`:452-455`);
5. `causal_chain` over `messages.cause_id` (`:456`, `:461-480`);
6. `shown_to` over `turns` (`:457`).

Tables: the row's table, `receipts`, `sessions`, `tool_calls`, `messages`,
`turns`. `_refs` (`:371-376`) parses `sessions.wake_refs`, not a ref column.
The panel never branches on a provenance value and never reads one of the
five ref columns. `LEAD_COLUMNS` (`:27-30`) lists `provenance` and
`term_refs` for the row lists, display only. `panels.js:1333-1410` renders
four groups. `tests/rota/provenance_check.js:100-118` asserts the four
headings and the recorded-or-not-retained line. `tests/rota/test_provenance.py`
seeds provenance values through `Write` (`:81`, `:177`) and asserts the wake
refs (`:153-154`) and the chain.

`out["row"]` dumps every column (`:418`). After the change the row shows no
provenance field unless the API joins the view. That is one line per table.
A "WHAT IT RESTS ON" group listing the row's refs is the natural addition
and is optional for the frame.

## F. Validators

| Check | file:line | enforces | reads | called from |
|---|---|---|---|---|
| `check_criteria_terms` | `rota/roles/validators.py:190-199` | every criterion has at least one `term_refs` entry, and each names a `glossary_terms.id` | `criteria.term_refs`, `glossary_terms.id` including superseded rows (`rota/roles/api.py:1681-1684`) | `tests/rota/test_arc_synthetic.py:298` |
| `check_bindings_resolve` | `:120-140` | every binding with `resolves = 1` names a grain or an area in the index | `constraint_bindings`, `code_index` | absent from the arc on purpose (`test_arc_synthetic.py:308`) |
| `check_survey_citations` | `:142-161` | every survey record cites at least one grain, and no citation has `resolves = 0` | `survey_records`, `survey_citations` | same |
| `check_survey_areas` | `:164-187` | every survey record's area is still in the index | `survey_records`, `code_index` | |

No validator reads `source_refs`. The `source_refs` checks live in
`rota/testkit/artefacts.py:257-281` (`unbacked_citations`, section C) and
`rota/tools/audit.py:41` with `:80-97` (every `term_refs` and `surface_refs`
entry resolves to an id in some table). With one relation, all three become
one query: a ref whose target is not in its kind's table.

## G. Tests, cases, briefs, docs

### G1. Test assertions

11 test files name `source_refs` or `term_refs`. 47 name `provenance`. The
assertions, not the seeds:

| Assertion | file:line | asserts | after the change |
|---|---|---|---|
| criteria are written in glossary terms | `tests/rota/test_arc_synthetic.py:141-142` | `json.loads(row["term_refs"]) == ["g1"]` | read the relation |
| cited with nothing behind it | `tests/rota/test_artefact_quality.py:140-152` | `"no source_refs"`, `"r_missing"` in the finding | the finding's wording changes |
| an observed constraint needs no reference | `:155-159` | `unbacked_citations(db) == []` | keep |
| describe records what it opened | `tests/rota/test_onboarding_phases.py:1128-1137` | `"src/billing/charges.py" in w[2]["source_refs"]` | the write is a refs row |
| a list argument stays a list | `tests/rota/test_t0_sandbox.py:200-208` | `writes[0][2]["term_refs"] == '["g1", "g2"]'` | the write is refs rows |
| supersede repoints | `tests/rota/test_glossary_senses.py:440-451` | `refs == ["note"]` | read the relation |
| staged write shape | `tests/rota/test_t0_sandbox.py:136-158` | the `items` write carries `"provenance": "decided"` | the write carries no provenance |
| observed never amends decided | `tests/rota/test_onboarding_phases.py:953-973` | the note says `decided`; the row keeps `("decided", ...)` | seed a ratified statement and a ref instead of the stamp |
| frame ruling outranks | `tests/rota/test_onboarding_phases.py:1556-1566` | seeds `decided` in `frame_rulings`; `match="decided\|outranks"` | Q3 |
| observed asserts | `tests/rota/test_onboarding.py:296`; `test_onboarding_phases.py:422`, `:451`, `:1164`, `:1551` | `row["provenance"] == "observed"` | read the view |
| slicing and the observed row | `tests/rota/test_desk_guards.py:1355-1367`, `:1420-1432` | `match="is observed"`, `match="observed row"` | the messages stay if the view returns `observed` |
| adopt moves rows to decided | `tests/rota/test_arc_synthetic.py:318-404` | `rows == {"g1": "decided", "k1": "decided", "g2": "observed"}` | read the view; the arc drives the ruling path |
| who writes decided can author | `tests/rota/test_laws.py:225-236` | a role that writes `decided` can write `decisions` | reword to the roles that write refs to a ruling |
| every lifecycle state has a way out | `tests/rota/test_predicates.py:20-28` | `check_terminal_states() == []` | passes once the three columns and six `TERMINAL` entries go together |
| provenance as a sense | `tests/rota/test_glossary_senses.py:108` | `"provenance" in msg` | no change |
| every table is classified | `tests/rota/test_identity.py:27-39` | a new table must be in `NATURAL_KEYS` | add the relation as `relation` |
| a ref that names no row is refused | `tests/rota/test_identity.py:72` | the door check | extend to the relation's targets |
| cockpit chain | `tests/rota/test_provenance.py:81`, `:177` | seeds only | no change |

### G2. Cases

127 cases in `tests/rota/cases/*.yaml`. Counted by a script over the YAML.

| Column | cases that seed it | non-empty | cases whose `expect:` or `forbidden:` reads it |
|---|---|---|---|
| `criteria.term_refs` | 42 | 2 (`L1-DV-apply-the-answer-and-carry-on`, `L1-TS-apply-a-term-and-write-the-test`) | 0 |
| `glossary_terms.source_refs` | 2 (`l1_liaison2.yaml:122-124`, `l1_researcher.yaml:160`) | 1 | 0 |
| `constraints.source_refs` | 0 | 0 | 0 |
| `model_areas.source_refs` | 0 | 0 | 0 |
| `business_rules.term_refs` | 0 | 0 | 0 |
| `provenance`, any table | 91 | items 72 cases (79 `decided`, 3 `observed` rows); glossary_terms 24 cases (23 `decided`, 17 `observed`); constraints 18 cases (10 `decided`, 8 `observed`); model_areas 1 case (`observed`) | 0 |
| `references_` rows | 3 (`L1-AR-cite-the-clause-into-a-constraint`, `L1-TE-a-standard-definition-is-not-automatically-ours`, `L1-VK-a-source-does-not-settle-scope`) | | 0 |
| `item_statements` rows | 2 (`l1_gatekeeper2.yaml:32`, `l1_liaison.yaml:127`) | | 0 |

No `expect:` block reads a ref column or a provenance value. The survey
spike cases comment on `source_refs` (`l1_survey_spike.yaml:17`, `:40`,
`:63`, `:86`, `:109`) and score on `constraints` text and `is_global`.
`fields_nonempty` (`rota/testkit/fixtures.py:320-331`) is used by no case.

Which cases show a value to the model. A case's prompt hash covers the whole
prompt including pushed rows (`rota/core/runner.py:218-231`,
`rota/llm/llm.py:73-76`), and the register keys runs on it
(`rota/llm/cassettes.py:365-367`). The transcript column keeps completions
only, so the count comes from the case files and the recorded calls:

- 7 cases render a seeded item row through `_resolve_refs`
  (`runner.py:988`): `L1-DV-elect-on-a-revoked-item`, `L1-LI-present-the-touch`,
  `L1-LI-surface-a-quarantined-message`, `L1-VK-amend-a-contested-item`,
  `L1-VK-amend-a-contested-item-from-a-verdict`, `L1-VK-slice`,
  `L1-VK-submit-drafts-together`.
- 30 cases show a seeded provenance value through a wake ref, a glossary
  read or a model read. The list is in section K.
- 75 cases called an op that returns `provenance` or `term_refs`
  (`glossary.consult`, `glossary.lookup`, `model.consult`, `model.load`,
  `frame.load`, `criteria.load`, `challenge.load`, `glossary.synthesise`,
  `glossary.same`). A changed result shape re-keys every one of them.

### G3. Briefs

| Brief | file:line | the sentence | names |
|---|---|---|---|
| Terminologist answer | `rota/roles/prompts/terminologist/answer.md:16-17` | "**Citing it makes the entry `cited`.** Pass the reference id in `source_refs` and the provenance follows" | a parameter `glossary.amend` does not have |
| Vision Keeper answer | `vision_keeper/answer.md:12-13` | "**Citing it makes the item `cited`.** `problem.assert` with the reference id in `source_refs`" | a parameter and a column that do not exist |
| Architect answer | `architect/answer.md:13` | "Cite the reference in `source_refs` and the entry becomes `cited`" | the real parameter of `model.amend` |
| Architect survey | `architect/survey.md:32` | "cite the line that keeps it in `source_refs`" | a line. The op takes reference ids only |
| Terminologist doctrine | `terminologist/base.md:13-14` | "A term is `decided` (someone chose it, reason on file) or `observed` (extracted from a codebase, found not chosen)" | the two values. Frame 20's line |
| Terminologist doctrine | `terminologist/base.md:18` | "its `term_refs` must name the glossary entries it depends on" | the parameter |
| Terminologist doctrine | `terminologist/base.md:36` | "A glossary entry marked `decided` means the reason is on file, and you are the one who has to put it there" | the value. Frame 20's line |
| Terminologist criteria | `terminologist/criteria.md:8` | "**Every criterion carries `term_refs`** naming the glossary entries it relies on" | the parameter |
| Terminologist repair | `terminologist/criterion_repair.md:13` | "Keep `term_refs` honest" | the parameter |
| Terminologist relay | `terminologist/relay.md:8-9` | "`observed` to `decided`: the content is untouched, and what changes is who stands behind it, which is exactly what provenance records" | the values. Still true of the derived value |
| Architect relay | `architect/relay.md:8-9` | same | same |
| Architect frame | `architect/frame.md:20` | "a decided row outranks you" | the value |
| Liaison observed entries | `liaison/observed_entries.md:4` | "`observed`: found, not decided" | the value |
| Vision Keeper survey | `vision_keeper/survey.md:8-9`, `:16`, `:20` | "`problem.assert` each behaviour as an `in_scope` item with provenance `observed`" | the value |
| Vision Keeper orient | `vision_keeper/orient.md:23` | "Everything here is observed" | the value |
| Liaison verdict signoff | `liaison/verdict_signoff.md:18` | "provenance and approval are the owners' artefacts" | the word |

The base rule: a mode with `<mode>.base.md` does not see `base.md`
(`rota/roles/prompts.py:67-83`). `survey`, `define` and `term_collision`
have their own base in `terminologist/`. So `terminologist/base.md` reaches
13 cases (section K).

### G4. Docs

| Doc | file:line | says |
|---|---|---|
| Law 11 | `rota/LAWS.md:277-295` | the three words, and the `cited` amendment with `source_refs` |
| Law 9 | `rota/LAWS.md:241-249` | "Resolution descends the refs DAG through each artefact's owner" |
| enforcement | `rota/LAWS.md:378`, `:380` | law 9 is `scheduler.cascade_wakes`; law 11 is "`provenance` is `NOT NULL CHECK` on every artefact that has one" |
| L0 | `rota/LAWS.md:110-116` | records reached by following a ref |
| schema sketch | `rota/TESTS.md:93-105` | the columns by name |
| criteria expect | `rota/TESTS.md:318` | non-empty `term_refs` |
| Law 11 record | `rota/DECISIONS.md:750-757` | the `cited` proposal |
| rulings in config | `rota/DECISIONS.md:897-899` | "Law 11 has never been asked about it" |
| adopt stamp | `rota/DECISIONS.md:919` | "The internal stamp stays `provenance='observed'`" |
| term_refs | `rota/DECISIONS.md:1069` | why the column exists |
| drift | `rota/DECISIONS.md:50-70` | "the drift predicate wakes the role whose artefact cited it". No such predicate exists: `grep -n references_ rota/core/predicates.py` is empty |
| onboarding | `rota/ONBOARDING.md:69`, `:166`, `:729`, `:783`, `:1146` | observed provenance, `term_refs`, the frame's two values |
| register | `rota/REGISTER.md:138` | "`criteria.term_refs` is a join that exists" |
| answer key | `rota/ANSWER_KEY.md:74-75`, `:106` | "`provenance = 'cited'` with a `source_refs` pointing at a reference row" |
| graph | `rota/design/graph.json:64`, `:76`, `:94`, `:2198` | provenance on statements, terms and constraints; `term_refs` |
| handoff | `rota/HANDOFF.md:147-150` | law 11 in two values |
| seat | `rota/SEAT.md:465`, `:563` | `refs` on terms; principal rows with provenance `decided` |

## H. Design candidates

### H1. The relation

`item_statements` is the precedent: the pair is the row, both sides are
ids, `identity.py:63` classifies it as `relation`. One table:

```sql
-- What a row rests on. One row per (source, target). The pair is the row.
-- `kind` says which table the target lives in, because the targets are
-- of different kinds and SQLite has no polymorphic foreign key.
CREATE TABLE IF NOT EXISTS refs (
    src_table  TEXT NOT NULL CHECK (src_table IN
                 ('items','glossary_terms','constraints','model_areas',
                  'frame_rulings','criteria','business_rules')),
    src_id     TEXT NOT NULL,
    kind       TEXT NOT NULL CHECK (kind IN
                 ('statement','reference','term','grain','ruling')),
    target     TEXT NOT NULL,
    resolves   INTEGER NOT NULL DEFAULT 1,   -- grains only: 0 once the grain leaves the index
    PRIMARY KEY (src_table, src_id, kind, target)
);
CREATE INDEX IF NOT EXISTS ix_refs_target ON refs(kind, target);
```

The target of each kind: `statement` is `statements.id`; `reference` is
`references_.id`; `term` is `glossary_terms.id`; `grain` is
`code_index.grain`; `ruling` is `rulings.id`. `resolves` follows
`constraint_bindings.resolves` (`schema.sql:150`) and
`survey_citations.resolves` (`:187`): the index is rebuilt, so a grain is
not a foreign key.

An alternative keeps foreign keys: one nullable column per kind
(`statement_id REFERENCES statements(id)`, and so on) with a CHECK that
exactly one is set. It is stricter and wider. The door check
(`tests/rota/test_identity.py:72`) already refuses a ref that names no row,
so the narrow shape loses little.

Registration: `rota/core/db.py:42-75` (`TABLES_OF_ARTEFACT`), `:226-229`
(`JUNCTION_TABLES`), `rota/core/identity.py:63` (`NATURAL_KEYS`, kind
`relation`), `rota/design/graph.json` (a `writes` edge per owner). The
Law 1 question on one table with five writers is Q7.

### H2. The derivation

Precedence: decided over observed over reasoned. The view also returns the
basis, so the readers that distinguish the world from the code keep their
signal.

```sql
-- Provenance derived from what a row reaches. A row with no refs is absent
-- here; the per-table views below coalesce it to 'reasoned'.
CREATE VIEW IF NOT EXISTS provenance AS
WITH RECURSIVE reach(src_table, src_id, kind, target, depth) AS (
    SELECT src_table, src_id, kind, target, 1 FROM refs
    UNION
    SELECT r.src_table, r.src_id, t.kind, t.target, r.depth + 1
    FROM reach r JOIN refs t
      ON r.kind = 'term'
     AND t.src_table = 'glossary_terms' AND t.src_id = r.target
    WHERE r.depth < 8
),
basis AS (
    SELECT src_table, src_id,
        MAX(kind = 'ruling' AND EXISTS (
            SELECT 1 FROM rulings u WHERE u.id = target AND u.status = 'landed'))
          AS ruled,
        MAX(kind = 'statement' AND EXISTS (
            SELECT 1 FROM statements s WHERE s.id = target AND s.status = 'ratified'))
          AS ratified,
        MAX(kind = 'reference' AND EXISTS (
            SELECT 1 FROM references_ x WHERE x.id = target))
          AS world,
        MAX(kind = 'grain' AND resolves = 1) AS code
    FROM reach GROUP BY src_table, src_id
)
SELECT src_table, src_id,
    CASE WHEN ruled OR ratified THEN 'decided'
         WHEN world OR code    THEN 'observed'
         ELSE 'reasoned' END AS provenance,
    CASE WHEN ruled THEN 'ruling' WHEN ratified THEN 'statement'
         WHEN world THEN 'world'  WHEN code THEN 'code'
         ELSE 'none' END AS basis
FROM basis;

-- One per owner table, so a reader can join on the id alone.
CREATE VIEW IF NOT EXISTS item_provenance AS
SELECT i.id, COALESCE(p.provenance, 'reasoned') AS provenance,
       COALESCE(p.basis, 'none') AS basis
FROM items i LEFT JOIN provenance p
  ON p.src_table = 'items' AND p.src_id = i.id;
```

The same per-table view for `glossary_terms`, `constraints`, `model_areas`
and `frame_rulings`. `tick_slicing` (`scheduler.py:250`) becomes a join on
`item_provenance`. `observed_entries` (`predicates.py:524-526`) becomes a
join per table.

Where the recursion is needed. Today one hop reaches every source:
criteria and business rules cite terms (`term` kind), and a term cites a
statement, a reference or a grain. No column records a term citing a term.
`glossary.synthesise` composes from other terms (`api.py:1516-1533`) and
records `composed_from` in its result only, not in a column. `superseded_by`
(`schema.sql:104`) is a pointer, not a ref. So two hops suffice today: a
criterion that cites a term that cites a ratified statement. The CTE is
cheap and the cap at 8 guards a cycle written by hand. A constraint citing a
term would be a third path (`graph.json:961-966`, "constrains term") and no
column carries it.

Both a `references_` row and a ratified statement: `decided` wins, `basis =
'statement'`. Reasons: `glossary.synthesise` already ranks a decided reading
over an observed one (`api.py:1526-1528`); `_adopt_rows` moves an observed
row to decided on a ruling and never back (`:839-842`); the frame's `decided`
outranks the judge (`areas.py:69`, `api.py:6716`). A ruling is the stronger
claim about who stands behind the row. The finding stays visible in `basis`
only while no stronger basis exists. A reader that needs "cited and
decided" together reads the refs, not the view.

### H3. The walk of law 9 on the same table

The walk from an amended statement to the rows that rest on it:

```sql
SELECT src_table, src_id FROM refs
WHERE kind = 'statement' AND target IN (?);       -- the amended statements
```

Then one hop for the rows that cite those rows:

```sql
SELECT src_table, src_id FROM refs
WHERE kind = 'term' AND target IN (?);            -- the terms found above
```

`cascade_wakes` (`scheduler.py:1558-1600`) keeps its artefact order from
`cascade_order` and gains row ids: `Wake(owner, "cascade", refs=(row ids))`
instead of `refs=(artefact,)` (`:1596`). The trigger is the same receipts
read (`:1566-1573`) plus the rows those receipts name. The view flips on
its own: a statement whose status leaves `ratified` drops every row that
rests on it from `decided` at the next read. `cancel` (`predicates.py:1135-1157`)
keeps reading `approval_ver` against `version`. The relation adds the hop
the walk lacks today (section B), it does not replace the version compare.

## I. Migration

The design refuses a table rebuild for a run database: "Databases here are
throwaway and rebuilt by `init_db` at boot; a migration path would be a
promise the design deliberately does not make" (`rota/cli.py:273-276`).
`init_db` runs `executescript` over `CREATE TABLE IF NOT EXISTS`
(`rota/core/db.py:111-114`) and alters nothing.

| Item | file:line | carries | after the change | cost |
|---|---|---|---|---|
| run databases | `.rota/clickI_n42.db`, `clickI_n70_merged.db`, `clickI_warm.db`, `tipsAL.db`, `tipsAN.db`, `tipsAP.db`, `tipsAQ.db`, `tipsAR.db`, `tipsAS.db` | the five provenance columns with seat-written rows (clickI: 21-23 `decided` terms, 21 `decided` constraints). `model_areas.source_refs` with paths (10 rows). `criteria.term_refs` (24 rows). No `references_` row. 0-2 `item_statements` rows | no `refs` table. A view over `refs` raises on open | `cli.py:198-206` marks the run `stale` and prints `[behind schema: ...]` (`:272-277`). Counts still print. The cockpit's `provenance()` dumps the row (`inspect_api.py:409-418`) and works. A view join there needs a guard |
| warm snapshot | `.rota/clickI_warm.db`, `clickI_warm.json` | the old columns, no `refs` | a run started from it has no relation to write | re-create from a fresh boot after the schema lands |
| cassettes | `tests/rota/cassettes.db`, 18166 rows | 1408 rows carry `source_refs` in the system prompt, 2968 `term_refs`, 3360 `provenance`, 588 `cited` | no migration. A changed brief or a changed pushed row changes the key (`rota/llm/cassettes.py:105-123`) and misses. Stale rows stay with `hits = 0` | back up first. The 2026-09-16 backups are in `.rota/` |
| register | `case_runs`, 144428 rows | keyed by `prompt_hash` (`cassettes.py:72`) | new prompts are new rows | none |
| cases | `tests/rota/cases/*.yaml` | 91 seed `provenance:`, 44 seed a ref column, 2 seed `item_statements` | the loader must translate or the seeds must change | Q9 |
| precedent | `57823c1` | `cited` joined the CHECK with no migration | same shape | |

Forward-only cost: every existing run database is read-only history from
the landing on. A seat cannot resume one. The nine databases above are
already behind at least one schema change (frame 20's `reasoned` would have
failed their CHECK the same way).

## J. Open questions

Each with a recommended answer.

Q1. What does an `observed` row reach? The ruling says a `references_` row.
That is the world half (`plans/composition.md:58`). Items and terms written
by a survey reach nothing today (section D). Without a code target every
onboarding item and term derives as `reasoned`, `tick_slicing` slices the
account's behaviours (the tipsK and tipsT regression, `scheduler.py:236-239`),
`observed_entries` presents nothing, and the two guards at `api.py:471-500`
stop holding. Recommended: a `grain` kind. On an onboarding wake
(`ONBOARDING_TICKS`), `problem.assert`, `glossary.amend` and `model.amend`
write one `grain` ref per path in `ctx.opened`, capped at 12 as
`model.describe` does (`api.py:2176`). `model.describe` writes the same rows
instead of `source_refs`. `frame.assign` writes one `grain` ref per prefix,
the first indexed grain, as `_derive_frame_record` computes
(`runner.py:2350-2356`). The wake kind stays the fact that decides which refs
a write records, so `runner.py:1579` moves, it does not vanish. The
alternative, a `survey` kind pointing at `survey_records.id`, is one row per
write and needs no cap, and it makes "observed" depend on a journal row
whose `area_hash` can go stale (`schema.sql:160-164`).

Q2. Precedence when a row reaches both a `references_` row and a ratified
statement. Recommended: `decided`, with `basis = 'statement'` (section H2).

Q3. `frame_rulings.provenance`. Two values, the judge writes `observed`, no
code writes `decided`, and two readers rank on it (`areas.py:69`,
`api.py:6716`). The frame's ends-when names five columns, so this one goes.
Recommended: fold it in. The judge's `frame.assign` writes a `grain` ref
(Q1). A principal's ruling on a prefix, when built, writes a `ruling` ref.
The two readers join `frame_provenance`. Cost: two readers, one test
(`test_onboarding_phases.py:1564-1566`), the schema comment at `:698-699`
and `:723-724`. The cheaper alternative renames the column to `source`
(`'judge'`, `'ruling'`) as the schema comment already calls it. That keeps
a stamp on an owner table under another name.

Q4. The `cited` value and `model.amend` (`api.py:2065`; the brief calls the
mode `model.constrain`). Under the composition a `references_` row is
"observed from the world", so `cited` becomes `observed` with `basis =
'world'`. Readers that distinguish it today: `TERMINAL`
(`predicates.py:165-167`), `unbacked_citations` (`artefacts.py:271`),
`onboard_run` (`:185`), four briefs (section G3), `rota/ANSWER_KEY.md:74-75`.
One behaviour changes: `observed_entries` (`predicates.py:524-526`) drains
`observed` and never presented a `cited` row. Recommended: keep today's
behaviour in this frame. `observed_entries` drains `basis = 'code'` only,
and a row observed from the world waits for a challenge as it does now.
Present the alternative, one page for both kinds, as its own question.

Q5. `model_areas.provenance` allows `'ratified'` (`schema.sql:143`). Nothing
writes it. Recommended: it goes with the column. A ratified area is a
`ruling` ref.

Q6. Does `item_statements` fold into the relation? Recommended: yes, as
`kind = 'statement'`. The walk of law 9 and the view then read one table
with no `UNION`. Cost: one writer (`api.py:671`), five readers
(`api.py:724`, `:8559`, `runner.py:907`, `:1312`, `sandbox.py:1498`), three
registrations (`db.py:42`, `:227`, `identity.py:63`), four test files
(`test_desk_guards.py`, `test_developer_expect.py`, `test_pushes.py`,
`test_signoff_assumptions.py`, seven mentions), two case fixtures
(`l1_gatekeeper2.yaml:32`, `l1_liaison.yaml:127`). The FK on
`statement_id` is lost (H1 names the alternative that keeps it).

Q7. Law 1 on one table with five writers. `ARTEFACT_OF_TABLE` maps a table
to one artefact (`db.py:79-83`). Receipts key on the table (`db.py:409-416`).
`cascade_wakes` maps touched tables to artefacts (`scheduler.py:1566-1573`).
`RULED_TABLES` maps a table to its owner (`sandbox.py:601-610`).
`graph.check_writers` wants one writer per artefact (`graph.py:342-351`).
Recommended: one table, and the four maps resolve a `refs` row by its
`src_table`. The `Write` for a refs row carries `src_table` in `values`, so
`session_commit` can receipt it under the source artefact. The alternative
is one table per owner artefact (`item_refs`, `term_refs`, `constraint_refs`,
`area_refs`, `frame_refs`) with the view a `UNION` of five. It touches no
map and it is not "one refs relation".

Q8. What a `ruling` ref targets. Today a ruling lives in three places:
`rulings.id` (`schema.sql:444-454`), the `config` key `verdict:<msg>`
(`principal.py:725-728`), and a `decisions` row with `author = 'principal'`
(`principal.py:670-672`). Recommended: `rulings.id` with `status = 'landed'`.
It is the record with a version that the composition names
(`plans/composition.md:62-63`). `_adopt_rows` (`api.py:822-849`) writes the
ref instead of the stamp. One gap: the seat's answer lands through `land()`
directly (`principal.py:550`) with no `rulings` row. That path needs a
`rulings` row too, or `verdict_for` has to stay as a second source. Push it
as its own line in the frame.

Q9. The 91 fixtures that seed `provenance:`. Recommended: the fixture
loader (`rota/testkit/fixtures.py`) translates the key. `observed` becomes
a `grain` ref to a fixture grain, `decided` becomes a `ruling` ref to a
landed fixture ruling, `cited` becomes a `reference` ref to a seeded
reference. The case files do not change. The rendered value stays the same
word, so the 30 prompts that show a seeded value stay byte-identical. The
same translation covers `source_refs:` and `term_refs:` seeds.

Q10. Op parameters and result shapes. `model.amend(source_refs=)`,
`criteria.specify(term_refs=)`, `criteria.respecify(term_refs=)` are the
names the briefs use. `glossary.consult`, `glossary.lookup`, `model.consult`,
`model.load`, `frame.load` return `provenance`; `criteria.load` returns
`term_refs`. Recommended: keep every name. The parameter writes refs rows.
The result reads the view. This is what holds the re-record count at 13.

Q11. Two briefs name a `source_refs` parameter that does not exist
(`terminologist/answer.md:16`, `vision_keeper/answer.md:12-13`).
Recommended: give `glossary.amend` and `problem.assert` a `source_refs`
parameter that writes `reference` refs, in this frame, since the writer of
a `reference` ref must exist for the relation anyway. The briefs then say
what the ops do. No brief line changes, so no extra re-record.

Q12. Frame 20 folds in. The rename's stored value never exists: no column
stores `reasoned`. The rename's brief lines (`terminologist/base.md:13-14`,
`:36`) still change, because they describe two values. Recommended: land
them in this frame with the three words of `rota/LAWS.md:279-285`. The 13
Terminologist cases re-record once, not twice.

## K. Change set in landing order

1. Schema. `rota/core/schema.sql`: add `refs` and the views (H1, H2).
   Delete `:54`, `:83`, `:125`, `:142-143`, `:725`. Delete `:84`, `:112`,
   `:129`, `:141`, `:329`. Delete `item_statements` (`:68-72`) on Q6.
   Registration: `rota/core/db.py:42-75`, `:226-229`;
   `rota/core/identity.py:63`; `rota/design/graph.json` writes edges;
   `rota/core/predicates.py:127-129`, `:154-167`.
2. The session fact. `rota/core/runner.py:1575-1583`: the wake kind
   travels as `ctx.onboarding` (or the wake itself), not as a value.
   `rota/roles/api.py:42-48`, `rota/core/sandbox.py:80`, `:450`, `:467`.
3. Writers. `rota/roles/api.py:659-673` (`problem.assert`: statement refs
   as today, grain refs on an onboarding wake, `source_refs` on Q11);
   `:1351-1356` (`glossary.amend`: grain refs, `source_refs` on Q11);
   `:1516-1545` (`glossary.synthesise`: the kept row inherits the readings'
   refs); `:1660-1705` (`glossary.same`: copy refs, repoint `term` refs);
   `:2033-2071` (`model.amend`: `reference` refs, grain refs on an
   onboarding wake); `:2174-2177` (`model.describe`); `:3210-3214`,
   `:3263-3264` (criteria); `:6727-6729` (`frame.assign`); `:822-849`
   (`_adopt_rows` writes a `ruling` ref); `rota/onboarding/boot.py:244-246`
   (constraint zero: a grain ref per unsurveyed area); `runner.py:2340-2367`.
4. Readers. Section C, every row. `rota/core/scheduler.py:250`, `:600`,
   `:1244-1250`; `rota/core/predicates.py:486-491`, `:524-526`, `:562-566`;
   `rota/roles/api.py:471-500`, `:731-750`, `:1743-1749`, `:1777-1780`,
   `:2195-2211`, `:2707-2719`, `:3277`, `:3296-3297`, `:3634-3646`,
   `:6417-6422`, `:6682`, `:6715-6716`, `:8559-8562`; `:724-728`,
   `runner.py:907`, `:985-988`, `:1312-1315`, `sandbox.py:1498`;
   `rota/roles/principal.py:317-326`, `:660-668`;
   `rota/onboarding/areas.py:62-69`; `rota/roles/validators.py:190-199`;
   `rota/testkit/artefacts.py:257-281`; `rota/tools/audit.py:41`, `:80-97`;
   `rota/tools/onboard_run.py:183-191`; `rota/cockpit/inspect_api.py:27-30`,
   `:414-421`.
5. The walk. `rota/core/scheduler.py:1558-1600`: row ids on the cascade
   wake from the relation (H3). `rota/LAWS.md:378` names it.
6. Fixtures. `rota/testkit/fixtures.py`: translate `provenance:`,
   `source_refs:`, `term_refs:` and `item_statements:` seeds into refs (Q9).
   The two `item_statements` fixtures on Q6.
7. Tests. Section G1, every row that says "read the view" or "the write is
   refs rows": `test_arc_synthetic.py:141-142`, `:401-404`;
   `test_artefact_quality.py:140-152`; `test_onboarding_phases.py:953-973`,
   `:1137`, `:1564-1566`, and the `observed` asserts; `test_t0_sandbox.py:142`,
   `:158`, `:208`; `test_glossary_senses.py:449-451`; `test_laws.py:225-236`;
   `test_identity.py` picks up the new table. New tests: the view's three
   values from three seeded refs; the precedence of H2; a statement that
   leaves `ratified` drops its items to `reasoned`; the cascade wake carries
   row ids. Run `tests/rota/` with the recorder off.
8. Briefs. `rota/roles/prompts/terminologist/base.md:13-14`, `:36` (Q12).
   Optional: `terminologist/relay.md:8-9`, `architect/relay.md:8-9`,
   `liaison/observed_entries.md:4`. Nothing else, on Q10 and Q11.
9. Docs. `rota/LAWS.md:277-295` (the `cited` amendment becomes a basis),
   `:378`, `:380` (law 11's check becomes "every provenance is a view over
   `refs`"); `rota/TESTS.md:93-105`, `:318`; `rota/DECISIONS.md:750`,
   `:897`, `:919` (dated notes); `rota/HANDOFF.md:147-150`;
   `rota/ONBOARDING.md:69`, `:1146`; `rota/ANSWER_KEY.md:74-75`, `:106`;
   `rota/design/graph.json:64`, `:76`, `:94`; `rota/SEAT.md:465`, `:563`.
10. Re-record. Back up `tests/rota/cassettes.db` first. Re-create
    `.rota/clickI_warm.db` from a fresh boot.

Cases that re-record on the recommended path, 13, all on
`terminologist/base.md`:

| Case | file | mode |
|---|---|---|
| `L1-TE-answer-an-inquiry-read-only` | `tests/rota/cases/l1_answers.yaml` | ask |
| `L1-TE-answer-the-architects-question` | `l1_answers.yaml` | question |
| `L1-TE-log-the-word-you-took-one-way` | `l1_generators.yaml` | deliver |
| `L1-TE-a-standard-definition-is-not-automatically-ours` | `l1_researcher.yaml` | answer |
| `L1-TE-a-new-behaviour-is-a-new-callable` | `l1_surface.yaml` | criteria |
| `L1-TE-amend-glossary` | `l1_terminologist.yaml` | deliver |
| `L1-TE-specify-criteria` | `l1_terminologist.yaml` | criteria |
| `L1-TE-answer-a-term-question` | `l1_terminologist.yaml` | question |
| `L1-TE-challenge-an-unusable-item` | `l1_terminologist.yaml` | ask |
| `L1-TE-the-words-are-already-defined` | `l1_terminologist.yaml` | deliver |
| `L1-TE-a-rung-for-a-question-the-principal-asked` | `l1_unresolved.yaml` | unresolved |
| `L1-TE-adopt-what-the-principal-approved` | `l1_unresolved.yaml` | relay |
| `L1-TE-repair-the-criterion-the-tester-cannot-encode` | `l1_unresolved.yaml` | criterion_repair |

Also check `L3-ratified-statement-becomes-a-term` (`l3_handoffs.yaml`), which
routes through a Terminologist deliver, and `L1-AR-adopt-what-the-principal-approved`
if `architect/relay.md` changes.

Cases that re-record in addition if the loader does not translate the
seeds (Q9), 30: `G1-a-ratified-conflict-is-caught-by-the-owner`,
`L1-AR-a-dead-end-is-reported-not-sat-on`, `L1-AR-answer-a-question-read-only`,
`L1-AR-find-against-a-constraint`, `L1-AR-route-an-escalation`,
`L1-DV-apply-the-answer-and-carry-on`, `L1-DV-elect-on-a-revoked-item`,
`L1-DV-give-the-new-parameters-defaults`, `L1-DV-restore-what-the-finding-names`,
`L1-LI-present-the-touch`, `L1-LI-surface-a-quarantined-message`,
`L1-TE-a-new-behaviour-is-a-new-callable`,
`L1-TE-a-rung-for-a-question-the-principal-asked`,
`L1-TE-a-standard-definition-is-not-automatically-ours`,
`L1-TE-adopt-what-the-principal-approved`, `L1-TE-answer-a-term-question`,
`L1-TE-answer-an-inquiry-read-only`, `L1-TE-answer-the-architects-question`,
`L1-TE-put-a-word-with-two-senses-to-the-principal`, `L1-TE-specify-criteria`,
`L1-TE-the-words-are-already-defined`, `L1-TS-apply-a-term-and-write-the-test`,
`L1-VK-amend-a-contested-item`, `L1-VK-amend-a-contested-item-from-a-verdict`,
`L1-VK-reorient-the-account`, `L1-VK-slice`, `L1-VK-submit-drafts-together`,
`L2-AR-place-a-block-developer-could-not`,
`L3-a-maintainers-question-reaches-the-owner`,
`L3-scope-becomes-a-ticket-with-criteria`. Nine of them are in the 13
above, so the union is 43.

Cases that re-record if a result shape changes (against Q10), 75: every
case whose latest run called `glossary.consult`, `glossary.lookup`,
`model.consult`, `model.load`, `frame.load`, `criteria.load`,
`challenge.load`, `glossary.synthesise` or `glossary.same`, plus the 7 that
render an item row. The list is reproducible from `case_runs` and the case
files with the script in this survey's transcript.
