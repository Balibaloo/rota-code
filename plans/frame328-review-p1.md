# Frame 328, review 1 of passes 1 and 2 at 5d76fddc

2026-10-26. Read-only review of 0b98954c, 9913fc88 and 5d76fddc above cce18a2e. The reviewer worked in an extracted copy of 5d76fddc and changed no tracked file.

Verdict: hold 9913fc88 for one guard, and hold 0b98954c for one condition. 5d76fddc can go to the branch as it is. The span check follows the ruling on contiguity, but it has no floor, so a quote of two letters passes on both sides. The old 12-character rule refused that quote. The encode note can fire on a base head after a boot, where a test written before the code is red by design.

## (a) Verdicts

1. Encode note: CONFIRMED on the fire conditions, with one wrong name on a body with two red tests. PLAUSIBLE high risk on a base head (finding 1).
2. Span check: CONFIRMED contiguous and verbatim after normalisation. The three forms undo the call's encoding. The escape form also lets one non-verbatim code quote through (finding 4).
3. No minimum length: CONFIRMED. A quote of `in` and `a1` lands, and one quote serves both rows. This defeats the purpose of the ruling (finding 2).
4. Other channels: CONFIRMED that three channels keep the window, not four. The Critic to Tester channel is strict now, because the branch keys on the recipient (finding 7).
5. Green-test door: CONFIRMED on every condition. One PLAUSIBLE gap: the door reads a run of an older body (finding 6).
6. Changed tests: CONFIRMED. Each change follows the ruling, and no assertion is weaker.
7. STALE set: CONFIRMED 24. No case file changed. The 6 new stale cases come from new refusal text on recorded refused calls, and a re-record absorbs them.
8. Suite: CONFIRMED no unit red from the pass. The register reds are 18 STALE, 2 below threshold and 1 follow check, and the pass owns only STALE ones.

## Point 1: the encode note

The note fires only when `_encode_run` returns `fail` and `arrange_fault` returns None. A collection error and an import error return `error`, so the door returns before the note. `_own_assertion` then needs the last traceback location to be the test's own file and to end with `AssertionError`.

Probe p1 ran nine bodies through `harness._run_one` on a scratch project:

- An assert in the test file: the note holds the name, line 5, the assert line and the `E` line.
- An assert inside project code: None.
- A syntax error and an import error: verdict `error`, so the door stops before the note.
- An assert inside a helper file: None.
- A green body: verdict `pass`, no note.
- A `KeyError` in the test and a `DID NOT RAISE`: None.
- Two red tests in one body: the note names `test_g1` and quotes line 7 and the `E` line of `test_g2` (finding 3).

The pass's own test replays s198's call of night 166 against `format_filename` at a0295dff. It passes, and it pins the stored id, `line 7`, the assert, the `E` line and the step. The green test pins "no note" with a spy on the run. The test is stored as before, because the door still returns None.

`batches.head_commit` has a writer in `rota/core/boot.py` line 163. At a boot, a running batch with a worktree takes the git head, also before any Developer commit. Then a Tester encode of a test written before the code meets the note. The note says the test is wrong if the criterion gives the value the run shows. On a base head the run shows the old behaviour (finding 1).

## Point 2: the span check against "verbatim"

Each quote must be a substring of its row after whitespace normalisation. The 12-character window is gone on the tester channel. The three forms:

- Enclosing quote marks. Night 119, s250, message m136: the criterion quote came inside double marks. The marks are the call's syntax.
- A literal backslash-n. Night 124, s144 (`S144_T9` in `test_desk_guards.py`): the test quote joined two lines with the two characters of the JSON escape. The two lines are contiguous in the row.
- A single mark for a double mark. Night 126, s172, messages m76 and m77: the criterion holds `separators=(",", ":")` and the seat wrote the same call with single marks inside its double-quoted string.

Each form undoes the encoding of the call, not the seat's words. In the register, 50 challenge messages pass the strict check only by a form, most by enclosing marks. One leak is real: the escape form also decodes a backslash-n that the row holds as code. Probe p2 shows that `assert r == "a<backslash-n>b"` matches a row that holds `assert r == "a b"`. These are two different code lines. The mark swap is global, so `don"t` matches the row word with an apostrophe. That swap changes no meaning in prose or in Python code.

## Point 3: no minimum length

Probe p2 and the sandbox probe confirm it. `_span_of` returns True for a quote of one open bracket and for a quote of one equals sign. Through the real `msg.challenge_tester` door, `quotes=["in", "a1"]` lands. `quotes=["invoices"]` lands too, because one quote counts for both rows. The old window refused both, because the rows are longer than 12 characters. The ruling makes the seat pay the reading before a challenge. A two-letter quote pays nothing, so the gap defeats the purpose.

The cheapest guard: each quote, normalised, holds at least 12 characters or the whole row. Also, a quote that counts for one row cannot be the only quote of the other row. Over the register, the floor refuses 2 quotes that the strict check accepts: `echo(obj)` in night 144, m153 and m159. A word guard (one whole word of three letters or more) refuses the same 2 quotes and adds a rule that is harder to explain. Use the floor.

