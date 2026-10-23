# Frame 310, the provenance: how `criteria.specify` came to admit a second write of one id on one ticket

Reader on Opus, read-only, at the branch head 9681c5bc, 2026-10-23. Night databases opened with `?mode=ro`. No test, no gate, no re-record.

## (a) Verdict

No commit, frame, review or ruling ever decided the same-ticket admission. The admission is a gap that a9cb55de left on 2026-09-03, when it closed the cross-ticket case only. Frame 257 named this wall on 2026-10-15 and never got a fix, so frame 310 is frame 257's wall again.

Verdict on each point:

1. Since when, and why: since before a9cb55de. That commit refused another ticket only. No record decides the same ticket.
2. The version column: the commit path counts each write as an amendment. The overwrite replaces the text. Only `_park_versions` reads the number, and no seat reads an earlier text.
3. The count: 16 sessions on 12 of 20 nights. 70 admitted writes, 54 lost texts. 1 lost text shares a 4-word phrase with a ruling. 7 of 9 `echo_json` sessions lost the item's newline requirement. 0 batches died on a test that a lost text would change.
4. The neighbours: `criteria.respecify` exists, but only the `criterion_repair` mode has it. The `criteria` mode brief says nothing about ids.
5. The repair: refuse a second `criteria.specify` of an id this ticket already holds, and offer a new id. This keeps a9cb55de's sentence "An id you invent is yours once".

## (b) The commit and its reasoning

- The reused-id check entered in a9cb55de, 2026-09-03 02:50, "fix(sandbox): a criterion's id is one ticket's, and a value from the user is read". Source: `git log -S` on the predicate, in `rota/roles/api.py`.
- The message names one case only: "silently overwrote a ticket's criterion when the same id was reused for a second ticket". The predicate is `prior_ticket is not None and prior_ticket != ticket_id`, `rota/roles/api.py` 5294. The same ticket falls through by omission.
- The refusal text says more than the predicate does: "An id you invent is yours once" (api.py 5296 to 5298). The sentence states the one-id rule. The code keeps the rule only across tickets.
- No sentence decides the same-ticket admission. I searched `plans/stack.md` and `plans/archive/` for "specify" with "same id", "reuse", "overwr", "rewrit" and "replace". `DECISIONS.md` and `LAWS.md` do not exist at the repository root. No test pins the admission or the cross-ticket refusal: a grep of `tests/rota/*.py` for "yours once" gives 0 hits.
- The respecify design assumed the opposite. The `criteria_respecify` docstring, api.py 5702 to 5703, from fd788bd1 (2026-08-26), says: "`specify` inserts, so a second specify of the same id dies on the primary key inside the transaction". At fd788bd1, `rota/core/db.py` already held "Existing row -> UPDATE, not upsert" (`git show fd788bd1:rota/core/db.py`, line 237). So the premise was false when it was written.
- Frame 257, `plans/stack.md` 951 to 962, "`criteria.specify` under one id replaces the last criterion, and the merge builds to the survivor (2026-10-15)", is the same wall. Its ends-when line asks for "the call refuses a second text under a landed id or takes a new id, with s114's calls as the red test". It holds status lines from nights 149, 150, 152, 153 and 154, and no pass.

## (c) The version column

- Schema: `criteria.version INTEGER NOT NULL DEFAULT 1`, `rota/core/schema.sql` 489.
- The writer: `criteria_specify` appends a 3-tuple write, api.py 5369. `Write.amends` defaults to True, `rota/core/db.py` 285. `_apply_write` turns a write on an existing id into an UPDATE that adds 1 to `version`, db.py 482 to 493. In one session the first write inserts at version 1, and each next write updates. Four writes give version 4, as on night 160.
- The overwrite is a replacement. The UPDATE sets `text` and `surface_refs` in place. No table keeps the old text, except `rulings.texts` at the moment of a principal's ruling (schema.sql 670 to 674: "No other record keeps a criterion's old text").
- The one reader: `_park_versions`, `rota/core/scheduler.py` 1941. It hashes `id:version` pairs into the park ask id. No seat and no door reads an earlier version. The map lists no other reader of `criteria.version`.
- The comment at api.py 5870, "No reader reads a criterion's version", is wrong by `_park_versions`. This is a low point.

## (d) The count, with its query

Scope: `D:/repos/rota/.rota/clickI_night140.db` to `clickI_night159.db`. All 20 exist. Committed sessions only.

Method:

1. Find the sessions with a `criteria.specify` call:
   `SELECT DISTINCT t.session_id FROM tool_calls t JOIN sessions s ON s.id = t.session_id WHERE t.fn = 'criteria.specify' AND s.committed = 1`.
