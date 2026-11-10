# Can a careful person read what rota merged? A blind read, 2026-11-10

Written by one blind reader for the review of rota, the product. The
reader read no review page of the frame. Each claim carries its source.

## Result

1. 12 merged changes in the draw: the 3 dry runs, and 9 of 74 night merges. All 12 commits still exist.
2. A careful reader can say what the change does from the diff alone in 12 of 12. 7 of 12 hold a part the diff does not explain.
3. The change does what the words ask in 8 of 12. 3 put `echo_json` far from `echo`. 1 does nothing (night 152, `show_python`).
4. The change does more than the words ask in 6 of 12: extra parameters, a second file, and a second exit path.
5. No page to the person says what merged, in 0 of 12. After a merge the person reads one line: "Done: 1 change built, tested and merged."
6. No page names the merge commit, the files, the tests added, or what nobody checked.
7. By my own check, 11 of 12 are right and 1 is wrong. Rota reported the wrong one as built, tested and merged.
8. In 2 nights the person contested the plan, and rota read his words back wrong. The batch merged with no page between (nights 141, 173).
9. The person must run `git log` and `git show` alone to learn what he got. 10 of 12 merge commits are on no branch.
10. Every commit of a model carries the name of the machine's git user. The merge message is "rota: deliver bg_1", with no body.

## Part A. The population and the draw

- The dry runs (observed: `batches` with `status='merged'` in `.rota/dry1.db`, `dry2.db`, `dry3.db`):
  - dry1, clickI, `bg_1`, item `click_pause_returns_true_on_key`, merge `09c82f3b`.
  - dry2, tipsI, `b_1`, item `raises_value_error_for_invalid_tip_percentage`, merge `ff1f65ff`.
  - dry3, icalendarI, `bg_1`, item `canonical_order_duplicate_keys`, merge `4f12af1e`.
- The nights: 98 files `.rota/clickI_night*.db` (observed: glob). 47 files hold a merged batch. The population is 74 merged batch rows.
- The 74 rows cover 8 items. `echo_json` has 33 rows, `confirm_default_on_eof` 13, `version_option_show_python` 7 (observed: `scratchpad/readable/inv.py`).
- Two rows share one head commit, nights 103 and 104 at `e1f99723` (observed: `exists.py`). Night 103 is a seam night that resumed the batch of night 101 (observed: `.rota/night103.log`).
- The sort is by file name as a string, then batch id. So `clickI_night100.db` comes before `clickI_night92.db`.
- `random.Random(364).sample(pop, 9)` drew, in draw order:

| draw | file | batch | item | merge commit |
|---|---|---|---|---|
| 1 | clickI_night100.db | bg_1 | echo_json | adf3b6a3 |
| 2 | clickI_night126.db | bg_2 | confirm_default_on_eof | 8628cd39 |
| 3 | clickI_night173.db | bg_2 | clear_returns_status | fc0ee70e |
| 4 | clickI_night102.db | bg_1 | echo_json | f60ce8e7 |
| 5 | clickI_night103.db | bg_1 | echo_json | a4dbf3f7 |
| 6 | clickI_night136.db | bg_1 | echo_json | 7ac61388 |
| 7 | clickI_night152.db | bg_3 | version_option_show_python | 948ea247 |
| 8 | clickI_night141.db | bg_1 | echo_json | 7b1e425a |
| 9 | clickI_night132.db | bg_1 | echo_json | 7091f8c8 |

- How I found each merge (observed: `merges.py`). I started at `config.project_commit` and walked first parents. I took the commit "rota: deliver <batch>" with two parents. `rota/core/worktrees.py:487` writes that message with `merge --no-ff`.
- The change is the diff from the first parent to the merge. The second parent is a commit "rota: tests of <batch>" after `batches.head_commit`.
- All 12 merges exist in `D:/repos/_AI/sample_repos/clickI`, `tipsI` or `icalendarI`. 0 changes are not recoverable.
- Only the dry1 merge (clickI `main`) and the dry2 merge (tipsI `master`) are on a branch. The other 10 are reachable from no branch (observed: `git branch -a --contains`).

## Part B. One row per change

Columns: 1 the diff alone, 2 the words against the change, 3 what rota told him, 4 my own check, 5 the commit as he meets it.

