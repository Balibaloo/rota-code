# W14 pass 1 review: commit 96b81667 on w14root

Verdict: NOT READY. 1 high finding, 3 low findings.
The code part retires 0 of the 4 remove rows of night 175, the night that stopped.
The own-id guard blocks the exact shape that the seat wrote on that night.

## (a) Verdicts on the numbered points

1. One reader: PASS. criteria_page_acts, criteria_retire, tests_retire and sandbox.py 2163 read _dropped_line only. The other remove readers read items or code targets.
2. Guard: FAIL. c_1 stays live, but c_2 and c_3 also stay live at r_m103_2 and r_m148. The real rows carry target = own id. See finding 1.
3. Remove, kind row, a target that names another row: the criterion that holds the row retires. A drop does the same today. Acceptable, see finding 2.
4. Prompt: PASS. No case, test or door reads the cut sentence. The new sentence contradicts no other line of landing.md.
5. Cases: PARTLY. The replies match the records. Case 1 uses a c_2 text from a later page. The expects do not bind drop to each deleted line. All three are unrecorded.
6. Tests: CONFIRMED. The new file is 1 red, 6 green at the parent and 7 green at 96b81667. The touched-file suite has 1 red at both commits, and that red is not from this commit.
7. Committed files: PASS. The commit holds 4 files and no recordings, caches or scratch files.

## (b) Findings

1. rota/roles/api.py 6590 to 6592, and tests/rota/test_w14_remove_row_drops.py 106. Severity high. CONFIRMED.
   The guard returns None when the target is the criterion's own id.
   Night 175 stored r_m103_2 and r_m148 on c_2 and c_3 as remove, kind row, target = the criterion's own id.
   A replay of the night 175 register at each ruling step gives _dropped_line None after r_m103_2 and after r_m148.
   So the code part covers only night 174's r_m79 rows, which have no target: 2 of 6 remove rows.
   The premise of the guard is wrong. r_m118 on c_1, c_2, c_3 and the 4 tests has the kind source_line, not row.
   r_m138 on c_1 has no kind. The check of the kind alone keeps c_1 live at every step.
   The guard has no recorded case that it protects. The test remove-row-on-its-own-id fixes the wrong reading in place.
   The commit body and the docstring repeat the wrong r_m118 shape.
   The guard came from the brief and the reach read caution (section 1.5), which is reasoned, not a ruling.
   Fix: remove the own-id clause, keep target_kind == "row", and expect a retire in the own-id test.

2. rota/roles/api.py 6576 to 6583. Severity low. CONFIRMED.
   The docstring says "on the row itself", but the code accepts any target except the own id.
   A remove with kind row and target reading:m103, c_1 or "3" on the c_2 row retires c_2.
   A drop with target c_1 on the c_2 row also retires c_2, so the two acts agree.
   Fix: after the fix of finding 1, say in the docstring that the kind row decides and the target does not.

3. tests/rota/cases/l1_landing.yaml 380 to 381. Severity low. CONFIRMED.
   Case 1 names m116 as its page, but its c_2 text is the text of the m136 page.
   On m116, c_2 says "when shorten=False, the path a/b/c.txt is displayed as a/b/c.txt".
   The case text "exactly one example ... shorten=True" states his own ask, so the page reads less like his page.
   Fix: copy the c_2 text of m116 from l3_rulings_judged.yaml entry n175-m116-m118.

4. tests/rota/cases/l1_landing.yaml, the three ruled_refs expects. Severity low. PLAUSIBLE.
   text_includes checks '"act": "drop"' and '"target_kind": "row"' on all rows together.
   A run with drop on c2 and contest with no act on c3 can pass. The real fault left one row live in this way.
   Fix: bind each expect to its ref, for example text_includes that holds the ref id with "act": "drop".

Outside the points: the prompt edit changes the prompt hash of landing. The 9 recorded l1_landing cases go stale until the gate records them again. The brief accepts this.

## (c) Probes

All probes are in C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/161c371b-f6a2-4d73-aebc-bae776885ab7/scratchpad.

- w14r_q1.py: lists the act rows on criteria in ruled_refs. It ran on n175/clickI_night175.db and l3g/clickI_night174.db. It showed r_m103_2 and r_m148 with target = own id, r_m118 as source_line, and night 174 r_m79 with no target.
- w14r_q2.py: runs grant and _dropped_line of 96b81667 on the end state of night 175. c_4, c_5 and c_6 drop. The c_*_format_filename_example rows do not.
- w14r_q3.py: makes an in-memory copy of night 175, deletes the rulings after each step and runs _dropped_line. It gave None for c_1, c_2 and c_3 at every step.
- w14r_q4.py: lists the landed remove rows on refs that are not criteria, nights 170 to 175. Night 175's test rows are source_line.
- w14r_q5.py: reads m102, m116, m118, m136, m138 and the stored order:m118. The order is item, c_1, 4 tests, c_2, c_3, bg_3, readings.
- w14r_p3.py: builds the page of the new test with 7 remove and drop shapes and runs _dropped_line and criteria_page_acts.
- w14par: git archive of 646fedfe with the new test file. The new test file ran 1 failed, 6 passed. The touched-file suite of 46 files ran 5 failed, 1337 passed, 14 skipped. The test_refs red and the extra skips come from data missing in the archive copy.
- The worktree at 96b81667: the new test file ran 7 passed. The touched-file suite ran 1 failed, 1353 passed, 2 skipped, 16 xfailed. The red is test_scene_two_batches test_a_right_call_lands: ledger.log misses the argument kind. It is red at the parent too.

## (d) Usage

Input tokens: about 105k. Output tokens: about 9k. Total: about 114k. The harness gives no exact count.

## p2: review of pass 1b, commit a1589b6d

