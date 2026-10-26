# The reach of 17 closed frames, archives of 2026-10-17, 2026-10-18 and 2026-10-21

Roman asked on 2026-10-26 at about 21:5x: "with all this knowledge, send another agent to review frames resolved in the last two weeks to see how much work should have been generalised". This record reads the 17 frames of `plans/archive/stack-2026-10-17.md`, `stack-2026-10-18.md` and `stack-2026-10-21.md`, read only, at head d1c934ae. The shape is the one of `plans/agency-prevalence-2026-10-26.md`: a fact held once, re-derived by N readers, and a fix that adds a rule at the reader the night showed.

## The result

13 of 17 frames fixed at one door of N. 2 of 17 fixed at the source, frames 220 and 290. 2 of 17 are not this shape, frames 287 and 293. 0 of 17 rest on a wrong premise (observed: the table below). The 15 frames of the shape cost 104 cycles by their closing status lines. A fix at the source of each fact would have cost about 42 cycles by the anchors (reasoned: the last section). Twelve of the 13 door fixes have a later frame at the same fact.

| Frame | Closed on | The fact | Reach then, k of N | Reach now | Later frames | Verdict |
|---|---|---|---|---|---|---|
| 261 | 2026-10-17 | the drafts that woke a signoff | 1 of 2 send routes refuse, the door re-queries the tick's set | 2 queries | none found | at one door of 2 |
| 129 | 2026-10-17 | who owns an item's words on an assert | 1 branch per wake kind, 4 branches | 4 branches | 263, 275, 303, 315 | at one door of 4 |
| 263 | 2026-10-17 | which of his sentences are about the item | 1 of 3 sentence splitters, a new `_PAGE_CUE` | 4 splitters, 2 cue regexes | 275, 315, 322, 337 | at one door of 3 |
| 222 | 2026-10-17 | the import line that binds a name | 1 of 3 import readers | 3 | 260, 301 | at one door of 3 |
| 223 | 2026-10-17 | the raise frame of a failed run | 1 of 2 traceback readers | 4 | 284, 336 | at one door of 2 |
| 267 | 2026-10-17 | a reply landed no ruling | 1 of about 7 answered-mark writers | about 10 | 320, 272 | at one door of 7 |
| 273 | 2026-10-18 | an assert that cannot fail | 1 of 2 rules | 3 rules | 277, 304, 328 | at one door of 2 |
| 274 | 2026-10-18 | which request owns a row | 0 of 6 owner functions, a 7th rule in `land` | 7 | 316, 268, 298's `_owner_of_ref` | at one door of 6 |
| 277 | 2026-10-21 | an assert that cannot fail | 1 of 3 rules | 3 rules | 304, 328 | at one door of 3 |
| 220 | 2026-10-21 | the file at the batch's base commit | 2 of 3, `_base_text` shared with `_base_held` | 1 helper, 1 tool copy | 286 reused it | at the source |
| 282 | 2026-10-21 | the line numbers his words name | 1 of 3 regexes | 6 regexes | 289, 305, 272 | at one door of 3 |
| 286 | 2026-10-21 | law 12, a stray goes to the Architect | 1 of 2 refusing doors | 1 door refuses | 339, 306 | at one door of 2 |
| 290 | 2026-10-21 | a criterion contradicts its request | 2 of 2 doors, one helper | 1 helper | none at the fact | at the source |
| 296 | 2026-10-21 | his words name the request | 1 of 2 predicates, a 2nd added | 2 | 337, 322, 305 | at one door of 2 |
| 298 | 2026-10-21 | the request's predicted files | the guess at the source, his file words at a new parser | 4 readers of his fault words | 299, 300, 302, 305, 307, 315 | at one door of 4 |
| 287 | 2026-10-18 | none, the method rebuilt | not counted | not counted | 340 | not this shape |
| 293 | 2026-10-18 | none, a ledger pilot measured | not counted | not counted | none | not this shape |

## The frames

