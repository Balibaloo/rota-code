# Night 172, the read of the rulings walls W5 and W6, by rule C76

Meta workflow, read on 2026-10-28 at head de1203a9, which holds the F2 merge 135c87d1 (observed: `git merge-base --is-ancestor`). The code under `rota/` has no commit after de1203a9 (observed: `git log de1203a9..HEAD -- rota/`). Sources: `.rota/clickI_night172.db` opened `?mode=ro`, the night 170 and 171 registers for the reach, `plans/night172-read.md` sections 3 and 7, `plans/facts-2026-10-27.md` rows F2 and F3, `plans/rootfix-audit-2026-10-27-a.md` F2 and F3, frame 344's status lines of 2026-10-28 02:22 to 02:43, `plans/f2-review-p1.md`, and the code. One agent on Opus. No code was edited. No commit. The replays ran the head's `rulings_rule` on a scratch copy of the register (section 6, the method).

**The result. Two gaps in one door, and neither is a cause the F2 build could change.**

1. **W6: the empty-words check reads one argument, and the seat put his words in another.** `rulings_rule` refuses a contest when the top-level `words` argument is empty (api.py 14063 to 14083). It does not read `words` inside a line's object or inside `acts`. It does not read his reply, which the door already holds as `his` (api.py 13685). The check dates from 2026-09-10 (b57772f5). The `acts` and object forms that carry `words` came on 2026-10-27 (efde1aea), whose body says "Every refusal of rulings.rule stays". On nights 170 to 172, 19 of 20 calls refused with "words is empty" held a verbatim span of his words in a nested `words` field (observed: section 4). At head, s271's call lands when the door takes his reply as the words (observed: the replay).
2. **W5: a reply that numbers one line let a contest land on a criterion line it never names.** `_unnamed_contest` spares every request line and criterion line when the reply holds one sentence with no line number (api.py 13150 to 13152). m121 held two such sentences: "Please fix the change ... put back the two removed lines of code ..." and "The other lines are fine." So the contest of line 4, c_2, passed (observed: a direct call of `_unnamed_contest` with s258's inputs). The act on line 12, `remove` on `src/click/utils.py:12`, passed because an act with no words of its own rests on the whole reply, and the whole reply is his (api.py 13738 to 13754).

**The proposal.** One change at the rulings door, `rulings_rule` and its helper `_unnamed_contest` in `rota/roles/api.py`: the door reads his words and the lines they name from the record, and spares only what they name. Three edits, priced 4 cycles. Section 6 gives the edits, the red tests and what the change leaves out.

## 1. The find, question 1

### s258, the Liaison on m121, which landed r_m121

**What the seat was shown** (observed: s258 turn 1, `landing`). The page m120, verbatim in its lines: line 1 the item `format_filename_example`; lines 2, 4 and 6 the criteria c_1, c_2 and c_3; lines 3, 5 and 7 their tests, each "Passes"; "The team gave up: the tests still fail after 3 attempts"; line 8 the touch line of bg_3; lines 9 to 12 the read-back lines of m84, m93, m98 and m118. Line 12: `Your answer "", as the team read it: 1 line approved. Say ok, or say what we misread.` The `lines` map: 4 is `c_2_format_filename_example`, 12 is `reading:m118`. The `reply` and `principal_said`: "Please fix the change instead of giving up: put back the two removed lines of code, because only the docstring changes and the code stays the same. Line 12 is wrong, because my last answer was not empty: I said the example shows both the input path and the short output, and the removed code must go back. The other lines are fine."

**What it sent and what came back.** Each call passed the whole reply as the top-level `words` (observed: the completions). No call passed `acts`.

| Call | `rulings` | Result |
|---|---|---|
| 1 | 1 to 3 approve, **4 contest**, 5 to 11 approve, 12 contest, and `"act": "remove"`, `"target_kind": "source_line"`, `"target": "src/click/utils.py:12"` as keys of the map | "`act`, `target_kind`, `target` are fields of one line's object, not lines of the page. Put them inside the line they are about: ..." |
| 2 | as 1, with the three fields inside line 12's object `{"verdict": "contest", "act": "remove", "target_kind": "source_line", "target": "src/click/utils.py:12"}` | "line 9 is his read-back line, and only his words confirm it. His reply does not say that line 9 is right, and it does not approve the whole page. Leave line 9 out of the ruling" |
| 3, 4 | as 2, with `"9": "ignore"` | "line 9: 'ignore' is not a ruling. Each line takes approve, contest or revise. ..." twice |
| 5 | as 2 | the read-back text for line 9 |
| 6 | as 2, line 9 left out | the read-back text for line 10 |
| 7 | lines 9 and 10 left out | the read-back text for line 11 |
| 8 | lines 1 to 3 approve, **4 contest**, 5 to 8 approve, 12 the object of call 2, lines 9 to 11 left out | landed r_m121 |

**The landed ruling beside his words** (observed: `rulings`, `ruled_refs` source `reading`).

| Line | Ref | Verdict | Act, target kind, target | His words on the line |
|---|---|---|---|---|
| 1 to 3, 5 to 8 | the item, c_1, the three tests, bg_3 | approve | none | "The other lines are fine." |
| 4 | `c_2_format_filename_example` | **contest** | none | none. His words name line 12 only (observed: `_line_reading(m121, 12).named` is {12}) |
| 9 to 11 | `reading:m84`, `reading:m93`, `reading:m98` | no row | | "The other lines are fine." |
| 12 | `reading:m118` | contest | **remove, `source_line`, `src/click/utils.py:12`** | "Line 12 is wrong, because my last answer was not empty" |

Each row's `words` is the whole reply. Four `landed` rows derive from the reading rows, line 4's contest among them. `rulings.texts` keeps c_2's old text. Line 12 of the page is a read-back line and holds no code. His words ask to "put back" code, and the act says `remove` (observed). s260 then respecified c_2 on the contest (observed: `plans/night172-read.md` section 3, step 8). m127 and m130 read the ruling back as "line 4 is wrong; 7 lines approved" (observed: s269 and s273, `landing.page`).

### s269 to s275, on m128, m129, m131 and m132

The page of s269 to s271 is m127: lines 1 to 8 as m120, line 4 now the respecified c_2, and lines 9 to 11 the read-back lines of m84, m93 and m121. Line 11 says "line 4 is wrong; 7 lines approved". The page of s273 to s275 is m130: 18 lines, line 2 the guess line, line 4 the test `tst_c1`, line 5 c_2, lines 9 to 15 the Critic's falsified constraint claims, lines 16 to 18 the read-back lines of m84, m93 and m121 (observed: each session's `landing.lines`).

