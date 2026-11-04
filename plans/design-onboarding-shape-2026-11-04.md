# Design: the shape layer of onboarding (2026-11-04)

Frame 362. One design iteration of the up-front shape facts of `plans/design-onboarding-2026-11-03.md`, section 3.B, "Shape against prose", for capability 11 of `rota/COMPLETION.md`.

## 1. Result

Hold the four shape facts with no model and no new survey. Copies of one function are a query on `code_index`, which holds them today. Shared helpers need one new mechanical table, `code_calls`, which the indexer writes: one row for each resolved call from a file to a top-level definition, through `__init__.py` re-exports, with the resolver shared with the harvester's binding rule. Disagreements are the harvester's `contradicts` group, plus a later variant group: one method that two or more subclasses of one base override with different bodies. Boundaries are the `export` grains of the index, plus two new harvester kinds: `entry_point` (a `[project.scripts]` target, a `__main__` guard, a README run line) and `intake` (`testpaths`, the change-log rule). The harvester runs again after each merge, beside the index refresh. One door family carries the facts. It pushes the shape of the touch beside `bound_constraints` to the Developer, the Tester, the Critic and the structural review. It marks copies and their entry-point reach in the guess's `code.callables`. It gives the Architect's read-only `ask` one read, `model.shape(name)`. The up-front cost on icalendar's 2,800 pinned grains is about 1.5 deterministic seconds and 0 model minutes, and the same after each merge. Each fact kind has a keep rule, set before any measure (section 6.1). The order builds `entry_point`, `intake`, `code_calls` and the copies query first, measures, and builds the variant kind only if its rule passes. The build is about 24 to 26 cycles priced for the shape layer, about 38 to 42 at the actual rate, and about 36 to 41 priced, about 58 to 65 actual, with the slice's passes 2 to 4, so about three sessions.

Predictions, one number per measure (reasoned: section 4):

- Answers: on the icalendar consult set, the new shape records add 0 points. A door over records that exist today adds 2 (Q5 from the `export` grains, Q8 from the script candidate), so 4.5 of 8, from 2.5 today (observed: `plans/dry3-key-score-2026-11-03.md`, section 1, last paragraph). The gain shows only after `probes/consult.py` gains a shape section, about 3 cycles (section 4.1).
- Future work: a shape fact disarms the trap of 4 of the 12 blind test tasks (T2, T3, C3, I2), 2 more partly (T1, C4), and 6 have none from shape (T4, C1, C2, C5, I3, and I1, which moves to the commitment layer). Before the variant kind, 3 are disarmed (T2, T3, I2) and C3 is partly. The `intake` kind also carries the landing check and the change-log check of every task.
- Operation: on a touch of `get_duration_property`, the I2 request, about 2 of 10 writing tool calls of the Developer, the Tester and the Critic cite a pushed id or grain, from 0 today. The count is defined in section 4.3.

## 2. What exists

