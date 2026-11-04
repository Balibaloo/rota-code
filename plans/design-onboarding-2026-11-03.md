# Design: an onboarding that delivers what the seats need (2026-11-03)

A design page for frame 362, after `plans/onboarding-demand-read-2026-11-03.md`. Read-only at 3ed009a9 on `rota/foundation`, and a read of the icalendar root `D:/tmp/rota-live/icalendar` at `99619246`. Revised once from `plans/design-onboarding-review-2026-11-03.md`, see `## Revision`. No model session started. No file changed except this page.

## Result

Recommend design B: the `lazy` election that exists today becomes the default, the index and a deterministic harvest of commitment witnesses run before any request, and the model reads run only on the area that a request touches and the areas of its ranked callers, with external commitments as a record that names the outside party, the behaviour and a witness line, bound to source files by a stated rule. The reason is the composition's: "no work happens that the Principal did not ask for", "every claim cites a source", and "a weak model is trusted only as far as the loop that checks it is short", and a witness line gives a small model a source to cite and the Tester and the Critic a line to check. Build B as two sessions of slices, the first one the icalendar commitments end to end at 16 to 19 cycles, and hold design C, one stronger read per project, until that slice measures where the small model stops.

Questions for Roman, each a ruling:

1. The default choice: on 2026-08-26 (05fbe247) you ruled that "confirm the whole baseline up front, or lazily as work first touches each area" is your call and no session's; should a project where you have not chosen start on "lazily", and your choice override it (recommended: yes)?
2. The scope of the reading: both choices of that ruling have the team read the whole project before your first request, and law 12 starves constraint zero by surveying every area; should the team read only the parts your job touches and their callers (recommended: yes)?
3. A broken outside promise: on 2026-09-30 (13d138b2) you ruled that the checker fails a change only on what your request says, and the purpose line of 2026-09-16 says no work happens that you did not ask for; should a broken promise to outside programs stop the merge even when your request did not name it (recommended: yes)?

