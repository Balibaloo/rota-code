# W11 review, pass 1: commit 5d73ffa1 on w11root

Verdict: NOT READY. The commit stops the s130 crash, and its tests prove it. One high stays: the night print does not show this ending. Four lows follow.

## (a) The verdict on each point

1. Cause: CONFIRMED. The parser gives 9 ToolCall and 1 ToolError in s130 turn 5. The hold step makes the mixed list, so a guard at the hold step is the correct fix. The two `isinstance` checks are copies of the turn loop check (F2).
2. Reach: CONFIRMED. All `.name` reads on a parser list in `rota/core/` and `rota/llm/` are guarded. The probe found no unguarded read.
3. Refusal: PARTLY. The ERROR line has the same form as the turn loop line, and its reason has five words with no rota identifier. The heading of the refusal says the line "ran", and that is false (F4).
4. Record: HIGH. The night print does not count the ending. The builder's claim that the night report reads the SESSION ENDED reason is wrong (F1).
5. Tests: CONFIRMED. At the parent, the s130 test fails with the exact night error. Test 2 checks parts of the refusal text. No test checks the hold note (F5).
6. Gate: NO HIGH. The baseline is in the builder's worktree, and Git ignores it. The probe found no write to a shared file. The baseline compares the run with itself (F6).

Point 1 in detail. The turn loop, `rota/core/runner.py:5543-5553`, is the one reader of "a parsed call is a call". It checks `isinstance(call, toolproto.ToolError)` and then `toolproto.validate`. The hold step at `runner.py:5644-5645` copies `calls[i:]` without that reader. The stand-by guard at `runner.py:5386` and the toolcheck guard at `rota/llm/toolcheck.py:73` are two more copies. The `toolproto` module has no shared predicate.

Point 2 in detail. The guarded reads are at these lines. In `runner.py`: 1577 and 3631 (an `isinstance` filter), 5215, 5527 and 5644 (`getattr`), 5543 (`isinstance` before every later read in the loop), 6497 (`isinstance`), and now 5386. In `rota/llm/toolcheck.py`: 73 (now guarded), and 80 reads native calls only. `rota/llm/cassettes.py:308` reads native calls, which the parser does not make. Outside the two trees, `rota/testkit/fixtures.py:1481` is guarded.

Point 3 in detail. The seat reads this text on its retry turn:
"The calls you stood by ran, and these were refused:" + "ERROR TOOL:` is a literal marker ... write those five characters, th: no function name after TOOL:" + "Answer the refusals with corrected calls, or end."
The turn loop writes `ERROR {raw}: {reason}`, and that is the same form. The parser cuts the raw at 60 characters, in the middle of a word, with a replacement character.

## (b) Findings

1. HIGH. `rota/tools/nightreport.py:688-697` and `:922-929`. CONFIRMED. Probe 5 replayed the s130 shape and ran `nightreport.build` on the database. The print shows only "tester message x1 t=3 c=1". No line names the parse error, the refusal of the held call, or the account turn. The night report uses `RUNNER_PREFIXES` only to remove runner turns from counts. The report prints the last turn for an uncommitted session only. So the W11 ending and every turn-loop parse error are silent after the fix. Before the fix, the failure was visible in the failures section. Fix: add a line to the night print that counts the reasons in the SESSION ENDED account turns, or write a fault row for a held parse error.

2. LOW. `rota/core/runner.py:5644-5645` and `:6000-6004`. CONFIRMED. Probe 4 read the s130 turn 6 prompt. The prompt said "NOT RUN, because you wrote them before the answers above came back: ..., TOOL:` is a literal marker ... th, artefact.verb(key='value'). ... Send them again". The hold step puts the parse error in `held_calls` and in the hold note. Thus the seat gets an instruction to send a line again that is not a call. The stand-by guard protects only the later step. Fix: at the hold step, give each ToolError in `calls[i:]` the turn loop's ERROR line, and hold only ToolCall objects.

