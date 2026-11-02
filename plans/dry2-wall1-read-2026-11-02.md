# dry2 wall 1 read: the second half of the sentence restates the code, and its item cannot start (2026-11-02)

Reader: an agent of session 208997ee, read-only at eaeec359 on `rota/foundation`. The copies are `dry2w2` (before turn 3) and `dry2w3` (after turn 3), both in the scratchpad of 208997ee. The reader did not open the live dry2 database or `C:/Users/roman/rota_dry2/`. The probes are in `.../208997ee-.../scratchpad/w10read/`.

## Result

1. The hypothesis holds: the criteria of `tk_2` pass on the code with no change, and no seat, door or page has a state for "this item is already true", so the only exit the code gives is a failed start (observed: 16 of 16 probe tests pass at ff1f65f and at the walk base 99101f1; s63 to s65).
2. The system saw the fact four times and dropped it each time: the Critic's verdict `stands` on the request item at s40, three Developers that said "already satisfies the criteria", and the commit door's own note "If the criteria are already met, say so in your reply and end the session", which the stall predicate then counts as a failed start (observed: `challenges`, turns of s63 to s65, `api.py` 24043, `scheduler.py` 509 to 549).
3. No open or parked frame covers turn 3, and the stopped page m34 is correct under frame 330's rule but wrong in meaning, because it says "The team gave up" on a change that the code already holds (observed: the stack headings, the render of m34, `quiet_park` on the copy).
4. The second item comes from the Vision Keeper's deliver brief, "One item per distinct thing the software must do" (2026-08-09, 9a109336), and its premise "The statement is a new behaviour" (2026-09-09, f4b29e57), so by design the guard clause is a request and not a constraint on the first item (observed: `deliver.md`, git log).
5. The reach is 11 places in the code that assume an approved item means a code change, and on the nights it is 1 batch of 51, dry2's `b_2` only, because the night asks are all new behaviours (observed: `nights.py`, `nights2.py`; reasoned: section 5).
6. The smallest fix is one write at the empty-commit branch of `code.commit`: the batch takes its fork commit as its head when the Developer says the criteria are met, so the Tester, the harness and the merge prove the claim with tests and no code change, at about 5 to 6 cycles; it changes a door's result, a prompt note and the page the seat reads, so it needs a design page and Roman's ruling (reasoned: section 6).

## 1. Find

The statement and the items (observed: `statements`, `items`, `item_provenance`, `refs`, `ruled_refs` in dry2w3):

- `s1`, `ratified`: "Make tip_calculator.calculate_tip() raise ValueError when the tip percentage is below 0 or above 100, and return the tip as before otherwise."
- `raises_value_error_for_invalid_tip_percentage`: "The program raises ValueError when the tip percentage is below 0 or above 100." Provenance `decided`, basis `statement`, ref `statement` to `s1`, approved by r_m18 ("ok") on line 1.
- `returns_tip_as_before`: "The program returns the tip amount as before when the tip percentage is valid." Provenance `decided`, basis `statement`, ref to `s1`, approved by r_m18 on line 3.
- The signoff page m16 put `returns_tip_as_before` under "You asked:" and the ValueError item under "It would:" (observed: `probe_pages.py dry2w3 m16`). This is a side finding: the page shows the guard clause as the request.

Tickets and criteria (observed: `tickets`, `criteria`):

- `tk_1`: "the program raises a ValueError when the tip percentage is invalid". Criteria `c_1`, `c_2`, `c_3`. `c_2` already says: "When the tip percentage is valid (between 0 and 100 inclusive), the program returns the calculated tip amount without raising an exception."
- `tk_2`: "the program returns the tip amount as before when the tip percentage is valid". Criteria `c_5` "When input_tip_percentage returns a valid percentage (>= 0 and <= 100), calculate_tip must return the tip amount derived from that percentage." and `c_10` "When input_tip_percentage returns a valid percentage, the program must not raise any exceptions or errors." s48 wrote 15 `criteria.specify` calls to get these two (observed: tool_calls of s48).

The steps of turn 3 on `b_2`. The dry2w2 copy ends at s41, and dry2w3 ends at s76, so the copy holds 35 committed sessions for turn 3, not 40 (observed: `sessions`). The merge of `b_1` is s62.

