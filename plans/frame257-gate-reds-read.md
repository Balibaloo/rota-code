# The four reds of the gate at 8e22d0fc

Result first. Frame 311 moved no seat. Frame 257 moved one seat:
L1-TE-a-new-behaviour-is-a-new-callable went from 835 of 835 passes to 2 of 5.
The cause is the new brief sentence, not the new specify refusal. The other
three cases fail with the same fault as their baseline.

## Sources

- The gate output `g8e22_gate.txt` in session 0cdcac52's scratchpad.
- A read-only copy of `C:/Users/roman/rota_g301/tests/rota/cassettes.db`, made
  with the sqlite backup call from a `mode=ro` connection. The copy is
  `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/b00cc646-4611-4fd9-8f73-b6b404eeda3a/scratchpad/g8e/db.sqlite`.
- The case YAML in `tests/rota/cases/l1_surface.yaml`, `l1_judgement.yaml`
  and `l3_handoffs.yaml`.
- The diffs of 4db40665, 5d21a737, 8e22d0fc (frame 311) and bab9911b,
  4f69d0a4 (frame 257).

Caution: the new gate in rota_g301 overwrote `.rota-gate.log` (5 KB, a
fresh suite run at 02:30). The re-record log of this gate is gone. All
evidence below comes from the `case_runs` rows.

## The two changes

- Frame 311 adds to `rota/roles/prompts/critic/review.md`: "A docstring or
  comment line is evidence only for a criterion that asks for documentation.
  A criterion with no added line that meets it looks like it fails." The
  lines check in `api.py` admits a docstring line when the criterion text
  holds "docstring" or "documentation".
- Frame 257 adds to `rota/roles/prompts/terminologist/criteria.md`: "Each
  criterion has its own id, and a new text takes a new id." The new refusal
  reads "`<id>` already holds a criterion on `<ticket>`: ... An id you invent
  is yours once. For a new criterion, send criteria.specify with a new id of
  your own." Both commits are ancestors of 8e22d0fc.

## Case 1. L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist

(a) In all five runs the Critic sends `verdicts.claim_encodes(encodes=True)`
and `verdicts.emit(result="pass", lines={c: 'delete("invoices", account_id)'})`.
The door asks "Does that line do what the criterion says, or the opposite?".
The Critic says yes and sends the pass again, and the pass lands. The Critic
never sends `msg.question_terminologist`, and the case expects one question.
(b) The failure path does not touch frame 311. The cited line is a code line,
not a docstring or a comment, and no lines-check refusal appears in the
errors. The only refusals are the "does that line do what the criterion
says" door and "one commit gets one verdict". Frame 257 does not apply to the
Critic. (c) The prompt hash moved from 47f78c38 to 26d3fd0c. The baseline
hash holds 0 passes in 1618 rows. The last baseline set (01:10, seq
552405-552409) shows the same path, run by run, with near-identical text.
Verdict: the same fault the baseline had.

## Case 2. L3-a-challenge-reaches-the-role-that-can-answer-it

(a) In all five runs the Terminologist writes three criteria for "make the
reporting better", with invented terms and invented callables such as
`generate_report`. It ends with "No further action is required" and sends
nothing to the Vision Keeper. The case forbids criteria writes and expects
an item or a decision write. (b) The failure path does not touch frame 257's
refusal. Each run uses a new id per criterion, and the only refusal in the
new runs is "wrote its own tool results" in run 2. No "already holds a
criterion" refusal appears. The new brief sentence changed the id choice. In
the baseline, three runs first used an item id (`i_57949a`) and met the
"already a row of items" refusal. In the new runs, no seat does that. The
outcome is the same. (c) The prompt hash moved from 3d6355ba (0 passes in 795
rows) to fe65642c. The last baseline set (01:00, seq 551702-551706) fails the
same way: criteria written, "terminologist never messaged vision_keeper; sent
nothing". Verdict: the same fault the baseline had.

## Case 3. L3-a-failed-verdict-turns-into-a-fix

Note first: the case pins `model: gemma3:12b`, so its runs are on gemma3:12b,
not qwen3:8b. The database holds 1 of 5 passes at the new hash bfee0df7 (run
3 passed). The gate line says 0 of 5. The likely reason is that the passing
run carries another system hash (6762fbdc against 3d6e183c), and the
casestatus match drops it. I did not confirm this. The case is red at 1 or 0
of 5 alike.

