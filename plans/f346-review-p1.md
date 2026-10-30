# Review p1, frame 346 at 2aa9474d

Verdict: READY. The commit has no high finding and three low findings.

## (a) Verdicts on the points

1. PASS with two low findings. The paragraph has three sentences. No test pins the text or the line count of base.md. `tests/rota/test_prompts.py` and `tests/rota/test_map.py` pass, 59 tests.
2. PASS. The case loads with `fixtures.load_case` and the fixture builds. A scripted seat that writes only `src/click/utils.py` passes. A seat that commits `criteria.json` or `notes/out.json` fails.
3. PASS. The pin `qwen3.5:9b` is the pin of the neighbour cases at lines 995 and 1140 of `l1_developer.yaml`. The night's seat was `qwen3.5:9b`.
4. One low finding on the case's `.json` word. The diff has no other change.

## (b) Findings

1. `rota/roles/prompts/developer/base.md:20`, low, CONFIRMED. The word "harness" now has two meanings for the Developer. `tests_failing.md` lines 1, 4 and 46 use "the harness" for the test runner. The probe read both files. Fix: write "rota keeps them outside the project" in place of "part of the harness around the project".
2. `rota/roles/prompts/developer/base.md:21`, low, CONFIRMED. The sentence says that load calls read the glossary and the messages. The `.tools` files offer `glossary.lookup` for the glossary, and no load call reads messages. Fix: write "`criteria.load`, `verdicts.load` and `glossary.lookup` read them".
3. `tests/rota/cases/l1_developer.yaml:121`, low, PLAUSIBLE. The check `text_in_writes` reads every written row of every table, not only `touch_strays`. A seat that logs a decision such as "I did not write criteria.json" fails the case. The Developer may write `decisions` and `ledger` rows in this case. Fix: keep the word list and add a comment that names this limit, or add a table-scoped form later.

Note, not a finding: the case has no recording yet. The worktree's `tests/rota/cassettes.db` holds 15 `key_misses` rows for the case id. The comment on the case says so.

## (c) Probes

1. `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/00ca90d0-18a5-4929-b3d3-aedcb3b99ae5/scratchpad/p346/probe.py`. The probe set `samplerepo.GIT_ENV`, loaded the case, and ran `fixtures.run_case` three times with `ScriptedBackend`. The first run wrote only `src/click/utils.py` and committed: no problems, passed. The second run also wrote `criteria.json`: a `touch_strays` row, two forbidden-text problems, failed. The third run also wrote `notes/out.json`: one forbidden-text problem on `.json`, failed.
2. `pytest tests/rota/test_prompts.py tests/rota/test_map.py -q` with `ROTA_MODEL=qwen3:8b`: 59 passed.
3. A read-only query of `tests/rota/cassettes.db` found 15 `key_misses` rows for the case id.
4. Reads: `rota/testkit/fixtures.py` lines 560 to 610 and 820 to 835, `rota/roles/api.py` lines 23060 to 23090, `rota/core/db.py` lines 127 to 136 and 569 to 573.

## (d) Usage

Input tokens: about 40k. Output tokens: about 6k. Total: about 46k.
