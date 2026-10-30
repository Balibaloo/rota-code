# The 5 wrong L3R cases after R3, read (2026-10-30)

Result: the 5 cases have 4 causes, and no cause holds more than 2 cases.
The largest group (D, 2 cases) is a refusal text that steers the seat to a
landing that he did not ask for. A new cause holds n174-m47-m48: the wake
was cut before the clause list and the menus, so the seat never saw the
`add` option that R3 built. Group A's lever works where the seat sees it:
n170-m58-m59 and n175-m75-m76 land `c3: add <quote>` 3 runs of 3.

The proposal for group D: end the "is not an option" refusal with one line
that names `rulings.rule(ask=...)`. Reach in the 36 cases: 1 wrong case
(n174-m53-m58). No right case met that refusal today. Price: one build
pass, one review pass, one measure run of the 24 L3R and the 12 L1 landing
cases.

Sources:

- The log `land_r3_after.txt` in the session scratchpad, and the table of
  `seam2_table.py`: 19 of 24, 57 of 72 runs right.
- The `case_runs` rows of each case at `at >= 2026-10-30T03:4`, queried by
  `case_id` first.
- The first wake of each case, read from `cassettes.user` by the reply text.
- `page_clauses` run at head 68eacb2e on each reply of the 36 cases.
- `rota/roles/api.py` 13905 to 14330 and `rota/core/runner.py` 1233 to
  1260 and 2460 to 2480.

Scripts: `r3wr/tx.py`, `r3wr/cl.py`, `r3wr/cut.py` and `r3wr/home.py` in
the session scratchpad.

## 1. The cases

### n174-m47-m48. The wake cut hides the clauses (group E, new)

- His reply: "Line 68 misreads me ... Lines 8 to 67 are a long repeated
  list ... so please drop them. This page also no longer shows my request:
  clear should return True when it cleared the screen and False when
  stdout is not a terminal."
- The binding at head: c1 line 68, c2 lines 8 to 67, c3 "This page also
  no longer shows my request" no lines, c4 "clear should return True ..."
  no lines. The binding is right.
- The menus: line 1 is `how_it_works`, an item, and holds `add <quote>`.
  The refusal of run 3 offers `add <quote>` to c3, so `_add_lines` found
  one add line.
- The first wake is 19,678 characters, cut to 12,838. `runner.py:2464`
  writes `his_words` before `clauses` (2475) and `menus` (2479).
  `his_words` repeats the 115-character c2 sentence for each of lines 8 to
  67. The cut falls inside `his_words` at line 50. The seat saw no clause
  list and no menu.
- What the seat sent:
  - Runs 1 and 2: one call, lines 8 to 67 drop, 68 misread, `rest: none`,
    and `ask=` his request sentence. The ask went to him as a converse, and
    no ruling landed.
  - Run 3: a first call with no clause keys. The refusal at
    `api.py:14288-14298` names "c3, c4" but not their words. The seat sent
    `c3: none, c4: none`. A second refusal (`api.py:14327`) named lines 1
    to 7, and the seat approved them.
- What landed: run 3 lands line 1 approve with act None. Runs 1 and 2 land
  nothing.
- The judge expected line 1 approve with act `add`, and one ruling.
- The cause: the cut. The clause refusal cannot repair the cut, because it
  names the clause keys and not the words.
- R3 touched the case. Its clause options and its unkeyed refusal fire
  here. The lever did not land the case because the seat never saw the
  options in the wake, and the refusal gives keys with no words.

### n174-m53-m58. The menu refusal never names ask (group D)

- His reply: "I can't approve this page ... Please drop all twelve lines
  and replace them with one line saying the docstring gains an example ...
  The new page should also say that only the docstring in the termui file
  changes ..."
- The binding: c1 lines 1 to 12, c2 and c3 no lines. Right.
- The menus: line 11 request, `approve; add <quote>; other <quote>`. Line
  12 touch of a closed batch, `approve` only.
