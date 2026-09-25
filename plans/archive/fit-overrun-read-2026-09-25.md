# Frame 56, the 603 prompts over the `_fit` budget: the read

Rota workflow. Read-only, tree at 794a28f, register `tests/rota/cassettes.db`
opened with `mode=ro`. Clock at the write: 2026-09-25 02:01.

**Result: the 603 are historical.** Every overrun is a recording from before the
caps of 2026-09-18 and 2026-09-19. No dated run since 2026-09-23 sent a prompt
over the budget. The one live path without `_fit` writes no cassette.

## 1. The budget and the columns

- `_fit_budget(num_ctx, system_chars)` returns
  `max(2000, int(num_ctx / 2 * 3.97) - system_chars)`. The unit is
  characters. The budget is half the window at 3.97 characters to the token,
  less the system prompt (observed: `rota/core/runner.py:633-646`, 794a28f).
- At 12288 the budget is 24391 characters less the system prompt. At 8192 it
  is 16261 characters less the system prompt (reasoned: the formula above).
- `run_session` computes the budget once per session, and calls
  `_fit(transcript, budget)` before every send. `user` is
  `"\n\n".join(transcript)` (observed: `rota/core/runner.py:2236-2244`).
- `_prompt_overrun` measures `system + user` against
  `min(len(system) + budget, int(num_ctx / 2 * 3.97))` before every send. An
  overrun appends `prompt over budget by N characters` to `outcome.errors`
  (observed: `rota/core/runner.py:710-745`, landed cb0649c 2026-09-20 17:40).
  The condition is at least as strict as `len(user) > budget` (reasoned: the
  first term of the `min` gives exactly that condition).
- The prompt lives in `cassettes.user`, and `cassettes.system` holds the system
  text. `CassetteBackend.complete` writes both on every miss
  (observed: `rota/llm/cassettes.py:340-373`).
- `case_runs.transcript` holds no prompt. It holds a JSON list of per-turn
  `say`, `called`, `wrote`, `sent` and one `errors` entry
  (observed: key count over 3000 rows, 2026-09-25 01:5x;
  `rota/testkit/fixtures.py:703-716`). So the overrun count runs over
  `cassettes`, and `case_runs` gives only the date and the case.
- `cassettes` has no date column. `case_runs.at` is empty on 171095 of 200426
  rows. The dated rows run from 2026-09-23 to 2026-09-25T01:56:06
  (observed: `SELECT substr(at,1,10), count(*) FROM case_runs GROUP BY 1`,
  2026-09-25).

## 2. The count on today's register

Each row is counted against `max(2000, int(num_ctx/2*3.97) - len(system))`
with its own `num_ctx` and its own `system`.

- **603 of 22310 cassettes** hold a `user` over the budget. The worst is
  67295 characters over (observed: scratchpad `q1.py`, read-only SQL over
  `cassettes`, 2026-09-25). The count matches frame 46's 603. The table grew
  from 18435 to 22310 rows, and no new row is over.
- Against 16384 the count would be 66. The 16384 count is the wrong measure,
  because no cassette was recorded at 16384 (observed: same query).

By `num_ctx` (observed: `q1.py`, 2026-09-25):

| num_ctx | over | all rows |
|---|---|---|
| 12288 | 436 | 18789 |
| 8192 | 167 | 3521 |

By model (observed: `q1.py`, 2026-09-25): llama3.1:8b 316, qwen3:4b 208,
qwen3.5:9b 36, qwen3:8b 24, qwen3.5:4b 9,
openai/gemma-4-26B-A4B-it-UD-Q8_K_XL.gguf 8, gemma3:12b 2.

By mode, read from the wake line `You were woken by:` (observed: `q2.py`,
2026-09-25): message 335, tests_failing 44, criteria 30, exhausted 26,
annotate 26, review 22, tests_missing 21, survey 21, batch_start 21,
finding_violated 20, contested 8, verdict_failed 7, unresolved 7, and 15
across six other modes. All 603 open with `You were woken by:`, so all 603
are `run_session` prompts. No row is an interview prompt.

