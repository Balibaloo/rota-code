# The demand read: what every seat and page needs from onboarding (2026-11-03)

Reader: one read-only agent at 7381ca1f on `rota/foundation`. Copies: `dry3w7` in the scratchpad of ce483c7b, `dry2w5` and `dry1w14` in the scratchpad of 208997ee. The probes are `loads.py` and `supply.py` in `.../ce483c7b-.../scratchpad/demand/`. No live database was opened and no model session started.

## Result

On all three merged dry runs, no delivery seat acted on an understanding row: the index and the request's own words carried each merge (observed: section 2). Three of the four doors that hand understanding to delivery are broken in the wiring, not in the rows. The pushed `glossary.lookup` says "the rows this wake named are gone." on 21 delivery sessions, the Developer's `model.load` got 14 calls and none with a constraint id, and the structural review saw only `k0` "this area has not been surveyed" on 3 of 3 batches (observed: section 2). The demand that the briefs state most strongly is for external commitments, and the run observed the icalendar commitments ("RFC 5545 compatible", the timezone back ends, the import shortcuts) but filed them as 16 README-against-code `conflict` ledger rows that no page and no seat read (observed: `ledger` in dry3w7). The supply is front-loaded: on dry3, 153 of 206 sessions and about 112 of 132 model minutes were onboarding, and all four walls that touched understanding pushed supply at the principal that he did not ask for (observed: section 4; reasoned: section 6). The session's reading holds in part: the survey was built from what the source offers, but the consumers do not even take what exists, because the doors between them do not connect (reasoned: sections 2 and 6).

## 1. The consumers

"Job" means a brief, `ROLES.md` or the composition asks for the read. "Table" means the read arrives only because `push_working_set` runs every read that takes no argument (observed: `rota/core/runner.py` 4313 to 4345, "Callable-with-no-arguments is the honest rule").

