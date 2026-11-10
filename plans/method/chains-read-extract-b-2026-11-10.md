Part b of the chains read, sub-agent, one pass. Chains 2, 7, 14, 24, 25, 26, 28, 29, 36, 37, 38, 39, 40, 41.

The limits of this page. The chains come from one reader and one pass, and a firm link is that reader's call. Cell 1 is the second look. A read page is the build session's own account, so a wall that no read named after a change can still be there. The nights share state, so one run without the sign does not show that the sign is gone. The reads count walls in different ways, and a wall that a read does not name is "not named", not "gone". This page does not judge a fix and does not rank the chains.

### Chain 2: n166-W9, 10 turns, firm

1. The wall: "the constraint tick quarantines at onboarding [C?] (W-I)" (`plans/method/turns-list-2026-11-10.md:324`; `plans/night166-read.md:217`). First turn night 166, last turn night 175, 10 turns. The chain holds two signs, so this block splits it.
   - Part A, the key `-|tick:constraint_zero|` at 3 at onboarding, and s1's refused report of it. n166-W9, n167-W12, n168-W11, n169-W8 name the key only (`plans/night167-read.md:105`, `plans/night168-read.md:114`, `plans/night169-read.md:69`). n170-W14 and n171-W14 name the key and s1's refusal on the ref 'tick: quarantined' (`plans/night170-read.md:70`, `plans/night171-read.md:71`). n172-W11, n173-W4 and n174-W11 name the refusal only: "refs are ids, and 'tick: quarantined' is not one" (`plans/night172-read.md:68`, `plans/night173-read.md:61`, `plans/night174-read.md:70`). Turns n166 to n174, 9 turns. From night 173 the key itself is a wall of its own, n173-W3, n174-W10, n175-W13, which is chain 26.
   - Part B, the onboarding claim tick `critic|tick:challenge|@claim:constraints:argument` that quarantines with no verdict. n172-W10, n173-W2, n174-W9, n175-W12 (`plans/night172-read.md:67`, `plans/night173-read.md:59`, `plans/night174-read.md:68`, `plans/night175-read.md:68`). Turns n172 to n175, 4 turns. The key is absent from night 171's quarantine line (`plans/night171-read.md:22`). The night 172 read itself links W10 to night 171's W14 as "Same key family" (`plans/night172-read.md:155`). The key, the seat and the sign differ, so the parts are two walls.
   - The same sign as Part A is older than the chain. n160-W8 names "`constraint_zero` quarantine at onboarding, a fifth night" (extract b, night 160, item 4), in the firm chain of n156-W10 (list line 335). The night 166 read says "The same key at 3 on nights 164 and 165" (`plans/night166-read.md:217`). The reads of nights 161 to 165 list no such wall, so no link joins the two chains.
2. The state at the end:
   - Part A: Open. Night 174, one of the last three runs of the night series, named it (n174-W11). The key itself is named at night 175 and at dry1 (chain 26).
   - Part B: Open. Night 175, the last run of the night series, named it (n175-W12).
3. The conditions at the end:
   - Part A: the nights stopped after night 175 (Roman, 2026-10-29 01:53, extract c, night 175, item 9). The next run is dry1, a dry run with the session in the Principal seat and a 40-step cap. Dry1 ran on click, the same repository as the nights (`plans/archive/stack-2026-11-02.md:195`, "dry1 on click"; `plans/dry1-first-wall-read-2026-10-31.md:5`). The kind of run changed. Conditions changed.
   - Part B: the last naming is night 175, the last night. The next three runs are dry1, dry2 and dry3, another kind of run, and dry2 and dry3 run on other repositories (extract c, dry2 item 2, dry3 item 2). Conditions changed.
