# The 12 landing cases after the one-word seam, 2026-10-29

Result: 8 failed cases, class A 0, class B 4, class C 4, class D 0. No expectation reads a dead shape. Four failures are the seat's word. Four are a door that refuses a right word. (observed: the log l1_landing_main_2c.txt and the case_runs rows of 05:43 to 05:45)

Review p4 finding 4 does not bite. The rulings write fills `words` with his whole reply, so 'separate request' at l1_landing.yaml 348 matches. (observed: case 5 rows carry "words": "They're independent. The confirm change is a separate request ...")

## The eight cases

1. a-correction-in-a-sentence. Expects `"<i2>": "contest"`, `"<i1>": "approve"`. The seat wrote `{"1": "revise", "2": "revise", "3": "drop"}` in 3 runs and `contest` on all three lines in 2 runs. The door accepted every write. (observed: transcripts run 1 to 5)
   Class B. His words name no line, so `line_words` binds the whole reply to all three lines, and the no-words door has nothing to refuse. (observed: probe, all three lines carry "no, it should print the total ...")
   Lever: the prompt sentence "A correction counts against the line it is about" has no door behind it when the reply names no number. (reasoned: the door reads `his_lines` only)

2. a-question-about-the-page. Expects one `converse` and no rulings write. 3 of 5 passed with `rulings.rule(ask=...)`. Runs 1 and 5 wrote `{"1": "approve", "2": "approve", "3": "contest"}`. (observed: log 204 to 206, transcript run 1)
   Class B. The threshold is 4. Lever: a door that refuses a `rulings` map when the reply is a question and points at `ask`. The `ask` word on a line already gets that pointer. (observed: run 2 refusal "'ask' is a question back, and a question is its own call")

3. a-question-then-a-statement-at-the-confirm. Expects one `converse` and no rulings write. The seat wrote `{"1": "contest"}` in all 5 runs. (observed: transcript run 1, log 307 to 311)
   Class B. The case comment says a prompt sentence on questions turned a green case red on each model. Lever: the same door as case 2, on the confirm page. (observed: l1_landing.yaml 165 to 167; reasoned: the lever is a door, not a sentence)

4. approve-one-line-only. Expects `"<i1>": "approve"` and no approve on i2 or i3. The seat wrote `{"1": "approve", "2": "drop", "3": "drop"}` three times and got 0 writes. (observed: transcript run 1)
   Class C. Refusal: "rulings.rule: line 2: no words of his name line 2. Rule the lines his words name, and approve or leave out line 2". His words say "2 and 3 say the same sentence twice each". (observed: transcript run 1, yaml 204)
   Lever: `line_words` gives lines 2 and 3 no words. It binds "1 is fine" and misses the conjoined subject "2 and 3". (observed: probe {1: '1 is fine, go ahead with it.', 2: None, 3: None}; code `_subject_lines` api.py 13434)

5. a-separate-request-is-later. Expects `"<i1>": "park"`. The seat wrote `{"1": "drop"}` in all 5 runs on the shift page. The door accepted it, and `per_item` kept `drop`. (observed: log 517 to 521, transcript run 1)
   Class B. The prompt says "It is a separate request" is `later`, and the code maps `separate` to `park`. (observed: landing.md 23, api.py 11588)
   Lever: the shift page door takes `drop` with a `later` cue in his words. A cue door on the shift page, fed by the map at 11588, refuses it. (reasoned: the map exists, no door reads it on the shift page)

6. remove-lines-on-a-criteria-page. Expects c1 (line 2) `approve`, c2 and c3 `contest`, and two `ruled_refs` rows with act `drop`. The seat first wrote the right map, lines 7 and 8 `drop`, lines 1, 2, 9 `approve`, and lines 3 to 6 `drop`. (observed: transcript run 1)
   Class C. Refusal: "rulings.rule: The words fault line 2, "alone". An approve keeps the line as it is ... Rule line 2 contest or revise". His words say "finish with line 2 alone", which keeps line 2. The seat then wrote `revise` on line 2. (observed: transcript run 1, yaml 366)
   Lever: the fault cue reads "alone" in the clause that names line 2 as a fault. (reasoned: the clause keeps the line)
   Open point: the write carried `contest` for lines 7 and 8, and 0 `ruled_refs` rows landed. `line_words` binds both lines, so `_word_shape` at api.py 14526 gave no shape. Check it before the re-record. (observed: log 622 "expected writes to ruled_refs (>0), got 0"; probe binds 7 and 8; reasoned: the cause)

7. drop-both-examples. Expects c2 and c3 `contest` and two `ruled_refs` rows with act `drop`. The seat wrote `{"1": "drop", "2": "drop"}` three times and got 0 writes. (observed: transcript run 1)
   Class C. Refusal: "rulings.rule: The words name no line of this page, so they change no row on it." His words say "Drop both of those examples" on a two-line page. (observed: transcript run 1, yaml 430)
   Lever: the row-change door wants a line number. `line_words` binds the whole reply to both lines, so the door reads a stricter source than the matcher. (observed: probe binds lines 1 and 2; reasoned: the door's source)

8. removing-lines-is-right. Expects c2 and c3 `contest`, i1 and c1 `approve`. In run 1 the seat's first map was exactly right: lines 7 and 8 `drop`, the rest `approve`. (observed: transcript run 1)
   Class C. Refusal: "rulings.rule: The words say lines 7 and 8 match what the principal asked for, and a contest reverses the principal. Approve lines 7 and 8." The prompt says "removing line 5 is right" drops line 5. (observed: transcript run 2, landing.md 17)
   Lever: the agreement cue reads "is right" as approval of the line, while the sentence drops the line. The door contradicts the prompt. Runs 2 to 5 also dropped lines 3 to 6, which the door refused rightly. (observed: run 2 second refusal "Approve the lines the words do not name")

## Count and the next step

- Class A: 0. No edit to l1_landing.yaml. The two `words` expectations at 59 and 348 read a column the write still fills. (observed: case 5 rows)
- Class B: 4, cases 1, 2, 3, 5. Three of the four levers are a door with no sentence behind it, on a reply with no line number, a question, or a `later` cue.
- Class C: 4, cases 4, 6, 7, 8. Three doors refuse a word that `line_words` or the prompt supports: the conjoined subject, the "alone" fault cue, the row-change line demand, and the "is right" agreement cue.
- Class D: 0. One open check inside case 6, the missing `ruled_refs` rows.

Order by reach: the "is right" cue and the row-change door hit 3 drop cases. The question door hits 2 cases. The conjoined subject hits 1. (reasoned: the counts above)
