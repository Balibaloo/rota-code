# Intent down, read from the records of 11 runs, 2026-11-10

Written by one reader for frame 364, mass 2. The reader read the design
pages named in the brief, the 11 state databases read-only, and the
repository copies with read-only git. The reader read no other reader's
page. The scripts are in the scratch directory `mass2/` of session
1efd37b1 (`dbs.py`, `dump.py`, `counts.py`, `ledger.py`).

## Result

1. The 11 databases hold 12 principal messages with no cause, and these are 11 distinct requests (observed: `messages`, `cause_id IS NULL`).
2. Dry run 6b and dry run 6c share one request, and dry run 1 holds two: m1, and m70, which the Principal later called "not new requests" (observed: dry1 e_m75).
3. All 11 requests are read, so no draw is made.
4. Every request became a statement in its own words, and a confirm page put the statement to the Principal (observed: `statements`, `rulings`).
5. In all 8 requests that reached a batch, the request item was approved and the touch note was put before the first batch start (observed: session and message order).
6. Three requests merged (dry1 m1, dry2, dry3), and each merged diff holds test files that the predicted touch does not name and that no `touch_strays` row records (observed: git, `batch_touch`, `touch_strays`).
7. The request item restates the request in 10 of 11 requests, dry6 has no request item at all, and blind1's item adds "displaying an error message" and reached no page (observed: `items`, `messages`).
8. No run holds an `out_of_scope` item, although 8 requests name what must stay as it is (observed: `items.kind`).
9. In 5 of the 8 requests with criteria, a criterion asks for a behaviour that the request does not name, and in 3 of them the Principal dropped it in his own words (reasoned: criteria text against request text; observed: `ruled_refs`).
10. In all 5 fold runs that reached signoff, the touch guess beside the item named parameter.py or property.py, and in 4 the Principal contested it with words that name `_foldline` in string.py (observed: `touch_guesses`, `rulings`).
11. In 4 requests a landed contest or revise left its target row unchanged, for example dry5's c_1 and c_3 after "split at the limit" (observed: `rulings.texts` against `criteria.text`).
12. Before the first batch start, 54 to 206 sessions ran and 6 to 16 pages went to the Principal, and 48% to 81% of those sessions were onboarding wakes (observed: `sessions`; the grouping of wake kinds is reasoned).

## Part A: what the design says intent down is meant to do

Each statement is close to the source words. The check against the
records is in brackets.

1. "The principal's sentence is an entry; the Liaison confirms the statements (`awaiting_confirm`)" (rota/MAP.md:58-59). [An `entries` row by the principal, a `statements` row on it, a confirm page that names it, a landed approve.]
2. "The verbatim words and the confirmed reading are two records. An unchecked inference is never a record." (plans/composition.md:106-107). [Every ratified statement has a landed approve on a page that names it. A statement made from a reply is put to a confirm before a seat uses it.]
3. "Approval of intent is required before work starts." (plans/composition.md:22). [The reply that approves the request item comes before the first `tick:batch_start` session.]
4. "the Vision Keeper asserts items" (rota/MAP.md:59). [A non-description `items` row exists for the request.]
5. The vision_keeper is "Answerable for scope: what is in, what is explicitly out" (rota/ROLES.md:107-108). [Where the request names what must stay as it is, an `out_of_scope` item exists. The test of "names" is reasoned.]
6. "The present page carries the items and the open assumptions" (rota/MAP.md:63-64). [A present page names the request item and the ledger rows about the item that are open at that time.]
7. "a lineage's open assumptions are presented at its gates: nothing ships whose assumptions the principal never saw" (plans/a1-seed-interview-at-intent.md:29-30, law 8 quoted). [For a merged batch, every ledger row about its item, tickets or criteria is named on some page.]
8. "the Terminologist specifies criteria per ticket" (rota/MAP.md:60-61). [Each ticket has at least one criterion that is not retired.]
9. The terminologist "Never decides scope." (rota/ROLES.md:130). [No criterion asks for a behaviour that the request does not name. Reasoned per criterion.]
10. "a criterion must carry a callable surface" (rota/DECISIONS.md:1056). [`criteria.surface_refs` is not empty.]
11. "the Architect groups tickets into a batch (`grouping`) and predicts its touch (`annotate`)" (rota/MAP.md:61-62). [A `batch_tickets` row per ticket and `batch_touch` path rows.]
12. "Before the batch builds, the predicted touch is put to the principal as a sense check" (rota/MAP.md:66-67). [A `tick:touch_note` session and its page come before the first `tick:batch_start` session.]
13. For the touch note, "nothing waits on the answer" (rota/ROLES.md:95). [The first batch start comes before the reply to the touch note.]
14. "A commit that touches paths the prediction never named writes `touch_strays` rows" (rota/MAP.md:73-74). [Each file in the merged diff, or in the batch head diff, that `batch_touch` does not name has a stray row.]
15. "the Architect judges each foreseen or a mistake" (rota/MAP.md:74-75). [No `touch_strays` row is still `open` at the end of the run.]
16. "contest re-derives through `contested`" (rota/MAP.md:65). [After a landed contest or revise on a row, the row has new text, a new version, a `retired_by`, a dropped state, or a ruled guess set.]
17. "An approved item is amended: its text changes under the principal's name." A batch built from it that has not merged "is cancelled", and "The item is re-batched from the new text." (plans/amendment-and-conflicts.md:9-13). [An item version above 1 after a principal ruling, and the state of its batches.]
18. "Nothing is asked twice." (rota/DECISIONS.md:1382). [No two pages in one run have the same verb, the same `body_refs` and the same `body_text`.]
19. "Rota exists so that no work happens that the Principal did not ask for" (plans/composition.md:8-9). [The merged diff changes nothing that the request does not name. Reasoned per hunk.]

