The dropped snapshot: `checkpoint_invalid` is the discharge half of the suspend-and-resume design that `plans/composition.md` drops, and no code path ever writes the row it reads.

All paths below are relative to `D:\repos\rota`. Line numbers are from the working tree on 2026-09-16.

## Evidence

The page and the design it drops:

- `plans/composition.md:57` — "A seat restarts from records. There is no snapshot."
- `plans/composition.md:105` — "A seat restarts from records. The snapshot design is dropped."
- `plans/composition.md:103` — "Checkpoints are opt-in" uses the word in a different sense: a point where the Principal spends attention. That sense is not the `checkpoints` table.
- `plans/composition.md:120-123` — the open check this report answers.
- `rota/HANDOFF.md:90-93` — the original law 5: "suspension is a cache", a checkpoint holds the working set's version stamps, receipts "allow patched resume". This is the snapshot design.
- `rota/LAWS.md:166-174` — law 5 as rewritten on 2026-09-13: the table and its invalidation exist, "no session writes a checkpoint and nothing resumes from one", the patched resume was "never built".
- `rota/LAWS.md:184-185` — law 6: "Nothing routes a counter-question into a suspended session". The other consumer of a suspended session is also gone.
- `rota/LAWS.md:247-250` — law 9: preemption "discards its checkpoint". The word names the derived state that dies on deferral.
- `rota/LAWS.md:254-256` — law 10: a readonly session "cannot revoke anything or invalidate any checkpoint".
- `rota/LAWS.md:360` — the law 5 check row names `scheduler.sweep_checkpoints` and admits it "invalidates the checkpoints nothing resumes from".
- `rota/REGISTER.md:29` — the register list carries `checkpoint_invalid`. `rota/REGISTER.md:20-22` counts the entries.

The predicate and what it reads:

- `rota/core/predicates.py:1223-1231` — `checkpoint_invalid` selects `session_id, role FROM checkpoints WHERE valid = 0` and returns `Wake(role, "tick:checkpoint_invalid", detail=session_id)`. Its docstring says "the suspended role must restart cold".
- `rota/core/predicates.py:1223` — declared with `wakes=DERIVED`, `band="fix"`, no `drains` and no `derives`. Nothing declares what discharges it, and the mode-coverage check cannot see which role it wakes.
- `rota/core/predicates.py:1482` — `REGISTER_ENTRIES` names it, so `outstanding()` (`:1507`) folds it into "what the system owes".
- `rota/core/scheduler.py:1331-1332` — `tick_key` is `role|kind|refs`. The wake carries no refs, so every invalid row for one role shares one key, and the cap quarantines them together.
- `rota/core/runner.py:213-214` — a tick wake's mode is the kind after `tick:`, so the mode would be `checkpoint_invalid`. No file under `rota/roles/prompts/` has that name, and `rota/design/graph.json` has no such mode. The wake has no brief.
- `rota/core/runner.py:239` — `DETAIL_SHOWN` is `{"tick:tests_missing"}`, so the session id in `detail` would not reach the role.
- `tests/rota/walks.jsonl` — zero mentions of `checkpoint_invalid`. It has never fired in a recorded walk.

Every writer and reader of `checkpoints`:

- `rota/core/schema.sql:620-629` — the table: `session_id`, `role`, `batch_id`, `working_set` as `[[table, version], ...]`, `valid`. The `working_set` is the snapshot's validity key.
- `rota/core/db.py:191` — `SessionResult.checkpoint: dict | None = None`.
- `rota/core/db.py:468-478` — `session_commit` inserts a `valid = 1` row when `result.checkpoint is not None`, else deletes the claim: "a suspended one keeps it". This is the only insert in the package.
- `rota/core/runner.py:2244-2264` — the single `SessionResult(...)` construction in the package passes no `checkpoint`. No other module constructs one.
- `grep "checkpoint\s*=" rota/ tests/` — zero hits outside the predicate name. `git log --all -S "checkpoint=" -- rota/` — no commit on any branch ever passed the field. The audit claim at `plans/lost-work-audit.md:28` holds today.
- `rota/core/scheduler.py:1606-1622` — `sweep_checkpoints` sets `valid = 0` where a stamp is behind `artefact_versions`. It only invalidates; it never resumes.
- `rota/core/lifecycle.py:110` and `:132-133` — `defer` and `abandon` set `valid = 0` by `batch_id`. Both are no-ops on the always-empty table.
- `rota/core/boot.py:31, 206` — boot imports and runs `sweep_checkpoints`; `:40, 47` report the count; `:15` lists it as step 5.
- `rota/core/boot.py:70-74` — `reap_claims` left-joins `checkpoints` so a "suspended" session keeps its claim. Without suspension the join is dead.
- `rota/core/identity.py:104` — classifies `checkpoints` as `ephemeral`, "dies with deferral; valid=0 is the record". `batches.status = 'deferred'` is already that record (`lifecycle.py:109`).
- `rota/cockpit/server.py:138`, `rota/cockpit/static/panels.js:712`, `rota/cockpit/viewer.html:429` — the cockpit reads and renders the table. Display only.
- `grep -i resume rota/ --include=*.py` — the only `resume` function is `config.resume` (`rota/core/config.py:321`), the run-state pause switch. Nothing loads a checkpoint.

