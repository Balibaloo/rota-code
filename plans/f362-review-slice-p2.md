# Frame 362, slice pass 2: review of `7bd7f78b`

Verdict: fix. The pass does what its report says, and the touched tests are green (39 passed). No finding is high. Five findings are medium. Two of them are on the tie key, and pass 3 builds on that key. Fix findings 1, 2 and 5 before pass 3. Give findings 3 and 4 to pass 3 as rules.

Worktree `C:/Users/roman/rota_r362s` at `7bd7f78b`, parent `9b8447cd`. The icalendar root is `D:/tmp/rota-live/icalendar` at `99619246`.

## (a) Verdicts by point

1. One writer per record: CONFIRMED. `harvest.record` writes only `commitment_candidates` and `candidate_bindings`. The door writes only `constraints`, `constraint_bindings` and `refs`.
2. The tie key: CONFIRMED with defects. A shift keeps the tie. An edit or a move breaks the tie silently. `witnessed` then returns a stale row (findings 1 and 2).
3. The push: CONFIRMED. 31 of 64 candidates are shown in 5,823 characters. The rank order holds, and the cut line counts 33. 22 of the 31 shown lines come from docs files (finding 4).
4. The door: CONFIRMED. The refusal shows the form, and a statement lands with the placed bindings only. A project-wide-only candidate is refused on a survey wake, and lands global with no area (finding 6).
5. The falsified rule: CONFIRMED for the Architect's push. `bound_constraints` does not read the rule, so pass 3 needs its own exclusion (finding 3).
6. Stale cases: CONFIRMED. Six Architect `survey` cases go stale, with ten runs in total. The gate re-records them by itself, unless the main card is held.
7. The runner change: CONFIRMED. The change deletes only a None from `model.witnesses`. No other push changes, and no seat relied on the new line.
8. The seat's view: PLAUSIBLE, with defects. The push gives the id, and a small model can state one line in one call. The brief contradicts itself on when the seat is done, and the headline asks for a symbol the push does not give (finding 5).

Detail by point:

- Point 1. The harvest trace ran with a SQLite authorizer on a fresh icalendar database. The writes were INSERT and UPDATE on `commitment_candidates` (columns `commit_sha`, `contradicts`, `detail`), and INSERT and DELETE on `candidate_bindings`. The `constraints` row count and the party count did not change. The door trace applied one statement. It wrote `constraints`, `constraint_bindings` and `refs`, and the candidate count stayed at 185. The map shows one more writer of `constraints`, `boot.refresh_constraint_zero`. That writer names only `id, headline, text, is_global`, so it never touches the three columns.
- Point 2. The key is `kind|path|text`.
  - A shift of three lines: the new candidate (line 10) shows "Constraint src_pkg_fold_py_fold states it already". The tie holds.
  - An edit of the witness line: the push shows the new candidate with no mark. The constraint keeps its party, its behaviour, the old key and the old binding. Nothing marks the broken tie. The failure is silent.
  - A move to `src/pkg/other.py`: the result is the same, and the constraint still binds the old file `src/pkg/fold.py`.
  - `witnessed(key)` returns the stale line-10 row of commit `c2` after the shift back, the edit and the move.
- Point 3. The area `src/icalendar/parser` holds 64 bound candidates: 34 `standard`, 17 `project_wide`, 9 `witness_file`, 3 `symbol` and 1 `exports`. The push shows 31 of them (9 `witness_file`, 22 `standard`) in 5,823 characters, under the limit of 6,000 less 200. The cut line reads "33 more candidates were cut to fit this push. The cut takes the project-wide candidates first." All 17 `project_wide` rows are cut, and the rank order of the shown rows is monotonic. Every shown candidate binds a file of the area. No candidate is bound only to another area. But 22 of the 31 witness lines lie in `README.rst`, `docs/how-to`, `docs/explanation` and `docs/contribute/documentation`. The user prompt is 15,560 characters, and the block is about 37% of it.
- Point 4. The refusal for no witness gives the full form with a real id and 31 shown ids, capped at 8 with "and 23 more". A cut id is refused with "is not a candidate that [model.witnesses] showed". The 75-octets statement (`cc_e5f3f831b415`) landed with these values:
  - `party`, `behaviour` and `witness = wk_99502ef494ad`;
  - `is_global = 0`;
  - one binding, `src/icalendar/parser/string.py`;
  - one `grain` ref.