| change | 1. diff alone | 2. words vs change | 3. pages | 4. own check | 5. commit |
|---|---|---|---|---|---|
| dry1 bg_1 | `pause()` in `src/click/termui.py` returns `False` on no terminal and `True` at the end. Source +3 -2. 3 new test files, +37. One test, `test_raw_terminal_non_terminal`, tests `raw_terminal`, not `pause`. I cannot explain that test (observed: diff). | Words: "Make click.pause() return True when it waited for a key and False when it skipped" (observed: `entries` e_m1). Does that. Nothing more in the source. Nothing left out. | The page after the merge said "The team stopped work on this change" and "the change could not start" (observed: `m144`, rendered now). His reply: "This page is wrong. The change merged" (observed: e_m146). The state view says "Done: 1 change built, tested and merged" (observed: `render_state`). | Right. No terminal gives `False`, a key gives `True`, and Ctrl-C also gives `True`. `tests/test_termui.py` and `tests/test_utils`: 411 passed on the parent and on the merge (observed: `runtests.py`, `probe_click.py`). | Merge by `rota <rota@local>`, "rota: deliver bg_1", no body. 2 branch commits as "Roman Kubiv". The source message says what changed. Test names carry ids: `test_termui_tk_1_criteria_waited.py`. |
| dry2 b_1 | A range check, 0 to 100, raises `ValueError` in `calculate_tip` of `tip_calculator.py` and in a second copy in `main.py`. Removes the newline at the end of `tip_calculator.py`. Source +5 -1, 3 test files +33. | Words name `tip_calculator.calculate_tip()` (observed: e_m1). Does that. Also edits `main.py`, which the words do not name. The plan page named `main.py` before the build, and he said ok (observed: `m24`, rendered now). | `m24` before the build lists the checks and the files it expects to touch. No page after the merge names the change. State: "Done: 1 change built, tested and merged. It carries 1 choice ... and 2 invented test values" (observed: `render_state`). | Right. -5, -0.01, 100.5 and 101 raise. 0, 15 and 100 give 0.0, 30.0 and 200.0, in both files. The 7 tests pass (observed: `probe_other.py`). | As dry1. `test_calculate_tip_c_3.py` imports `builtins` and does not use it. Two tests end with `assert True`. |
| dry3 bg_1 | `canonsort_keys` in `src/icalendar/caselessdict.py` raises `ValueError` on a duplicate in `canonical_order`. Docstring updated. The newline at the end of the file is gone. 3 test files in a root `tests/`. The project keeps its tests in `src/icalendar/tests` (observed: tree). | Words: "raise ValueError when canonical_order names the same key twice, and sort the keys as before otherwise" (observed: e_m1). Does that. Nothing more. Nothing left out. | `m40` before the build. No page after the merge (observed: `messages`, last page `m40`). State as dry2, with "8 notes". | Right. `["B","B"]` raises. `["B","C"]` gives `['B','C','A']` as on the parent. The project suite gives 12220 passed and the same 8 failures on both (observed: `src/icalendar/tests` with tzdata in scratch). The batch inherited only `.github/workflows/test_generate_matrix.py` as an old test (observed: `tests` rows). | As dry1. The merge is reachable from no branch. |
| night 100 bg_1 | `echo_json(obj, nl=True, err=False)` right after `echo` in `src/click/utils.py`, with no blank line before it. Dead code: `file = None`, then `if file is None`. `import json` twice. `versionadded:: 8.17.0`, and the project is `8.5.0.dev` (observed: `pyproject.toml`). +46, 3 test files +86. | Words: "Add an echo_json(obj) helper next to echo that prints an object as compact JSON on one line, followed by a newline" (observed: e_p1). Does that. More: parameters `nl` and `err`. Not exported as `click.echo_json` (reasoned: a reader can ask). | The person was a script: every page got "yes that all looks right, go ahead" (observed: `.rota/night100.log`). After the merge: "Done: 1 change built, tested and merged." (observed: line 51). | Right. Compact output with one newline. A set raises `TypeError`. The area tests give 513 passed on the parent, 516 on the merge (observed). | Merge as dry1. 5 branch commits, with 2 "Fix UnboundLocalError" commits. |
| night 126 bg_2 | `confirm(..., default_on_eof=False)`. On `EOFError` or `KeyboardInterrupt` with the flag on and a default, it returns the default. Removes the two blank lines before `get_pager_file`. +8 -2, 2 test files +30. | Words: "when stdin is closed it returns the default instead of aborting" (observed: e_p2). Does that. More: Ctrl-C also returns the default. | Script principal (observed: `night126.log`). After the merge: "Done: 1 change built, tested and merged." (observed: line 101). | Right on EOF: flag on gives the default, flag off aborts. Ctrl-C with the flag on returns `True` (observed: `probe_click.py confirm`). The parent refuses the flag. | As night 100. Two commits with the same message, "Add default_on_eof flag to confirm()". |
| night 173 bg_2 | `clear()` returns `False` on no terminal and `True` after the escape. +3 -2, 3 test files +25. Test c_3 repeats c_1 and c_2. | Words: "Make clear() return True when it cleared the screen and False when stdout is not a terminal" (observed: e_p2). Does that. Nothing more. | The plan page `m61` showed "check: none yet" and "expected to touch nothing named". He said line 5 must name `clear`. The read-back on the next request's page said "line 5 is wrong: remove src/click/termui.py:clear". He replied "I never sent that answer" (observed: `clickI_night173.principal.jsonl`). No page names the merge. | Right. Terminal gives `True`, no terminal gives `False`. 522 passed on both (observed). | As night 100. Base is the merge of bg_1, `get_app_dir`. |
| night 102 bg_1 | As night 100, without the dead code. Turns every `TypeError` or `ValueError` of `json.dumps` into a new `TypeError`. +39, 3 test files +87. | Words as night 100. Does that. More: `nl`, `err`, and a circular list now raises `TypeError`, not `ValueError`. | Script principal. After the merge: "Done: 1 change built, tested and merged." (observed: `night102.log` line 48). | Right on the words. The circular list gives "Object of type list is not JSON serializable", which is false (observed: probe). | As night 100. |
| night 103 bg_1 | As night 100. A `try` that only re-raises. A branch for bytes output that `json.dumps` never makes. No blank line before `_get_binary_stream`. +43, 3 test files +87. | Words as night 100. Does that. More: `nl`, `err`. | A seam night with 0 pages: "MERGED (1 total) after 3 steps, 0 asks" (observed: `night103.log`). His pages were in night 101, not read. | Right (observed: probe). | 17 branch commits. They switch the ANSI stripping on and off three times. |
| night 136 bg_1 | `echo_json(obj)` at the end of `utils.py`, after the module `__getattr__`, 340 lines from `echo`. +11, 3 test files +38. `test_echo_no_deps` splits on `"\\n"`, so its loop checks one line. | Words as night 100. Prints as asked. Leaves out "next to echo". He said "Put the helper in the same source file where echo lives" (observed: jsonl `m53`). | Seat was a model (observed: jsonl `"model": "opus"`). `m57` predicted `tests/test_utils/test_echo.py`. The tests went to 3 new files. After the merge: "Done: 1 change built, tested and merged." The next pages asked about `echo_json` again (observed: jsonl `m78`). | Right on output (observed: probe). With no stdout, it fails on `None.write` (reasoned: no `None` check, unlike `echo`). | As night 100. |
| night 152 bg_3 | Adds `show_python: bool = False` and its docstring to `version_option` in `src/click/decorators.py`. No code uses the flag. Adds a comment "Append Python version if show_python is enabled" with no code. Adds two unreachable lines after `return` and an unused `import sys`. +7 -2, 1 test +16. | Words: "Give version_option a show_python flag that appends the running Python version to the message" (observed: e_p3). Does not do that. | `m145` showed "check: none yet". He asked to limit line 3 to the version tests. Then the merge, and: "Done: 3 changes built, tested and merged." (observed: `night152.log` lines 135 to 140). | Wrong. `show_python=True` prints "prog, version 1.2.3" with no Python version (observed: `probe_click.py version`). The test asserts `hasattr(cmd1, '_show_python') or True`, so it always passes. | 6 branch commits. The last is "Restore original version printing logic and add show_python flag". |
| night 141 bg_1 | `echo_json(obj, file=None)` at the end of `utils.py`. It writes to `sys.stdout` with no flush. +13, 1 test +10. | Words as night 100. Prints as asked. More: `file`. Leaves out "next to echo". On `m59` he said "The new helper should go next to echo and leave echo itself unchanged" (observed: jsonl). | His `m59` reply said "Line 2 looks right". The ruling row holds `echo_json_compact: contest` and `bg_1: contest` (observed: `rulings` r_d9cb147a6d). The touch rows kept the pager test he refused. The next page is for the next request (observed: jsonl `m64`). | Right on output (observed: probe). | As night 100. Two commits "Add file parameter to echo_json". |
| night 132 bg_1 | `echo_json(obj)` at the end of `utils.py`, `versionadded:: 8.5`. +13, 3 test files +38. `test_echo_json_compact` holds an unused `capture` function and a comment "Actually, we need to capture the output". | Words as night 100. Prints as asked. Leaves out "next to echo". Nothing more. | Script principal. After the merge: "Done: 1 change built, tested and merged." (observed: `night132.log` line 46). | Right on output (observed: probe). | As night 100. |