## Part B: the requests

### The list and the count

A request is a `messages` row with `from_role='principal'` and
`cause_id IS NULL`. Every other principal row has a cause and is a reply
or a verdict (observed: `messages`; `counts.py`).

| run | principal entries | requests (no cause) | request ids |
|---|---|---|---|
| dry1 | 61 | 2 | m1, m70 |
| dry2 | 18 | 1 | m1 |
| dry3 | 15 | 1 | m1 |
| dry4 | 18 | 1 | m1 |
| dry5 | 19 | 1 | m1 |
| dry6 | 8 | 1 | m1 |
| dry6b | 9 | 1 | m1 |
| dry6c | 20 | 1 | m1, the same row as dry6b m1 in the same database |
| dry7 | 15 | 1 | m1 |
| dry8 | 12 | 1 | m1 |
| blind1 | 4 | 1 | m1 |

12 rows, 11 distinct requests. 11 is 16 or fewer, so all are read.
The short names below are R1 to R11. "Sessions before the first batch
start" counts `sessions.seq` below the first `tick:batch_start`. "Pages"
counts page rows (`to_role='principal'`, verb not `converse`) with a
message seq below the first message that woke a session after that
batch start. No page-sending session falls between the two in any run
(observed: `counts.py`, `tool_calls`).

### R1, dry1 m1 (clickI)

1. Words: "Make click.pause() return True when it waited for a key and False when it skipped because stdin or stdout is not a terminal."
2. Statement s1, the same words, confirmed "ok" on m2 (r_m4). s1 was put again on m8 and on presents m6, m16, m18, m19, and the Principal wrote "ok. I already said ok to this on the first page, and the request has not changed." (r_m11) (observed).
3. Item `click_pause_returns_true_on_key`, the request's words verbatim, final state approved v1 (observed).
4. Criteria on tk_1: `tk_1_criteria_skipped` "When click.pause() skips execution because stdin or stdout is not a terminal (e.g., piped input), it must return False."; `tk_1_criteria_waited` "When click.pause() suspends execution awaiting a keypress from the user, it must return True."; `tk_1_criteria_terminal_check` v2 "The return value is False when raw_terminal reports a non-terminal, and True when execution suspended for a keypress." (observed).
5. Batch bg_1 (tk_1), predicted touch: src/click/termui.py, src/click/testing.py, tests/test_termui.py (observed: `batch_touch`).
6. Signoff m40: "ok" (r_m42). Account m41: "7, 8 and 9 are wrong. The README is not stale, and the code has no bug there. The rest is fine." (r_m43). Touch note m51: "ok" (r_m62), and m59, a copy, "ok" (r_m65). Park page m_park_e8c0: "3 is vague. click.pause() returns False when stdin or stdout is not a terminal, checked with isatty, and True after it waited for a key." (r_m79, rewrite) (observed).
7. No item amendment. The criterion terminal_check rose to v2 after r_m79 (old text in `rulings.texts`). After the merge the notes page m145 drew "I asked for none of these notes. ... Drop every note and build nothing.", and four statements s4 to s7 were cut from the Principal's later replies e_m159 and e_m160, then dropped on confirms m163 and m168 (observed).
8. Merged. Merge commit 09c82f3 in D:/repos/_AI/sample_repos/clickI (reflog HEAD@{0}), head 4fcd6d7 matches `batches.head_commit`. Diff 2c8cd3a..09c82f3: src/click/termui.py, tests/test_termui_tk_1_criteria_skipped.py, tests/test_termui_tk_1_criteria_terminal_check.py, tests/test_termui_tk_1_criteria_waited.py (observed: git).
9. Before the first batch start: 144 sessions, 16 pages. To the end: 311 sessions, 41 pages. The last session that names bg_1 is 270 (observed). The database holds four measures, so these counts cover all four (observed: inventory page; Part E).

### R2, dry1 m70 (clickI)

