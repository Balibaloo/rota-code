# Design: a claim of "already done" that is false (2026-11-06)

A design page by C76 step 3b for frame 360, after `plans/arm-run1-merge-read-2026-11-06.md` (`the read` below). Read-only at 47ca1e43 on `rota/foundation`. No model ran. No tracked file changed except this page. The one probe is `dc360/control.py` in session 8b2312ef's scratchpad, run on the read's `mr362/runbase.json`.

## Result

Revised once after `plans/design-false-claim-review-2026-11-06.md`. The Revision section at the end supersedes sections 5 and 6, the claimed line and the touch page of shape A, and shape D (observed: the review).

**Recommend shapes F and A, in two slices, with no new gate on the merge and no departure from a ruling.** F tells the Tester of a claimed batch that its tests decide the claim, so a test that fails on the code as it is disproves the claim by a run. A shows the claim to him in words that are true in every state, in the turn of the merge. **The limit: a false claim whose tests are weak still merges before he reads of it** (reasoned: Revision R3).

- **The main finding.** On a claimed batch the head is the fork. So every test that passes at the head passes at the fork, for a true claim and for a false claim alike (observed: `rota/roles/api.py` 26439 to 26441 writes the fork as `head_commit`; the read section 7 item 1 said the same). The fork run cannot tell a true claim from a false one. A reading of each test against its criterion can, and a run with the criterion's surface replaced by a stub can show a test that reaches no behaviour (reasoned: Revision, shape G). The fork run tells something new only on a change batch.
- **The ruling of 2026-11-02 17:14 rested on the reason "a test run and not a model's word checks the claim".** On run 1 the test run checked nothing, because the Tester's tests pass on the old code (observed: `plans/stack.md` block 360, status 14:28; the read section 1). So the question in the Revision opens with that ruling.
- **Seven shapes.** A, show the fact. B, a claim waits for his word. C, the fork fact gates. D, the Critic records a boolean for each test (out: 29 of 29 `True` on nights 114 to 128). E, a claim cites its source line. F, the Tester's tests decide the claim. G, a stub run of each criterion's surface.
- **B departs from ruling 2 of 2026-09-12. C departs from the ruling of 2026-11-02 17:14 and from the rule of 2026-09-02 that no rule bounds an LLM judgement. D departs from the same rule of 2026-09-02.** A, E, F and G depart from no ruling (reasoned: section 3 and the Revision).
- **Price: about 10 agent cycles after this page.** Slice 1 about 5 to 6, slice 2 about 4 to 5 (reasoned: Revision R5).
- **The question for Roman is Revision R6.** Recommended: the Tester decides the claim and he reads it in the same round, with no wait.

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

## Revision, after the review (2026-11-06)

The review is `plans/design-false-claim-review-2026-11-06.md`: revise, 5 high and 3 low findings. I checked each high finding against its source before I took it (observed: the lines named below, read at 47ca1e43). This section supersedes sections 5 and 6, the claimed line and the touch page of shape A, and shape D.

### R1. The findings, taken or not taken

1. **Taken. D repeats a door shape that the records measured as rote.** `plans/frame170-merges-read.md` line 50 says "`claim_encodes` came back `True` for 29 of 29 claims", and line 107 says this was on "tests that never run the criterion's path" (observed). A refusal text "is an instruction that the model follows literally" (observed: `plans/operating-facts.md` 330). D also bounds a review judgement by rule, against "Do not bound LLM judgements (slicing, triage, review) by rule" (ruled: Roman, 2026-09-02, `plans/operating-facts.md` 301 to 305). D is out. The one check that stays at the Critic is the `code.read` note, and it is a fact of the batch row, not a word of the model (reasoned).
2. **Taken. The claimed line is false on run 1.** `CLAIMED_LINE` at `rota/roles/principal.py` 303 says "These tests show the code already does this" (observed). On run 1 the tests pass on code that does not do it (observed: the read section 1). My first option 1 promised words that no slice built for a claim. R3 gives the new line, and R6 quotes the same words.
3. **Taken. The touch page "as a record" stays an open ask.** `pending_asks`, `principal.py` 171 to 192, returns every open message to the principal, and `_render_state` 332 to 340 heads it with "Waiting on you." (observed). Frame 358 built the after-merge shape: "A re-survey after a merge asks nothing, so the state view shows it as one sentence and no page" (observed: `principal.py` 410 to 415). R3 follows that shape and names each line that moves.
4. **Taken. The page had no shape at the Tester.** The Tester's brief says: "A test written against code that already exists tends to encode what the code does rather than what was asked for, which is precisely the failure Critic cannot catch" (observed: `rota/roles/prompts/tester/tests_missing.md` 23 to 25). The brief holds no word "claim" (observed: a search). R2 adds shape F.
5. **Taken. Slice 1 named a control that needs slice 2, and D's replay had no target.** A's third control needs the fork run (observed: section 3 A). R4 lists controls that each slice can run and fail.
6. **Taken. The question omitted the reason of the ruling of 2026-11-02 17:14.** The recommendation that he took was "A, because a test run and not a model's word checks the claim" (observed: `plans/stack.md` block 360, status 14:28, and the ruling at status 17:15). My main finding shows that this reason fails on a false claim. R6 opens with that ruling.
7. **Taken, as shape G. A mechanical fact can show a vacuous test.** `tst_fold_c3` folds the word "Short" and asserts that every line is at most 75 octets (observed: `tests/test_no_split_word.py` in `arm362/icalendarI`). Under a fold that does nothing, that test still passes, and so does `test_fold_avoids_splitting_words`, whose `"A" * 80` holds no space (reasoned: the bodies, no run). The word "only" is gone from the main finding.
8. **Taken. B' leans on a hold that nothing releases.** `merge_gate` has one reader, `mergeable` at `lifecycle.py` 1168, and "`merge_gate=review` waits on a page that nothing presents" (observed: `plans/operating-facts.md` 377). B' needs the merge read page of `plans/principal-flow.md` page 4 first, about 8 to 10 cycles (reasoned: the anchors, a seam design).

### R2. The new shapes

#### F. On a claim, the Tester's tests decide the claim

**What the Tester is shown and asked.** The wake of `tests_missing`, `rota/core/predicates.py` 959, carries a detail on a batch with `claimed_head = head_commit`: "No code changed on this batch. The Developer claims that the code as it is already meets each criterion. Your tests decide the claim." `rota/roles/prompts/tester/tests_missing.md` gets one paragraph for that detail: "For each criterion, pick an input where code that meets the criterion's words and code that does not give different results. A test that fails on the code as it is shows that the claim is false. That is a right result, not a fault of your test. Do not change a test so that it passes."