| Seat or page | Moment | Question it asks | Record and table | File and line | Source |
|---|---|---|---|---|---|
| Architect | `guess` | Which files will this request touch? | grains, `code_index` through `code.callables` and `code.probe` | `rota/core/predicates.py` 319 to 345; `architect/guess.tools` | Job: "the architect owns the guess" (ruled 2026-10-18, predicates.py 322) |
| Terminologist | `criteria` | What does each word of the item mean here, so the criterion says the right thing? | `glossary_terms` through `glossary.consult` and `glossary.lookup`; the item; `code.callables` | predicates.py 598 to 603; runner.py 4413 to 4423 and 4440 to 4470 | Job: "Every criterion carries `term_refs` naming the glossary entries it relies on" (`terminologist/criteria.md` 8) |
| Developer | `batch_start` | Which commitments bind what I am about to touch? | `constraints` through `model.load(ids)` | `rota/roles/api.py` 4512 to 4521; `developer/batch_start.md` 14 | Job: "`model.load` — the constraints in play. These are external commitments" |
| Developer | `batch_start` | What does a term of the criterion mean? | `glossary_terms` through `glossary.lookup` | api.py 3655 to 3669; `batch_start.md` 16 | Job: "`glossary.lookup` any term you are about to encode" |
| Developer, Tester | every delivery wake | What do the criteria say, and which terms do they rely on? | `criteria` with `term_refs` from `refs` | api.py 7461 to 7509 | Job (the criteria are "the specification", `batch_start.md` 12) |
| Developer | `batch_start`, `tests_failing` | Where does the work live? | `code_index` through `code.probe` | api.py 18049 | Job (`batch_start.md` step 4) |
| Tester | `tests_missing` | What does the criterion's term mean? | `glossary_terms` through `glossary.lookup` | `tester/tests_missing.md` 27; `tester/base.md` 11 | Job: "Test the criterion's terms as the glossary defines them" |
| Critic | `review` | Does the diff meet the criteria? | `criteria`, `tests`, the diff. No understanding row. | `critic/review.tools`; `critic/base.md` 12 | Job: "Anything the diff does outside the criteria is a remark" |
| Critic | `challenge` | Does an onboarding claim survive the source? | `constraints`, `glossary_terms` claims through `challenge.load` | api.py 19419; predicates.py 2174 | Job (`critic/challenge.base.md` 1 to 6). The consumer is inside onboarding. |
| Architect | `structural_review` | Does the diff satisfy or violate each constraint it touched? | `constraints`, `constraint_bindings` through `model.consult` and `constraints_for_grains` | predicates.py 1580; api.py 4487 to 4509; `rota/core/scheduler.py` 3183 | Job (`architect/structural_review.md` 6 to 9; ROLES "constraints that are external commitments") |
| Architect | `grouping` | Which tickets go in one batch? | `constraints` index through `model.consult`, pushed | `architect/grouping.tools` | Table: `grouping.md` names no constraint (observed: grep) |
| Vision Keeper | `signoff`, `slicing` | What did the principal ask for, against the project today? | `items`, the description included, through `problem.consult` | api.py 2491 | Job |
| Liaison and principal | the description present, m4 | What does the project do today? | `items` with `is_description` | predicates.py 2090 (`orient`); `rota/roles/principal.py` 2455, `ACCOUNT_TODAY` | Job: "the summary stays, presented as the project today" (ruled 2026-10-17 04:33, principal.py 2453) |
| Liaison and principal | the account page, `observed_entries` | Does the principal confirm the team's rows? | `glossary_terms`, `constraints`, `model_areas` | predicates.py 669 to 806; principal.py 2451, `TEAM_NOTES` | Table: the docstring says "nothing was ever going to ask the principal to confirm them, so `observed` was a state with no exit" (predicates.py 673) |
| Liaison and principal | `term_collision` pages | Which of two senses of one word stands? | `glossary_terms` | predicates.py 355 | Job of the glossary owner (ROLES 150); the page to the principal is the predicate's |
| Liaison and principal | the present's touch line, `touch_note` | What will this change touch, what nobody surveyed, and which commitments bind it? | `batch_touch`, `constraint_bindings`, `k0` | predicates.py 1024; `rota/core/lifecycle.py` 577; principal.py 3281 to 3315 | Job: "expected paths, guessed symbols, unsurveyed ground, bound commitments" (ROLES 93, ruled P4 2026-09-03) |
| Principal | the Done line | What is done? | `batches`, `ledger`. No understanding row. | principal.py 340 to 390 | Job |
| Liaison | `agenda` | Which open ledger rows does the principal see? | `ledger`, the reconcile `conflict` rows included | scheduler.py 1219 to 1245 | Job (law 6, scheduler.py 1236) |

## 2. What each consumer got on the merged batches

dry3, icalendar, bg_1, `canonical_order_duplicate_keys` (observed: `loads.py` on dry3w7, the first turn of each session and `tool_calls`).

