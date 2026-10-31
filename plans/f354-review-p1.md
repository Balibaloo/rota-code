# Review of frame 354, commit 7e553500 on rota/foundation, pass 1

Verdict: the change works, but one group failure loses every file of the group, and pass 2 must fix that before close. Counts: 2 high, 3 low.

Worktree: C:/Users/roman/rota_f354r at 7e553500. The review did not remove the worktree. The review did not call the model and did not run the gate.

## (a) Verdicts on the points

1. The strings match. The runner sets `ctx.area` to `wake.refs[0]` for an onboarding tick (runner.py 4933). `surveys.attest` writes `area` from the group, and the group is the `@prose` refs of the wake. On f354.db the refs and the 34 `area` values are the same `@prose` and `@prose:docs/<path>` strings. Seven other wake kinds write `survey_records` through `surveys.attest`: `tick:frame`, `tick:orient`, `tick:survey`, `tick:define`, `tick:reorient`, `tick:boundary` and `tick:blindspot`. `_derive_frame_record` also writes the table, after the loop. For each kind other than `tick:reconcile`, `closed` is non-empty after any write, so the old end rule holds. A reconcile attest cannot land a row outside the refs, because `_group_targets` picks only from the group. A refused attest writes nothing, so a seat that only names files outside the group runs to the turn cap. A group of one closes on any citation, as before.
2. The cause is the seat. In s10, the pushed `code.prose` held all four files under their headers. The turn 1 prompt was 16,617 characters, with no cut marker. The runner did not cut the text at `PUSH_CHARS`, and all four headers stay in every turn. In each of turns 2 to 12, the seat called one `code.source` on one of the four pushed files, then wrote its own result "OK code.source ->". The stream stopped there each time. It cycled the four files three times and never named `surveys.attest`. The last row is the runner's account: ten lines of "wrote its own tool results". s11 and s12 show the same pattern, with 9 invented results each.
3. The 26 refusals are three reasons. The same-words guard refused 9 (s5 4, s9 4, s19 1). The restated-row guard refused 12 (s17 1, s19 3, s20 4, s23 4). The `about_ref='about_ref=@prose'` error refused 5, all in s19, not 1. Example, s20 seq 17: `about_ref='defines_commands_and_options'`, note "the README says Users define commands and options using decorators in Python functions, which Click then uses to parse and execute command-line inputs.; the code shows import typing as t; import click; ...". The README side is the item's own text, word for word, and the code side is a source dump. The guard was right. At 7e553500, neither guard refuses any of the 7 dry1 conflicts. Four of the 7 hold only "the README is stale; the code has a bug", and two describe a file and name no difference. The guard removed only noise in this run. The run gives no evidence that the group lowered the finding rate, because neither run holds a real conflict.
4. The cap does not grow with the group. `run_session` takes `max_iterations=MAX_ITERATIONS`, 12 (runner.py 45), and `ROTA_MAX_ITERATIONS` is the only override. s4 (README and advanced.md, 17,862 characters in turn 1, no cut) read README once and advanced.md twice. Then it called `code.probe` on the four account items in turns 6 to 12, with 8 invented results, and never attested. s16 (options.md alone) got the old 6,000-character cut, "first 6000 of 25663 characters". It paged the file with `code.source` and probed the items. Its last turn was cut at the output budget, and it ended after 11 turns. s17 then closed options.md.

Outside: no hunk falls outside the claim, except the runner hunk that the pass report names and the scheduler rule that a quarantined group abandons all its files (finding 1). The test `test_reconcile_groups_the_open_prose_by_size` passes with `-n0`. The 6 reconcile tests of test_onboarding_phases.py passed in 80.8 s.

## (b) Findings

1. rota/core/scheduler.py 798, high, CONFIRMED. A quarantined group abandons every file it held. On f354.db, `tick_attempts` holds one quarantined key with 4 refs, 3 attempts. The 4 files have no row. The one-file wake lost a file only after 3 failures on that file. A group that one hard file breaks now loses its neighbours, and the group key changes when a file closes, so the bound no longer counts per file. Fix: when a group of more than one file hits the bound, wake its files as groups of one, and abandon only a quarantined group of one.
2. rota/core/runner.py 45 with rota/roles/api.py 4999, high, PLAUSIBLE. Invented tool results rose from 10 of 148 reconcile turns on dry1 to 63 of 145 on f354.db. Each invented result stops the stream, so the seat makes one call per turn. A group needs one attest per file inside the same 12 turns. The rate does not follow prompt length: s14 (17,716 characters) closed 4 files in 2 turns. So the probe cannot say whether the group text or the brief causes the rise. Fix: measure the rate per session against the brief and the group size in pass 2, then scale the cap with the group or shrink the budget.
3. f354_pass1_report.md, part (b) 3, low, CONFIRMED. The report names one `about_ref='about_ref=@prose'` error. s19 made 5 such calls, and two were notes about setuptools.md and shell-completion.md. Fix: correct the count in the pass 2 report.
4. rota/roles/api.py 15602, low, PLAUSIBLE. The `about_ref` refusal tells a seat to "use the @-prefixed area name". In a group, the seat does not see which area name a file has. s19 wrote `about_ref="about_ref=@prose"` with `about_table="docs/shell-completion.md"`, and that note names a real difference, "Bash (version 4.4 and up)". Fix: in a reconcile group, the refusal lists the wake's area ids, `@prose:docs/<path>`.
5. Outside. rota/roles/api.py 4955, low, PLAUSIBLE. One attest that cites several files stamps one outcome on every target and writes all its citations under each row. A `found` from file A marks file B `found`. No row in f354.db shows this, because all 34 rows are `none_found`. Fix: give `found` only to the files that the session's ledger rows since the last attest name in `about_table`.

## (c) Probes

All probes ran from C:/Users/roman/rota_f354r with the venv Python. Each probe was a read-only query or a unit test.

- `git show 7e553500` for the five files, and reads of runner.py 4925-4940, 5225-5240 and 6240-6275, and api.py 4560-4580 and 15630-15790.
- `rota.tools.map fn surveys_attest` and `map table survey_records` for the writers. A grep of `rota/roles/prompts` for `.tools` files that hold `surveys.attest`.
- f354.db: `sessions.wake_refs` and turn counts for the 19 reconcile sessions, `tick_attempts` for the quarantined key, `survey_records` areas and outcomes.
- f354.db: `tool_calls` and `turns` of s10, s11, s12, s4 and s16, with prompt length, file headers, cut markers and completion heads per turn, and the last account row.
- f354.db: `ledger.log` calls per session from `tool_calls`, the call text from completions, and the refusal lines from the next prompt or the account row.
- dry1.db: the 7 `conflict` rows of `ledger` and their `default_taken` text. The probe ran `api._misplaced_conflict` and the same-words test of `ledger_log` at 7e553500 on each one, against a read-only dry1.db connection.
- Both databases: the count of reconcile turns whose completion holds an invented "OK " result line, and the count per session against the length of the turn 1 prompt.
- `pytest tests/rota/test_onboarding_phases.py -q -n0 -k reconcile`: 6 passed, 86 deselected, 80.8 s.

## (d) Usage

About 50k input tokens of context, about 9k output tokens, about 59k in total. The cap was 40k, and the review went over it.
