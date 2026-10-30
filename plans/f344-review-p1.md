# Frame 344, review 1 of commit b3d7c775 (branch critroot)

Verdict: NOT READY. The review has 2 high findings and 5 low findings.

## (a) Verdict on each point

1. kept route: NOT SOUND. The route checks only that the value is in a context line. A `def` header, a `}` line, a 12-character fragment and a line of Markdown prose all pass. A comment and a blank line are refused. A line that the change adds or removes is refused (finding 1).
2. test route: SOUND with one gap. The binding is `tests.criterion_id`, which `tests_encode` writes. A test with no criterion is refused. `latest_runs` keeps the newest run for each test, so a later failed run wins over an older pass. The route does not compare the run's commit with the head (finding 4).
3. _fail_tail: BROADER THAN NEEDED. The tail is needed on the missing-line refusal and on the not-an-added-line refusal only. The stale count under that placement is not measured (finding 5).
4. _review_pending_line: FAULTY. The line does not fire on a batch with no runs (probe p4). The line does fire when one test passed at the head and another test failed at an older commit (finding 2). The line reaches the Developer on `tick:exhausted` only. The 19 stale L1-DV cases do not come from `developer/exhausted.md` alone (finding 7).
5. verdicts.routes: SOUND. An old database with the schema mark opens, and `init_db` adds the column (probe p5).
6. New case: the diff holds `smtp.send_message(msg)` as a context line. The expected pass needs the kept route. A valid `test:` pass fails the case (finding 3).
7. Route words: no seeded code line starts with `kept:` or `test:`. The `kept: true` lines in `tests/rota/cases/sources/l3_rulings_judged.yaml` are case data. No batch diff holds them.
8. answer wake: YES. `critic/answer.tools` lists `verdicts.emit`, so the answer wake reaches `_pass_lines_check` (finding 6).

## (b) Findings

1. rota/roles/api.py:16863-16873 (`_route_fault`, kept branch). Severity high. CONFIRMED. Probe p1 passed `kept: def f(x):`, `kept: }` and `kept: 'a': 1,`. Probe p1b passed a line of README.md prose and the fragment `The send function`. The added route refuses a line of a file with no code (`_note_files`, frame 306). The kept route skips that check. With `function_context=True`, each hunk shows the whole function, so many unrelated kept lines are available. Fix: apply the `_note_files` code-file test and the whole-line match to a kept value, and refuse a header-only line.
2. rota/core/runner.py:456-479 (`_review_pending_line`). Severity high. CONFIRMED. In probe p4, test tA passed at head h2, and test tB last failed at commit h1. The line said "The tests of batch b1 pass at its head commit" and "Do not change the code". The query reads only the runs at the head, so a test with no run at the head is not counted. Fix: require that each live test of the batch has its latest run at the head and that the run passed.
3. tests/rota/cases/l1_judgement.yaml, case L1-CR-a-kept-behaviour-passes-by-its-kept-line, the `expect` block. Severity low. PLAUSIBLE. The fixture binds the passing test tst3 to c3, so `test: <tst3>` is a valid pass. That pass stores `test` in `routes`, and `text_includes: ['kept']` then fails. The case scores a correct verdict as red. Fix: accept the kept route or the test route for c3.
4. rota/roles/api.py:16893-16901 (`_route_fault`, test branch). Severity low. PLAUSIBLE. The route reads the newest run of the test and ignores its commit. When the head moves and the test is not run again, an older pass counts. The comment trusts the review tick, but finding 2 shows that a head check by run alone misses tests that did not run. Fix: require `run["commit_sha"]` to equal the batch's `head_commit`.
5. rota/roles/api.py, the `_fail_tail` call sites at 16961, 17066, 17094, 17134, 17151, 17173, 17184 and 17199. Severity low. PLAUSIBLE. The kept route helps when no added line meets the criterion. That cause is the missing-line refusal (16961) and the not-an-added-line refusal (17184). The other refusals reject a wrong added line, a block, a note line or the criterion's text. On those refusals, the tail invites a route change in place of a correct line. Fix: keep the tail on 16961 and 17184, and keep the old fail sentence elsewhere. Measure the stale set before a re-record.
6. rota/roles/prompts/critic/answer.md:20-21. Severity low. PLAUSIBLE. The text says that a pass names an added line for every criterion. The answer wake has `verdicts.emit`, so a Critic with a kept criterion gets one refusal before the tail teaches the routes. Fix: name the two routes in answer.md as review.md does.
7. The gate's 19 stale L1-DV cases. Severity low. PLAUSIBLE. `instructions_for` (rota/testkit/fixtures.py:1229) composes `base.md` and the case's mode file only. `developer/exhausted.md` reaches the mode `exhausted` cases only, and the case files hold about 5 of those. The other stale cases have a different cause, perhaps the system text or a set that was stale before this commit. Fix: name the cause of each stale L1-DV case before a re-record.

Outside the points: none above low. A fresh database puts `routes` before `version`, and a migrated database puts it after `version`. No reader by position was found.

## (c) Probes

All probes are in C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/68459b4f-6e2b-4299-b66e-6ca5ca44f7fd/scratchpad/f344.

- p1.py: `_added_walk` with a kept list, and `_route_fault` on 11 kept values against a synthetic Python diff.
- p1b.py: `_route_fault` on a kept line and a fragment of a README.md hunk.
- p4.py: a fresh `init_db` database, a batch at head h2, and `_review_pending_line` with no runs and with a split run state.
- p5.py: the parent's schema.sql with the schema mark, then `init_db` from the commit. The column `routes` was added.

