# The model of the project, read from 40 drawn records, 2026-11-10

One blind reader, frame 364, mass 4. The reader read the design pages
named in the brief, the four run databases (read only), and the three
repository copies at the onboarding commits (git, read only). The reader
read no other reader's page. The scripts are in
`C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/1efd37b1-058e-4b19-8ab1-e1a6c654a389/scratchpad/mass4/`
(`draw.py`, `detail.py`, `readers.py`), with their output in
`details.txt` and `readers2.txt` in the same folder.

## Result

1. No delivery desk read any of the 40 drawn records, by tool call, by wake refs or by a phrase of the record in its prompt (observed: `readers2.txt`, DELIV 0 on all 40).
2. Of the 40 records, 27 are true at the code, 7 are true in part, 3 are false, and 3 make no claim that a reader can check (observed: Part B, git at the onboarding commits).
3. One of the 3 false records is a dry8 Critic verdict that "falsified" a true statement (observed: `component_factory.py:91`). A second dry8 verdict outside the draw falsified the drawn constraint `cw_4c0e2101263f`, which is true (observed: `pyproject.toml:139-140`).
4. Six of the 40 records say something that a person cannot read from the one file or symbol that the record points at (reasoned: Part B, item 4 of each block).
5. Ten records reached the Principal on a page, in 6 pages. Two more pages carry one of them as a quarantine ref (observed: `messages.body_refs`). In dry8 none of the 10 drawn records reached a page.
6. When the Principal saw such records, he said "I asked for none of these notes" (dry1 m147) and "I do not know this step and I did not ask for it. Drop it." (dry3 m44) (observed: `rulings.words`).
7. After those two drops, the dropped glossary and constraint rows stay unchanged and stay marked `observed` (observed: `term_provenance`, `constraint_provenance`).
8. Only 12 of the 40 records carry a mark of observed, reasoned or decided. Survey records, challenges, ledger rows and commitment candidates have no provenance view (observed: `schema.sql:167-196`).
9. The 40 records split as 14 challenges, 8 survey records, 6 constraints, 5 glossary rows, 4 commitment candidates, 2 ledger rows and 1 frame row. No `model_areas` row and no description item came into the draw.
10. Onboarding wakes took 108 of 311 sessions in dry1, 34 of 97 in dry2, 149 of 206 in dry3 and 123 of 199 in dry8 (observed: `sessions.wake_kind`).
11. The onboarding readers of the records are mostly the next onboarding phase: survey, reorient, boundary and challenge sessions (observed: `readers2.txt`).
12. Most tables carry no tree on a record, and three runs show records written after a merge about the merged tree (observed: Part D, items 2 and 3).

## Part A: the design's statements

Each check in brackets is the test the reader applied to a record.

