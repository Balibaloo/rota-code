# Frame 322: the read of the red case `L1-TE-a-docstring-ticket-gets-a-docstring-criterion`

Date: 2026-10-26 07:46 (from `date`). Repository head: 523f5666. The gate
tree: `C:/Users/roman/rota_g328` at 4bb2656b. Read-only, no model call, no
pytest.

Sources:

- The gate output: `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/4cdad7e1-c78d-472d-86ab-f4c72d52763e/scratchpad/gate_4bb2656b.txt`, lines 62 to 70.
- The register: `C:/Users/roman/rota_g328/tests/rota/cassettes.db`, opened
  with `?mode=ro`. Table `case_runs`, the live rows seq 566798 to 566802
  (at 2026-10-26T07:36:22, prompt hash 4427426eec78b96b). Table
  `cassettes`, three rows per run, found by the run's ticket id.
- The case: `tests/rota/cases/l1_terminologist_docs.yaml` in the gate tree.
- The door: `rota/roles/api.py` 5840 to 5875 in the gate tree,
  `_docs_ticket_refusal`.
- The session end: `rota/core/runner.py` 6075 to 6090 in the gate tree.
- The pass report: `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/ad481e08-d0cc-4317-a992-02d5208ea7e8/scratchpad/f322_pass2.md`.
- `plans/frame322-we-read.md` 160 to 172, `plans/frame322-review-2.md` line 11.

## The result

**The red is the door's refusal text: on 5 of 5 runs the seat sent a
behaviour criterion, the door refused it correctly, and the seat then
obeyed the refusal's last instruction, `msg.challenge_vision_keeper`,
which ends the session before any retry (observed: `case_runs` seq 566798
to 566802, each `wrote: {}` and `sent: [["vision_keeper", "challenge"]]`).**

The model's first reading is a second cause, because the criteria brief
holds no line for a documentation ticket (observed: the system text of
cassette 67860b5f). The door catches that first reading as designed. The
case fails because the refusal gives the seat an exit and no second try
(reasoned: the runner ends a session once a message is sent).

## 1. The five runs

Each run has three model turns and six calls that the runner made before
the first turn (observed: three `cassettes` rows per ticket id, and the
"Already run for you" block of each first prompt). The six pre-run calls
are `code.callables`, `glossary.consult`, `glossary.lookup`,
`tickets.scan` twice and `code.callables` again. The seat did not make
them.

The turns have the same shape in all five runs (observed: the transcripts):

1. Turn 1: `criteria.specify` with a behaviour text. The door refuses.
2. Turn 2: `msg.challenge_vision_keeper(refs=[<ticket>], quotes=[<headline>], round_no=0)`.
   The tool returns OK. The runner adds "You have sent your message. Your
   work for this session is complete — emit no further tool calls."
3. Turn 3: no call. Runs 1, 2, 4 and 5 say only `</think>` three times.
   Run 3 says prose: "The documentation must reflect this calculation
   logic ... the Vision Keeper should slice the work accordingly."

The criterion texts of turn 1 (observed: `case_runs.transcript`):

| Run | Text | surface_refs |
|---|---|---|
| 1 | "The line total must calculate the price of ten units of a 100-cent product as 950 cents" | `line_total` |
| 2 | the same as run 1 | `line_total` |
| 3 | "The line total must calculate the price of one order line after the volume band." | `total_of` |
| 4 | the same as run 1 | `total_of` |
| 5 | "The line total of ten units of a 100-cent product must equal 950 cents" | `total_of` |

Counts over the five runs (observed: the same rows):

- Model turns: 15.
- Calls to `criteria.specify`: 5, one per run. Landed: 0.
- Refusals by door: the documentation door 5. Any other door 0.
- Calls to `msg.challenge_vision_keeper`: 5.
- Turns with no call: 5, the last turn of each run.

A side finding: `line_total` is not in the 20 rows of `[code.callables]`
that the prompt shows. The runner cut 39 of 59 rows (observed: the
`errors` line "cut the candidate symbols: 39 of 59 rows not shown", and
the shown rows hold no `src/catalog/pricing.py` row). Runs 3 to 5 named
`total_of`, which is the wrong callable (reasoned: the headline names
`line_total`, and the brief says that a name in the item's own words is
the surface). The case does not check the surface, so this finding does
not cause the red (observed: the case's `expect` block).

## 2. The refusal

The door refused a behaviour criterion and did not misread it (reasoned:
no text of the five holds "docstring", "documentation", "document", "docs"
or "help text", so `_asks_for` returns False, and the headline holds
"docstring" as a whole word). The refusal in full, run 1:

```
criteria.specify: tk_4af07e's headline is 'the example in the docstring of line_total shows that ten units of a 100-cent product total 950 cents'. The headline names the documentation, and this criterion names no documentation. Write the criterion on the documentation: say what the docstring, the docs or the help text must say. If the item also needs a code change, that is the Vision Keeper's to slice: send msg.challenge_vision_keeper with the ticket
```

The refusal ends with a second route, and its last instruction is "send
msg.challenge_vision_keeper with the ticket". The seat obeyed that last
instruction on 5 of 5 runs (observed: turn 2 of each run). The item needs
no code change. `line_total` on a 100-cent product and a quantity of ten
already returns 950 through the 5% band (observed:
`rota/testkit/samplerepo.py` 508 and 518 to 523 in the gate tree). So the
challenge is wrong, and the seat sent it because the text offered it
(reasoned).

The route clause is the session's own choice and not a ruling of Roman's
(observed: `plans/frame322-we-read.md` 168 to 172 marks it "reasoned").
Review 2 confirmed the clause as true and did not test whether a seat
takes it (observed: `plans/frame322-review-2.md` line 11).

## 3. No `criteria.specify` at all

This question does not apply. Every run sent one `criteria.specify`
(observed: question 1). The wake does not point the seat away from the
docstring. The wake gives the headline twice, and the headline names the
docstring (observed: the first prompt). The criteria brief points toward
behaviour (reasoned: "Criteria describe what must be *true when it is
done*" and "the callables a test would exercise", with no line on a
documentation ticket; observed: the system text).

## 4. The fixture

The headline holds "docstring" as a whole word (observed: the case file,
and `tickets.scan` in the prompt):

> "the example in the docstring of line_total shows that ten units of a
> 100-cent product total 950 cents"

`_HEADLINE_NAMES_DOCS` is `\b(?:docstrings?|documentation)\b`, and it
matches "docstring" here (observed: the refusal quotes this headline, so
the door read it as a documentation headline).

The item text names the docstring (observed: the case file):

> "Give line_total one example in its docstring: ten units of a 100-cent
> product total 950 cents."

The item text does not reach the seat. The prompt holds the headline only
(observed: the first prompt). The fixture is not the cause (reasoned: the
door fired on it as built).

## 5. The verdict

The red is the door's refusal text, and row seq 566798 shows it: the
route clause gives the seat an exit that ends the session, so a refused
first criterion never becomes a landed second one (observed: `case_runs`
566798, `runner.py` 6085 to 6090). No run reached a second
`criteria.specify`, so the register does not measure whether qwen3:8b
writes a docstring criterion on a retry (observed: question 1). This read
cannot say that qwen3:8b fails the case, and the case keeps its model pin
(reasoned).

## The repair

Remove the route clause from the refusal, so that the rewrite is its last
and only instruction. Name the Vision Keeper route for a mixed ticket in
the criteria brief, where the seat reads it before any refusal. Record the
case again: a seat that writes behaviour on its second turn too shows the
model's limit, and the next step is then a criteria-brief line for a
documentation ticket.
