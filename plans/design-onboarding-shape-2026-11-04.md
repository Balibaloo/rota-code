# Design: the shape layer of onboarding (2026-11-04)

Frame 362. One design iteration of the up-front shape facts of `plans/design-onboarding-2026-11-03.md`, section 3.B, "Shape against prose", for capability 11 of `rota/COMPLETION.md`.

## 1. Result

Hold the four shape facts with no model and no new survey. Copies of one function are a query on `code_index`, which holds them today. Shared helpers need one new mechanical table, `code_calls`, which the indexer writes: one row for each resolved call from a file to a top-level definition, through `__init__.py` re-exports. Disagreements are the harvester's `contradicts` group, plus a new variant group: one method that two or more subclasses of one base override with different bodies. Boundaries are the `export` grains of the index, plus three new harvester kinds: `entry_point` (a `[project.scripts]` target, a `__main__` guard, a README run line) and `intake` (`testpaths`, the change-log rule). One door family carries all four facts. It pushes the shape of the touch beside `bound_constraints` to the Developer, the Tester, the Critic and the structural review, and it gives the Architect's read-only `ask` one read, `model.shape(name)`, for the principal's questions. The up-front cost on icalendar's 2,794 grains is about 1.3 deterministic seconds and 0 model minutes. A model reads a variant group only when a request touches a member, inside the delivery session that already runs. The build is about 13 cycles priced for the shape layer, about 21 at the actual rate, and about 27 priced, about 43 actual, with the slice's passes 2 to 4, so two sessions.

Predictions, one number per measure (reasoned: section 4):

- Answers: the icalendar consult set scores 4.5 of 8 (2 whole, 5 partly, 1 missed), from 2.5 of 8 today (0 whole, 5 partly, 3 missed; observed: `plans/dry3-key-score-2026-11-03.md`, section 1, last paragraph).
- Future work: a shape fact names the trap of 6 of the 12 blind test tasks (T2, T3, C3, C4, I1, I2), 1 more partly (T1), and 5 have none (T4, C1, C2, C5, I3). The new `intake` kind also carries the landing check and the change-log check that apply to every task.
- Operation: on the fold dry run of section 4.2 of the design page, about 1 in 4 delivery acts cites a pushed record, from 0 of the acts today (observed: `plans/onboarding-demand-read-2026-11-03.md`, section 2; reasoned: the fold touch has one contradiction group and no copy, no helper and no variant, so the push is short).

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
| `probes/consult.py` | Asks the three owners in turn from their artefacts. `probes/downstream.py` holds the eight questions of the Obsidian plugin project. The icalendar set is `probes/ical/questions.py`, keyed in `probes/ical/answer_key.yaml`. | observed: consult.py 1 to 22, 107 to 113; ical/questions.py 1 to 5 |

## 3. The four shape facts

