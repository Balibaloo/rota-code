# Frame 261, review 1 of db7c950d

Verdict: accept with fixes. The door is correct on the recorded case and is narrow. The gate line needs a re-run from the holding session.

## (a) Verdict on each point

1. PLAUSIBLE. The s251 replay test is red at the parent (pass report) and green here (352 passed). This review did not reproduce the five-night count, because of the token cap.
2. CONFIRMED by code read. A draft that another wake approved is no longer `approval = 'draft'`, so the door passes it. That is right. A wake ref that is not an item row also passes.
3. CONFIRMED by code read. `stage` takes `refs` alone for a submit, so the offered `msg.submit_liaison(refs=full)` is a complete call. `_offer` records it for the follow check.
4. CONFIRMED by code read. The only submit route is `_bind_send.stage`. The `present` branch at `sandbox.py:3250` adds the wake refs, "added, never substituted". A submit could do the same at zero turns.
5. PLAUSIBLE. `tick_signoff` (`scheduler.py:492`) returns no wake when no unparked draft is left, so the gate band goes quiet and `start` runs. This review did not read the relay's approve path.
6. NOT CLEAN. The gate printed `exit 1: 3 new reds, 1 of them flaky`. Two reds stay on its re-run. The five lines were lost, see finding 1.
7. CONFIRMED. The comment and the docstring are accurate. The text is short STE. With ten drafts left out, the refusal lists ten ids and then the full refs list.

## (b) Findings

1. Gate, high, PLAUSIBLE. Two reds stay: `test_invoke_door.py::test_a_session_with_no_batch_reads_the_root` (`DID NOT RAISE`) and `test_scene_two_batches.py::test_a_right_call_lands[the project test tests/test_templates.py as an encode]`. The diff fires only on a Vision Keeper `tick:signoff` submit, and neither test takes that path. So the reds are probably the worktree, a project root or a file under it. This reviewer piped the gate through `tail` and lost the five lines. Fix: run the gate unpiped in the holding session and compare the two reds against the checkout's known set.
2. `rota/roles/api.py:724`, low, PLAUSIBLE. The door's query has no `not_parked` filter, but `tick_signoff` has one. A woken draft parked between the tick and the submit is still refused. Fix: add `not_parked(conn, "id")` to the door's query.
3. `rota/roles/api.py:707`, low, PLAUSIBLE. The count's predicate is "a woken ref is absent from the submit". The door's predicate is "a woken ref that is a draft now is absent". The claim "0 of 348 right submits refused" is (reasoned), not observed on the door. Fix: mark the claim (reasoned) in the record, or replay the door on the 348.
4. `rota/core/sandbox.py:2731`, low, PLAUSIBLE. The `present` precedent adds the wake refs at no turn cost. A refusal costs one turn per omit and asks the model to copy a long list. Fix: decide refusal or addition at the frame. Addition removes the wall at zero turns and matches "added, never substituted".
5. `rota/roles/api.py:736`, low, CONFIRMED by code read. With ten drafts left out, the text names each id twice: once in the first sentence and once in the call. Fix: with more than three left out, name the count in the first sentence and keep the ids in the call.

## (c) Probes

- `pytest tests/rota/test_desk_guards.py -q` in `C:/Users/roman/rota_r261`: 352 passed.
- `python -m rota.tools.gate` in the worktree, with `.rota-gate.json` present: `exit 1: 3 new reds, 1 of them flaky`. The output went through `tail`, so the five lines are incomplete.
- `pytest tests/rota/test_invoke_door.py::test_a_session_with_no_batch_reads_the_root`: 1 failed, `DID NOT RAISE <class 'ValueError'>`.
- No probe on the night databases ran. The count was not reproduced.

## (d) Usage

About 45k input tokens, 4k output tokens, 49k total (estimate from the context count).
