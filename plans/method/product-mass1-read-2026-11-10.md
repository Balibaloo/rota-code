# The seat's pages against the design, mass 1, 2026-11-10

One reader, no hypothesis, primary records only. The reader read no
stack page, no meta page and no `dry*-read-*` page. Every database read
was a read-only copy in the scratchpad of session 1efd37b1, folder
`mass1/db/`. The scripts are `copy_all.py`, `extract.py`, `find_copy.py`,
`render.py` and `checks.py` in `mass1/`. Rendered pages are in
`mass1/pages/`.

## Result

1. Six of 18 design statements hold on every drawn page where the records can tell. They are: the words are recorded, a clarify names its rows, intent approval comes before work, a question changes nothing, the tool does not rule for the Principal, and no page carries a time.
2. "One page at a time" fails most often: 20 of 24 pages were open beside at least one other page.
3. On 13 pages, desks got work from the Liaison's reading of a reply before the Principal saw that reading.
4. On 11 pages, rota asked the same thing again after an answer, or put the same rows again. The seat's own words say so on three pages.
5. On 10 replies, the Liaison's reading was never shown back to the Principal.
6. Both replies that asked a question got no answer. dry1 m3 got no lines, and blind1 m4 got a question back that the seat could not then answer.
7. On three pages a contest or revise ruling left the contested row unchanged, and on blind1 m4 the correction landed no ruling at all. On dry6c the seat gave the same correction twice before the touch changed.
8. Nine pages do not say truly whether work waits on them. Seven intent pages say only "nothing is built". Two touch notes say "Reply 'ok' to go ahead" after the batch had started.
9. None of the 8 clarify pages offers a default.
10. The page text comes from a render by today's code on copies of the databases. For blind1 m2, blind1 m4 and dry8 m18 the render matches the recorded page exactly. For the other 21 pages nobody checked the render against what was shown.

## Part A: what the design says about the seat

Each statement is the source's words or close to them. The check that
this read applied is in brackets.

