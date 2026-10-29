# Frame 345: the L3 rulings cases with `_faulted_approve` off

1. With `_faulted_approve` off, 0 of 24 cases read right, the same as before. 1 of 72 runs reads right, the same run as before (observed: the two runs).
2. No run changed its reading. No run went from right to wrong. The right run is L3R-n174-m53-m55 run 2 in both runs (observed: the two runs).
3. The refusals fell from 199 to 170. The door's own refusals fell from 24 to 0. The other refusals fell from 175 to 170 (observed: the two runs).
4. The door fired in 18 runs of 8 cases. With the door off, the line it named took the expected verdict in 13 runs of 6 cases, so its refusal there was wrong (observed: the two runs).
5. In 4 runs of 2 cases the door was right: with it off, the seat approved lines that the case expects to be contested. 1 run gives no verdict (observed: the two runs).

## The experiment

- Worktree `C:/Users/roman/rota_f345x`, branch `f345x`. The baseline is at `d9bc5e96`. The experiment is at `89f37240`, "experiment(doors): _faulted_approve off for the L3 rulings cases".
- The change: in `_line_refusal` of `rota/roles/api.py`, `approve = None` replaces the call to `_faulted_approve`. Nothing else changed.
- The command: `ROTA_L1=1 ROTA_MODEL=qwen3:8b ROTA_NUM_CTX=12288`, no `ROTA_PROFILE`, `python -m pytest tests/rota/test_l3_rulings.py -q -s -n0 -p no:cacheprovider`.
- The outputs: `l3r_baseline.txt` (24 failed in 903.50s) and `l3r_no_faulted.txt` (24 failed in 706.72s), both at the worktree root. The second run started at 01:19:06 UTC and showed no connection error and no model-load error.
- A case reads right when 2 of its 3 runs read right, as the test judges it.

## Question 1: runs right per case, and the refusals per case

| case | runs right before | runs right after | refusals before | refusals after | runner errors before | runner errors after |
|---|---|---|---|---|---|---|
| L3R-n170-m6-m7 | 0 | 0 | 12 | 3 | 2 | 0 |
| L3R-n170-m58-m59 | 0 | 0 | 12 | 12 | 0 | 0 |
| L3R-n170-m74-m75 | 0 | 0 | 7 | 7 | 0 | 0 |
| L3R-n171-m27-m28 | 0 | 0 | 3 | 3 | 0 | 0 |
| L3R-n172-m76-m77 | 0 | 0 | 7 | 7 | 2 | 2 |
| L3R-n172-m92-m93 | 0 | 0 | 11 | 11 | 1 | 1 |
| L3R-n172-m97-m98 | 0 | 0 | 6 | 6 | 0 | 0 |
| L3R-n172-m80-m81 | 0 | 0 | 11 | 6 | 2 | 0 |
| L3R-n172-m83-m84 | 0 | 0 | 5 | 5 | 2 | 2 |
| L3R-n173-m90-m91 | 0 | 0 | 9 | 9 | 3 | 3 |
| L3R-n173-m90-m92 | 0 | 0 | 6 | 3 | 0 | 0 |
| L3R-n173-m34-m35 | 0 | 0 | 5 | 5 | 0 | 0 |
| L3R-n173-m61-m62 | 0 | 0 | 9 | 9 | 2 | 3 |
| L3R-n174-m47-m48 | 0 | 0 | 6 | 5 | 1 | 2 |
| L3R-n174-m53-m55 | 1 | 1 | 9 | 9 | 0 | 0 |
| L3R-n174-m53-m58 | 0 | 0 | 9 | 9 | 0 | 0 |
| L3R-n175-m44-m45 | 0 | 0 | 9 | 9 | 1 | 1 |
| L3R-n175-m44-m46 | 0 | 0 | 10 | 10 | 1 | 1 |
| L3R-n175-m75-m76 | 0 | 0 | 6 | 3 | 0 | 0 |
| L3R-n175-m75-m77 | 0 | 0 | 4 | 4 | 0 | 0 |
| L3R-n175-m102-m103 | 0 | 0 | 0 | 0 | 0 | 0 |
| L3R-n175-m116-m118 | 0 | 0 | 15 | 15 | 2 | 2 |
| L3R-n175-m121-m122 | 0 | 0 | 13 | 8 | 0 | 0 |
| L3R-n175-m136-m138 | 0 | 0 | 15 | 12 | 0 | 0 |
| total | 1 | 1 | 199 | 170 | 19 | 17 |

