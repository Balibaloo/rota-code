# Night 173's rulings seam, W1, W9 and W16, the read by rule C76

Meta workflow, read on 2026-10-28. The code at head is `rota/foundation` at 189dc7b2. Its `rota/roles/api.py` is the same as at 36d2a667, the code of night 173, and as at 2b1ef4c9 (observed: `git diff --stat 36d2a667 189dc7b2 -- rota/` shows `principal.py` only, and `git diff 36d2a667 2b1ef4c9 -- rota/` is empty). Line numbers below are at 189dc7b2. Sources: `plans/night173-read.md` sections 2, 3 and 5; `.rota/clickI_night173.db` and its principal jsonl; `plans/f2-night172-read.md`; `plans/f1-f15-f21-night172-read.md` section 2; `plans/facts-2026-10-27.md` F2 and F3; `plans/p7-review-p1.md`; `plans/f2-review-p2f.md`; `plans/rulings-seam-design-2026-10-26.md` 2.2; `rota/roles/prompts/liaison/landing.md`; frame 344's status lines of 2026-10-28; the code. One agent on Opus, no sub-agents. No code was edited and nothing was committed.

**The result. The door was right by its own rules on all 15 parsed refusals, and 8 of them were one removal away from a landed ruling. The two lands of W9 and W16 come from two readers that do not exist.**

1. **W1: each refusal named its own fix, and the seats did not apply it.** A call that leaves line 23 out lands m91. A call that leaves the paraphrased acts out lands m92 (observed: the replay at 2b1ef4c9 and at 0ae7ab54). s234 sent that form with line 23 as `approve` or `ignore` five times. s235 sent the same call four times with acts on "Remove line N" (observed). Line 24, the read-back of an empty answer, takes its contest in every form and causes no refusal (observed).
2. **W9: the fault reader reads a number in his report of an earlier answer as a line of this page.** `_line_reading` faults lines 1 and 4 on "I approved two lines, lines 1 and 4, not one", with the cue "not". The faulted-approve door then told s120 to contest or revise line 4, and the seat revised c_3 (observed).
3. **W16: no check reads the act's verb against its span.** The act check proves only that the span is his words (api.py 13774 to 13786). `granted` then reads the act as his permission. On the night's register, `granted(bg_2, "remove", "src/click/termui.py:clear")` is True (observed).

**The proposal.** Three edits in `rulings_rule`, about 5 cycles as one pass after w7root lands. W1: the door leaves out the part that its own refusal tells the seat to leave out, and lands the rest. W9: a line number after his report verb, in a sentence about a read-back line, names the earlier page. W16: a `remove` or `drop` on a code target lands only when its span asks for a removal (section 6).

## 1. The find, question 1

### m91 and m92 on m90

**The page he saw** (observed: the jsonl `call` rows of m90 at 09:47:57 and 09:48:46). Lines 1 to 8 are the request, the guess `src/click/utils.py` and the criteria c_1 to c_6. Lines 9 and 10 are glossary rows of `option`. Lines 11 to 22 are "Users of click.X in their command-line interfaces" constraint rows. Line 23: `Your answer "Line 4 is wrong because it leaves out ...", as the team read it: 3 lines approved.` Line 24: `Your answer "", as the team read it: 2 lines approved.` Line 24 reads back r_m87, his clarify answer m87, which has no `body_text` (observed: `messages`, `entries`). The second send opens with "Your last answer to this page did not reach the team."

**His words** (observed: `messages.body_text`):

- m91: "Line 24 is wrong because I never sent an empty answer, so nothing was approved there. Lines 11 to 22 are wrong because they name users of other parts of the library, and only the format_filename docstring changes. The other lines are fine, and the code stays the same."
- m92: "Lines 1 to 10 and line 12 are fine, so keep them. Remove lines 11 and 13 to 22, because they name users of other parts of the library and only this one docstring changes. Line 23 is read right, so keep it, but remove line 24, because I never sent an empty answer."

