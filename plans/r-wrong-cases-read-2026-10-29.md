# The 7 wrong L3R cases of R, read (2026-10-29)

Result: 4 of the 7 cases fail because the seat chose a wrong option on a
right binding. 3 of those 4 share one mechanism: a clause of his that asks
for something the page leaves out names no line, so the seat never gives it
an option and approves line 1. 2 cases fail because a refusal's text sent
the seat astray. 1 case fails because the menu lacks the expected reading.
No case fails mainly on the binder or mainly on the expectation. Two
expectations carry a doubt (n171, m121).

The proposal: give each clause that names no line its own menu, `none` or
`add <quote>`, keyed by its clause key, and land the add on the request
line. Reach: 12 of 24 L3R cases carry such a clause, 3 of them expect the
add. Price: one build pass, one review pass, one measure run.

Sources: the log `l3r_main_R.txt` in the session scratchpad, the
`case_runs` rows at prompt hash `47f0e77f5584b482` (all 3 runs of each case
send the same call), `page_clauses` run on each reply at head 559b2540, and
`menu_ruling`, `line_menu`, `_MENU_BASE` in `rota/roles/api.py`
(lines 13769 to 14140).

## 1. The cases

### n170-m58-m59. Seat, right binding (group A)

- His reply: "Ok, every line matches ... lines 5 and 6 read my earlier
  answers right. Please keep what clear() prints exactly as it is now,
  because only the return value should change."
- The binding: c1 lines 5 6, c2 lines 1 to 4, c3 "Please keep what clear()
  prints ..." no lines. The binding is right. The sentence names no line.
- The menu: line 1 is the request line, and it offers `add <quote>`.
- The seat sent `{"1": "approve", ..., "5": "ok", "6": "ok", "rest":
  "approve"}`. No refusal.
- The judge expected line 1 approve with act `add`. It got act None.

### n171-m27-m28. Menu lacks the reading (group C)

- His reply: "Line 3 is wrong, because click does not do this today and
  adding it is the whole change I asked for. ..."
- Line 3 is a ledger row of the vision keeper, `default_taken` "The
  behaviour described in s1 is correctly implemented ...". `menu_kind`
  gives it kind `other`: `approve`, `drop`, `rewrite`, `other <quote>`.
- The binding is right: c1 names line 3.
- The seat sent `"3": "drop"`. No refusal.
- The judge expected line 3 contest with act None. Only `other <quote>`
  lands that row, and the prompt keeps `other` for "when no option fits".
  The menu offers no plain "wrong" for a claim row, so the seat took the
  nearest act.
- Doubt on the expectation: "Line 3 is wrong" on a false claim can read as
  a drop of the claim. I did not read what a mechanical reader does with a
  drop on a ledger row.

### n172-m76-m77. Seat, right binding (group B)

- His reply: "Line 5 is wrong because the clear change has nothing to do
  with the encoding helpers or with the tests for defaults, options, the
  test runner and the app folder. Please keep line 5 to the terminal
  module, the compat module and the terminal tests."
- Line 5 is the touch line with 8 paths. Its menu offers `exclude <path>`
  for each path, and a comma joins paths.
- The binding is right: c3 names line 5.
- The seat sent `"5": "rewrite"`. No refusal.
- The judge expected contest, act `exclude`, target kind `path`.
- He names the files by what they do, and he names the kept files, not the
  excluded ones. The seat must turn "keep X" into the complement of 4 or 5
  paths. The menu holds the reading, but only by excluded path.

### n174-m47-m48. Seat, right binding (group A)

- His reply ends: "This page also no longer shows my request: clear should
  return True when it cleared the screen and False when stdout is not a
  terminal."
- The binding: c1 line 68, c2 lines 8 to 67, c3 and c4 no lines. Right.
- Line 1 is the description item `how_it_works`, kind `other`, and
  `line_menu` adds `add <quote>` on an item.
- The seat sent approve on 1 to 7, drop on 8 to 67, misread on 68. Its
  first call gave `"3": "rewrite"`, and the refusal "no clause of his names
  line 3, so line 3 takes approve" moved line 3 to approve in two turns. The
  refusals worked.
- The judge expected line 1 approve with act `add`. It got act None. All
  other lines pass.

### n174-m53-m58. Refusal text (group D)

- His reply: the page shows the closed clear change, "Please drop all
  twelve lines and replace them with one line saying the docstring gains
  an example ...".
- The binding: c1 lines 1 to 12. Right.
- The menus: line 11 is the request (`approve`, `add`, `other`). Line 12 is
  the touch line of a closed batch, so `line_menu` gives `approve` only.
- The seat sent drop on all 12 lines. Six calls followed. Each refusal
  named the menu ("Line 12, kind touch, takes approve"), and no refusal
  named `ask`. The last call landed drop on 1 to 10, `add` on 11, approve on
  12. One reply was cut at the output budget.
- The judge expected `ask` and no ruling. The landed ruling approves the
  touch line of a change he called finished, which he never said.
- The menus are right: a closed batch moves nothing. The refusal lists only
  the options, so the seat bends his words to fit them.

### n175-m75-m76. Seat, right binding (group A)

- His reply: "Line 6 misreads me ... This page also leaves out my request
  for the one docstring example, and line 5 about the example program has
  nothing to do with it."
