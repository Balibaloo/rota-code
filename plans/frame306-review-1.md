# Frame 306, review 1: repair 1 at 07e4d1bc

Verdict: accept for the branch. The claim holds on every point that a probe reached. The repair cures the missing-key refusal and the double wake. It does not move night 158's words on the seat's recorded first call. That call, `{cr_2: approve, tst_02: approve}`, now lands and wakes the Terminologist in `relay` mode, as s287 did. Only a revise reaches `criterion_repair`, and with change 3 held nothing pushes the seat to a revise.

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_r306` at 07e4d1bc, parent d2b4f79a. No gate and no re-record ran.

## (a) The claim, point by point

1. CONFIRMED. On a copy of night 158 at 07e4d1bc, `{cr_2: approve, tst_02: approve}` lands with no refusal. `{cr_2: revise, tst_02: approve}` lands, stages one relay `[cr_2]`, and that relay keys `criterion_repair`. `open_tips` gives one Terminologist wake. See finding 1 for what the recorded call now does.
2. One site disagrees with the door, `prior_answers` (finding 3). The relay widening reads the reply's refs, which are the clarify's own refs (finding 4). Parking keeps the clarify's own refs on purpose, and the re-present reads the parked ledger rows, so both agree with each other. The page shows the clarify's own refs to the principal. That is what he read, so it is no fault. The receipt does not read a clarify's refs.
3. On nights 150 to 158, one clarify of 72 with an asker has an asker criterion that the clarify did not carry: night 158's m145, reply m146. The seat ruled `{cr_2: approve, tst_02: approve}`, the old door refused cr_2, and `{tst_02: approve}` landed. The new door admits the first call. The words of m146 are a revise of cr_2, so the new door admits an approve that the words do not support (finding 1). On nights 140 to 158, ten other clarifies have asker-only rows: batches, message ids and one entry. The door now admits each as a key (finding 2).
4. CONFIRMED. The relay of a revised cr_2 carries `principal_verdict {cr_2: revise}` and `principal_said` with the words of m146. `chain_verdict` finds the landed `rulings` row by `reply_id`.
5. The rebuilt held door gives 70 of 125, with the same cue split as the pass report: should 44, not 8, instead 6, drop 4, also 4, still 2, wrong 2. A sample of five "should" fires: night 143 m279, 145 m132, 146 m60 and 147 m110 are right approves, and 144 m312 is a faulted approve. The narrow set, "do not", "don't", "never", "instead of", fires on 47 of 125. It fires on m146 ("Do not"). It does not fire on m313. By my reading, at most 7 of the 47 fault a ruled row. Most fires are "I don't know" and "instead of aborting" in agreement. The narrow set is not a better words test.
6. CONFIRMED. The diff is five files. Every source hunk is inside `answer_about`, `resolve_inbound`, `rulings_rule`, `park_criterion_relay`, `ruled_clarify_criteria` and `_bind_send.stage`. The test file is new. `test_frame306_clarify_about.py` and `test_frame250_verdict_faults.py` give 22 passed, 1 xfailed with `-n 0`.

## (b) Findings

1. `rota/roles/api.py` 10185 to 10196 with `rota/core/scheduler.py` 1873. Severity: low for the night, high for the frame. CONFIRMED. A whole session on a night 158 copy, with the calls of s286 turn 1, `{cr_2: approve, tst_02: approve}` and `relay_terminologist([cr_2])`, commits. Relay m150 `[cr_2]` keys `relay`, not `criterion_repair`, and cr_2 keeps its text. This is night 158's s287 end by another route. The seat's recorded reading of m146 was approve. The repair needs a revise that no door asks for. Fix: keep the frame open on the m146 shape, and measure the seat on the new door with the held change 3 still out.
2. `rota/core/runner.py` 183 to 203, `answer_about`. Severity: low for the night, low for the frame. CONFIRMED. The union takes every asker ref, not only rows. On a night 144 copy, the door admits `m385`, a message id, as a key on m399, and lands it in `per_item`. Batch keys `bg_2` and `bg_3` reach the batch door. They are refused there only because each batch closed by the night's end. Fix: keep an asker ref in `answer_about` only when `_table_of_ref` finds a criterion or a test row.
3. `rota/core/runner.py` 2219 to 2233, `prior_answers`. Severity: low for the night, low for the frame. PLAUSIBLE. A later report shows a prior clarify answer only when the report's refs meet the clarify's own refs. m146 is about cr_2 by the door and the prompt, but a later report that names only cr_2 does not see it. Fix: match `prior_answers` on `answer_about(conn, c["id"])` when the clarify has an asker.
4. `rota/core/sandbox.py` 3623 to 3634, the relay widening. Severity: low for the night, low for the frame. PLAUSIBLE. The widening adds the reply's refs, which `land` copies from the clarify's own refs. A criterion that the seat rules contest from the asker's refs is not added when the seat leaves it out of the relay. On night 158 the test row covers this, because tst_02 travels as cr_2. A clarify with no test of that criterion has no such cover. Fix: on a clarify reply, also add the landed ruling's contest and revise keys to the relay's refs.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/1b2c3f89-168f-4708-a241-5ecb0a745d11/scratchpad/r306/`. Each copies a night database with `?mode=ro` and the SQLite backup, then works on the copy.

- `p1_replay.py`: night 158 copy, the m146 rulings deleted, m146 reopened. Three door calls, the prompt's `about`, a scripted session with the revise, `apply_rulings`, the mode key, the Terminologist's inbound and `open_tips`.
- `p1c_turn1.py`: night 158 copy, the scripted session with s286 turn 1's calls, the relay's mode and cr_2's text.
- `p3_count.py`: nights 150 to 158, read-only. It lists clarifies whose asker named a criterion that the clarify did not carry, with the ruling and the seat's tool calls.
- `p3b_any.py`: nights 140 to 158, read-only. It lists clarifies whose asker named any ref that the clarify did not carry.
- `p3c_door.py`: night 155, 144 and 148 copies. It runs the door with asker-only keys `bg_3`, `m385` and `bg_2`.
- `p5_held.py`: nights 143 to 158, read-only. It rebuilds the held door from `_live_cues`, `_SENTENCE` and `_WEAK_CUES`, counts it, and counts the narrow cue set.
- `pytest tests/rota/test_frame306_clarify_about.py tests/rota/test_frame250_verdict_faults.py -q -n 0`: 22 passed, 1 xfailed.

## (d) Usage

- Input tokens: about 110k, from the remaining-token counter.
- Output tokens: about 14k, estimated.
- Total: about 124k. The harness does not show the exact split.