| Step | Session | What happened |
|---|---|---|
| Critic on the item (turn 2) | s40 | `challenge.uphold` on `items:returns_tip_as_before`, verdict `stands`, quote `def calculate_tip(total, tip_percentage):\n    return total * (tip_percentage / 100)`. On the ValueError item, s41 wrote `falsified`. No reader acts on `stands` (observed: `challenges`). |
| Slicing | s46 | `tickets.slice(id='tk_2', item_id='returns_tip_as_before', ...)` (observed). |
| Criteria | s48 | `c_5`, `c_10` and later twins. The ledger row `l_7692360989`: "c_5, c_10, and c_13 are the final criteria for tk_2" (observed). |
| Grouping, annotate, touch note | s49, s52, s54 | `b_2` on `tk_2` alone. Touch note "expected 3, possible 5" (observed). |
| `b_1` merges | s55 to s62 | Developer, Tester, two red attempts, Critic, Architect. ff1f65f on tipsI 14:00:20 (observed: git). |
| Start 1 | s63 | Read `tip_calculator.py`, `main.py`, `tests/test_calculate_tip.py`. Wrote 4 test files, all refused: "tests/test_calculate_tip.py is a test file, and the tests are the Tester's". `code.commit` committed nothing. Reply: "The implementation in `tip_calculator.py` already satisfies the criteria ... no changes are needed." (observed: turns, tool_calls) |
| Start 2 | s64 | Wake "attempt 2 of 3: the last session ended with nothing written and nothing committed". Wrote `main.py` with its own text. The door answered: "main.py already holds this text, so this write changed nothing. Commit ff1f65ff holds it." Then `code.commit` gave "committed: False, why: nothing changed" and the note "If the criteria are already met, say so in your reply and end the session, with no message to anybody". The seat did that: "The codebase is exactly as it should be. The session ends here with nothing owed." (observed) |
| Start 3 | s65 | Same reads, `ledger.log` `l_b81ccdff1f`, wrote `main.py` and `tip_calculator.py` with the same text, a test write refused, commit of nothing (observed). |
| Quarantine | runner | `developer\|tick:batch_start\|b_2` attempts 3, quarantined 1, reported 1. `b_2` stays `running`, `head_commit` NULL (observed: `tick_attempts`, `batches`). |
| Rung 1 | s66 | `tick:exhausted`, detail "the change could not start after 3 attempts". `tests.load` showed no test for `c_5` or `c_10`. `ledger.log` kind `blocked`: "Tests for c_5 and c_10 exist but content is not ...". `msg.escalate_architect(refs=['c_5','c_10'])` as m28 (observed). |
| Escalation | s67 | Architect: `msg.challenge_vision_keeper` m29, decision `d_1` "The criteria c_5 and c_10 are valid and correctly formulated ... No further action is required.", answer m30 (observed). |
| Challenge | s68 | Vision Keeper: `d_12` with the same words, five times, then repeats refused (observed). |
| Answer | s69 | Developer: loads only. "The criteria c_5 and c_10 are valid and correctly formulated; no code changes or ledger entries are required." (observed) |
| Rung 2 | s70 | Architect `tick:exhausted`: `msg.report_liaison(refs=["b_2"])` as m31 (observed). |
| Report | s71 | Liaison: reads, no message (observed). |
| Rung 3 | s72 | Vision Keeper `tick:exhausted`: "Since the item is already approved and in scope, the next step is to consult the principal". `msg.report_liaison(refs=["b_2","tk_2"])` as m32 (observed). |
| Clarify | s73 | m33, rendered: "The requirement (s1) specifies returning the tip "as before" for valid percentages. Does "as before" refer to the original calculation logic (tip = total * percentage) or a specific previous behavior that deviates from that standard calculation?" Footer "Reply in a sentence. I take it from there." (observed: `probe_pages.py`) |
| Stopped page | s74 | `tick:quarantined`, detail "1 abandoned: batch_start for b_2 (developer), 3 attempts". m34, rendered: "The team stopped work on this change." Line 1 the item, lines 2 and 3 the criteria with "check: none yet.", "The team gave up: the change could not start after 3 attempts.", line 4 the touch, footer "Reply 'ok' if every line says what you want. Name a line to correct only that line. Ask, if something here is unclear. To change what you asked for, name line 1." (observed) |
| Re-survey | s75, s76 | Terminologist and Architect `tick:survey` on "." (observed). |

