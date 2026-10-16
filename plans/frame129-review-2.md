# Frame 129, review 2 of bc226206: a contested wake asserts only its refs, and frame 263's page-reply door

Reviewer: a read-only agent on Opus, in the worktree `C:/Users/roman/rota_r129` at bc226206.
Date: 2026-10-16. Workflow: the rota workflow (the door), reviewed from the meta workflow.

Verdict: the claim holds on all seven points. The door refuses the s112 new id and the 36 off-ref asserts.
It admits the brief's amend, and the counts re-run exactly. Seven low findings stay. Finding 1 is the sharpest.
The account door still tells a contested seat to assert a new id, and the new branch refuses that id.

## (a) The verdict on each point

1. HOLDS. A new id and an existing id outside the refs are refused, an in-ref id lands, and message and propose wakes are untouched. A contested wake with no refs refuses only decided ids.
2. HOLDS. The re-run from the worktree gives 347, 310, 1 new (1 landed), 36 existing (5 landed), and 14 of 310. The output matches `count.out` line for line. The three spot-read asserts are wrong by the contested brief.
3. HOLDS WITH LOWS. The 14 fires are all page talk. Of five admitted asserts read, two carry his page talk ("code pointer"). The "page size" probe is refused wrongly. A one-sentence reply verbatim lands.
4. HOLDS WITH A LOW. On M25 and M91 the door offers no sentence. The step "amend ... with what he said about X" has no source in his words. On s205's words (the m90 ruling and e_m108) the door offers no sentence either.
5. HOLDS. Five new tests are red on a `git archive 30f1d744` copy and green at bc226206. The amend test is green both ways.
6. HOLDS WITH A LOW. Every call named is in `contested.tools`. The words-door refusal has two fact sentences before its step. The amend step names no call.
7. HOLDS. No recorded case asserts off the refs on a contested wake. No recorded assert text holds a page cue. The INVENT offer is never made in replay.

### Point 1, the read

- The door reads the wake kind from `ctx.wake_kind` and the refs from `ctx.wake_refs`, filtered to strings (api.py:1392, 1411-1412).
- The branch at api.py:1413 fires only on `wake == "tick:contested"` with refs that do not hold the id. It runs before the `cur is None` branch, so a new id reaches it.
- A message wake (answer, propose) has `wake_kind == "message"` and empty refs, so the branch never fires. The probe returned None for a new id and for a non-decided id on both wakes.
- The `contested` predicate always sets one ref (predicates.py:305). With no refs, the probe shows: a new id lands, a non-decided id lands, and a decided id is refused by the old "names no contest" branch (api.py:1486). So a no-refs contested wake does not refuse everything.

Probe output, verbatim:

- New id: `json_only is not an item, and this wake contests how_it_works and makes no new item. Amend how_it_works with problem.assert on its own id, or answer with decisions.author`
- Existing non-decided id: `reads_flags is not the item this wake contests, which is how_it_works. Amend how_it_works with problem.assert on its own id, or answer with decisions.author`
- Existing decided id: `confirm_default_on_eof is the principal's own words, and this wake names no contest on confirm_default_on_eof. Amend how_it_works with problem.assert on its own id, or answer with decisions.author`
- In-ref id with his M38 sentence added to the account: LANDED, one items write.

### Point 2, the three spot reads

- Night 133, s342, turn 2. The wake contests `how_it_works`. He said "The page should say that confirm gets a new flag ...". The seat rewrote `confirm_default_on_eof`, then minuted it with `decisions.author`. The account stayed contested. Wrong by the contested brief: "One call, on the item's own id". Finding 1 shows that the account door points the other way.
- Night 143, s152, turn 2. The wake contests `provides_command_line_interface`, attempt 3 of 3, with no words in the prompt. The seat rewrote `how_it_works` and `defines_commands_and_options` in its own words. Wrong: the brief says to report when no words arrive.
- Night 150, s451, turn 2. The wake contests `how_it_works`. The account door refused turn 1. The seat then wrote "The program should cover only the version flag" into `json_only`. Wrong: his page talk on another item.

### Point 3, the predicate

