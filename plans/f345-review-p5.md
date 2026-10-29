# Frame 345, review p5: commit ac900593 on seam3root (parent 7b4529ff)

NOT READY. The stage itself is sound, and the three drop cases cannot pass on it or on the parent, because the runner counts no ruled_refs write. One prompt sentence contradicts the code. Two one-line fixes.

## (a) Verdicts

1. Cause found. The rows land. session_commit writes no receipt for a ruled_refs row, so fixtures.capture counts 0 writes. The parent has the same fault. Review p4's _word_shape suspicion is wrong.
2. Confirmed. No cue list and no meaning read was added. Each deleted test pinned a removed refusal, except the second half of the p9 test (finding 3).
3. 41 lines, the four definitions are present. Line 19 contradicts the code (finding 2).
4. "1 is fine, 2 and 3 are wrong" binds lines 1, 2 and 3 to the whole sentence. "lines 7, 8 and 9 go" binds 7, 8 and 9.
5. Confirmed on four names. The same four fail at the parent tree.

## Point 1, the trace

The seat's call in the worktree register (case_runs row 667631, 06:08:19) is
rulings.rule(rulings={"1": "approve", "2": "approve", "3": "drop", "4": "drop", "5": "drop", "6": "drop", "7": "drop", "8": "drop", "9": "approve"}), with no words argument. The turn shows wrote: {"rulings": 1}.

Probe 1 replays that call through fixtures.run_case with a ScriptedBackend, as test_l3r_retire_check.py does. The test database then holds ruled_refs rows for lines 7 and 8: verdict contest, act drop, target_kind row, source reading, words "remove lines 7 and 8 and finish with line 2 alone, ...". So rulings_rule, _word_shape (api.py 11612), _ruled_rows (api.py 12268) and _stage_ruling (api.py 12286) all do their work. The runner still reports "expected writes to ruled_refs (>0), got 0".

Probe 3 reads the receipts table after the same replay: one row, (s1, rulings, r_m_in). fixtures.capture (rota/testkit/fixtures.py 541-545) builds delta.writes from receipts alone. session_commit (rota/core/db.py 1705) skips the receipt: "if table not in ARTEFACT_TABLES or not changed: continue". ARTEFACT_TABLES comes from TABLES_OF_ARTEFACT (db.py 40-88), and ruled_refs is not in it (probe: 'ruled_refs' in ARTEFACT_TABLES is False). So delta.writes never holds ruled_refs, and a case that expects writes.ruled_refs fails on every call that lands.

The three cases are the only cases of l1_landing.yaml with a ruled_refs expectation. Commit 96b81667 added it. The main register holds 5 runs of each case, all of 05:44, none passed.

The parent: db.py and fixtures.py are not in the stage's diff. The main register rows of 05:44:00 and 05:44:01 show the seat's first call refused by _faulted_approve ("The words fault line 2, 'alone'"), then a second call with words that landed with wrote: {"rulings": 1} and 0 ruled_refs. The parent has the same fault. The stage removed the refusal, so the first call now lands, and the count still reads 0.

One-line fix, in capture after the receipts loop (fixtures.py 545):
writes["ruled_refs"] = [r[0] for r in conn.execute("SELECT id FROM ruled_refs WHERE source = 'reading' AND ruling_id IN (SELECT row_id FROM receipts WHERE session_id = ? AND table_name = 'rulings')", (session_id,))], kept out of the map when empty.

## (b) Findings

1. rota/core/db.py 1705 and rota/testkit/fixtures.py 541-545. High. CONFIRMED: probe 3 shows the ruled_refs rows in the table and one receipt, for rulings. The three drop cases measure nothing until the count sees the rows. Fix: the capture line above, or receipt ruled_refs under its ruling row.
2. rota/roles/prompts/liaison/landing.md 19, "On any other page line, remove is a drop of that line". High. CONFIRMED: probe 5 lands the word remove on criterion line 7 as act remove, target_kind row. The code converts nothing, and the three cases exclude "act": "remove". Fix: write "On any other page line, write drop, not remove".
3. tests/rota/test_p9_account_rows.py, the deleted test_words_that_name_no_line_land_on_nothing_on_the_account_page. Low. CONFIRMED by the diff: its second half pinned ACCOUNT_UNNAMED on the next request page from a note set by hand, under 25 words and not in render_page. That sentence is still live for old notes. Fix: restore the second half as its own test, or delete account_unnamed_line with it.
4. rota/roles/api.py, line_words, outside. Low. CONFIRMED: probe 4 binds line 1 of "1 is fine, 2 and 3 are wrong" to the whole sentence, "are wrong" included. The seat reads the fault beside the line that is fine. Fix: bind a bare-list clause to its own clause, as _bare_subject already splits on the comma.
5. Outside. Low. PLAUSIBLE: in probe 1 the seat dropped lines 3 to 6, four test rows that his words call ok, and the case pins only lines 7 and 8. With finding 1 fixed the case passes on a wrong map. Fix: add text_excludes for a drop on lines 3 to 6 to the three cases, or text_includes of their approve.
6. Outside. Low. PLAUSIBLE: after the land, ruled_refs holds each row twice, source reading and source landed, for lines 2 to 8 (probe 2). A reader that counts rows by ruling counts double. No fix proposed here, the writer _insert_landed_rows (principal.py 3541) decides.

