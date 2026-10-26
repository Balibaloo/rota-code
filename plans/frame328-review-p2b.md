# Frame 328, review 2 of pass 2b at 8f960862

2026-10-26. Read-only review of 1631ba36 and 8f960862 above 5d76fddc in `C:/Users/roman/rota_p328`. The reviewer probed an extracted copy of 8f960862 and changed no tracked file. The worktree is clean.

Verdict: accept both commits for the branch. Every numbered point holds. The review found five low findings and no high finding. Findings 1 to 4 are follow-ups on 1631ba36, and none of them blocks the merge. On the latest recording of each case, the new door changes no recorded call, so the quote door adds no STALE case to the next gate.

## (a) Verdicts

1. Floor and own quote: CONFIRMED. One gap: the same quote sent twice passes the own-quote rule (finding 1).
2. Escape form: CONFIRMED for `\n`. S144_T9 lands, and `"a\nb"` against `"a b"` is refused. The `\t` escape still meets a space (finding 2).
3. One string is one quote: CONFIRMED. No other door offers joined text. The answer-mode door offers the seat's quotes unchecked, so a bad quote set gives an offer that the follow check refuses (finding 3).
4. Note after the batch's own commit: CONFIRMED. The receipt shape matches night 166. One silent case remains (finding 5).
5. `_own_assertions`: CONFIRMED on real pytest output.
6. Run delete on a new body: CONFIRMED. Every Tester path stores a body through `tests.encode` and `session_commit`, and the delete covers it.
7. The two doors outside the brief: CONFIRMED. The diff adds only the `spans` argument and the list in the offer.
8. Register impact: 0 calls on the latest recordings. Over older live recordings, 22 calls are newly refused and 25 refused calls get a new text. None of them is under the floor, one quote for both rows, or a joined string.
9. Critic channel: no Critic call in the register meets the floor or the own-quote refusal.

## Points

### Point 1: the floor and the own-quote rule

Probe P1 sent each quote set through the real `msg.challenge_tester` door on the fixture of `test_challenge_evidence.py`:

- `["in", "a1"]` and `["invoices"]`: refused with "shorter than 12 characters".
- `["leaves its i", "invoices_for"]`, 12 characters each: lands.
- An 11-character quote on either side: refused.
- The whole criterion row `Keep a1.` (8 characters): lands. A 7-character part of the row is refused.
- The whole test row `assert f()` (10 characters): lands.
- One quote that is a span of the criterion and of the test's docstring: refused with "Each row needs a quote of its own".

The test side counts the floor on `_code_only(q)`, so a comment does not fill the floor. The real quotes of the three nights all land. Night 119 m136 has quotes of 128 and 43 characters. Night 124 m64 has 208 and 74, and S144_T9 lands in `test_desk_guards.py`. Night 126 m76 and m77 have 177 and 79. Each row has a quote of its own. The night rows are the end state of each night, so this part is an estimate.

### Point 2: the escape form

`_span_of` builds a pattern from the decoded quote. A decoded line break must meet a line break of `_lined(source)`, and a space may meet a space or a wrap. Probe P2 shows these results:

- `assert r == "a\nb is the text"` is refused against a row that holds `"a b is the text"`.
- A quote that joins two real lines of the row with `\n` lands.
- The five night 119, 124 and 126 tests of `test_desk_guards.py` pass, and S144_T9 is among them.

### Point 3: one string is one quote

The binder computes `_spans` before it joins, and `stage` hands it to `_challenge_evidence`. Probe P3 shows these results:

- A plain string with ` ... ` is one quote and is refused.
- A list of the two spans lands, and a dict of the two spans lands.
- `_quote_list(text)` with no list still splits a stored message.

The reason door's offer and the answer-mode door's offer now carry the list. `test_row_route.py` and `test_challenge_evidence.py` pass with the conftest follow check active. No other door offers joined text. `api.py` 12705 and 19682 offer a list of whole rows. `decision_challenge_call` offers no quotes, and the other hints name no quotes. Finding 3 names one gap in the answer-mode offer.