2. `tool_calls.args_summary` cuts each argument at 60 characters (`rota/core/sandbox.py` 4344), so the texts come from `turns`. Take the last turn with a user text:
   `SELECT user, completion FROM turns WHERE session_id = ? AND length(user) > 0 ORDER BY seq DESC LIMIT 1`.
   The user text holds the whole transcript of the session.
3. Pair each `TOOL: criteria.specify(...)` line with its `OK` or `ERROR` result line, in call order. Skip a line `OK criteria.specify ->` with nothing after the arrow, because the seat wrote that line into its own reply. Count only `OK` calls as admitted.
4. Group the admitted calls by `(id, ticket_id)`. A group with two or more texts is an overwrite. The lost texts are all but the last.
5. Principal words: a lost text shares a 4-word phrase with `items.text` or `rulings.words`, and the survivor in `criteria` does not hold that phrase.
6. Batches and tests:
   `SELECT b.id, b.status FROM batch_tickets bt JOIN batches b ON b.id = bt.batch_id WHERE bt.ticket_id = ?` and
   `SELECT id FROM tests WHERE criterion_id = ?`.

Cross-check: the parsed call count equals the `tool_calls` count in all 16 sessions. The admitted count equals the row's `version` where no later session moved the row: night 149 s114, 150 s119, 152 s115, 153 s115, 155 s114 and 159 s116 all read 4 writes and version 4.

| night | session | id | admitted writes | lost | 4-word hit | batch |
|---|---|---|---|---|---|---|
| 143 | s420 | ver_opt_show_py_tk2 | 3 | 2 | 0 | bg_5 abandoned |
| 144 | s526 | ver_opt_show_py | 2 | 1 | 0 | bg_5 running |
| 147 | s334 | ver_opt_show_py | 3 | 2 | 0 | bg_4 merged |
| 148 | s110 | echo_json_helper | 4 | 3 | 0 | bg_1 merged |
| 148 | s182 | ver_opt_show_py | 3 | 2 | 0 | bg_3 merged |
| 149 | s114 | echo_json_helper | 4 | 3 | 0 | bg_1 merged |
| 150 | s119 | echo_json_helper | 4 | 3 | 0 | batch_1 and batch_2 abandoned |
| 151 | s120 | echo_json_helper | 4 | 3 | 0 | bg_1 abandoned, bg_2 merged |
| 152 | s115 | echo_json_helper | 4 | 3 | 0 | bg_1 merged |
| 152 | s271 | ver_opt_show_py | 10 | 9 | 1, r_4db5597c3b | bg_3 merged |
| 153 | s115 | echo_json_helper | 4 | 3 | 0 | bg_1 merged |
| 153 | s230 | ver_opt_show_py | 10 | 9 | 0 | bg_3 running |
| 155 | s114 | echo_json_helper | 4 | 3 | 0 | bg_1 and bg_2 abandoned |
| 158 | s112 | echo_json_helper | 4 | 3 | 0 | bg_1 merged |
| 159 | s116 | echo_json_helper | 4 | 3 | 0 | bg_1 merged |
| 159 | s264 | ver_opt_show_py | 3 | 2 | 0 | bg_4 deferred |

Totals: 16 sessions, 12 nights, 70 admitted writes, 54 lost texts.

Principal words:

- By the 4-word rule, 1 of 54 lost texts holds a phrase of a principal's row. Night 152 s271 lost the text that names `sys.version_info`, which shares a phrase with ruling r_4db5597c3b. Frame 257's status line of 2026-10-16 records the same loss.
- The 4-word rule misses the paraphrase. The `echo_json` item says "followed by a newline". The lost text says "must end with exactly one newline character". In 7 of 9 `echo_json_helper` sessions, the survivor holds no newline: nights 148, 149, 150, 152, 153, 155 and 159. On nights 151 and 158 the survivor keeps the newline.
- The 9 `echo_json` sessions open with the same three texts, word for word. So the overwrite is one stable reply shape of the seat, not 9 independent events. Night 153's s115 is the same as night 152's s115.

Batches that died on a test that a lost text would change: 0 of 16 in the range.

- Night 155 bg_1: the test `inh_05f7b1750` still asserts a trailing newline (`plans/night155-read.md` 88 to 92). The batch died on other walls of that read.
- Night 151 bg_1: the test compares `output_bytes.strip()`, which ignores the newline.
- Night 150: no test names `echo_json_helper`.
- Night 143 bg_5: the lost texts give the `show_python` default, and the survivor and the test both cover the default. This one is PLAUSIBLE, from the texts and not from a read.
- The harm in the range is at the merge. Night 149 merged to the survivor, and `echo_json(None)` prints nothing (frame 257). Night 160, outside the range, is the first death.

## (e) The neighbours

