# Two pairs of statements, reconciled, 2026-11-10

A read for frame 364 by session 1efd37b1. The scripts are in the scratch folder `C:\Users\roman\AppData\Local\Temp\claude\6d9eb18c9e6274ab\1efd37b1-058e-4b19-8ab1-e1a6c654a389\scratchpad\reconcile\`. Every database was opened with `mode=ro`.

## Result

1. Pair 1: both statements are true, and they cover different sets. Night 62 ran on 2026-09-14, and no database of night 62 exists. The model read covers only the databases that exist (observed: below).
2. Pair 2: both statements are true, and they agree. The mass 5 count comes from `turns`, not from `tool_calls`. Its method gives 4,209 and 1,418 on its copies, and 4,259 and 1,450 on the original files, because the copy of dry6 lost its WAL (observed: below).

## Pair 1: a stronger model at the Developer's desk

- No file for night 62 is in `D:/repos/rota/.rota/`, `C:/Users/roman/rota_night/` or `C:/Users/roman/rota_night/state/` (observed: `p1.py`).
- The night files are `clickI_night82.db` to `clickI_night175.db`, 92 numbers. Night 129 has only `_partial`, and night 134 has no file. Copies such as `night109_cut` are extra (observed: `p1.py`, directory list).
- Every database with a `sessions` table in those folders has `qwen3.5:9b` (or `openai/qwen3.5:9b` in `tipsAS`) at the Developer's desk. No row names gemma there (observed: `p1.py`).
- `clickI_n70_merged.db` holds an `s139`, but night 70 numbers its own sessions. Its Developer model is `qwen3.5:9b` (observed: `p1.py`).
- `rota/COMPLETION.md`:211-214 says: "with the file list of finding 66 in `tests.load`, the 9B does act 3 in isolation 5/5, and gemma-4 at the Developer's desk (night 62) failed the same way the 9B did without it." (observed).
- The design page quotes the clause and drops "without it". The COMPLETION line compares gemma-4 to the 9B before the door of finding 66 (reasoned).
- The record behind the line is `plans/archive/stack-2026-09-16.md`:482-492. It reads: "two Developer sessions on gemma-4. s139 implemented confirm() right at turn 9 ... no commit (finding 68 ...). s140 ... no commit. Both without the door" (observed).
- The same record says: "the wake, not the model, was the limit in both sessions." The night was killed at 18:13 (observed: line 488-490).
- Night 62's first start, 17:24, ran the Developer on `qwen3.5:9b` from a stale warm snapshot. It was killed and relaunched cold at 17:26 (observed: commit `1057e177`, the removed stack lines, and commit `0ee2085f`).
- The gemma-4 model is `openai/gemma-4-26B-A4B-it-UD-Q8_K_XL.gguf` in `rota/llm/profiles/local-gemma-dev.toml`:30 (observed). One walk row has profile `local-gemma-dev`, merged 0, 28 steps (observed: `tests/rota/walks.jsonl`:126).
- The model read names night 62 as outside its population and says no database for it is in `.rota/` (observed: `product-model-read-2026-11-10.md`:135). So statement b does not claim night 62.
- So the evidence for statement a is prose only: two Developer sessions, one night, no `sessions.model` row. Statement a is correct about the record, but the record is thin (reasoned).

## Pair 2: the count of refused calls

- `tool_calls` has four columns: `session_id`, `fn`, `args_summary`, `seq` (observed: `rota/core/schema.sql`:1198-1204, and `pragma table_info` in all 11 files).
- `_bind` appends `(label, args_summary)` to `_CALL_LOG` before the call runs (observed: `rota/core/sandbox.py`:5356-5358). `db.py`:2067-2072 inserts those pairs and nothing else (observed).
- No column of `tool_calls` records a result or an error (observed). Statement b is correct.
- The mass 5 read says the same, at its line 103 (observed). It uses `tool_calls` only for the call count, 30,209 (observed: its table, line 139).
- Its refusal pool is the "SESSION ENDED. The runner's account:" turn in `turns` for committed sessions, else the `ERROR` lines in the next prompt (observed: `scratchpad/mass5/pool.py`, `extract.py`).
- "Never shown" means an account item that matches no `ERROR` line in a later prompt of the session, field `turn` null (observed: `pool.py`:41-50).
- The pool uses 10 files. The shared file `dry6b/runs/dry6b.db` gives dry6b for session `seq` 137 or lower, else dry6c. `dry6b_after_turn4/dry6b.db` is not used (observed: `extract.py`:5).
- The mass 5 code on its own copies in `scratchpad/mass5/db/` gives 4,209 and 1,418 (observed: `p2c.py`).
- The same code on the original paths of `product-seat-population-2026-11-10.md` gives 4,259 and 1,450 (observed: `p2.py`).
- The whole difference is dry6: 137 against 87 refusals, 52 against 20 never shown. The other 9 files give the same counts (observed: `p2b.py`).
- The original dry6 has a `dry6.db-wal` of 1,804,592 bytes, written 2026-11-06 03:19. The copy has a WAL of 0 bytes (observed).
- The original dry6 holds 89 sessions and 1,015 `tool_calls` rows. The copy holds 77 and 920 (observed). The copy missed the last 12 sessions of dry6 (reasoned).
- Every one of the 4,209 rows of `pool.json` is in the repeat (observed: `p2.py`, key of file, session, place and text).

## What I could not see

- The database of night 62. Its two sessions are known only from the stack text and finding 68 of `plans/wake-audit.md`:154-163.
- Whether night 62's relaunch really ran gemma-4 at the Developer's desk. The routing check came later, in commit `46f24656` (reasoned).
- Which dry6 sessions the WAL holds, by name. I counted them only.
- I did not read `plans/stack.md`, any meta page, or the night 62 transcript. I ran no model, night or gate, and changed no file but this page.
