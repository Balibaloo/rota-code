# The fold request in dry runs 4, 5, 7 and 8, a read of the code changes, 2026-11-10

One reader wrote this page. It reports what the recorded code changes are. It does not explain why rota is built as it is, and it proposes no change. Every database was opened with `file:<path>?mode=ro`. The git objects are in `D:/repos/_AI/sample_repos/icalendarI` (observed: `config.project_root` of dry8.db). The scripts and their outputs are in `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/1efd37b1-058e-4b19-8ab1-e1a6c654a389/scratchpad/fold/`: `run.py` and `run_out.txt` (the calls of `_foldline`), `d5.py` (the dry5 head in detail), `tj.py` and `reds.py` (the test journal), `att.py` and `att2.py` (the Developer sessions).

## Result

1. No head commit of dry runs 5, 7 and 8 folds a plain long line at a space (observed: `run.py`, inputs "lorem" and "40 words").
2. The dry5 head 670629b3 doubles every backslash in `string.py`, so its fold separator is the five literal characters `\r\n ` and no real line break is written (observed: git diff, `run.py`).
3. The dry7 head 21bbe661 has no `current_chars.append(char)` in the loop of `_foldline`, so it returns an empty string for every input (observed: git, `run.py`).
4. The dry8 head fddff3af has no space search; it keeps the base cut and starts each later piece at a count of 2, so the pieces after the first hold at most 72 octets (observed: git, `run.py`).
5. Only the dry4 head 1c452198 folds at a space, and it breaks the line limit, for example a wire line of 76 octets on the 40-word line (observed: `run.py`).
6. Every stray row on `_foldline` in the four runs records removed lines that a change which folds at a space can keep unchanged (reasoned: code, section "Across the runs").
7. No stray row records the faults that the script shows: the literal separator of dry5, the empty output of dry7 or the shorter window of dry8 (observed: `touch_strays`, reasoned against `run.py`).
8. When woken on a mistake, the dry4 and dry5 Developers landed no write, the dry7 Developers made 8 commits that removed more lines than they put back, and the dry8 Developer put the assert back in its first commit (observed: `turns`, git).
9. Dry5 and dry7 parked on the spent `touch_mistaken` ladder, dry8 parked on two repository test files that its own last commit turned red, and dry4 was still `running` (observed: `sessions`, `batches.status`, `test_run_journal`).
10. Against the dry9 key, every head is wrong, and dry4 is right in part (reasoned: the rule in "The base and the rule").

## The base and the rule

The request, the same in all four runs (observed: `messages` m1 of each database): "When icalendar writes a long line, fold it at a space where it can, so that a word is not split, and keep everything else as before."

