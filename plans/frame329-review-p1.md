# Frame 329, review 1: f0abfecb above 150607c1

**Verdict: hold for finding 1. Accept the rest for the branch.** Repair R is right, and the s194 replay on the night's own state shows it. Repair R2 sends the seat to `msg.challenge_vision_keeper`. After that challenge, the answer door still refuses every `msg.answer_tester`, so the landed c_1 rewrite never reaches the Tester in the session. The answer door also tells the seat to respecify c_2 again, and that invites a paraphrase twin under the 0.85 line. Register impact is zero, so the commit adds no stale case.

Counts: 7 points, 7 CONFIRMED. 4 findings: 1 high, 3 low.

## (a) The points

1. CONFIRMED. On a copy of night 166 with c_1 and c_2 reset to their relay texts, seq 12 lands and seq 13 is refused with "this says what c_1_format_filename_example says". At 150607c1, both land.
2. CONFIRMED that the exact check reads the staged ticket. The pass's reason for the cap is false: the cap with `_staged_ticket` seats no retired row, because the helper drops retired rows. A specify after a respecify is counted right with either read (finding 2).
3. CONFIRMED that the skip of a file-retired row is right. No writer clears `retired_by`, so a rewritten retired row never becomes live. The skip is wrong for a row that the session retires, because the read is of the file and not of the session (finding 3).
4. CONFIRMED. Only `terminologist/criterion_repair` holds `criteria.respecify`, and it holds `msg.challenge_vision_keeper`. So that mode always gets the whole tail. No terminologist mode lacks a tools file. The tail names no retire, so law 6 holds. The route that the tail names ends at a closed answer door (finding 1).
5. CONFIRMED. The specify refusal text is the same at both commits. At 150607c1 the respecify refusal equals it. At f0abfecb the respecify refusal starts with it and adds only the tail. The frame 306 file no longer pins the tail, and the frame 329 tests pin three parts of the tail.
6. CONFIRMED: zero. At qwen3:8b, two cases record `criteria.respecify` calls that reach the door. They are `L1-TE-repair-the-criterion-the-tester-cannot-encode` (3109 runs, one call each) and `L1-TE-a-ruled-criterion-is-respecified-and-the-tester-told` (1313 runs, 116 with two calls on one id). No run respecifies two ids, and no run specifies after a respecify. No recorded run holds a respecify near-twin refusal, so the new tail changes no recorded text. Three G1 cases call `criteria.respecify` from a seat without the op, and the sandbox refuses those calls before the door. The stale estimate from this commit is 0.
7. CONFIRMED. The body of `_twin_refusal` is the same text at both commits. It moves from 5669 to 5691 to 5687 to 5709, because `_staged_ticket` goes in above it. No hunk touches it, and bf300ce4 is an ancestor of f0abfecb.

## (b) Findings

