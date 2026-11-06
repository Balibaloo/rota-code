# Run 1 of the frame 362 arm: a merge with no source change, 2026-11-06

A read only. No tracked file changed, and no model ran. The probes are in
`C:/Users/roman/AppData/Local/Temp/claude/6d9eb18c9e6274ab/8b2312ef-0b14-4322-a20c-908058cac23b/scratchpad/mr362/`
(`MR` below). `ARM` is the arm's scratchpad folder `arm362/` beside it.

## Result

- **The merge is the claim of frame 360, shape A, working as built, and it met the design's named failure.** The Developer s152 committed nothing. The commit door made the fork commit the head and wrote the claim mark. The Tester's three tests pass on the code before the change. The harness, the Critic, the Architect and `mergeable` then each passed on facts that do not compare the tests with the code before the change (observed: `ARM/runs/dry6b.db`; `rota/roles/api.py` 26427 to 26448 of `822311e0`). The design page names this failure: "a weak Tester writes a test that asserts what the code does ... The test is green at the fork, and a new behaviour merges with no code" (observed: `plans/design-item-already-held-2026-11-02.md` line 85).
- **The claim is false.** On the code before the change, the fold splits a word in 8 of 12 sample texts, and a word of 80 letters is folded, against criterion c3 (observed: `MR/direct2.py`, `MR/direct.py`). The request does not hold on the old code.
- **The two safeguards that the design named both failed, each by a defect of its own.** The Critic's step 2 is "the only check", and the Critic was told `"diff": "", "note": "no commit yet on this batch"` for the claimed batch (observed: s154 turn 1; `api.py` 24255 to 24258, built `a6bed3b2a` 2026-09-30, before the claim). The Done line "puts 'No code changed' in front of the seat", and the seat never saw the line, because a waiting page hides every other state line (observed: `MR/state.py`; `rota/roles/principal.py` 332 to 340). So the build did not meet its design's condition on these two readers (reasoned).
- **The principal reads only the touch page at the end.** It says "Before I build this, here is what I expect to touch", lists three checks as "Passes.", and asks "Reply 'ok' to go ahead". No page and no line says that a change merged, or that it holds tests only (observed: `ARM/run1.log` lines 37 to 70). The touch page is a note that never blocks, by ruling 2 of 2026-09-12 and R7 (ruled: Roman, `rota/DECISIONS.md` about line 1383; `plans/principal-flow.md` line 267).
- **No open frame covers it.** Frame 360 is the build, and its status of 2026-11-02 18:03 lists "the weak Tester's green test" as residue with no frame. Frames 357, 358 and 361 have other causes (observed: `plans/stack.md` blocks 357 to 361).
- **Reach in the records: 1 of 19 distinct merges holds no source change, and 3 of 19 hold only tests that pass before the change.** 21 of the 66 criterion tests of those merges pass at the fork (observed: `MR/runbase.json`).
- **Proposal: one fact, the fork run of the batch's own tests, read by the Critic, by the code read, and by the principal's state line, with no new gate.** About 6 to 7 agent cycles. A question goes to Roman only if he wants a claimed merge to wait on him.

## 1. Find: what let each step pass

The sessions from the batch start to the merge, in run order (observed: `sessions`, `tool_calls`, `turns` of `ARM/runs/dry6b.db`; `ARM/run1.log` lines 9 to 17).

