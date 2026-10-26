# The closed frames of 2026-10-12 to 2026-10-14: how far each fix reached

Roman asked on 2026-10-26 at about 21:5x: "with all this knowledge, send another agent to review frames resolved in the last two weeks to see how much work should have been generalised". This record reads the 15 frames of `plans/archive/stack-2026-10-12.md`, `-13.md` and `-14.md`. It is read only, at head 9b33fa12 (code as at d1c934ae). Three agents on Opus ran the counts with `git grep` at each closing commit and at head. Their reports sit in session 8db3a3f9's transcript.

## The result

Of 15 frames, 2 fixed at the source, 10 fixed at one door of N, 0 rest on a wrong premise, and 3 are not this shape (observed: the table). The 10 door fixes covered a median of 1 of their reach. Five of them, 213, 225, 226, 227 and 221, sit at one fact: his ruling on a ref. That fact has about 20 separate readers at head (observed: agent 2, grep at d1c934ae). The frames cost 105 cycles by their closing lines. A fix at the source of each fact prices at about 79 by the anchors (reasoned: the last section).

| Frame | Closed | The fact | Reach then | Reach now | Later frames at the fact | Verdict |
|---|---|---|---|---|---|---|
| 210 | 10-12 | a test's latest run in its own batch | 6 of 18 | 24 readers, no helper, 3 order rules | 213, 306, 318, 330, 336 | at one door of 18 |
| 209 | 10-12 | the criterion of a test ref | 1 of about 13 | about 17 lookups, 3 partial helpers | 213, 316, 204 pass 3 | at one door of 13 |
| 207 | 10-13 | "passed before this batch"; a test is the batch's own | 4 of 4; 1 of 1 | one record, `project_tests_fact` | 335, 336 (neighbours) | at the source |
| 215 | 10-13 | where a criterion's surface may live | 1 of 4 (import offers 4 of 4) | `_surface_outside_batch` on 1 door; `code_callables` by fan-in | 202, 218, 295, 324 | at one door of 4 |
| 227 | 10-13 | his contested words on a criterion | with 226: 2 of 6 | as 226 | as 226 | at one door of 6 |
| 200 | 10-13 | none shared; a design of doors and briefs | 1 change at 1 of 4 | `_sent_this_session` 9 callers, 3 inline copies | 202, 223, 267, 308 | not this shape |
| 231 | 10-13 | none; a read | n/a | n/a | n/a | not this shape |
| 232 | 10-14 | the invented-result line | 3 of 3 | one regex in `toolproto.py` | none | at the source |
| 213 | 10-14 | his ruling on a test and on its criterion | 5 copies of 1 rule; the fact in 11 places | 7 copies; `FROM rulings` 13 to 23 | 238, 268, 308, 322, 337, 338 | at one door of 11 |
| 226 | 10-14 | his contested words on a criterion | readers 2 of 6; writers 3 of 3 | `last_ruling_on` 10 callers, 9 other readers | 243, 263, 283, 306, 308, 312, 315, 337 | at one door of 6 |
| 189 | 10-14 | which ref a ruling on a page line lands on | no fix; frame 190 fixed 2 of 2 copies | 1 predicate since frame 255 | 234, 255, 289, 299 | not this shape |
| 235 | 10-14 | the default model host | 4 of 6 | 6 copies, 2 toml copies still `localhost` | none | at one door of 6 |
| 225 | 10-14 | his verdict on an item against a note's contest | 1 of 3 | no one reader | 234, 238, 258, 268, 274, 316 | at one door of 3 |
| 221 | 10-14 | does a text carry his words; his newest ruling | 1 of 3 token checks, 5 word checks | 8 or more checks, no helper | 238, 263, 316, 322, 337, 339 | at one door of 5 |
| 198 | 10-14 | which request a ledger row belongs to | 0 of 2 | 2 rules; `ledger_items` since frame 316 | 241, 274, 316, 325 | at one door of 2 |

## The frames

