# F37 review 1: cb5d8dc1 on f37root, the branching statement for a criterion of several cases

**Verdict: not ready to merge. 2 high findings, 4 low findings.** The case-word gate fits night 171's wording only. One `if` that wraps the whole change lands as the line of every criterion of several cases, and that is frame 170's fault again. The touched test file passes: 102 passed.

## (a) The points

1. Word list. `_CASE_WORDS` counts `if`, `when`, `whenever`, `unless`, `otherwise`. 10 of 12 two-case criteria miss, and 3 of 6 one-case criteria hit. HIGH, finding 1.
2. Yes. One 8-line `if` that wraps the change lands for three criteria at once. Night 171's own c_3 text lets the 4-line block land for c_1 and c_3. HIGH, finding 2.
3. One Python parser. The change reuses the module's `_ast` (api.py 24), as `_parses` (14605) does. The change adds a third diff walker, `_added_runs`, beside `_added_kinds` and `_added_lines`. LOW, finding 5.
4. Yes. The named lines land as text with line breaks and as a list of lines. The generic sentence names no syntax for a value of several lines. LOW, finding 6.
5. No reader was missed. The only reader of `verdicts.lines` outside the door is `nightreport.py` 704, and it counts entries. The Critic prompts still say "the line", as the pass report states.

## (b) Findings

1. **The case gate is a word list that fits night 171's wording.** `rota/roles/api.py` 14404 to 14412 and 14973. HIGH. CONFIRMED: probe `p1_cases.py` tested 12 criteria that name two cases. Only 2 hit, and both hold "when" and "otherwise". The brief's own form "Returns X if A, else Y" misses. "For an empty list ... and for a full list ...", "both A and B", "for roaming=True and ... for roaming=False" and "on Windows ...; on POSIX ..." miss. Of 6 criteria with one case, 3 hit: "If the cache is warm ... even when ...", "when the option is unknown, as if ...", "if ... when ...". Probe `p1_db.py` on night 158's database: 2 of 7 criteria hit, and both are one case, "When confirm() is called ... if that read hits end of file". Night 171's c_1 holds "When", "If", "If", the shape the list was cut from. Fix: decide the admission from the diff and the guards of finding 2, not from words, or measure any word rule against the criteria of the stored night databases before it ships.

2. **One large branching statement lands as the line of every criterion of several cases.** `rota/roles/api.py` 14443 to 14467 (`_branch_kind`) and 14973 to 14975. HIGH. CONFIRMED: probe `test_p2_wrap.py` adds a function whose body is one 8-line `if`. The same 8 lines land for c_1, c_2 and c_3 in one pass, in the text form and in the list form. For the whole function, the refusal names lines 2 to 9 and tells the seat to send them, so the door steers the seat to the block. Probe `p2_kinds.py`: an `if` that guards a `def` and a `class`, a `try` that wraps a `def`, and a 6-line dict literal with one conditional expression all count as one branching statement. So the "a whole function is no branch" guard falls to one wrapping `if` or `try`. Probe `test_p2_n171.py` uses c_3's text from night 171's database, which now holds "when roaming=False". The 4-line block lands for c_1 and c_3 at once. s128's 8-line value for c_3 now gets "Send those 4 lines alone for c_3". The pass report's "c_3 at review time holds one" holds only for the text at review time. Fix: refuse one block named for two criteria, refuse a branch whose body holds a `def` or a `class`, and refuse a block that holds every added code line of its hunk.

3. **An added `elif` or `else` arm never lands.** `rota/roles/api.py` 14449 to 14452. LOW. CONFIRMED: probe `p3_elif_time.py`, `_branch_kind` on `elif mode == 'b':` with its `else:` returns None. A change that adds one case to an existing chain is the common shape of a two-case criterion, and its run does not parse alone. Fix: parse a run that opens on `elif`, `else` or `except` under a stub header, or with its context lines from the function-context diff.

4. **`_branch_inside` is slow on a long pasted value.** `rota/roles/api.py` 14486 to 14502. LOW. CONFIRMED: probe `p3_elif_time.py`, a 300-line value with 60 `if` starts took 7.71 seconds on one refusal. Each start parses every longer slice, and `_branch_block` re-parses per run. Fix: parse each added run once, and take each statement's span from `lineno` and `end_lineno`.

5. **A third walker of the unified diff.** `rota/roles/api.py` 14415 (`_added_runs`) beside 14644 (`_added_kinds`) and 17435 (`_added_lines`). LOW. PLAUSIBLE: each walker holds its own header test and its own idea of an added line. `_added_runs` keeps indentation, and the others strip it. A later fix to one header rule, such as a removed line whose text starts with `--`, then reaches one walker of three. Fix: let `_added_kinds`'s walk also return the runs, so one walk reads the diff.

6. **The refusal opens with a sentence that the next sentence takes back.** `rota/roles/api.py` 15034 to 15038 and 14981 to 14985. LOW. PLAUSIBLE: the text says "Copy the one line of the [diff] block that meets c_1" and then that one statement "also counts as one line". The generic sentence, with no statement inside the value, names no form for several lines in one value. Night 171's seat wrote line breaks inside one string, so a seat on that card knows one form. A seat on another card may send one line again. Fix: for a criterion of several cases, open with the statement form, and name "one string with line breaks, or a list of lines".

Outside the points:

- The pass report's reach is right for the door. `_first_pass_hold` quotes each part with `'{p}'`, not with `repr`, so a part such as `log.warning('missing')` shows broken quotes. That predates the change, and the change sends more such parts to it.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/6d9cf7e1-0faa-4156-bacb-f95ee6e7ec4f/scratchpad/f37probe/`. Each ran from `C:/Users/roman/rota_f37` with `PYTHONPATH` set to the worktree.

- `p1_cases.py`: `_names_cases` on 12 two-case and 6 one-case criteria. 2 of 12 hit, 3 of 6 false hits.
- `p1_db.py`: `_names_cases` on the criteria of the night 171, 158, 159, 160 and frame 306 databases, opened read-only. Night 171: 2 of 2 hit, c_3 by its amended text. Night 158: 2 one-case hits. Night 159: 1 hit.
- `test_p2_wrap.py`: pytest on a function that is one 8-line `if`. 3 passed: the block lands for three criteria, the list form lands, and the refusal names lines 2 to 9.
- `p2_kinds.py`: `_branch_kind` on a version guard over a `def`, a dict literal and a `try` over a `def`. All three count.
- `test_p2_n171.py`: pytest on night 171's fixture with c_3's database text. 2 passed: one block lands for c_1 and c_3, and the 8 lines for c_3 get "Send those 4 lines alone for c_3".
- `p3_elif_time.py`: `_branch_kind` on an `elif` arm returns None. `_branch_inside` on 300 parts took 7.71 seconds.
- `ROTA_MODEL=qwen3:8b python -m pytest tests/rota/test_verdict_lines.py -q`: 102 passed in 68.78s.
- A read of s128's turns in night 171's database: the seat writes a block as one string with line breaks.

## (d) Usage

- Input tokens: about 75k. Output tokens: about 10k. Total: about 85k. The harness gives no exact count, so the numbers are estimates.
