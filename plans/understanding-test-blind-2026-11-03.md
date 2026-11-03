# A test of repository understanding, designed blind

Written 2026-11-03 by a blind investigator. The investigator read only the three subject repositories and no file of rota.

## Result

The test is twelve requests on the three repositories, in three tiers, and each request has a trap that only the records can disarm. The traps are real: a duplicated function in the tip calculator, a zsh completion formatter that disagrees with the PowerShell formatter in click, and a shared duration helper in icalendar whose obvious fix silently changes to-do items. The score reads only the merged diff, the page shown to the person and hidden probe tests, never the records, and a run with the records withheld sets the baseline that the records must beat. One wrong merge on a promise task fails the whole test, because a wrong merge costs the person more than an honest stop. The per-request cost may grow with the reach of the request, not with the size of the repository. The largest doubt is that a strong model knows click and RFC 5545 from training, so two of the tiers need renamed forks to measure the records and not the model's memory.

## 1. What understanding means operationally

Understanding is the ability of the later work to answer five questions from the records alone, before it reads code for the request. Where does this behaviour live, including every copy of it and every shared helper behind it? What does the repository promise here, to its users, to a standard, to its tests and to its contributors? Does the behaviour already exist, so that the right change is no change? Do two parts of the repository state different facts here, and which one does the person need to rule on? Where do the tests and the change log go, so that the configured runner and the release process see them? A wrong answer to the first question costs a change in the wrong place, which the person must find by reading. A wrong answer to the second question costs a merged break that no test catches, and that is the most expensive error, because the person trusted the merge. A wrong answer to the third question costs dead code and false credit. A wrong answer to the fourth question costs a silent choice that belonged to the person. A wrong answer to the fifth question costs tests that never run and a release note that never appears.

## 2. The test design

Pin the subject commits first: tipsI `ff1f65f`, clickI `09c82f3`, icalendarI `4f12af1e` (observed: `git log` in each repository). Each pinned history already carries earlier deliveries of the system, so the repositories are not pristine.

Two checks apply to every task in addition to its own observable:

- Landing check. New tests go where the configured runner collects them. In icalendar, `testpaths` is `src/icalendar/tests` (observed: icalendarI/pyproject.toml 298-300). The pinned history holds a delivery that put tests in a top-level `tests/` directory, outside `testpaths` (observed: icalendarI commit 08aab3c8, files tests/test_caselessdict*.py). The investigator could not run the collection, because the global interpreter has no tzdata and conftest fails (observed: src/icalendar/tests/conftest.py 210, ZoneInfoNotFoundError).
- Change-log check. icalendar requires a news fragment named `#.type` (observed: icalendarI/pyproject.toml 310-312, docs/contribute/index.rst 191-199). click records each change under "Version 8.5.0, Unreleased" and marks API changes with `versionchanged` (observed: clickI/CHANGES.md 1-3, src/click/core.py 2389-2390). The pinned history holds a delivery that changed the return value of `click.pause()` with no CHANGES.md line and no `versionchanged` note (observed: clickI commit 4fcd6d7, src/click/termui.py 983-1015, CHANGES.md has only the 2.0 entry at line 1637).

### Tier 1: tipsI (two modules, about 50 lines)

The facts behind tier 1: `calculate_tip` exists twice, in main.py and tip_calculator.py (observed: main.py 1-4, tip_calculator.py 1-5). The README tells the user to run main.py (observed: README.md 3). One test imports tip_calculator and three import main (observed: tests/test_calculate_tip.py 1, tests/test_calculate_tip_c_1.py 1, c_2.py 1, c_3.py 1). The two `display_results` functions have different signatures and outputs (observed: main.py 6-9, tip_calculator.py 13-15).

**T1. Tests pass before code.** Request: "Do not let anyone enter a tip above 100 percent."
- With understanding: the system reports that both copies already raise (observed: main.py 2-3, tip_calculator.py 2-3), the prompt already loops (observed: main.py 26-29), and a test already covers 101 (observed: tests/test_calculate_tip_c_1.py 10-14). It shows a page that says "already done" with the evidence and merges nothing, or merges only a test the key accepts.
- Without understanding: it adds a second check, or writes a new test that passes at once and claims a fix.
- Observable: the source diff is empty, and the page names the existing check.

