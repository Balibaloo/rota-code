# Frame 304, review 1 of eb7d11b0 and bc1fcda0

Verdict: does not stand as one fix. The arrange step is right for night 162. The NameError door still sends s351 the other way, and its fallback brings back a known bad text.

## (a) The points

1. The pick, over the record: the final rows hold no criterion with two surfaces, so the record cannot test the pick. Of 30 criteria with a surface, touch rows decide 25 and the one surface decides 5. None gets no surface. The two-surface rows lived only between respecifies, and night 161's b_4 touches both functions, so there the pick does not decide.
2. s351 and s364: s364 gets one way, "call `version_option`". s351 gets two ways in two turns. Body 1 gets the NameError shape 4 "add `from src.click.decorators import custom_version_option`". Body 2 then gets "call `version_option`". The two hints are never in one refusal.
3. `batch_id or ctx.batch_id`: `batch_id` is None when the Tester omits it, which is 398 of 869 encodes on nights 160 to 162. `ctx.batch_id` is None when the wake names no batch and not exactly one batch runs. The door then reads no touch rows, but `tests_encode` at 9522 still finds the batch through the criterion. No recorded encode has an explicit `batch_id` that differs from its criterion's batch.
4. The reach: the arrange predicate does not change. The NameError predicate changes for a criterion with two or more surfaces and no touched match. Existing tests: 82 passed. Gate: 6 failed, 0 new reds, 0 reds gone. No cassette holds an arrange refusal. The NameError cassettes name one surface, so no L1 case goes stale. The stale set is unreadable in the worktree because the register is absent.
5. The diff: hunk 1 changes the text of every arrange refusal, not only the signature case. Hunk 2 matches full refs where hunk 1 matches leaf names. The report states neither difference.

## (b) Findings

1. rota/roles/api.py:8401-8404 with `_unbound_name_hint` shape 4. Severity high. CONFIRMED. Probe P2 builds s351's first body with the night's two refs and a touch row on `version_option`. The refusal says "custom_version_option is defined in src.click.decorators of the project: add `from src.click.decorators import custom_version_option`". The next turn's arrange step says "call `version_option`". s351 still imports the wrong function first, then the door turns it back. Fix: when the unbound name is a criterion ref that the pick dropped, use shape 3a before shape 4.
2. rota/roles/api.py:8403-8404. Severity medium. CONFIRMED. Probe P4 uses two refs that no touch row names. The door now skips every shape and raises the plain text "import the function the criterion's surface names". The comment at 8386-8388 records that this text made Testers invent `ledger`, `app` and `create_account` five runs of five. Before this change, the door named the first ref. Fix: with no pick, name every ref of the criterion and let the Tester choose, or keep the old first-ref text.
3. rota/roles/api.py:8402. Severity medium. CONFIRMED. Probe P3 builds the sandbox with no wake batch and no `batch_id`. The door reads no touch rows and raises the plain text from finding 2, though the encode itself resolves the batch at 9522. Fix: resolve the batch the same way as line 9522, with `_batch_of_criterion(ctx, criterion_id)` as the third fallback.
4. rota/roles/api.py:16211-16219. Severity medium. CONFIRMED for the code and PLAUSIBLE for a night. Probe P5 adds a touch row on `custom_version_option`. Then `target` holds both names, and the step is the old "Call `custom_version_option` with `callback`" again. On night 161 the `batch_touch` rows of b_4 name both functions. Those rows come from the Architect's guess and annotate calls s251 and s270. Fix: when more than one surface is touched, prefer the surface that the item text or the ruling names, or name the line only.
5. rota/roles/api.py:16209-16211 against 8401-8404. Severity low. CONFIRMED. Hunk 1 matches the leaf after "::", and hunk 2 matches the full ref. Probe P5b shows that a touch row on `decorators.py::version_option` picks a criterion ref `core.py::version_option` in the arrange door. The NameError door rejects the same ref. Night 162's s353 respecified the criterion to `src/click/core.py::version_option`. Fix: use one helper for both doors, and match the full ref.
6. tests/rota/test_frame304_step.py, last test. Severity low. CONFIRMED by probe P2. The test asserts only what the refusal does not say. It passes while the refusal tells s351 to import `custom_version_option`. Fix: assert that the refusal names `version_option`, or that it does not tell the Tester to import `custom_version_option`.
7. rota/roles/api.py:16226-16233. Severity low. CONFIRMED by the diff. The "Fix line N" step for a criterion with one surface now names that surface. With no surface, the step prefixes "Line N raises `X`". These are text changes for every arrange refusal. No cassette holds that text yet, so no case renders them. Fix: state the scope in the commit body.

Outside the points:

8. The gate. Severity low. CONFIRMED. The gate printed "note: baseline stored at bc1fcda", but I did not pass `--baseline`. A review run can therefore move the baseline. Fix: confirm that the gate's auto-store on an absent baseline is meant for a review worktree.
9. The cause of the two surfaces. Severity low. PLAUSIBLE. On night 162, s326 respecified the criterion with `custom_version_option` in its refs, and the specify path stored both refs. Both doors now read the touch rows to correct a criterion error. Fix: refuse a respecify whose refs name a function that the item text does not name, as a separate frame.

