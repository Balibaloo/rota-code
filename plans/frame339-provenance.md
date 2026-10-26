# Frame 339, the provenance of the removal door and its matcher

Read-only read on Opus, 2026-10-26 20:41 to 20:53, at HEAD def9530d. The live register was copied with the sqlite backup API to `f339_clickI_copy.db` in session 8db3a3f9's scratchpad, and the night copies were opened `?mode=ro`. Line numbers are at HEAD.

## Answers

1. **No ruling of Roman's names the removal door.** The session built it in frame 283, W1 a, pass 1, commit 92e240fc (2026-10-21 16:40), from night 158's read. The only ruled source is the composition line "A prediction never blocks. Only a fact or a ruling gates." (ruled: C, ratified 2026-09-16). The door's own comment and commit body cite that line (observed).
2. **The phrase match on "line N" came in pass 2, commit 2acc7b5c (2026-10-23 12:54), frame 283, W1 a, rota workflow. No brief, status line or review asked for it.** e48bdaf2 (pass 4b, 16:00) moved it into the request clause. The build meets the frame's Ends-when, which is about notes. It does not meet the W1 a condition "lands only on a criterion or on his words" for his words in any form other than three fixed shapes (reasoned).
3. **e1cfcdd2 (2026-10-24 21:36), frame 312, row 5, pass 1b, added the sentence to copy.** Frame 312's review w5 said his other words fail, and called the route "a seat's route". The frame closed the row with that finding left to frame 283. Frame 283 then closed on 2026-10-26 with the finding still open (observed).
4. **No ruling says the permission is read from a structured record, or that a door never reads his free text by a phrase.** The door departs in part from the ruling of 2026-10-17 16:50 that an unexpected change goes to the Architect for sign-off (reasoned, below).
5. **Nights 160 to 168: 0 refusals each. Night 169, to 20:41: 15 seen in turns, over 5 Developer sessions, and 12 of the 15 followed his answer that granted the removal in other words** (observed: below).

## Q1, the door's origin

- `git log -S "_unruled_removal"`: first code commit 92e240fc, "fix(api): a removal of a base statement lands on a ruling, never on a note". Body: "A note is the seat's own claim, and only a fact or a ruling gates." (observed).
- `rota/roles/api.py:20566-20569`, the comment: "Frame 283's W1 a ... A note is the seat's own claim, so only a ruling admits a removal (composition: only a fact or a ruling gates)." (observed).
- The scope came from the session, not from Roman. `plans/night158-read.md:280`: "W1 (a), frame 283's case, 2 cycles: a removal of a base statement lands only on a criterion or on his words, not on a note's own claim" (reasoned there, not ruled). Frame 283 status 2026-10-21 16:23 (rota-f9) repeats it, tagged "Meta workflow" (observed: `plans/archive/stack-2026-10-26.md`, block `### 283.`, line 56 of the block).
- `plans/composition.md:73`, "A prediction never blocks. Only a fact or a ruling gates.", commit 9f8cbdf5, 2026-09-16 (ruled: C).
- The grep of `plans/stack.md`, the archive, `rota/DECISIONS.md` and `rota/LAWS.md` for "removal", "removes" and "unruled" finds no ruling of Roman's on a removal door. Frames 140 and 283 hold no "(ruled: Roman" line on the door (observed). Note: `DECISIONS.md` and `LAWS.md` are under `rota/`, not at the root.

## Q2, the matcher

- The line: `api.py:20844`, `if principal and g["no"] and re.search(rf"\bline {g['no']}\b", c, re.I): return True` (observed).
- `git log -G "line \{g\['no'\]\}"`: 2acc7b5c added it with the docstring "The principal's words can name the line by its number." e48bdaf2 changed `s` to `c`, the request clause (observed).
- The status line of pass 2, 2026-10-23 12:38 (rota-08): "Pass 2 runs ... the batch's own texts that ask for the removal". The 12:54 line: "the predicate reads the batch's own criteria, request item and rulings and needs a removal word". No line in the block names a line number (observed: grep of the 283 block for "line number", "by its number").
- The only review word on it is about false admits. `plans/frame283-review-w1a-2.md:28`, finding 3, low: "Page-line numbers of the principal admit a removal by chance." Fix offered: "require the path or the call name ... or drop the line-number rule." Review 3 (`frame283-review-w1a-3.md:32`): "The page-line number rule is still at `16929`." No review probed a grant in other words (observed).
- Workflow: the site line of frame 283 says "Rota workflow". Pass 2's line at 12:54 has no tag, and the 13:24 acceptance line says "Rota workflow" (observed).
- The frame's Ends-when, `plans/archive/stack-2026-10-26.md`, block line 21: "first, the mechanism: a commit whose tree removes a statement that no landed note names is refused whatever reply wrote it, with s340's turn 14 as the red test, and the count of the door over nights 140 to 154 before and after; second, on a night, batches whose first red project test follows an unnoted removal, from 1 of 4 toward 0 of the next 3, beside frame 140's ratio; third, a session that still shows the sign is read, and the frame closes when its cause is not the one this frame names." (observed).
- The status line of 2026-10-24 21:40 (rota-4e) names the gap as unmet: "a rewrite that a criterion names is not an unruled removal, not yet met for his words" (observed).
- Met or not: the Ends-when measures notes and red tests, so frame 283 closed on 2026-10-26 18:08 by it. Nights 166 to 168 hold 0 fires of this door, so the close measured no grant in other words. The W1 a condition "on his words" is met only for the quoted statement, the call head, and "line N" inside a removal clause (reasoned).

