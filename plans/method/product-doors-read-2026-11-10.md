# The doors of rota: a blind read, 2026-11-10

## Result

1. The code holds 503 refusal sites. `rota/roles/api.py` holds 421 of them, and `rota/core/sandbox.py` holds 72 (observed: AST count).
2. Of 40 drawn sites, 11 are workflow rules, 11 are checks of form, 11 are guards against one fault of a model, 2 are caps, 3 are Python rules, and 2 are internal checks (reasoned).
3. By judgement, 25 are general, 14 are general in aim and fitted in their pattern, and 1 is fitted to one case (reasoned).
4. 31 of the 40 origin commits name a night, a dry run, a recorded case or a model as their reason (observed: commit text).
5. 22 of the 40 rules have a line on a design page or in a desk prompt. Only 11 have a line on a design page (observed: grep).
6. 11 of the 36 sites that a text can match never show in the 109 run databases. 4 sites have no text to match (observed).
7. The sites grew by about seven a day in October. `api.py` grew from 1,753 lines on 2026-08-15 to 31,223 lines today (observed: git).
8. The fitted part is mostly Python and pytest, not one repository. A small set of doors names click by its API (`CliRunner.invoke`) (observed).
9. The guards against one fault usually state a general rule in the text, and match a narrow shape in the code (reasoned).

## How a refusal works

- A tool call runs in `runner.py`. Any exception becomes a line `ERROR <call>: <text>` in the next prompt (observed: rota/core/runner.py:6702-6712).
- The marker of a refusal is `raise` of `ValueError` or a subclass: `Wall`, `EndRefusal`, `LinesRefusal`, `PassHeld`, `_stands` (observed: rota/roles/api.py:591-615, 7880).
- The sandbox adds `ArgumentError`, `NotInWorkingSet` and `SandboxError` (observed: rota/core/sandbox.py:79, 87, 472).
- A refusal repeated in three turns gets a NOTE. A fourth ends the session (observed: rota/core/runner.py:6743-6750).
- `tool_calls` holds only `fn` and `args_summary`. The binder writes the row before the door runs, so the row has no refusal mark and no text (observed: rota/core/schema.sql:1198, rota/core/sandbox.py:5357-5358).
- The refusal texts are in `turns`. The "SESSION ENDED" note lists each error of a committed session (observed: rota/core/db.py:2423-2440).

## The inventory

| file | lines | refusal sites |
|---|---|---|
| rota/roles/api.py | 31,223 | 421 |
| rota/core/sandbox.py | 6,190 | 72 |
| rota/core/runner.py | 7,572 | 6 |
| rota/core/db.py | 2,440 | 2 |
| rota/core/fence.py | 177 | 2 |
| rota/core/scheduler.py | 3,707 | 0 |
| rota/core/predicates.py | 2,898 | 0 |
| rota/core/lifecycle.py | 1,244 | 0 |
| rota/core/harness.py | 869 | 0 |
| rota/core/loop.py | 768 | 0 |
| rota/core/divergence.py | 132 | 0 |