**T2. The right place is not where the words point.** Request: "Show the tip percentage on the result screen too."
- With understanding: the result screen is the one main.py prints, because the README names main.py (observed: README.md 3, main.py 6-9, 33-38). The system adds the percentage there and keeps the dollar format.
- Without understanding: a search for "Tip Percentage" finds tip_calculator.py line 15, which already shows it, and the system reports "already done" or edits that unused function (observed: tip_calculator.py 13-15, no caller in the repository).
- Observable: the hidden probe runs `python main.py` with the input "100" then "15" and finds a line with the percentage in the output.

**T3. More than one module.** Request: "Refuse a negative bill amount, the same way a bad tip percentage is refused."
- With understanding: both copies of `calculate_tip` raise ValueError for a negative total, with tests through both import paths. Today both return -7.5 for a total of -50 at 15 percent (observed: probe in the scratchpad). Zero stays legal, because the request says "negative" and `input_total` accepts zero (observed: main.py 15). The page notes one disagreement and does not fix it unasked: the message says "positive" but the check accepts zero (observed: main.py 15 and 18).
- Without understanding: it changes one copy only, or merges the two modules, which is work the person did not ask for.
- Observable: hidden probes import both modules and call `calculate_tip(-1, 15)` and `calculate_tip(0, 15)`. The diff touches both files and does not delete either.

**T4. Everyday words, no function named.** Request: "The receipt does not add up: a $20.25 bill at 18 percent shows a $3.65 tip and a $23.89 total."
- With understanding: the cause is that main.py adds the unrounded tip to the total and then formats each number to two places (observed: main.py 36-37, 7-9). The probe confirms Total $20.25, Tip $3.65, Total with Tip $23.89 for that input, and $1.00, $1.00, $2.01 for 1.005 at 100 percent (observed: scratchpad probe). The fix rounds the tip to cents once, with a stated rounding rule, and computes the total from the rounded tip. The page names the rounding rule as the person's choice if the records show no rule.
- Without understanding: it changes the print format to three places, or rounds only the display line of the total.
- Observable: a hidden grid probe over totals and percentages checks that the printed Total plus the printed Tip equals the printed Total with Tip, and the seven existing tests still pass (observed: `pytest` gives 7 passed).

### Tier 2: clickI (17 modules, 12 675 lines in src/click)

**C1. Tests pass before code.** Request: "When someone mistypes an option, tell them which option they probably meant."
- With understanding: the suggestion exists in `NoSuchOption` through `difflib.get_close_matches` (observed: src/click/exceptions.py 254-256). Tests cover it for options and commands (observed: tests/test_options.py 164-169, tests/test_commands.py 680-684). The page says "already done" and merges nothing.
- Without understanding: it adds a second suggestion path in the parser.
- Observable: the source diff is empty.

**C2. The right place is a ruling, not the words.** Request: "Let --version also print the Python version."
- With understanding: the parameters of `version_option` are frozen by a maintainer ruling, and the ruling names `custom_version_option` for exactly this case (observed: src/click/decorators.py 443-448, 561-582, docs/option-decorators.md 88, CHANGES.md 21-24). The system shows the ruling on a page and recommends a callback with `custom_version_option`, or at most a documentation example.
- Without understanding: it adds a `%(python)s` slot to the message of `version_option`.
- Observable: the diff adds no parameter and no message variable to `version_option`, and the page cites the frozen note.

**C3. Everyday words, and two parts disagree.** Request: "In zsh, tab completion shows garbled suggestions when an option's help text has two lines."
- With understanding: the zsh script reads the response in groups of three lines, type, key and description (observed: src/click/shell_completion.py 155). `ZshComplete.format_completion` passes a newline in the help through, so one item becomes four lines (observed: shell_completion.py 466-481, probe output `'plain\n--count\nLine one\nline two'`). The PowerShell formatter collapses newlines for the same framing reason, and the fish formatter escapes them (observed: shell_completion.py 543-551, 507-516). Tests exist for fish and PowerShell and not for zsh (observed: tests/test_shell_completion.py 599, 607). The fix follows the PowerShell rule in the zsh formatter and adds a zsh test. Option help reaches the formatter raw (observed: src/click/core.py 1447).
- Without understanding: it edits the zsh shell script template, or collapses newlines in `CompletionItem`, which changes fish output too.
- Observable: a hidden probe checks that every formatter returns the line count its shell expects for a two-line help, and the fish output keeps its escaped `\n`.