## (c) Probes

- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/f1f0bcfa-7b93-4f01-99dc-afb4bf54e8a6/scratchpad/r4_p1.py reads the criteria and the `batch_touch` rows of nights 160 to 162. It counts the pick's outcome per criterion.
- r4_p1b.py in the same directory reads the refs of the specify and respecify calls. The args are cut at about 50 characters, so the turns gave the two-surface lists.
- r4probe/test_r4_probe.py in the same directory runs P2, P3, P4, P4 one-ref, P5 and P5b against the worktree's code with pytest `-s`. Result: 7 passed, with the texts quoted above.
- Inline queries read the `sessions` and `tool_calls` rows for point 3, and the `cassettes` table of D:/repos/rota/tests/rota/cassettes.db for point 4.
- The tests: test_frame304_step.py, test_frame304_arrange_door.py, test_frame304_arrange_raises.py and test_night46_context.py. Result: 82 passed.
- The gate in C:/Users/roman/rota_r304. Result: 6 failed, 4592 passed, 0 new reds, 0 reds gone, 362.5s.
- r4_p4.py ran too long on `case_runs`, so I stopped it. A shorter query replaced it.
- I put a copy of the probe in tests/rota by mistake. It was an untracked file, and I removed it before any run. `git status` is clean.

## (d) Usage

About 75k input tokens, about 12k output tokens, about 87k in total, by estimate. That is above the 30k cap.

Does not stand: the step is right, but the NameError door still sends s351 to `custom_version_option`, and its no-pick fallback brings back the frame 82 text.

## Re-check of 27e4c40e

Result: findings 1 to 6 are closed. One low residue stays open in the both-touched case. The worktree is at 27e4c40e and `git status` is clean. No gate ran.

### The texts each seat gets now

The criterion has the night's two refs. "One touched" is the night's row on `version_option`. "Both touched" adds a row on `custom_version_option`, as on night 161's b_4.

- s351, first body (NameError), one touched: "custom_version_option is not the criterion's surface. A test calls the criterion's surface src/click/decorators.py::version_option: add `from src.click.decorators import version_option`, call version_option in place of custom_version_option, and assert on what it returns."
- s351, first body, both touched: "Line 5 uses custom_version_option. Import or define custom_version_option before line 5, and send the encode again."
- s351, second body (arrange), one touched: "Line 6 raises `TypeError` before the call under test runs. The criterion's surface is `version_option`, so call `version_option` in the test and assert on its result."
- s351, second body, both touched: "Line 6 raises `TypeError` before the call under test runs. The criterion names the surfaces `custom_version_option` and `version_option`. Fix line 6 so that it runs."
- s364 (arrange, line 9), one touched: the same step as s351, at line 9, and it names `version_option`.
- s364, both touched: the same step as s351, at line 9, and it lists both surfaces.
- No wake batch and no `batch_id`: the NameError door finds b1 through the criterion and gives the shape 3a text above.

With one touched, s351's two refusals now point one way, to `version_option`.

### Per finding

1. Finding 1: closed. CONFIRMED. Shape 3a now runs before shape 4 for a dropped ref.
2. Finding 2: closed. CONFIRMED. With no pick, the door names the line and the name, and never the frame 82 text.
3. Finding 3: closed. CONFIRMED. `_surface_pick` resolves the batch as line 9522 does.
4. Finding 4: closed. CONFIRMED. With both touched, the arrange step no longer says "Call `custom_version_option` with `callback`".
5. Finding 5: closed as one helper. CONFIRMED. Both doors call `_surface_pick` and match the name after "::". The coordinator chose that match over the full ref. So a touch row on `decorators.py::version_option` still picks a ref `core.py::version_option`. That is a known and accepted over-match.
6. Finding 6: closed. CONFIRMED. The 1b test asserts the exact shape 3a text.
7. New, low, PLAUSIBLE: with both touched, s351's NameError text says "Import or define custom_version_option before line 5". That text sends the Tester back to the dropped function, and the arrange door then lists both surfaces. The text points no wrong way on its own, but it gives no direction. Fix: with no pick, list the criterion's surfaces in the NameError text as the arrange step does.

### Probes and tests

- r4_p1.py and r4_p1b.py read only the night databases, so the new commit cannot change their output. Re-run: the counts are as in point 1, with no criterion that keeps two surfaces.
- C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/f1f0bcfa-7b93-4f01-99dc-afb4bf54e8a6/scratchpad/r4probe/test_r4_recheck.py and test_r4_probe.py in the same directory: 16 passed, with the texts quoted above.
- The four test files: 85 passed in 19.07s.
- Usage of the re-check: about 15k input tokens and 4k output tokens, about 19k in total, by estimate.

Stands: with the night's touch rows, both doors now send s351 and s364 one way, to `version_option`, and the residue is low.