The probe is `shape.py` in the probe directory of section 8. It ran on the dive's trees at icalendar `99619246`, click `2c8cd3a` and tips `99101f1`, and on the dive's index copies, `ical.db` with 2,794 grains in 20 areas, `click.db` with 1,182 grains in 4 areas, `tips.db` with 20 grains in 1 area (observed: the dive's Probes section; probe). "True" below is my read of a sample of ten, or of all rows when fewer: would a designer of a change want this fact (reasoned).

### 3.1 Copies of one function

Rule: two top-level definitions of one name in two source files, tests, examples and dot-directories left out by `areas.is_attached`, dunder names left out. A copy pair carries the call count of each side from `code_calls` and whether each side is reachable from a boundary of 3.4.

Record: none new. The index holds it, and the door runs the query (reasoned: the indexer is the one writer of `code_index`, law 1, `rota/LAWS.md` section 1, and a query adds no writer). Methods stay out of the index. A method copy reaches a reader through the variant group of 3.3.

| Repository | Pairs | True | Notes |
|---|---|---|---|
| tips | 2 | 2 of 2 | `calculate_tip`, bodies similar 0.77; `display_results`, other arguments, and the `tip_calculator.py` side has no caller |
| click | 1 (7 with dunders, 10 in the index) | 1 of 1 | `get_pager_file`, the wrapper in `termui.py` and the work in `_termui_impl.py`. The 6 dunder pairs are module `__getattr__` shims |
| icalendar | 3 | 0 of 3 | all three are `main` of three tools |

(observed: probe.) Method pairs that share a name and are 0.8 alike: icalendar 123, 0 of 10 true in the sample (`to_jcal`, `example`, `ical_value` boilerplate); click 5, 5 of 5 true (the shell formatters and the usage errors) (observed: probe). That is why method copies stay out of this fact.

A model adds nothing. Which copy is live is a join with 3.4, not a judgement (reasoned: tips `main.py` has the `__main__` guard and the README line, `tip_calculator.py` has neither).

Readers: the Architect at the guess, where a copy of a guessed symbol becomes a rank 1 entry of the caller rule, the fix the dive asked for (observed: deep dive, section 3, tips `b_1`). The Developer, the Tester, the Critic and the structural review through the shape push of 3.5. The Architect's `ask` through `model.shape`.

### 3.2 Shared helpers

Rule: a top-level definition that two or more non-attached source files call, the definer left out, with the call resolved through `from` imports, module aliases and `__init__.py` re-exports. The rule counts files, not areas. The area rule misses the blind test's own case: `get_duration_property` has two caller files, `cal/event.py` and `cal/todo.py`, in one area (observed: probe). On click the area rule finds 0, because one area holds all 17 source files (observed: probe).

Record: a new table `code_calls (src, dst_grain)`, written only by the indexer in the same transaction as `code_edges` (reasoned: a call row is mechanical and rebuilt, as an edge is; law 1). It must not join `code_edges`, because `areas.propose` reads every edge as coupling, and call rows would move the partition (observed: areas.py 239 to 250). The same table gives the caller rule of 3.B step 5 its rank 1 through re-exports, which `probes/callers.py` of the dive did by hand (reasoned).

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
2. The variant group, new: one method name that two or more classes with one base override, with bodies that differ. The base is matched by name across all source files. Overloads in one class count once.

Record: the unit group stays where it is. The variant group goes in the harvester's record as a candidate of a new kind `variant`, one row per member method, with the members' ids in `contradicts` (reasoned: the column already means "these lines state the same thing another way, quote both", and the harvester is already the one writer of that table, law 1). The `kind` check of `commitment_candidates` gains `variant`, `entry_point` and `intake` (observed: schema.sql 276 to 278).

| Repository | Unit groups | True | Variant groups | True in sample |
|---|---|---|---|---|
| tips | 0 | none | 0 | none; the copy pair of 3.1 with other bodies is the disagreement here |
| click | 0 | none | 10 | 7 of 10; noise is two `ABC` groups across hierarchies and `get_error_hint` |
| icalendar | 1 | 1 of 1, 75 octets against 75 characters | 31 | 3 of 10; `set_start` and `set_duration` of `Event` and `Todo` are true, the `PYTZ` and `ZONEINFO` backends and `example` are noise |

(observed: probe.) The click groups hold `format_completion` over the four shells, which is the C3 trap, and `to_info_dict` of `Option` and `Argument`, which is the C4 trap (observed: probe). The icalendar groups hold `duration`, `start` and `end` over `Event` and `Todo`, beside the I2 trap (observed: probe).

A model adds the content of the disagreement: "zsh passes a newline through, PowerShell collapses it". The rule finds where siblings differ, not how. A small model on two pushed method bodies of 10 to 20 lines may say how they differ. That is unmeasured, and the design does not depend on it (reasoned). The model reads a group only when a request touches a member, in the Developer's or the Critic's session that already runs, so no new wake exists.

Readers: the shape push of 3.5 names the group and the member lines. The Critic reads it at `review` as a remark source, not a fail source (reasoned: ruling 3 of 2026-11-03 makes a broken outside promise a fail, and a variant is no promise).

### 3.4 Boundaries

Rule, three parts:

1. Exports: the `export` grains of a top-level `__init__.py`. Where no `__all__` exists, the public names that `__init__.py` binds by import.
2. Entry points: each `[project.scripts]`, `gui-scripts` and `entry-points` target; each source file with an `if __name__ == "__main__"` guard or named `__main__.py`; each README line that runs `python <file>`.
3. Intake: `testpaths` of `[tool.pytest.ini_options]`, the `[tool.towncrier]` fragment rule, and a change-log file with an unreleased heading.

Record: exports stay in the index. Entry points and intake become harvester kinds `entry_point` and `intake`, with the binding rule `entry_point` that exists (observed: harvest.py 503 to 506). Script targets are `metadata` candidates today, so `entry_point` takes them over (observed: harvest.py 12 to 13).

| Repository | Exports | Scripts | `__main__` guards | README run lines | Intake | True |
|---|---|---|---|---|---|---|
| tips | 0 | 0 | 1, `main.py` | 1, `python main.py` | none | 2 of 2 |
| click | 65 by import, no `__all__` | 0 | 0 | 1, `python hello.py`, an example | `CHANGES.md` | exports true by definition; the run line is noise |
| icalendar | 84 in `__all__` | 1, `icalendar = icalendar.cli:main` | 4 | 0 | `testpaths`, towncrier | exports and script true; guards 2 of 4, the fuzzer and `cal/lazy.py` are noise |

(observed: probe; `pyproject.toml` 294 to 312 of the icalendar tree.) An export is true by definition. The fact a designer needs is the join: "the touched name is public" (reasoned).

A model adds nothing. A script target's first docstring line comes with the row by rule, so the Architect can say what the command does (reasoned: consult question 8).

Readers: the shape push of 3.5 says "public" or "entry point" beside a touched grain. The Tester and the Developer get the intake rows at every delivery wake, so a test lands where `testpaths` collects it and a change carries its fragment (reasoned: the blind test's landing check and commit 08aab3c8, `plans/understanding-test-blind-2026-11-03.md`, section 2). The Architect's `ask` reads exports and scripts through `model.shape`.

### 3.5 The door family

One push and one read, both beside the doors that exist (reasoned: the touch files that `bound_constraints` computes are the right key, api.py 4228 to 4240).

1. The push, `shape_of_touch(batch_id)`, no argument. For each touched file and grain: its copies, its other caller files and test callers, its variant groups with member lines, and whether it is exported or an entry point. The intake rows always come with it. It rides the push of runner.py 4424 to 4440 and is extended to the Critic's `review` and to the structural review.
2. The read, `model.shape(name)`, with an argument, in `architect/ask.tools`. It answers "where does X live, every copy, who calls it, is it public, which siblings vary". This is the only new line in a `.tools` file.

The push keeps the cut rule of the push it rides: after the criteria block (observed: runner.py 4434 to 4440).

## 4. The two measures, predicted

### 4.1 The icalendar consult questions

The set is `probes/ical/questions.py`. The eight questions of `probes/downstream.py` are the Obsidian plugin project's, and this probe does not run on TypeScript (observed: downstream.py 33 to 72; reasoned: the rules use Python's `ast`).

| Q | Question, short | Record after this design | Prediction |
|---|---|---|---|
| 1 | Text to a Calendar and back | exports (`Calendar`), the preservation candidate for `vBroken` | partly; the round trip is the commitment layer |
| 2 | What a component is, how it nests | the variant group of `Component` subclasses lists the kinds; the glossary | partly |
| 3 | Property against parameter | the glossary only | partly, no change |
| 4 | Where DTSTART becomes a datetime, `TypesFactory` | none; the resolver does not see the factory lookup | missed |
| 5 | Rename `Calendar.from_ical`, who notices | exports: `Calendar` is public, so every importer, at run time | whole |
| 6 | An unparseable value | the preservation candidate, not a shape fact | partly |
| 7 | VTIMEZONE to tzinfo | the `PYTZ` and `ZONEINFO` variant group, the `tzdata` dependency candidate | partly |
| 8 | The `icalendar` command | the `entry_point` row with the target's docstring line | whole |

2 whole and 5 partly, 4.5 of 8 at half a point for partly, against 2.5 today (reasoned). The answers depend on the Architect's `ask` holding `model.shape`. Without that read the score does not move (observed: ask.tools).

### 4.2 The twelve blind test tasks

| Task | Trap | Shape fact that disarms it |
|---|---|---|
| T1 | a second check where both copies already raise | copies, partly: both copies are named; "already done" still needs a read of the bodies and the test |
| T2 | edit the unused `display_results` | copies with the entry point: the `main.py` copy is the one the guard and the README reach |
| T3 | change one copy only | copies |
| T4 | the rounding of the receipt | none |
| C1 | a second suggestion path | none; a feature that exists is a code read |
| C2 | a frozen `version_option` | none; a maintainer ruling is a commitment kind the harvester lacks |
| C3 | edit the template or `CompletionItem` | the `format_completion` variant group, and `CompletionItem` as a helper with two caller files |
| C4 | `Option.to_info_dict` only | the `to_info_dict` variant group of `Option` and `Argument`; intake for the change-log line |
| C5 | auto-correct against a documented refusal | none; the harvest finds no line of `docs/why.md` |
| I1 | rewrite the fold to count characters | the unit group, 75 octets against 75 characters |
| I2 | clamp the shared duration helper | `get_duration_property` as a helper with two caller files, `event.py` and `todo.py` |
| I3 | delete the comma escape | none from shape; the RFC 5545 standard candidate is the commitment layer's |

(observed: probe for every named fact; `plans/understanding-test-blind-2026-11-03.md`, section 2, for the traps.) 6 disarmed, 1 partly, 5 none. The blind test's pins differ from the probe's trees: tipsI `ff1f65f`, clickI `09c82f3`, icalendarI `4f12af1e` (observed: the blind test, section 2). The facts must be counted again on those commits before the score counts (reasoned).

## 5. Cost

On icalendar's 2,794 grains, 84 source files, 258 Python files (observed: probe, `[seconds]` line):

| Fact | Deterministic seconds | Model minutes up front |
|---|---|---|
| parse of the tree, shared | 0.14 to 0.27 | 0 |
| copies | 0.45 (the index query alone is under 0.01) | 0 |
| shared helpers | 0.36 | 0 |
| disagreements, unit and variant | 0.39 | 0 |
| boundaries | 0.01 | 0 |
| total | about 1.3 | 0 |

No model session runs per area, per group or per fact. A variant group costs model time only when a request touches a member, and then inside a delivery session that runs anyway (reasoned). The comparison: the first dry3 survey cost 13.9 model minutes on 22 areas (observed: the design page, section 2).

The re-read after a merge: the indexer rebuilds `code_calls` in the transaction that rebuilds `code_edges`, and the harvester runs again on the new commit, about 1.3 seconds in total (reasoned: the probe's times; harvest.py 527 to 550 skips a commit it has read). The facts take the commit, so no survey reopens.

## 6. The build order

Prices from `plans/operating-facts.md` line 250: a door text 2 cycles, an instrument fix 3, a seam with its night 8 to 10, about twenty cycles a session. The actual rate is 1.6 times (observed: deep dive, section 8). The slice's passes 2 to 4 are those of section 4.2 of the design page: pass 2 the record kind and the push door, pass 3 the two Critic sentences with two register cases, pass 4 the dry run and the key re-cut (reasoned: pass 1 is the harvester, built, harvest.py).

| Cycle step | What | Priced | At 1.6 |
|---|---|---|---|
| 1 | `code_calls` in the indexer, the schema row, the probe's resolver as code, a test on the three trees | 3 to 4 | 5 to 6 |
| 2 | Pass 2 with the shape push in the same door family: the commitment columns, `shape_of_touch`, the push to the Critic and the structural review | 10 to 12 | 16 to 19 |
| 3 | The `variant`, `entry_point` and `intake` kinds in the harvester | 3 | 5 |
| 4 | Pass 3, the Critic sentences and the register cases, with one remark line for a pushed variant | 2 to 3 | 3 to 5 |
| 5 | `model.shape` in `architect/ask.tools` | 2 | 3 |
| 6 | Pass 4, the fold dry run and the key re-cut, and the consult probe on the icalendar set | 4 to 5 | 6 to 8 |

The total is about 24 to 29 priced and 38 to 46 at the actual rate, two sessions (reasoned). The shape layer's own share is steps 1, 3, 5, the shape part of 2 (about 2) and the consult run (about 2), about 12 to 13 priced and 19 to 21 actual. Step 1 can run beside the design of step 2, because neither changes the other's files (reasoned). The blind test stays its own frame after the slice (ruled: Roman, 2026-11-04, `rota/COMPLETION.md`, the band added under entry 11).

## 7. Doubts

- Overfitting, observed: copies count on tips only. icalendar's 3 pairs are all `main`, 0 of 3 true, and click has 1 pair. The fact is cheap, and it is the tips trap, so it stays. Its value is not shown on a large project (observed: probe).
- Overfitting, observed: the unit group finds 1 group on icalendar and 0 on click and tips. It is one project's habit (observed: probe; the design page's doubt on the harvester's kinds).
- Overfitting, observed: the variant group is 7 of 10 true on click and 3 of 10 on icalendar. icalendar's component and value classes override many methods by design, so the push on a touch of `Component` can be long (observed: probe, the `example` and `new` groups over 8 to 9 classes). A cap on members per group is not designed here.
- The area rule fails, observed: shared helpers by area find 0 on click and miss I2 on icalendar. The rule counts files. A project whose files are many small modules may then list many helpers (reasoned).
- The resolver sees calls by name and through module aliases only. Method calls on instances, factories and calls by string are invisible, so Q4 stays missed and some helpers are missed (observed: `TypesFactory`; reasoned).
- The probe is Python only. The indexer is multi-language through tree-sitter, and rota's lineage includes the Obsidian plugin in TypeScript. On that project the four facts do not run as designed (observed: indexer.py `_parser`; reasoned).
- The variant group finds where siblings differ, not whether they disagree. The C3 fix needs the bodies read. Whether a small model sees the newline difference from two pushed bodies is unmeasured (reasoned).
- Law 1: `variant` rows in `commitment_candidates` widen what a "candidate" means beyond a promise. A separate table is cleaner and needs a second door read. I chose the column that exists. A reviewer may judge the other way (reasoned).
- Noise in the push: icalendar has 34 helpers and 31 variant groups. The push lists only the facts of the touched grains, so the size is bounded by the touch, not the project (reasoned). Unmeasured on a real batch.
- The predictions of section 4 are reasoned from the probe, not run. `probes/consult.py` starts model sessions, and this brief forbids them (ruled: the brief). The blind test pins are not the probe's trees (observed: section 4.2).
- The operation number is the weakest. The fold touch carries one shape fact, so the dry run of pass 4 tests the commitment push more than the shape push. A second sentence that touches a helper or a copy is needed to measure the shape push, and the blind test frame holds those sentences (reasoned).

## 8. Usage

Probe directory: `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/535a30c6-b4f1-4ae7-85bc-11d741145722/scratchpad/shape/`, `shape.py` and `tips.json`, `click.json`, `ical.json`. Run as `D:/repos/rota/.venv/Scripts/python.exe -I shape.py <tree> <index.db> --json <out>`, with the dive's trees and databases of `plans/design-onboarding-deep-dive-2026-11-03.md`, Probes.

About 95k tokens and about 45 tool calls, counted by the agent from the session. The harness line was not visible to the agent.