No suite run. No tracked file was changed.

## (d) Usage

Input tokens: about 80k, an estimate. Output tokens: about 10k, an estimate. Total: about 90k, an estimate. The harness gives no exact count.

## p1b

Re-check of commit 23416479 on critroot, built on b3d7c775. Verdict: READY for the land. All 7 findings are closed. Six are closed on a probe or a diff, and one is closed on reading. Both questions answer yes. One low residual remains, and it does not block the land.

### Findings

1. Finding 1: CLOSED on probes p1c and p1d. `kept: def f(x):` gets the header refusal, and `kept: }` gets the brackets refusal (api.py:16893-16901). `kept: sorted(x)`, a fragment, is refused (api.py:16889). A prose line of README.md is refused when the worktree holds the file (`_code_context`, api.py:16813). `return sorted(x)` and `with open(x) as fh:` still pass.
2. Finding 2: CLOSED on probe p1c. When tB last failed at h1, `_review_pending_line` gives "" (runner.py:469-482). When both tests pass at h2, the line fires.
3. Finding 3: CLOSED on reading. The case now has two `any_of` branches, `kept:` and `test:` (l1_judgement.yaml, the case's `expect` block). `any_of` is read at rota/testkit/fixtures.py:685. No probe was run, because the brief forbids a live recording.
4. Finding 4: CLOSED on probe p1c. With the latest run of tA at h1 and the head at h2, the route gives "has no run at the head". With a run at h2, the route holds (api.py:16924-16928).
5. Finding 5: CLOSED on grep. `_fail_tail` has two call sites: api.py:16995 (missing line) and api.py:17221 (not an added line).
6. Finding 6: CLOSED on the diff. critic/answer.md:24-25 now names `kept:` and `test:`.
7. Finding 7: CLOSED on the builder's probe, not on mine. The builder replayed `test_l1.py -k L1-DV` at 020a241 and saw the same 14 ids stale (critic_loop_report2.md line 8). I did not repeat that replay, because it needs a new worktree.

Residual, low, CONFIRMED by p1c: `kept: d = {` passes. The line opens a bracket and does nothing. The brackets test (api.py:16898) does not catch it, because `d =` is not a bracket. Fix: refuse a kept line whose code ends in an open bracket. The fix does not block the land.

### Questions

1. Does the narrowed `_fail_tail` sit on the two refusals only? YES. Grep shows `_fail_tail(` at api.py:16995 and api.py:17221 only. The 6 other refusals carry the old sentence "If no added line meets ..." again.
2. Do the 29 reverted test texts match the parent's texts byte for byte? YES, at the line level. Probe q2 shows that each of the 21 lines that changed from b3d7c775 to 23416479 is in 020a241b without a change. Neither version holds a CR byte. The diff from 020a241b to 23416479 now holds only the `_routes` and `_fail_tail` helpers and their 6 call sites. Those are the kept route sentences.

### Probes of p1b

All probes are in C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/68459b4f-6e2b-4299-b66e-6ca5ca44f7fd/scratchpad/f344.

- p1c.py: 9 kept values against a Python hunk and a README.md hunk, then `_review_pending_line` and the test route on split runs. The worktree in that probe is NULL.
- p1d.py: the README.md prose line again, with a worktree that holds README.md.
- q2.py: the three versions of test_verdict_lines.py from git show, compared line by line as bytes.

The worktree C:/Users/roman/rota_crit has no change, by `git status`.

Usage for p1b: input about 45k, output about 6k, total about 51k. These numbers are estimates.

## p1c

Re-check of commits 319a4767 and e226cca3 on crit3root in C:/Users/roman/rota_crit3. Verdict: NOT READY for the land, on point 1 only. A split of one sentence fixes it.

The parent of 319a4767 is 370f0a05, not 64e4cfa8. 64e4cfa8 is 16 commits back. Both 64e4cfa8 and 370f0a05 are on rota/foundation (ee0bf392), by `git merge-base --is-ancestor`. So the land brings only the two commits. The diff in this section is 370f0a05 to e226cca3.

1. Point 1: PARTLY MET. The added line is first in step 1 (review.md:9-12). The added route is one sentence. The kept route and the test route share one sentence of about 47 words (review.md:15-18). That sentence breaks the point and the 25-word limit of STE. Fix: split it into a `kept:` sentence and a `test:` sentence.
2. Point 2: MET in the prompt. Step 1 admits `test:` only for "its own passing test that step 2 finds encodes it" (review.md:17-18). The prompt also says "A test that encodes nothing is a challenge in step 2, never a pass" (review.md:20-21). Step 2 asks the question of encoding (review.md:26). The door does not check encoding. `_route_fault` checks only the binding and a pass at the head, so the rule holds in the prompt only. PLAUSIBLE, low, no fix needed for this land.
3. Point 3: MET. `git diff --stat 370f0a05 e226cca3` lists rota/roles/prompts/critic/review.md only, 14 insertions and 12 deletions. From 64e4cfa8 to 370f0a05, review.md has no change. The worktree has no uncommitted change, by `git status`.

Probes: git diff, git log, git merge-base and grep only. No Python probe and no suite run.

Usage for p1c: input about 20k, output about 3k, total about 23k. These numbers are estimates.
