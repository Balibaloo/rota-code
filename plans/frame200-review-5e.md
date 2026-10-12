# Frame 200, review 5e of passes 5c, 5d and 5e at 129cd9eb

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_rv200p5e` at 129cd9eb. Date: 2026-10-12. Rota workflow, except where a line says meta workflow.

Verdict: the three passes stand with no high finding. Review 5b's finding 1 and finding 2 are fixed. Two low findings are on the points, and one low finding is outside the points.

## (a) Verdict on each point

1. The diff: PASS. The code and test hunks touch only the six files the brief names. `plans/stack.md` also moves, from the two docs commits 2f395ac6 and c6643cfd, meta workflow. The diff holds 0 CR bytes.
2. The verdict door: PASS. The pattern admits the review's four facts. It matches "the test passes", "it passes now" and "the criterion is met". The full door refuses these three by the word count first, and refuses each padded to six words or more by the verdict door.
3. The reason paragraph: PASS with finding 1. Both briefs hold the three facts in one sentence with the example. The paragraph says "The callable is a fact from a signature, not a fix". The paragraph has four sentences, not fewer than four.
4. The slot text: PASS. `REASON_SLOT` is the one source. The TOOL line, `sandbox.py:1036`, `:1942`, `:1973`, `:3810`, `api.py:8118` and `api.py:13410` read it. The slot door at `sandbox.py:1900` derives from it, and test 18 refuses the briefs' copy. The composed system of developer/tests_failing holds the slot 2 times and the old slot 0 times.
5. The Tester sentence: PASS. `runner.py:2229-2232` resolves a ref to a decisions row as `{id, author, text, "table": "decisions"}`. `tester/challenge.md:8` names the same key and value.
6. The read call: PASS with finding 2. The mode developer/tests_failing offers `code.probe` (`api.py:9203`) and `code.source` (`api.py:11045`). Both read the project only.

## (b) Findings

1. `rota/roles/prompts/developer/tests_failing.md:35-42` and `developer/answer.md:26-33`. LOW. CONFIRMED by reading. The reason paragraph now has four sentences: the three facts, the read instruction, the example and the not-a-fix line. The brief asked for fewer than four. Fix: join the read instruction into the first sentence, or accept four and correct the brief's limit.
2. `rota/roles/api.py:9226` and `rota/roles/api.py:11070`. LOW. PLAUSIBLE. `code.probe` searches `code_index`, and the indexer keeps dependencies out (`indexer.py:276-278`). `code.source` resolves the path inside the worktree only. So a seat can read the signature of a project callable only. The measured case is the click project, so `version_option` and `CliRunner.invoke` are project code and the read works. On a project whose callable is in an installed library, the brief asks for a read that no call in the mode can do. Fix: say "a project callable" in the paragraph, or wait for a night that shows the case.
3. OUTSIDE. `rota/core/sandbox.py:1867-1869`. LOW. CONFIRMED by the probe on the new pattern and by reading the old one. The lookahead now admits verdicts that the old pattern refused: "the test passes for me on the current code", "the test passes with the current code", "it passes in CI already", "the test passes cleanly against the code". The old pattern refused each, because "passes" was in the first four words. Plural "the tests pass" is admitted on both sides. Fix: add `for`, `with`, `in`, `cleanly`, `fine` and `green` to the lookahead, and add the four to test 19 as refused.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d609cf11-e3b0-446b-b02a-29ab3633c919/scratchpad/rv200p5e/`. No probe wrote to the worktree or the checkout. `git status --short` in the worktree was empty after the runs. No model was loaded. No gate and no re-record ran.

- `door.py`: `_REASON_VERDICT.search` and `_reason_problem` on 15 reasons, on an in-memory `init_db`. The review's four facts: admitted. The three verdicts: pattern match, refused by the word count. Three padded verdicts: refused by the verdict door. Five verdicts with "for", "with", "in", "cleanly" and plural "pass": admitted (finding 3).
- `sys_tf.py`: `sandbox.build("developer", ...)` with the mode's tools and order, then `runner.compose_system` with `prompts.compose("developer", "tests_failing")`. The slot occurs 2 times, the old slot 0 times. The TOOL line is `msg.challenge_tester(refs, quotes, reason="<the error, the line, and the call that takes the argument>", round_no=0)`.
- `python -m rota.tools.map mode developer/tests_failing` from the worktree: 13 tools, `code.probe` and `code.source` among them. The bare name `tests_failing` gives "no mode named tests_failing".
- `git diff --stat 445d3519~1 129cd9eb` and a CR count on the full diff: 7 files, 0 CR bytes.
- The touched tests with `ROTA_MODEL=qwen3:8b`: `test_challenge_evidence.py` and `test_prompts.py` gave 55 passed.

## (d) Usage

About 30k input tokens of context and about 6k output tokens, about 36k in all. These are the reviewer's own estimates. Read the harness line for the real count.
