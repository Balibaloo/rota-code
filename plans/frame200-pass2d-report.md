# Frame 200, pass 2d: the three findings of the review of pass 2c

Worktree `C:/Users/roman/rota_rv200c`, at 8d090e2e with pass 2c staged in
the index. The delta of this pass is the unstaged diff alone. The patch is
`C:\Users\roman\AppData\Local\Temp\claude\d--repos-rota\c81dd240-3837-494d-a148-76820abc8093\scratchpad\f200\pass2d.patch`,
155 lines. No commit, no gate, no model call, no sub-agent.

## (a) What changed

```
 rota/core/db.py               | 37 +++++++++++++++++++++++++++++++++----
 rota/core/sandbox.py          |  6 +++++-
 tests/rota/test_predicates.py | 29 +++++++++++++++++++++++++++++
 tests/rota/test_row_route.py  | 23 +++++++++++++++++++++++
 4 files changed, 90 insertions(+), 5 deletions(-)
```

- `rota/core/db.py:664-684`: the new table `RECEIPT_RULES`, keyed by
  `(from_role, to_role, verb)`, and `_receipt_rule`. The table holds three
  rules: `critic -> developer challenge` is "none", `architect ->
  vision_keeper propose` is "items", and `developer -> architect escalate`
  is "message".
- `rota/core/db.py:692-696`: `_owes_a_reply` reads the "none" rule from the
  table. The critic special case in code is gone.
- `rota/core/db.py:735-747`: `_received` returns False for a "message" edge
  when no reply is caused by the trigger. For a table rule, a write on that
  table is a receipt. Then the default rules run.
- `rota/core/sandbox.py:997-1003`: `mine` keeps only rows of `constraints`,
  `findings` and `decisions`.
- `tests/rota/test_predicates.py`: two tests at the end of the file, after
  the three tests of pass 2c.
- `tests/rota/test_row_route.py`: one test at the end of the file, after
  the pass 2c tests.

## (b) The tests

Each test was red on the pass 2c tree before its fix (observed:
2026-10-11, `3 failed, 107 deselected`).

1. `test_an_item_the_vision_keeper_asserts_answers_the_proposal`, finding
   1, the shape of `r1b.py`. The proposal reads `answered`, and
   `unresolved()` wakes nobody for m9.
2. `test_an_amend_with_no_answer_leaves_the_escalation_owed`, finding 2,
   the shape of `r2.py`. The escalation reads `unresolved`.
3. `test_an_amend_with_a_binding_is_offered_the_constraint_alone`, finding
   3, the shape one of `r5.py`. The offer carries `['k_new']` alone, and the
   doors admit it.

Commands, from the worktree root, after the fixes (observed: 2026-10-11):

```
ROTA_MODEL=qwen3:8b D:/repos/rota/.venv/Scripts/python.exe -m pytest tests/rota/test_predicates.py -n 0 -q -p no:cacheprovider
94 passed in 40.89s
ROTA_MODEL=qwen3:8b D:/repos/rota/.venv/Scripts/python.exe -m pytest tests/rota/test_row_route.py -n 0 -q -p no:cacheprovider
16 passed in 3.04s
```

No gate ran, as the brief says. No casestatus counts. No touched file
holds a CR byte.

## (c) Deviations

1. The "items" rule adds to the default receipts. The rule does not
   replace them. Reason: `vision_keeper/propose.md` names two answers, an
   item or "`decisions.author` refusing it with the reason". A replacing
   rule would mark a refusing decision on a row of the proposal as
   unresolved.
2. The "items" rule checks the table of the write, not the session's
   role. Reason: only the addressee, the Vision Keeper, is woken by the
   trigger, so the session's role is the edge's `to_role` already.
3. The comment on the critic edge moved from the `_owes_a_reply` docstring
   to the table entry. The citation of `developer/challenge.md` stays.

## (d) Open questions

1. The "message" rule for the escalation also drops a decision receipt.
   `_answers_by_message` dropped it already for this edge, so the result
   is the same. `_answers_by_message` still covers any other edge with an
   `answer` edge back. Should the table absorb that rule too, so one place
   holds every edge rule? Recommended: no in this pass, because the graph
   derives it and the table would duplicate the graph.

## (e) Usage

Estimate: about 45k input tokens, about 8k output tokens, about 53k
total. No sub-agent.
