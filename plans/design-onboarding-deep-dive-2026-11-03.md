# Deep dive: the design of onboarding, measured (2026-11-03)

A read-only dive for frame 362, after `plans/design-onboarding-2026-11-03.md`, its review `plans/design-onboarding-review-2026-11-03.md` and Roman's three rulings of 2026-11-03 in `plans/method/handoff-ce483c7b.md`. Read at 888dbdf0 on `rota/foundation`. The trees are `git archive` exports of icalendarI at `99619246`, clickI at `2c8cd3a` and tipsI at `99101f1`, the bases of the three merged batches. The dry3w7 database is a copy. No model session, night, gate or dry run started. One file written in the repository, this page.

## Result

1. A harvester of the seven kinds finds all 5 of 5 icalendar key commitments with a checkable witness, and 2 of 5 on click, in 302 and 182 candidates, so the noise is 60 and 36 candidates per key commitment, and 23 and 22 with the test witnesses taken out and the exports grouped (observed: `harvest.py`, `score.py`).
2. The harvester keeps the one real contradiction side by side, "75 octets" at `parser/string.py` 122 against "75 characters" at `docs/explanation/api-design.rst` 61 and `parser/content_line.py` 285, and finds 0 false ones (observed: `harvest.py`).
3. The binding rule places the fold, the exports and the entry point exactly, binds RFC 5545 to 49 of 83 source files, and sends 74 of 198 icalendar candidates and 77 of 175 click candidates project-wide, mostly docs claims (observed: `bind.py`).
4. The caller rule reads 1 area for `_foldline`, `canonsort_keys`, `pause` and `calculate_tip`, holds every key path of the fold, and misses `main.py`, one of the two files of the tips diff, because `main.py` holds a second definition of `calculate_tip` and calls nothing (observed: `callers.py`).
5. The `lazy` election does not keep the team's rows away from Roman: on a dry3w7 copy it deferred 240 rows to the ledger, and `tick_agenda` then paged the same 7 rows each time he answered without a ruling (observed: `lazy_trace.py`). No code reads a deferred row at a touch, so "awaiting first touch" has no exit.
6. The three broken doors have one cause each and cost 2 cycles each: the lookup reads `bg_1` as a glossary id (api.py 3662 to 3669), `model.load` needs ids the Developer cannot know and got `c1` to `c3` (api.py 4513), and `k0` is read as global because it is unbound (scheduler.py 3196 to 3201). All three come before the slice.
7. Ruling 2's measure is two dry runs on icalendarI at `99619246` with the fold sentence of section 4.2 step 6, about 55 and about 20 model minutes, after the door repairs and the lazy fix, and its deciding count is the number of delivery acts that cite a row from outside the touched area.
8. On the actuals of frames 357, 358 and 360, 19 cycles spent against 12 priced, the build is about 15 cycles of prerequisites and the measure, then the slice, then the rest, about 72 cycles or four sessions, not the two the design states (reasoned: section 8).

## 1. The harvester, prototyped

The harvester is `probes/harvest.py`, about 250 lines, standard library only. It reads the tree and writes JSON (observed: the script).

| Kind | icalendar | click | tips | Key witnesses it holds |
|---|---|---|---|---|
| metadata | 7 | 3 | 1 | ical: RFC 5545 description, `requires-python`, `python-dateutil` and `tzdata`, `[project.scripts]`. click: `name`, `requires-python` |
| doc_claim | 60 | 73 | 0 | ical: 3 lines that repeat the RFC 5545 claim. click: 0 |
| preservation | 33 | 10 | 0 | ical: `prop/broken.py` 1, 17 and 20, `docs/how-to/parse-errors.rst` 47 and 97, and `parser/string.py` 138, "For compatibility with existing clients". click: 0 |
| numeric_default | 1 | 1 | 0 | ical: `_foldline`, `limit: int = 75`, with the docstring line "75 octets". click: `_make_default_short_help`, `max_length = 45`, no commitment |
| issue_comment | 13 | 24 | 0 | ical: `parser/string.py` 140, "See issue #1501". click: 0 |
| export | 84 | 64 | 0 | ical: `__all__` of `src/icalendar/__init__.py` 101. click: the `from .x import A as A` lines of `src/click/__init__.py` |
| test_witness | 104 | 7 | 0 | Tester input, not a commitment |
| total | 302 | 182 | 1 | |

