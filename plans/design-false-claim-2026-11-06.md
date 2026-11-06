# Design: a claim of "already done" that is false (2026-11-06)

A design page by C76 step 3b for frame 360, after `plans/arm-run1-merge-read-2026-11-06.md` (`the read` below). Read-only at 47ca1e43 on `rota/foundation`. No model ran. No tracked file changed except this page. The one probe is `dc360/control.py` in session 8b2312ef's scratchpad, run on the read's `mr362/runbase.json`.

## Result

**Recommend shapes A and D together, as two slices, with no new gate on the merge and no departure from a ruling.** A shows the fact. D makes the Critic's reading of each test a recorded act on a claimed batch. The first slice changes only readers of facts that exist today. The second slice adds the fork run of a change batch's own tests (reasoned: section 5).

- **One finding changes the read's proposal.** On a claimed batch the head is the fork. So every test that passes at the head passes at the fork, for a true claim and for a false claim alike (observed: `rota/roles/api.py` 26439 to 26441 writes the fork as `head_commit`; reasoned). The fork run cannot tell a true claim from a false one. Only a reading of each test against its criterion can, by the Critic or by him. The fork run tells something new only on a change batch: a test that passes before the change does not show the change (reasoned).
- **Five shapes.** A, show the fact (the read's proposal). B, a claim waits for his word before the merge. C, the fork fact gates, with no word of his. D, the Critic's step 2 is a recorded act before a pass on a claim. E, a claim cites its source line for each criterion.
- **B departs from ruling 2 of 2026-09-12**, "After that, nothing waits on a page". **C departs from the ruling of 2026-11-02 17:14**, because it stops every true claim, and from the line of 2026-09-02 that a door refuses only a fact that is certain whatever the criterion means. A, D and E depart from no ruling (reasoned: section 3).
- **Price: about 9 agent cycles after this page.** Slice 1 about 4 to 5, slice 2 about 4 to 5 (reasoned: section 5).
- **The question for Roman is in section 6.** It asks whether a claim of "already done" waits for his word. The recommended answer is no, not now.

## 1. What the code holds, in four facts

At 47ca1e43 (observed: each file and line below).

1. **A claim makes the fork the head, and nothing more records it.** `code_commit`, `rota/roles/api.py` 26427 to 26448: an unchanged tree on a batch with no head, no challenge or escalation sent, and no refused write to a program file, writes `head_commit` and `claimed_head` as the fork commit. The note says "The Tester's tests check the claim". The claim carries the commit message only. It cites no line and no run (observed: s152's message "No changes needed; existing implementation in string.py already meets criteria", the read section 1).
2. **No run puts a batch's own tests on the code before the change.** `record_base_run`, `rota/core/harness.py` 668 to 702, has one caller, `inherit` at 553. It runs the inherited tests at the fork, before any head. The Tester writes only after a head exists (observed: `predicates.tests_missing`, the read section 1). So the fork result of a Tester's test exists only when the head is the fork, which is a claim.
3. **The Critic's door holds a `test:` value on four facts, and none of them is the reading of step 2.** `_route_fault`, `rota/roles/api.py` 19348 to 19409: the test belongs to the batch, binds to the criterion, is live, and passed at the head. `verdicts_claim_encodes`, 18426 onward, keeps the step 2 answer in `ctx.verdict_claims` for the session only, and `_route_fault` does not read it. On a claim, `code_read`, 24255 to 24258, says "no commit yet on this batch", because the fork equals the head.
4. **The principal reads a claim nowhere while a page waits, and nothing waits on him.** `_render_state`, `rota/roles/principal.py` 330 to 340, returns the first waiting ask and stops. `CLAIMED_LINE` (303) and the Done count (357 to 371) are below that return. The touch page, 3244 to 3258, says "Before I build this" and "Reply 'ok' to go ahead" whatever the batch's status. `mergeable`, `rota/core/lifecycle.py` 1161 to 1169, waits on a seat and never on a page. The one hold on him is `merge_gate=review`, a setting he toggles, default `auto` (`rota/core/config.py` 70 to 74).

## 2. The axes that a fix can move on

- **Which fact is recorded, and by whom.** The claim mark, by the commit door (exists). The fork run of the batch's own tests, by the harness (new). The Critic's step 2 answer for each test, by the Critic through its door (exists for the session only). A cited source line for each criterion, by the Developer through the commit door (new).
- **Which seat reads the fact.** The Critic in `code.read` and `tests.load`. The Tester, sent back by a gate. The Architect. `mergeable`. The principal on the state and on the touch page.
- **What the principal reads, and when.** Before the merge, on a hold page. After the merge, on the state line in the turn of the merge. Never, which is today (observed: the read section 2).
- **What waits, and on whom.** Nothing, which is today. The Critic, refused by its door until it records a reading. The Tester, sent back by a gate. The principal, on a hold.
- **Which batches the fix covers.** Claims only: 1 of 19 recorded merges. Every batch whose tests show nothing at the fork: 3 of 19 (observed: section 4).
- **What a caught false claim costs, and where it goes.** A red test sends it to the Developer through `tests_failing`. A challenge sends it to the Tester. His "no" after the merge is an amendment, and "a merged batch stays, and the amendment is a new batch on top" (ruled: Roman, 2026-09-12, ruling 3, `rota/DECISIONS.md` 1385 to 1388).
- **Who can tell a true claim from a false one.** The fork run cannot, on a claim (reasoned: fact 1 and the Result). Only a reader of the test against the criterion can: the Critic, a cited line, or him.

## 3. Candidate shapes

Prices use the anchors of `plans/operating-facts.md`: a door text or a number, 2 cycles; an instrument fix, 3; a seam design with its night, 8 to 10 (observed: the anchors as cited by `plans/design-item-already-held-2026-11-02.md` line 76).

### A. Show the fact: the read's proposal, with no gate

**What changes, by file.**
- `rota/roles/api.py` `code_read`, 24255: on a claimed batch the note says "The Developer changed no code and claims the criteria are met. The tests are the only evidence", in place of "no commit yet".
- `rota/core/harness.py`: on a change batch, run the Tester's tests once at the fork per test version, in a checkout of the fork, and keep the result beside the base record. On a claim the head run is the fork run, so no run is added.
- `rota/roles/api.py` `tests_load`, 13339: one line for each test, "passes on the code before the change" or "fails on the code before the change".
- `rota/roles/principal.py` `_render_state`: the shipped lines stay under a waiting ask, as the objections tail does now (340). The claimed line names its request and its tests. A merged change batch whose every criterion test passes at the fork gets one line: "Merged: <request>. No test of it fails on the code before it, so the tests do not show the change."
- `rota/roles/principal.py` touch page, 3244: for a merged batch, the page says "This was built and merged before you read it", with no "Reply 'ok' to go ahead".

**Cost.** To a correct run: one pytest call at the fork per change batch, a few seconds on icalendar, and none on a claim. About 100 characters per test in the Critic's prompt (reasoned: the read section 7). To his attention: one line per merge whose tests show nothing, 3 of 19 on the records, and two to three words less on a touch page after its merge (observed: section 4).

**How it fails.**
- On a claim, every test reads "passes on the code before the change". That is true of every claim, so the line adds no news for the Critic beyond the claim note (reasoned: the Result).
- The Critic on qwen3.5:9b may not act on the note. s154 reasoned "Met by existing behavior" and skipped step 2 (observed: the read section 1).
- He reads the line after the merge. A false claim is merged when he reads it, and his "no" is a new batch on top (ruled: 2026-09-12, ruling 3).

**Measure.** With no model: on a copy of `dry6b.db`, `render_state` shows the claimed line while m31 waits (control: m31 only). s154's prompt shows the claim note (control: "no commit yet on this batch"). Over the 19 recorded merges, the new reader flags 3 and no other (control: section 4). With a model: on the next 3 dry runs, each merge whose tests show nothing reaches his state in the turn of the merge (target: all), and the count of Critic challenges on such a batch.

**Departure.** None. Precedent: the removal line after a merge, "under `merge_gate=auto` nothing holds the merge, so the summary he reads after it names each ungranted removal once ... No hold and no gate" (ruled: Roman, 2026-10-27, `rota/roles/principal.py` 2939 to 2943).

### B. A claim waits for his word before the merge

**What changes, by file.**
- `rota/core/lifecycle.py` `mergeable`: a batch with `claimed_head = head_commit` and no ruling row of his returns "waiting on the principal: the team says the code already does this".
- `rota/core/predicates.py`: a present wakes the Liaison for the claim after the Critic's pass.
- `rota/roles/principal.py`: a hold page. "The team says the code already does <request>. No code changed. These checks pass on the code as it is:" then each test's assertion in plain words, then "Reply 'ok' to accept. Say what is missing if it is not done."
- `principal.land`: "ok" writes a ruling row and the merge goes on. Words go to the Developer and the Tester as a contest.
- The batch defers while it waits, and the next batch starts, as for a slice hold (ruled: Roman, 2026-09-13, `plans/principal-flow.md` "R7", 172 to 177).

**Cost.** To a correct run: a true claim waits one whole turn, because he reads between runs and one turn is one `rota run` (observed: the read section 2). To his attention: one page per claim. On the records that is 1 page in 19 merges. Each Developer escape to a claim is also a page. The comment over the empty-commit branch names five such escapes in five runs, twice (observed: `plans/design-item-already-held-2026-11-02.md` 1.1).

**How it fails.**
- He must judge whether a check encodes his words. The page shows an assertion in plain words, and a "Passes." beside it reads as a proof, as on m31 (observed: the read section 2). So the error of s154 can move to him, with his attention spent.
- A hold that he never answers holds the claim forever. The register says "waiting on you" and other batches run (ruled: 2026-09-13, answer 2). Silence is never consent (observed: `plans/composition.md` 74 to 75).
- The page count rises with the weak Developer's escape rate, which nothing caps (reasoned).

**Measure.** With no model: on a copy of `dry6b.db` before the merge, `mergeable` on the claimed batch returns the wait (control: None, then merged). His "ok" lands a ruling and the merge runs. His words reach the Developer. With a model: on the next dry runs, count claims, hold pages, and the claims he rejects.

**Departure.** Ruling 2 of 2026-09-12: "Hold at intent time only. No batch starts until the first page is answered. After that, nothing waits on a page" (ruled: Roman, `rota/DECISIONS.md` 1383 to 1384). It also departs from frame 204's design, "The merge waits on the seat, never on a page" (observed: `lifecycle.py` 1161 to 1163). A variant B' makes the hold a value of a setting that he toggles, like `merge_gate`. B' departs from no ruling, because "Sign-offs after that, including on merges, are opt-in" (observed: `plans/composition.md` 22 to 23). Then the default stays A.

### C. The fork fact gates, with no word of his

**What changes, by file.** The fork run of A in `rota/core/harness.py`. `rota/core/lifecycle.py` `mergeable` returns "no test of the batch fails on the code before it" when every criterion test passes at the fork. `rota/core/predicates.py` sends the batch back to the Tester with that reason.

**What it does to a true claim.** It stops every one. A true claim has every test green at the fork by definition (reasoned: fact 1). The Tester cannot write a red test for code that already holds the behaviour. The batch stalls, the ladder runs, and the page says "The team gave up", which is the wall of dry2 that frame 360 fixed (observed: `plans/stack.md` block 360, the Site line). So C ends shape A.

**Cost.** To a correct run: the fork run of A, and one Tester cycle for each change batch whose tests show nothing. On the records C stops 3 of 19 merges (observed: section 4). One is the false claim, a right stop. Two are night 171's `bg_2` and night 174's `bg_3`, where he asked for a docstring example and "the code stays as it is" (observed: `plans/night171-read.md` 106, `plans/night174-read.md` 101). A test that reads the docstring could show that change, so those two cost one Tester cycle each (reasoned). To his attention: none, until a stall reaches a page.

**How it fails.** Every true claim and every pure refactor, a request whose criteria all keep a behaviour, stops (reasoned). A variant C2 exempts claims. C2 then misses this case, 1 of 1 claims (observed: section 4).

**Measure.** With no model: `mergeable` with the fork run over the 19 recorded merges gives the new reason for 3 (control: None for 19). On a copy of `dry2.db` with the claim of frame 360's test, the true claim stalls (control: it merges). With a model: on the next dry runs, the batches sent back, the red tests the Tester then writes, and the true claims that stall.

**Departure.** The ruling of 2026-11-02 17:14, shape A: "the team proves it with checks that join the project, and he reads 'No code changed'" (ruled: Roman, `plans/stack.md` block 360, status 17:15). Also the line of 2026-09-02: a door refuses a fact that "is certain independent of what the criterion means ... judgement stays with the roles" (ruled: `rota/DECISIONS.md` 943 to 958). A green test at the fork is right for a criterion that keeps a behaviour, so it is not certain (reasoned).

### D. On a claim, the Critic's step 2 is a recorded act before a pass

**What changes, by file.**
- `rota/roles/api.py` `_route_fault`, 19385 to 19409: on a batch with `claimed_head = head_commit`, a `test:` value holds only if this session claimed `verdicts.claim_encodes(<criterion>, encodes=True)`. The refusal says: "No code changed on this batch, so the test is the only evidence. Read its assertion against the criterion's words, then claim encodes for <criterion>."
- `rota/roles/api.py` `code_read`, 24255: the claim note of A.
- `rota/roles/prompts/critic/review.md` step 1: one sentence that a claimed batch has no diff, and each criterion stands on its test and step 2.

**Cost.** To a correct run: one tool call per criterion for the Critic, on a claim only, and nothing on a change batch. To his attention: none.

**How it fails.** A weak Critic claims `True` by rote. The door forces the act, not the reading. s154 wrote "Met by existing behavior" for c2, and it would likely claim `True` (observed: the read section 1; reasoned). The session-local claim store holds the act for one session, which is the session that emits the pass (observed: `verdicts_claim_encodes`). The recorded Critic cases that reach a claimed batch go stale, and the review of pass 1 found that no recorded case seeds a claim (observed: `plans/f360-review-p1.md` Pass 1b, the refusal record).

**Measure.** With no model: on a copy of `dry6b.db`, s154's turn 2 pass is refused with the step 2 words (control: the pass lands). With a model: replay s154 on qwen3.5:9b, 5 samples, and count `encodes=False` with `msg.challenge_tester` (control: 0 of 1).

**Departure.** None. It is a door on the shape of an act, like the pass lines (ruled: Roman, 2026-10-07 08:57, the read section 3). It follows the brief's own words, "its own passing test that step 2 finds encodes it" (observed: `review.md` 17 to 18).

### E. A claim cites its source line for each criterion

**What changes, by file.**
- `rota/roles/api.py` `code_commit`, the claim branch: a claim needs `evidence={<criterion>: 'kept: <one line>'}` for each live criterion. The door checks each value as a whole line of a code file at the fork, with the rules of `_route_fault`'s `kept:` branch. A claim with no evidence gets the old note and no head.
- `rota/roles/prompts/developer/batch_start.md`: how to claim, with one example.
- `tests.load` for the Critic and the claimed line for him: "c3: the team says this line does it: <line>".

**Cost.** To a correct run: one longer call for the Developer on a true claim. To his attention: the claimed line grows by one line per criterion, and he reads a line of code and not a test name.

**How it fails.** A weak Developer cites a near line. On run 1 it could cite the 75-octet line of `_foldline` for c3 (reasoned: the read section 1). The door checks that the line exists, not what it does. A Developer that cannot cite falls back to an empty start, so the stall of dry2 can return for a weak model (reasoned).

**Measure.** With no model: on a copy of `dry6b.db`, s152's commit with no evidence gets no claim (control: a claim). With a model: replay s152 on qwen3.5:9b, 5 samples, and count claims with evidence and cited lines that do not do what the criterion says.

**Departure.** None. It applies "Every claim cites a source. A seat can check the claim against the source" (observed: `plans/composition.md` 78 to 79). It adds a condition to the claim of 2026-11-02 17:14 and removes no check, so it stays inside that ruling (reasoned).

## 4. The control: what the recorded runs give today

From `dc360/control.py` on `mr362/runbase.json`, the read's fork and head runs of every criterion test of every recorded merge (observed).

| Count | Value |
|---|---|
| Merges on record | 19, on clickI, tipsI and icalendarI |
| Merges with every criterion test green at the fork | 3: the arm's run 1, night 171 `bg_2` at 090dec8e, night 174 `bg_3` at d6937a50 |
| Merges with some tests green at the fork | 7 |
| Merges with no test green at the fork | 9 |
| Criterion tests | 66, all green at the head |
| Criterion tests green at the fork | 21 |
| Claims merged | 1, and it is false (observed: the read section 1) |
| True claims merged live | 0. Dry2's true claim came before the build and ended by his drop (observed: `plans/stack.md` block 360) |
| Critic step 2 acts on the claim | 0 (observed: the read section 1, no `verdicts.claim_encodes` in s154) |
| Times the claimed line reached him | 0 of 1. m31 waited, and `_render_state` returned first (observed: the read section 2) |
| Touch pages he read after their merge | 2 known: run 1's m31 and dry3's m40. The nights keep no merge time, so they are not counted (observed: the read sections 2 and 8) |

Under each shape, on the same records (reasoned): A shows 3 lines and stops nothing. B holds 1 batch. C stops 3, one of them right. D refuses 1 pass, s154 turn 2. E refuses 1 claim, s152.

## 5. Recommendation

**Build A and D, in two slices. Do not build B, C or E now.**

The reason, from the purpose line and the destination (observed: `plans/composition.md` 8 to 14, 78, 83 to 85):

- "No work stays invisible." Today the claimed line reached him 0 times of 1. A puts it in the turn of the merge, and every shape needs that reader (reasoned).
- "Honest about where small models stop." A says on his page that the tests are the only evidence and that they pass on the old code. The touch page stops asking for a go that the run already took.
- "The feedback rate is the ceiling. A weak model is trusted only as far as the loop that checks it is short." On a claim the only check is the Critic's step 2, and the Critic skipped it. D puts that check inside the same session, at no cost to him. B moves the check to the scarcest budget, and C stops every true claim.
- "A careful person ... gets a merged change they can read." A false claim is a merged change that reads as done. A plus D make it a candidate that he can see is weak, in the turn of the merge (reasoned).
- The records do not yet justify a hold. 1 claim of 19 merges, false, with both of its safeguards broken by defects of their own (observed: the read, Result). The rate of false claims after the fix is the count that would justify B (reasoned).

**Slice 1, the claim readers, no new run.** `code_read`'s claim note. D's door in `_route_fault` and its sentence in `review.md`. The shipped lines under a waiting ask, with the claimed line naming its request and tests. The touch page of a merged batch as a record. Red tests on a copy of `dry6b.db`: the four no-model controls of A and D. About 4 to 5 cycles: two door texts and a page form in one pass, 2; the door of D, 1; one review, 1; the gate, 1 (reasoned: the anchors).

**Slice 2, the fork run of a change batch.** The harness runs the Tester's tests in a checkout of the fork, the Critic's `tests.load` shows the line, and the state shows the merged line. Red test: the 19 recorded merges give 3 flags. About 4 to 5 cycles: an instrument fix, 3; one review, 1; the gate, 1.

**Price.** About 9 cycles after this page, against 6 to 7 in the read, because D and the split into two slices add about 2 (reasoned).

**Departure.** None. The recommendation leaves ruling 2 of 2026-09-12, R7, and the ruling of 2026-11-02 17:14 as they are.

**What comes next on a count.** If D's replay shows the Critic claims `True` by rote, E is next, because a cited line is a source that a seat can check. If false claims merge on the next 3 dry runs after A and D, B or B' goes to him (reasoned).

## 6. The one question for the principal

A shape departs from a ruling: B. The recommendation does not take B. Ask only if he wants more than visibility.

> **Your ruling of 12 September says that after you approve the first page, nothing waits on a page. Option 2 below departs from that ruling for one case.**
>
> The situation: you ask the team, "Fold long lines so that no word splits." The builder looks at the code and says, "The code already does this." He changes nothing. A tester writes three checks, and all three pass on the code as it is. A reviewer reads the checks and passes them. The checks join the project, and the job is marked done. In truth the code still splits words, because the checks test the old line length and not the split.
>
> What happens today: you learn of it after the job is done. Your screen shows an older page that says "Before I build this", and no line says that the job closed with no code change.
>
> Option 1, the team shows it: the job still closes by itself. In the same round, your screen says, "Done with no code change: fold long lines. No check of it fails on the old code, so the checks do not show a change." The reviewer must also read each check against your words before it can pass a job with no code change. If you disagree, you say so, and the team opens a new job on top.
>
> Option 2, the job waits for you: when the builder says "already done", the job does not close. You get a page with each check in plain words, and the job waits until you say "ok". Other jobs go on while it waits. If you never answer, it waits for ever.
>
> One exact analogy: a builder says a wall already stands. In option 1 the inspector must sign each test of the wall, and the owner reads the report the same day. In option 2 the owner walks out to look at the wall before anyone signs.
>
> Recommended: option 1 now. Count how often a job closes this way with a wrong check, and ask again if it happens.

## 7. What is unproven

- **Whether the Critic uses the fact.** No sample shows a Critic on qwen3.5:9b that sees the claim note or D's refusal. A and D make the reading an act. They do not prove a right reading (reasoned).
- **The rate of false claims.** The records hold 1 claim, at temperature 0 and one sample, and it is false. Dry2's true claim never ran under the build (observed: section 4).
- **The cost of the fork checkout.** The harness has no checkout of the fork for a change batch. Its runtime on a larger repository is not measured. The read's estimate is a few seconds on icalendar (observed: the read section 7).
- **The two docstring merges.** I read them as right merges whose tests cannot show the change, from his words on the two nights. I did not open their tests (reasoned: section 3 C).
- **D's claim store.** `ctx.verdict_claims` holds for one session. I did not check that every path to a pass runs in the session that claims (observed: `verdicts_claim_encodes`; reasoned).
- **The touch page after a merge on the nights.** The nights keep no merge time, so the count of 2 is a floor (observed: the read section 8).
- **The criteria themselves.** c3 of run 1 says a line with no whitespace is not folded, which breaks the 75-octet rule of c1. A bad criterion can make every shape fail. I did not follow that cause (observed: the read section 8).
- **The line numbers of the read.** The read cited `822311e0` in another worktree. I checked the four facts at 47ca1e43 in this checkout, and the lines agree (observed: section 1).