| Session, call | His reply | Fields the seat filled | Result |
|---|---|---|---|
| s269, 1 | m128 | `rulings` 1 to 10 approve, 11 contest; `words` the whole reply | "line 9 is his read-back line, ... Leave line 9 out of the ruling" |
| s269, 2 and 3 | m128 | as 1, `"9": "ignore"` | "line 9: 'ignore' is not a ruling. ..." twice; then the repeat rule ended the session |
| s270, 1 and 2 | m128 | `rulings` 1 to 8 approve, 9, 10 and 11 contest; `words` the whole reply | "The words name lines 4 and 11 and do not name lines 9 and 10. A contest rests on the principal's words. Approve the lines the words do not name, or rule them as the words say." twice; repeat end |
| s271, 1 and 2 | m129 | `rulings` 1 to 10 approve, 11 contest; **no `words`**; `acts={"11": {"verdict": "contest", "act": "remove", "target_kind": "row", "words": "Fix the change instead of giving up by putting back the two removed lines of code, because only the docstring changes and the code stays the same."}}` | "a contest carries the principal's words to the row's owner, and words is empty. Pass the reply, whole" twice; repeat end |
| s273, 1 and 2 | m131 | `rulings` 1 to 3 approve, **4 contest**, 5 to 8 approve, 9 to 15 `drop`, 16 and 17 approve, 18 contest; no `words`; `acts={"4": {"verdict": "contest", "act": "remove", "target_kind": "row", "words": "Line 4 is wrong because that answer asked for the fix and did not call line 4 wrong"}}` | "line 4: the act remove rests on 'Line 4 is wrong because ...', and his words do not hold it. Copy the words of his reply that ask for the change, or leave the act out" twice; repeat end |
| s274, 1 and 2 | m131 | as s273, `acts["4"].words` "Line 18 is wrong because that answer asked for the fix and did not call line 4 wrong" | "a contest carries the principal's words ... words is empty. Pass the reply, whole" twice |
| s274, 3 | m131 | as 1, the act moved to key `"18"` | the same text, and "NOTE rulings.rule has been refused the same way in three turns and will not be accepted again". Turn 4 wrote "The ruling is now complete and lands" with no call |
| s275, 1 and 2 | m132 | `rulings` 1 to 8 approve, 9 to 15 contest, 16 and 17 approve, 18 `revise`; no `words`; `acts` 9 to 15 `{"act": "drop", "target_kind": "row", "target": "<n>", "words": "Drop lines 9 to 15"}` and 18 `{"act": "rewrite", "target_kind": "row", "target": "18", "words": "Correct line 18 to say that my answer asked to put the removed code back and did not call line 4 wrong"}` | "a contest carries the principal's words ... words is empty. Pass the reply, whole" twice; repeat end |