- The binding: c1 line 6, c4 line 5, c2 and c3 no lines. Right.
- Line 1 is `how_it_works`, kind `other`, with `add <quote>`.
- The seat sent `{"1": "approve", ..., "5": "drop", "6": "misread"}`. No
  refusal. The code branch of review p9b-2 waits for exactly this add, and
  the seat never sends it.
- The judge expected line 1 approve with act `add`. It got act None.

### n175-m121-m122. Refusal text (group D), with a binder miss

- His reply ends: "Finish it with line 2 alone, and change only the
  docstring in the file on line 9, not the code."
- The binding: c6 "change only the docstring in the file on line 9" has no
  lines. `_subject_lines` returns an empty set on "the file on line 9",
  and returns {9} on "Line 9 is fine". The binder misses a line named
  inside a clause.
- The seat's first call gave `"9": "rewrite"`. The refusal said "To change
  line 9, give add or other with a quote of his words that ask for it". The
  second call gave `"9": "other \"change only the docstring ...\""`, and
  the p9b-2 branch accepted the quote because it lies in a no-line clause.
  Line 9 landed contest.
- The judge expected line 9 approve. A right binding alone does not fix
  the case, because `rewrite` is on the touch menu and lands contest too.
- Doubt on the expectation: "change only the docstring in the file" can
  read as a narrowing of the touch line. The judge reads it as an approve
  of the one path.

## 2. The groups

| Group | Cause | Cases |
|---|---|---|
| A | Seat, right binding: a no-line clause asks for an add, the seat approves line 1 | n170-m58-m59, n174-m47-m48, n175-m75-m76 |
| B | Seat, right binding: "keep X" on the touch line read as rewrite | n172-m76-m77 |
| C | Menu lacks the reading: no plain contest on a claim row | n171-m27-m28 |
| D | Refusal text: the refusal lists options or invites a quote, never `ask` | n174-m53-m58, n175-m121-m122 |

A and B are one cause in the question's terms, 4 cases. Group A is the
largest group with one mechanism.

## 3. The proposal for group A

The mechanism: the prompt says "Key each option by its page line number.
Give an option to every line that his words name." A clause with no lines
names no line, so the seat gives it nothing. The prompt's rule "When his
words ask for a change and name no line, key the line the change is about"
asks the seat to find the line itself. The seat failed that step 9 of 9
runs. The design page, option R, says "The seat answers one option per
clause". Pass R1b moved the keys to lines, and the no-line clause lost its
turn.

The change, in three parts:

1. `page_clauses`: give each clause with no lines an `options` list,
   `["none", "add <quote>"]`, when the page has a line whose menu holds
   `add <quote>`.
2. `menu_ruling`: a clause key `cN` with no lines and option `add` lands
   on the line whose menu holds `add`. Today the same call raises "names no
   page line". When two lines hold `add`, refuse and name them. A call that
   gives a no-line clause no key is refused once (the `refused` set
   exists), and the refusal names its two options.
3. `landing.md`: replace the paragraph "When his words ask for a change
   and name no line ..." with one rule: "Key each clause with no lines by
   its clause key: `none`, or `add <quote>` when it asks for something the
   page leaves out."

The p9b-2 branch (`span = given` for a line key with a quote from a
no-line clause) then has no use for an add. Narrow it, or remove it. That
branch is the path by which m121 landed contest, so the narrowing can also
move group D's m121.

Reach, every place the same rule applies:

- 12 of 24 L3R cases carry a clause with no lines (read by `page_clauses`
  on each reply). 3 of them expect `add` on line 1, and all 3 fail today.
  9 pass today and expect no add: n170-m6-m7, n172-m92-m93, n172-m80-m81,
  n172-m83-m84, n174-m53-m55, n175-m116-m118, n175-m136-m138, and the two
  failing cases of group D.
- Every landing page with a request line or an item line, because
  `line_menu` offers `add` on both kinds.
- The L1 landing cases: my glob found none with a no-line clause. I did
  not confirm the glob covers every L1 file.

Price: one build pass for the three parts and their unit tests, one review
pass, one measure run of the 24 L3R cases (17 minutes measured) and the L1
landing cases. Expected gain: up to 3 cases, 17 to 20 of 24.

## 4. Doubt

- A false add. The seat can answer `add` on a no-line clause such as "Only
  the docstring changes and the code stays the same" (n172-m92-m93) or
  "Please don't give up on this change" (m121). The judge checks only the
  keys of `expect_lines`, and line 1 of those cases holds only a verdict.
  A false add lands approve and passes the judge unseen. Before the
  measure, the nine cases need `act: null` on their request line, or the
  gain is not readable.
- A forced key adds a turn. n174-m53-m58 already took six calls and hit the
  output budget once.
- The 9 of 9 miss can mean the seat does not see the clause as a request,
  not only that it has no key for it. A list choice tests that. A prompt
  sentence alone was the R1 form and failed.
- Group D has its own small change: the "not an option" refusal can end
  with "When no option holds his words, call rulings.rule(ask=...)". Reach:
  every menu refusal on every page. That change is not measured here, and
  it can pull the seat to `ask` on cases that pass today.
- Group C and B are one case each. A plain contest option on a claim row,
  or a `keep only <paths>` option on the touch line, is a fit to one case
  until a second case shows the same need.
