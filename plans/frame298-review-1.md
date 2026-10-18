# Frame 298, review of pass 1

Reviewer on Opus, read-only, worktree `C:/Users/roman/rota_r298` at 7ec9b940
(parent 861cd414), 2026-10-18. No tracked file was edited.

**Verdict: pass 1 holds. No high finding. Six low findings, two of them for pass 3.**

## (a) Verdicts on the points

1. The row: HOLDS. The key, the class `relation`, one writer and no counter match 1.2. The op refuses a second call for the same item in one session, whatever the version. A row with a ruling id keeps the first row (probe 1).
2. The predicate: HOLDS. It fires on one request item by id, before `tick:signoff`, and drains at the row. A version move fires it again. Sign-off reads no guess (R7), but it runs after every owed guess (finding 3).
3. The refusal texts: HOLD. No text names a path the index lacks. The index-symbol text names only index grains. The no-request text does not name the right item (finding 4).
4. The L1 case: HOLDS for the gate. It counts `touch_guesses` writes and reads no grain. The qwen3.5:9b 5 of 5 rests on the new symbol text in 4 runs. The gate replay never meets that text. Keep the case in the replay set.
5. Departures: all five are right (one line each below).
6. `test_a_verb_carries_words_or_does_not_regardless_of_recipient`: CONFIRMED red at the parent. Commit e3cbfbb0 (2026-09-15) broke it.
7. Pass 3 needs four things this pass does not give: the ruling branch, a `clear` before a rewrite, the relay mode key, and the relay working set (finding 1, finding 2).

### Point 5, one line each

- `graph.json` edge: right. The namespace comes from the edges, and the Architect already writes the artefact, so law 3 gains no contact. `"rows": "single"` is display only, and `"batch"` describes a set better.
- Roles count 47 to 48 and the **Woken by** line: right. The two doc tests require them.
- Fixture label `item_id:item_ver:ruling_id:grain`: right. It copies the f-string of the op, and the fixture joins columns in SQL, so a `::` in a symbol grain does not break it.
- Python item pick: right. The SQL orders by id, and the first row that passes `_is_request_item` is the same item as `LIMIT 1` over request items.
- Billing item in the case: right. The sample repository holds no `src/click/utils.py`, and the brief allows the swap.

## (b) Findings

1. **Pass 3: a rewrite at one (item, version, ruling) merges two sets.** `rota/core/db.py:461` applies a junction write as `INSERT OR REPLACE`. A second relay of one ruling with a different path list keeps the old paths beside the new ones. Design 1.2 assumes "the same rows again". `INSERT OR REPLACE` also gives a rewritten row a new `rowid`, and design 1.2 orders sets by the first `rowid`. Severity low (no pass 1 path reaches it). PLAUSIBLE: read of `_apply_write`, and probe 1 shows the key keeps rows beside each other. Fix: in pass 3, `batches_guess` appends a `clear` write on `(item_id, item_ver, ruling_id)` before its rows, as `batches_annotate` does.

2. **Pass 3: the relay route has no hook yet.** `rota/roles/api.py:6034` sets `ruling = ""` with no branch. `_mode_key` (`rota/core/runner.py:296`) sends every Architect batch relay to `annotate`, and has no `guess:` branch. `push_working_set` has no guess-relay block with `guess` and `disputed`. `ref_resolves`, `GUESS_RELAY` and `_owner_of_ref` do not know `guess:`. Severity low (design section 6 gives them to pass 3). CONFIRMED: grep finds `tick:guess` and `touch_guesses` only at the sites of this pass. Fix: the pass 3 brief lists these sites, with the `guess:` mode-key branch before the `batch_relay` branch.

