# Frame 362, review of `36a2edd2`: a contested record stays owed until its owner rewrites it, 2026-11-06

## Result

**Verdict: sound for the measured case, with gaps. Merge after findings 1 and 2 are decided.** The fact holds on every recorded contest. Only the three b_1 starts of dry run 6b change. Seven of the 20 tests cannot fail at the parent. Six new branches have no test that fails when the branch is removed. Two defects can start a batch on a set he contested, or hold a batch that was already rewritten. No model was called. No tracked file was edited.

## (a) The verdict on each point

1. Confirmed. m27 is owed at s143, s150, s152, s155 and s156. r_m39 replaces it at s165, and r_m41 replaces r_m39 at s167. s171 does not discharge it, and s172 does. Nothing is owed after a rewrite on dry 4, dry 5 or night 166. Nothing is owed on dry 3 or dry 6a.
2. Confirmed. Only b_1 of dry 6b changes, at s152, s155 and s156. The other 12 recorded starts are equal at the parent and the commit. The night 166 starts cannot run `next_batch` on the old schema. `owed` is None at each of them, so the new filter cannot change them.
3. Seven tests pass at the parent with stubs, so they cannot fail for their own reason. Finding 3 names them.
4. The worst case is 1 relay, 3 `tick:guess` sessions, 1 quarantine report and 1 park ask per batch. The quarantined key `architect|tick:guess|<item>,<verdict>` ends it. The page is mostly true and names a way out. A reply through that way out lifts the park in the code, but no test lands that reply.
5. A run opens through `init_db` and migrates. `connect` does not migrate (finding 8). A migrated old database re-owes a batch-line contest that was already rewritten (finding 2). A `batches_judge_touch` write stamps the empty string and discharges nothing. No reader of the column breaks on it.
6. `code_target` and `code_line` still show the contested set with no mark, on the sign-off page and on the new park page. `touch_set`, `predicted_rows` and `first_touch_rows` still seed a running batch whose line he contests. No pending batch can start on an owed set.
7. The changed brief line adds: "When it holds the principals words and no paths, he called the set wrong: write the files his words name." (quoted without its apostrophe). The new `tick:annotate` wake is bounded by its key, 3 attempts, then the park. No test covers it (finding 4). Three annotate cases go stale on the brief line: `L1-AR-annotate-a-batch`, `L1-AR-annotate-from-the-guess` and `L1-AR-re-annotate-from-the-principals-correction`. The third also gets a new seed (finding 6).
8. Not the measured case. On dry 6b the batch was annotated at s150, after the contest at s143. The cost is one start on the old batch set, the same wall as dry 6b (finding 7).

## (b) Findings