**The calls** (observed: `turns.completion` parsed by `rota.llm.toolproto.extract`). The `rulings` map is given as ranges of the same verdict. "m91 whole" means `words` equal to the reply. Each refusal text is quoted in full once, below the table.

| Session, call | `rulings` | `words` | `acts` | Refusal |
|---|---|---|---|---|
| s233, 1 | 1-8 approve, 9-11 contest, 12 approve, 13-22 contest, **23 approve**, 24 contest | m91 whole | none | RB, line 23 |
| s233, 2 | 1-8 approve, 9-11 contest, 12 approve, 13-24 contest | m91 whole | none | NM, "do not name lines 9, 10 and 23" |
| s233, 3 | as 2 | m91 whole | none | NM, as 2 |
| s233, 4 | as 1 | m91 whole | none | RB, line 23 |
| s233, 5 | as 2 | m91 whole | none | NM, as 2 |
| s234, 1 | 11-24 contest only | m91 whole | none | "lines 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 have no ruling. ..." |
| s234, 2 | 1-10 approve, 11-24 contest | m91 whole | none | NM, "do not name line 23" |
| s234, 3 | 1-10 approve, 11-22 contest, **23 approve**, 24 contest | m91 whole | none | RB, line 23 |
| s234, 4 | as 3, **23 `ignore`** | m91 whole | none | IG, line 23 |
| s234, 5 | as 3 | m91 whole | none | RB, line 23 |
| s234, 6 | as 4 | m91 whole | none | IG, line 23 |
| s234, 7 | as 4 | m91 whole | none | IG, line 23 |
| s235, 1 | 1-10, 12 and 23 approve; 11, 13-22 and 24 contest | none | for 11 and 13 to 22: `{"verdict": "contest", "act": "remove", "target_kind": "row", "words": "Remove line 11"}`, each with its own number | AS, line 11, "Remove line 11" |
| s235, 2 | as 1, with `"19": {","verdict"` in the text | | | the parse door, "unterminated argument list ..." |
| s235, 3 | as 1 | none | as 1 | AS, as 1 |
| s235, 4 | as 1 | none | as 1 | AS, as 1 |

The brief's split, 4, 4, 3, 3 and 1, counts 15 calls. The sixteenth is s234 call 1, the "have no ruling" text (observed). Each session then met "rulings.rule has been refused the same way in three turns and will not be accepted again" (observed: `plans/night173-read.md` section 3).

The four texts, verbatim (observed: the next prompts' `ERROR rulings.rule:` lines and the runner's accounts):

- RB: "line 23 is his read-back line, and only his words confirm it. His reply does not say that line 23 is right, and it does not approve the whole page. Leave line 23 out of the ruling"
- NM: "The words name lines 11 to 22 and 24 and do not name lines 9, 10 and 23. A contest rests on the principal's words. Approve the lines the words do not name, or rule them as the words say."
- IG: "line 23: 'ignore' is not a ruling. Each line takes approve, contest or revise. drop, remove and strike are contest. resume takes up a request you put aside. ask, unclear and question are a question: rulings.rule(ask=...) with no rulings."
- AS: "line 11: the act remove rests on 'Remove line 11', and his words do not hold it. Copy the words of his reply that ask for the change, or leave the act out"

**Which calls were right on every other line, by his words** (reasoned: each call read line by line against m91 and m92):

- s233: no call. Each call contests lines 9 and 10, which m91 calls fine, and approves line 12, which m91 calls wrong.
- s234 calls 3 to 7: yes. Lines 1 to 10 approve, and 11 to 22 and 24 contest, is m91. Only line 23 has the wrong form.
- s235 calls 1, 3 and 4: yes on every verdict. The acts carry a paraphrase.

### m35, s120 and r_m35

