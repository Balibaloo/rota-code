# What the records know about the limits of the seat models

Task D of the wall research. Written 2026-10-15 by an Opus agent of session dae006d1. Meta workflow: the build session reads the records about the rota workflow's seats.

## The models

- The seats run `qwen3:8b` with `think: false` since the 2026-08-25 bakeoff. The flag goes in the Ollama payload. "The `/no_think` prompt prefix does NOT work" (observed: `plans/operating-facts.md` line 93, 2026-08-25).
- Without the flag, `qwen3:8b` "decodes at 0.1 tok/s and scores 0 on frame. That result is thinking contamination, not model quality" (observed: `plans/operating-facts.md` line 94).
- Some nights and interviews run `qwen3.5:9b` at a 16,384 window: frames 152, 165 and 243 (observed: the interview headers). The other interviews run `qwen3:8b`.
- `gemma3:12b` is the Critic's model. It "passes every Critic register case 5/5 on one load. That includes `CR-a-test-that-encodes-nothing`, which is red on every 8B and on qwen2.5:14b-q3" (observed: `plans/operating-facts.md` line 108, 2026-09-12).
- `qwen2.5:14b-instruct-q3_K_M` "keeps judgement parity" at 153 s a turn and stays only for cross-family reads (observed: `plans/operating-facts.md` line 95).

## The limits

Each row is one limit. Rows that show the same limit share a group. The fix column says "none" when no record shows a fix that moved the sign.

### Group A. The seat has the fact and does not act on it

| # | Limit | Frame | Evidence, verbatim | Fix | Mark |
|---|---|---|---|---|---|
| A1 | The seat does not act on a failure line that sits inside an escaped JSON string. It reads the same line when a person states it in plain words. | 110, the Tester answers the Developer and not the failure | "In the seat's user text the same line sits inside an escaped JSON string under `resolved_refs.last_run.output_tail`." "The model has no picture of the fix." | Proposed: the failure's last line as plain text above the JSON, with one concrete edit. "Only a re-record can test this change." | (observed: `plans/frame110-interview.md`, 2026-10-02) |
| A2 | The seat knows that a format comes from no material, and its triage still says `encodable`. The verdict follows the encode it plans in the same reply. | 204, the Tester triage | "I invented it ... assuming a format that was not explicitly named." "So the fact was in front of the seat and understood, and the triage did not apply it." | none recorded. A door on `tests.triage` is proposed and needs its own frame. | (observed: `plans/frame204-interview.md`, 2026-10-12) |
| A3 | The seat states the difference between two requests and does not compare the new words against `current_request`. It compares against the brief's example instead. | 193, the second request | "Both seats stated the difference of function and did not use it. The comparison against `current_request` is the step that neither seat made." | The page and route changes of frame 193. Closed on night 139: "0 of 20 pages by line 1 carry a request the principal moved past". | (observed: `plans/frame193-interviews.md`, 2026-10-10, and `plans/stack.md` frame 193 status, 2026-10-11) |
| A4 | The seat keeps a list that the prompt calls `expected` over the principal's correction of that list. | 190, what the principal sees | Think false, answer 4: "The principal's comment about the defaults test file being wrong did not affect my decision to keep it, as it was part of the expected list." | The runner removes the disputed paths from `expected` and `possible` before the wake (`disputed_paths`, `rota/core/runner.py:1883`). | (observed: `plans/frame190-interview.md`, 2026-10-09; the code read 2026-10-15) |
| A5 | The seat reads a declined format as not rejected when the principal describes the format and does not quote it. A brief line does not move the seat. | 243, the relay keeps a declined form (qwen3.5:9b) | "It reads the format `\"{command} {python_version}\"` as not rejected." "The candidate line of scope 4.3 does not move s188." "a brief line does not answer s188." | A door at seam 1 that matches the literal against the principal's words. Validating on night 149. | (observed: `plans/frame243-interview.md`, 2026-10-15) |

### Group B. The seat acts only on what the row in front of it names

| # | Limit | Frame | Evidence, verbatim | Fix | Mark |
|---|---|---|---|---|---|
| B1 | A brief sentence that keys on a callable does not fire when the reason row names no callable. | 200 pass 5, the Tester acts on a challenge's reason | "The cause is the row's shape, not the Tester sentence and not the seat." "The Tester read that row exactly and said that the row names no callable." | Pass 5f, a row that names the callable. | (observed: `plans/frame200-pass5-interview.md`, 2026-10-12) |
| B2 | The seat disputes the criterion when the wake does not show the item's words. It asks a question in place of a fix. | 204 pass 2, the Developer takes out what nobody asked for | "The wake does not name the disputed thing, so the seat disputes the criterion." "The seat is not the cause: it asks honestly from what it sees." | Proposed and untested: the item's text beside the criterion in the `challenge` wake. | (observed: `plans/frame204-pass2-interview.md`, 2026-10-13) |