`b_1` in brief. ff1f65f merges 51231b6 ("rota: tests of b_1") onto 99101f1, with the Developer's e40742e (observed: git). The diff adds the guard `if tip_percentage < 0 or tip_percentage > 100: raise ValueError("Tip percentage must be between 0 and 100.")` to `calculate_tip` in both `main.py` and `tip_calculator.py`, and three test files of 9 to 14 lines (observed: `git diff 99101f1 ff1f65f`). A careful person can read it in a minute (reasoned: 2 lines of code per file and plain tests). The noise is small: `tip_calculator.py` loses its last newline, `test_calculate_tip_c_1.py` has `assert True` after each `with` block, and `test_calculate_tip_c_3.py` imports `builtins` and does not use it (observed). The tests import `main.calculate_tip`, while his sentence names `tip_calculator.calculate_tip` (observed). The guard is in both files, so his function has it (observed).

## 2. Match by symptom

- **Frame 330, closed today.** The page m34 is not the park page of conditions 4 to 7. It is the Liaison's quarantine note at s74 (observed: the wake of s74). The park had not fired at the copy's end: on dry2w3, `quiet_park` returns `do:park(b_2: the change could not start after 3 attempts, and its ladder is spent)`, but `frontier_readonly` still holds six Critic `tick:challenge` wakes from the re-survey, so the quiet has not come (observed: `park.py`, `fr.py`). Under frame 330 the page is right: the ladder is spent and the page says so. The rule has no case for a batch with nothing to do, so the page tells him the team failed at work that the code already holds (reasoned). The later park page will offer "try again" and "drop" (observed: `gave_up_lines`, principal.py 3040 to 3047). A restart buys three more empty starts (reasoned: nothing in the start changes).
- **Frame 357.** A drop on line 1 of m34 lands `dropped` on a request item, and `cancel` then abandons `b_2` (observed: `_item_drops` principal.py 3914, the write at 3744 to 3758, `cancel` predicates.py 1696). The mechanism ends the stall. The record then says that he withdrew "return the tip as before", which he did not (reasoned).
- **Frame 358.** s75 and s76 are its re-survey. The re-survey is not the stall (reasoned).
- **Frame 306.** Its open evidence half, "a change ... merges with no page that shows it", is near the proposal of section 6 and not the stall (reasoned).
- **Frames 315, 322, 264, 276, 253.** A re-slice after a contest, the criteria wake text, account rows on a request page, a quarantine page for a contested item, a tick key on a page. None names an item with nothing to write (observed: the headings).

No frame covers turn 3. No closed frame, ruling or decision names an approved item that the code already satisfies (observed: grep of `plans/stack.md`, `plans/archive/`, `rota/DECISIONS.md`, `plans/composition.md` for "already true", "already satisf", "nothing to build", "empty diff").

## 3. The purpose and the provenance

- The statement stays whole by law L1: "one thing they asked for is one statement ... Downstream roles re-decompose into their own artefacts" (observed: `rota/LAWS.md` 224 to 227, 27f02dc5, 2026-08-09).
- The Vision Keeper split it by `deliver.md`: "One item per distinct thing the software must do" (observed: 9a109336, 2026-08-09, the prompt layer). The paragraph "If `how_it_works` is already on file ... The statement is a new behaviour. Assert it as its own item ... one `problem.assert` per distinct thing" came at f4b29e57, 2026-09-09, from tipsL and tipsM, by the build workflow and not by a ruling of Roman (observed: the commit body). By this design, "and return the tip as before otherwise" is a thing the software must do, so it is a request item (reasoned).
- In meaning, the clause is a constraint on the first item. The Terminologist wrote it as `c_2` of `tk_1`, the Tester encoded it as `tst_tip_valid`, and it was green at the merge (observed: `criteria`, `tests`).
- One item gets one batch by the identity law (observed: `rota/DECISIONS.md` 838, "one item's open work is one batch", 2026-08-28).
- The slicing cannot set the item aside. `problem.describe` refuses a decided item: "is the principal's own words, so it asks for something" (observed: api.py 2445 to 2449, 74c43005, 2026-09-24, frame 80).
- The Tester waits for a commit: "The Tester now waits for `head_commit` ... `batch_start` needs no tests, so nothing deadlocks" (observed: predicates.py 910 to 924, 01e48a6f, 2026-09-08). The premise fails for an item with nothing to write (reasoned).
- A start with no commit counts as a failed start: "A running batch with no commit is a start that did not land ... The start is owed until a commit exists" (observed: scheduler.py 509 to 525, 75e732fd, 2026-09-10, from tipsAI). The attempt count came at a5be4e57, 2026-09-15, and the detail at frame 297.
- The commit door's note offers an end that no state records: "If the criteria are already met, say so in your reply and end the session" (observed: api.py 24043 to 24047; first at 858d7634, 2026-08-26, reworded on 2026-09-19 by the comment, and 2e6afd1c, 2026-10-11). The seat followed the note in s64, and the predicate then counted the session as a failed start (observed).