**The page m34** (observed: the jsonl): line 1 the request `get_app_dir_windows`, lines 2 to 5 the criteria c_1 to c_4, line 6 bg_1, line 7 `Your answer "Line 2 is wrong because this function lives ...", as the team read it: line 2 is wrong; line 3 is wrong; 1 line approved.`, line 8 `Your answer "", as the team read it: 5 lines approved.` Line 7 reads back m25, his answer to the page m24.

**His words, m35:** "Lines 2 and 3 are wrong: with the roaming flag on, only the roaming app data variable being unset should matter, and with it off, only the local app data variable being unset should matter. Line 7 is slightly off, because I approved two lines, lines 1 and 4, not one. Line 8 is a misread, since I never sent an empty answer, so please drop it; the rest of the page is fine." His "lines 1 and 4" are lines of m24, the page he answered with m25 (reasoned: line 7 says "1 line approved" of m25).

| Call | `rulings`, all with `words` m35 whole | Result |
|---|---|---|
| 1 | 1 approve, 2 and 3 contest, 4 approve, 7 contest, 8 drop | "lines 5, 6 have no ruling. ..." |
| 2 | as 1, with 5 and 6 approve | 'The words fault line 4, "not". An approve keeps the line as it is, and his words reach nobody. Rule line 4 contest or revise, as the words say, and pass the words. It takes no approve.' |
| 3 | as 2, with **4 revise** | landed r_m35 |

**The landed row** (observed: `ruled_refs`): c_3, line 4, `revise`, `words_from` m35, source `reading` and `landed`. His words fault no part of c_3 (reasoned). s122 wrote "The principal's verdict 'revise' for c_3 was a misread" and was refused three times on c_3 (observed: `plans/night173-read.md` W9).

### m62, s179 and r_m62

**The page m61, line 5** (observed: the jsonl): "the work for: Make clear() return True when it cleared the screen and False when stdout is not a terminal.; expected to touch nothing named; might touch src/click/termui.py::clear".

**His words, m62:** "Lines 1 to 4 are fine. Line 5 is wrong: the change has to touch the clear function in the terminal UI file, so that function should be named as expected, not as nothing named. Line 6 read me right, so ok to that."

**The call**, one, landed: lines 1 to 4 and 6 approve; line 5 `{"verdict": "contest", "act": "remove", "target_kind": "source_line", "target": "src/click/termui.py:clear", "words": "the change has to touch the clear function in the terminal UI file, so that function should be named as expected, not as nothing named"}` (observed: s179 turn 1).

**The landed row** (observed: `ruled_refs`): bg_2, line 5, `contest`, act `remove`, `source_line`, `src/click/termui.py:clear`, `words_from` m62. m65 read it back as "line 5 is wrong: remove src/click/termui.py:clear", and m66 answered "nothing about the clear function belongs in this change" (observed: `reading_line`, `messages`). His words ask to name the function as expected. They ask for no removal (reasoned).

## 2. The mechanism, question 2

All in `rota/roles/api.py` at 189dc7b2.

