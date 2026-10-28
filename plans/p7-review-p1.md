# Review of P7 passes 1 and 1b with F2 passes 2f and 2g, 2b1ef4c9..0ae7ab54 on w7root

**Verdict: NOT READY.** The reader `said` fixes wall W7, and the five night 172 pages now quote his words. The new rulings guard `_unbacked_approve` has two high holes. It does not run on a call that passes `words`, and it does not run on a call that holds a contest. Its name rule also matches row columns that he never saw. The replay of 240 calls changes 13 refusal texts, and no land or refusal changes. Two findings are high and six are low.

Reviewer: a read-only agent in `C:/Users/roman/rota_r7` at 0ae7ab54. No tracked file was edited.

## (a) The verdict on each point

1. The reader: PASS with a low finding. `said` gives his words on every shape that `land` writes. It gives `""` and never None when he typed nothing. Three readers of his words still disagree (finding 5).
2. The replay: 13 of 240 results change, and all 13 move from one refusal to another refusal. Each new text is right on his words. P7 changes no recorded call, because the seats passed `words` on all 9 clarify answers. With `words` dropped, the guard refuses m33, m86 and m55, three answers that state a choice with no agreement word (finding 1).
3. The name rule: FAIL, high. An approve lands on an identifier that only the hidden `sense_body` column holds. A ref id that is a plain word, such as `command`, also counts as named by any use of that word (finding 2).
4. The nine sites and `_words_from`: each site now reads his words, and no site changes its verdict shape beyond that, except site 4. Site 4 fills an empty `words` on a clarify answer. Calls that the parent refused with "words is empty" now land, and some of them land approves on a question (finding 1).
5. The merge: PASS. `rulings_rule` reads his reply only through `_his_reply`, which calls `said`. The nested check and the act span read through `said`. `api.py` holds no `entry_for` call.
6. The pin: PASS on the planted literal, with a low finding. The pin goes red on `SELECT body_text FROM messages WHERE id = ?`. It stays green on six other shapes. Three live readers of his words already escape it (finding 6).
7. The gate: PASS. The gate gives 6 failed, 5820 passed, and the 6 reds are the known set of f9f5cd19. The flaky handover test passed this run. The 36 test files give 1 failed, 996 passed, and the red is the known `test_pins.py` test. The diff holds no CR byte, and no hunk is outside the claim.
8. F2 pass 2g against review p2f: the high of p2f is closed. Every words field, the top level, each line object and each act entry with no act, is checked against his reply. The clause rule does what the brief says on all probes. The two kept deviations each leave a low law 6 hole (findings 3 and 4).

## (b) Findings