1. Words: "Write the tests again. The surface is click.pause in src/click/termui.py."
2. Statements s2 "Write the tests again." and s3 "The surface is click.pause in src/click/termui.py.". Confirm m71: "No. Those two sentences were not new requests. Drop both. I was telling you to write the tests for the change you stopped." (r_m75, drop on s2 and s3). Confirm m77 named s2, s3 and `reading:m75`, and the Principal said "ok" (r_m78). Final state of s2 and s3: ratified (observed).
3. Items `write_tests_again` "Write the tests again." (dropped v1) and `surface_is_click_pause` v2 "The surface is click.pause in src/click/termui.py. Drop 1 and 3. They are not requests. I dropped them once already, and the team asked again." (dropped) (observed).
4. No tickets, so no criteria (observed).
5. No batch. Touch guesses: src/click/termui.py, tests/test_termui.py for surface_is_click_pause; tests/test_arguments.py, tests/test_basic.py for write_tests_again (observed).
6. Request-shift page m_shift: "1 now" (r_m73, item park kind `now`). Signoff m90: "Drop 1 and 3. They are not requests. I dropped them once already, and the team asked again." (r_m101). Clarifies m108, m112, m114, answered "Nothing. 'Write the tests again' is dropped. It was never a request.", "Yes. Drop write_tests_again too. Both items are dropped.", "No. Both items are dropped. The team wants nothing from them." Signoff m122: "Drop 1 and 3. They are not requests." (r_m123, drop) (observed).
7. surface_is_click_pause rose to v2 after r_m101 with the Principal's words in its text. No batch existed to cancel (observed).
8. No merge from this request (observed).
9. From the first session that m70 woke (168) to the end: 144 sessions, and 22 pages above message seq 70. Nine of the 22 name the m70 rows or came from the same submit m89: m71, m_shift, m77, m90, m91, m108, m112, m114, m122 (observed).

### R3, dry2 (tipsI)

1. Words: "Make tip_calculator.calculate_tip() raise ValueError when the tip percentage is below 0 or above 100, and return the tip as before otherwise."
2. s1, the same words, confirmed "ok" (r_m5) (observed).
3. Items `raises_value_error_for_invalid_tip_percentage` "The program raises ValueError when the tip percentage is below 0 or above 100." (approved) and `returns_tip_as_before` "The program returns the tip amount as before when the tip percentage is valid." (dropped) (observed).
4. tk_1: c_1 "The program raises a ValueError when the tip percentage is below 0 or above 100.", c_2 "When the tip percentage is valid (between 0 and 100 inclusive), the program returns the calculated tip amount without raising an exception.", c_3 "The ValueError raised for invalid percentages must be a standard Python ValueError with no additional message requirements.". tk_2: c_5 "When input_tip_percentage returns a valid percentage (>= 0 and <= 100), calculate_tip must return the tip amount derived from that percentage.", c_10 "When input_tip_percentage returns a valid percentage, the program must not raise any exceptions or errors.". Every surface names `main.py::calculate_tip` (c_10 adds `main.py::display_results`) (observed).
5. b_1 (tk_1) and b_2 (tk_2), each predicted main.py, tip_calculator.py, tests/test_calculate_tip.py, and b_2 five symbols as possible (observed).
6. Signoff m16 "ok" (r_m18), assumption page m17 "ok" (r_m19), touch note m24 "ok" (r_m36). Clarify m33 on b_2: "As before means what calculate_tip does today: the total times the percentage divided by 100. Nothing to build for it." (r_m37_2, approve on b_2 and tk_2). Present m34: "Line 1 is not a change. The program already returns the tip as before. Drop it." (r_m38, drop). The same words to touch note m25 (reply m39) have no `rulings` row (observed).
7. No amendment. returns_tip_as_before was dropped. b_2 is abandoned. The b_2 wake was quarantined at session 74 before the drop landed (sessions 80 and 82), so the act that set `abandoned` cannot be told (observed: `sessions.wake_detail`).
8. b_1 merged. Merge ff1f65f on tipsI master, head e40742e matches. Diff 99101f1..ff1f65f: main.py, tip_calculator.py, tests/test_calculate_tip_c_1.py, tests/test_calculate_tip_c_2.py, tests/test_calculate_tip_c_3.py. The main.py hunk adds the same check to main.py's own `calculate_tip`. The tip_calculator.py hunk also removes the newline at the end of the file (observed: git diff).
9. Before the first batch start: 54 sessions, 7 pages. To the end: 97 sessions, 10 pages. Last session that names b_1: 62 (observed).

### R4, dry3 (icalendarI)

1. Words: "Make icalendar.caselessdict.canonsort_keys() raise ValueError when canonical_order names the same key twice, and sort the keys as before otherwise."
2. s1, confirmed "ok" (r_m5) (observed).
3. Item `canonical_order_duplicate_keys` "The icalendar.caselessdict.canonsort_keys() method raises ValueError when canonical_order names the same key twice, and sorts the keys as before otherwise." (approved) (observed).
4. tk_1: c1 "The method raises ValueError if canonical_order contains duplicate keys.", c2 "If no duplicates are found in canonical_order, the method returns the sorted keys as before.", c3 "The method sorts the keys as before when no duplicates are found in canonical_order.". Surface `src/icalendar/caselessdict.py::canonsort_keys` (observed).
5. bg_1, predicted src/icalendar/caselessdict.py and the symbol canonsort_keys (observed).
6. Signoff m33 "ok" (r_m34). Clarify m38: "Check before any sort. Raise before sorting." (r_m43, no row). Notes page m39: "Line 2: I do not know this step and I did not ask for it. Drop it. The rest is right." (r_m44). Touch note m40 "ok" (r_m45). Four glossary clarifies came first, m14, m16, m18, m26 (observed).
7. No amendment (observed).
8. Merged. Merge 4f12af1e, read from reflog main@{1} of icalendarI, because main is now reset to 99619246. Head c5e780a5 matches. Diff 99619246..4f12af1e: src/icalendar/caselessdict.py, tests/test_caselessdict.py, tests/test_caselessdict_c1.py, tests/test_caselessdict_sort.py. The caselessdict.py hunk adds the check, a "Raises:" docstring line, and removes the newline at the end of the file (observed: git).
9. Before the first batch start: 179 sessions, 10 pages. To the end: 206 sessions, 10 pages. Last session that names bg_1: 190 (observed).

