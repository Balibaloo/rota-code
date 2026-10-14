# Frame 202, pass 2: the diff review of the request rule (review 3)

Rota workflow, the Architect's `criteria.respecify` door. Read-only review of 6419a40b over 7ad7f7c7, on the worktree `C:/Users/roman/rota_rv202c`. Reviewer: an Opus agent, 2026-10-14.

## Verdict

Accept. The request rule refuses s130's move on the night's real inputs, and the backtick route lands. Nine test files that call the door are green. No finding is high. Four low findings go to the stack or to a later pass. Fix finding 1 first, because a near paraphrase of the night's words reopens the night's wrong move.

## (a) The points

1. Night 147's case: refused with the brief's text, and the backticked `echo` text lands (CONFIRMED, probe P1).
2. `_request_callables`: never empty, because it adds the item id. It returns many words that are no callable. No such word is on a surface, so the door ignores them. With no item callable on the old surface, every move is admitted.
3. Location cues: the code holds "next to", "beside", "alongside" and "near", and also "like", "the way", "similar to", "same as", "as in". The five shapes cut right.
4. Frame 215's fixtures: the backticked text does not change what frame 215's door decides. Every caller file is green. One docstring is now false (finding 2).
5. STE: the refusal text passes. One comment uses the passive (finding 4). The three files hold 0 CR bytes.

### Point 1

The probe P1 rebuilt s130's call from `clickI_night147.db`. The inputs are the `echo_json` item text, the words of `r_0dd76d63e1` (relay m44's reply), the old surface `src/click/utils.py::echo_json`, and the new surface `src/click/utils.py::echo`. The door refuses. The text is: "The item asks for `echo_json`, and this move drops `echo_json` from the surface. The surface is what the test calls. Keep `src/click/utils.py::echo_json` in surface_refs. If the principal asked for `echo` itself, name `echo` in backticks in the criterion's text." The same move with "`echo` must raise an error if serialization fails." lands, because the first rule of `_surface_move_fault` returns None when the text names the new callable. The night's later words, `r_m38`, `r_m51` and `r_m63`, each still give a refusal. `r_m63` says "echo itself does not change", and the negation guard skips that cue.

### Point 2

The probe P2 ran `_request_callables` on every item with `is_description = 0` and on every statement of nights 143 to 147, deduplicated by id and text. The function never returns an empty set for an item, because it adds the item id. The results with only the id are the `echo_json` items and `bg_3_ref` on night 146. For `echo_json`, the id is the asked callable, and the index lacks it until the build. `bg_3_ref` is a constraint. Words that are no callable in `code_index`: `echo_json` (not yet built), `default_on_eof`, `show_python`, `False`, `off`, and the item ids `confirm_default_on_eof`, `version_option_show_python`, `cr_3_show_python_append`, `echo_json_support`, `bg_3_ref`. A backticked path gives a fragment too: "`utils.py`" returns `py` (probe P3).

The door reads only `held = old & items`, and `old` holds surface symbols. So these words never act. When the old surface holds no item callable, `held` is empty and the rule returns None, so every move is admitted. The rule fails open, never closed. The Architect rewrites the item text per night. On nights 144 and 146, the `confirm` and `version_option` texts keep their callable in backticks, so the result holds.

### Point 3

`_LOCATION_CUE` holds "next to", "beside", "alongside", "near", "like", "the way", "similar to", "same as" and "as in". The probe P3 ran ten shapes. "in `utils.py` next to echo" gives `json_line` and `py`. "after echo in utils" gives `json_line`. "after" is not a cue, but `echo` there is no call form, no backticked name, no snake name and no verb object, so `echo` stays out. "near", "alongside" and "beside" cut right. "Next to echo, add an echo_json(obj) helper" cuts at position 0 and keeps only the item id, which fails open when the id is not the callable. A bare "like" cuts "I would like echo to take a json flag" before `echo`. That also fails open: the door admits the move. The review of ee535945, finding 2, took the bare "like" out of `_COMPARE_CUES` for this sentence. Here the cost is an admitted move only, so it is not a finding.

### Point 4