1. **rota/roles/api.py 11951 and 14258, high. CONFIRMED.** The guard `_unbacked_approve` runs only when the call passes no `words` and every verdict is approve. On the clarify answer "what time is the meeting", two approves land when the seat passes `words="what time is the meeting"`, at the parent and at the head. One contest plus one approve with no `words` also lands at the head, and the parent refused it. The replay shows that the seats passed `words` on 9 of 9 recorded clarify calls, so the guard reaches 0 recorded calls. The skip for a contest has a reason only on a page with a line order, and a clarify has no line order. The guard also refuses m33 ("I don't know for sure, so I'll take the simple reading ..."), m86 and m55 when `words` is dropped. These replies state his choice, and both trees land them when `words` is passed. So one reply gets two outcomes, and only the form of the call decides which. Fix: run the check whether or not `words` is passed, keep the contest skip only on a page with a line order, and ask Roman whether a stated choice approves a clarify row.
2. **rota/roles/api.py 11931 to 11937 and 11960 to 11962, high. CONFIRMED.** `_row_words` joins every text column of the row, and the name rule matches his reply against all of them. A glossary row with `sense_body = "see the meeting_time flag"` takes an approve on the reply "what about meeting_time" with no `words`. The same row with no hidden text is refused. Ledger rows hold `unaddressed_answer` and `glossary_terms` in `kind` and `about_table`, and criteria hold identifiers in `surface_refs`. Every word of his reply also names a ref whose id is that word. A row with the id `command` takes an approve on the reply "what command do I run". Night 172's m55 has refs named `command` and `command#root`. The parent refused all of these calls with "words is empty". Fix: match the name rule against the line text that the page rendered for the row, and match a ref id only when the id holds a digit, an underscore or a `#`.
3. **rota/roles/api.py 11984 and 11995, low. CONFIRMED.** Kept deviation 1 leaves a law 6 hole. The act span check of `_words_from` is a substring check, so an act span can cut his clause. On m129, an act `remove` on line 11 lands with the span "giving up", "did not call line 4" or "call line 4 wrong". The landed row carries that fragment to the owner as his words. The verdict stays guarded, because "call line 4 wrong" as an act on line 4 is refused by the agreement rule. Fix: check an act span with `_holds_clauses` in `_words_from`. The s357 shape "use click directly in the test" in "On line 11, use click directly in the test." still passes that check (probe: ok).
4. **rota/roles/api.py 13740 to 13748, low. CONFIRMED.** Kept deviation 2 leaves a law 6 hole. A nested words field can match a sentence of an earlier answer that his reply takes back. On a copy where m128 says "Line 10 is wrong." and m129 says "Lines 9 and 10 are read right", an approve of line 10 lands with the words "Line 10 is wrong." and `words_from` m128. A contest of line 10 with the same words is refused, so only the words are wrong, not the verdict. Fix: refuse an earlier sentence when his reply names the same line.
5. **rota/roles/principal.py 3441, rota/roles/api.py 645, rota/core/runner.py 2646, low. CONFIRMED.** `said` is not the one reader of his words of a message. `api.message_entry` and `runner._recent_chat` read the same fact by other rules, and the three disagree on four shapes. For an own entry and a different body, `_recent_chat` gives the body and the other two give the entry. For an empty own entry, `message_entry` gives `""` and `said` gives the body. For the walk shape `m_p1` with the entry `e_p1` in its refs, `said` gives `""` and the other two give the words. For a legacy `entry:` key, only `said` reads it. Fix: make `message_entry` and `_recent_chat` call `said`, and make `said` read an entry that the refs name.
6. **tests/rota/test_w7_his_words.py 122 to 125, low. CONFIRMED.** The pin catches the brief's literal only. It stays green on `SELECT id, body_text FROM messages WHERE id = ?`, which is the shape of a new door read of the trigger. It also stays green on lower case SQL, on `SELECT *` with `row["body_text"]`, on a module level constant, on `from_role='principal'` with no spaces, and on an f-string column. Three live readers of his words escape it: `api.py` 687 through `message_entry`, `runner.py` 2640 in `_recent_chat`, and `runner.py` 2412 (finding 7). Fix: match `body_text` with `FROM messages` in any order and in any case, and keep an allow list of the readers of a seat's body.
7. **rota/core/runner.py 2412, low. PLAUSIBLE.** The landing block gives the seat `"reply": row["body_text"] or ""`. A park clarify page takes this branch, and his answer to a clarify lands on the verdict path with no body. So the seat can read an empty reply in the landing block, the W7 shape. The `principal_said` key at runner.py 2073 holds the words, which lowers the cost. No probe ran. Fix: read the reply with `said(conn, trigger)`.
8. **rota/roles/principal.py 3121 to 3126, low. CONFIRMED.** The verdict path of `land` keeps `answer.text` without a strip, and the reply path strips it. A keypress with the text "   " gives `said` the value `"   "`, which is not empty, so `_earlier_answers` keeps it as an answer. `parse_reply` strips the text, so only a direct caller of `land` reaches this. Fix: strip the text before `record_entry` on the verdict path.

Outside the points: findings 5, 7 and 8 are outside the numbered points. Finding 5 also bears on point 1, and finding 6 answers point 6.

### Point 1, the shapes

