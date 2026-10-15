# Frame 250, review 1: pass 1 at f0b2924c

Verdict: accept with one fix before night 150. The present door does what the frame names, and the counts reproduce. One high finding: the batch-line guard leaves a wrong approve of an open built batch line. Six low findings. Reviewed on the worktree `C:/Users/roman/rota_r250` at f0b2924c, 2026-10-16.

## (a) Verdicts on the points

1. PASS with one low. The door refuses a faulted approve with each line and its cue. The contest door is unchanged. The rerun gives 5 of 177: 4 wrong approves and 1 right one (m86). On m86 the words land, but only on a contest or revise of line 2, which he did not fault (finding 2).
2. PASS with one high. The batch guard also spares an open built batch line, and night 145's m245 line 6 lands wrong (finding 1). The line-1 guard spares m164 only. Night 136's m85 tests prove the third guard: 3 of them go red with the guard off. The third guard also spares a check fault on any page with a batch line (finding 5).
3. PASS. m92 says "Lines 2 through 7 still say confirm raises a usage error", so the approve of lines 4, 6 and 7 is refused by m92's words. With `M92_MAP`, the frame 255 door admits the bg_2 contest, and both tests pass.
4. PASS. The rerun gives 6 of 9 and 40 of 69. The three spot reads, 144 m43, 144 m55 and 146 m84, are right approves.
5. PASS. `_ref_lines` takes `re.I`. `_WORDS_FAULT` takes "through" and "-". The `_unnamed_contest` docstring names the merged or abandoned case. Frame 256's review finding 2, "line 3 through line 5", stays open and was not named.
6. PASS with one low. At d3340828 the new file gives 5 failed, 8 passed, 1 xfailed, each red for its named reason. At f0b2924c the file gives 13 passed, 1 xfailed. m81 fails by "DID NOT RAISE", as its reason says. The xfail takes any error (finding 6).
7. Night 150's read counts two lines:
   - Present and confirm verdicts with words and an approve: the door fires a of n, each fire labelled right or wrong, and each landed approve of a faulted line labelled as a miss, batch lines included.
   - After each refusal, the seat's next call: a contest that lands his words whole, or a call that trims the words or contests a line he did not fault.

## (b) Findings

1. `rota/roles/api.py:8581` (`_faulted_approve`, `n not in batch_lines`). Severity high. CONFIRMED. The guard spares every batch line, but frame 255 refuses only a ruling on a merged or abandoned batch line. An approve of an open batch line that the words fault therefore lands, and no door reads it. Night 145's m245 approved line 6, bg_4, status running with head commit 04d4368f. The words said "Line 6 is also still wrong because the work should touch only the version option code and its tests". `_line_cues` faults line 6, and the door excludes it. The verdict count stays 5 of 177, because m245 fires on line 4 already. The files correction is lost after the seat fixes line 4. Fix: spare a batch line only when its batch is merged or abandoned, and pass that set from `rulings_rule`.
2. `rota/roles/api.py:8470` (`_line_cues`, the window of a reference). Severity low. CONFIRMED. On night 147's m86, "Line 7 just repeats line 2 and isn't really an assumption, so you can drop it" faults line 2 with the cue "drop". Line 7 gets no cue. The night's right map approves line 2, `how_it_works`, the project description item. The probe refuses that map with "Rule line 2 contest or revise". With line 2 contested, the map lands. So the right map cannot land with the reply whole. The steer contests or revises an item he did not fault, and a revise writes m86's words into the description item. Fix: in `_faulted_approve`, skip a line whose reference is not the first line reference of its sentence. All four true fires are the first reference of their sentence.
3. `rota/roles/api.py:8466` (the cue choice). Severity low. CONFIRMED. When a clause holds only weak cues, the refusal quotes the weak word. Night 143's m133 gives "still", night 146's m162 gives "not", and m92 gives "still" for lines 4, 6 and 7. A seat that reads `The words fault line 4, "still"` sees no reason. Fix: when the clause holds only weak cues, quote the first eight words of the clause.
4. `rota/roles/api.py:8592` (the refusal text). Severity low. PLAUSIBLE. The refusal offers "contest or revise" for every line. The team-note door at api.py:8877 refuses a revise of a team note when the page holds a request. m86's lines 6 and 7 are `l_` rows. A seat that picks revise there meets a second refusal. Fix: name contest alone for a line that `_is_team_note` reads as a note.
5. `rota/roles/api.py:8583` (the third guard, `_TOUCH_WORDS`). Severity low. CONFIRMED. The guard spares any clause with "file", "test" or "touch" on a page with a batch line. The probe spared "Line 4 is wrong, its test calls plain echo." with a batch on line 6. The same words with no batch line were refused. Present pages after a build carry a batch line, as m245, m162 and m91 do. Fix: spare the clause only when it names a path of the batch's `batch_touch` rows.
6. `tests/rota/test_frame250_verdict_faults.py:117` (the m81 xfail). Severity low. CONFIRMED. The xfail has no `raises=`, so an import error or a fixture error also keeps the test xfailed. Today it fails by "DID NOT RAISE". Fix: add `raises=pytest.fail.Exception` to the mark.
7. Outside the points. `rota/roles/api.py:8941` (the door reads the `words` argument). Severity low. CONFIRMED for the mechanism. The door reads the words the seat passes, not the reply text. The probe ruled all eleven fixture lines approve with m105 cut to its last sentence, and the ruling landed. With m105 whole, the door refused. The contest door had the same gap before this pass. The new refusal can teach a seat to trim the words. Fix: read the trigger message text for the line reading, or refuse words that are not a part of the reply.

## (c) Probes

All probes are in the scratchpad folder `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4492a9c1-4457-41ce-a46b-42b300ec21c1/scratchpad/f250r1/`.

- `count_present_wt.py`: the pass's `count_present.py` with the import path set to the worktree. Output: 177 verdicts, fires on 5, the same five as the pass report.
- `count_clar_wt.py`: the pass's `count_clar.py` from the worktree. Output: the brief predicate fires on 6 of 9 and refuses 40 of 69.
- `m86.py` and `m86b.py`: night 147's m86 ruling row, line map and item rows. `_line_refusal` on the night map refuses line 2, "drop". With line 2 contested, it returns None.
- `batchlines.py`: the line maps and batch states of m245, m162, m91 and m133. m245 line 6 is bg_4, running, approved.
- `spot.py`: three clarify refusals, 144 m43, 144 m55 and 146 m84, with the question, the map and the words.
- `noguard3.py off` and `noguard3.py on`: `test_request_page.py`, `test_frame234_verdict_lines.py` and `test_park_page.py` in one process. With `_TOUCH_WORDS` disabled: 3 failed, the three m85 tests. With the guard: 176 passed, 4 xfailed.
- `old/`: an export of d3340828 by `git archive`, with the new test file from f0b2924c. Result: 5 failed, 8 passed, 1 xfailed. The reasons: DID NOT RAISE, an ImportError of `_line_cues`, the reading ({2, 7}, set()), and two `assert None`.
- `test_probe_bypass.py`: m105 with an all-approve map is refused for lines 2, 3 and 5 to 7. The cut words land the all-approve map.
- Inline `python -c` probes: m92 with the night map is refused for lines 4, 6 and 7, cue "still". The third guard spares two check faults on a page with a batch line.
- The six touched or near test files at f0b2924c: 201 passed, 5 xfailed. The m81 test with xfail off fails by "DID NOT RAISE". The gate was not run. The pass report's gate shows no red that this pass caused.

## (d) Usage

About 80k input and 15k output, about 95k in total, against the 50k cap. Read the harness line for the true number. Sub-agents: none.
