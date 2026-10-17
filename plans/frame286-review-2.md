# Frame 286, review 2 of 73c40121: the three lows of review 1

Rota workflow. Read-only review on the worktree `C:/Users/roman/rota_r283old` at 73c40121, 2026-10-18. The commit stands. No high finding. One new low, on the Developer prompt.

## (a) Verdict per point

1. CONFIRMED. `./src/click/utils.py::echo`, `/src/click/utils.py::echo` and `././src/click/utils.py::echo` each return `mistakes == ["src/click/utils.py::echo"]` with no `ignored` key. `./src/click/core.py::Click` still maps to the open bare row `src/click/core.py`. `./src/other.py::x` still refuses with the unchanged text. The `::` branch returns one element only, and `dict.fromkeys` removes repeats. With both rows open, three names give `["src/click/utils.py::echo", "src/click/utils.py"]`, each once. With both rows open and only the symbol named, the bare row stays unjudged and the call refuses, as at b0dbd926.
2. CONFIRMED. `_batch_worktree` raises `ValueError` ("batch b1 has no worktree...") for a NULL worktree. It raises the same `ValueError` for a missing batch row, because `row` is None and the one check covers both. The inner `except ValueError` catches both, and the root fallback runs: each case returns `[]` where review 1 saw `['echo']`. `_base_text` catches its own `ValueError` from `relative_to`, and `worktrees.base` catches its own errors, so the inner except catches no other git failure. A worktree path that no longer exists on disk gives `None` from `_base_text`, and the root fallback runs. A `ctx` without `batch_id` calls `_batch_worktree` zero times and reads the root file.
3. CONFIRMED with one low (finding 1). The Architect sentence is "Judge it with `batches.judge_touch`, as you judge a path.", nine words and one instruction. The Developer sentences have 13 words and 4 words, one instruction each, and the second names `code.commit`. `git diff b0dbd926 73c40121 -- rota/roles/prompts` shows these two hunks and nothing else.
4. CONFIRMED. On a `git archive b0dbd926` copy with the HEAD test file, both new tests fail: the first on the old refusal ValueError, the second on `['echo'] == []`. At 73c40121, `test_night46_context.py` passes 54 of 54. The file has 47 tests at b0dbd926 and 49 at 73c40121. The test diff has no removed line.
5. CONFIRMED. The diff adds no `raise`. The new `except ValueError` turns an error into the root fallback, and so it refuses less. Outside the plans files, the diff touches `api.py` (two hunks, one per low), the two prompt files, and the one test file.

## (b) Findings

1. `rota/roles/prompts/developer/touch_mistaken.md:10-11`, low, PLAUSIBLE. The new text drops "keep the rest of the file". `code.write` with no span replaces the whole file (`api.py:14017`, `start=0, end=-1`). A Developer that reads "write only its base source back" can send the definition alone as the whole file, and the write then deletes the rest of the file. No case renders this mode with a definition grain, so the suite cannot show it. Fix: "Write the base source of that definition back over its span with `code.write`. Keep the rest of the file. Then run `code.commit`."
2. Outside, `tests/rota/test_night46_context.py:609-621`, low, CONFIRMED by a probe. The new test checks the return value only. `arch.call` leaves the `touch_strays` row `open` in the database, because the writes go to `ctx.writes` and are applied later. No test in the file proves that a `./`-prefixed symbol judgement stamps the row `mistake` through the write pipeline. Fix: in the test, assert the `ctx.writes` entry for `touch_strays` carries the folded path `src/click/utils.py::echo`.

## (c) Probes

All probe files are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/bf5baa63-e3e0-4611-8e8d-2e8c20403b25/scratchpad/f286/r2/`.

- `test_probe_r2.py` with `conftest.py` (re-exports `tests.rota.conftest`), run from the worktree root with `PYTHONPATH` set to the worktree and `--rootdir` set to the probe folder: 11 passed. The cases: three prefixes (point 1), a symbol on a bare-path row, a grain with no match, both rows open with three names, both rows open with the symbol alone, a missing batch row, a NULL worktree, a worktree path not on disk, and a `ctx` with no `batch_id` and a counter on `_batch_worktree`.
- `parent/`: `git archive b0dbd926` with HEAD's `tests/rota/test_night46_context.py`, run `-k "leading_dot_slash or no_worktree_reads_the_root"`: 2 failed, for the reasons in point 4.
- Worktree: `ROTA_MODEL=qwen3:8b pytest tests/rota/test_night46_context.py -q -p no:cacheprovider`: 54 passed in 17.8 s.
- `git diff b0dbd926 73c40121 --stat` and `-- rota/roles/prompts`, `git show <rev>:tests/rota/test_night46_context.py | grep -c "^def test_"`.
- The worktree still holds the untracked `tests/rota/test_r4_new.py`. This review did not read or run it.

## (d) Usage

About 45k input tokens and 7k output tokens, about 52k in all, from this agent's estimate. The harness line is the record. No sub-agent.