(observed: `harvest.py` on the three trees; `score.py`.)

The score against the keys:

| | icalendar | click |
|---|---|---|
| Key commitments found with a checkable witness | 5 of 5 | 2 of 5 |
| Candidates per key commitment, all kinds | 60.4 | 36.4 |
| The same, without the test witnesses and with the exports as one candidate | 23.0 | 22.4 |
| The same, without the doc claims too | 11.0 | 7.8 |
| Candidates that match no key commitment | 199 of 302, 66% | 116 of 182, 64% |
| Contradictions kept side by side | 1 real, 0 false | 0 |

(observed: `score.py`.) The icalendar witnesses are: `pyproject.toml` 42 for `rfc_5545_conformance`, with `_foldline` at `parser/string.py` 119 and the #1501 carve-out at 138 to 140 under it; `pyproject.toml` 13 and 58 and `__init__.py` 101 for the import surface; `pyproject.toml` 77 and 80 for `tzdata` and `dateutil`; `prop/broken.py` 17 and `parse-errors.rst` 47 for the round trip; `pyproject.toml` 140 for the entry point (observed: `score.py`).

The click key holds three commitments that no kind can find (observed: `score.py`, 0 hits each):

- `the_shell_completion_protocol`: the `_{PROG}_COMPLETE` environment variable in `shell_completion.py`. No kind reads an environment variable that the package reads.
- `deprecations_are_commitments`: 141 source lines say "deprecat" or "removed in" (observed: grep). No kind reads a deprecation warning.
- `readthedocs_builds_the_docs`: `.readthedocs.yaml`. No kind reads a service file.

So the seven kinds are fitted to icalendar, as the design's second doubt feared (reasoned: 5 of 5 on the repository they came from, 2 of 5 on the control). Tips has no key, and its one candidate is the package name (observed). A tool finds nothing there, and that is the honest result for a 20-grain script (reasoned).

Which kinds earn their place:

- Keep: metadata, preservation, numeric_default and export. Each holds a key witness that no other kind holds (observed: the table). Count the exports as one candidate per `__init__.py`, not one per name (reasoned: 84 rows carry one commitment).
- Drop: doc_claim. It holds 60 and 73 lines and no witness that metadata does not hold, and 58 of its 60 icalendar rows bind project-wide (observed: `bind.py`).
- Merge: issue_comment into preservation. Its one key hit, line 140, is the line under the preservation hit at 138, and its other 36 rows on both projects are bug history (observed).
- Fix: test_witness. As built it names 104 rows, 76 of them for `to_ical`, because it takes words from the quotes. Tied to the symbol that holds the witness it names 2 test files for `_foldline` and 4 for `vBroken` (observed: grep).
- Add, scored on a third repository first: a deprecation kind and an environment-variable kind (reasoned: they are general Python promises, and adding them from click alone is the same over-fit in the other direction).

## 2. The binding rule, measured

`probes/bind.py` applies 3.B step 4 to every candidate except the test witnesses. A source-file witness binds its file and the read set of the caller rule for the symbol that holds the line (observed: the script).

| Key commitment | Witness | Rule | Files bound | Key paths bound |
|---|---|---|---|---|
| `rfc_5545_conformance` | `pyproject.toml` 42 | standard | 49 of 83 source files | `parser/string.py` yes, `parser/content_line.py` yes |
| the fold, prediction 3 | `parser/string.py` 119 | source and callers of `_foldline` | 2 | both, and nothing else |
| `the_pypi_package_and_import_surface` | `__init__.py` 101 | exports | 1 | `__init__.py` yes. `requires-python` binds project-wide |
| `tzdata_and_dateutil_are_load_bearing` | `pyproject.toml` 77, 80 | dependency | `dateutil`: 7 files, all under `timezone/` and `cal/timezone.py`. `tzdata`: 83, project-wide | `timezone/` yes, `prop/recur/` only by the project-wide fallback |
| `unknown_content_survives_round_trip` | `parse-errors.rst` 47 | none fits, project-wide | 83 | `prop/` and `cal/component.py`, only by the fallback |
| the same | `prop/broken.py` 17 | source and callers of `vBroken` | 2: `broken.py`, `parser/ical/component.py` | `prop/` yes, `cal/component.py` no |
| `the_cli_preview_entry_point` | `pyproject.toml` 140 | entry point | `cli.py`, `pyproject.toml` | yes |

