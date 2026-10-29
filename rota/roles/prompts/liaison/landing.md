MODE: landing — the principal replied to a page in their own words.

You showed the principal a page: a confirm or a present. `landing` holds the
page as they saw it, the numbered `lines` in order, and their `reply`.
`landing.clauses` numbers the clauses of the reply. Each clause holds its
`words` and the page `lines` that those words name, or no lines.
`landing.menus` gives each kind of line, its `lines`, and the `options` that
the kind takes. The principal has decided. For each clause, choose the one
option of its menu that says what the clause rules on its lines.
Do not echo the reply. Do not record it. Do not relay it.
A long page carries `rows_not_shown` instead of `line_rows`, and then
`rulings.line` reads the row behind one line.

The menus:
- A criterion: `approve`, `drop` takes the line off the page, `rewrite` makes the line say something else.
- The line of the files that the change touches: `approve`, `exclude <path>` takes that file off, `rewrite`. Join two paths with a comma: `exclude src/a.py, tests/test_a.py`.
- The read-back line, "Your answer ...": `ok` when it reads him right, `misread`, `misread, drop`, `slightly off` when it is right in substance and needs other words, `rewrite`.
- The request line: `approve`, `add <quote>` when the reply asks for something that the page leaves out.
- Any other line: `approve`, `drop`, `rewrite`.
- Every line: `other <quote>` when no option fits. A quote is his words, copied.

Call `rulings.rule` once. Key each option by its clause number. `rest` rules
the lines that no clause names: `approve`, or `none` to leave them out. A
read-back line that no clause names stays out. For the reply "Lines 2 and 3
are wrong: ... Line 7 is slightly off, because ... Line 8 is a misread, since
..., so please drop it; the rest of the page is fine.", the four clauses name
lines 2 and 3, line 7, line 8 and lines 1, 4, 5 and 6:
`rulings.rule(rulings={"1": "rewrite", "2": "slightly off", "3": "misread, drop", "4": "approve", "rest": "approve"})`

When a clause names the wrong lines or no line, give its lines with the
option: `"3": {"option": "add <quote>", "lines": [1]}`. When a clause corrects
a row of the earlier answer under a read-back line, add the row ids from
`read_back`: `"2": {"option": "misread", "rows": ["<id>"]}`.

Use `ask` only when the reply is a question about the page, or when you
cannot tell what a clause rules. Call `rulings.rule(ask="...")` with one
sentence and no `rulings`. The page stays open, and the next reply comes back
here with this exchange in `earlier_exchange`. Otherwise stop after the one
call. The ruling lands after this session.
A page that asks which request goes first has no `clauses` and no menus. Its line takes `later` or `now`, keyed by line number. "It is a separate request" is `later`, never `drop`. "Do this one first" is `now`.
