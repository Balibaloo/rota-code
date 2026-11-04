# Frame 362, dry run 5, walls 10 and 11: the provenance read, 2026-11-04

## 1. Result

- **Wall 10.** The Developer s216, not s207, retyped the whole 289-line `string.py` as one quoted call argument. It wrote four backslashes for each backslash of the source, so the file holds two (observed: s216 turn 6 completion; probe `p_parse.py`, rota's own parser gives a text equal to the 670629b3 file, 9,517 characters). The parser did its job. No check in the write door compares the written text against the text the seat read (observed: `rota/roles/api.py:23104-24756`).
- **Why a whole file.** The rewrite refusal at s216 seq 14 offered "write the whole file" first. It did not offer the span 118 to 156 that the seat had just read (observed: `api.py:24507-24515`, s216 seq 14 to 16). The span write at seq 14 had the correct escape level (observed: s216 turn 4 completion).
- **Wall 11.** The pass hold asks "Does the diff keep that line", and every witness line is kept, so the true answer is yes. The break sits on lines 119 and 130, the fold separator and the assert, and no witness names them (observed: s244 turn 3 hold; 670629b3 line 140 is still the issue 1501 comment).
- **Upstream.** Wall 10 is upstream of the issue 1501 break only. The fold change alone, with the escapes undone, keeps the 1501 behaviour but gives a 76-octet line and drops 5 characters (observed: `p_fold2.py`). So wall 11 is not wholly downstream of wall 10.
- **Fix 1, wall 10, at the write door.** Refuse a write in which 3 or more added lines equal removed lines once each doubled backslash is halved, and name those lines. On 670629b3, 43 of 60 added lines meet the test (observed: `p_check.py`). Reach: icalendar 76 of 258 Python files, click 51 of 82, tips 0 of 6. A second line: the rewrite refusal names the definition's span before the whole file.
- **Fix 2, wall 11, at the harness.** Run the repository's own tests of the touched definition. `code.probe` already lists the two issue 1501 tests of `_foldline`, and both fail on 670629b3 (reasoned: `p_fold.py`, the folded output holds no CR LF space, and the first assert of each test asks for one). The inherited test was `.github/workflows/test_generate_matrix.py`, which is wall 9. So fix 2 is the repair of wall 9's test choice. Reach: every pushed commitment whose behaviour sits on code beside a kept witness, 2 of the 14 pushed in this run.

Six premises of the brief do not hold, each with its record:

1. s207 wrote no code. It logged "no code change is needed" and committed (observed: `tool_calls` s207 seq 16, 17). The writer is s216, `tick:tests_failing`, seq 16, commit 670629b3 at seq 21.
2. The issue 1501 branch is not removed. Its condition now reads a raw string of two backslashes and a caret, which holds the same characters (observed: 670629b3 line 141; `p_fold.py`, the escape stays whole). The "removal" is the text of the `touch_strays` note, which reads every changed line as removed (observed: `touch_strays`, row `_foldline`, status `mistake`).
3. `cw_41e48f82e948` is not the 75-octet row. It is "The description must state that the package is RFC 5545 compatible.", witness `pyproject.toml` line 42 (observed: s243 turn 1 block). The 75-octet rows are `cw_99502ef494ad` and `cw_4465e7c69f00`.
4. The push carried 14 commitments, not 2 (observed: the hold lists 14 ids, s244 turn 3).
5. s251 sent 14 `verdicts.rule` calls, and 1 landed (observed: s251 turns). The 12 landed dismissals come from 12 sessions, s245 to s257, one finding each (observed: `finding_rulings`).
6. The hold fired in s244, not s243. s243 never landed a pass (observed: s243 turns 2 to 5).

## 2. Wall 10

**Point 1. What the model read, in what form, and what it wrote.**

- s207, `tick:batch_start`, read `string.py` by `code.source` 7 times and the test file 3 times. It wrote a ledger default and an empty commit (observed: `tool_calls` s207 seq 1 to 17).
- s216, `tick:tests_failing`, read `string.py` lines 118 to 156 at seq 12. The tool result shows the source as plain text under a `[text]` header (observed: s216 turn 5 user). The pre-run block of the same prompt shows `q_split` as a JSON string with escaped quotes and newlines (observed: s216 turn 5 user, `[code.source]`). So one prompt holds the source in two forms.
- Seq 14: a span write, start 118, end -1, as a double-quoted argument with two backslashes per source backslash. That is the correct level (observed: s216 turn 4 completion). The door refused it because the span to the end of the file drops `_unescape_string` and `validate_token`.
- Seq 15: `code.source` of lines 0 to 289, plain text again.
- Seq 16: a whole-file write as a triple-quoted argument, 10,347 characters, with 102 runs of four backslashes (observed: `p_parse.py`). Rota's parser stored it unchanged, and the file at 670629b3 equals it.
- Effect: 46 of the 51 base lines that hold a backslash changed, and 236 of the 238 lines without one stayed (observed: `p_parse.py`). Four lines of the `_escape_string` docstring lost their backslash instead.
- Behaviour on 670629b3: the fold separator default is the literal text of a backslash, r, backslash, n and a space. So no line folds. The assert now refuses any line that holds an escaped newline, and `_escape_char` writes two backslashes for one (observed: `p_fold.py`).

**Point 2. The door and its checks.** `code.write` (`api.py:23021`) calls `_code_write` (`api.py:23104-24756`). The checks on the path are these (observed):

- `_refuse_after_challenge`, the span boundary guards and the docstring guard.
- The parse check. On a parse failure it adds `_escape_note` (`api.py:24005`, `api.py:27963-27993`).
- One name, one definition.
- The rewrite refusal for dropped definitions (`api.py:24497-24515`).

No check reads the escape level of the written text against the read text. A grep of the door for backslash and escape finds only the docstring-words guard (`api.py:23744`) and the note (`api.py:24005`). The write parsed as valid Python, so no check fired. `sandbox.py:1064` `_quote_forms` reads the escape level of a quote in a message, not of a write. The only later check is the removal note that `code.commit` writes to `touch_strays`, which the Architect judged a mistake (`predicates.py:2611-2659`). That check acts after the commit (observed: `touch_strays` rows).

**Point 3. The records.**

- `plans/operating-facts.md` holds no entry on backslash or escaped text (observed: grep).
- `plans/wall-guide.md` names no backslash cause. The nearest is cause 4, "The prompt holds the fact in a shape the seat does not read" (`wall-guide.md:279`), with "A failure line sits inside an escaped JSON string" (`wall-guide.md:286-287`). That is the read side, not the write side.
- Rota-side record 1, night 99, 2026-09-30: the Developer wrote the newline escape as one escape, and the decoder made it a line break (`plans/stack.md:3690-3698`). The repair is `_escape_note`, which tells the seat to write the doubled form (`api.py:27974-27979`).
- Rota-side record 2, sprint 25, 2026-10-26, night 168: W1 and W2, a Tester body lost one escape level. Candidate C2 is "the call's escape level of a body" (`stack.md:455-462`, `stack.md:485-487`, `stack.md:564`).
- Wall 10 is the same class in the other direction: one level too many. `_escape_note` fired in s221, s225 and s226, after the wall, and not in s216 (observed: `p_note2.py`).

**Point 4. Reach.** Counted with `git grep -l -F` on one backslash (observed):

| Tree | Commit | Python files | Files with a backslash |
|---|---|---|---|
| icalendarI | 99619246 | 258 | 76, 461 lines; 22 under `src/icalendar` outside the tests |
| clickI | 09c82f3 | 82 | 51 |
| tipsI | ff1f65f | 6 | 0 |

The exposure is a long retype. A whole-file write or a long span carries the risk, and the rewrite refusal sends the seat to the whole file (reasoned).

**Point 5. Unbuilt solutions.** No frame heading in `plans/stack.md` holds "backslash", "code.write" or "the write door". Frame 158 (`stack.md:3066`) is a test's non-raw string, an instrument, and does not apply. Frames 270, 194 and 146 are write doors on other faults. The match is sprint 25's candidate C2, the call's escape level of a body (`stack.md:485-487`, `stack.md:564`). C2 is scoped to `tests.encode`. Built in the shared argument path, it would cover `code.write` too (reasoned).

**Point 6. The fix the evidence supports: the write door.** The source reached the seat in the plain form, and the seat's span write at the same level was right (observed: s216 turns 4 and 5). The fault came with the long retype, so the shown form is not the cause (reasoned). The fix has two lines:

1. In `_code_write`, refuse a write when 3 or more added lines equal removed lines once each doubled backslash is halved. Say the converse for one level too few. Name the lines and the level. On 670629b3 the test meets 43 of 60 added lines, and the fold edit's own lines meet none (observed: `p_check.py`). The converse covers night 99 and C2's W2.
2. In the rewrite refusal (`api.py:24507`), name the span of the definition the seat read before "the whole file". Here that is start 118, end 156, from the `defs` map that `code.source` already prints.

## 3. Wall 11

**Point 1. The first user turn of s243, and the hold.** The turn holds, in order:

1. The wake line.
2. `criteria.load`.
3. `[the constraints that bind the files of this batch]`, one JSON list of 14 rows with id, headline, text, party, behaviour and witness.
4. `tests.load`.
5. `code.read` with `[removed lines]` and `[diff]`.

The block comes before the diff, and turn 1 asks no question per commitment (observed: s243 turn 1). s243 never reached the hold. Its three passes were refused for a four-line unit on `c_2`, and the session ended on a repeat (observed: s243 turns 2 to 5). The hold fired in s244 turn 3, after the pass of turn 2, and asked 14 commitments in one block of 3,744 characters (observed: `p_hold.py`). Its question for `cw_f0bc828192c0`:

> Commitment cw_f0bc828192c0 rests on src/icalendar/parser/string.py line 140: "# escapes across a folded line boundary. See issue #1501.". Does the diff keep that line and "escaped sequences are not split across folded line boundaries"? Say which in your own words, and in the same reply send the pass again or your own fail on the criterion or the commitment.

The seat answered that every commitment rests on an untouched file except `cw_99502ef494ad`, and that its line 122 is kept. It skipped `cw_f0bc828192c0`, and the pass landed at turn 4 (observed: s244 turn 3 completion, turn 4).

**Point 2. The dismissals.** s251 sent 14 calls. 1 landed on `fnd_4`, 11 were refused as "not the finding you were woken about", and 2 were repeats (observed: s251 turns). The 12 landed rulings, by reason (observed: `finding_rulings`):

| Group | Findings | Sessions | Reason |
|---|---|---|---|
| A, the escape change read as a fix | fnd_1, fnd_3, fnd_10, fnd_12, fnd_6 | s245, s250, s246, s248, s254 | "fixes a logic error in string escaping". For `fnd_10`: "correctly reflects the constraint that escaped sequences are not split" |
| B, the witness file is not in the diff | fnd_2, fnd_4, fnd_7, fnd_8, fnd_9 | s249, s251, s255, s256, s257 | the witness is in `pyproject.toml`, the docs or the timezone module. Correct for these five |
| C, the challenge verdict decides | fnd_11, fnd_5 | s247, s252 | "stands" or "unfounded" |

s222 filed the 12 findings with `findings.find` (observed: `tool_calls`).

**Point 3. The case against the run.**

| Item | The case | The run |
|---|---|---|
| Diff | 1 changed number, 72 to 80 | 60 added lines, 43 of them escape copies |
| Commitments pushed | 1 | 14 |
| Witness line | the changed line | a comment, kept |
| True answer to "Does the diff keep that line" | no | yes |
| Criteria | passed by a line | passed by `test:` on tests that call `q_split`, so no criterion line was held |

The hold reached the seat after its first judgement in both (observed: s244 turns 2 and 3; gate 4 report, section (d) point 2). In the run the timing is not decisive. The question names the wrong line, so even a seat that answers it before any judgement answers yes (reasoned). The case's rate: 1 of 5 at gate 4 (`f362_gate4_report.md:41`), then measured green live after pass 4b (`stack.md`, frame 362, status 2026-11-04 07:40). The run is 0 of 1.

**Point 4. The `verdicts.rule` door** (`api.py:18891-18930`) checks four things: the wake names the finding, the ruling is a ruling word, the reason is not empty, and the finding exists. It reads no diff, no witness and no commitment (observed). The fail route checks that the id was pushed and that the witness is not `LOST_WITNESS` (`_pushed_commitment`, `api.py:17491-17509`). `_commitment_reason` adds the witness quote (`api.py:17512-17525`). A dismissal check could reuse the lost-witness test. In this run it would refuse nothing. Line 140 and line 122 are kept at 670629b3, and the other 10 witnesses are in files the diff does not touch (observed). So no existing check, and no reuse of the fail route's check, could refuse the `fnd_10` dismissal (reasoned).

**Point 5. Downstream, reach and the fix.**

- For `cw_f0bc828192c0`, yes, it is downstream. Only the doubled fold separator breaks the 1501 behaviour. The fold change alone keeps it (observed: `p_fold2.py`).
- For the 75-octet rows, no. The fold change alone gives a 76-octet line and loses 5 characters (observed: `p_fold2.py`). Their witnesses are a docstring line and a doc line, both kept, so the hold's question again has the answer yes.
- So a readable diff gives the Critic a chance only when the witness is the changed line. The case at its threshold has that shape, and the run at 0 of 1 does not (reasoned).
- The general fix is at the harness, as in section 1, fix 2. The index already maps `_foldline` to `test_parsing.py` lines 166 to 177 and 180 to 193 (observed: s216 seq 9, `code.probe`). The run used `.github/workflows/test_generate_matrix.py` as `inh_7e3e30b6` instead.
- A door-side second line: the hold quotes the changed lines inside the definition that holds the witness, beside the behaviour, and asks about them. In this run that reaches 2 of 14 pushed commitments, the two witnesses in `string.py` (observed: the hold text).

## 4. Outside the points

- **O1, high, PLAUSIBLE.** `_escape_note` (`api.py:27977-27979`) tells the seat to write the doubled newline escape. It fired in the three restore sessions, s221, s225 and s226, and none of their 10 parsed writes equals the base (observed: `p_note2.py`, `p_restore.py`). This plausibly feeds wall 12. Fix: a restore door that takes the base span from git, so the seat does not retype it.
- **O2, low, CONFIRMED.** The `verdicts.emit` refusal lists added lines with `repr` (`api.py:18502`). So the Critic reads each backslash doubled once more than the file holds (observed: s243 turn 3). Fix: list the lines as plain text.
- **O3, low, CONFIRMED.** The Critic claimed that the three tests encode `c_1` to `c_3`, and each test calls `q_split`, not `_foldline` (observed: s243 and s244 `verdicts.claim_encodes`, the test bodies). This belongs with walls 7 and 9.

## 5. Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/9f60e445-30b5-431b-b448-1ab48919fbaf/scratchpad`. Each opens `dry5/runs/dry5.db` with a `mode=ro` URI, or reads git objects of icalendarI.

- `p_schema.py`, `p_writes2.py`: the tables and the Developer's writing calls.
- `p_s207.py`: dumps of s207 and s216 to `w10_s207.txt` and `w10_s216.txt`.
- `p_parse.py`: rota's `toolproto.extract_lenient` on s216 turn 6, compared to 670629b3.
- `p_fold.py`, `p_fold2.py`: run `_foldline` and `_escape_char` of the base and of the batch, and of the batch with the escapes undone.
- `p_check.py`: the doubled-line test on the diff.
- `p_note2.py`, `p_restore.py`: the escape note's sessions and the restore writes.
- `p_w11.py`, `p_s244.py`, `p_hold.py`, `p_s251.py`, `p_find.py`, `p_reasons.py`, `p_strays.py`: the Critic sessions, the hold, the findings, the rulings and `touch_strays`.
- `git grep -l -F` counts in icalendarI, clickI and tipsI. `git diff 99619246 670629b3` is saved to `w10_diff.txt`.

## 6. Usage against the cap

The cap was about 70k. This read used about 130k input tokens of context and about 16k output tokens, about 146k in total. That is over the cap. The extra came from reading the s216 transcripts and the hold text in full.