- By class: `ValueError` 428, `Wall` 39, `LinesRefusal` 13, `_stands` 6, runner `ERROR` lines 4, `ArgumentError` 4, `NotInWorkingSet` 4, `EndRefusal` 2, `JournalAuthorError` 1, `SandboxError` 1, `PassHeld` 1 (observed).
- The six core files with 0 sites give helpers, predicates and texts to the doors. They do not raise to a model (observed).
- 294 sites sit in a function with `@op`. 209 sit in shared helpers, such as `_bind_send` (40, the message doors) and `_code_write` (31, `code.write`) (observed).
- By desk, from the `.tools` lists of 82 modes, for the 294 sites in an op: architect 88, tester 82, terminologist 77, liaison 76, vision_keeper 49, developer 24, critic 17, researcher 1 (observed). An op that two desks share counts for each desk.
- The developer's count is low only because `code.write` is a helper. With its 31 sites the developer has 55 (observed).
- The ops with most sites: `tests.encode` 56, `rulings.rule` 31, `model.amend` 16, `brief.segment` 15, `ledger.log` 13 (observed).
- Caps with a number: 49 named module constants in api.py (19), sandbox.py (11), runner.py (16), scheduler.py (2) and loop.py (1) (observed: grep). Examples: `MAX_ITERATIONS = 12`, `PAGE_ASSUMPTIONS = 7`, `QUOTE_MIN = 12`, `REASON_WORDS_MIN = 6`, `SERVE_CAP = 3`, `DOWN_AFTER = 3`.
- Inline numbers inside a door are not in the 49. An example is the four-word floor of `ledger.log` (observed: rota/roles/api.py:18137).
- Predicates of the scheduler: 50 `@predicate` registrations, all in `rota/core/predicates.py` (observed).
- The ladder: `LADDER` has 3 rungs (developer, architect, vision_keeper). `QUESTION_LADDER` has 2 (architect, vision_keeper) (observed: rota/core/predicates.py:46, 53).

## The draw

The 503 sites, sorted by file and line, went to `random.Random(364).sample(sites, 40)`. The table shows the draw sorted again by file and line.

Kinds: W a rule of the workflow, F a check of form or state of a call, G a guard against one fault of a model, C a cap or counter, P a rule of Python or pytest, I an internal check that no model call meets.
Match: R the rows or the session state, T a pattern in the text of the model.
Origin: the first commit that adds the text, by `git log -S` on rota/roles and rota/core. "Names" says what the commit gives as its reason.
Fired: the count in "SESSION ENDED" notes, and the number of databases. "-" means no text to match.
Judgement: Gen general, Aim general in aim and fitted in pattern, One fitted to one case.

