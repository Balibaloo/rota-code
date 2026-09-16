# Scope of the `reasoned` rename (frame 20)

Written 2026-09-16 by the scope agent. Read-only survey of the tree at
`5a8c320` plus the uncommitted `tests/rota/walks.jsonl`.

Summary: 5 schema columns. 13 writer sites, of which 4 change and 4 change
value with no code edit. 19 reader sites, of which 4 change. 10 brief lines in
9 files, of which 2 lines in 1 file must change, and 13 cases re-record. 48
test files mention the value, and 6 assertions change. 18 doc lines. The rename
is forward-only: 9 run databases carry seat-written `decided` rows and their
CHECK constraints reject `reasoned`.

The ruling: a record is `observed` (from the code or the world), `reasoned` (a
seat's own inference, written in the same session with the reason on file) or
`decided` (rests on a ruling of the Principal). `rota/LAWS.md:279-285` and
`plans/composition.md:58-59` already carry the words.

The one source of the value is `rota/core/runner.py:1579`. A session's
provenance is `observed` on an onboarding tick and `decided` on every other
wake. Every owner write copies `ctx.provenance`. So the rename is one word at
the source, plus the defaults, the derivation in `glossary.synthesise`, and the
readers that compare against `'decided'` to protect a row.

## 1. Schema

Five columns hold a provenance value. No table has a `cited` writer outside
`constraints` and `glossary_terms`.

| Item | file:line | today | after the rename | note |
|---|---|---|---|---|
| `items.provenance` CHECK | `rota/core/schema.sql:54` | `('observed','decided','cited')` | add `'reasoned'` | the Vision Keeper writes `ctx.provenance` here |
| `glossary_terms.provenance` CHECK | `rota/core/schema.sql:83` | `('observed','decided','cited')` | add `'reasoned'` | the Terminologist writes `ctx.provenance` here |
| `constraints.provenance` CHECK | `rota/core/schema.sql:125` | `('observed','decided','cited')` | add `'reasoned'` | the Architect writes `ctx.provenance` or `cited` here |
| `model_areas.provenance` DEFAULT + CHECK | `rota/core/schema.sql:142-143` | `DEFAULT 'observed'`, `('observed','decided','ratified')` | add `'reasoned'` | `model.account` writes `ctx.provenance or "observed"` (`api.py:2177`); nothing writes `'ratified'` |
| `frame_rulings.provenance` CHECK | `rota/core/schema.sql:725` | `('observed','decided')` | no change | the judge writes `observed`; a principal's ruling is `decided`; no code writes `decided` today (see Q3) |
| comment | `rota/core/schema.sql:698-699` | judge `observed`, ruling `decided` | no change | describes `frame_rulings`, still true |
| comment | `rota/core/schema.sql:723-724` | "Law 11's words" | no change | still true for `frame_rulings` |

`CREATE TABLE IF NOT EXISTS` does not alter an existing table. An existing
database keeps its old CHECK. See section 7.

## 2. Writers

`rota/core/runner.py:1579` sets `provenance` for the session. `sandbox.build`
copies it into `Ctx`. Every owner write copies `ctx.provenance`. The Liaison
writes no provenance-bearing row: `rulings.rule` (`api.py:4674`) writes the
`rulings` table, which has no provenance column, and `land()` in
`principal.py` writes `decisions` and approvals.

| Item | file:line | today | after the rename | note |
|---|---|---|---|---|
| the source | `rota/core/runner.py:1579` | `"observed" if wake.kind in ONBOARDING_TICKS else "decided"` | `... else "reasoned"` | every role, every non-onboarding mode; the one line that matters. Update the comment at `:1575-1576` |
| `Ctx.provenance` default | `rota/roles/api.py:48` | `"decided"` | `"reasoned"` | reached by tests that build `Ctx` directly; update the docstring at `:42-47` |
| `sandbox.build` default | `rota/core/sandbox.py:450` | `provenance: str = "decided"` | `"reasoned"` | reached by `build(role, db)` in tests |
| `problem.assert` | `rota/roles/api.py:665` | writes `ctx.provenance` | no code change; value becomes `reasoned` on deliver, contested, challenge, elect, propose, answer, question, unresolved, exhausted | Vision Keeper. Rests on the seat's reading of a statement, not on a ruling |
| `glossary.amend` | `rota/roles/api.py:1353` | writes `ctx.provenance` | no code change; value becomes `reasoned` outside `define`/`survey` | Terminologist deliver, criteria, answer, question, ask, unresolved, criterion_repair |
| `glossary.synthesise` | `rota/roles/api.py:1528` | `"decided" if any row is decided else "observed"` | `decided` if any row is `decided`; else `reasoned` if any is `reasoned`; else `observed` | Terminologist term_collision. Update the comment at `:1520-1527` |
| `model.constrain` | `rota/roles/api.py:2065` | `"cited" if cited else ctx.provenance` | no code change; value becomes `reasoned` outside survey | Architect deliver, answer, structural_review, escalate |
| `model.account` | `rota/roles/api.py:2177` | `ctx.provenance or "observed"` | no code change; needs `'reasoned'` in the `model_areas` CHECK | Architect. Reachable outside onboarding only if a `.tools` file grants it |
| `_adopt_rows` | `rota/roles/api.py:842` | writes `"decided"` | stays `decided` | `glossary.adopt` (`:852`) and `model.adopt` (`:858`) in the owners' `relay` mode. `_ruled_ids` (`:797-819`) checks the principal's verdict on the cause chain. This is the ruling path |
| `frame.assign` | `rota/roles/api.py:6728` | writes `"observed"` | stays (see Q3) | the Architect's frame judge |
| constraint zero | `rota/onboarding/boot.py:245` | `'observed'` literal | stays | written outside any session |
| `ENUMS["provenance"]` | `rota/core/sandbox.py:80` | `("observed", "decided")` | add `"reasoned"` | dormant: no op takes `provenance` as an argument. Update for consistency |
| `_PROVENANCE_WORDS`, `_FRAME_WORDS` | `rota/roles/api.py:5225, 5230` | `{"observed", "decided", "provenance"}` | add `"reasoned"` | stops a model naming a sense after the provenance word |

Who writes `decided` after the rename: `_adopt_rows` only, on a verdict the
op verifies. Who writes `reasoned`: every owner write on a non-onboarding wake.

## 3. Readers

| Item | file:line | today | after the rename | note |
|---|---|---|---|---|
| found never overwrites decided | `rota/roles/api.py:475-481` | an `observed` session refuses to amend an item `WHERE provenance = 'decided'` | `IN ('decided', 'reasoned')`; reword the note "is decided by the principal" | without the change, reorient overwrites a Vision Keeper's `reasoned` item with the code's account. tipsU (2026-09-09) is the measured case |
| the same words on an observed row | `rota/roles/api.py:487-500` | a non-observed session refuses to restate an `observed` row | no change | comment at `:487` says "A decided wake writes decided"; reword |
| `problem.baseline` | `rota/roles/api.py:750` | `provenance = 'observed'` only | no change | `reasoned` rows are not baseline |
| adopt moves observed only | `rota/roles/api.py:839` | `if row["provenance"] != "observed": skipped` | no change in frame 20 (see Q1) | a `reasoned` row cannot be adopted today |
| slicing refuses observed | `rota/roles/api.py:2715-2719` | `== "observed"` raises; message says "the decided ones" | branch unchanged; message becomes "the ones the principal asked for" | `reasoned` items slice, same as `decided` |
| frame ruling outranks | `rota/roles/api.py:6716` | `== "decided"` refuses reassign | no change | a principal's frame ruling |
| frame ruling depth tie | `rota/onboarding/areas.py:69` | `decided` outranks at equal depth | no change | `frame_rulings` has no `reasoned` |
| TERMINAL | `rota/core/predicates.py:154-157` | `decided` terminal on items, glossary_terms, constraints | add three `reasoned` entries with a reason | `check_terminal_states` (`:1597-1618`) reads the CHECK values from `schema.sql` (`:1573-1590`). A CHECK value with no drain and no TERMINAL entry fails `tests/rota/test_predicates.py:28` |
| `observed_entries` | `rota/core/predicates.py:488-491, 526, 564` | drains `observed` only | no change | `reasoned` rows are never presented as onboarding finds |
| slicing predicate | `rota/core/scheduler.py:250` | `i.provenance != 'observed'` | no change | `reasoned` slices |
| observed item words | `rota/core/scheduler.py:600` | reads `observed` items | no change | |
| signoff page | `rota/roles/principal.py:323` | `observed` under "It does today", else "It would" | no change | `reasoned` renders as a plan |
| contest skips observed | `rota/roles/principal.py:668` | a contest on an `observed` item is not relayed | no change | a `reasoned` item takes the contest |
| cockpit row lists | `rota/cockpit/inspect_api.py:27-28` | column shown raw | no change | display only |
| cockpit provenance panel | `rota/cockpit/inspect_api.py:379`, `rota/cockpit/static/panels.js:1339` | the cause chain; no branch on the value | no change | `tests/rota/provenance_check.js` checks the chain, not the value |
| `onboard_run` print | `rota/tools/onboard_run.py:185, 191` | `[cited]` tag; `provenance:9s` | no change | `reasoned` is 8 characters |
| unbacked citations | `rota/testkit/artefacts.py:271` | `cited` only | no change | |
| `split_senses` | `rota/tools/split_senses.py:161-162` | a historical rename table names `'decided'` | no change | archive tool |

## 4. Briefs

The Terminologist's `base.md` is the base of every Terminologist mode that
has no `<mode>.base.md` (`rota/roles/prompts.py:68-83`). `survey`, `define`
and `term_collision` carry their own base and do not see the change.

| Item | file:line | today | after the rename | note |
|---|---|---|---|---|
| Terminologist doctrine | `rota/roles/prompts/terminologist/base.md:13-14` | "A term is `decided` (someone chose it, reason on file) or `observed`" | "`reasoned` (you inferred it, reason on file), `observed` (found in the code), or `decided` (the principal ruled)" | must change |
| Terminologist doctrine | `rota/roles/prompts/terminologist/base.md:36` | "A glossary entry marked `decided` means the reason is on file, and you are the one who has to put it there" | `reasoned` | must change |
| Liaison onboarding page | `rota/roles/prompts/liaison/observed_entries.md:4` | "found, not decided" | optional: "found, not chosen" | prose, not a value; a change re-records `L1-LI-present-what-onboarding-only-observed` |
| Terminologist relay | `rota/roles/prompts/terminologist/relay.md:8` | adopt moves `observed` to `decided` | no change | the principal's ruling |
| Architect relay | `rota/roles/prompts/architect/relay.md:8` | same | no change | same |
| Architect frame | `rota/roles/prompts/architect/frame.md:20` | "a decided row outranks you" | no change | the principal's ruling |
| Vision Keeper survey | `rota/roles/prompts/vision_keeper/survey.md:8-9, 16, 19-20` | `observed` | no change | |
| Vision Keeper orient | `rota/roles/prompts/vision_keeper/orient.md:23` | "Everything here is observed" | no change | |
| Terminologist answer | `rota/roles/prompts/terminologist/answer.md:16-17` | `cited` | no change | |
| Liaison verdict_signoff | `rota/roles/prompts/liaison/verdict_signoff.md:18` | "provenance and approval are the owners' artefacts" | no change | |

Cases that re-record for `terminologist/base.md` (13):

| Case | file | mode |
|---|---|---|
| `L1-TE-answer-an-inquiry-read-only` | `tests/rota/cases/l1_answers.yaml` | ask |
| `L1-TE-answer-the-architects-question` | `tests/rota/cases/l1_answers.yaml` | question |
| `L1-TE-log-the-word-you-took-one-way` | `tests/rota/cases/l1_generators.yaml` | deliver |
| `L1-TE-a-standard-definition-is-not-automatically-ours` | `tests/rota/cases/l1_researcher.yaml` | answer |
| `L1-TE-a-new-behaviour-is-a-new-callable` | `tests/rota/cases/l1_surface.yaml` | criteria |
| `L1-TE-amend-glossary` | `tests/rota/cases/l1_terminologist.yaml` | deliver |
| `L1-TE-specify-criteria` | `tests/rota/cases/l1_terminologist.yaml` | criteria |
| `L1-TE-answer-a-term-question` | `tests/rota/cases/l1_terminologist.yaml` | question |
| `L1-TE-challenge-an-unusable-item` | `tests/rota/cases/l1_terminologist.yaml` | ask |
| `L1-TE-the-words-are-already-defined` | `tests/rota/cases/l1_terminologist.yaml` | deliver |
| `L1-TE-a-rung-for-a-question-the-principal-asked` | `tests/rota/cases/l1_unresolved.yaml` | unresolved |
| `L1-TE-adopt-what-the-principal-approved` | `tests/rota/cases/l1_unresolved.yaml` | relay |
| `L1-TE-repair-the-criterion-the-tester-cannot-encode` | `tests/rota/cases/l1_unresolved.yaml` | criterion_repair |

Also check `L3-ratified-statement-becomes-a-term` in
`tests/rota/cases/l3_handoffs.yaml`. It routes through a Terminologist deliver.

Fixture rows are a second cause of re-records. 80 of 127 cases seed a
`provenance: decided` row. The brief renders `items.provenance`
(`rota/core/runner.py:988`) and `glossary.consult` and `model.consult` return
the column. A fixture rename changes the prompt hash. No `expect:` block checks
a provenance value. See Q2.

## 5. Tests

48 test files mention `decided` or `provenance`. Most are seed rows in
`INSERT` statements. `decided` stays a legal value, so the seeds keep passing.
Six assertions change.

| Item | file:line | today | after the rename | note |
|---|---|---|---|---|
| staged write shape | `tests/rota/test_t0_sandbox.py:142, 158` | expects `"provenance": "decided"` from `build("vision_keeper", db)` | `"reasoned"` | the default flips |
| terminal states | `tests/rota/test_predicates.py:28, 73, 87` | every CHECK value drained or terminal | passes once `TERMINAL` has the three `reasoned` entries | fails first if the schema lands before `predicates.py` |
| who writes decided can author | `tests/rota/test_laws.py:225-236` | roles that write `decided` can write `decisions` | rename to `reasoned`; the invariant is the same | the law's "reason on file" |
| observed never amends decided | `tests/rota/test_onboarding_phases.py:953-973` | seeds `decided`, expects the note to say `decided` | keep; add a twin that seeds `reasoned` and expects the guard to hold | the note text at `api.py:480` changes with it |
| frame ruling outranks | `tests/rota/test_onboarding_phases.py:1564-1566` | seeds a `decided` frame ruling; `match="decided\|outranks"` | no change | `frame_rulings` keeps `decided` |
| observed becomes decided | `tests/rota/test_arc_synthetic.py:318-404` | adopt moves `g1`, `k1` to `decided` | no change | the ruling path |
| observed asserts | `tests/rota/test_onboarding.py:296`; `tests/rota/test_onboarding_phases.py:422, 451, 1164, 1551` | `== "observed"` | no change | |
| provenance as a sense | `tests/rota/test_glossary_senses.py:108` | `"provenance" in msg` | no change | add a case for `sense="reasoned"` if `_PROVENANCE_WORDS` grows |
| a new test | none | | a non-onboarding wake writes `reasoned`; an onboarding tick writes `observed` | pins `runner.py:1579`. `tests/rota/test_runner.py:570` is the nearest neighbour |
| cockpit provenance | `tests/rota/test_provenance.py:81, 177` | seeds `decided` via `Write` | no change | the chain, not the value |

Seed-only files (no assertion on the value, no change needed):
`test_arc_seam.py`, `test_challenge_evidence.py`, `test_chaos_confirm.py`,
`test_chaos_inquiry.py`, `test_criteria_surface.py`, `test_delivery.py`,
`test_desk_guards.py`, `test_developer_expect.py`, `test_frontier.py`,
`test_greenfield.py`, `test_night46_context.py`, `test_pushes.py`,
`test_signoff_assumptions.py`, `test_steering.py`, `test_t0_plumbing.py`,
`test_touch_note.py`, `test_triage_fork.py`, `test_turns.py`, and the rest of
the 48.

## 6. Docs

`rota/LAWS.md:279-285` and `plans/composition.md:58-59` already say
`reasoned`. `plans/greenfield-setup.md:5-6, 27, 61-64` already use the word.
Rulings in `rota/DECISIONS.md` keep their wording; add a dated note.

| Item | file:line | today | after the rename | note |
|---|---|---|---|---|
| law 11 summary | `rota/HANDOFF.md:147-150` | two values | three values, `decided` reserved for the principal | |
| partition pin | `rota/HANDOFF.md:301, 434` | "a `decided` entry" | stays: the principal pins | check the sentence still says who |
| schema sketch | `rota/TESTS.md:93` | `provenance[observed\|decided]` | `provenance[observed\|reasoned\|decided\|cited]` | `rota/tools/vocabulary.py:197` reads this file as a word list, not as enums |
| seat answers | `rota/SEAT.md:563` | "with provenance `decided` and author `principal`" | no change | the principal's rows |
| law 11 record | `rota/DECISIONS.md:752-757` | "`decided` is the reason on file, written by the decider" | keep; add a 2026-09-16 note pointing at `rota/LAWS.md:279` | a ruling record |
| rulings in config | `rota/DECISIONS.md:897` | "provenance-bearing decision record" | no change | |
| adopt stamp | `rota/DECISIONS.md:919` | "stays `provenance='observed'`" | no change | |
| gauge | `rota/ONBOARDING.md:586` | "observed:decided" | "observed:reasoned:decided" | |
| signoff spine | `rota/ONBOARDING.md:689, 701` | "`observed` becomes decided", "81 rows moved to `decided`" | no change | the ruling path, historical |
| frame rulings | `rota/ONBOARDING.md:1147` | "decided outranks observed" | no change | |
| approve confirms | `plans/principal-flow.md:93` | "Approve confirms provenance decided" | say what approve does to a `reasoned` row once Q1 is ruled | |
| shape provenance | `plans/principal-flow.md:211-213` | `observed` then `decided` on approval | add `reasoned` for a drafted row | |
| law 11 draft | `plans/decisions-rulings-draft.md:137` | the `cited` amendment | add the `reasoned` ratification | |
| graph note | `rota/design/graph.json:94` | "decided (authored reason on file) or observed" | three values | the cockpit shows this note |
| graph page | `rota/design/team-graph.html:189` | same text | same | generated from the graph? check before editing by hand |
| story | `rota/design/stories.json:1014`; `rota/design/team-graph.html:528` | "observed-to-decided ratio" | "observed to reasoned to decided" | |
| completion probe | `rota/COMPLETION.md:400-401, 432` | "provenance chain" | no change | means the cause chain |

## 7. Migration

The rename is forward-only. No data migration is needed for the cassettes. A
data migration is not possible for old run databases without a table rebuild,
and the design refuses one (`rota/cli.py:273-276`: databases are throwaway and
rebuilt by `init_db` at boot).

| Item | file:line | today | after the rename | note |
|---|---|---|---|---|
| run databases | `.rota/clickI_n42.db`, `clickI_n70_merged.db`, `clickI_warm.db`, `tipsAL.db`, `tipsAN.db`, `tipsAP.db`, `tipsAR.db`, `tipsAS.db` (`tipsAQ.db` has none) | seat-written `decided` rows: clickI 22-23 glossary terms, 21 constraints, 1-2 items, 1 area | readers treat `decided` and `reasoned` alike except `adopt` and the frame; the rows read as before | the old CHECK stays in the file. A new `reasoned` write fails at commit with an IntegrityError |
| warm snapshots | `.rota/clickI_warm.db` + `clickI_warm.json` | old CHECK | re-create from a fresh boot after the schema lands | a run started from it cannot write `reasoned` |
| schema apply | `rota/core/db.py:111-114` | `executescript` of `CREATE TABLE IF NOT EXISTS` | no change | does not alter an existing table |
| precedent | `57823c1` | `cited` was added to the CHECK with no migration | same | |
| cassettes | `tests/rota/cassettes.db` (18166 rows) | 3017 rows carry `` `decided` `` in the system prompt; 4648 carry the word anywhere | no migration. A changed brief changes the key, misses, and re-records. Stale rows stay with `hits = 0` | the register (`case_runs`) is keyed by `prompt_hash`; new recordings are new rows |
| cassettes fixture | `tests/rota/cassettes.json` | no `decided` | no change | |
| cases | `tests/rota/cases/*.yaml` | 80 cases seed `decided` | see Q2 | |
| walks | `tests/rota/walks.jsonl` | one hit, in a prose note | no change | |

## Open questions for the frame

Each needs a ruling before the corresponding line lands.

Q1. Does a principal's approval promote a `reasoned` row to `decided`?
Today `problem.set_approval` (`api.py:677`) leaves provenance alone, and
`_adopt_rows` (`api.py:839`) moves `observed` rows only. `plans/greenfield-setup.md:61`
and `plans/principal-flow.md:93` expect promotion. Recommended: not in frame
20. `approval` already records the ruling on items. Push a follow-up frame
that lets `adopt` take `reasoned` rows and wires the signoff verdict to it.

Q2. Do the 80 case fixtures that seed `decided` change to `reasoned`?
Recommended: no. `decided` stays a legal value. The fixtures model rows the
principal approved (`approval: approved`). A rename re-records 80 cases for no
behaviour change. Change a fixture only where a case's premise is a seat's
inference and the case is re-recording anyway.

Q3. The frame judge writes `observed` (`api.py:6728`, `schema.sql:723-724`).
By the new words a judge's classification is a seat's inference. Recommended:
leave `frame_rulings` alone in frame 20. It is a separate ruling, and
`areas.py:69` and `api.py:6716` depend on the two-value shape.

Q4. Old run databases cannot take a `reasoned` write. Recommended: accept.
Say so in the status line. Re-create the warm snapshot after the schema lands.

## Change set, in landing order

1. Schema. `rota/core/schema.sql:54, 83, 125, 143`: add `'reasoned'`.
2. Readers that gate. `rota/core/predicates.py:154-157`: three `reasoned`
   TERMINAL entries. `rota/roles/api.py:475-481`: `IN ('decided', 'reasoned')`
   and the note text. `rota/roles/api.py:2719`: the message.
3. Writers. `rota/core/runner.py:1579` and its comment at `:1575-1576`.
   `rota/roles/api.py:48` and the docstring at `:42-47`. `rota/core/sandbox.py:450`.
   `rota/roles/api.py:1528` three-way derivation and the comment at `:1520-1527`.
   `rota/core/sandbox.py:80`. `rota/roles/api.py:5225, 5230`. Comment at
   `rota/roles/api.py:487`.
4. Tests. `tests/rota/test_t0_sandbox.py:142, 158`. `tests/rota/test_laws.py:225-236`.
   A `reasoned` twin beside `tests/rota/test_onboarding_phases.py:953`. A new
   test for `runner.py:1579` beside `tests/rota/test_runner.py:570`. Run
   `tests/rota/` with the recorder off.
5. Briefs. `rota/roles/prompts/terminologist/base.md:13-14, 36`. Optional:
   `rota/roles/prompts/liaison/observed_entries.md:4`.
6. Docs. `rota/HANDOFF.md:147-150`. `rota/TESTS.md:93`. `rota/DECISIONS.md:752`
   (a dated note). `rota/ONBOARDING.md:586`. `plans/principal-flow.md:93, 211-213`.
   `plans/decisions-rulings-draft.md:137`. `rota/design/graph.json:94`.
   `rota/design/team-graph.html:189, 528`. `rota/design/stories.json:1014`.
7. Re-record. The 13 Terminologist cases in section 4, by exact id. Then
   `L3-ratified-statement-becomes-a-term`. Back up `tests/rota/cassettes.db`
   first. Re-create `.rota/clickI_warm.db` from a fresh boot.
