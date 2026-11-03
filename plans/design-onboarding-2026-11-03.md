# Design: an onboarding that delivers what the seats need (2026-11-03)

A design page for frame 362, after `plans/onboarding-demand-read-2026-11-03.md`. Read-only at 3ed009a9 on `rota/foundation`, and a read of the icalendar root `D:/tmp/rota-live/icalendar` at `99619246`. No model session started. No file changed except this page.

## Result

Recommend design B: the whole-project index and a deterministic harvest of commitment witnesses run before any request, and the model reads run only on the area that a request touches and its neighbours, with external commitments as a record that names the outside party, the behaviour and a witness line. The reason is the composition's: "no work happens that the Principal did not ask for", "every claim cites a source", and "a weak model is trusted only as far as the loop that checks it is short", and a witness line from the harvest gives a small model a source to cite and a reviewer a line to check. Build B as slices, the first one the icalendar commitments end to end, and hold design C, one stronger read per project, until that slice measures where the small model stops on commitments.

Questions for Roman:

1. Should the team read only the parts of the project that your job touches, and stop asking you to approve its notes on the whole project (ruling needed, recommended: yes)?
2. When a change breaks a promise the project makes to outside programs, and your request did not mention that promise, should the checker stop the merge (ruling needed, recommended: yes)?
3. When the small reader cannot state a promise in words, should the page show the raw line from the code and say that a small model could not state it (no ruling needed now, recommended: yes, and a bigger model only after a measure)?

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
| Liaison, the touch note | Which commitments bind this change? | No commitment line | `constraint_bindings` on the touched paths | Yes, and empty: no binding names a source path that a request touched (observed: m40, dry1 `termui.py`) |
| Liaison, `agenda` | Which open rows does the principal see? | 0 of 16 README-against-code `conflict` rows on a page | `ledger` through the agenda | Yes, and nobody acts on the rows (observed: the read, section 4) |
| Principal, the account and collision pages | none. He asked for no team rows | 235 names on m39, four collision pages of one sense written twice | `observed_entries`, `term_collision` | Yes, supply pushed at him (observed: predicates.py 673; the key score, section 3) |

## 2. The axes

| Axis | Options | What the facts say |
|---|---|---|
| When understanding is made | before any request, for the whole project; or from the request outward | The whole-project survey took 153 of 206 dry3 sessions and about 112 of 132 model minutes, and no row of it changed a delivery act (observed: the read, section 4). |
| Who makes it | deterministic tools; a small model per area; one stronger read | The index is deterministic and carried every merge (observed). The small model gets terms and the description right, 9 of 10 required terms and 0 of 7 traps hit, and gets commitments wrong, 0 of 5 (observed: the key score, section 1). |
| What it holds | facts; commitments; both | The briefs ask most for commitments, and the tables hold identifiers. The median constraint body is 43 characters (observed: the key score, section 1). |
| How it reaches a seat | a door that works; a brief line; a page | Three of the four delivery doors are broken in the wiring (observed: section 1 above). A push needs no thought from the model (observed: runner.py 4313, "Callable-with-no-arguments is the honest rule"). |
| What reaches the principal | the description, the touch line, his own questions, the Done line; or the team's rows | He asked only for the first group (reasoned: the read, section 3, the purpose line). |
| How it is measured | producer side, the answer key; consumer side, what a seat loaded and whether it acted | Today only the producer side exists (observed: the read, section 5). |

A small model stops at the commitments (observed: 0 of 5 on icalendar, 0 of 2 required on click and on ical_v0). The witnesses of all five icalendar commitments are lines a tool can find without a model (observed: section 4.1 below). So the gap is in the statement of a commitment, not in the search for its source (reasoned: the small model never saw the witness lines, because the survey reads at index depth, as the key predicted for `vBroken`).

## 3. Three candidate designs

The cycle prices come from `plans/operating-facts.md` line 250: a door text or a number is 2 cycles, an instrument fix is 3, a seam design with its night is 8 to 10.