| Part | What it carries today | Source |
|---|---|---|
| `code_index` | Top-level definitions as `path::name` symbol grains, with `line_start` and `line_end`. Two definitions of one name are two grains, so a `GROUP BY` on the name after `::` finds them. Methods are not indexed. | observed: `rota/core/schema.sql` 461 to 482; `rota/onboarding/indexer.py` 147 to 149, "Do not descend" |
| `code_index`, kind `export` | Each `__all__` entry, a boundary of the package. icalendar holds 261 such grains, 84 in the top `__init__.py`. click has no `__all__` and no `export` grain. | observed: schema.sql 463 to 467; indexer.py 152 to 165; probe |
| `code_edges` | File-to-file import edges, `(src, dst)`, not calls. An import through a re-export ends at `__init__.py`, not at the defining file. | observed: indexer.py 486 to 493 and 101 to 123; deep dive, section 3 |
| `areas.propose` | An area is a directory checked against the import graph. `Proposal.crossing` counts import edges between areas, so a cross-area import is countable today and a cross-area call is not. | observed: `rota/onboarding/areas.py` 1 to 20, 140 to 162, 236 to 250 |
| `fan_in` | A count of import edges into a path grain. Symbol grains always hold 0. | observed: indexer.py 495 to 497, 521 |
| `glossary_terms`, `survey_records` | A sense holds `term`, `sense_short`, `sense_body`, `area`. A survey row holds `area`, `outcome`, `refs`, `area_hash`, `commit_sha`. Neither holds a shape fact. `glossary.lookup` and `model.consult` read them. | observed: schema.sql 202 to 210, 302 to 310; `rota/roles/api.py` 3686, 4587 |
| `harvest.py` | Seven candidate kinds, a content id, and the `contradicts` group: one number in two units of one family. The binding rule binds candidates to files. `boot.py` runs it after the indexer. No door reads `commitment_candidates` yet. | observed: `rota/onboarding/harvest.py` 1 to 31, 393 to 427, 491 to 524; `rota/onboarding/boot.py` 119; grep of `rota/roles` and `rota/core` |
| `bound_constraints` | The push of the constraints that bind the batch's files, with no argument, to the Developer at `batch_start` and the Tester at `tests_missing`. The Critic's `review` gets no push. | observed: api.py 4214 to 4240; `rota/core/runner.py` 4424 to 4440 |
| `constraints_for_grains`, `model.consult` | The structural review's reads of constraints by grain. | observed: `rota/core/scheduler.py` 3189; api.py 4587 |
| `boundary_subjects`, `code.boundary`, `code.front` | The boundary files enumerated from the index: the authoring surface and the root manifests. `code.boundary` reads a boundary file and its importers. `code.front` reads the manifest, the README and the declared entry point for `orient`. | observed: scheduler.py 1389 to 1403; api.py 19985 to 20007, 18729 to 18745 |
| `code.callables` | The Architect's guess sees every symbol whose name shares a word with the request. It shows both copies of `calculate_tip` when the request names it, but nothing marks them as copies. | observed: api.py 20081 to 20100; `architect/guess.tools` |
| The inquiry route | The Liaison sends `ask` to an owner, which runs read-only. The Architect's `ask` holds `model.consult`, `model.load`, `decisions.search` and no code read. So a principal's question about shape reaches records only through those reads. | observed: runner.py 112 to 120; `rota/roles/prompts/architect/ask.tools` |
| `probes/consult.py` | Asks the three owners in turn from their artefacts. The Architect's artefact is `model_areas` and `constraints` only, and the probe calls no `.tools` read. `probes/downstream.py` holds the eight questions of the Obsidian plugin project. The icalendar set is `probes/ical/questions.py`, keyed in `probes/ical/answer_key.yaml`. | observed: consult.py 1 to 22, 44 to 57, 107 to 140; ical/questions.py 1 to 5; the review, finding 1 |
| `indexer.refresh` | After a merge, `refresh(main=True)` rebuilds the index and pins the areas again. It calls no harvest. `boot.py` is the one caller of `harvest.record`. | observed: indexer.py 608 onwards; boot.py 119; the review, finding 3 |

## 3. The four shape facts

The probe is `shape.py` in the probe directory of section 8. It ran first on the dive's trees, icalendar `99619246`, click `2c8cd3a` and tips `99101f1`. The review ran it again on the blind test's pinned commits, tipsI `ff1f65f`, clickI `09c82f3` and icalendarI `4f12af1e`, with grains 29, 1,188 and 2,800. Every count below is the same on the pins (observed: the review, point 1, `rshape/out/pin_<repo>.json`). So the counts of this section are taken on the pinned commits. Only line numbers, grain totals and one similarity changed, and the tables give the pinned values. "True" below is my read of a sample of ten, or of all rows when fewer: would a designer of a change want this fact (reasoned).

### 3.1 Copies of one function

Rule: two top-level definitions of one name in two source files, tests, examples and dot-directories left out by `areas.is_attached`, dunder names left out. A copy pair carries whether each side is reachable from a boundary of 3.4. It carries no call count. On tips `code_calls` holds 0 rows, because `main.py` calls its own copy inside `main.py` and the tests are attached files, so the count is 0 and 0 and cannot tell the live copy from the dead one (observed: the review, finding 9). The entry-point join tells them apart.

Record: none new. The index holds it, and the door runs the query (reasoned: the indexer is the one writer of `code_index`, law 1, `rota/LAWS.md` section 1, and a query adds no writer). Methods stay out of the index. A method copy reaches a reader through the variant group of 3.3.

| Repository | Pairs | True | Notes |
|---|---|---|---|
| tips | 2 | 2 of 2 | `calculate_tip`, bodies similar 0.88 on the pin; `display_results` at `main.py:6` and `tip_calculator.py:13`, other arguments, and the `tip_calculator.py` side has no caller |
| click | 1 (7 with dunders, 10 in the index) | 1 of 1 | `get_pager_file`, the wrapper in `termui.py` and the work in `_termui_impl.py`. The 6 dunder pairs are module `__getattr__` shims |
| icalendar | 3 | 0 of 3 | all three are `main` of three tools |

