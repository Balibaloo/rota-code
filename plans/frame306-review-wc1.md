# Frame 306, W-C1 review: the pass check skips retired criteria

Worktree `C:/Users/roman/rota_r306wc1` at 0379fd43, on bc16c86d. Reviewer on Opus, read-only.

Verdict: Stands. The s415 shape passes. The pass door rejects a retired line, but the refusal text does not say why.

## (a) The points

1. Holds. A pass with one line for the live criterion is held once, then lands. The hold names no retired id.
2. Partly holds. Both checks add `_live_rows(ctx.conn, "c.retired_by")` (api.py 13735, 13969). The refusal text does not say why (finding 1).
3. Holds. With no retired criterion, the Critic and Tester pushes are byte-equal at bc16c86d and 0379fd43.
4. Holds for pass, review, tests and merge. The fail branch of `verdicts.emit` does not skip `retired_by` (finding 2).
5. Holds. 266 passed, 4 xfailed. The commit changes no existing test, so it weakens no assertion.

Point 4 readers:
- `_pass_lines_check` api.py 13733: skips retired (new).
- `_first_pass_hold` api.py 13967: skips retired (new).
- `_quotes_a_criterion` api.py 13897: reads the live `texts_of`, so it skips retired.
- `criteria_load` api.py 6770/6793: skips retired (pass 1c).
- `review` predicates.py 1369 and `tests_missing` 828: skip retired.
- `mergeable` lifecycle.py 816: skips retired in the untested count. The verdict read takes no criteria.
- `verdicts_emit` fail branch api.py 13316, `_must_exist`: does not skip retired.
- `_criteria_texts` api.py 16412 and `_batch_rows` lifecycle.py 608: no filter. They decide no pass, review or merge.

## (b) Findings

1. api.py 13748, `_pass_lines_check`. Medium. CONFIRMED. A line for retired `crit_2` gets "'crit_2' is not a criterion of batch bg_3. Its criteria are crit_1." The text is false: crit_2 is a criterion of the batch. It does not say that a ruling retired it. A seat that reads the page may send the line again. Fix: when the key is retired, name the ruling in the refusal. Reuse `retired_note`.
2. api.py 13316, `verdicts_emit` fail branch (outside the diff, existing). Medium. CONFIRMED. After `claim_encodes('crit_2', True)`, a fail on retired crit_2 lands: `{'result': 'fail'}`. The batch then goes back to the Developer for a criterion that `review` and `mergeable` ignore. Fix: refuse a `failed_criterion` that is retired, with the same retired text as finding 1.
3. runner.py 4208. Low. CONFIRMED by read. `push_working_set` imports `RETIRED_KEY` from api.py as a local name. runner.py 4080 has its own module `RETIRED_KEY` with a different meaning. A later use of the module name in this function raises `UnboundLocalError`. Fix: rename the api.py constant to `RETIRED_NOTE_KEY`.
4. api.py 6844, `retired_note`. Low. CONFIRMED. The Tester's push gets the note too. The note says "a pass or a review does not name them", which is Critic wording. Fix: say "no seat tests, passes or reviews them".

Not findings: `retired_note` returns "" on a database with no `retired_by` column (probed). An all-retired batch returns early from the door, which is correct.

## (c) Probes

All in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/79847ec6-3334-49c7-8221-098d6165a403/scratchpad/r306/`.
- `base/`: `git archive bc16c86d`, untarred. No worktree changed.
- `p3.py <root> <0|1>`: composes the Critic (review) and Tester (tests_missing) push on a two-criterion fixture and hashes the JSON. With 0: critic 2cbca532, tester a9fb8013 at both commits. With 1: only 0379fd43 adds `retired criteria`.
- `p2.py`: the refusal text for a retired line, a fail on retired crit_2 (lands), and `retired_note` on a database with no `retired_by` column ('').
- Pins: the nine files of point 5, `-p no:cacheprovider`, 266 passed, 4 xfailed.

## (d) Usage

About 48k input tokens and 7k output tokens, total about 55k (an estimate).

Stands.

## Re-check of 79391b21

All four findings are closed. The same p2 and p3 ran on the new code.
1. Closed. A retired line gets "crit_2 is retired by the principal's ruling r_m244. ... Send the pass again with lines= naming only crit_1."
2. Closed. A fail on retired crit_2 is refused three times, also after `claim_encodes(True)`. No verdict lands.
3. Closed. The key is now `RETIRED_NOTE_KEY`. No `RETIRED_KEY` remains in api.py or in the test.
4. Closed. The note now says "no seat tests, passes or reviews it".
- p3 with no retired criterion: critic 2cbca532, tester a9fb8013. These are the same bytes as at bc16c86d.
- The nine pin files: 267 passed, 4 xfailed. The changed test assertions are exact-equality checks now, so they are stronger, not weaker.
- New, low, PLAUSIBLE: when every criterion is retired, the fail refusal ends with an empty list, "bg_3: .". Fix: say that no criterion is live.

Stands.