### A. Repair the doors and keep the survey

What it does:

1. The pushed `glossary.lookup` reads the criteria's `term_refs`, not the wake refs. 2 cycles.
2. `batch_start`, `tests_missing` and `review` get the bodies of the constraints bound to the touched grains as a push. 2 to 3 cycles.
3. `constraints_for_grains` drops `k0` when every area has a survey record. 2 cycles.
4. The touch note reads the bindings of the guess. It exists, so 0 cycles.

Cost: about 7 cycles and a dry run read of 2 (reasoned). Keeps: the whole survey, its 153 sessions on icalendar, the account page and the collision pages. Cuts: nothing.

Failure case: the Developer of `bg_1` on icalendar touches `src/icalendar/caselessdict.py`. No constraint binds that path, because `icalendar_caselessdict` binds `docs/reference/api/icalendar.caselessdict.rst` (observed: the read, section 2). So the repaired push is empty. On a change to `_foldline`, the push holds rows such as `vrecur`: "icalendar.prop.recur.vRecur", and no row says 75 octets (observed: the key score, section 1). The doors connect, and they deliver rows with no promise in them (reasoned).

Measure: the share of delivery sessions whose push holds every `term_refs` sense, from 0 of 21 toward all. The seeded change of the fold to 76 octets, and whether the structural review files `violated`. A predicts no on the second measure (reasoned: no row holds the fact).

What it changes: one door family. No law, no seat form.

On 2,800 grains: the full survey cost again, about 112 model minutes, and the account page of 235 rows that frame 361 must still fix (observed: dry3). On 300 grains: on the order of dry2 tips, 35 sessions and about 4 minutes, and the doors work there too (observed: dry2 supply row).

### B. Understanding from the request outward

What it does:

1. Before any request, two deterministic tools run, and one model wake. The indexer writes the grains and edges, as today. A new harvester writes commitment candidates: each one a witness line with its path, its line number, its quoted text and its kind. The kinds: the package metadata (`description`, `requires-python`, `[project.scripts]`, the dependencies), README and docs claims that name a standard or say "compatible" or "supports", numeric defaults in a signature of a module that cites an RFC, comments that cite an issue, and the public exports of `__init__.py`. `orient` writes the description for m4 from the README and the index, as today, 2 sessions.
2. On a request, after the guess, the scheduler wakes the model reads for the touched areas and their neighbours only. The neighbours are the areas one edge away, or the parent directory when the area has no edge (reasoned: 313 edges for 2,800 grains is thin). The Architect states each commitment candidate of those paths as a record with the outside party, the behaviour and the witness, or declines it. The Terminologist defines the request's own words in the touched area, not the whole lexicon.
3. One door family pushes the commitments bound to the touched paths to the Developer, the Tester, the Critic and the structural review. The same push carries the senses of the criteria's `term_refs`.
4. A survey record per area stays valid while the area's hash holds, so a second request on the same area pays nothing (observed: `survey_records` stamps `area_hash`).

Keeps: the index, the description, the guess, the touch line, the area-hash rule and constraint zero. Constraint zero now honestly marks every area no request has touched (reasoned: law 12 says constraint zero "makes ignorance safe on day one", and B keeps ignorance outside the touch).

Cuts: the whole-project survey and `define` over every lexicon word, `reconcile`'s 39 to 41 sessions (the README claims become candidates), the account page of `observed_entries`, the `term_collision` pages, and the area accounts, which no delivery seat read (observed: the read, section 4). `challenge` runs on the commitments in play only.

Failure case: a change in `src/icalendar/prop/` to the way a value is parsed breaks the round trip of `vBroken`, and `cal/component.py`, which holds the `errors` list, is two edges away or in no edge at all. The neighbour rule misses the area, and the Critic gets no commitment for it (reasoned: the key binds `unknown_content_survives_round_trip` to `prop/` and `cal/component.py`). The repair is that a commitment binds every path its witness names, so the bind reaches across areas even when the read does not (reasoned). A second failure case: a request in everyday words that names no function. The guess then has less to start from, and B depends on the guess more than today does (reasoned: all three merges came from requests that named the function).

