# F22 pass 1 review: the table an id lives in

Commit e33bc142 on branch f22root, worktree C:/Users/roman/rota_f22, parent ae9b99c6. Read-only review. No file of the worktree changed.

Verdict: PARTIAL. The reader exists and the register derives from the schema. The register order changes the answer of three helpers on ids that real nights hold twice. The new adopt text does not give s209 a route.

## (a) Verdicts

1. PASS with a defect. `id_tables` is `NATURAL_KEYS` filtered by the schema's `id` column, less `test_run_journal`. It holds all 27 id tables, and no seat-named id table is missing. Its order is a defect (finding 1).
2. PARTIAL. `table_of` reads both prefixes in one place. `guess_item` still strips `guess:`, and the literal `"guess:"` stays at 3 sites (finding 6).
3. The lists are scope rules or column maps. Eight of the nine searches are second readers of the table. `_reply_sentence_fault` reads text only (finding 5).
4. FAIL. The text is plain but gives no route. s209 holds no batch door, so the new words would not change its next call (finding 3).
5. PARTIAL. The pin test goes red only for a one-line f-string `FROM {x} WHERE id = ?` outside a named function (finding 4).
6. None found. No case file holds a changed refusal or label. The gate's stale line must settle the cassette prompts.
7. None. `_must_exist(ctx, table, id)` keeps its signature, and the diff changes none of its 20 callers.

Point 3, by site:

- `lifecycle._batch_notes` (lifecycle.py 721): a search over `_BATCH_TABLES`. Second reader, with a scope rule.
- `loop._perform` (loop.py 488): a search that picks the table and its words column. Second reader, with a column map.
- `sandbox._quoted_rows` (sandbox.py 1106): the same form over `_QUOTABLE`. Second reader, with a column map.
- `api.cite` (api.py 1341): a search over the artefact's tables and the session's staged writes. Second reader. `table_of` cannot see `ctx.writes`, so the move is not one line.
- `api._reply_sentence_fault` (api.py 1651): reads `text` from `entries` and `statements`. It finds no table. It is a content read, not residue.
- `api.findings_find` (api.py 4236): finds which of `criteria` and `tests` holds a wrong constraint id. Second reader of the F22 fact. It duplicates `db.elsewhere` over two tables only.
- `api._is_team_note` (api.py 11174): a search over four tables. Second reader, with a scope rule.
- `api._owner_call` (api.py 13626): a search over `criteria` and `tickets`, then `_owner_of_ref`. Second reader, with an owner map.
- `api._misplaced_conflict` (api.py 13923): a search over `_ROW_WORDS`. Second reader, with a column map.

## (b) Findings

1. rota/core/db.py 237-252, with api.py 13991-13996, api.py 2644 and principal.py 982-994. Severity high. CONFIRMED.
   The register order replaces the order of each old helper. `items` is 26th of 27, and `constraints` follows `glossary_terms`.
   Night databases break law 14. `sentinel` and `unset` are both a constraint and a glossary term on nights 161, 162, 166 and 170. `echo_json` is both an item and a glossary term on night 162.
   On those ids `_table_of_ref` and `ruled_ref_home` now give `glossary_terms`. The old `LEDGER_HOMES` order gave `constraints` and `items`.
   Effect 1: `ledger.log(about_ref='sentinel', about_table='constraints')` now refuses and offers `about_table='glossary_terms'` (api.py 13787).
   Effect 2: `model.adopt(ids=['sentinel'])` now routes to `model_areas`, because `table_of` is not `constraints`. The refusal then says "'sentinel' is a row of glossary_terms".
   Fix: give `table_of` an `among=` set, so that a caller with a scope rule asks whether the ref is a row of one of its tables.

2. rota/core/db.py 234-249. Severity low. CONFIRMED.
   `_ID_TABLES_CACHE` is keyed by `id(conn)`. A new connection at a reused address reads the register of a closed connection.
   The probe gave a fresh database a 26-table register. A night 160 connection at a reused address raised `OperationalError: no such table: ruled_refs`.
   The old `api._id_tables` had the same key. F22 puts the cache on every `table_of` path: the wake render, the `_must_exist` miss and the owner split.
   Fix: key the cache on the database path and `PRAGMA schema_version`, or read the schema on each call.