(observed: probe.) Method pairs that share a name and are 0.8 alike: icalendar 123, 0 of 10 true in the sample (`to_jcal`, `example`, `ical_value` boilerplate); click 5, 5 of 5 true (the shell formatters and the usage errors) (observed: probe). That is why method copies stay out of this fact.

A model adds nothing. Which copy is live is a join with 3.4, not a judgement (reasoned: tips `main.py` has the `__main__` guard and the README line, `tip_calculator.py` has neither).

Readers: the Architect at the guess. `code.callables` marks each row that has a copy, and says which side an entry point reaches, so the guess names both copies or the live one (build step 4, 2 cycles). This is the reader that decides the place for T2 and T3, because the push of 3.5 reaches the Developer only after the guess wrote the touch, and the Developer can then only stray through `touch_strayed` (observed: the review, finding 2). A copy of a guessed symbol also becomes a rank 1 entry of the caller rule, the fix the dive asked for (observed: deep dive, section 3, tips `b_1`). The Developer, the Tester, the Critic and the structural review through the shape push of 3.5. The Architect's `ask` through `model.shape`.

### 3.2 Shared helpers

Rule: a top-level definition that two or more non-attached source files call, the definer left out, with the call resolved through `from` imports, module aliases and `__init__.py` re-exports. The rule counts files, not areas. The area rule misses the blind test's own case: `get_duration_property` has two caller files, `cal/event.py` and `cal/todo.py`, in one area (observed: probe). On click the area rule finds 0, because one area holds all 17 source files (observed: probe).

Record: a new table `code_calls (src, dst_grain)`, written only by the indexer in the same transaction as `code_edges` (reasoned: a call row is mechanical and rebuilt, as an edge is; law 1). It must not join `code_edges`, because `areas.propose` reads every edge as coupling, and call rows would move the partition (observed: areas.py 239 to 250). The same table gives the caller rule of 3.B step 5 its rank 1 through re-exports, which `probes/callers.py` of the dive did by hand (reasoned). The call resolver lives beside `_reexported` on `harvest.Tree`, and it shares one module map with the binding rule. The indexer calls it and stays the one writer of `code_calls`. The reason: the indexer resolves imports in `resolve`, and the harvester resolves re-exports in `_reexported`, so a third resolver on its own could disagree with both on one package (observed: indexer.py 214; harvest.py 468; the review, finding 10).

| Repository | Resolved cross-file targets | Called from 2 or more files | From 2 or more areas | True in sample |
|---|---|---|---|---|
| tips | 0 | 0 | 0 | none to read |
| click | 54 | 13 | 0 | 8 of 10; `BadParameter` and `Abort` are exceptions |
| icalendar | 65 | 34 | 15 | 6 of 10; noise is value types (`vText`, `vDatetime`), an exception, a container class |

(observed: probe.) The resolver sees only calls by name and through a module alias. It does not see `self.x()`, an instance's method, or a lookup by string, so `TypesFactory` is not a target (observed: probe; the dive's doubt on `TypesFactory`). A filter that drops exception classes takes the click sample to 8 of 8 (reasoned).

A model adds nothing to the fact. A model reads a helper's callers only when a request touches the helper, inside the delivery session (reasoned).

Readers: the shape push of 3.5, where a touched helper lists its other caller files. The Tester gets the test files that call it, from the same table, as witnesses (observed: probe, `test_files` column; icalendar has 41 targets with a test caller).

### 3.3 Disagreements

Two rules, one group.

1. The unit group, as built: one number in two units of one family. The harvester writes it in `contradicts` (observed: harvest.py 393 to 427).
2. The variant group, later: one method name that two or more classes with one base override, with bodies that differ. The base is matched by name across all source files. Overloads in one class count once. Getter and setter pairs in one class do not inflate the count (observed: the review, `variant.py`, 10 of 10 click groups and 31 of 31 icalendar groups hold).

Record: the unit group stays where it is. The variant group goes in the harvester's record as a candidate of a new kind `variant`, one row per member method, with the members' ids in `contradicts` (reasoned: the column already means "these lines state the same thing another way, quote both", and the harvester is already the one writer of that table, law 1). The variant kind is not built in the first pass. It is 3 of 10 true on icalendar, it needs a cap on members, and it widens what `contradicts` means. A touch of `cal/event.py` pushes 9 lines, with `new` and `example` as noise (observed: the review, finding 6, `pushsize.py`). It is built only if its keep rule of section 6.1 passes.