1. `rota/core/sandbox.py` 1621 to 1626 (`_ruling_answer_refusal`), with `rota/roles/api.py` 6644 to 6650. Severity high. CONFIRMED for the doors, PLAUSIBLE for the night. On the s194 replay, the seat sends the challenge that the tail names, and the challenge lands. Then `msg.answer_tester` with c_1 and c_2 is refused with "No respecify of c_2 ... Respecify c_2_format_filename_example first". With c_1 alone, it is refused with "Your answer leaves out c_2". So the Tester gets no word of c_1's rewrite in the session. The session also gets a second order to rewrite c_2, and a small model can then write a paraphrase at 0.82, as c_3 is. Before f0abfecb the twin landed and the answer went out. The same gap exists for a twin on file since frame 306, so this is not new code. The commit makes the s194 shape reach the gap. Fix: in `_ruling_answer_refusal`, count a criterion that this session challenged to the Vision Keeper as written, as `respecify_stands` is counted, and pin it with the s194 replay.
2. `rota/roles/api.py` 5866 to 5868, and `tests/rota/test_desk_guards.py` 5018 to 5050. Severity low. CONFIRMED. The comment says that a staged read at the cap would seat a retired row. A copy with `_staged_ticket` at the cap passes the new test and the 38 other cap and seat tests. So the new test does not tell the two reads apart, and the comment states a false reason. The pass probe likely ran before the helper dropped retired rows. Fix: change the comment to say that both reads give the same count, or delete the comment. Keep the test as a pin of the count.
3. `rota/roles/api.py` 5674 to 5685 (`_staged_ticket`) and 6614 to 6622 (`_near_twin`). Severity low. CONFIRMED. A probe stages a rewrite of c_2, then a retire of c_2, then a respecify of c_1 with the same text. f0abfecb refuses the respecify as a twin of c_2, and 150607c1 admits it. The row on file is still live, so the helper gives c_2 its ticket. The cap subtracts a staged retire, and the twin doors do not. No night shows the order. Fix: drop the ids with a staged `retired_by` from the staged dict and from the file list, in `_near_twin` and in the exact check.
4. `rota/roles/api.py` 5834 to 5843 (the exact check of `criteria_specify`). Severity low. PLAUSIBLE, from the code. The staged part matches every staged text of an id, including a text that a later respecify replaced. The file part still matches the old text of a row that the session rewrote. So the exact door can refuse a specify as a twin of words that no row holds at commit. `_near_twin` now reads the last staged text, so the two doors disagree. No recorded run has a specify after a respecify. Fix: build the exact check from the same last-text dict as `_near_twin`.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/192bbbc0-82bf-4501-9027-b2a27953d7ec/scratchpad/r329/`. The trees `tree` (f0abfecb), `base` (150607c1 with the new test file) and `cap` (f0abfecb with `_staged_ticket` at the cap) were extracted with `git archive` and are deleted. No `cassettes.db` was copied. The register and the night database were opened with `mode=ro`.

- `pytest` on `base`: `test_frame329_staged_twin.py` gave 4 failed and 1 passed. The 4 failures include "DID NOT RAISE".
- `pytest` on `tree`: the three touched test files gave 369 passed.
- `replay.py`: night 166 copied by the SQLite backup API, with c_1 and c_2 reset. A session sandbox on wake m79 (mode `criterion_repair`) ran seq 12, seq 13, the answer, the challenge and the answer again. The probe ran on both trees (points 1 and 4, finding 1).
- `cap_patch.py`, then `pytest -k "seat or seventh or six or cap"` on `cap`: 39 passed (point 2, finding 2).
- `p3.py`: a staged rewrite and a staged retire of c_2, then a respecify of c_1, on both trees (finding 3).
- `p5.py`: the frame 306 fixture, with the specify and respecify refusals on both trees (point 5).
- `p7.py`: the source of `_twin_refusal` compared with `ast` at both commits (point 7).
- `modes.py`: every role mode, its tools file, and whether it holds respecify and the challenge op (point 4).
- `reg.py`, `reg2.py`, `reg3.py`, `reg4.py`, `reg5.py`: scans of `case_runs` transcripts and `cassettes.user` in the checkout register (point 6).
- `git status` in `C:/Users/roman/rota_p329`: clean, with HEAD at f0abfecb after the review.

## (d) Usage

- Input tokens: about 100k, an estimate. The harness shows no exact count.
- Output tokens: about 16k, an estimate.
- Total: about 116k, an estimate.

## Review 1b at 15e1a809

**Verdict: hold for finding 5. Accept the rest of 15e1a809 for the branch.** Findings 1, 2 and 3 are built and confirmed. The written-count rule of finding 1 is too wide. A challenge on a criterion now counts as a write, also when the session never tried to rewrite that criterion. So an answer that carries only the words he contested lands again, and frame 308 closed that route after night 159's s382 and s398.

### (a) The four checks

1. CONFIRMED. The s194 replay on the night 166 copy runs seq 12 (lands), seq 13 (twin refusal), the challenge on c_2 (lands), and `msg.answer_tester` with c_1 and c_2. At 15e1a809 the answer lands. At f0abfecb the door refuses it with "No respecify of c_2_format_filename_example has landed in this session".
2. CONFIRMED that the rule opens two more answers (finding 5). Both land at 15e1a809, and f0abfecb refuses both.
   - C: no respecify at all, a challenge on c_1 and c_2, then the answer with c_1 and c_2.
   - D: a respecify of c_1 lands, then a challenge on c_2 with no try at c_2, then the answer with c_1 and c_2.
   - E: a challenge on c_2 alone, with no respecify, is still refused, because c_1 has no write.
3. CONFIRMED. `test_a_rewrite_then_a_retire_of_a_sibling_is_no_twin` stages the retire in the same form as `criteria_retire` (api.py 6444, `{"retired_by": ...}` with the flag False). My probe from finding 3 now lands. `_staged_retired` uses the same predicate as the cap's retire subtraction. The exact check and `_near_twin` leave out those ids in their staged part and in their file part.
4. CONFIRMED. The comment at api.py 5877 to 5879 now says that a staged read gives the same count, and the probe of finding 2 showed that.

The implementer's note is right. Scenario B, an answer that leaves out c_2 after the challenge, is refused with "Your answer leaves out c_2_format_filename_example". The door keeps the one-answer rule of frame 308, night 158's s220: one answer carries every ruled criterion. The refusal now offers the full answer, and that answer lands in the replay.

### (b) Findings

5. `rota/core/sandbox.py` 1620 to 1626 (`_ruling_answer_refusal`). Severity high. CONFIRMED by scenarios C and D on both commits. The challenge set has no condition on a respecify try, so a seat can challenge a ruled criterion in place of rewriting it. Then the Tester reads the text that he ruled on, which is the night 159 fault. Fix: count a challenged criterion as written only when `ctx.respecify_refused` holds a refusal for it in this session. Add scenarios C and D as tests that stay refused.

### (c) Probes

- `replay2.py`: scenarios A to E on the night 166 copy, run on 15e1a809 and on f0abfecb. Both trees were extracted with `git archive` and are deleted.
- `p3.py` on 15e1a809: the respecify of c_1 lands.
- `pytest` on 15e1a809: the five touched files, the two frame 308 files included, gave 419 passed.

### (d) Usage

- Input tokens: about 25k more for this pass, an estimate.
- Output tokens: about 5k, an estimate.
- Total for review 1 and 1b: about 146k, an estimate.

## Review 1c at 9b60957d

**Verdict: accept 9b60957d for the branch.** Finding 5 is built and confirmed. No new finding. The deviation is right. `respecify_refused` keeps only the last refusal of each criterion, so a later refusal of another kind would erase the twin, and scenario F shows that case.

### (a) The three checks

1. CONFIRMED. On the night 166 copy, scenarios C and D are refused again with "No respecify of ... has landed in this session". Scenario E stays refused. Scenario A, the s194 replay, still lands its answer. In scenario B, the answer without c_2 is refused, and the full answer then lands.
2. CONFIRMED. The flag is set on the `ValueError` in `_near_twin` (api.py 6663 to 6667), only on the respecify branch. `_respecify_record` (sandbox.py 1733 to 1738) adds the id to `ctx.respecify_twinned`, and no code removes it. In scenario F, a twin refusal of c_2 is followed by a refusal for a bad argument, an "about the tests" refusal, a `glossary.lookup` and the challenge. The answer then lands. In scenario G, a different fact for c_2 lands after the twin refusal, and the answer lands. In scenario H, the challenge names c_1 only, and the answer is still refused. The ctx lives for the whole session, because `run_session` builds one sandbox. The `dry_run` of the follow check snapshots and restores a set, so a dry run leaves no flag. `dry_run` runs only in the case harness.
3. CONFIRMED. `_ruling_answer_refusal` (sandbox.py 1627) is the only reader of `respecify_twinned` and of `criterion_twin`. No test and no other module reads either name.

### (b) Probes

- `replay2.py`, scenarios A to H, on 9b60957d. The tree was extracted with `git archive` and is deleted.
- `pytest` on 9b60957d: the five touched files gave 421 passed.
- `git status` in `C:/Users/roman/rota_p329`: clean.

### (c) Usage

- Input tokens: about 20k more for this pass, an estimate.
- Output tokens: about 4k, an estimate.
- Total for reviews 1, 1b and 1c: about 170k, an estimate.