| # | site | op or helper | kind | match | origin | names | page | next | fired | judg |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | db.py:869 | journal write | W | R | 10-28 | ruling | LAWS | no | 11/5 | Gen |
| 2 | runner.py:1882 | `_fit` | I | R | 10-01 | night 99 | none | no | - | Gen |
| 3 | sandbox.py:518 | working set | W | R | 08-10 | moved | LAWS | yes | 1136/108 | Gen |
| 4 | sandbox.py:792 | `build` | I | R | 08-10 | moved | none | no | 0 | Gen |
| 5 | sandbox.py:1885 | challenge quote | G | T | 10-26 | night 144 | none | yes | - | Aim |
| 6 | sandbox.py:3987 | present page | C | R | 09-12 | night 17 | DEC | yes | 16/10 | Gen |
| 7 | sandbox.py:4013 | ask again | W | T | 09-08 | none | DEC | yes | 39/13 | Gen |
| 8 | sandbox.py:4917 | confirm | W | R | 08-26 | fixture | DEC | yes | 26/18 | Gen |
| 9 | sandbox.py:5105 | relay again | G | R | 08-26 | none | prompt | yes | 735/63 | Gen |
| 10 | api.py:1116 | brief.segment | F | R | 10-10 | case | prompt | yes | 0 | Gen |
| 11 | api.py:1144 | brief.segment | G | T | 10-24 | night 163 | prompt | yes | 2/2 | Aim |
| 12 | api.py:1242 | brief.segment | G | T | 10-09 | night 135 | none | yes | 0 | Gen |
| 13 | api.py:2197 | problem.assert | W | T | 10-14 | nights 143-146 | LAWS | yes | - | Aim |
| 14 | api.py:2431 | problem.set approval | W | R | 11-01 | dry1 | none | yes | 0 | Gen |
| 15 | api.py:3331 | glossary.amend | G | T | 08-24 | cnt, models | prompt | yes | 31/8 | Aim |
| 16 | api.py:4608 | model.amend | F | T | 08-24 | cnt, models | none | yes | 39/3 | Gen |
| 17 | api.py:6781 | `_vet_surface` | G | R | 11-01 | dry1, click | DEC | yes | - | Aim |
| 18 | api.py:8161 | tests.retire | W | R | 10-24 | night 164 | prompt | yes | 229/8 | Gen |
| 19 | api.py:9239 | batches.guess | F | R | 10-18 | case, qwen | prompt | yes | 104/28 | Gen |
| 20 | api.py:11923 | tests.encode | W | T | 10-26 | night 167 | DEC | yes | 0 | Aim |
| 21 | api.py:11941 | tests.encode | W | R | 09-24 | case, qwen | DEC | yes | 37/12 | Gen |
| 22 | api.py:14087 | rulings shape | F | R | 10-27 | fixture | prompt | yes | 0 | Gen |
| 23 | api.py:17238 | rulings.rule | F | R | 09-10 | models | none | yes | 14/6 | Gen |
| 24 | api.py:17453 | rulings.rule | G | T | 10-27 | gate run | prompt | yes | 12/5 | Aim |
| 25 | api.py:17505 | rulings.rule | F | R | 10-27 | fixture | prompt | yes | 20/4 | Gen |
| 26 | api.py:17509 | rulings.rule | F | R | 10-27 | fixture | prompt | yes | 0 | Gen |
| 27 | api.py:17665 | rulings.rule | W | R | 09-10 | models | comp | yes | 174/44 | Gen |
| 28 | api.py:18128 | ledger.log | G | R | 09-09 | tipsQ | none | yes | 28/8 | Gen |
| 29 | api.py:18138 | ledger.log | C | T | 10-09 | none | prompt | yes | 94/11 | Aim |
| 30 | api.py:18558 | decisions.author | G | R | 08-12 | case | none | yes | 20/14 | Aim |
| 31 | api.py:19724 | critic pass lines | F | R | 10-25 | none | none | yes | 0 | Gen |
| 32 | api.py:20276 | schedule.reask | F | R | 08-14 | 9b | none | no | 0 | Gen |
| 33 | api.py:25318 | code.run | F | T | 11-08 | none | none | yes | 0 | Gen |
| 34 | api.py:25541 | code.write | G | T | 09-14 | tipsBG | none | yes | 10/6 | One |
| 35 | api.py:26097 | code.write | P | T | 09-30 | none | none | yes | 10/9 | Aim |
| 36 | api.py:26375 | code.write | P | T | 10-05 | night 113 | none | yes | 1/1 | Aim |
| 37 | api.py:26567 | code.write | W | T | 09-09 | tipsR | LAWS | yes | 352/70 | Aim |
| 38 | api.py:26903 | code.write | G | T | 09-30 | ACT case | none | yes | 136/46 | Aim |
| 39 | api.py:27032 | code.write | P | T | 09-14 | night 51 | none | yes | 53/19 | Aim |
| 40 | api.py:29838 | batches.expect | F | R | 09-13 | tipsI | none | no | 0 | Gen |

All origin dates are in 2026. "moved" means the first commit on the present path is the refactor of 2026-08-10 (observed: b519a246b).

## The sites in plain words

Each line gives the refusal, the text or its pattern, and the reason for the judgement (reasoned unless marked).

