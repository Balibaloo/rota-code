# Frame 226, pass 1c: the review of 84a06216

Reviewer: a read-only agent on Opus, worktree `C:/Users/roman/rota_rv226c` at 84a06216, 2026-10-13. Meta workflow.
Verdict: accept with one high finding. The surface repair lands. The new check route also catches contests of the words.
Counts: 1 high, 2 low.

## (a) Verdicts on the points

1. CONFIRMED. The surface vet runs before both text checks. s292's call and s272's call land `surface_changed` with an amending write (observed: probe P1, P1b).
2. CONFIRMED live, low. `criteria.specify` vets with `required=False`, so a row with `[]` is possible. Night 145 and nights 140 to 144 hold 0 such rows (observed: probe P2, row counts).
3. CONFIRMED. `back` still fires on a surface change that brings `--show` back. A token that his words contain is admitted (observed: probe P3, P3b).
4. CONFIRMED clean. Only `terminologist/criterion_repair.tools` holds `criteria.respecify`, and it holds `msg.answer_tester`. The runner sends a criterion relay to `criterion_repair` (observed: tools files, `runner.py:277-282`).
5. Finding 1, high. 9 of the 14 contested rulings of night 145 match `_CHECK_FAULT`. 5 match only on the verb "check", and some fault a line's words. The phrase "the flag belongs to the decorator, not the command line" alone does not match.
6. CONFIRMED. The commit's test file on the parent 1ff3ab87: 4 failed, 11 passed, the 4 new tests. At the commit: 15 passed (observed: probe P6).
7. CONFIRMED. Worktree gate: 30 failed, 3836 passed, 35 skipped, 17 xfailed, 556 s. 8 new reds: the 7 known ones and 1 flaky. 1 red gone. No re-record.

## (b) Findings

1. `rota/roles/api.py:4789` and `:4886`. High. PLAUSIBLE as a seat effect, CONFIRMED at the door (observed: probe P5, P5b).
   `_CHECK_FAULT` matches the verb "check" ("then check the printed output") as well as the noun. It searches the whole answer, and not the line of this criterion.
   On night 145, 9 of 14 contested rulings match. r_00a80e9257, r_f38b69e7c3, r_c8757431e3 and r_58c63355f6 match only on the verb.
   r_c8757431e3 and r_58c63355f6 also say "Line 2 should say a fixed program version like 1.0, not a fixed Python version". That is a fault of a criterion's words.
   r_b0241f8ce0 faults line 4's behaviour and also names "its check".
   For such a ruling, a same-text call now gets "The criterion stands. Send his words to the Tester". Before, it got "Write what he asked for".
   The new text tells the relay to stop the repair of a contested sentence. That reverses frame 227 for mixed answers (reasoned: probe P5b shows the text on r_c8757431e3's words).
   Fix: match the noun only, `line N's check` or `their checks`, and when the words also fault a line's words, keep "Write what he asked for" and add the check route.
2. `rota/roles/api.py:4849-4851`. Low. CONFIRMED (observed: probe P2, `api.py:4764`).
   A row with `surface_refs = '[]'` and the same text answers `unchanged`, and the named surface drops. `criteria.specify` can write `[]`. Six night databases hold 0 such rows.
   Fix: keep the deviation. Record it in the frame as a known branch, and treat a first surface on an empty row as a change only if a night shows one.
3. `rota/roles/api.py:4841-4844`. Low. CONFIRMED (observed: probe P1c).
   A same-text call with a bad surface now gets the surface refusal. Before the commit it got `unchanged`. A same-text call on a greenfield index with `surface_refs=[]` on a row with a surface counts as a change and clears the surface (reasoned: `_vet_surface` returns `[]` when the index holds no symbols).
   Fix: set `surface_changed` only when the vetted surface is not empty.

Gate detail, point 7. The new reds against baseline 5d68808: `test_invoke_door::test_a_session_with_no_batch_reads_the_root` and `test_scene_two_batches::...as an encode` (the 2 HEAD reds), `L1-AR-route-an-escalation` and `L1-AR-a-test-that-misses-its-criterion-gets-a-decision-row` (the Architect cases), `L1-DV-apply-the-answer-and-carry-on` (frame 224), `L2-DV-name-the-block-rather-than-retry` and `L2-DV-name-the-deferred-batch-not-the-running-one` (frame 204). The flaky one is `test_scene_challenged_again::test_a_second_build_gives_equal_rows_and_lands_a_right_call_per_op`, which passed on the rerun. Red gone: `L1-VK-a-statement-on-an-existing-account-is-a-behaviour`. The gate's last stdout line: "exit 1: 8 new reds, 1 of them flaky". The log holds 0 re-record lines.
Caution: the reviewer piped the gate through tail, so the summary, stale and time lines were cut from stdout. The counts above come from the pytest line in `.rota-gate.log` and a diff against `.rota-gate.json`'s `failed` list. The stale line is not quoted.

## (c) Probes

- Scratchpad `rv1c/q2.py`, `rv1c/q3.py`: read the 14 contested rulings of a copy of `clickI_night145.db` through `_CHECK_FAULT`, and print each match span.
- Scratchpad `rv1c/test_probe_1c.py`, run with `--rootdir` at the worktree: P1 (s292 shape, surface and text writes compared), P1b (s272 under the m170 contest), P1c (bad surface, same text), P2 (row with `[]`), P3 and P3b (`back` on a surface change, a token in his words), P5 and P5b (phrases, r_c8757431e3's words at the door). 8 passed.
- Row counts of `criteria` with an empty surface in `clickI_night140.db` to `clickI_night145.db`, read-only.
- P6: the commit's `test_criterion_contest.py` run in a second worktree `C:/Users/roman/rota_rv226p` at 1ff3ab87, then the file at the commit.
- Gate: `python -m rota.tools.gate` in the worktree, with the checkout's `.rota-gate.json`, `tests/rota/cassettes.db` and its WAL copied in.

## (d) Usage

About 52k tokens in total by the harness budget: about 43k input and about 9k output. No sub-agents.