**261.** The tick computes the signoff drafts and sends them as wake refs, and the door re-queries each ref with its own SQL (observed: `scheduler.py` 507 and `api.py` 730 at 65ee8ca1). Review 1 found the door's copy lacked the tick's `not_parked` filter, and pass 1b copied it, the drift of a second reader (observed: the frame's 11:09 line, the diff of 65ee8ca1). The `present` route adds the wake refs itself at `sandbox.py` 3250, the route review 1 named for the submit (observed: grep at 65ee8ca1). No later frame names the door (observed: the later records searched), so the cost of the second reader has not shown yet (reasoned).

**129.** The door `_assert_words_fault` decides by the wake kind whether a session may rewrite an item, and each pass added a branch: contested, propose, answer, deliver (observed: the lines of 17:41 and 18:16, the diff of bc226206). The fact under the branches is the owner of the item's words, which no record holds (reasoned: review 1b's low, "every deliver wake gets through"). Frames 263, 275, 303 and 315 sit at the same door or the same fact (observed: the later records name `_assert_words_fault` or "frame 129").

**263.** Built inside frame 129's pass 2 at bc226206, it adds `_PAGE_CUE`, a line-number regex, and `_sentences`, the third copy of the sentence split in `api.py` (observed: grep at bc226206, 3 splits). His words about an item are the fact of group 2 in `plans/agency-groups-2026-10-26.md`, and frames 322 and 337 propose one reader for it (observed: the groups page, section 1). Frame 275 met the same door on another word form (observed: its heading).

**222.** The NameError hint builds an import line with `_package_definer`, beside the older `_package_definers`, and the surface door reads imports with `keep_root` (observed: grep at c5f67351 and d1c934ae, both helpers still present). Review 1's second high found the two doors disagree on the `src.` prefix, and frame 260 holds that disagreement (observed: review 1 in the frame, frame 260's heading). Frame 301 is the same door offering a shape it refuses (observed: its heading).