### Point 4: the note after the batch's own commit

In `clickI_night166.db`, `receipts` holds `('s195', 'batches', 'bg_3', 6)`, and `sessions` gives s195 the role `developer`. The fixture of `test_frame328_encode_note.py` holds the same row. `code_commit` (`api.py` 19859) is the only pipeline writer of `head_commit`. `batches_group` writes `item_id` and `status`, and night 166 shows only Architect receipts from it. So a Developer receipt on a `batches` row is a commit. The two pass tests pass: a base head with an Architect receipt gives no note, and three tests with two red give the note.

### Point 5: `_own_assertions`

Probe P5 ran real bodies through `harness._run_one` and parsed the output:

- Red, green, red: the note names `test_r1` with line 3 and `test_r2` with line 10, each with its own `E` line. The green test is not named.
- The headers removed: one entry, `test_r2` and line 10, named from the last `FAILED` line.
- A class test gives `TestX.test_a`. A parametrized test gives `test_v[2]`.
- One red in project code and one own red: only the own red is named.
- Twelve reds cut by `_tail`: the three reds left in the tail are named.

### Point 6: the run delete

`session_commit` (`db.py` 1196 to 1219) calls `_lift_quarantines` on each changed artefact write. That function deletes all runs of the test when the write carries `body` (`db.py` 636 to 637). The only pipeline writer of `tests.body` is `tests_encode` (`api.py` 10521). That writer covers a new id and a re-encode of a stored id. `tests_retire` writes only `retired_by`. An encode with an unchanged body changes nothing, so its runs stay, and the runs then describe the body that stands. Outside: `harness.inherit` writes the bodies of the project's own tests raw, with no delete. The challenge door refuses a test with no criterion, so this does not reach the green door.

### Point 7: the two doors outside the brief

The diff of `_stage_reason` and `_answer_mode_challenge_refusal` adds the `spans` parameter and `spans if spans else ...` in the offered `quotes`. The refusal text, the refs, the reason slot and the door order are unchanged. The binder always passes `spans`, so the fallback to joined text is dead on the live path.

### Point 8: register impact

Probe P8 parsed every `msg.challenge_tester` call in the live transcripts of `case_runs`. It took the rows from the prompt of the cassette that holds the call. Then it ran the pass 2 door and the new door on the same rows. The count is an estimate, because the rows come from the prompt text.

- Latest live recording of each case: 216 calls with known rows. 134 land on both doors, and 82 get the same refusal. No call is newly refused, and no refusal text changes.
- All live recordings: 1085 calls. 620 land on both, and 314 get the same refusal. 104 have no matching cassette or no rows in the prompt.
- Under the floor, one quote for both rows, a joined string: 0 calls each.
- Newly refused: 22 calls in older groups. L1-DV-say-why-the-test-cannot-pass has 17 calls and L1-DV-a-wordless-answer-leaves-a-wrong-test-alone has 5. Each call is a test quote whose lines after a `#` comment are not in the row: a pytest `>` line, or a garbled argument. Pass 2 normalised the joined text to one line before `_code_only`, so the comment cut removed the rest of the quote. The list as sent keeps the lines, so the new door checks them. This follows the ruling, and the pass report does not name it.
- New refusal text: 25 refused calls in 7 cases of older groups (finding 4).

The stale estimate for the next gate from the quote door is 0 new cases. L1-DV-say-why-the-test-cannot-pass and ACT-CR-quote-the-tests-code carry a risk only if a replay reaches an older prompt group. No cassette prompt holds the new note text or the new refusal texts.

### Point 9: the Critic channel

No Critic call meets the floor or the own-quote refusal. The Critic cases are ACT-CR-quote-the-tests-code, L1-CR-a-test-that-encodes-nothing-is-a-challenge and L1-CR-fail-names-its-criterion. Their calls give 146 that land on both doors and 66 that get the same kind of refusal on both. Two older calls of ACT-CR-quote-the-tests-code get the new text of finding 4.

