# C5, the provenance read: the page's check line shows where a red test failed and not its error

Date: 2026-10-26, read at 19:20 to 19:37. Read at commit 3855ac49 on
`rota/foundation`, dated 2026-10-26 19:34. Read-only. The night databases
were opened with `?mode=ro`. No model call ran and no pytest ran. Meta
workflow for the read, by the rule of 2026-10-18 (provenance before a fix).
Sprint 25, row 6, candidate C5 of night 168's read.

Sources:

- The symptom records, cited and not repeated: `plans/night168-read.md`
  section 1, walk 1 (lines 55 to 75), section 2 row W8 (line 111), section 5
  row 6 (line 278) and C5 (line 301); `plans/wall-guide.md` cause 11
  (line 532).
- `rota/roles/principal.py`: `_failure_line` 512 to 519, `check_line` 522
  to 562 (the `Fails:` tail 557 to 560), the builder's last attempt 1532.
- `rota/core/harness.py`: `run` 140 to 186 (the `test_runs` write 180 to
  183), `_tail` 189 onward, the stored output 259.
  `rota/core/schema.sql` 568 to 580 (`test_runs.output`).
- `rota/DECISIONS.md` lines 1445 to 1484 (the park ask is a page with rows,
  2026-10-08). `plans/frame142-design.md` lines 340 to 346, 356 to 361, 751
  to 756 and 784. `plans/archive/stack-2026-10-09.md` line 13 (frame 142).
  `plans/stack.md` frames 127 (line 2822) and 130 (line 2791).
- `.rota/clickI_night168.db`: `messages` m39, m47 and m53, `test_runs`
  `batch_1`, `test_run_journal` seq 69, 104, 174, 175, 211 and 212.
- `.rota/clickI_night160.db` to `.rota/clickI_night168.db`, 9 files:
  `test_run_journal`, the red rows.
- `.rota/clickI_night167.principal.jsonl` and
  `.rota/clickI_night168.principal.jsonl`: the `call` rows of nights 160 to
  168, the `page` and `words` fields.
- `git log -S` on `_failure_line`, `Fails: {why}`, `startswith("E   ")` and
  `led by the run's first`; `git log -L` on `_failure_line` and
  `check_line`.

## The result

**A design gap, not a departure: frame 142's design takes the first `E   `
line of a red run, and on a collection error that line is the traceback's
`File "...", line 13`, so the error text never reaches his page.** The
ruling of 2026-10-08 asks the row to show whether the test is red, and the
row does that (observed: `rota/DECISIONS.md` 1459 to 1465). The stored run
holds the real error as its last `E   ` line (observed: journal seq 174 and
211). So the fact is in the record, and the page reader picks the wrong line
of it (reasoned: questions 1 and 2). The wall is 6 pages on 2 nights, and he
misread the cause on all 6 (observed: question 4).

## 1. Which design made the check line show the file and the line

Commit b0a2086e, 2026-10-09 00:48, "feat(rota): the park ask is a page with
the item and its criteria", added `_failure_line` and the `Fails: {why}`
tail (observed: `git log -S` on both strings, one commit each). The commit
served frame 142, "A park ask gets an answer that names no option"
(observed: `plans/archive/stack-2026-10-09.md` line 13). The design wrote
the rule: "`Fails:` and the first line of the run's output that starts with
`E   `" (observed: `plans/frame142-design.md` 343 to 345). Its review gave
the reason, finding 5: pytest cuts the `FAILED` line to the terminal width,
as night 132's run `tr248` showed (observed: the same file, 751 to 756).

The design had assertion failures in view. Its worked line is "Fails:
assert False == True." (observed: `plans/frame142-design.md` 327). An
assertion failure puts the assertion first. A SyntaxError at collection
puts the traceback frame first: `E     File "...", line 13`, then the
source line, the caret line, and `E   SyntaxError: ...` last (observed:
`test_runs` tr35 of night 168). The design did not name the collection case
(reasoned: no line of `plans/frame142-design.md` names a collection error
or a traceback).

Commits since on the two functions: a2b70a84, 2026-10-12 02:23, frame 210,
reads the latest run inside the test's own batch (observed: `git log -L` on
`check_line`; `plans/frame210-review-1.md` line 1). Nothing changed
`_failure_line` after b0a2086e (observed: `git log -L`, one commit). The
same first-line rule also writes the builder's last attempt on the page
(observed: `rota/roles/principal.py` 1532; `plans/frame142-design.md` 359).
A separate reader, frame 318's f2481197 of 2026-10-24, keeps the first `E `
line as the red's identity in `_tail` (observed: `rota/core/harness.py`
189 onward). That identity is for comparison, not for him, and the repair
leaves it alone (reasoned: the red's identity must stay stable across runs).

No rule in `rota/LAWS.md`, `rota/DECISIONS.md` or `plans/stack.md` says
which line of a red run a page shows (observed: grep for "failure line",
"Fails:", "E   " and "check line" in the three files). Frames 127 and 130
are about the Developer's fix wake, not his page (observed: `plans/stack.md`
2822 and 2791).

