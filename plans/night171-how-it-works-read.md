# Night 171, the `how_it_works` row: a side wake rewrote the approved account, and no seat can amend it after his contest

Read under rule C76 on 2026-10-27, on Opus, about 180k, at head 838a507a. Read only. Sources: `.rota/clickI_night171.db` read-only, the jsonl, `rota/roles/api.py`, `rota/core/scheduler.py`, `rota/roles/principal.py`, `rota/core/sandbox.py`, the Vision Keeper briefs, `rota/LAWS.md`, `rota/DECISIONS.md`, `plans/composition.md`, frames 264 and 188 on the stack, `plans/frame264-reads.md`. The agent's write of this page was refused by the pause of 19:49, so the coordinator copied the agent's reply here unchanged in substance. The scratch files `s152_turns.txt` and `desc_writes.py` are in session b3bc8a66's scratchpad.

## 0. The result

A seat woken for an unrelated note rewrote the approved account row because the two doors on an observed row compare words only, and nothing checks whether the wake may change the row. No seat can amend the row after his contest because his words keep none of the account's words, so every door refuses, and the contested mode has no call that changes the approval. This is routine, not a one-off: over nights 140 to 171, description rows got text writes from 40 deliver wakes on 23 nights.

## 1. The turn

- s152, a Vision Keeper, was woken by m53, a deliver of ledger note l_0cfe6f462c about s1. It called `problem.assert` on `how_it_works` three times (seq 6, 10, 11) with new words. The door took it (observed: `s152_turns.txt`).
- The same-words door (api.py 2042 to 2056) needs an overlap of 0.8. s152's text shares 15 of 27 words with v2, 0.56, so the door let it pass (observed: `_prose_words`). v2 is taken to be s98's text, because the register keeps no version history (reasoned).
- The second door (api.py 2057 to 2068) compares against the statements the wake names. m53 named a ledger row and no statement, so the door did not run (observed).
- The account door (api.py 2118) needs half of the old words kept. s152 kept 15 of 21, so it passed (observed).
- `problem_assert` writes `"approval": "draft"` on every text change (api.py 2209). Nothing then checks law 9, a ratified amendment (observed).

## 2. How the change reached his pages

The signoff (scheduler.py 580) submits every draft. `off_page` (principal.py 1390) never removes a description row. `_page_body` prints the row under "What we are building:" (principal.py 2266) (observed). m65 showed it four times and m94 once on night 171.

## 3. Why no seat can amend it after his contest

His words keep 0 of the account's 21 words, and the account door needs 10. The row's own words hit the same-words door. The contested tick ends only when the approval leaves `contested`, and the contested mode has no call that changes the approval (observed: s203, s205, s207 refused, key at 3).

## 4. Upstream cause

m53 came from s149, a Liaison woken by a relay from the Liaison to itself. It had no `MODE:` line and every tool, and it sent `msg.deliver_vision_keeper(refs=['l_0cfe6f462c'])`. The deliver door (sandbox.py 4500) took a ledger ref. That is frame 188, open and unclaimed (observed).

## 5. Matches

- Frame 264 (parked) covers the contest half. Roman ruled it on 2026-10-17: the summary stays on the page under a heading that says it is the project today. That heading is not built (observed: the frame).
- `plans/frame264-reads.md` named a wall D, "some write path changes the text of an observed row", and said it was its own frame. No frame was opened. s152 is that write path (observed).
- None of the 37 facts covers which wake may change an item's text (observed: `plans/facts-2026-10-27.md`).
- The count: nights 140 to 171, description rows got text writes from 40 deliver wakes on 23 nights, 26 contested wakes, 2 challenges and 2 proposes. 3 of the 40 delivers carried no statement: s176 on night 143 for two rows, and s152. On night 160 three delivers moved the account from version 1 to 4, and three relays approved it again (observed: `desc_writes.py`).
- The doors are fix commits of 2026-09-09 to 09-12: 62c5c046, 0cc1733d, 78490b93, f4b29e57. None carries a ruling of his. His only ruling on the account is "a statement gets the account first" (DECISIONS.md 1355, 2026-09-03) (observed).

## 6. Proposal

- **Part A, one gate in `problem_assert`, api.py before line 2042.** An observed row with `is_description` 1 keeps its text on every wake except onboarding. The refusal gives the route the deliver brief already gives: assert what the principal asked for as its own item under its own name. It covers the 40 deliver writes, the 2 challenge writes, the 2 propose writes and the contested writes that put his request into a description row (wall D). The account door's text "Amend the account only to add the new behaviour" goes, because it comes from a fix commit and not a ruling. Price: 1 build cycle and 1 review, about 60k, then a gate. The Vision Keeper's deliver and contested cases that assert the account need new recordings. Night counts that move: description-row text writes outside onboarding, 44 on nights 140 to 171, to 0; account renderings after a seat's change, 5 on night 171, to 0; version bumps of the account per request, 3 on night 160, to 0; the quarantined `vision_keeper|tick:contested|how_it_works` key, to 0.
- **Part B, frame 264's ruled heading.** Priced at 2 cycles. It covers the misread that started the contest (m68 and m80 on night 171) and the 12 replies counted in frame 264's read.
- **Residue, no build.** A contested description row has no exit. Both exits, one at `land` and one new call in the contested mode, change what his contest means. Roman rules on either.
- **Departure.** None found. Part A enforces the deliver brief's "If `how_it_works` is already on file, leave it". His ruling of 2026-09-03 applies when no account exists yet.

## 7. Doubt

1. Why one session moved the version from 2 to 5 is not proved. Three staged writes would explain it.
2. v2 is taken to be s98's text.
3. The 37 deliver writes that carried a statement may be the intended way to keep the account current, and the account door invites them. If Roman wants the account to grow with each request, Part A departs from his intent.
4. Part A leaves the contest without an exit. A night with a contested description row still stops with the contested key at 3.
5. Part A closes the write that followed frame 188's hop, not the hop itself.