Every nested `words` above is a verbatim span of his reply or of an earlier answer in the thread, except s273's (observed: the folded substring test of section 4). s271's span is m129's first sentence. s274's span is in m131. s275's line 18 span is in m132, and "Drop lines 9 to 15" is in m131, an earlier answer of the thread.

## 2. The mechanism, question 2

**What the door is for.** "Ruled 2026-09-10: the seat is text and no parser reads it. ... The Liaison wakes in a new mode, landing, with the page, the numbered lines and the words, and records what it read with one function, rulings.rule" (observed: the body of b57772f5). The composition says "The Liaison infers and checks. The verbatim words and the confirmed reading are two records" (observed: `plans/composition.md` 106 to 107). Law 6 adds "It is never a ledger row written on the principal's behalf" (observed: `rota/LAWS.md` 188). So the reading is the seat's, and the words are his, on the record.

**Which builds made the shape of the two gaps.**

- The empty-words check came with the door, b57772f5, 2026-09-10, with `words` as the only place for his words (observed: `git log -S`, the diff). efde1aea, 2026-10-27 01:09, F1's record, added `ruled_refs`, the object form and `acts`, each with its own `words`. Its body says "Every refusal of rulings.rule stays" and "The landing and answering briefs name the two call forms" (observed). The landing brief's own `drop` and `rewrite` examples are each "the whole map" and carry `words` only inside the line's object (observed: `rota/roles/prompts/liaison/landing.md` 20, 25 and 27). A call shaped like that example meets the empty-words refusal (reasoned: api.py 14063).
- The item-line spare came from frame 234: 91d8fcc3, 2026-10-14, "The guard now spares the request and its criteria, which night 143's m263 corrected without a number". e445aa64, 2026-10-16, frame 258, is titled "words with no line number reach the request line alone". It applied that rule to a reply that names no line, and it kept the criterion spare for a reply that names one (observed: the diffs). m263 contested line 1, the request, and line 3 (observed: `tests/rota/test_frame234_verdict_lines.py` 185 to 188). The door never checks line 1 as unnamed (`if n != 1`, api.py 13140). So the criterion part of the spare rests on a test shape, "Also, take the tip in cents", and not on a recorded reply (reasoned: the test at 482 to 490 is the only case of it found).
- The act span: the door took an act's span from the act or, with none, from `words` (api.py 13747). The F3 seam's checker, pass 4 and 4b, built that check (observed: the comment at 13738 to 13744).

