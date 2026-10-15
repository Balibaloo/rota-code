# Frame 245, review 1 of 01df5c4c: `tick:unresolved` skips a challenge whose tests are green

Reviewer: Opus, 2026-10-15. Meta workflow review of a rota workflow (the seats) predicate.
Worktree: `C:/Users/roman/rota_r245` at 01df5c4c, read-only, removed after the review.

## Verdict: accept with fixes

The skip is right for the shape it was built on, a Developer challenge to the Tester on a red test.
The skip also fires on a Critic challenge to the Tester. A Critic challenge names a green test by construction.
On that shape the obligation disappears from every count and from the merge hold (finding 1, high, CONFIRMED).
One guard on the sender closes it.

## (a) The seven points

1. Partly. `_tests_green` reads the newest run of the own batch of the test, keyed on `test_runs.rowid DESC`. It has no bound against the time of the challenge.
2. The skip covers the message kind only. The `challenges` table holds the claim verdicts of the Critic, has no status, and never feeds this predicate.
3. No reader counts the skipped row as owed work. For the Critic shape that is the defect: the obligation goes silent (finding 1).
4. Inside law 6 for a Developer challenge on a red test. Outside law 6 ("It is never silence") for a Critic challenge.
5. Red at the parent for the right reason: the parent wakes `architect` `tick:unresolved` on m76. Green at the commit.
6. Stale reads 0 because no recorded case seeds an unresolved challenge with a green run. No pushed byte changes.
7. Intact. The backslash-quote bytes are in the blob, the worktree file equals the blob, and both files hold 0 CR.

### Point 1: what "newest" keys on

- The key is `ORDER BY tr.rowid DESC LIMIT 1` with `tr.batch_id = t.batch_id`. This copies `sandbox._test_is_red` (sandbox.py:1673).
- `harness.run` deletes the runs at the same commit and then inserts (harness.py:150-157). The new rows take a rowid above every surviving row. So rowid order is run order.
- A run of another batch: excluded. `harness.inherit` moves `tests.batch_id` to the new batch by `INSERT OR REPLACE` (harness.py:262). So the own batch is the current batch.
- A run before the challenge: not excluded. The query has no seq or time bound against the message. A challenge raised on a test that was already green is skipped at once. This is the Critic shape (finding 1).
- A test re-encoded: `db.py:611` deletes all runs of the test on a body change. The ref then has no run, `seen` stays false, and the challenge climbs until the harness runs again. That is conservative.
- A test renamed to a new id: the old id keeps its old runs while the old row stays. A green old run then skips the challenge. No night shows this (PLAUSIBLE, low, not listed as a finding).
- A ref with no run is ignored. One green test plus one ref with no run reads green.

### Point 2: the shapes over 65 nights (probe p2_shapes.py)

Rows with `messages.verb = challenge`, by sender, addressee and final status. The last column says whether a ref names a `tests` row.

| from -> to | answered | open | unresolved | names a test |
|---|---|---|---|---|
| developer -> tester | 353 | 1 | 1 | all |
| critic -> tester | 4 | 0 | 0 | all |
| critic -> developer | 1 | 0 | 0 | none |
| architect -> vision_keeper | 174 | 0 | 1 | 55 |
| terminologist -> vision_keeper | 172 | 1 | 2 | none |

The `challenges` table holds 925 rows over the same nights. Those rows are claim verdicts (`stands`, `falsified`, `unfounded`). They have no status column and no test ref. No end-of-night row is both unresolved and green. The 13 wakes in the pass report were on rows that a later session answered.

Three of the four Critic challenges read green at the end of the night (night 92 m101, night 116 m68, night 147 m70). The Critic sends `msg.challenge_tester` from review, and review runs on a green batch.

### Point 3: the readers of `status = unresolved`

- Counted through the predicate, so the skipped row drops out: `predicates.outstanding` (predicates.py:1945, the cockpit and TUI pane of what the system owes) and `lifecycle.waiting_on_a_seat` (lifecycle.py:519, through `_next_rungs`). `mergeable` uses the second as its seat hold (lifecycle.py:651).
- Counted on `status = open` only, so the row never counted: `scheduler.tick_agenda` (scheduler.py:1050), `loop._why_idle` (loop.py:597), `loop.gates_open` (loop.py:615), and the `awaiting_principal` part of `outstanding` (predicates.py:2003).
- Other predicates: `tests_missing` (predicates.py:797), `sandbox` (2955) and `api.tests_triage` (6030) read `verb = question` only. `criterion_repair` (predicates.py:1295) reads `from_role = tester` only, and the Tester sends no challenge.
- Writers, not counters: `db.session_commit` lines 876 and 988 set the row to `answered` when a later session sends in the thread. That is still a discharge for the row.
- Shown, not counted: `nightreport.py:481` prints the row as `unresolved`. The cockpit snapshot (server.py:140) shows the raw status of the last 60 messages.
- `invariants.i9` and `audit` group 5 read `status = answered` only.

For a Developer challenge, the green run is a derived discharge, like the empty ladder that "goes quiet" in the docstring. The note under law 6 prefers a derived rung over a stored one. So that shape needs no write. For a Critic challenge, nothing discharges the row and nothing counts it.