Base `_foldline`, `src/icalendar/parser/string.py` lines 119 to 156 at 99619246 (observed: `git show`). Lines 129 and 130 assert a `str` with no `"\n"`. The loop of lines 135 to 151 adds one character at a time and counts its UTF-8 octets (line 136). When the count plus the next character reaches `limit` (line 137, `>= limit`), the piece closes, so a piece holds at most 74 octets at the default 75. Lines 141 to 145 carry a trailing `\` or `^` to the next piece (issue #1501). Lines 146 to 149 close the piece at any character, so on a long line of words the cut lands inside a word: LOREM gives `conval\r\n lis` (observed: `run.py`). Line 156 joins the pieces with `fold_sep = "\r\n "`.

The rule used on this page (reasoned, from `plans/dry9/key.md` fields 2, 3 and 6):

- Right fold: on a line with a space in the window every fold lands at a space, every piece holds at most 74 octets, the base unfold rule `UFOLD` of `content_line.py` line 20 gives back the input, a line with no space still folds, and the asserts, the escape carry, the separator and the signature stay.
- Right in part: the head folds at a space on plain long lines and breaks one of the other conditions.
- Wrong: the head does not fold at a space on a plain long line, or it breaks the output.

The script `run.py` copies only the `FunctionDef` of `_foldline` out of each commit's `string.py` (git show), sets `DEFAULT_ENCODING = "utf-8"`, and calls it. "Wire line" is a part between CRLFs. "Piece" is a part between `"\r\n "` separators. The results below quote `run_out.txt`.

| input | base 99619246 |
|---|---|
| `SUMMARY:Short line` (18 octets) | unchanged |
| LOREM (100 octets) | pieces 74, 26, cut `conval|lis` |
| `DESCRIPTION:` + 40 x `word` (211) | pieces 74, 74, 63, two cuts inside a word |
| `X:` + 200 x `a` (202) | pieces 74, 74, 54 |
| `DESCRIPTION:a b c ` + 150 x `x` (168) | pieces 74, 74, 20 |
| Cyrillic test line (78) | pieces 74, 4 |
| `SUMMARY:` + 60 a, space, 10 x `é`, ` end` (93) | pieces 73, 20, cut inside the `é` run |
| `DESCRIPTION:` + 61 a + `\n` + `after` (80) | pieces 73, 7, the `\` carried |
| `DESCRIPTION:` + 20 x `слово` (231) | pieces 73, 73, 74, 11, two cuts inside a word |
| a line that holds `\r\n ` already | `AssertionError` |

The base round-trips every input that it accepts, and its longest wire line is 75 octets (observed).

## dry run 4 (short form)

- Live criteria c1 to c5 and c7, all v1, every surface `src/icalendar/parser/parameter.py::q_split` (observed: `criteria`). c1: "...folded by inserting a CRLF followed by a space at a valid word boundary (space or hyphen)...". c3: "Lines containing no valid word boundaries ... must not be folded, even if they exceed the length limit."
- Commits (observed: `git log 99619246..1c452198`): 8e706696 "Fold long lines at valid word boundaries (space or hyphen)...", `string.py` +15 -3, a backward search for `" \-"` in the else branch. Then 7fe86f47, edd92b42, 3f27b9e6, 751f67c2, 87071d8b, 4b1c3a3b and 1c452198 change only `parameter.py` (`q_split`, +89 in total).
- Head `_foldline` (lines 146 to 161 at 1c452198): the window searches back for a space, a backslash or a hyphen (`" \-"` is a non-raw string, so it holds `\` too), cuts after it, and sets `byte_count` to the octets of the first carried character only (line 154). Script: LOREM cuts at `Vestibulum \r\n convallis`, 40 words cut at spaces with pieces 72, 75, 64 and a wire line of 76, `a b c` + 150 x cuts at `c ` and leaves a piece of 129, 20 x `слово` gives a piece of 77, no space folds as the base, every input round-trips (observed: `run.py`). Rule: right in part (reasoned).
- Tests: at attempt 8 on 4b1c3a3b, `tst_fold_c1`, `c2`, `c3`, `c5` fail and `tst_fold_c3_fixed` passes. The one repository test (`.github/workflows/test_generate_matrix.py`) passes. No run on 1c452198 (observed: `test_run_journal`).
- Strays: 8 rows `string.py::_foldline` "mistake", one per commit, each "removal: `folded_lines.append("".join(current_chars))` at line 146, `current_chars = []` at line 147, `byte_count = 0` at line 148 The removal of _foldline was not foreseen. The prediction named the file but not the specific definition. The request does not name this behaviour, and no criterion governs this removal." (observed: `touch_strays`). The same three lines stand at lines 159 to 161 of the head with a deeper indent, inside `if not found_boundary:`, and do the same work (observed: git show 1c452198). 11 rows on `parameter.py` stay `open`.
- Woken: s208, s209, s212 (`tick:touch_mistaken`) landed no write; every commit returned "nothing changed", and s208 ended with "The runner discarded the writes that no commit held" (observed: `att2.py`). s213 quarantined, the batch is `running`.
- The Principal: m58 "Line 8: the fold lives in src/icalendar/parser/string.py, in _foldline, and parameter.py and property.py are not it." (observed: `messages`).

## dry run 5

1. Live criteria, all v1, surface `parameter.py::q_split` (observed: `criteria`): c_1 "When serializing a text value that exceeds the line length limit, the output must be folded at a space character within a word boundary to prevent splitting words." c_2 "The folding logic must preserve all original characters and formatting, ensuring no data is lost during the line break insertion process." c_3 "Folding must only occur where a space exists within the line; if no suitable space is found before the limit, the behavior follows existing constraints without splitting words."
2. One commit, 670629b3 "Fix tst_fold_c1 to call _foldline instead of q_split", by s216 (`tick:tests_failing`, attempt 3), `string.py` +60 -49 only (observed: git show --stat). Compact diff (observed: git diff):
   - Every backslash in `_escape_char`, `_unescape_char`, `_escape_string`, `_unescape_string` and their docstrings is doubled, for example `.replace("\\", "\\\\")` becomes `.replace("\\\\", "\\\\\\\\")`.
   - Line 119: `fold_sep: str = "\\r\\n "`. Line 130: `assert "\\n" not in line`. Line 141: `current_chars[-1] in r"\\^"`.
   - Lines 146 to 160: the else branch searches back for `" "`, appends `current_chars[:i]`, keeps `current_chars[i+1:]`, sets `byte_count = 0`, and keeps the old cut under `if not found_space:`.
3. Head `_foldline`: the cut drops the space, and the count restarts at 0 while the carried characters stay. The separator is five literal characters, so the output holds no CRLF (reasoned: text). Script (observed: `run.py`, `d5.py`): LOREM gives one line of 104 octets, `...Vestibulum\\r\\n convallis...`. Between the literal separators the pieces are 67 and 32, and one space is lost. 40 words: pieces 71, 74, 64, two spaces lost. `a b c` + 150 x: a piece of 130. Cyrillic words: a piece of 76, three spaces lost. No-space line: pieces 74, 74, 54 between literal separators. The `\n` escape input raises `AssertionError`, and `"DESCRIPTION:a\nb"` with a real newline is accepted. `_foldline("foobar", limit=4)` is not `"foo\r\n bar"`. No input other than the short line round-trips. Rule: wrong (reasoned).
4. Tests (observed: `tj.py`): base attempts 2 and 3, `tst_fold_c1` fail, c2 and c3 pass. Head attempt 4: c1 fail. Head attempt 5: all three pass, after the tests were re-encoded to v3. The only repository test is `.github/workflows/test_generate_matrix.py`, and it passes at every attempt. The 162 repository test files were not run, so no record shows a repository test at the head. The script shows that `test_fold_line`'s `foobar` assertion fails on this head (reasoned from the `run.py` result).
5. Strays, all on 670629b3, judged by s220 `tick:touch_strayed` (observed: `touch_strays`, `sessions`): `_escape_char`, `_escape_string`, `_unescape_char`, `_unescape_string` "foreseen", and `string.py::_foldline` "mistake" with the note "removal: `assert "\n" not in line` at line 129, `if len(current_chars) > 1 and current_chars[-1] in r"\^":` at line 140 The batch touched the implementation of escape and fold logic, which was foreseen. However, the removal of assert statements and changes to the foldline function were not part of the requested functionality and are considered mistakes."
   - The two removed lines are replaced by lines 130 and 141 with doubled backslashes (observed: head file). Line 141, `in r"\\^"`, tests the same two characters as the base, so it does the same work (reasoned: Python raw strings). Line 130 rejects the two characters `\n` and accepts a real newline, so it does other work (observed: `d5.py`).
   - A fold at a space needs neither line changed (reasoned: the space cut is a new branch beside the escape carry, as the key's reference does).
6. Woken on the mistake (observed: `att.py` on s221, s225, s226). The wake prompt opens: "You were woken by: tick:touch_mistaken / Refs: b_1 / src/icalendar/parser/string.py::_foldline (removal: ...)" with the note above, and the `code.diff` part says "definitions this batch changed that no criterion names: {'src/icalendar/parser/string.py': ['_escape_char', '_unescape_char', '_foldline', '_escape_string', '_unescape_string']}, what that means: the project's tests call these as they were; restore them and add only what the criteria name".
   - s221, 8 turns: 5 whole-file writes, each refused as "not valid Python (unterminated string literal ...)", commits "nothing changed", 2 escalations refused for a bare-string ref.
   - s225, 17 turns: whole-file writes refused (drops `DEFAULT_ENCODING`, not valid Python, `_escape_string` defined twice, quote errors), no commit.
   - s226, 18 turns: the same kinds of refusal, no commit.
   - s227 `tick:exhausted` "the team could not put back code it was not asked to change after 3 attempts", s242 quarantined, s258 `park_ask` (observed: `sessions`).
7. The Principal (observed: `messages`, `t7.log` to `t9.log` beside dry5.db). Each page after the commit opened with "The change removes code that no answer of yours allowed: in _foldline, the line `assert "\n" not in line` and the branch `if len(current_chars) > 1 and current_chars[-1] in r"\^":`."
   - After the three attempts were spent, m63: "Do not remove the assert or the escape branch in _foldline. The branch keeps an escape whole across a fold, issue #1501. With both kept, go ahead."
   - On the park page m70 ("The team gave up: the team could not put back code it was not asked to change after 3 attempts."), m73: "Line 8 misses the cause. The diff doubles every backslash in _escape_char and _unescape_char, and it drops the escape branch. Undo both, keep the assert, and change only the fold."
   - His first claim agrees with the diff. His claim that the diff drops the escape branch disagrees with the head, which keeps the branch with `r"\\^"` (observed: head line 141).
   - After m73, 7 sessions ran, no Developer session, and the last page reads: "Stuck: b_1 stops here. It breaks . A new commit on the change starts it again." (observed: `t9.log`).

## dry run 7

1. Live criteria (observed: `criteria`): c1 v1 `parameter.py::q_split` "The parser must fold long lines at a space character that does not split a word." c2 v2 `string.py::_foldline` "The parser must invoke _foldline when a line exceeds the limit, ensuring the fold occurs only at a valid space that does not split a word." c3 v2 `string.py::_foldline` "The output of _foldline must preserve all original characters except for the inserted newline at the fold point, including any escape sequences handled by _foldline." c_1, c_2, c_3 retired by r_m42.
2. Commits, all `string.py` only (observed: `git show`):
   - 63a1c381 "Fix _foldline to fold only at spaces" (s164, `tests_failing`): removes the escape carry of lines 138 to 145 and the old cut of lines 146 to 149. Adds a forward search for the first `c.isspace()` in the window, cut before it, and `pass` when no space is found.
   - 2d20cc90 "Restore escaped character handling in _foldline" (s191): puts back the line `if len(current_chars) > 1 and current_chars[-1] in r"\^":` with the body `pass`, and moves the space search under `else`.
   - aba4c0a2 (s195) and 40778404 (s196): each removes one blank line before `foldline = ...`.
   - c85fe55f (s202): puts back the three comment lines of issue #1501.
   - 3d20a228 (s204): replaces the branch with `escaped_prefix = current_chars.pop()` ... and then `current_chars = []`, `byte_count = 0` in one block with no condition.
   - 17ed55ce (s204): puts back the 2d20cc90 form, and removes `foldline = deprecate_for_version_8(_foldline)` with its docstring.
   - 49e0fc1a "Restore _foldline definition; removal was a mistake" (s207): removes `current_chars.append(char)`.
   - 21bbe661 "Restore foldline alias per touch_mistaken judgement" (s209): adds `foldline = deprecate_for_version_8(_foldline)` with no docstring and no blank lines.
3. Head `_foldline`, lines 119 to 164 at 21bbe661: the loop only adds to `byte_count`, and no line adds a character to `current_chars`, so `folded_lines` stays empty (reasoned: text). Script: every accepted input gives `''`, and the folded input raises `AssertionError` (observed: `run.py`). The first commit 63a1c381 cuts before the first space of the window and then cuts again on every character, which gives empty pieces, for example 22 folds and 21 empty pieces on LOREM, and a no-space line stays whole at 202 octets (observed: `run.py`). Rule: wrong (reasoned).
4. Tests (observed: `tj.py`): base attempt 2, 5 batch tests fail and 159 of 162 repository files pass. Attempts 9 and 10 (17ed55ce, 49e0fc1a): batch tests error, 161 files error. Head attempt 12: `tst_fold_c1` pass, `tst_fold_c2` pass, `tst_fold_c3` fail, 105 pass, 56 fail and 1 error of 162.
   - 54 repository files are red at the head and green at the base (observed: `reds.py`). Among them are `test_icalendar.py` (`test_fold_line` "assert '' == 'foo'", `test_long_lines`, `test_contentline_class`), `test_parsing.py` (303 failed, the issue 1501 cases), `test_with_doctest.py` (41 failed) and `test_issue_662_component_properties.py` ("ValueError: Found no components where exactly one is required: b'\r\n\r\n\r\n\r\n'").
   - The kept output of 12 of the 54 files shows an empty serialisation. The rest keep only the summary lines (observed: `d7cause.py`). Every content line goes through `_foldline` at `content_line.py` line 288, so the empty return causes all 54 (reasoned).
5. Strays (observed: `touch_strays`; the judging sessions are s190, s192, s205 and s208 by their `wake_detail`):
   - 63a1c381 `_foldline` mistake: "removal: `if len(current_chars) > 1 and current_chars[-1] in r"\^":` at line 140 The removal of the code block that handles escaping and folding of escaped values in _foldline is a mistake. The request and criteria do not mention removing this logic, and it is part of the existing functionality that should be preserved."
   - 2d20cc90, aba4c0a2, 40778404, c85fe55f, 17ed55ce `_foldline` mistake: "removal: `escaped_prefix = current_chars.pop()` at line 141, `folded_lines.append("".join(current_chars))` at line 142, `current_chars = [escaped_prefix]` at line 143, `byte_count = len(escaped_prefix.encode(DEFAULT_ENCODING))` at line 144, `current_chars = []` at line 147, `byte_count = 0` at line 148 The removal of the code in _foldline is a mistake because the request and approved criteria do not ask for this behaviour to be removed. The code was part of the implementation that ensures compatibility with existing clients and avoids splitting escaped values across a folded line boundary."
   - 3d20a228 `_foldline` open: "removal: `if len(current_chars) > 1 and current_chars[-1] in r"\^":` at line 140".
   - 17ed55ce and 49e0fc1a path `string.py` mistake: "removal: `foldline = deprecate_for_version_8(_foldline)` at line 158 The removal of `foldline` is a mistake because the request and approved criteria name the behavior, and the removal was not requested or approved."
   - 49e0fc1a and 21bbe661 `_foldline` mistake: the six lines above plus "`current_chars.append(char)` at line 149 The removal of _foldline and the introduction of the new folding logic aligns with the requirement to fold long lines at a space where a word is not split. The changes are foreseen as they implement the folding logic described in the criteria." The status says "mistake", and the reason text says "foreseen".
   - The rows compare each commit with the base. aba4c0a2 changes one blank line and its row lists the six lines (observed: git show aba4c0a2, row 5).
   - Replacement: at the head the `if` line stands at line 144 with the body `pass`, so the carry of lines 141 to 144 has no line that does its work. `current_chars = []` and `byte_count = 0` have no replacement. `current_chars.append(char)` has no replacement (observed: head file). A fold at a space can keep all seven lines unchanged, and it must keep `current_chars.append(char)` (reasoned: the space cut is a new branch, and without the append no character reaches the output).
6. Woken on the mistakes, 19 `tick:touch_mistaken` sessions s191 to s221 (observed: `att2.py`). Each prompt opens "You were woken by: tick:touch_mistaken / Refs: b1 /" and then the row path, the removal list and the reason, as quoted above. Attempts 2 and 3 add "This is attempt 2 of 3 on this wake. The earlier attempt did not clear this wake, so the same answer will not clear it. Do something the earlier attempt did not."
   - Commits: s191 2d20cc90, s195 aba4c0a2, s196 40778404 (it ended with "The batch is complete."), s202 c85fe55f, s204 3d20a228 and 17ed55ce, s207 49e0fc1a, s209 21bbe661.
   - No commit: s193, s194, s197, s201, s203, s206, s210, s220, s221. Their ends name "nothing changed", "named an act and did not perform it", refused writes, or refused escalations.
   - s217, s218, s219: `LLMUnavailable` "No connection could be made because the target machine actively refused it", `committed = 0`.
   - s222 quarantined, s223 `park_ask` "attempt 12 of 10" (observed: `sessions`).
7. The Principal (observed: `messages`, `t5.log` to `t7c.log` beside dry7.db).
   - After 63a1c381, and before the Architect judged its row, m42: "Do not remove that branch in _foldline. Keep everything else as before. The checks on lines 5, 7, 9 and 12 call q_split, and that is the wrong function: the fold is _foldline. Lines 8, 10 and 11 are not my request. I did not ask about parameter values."
   - After the first loop of wakes, m56: "Try again. The checks on lines 5 and 7 still call q_split with max_length, and q_split is the wrong function. Write the checks against _foldline in src/icalendar/parser/string.py. Do not remove the lines of _foldline that handle an escape."
   - The last pages, m61 and the park page, stay `open`. The park page reads: "The change removes code that no answer of yours allowed: in _foldline, the assignment `escaped_prefix = current_chars.pop()` and the call `folded_lines.append("".join(current_chars))` and the assignment `current_chars = [escaped_prefix]`, and 4 more. / This change stopped. The team tried 12 times, and 1 of its 5 checks still fail." with "The last attempt: tests/test_fold_preserve_chars.py failed: AssertionError: Original characters were not preserved in the folded output." (observed: `t7c.log`). The page shows c1 and c2 as "Passes" on a head that returns an empty string.

## dry run 8

1. Live criteria (observed: `criteria`), both `string.py::_foldline`: c1 "The _foldline function must not split a word at any point; it may only insert a CRLF followed by a space between existing characters." c3 "The function must return a string where every line is at most 75 octets long, excluding the line break." c2 (escape handling) retired by r_m46.
2. Commits, all `string.py` only (observed: `git show`):
   - 67e0b2d0 (s162, `tests_failing`): removes `assert "\n" not in line`.
   - a585c4ea (s164, `message`): adds two comment lines and an `elif current_chars and current_chars[-1] == "\\":` branch that moves a backslash. The first branch already catches a trailing `\` when the piece holds two or more characters, so the new branch runs only on a one-character piece (reasoned: text).
   - 8a8eb07f "Restore removed assert ..." (s198): puts the assert back at line 130 and removes the blank line after it.
   - 4d42947d (s198): adds one comment line.
   - fddff3af "Fix multi-byte UTF-8 folding by accounting for fold separator bytes" (s198): `byte_count = 0` becomes `byte_count = len(fold_sep) - 1`.
3. Head `_foldline`, lines 119 to 163 at fddff3af: the base loop with no space search. After a cut the count starts at 2 for the default separator, so a later piece closes at 72 octets (reasoned: text). Script (observed: `run.py`): LOREM gives the base cut `conval\r\n lis`. 40 words gives pieces 74, 72, 65, one cut inside `wo|rd`, one cut before a space. 20 x `слово` gives pieces 73, 71, 72, 15, two cuts inside a word. The longest wire line on all inputs is 74, and every input round-trips. `_foldline("foobar", limit=4)` gives `'foo\r\n b\r\n a\r\n r'`. Rule: wrong (reasoned: no fold at a space on a plain long line).
4. Tests (observed: `tj.py`, `reds.py`): base attempt 2, `tst_c1` and `tst_c3` fail, 159 of 162 files pass. Attempt 5 on a585c4ea: `tst_c1` passes at the same commit as attempt 4. Head attempt 6: both batch tests pass, 157 of 162 files pass. Two files are red at the head and green at the base:
   - `test_icalendar.py::IcalendarTestCase::test_fold_line`, "assert 'foo\r\n b\r\n a\r\n r' == 'foo\r\n bar'". The head line 156 causes it (reasoned: the script gives the same string).
   - `test_issue_116.py::test_issue_116`, "At index 163 diff: b'\r' != b'0'". The expected bytes hold a fold after 74 octets, and the head folds the second piece 2 octets earlier (reasoned: the key's base section and line 156).
5. Strays (observed: `touch_strays`):
   - 67e0b2d0 `_foldline` open: "removal: `assert "\n" not in line` at line 129".
   - a585c4ea `_foldline` mistake, judged by s197: "removal: `assert "\n" not in line` at line 129 The removal of `assert "\n" not in line` in `_foldline` is a mistake. The principal explicitly stated that this line should remain as it ensures no newline characters are present in the line, aligning with the current behavior and criteria."
   - No row on 8a8eb07f, 4d42947d or fddff3af. The assert stands at line 130 of the head (observed: git show).
   - A fold at a space keeps the assert unchanged (reasoned). In 67e0b2d0 and a585c4ea no other line does its work (observed: diff).
6. Woken on the mistake: s198, 25 turns (observed: `att2.py`, `sess.py`). The prompt opens: "You were woken by: tick:touch_mistaken / Refs: bg_1 / src/icalendar/parser/string.py::_foldline (removal: `assert "\n" not in line` at line 129 ...)" with the reason above, and the `[removed lines]` part lists `-     assert "\n" not in line`.
   - Turn 2: one write of line 129 and a commit, 8a8eb07f.
   - Then the session worked on the red `tst_c3`. Its writes to `test_foldline_75octets.py` were refused, and it committed 4d42947d and fddff3af. 6 writes were refused in all.
   - The session's last write was refused: "start=20, end=32 crosses from one block to another".
   - Before s198, s196 quarantined `tests_failing`. After s198, s199 `park_ask` "bg_1 is parked. The team gave up on: tests_failing for bg_1. It is a note." (observed: `sessions`).
7. The Principal (observed: `messages`, `config` entries, `turns/t5.txt` and `t6_tail.txt`).
   - On m30, whose page opened "The change removes code that no answer of yours allowed: in _foldline, the line `assert "\n" not in line`.", m45: "Fold only a line longer than 75 octets, as the code does today, and keep the line assert "\n" not in line in _foldline."
   - On m31, m46: "Line 4: drop it. I did not ask for escape handling." The Architect's reason on the a585c4ea row cites the principal's words (observed: row 3).
   - The last page m59 stays `open`: "The team stopped work on this change. ... The team gave up: src/icalendar/tests/test_icalendar.py and src/icalendar/tests/test_issue_116.py still fail after 3 attempts: AssertionError: assert 'foo\r\n b\r\n a\r\n r' == 'foo\r\n bar'." The park note `m_park_e65413c486_bg_1` is `answered`.

## Across the runs

| run | head | folds at a space on a plain long line | keeps the line limit | fold reversible | batch tests at the head | repository tests at the head against the base | strays that are removals inside `_foldline` | of those, removals a right fold must make | Architect's judgement | how the batch ended |
|---|---|---|---|---|---|---|---|---|---|---|
| dry4 | 1c452198 | yes | no, a wire line of 76 and of 130 | yes | no run on the head; at 4b1c3a3b 4 fail, 1 pass | 1 file only, pass | 8 rows, 3 lines each | 0 | mistake on all 8 | `running`, touch_mistaken quarantined, no run on the head |
| dry5 | 670629b3 | no, the separator is literal text | no, one line of up to 243 octets | no, spaces lost | 3 of 3 pass, after re-encode | 1 file only, pass; 162 not run | 1 row, 2 lines | 0 | mistake | parked, 3 attempts wrote nothing |
| dry7 | 21bbe661 | no, empty output | no output | no, empty output | c1 pass, c2 pass, c3 fail | 105 of 162 against 159; 54 files red at the head only | 9 rows (8 mistake, 1 open), up to 7 lines | 0 | mistake on 8, open on 1, plus 2 alias rows mistake | parked, "attempt 12 of 10" |
| dry8 | fddff3af | no, the base cut | yes, at most 74 | yes | 2 of 2 pass | 157 of 162 against 159; 2 files red at the head only | 2 rows, 1 line, none on the head | 0 | mistake on 1, open on 1 | parked on `tests_failing`, page open |

The "must make" column is 0 in each run because each removed line can stay as it is beside a new branch that cuts at the last space of the window (reasoned: the key's reference fold, "a cut after the last space of the window with the base rule as fallback", and the base text). The dry4 and dry5 rows record lines that the head keeps in another form: dry4 re-indents the three lines, and dry5 doubles the backslashes (observed: git).

What the records show about where each batch stopped:

1. The code: the dry5 head writes no real fold and drops the space, the dry7 head writes nothing, and the dry8 head cuts as the base with a shorter window, so none of the three folds a plain long line at a space (observed: `run.py`).
2. The code: the dry4 head folds at a space and breaks the line limit, and its later commits went to `parameter.py` (observed: `run.py`, git).
3. The stray rows record only removed lines, and each recorded line can stay unchanged in a fold at a space (reasoned).
4. No stray row and no judgement names the faults that the script shows in the heads, and in dry7 two rows carry the status "mistake" with a reason text that calls the change foreseen (observed: `touch_strays` rows 14 and 15).
5. In dry4 and dry5 the woken Developers landed no write in any attempt, so the mistake stayed in the head and the ladder ran out (observed: `turns`, `sessions`).
6. In dry7 the woken Developers committed 8 times, and the later commits removed the `foldline` alias and then `current_chars.append(char)`, so each commit drew a new mistake row until the cap (observed: git, `touch_strays`).
7. In dry8 the woken Developer put the assert back at once, and its next commit, made against a red batch test, turned two repository test files red (observed: git, `test_run_journal`).
8. So dry5 and dry7 stopped on the mistake ladder, dry8 stopped on repository tests that its last commit broke with no mistake row on the head, and dry4 stopped `running` with no run on its head (observed: `sessions`, `batches`).

## Limits

- The script calls `_foldline` alone. The wire behaviour of `Contentline.to_ical` is reasoned from `content_line.py` line 288, not run.
- Dry4 and dry5 ran 1 repository test file. Whether their heads break the repository's tests is not recorded. The `foobar` result for dry5 is a script result, not a test result.
- In dry7, 12 of the 54 red files show the empty serialisation in the kept output. The cause for the other 42 is reasoned.
- No column records which Architect session judged which stray row. The mapping uses `sessions.wake_detail`. Why the 63a1c381 row names one line while the commit removes eleven is not established.
- The `tests.body` is the newest version. The text of a test at an earlier attempt was not read.
- The dry9 key was written on 2026-11-10 for a later run. This page applies it as a rule. The fold runs did not see it.
- The `-wal` and `-shm` files beside the databases mean that a later write can change what this reader saw.
- No repository test, gate or model ran. The reader did not read `plans/stack.md`, any `meta` page or any `dry*-read-*` page.