| Text or land | The check | What it reads | The build, its date | Its own condition |
|---|---|---|---|---|
| RB | `rulings_rule` 13710 to 13728. A `reading:` line ruled `approve` passes only when it is in `his_reading.matched`, or when his reply names no line and every verdict is approve (`whole`, 13720) | `_line_reading(his)` of his recorded reply, never the `words` argument (13714) | f920fd39 and 9e4d7c6c, 2026-10-27 02:44 and 02:51, the fixes for findings 2 and 5 of the seam's review of pass 5 | The design measures "read-back lines contested against lines shown, and rows unconfirmed at the night's end" (observed: design line 240). A bound on refusals is not in the records |
| IG | `_ruling_word` 11532, its last raise at 11556 to 11560 | the value of one key | 6950314b, 2026-10-10, frame 193 pass 1 | Not read |
| NM | `_unnamed_contest` 13113 to 13182, text at 13177 to 13180, through `_line_refusal` 12752 from `rulings_rule` 14071 | the sentences of `his`, and the contested lines | 250f3806, 2026-10-14, frame 234; the criterion spare narrowed by f53ff5b0, 2026-10-28 06:27, F2 pass 2 | F2 pass 2's count, "a landed contest of a line his reply never numbers, 1, toward 0", is met on night 173 (observed: `plans/night173-read.md` section 5) |
| AS | `rulings_rule` 13774 to 13786. An act needs `shape["words"]`, and `_words_from` 11867 must find the span in his reply or in an earlier answer of the thread | the act's own span only, since f53ff5b0 | 76f2f981, 2026-10-27 03:09, the seam design's checker, step 1; f53ff5b0 removed the fallback to the reply | F2 pass 2's count, "landed acts with no span of their own, 1, toward 0", is met (observed: r_m62's act has its own span). The design gate is "0 new false refusals". The 7 refusals of night 173 are right by the span rule (reasoned) |
| W9, the land of r_m35 | `_faulted_approve` 13020 to 13066, through `_line_refusal` 12807. It refuses an approve of a line in `cues`. Line 1 is spared as the request (`request_first`, 13056) | `words_reading = _line_reading(his, 8)` at 13941. Its cues give line 1 and line 4 the cue "not" from ", not one." (observed: `_line_cues(m35, 8)`) | f0b2924c, 2026-10-16. Its body: "Over nights 143 to 149 it fires on 5 of 177 verdicts, 4 wrong approves and 1 right one" | The build accepted 1 wrong fire in 5. Its frame, 250, is parked. A count of wrong fires since then is not in the records |
| W16, the land of r_m62 | the AS check above. It reads no verb | the span's presence in his reply | 76f2f981. The design's checker has steps for the span, the target and the verdict, and no step for the act (observed: design 2.2, lines 66 to 73) | Not applicable. No build claimed this check. F3 has no one reader (observed: facts F3). `plans/f2-night172-read.md` section 6 lists "the direction of an act" as left out |

**The parser in W9** (observed: `_line_reading` at 0ae7ab54 and at 2b1ef4c9). "Line 7 is slightly off, because I approved two lines, lines 1 and 4, not one." gives `named` {1, 4, 7} and `faulted` {1, 4, 7}. "I approved two lines, lines 1 and 4, not one." alone gives `faulted` {1, 4}. The parser has a rule for a second reference that is an object, `_RELATING` at api.py 12185, "Line 7 repeats line 3". It has no rule for a reference inside his report of an earlier answer (reasoned).

**The read-back rule and the brief** (observed: `landing.md` 52 to 82). The brief says "Every line gets a ruling, except the read-back line" and "Otherwise leave it out". Its last paragraph says "Call `rulings.rule` once, with `rulings` for every line and the whole reply as `words`". All 15 parsed calls rule line 23 (observed). After an RB refusal, the IG text says "Each line takes approve, contest or revise", and s234 went back to `approve` (observed: calls 4 to 7). So two refusal texts send the seat between two refused forms (reasoned).

## 3. The read-back line after P7, question 3

**P7 changes the page, not the door, on these calls.** `reading_line("reading:m87")` gives `Your answer "", as the team read it: 2 lines approved.` at 2b1ef4c9. At 0ae7ab54 it gives `Your answer "Yes, I mean the shorten option the function ...", as the team read it: 2 lines approved.` (observed: `rl173.py`). r_m87 approved `format_filename` and `s3` on his "Yes, I mean the shorten option ...". So the line is right, and his reply would likely not contest it (reasoned). Whether he would contest it is not in the records.

**The replay** (observed: `replay.py` on a scratch copy of the register, each call at the state of its trigger). For night 173 the script also puts back each batch's status and head commit and each item's `delivered:` key to their state at the session. At 2b1ef4c9, the 50 parsed `rulings.rule` calls of night 173 give the night's result on 50 of 50. At 0ae7ab54 they give the same land or refusal on 50 of 50. One text changes: s91 call 1 moves from RB to "line 21 words must be his own words ...". At the w7root tip, 3b31077a, after P7 pass 1c, the 15 calls on m91 and m92 give the same 15 refusals. There, s165 call 3, r_m52, moves from a land to an AS refusal (observed: `tip.json`).