Measure: supply, the key's five commitments found whole with a witness that a person can check. Demand, the share of `batch_start`, `tests_missing` and `review` sessions whose push holds the commitments bound to the touched paths, from 0 today, and the seeded break of the fold filed as a finding. Cost, onboarding model minutes per request.

What it changes: law 12, in that "starved by positive survey records" applies to touched areas only, and constraint zero is the normal state of the rest. A record kind: the commitment candidate, and three columns on the constraint, the party, the behaviour and the witness. A seat's form: the Critic's "Anything the diff does outside the criteria is a remark" gets one exception, a broken commitment of the push. A door family: one push for all delivery seats. A page form: the account page and the collision pages go, and the ledger holds the team's rows for him to ask about.

On 2,800 grains: the Architect's survey cost about 46.5 minutes over 22 areas, about 2.1 minutes an area (observed: dry3 supply row). A request that touches one area and two neighbours costs about 6 to 7 Architect minutes and under 1 Terminologist minute, about 10 sessions with `orient` (reasoned: the per-area mean, unmeasured per request). That is about 8 minutes against about 112. On 300 grains the whole project is two or three areas, so B reads nearly all of it on the first request, and the cost is close to today's (reasoned: tips has 29 grains, dry2 onboarding cost about 4 minutes).

Build cost: the harvester, an instrument, 3 cycles. The record kind and the push door, a seam design with its night, 8 to 10. The survey wakes fired from the guess and not from boot, a second seam, 8 to 10. The cuts of three pages and `reconcile`, about 2 each, 6 to 8. Total about 25 to 30 cycles, in slices (reasoned).

### C. B, with one stronger read per project for the commitments

What it does: B, and one session on a stronger model reads the harvest's candidates for the whole project once, and writes the commitments. The small model still writes the terms and reads the touched area.

Price on the box: `qwen2.5:14b-instruct-q3_K_M` runs at 75% GPU and 153 seconds a turn, and keeps "judgement parity", which is not a measured gain on commitments (observed: operating-facts line 96). The 27b models overflow by about 8 GB and run minutes a turn (observed: line 102). So one read of 10 to 20 turns costs 25 to 50 minutes on the 14b, and a 27b read costs hours (reasoned). A hosted model is faster and makes rota depend on a service outside the box. The destination says "a careful person runs rota alone" (reasoned: whether a hosted model breaks "alone" is his to say).

Keeps and cuts: as B. The commitments of areas no request touched now exist too.

Failure case: the stronger model states the fold commitment as "lines fold at 75 characters", a number present in the file with the wrong unit. The page then shows a confident wrong promise, and the Tester writes a test on characters (reasoned: the key names "75 octets, not characters" as the trap, and no stronger local model was scored against the key).

Measure: as B, and the stronger read against the small read on the same candidates, five commitments each.

What it changes: as B, and a model profile per wake kind. The destination's honesty line moves: rota says that small models stop at commitments and that it buys them with one stronger read (reasoned).

On 2,800 grains: B's cost, and one stronger read of all candidates. On 300 grains: B's cost, and a stronger read of few candidates, so the read is small but the reload of a second model in each direction is a fixed cost (observed: line 97, "A model swap costs a reload in each direction").

Build cost: B, and 3 to 5 cycles for the profile, the one-shot wake and its key score (reasoned).

### 3.4 The contract of design B

One row per record kind. "Supply" is the producer's measure against the key. "Demand" is the consumer's outcome.