| Step | Session | What it sent and what the door answered | The rule that let it pass |
|---|---|---|---|
| Touch note | s151 Liaison, `tick:touch_note` | `msg.present_principal` with the batch and the item, page m31, status `open` | `predicates.touch_note`, band `start`. A note waits on nothing |
| Batch start | s152 Developer, `tick:batch_start` | 14 reads, then `code.commit(message='No changes needed; existing implementation in string.py already meets criteria')`. The door answered `{"committed": false, "why": "nothing changed", "claimed": "99619246...", "note": "... You claimed the criteria are met. The Tester's tests check the claim. Now end the session ..."}` | `code_commit`, the claim branch, `api.py` 26434 to 26448: the batch had no head, no challenge or escalation was sent, and no program write was refused |
| Harness | `do:harness` | 162 tests, 3 not passing | The 3 reds are red at the base (`test_issue_1445.py`, `test_rfc_6868.py`, `test_time.py`), and `drop_base_reds` excuses them, `harness.py` 613 |
| Tests | s153 Tester, `tick:tests_missing` | triage of c1 to c3 as `encodable`, then 3 encodes that landed. The later re-encodes got "c1 already has a test this session ... Nothing was written" | `tests_missing` wakes on any head, and the claim gave a head. `tests.encode` checks the shape of a test, not what it detects |
| Test run | `do:harness` | 165 tests, the same 3 base reds | `reds_that_hold` holds no new red |
| Critic | s154 Critic, `tick:review` | Turn 1 pass with test lines was refused: "... is not an added line of the diff ... or `test: <the id of a test of c1 that passed>`". Turn 2 sent `lines={'c1': 'test: tst_fold_c1', 'c2': 'test: tst_fold_c2', 'c3': 'test: tst_fold_c3'}` and landed `pass` | `_pass_lines_check` and `_route_fault`, `api.py` 19385 to 19409: a `test:` value holds when the test belongs to the batch, binds to the criterion, is live, and passed at the head. The head is the fork |
| Structural review | s155 Architect, `tick:structural_review` | three `findings.find` rows, `satisfied`, at the fork commit. Its reply: "Since no changes were made in the diff, all constraints are considered satisfied" | `findings.find` admits `satisfied` on an empty diff |
| Merge | `do:merge` | merged at 12:20:55, `8b4c98af` | `lifecycle.mergeable`, `lifecycle.py` 1068 to 1171: head, a test for each criterion, a pass verdict at the head, no stray, no red that holds, findings, no seat owed. No line reads `claimed_head` |

The Developer's decision, verbatim from s152 turn 14 (observed):

> Since I'm not supposed to make changes if the code already meets the criteria, and the principal's feedback indicates the current code is correct, I should commit as-is without making any modifications.

The Developer read "Line 2 is wrong" as "the current implementation and tests are correct" (observed: the same turn). Its brief says "Committing nothing is a legitimate outcome and says so" (observed: s152 system prompt, `batch_start.md` line 34).

The Critic's reasoning, verbatim from s154 turn 3 (observed):

> Criterion c2: Requires folding breaks at unquoted whitespace. The test `tst_fold_c2` passes. Met by existing behavior (`test: tst_fold_c2`).

The Critic did not run step 2, "Does each test encode its criterion?" (observed: no `verdicts.claim_encodes` and no `msg.challenge_tester` in `tool_calls`).

### The tests, and what each one asserts

The merge `8b4c98af` holds `tests/test_fold_long_lines.py`, `tests/test_fold_quoted_strings.py` and `tests/test_no_split_word.py`, 50 lines, and no other file (observed: `git show --stat 8b4c98af` in `ARM/icalendarI`).

| Test | Criterion | Input | Assertion | What it shows |
|---|---|---|---|---|
| `tst_fold_c1`, `test_fold_max_75_octets` | c1, lines of 75 octets at most | `"A" * 80`, one word | every line `len(ln.encode()) <= 75` | The old fold length. It needs the old code to split the word, so it contradicts c3 (reasoned) |
| `tst_fold_c1`, `test_fold_avoids_splitting_words` | c1 | the same | `" " not in ln or len(ln.encode()) <= 75` | Nothing. The first test already makes it true |
| `tst_fold_c2` | c2, the break at a whitespace | `"Hello World" * 10` | `"Hello World" not in ln.split("\n")[0] or len(ln.encode()) <= 75` | Nothing. The second half is the old fold length |
| `tst_fold_c3` | c3, no split of a word | `"Short"` | every line `<= 75` | Nothing. No line needs a fold |

All 4 test functions pass on `99619246`, the code before the change (observed: `MR/pre`, pytest, "4 passed in 0.40s").

### The direct check on the code before the change

`_foldline` at `99619246` folds at the 75th octet, at any character, and avoids only a split backslash or caret escape (observed: its source, printed by `MR/direct.py`). Twelve texts with a shifted start give a fold between two letters of a word in 8 of 12 (observed: `MR/direct2.py`, for example `' and keeps r' | ' unning far '`). A word of 80 letters folds after 66 letters, so c3 is false on the old code (observed). The request's behaviour does not hold before the change. The Developer's claim is false.

## 2. The page after the merge