## Q3, the sentence to copy

- `git log -S "To allow that, say so"`: e1cfcdd2, cherry-picked from 26186652 (frame 312 status 21:47). Text at `rota/roles/principal.py:1482-1483` (observed).
- The earlier form came in 172c86ff (from 16c36c2f): "If the change must remove it, say so, as '...'" (observed: `git show 172c86ff`).
- Frame 312's review, `plans/frame312-review-w5.md:49-55`, finding 2, high: "The page's phrase lands when the ruling is keyed to a criterion or to the batch rows ... His own words 'clear() must return False there instead of the bare return' are refused ... So the route depends on how the Liaison writes the ruling. That is a seat's route." (observed).
- The re-check, lines 120-131: "the door admits only removal words ... So the page cannot offer the rewrite's own words today ... Do it in a new frame." Status 21:47 (rota-4e): "the medium on the offered 'remove' sentence stays with frame 283" (observed).
- Frame 283 got it as a residue line at 21:40, "the words route is the next pass after its read". No pass built it before the close (observed: the block's later lines; reasoned: no commit on `_asks_removal` after 2026-10-23 16:18).

## Q4, a ruling crossed

- No ruling covers a structured permission or a ban on a phrase read (observed: the greps of Q1, plus "phrase", "regex", "keyword", "structured" with "ruled: Roman").
- The ruling nearest to a departure: `rota/DECISIONS.md:1490`, 2026-10-17 about 16:50, Roman: "File writes were always permitted everywhere, just that if there were unexpected changes then the architect is required to sign off." Its consequence: "a door that refuses a write for the want of a criterion is a wall to fix, not a rule." (ruled: Roman, 2026-10-17). The removal door refuses a commit for the want of a criterion, request or ruling. In the `batch_start` mode its text names no Architect route (observed: `plans/night169-m36-read.md`, Q3). So the door departs from that ruling in part (reasoned). The ruling's list of kept backstops holds "a removal", but that list is the fence's reach of the code, not a removed statement (reasoned).
- Records near the question, none a ban: the composition, "A ruling is a record. The Principal rules, the Liaison writes it, and it carries a version." (ruled: C, 2026-09-16). `DECISIONS.md:1445`, 2026-10-08 23:25: "Every word of the principal is a ruling on a row" (ruled: Roman). `LAWS.md:114`, law 2: "Judgement crosses a role boundary only as structured findings — ids and states." (observed).
- His structured verdict exists and the door does not read it: r_58bf1e8c70 `per_item` holds `"batch_1": "approve"` (observed: the register copy).

## Q5, the count

Signature: the commit refusal "this commit removes ... No criterion, request or ruling of the principal names". A turn's `user` holds the session's history, so the count per session is the most refusals in one turn. The result of a session's last commit is in no turn, so the count is a floor.

| Night | Database | Refusals | Sessions | After a grant in other words |
|---|---|---|---|---|
| 160 to 168 | `clickI_night160.db` to `clickI_night168.db`, and `164a` | 0 each | 0 | 0 |
| 169, to 20:41 | live copy | 15 seen, 18 commit calls | s124, s129, s130, s131, s136, 3 each | 12, in s129 to s131 and s136 |

- s124 (attempt 3) came before m36 and m37. Its words block held m25 and m33, a contest of line 4, and no grant. So its 3 do not count (observed).
- s129 to s131 followed r_58bf1e8c70 (m37), "You can remove the line at 518 in get_app_dir that sets the folder to the bare home folder." s136 followed r_62dd42ab85 (m41), "Yes, you can remove the line at 518 ...". Each first turn holds "line at 518" in the words block (observed).
- s122 and s123 met the open-note door, not this door: "a code.write in an earlier reply returned a note ..." and "your code.write in this reply returned a note before this commit ...". The gathering read's "refused every commit" is right for s124 only. s139 and s140, live at the copy, met the open-note door and the repeat door (observed).

## Usage

About 75k tokens in, all questions reached. No sub-agents.
