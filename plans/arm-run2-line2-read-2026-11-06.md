# Arm run 2: "Line 2" in the Developer's start push, a read before any fix, 2026-11-06

Written 2026-11-06 13:09 (observed: `date`). Read only. No model call. The probes are in `C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/8b2312ef-0b14-4322-a20c-908058cac23b/scratchpad/l2r362/` (below: `L2R`). The run database is `ARM/runs2/dry6b.db`, with `ARM` = `.../8b2312ef-.../scratchpad/arm362/`, opened `mode=ro`.

## Result

- **The premise holds only in part.** s154's commit subject says "Fix line 2 in string.py". Its edit does not touch line 2 of `string.py`. It rewrote lines 118 to 156, the span of `_foldline`, with the same body, and the line `foldline = deprecate_for_version_8(_foldline)` came out twice. The 3 added lines are a blank line, a blank line and that duplicate. No behaviour changed (observed: `git diff 99619246 60127d92` in `ARM/icalendarI2`, and s154 turn 3).
- **What the seat was shown.** The first key of every turn of s153 and s154 is `[the principal's words on this change, newest last]`. It holds his reply verbatim and one legend line: "On his page, line 2 is wrong: rewrite. The line was the team's guess at the code this touches, guess:folds_long_lines_in_icalendar." (observed: `L2R/turns/s153_01.txt` line 120 to 122, `s154_01.txt` line 121 to 123).
- **The legend gave line 2 its referent, and it gave a closed contest as an open order.** s147 had already rewritten the guess with his two files, stamped `m28`, before the batch existed. The legend does not say so. It also does not say that the guess is the Architect's row and not the Developer's work (observed: the session order; reasoned: `_line_legend` reads no owed state and no owner).
- **The mechanism** is `_line_legend` in `rota/core/runner.py` 692 to 771, called by `_ruled_block` 4435 to 4486, which the start push puts first at 4690 to 4704. The start push came from frame 312 (`6785f35b`, 2026-10-24). The legend came from frame 306 (`f1580938`, 2026-10-25). Frame 362 gave both their form today (`b9f269aa` and `dbcbdf2e`, 2026-11-06 09:17 and 09:30).
- **No unbuilt proposal covers this issue.** The `lines:<ask>` stamp, the file-line rule and the ordinals in the push reports address other faults. Frames 357, 358, 360 and 361 do not name it.
- **Reach.** In the code: 10 site groups put his words before 5 non-Liaison seats. 6 groups add a legend through `_line_legend`. 4 groups show the raw words with no legend. In 6 recorded databases: 16 of 68 replies hold a page line number, and 61 non-Liaison sessions were shown one, 34 with a legend line and 27 without. 3 seat writes bind a page line to the wrong thing.
- **Proposal.** `_line_legend` states two more facts for each page line: whose row it is, and whether the team already acted on his verdict there. The one inbound render, runner 1096 to 1108, puts the same legend beside `principal_said`. His words stay verbatim. Price: 3 to 4 cycles.
- This is one sample of one turn at temperature 0. It gives no rate.

## 1. Find: what each seat was shown and what it did

### 1.1 The order of the sessions after his reply m27

| session | role | wake | his words in the first prompt | legend line |
|---|---|---|---|---|
| s145 | architect | message `relay` m29 | `"principal_said"` in the message JSON | no |
| s146 | vision_keeper | message `relay` m30 | `"principal_said"` | no |
| s147 | architect | `tick:guess`, refs `[item, m28]` | `"principal_said"` | no |
| s148 | vision_keeper | `tick:slicing` | `[the principal ruled on this item, newest last]` | yes |
| s149 | terminologist | `tick:criteria` | the same key | yes |
| s151 | architect | `tick:annotate`, refs `b1` | `[the item's guess]`, `"the principal said"` | no |
| s153 | developer | `tick:batch_start` | `[the principal's words on this change, newest last]` | yes |
| s154 | developer | `tick:batch_start`, attempt 2 of 3 | the same key | yes |
| s155 to s172 | tester, developer, others | `tests_missing`, `tests_failing`, `exhausted`, messages | none | none |

(observed: `L2R/sess.py`, and a count of "Line 2 is wrong" in each first prompt.)

### 1.2 The start prompt of s153 and s154, verbatim

The user prompt of s153 turn 1 starts as follows. s154 adds one line after `Refs: b1`: "This is attempt 2 of 3 on this wake. The earlier attempt did not clear this wake, so the same answer will not clear it. Do something the earlier attempt did not." (observed: `s154_01.txt` line 117).