## Point 2, the diff

Added to api.py: _BARE_LIST, _BARE_SEP, _BARE_VERB and _bare_subject, a number-list shape with "and", a comma and "to", and four lines at the end of _subject_lines. _unnamed_contest adds _subject_lines of each sentence to its named set. No word list and no verb read was added. _line_refusal returns None where it returned the agreement refusal, and _faulted_approve is deleted. _account_page_refusal returns None instead of ACCOUNT_NO_LINE.

Deleted tests and what each pinned: test_s212s_approve_of_faulted_lines_is_refused ("The words fault line 6"), test_a_fault_after_the_report_clause_stays_on_this_page ("The words fault line 4, adds"), the _faulted_approve half of test_reading_says_when_the_words_touch_files, test_s274s_reversal_on_line_4_stays_refused and test_s274s_call_with_no_words_meets_the_reversal (REVERSAL), test_a_contest_on_lines_the_words_say_match_is_refused and test_the_refusal_names_only_the_matched_lines_contested (the agreement door), test_words_that_name_no_line_land_on_nothing_on_the_account_page (ACCOUNT_NO_LINE, and the second half of finding 3).

## Point 5, the replay reds

test_frame255_files_correction.py::test_m105_does_not_fault_line_8_and_is_still_refused, test_frame258_request_line.py::test_a_sentence_that_names_line_1_lets_it_be_contested, test_frame193_pass1.py::test_s159s_drop_on_lines_2_to_8_lands_as_contest and ::test_a_phrase_maps_by_its_first_word fail in both trees, 4 failed and 26 passed each.

## (c) Probes

All under C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0ce92518-cd4c-46c5-8db2-374566fad335/scratchpad/p5/, run from the worktree with PYTHONPATH set to it.

- probe1_replay.py: the seat's bare call through fixtures.run_case, then rulings, ruled_refs and line_words.
- probe2_sources.py: source and ruling_id of each ruled_refs row, and delta.writes.
- probe3_receipts.py: the receipts rows and the ruled_refs ids after the replay.
- probe4_line_words.py: line_words on the two sentences of point 4 and two more.
- probe5_remove_word.py: the word remove on lines 7 and 8, and the landed act.
- Inline: the worktree and main register case_runs queries, ARTEFACT_TABLES membership, the three replay files in both trees.

## (d) Usage

About 100k tokens in total, input about 90k and output about 10k, the harness gave no exact split. The cap of 45k was passed. The point 1 trace took most of it.

## p5b: commit 3caf75e4

READY. The five points hold. One red in the named run is older than the commit and is red in main too.

### (a) Verdicts

1. Confirmed. fixtures.capture (rota/testkit/fixtures.py 546-558) selects the ruled_refs rows with source reading whose ruling_id sits in this session's rulings receipts. The diff touches no file under rota/core, and no table list changed.
2. Confirmed. The parametrized test test_remove_on_a_line_that_is_no_code_lands_as_a_drop passes for the three cases, act drop and kind row. _word_shape (api.py 11632-11640) keeps source_line on a code line through guess_item and table_of.
3. Confirmed. test_an_account_note_with_no_line_shows_once_on_the_next_request_page is in tests/rota/test_p9_account_rows.py 153-192 and passes. It pins ACCOUNT_UNNAMED on the first page and its absence on the second.
4. Confirmed by probe. line_words("1 is fine, 2 and 3 are wrong", 3) gives {1: "1 is fine", 2: "2 and 3 are wrong", 3: "2 and 3 are wrong"}. The reversed order "2 and 3 are wrong, 1 is fine" splits the same way. "lines 7 and 8 go, 1 and 2 are fine" binds each pair to its own part.
5. Run with ROTA_L1 unset: 1 failed, 65 passed. The red is test_fixtures.py::test_no_case_leaves_a_reference_unwrapped. Finding 1 explains it.

### (b) Findings

1. tests/rota/cases/l1_liaison2.yaml 347, a bare `item` beside `<item>` in a comment. Low. CONFIRMED: the file is byte-equal at ac900593 and 3caf75e4, the last change is ed7d00a8 of 2026-10-28, and the same test fails in D:/repos/rota. The red is not this commit's. The builder's report calls test_fixtures.py green, and that line is wrong. Fix: write `<item>` in the comment at line 347, in its own commit.
2. rota/roles/api.py _subject_parts, outside. Low. CONFIRMED by probe: "1 is fine, 2 and 3 are wrong, 4 goes" binds lines 2 and 3 to "2 and 3 are wrong, 4 goes" and line 4 to nothing. _BARE_LIST needs two numbers, so a single bare number after a comma starts no part. The parent had the same gap. Fix: let _bare_subject accept a single number after a comma when a verb follows it.

### (c) Probes

Inline, from C:/Users/roman/rota_seam3:

- The named pytest run, then the failing test alone, then the same test in D:/repos/rota.
- python -c with line_words on the two point 4 sentences and three variants, and _subject_parts on two orders.
- git diff ac900593 3caf75e4 on rota/core and tests/rota/cases, and git log on l1_liaison2.yaml.

### (d) Usage

About 22k tokens in total, input about 19k and output about 3k. The harness gave no exact split.
