# Frame 319, review 1 of 3aa6ccba

Verdict: the change stands, with two medium findings and one high finding outside the points. The door makes no false refusal on the landed criteria of nights 160 to 162. The door refuses correct texts that name a wrong exception in a negation, and texts that start with "Exception" or "Warning". An empty `surface_refs` lets s157's c2 land. The old module push of the criteria wake never fires on clickI, and that is the cause of the wall the report leaves open.

## (a) Verdicts on the points

1. The count: confirmed. No landed criterion names an exception that the source at any batch head of its item holds and the door refuses.
2. The identifier: "UsageError" in prose and "must not raise UsageError" refuse. "usage error", "Abort" at a sentence start and "SystemExit" with no surface land. All five follow the frame's rule. The negation refusal is wrong by meaning (finding 1).
3. The reach: confirmed. Neither recorded criteria case can carry a raise block. No other case has `tick: criteria`.
4. The place: the door is the last check before the write, after the twin, near-duplicate and cap-of-six doors. Its refusal names a way forward in words, but it does not use `_offer` (finding 4).
5. The silence: 0 of the 35 criteria rows over the three nights have an empty `surface_refs`. s157's c2 lands with an empty list (finding 2).
6. The diff: the report omits the dead module push (finding 3), the English-word refusals (finding 1) and the ambiguous bare name (finding 5).

## (b) Findings

1. `rota/roles/api.py:5050` (the `missing` test in `_exception_from_a_source`). Medium. CONFIRMED.
   The door reads every capitalised exception name, including one in a negation and an English word that is a builtin.
   The probe refused "confirm() must not raise UsageError" and night 162's final text "must raise Abort ..., not UsageError".
   It also refused "Exception text is not shown ..." and "Warning output stays the same ...".
   Night 161's cr_2, "must not raise UsageError or any other exception", is a correct criterion, and the door refuses it.
   The refusal says "with the exception from one of those", so the seat has no stated way to keep "no exception".
   Fix: add to the refusal that a criterion can drop the name and say "raises no exception", and skip `Exception` and `Warning` when no `raise` or `raises` word is near them.

2. `rota/roles/api.py:5031` (`if not idents or not surface: return`). Medium. CONFIRMED.
   The probe sent s157's c2 with `surface_refs=()`, and it landed with the "no surface named" note.
   A refused seat can therefore land the same wrong text by dropping the surface.
   No landed row of nights 160 to 162 has an empty surface, so the route is not yet measured.
   Fix: with an empty surface, refuse an identifier that his words and the item do not hold and that no project class defines.

3. `rota/core/runner.py:4222` (outside the points). High. CONFIRMED.
   The criteria module push reads `pushed["code.callables"]` before line 4261 replaces it with the hinted list.
   At line 4222 the value is the generic unhinted push, which `code_callables` caps at the first 20 symbols.
   On night 162 the index holds 897 symbols, and `src/click/termui.py::confirm` is at position 225.
   So the module push of `code.source` never fires on clickI. That is the report's open question 3, and it is why s157 saw no body.
   The fixture of the new tests holds 5 symbols, so the tests do not show the defect.
   Fix: compute the hinted `code.callables` before the criteria module push, and add a test with more than 20 symbols.

4. `rota/roles/api.py:5054` (the `raise ValueError` of the door). Low. CONFIRMED.
   The refusal names a way forward in words, as the twin and near-duplicate refusals do.
   It does not use `_offer`, as the id refusals of the same function do.
   Fix: wrap the message in `_offer` with the call and its arguments, the text left for the seat to rewrite.

5. `rota/roles/api.py:4927` (`_callable_source`, `LIMIT 1` on `%::ref`). Low. PLAUSIBLE.
   On night 162, 25 bare names occur in more than one file, and `cli` occurs in 13.
   A bare surface name picks one file with no stated order, so the door can read the wrong source.
   `_vet_surface` may resolve the name first. The probe did not trace that path.
   Fix: make the door silent when a bare name matches more than one grain.

6. `rota/roles/api.py:5047` (the pool). Low. PLAUSIBLE.
   The pool holds the whole source of the surface, with its docstring, comments and `except` clauses.
   An exception that the surface catches or only mentions passes as a raised one.
   Fix: none now. Record the limit in the docstring, because the frame's rule reads where an identifier occurs.

## (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/f1f0bcfa-7b93-4f01-99dc-afb4bf54e8a6/scratchpad/r319/`.