```
You were woken by: tick:batch_start
Refs: b1

Already run for you, with the results below. Calling any of these again returns the same thing and costs you a turn:

[the principal's words on this change, newest last]
His answer m27 to page m26: "Line 2 is wrong. The fold is _foldline in src/icalendar/parser/string.py, and its tests are in src/icalendar/tests/test_icalendar.py. Do not touch parameter.py or property.py."
On his page, line 2 is wrong: rewrite. The line was the team's guess at the code this touches, guess:folds_long_lines_in_icalendar.
```

The keys after it, in order: `[batches.expect]` with `"expected to touch": ["src/icalendar/parser/string.py", "src/icalendar/tests/test_icalendar.py"]`, `[criteria.load]` with c1 and c2, `[the constraints that bind the files of this batch]`, `[glossary.lookup]` and `[tickets.load]` (observed). The block repeats unchanged in all 19 prompts of s153 and all 3 of s154 (observed: a grep over `L2R/turns/`).

Other line numbers stand near his "Line 2". These are lines of files. The bound block says "src/icalendar/tests/test_icalendar.py line 9", "test_parsing.py line 16" and "src/icalendar/parser/string.py line 122". The `code.source` answers give `defs` maps such as `'_foldline': [118, 156]`, with "defs maps each top-level name to its [start, end) lines" (observed: `s153_01.txt` line 133, `s154_03.txt` line 134). So the prompt uses "line N" for a page line once and for file lines four times (reasoned).

### 1.3 What s153 sent and what the doors answered

- Turn 1: `code.probe(pattern='string.py')`, then `code.source` of `string.py` 0 to 400 and of `test_icalendar.py` 0 to 200. So the seat opened his file first (observed).
- Turns 2 to 17: `code.source` of the same two files again and again, once with `glossary.lookup(term='fold')`.
- Turn 18: `code.write(path='src/icalendar/parser/string.py', text='''\n# This file is intentionally left empty to avoid conflicts.\n''', start=0, end=-1)` and `code.commit(message="Fold long lines in icalendar output without splitting words")`.
- The runner's account: "code.write: this rewrite of src/icalendar/parser/string.py drops _escape_char, _unescape_string, validate_token, ..." and "code.source was refused the same way in four turns; the session ended on it" (observed: `s153_20.txt`).

s153 wrote nothing. Its commit message does not name a line.

### 1.4 What s154 sent and what the doors answered

- Turn 1: `code.probe(pattern='string.py')`, `code.source` of `string.py` 0 to 400, of `test_icalendar.py` 0 to 100.
- Turn 2: `code.source(path='src/icalendar/parser/string.py', start=118, end=160)` and `test_icalendar.py` 0 to 200. The door answered `defs: {... '_foldline': [118, 156] ...}` (observed: `s154_03.txt` line 134).
- Turn 3: `code.write(path='src/icalendar/parser/string.py', text='def _foldline(...) ... return fold_sep.join(folded_lines)\n\n\nfoldline = deprecate_for_version_8(_foldline)', start=118, end=156)`, then `code.commit(message='Fix line 2 in string.py to use _foldline as per principal instruction')` (observed: `tool_calls` seq 11 and 12).
- The receipt: `batches b1 version 2` (observed: `receipts`).

The 3 added lines. The text of the write is the body of `_foldline` byte for byte, plus the line `foldline = deprecate_for_version_8(_foldline)`. The span `[118, 156)` ends before that line, so the line stays in the file and the write adds a second copy (observed: `git diff 99619246 60127d92` gives `+foldline = deprecate_for_version_8(_foldline)` and two blank lines). Line 2 of `string.py` is the blank line after the module docstring, and nothing changed there (observed: `git show 99619246:src/icalendar/parser/string.py`).

So "line 2" lives only in the commit subject (observed). The edit acts on "The fold is _foldline", read as "use _foldline" (reasoned: the subject says "to use _foldline as per principal instruction", and the edit rewrote `_foldline` unchanged). The pressure line "Do something the earlier attempt did not" stood in the same prompt (observed).

### 1.5 What the later seats did with his words

None of them saw his words (observed: 0 matches of "Line 2 is wrong" and of "Do not touch parameter.py" in every turn of s155 to s172).