| Calls | At 2b1ef4c9 | At 0ae7ab54 | At 3b31077a |
|---|---|---|---|
| s233 1 to 5 | RB, NM, NM, RB, NM | the same | the same |
| s234 1 to 7 | no ruling, NM, RB, IG, RB, IG, IG | the same | the same |
| s235 1, 3, 4 | AS, AS, AS | the same | the same |
| s120 1 to 3 | no ruling, the fault of line 4, lands r_m35 | the same | the same |
| s179 1 | lands r_m62 | the same | the same |

**The forms that land** (observed: `hypo.py` at 2b1ef4c9, 0ae7ab54 and 3b31077a, each the same):

- m91: lines 1 to 10 approve, 11 to 22 and 24 contest, line 23 left out. It lands with `words` and without. The same call with line 23 `approve` is refused RB.
- m92: s235's verdicts with no acts land. With his sentence "Remove lines 11 and 13 to 22, because ..." as each act's span, it lands with `remove` and with `drop`.
- m91 with its line 24 sentence taken out, as a P7 page could leave it (reasoned): the seat's form with lines 23 and 24 `approve` is refused RB on line 23. With 23 and 24 left out, it lands (observed: `hypo2.py` at 0ae7ab54).

So the line of sprint 33 row 1, "He contested the read-back of an empty answer in every call, which P7 lands", does not hold. The contest of line 24 met no refusal, and no refusal text names line 24 (observed). P7 lands none of the 16 calls (observed).

## 4. The reach, question 4

### The four texts, nights 170 to 173

Method: each `rulings.rule` call of each Liaison session, its recorded result, then a replay at 2b1ef4c9 (`fixreach.py`). "Same" means the replay gives the recorded text. "Lands on its own fix" means: apply the fix that the refusal names, repeat while the refusal keeps the same text, and the call lands. The fixes are: RB, leave the line out; IG, leave the key out; AS, leave the act out; NM, approve the unnamed lines. A call that lands on its own fix carried every other line in a form the door accepts. On night 173 such a call is also right by his words (reasoned: section 1).

| Text | Night 170 | Night 171 | Night 172 | Night 173 | Total: refused, same, lands on its own fix |
|---|---|---|---|---|---|
| RB, read-back | 8, 8, 5 | 7, 3, 1 | 13, 13, 4 | 7, 7, 3 | 35, 31, 13 |
| NM, naming | 4, 1, 1 | 2, 1, 1 | 9, 9, 0 | 4, 4, 0 | 19, 15, 2 |
| IG, "is not a ruling" | 0 | 0 | 6, 6, 0 | 3, 3, 3 | 9, 9, 3 |
| AS, act span | 1, 1, 0 | 18, 12, 2 | 10, 10, 3 | 7, 7, 5 | 36, 30, 10 |

The refused counts equal `plans/f2-night172-read.md` section 4 for nights 170 to 172 and `plans/night173-read.md` section 5 for night 173 (observed). With every fix of the four texts applied in turn, 18 RB, 10 NM, 5 IG and 13 AS calls land (observed). On night 173 the calls that land on their own fix are s234 calls 3 to 7, s235 calls 1, 3 and 4, s91 call 4, and s188 calls 1 and 2 (observed). The 4 NM refusals of night 173 are right by his words (reasoned: section 1).

### W9, a line number from words about another page

Method: each principal reply of nights 170 to 173 with a recorded page order (`w9expo.py`, `w9reach.py`). A sentence counts when its first line reference is a read-back line of the page and it names another line.

