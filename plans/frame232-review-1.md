# Frame 232, review 1: commit 56bfe7c5, the stream stops at the first invented result

Reviewer: a read-only agent on the worktree `C:\Users\roman\rota_rv232` at `56bfe7c5`, 2026-10-13. Meta workflow for this record. The rule under review acts in the rota workflow, in the stream reader of every seat.

Verdict: accept. The stop does what the design and the brief say. Every point holds. Four low findings and no high finding. The gate shows 9 new reds, and all 9 are in the known set.

## (a) The verdict on each point

1. CONFIRMED. The s117#4 shape stops after 6 of 208 chunks, keeps `TOOL: ...` and `OK code.source ->`, and reads `invented_result`. A `TOOL:` line after the `OK` line runs to its end with `done_reason` "stop".
2. CONFIRMED. The runner finds the kept head, runs the call before it, and keeps "wrote its own tool results" first. The second line quotes the regex match, so a partial line reads the same as a whole line. Finding 1 is the one exception.
3. CONFIRMED. Every stop probe reads `invented_result`. Only "length" fires the cut note at `runner.py:3581`.
4. CONFIRMED. The flag changes no case. `line_buf` never holds a newline after the split loop, and each completed line holds none. The stream tests both completed lines and `line_buf`.
5. CONFIRMED. The script runs the real `_consume_stream` in 16-character chunks, not the whole text at once. The chunk size cannot change whether a line stops the stream. The re-run gives 2,572 shortened and 0 unflagged at 16 and at 4 characters.
6. CONFIRMED. Test 2 catches a stop with no `TOOL:` line before the head. Test 3 catches a stop on a `TOOL:` line. Finding 3 names two gaps.
7. CONFIRMED. The invented stop fires first in every mixed shape, and `done_reason` reads one value.
8. CONFIRMED. The worktree gate shows 9 new reds, all known, and `stale (0): none` after one re-record.

## (b) Findings

1. `rota/core/runner.py:3834-3840`. Low. CONFIRMED (observed: probe P2b). The second account line quotes the first head in `scanned`, not the head where the stream stopped. A reply `OK code.write: fine`, then `TOOL: code.source('a.py')`, a blank line and `OK code.source -> [x` stops at line 4. The account says `the stream stopped at the invented result "OK code.write:" on line 1 of the reply`. Rule 1 also cuts at line 1, which is the existing behaviour, so no call changes. Only the account is false.
   Fix: put the stop offset in the stream's result, for example `final["stopped_at"]`, and quote that head. Or word the line "the first invented result".

2. `rota/llm/llm.py:333-341`. Low. CONFIRMED as a mechanism (observed: probe O1), with 0 cases in the register (observed: the re-run of `equiv_impl.py`). The stop has no open-call guard, as brief item 5 rules. A `code.write` whose text holds a line `OK code.source: read fine` is cut inside its argument. The kept text parses as `ToolError ... unterminated argument list`, so the write does not run. On the full text the runner runs that write, because the write starts before the head. A seat that writes a log or a fixture with a result-shaped line loses the write.
   Fix: record this as the known residue of the no-guard ruling. Add the guard if a night shows one case.

3. `tests/rota/test_llm_stream.py:61-107`. Low. CONFIRMED (reasoned: the three tests read). Test 1 covers only the `line_buf` branch, because its head never ends in a newline. No test covers a head on a completed line in the middle of a chunk. No test covers an `OK` head before the first `TOOL:` line in a reply that holds a `TOOL:` line later. Probes P4b and P1b show that both shapes behave correctly today.
   Fix: add a test with the pieces `TOOL: code.source('a.py')` plus a newline, then one chunk `OK code.source -> y`, a newline and a `TOOL: code.write(...)` line, then `never`. Assert 2 chunks pulled and `invented_result`. Add a test with `OK code.source -> x` before a `TOOL:` line, and assert that the stream runs to its end.

