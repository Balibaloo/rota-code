# Frame 144, pass 1: offers as data, the dry run, and the follow check

Meta workflow. Pass 1 of frame 144, the night databases are not a test tier. The implementing agent on Opus wrote this record on 2026-10-05. It builds change 1, parts (a), (b) and (c), of `plans/frame144-design.md`. Part (d), the fact check, is the next pass.

## The mechanism as built

- `api._offer(ctx, said, op, args, then=())` returns `said` unchanged and appends an `api.Offer` to `ctx.offers` (observed: `rota/roles/api.py`, 2026-10-05). The offer holds the op, the arguments, the calls that the same sentence names after it, the door's file, line and function, and the sentence.
- No refusal text moved. Each site wraps its existing f-string, or records the offer beside the raise (observed: `git diff`, 2026-10-05). The gate's stale line is the check.
- `api.INVENT` marks an argument that the seat must invent. The follow check gives an id a fresh value, `x_follow<n>_<key>`. An invented text or body has no fresh value, so the offer is not sent and the record says so.
- `api.AGAIN` is a step of `then` that sends the refused call again, unchanged. It fails only when it meets the first refusal again. A later door's refusal of the seat's own arguments is that door's fact, and the first call meets it too (reasoned: "then send this encode again unchanged" promises only this door).
- `Sandbox.call` clears `ctx.offers` at the start of each call. `ctx.refusals` is never cleared per call, so no equal site exists (observed: `sandbox.py`, `_bind`, 2026-10-05).
- `api._admits` now drops the offers that its own dry run records, because they are not the outer refusal's.
- `sandbox.dry_run(sb, op, args, then=())` sends the calls through `Sandbox.call` on the real `ctx`, then restores `ctx`. It returns `(admitted, refusal, call, step)`. No door calls it.
- `sandbox.follow(...)` runs `dry_run` for each offer of one refusal and returns one record per offer: the door, the sentence, the refused call, the refusal, the offer and the second refusal.
- `sandbox._ON_REFUSAL` is None in a session. `Sandbox.call` calls it only on a `ValueError` whose call recorded an offer. So the behaviour that a seat meets does not change (reasoned: the hook is the one added branch, and it is dead when None).
- `tests/rota/conftest.py` wraps `pytest_runtest_call` for every test in `tests/rota`. It sets the hook, collects the follow records, and fails the test when an offered call is refused, unless `KNOWN_REFUSED_OFFERS` names the finding. `ROTA_OFFER_LOG=<file>` writes one JSON line per followed offer.

## The fields of `ctx` that the dry run copies

Every attribute in `vars(ctx)` except `conn`, deep-copied, and restored in place so that a list, a dict or a set keeps its identity (observed: `_ctx_snapshot`, `_ctx_restore`, 2026-10-05). That covers the dataclass fields `writes`, `outbound`, `opened`, `lookup_misses`, `read_words`, `read_idents`, `refusals`, `kind_facts`, `verdict_claims`, `cuts`, `diff_files` and `offers`, the scalars, and the attributes that `build` and the ops add: `triaged`, `intake`, `area_hash_at_wake`. An attribute that the dry run adds is deleted. The module's `_CALL_LOG` entry for the `ctx` is cut back to its length. `conn.total_changes` is read before and after, and a change raises `RuntimeError`, because the restore cannot undo a database write (reasoned: no op writes the database, by the judge's read of `api.py`).

The three ops outside `ctx`:

- `code.write` runs `api._code_write(..., dry=True)` after the binder's argument check. The dry mode returns before the disk (frame 136). The dry run takes `_code_write` at import, so a test that spies on it counts its own calls only.
- `code.commit` runs git, which has no dry mode here. `dry_run` raises `DrySkipped`. No offer names it today.
- `web.fetch` reads the network. `dry_run` raises `DrySkipped`. No offer names it today.

## The sites