| Record | Producer | Source | Provenance | Consumer | Moment | Door | Supply measure | Demand measure |
|---|---|---|---|---|---|---|---|---|
| grains and edges | indexer | the code | observed | guess, Developer probe, touch line | before any request | `code.callables`, `code.probe` | the key's counts re-cut on today's indexer | the guess's paths hold the diff's paths |
| description | Vision Keeper `orient` | README, the index | reasoned | the principal on m4, the Vision Keeper on signoff | before the first request | m4, `problem.consult` | the key's Q1 and the five items | his "ok" in one turn |
| commitment candidate | harvester | metadata, README, docs, signature defaults, issue comments, exports | observed | the Architect's touched-area read | before any request | pushed to that read | the key's five witnesses present | share of stated commitments that cite a candidate |
| commitment | Architect, touched-area read | candidates and the source of the touched paths | reasoned, with an observed witness | Developer, Tester, Critic, structural review, touch line | after the guess, before the criteria | one push from the touched paths | the key's five commitments whole | seeded break filed as a finding, a test that guards the behaviour |
| term in context | Terminologist | the item's words and the touched area | reasoned | criteria `term_refs`, Developer, Tester | criteria | the push from `term_refs` | required terms and traps of the touched area | share of delivery sessions whose push holds every `term_refs` sense |
| unsurveyed ground, `k0` | scheduler | the survey records | observed | touch line, structural review | each batch | `constraints_for_grains`, `k0` dropped where the touch is surveyed | no area of the touch under `k0` | the review sees a real row, not `k0` |
| challenge verdict | Critic `challenge` | the commitment and its witness | reasoned | the push filter: a falsified commitment does not bind | after the read | `challenges` | falsified share on the key | no seat gets a falsified commitment |

Cut, because no consumer reads the record to effect: the README `conflict` rows, the area accounts, the whole-lexicon glossary rows (observed: the read, section 4).

### 3.5 What reaches the principal

| Reaches him | Never reaches him unasked |
|---|---|
| The description once, on m4 | The account page of observed rows |
| The touch line with the commitments the change must keep | Term collisions between the team's own rows |
| His own open questions, and a commitment that a request contradicts | Re-survey notes after a merge |
| The Done line | The team's rows in bulk. They stay in the ledger, and the Liaison shows them when he asks |

The cases decide as follows (reasoned: the purpose line, both halves):

- Frame 361's page of 235 rows does not exist under B. A first baseline is the index and the description, so the size bound of frame 361 is not needed. The rows stay visible in the ledger and countable on the state line.
- Frame 358's re-survey after a merge writes rows to the ledger and no page. Under B a re-read happens only when a later request touches a changed area.
- The four term pages on dry3 go. A real ambiguity, such as `timezone` with three senses, reaches him only when it changes what his request means, as a question the Liaison originates and that names the row (observed: the composition, "the question names the row it is about").

### 3.6 The cost bound

| Project | Today, onboarding | A | B, the first request | B, a later request on the same area |
|---|---|---|---|---|
| tips, 29 grains | 35 sessions, about 4 min | the same | about the same | 0 |
| click, 1,188 grains | 110 sessions, about 28 min | the same | about 10 sessions, under 10 min | 0 |
| icalendar, 2,800 grains | 153 sessions, about 112 min | the same | about 10 sessions, about 8 min | 0 |

(observed: the "Today" column, the read, section 4; reasoned: the B columns from the per-area means). The bound under B: the touched areas and their neighbours, capped at four areas a request, times the per-area cost, and `orient` once. The cap is a design number, not a measure (reasoned).

## 4. The first vertical slice: the icalendar commitments, end to end

### 4.1 The witnesses exist, and a tool can find them

All read at `99619246` (observed):