1. A write over another role's journal row. Text: "A journal row is its author's record." Law 1, "one author per entry" (observed: rota/LAWS.md:96). The text names no next step.
2. The window fit gets lists of two lengths. A runner invariant. No model call meets it (reasoned).
3. A call to a function outside the desk's working set. The text lists the available artefacts. The most frequent refusal in the records.
4. A role that the graph does not hold. A check of configuration, not of a model.
5. A challenge quote shorter than `QUOTE_MIN = 12` characters. The aim is that a challenge cites the rows. The 12-character floor is a chosen number from one review.
6. A page with more than `PAGE_ASSUMPTIONS = 7` open assumptions. Roman ruled the interview "iterative, most important first" (observed: rota/DECISIONS.md:1378). The number is the door's own.
7. The same words already put to the principal. Exact match after a whitespace collapse. "Nothing is asked twice" (observed: rota/DECISIONS.md:1382).
8. A confirm that names a row that is not a statement. "A confirmation names a statement, or it is refused" (observed: rota/DECISIONS.md:527).
9. A second relay to an owner that has one. Text: "Your work here is done". The liaison prompt says "Send one relay. Then stop." (observed: rota/roles/prompts/liaison/answering.md:77). A repeat guard on a rule that holds anywhere.
10. `supersedes` when no earlier request exists. A state check.
11. `supersedes` on words that name other identifiers. Pattern: `r"\b([A-Za-z_][A-Za-z0-9_]*)\("` plus `_identifiers` (observed: rota/roles/api.py:1057-1063). The aim is general. The pattern assumes a request names a function by its identifier, which fits code requests in English (reasoned).
12. Words that equal a ratified statement. Text: "Cite s.. There is nothing to segment or ask". A repeat guard on exact text.
13. A Vision Keeper assert that puts its own words on a decided item. Law 11 (observed: rota/LAWS.md:279-289). The check reads the wake kind and compares words, with many branches from nights 143 to 150 (observed: rota/roles/api.py:1835-1880).
14. An approval of `dropped` by a desk. Text: "only the principal's drop ends {id}. Leave it". Law 6, nothing on his behalf.
15. A second glossary sense that adds no content word. Word sets minus the stoplist `_FRAME_WORDS` (observed: rota/roles/api.py:20475). The heuristic is English and the stoplist was written from the words of the surveyed repositories (reasoned).
16. A constraint with an empty `text`. Text: "is a title with nothing under it". A form check.
17. A surface ref that names several index rows. The resolver `_dotted_rows` and `_module_fits` read a Python package layout, written from `click.pause` (observed: rota/roles/api.py:6610-6625).
18. `tests.retire` without his ruling that drops the line. Law 6. 229 notes in 8 databases suggest a loop on this text (reasoned).
19. A bare symbol in `batches.guess`. Text: "names no path. A symbol is written path::name". The form is rota's own.
20. A test path outside the project. The check is general. The text tells the model "Name the file tests/test_<thing>.py", which is the pytest layout.
21. An encode for a criterion that the session routed. The triage fork (observed: rota/DECISIONS.md:978).
22. A ruling object with no `verdict`. Form. The example names `app.py:518`.
23. `rulings.rule` when no page is open. Text ends "Stop".
24. Act fields given as keys of `rulings`. Match on `_ACT_FIELDS = ("act", "target", "target_kind")` (observed: rota/roles/api.py:13876). Added after one gate where the Liaison did this 5 of 5. The door rewrites the call for the model.
25. A key of `acts` that `rulings` does not hold. Form.
26. A value of `acts` that is not an object. Form.
27. Lines of the page with no ruling. "treats silence as consent" is refused (observed: plans/composition.md:75).
28. A ledger row about a ledger row. Added after tipsQ ran "36 rounds of a ledger about the ledger" (observed: rota/roles/api.py:18122-18126). The rule "an assumption is about an artefact" holds anywhere.
29. An assumption of fewer than 4 words. The prompt rule "Say the actual thing" (observed: rota/roles/prompts/liaison/blindspot.md:25). The floor of 4 is a chosen number.
30. A decision about an item the session amended. Match: `i == id or i in id`, a substring of the id (observed: rota/roles/api.py:18556). The text says "Report it and stop". 3 of 10 modes that offer `decisions.author` offer no `msg.report_*` call (observed: grep of the `.tools` files).
31. A pass whose `lines=` names a retired criterion. State check.
32. `schedule.reask` with no answer that woke the desk. The text states the fault and gives no step.
33. `code.run` with an empty program. Form. `code.run` runs Python only, through `python_for` (observed: rota/roles/api.py:25308).
34. `code.write` to a path that is an argument name. Match: `path.strip().lower() in ("path", "file", "filename", "text", "...")` (observed: rota/roles/api.py:25540). A literal list from one tipsBG write.
35. A span insert above `from __future__`. Python only. The door offers the correct call.
36. Text that puts a statement above `from __future__`. Python only. The door offers the reordered call.
37. A Developer write to a test file. Law 1 and the Tester's ownership. Match: `r"test_\w+\.py|\w+_test\.py|conftest\.py"` (observed: rota/roles/api.py:8921). The rule is general. The pattern is pytest.
38. A whole-file rewrite that drops names that the file still uses. Python `ast`. Added after every run of `ACT-DV-edit-inside-the-function` dropped `_readline_prompt` (observed: commit 791da68dc).
39. A module that imports its own package at module level. Python import rules, from night 51 on click.
40. `batches.expect` on an id that is not a batch. Form. No step.