### Group C. The seat follows the literal words of the last runner line

| # | Limit | Frame | Evidence, verbatim | Fix | Mark |
|---|---|---|---|---|---|
| C1 | The seat drops the condition of a conditional invitation and calls again. | 121, three runner notes tell the seat a wrong thing | "the seat read \"ask once more\" and dropped the condition (call 1)." | Frame 169 removed the invitation. Closed on night 140 at "1 of 4 refusal lines after an eviction is false ... against 2 of 6 on night 126". | (observed: `plans/frame121-interview.md`, 2026-10-05; `plans/archive/stack-2026-10-11.md`, frame 169) |
| C2 | The seat follows a refusal's step even when the step does not fit the call. | 121, the serve cap refusal | "The seat read the named step, \"a narrower span\", and knew `tests.load` has no span." | The refusal names a step the call can take (asked by the answers). | (observed: `plans/frame121-interview.md`, 2026-10-05) |
| C3 | The seat follows the door's last words and not the door's main sentence. | 123, the literal door | "The seat then followed the door's last words, \"send this encode again unchanged\", and not its own sentence about removing the literal." | none recorded here. | (observed: `plans/frame123-read.md`) |
| C4 | The seat follows the refusal's advice literally and is refused again. | 204, the Vision Keeper `about_ref` | "The seat followed the refusal's own advice in turn 4, wrote `about_ref='@billing'`, and was refused again." | Proposed: the brief names `about_ref="@prose"`. Not run. | (observed: `plans/frame204-interview.md`, 2026-10-12) |
| C5 | The form of the next reply follows the refusal's words, and a repetition loop can follow. | night 119, s130 | "the form follows the refusal's words, and the reply ends mid-identi[fier]" | none recorded here. | (observed: `plans/night119-read.md`, line 57) |

### Group D. The seat needs a form to copy

| # | Limit | Frame | Evidence, verbatim | Fix | Mark |
|---|---|---|---|---|---|
| D1 | Runner text with no speaker mark reads as the tail of the seat's own reply. A `body='...'` gap stays unfilled, although the body stood in the prompt three times. | 152, the Tester writes its repair in a code block (qwen3.5:9b) | "both say the sentence is `not shown`". "s154 says the call line had to carry the body". The nudge "moved 0 of 2". | Proposed: a template with the body already filled and a speaker mark. | (observed: `plans/frame152-interview.md`, 2026-10-06) |
| D2 | A step with no form gets the seat's own form, which is a call. "End the session with no call" did not end the session. | 165, the Developer sends the next call (qwen3.5:9b) | "The seats sent the next call in 10 of 11 turns". "A step with a form the seat can send is taken, and a step with no form gets the seat's own form, which is a call." | Proposed: the step names what the next reply looks like. | (observed: `plans/frame165-interview.md`, 2026-10-06) |
| D3 | With no call example for a verb, the seat copies the shape of a brief sentence as a prose list. | 237, the Terminologist writes a prose list | "So the seat has no `glossary.amend` call to copy, and it copies the brief sentence's shape instead (reasoned)." "A written-out `TOOL: glossary.amend(term=...)` example moves the form in 3 of 3 runs (observed)." | A written-out call example, 3 of 3 on replay. The defect did not reproduce on the replay, 0 of 3. | (observed: `plans/frame237-interview.md`, 2026-10-14) |

### Group E. The seat writes the results of its own calls

| # | Limit | Frame | Evidence, verbatim | Fix | Mark |
|---|---|---|---|---|---|
| E1 | The seat writes `OK <tool> -> ...` result lines in its own completion. Many lines copy a real result line of the same prompt. | 113, a Developer writes its own tool results | Night 109: "29 of 35 Developer sessions invented a result line". Night 115: "Lines that copy a real line of the same prompt: 15 of 28, 33 of 66, 30 of 33." Night 131 counter: "made up: 109 turns, 49 sessions". | none. Frame 113 is still parked. The night counter counts the sign. | (observed: `plans/stack.md` frame 113; `plans/night115-read.md`; `plans/night131-read.md`) |
| E2 | A seat invents the result of a write and then commits on it. | night 130, t19 | "The seat invented that result, and then sent `code.commit`." | none. | (observed: `plans/night130-read.md`, line 152) |

### Group F. Long replies, loops and re-reads

