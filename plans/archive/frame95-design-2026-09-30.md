# Frame 95, a whole-function rewrite that stops short: design note, 2026-09-30 04:30

This is a meta workflow note about a rota workflow wall, written at f63767f. No code exists yet.

## 1. The wall

- Night 98, s183 sent span `288,345`, all of `confirm`. The text stopped at
  `raise Abort() from None`. Every door accepted it. Commit `d8d87beb` deleted
  13 lines, `if value in ("y", "yes"):` to `return rv` (observed: night98 walk, section 6).
- Night 97, s214 sent `340,352`, the tail of `confirm`. The text was the loop,
  and it ended at `continue`. The lines `if abort and not rv:` to `return rv`
  went (observed: night97 walk, section 6).
- Night 98 ends on `raise`. Night 97 ends on `continue`. A gate of `raise` or
  `return` alone misses night 97, so the gate below takes four words.

## 2. Where things sit today (reasoned: read at f63767f)

- `code_write`, `rota/roles/api.py:8499-9604`: span doors in `if span:`, the
  merge at line 9010, the parse door near 9072, then the write and `out`.
- The drops door and `_changed_unnamed_defs` judge whole defs only.
- `push_working_set` (`rota/core/runner.py:1560`) puts `code.read` into the
  Critic's prompt. `code_read` (`api.py:8458`) returns `git diff HEAD~1 HEAD`.
- The Critic wakes on `tick:review` only (`rota/core/predicates.py:1149`),
  and only on a green harness at `head_commit`.

## 3. Design A: a note in `code.write`

Site: a helper `_tail_drop(old_lines, new_text, start, stop, n_new)` beside
`_changed_unnamed_defs`, called right after the merge at line 9010. The
sentence goes into `out["dropped"]`. The write is accepted in every case.

The helper computes the loss from two ASTs:

1. Parse the original file and the merged file. The doors before prove both.
2. `O` is the innermost (parent, field) list of the original that holds
   `[start, stop)`, cut to the span. The walk is the one the "innermost
   statement that holds the whole span" loop uses.
3. Find the same list in the merged tree by the index path of its parent.
   The lines above the span do not move. `N` is the list's statements with
   `_lo` in `[start, start + n_new)`.
4. When `O` and `N` are each one def of one name, step into the two bodies.
   Night 98 is this case. Otherwise the chain starts on the span's own list,
   as on night 97. A whole-file write uses `start=0` and the old length.
5. Take `n`, the last statement of `N`. Pair it with the statement of `O` whose
   stripped first line equals the stripped first line of `n`. Else pair it with
   `O[len(N)-1]` when the type is the same. Else stop, with no note.
6. The statements of `O` after the paired one are the drops of this level.
7. Step into the pair, through the last non-empty field of `n` by line:
   `body`, `orelse`, `finalbody`, `handlers` or `cases`. Repeat from step 5.
8. The gate, "a terminator inside a branch": the chain's leaf is `Return`,
   `Raise`, `Continue` or `Break`. Its parent is a compound statement, not the
   span's list and not the def.
9. "Statements after that branch at the same level" are the drops of step 6,
   at every level from the span's list down to the parent of the leaf.
10. A dropped line counts only when its stripped text is absent from the text.
    A tail that the seat moved into the branch is then not a loss.
11. Count the lines, and name the lowest one.

The sentence: "This write drops 13 lines that came after
`raise Abort() from None`, from `if value in ("y", "yes"):`."

Lines: about 60 in `api.py` (helper 45, call and key 8, comments 8), 40 in tests.

What it buys:

- s183: the write lands, and s183 reads "13 lines" before `code.commit`. The
  note is a chance, not a refusal. Later sessions never see the note.
- Night 97: s214, s215 and s216 each read "drops 3 lines that came after
  `continue`, from `if abort and not rv:`".

False positives, and the way past:

- A stub that means to end at `raise`, or a new tail that ends at `return`
  in an `if`. The note fires, the write lands, and the seat commits.
- A small model can read the note as an order and paste the old lines back.
  The sentence states a fact and asks for nothing.

Tests:

1. A whole-def `confirm` span cut after `raise` lands with `dropped`: 13 lines and the first.
2. A span that moves `return rv` into the loop's branch has no `dropped` key.

## 4. Design B: the Critic judges the deleted lines

The wake gets the diff from `push_working_set`, which puts the result of
`code.read` in the prompt. Today the Critic sees the unified diff of the last
commit. Deleted lines are `-` lines among `+` lines, with no count and no list.
A deletion in an earlier commit is out of view. On night 98 it sees `c59c92f2` only.

The one change: `code_read` adds `removed lines`, per file. An entry is a `-`
line whose stripped text no `+` line of that file carries. The key appears
only when it has entries. `review.md` gains one step: "For each removed line,
name the criterion that asks for its removal. A removed line that no criterion
asks for fails the criterion of its function."

A batch of several commits also needs the diff against the merge-base, not
`HEAD~1`. Lines: `code_read` 20, `worktrees.diff` 5, `review.md` 2, tests 30.
About 8 case entries carry `role: critic` (observed: grep of `tests/rota/cases`,
2026-09-30). Each one whose diff removes a line goes stale.

What it buys:

- s183 and night 97: nothing. Both harnesses stayed red, `tick:review` never
  fired, and no Critic woke.
- B catches a lost tail only when the tests do not cover the tail.

False positives, and the way past: a deleted comment or a renamed variable is
a removed line. The Critic must name a criterion for each one, or it fails a
batch that is right. The seat gets past only with a new commit and verdict.

Tests:

1. A commit that deletes `return rv` returns `removed lines` with `return rv`.
2. A commit that moves a line to a new place has no `removed lines` key.

## 5. The choice

- Smaller: B, about 27 lines of code against about 60, before its re-records.
- Recommended: A. No Critic wakes on a red harness, so B buys nothing on either night.