- s155, Tester, `tick:tests_missing`: `tests.triage` and `tests.encode` from criterion c1. It wrote `tst_c1_line_folding` (observed: `receipts`).
- s156, s157, s160, s170, s171, Developer, `tick:tests_failing`: `code.source` of `string.py` many times, then a run of `msg.challenge_tester` on inherited tests. None of them wrote `string.py` (observed: `tool_calls`).
- s161, Developer, `tick:exhausted`: `msg.question_vision_keeper`.
- s163, Developer, message `answer`: a `code.write` on the Tester's file `test_icalendar_c1.py` and a commit.
- s169, Tester: a test from c2.

The criteria and the tests carry the change from here. His words drop out of every prompt after the start (reasoned: the start push is the only Developer push of `START_RULED_KEY`, runner 4690).

## 2. Purpose and provenance

### 2.1 The mechanism

1. `push_working_set`, runner 4690 to 4704: on `developer` and `tick:batch_start`, it calls `_ruled_block(conn, api.batch_ruled_refs(conn, bid), item=...)` and puts the result first as `START_RULED_KEY`.
2. `_ruled_block`, runner 4435 to 4486: each landed ruling once, as `His answer <m> to page <p>: "<words>"`, then `_line_legend(conn, rid, words, contested_text=False)`.
3. `_line_legend`, runner 692 to 771: for each page line his words name and the ruling holds a reading row for, "On his page, line N <read-back verdict>: <act>", then the line's kind and id. With `contested_text=False`, a line he did not approve shows its kind and id and not its text, from `_line_kind` 779 to 790: "the team's guess at the code this touches, ".

The legend reads `seen_order`, the ruling's reading rows and the stamp. It reads no owed state and no owner (observed: the code). So a contest that the Architect closed at s147 reads the same as an open one.

### 2.2 The provenance

| commit | date | frame | purpose, from the message |
|---|---|---|---|
| `6785f35b` | 2026-10-24 21:45 | 312 | "The stopped page says that his answer starts the team once more and that the team reads his words." The start wake pushes his landed words that name the batch, "so the Developer sees what the door will accept." |
| `f1580938` | 2026-10-25 03:06 | 306 | "His page line numbers reached seats that never saw the page." Night 165's s359 read "remove both lines" as docstring lines and cut 17. One legend line for each page line his words name, "His words stay verbatim." |
| `d76524ad` | 2026-11-06, before 08:51 | 362 | Push his whole reply once with the page lines it names (push report 1). |
| `b9f269aa` | 2026-11-06 09:17 | 362 | His words at the front. The legend starts with the read-back's words for his verdict, "as 'line 2 is wrong: rewrite'". |
| `dbcbdf2e` | 2026-11-06 09:30 | 362 | His words are the first key. "A push no longer shows the text of a line that he did not approve. The legend names the kind of the line and its id." |

(observed: `git show -s` in `C:/Users/roman/rota_p362a`; `dbcbdf2e` is an ancestor of the run's `822311e0`, and `3b209833`, the recorded turn's code, holds `6785f35b` and `f1580938` but not `dbcbdf2e`.)

The ruling behind the form: composition line 106, "The verbatim words and the confirmed reading are two records" (ruled: Roman, ratified 2026-09-16). The legend's docstring cites it.

### 2.3 Did the build meet the condition of its own design

- Frame 362's push measure asked "does the Developer open the file that he named". At `86ca7e23` it gave 0 of 10, because the touch set still named `property.py` (observed: `plans/f362-push-measure-2026-11-06.md`, result). On this arm, with slice 1's guess, the condition holds 2 of 2: s153 and s154 each sent `code.probe(pattern='string.py')` first (observed: section 1.3 and 1.4).
- Frame 306's purpose was a referent for a page line number. The legend gave the referent here (observed). It did not stop s154 from naming "line 2" as its own work (observed: the subject). Frame 306's design did not ask whether the seat owns the row or whether his verdict on it is still open (reasoned: `f1580938` names the repair wake, where the woken seat owns the criterion, and the start push reuses it for a seat that owns none of the named rows).
- Frame 312's purpose, "the Developer sees what the door will accept", is met in form (observed: the block is present on every turn).

## 3. What the code already holds: line number to row, for a seat that never saw his page