| Consumer | Session | Rows loaded | Did a row change the act? |
|---|---|---|---|
| Architect guess | s164 | `code.callables` 4,338 characters of index rows, `code.probe`. 0 glossary, 0 constraint, 0 area rows. | Yes, the index. The door refused "canonsort_keys names no path ... The index holds src/icalendar/caselessdict.py::canonsort_keys", and the second call used that form. The target came from the request's words, "icalendar.caselessdict.canonsort_keys()". |
| Terminologist criteria | s171 | `glossary.consult` 106 rows, 10,402 characters; `glossary.consult(terms=['canonical_order'])`; the pushed `glossary.lookup` was "the rows this wake named are gone." | Partly. The three criteria restate the item's words and carry `term_refs` `["canonical_order"]`. That row says "A class variable in the Calendar component that defines the preferred sequence of properties", and the request means the parameter of `canonsort_keys`, "The preferred order for leading keys" (observed: `caselessdict.py` line 30 at the key's root). |
| Architect grouping | s172 | `model.consult` 117 constraint rows; `model.consult(grains=['calendar_canonical_order'])` | No. One ticket, one batch. |
| Developer | s180 | `criteria.load` 3 rows; `glossary.lookup` "the rows this wake named are gone."; `model.load(ids=['c1', 'c2', 'c3'])`, criterion ids, so 0 constraint rows | No understanding row. The code came from the criteria and `code.source`. |
| Tester | s181, s183 | `criteria.load`, the same "gone" note | No. The tests came from the criteria. The clarify m38 went to the Terminologist s182, who looked up `duplicate keys` and missed. |
| Critic review | s187 to s189 | `criteria.load`, `tests.load`, the diff | None loaded, by design. |
| Architect structural review | s190 | `model.consult` pushed: `[{"id": "k0", "headline": "this area has not been surveyed", ...}]` and nothing else | No. It filed `f1`, `k0`, `satisfied`. The headline is false: all 22 areas have a survey record (observed: the key score, section 4). |
| Liaison touch note | s179, m40 | the touch set | No commitment line. The constraint `icalendar_caselessdict` binds `docs/reference/api/icalendar.caselessdict.rst`, not the source file (observed: `constraint_bindings`). |
| Liaison pages | m4, m14, m16, m18, m26, m39 | 5 description items; 11 of 108 glossary rows; 2 of 119 constraints; 20 of 22 areas by name on any message | The principal said "ok" to m4. The four collision pages asked him about the team's duplicate rows. m39 carried the 235 names of a stopped step (observed: `messages.body_refs`; the key score, section 3). |

The structural review read `k0` because `k0` has no binding once every area is surveyed, and `constraints_for_grains` loads an unbound constraint as global, "unbound = global" (observed: scheduler.py 3196 to 3200; dry3w7 `k0` is the one unbound row; reasoned: the fail-safe turns the end of constraint zero into a false line).

dry2, tips, two batches (observed: dry2w5). Guesses s36 and s37 read the index only. Criteria s47 and s48 got the "gone" note. Developers s55, s63 to s65 called `model.load` with `['c_1', 'c_2', 'c_3']` and `['c_5', 'c_10']`, criterion ids. Structural review s62 saw `k0` only and filed `k0` `satisfied` twice. The request's words and the 29-grain index carried the merge.

dry1, click, bg_1 (observed: dry1w14). Five guesses read the index only. Developers s145, s192, s256 and s265 called `model.load` with `['bg_1']` or `['tk_1']`. 11 sessions got the "gone" note. Structural review s270 called `model.consult(grains=["src/click/termui.py"])`, got `k0` only, and filed `k0` `satisfied`. No constraint binds `termui.py`, and the 20 click constraints are class names such as `Argument` and `Command` (observed: `constraints`).

What carried the merge, all three runs: the request's own words named the function and the behaviour, and the index turned the name into a path (observed: the guesses and `batches.expect`). No survey row changed a delivery act on any run (observed: the tables above). Totals: the "gone" note on 21 sessions, 3 on dry3, 7 on dry2 and 11 on dry1; `model.load` 14 calls, 0 with a constraint id; structural review `k0` only, 3 of 3 (observed: a count over the first turns of the three copies).

## 3. What each consumer needs by its job and does not get

### The commitments first