- Point 4, continued. The rule matches section 7, "copied from the candidate's placed bindings", with two departures. First, a seat binding replaces the placed bindings instead of joining them (finding 7). Second, a `standard` candidate copies 49 bindings over 8 areas (finding 4). No icalendar candidate mixes `project_wide` with a placed rule, and 17 are `project_wide` only. On a survey wake the door refuses such a statement with the generic survey-binding text. So no stated constraint lands with no binding there. With no area, the statement lands `is_global = 1` with no binding, and `_reaching_constraints` then reaches every diff. So the brief's fear is reversed: such a row is pushed everywhere, not nowhere (finding 6).
- Point 5. A `falsified` row in `challenges` for `constraints:<id>` takes `cc_e5f3f831b415` out of `area_witnesses`. `_reaching_constraints(["src/icalendar/parser/string.py"])` still returns the falsified constraint. `bound_constraints` reads only `_reaching_constraints`, so the Developer, the Tester and the Critic would get the falsified commitment.
- Point 6. The six cases are `L1-AR-survey-an-area-for-its-commitments` in `l1_survey.yaml` (5 runs), and five spike cases in `l1_survey_spike.yaml` (1 run each). The prompt changes for all six, because `survey.tools` is in the system prompt. `rota/tools/gate.py` lines 6 to 11 say that a stale case is re-recorded after the run, one case at a time. When a model is loaded on the main card, the re-records wait and the run exits 3. In that case, `--rerecord-now` re-records them. A separate command is not necessary.
- Point 7. `push_working_set` (`rota/core/runner.py` 4370 to 4380) keeps every other None result as before, because the guard names `model.witnesses` only. Only `survey.tools` lists `model.witnesses`, so no other mode calls the read.
- Point 8. Each push line gives the id, the path, the line and the quote. The brief line gives the three keyword names. That is enough for one `model.amend` call per line. Three parts ask for more than the seat has:
  - Line 36 says "you are finished" after the none_found attest, before the witnesses paragraph at line 45.
  - Line 38 asks for a `path::symbol` headline, and the push does not print the candidate's `symbol`. A doc-claim witness from `docs/how-to/usage.rst` has no symbol in the area.
  - Line 41 says that `bindings` must be paths "you must have opened". The door copies the placed bindings for a statement, and the brief does not say so.
- Point 8, continued. The tokens `rule witness_file` and `rule standard` are jargon that the seat cannot act on.

## (b) Findings