| Repository | Unit groups | True | Variant groups | True in sample |
|---|---|---|---|---|
| tips | 0 | none | 0 | none; the copy pair of 3.1 with other bodies is the disagreement here |
| click | 0 | none | 10 | 7 of 10; noise is two `ABC` groups across hierarchies and `get_error_hint` |
| icalendar | 1 | 1 of 1, 75 octets against 75 characters | 31 | 3 of 10; `set_start` and `set_duration` of `Event` and `Todo` are true, the `PYTZ` and `ZONEINFO` backends are noise as a disagreement and `example` is noise |

(observed: probe.) The click groups hold `format_completion` over the four shells, which is the C3 trap, and `to_info_dict` of `Option` and `Argument`, which is the C4 trap (observed: probe). The icalendar groups hold `duration`, `start` and `end` over `Event` and `Todo`, beside the I2 trap (observed: probe).

A model adds the content of the disagreement: "zsh passes a newline through, PowerShell collapses it". The rule finds where siblings differ, not how. A small model on two pushed method bodies of 10 to 20 lines may say how they differ. That is unmeasured, and the design does not depend on it (reasoned). The model reads a group only when a request touches a member, in the Developer's or the Critic's session that already runs, so no new wake exists.

Readers: the shape push of 3.5 names the group and the member lines. The Critic reads it at `review` as a remark source, not a fail source (reasoned: ruling 3 of 2026-11-03 makes a broken outside promise a fail, and a variant is no promise).

### 3.4 Boundaries

Rule, three parts:

1. Exports: the `export` grains of a top-level `__init__.py`. Where no `__all__` exists, the public names that `__init__.py` binds by import.
2. Entry points: each `[project.scripts]`, `gui-scripts` and `entry-points` target; each source file with an `if __name__ == "__main__"` guard or named `__main__.py`; each README line that runs `python <file>`.
3. Intake: `testpaths` of `[tool.pytest.ini_options]`, the `[tool.towncrier]` fragment rule, and a change-log file with an unreleased heading.

Record: exports stay in the index. Entry points and intake become harvester kinds `entry_point` and `intake`, with the binding rule `entry_point` that exists (observed: harvest.py 503 to 506). Script targets are `metadata` candidates today, so `entry_point` takes them over (observed: harvest.py 12 to 13). Three costs come with the kinds (observed: the review, finding 7, `widen.py`):

- The `kind` CHECK of `commitment_candidates` refuses the new kinds, and `init_db` widens three other tables only. So a `_widen_candidate_kinds` step is needed (observed: `rota/core/db.py` 427 to 429; schema.sql 274 to 278).
- The id hashes the kind. A script row that moves from `metadata` to `entry_point` gets a new id, and the old row goes stale.
- The `bind` branch at harvest.py 503 keys on `metadata`, and it moves to `entry_point`.

The harvester runs again after each merge. `indexer.refresh(main=True)` calls `harvest.record` after `build`, on the merged commit (reasoned: today only `boot.py` 119 calls it, so after the first merge the `entry_point` and `intake` rows, and the unit group, would describe the onboarding commit while `code_calls` describes the new one; the review, finding 3). `harvest.record` writes nothing for a commit it has read, so a refresh with no new commit costs one query (observed: harvest.py 541 to 545).

| Repository | Exports | Scripts | `__main__` guards | README run lines | Intake | True |
|---|---|---|---|---|---|---|
| tips | 0 | 0 | 1, `main.py` | 1, `python main.py` | none | 2 of 2 |
| click | 65 by import, no `__all__` | 0 | 0 | 1, `python hello.py`, an example | `CHANGES.md` | exports true by definition; the run line is noise |
| icalendar | 84 in `__all__` | 1, `icalendar = icalendar.cli:main` | 4 | 0 | `testpaths`, towncrier | exports and script true; guards 2 of 4, the fuzzer and `cal/lazy.py` are noise |

(observed: probe; `pyproject.toml` 294 to 312 of the icalendar tree.) An export is true by definition. The fact a designer needs is the join: "the touched name is public" (reasoned).

A model adds nothing. A script target's first docstring line comes with the row by rule, so the Architect can say what the command does (reasoned: consult question 8).