## Part C. The counts over the draw of 12

| measure | count | which |
|---|---|---|
| A reader can say what the change does from the diff alone | 12 of 12 | 7 hold a part the diff does not explain: dry1, dry2, dry3, nights 100, 102, 103, 152 |
| The change does what the words ask | 8 of 12 | 3 in part (nights 136, 141, 132: not next to `echo`); 1 no (night 152) |
| The change does more than the words ask | 6 of 12 | dry2, nights 100, 102, 103, 126, 141 |
| A page says what merged | 0 of 12 | the only text is the count line "Done: N change(s) built, tested and merged" |
| Right by my own check | 11 of 12 | wrong: night 152. Not checked: 0 |

- The "more" in dry2 was on the plan page before the build. The other 5 were on no page that I saw (observed: the pages of Part B).
- The counts rest on code behaviour. The test files hold more defects, and Part B names them.

## Part D. What a careful person cannot learn from rota

1. Which commit merged. No page and no state line names a commit, a branch or the batch id (observed: `render_state` in `rota/roles/principal.py`, lines 538 to 557; the night logs).
2. Which files changed, and how many lines. The plan page names the files the team expects to touch, before the build. Night 136 predicted one test file, and the change added three others.
3. Which tests were added and what they assert. The plan page names checks, but in nights 141, 152 and 173 it said "check: none yet" when he approved (observed: jsonl).
4. Whether a test proves anything. `or True` (night 152), `assert True` (dry2, night 100), and a test of `raw_terminal` for `pause` (dry1) all count as checks.
5. That a change does not do the request. Night 152 merged a flag that does nothing, and the state view said "built, tested and merged".
6. What the change does beyond his words: `nl`, `err`, `file`, the Ctrl-C path, the second `calculate_tip`.
7. What nobody checked. No page says that the project suite of icalendar was not inherited (observed: dry3 `tests` rows). No page says that the harness ran on Windows only (reasoned: the runs are on this machine).
8. That his contest landed as something else. Nights 141 and 173 merged after a reading that inverted his words (observed: Part B).
9. Who wrote the code. Every model commit carries "Roman Kubiv <romankubiv101@gmail.com>" (observed: `authors.py`). A reader of `git log` reads it as the person's own work.
10. Where the change lives after the run. 10 of 12 merges are on no branch, and a `git gc` can delete them (reasoned: git removes unreachable objects).