| # | Limit | Frame | Evidence, verbatim | Fix | Mark |
|---|---|---|---|---|---|
| F1 | A reply repeats one call or one definition until the output budget ends. | nights 118 and 119, s130 | "s130 turn 5 holds one `ledger.log` and 54 `tests.encode` calls, all `id='tst_echo_json_compact_5'`". "It is a repetition loop that ran to the output budget." | none recorded here. | (observed: `plans/night118-read.md` line 48; `plans/night119-read-fable.md` line 44) |
| F2 | The seat re-reads a span that is still in view. | 100 and 113, the window and the repeat door | "s190 ... re-read 286-351 at t6, t7, t9, t10, t11 and t12 with the block in view." "s32 and s196 ... each re-read with the read in view." | The repeat door stops the loop. The cause is the long reply, not the wake (night 116). | (observed: `plans/night116-read.md` lines 31 and 46; `plans/night113-read.md` line 47) |
| F3 | The seat does not restore code it removed, when a stale read says nothing is broken. | night 141 | "The seat never restored the removed loop. It saw the removed lines at turn 1 and turn 16 and wrote other code." | none recorded here. | (observed: `plans/night141-read.md`, line 100) |

### Group G. The model's own account is not evidence

| # | Limit | Frame | Evidence, verbatim | Fix | Mark |
|---|---|---|---|---|---|
| G1 | The interview answers disagree with the record. The seat names a sentence it followed, and the recorded call contradicts it. | 200 pass 2, 204, 165 | "the sentence the model names as followed disagrees with the recorded call in 3 of 4 turns." "two of the Vision Keeper's answers disagree with the record." Frame 165: "both runs say that the turn sent no call, and the record says each sent one." | The rule reads every answer against the record. | (observed: `plans/frame200-interviews.md`, 2026-10-11; `plans/frame204-interview.md`, 2026-10-12; `plans/frame165-interview.md`, 2026-10-06) |
| G2 | One word in the system text moves the seat's act at temperature 0, so one replay can show a prompt perturbation and not a meaning. | 204 and 243 | "The one-word change moved the seat from `none_found` to logging." "A temperature-0 change on s173 can be a prompt perturbation and not the meaning of the line." | none. | (observed: `plans/frame204-interview.md`; `plans/frame243-interview.md`) |

### Group H. Model and window limits

| # | Limit | Frame | Evidence, verbatim | Fix | Mark |
|---|---|---|---|---|---|
| H1 | No 8B model and no `qwen2.5:14b-q3` passes the Critic case for a test that encodes nothing. | the Critic's lever | "red on every 8B and on qwen2.5:14b-q3" | The Critic runs `gemma3:12b`, profile `local-gemma-critic`. | (observed: `plans/operating-facts.md` line 108, 2026-09-12) |
| H2 | A prompt one token over `num_ctx` loses its front, and the brief sits at the front. The model then answers as a generic assistant. | finding 79 | "A prompt that exceeds `num_ctx` by one token is cut to `num_ctx/2 + 2`, and the server keeps the tail." | `OLLAMA_NUM_PARALLEL=1`. The overflow rule stays. | (observed: `plans/operating-facts.md` lines 110 and 115, 2026-09-15 to 2026-09-18) |
| H3 | The thinking mode of `qwen3:8b` makes it unusable for the seats. | the bakeoff | "Without think:false the model decodes at 0.1 tok/s and scores 0 on frame." | `think: false` in the payload. | (observed: `plans/operating-facts.md` line 94, 2026-08-25) |

## The boundary in DECISIONS.md

`rota/DECISIONS.md` line 1186, "What deterministic checks cannot catch, and what stands there instead", draws the line once: "What no invariant can see: perfect form with wrong meaning; plausible-but-wrong judgement; drift that compounds across hops while every hop looks locally reasonable; the thing *not* done ... and the instrument's own nature — a 4/5 case is a frequency claim" (observed: `rota/DECISIONS.md`, 2026-08-29). The record names what stands there instead: "preregistered ground truth", "adversarial passes", "disagreement as signal (two models, cross-role challenges, the interview)", "the human made cheap", and "containment for the residue".

## The probe questions

`probes/frame37/q_tester.txt` and `q_developer.txt` ask about inputs only, for example "Quote the request text you were shown for echo_json, exactly as it appeared in your prompt." and "Was there anything you needed in order to decide, and could not find?" (observed: `probes/frame37/q_tester.txt`, 2026-10-15). The files hold questions and no findings.

## Counts

- Limits: 25 rows in 8 groups.
- Rows with a fix in place: A3, A4, C1, D3, H1, H3. A4's fix is in the code. This read did not find a night count for it.
- Rows with no fix or only a proposed fix: the other 19.