1. `rota/core/scheduler.py` 1908 to 1915. Severity high. PLAUSIBLE. The newest landed ruling that names the guess line or a batch of the item replaces an owed contest, also when it only approves the batch line. The dry 6b ruling r_m54 holds `"b_1": "approve"` from page m53, so such rows land (probe: `look.py`). A page with the batch in its rows, answered "ok" while the guess contest is owed, ends the hold with no rewrite. The batch then starts on the contested set. Fix: let only a contest or a revise replace an owed ruling, or let an approve replace it only on a page that showed the code line.
2. `rota/core/db.py` 498 to 502. Severity low. CONFIRMED. The migration gives every old `batch_touch` row the empty stamp. On a migrated copy of dry 6b in the s173 shape, `owed("b_1")` gives r_m41, and `next_batch` gives `[]`. So the recorded s172 rewrite under m44 counts for nothing. A resumed night wakes the Architect again, and it can park with a page that says the team wrote nothing. Fix: backfill `ruling_id` from the receipts of a session that the relay of a verdict woke.
3. `tests/rota/test_frame362_owed_contest.py`. Severity low. CONFIRMED. With `owed`, `owed_key` and `owed_park` as stubs and the column added, 13 tests fail and 7 pass at the parent (probe: `parent/`). The 7 are `test_a_set_that_carries_the_verdict_discharges_it`, `test_a_stamped_batch_set_discharges_it`, `test_the_relay_write_carries_the_verdict`, `test_the_tick_write_carries_the_verdict`, `test_a_plain_tick_write_carries_no_verdict`, `test_the_door_admits_the_same_set_under_a_revise` and `test_the_guess_tick_waits_behind_an_open_relay`. `test_the_tick_write_carries_the_verdict` asserts only `owed is None` and never reads the stamp. Fix: assert the `ruling_id` value in each stamp test, and a positive result beside each `None` or `[]`.
4. `rota/core/predicates.py` 1064 to 1077, `rota/core/scheduler.py` 1917, 2168 and 2920, `rota/roles/api.py` 9126. Severity low. CONFIRMED. Six mutations leave the 20 tests green (probe: `mutate.py`). They remove the batch-line `tick:annotate` wake, its `owed_in_flight` wait, the door in `batches_annotate`, the merged guard in `owed`, the `given_up` addition and the `close_stale_park_asks` change. The batch-line wake is deviation 3, new behaviour with no test. Fix: add one test per branch, the batch-line wake and its park first.
5. `rota/roles/principal.py` 2606 to 2634, `rota/core/predicates.py` 2083. Severity low. PLAUSIBLE. The owed key is per item, and `park_ask` asks per batch. So an item with two pending batches gets two park pages for one owed write. The page also shows the contested set on line 2 as the team guess. It asks him to name the files again, and on dry 6b he named them already. Fix: ask once per owed key, and show his named files on line 2.
6. `rota/core/runner.py` 4317 to 4325. Severity low. PLAUSIBLE. `_guess_seed` drops the whole item guess under any owed ruling, also under a batch-line contest. Then his batch-line words arrive with no guess, but he did not contest the guess. The case `L1-AR-re-annotate-from-the-principals-correction` seeds that shape. Fix: drop the guess paths only when the owed line is `guess`.
7. `rota/core/scheduler.py` 1919 to 1922 and `rota/core/predicates.py` 1081 to 1083. Severity low. PLAUSIBLE. This is fault 1 of the build report. A batch annotated before a guess contest keeps its old rows. A stamped guess rewrite discharges the fact, and `annotate` does not fire on a batch with rows. The reach on the records is 0 of 6 guess contests, because each batch was annotated after its contest (probe: `replay.py`). Fix: a stamped guess rewrite clears the touch rows of the pending batches of the item, so `annotate` runs again.
8. Outside the brief. `rota/core/db.py` 139 to 151. Severity low. CONFIRMED. `connect` adds no `ruling_id` column, but it adds the other late columns. On an unmigrated night copy an insert with `ruling_id` fails with "table batch_touch has no column named ruling_id" (probe: `mig.py`). `owed` is guarded and gives None there. Only `cmd_run` migrates, so a writer on another path fails. Fix: add the column in `connect`, as `commitment_columns` does.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/029756dd-9273-4a54-95d8-2da05a2bfe52/scratchpad/ro362/`.

- `parent/`: a `git archive` of `f29d1352`, with stub `owed`, `owed_key` and `owed_park`, and the column in `schema.sql`. It ran the 20 new tests: 13 failed, 7 passed.
- `head/` and `mutate.py`: a `git archive` of `36a2edd2`, 11 mutations of one branch each, and the 20 tests per mutation. Six mutations stayed green.
- `replay.py`, `replay_head.out`, `replay_parent.out`: the state of dry 3, dry 4, dry 5, dry 6a, dry 6b and night 166 at each session that landed a ruling, wrote a touch row or started a batch. The script rebuilds the rows from `receipts` and stamps a relay rewrite with its verdict. It calls `owed`, and `next_batch` at each start, at the parent and at the commit. Each database opens with `immutable=1` or `mode=ro` into an in-memory copy.
- `look.py`, `look2.py`: the dry 6b rulings on code lines, the receipts and the Architect sessions.
- `mig.py` and `mig_dry6b.db`: `connect` and `init_db` at the commit on copies of night 166 and dry 6b. The dry 6b probe sets r_m54 to `stale` in a transaction that it rolls back, for the s173 shape.

## (d) Usage

The harness does not show this agent its token counts. The estimate is about 120k input tokens, about 17k output tokens, about 137k in total. No model call, no suite and no gate ran.

## Second look, 822311e0

### Result

**Verdict: the eight findings are fixed. Two residual gaps stay, both low.** The 32 new tests and the related files pass: `2105 passed, 5 skipped, 10 xfailed`. All 11 mutations of the first look now turn a test red, and 3 new mutations of the pass 2 fixes do too. No model was called, and no tracked file was edited.

### (a) The eight findings

1. Fixed. `owed` takes only a contest or a revise as the newest ruling. Mutation `f1_approve_replaces` turns 2 tests red.
2. Fixed where a relay woke the rewrite. My own run: w7 owes r_m27 with stamps empty and gives `[]`. w8 and the final database stamp `m44`, owe nothing and give `["b_1"]`.
3. Fixed. The weak tests now assert a stamp value or a positive case first.
4. Fixed. The 6 mutations that stayed green now fail 1 or 2 tests each (probe: `mutate2.py`).
5. Fixed. `park_owns` keeps an owed park on the first live batch only. The page shows no contested set.
6. Fixed. `_guess_seed` drops the guess only on the guess line.
7. Fixed. A stamped `batches.guess` clears the plans of the pending batches. Mutation `f7_clear` turns 1 test red.
8. Fixed. `connect` calls `touch_columns`. Mutation `f8_connect` turns 2 tests red.

### (b) Point 2: which reading the rows support

The rows support the wide reading. His m39 and m41 are on pages m31 and m38, with `b_1` in the refs. Both rulings contest `b_1`, the batch line, not `guess:<item>`. His words on m44 repeat m27 with the line number changed: "Line 5 is wrong. The fold is _foldline in src/icalendar/parser/string.py ...". So he contested the same fault on the batch plan that s150 copied from the guess. s172 wrote `string.py` and `test_icalendar.py` into `batch_touch` under m44, which is his correction. The strict reading keeps m27 owed after a true rewrite and holds b_1 for good.

The wide reading cannot end an owed guess contest without a stamped write. A newer contest on the batch line becomes the owed ruling, and only a `batch_touch` row stamped with its verdict ends it. Two narrow ways remain:

- Under a newer revise, the door admits a batch set that equals the contested one. The stamp then ends the fact with the old files. This is the revise rule of the design, so it is not a defect.
- A newer contest on a merged or abandoned batch of the item makes `owed` give None. A guess contest on the same item then ends with no rewrite. No record shows this order, so it stays PLAUSIBLE.

The guess line itself keeps the old set in `touch_guesses`, and `code_target` still shows it. That is slice 3.

### (c) Point 3: the migration

The w7, w8 and final runs agree with the implementer, as section (a) shows. On a copy of the final database with every `sessions.trigger_msg` set to NULL, no receipt names a relay. The backfill then stamps nothing, and `owed("b_1")` gives r_m41 again. So a database whose rewrites came from ticks, or from sessions with no recorded trigger, still owes a contest that was rewritten. That is fault 3 of the pass 2 report. The cost is one more Architect wake, and at worst a park page that asks him again.

The backfill runs once, only when the column is missing. A database that pass 1 code already migrated keeps every stamp empty. `connect` now writes (`ALTER` and `UPDATE`) whenever a reader opens an old file, the cockpit included.

### (d) Point 4: the page in the worst case

The worst case is 1 relay, 3 `tick:guess` wakes, the quarantine report and one park ask.

- "This change waits before it starts." True. `next_batch` holds the batch.
- "The team tried 3 times, and it did not rewrite the guess." Mostly true. The count is the 3 tick attempts. The relay before them was a fourth try, so the page counts low by one.
- "You said: ..." True. These are his words of the owed verdict.
- "1." and "2. The code this request touches. It waits for the rewrite of the team." True.
- "Reply to line 2 to say again what to change, and the team tries again." True in the code. The order is `[item, guess:<item>]`. `land` has no code stamp for the park page, so a contest of line 2 stays on `guess:<item>`. That makes a newer ruling with a fresh key, and the park ends (`test_a_second_contest_gets_a_fresh_key_and_ends_the_park`). No test lands that reply through the Liaison.
- "Or say that you give the request up." No code reads these words. The Liaison landing seat must turn them into a ruling on line 1. A contest of the item goes to `do:cancel` through `park_owns`, but `rota/roles/api.py` 15267 reads only a "do not give up". This is PLAUSIBLE, as on the frame 87 page.
- "Nothing else waits on you." True. The hold is per item.

### (e) New findings

1. `rota/core/db.py` 155 to 198. Severity low. CONFIRMED. With no relay receipt, the backfill stamps nothing, and a rewritten batch contest is owed again (probe: `mig2.py`, `m2_norelay.db`). Fix: also stamp a row whose session was a `tick:annotate` on the batch after the verdict landed.
2. `rota/roles/principal.py` 2618 to 2634. Severity low. PLAUSIBLE. The page offers "give the request up", but no code or test turns those words into a drop of the request. Fix: add one landing case for a give-up reply on the owed park page.
3. `rota/core/scheduler.py` 1917. Severity low. PLAUSIBLE. A newer contest on a merged batch of the item ends an owed guess contest with no rewrite. Fix: skip a ruling on a merged or abandoned batch when `owed` picks the newest ruling.

### (f) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/029756dd-9273-4a54-95d8-2da05a2bfe52/scratchpad/ro362/`.