Ruled by Roman on 2026-11-03 at about 01:05 (observed: frame 362, the status line of 01:10; the words are from session ce483c7b's terminal):

1. Yes. `lazy` is the default where he has not chosen, and his choice overrides it. This amends the use of 05fbe247, 2026-08-26, not the ruling: the choice stays his.
2. Not as asked. His words: "I guess we can let the principal decide in the moment, but I'm expecting reading up front to have significant benefits." So the scope of the read is his choice in the moment, the whole project or the touched area and its callers, and the design keeps both. His expectation is measured, not assumed: the demand read's finding that no seat acted on a survey row was taken with three of four doors broken, so it does not yet test the full read. The order is: repair the doors (section 3.A, steps 1 to 3), then one dry run with the full read and the doors working against one with the touched read, scored against the key and by what each seat loaded.
3. Yes. A broken promise to outside programs stops the merge even when his request did not name it. This amends 13d138b2, 2026-09-30, and reads the purpose line as the project's promise to the outside, not as the team's work.

What ruling 2 changes in B: the "Cuts" line of section 3.B no longer cuts the whole-project survey. The survey's scope becomes a choice he makes per project in the moment, beside the eager-or-lazy election, and neither scope is the default until the measure above says which one pays. The touched read of 3.B step 5 is the second scope, not the only one.

## 1. The facts the demand read established

The door is the call or push that hands a record to the seat. "Connects" means the record reaches the seat in a usable form.

| Consumer | Its question | What it got on the three merged runs | The door | Connects |
|---|---|---|---|---|
| Architect, `guess` | Which files will this request touch? | Index rows, and the request's own words named the function | `code.callables`, `code.probe` | Yes. It carried 3 merges of 3 (observed: the read, section 2) |
| Terminologist, `criteria` | What does each word of the item mean here? | 106 glossary rows. The `term_refs` row `canonical_order` held the class-variable sense, not the parameter sense the request meant | `glossary.consult` | In part. The row is of the wrong area (observed: the read, s171) |
| Developer and Tester, every delivery wake | What does a criterion's term mean? | "the rows this wake named are gone." on 21 sessions | the pushed `glossary.lookup` reads the wake refs, such as `bg_1`, as glossary ids | No (observed: api.py 3662 to 3669, the read, section 2) |
| Developer, `batch_start` | Which commitments bind what I touch? | 14 `model.load` calls, 0 with a constraint id | `model.load(ids)`. `batch_start.tools` has no `model.consult` | No (observed: the read, section 3) |
| Tester, `tests_missing` | What must not change here? | Nothing. The brief asks for none | none | No door exists (observed: `tester/base.md` 11) |
| Critic, `review` | Does the diff meet the criteria, and does it break anything? | Criteria, tests, the diff. Work outside the criteria is "a remark" | none for understanding | No door, by design (observed: `critic/base.md` 12) |
| Architect, `structural_review` | Does the diff break a constraint it touched? | `k0` "this area has not been surveyed" only, 3 of 3 | `constraints_for_grains`, which reads an unbound row as global | No. The headline is false once every area has a survey (observed: scheduler.py 3196 to 3203) |
| Liaison, the touch note | Which commitments bind this change? | No commitment line | `constraint_bindings` on the touched paths | Yes, and empty on the touched paths. 108 of 122 dry3 bindings name a `src/` path, and none names a path that a request touched (observed: m40, dry1 `termui.py`, the review's `p1.py`) |
| Liaison, `agenda` | Which open rows does the principal see? | 0 of 16 README-against-code `conflict` rows on a page | `ledger` through the agenda | Yes, and nobody acts on the rows (observed: the read, section 4) |
| Principal, the account and collision pages | none. He asked for no team rows | 235 names on m39, four collision pages of one sense written twice | `observed_entries` under the `eager` election, `term_collision` | Yes, supply pushed at him. The `lazy` election sends the same rows to the ledger "awaiting first touch" (observed: predicates.py 673 and 777 to 792; cli.py 798 to 804; the key score, section 3) |

## 2. The axes

| Axis | Options | What the facts say |
|---|---|---|
| When understanding is made | before any request, for the whole project; or from the request outward | Before the first delivery dry3 spent 37.6 model minutes on onboarding, the first survey of 22 areas 13.9 of them, about 0.63 minutes an area. No row of it changed a delivery act (observed: the review, `turns.ms` per session on dry3w7; the read, section 2). |
| When the principal confirms | `eager`, the baseline on a page for signoff; `lazy`, every row to the ledger awaiting first touch | Both exist, and the choice is his (observed: cli.py 798 to 804, "It is the principal's call and nothing else's"). Both choices survey the whole project first (reasoned: the election changes the page, not the survey, predicates.py 777 to 792). |
| Who makes it | deterministic tools; a small model per area; one stronger read | The index is deterministic and carried every merge (observed). The small model gets terms and the description right, 9 of 10 required terms and 0 of 7 traps hit, and gets commitments wrong, 0 of 5 (observed: the key score, section 1). |
| What it holds | facts; commitments; both | The briefs ask most for commitments, and the tables hold identifiers. The median constraint body is 43 characters (observed: the key score, section 1). |
| How it reaches a seat | a door that works; a brief line; a page | Three of the four delivery doors are broken in the wiring (observed: section 1 above). A push needs no thought from the model (observed: runner.py 4313, "Callable-with-no-arguments is the honest rule"). |
| What reaches the principal | the description, the touch line, his own questions, the Done line; or the team's rows | He asked only for the first group (reasoned: the read, section 3, the purpose line). |
| How it is measured | producer side, the answer key; consumer side, what a seat loaded and whether it acted | Today only the producer side exists (observed: the read, section 5). |

A small model stops at the commitments (observed: 0 of 5 on icalendar, 0 of 2 required on click and on ical_v0). A tool with no model finds a behaviour line for four of the five icalendar commitments and a bare name for the fifth (observed: the review, section 3, `harvest.py`). So the gap is mostly in the statement and the binding of a commitment, not in the search for its source (reasoned: the survey reads at index depth, as the key predicted for `vBroken`).

## 3. Three candidate designs

The cycle prices come from `plans/operating-facts.md` line 250: a door text or a number is 2 cycles, an instrument fix is 3, a seam design with its night is 8 to 10, and a session holds about twenty cycles after its wake.

The minutes below come from the per-session sums on dry3w7, with three runaway sessions named apart (observed: the review, finding 2):

- s174, the account page Liaison on `gemma4:12b`, 33.3 minutes.
- s175 and s176, the same wake again, 9.7 minutes together.
- s194, a re-survey of the `.` area after the merge, 31.4 minutes.

These four sessions hold about 74 of the 112 onboarding minutes. The first two are frame 361's wall and the third is frame 358's (reasoned: the frames' sites). A design is priced against the 37.6 minutes before the first delivery, and the runaways are priced apart.

### A. Repair the doors and keep the survey

What it does:

1. The pushed `glossary.lookup` reads the criteria's `term_refs`, not the wake refs. 2 cycles.
2. `batch_start`, `tests_missing` and `review` get the bodies of the constraints bound to the touched grains as a push. 2 to 3 cycles.
3. `constraints_for_grains` drops `k0` when every area has a survey record. 2 cycles.
4. The touch note reads the bindings of the guess. It exists, so 0 cycles.

Cost: about 7 cycles and a dry run read of 2 (reasoned). Keeps: the whole survey, the `eager` default with its account page, and the collision pages. Cuts: nothing.

Failure case: the Developer of `bg_1` on icalendar touches `src/icalendar/caselessdict.py`. No constraint binds that path, because `icalendar_caselessdict` binds two docs paths (observed: the review's `p1.py`). So the repaired push is empty. On a change to `_foldline`, the push holds rows such as `vrecur`: "icalendar.prop.recur.vRecur", and no row says 75 octets (observed: the key score, section 1). The doors connect, and they deliver rows with no promise in them (reasoned).

Measure: the share of delivery sessions whose push holds every `term_refs` sense, from 0 of 21 toward all. A seeded break that only a commitment can catch, section 4.2 step 6, and whether the structural review files `violated`. A predicts no on the second measure (reasoned: no row holds the fact).

What it changes: one door family. No law, no seat form.

On 2,800 grains: 37.6 minutes before the first delivery, as today, and the runaways stay until frames 361 and 358 close (observed: dry3). On 300 grains: on the order of dry2 tips, 35 sessions and about 4 minutes in total (observed: dry2 supply row; the split per session is unread).

### B. Understanding from the request outward, on the `lazy` election

What it does:

1. The `lazy` election becomes the default where the principal has made no choice. His `rota elect eager` still overrides it (observed: the election exists, cli.py 798 to 804; reasoned: a default is not a choice for him only if his word wins).
2. Before any request, two deterministic tools run, and one model wake. The indexer writes the grains and edges, as today. A new harvester writes commitment candidates: each one a witness line with its path, its line number, its quoted text and its kind. `orient` writes the description for m4 from the README and the index, as today, 2 sessions.
3. The harvest kinds:
   - the package metadata: `description`, `requires-python`, `[project.scripts]`, the dependencies;
   - README and docs claims that name a standard or say "compatible" or "supports";
   - docs and docstring sentences of preservation: "preserv", "round-trip", "for compatibility with existing clients";
   - numeric defaults in a signature of a module that cites a standard, with the docstring line beside them;
   - comments that cite an issue;
   - the public exports of `__init__.py`, as names;
   - tests that name a witness symbol, as the Tester's input.

   Two witnesses that contradict are kept side by side in one candidate, for example "75 octets" at `parser/string.py` 122 and "75 characters" at `docs/explanation/api-design.rst` 61 and `parser/content_line.py` 285 (observed: the review, finding 5).
4. The binding rule. A commitment whose witness is in a root file binds source files by its kind, deterministically:
   - a standard claim binds every source file whose text cites the same standard;
   - a dependency claim binds every source file that imports the dependency;
   - an entry point binds its target module and `pyproject.toml`;
   - the exports bind `__init__.py` and every module it re-exports;
   - a claim that matches none of these binds every source file of the package, marked project-wide.

   A commitment whose witness is in a source file binds that file and its ranked callers (step 5).
5. On a request, after the guess, the scheduler wakes the model reads for the touched area and the areas of its ranked callers only. The callers are found from the touched symbols, not from the area edges, because the edges stop at the `__init__.py` re-exports (observed: the review, section 4; `parser/string.py` has 1 in-edge and `caselessdict.py` has none). The rank:
   1. source files that call the touched symbol by name, following a re-export through `__init__.py` to the file that imports it;
   2. source files that only re-export it, which count as a pass-through and are not read;
   3. test files that name it, which go to the Tester as witnesses and are not read.

   The read takes callers in rank order and stops at three areas. The Architect states each commitment candidate bound to those paths as a record with the outside party, the behaviour and the witness, or declines it. The Terminologist defines the request's own words in the touched area, and reads the existing senses of each word first, so a touch over two areas does not write one sense twice (reasoned: the key score, section 3).
6. One door family pushes the commitments bound to the touched paths to the Developer, the Tester, the Critic and the structural review. The same push carries the senses of the criteria's `term_refs`.
7. A survey record per area stays valid while the area's hash holds. A merge changes the hash, so the next request on that area reads it again (observed: `survey_records` stamps `area_hash`; reasoned: s194 is that re-read done at once and for the whole `.` area).

Keeps: the index, the description, the guess, the touch line, the area-hash rule, the election and constraint zero. Constraint zero now honestly marks every area no request has touched (reasoned: law 12 says constraint zero "makes ignorance safe on day one", and B keeps ignorance outside the touch).

Cuts (amended by ruling 2 of 2026-11-03, see Result: the whole-project survey is not cut, it is his choice in the moment beside the touched read, and the measure decides the default): the whole-project survey as the only scope and `define` over every lexicon word, `reconcile`'s 39 to 41 sessions (the README claims become candidates), the `eager` account page as a default, the `term_collision` pages, the re-survey of the whole project after a merge, and the area accounts, which no delivery seat read (observed: the read, section 4). `challenge` runs on the commitments in play only.

Shape against prose (amended 2026-11-03 from Roman's words of 09:50 in session ce483c7b, recorded in addendum 1 of `plans/method/handoff-ce483c7b.md`: "understanding can also be measured by what the tool can answer about the project" and "whole project understanding is key for efficient solution designs for future work"). The line of B is shape against prose, not whole against touched. Up front and whole, steps 2 to 4: the index, the promises with their witnesses, and the shape facts a designer asks for, the copies of one function, the shared helpers, the parts that state different facts, and the boundaries. The measure of this layer is the key's eight consult questions, `probes/consult.py`, and the traps of `plans/understanding-test-blind-2026-11-03.md`. On demand, where the request lands, step 5: the senses of the request's words and the detailed reading of the touched files and their callers. The measure of this layer is the outcome. The up-front read is not an option that a measure can remove. What it must not be is 153 sessions of prose about every area. The reason: the deep dive's caller rule missed `main.py`'s own copy of `calculate_tip` on tips, and the blind test built three of its twelve traps on facts of that kind, two copies of one function, a shared helper, two formatters that disagree (observed: `plans/design-onboarding-deep-dive-2026-11-03.md`, Result 4; `plans/understanding-test-blind-2026-11-03.md`, Result). The shape facts of the up-front layer have no design yet. That design waits on the ruling of addendum 2 of the same note, the understanding capability.

Failure case: a change in `src/icalendar/prop/` to the way a value is parsed breaks the round trip of `vBroken`, and `cal/component.py`, which holds the `errors` list, calls nothing in the touched file. The caller rule misses it. The binding rule still reaches it, because the preservation witness in `docs/how-to/parse-errors.rst` 46 and 47 names `vBroken` and the commitment binds the files that use the name (reasoned: the key binds `unknown_content_survives_round_trip` to `prop/` and `cal/component.py`). A second failure case: a request in everyday words that names no function. The guess then has less to start from, and B depends on the guess more than today does (reasoned: all three merges came from requests that named the function).

Measure: supply, the key's five commitments found whole with a witness that a person can check, and the harvest's noise, candidates per key commitment. Demand, the share of `batch_start`, `tests_missing` and `review` sessions whose push holds the commitments bound to the touched paths, from 0 today, and the seeded break of section 4.2 filed as a finding. The caller rule, on `bg_1` and on the fold sentence: the share of the diff's files and of the key's bound paths inside the read set, and the number of areas read. Cost, onboarding model minutes per request.

The caller rule on the two cases, as a prediction to measure (reasoned: a grep at `99619246`, not a run):

- The fold sentence touches `_foldline`. Its one source caller is `parser/content_line.py` 288, through the re-export in `parser/__init__.py`. Both files are in the `src/icalendar/parser` area, so the read is one area.
- `bg_1` touches `canonsort_keys` in `caselessdict.py`. Files of `cal/` and `prop/recur/` name `canonsort_keys` or `canonical_order`, so the read is about three areas. The split between callers and same-word hits is unread.

What it changes: law 12, in that "starved by positive survey records" applies to touched areas only, and constraint zero is the normal state of the rest. The election's default. A record kind: the commitment candidate, and three columns on the constraint, the party, the behaviour and the witness. A seat's form: the Critic's rule gets one exception, section 4.2 step 3. A door family: one push for all delivery seats. A page form: the account page leaves the default path, and the collision pages go. The ledger holds the team's rows, and the Liaison shows them when he asks.

On 2,800 grains: before the first delivery, `orient` at about 0.3 minutes, the harvest at 0, and three areas at about 0.63 minutes each, with the request's words defined in under a minute. That is about 3 to 4 minutes against 37.6, so B saves about 30 minutes before the first delivery on icalendar (reasoned: the per-area mean of the first survey; the review's estimate agrees). The `lazy` default removes the s174 to s176 runaways, and the touched re-read removes s194, about 74 minutes more, but frames 361 and 358 can remove those runaways without B (reasoned). On 300 grains the whole project is two or three areas, so B reads nearly all of it on the first request, and the cost is close to today's (reasoned: tips has 29 grains, dry2 onboarding cost about 4 minutes in total).

Build cost: the first slice, section 4.2, 16 to 19 cycles. The survey wakes fired from the guess and not from boot, a second seam, 8 to 10. The caller rule, 2 to 3. The cuts of `reconcile`, the collision pages and the whole re-survey, about 2 each, 6. Total about 32 to 38 cycles, which is two sessions, not one (reasoned: operating-facts line 250, about twenty cycles a session).

### C. B, with one stronger read per project for the commitments

What it does: B, and one session on a stronger model reads the harvest's candidates for the whole project once, and writes the commitments. The small model still writes the terms and reads the touched area.

Price on the box: `qwen2.5:14b-instruct-q3_K_M` runs at 75% GPU and 153 seconds a turn, and keeps "judgement parity", which is not a measured gain on commitments (observed: operating-facts line 96). The 27b models overflow by about 8 GB and run minutes a turn (observed: line 102). So one read of 10 to 20 turns costs 25 to 50 minutes on the 14b, and a 27b read costs hours (reasoned). A hosted model is faster and makes rota depend on a service outside the box. The destination says "a careful person runs rota alone" (reasoned: whether a hosted model breaks "alone" is his to say).

Keeps and cuts: as B. The commitments of areas no request touched now exist too.

Failure case: the stronger model states the fold commitment as "lines fold at 75 characters", the unit of two of the three witness lines. The page then shows a confident wrong promise, and the Tester writes a test on characters (reasoned: the key names "75 octets, not characters" as the trap, the contradicting witnesses exist, and no stronger local model was scored against the key).

Measure: as B, and the stronger read against the small read on the same candidates, five commitments each.

What it changes: as B, and a model profile per wake kind. The destination's honesty line moves: rota says that small models stop at commitments and that it buys them with one stronger read (reasoned).

On 2,800 grains: B's cost, and one stronger read of all candidates. On 300 grains: B's cost, and a stronger read of few candidates, so the read is small but the reload of a second model in each direction is a fixed cost (observed: line 97, "A model swap costs a reload in each direction").

Build cost: B, and 3 to 5 cycles for the profile, the one-shot wake and its key score (reasoned).

### 3.4 The contract of design B

One row per record kind. "Supply" is the producer's measure against the key. "Demand" is the consumer's outcome.

| Record | Producer | Source | Provenance | Consumer | Moment | Door | Supply measure | Demand measure |
|---|---|---|---|---|---|---|---|---|
| grains and edges | indexer | the code | observed | guess, Developer probe, touch line, caller rule | before any request | `code.callables`, `code.probe` | the key's counts re-cut on today's indexer | the guess's paths hold the diff's paths |
| description | Vision Keeper `orient` | README, the index | reasoned | the principal on m4, the Vision Keeper on signoff | before the first request | m4, `problem.consult` | the key's Q1 and the five items | his "ok" in one turn |
| commitment candidate | harvester | metadata, README, docs, docstrings, signature defaults, issue comments, exports, test names | observed | the Architect's touched-area read, the Tester | before any request | pushed to that read | the key's five witnesses present, and candidates per key commitment | share of stated commitments that cite a candidate |
| commitment | Architect, touched-area read | candidates and the source of the touched paths | reasoned, with an observed witness | Developer, Tester, Critic, structural review, touch line | after the guess, before the criteria | one push from the touched paths, bound by the rule of 3.B step 4 | the key's five commitments whole | seeded break filed as a finding, a test that guards the behaviour |
| term in context | Terminologist, after it reads the existing senses of the word | the item's words and the touched area | reasoned | criteria `term_refs`, Developer, Tester | criteria | the push from `term_refs` | required terms and traps of the touched area, and no sense written twice | share of delivery sessions whose push holds every `term_refs` sense |
| unsurveyed ground, `k0` | scheduler | the survey records | observed | touch line, structural review | each batch | `constraints_for_grains`, `k0` dropped where the touch is surveyed | no area of the touch under `k0` | the review sees a real row, not `k0` |
| challenge verdict | Critic `challenge` | the commitment and its witness | reasoned | the push filter: a falsified commitment does not bind | after the read | `challenges` | falsified share on the key | no seat gets a falsified commitment. Supply that waits for its first demand: no seat read a verdict on dry3 (observed: the read, section 4) |

Cut, because no consumer reads the record to effect: the README `conflict` rows, the area accounts, the whole-lexicon glossary rows (observed: the read, section 4).

### 3.5 What reaches the principal

| Reaches him | Never reaches him unasked |
|---|---|
| The description once, on m4 | The account page of observed rows, unless he elects `eager` |
| The touch line with the commitments the change must keep | Term collisions between the team's own rows |
| His own open questions, and a commitment that a request contradicts | Re-survey notes after a merge |
| The Done line | The team's rows in bulk. They stay in the ledger "awaiting first touch", and the Liaison shows them when he asks |

The cases decide as follows (reasoned: the purpose line, both halves):

- Frame 361's page of 235 rows is answered by `rota elect lazy` today (observed: the review, section 5, dry3-wall1-read line 82). B makes `lazy` the default, so the page appears only when he elects `eager`. Frame 361's size bound then matters only under `eager`.
- Frame 358's re-survey after a merge does not run under B. A re-read happens only when a later request touches a changed area, and its rows go to the ledger.
- The four term pages on dry3 go. A real ambiguity, such as `timezone` with three senses, reaches him only when it changes what his request means, as a question the Liaison originates and that names the row (observed: the composition, "the question names the row it is about").
- Under `lazy`, each row waits "awaiting first touch", and the touch line of B is that first touch (reasoned: cli.py 803).

### 3.6 The cost bound

Model minutes before the first delivery, and the runaways apart (observed: the "Today" column for icalendar, the review, finding 2; the click and tips totals, the read, section 4, with the runaway split unread there; reasoned: the B columns from the per-area mean of 0.63 minutes).

| Project | Today, before the first delivery | Today, runaways | A | B, the first request | B, a later request on an unchanged area | B, a later request on an area a merge changed |
|---|---|---|---|---|---|---|
| tips, 29 grains | about 4 min in total, 35 sessions | unread | the same | about the same | 0 | under 1 min |
| click, 1,188 grains | about 28 min in total, 110 sessions | unread | the same | about 3 to 4 min, about 10 sessions | 0 | about 2 min |
| icalendar, 2,800 grains | 37.6 min | about 74 min: s174, s175 and s176, s194 | the same | about 3 to 4 min, about 10 sessions | 0 | about 2 min, and s194's 31.4 min shows that one re-read can run away |

The bound under B: up to three areas a request, the touched area and the areas of the ranked callers, times the per-area cost, and `orient` once. The cap of three is a design number, not a measure (reasoned).

## 4. The first vertical slice: the icalendar commitments, end to end

### 4.1 The witnesses exist, and a tool can find most of them

All read at `99619246`, or at `4f12af1e` for the review (observed):

- `pyproject.toml` line 42: `description = "RFC 5545 compatible parser and generator of iCalendar files"`. Line 58: `requires-python = ">=3.10"`. Lines 78 to 80: the dependencies, "required on Windows". Lines 139 and 140: `[project.scripts]`, `icalendar = "icalendar.cli:main"`.
- `src/icalendar/parser/string.py` line 119: `def _foldline(line: str, limit: int = 75, fold_sep: str = "\r\n ") -> str:`. Line 122: "75 octets". Line 140: "escapes across a folded line boundary. See issue #1501."
- `docs/explanation/api-design.rst` line 61 and `parser/content_line.py` line 285 say "75 characters", the trap unit.
- `src/icalendar/tests/test_icalendar.py` imports `_foldline` and holds "We do not fold within a UTF-8 character" at line 77.
- `docs/how-to/parse-errors.rst` lines 46 and 47 hold the `vBroken` round-trip behaviour. `vBroken` appears in 21 lines of tests.
- `src/icalendar/__init__.py` line 101 holds `__all__`.
- The files that cite RFC 5545 include `parser/string.py` and `parser/content_line.py`. The files that import `dateutil` or `zoneinfo` are under `timezone/`, `cal/timezone.py`, `attr.py`, `cal/calendar.py` and `prop/dt/datetime.py`.

The review's approximation of three kinds found 4 numeric defaults in modules that cite an RFC, 88 claim lines in 18 docs files and 7 issue comments in `src/` (observed: the review's `harvest.py`). So the yield exists, and the noise is large enough to measure (reasoned).

### 4.2 The slice

1. The record. A table of commitment candidates: id from content (law 14), path, line, quoted text, kind, and the contradicting lines beside it. Three columns on `constraints`: `party`, `behaviour`, `witness`, and the bindings of the rule of 3.B step 4.
2. The producer. The harvester in `rota/onboarding/`, run at boot after the indexer, with the binding rule. The Architect's survey wake of an area gets the candidates bound to its paths pushed, and a brief line: state the party, the behaviour and the witness, or decline. Where two witnesses contradict, quote both and say which one the code does.
3. The consumers. The Tester's `tests_missing` gets the commitments bound to the touched paths, and one brief line: a test guards each pushed commitment whose behaviour the change can reach, from the witness's input and output. The Critic's `review` gets the same push. Two sentences of `critic/base.md` change:
   - line 10, "Do not fail a diff for a purpose you read in a docstring or a comment", gains "except a pushed commitment, whose witness the push quotes";
   - line 12, "Anything the diff does outside the criteria is a remark", gains "except a broken pushed commitment, which is a fail".

   The rule came from night 101, where the Critic failed `bg_1` for a trailing newline after it read a purpose from the builder's docstring (observed: 13d138b2, 2026-10-01, Roman's ruling of 2026-09-30). That commit changed two prompt files and added no register case (observed: `git show --stat`). So the slice writes two register cases: the night 101 case, which must still pass, and a pushed-commitment case, which must fail (reasoned).
4. The door. One read with no argument, so `push_working_set` sends it unasked: the commitments bound to the batch's touch set, with `k0` dropped where the touch has a survey record (observed: runner.py 4313, the push rule).
5. The page line to the principal. The touch line gains one part, for example: "This change touches `src/icalendar/parser/string.py`. It must keep: lines fold at 75 octets, because other calendar programs read the files." No other understanding text reaches him.
6. The measure. The dry run sentence names no limit and no unit: "When icalendar writes a long line, fold it at a space where it can, so that a word is not split, and keep everything else as before." The sentence touches `_foldline`. Count on the run:
   - Supply: the five key commitments in the candidates, each with its witness, and with the dry3w7 copy as the red test today at 0 of 5. The noise, candidates per key commitment.
   - Demand: `rfc_5545_conformance` and the issue #1501 carve-out in the Tester's and the Critic's push. A test that a line of multi-byte characters folds at 75 octets or fewer. The request does not say "octets", so that test can come only from the push (reasoned).
   - Sizing: the other three commitments absent from the push, because the change does not reach them.
   - The seeded break, outside the request: the same batch replayed with a fold that counts characters, not octets. The request names no unit, so only the push lets the Critic file a fail (reasoned). A second seed: a fold inside a backslash escape, which only the #1501 witness names.
   - The principal: one touch line with the commitment, and no other page from understanding.
7. The control. The key's counts re-cut on today's indexer, so the 1,731 grains in 9 areas of the key match the 2,800 in 22 of the run (observed: the key score, section 4).

Price: the harvester with the binding rule, an instrument and a rule, 3 to 4 cycles. The record kind and the push door, a seam with its night, 8 to 10. The two brief changes with their two register cases, 2. The dry run and its read, 2. The key re-cut, 1. About 16 to 19 cycles, close to the twenty that one session holds after its wake (reasoned: operating-facts line 250). The slice does not need the request-outward scheduling of B step 5. It runs on today's whole survey, so it tests the record, the binding and the doors first, and the scheduling in the second session.

## 5. The recommendation

Recommend B, built from the slice in section 4, over two sessions. The reasons, in the composition's words:

- "The structure holds a model of its shape, terms, boundaries, and external commitments, as records observed from the code." Today it holds the first three and not the fourth (observed: the key score). The harvest gives the fourth an observed witness, and the binding rule ties it to the code.
- "Every claim cites a source. A seat can check the claim against the source." A commitment with a witness line is checkable. A 43-character body is not (observed: the key score).
- "A weak model is trusted only as far as the loop that checks it is short." The small model states a commitment from a line it is given. The Tester's test and the Critic's fail check it on the same batch (reasoned).
- "No work happens that the Principal did not ask for." The whole-project survey is 37.6 minutes before the first delivery that no seat used, and under `eager` it pushed 235 rows at him (observed: the review, finding 2; the read, section 6).

A alone is not enough, because the repaired doors deliver rows that hold no promise (reasoned: section 3.A failure case). The door repairs of A are inside B's push, so none of A is lost. The lookup fix of A step 1 is a wiring bug, 2 cycles, and it can go first with no ruling (reasoned: it delivers what the briefs already ask for).

C waits for the slice's measure (reasoned: the destination's honesty line asks for the measured place where small models stop):

- 4 or 5 of 5 stated whole: C buys nothing, and the page shows the rest as raw witness lines.
- 3 of 5: one trial of the stronger read on the missed commitments only, scored against the key, before any profile is built.
- 2 or fewer: C is the next frame.

Notice, no ruling needed now. When the small reader finds a line such as `limit = 75` and cannot state who depends on it, the touch line shows the raw line and says that a small model could not state the promise. A bigger model is a question for him only if the slice measures 2 or fewer of 5, or 3 of 5 and the trial wins (reasoned: the purpose line, "no work stays invisible").

### The questions for Roman, in plain words

1. **The default choice. Needs his ruling.** On 26 August you ruled that it is your call, and no session's, whether the team asks you to confirm its picture of a project all at once at the start, or bit by bit as work first touches each part. Today, when you say nothing, the team takes "all at once". On the big calendar project that put 235 of its notes on one page for you to approve or drop. The design keeps your choice yours and changes only what happens when you have not chosen: the team takes "bit by bit", and its notes wait in the log. Recommended answer: yes, "bit by bit" when you have not chosen, and your word always wins.
2. **The scope of the reading. Needs his ruling.** Both choices of that ruling have the team read the whole project before your first request. Law 12 also has it read every part, so that no part stays marked "not yet understood". On the big calendar project that reading took about 38 minutes of model time before any work on your request, and no builder used a line of it. Under the design, the team reads the floor plan and the promises on the front door first, and then only the rooms your job touches and the rooms that call into them. The rest stays marked "not yet understood", which is true. Recommended answer: yes, read only what the job touches.
3. **A broken outside promise. Needs his ruling.** On 30 September you ruled that the checker fails a change only on what your request says, after the checker failed good work for a purpose it read in a code comment. The purpose line of 16 September says no work happens that you did not ask for. You ask the team to fold long lines at a space. The checker sees that the change now counts letters, not bytes, so a line of accented text runs past the limit that other calendar programs accept. Today the checker writes this as a side remark, and the change merges. Under the design, the checker fails the change only for a promise the project already makes, quoted from the code, and the builder fixes it. Recommended answer: yes, a broken outside promise is a fault.

## Doubts

- All three merges came from requests that named the function (observed: the read, section 2). B leans on the guess and the caller rule, and a request in everyday words is not yet tested. A dry run sentence with no symbol name must come before B's scheduling slice (reasoned).
- The harvester's kinds are drawn from one project, icalendar. A numeric default in an RFC module and an issue comment may be icalendar's habits. The control is click and tips, and the harvester's yield and noise must be scored there before they count (reasoned: "I want to prevent over fitting", ruled 2026-10-15). On click the commitments are command-line behaviour, and `[project.scripts]` and the exports may be the whole yield (reasoned, unread).
- The binding rule by citation and by import is a lexical rule. A file that implements RFC 5545 and does not say so gets no binding, and the project-wide fallback can then over-push (reasoned).
- The B cost per request is the per-area mean of the first dry3 survey, not a measure. s194 shows that one area, `.`, can take 31.4 minutes on a re-read (observed: the review, finding 2). A cap per area read is not designed here.
- The caller rule follows a re-export by name. A symbol called through an attribute or a string, such as a factory lookup, has no caller by name (reasoned: `TypesFactory`, the key's Q4).
- I reject A on the content of the rows, not on a measured outcome. A dry run with A's door fixes could show that some rows help. The lookup fix is cheap enough to test that, and it is in the recommendation as the first step (reasoned).
- Law 1 asks for one writer per row. The harvester writes the candidate and the Architect writes the commitment. That holds only if the commitment is a separate row, and the three new columns on `constraints` must not be filled by the harvester (reasoned).
- The Critic's exception widens what can stop a merge. A false commitment with a real witness line could stop good work, which is the night 101 fault in a new form. The challenge on each commitment in play and the night 101 register case are the guards, and the false-fail rate is unmeasured (reasoned).
- Under B, constraint zero covers most of a large project for ever. The touch line must then not say "nobody surveyed" on every change, or it becomes noise to him. The line names only the unsurveyed ground inside the touch (reasoned).
- The demand read was one agent's read of three runs. Its "no delivery seat acted" is in part a result of the broken doors, so the demand for terms may be larger than the runs show once the doors connect (reasoned).
- The description stays a whole-project read. Its sole consumer of note is m4, and his "ok" on m4 is a light check. Whether he needs the description at all is not asked here (reasoned).

## Usage

First pass: about 95k tokens and 15 tool calls. Revision: about 35k tokens and 9 tool calls. No model session, night, gate or dry run started. One file written in the repository, this page.

## Revision

From `plans/design-onboarding-review-2026-11-03.md`, one line per finding:

- H1: B is now `lazy` as the default plus a touched-area read. The election is in sections 1, 2, 3.B step 1 and 3.5. The 2026-08-26 ruling is restated as the eager-or-lazy choice being his, and question 1 is split into questions 1 and 2.
- H2: every cost is restated from the per-session minutes: 37.6 minutes before the first delivery, 0.63 minutes an area, and s174, s175 and s176, and s194 named apart in section 3 and 3.6. The B saving is about 30 minutes on icalendar, and "most of the day" is gone.
- H3: a binding rule by kind is in 3.B step 4. It ties a root-file commitment to source files by citation, by import, by entry point and by export, with a project-wide fallback, and it is priced inside the slice's harvester at 3 to 4 cycles.
- H4: neighbours are now the ranked callers of the touched symbols through the re-exports, capped at three areas, in 3.B step 5. The rule is predicted on `bg_1` and on the fold sentence, and measured by the share of the diff's files and bound paths in the read set.
- M5: the harvest gains a docstring kind and a preservation kind, and keeps contradicting witnesses side by side. Yield and noise are scored in 3.B and 4.2.
- M6: both Critic sentences, `critic/base.md` lines 10 and 12, are named with their change. The night 101 provenance is stated, and two register cases are added to the slice.
- M7: the slice is priced at 16 to 19 cycles, and B at 32 to 38 cycles over two sessions.
- M8: the dry run sentence names no limit and no unit. The seeded break is a character count, outside the request. The case of 3 of 5 now gets one scored trial of C.
- M9: question 3, the old question 2, opens with the ruling of 2026-09-30, its commit, and the purpose line of 2026-09-16.
- L10: table 3.6 shows the re-read after a merge, with s194's 31.4 minutes as its runaway case.
- L11: the old question 3 is now a notice under the recommendation in section 5.
- L12: the touched-area `define` reads the existing senses of a word first, in 3.B step 5 and in 3.4.
- Review section 2: the challenge verdict row in 3.4 is marked as supply that waits for its first demand.

From Roman's rulings of 2026-11-03, written by session 07f209e6 at 01:2x:

- Ruling 1 closes question 1 as recommended.
- Ruling 2 keeps the whole-project read as his choice in the moment. The Result holds his words and the measure. Section 3.B "Cuts" is amended in place. The door repair of 3.A steps 1 to 3 moves first, as the prerequisite of the measure and of B's push door.
- Ruling 3 closes question 3 as recommended.

From Roman's words of 2026-11-03 09:50 and 09:58, written by session 535a30c6 on 2026-11-04:

- Section 3.B gains the paragraph "Shape against prose": the up-front whole read holds the index, the promises and the shape facts, and the on-demand read holds the words and the touched files. Each layer has its own measure.
- The shape layer's design and the understanding capability wait on his ruling, asked by session 535a30c6.

From frame 362's passes 4 to 4c, 2026-11-04, by session 9f60e445, measured on `qwen3:8b`:

- Step 2 of 4.2 changes. The survey wake no longer states commitments. It asked the 8B model for surfaces and for stated commitments in one wake, and the model mixed the two in every partial form: a party with no witness, a witness with no party, a statement on a line that names no function. Five door guards each refused one partial, and the four survey cases went to 0 of 5 (observed: the gate 3 and gate 4 reports of session 535a30c6, and `f362_door_shape_pass_report.md` of session 9f60e445).
- One kind of call per wake. The survey writes surfaces only, on the prompt and the system text of the green recordings. A second Architect mode, `commitments`, wakes after an area survey when the area has placed witness lines. The push carries the lines with their ids. The model names a pushed id, a party and a behaviour per line, and nothing else. The door fills the headline, the id and the bindings. Measured: 20 of 20 runs with no refusal on three of four fixtures, and the six survey cases 26 of 30 (observed: `f362_split_report.md`, `f362_pass4c_report.md`).
- A project-wide line is stated once, at the root, in one `commitments` wake with the pseudo area `@project-wide`. The door binds it to the harvester's `candidate_bindings` rows of that witness, 84 on icalendar, and never to an area's file list, which bound up to 422 rows over 8 areas with 316 test files among them (observed: `plans/f362-review-split.md`, point 2).
- The consumers of step 3 keep their push. The Tester's ask rides in the header of the pushed block and leaves the static prompt, because a static paragraph cost one of the two one-per-reply cases wherever it sat (observed: the register, hashes `3b7fee27`, `e30204aa`, `2d808f0c`).
- The Critic fails a broken pushed commitment through the pass hold's per-item question, the same form a criterion gets, because the model claims the commitment as a criterion at step 0 and a hold text after that never changed its judgement. Measured 4 of 5 (observed: `f362_door_shape_pass_report.md`).