**223.** The push reads the raise frame with `_TRACE_FRAME`, native frames only, while `_rota_caught.py` reads tracebacks by its own rule (observed: grep at afcf52d3, 2 readers). Night 154 showed 0 of 19 pushes, because pytest prints its own form, and frame 284 holds that (observed: the close line, frame 284's heading). At head 4 places read a traceback, and frame 336's agency read proposes one `error_line()` for all (observed: grep at d1c934ae, the prevalence table).

**267.** The fix guards the answered mark of a page reply in `session_commit`, while `db.py`, `scheduler.py`, `principal.py`, `predicates.py` and `runner.py` set or read the answered state at about 7 places (observed: grep at 98b7b562). Pass 1c added `REFUSED_END` beside `REPEAT_END`, and "the runner keeps its own copy of the text" (observed: the line of 20:27). Frame 320, a fresh request whose session lands nothing is marked answered, is the same fact on another path (observed: frame 320's heading).

**273.** The door gained `_vacuous` beside the old constant rule, two rules for one fact (observed: the diff of 000dfa78). Night 153 showed a tautology that neither rule reads, and frame 277 added a third (observed: the line of 03:39). Frame 328's `_own_assertions` and frame 304, an arrange step that raises, read the same fact again (observed: grep at d1c934ae, frame 304's heading).

**274.** Six functions decide which request owns a row at 6553d0f1: `request_of`, `off_page`, `_is_description`, `page_request`, `_is_request_item`, `current_request` (observed: grep). Review 1 found `request_of` and `off_page` disagree on a description, and night 153 found `request_of` gives None for a criterion (observed: the lines of 23:41 and 04:31). Frame 316 holds a page that carries the rows of other items, and frame 298 added `_owner_of_ref` (observed: frame 316's site names `request_of` and `off_page`, grep at d1c934ae).

**277.** It adds a third rule, `_only_reads`, inside the `or` (observed: grep at 8b290211). Three reviews and 7 cycles went to one predicate on one fact (observed: the close line). A fix that read "can this assert fail" once would have taken 273, 277 and 304 (reasoned: the three bodies differ in shape and not in fact).

**220.** The fix made `_base_text` the one reader of the base commit's file, and frame 283's `_base_held` calls it (observed: the line of 23:05, grep at d2ffdfe3). Frame 286 then read the base through `_base_text` and wrote no new reader (observed: frame 286's 00:03 line). A `git show` copy stays in `rota/tools/invariants.py` 111, a tool and not a door (observed: grep at d2ffdfe3).

**282.** The fix widened `_LINE_REF`, one of three regexes that read line numbers from his words, beside `_PAGE_CUE` and `_WORDS_FAULT` (observed: grep at 42a4449e). Review 2 found `land` and `_line_refusal` read with no page size, and frame 289 found the fault cues miss his words (observed: the lines of 18:45 and 18:47). At head six such regexes stand, and frame 305 holds the next miss (observed: grep at d1c934ae, the close line).

**286.** The `code.write` door now writes a stray for the Architect, as law 12 says (observed: the diff of b0dbd926). The removal door still refuses on the same law, and frame 339 holds it, with "frame 286's route" as its proposal (observed: `plans/frame339-agency-read.md`, the prevalence table). Frame 306, a change outside the criteria that merges with no page, sits at the same law (observed: frame 306's heading).

**290.** The triage check moved unchanged into `_contradiction_offer`, and both doors call it (observed: the line of 19:21, grep at db99b45b). Review 1 found the night count 0 of 112, so the wall came from one re-record, and the fix stands as a door right by law (observed: the line of 19:27). The offer-against-door shape returns in frames 301, 334 and 335 with other facts (reasoned: the groups page, the cross-group shape).

**296.** The fix wrote a number-or-quote check for "the words name the request" beside frame 258's `_names_request`, and the two give opposite answers on m125 (observed: review 1 at 11:51, grep at 1dc02594). The close leaves both as frame 258's residue (observed: the close line). Frame 337's agency read names `_names_request` among the readers of his ruling (observed: `plans/frame337-agency-read.md`).

**298.** The Architect's guess became a row, and the send door stamps the line once for the render and `land` to read, which is the source (observed: the lines of 12:40 and 15:04). The parser `disputed_paths` is a fourth reader of what his words fault, and reviews 5 and the probe found wrong parses on kept clauses (observed: the lines of 16:23 and 16:31). Frames 299, 300, 302, 305, 307 and 315 followed at the same request line or the same words (observed: their headings).

**287.** The frame rebuilt the meta workflow: the intent page, the state and status tools, the reference page and the law lines (observed: the close line). It re-derives no fact for a door (reasoned). Its tools parse the stack's status lines, and frame 340's commits d1c934ae and 6e3a442c widen those parses, a sign of the shape inside the tools (observed: `git log` at head).

**293.** A pilot that measured a rulings ledger, 0 of 11 by the question's words (observed: the close line). It is a measurement with no reader of a fact (reasoned).

## The counts

| Verdict | Count | Frames |
|---|---|---|
| at the source | 2 | 220, 290 |
| at one door of N | 13 | 129, 222, 223, 261, 263, 267, 273, 274, 277, 282, 286, 296, 298 |
| wrong premise | 0 | none |
| not this shape | 2 | 287, 293 |

Cycles by the closing status lines (observed): 261 4, 129 5 with pass 2 unrecorded, 263 0 inside 129's pass 2, 222 7, 223 9, 267 6, 273 2, 274 6, 277 7, 220 4, 282 6, 286 6, 290 3, 296 4, 298 35. The 15 frames of the shape cost 104 cycles, the 13 door frames 97 of them. Frames 287 and 293 cost about 29 and 5 more.

A fix at the source, by the anchors of `plans/operating-facts.md` (a door text 2, an instrument fix 3, a seam design 8 to 10), costs about 42 cycles (reasoned). The facts form 12 groups: 129 with 263, 273 with 277, 282 with 296, and nine alone. Ten groups at 3, frame 290 at 2 and frame 298 at 10 give 42. The 42 leave out the later frames that a source fix would have closed, at least 20 by the table, so the gap is wider than 104 against 42 (reasoned).

## The doubt

1. The N counts come from grep on names and patterns, so a reader that re-derives a fact with no shared word is missed. Every N is a lower bound (reasoned).
2. Frame 129's cycles and frame 263's share one pass 2 with no cycle line of its own (observed: the two blocks).
3. The later frames are matched by headings and by the identifiers they name. No later frame's code was read for this record (reasoned).