Verdict: READY. 0 high findings, 1 low finding. Findings 1 to 4 of p1 closed on a probe.

### (a) Verdicts on the checks

1. The own-id clause: CLOSED. _dropped_line now returns None only when no grant exists or target_kind is not "row". _target_key is no longer imported.
2. The replay: CLOSED. The r_m103_2 shape on c_2 (remove, row, target c_2) retires in the test page. The r_m118 shape (source_line) and the r_m138 shape (no kind) on c_1 do not. On the night 175 register, r_m148 now retires c_2 and c_3 at lines 8 and 9. c_1 stays live at every step.
3. Case 1: CLOSED. c_2 now has the m116 text "when shorten=False, the path a/b/c.txt is displayed as a/b/c.txt".
4. The expects: CLOSED. Each case expects one ruled_refs string per deleted line with the ref, the line, contest, drop and row. Cases 1 and 3 expect c2 at line 7 and c3 at line 8. Case 2 expects c2 at line 1 and c3 at line 2.
5. The docstring and the commit message: CLOSED. Both state r_m103_2 and r_m148 as kind row with the own id. Both state r_m118 as source_line on c_1 and r_m138 as no kind.
6. test_fixtures.py::test_no_case_leaves_a_reference_unwrapped: the failure is there before this branch. The test finds each placeholder name, such as <t1>, that also stands bare in the same case file. A bare name points a foreign key at a row that does not exist. At 646fedfe the test finds 30 hits, in g1_segments.yaml (2), l1_liaison2.yaml (9) and l1_tester.yaml (19). At 96b81667, l1_landing.yaml adds 14 hits. The new <t1> collided with the literal thread_id t1. At a1589b6d the rename to <tst1> to <tst4> removes all 14 hits. The set is again equal to the set at 646fedfe.

### (b) Findings

5. rota/roles/api.py 6593, outside the checks. Severity low. CONFIRMED.
   The real r_m103_2 still retires nothing. Its rows come from the clarify page m102, and that page has no line numbers.
   grant returns the r_m103_2 row with kind row. row["line"] is None, and _ruling_line also gives None.
   A drop on a clarify page has the same gap, so the gap is older than this branch. Night 175 recovers at r_m148.
   The test page has numbered lines, so the test passes. The docstring suggests that r_m103_2 retires.
   Fix: give _dropped_line the position of the ref in the refs of the clarify page, or file the gap as its own issue.

The r_m138 test gives no target, but the real row carries the own id as its target. The kind check rejects the row either way, so the gap has no effect.

### (c) Probes

- w14r_q3.py on n175/clickI_night175.db with the worktree at a1589b6d. After r_m148, c_2 gives line 8 and c_3 gives line 9. After r_m103_2, grant finds the row with kind row, and _dropped_line gives None. c_1 gives None at every step.
- pytest on tests/rota/test_w14_remove_row_drops.py at a1589b6d: 9 passed.
- pytest on test_no_case_leaves_a_reference_unwrapped: red at a1589b6d and red in the w14par archive copy of 646fedfe. Both runs give the same first hits, in l1_liaison2.yaml.
- w14r_fx.py: runs the same check on each case file through git show at 646fedfe, 96b81667 and a1589b6d. It gives the hit counts in item 6 of (a).

### (d) Usage

Input tokens: about 30k. Output tokens: about 4k. Total: about 34k. The harness gives no exact count.

## p3: review of pass 1c, commit 55785d6a

Verdict: READY. 0 high findings, 1 low finding. p2 finding 5 closed on a probe.

### (a) Verdicts on the checks

1. The value 0: SAFE. Five places read the value, and each compares it with None. criteria_page_acts (api.py 6654) and sandbox.py 2163 use "is not None". criteria_retire (6759) and tests_retire (6814) use "is None". runner.py reads only the retire list of criteria_page_acts.
   The door tests "if dropped" and "not dropped" on the dict, not on a value. The door formats n only in the new branch. Nothing sorts the value.
   The one "or" in _dropped_line runs before the 0 exists. It acts on row["line"] and _ruling_line, which are both 1-based or None.
2. The replay: CLOSED. On the night 175 register, criteria_page_acts lists c_2 and c_3 for retire after r_m103_2, with value 0. It lists them again after r_m148, at lines 8 and 9. c_1 is never listed, and its value is None at every step.
3. The door sentence: CORRECT by reading. Page lines start at 1 (_ruling_line: order.index + 1, seen order: index + 1). So n == 0 comes only from DROPS_THE_ROW. The numbered sentence stays, and test_frame308_ruling_answer.py checks it and passes.
4. The tests: CONFIRMED. The new file runs 12 passed. The touched-file suite runs 1 failed, 1358 passed, 2 skipped, 16 xfailed. At 96b81667 it ran 1 failed, 1353 passed. The 5 extra passes are the 5 new tests. The one red is still test_scene_two_batches test_a_right_call_lands, the same ledger.log kind error.

### (b) Findings

6. rota/core/sandbox.py 2172. Severity low. CONFIRMED.
   No test renders "The principal's ruling drops c_2.". The two new clarify tests stop at criteria_page_acts and criteria.retire.
   Fix: add one door test with a clarify drop, and check the sentence and that "line 0" does not appear.

### (c) Probes

- w14r_p3c.py in the scratchpad: it copies night 175 into memory, deletes the rulings after each step and clears retired_by. Then it runs _dropped_line and criteria_page_acts on c_1, c_2 and c_3.
- A grep for ruling_drops_line, _dropped_line and DROPS_THE_ROW in rota/, and a read of sandbox.py 2160 to 2215.
- pytest on the new file and on the 46-file touched-file suite at 55785d6a.

### (d) Usage

Input tokens: about 25k. Output tokens: about 3k. Total: about 28k. The harness gives no exact count.