The briefs that ask for commitments are the Developer, the structural review and the touch note (observed: section 1). The Tester's and the Critic's briefs ask for none: the Tester tests "the criterion's terms", and the Critic treats work outside the criteria as "a remark" (observed: `tester/base.md` 11, `critic/base.md` 12). So the demand that a Tester or a Critic knows what must not change comes from the composition and the walls, not from their briefs (reasoned: the composition holds "external commitments" as a record kind, and the request's own clause "sorts the keys as before otherwise" is a must-not-change statement that only criteria c2 and c3 carried).

What the Tester and the Critic need: for each touched source path, the commitments bound to it, each with the outside party, the observable behaviour that must hold, and a witness in the repository that a test can use (reasoned: a test guards a behaviour only when it can name the input and the expected output). No table holds the party, the behaviour or the witness today. `constraints` holds `headline`, `text` and `rationale_decision`, and its median body is 43 characters (observed: `pragma table_info(constraints)`; the key score, section 1).

The key's five commitments on icalendar as records (observed: `probes/ical/answer_key.yaml` 85 to 114; reasoned: the record shape).

| Commitment | Outside party | Behaviour that must hold | Witness | Binds |
|---|---|---|---|---|
| `rfc_5545_conformance` | every program that reads or writes .ics files | output parses as RFC 5545, input from other programs parses, lines fold at 75 octets | pyproject "RFC 5545 compatible parser and generator", `tests/calendars/*.ics` | `src/icalendar/parser/`, `cal/`, `prop/` |
| `the_pypi_package_and_import_surface` | importers on PyPI | `import icalendar`, the class shortcuts, `requires-python >=3.10` | pyproject, `src/icalendar/__init__.py` | `__init__.py`, `pyproject.toml` |
| `tzdata_and_dateutil_are_load_bearing` | users on Windows, recurrence users | zoneinfo falls back to tzdata, recurrence math uses dateutil | pyproject dependencies, `timezone/` | `src/icalendar/timezone/`, `prop/recur/` |
| `unknown_content_survives_round_trip` | anyone who round-trips another program's file | a value that fails to parse is kept as `vBroken` and written back | `vBroken`, the component `errors` list | `prop/`, `cal/component.py` |
| `the_cli_preview_entry_point` | shell users and scripts | the `icalendar` command keeps working | `icalendar = icalendar.cli:main` | `cli.py`, `pyproject.toml` |

The run saw the first three. The reconcile sessions wrote "The README says "The icalendar package is an RFC 5545 compatible parser and generator of iCalendar files."", "icalendar supports multiple timezone implementations, including zoneinfo, dateutil.tz, and pytz." and "the icalendar library provides shortcuts for importing its Python classes." as `conflict` rows of the ledger (observed: `l_bf39c83516`, `l_4bf2fc80bb`, `l_7dba4c3acc`). A README claim is filed as a disagreement with the code, not as a commitment, so no constraint and no binding came of it (reasoned: `reconcile` docstring, predicates.py 2110 to 2116, "A claim the account does not support is not merged -- it is a ledger entry").

### The other seats

- Developer: the bodies of the constraints bound to the touched grains, pushed, and the senses of the criteria's `term_refs`. Neither arrives. `model.load` needs ids the Developer never sees, because `batch_start.tools` has no `model.consult` (observed). The pushed lookup reads the wake's refs, `bg_1`, as glossary ids (observed: api.py 3662 to 3669).
- Tester: the senses of the criteria's `term_refs`. The same push sends "gone" (observed).
- Architect, structural review: the constraints bound to the diff's source paths. It gets `k0` only (observed).
- Terminologist, criteria: the sense of a term in the request's context. The glossary holds one sense per area, so a parameter that shares a name with a class variable gets the wrong row (observed: s171; reasoned).
- Liaison, touch note: the commitments of the touched path. None binds a source path that a request touched on the three runs (observed: m40; dry1 `termui.py` has no binding).

### The principal

By the composition, "The Principal holds the shape in their head. The structure holds it in rows" (observed: `plans/composition.md` 41 to 43). So he needs the description of the project today once, the touch line with the commitments a change risks, his own open questions, and the Done line (reasoned: the purpose line, "no work stays invisible"). He never asked to confirm the team's rows: the account page exists because `observed` "was a state with no exit" (observed: predicates.py 673 to 674). He never asked to rule on the team's duplicate terms: all four collisions on dry3 were one sense written twice (observed: the key score, section 3). He did rule that the election of the baseline is "the principal's call" (observed: frame 361, ruling of 2026-08-26), so a change to the account page needs his word (reasoned).

## 4. The supply

Sessions and model minutes are the sum of `turns.ms` per wake kind, not wall time (observed: `supply.py`). "dry3" is icalendar, "dry2" is tips, "dry1" is click.

| Producer | Writes | Table | Provenance | dry1 click | dry2 tips | dry3 icalendar | Read by |
|---|---|---|---|---|---|---|---|
| indexer | grains, edges, lexicon | `code_index`, `code_edges`, `code_lexicon` | observed | 0 sessions, 1,188 grains | 0, 29 grains | 0, 2,800 grains | guess, criteria, Developer probe, touch line. Carried every merge. |
| Architect `frame` | the partition | `model_areas` | observed | 1, 0.2 min | 1, 0.2 | 1, 0.2 | the survey wakes. No delivery seat. |
| Vision Keeper `orient`, `reorient` | the description | `items` `is_description` | observed | 2, 0.2 | 2, 0.2 | 2, 0.3 | m4, `problem.consult` |
| Vision Keeper `reconcile` | README against code | `ledger` `conflict` | reasoned | 39, 11.8 | 1, 0.1 | 41, 8.6 | `agenda` only. 0 of 16 on a page on dry3. **No consumer acted.** |
| Terminologist `define`, `survey` | terms | `glossary_terms`, `survey_records` | observed | 24, 2.1 | 8, 1.0 | 44, 4.8 | criteria (`term_refs`), collision pages, the account page |
| Terminologist `term_collision` | merges, pages | `glossary_terms`, `messages` | reasoned | 0 | 0 | 14, 2.6 | the principal. Duplicates only. |
| Architect `survey` | constraints, bindings, area accounts | `constraints`, `constraint_bindings`, `model_areas` | observed | 4, 4.6 | 2, 0.6 | 26, 46.5 | grouping (pushed, no effect), structural review (`k0` only), touch line (none bound). **No consumer acted.** |
| Architect `boundary` | outside-in constraints | `constraints` | observed | 3, 0.2 | 1, 0.0 | 3, 0.1 | as above |
| scheduler `constraint_zero` | `k0` bindings | `constraint_bindings` | reasoned | 0 | 0 | 0 | touch line; structural review reads the unbound `k0` as global |
| Critic `challenge` | verdicts on claims | `challenges` | reasoned | 34, 8.1 | 18, 1.5 | 17, 5.3 | no delivery seat observed. **No consumer acted.** |
| Liaison `blindspot` | what the run could not see | `ledger` `gap` | reasoned | 1, 0.8 | 1, 0.3 | 1, 0.2 | `agenda` |
| Liaison `observed_entries` | the account page | `messages` | the rows' own | 2, 0.4 | 1, 0.3 | 3, 43.0 | the principal. Walls 358 and 361. |

Onboarding share: dry3 153 of 206 sessions and about 112 of 132 model minutes; dry2 35 of 97 and about 4 of 22; dry1 110 of 311 and about 28 of 92 (observed: the sums of the rows above against `sessions` and `turns`).

Rows no consumer reads to effect: the `conflict` ledger rows, the 118 constraints and their bindings, the area accounts, and the challenge verdicts (observed: section 2). Demands no producer meets: the commitment with its party, behaviour and witness; a constraint bound to a source path a request touches; a term's sense in a request's context; the push of constraint bodies to the Developer and the Tester (reasoned: section 3).

## 5. The measures

What measures onboarding today (observed: the files):

- `probes/cnt/score.py` with `--key`: required terms, trap terms, copied terms, required and expected constraints by keyword groups, decoys. Producer-side: it counts rows, not reads.
- The answer keys, `rota/ANSWER_KEY_icalendar.md` with five predictions and `probes/ical/answer_key.yaml`, `probes/click/answer_key.yaml`. Producer-side.
- `probes/consult.py`: eight maintainer questions answered from the records by owner sessions. It starts model sessions. It is the nearest consumer-side measure, and it asks a maintainer's questions, not a delivery seat's.
- `probes/downstream.py`: "can a cold role act on the repository from the artefacts alone?", for cnt only.
- `probes/partition_judge.py`: the partition against ground truth on six repositories.
- `rota/tools/onboard_run.py` `audit` and `report`: counts per table.

What measures nothing: no gate, night count or dry run measure reads what a delivery seat loaded and whether it acted on it (reasoned: no file name or docstring read under `probes/` and `rota/tools/` names such a probe, and the "gone" note ran on 21 sessions of three runs and no record names it). Session counts and quarantines measure cost, not use (reasoned).

A consumer-side measure per demand (reasoned):

| Demand | Measure |
|---|---|
| Developer and Tester term senses | Share of delivery sessions whose push holds the sense of every `term_refs` id. Today 0 of 21. |
| Developer constraints | Share of `batch_start` sessions with the bodies of the constraints bound to the touched paths pushed. Today 0. |
| Structural review | Share of reviews with a constraint other than `k0` in range, today 0 of 3. Then a seeded change that breaks a key commitment, such as a line fold at 76 octets, and whether the review files `violated`. |
| Tester, must not change | On a seeded request that names a commitment's path, whether a test guards the commitment's behaviour. |
| Touch line | Share of touch notes with a commitments part when a key commitment binds the touched path. Today 0 on the three runs. |
| Principal | Team rows put to him per run that he did not ask for, and his replies of "drop" or "I did not ask". dry3: 235 names on m39 and four collision pages. |

## 6. The shape of the gap

1. Supply meets demand at the index: every guess and every Developer probe used it, and it carried three merges of three (observed: section 2).
2. Supply meets demand in part at the vocabulary: 9 of 10 required terms exist, but the one link a criterion makes, `term_refs`, points to a sense from another area, and no delivery seat reads the sense (observed: s171, the "gone" note).
3. Demand exceeds supply at the commitments: the briefs ask for "external commitments" and the tables hold identifiers, with the real commitments filed as README conflicts that nobody reads (observed: sections 3 and 4).
4. Demand also exceeds supply at the doors, before the rows matter: the lookup reads the wrong refs, `model.load` needs ids no Developer holds, and `k0` reads as global (observed: section 2).
5. Supply exceeds demand at the principal's page: the account page, the term collisions and the re-survey notes put the team's rows to a person who asked for none of them (observed: predicates.py 673; the key score, section 3).
6. Supply exceeds demand in cost: about 112 of 132 dry3 model minutes went to onboarding, and none of its constraints, accounts or challenge verdicts changed a delivery act (observed: section 4).
7. Frame 354 is cost with no reader: 39 to 41 reconcile sessions per run write ledger rows the agenda never pages, and constraint zero's quarantine came from two definitions of a coded area (observed: the archive heading, section 4).
8. Frame 358 and frame 361 are supply pushed at the principal: the re-survey notes and then the first baseline of 235 rows went to his page because `observed` needed an exit, not because he or a seat needed the rows (reasoned: predicates.py 673 to 674 and the two reads).
9. The four term pages on dry3 are supply pushed at the principal from a detector that fires on duplicate rows, while the real ambiguities, `timezone` and `parameter`, raised no page (observed: the key score, section 3).
10. So the gap is two-sided: the consumers that need understanding get nothing through broken doors, and the one consumer who needs least, the principal, gets the most (reasoned: 1 to 9).

## Probes

All in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/ce483c7b-be58-4d58-bfc4-db1081518842/scratchpad/demand/`, read-only with `mode=ro`:

- `loads.py <db> <first seq>`: per delivery session, the pushed blocks of turn 1 with their sizes, and the understanding calls.
- `supply.py <db>`: sessions and model minutes per role and wake kind, and the rows per table.
- Inline queries: the "gone" note and `model.load` arguments over the first turns of all three copies; `ledger` `conflict` rows; understanding ids on any `messages.body_refs`; `constraint_bindings` for `caselessdict` and `termui`.
- `w11read/probe_pages.py dry3w7/dry3.db m4 m33 m40` from the wall read, for the rendered pages.

## Usage

About 95k tokens and 45 tool calls. No model session, night, gate or dry run started. One file written in the repository, this page. Two probe scripts written in the scratchpad.