The tests:

- No test calls `checkpoint_invalid()`. `grep checkpoint_invalid tests/` returns nothing. The predicate itself has no direct test.
- `tests/rota/test_t0_plumbing.py:348-357, 360-369` — T0-S7: `sweep_checkpoints` keeps a disjoint stamp valid and invalidates an overtaken one.
- `tests/rota/test_t0_plumbing.py:516-522` — `test_boot_keeps_suspended_claim`: a `valid = 1` row keeps its claim through `reap_claims`.
- `tests/rota/test_delivery.py:107-125` — `lifecycle.defer` keeps the worktree and sets the row to `valid = 0`.
- `tests/rota/test_predicates.py:1594-1598, 1627-1635` — the preempt test inserts a row in `_two_batches` and asserts `valid = 0` after `do:preempt`. `:1641-1643` docstring names the checkpoint as the cost of preemption.
- `tests/rota/test_t1_liaison.py:239-240, 258-261` — I4 inserts a developer row and fails if a readonly session disturbs it. I4 is a recorded case (`record_case_run`).
- `tests/rota/test_predicates.py:818` — pins `len(REGISTER_ENTRIES) == 27`.
- `tests/rota/test_roles_doc.py:143-165` — parses the list under "**sixteen are register entries**" in `REGISTER.md` and asserts it equals `REGISTER_ENTRIES`. `:176` pins the total predicate count at 43.
- `tests/rota/test_identity.py:28-32` — refuses a `NATURAL_KEYS` entry for a table not in the schema, so `identity.py:104` must go with the table.
- `tests/rota/test_environments.py:324-325` and `tests/rota/cases/l1_answers.yaml:211` — prose only.

## Recommended ruling

Rule that `checkpoint_invalid` is the dropped snapshot. The register entry is an obligation that cannot arise: no seat suspends, so no seat owes a cold restart. Remove the predicate, the register line, the `checkpoints` table, and every reader and writer of the table in one frame. Rewrite law 5 to the page's sentence: a seat restarts from records, and a deferred batch restarts from its rows. Keep the law 9 split between durable product and derived state, in words that do not say checkpoint. Approve the LAWS text before the agent lands the code. Re-record I4 after its fixture changes.

## Change set

Order: Roman approves the LAWS text (1). One agent lands code and tests together (2, 3), runs `tests/rota/`, runs the cockpit lens check, and re-records I4. Docs follow (4). Existing run databases keep an empty `checkpoints` table, because `init_db` uses `CREATE TABLE IF NOT EXISTS` and has no migrations. Nothing reads it after the change, so no migration is needed.

1. Laws and register (Roman rules first):
   - `rota/LAWS.md:166-174` — rewrite law 5 body. Drop the sentence that names the table, `lifecycle.defer` and `checkpoint_invalid`.
   - `rota/LAWS.md:248` — "and discards its checkpoint" becomes "and its environment dies with it".
   - `rota/LAWS.md:255-256` — drop "or invalidate any checkpoint".
   - `rota/LAWS.md:360` — replace the check with one that exists after the change, for example: "`schema.sql` has no `checkpoints` table; `SessionResult` has no checkpoint field; `lifecycle.defer` writes `batches.status` only".
   - `rota/REGISTER.md:29` — remove `checkpoint_invalid` from the list. Keep the anchor phrase "**sixteen are register entries**" at `:20`, or change `tests/rota/test_roles_doc.py:143-144` with it. Fix the count prose at `:20-22` (twenty-six after the change).