**210.** The fix at a2b70a84 bound 6 readers of `test_runs` to the test's batch, and 12 others kept their own rule (observed: agent 1, grep `FROM test_runs` at a2b70a84). Three order rules exist: rowid, attempt with rowid, and attempt alone. `tests_failing`, `exhausted` and `_encode_nudge` stay unbound, and frame 213 added a fourth unbound reader, `_red_line_refusal`, one day later (observed: agent 1; `plans/frame333-agency-read.md` line 60). Frames 306, 318 and 330 met the same rows with new readers (observed: `plans/stack.md` 1331, 1600, 1794).

**209.** The fix guarded `reaches_request` and the callee `_items_reached` (observed: the diff of b170ba43). About 12 other places map a test ref to its criterion, each with its own None guard (observed: agent 1, grep `criterion_id FROM tests`). No other place crashed, so the review's "no other site" was true for the crash and not for the fact (reasoned). Frame 213 added `ruled_test_criteria`, and frame 316 added `ledger_items`, two more partial helpers (observed: agent 1).

**207.** The four "passed before this batch" sentences read one record, `project_tests_fact`, written once per batch start (observed: agent 1, runner.py 2910 and sandbox.py 1155, 1195, 1227 at f8ae0140). The filter decision has one reader, `_own` with `tester_paths` (observed: harness.py 69). Eight places still tell "own" from "project" by criterion presence for routing, which is a different use (reasoned). No later frame re-derives either fact.

**215.** `_surface_outside_batch` runs on `criteria_respecify` alone (observed: agent 3, api.py 4814 at 5ac87a07). `criteria_specify` keeps its own rule, `code_callables` still ranks by `fan_in DESC`, and night 142's wrong pick came from that list (observed: agent 3). The import offers share one probe, `_module_load_error`, 4 of 4, so that half is at the source (observed). Frames 202, 218, 295 and 324 met the surface again, and frame 324 names frame 215 as its own source (observed: `plans/frame324-agency-read.md` lines 7 and 51).

**227.** The fix is the `unchanged` branch of the same `last_ruling_on` read as frame 226 (observed: agent 2, api.py at 33cd99b2). Its reach and later frames are frame 226's. `criteria_respecify` reads two sources that can disagree, `_verdict_of` and `last_ruling_on` (observed: api.py 6911 and 6980 at head).

**200.** The five changes are a door text, a brief sentence, a reason slot, a stamp and one write-door rule (observed: agent 3, `plans/frame200-design.md`). Only the write-door rule has the shape: the change wrote two inline copies of "this session sent a challenge" beside the helper `_sent_this_session`, and three copies remain at head (observed: api.py 13799, 18404, 20449). The frame's residue went to frames 202 and 223, a criterion fact and a value that does not reach the Tester (observed: the close line). The 46 cycles are a seam design's cost and not a door repeated (reasoned).

**231.** A read of where a night's time goes, with no code fix (observed: the frame's Site line). It priced options and handed frame 232 its mechanism.

**232.** The fix moved the recogniser to one regex, `INVENTED_RESULT` in `toolproto.py`, and the stream, the runner and `nightcount.py` read it (observed: agent 1, toolproto.py 36). One possible gap: `nightreport.py` `COMMIT_RE` scans the raw completion, so an invented `OK code.commit` line can count as a commit (reasoned, not run). No later frame sits at the regex.

**213.** Five places map a ruled test to its criterion, each with its own query, and they read three ruling sources (observed: agent 2, the four diffs to 57c1a869). "His ruling on this ref" was derived in 11 places, and the answer-wake fix reused one, `chain_verdict` (observed). At head 7 copies of the test-to-criterion rule exist, and direct `FROM rulings` reads grew from 13 to 23 (observed: grep count). Frames 238, 268, 308 and 338 sit at the same fact, and frame 338 proposes `ruled_rows` for it (observed: `plans/frame338-agency-read.md` lines 19 to 20 and 52 to 55).

**226.** The writers were made one, `contested_texts`, 3 of 3 (observed: agent 2, 81ce21b7). The readers were not: 2 of 6 read `last_ruling_on`, and four paths still take his words from `entries` by a message chain (observed: runner.py 1696, 1759, 1876, 2098). `last_ruling_on` counts open rows and `chain_verdict` counts landed rows, and both rules stand at head (observed: principal.py 779). Eight later frames re-derive his words, from frame 243's `contests_on` to frame 337's `rulings.words` (observed: agent 2).