| Shape | verb | body_text | entry | said |
|---|---|---|---|---|
| present answer with words | converse | his words | his words | his words |
| confirm answer "  no, not that  " | converse | `no, not that` | `no, not that` | `no, not that` |
| clarify answer "  the options one  " | converse | NULL | `the options one` | `the options one` |
| keypress, no text, on each verb | verdict | NULL | none | `""` |
| keypress, text "   " | verdict | NULL | `"   "` | `"   "` |
| None, or a missing id | | | | `""` |

On one message, `entries` and `body_text` disagree when a seeded body and a later entry differ. `said` then returns the entry. When the entry is empty, `said` returns the body. `land` writes no such pair.

### Point 2, the replay

The harness is the p2f replay with this review's register copies. It replays 240 calls at the parent 2b1ef4c9 and at the head.

| Night, session | Trigger | Parent refusal | Head refusal | Right? |
|---|---|---|---|---|
| 170 and 171 s92, 4 calls | m7 | act span, or lines with no ruling | line 29 words hold the page text "Your answer ..." | yes, the page text is not his |
| 171 s139, 2 calls | m41 | lines with no ruling, or the naming refusal | "add a check ..." cuts "Please" off his clause | yes by the rule, and strict |
| 171 s177, 5 calls | m67 | read-back line, or lines with no ruling | line 1 words "lines 1, 3, 4 and 5 are right" paraphrase "so are lines 1, 3, 4 and 5" | yes |
| 172 s91, 1 call | m7 | read-back line | line 21 words "approve line 21" | yes |
| 172 s214, 1 call | m93 | the naming refusal | the cut sentence of p2f | yes |

The 9 clarify answers with no body are 170 m14, m33, m86, 171 m14, 172 m31, m44, m55, m68 and m118. Each recorded call passes `words`, and each lands the same rows at both trees. With `words` dropped, the parent refuses all 9 with "words is empty". The head lands 6: the 5 answers that open with "Yes" and m44 with its contests. The head refuses m33, m86 and m55 with the new guard.

### Point 4, the sites

| Site | Change beyond "his words are now read" |
|---|---|
| 1 `reading_line` | none. The 5 night 172 pages quote his words at the head and `""` at the parent |
| 2, 3 `_his_reply`, `_faulted_by_his_words` | none. The callers build refusal texts and see his words on a clarify answer |
| 4 `rulings_rule` | yes. An empty `words` is now filled on a clarify answer, so "words is empty" no longer fires there (finding 1) |
| 5 act span | none. A clarify answer's span now resolves to the trigger |
| 6 `returned_line` | none. It now names a line from a clarify answer |
| 7 `_earlier_reading`, `_earlier_sources` | none. A verdict path answer with words now counts. `verb = 'converse'` still drops keypresses |
| 8 runner earlier exchange | none. His turn is kept when `said` is not empty, and a Liaison turn when its body is not NULL |
| 9 sandbox quote check | none. It read `entries` before, and it reads them now |
| `_words_from` | none. `_holds_span` folds as the old code folded |

The four sites that filtered `body_text IS NOT NULL` keep the same rows for a reply path message. They add a verdict path answer only when it has words.

### Point 6, the plants

| Plant in a copy of api.py | Pin |
|---|---|
| `SELECT body_text FROM messages WHERE id = ?` | RED |
| `SELECT id, body_text FROM messages WHERE id = ?` | green |
| the same in lower case | green |
| `SELECT * FROM messages ...` then `["body_text"]` | green |
| a module level constant | green |
| `... WHERE from_role='principal'` with no spaces | green |
| `f"SELECT {col} FROM messages ..."` | green |

### Point 8, the clause rule on m129