- Cues (`_PAGE_CUE`, api.py:1308-1309): the word `page`, and `line` or `lines` followed by a digit, with a range such as "4 to 8".
- The three fires (api.py:1316-1345): a reply of more than one sentence equal by `_same_words`; a cue in the new text; or the first 4 words after a cue in one of his sentences, cut at the first comma, colon or semicolon.
- The 14 fires, re-run: seven night 142 texts name "Line 7", "Lines 1 and 8", "Line 2" or "line 1". Night 150's s112 turn 6 is his reply verbatim. s193 names "page". s205 copies the window of "The finished page should cover only the ...". s404, s420, s422 and s426 name "Lines 4 to 8". All 14 are page talk.
- Five admitted on-ref asserts whose words hold a page cue: night 140 s187, s189, s199, s203 and s243. s187, s189 and s243 are his words about the item. s199 and s203 write "the code pointer includes the utilities module where echo lives". That is his reply about the page (finding 5).
- "The page size option defaults to 20 rows ..." on an item `page_size_option`: refused, `the new text names 'page', a part of the page` (finding 3).
- A one-sentence reply verbatim, no cue: LANDED (finding 4). M25, two sentences, verbatim: refused.

### Point 4, the offered sentence

- M25 on `how_it_works`, with a seat text that adds words. The refusal ends: "Write his words about how_it_works, never his instruction about the page or the team: amend 'The program is a command-line interface toolkit called Click. [...]' with what he said about how_it_works, or keep the item and answer with decisions.author".
- M91 on `json_only`, with s205's text. The refusal, verbatim: "json_only is the principal's own words, and the new text copies his sentence 'The page should cover only the confirm flag.', which is about the page. Write his words about json_only, never his instruction about the page or the team: amend 'The program is built using the standard library json module only, without the Click toolkit.' with what he said about json_only, or keep the item and answer with decisions.author".
- The amend half of the step is not possible from the text in either case. M25 says nothing about `how_it_works` except a request to the team. M91 asks to take the json lines off the page, and no amend expresses that. The other half, `decisions.author`, is possible.
- s205's own wake words (e_m108) and the m90 ruling (r_c38db1262c, M91) both give `_item_sentence` None. The door offers no sentence on s205. Night 150's json_only rulings offer a sentence on 5 of 14. Of the 9 offers across night 150's contest rulings, 4 are page or team talk (finding 2).

### Point 5, red first

Red on the 30f1d744 copy, 5 failed, 20 passed:

- `test_s112_a_contested_wake_makes_no_new_item`: DID NOT RAISE.
- `test_s112_turn_6_his_reply_word_for_word_is_refused`: no refusal from the words door.
- `test_s205_his_instruction_about_the_page_is_refused`: DID NOT RAISE.
- `test_s404_a_text_that_names_lines_of_the_page_is_refused`: the old "Write what the principal said" text, so the regex did not match.
- `test_the_words_repair_says_what_an_items_text_is`: the old text.

`test_an_amend_with_his_ruling_sentence_lands` passed on both trees. At bc226206 the file gives 25 passed.
No test covers the "is not the item this wake contests" branch, the class of 36 (finding 6).

### Point 6, the refusal texts

- `_contested_elsewhere`: one fact sentence and one step. It names `problem.assert` and `decisions.author` only when `_wake_mode_tools` lists them. `contested.tools` lists both.
- The page refusal: one fact sentence and one step sentence. The words refusal (api.py:1583-1585) has two fact sentences, then the step.
- `_amend_step` says "amend ... with ..." and names no call. A seat must infer `problem.assert`. The quoted item text and his quoted sentence hold full stops, so the step reads as several sentences.
- The `keep` text (api.py:1480) still names `msg.report_liaison`, which `contested.tools` offers.

### Point 7, the INVENT offer

- The register at `D:/repos/rota/tests/rota/cassettes.db` holds 292 cassettes on a contested wake over six models, 216 on qwen3:8b.
- Every `problem.assert` id in a qwen3:8b completion is the wake's ref: seven ref ids, 25 calls. The 19 "off" hits on qwen3:4b are prose words from a loose regex, not calls.
- The two cases are `L1-VK-amend-a-contested-item` and `L1-VK-amend-a-contested-item-from-a-verdict` in `tests/rota/cases/l1_gatekeeper2.yaml`. Both assert on `<i1>`, the ref.
- So `_contested_elsewhere` never fires in replay, no `_offer` with INVENT is made, and no follow check meets it. No recorded assert text holds a page cue.

## (b) Findings