3. rota/roles/api.py 2603-2605. Severity high. PLAUSIBLE.
   On night 170, s209 woke on relay m87, and the principal approved b_3. Its tools were `model.adopt`, `model.consult`, `model.load`, `msg.question_terminologist` and `msg.report_liaison`.
   The new refusal reads: "'b_3' is not a row of model_areas; 'b_3' is a row of batches; adopt what the ruling names, from the refs you were given".
   The ruling names only b_3, so "adopt what the ruling names" still points at b_3. No door of the seat acts on a batch.
   The seat would end the session or call `model.adopt` again. The night measure, a repeated id refusal goes to 0, will probably not move for s209.
   The cause is upstream: a batch verdict reached a seat with model doors only. F22 does not touch that route.
   Fix: when the holding table has no door in the seat's set, name `msg.report_liaison` as the route, and trace why a batch verdict reached the Architect's model seat.

4. tests/rota/test_f22_table_of.py 128-185. Severity low. CONFIRMED.
   The pin is one regex on one line, and it allows a site by file and function name.
   The probe matched none of these forms: a string split over two lines, `id=?` with no spaces, an alias `r.id = ?`, and a chain of literal tables.
   Literal chains already exist outside the pin: sandbox.py 4676-4688 in the relay split, api.py 4232-4237, and runner.py 213-214.
   A new search inside an allowed name such as `has`, `wrapper` or `_must_exist` also stays green.
   Fix: pin the count of lookups per allowed function, and add the literal chain form to the scan.

5. Report section "Residue" and api.py 1341, api.py 1651, api.py 4236. Severity low. CONFIRMED by reading.
   The report says each residue site is a one-line change to `table_of(conn, ref) in (...)`. That is wrong for `cite`, because `cite` also reads `ctx.writes`.
   The change also alters the answer on a clash id, by finding 1.
   `_reply_sentence_fault` finds no table, so it is not residue.
   `findings_find` names only `criteria` and `tests`. A batch id sent as a constraint still gets no table name.
   Fix: move `findings_find` to `db.elsewhere`, and drop `_reply_sentence_fault` from the residue list.

6. rota/core/sandbox.py 4682, rota/core/scheduler.py 2090, rota/roles/principal.py 2099, rota/roles/api.py 12237, rota/core/sandbox.py 916. Severity low. CONFIRMED by reading.
   Three sites still test the literal `"guess:"` and not `GUESS_REF`. `guess_item` still strips the prefix by its own rule.
   `_owner_of_ref` gives `architect` for any `guess:` ref, and checks no item. `table_of` gives None for `guess:` with a missing item.
   `ref_resolves` accepts `guess:` only for a request item, and `ruled_ref_home` accepts any item. Two rules exist for one prefix.
   Fix: use `GUESS_REF` at each site, and let `_owner_of_ref` read `table_of` before it names the Architect.

## (c) Probes

All probes are in C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b3bc8a66-bd69-4749-a050-07bdd1893c24/scratchpad/.

- `f22_p1.py`: copied night 170 with the backup API to `n170_copy.db`, and made `fresh.db` with `init_db`. It compared the register with every table that has an `id` column. Only `test_run_journal` was outside. It listed the ids that two tables hold.
- `f22_p2.py`: opened the night databases 160 to 171 read-only and listed the clash pairs. It ran `table_of`, `_table_of_ref`, `ruled_ref_home` and `_owner_of_ref` on `sentinel` and `unset`. All four gave `glossary_terms` or `terminologist`.
- `f22_p3.py` and `f22_p4.py`: showed the cache reuse. A fresh connection read a 26-table register. A night 160 connection raised `no such table: ruled_refs`.
- `python -c` on night 162: `echo_json` gives `glossary_terms` from `table_of` and from `_table_of_ref`.
- `python -c` on night 170 `turns`: read the s209 wake, its three refusals, its final turn and its tool list.
- `python -c` with the test module: ran `LOOKUP` on four sample forms. All four did not match. The live scan found no extra site and no stale `ALLOWED` entry.
- `grep` of tests/rota/cases for the old adopt words, `no <table> row with id=`, `(row)` and `"table": null`. It found no match.

## (d) Usage

About 62k input tokens and 13k output tokens, about 75k in total. These are estimates. No sub-agent ran.