### R5, dry4 (icalendarI), the fold request

1. Words, the same in R5 to R10: "When icalendar writes a long line, fold it at a space where it can, so that a word is not split, and keep everything else as before."
2. s1, confirmed "ok" (r_m5) (observed).
3. Item `folds_long_lines`, the words verbatim, approved v1. Ticket tk_1 "when icalendar writes a long line, fold it at a space where it can, so that a word is not split" (observed).
4. c1 "... folded by inserting a CRLF followed by a space at a valid word boundary (space or hyphen) ...", c2 "... preserve the original logical content ...", c3 "Lines containing no valid word boundaries (e.g., a single long token with no spaces or hyphens) must not be folded, even if they exceed the length limit.", c4 "... 75 octets per line.", c5 "... ensuring that q_split can correctly reconstruct the original string after parsing.", c7 "The folding operation must handle quoted strings correctly, ensuring that spaces within quotes are preserved and not treated as word boundaries for folding.". All six surfaces name `src/icalendar/parser/parameter.py::q_split` (observed).
5. bg_1 predicted src/icalendar/parser/string.py and 10 test paths. The item guess at signoff was a different set of 26 paths, with parameter.py, property.py and .github/workflows/test_generate_matrix.py, and string.py not among them (observed: `batch_touch`, `touch_guesses`).
6. Signoff m34 "ok" (r_m35). Clarify m39: "Leave it as it is; a change goes ahead where nothing is surveyed." Touch note m40 "ok" (r_m49). Clarify m44: "Only a line longer than the limit the code already uses is folded; a short line stays as it is." (r_m50_2, revise on bg_1). Clarify m46: "The content stays identical and only the fold is inserted, so a reader joins the lines back to the original." Present m57: "Line 8: the fold lives in src/icalendar/parser/string.py, in _foldline, and parameter.py and property.py are not it." (r_m58, contest, exclude property.py). m63 is open at the end (observed).
7. No amendment. bg_1 stays v1 with the same criteria after r_m50_2 and r_m58 (observed).
8. No merge. bg_1 is running. Head 1c452198 (still in the icalendarI object store) changes parameter.py and string.py (observed: git).
9. Before the first batch start: 177 sessions, 9 pages. To the end: 234 sessions, 15 pages (observed).

### R6, dry5 (icalendarI)

1. Words: the fold request. 2. s1, confirmed "ok" (observed).
3. Item `folds_long_lines`, verbatim, approved v1. tk_1 keeps "and keep everything else" (observed).
4. c_1 "When serializing a text value that exceeds the line length limit, the output must be folded at a space character within a word boundary to prevent splitting words.", c_2 "The folding logic must preserve all original characters and formatting, ...", c_3 "Folding must only occur where a space exists within the line; if no suitable space is found before the limit, the behavior follows existing constraints without splitting words.". All surfaces `parameter.py::q_split` (observed).
5. b_1 predicted string.py, tests/test_icalendar.py, symbols `_escape_char`, `_unescape_char` (possible). The guess at signoff named parameter.py and property.py. A ruled set from m38 names string.py and tests/test_icalendar.py (observed).
6. Signoff m36: "Line 2 is wrong. The fold is _foldline in src/icalendar/parser/string.py, and its tests are in src/icalendar/tests/test_icalendar.py. Do not touch parameter.py or property.py." (r_m37, contest on the guess). Clarify m42: "When no space comes before the limit, split at the limit as the code does today. A folded line never passes the limit." (r_m61_2, revise on tk_1, c_1, c_3). Touch note m43: "Do not remove the assert or the escape branch in _foldline. The branch keeps an escape whole across a fold, issue #1501. With both kept, go ahead." (r_m63, approve). Clarifies m47, m65, m68: "Split at the limit, as the code does today. Do not leave a line longer than the limit.", "Use the limit that _foldline has today. Do not change the limit.", "Every content line that icalendar writes.". Present m70: "Line 8 misses the cause. The diff doubles every backslash in _escape_char and _unescape_char, and it drops the escape branch. Undo both, keep the assert, and change only the fold." (r_m73, contest on b_1) (observed).
7. No amendment. c_1 and c_3 keep the text that `rulings.texts` stores as their text at the revise (observed: query on dry5).
8. No merge. b_1 deferred, head 670629b3 changes string.py (observed: git).
9. Before the first batch start: 206 sessions, 10 pages. To the end: 265 sessions, 15 pages (observed).

### R7, dry6 (icalendarI)

