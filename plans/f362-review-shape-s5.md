# Review: frame 362, shape pass S5 and S5b, `9c8ad879`

Verdict: fix. The diff does what the report says. `code.callables` did not change. The tests are red and green where the report says. Three high findings stop the op from meeting its own purpose on Q5. On `from_ical`, `model.shape` gives 40 rows that share a word and no note. A 40-row reply is cut at 6000 characters. On `Calendar`, the `callers` field lists only test files and misses `cli.py`.

## (a) The eight points

1. The op's rows: PARTLY TRUE, CONFIRMED. The paths, spans, `copies`, `entry_point` and `exported` match the tree at `99619246`. The `callers` and `test_callers` fields are wrong for `Calendar` (finding 3). The `from_ical` lead row is a word hit, not the method (finding 1).
2. `code.callables` unchanged: CONFIRMED. The rows, the order and the cut notes are the same at `623b3ada` and `9c8ad879` for three hints, one of them the dry run 5 item text.
3. The two rule additions: RIGHT, WITH NOISE, CONFIRMED. The dotted split brings back the `_NOT_VOCABULARY` words (finding 5). The script match fires on the package name (finding 6). The whole-name rule needs an identifier rule that keeps the case (finding 7).
4. The Architect's ask: CONFIRMED. The `.tools` line has the same form as the other lines. The `ask.md` sentence promises a note that the op does not give on `from_ical`. One recorded case goes STALE. `model.shape` is never pushed without an argument.
5. The probe's block: CONFIRMED by simulation. The ranking puts attached rows last but does not remove them. On Q1, Q2 and Q5 the fixtures stay. On Q4 the fixture `dtstart` drops, but only because the 40-row cap cuts it (finding 4).
6. The tests: CONFIRMED. 13 red at `623b3ada`, 2 red at `7e3d8848`, 13 green at `9c8ad879`. There are 0 CR bytes. The diff stat matches the report's list of nine files, and the report gives a reason for each. No case pins the dotted split (finding 8).
7. Cost: NOT A WALL ON TIME, A WALL ON SIZE, CONFIRMED. A `shape_of` call takes 1.3 to 2.0 s, and the eight questions take 14.2 s together. A 40-row reply is 9,024 to 10,823 characters, against a render limit of 6000 (finding 2).
8. Outside the points: three low findings (10 to 12).

## (b) Findings

### High

1. `rota/roles/api.py:5258-5268`, CONFIRMED. `model.shape("from_ical")` gives 40 of 72 rows, and `ICalParsingError` leads. No row has the name `from_ical`, and no note says so. The tree defines `from_ical` at `cal/calendar.py:101` and `cal/component.py:529`. The design, section 3.5 item 2, and `ask.md:10-12` both promise a note when the index does not name the name. The note fires only when no word matches at all.
   Fix: when no row's whole name equals the name or its last dotted part, put a note row first. The note says that no definition has that name, that the index holds no methods, and that the rows below only share a word.

2. `rota/roles/api.py:5326` against `rota/core/runner.py:1080`, CONFIRMED. `_render` gives 10,823 characters for `Calendar`, 10,244 for `Calendar.from_ical` and 9,024 for `from_ical`. `RESULT_CHARS` is 6000. The wake shows 20 to 26 whole rows, cuts a row in the middle, and says "Nothing returns the rest". The `Calendar` row alone lists 21 callers in full.
   Fix: limit each caller list to 3 paths and a count, as `shape_for` does. Then set the op's cap so that a reply fits in 6000 characters.

3. `rota/onboarding/shape.py:49-61` and `rota/roles/api.py:5346-5351`, CONFIRMED. For `Calendar`, `callers` holds 21 files and all of them are under `src/icalendar/tests`. `test_callers` is empty. `cli.py:133` calls `Calendar.from_ical(f.read())`, but `code_calls` has no row from `cli.py`. So the reply to Q5, "who is affected", names only tests, and it names them as program callers. The test split is wrong because the dry run 5 frame rules `src` as program. The miss of `cli.py` comes from `code_calls`, which reads direct calls only. The report records both as residue, but the op still shows the false fields.
   Fix: make the indexer write a `code_calls` row for `Name.attr(...)` when `Name` resolves to an imported class grain. Until then, make the op label `callers` as "direct calls only".

### Low

4. `probes/consult.py:112-115`, CONFIRMED by simulation. `shape_for` applies the whole-name filter to the rows that remain after the 40-row cap of `shape_of`. I simulated pass 5 by setting `kind_of` to `attached` under `src/icalendar/tests/`. With that change, Q4 loses `dtstart` past the cap, and Q1, Q2 and Q5 still keep the fixtures `calendar` and `component`. A whole-name hit of the surface or attached kind is kept only when fewer than 40 hits rank ahead of it.
   Fix: apply the whole-name filter to all hits before the cap, with a `cap=None` parameter on `shape_of`. Then drop rows where `_is_test_file` is true, or mark them as tests.

5. `rota/roles/api.py:5280`, CONFIRMED. The dotted split adds back the parts that `_words_in` drops as `_NOT_VOCABULARY`. `string` is one of these parts. So `model.shape("string._foldline")` goes from 5 hits at `7e3d8848` to 36 at `9c8ad879`, and `parser.string._foldline` goes from 12 to 43. The report (f) says "The rows that `model.shape` returns do not change", and these counts show that the claim is false for dotted names. The split also helps: `_foldline` moves up to the second row.
   Fix: let a dotted part feed only the whole-name set, or skip a part that `_NOT_VOCABULARY` holds.

