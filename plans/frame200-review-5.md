# Frame 200, review 5 of pass 5 at 7b0a9aac

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_rv200p5` at 7b0a9aac. Date: 2026-10-12. Rota workflow, except where a line says meta workflow.

Verdict: the pass stands. No high finding. Five low findings. Three of the five are test gaps or brief lines, and none blocks the commit.

## (a) Verdict on each point

1. The reason row: PASS. A missing reason, a five-word reason, the slot text and a copy of the criterion are refused, with no write and no message. An admitted reason stages one `developer` row `d_` + sha256(text|c1|ts1)[:10], and the message refs end with that id.
2. `_without_own_reasons`: PASS. On night 142's rows, a prior with an own reason id still matches with `drop_own`, and drops out without it. The Architect's and the Vision Keeper's rows still lift the cap. The Developer's own row does not lift the cap.
3. The hint sites: PASS on the four sites. Each one writes `REASON_SLOT`, or the seat's reason when the reason door admits the reason. The slot sent back is refused. Two Developer prose lines in `api.py` still name the call with no reason (finding 3).
4. `decisions_author`: PASS. The author check refuses another author's id. The graph edge is `writes author` with `actor: system`. The Developer has no `decisions` namespace in six modes.
5. The 12 deviations: 12 right, 0 wrong. Deviation 9 is right but has no test that holds it (finding 1).
6. Red before the fix: PASS. The recipe gives 24 failed, 2 passed at 59a91766, and 26 passed at 7b0a9aac. Each of the six mutants goes red. Three other own-row skips survive their mutants (finding 1).
7. The two cases: no false green on a body that keeps the night's lines. The Tester case can pass on one wrong package name and on run output alone (finding 4).
8. The briefs: PASS. Only `developer/tests_failing.md` and `developer/answer.md` moved. Both carry the design's slot text. The diff holds 0 CR bytes. `tests_failing.md` adds one sentence that the design did not name, and the sentence is sound.

## (b) Findings

1. `rota/core/sandbox.py:2041-2042`, also `:970` and `:1150`. LOW. CONFIRMED. No test holds the sender skip in `_challenge_cap_refusal`, in `_answer_decisions` or in the `keep` list. Each mutant passes all 429 tests of five files. The cap skip is load-bearing: after three reasoned priors, a seat that copies its own old reason id into refs gets past the cap. At the fix the call is refused with the cap sentence. With the skip undone the call lands as m4. Fix: add a test for an own reason id copied into refs after the cap, and one test for each of the two other skips.
2. `rota/core/sandbox.py:3605-3608`. LOW. CONFIRMED. A seat that copies its old reason id into refs and writes a new reason sends two reason ids. The stored refs were `['c1', 'ts1', 'd_d445031812', 'd_a804061b20']`. The Tester then reads two reasons, and the old one can be stale. Fix: drop the sender's own reason ids from refs before `_stage_reason` appends the new id.
3. `rota/roles/api.py:12742` and `:12871`, with `rota/roles/prompts/developer/exhausted.md:14-15`. LOW. CONFIRMED by reading. The two Developer refusals name `msg.challenge_tester` and its arguments with no `reason=`. `exhausted.md` writes the whole call with no `reason=`. A seat that copies any of the three meets the reason refusal once. The refusal then teaches the slot, so the cost is one round. `findings_exhausted.md` names no challenge, so it needs no line. Fix: add `REASON_SLOT` to the `exhausted.md` call form and to the two refusal sentences, and re-record the touched cases.
4. `tests/rota/cases/l1_tester.yaml`, the new case's `expect` block. LOW. PLAUSIBLE. The excludes list holds `package_name="test_version_option")` only. A body with the same name in single quotes passes the check and still fails at run time. The run output also shows the hint "Try passing 'package_name' instead", so a pass does not show that the reason row moved the seat. The case comment says the case measures the seat. Without a control case, the section 5 probe alone separates the row's effect. Fix: add the single-quote form to `text_excludes`, and read the section 5 probe against a control case with no `<d1>`.
5. `rota/core/sandbox.py:1895`. LOW. CONFIRMED. The copy door refuses only a reason that is a substring of the quotes or of the criterion. A reason that holds a whole quote and four more words lands. The probe call `"the criterion keeps them assert invoices_for('a1') == [] so it fails"` landed with one row. The DV case counts any admitted row, so a padded quote counts as a reason there. Fix: refuse a reason whose words outside the quotes and the criterion number fewer than six.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/d609cf11-e3b0-446b-b02a-29ab3633c919/scratchpad/rv200p5/`. No probe wrote to the worktree or the checkout. No probe opened `tests/rota/cassettes.db`.

- `probe.py`: point 1 on fresh `init_db` copies `p1.db` and `p1b.db`. Seven refused or landed calls, one admitted call with its staged row and refs, and the own-old-id call of finding 2. Point 2 on `n142.db`, a copy of `rv215/n142.db`. The probe added a `developer` row `d_rv1` to m393's refs. `_same_refs_rows` with `drop_own` gave m393, m382, m373. Without `drop_own` it gave m382, m373. `_carries_decision` gave False with the skip and True without it. With `d_arch1` (architect) or `d_vk1` (vision_keeper) on the test, it gave True.
- `probe4.py`: `build("developer")` in the modes tests_failing, answer, exhausted, findings_exhausted, normal and challenged. Each call of `decisions.author` raised `NotInWorkingSet`.
- `head/` and `fix/`: `git archive` of 59a91766 and of 7b0a9aac. The five new test files were copied into `head/`. The 26 node ids are in `ids.txt`, which holds the 24 from `f200/red_head.txt` plus test 9 and `test_owners_can_read_what_they_own`. Result: 24 failed, 2 passed at `head/`, and 26 passed at `fix/`.
- `f200/mutate.py`, run with `fix/` as the working directory. The six mutants gave 2, 2, 1, 1, 2 and 1 failed.
- `mutate2.py` in `fix/`: five more mutants on five test files. The cap skip, the `_answer_decisions` skip and the `keep` skip passed 429 tests. The copy door mutant failed test 3. The `_fill` stand-in mutant failed one `test_row_route.py` test.
- `fix/tests/rota/test_rv_ownrid.py`: the own reason id after the cap. At the fix the call was refused with the cap sentence. With the cap skip undone, the call landed as m4. `fix/rota/core/sandbox.py` was restored from `.orig` after the run.
- `git show 7b0a9aac | grep -c` on the CR byte gave 0.

## (d) Usage

The harness usage line is not visible to this agent. The context counter gives about 108k tokens in all, about 96k input and 12k output. The review went past the 70k cap by about 38k. The cause was the mutant runs and the case reads. No sub-agent ran.