**C4. More than one file, and a schema promise.** Request: "Tools that build documentation from a command should be able to see which options are deprecated."
- With understanding: `Command.to_info_dict` already reports `deprecated` and `Parameter.to_info_dict` does not (observed: src/click/core.py 1079-1088, 2381-2404). Parameters store the value (observed: core.py 2357). The change adds the key in `Parameter.to_info_dict`, so options and arguments both get it (observed: core.py 3172-3193, 3711-3714). It updates every expected dictionary in the test (observed: tests/test_info_dict.py 9-28, 29-44, 45 onwards), adds a `versionchanged:: 8.5.0` note, and adds a CHANGES.md line.
- Without understanding: it adds the key in `Option.to_info_dict` only and leaves arguments out, or edits the tests to delete the dictionaries.
- Observable: hidden probes read `to_info_dict()` of a deprecated option and a deprecated argument. The change-log check applies.

**C5. A request against a documented refusal.** Request: "If someone types --cout, just run --count."
- With understanding: the docs refuse auto correction for a backwards-compatibility reason and point to explicit aliases (observed: docs/why.md 98-104). The system shows the refusal on a page and asks the person to rule. It changes nothing before the ruling.
- Without understanding: it makes `NoSuchOption` pick the closest match and continue.
- Observable: the diff is empty before a ruling, and the page quotes the reason.

### Tier 3: icalendarI (22 420 lines of source, 338 test files)

**I1. Tests pass before code.** Request: "Saving an event with a long Russian or emoji description must never cut a letter in half."
- With understanding: `_foldline` iterates by character and counts octets, so it never splits a UTF-8 sequence (observed: src/icalendar/parser/string.py 119-158, 134-151). Tests assert it (observed: src/icalendar/tests/test_icalendar.py 77-80, 245-272). A probe with 80 copies of "é" folds into lines of 74 and 75 octets (observed: scratchpad probe).
- Without understanding: it rewrites the fold to count characters, which breaks the 75-octet rule.
- Observable: the source diff is empty.

**I2. A silent break of a promise, and two parts disagree.** Request: "An event's duration should never come out negative, the same as its end."
- With understanding: `Event.end` ignores a negative duration and `Event.duration` returns it raw (observed: src/icalendar/attr.py 1820-1823, 1837-1853). The probe gives a duration of `-1 day, 23:59:56` and an end minus start of `0:00:00` (observed: scratchpad probe). `get_duration_property` is shared with `Todo` (observed: src/icalendar/cal/todo.py 218-232, cal/event.py 301-318). A to-do item may have a negative duration to show it is overdue (observed: src/icalendar/tests/test_issue_999_negative_event_duration.py 3-7). The only to-do test checks `todo.end`, not `todo.duration` (observed: the same file, 28-32). So the fix goes in `Event.duration` or in a VEVENT branch, never in the shared helper for all components. It adds a test in `src/icalendar/tests` and a news fragment.
- Without understanding: it clamps the shared helper. The existing suite still passes, and `Todo.duration` silently stops being negative.
- Observable: a hidden probe asserts that `Todo.duration` stays at -4 seconds and that `Event.duration` equals `Event.end - Event.start`. The landing and change-log checks apply.

**I3. A promise to a standard, in everyday words.** Request: "My other calendar app shows backslashes before commas in event titles. Stop the library adding them."
- With understanding: RFC 5545 section 3.3.11 requires the escape, and the code cites it (observed: src/icalendar/parser/string.py 9-51). A related issue has its own test (observed: src/icalendar/tests/test_issue_127_categories_comma_escaping.py). The system shows the standard on a page, says the other application probably does not unescape, and recommends no code change.
- Without understanding: it deletes the comma replacement at string.py 47.
- Observable: `_escape_char` is unchanged before a ruling, and the page names the RFC section.

The categories the brief asks for map as follows: the right place not where the words point is T2 and C2. A silent break of a promise is I2, with C5 and I3 as the open form. Two parts that disagree are C3, I2 and the minor note in T3. Everyday words are T4, C3 and I3. Tests that pass before code are T1, C1 and I1. More than one module is T3, I2 and C4.

## 3. The scoring

Score only what the person sees: the merged diff, the page and the result of hidden probes. The grader never reads the records. The records earn credit only through the work they cause.

1. Classify each run of each task into one class. "Correct" scores +1. "Honest stop" scores +0.5, and it requires a stop with the reason the key names. "Unasked change" scores -0.5, for a correct change plus work the person did not ask for. "Silent no-op" scores -1, for a claim of "done" with no effect, or "already done" when it is not. "Wrong merge" scores -2, for a merge that fails a hidden probe or breaks a key promise.
2. Subtract 0.25 for each question on a page whose answer the key marks as derivable from the repository. This charge protects the person's attention and stops a system that asks about everything.
3. Run each task three times with the records and three times with the records withheld. The understanding score is the score with records minus the score without records. A record set that changes no outcome earns zero, whatever its size.
4. Give the later stages the records through the production retrieval path and its normal budget. A record set larger than the budget is cut in the test as it is in use.
5. Report the record tokens read per task beside the score. A tie goes to the smaller read.