1. api.py:1760-1765 and 1706-1711 against api.py:1413. Low. CONFIRMED.
   The account door tells a contested seat "A behaviour the principal asked for is its own item: assert it under its own name". The new branch then refuses that new id. Probe p1b replays s451's turn 1 on night 150's words. Turn 1 got the account refusal. A new id then got "is not an item, and this wake contests how_it_works and makes no new item". Adding to the account then landed. So a path exists, but one door names a call that another door refuses, against frame 135's law. Night 133's s342 and night 150's s451 took the account door's direction. The rating is low because the 37 are wrong by the contested brief.
   Fix: on `tick:contested`, drop "assert it under its own name" from the account door and the observed door, and keep "Amend the account only to add the new behaviour".
2. api.py:1356-1365, `_item_sentence`. Low. CONFIRMED.
   The offer keeps a sentence about the page when the line has no digit. Night 150 offers "Drop those lines." (m6), "otherwise drop the line." (m11), "The other lines match what I asked for." (m345), and "That line is really my earlier correction [...] so please settle its open notes first" (m_shift). Probe 4x: the refusal offers "Drop those lines.", and an assert of that text then LANDED on the item.
   Fix: in the offer only, drop a sentence that holds `line`, `lines` or `page` in any form, or "please" anywhere.
3. api.py:1336-1339. Low. CONFIRMED.
   A cue in the new text refuses the assert whatever the item says. Probe 3a: an item `page_size_option` cannot be amended with any text that keeps "page".
   Fix: skip the text cue when the cue's words stand in `cur["text"]`.
4. api.py:1333. Low. CONFIRMED.
   The verbatim check needs more than one sentence in his reply. Probe 3b: a one-sentence reply asserted word for word LANDED.
   Fix: drop the `len(sents) > 1` guard, or keep it only for a reply that is one bare request about the item.
5. api.py:1308-1309, the cue. Low. CONFIRMED.
   Night 140's s199 and s203 wrote "the code pointer includes the utilities module where echo lives" from his "Line 1's code pointer still names only test files". The 4-word window after "Line 1" is "s code pointer still". The text does not hold it, so the predicate admits the text. The 296 admitted asserts are not all read.
   Fix: add "code pointer" to the text cue, and count the admitted asserts again.
6. tests/rota/test_frame221_assert_words.py, the new tests. Low. CONFIRMED.
   No test asserts the "is not the item this wake contests" branch. That branch holds the class of 36 in the count, and nights meet it most.
   Fix: add the night 150 s451 turn 2 assert on `json_only` under a `how_it_works` wake as a test.
7. api.py:1371-1375, `_amend_step`. Low. PLAUSIBLE.
   When no sentence is offered, the step says "amend [...] with what he said about X". On M25 and M91 his words hold nothing about X. The contested brief's route for an unclear contest is `msg.report_liaison`, and the step leaves it out.
   Fix: when `_item_sentence` is None, name `msg.report_liaison` in place of the amend.

Outside the points: findings 1 and 2 are outside the brief's claim text. Both bear on the next night.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/738ddbaf-1cc4-48f9-9414-01f5058ba1fb/scratchpad/f129/r2/`. Every database opens with `?mode=ro`.

- `run_count.py`: runs `count.py` with `rota` imported from the worktree. Output `count_r2.out`. It matches `count.out` with CR bytes ignored.
- `spot.py`: reads night 133 s342, night 143 s152 and night 150 s451 turns and wake words.
- `p1.py`: the point 1 branches on the test file's fixture: new, non-decided, decided, in-ref, answer, propose, no refs.
- `p1b.py`: the account door against the new branch, on night 150's m356 words.
- `p3.py`, output `p3.out`: the predicate over nights 140 and later, the 14 fires and the admitted asserts whose words hold a page cue.
- `p4a.py`: s112's and s205's wake words, and the m24 and m90 rulings, night 150.
- `p4.py`: `_item_sentence` over night 150's contest rulings.
- `p34.py`: the page-size text, the one-sentence verbatim reply, the M25 and M91 refusals, and the "Drop those lines." offer and its assert.
- `old/`: a `git archive 30f1d744` copy with bc226206's test file. `pytest tests/rota/test_frame221_assert_words.py` ran there and in the worktree.
- `p7.py`, `p7b.py`, `p7c.py`: the register's schema, and every contested-wake cassette's assert ids and texts.

## (d) Usage

The harness line is the authority. This agent's own estimate: input about 110k tokens, output about 15k tokens, total about 125k tokens. That is over the brief's cap of 50k. The count re-run and the register read cost the most.