- What the seat sent, all 3 runs: drop on 1 to 12 with `c2: add` and
  `c3: add`. The refusal at `api.py:14242` said "Line 11, kind request,
  takes approve; add <quote>; other <quote>". The seat sent `11: other
  <quote>`. The next refusal said "Line 12, kind touch, takes approve", and
  the seat sent `12: approve`. Run 2 also hit the output budget once.
- What landed: drop on 1 to 10, contest `other` on 11, approve on 12. The
  `c2` add rides to line 11, and the line key wins (`api.py:14150-14152`),
  so the add lands nothing.
- The judge expected `ask` and no ruling.
- The cause: no option of any menu holds "replace the page", and the
  refusal text lists only options. So the seat bends his words to fit them.
- R3 touched the case. The seat now keys `c2` and `c3` add. The outcome is
  the same as at 559b2540.

### n175-m121-m122. A quote path lands a contest (group D)

- His reply ends: "Finish it with line 2 alone, and change only the
  docstring in the file on line 9, not the code."
- The binding: c6 "change only the docstring in the file on line 9, not
  the code." has no lines. `_subject_lines` still misses "the file on line
  9". The binder miss stands.
- The menus: `_mentioned_lines` finds line 9 in c6, so `api.py:14001`
  gives c6 `none` only.
- What the seat sent, all 3 runs: `9: rewrite`. The refusal at
  `api.py:14213` says "line 9 takes approve. To change line 9, give add or
  other with a quote of his words that ask for it". The seat then sent `9:
  other "change only the docstring ..."`.
- What landed: `api.py:14188` finds c6 as the home of the quote. The
  refusal at 14197-14206 fires only when c6 holds `add`, and c6 holds
  `none` only. So `span = given`, and line 9 lands contest.
- The judge expected line 9 approve.
- The cause: the refusal invites a quote, and the home path accepts a
  quote from a `none`-only clause on a line key.
- R3 touched the case. R3 added the refusal for a clause that holds
  `add`, and R3b made c6 `none`-only. The comment at 14193-14196 keeps the
  line key as "the one place of the change" for such a clause. The outcome
  is the same as at 559b2540. The doubt on the expectation from the earlier
  read stands.

### n171-m27-m28. The menu lacks the reading (group C)

- His reply: "Line 3 is wrong, because click does not do this today ..."
- The binding: c1 line 3, c2 lines 1 2, c3 line 4. Right.
- What the seat sent, all 3 runs: one call, `3: drop`, and `1: add
  Roaming when ...`. No refusal.
- What landed: line 3 contest, act `drop`.
- The judge expected line 3 contest with act None.
- The cause: line 3 is a ledger row of kind `other`, with `approve`,
  `drop`, `rewrite`, `other <quote>`. No plain contest is on that menu.
- R3 did not touch the line that fails.

### n172-m76-m77. The seat picks a visible wrong option (group B)

- His reply: "Line 5 is wrong because ... Please keep line 5 to the
  terminal module, the compat module and the terminal tests."
- The binding: c3 line 5. Right.
- What the seat sent, all 3 runs: one call, `5: rewrite`. No refusal.
- What landed: line 5 contest, act `rewrite`, target kind `row`.
- The judge expected act `exclude`, target kind `path`.
- The cause: he names the kept paths. The menu offers `exclude <path>` by
  excluded path only, and the seat does not compute the complement.
- R3 did not touch the case.

## 2. The groups

| Group | Cause, observed in code | Cases |
|---|---|---|
| D | A refusal text steers the seat: `api.py:14242` lists options and never ask, `api.py:14213` invites a quote that `api.py:14188` accepts | n174-m53-m58, n175-m121-m122 |
| E | The wake cut: `his_words` (`runner.py:2464`) comes before `clauses` and `menus`, and the cut drops them | n174-m47-m48 |
| C | The claim row menu has no plain contest | n171-m27-m28 |
| B | "keep X" on the touch line, read as rewrite | n172-m76-m77 |

Group A is gone as a group: its lever works when the seat sees it.
Group D holds two code sites. One lever covers both only in shape 3 below.

## 3. The next lever, group D

What the code holds now:

- `api.py:14242`: "{label}: {value!r} is not an option of line {n}. Line
  {n}, kind {kind}, takes {options}". No text names `ask`.
- `api.py:14213`: "line {n}: no clause of his names line {n}, so line {n}
  takes approve. To change line {n}, give add or other with a quote of his
  words that ask for it". It fires on every call.
- `api.py:14188-14207`: a line key with an `add` or `other` quote from a
  no-line clause lands on that line when the clause holds `none` only.
- `ASK_NOT_OPTION` (`api.py:13927`) names `rulings.rule(ask=...)` only for
  his question.
- An ask with rulings sends the question and lands no ruling. Runs 1 and 2
  of n174-m47-m48 show that today.

The refusal texts that the cases met today (the log):

| Refusal | Site | Right cases | Wrong cases |
|---|---|---|---|
| "clause cN names no page line, so it takes none" | `api.py:14158-14168` | n174-m53-m55, n175-m136-m138 | none |
| "is not an option of line N" | `api.py:14242` | none | n174-m53-m58 |
| "no clause of his names line N" | `api.py:14213` | none | n175-m121-m122 |
| "cN: ... gives it no key" | `api.py:14293` | none | n174-m47-m48 |
| "lines ... have no ruling" | `api.py:14327` | none | n174-m47-m48 |

The 12 L1 landing cases, last run 03:56 to 03:59 today, met no refusal.
10 of them passed.

Candidate shapes:

1. One ask line at the end of the 14242 refusal only: "When no option
   holds his words, call rulings.rule(ask=...) with no rulings."
   - Cost: one text line and one unit test.
   - Failure: the seat can still take the listed option. The seat can also
     ask on a page where an option fits. Runs 1 and 2 of m47-m48 show that
     the seat puts a plain request into `ask`.
   - Reach in the 36 cases: n174-m53-m58. No right case met the refusal.
     m121 stays wrong.
2. Shape 1, and close the home path for a `none`-only clause. At 14188,
   a quote from a clause that mentions a page line does not land, and the
   14213 text drops its second sentence.
   - Cost: two sites, the comment at 14193-14196 reversed, and about four
     unit tests.
   - Failure: a real change that he names inside a clause, as "drop the
     file on line 9", loses its only place until the binder reads "the
     file on line 9" as line 9. The m121 expectation carries a doubt.
   - Reach: m58 and m121. In the 19 right L3R cases, no final call keys a
     line that no clause names with `add` or `other` (`r3wr/home.py`).
3. One shared tail with the ask line on every menu refusal: 14158, 14213,
   14242, 14293 and 14327.
   - Cost: one constant and five sites.
   - Failure: the two right cases that met the 14158 refusal today,
     n174-m53-m55 and n175-m136-m138, can switch to ask and go wrong.
   - Reach: m58 sure, m121 and m47-m48 unsure.

Recommendation: shape 1. It is the smallest place that covers the
observed cause of m58, and no right case passes through it today. The risk
to the 19 right cases is none by the log. The risk on new pages is a false
ask, which costs him one question and lands nothing. Leave m121 for the
binder: its true cause is "the file on line 9" bound to no line.

Group E is the next lever after D. Its reach in the 36 cases is 1, because
only the first wake of n174-m47-m48 was cut (`r3wr/cut.py`). Its reach in
use is every page where one clause names many lines, because `his_words`
repeats the clause once for each line. Two shapes: write `clauses` and
`menus` before `his_words`, or drop `his_words` when `clauses` is present.
The clause list holds the same words once. A second small change: the
unkeyed refusal at 14293 can name each clause's words, so a cut wake can
recover. No right case met that refusal today.

## 4. The p12c low 1: reach

`page_clauses` at head on each of the 36 replies finds one clause that
holds a question and a statement:
L1-LI-a-question-then-a-statement-at-the-confirm-is-the-question, c1,
"before I say yes: does each person pay an equal share, or their own
order? I mean an equal share of the total including the tip." The case
expects the question, and the statement only explains it. It passed 3 runs
of 3 today. No L3R reply carries a question. So no case of the 36 shows
the harm of low 1: a statement whose line stays unruled. A fix of low 1
has no measured case.

The L1 page size was read as the count of `body_refs`, not from the built
page. That count can differ from the page lines.

## 5. Doubt

- Group D is two sites. The grouping by "a refusal steers" is mine. The
  two cases do not share one line of code.
- Shape 1 may not move m58. The seat bent his words to the listed options
  through two refusals. One added sentence can lose to the menu list.
- `seam2_table.py` counts refusals per run from the log. Its turns column
  is not a full count of calls.
- The L1 refusal read used `case_runs` rows whose model I did not check.
- Duplicate rows in `case_runs` inside the time window doubled the scan
  output. They do not change the counts above.

## 6. Usage

About 75k tokens, above the 40k cap. One register query on `case_id LIKE`
ran past two minutes in the background.