(observed: `bind.py` on icalendar.)

The rule's failures to place:

- Project-wide: 74 of 198 icalendar candidates, 37%, of which 58 are doc claims, 13 are docs preservation lines and 3 are metadata. On click 77 of 175, 44%, of which 73 are doc claims (observed: `bind.py`).
- `tzdata` is imported nowhere. Python's `zoneinfo` reads it as data, so the import rule cannot see it (observed: grep on `src/icalendar`).
- The `vBroken` commitment does not reach `cal/component.py`, which holds the `errors` list, through any placed rule. It reaches it only through the project-wide fallback of the docs witness (observed). The design's failure case says "the commitment binds the files that use the name", and the rule as written has no such kind (reasoned: 3.B step 4 lists five kinds).
- The standard rule over-pushes. RFC 5545 is cited in 59% of the source files, so a push on that rule reaches nearly any touch (observed).

With the doc claim kind dropped, the project-wide share falls to 16 of 140 on icalendar and 4 of 102 on click (reasoned: the project-wide rows by kind above).

## 3. The caller rule, measured

`probes/callers.py` implements 3.B step 5 on the tree and the index (observed: the script). The index for icalendar is the dry3w7 copy, read-only, 2,800 grains in 22 areas. For click and tips no dry run database was at hand, so I rebuilt the index with rota's own `rota.onboarding.indexer.build` and `areas.propose` into the scratchpad: click 1,182 grains in 4 areas, tips 20 grains in 1 area (observed: `reindex.py`). The rebuilt icalendar index holds 2,794 grains in 20 areas, close to dry3w7 (observed).

| Touched symbol | Rank 1 callers | Rank 2 pass-through | Rank 3 tests | Read set | Areas |
|---|---|---|---|---|---|
| `canonsort_keys`, icalendar | `caselessdict.py` only | none | 2 files | 1 file | `src/icalendar` |
| `_foldline`, icalendar | `parser/string.py`, `parser/content_line.py` | `parser/__init__.py` | 2 files | 2 files | `src/icalendar/parser` |
| `pause`, click | none | `src/click/__init__.py` | 2 files | 1 file | `src/click` |
| `calculate_tip`, tips | `tip_calculator.py` only | none | 1 file | 1 file | `.` |

(observed: `callers.py`, depth 1.)

Inside the read set:

- icalendar `bg_1`: the diff's source file `caselessdict.py` is inside. The key path of prediction 5, `canonsort_keys` in `caselessdict.py`, is inside. The dry3 constraint `calendar_canonical_order` binds `cal/calendar.py`, which is outside, and rightly so: `cal/calendar.py` holds its own `canonical_order` tuple and calls nothing in the touched file (observed: grep).
- The fold: both key paths are inside, one area (observed). The design predicted this (section 3.B).
- click `bg_1`: the diff's source file `termui.py` is inside. The key's import-surface commitment lives in `__init__.py`, which is rank 2 and not read. The export rule of step 4 binds `__init__.py` and `termui.py`, so the push still carries it (observed: `bind.py`, click).
- tips `b_1`: the diff touched `main.py` and `tip_calculator.py`. From either file the other is outside, because each file defines its own `calculate_tip` and neither imports the other (observed: `callers.py` from both files). A caller rule cannot find a twin definition. The guess must name both, or the rule must add same-name definitions as rank 1 (reasoned).

The design predicted about three areas for `bg_1` from same-word hits (section 3.B). The rule as written gives one, because the four `canonical_order` tuples in `cal/` and `prop/recur/` are class attributes, not calls (observed: grep). One step of closure, the callers of the symbols in `caselessdict.py` that call `canonsort_keys`, reaches 9 files in 5 areas, and the cap of three cuts 4 of them (observed: `callers.py --depth 2`). So the cap decides the read on a class such as `CaselessDict`, and the rank inside the cap is by reference count, which is a design number (reasoned).