Readers: the shape push of 3.5 says "public" or "entry point" beside a touched grain. The Tester and the Developer get the intake rows at every delivery wake, so a test lands where `testpaths` collects it and a change carries its fragment (reasoned: the blind test's landing check and commit 08aab3c8, `plans/understanding-test-blind-2026-11-03.md`, section 2). The Architect's `ask` reads exports and scripts through `model.shape`.

### 3.5 The door family

One push, one read and one mark on the guess, all beside the doors that exist (reasoned: the touch files that `bound_constraints` computes are the right key, api.py 4228 to 4240).

1. The push, `shape_of_touch(batch_id)`, no argument. For each touched file and grain: its copies, its other caller files and test callers, its variant groups with member lines, and whether it is exported or an entry point. The intake rows always come with it. It rides the push of runner.py 4424 to 4440 and is extended to the Critic's `review` and to the structural review.
2. The read, `model.shape(name)`, with an argument, in `architect/ask.tools`. It answers "where does X live, every copy, who calls it, is it public". The match rule is the word match of `code.callables`: the words of `name` against grain names, export names and the `Class.method` form, with identifiers split as `code.vocabulary` splits them, and every hit is returned (reasoned: the `ask` has no code read to find a name it lacks, and Q5 names `from_ical`, a method that `code_index` does not hold; the review, finding 8). A question in everyday words that matches no name gets no shape row, and the reply says so. This is a new op with a body and a `.tools` line, not a door text.
3. The guess, `code.callables`: each returned row gains a `copies` field and an `entry_point` field from the same queries. No new `.tools` line.

The push keeps the cut rule of the push it rides: after the criteria block (observed: runner.py 4434 to 4440).

## 4. The measures, predicted

### 4.1 The icalendar consult questions

The set is `probes/ical/questions.py`. The eight questions of `probes/downstream.py` are the Obsidian plugin project's, and this probe does not run on TypeScript (observed: downstream.py 33 to 72; reasoned: the rules use Python's `ast`).

Only a gain from a record that this design adds counts as a shape gain. A gain from a door over a record that exists today is listed apart (observed: the review, finding 1).

| Q | Question, short | Today | Record that answers it | Gain from a new shape record | Gain from the door over a record that exists |
|---|---|---|---|---|---|
| 1 | Text to a Calendar and back | partly | the `export` grain `Calendar`, the preservation candidate for `vBroken` | 0 | 0; the round trip is the commitment layer |
| 2 | What a component is, how it nests | partly | the glossary | 0; the variant kind is deferred | 0 |
| 3 | Property against parameter | partly | the glossary only | 0 | 0 |
| 4 | Where DTSTART becomes a datetime, `TypesFactory` | missed | none; the resolver does not see the factory lookup | 0 | 0 |
| 5 | Rename `Calendar.from_ical`, who notices | missed | the `export` grain `Calendar`, which the indexer writes today | 0 | +1, to whole |
| 6 | An unparseable value | partly | the preservation candidate | 0 | 0 |
| 7 | VTIMEZONE to tzinfo | partly | the `tzdata` dependency candidate | 0 | 0 |
| 8 | The `icalendar` command | missed | the `metadata` script candidate, which the harvester writes today; `entry_point` only renames it | 0 | +1, to whole |

(observed: harvest.py 12 to 13, 503 to 506; schema.sql 463 to 467; the review, finding 1.) So the new shape records, `code_calls`, the copies query, the guards, `intake` and the variant kind, add 0 points on this set. The door adds 2 points, to 4.5 of 8 at half a point for partly, against 2.5 today (reasoned). The consult set asks about the project as a user sees it, and the new records serve a change, so the future-work measure of 4.2 is where they must show.

The instrument does not see the door today. `probes/consult.py` gives the Architect `model_areas` and `constraints` only, and it calls no `.tools` read (observed: consult.py 44 to 57, 128 to 140). The change: a `shape_for(conn, question)` section in the Architect's artefact, built like `glossary_for` from the question's words with the match rule of 3.5 item 2, over the `export` grains, the script and `entry_point` candidates, the copies query and `code_calls`. The cost is an instrument fix, 3 cycles, build step 7 (reasoned: `plans/operating-facts.md` line 250). The other route, scoring through the live `ask` of a dry run, needs no probe change but needs a run per question set.

### 4.2 The twelve blind test tasks

