# Frame 200, review 5b of pass 5b at ba2ddf5e

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_rv200p5b` at ba2ddf5e. Date: 2026-10-12. Rota workflow, except where a line says meta workflow.

Verdict: the pass stands with one high finding. The verdict door refuses the fact that the frame targets when the seat writes it with the verb "passes". One low finding is outside the points.

## (a) Verdict on each point

1. The reason paragraph and the slot: PASS. Both briefs ask for the error and the test line, and say the reason is not a fix. Each paragraph has three sentences. Every hint site in `sandbox.py` and `api.py:8118`, `:13410` writes `REASON_SLOT`. The TOOL line shows `reason="<the error and the line>"` in five Developer modes.
2. The Tester sentence: PASS. `tester/challenge.md:8` puts the argument on the call the traceback names, and says the row outranks the criterion's wording. `_mode_key` keys a message wake by its verb, so the receiver of `msg.challenge_tester` wakes in `tester/challenge`. The map lists that mode's tools.
3. The verdict door: PASS on the three phrases and on red before the door. FAIL on the flagged fact: the door refuses "the test passes package_name to invoke" (finding 1).
4. `__shown__`: PASS. Of 95 composed modes, 6 moved. In each, the only TOOL line that changed is `msg.challenge_tester`. The modes are developer/answer, developer/base, developer/exhausted, developer/findings_exhausted, developer/tests_failing and tester/challenge. tester/challenge moved by its brief sentence only.
5. Hygiene: PASS. The diff holds 0 CR bytes. It moves three briefs, all three named in the brief, and no other brief or door.

## (b) Findings

1. `rota/core/sandbox.py:1864` and `:1907`. HIGH. CONFIRMED. The door reads "passes" in the first four words as a verdict. "passes" is also the verb that names the fact this frame targets. The probe refused four facts: "the test passes package_name to invoke", "The test passes package_name to runner.invoke, and invoke raises TypeError on it", the same with backticks, and "runner.invoke(package_name=...) passes an argument invoke does not take, TypeError". The refusal then tells the seat that it said the test passes, which is false. The pass 5 probe quotes the seat's own words, "the test must either pass `package_name`", so the seat uses this verb on the measured path. A seat that looped before can loop again on this refusal. Fix: refuse "passes" only with no object, for example `\bpasses(?=\s*(?:$|[.,;!?]|on\b|as\b|already\b|now\b|today\b))`, and add the four facts above to test 19 as admitted.
2. OUTSIDE. `rota/core/sandbox.py:1918`. LOW. CONFIRMED by reading. The copy refusal still ends "reason= says why they conflict". Pass 5b asks for the error and the line, so this refusal teaches the old ask. Fix: end the copy refusal with `_REASON_SAID`'s first sentence.

Also seen, not a finding: "the test would pass on right code as it stands" and "e.g. the test passes on right code" are admitted. The door reads one verb form, and the first ". " splits the head. This is a ratio question for the night, not a defect.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d609cf11-e3b0-446b-b02a-29ab3633c919/scratchpad/rv200p5b/`. No probe wrote to the worktree or the checkout. `git status` in the worktree was empty after the runs. No model was loaded.

- `old/`: `git archive 7b0a9aac rota` extracted to the scratchpad.
- `sysdump.py`: for every `<role>/<mode>.md` under the prompts, `build(role, init_db(...), mode="normal", allow=mode_tools)`, `_order = mode_order`, then `runner.compose_system` with `prompts.compose`. It wrote `old.json` (PYTHONPATH `old/`) and `new.json` (PYTHONPATH the worktree). 95 modes, 0 errors on each side.
- `cmp.py`: the modes whose text moved, and the TOOL lines that changed in each. Result in point 4.
- `door.py`: `_reason_problem` on ten reasons on a fresh `init_db`. Six refused, four admitted. Result in finding 1.
- `nodoor.py`: a pytest plugin that makes `_REASON_VERDICT` match nothing. `test_challenge_evidence.py` gave 1 failed (test 19), 23 passed.
- `noshown.py`: a pytest plugin that deletes `__shown__` before the render. `test_challenge_evidence.py` gave 1 failed (the TOOL line test), 23 passed.
- The touched tests with `ROTA_MODEL=qwen3:8b`: `test_challenge_evidence.py`, `test_prompts.py`, `test_revert_door.py` and `test_row_route.py` gave 97 passed.

## (d) Usage

About 33k input tokens of context and about 7k output tokens, about 40k in all. These are the reviewer's own estimates. Read the harness line for the real count.