## 4. What a careful person meant, and what the code offered

He meant one change with a guard on its edge (reasoned: his words). The sentence "Make tip_calculator.calculate_tip() raise ValueError when the tip percentage is below 0 or above 100." would likely make one item, by s34's pattern of one `problem.assert` per clause (reasoned, not measured). A careful person should not carry that burden. The clause is the precise part of his sentence, and a workflow that punishes precision fails the destination "a careful person runs rota alone" (reasoned: `plans/composition.md`).

On turn 3 the pages offered these acts (observed: the renders):

- m33: one sentence about the meaning of "as before". An answer such as "the current formula" goes back to the Vision Keeper, which has no act that ends a satisfied item (reasoned: `vision_keeper/exhausted.md` offers `problem.assert` or `msg.report_liaison` for a decided item).
- m34: "ok" approves four lines that are already approved, a correction of a line, a question, or line 1 to change the request.
- The later park page: "try again" or "drop".

A drop is a working exit but the wrong end. It records a withdrawal of a requirement that he holds and that is true (reasoned). The structure needs a state for an item that the code already satisfies, with evidence. The evidence exists today:

- `tst_tip_valid` asserts `calculate_tip(total=100, tip_percentage=0) == 0.0`, `100` gives `100.0`, `50` gives `50.0`, and passed at the merge of `b_1` (observed: `tests`).
- A probe of `c_5` and `c_10` on both `main.calculate_tip` and `tip_calculator.calculate_tip`: 16 of 16 pass at ff1f65f, and 16 of 16 pass at the walk base 99101f1, before any change (observed: `w10read/tips_ff1f65f`, `w10read/tips_99101f1`).

## 5. The reach

The places where an item that the code already satisfies stalls the same way (observed: the files and lines; the count is reasoned):

1. `vision_keeper/deliver.md`: one item per distinct thing, and every statement on an existing account is "a new behaviour".
2. `challenge_subjects`, scheduler.py 1428 to 1458: the Critic checks request items too, and a `stands` verdict on a decided item is recorded and read by nobody.
3. `problem_describe`, api.py 2445: a decided item cannot be set aside as a description.
4. `terminologist/criteria.md` 19 to 22: an existing callable is the surface "only when the item asks for what that callable already does", and no check follows.
5. `tests_missing`, predicates.py 910: the Tester waits for `head_commit`.
6. `harness`, predicates.py 971: no run without `head_commit`.
7. `tick_batch_start`, scheduler.py 509 to 549: no commit is a failed start.
8. `code.commit`, api.py 24043: the note "say so ... and end the session", with no state behind it.
9. `mergeable`, lifecycle.py 862: "nothing committed".
10. The ladder: no rung's tools hold an act for "already met" (`developer/exhausted.tools`, `architect/exhausted.md`, `vision_keeper/exhausted.md`).
11. The stopped page, principal.py 3062 to 3070: "The team stopped work" and "The team gave up".

The count on the records (observed: `nights.py` and `nights2.py`, read-only):

