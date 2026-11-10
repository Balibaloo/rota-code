# The read of mass 6: the session, 38 drawn sessions, 2026-11-10

One reader, no hypothesis, primary records only. `T` is
`C:/Users/roman/AppData/Local/Temp/claude/`. The scripts and their raw
output are in `T/6d9eb18c9e6274ab/1efd37b1-058e-4b19-8ab1-e1a6c654a389/scratchpad/mass6/`
(`extract.py`, `after.py`, `counts.py`, `q1.py` to `q9.py`). All database
reads used `mode=ro`. Git reads on the sample repositories were read only.

## Result

All 38 drawn sessions committed, and each was woken by one message or one
predicate and ran one mode brief (observed: `sessions`, `turns.system`). In
182 turns the doors accepted 267 calls and refused 182, and the Architect took
116 of the refusals and the Critic none (observed: the runner's account,
`tool_calls`). Thirty-two sessions left rows or messages, and 6 left nothing.
Four of the 6 empty sessions woke on a question, and an `unresolved` tick
followed 1 to 26 sessions later. The briefs of the other two named an empty
end. Where I could check the output, 18 were true, 12 partly true, 4 false,
and 4 allowed no check. The 4 false outputs are last words that the rows
contradict, such as s195 of dry7, which says it restored code while its commit
deletes one blank line. After the door, something in the run checked the
output of 18 sessions: desks and ticks within 1 to 26 sessions, the Principal
6 to 83 sessions later. Nothing after the door checked the other 20. One wake
of dry7 ran 16 times, and the drawn s197 ran it again after the drawn s195 had
read "attempt 3 of 3". Three Principal messages ran in `normal` mode, and no
run database holds a `readonly` session. The draw holds no failed session,
and 25 of the 36 wake kinds in the pool are absent from it.

## Part A: what the design says a session is

The bracket gives the check that I apply to the rows.