By role. `cassettes` carries no case id, and its `prompt_hash` shares no value
with `case_runs.prompt_hash` (417 and 2600 distinct values, 0 in common). So
the join runs on `(model, num_ctx, system_hash(system))`. A system text can
serve more than one case, so the role is the role of the first linked case id
(observed: `q2.py`, 2026-09-25): DV 134, AR 98, CR 98, TE 74, VK 55, TS 29,
LI 13, RS 7, GK 5, other ids 15, no linked run 75.

By date. The cassette has no date, so the date is the latest `case_runs.at`
of a run with the same system text (observed: `q2.py`, 2026-09-25):

| latest dated run with the same system text | over |
|---|---|
| none (no `at`, or no linked run) | 576 |
| 2026-09-25 | 27 |

The 27 link to `L1-AR-annotate-a-batch` (21),
`L1-DV-give-the-new-parameters-defaults` (4) and
`L1-TE-resurvey-an-area-that-moved` (2). A shared system text does not show
that the run replayed that cassette. Step 3 shows that it did not.

The worst ten (observed: `q2.py`, 2026-09-25). `at` is empty on all ten.

| cassette key | first linked case_id | at | num_ctx | overrun |
|---|---|---|---|---|
| d490c9b9758a | L1-TE-a-new-behaviour-is-a-new-callable | '' | 12288 | 67295 |
| 5f2e73a990fd | L1-TE-a-new-behaviour-is-a-new-callable | '' | 12288 | 61599 |
| 878822914615 | L1-TE-a-new-behaviour-is-a-new-callable | '' | 12288 | 61446 |
| 41fdfce94279 | L1-TE-a-new-behaviour-is-a-new-callable | '' | 12288 | 61109 |
| d7955028bfac | L1-DV-build-a-clear-criterion | '' | 12288 | 48617 |
| dae4826bfd50 | L1-DV-build-a-clear-criterion | '' | 12288 | 48391 |
| ae081578f0e1 | L1-AR-route-an-escalation | '' | 12288 | 48181 |
| af7034c2c2a4 | L1-TE-a-new-behaviour-is-a-new-callable | '' | 12288 | 45686 |
| a244f6c2767e | (no linked run) | '' | 8192 | 42071 |
| a3d8af3298c0 | L1-VK-reconcile-the-readme | '' | 12288 | 39172 |

## 3. Historical or live

**Historical.** Four facts, each observed on 2026-09-25.

1. The caps landed on 2026-09-18 and 2026-09-19 (observed:
   `git log -S<string> -- rota/core/runner.py` and
   `git log -L633,707:rota/core/runner.py`):
   - 8ebbae1, 2026-09-18 04:43: the wake cut runs on every turn, not only
     from turn four.
   - 8b15af8, 2026-09-18 06:06: `_fit_budget` replaces
     `max(2000, (num_ctx * 4 * 2) // 3 - len(system))`. The budget fell from
     two thirds of the window at 4 characters to the token to half at 3.97.
   - 34c3e72, 2026-09-19 10:32: `_cap_exchange` bounds the latest exchange.
   - 8ca1028, 2026-09-19 11:48: the eviction reserves room for its notice. This
     is the last commit on lines 633-707.
2. **509 of the 603 fit the old two-thirds budget.** Only the fall of
   8b15af8 puts them over (observed: `q3`-style count with both formulas: 394 at
   12288 and 115 at 8192 fit the old budget). The other 94 are over the old
   budget too. That is the shape 8ebbae1 and 34c3e72 closed: an uncut wake on
   turns one to three, or an uncapped latest exchange (reasoned: the commit
   bodies name these shapes).