The test diff files of all three merges are new files, so no rule can hold them. The Tester gets the rank 3 files as witnesses (observed).

## 4. The lazy path, traced

`probes/lazy_trace.py` takes a copy of the dry3w7 database, removes the 4 principal presents and the ledger, sets `baseline_election` to `lazy`, and runs the predicates and the scheduler's own actions. It writes only the copy (observed: the script).

What happens, in order:

1. `observed_entries`, predicates.py 673, fires only when `onboarding_phase` is `done` or `none` (predicates.py 684). So on `lazy` the whole survey still runs first, the 37.6 minutes included (observed: the code; reasoned: the election changes the page and not the survey).
2. Its first wake is `do:resurvey_note` for 8 re-survey rows, written as one ledger row (observed: the trace).
3. Its second wake is `do:defer_baseline` with 240 refs: glossary 99, constraints 114, areas 22, items 5 (observed). predicates.py 786 to 792 is the branch.
4. `loop._perform`, loop.py 494 to 528, writes one ledger row per ref, kind `default`, status `open`, author `principal`, text "observed and unconfirmed under the lazy election: " and the row's words. 223 rows are open after it (observed: 101 glossary, 96 constraints, 21 areas, 5 items).
5. `tick_agenda`, scheduler.py 1195, wakes the Liaison with 7 rows, `PAGE_ASSUMPTIONS` in sandbox.py 38, "ledger=223" (observed). It fires when he is present and nothing else waits on him.
6. After a page that he answers with no ruling, the next agenda wake carries the same 7 rows, three times of three (observed). The rows reach no item, so `ledger_items` is empty, no page dedup applies, and the merge does not park them, because lifecycle.py 764 parks a row only when its items are inside the merged item (observed: the code; reasoned: the trace).

What "first touch" means in the code: nothing. `defer_baseline` writes the rows. No predicate, door or touch note reads a ledger row by the grains of a batch's touch (observed: grep for `first touch`, `lazy` and `baseline_election` in `rota/`, the touch note in predicates.py 1024 to 1056). The test `test_the_lazy_election_defers_the_baseline_to_the_ledger` in `tests/rota/test_predicates.py` 1351 checks the deferral only.

What reaches the principal: the team's rows, seven at a time, on agenda pages that repeat until he rules on each (observed). That contradicts the design's 3.5, "They stay in the ledger awaiting first touch" (reasoned: the trace). So ruling 1 does not hold today when `lazy` becomes the default.

What is missing for 3.B step 6 to fire the reads from the guess:

- scheduler.py 1105: `tick_survey` fires only in the `survey` phase, and `_survey_wakes` offers every area not yet surveyed, scheduler.py 1185 to 1191. No input names the areas of a batch's touch.
- scheduler.py 1018: `onboarding_phase` is strict, and `observed_entries` waits for `done` (predicates.py 684). The guess has no phase gate (predicates.py 319 to 335), so a survey that skips areas must still let the phase reach `done`, or the rows of the touched read never reach the ledger.
- predicates.py 319, the `guess`: its output, `batch_touch`, feeds the touch note and nothing that wakes a survey (observed: grep).
- scheduler.py 1170 to 1181: the area-hash rule re-reads a whole area after a merge, which is s194's 31.4 minutes. A touched re-read needs the same filter.
- The agenda must leave the `lazy` rows out, and a touch note must name the deferred rows bound to its touch. That is the "first touch" the design assumes.

## 5. The three broken doors, diagnosed