**What the run decides.** The harness runs the tests at the head, which is the fork. A criterion test that is red and not a base red disproves the claim. That is a test run, not a model's word (reasoned: `harness.reds_that_hold`, 567 to 583).

**What happens when a test fails.** `tests_failing` wakes the Developer with the red test, as on any batch (observed: `plans/f360-review-p1.md` point 2, step 2). The Developer's real commit clears `claimed_head` (observed: the same, Pass 1b, F7). The batch then runs the normal loop to a merge. He reads "Done: 1 change built, tested and merged.", which is true. He reads no line about the disproved claim, as he reads no line about any red test inside a build today (reasoned: `_render_state` shows no red test of a batch that later merged).

**What a weak test does.** A weak test passes on the code as it is, so the claim stands and F does nothing. Run 1 is that case: three tests, all weak, all green at the fork (observed: the read section 1). The records show what Testers do after a code change: 45 of 66 criterion tests fail at the fork, and 21 of 66 pass there (observed: section 4). Some of the 21 are right, for criteria that keep a behaviour (observed: the read section 6). On a claim, the records hold 1 batch and 3 tests, and 0 of 3 failed at the fork. That is no rate (reasoned). A further limit: run 1's c1 and c3 contradict, so a right test of each fails on any code. A disproved claim then goes to a Developer who cannot pass both (reasoned: the read section 8).

**Cost.** To a correct run: no extra session and no extra run. The Tester gets about 60 words, on a claim only. To his attention: none. A true claim passes as before.

**Measure.** With no model: on a copy of `dry6b.db`, the wake of s153 rebuilt from the rows holds the claim detail (control: no claim word, review probe p4). It fails if the detail is missing or reaches a change batch. On the `world` fixture of pass 1, a claim with a criterion test red at the fork wakes the Developer on `tests_failing`, and the later merge shows no claimed line (control: probe p2 of review p1). With a model, the target set before the run: replay s153 on qwen3.5:9b, 5 samples, with the new wake. F holds on this model if at least 1 of 5 samples writes a c3 test that fails on `99619246`. 0 of 5 says that F's brief part does not move this model, and A's line is what remains.

**Departure.** None. A brief change is the form that the rulings on doors prefer: "Prefer the brief unless the rule is a fact about the harness" (ruled: Roman, 2026-09-02, `plans/operating-facts.md` 305).

#### G. A stub run shows a test that reaches no behaviour

**What changes.** For each criterion of a claimed batch, the harness runs its tests once more with the criterion's surface replaced by a stub that returns its first argument. A test that still passes reaches no behaviour of the surface. The Tester's wake and his claimed line name it.

**How it fails.** A stub that fits every signature does not exist. An identity stub breaks a function whose result is not its argument, and then every test fails, so no test is flagged (reasoned). The surface comes from the criterion's `surface_refs`, and on run 1 the fold sits one call below `to_ical` (observed: the review, outside the points).

**Cost.** A seam design with its night, about 8 to 10 cycles (reasoned: the anchors). **Measure.** With no model: on run 1's tests with `_foldline` replaced by an identity, `tst_fold_c3` passes and the first function of `tst_fold_c1` fails. That is a prediction, and it fails if `tst_fold_c3` goes red (reasoned). **Departure.** None. Not recommended now, because no general stub is designed.

#### D, as written: out

D is out by R1 item 1. The review's variant, a `test:` value that carries the test's assertion line and the criterion's words as substrings the door matches, is still a quote that the model picks. I do not recommend it now (reasoned: frame 170 moved the Critic to pass lines, and the run's pass lines landed on three weak tests).

### R3. The lines that he reads, each true in every state

1. **The claimed line**, slice 1, in place of `CLAIMED_LINE`: "<request>: no code changed. The team says the code already does this. The only evidence is <n> tests that the team wrote, and they pass on the code as it was. Ask me to show them." A claimed batch merges only when its tests pass at the fork. So each sentence is true for a true claim and for a false claim (reasoned: fact 1).
2. **The touch note of a merged batch**, slice 1, in the shape of frame 358. At render time `pending_asks` skips an open touch note whose every batch is merged, so no "Waiting on you." heads it. `_render_state` shows one line: "The plan for <request> reached you after its merge. Ask me to show it." The message stays in the register, so nothing stops quietly (reasoned: `plans/composition.md` 50 to 51).
3. **The lines that move under a waiting ask.** Only the claimed line of item 1 and the change-batch line of item 4. The Done count, the notes tail, the fault line and the objections tail do not move, so the tail of line 339 does not show twice (reasoned).
4. **The change-batch line**, slice 2: "Merged: <request>. No test of it fails on the code before the change, so no test shows the change." It is true whenever every criterion test passes at the fork (reasoned).
5. **The Critic's note**, slice 1, `code_read` at 24255 on a claimed batch: "No code changed on this batch. The Developer claims the criteria are met. The tests are the only evidence." It replaces "no commit yet on this batch" and reads the batch row only.

### R4. The recommendation, the slices, the prices and the measures

**Build F and A in two slices. Do not build B, C, D, E or G now.** The reason, from the purpose and the destination (observed: `plans/composition.md` 8 to 14, 22 to 23, 83 to 85):

- "The feedback rate is the ceiling." F puts the check of a claim in a test run, the shortest loop rota has, at the seat whose brief names this failure. The Critic's boolean is not a check (R1 item 1).
- "No work stays invisible" and "Honest about where small models stop." A's line says that the tests are the only evidence and that they pass on the old code. He reads it in the turn of the merge, also under a waiting ask.
- "Their attention is the scarcest budget. Sign-offs after that, including on merges, are opt-in." F and A spend none of it on a true claim. B spends one page per claim and asks him to judge the tests, which the Critic of run 1 judged wrong (reasoned).
- The honest limit: under F and A, a false claim whose tests are weak still merges before he reads of it. His "no" then opens a new batch on top (ruled: 2026-09-12, ruling 3).

**Slice 1, the claim, with no new run.** F's wake detail and Tester paragraph, and R3 items 1, 2, 3 and 5. Controls with no model, each able to fail on today's code:

1. On a copy of `dry6b.db`, `render_state` shows no "Waiting on you." and shows the touch line and the claimed line (control: "Waiting on you." and m31 whole).
2. On the same copy with one more open ask to him added, the state shows that ask, then the claimed line once (control: the ask alone).
3. s154's `code.read` on the copy gives the claim note (control: "no commit yet on this batch").
4. s153's wake rebuilt from the copy holds the claim detail, and the wake of dry3's change batch `bg_1` does not (control: no claim word).
5. On the `world` fixture, a claim with a red criterion test wakes the Developer, and the merge after a real commit shows "Done" and no claimed line (control: probe p2 of review p1).

With a model: the s153 replay of F, target at least 1 of 5, set before the run. Live: on the next 3 dry runs, each claim either meets a red test or reaches his state with its line in the turn of the merge. Target: all.

Price: about 5 to 6 cycles. The wake detail and the brief paragraph, with the Tester cases on the register, 2 to 3. The three texts and the render filter, one pass, 2. One review, 1. The gate, 1 (reasoned: the anchors).

**Slice 2, the fork run of a change batch.** The harness runs the Tester's tests in a checkout of the fork. `tests.load` shows "passes on the code before the change" or "fails on the code before the change" for each test, and the state shows R3 item 4. Control with no model: over the 19 recorded merges the reader flags exactly the 3 of section 4 (control: no flag). It fails on a fourth flag or a missing one. Price: about 4 to 5 cycles. An instrument fix, 3. One review, 1. The gate, 1.

**Price in all: about 10 cycles after this page.** **Departure: none.** Ruling 2 of 2026-09-12, R7 and the ruling of 2026-11-02 17:14 stay as they are. F keeps that ruling's shape and puts back its reason, a test run that checks the claim.

**Next on a count.** If a false claim merges past a Tester shown the claim on the next 3 dry runs, the question of R6 goes to him again for option 2 or B'. If the s153 replay gives 0 of 5, G is next (reasoned).

### R5. Prices against the first pass

The first pass priced about 9 cycles for A and D. The revision prices about 10 for F and A. D's door goes, F's brief and its register measure come in, and the render filter of the touch note is added (reasoned).

### R6. The question for the principal, in plain words

> **On 2 November you ruled that when the team finds a job already true of the code, the team proves it with checks that join the project, and you read "No code changed". You were told the reason: a check that runs, and not a team member's word, tests the claim.** On a trial run that reason did not hold. The builder said "already done" and changed nothing. A tester wrote three checks, and all three passed on the old code, because they tested nothing that the job changes. A reviewer passed them. The job closed as done, and in truth the code still breaks long words in two. A check that passes on the old code always passes when nothing changed, so it cannot tell a true "already done" from a false one.
>
> What happens today: the job closes by itself. Your screen shows an older page that says "Before I build this" and asks you to go ahead. No line says that the job closed with no code change.
>
> Option 1, the tester decides, and you read it the same day: when the builder says "already done", the tester is told so. The tester is told to pick a case where a right and a wrong program give different answers. If a check fails on the code as it is, the claim is false, and the builder gets the failing check and works as usual. If every check passes, the job closes, and your screen says: "Fold long lines: no code changed. The team says the code already does this. The only evidence is 3 tests that the team wrote, and they pass on the code as it was. Ask me to show them." The old page no longer asks you to go ahead. If the checks are weak, a false "already done" still closes before you read of it. Then you say so, and the team opens a new job on top.
>
> Option 2, the job waits for you: when the builder says "already done", the job does not close. You get a page with each check in plain words, and the job waits until you say "ok". Other jobs go on while it waits. If you never answer, it waits for ever. You must then judge whether each check tests your words, which the reviewer judged wrong on the trial run.
>
> Option 3, no "already done": the builder may not say it. A job with nothing to change goes round three times, and you get a page that says "The team gave up", as before your ruling.
>
> One exact analogy: a builder says a wall already stands. In option 1 the inspector is told to push where a weak wall gives way, and the owner reads his report the same day. In option 2 the owner walks out to look at the wall before anyone signs.
>
> Recommended: option 1. Its limit: a weak inspector can still sign a weak wall, and you learn of it after the job closes. If that happens on the next three trial runs, I ask you again about option 2.

### R7. What is unproven, added

- Whether qwen3.5:9b writes a test that fails on the old code when it is told of the claim. The s153 replay measures it (reasoned).
- Whether a Tester that sees its own test red on a claim changes the test to pass. F's paragraph forbids it. No sample shows it (reasoned).
- G's stub is a prediction from the test bodies. I did not run it (reasoned: R1 item 7).

## Amendment of 2026-11-08

An amendment on Opus for frame 360, by the brief `f360_design_amend_brief.md` in the scratchpad of session 0d047fa7. Read-only at b2c67c3e on `rota/foundation`. No model ran. No tracked file changed except this page. The probes are `p360c/p1` and `p360c/arch` in the same scratchpad, and their rows are cited as "P1 sample n" and "A sample n". This section adds shape H. R4's slice 1 stays as built, and H1 is the next slice.

### H0. Result

- **Recommend H1 with its reach.** On a claim, the Architect writes one program, and the run door executes it at the claimed head. The door records the program, its stdout and its stderr in a new table. The seat types no output and no verdict (reasoned: H2 below).
- **The fact gates nothing.** The batch closes as today. The run's stdout goes to the Tester's wake, to the Critic's note and to his claimed line in the turn of the merge (reasoned: H6).
- **Price: about 9 cycles.** To his attention: one sentence and up to 600 characters of printed output per claim, and claims are 1 of 19 merges (observed: section 4).
- **Departure: none from a ruling of his.** H1 departs from the session's reading of 2026-11-08 08:20, "records its output as the fact that gates". The status line of 09:29 already withdrew that reading (observed: `plans/stack.md`, frame 360).
- **The limit.** A weak example prints an output that looks right. A sample 3 did that. Then F and A are what remain, and he judges the printed output himself after the merge (observed: H1; reasoned).
- **H2 departs from ruling 2 of 2026-09-12. H3 cannot be a general door.** The only general check of the output is the Tester's test at the run's input, and H1's reach gives the Tester that input (reasoned: H4, H5).
- **One more door fact from P1.** P1 sample 1 claimed `encodes=False` for c2 and then passed with `test: tst_fold_c2`. The `test:` route does not read the session's own claim. A door fix, about 2 cycles, with no departure (observed: H8).

### H1. The counts, sample by sample

The Architect probe, `arch/live/results.json`, qwen3.5:9b, sample 1 at temperature 0 and samples 2 to 5 at 0.6 (observed: each row).