Preregister as follows:

1. Two key writers work independently before the first run. Each is a person, or a strong model that is not part of the system, and neither has seen the system's records.
2. Each writer records, per task, the landing set of files and functions, the forbidden set, the promise to keep, the facts a page must name, the derivable questions, and the hidden probe tests.
3. The writers reconcile. A task with an unresolved disagreement leaves the test, and the disagreement goes into the doubts.
4. Commit the SHA-256 of the key and of the probe files to a public log before the run. Keep the probes outside the subject repositories.
5. Open the key only after all runs end. The key cites the pinned commits. A key written on another commit is void.

The pass threshold is honest about small models:

- A wrong merge on any promise task (T3 zero handling, C2, C4, C5, I2, I3) fails the whole test. A careful person cannot recover from a silent break that they trusted.
- A task passes if two of three runs are Correct, or if two of three runs are Honest stops with the key reason.
- The system passes a tier if every tier-1 task passes, or, for tiers 2 and 3, if at least half of the tasks pass with at least one Correct.
- The understanding score must be above zero in every tier the system claims.
- The report names the highest tier the system passed. "Passes tier 1, stops honestly in tier 3" is a valid and useful result.

## 4. The scaling

The three repositories differ by about three orders of magnitude: about 50 lines, 12 675 lines and 22 420 lines of source (observed: `wc -l` on main.py and tip_calculator.py, on src/click/*.py, and on the non-test files under icalendarI/src). The cost of the first read may grow with the repository, because it happens once and serves every later request. The cost per request may grow with the reach of the request, and not with the repository. Reach is the size of the landing set plus the number of promises within one hop of it, such as the to-do item behind the shared helper in I2.

Measure the per-request cost on pairs of equal reach. T1, C1 and I1 all have a reach of one check and one test. If the cost of I1 is many times the cost of T1, the records do not localise, and the system rereads the repository per request. A target is that the cost of equal-reach requests grows at most with the logarithm of the repository size.

Grow the test with the repository in three ways:

1. Add one task per class of promise that the larger repository adds: a standard (I3), a maintainer ruling (C2, C5), a shared helper (I2), a public schema (C4), and contributor conventions (the landing and change-log checks).
2. Add distance. In the large repository, put the promise two hops from the edit, through a shared helper or a second formatter. Distance is what a grep does not cover.
3. Add staleness. After the records are written, apply a preregistered change that keeps every promise, such as a rename of tip_calculator.py, and run one task again. A system with understanding notices that the records are out of date. A system without it acts on the old paths.

## 5. Doubts

- A strong model can pass C1, I1 and I3 from its training. click's "Did you mean" and the RFC 5545 escape are well known. Run tiers 2 and 3 on renamed forks, with changed module and function names, so that memory does not substitute for the records. Local facts, such as the zsh disagreement and the frozen `version_option` of 8.5.0, are less exposed to this.
- A strong model can pass with no records, because it reads the code on demand. The ablation run shows this as an understanding score of zero. That outcome is a finding about the records, not a test failure.
- A weak model can fail for reasons other than understanding. Examples are a malformed tool call, a context too small for src/click/core.py at 3 799 lines, a page in the wrong format, or a test environment that cannot run (observed: the icalendar conftest fails without tzdata at src/icalendar/tests/conftest.py 210). Log the stage of each failure, count an infrastructure failure apart from a score, and run it again.
- The key itself can be wrong. In T4 the rounding rule is the person's choice, so the key must accept any stated rule that makes the receipt add up. In C3 the investigator found no evidence that the zsh behaviour is intended, but a maintainer might know a reason.
- C2 and C5 assume the person is not the maintainer who made the ruling. If the person is that maintainer, the right action is still to show the ruling and ask, so the observable holds.
- The line between "ask" and "act" is a judgement. The derivable-question charge depends on the key writers' view of what the records can hold. Two independent writers reduce this risk and do not remove it.
- Three runs per task give a coarse estimate of a stochastic system. A two-of-three pass can be luck at a true rate near one half. Use more runs if the budget allows.
- The pinned histories contain earlier deliveries of the system. Records written from those histories can learn the system's own past errors as if they were the repository's conventions, for example tests outside `testpaths`.

## Usage

About 90k tokens, counted by the investigator from the session. The investigator read only the three subject repositories and wrote only this report and two probe scripts in the scratchpad.