1. Words: the fold request. 2. s1, confirmed "ok" (r_m5) (observed).
3. No request item. The deliver m11 from the Liaison to the vision_keeper is `open` with 0 attempts at the end (observed: `messages`).
4-5. No ticket, criterion, batch or guess (observed).
6. Account m4 "ok", the same account again on m12 "ok", clarify m14 on "parameter": "When no space comes before the limit, split at the limit as the code does today. A folded line never passes the limit. Parameters fold like the rest of the line." (observed).
7-8. No amendment, no merge (observed).
9. No batch start. To the end: 89 sessions, of which 18 have `committed=0`, and 4 pages (observed).

### R8, dry6b and dry6c (icalendarI), one database

1. Words: the fold request. 2. s1, confirmed "ok" (observed).
3. Item `folds_long_lines_in_icalendar`, verbatim. It is draft at the end of dry6b and approved v1 at the end of dry6c (observed: both files).
4. tk_1 "fold long lines in iCalendar output at spaces to avoid splitting words". c_1 "The serialized iCalendar output must fold lines at whitespace boundaries without splitting any word.", c_2 "No line in the serialized output may contain a hyphenated word broken across two lines." (retired by r_m54), c_3 "The folding behavior must not alter existing escape sequences or break them across lines.". Surfaces `to_ical` (observed).
5. b_1 predicted string.py and tests/test_icalendar.py. The guess at signoff named property.py and three test paths. No ruled guess set exists (observed).
6. The account page went out four times, m4, m12, m15, m18, each answered "ok". Signoff m26: "Line 2 is wrong. The fold is _foldline in src/icalendar/parser/string.py, ... Do not touch parameter.py or property.py." (r_m27, contest on the guess). Touch note m31 and its copy m38: "Line 5 is wrong. The fold is _foldline ..." (r_m39, r_m41). Clarify m37: "Every content line that icalendar writes. Keep everything else as it is today." (r_m40_2, revise on b_1). Present m53: "Line 4 is not what I asked. Remove it. Line 5 is right: do not remove the assert or the escape branch in _foldline, issue #1501. Its tests are in src/icalendar/tests/test_parsing.py. With both kept, go ahead." (r_m54, drop on c_2) (observed).
7. No amendment. c_2 retired. b_1 stays v1 (observed).
8. No merge. b_1 deferred, head 99619246, which is the base commit (observed).
9. dry6b end: 137 sessions, 5 pages, no batch. dry6c: 151 sessions and 7 pages before the first batch start, 195 sessions and 13 pages to the end (observed).

### R9, dry7 (icalendarI)

1. Words: the fold request. 2. s1, confirmed "ok" (observed).
3. Item `folds_long_lines`, verbatim, approved v1. tk_1 "fold long lines in the icalendar parser at a space where a word is not split" (observed).
4. c1 "The parser must fold long lines at a space character that does not split a word." (q_split), c2 v2 "The parser must invoke _foldline when a line exceeds the limit, ...", c3 v2 "The output of _foldline must preserve all original characters except for the inserted newline ...". Retired by r_m42: c_1 "... preserving the original tokenization of parameter values.", c_2 "The parser must not split parameter values at spaces ...", c_3 "... without altering the semantic meaning of parameters." (observed).
5. b1 predicted string.py, tests/test_icalendar.py, symbol `_foldline`. The guess at signoff named parameter.py with nine symbols. A ruled set from m26 names string.py, tests/test_icalendar.py, `_foldline` (observed).
6. Signoff m22: "Line 2 is wrong. ..." (r_m24, contest on the guess). Touch note m29: "Do not remove that branch in _foldline. Keep everything else as before. The checks on lines 5, 7, 9 and 12 call q_split, and that is the wrong function: the fold is _foldline. Lines 8, 10 and 11 are not my request. I did not ask about parameter values." (r_m42). Clarify m40: "Only the writing. Reading stays as before." Clarify m50: "That test was red before this change. It is not part of my request. Leave it as it is." Present m51: "Try again. The checks on lines 5 and 7 still call q_split with max_length, ..." (r_m56). m61 and a park page are open at the end (observed).
7. No amendment (observed).
8. No merge. b1 deferred, head 21bbe661 changes string.py (observed: git).
9. Before the first batch start: 153 sessions, 6 pages. To the end: 223 sessions, 11 pages (observed).

### R10, dry8 (icalendarI)

1. Words: the fold request. 2. s1, confirmed "ok" (observed).
3. Item `folds_long_lines`, verbatim, approved v1. tk_1 "fold long lines in the _foldline function at src/icalendar/parser/string.py" (observed).
4. c1 "The _foldline function must not split a word at any point; it may only insert a CRLF followed by a space between existing characters.", c2 "... _foldline must first check if the current line ends with an escaped prefix (backslash) and handle it ..." (retired by r_m46), c3 "The function must return a string where every line is at most 75 octets long, excluding the line break.". Surfaces `string.py::_foldline` (observed).
5. bg_1 predicted string.py, tests/test_icalendar.py, symbol `_foldline`. The guess at signoff named parameter.py, property.py and 25 test paths. A ruled set from m26 matches the batch (observed).
6. Signoff m22: "Line 2 is wrong. The code this touches is the function _foldline in src/icalendar/parser/string.py, ... Nothing in parameter.py or property.py changes." (r_m24). Clarify m30: "Fold only a line longer than 75 octets, as the code does today, and keep the line assert "\n" not in line in _foldline." Touch note m31: "Line 4: drop it. I did not ask for escape handling." (r_m46). Clarifies m52, m54, m57, m58 and present m59 are open at the end (observed).
7. No amendment. c2 retired (observed).
8. No merge. bg_1 deferred, head fddff3af in the bg_1 worktree of icalendarI. The head diff changes string.py and adds an `elif` branch that moves a backslash to the next line (observed: git diff).
9. Before the first batch start: 156 sessions, 7 pages. To the end: 199 sessions, 13 pages (observed).