4. `rota/core/runner.py:3837`. Low. CONFIRMED (reasoned: `fixtures.py:1262-1265` read). When the head ends in a colon, for example `ERROR tests.run:`, the text before the first colon of the new line holds a dotted op name. `runner.py:4555-4561` says "Never head a line here with a dotted op name". `fixtures.py:1263` then counts a refused call under the key `the stream stopped at the invented result "ERROR tests.run`. The key never equals an op name, so no score changes today. A replay also never gets the line, because `cassettes.py:356-359` and `:408` build the completion with no `raw`. So only a recording run can show it.
   Fix: start the line with a prefix that holds no dot before its first colon, for example `stream stop: the reply invented ...`, or quote the head with its colon stripped.

## Detail on the points

Point 1 (observed: probe P1). The pieces are a `TOOL:` line, a blank line, `OK`, ` code`, `.source`, ` ->`, ` [`, and 200 chunks of `'import click', `. The reader pulls 6 of 208 chunks. The content is the `TOOL:` line, a blank line and `OK code.source ->`, 51 characters. The live view gets `[stopped: the reply wrote a tool result it was not given]`. Probe P1b puts `OK code.source -> x` before a `TOOL:` line. All 8 chunks are pulled, no note is written, and `done_reason` is the server's "stop".

Point 2 (observed: probes P1 and P4b, with the runner's code at `runner.py:3828-3840` applied to the kept text). The account is `['wrote its own tool results', 'the stream stopped at the invented result "OK code.source ->" on line 3 of the reply, so nothing after it was generated']`. The `code.source` call before the head runs. In P4b the chunk that completes the head also holds a `TOOL: code.write` line. That text stays in the content, and rule 1 drops the write. The head is `group(0)` of the regex. So the quote ends at `->` or `:` whether the line is whole or partial. The line number counts newlines up to the first non-space character of the match, so a blank line that the leading whitespace class absorbs does not move the number.

Point 3 (observed: all stop probes). P1, P2b, P4a, P4b, P4c, P7a, P7b, P7d and O1 read `invented_result`. The runner tests only `== "length"` at `runner.py:3581`, and a grep for `done_reason` finds no other reader in `rota/`.

Point 4 (reasoned: `llm.py:329-341`; observed: probes P4a, P4b, P4c). The inner `while` splits at every newline, so a completed line holds no newline, and `line_buf` holds at most one partial line. `.match` anchors at offset 0 with or without `re.MULTILINE`. A chunk with two newlines and then `OK code.source -> [rest` in its middle (P4a) stops on that chunk, and the rest of the chunk stays in the content. A head on a completed line inside a chunk (P4b) breaks the split loop, and the remainder of that chunk stays in the content. An indented `ERROR tests.run:` line after a CRLF `TOOL:` line (P4c) also stops.

Point 5 (observed: `equiv_wt.py`, a copy of `equiv_impl.py` that imports the worktree and reads the worktree's register backup with `mode=ro`). The original script imports `D:/repos/rota` through `sys.path`, so it tests the checkout's code, not the commit. At the time of the implementer's run, the two were the same. The script feeds each completion in 16-character chunks, which is coarser than the server's one token per chunk. The head test is a prefix test, so a line that matches on a prefix also matches whole. The chunk size moves only where the kept text ends, never whether a line stops the stream. The results:

- STEP 16: completions 32,532, shortened 2,572, unflagged 0, same calls 2,571, calls differ 1 (`ee7adee7705a9691a65a18da7c5ba8c6`, the known `l_3aea8c134c` case). 32 s.
- STEP 4: the same four numbers. Shortened by the cycling stop goes from 45 to 70, because finer chunks let the cycling test see a cycle sooner. 43 s.

The register has 22 more completions than the implementer's run, 32,532 against 32,510. The script derives `allowed` from every dotted name in the completion, not from the seat's working set. That is a superset, so the bare-call fallback can see more calls than a seat would see (reasoned).

Point 6 (reasoned: `test_llm_stream.py:61-107`). Test 2 asserts that the regex matches `OK code.write -> done`, that the stream runs to its end, that the content is whole, and that `done_reason` is not `invented_result`. A stop that fires with no `TOOL:` line before the head turns test 2 red. Test 3 asserts that three `TOOL:` lines and `done` run to the end with the content whole. A stop on any `TOOL:` line, the second included, turns test 3 red. Finding 3 names what neither test covers.

Point 7 (observed: probes P7a to P7d). The invented test runs before `_cycling` in each chunk. So:

- A cycle after an invented result (P7a): the stream stops after 2 chunks, `invented_result`.
- A cycle of a `TOOL:` line and a head, three times in one chunk (P7b): `invented_result` after 1 chunk.
- The third cycle line and a head in the same chunk (P7d): `invented_result`, though `last_lines` already held the cycle.
- A cycle of head lines with no `TOOL:` line (P7c): `repeating`, because the flag is never set.

`stopped` holds one string, so `done_reason` always reads one value.

Point 8 (observed: `rv232_gate.out`, 2026-10-13). The checkout's `.rota-gate.json` and a `sqlite3` backup of `tests/rota/cassettes.db` went into the worktree first. The backup matched the source in `cassettes` (32,532) and `case_runs` (390,625), and `pragma quick_check` read ok. The main card was free. The gate re-recorded the 2 stale cases into the worktree's copy: `L1-AR-judge-a-stray-foreseen-or-a-mistake: STALE -> green 5/5, red cleared` and `L3-a-failed-verdict-turns-into-a-fix: FAIL 0/5 -> FAIL 0/5, stale by its failure`. The five lines, with the file prefix of each new red dropped:

```
suite: 32 failed, 3859 passed, 35 skipped, 17 xfailed, 28 warnings (baseline: 24 failed, 3580 passed, 32 skipped, 20 xfailed, 17 warnings)
new reds (9): test_invoke_door::test_a_session_with_no_batch_reads_the_root, L1-AR-a-test-that-misses-its-criterion-gets-a-decision-row, L1-AR-route-an-escalation, L1-DV-apply-the-answer-and-carry-on, L1-TS-encode-a-criterion-the-principal-corrected, L2-DV-name-the-block-rather-than-retry, L2-DV-name-the-deferred-batch-not-the-running-one, test_scene_challenged_again::test_a_second_build_gives_equal_rows_and_lands_a_right_call_per_op, test_scene_two_batches::test_a_right_call_lands[the project test tests/test_templates.py as an encode]
reds gone (1): L1-VK-a-statement-on-an-existing-account-is-a-behaviour
stale (0): none
time: 610.1s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 5d68808 2026-10-11 02:11
```

The gate marked `test_scene_challenged_again` flaky and exited 1 with `9 new reds, 1 of them flaky`. The 9 against the known set: the 2 HEAD reds (`test_invoke_door`, `test_scene_two_batches`), the 2 Architect cases, frame 224's `L1-DV-apply-the-answer-and-carry-on`, frame 204's 2 L2 cases, the flaky scene, and frame 213's `L1-TS-encode-a-criterion-the-principal-corrected`. No red is outside the set. `test_map` and `test_handover` were not red on this run. The re-recorded cassettes are in the worktree's copy only, and they leave with the worktree.

## (c) Probes

All probes are under `C:\Users\roman\AppData\Local\Temp\claude\d--repos-rota\b4070ef8-e7e4-4930-a6a9-73b61f3672a9\scratchpad\`.

- `rv232/probe_stream.py`: runs the worktree's `_consume_stream` on the shapes P1, P1b, P2b, P4a, P4b, P4c, P7a to P7d and O1. It applies the runner's account and rule 1 code to the kept text, and for O1 to the full text too.
- `rv232/equiv_wt.py`: a copy of `f232/equiv_impl.py` with the worktree on `sys.path`, the worktree's register backup opened `mode=ro`, and the chunk size from the command line. It ran at 16 and at 4.
- `pytest tests/rota/test_llm_stream.py` in the worktree: `6 passed in 3.37s`.
- `rv232_gate.out`: `python -m rota.tools.gate` from the worktree, unpiped into the file, 610.1 s.
- Reads: `git show 56bfe7c5`, `llm.py:278-367` and `:440-506`, `runner.py:3560-3600`, `:3770-3860` and `:4550-4566`, `cassettes.py:340-410`, `fixtures.py:1256-1268`, and a grep for `done_reason` over `rota/`.

## (d) Usage

The agent's own estimate: about 75k input tokens, about 14k output tokens, about 90k in total. The harness line is the authority. No sub-agent ran.