1. `rota/roles/api.py` 3802 to 3846, `rota/onboarding/harvest.py` 100 to 110. Medium. CONFIRMED (`p_tie.py`). An edit or a move of the witness line breaks the tie with no mark. The stated constraint keeps its party, its behaviour and its binding to the old file. The push offers the new line as unstated. Under ruling 3, the stale row can still stop a merge on a promise text that no longer exists. Fix: in `area_witnesses`, list each stated key with no current bound candidate as "Constraint X lost its witness line", so the survey re-states or retires it.
2. `rota/onboarding/harvest.py` 113 to 123. Medium. CONFIRMED (`p_tie.py`, c3 to c6). `witnessed` orders by `rowid DESC`, and it filters neither on the latest `commit_sha` nor on a binding. An upsert keeps the old rowid. So after a shift back, an edit or a move, the function returns the stale line-10 row of commit `c2`. No production code calls the function yet. The pass-3 push of "the witness line" would show that stale line. Fix: select only rows of the latest harvest commit, or rows with a `candidate_bindings` row, then order by line.
3. `rota/roles/api.py` 4386 to 4450. Medium. CONFIRMED (`p_door.py`, step 6). The `falsified` exclusion lives only in `area_witnesses`. `_reaching_constraints` and `bound_constraints` still return a falsified stated commitment. Under ruling 3, that row could stop a merge. Fix: put the falsified rule in one shared predicate, and have `area_witnesses`, `bound_constraints` and the pass-3 reader all call it.
4. `rota/roles/api.py` 3790 and 4228. Medium. CONFIRMED (`p_push.py`, `p_door.py` step 4). The rank puts `standard` second, so 22 of 31 shown lines in `src/icalendar/parser` are RFC citations from docs files. A statement of one of them, `cc_5da27298830a`, copies 49 bindings over 8 areas. That row then reaches most diffs, which is the over-push risk in section 8 of the dive. Fix: rank a `standard` row whose witness lies outside the area below `symbol` and `exports`, and copy only the placed bindings inside the surveyed area.
5. `rota/roles/prompts/architect/survey.md` 33 to 45. Medium. PLAUSIBLE. Line 36 says the seat is finished at `none_found`, so a seat with witnesses and no counterfactual can stop before line 45. Line 38 asks for a `path::symbol` headline that the push does not give for a witness. Fix: move the witnesses paragraph before the none_found branch, and print the candidate's `symbol` or a headline form in each push line.
6. `rota/roles/api.py` 3917 and 3938, and 4228 to 4232. Low. CONFIRMED (`p_noarea.py`). With no area, the door accepts any candidate on file. A project-wide-only statement then lands `is_global = 1` with no binding, and it reaches every diff. Six Architect modes other than survey list `model.amend`. Fix: refuse a `witness` when `ctx.area` is empty, because only the survey push shows the ids.
7. `rota/roles/api.py` 4228. Low. CONFIRMED by reading. When the seat sends its own `bindings`, the door drops the candidate's placed bindings. Section 7 says the bindings are copied from the candidate. Fix: join the placed bindings to the seat's bindings, as a set.
8. Outside the points. `rota/roles/api.py` 4074 to 4077. Low. CONFIRMED (`python -c` on `_INSIDE_PARTY`). Any party that the inside regex misses counts as outside. "other areas of this repository", "the parser" and "nobody" all pass. Ruling 3 makes an outside commitment a merge stop, so an inside party gets that weight. Fix: require the party to match the outside-word regex, or to name a program, a user or a standard.
9. Outside the points. `rota/roles/api.py` 3870 to 3874. Low. CONFIRMED (`p_push.py`). `_quoted` wraps a line that starts with triple quotes in four quote marks, as in the push line of `content_line.py` line 285. Fix: strip the leading and trailing quote marks of the copied text before the wrap.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/535a30c6-b4f1-4ae7-85bc-11d741145722/scratchpad/r362p2/`, with the worktree root first on `sys.path`.

- `p_build.py`: runs `boot.onboard` on icalendar and clears the candidate tables. Then it runs `harvest.record` under a SQLite authorizer and prints the tables and columns written. The output is `ical.db`, with 185 candidates written.
- `p_push.py`: on a copy of `ical.db`, builds a survey wake for `src/icalendar/parser`, then calls `push_working_set` and `build_prompt`. It counts the candidates, the characters, the rules shown and cut, the rank order and the witness paths outside the area.
- `p_door.py`: on a copy of `ical.db`, sends `model.amend` with no witness and with a cut id. Then it sends the 75-octets statement, a `standard` doc claim and a project-wide-only candidate in `src/icalendar/prop/recur`. It applies the writes under an authorizer, and then inserts a `falsified` challenge.
- `p_noarea.py`: sends a project-wide-only statement with `ctx.area` set to None, and prints `is_global` and the binding count.
- `p_tie.py`: a small tree in a temporary directory under `r362p2/`. It states the fold line, then harvests five more commits: a shift by three lines, a shift back, an edit, a restore and a move. For each commit, it prints the push rows, `witnessed(key)` and the constraint bindings.
- A one-line Python call on `api._INSIDE_PARTY` with six parties.
- The suite: `ROTA_MODEL=qwen3:8b python -m pytest tests/rota/test_f362_commitments.py tests/rota/test_map.py -q` printed 39 passed in 13.12 s. The gate did not run, because no point needed it.

## (d) Usage

- Input tokens: about 65k as context, all turns together. The harness gives no exact count.
- Output tokens: about 14k.
- Total: about 79k.
- Sub-agents: none.

## Pass 2b

Verdict: fix. Commit `935aa904` is on top of `7bd7f78b`. I did not move the worktree, because my rules forbid a git command that changes a tree. I read the commit with `git diff` and probed a `git archive` copy at `scratchpad/r362p2b/`. The probe is `scratchpad/r362p2/p2b_tie.py`.

- Medium 1, fixed in part. CONFIRMED. After an edit, the push shows "Constraint src_pkg_fold_py_line_7 lost its witness line" with a restate form. After a move with the index rebuilt, `lost_witnesses` shows nothing, because the old file left `code_index`, and the area match then fails. Fix: list a lost constraint whose bindings no longer resolve in any area, or match on the witness path of the stale candidate.
- Medium 2, fixed. CONFIRMED. `witnessed` reads only the latest harvest commit. It returns line 10 after the shift, line 7 after the shift back, and None after the edit and after the move.
- Medium 5, fixed in part. The witnesses paragraph now comes at line 28, before the none_found branch, and it says "Do these lines first". Line 40 still says that a headline is `path::symbol`, and line 44 still asks for bindings "you must have opened". Fix: in lines 40 and 44, add "except a witness line, which takes `<path> line <n>` and needs no bindings".
- Point 8, fixed in part. The headline form `<path> line <n>` uses only what the push prints, and the door accepts that form. The constraint id then holds a line number, so after a shift the id and the headline name a stale line. Fix: leave the line out of the headline form, and use `<path>` and the first words of the quote.
- Deviation, fix. CONFIRMED. The edit made the old constraint lose its witness. The seat then stated the new line as `src/pkg/fold.py line 7 octets` and did not restate the old row. Both rows landed, with one subject stated twice. Before the deviation, the duplicate-subject check refused that pair, because the two headlines share their path words. Fix: skip the check only when the other row's witness key is still current, so a row that lost its witness keeps its subject.