| Sample | The program | The real stdout | What the seat recorded | `holds` | Refusals met |
|---|---|---|---|---|---|
| A1 | imports `_foldline` from `icalendar.parser.string`. Run 1 failed on `assert "\n" not in line`, runs 2 and 3 completed | `'... without splitting wo\r\n rds like ...'`. A split word | "folded at space, words intact" | true | path |
| A2 | imports `_foldline`. Run 1 imported `foldline` and failed on the same assert, run 2 caught it, run 3 split the input by line | `'... at a space w\r\n here it can ...'` and `'... as befo\r\n re.'`. Two split words | a paraphrase: "folded at spaces without splitting words (e.g., "before." remains intact)" | true | path, `holds` as a list, `holds` not a boolean |
| A3 | imports `_foldline`, one run | `"... so that words "`, then `" are not split ..."`. The cut fell on a space, so no word split | "The claim is violated. ..." | true | path, two parse faults, `holds` not a boolean |
| A4 | defines its own `def _foldline(line)` and imports nothing. Its first try wrote over `src/icalendar/parser/string.py` | three lines folded at spaces, by its own function | the stdout, copied | true | path, two parse faults, `holds` not a boolean |
| A5 | no run. Its one `code.run` aimed at `src/icalendar/tests/test_icalendar.py` | none | four tries of "Claim verified: ..." before any run | none | path, `holds` as a list, "run the code first" four times |

Counts (observed: the table):

- 4 of 5 ran a program. 3 of 5 ran the project's function. 2 of 3 of those runs show a split word in the real stdout.
- 3 of 4 records hold the seat's own words in place of the stdout. 4 of 4 records say `holds: true`.
- 5 of 5 met the path refusal. 2 of 5 aimed the program at a file of the project. 4 of 5 met a `claim.record` refusal.
- 0 of 5 called `code.source`, so no sample read `_foldline` before it wrote the program (observed: `turns.completion` of s164 in each sample database).

P1, the Critic replay with the arm's root, `p1/run/results.json` (observed):

- Pass in P1 samples 1, 2 and 4. No verdict in P1 samples 3 and 5. One challenge to the Tester, P1 sample 5, on c2.
- 3 of 5 claimed `encodes=False` for c2: P1 samples 1, 3 and 5 met the refusal "it was claimed False". P1 sample 1 then landed a pass with `test: tst_fold_c2`.
- 0 of 5 said that the claim is false.

### H2. Shape H1: the Architect runs the code, and the door records the run

**What changes, by file and door.**

