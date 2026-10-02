# Night 108, the read

Night 108 ran from a worktree at 4eb5a9a, launched 2026-10-02 18:34 cold, ended with `GAUNTLET-DONE 22:24` and `launcher done 22:24 exit 0`. It walks frame 111 (built at d366702) and frame 110's label fix at 4eb5a9a. NIGHTCOUNT clickI: 365 sessions, 1710 turns; made up 94 turns in 54 sessions, developer 21; ran anyway 0 writes after an invention, 4 with a landed commit (452b87ff, 2530b895, 036a6a53); dangling pointers 93 turns, 23 sessions; repeats 12 wakes, 47 sessions. Read on Opus from `.rota/night108_report.txt` (250 lines), `.rota/night108.log` (190 lines) and 17 read-only queries on `.rota/clickI_night108.db`, written 2026-10-02 22:29. Every statement is about the rota workflow and is (observed: query, 2026-10-02) unless it carries another mark.

## 1. Frame 111, the repeat doors and the push

The "on exactly these refs already" refusal fired 23 times in 9 Developer sessions. Three sessions got the same refusal three times: `s307` (m173 x3), `s314` (m179 x3), `s318` (m179 x3). Per session: `s236` 2 (m120, m129), `s291` 2, `s296` 2, `s299` 2, `s307` 7, `s314` 3, `s316` 1, `s318` 3, `s324` 1.