## 2. What the row holds

The runs behind m47 and m53 are `tst_crit_1` and `tst_crit_2` of `batch_1`
at d607d440, attempts 5 and 6 (observed: `test_run_journal` seq 174, 175,
211 and 212). Each row stores the whole pytest output in the `output`
column, 1,835 and 1,829 characters, under the 2,000-character cut of
`_tail` (observed: `test_runs` tr35 and tr36; `rota/core/harness.py` 259).
The table has no `error` column (observed: `rota/core/schema.sql` 568 to
580). The output holds the traceback frame, the source line, the caret
line, the last `E   ` line and the `ERROR tests/...` line (observed: tr35).
The last `E   ` line is the error: `E   SyntaxError: "\R" is an invalid
escape sequence. Did you mean "\\R"? A raw string is also an option.`
(observed: tr35 and journal seq 211; tr36 carries `"\L"`). m39's run,
`tst_crit_3` at journal seq 69 and 104, has the same shape (observed).

## 3. What he read

- His reading of m53 line 4: "change the first Roaming test so it clears
  both variables and runs the Windows branch, the same way the third test
  does" (observed: `.rota/clickI_night168.principal.jsonl`, the night 168
  `call` row of m53 at 09:56:50).
- The test's real `E ` line: `E   SyntaxError: "\R" is an invalid escape
  sequence. Did you mean "\\R"? A raw string is also an option.` (observed:
  `test_runs` tr35).

## 4. How often

Over nights 160 to 168, 6 pages show a red check row with no error text,
and he misread the cause on all 6 (observed: the `call` rows of the two
principal files, a `Fails: File` or a bare `Fails.` on a page line).

| Night | Pages with a red check row | Of them, no error text | Misread |
|---|---|---|---|
| 160 | 4 | 0 | 0 |
| 161 | 9 | 0 | 0 |
| 162 | 11 | 0 | 0 |
| 163 | 0 | 0 | 0 |
| 164 | 6 | 0 | 0 |
| 165 | 7 | 0 | 0 |
| 166 | 0 | 0 | 0 |
| 167 | 7 | 3: m42, m50, m56 | 3 |
| 168 | 4 calls, 3 pages | 3: m39, m47, m53 (m53 asked twice) | 3 |

Each misread names a cause in the test's setup or its call, "no app name"
or "does not clear both variables" or "does not act as Windows". Each real
error is a backslash escape SyntaxError at collection (observed: night 167
journal seq 35 and 143, night 168 seq 69 to 212). Nights 163 and 166 have
no principal `call` row with a check row (observed). By the night
databases, 8 of 318 red runs over the 9 nights have a first `E   ` line
that is a traceback frame, and all 8 are on nights 167 and 168 (observed:
`test_run_journal`, `result != 'pass'`). So the wall arrived with the
backslash wall of C2 and frame 328, and it hides that wall from him
(reasoned: the same runs).

## 5. Whether a design departure stands

No ruling of Roman's says which line of a red run his page shows, so no
departure stands. The ruling of 2026-10-08, point 2, asks the row for "its
test's expectation beside it in one line and whether that test is red", and
the row meets it (ruled: Roman, 2026-10-08 23:25, `rota/DECISIONS.md` 1459
to 1465). The first-line rule is frame 142's design choice, not his words
(observed: question 1). The intent of what reaches him is cause 11 and the
composition's "no work stays invisible" (ruled: ratified 2026-09-16, C).
The repair serves those and changes no ruling (reasoned).

## The repair

Change `_failure_line` in `rota/roles/principal.py`: when the first `E   `
line is a traceback frame, `File "...", line N`, return the last `E   `
line instead, and keep the first line in every other case. Over nights 160
to 168 this changes the 8 traceback-frame runs and none of the other 310
(observed: a simulation over `test_run_journal`; a "least indent" rule was
rejected because it also changed 4 chained-exception runs). The page's
check line and the builder's last attempt both read this function, and
`_tail`'s red identity stays as it is.

The red test, in `tests/rota/test_park_page.py`: seed `tst_crit_1` of
`batch_1` with tr35's stored output from night 168, and assert that
`check_line` ends `Fails: SyntaxError: "\R" is an invalid escape sequence.
Did you mean "\\R"? A raw string is also an option.` That is m53 line 4.
It fails today, because the line ends `Fails: File "...test_get_app_dir_roaming.py", line 13.`
(observed: the m53 page).
