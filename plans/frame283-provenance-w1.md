# Frame 283, W1 of night 163: the provenance of the keep route and the one-token rewrite

Read-only read on Opus, 2026-10-24, at the branch head d8fc792a. The code
tree under `rota/` is the same as at 9c4f02d9 (observed: `git log
9c4f02d9..HEAD -- rota/` is empty). Databases opened with `?mode=ro`.

## Verdict

The door is wrong to fire, and the cause is a known price that the
session accepted on a route nobody followed to the seat. Two defects
join (observed and reasoned below):

1. **The predicate.** The span branch of `code.write` has no rewrite rule
   for a short line. `_changed_kept` keeps a dropped line only when it has
   three or more distinct tokens, so `return` (one token) always stays in
   the note. 25fa18ef already fixed this shape for whole-file writes with
   a per-owner AST kind count. The span branch, which s221 used, did not
   get the same rule.
2. **The route.** `_note_routes` names `msg.escalate_architect` as the
   only way to keep a rewrite, unconditionally. The Developer's
   `batch_start` and `verdict_failed` modes do not hold that tool. Review
   5 checked the route against `tests_failing.tools` only. This breaks
   the rule of frame 135: name a call only where the door then admits it.

By the frame's own design, `return` to `return False` is a rewrite, not a
removal. The smallest repair is to run 25fa18ef's kind count in the span
branch too. s340 keeps its refusal, because its seven statements lose
their kind counts.

## 1. The predicate

- The write. s221 t13 is a span write, `code.write(path='src/click/termui.py',
  start=601, end=613, ...)` (observed: `tool_calls` of night 163). The span
  branch calls `_drop_note` at `rota/roles/api.py:17850`. `_drop_note`
  (`api.py:21456`) calls `_tail_drop` and `_lost_statements`. Neither has a
  rewrite rule, so `return` at line 609 goes into `drop_lines`.
- The filter that failed. `api.py:18705` calls `_changed_kept(entry, text,
  before)` on both branches. At `api.py:19734-19738`:

  ```
  # A line of one or two distinct tokens, such as `return x` or
  # `x = int(x)`, is never kept: too many lines hold its tokens.
  toks = set(re.findall(r"\w+", line))
  return len(toks) >= 3 and any(toks <= n for n in new)
  ```

  `{"return"}` has one token, so `kept` is False, and the note opens. The
  new line `return False` holds the token, but the floor stops the test
  before the subset check.
- The base filter. `_base_held` (`api.py:19786`) keeps the line, because
  click's base holds `return` under `clear`.
- The commit door. `_note_refusal` (about `api.py:19190-19231`) calls
  `_unruled_gone` (`api.py:19521`). That calls `_asks_removal`
  (`api.py:19494`). `return` is in `_BARE_LINES` (`api.py:19369`), so it
  needs a removal verb in a clause that names `return`, and the owner
  `clear` in the sentence. The item and all eight criteria hold no
  removal verb (observed: `items`, `criteria` of bg_2). So the line stays
  unruled, and every commit is refused.
- The floor's provenance. The floor came in pass 4 at 18:13 on
  2026-10-17: "a stored line of three or more whole tokens is kept when
  one new line holds them all" (observed: `plans/stack.md`, frame 283).
  Review 4, finding 1, judged it only in the other direction, a line
  wrongly kept: "The floor counts repeated words, so `x = int(x)` passes
  the floor with two distinct tokens" (observed:
  `plans/frame283-review-4.md:17`). Pass 5 at 18:27 made the floor
  "three distinct tokens". The pin is
  `test_a_line_of_two_tokens_is_never_kept_by_the_subset_rule`.
  So the floor is a reviewed decision against false keeps. No review
  asked what it costs for a one-token rewrite on the span branch. That
  cost was then named and accepted as a price (see section 3).

## 2. The design

- The frame's words. Ends-when: "a commit whose tree removes a statement
  that no landed note names is refused whatever reply wrote it, with
  s340's turn 14 as the red test" (observed: `plans/stack.md`, `### 283.`).
  The site line names the loss: s340 "dropped the `version` logic of
  `version_option`, turned three of click's own tests red".
- s340. `plans/frame283-count.md:91`: "lost: `if not param_decls:` and 6
  `kwargs` lines, writes in replies 8 and 12 hold 0 of 7". The statements
  left the function. No statement took their place.
- s221. One `Return` node with no value became one `Return` node with the
  value `False`, at the same place under `clear`. The item asks for it:
  "clear() returns True when it cleared the screen and False when stdout
  is not a terminal." c2_non_terminal_false says "clear() returns False
  when stdout is not a terminal" (observed: night 163 `criteria`).
- The reading. The design was built for a loss of behaviour. A rewrite is
  not a removal by that design (reasoned). The frame's own later commit
  says so: 25fa18ef, "Under one owner, a statement is now dropped when
  the count of its AST kind falls, and rewritten when the count holds",
  and "The price shapes of review 5 now read as rewrites, so their tests
  expect no note" (observed: commit body).
- What tells them apart, in the data the door has:
  - The token sets cannot. `{"return"}` is a subset of `{"return",
    "False"}`, and also of every other `return x` in a file. That is why
    the floor exists.
  - The AST can. s340: the `If` and `Expr` counts under `version_option`
    fall by seven. s221: the `Return` count under `clear` holds.
  - The item and criterion text name the owner `clear` and the value
    "False". They hold no removal verb. A text match on "returns False"
    to `return False` is possible but fits one case (reasoned).
  - The note text says "removes or rewrites 1 statement". The note
    itself does not say which.

## 3. The keep route

- The text. `_note_routes` at `api.py:19865-19879`: "To keep the change,
  send msg.escalate_architect and name the change to the Architect." It
  is a fixed string. It does not read the seat's mode.