The pass changed two calls in `tests/rota/test_criteria_surface.py` to `_N142_TEXT_NAMED`, which names `process_commands` in backticks. The probe P4 sent `_N142_TEXT_NAMED` with no statement change. Frame 215's door still refuses it ("lives in examples/imagepipe/imagepipe.py, and the batch expects to touch ..."). So the backtick does not admit frame 215's door, and the statement still decides the second test. The first test's last call runs with no batch, so frame 215's door passes as before. The probe P4 also sent the old plain text with the statement naming `process_commands`: frame 215 admits it, and frame 202 refuses it (finding 3).

The map tool lists `criteria_respecify` as the only caller of `_surface_move_fault`. Nine test files call `criteria.respecify`. Each ran green alone: `test_criteria_surface` 36, `test_frame202_surface_move` 21, `test_criterion_contest` 17, `test_desk_guards` 336, `test_night46_context` 48, `test_park_page` 21, `test_predicates` 98, `test_refs` 43, `test_request_page` 107 passed and 4 xfailed. No other file builds a plain move that now fails. The implementer's gate shows `L1-TE-a-ruled-criterion-is-respecified-and-the-tester-told` green 5/5. This review did not run the gate.

### Point 5

The refusal has four sentences, each under 20 words, in the active voice and the imperative. The new comments follow STE, except one passive sentence (finding 4). A byte count finds 0 CR bytes in each of the three files. `git diff --check` is clean.

## (b) Findings

1. `rota/roles/api.py:5095`, low, CONFIRMED (probe P5). The new cue "give {n}" also matches a principal who gives a value to `echo`. The words "Build the compact string and give echo the result, so echo adds the one newline." admit the exact move of s130. The words "pass it to the existing echo" are refused. The words of night 147 use "pass it to" and "through", so no night shows the phrase yet. Fix: match "give {n}" only when "a" or "an" and a parameter noun follow (flag, parameter, option, argument, mode).
2. `tests/rota/test_criteria_surface.py:466-468`, low, CONFIRMED by reading. The docstring of `test_only_the_statement_names_the_callable_and_the_surface_is_admitted` says that the new text does not name `process_commands`. The text now names it. Fix: say that the text names it for the door of frame 202, and that the door of frame 215 ignores the text.
3. `rota/roles/api.py:5290-5297`, low, CONFIRMED (probe P4, second case). The request rule reads the words of the rulings and the text, not the statements of the item. The door of frame 215 reads the statements. A statement that names the new callable admits frame 215, and frame 202 refuses the same move. The refusal names the backtick route, so a seat can recover. Fix: accept a new callable that a request cue or a backticked name finds in the ratified statements of the item, or record the difference as ruled.
4. `rota/roles/api.py:5288-5289`, low, CONFIRMED by reading. The comment "A move that drops every callable of the request is refused" uses the passive voice. Fix: "The door refuses a move that drops every callable of the request, unless the text or a request cue names the new callable."

Outside the points (reasoned): the refusal tells the seat how to pass the door, by a backtick on the new callable. A seat that misreads the request can follow that route with no word from the principal. Open point 2 of the implementer already names this risk as risk 3 of the scope read. No new finding.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4a757f92-bd97-4750-9830-bd149134e576/scratchpad/rv202/`. Each probe opens the night databases with `immutable=1`.

- `p1_p3.py`: P1 runs `_surface_move_fault` on the inputs of s130 from `clickI_night147.db`. It uses the words of `r_0dd76d63e1`, `r_m38`, `r_m51` and `r_m63`, and the backticked text. P3 runs `_request_callables` on ten request shapes.
- `p2_callables.py`: P2 runs `_request_callables` on every item request and statement of `clickI_night143.db` to `clickI_night147.db`. It lists the words that are not in `code_index`.
- `test_p4_probe.py`: P4, two pytest cases on `_night142`. The first sends the backticked text alone, and frame 215 refuses it. The second sends the plain text with the statement naming `process_commands`, and frame 202 refuses it.
- `p_give.py`: P5, three sets of words on the move of s130. "give echo the result" admits the move.
- pytest from the worktree, one file at a time, with `ROTA_MODEL=qwen3:8b`: the nine files that call `criteria.respecify`. All are green.

## (d) Usage

About 85k tokens in all on the session counter, from 15.00M to about 14.915M. The counter does not split input and output. Output is about 12k of that, as an estimate. No sub-agent.
