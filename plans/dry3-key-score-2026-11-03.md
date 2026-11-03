# Dry run 3 against the icalendar answer key, 2026-11-03

## Result

Rota's survey of icalendar holds the vocabulary and not the commitments: 9 of 10 required terms, 0 of 7 trap hits, 0 of 2 required constraints, 0 of 3 expected constraints (observed: `probes/cnt/score.py --key probes/ical/answer_key.yaml` on the dry3w7 copy). Of the 118 constraints, none states an outside commitment, and 5 on `news/` files invent one (observed: `constraints` rows). Of the five preregistered predictions of `rota/ANSWER_KEY_icalendar.md`, none is found whole, 3 are partly found, and 2 are missed, the 75-octet line fold among them (observed: section 1). The description and 21 of 22 model areas are right or partly right, and the `.` area's account describes the wrong files (observed: section 2). All four term collisions the principal answered were the team's own duplication, not ambiguity in the source (observed: section 3).

## 1. The score against the key

The scorer exists, so the numbers below are mechanical (observed: `probes/cnt/score.py` lines 360 to 372 take `--key`). The run used the copy at `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/ce483c7b-be58-4d58-bfc4-db1081518842/scratchpad/keyscore/dry3.db`.

| Measure | dry3 | ical_v0, 2026-08-24 | click v2 |
|---|---|---|---|
| terms_required present | 9 of 10, `todo` absent | 8 of 10 | 8 of 10 |
| must_not_mean hits | 0 of 7, all 7 trap terms present | 0 of 7 | 1 of 7 |
| copied from the index | 9 of 108 (8%) | 7 of 110 (6%) | 1 of 24 (4%) |
| constraints written | 118, no empty body | 50 | 31 |
| constraints_required found | 0 of 2 | 0 of 2 | 0 of 2 (v1) |
| decoys recorded | 0 | not given | 2 (v1) |

(observed: scorer output; `probes/ical/answer_key.yaml` `recorded_run_result`; `probes/click/answer_key.yaml` lines 136 to 166). No record holds a key score for the click dry runs (observed: a search of `plans/dry1-*.md` for "answer key" finds none).

The `property` trap is passed this time. The row `property` reads "The fundamental building block of an iCalendar component", not the Python sense (observed: `glossary_terms` id `property`). In ical_v0 no `property` row existed to trap (observed: the yaml key, `property_trap_is_live`).

Expected terms by hand: 2 found (`text`, `duration`), 1 partly found (`componentfactory` for `factory`), 5 missing (`journal`, `subcomponent`, `caselessdict`, `free_busy`, `broken`) (observed: live `glossary_terms` rows). 81 of 108 rows are off the key. Most are test fixtures and identifiers such as `.gitkeep` and `fuzz_v1_calendar` (observed: scorer).

The five predictions of `rota/ANSWER_KEY_icalendar.md`:

| Prediction | Verdict | Row |
|---|---|---|
| 1. `timezone` has three senses bound by the TZID rule | partly | `timezone` (VTIMEZONE), `tzp` (backend switch), `tzid` (the parameter). The three senses exist as three terms. No row states the binding rule. |
| 2. `parameter` means the concept and the parser | missed | `parameter` is superseded into `parameter#src_icalendar_parser`, one sense only |
| 3. Line folding at 75 octets, issue #1501 | missed | no row holds "75", "octet" or "fold" |
| 4. `vBroken` keeps a failed value for the round trip | partly | model area `.` names `vBroken`. It gives no round-trip reason, and it sits in the wrong area. |
| 5. Canonical order is a convention | partly | constraint `calendar_canonical_order`, "The order in which calendar properties are stored", bound to `cal/calendar.py`, not to `canonsort_keys` |

(observed: `glossary_terms`, `model_areas`, `constraints`, a regex search for each fact).