- The door fires only on an answered challenge. The Tester answered none of m190, m193 to m200, so nine challenges on the same sorted refs `[cr_1_version_option_show_python_flag, tst_cr1_version_option_flag_exists_fixed]` landed, one per session from `s307` to `s328`.
- The key `challenges and escalations on these tests` is first in `tests.load` in all 24 Developer wakes that had a landed challenge on a red test: `s143` to `s154` (bg_1), `s231`, `s233`, `s236`, `s238` (bg_2), `s288` to `s328` (bg_3).
- bg_1 keys list m64 to m69, all "not answered yet" except m69, which carries the Tester's answer text. The next call was a new challenge in every wake. `s154` then escalated, m72.
- bg_2 keys list m125 "answered with no words" and m126, m128 "not answered yet". `s231` challenged (m128), `s233` tried `code.write` and challenged (m129), `s236` was refused twice, `s238` challenged (m132).
- bg_3 keys from `s313` on list m175 (escalate) and m177 (the Architect's own challenge to the Vision Keeper), both "not answered yet", then m190 and each later challenge, "not answered yet". The next call was a challenge in `s314`, `s316`, `s318`, `s320`, `s324`, `s326`, `s328`. `s313` and `s322` spent their turns on `code.source` and `code.write`.
- `s307` saw m181 "answered with no words" and escalated again, m189. `s299` escalated (m181) after two exact-refs refusals.
- No seat met "the answer points at" or "with no row beyond your own refs": 0 turns. No Developer escalated twice on one set of refs. The only escalate refusal is "you have already sent escalate to architect", 7 lines.
- The stdin door refused no `code.write`. `tests.encode` accepted five bodies that assign `sys.stdin = ClosedStdin()` (`s225`, `s252`, tests `tst_cr2` to `tst_cr5`, `tst_cr1_confirm_...`). One encode refusal: "this test closes sys.stdin" in `s252`. No refusal names "sys.stdin assignment shielding" or "monkeypatch shielding".

## 2. Frame 110, the label

Twelve Tester challenge wakes carried "[last run of ...: failed before any assertion]": `s142`, `s144`, `s146`, `s152`, `s155`, `s158`, `s214`, `s229`, `s234`, `s315`, `s317`, `s325`. Seven were spot-read (`s142`, `s152`, `s214`, `s229`, `s234`, `s315`, `s325`). In each, the last section ends in a library frame with no body assert line before the `E ` line: `testing.py:387 AttributeError`, `termui._readline_prompt`, `decorators.py:219 TypeError`. The label is right in all seven. Five were not read.

- `code.source` by a Tester on a challenged failed test: `s150` (two test files, m68, label "failed") and `s152` (`utils.py` 0-400 and 688-705, m69, label "before any assertion").
- `s152` and `s155` encoded a new test `inh_echo_json_02_fixed`, which passes at 4ab8db26. The challenged `inh_echo_json_02` stays red.
- `tst_cr3_confirm_returns_default_no_exception` went green at 452b87ff after `tests.encode` in `s229` (labelled "before any assertion"), `s232` and `s237`.

## 3. The merge

bg_3 reached no review, no verdict and no merge. The premise "0 failing" is wrong: the head 4b914e93 has 5 not passing (report line 182). Batch row: `status = running`, head `4b914e9384c02c335f8885ff76babc0f5cd979c1`, 8 commits. The last three log lines about bg_3 are:

- `do:harness: bg_3: 39 test(s), 6 not passing` (line 166)
- `do:harness: bg_3: 39 test(s), 3 not passing` (line 169)
- `do:harness: bg_3: 39 test(s), 5 not passing` (line 170)

Red at head: `tst_cr1_version_option_flag_exists`, `tst_cr2_..._true_appends_python`, both `_fixed` copies, and `inh_dcc9ea38` (`tests/test_basic.py`). The Developer ladder ended at `s330`, `tick:exhausted` attempt 10 of 10. Commits after that came from message wakes `s340`, `s342`, `s344`, `s346`, each woken by an empty Architect answer. The last commit is `s346` seq 3, 4b914e93. The last bg_3 seat is Tester `s348`, refused on `tests.encode`. Walk 3 then went "quiet after 132 steps" with no park line for bg_3 (reasoned: the walk ended before the park tick ran).

## 4. The stalls

- bg_1: Developer `tests_failing` wakes reached attempt 9 (`s154`), then `s157` `tick:exhausted` attempt 10 of 10. It was deferred at the start of walk 2: `do:park: deferred bg_1; its ladder is spent` (log line 76). `s157` sent challenge m73 and was refused seven more times.
- bg_2: attempt 9 (`s238`), then `s240` attempt 10 of 10. Deferred at the start of walk 3 (log line 124). `s240` asked the Vision Keeper, m133, and was refused twice more.
- bg_3: `s330` at attempt 10 of 10 asked the Vision Keeper, m201, and was refused four times more.
- One CYCLE line: `CYCLE: period 1, rounds 3, wakes: developer|tick:tests_failing|attempt 1|["bg_2"]` (log line 80), sessions `s207`, `s208`, `s209`.
- Frame 114: inherited tests failed in two batches. bg_2: `inh_022b8a87` (`test_confirm.py`) and `inh_51d478df` (`test_termui.py`) at c568b770 and 452b87ff. bg_3: `inh_dcc9ea38` (`test_basic.py`) at five commits from 05c75b3d to 4b914e93. In bg_1 the six `inh_echo_json_*` tests carry a criterion and are the Tester's own, named with the `inh_` prefix by `s140`.
- The unnamed-definition door refused four writes: `s233` twice on `_readline_prompt`, `s332` on `custom_version_option` and `help_option`. Whether either write was a repair of the red inherited test is (reasoned: unread, the refused text was not compared with the failing test).

## 5. The Architect

Five escalations landed: m72 (`s154`), m125 (`s227`), m175 (`s291`), m181 (`s299`), m189 (`s307`). Three got an answer, and every answer has an empty `body_text`.

| Escalation | Architect | Answer | `body_refs` of the answer |
|---|---|---|---|
| m72 | `s156` | none, 15 `findings.find`, fnd_001 "k0 satisfied" | - |
| m125 | `s228` | m127 | `["cr_3", "tst_cr3_confirm_returns_default_no_exception"]` |
| m175 | `s292` | none, sent m177 challenge to the Vision Keeper | - |
| m181 | `s300` | m183, plus m182 to the Vision Keeper | `["cr_1_version_option_show_python_flag", "tst_cr1_version_option_flag_exists"]` |
| m189 | `s308` | m191 | `["cr_1_...flag", "cr_2_..._true", "cr_3_..._false"]` |

All ten `architect->developer answer` rows have an empty `body_text`. Frame 115: `model.amend` was refused with "that is what the product does, and an item already says it" in five Architect sessions, `s74` (twice), `s180`, `s228`, `s254`, `s357`. `s228` then sent m127.

## 6. Made up

Completions that hold their own `OK` or `ERROR` result line, by this read's count: vision_keeper 27 turns in 15 sessions, architect 19 in 8, developer 36 in 21, tester 9 in 7, critic 3 in 3, terminologist 1 in 1. Total 95 turns, 55 sessions. The report says 94 and 54, tester 6. Developer tools: `code.source` 31, `code.write` 12, `msg.challenge_tester` 5, `code.commit` 3, `batches.expect` 2. `s230` alone holds 8 turns. Developer sessions with made-up lines: night 106 22, night 107 9, night 108 21. Night 108 had 59 Developer sessions and 548 Developer turns.

## 7. New, held by no frame

- The repeat-refs door skips an unanswered challenge, so nine challenges on one set of refs landed while the Tester answered none (m190, m193 to m200; `s307` to `s328`).
- The push key lists the Architect's own challenges to the Vision Keeper as entries on the Developer's test (m177, m182; `s296`, `s307`).
- The Tester answers a challenge with a new `_fixed` test and leaves the challenged test red; the answer refs name the new id (m174, m178; `s146`, `s148`, `s152`, `s289`, `s293`).
- The Architect's `tick:unresolved` answers challenges that were sent to the Tester, with no words, and each wake gave a Developer commit after the ladder ended (m208 to m211; `s339` to `s346`).
- Tester `s315` to `s329` re-encoded `tst_cr1_version_option_flag_exists_fixed` five times and sent no answer.
- A batch whose ladder is spent keeps taking commits and is not parked within the walk (bg_3, `s330` then `s346`).