45 offer sites at c888968, 42 in `api.py` and 3 in `sandbox.py` (observed: an ast count of the calls of `_offer` and `_send`, less the helper's own call, pass 2, 2026-10-05). The first count, 47 by grep, was wrong.

Converted:

- `tests.encode`: the triage step, then the call again. The added import line. The three exits of the written-back sentence (`msg.question_terminologist`, `msg.question_vision_keeper`, `schedule.reask`). Both `ledger.log` steps, then the call again. Frame 135's project-id door, both branches (its own file, and a new id). The stored path. The other batch's id, as a new id. The same criterion's clash, as the stored id.
- `tests.triage`: the contradicts-request call.
- `criteria.specify`: an item sent as a ticket, with a new id and the first ticket.
- `ledger.log`: the right `about_table`.
- `verdicts.emit`: `verdicts.claim_encodes(encodes=True)`, then the call again.
- `glossary.amend`: two sites that name `surveys.attest(outcome='none_found')`.
- `code.write`: a start with no end, a span of a file that does not exist, the cut door's offers (10), the whole parent, the insert after, the replace whole and the add after, the `__future__` door, the docstring door, the cross-block door's whole statement and top level, D, and both of `_span_lost_refusal`'s calls.
- `sandbox.py`: `brief.intake(verdict='work')`, `msg.report_liaison` with the same refs, and the unique-id door in `_bind` with a new id.

The boundary offers of the cut and cross-block doors mark `text` as `INVENT`. The sentence names the numbers, and the text that fits them is the seat's to write (reasoned: "To replace f whole" asks for a whole new f). Those offers are recorded and not sent. The insert offers ("To add after ...") keep the seat's text.

Not converted, each because the named call has no argument that the door knows, or names no call:

- The route exits that name an op with no arguments: `decisions.author` (problem.describe, 2), `glossary.amend` and `glossary.same` (glossary.synthesise, 2), `msg.report_liaison` (glossary.same), `code.source` and `code.area` (model.amend, 4; surveys.attest, 2; glossary.amend, 1), `msg.challenge_vision_keeper` (model.amend, criteria.specify), `model.consult` (findings.find), `problem.prioritize` (batches.group), `msg.challenge_tester` (verdicts.claim_encodes, code.write, code.commit, verdicts.emit's second exit), `msg.escalate_architect` (code.commit), `challenge.load` and `challenge.vacuous` (challenge ops), `msg.converse_principal` (brief.segment), `rulings.rule` and `ledger.unaddressed`, `schedule.reask` (the relay), `brief.segment` (3 sites), `code.diff`, `code.commit` (2 sites in `_escalation_over_removed_grain`), `tests.encode` in `_answer_evidence`.
- The calls whose arguments the seat composes: `problem.assert(id=..., text=...)` (surveys.attest), `surveys.attest(..., citations=[the file])` (ledger.log), the bindings pattern of model.amend, the monkeypatch bodies of five `tests.encode` walls, the quotes of `_challenge_evidence`, the one assumption of a page, the dict-wrapped ref.
- The drops refusals and the unnamed-definition refusal of `code.write`: "write only your new definition" names a text that the seat writes.
- The notes that are results and not refusals: four `surveys.attest` lines in `code.survey`, `code.vocabulary`, `prose.reconcile` and `frame.assign`.
- The repeat doors of `_bind_send` that say "do not send this again" or "end the session".

## The counts

Over the first full gate run with `ROTA_OFFER_LOG` set (observed: `offers_all.jsonl` in the agent's scratch area, 2026-10-05):

- 69 existing tests met a refusal that recorded an offer. They recorded 184 offers.
- 113 offers were sent, in 64 existing tests. The doors admitted 105 and refused 8. The 8 are the three findings below.
- 71 offers were not sent, because their text is the seat's to write (the boundary offers of `code.write`).
- 18 `AGAIN` steps met another door's refusal of the seat's own arguments. The follow check counts those as admitted, by the rule above.
- 73 of the 184 offers came from L1 and L3 cases that replay recorded sessions through the runner. So the hook sees a seat's own refusals on a replay (observed: the log's test ids, 2026-10-05).
- The new file `test_offers_followed.py` adds 11 tests, 3 of them strict xfails (corrected in pass 2 from 12, observed: `grep -c "^def test_"` at c888968).

## The offers that fail today

Each is a strict xfail in `tests/rota/test_offers_followed.py` and a line in `KNOWN_REFUSED_OFFERS` (observed: the follow check on `test_t0_sandbox.py` and `test_desk_guards.py`, 2026-10-05).

1. **`tests_encode`, frame 135's project-id door, the branch outside a challenge.**
   - First refusal: "inh_022b8a87 is the id of the project's test tests/test_utils/test_confirm.py. An encode never replaces a project test. Send this encode again with a new id that you invent."
   - Offer: `tests.encode(id=<new>, criterion_id='c1', path='tests/test_utils/test_confirm.py', body=..., batch_id='b1')`.
   - Second refusal: "tests/test_utils/test_confirm.py is already inh_022b8a87's file; two tests in one file overwrite each other on disk. Name this one for its own criterion -- tests/test_<what it checks>.py".
   - Met by `test_a_project_id_at_its_own_path_is_refused_outside_a_challenge`, `test_a_challenge_of_another_test_does_not_open_a_project_test` and `test_a_project_id_on_another_tests_file_gets_the_id_fact_only`. The last one's docstring accepts two refusals in a row as frame 135's design ("The clash door answers the path on the next call, in its own words"). The judge decides whether the first two are the same accepted case.
2. **`_code_write`, the cut door, "To add after it send start=, end=."**
   - First refusal: "start=3, end=6: start=3 falls inside f (lines 0 to 6 in code.source numbering). ... To replace f whole send start=0, end=6. To add after it send start=6, end=6."
   - Offer: `code.write(path='m.py', text='def f():\n    return 1\n', start=6, end=6)`.
   - Second refusal: "m.py defines f twice (lines 4 and 7). Python keeps the last one and the first never runs. ..."
   - The same sentence fails on `test_a_span_from_the_top_into_the_first_statement_gets_no_moved_boundary` (the text does not parse alone) and `test_a_span_from_a_blank_line_before_else_is_refused_with_an_offer` (an `else:` text). The seat's text was a replacement, and the sentence offers to add it after the statement.

3. **`tests_encode`, the unimported-module wall, "Add the line `import pytest` at the top of the body and send the encode again".**
   - First refusal: "the test uses pytest and never imports it: a NameError against any code. Add the line `import pytest` at the top of the body and send the encode again".
   - Offer: the same encode with `import pytest` as the body's first line.
   - Second refusal: "the test chooses 'default_answer', and nothing in the criterion, its ticket, the glossary or the principal's words says it. That is an assumption, and it is logged where it is made: ledger.log(...) -- then send this encode again unchanged".
   - Met by the replay of `ACT-TS-give-the-prompt-a-stream` in the full gate. The second refusal is a later door's fact about the seat's own literal. The original call meets it too, once the import is there. The judge decides whether two refusals in a row is the accepted shape here, as frame 135 accepted it for the clash door.

## The two proofs

1. **The `_admits` guards in `_span_lost_refusal` removed** (both replaced by a constant, then reverted). Three tests went red: `test_a_span_refusal_names_no_call_the_doors_refuse`, `test_a_dry_run_leaves_the_context_and_the_disk_as_they_were` and `test_a_crash_in_a_dry_run_names_no_call_and_is_logged` (observed: `pytest tests/rota/test_desk_guards.py tests/rota/test_night46_context.py`, 2026-10-05). Each went red by its own assertion. The follow check did not go red. Those three tests make `_admits` refuse by a monkeypatch, and the follow check sends the offer through the real doors, which admit it. A probe state that I built, a span that removes a used import with a text that redefines `f`, met an earlier door first ("defines f twice"). No state in the suite has an A1 or A2 offer that the real doors refuse (reasoned: the frame 136 doors move the insert point below the docstring, the `__future__` lines and the coding lines, which removes the cases that I tried). The design names S6 as the state that holds this proof.
2. **Frame 135's pass 4 condition removed** (`and id in refs_of(msg["body_refs"])`, a71951a, then reverted). One test went red: `test_t0_sandbox.py::test_a_challenge_of_another_test_does_not_open_a_project_test` (observed: 2026-10-05). It went red by its own `pytest.raises`. The follow check did not go red, because the encode lands and no refusal and no offer exist (reasoned: a follow check reads refusals only).

`git diff` shows neither removal (observed: grep for both guards and the condition after the revert, 2026-10-05).

## The suite

The gate on the tree of commit c888968 (observed: `python -m rota.tools.gate`, 2026-10-05):

```
suite: 23 failed, 2733 passed, 27 skipped, 4 xfailed, 19 warnings (baseline: 23 failed, 2324 passed, 27 skipped, 1 xfailed, 16 warnings)
new reds (3): tests/rota/test_l1.py::test_l1_case[L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist], tests/rota/test_l1.py::test_l1_case[L1-TS-fix-a-test-that-calls-a-plain-function-through-a-runner], tests/rota/test_map.py::test_mode_lists_its_base_file_and_joins_every_line
reds gone (3): tests/rota/test_l1.py::test_l1_case[L1-AR-annotate-a-batch], tests/rota/test_l1.py::test_l1_case[L1-DV-fix-what-the-verdict-names], tests/rota/test_l3.py::test_l3_chain[L3-a-failed-verdict-turns-into-a-fix]
stale (0): none
time: 616.6s, model qwen3:8b, temp root C:\Users\roman\rota_gate\tmp, baseline 658abb6 2026-09-27 19:24
```

The three new reds fail the same way with this pass's changes stashed, at 5ca1fa8 (observed: the three tests run on the stashed tree, 2026-10-05). The baseline is from 2026-09-27, so they are reds of the tree since then, not of this pass.

## What the follow check cannot see

- A wrong call that a door admits. The follow check runs only on a refusal, so proof 2 is outside it. That is design change 1(c)'s second half, the invariants on the staged result, and item 4.
- A refusal that a test meets by `api.op(ctx, ...)` directly, outside `Sandbox.call`.
- A refusal inside a runner session that a test drives with a scripted backend: the hook sees it, because the runner calls `Sandbox.call`. A refusal that the runner raises itself (A5) names its calls in prose and records no offer.
- An offer whose text or body the seat must write. It is recorded and not sent.
- A refusal that names a call with no arguments, listed above as not converted.
- A door whose guard simulates a refusal by a monkeypatch. The follow check uses the real doors.
- The truth of the facts in a refusal. That is part (d), the next pass.
- The state of a night. The follow check runs on the states that the tests build. The scenes of item 3 are the wider states.