- `head2/`: a `git archive` of `822311e0`.
- `mutate2.py`: the 11 mutations of the first look on `head2/`, and the 32 tests per mutation. All 11 turn a test red.
- `mutate3.py`: 3 mutations of the pass 2 fixes for findings 1, 7 and 8. All 3 turn a test red.
- `mig2.py`: `init_db` at `822311e0` on copies of w7, w8, the final database, and a final copy with no trigger messages. It prints the stamps, `owed`, `next_batch` and the messages m39 to m46.
- The worktree run: the new test file, the files in `p362o/files.txt`, and four pin files, `2105 passed, 5 skipped, 10 xfailed in 196.81s`.

### (g) Usage

The harness shows no token counts. The estimate for the second look is about 30k input tokens and 5k output tokens.

## Third look, 3ebc5ac5

### Result

**Verdict: fix before the pick.** Finding 1 is high. The new approval check in `owed` also opens the equal-set door. A reply that contests line 1 and line 2 together lets the Architect stamp the set he called wrong, and the contest then ends for good. The fix is one line, and the 39 tests stay green with it. The other points hold. No model was called, no gate ran, and no tracked file was edited except this page.

### (a) The verdict on each point

1. Fails for `contested` and `pending`. The code writes 5 item statuses: `draft`, `pending`, `approved`, `contested` and `dropped`. An owed contest can be live in `draft` and `approved`. In `pending` and `contested` the contest must hold, because the request comes back. In `dropped` it ends correctly. `next_batch` and `cancel` already hold every batch of an item that is not `approved`, so the check gives no batch a start. But the door `_refuse_the_contested_set` also reads `owed`, and it opens (finding 1).
2. Confirmed. I ran the strict reading: a ruling on a closed batch never replaces, carried or not. On the migrated dry 6b copies with `b_1` merged or abandoned, it owes r_m27 again and wakes `tick:guess` with m28 for a done item. The implementer's test `test_a_rewritten_contest_on_a_closed_batch_owes_nothing` goes red under it. At the commit: w7 owes r_m27 and gives `[]`. w8 and the final database stamp `m44`, owe nothing and give `['b_1']`.
3. No wrong wake, hold or park page. His line-1 contest moves the approval, and that lift deletes the spent owed key (probe: `probe_back.py`). After the rewrite and his approve of version 2, r_m27 is owed again with a fresh bound of 3. The guess tick carries m28 and his version 1 words. The new batch waits for one stamped guess. The Architect writes a guess for version 2 in any case, so the cost is the stamp only.
4. On the recorded rows of dry 6b the page shows "tried 1 time". The count is s145 on the relay m29. The recorded ticks carry no verdict in their refs, so none count. The number is false when one verdict contests the guess of two requests: the page of one request counts the ticks of both (finding 2). The other sentences hold in the worst case. Line 2 and the give-up line now have landing tests.
5. Confirmed. Each of the 7 new tests turns red under its planted fault (probe: `mutate.py`). The two landing tests use `parse_reply`, `land` and a scripted Liaison session that calls `rulings.rule`. They write no ruling row by hand. The fixture r_m27 and the spent key of `_spend` are hand-built setup.
6. Small. One `frontier` read on the final dry 6b copy calls `owed` 14 times. One call takes 0.11 ms at `822311e0` and 0.15 ms at `3ebc5ac5`. One read takes about 690 ms at both commits, and the difference is in the noise.