To learn what he got, he must do these steps alone:

1. Find the merge with `git log --grep "rota: deliver"`. That works only while the merge is on a branch.
2. Read `git show -m` or `git diff <parent> <merge>`.
3. Read each new test file, because a passing test can assert nothing.
4. Call the function himself.

## Part E. Limits

- The dry run pages are `render_page()` of today's code on the final database, not the page as shown. `m_park_a162344dbf_bg_1` of dry1 did not render: "no such column: t.commitment_id".
- For nights 100 to 132 I saw only the first line of each page and the state line, in the night logs. No `principal.jsonl` exists for them.
- Night 103's request and pages are in the database of night 101, which I did not read.
- I did not read the build transcripts or the turn copies of the dry runs. So I cannot say what the build session saw on the terminal after each merge.
- In the nights the person was a script (100 to 132) or an Opus seat (136 to 173). Neither is a careful person reading a diff.
- My checks ran on Windows, Python 3.14.2, with `PYTHONPATH=src` on `git archive` copies. Click's area tests skip 1090 on the parent and on the merge alike. icalendar needed tzdata, which I put in the scratch folder.
- "Next to echo" and "not exported as `click.echo_json`" are my reading of the words. A reader can read them another way.
- The draw is 9 of 74 night rows, and 6 of the 9 are `echo_json`. The 33 `echo_json` rows of 74 make that share likely.
- Scripts and copies are in `C:\Users\roman\AppData\Local\Temp\claude\6d9eb18c9e6274ab\1efd37b1-058e-4b19-8ab1-e1a6c654a389\scratchpad\readable\`.