| Task | Trap | Shape fact that disarms it |
|---|---|---|
| T1 | a second check where both copies already raise | copies, partly: both copies are named; "already done" still needs a read of the bodies and the test |
| T2 | edit the unused `display_results` | copies with the entry point, read at the guess through the mark of build step 4: the `main.py` copy is the one the guard and the README reach. Without step 4 this is partly, because the push arrives after the guess |
| T3 | change one copy only | copies, at the guess (step 4) and at the Critic's `review`, which sees the diff and the copy push |
| T4 | the rounding of the receipt | none |
| C1 | a second suggestion path | none; a feature that exists is a code read |
| C2 | a frozen `version_option` | none; a maintainer ruling is a commitment kind the harvester lacks |
| C3 | edit the template or `CompletionItem` | the `format_completion` variant group, and `CompletionItem` as a helper with two caller files. Before the variant kind, the helper alone, so partly |
| C4 | `Option.to_info_dict` only | partly: the `to_info_dict` variant group of `Option` and `Argument` names the two overrides, and the change belongs in `Parameter.to_info_dict`, the base, which no shape fact names; intake carries the change-log line |
| C5 | auto-correct against a documented refusal | none; the harvest finds no line of `docs/why.md` |
| I1 | rewrite the fold to count characters | none from shape. The unit group is the pass 1 harvester row, and the commitment push of pass 2 reads it. The right outcome is "already done", which falls before a batch exists, so a push at `batch_start` is late. The docs side says "75 characters", so the push carries the code side, `parser/string.py` 122, as the binding fact (observed: harvest.py 393 to 427; the review, finding 4) |
| I2 | clamp the shared duration helper | `get_duration_property` as a helper with two caller files, `event.py` and `todo.py` |
| I3 | delete the comma escape | none from shape; the RFC 5545 standard candidate is the commitment layer's |

(observed: probe for every named fact; `plans/understanding-test-blind-2026-11-03.md`, section 2, for the traps.) With the full design: 4 disarmed (T2, T3, C3, I2), 2 partly (T1, C4), 6 none from shape. Before the variant kind: 3 disarmed (T2, T3, I2), 3 partly (T1, C3, C4). The trap facts are present on the pinned commits: `CompletionItem` with 2 caller files, `format_completion` over 4 shells, `to_info_dict` of `Option` and `Argument`, and `get_duration_property` with 2 caller files (observed: the review, point 1, `traps.py`).

### 4.3 The operation count

The count a dry run read takes (observed: the review, finding 5, which defines it on the tables a run writes):

- The denominator: the `tool_calls` rows with a writing `fn` of the Developer, Tester and Critic sessions on the batch.
- The numerator: the rows of the denominator whose `args_summary`, or the `turns.completion` of that turn, names an id or a grain of the pushed constraint key or shape key in the `turns.user` of that session.

Prediction: on a touch of `get_duration_property`, the I2 request, about 0.2, 2 of 10 writing calls, from 0 today (reasoned: the push holds one helper row with two caller files and the intake rows, and a Tester call that writes a test in `src/icalendar/tests` names the `testpaths` row). The fold touch carries no shape fact, so it measures the commitment push and not this layer (reasoned: section 3, the fold has no copy, no helper with two caller files and no variant).

## 5. Cost

On icalendar's 2,794 grains, 84 source files, 258 Python files, the dive's tree (observed: probe, `[seconds]` line). On the pinned tree, 2,800 grains and 261 Python files, the total was 1.50 and 1.56 seconds in two runs (observed: the review, section c):

| Fact | Deterministic seconds | Model minutes up front |
|---|---|---|
| parse of the tree, shared | 0.14 to 0.27 | 0 |
| copies | 0.45 (the index query alone is under 0.01) | 0 |
| shared helpers | 0.36 | 0 |
| disagreements, unit and variant | 0.39 | 0 |
| boundaries | 0.01 | 0 |
| total, up front | about 1.3, and 1.5 on the pin | 0 |
| after each merge: `code_calls` in the index rebuild, `harvest.record` on the merged commit | about 1.5, the same work again | 0 |

No model session runs per area, per group or per fact. A variant group costs model time only when a request touches a member, and then inside a delivery session that runs anyway (reasoned). The comparison: the first dry3 survey cost 13.9 model minutes on 22 areas (observed: the design page, section 2).

