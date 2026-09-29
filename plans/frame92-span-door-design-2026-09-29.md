# Frame 92: the span door names the wrong exit when a boundary lands one line late

Design record, revision 1. Written by session 00aea66b, rota-ba, 2026-09-29.
Meta workflow. The code is `code_write` in `rota/roles/api.py`, the span
door near line 8560.

## 1. What night 96 showed

The frame's first lines say a broken indent folded `confirm`'s tail into
`get_pager_file`. That reading is wrong (observed: `git show` of
`src/click/termui.py` at `972c025`, `12b76ce` and `6f8394d` in the worktree
`.rota/worktrees/bg_3` of the clickI checkout, 2026-09-29 06:0x). The file
parses at every commit of the batch. `confirm` occupies lines 286 to 344
and `get_pager_file` lines 344 to 361, in `code.source` numbering, at every
one of them. The statement map was right.

What the Developer saw (observed: `turns` of s241, the `code.source`
result for start 340, end 350):

- `code.source` prints the text with no line numbers. It prints a `defs`
  map, `confirm: [286, 344]`, `get_pager_file: [344, 361]`, and the slice.
- The slice has no blank line between `return value` and
  `def get_pager_file(`. Commit `94bd99d` of the batch removed the two blank
  lines.
- The seat counted the lines of the slice and sent `start=340, end=345`
  with four lines of text. Index 344 is the `def` line. The seat meant to
  stop at `return value`.

What the door answered, four times in s241 and the same in s242 and s243:

```
start=340, end=345 cuts through get_pager_file (lines 344 to 361 in
code.source numbering). A span replaces whole statements: to replace
get_pager_file send start=344, end=361; to add after it send start=361,
end=361
```

Both exits are about `get_pager_file`. The seat was editing `confirm`. In
s225 the boundary `end=350` fell inside the docstring of `get_pager_file`,
and the door named the innermost statement, `expr (lines 347 to 356)`, and
offered its span. The seat took that exit, wrote `confirm`'s tail over the
docstring, and the next door refused: "this write changes get_pager_file,
and no criterion of this batch names it". That door is right. The exit
that led there was wrong.

So the fault is one door's message. The exit it offers is the span of the
statement the boundary fell into. The exit the seat needs is the boundary
moved to the edge of that statement, on the side of the statement the
other boundary is in.

## 2. The change

One door, one message. In the span door of `code_write`, when a boundary
`b` falls strictly inside a top-level statement `n` with lines `lo` to
`hi`:

1. Name the top-level statement by its `def` or `class` name. When the
   innermost hit is an unnamed statement inside a definition, such as a
   docstring `Expr`, name the definition and not `expr`. Keep the innermost
   hit's lines in the message as the place the boundary fell.
2. Say which boundary fell: `end=345` or `start=340`.
3. Offer the moved boundary first. For `end` inside `n`, the exit is
   `end=lo`, which stops before `n`. For `start` inside `n`, the exit is
   `start=hi`, which begins after `n`. Name the statement the other
   boundary is in, when it is a top-level definition, so the seat reads
   that the span then covers that statement alone.
4. Offer the whole-statement span and the insert-after span as today, after
   the moved boundary.

The message for s241's call reads:

```
end=345 falls inside get_pager_file (lines 344 to 361 in code.source
numbering). Your start=340 is inside confirm (lines 286 to 344). To edit
confirm alone send end=344, which stops before get_pager_file. To replace
get_pager_file whole send start=344, end=361; to add after it send
start=361, end=361
```

The message for s225's call, `start=340, end=350`, reads the same with
`end=350` and `the boundary fell in its docstring, lines 347 to 356`.

When both boundaries fall inside the same statement, the message is
today's, with the top-level name. When the other boundary is at a
top-level edge, the sentence about it says so: `Your start=344 is the
start of get_pager_file`.

## 3. What does not change

- `code.source` prints no line numbers. A change there moves every
  cassette's prompt and owes a re-record of the register (reasoned: the
  prompt hash covers the tool result text). Out of this frame.
- The door "this write changes X, and no criterion names it" stays as it
  is. It refused a wrong write correctly.
- The runner's rule that ends a session after the same refusal three
  times stays.

## 4. Tests

- One unit test in `tests/rota/test_desk_guards.py` beside
  `test_a_span_that_cuts_a_statement_is_told_where_the_boundaries_are`: a
  file with two adjacent defs and no blank line between them, a span whose
  `end` covers the second `def` line, and the message names the first def,
  the second def, and `end=<lo>`.
- One unit test for the docstring case: `end` inside the docstring of the
  second def names the def, not `expr`.
- The existing test's expected message keeps matching: `cuts through` is
  replaced by `falls inside`, so its regex changes with it. The
  night46 test at `test_night46_context.py:458` matches `cuts through
  assign`, an unnamed top-level statement, and its wording follows the
  same change.
- A recorded case: the Developer, `tests_failing` mode, on a worktree with
  the s241 shape, shows the seat send the moved boundary after one
  refusal. Case file: the Developer's L1 file, beside the span cases.

## 5. The night

Frame 92 ends on a night from a worktree at the closing commit, and it
shares that night with frames 88, 87 and 86 when they are ready. The
night shows a batch that meets this refusal recover with a commit between
attempts, or reach its cap with commits between attempts.

## 6. Price

One implementer pass on Opus, about 60k. One design review, about 60k.
One diff review, about 50k. One recorded case, one live call. One night.