- 25 such sentences on 4 nights. In 10 of them, on 8 replies, the other number belongs to his earlier page, and `_line_reading` faults it on this page: 170 m17 (line 18), 171 m17 (the same reply, replayed), 171 m41 ("the old line 4"), 171 m62 and m63 ("I also said line 8 was wrong"), 172 m12 ("lines 13 to 20 don't belong on that page"), 172 m128 ("did not say line 4 is wrong"), 173 m12 (replayed), 173 m18 ("I never said that line 3 or line 4 is wrong"), 173 m35 (lines 1 and 4) (observed: the probe; reasoned: the page each number is about).
- Each of the 10 puts the number after a first-person report of his earlier answer: "I said", "I approved", "I asked", "I meant", "I never said", "my last answer ... did not say" (observed).
- **Landed rulings whose line came from such words: 1, r_m35** (observed: `w9reach.py`). The two other hits, r_m7 of nights 170 and 171, contest line 1 on "line 1 and the rest of the word notes are fine", and that line 1 is this page's line (reasoned).
- Refusals from such a fault: 1, s120 call 2 (observed). The other replies met other doors.

### W16, a landed act whose verb his words do not hold

Method: every landed `ruled_refs` row with an act and source `reading` (`w16probe.py`). The removal door's request reader, `_removal_spans` api.py 23336, reads each span.

- Landed acts `remove` or `drop`: 35. On a code target, `source_line`, `path`, `identifier` or `sentence`: 10. Their spans hold a removal request in 2, r_m75 and r_m97 of night 170, both right by his words (observed).
- **The other 8 grant a removal of code that his words do not ask for** (reasoned: each span read): the three r_m91 rows of night 170, "no new test is needed", on three project tests; r_m7 of nights 172 and 173, `keepopenfile:7`, on a fault of a glossary row; r_m121 of night 172, "put back"; r_m52 of night 173, `src/click/utils.py::make_str`, on "not the string helper"; r_m62 of night 173. Three reverse his words: r_m121, r_m52 and r_m62.
- `granted` reads each such row as his permission, and its 7 callers are the removal readers (observed: `rota.tools.map fn granted`). On night 173, `granted` is True for bg_2 on `src/click/termui.py:clear` and for `guess:clear_returns_status` on `make_str` (observed). No commit of night 173 removed code, so the grants did no harm that night (observed: `plans/night173-read.md` section 5).
- On a `row` target, 15 of 25 `remove` or `drop` spans hold no removal request. Most fault the row, and a read-back row takes `remove` as "drop the misreading" (reasoned). Section 6 leaves them out.

## 5. The match, question 5

| Candidate | W1 | W9 | W16 |
|---|---|---|---|
| w7root at 0ae7ab54: F2 2f and 2g with P7 1 and 1b | No. It changes 0 of the 16 results (observed: section 3) | No. r_m35 lands the same | No. r_m62 lands the same |
| w7root tip 3b31077a: P7 1c and the lead-word fix | No. The whole-clause act rule refuses more act spans: s165's r_m52 is now refused (observed) | No | Partly, by chance. r_m52 is refused for a cut clause, not for its verb. r_m62 still lands (observed) |
| Frame 337, earlier answers name lines | No. It adds lines and reads no read-back rule (observed: `_earlier_sources`) | No. It reads earlier answers for numbers of this page, the opposite case | No |
| Frame 306, his words reach the criterion | No | No | No |
| Frame 289, the batch filter's fault cues | No | No. Its cues are files cues | No |
| Frame 292, the shift page's door | No. Its sibling 6a5d0850 offers the whole call on a shift page, the F25 offer pattern | No | No |
| Frame 339, the removal door's phrase readers | No | No | Partly. Its reach is the reading side, the 11 phrase readers of F3. The write side, the act check, is outside its reach (observed: facts F3) |
| The F2 debts on frame 344's status lines of 2026-10-28 | The words debt, built as 2f and 2g; "the nested thread match, the three readers, the pin's six shapes" (observed: the status of 09:47 and the review of 10:12). None is a W1 text | The parser's negated fault, m128, listed as left out in `plans/f2-night172-read.md` section 6. 172 m128 is one of W9's 10 sentences | "The direction of an act", listed as left out there and in facts F3 |