The turns fell from 274 to 244 (observed: the two runs).

## Question 2: the refusal texts that went away and the ones that appeared

The key is the tool and the first 60 characters of the text. Line numbers become N, a quoted text becomes Q, and "lines" becomes "line". The table shows the keys whose count changed. The 22 other keys kept their count (observed: the two runs).

| before | after | change | key |
|---|---|---|---|
| 22 | 0 | -22 | `rulings.rule: The words fault line N, "Q". An approve keeps the line as it` |
| 2 | 0 | -2 | `rulings.rule: The words fault line N, "Q", line N, "Q", line N, "Q", line ` |
| 3 | 0 | -3 | `rulings.rule: line N: his words 'Q' ask no removal of src/click/utils.py:N` |
| 2 | 0 | -2 | `rulings.rule: line N: 'Q' is not an act. An act is drop, keep, rewrite, ad` |
| 9 | 8 | -1 | `rulings.rule: rulings has a key words, and words is its own argument, not ` |
| 21 | 20 | -1 | `rulings.rule: line N have no ruling. Every line of the page takes one: the` |
| 4 | 3 | -1 | `rulings.rule: line N: a revise rewrites the line, and his words neither fa` |
| 8 | 7 | -1 | `rulings.rule: line N: the act drop rests on 'Q', and his words do not hold` |
| 11 | 13 | +2 | `rulings.rule: The words name line N and do not name line N. A contest rest` |
| 5 | 7 | +2 | `rulings.rule: line N: the act keep rests on 'Q', and his words do not hold` |

The first two rows are the door's 24 refusals. Only two keys grew, each by 2. No new key appeared (observed: the two runs).

## Question 3: did the door's refusals hold

For each run where the door fired in the baseline, the table reads the verdict of the named line in the run with the door off. The cue is the word the door quoted (observed: the two runs).

| case | runs | line | cue | with the door off |
|---|---|---|---|---|
| L3R-n170-m6-m7 | 1, 2, 3 | 1 | "are fine" | verdict as expected, door wrong |
| L3R-n172-m80-m81 | 1, 2, 3 | 1 | "drop" | verdict as expected, door wrong |
| L3R-n175-m116-m118 | 3 | 2 | "alone" | verdict as expected, door wrong |
| L3R-n175-m121-m122 | 1, 2, 3 | 9 | "not" | verdict as expected, door wrong |
| L3R-n175-m136-m138 | 1, 2, 3 | 2 | "instead" | verdict as expected, door wrong |
| L3R-n175-m75-m76 | 1, 2, 3 | 5 | "has" | approve where contest is expected, door right |
| L3R-n174-m47-m48 | 3 | 8 to 67 | "drop" | approve where contest is expected on 59 lines, door right |
| L3R-n174-m47-m48 | 1 | 8, 25 to 39 and more | "drop" | no ruling landed, no verdict |

Totals: door wrong in 13 runs, door right in 4 runs, no verdict in 1 run (observed: the two runs).

## Question 4: how the wrong runs changed

The test lists the problems of each wrong run. The table counts them per class over all 72 runs. A run that landed no ruling counts in no other column (observed: the two runs).

| class | before | after |
|---|---|---|
| runs that landed a ruling | 50 | 53 |
| lines approved where the case expects contest | 6 | 68 |
| lines with another wrong verdict | 23 | 15 |
| lines with a wrong act or target kind | 146 | 179 |
| lines with no ruling | 24 | 27 |

- L3R-n170-m6-m7 landed no ruling in its 3 runs before. After, all 3 runs landed a ruling, and lines 18 to 28 have no act (observed: the two runs).
- L3R-n172-m80-m81 landed in 1 run before and in 3 after. Each run now fails on the act of line 2 only (observed: the two runs).
- L3R-n175-m121-m122 and L3R-n175-m136-m138 lost their wrong verdict on line 9 and line 2. They still fail on lines 7 and 8 (observed: the two runs).
- L3R-n174-m47-m48 run 3 approved lines 8 to 67 after, where the case expects contest. 59 of the 62 new approve-for-contest lines come from this run (observed: the two runs).