Inventions: 5 `news_*` constraints say "The maintainers ... would break if this file was removed or renamed" (observed: for example `news_1536_feature`). Nobody outside the repository depends on a news fragment, so the commitment is invented (reasoned: the key's test, who outside this repository would notice). The other 113 constraints restate an identifier or a test, for example `vrecur`: "icalendar.prop.recur.vRecur" (observed). The median body length is 43 characters (observed).

The eight consult questions were not run, because `probes/consult.py` starts model sessions (reasoned: the brief forbids a model session). By hand, the records hold 0 answers whole, 5 partly (Q1, Q2, Q3, Q6, Q7), and miss 3 (Q4 TypesFactory, Q5 importers and AttributeError, Q8 the `icalendar` command) (observed: a regex search over glossary, areas, items and constraints). ical_v0's consult scored about 5.5 of 8 with a model that read the records (observed: the yaml key). The two numbers measure different things and do not compare directly (reasoned).

## 2. The description and the 22 model areas

The five description items, presented in m4, are right at a general level (observed: `messages` m4 `body_refs`, `items`).

- `how_it_works`: partly right. It calls iCalendar a "protocol", and RFC 5545 defines a format. It does not name the round trip, which is the design centre of the library (observed: the item text; the yaml key Q1).
- `parses_ical_data`, `generates_ical_data`: right.
- `handles_timezones`: right, and generic. It does not say that a VTIMEZONE becomes a `tzinfo` (observed).
- `supports_recurring_events`: right. It claims the parse and the output of rules, not their expansion, and that is correct (reasoned: icalendar parses RRULE and does not expand it).

The model areas: 18 right, 3 partly right, 1 wrong (observed: `model_areas.account`, checked against the source at `99619246`).

- Right: `news`, `src/icalendar/cal`, `src/icalendar/fuzzing/corpus`, `src/icalendar/parser` (the RFC 2426 vCard claim is in `parser/__init__.py` line 3), `src/icalendar/parser/ical`, `src/icalendar/prop`, `src/icalendar/prop/dt`, `src/icalendar/prop/recur`, `src/icalendar/timezone`, `src/icalendar/tests`, `tests/alarms`, `tests/attr`, `tests/events`, `tests/fuzzed`, `tests/prop`, `tests/rfc_6350_vcard`, `tests/rfc_7265_jcal`, `tests/rfc_9253_icalendar_relationships`.
- Partly right: `src/icalendar` says "a Python library for parsing and generating" and names none of its own modules, such as `attr.py`, `param.py`, `alarms.py` or `cli.py` (reasoned: the account fits any area of the package).
- Partly right: `tests/calendars` says the files are "malformed or edge-case". Many of the 118 files are ordinary client calendars, for example `alarm_google_acknowledged.ics` and `example.ics` (observed: `git ls-tree`).
- Partly right: `tests/timezones` is right on content, and it holds 4 grains only, so the account says little (observed: `code_index`).
- Wrong: `.` describes `icalendar.prop`, `icalendar.cal`, `icalendar.parser` and `icalendar.timezone`. The `.` area holds the `.github/` workflows, `docs/`, `CHANGES.rst`, `pyproject.toml` and other root files (observed: `code_index` paths of area `.`).

## 3. The four term collisions

All four collisions came from one sense that the team wrote more than once. None was an ambiguity in the source (observed: the `glossary_terms` rows that `messages` m13 to m28 name).

- `component` (m14): `component` and `Component` both say "base class for all calendar components", for the one class in `cal/component.py`. The difference is case only (observed).
- `alarm` (m16): both rows say the VALARM trigger component. The `tests/events` row adds the snooze link through RELATED-TO, and the Liaison framed that detail as a second sense. Snooze is part of alarm handling in `alarms.py` (observed: `alarms.py` lines 8 and 52 at the base). The principal's answer, one term, is right (observed: config `entry:m20`).
- `jCal` (m18): four rows from four areas give one sense, the RFC 7265 format. All four call jCal a "compact text format", and the source calls it "a JSON based representation" (observed: `docs/how-to/jcal.rst` line 7). The collision is duplication, and the shared definition is partly wrong.
- `vFrequency` (m26): one class, `prop/recur/frequency.py`, defined once from the source and once from its tests. The source changes the value to upper case, so the two senses agree (observed: `frequency.py` lines 45 and 50).

The real ambiguities of the key, `timezone` with three senses and `parameter` with two, raised no collision (observed: no message names them). The detector fires on duplicate rows, not on one word with two meanings (reasoned: every collision listed rows of one sense from different areas).

## 4. The counts

| Count | dry3 | key `ANSWER_KEY_icalendar.md` |
|---|---|---|
| grains | 2,800 | 1,731 |
| edges | 313 | 313 |
| areas | 22, plus 629 grains with no area | 9 |
| glossary rows | 108, 97 live, 89 distinct by slug | not given |
| constraints | 118, plus constraint zero | not given |
| areas under constraint zero | 0 | 9 of 9, before the survey |

(observed: `code_index`, `code_edges`, `model_areas`, `glossary_terms`, `constraints`, `survey_records`). Constraint zero, `k0`, has no binding, and all 22 areas have a survey record (observed). The run wrote 170 survey records, 43 `found` and 127 `none_found` (observed).

The commit is the same, so the root does not cause the difference (observed: the walk base `99619246` matches the key's `9961924`; `plans/dry3-recipe-2026-11-02.md` line 5 makes the copy a clone of the key's root `D:/tmp/rota-live/icalendar`). The edges agree exactly. Today's indexer adds 261 `export` and 367 `variable` grains, and 628 of them carry no area (observed: `code_index` by `grain_kind`). The partitioner now splits `src/icalendar/tests` into 11 areas, and `src/icalendar` holds 135 grains, not 1,357 (observed). So the indexer and the partitioner changed between the key and dry run 3 (reasoned). The copy's own head is `4f12af1e`, the merge of the run (observed: config `project_commit`).

Correction, 2026-11-03, frame 362's re-cut (observed: `rota/ANSWER_KEY_icalendar.md` at the re-cut, and the report f362_keyrecut_report.md in session 07f209e6's scratchpad): a fresh onboarding of `99619246` on today's indexer gives 2,794 grains, 313 edges and 20 areas, with 628 grains in no area, 261 `export` and 367 `variable`. The partitioner did not change. Dry3's 22 areas come from the judge's 16 frame rulings, which re-pin the partition: `src` ruled `program` turns the tests into 11 areas, and `docs` attaches to `.`. The 6 extra grains of dry3 are the 3 test files that `bg_1` added at `4f12af1e`. So the sentence above that the partitioner changed is wrong, and the next score compares the counts after the rulings with the key's counts before them.

## Usage

One read-only reader. About 45k tokens and 23 tool calls. No model session started. One database copy in the scratchpad folder `keyscore`. One file written in the repository, this page.