## Counts over the 40

| kind | count | judgement Gen / Aim / One |
|---|---|---|
| W rule of the workflow | 11 | 8 / 3 / 0 |
| F form or state | 11 | 11 / 0 / 0 |
| G guard against one fault | 11 | 3 / 7 / 1 |
| C cap or counter | 2 | 1 / 1 / 0 |
| P Python or pytest | 3 | 0 / 3 / 0 |
| I internal | 2 | 2 / 0 / 0 |
| total | 40 | 25 / 14 / 1 |

- Match on the rows or the state: 23. Match on the text of the model: 17 (observed).
- Text with a next step: 35 of 40. Texts 1, 2, 4, 32 and 40 give none (observed).
- A line on a design page: 11 (LAWS 4, DECISIONS 6, composition 1). A line only in a desk prompt: 11. None: 18 (observed). `rota/MAP.md` held no line for any of the 40.
- The 14 "Aim" sites share one shape. The text states a rule that holds anywhere. The code matches the shape that one model wrote on one night (reasoned).

## Origins

- The origin commit names a live night, a dry run or a named repository run (`tipsQ`, `tipsR`, `tipsBG`, `tipsI`, the `cnt` baseline) for 18 sites (observed).
- It names a recorded case, a fixture, a gate run or the register for 10 sites (observed).
- It names only a model for 3 sites (`8b`, `9b`, `qwen`, `llama`) (observed).
- It names none of these for 9 sites. Of the 9, sites 3 and 4 moved in the refactor of 2026-08-10, so the first reason is not on this path (observed).
- By month of origin: August 8, September 12, October 17, November 3 (observed).
- Over all 503 sites, 145 have a comment in the 12 lines above that names a night, a repository, a model or a run (observed: regex over the comments). The count is a floor, because a reason can sit further up (reasoned).

## The runs

- The search covered 109 databases: dry1 to dry8, dry6b, dry6c, blind1 and 98 `clickI_night*.db` files. All opened read-only (observed).
- The nights have file times from 2026-09-18 to 2026-10-28. The dry runs end 2026-11-08, and blind1 ends 2026-11-10 (observed).
- The databases hold 17,946 "SESSION ENDED" notes with 107,057 error lines, and 212,708 `ERROR` lines in prompts (observed).
- 25 of the 36 matchable drawn sites show in the notes. 11 never show: sites 4, 10, 12, 14, 20, 22, 26, 31, 32, 33 and 40 (observed).
- Site 33 was added on 2026-11-08, after nearly all runs. Sites 14 and 17 were added on 2026-11-01. So a part of "never fired" is "too new" (reasoned).
- Sites 2, 5, 13 and 17 have no fixed text that belongs to them alone, so they were not counted (observed).
- The hot sites: 3 (1,136 notes in 108 databases), 9 (735 in 63), 37 (352 in 70), 18 (229 in 8), 27 (174 in 44), 38 (136 in 46) (observed).
- A high count can be one loop. Site 18 has 229 notes in only 8 databases (observed). The four-turn stop of the runner bounds a loop per session, not per night (reasoned).

## Growth