4. The changes:
   - Part A, change 1. F20 with F21, sprint 28 row 1, "the root fix by frame 344's audit", a fact of frame 330. Commits ba128953, b2762648, a7127d41 on f20root, landed by merge 82d426c4 at 2026-10-27 16:48 (`plans/archive/stack-2026-11-02.md:108-112`; git log). Files and names: `scheduler.quarantined_keys`, `key_parts`, the lift in `db.write_state`, and the word tables through `TICK_WORDS` and `_gave_up_words` (`plans/f1-f15-f21-night172-read.md:124`). Kind: other code of rota. The night 170 read places W14 under F21 (`plans/night170-read.md:142`). The audit's proposal for F20 names "the constraint tick at onboarding (nights 160, 166 to 170)" as night evidence that should "go to 0 over 3 nights" (`plans/rootfix-audit-2026-10-27-b.md:42`). The build's status lines name b_3's stop on `tests_missing`, not the constraint tick. The next read: night 172's W11 has "Same text as night 171's W14: \"'tick: quarantined' is not one\"", 6 refusals in s1 and s84 (`plans/night172-read.md:68`, `:156`). Night 173 counts 12 refusals, night 174 counts 6.
   - Part A, change 2. Frame 354, commit e7016e65 at 2026-10-31 17:27, "fix(onboarding): constraint zero settles, and a quarantine report is never an empty page". Files: `rota/core/predicates.py`, `rota/onboarding/boot.py`, `rota/core/scheduler.py`, `rota/roles/api.py`, `rota/roles/principal.py`, `rota/core/sandbox.py` (git show). Kind: other code of rota, and a door that refuses a present with no refs. The commit message: "boot.coded_areas is now the one definition of an area with code", and "a quarantined key that reaches no row now travels as its own ref". Its own measure: "constraint zero fired twice with refs and was never quarantined" on a cold run of click at 2c8cd3a. This change answers dry1-W2 and dry1-W3, after the night series.
   - Not counted: frame 326's pass 1d of 2026-10-26 00:49 makes the test fixture's chain offer no `tick:constraint_zero` (`plans/stack.md:2332`). Its aim is the fixture state, not the night.
   - Part A count: 2.
   - Part B, change 1. F20 with F21, the same commits as Part A change 1, built before night 172. The night 172 read places W10 under F20 and F21: "The words \"could not check a claim for argument\" now reach the end print" (`plans/night172-read.md:155`). Sprint 33 row 6 keeps the wall as "A count until a fix of F20's lift covers it" (`plans/stack.md:305-307`). Status lines of 2026-10-28 12:34 and 17:08 count it on nights 174 and 175, "no held frame's site" (`plans/archive/stack-2026-10-30.md:349`, `:387`). No change after F20 aims at it (absent only: grep of `plans/stack.md` and the archives for "claim tick" and "constraints:argument").
   - Part B count: 1 (F20 with F21, by the read's placement).
5. The last change before the end: not applicable. Both parts are open.
6. The place of the changes:
   - Part A: the sign shows in the scheduler step `-|tick:constraint_zero|` (the predicate `constraint_zero` in `rota/core/predicates.py` and `refresh_constraint_zero` in `rota/onboarding/boot.py`, `plans/dry1-first-wall-read-2026-10-31.md:26`), and in the Liaison's call `present_principal` refused by the ref check. Change 1 touches the key readers in `rota/core/scheduler.py` and the word tables in `rota/roles/principal.py`. It does not touch the predicate or the refresh. Change 2 touches the predicate, the refresh, the send door and the page renderer, so it touches the place of the sign.
   - Part B: the sign shows in the Critic's `tick:challenge` sessions on the claim and in the key's quarantine. Change 1 touches the key readers and the words, another place.
7. Who started each change:
   - F20 with F21: frame 344's audit, which started on Roman's message of 2026-10-27 14:08: "a few sessions ago we analyzed the completed frames and found that many did not fix the root cause. Go back and review them" (extract c, night 170, item 9). It is sprint 28 row 1 (`plans/archive/stack-2026-11-02.md:108`).
   - Frame 354: a read of a run, `plans/dry1-first-wall-read-2026-10-31.md`, pushed in commit a79fd411.
8. The origin:
   - Part A. The predicate `constraint_zero` exists from 210649a7 (2026-08-09, "feat(scheduler): schema, atomic session commit, scheduler and boot"). The dry1 read gives the cause: the predicate wants every area of `code_index`, and the refresh binds only areas with `grain_kind = 'symbol'` (`plans/dry1-first-wall-read-2026-10-31.md:26-27`, reasoned, not replayed). `git log -S "grain_kind = 'symbol'"` on `rota/onboarding/boot.py` gives 01e48a6f (2026-09-08). Its message: "Constraint zero bound every indexed area, including areas of pure prose ... k0 now binds only to areas with symbol grains". It answers a wall of a cold walk on tipsC, 2026-09-04, and names no frame. The refusal text "refs are ids" comes from f73a7c01 (2026-08-14, "fix(sandbox): refs are ids, and the sandbox now knows what an id looks like"). Origin class: a fix that answered another wall, the prose-only walk of 2026-09-04, frame not found.
   - Part B. The predicate is `challenge` at `rota/core/predicates.py:2467-2472` (`python -m rota.tools.map fn challenge`). The `@claim:` refs come from 99774be3 (2026-08-24, "feat(sandbox): v2 stage 9 -- the understanding pipeline gets its adversarial reader"). No record says why the key first quarantines on night 172. Origin class: rota's first design for the predicate. The cause of the start at night 172 is not found.
9. After the end: not applicable for open parts. For Part A, the key is named after night 174 as n175-W13 and dry1-W2 (chain 26). For Part B, dry1 to dry3 name no claim tick (extract c, dry1 to dry3, item 4). The dry1 read says "Nights 173 and 175 repeat this at s84 for a Critic quarantine" (`plans/dry1-first-wall-read-2026-10-31.md:36`). Not sure.

Row (Part A): Open | conditions changed | 2 | not applicable | prose walk fix | origin frame: none
Row (Part B): Open | conditions changed | 1 | not applicable | first design predicate | origin frame: none

### Chain 7: n170-W6, 6 turns, firm

1. The wall: "the Liaison's `rulings.rule` is refused before it lands [C?] (W6, F2)" (`plans/method/turns-list-2026-11-10.md:329`; `plans/night170-read.md:62`). First turn night 170, last turn night 175, 6 turns. The walls are n170-W6, n171-W6, n172-W6, n173-W1, n174-W1, n175-W6 (`plans/night171-read.md:63`, `plans/night172-read.md:63`, `plans/night173-read.md:58`, `plans/night174-read.md:60`, `plans/night175-read.md:62`). Each names refusals of `rulings.rule` and an answer of his that lands nothing. The reads' own "Same as" column joins them: night 172 "Same" (`plans/night172-read.md:151`), night 173 "Same door, `rulings.rule`" (`plans/night173-read.md:173`), night 174 "Same door ... as night 173's W1" (`plans/night174-read.md:205`), night 175 "Same shape as night 174's W1 on a new page, an account page" (`plans/night175-read.md:183`). The refusal texts change from night to night: the empty-words text is gone on night 173, and the act text fires on new forms on nights 173 and 174. The door and the sign are the same, so I do not split the chain.
2. The state at the end: Open. Night 175, the last run of the night series, named it (n175-W6). n175-W6 meets dry1-W5 by a "not sure" link only (extract c, night 175, item 8).
3. The conditions at the end: the last naming is night 175, the last night. The next runs are dry runs with the session in the Principal seat (extract c, night 175, item 9). Dry1 ran on click, and dry2 and dry3 on other repositories. Conditions changed.
4. The changes, in order. Before the chain, frame 330's rulings seam passes 4 to 4i and two brief changes landed before night 170 at 26a44700 (`plans/archive/stack-2026-11-02.md:95-102`). They come before the first naming, so I do not count them.
   1. F2 with F3, frame 344's audit, merge 135c87d1 at 2026-10-28 02:43, "land f2root, F2 with F3, one parser of his line references and what they ask of a named target". Files: `rota/roles/api.py`, `rota/roles/principal.py`, `rota/core/runner.py` (git show). Kind: a door. Built before night 172. The next read: "Same. The read-back text, the empty-words text and the act text all fired on night 171" (`plans/night172-read.md:151`). Count: 65 of 93 calls refused, against 75 of 92 on night 171 (`plans/stack.md:325-326`).
   2. Sprint 32 row 1, branch f2b: f53ff5b0 "read his words from the record at the rulings door" and 7762b169 "read his reply, not the seat's words, at the naming door", merged at ee3464fc (06:47) and bf858f82 (08:36) on 2026-10-28. File: `rota/roles/api.py`. Kind: a door. Built before night 173 (night 173 ran on 36d2a667). The next read: refusals that held his words in a nested field, "9" to "0", and "The empty-words text is gone" (`plans/night173-read.md:144`, `:173`). Count: 33 of 51 refused (`plans/stack.md:278`).
   3. Sprint 33 row 1, merge 793aa684 at 2026-10-28 11:47, "land w7root at 9923a021, one reader of his words and the rulings door on his reply, F2 passes 2f to 2g and P7 passes 1 to 1e". Commits include 1a57eb2c, af557f43, 4d13a8d8, 3b31077a, 9923a021, 69561d5b. File: `rota/roles/api.py`. Kind: a door. Built before night 174. The next read: "68 of 81 refused from 33 of 51, and 12 refusals were wrong on his words: 7 by the clause-edge rule on act spans, 4 by a false key on a ref shown on two lines, 1 a team's-note revise" (`plans/stack.md:236-239`).
   4. Sprint 34 row 1, merge dfcffd40 at 2026-10-28 14:45, "land seamroot at 90c5d390, the rulings seam of nights 173 and 174, W1, W9, W16 and the two door faults". Commits d28e6e05, cb7783db, 5cd73a2d, 9b2d34d6, 3944adee, 22f98cf2, eed16a28. File: `rota/roles/api.py`. Kind: a door. Built before night 175. The next read: "90 were refused: 79 by a door and 11 by the parser. 20 rulings landed", "Night 174 refused 68 of 81", and "8 of the 90 refusals are wrong on his words" against 12 on night 174 (`plans/night175-read.md:128`, `:148`).
   5. Frame 345, the deep Liaison cases, after night 175: the L3 rulings cases at 0b7fcc3b (2026-10-29 01:21), then the menu ruling b9337a8c "land R, a menu per page line from its row kind" (10-29 14:10) and f5487759 "retire the word form of a page ruling and its doors" (10-29 15:22). Files: `rota/roles/api.py`, `tests/rota/cases/l3_rulings.yaml` (`plans/archive/stack-2026-10-30.md:141`). Kind: a door, and the harness for the measure. Frame 345 "closed at 21 of 24 on gemma4:12b-it-qat" (same line). The next read is dry1, which names no wall of the rulings door by id (absent only). dry1-W5 meets n175-W6 by a "not sure" link.
   - Count: 5.
5. The last change before the end: not applicable. The chain is open.
6. The place of the changes: the sign shows in the refusals of `rulings_rule` at `rota/roles/api.py:17200-17728` (`python -m rota.tools.map fn rulings_rule`). Changes 1 to 4 each touch `rota/roles/api.py`, the file of the door. The commit subjects name the rulings door, the naming door, the line parser and the act readers. Change 1 also touches `rota/roles/principal.py` and `rota/core/runner.py`. Change 5 replaces the word form of a page ruling with a menu in `rota/roles/api.py`, at `line_menu` and `menu_ruling` (`plans/archive/stack-2026-10-30.md:141`). All five touch the place of the sign.
7. Who started each change:
   1. Frame 344's audit, on Roman's message of 2026-10-27 14:08: "a few sessions ago we analyzed the completed frames and found that many did not fix the root cause. Go back and review them". Then Roman at 19:40: "I want all the fixes implemented before the next night" (extract c, nights 170 and 171, item 9).
   2. A read of a run: sprint 32 row 1, "recommended on night 172's read" (`plans/stack.md:309`, `:331-337`).
   3. A read of a run: sprint 33 row 1, "recommended on night 173's read" (`plans/stack.md:271`, `:286-291`).
   4. A read of a run, sprint 33 row 1 and sprint 34 row 1. It landed "on Roman's word of 14:45" (`plans/stack.md:244`).
   5. Roman, 2026-10-28 14:30: "Sounds like we need less doors and more in depth test cases". Frame 345 was "pushed on Roman's go" (commit 6bd52ad4; extract c, night 174, item 9).
8. The origin: the door is `rulings_rule` in `rota/roles/api.py`. The route of his words through the Liaison comes from b57772f5 (2026-09-10, "feat(seat): the principal's words land through the Liaison, not a parser"). Each refusal text has its own origin. `_faulted_approve` comes from f0b2924c (2026-10-16, "fix(api): the verdict door refuses an approve of a line the words fault"). Its message names night 149's s212, which approved lines that his words faulted. The list names "frame 250's approve refusal" in another chain (list line 342), and this pass did not check that f0b2924c belongs to frame 250. The text "Your last answer to this page did not reach the team" comes from 0582873a (2026-10-16), frame 267 (`plans/archive/stack-2026-10-17.md:122`). Frame 267 answered a reply whose session lands no ruling. Origin class: a frame that answered another wall: frame 267, a reply that landed no ruling; and the door of f0b2924c, night 149's wrong approve, frame not sure.
9. After the end: not applicable. The chain is open.

Row: Open | conditions changed | 5 | not applicable | doors of frames | origin frame: 267

### Chain 14: n170-W13, 5 turns, firm

1. The wall: "argument form and id refusals that a seat repeats [C?] (W13, F19, F22)" (`plans/method/turns-list-2026-11-10.md:336`; `plans/night170-read.md:69`). First turn night 170, last turn night 174, 5 turns. n170-W13 holds two signs, and the read places them under two facts: "F19 for s211; F22 for s209 and s200". Night 171 splits them into W11 and W13 (`plans/night171-read.md:68`, `:70`). So this block splits the chain.
   - Part A, ids from the wrong table, F22: n170-W13 (s209 `model.adopt` on b_3, s200 `tests.encode` on a b_1 id), n171-W11, n172-W16, n173-W15, n174-W18 (`plans/night172-read.md:73`, `plans/night173-read.md:72`, `plans/night174-read.md:77`). The reads say "Same as night 171's W11", "Same as night 172's W16", "Same as night 173's W15" (`plans/night172-read.md:161`, `plans/night173-read.md:187`, `plans/night174-read.md:222`). Turns n170 to n174, 5 turns. n175-W10 is "Same family as night 174's W18" (`plans/night175-read.md:187`), a "not sure" link in the extract.
   - Part B, argument form refusals that a seat repeats, F19: n170-W13 (s211 `msg.relay_vision_keeper`, round_no as words) and n171-W13 (`plans/night171-read.md:70`). Turns n170 and n171, 2 turns. n171-W13 meets n173-W14 by a "not sure" link (extract c, night 171, item 8). Part B alone does not reach four turns.
2. The state at the end:
   - Part A: Open. Night 174, one of the last three runs of the night series, named it (n174-W18).
   - Part B: Ended by the firm links. Nights 172, 173 and 174 name no wall of argument form refusals by a firm link. n173-W14, "the bg_3 Tester sends six broken bodies per turn", sits under the same fact F19 as "Same parse family as night 172's W18" (`plans/night173-read.md:186`). That is a "not sure" match, so the end rests on the firm links alone.
3. The conditions at the end:
   - Part A: open. The next runs after night 175 are dry runs, another kind of run. Conditions changed.
   - Part B: the last naming is night 171. Nights 172 to 174 ran on the same requests, the same models and the same repository (extract c, nights 172 to 174, item 2). Same.
4. The changes:
   - Part A, change 1. F22, frame 344's audit, merge 471ec356 at 2026-10-28 02:48, "land f22root, F22, one reader of the table an id lives in", with 538700af "four more sites read the one table reader". Files: `rota/core/db.py`, `rota/roles/api.py`, `rota/core/sandbox.py`, `rota/core/runner.py`, `rota/roles/principal.py` and five more (git show). Kind: other code of rota, one reader `db.table_of`. Built before night 172. The next read: "Same as night 171's W11", with 5 `model.adopt` refusals and one `ledger.log` refusal (`plans/night172-read.md:73`, `:161`). Night 173 counts 16 refusals, night 174 counts 8. The audit of 2026-10-30 marks F22 "FIXED" (`plans/rootfix-audit-2026-10-30-head.md:26`).
   - Part A count: 1.
   - Part B, change 1. F19, frame 344's audit, merge f8955d32 at 2026-10-27 18:10, "land f19root, F19, the quote forms from the parser". It deletes `_seat_forms`, `_one_backslash` and `_unescaped` in `rota/core/sandbox.py` (`plans/rootfix-audit-2026-10-30-head.md:23`). Kind: other code of rota. Built before night 172. The audit's aim: "night 170 W13 s211 repeated one call form 3 times ... go to 0 over 3 nights" (`plans/rootfix-audit-2026-10-27-b.md:34`). The next read, night 172, names no argument form wall. It counts "Seats repeat a refused call" as W18 (`plans/night172-read.md:75`). Night 173's W14 names 62 refusals of broken bodies in one session under F19.
   - Part B count: 1.
5. The last change before the end:
   - Part A: not applicable. Part A is open.
   - Part B: F19 at f8955d32. Evidence: absent only. Nights 172 to 174 name no such wall, and no read gives a count of argument form refusals that goes to 0. Night 173 names a sign under the same fact (n173-W14).
6. The place of the changes:
   - Part A: the sign shows in the id checks of the doors, `_must_exist` and the table helpers in `rota/roles/api.py`, `rota/core/runner.py` and `rota/roles/principal.py` (`plans/rootfix-audit-2026-10-27-b.md:55`). Change 1 adds `db.table_of` in `rota/core/db.py` and moves the helpers to it. It touches the place of the sign.
   - Part B: the sign shows in the call parser and the door texts on a call form, `rota/core/toolproto.py` and the relay tool. Change 1 touches the quote forms in `rota/core/sandbox.py`, `_quote_forms` and `_shown_views`. The relay refusal on round_no is another place. So change 1 touches another place for s211's sign, by the audit's own proposal.
7. Who started each change: both are rows of frame 344's audit, sprints 28 to 31, on Roman's message of 2026-10-27 14:08, "Go back and review them", and his message of 19:40, "I want all the fixes implemented before the next night" (extract c, nights 170 and 171, item 9). The audit names night 170's W13 as the evidence for both facts (`plans/rootfix-audit-2026-10-27-b.md:34`, `:58`).
8. The origin:
   - Part A: `_must_exist` comes from 6f2a2a7a (2026-08-10, "test(harness): the case runner, the obligation set, L1's first cases"). The text "is not a row of" comes from 84ea995f (2026-08-26, "feat(sandbox): observed gets its exit"). The audit says the helper set grew from 3 to 5 after frame 187 added an inline check (`plans/rootfix-audit-2026-10-27-b.md:57`). Origin class: rota's first design.
   - Part B: the call protocol comes from 231afe4c (2026-08-09, "feat(sandbox): namespaces built from edges, and the TOOL: protocol"). Origin class: rota's first design.
9. After the end:
   - Part A: not applicable. Part A is open. n175-W10 is "Same family", 113 `tests.retire` refusals (`plans/night175-read.md:66`, `:187`).
   - Part B: night 173 names n173-W14 under the same fact F19, with the Tester as the seat and a body as the call form. Not sure.

Row (Part A): Open | conditions changed | 1 | not applicable | rota's first design | origin frame: none
Row (Part B): Ended | same | 1 | absent only | rota's first design | origin frame: none

### Chain 24: n166-W3, 4 turns, firm

1. The wall: "an unasked answer wakes the Tester before the batch exists [C8] (W-C)" (`plans/method/turns-list-2026-11-10.md:346`; `plans/night166-read.md:211`). First turn night 166, last turn night 173, 4 turns. The walls are n166-W3, n169-W3, n170-W7, n173-W10 (`plans/night169-read.md:64`, `plans/night170-read.md:63`, `plans/night173-read.md:67`). Each names `msg.answer_tester` sent from the criteria tick before a batch exists, and a Tester woken on it whose writes the doors refuse. Night 170 says "as night 169's W3". The sign and the place are the same in all four, so the chain holds one wall.
2. The state at the end: Open by the rule, because night 173 is one of the last three runs of the night series. Only two night runs follow it. Night 174 counts "0 sessions; 0 fault rows", and "The answer door refused 4 `msg.answer_tester` calls of the Terminologist s228" (`plans/night174-read.md:238`). Night 175 counts "0; 0", and "The first Tester, s227, woke after s224 started bg_3" (`plans/night175-read.md:204`). Dry1 names no such wall (extract c, dry1, item 4).
3. The conditions at the end: the nights after night 173 ran on the same requests, models and repository. The nights stopped after night 175, and dry1 is another kind of run (extract c, night 175, item 9). Conditions changed after night 175.
4. The changes:
   1. Before the chain is a change that the cell 8 origin names. Between night 166 and night 169 no change aims at the wall. Sprint 23 keeps it as row 5, "W-C, next sprint rank 2: the answer door refuses an unasked answer in every mode. 1 read, 1 to 2 build" (`plans/stack.md:658-659`). The night 169 read says "No. 328's Site is `tests.encode`, which refused right. A candidate, C6" (`plans/night169-read.md:64`).
   2. F25, frame 344's audit, merge 552490b1 at 2026-10-28 00:28, "land f25root, F25, offers held to the seat's mode". Kind: a door and a prompt check. The night 170 read places W7 under F25 (`plans/night170-read.md:63`). Built before night 172. Night 172 names no such wall (absent only). Night 173 names it again as W10, with 16 refusals and 12 fault rows (`plans/night173-read.md:67`).
   3. Sprint 33 row 4, W10 of night 173: f0642982 "a message to a Tester or a Developer lands only on an item with a built batch" and 308b257f "the parked check reads the one batch predicate", merged at eeb0db69, 2026-10-28 14:08. File: `rota/core/sandbox.py`. Kind: a door. It landed after night 174 ended at 13:58, so night 174 ran without it (night 174 ran on 3ac83acc, `plans/stack.md:233`).
   4. W10 pass 1e: 7f7a6d88 "the encode door asks for a batch and the send door for its commit", merged at 21d145df, 2026-10-28 17:05:19, 27 seconds before night 175 launched (git log). File: `rota/roles/api.py`. Kind: a door. The next read: "**W10, `_unbuilt_refusal`.** 2 refusals, both in s222, `msg.answer_tester` ... The refusal is right by its rule" (`plans/night175-read.md:160`).
   - Count: 3 (changes 2, 3 and 4).
5. The last change before the end: not applicable by the rule, because the chain is open. The records show the sign absent on night 174 before changes 3 and 4 landed (`plans/night174-read.md:238`; git log, eeb0db69 at 14:08 after the run end at 13:58). So night 174's 0 is not joined to changes 3 and 4.
6. The place of the changes: the sign shows in `msg.answer_tester` from the Terminologist's criteria mode and the Tester's wake on it. The answer door in the criteria-tick mode does not fire, and the same door in the relay mode does (`plans/night169-read.md:64`). Change 2 touches the offers of each mode, another place by its subject. Change 3 touches the message landing in `rota/core/sandbox.py`, the place where the answer lands. Change 4 touches the encode door and the send door in `rota/roles/api.py`, the place of the refusal that s222 met.
7. Who started each change:
   - F25: frame 344's audit, on Roman's message of 2026-10-27 14:08, "Go back and review them" (extract c, night 170, item 9).
   - Changes 3 and 4: a read of a run, sprint 33 row 4, "recommended on night 173's read": "W10 and W20, a Tester woken before any batch exists writes 12 fault rows, under F25 and F6. Counts, then reads" (`plans/stack.md:299-302`).
8. The origin: the route comes from a3f2f96e (2026-10-24 01:41), "fix(terminologist): the criteria mode holds the route to the Tester". Its message: "Frame 306, pass 1b, from review 1, finding 1 ... so the criteria mode now holds msg.answer_tester" (git show). The status line of frame 306 says the same: "`criteria.tools` holds `msg.answer_tester`" (`plans/stack.md:2477`). Frame 306 answered his notes about a check that became criterion text, night 160's W2 (`plans/frame306-provenance-wa.md:100`, "Night 160 W2 is the same wall"). Night 166 is the first naming, two days later. Origin class: a frame that answered another wall: frame 306, wall n160-W2.
9. After the end: not applicable by the rule. Night 175 names "W10, `_unbuilt_refusal`", 2 right refusals of `msg.answer_tester` in s222, at the same seat and step (`plans/night175-read.md:160`). The read does not count it as a wall. Not sure.

Row: Open | conditions changed | 3 | not applicable | frame 306 route | origin frame: 306

### Chain 25: n171-W2, 4 turns, firm

1. The wall: "the account's description row reaches his pages after a rewording [C?] (W2)" (`plans/method/turns-list-2026-11-10.md:347`; `plans/night171-read.md:59`). First turn night 171, last turn night 174, 4 turns. The walls are n171-W2, n172-W9, n173-W8, n174-W7. The signs differ, so this block splits the chain.
   - Part A, n171-W2 alone: s152, a Vision Keeper woken by an unrelated deliver, re-asserted the `how_it_works` row with new words, the door took it, and the row reached m65 and m94 as a draft (`plans/night171-read.md:59`). 1 turn.
   - Part B, rows from other work on a request's page: n172-W9, "m71 lines 6 to 24 were glossary and constraint rows" (`plans/night172-read.md:66`), and n173-W8, "m56 carried 8 glossary and 14 constraint rows on the walk 2 request" (`plans/night173-read.md:65`). n174-W7 names the same kind of rows on account pages only, under the heading "A word that means more than one thing here" (`plans/night174-read.md:66`). The night 174 read says "Same rows as night 173's W8, now on account pages only. The heading is new in these reads" (`plans/night174-read.md:211`). Turns n172 to n174, 3 turns.
   - The night 172 read joins the parts: "Same sign as night 171's W2, with other rows: glossary, constraint and claim rows on a request's page" (`plans/night172-read.md:154`). The rows, the seat and the page differ, so I read two walls.
2. The state at the end:
   - Part A: Ended. Nights 172, 173 and 174 name no rewording of the description row (extract c, nights 172 to 174, item 4). The link of night 172 names other rows.
   - Part B: Open. Night 174, one of the last three runs of the night series, named it (n174-W7). The request-page sign itself fell: "rows of other work on a request page 36 to 0" on night 174 (`plans/stack.md:235-236`). n174-W7 holds the rows on account pages.
3. The conditions at the end:
   - Part A: nights 172 to 174 ran on the same requests, models and repository. Same.
   - Part B: open. The nights stopped after night 175, and the dry runs are another kind of run. Conditions changed.
4. The changes:
   - Part A, change 1. hiwroot, from the read `plans/night171-how-it-works-read.md`: f25b6303 "keep an observed description row's words outside onboarding", 2fb92e9c, 575e09b5 and 46c23831, landed at 5521b809 and bba2f842 on 2026-10-28 01:27 to 01:30 (git log; `plans/archive/stack-2026-10-30.md:221`, `:240`). Part A of the build is "a gate in problem_assert refuses a new text on an observed description row on every wake except onboarding". File: `rota/roles/api.py`. Kind: a door. Built before night 172. The next read names no rewording of the row (absent only).
   - Part A count: 1.
   - Part B, change 1. F15, frame 344's audit, merge 38a44c39 at 2026-10-28 02:48, "land f15root, F15, one reader of which request owns a row", with 7f1c7b6b and b68f9196. File: `rota/roles/principal.py`. Kind: other code of rota. Built before night 172. The night 172 read places W9 under F15: 2 pages, 26 lines (`plans/night172-read.md:66`). Night 173 counts 2 pages, 36 rows (`plans/night173-read.md:65`).
   - Part B, change 2. P8 and P9, merge 3ac83acc at 2026-10-28 11:48, "land w89root, a page is about one request, P8 and P9 under Roman's ruling of 2026-10-28 09:10". Commits 03876804 "the account's rows reach him on the account's page", 65cbda09 "a row of no request is off a request's page", 0d0bc33d. File: `rota/roles/principal.py` and the roles code. Kind: other code of rota, the page. Night 174 ran on 3ac83acc. The next read: "rows of other work on a request page 36 to 0" (`plans/stack.md:235-236`), and the same rows now stand on account pages under a new heading (n174-W7).
   - Part B count: 2.
5. The last change before the end:
   - Part A: hiwroot at bba2f842. Evidence: absent only. No read after it counts rewordings of the row.
   - Part B: not applicable. Part B is open.
6. The place of the changes:
   - Part A: the sign shows in `problem_assert`, the door that compares words only, at `rota/roles/api.py` about 2042 to 2056 (`plans/night171-how-it-works-read.md`, section 1). Change 1 puts a gate in `problem_assert`. It touches the place of the sign.
   - Part B: the sign shows in the page body of a request, `render_page` in `rota/roles/principal.py`. Change 1 adds one reader of the owner of a row in `rota/roles/principal.py`. Change 2 moves the account's rows to the account's page in the same file. Both touch the place of the sign.
7. Who started each change:
   - Part A: a read of a run, `plans/night171-how-it-works-read.md` (status of 2026-10-27 23:31, `plans/archive/stack-2026-10-30.md:207`), in the sprint that ran on Roman's message of 19:40: "I want all the fixes implemented before the next night".
   - Part B, change 1: frame 344's audit, on Roman's message of 2026-10-27 14:08, "Go back and review them".
   - Part B, change 2: sprint 32 row 4, a read of a run (`plans/stack.md:349-351`), and Roman's ruling of 2026-10-28 09:10, "Yeah that's right", to the answer "the account's own rows, the glossary, the constraints and the claims, go on their own page and never on a request's page" (`plans/stack.md:2977`).
8. The origin:
   - Part A: the read names the same-words door in `problem_assert`, overlap 0.8, and the signoff that submits every draft (`plans/night171-how-it-works-read.md`, sections 0 and 1). `_prose_words` comes from c6eb0274 (2026-09-01, "fix(sandbox): the intake fork"). The commit that set the 0.8 threshold is not found by this pass. Origin class: not found.
   - Part B: the rows come from `tick:observed_entries`, declared in 9c971e84 (2026-08-09, "feat(predicates): declare every predicate; no state is a dead end"). The night 174 read: "The rows are the survey's content, frame 179 by the facts page's unplaced list" (`plans/night174-read.md:211`). Origin class: rota's first design.
9. After the end:
   - Part A: n171-W1, in the same night, names the same row on another sign, "The contested description row cannot be amended" (`plans/night171-read.md:58`). After night 171, dry1-W5 names "how_it_works repeats; the landed approve is never read" (extract c, dry1, item 4), far after the end. Not sure.
   - Part B: not applicable. Part B is open. dry1-W15, "page m145 puts 15 re-survey constraints to the seat", meets n174-W7 by a "not sure" link (extract c, night 174, item 8).

Row (Part A): Ended | same | 1 | absent only | not found | origin frame: none
Row (Part B): Open | conditions changed | 2 | not applicable | rota's first design | origin frame: none

### Chain 26: n173-W3, 4 turns, firm

1. The wall: "the constraint tick is quarantined at the start [C?] (W3, F20)" (`plans/method/turns-list-2026-11-10.md:348`; `plans/night173-read.md:60`). First turn night 173, last turn dry1, 4 turns. The walls are n173-W3, n174-W10, n175-W13 (`plans/night174-read.md:69`, `plans/night175-read.md:69`), each "`-|tick:constraint_zero|` at 3", and dry1-W2, "constraint zero quarantined; the predicate wants every area" (`plans/dry1-first-wall-read-2026-10-31.md:6`). The key is the same in all four, so the chain holds one wall. The same key is Part A of chain 2 on nights 166 to 171, and n160-W8 names it on night 160. So the wall is older than this chain.
2. The state at the end: Ended. The chain crosses from the night series to the dry run series at dry1. dry2, dry3 and dry4, the three runs after dry1, name no such wall (extract c, dry1 item 8, "dry1-W2 to W4 ... not met in the next three reads"). The dry3 read lists "`constraint_zero n=1`" as outstanding, not quarantined (`plans/dry3-wall1-read-2026-11-02.md:42`).
3. The conditions at the end: the last night naming is night 175, and the nights stopped there. Dry1 ran on click, the same repository as the nights, with the session in the Principal seat (`plans/archive/stack-2026-11-02.md:195`). dry2 ran on tips, and dry3 and dry4 on other repositories (extract c, dry2 to dry4, item 2). The chain crosses from one series to the other, and the repository changed after dry1. Conditions changed.
4. The changes:
   1. F20 with F21, frame 344's audit, merge 82d426c4 at 2026-10-27 16:48 (the same change as chain 2, Part A). It landed before night 172, before this chain's first naming. The audit's proposal names "the constraint tick at onboarding (nights 160, 166 to 170)" and wants it at 0 over 3 nights (`plans/rootfix-audit-2026-10-27-b.md:42`). Kind: other code of rota. The night 173 read places W3 under F20, "Same as the F20 row's nights" (`plans/night173-read.md:175`). Nights 173, 174 and 175 each count the key at 3.
   2. Frame 354, commit e7016e65 at 2026-10-31 17:27, "fix(onboarding): constraint zero settles, and a quarantine report is never an empty page". Files: `rota/core/predicates.py`, `rota/onboarding/boot.py`, `rota/core/scheduler.py`, `rota/roles/api.py`, `rota/roles/principal.py`, `rota/core/sandbox.py`. Kind: other code of rota, and a door that refuses a present with no refs. The commit's own run: "constraint zero fired twice with refs and was never quarantined". Frame 354 closed on 2026-11-01 08:28: "condition 2 settled 1 of 1" (`plans/archive/stack-2026-11-01.md:100`). dry2 to dry4 name no such wall.
   - Count: 2.
5. The last change before the end: frame 354 at e7016e65. Evidence: a frame closes on a count. Frame 354's Ends-when holds "the predicate and the refresh use one rule for an area with code, so constraint zero settles and no quarantine row lands, after one onboarding replay confirms the cause" (`plans/archive/stack-2026-11-01.md:40`), and it closed on "condition 2 settled 1 of 1" (`:100`). The later dry runs do not name the key, but they ran on other repositories.
6. The place of the changes: the sign shows in the predicate `constraint_zero` at `rota/core/predicates.py` (about line 1880 at the read) and in `refresh_constraint_zero` at `rota/onboarding/boot.py` (about line 224) (`plans/dry1-first-wall-read-2026-10-31.md:26`). Change 1 touches the key readers in `rota/core/scheduler.py` and the word tables, another place. Change 2 touches the predicate and the refresh through `boot.coded_areas`, the place of the sign.
7. Who started each change:
   - F20 with F21: frame 344's audit, on Roman's message of 2026-10-27 14:08, "Go back and review them".
   - Frame 354: a read of a run, `plans/dry1-first-wall-read-2026-10-31.md`, pushed in a79fd411. The dry run itself came from Roman's ruling of 2026-10-31 00:58: "I will not sit in the seat untill it delivers multiple changes on multiple repos and is responsive. Use it yourelf" (extract c, night 175, item 9).
8. The origin: the same as chain 2, Part A. The predicate exists from 210649a7 (2026-08-09). The symbol filter in the refresh comes from 01e48a6f (2026-09-08): "Constraint zero bound every indexed area, including areas of pure prose ... k0 now binds only to areas with symbol grains". The predicate kept every area, and the dry1 read names that gap as the cause (reasoned, not replayed). 01e48a6f answers a wall of a cold walk on tipsC, 2026-09-04, and names no frame. Origin class: a fix that answered another wall, the prose-only walk of 2026-09-04, frame not found.
9. After the end: dry4-W1, "one `reconcile` key quarantines on the prose files", is another onboarding key at the start of a run (extract c, dry4, item 4). Frame 354's first condition aimed at the reconcile step. It is another tick at the same phase. Not sure.

Row: Ended | conditions changed | 2 | frame closes count | prose walk fix | origin frame: none

### Chain 28: n166-W2, 8 turns, not sure

1. The wall: "the naming door ignores the Liaison's own ask [C2] (W-B)" (`plans/method/turns-list-2026-11-10.md:353`; `plans/night166-read.md:210`). First turn night 166, last turn night 175, 8 turns: n166, n168, n170, n171, n172, n173, n174, n175. Rebuilt from column 8 of extract c: n166-W2 to n168-W7 (same cause); n168-W7 to n170-W4 (not sure); n170-W4 to n171-W7 (not sure); n171-W7 to n172-W5 (not sure, "the read says New"); n172-W5 to n173-W16 and n173-W9 (not sure, "New"); n173-W16 to n174-W5 and n175-W5 (same sign at the same place). The walls carry three signs, so this block splits the chain into three parts. The brief asks for two parts. Three parts are the honest split.
   - Part A, the naming door: n166-W2 and n168-W7, "the naming door reads his last answer only [C2]" (`plans/night168-read.md:110`). 2 turns.
   - Part B, a reading door misreads which line his words fault: n170-W4 "a door's text makes the Liaison contest an unfaulted criterion", n171-W7 "the rulings door reads a fault as no fault", n172-W5 "the rulings door lands a contest on a line his words do not name", n173-W9 "the rulings door reads a fault from another page's line number" (extract c, nights 170 to 173, item 4). 4 turns, joined by "not sure" links only. The reads call n172-W5 and n173-W9 "New" (`plans/night173-read.md:181`).
   - Part C, a landed act reverses his words: n173-W16, n174-W5 and n175-W5 (`plans/night173-read.md:73`, `plans/night174-read.md:64`, `plans/night175-read.md:61`). 3 turns, firm.
2. The state at the end:
   - Part A: Ended. Nights 169, 170 and 171 name no naming-door wall by a firm link (extract c, night 168, item 8).
   - Part B: Open by the rule. Night 173 is one of the last three runs of the night series. Night 174 counts the sign of W9 at "0" (extract c, night 173, item 8). Night 175 names no wall of Part B.
   - Part C: Open. Night 175 named it.
3. The conditions at the end:
   - Part A: nights 169 to 171 ran on the same requests, models and repository. Same.
   - Parts B and C: the nights stopped after night 175, and the dry runs are another kind of run. Conditions changed.
4. The changes:
   - Part A, change 1. Frame 337, "the naming door reads his earlier answers": 21f67802 and af60c5b9, landed as 7121f613 and 322da4b9 on 2026-10-26, before night 169 (`plans/f335-338-close-read-2026-10-30.md:14`, `:88`). File: `rota/roles/api.py`, `_unnamed_contest`. Kind: a door. Night 169 names no naming-door wall.
   - Part A, change 2. 7762b169 "read his reply, not the seat's words, at the naming door", 2026-10-28 06:46, branch f2b, in night 173's commit (git merge-base). Kind: a door. After the end.
   - Part A, change 3. f5487759, 2026-10-29 15:22, "retire the word form of a page ruling and its doors", which removes `_unnamed_contest`; then 939536c1 and fb27155b of frame 347 give the menu his earlier answers (`plans/f335-338-close-read-2026-10-30.md:88-89`). Kind: a door removed, and a prompt form. After the end.
   - Part A count: 3.
   - Part B: the changes of chain 7 to the rulings door: F2 with F3 at 135c87d1 (before night 172), f2b (before night 173), w7root at 793aa684 (before night 174), seamroot at dfcffd40 (before night 175), and frame 345's menu after night 175. The seam's commit 69561d5b, "an earlier page's numbers fault no line", aims at n173-W9 (`plans/seam-night173-read.md:11`). It is not in night 174's commit 3ac83acc (git merge-base), so night 174's "0" came before it. Part B count: 5.
   - Part C, change 1. seamroot, merge dfcffd40 at 2026-10-28 14:45, "the rulings seam of nights 173 and 174, W1, W9, W16". The read's proposal for W16: "a `remove` or `drop` on a code target lands only when its span asks for a removal" (`plans/seam-night173-read.md:11`). Commits d28e6e05 "a removal lands only on his named code target", 9b2d34d6 "a removal needs its target". File: `rota/roles/api.py`. Kind: a door. Built before night 175. The next read: n175-W5 "landed rulings reverse him" (`plans/night175-read.md:61`).
   - Part C, change 2. Frame 345's menu, b9337a8c and f5487759 on 2026-10-29, after the last naming. Kind: a door and the measure (24 L3R cases).
   - Part C count: 2.
5. The last change before the end:
   - Part A: frame 337. Evidence: a frame closes on a count. Frame 337 closed on 2026-10-30 17:33: "Naming-door refusals on a line his earlier answer names went from 2 of 2 to 0 on nights 169 to 175, reached once on night 175" (commit 613afc3b).
   - Parts B and C: not applicable. Both are open.
6. The place of the changes:
   - Part A: the sign shows in `_unnamed_contest` in `rota/roles/api.py`, which filled `words` with his last reply (`plans/archive/stack-2026-10-30.md:473`). Changes 1 to 3 touch that function or remove it. They touch the place of the sign.
   - Part B: the sign shows in the fault readers of `rulings_rule` in `rota/roles/api.py`. The changes touch the same file and function (chain 7, cell 6).
   - Part C: the sign shows where an act lands and where `granted` reads it as his permission: "The act check proves only that the span is his words (api.py 13774 to 13786). `granted` then reads the act as his permission" (`plans/seam-night173-read.md:9`). Change 1 touches the act check in `rulings_rule`. Change 2 replaces the word form. Both touch the place of the sign.
7. Who started each change:
   - Part A, change 1: a read of a run, sprint 25 row 5, "W7, W-B of night 166" (`plans/stack.md:548`), and Roman, 2026-10-26 19:30: "are we not fixing all the things in one go before the next night?" (extract c, night 168, item 9).
   - Part A, change 2: a read of a run, sprint 32 row 1 (`plans/stack.md:331-337`).
   - Part A, change 3, and Part C, change 2: Roman, 2026-10-28 14:30: "Sounds like we need less doors and more in depth test cases" (frame 345).
   - Part B: as chain 7, cell 7.
   - Part C, change 1: a read of a run, sprint 33 row 1, "recommended on night 173's read" (`plans/stack.md:286-291`), landed "on Roman's word of 14:45" (`plans/stack.md:244`).
8. The origin:
   - Part A: `_unnamed_contest` comes from 250f3806 (2026-10-14), "the verdict door refuses a contest on a line the principal's words do not name". It is frame 234's pass 2 (`plans/archive/stack-2026-10-15.md:29`; `plans/archive/stack-2026-10-30.md:473`). Its message names night 147's m131, where the Liaison contested lines that his words did not fault. Origin class: a frame that answered another wall: frame 234, the over-contest of night 147's m131.
   - Part B: the fault readers of `rulings_rule`. `_faulted_approve` comes from f0b2924c (2026-10-16), as in chain 7. Origin class: a frame that answered another wall: frame not sure, night 149's wrong approve.
   - Part C: the act check comes from 76f2f981 (2026-10-27 03:09), "an act is checked against his words before it is written". It is in night 170's commit 26a44700 (git merge-base). The seam read says "No build claimed this check" for the verb (`plans/seam-night173-read.md:95`). The frame of 76f2f981 is not found by this pass. Origin class: not found.
9. After the end:
   - Part A: night 170 names n170-W4, a door text that makes the Liaison contest an unfaulted criterion, at the same seat and the same door family. Not sure.
   - Parts B and C: not applicable. Both are open.

Row (Part A): Ended | same | 3 | frame closes count | frame 234 door | origin frame: 234
Row (Part B): Open | conditions changed | 5 | not applicable | fault reader door | origin frame: none
Row (Part C): Open | conditions changed | 2 | not applicable | not found | origin frame: none

### Chain 29: n166-W1, 6 turns, not sure

1. The wall: "the Tester's three bg_3 tests are red on any code [C5] (W-A)" (`plans/method/turns-list-2026-11-10.md:354`; `plans/night166-read.md:209`). First turn night 166, last turn night 174, 6 turns: n166, n167, n170, n172, n173, n174. Rebuilt from column 8 of extract c: n166-W1 to n167-W7 (not sure); n167-W7 to n170-W1 (not sure); n170-W1 to n172-W15 and n173-W13 (not sure, "the same door, sessions land tests later"); n172-W15 to n173-W13 and n174-W17 (same sign at the same place). The walls carry two signs, so this block splits the chain.
   - Part A, a Tester's test that the code cannot pass: n166-W1, three tests that assert what the right docstring cannot return, and n167-W7, "The Tester's test path replaces the module under test ... 35 of 35 tests error at fa4e8230" (`plans/night167-read.md:100`). Frame 328 holds both (extract c, night 166 item 6; `plans/stack.md:596-600`). 2 turns, joined by a "not sure" link.
   - Part B, the test-file door: n170-W1, "The test-file door refuses every path the Tester sends for the docstring criterion, and the key quarantines", 12 "is already inh_..'s file" refusals (`plans/night170-read.md:57`); n172-W15, n173-W13 and n174-W17, "the test-file door fires; sessions land tests later" (extract c, nights 172 to 174, item 4). 4 turns.
2. The state at the end:
   - Part A: Ended. Nights 168, 169 and 170 name no such wall by a firm link (extract c, night 167, item 8). n170-W1 meets it by a "not sure" link.
   - Part B: Open. Night 174, one of the last three runs of the night series, named it.
3. The conditions at the end:
   - Part A: the model changed. Night 168 ran on Gemma, "frame 323's second Gemma night, on Roman's word of 09:01" (`plans/stack.md:499-500`). Night 169 ran on "qwen3.5:9b in every seat" (`plans/stack.md:557-559`). Conditions changed.
   - Part B: open. The nights stopped after night 175, and the dry runs are another kind of run. Conditions changed.
4. The changes:
   - Part A, change 1. Frame 328, W-A, passes 1 to 3 on the branch, "Validating at a875a798" at 2026-10-26 03:52, before night 167 (extract c, night 166, item 6). a875a798 is dated 2026-10-26 03:05. Kind: a door at the encode and a route of the red to the Tester (frame 328's heading, "a red at encode goes back to the Tester", `plans/stack.md:648-649`). Night 167 names W7, another sign.
   - Part A, change 2. Frame 328, pass 4, sprint 24 row 2: "`tests.encode` refuses a test path that is a file of the code index outside the test folders, and a run that errors at collection goes back to the Tester as a red" (`plans/stack.md:596-600`). Pass 4b at a79474fd (commit d0902a1a, 2026-10-26 08:04). Night 168 "runs cold from the head of rows 2 and 3" (`plans/stack.md:621-624`). Kind: a door. Night 168 names no such wall (absent only).
   - Part A count: 2.
   - Part B, change 1. Frame 343, pass 1 at 685f44dc, "the test-file door offers a filled call to a new file beside a project test file, and tests_missing.md says the touch path with the project's tests is not the Tester's" (commit e904b295, status 2026-10-27 14:10). The branch commit is 6f7ab327, "offer a new file beside a project test file at the encode". Night 171 ran on 9827e38a with it (extract c, night 170, item 6). Kind: a door and a prompt. Night 171 names no such wall. Night 172 names W15: the door fires, and sessions land tests on the next call.
   - Part B, change 2. F35, merge 7021f964 at 2026-10-28 02:44, "one reader of the predicted files less the paths his words decline", and F31, merge e42d13d1 at 2026-10-27 18:56, "one asks_for_docs". The night 170 read places W1 under "F35 ... with F31" (`plans/night170-read.md:57`). Kind: other code of rota. Built before night 172. Night 172 and night 173 name the door again.
   - Part B count: 2.
5. The last change before the end:
   - Part A: frame 328's pass 4. Evidence: absent only. Frame 328 closed on 2026-10-31 01:58 with "328's count was ruled taken by a case or not at all" (commit 3c82ffa2), not on a night count.
   - Part B: not applicable. Part B is open. Frame 343 "closes at 0 of 3 on three nights with the door firing 12 times" (`plans/stack.md:279-280`).
6. The place of the changes:
   - Part A: the sign shows in `tests.encode` in `rota/roles/api.py`, which "checks only that the path ends in `.py`" (`plans/night167-read.md:100`), and in the route of a red run. Both changes of frame 328 touch `tests.encode` and the route. They touch the place of the sign.
   - Part B: the sign shows in the test-file clash refusal in `rota/roles/api.py` about lines 13447 to 13500 ("is {clash['id']}'s file", grep). Frame 343 touches that door and the brief `tests_missing.md`, the place of the sign. F35 and F31 touch the readers of the predicted files and of a docs criterion, another place.
7. Who started each change:
   - Part A, change 1: a read of a run, sprint 23 row 1 on night 166's read (`plans/stack.md:648-650`).
   - Part A, change 2: a read of a run, sprint 24 row 2 on night 167's read (`plans/stack.md:596`).
   - Part B, change 1: a read of a run, night 170's read, which pushed frame 343 in its own commit (extract c, night 170, item 5).
   - Part B, change 2: frame 344's audit, on Roman's message of 2026-10-27 14:08, "Go back and review them".
8. The origin:
   - Part A: frame 328's provenance read: "The encode door ran s198's tests on the head and let the red assertions through on purpose, frame 304's rule a3ce3f01 of 2026-10-23" (commit 3c82ffa2, frame 328 status of 2026-10-25 23:00). This pass did not read which wall frame 304 answered. Origin class: a frame that answered another wall: frame 304, wall not found.
   - Part B: the text "two tests in one file" of the clash refusal comes from e8c68bec (2026-09-02, "fix(sandbox): walk twelve -- the dispute reaches the seat, two more harness facts"). The night 170 read gives the cause: "The brief tells the Tester to use a path under `touch`, and every touch test path is a project test's file" (`plans/night170-read.md:57`). Origin class: a fix that answered another wall, a walk of 2026-09-02, frame not found.
9. After the end:
   - Part A: night 170 names n170-W1, the test-file door on the same seat and step, the Tester's encode. Not sure.
   - Part B: not applicable. Part B is open.

Row (Part A): Ended | conditions changed | 2 | absent only | frame 304 rule | origin frame: 304
Row (Part B): Open | conditions changed | 2 | not applicable | walk twelve fix | origin frame: none

### Chain 36: n160-W5, 4 turns, not sure

1. The wall: "page after a review with no verdict says the team stopped [C11] (W5)" (`plans/method/turns-list-2026-11-10.md:361`; `plans/night160-read.md:275`). First turn night 160, last turn night 163, 4 turns: n160, n161, n162, n163. Rebuilt from column 8: n160-W5 to n161-W7 (not sure) and to n163-W5 (same cause, "Frame 312") (extract b, night 160, item 8); n161-W7 to n162-W6 (not sure) (extract c, night 161, item 8). The walls carry two signs, so this block splits the chain.
   - Part A, a stop page that hides or misstates the state: n160-W5, "The page after a review with no verdict says the team stopped work, and he parked bg_1 on that belief" (`plans/night160-read.md:275`), and n163-W5, "The stuck after an all-approve, and stop pages that hide the cause ... Frame 312" (`plans/night163-read.md:183`). 2 turns.
   - Part B, a send with no text becomes an invented question: n161-W7, "The Vision Keeper's report with no words became a three-item question" (`plans/night161-read.md:288`), and n162-W6, "A textless propose became an invented question ... Frame 303's seam" (`plans/night162-read.md:333`). 2 turns.
2. The state at the end:
   - Part A: Ended. Nights 164a, 164 and 165 name no such wall (extract c, night 163, item 8, "n163-W5, W6, W8, W9: not met in n164, n165"). Night 164a has no read page of its own. `plans/night164-read.md` names one wall of it, W-F, so night 164a is "not named", not "gone".
   - Part B: Ended. Nights 163, 164a and 164 name no such wall (extract c, night 162, item 8, "n162-W4 to W8: not met in n163, n164; n164a: no read"). Night 164a is thin in the same way.
3. The conditions at the end:
   - Part A: the last naming is night 163, the first night on the trio R2 (`plans/method/turns-list-2026-11-10.md:243`). Nights 164a, 164 and 165 ran on the same requests, models and repository. Same between the last naming and the next three. The requests changed inside the chain, between night 162 (R1) and night 163 (R2).
   - Part B: the last naming is night 162, on R1. The next run, night 163, is the first on R2. Conditions changed.
4. The changes:
   - Part A, change 1. Frame 312, pass 1 and 1b: ced9de67 "the stopped page and the shift page name a quarantined review" and cc013d96 "a stuck tick reaches the principal in plain words", 2026-10-24 01:27 and 01:35 (+0100). File: `rota/roles/principal.py`. Kind: other code of rota, the page. Built before night 161 (extract b, night 160, item 6; both are ancestors of night 162's commit 214d22d0). Night 161 names no such wall. Night 163 names W5 with "Frame 312" as its place.
   - Part A, change 2. Frame 312, row 5's pass and passes 1b and 1c, commits 1694320b, c515e7f7 and 7f29d9e1 of 2026-10-24 21:19 to 21:46 (git log, author time). The close names "an answer lifts the `batch_start` key at `land` ... from 6785f35b" (commit b319696a). Kind: other code of rota. Nights 164 and 165 name no such wall (absent only).
   - Part A count: 2.
   - Part B, change 1. Frame 303's case, sprint 19 row 7, "a textless propose is refused, with s228 to s234 and m110" (`plans/stack.md:856-857`). It landed on night 163's commit 5758cc46 as 6862e93b "a Liaison wake resolves a batch ref to its item, state and verdict" and 970cbd81 "a batch verdict names its commit, and the report brief reads the batch row" (git merge-base). Files: `rota/core/` and the report brief. Kind: other code of rota and a brief of a seat. Night 163 names no such wall. Frame 303's status: "Past its night 3. Not exercised: 0 propose calls" (frame 303, status 2026-10-24 18:19 BST, `plans/stack.md` under heading 303).
   - Part B count: 1.
5. The last change before the end:
   - Part A: frame 312's row 5 pass. Evidence: a frame closes on a count. Frame 312 closed on 2026-10-30 17:44: "Pages after a review with no verdict that say \"stopped work\": 0 of 1 on night 171, m40, after 0 on night 161, from 2 on night 160" (commit b319696a). The count is of the first sign only.
   - Part B: frame 303's case. Evidence: absent only. Frame 303's last count is of propose calls, 0, which is another sign.
6. The place of the changes:
   - Part A: the sign shows in the stopped page text and the shift page in `rota/roles/principal.py` (frame 312's Site, `plans/archive/stack-2026-10-30.md:498`). Both changes touch that file: `_stuck_ticks` and `TICK_WORDS` for the page, and `land` for the lift. They touch the place of the sign.
   - Part B: the sign shows at the Architect's and the Vision Keeper's report edge to the Liaison, refs with no text, and in the Liaison's next page. The change touches the Liaison's wake and the report brief, the place where the empty send is read.
7. Who started each change:
   - Part A: a read of a run, sprint 17 row 4: "pushed from night 160's read, section 2, W5, by sprint 17's row 4" (`plans/archive/stack-2026-10-30.md:503`). Roman ruled the second half on 2026-10-24 01:30: "Yes there needs to be a passing review" (same frame, Waits-on line).
   - Part B: a read of a run, sprint 19 row 7 on night 162's read (`plans/stack.md:856`).
8. The origin:
   - Part A: the text "The team stopped work on this change" comes from 358fed11 (2026-10-09), "every page to the principal numbers the request's own lines first", frame 190's pass 1, the page (`plans/archive/stack-2026-10-10.md:17`). This pass did not read which wall frame 190 answered. Origin class: a frame that answered another wall: frame 190, wall not found.
   - Part B: `msg.report_liaison` exists from 7fcec388 (2026-08-09). Frame 303's case names the cause: "the seam is the Architect's report edge to the Liaison, refs only by the ruling of 2026-08-15" (frame 303, status 2026-10-24 15:42). Origin class: rota's first design.
9. After the end:
   - Part A: night 164 names n164-W1, "a batch with a retired criterion never reaches the Critic", and night 165 names n165-W9, "bg_1 ends with 2 red tests". Neither is a page sign. Not sure.
   - Part B: night 163 names n163-W6, "item 2 dies at its first Liaison session, four refused clarifies", at the Liaison seat. Not sure.

Row (Part A): Ended | same | 2 | frame closes count | frame 190 page | origin frame: 190
Row (Part B): Ended | conditions changed | 1 | absent only | rota's first design | origin frame: none

### Chain 37: n167-W2, 4 turns, not sure

1. The wall: "a body's backslash loses one escape level in the call [C4] (W2)" (`plans/method/turns-list-2026-11-10.md:362`; `plans/night167-read.md:95`). First turn night 167, last turn night 171, 4 turns: n167, n168, n169, n171. Rebuilt from column 8: n167-W2 to n168-W1 (same cause, "C4, the escape level") and to n169-W4 (not sure); n168-W1 to n169-W4 (same sign at the same place) and to n171-W3 (not sure); n169-W4 to n171-W3 (not sure) (extract c, nights 167 to 169, item 8). The walls carry two signs, so this block splits the chain.
   - Part A, an invalid escape passes rota's parse: n167-W2, n168-W1 "a body's backslash loses an escape level; encode admits the invalid escape" (`plans/night168-read.md:104`), and n169-W4 "A Developer write with an invalid escape passes rota's parse with a warning" (`plans/night169-read.md:65`). The night 169 read names the place as "a second site": `code.write`, not `tests_encode`. 3 turns.
   - Part B, n171-W3, "The escape door's advice produces a test that cannot pass on Windows", s153 told to "Write the path with forward slashes" (`plans/night171-read.md:60`). 1 turn. It is the advice of the door that frame 335 built for Part A (cell 8).
2. The state at the end:
   - Part A: Ended. Nights 170, 171 and 172 name no such wall by a firm link (extract c, night 169, item 8). n171-W3 meets it by a "not sure" link.
   - Part B: Ended. Nights 172, 173 and 174 name no such wall (extract c, night 171, item 8, "n171-W1, W3, W8, W9, W12: not met").
3. The conditions at the end:
   - Part A: the chain starts on models C (nights 167 and 168) and ends on models B (night 169) (`plans/method/turns-list-2026-11-10.md`, the run lines of nights 167 to 169). Nights 170 to 172 ran on trio R2, clickI and models B, the same as night 169. Same.
   - Part B: nights 172 to 174 ran on R2, clickI and models B, the same as night 171. Same.
4. The changes:
   - Part A, change 1. Frame 335, "The encode check lets an invalid escape through as a warning" (`plans/archive/stack-2026-10-30.md:442`): 71642373 "refuse an invalid escape at encode and name its raw form", 9a22a120 "give escape advice that the call keeps, on escapes only", and 0fcbce6d "name a real backslash form and no wrong form in escape advice", 2026-10-26, closed as a mechanism at 0fcbce6d at 19:32 (extract c, night 168, item 6). All are in night 169's commit 322da4b9 (git merge-base). File: `rota/roles/api.py`, `tests_encode`. Kind: a door. The next read names n169-W4 at another site: "**Partly, 335.** Its Site names the parse in `tests_encode`, not in `code.write`" (`plans/night169-read.md:65`).
   - Part A, change 2. F19, merge f8955d32 at 2026-10-27 18:10, "the quote forms from the parser". Kind: other code of rota. In night 172's commit de1203a9. It came after nights 170 and 171, which already did not name the wall.
   - Part A count: 2.
   - Part B, change 1. d6a9efe6 at 2026-10-27 19:38, "give escape advice that keeps the value of the string first", "the W3 advice fix at d6a9efe6 about 54k under frame 344" (`plans/archive/stack-2026-10-30.md:457`). File: `rota/roles/api.py`. Kind: a door text. In night 172's commit de1203a9. Night 172 names no such wall (absent only).
   - Part B count: 1.
5. The last change before the end:
   - Part A: frame 335 at 0fcbce6d, before night 169. Night 169 still names the sign at `code.write`, which no change touched: "The code.write site of night 169's W4 stays outside this frame" (`plans/archive/stack-2026-10-30.md:457`). The close read counts "0 `SyntaxWarning` lines on 170 to 173" (`plans/f335-338-close-read-2026-10-30.md:45`) and "Landed encodes that err at collection on an escape went from 6 of 7 to 0 on nights 170 to 175". Evidence: a frame closes on a count for the encode site. For the `code.write` site the sign is absent with no change at that site, and no record says why.
   - Part B: d6a9efe6. Evidence: absent only.
6. The place of the changes:
   - Part A: the sign shows at the seat's call form (two escape levels), at `tests_encode`, and at `code.write` (`plans/night169-read.md:65`). Change 1 touches `tests_encode` and its advice. It does not touch `code.write` ("No `simplefilter(\"error\"...)` exists outside `tests_encode` and `_form_value` at HEAD", `plans/f335-338-close-read-2026-10-30.md:45`). Change 2 touches the quote forms in `rota/core/sandbox.py`, another place.
   - Part B: the sign shows in the escape advice of the encode door in `rota/roles/api.py`. Change 1 touches that advice. It touches the place of the sign.
7. Who started each change:
   - Part A, change 1: a read of a run, candidate C2 of night 167's read (`plans/night167-read.md:95`), pushed as frame 335 at night 168's close (extract c, night 168, item 6), with Roman's message of 2026-10-26 19:30: "are we not fixing all the things in one go before the next night?".
   - Part A, change 2: frame 344's audit, on Roman's message of 2026-10-27 14:08, "Go back and review them".
   - Part B: frame 344's work on night 171's read, under Roman's message of 2026-10-27 19:40, "I want all the fixes implemented before the next night".
8. The origin:
   - Part A: the night 167 read names cause 4, "the call form needs two escape levels", and cause 8, "a collection error is not a red" (`plans/night167-read.md:95`). The call form comes from 231afe4c (2026-08-09, "the TOOL: protocol"). Origin class: rota's first design.
   - Part B: `git log -S "forward slashes"` gives 9a22a120 (2026-10-26 18:56), "give escape advice that the call keeps, on escapes only", a pass of frame 335. Frame 335 answered n167-W2 and n168-W1, which are Part A. Origin class: a frame that answered another wall: frame 335, walls n167-W2 and n168-W1.
9. After the end:
   - Part A: night 171 names n171-W3, the advice of the escape door, at the same seat and step, the encode of a test body with a backslash. Not sure.
   - Part B: nights 172 to 174 name no escape wall. n173-W14, "the bg_3 Tester sends six broken bodies per turn", sits under F19 (`plans/night173-read.md:186`). Not sure.

Row (Part A): Ended | same | 2 | frame closes count | rota's first design | origin frame: none
Row (Part B): Ended | same | 1 | absent only | frame 335 advice | origin frame: 335

### Chain 38: n169-W1, 4 turns, not sure

1. The wall: "the removal door reads his permission by one phrase [C11] (W1)" (`plans/method/turns-list-2026-11-10.md:363`; `plans/night169-read.md:62`). First turn night 169, last turn night 174, 4 turns: n169, n171, n172, n174. Rebuilt from column 8: n169-W1 to n171-W4 (not sure, "removals with no grant land, the opposite sign"); n171-W4 to n172-W2 (same sign at the same place) and to n174-W15 (not sure); n172-W2 to n174-W15 (not sure) (extract c, nights 169, 171 and 172, item 8). The walls carry two opposite signs, so this block splits the chain.
   - Part A, the removal door refuses or holds a commit: n169-W1, "each commit that removes line 518 is refused" after his grants, 28 removal refusals (`plans/night169-read.md:62`), and n174-W15, "The commit gate holds a write with an unread removal note", 2 refusals, "Same family as frame 339's door" (`plans/night174-read.md:74`, `:219`). 2 turns.
   - Part B, removals with no grant land: n171-W4, "A Developer deletes code he did not ask to change, and the commit lands" (`plans/night171-read.md:61`), and n172-W2, "the commits remove base code with no grant", "Same outcome as night 171's W4" (`plans/night172-read.md:59`, `:147`). 2 turns.
2. The state at the end:
   - Part A: Open. Night 174, one of the last three runs of the night series, named it.
   - Part B: Ended. Nights 173, 174 and 175 name no such wall by a firm link. Night 173: "Row 2 was not reached, because bg_3 removed no code" (`plans/stack.md:278-279`). n174-W15 meets it by a "not sure" link.
3. The conditions at the end:
   - Part A: open. The nights stopped after night 175, and the dry runs are another kind of run. Conditions changed.
   - Part B: nights 173 to 175 ran on R2, clickI and models B, the same as night 172. Same.
4. The changes:
   - Part A, change 1. Frame 339, "The removal door reads the principal's permission by one fixed phrase" (`plans/archive/stack-2026-10-28.md:22`). Commits include 076ea892 "the removal door records a stray for the Architect instead of refusing the commit" (2026-10-26 22:43), 4e58ad9c, d495db74, 99d88c8e and 5480f6b6 "the permission readers read act and target from the record per ref" (2026-10-27 02:49). The status: "The mechanism is on the branch" at 05:11, in night 170's commit 26a44700 (extract c, night 169, item 6). File: the roles code of the removal door. Kind: a door. Nights 170, 171, 172 and 173 name no such wall.
   - Part A count: 1.
   - Part B, change 1. F7 with W4, frame 344's audit, merge c8c819cd at 2026-10-28 01:01, "land f7root, F7 with W4, the commit compares the base with the tree". Pass 2 at aae59d4b: "night 171's commit names both of s164's removals ... a statement that moves under a new if or loop counts as removed" (`plans/archive/stack-2026-10-28.md:52`). Kind: a door. In night 172's commit de1203a9. The next read: n172-W2, "removals with no grant land, and no door refuses. New beside it: the stray route judged this one a mistake (s262)" (`plans/night172-read.md:147`).
   - Part B, change 2. Sprint 32 row 2, branch f7b: f6b0f41f "show the removed lines in the touch_mistaken wake", e855bd79 "show the judged row and grade the head in the restore wake", 00186009 "keep the mistake notes out of the touch_mistaken cycle key", merged at 27f8b53b and 36d2a667 on 2026-10-28 07:56 and 08:37. Kind: a prompt of a seat and a cycle key. In night 173's commit 36d2a667. The next read: "Row 2 was not reached, because bg_3 removed no code" (`plans/stack.md:278-279`).
   - Part B count: 2.
5. The last change before the end:
   - Part A: not applicable. Part A is open. Frame 339 closed on 2026-10-28 14:18: "Ends-when held on nights 172, 173 and 174: Developer sessions refused at the removal door after an answer that grants the removal, 0 of 1 on each night, one sample per night" (`plans/archive/stack-2026-10-28.md:57`). The same night 174 names W15 at the commit gate.
   - Part B: f7b at 36d2a667. Evidence: absent only. Night 173 says the row "was not reached, because bg_3 removed no code", so the case did not occur. Nights 174 and 175 name no removal with no grant by a firm link.
6. The place of the changes:
   - Part A: the sign shows in the removal door at the commit, its "line N" matcher and the sentence the page offers (`plans/archive/stack-2026-10-28.md:33`). Change 1 touches the removal door and the permission readers. It touches the place of the sign. n174-W15 shows at the same commit gate, on an unread removal note.
   - Part B: the sign shows at the commit, where no door refused removals of base code. Change 1 touches the commit's compare of the base with the tree, the place of the sign. Change 2 touches the `touch_mistaken` and restore wakes, the route after the sign, another place.
7. Who started each change:
   - Part A: a read of a run, `plans/night169-m36-read.md`, during night 169. Frame 339 was "pushed 20:47 from the m36 read" (extract c, night 169, item 6).
   - Part B, change 1: frame 344's audit, on Roman's message of 2026-10-27 14:08, "Go back and review them".
   - Part B, change 2: a read of a run, sprint 32 row 2 on night 172's read (`plans/stack.md:338-344`).
8. The origin:
   - Part A: frame 339's provenance read: "no ruling made the removal door, the session built it in frame 283 W1a pass 1 at 92e240fc on 2026-10-21 from night 158's read ... the 'line N' matcher came at 2acc7b5c on 2026-10-23 in pass 2 with no brief, status line or review that asked for it; the sentence to copy came at e1cfcdd2 on 2026-10-24 in frame 312" (`plans/archive/stack-2026-10-28.md:33`). This pass did not read which wall of night 158 frame 283 answered. Origin class: a frame that answered another wall: frame 283, a wall of night 158's read.
   - Part B: the same removal door of frame 283, which did not see a removal inside a rewrite. F7's subject says the commit did not compare the base with the tree before 2026-10-28. The commit that set the old compare is not found by this pass. Origin class: not found.
9. After the end:
   - Part A: not applicable. Part A is open.
   - Part B: night 174 names n174-W15 at the same commit and seat, the Developer, with the opposite sign. Night 175 names n175-W9, "a Developer writes the criteria into the code". Not sure.

Row (Part A): Open | conditions changed | 1 | not applicable | frame 283 door | origin frame: 283
Row (Part B): Ended | same | 2 | absent only | not found | origin frame: none

### Chain 39: n170-W15, 4 turns, not sure

1. The wall: "pages after the stop say \"check: none yet\" [C?] (W15, F21)" (`plans/method/turns-list-2026-11-10.md:364`; `plans/night170-read.md:71`). First turn night 170, last turn dry1, 4 turns: n170, n172, n175, dry1. Rebuilt from column 8: n170-W15 to n172-W12 (not sure); n172-W12 to n175-W1 (not sure); n175-W1 to dry1-W7 (same sign at the same place, "the causes differ") (extract c, nights 170, 172 and 175, item 8). The walls carry two signs, so this block splits the chain.
   - Part A, a stop page whose check lines misstate the tests: n170-W15, "The pages after the stop say \"check: none yet\"" on m96 and m102 (`plans/night170-read.md:71`), and n172-W12, "The page says the tests fail, and every check line on it says \"Passes\"" (`plans/night172-read.md:69`). 2 turns.
   - Part B, the `tests_missing` tick stops a batch at 3 attempts: n175-W1, "The `tests_missing` tick on c_2 and c_3 stops bg_3" (`plans/night175-read.md:57`), and dry1-W7, "a dotted surface ref passes the vet; encode refuses every test" (`plans/dry1-third-wall-read-2026-11-01.md:7`). 2 turns. The sign is the same and the causes differ: on night 175 his deletion of c_2 and c_3 never reached the criteria (n175-W2), and on dry1 the Terminologist stored `surface_refs=['click.pause']`.
2. The state at the end:
   - Part A: Ended. Nights 173, 174 and 175 name no such wall by a firm link. Night 173 counts the sign at "0. No tick gave up on tests and no page stopped" (`plans/night173-read.md:205`). So on night 173 the case did not occur.
   - Part B: Ended. dry2, dry3 and dry4 name no such wall (extract c, dry1, item 8).
3. The conditions at the end:
   - Part A: nights 173 to 175 ran on R2, clickI and models B, the same as night 172. Same.
   - Part B: the chain crosses from the night series to the dry run series at dry1. Dry1 ran on click, and dry2 to dry4 ran on other repositories. Conditions changed.
4. The changes:
   - Part A, change 1. F20 with F21, merge 82d426c4 at 2026-10-27 16:48 (chain 2). The audit says "W15, \"check: none yet\", comes from `_gave_up_tries` reading the page's keys, which is F20" (`plans/rootfix-audit-2026-10-27-b.md:50`). Kind: other code of rota. In night 172's commit. The next read names W12: "New. The page shows the tick's words and no red line, because the red test has no criterion and no line" (`plans/night172-read.md:157`).
   - Part A, change 2. w12root, merge 189dc7b2 at 2026-10-28 10:07, "the stopped page names the red test, night 172's wall W12", with 61608940 "the stopped page names the red test". File: `rota/roles/principal.py` and the roles code. Kind: other code of rota, the page. It landed after night 173 ended at 10:00 and is in night 174's commit 3ac83acc. Nights 174 and 175 name no such wall (absent only).
   - Part A count: 2.
   - Part B, change 1. For n175-W1, no change found. Sprint 35 does not name it (grep of `plans/stack.md:149-230`).
   - Part B, change 2. Frame 356, "A dotted surface ref passes the vet as written, and the encode door refuses every test for the criterion" (`plans/archive/stack-2026-11-01.md:102`): eeed30cc "one resolver reads a surface ref for the vet and the encode door" and 584f7f91 "a method grain only when the class defines the method", 2026-11-01. Kind: other code of rota. Frame 356 closed at 18:25 on dry1 turn 12: "the Tester wrote a test for each of the three criteria in 9 sessions with 0 never-calls refusals, against about 50 on the three sessions of the third wall".
   - Part B count: 1.
5. The last change before the end:
   - Part A: w12root at 189dc7b2. Evidence: absent only. Night 173's "0" came before w12root landed, and on that night no page stopped on tests.
   - Part B: frame 356. Evidence: a frame closes on a count, "0 never-calls refusals, against about 50", on dry1 turn 12 (`plans/archive/stack-2026-11-01.md`, frame 356, status 18:25).
6. The place of the changes:
   - Part A: the sign shows in the stop page's check lines in `rota/roles/principal.py`, `_gave_up_tries` by the audit. Change 1 touches the key readers and the word tables, the readers that `_gave_up_tries` uses. Change 2 touches the stopped page's text. Both touch the page, the place of the sign.
   - Part B: the sign shows at the `tests_missing` tick and at the encode door that refuses every test. Change 2 touches the vet and the encode door's read of a surface ref, the place of dry1's cause. The place of night 175's cause, the retire of his deleted criteria, is another place. No change touched it within the chain. w14root of 2026-10-29, "a criterion that his words delete is retired", aims at n175-W2 (merge 5bc46206).
7. Who started each change:
   - Part A, change 1: frame 344's audit, on Roman's message of 2026-10-27 14:08.
   - Part A, change 2: a read of a run, sprint 32 row 4, "W12 under F21" (`plans/stack.md:349-351`).
   - Part B, change 2: a read of a run, `plans/dry1-third-wall-read-2026-11-01.md`, in the dry run of Roman's ruling of 2026-10-31 00:58.
8. The origin:
   - Part A: `git log -S "none yet"` on `rota/roles/principal.py` gives b0a2086e (2026-10-09, "the park ask is a page with the item and its criteria"), in the same session's status lines as frame 190 (`plans/archive/stack-2026-10-10.md:21`). The frame of b0a2086e is not sure. Origin class: not found.
   - Part B: the stop text "could not write the tests" comes from cc013d96 (2026-10-24), frame 312's pass, which answered n160-W5 (chain 36). The attempt bound is older. The dotted ref of dry1 passed a vet whose origin this pass did not read. Origin class: not found for the sign's cause. The page text is from frame 312.
9. After the end:
   - Part A: night 175 names n175-W1, a stop page on `tests_missing` with "The team gave up: the team could not write the tests after 3 attempts", at the same page. Not sure.
   - Part B: dry3-W2, "stopped page m39 says \"after 0 attempts\"", and dry4-W14, "`touch_mistaken` quarantine; page says \"after 0 attempts\"", are stop pages of another key (extract c, dry3 and dry4, item 4). Not sure.

Row (Part A): Ended | same | 2 | absent only | not found | origin frame: none
Row (Part B): Ended | conditions changed | 1 | frame closes count | not found | origin frame: none

### Chain 40: n171-W5, 4 turns, not sure

1. The wall: "the Critic's pass door refuses a compound criterion [C?] (W5)" (`plans/method/turns-list-2026-11-10.md:365`; `plans/night171-read.md:62`). First turn night 171, last turn night 175, 4 turns: n171, n172, n174, n175. Rebuilt from column 8: n171-W5 to n172-W1 (not sure, "the read says New") and to n174-W12 (not sure); n172-W1 to n174-W12 (not sure, "New") and to n175-W14 (not sure); n174-W12 to n175-W14 (same sign at the same place) (extract c, nights 171, 172 and 174, item 8). The signs differ in form: 10 `verdicts.emit` refusals with no verdict (n171-W5), a fail on a two-line docstring example (n172-W1, `plans/night172-read.md:58`), three fails on an invariant criterion (n174-W12, `plans/night174-read.md:71`), and a review cycle on bg_1 (n175-W14, `plans/night175-read.md:70`). The build session's own read joins them by place: "The one door in all three cases is `_pass_lines_c[heck]`" (`plans/critic-loop-read-2026-10-29.md`, the result, nights 171, 174 and 175). Night 172's W1 sits under the same fact F37, "the added code lines that a pass names" (`plans/night172-read.md:146`). One place, one seat and one step, so I do not split the chain.
2. The state at the end: Open. Night 175, the last run of the night series, named it (n175-W14).
3. The conditions at the end: the nights stopped after night 175, and the dry runs are another kind of run. Conditions changed.
4. The changes:
   1. Sprint 32 row 3, branch f37b: ce3ecce5 "the Critic's pass names one line or several, as a list", 3b26e66e "a docstring run is one unit, and a kept line answers the hold", 91dd9119 and 9fc4d30c, merged at 0eaff3f1 on 2026-10-28 07:08. File: `rota/roles/api.py` and the Critic's prompts. Kind: a door and a prompt of a seat. In night 173's commit 36d2a667. The next read: "a Critic fail on a multi-line unit, 1 to 0" (`plans/stack.md:277`). Night 174 names W12, a fail on an invariant criterion, which no added line can meet.
   2. Sprint 34 row 2 and sprint 35 row 4, after the read `plans/critic-loop-read-2026-10-29.md`: b3d7c775 "admit a kept line or a passing test for a kept criterion" (2026-10-29 11:14), 23416479 "check the kept and test routes as whole facts", 319a4767, e226cca3 and a662f776 (2026-10-29). File: `rota/roles/api.py` and `rota/roles/prompts/critic/review.md`. Kind: a door and a prompt of a seat. After the last night. The next read is dry1, which names no Critic loop wall (absent only).
   - Count: 2.
5. The last change before the end: not applicable. The chain is open.
6. The place of the changes: the sign shows in `_pass_lines_check` in `rota/roles/api.py`, which serves `verdicts_emit` (`plans/rootfix-audit-2026-10-27-b.md:169`), and in the Critic's `review.md`. The critic-loop read: "`_pass_lines_check` and `review.md` admit an added line or a fail only, so a criterion met by a kept line or a passing test loops" (`plans/stack.md:173-177`). Both changes touch `_pass_lines_check` and the Critic's prompts. They touch the place of the sign.
7. Who started each change:
   1. A read of a run, sprint 32 row 3 on night 172's read: "The Critic's one-line pass, W1, under F37" (`plans/stack.md:345-348`).
   2. A count and a read: sprint 34 row 2, "A count on nights 170 to 174, then a read" (`plans/stack.md:248-251`), then the read of 2026-10-29 for sprint 35 row 4.
8. The origin: `_pass_lines_check` comes from 1663c2bb (2026-10-07), "feat(desks): a pass names an added line per criterion". Its message: "Roman ruled on 2026-10-07 that the Critic names, for each criterion, the line of the change that meets it, and that the door refuses a pass that leaves a criterion unnamed. This commit builds frame 170's design". The audit marks F37 "FIXED", each half with one reader (`plans/rootfix-audit-2026-10-27-b.md:170`). This pass did not read which wall frame 170 answered. Origin class: a frame that answered another wall: frame 170, on Roman's ruling of 2026-10-07, wall not found.
9. After the end: not applicable. The chain is open.

Row: Open | conditions changed | 2 | not applicable | frame 170 door | origin frame: 170

### Chain 41: dry1-W14, 4 turns, not sure

1. The wall: "page m144 says the team gave up after a merge [C?] (turn 16, 2)" (`plans/method/turns-list-2026-11-10.md:366`; `plans/dry1-turn16-read-2026-11-02.md:8`). First turn dry1, last turn dry5, 4 turns: dry1, dry3, dry4, dry5. Rebuilt from column 8: dry1-W14 to dry4-W14 (not sure, "a stopped page with a wrong count, another key"); dry1-W16 to dry3-W2 (not sure); dry3-W2 to dry4-W14 (not sure); dry4-W13 and dry4-W14 to dry5-W12 (same sign at the same place, "as dry run 4 walls 13 and 14") (extract c, dry1, dry3 and dry4, item 8). The chain holds three signs, so this block splits it into three parts. The brief asks for two parts. Three parts are the honest split.
   - Part A, a stopped page whose count or state is false: dry1-W14, "`quarantine_stalled` quarantined `developer|tick:batch_start|bg_1` at 3 because s192, s256 and s265 each counted one restart resume" while bg_1 had merged (`plans/dry1-turn16-read-2026-11-02.md:8`); dry3-W2, "m39 said \"after 0 attempts\"" (`plans/dry3-wall1-read-2026-11-02.md:8`); dry4-W14, "the page says \"could not put back code it was not asked to change after 0 attempts\"" (`plans/dry4-read-2026-11-03.md:135`). 3 turns.
   - Part B, the `touch_mistaken` route quarantines after a wrong mistake judgement: dry4-W13, "the Developer's edit of `_foldline` at `8e706696` was judged a mistake" (`plans/dry4-read-2026-11-03.md:134`), dry4-W14 (the same quarantine), and dry5-W12, "quarantine of `developer|tick:touch_mistaken|b_1`, 3 attempts, then m70 \"The team gave up\"" (`plans/dry5-read-2026-11-04.md:61`). 2 turns.
   - Part C, a drop lands as a contest: dry1-W16, "a drop on the description loops as `contested`" (`plans/dry1-turn17-read-2026-11-02.md:8`), and dry3-W2, "his \"Drop it\" landed as `contest` and not as a drop" (`plans/dry3-wall1-read-2026-11-02.md:8`). 2 turns.
2. The state at the end:
   - Part A: Ended. dry5, dry6 and dry6b name no stopped page with a false count. dry5-W12's page says "The team gave up" after 3 attempts, which `tick_attempts` holds (`plans/dry5-read-2026-11-04.md:61`).
   - Part B: Ended. dry6, dry6b and dry6c name no such wall (extract c, dry5, item 8, "dry5-W1, W4, W5, W9, W11 to W13: not met in dry6, dry6b, dry6c").
   - Part C: Ended. dry4, dry5 and dry6 name no drop that lands as a contest (extract c, dry3, item 8; dry4 and dry5, item 4).
3. The conditions at the end:
   - Part A: dry4 and dry5 both ran on icalendar with the fold sentence (extract c, dry4 and dry5, item 2). dry6 and dry6b are of group d. dry6c ran "with `ROTA_ONESHOT=1` and the 3080 alone" (`plans/method/turns-list-2026-11-10.md:305`). Not sure whether the requests changed at dry6. This pass did not read group d's run lines.
   - Part B: dry6c changed two settings on one database (`plans/method/turns-list-2026-11-10.md:305`). Conditions changed in part.
   - Part C: dry3 ran on another repository from dry4 and dry5 (extract c, dry3 to dry5, item 2). Conditions changed.
4. The changes:
   - Part A, change 1. 0b90f02b at 2026-11-02 02:52, "fix(core): a drained start is not a stall, and his restart forgets the start count". Its message: "The wall is the page m144 of dry1 turn 16". Kind: other code of rota, the stall rule. Before dry3 (in 44088319, git merge-base). dry2 names no such wall. dry3 names W2 with another cause: "the re-survey's writes to rows in the key lifted its quarantine".
   - Part A, change 2. Frame 360, a66b9a31 at 2026-11-04 00:35, "fix(roles): a stall page names the count at its send". Files: `rota/roles/principal.py`, `rota/core/sandbox.py`. Kind: other code of rota, the page. Before dry5 (in 79b1cdb0, extract c, dry4, item 6). dry5 names no page with "after 0 attempts" (absent only).
   - Part A count: 2.
   - Part B, change 1. Frame 362, 40980c59 at 2026-11-04 00:20, "fix(api): frame 362, a statement moved into a nested block is not lost". File: `rota/roles/api.py`. Kind: a door. Before dry5. The next read: dry5-W12 names the quarantine again, on "the removal of the assert and the 1501 branch" (`plans/dry5-read-2026-11-04.md:61`). After dry5 no change names wall 12 (extract c, dry5, item 6: walls 5, 10, 11 and 14 got passes).
   - Part B count: 1.
   - Part C, change 1. Not found for the description row. `plans/stack.md:2190`: "A drop on an observed row with no end state is frame 357's reach, 4 of 10 line kinds, and waits on Roman's ruling there". Frame 357's shape B is "on the branch" at a84a1cf4, 2026-11-02 13:44 (extract c, dry1, item 6). This pass did not check that shape B covers the description row. Part C count: 0 found, 1 not sure.
5. The last change before the end:
   - Part A: a66b9a31. Evidence: absent only.
   - Part B: 40980c59 came before the last naming, dry5. No change came after it. Evidence: absent only. The sign is absent in dry6 to dry6c, and no record says why.
   - Part C: not found. Evidence: absent only.
6. The place of the changes:
   - Part A: the sign shows in `quarantine_stalled` (dry1), the lift of a quarantine on a row write (dry3), and `_stuck_ticks`, which reads `tick_attempts` while the stall store holds the key (dry4) (`plans/dry4-read-2026-11-03.md:135`). Change 1 touches the stall rule, the place of dry1's cause. Change 2 touches the stall page's count, the place of dry4's cause.
   - Part B: the sign shows in `_removal_entry` and `_lost_in_block`, the block compare (`plans/dry4-read-2026-11-03.md:134`). Change 1 touches the same compare in `rota/roles/api.py`.
   - Part C: the sign shows in `land`, which "ends a drop only on a statement or a request item", in `_item_drops` at `rota/roles/principal.py` about 3858, and in `contested.md` (`plans/dry1-turn17-read-2026-11-02.md:8`).
7. Who started each change:
   - Part A, change 1: a read of a run, `plans/dry1-turn16-read-2026-11-02.md`, within frame 353's dry run on Roman's ruling of 2026-10-31 00:58.
   - Part A, change 2: a read of a run, dry4's read: "Walls 8 and 14 went to frame 360" (extract c, dry4, item 6).
   - Part B, change 1: a read of a run, dry4's read: "wall 13 to frame 362" (same cell).
8. The origin:
   - Part A: `quarantine_stalled` comes from 90f09152 (2026-08-11, "fix(scheduler): a tick that cannot drain"), rota's first design. `_stuck_ticks`, which gives the count on the page, comes from ced9de67 (2026-10-24), frame 312's pass, which answered n160-W5 (chain 36). Origin class: a frame that answered another wall: frame 312, wall n160-W5, for the count of dry4's page; rota's first design for the stall rule of dry1.
   - Part B: `_lost_in_block` comes from 11d04b18 (2026-10-27, "fix(api): F7, the commit compares the base with the tree for removals"). F7 is frame 344's fact that answered n171-W4, removals with no grant (chain 38, Part B). Origin class: a frame that answered another wall: frame 344 (F7), wall n171-W4.
   - Part C: `_item_drops` comes from 351f63c8 (2026-11-01, "a landed drop on a request line ends the item as dropped"), in the dry1 days of frame 357, which holds dry1-W10, "a dropped request returns as items" (extract c, dry1, item 6). This pass did not confirm 351f63c8's frame. Origin class: a frame that answered another wall: frame 357 (not sure), wall dry1-W10.
9. After the end:
   - Part A: dry6c-W1, "the Developer's start gave up after 3 sessions that wrote no code" (`plans/method/turns-list-2026-11-10.md`, group d, dry6c), is a true give-up of another key. dry8-W10, "the stopped page names the wrong cause", is the same page with another false part, five runs after dry5. Not sure.
   - Part B: dry8-W10, "the restore wake changed the fold" (group d, dry8), names the same route of the Developer, two runs past the three-run window. Not sure.
   - Part C: not found.

Row (Part A): Ended | not sure | 2 | absent only | frame 312 count | origin frame: 312
Row (Part B): Ended | conditions changed | 1 | absent only | frame 344 F7 | origin frame: 344
Row (Part C): Ended | conditions changed | 0 | absent only | frame 357 drop | origin frame: 357

## What I could not find

- The brief says the dry runs use another repository. Dry1 ran on click, the same repository as the nights (`plans/archive/stack-2026-11-02.md:195`, "dry1 on click"; `plans/dry1-first-wall-read-2026-10-31.md:5`, "clickI has 39"). So at dry1 the kind of run changed and the repository did not. dry2 ran on tips and dry4 on icalendar. Cells 3 of chains 2, 7, 26 and 39 say this.
- Chains split into more parts than the brief's two: chains 28 and 41 into three parts each. Chains split into two parts: 2, 14, 25, 29, 36, 37, 38, 39.
- Parts that do not reach four turns after the split: chain 14 Part B (2), chain 25 Part A (1) and Part B (3), chain 28 Parts A (2), C (3), chain 29 Part A (2), chain 36 Parts A and B (2 each), chain 37 Part B (1), chain 38 Parts A and B (2 each), chain 39 Parts A and B (2 each), chain 41 Parts B and C (2 each). The turn counts of the list are counts of the joined chain.
- Cells that read "not found":
  - Chain 2, Part B, cell 8: why the claim tick first quarantines on night 172.
  - Chain 25, Part A, cell 8: the commit of the 0.8 overlap threshold of the same-words door.
  - Chain 28, Part C, cell 8: the frame of 76f2f981, the act check.
  - Chain 29, Part A, cell 8: the wall that frame 304 answered.
  - Chain 36, Part A, cell 8: the wall that frame 190 answered.
  - Chain 38, Part B, cell 8: the commit of the old compare at the commit.
  - Chain 39, Parts A and B, cell 8.
  - Chain 39, Part B, cell 4: no change aimed at n175-W1.
  - Chain 40, cell 8: the wall that frame 170 answered.
  - Chain 41, Part C, cells 4 and 9.
  - Chain 2, Part A, and chain 26, cell 8: the frame of 01e48a6f. The commit names a walk of 2026-09-04 and no frame.
- Frames and commits named but not confirmed: f0b2924c as frame 250 (chains 7 and 28); 351f63c8 as frame 357 (chain 41); b0a2086e's frame (chain 39); frame 357's shape B on the description row (chain 41).
- The status times of frames before 2026-10-25 02:00 are BST in the stack. Commit times in this page come from `git log`, in the author's zone. Chain 36 names some of each, and this pass did not convert every one.
- Group d (dry6 to dry9, blind1) was read only by a grep of `plans/method/turns-list-2026-11-10.md`, lines 368 to 568, for chain 41. So cell 3 of chain 41, Part A, reads "not sure".
- No database was opened. No source failed to open.

## Apart from the blocks

- Several chains share their changes. Frame 344's audit (F2, F7, F19, F20, F21, F22, F25, F35) appears in chains 2, 7, 14, 24, 25, 26, 28, 29, 37, 38 and 39. The seam and frame 345 appear in chains 7 and 28.
- Several origins are a door of an earlier frame that answered another wall: frame 306 (chain 24), frame 312 (chains 39 and 41), frame 335 (chain 37), frame 283 (chain 38), frame 234 (chain 28), F7 of frame 344 (chain 41). This is a count of this page only and not a cause.
- In three places a read counts the sign at 0 on the night before the change aimed at it landed: chain 24 (night 174, before eeb0db69), chain 28 Part B (night 174, before 69561d5b), chain 39 Part A (night 173, before 189dc7b2).