- An inline heredoc probe over `clickI_night160.db` to `clickI_night162.db`, opened with `?mode=ro`. It read every `criteria` row and checked each identifier against his statements, the item text and `confirm` at each batch head of the item and at `2c8cd3a`. Results: 160, cr_1 refused at f770f88d and 2c8cd3a. 161, cr_2 ("must not raise UsageError") refused at 395e2648, 9622b3e5 and 2c8cd3a. 162, c1 and c4 pass. c2 and c5 now hold the respecified text "Abort ..., not UsageError". At 8717098b they pass because the Developer's edit holds `UsageError`, and at 2c8cd3a they refuse. All rows have a non-empty surface.
- `test_r319_probe.py`: the five texts of point 2 and three more on the frame's fixture. It also sent c2 with an empty surface and printed the full refusal.
- `test_r319_push.py`: the criteria wake on the fixture. Both `code.source` and the raise block appear, because the fixture holds 5 symbols.
- `hint_probe.py`: `code_callables` with the real ticket headlines on each night. It returns 40 rows, capped, and `confirm` is among them.
- An inline `python -c` probe: night 162's index holds 897 symbols, and `confirm` is at position 225 of the unhinted order.
- The case scan: only `L1-TE-specify-criteria` and `L1-TE-a-new-behaviour-is-a-new-callable` have `tick: criteria`. Neither has `repo:`, so `project_root` raises inside `_callable_source`, the function gives None, and the block is absent.

## (d) Usage

About 75k input tokens, 14k output tokens, about 89k in total. These numbers are an estimate.

Stands: the door and the block do what the frame asks with no false refusal on the three nights. Before the frame closes, fix finding 3 and add the empty-surface and negation routes of findings 1 and 2.

## Re-check of d84fb350

### (a) Verdicts on the points

1. The cap: fixed. On night 162, `_named_callables` with the real headline returns `src/click/termui.py::confirm` first, out of 897 symbols. The test `test_the_criteria_wake_holds_the_source_of_a_callable_past_twenty` adds 30 rows, and it is red at 3aa6ccba.
2. The empty surface: refused now. The refusal quotes `line 15: raise Abort() from None` and `line 18: raise Abort()`. When the headline names no callable, c2 lands silently with the "no surface named" note.
3. The helper: the push and the raise block read the same list, capped at ten. The door reads the list uncapped, and from one ticket's text, not from the item's headlines and `asked`. No reader takes the first unhinted 20 now.
4. The cases: both recorded criteria cases keep their prompt shape. Their wake refs name `<tk1>`, so the item lookup and `tickets.scan` find nothing, and the hint is empty. No other recorded case changes. The two L3 criteria cases hold no `code_index`.
5. The suite: the new file gives 8 passed. The five named files give 78 passed. Both counts match the report.

### (b) Findings

1. `rota/roles/api.py:5061` (the fallback `surface = _named_callables(...)`). Medium. CONFIRMED.
   With an empty surface, the pool holds the source of every callable the headline names.
   The probe set the headline to name `confirm` and `edit`, and `edit` raises `UsageError`.
   s157's c2 with an empty surface then landed. The same text with `surface_refs=["confirm"]` was refused.
   So a refused seat can still land the wrong exception by dropping the surface, when the headline names a second callable.
   No headline on nights 160 to 162 names two callables, so the route is not measured.
   Fix: with no surface named, refuse when any named callable's source lacks the identifier, not when all of them lack it.

2. `rota/roles/api.py:5061` against `rota/core/runner.py:4215` and `:4085`. Low. CONFIRMED by reading.
   The wake reads `asked` and every headline of the item, capped at ten. The door reads one ticket's text, uncapped.
   The door can quote a callable the wake did not show, or miss one the wake showed.
   Fix: give the door the same hint and the same `[:RAISE_LINES_SHOWN]` cut, or record why they differ.

3. `rota/core/runner.py:4215` (the span loop). Low. PLAUSIBLE.
   `_named_callables` sorts by grain, and the cut takes the first ten. A headline word such as `cli` matches 13 files on night 162.
   The push then reads up to ten files of 400 lines each, where pass 1 read two. A common word can also push the wanted callable past the cut.
   Fix: cap the files at two again, and order the named callables by the headline word that matched first.

### (c) Probes

All probes are under `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/e7141541-fc20-4c5c-a91b-4a10a610ec42/scratchpad/r319b/`.

- `p1.py`: `_named_callables` on the headlines of each criteria item of nights 160 to 162, opened with `?mode=ro`. Each item names one callable. `confirm` is at position 0. No symbol row has a NULL or zero span.
- `old/`: `git archive 3aa6ccba` of `rota` and `tests`, with d84fb350's test file. Result: 2 failed, 6 passed. The import came from the archive.
- `test_p2.py`: the door on the frame's fixture. Empty surface: refused with lines 15 and 18. Headline with no callable: landed. Headline naming `confirm` and `edit`: landed with an empty surface, refused with `confirm`. The wake pushed lines 4 to 22 and two raise-block keys.
- The case scan: `tick: criteria` occurs in `l1_surface.yaml`, `l1_terminologist.yaml` and `l3_handoffs.yaml` only.
- The suite: the new file and the five named files, run from the worktree root.

### (d) Usage

About 45k input tokens, 7k output tokens, about 52k in total. These numbers are an estimate.

Stands: findings 1 and 3 of review 1 are fixed and proved red-then-green. Finding 1 above leaves a narrower empty-surface route open.
