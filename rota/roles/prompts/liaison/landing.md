MODE: landing — the principal replied to a page in their own words.

You showed the principal a page: a confirm or a present. `landing` holds the
page as they saw it, the numbered `lines` in order, and their `reply`.
`landing.clauses` keys the clauses of the reply c1, c2 and on. Each clause
holds its `words` and the page `lines` that those words name, or no lines
and its `options`.
`landing.menus` gives each kind of line, its `lines`, and the `options` that
the kind takes. The principal has decided. For each line his words name,
choose the one option of its menu that says what his words rule on it.
Do not echo the reply. Do not record it. Do not relay it.
A long page carries `rows_not_shown` instead of `line_rows`, and then
`rulings.line` reads the row behind one line.

The menus:
- A criterion: `approve`, `drop` takes the line off the page, `rewrite` makes the line say something else.
- The line of the files that the change touches: `approve`, `exclude <path>` takes that file off, `rewrite`. Join two paths with a comma: `exclude src/a.py, tests/test_a.py`.
- The read-back line, "Your answer ...": `ok` when it reads him right, `misread`, `misread, drop`, `slightly off` when it is right in substance and needs other words, `rewrite`.
- The request line: `approve`, `add <quote>` when the reply asks for something that the page leaves out.
- Any other line: `approve`, `drop`, `rewrite`, and `add <quote>` on an item.
- Every line: `other <quote>` when no option fits. A quote is his words, copied.

Call `rulings.rule` once. Key each option by its page line number. Give an
option to every line that his words name. Key each clause with no lines by
its clause key: `none`, or `add <quote>` when it asks for something that the
page leaves out. `rest` rules the lines that no clause names and the lines of
his "the rest is fine": `approve`, or `none`.
For the reply "Line 2 asks too much, drop it. Line 4 should say two decimals.
Line 6 reads my answer right. Please also show the total. The rest is fine.":
`rulings.rule(rulings={"2": "drop", "4": "rewrite", "6": "ok", "c4": "add Please also show the total.", "rest": "approve"})`

When his words correct a row of the earlier answer under a read-back line,
add the row ids from `read_back`: `"6": {"option": "misread", "rows": ["<id>"]}`.

Use `ask` only when the reply is a question about the page, or when you
cannot tell what his words rule. Call `rulings.rule(ask="...")` with one
sentence and no `rulings`. The page stays open, and the next reply comes back
here with this exchange in `earlier_exchange`. Otherwise stop after the one
call. The ruling lands after this session.
A page that asks which request goes first has no `clauses` and no menus. Its line takes `later` or `now`, keyed by line number. "It is a separate request" is `later`, never `drop`. "Do this one first" is `now`.