3. LOW. `rota/core/runner.py:5495`. PLAUSIBLE. A turn with a call clears `held_calls`. A parse error in the held tail then goes away with no line in `outcome.errors` and no line to the seat. Only the stand-by path reports it, so the report depends on the next turns having no call. Fix: the fix of finding 2 also fixes this finding.

4. LOW. `rota/core/runner.py:5422-5426`. CONFIRMED. Test 2 found the ERROR line under "The calls you stood by ran, and these were refused". A parse error did not run, and the seat did not stand by it. In s130 the line was a copy of the prompt. The correct answer is to remove the line, not to correct it. Fix: the fix of finding 2 removes the line from the stand-by path.

5. LOW. `tests/rota/test_runner_toolerror.py:85-96`. CONFIRMED by a read. The tests check parts of the refusal and of the account turn. No test checks the hold note of turn 2, and no test checks the night print. Fix: check that the turn 2 prompt has no "literal marker" in its NOT RUN line, and check one line of the night print.

6. LOW. `C:/Users/roman/rota_w11/.rota-gate.json`, written 2026-10-28 12:34. CONFIRMED with `ls` and `git check-ignore`. The gate stored its baseline in the builder's worktree. The result "new reds (0)" compares the run with itself. The register is absent, so the replay cases did not run. `D:/repos/rota/.rota-gate.json` (2026-10-24) and `D:/repos/rota/tests/rota/cassettes.db` (06:21) have no change. The `.rota/` files that changed in that time are the files of night 174 and `-shm` files that readers make. Fix: delete the baseline in the worktree, and run the gate in `D:/repos/rota` against its own baseline before the merge.

Outside the points: none at high severity. `tests/rota/test_pins.py::test_with_prompt_keeps_every_pin` fails at the parent as well, so the commit did not cause it.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/2ebac251-aff2-4075-a2e8-ad7f47182931/scratchpad/`.

- `w11_probe2.py`: read the eight turns of s130 from `clickI_night173.db` with `mode=ro`. Turn 8 is the SESSION FAILED line. Turns 6 and 7 have no TOOL line.
- `w11_probe3.py`: parsed each turn with `extract_lenient`. Turn 5 gave 9 ToolCall and 1 ToolError, "no function name after TOOL:", at offset 2939. All the calls are a copy of the working-set list in the prompt.
- `w11_probe4.py`: printed the raw of the ToolError (60 characters) and the NOT RUN note of turn 6.
- `w11_probe5.py`: replayed the s130 shape with the fixture of the test, then ran `nightreport.build`. No line names the parse error.
- `w11_parent/`: the parent 8c71b473 from `git archive`, with the new test file added. The result was 3 failed and 1 passed. The s130 test fails with `AttributeError("'ToolError' object has no attribute 'name'")`, and the toolcheck test fails at `toolcheck.py:72`.
- In the worktree, `test_runner_toolerror.py` gave 4 passed. The 54 files that name `run_session` or `toolcheck` gave 1584 passed and 1 failed. The failure is the known red `test_pins`, which fails at the parent too.

## (d) Usage

Input tokens: about 75k in context. Output tokens: about 9k. Total: about 84k. The work went past the 40k cap because of the parent replay and the night report probe.

## p2

Verdict: READY. Commit f47bd1e0 closes the p1 high and p1 findings 2 to 5. Two lows stay, and neither stops the merge.

### (a) The verdict on each point

1. The high: CLOSED. The night print now shows the s130 shape in the failures section. The probe quotes the line under finding p2-1. On the real night 173, the line counts 155 sessions, so it cannot find the W11 ending by kind (p2-1).
2. One reader: CONFIRMED. `_parse_refusal` at `rota/core/runner.py:6485` answers the parse errors of the turn loop (5534) and of the hold step (5644). The hold step holds real calls only. With the real s130 turn 5, the turn 6 NOT RUN line lists the five held calls and `artefact.verb(key='value')`, and no parse error. The parse error comes in its own ERROR line on that turn.
3. The lost error: CONFIRMED. When a parse error in turn 1 is followed by a real call in turn 2, the error goes in `outcome.errors` and in the SESSION ENDED account as "- no function name after TOOL:".
4. The toolcheck guard: LIVE, so it is not a finding. The runner does not call `toolcheck.check`. The `rota cli toolcheck` command at `rota/cli.py:620` calls it on a reply from a live model. The guard protects that path, and `test_toolcheck_reads_past_a_tool_error` tests it.
5. Tests: CONFIRMED. `test_runner_toolerror.py` gives 7 passed. The 58 files that name `_parse_refusal`, `run_session` or `nightreport` give 1679 passed and 1 failed. The failure is the known red `test_pins`, which also fails at the parent.

### (b) Findings

p2-1. LOW. `rota/tools/nightreport.py:931-948`. CONFIRMED. Probe A printed "committed sessions that ended with refusals in the runner's account: 1, 7 lines, the most common 1x: artefact.verb (held): ...". Probe C, on `clickI_night173.db`, printed "155, 897 lines, the most common 71x: repeat refused: code.source asked three times ...". The line includes nearly every committed session, so a W11 ending stays hidden in a real night. Fix: count the account lines by mechanism with `rota/tools/triage.py` `mechanism()`, and print the count for "parse".

p2-2. LOW, outside the points. `rota/core/runner.py`, the `invented_tail` list in the turn loop (about line 5525). PLAUSIBLE. That list copies `c.raw` for each item in `calls[i:]`, and parse errors are included. The seat then reads a parse error as a call under "NOT RUN, because you wrote a tool result", and no reason goes to `outcome.errors`. This is the same defect as p1 finding 2, on the path for an invented result. Fix: answer each ToolError in that tail with `_parse_refusal`, as the hold step does.

### (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/2ebac251-aff2-4075-a2e8-ad7f47182931/scratchpad/w11_p2_probe.py`. It has three parts:
  - A: the test fixture with the real s130 turn 5 from `clickI_night173.db` (`mode=ro`), then prose turns. A prints the turn 2 NOT RUN line, the ERROR lines and the night print line. No session failed.
  - B: the parse error of `TURN_5`, then `TOOL: criteria.load(batch_id='bg_1')`. B prints `outcome.errors` and the account turn.
  - C: `nightreport.build` on `clickI_night173.db`, opened with `open_ro`.