1. "Woken by exactly one inbound message or one predicate" (`rota/LAWS.md:150`). [The `sessions` row holds one `trigger_msg` or one tick `wake_kind`.]
2. "Each seat wakes cold, acts once, and ends. Nothing accumulates in a conversation. Everything accumulates in records" (`plans/composition.md:37-38`, also `rota/LAWS.md:28`). [The first user prompt opens with the wake, its refs and reads from rows, and holds no turn of an earlier session.]
3. "Briefs hold judgement ... one mode per wake kind" (`rota/MAP.md:37-38`). [The system prompt names one `MODE:` and it fits the wake kind or the message verb.]
4. "The unit per pass is a question" (`plans/composition.md:54`). [The mode text asks for one act or one question in this session, not a series.]
5. A session "reads its working set; emits writes, messages and a receipt; ends" (`rota/LAWS.md:151`). [The session left at least one row or one message.]
6. "A session commits or discards before it ends, so its output stays attributable" (`plans/composition.md:64-65`), and "A failed session leaves its row with `committed = 0`" (`rota/MAP.md:22-23`). [`committed` is 1 or 0, never open.]
7. A door "refuses what a fact makes wrong, and names the route" (`rota/MAP.md:42-43`). [Each refusal text states a fact and a next call or step.]
8. "A door never decides what a role should have judged" (`rota/MAP.md:41-42`). [No refusal turns on a word in the model's own reasoning text.]
9. "Every claim cites a source. A seat can check the claim against the source" (`plans/composition.md:78-79`). [Each row left carries a citation, and the cited source is the one the row names.]
10. "Judgement crosses a role boundary only as structured findings — ids and states" (`rota/LAWS.md:114`). Message prose is declared on the graph edge (`rota/core/schema.sql:1023-1033`). [Messages sent carry refs, and `body_text` only on an edge with `prose`.]
11. "Failure is bounded" and "A wake dispatched past its cap is quarantined and said out loud" (`rota/LAWS.md:164-167`, `190-191`). [The same wake runs no more than its cap of 3 before quarantine.]
12. "A question nobody answers climbs (`unresolved`)" (`rota/LAWS.md:190`). [A question that the woken session left unanswered gets an `unresolved` wake.]
13. "Every principal message is handled read-only first" (`rota/LAWS.md:267-268`). [A session woken by a Principal message has `mode = 'readonly'`.]
14. "A weak model is trusted only as far as the loop that checks it is short" (`plans/composition.md:83-84`). [Something after the door checked the output inside the run, and I count the sessions between.]
15. "Constraint zero ... is starved by positive survey records ("surveyed, no constraints found" counts)" (`rota/LAWS.md:332-334`). [A survey-type session writes a `survey_records` row, found or not.]
16. The Liaison "infers intent, then checks and clarifies with the Principal" and "An unchecked inference is never a record" (`plans/composition.md:26-27`, `107`). [A Liaison reading that became a row was checked with the Principal.]
17. "The tool never rules for the Principal ... or treats silence as consent" (`plans/composition.md:74-75`). [An adoption or a ruling row rests on words or a verdict of the Principal in a message row.]

## Part B: the 38 sessions

Counts. "Calls" are the model's calls in `tool_calls` after the reads that the
runner made before turn 1 ("pushed"). "Refused" counts the lines of the
runner's account (the last turn, `SESSION ENDED. The runner's account:`) that
name a call. "Answer withheld" is a `repeat refused` line: the call ran, and
its answer was not shown again (`rota/core/runner.py:6598-6604`). Turn lists
give the calls in each completion's text. Ms is the sum of `turns.ms`. "N
later" counts sessions by `seq`.

### Architect

**dry1 s83** · tick:survey `src/click` · qwen3:8b · num_ctx 16,384
- Given: system 4,279, user 14,211 characters. Describe one area, then answer one counterfactual question with one `model.amend` per commitment, then `surveys.attest`. One question.
- Did: 10 turns, 155,485 ms. t1 amend×96. t2 source×5. t3 amend×110, source×5, describe. t4 attest. t5 source×8. t6 to t8 source×24 each. t9 describe, attest. t10 amend×5, attest. 200 calls: 102 accepted, 98 refused, 3 answers withheld. 96 amends were refused, mostly "you have not read src/click/core.py this session. A constraint binds the grains it governs ..." and 9 "'t' is a label, not a headline". Two attests were refused: "you have attested `found` and written no constraints ...".
- Left: 5 `constraints` (argument, command, context, option, usageerror), 5 `constraint_bindings`, `model_areas` src/click, `survey_records` architect:src/click, 9 `survey_citations` (observed: `receipts`).
- True: part. `src/click/__init__.py` exports BadArgumentUsage, NoSuchCommand, NoSuchOption, UsageError and get_current_context (observed: clickI `2c8cd3a`, lines 31-42). Headline "Argument" carries the text "Users of Click that catch BadArgumentUsage exceptions" (observed: call c199). The headline and the text name two different things.
- Checked by: the door (0 later). The Critic challenged command, context, option and usageerror, all "stands", from s89 (6 later) (observed: `challenges`). The Principal saw page m50, and his verdict m66 woke s164 (81 later).
- Used: s166 adopted argument and usageerror (83 later). s273 surveyed the area again and rewrote all five rows (190 later) (observed: `receipts`, current `constraints` text).
- Same wake again: 1 (s273).

**dry3 s122** · tick:survey `src/icalendar/parser` · qwen3:8b
- Given: system 4,279, user 24,726. Same survey brief. One question.
- Did: 3 turns, 20,034 ms. Each turn: amend×8 written, attest×1. 16 calls: 2 accepted, 14 refused. Twelve amends: "a quote inside headline ended it early ..." and "'unescape_backslash' is a title with nothing under it". Two attests: "you have attested `found` and written no constraints".
- Left: `model_areas` src/icalendar/parser (the account), `survey_records` with outcome `none_found`, 2 citations. The call said `found`. The door records `none_found` when no row was written (observed: `rota/roles/api.py:5743-5746`).
- True: part. The account's "RFC 5545 (iCalendar) and RFC 2426 (vCard)" is in the area's docstring (observed: the first prompt). The record says no commitment, and `src/icalendar/__init__.py:51-55` imports Parameters, q_join and q_split from `icalendar.parser` (observed: icalendarI `main`).
- Checked by: the door (0). The Principal's verdict m46 led to relay m47, which cites the area, at s205 (83 later) (observed: `messages`).
- Used: wakes s174 to s176 (`tick:observed_entries`) cite the area (52 later).
- Same wake again: 0.

**dry7 s101** · tick:commitments `src/icalendar` · qwen3:8b
- Given: system 5,080, user 23,543. "For each line, ask who outside this repository notices ... Then state it with one call". A series, one call per witness line.
- Did: 9 turns, 8,600 ms. t1 witnesses. t2 source. t3 amend. t4 attest, refused: "you cited ['src/icalendar/enums.py'] and opened none of them". t5 source. t6 witnesses. t7, t8 amend. t9 attest. 8 calls: 6 accepted, 2 refused. One amend was refused: "... names nobody outside this area -- a maintainer, the codebase, the build are inside". One stream stopped at an invented result "OK code.source ->".
- Left: `constraints` cw_15895860fbf4 (party "tests", behaviour "must preserve value data for x-name and iana-token values"), 1 binding, `survey_records` commitments:src/icalendar.
- True: part. Witness cc_bfe9ad3b1bec is a docstring at `enums.py:388`, "Applications MUST preserve the value data for x-name and iana-" (observed: `commitment_candidates`). The row names "tests", and the witness names applications.
- Checked by: the door (0). No challenge and no page cites the row (observed: `challenges`, `messages`).
- Used: 13 later first prompts hold the id, the first in s111 (10 later).
- Same wake again: 0.

**dry1 s87** · tick:boundary `@surface:.readthedocs.yaml` · qwen3:8b
- Given: system 6,207, user 1,965. Read one file that the outside touches. One question.
- Did: 5 turns, 2,369 ms. t1 probe. t2 source. t3 amend, refused: "'Read the Docs build configuration' names nobody outside this area -- a maintainer, the codebase, the build are inside ...". t4 attest `found`, refused. t5 attest `none_found`. 5 calls: 3 accepted, 2 refused.
- Left: `survey_records` with `none_found`, 1 citation.
- True: no check possible. Whether Read the Docs is an outside party is a judgement. The session's own amend called the file a commitment, and its last attest says none.
- Checked by: the door (0). Nothing later.
- Used: nothing.
- Same wake again: 0.

**dry1 s166** · message relay m68 · qwen3:8b
- Given: system 4,810, user 670. Adopt the ids that the Principal approved. One act.
- Did: 2 turns, 6,764 ms. t1 `model.adopt(ids=["argument", "usageerror"])`. t2 the same call again, answered as a copy, "sent again only calls that landed earlier in this session; ended". 1 call accepted.
- Left: `constraints` argument v6, usageerror v7.
- True: yes. The ids equal the approved ids in `principal_verdict` of m68 (observed: first prompt).
- Checked by: nothing after the door.
- Used: s273 rewrote both rows (107 later).
- Same wake again: 0.

### Critic

**dry2 s40** · tick:challenge `@claim:items:returns_tip_as_before` · qwen3.5:9b
- Given: system 4,159, user 412. Attack one claim against the source it cites. The claim cites nothing. One act.
- Did: 4 turns, 19,377 ms. probe, source main.py, source tip_calculator.py, `challenge.uphold`. 4 calls accepted, 0 refused.
- Left: `challenges` items:returns_tip_as_before, verdict `stands`.
- True: yes. The quote `def calculate_tip(total, tip_percentage):\n    return total * (tip_percentage / 100)` is in main.py (observed: s21's prompt shows main.py whole).
- Checked by: nothing. The item later has approval `dropped` (observed: `items`). No row links the drop to the challenge.
- Used: nothing.
- Same wake again: 0.

**dry4 s161** · tick:challenge `@claim:constraints:tzname_in_standard_daylight_blocks` · qwen3.5:9b
- Given: system 4,159, user 919. One claim, one act.
- Did: 3 turns, 19,106 ms. probe, source, `challenge.break` (completion 7,040 characters). 3 calls accepted.
- Left: `challenges` verdict `falsified`, `ledger` challenge_constraints_tzname_... (author critic).
- True: part. The quote "BEGIN:STANDARD\nTZNAME:Brasília standard" is at line 4 of the `.ics` file (observed: git `main`). The reason says the file "shows a valid VTIMEZONE definition containing TZNAME in both STANDARD and DAYLIGHT blocks without error". The quote shows the subject of the claim. It shows no line that defeats the claim (reasoned).
- Checked by: nothing after the door.
- Used: the ledger row is in the first prompt of s168, a Liaison session (7 later).
- Same wake again: 0.

**dry3 s150** · tick:challenge `@claim:constraints:tzid_from_tzinfo` · qwen3.5:9b
- Given: system 4,159, user 4,409. One act.
- Did: 6 turns, 16,095 ms. probe, source, probe, source, source (the same span), `challenge.uphold`. 6 calls accepted.
- Left: `challenges` verdict `stands`.
- True: yes. The quote is `src/icalendar/timezone/tzid.py:79` (observed: git `main`).
- Checked by: nothing. Used: nothing. Same wake again: 0.

**dry2 s21** · tick:challenge `@claim:items:validates_input` · qwen3.5:9b
- Given: system 4,159, user 2,213. One act.
- Did: 1 turn, 1,127 ms. `challenge.break(citation='main.py', quote='if total >= 0:')`. 1 call accepted.
- Left: `challenges` verdict `falsified`, `ledger` challenge_items_validates_input.
- True: yes. The item says "a positive number", and main.py accepts zero with `if total >= 0:` (observed: first prompt).
- Checked by: the Principal. The ledger row is on page m47, sent by s88 (67 later), and his reply m48 woke s95 (74 later).
- Used: page m47, and the first prompts of s39, s88 and s95.
- Same wake again: 0.

**dry7 s130** · tick:challenge `@claim:constraints:cw_72e950053820` · qwen3.5:9b
- Given: system 4,159, user 13,777. One act. The prompt says "This is attempt 2 of 3 on this wake".
- Did: 2 turns, 23,838 ms. probe and source of a docs file, then `challenge.uphold` (completion 8,444 characters). 3 calls accepted.
- Left: `challenges` verdict `stands`.
- True: yes. The quote is `docs/how-to/custom-components.rst:110` (observed: git `main`).
- Checked by: nothing. Used: nothing. Same wake: once before (s129), 0 later.

### Developer

**dry7 s172** · message answer m37 · qwen3.5:9b
- Given: system 6,773, user 14,178. "Read it, apply it, carry on with the batch." A series.
- Did: 17 turns, 70,711 ms. challenge_tester in t1, t8, t12, t13, t14, t17. ledger.log in t2, t3, t5, t6, t9, t15. reask t7. write and commit in t10, t11, t15, t16. 20 calls: 11 accepted, 9 refused, 1 answer withheld. The challenge was refused 4 times: "... yours names no criterion ... The base run said: AssertionError: assert 'line1\r\nline2' == 'line1\nline2'. Your diff did not break it, and the fix is not yours. End the session with no call". Writes were refused: "is a test file, and the tests are the Tester's" (2) and "is not valid Python (unexpected indent ...)" (2). Two streams stopped at invented results.
- Left: `ledger` l_2d6975a346, l_37b0f99728, l_c2a0ba2e15 (kind `scope`).
- True: part. The rows say that the test expects RFC 6868 decoding, and `test_issue_1445.py:147-157` asserts `"line1\nline2"` (observed: git `main`). The last words say that the implementation returns `"line1^nline2"`, and the door quotes the base run as `'line1\r\nline2'`.
- Checked by: nothing after the door.
- Used: no later prompt, message or wake cites the three rows (observed).
- Same wake again: 0.

**dry2 s66** · tick:exhausted `b_2` "the change could not start after 3 attempts" · qwen3.5:9b
- Given: system 5,103, user 1,193. Act on the cause of the exhausted budget. One act.
- Did: 2 turns, 5,583 ms. t1 ledger.log (kind `blocked`) and escalate_architect. t2 prose. 2 calls accepted. The ledger call returned `{"fault": "f_ba9561d44c" ... "No page shows it, and nobody in rota answers it. End the session."}`.
- Left: `faults` f_ba9561d44c (session_id s66), message m28 escalate to the Architect, refs c_5 and c_10. No `receipts` row.
- True: yes. The pushed `tests.load` shows each body as "not run yet, not shown" (observed: first prompt).
- Checked by: the Architect, s67 woke on m28 (1 later).
- Used: s67.
- Same wake again: 0.

**dry8 s177** · message answer m43 · qwen3.5:9b
- Given: system 6,773, user 2,619. The same answer brief, which also says "If the answer leaves the code right as it stands, say so in one sentence and end."
- Did: 1 turn, 9,009 ms. No call.
- Left: nothing. Last words: "The code remains unchanged because the principal's answer confirms that no modifications are needed in `parameter.py` or `property.py` ..."
- True: no. m43 cites c3 and d_7b8f16d813, which speak of `_foldline` folding at spaces and name neither file (observed: first prompt).
- Checked by: nothing. No `unresolved` wake cites m43. Used: nothing.
- Same wake again: 0.

**dry7 s195** · tick:touch_mistaken `b1` · qwen3.5:9b
- Given: system 4,021, user 19,118. Take the mistaken removal out of the head commit. One act. The prompt says "This is attempt 3 of 3 on this wake" and ends "CUT your wake: 24,397 of 43,397 characters are not shown".
- Did: 13 turns, 50,908 ms. t1 expect, source. t2 to t7 source (spans of string.py). t8 write, refused: "start=138, end=165 crosses from one block to another ...". t9 write, commit. t10, t11 source. t12 diff. t13 prose. 14 calls: 13 accepted, 1 refused. One stream stopped at an invented result.
- Left: commit aba4c0a2, `batches` b1 v5, `touch_strays` b1:aba4c0a2...:_foldline.
- True: no. The last words say "The mistaken removal of the space-folding logic in `_foldline` has been restored". Commit aba4c0a2 deletes one blank line, and the file at that commit holds no `escaped_prefix` line (observed: `git show aba4c0a2`).
- Checked by: the stray check at `code.commit` (0), then the Architect at s205, `tick:touch_strayed` (10 later).
- Used: later versions of b1 by s196 and on.
- Same wake again: 12 later (s196, s197, s201 to s204, s210, s217 to s219 failed, s220, s221).

**dry7 s197** · tick:touch_mistaken `b1` · qwen3.5:9b
- Given: as s195, with no attempt line.
- Did: 8 turns, 20,071 ms. t1 expect, source. t2, t3 source. t4, t5 commit "No changes needed - _foldline function already cont...". t6 prose. t7 escalate, refused: "refs is a list of ids and you sent a bare string, 'b1' ...". t8 escalate. 8 calls: 7 accepted, 1 refused. The account adds "ended a tick with nothing done".
- Left: message m52 escalate to the Architect, refs b1. No commit with that message exists in any branch (observed: `git log --all --grep`).
- True: no check possible. The head that the session read is not in the rows.
- Checked by: the Architect, s198 woke on m52 (1 later). Used: s198.
- Same wake again: 10 later.

### Liaison

**dry1 s294** · message report m151 · gemma4:12b-it-qat
- Given: system 7,133, user 3,679. One report from the top of the ladder. One act.
- Did: 3 turns, 11,803 ms. Pushed: brief.list and 6 `decisions.search`. t1 transcript.quote. t2 clarify_principal. t3 prose. 2 calls accepted.
- Left: message m152 clarify to the Principal, with a question in `body_text`.
- True: yes. The question quotes e_m148, "Drop every note and build nothing", word for word and asks what the words leave open (observed: `entries`, `messages`).
- Checked by: the Principal, his reply m158 woke s300 (6 later). Used: s300.
- Same wake again: 0.

**dry1 s115** · message verdict m27 · gemma4:12b-it-qat
- Given: system 5,640, user 468. Relay the ruling to the owner of each named row. The wake names one row.
- Did: 1 turn, 1,120 ms. No call.
- Left: nothing. Last words: "`s1` belongs to the `statements` table ... No tool calls are required."
- True: yes. s1 is a `statements` row, and the brief holds "has no relay here" (observed: `statements`, `turns.system`).
- Checked by: nothing. Used: nothing. Same wake again: 0.

**dry3 s42** · message converse m6, the Principal said "ok" · gemma4:12b-it-qat
- Given: system 5,763, user 7,318. Land one reply to one page. One act.
- Did: 1 turn, 1,987 ms. `rulings.rule` with "approve" for lines 1 to 5 and "rest". 1 call accepted.
- Left: `rulings` r_m6, words "ok", 5 items `approve`, and 10 `ruled_refs`.
- True: yes against the words. The words are one token, and the ruling applies it to each line of page m4.
- Checked by: nothing after the door.
- Used: verdict m8 woke s44 (2 later), and the five items are `approved`.
- Same wake again: 0.

**dry1 s230** · message report m117 · gemma4:12b-it-qat
- Given: system 7,133, user 5,051. One report. One act.
- Did: 4 turns, 12,268 ms. t1 transcript.quote. t2 clarify, refused: "'drop 1 and 3 they are not requests ...' is the principal's own sentence, pasted back to them ...". t3 relay_vision_keeper. t4 prose. 3 calls: 2 accepted, 1 refused.
- Left: message m118 relay to the Vision Keeper, refs e_m103.
- True: yes. The relay carries the Principal's entry unchanged.
- Checked by: the Vision Keeper, s231 (1 later). Used: s231.
- Same wake again: 0.

**dry1 s163** · message converse m65, "ok" · gemma4:12b-it-qat
- Given: system 5,763, user 8,851. Land one reply. One act.
- Did: 1 turn, 2,755 ms. `rulings.rule` with "approve" for 1 to 5, `"6": "ok"`, and "rest". 1 call accepted.
- Left: `rulings` r_m65 with 6 refs `approve`.
- True: part. The words are "ok". The call gave line 6 the value "ok", and the row stores `approve` for reading:m42 (observed: `rulings.per_item`).
- Checked by: nothing after the door. Used: item click_pause_returns_true_on_key is `approved`.
- Same wake again: 0.

### Researcher

**dry4 s215** · message question m64 from the Tester · qwen3:8b
- Given: system 5,862, user 534. Answer one question of fact from outside the repository, `web.search` first. One question.
- Did: 1 turn, 17,690 ms. No call.
- Left: nothing. Last words: "... without additional context or documentation, it is not possible to definitively d[etermine]".
- True: no check possible. The question asks what the Principal means by "prints", which is not a fact outside the repository.
- Checked by: the `unresolved` tick, s225 of the Vision Keeper, "the woken session sent nothing and wrote no row that cites this message" (10 later). Answer m70 went from the Vision Keeper to the Tester.
- Used: nothing. Same wake again: 0.

**dry6c s184** · message question m51 · qwen3:8b
- Given: system 5,941, user 540. One question.
- Did: 2 turns, 7,903 ms. t1 `web.search`. The result reads "[refused] no search engine is granted: `research_search` is `none` ...". t2 prose. 1 call, refused in its result.
- Left: nothing. Last words: "... no search or fetch has been performed, and the system does not have access to a search engine ...".
- True: part. The second half matches the refusal. The first half says that no search was performed, and the call ran and was refused.
- Checked by: the `unresolved` tick s185 (1 later). Used: nothing. Same wake again: 0.

**dry6c s175** · message question m47 · qwen3:8b
- Given: system 5,941, user 619. One question.
- Did: 2 turns, 7,202 ms. t1 `web.search`, refused in its result as above. t2 prose.
- Left: nothing. Last words: "The question cannot be answered because there is no search engine available ..."
- True: yes. The words match the refusal text.
- Checked by: the `unresolved` tick s176 (1 later). Used: nothing. Same wake again: 0.

### Terminologist

**dry5 s77** · tick:survey `src/icalendar/parser/ical` · qwen3.5:9b
- Given: system 3,154, user 24,373. Describe one area, then amend its words. One area.
- Did: 1 turn, 7,557 ms. amend×3, attest. 4 calls accepted.
- Left: `glossary_terms` lazycalendaricalparser, lazysubcomponent, parse_instantly, `survey_records`, 3 citations.
- True: yes. `lazy.py:15` LazyCalendarIcalParser parses lazily, `lazy.py:27` holds parse_instantly, and `lazy.py:91` LazySubcomponent "holds the raw data" (observed: git `main`).
- Checked by: nothing. The pool holds no challenge of a glossary row (observed: `challenges` in dry5 and dry6).
- Used: 24 later first prompts carry the terms in `[glossary.consult]`, from s78 (1 later).
- Same wake again: 0.

**dry5 s109** · message relay m23 · qwen3.5:9b
- Given: system 4,322, user 1,690. Adopt the approved senses. One act.
- Did: 2 turns, 2,220 ms. adopt `alarm#src_icalendar_tests_events`. 1 call accepted.
- Left: `glossary_terms` alarm#src_icalendar_tests_events v119.
- True: yes. It is the one id with `approve` in m23. The other id has `revise`.
- Checked by: s111 woke on the term collision (2 later). Used: s111.
- Same wake again: 0.

**dry6 s62** · tick:survey `src/icalendar/prop/recur` · qwen3.5:9b
- Given: system 3,154, user 25,739. One area.
- Did: 1 turn, 60,121 ms. amend×4, source×3, attest. 8 calls accepted.
- Left: 4 `glossary_terms` (vskip, vfrequency, vmonth, vweekday), `survey_records`, 3 citations.
- True: yes. `vSkip(vText, Enum)`, `vFrequency(str)` with a CaselessDict, `vMonth(int)` and `vWeekday(str)` (observed: git `main`).
- Checked by: nothing. Used: the first prompt of s63 (1 later). Same wake again: 0.

**dry5 s54** · tick:define `@term:parser` · qwen3.5:9b
- Given: system 4,607, user 6,924. One word for the whole program.
- Did: 1 turn, 4,510 ms. `glossary.amend` of parser. 1 call accepted.
- Left: `glossary_terms` parser.
- True: part. The text names `ComponentIcalParser` in `parser/ical/component.py` (line 18) and `_get_ical_parser` in `cal/component.py` (line 538), and both exist. The row's only grain ref is `src/icalendar/parser_tools.py`, a file that the text does not name (observed: `refs`).
- Checked by: nothing. Used: the `[glossary.consult]` of s77 carries it (23 later). Same wake again: 0.

**dry5 s111** · tick:term_collision `alarm` and two senses · qwen3.5:9b
- Given: system 3,274, user 7,411. One word. One act.
- Did: 4 turns, 8,531 ms. t1 synthesise, refused: "that is 'alarm' again, word for word". t2 same, refused: "drop was given a list". t3 same, refused: "... is a reason they are *not* the same -- it says 'different' ...". t4 same and report_liaison. 5 calls: 2 accepted, 3 refused. One refused call has no `tool_calls` row.
- Left: `glossary_terms` alarm v121 and alarm#src_icalendar_tests_events v120, message m25 report to the Liaison.
- True: yes. The Principal's words in m23 are "One term. An alarm is the VALARM component".
- Checked by: the Principal. Page m26 went out from s112 (1 later), and his reply m29 woke s145 (34 later).
- Used: s112, s145, then relay m31 to s147.
- Same wake: twice before (s97, s98), 0 later.

### Tester

**dry1 s208** · message challenge m99 from the Developer · qwen3.5:9b
- Given: system 5,595, user 12,365. One disputed test. The brief says "read the failure and the called code with `code.source`".
- Did: 2 turns, 21,185 ms. No call. The account says "named an act and did not perform it".
- Left: nothing. Last words: "Since I cannot see the implementation (I have no access to the codebase) ...".
- True: no. The brief names `code.source`, and s166 of dry8 in the same mode calls it (observed).
- Checked by: the `unresolved` ticks s234 of the Architect (26 later) and s235 of the Vision Keeper. Answer m121 went to the Developer at s236.
- Used: nothing. Same wake again: 0.

**dry8 s166** · message challenge m36 · qwen3.5:9b
- Given: system 5,595, user 12,557. One disputed test.
- Did: 5 turns, 104,584 ms. t1 had a 30,181-character completion with no call: "your reply was cut at the output budget ..." and "wrote a test into its reply". t2 encode, refused: "the test uses _foldline and never imports or defines it ...". t3 encode. t4 answer_developer. t5 prose. 5 calls: 4 accepted, 1 refused.
- Left: `tests` tst_c1 rewritten, message m38 answer to the Developer, with quotes in `body_text`.
- True: part. tst_c1 passes in runs tr491 and tr655 (observed: `test_runs`). I did not check the words of the last line.
- Checked by: the Developer at s168 (2 later), and later test runs.
- Used: s168. Same wake again: 0.

**dry1 s186** · message answer m88 · qwen3.5:9b
- Given: system 4,873, user 8,308. "Read it, apply it to the tests you were writing, carry on." A series.
- Did: 17 turns, 34,927 ms. encode×2 in each of t1, t3 to t6, t10 and t14. retire in t1, t8, t12, t15, t17. reask in t9 and t13. 30 calls: 12 accepted, 18 refused, 2 answers withheld. Refusals: NameError for StringIO, patch and raw_terminal. "is already inh_51d478df's file". "no ruling of the principal names inh_01fdb170". "inh_04b2c3d4 is not a test" (4). "the message that woke you is not a reply to a question you asked" (2). The account ends "tests.retire was refused the same way in four turns; the session ended on it".
- Left: `tests` inh_03a1b2c3, an id that the model chose, at `tests/test_termui_tk_1_criteria_terminal_check.py`.
- True: part. The test passes (tr3) and asserts `ctx.__enter__() == -1`. The criterion says "The return value is False when raw_terminal reports a non-terminal" (observed: `tests`, `criteria`).
- Checked by: the Developer's challenge m92, and s194 rewrote the test (8 later).
- Used: s192 and on, through first prompts. Same wake again: 0.

**dry8 s161** · tick:tests_missing `bg_1`, c1 to c3 · qwen3.5:9b
- Given: system 7,779, user 11,248. "Every criterion gets a verdict, then its door." A series of 3.
- Did: 7 turns, 92,571 ms. t1 encode×3. t2 triage×3. t3 encode×3. t4 encode. t5 encode×3. t6, t7 triage and encode (the same text). 15 calls: 9 accepted, 6 refused, 1 answer withheld. Refusals: "body is not Python (unterminated string literal ...)" (4), "c3 has no triage verdict from you yet", and "is already tst_c1's file". The account ends "tests.encode was refused the same way in four turns".
- Left: `tests` tst_c1 and tst_c3, and `ledger` l_27fb706ccc and l_92557359be (kind `invented`).
- True: part. tst_c3 fails at attempts 2, 3 and 5 and passes at attempt 6 (observed: `test_runs`). The Developer challenged tst_c1 (m36), and s166 replaced it.
- Checked by: the Developer's challenge m36, then s166 (5 later), and test runs.
- Used: s162 and on. Same wake again: 0.

**dry7 s216** · message answer m60 · qwen3.5:9b
- Given: system 4,873, user 18,550, cut "19,517 of 37,949 characters are not shown". The answer brief. A series.
- Did: 9 turns, 72,860 ms. t1 source. encode×2 in t2 to t4, encode×1 in t5 to t9. 13 calls: 6 accepted, 7 refused. Refusals: "this test imports src, and the batch's other tests import icalendar" (2). "is stored at tests/test_fold_no_split_delimiters.py". "body is not Python" (3). One stream stopped at an invented result. The account ends "repeated its previous turn verbatim twice; ended".
- Left: `tests` tst_fold_c2 and tst_fold_c3, and `ledger` l_62717b5f71 (kind `invented`).
- True: part. At attempt 12, tst_fold_c2 passes and tst_fold_c3 fails (observed: tr1486, tr1487). Batch b1 ends `deferred`.
- Checked by: test runs. Used: the first prompts of s220 and s221 (4 later). Same wake again: 0.

### Vision Keeper

Each session below reads one prose file against the account, logs a conflict as
`ledger.log`, and then attests. One file each.

**dry8 s35** · tick:reconcile `docs/reference/changelog.rst` · qwen3:8b
- Given: system 3,696, user 2,480. The file holds `.. include:: ../../CHANGES.rst`.
- Did: 3 turns, 2,174 ms. t1 probe, prose. t2 `code.source(path='../../CHANGES.rst')`. t3 prose and attest `none_found`. 4 calls accepted.
- Left: `survey_records` with `none_found`, 1 citation.
- True: no. The last words say "The file `CHANGES.rst` could not be found, and no grain in the index is named anything like it". dry8 `code_index` holds the grain `CHANGES.rst` (observed).
- Checked by: nothing. Used: nothing. Same wake again: 0.

**dry4 s23** · tick:reconcile `docs/reference/api/icalendar.rst` · qwen3:8b
- Given: system 3,696, user 3,045. The file is a toctree.
- Did: 10 turns, 8,686 ms. t1 probe, prose, consult. t2 source×9. t3 to t8 probe×1 each. t9 probe×5. t10 attest `none_found`. 24 calls accepted, 0 refused, 1 answer withheld. Four streams stopped at invented results "OK code.probe ->". The probes used the item ids as patterns.
- Left: `survey_records` with `none_found`.
- True: yes (reasoned). A toctree states no claim about behaviour.
- Checked by: nothing. Used: nothing. Same wake again: 0.

**dry5 s29** · tick:reconcile `docs/reference/api/icalendar.timezone.tzp.rst` · qwen3:8b
- Given: system 3,696, user 2,660. The file is an automodule stub.
- Did: 6 turns, 8,685 ms. probe, source, probe, prose, then ledger.log×6 and attest `found`, then attest `none_found`. 12 calls: 5 accepted, 7 refused. Five logs: "... is the row this note is about, and one side of the note is its own text ...". One log: "'icalendar.timezone.tzp' names no row". The attest was refused. Two invented results.
- Left: `survey_records` with `none_found`.
- True: yes (reasoned). An automodule stub states no claim.
- Checked by: nothing. Used: nothing. Same wake again: 0.

**dry7 s18** · tick:reconcile `docs/how-to/usage.rst` · qwen3:8b
- Given: system 3,696, user 8,472. The prompt shows the "first 6000 of 19017 characters".
- Did: 4 turns, 5,075 ms. probe×5 on the item ids, prose, baseline, ledger.log×3, attest `found`, attest `none_found`. 12 calls: 8 accepted, 4 refused. Three logs were refused as restating their row, and the attest as "attested `found` and written no ledger".
- Left: `survey_records` with `none_found`.
- True: no check possible. Whether usage.rst conflicts with the account is a judgement, and the session saw a third of the file.
- Checked by: nothing. Used: nothing. Same wake again: 0.

**dry5 s31** · tick:reconcile `docs/reference/api/icalendar.timezone.zoneinfo.rst` · qwen3:8b
- Given: system 3,696, user 2,685. An automodule stub.
- Did: 9 turns, 10,836 ms. probe, prose, source×5 (t3 to t7), ledger.log×5 and attest, attest `none_found`. 15 calls: 9 accepted, 6 refused, all of the restate type. Five streams stopped at invented results.
- Left: `survey_records` with `none_found`.
- True: yes (reasoned). An automodule stub.
- Checked by: nothing. Used: nothing. Same wake again: 0.

## Part C: the grid

| # | statement | holds | does not hold | cannot be told |
|---|---|---|---|---|
| 1 | one message or one predicate | 38: all | 0 | 0 |
| 2 | wakes cold, records not conversation | 38: all | 0 | 0 |
| 3 | one mode per wake kind | 38: all | 0 | 0 |
| 4 | the unit per pass is a question | 32: all others | 6: d7s101, d7s172, d8s177, d1s186, d8s161, d7s216 | 0 |
| 5 | leaves writes or messages | 32: all others | 6: d8s177, d1s115, d4s215, d6c s184, d6c s175, d1s208 | 0 |
| 6 | commits or discards | 38: all, `committed = 1` | 0 | 0 |
| 7 | a refusal names the fact and the route | 16: d1s83, d3s122, d7s101, d1s87, d7s195, d7s197, d1s230, d6c s184, d6c s175, d5s111, d8s166, d8s161, d7s216, d5s29, d7s18, d5s31 | 3: d1s186, d7s172, d4s23 | 19: no refusal |
| 8 | a door does not judge for the role | 16: the same 19 minus the 3 at right | 3: d1s87, d7s101, d5s111 | 19: no refusal |
| 9 | the claim cites its source | 30: all others | 1: d5s54 | 7: the 6 empty sessions, d7s195 (code commit) |
| 10 | ids and states, prose on declared edges | 6: d2s66, d7s197, d1s294, d1s230, d5s111, d8s166 | 0 | 32: sent no message |
| 11 | a repeated wake stops at its cap | 36: all others | 2: d7s195, d7s197 | 0 |
| 12 | an unanswered question climbs | 4: d4s215, d6c s184, d6c s175, d1s208 | 0 | 34: not an unanswered question |
| 13 | a Principal message runs read-only first | 0 | 3: d1s115, d3s42, d1s163 | 35: not a Principal message |
| 14 | a check after the door, inside the run | 18: d1s83, d3s122, d2s21, d2s66, d7s195, d7s197, d1s294, d1s230, d4s215, d6c s184, d6c s175, d5s109, d5s111, d1s208, d8s166, d1s186, d8s161, d7s216 | 20: all others | 0 |
| 15 | a survey writes its record | 11: d1s83, d3s122, d7s101, d1s87, d5s77, d6s62, d8s35, d4s23, d5s29, d7s18, d5s31 | 0 | 27: not a survey kind |
| 16 | a Liaison reading is checked | 2: d1s294, d1s230 | 0 | 36: d3s42, d1s163 (no read-back row found), d1s115 (no reading), 33 not Liaison |
| 17 | never rules for the Principal | 4: d1s166, d5s109, d3s42, d1s163 | 0 | 34: no ruling or adoption |

Evidence for each "does not hold":

- 4, d7s101: "For each line ... state it with one call" (observed: MODE text).
- 4, d7s172 and d8s177: "Read it, apply it, carry on with the batch" (observed: MODE text).
- 4, d1s186 and d7s216: "Read it, apply it to the tests you were writing, carry on" (observed).
- 4, d8s161: "every criterion gets a verdict, then its door", three criteria (observed).
- 5, the six empty sessions: no `receipts`, `faults` or message row (observed). The briefs of s177 and s115 name the empty end (Part D, item 7).
- 7, d1s186: "the message that woke you is not a reply to a question you asked" names no route. "inh_04b2c3d4 is not a test" refers to an id that the session encoded itself (observed: call c15).
- 7, d7s172: "is not valid Python (unexpected indent ...); the harness imports it and would die at collection." names no next step (observed).
- 7, d4s23: "repeat refused: code.probe asked three times this session and the answer has not changed; not answered again" names no next step (observed).
- 8, d1s87 and d7s101: the refusal rests on a word list in the party or headline, "a maintainer, the codebase, the build are inside" (observed).
- 8, d5s111: the refusal of `glossary.same` rests on the word "different" in the model's `why` (observed).
- 9, d5s54: the only grain ref is `src/icalendar/parser_tools.py`, and the text cites `parser/ical/component.py` and `cal/component.py` (observed: `refs`).
- 11, d7s195 and d7s197: the s195 prompt says "attempt 3 of 3", and s196 and s197 then run the same wake. Sixteen sessions run on the key `developer|tick:touch_mistaken|b1`. `tick_attempts` holds attempts 3, quarantined 1 and reported 1 at the end (observed).
- 13, d1s115, d3s42 and d1s163: `mode = 'normal'` on a Principal message. None of the 9 run databases holds a `readonly` session (observed: query).
- 14, the 20 sessions: no later challenge, page, message, wake or test run cites their output (observed: `after.py`). The output of five of them was read in later prompts without a check: d7s101, d4s161, d5s77, d6s62 and d5s54.

| run, session | role | wake kind | model | turns | accepted | refused | left | true | checked by, later | used later by | again |
|---|---|---|---|---|---|---|---|---|---|---|---|
| dry1 s83 | architect | tick:survey | qwen3:8b | 10 | 102 | 98 | 21 rows | part | door; Critic 6; Principal 81 | s166, s273, page m50 | 1 |
| dry3 s122 | architect | tick:survey | qwen3:8b | 3 | 2 | 14 | 4 rows | part | door; Principal 83 | s174 to s176, m47 | 0 |
| dry7 s101 | architect | tick:commitments | qwen3:8b | 9 | 6 | 2 | 4 rows | part | door | 13 prompts from s111 | 0 |
| dry1 s87 | architect | tick:boundary | qwen3:8b | 5 | 3 | 2 | 2 rows | no check | door | nothing | 0 |
| dry1 s166 | architect | message | qwen3:8b | 2 | 1 | 0 | 2 rows | yes | nothing | s273 | 0 |
| dry2 s40 | critic | tick:challenge | qwen3.5:9b | 4 | 4 | 0 | 1 row | yes | nothing | nothing | 0 |
| dry4 s161 | critic | tick:challenge | qwen3.5:9b | 3 | 3 | 0 | 2 rows | part | nothing | s168 prompt | 0 |
| dry3 s150 | critic | tick:challenge | qwen3.5:9b | 6 | 6 | 0 | 1 row | yes | nothing | nothing | 0 |
| dry2 s21 | critic | tick:challenge | qwen3.5:9b | 1 | 1 | 0 | 2 rows | yes | Principal 67 | page m47, s95 | 0 |
| dry7 s130 | critic | tick:challenge | qwen3.5:9b | 2 | 3 | 0 | 1 row | yes | nothing | nothing | 0 |
| dry7 s172 | developer | message | qwen3.5:9b | 17 | 11 | 9 | 3 rows | part | door | nothing | 0 |
| dry2 s66 | developer | tick:exhausted | qwen3.5:9b | 2 | 2 | 0 | fault, message | yes | Architect 1 | s67 | 0 |
| dry8 s177 | developer | message | qwen3.5:9b | 1 | 0 | 0 | nothing | no | nothing | nothing | 0 |
| dry7 s195 | developer | tick:touch_mistaken | qwen3.5:9b | 13 | 13 | 1 | commit, 2 rows | no | stray check 0; Architect 10 | s196 and on | 12 |
| dry7 s197 | developer | tick:touch_mistaken | qwen3.5:9b | 8 | 7 | 1 | message | no check | Architect 1 | s198 | 10 |
| dry1 s294 | liaison | message | gemma4:12b-it-qat | 3 | 2 | 0 | message | yes | Principal 6 | s300 | 0 |
| dry1 s115 | liaison | message | gemma4:12b-it-qat | 1 | 0 | 0 | nothing | yes | nothing | nothing | 0 |
| dry3 s42 | liaison | message | gemma4:12b-it-qat | 1 | 1 | 0 | ruling | yes | nothing | s44, items approved | 0 |
| dry1 s230 | liaison | message | gemma4:12b-it-qat | 4 | 2 | 1 | message | yes | Vision Keeper 1 | s231 | 0 |
| dry1 s163 | liaison | message | gemma4:12b-it-qat | 1 | 1 | 0 | ruling | part | nothing | item approved | 0 |
| dry4 s215 | researcher | message | qwen3:8b | 1 | 0 | 0 | nothing | no check | unresolved tick 10 | nothing | 0 |
| dry6c s184 | researcher | message | qwen3:8b | 2 | 0 | 1 | nothing | part | unresolved tick 1 | nothing | 0 |
| dry6c s175 | researcher | message | qwen3:8b | 2 | 0 | 1 | nothing | yes | unresolved tick 1 | nothing | 0 |
| dry5 s77 | terminologist | tick:survey | qwen3.5:9b | 1 | 4 | 0 | 7 rows | yes | nothing | 24 prompts from s78 | 0 |
| dry5 s109 | terminologist | message | qwen3.5:9b | 2 | 1 | 0 | 1 row | yes | s111, 2 | s111 | 0 |
| dry6 s62 | terminologist | tick:survey | qwen3.5:9b | 1 | 8 | 0 | 8 rows | yes | nothing | s63 prompt | 0 |
| dry5 s54 | terminologist | tick:define | qwen3.5:9b | 1 | 1 | 0 | 1 row | part | nothing | s77 prompt | 0 |
| dry5 s111 | terminologist | tick:term_collision | qwen3.5:9b | 4 | 2 | 3 | 2 rows, message | yes | Principal 34 | s112, s145, s147 | 0 |
| dry1 s208 | tester | message | qwen3.5:9b | 2 | 0 | 0 | nothing | no | unresolved tick 26 | nothing | 0 |
| dry8 s166 | tester | message | qwen3.5:9b | 5 | 4 | 1 | 1 row, message | part | Developer 2; test runs | s168 | 0 |
| dry1 s186 | tester | message | qwen3.5:9b | 17 | 12 | 18 | 1 row | part | Developer 8; test run | s192 and on, s194 | 0 |
| dry8 s161 | tester | tick:tests_missing | qwen3.5:9b | 7 | 9 | 6 | 4 rows | part | Developer 5; test runs | s162 and on | 0 |
| dry7 s216 | tester | message | qwen3.5:9b | 9 | 6 | 7 | 3 rows | part | test runs | s220, s221 prompts | 0 |
| dry8 s35 | vision_keeper | tick:reconcile | qwen3:8b | 3 | 4 | 0 | 2 rows | no | nothing | nothing | 0 |
| dry4 s23 | vision_keeper | tick:reconcile | qwen3:8b | 10 | 24 | 0 | 2 rows | yes | nothing | nothing | 0 |
| dry5 s29 | vision_keeper | tick:reconcile | qwen3:8b | 6 | 5 | 7 | 2 rows | yes | nothing | nothing | 0 |
| dry7 s18 | vision_keeper | tick:reconcile | qwen3:8b | 4 | 8 | 4 | 2 rows | no check | nothing | nothing | 0 |
| dry5 s31 | vision_keeper | tick:reconcile | qwen3:8b | 9 | 9 | 6 | 2 rows | yes | nothing | nothing | 0 |

| role | sessions | turns | accepted | refused | left something | true: yes, part, no, no check | checked after the door | used later | same wake again |
|---|---|---|---|---|---|---|---|---|---|
| architect | 5 | 29 | 114 | 116 | 5 | 1, 3, 0, 1 | 2 | 4 | 1 |
| critic | 5 | 16 | 17 | 0 | 5 | 4, 1, 0, 0 | 1 | 2 | 0 |
| developer | 5 | 41 | 33 | 11 | 4 | 1, 1, 2, 1 | 3 | 3 | 22 |
| liaison | 5 | 10 | 6 | 1 | 4 | 4, 1, 0, 0 | 2 | 4 | 0 |
| researcher | 3 | 5 | 0 | 2 | 0 | 1, 1, 0, 1 | 3 | 0 | 0 |
| terminologist | 5 | 9 | 16 | 3 | 5 | 4, 1, 0, 0 | 2 | 5 | 0 |
| tester | 5 | 40 | 31 | 32 | 4 | 0, 4, 1, 0 | 5 | 4 | 0 |
| vision_keeper | 5 | 32 | 50 | 17 | 5 | 3, 0, 1, 1 | 0 | 0 | 0 |
| all | 38 | 182 | 267 | 182 | 32 | 18, 12, 4, 4 | 18 | 22 | 23 |

## Part D: what the grid does not cover

1. Seven sessions wrote their own tool results, and the runner stopped the stream at the invented line. There were 16 stops: s101 1, s172 2, s195 1, s216 1, s23 4, s29 2 and s31 5 (observed: the account, "wrote its own tool results").
2. Some sessions sent the same call many times. s83 sent `model.amend` 96 times in turn 1 and 110 times in turn 3, and called `code.source` 90 times on 8 files. s186 encoded the same two tests 16 times. s23 probed the 5 item ids twice. s172 sent a refused challenge 4 times after the refusal said "End the session with no call" (observed: `tool_calls`, the account).
3. The door changed the outcome of a call. s122 attested `found`, and its row says `none_found` (observed: `survey_records`, `rota/roles/api.py:5743-5746`).
4. The model chose the ids of test rows. s186 encoded `inh_03a1b2c3` and `inh_04b2c3d4`, which use the prefix of the project's inherited tests. A later retire was refused: "inh_04b2c3d4 is not a test". The brief of `tests_missing` says "you choose the test id and the path" (observed: `tool_calls`, `turns.system` of s161).
5. A message row holds no session id. I attributed m28, m52, m152, m118, m25 and m38 by their `cause_id`, their refs and the next session's `trigger_msg`. A `ledger.log` of kind `blocked` became a `faults` row with no receipt, and the call's answer said "No page shows it" (observed: schema, s66 turn 2).
6. In 4 of the 6 empty sessions, a session of another role answered the question. The Vision Keeper sent answers m70, m52 and m48 to the Tester, in reply to the Researcher's questions m64, m51 and m47. The Architect and the Vision Keeper took m99 (observed: `messages`, the `unresolved` wakes).
7. Two of the 6 empty sessions followed their brief. The brief of s177 says "If the answer leaves the code right as it stands, say so in one sentence and end", and the brief of s115 says a statement "has no relay here; leave it" (observed: `turns.system`).
8. Last words disagree with the rows in 6 sessions: s195 (restored), s35 (CHANGES.rst), s208 (no access), s177 (parameter.py), s172 (the raw string) and s184 (no search performed). A door reads only calls, and no row records the last words (observed: Part B).
9. The context was cut in three first prompts: "CUT your wake: 24,397 of 43,397 characters are not shown" in s195, 24,526 of 43,526 in s197, and 19,517 of 37,949 in s216. The prompt of s83 says "3 earlier exchange(s) dropped to fit the window". All 38 sessions ran at `num_ctx` 16,384 (observed: `turns.user`, `sessions`).
10. A later session rewrote rows that the Principal had approved. The Principal approved argument and usageerror of s83 in verdict m66, and s166 adopted them. s273 then rewrote all five of s83's constraints, and the rows now hold s273's text, not the text on his page (observed: `constraints.version`, `receipts`).

## Part E: limits

- The counts of refusals come from the runner's account. That account lists a repeat refusal once per key and drops a repeated "listed" line. A call that fails at the parse can have no `tool_calls` row, as in s111. The two Researcher refusals arrive as "OK web.search -> ... [refused]" in the next prompt and are not in the account. I counted them from a scan of the prompts for "[refused]". So "accepted" is calls minus refusals, corrected by hand for s111 and the Researchers.
- I took the turn lists from the completion text. Native calls are rendered as text too (`rota/core/runner.py`, `_with_native_lines`), so the rows cannot tell native from text calling.
- `test_runs` holds no session id, so I cannot count the distance from a test to its run in sessions.
- A message holds no session id (Part D, item 5).
- The sample repositories serve every run. I checked icalendar code at `main` (99619246, the `commit_sha` of s122's survey record) and click code at `2c8cd3a` (the `commit_sha` of s87's record). Today, click `main` carries the delivery of dry run 1.
- The `.rota/dry*.db` files were opened on 2026-11-10 and can hold a back-fill of `ruled_refs` (inventory page). The `ruled_refs` of s42 and s163 can be later than the run.
- For s23, s29 and s31, "true" is reasoned from the file type. For s87 and s18, the claim is a judgement with no key.
- "Used later" through a first prompt is a substring match on the row id. For common words (argument, command, parser), the match also finds unrelated text, so I cite only the specific links in Part B.
- By run, the draw holds dry1 9, dry2 3, dry3 3, dry4 3, dry5 6, dry6 1, dry6b 0, dry6c 2 (s175 and s184 come after s137, the end of dry run 6b), dry7 7, dry8 4 and blind1 0.
- By wake kind, the draw holds message 16, tick:reconcile 5, tick:challenge 5, tick:survey 4, tick:touch_mistaken 2, and 1 each of commitments, boundary, exhausted, define, term_collision and tests_missing. These 11 kinds cover 1,571 of the 1,858 sessions in the pool. The 25 absent kinds hold 287 sessions. The largest are tick:tests_failing 35, tick:quarantined 30, tick:batch_start 25, tick:signoff 19, tick:unresolved 18 and tick:guess 16 (observed: query over the 10 databases).
- No drawn session has `committed = 0`, and 38 of the 1,858 sessions in the pool do: dry1 8, dry6 18, dry6bc 9 and dry7 3. The failure path of statement 6 (`db.session_fail`) was not observed in this draw.
- The pool holds only 3 Researcher sessions, so the Researcher row is the whole role, not a sample.