3. **No overrun prompt carries a cut marker.** A prompt that today's `_fit`
   cuts carries `Nothing returns a wake` or `this exchange`. None of the 603
   carries either (observed: `q3.py`, 2026-09-25: 393 carry no marker, 210
   carry only the eviction notice, which predates the caps).
4. **No run has reported an overrun.** `_prompt_overrun` runs above every
   backend, so a replay that reached an over-budget cassette would write
   `prompt over budget` into the run's `errors`. Zero of 200426 `case_runs`
   rows hold the string, and the 29331 dated rows are all after cb0649c
   (observed: `SELECT ... WHERE transcript LIKE '%prompt over budget%' OR
   problems LIKE '%prompt over budget%'` returned no row, 2026-09-25).

So the last overrun row cannot carry a date, because `cassettes` has no date
column. The upper bound on its date is 2026-09-19 11:48 for the 94 over the old
budget, and 2026-09-18 06:06 for the 509 that fit it (reasoned: facts 1 to 3).
The rows stay because `INSERT OR REPLACE` never deletes a cassette that no key
reaches any more (observed: `rota/llm/cassettes.py:367`). 434 of the 603 have
`hits > 0`, and the hits carry no date either (observed: `q2.py`).

## 4. Writers that bypass `run_session`

- **`cassettes` has one writer on the live path**: `CassetteBackend.complete`
  (observed: `rota/llm/cassettes.py:367`). `rota/tools/migrate_register.py:281`
  copies rows verbatim and builds no prompt.
- Four callers of `.complete(` exist (observed: `grep "\.complete("`, 794a28f):
  - `rota/core/runner.py:2252`, inside `run_session`, after `_fit`.
  - `rota/llm/toolcheck.py:71` and `:76`, with fixed `SYSTEM` and `USER`, on
    `prof.backend()`. That is a bare provider backend, so no cassette is
    written (observed: `rota/cli.py:605-628`). It writes two `case_runs`
    rows with a one-entry transcript and no prompt.
  - `rota/testkit/interview.py:95`. **This path skips `_fit`.** It quotes
    `outcome.user`, which is the raw wake before `_fit`
    (observed: `rota/core/runner.py:2103`), and adds the questions. It runs
    only under `ROTA_INTERVIEW` and `ROTA_L1`, on a bare `OllamaBackend`
    (observed: `tests/rota/test_l1.py:163-171`). So it writes to
    `case_interviews` and never to `cassettes` or `case_runs`. It is not a
    source of the 603. It can still send a prompt over the window
    (reasoned: an uncut wake plus the preamble has no bound).
- `case_runs` writers: `record_case_run` from the test suite after
  `run_session`, the toolcheck rows above, and `migrate_register.py:296`,
  which copies old rows. No writer stores a prompt in `case_runs`
  (observed: the insert statements, 794a28f).

## 5. Cause and repair

**Cause:** the 603 cassettes were recorded before 8b15af8, 8ebbae1 and
34c3e72 lowered and enforced the budget on 2026-09-18 and 2026-09-19, and
the register keeps every cassette with no date and no expiry
(reasoned: steps 2 to 4).

**Smallest repair:** one test that holds the line. The test reads the register
read-only and asserts that no dated `case_runs` row carries
`prompt over budget`. The runner already measures every send, so the test adds
no measurement. Price: about 30k for an implementer, one test file, no
re-record (reasoned: one query and one assertion, from the anchors of small
test passes).

Two optional steps are not part of the repair:

- A `recorded_at` column on `cassettes` would let the next read date an
  overrun directly. Price: about 60k, because the migration and the key tests
  move (reasoned).
- The interview path could pass the wake through `_fit`. The interview then
  would not see what the session saw, and its docstring says it quotes the
  prompt verbatim. That is a ruling for Roman and not a repair
  (reasoned: `rota/testkit/interview.py:73-76`).

Pruning the 603 stale cassettes edits the register and changes no behaviour.
The prune is Roman's decision (reasoned: 434 of them have been replayed at
some time, and no current key is shown to reach them).