- The pytest runs at f47bd1e0 are in (a) point 5.

### (d) Usage

Input tokens: about 20k in context for p2. Output tokens: about 4k. Total: about 24k.

## p3

Verdict: READY. Commit b6625bb8 closes p2-1 and p2-2. One low remains outside the points. The parser causes it, and the commit did not add it.

### (a) The verdict on each point

1. p2-1: CLOSED. On `clickI_night173.db`, the failures line reads "committed sessions that ended with refusals in the runner's account: 155, 897 lines, parse errors 18 lines in 14 sessions". So the print now shows the parse endings beside the total of 155.
2. p2-2: CLOSED. A reply had a real call, an invented `OK` result, a parse error and a real call. The parse error got its ERROR line, and the reason went to `outcome.errors`. The NOT RUN note named only `tests.consult()`.
3. Tests: CONFIRMED. `test_runner_toolerror.py` gives 8 passed. The 10 files that name `_parse_refusal` or `nightreport` give 240 passed and 1 skipped.

### (b) Findings

p3-1. LOW, outside the points. `rota/llm/toolproto.py`, the parser's ToolError for a line with no function name. CONFIRMED. The probe line "TOOL: `x`" gave a ToolError with the raw text "TOOL: `x`" + newline + "TOOL: tests.consult()". So the seat's ERROR line also quotes the next real call. The turn loop has the same behaviour, so W11 did not add it. Fix: cut the raw text of a ToolError at its first newline.

### (c) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/2ebac251-aff2-4075-a2e8-ad7f47182931/scratchpad/w11_p3_probe.py` has two parts:
  - A run of the test fixture with an invented-result reply. The probe prints the ERROR line, the NOT RUN note and `outcome.errors`.
  - `nightreport.build` on `clickI_night173.db`, opened with `open_ro`.
- The pytest runs at b6625bb8 are in (a) point 3.

### (d) Usage

Input tokens: about 10k in context for p3. Output tokens: about 3k. Total: about 13k.