Refused: "No.", "call line 4 wrong.", "Line 4 is wrong too.", "line 4 wrong", "so keep line 4", "asked for that fix and did not call line 4 wrong". Passed: "did not call line 4 wrong" with and without a full stop, "keep line 4 as it is" with quotes or a full stop, "Line 11 is wrong, my answer asked for that fix". On a reply with a colon, curly quotes and a curly apostrophe, his words pass with a comma for the colon, with straight quotes and with a straight apostrophe. "Roaming" alone and "Line 3 is wrong; it says" are refused. In the door, a line object or an acts entry with no act and the words "Line 4 is wrong too." or "call line 4 wrong" is refused. His clause "keep line 4 as it is" lands.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/77c8dc39-1322-4ba4-bcb6-9a1031822837/scratchpad/p7r/`.

- `db/`: copies of `clickI_night170.db`, `clickI_night171.db` and `clickI_night172.db` with their `-wal` and `-shm` files. Every probe opened a copy, most of them through `backup` into memory.
- `parent/` and `head/`: `git archive` of 2b1ef4c9 and 0ae7ab54.
- `replay.py`, `cdiff.py`: the p2f replay of 240 calls at each tree, with `par.json` and `new.json` (point 2).
- `nobody.py`, `replay_nowords.py`: the 9 clarify calls as recorded and with `words` dropped, in `nw_parent.json` and `nw_head.json` (point 2, finding 1).
- `probe1.py`: `said` on each shape that `land` writes, the walk shape and two seeded disagreements (point 1, finding 8).
- `probe3.py`: the term collision scene at each tree. It holds the pinned case, `words` equal to his reply, a contest with an approve, a hidden column and a plain-word ref id (point 3, findings 1 and 2).
- `probe6.py`, `pinrun/`: seven plants in a copy of `api.py`, with the pin pointed at the copy (point 6).
- `probe8.py`, `probe8b.py`, `probe8d.py`, `probe8e.py`: the clause rule, the nested shapes and the two kept deviations on m129 (point 8, findings 3 and 4).
- `probe_rl.py`: `reading_line` on the five night 172 pages at each tree (point 1).
- `probe_readers.py`: `said`, `message_entry` and the `_recent_chat` order on four shapes (finding 5).
- Tests: the 36 files that the diff touches or that name `rulings.rule`, then `python -m rota.tools.gate` once. The gate stored a baseline at 0ae7ab5 in the ignored `.rota-gate.json` of the worktree, because the worktree had none.
- Three probes hold a backslash in a quoted heredoc. Each output shows that the backslash survived.

## (d) Usage

Input about 140k tokens, output about 20k tokens, about 160k in total. These are estimates from the session count, because the harness shows no per-call counts. The cap was 70k, and the replay, the gate and the probes used the rest.

# p2

Review p2 of passes 1c and 1d, 0ae7ab54..3b31077a, in `C:/Users/roman/rota_r7` at 3b31077a. No tracked file was edited.

**Verdict: NOT READY.** The two highs of p1 are closed, and so is finding 3. The new backing rule has two new high holes on a clarify page, which has no line order. One shared content word backs a verdict even in a question or a negated clause. One backed verdict also carries an unbacked contest. Two findings are high and two are low.

## (a) The verdict on each point

1. The p1 highs: CLOSED. All seven probes of `probe3.py` now refuse. The question passed as `words`, the contest beside an approve, the hidden column and the plain-word id each give "His words neither approve nor name ...".
2. The replay: 4 of 240 results move against 0ae7ab54, and 13 move against the parent. Every move goes from one refusal to another refusal, and no land moves. Each new text is right on his words. The 9 recorded clarify calls still land.
3. Law 6 on the backing rule: FAIL, high. On a clarify page, an approve lands on a row that his words refuse, and "fine" carries a contest (findings p2-1 and p2-2). On the numbered page m129, the read-back and agreement doors still refuse every probe.
4. The lead-word rule: PASS on the closed list, with a low finding on the -ly rule (finding p2-3). A lead word inside a clause makes no cut. A clause that is only a lead word, "Now." or "Please", passes, and it backs no verdict.
5. The tests: PASS. The 38 files give 1 failed and 1010 passed, and the red is the known `test_pins.py` test. The gate gives 6 failed and 5834 passed, with 0 new reds against the baseline at 0ae7ab5. The 6 reds are the known set. The diff holds no CR byte, and every hunk is in the claim. One test edit changes what the test pins (finding p2-4).

## (b) Findings

- **p2-1. rota/roles/api.py 11956 to 11966, high. CONFIRMED.** `_names_shown` backs a verdict when his words share one content word with the text that the page showed for the row. The rule does not read a question or a negation. On the clarify page, g1 shows "group: a set of related options" and g2 shows the command sense. The question "what is a group anyway" lands approves on g1 and g2, because both rows show "group". The reply "the options one, not the command one" lands an approve on g2, which is the sense he refused. "the options one is fine" backs a contest of g1. The parent lands these calls when `words` is passed, so p2-1 is a hole that the new rule claims to close, not a regression. Fix: count only a word that one row shows and the other rows do not show, and back nothing from a question or from a clause that negates the word.
- **p2-2. rota/roles/api.py 12014 to 12019, high. CONFIRMED.** One backed verdict lets every other verdict of the call land, contests included. The stated rule lets only an approve of an unnamed row ride beside a backed verdict. On the reply "fine", the call g1 contest with g2 approve lands, because "fine" backs the approve, and nothing faults g1. With two contests, the same reply is refused. Fix: require each contest and each revise to be backed on its own, and let only an approve ride.
- **p2-3. rota/roles/api.py 11888, low. CONFIRMED.** Any word that ends in -ly at a clause start opens a new clause, so the seat can drop a hedge or a negative adverb. "any of line 3 is right" passes for his "Hardly any of line 3 is right.", which inverts his meaning. "line 4 is wrong" passes for "Possibly line 4 is wrong.", and "line 4 is right" passes for "Only line 4 is right.". "the patch to line 2" passes for "Apply the patch to line 2.". Fix: remove the -ly suffix test and name the lead adverbs in `_CLAUSE_LEAD`.
- **p2-4. tests/rota/test_frame234_verdict_lines.py 154, low. CONFIRMED by reading.** `test_a_clarify_is_not_read_for_lines` now passes "Lines 1 to 4 are wrong." in place of "Lines 1 to 4 match what I asked for.". The words now back the contests, so the test no longer shows that a clarify is not read for lines. Fix: rename the test, or keep the agreeing words and expect the new refusal.

Open from p1: findings 4 to 8 are outside the claim of 1c and 1d, and they stay open.

## (c) The replay moves

Against 0ae7ab54:

| Night, session | Trigger | 0ae7ab54 refusal | 3b31077a refusal | Right? |
|---|---|---|---|---|
| 171 s139, 2 calls | m41 | words cut "Please" off his clause | lines 1 and 4 have no ruling, and the naming refusal, as at the parent | yes, "add a check ..." is now his clause after "Please" |
| 171 s171, 2 calls | m63 | lines with no ruling, and the fault on line 6 | the act span "look for backslashes like the roaming check" is not his | yes by the clause rule. The span cuts "change the check to look for ...", and the call needs one more turn |

Against the parent, the 13 moves are the 13 moves of p1 with s139 gone and s171 added. These are s92 four times, s171 twice, s177 five times, s91 once and s214 once. Each is right on his words, as point 2 of p1 says.

## (d) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/77c8dc39-1322-4ba4-bcb6-9a1031822837/scratchpad/p7r/`.