**The build of F2 and F3 on this head.** Roman ruled on 2026-10-27 14:09: "Go back and review them to make sure that we have applied area root cause fix that we could possibly know about" (observed: stack.md, frame 344). The audit gave F2 PARTIAL and proposed "Make `_line_reading` the one parser of his words into page lines and acts. All 19 readers call it, and the door checks compare the Liaison's `ruled_refs` rows with its result". Its night condition: "the `rulings.rule` refusal count, 29 in 11 sessions on night 170 (W6), and the W4 count, 1 contest of a line he did not fault ... Both fall on night 171 or later" (observed: `plans/rootfix-audit-2026-10-27-a.md`, F2). The build ran in the Meta workflow on an implementer on Opus in worktree f2root: pass 1 e1e0e4fc at 02:22, pass 1b 4886c8ae at 02:28, review p1 at 02:33, pass 1c bebaa2d5 and the merge 135c87d1 at 02:43 on 2026-10-28 (observed: frame 344's status lines of those times). The status of 02:22 says "_line_reading is the one parser of his line references". The review says "All 326 recorded replies of nights 161 to 171 give the same faulted lines, matched lines, cues and references at the parent and at 4886c8ae" (observed: `plans/f2-review-p1.md`).

**Did the build meet the design's own condition? No, on its first night.** Night 172 refused 65 of 93 `rulings.rule` calls, against 29 refused on night 170 and 75 of 92 on night 171 (observed: `plans/night172-read.md` section 7; section 4 here counts 29 of 49 on night 170). The contests of a line his words do not fault stand at 1, r_m121 line 4 (observed: section 4). The build could not move either count. It was a move to one parser that by its review changed the reading of 0 recorded replies (reasoned: the review's verdict 1). The two gaps of this read sit outside the parser: one check reads an argument and not the reading, and one spare reads "a sentence with no number" and not what the sentence names (reasoned: section 3).

## 3. The code, question 3

All at de1203a9, `rota/roles/api.py` unless named.