- The entry. `git log -S"send msg.escalate_architect and name the"` gives
  2acc7b5c (2026-10-23 13:14), "a removal of a base statement lands on the
  batch's own ruling", pass 2 of W1 a, with the words "Or send
  msg.escalate_architect and name the removal". The words "To keep the
  change" came in pass 5c, c49fcf7c, reverted at f8d3ab64 and landed again
  as bb863f14 (observed: `git log -S"To keep the change, "`).
- The tool lists. `rota/roles/prompts/developer/batch_start.tools` and
  `verdict_failed.tools` do not list `msg.escalate_architect`. It is in
  `exhausted`, `finding_violated`, `findings_exhausted`, `tests_failing`
  and `touch_mistaken` (observed: grep). `mode_tools` in
  `rota/roles/prompts.py:148` reads the mode's `.tools` file. Its
  docstring says "a mode file cannot widen a role's power ... mode scoping
  is purely about not putting eleven functions in front of a model".
  `toolproto.py:1962` refuses any other call: "is not in this role's
  working set". The tool lists have not changed since b00aaa59.
- The check that missed it. Review 5, point 4: "The price holds ... The
  Developer keeps the edit only by the escalation." Low 4's re-probe:
  "The route still exists. `msg.escalate_architect` is in the Developer's
  `tests_failing` tools" (observed: `plans/frame283-review-5.md:36,60`).
  The pass 5 status line of 08:23 named the shape as open: "a whole-file
  write that rewrites one short line inside a kept definition now opens a
  note and blocks the next commit, frame 140's price moved to whole-file
  writes".
- The cause. The absence is a gap, not a deliberate withholding. No
  ruling or status line withholds escalation from `batch_start`. The
  route was checked in the wrong mode. The text also breaks the frame 135
  law in `plans/operating-facts.md:362`: "name another call only where
  the door itself then admits that call". `_offer` (`api.py:288`) and
  `_escalation_admitted` (`rota/core/sandbox.py:1728`) exist for that
  law, and `_note_routes` uses neither.

## 4. The count, nights 160 to 163

Refusals are counted as the most refusal sentences in one turn's input
per Developer session. This is an estimate, because a turn's input holds
the history. The note rows are the last state per batch and path.
"Restored" means a later write of the same session held the line again.

| Night | Refusals, sessions | Note | Dropped lines, tokens | Asked by item or criterion | Shape |
|---|---|---|---|---|---|
| 160 | about 7, 3 (s189, s191, s197) | bg_2 `confirm` | `prompt = _build_prompt(` 2, `while True:` 2, `if abort and not rv:` 5 restored in 11 of 17 writes; `return rv` 2, rewritten | no | s340, a loss, with one short rewrite |
| 161 | about 18, 7 | b_1 `echo_json`, b_3 `confirm`, b_5 `version_option` | b_1: `if file is None:` 4. b_3: 7, `break` 1, 5, 2. b_5: 10 lines, 9 of 3 or more | no | s340. b_5 drops the same `kwargs` lines as s340 |
| 162 | about 16, 5 | b_2 `confirm` tail drop, b_3 `version_option` | b_2: 7 lines after `break`, 2 to 5 tokens. b_3: `if not param_decls:` and 4 `kwargs` lines | no | s340 |
| 163 | about 39, 12 | bg_1 `format_filename`, bg_2 `clear` | bg_1: `if shorten:` 2, `if isinstance(...)` 4, `return filename` 2, restored. bg_2: `return` 1, rewritten as `return False` in 17 of 17 writes | bg_1 no; bg_2 yes, the item and c2 | bg_1 s340; bg_2 W1 |

So about 80 refusals over four nights. Every note but one is s340's
shape: lines that left the function, which a later write put back
verbatim. Only bg_2 on night 163 is W1's shape. In it, every write holds
the rewrite and none holds the bare line (observed: the code.write texts
in `turns.completion`). The one-and two-token lines on nights 160 to 162
travel inside multi-line losses, so a short-line rule changes none of
those refusals (reasoned).

## 5. The repair

- The change. Run 25fa18ef's per-owner AST kind count in the span branch.
  Under the owner, a statement is dropped when the count of its kind
  falls, and rewritten when the count holds. Put it in `_drop_note` or
  after it, beside the existing call of the whole-file branch
  (`api.py:21524-21580`). It rests on the second reading of question 2:
  a rewrite is not a removal.
- Why s340 still fails. Its seven statements each lose their kind count,
  as the 25fa18ef body says: "Night 154's s340 shape keeps its note and
  its refusal".
- The route. Make `_note_routes` name `msg.escalate_architect` only where
  `_escalation_admitted` and the mode's tool list admit it. Otherwise
  name the write route alone. Adding the tool to `batch_start.tools` is
  the other option, and it widens the seat's power (reasoned). That needs
  a ruling and a re-record.
- The red tests:
  1. s221 t13: the span write of lines 601 to 613 that writes
     `return False` over `return` under `clear`, then the commit. Today
     the commit is refused. After the fix the commit lands and no note
     opens.
  2. s252 t8: the refusal names `msg.escalate_architect` in a
     `batch_start` session, and the call is refused with "not in this
     role's working set". After the fix the refusal names no call that
     the mode does not hold.
  3. Keep green: s340 turn 14 and s388, refused.
- Other signs, if a token rule must stay. A 1 to 1 replace pair in the
  diff of the span, where the new line starts with the old line and a
  space. The same AST node type at the same index of the owner's body.
  The kind count is the general one of these and is already built and
  reviewed (reasoned).

## Usage

About 75k tokens in and 9k out, an estimate. No sub-agents.