3. **Sign-off waits behind every owed guess.** `frontier_readonly` offers `tick:guess` first while any request item owes one. A seat that writes nothing holds sign-off for up to three attempts per item and per version. R7 holds in the predicate, but the order is a delay. Severity low. CONFIRMED by probe 1: with two items, `tick:guess` for `a_flag`, then for `echo_json`, comes before `tick:signoff`. With both items approved and one at a new version, `tick:guess` is alone on the frontier. Fix: none now. Count the delay on the night beside M0, in sessions between the first `tick:guess` and the `present`.

4. **The no-request refusal does not name the item.** `rota/roles/api.py:6007` says "`i1` is not a request item" for an unknown id, a delivered item and a description alike. The seat learns no id it can use. Severity low. CONFIRMED by probe 3. Fix: when no `items` row exists, say "no item `<id>`. The request is `item` in your working set".

5. **A symbol under a directory the index lacks is admitted.** `_refuse_stray_dirs` reads `paths` only. `symbols=["nowhere/x.py::y"]` wrote a row. Symbol rows are `possible`, and `batches.annotate` has the same gap. Severity low. CONFIRMED by probe 3. Fix: pass the path part of each symbol to `_refuse_stray_dirs` too, in both ops, in one later pass.

6. **Outside the points: the map tool misreads the new table.** `python -m rota.tools.map table touch_guesses` prints `columns item_id, item_ver, the, grain_kind, confidence`. The comment on `ruling_id` (`rota/core/schema.sql:339`) holds two single quotes and an apostrophe, and the map then drops `ruling_id`. The pass 3 implementer asks the map first. Severity low. CONFIRMED by the map output. Fix: reword the comment with no apostrophe, or make the map strip a `--` comment before it reads quotes.

Observed beside question 2 of the implementer report, not a defect: in qwen3.5:9b run 1 (seq 536319), the seat met the bare-symbol text twice. It then wrote one path and one symbol, and lost `src/billing/charges.py`. The "already guessed" refusal then stopped two calls that tried to add it back. The second-call rule costs a seat its own correction. Count it on the night.

## (c) Probes

All probe files are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/6977407c-6cda-4904-bd57-2ba520a13d06/scratchpad/r298/`. Each ran from the worktree with `PYTHONPATH=C:/Users/roman/rota_r298`.

1. `probe_frontier.py`: a fresh database with two draft request items and one index path. It printed the `tick:guess` and `tick:signoff` wakes after each step: two items, one guessed, both guessed, a version move, both approved. It then wrote a row with ruling id `v9` at version 1. The first row stayed.
2. `probe_old.py`: `init_db` and the `guess` predicate on copies of `.rota/clickI_night154.db`, `155` and `156`. Night 154: no fire (batch b4 of the item runs). Night 155: one fire, `confirm_default_on_eof`, a draft at version 3. Night 156: no fire (both items are contested). No old database raised an error, and no merged or delivered item fired.
3. `probe_op.py`: `batches.guess` through `sandbox.build` in mode `guess`, with an unknown id, a bare `echo_`, a bare `ECHO`, and a stray-directory symbol with a duplicate path.
4. `git archive 861cd414` into `parent/`, then `pytest tests/rota/test_roles_doc.py -k verb_carries`: `1 failed`. The same file at 7ec9b940: `1 failed, 8 passed`. A graph check of the split rule printed an empty list at e3cbfbb0~1 and `answer` at e3cbfbb0. That commit added `"prose": "quotes"` to the two `answer` edges of the Tester.
5. `pytest tests/rota/test_touch_guess.py test_frontier_order.py test_predicates.py test_identity.py`: `139 passed in 38.43s`.
6. `case_runs` in `D:/repos/rota/tests/rota/cassettes.db`, opened read-only, for `L1-AR-guess-the-code-of-a-request`. qwen3:8b: 5 of 5 live and 5 of 5 replay, `system_hash` 42a36ace in both. qwen3.5:9b: 1 of 5, then 5 of 5. The worktree holds no cassettes, so the case skipped there.

The gate did not run. No point needed it.

## (d) Usage

Reviewer estimate: about 110k input tokens, about 14k output tokens, about 124k in all. The harness line holds the exact count.