### (b) Findings

1. `rota/core/scheduler.py` 1899 to 1901, with `rota/roles/api.py` 9150 to 9163. Severity high. CONFIRMED. The approval check makes `owed` give None for a `contested` or `pending` item. So `_refuse_the_contested_set` admits the set he contested. The relay path of `owed_ruling` still stamps the verdict, and the stamp ends the contest for good. Probe `probe_contested.py`: r_m27 holds `{guess: contest, item: contest}`, and the item is `contested`. The Architect's relay session on m29 sends the old 6-grain guess. At `822311e0` the door refuses it. At `3ebc5ac5` it lands with `m28`. After his approve of version 2, `owed` gives None, the guess tick has no verdict, and `next_batch` gives `['b_1']`. Fix: return None only when the approval is `dropped`. With that change all 39 tests pass, except the first assert of the `[other ...]` give-up case. Its later asserts pass (probe: `droponly.py`).
2. `rota/core/scheduler.py` 1974 to 1991. Severity low. CONFIRMED. `owed_tries` matches the verdict only, and not the item. One reply that contests the guess of two requests has one verdict. Probe `probe_tries.py`: the page of the first request says "tried 7 times". Its own tries are 4. Fix: count a tick only when `refs[0]` is the item or one of its batches.

### (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/8b2312ef-0b14-4322-a20c-908058cac23b/scratchpad/rv362/`.

- `head2/`, `head3/`: a `git archive` of `822311e0` and `3ebc5ac5`. `head3s/` is `head3/` with the strict closed-batch rule (`strict.py`). Its test file gave `1 failed, 38 passed`.
- `chk.py`: `init_db` on copies of w7, w8 and the final dry 6b database. It prints the stamps, `owed` and `next_batch`. `merged.py` sets `b_1` merged or abandoned in a rolled-back transaction, and prints `owed` and the guess wakes for both readings.
- `mutate.py`: 6 planted faults on copies of `head3/`, and the 7 new tests for each. Each fault turns 1 or 2 of them red. `head3/` itself gives `7 passed`.
- `probe_contested.py`: the door under a `contested` item, at both commits. `droponly.py`: the fix of finding 1 with the whole test file and that probe.
- `probe_back.py`: the park page, his line-1 contest through the landing door, then version 2 approved by `write_state`.
- `tries.py`: `owed_tries` on the dry 6b copies. `probe_tries.py`: one verdict on two requests.
- `cost.py`: 20 `frontier` reads and 1000 `owed` calls on the final copy at each commit.

### (d) Usage

The harness shows no token counts. The estimate for the third look is about 85k input tokens and 12k output tokens, about 97k in total.