| place | what it does | readers |
|---|---|---|
| `_line_legend`, runner 692 to 771 | one legend line for each named page line, beside the verbatim words | 3 callers: `_last_word_lines` 630, `_contest_block` 921, `_ruled_block` 4467 |
| `_words_on_rows`, runner 656 to 689 | keeps only the sentences of his words whose line numbers name the woken rows | `_last_word_lines` 629, `_contest_block` 917 |
| `_FILE_LINE`, runner 774 to 778 | drops "line N of <file>" before the legend reads line numbers | `_line_legend` 721 only |
| `_line_kind`, runner 779 to 790 | the kind words of a line: guess, criterion, item, note, batch | `_line_legend` |
| `_page_named_lines`, runner 2838 to 2860 | rewrites "Line 2" in the text as "row <ref> of page <page>" | `_recent_chat` 2920, the Liaison only (`c22e8162`, 2026-10-23) |
| `_line_reading`, `rota/roles/api.py` 14313 to 14330 | the line parser | 23 callers, most of them the Liaison's landing doors |

(observed: `python -m rota.tools.map fn <name>` at `822311e0`.)

`_page_named_lines` is the only place that replaces the number in the text. It serves the Liaison, who composes the pages. Every other seat gets the number verbatim, with a legend or with nothing (observed).

## 4. Match against the unbuilt proposals and the open frames

- Push report 2, section 6, and open question 2: the send door stamps `lines:<ask>`, so a legend shows the line he read. It fixes stale line text (S3). It does not tell the seat that the row is closed or not its own. Not a cover (reasoned).
- Push report 2, section 8: `_line_reading` reads "line 5 of string.py" as page line 5 in 22 callers. That is the opposite direction, a file line read as a page line. Not a cover.
- Push report 2, pass 3, open: ordinals ("both lines") give no legend. Not a cover.
- Push report 1, open question 2: a frozen text for a batch line. Not a cover.
- Frame 357, a landed drop on a statement. Frame 358, a re-survey present after a merge. Frame 360, an item the code already satisfies. Frame 361, a large observed-entries page. None names a page line number in a seat prompt (observed: the head and the last status lines of each, `plans/stack.md` 1830, 1855, 1893, 1921).

No unbuilt proposal covers this issue (reasoned: the list above).

## 5. Reach

### 5.1 In the code

His words reach a seat that never saw his page at 10 site groups (observed: the code at `822311e0`).

With a legend, through `_line_legend`:

1. Developer, `tick:batch_start`: `START_RULED_KEY`, runner 4690 to 4704.
2. Terminologist, `tick:criteria`: `RULED_KEY` through `_item_ruled`, runner 4817.
3. Vision Keeper, `tick:slicing`: `RULED_KEY` as a map by item, runner 4908.
4. Developer and Tester, every wake that pushes `criteria.load`, for a contested criterion: `_contest_block`, runner 4677 to 4686.
5. Terminologist, message `relay`: `_relay_contest_block`, runner 925 to 950, rendered at 1111.
6. `tick:criterion_repair`: `_last_word_lines`, runner 600 to 653, rendered at 1073.

With no legend, the raw words as `principal_said`, rendered as JSON at runner 1096 to 1108:

7. Every message wake whose trigger has an entry: `resolve_inbound` 2246 to 2248, with the carried verdicts at 2316, the principal's resolved refs at 2393 and 2433, and the earlier clarify answers at 2475.
8. `tick:contested`: `_resolve_contest`, runner 2800 to 2835.
9. `tick:guess` and `tick:annotate` with two refs: `_resolve_owed`, runner 2760 to 2799.
10. `"the principal said"` in the guess seed, runner about 4318 to 4349, under `[the item's guess]` (observed: s151).

The seats: Developer, Tester, Terminologist, Vision Keeper and Architect, 5 of the 6 non-Liaison seats. I found no Critic site. The door answers at `api.py` 1795 and 1976 also carry `principal_said`, and I did not read them.

### 5.2 In the recorded runs

A reply counts when `api._line_reading` finds a page line in it. A session counts when its first prompt holds the first sentence of such a reply, and the Liaison is left out (observed: `L2R/reach.py`, `L2R/reach_out.txt`).

| database | replies | with a page line number | non-Liaison sessions shown one | with a legend line |
|---|---|---|---|---|
| `.rota/dry1.db` | 28 | 7 | 38 | 29 |
| `.rota/dry2.db` | 10 | 2 | 0 | 0 |
| `.rota/dry3.db` | 6 | 1 | 1 | 0 |
| `.rota/dry4.db` | 7 | 1 | 2 | 0 |
| dry6b `runs/dry6b.db` | 10 | 4 | 12 | 1 |
| arm run 2 | 7 | 1 | 8 | 4 |
| **total** | 68 | 16 | 61 | 34 |