| Door | Cause, file and line | Probe on the dry3w7 copy | Fix shape | Price | Place |
|---|---|---|---|---|---|
| `glossary.lookup` returns "the rows this wake named are gone." | With no term, api.py 3662 to 3669 reads `ctx.wake_refs` as glossary ids. A delivery wake's refs are `bg_1` and its item. | 3 sessions on dry3 got the line: `criteria`, `batch_start`, `tests_missing`. The batch's 3 criteria hold 3 `term` refs, all `canonical_order`, and all resolve to a glossary row (observed: `turns`, `refs`). | Where no wake ref is a glossary id, resolve the batch's criteria and return the senses of their `term` refs. | 2 cycles, a door text | Prerequisite |
| `model.load` never gets a constraint id | api.py 4513, `model_load(ctx, ids)`, needs ids. `push_working_set`, runner.py 4313, pushes only reads with no argument, so the read never arrives. The brief, `developer/batch_start.md` 14, tells the Developer to call it. | s180, the Developer of `bg_1`, called `model.load ids=['c1','c2','c3']`, the criteria ids (observed: `tool_calls`). | A no-argument path: the constraints that `constraints_for_grains` returns for the batch's touch, with their bodies. Then the push sends it. | 2 to 3 cycles | Prerequisite. The slice's push door extends it |
| The structural review sees only `k0` | scheduler.py 3196 to 3201 adds every unbound constraint as global. `k0` loses its bindings when every area has a survey record, so it becomes global. | `constraints_for_grains` on the `bg_1` touch returns `['k0']`. No constraint binds `caselessdict.py`. 0 constraints are global and 0 bindings fail to resolve (observed). s190 filed 2 findings, both on `k0`. | Leave `k0` out of the unbound rule. Add it only where a touched grain's area has no survey record. | 2 cycles | Prerequisite |

The k0 fix and the lookup fix change what the doors deliver today. The `model.load` fix delivers the 118 constraints of today, and on `bg_1` it delivers none, because none binds the touched file (observed). So the three repairs test whether a seat acts on a row that reaches it, which is what ruling 2 asks, and they deliver no commitment until the slice (reasoned).

## 6. Ruling 2's measure

The comparison, one run of each:

