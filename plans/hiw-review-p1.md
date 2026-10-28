# Review of hiwroot, pass 1: f25b6303, 2fb92e9c, 575e09b5

Read-only review on 2026-10-28. Worktree `C:/Users/roman/rota_hiw`, parent ae9b99c6. The read is `plans/night171-how-it-works-read.md`, section 6. I edited no tracked file and ran no gate.

Verdict: READY on Part B. Part A needs one ruling before it lands, because the gate widens the contest dead end from the account to every observed description row (finding 1).

## (a) Verdicts

1. CONFIRMED. The s152 shape is refused, the onboarding shape is admitted, and the s203 shape is refused by the new gate in place of the same-words door. The contested key still quarantines at 3, because no call leaves `contested`.
2. CONFIRMED. `ctx.onboarding` has one writer, `runner.session_sandbox` at runner.py:4772, and every session path goes through it.
3. CONFIRMED with a gap. In a deliver wake the route works: `deliver.tools` holds `problem.assert`, and a new item is admitted. In every other wake the refusal quotes a brief the seat does not hold (finding 2).
4. CONFIRMED. No brief, case or test expects the removed sentence. Only the new test names it, to assert its absence.
5. CONFIRMED. The numbered lines he rules by do not move. Only the unnumbered page lines shift by one on the observed pages.
6. CONFIRMED. The Vision Keeper leaves the account and asserts the statement as its own item. No recorded case drives the gate (finding 3).
7. None stale. The 22 Vision Keeper L1 cases give the same 8 reds at the parent and at head.

## (b) Findings

1. `rota/roles/api.py:2048`. Severity high. CONFIRMED.
   The gate also closes the contest exit for an observed description row that is not the account.
   At the parent, a `tick:contested` wake amended `provides_command_line_interface` with new words, and the assert was admitted.
   At head, the same call is refused, so each such contest ends with its contested key quarantined at 3.
   The read's doubt 4 says a contested description row "still" stops. That holds for the account in the night 171 shape only.
   The read wants this effect for wall D. The cost is new stuck contests, and Roman has not seen that cost.
   Frame 264 counted 3 of 12 misreads on description rows, and the contests that follow now have no exit.
   Fix: ask Roman before landing whether `tick:contested` stays outside the gate until he rules the contest exit.

2. `rota/roles/api.py:2049` to 2054. Severity low. CONFIRMED.
   The refusal quotes "The deliver brief says" in every wake that is not onboarding.
   The contested, challenge, propose, exhausted and answer modes hold `problem.assert`, and their seats do not read the deliver brief.
   `contested.md` lines 12 to 16 tell the seat to amend "on the item's own id". The door now refuses that call on every observed description row.
   A new item does not drain the contested tick, so the refusal's route does not end that wake.
   The quote spans `deliver.md` lines 37 and 38, not line 37 alone.
   Fix: in a contested wake, tell the seat to leave the row and report to the Liaison with `msg.report_liaison`.

3. `tests/rota/cases/l1_gatekeeper.yaml:174`. Severity low. CONFIRMED.
   `L1-VK-a-statement-on-an-existing-account-is-a-behaviour` is the one case on the path of point 6.
   It seeds the account with no `is_description`, so the column is 0. An onboarding at head always stages 1.
   The case replays the same-words door and not the gate: 30 cassettes replayed, and the case passed at head.
   The case loader inserts any yaml column (fixtures.py:85), so `is_description: 1` seeds the production shape.
   Fix: add a twin case with `is_description: 1` on the account row and record it.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b3bc8a66-bd69-4749-a050-07bdd1893c24/scratchpad/hiwrev/`. The parent tree is `parent/` and `p2/`, from `git archive ae9b99c6`. Each probe ran on a copy of a database, never on the original.

- `replay.py`, on a copy of `D:/repos/rota/.rota/clickI_night171.db`, through `runner.session_sandbox` with the recorded wakes:
  - A, s152: wake m53, deliver, account set back to approved v2. Head: refused by the gate, no write. Parent: admitted, draft staged.
  - B, `tick:reorient`: `onboarding` is True. Admitted at head and at the parent.
  - C, s203: `tick:contested` on `how_it_works` with the row's own words. Head: refused by the gate. Parent: refused by the same-words door.
  - C2: the contested wake with his m80 words. Refused at both by `_assert_words_fault`, before the gate. `predicates.contested` still wakes the row after the session.
  - The night 171 database holds `vision_keeper|tick:contested|how_it_works` with attempts 3 and quarantined 1.
- `probe2.py`, on the same copy:
  - D: wake m86 delivers s3, and the account is asserted with one sentence added. Head: refused. Parent: admitted.
  - D2: the same wake asserts s3 as `format_filename_docstring_example`. Admitted at head and at the parent.
  - E: `tick:contested` on `provides_command_line_interface`, an observed description row, with new words. Head: refused. Parent: admitted.
- `pages.py` rendered the touch note, the stopped-work page and the request page with an observed account and a decided account, at head and at the parent:
  - Touch and stopped, observed: line 7 is "What the project does today. This is not your request:", and the account stays numbered 4. The next numbered line stays 5.
  - Request, observed: line 5 is the new heading, and the account stays numbered 2. The order stays `['show_python', 'how_it_works']`.
  - Request, decided: "What we are building:". Touch and stopped, decided: no heading, the same as at the parent.
  - The diff between the parent output and the head output holds only the three heading lines.
- Map and grep:
  - `rota.tools.map fn _is_description`, `fn problem_assert` and `table items`: one writer of `items.text`.
  - A grep of `onboarding=`, `Ctx(` and `sandbox.build`: the cockpit builds at inspect_api.py:248 and 269 and server.py:204 only list signatures.
  - A grep of `Amend the account` and of the page headings under `rota/` and `tests/`.
  - A grep of `how_it_works` under `tests/rota/cases`: `l1_gatekeeper.yaml` 3 times and `l1_survey.yaml` once. No `g*.yaml` case names it.
- Cassettes: a read-only scan of `tests/rota/cassettes.db` for qwen3:8b.
  - 32 cassettes hold the same-words refusal, all in the L1 case of finding 3.
  - None holds "Before I build this", "The team stopped work on this change" or "What we are building:".
- Suite: `pytest tests/rota/test_l1.py -n 0 -k VK` against a copy of the cassettes, through `ROTA_DEV_DB`.
  - Head: 8 failed, 14 passed. Parent: the same 8 failed, 14 passed.

## (d) Usage

About 95k input tokens, about 14k output tokens, about 109k in total. These counts are estimates. The cap was 70k, and the cassette replays at the parent took the overrun.