- **When it was due.** s151 wrote the touch page m31 at run step 9. The batch started at step 11, and the merge came at step 17 (observed: `ARM/run1.log`). The page was due before the start.
- **What held it.** No rule held it. A touch note never blocks: "Hold at intent time only. No batch starts until the first page is answered. After that, nothing waits on a page" (ruled: Roman, 2026-09-12, ruling 2 of "The principal's flow", `rota/DECISIONS.md` about line 1383). R7, "the touch note never blocks", stands on the oneshot path (ruled: 2026-09-13, `plans/principal-flow.md` line 267). The merge "waits on the seat, never on a page" (observed: `lifecycle.py` 1161 to 1163). The principal reads only between runs, and one turn is one `rota run` (observed: `plans/operating-facts.md`, the seat's baseline). So the page reached him after the merge by design. Dry run 3 showed the same order with m40 (observed: `plans/dry3-wall1-read-2026-11-02.md` line 137).
- **What he reads at the end.** "Waiting on you." and then page m31 (observed: `ARM/run1.log` lines 37 to 70; the same text from `principal.render_state` on a copy, `MR/state.py`):

  > Before I build this, here is what I expect to touch.
  > ...
  > 2. check: fold max 75 octets, expects len(ln.encode()) <= 75, f"Line too long: {len(ln)} octets". Passes.
  > ...
  > This is a prediction, not a promise. Reply 'ok' to go ahead. Reply with words if something concerns you.

- **No line tells him that a change merged.** `_render_state` returns the first waiting ask and stops. The Done line, the claimed line and the fault line are below that return (observed: `principal.py` 332 to 340). On a copy with m31 marked answered, the state shows "No code changed. These tests show the code already does this." and "Rota itself failed 1 time this run" (observed: `MR/state.py`). The claimed line names no batch, no request, no test and no commit (reasoned: `CLAIMED_LINE`, `principal.py` 303).
- **The page misleads in three words.** "Before I build this" is false after the merge. "Reply 'ok' to go ahead" asks for a go that the run already took. "Passes." beside each check reads as a proof, and each check proves nothing (reasoned: section 1).

## 3. Purpose and provenance of each mechanism that decided

| Mechanism | Purpose | Made by | Met its design? |
|---|---|---|---|
| The claim branch of `code.commit`, `api.py` 26427 to 26448 | An item that the code already holds ends through tests and a merge, not through three failed starts | Ruled: Roman, 2026-11-02 17:14, shape A of `plans/design-item-already-held-2026-11-02.md`. Built `657cf1a81` (pass 1) and `a6ef4214b` (pass 1b, "a claimed batch reads as a claim on every page"), 2026-11-02 | The door works as designed. Pass 1b's "every page" missed the Critic's `code.read` (observed: section 1) |
| The Critic's `test:` route, `api.py` 19385 to 19409 | A criterion that keeps a behaviour is met by its passing test | `b3d7c775b` 2026-10-29, "admit a kept line or a passing test for a kept criterion"; `234164796` 2026-10-29 checks the test at the head. Pass lines ruled: Roman, 2026-10-07 08:57 | Partly. The commit names a kept criterion. The door admits the route for any criterion, and the judgement of "kept" stays with the Critic's prompt (observed: no kind check in `_route_fault`) |
| `code.read` note "no commit yet on this batch", `api.py` 24255 to 24258 | An empty diff says why it is empty | `a6bed3b2a` 2026-09-30 | Right when built. Wrong since the claim, because a claim makes the fork the head (reasoned) |
| The state shows the waiting ask alone, `principal.py` 332 to 340 | "First what waits on you, because that line asks for something" | `9c5c71fe6` 2026-09-08 (tips9, 2026-09-04); the objections tail `7851516d8` 2026-11-02 | The design page of frame 360 relied on the Done line reaching the seat. The line does not reach him while any page waits (reasoned) |
| The touch note never blocks | A prediction never blocks. Only a fact or a ruling gates | Ruled: Roman, 2026-09-12, ruling 2, and R7 of 2026-09-13; `plans/composition.md` line 73 | Yes, as a gate. The page words still read as a gate after the merge (reasoned) |
| The base run, `harness.py` 549 to 554 and 668 | A door says "passed before this batch" only from a record | `8888ea930` 2026-10-11, frame 207; base reds frame 362 pass 5b | Yes, for inherited tests only. No base run covers a Tester's test |
| `mergeable`, `lifecycle.py` 1068 to 1171 | Law 8: harness, then Critic, then Architect | Law 8 (`rota/LAWS.md` 222) | Yes. It reads no claim and no fork run |

## 4. What the code already holds: checks against the code before the change

By file and line, in `C:/Users/roman/rota_p362a` at `822311e0` (observed):

1. `rota/core/harness.py` 549 to 554, `inherit`: records the base run of the inherited tests at the fork, once, before any head.
2. `rota/core/harness.py` 558 to 564, `base_red_ids`: the inherited tests red at the base.
3. `rota/core/harness.py` 567 to 583 and 613 onward, `reds_that_hold` and `drop_base_reds`: a red at the head that was red at the base, node by node, holds no gate.
4. `rota/core/lifecycle.py` 1137, `mergeable`, and `rota/core/predicates.py` 1171, 1271 and 1631, and `rota/core/scheduler.py` 2050 and 2373: the readers of item 3.
5. `rota/core/sandbox.py` about 2391: the "passed before this batch" sentence comes from the base run record.
6. `rota/roles/api.py` 26372 to 26385, `code_commit`: a commit that puts the tree back to `HEAD~1` is churn and is refused.
7. `rota/roles/api.py` 26434 to 26448, `code_commit`: an unchanged tree with no head becomes a claim at the fork.
8. `rota/roles/api.py` 24246 to 24258, `code.read`: the diff from the fork, and the note when the fork equals the head.
9. `rota/roles/prompts/critic/review.md` step 2: the Critic reads each assertion against the criterion's words. This is a judgement, not a run.

No check runs a Tester's test on the code before the change. No check compares a criterion with the code before the change except the Critic's step 2 (reasoned: items 1 to 9).

## 5. Match by symptom and by cause

- **Frame 360** (open, validating): an item that the code already satisfies. Its build is the mechanism of this merge. Its end conditions count empty starts, not false claims. Its status of 2026-11-02 18:03 lists "the weak Tester's green test, the design page's first failure, with the Critic's step 2 as the one check" as residue. So this issue is that build working as designed, plus two reader defects that the design did not foresee (observed: `plans/stack.md` block 360; reasoned).
- **Frame 357**: a landed drop on a statement. Another cause.
- **Frame 358**: the re-survey notes after a merge. Another cause. Run 1 wrote its re-survey rows to the ledger and no page (observed: `ARM/run1.log` step 26).
- **Frame 361**: the onboarding account page. Another cause.
- **Frame 362**, the held frame: the owed contest of the guess. Run 1 does not count for it (observed: `plans/f362-live-arm-2026-11-06.md` section 4).
- **The touch page after the merge**: named by the dry3 read as by design, and not read further. No frame (observed: `plans/dry3-wall1-read-2026-11-02.md` line 137).
- **The wall guide.** The Critic's note is cause 12, two records of one fact disagree: `claimed_head` says a claim, and `code.read` says no commit. The hidden line is cause 11, what is his does not reach him. The green test is cause 5, the seat has the fact and judges wrong, with cause 2 behind it: no prompt holds the fact that the tests pass on the old code (reasoned: `plans/wall-guide.md` headings).
- **An unbuilt proposal.** None in `plans/` proposes a fork run of a Tester's test (observed: a search for "green at the fork", "red at the fork" and "passed before").

## 6. Reach

In the code, the same gap sits at four readers. None of them sees whether a test of the batch fails on the code before the change: `_route_fault` (`api.py` 19385), `code.read` (`api.py` 24255), `_render_state` (`principal.py` 332), and `mergeable` (`lifecycle.py` 1068). The harness has the one place that could record the fact, `record_base_run` (`harness.py` 668), and it runs inherited tests only (observed).

In the records, I opened every run database over 1 MB in the two temp roots, without the test fixtures' `tmp*` folders, with `immutable=1` (observed: `MR/scan.py`, `MR/scan_out.txt`). They hold 21 distinct merged batches. Two are fixtures with the heads `aaaa` and `bbbb`. The other 19 come from clickI nights 166 and 170 to 175, dry1, dry2 on tipsI, dry3 on icalendar, and this arm. Every head is still in its repository (observed: `MR/heads.py`). I ran each batch's criterion tests at its fork and at its head (observed: `MR/runbase.py`, `MR/runbase.json`).

| Count | Value |
|---|---|
| Merges | 19 |
| Merges with no source change | 1, this arm's run 1 |
| Merges whose every criterion test passes at the fork | 3: this arm's run 1, night 171's `bg_2` at `090dec8e`, night 174's `bg_3` at `d6937a50` |
| Merges with at least one criterion test green at the fork | 10 |
| Criterion tests | 66, all green at the head |
| Criterion tests green at the fork | 21 |

The two clickI merges changed only the docstring of `format_filename` (observed: `git diff`). Their tests call the function and pass on the old code, so no test shows the docstring change (reasoned). Some of the 21 green tests are right. They encode a criterion that keeps a behaviour, for example `tst_tip_valid` and the c2 and c3 tests of dry3's `bg_1` (reasoned). Dry runs 4, 5, 6, 6b and 6c merged nothing in the copies I found (observed: the scan).

## 7. Proposal

**Record the fork run of the batch's own tests, and show it to the three readers that judge or report the batch. Add no gate.**

1. `harness.record_base_run` already runs tests at the fork. Run the Tester's tests there too, once per test version, and store the result in the same record. On a claimed batch the head is the fork, so the head run is the fork run and no run is added.
2. The Critic's `code.read` on a claimed batch says "The Developer changed no code and claims the criteria are met. The tests below are the only evidence", in place of "no commit yet". Its review block adds one line for each test: "passes on the code before the change" or "fails on the code before the change".
3. `_render_state` shows the shipped lines under a waiting ask, as it already shows the objections tail. For each merged batch whose every criterion test passes at the fork, the line names the request and the tests: "Merged: <request>. No test of it fails on the code before it, so the tests do not show the change." The claimed line names its batch in the same form.
4. A touch note of a merged batch reads as a record, not a go: "This was built and merged before you read it", with no "Reply 'ok' to go ahead".

The reason for this place (reasoned):

- One fact covers the claim and the weak change batch, which have the same signature: no criterion test fails at the fork. It covers 3 of 3 such merges in the records, on two repositories.
- The fact is a test run, not a model's word. The Critic keeps the judgement, and the principal keeps the end: "The Principal declares finished. The system observes a candidate only" (observed: `plans/composition.md`).
- No ruling changes. The touch note still never blocks, and the merge still waits on the seat only.
- A door that refuses a pass on green-at-the-fork tests would end shape A, because every true claim has such tests. That is a departure from Roman's ruling of 2026-11-02 17:14, so this proposal does not take it.

Price: a design page by C76 step 3b, 1 cycle, because the fix changes a page form, a door's text and a prompt block. The build is 3 to 4 cycles: the fork run, the Critic's two texts, the state line and the touch note. Then 1 review and 1 gate. About 6 to 7 cycles in all (reasoned: the frame 360 prices, `plans/stack.md` block 360).

Cost to a correct run: one pytest call at the fork per change batch for the Tester's files, which needs a checkout of the fork, a few seconds on icalendar. No extra run on a claim. One line per test in the Critic's prompt, about 100 characters. One line on the page per merge whose tests show nothing (reasoned: `record_base_run` runs one child per filter group).

What would measure it:

1. On a copy of `ARM/runs/dry6b.db`, `render_state` shows the merged line while m31 waits. Control: only m31 (observed: `MR/state.py`).
2. s154's prompt on that copy shows the claim note and three "passes on the code before the change" lines. Control: "no commit yet on this batch" (observed).
3. Over the 19 recorded merges, the new reader flags the 3 of section 6 and no other. Control: `MR/runbase.json`.
4. On the next 3 dry runs: each merge whose tests all pass at the fork reaches the principal's state with its line in the turn of the merge. Target: all. Also count how often the Critic challenges with the new fact, which no sample shows yet.

**One question for Roman, only if he wants more than visibility.** Ruling 2 of 2026-09-12 says that after the first page "nothing waits on a page", and `mergeable` waits on the seat only. A claimed merge that waits for his "ok" departs from that ruling. In plain words: the builder says "already done", a checker writes checks that pass on the old code, and today the change merges and he learns of it later. With the departure, the merge of a claim waits until he reads "No code changed" and says ok. Recommended: no departure now. Build the visibility first, and count on the next dry runs how many claims are false.

## 8. Doubt

- One sample at temperature 0. Run 1 ran without `ROTA_ONESHOT=1`, unlike the recorded turn, so its later sessions are not the record's (observed: `plans/f362-live-arm-2026-11-06.md` section 4).
- I did not measure whether the Critic on a 9b model challenges the Tester when it sees the fork-run lines. The proposal makes the fact visible. It does not prove that the seat uses it.
- The fork for each recorded batch is my walk back over the commits authored by the Developer, to the first commit by another author or with a `rota:` subject (observed: `MR/forks.py`). A batch that started on top of an earlier unmerged Developer commit would get a wrong fork.
- The test runs used the rota venv with each project's `src` on `PYTHONPATH`, not each batch's own `.venv` (observed). The heads gave 66 of 66 green, as the records say, so the environment matches on these tests (reasoned).
- I opened the copies with `immutable=1`, so a frame that only a `-wal` file holds is not read. The arm's own database I opened with `mode=ro` (observed).
- I did not count the touch page after a merge across the clickI nights. Their principal was a script, and the record keeps no time of a merge, so the order of page and merge is not in the rows (reasoned).
- I did not read `lifecycle.merge` or the Tester's `tests_missing.md` in full. The Tester's prompt holds no word about a claim (observed: a search).
- The criteria themselves are doubtful: c3 says a line with no whitespace is not folded, which breaks the 75-octet rule of c1 and RFC 5545. I did not follow that cause (reasoned).