- `head3/`: `git archive` of 3b31077a.
- `probe3.py` at `head3/`: the p1 highs (point 1).
- `replay.py` to `new3.json`, and `cdiff2.py` against `new.json` and `par.json` (point 2).
- `probe_p2.py`: the backing rule on the term collision clarify page, `_line_reading` of "fine", and 14 lead-word cases (points 3 and 4).
- `probe_p2b.py`: the backing rule on the m129 numbered page (point 3).
- `gate3.txt`: the gate output. The 38 test files ran with pytest (point 5).

## (e) Usage

Input about 40k tokens, output about 9k tokens, about 49k in total for p2. These are estimates from the session count. The cap was 40k.

# p3

Review p3 of pass 1e, 3b31077a..9923a021, in `C:/Users/roman/rota_r7` at 9923a021. No tracked file was edited.

**Verdict: NOT READY.** Pass 1e closes p2-2, the question that ends with "?", the negated clause "not the command one", "Hardly" and "Only". The name rule still backs a verdict whatever the clause says about the name. On a clarify page, an approve lands on "the command one is wrong" and on "I do not like the command one". A contest lands on "the options one is fine". Two findings are high and one is low.

## (a) The verdict on each point

1. The p2 probes: the question, the negated clause and the contest beside "fine" now refuse. "Hardly" and "Only" keep their hedge. "the options one is fine" still backs a contest of g1 (finding p3-2). "Possibly", "Probably" and "Supposedly" still drop off (finding p3-3).
2. The judgement cases: each leaves a law 6 hole on a clarify page. The negation rule does not read a fault word, a negated verb, or a question with no "?" that opens with "when" (finding p3-1). The choice rule backs a contest of g2 on "the options one confuses me", which chooses nothing (finding p3-2). The numbered page holds: on m129 with the reply "Line 11 is wrong. Line 3 is fine. Lines 9 and 10 are right.", a contest of line 3 and a contest of line 5 are each refused by the line doors.
3. The replay: 0 of 240 results move against 3b31077a. Against the parent, the 13 moves of p2 stay, and each is right on his words.
4. The tests: PASS. The rename removes a clash: `_content_words` at api.py 906 is an older helper that `test_frame193_pass3.py` tests. The 39 files, which include `test_frame193_pass3.py`, give 1 failed and 1040 passed, and the red is the known `test_pins.py` test. The gate gives 6 failed and 5838 passed, with 0 new reds against the baseline at 0ae7ab5. The diff holds no CR byte, and every hunk is in the claim. The test rename of p2-4 is done.