1. "The structure holds a model of its shape, terms, boundaries, and external commitments, as records observed from the code" (`plans/composition.md:40-42`). [The record is one of these kinds and rests on a grain, a citation or a copied line.]
2. The glossary has the terminologist as its one writer, the model and the frame have the architect, and the challenge has the critic. "A survey record is an attestation by the role that did the reading" (`rota/ROLES.md:24-50`). [The receipts name only that role.]
3. "A record says whether it was observed from the code or the world, reasoned by a seat, or decided by the Principal" (`plans/composition.md:58-59`). [The record or a provenance view gives the mark.]
4. "A row is `decided` when its refs reach a ratified statement or a landed ruling. A row is `observed` when its refs reach a grain or a reference" (`rota/LAWS.md:286-288`). [The mark matches the refs and the rulings.]
5. "Every claim cites a source. A seat can check the claim against the source" (`plans/composition.md:78-79`). [The cited source exists at the run's tree and supports the claim.]
6. "A define sense must name where the word is written down -- a key, type or file the concordance showed" (`rota/ONBOARDING.md:185-187`). [The glossary sense names the file or the declaring type.]
7. "Constraints protect external commitments only ... Each constraint declares bindings" (`rota/LAWS.md:325-330`). [The constraint names a party outside the module and has bindings.]
8. "`party` names who outside notices, and `behaviour` says what must hold. An empty `party` marks a row that is not an outside commitment" (`rota/core/schema.sql:245-247`). [Both columns are filled.]
9. "Structural review triggers by mechanical intersection of diff-touched grains with bindings" (`rota/LAWS.md:329-330`). [When the run's diff touched a binding, the review read the constraint.]
10. "Citations make "surveyed" evidence rather than a claim: each cited grain is validated against the code index" (`rota/core/schema.sql:344-346`). [The citations carry `resolves`.]
11. A survey record stamps `area_hash` and `commit_sha`, "Which tree this was a survey *of*" (`rota/core/schema.sql:323-340`). [Both fields are filled.]
12. "`reconcile` (every prose file against the account, one session each; a disagreement is a page)" (`rota/MAP.md:100-101`), with "each disagreement a ledger entry ("README says X; the code shows Y")" (`rota/ONBOARDING.md:574`). [One prose file per session, and a disagreement names X and Y and reaches a page.]
13. "A row is a candidate, not a commitment: the Architect states a commitment as a `constraints` row. `commit_sha` is the project commit the harvest read" (`rota/core/schema.sql:284-288`). [The candidate carries its commit, and a commitment exists only as a constraint.]
14. "A challenge session succeeds only by citation -- a line of source the claim cannot survive" and "break demands a citation the session opened and the quoted line" (`rota/ONBOARDING.md:1128-1129`, `1179-1181`). [The quote is a real line at the tree, and the line decides the claim the way the verdict says.]
15. "A falsified claim goes to the ledger; standing changes only by ruling" (`rota/ONBOARDING.md:1181-1182`). [A ledger row exists, and the claim row changes only by a ruling.]
16. "`observed` provenance carrying the residual wrongness to the principal's agenda", and the agenda holds "observed entries and parked collisions" for the principal (`rota/ONBOARDING.md:69-70`, `84`). [A page names the record.]
17. "`observed` becomes decided where they said so and ledger where they deferred" (`rota/ONBOARDING.md:691-692`). [After his words on the record, the mark is `decided`, or the row changes as he said, or a ledger row holds the deferral.]
18. "Onboarding is done when a cold role can act on the repository from the artefacts alone. A Developer who has read only the glossary writes the right thing; a Critic can judge a change against the constraints" (`rota/ONBOARDING.md:15-18`), measured as "the share of delivery acts, by the Developer, the Tester and the Critic, that cite a record" (`rota/COMPLETION.md:117-118`). [A delivery desk read or cited the record.]

## Part B: the draw

### The tables

The draw takes these tables (observed: `schema.sql`, `rota/onboarding/harvest.py`, `rota/roles/api.py`, `scheduler.ONBOARDING_TICKS` at `rota/core/scheduler.py:670-673`):

- `glossary_terms`, `constraints`, `model_areas`, `survey_records`, `frame_rulings`, `challenges` and `commitment_candidates`, whole.
- `items` where `is_description = 1`, the account. The request items are left out.
- `ledger` rows whose first writer session has an onboarding wake kind (the ten `ONBOARDING_TICKS` and `tick:term_collision`).

Child rows (`constraint_bindings`, `survey_citations`, `candidate_bindings`, `refs`) are read as parts of their parent. `business_rules` and `references_` hold 0 rows in all four runs. `decisions` holds no row from an onboarding wake. The 139 ledger rows of dry8 with `author = 'principal'` and no receipt are left out of the draw and read in Part D.

| table | dry1 | dry2 | dry3 | dry8 |
|---|---|---|---|---|
| items (description / all) | 4 / 7 | 8 / 10 | 5 / 6 | 5 / 6 |
| glossary_terms | 15 | 9 | 108 | 62 |
| constraints | 21 | 8 | 119 | 82 |
| model_areas | 2 | 1 | 22 | 11 |
| survey_records | 62 | 8 | 170 | 158 |
| frame_rulings | 9 | 4 | 16 | 16 |
| challenges | 23 | 17 | 16 | 12 |
| commitment_candidates | absent | absent | absent | 189 |
| ledger (onboarding / all) | 23 / 26 | 6 / 12 | 23 / 34 | 21 / 166 |
| code_index, code_edges, code_lexicon | 1188, 108, 159 | 29, 4, 3 | 2800, 313, 403 | 2794, 313, 403 |

Sessions by wake kind that wrote each table (observed: `receipts` joined to `sessions`):

- dry1: glossary define 7, survey 4, message 2. Constraints survey 3, message 1. Survey records reconcile 38, define 13, survey 8, boundary 3, one each of reorient, orient, frame, blindspot. Challenges challenge 23. Onboarding ledger reconcile 5, challenge 10, blindspot 1.
- dry2: glossary define 6, survey 1, message 1. Constraints survey 1, boundary 1, message 1. Survey records survey 4 and one each of six other kinds. Challenges challenge 17.
- dry3: glossary survey 23, define 20, term_collision 9, message 3. Constraints survey 14. Model areas survey 25. Survey records survey 48, reconcile 36, boundary 3. Challenges challenge 16.
- dry8: glossary define 20, survey 11, term_collision 4, message 3. Constraints commitments 10, survey 7. Survey records reconcile 36, survey 22, commitments 10. Challenges challenge 12. Candidates: no session; the harvester writes them (`schema.sql:284-285`).

### The populations and the draw

`random.Random(364).sample(list, 10)` on the list sorted by (table, id), a new `Random(364)` for each run (observed: `draw.py`).

- dry1, population 159: challenges `constraints:click_format_filename`, constraints `argument`, survey `vision_keeper:@prose:docs/commands-and-groups.md`, challenges `constraints:context`, challenges `constraints:make_text_stream`, frame `.github`, ledger `l_5112bc3d5f`, glossary `decorator`, constraints `sentinel`, survey `vision_keeper:@prose:docs/exceptions.md`.
- dry2, population 61: ledger `challenge_items_validates_input`, challenges `constraints:accept_tip_percentage`, `constraints:input_total`, glossary `display_results`, survey `vision_keeper:@prose`, challenges `constraints:accept_total`, `items:raises_value_error_for_invalid_tip_percentage`, constraints `input_tip_percentage`, challenges `items:takes_inputs`, `items:formats_output`.
- dry3, population 479: survey `...@prose:docs/reference/api/icalendar.caselessdict.rst`, challenges `constraints:icalendar_caselessdict`, constraints `event_with_escaped_character2_ics`, glossary `vskip`, survey `...@prose:docs/styles/config/vocabularies/Base/accept.txt`, challenges `constraints:icalendar_prop`, survey `...@prose:docs/reference/api/icalendar.prop.xml_reference.rst`, challenges `constraints:tzurl_and_x_lic_location_in_vtimezone_blocks`, constraints `test_categories_parse_with_more_items`, glossary `datetime`.
- dry8, population 556: challenges `constraints:cw_4403c6b62018`, candidates `cc_7d9fd052e0ef`, survey `...@prose:docs/reference/api/icalendar.prop.dt.time.rst`, challenges `constraints:cw_8ad4a1347ba6`, candidates `cc_13f4cacdbaa1`, `cc_ea87e3443ace`, glossary `text`, constraints `cw_4c0e2101263f`, candidates `cc_ce6f0fb1df30`, survey `...@prose:docs/reference/api/icalendar.timezone.zoneinfo.rst`.

The trees: clickI onboarding commit `2c8cd3ac`, end `09c82f3b`. tipsI `99101f18`, end `ff1f65ff`. icalendarI `99619246` for dry3 and dry8, dry3 end `4f12af1e`, dry8 end `99619246` (its batch is `deferred`) (observed: `survey_records.commit_sha`, `config.project_commit`, `batches.status`).

### How the reader counted readers and pages

- A later reader is a session with a higher `seq` than the first writer. It called a read function with the record's id quoted, or its `wake_refs` names the record, or its prompt carries a 30-character phrase from the record's text. The bare id counts in a prompt only when the id is not a code identifier.
- Delivery desks: developer and tester at any wake, critic at `tick:review`, architect at `tick:structural_review` or `tick:touch_strayed`. Onboarding wakes: the set above. Other wakes are counted apart (Liaison, Vision Keeper at messages, Terminologist at criteria, Architect at grouping or guess).
- A page is a `messages` row to the principal, not `converse`, whose `body_refs` names the id. His words are `rulings.words` of the ruling on that page.

### The records

Writer, wake and session come from `receipts`. "Mark" is the provenance view, where the table has one. "Readers" gives onboarding / delivery / other counts.

**d1.1 challenges `constraints:click_format_filename`.** Critic, s275, tick:challenge. Verdict `stands`, citation `src/click/utils.py`, the quote is the `format_filename` signature. No mark. The claim judged: "Users of the `click.format_filename` function", bound to `examples/complex/complex/commands/cmd_init.py`. True: yes, `cmd_init.py:13` calls `click.format_filename(path)` and `utils.py:442` defines it. Says more: yes, it ties a caller in an example file to the function (reasoned). Page: no. Readers 0/0/0. Changed: no.

**d1.2 constraints `argument`.** Architect, s83 tick:survey first, then s166 message (`model.adopt`), s273 tick:survey. Version 3. "Users of Click that rely on the `Argument` class for defining command-line arguments". Bindings `src/click/__init__.py`, `src/click/core.py`. Refs: 10 grains and ruling `r_m61`. Mark `observed`, basis `code`. True: yes, `core.py:3663` and `__init__.py:10`. Says more: no, the re-export in `__init__.py:10` shows the same (reasoned). Pages m24 and m33 (as the challenge wake's quarantine ref) and m50. His words: m24 "1 ok. 2 drop. 3 try again. 4 try again."; m33 "1 ok. 2 drop. 3 ok."; m50 "ok". Ruling `r_m147` later contests the reading of m61 with "I asked for none of these notes. The change is merged and the work is done. Drop every note and build nothing." Readers 6 (critic challenge) / 0 / 6. Changed: yes, rewritten twice and contested.

**d1.3 survey `vision_keeper:@prose:docs/commands-and-groups.md`.** Vision Keeper, s13, tick:reconcile, one record in the session. `none_found`, citation `docs/commands-and-groups.md` (resolves), `commit_sha` 2c8cd3ac, `area_hash` empty. No mark. True: no claim that this reader can check against a four-item generic account. Says more: no. Page: no. Readers 0/0/0. Changed: no.

**d1.4 challenges `constraints:context`.** Critic, s91. `stands`, citation `src/click/globals.py`, quote `def get_current_context(...)`. Claim: "Users of Click that rely on the `Context` class for managing the execution context of commands". True: yes, `globals.py:20`. Says more: no. Page: no. Readers 0/0/0. Changed: yes, the constraint was rewritten at s273 after this verdict (version 3).

**d1.5 challenges `constraints:make_text_stream`.** Critic, s282. `falsified`, citation `src/click/_compat.py`, quote `return _NonClosingTextIOWrapper(...)`. Claim: "Any code that uses `make_text_stream` to make a text stream would break." Ledger `challenge_constraints_make_text_stream`, open. True: in part. The quote is real (`_compat.py:33`, in `_make_text_stream` at `:22`). The reason says the function works, which answers a claim the constraint did not make. Says more: no. Page: no. Readers 0/0/2 (Liaison messages). Changed: no.

**d1.6 frame_rulings `.github`.** Architect, s3, tick:frame. Kind `attached`, reason "Contains GitHub actions and configuration". Ref grain `.github/ISSUE_TEMPLATE/bug-report.md`. Mark `observed`. True: yes, `.github/workflows` and `.github/ISSUE_TEMPLATE` exist at 2c8cd3ac. Says more: no. Page: no. Readers 0/0/0. Changed: no.

**d1.7 ledger `l_5112bc3d5f`.** Vision Keeper, s34, tick:reconcile on `@prose:docs/shell-completion.md`. Kind `conflict` about item `provides_command_line_interface`, text "the README is stale; the code has a bug". The same session wrote the same text about four items (observed: `tool_calls` of s34). No refs, no mark. True: no, by his ruling, and the record names no line of either side. Page m41, his words "7, 8 and 9 are wrong. The README is not stale, and the code has no bug there. The rest is fine." (verdict `contest`, act `drop`). Readers 0/0/19 (Liaison and Vision Keeper messages and contested). Changed: yes, status `resolved`.

**d1.8 glossary `decorator`.** Terminologist, s62 tick:define, then s167 message (`glossary.adopt`). Version 1. "A function that transforms another into a Click command, group, or parameter." The body names `src/click/decorators.py`. Refs grain `decorators.py` and ruling `r_m61`. Mark `observed`. True: yes, `decorators.py:144`, `:269`, `:324`, `:352`. Says more: no. Page m50, "ok". Ruling `r_m147` then contests the reading of m61 ("Drop every note"). Readers 5 (terminologist survey 4, reorient 1) / 0 / 11. Changed: yes, contested.

**d1.9 constraints `sentinel`.** Architect, s273, tick:survey, after the merge (review at s270). Version 5. "The `Sentinel` enum is used to define sentinel values. Any code that uses `Sentinel` to define sentinel values would break." Binding `src/click/_utils.py`. Mark `observed`. True: in part, `_utils.py:7` defines `class Sentinel(enum.Enum)`, and the second sentence is a template. Says more: no. Page m145, his words "I asked for none of these notes. The change is merged and the work is done. Drop every note and build nothing." (contest, drop). Readers 1 (challenge) / 0 / 4. Changed: yes, falsified at s279 and dropped by him. The row is unchanged after the drop.

**d1.10 survey `vision_keeper:@prose:docs/exceptions.md`.** Vision Keeper, s21, one record. `none_found`, citation resolves, `area_hash` empty. True: no claim that can be checked. Page: no. Readers 0/0/0. Changed: no.

**d2.1 ledger `challenge_items_validates_input`.** Critic, s21, tick:challenge. "the Critic falsified items:validates_input against main.py: "if total >= 0:" ... explicitly allows zero". True: yes, `main.py:13`. Says more: no. Page m47, his words "ok" (`r_m48`). Readers 0/0/4. Changed: yes, status `resolved`.

**d2.2 challenges `constraints:accept_tip_percentage`.** Critic, s92. `falsified`, citation `tip_calculator.py`, quote of the two-line function. Claim: "Users of `main.py`", bound to `tip_calculator.py`. Ledger row open. True: yes, `tip_calculator.py:8-9` returns the input with no check. The line does not decide the claim. Page: no. Readers 0/0/0. Changed: no.

**d2.3 challenges `constraints:input_total`.** Critic, s90. `stands`, quote `if 0 <= tip_percentage <= 100:`. Claim: "Users of `main.py`" about `input_total`. True: in part. The quote is `main.py:24` in `input_tip_percentage`, and `input_total` is `main.py:9-18`. Page: no. Readers 0/0/0. Changed: no.

**d2.4 glossary `display_results`.** Terminologist, s13 tick:survey, then s86 message (adopt). Area `.`. "prints formatted results including total, tip, and total_with_tip to the console". Refs 7 grains and `r_m35`. Mark `decided`, basis `ruling`. True: in part. `main.py:4-7` prints. `tip_calculator.py:11-13` is a second `display_results` that returns a string and prints nothing. Says more: no. Page m23, "ok". Readers 3 (reorient, survey, challenge) / 0 / 5. Changed: yes, the mark moved to `decided`.

**d2.5 survey `vision_keeper:@prose`.** Vision Keeper, s6, one record. `none_found`, citation `README.md`. True: yes, `README.md` holds one line, "Run it: `python main.py`". Page: no. Readers 0/0/0. Changed: no.

**d2.6 challenges `constraints:accept_total`.** Critic, s93. `falsified`. Claim "Users of `main.py`". The reason says "The actual constraint exists in `calculate_tip`, which validates the `tip_percentage`". True: in part. `tip_calculator.py:5-6` is right. `calculate_tip` at `tip_calculator.py:1-3` and `main.py:1-2` validates nothing. Page: no. Readers 0/0/0. Changed: no.

**d2.7 challenges `items:raises_value_error_for_invalid_tip_percentage`.** Critic, s41. `falsified`, citation `main.py`, "The code checks the range and prints an error message instead of raising a ValueError." The item is the Principal's request (`is_description = 0`). Ledger row `parked`. True: yes at 99101f18 (`main.py:24-27`). At the end commit ff1f65ff, `tip_calculator.py:3` and `main.py:3` raise `ValueError`. Page: no. Readers 0/0/0. Changed: yes, the merge changed the code and no later verdict exists.

**d2.8 constraints `input_tip_percentage`.** Architect, s76, tick:survey, after the merge (review at s62). Version 3. "Users of `main.py`", binding `main.py`. Mark `observed`. A glossary row has the same id. True: no claim that can be checked. Says more: no. Page: no. Page m23 names the id, but its ruling ref `r_m35` sits on the glossary row. The page came from the observed-entries session s50, before the constraint's first write at s76 (observed: `tool_calls` of s50). Readers 1 (challenge, `stands`) / 0 / 1. Changed: no.

**d2.9 challenges `items:takes_inputs`.** Critic, s25. `stands`, quote of `input_total`. True: yes, `main.py:9-12`, `:20-23`. Page: no. Readers 0/0/0. Changed: no.

**d2.10 challenges `items:formats_output`.** Critic, s20. `stands`, quote of the three `print` lines. True: yes, `main.py:5-7`. Page: no. Readers 0/0/0. Changed: no.

**d3.1 survey `...@prose:docs/reference/api/icalendar.caselessdict.rst`.** Vision Keeper, s19. That one session woke for 71 prose files and wrote 71 records from one `surveys.attest` call in 2 turns. `none_found`, `area_hash` empty. True: yes, the file is an automodule stub, lines 1-8. Page: no. Readers 0/0/0. Changed: no.

**d3.2 challenges `constraints:icalendar_caselessdict`.** Critic, s198, after the merge and the re-survey (s191-196). `stands`, quote `raise ValueError("canonical_order contains duplicate keys")`. Claim: "Clients that use the icalendar.caselessdict module for case-insensitive dictionary handling". True: yes at 4f12af1e (`caselessdict.py:52`). The line is absent at 99619246. It is the run's own merged change. Page: no. Readers 0/0/0. Changed: no.

**d3.3 constraints `event_with_escaped_character2_ics`.** Architect, s121, tick:survey. "tests that expect escaped spaces in the organizer field". Binding `src/icalendar/fuzzing/corpus/event_with_escaped_character2.ics`. Mark `observed`. True: in part. `test_parsing.py:296` expects `r"Society\ 2014"`. The test reads the copy in `src/icalendar/tests/events/` (`conftest.py:149`, `:181`), not the bound corpus copy. Says more: yes, it relates a data file to a test (reasoned). Page m39, his words "Line 2: I do not know this step and I did not ask for it. Drop it. The rest is right." Line 2 is the offer of observed entries that holds this id (verdict `contest`). Readers 0/0/4. Changed: yes, contested.

**d3.4 glossary `vskip`.** Terminologist, s80, tick:survey, area `src/icalendar/prop/recur`. "Skip direction enum for RRULE." The body names `vText`, `Enum`, RFC 7529, OMIT, FORWARD, BACKWARD. A constraint has the same id. Mark `observed`. True: yes, `prop/recur/skip.py:1`, `:11`, `:16`. Page m39, same words as d3.3. Readers 9 (survey 8, reorient 1) / 0 / 8. Changed: yes, contested.

**d3.5 survey `...@prose:docs/styles/config/vocabularies/Base/accept.txt`.** Vision Keeper, s46, one record. `found`. Citations: the file (resolves) and `problem.baseline()` (resolves 0). Its ledger row `l_8a773df8b4` says "The README is empty and does not contain any claims about the program's functionality." True: no. The file is a word list with one line, "inviter". Page: no, and the ledger row is on no page. Readers 0/0/0. Changed: no.

**d3.6 challenges `constraints:icalendar_prop`.** Critic, s144. `falsified`, quote of the automodule block. Claim: "It is used by all iCalendar-related code in the project." Reason: the source "does not support this broad assertion". True: yes, `icalendar.prop.rst:43-46` says nothing about use. The line does not defeat the claim. Ledger row open. Page: no. Readers 0/0/1. Changed: no.

**d3.7 survey `...@prose:docs/reference/api/icalendar.prop.xml_reference.rst`.** Vision Keeper, s19, one of 71. `none_found`. True: yes, an automodule stub. Page: no. Readers 0/0/0. Changed: no.

**d3.8 challenges `constraints:tzurl_and_x_lic_location_in_vtimezone_blocks`.** Critic, s156. `stands`, quote of the TZURL and X-LIC-LOCATION lines. True: yes, `issue_53_tzid_parsed_properly.ics:3-4`. Page: no. Readers 0/0/0. Changed: no.

**d3.9 constraints `test_categories_parse_with_more_items`.** Architect, s135, tick:survey. Headline is a test name. Text "vCategory and vText classes". Binding `test_categories.py`. Mark `observed`. True: in part, the test runs over both classes (`test_categories.py:5`, `:9`, `:21`), and the row names no party and no behaviour. Page m39, same words as d3.3. Readers 0/0/4. Changed: yes, contested.

**d3.10 glossary `datetime`.** Terminologist, s67, tick:define. "a precise calendar date and time of day value used in iCalendar events, formatted per ISO 8601." The body names `vDatetime` in `src/icalendar/prop/dt/datetime.py`. Mark `observed`. True: yes, `datetime.py:16`, `:25`. Page m39, same words. Readers 22 (survey 21, reorient 1) / 0 / 8. Changed: yes, contested.

**d8.1 challenges `constraints:cw_4403c6b62018`.** Critic, s128. `falsified`. Claim: "users of icalendar rely on this: round-trip safety for custom components", from `docs/how-to/custom-components.rst`. Reason: the factory creates a generic subclass "instead of using any previously registered custom class". True: no. `component_factory.py:91` reads the registered class first, and `:92-99` create one only when none is registered. Says more: yes, it judges a promise in a doc against a module (reasoned). Ledger row open. Page: no. Readers 0/0/1. Changed: no.

**d8.2 commitment_candidates `cc_7d9fd052e0ef`.** The harvester, no session. Kind `issue_comment`, `src/icalendar/prop/recur/recur.py:207`, "# E.g. incorrect trailing semicolon, like (issue #157):", symbol `vRecur.from_ical`, commit 99619246. True: yes, `recur.py:207`. Says more: no. The Architect stated it as `cw_fc55cbf9bd37`, "The line must not contain incorrect trailing semicolons". The code skips such a pair and goes on (`recur.py:205-209`). Page: no. Readers 1 (tick:commitments) / 0 / 0. Changed: yes, restated with another sense (reasoned).

**d8.3 survey `...@prose:docs/reference/api/icalendar.prop.dt.time.rst`.** Vision Keeper, s19, one of 71. `none_found`. True: yes, a stub. Page: no. Readers 0/0/0. Changed: no.

**d8.4 challenges `constraints:cw_8ad4a1347ba6`.** Critic, s123. `stands`, quote of the `broken.py` docstring, `why` empty. Claim: "correct round-trip serialization for broken properties". True: yes, `prop/broken.py:17`. Says more: yes, a doc promise checked in a module (reasoned). Page: no. Readers 1 (challenge) / 0 / 0. The Tester at `tick:tests_missing` saw the constraint itself, not this verdict. Changed: no.

**d8.5 commitment_candidates `cc_13f4cacdbaa1`.** Harvester. `test_witness`, `src/icalendar/tests/prop/test_unit.py:202`, "from icalendar.prop import vText", `held_by` `prop/text.py`. True: yes. Says more: yes, a test to module relation (reasoned). Not stated. Page: no. Readers 1 (commitments) / 0 / 0. Changed: no.

**d8.6 commitment_candidates `cc_ea87e3443ace`.** Harvester. `doc_claim`, `docs/contribute/documentation/style-guide.rst:274`. No bindings. True: yes. Not stated. Page: no. Readers 0/0/0. Changed: no.

**d8.7 glossary `text`.** Terminologist, s69, tick:define. "a human-readable string value type for iCalendar properties that applies specific escaping rules to commas, semicolons, and line breaks when serialized." The body names `vText` in `src/icalendar/prop/text.py`. Mark `observed`. Ledger `l_9d2582d303` (author `principal`, `parked`): "observed and unconfirmed under the lazy election". True: yes, `text.py:7`, `:11`, `:96`, and `parser/string.py:9-30`. Page: no. Readers 11 (survey 9, reorient 2) / 0 / 4. Changed: no.

**d8.8 constraints `cw_4c0e2101263f`.** Architect, s109, tick:commitments. Headline `pyproject.toml: icalendar = "icalendar.cli:main"`, party "tool users", witness `wk_4c0e2101263f`, binding `pyproject.toml`. Mark `observed`. Lazy-election ledger `l_22b92d833f` open. True: yes, `pyproject.toml:139-140`. Says more: yes, a promise to outside tool users (reasoned). The Critic falsified it: "does not define an entry point named "icalendar"". That verdict is false. Ledger `challenge_constraints_cw_4c0e2101263f` open. Page: no. Readers 6 (reorient 2, boundary 3, challenge 1) / 0 / 7. Changed: yes, contradicted by a false verdict.

**d8.9 commitment_candidates `cc_ce6f0fb1df30`.** Harvester. `doc_claim`, `docs/reference/versions-branches.rst:28`, "compatible with Python versions 3.10 - 3.14", `contradicts` `[]`. True: yes, and `pyproject.toml:58`, `:67-71` agree. Not stated. Page: no. Readers 0/0/0. Changed: no.

**d8.10 survey `...@prose:docs/reference/api/icalendar.timezone.zoneinfo.rst`.** Vision Keeper, s31, one record. `none_found`. True: yes, a stub. Page: no. Readers 0/0/0. Changed: no.

## Part C: the grid

"n/a" counts the records that the statement does not speak to. Each row sums to 40.

| # | holds | does not hold | cannot be told | n/a |
|---|---|---|---|---|
| 1 kinds, observed from code | 16: d1.2, d1.6, d1.8, d1.9, d2.4, d2.8, d3.3, d3.4, d3.9, d3.10, d8.2, d8.5, d8.6, d8.7, d8.8, d8.9 | 0 | 0 | 24 |
| 2 one writer by role | 36: all but the candidates | 0 | 4: d8.2, d8.5, d8.6, d8.9 | 0 |
| 3 a mark is carried | 12: d1.2, d1.6, d1.8, d1.9, d2.4, d2.8, d3.3, d3.4, d3.9, d3.10, d8.7, d8.8 | 28: the 14 challenges, 8 surveys, 2 ledger rows, 4 candidates | 0 | 0 |
| 4 mark matches refs | 10: d1.6, d1.9, d2.4, d2.8, d3.3, d3.4, d3.9, d3.10, d8.7, d8.8 | 2: d1.2, d1.8 | 0 | 28 |
| 5 claim checkable at source | 27: d1.1, d1.2, d1.4, d1.6, d1.8, d2.1, d2.2, d2.5, d2.7, d2.9, d2.10, d3.1, d3.2, d3.4, d3.6, d3.7, d3.8, d3.10, d8.2 to d8.10 | 10: d1.5, d1.7, d1.9, d2.3, d2.4, d2.6, d3.3, d3.5, d3.9, d8.1 | 3: d1.3, d1.10, d2.8 | 0 |
| 6 sense names its place | 4: d1.8, d3.4, d3.10, d8.7 | 1: d2.4 | 0 | 35 |
| 7 outside commitment, bindings | 2: d1.2, d8.8 | 4: d1.9, d2.8, d3.3, d3.9 | 0 | 34 |
| 8 party and behaviour | 1: d8.8 | 0 | 5: d1.2, d1.9, d2.8, d3.3, d3.9 | 34 |
| 9 review by binding | 0 | 0 | 6: the 6 constraints | 34 |
| 10 citations validated | 8: the 8 surveys | 0 | 0 | 32 |
| 11 hash and commit stamped | 0 | 8: the 8 surveys | 0 | 32 |
| 12 reconcile: one file each, X and Y, a page | 4: d1.3, d1.10, d2.5, d8.10 | 5: d1.7, d3.1, d3.5, d3.7, d8.3 | 0 | 31 |
| 13 candidate with commit | 4: d8.2, d8.5, d8.6, d8.9 | 0 | 0 | 36 |
| 14 verdict decided by a real line | 8: d1.1, d1.4, d2.7, d2.9, d2.10, d3.2, d3.8, d8.4 | 6: d1.5, d2.2, d2.3, d2.6, d3.6, d8.1 | 0 | 26 |
| 15 falsified to ledger | 9: d1.5, d1.9, d2.1, d2.2, d2.6, d2.7, d3.6, d8.1, d8.8 | 0 | 0 | 31 |
| 16 observed entry reaches a page | 10: d1.2, d1.7, d1.8, d1.9, d2.1, d2.4, d3.3, d3.4, d3.9, d3.10 | 10: d1.5, d1.6, d2.2, d2.6, d2.7, d2.8, d3.6, d8.1, d8.7, d8.8 | 0 | 20 |
| 17 his word changes the mark | 5: d1.7, d2.1, d2.4, d8.7, d8.8 | 7: d1.2, d1.8, d1.9, d3.3, d3.4, d3.9, d3.10 | 0 | 28 |
| 18 a delivery desk reads it | 0 | 15: the 5 glossary rows, 6 constraints, 4 candidates | 0 | 25 |

Evidence for each "does not hold" cell:

- 3: the provenance views cover `items`, `glossary_terms`, `constraints`, `model_areas` and `frame_rulings` only (`schema.sql:167-196`). `challenges`, `survey_records`, `ledger` and `commitment_candidates` have no mark column and no view.
- 4, d1.2 and d1.8: refs reach the landed ruling `r_m61` ("ok"), and the view says `observed`. The view also needs an approved read-back (`schema.sql:119-122`), and `r_m147` contests `reading:m61`.
- 5, d1.5: the reason answers a claim the constraint did not make. d1.7: no line on either side, and he ruled it wrong. d1.9: the second sentence is a template. d2.3: the quote is from another function (`main.py:24`). d2.4: a second `display_results` prints nothing (`tip_calculator.py:11-13`). d2.6: `calculate_tip` validates nothing (`tip_calculator.py:1-3`). d3.3: the bound file is not the one the test reads (`conftest.py:149`). d3.5: `accept.txt` is a one-word list. d3.9: no party, no behaviour. d8.1: `component_factory.py:91` reads the registry first.
- 6, d2.4: the sense names no file, and the word has two definitions in two files.
- 7, d1.9: `Sentinel` lives in the private module `_utils.py`. d2.8: "Users of `main.py`" names no commitment. d3.3: the party is the project's own tests. d3.9: no party.
- 11: `area_hash` is empty on all 8 drawn survey records and on every pseudo-area record in the four runs. `commit_sha` is filled on all.
- 12, d1.7: on page m41, but the text is "the README is stale; the code has a bug", with no X and no Y. d3.1, d3.7, d8.3: session s19 wrote 71 prose records from one attest. d3.5: the disagreement ledger row `l_8a773df8b4` is on no page.
- 14, d1.5, d2.2, d2.6, d3.6: a real line that does not decide the claim. d2.3: a real line from another function. d8.1: the line does not show what the reason says.
- 16, d1.5, d2.2, d2.6, d2.7, d3.6, d8.1: the challenge ledger rows are on no page. d1.6: no page names a frame row in dry1. d2.8: the page m23 ref belongs to the glossary row of the same id. d8.7, d8.8: dry8 sent 13 pages and none names them. The lazy election wrote ledger rows for them.
- 17, d1.2, d1.8, d1.9: he said "Drop every note and build nothing" (`r_m147`). The rows are unchanged and `observed`. d3.3, d3.4, d3.9, d3.10: he said "Drop it" on the offer (`r_m44`). The rows are unchanged and `observed`.
- 18: DELIV 0 for all 15 (observed: `readers2.txt`). In dry1 and dry2, no glossary sense and no constraint text appears in any delivery desk prompt.

Per record:

| run | table and id | kind | writer, wake | true | says more | page | onb. readers | delivery readers | changed |
|---|---|---|---|---|---|---|---|---|---|
| dry1 | challenges click_format_filename | stands | critic, challenge | yes | yes | no | 0 | 0 | no |
| dry1 | constraints argument | constraint | architect, survey | yes | no | m50 (m24, m33) | 6 | 0 | yes |
| dry1 | survey commands-and-groups.md | none_found | vision_keeper, reconcile | no claim | no | no | 0 | 0 | no |
| dry1 | challenges context | stands | critic, challenge | yes | no | no | 0 | 0 | yes |
| dry1 | challenges make_text_stream | falsified | critic, challenge | part | no | no | 0 | 0 | no |
| dry1 | frame .github | attached | architect, frame | yes | no | no | 0 | 0 | no |
| dry1 | ledger l_5112bc3d5f | conflict | vision_keeper, reconcile | no | no | m41 | 0 | 0 | yes |
| dry1 | glossary decorator | term | terminologist, define | yes | no | m50 | 5 | 0 | yes |
| dry1 | constraints sentinel | constraint | architect, survey | part | no | m145 | 1 | 0 | yes |
| dry1 | survey exceptions.md | none_found | vision_keeper, reconcile | no claim | no | no | 0 | 0 | no |
| dry2 | ledger challenge_items_validates_input | default | critic, challenge | yes | no | m47 | 0 | 0 | yes |
| dry2 | challenges accept_tip_percentage | falsified | critic, challenge | yes | no | no | 0 | 0 | no |
| dry2 | challenges input_total | stands | critic, challenge | part | no | no | 0 | 0 | no |
| dry2 | glossary display_results | term | terminologist, survey | part | no | m23 | 3 | 0 | yes |
| dry2 | survey @prose | none_found | vision_keeper, reconcile | yes | no | no | 0 | 0 | no |
| dry2 | challenges accept_total | falsified | critic, challenge | part | no | no | 0 | 0 | no |
| dry2 | challenges raises_value_error... | falsified | critic, challenge | yes | no | no | 0 | 0 | yes |
| dry2 | constraints input_tip_percentage | constraint | architect, survey | no claim | no | no | 1 | 0 | no |
| dry2 | challenges takes_inputs | stands | critic, challenge | yes | no | no | 0 | 0 | no |
| dry2 | challenges formats_output | stands | critic, challenge | yes | no | no | 0 | 0 | no |
| dry3 | survey caselessdict.rst | none_found | vision_keeper, reconcile | yes | no | no | 0 | 0 | no |
| dry3 | challenges icalendar_caselessdict | stands | critic, challenge | yes | no | no | 0 | 0 | no |
| dry3 | constraints event_with_escaped_character2_ics | constraint | architect, survey | part | yes | m39 | 0 | 0 | yes |
| dry3 | glossary vskip | term | terminologist, survey | yes | no | m39 | 9 | 0 | yes |
| dry3 | survey accept.txt | found | vision_keeper, reconcile | no | no | no | 0 | 0 | no |
| dry3 | challenges icalendar_prop | falsified | critic, challenge | yes | no | no | 0 | 0 | no |
| dry3 | survey xml_reference.rst | none_found | vision_keeper, reconcile | yes | no | no | 0 | 0 | no |
| dry3 | challenges tzurl_and_x_lic... | stands | critic, challenge | yes | no | no | 0 | 0 | no |
| dry3 | constraints test_categories_parse... | constraint | architect, survey | part | no | m39 | 0 | 0 | yes |
| dry3 | glossary datetime | term | terminologist, define | yes | no | m39 | 22 | 0 | yes |
| dry8 | challenges cw_4403c6b62018 | falsified | critic, challenge | no | yes | no | 0 | 0 | no |
| dry8 | candidates cc_7d9fd052e0ef | issue_comment | harvester, none | yes | no | no | 1 | 0 | yes |
| dry8 | survey dt.time.rst | none_found | vision_keeper, reconcile | yes | no | no | 0 | 0 | no |
| dry8 | challenges cw_8ad4a1347ba6 | stands | critic, challenge | yes | yes | no | 1 | 0 | no |
| dry8 | candidates cc_13f4cacdbaa1 | test_witness | harvester, none | yes | yes | no | 1 | 0 | no |
| dry8 | candidates cc_ea87e3443ace | doc_claim | harvester, none | yes | no | no | 0 | 0 | no |
| dry8 | glossary text | term | terminologist, define | yes | no | no | 11 | 0 | no |
| dry8 | constraints cw_4c0e2101263f | commitment | architect, commitments | yes | yes | no | 6 | 0 | yes |
| dry8 | candidates cc_ce6f0fb1df30 | doc_claim | harvester, none | yes | no | no | 0 | 0 | no |
| dry8 | survey zoneinfo.rst | none_found | vision_keeper, reconcile | yes | no | no | 0 | 0 | no |

By run:

| run | true yes / part / no / no claim | says more | reached a page | read by an onboarding wake | read by a delivery desk | changed | onboarding-wake sessions / all | sessions that wrote these tables |
|---|---|---|---|---|---|---|---|---|
| dry1 | 5 / 2 / 1 / 2 | 1 | 4 | 3 records, 12 reads | 0 | 5 | 108 / 311 | 99 |
| dry2 | 6 / 3 / 0 / 1 | 0 | 2 | 2 records, 4 reads | 0 | 3 | 34 / 97 | 35 |
| dry3 | 7 / 2 / 1 / 0 | 1 | 4 | 2 records, 31 reads | 0 | 4 | 149 / 206 | 140 |
| dry8 | 9 / 0 / 1 / 0 | 4 | 0 | 5 records, 20 reads | 0 | 2 | 123 / 199 | 115 |
| all | 27 / 7 / 3 / 3 | 6 | 10 | 12 records, 67 reads | 0 | 14 | 414 / 813 | 389 |

"Sessions that wrote these tables" counts the sessions of any wake with a receipt on `glossary_terms`, `constraints`, `model_areas`, `survey_records`, `frame_rulings` or `challenges`.

## Part D: what the grid does not cover

1. One id names rows in two tables. In dry2, `display_results` and `input_tip_percentage` are both a glossary row and a constraint. In dry3, `vskip` is both. A page's `body_refs` carries the bare id with no table (observed: dry2 m23, query on both tables).
2. Records written after the merge describe the merged tree. Re-surveys ran after the merge at s271-274 (dry1), s75-76 (dry2) and s191-196 (dry3), and the dry3 challenge s198 quotes `caselessdict.py:52`, which exists only at 4f12af1e. `challenges` and `constraints` carry no commit (observed: `sessions.seq`, git).
3. An earlier record outlives the code it judged. The dry2 verdict on `raises_value_error_for_invalid_tip_percentage` (s41) says the code prints and does not raise. After the merge, `tip_calculator.py:3` raises, and the ledger row stays `parked` (observed: git at ff1f65ff, `ledger`).
4. A Critic challenge took the Principal's own request item (`is_description = 0`) as a claim about the code and falsified it (observed: dry2 `challenges` `items:raises_value_error_for_invalid_tip_percentage`, `items`).
5. The repository holds two copies of one thing, and a record sees one. `display_results` is in `main.py:4` and `tip_calculator.py:11` with other behaviour. `event_with_escaped_character2.ics` is in `fuzzing/corpus/` and `tests/events/`, and the constraint binds the copy the test does not read (observed: git).
6. In dry8, 139 ledger rows carry `author = 'principal'` and no session receipt, each "observed and unconfirmed under the lazy election". The Principal answered 7 pages of that run (observed: `ledger`, `receipts`, inventory page).
7. The glossary and constraint tables have no column that holds a drop. After "Drop every note" (dry1) and "Drop it" (dry3), the rows keep their text and version (observed: `schema.sql:202-228`, `:254-264`, the rows).
8. Delivery desks read some records outside the draw. In dry8 one Tester session (`tick:tests_missing`) carried 19 constraint texts, and 6 Developer message sessions carried the glossary row `fold`. In dry3 one Tester session carried `canonical_order`. In dry1 and dry2 the delivery prompts carry no glossary sense and no constraint text (observed: phrase search over delivery turns).
9. In dry8 the harvester wrote 189 candidates. The ids of 99 appear in the prompts of the `tick:commitments` sessions, and 32 became constraints. Two of the 4 drawn candidates reached no session (observed: `commitment_candidates`, `constraints.witness`, turns).
10. dry3 and dry8 share an identical onboarding start: the same five description items word for word, the same reconcile session s19 with 60278 prompt characters, and the same reconcile counts, 6 `found` and 113 `none_found` (observed: `items`, `turns`, `survey_records`).

## Part E: limits

- The draw does not cover `model_areas` (36 rows across runs) or the description items (22 rows). No statement about the account is tested here.
- The draw takes 10 records a run from populations of 61 to 556. Challenges are 14 of 40, and the tables with few rows (dry1 and dry2) weigh more than their share of all rows.
- The ledger population takes only rows whose first writer has an onboarding wake. The 139 lazy-election rows, the delivery ledger rows and the `decisions` table are outside it.
- The reader search finds a reader by a quoted id in a read call, by `wake_refs`, or by a 30-character phrase. It misses a reader that saw a row at index depth (id and headline only), when the id is also a code identifier. Some survey sessions in dry3 carry `event_with_escaped_character2_ics` by id in a pushed list, and this reader did not count them.
- A record written at s273 can carry text that differs from the version a challenge judged at s91. The databases keep only the last version of a row, so the reader cannot tell what changed.
- The truth check reads the tree at the onboarding commit, except d3.2, which this reader read at the merged commit. The reader did not read whole prose files for the three `none_found` records that make no claim the reader could check.
- "Says more" is the reader's judgement in each case (reasoned). Another reader can draw the line in another place.
- The reader did not read the turn logs, the transcripts of the build sessions, or the copies made before each turn. A page as the Principal saw it can differ from its rows at the end of the run.
- dry1 holds four measures in one database, and this reader did not split the draw by measure.