- Run F, the full read: icalendarI at `99619246`, a fresh clone, the doors repaired, `lazy`, today's whole survey of 22 areas.
- Run T, the touched read: the same, with the survey cut to the area of the touch. The guess-fired seam does not exist (section 4). A partition ruling of `ignore` on every area outside `src/icalendar/parser` approximates it, because `areas.ruling_for` takes a grain out of the partition (reasoned: areas.py 54 and 174 to 190; the guess and `code.probe` still read the whole index). Check that approximation on the copy before the run.
- The sentence: "When icalendar writes a long line, fold it at a space where it can, so that a word is not split, and keep everything else as before." It names no function and no unit, its read is one area, and its area holds the strongest outside commitment of the key (observed: section 3; the key's prediction 3).

The counts that decide, from the database of each run:

1. Acts on rows from outside the touched area: the delivery sessions whose tool arguments, commit messages, test bodies, verdict lines or findings cite a row id or quote a row's words from an area that Run T did not read. Run F pays for its read only if this count is above 0 (reasoned: this is the benefit he expects, and Run T cannot produce it).
2. Rows each seat loaded: the pushed glossary senses, constraints and findings per delivery session, from `turns.user`.
3. Outcome: merged or not, the `tests_failing` wakes, the Critic's fails, the structural findings that are not `k0`, the invented test values, and whether a test folds a line of multi-byte characters at 75 octets or fewer.
4. The key score of each run by `probes/cnt/score.py --key probes/ical/answer_key.yaml`.
5. Cost: model minutes before the first guess, model minutes in total, and pages that reached the principal.

Read the result so: if count 1 is 0 and count 3 is equal, the touched read is the default and the full read stays his choice. If count 1 is above 0 and count 3 is better on Run F, the full read is the default for that project size. One run each is n of 1 with a small model, so a difference of one fix attempt is not a result (reasoned).

The cost of each run, from the per-session minutes of dry3w7 (observed: `minutes.py`):

| | Run F | Run T |
|---|---|---|
| Before the first guess | 37.6 min, 163 sessions: survey 12.9 and 2.9, `reconcile` 8.6 on 41 sessions, term collisions 2.6, `define` 1.7 | about 1 to 2 min: `orient` 0.2, one area at about 0.72 min for both survey roles, `define` of the request's words |
| The `eager` page, s174 to s176 | 0, because `lazy` | 0 |
| Delivery, from the guess on, without the runaways | about 17.5 min | about 17.5 min |
| The re-survey after the merge, s194 | up to 31.4 min. Stop the run at the merge | up to 1 area |
| Total | about 55 min | about 20 min |

The holding session pays 2 cycles for each run and its read (observed: operating-facts line 250, the design's price for "the dry run and its read"). Both runs need the three door repairs and the lazy agenda fix first, or the full read is measured with its rows unable to reach a seat again (reasoned: section 5).

## 7. The commitment record, drafted

Two records, two writers, as law 1 asks (reasoned: LAWS.md section 1; the design's doubt on law 1).

A new table, the candidate, written only by the harvester at boot:

| Column | Meaning |
|---|---|
| `id` | from content, `sha256(kind, path, line, quote)`, law 14 |
| `kind` | `metadata`, `preservation`, `numeric_default`, `export`, `test_witness`, and later kinds by a check list |
| `path`, `line`, `quote` | the witness, copied from the file |
| `symbol` | the grain that holds the line, or empty for a root file |
| `group_id` | the contradiction group, for example the 75 octets and 75 characters lines |
| `commit_sha`, `area_hash` | the tree it was read from, so a merge makes it stale as a survey record goes stale |

A binding table for the candidate, `candidate_id`, `grain`, `rule`, where `rule` is one of `standard`, `dependency`, `entry_point`, `exports`, `source_callers`, `project_wide`. The rule is kept so that a reader can tell a placed binding from the fallback (reasoned: section 2, 37% project-wide).

The stated commitment is a `constraints` row with three new columns, written only by the Architect:

| Column | Meaning |
|---|---|
| `party` | who outside notices, for example "other calendar programs" |
| `behaviour` | what must hold, for example "lines fold at 75 octets" |
| `witness` | the candidate id it states. Its `path`, `line` and `quote` come from the candidate, and a `refs` row of kind `grain` to the witness path makes the provenance `observed` |

The bindings of the stated commitment stay in `constraint_bindings`, copied from the candidate's placed bindings (reasoned: every reader joins there).

Why three columns and not a new table for the commitment: `constraints_for_grains` (scheduler.py 3183), `model.consult` (api.py 4488), `model.load` (api.py 4513), the findings' `constraint_id`, the challenge `id` of `constraints:<id>` (schema.sql 1132) and the touch line all key on `constraints.id` (observed: grep). A new table would need each of them to read two tables. A row with `party` empty is not an outside commitment, which marks the 118 rows of today without a migration of their words (reasoned). Why a new table for the candidate: `refs` holds a target and no line or quote, its grain kinds are `path`, `symbol`, `table` and `route`, and its `src_table` check does not admit a harvester (observed: schema.sql 96 to 105). The nearest existing shape is `challenges`, which already holds `citation` and `quote` (observed: schema.sql 1132 to 1143).

How the seats read it:

- The Developer, `batch_start`: the no-argument `model.load` of section 5 returns the rows bound to the touch with `party` set, each with its party, behaviour and witness line.
- The Tester, `tests_missing`: the same push, and one brief line: write a test that guards each pushed commitment whose behaviour the change can reach.
- The Critic, `review`: the same push. The two sentences of `critic/base.md` 10 and 12 gain the exception that ruling 3 grants.
- The structural review: `constraints_for_grains` with the `k0` fix, and a `violated` finding names the commitment.
- The push leaves out a commitment whose challenge verdict is `falsified`.

## 8. Risks and order

The failure cases, each with a case found here:

| Risk | Case | Source |
|---|---|---|
| `lazy` still pages the team's rows | 223 open rows, the same 7 on every agenda page | observed: `lazy_trace.py` |
| "First touch" has no code, so deferred rows never close | the rows reach no item and do not park at a merge | observed: lifecycle.py 764 |
| The kinds fit icalendar only | click 2 of 5, with the completion protocol, the deprecations and the docs service missed | observed: `score.py` |
| The noise buries the witnesses | 199 of 302 icalendar candidates match no key commitment | observed |
| The binding fallback over-pushes | 37% and 44% project-wide, RFC 5545 in 49 of 83 source files | observed: `bind.py` |
| A dependency used as data binds nowhere | `tzdata` | observed |
| The caller rule misses a twin definition | tips `main.py` | observed: `callers.py` |
| The caller rule misses a reader of the result | `cal/component.py` and its `errors` list for `vBroken` | observed |
| The cap decides the read on a class | `canonsort_keys` at depth 2: 9 files in 5 areas, 4 cut | observed |
| The partition makes "area" mean little | click: 4 areas, `.` holds 772 grains | observed: `reindex.py` |
| A wrong unit becomes a confident promise | 2 of 3 witness lines say "characters" | observed: section 1 |
| A door that needs an argument is never pushed | `model.load` got criteria ids | observed: s180 |

The build order. Prices come from operating-facts line 250: a door text 2 cycles, an instrument fix 3, a seam with its night 8 to 10, about twenty cycles a session. The actuals of the last three frames are 10 of 2 priced for frame 357, 4 of 3 for frame 358 and 5 of 7 for frame 360, so 19 cycles spent against 12 priced, about 1.6 times (observed: `plans/stack.md`, the last "Cycles" line of each frame).

1. Before the measure, about 12 cycles priced, about 19 at the actual rate:
   - the lookup door, 2;
   - the `model.load` push, 2 to 3;
   - the `k0` rule, 2;
   - the lazy agenda fix and the `lazy` default: the agenda leaves the deferred rows out, and the touch note names the deferred rows bound to its touch, 3, which closes frame 361's question by ruling 1;
   - the key re-cut on today's indexer, 1.
2. Ruling 2's measure: two runs and their reads, 4 cycles, about 6.
3. The slice of 4.2, 16 to 19 cycles, about 26 to 30. The harvester is priced inside it at 3 to 4. This dive's prototype shows its shape, with the kind changes of section 1.
4. The rest of B: the guess-fired survey seam, 8 to 10, the caller rule with twin definitions, 2 to 3, and the cuts, 6. That is 16 to 19, about 26 to 30.

The total is about 48 to 54 cycles priced and about 77 to 86 at the actual rate, so three to four sessions, not two (reasoned: twenty cycles a session). The measure in step 2 can change step 4: if the full read pays, the guess-fired seam drops out and 8 to 10 cycles go with it (reasoned: ruling 2).

## Probes

All in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/ce483c7b-be58-4d58-bfc4-db1081518842/scratchpad/dive362/`. Run from that folder with `D:/repos/rota/.venv/Scripts/python.exe`. The trees are `src/ical`, `src/click` and `src/tips`, from `git archive` of the three repositories at `99619246`, `2c8cd3a` and `99101f1`. `db/dry3.db` is a copy of the dry3w7 database.

- `probes/harvest.py src/<repo> --out out/h_<repo>.json`: the seven kinds and the contradictions.
- `probes/score.py out/h_ical.json ical` and `probes/score.py out/h_click.json click`: the key commitments found, the noise.
- `probes/bind.py src/ical out/h_ical.json db/dry3.db ical`, and the same for click: the binding rule.
- `probes/reindex.py src/<repo> db/<repo>.db`: rota's indexer and partitioner into a scratch database.
- `probes/callers.py src/ical db/dry3.db src/icalendar/parser/string.py _foldline --key src/icalendar/parser/string.py,src/icalendar/parser/content_line.py`, and the same for `canonsort_keys` in `caselessdict.py`, `pause` in `src/click/termui.py` with `db/click.db`, and `calculate_tip` in `tip_calculator.py` and in `main.py` with `db/tips.db`. Add `--depth 2` for the closure.
- `probes/lazy_trace.py`: the lazy path on `db/lazy.db`, a second copy.
- `probes/minutes.py db/dry3.db`: the model minutes by wake kind.
- Inline, read-only on the copy: the sessions shown the lookup line, the delivery seats' tool calls, `constraints_for_grains` on the `bg_1` touch, and the term refs of the `bg_1` criteria.

## Usage

About 130k tokens and 50 tool calls. No model session, night, gate or dry run started. One file written in the repository, this page.