- `rota/core/db.py`: a table `claim_runs`, with `id` from the content (batch, commit, program), `batch_id`, `commit_sha`, `session_id`, `program`, `stdout`, `stderr`, `returncode` and `imported`. Its one writer is the `code.run` door.
- `rota/roles/api.py`: `@op("code", "run") code_run(ctx, text)`. It takes no path. The door writes the program to a folder outside the worktree, and it runs the program with the worktree's interpreter, `python_for`, with the worktree as the working folder. The run uses `execute.run` with a timeout, as the harness does for tests (observed: `rota/core/harness.py` 376).
- The door refuses before the run, with the reason named:
  1. a batch whose head is not a claim;
  2. a program whose syntax tree defines a function, a class or a name that a source file of the touch defines (A4's `def _foldline`);
  3. a program that assigns to an attribute of a module of the touch;
  4. a program that imports no module of the touch and no parent package of one (A4).
- The door records each run that completes, returns the stdout and the stderr, and says "The run is recorded. End the session." It refuses a fourth run in one session, as `code.read` refuses a fourth read.
- `rota/core/predicates.py`: a predicate wakes the Architect on `tick:claim` for a claimed batch with no `claim_runs` row and no ended `tick:claim` session at its head. Its detail carries the request, the touch files and the touch symbols, as the probe's `wake_detail` did. `tests_missing` on a claimed batch waits until that session ends. That is a wait on a seat, which frame 204's design keeps (observed: `rota/core/lifecycle.py` 1235 to 1236).
- `rota/roles/prompts/architect/claim.md` and `claim.tools`: see H5.

**What he reads.** One more sentence in the claimed line, in H6.

**Cost.** One Architect session per claim, 7.7 to 20.2 seconds and 5 to 7 model calls per sample (observed: `arch/live.out`). To his attention: one sentence and up to 600 characters per claim.

**How it fails.**

- A weak example. A3's input folded at a space by chance, so its true stdout shows no fault (observed: H1). 1 of 3 runs of the project's function is that case.
- No run. A5 ran nothing. The claimed line then says "No run of the code is on record", and F and A remain (reasoned).
- He reads escapes. A1 and A2 printed `repr`, so the fold shows as `\r\n`. That is exact, and it is not plain words (reasoned).
- The Tester copies the printed output as the expected value, and the test then encodes what the code does. The Tester's paragraph must forbid it (reasoned: `tests_missing.md` 23 to 25).
- The syntax check closes the names and the attributes only. A program can still `exec` a string. The check stops the act of A4, not every dodge (reasoned).
- The program is code that a model wrote, and it runs at the same trust as a test that a model wrote (reasoned: the harness runs the Tester's tests in the same worktree).

**Measure.** With no model, each red on today's code because no door exists:

1. A4's program text is refused, and the refusal names `_foldline`.
2. A2's third program is accepted. One `claim_runs` row holds `befo\r\n re.` in its stdout.
3. After A1's second program, `git status` of the worktree is empty, and no file of the program is under the tree.
4. On a copy of `dry6b.db` with A1's row, the claimed line holds `splitting wo\r\n rds` and does not hold "folded at space, words intact".
5. On the same copy, the Tester's wake and the Critic's `code.read` note hold the same stdout. The wake of dry3's change batch `bg_1` holds none.
6. `architect/claim.tools` holds `code.run` and no door that takes `holds` or an output.

With a model, the targets set before the run: the probe on the built door, 5 samples on qwen3.5:9b. H1 holds on this model if at least 3 of 5 runs import the touch and at least 2 of 5 show the split. Then replay s153 with the run in its wake. F with H1 holds if at least 1 of 5 c3 tests fails at `99619246`.

**Departure.** None from his rulings. His ruling of 2026-11-06 14:19 stays met in form, by the Critic's pass. The run is evidence for him, not a verification (reasoned).

### H3. Shape H2: as H1, and the claim waits for his word

**What changes.** H1, and `mergeable` returns "waiting on the principal: the team says the code already does this" for a claimed batch with no ruling row of his. A hold page shows the request, the program and the printed output, then "Reply 'ok' to accept. Say what is wrong if it is not done." His "ok" writes a ruling row. His words go to the Developer and the Tester.

**What he reads.** One page per claim. Against shape B, he judges a printed output and not the code of a test. A1's `wo\r\n rds` is one look (reasoned).

**Cost.** About 5 to 6 cycles more than H1: the page form 2, `mergeable` and the land 2, one review 1, the gate 1 (reasoned: the anchors). To his attention: one page per claim, and every Developer escape to a claim is a page (observed: section 3 B).

**How it fails.** A hold that he never answers holds the claim for ever. The page count rises with the escape rate, which nothing caps (observed: section 3 B).

**Measure.** On a copy of `dry6b.db` before the merge, `mergeable` returns the wait (control: None, then merged). Live: count the holds and his rejections.

**Departure.** Ruling 2 of 2026-09-12: "Hold at intent time only. No batch starts until the first page is answered. After that, nothing waits on a page" (ruled: Roman, `rota/DECISIONS.md` 1383 to 1384). It also departs from frame 204's design, "The merge waits on the seat, never on a page", and from "Sign-offs after that, including on merges, are opt-in" (observed: `lifecycle.py` 1235 to 1236; `plans/composition.md`, The parties).

**The reading that a claim is an intent question.** The claim asks him whether what he meant is already true of the code. Intent is his to hold (observed: `plans/composition.md`, The parties). On that reading H2 holds at intent time, inside the reason of ruling 2. The letter still departs, because the batch started before the claim (reasoned). The opt-in form exists: `merge_gate=review` holds a claimed batch today, and no page presents that hold (observed: `lifecycle.py` 1241 is its one reader; the review, finding 8).

### H4. Shape H3: a check judges the output

**Not designed as a door.** A general door cannot write the check for an arbitrary request (reasoned). The check needs the meaning of the request in code. For the fold, it must find a word of the input that the output cuts across a CRLF and a space.

**The fold case shows it.** The session wrote that check for this one request, `split_word` in `arch/probe_architect_claim.py`. It gave "no" for A1's run, and A1's stdout holds `wo\r\n rds`, because A1 printed a `repr` on one line (observed: `results.json`, `split_in_run` of sample 1). So a check written by hand for one request misread 1 of 4 runs. The clause "keep everything else as before" has no check on one run at all. A3 raised it and could not test it (observed: A3's record).

**What the Tester's criteria give.** A check per request is a test, and the Tester writes the tests. c3 says "Folding does not split a word", which is the assertion at A1's input (observed: `criteria` in `dry6b.db`). So H3's check is the Tester's test at the run's input. That is F with the run in the Tester's wake, which is H1's reach (reasoned). c1 and c3 contradict when no whitespace falls inside 75 octets. A1's and A2's inputs hold spaces, so the contradiction does not reach them (reasoned).

### H5. The seat

**Why the Architect** (observed: each record named; reasoned: the choice):

- The Developer made the claim. His ruling of 2026-11-06 14:19 asks for another seat.
- The Tester's tests are the evidence under question. Its brief says that a test against existing code "tends to encode what the code does" (`tests_missing.md` 23 to 25). Under H1 the Tester reads the run and does not make it.
- The Critic has no instrument and its brief says "there is nothing to fetch" (`critic/review.md`). Its pass is the verification of 14:19, so a run in its hands makes one seat both maker and judge of the evidence. On qwen3.5:9b it went 0 of 20 on the vacuous test case (the read, section F).
- The Architect holds the touch. Its `annotate` writes the `batch_touch` rows. The probe's wake named their files and, from the index, `_foldline` (observed: `touch` in the probe). It already reads source with `code.source` and `code.probe` in `annotate.tools` and `touch_strayed.tools`.
- On dry run 7 its `touch_strayed` note judged the removal in `_foldline` a mistake that "should be preserved" (`plans/dry7-read-2026-11-07.md` 91).
- It has no stake. It wrote no code, no test and no verdict on the batch.

**What the probe shows of the seat.** 4 of 5 ran a program at the touch, so the seat can do the act. 4 of 4 recorded `holds: true` against two stdouts that show a split, so the seat cannot do the judgement. H1 asks for the act only (observed: H1; reasoned).

**What the brief and `.tools` gain.**

- A new mode, `architect/claim.md`, about 700 characters: "MODE: claim. The Developer changed no code and says the request is already true of the code. Read the function at the touch with `code.source`. Import it from its module. Never write your own copy. Write one program that calls it with one example from the request. Pick an example where code that meets the request and code that does not print different results. Print the input, then print the result with `print(repr(...))`. Call `code.run(text)`. The run is the record. You type no output and no verdict. End the session after one run that completes."
- `architect/claim.tools`: `code.source`, `code.probe`, `code.run`.
- `architect/base.md`: no change. "You are woken once, act, and end" already fits (reasoned).

**What the `annotate` piece cost the probe.** It filled 1,719 of the 5,628 characters of the system prompt, about 31 per cent. It set another task, "predict what one batch will touch". It named four tools the seat did not have: `tickets.scan`, `criteria.scan`, `code.probe` and `batches.annotate` (observed: `arch/dry/results.json`). That breaks "No brief grants what is not wired" (observed: `plans/composition.md`, The structure). 0 of 5 called one of them. 0 of 5 called `code.source`, and A4 wrote its own `_foldline`. The piece's part in that is not measured (reasoned). The door cost more: 5 of 5 met the path refusal and 4 of 5 a `claim.record` refusal. H1's door takes no path and has no record call, so both refusals go (reasoned).

### H6. The record

**Where the fact lives: the table `claim_runs`, written only by `code.run`** (reasoned). A ledger row does not fit. The ledger holds choices and defaults, its kinds are a fixed list, and frame 358's resolved row is written by the scheduler (observed: `lifecycle.discharge_touch_notes`). A run is a record observed from the code, and one word keeps one meaning.

**Which run is the fact.** The last row of the batch that completed. No seat picks it (reasoned). The reader keys the row by batch and not by commit, because `boot.py` 172 to 179 moves `claimed_head` to the merge's tests commit (observed).

**How his line reads it.** Frame 358's form: one sentence in the state view, no page, nothing asked, and "Ask me to show it" (observed: `principal.py`, `merged_touch_notes`). The run joins `claimed_lines`, which shows under a waiting ask too (observed: `principal.py` 399). The line, each sentence true in every state:

> "Fold long lines: no code changed. The team says the code already does this. The architect ran the code on one example, and it printed: <the stdout, first 600 characters>. The only other evidence is 3 tests that the team wrote, and they pass on the code as it was. The reviewer passed them. Ask me to show the program and the tests."

With no row, the third sentence reads "No run of the code is on record."

### H7. The reach

13 places read a claim today (observed: a search for `claimed_head`, `_claimed(`, `critic_claim_note`, `claimed_lines`, `CLAIM_DETAIL` and "check the claim" at b2c67c3e). What each becomes under H1 (reasoned):

| # | Place | Today | Under H1 |
|---|---|---|---|
| 1 | `predicates._claimed_batches` | the one test of a claim, `claimed_head = head_commit` | unchanged. The new predicate reads it too |
| 2 | `predicates.tests_missing`, `CLAIM_DETAIL` | "Your tests decide the claim." | waits for the Architect's session. Adds "The architect ran the code on one example, and it printed: <stdout>" |
| 3 | `runner._claim_line` | the claim words in every Tester and Critic wake | adds the stdout for both seats |
| 4 | `api.critic_claim_note`, in `code.read` | "The tests are the only evidence." | "The tests and one run of the code are the evidence. The run printed: <stdout>" |
| 5 | `api` encode note, 23589 | a red on a claim stands and goes to the Developer | unchanged |
| 6 | `api` replace refusal, 13157 | a red test on a claim stands on every try | unchanged |
| 7 | `api.verdicts_emit` guard, 18612 | no pass on another batch's claim | unchanged |
| 8 | `api.code_commit` claim branch, 26535 to 26541 | tells the Developer "The Tester's tests check the claim" | "The Architect runs the code, and the Tester's tests check the claim" |
| 9 | `api.code_commit`, 26547 and 26574 | a second claim against a red; a real commit clears the mark | unchanged. A real commit makes the run stale, and the reader then drops it |
| 10 | `boot.py` 172 to 179 | moves the claim with the merge's tests commit | unchanged. The run is keyed by batch |
| 11 | `principal.claimed_lines` | the claimed line, also under a waiting ask | adds the run sentence of H6 |
| 12 | `principal` Done count, 424 | a claim is not "built" | unchanged |
| 13 | `principal._built_words`, 2734 to 2745, and the Tester paragraph, `tests_missing.md` 27 | "and the tests check the claim"; "pick an input where ..." | `_built_words` drops "and the tests check the claim" and names the run. The paragraph adds: "The run shows what the code does, not what was asked. Write the result the criterion's words give for that input." |

**A finding outside the brief.** `_built_words` still says "and the tests check the claim" on the request-shift page (observed: `principal.py` 2738 to 2740). That is the assertion that the review's finding 2 removed from `CLAIMED_LINE`, and it is false on run 1 (observed: the review, finding 2). H1's reader pass fixes it.

### H8. The P1 door fact

`_route_fault`'s `test:` branch holds a value whose test is bound, live and passed at the head. It does not read `ctx.verdict_claims` (observed: the read, section C). P1 sample 1 claimed `encodes=False` for c2 and then landed a pass with `test: tst_fold_c2` (observed: P1 sample 1, `errors` and `verdicts`). The fix: the `test:` route refuses a test that the same session claimed does not encode its criterion. The refusal points to `msg.challenge_tester`. The door checks the seat's own recorded act, not its words, so it bounds no judgement (reasoned: "The door checks a fact, never the seat's words", the read, section C). About 2 cycles, a door text, in the same pass as H1 or before it. Measure: P1 sample 1's calls on a copy of `dry6b.db` give a refusal at the pass (control: the pass lands).

### H9. The recommendation and the price

**Build H1 with the reach of H7 and the door fact of H8. Do not build H2 or H3 now.** The reason, from the purpose and the ceiling (observed: `plans/composition.md`):

- "Every claim cites a source. A seat can check the claim against the source." The run is the first source that a claim cites, and it is a run, not a word.
- "A weak model is trusted only as far as the loop that checks it is short." The probe trusts the seat for the act, which 4 of 5 did, and not for the verdict, which 4 of 4 got wrong.
- "No work stays invisible." He reads what the code printed in the turn of the merge.
- "Sign-offs after that, including on merges, are opt-in." H1 adds no wait on him.

**Price: about 9 cycles.** The door, the table and the predicate, 3. The mode, the tools and a register case, 2. The readers of H7 and the door fact of H8, 2. One review, 1. The gate, 1 (reasoned: the anchors of section 3).

**Next on a count.** On the next 3 dry runs, count the claims whose printed output shows the request unmet and that merge. If one merges, H2 or its opt-in form goes to him again (reasoned).

**The measure on the next dry run.** Each claim gets one `claim_runs` row (target: all). The claimed line shows the stdout in the turn of the merge (target: all). The count of claims whose Tester writes a red test after the run (no target, a first count).

### H10. The question for the principal, in plain words

> **On 12 September you ruled that after you approve the first page, nothing waits on a page. Option 2 below departs from that ruling for one case. Option 1 departs from no ruling.**
>
> How it came to be: you asked the team, "Fold long lines so that no word splits." The builder said "already done" and changed nothing. A tester wrote three checks, and all three passed on the old code. A reviewer passed them, and the job closed. In truth the code still splits words. You then said, "try the planner", the team member who knows where each job lives in the code.
>
> On a trial the planner wrote a small program and ran it on the old code, five times. In two runs the printout showed "splitting wo" and "rds" on two lines, so the code splits words. The planner then wrote "words intact" and "the claim holds" anyway, in all four of its reports.
>
> What happens today: the job closes by itself. Your screen says that no code changed and that three checks pass on the old code. No run of the code is shown.
>
> Option 1, recommended, the printout is the record: the planner runs the code, and the system keeps what the run printed, never the planner's words. The tester sees the printout before it writes its checks. The job still closes by itself, and your screen shows the printout the same day. Its limit: a poor example prints nothing wrong, and a false "already done" can still close before you read it.
>
> Option 2, the job waits for you: as option 1, and the job does not close until you read the printout and say "ok". Other jobs go on while it waits. If you never answer, it waits for ever.
>
> Option 3, a machine judges the printout: not possible in general. A judge for "no word splits" fits one job only. The one written by hand for this job misread one run in four.
>
> One exact analogy: a builder says the wall already stands. A surveyor takes a photo of it. The file keeps the photo, not the surveyor's caption. In option 1 the owner sees the photo the day the job closes. In option 2 the owner sees the photo before anyone signs.
>
> Recommended: option 1. If a job closes on a printout that shows the job undone on the next three trial runs, I ask you again about option 2.

### H11. Doubt

- **One run, one request.** Every count rests on the claim of dry run 6b, the fold of icalendar, and its three tests (observed).
- **One model.** All ten samples ran on qwen3.5:9b. Four of five per probe ran at temperature 0.6, not the run's 0 (observed: `pins`).
- **The probe's wake is not rota's.** It used the `annotate` piece, a patched runner and a backend that ends the session at the record call (observed: `probe_architect_claim.py`). The `claim` mode and the door with no path are unmeasured.
- **The split in 2 of 5 depends on the example.** A3's example hid the fault by chance, so the rate is a property of the inputs the seat picks (reasoned).
- **The Tester with the run is unmeasured.** Whether it writes a red test at the run's input, or copies the printed output as the expected value, is not known (reasoned).
- **His reading of `repr` escapes is unmeasured** (reasoned).
- **The claim rate is 1 of 19 merges, and no true claim has merged live** (observed: section 4). H1's cost on a true claim is one Architect session, from the probe's timing only.
- **Not checked.** The register cases that a new Architect mode needs. The trust boundary of a run that a model wrote, beyond the harness's own runs of tests.

### Revision of the amendment

The review is `plans/design-false-claim-amend-review-2026-11-08.md`: revise, 2 high, 7 medium and 5 low. I take all 14 findings. This section supersedes the parts of H0 to H11 that it names (observed: the review). No model ran. No tracked file changed except this page.

#### RA. The findings, taken

1. **F1, taken. The limit of H1 is wider than a weak example.** Under H1 the fact gates nothing, so only a red test stops a false claim. In A1 and A2 the printout shows the split, and H1 still merges both. He reads the printout after the merge (observed: H1 table; reasoned: H2). The limit, in place of H0's fifth bullet and H10's option 1: **"A false claim closes even when the printout shows the fault, unless a test goes red. He reads the printout after the merge."** On the measured case the trigger of H9 is predicted to fire on the first such claim, because 2 of 5 printouts showed the fault and nothing in H1 acts on them (reasoned). So H9's "Next on a count" is a check of that prediction, not an open question.
2. **F2, taken. "Departs from no ruling" is withdrawn.** His ruling of 2026-11-06 14:19: "It can close as long as it is verified by another seat (and the review every merge setting is not on)" (ruled: Roman, `plans/stack.md`, frame 360). Under H1 the Critic's pass meets "verified by another seat" in form only. P1 gave 0 of 5 Critics who said that the claim is false, and the read, section G, shows that the Critic has no means to verify a claim (observed). So H1 keeps the letter of the 14:19 ruling and not its intent. RE opens the question with that ruling.
3. **F3, taken. The door stores the exact bytes.** `execute._local` decodes with universal newlines, so a plain print of a fold is stored as two line feeds and no CR (observed: the review's probe `rev360/crlf.py`; `rota/core/execute.py` 43 to 45). A3's seat read those two line feeds as "inserts two newlines" (observed: A3's record). The door therefore sets `PYTHONIOENCODING=utf-8`, runs the child with its stdout opened with `newline=""`, captures bytes, and stores the bytes as `stdout_bytes`. The text the line shows comes from those bytes. Each CR LF followed by a space shows as the visible mark ` ⏎ ` and each other CR LF as ` ↵ `. The door does not depend on the brief's `repr`.
4. **F4, taken. Every run that does not time out is recorded.** "Completes" means "ended before the timeout". The row holds the return code, the stdout bytes and the last 1,500 characters of the stderr. A timeout is recorded with `timed_out = 1` and no output. The line reads the last row (RC).
5. **F5, taken. Refusals 2 and 4 are restated.** Refusal 2 counts definitions and assignment targets only: a `def`, a `class`, an `=` or a `lambda` bound to a name that a source file of the touch defines. A name bound by an import is exempt, so A1 to A3 pass and A4 is refused (observed: the review's probe `rev360/refusals.py`). Refusal 4 asks for a call of a name that the program imports from a touch module, so `import icalendar` with no such call is refused. **The renamed copy.** A program that imports `_foldline`, calls it once, and prints the result of its own `def fold` passes every text check. No check of the text can tell which call made the printout (reasoned). The door records the touch names that the program imported and called in the row's `imported`. His line does not show them, because it holds no identifiers, and "Ask me to show the program" reaches them. The honest statement: the door stops A4's act and a renamed copy with no call of the touch. It does not stop a copy beside a real call.
6. **F6, taken. The wiring is in the reach and the price.** The probe patched four things (observed: `probe_architect_claim.py` 125 to 159):
   - `runner._wake_allow`, the tools of the wake. `tick:claim` must map to `architect/claim.tools` (`rota/core/runner.py` 442).
   - `runner.DETAIL_SHOWN`, the wake kinds whose detail the seat reads (`rota/core/runner.py` 288). Without `tick:claim` in the set, the seat does not see the request or the touch.
   - The graph, `rota/design/graph.py`: an edge `architect -> code`, reads, `run`, and the table node `claim_runs` with its one writer.
   - `TICK_WORDS`, `rota/roles/principal.py` 2539: `"claim": "the team could not run the code"`, so a stuck claim tick does not read "the team could not finish a step".
   Price: one more cycle, in RD.
7. **F7, taken. The claim rate since the claim door.** The claim mark landed at 657cf1a81, 2026-11-02 17:32 (observed: `git log`). Since then, 2 batches merged on the records: dry run 3's `bg_1`, a change, and the arm's run 1, the claim (observed: `plans/dry3-wall1-read-2026-11-02.md`; the arm read). Dry runs 4, 5, 6, 6b, 6c and 7 merged no batch (observed: each read's Result). So the rate since the door is 1 claim of 2 merges, and 1 of 1 claims is false. The 1 of 19 is a rate from before the door, because the claim branch did not exist on the nights (reasoned). The nights after 2026-11-02 are not checked.
8. **F8, taken. The opt-in form is option 3.** `merge_gate=review` holds a claimed batch today, and no page shows the hold (observed: `rota/core/lifecycle.py` 1241, its one reader). His 14:19 ruling names that setting, so a claim that waits only when he switches the setting on departs from no ruling (reasoned). H2-opt: a hold page for a claimed batch under `merge_gate=review`, with the printout of RC and "Reply 'ok' to accept. Say what is wrong if it is not done." Price: the page form 2, the land of "ok" and of his words 2, one review 1, the gate 1, so about 6 cycles over H1 (reasoned: the anchors). A merge page for change batches under the same setting is not in it.
9. **F9, taken. The story keeps to the counts.** RE says "ran a program four times, three of them on the project's own code" and "in all four reports it marked the claim as holding". Option 2 and option 3 say what happens after his "no": his words go to the builder and the tester, and the job goes back to them.
10. **F10, taken. The reach is 14 places.** Row 13 of H7 holds two places, `_built_words` and `tests_missing.md` 27 (observed: the review). With the four places of F6, H1 touches 18.
11. **F11, taken. The line's words.** "ran the code on one example" becomes "ran one program". "The only other evidence" becomes "The only evidence" when no run is on record. RC gives the line.
12. **F12, taken. The predicate keys the wake by batch.** The wake fires for a claimed batch with no `claim_runs` row and no ended `tick:claim` session for that batch. `boot.py` 167 to 179 moves the head, and the key by batch survives the move (reasoned).
13. **F13, taken. The door puts the tree back.** After each run the door reads `git status --porcelain` of the worktree. A change is put back with `git checkout -- .` and `git clean -fd` on the changed paths only, and the row records `wrote_tree = 1` with the paths. Measure 3 then runs for A4's first program, which aimed at `src/icalendar/parser/string.py`, as well as for A1.
14. **F14, taken. The 08:20 reading is deferred, not withdrawn.** The status of 09:29 says "Roman rules its gate after the page". So H1 departs from the session's 08:20 reading that the fact gates, and that question is his (observed: `plans/stack.md`, frame 360, 09:29).

No finding is left untaken.

#### RB. The result, restated

- **Recommend H1 with the reach of H7, the wiring of F6 and the door fact of H8.** The Architect runs one program on a claim. The door records the exact printout. The fact gates nothing.
- **Departure: H1 meets his ruling of 2026-11-06 14:19 in form only.** "Verified by another seat" stays the Critic's pass, and that pass cannot verify a claim (RA item 2). It also leaves open the session's 08:20 reading that the fact gates, which he rules (RA item 14).
- **The limit:** a false claim closes even when the printout shows the fault, unless a test goes red. He reads the printout after the merge (RA item 1).
- **Options 2 and 3:** the default wait, which departs from ruling 2 of 2026-09-12, and the opt-in wait under the review setting, which departs from no ruling (RA item 8).

#### RC. The line, in every state

The line joins `claimed_lines`, in frame 358's form, one sentence and nothing asked. The first two sentences stay: "<request>: no code changed. The team says the code already does this." The third sentence reads the last `claim_runs` row of the batch:

| State of the last row | Third sentence |
|---|---|
| Return code 0 and a printout | "The architect ran one program on the code, and it printed: <the text, with ⏎ for each fold, first 600 characters>." |
| Return code 0 and no printout | "The architect ran one program on the code, and it printed nothing." |
| Return code not 0 | "The architect ran one program on the code, and it stopped with an error: <the last line of the stderr>." |
| Timed out | "The architect ran one program on the code, and it did not finish in <n> seconds." |
| No row | "No run of the code is on record." |

Then, with a row: "The only other evidence is <n> tests that the team wrote, and they pass on the code as it was." With no row: "The only evidence is <n> tests ...". Then "The reviewer passed them." when a pass is at the head, and "Ask me to show the program and the tests." Each sentence states a fact of a row, so it is true for a true claim, for a false claim and for no run (reasoned). A1's first run, the `AssertionError` inside `_foldline` on a line that holds a line feed, is a fact about the code, and the line shows it if it is the last run.

#### RD. The price, restated

**About 10 cycles for H1.** The door with exact bytes, the tree check and the table, 3. The predicate keyed by batch and the wiring of F6, 1. The mode, the tools and a register case, 2. The readers of H7, the line of RC and the door fact of H8, 2. One review, 1. The gate, 1 (reasoned: the anchors of section 3). Option 2 adds about 5 to 6. Option 3 adds about 6, with its hold page (RA item 8).

#### RE. The question for the principal, in plain words

This replaces H10.

> **On 6 November you ruled that a job with no code change can close "as long as it is verified by another seat", unless the review setting is on. Option 1 below meets that ruling in form only: a reviewer still passes the job, and the trial shows that the reviewer cannot tell a true "already done" from a false one. Option 2 departs from your ruling of 12 September that nothing waits on a page after the first one. Option 3 departs from no ruling.**
>
> How it came to be: you asked the team, "Fold long lines so that no word splits." The builder said "already done" and changed nothing. A tester wrote three checks, and all three passed on the old code. A reviewer passed them, and the job closed. In truth the code still splits words. On a replay, five reviewers looked at the same job, and none of them said it was false. You then said, "try the planner", the team member who knows where each job lives in the code.
>
> On a trial the planner ran a program four times, three of them on the project's own code. In two of those three runs the printout showed "splitting wo" and "rds" on two lines, so the code splits words. In all four reports the planner marked the claim as holding.
>
> What happens today: the job closes by itself. Your screen says that no code changed and that three checks pass on the old code. No run of the code is shown.
>
> Option 1, recommended, the printout goes on your screen: the planner runs the code, and the system keeps what the run printed, never the planner's words. The tester sees the printout before it writes its checks. If a check then fails, the builder must change the code. If no check fails, the job closes by itself, and your screen shows the printout the same day. Its limit: a false "already done" closes even when the printout shows the fault, and you read it after the job closed. Then you say so, and the team opens a new job on top.
>
> Option 2, every such job waits for you: as option 1, and the job does not close until you read the printout and say "ok". Other jobs go on while it waits. If you say "no", your words go to the builder and the tester, and the job goes back to them. If you never answer, it waits for ever.
>
> Option 3, such a job waits only when you switch on the review setting: as option 1 when the setting is off. When it is on, you get a page with the printout, and the job waits for your "ok". A "no" goes back to the builder and the tester, as in option 2. The setting exists today, but no page shows you a job that waits on it.
>
> One exact analogy: a builder says the wall already stands. A surveyor takes a photo of it. The file keeps the photo, not the surveyor's caption. In option 1 the owner sees the photo after the wall is signed off. In option 2 the owner sees every photo before anyone signs. In option 3 the owner sees the photo before anyone signs, on the days the owner asked to.
>
> Recommended: option 1, with its departure named: your ruling of 6 November is met in form only. If a job closes on a printout that shows the job undone on the next three trial runs, I ask you again about option 3.

#### RF. Doubt, added

- The rate since the claim door is 1 claim in 2 merges. Two merges are no rate (observed: RA item 7).
- The exact-bytes capture and the fold mark are a design from the review's probe on one machine, Windows. Not run on the door (reasoned).
- The tree check puts back what a program wrote. A program that writes outside the worktree is not covered (reasoned).