Fix line: restrict the skip to a Developer sender and a Tester addressee. No new writer is needed, so the one-writer rule is not touched. If Roman wants the status itself to change, `scheduler` is the writer, as for `close_park_asks`. The write is `status = answered`, and `i9` then needs a green-run exemption.

### Point 4: law 6

Law 6 (rota/LAWS.md:185-191): "At the Liaison it is a page, a hold or a note for the principal. It is never silence. ... A question nobody answers climbs (`unresolved`)."

A Developer challenge says that a red test is wrong. A green newest run means the Tester replaced the test or the code met it. Law 8 says gates are predicates, so a run result settles that dispute mechanically. `invariants.i9` already treats the replace by the Tester as the answer. So the skip is inside law 6 for that shape.

A Critic challenge says that a passing test does not encode its criterion. A green run is the premise of that dispute, not its answer. The skip then makes the tool settle the dispute, and the result is silence. That is outside law 6.

### Point 5: the tests both ways (probe p5_parent.py)

- At the parent (predicates.py from the parent commit, loaded in place of the module): the green test FAILS with `the test passed, so the challenge is moot`. `unresolved` returns one wake, `architect`, `tick:unresolved`, refs `m76`. That is the night 148 s200 wake. Right reason.
- At the parent, the red test passes. It is a guard, not a red-first test.
- At the commit: `pytest tests/rota/test_predicates.py -q -k "newest_run or lifecycle_state"`: 3 passed in 3.04s.
- The seed holds one run row. So the tests do not exercise "newest" over an older red row.

### Point 6: why stale reads 0

The recorded cases give the wake through `role` and `inbound`. They do not take it from `unresolved()`. Seven case lines seed or expect `status: unresolved`. The only case file with both an unresolved line and `test_runs` is `l1_tester.yaml`, and every run there is `result: fail`. So no case reaches the new branch, and no pushed byte changes (observed: grep, 2026-10-15). `outstanding` feeds no prompt.

### Point 7: the heredoc bytes

`tests/rota/test_predicates.py` at 01df5c4c: 0 CR and 54 backslash-quote pairs. Lines 2487-2488 hold the escaped JSON refs as written. The worktree file equals the blob at 01df5c4c byte for byte. `rota/core/predicates.py` holds 0 CR. `git diff --check` is clean. The refs parse, because the parent run reaches the wake on m76.

## (b) Findings

1. **A Critic challenge on a green test goes silent.** rota/core/predicates.py:1149. Severity high. CONFIRMED (probe p3_critic.py): the night 148 seed with sender `critic` wakes `liaison` at the parent and nothing at the commit. `waiting_on_a_seat` on bg_3 reads `waiting on liaison: m76` at the parent and `None` at the commit. `outstanding` drops `unresolved`. A barren Tester session sets such a row to `unresolved` (db.py:941), so the shape is reachable. Fix: skip only when `from_role` is `developer` and `to_role` is `tester`, and add a Critic-sender test that still climbs.
2. **A later red run revives the old challenge.** rota/core/predicates.py:1149. Severity low. PLAUSIBLE: the skip is a read, not a discharge. A new red run on the same test wakes the next rung on the old dispute, beside the `tick:tests_failing` wake of the Developer. Fix: accept as is, or bound the run to the seq of the challenge when a column for that exists.
3. **The night report shows a skipped row as owed.** rota/tools/nightreport.py:481. Severity low. CONFIRMED by read: the line prints `m76 unresolved developer->tester challenge` with no sign that the ladder skips it. A meta workflow reader can read a discharged row as open. Fix: mark the row `green: no rung` when `_tests_green` is true.
4. **The tests pin neither "newest" nor the sender.** tests/rota/test_predicates.py:2461-2514. Severity low. CONFIRMED by read: one run row only, and sender `developer` only. Fix: seed a `fail` row before the `pass` row, and add the Critic case of finding 1.

Outside the points: architect -> vision_keeper challenges named a `tests` row 55 times (night 106 m69, night 108 m177). Their subject is scope, not the colour of a test. The guard of finding 1 covers them too.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/dae006d1-0f15-4df0-b329-c022767b2f08/scratchpad/f245/r1/`. Each opens night databases with `mode=ro`.

- `p2_shapes.py`: counts challenge messages by sender, addressee, status and test ref over `.rota/clickI_night*.db`, less `partial`, `cut`, `walk1`. It also counts `challenges` rows and runs `_tests_green` on unresolved rows.
- `p2b.py`: lists Critic and Architect challenges that name a test, with `_tests_green` at the end of the night.
- `p3_critic.py`: seeds the night 148 chain of the test with sender `developer` and then `critic`. It compares `unresolved`, `waiting_on_a_seat` and `outstanding` at the commit and with `_tests_green` forced false, which is the behaviour of the parent.
- `p5_parent.py` with `predicates_parent.py` (the parent blob): runs the two new tests against the parent predicate module.
- Inline: `pytest tests/rota/test_predicates.py -q -k "newest_run or lifecycle_state"` in the worktree, 3 passed. A byte check of both files for CR and backslash-quote pairs.

## (d) Usage

About 100k tokens of context in total, by the harness count. The reviewer cannot see the split of input and output. No sub-agent.