No built branch and no open frame covers any of the three gaps (reasoned: the table).

## 6. The proposal, question 6

All three edits sit in `rulings_rule`, `rota/roles/api.py`. w7root edits the same function, so the pass branches from w7root after it lands (observed: `git log w7root`).

### W1: the door leaves out what its refusal would tell the seat to leave out

- **The change.** A `reading:` line ruled `approve` that the RB check refuses leaves the map. A `reading:` line ruled with a word that is not a verdict leaves the map. An act whose span his words do not hold leaves its line, and the line keeps its verdict. The ruling lands, and its result names each part it left out. The door adds no verdict, so nothing is ruled for him (reasoned: law 6). A left-out read-back line stays unconfirmed and shows on his next page, by the ruling of 2026-10-26 22:5x. One sentence of `landing.md` changes to "with `rulings` for every line except the read-back line".
- **The reach.** On night 173, 8 of 15 parsed calls land. m91 lands on s234 call 3 and m92 on s235 call 1, the first such call of each (observed: the reduced calls of section 3 land). Over nights 170 to 173, 26 calls land on their own fix: RB 13, IG 3 and AS 10 (observed: section 4).
- **Red tests.** m90 with m91, s234 call 3: lands, with line 23 named as left out. s234 call 4: the same. m90 with m92, s235 call 1: lands with 12 contests, and the 11 acts named as left out. Guard: m91 with line 23 `contest` stays refused by NM.
- **The price.** 4 cycles alone: one build pass, one review with the replay of the 290 calls of nights 170 to 173, one pass for findings, one gate. The brief sentence puts the landing cassettes on the re-record list.
- **What it leaves out.** NM. Its 4 refusals on night 173 are right, and an approve for the seat would rule for him.

**Ask before the build** (reasoned: the composition says "The Liaison infers and checks"). The door now drops a part of the seat's reading in place of a refusal. Recommended: build it, because the door only removes, and the seats did not reach a land in three turns on these texts. The alternative is the F25 offer: the refusal shows the reduced call, and the seat sends it. s235 sent one call four times unchanged, so an offer may not move it (observed).

**An open question for Roman, not a fix.** m91 says "The other lines are fine" after it names lines 11 to 22 and 24. The door does not read that as a confirmation of line 23. The rule is the seam review's, 9e4d7c6c, not his ruling. Recommended answer: keep the rule, because the read-back line exists to catch a misreading, and the cost is one line on his next page.

### W9: a number in his report of an earlier answer names the earlier page

- **The change.** One helper beside the two reads of `_line_reading(his, ...)` at 13714 and 13941. In a sentence whose first line reference is a read-back line of the page, a reference after a first-person report verb leaves `faulted`, `named` and the cues. The verbs are "I said", "I approved", "I asked", "I meant", "I never said" and "my answer ... said". The helper needs the page order, so it sits in the door and not in `_line_reading`.
- **The reach.** 10 sentences on 8 replies over 4 nights, 1 landed revise and 1 refusal (observed: section 4).
- **Red test.** m34 with m35, s120 call 2: lands with c_3 `approve` (observed: the replay with the numbers taken out of his words lands). Guards: "Line 7 is wrong, and line 4 is wrong too." keeps the fault of line 4. m92's "Line 23 is read right, so keep it, but remove line 24" keeps line 24.
- **The price.** 3 cycles alone: build, review with the 25 sentences as cases, gate.
- **What it leaves out.** A `revise` of a criterion line his words do not name still lands: s120 call 3 lands with his numbers taken out (observed). The naming check counts a `revise` only on a team note (api.py 14043 to 14045). The reach is 1 row in 4 nights, r_m35, and this edit removes the refusal that led to it (observed). The ordinal names and the negated fault of m128 stay with F2's parser.