- Nights 160 to 175 and 164a: 48 batches, 0 with a quarantined `batch_start` key.
- dry1 (copy dry1w11): 1 batch, 0.
- dry2: 2 batches, 1, `b_2`.
- Two night batches had many empty starts with no head: night 163 `bg_2` (17 of 18) and night 169 `batch_1` (10 of 11). Their cause is writes that a door refused or discarded, the note at line 609 and frame 339's removal door, not a satisfied item (observed: `plans/night163-read.md` lines 33 to 41; frame 330's status of 2026-10-26 20:47).
- Developer replies with "already satisfies" or "no changes needed" occur on 22 night batches, mostly in fix modes, and the reader did not verify them (observed: `nights2.py`; reasoned: model claims are not evidence).

The night asks are new behaviours from the lineage, so the shape is rare there (reasoned). A careful person writes guard clauses, and a re-ask of merged work or a restart after a merge meets the same 11 places (reasoned).

## 6. The proposal

**At the empty-commit branch of `code.commit`** (api.py about 24020 to 24047): when the tree is unchanged, the batch has no head, and the session sent no challenge or escalation, take the claim "the criteria are already met" as an act. The door writes the worktree's HEAD, the fork commit, as `head_commit`, with a mark that the head is a claim and not a change. Then the readers that exist do the rest:

1. `tests_missing` wakes the Tester, who encodes `c_5` and `c_10`.
2. `harness` runs them at the fork commit.
3. Green goes to the Critic, the Architect and the merge. The merge carries the tests commit only.
4. Red goes to `tests_failing`, the normal fix loop with real tests, so a false claim costs one Tester session and one run.

The stall predicate, the quarantine, the ladder and the stopped page then never fire for this case (reasoned: places 5 to 11 read `head_commit`). The page before the merge must say "No code changed. These tests show the code already does this." That is the evidence half of frame 306 (reasoned).

Price: 5 to 6 cycles (reasoned: a door write with a red test from the dry2w3 copy, 2 to 3 cycles; the page line, 2 cycles; one review; by `plans/operating-facts.md` line 250).

It leaves out these things (reasoned):

- The slicing still makes the second item, so the seat still reads two items on m16. The cost falls from about 12 sessions and two dead pages to one Tester session and one run.
- The Critic's `stands` on a request item stays unread. It could later put "the code already does this" on the signoff page, before any batch.
- The duplicate of `tk_1`'s `c_2` and `tk_2` goes undetected.
- The deliver brief's premise "The statement is a new behaviour" stays.

It changes a door's result (`code.commit` on an unchanged tree), the Developer's note, a prompt's shape, and the page the seat reads. It also changes what "delivered" means: a merge with tests and no code change. So it needs a design page and Roman's ruling (reasoned: the rule that a seat's form, a prompt's shape or a door family needs one).

Doubt:

- A small model may claim "met" to escape work. The tests gate the claim, but tests written against an existing callable can be weak. `tst_tip_valid` first expected `50.0` for 100 percent (observed: decision `d_5493228983`).
- The reader did not probe whether `lifecycle.merge` takes a branch whose only new commit is the tests commit. ff1f65f suggests that it does, but the reader did not measure it.
- A fix at the source of this instance is in the Vision Keeper: keep a guard clause as a criterion of the first item. That covers one of the three ways in (the clause), and not a re-ask or a restart (reasoned).
- The reach on the nights is 1 of 51 batches, so the price buys the careful person's way of writing and is not supported by the night counts (reasoned).

## Probes

All in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/208997ee-71a2-496f-83aa-e1425ff49524/scratchpad/w10read/`, read-only on the copies:

- `q.py`: rows of any table.
- `t2.py`: the tool calls and the completions per session.
- `t3.py`: the tool results in the next turn's user text.
- `probe_pages.py`: the render of m16, m25, m33 and m34 through `principal.render_page`.
- `park.py`: `stopped_bouncing`, `parked`, `_next_rung`, `spent_park`, `quiet_park` and `stop_detail` on `b_2`.
- `fr.py`: `frontier_readonly` on dry2w3.
- `nights.py`, `nights2.py`, `n163.py`: the counts over nights 160 to 175, 164a, the dry1w11 copy and dry2w3.
- `tips_ff1f65f/`, `tips_99101f1/`: the tipsI files from git, and `tests/test_tk2_probe.py` for `c_5` and `c_10`, run with pytest in the scratchpad.

## Usage

About 198k tokens by the harness counter, against the cap of about 100k (observed: the counter at start and at end). Most of the excess was the session and tool-call dumps of the ladder.
