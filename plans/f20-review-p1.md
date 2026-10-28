# Review of F20 and F21, commit ba128953 on f20root, pass 1

Verdict: the reader and the lift hold. One high finding is about scope, and five low findings are about words and stray deletes. The commit breaks no rule of frame 87 or frame 318. The five new tests pass (`5 passed in 6.21s`).

## (a) Verdicts on the points

1. Holds. No key form relied on the wildcard. Batch, item and ledger keys still lift on a move, with one ref or a list. Keys with an empty ref and survey keys never lifted on a row move, before or after.
2. Holds. No state write can lift a key that frame 318 protects. The head write keeps its old path, and ledger and item writes reach only keys that name the ledger or item id.
3. Holds. Each caller is on its old view. `_survey_wakes` changed on purpose. `_abandoned` now drops a key with an empty ref, and no caller asks for one.
4. Open, finding 1. Only a commit on b_3 or a moved criterion or test of b_3 lifts the key. The page says "Stuck. The team gave up: the team could not write the tests for b_3 after 3 attempts."
5. Partly. The five new entries are plain words. Kinds with no entry fall back to a phrase with no verb, and some refs stay internal (findings 2, 3, 4).
6. Two places left. Three deletes of quarantined keys skip `lift_keys`, and `invariants.i6` parses keys by its own rule (findings 5, 6).

## (b) Findings

1. `rota/roles/principal.py` 441-448 and `rota/core/db.py` 656-674. Severity high. CONFIRMED. On the night 170 copy, a ledger write, a ledger status move and an item approval move all left `tester|tick:tests_missing|b_3` quarantined. A head write on b_3 lifted it. The key names b_3 alone, so no answer of the principal reaches it unless the answer moves a criterion or a test of b_3. The page tells him "Tell me what to change", and his three answers of night 170 (m92, m98, m103) are the same kind. So this commit does not change the end of night 170. The audit counts that end as F20 night evidence. Fix: name the exit on the gave-up line ("a new commit or a changed check starts it again"), or let a ruling on the item of a running batch lift that batch's seat keys, in its own frame.
2. `rota/roles/principal.py` 1793 (`_tick_words`) and `rota/roles/api.py` 16510. Severity low. CONFIRMED. A kind with no entry reads "a step of the team for program after 3 attempts". The phrase has no verb, and `@program` becomes "program", an internal name. The kinds `orient`, `frame`, `reorient`, `blindspot`, `define`, `slicing`, `criteria` and more have no entry. `code_gaps` said "The Vision Keeper could not finish work on program" before, so its fallback lost its verb. Fix: make the fallback "the team could not finish a step", and give `_ref_words` words for `@program`, `@frame`, `@reorient` and `@blindspots`.
3. `rota/roles/principal.py` 1717-1730 (`_gave_up_words`). Severity low. CONFIRMED. The refs of a `tick:agenda` key are ledger ids. The page reads "a question to you got no answer for l_c1e73d2ef4, l_910f9907ba". These ids are rota's keys, not his words. Fix: drop ledger ids in `_ref_words`, or say the count of questions.
4. `rota/roles/principal.py` 445. Severity low. CONFIRMED. The line reads "The team gave up: the team could not write the tests". The subject comes twice, because the new entries start with "the team". Fix: open the line with "Stuck:" and the capitalised parts, without "The team gave up".
5. `rota/core/db.py` 687-689, 912-914 and 919-920, and `rota/core/scheduler.py` 423. Severity low. CONFIRMED by a read. These four deletes remove quarantined keys outside `lift_keys`. The three in `db.py` still match with LIKE, so `_` is a wildcard and case does not count, which is frame 242's first point. The pass report calls `lift_keys` "the one delete". Fix: read the keys through `quarantined_keys(conn, batch, kind=...)` and delete them through `lift_keys`, with a separate delete for the live counts.
6. `rota/tools/invariants.py` 197-204 (`i6`). Severity low. CONFIRMED by a read. The invariant reads quarantined keys with its own SELECT and its own split. The pass report does not list it. Fix: use `quarantined_keys` and `key_parts`.

Outside the points: none beyond findings 5 and 6.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/c66eae69-d69c-45cb-8d68-947dc45d2ac1/scratchpad`. Each ran on a copy of `clickI_night170.db`, never on the file.

- `f20_probe1.py` on `n170_copy.db`: it printed the tick rows, the batches, the ledger, `render_state`, `quarantined` and `park_ask`. The page line is in point 4. Both predicates return no wake.
- `f20_probe2.py`: it ran `write_state` for a same-value ledger write, a ledger status move, an item approval move and a b_3 head write, each on its own copy. Only the head write lifted the key.
- `f20_probe3.py`: it added seven quarantined keys of other kinds and printed `_gave_up_words`. The output is in findings 2 and 3.
- A message query on the copy: it read m92 to m105, the principal's three last answers.
- `pytest tests/rota/test_f20_quarantined_keys.py -q` in the worktree: 5 passed.

## (d) Usage

The harness shows no split into input and output tokens. The session counter moved from 15,000,000 to about 14,925,000, so about 75k tokens in total. That is past the cap of 50k.
