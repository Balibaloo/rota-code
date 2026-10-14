# Frame 202, scope read for pass 2: why s130's move to `echo` passed the door

Read at HEAD 9b90abb4 (the door of c1a4cded), 2026-10-14 19:29, on Opus. Rota workflow. Read-only. A worktree at HEAD, `C:/Users/roman/rota_rd202`, ran the door and the measure, and the read removed the worktree after.

Verdict: the comparison rule's fall-through, `return None` at `rota/roles/api.py:5250`, admitted s130's move. Candidate A holds. On nights 144 to 147 it refuses 11 of 11 wrong moves that landed and 0 of 13 right moves. Candidate B misses night 145's s261.

Scripts and outputs, in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4a757f92-bd97-4750-9830-bd149134e576/scratchpad/s202/`:

- `measure_orig.py`: pass 1c's measure, copied unchanged.
- `measure_head.py` and `measure_head.out`: the same measure on nights 144 to 147, with the door at HEAD.
- `mcore.py`: the measure as a row collector. `rows.pkl` holds its rows.
- `cands.py` and `cands.out`: candidates A, B1 and B2 on every move, with labels.
- `cand_a.py`: candidate A as a door function. `run_a.py` runs it with the final item-callable rule.
- `patch_a.py`: a pytest plugin that puts candidate A in place of `_surface_move_fault`.
- `test_s130.py`: the proposed test.

## 1. s130's call and the branch that admitted it

These are the rows of `.rota/clickI_night147.db` (observed: 2026-10-14 19:2x):

- Session s130 is a Terminologist, mode `normal`, woken by the relay m44. The relay has `body_refs ["cj_serializable"]` and no `body_text`.
- The ruling r_0dd76d63e1 contests `cj_serializable`. Its words: "Line 3 is wrong: there should be no conversion of arbitrary objects, so the standard json module's usual error should stand when an object cannot be serialized. Line 5 also lists a pager test, but I did not ask for anything about the pager, so please keep the work to utils and the echo tests."
- The item is `echo_json`. The ticket is `tk_1`. The text of both: "Add an echo_json(obj) helper next to echo that prints an object as compact JSON on one line, followed by a newline."
- The call is `criteria.respecify(id='cj_serializable', text='The function must raise an error if serialization fails (no conversion of arbitrary objects).', surface_refs=['src/click/utils.py::echo'])`.
- The seat gave its reason: "From `[code.callables]`, `src/click/utils.py::echo` is the main entry point for echo functions." No word of the principal asked for `echo`. The seat picked the callable from the list of callables.

This is what `_surface_move_fault` got on s130's inputs at HEAD. The read ran the function itself (observed):

| Value | Result |
|---|---|
| `old` / `new` | `{echo_json}` / `{echo}` |
| `named`, the callables the text puts in backticks | `[]`. "The function" names no callable. |
| `asked`, from `_item_callables` | `{echo_json}` |
| `mine` | `[]` |
| `_item_names`, then `toward` | `{echo_json}` (the call form `echo_json(`), then `set()` |
| Request cues on `echo` in the words | none |
| Comparison cues on `echo` in the words | none |
| Comparison cue on `echo` in the item text | `'next to echo'`. The door does not read the item text for cues. |
| Result | `None` |

The branches, by line at HEAD:

1. Line 5217, `if new & set(named) and not mine`. False, because the text names nothing.
2. Line 5226, `toward`. Empty. The item names `echo` only as a location, and `_item_names` reads only backticks and call forms. So the line of pass 1c, "a move to a callable the item names lands", did not admit s130. The brief's suspicion is wrong on this point (observed).
3. Line 5227, the text rule. It is idle because `mine` is empty, and the text names no callable.
4. Line 5234, `if not old & asked`. False, so the comparison rule runs.
5. Lines 5236 to 5249, the comparison rule. No word of r_0dd76d63e1 holds a cue on `echo`. "The echo tests" is no cue. The loop ends with no refusal.
6. Line 5250, `return None`. The move lands.

Both rules of the door need a name. The text rule needs a backticked callable in the criterion's text. The comparison rule needs a cue in the principal's words. s130 gave neither. The one cue, "next to echo", is in the item text, and the door reads that text only for `_item_names` (observed). This is the shape that pass 1 named for s135 on night 146: a move to a callable that no word of the principal or of the text names.

## 2. The three moves of night 147 against the door at HEAD

| Session | Criterion | From | To | Door at HEAD | Branch | Label |
|---|---|---|---|---|---|---|
| s130, m44 | `cj_serializable` | `echo_json` | `utils.py::echo` | lands | 5250, fall-through | wrong |
| s173, m68 | `cj_serializable` | `echo` | `utils.py::echo_json` | lands | 5250, fall-through. `toward` = `{echo_json}`, but `mine` is empty, so the text rule is idle anyway | right |
| s340, m180 | `ver_opt_show_py` | `version_option` | `custom_version_option`, `version_option` | lands | 5250, fall-through. `new - old` = `{custom_version_option}`, no cue | right |

The texts and the words:

- s173. Text: "The function must raise a TypeError if serialization fails, without converting arbitrary objects or emitting custom messages." Ruling r_19f3a3cbe9. No cue on either name.
- s340. Text: "The implementation of show_python must append ...". Ruling r_1ed6c3dbaf: "Ok, approved. The Python version in line 2 should read as major, minor and micro ...". The item: "Give version_option a show_python flag that appends the running Python version to the message." The move keeps `version_option` in the surface.

The measure also lists night 147's s284 and s302. They moved `confirm` criteria to test names 10 times, and `_vet_surface` refused all 10 first, so the door at HEAD never saw them (observed: `measure_head.out`).

## 3. The candidates, per night

Each candidate goes in after the door at HEAD. It runs only where the door at HEAD returns `None`. So every move that the door refuses today stays refused.

The labels come from the records. A move is right when its new surface holds the callable that the item asks for: `echo_json` for the two echo_json items, `version_option` for the three version_option items, and `confirm` for night 147's confirm item. Any other move is wrong. These labels agree with the pass 1 to 1c tables and with the night 147 read, which counts s173 and s340 as right.

"Wrong, landed" counts the wrong moves that landed on the night. Those are the moves that matter. "Wrong, refused elsewhere" counts the wrong moves that another door (`_vet_surface`, the contested words) refused first.

The rules:

- **A**: the item's callables are the item id and the names in the request's first verb phrase, cut before a location or comparison cue ("next to", "beside", "alongside", "near", "like", "the way", "similar to", "same as", "as in"). A name counts when it is a call form, a backticked callable, an identifier with an underscore, or a plain word that is the old surface's symbol. A move whose old surface holds an item callable and whose new surface holds none is refused. Two things admit the move: the text names a new callable in backticks, or the principal's words carry a request cue on the new name, with the negation guard of HEAD.
- **B1**: when the text names no callable, the surface stays on `_item_callables` (the item id and the old surface). The other exceptions are the same as A.
- **B2**: B with A's item callables.

The counts (observed: `cands.out` and `run_a.py`, 2026-10-14 19:2x):

| Night | Door at HEAD: wrong, landed | A: wrong, landed | A: right refused | B1 or B2: wrong, landed | B: right refused |
|---|---|---|---|---|---|
| 144 | 2 of 3 (s591, s609). Misses s190 | 3 of 3 (s190, s591, s609) | 0 of 0 | 3 of 3 | 0 of 0 |
| 145 | 0 of 1. Misses s261 | 1 of 1 (s261) | 0 of 8 (s272, s292, s321 ×4, s340 ×2) | 0 of 1. Misses s261 | 0 of 8 |
| 146 | 5 of 6 (s160 ×2, s248 ×2, s310). Misses s135 | 6 of 6 (adds s135) | 0 of 3 (s291, s304 ×2) | 6 of 6 | 0 of 3 |
| 147 | 0 of 1. Misses s130 | 1 of 1 (s130) | 0 of 2 (s173, s340) | 1 of 1 | 0 of 2 |
| Total | 7 of 11 | 11 of 11 | 0 of 13 | 10 of 11 | 0 of 13 |

The wrong moves that another door refused first:

- Door at HEAD: 4 of 58.
- A: 57 of 58. The one A lets through is night 146's s209, `echo` to `echo_json_compact`, a criterion id. Its old surface is not an item callable, and `_vet_surface` refused it.
- B1: 34 of 58. B2: 33 of 58.

B misses s261 because its text names `version_option` without backticks. B reads that as "the text names a callable", so B does not fire, and the text rule at HEAD needs backticks. B1 also carries a defect the nights do not show. Its item callable includes the old surface, so a restore whose text names no callable and whose item id is not a callable gets refused. Night 145's restores pass B1 only because their texts name `version_option`.

A holds. C is not needed (reasoned: the table).

## 4. The proposed rule, the refusal text and the test

**Rule (A).** The item's callable is the item id, or a name that the request's first verb phrase adds or changes. A location such as "next to echo" is not the item's callable. A move that drops every item callable from the surface is refused. The exceptions are a text that names the new callable in backticks, or a request cue on the new callable in the principal's words.

Where it goes: replace the final `return None` of `_surface_move_fault` (line 5250) with the check. Then no refusal at HEAD changes, and the counts above hold. `_item_callables` keeps its role for the text rule. The new reader of the item callables is separate, so review 2's finding 3, "works like echo(msg)", stays closed. The cut at "like" keeps `echo` out.

**Refusal text.** STE, and no sentence has more than 20 words:

> The item asks for `echo_json`, and this move drops `echo_json` from the surface. The surface is what the test calls. Keep `src/click/utils.py::echo_json` in surface_refs. If the principal asked for `echo` itself, name `echo` in backticks in the criterion's text.

The question route of `ask` follows when the wake's mode offers it, as on the other refusals.

**Test, red first.** `test_a_location_in_the_request_is_not_the_surface` goes in `tests/rota/test_frame202_surface_move.py`, and the scratchpad copy is `test_s130.py`. It is s130's call, built with the file's `db`, `_criterion`, `_ruling` and `_respecify` helpers. The text is S130, the words are those of r_0dd76d63e1, the old surface is `ECHO_JSON` and the new surface is `ECHO`. It asserts `"The item asks for `echo_json`"` and `Keep `{ECHO_JSON}` in surface_refs`.

- At HEAD: red, DID NOT RAISE. With the frame 202 file: 1 failed, 18 passed (observed).
- With candidate A put in through `patch_a.py`: 19 passed (observed).

## 5. The risk: what the rule would refuse wrongly

1. **Two tests of frame 215 go red.** The read ran A over the 9 test files that call `criteria.respecify` or `_surface_move_fault`. The result: 722 passed and 2 failed, against 724 passed at HEAD (observed). The two red tests are:
   - `test_criteria_surface.py::test_a_repair_surface_outside_the_batch_files_is_refused`, its last call, "a ticket in no batch passes as today".
   - `test_only_the_statement_names_the_callable_and_the_surface_is_admitted`.

   Both move a version_option criterion to `examples/imagepipe/imagepipe.py::process_commands` and expect it to land. Their subject is frame 215's batch-file door. The move is only their vehicle, and on the nights the same move is a wrong one. The second test does matter: a statement of the item names `process_commands`, and frame 215 reads that as a reason to admit. A does not read statements. Recommend: the pass gives both tests a text that names `process_commands` in backticks, so A admits the move, and the subject stays frame 215's. The other option is that A admits a new callable that an item statement names. That widens A, and no night needs it (reasoned).
2. **A request with no cue is refused.** The probe "Forget the helper; give echo a json parameter instead." is refused, and the door at HEAD lands it (observed: `run_a.py` probe R1). A rename, "Call the helper dump_json, not echo_json.", is refused too (probe R2). Each refusal gives the route "name `echo` in backticks in the criterion's text", so the seat has a way through. Recommend: add `give {n}` to `_REQUEST_CUES`. No move of the nights depends on it.
3. **The backtick route is also an escape.** A seat that wraps the wrong name in backticks gets past both A and the door at HEAD. On nights 144 to 147, no wrong move did that (reasoned: the text rule's counts). This is the same route as today.
4. **Review 2's lows on the cues stay open.** "as in echo" and "echo should stay as it is" still read as requests, and the move lands under A too (probes C1 and C2). "Let echo print JSON too, as echo does for text" is still refused, by the comparison rule (probe C3). A does not change these. They are the night's measure, as the stack records.
5. **An item whose first phrase names nothing.** An example is "Make the bar show an ETA" with the item id `bar_eta`. That item has no item callable that is a symbol, so A never fires. That is the behaviour at HEAD (reasoned).
6. **The first-sentence split.** An item that names its callable only in a later sentence gets only its id as an item callable (reasoned). All 11 items of the four nights name their callable in the first sentence (observed: the items listed by `mcore.collect`).

## 6. Tokens

About 85k of the 90k budget, read from the context count at the end.