## (b) Findings

1. `rota/core/sandbox.py` 1564. Low. CONFIRMED. The own-quote rule compares the positions of the quotes, not their texts. Probe P1 sent a quote that is a span of the criterion and of the test's docstring. `[q]` is refused. `[q, q]` and `{"criterion": q, "test": q}` land. Two different quotes that both stand only in the docstring also land, because a docstring counts as test code by design. Fix: require a criterion quote and a test quote with different normalised text.
2. `rota/core/sandbox.py` 1269. Low. CONFIRMED. The escape form still decodes `\t` to a tab, and `_lined` turns the tab into a space. So `assert r == "a\tb is the text"` lands against `assert r == "a b is the text"`. These are two different code lines, as in review 1's finding 4. Fix: drop the `\t` decode, or make a decoded tab meet only a tab of the row.
3. `rota/core/sandbox.py` 1084, called at 3590. Low. CONFIRMED. The answer-mode door runs before the evidence door and offers the seat's quotes unchecked. One elided string now gives an offer that the evidence door refuses, and the follow check of `conftest.py` fails. Pass 2 split that string, so its offer passed. Probe P3b shows the same failure for a paraphrase and for a pair of short quotes. By reading, the paraphrase gap is older than the pass. Fix: offer the call only when `_challenge_admitted` accepts the sent quotes, else name the quote refusal first.
4. `rota/core/sandbox.py` 1306. Low. The mechanism is CONFIRMED and the impact is PLAUSIBLE. The refusal now shows the quote as sent, with its line breaks and space runs. Pass 2 showed the normalised quote. In older live recordings, 25 refused calls in 7 cases get a new text. The latest recordings hold none. Fix: normalise the whitespace of `shown` in `_quote_refusal`.
5. `rota/roles/api.py` 17025. Low. PLAUSIBLE. Sometimes a Developer session commits in git and dies before `session_commit`. Then the session has no receipt, and a boot moves `head_commit` to its commit (`boot.py` 163). The note then stays silent on a head that holds the Developer's code. The note only advises, so the cost is one missed note. Fix: name the case in the docstring of `_developer_committed`, and change no code now.

## (c) Probes

The probe scripts are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/192bbbc0-82bf-4501-9027-b2a27953d7ec/scratchpad/r328b/probes/`. The extracted tree of 8f960862 was `r328b/tree`. The tree was removed at the end, and the two probe test files inside it were removed with it. Every database was opened with `mode=ro`.

- `test_zz_probe_r328b.py` (in the tree): P1, P2 and P3 through the real `msg.challenge_tester` door. The output is in `probes/probe_out.txt`.
- `test_zz_probe_r328b_route.py` (in the tree): P3b, the answer-mode offer with a list, one elided string, a paraphrase and short quotes, each followed with `dry_run`.
- `p1_nights.py`: the challenge messages of nights 119, 124 and 126 against their rows under the new `_span_of`.
- `p4_receipts.py`: the `receipts`, `sessions` and `batches` rows of `clickI_night166.db`.
- `p5_assertions.py`: five bodies through `harness._run_one`, then `_own_assertions`.
- `p8_register.py`, `p8_more.py`, `p8_text.py`, `p8_latest.py`, `p8_runs.py`, `p8_debug.py` and `p8_debug2.py`: the register count of points 8 and 9, from `D:/repos/rota/tests/rota/cassettes.db`.
- Eight test files in the tree: `test_desk_guards.py`, `test_end_form.py`, `test_challenge_evidence.py`, the three `test_frame328_*.py`, `test_night46_context.py` and `test_revert_door.py`. Result: 490 passed.
- Ten test files of offers and doors in the tree: `test_row_route.py`, `test_offers_followed.py`, `test_t0_sandbox.py` and seven more. Result: 358 passed, 7 xfailed.

## (d) Usage

- Input tokens: about 175,000 (estimate, the harness gives no split).
- Output tokens: about 22,000 (estimate).
- Total: about 197,000.