### R11, blind1 (tips copy)

1. Words: "Refuse a negative bill amount, the same way a bad tip percentage is refused."
2. s1, confirmed "ok" (r_m5) (observed).
3. Item `bill_amount_rejection` "The program rejects a negative bill amount in the same way it rejects a bad tip percentage, displaying an error message." (draft) (observed).
4-5. No ticket, criterion or batch. A guess exists for the draft item: main.py, tip_calculator.py, tests/test_calculate_tip_c_1.py, _c_2.py, _c_3.py (observed).
6. Account m4 carried five description items and not the request item. The reply m6: "Line 5 is wrong: today the calculation accepts a negative bill with no error ... Also, what does "nothing is built" mean after 'ok'? I still want the change made." No `rulings` row has ask m4. The Liaison's question m8 stays open, and two replies to it were refused with "m8 is not an open gate" (observed: `rulings`, `seat/exchange.jsonl`).
7-8. No amendment, no merge (observed).
9. No batch start. To the end: 39 sessions, 2 pages (observed).

## Part C: the grid

R1 dry1-m1, R2 dry1-m70, R3 dry2, R4 dry3, R5 dry4, R6 dry5, R7 dry6,
R8 dry6b/6c, R9 dry7, R10 dry8, R11 blind1.

| # | statement, short | holds | does not hold | cannot be told |
|---|---|---|---|---|
| 1 | entry, statements confirmed | 11: all | 0 | 0 |
| 2 | two records, no unchecked inference | 10: all but R2 | 0 | 1: R2 |
| 3 | approval before work | 11: R1,R3,R4,R5,R6,R8,R9,R10; R2,R7,R11 with no batch | 0 | 0 |
| 4 | VK asserts items | 10: all but R7 | 1: R7 | 0 |
| 5 | VK holds what is explicitly out | 0 | 7: R3,R4,R5,R6,R8,R9,R10 | 4: R1,R2,R7,R11 |
| 6 | present carries item and assumptions | 8: R1,R3,R4,R5,R6,R8,R9,R10 | 2: R7,R11 | 1: R2 |
| 7 | nothing ships with unseen assumptions | 0 | 3: R1,R3,R4 | 8: the rest, no merge |
| 8 | criteria per ticket | 8: R1,R3,R4,R5,R6,R8,R9,R10 | 0 | 3: R2,R7,R11 |
| 9 | Terminologist never decides scope | 3: R1,R3,R4 | 5: R5,R6,R8,R9,R10 | 3: R2,R7,R11 |
| 10 | criterion carries a surface | 8: as row 8 | 0 | 3: R2,R7,R11 |
| 11 | batch grouped, touch predicted | 8: as row 8 | 0 | 3: R2,R7,R11 |
| 12 | touch note before build | 8: as row 8 | 0 | 3: R2,R7,R11 |
| 13 | nothing waits on the touch note | 8: as row 8 | 0 | 3: R2,R7,R11 |
| 14 | unpredicted path writes a stray | 4: R5,R6,R9,R10 | 3: R1,R3,R4 | 4: R2,R7,R8,R11 |
| 15 | Architect judges each stray | 1: R6 | 3: R5,R9,R10 | 7: the rest, no stray |
| 16 | contest re-derives | 4: R1,R3,R9,R10 | 4: R2,R5,R6,R8 | 3: R4,R7,R11 |
| 17 | amendment cancels and re-batches | 0 | 0 | 11: no item amended by a ruling of change |
| 18 | nothing asked twice | 7: R2,R4,R6,R7,R9,R10,R11 | 4: R1,R3,R5,R8 | 0 |
| 19 | no work not asked for, merged diff | 1: R1 (reasoned) | 2: R3,R4 (reasoned) | 8: no merge |

Evidence for each "does not hold" cell:

- 4, R7: dry6 `items` holds only `is_description=1` rows, and message m11 (deliver to vision_keeper) is `open` with `attempts=0` at the end.
- 5, R3: dry2 `items.kind` is `in_scope` for all 10 rows. The clause "return the tip as before otherwise" became the in_scope item `returns_tip_as_before` (reasoned: the clause names what stays).
- 5, R4: dry3 no `out_of_scope` row. The clause "sort the keys as before otherwise" is inside the in_scope item (reasoned).
- 5, R5, R6, R8, R9, R10: no `out_of_scope` row in dry4, dry5, dry6c, dry7, dry8. The clause "keep everything else as before" is inside the in_scope item (reasoned).
- 6, R7: dry6 no page names a request item, because no request item exists.
- 6, R11: blind1 m4 `body_refs` name five description items and not `bill_amount_rejection`, and no later present exists.
- 7, R1: dry1 ledger l_4d193465bc (tk_1) and l_fed52da387 (tk_1_criteria_waited) are `parked` and are in no page's `body_refs`. schema.sql defines `parked` as "the row's item merged with the row open. No page shows it".
- 7, R3: dry2 ledger l_41ba388d8a (c_3) and l_afe099fded (c_1), both `parked`, in no page's `body_refs`.
- 7, R4: dry3 ledger l_bd39fdc515 (c1), l_9c1f01a01d (c2), l_038fec553c (c1), all `parked`, in no page's `body_refs`.
- 9, R5: dry4 c3 asks that a line with no boundary "must not be folded, even if they exceed the length limit", c7 asks for quoted-string handling, c1 adds "or hyphen" (reasoned).
- 9, R6: dry5 c_3 decides the no-space case "without splitting words". The Principal ruled the opposite on m42 (r_m61_2) (reasoned).
- 9, R8: dry6c c_2 asks for hyphenated words. The Principal: "Line 4 is not what I asked." (r_m54, ruled_refs act drop on c_2).
- 9, R9: dry7 c_1, c_2, c_3 ask about parameter values. The Principal: "Lines 8, 10 and 11 are not my request." (r_m42).
- 9, R10: dry8 c2 asks for escape handling. The Principal: "I did not ask for escape handling." (r_m46).
- 14, R1: clickI 09c82f3 adds tests/test_termui_tk_1_criteria_*.py (3 files). `batch_touch` for bg_1 names tests/test_termui.py, and dry1 `touch_strays` has 0 rows.
- 14, R3: tipsI ff1f65f adds tests/test_calculate_tip_c_1.py, _c_2.py, _c_3.py. b_1 predicts tests/test_calculate_tip.py, and dry2 `touch_strays` has 0 rows.
- 14, R4: icalendarI 4f12af1e adds tests/test_caselessdict.py, _c1.py, _sort.py. bg_1 predicts caselessdict.py only, and dry3 `touch_strays` has 0 rows.
- 15, R5: dry4 `touch_strays` rows for src/icalendar/parser/parameter.py on 7 commits, and for parameter.py::q_split on 4 commits, are `open`, while the `_foldline` rows of the same commits are `mistake`.
- 15, R9: dry7 stray on commit 3d20a228 (`_foldline`) is `open`, and later commits are judged.
- 15, R10: dry8 stray on commit 67e0b2d0 (`_foldline`) is `open`, and a585c4ea is judged `mistake`.
- 16, R2: dry1 r_m75 drop on s2 and s3. Both statements are `ratified` at the end, and items were cut from them after the drop.
- 16, R5: dry4 r_m50_2 revise and r_m58 contest on bg_1. bg_1 is v1 and its criteria are v1 at the end. No ruled guess set exists.
- 16, R6: dry5 r_m61_2 and r_m62_2 revise c_1 and c_3. `rulings.texts` equals the final `criteria.text` for both.
- 16, R8: dry6c r_m27 contests the guess. `touch_guesses` holds only rows with `ruling_id=''`.
- 18, R1: dry1 pages m2 and m8 (confirm, s1); m6, m16, m18, m19 (present, s1); m7 and m17; m51 and m59; three park pages with the same refs.
- 18, R3: dry2 m25 and m34 have the same verb, refs and text.
- 18, R5: dry4 m40 and m47 have the same verb, refs and text.
- 18, R8: dry6c m31 and m38, and three park pages `m_park_*_b_1` with refs ["b_1"].
- 19, R3: tipsI 99101f1..e40742e changes main.py `calculate_tip`, and the request names tip_calculator.calculate_tip(). The same diff removes the final newline of tip_calculator.py (reasoned).
- 19, R4: icalendarI c5e780a5 removes the final newline after `__all__` in caselessdict.py (reasoned).

| request, at most 12 words | items | restate | add (quote) | not held by any item (quote) | predicted touch | merged diff | both |
|---|---|---|---|---|---|---|---|
| R1 click.pause() returns True after a key, False when skipped | 1 | 1 | none | none | termui.py, testing.py, tests/test_termui.py | termui.py, 3 tests/test_termui_tk_1_*.py | termui.py |
| R2 Write the tests again; surface is click.pause | 2 | 2 | 1: "Drop 1 and 3. They are not requests. I dropped them once already, and the team asked again." | none | no batch | none | none |
| R3 calculate_tip() raises ValueError outside 0 to 100, else as before | 2 | 2 | none | none | main.py, tip_calculator.py, tests/test_calculate_tip.py | main.py, tip_calculator.py, tests/test_calculate_tip_c_1/2/3.py | main.py, tip_calculator.py |
| R4 canonsort_keys() raises ValueError on a duplicate key, else as before | 1 | 1 | none | none | caselessdict.py | caselessdict.py, tests/test_caselessdict.py, _c1.py, _sort.py | caselessdict.py |
| R5 fold long lines at a space, keep everything else (dry4) | 1 | 1 | none | none | string.py and 10 test paths | none, running | none |
| R6 the same (dry5) | 1 | 1 | none | none | string.py, tests/test_icalendar.py | none, deferred | none |
| R7 the same (dry6) | 0 | 0 | none | the whole request | no batch | none | none |
| R8 the same (dry6b/6c) | 1 | 1 | none | none | string.py, tests/test_icalendar.py | none, deferred | none |
| R9 the same (dry7) | 1 | 1 | none | none | string.py, tests/test_icalendar.py | none, deferred | none |
| R10 the same (dry8) | 1 | 1 | none | none | string.py, tests/test_icalendar.py | none, deferred | none |
| R11 refuse a negative bill like a bad tip percentage | 1 | 1 | 1: "displaying an error message" | none | no batch | none | none |