## (b) Findings

- **p3-1. rota/roles/api.py 11961 to 12000 and 12031, high. CONFIRMED.** `_shown_mention` gives "named" for any mention that no direct negation governs, and a "named" mention backs an approve. On the clarify page, both approves land for "the options one is right, the command one is wrong". The approve of g2 lands for "I do not like the command one", because "like" stands between "not" and "command". Both approves land for "when does the group meet", because `_QUESTION_OPEN` has no "when", "where", "who", "should" or "could". The approve of g2 lands for "Not the command one. The command one confuses me.", because the second sentence counts as a positive mention. Fix: back an approve by a name only when the clause that holds the name reads as an agreement or a choice by `_line_reading`, and back nothing from a clause that faults or negates.
- **p3-2. rota/roles/api.py 12031 and 12082 to 12086, high. CONFIRMED.** A name backs a verdict in either direction, so a name backs a contest. "the options one is fine" lands a contest of g1. `chose_other` reads any positive mention of g1 as a choice, so "the options one confuses me" lands an approve of g1 and a contest of g2. Fix: back a contest by a name only when the clause that holds the name faults, and count a mention as a choice only in a clause with no fault word and no complaint.
- **p3-3. rota/roles/api.py 11875 and 11891, low. CONFIRMED.** `_HEDGES` lists six words, and every other word that ends in -ly is still a lead word. "line 4 is wrong" passes for "Possibly line 4 is wrong." and for "Probably line 4 is wrong.". "the docstring is fine" passes for "Supposedly the docstring is fine.". Fix: remove the -ly suffix test and name the lead adverbs in `_CLAUSE_LEAD`, as p2-3 said.

Open from p1: findings 4 to 8 stay open, outside the claim of 1e.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/77c8dc39-1322-4ba4-bcb6-9a1031822837/scratchpad/p7r/`.

- `head4/`: `git archive` of 9923a021.
- `probe_p3.py`: the p2 probes, five hedges and six judgement cases on the term collision clarify page (points 1 and 2).
- `probe_p3b.py`: three contests on m129 with his reply set to "Line 11 is wrong. Line 3 is fine. Lines 9 and 10 are right." on a copy (point 2).
- `replay.py` to `new4.json`, and `cdiff2.py` against `new3.json` and `par.json` (point 3).
- `gate4.txt`: the gate output. The 39 test files ran with pytest (point 4).

## (d) Usage

Input about 22k tokens, output about 6k tokens, about 28k in total for p3. These are estimates from the session count. The cap was 25k.