2. Code:
   - `rota/core/predicates.py:1218-1231` — delete the "Runtime" header and `checkpoint_invalid`.
   - `rota/core/predicates.py:1482` — remove `"checkpoint_invalid"` from `REGISTER_ENTRIES`.
   - `rota/core/predicates.py:1169` — `preempt` docstring: "a preemption discards a checkpoint" becomes "a preemption kills the environment".
   - `rota/core/scheduler.py:1602-1622` — delete `sweep_checkpoints` and its header. `:5` — "claims and checkpoints are rows" becomes "claims are rows".
   - `rota/core/boot.py:15, 31, 40, 47, 206` — delete step 5, the import, the report field, the summary field, the call. `:70-74` — drop the `LEFT JOIN checkpoints` and `AND k.session_id IS NULL` from `reap_claims`.
   - `rota/core/db.py:191` — delete `SessionResult.checkpoint`. `:379` — drop "and checkpoint". `:468-478` — replace the branch with the unconditional `DELETE FROM claims WHERE session_id = ?`.
   - `rota/core/lifecycle.py:110, 132-133` — delete the two `UPDATE checkpoints`. `:8, 11, 95-103` — reword the docstrings: the environment dies, the worktree lives.
   - `rota/core/schema.sql:620-629` — delete the table. `:477` — drop "checkpoints" from the comment.
   - `rota/core/identity.py:104` — delete the `"checkpoints"` entry.
   - `rota/cockpit/server.py:138` — delete the `checkpoints` row. `rota/cockpit/static/panels.js:712` — delete the table. `rota/cockpit/viewer.html:429` — heading becomes "Claims / ledger". Run the lens check, not only `node --check`.
   - Comments only: `rota/core/environments.py:10-16`, `rota/core/loop.py:294`, `rota/core/sandbox.py:15-16`, `rota/roles/api.py:7269, 8042-8044`. Say "environment" or "derived state" where they say "checkpoint".
   - `rota/tools/vocabulary.py:90` — optional. `"checkpoint"` in `MACHINE_MARKERS` still catches the word if it returns to a brief. Keep it.

3. Tests:
   - `tests/rota/test_t0_plumbing.py:29` — drop the `sweep_checkpoints` import. `:345-369` — delete T0-S7 (both tests). `:516-522` — delete `test_boot_keeps_suspended_claim`.
   - `tests/rota/test_delivery.py:107-125` — rename to "deferring keeps the worktree". Delete `:114-116` (the insert) and `:124-125` (the assertion). Keep the `head_commit` assertion.
   - `tests/rota/test_predicates.py:1594-1598` — delete the session and checkpoint inserts from `_two_batches`. `:1627-1635` — delete the `ck` assertion; keep the worktree and status assertions. `:1641-1643` — reword the docstring. `:818` — 27 becomes 26.
   - `tests/rota/test_t1_liaison.py:239-240, 258-261` — delete the checkpoint row and the "readonly disturbed a developer checkpoint" check. Re-record I4.
   - `tests/rota/test_roles_doc.py:176` — 43 becomes 42. Add one clause to the comment at `:166-175`.
   - `tests/rota/test_environments.py:324-325`, `tests/rota/cases/l1_answers.yaml:211` — reword the comments.

4. Docs and design records:
   - `plans/composition.md:120-123` — close the open check: the entry was the dropped snapshot and is removed.
   - `plans/lost-work-audit.md:28` — disposition becomes "Done <date>: removed with the table".
   - `rota/roles/prompts/liaison/answer.md:21-22` — a brief. Drop the clause "and no checkpoint is disturbed". Measure on the register and a cold walk before it lands.
   - `rota/design/graph.json:13` — drop "and no checkpoint is disturbed" from the Liaison note.
   - `rota/design/stories.json:526, 1031, 1106, 1257` — story text: replace "checkpoint" with "environment" or drop the clause.
   - `rota/ENVIRONMENT.md:147-154` — keep the durable-versus-derived argument; say "environment" for "checkpoint".
   - `rota/TESTS.md:135` (table list), `:183` (T0-S7), `:189-190` (T0-S15, T0-S13), `:230, 235` (I4), `:270` (V3), `:427, 435` (Dev1, Dev2), `:446-459` (Dev4, Dev5) — delete the checkpoint rows and the two resume cases.
   - `rota/MILESTONE.md:141-142`, `rota/HANDOFF.md:90-93, 136, 142, 238, 255, 469` — historical. Add one line that points to the ruling, or leave as history. Roman decides.
   - `rota/DECISIONS.md:479, 950` — rulings keep their wording (CLAUDE.md exception). Leave.
   - `plans/archive/enforcement-verification.md:15`, `plans/archive/responsibility-allocation.md:59` — archive. Leave.
