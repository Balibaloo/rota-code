# The architecture review of 2026-09-15, and the verdict on it

Meta workflow. The review is an agent's report on rota's module depth. It
proposes ten candidates. This file records which ones survive, checked
against the tree, and which ones the standing order refuses.

Written by session 1f54b02f, peer name rota-c1, on 2026-09-19. The
session held no frame. Roman asked one question: "are any of these
good?"

## The source

The review is an HTML page at
`C:/Users/roman/AppData/Local/Temp/architecture-review-20260915-235445.html`
(observed: the path Roman gave). It reads the tree at `392785a` plus one
uncommitted door. The temporary directory is volatile, so the source can
disappear. A copy in this repository is not made yet, and Roman has not
ruled on whether to make one.

The review fixed two defects itself, in `904f596`, on the night it was
written. They are finding 83 and finding 84 in `plans/wake-audit.md`.

## The verification

The verdict does not trust the review's numbers. The claims below are
checked by grep and by a line count against the tree at `c4599dc`, which
is 190 commits after the reviewed commit (observed: this session's own
probes of the tree).

| Claim in the review | At `c4599dc` |
| --- | --- |
| `tests_encode` is 870 lines with 27 doors | 876 lines, 30 raises. It grew |
| `code_write` is 714 lines with 22 doors | 714 lines, 22 raises. Exact |
| Six lists of reffable tables | Six, and two more in `testkit` |
| "attempt n of 3" is a literal | `rota/core/scheduler.py:334`, against the `tick_attempt_cap` Setting at `:1470` |
| Five fakes omit `tools=` | All five present: `test_runner.py:132`, `test_chaos.py:46`, `test_chaos_confirm.py:43`, `test_chaos_inquiry.py:45`, `test_chaos_onboarding.py:44` |
| `Write.op` is never set on the runner path | `rota/core/runner.py:2434` sets no `op`. `rota/core/db.py:409` branches on it |
| Nine spellings of "is this a test path" | Overstated. One owner and four disagreeing copies |
| `turns` is initialised twice | Gone |
| `test_l1` has a `skipif(True)` | Gone |

The review's structural readings hold. Its counts are close but not
exact, and one count is inflated.

## The suggestions that survive

Each row is a candidate, not a frame. No row carries a token price yet,
so no row is a frame (reasoned: the grill prices every ends-when line
from the anchors in `plans/operating-facts.md`).

| # | What | Evidence | Why it pays | Size |
| --- | --- | --- | --- | --- |
| 1 | One owner for "is this a test path" | Owner at `rota/roles/api.py:9009`. Copies at `:3153`, `:4087`, `:7868` disagree. The copies miss `_test.py` and `conftest.py` | A disagreeing copy is how finding 83 stayed hidden for six nights | Small |
| 2 | One owner for the `.rota/worktrees` path rule | The defect fixed in `904f596`. `code_commit` fixed it on click night 22. The escalation door stayed broken | Frame 33's design review caught the same class: `walk` tested an absolute path against `SKIP_DIRS` | Small |
| 3 | Fix the five fakes that omit `tools=` | The five sites listed above | Five chaos tests pass for the wrong reason. They raise `TypeError`, not their scripted error | Small |
| 4 | Move "attempt n of 3" into the Setting | `scheduler.py:334` against the Setting at `:1470` | Law 7 says caps live in config. The cockpit prints "of 3" while `loop_cap` is 10 | One line |
| 5 | A declared case schema, validated at load | `check()` reads every key with `.get` | A misspelt `expect` key passes as a green case that checks nothing. The gate's stale line is part of every acceptance | Small |
| 6 | Set `Write.op` or delete its branch | `runner.py:2434` and `db.py:409` | A dead branch in the write pipeline reads as live code | One line |
| 7 | `tick_slicing` writes, and the purity test misses it | `test_predicates_are_pure` checks `items`, `messages` and `sessions` only | A predicate that writes breaks the purity the test claims to hold | Small |

Rows 1 and 2 are one frame. Rows 3, 4, 6 and 7 are parked rows, or one
cleanup frame. Row 5 is its own small frame.

All seven sit outside Roman's order. The order runs finding 42, then the
language seam, then breadth.

## The suggestions that are refused

Cards 1, 3, 5, 6, 7 and 8 rewrite the core. Card 1 is the review's own
top recommendation. It rewrites 1,590 lines of the two hottest
functions.

Three reasons to refuse them (reasoned: this session's judgement, not a
ruling by Roman):

1. The order forbids it. `rota/COMPLETION.md`, "The order from here",
   says "do not rewrite the core".
2. Frame 33 was writing the same pipeline while the review was read. A
   card 1 rewrite would collide with it.
3. The review's safety argument fails against the review's own card 10.
   Card 1 claims the register verifies a pure refactor for free. Card 10
   records that 1,140 of 1,419 recordings are never replayed. The
   instrument covers about one fifth of the corpus. That is not free
   verification.

Card 4, the world builder for the tests, is the one large candidate
worth an argument later. It lowers the price of every future frame. It
is a campaign, not a frame, and it is also outside the order.

## Open

- Roman has not ruled on any row above.
- The source HTML is in a temporary directory and can disappear. A copy
  in `plans/archive/` is offered and not made.
- No row is priced.