1. "The wiring records the words verbatim before the Liaison wakes." (`plans/composition.md:27-28`) [the reply's words are on a row tied to the reply]
2. "It infers intent, then checks and clarifies with the Principal." (`composition.md:26-27`) [a later page shows the reading of this reply back, or the Liaison asks]
3. "The verbatim words and the confirmed reading are two records. An unchecked inference is never a record." (`composition.md:106-107`) [no desk gets work from the reading before the Principal confirms it]
4. "It may originate a question the Principal did not raise, and the question names the row it is about." (`composition.md:30-31`)
5. "Approval of intent is required before work starts." "No batch starts until the first page is answered." (`composition.md:22`, `rota/DECISIONS.md:1383-1384`)
6. "A question changes nothing." (`composition.md:71`)
7. "The tool never rules for the Principal. It never settles a conflict, closes an assumption, or treats silence as consent." (`composition.md:74-75`)
8. "Nothing stops quietly. Every open obligation stays visible and countable until something discharges it." (`composition.md:50-51`)
9. "A question at a page is answered." (`rota/COMPLETION.md:69`)
10. "Nothing is asked twice." "A page after a contest shows only what is still open." (`DECISIONS.md:1382`, `plans/principal-flow.md:253-254`)
11. "Contest overrules and re-derives through the contested loop." (`COMPLETION.md:29-30`) [the contested row changes]
12. "Contest is words, not a form. The words go to the owner." (`principal-flow.md:258-259`)
13. "A page is a hold or a note." "The header says whether the page holds." (`DECISIONS.md:1428`, `principal-flow.md:255-257`) [the page says whether work waits, and the record agrees]
14. "The header says what the page is for." (`principal-flow.md:249-250`)
15. "One page at a time. The seat shows the page that is owed and nothing else." (`principal-flow.md:246-247`) [open pages in the copy nearest before the reply]
16. "The page shows no ids by contract." (`plans/seat-exchange.md:55-56`) [the page body, without the agenda header]
17. "A question still is not ready to ask until its default and its plausible choices are prepared." (`rota/SEAT.md:589-591`)
18. "No time, no estimate, no deadline on any page." (`principal-flow.md:474`)

## Part B: the 24 pages

Keys: `w`, `t` and `frozen` name the copies. "Render" means
`principal.render_page` from today's code (HEAD 16d72fba) on a throwaway
copy of that copy. "Next" is from `messages` (by `seq`) and `sessions`
(by `seq`, linked by `trigger_msg`). The two counters are separate.

**dry1 m2, confirm.** Source: render of `.rota/dry1_frozen.db`, taken after the reply (no inventory copy holds the page before its reply). 4 lines, 472 chars.
- Asks: confirm the request "Make click.pause() return True when it waited for a key and False when it skipped ...".
- Reply: keypress verdict `m4`, no `converse` row. `rulings` r_m4: words "ok", `ruled_refs` source `keypress`.
- Meaning: s1 approve. Matches.
- Next: m4 quarantined after Liaison sessions s38, s39, s40 (`committed=0`), `told=1`. The confirm came back as m8. The seat's words on it (r_m11): "ok. I already said ok to this on the first page, and the request has not changed." Delivers m13, m14 followed. bg_1 merged at the end of the run.

**dry1 m3, present.** Source: render of `dry1_frozen.db`, after the first reply. 2 lines, 194 chars. `body_refs` is `[]`, so the page has no numbered line.
- Asks: approve "this page" with no rows on it.
- Replies: m5 "The page shows me no lines. What do you want me to approve? Show the plan as numbered lines." (quarantined, s41 to s43 `committed=0`). m25, the same words (status answered). m34 "ok". m37 "ok", verdict m38.
- Meaning: r_m37, words "ok", `per_item` `{}`, no `ruled_refs` row. No message has `cause_id` m25. s113 called `rulings.rule rulings={'rest': 'none'}` twice.
- Next: m39 Vision Keeper submit, then pages m40 and m41.

**dry1 m17, present.** Source: render of `dry1_frozen.db`, page open and no reply. 4 lines, 636 chars.
- Asks: approve line 1, "The program is a command-line interface toolkit called Click ...".
- Reply: keypress verdict m29. r_m29 words "", how_it_works approve, source `keypress`.
- Meaning: matches a keypress.
- Next: relay m31 to the Vision Keeper (s119). The same row was approved on m7 (r_m10, "ok, that is what Click does", seq 10) and was put again on m157 (seq 162).

**dry1 m_park_421158fa15_bg_1, present (park).** Source: render of `dry1w7`, page open, no reply. Ten columns of today's schema were added to the throwaway copy. 17 lines, 1468 chars.
- Asks: rule on a stopped change. Three criteria with checks. Line 7's check fails "assert False is True". The page lists one held page by id, m120.
- Reply: m128 "Line 7's check is wrong, and line 6 stands. The test patches click.pause after the import, so the patch does nothing. Patch click.termui.isatty ...".
- Meaning: r_m128, verdict m135. Line 7 (tst_waited) contest, rewrite. Line 6 approve, "line 6 stands." Line 1, the request, approve with act `add` and the patch sentence. Lines 2 to 5 approve, words the whole reply. Lines 6 and 7 match the words.
- Next: no message has `cause_id` m128 or m135. s256 batch_start "resume after attempt 8: all 36 tests pass". s257 tests_failing attempt 9. s259 park_ask "attempt 10 of 10 with tst_waited red". Park page m_park_a162344dbf_bg_1 put the same rows. The reply m139 again began "Line 7's check is wrong, and line 6 stands." bg_1 merged at the end.

**dry2 m17, present.** Source: render of `dry2w2`, open. 5 lines, 503 chars.
- Asks: approve one assumption: "The 9 live terms in the glossary are being treated as program vocabulary by the terminologist, but their functional role (vocabulary vs. furniture) remains unverified."
- Reply: m19 "ok". Meaning: r_m19, l_6f936b0fd0 approve. Matches.
- Next: verdict m21, no relay. The read-back on m23 was approved (r_m35). Slicing s46, criteria s47 and s48, grouping s49. b_1 merged and b_2 abandoned at the end.

**dry2 m24, present (touch note).** Source: render of `dry2w3`, open. 13 lines, 1574 chars.
- Asks: approve the predicted touch of b_1 (main.py, tests/test_calculate_tip.py, tip_calculator.py) and three criteria with passing checks.
- Reply: m36 "ok". Meaning: r_m36 approves 9 rows, `verdict_id` null. Matches.
- Next: b_1 was built and reviewed before the reply landed. s53 touch_note, s55 batch_start, s56 to s60 tests, s61 critic review, then s78 lands m36. b_1 merged at the end.

**dry3 m14, clarify.** Source: render of `dry3w3`, open. 6 lines, 705 chars.
- Asks: are "component" and "Component" one term or two, and should they merge.
- Reply: m19 with `body_text` null. Words in r_m19: "One term. Component is the class in the code, and the word component means the same thing."
- Meaning: r_m19_2 approves both term rows. The words say one term. The record keeps two approved rows (reasoned: no merge act is recorded).
- Next: relay m22 to the Terminologist (s108), term_collision ticks s111 to s114. The read-back on m39 was approved (r_m44). bg_1 merged at the end.

**dry3 m16, clarify.** Source: render of `dry3w3`, open. 6 lines, 717 chars.
- Asks: is "alarm" the trigger component only, or does it include the snooze logic.
- Reply words (r_m20): "An alarm is the trigger component. Snooze is a relationship between alarms, not part of the term."
- Meaning: r_m20_2. alarm#src_icalendar_tests approve. alarm#src_icalendar_tests_events contest, act `remove`, target `sentence`, words "Snooze is a relationship between alarms, not part of the term." Matches the words.
- Next: relay m23 to the Terminologist (s109). The read-back on m39 was approved. The contested row reads "A component representing a notification trigger for an event." at version 1 in the copy and at the end.

**dry4 m40, present (touch note).** Source: render of `dry4w6`, open. 20 lines, 4036 chars. Line 8 alone names 15 paths, 7 commitments and 10 notes, "and 33 more". Six criteria show "check: none yet."
- Asks: approve the predicted touch.
- Reply: m49 "ok". Meaning: r_m49 approves 9 rows, `verdict_id` null. Matches.
- Next: the batch had started before the reply. s177 touch_note, s178 to s180 batch_start "nothing written", s188 quarantined, s189 park_ask "It is a note". After the reply, s199 to s201 batch_start "nothing written", s202 quarantined. The same rows came back on m47 ("ok"), m57 and m63 (open at the end). On m57 the seat wrote "Line 8: the fold lives in src/icalendar/parser/string.py, in _foldline, and parameter.py and property.py are not it." bg_1 is `running` at the end.

**dry4 m46, clarify.** Source: render of `dry4w6`, open. 5 lines, 2816 chars. The "This is about" line repeats the whole batch line of m40.
- Asks: does "keep everything else as before" mean line numbers, or identical content.
- Reply words (r_m51): "The content stays identical and only the fold is inserted, so a reader joins the lines back to the original."
- Meaning: r_m51_2, bg_1 approve, with the words. Matches.
- Next: relays m55 to the Architect and m56 to the Vision Keeper (`e_m51`). Then s199 to s202 as above.

**dry5 m16, clarify.** Source: render of `dry5/w4`, open. 6 lines, 554 chars.
- Asks: does "alarm" include the RELATED-TO property for snooze.
- Reply words (r_m20): "One term. An alarm is the VALARM component, and RELATED-TO is one property it can carry."
- Meaning: r_m20_2. alarm#src_icalendar_tests revise, rewrite. alarm#src_icalendar_tests_events approve. The words say one term, and the record revises one row (reasoned: partial match).
- Next: relay m23 (s109), s111 term_collision "alarm", m25 report, then clarify m26: "Does the scope of 'alarm' in the codebase include the logic for handling 'RELATED-TO' snooze relationships ...". The seat's words on m26 (r_m29): "One term, as I said on m16. ..." The revised row is version 1, same text, at the end. b_1 deferred at the end.

**dry5 m47, clarify.** Source: render of `dry5/w8`, open. 8 lines, 1104 chars. The first line is a stray-touch notice: "The change removes code that no answer of yours allowed: in _foldline, the line `assert "\n" not in line` and the branch ...".
- Asks: with no space before the limit, leave the line long or split the word.
- Reply words (r_m62): "Split at the limit, as the code does today. Do not leave a line longer than the limit."
- Meaning: r_m62_2. c_1 revise, c_2 approve, c_3 revise, old texts kept. Matches.
- Next: relay m67 to the Terminologist, answer m69 to the Tester. Clarifies m65 and m68 on the fold followed. s241 exhausted "the team could not put back code it was not asked to change after 3 attempts". s242 quarantined touch_mistaken. c_1 and c_3 are version 1, same text, at the end. b_1 deferred.

**dry6 m4, present.** Source: render of `dry6/w2`, open. 9 lines, 1348 chars.
- Asks: approve five lines on what icalendar does today.
- Reply: m6 "ok". Meaning: r_m6 approves 5 rows. Matches.
- Next: verdict m8 quarantined after s50 to s52 (`committed=0`), `told=1`. The same rows came back on m12.

**dry6 m12, present.** Source: render of `dry6/w5`, open. 10 lines, 1442 chars. The same five lines and a read-back line.
- Reply: m15 "ok". Meaning: r_m15 approves 6 rows. Matches.
- Next: verdict m17 (s80 failed, s81 committed), relay m19 to the Vision Keeper (s83). Architect surveys then quarantined (s84 to s89). `dry6/t5.log` agenda: "Stuck: the team could not read a part of the code for news after 3 attempts ...". No batch at the end.

**dry6b m2, confirm.** Source: render of `dry6b/w2`, open. 4 lines, 488 chars.
- Asks: confirm "When icalendar writes a long line, fold it at a space where it can, so that a word is not split, and keep everything else as before."
- Reply: m5 "ok". Meaning: r_m5, s1 approve. Matches.
- Next: verdict m7, delivers m9, m10, m11 to the Architect, Terminologist and Vision Keeper.

**dry6b m12, present.** Source: render of `dry6b/w3`, open. 10 lines, 1587 chars.
- Asks: approve five lines on what icalendar does today, and the read-back of "ok" on m4.
- Reply: m13 "ok". Meaning: r_m13 approves 6 rows. Matches.
- Next: verdict m14 quarantined (s73 to s75), `told=1`. The same rows came back on m15 ("ok", verdict m17 quarantined) and on m18, open at the end of dry run 6b. The verdict m8 of m4 was quarantined too.

**dry6c m26, present.** Source: render of `dry6b/w6`, open. 9 lines, 1173 chars.
- Asks: approve the request, the team's guess of the code it touches (property.py and three test files) and one assumption. "'ok' approves all of this and starts building."
- Reply: m27 "Line 2 is wrong. The fold is _foldline in src/icalendar/parser/string.py, and its tests are in src/icalendar/tests/test_icalendar.py. Do not touch parameter.py or property.py."
- Meaning: r_m27. Line 2 contest, rewrite, "Line 2 is wrong." Line 1 approve, act `add`, "Do not touch parameter.py or property.py." Line 3 approve. No `ruled_refs` row carries the two named files except as the whole words on line 3.
- Next: relays m29 (Architect) and m30 (Vision Keeper). In `dry6b/w7`, `batch_touch` of b_1 names property.py. Developer question m32: "The principal said "Do not touch parameter.py or property.py." but the ticket explicitly names src/icalendar/parser/property.py ...". Page m38 line 5 still names property.py, and the seat replied again (m41 "Line 5 is wrong. ..."). `batch_touch` names string.py only in `dry6b/w8`. b_1 deferred at the end.

**dry6c m37, clarify.** Source: render of `dry6b/w7`, open. 5 lines, 2108 chars. The row line carries the batch line, commitments, notes and 5 red tests.
- Asks: does the fold apply to line content only, or must the format's structure stay as in the source.
- Reply words (r_m40): "Every content line that icalendar writes. Keep everything else as it is today."
- Meaning: r_m40_2, b_1 revise, rewrite row. The words name which lines. The record revises the batch row (reasoned: partial match).
- Next: relay m43 to the Architect. Tester questions m47 and m49: "Cannot encode tests for c_1, c_2, c_3 because the criteria reference modules (billing) or functions (fold) that do not exist ...". b_1 and c_1 to c_3 are version 1 at the end. Three park pages on b_1 followed. b_1 deferred.

**dry7 m2, confirm.** Source: render of `dry7/copies/w1`, open. 4 lines, 488 chars. The same request as dry6b.
- Reply: m5 "ok". Meaning: r_m5, s1 approve. Matches.
- Next: verdict m7, delivers m9 to m11. The read-back of m5 was on m22 and m29, approved by r_m42.

**dry7 m14, clarify.** Source: render of `dry7/copies/w3`, open. 6 lines, 729 chars.
- Asks: is "parameter" the class or the attribute, and which definition the parser takes.
- Reply words (r_m15): "Both are the same thing. A parameter is an optional attribute that modifies a property, and the Parameters class holds them."
- Meaning: r_m15_2 approves both rows. Matches.
- Next: relay m16 to the Terminologist, report m17, then clarify m18: "The principal previously stated they are the same thing, but the code requires a distinction ...". The seat's words (r_m23): "It is a modifier of a property. ... This does not change my request." b1 deferred, m61 and a park page open at the end.

**dry8 m18, clarify.** Source: render of `dry8/copies/t4`, open. `dry8/turns/t4.txt` lines 55 to 61 show the same text. 6 lines, 646 chars.
- Asks: is a parameter the container object or the attribute entries. The question says "The principal previously stated they are one thing".
- Reply: m23 with `body_text` null. Words (r_m23): "Treat a parameter as one attribute entry inside the container; the Parameters class is only the container, and this question is settled."
- Meaning: r_m23_2 approves both rows. Matches.
- Next: relay m25 to the Terminologist (s147), slicing s151, criteria s152, grouping s153. bg_1 deferred at the end with m52, m54, m57, m58, m59 open.

**dry8 m_park_e65413c486_bg_1, present (park).** Source: render of the final copy. No copy holds the page open. 8 lines, 968 chars.
- Says: the change stops and breaks two checks. "Nothing waits on you. A new commit on the change starts it again." It lists four held pages by id.
- Reply: none. No message has the page as `cause_id`, and no `rulings` row names it. Its status is `answered`.
- Next: none. It is the last message (seq 60). No session has it as `trigger_msg`. It is not in `turns/t6_agenda.txt` or `turns/t6_tail.txt`.

**blind1 m2, confirm.** Source: `blind1/seat/exchange.jsonl` line 1, the page as shown. The render of `copies/t2` matches it. 4 lines, 376 chars, and the seat also saw a header "[m2] confirm · rule by id: s1".
- Asks: confirm "Refuse a negative bill amount, the same way a bad tip percentage is refused."
- Reply: m5 "ok" (exchange line 1). Meaning: r_m5, s1 approve. Matches.
- Next: s34 `brief.ratify` s1 and delivers m9 to m11. Definitions, surveys, commitments and challenges ran (s8 to s31). The run ends at session 39 with no batch.

**blind1 m4, present.** Source: exchange line 3, the page and the words. The render of `copies/t2` matches it. 9 lines, 1085 chars.
- Asks: approve five lines on what the program does today. "'ok' approves this page, and nothing is built."
- Reply: m6 "Line 5 is wrong: today the calculation accepts a negative bill with no error ..., and a bill of zero is fine, so "positive" is not right either. Also, what does "nothing is built" mean after 'ok'? I still want the change made."
- Meaning: no `rulings` row for m4. s33 called `rulings.rule {'5': 'rewrite', 'c2': 'ask', 'c3': 'none'}` and an ask. The ask became m8: "Does 'nothing is built' mean that the current state of the code is what you want to keep, or that you want me to proceed with the changes described in the previous turn?"
- Next: both seat replies to m8 failed with "m8 is not an open gate; `rota agenda blind1` lists them" (exchange lines 6 and 8). m4 is open at the end. total_validation is version 1 and still says "positive number".

## Part C: the grid

Page ids are `run:message`. `d1park` is dry1 m_park_421158fa15_bg_1 and
`d8park` is dry8 m_park_e65413c486_bg_1. In the third column, "n/a"
marks a page that the statement does not apply to.

| # | statement | holds | does not hold | cannot be told |
|---|---|---|---|---|
| 1 | words recorded verbatim | 22: all others | 0 | 2: dry1:m17 (keypress, no words), d8park (no reply) |
| 2 | Liaison checks its reading | 8: dry2:m17, dry3:m14, dry3:m16, dry6:m4, dry6b:m12, dry6c:m26, dry7:m2, blind1:m4 | 10: d1park, dry2:m24, dry4:m40, dry4:m46, dry5:m16, dry5:m47, dry6b:m2, dry6c:m37, dry7:m14, dry8:m18 | 6: dry1:m2, dry1:m17 (keypress), dry1:m3 (no rows), dry6:m12, blind1:m2 (run stopped soon after), d8park (no reply) |
| 3 | no work on an unconfirmed reading | 7: dry1:m2, dry1:m3, dry1:m17, dry2:m17, dry6:m4, dry6b:m12, blind1:m4 | 13: dry3:m14, dry3:m16, dry4:m46, dry5:m16, dry5:m47, dry6:m12, dry6b:m2, dry6c:m26, dry6c:m37, dry7:m2, dry7:m14, dry8:m18, blind1:m2 | 4: d1park, dry2:m24, dry4:m40 (no relay, cause of later work not traced), d8park |
| 4 | originated question names its row | 8: all clarifies | 0 | 16 n/a |
| 5 | intent approval before work | 12: the 4 confirms, dry1:m3, dry1:m17, dry2:m17, dry6:m4, dry6:m12, dry6b:m12, dry6c:m26, blind1:m4 | 0 | 12 n/a |
| 6 | a question changes nothing | 2: dry1:m3, blind1:m4 | 0 | 22 n/a |
| 7 | the tool never rules for him | 23 | 0 | 1: d8park |
| 8 | nothing stops quietly | 22 | 1: dry1:m3 | 1: d8park |
| 9 | a question at a page is answered | 0 | 2: dry1:m3, blind1:m4 | 22 n/a |
| 10 | nothing is asked twice | 10: dry2:m17, dry2:m24, dry3:m14, dry3:m16, dry4:m46, dry6b:m2, dry6c:m37, dry7:m2, blind1:m2, blind1:m4 | 11: dry1:m2, dry1:m3, dry1:m17, dry4:m40, dry5:m16, dry6:m4, dry6:m12, dry6b:m12, dry6c:m26, dry7:m14, dry8:m18 | 3: d1park (new failure each time), dry5:m47 (m65 near the same point), d8park |
| 11 | a contest re-derives the row | 0 | 4: dry5:m16, dry5:m47, dry6c:m26, blind1:m4 | 20: d1park (the rewrite came from another page's chain), dry3:m16 (the row never held the sentence), dry6c:m37 (the change follows two replies), and 17 n/a |
| 12 | contest words go to the owner | 5: dry3:m16, dry5:m16, dry5:m47, dry6c:m26, dry6c:m37 | 2: d1park, blind1:m4 | 17 n/a |
| 13 | page says hold or note, truly | 15: the 4 confirms, the 8 clarifies, dry6c:m26, d1park, d8park | 9: dry1:m3, dry1:m17, dry2:m17, dry6:m4, dry6:m12, dry6b:m12, blind1:m4, dry2:m24, dry4:m40 | 0 |
| 14 | page says what it is for | 23 | 1: dry1:m3 | 0 |
| 15 | one page at a time | 3: dry6b:m12, dry6c:m26, dry7:m14 | 20: all others | 1: d8park |
| 16 | no ids on the page | 20 | 4: d1park, dry5:m47, dry7:m14, d8park | 0 |
| 17 | a default is prepared | 15: all confirms, presents and d1park | 8: all clarifies | 1: d8park (asks nothing) |
| 18 | no time on a page | 24 | 0 | 0 |

Evidence for each "does not hold" cell, one line per page. "No read-back"
means that no page to the principal carries `reading:<reply id>` in
`body_refs` (query in `checks.py`).

Row 2:
- d1park: no read-back of m128.
- dry2:m24: no read-back of m36.
- dry4:m40: no read-back of m49.
- dry4:m46: no read-back of m51.
- dry5:m16: no read-back of m20.
- dry5:m47: no read-back of m62.
- dry6b:m2: no read-back of m5. Later pages carry `reading:m6`, `reading:m13` and `reading:m16`.
- dry6c:m37: no read-back of m40.
- dry7:m14: no read-back of m15.
- dry8:m18: no read-back of m23.

Row 3 (a relay or deliver caused by the reply or its verdict, and no approve of `reading:<reply>` before it):
- dry3:m14: relay m22 (seq 22). The approve of `reading:m19` is r_m44, on page m39 (seq 39).
- dry3:m16: relay m23 (seq 23). The approve of `reading:m20` is r_m44, on m39.
- dry4:m46: relays m55, m56. No row on `reading:m51` exists.
- dry5:m16: relay m23. No row on `reading:m20` exists.
- dry5:m47: relay m67. No row on `reading:m62` exists.
- dry6:m12: relay m19. No row on `reading:m15` exists.
- dry6b:m2: delivers m9 to m11 (cause m7). No row on `reading:m5`. The words were "ok".
- dry6c:m26: relays m29, m30 (seq 29, 30). The first read-back is m31 (seq 31). No `ruled_refs` row on `reading:m27` exists.
- dry6c:m37: relay m43. No row on `reading:m40` exists.
- dry7:m2: delivers m9 to m11 (seq 9 to 11). The approve of `reading:m5` is r_m42, on m22 or m29. The words were "ok".
- dry7:m14: relay m16. No row on `reading:m15` exists.
- dry8:m18: relay m25. No row on `reading:m23` exists.
- blind1:m2: delivers m9 to m11. No row on `reading:m5`. The words were "ok".

Row 8:
- dry1:m3: m25 is `answered`, no message has `cause_id` m25, and s113 ruled `{'rest': 'none'}` twice. m25 `unresolved_note`: "your reply was cut at the output budget before it ended ...".

Row 9:
- dry1:m3: m5 quarantined (s41 to s43 `committed=0`). m25 got no answer (row 8). The next replies are "ok" (m34, m37).
- blind1:m4: m8 asked a question back. The seat's two replies to m8 failed, `exchange.jsonl` lines 6 and 8.

Row 10:
- dry1:m2: confirm m8 (seq 8) put s1 again after verdict m4 (seq 4). r_m11: "ok. I already said ok to this on the first page, and the request has not changed."
- dry1:m3: one page, four replies: m5, m25, m34, m37.
- dry1:m17: how_it_works was approved on m7 (r_m10, seq 10) before m17 (seq 16), and was put again on m157 (seq 162).
- dry4:m40: the same rows on m47 (open beside m40 in `dry4w6`), m57 and m63.
- dry5:m16: m26 asks the RELATED-TO question again. r_m29: "One term, as I said on m16."
- dry6:m4: the same five rows on m12 after "ok" (m6).
- dry6:m12: repeats m4, whose ruling r_m6 had landed.
- dry6b:m12: the same rows on m4 before it, and on m15 and m18 after it.
- dry6c:m26: m38 line 5 still names property.py (render of `dry6b/w7`). The seat repeated the correction on m41.
- dry7:m14: m18 asks again: "The principal previously stated they are the same thing".
- dry8:m18: repeats m14 (r_m15, "They are one thing: ..."). The text of m18 says "The principal previously stated they are one thing".

Row 11:
- dry5:m16: alarm#src_icalendar_tests revised. `glossary_terms` version 1, same text, in `dry5/w4` and at the end.
- dry5:m47: c_1 and c_3 revised. `criteria` version 1, same text, in `dry5/w8` and at the end.
- dry6c:m26: line 2 contested. `batch_touch` b_1 names property.py in `dry6b/w7`. string.py appears first in `dry6b/w8`, after the second contest m41.
- blind1:m4: no `rulings` row on m4. total_validation is version 1 and says "positive number" at the end.

Row 12:
- d1park: no message has `cause_id` m128 or m135.
- blind1:m4: no Liaison message to a desk has `cause_id` m6. The only one is m8, to the principal.

Row 13:
- dry1:m3: the closing line is "'ok' approves this page, and nothing is built." Nothing says whether work waits.
- dry1:m17: the same closing line.
- dry2:m17: the same closing line.
- dry6:m4: the same closing line.
- dry6:m12: the same closing line.
- dry6b:m12: the same closing line.
- blind1:m4: the same closing line. The seat asked "what does "nothing is built" mean after 'ok'?" (m6).
- dry2:m24: the page says "Reply 'ok' to go ahead." b_1 batch_start s55 and review s61 ran before s78 landed the reply.
- dry4:m40: the page says "Reply 'ok' to go ahead." batch_start s178 ran before s191 landed the reply.

Row 14:
- dry1:m3: no numbered line (`body_refs` `[]`, 2 lines). Reply m5: "The page shows me no lines."

Row 15 (open pages in the copy nearest before the reply):
- dry1:m2: m3 (seq 3) existed before the verdict m4 (seq 4) (reasoned from seq).
- dry1:m3: m3, m17, m16, m18, m19 open in `dry1_frozen`.
- dry1:m17: the same five pages open in `dry1_frozen`.
- d1park: m108, m112, m114, m120, m122 and the park page open in `dry1w7`. The park page folds only m120.
- dry2:m17: m17 and m16 open in `dry2w2`.
- dry2:m24: m23, m24, m25, m33, m34 open in `dry2w3`.
- dry3:m14: m14, m16, m18 open in `dry3w3`.
- dry3:m16: the same three pages.
- dry4:m40: m39, m40, m44, m46, m47 open in `dry4w6`.
- dry4:m46: the same five pages.
- dry5:m16: m14, m16, m18 open in `dry5/w4`.
- dry5:m47: m42, m43, m47 open in `dry5/w8`.
- dry6:m4: m2 and m4 open in `dry6/w2`.
- dry6:m12: m12 and m14 open in `dry6/w5`.
- dry6b:m2: m2 and m4 open in `dry6b/w2`.
- dry6c:m37: m31, m37, m38 open in `dry6b/w7`.
- dry7:m2: m2 and m4 open in `dry7/copies/w1`.
- dry8:m18: m18 and m22 open in `dry8/copies/t4`. `turns/t4.txt` shows both on one agenda.
- blind1:m2: m2 and m4 open in `copies/t2`. The exchange answers both at 01:08:47 and 01:08:54.
- blind1:m4: the same two pages.

Row 16:
- d1park: "m120: The criterion tk_1_criteria_waited requires ...".
- dry5:m47: "c_3 specifies".
- dry7:m14: "(parameter#src_icalendar)" and "(parameter#src_icalendar_parser)" in the question.
- d8park: "m52:", "m54:", "m57:", "m58:", "(cw_7039d1d2d899)", "(as shown in tst_c3)".

Row 17 (each page ends "Reply in a sentence. I take it from there." and shows no default):
- dry3:m14, dry3:m16, dry4:m46, dry5:m16, dry5:m47, dry6c:m37, dry7:m14, dry8:m18.

## Part D: what the grid does not cover

1. The seat saw ids in a header above each page, which `render_page` does not build: "[m18] clarify · rule by id: parameter, parameter#src_icalendar" (observed: `dry8/turns/t4.txt:55`, and `blind1/seat/exchange.jsonl` line 1, "[m2] confirm · rule by id: s1").
2. On all 8 clarify replies, the reply's `messages` row has `body_text` null. The words exist only in `rulings.words`, on two rows per reply: one with `verdict_id` the reply and `per_item` `{}`, and one reading (observed: r_m19 and r_m19_2 in dry3, and the same pair on the other seven).
3. The seat's approval on three drawn pages was lost, and the page came back with the same rows and a read-back line. Each verdict was quarantined after three uncommitted Liaison sessions (observed: dry1 m4, dry6 m8 and dry6b m14, each `told=1`). Two more verdicts in dry6b, m8 and m17, have `status='quarantined'`.
4. Long rows. One line of dry4 m40 names 15 paths, 7 commitments and 10 notes "and 33 more" (observed: render, line 8). The clarify pages dry4 m46 (2816 chars) and dry6c m37 (2108 chars) repeat the whole batch line under "This is about". The m22 agenda in `dry8/turns/t4.txt` lists 27 paths on line 2.
5. The touch predictions that the seat contested named files the seat said were wrong. The seat's words say "parameter.py and property.py are not it" (observed: dry4 m58, dry6c m27 and m41, dry7 m24, dry8 m24).
6. "ok" on dry4 m40 approved six criteria that each showed "check: none yet." (observed: render of `dry4w6`, r_m49).
7. One page carries two subjects. dry5 m47 starts with a stray-touch notice and then asks a clarify question (observed: render line 1). Park pages fold other pages by id at their end (observed: dry1 park, dry8 park).
8. The blind seat could not reply to the Liaison's question m8. The tool refused the reply twice with "m8 is not an open gate", while `messages` m8 has `status='open'` (observed: exchange lines 6 and 8, blind1 final copy).
9. Two pages asked the person about the team's own bookkeeping: "their functional role (vocabulary vs. furniture) remains unverified" (dry2 m17) and "should they be merged into a single entry?" (dry3 m14) (observed: renders).
10. An observed line can be wrong, and the record keeps no correction of it. blind1 m4 line 5 says the total "is a positive number, raising an error". The seat said the calculation accepts a negative bill. The row is unchanged at the end (observed: m6, `items` total_validation).

## Part E: limits

- No database stores a page. Every page text except the two blind1 pages comes from a render by today's code (HEAD 16d72fba) on an older copy. The code at the time of each run differed. The render matches the recorded page for blind1 m2, blind1 m4 and dry8 m18 (`exchange.jsonl`, `turns/t4.txt`). Nobody checked the other 21 renders.
- For the dry1 park page and the later dry runs, the render added missing columns of today's schema to the throwaway copy, with null or default values. Ten columns were added for dry1 (`constraints.party` to `verdicts.failed_commitment`).
- dry1 m2, m3 and m17: no inventory copy holds them before their replies. This read used `.rota/dry1_frozen.db`, which the inventory does not name (max message seq 23). Its m2 is already answered, and its m3 has one reply.
- dry8 park: only the final copy holds it, and there it is already `answered`. This read cannot tell which writer closed it, or whether the seat ever saw it.
- Sessions and messages have separate `seq` counters, and no table has a clock. Order between a session and a message is reasoned from `trigger_msg` and the copy times, not observed on one counter.
- The agenda display code at run time is not recorded. Row 15 counts open page rows. The seat may have seen fewer pages where a park page folds held pages.
- blind1 and dry6 ended soon after the drawn pages. A missing read-back there may come from the end of the run. For this reason, grid row 2 marks blind1 m2 and dry6 m12 "cannot be told".
- The `.rota/dry*.db` files were opened on 2026-11-10 (the `-shm` times). `ruled_refs` holds no `backfill` row in any of the 11 databases (query on `source`), so no back-fill reached the rows read here. Nobody checked the page rows for a change.
- Two copies named `dry1w6` exist in two scratchpads (3b83d22b and 62bcfbfb). The scratch copy of the first was overwritten by the second. No drawn page uses either.
- The words in `rulings.words` for the clarify replies cannot be compared with what the seat typed. The dry turn scripts pass the words to `rota sign --say`, and the logs print only "reply sent".
- Row judgements marked "(reasoned)" in Part B rest on the reader's reading of the words against the rows. Grid rows 13, 14 and 17 rest on the page text alone.