## Point 4: the other channels

The graph has five challenge edges. `_challenge_evidence` keys the strict branch on the recipient `tester`, so two edges are strict now:

- Developer to Tester (the frame's target).
- Critic to Tester. The pass did not name this channel. `L1-CR-a-test-that-encodes-nothing-is-a-challenge` went STALE because of it.

Three edges keep `_quotes_span`, the 12-character window, on the same ruling. Probe p34 counted the challenge messages of the 112 night databases. The rows are the end state of each night, so a count is an estimate.

| Channel | Messages | With a quotable row | Strict check refuses |
|---|---|---|---|
| Terminologist to Vision Keeper | 206 | 206 | 182 |
| Architect to Vision Keeper | 229 | 108 | 48 |
| Critic to Developer | 3 | 1 | 1 |
| Critic to Tester (strict now) | 19 | 19 | 15 |
| Developer to Tester (strict now) | 564 | 564 | 430 |

The strict check needs a brief change on the Terminologist channel. Its text is a proposed wording of the ticket, not a quote, for example m73 of night 166. The Architect channel refs a statement row in 121 of 229 messages, and no statement column is in `_QUOTABLE`, so the door is silent there. The Critic to Developer channel has too few records to judge. The Developer to Tester count of 430 is high because test bodies change during a night. The count shows the drift of rows, not 430 refused calls. The Tester's answer (`_answer_evidence`, ruling DECISIONS 1248) and the red-line door also keep the window on the tester channel.

## Point 5: the green-test door

The sandbox probe and the pass's 6 tests confirm each condition:

- A Critic sandbox gets None.
- A Developer gets the refusal when the last run at `head_commit` passed.
- A head with no run gets None.
- The text names the test, the head and the run's last line, for example `1 passed in 0.01s`.

The door stands after the same-refs door, so `test_end_form.py` keeps the repeat refusal and its end form. That file passes. The Tester's routes do not call the door, and `_answer_evidence` is unchanged. `_challenge_admitted` now reads the door, so the revert hint names no challenge that the door refuses.

One gap: the door reads the last run at the head, whatever body it ran. The probe re-encoded the test body after a green run at the same head. The door then refused a challenge on a body that never ran (finding 6).

## Point 6: the changed tests

- `test_challenge_evidence.py`, both sides: the prose form is now refused, and a list of two spans lands. DECISIONS 1279 to 1283 describe the sibling in prose, not as a call form. The test keeps its "lands" assertion and adds a refusal pin. The ruling asks for this.
- `test_challenge_evidence.py`, line wrap: the list keeps the wrapped whitespace, so the test still pins normalisation.
- `test_revert_door.py`: `QUOTES` is two true spans. The revert assertions are unchanged.
- `test_night46_context.py`: only the refusal text changed. The criterion quoted twice is still refused on the test side.
- `test_desk_guards.py`, two night 122 tests: s145's test quote is a line of version 1, and the strict door refuses it on version 2. The tests now send a line of version 2 and keep the exact repeat-door text. On the real night, s145's call now meets the quote refusal before the repeat door. That costs one turn and follows the live-text rule.

## Point 7: the STALE set

The gate of the implementer at 5d76fddc lists 24 STALE cases: ACT-DV-edit-inside-the-function, L1-AR-a-dead-end-leaves-the-desk-to-a-named-seat, L1-CR-a-test-that-encodes-nothing-is-a-challenge, L1-CR-fail-names-its-criterion, L1-DV-a-wordless-answer-leaves-a-wrong-test-alone, L1-DV-act-on-an-answered-challenge, L1-DV-apply-the-answer-and-carry-on, L1-DV-ask-when-the-test-contradicts-its-criterion-at-the-fix-wake, L1-DV-challenge-a-test-that-contradicts-its-criterion, L1-DV-challenge-a-test-with-a-long-body, L1-DV-escalate-a-finding-the-loop-could-not-answer, L1-DV-fix-the-code-not-the-test, L1-DV-give-the-new-parameters-defaults, L1-DV-read-the-map-not-the-whole-file, L1-DV-take-a-mistake-out, L1-LI-present-the-touch, L1-TE-a-new-behaviour-is-a-new-callable, L1-TE-specify-criteria, L1-TS-apply-a-term-and-write-the-test, L1-TS-assert-the-value-the-surface-returns, L1-TS-encode-a-criterion-the-principal-corrected, L2-AR-place-a-block-developer-could-not, L3-a-challenge-reaches-the-role-that-can-answer-it, L3-scope-becomes-a-ticket-with-criteria.

The pass changes no case file. Probe p7 read the last recording of the 6 cases that pass 2 made stale. Every recorded challenge there sends a list, and the two-element lists are true spans. Each case also records a refused call: a one-element list, or a garbled test quote. Both doors refuse those calls, but the refusal text is new, so the next prompt has no cassette. A re-record absorbs this. L1-DV-fix-the-code-not-the-test is 0 of 120 on its recording already. The green door shows only in a model turn, so the reviewer could not check the case fixtures for a green run at the head. PLAUSIBLE: no case meets the green door.

## Point 8: the suite

The brief forbids a copy of `cassettes.db`, so the reviewer did not run the gate. The reviewer ran the unit suite with no `test_l1.py` and no `test_l3.py`, at 5d76fddc and at cce18a2e, in extracted trees:

- 5d76fddc: 12 failed, 4828 passed.
- cce18a2e: 13 failed, 4816 passed.
- The difference is `test_handover.py::test_a_reserve_that_is_all_too_full_is_a_drought`, red at the base only. The handover tests are flaky by record.

The 12 shared reds are older than the pass. They are git and run-database tests that an extracted tree cannot satisfy, `test_scene_two_batches` with the `kind` argument, `test_pins`, `test_roles_doc` and `test_onboarding`. The implementer's gate at 5d76fddc (`p328_gate3.txt`) has 21 new reds against the baseline of f9f5cd1, all in `test_l1` or `test_l3`:

- 18 STALE. Five of them are the pass's, and point 7 explains all five.
- 2 below threshold: ACT-TS-five-criteria-one-per-reply and L1-TS-act-on-the-reason-of-a-challenge. Both are red at cce18a2e.
- 1 follow check: ACT-TS-three-criteria-one-per-reply, a `ledger.log` door. It is red at cce18a2e.

No red is this pass's beyond the STALE ones.

## Findings

1. `rota/roles/api.py` 17111 to 17124, with `rota/core/boot.py` 163. High. PLAUSIBLE. A boot writes the base head into `head_commit` before any Developer commit. A test written before the code then fails at its assertion and gets the note, and the note invites the Tester to fit the old behaviour. The pass's report raises the same question. Fix: fire the note only when the batch has a `code.commit` of its own at the head.
2. `rota/core/sandbox.py` 1496 to 1511 and 1230. High. CONFIRMED. A quote has no floor, and one quote counts for both rows. `["in", "a1"]` and `["invoices"]` land, and the old window refused both. Fix: each quote holds at least 12 normalised characters or the whole row, and each row needs a quote of its own. Over the register this refuses 2 quotes.
3. `rota/roles/api.py` 17044. Low. CONFIRMED. With two red tests in one body, the note names the first `FAILED` test and quotes the last red line. Fix: take the name from the last `FAILED` line, or from the section header of the last traceback.
4. `rota/core/sandbox.py` 1244. Low. CONFIRMED. The escape form decodes a backslash-n that the row holds as code, so `"a<backslash-n>b"` matches `"a b"`. Fix: decode the escape only when a line break stands at the same place in the row.
5. `rota/core/sandbox.py` 1264. Low. CONFIRMED. One quote string `A ... B` splits into two spans, and each span passes alone, so an elided quote lands. Fix: carry the quote list through the binder's `stage`, and split only the join that the binder made.
6. `rota/core/sandbox.py` 1298 to 1305. Low. PLAUSIBLE, with the mechanism CONFIRMED on a synthetic database. A re-encode at the same head with no new run leaves the green run of the old body, and the door refuses a challenge on the new body. Fix: count only a run newer than the test's last encode.
7. Outside the points. `rota/core/sandbox.py` 1348. Low. CONFIRMED. The strict check also covers the Critic to Tester channel. The commit says "Developer", and the register shows 15 of 19 Critic messages refused, for example quotes of a code docstring in night 160. Fix: name the channel in the frame, and pin one Critic quote in a test.

## Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/66edc387-a3b2-48b8-8dec-bb5b3aa63e50/scratchpad/r328/probes/`. The extracted trees are `r328/tree` (5d76fddc) and `r328/base` (cce18a2e) in the same scratchpad.

- `p1_note.py`: ran nine bodies through `harness._run_one` on a scratch project, then `_own_assertion` on each output.
- `p2_span.py`: `_span_of` on the mark swap, the escape forms, one character, one word and an elided quote.
- `test_zz_probe_r328.py`: ran in the tree, then moved out. It sent quotes through the real `msg.challenge_tester` door. It called `_green_at_head_refusal` for a Developer, a Critic, a head with no run and a re-encoded body.
- `p34_register.py`: read the challenge messages of 112 night databases read-only. It ran the strict check and the window per channel.
- `p7_cases.py` and `p7b.py`: read the last recordings of the 6 newly stale cases from `cassettes.db` read-only.
- `p_n1.py` to `p_n3.py`: read the schema and s198's calls of night 166 read-only.
- The unit suite at both commits, with no `test_l1.py` and no `test_l3.py`. The outputs are `r328/unit_tree.txt` and `r328/unit_base.txt`.
- The new and changed test files and `test_end_form.py` at 5d76fddc: 481 passed.

## Usage

- Input tokens: about 120,000 (estimate, the harness gives no split).
- Output tokens: about 14,000 (estimate).
- Total: about 134,000.
