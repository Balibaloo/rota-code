# F23 pass 1 review: commit 6e9a9f76 on f23root

Worktree `C:/Users/roman/rota_f23`, parent `ae9b99c6`. Read-only review. The new test file passes, 8 of 8. No gate run.

Verdict: the rule holds on the paths it names. Two claims of the build report are false: `config_history` has no cover, and a pipeline write does reach `messages`. One door stamps an author that is not the writing role, so a valid session can fail whole at commit. The pin catches one spelling of a second reader only.

## (a) Verdicts on the points

1. HOLDS for the pipeline. `_apply_write` has one caller, `session_commit` (db.py 1388), and it passes `result.role`. The raw paths insert rows or move `status` only. One exception is `rota/tools/faults.py` 27, which writes `closed_by` with no role. That tool is an operator tool, outside the rule. The cockpit and the testkit write no update to the five tables.
2. HOLDS for text. A write passes only when its keys are exactly `{"status"}`. Probe B: `status` plus `default_taken` is refused. `decisions` has no `status` column, so a status write cannot resolve or void a decision (probe E: OperationalError). The exception is wider than its reason (finding 4).
3. REFUTED for `messages`. `api.py` 15270 `schedule_reask` stages a pipeline write on `messages` through `_apply_write` (finding 5). The claim holds for `sessions`, `claims` and `item_parks`.
4. HOLDS at the doors. Quote: "d1 is a decisions row by principal, and you write as vision_keeper. A journal row is its author's record. Write yours under a new id." The text names the row, the table, the author role, the writing role and the next step. The commit text has no next step, because the session never hears the commit text. The supersede branch keeps the old wording (finding 7).
5. WEAK. The pin goes red only for a single-line `SELECT author FROM` or for `["author"] != ctx.role`. Probe pin: a multi-column select, `author IS NOT ?`, `!= role` and a reversed comparison all pass green (finding 6).
6. HOLDS, with one small loss. The 4 tests keep exact-equality pins, and each pin now adds the writing role. `test_challenge_evidence.py` test_6 lost the words "the reason's id" (finding 8).
7. NONE. No file under `tests/rota/cases` (25 files) or `tests/rota/fixtures` (27 files) holds the old refusal text. No tracked non-Python file outside `plans` holds it.

## (b) Findings

1. **`config_history` has no cover, and the reader raises on it.** `rota/core/db.py` 529. Severity low. CONFIRMED: probe J and probe K raise `OperationalError: no such column: id`. The table has no `id` column, so the claim "the rule covers all five" is false. `config.set` writes the table raw, so no caller reaches the error today. The coverage test asserts the set of table names only. Fix: return None for a table with no `id` column, and make the coverage test call `author_refusal` on each authored table.
2. **`frame.assign` stamps `author="frame"` under the role `architect`, so a second frame session fails whole.** `rota/roles/api.py` 17048. Severity high. Mechanism CONFIRMED: probe frame. A second Architect write over ledger row `frame_src` raised `JournalAuthorError`, and the commit rolled back the session row too (0 rows). The occurrence is PLAUSIBLE: a re-frame of a path that is not principal-decided restages the same id `frame_<slug>`. No door refuses first, so the session retries towards quarantine. The three night databases hold no frame-mode session, and no recorded case renders the path. Before the commit, the write landed. Fix: stamp `author=ctx.role` in `frame_assign`, and refuse at commit any staged `author` value that is not the writing role (finding 3).
3. **The rule never reads the author value that a write carries.** `rota/core/db.py` 547. Severity low. CONFIRMED: probe G. A developer wrote `{"author": "principal"}` on its own ledger row, and the row then belonged to the principal. Probe I: a tester inserted a decision with `author="principal"`, and the insert landed. Law 6 says a ledger row is never written on the principal's behalf. The doors stamp `ctx.role` today, except `frame` (finding 2) and `critic`, which matches its role. Fix: `_apply_write` refuses a write whose `values["author"]` is not `role`.
4. **The status exception admits any value on any authored row.** `rota/core/db.py` 514. Severity low. CONFIRMED: probe M. A tester reopened a resolved developer ledger row to `open`. Probe F: a tester closed a developer fault, and `closed_by` stayed NULL. The ruled reason is one case: a decision resolves a ledger row. This is no regression, because nothing checked before. Fix: pass only `{"status": "resolved"}` on `ledger`, staged in the same commit as a decision whose `resolves_ledger` names that row.
5. **A pipeline write reaches `messages`, and a seventh hand author check guards it.** `rota/roles/api.py` 15266 and 15270. Severity low. CONFIRMED by reading. `schedule_reask` compares `row["asker"]`, the question's `from_role`, with `ctx.role`, then stages `status` and `unresolved_note`. The check is correct, but it is a second reader of the author, outside the reach of 6. Fix: count it in the reach, and name it in the pin's `_ALLOWED` with its reason, or read it through `journal_author` over `from_role`.
6. **The one-reader pin misses most spellings of a second reader.** `tests/rota/test_f23_journal_author.py` 132. Severity low. CONFIRMED: probe pin. A regex match was found only for the two literal forms, and 7 other forms passed. Three by-hand row-author checks exist now and pass green: `sandbox.py` 2577 `_holds_decision`, `sandbox.py` 2591 `_without_own_reasons`, and `api.py` 15266. Fix: scan SQL strings for `author` beside `WHERE id = ?`, and comparisons of any `author` subscript, then list the 3 sites in `_ALLOWED` with reasons.
7. **The supersede branch keeps a second wording of the same refusal.** `rota/roles/api.py` 14197. Severity low. CONFIRMED by reading. The text reads "{id} is a decision by {author}" and does not name the writing role. The other two doors use the rule text. Fix: build the first sentence of `again` from `author_refusal`.
8. **The reason door no longer says that the id comes from the seat's words.** `rota/core/sandbox.py` 2759. Severity low. CONFIRMED by the test diff. The old text began "the reason's id {rid}". The remedy "Write the reason in your own words" works because the id hashes the words, and the seat no longer hears that link. Fix: put "the reason's id" before the rule text at this door.

Counts: high 1, low 7.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b3bc8a66-bd69-4749-a050-07bdd1893c24/scratchpad/f23rev/`. Each probe ran with `PYTHONPATH=C:/Users/roman/rota_f23` against a fresh `init_db` database.

- `probe_p2.py`: direct `_apply_write`, `journal_author` and `author_refusal` calls. Cases A to M: a status-only write, status plus text, key case, empty values, a decisions status write, a fault close, an author reassign, a forged insert, `config_history`, an empty role and a reopen.
- `probe_frame.py`: `session_commit` as `architect` over a ledger row with author `frame`. Result: `JournalAuthorError`, the row unchanged, 0 session rows.
- `probe_pin.py`: loads `_SECOND_READER` from the test file and matches 9 reader forms. Result: 2 match, 7 do not.
- Read-only queries on `C:/Users/roman/rota_night/state/clickI.db`, `clickI_prev.db` and `clickI_warm.db`: ledger authors and session roles. No `frame` author, and no frame-mode session.
- `pytest tests/rota/test_f23_journal_author.py`: 8 passed.
- `git grep` for the raw UPDATEs on the five tables, for staged writes whose author is not `ctx.role`, and for the old texts under `tests`. `rota.tools.map` for the writers of the 9 tables.

## (d) Usage

Input tokens: about 78k. Output tokens: about 14k. Total: about 92k. The figures are estimates from the context counter. The review ran past the 70k cap, partly on a heredoc retry.