**189.** The frame built nothing. Frame 190's commit 2dace61b changed both copies of the batch-line rule, in `rulings_rule` and `land`, five hours after the push (observed: agent 3, `git log -S`). The frame then waited five days on Roman's order for a refusal that no longer fired in that form (reasoned). The head-commit residue was lost 16 of 16 times over nights 136 to 149 until frame 255 made one predicate, `built_line_faulted` (observed: `plans/archive/stack-2026-10-16.md` 133).

**235.** The script fixed four Python defaults (observed: agent 1). Two endpoints in `rota/llm/profiles/local-openai.toml` and `local-openai-native.toml` still say `http://localhost:11434/v1`, and the test reads the four Python lines alone (observed). One constant read by all six would have cost the same cycle (reasoned). No later frame exists, because no night uses those profiles (reasoned).

**225.** The fix narrowed the note fold, `about_ref not in ruled` (observed: agent 2, principal.py 1893 at 8754a8b5). Two filters in `land` still drop his explicit approve, and `problem_set_approval` takes an approval from the relay's config and not the landed ruling (observed: principal.py 1798, 1815; api.py 1458). Frames 234, 238, 258, 268, 274 and 316 met the same inferred verdict, and frame 274 is the same fold on a merged item (observed: `plans/archive/stack-2026-10-18.md` 88 to 90).

**221.** The fix wrote a third token rule, `_assert_words_fault`, beside the rule of `criteria_respecify` and the overlap rule of `problem_assert`'s observed branch (observed: agent 2, api.py at 6761443b). Pass 1c replaced frame 226's `last_ruling_on` with its own landed-only query, so the frame forked the one shared reader (observed: the diff of 6761443b). At head 8 or more word checks exist with no shared helper (observed). Frames 316, 322, 337 and 339 met the fact again, and frame 339 alone counts 11 phrase readers (observed: `plans/stack.md` 1266).

**198.** The frame closed on a ratio, 0 of 9 pages over three merges, with no commit (observed: the close line). The park its status line placed in `lifecycle.merge` did not exist at the close (observed: agent 3, grep `parked` at 9624565c finds nothing). Frame 316 built `ledger_items` and `park_merged` ten days later, and `off_page` keeps a second rule (observed: lifecycle.py 636, principal.py 982). Frames 241, 274 and 325 met the page's rows again (observed: `plans/stack.md` 1512, 2272).

## The counts

- At the source: 2, frames 207 and 232.
- At one door of N: 10, frames 210, 209, 215, 227, 213, 226, 235, 225, 221 and 198.
- Wrong premise: 0. Frame 198's close named a park that the code did not hold, and frame 189 waited on a refusal frame 190 had changed. Neither frame's cause was wrong at its push (reasoned).
- Not this shape: 3, frames 200, 231 and 189.

## The cycles

The cycles spent, by the closing status lines: 210 2, 209 2, 207 2, 215 10, 227 2, 200 46, 231 4, 232 4, 213 10, 226 5, 189 0, 235 1, 225 10, 221 7, 198 0. The sum is 105 (observed: the lines). Frame 226's close says 5, and its last running count says 10 of 7, so the sum is 110 by the running counts. The ten door frames spent 49 of the 105.

A fix at the source, by the anchors of `plans/operating-facts.md` (a door text 2, an instrument fix 3, a seam design with its night 8 to 10, a count that closes on a night 0):

- 210: one latest-run reader for 18, an instrument fix, 3.
- 209: one test-to-criterion reader for 13, 3.
- 215: one record of where a surface may live, 3, the price frame 324 gives `areas.kind_of`.
- 213, 225, 226, 227 and 221: one record of his ruling per ref, a seam design, 10, near group 2's 9 to 10 in `plans/agency-groups-2026-10-26.md`.
- 235: one constant, 1.
- 198: one reader of a page's rows by request, 3, the shape frame 316 built.
- 207, 232, 200, 231 and 189 keep their 56.

That sums to about 79 against 105, and about 23 against 49 for the ten door frames (reasoned: the anchors). The saving is larger than the sum shows, because each later frame in the table spent its own cycles at a fact a source fix would have closed (reasoned: those cycles sit in later archives and are not summed here).