| date | api.py lines | sites api.py | sites sandbox.py | sandbox.py lines |
|---|---|---|---|---|
| 2026-08-15 | 1,753 | 25 | 15 | 807 |
| 2026-09-10 | 7,160 | 142 | 39 | 1,739 |
| 2026-10-05 | 12,111 | 222 | 51 | 3,216 |
| 2026-10-30 | 26,929 | 385 | 69 | 5,914 |
| 2026-11-10 | 31,223 | 421 | 74 | 6,190 |

- The count is a grep of `raise` with a refusal class at the last commit before each date (observed). The grep count for sandbox.py today is 74 against 72 by AST, so the error is small (observed).
- Between 2026-10-05 and 2026-10-30, api.py gained 14,818 lines and 163 sites, about 6.5 sites a day (observed). The two files together gained about 7 a day (observed).
- The lines per site in api.py rose from 70 to 74. The comments that carry the reasons grow with the doors (reasoned).

## What would break on a new repository

- A repository with tests that do not use pytest names. `_test_shaped` takes only `test_*.py`, `*_test.py` and `conftest.py` (observed: rota/roles/api.py:8921). Every test-file door asks this one question, site 37 included.
- A repository in another language. Sites 35, 36, 38 and 39, and the 870 `ast` references in api.py, read Python only (observed: grep). `code.run` runs Python (observed: site 33).
- A test that does not use click. `tests.encode` refuses a test that passes a plain function to `.invoke`, with the text "`CliRunner.invoke` takes a click command" (observed: rota/roles/api.py:12945-12960). Another door tells the model to move a call "into the command" that `CliRunner().invoke` runs (observed: rota/roles/api.py:10147-10156). These doors are click doors.
- A package without the `src/<pkg>/` dotted layout. The surface resolver of site 17 maps `click.pause` to `src/click/termui.py` (observed: rota/roles/api.py:6615-6625).
- The harness reads pytest's output form, with 21 pytest references in `rota/core/harness.py` (observed). The plugin `rota/core/plugins/_rota_caught.py` exists for `CliRunner` (observed: rota/core/harness.py:32).
- The prompts teach with click. The liaison prompt explains `supersedes` with `--color`, `--quiet`, `echo` and `confirm` (observed: rota/roles/prompts/liaison/converse.md:77-80).
- A model that makes other mistakes. The literal lists of sites 24 and 34 catch the exact shapes that one model wrote. A new model's misshape passes them, and other doors then refuse it with a less exact text (reasoned).
- A request in another natural language. Sites 11, 15 and 29 count English words or identifiers (reasoned).
- The tool order in each `.tools` file was set because "both 8B models took the first function whose arguments matched" (observed: rota/core/sandbox.py:510-515). The fix is general, but the order was tuned on two models (reasoned).

## Limits

- A site here is a `raise` of a refusal class, plus 4 runner `ERROR` lines. A helper that returns a refusal text, such as `_quote_refusal` or `_program_rank`, counts once at the raise that uses it. The runner's repeat and four-turn stops are not in the 503 (observed).
- `rota/roles/principal.py` holds 6 more `ValueError` raises. They serve the human seat, so they are not counted (observed).
- The desk counts use the `.tools` lists and the op that holds the site. Helper sites have no desk in the per-desk count (observed).
- The origin is the first commit that holds a chosen literal on the present paths. A reworded text gives the date of the wording, not of the rule. Code that moved shows the move (reasoned).
- The run counts see committed sessions only. A failed session loses its turns (observed: rota/core/db.py:2423-2440). Some night files are copies, such as `clickI_night91_walk1.db` and `clickI_night109_cut.db`, so a few counts are double (observed).
- A text with variable parts was matched by its fixed part. Two doors with the same fixed part would add up. The read checked this only for sites 17 and 20 (observed).
- The kinds and the judgements are one reader's. A second reader can draw the line between W and G, or between Gen and Aim, in another place (reasoned).
- This read did not open `plans/stack.md`, the other product readings or the meta pages. It ran no model and changed no file but this page (observed).