- `pyproject.toml` line 42: `description = "RFC 5545 compatible parser and generator of iCalendar files"`. Line 58: `requires-python = ">=3.10"`. Lines 139 and 140: `[project.scripts]`, `icalendar = "icalendar.cli:main"`.
- `src/icalendar/parser/string.py` line 119: `def _foldline(line: str, limit: int = 75, fold_sep: str = "\r\n ") -> str:`. Line 140: "escapes across a folded line boundary. See issue #1501."
- `src/icalendar/tests/test_icalendar.py` imports `_foldline` and holds "We do not fold within a UTF-8 character" at line 77.
- `vBroken` appears in 21 lines of tests.
- `src/icalendar/__init__.py` imports from `icalendar.alarms`, `icalendar.cal`, `icalendar.enums`, `icalendar.error` and `icalendar.parser`.

So the harvester finds a witness for each of the key's five commitments with no model (reasoned: each kind in 3.B step 1 matches one line above, and the timezone back ends are in the dependencies).

### 4.2 The slice

1. The record. A table of commitment candidates: id from content (law 14), path, line, quoted text, kind. Three columns on `constraints`: `party`, `behaviour`, `witness`, and a binding to every path the witness names.
2. The producer. The harvester in `rota/onboarding/`, run at boot after the indexer. The Architect's survey wake of the touched area gets the candidates of its paths pushed, and a brief line: state the party, the behaviour and the witness, or decline.
3. The consumers. The Tester's `tests_missing` gets the commitments bound to the touched paths, and one brief line: a test guards each pushed commitment whose behaviour the change can reach, from the witness's input and output. The Critic's `review` gets the same push, and one brief line: a diff that breaks a pushed commitment is a finding, not a remark.
4. The door. One read with no argument, so `push_working_set` sends it unasked: the commitments bound to the batch's touch set, with `k0` dropped where the touch has a survey record (observed: runner.py 4313, the push rule).
5. The page line to the principal. The touch line gains one part, for example: "This change touches `src/icalendar/parser/string.py`. It must keep: lines fold at 75 octets, because other calendar programs read the files." No other understanding text reaches him.
6. The measure. The dry run sentence: "When icalendar writes a long line, fold it at the last space before the 75-octet limit, so that a word is not split, and keep everything else as before." The sentence touches `_foldline`. Count on the run:
   - Supply: the five key commitments in the candidates, each with its witness, and with the dry3w7 copy as the red test today at 0 of 5.
   - Demand: `rfc_5545_conformance` and the issue #1501 carve-out in the Tester's and the Critic's push. A test that a line of multi-byte characters folds at 75 octets or fewer. The other three commitments absent from the push, because the change does not reach them.
   - The seeded break: the same batch replayed with `limit=76`, or with a fold inside a backslash escape, and whether the Critic files a finding.
   - The principal: one touch line with the commitment, and no other page from understanding.
7. The control. The key's counts re-cut on today's indexer, so the 1,731 grains in 9 areas of the key match the 2,800 in 22 of the run (observed: the key score, section 4).

Price: the harvester, 3 cycles. The table, the columns and the push, 2 to 3. The two brief lines with their register cases, 2. The dry run and its read, 2 to 3. The key re-cut, 1. About 10 to 12 cycles, about half of the twenty cycles that a session holds after its wake (reasoned: operating-facts line 250). The slice does not need the request-outward scheduling of B step 2. It runs on today's whole survey, so it tests the record and the doors first, and the scheduling later.

## 5. The recommendation

Recommend B, built from the slice in section 4. The reasons, in the composition's words:

- "The structure holds a model of its shape, terms, boundaries, and external commitments, as records observed from the code." Today it holds the first three and not the fourth (observed: the key score). The harvest gives the fourth an observed witness.
- "Every claim cites a source. A seat can check the claim against the source." A commitment with a witness line is checkable. A 43-character body is not (observed: the key score).
- "A weak model is trusted only as far as the loop that checks it is short." The small model states a commitment from a line it is given. The Tester's test and the Critic's finding check it on the same batch (reasoned).
- "No work happens that the Principal did not ask for." The whole-project survey is 112 minutes of work no seat used, and it pushed 235 rows at him (observed: the read, sections 4 and 6).