The re-read after a merge: the indexer rebuilds `code_calls` in the transaction that rebuilds `code_edges`. Then `refresh(main=True)` calls `harvest.record` on the merged commit, which today does not happen (observed: the review, finding 3). The two take about 1.5 seconds in total (reasoned: the probe's times on the pin; harvest.py 541 to 545 skips a commit it has read). The facts take the commit, so no survey reopens.

## 6. The build order

Prices from `plans/operating-facts.md` line 250: a door text 2 cycles, an instrument fix 3, a seam with its night 8 to 10, about twenty cycles a session. The actual rate is 1.6 times (observed: deep dive, section 8). The slice's passes 2 to 4 are those of section 4.2 of the design page: pass 2 the record kind and the push door, pass 3 the two Critic sentences with two register cases, pass 4 the dry run and the key re-cut (reasoned: pass 1 is the harvester, built, harvest.py).

### 6.1 The keep rule, set before any measure

A fact kind is kept when both parts hold. First, its true rate is at least 6 of 10 in a sample on at least two of the three pinned repositories where it fires. Second, it changes the outcome of at least one blind test task or one consult question in the measure of step 9. A kind that fails either part is dropped, with its door field and its rows (reasoned: the review, finding 6, "kept when 6 of 10 true and one trap task changes"). The thresholds per kind:

| Kind | Rate today, pinned | Outcome it must change | Rule status before the measure |
|---|---|---|---|
| `entry_point`, scripts and README run lines | true where it fires; guards 2 of 4 on icalendar | T2 or Q8 | rate holds for scripts and README lines; guards are kept only if a filter of fuzzers and module demos takes icalendar to 6 of 10 |
| `intake` | true where it fires, 2 of 3 repositories | the landing or change-log check in 2 of 3 runs that fail without it | rate holds |
| `code_calls`, helpers by two or more files | 8 of 10 click, 6 of 10 icalendar | I2 or C3 | rate holds |
| copies query | 2 of 2 tips, 1 of 1 click, 0 of 3 icalendar | T2 or T3 | rate holds on two repositories; it is a free query, so the outcome part decides |
| `variant` | 7 of 10 click, 3 of 10 icalendar | C3 or C4, with a push of at most 5 member lines per touched file | rate holds on one repository only, so it is not built before the measure |

### 6.2 The steps

The order is the review's: `entry_point`, `intake`, `code_calls` and the copies query first, the measure next, and the variant kind last and only if its rule passes (observed: the review, finding 6).

| Cycle step | What | Priced | At 1.6 |
|---|---|---|---|
| 1 | The `entry_point` and `intake` kinds: `_widen_candidate_kinds`, the move of script rows from `metadata` and their new ids, the `bind` branch at harvest.py 503 | 5 to 6 | 8 to 10 |
| 2 | The re-run: `harvest.record` in `indexer.refresh(main=True)` after `build`, with a test that a merge moves the rows to the new commit | 2 | 3 |
| 3 | `code_calls` in the indexer with the resolver on `harvest.Tree`, the schema row, the copies query, a test on the three pinned trees | 3 to 4 | 5 to 6 |
| 4 | The guess: `copies` and `entry_point` fields on `code.callables` rows | 2 | 3 |
| 5 | Pass 2 with the shape push in the same door family: the commitment columns, `shape_of_touch`, the push to the Critic and the structural review | 10 to 12 | 16 to 19 |
| 6 | `model.shape`, a new op with a body and a line in `architect/ask.tools` | 3 | 5 |
| 7 | The consult instrument: `shape_for` in `probes/consult.py` | 3 | 5 |
| 8 | Pass 3, the Critic sentences and the register cases | 2 | 3 |
| 9 | The measure: pass 4, the fold dry run and the key re-cut, the consult probe on the icalendar set, and one dry run sentence that touches a helper or a copy, the I2 or the T3 request | 6 to 7 | 10 to 11 |
| later | The variant kind with a member cap, only if 6.1 passes after step 9 | 3 to 4 | 5 to 6 |

The total of steps 1 to 9 is about 36 to 41 priced and 58 to 65 at the actual rate, about three sessions (reasoned: twenty cycles a session). The shape layer's own share is steps 1 to 4, 6 and 7, the shape part of step 5 (about 2), and the shape part of step 9 (about 4), about 24 to 26 priced and 38 to 42 actual. The variant kind is not in the total. Steps 1 to 4 can run beside the design of step 5, because they change other files (reasoned). The blind test stays its own frame after the slice (ruled: Roman, 2026-11-04, `rota/COMPLETION.md`, the band added under entry 11).

## 7. Doubts

- Overfitting, observed: copies count on tips only. icalendar's 3 pairs are all `main`, 0 of 3 true, and click has 1 pair. The fact is a free query and it is the tips trap, so it is built, and the keep rule of 6.1 drops it if no T2 or T3 outcome changes. Its value is not shown on a large project (observed: probe).
- Overfitting, observed: the unit group finds 1 group on icalendar and 0 on click and tips. It is one project's habit (observed: probe; the design page's doubt on the harvester's kinds).
- Overfitting, observed: the variant group is 7 of 10 true on click and 3 of 10 on icalendar. icalendar's component and value classes override many methods by design, so the push on a touch of `Component` can be long (observed: probe, the `example` and `new` groups over 8 to 9 classes). So the kind waits for the measure, and the keep rule of 6.1 sets a cap of 5 member lines per touched file.
- The area rule fails, observed: shared helpers by area find 0 on click and miss I2 on icalendar. The rule counts files. A project whose files are many small modules may then list many helpers (reasoned).
- The resolver sees calls by name and through module aliases only. Method calls on instances, factories and calls by string are invisible, so Q4 stays missed and some helpers are missed (observed: `TypesFactory`; reasoned).
- The probe is Python only. The indexer is multi-language through tree-sitter, and rota's lineage includes the Obsidian plugin in TypeScript. On that project the four facts do not run as designed (observed: indexer.py `_parser`; reasoned).
- The variant group finds where siblings differ, not whether they disagree. The C3 fix needs the bodies read. Whether a small model sees the newline difference from two pushed bodies is unmeasured (reasoned).
- Law 1: `variant` rows in `commitment_candidates` widen what a "candidate" means beyond a promise. A separate table is cleaner and needs a second door read. I chose the column that exists, and the choice is made again if the kind passes its keep rule (reasoned).
- Noise in the push: icalendar has 34 helpers and 31 variant groups. The push lists only the facts of the touched grains, so the size is bounded by the touch, not the project (reasoned). Unmeasured on a real batch.
- The predictions of section 4 are reasoned from the probe, not run. `probes/consult.py` starts model sessions, and this brief forbids them (ruled: the brief). The counts were taken again on the blind test's pinned commits by the review, and they hold (observed: the review, point 1).
- The consult gain is a door gain. The new records add 0 points on the consult set, so that set cannot decide the keep rule for them. The blind test and the I2 or T3 dry run sentence decide it (reasoned: section 4.1).
- The guess mark of step 4 is a field on a row the model reads. A small model may still name one copy. Unmeasured (reasoned).
- The operation number is the weakest. It is defined in 4.3, and it is predicted on a touch that hits a shape fact. One sentence gives a small denominator, about 10 writing calls (reasoned).

## 8. Usage

Probe directory: `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/535a30c6-b4f1-4ae7-85bc-11d741145722/scratchpad/shape/`, `shape.py` and `tips.json`, `click.json`, `ical.json`. Run as `D:/repos/rota/.venv/Scripts/python.exe -I shape.py <tree> <index.db> --json <out>`, with the dive's trees and databases of `plans/design-onboarding-deep-dive-2026-11-03.md`, Probes.

About 95k tokens and about 45 tool calls, counted by the agent from the session. The harness line was not visible to the agent. The revision took about 35k tokens and about 25 tool calls more, counted the same way.

## Revision

From `plans/f362-review-shape-design.md`, 2026-11-04, one change per finding:

1. High, the consult instrument: section 4.1 now credits 0 points to the new shape records and 2 to a door over records that exist today. It names `shape_for` in `probes/consult.py` as the instrument change, 3 cycles, step 7.
2. High, the guess reader: section 3.5 item 3 and build step 4, 2 cycles, add the `copies` and `entry_point` fields to `code.callables`. T2 stays disarmed only with step 4, and section 4.2 says so.
3. High, the harvester after a merge: section 3.4 adds `harvest.record` in `indexer.refresh(main=True)`. Section 5 adds the re-run row, about 1.5 seconds, and step 2 prices it at 2 cycles.
4. Low, I1: section 4.2 moves I1 to the commitment layer, with `parser/string.py` 122 as the binding fact.
5. Low, the operation count: section 4.3 defines it as the review does, and it predicts 0.2 on the I2 touch, not on the fold.
6. Low, the drop rule: section 6.1 sets a keep rule per kind before any measure. Section 6.2 builds `entry_point`, `intake`, `code_calls` and the copies query first, and the variant kind only after the measure.
7. Low, step prices: the harvester kinds are 5 to 6 cycles with `_widen_candidate_kinds`, the id move and the `bind` branch. `model.shape` is 3.
8. Low, `model.shape`: section 3.5 item 2 states the match rule, the word match of `code.callables` over grain names, export names and `Class.method`, with every hit. Q7 no longer uses the `PYTZ` and `ZONEINFO` group, which 3.3 calls noise.
9. Low, the copy row: section 3.1 drops the call count. The entry-point join tells the live copy from the dead one.
10. Low, the resolver: section 3.2 puts the call resolver beside `_reexported` on `harvest.Tree`, with one module map shared with the binding rule.

The counts are marked as taken on the pinned commits in section 3 (observed: the review, point 1).