### W16: a removal of code lands only on words that ask for it

- **The change.** In the act loop at 13774, an act `remove` or `drop` with a code target kind, `source_line`, `path`, `identifier` or `sentence`, lands only when `_removal_spans(span)` gives a request. The refusal names the act and quotes the span: "his words do not ask to take X away. Leave the act out, or copy his words that ask for it". The write then reads his removal ask by the same rule as the removal door.
- **The reach.** 8 of 10 landed code removals on nights 170 to 173 are refused, and the 2 right ones still land (observed: section 4). r_m62, r_m52 and r_m121 are among the 8.
- **Red test.** m61 with m62, s179's call: refused on line 5's act. With the act left out, the contest of bg_2 lands. Guards: r_m75 and r_m97 of night 170 land.
- **The price.** 3 cycles alone: build, review with the 35 landed acts as cases, gate.
- **What it leaves out.** The 15 `row` removals with no removal request, because a row removal grants no code, and a read-back row takes `remove` as its drop (reasoned). The target check of the design's step 2: `src/click/termui.py:clear` is not in the `function:line` form, and no check refused it (observed). Frame 339's reading side.

### The three as one pass

About 5 cycles: one implementer pass for the three edits and the brief sentence, one review with the replay of nights 170 to 173, one findings pass, and one gate with the landing re-records (reasoned: `plans/operating-facts.md` 248 and the prices above). The counts for night 174: RB, IG and AS refusals whose call lands on its own fix, 11 on night 173, toward 0; landed rows from an earlier page's number, 1, toward 0; landed code removals with no removal request, 2 on night 173, toward 0.

## 7. Doubt, question 7

- **The replay state.** For night 173 the script put back each batch's status and head commit and each item's `delivered:` key, from the commit and verdict seqs of the night read. With that repair, all 50 calls give the night's result (observed). Nights 170 to 172 had no repair, and their replays ran on night 173's door, so 71 of their 240 calls do not give the recorded result (observed). The counts of those nights that land on their own fix read night 173's door.
- **"Lands" is the door's word, not his.** The fix script applies the refusal's own instruction mechanically. I checked the night 173 lands against his words by hand. I did not check nights 170 to 172 line by line.
- **W1 removes a seat's act with no refusal.** A span that misquotes a real permission then lands no grant, and a later Developer meets the removal door. That is the safe direction, but it costs a later question to him. Frame 305's tests of act spans may change on purpose.
- **W9's verb list is a phrase reader.** It reads 10 of 10 cases of 4 nights. A sentence such as "As I said, line 3 is wrong" after a read-back line would lose a real fault. No such sentence is in the 4 nights (observed).
- **W16 couples the write to `_removal_spans`,** a reader that frame 339 means to retire. If 339 retires it, this check needs the reader that replaces it.
- **Why the seats did not apply the refusals is not in the records.** s235's turn 5 restated his words correctly and then sent no call. s234 changed only line 23, between two refused values.
- **Not read:** the build condition of frame 193's IG text; whether frame 250's night count was met; why s179 chose `remove` for "should be named".

## 8. Usage

One agent on Opus, no sub-agents. About 130k tokens against the 120k cap. Scripts are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/77c8dc39-1322-4ba4-bcb6-9a1031822837/scratchpad/seam/`: `replay.py` (all calls at one code root, with the night 173 state repaired), `hypo.py`, `hypo2.py` and `hypo3.py` (the forms that land), `fixreach.py` (the four texts and their own fixes), `w9expo.py` and `w9reach.py` (W9), `w16probe.py` (W16), `rl173.py` (`reading_line` at both trees), and `db/` with the copies of the night 170 to 173 registers. The trees: `p7r/parent` is 2b1ef4c9, `p7r/head` is 0ae7ab54, and `seam/tip` is 3b31077a.