6. `rota/roles/api.py:5318-5319`, CONFIRMED. A script name that is also the package name matches every question that names the project. "Does icalendar keep a broken line?" and the path `src/icalendar/cal/calendar.py` both put `cli.py::main` first. `shape_for` keeps a command row with no filter. Q8 is the case where the rule is right.
   Fix: match a command only when the text writes it as a command, in backticks or next to the word "command". Do not match a script name that is the same as the project name.

7. `probes/consult.py:114-115`, CONFIRMED. The "whole-name" set is every word of the question, plural forms and split parts included. So "value" keeps `enums.py::VALUE` on Q6. I measured four rules on the eight questions. A rule on case alone keeps 7 `component` fixtures on Q2 and drops `Component`. An identifier rule alone keeps the fixtures `calendar` and `dtstart`. The identifier rule with the case kept gives `Calendar` on Q1 and Q5, `main` on Q8, and nothing else.
   Fix, recommended: keep a whole-name row only when the token looks like an identifier and its case matches. A token looks like an identifier when it has backticks, `_` or `.`, a capital after its first letter, or a capital first letter that does not start the sentence.

8. `tests/rota/test_f362_shape_s5.py:157-162`, CONFIRMED. `test_the_block_keeps_a_class_method_and_its_class` passes at `7e3d8848`, before the dotted split, and it checks only the class. No case pins the split.
   Fix: add a case where a dotted part that contains `_` names a grain and ranks first, for example `fold.fold_line`.

9. `rota/roles/api.py:5309`, CONFIRMED. Of the 1.48 s in one call, `_frame_ranked` takes 1.38 s. It runs `kind_of` on all 269 paths before the word match. This is not a wall: section 5 prices only seconds up front, and a consult turn costs model minutes.
   Fix: run the match first and rank only the hits. Both sorts are stable on the kind, so the order stays the same.

### Outside the points

10. `rota/roles/api.py:5251`, CONFIRMED by reading. The docstring says "The match is the match of `code.callables`". But `shape_of` adds the `_words_in` split, the dotted parts, the export grains and the command lead. So `code.callables(hint="from_ical")` falls back to 20 rows, and `model.shape("from_ical")` gives 72 hits.
    Fix: write in the docstring that the words are a superset of the words of `code.callables`, and name the additions.

11. `rota/onboarding/shape.py:64-86`, CONFIRMED. The row `parser/string.py::_foldline` has `exported` set to `parser/__init__.py` only. But `string.py:280` lists `_foldline` in its own `__all__`. The row `string.py::foldline` lists `string.py` because the indexer writes an export grain for an assignment and none for a function definition.
    Fix: make the first set of `exports` also read each file's own `__all__` names, or leave the defining file out of both.

12. `rota/roles/api.py:13475, 15442, 15927`, CONFIRMED by grep. Local variables and parameters named `shape_of` shadow the new module function in those scopes.
    Fix: rename the module function, or rename the locals.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/94cb1260-d91d-4109-aa38-7528925f5f83/scratchpad/rv5/`. They ran on `git archive` copies `old` (`623b3ada`), `mid` (`7e3d8848`) and `new` (`9c8ad879`) in that folder. `dry5.db` and `cassettes.db` were opened with `mode=ro`.

- `p1_rows.py`: `shape_of` for `Calendar`, `main`, `foldline` and `from_ical`. I checked the rows against the tree at `99619246` with `git show` and `git grep` in `icalendarI`.
- `p1b_db.py`: the `code_calls` rows from `cli.py`, the export grains of `string.py`, the `frame_rulings` table and the `entry_point` candidates.
- `p2_callables.py`: `code_callables` on `old` and `new` for three hints. Its outputs are `p2_old.json` and `p2_new.json`, and they are equal.
- `p3_rules.py`: the block, the hits lost past the cap, and four whole-name rules on the eight questions. With `--attach`, the probe sets `kind_of` to attached under the tests.
- `p3b_cases.py` and `p3c_split.py`: the dotted split and the script match on `mid` and `new`.
- `p4b_stale.py` and `p4c_stale.py`: the `system_hash` of each Architect ask system against `case_runs`. They find one case, `L1-AR-answer-a-question-read-only`, recorded for six models.
- A runtime probe in Bash: the Architect ask sandbox offers `model.shape`, and a call with no argument raises `ArgumentError`. So `push_working_set` skips the op (`runner.py:4407-4410`).
- pytest: `tests/rota/test_f362_shape_s5.py` gives 13 failed on `old`, 2 failed and 11 passed on `mid`, and 13 passed on `new`. `ROTA_DEV_DB` pointed to scratch files.
- `p7_cost.py` and `p7b_prof.py`: the time of `shape_of`, the size of the reply from `_render`, the count of whole rows in view, and a cProfile run.
- CR bytes: a count of byte 13 in each of the nine files at `9c8ad879` gives 0, and `git diff --check` is clean.

## (d) Usage

This agent cannot see a token counter, so the figures are estimates.

- Input: about 95k tokens of context, against the cap of about 50k. I went over the cap. The causes are the reads of the diff, the probe outputs and the repeated attempts to write the report.
- Output: about 18k tokens.
- Total: about 113k tokens.