(a) In runs 1, 2, 4 and 5 the Critic sends `verdicts.emit(result="fail")`
first. The door refuses it: "a fail on c_... stands on its test actually
encoding it, and that has not been claimed this session". The Critic then
claims `encodes=False`, although the test `assert invoices_for(a) != []`
encodes the criterion. It sends `msg.challenge_tester`. No fail verdict lands,
so nothing wakes the Developer: "critic committed, but nothing woke developer
for verdict_failed". In run 3 the chain reached the Developer, who wrote and
committed. (b) The failure path does not touch frame 311. The fixture holds
the comment line "# Removes the invoices, which the criterion says must
survive.", but no Critic cites it, and no lines-check refusal appears. The
Critic fails on the `delete("invoices", account_id)` line. The fault is the
encodes claim. (c) The baseline hash 46412f27 read 2 of 5 on every re-record
from 14:11 to 01:01 on 2026-10-23/24. Its last set (seq 551747-551751) fails
runs 1 to 3 on the same encodes-claim path and passes runs 4 and 5 through the
Developer. The new text read 1 of 5. The run that passes moved from runs 4
and 5 to run 3. Verdict: the same fault the baseline had. The count change from
2 to 1 is the model's floor on a changed prompt text, not a new path.

## Case 4. L1-TE-a-new-behaviour-is-a-new-callable

(a) In all five runs the first `criteria.specify` names
`surface_refs=['calculate_tip', 'display_results']`, and the surface door
refuses it: "the item names split_bill, and the index has no such callable: a
new behaviour is a new callable ... Name split_bill as the surface". In the
failing runs 2, 3 and 5 the Terminologist does not send the refused criterion
again. It moves on to `c_002`, `c_003` and then writes `c_004`, "The
split_bill function is called after the total with tip is calculated ...",
with `surface_refs=['calculate_tip', 'split_bill']` (run 5 adds
`display_results`). The door admits `c_004`, because it names `split_bill`.
The written row then carries `calculate_tip`, which the case forbids. In the
passing runs 1 and 4, no admitted criterion names `calculate_tip`.

(b) The new specify refusal of frame 257 never fires. No error in the 15 new
rows holds "already holds a criterion". The prompt text changed. The previous
hash c9422c40 passed 835 of 835 rows, from 2026-10-12 to 01:05 on
2026-10-24, over about 60 model loads. The last of those records ran on load
`qwen3:8b@249000`, the same load as the new record. The only change to the
Terminologist's prompt files between the two records is bab9911b's sentence
"Each criterion has its own id, and a new text takes a new id." (git log of
`rota/roles/prompts/terminologist` at 8e22d0fc). In the baseline, runs 1, 3
and 4 sent the refused criterion again under the same id with
`split_bill` as the surface. In the new runs, only run 4 does that. The
sentence reads as "do not send an id again", and the seat then writes extra
criteria, one of which names the old function. (c) Verdict: moved by frame
257, through the brief sentence, not through the refusal.

A second fault sits under the red. The surface door admits a surface list
that holds the old callable beside the new one. The door refuses only a list
of old callables. That gap existed before frame 257, but the old text never
reached it.

## Verdicts

- L1-CR-a-doubtful-criterion-is-a-question-to-the-terminologist: the same fault the baseline had.
- L3-a-challenge-reaches-the-role-that-can-answer-it: the same fault the baseline had.
- L3-a-failed-verdict-turns-into-a-fix: the same fault the baseline had (gemma3:12b, 2 of 5 to 1 of 5 is the floor).
- L1-TE-a-new-behaviour-is-a-new-callable: moved by frame 257 (the criteria.md sentence).

Recommendation: frame 312 touches only the page and can cherry-pick onto this
head now. Frame 306 changes the criteria tools and `rota/core/sandbox.py`, and
every case on the criteria prompt goes stale with it. So repair the L1-TE red
first, because a re-record after 306 cannot separate 257's effect from 306's.
Two repairs are possible: the brief sentence tells the seat to send a refused
criterion again under its own id, or the surface door refuses an old callable
beside the new one. Choose one of them.
