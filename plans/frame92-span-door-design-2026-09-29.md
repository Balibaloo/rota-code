# Frame 92: the span door names the wrong exit when the seat miscounts lines

Design record, revision 2. Written by session 00aea66b, rota-ba, 2026-09-29.
Revision 1 was written at 05:5x and reviewed on Opus 5.5 at 05:57
(observed: 45.5k on the harness line, 12 tool calls). Revision 2 folds the
seven findings. Meta workflow. The code is `code_write` in
`rota/roles/api.py`, the span door near line 8560.

## 1. What night 96 showed

The frame's first lines say a broken indent folded `confirm`'s tail into
`get_pager_file`. That reading is wrong (observed: `ast.parse` of
`src/click/termui.py` at `972c025`, `12b76ce` and `6f8394d` in the worktree
`.rota/worktrees/bg_3` of the clickI checkout, by the reviewer, 2026-09-29
05:57). The file parses at every commit of the batch. `confirm` and
`get_pager_file` occupy lines 286 to 344 and 344 to 361 at `12b76ce` and
`6f8394d`, and 286 to 342 and 342 to 359 at `972c025`, in `code.source`
numbering. The statement map was right. Commit `c713ab4` of the batch, at
04:28, removed the two blank lines between the defs (observed: `git log` of
the file, the reviewer, 05:57).

What the Developer saw (observed: `turns` of s241, turn 10, the
`code.source` result for start 340, end 350, read by this session and the
reviewer):

- `code.source` prints the text with no line numbers. It prints a `defs`
  map, `confirm: [286, 344]`, `get_pager_file: [344, 361]`, and the slice.
- Line 339 of the file is `    if abort and not value:`. Line 340 is the
  over-indented `            if default_on_eof and default is not None:`.
  Line 343 is `    return value`. Line 344 is `def get_pager_file(`.
- s241 sent `start=340, end=345` with text whose first line is
  `    if abort and not value:`. Both boundaries are one line late. The
  span the seat meant is `start=339, end=343` or `start=339, end=344`.

What the door answered, four times in s241 (observed: `turns` of s241):

```
start=340, end=345 cuts through get_pager_file (lines 344 to 361 in
code.source numbering). A span replaces whole statements: to replace
get_pager_file send start=344, end=361; to add after it send start=361,
end=361
```

Both exits are about `get_pager_file`. The seat was editing `confirm`. In
s225 and s243 the boundary `end=350` fell inside the docstring of
`get_pager_file`, the door named the innermost statement, `expr (lines 347
to 356)`, and offered its span. The seat took that exit in s225, wrote
`confirm`'s tail over the docstring, and the next door refused: "this write
changes get_pager_file, and no criterion of this batch names it". That door
is right. s242 made no `code.write` (observed: `tool_calls` of s242, the
reviewer).