By wake on dry1: Developer `tests_failing` 10, Tester `challenge` 9, Developer `batch_start` 7, Vision Keeper `tick:contested` 6 with no legend, Tester `answer` 5, Terminologist `relay` 3, others 5. On dry6b: Architect `relay` 5 with no legend, Developer `batch_start` 5 with no legend (older code), others 2.

The recorded writes that bind a page line to the wrong thing, 3:

- arm run 2 s154: the commit subject "Fix line 2 in string.py ..." (observed).
- dry6b s156: the ledger note `l_67170b6f26`, "The principal said "Line 2 is wrong." This refers to the second criterion (c_2) which forbids hyphenated word breaks." (observed).
- dry6b s155: three `ledger.log` calls of kind `fault`, "The principal said "Line 2 is wrong." but no lin..." (observed: `tool_calls`, cut at 160 characters).

The dry6b cases ran `3b209833`, before the legend's form of `dbcbdf2e` (observed: section 2.2).

## 6. Proposal

**Site: `_line_legend`, runner 692 to 771, and the inbound render, runner 1096 to 1108.**

1. `_line_legend` adds two facts after the kind and id of each line. First, whose row it is: the guess and the batch are the Architect's, a criterion is the Terminologist's, the item is the Vision Keeper's. Second, whether the team acted on his verdict there after his reply. For a guess line, `scheduler.owed` gives the open contest, and touch rows stamped with the ruling's verdict id give the act. For a criterion or an item, a version newer than the ruling gives it. An example: "The Architect rewrote this line after his answer. It is not work for this session."
2. The clause about "this session" shows only when the woken seat does not own the row. On the repair wake, the woken seat owns the criterion, so frame 306's form stays.
3. The inbound render adds the same legend lines below the JSON when `principal_said` holds a page line number and the ruling has a recorded order. This covers sites 7 to 9 at one place. Site 10 needs one call where the seed is built.
4. His words stay verbatim at every site. The legend stands beside them, as composition line 106 says (ruled: 2026-09-16).

Why this place: one function renders a page line for 6 of the 10 sites, and one render prints the raw words for 3 more. The facts come from rows that exist: the ruling, the owed state, the stamps and the versions. Nothing in it names icalendar, a file or a seat of this run (reasoned).

Price: one build pass on Opus, about 60k to 80k, a review, and one fix pass. 3 to 4 cycles (reasoned: a render change with tests, by the anchors of `plans/operating-facts.md`).

Cost on a correct run: one clause of about 60 to 120 characters for each legend line. The 21 recorded pushes hold 12 legend lines, so about 1,400 characters in all. The inbound sites add one line for each named page line, about 130 characters on s145, s146 and s147. No new wake and no model call (reasoned).

Measure with no model:

1. On a copy of the arm run 2 database, the start push of `b1` shows the done clause and the owner clause on line 2. The relay of s145 and the `tick:guess` of s147 show a legend.
2. Replay the 21 recorded pushes and the 61 recorded sessions of section 5.2. Count the legend lines on a closed contest that carry the done clause, toward all of them.
3. A test with an open contest shows no done clause.

Measure with a model: replay s154's three prompts OLD and NEW on `qwen3.5:9b` at temperature 0, as the push measure did. Count commit subjects and ledger notes that cite "line N" as the session's work, and diff the write against the base. Then, on the next 3 dry runs, count seat writes that cite a page line number as their work, from 3 recorded toward 0.

## 7. My doubt

- One sample at temperature 0. One reply of one seat gives no rate.
- The cause is not shown. The edit acted on `_foldline`, not on line 2. The pressure line "Do something the earlier attempt did not" and the write span that doubled a line may drive s154's commit more than the legend did. The proposal can fix the subject and leave the no-op edit. The model replay of section 6 is the test of that.
- The failure that parked the run is a change with no behaviour, under criteria that stated the behaviour. That is a separate wall, and I did not read it.
- The session count matches the first sentence of a reply in the first prompt only. A legend line may belong to another reply. arm run 2 is a copy of dry6b, so m27 counts twice.
- I did not read the Developer's brief files, the Critic's prompts, or the door answers at `api.py` 1795 and 1976.
- I did not check that `scheduler.owed` and the stamps can give the done fact for every kind of line. A batch line and a team note may have no such record.