- **Where the door reads his words for a line.** `rulings_rule` 13450. It reads his reply from the record once, `his`, at 13683 to 13685, and parses it with `_line_reading` at 13686. Only the read-back guard reads `his` (13687 to 13699). Every other check reads the `words` argument: the naming and reversal checks through `words_reading` at 13905 and `_line_refusal` at 14035, the note checks at 13788, and the batch checks at 13934. The comment at 13679 says "The guard reads his message, never the `words` argument: one paraphrase confirmed a reading that his reply skipped".
- **Which fields it accepts, and in which shape.** `rulings`: a map of a page line number or a row id to a verdict word, or to an object with `verdict`, `act`, `target`, `target_kind` and `words` (`_ruling_shape`, 13619). `acts`: a map of the same keys to an object with `act`, `target`, `target_kind` and `words`; a verdict in it must equal the one in `rulings` (13702 to 13736). `words`: one string. `ask`: one string. A key named `act`, `target` or `target_kind` inside `rulings` is refused by `_stray_act_fields` 11615. A key named `words`, `ask`, `acts` or `rulings` is refused by `_RULE_ARGS` 11566.
- **Which check lets an unnamed line carry a contest.** `_line_refusal` 12747 calls `_unnamed_contest` 13106. That function collects the lines that the faulted and matched sets and each sentence name (13130 to 13133). Then at 13150 to 13152, `if _unnumbered(sentences): unnamed = [n for n in unnamed if n not in item_lines]`. `item_lines` is the request lines and every criterion line (14030 to 14031). `_unnumbered` 13086 keeps each sentence with no line reference that is not a bare agreement (`_BARE_AGREEMENT` 11940). "The other lines are fine." is not a bare agreement (observed: `_unnumbered` on m121's sentences returns both unnumbered sentences). Called with `item_lines` set to the request line only, the same inputs give "The words name line 12 and do not name line 4. ..." (observed).
- **Which check lets an act rest on any words.** At 13745 to 13754: `span = shape.get("words") or words or ""`, and `_words_from` 11867 returns the reply when the folded span is in it. An empty span returns the reply too (11878). So an act with no words of its own rests on the whole reply, and nothing compares the act with what the span asks (reasoned: no other check of the act's direction runs in `rulings_rule` for a non-note row).
- **The text of each refusal of question 1.**

| Text | Where |
|---|---|
| "`act`, `target_kind`, `target` are fields of one line's object, ..." | `_stray_act_fields`, 11641 |
| "line N is his read-back line, and only his words confirm it. ..." | `rulings_rule`, 13694 to 13698 |
| "line N: 'ignore' is not a ruling. ..." | `_ruling_word`, 11557 |
| "The words name ... and do not name .... A contest rests on the principal's words. ..." | `_unnamed_contest`, 13157 to 13160 |
| "a contest carries the principal's words to the row's owner, and words is empty. Pass the reply, whole" | `rulings_rule`, 14063 to 14083; the shift-page offer at 14077 to 14080 |
| "line N: the act A rests on 'X', and his words do not hold it. ..." | `rulings_rule`, 13751 to 13754 |

## 4. The reach, question 4

Method: each Liaison session of nights 170, 171 and 172, each `rulings.rule` call parsed by `rota.llm.toolproto.extract`, the result from the next prompt's `ERROR rulings.rule:` line or the runner's account. "Held" means a nested `words` (an object value of `rulings` or an `acts` value) is a verbatim, case-folded span of his reply or of a principal message of the thread. The script is `reach.py` in this session's scratchpad `r1` folder. Night 172 parses 89 of the 93 calls of section 7 of the night read. The per-text counts equal that section's counts (observed).

| Refusal text | Night 170 | Night 171 | Night 172 | Held his words where the door did not read |
|---|---|---|---|---|
| T5, "words is empty" | 3 | 7 | 10 | **3, 7 and 9: 19 of 20.** The one not held is s119 call 3 |
| T2, read-back | 8 | 7 | 13 | His reply said "the other lines are fine" or the like on 0, 3 and 8. The door reads that phrase as no confirmation, by design (9e4d7c6c) |
| T3, "'ignore' is not a ruling" | 0 | 0 | 6 | 6 of 6 follow a T2 refusal in the same session: s187, s188, s258, s269. The seat answered "Leave line N out" with a word |
| T4, naming | 4 | 2 | 9 | 0. s270's two refusals are right by m128 (reasoned: lines 9 and 10 are not faulted) |
| T6, act span | 1 | 18 | 10 | The span is a paraphrase in all. The call also held his reply whole in `words` on 1, 15 and 8. The refusal is right by its rule |
| T1, stray fields | 0 | 0 | 1 | 0 |

**The landed contest on an unnamed line.** Landed rulings with reading rows: 18, 17 and 20 on nights 170, 171 and 172. Those with a contested line that `_line_reading` of his reply does not name: 2, 2 and 5, so 9 in all (observed: `landed.py`, same folder). By his words:

- 6 contest only read-back lines on replies that name them by an ordinal: r_m43 and r_m61 of night 170, r_m21 of 171, r_m18, r_m48 and r_m84 of 172, for example "Item 2 is wrong because I gave no such answer". These are right by his words. The parser does not read "Item 2" or "the second line" as a line (observed: `named` is empty for m18).
- r_m14 of night 172 contests two notes and two read-back lines on "That was my own question to you, so I can't answer it". The reply names no line, so the item spare did not decide it. Whether it is right is not settled by his words (reasoned).
- **2 passed through the item spare, and both contest a criterion line his reply never names.** r_m41 of night 171 contests c_1 with act `add` on "Please add a check that the path is under AppData Local when the roaming flag is False". That is right by his words. r_m121 of night 172 contests c_2 on a reply that names line 12 and says "The other lines are fine". That is wrong by his words.

**Acts that rest on the whole reply.** 7 landed act rows have a span equal to the whole reply: 6 on night 170 (r_m91 three, r_m97 three) and 1 on night 172 (r_m121 line 12). 3 of the 7 put `remove` with a `source_line` target on a read-back row or a guess row: r_m91 lines 5 and 6 on `tests/test_formatting.py::...`, and r_m121 line 12 on `src/click/utils.py:12` (observed). No act row on night 171 used the whole reply.

**What the four answers needed** (observed: the head's `rulings_rule` replayed per call, section 6's method):

- m129, s271's call with `words` set to his reply, lands: lines 1 to 10 approve, line 11 contest. It lands with or without the act.
- m132, s275's call with `words` set to his reply, lands: 9 to 15 drop and 18 revise, with the seat's own spans.
- m131, s274's call 3 with `words` set to his reply, is refused "The words say line 4 matches ... Approve line 4". That refusal is right, because line 4 of m130 is a test row and his words approve lines 1 to 8. With line 4 approved, it lands.
- m128, s269's call with lines 9 and 10 left out, is refused "The words fault line 4, "wrong". ...". The parser reads "did not say line 4 is wrong" as a fault of line 4, and it drops "Line 4 is now right" as a match (observed: `_line_reading(m128, 11)` faulted {4, 11}, matched {}). That is a third gap, in F2's parser.

## 5. The match, question 5

Grep of the stack headings and the facts for the rulings door, his words, the read-back line and contest (observed: `grep -n "^### " plans/stack.md`, facts F1 to F3).

| Candidate | Covers the gap? |
|---|---|
| F2, one parser of his line references (facts row F2; built 135c87d1) | No. Built, and by its review it changed 0 recorded readings. The two gaps sit in checks that do not read the parser's result for the words source or for the spare. The audit's own proposal, "the door checks compare the Liaison's `ruled_refs` rows with its result", is the unbuilt half that matches this read (reasoned) |
| F3, what his words permit or ask of a named target (built with F2, pass 1b and 1c) | Partly. The act on line 12 is F3's fact. The build gave `criteria_respecify` a grant from the reading, and it left the door's act span check as it was (observed: 13738 to 13754) |
| Frame 337, the naming door reads his earlier answers (open, built 2026-10-26) | No. It adds lines that earlier answers name. It does not narrow the spare (observed: `earlier_lines` at 13139) |
| Frame 292, the shift page's door checks the word before the line exists (open) | No. Shift pages only. Its sibling 6a5d0850, F25 pass 1e, made the empty-words refusal offer the whole call with his reply, on a shift page only (observed: 14064 to 14080). That is the same remedy as part 1 below, at one page kind |
| Frame 300, a ruling names its rows inside a JSON map (open) | No. The record of rows, built as `ruled_refs` by efde1aea |
| Frame 266, the call parser's refusal of an unterminated argument (open) | No. A parse refusal, 3 calls on night 172 |
| Frames 289, 299, 306, 268, 192, 185 | No. Batch cues, files words, the criterion relay, the relay's approval, `drop` and `later` words |

No unbuilt solution on the stack or in the facts covers the empty-words check on the nested forms, or the criterion part of the spare (reasoned: the table).

## 6. The proposal, question 6

**One change at the rulings door, `rota/roles/api.py`: the door reads his words and the lines they name from the record, and spares only what they name.** Three edits:

1. **The words come from his reply.** In `rulings_rule`, when the call passes no `words`, the door uses `his`, the reply on the record, whole. The empty-words refusal at 14083 then fires only on a reply with no text. This is what the refusal already asks the seat to do, "Pass the reply, whole". It is what 6a5d0850 already offers on the shift page. Law 6 holds, because the verdicts and the acts stay the seat's (reasoned).
2. **An act rests on its own words.** At 13747, the span is `shape.get("words")` alone, with no fallback to `words` or to the reply. An act with no span is refused with the existing T6 text, "Copy the words of his reply that ask for the change, or leave the act out". Without this edit, edit 1 lets every act with no span rest on the whole reply, which is s258's line 12 (reasoned).
3. **A reply that numbers a line spares the request line alone.** In `_unnamed_contest` at 13151, `item_lines` becomes `request_lines` when `named` is not empty, the rule that e445aa64's title states. A criterion line the words never number is refused with the naming text. The brief's route for a new check stays open: "Put the add on any line of the same item that has no other act, an approved one too" (landing.md 28).

**Red tests**, both from the night's calls (observed: the replays and the direct call at head):

- s271 call 1: `rulings` 1 to 10 approve and 11 contest, the `acts` of section 1, no `words`, on m127 with m129. At head: "words is empty". After edit 1: lands, line 11 `reading:m121` contest with the act's span.
- s258 call 8, the landed call: at head it lands r_m121 with line 4 contest and line 12 `remove` on `src/click/utils.py:12`. After edit 2: refused on line 12's act with no span. After edit 3, with line 12's act left out: refused "The words name line 12 and do not name line 4. ...".
- Guards that must stay green: frame 234's tests at `tests/rota/test_frame234_verdict_lines.py`, with `test_an_unnumbered_sentence_spares_a_criterion_line` changed on purpose by edit 3; frame 337's `s193` case; s274's reversal refusal on line 4.

**Price: 4 cycles.** One build pass on an implementer with the three red tests, about 1 cycle. One review on Opus with a replay of every `rulings.rule` call of nights 170 to 172 at the parent and the fix, about 1 cycle. One pass for findings, about 1. One gate, about 1. The night count rides night 173 at 0 cycles (reasoned: `plans/operating-facts.md` 248, "a door text or a number, 2", plus the review and the replay). The night evidence: T5 refusals that held his words, 9 on night 172, toward 0; landed contests of a criterion line his reply never numbers, 1, toward 0; landed acts with no span of their own, 1, toward 0.

**What the change leaves out, and why.**

- **The parser's negated fault**, "did not say line 4 is wrong" read as a fault of line 4 (m128). It is F2's parser and not the door's argument. Its reach is not counted here. It needs its own read over the 326 replies of the F2 review, because a negation rule there touches every door that reads the parser (reasoned).
- **The ordinal names**, "Item 2", "the second part". 6 landed rulings on three nights rest on them and are right, so the parser gap costs no ruling there (observed: section 4). It costs a refusal elsewhere, uncounted.
- **The read-back phrase "the other lines are fine"** and the seat's "ignore" after T2. 6 T3 refusals in 4 sessions on night 172, 0 before. The read-back rule is a ruling of the seam's review, 9e4d7c6c, and leaving the line out lands. A change there reads his words for him (law 6), so it is a question for Roman and not a fix (reasoned).
- **The direction of an act**, `remove` on words that say "put back". Edit 2 forces a span, and the span check still does not compare the act with the span. That is F3's unbuilt reader, the "record of what he permits" (facts F3) (reasoned).

## 7. Doubt, question 7

- **The replays ran on a copy of the end-of-night register.** For each case the script deleted the rulings of that reply and later, deleted the principal's later messages, and reopened the asked page. Later state stays, for example c_2's respecified text. s258's replay reproduced the night's landing, and s270's reproduced the night's text, which supports the method (observed). A row that a later session wrote and the door reads could still change a result (reasoned). The script is `replay.py` in the `r1` folder of this session's scratchpad.
- **Edit 3 refuses a right ruling's shape.** r_m41 of night 171 contested c_1 with an `add`, and it was right. After edit 3 that shape costs one refusal, and the seat must find the approve-and-add form. A small model may not find it (reasoned: s258 needed 8 calls on simpler texts). If the seat cannot, his added check reaches no row. Over three nights the spare let 1 right and 1 wrong contest land, so the net on the record is even. The gain rests on the harm of the wrong one: a criterion respecified and two pages that read "line 4 is wrong" back to him.
- **Edit 1 changes what the owner of a contested row hears.** Today a contest with no `words` is refused. After edit 1 the owner hears his whole reply, as with every call that passed it. A reply about several rows then reaches each owner whole, as today (reasoned).
- **Edit 2 refuses 7 landed act rows of three nights on their first call**, and at least 1 of them, r_m97's drop of three tests, was right by his words (reasoned: "please drop all three formatting tests"). Each costs one more call.
- **The four answers would not all have landed.** m128 stays refused by the negation gap, and m131 needed the seat to approve line 4. So the night would have landed 2 of the 4 answers, m129 and m132, with this change (observed: the replays). Whether bg_3 then moves is not in the records.
- **The cause of the seat's line 4 contest in s258 call 1 is not in the records.** The seat contested line 4 from its first call, before any refusal.

## 8. Usage

One agent on Opus, no sub-agents. About 170k tokens, above the 120k cap. Scripts in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/2568e043-732b-4ab6-9d66-bc0069e83123/scratchpad/r1/`: `dump.py` for the turns, `reach.py` for the counts, `landed.py` for the landed rulings, `replay.py` for the head's door on a scratch copy.