The reviewer simulated the merge (observed: the reviewer's inline Python on
s241's slice, 05:57): a moved `end=344` with the seat's `start=340` and
text repeats the `if abort` header, and the merged file raises
`SyntaxError: expected an indented block`. So a moved boundary alone is not
the exit. The seat needs the facts its arithmetic lacks: the text of the
file at its `start` and at its `end`.

The root cause is that `code.source` prints no line numbers (reasoned: the
reviewer, point 7, and this session agrees). Section 3 says why that change
is not in this frame.

## 2. The change

One door, one message, and one helper that returns the path of statements
a boundary falls through. In the span door of `code_write`:

1. `_cut` returns the path from the top-level statement down to the
   innermost statement the boundary falls inside, as `(node, lo, hi)`
   tuples, or `aligned`, or `None`. The caller names the top-level node
   when it has a name, and cites the innermost node's lines as the place the
   boundary fell. When both boundaries fall inside one definition, the
   message names and offers the innermost statement, as today (reasoned:
   the night-52 loop came from offering the whole function when the edit
   was inside it, and the night46 test at `test_night46_context.py:458`
   holds that).
2. The message says which boundary fell: `end=345` or `start=340`.
3. The message echoes the file. For `start`, the line at index `start`.
   For `end`, the line at index `end - 1`, the last line the span covers,
   and the line at `end`, the first line it leaves. Each as
   `line 344 is 'def get_pager_file('`, the text stripped to 60 characters.
4. When the first line of `text` equals a line of the file within three
   lines of `start`, and not the line at `start`, the message says
   `your text's first line is line 339 of the file, so a span that replaces
   it starts at start=339`. A fact: the line is there. The same for the last
   line of `text` against the lines within three of `end - 1`, giving
   `end=<k + 1>`. When the text's last line matches nothing, no sentence.
5. The moved-boundary exit comes from the shallowest level where `start`
   and `end` fall in different siblings, not from the top level. For `end`
   inside sibling n at (lo, hi) and `start` in an earlier sibling, the exit
   is `end=lo`, which stops before n. For `start` inside n and `end` in a
   later sibling, `start=hi`. The exit is offered only when the moved span
   is not empty and `start < end` holds after the move.
6. The whole-statement span and the insert-after span follow, as today.
7. `start == end` inside a statement is an insert. The message says so and
   offers the insert-after span alone, as today.
8. `end` inside the first statement of the file with `start=0` gets no
   moved boundary, because `end=0` is an empty span. The message echoes the
   lines and offers the whole-statement span.

The message for s241's call reads:

```
start=340, end=345: end=345 falls inside get_pager_file (lines 344 to 361 in
code.source numbering); start=340 is inside confirm (lines 286 to 344).
Line 340 is '            if default_on_eof and default is not None:'. Line
344 is 'def get_pager_file('. Your text's first line is line 339 of the
file, so a span that replaces it starts at start=339. To edit confirm
alone send end=344, which stops before get_pager_file. To replace
get_pager_file whole send start=344, end=361; to add after it send
start=361, end=361
```

The message for s225's `start=340, end=350` names `get_pager_file`, says
the boundary fell in its docstring, lines 347 to 356, and carries the same
line echoes and exits.

## 3. What does not change

- `code.source` prints no line numbers. Numbering each line changes the
  tool result of every case whose seat calls `code.source`, and each such
  turn's cassette re-records (reasoned: the cassette key is the prompt hash,
  and the tool result is in the next prompt). That is the Developer's cases
  and the survey cases at least. If the night after this frame shows the
  seat loop on the same shape with the echoed lines in front of it, the
  numbering becomes its own frame, priced on the count of cases that call
  `code.source`.
- The door "this write changes X, and no criterion names it" stays as it
  is. It refused a wrong write correctly.
- The merged-parse door stays. With the echoed lines the seat can correct
  both boundaries before it reaches that door.
- The runner's rule that ends a session after the same refusal three
  times stays.

## 4. Tests

- `tests/rota/test_desk_guards.py`, beside
  `test_a_span_that_cuts_a_statement_is_told_where_the_boundaries_are`:
  - Two adjacent defs with no blank line between them, `start` one line
    late and `end` covering the second `def` line, text whose first line is
    the file's line at `start - 1`. The message names both defs, echoes
    the lines at `start` and `end - 1`, says `start=<start - 1>`, and offers
    `end=<lo>`.
  - `end` inside the docstring of the second def names the def and cites
    the docstring's lines, not `expr`.
  - Both boundaries inside one def name the innermost statement, as the
    night46 test does.
  - `start=0` and `end` inside the first statement offers no moved boundary.
- The existing regexes: `test_desk_guards.py:1969` matches
  `cuts through echo \(lines 3 to 8.*start=8, end=8`, and
  `test_night46_context.py:458` matches `cuts through assign .*lines 3 to
  5`. The wording `cuts through` becomes `falls inside`, and both regexes
  change with it. No other test in `tests/rota` matches the old wording
  (observed: the reviewer's grep, 05:57).
- A recorded case: the Developer, `tests_failing` mode, on a worktree with
  the s241 shape, shows the seat send corrected boundaries after one
  refusal. Case file: the Developer's L1 file, beside the span cases.

## 5. The night

Frame 92 ends on a night from a worktree at the closing commit, and it
shares that night with frames 88, 87 and 86 when they are ready. The
night shows a batch that meets this refusal commit between attempts, or
reach its cap with commits between attempts.

## 6. Price

One design review, 45.5k on Opus, done. One implementer pass on Opus,
about 60k. One diff review, about 50k. One recorded case, one live call.
One night.