All "restate", "add" and "not held" cells are (reasoned: the item text
against the request text, word by word). An item that restates and adds
counts in both columns.

## Part D: what the grid does not cover

1. Most sessions before the first batch start are onboarding wakes (orient, reconcile, define, survey, term_collision, commitments, reorient, boundary, challenge, frame, blindspot): dry1 90 of 144, dry2 26 of 54, dry3 138 of 179, dry4 140 of 177, dry5 166 of 206, dry6c 111 of 151, dry7 123 of 153, dry8 123 of 156 (observed: `sessions.wake_kind`; the grouping is reasoned).
2. Clarify pages on glossary words that the request does not use come before the request's signoff: dry3 4 (component, alarm, jCal, vFrequency), dry4 4, dry5 5, dry6 1, dry7 2 and dry8 2 (parameter) (observed: clarify `body_refs`).
3. The touch guess beside the item at signoff and the batch's predicted touch are separate sets. In dry4 they share only test paths, and string.py is only in the batch set. In dry6c the batch set names string.py with no ruled guess set behind it (observed: `touch_guesses`, `batch_touch`).
4. Criterion surfaces name functions other than the one in the request or in the Principal's words: dry2 `main.py::calculate_tip` against "tip_calculator.calculate_tip()"; dry4 and dry5 `parameter.py::q_split`; dry7 c1 `q_split` after "q_split is the wrong function"; dry1 terminal_check v2 `raw_terminal` after "checked with isatty" (observed).
5. The Principal's replies became new rows: dry1 s4 to s7 from e_m159 and e_m160, and the item text of surface_is_click_pause v2 holds his reply words (observed: `statements.span_entry`, `items.text`).
6. Two replies landed no ruling: dry2 m39 (to m25) and blind1 m6 (to m4). Two later replies in blind1 were refused at the door (observed: `rulings.ask_id`, `seat/exchange.jsonl`).
7. Tickets drop clauses of the request: dry3, dry4, dry6c, dry7 omit the "as before" clause, dry7 says "in the icalendar parser", and dry8 holds only "fold long lines in the _foldline function at src/icalendar/parser/string.py" (observed: `tickets.text`).
8. The "as before" clause of dry2 got a ticket (tk_2), two criteria and a batch (b_2) with three batch_start sessions (63 to 65), before the Principal said "Nothing to build for it" (observed: `sessions`, `rulings` r_m37_2).
9. Stray rows name a symbol inside a predicted file, with the removal in the note, for example "removal: `assert "\n" not in line`" in dry5 and dry8. dry8's head commit keeps an escape branch after the Principal dropped c2 (observed: `touch_strays`, git diff 99619246..fddff3af; the order of the drop and the commit cannot be told).
10. dry7 keeps live tests for retired criteria: tst_fold_c_1 (c_1) and tst_fold_c_3 (c_3) have `retired_by` NULL and call q_split (observed: `tests`).

## Part E: limits

- No table has a clock. Order comes from `sessions.seq`, `messages.seq` and the message that woke each session. The page counts before a batch start use that link, and a page written by a mechanical path with no session could be misplaced (reasoned).
- The merge point cannot be placed in the session order. The report gives the last session that names the batch (observed: `sessions.wake_refs`).
- No database stores a page's text, except clarify `body_text` and blind1's `exchange.jsonl`. So "Line 8" and similar references cannot be mapped to a row. Two pages with identical rows can still render different text, because `render_page()` reads the rows at call time.
- dry1 holds four measures in one database. The tables do not separate them, and the commit 4fcd6d7 (2026-11-01) is older than its merge 09c82f3 (2026-11-02). The dry1 counts cover all four measures.
- dry6b and dry6c share one database. The copy `dry6b_after_turn4` is the end of dry6b, and the request is counted once.
- Whether m70 in dry1 is a request is a judgement. Rota treated it as one, and the Principal said it was not (observed: e_m75).
- The `-shm` files of all scratch databases carry a 2026-11-10 time, so other readers opened them today. dry6.db has a 1.8 MB `-wal` file newer than the database, and the read-only open includes it. No `ruled_refs` row has `source='backfill'` in any of the 11 databases (observed: query).
- icalendarI main is reset to upstream. dry3's merge comes from the reflog. The worktrees of dry4 to dry7 are gone, and their head commits were read from the object store. clickI and tipsI merges are on their branches now, and a later run could have moved them (reasoned).
- The ledger rows "about the request" are matched by `about_ref` against the request's item, tickets, criteria, batches and s1. A row about another ref can still concern the request.
- The grouping of onboarding wake kinds, the "adds scope" calls on criteria, and the "work not asked for" calls on diff hunks are the reader's judgement.