- `criteria.respecify` exists: `criteria_respecify`, api.py 5696 to 5890. Its refusal texts:
  - "a criterion names what the program does; this one names the Tester's job. Rewrite it as what the script does for a valid name and for an empty or wrong one" (5716).
  - "the principal approved {id} and ruled its test {tests}. Keep the words. ... Your work on {id} is done" (5730), and the same with "Send msg.answer_tester(refs=['{id}'])" (5735).
  - The surface-move fault from `_surface_move_fault` (5785 to 5790).
  - "the principal contested {back} in this criterion. His words: ... Write what he asked for, without ..." (about 5813).
  - "the principal contested these words: ... Write what he asked for. {route}", and the same without the route (about 5852 and 5855).
  - The same words return `unchanged`, not a refusal (5858 to 5863).
- `criteria.respecify` is in `rota/roles/prompts/terminologist/criterion_repair.tools` only. `criteria.tools` does not list it. So a seat in the `tick:criteria` wake cannot call it.
- The `criteria` mode brief, `rota/roles/prompts/terminologist/criteria.md`, has no sentence on ids. It says "Three is usual and six is many" (line 33), and nothing about one id per criterion. The only id sentence the seat can meet is the item-as-ticket refusal at api.py 5240: "with a new c_ id of your own".

## (f) Findings

1. api.py 5294. High. CONFIRMED by `git show a9cb55de` and the count in section (d): the check compares tickets only, so a second text under one id on one ticket replaces the first. This happened 54 times on 12 nights. Fix: refuse when a staged or landed row holds the id on the same ticket with other words.
2. api.py 5702 to 5703. Low. CONFIRMED by `git show fd788bd1:rota/core/db.py` line 237: the respecify docstring says a second specify dies on the primary key, but the commit path already updated the row. Fix: correct the docstring in the pass of finding 1.
3. api.py 5870. Low. CONFIRMED by the map and scheduler.py 1941: the comment "No reader reads a criterion's version" is false. Fix: name `_park_versions` as the one reader.
4. `plans/stack.md` 951 and 719. Low. CONFIRMED by the stack text: frames 257 and 310 hold one wall with two ends-when lines. Fix: close one frame into the other before pass 1.
5. Frame 310's ends-when line, `plans/stack.md` 720. High. CONFIRMED by `criteria.tools`: a refusal that names `criteria.respecify` names a tool the `criteria` mode does not have. Fix: the refusal offers `criteria.specify` with a new id through `_offer`, as api.py 5236 does.
6. Outside the points: the brief's 4-word metric misses the paraphrase that killed night 160. Low. CONFIRMED by the count: 1 phrase hit against 7 newline losses. Fix: a night read counts a lost requirement against the item's words by hand, not by a phrase match.

## (g) The repair

- Option A, refuse and name the route. In `criteria_specify`, `rota/roles/api.py`, after line 5298: when `ctx.writes` or `criteria` holds the id on the same ticket with other words, refuse, and offer `criteria.specify` with an invented id through `_offer`. Name `msg.challenge_vision_keeper` when the seat wants to replace a landed criterion.
- Option B, version the write. In `_apply_write`, `rota/core/db.py`, keep each text in a history table, and give the Tester every version in the `tests_encode` prompt. No seat reads such a record today, and the Tester would then choose between texts that conflict.
- Option C, merge the texts. In `criteria_specify`, join the texts of one id into one criterion. The door then decides content for the seat, and law 14 keeps the door to exact facts.
- Recommended: option A. It keeps three existing designs:
  - a9cb55de's rule, "An id you invent is yours once";
  - the respecify design of fd788bd1, in which `specify` writes once and `criterion_repair` rewrites;
  - the `_offer` shape of the item-as-ticket refusal at api.py 5236.
- The red test: night 160's s111 at seq 8, and night 149's s114 at its second call. With option A the second call is refused, and the seat writes the next text under a new id. The six-criteria cap at api.py 5360 then counts each text, which is the cap's intent.
- The risk: a recorded case can expect a same-ticket re-specify of a landed id. This is PLAUSIBLE and not probed, because the brief forbids a test run. The pass must run the gate.

## (h) Probes

- `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/8e879083-89bd-4f17-a62c-8f59f02dd210/scratchpad/f310p/count.py`: the count over nights 140 to 159, read-only. Its output is `rows_ok.json` in the same folder.
- Inline `python -c` reads: night 152 s115's `tool_calls` and `turns`, the items and tests of the overwritten criteria, and the survivors on nights 148, 151 and 158.
- Git: `git log -S` on the refusal text and the predicate, `git show a9cb55de`, `git show fd788bd1:rota/core/db.py`, `git log -S` on the respecify docstring.

## (i) Usage

About 95k input tokens on the harness line, about 15k output tokens, about 110k in total. This is over the 40k cap. The parser debug on the transcripts took the extra tokens.