A alone is not enough, because the repaired doors deliver rows that hold no promise (reasoned: section 3.A failure case). The door repairs of A are inside B's push, so none of A is lost. The lookup fix of A step 1 is a wiring bug, 2 cycles, and it can go first with no ruling (reasoned: it delivers what the briefs already ask for). C waits for the slice's measure: if the small model with the witness lines states 4 or 5 of 5, C buys nothing, and if it states 2 or fewer, C is the next frame (reasoned: the destination's honesty line asks for the measured place where small models stop).

### The questions for Roman, in plain words

1. **The scope of the reading. Needs his ruling.** On 26 August you ruled that the team's first picture of a project is your call, and no session decides it. The design departs from that ruling. Today, a new team on a big project spends most of the day reading every room of the building before you ask for anything. Then it hands you 235 notes to approve or drop. Under the design, the team reads the floor plan and the promises on the front door first. Then it reads only the rooms your job touches, and you see one line with what the job must keep. The rest of its notes stay in the log, and you see them when you ask. Recommended answer: yes, read only what the job touches, and stop the approval page.
2. **A broken outside promise stops the merge. Needs his ruling.** You ask the team to fold long lines at a space. The checker sees that the change also splits a character across two lines, and other calendar programs reject such a file. Today the checker writes this as a side remark, and the change merges. Under the design, the checker reports a fault, and the builder fixes it before the merge. The fix is work your request did not name, and it keeps a promise your project already makes. Recommended answer: yes, a broken outside promise is a fault.
3. **Where small models stop. No ruling needed now.** The small reader finds the line `limit = 75` but cannot say in words who depends on it. Under the design, your page shows the raw line and says that a small model could not state the promise. A bigger model once per project could state it, at 25 to 50 minutes on the box or with a paid service. Recommended answer: show the line now, and decide on the bigger model when the first slice measures the gap. This returns to him only if the measure shows 2 or fewer of 5.

## Doubts

- All three merges came from requests that named the function (observed: the read, section 2). B leans on the guess, and a request in everyday words is not yet tested. A dry run sentence with no symbol name must come before B's scheduling slice (reasoned).
- The harvester's kinds are drawn from one project, icalendar. A numeric default in an RFC module and an issue comment may be icalendar's habits. The control is click and tips, and the harvester must be scored there before it counts (reasoned: "I want to prevent over fitting", ruled 2026-10-15). On click the commitments are command-line behaviour, and `[project.scripts]` and the exports may be the whole yield (reasoned, unread).
- The B cost per request is the per-area mean of dry3, not a measure. A touched area like `src/icalendar` with `attr.py` of 2,624 lines may cost far more than the mean (observed: the key; reasoned).
- I reject A on the content of the rows, not on a measured outcome. A dry run with A's door fixes could show that some rows help. The lookup fix is cheap enough to test that, and it is in the recommendation as the first step (reasoned).
- Law 1 asks for one writer per row. The harvester writes the candidate and the Architect writes the commitment. That holds only if the commitment is a separate row, and the three new columns on `constraints` must not be filled by the harvester (reasoned).
- The Critic's exception widens what can stop a merge. A false commitment with a real witness line could stop good work. The slice's challenge on each commitment in play is the guard, and its false-stop rate is unmeasured (reasoned).
- Under B, constraint zero covers most of a large project for ever. The touch line must then not say "nobody surveyed" on every change, or it becomes noise to him. The line names only the unsurveyed ground inside the touch (reasoned).
- The demand read was one agent's read of three runs. Its "no delivery seat acted" is in part a result of the broken doors, so the demand for terms may be larger than the runs show once the doors connect (reasoned).
- The description stays a whole-project read. Its sole consumer of note is m4, and his "ok" on m4 is a light check. Whether he needs the description at all is not asked here (reasoned).

## Usage

About 95k tokens and 15 tool calls. No model session, night, gate or dry run started. One file written in the repository, this page.
