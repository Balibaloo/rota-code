# Frame 202, the respecify door: review 2 of pass 1b at 3de76eaf

Rota workflow, the Terminologist's `criteria.respecify` door. Read-only review on the worktree C:/Users/roman/rota_rv202b at 3de76eaf, over its parent 81f27127. Reviewer: an Opus agent, 2026-10-14.

Verdict: revise. Two high findings stop an accept. The question route never shows in a live session. A text that names the new callable admits a wrong move, and the refusal's own route tells the seat to write that text. The findings below are the brief for pass 2.

## (a) Verdict on each point

1. Review 1's six findings: 1 fixed, 2 fixed, 3 fixed, 4 fixed by removal, 5 partly fixed, 6 not fixed and widened. The two highs land through the helper (probes H1 and H2).
2. Night 146: the door refuses 5 of 6 wrong moves and 0 right moves. Night 145 version_option repairs: 0 of 8 right moves refused. The counts match the implementer's.
3. Request cues: "in {n}" and "{n} should" admit a move the principal did not ask for (C1, C2). A comparison cue still refuses an asked move when no request cue matches (C3).
4. Refusal texts: both callables, a route and "the principal" are present. The question route never shows in a live session (finding 1). One route sentence holds 21 words and two instructions (finding 7).
5. Tests: 6 of 14 are red on the parent, 8 green. Three branches have no test (finding 6).

## (b) Findings

1. rota/roles/api.py:5146-5149, high, CONFIRMED. The door reads `prompts.mode_tools(ctx.role, ctx.mode)`, and `ctx.mode` is the sandbox mode, not the prompt mode. The runner builds the sandbox with `session_mode(wake)` (rota/core/runner.py:3275), and nights 145 and 146 stamp every mover session `normal`. `mode_tools("terminologist", "normal")` returns None, so `ask` is always empty. The test passes because it builds the sandbox with `mode="criterion_repair"` (tests/rota/test_frame202_surface_move.py:86), a shape the runner never builds. Fix: read the prompt mode from the wake (`_mode_key`) or the sandbox's allow list, and test through `session_sandbox`.
2. rota/roles/api.py:5030-5031, high, CONFIRMED. `if new & set(named): return None` runs before the comparison rule. Probe N1: a move from `echo_json` to `echo` with the text "`echo_json` wraps `echo`" and the words "the way echo does" lands. Both refusals end with "rewrite the criterion's text to name `echo` in backticks", so a seat that obeys the refusal lands the wrong move on its next call. Fix: admit on a named new symbol only when no comparison cue names it in the words, or only when the text names the new symbol and not the item's callable.
3. rota/roles/api.py:4949 and 4981-4987, low, CONFIRMED. `_CALL_FORM` counts every `name(` in the item text as the item's callable. Probe N2: the item "Add an echo_json(obj) helper that works like echo(msg)" makes `echo` an item callable. A right restore to `echo_json`, whose text names `echo` as a helper, is then refused and told to keep `utils::echo`. This brings review 1's finding 1 back on this item shape. Fix: take the call form only for the item's first callable, or only for a name the item id contains.
4. rota/roles/api.py:4938-4941, low, CONFIRMED. Two request cues read a comparison as a request. Probe C1: "the same newline handling as in echo" matches "in {n}". Probe C2: "Format it the way echo does; echo should stay as it is" matches "{n} should" with no negation word. Both wrong moves to `echo` land. Fix: drop "in {n}", and add "stay", "keep" and "as it is" to the negation guard or require a change verb after "{n} should".
5. rota/roles/api.py:4935-4937 and 5050-5063, low, CONFIRMED. A comparison cue refuses an asked move when the request uses a verb outside the list. Probe C3: "Let echo print JSON too, as echo does for text" refuses the move to `echo`. The rewrite route recovers the move, so the cost is one turn. Fix: no change in pass 2, and record the form as residue.
6. tests/rota/test_frame202_surface_move.py, low, CONFIRMED. Three branches have no test: the ask sentence in a runner-built sandbox (finding 1), an admit by a named new symbol beside a comparison cue (finding 2), and the absence of the ask sentence in a mode that does not offer `msg.challenge_vision_keeper`. Fix: add one test for each, built through `session_sandbox` with a wake.
7. rota/roles/api.py:5038-5039, low, CONFIRMED. The route sentence "Keep `x` in surface_refs, or rewrite the criterion's text to name `y` in backticks if the principal asked for `y` itself." holds 21 words and two instructions. STE allows 20 words and one instruction. Fix: split it into "Keep `x` in surface_refs." and "If the principal asked for `y` itself, name `y` in backticks in the criterion's text."
8. Outside the points. rota/roles/api.py:5031-5036, night 144 s591 t1 and s609 t4, low, CONFIRMED by the measure rows. Pass 1b admits two wrong moves from `version_option` to `custom_version_option` that pass 1 refused, as the implementer reports. With night 144 s190 and night 145 s261, four wrong moves now pass beside night 146 s135. Fix: count all five in the residue line, and read the item text's bare names in pass 2 or a new frame.

## (c) Probes

All probes are under C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/58da19ca-3cc0-49b5-a8a7-5edb2f08ef46/scratchpad/rv202b/.

- `probe_door.py`: calls `_surface_move_fault` from the worktree on seven cases, H1, H2, N1, N2, C1, C2 and C3, and reads `mode_tools` for `normal` and `criterion_repair`. H1 and H2 land. N1 lands. N2 refuses. C1 and C2 land. C3 refuses. `normal` gives None, and `criterion_repair` offers the ask.
- `measure_wt.py` and `measure_wt.out`: the implementer's f202/measure.py with the import path moved to the worktree, run on nights 144 to 146 with `mode=ro`. Its rows equal measure1b.out row for row.
- An inline query on clickI_night145.db and clickI_night146.db, `mode=ro`: the mover sessions s135, s160, s248, s291, s304, s310, s261, s272, s292, s321 and s340 all hold role terminologist and mode `normal`.
- `parent/`: `git archive 81f27127` of rota, the test conftest and the pytest config, with the new test file copied in. pytest gives 6 failed, 8 passed. The red six: the two old refusal tests on the route text, and the restore with echo as a helper, the request for echo itself, the request beside a comparison and the move away from a second callable. On the worktree the file gives 14 passed.

## (d) Usage

From the context counter: about 57k tokens in total, about 49k input and about 8k output. The cap was 40k, and the run went over it by about 17k.
