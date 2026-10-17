# Frame 283, review 1 of 6688654b

Reviewer: Opus, read-only, worktree `C:/Users/roman/rota_r283` at 6688654b, 2026-10-17. Meta workflow review of a rota workflow door.

Verdict: does not stand. The store and the step texts are sound. The restore check and the ledger match are prefix and substring tests on at most one line per note part. A seat can pass both with one line. The ledger route that the refusal names cannot close a whole-file note. The count does not see a right commit.

## (a) Verdicts on the points

1. The store: holds. `open_notes` lives on the session's `Ctx`, and `begin_reply` keeps it. No note crosses into another session or batch. A note on path A does not block a commit that leaves A clean, and that is right by the first line. One gap is outside the store: see finding 6.
2. The restore check: does not hold. It passes wrongly in three probed shapes: a twice-held line restored in another function, an unrelated line with the same prefix, and one line of a dropped tail put back.
3. The ledger route: does not hold. One short head such as `echo(` plus the path closes a note of any size. The kinds `invented`, `finding`, `default`, `gap` and `other` close a note. The kinds `fault` and `blocked` close nothing. A whole-file note never closes by this route.
4. Frame 140's tests: the change is intended, and one guarantee is now unguarded. Finding 5 gives the detail.
5. The refusal texts: one call and the next reply hold. The later text claims a route that the code does not give for whole-file notes. The mixed text omits the ledger route.
6. The count: does not hold. `count.py` opens a note only on a frame 140 refusal. Its `right` list is never appended, so it prints 0 by construction. 18 of 26 noted sessions over nights 140 to 154 landed a commit after the note, and the count reads none of them.

## (b) Findings

1. `rota/roles/api.py:15975` `_note_heads`, high, CONFIRMED (observed: probe_tail.py). A tail note names only its first dropped line: "This write drops 4 lines that came after `raise Abort() from None`, from `a = 1`." The heads are `['a = 1']`. A write that puts back `a = 1` alone makes `_restored` True, with three lines still gone. The `_lost_sentence` part names 8 statements at most, and "and N more" adds no head (observed: probe_helpers.py P5, 8 heads of 11). Fix: store the dropped lines from `_tail_drop`'s `gone_out` and `_lost_statements` as data in the note entry, and check each line.
2. `rota/roles/api.py:15981` `_head_count`, high, CONFIRMED (observed: probe_helpers.py P1 and P2). The count is a prefix match on any line of the file. `return x` dropped from `a()` and written again into `b()` passes. The S282 head `echo(` is satisfied by an unrelated `echo(something_else)`. Fix: compare the dropped lines in their enclosing definition, for example by the qualified name of the statement's parent function.
3. `rota/roles/api.py:15985` `_restored` and `:15960` `_close_logged_notes`, high, CONFIRMED (observed: probe_helpers.py P3). The whole-file note of `_whole_drop` reads "from `def b():`; write the whole file again". The regex wants "`." so `_note_heads` returns `[]`. With no heads, any write that changes the file closes the note, even a one-line comment. A ledger note can never close it, because `any(...)` over no heads is False. The later refusal still tells the seat to log the removal. Fix: parse the `from `x`;` form, or store the heads as data, and close a headless note by the ledger path match alone.
4. `rota/roles/api.py:15964`, high, CONFIRMED (observed: probe_helpers.py P6). The ledger match is `h in assumption` on any one head. "src/click/decorators.py keeps one echo( call for the version." closes the S282 note of three statements. The text need not name a removal. A text that says a line was restored also closes it. Fix: require each named head in the assumption, or one head of 12 characters or more and a removal word. Ask Roman whether a note must name every line (rated medium).
5. `tests/rota/test_frame140_commit_beside_note.py:263` and `:297`, low, CONFIRMED (observed: the diff). Before, `test_s282s_commit_beside_the_noted_write_is_refused` proved the refusal and that the next-reply commit lands. Now it proves the refusal only. Before, `test_the_commit_in_the_reply_after_the_noted_write_lands` proved that a read note lets the seat decide. Now it proves the reverse, s388's refusal. The reversal is the pass 1b ruling. No test now proves that a note on path A lets a commit with only path B dirty land. No test proves that a changing write that leaves the lines gone keeps the note open. Fix: add both tests.
6. outside: the session boundary, `rota/core/sandbox.py:717`, high, PLAUSIBLE (reasoned: `Ctx` is built per session, and `open_notes` starts empty). The noted text stays uncommitted in the batch worktree when the session ends. A retry session on the same batch starts with no open note. Its commit lands the removal with no note, which is s388's shape across a session. Fix: persist the open note per batch and path, or read the worktree diff at the first commit of a session.
7. `rota/roles/api.py:15944`, low, CONFIRMED (observed: the code). When a reply note and a later note are both held, the text joins both under "your code.write in this reply returned a note". Its step names only the write-back route. A seat with a meant removal of the later note does not read the ledger route. Fix: append the later step when `later` is not empty.
8. `count.py` in the pass scratchpad, high, CONFIRMED (observed: probe_exposure2.py, nights 140 to 154). The script opens a note only after a frame 140 refusal. It never appends to `right`. The new door acts on every `dropped` note, refused or not. 26 sessions got a `dropped` result, and 18 of them landed a commit after it. Examples: s369 night 142, s453 and s464 night 146, s314 night 151, s379 and s381 night 154. Each is a candidate right commit that the new door may refuse. Fix: re-run the count over those 18 sessions with `_restored` and `_close_logged_notes` applied to the turns. Report how many commits the door now refuses and how many of those were meant removals.

## (c) Probes

All probes are in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/0e37e9d7-d362-4c19-b149-990e66307aba/scratchpad/f283r1/`. They ran from the worktree root with the checkout's venv.

- `probe_helpers.py`: calls `_note_heads`, `_head_count`, `_restored`, `_close_logged_notes`, `_whole_drop` and `_lost_sentence` directly. P1 twice-held line, P2 prefix head, P3 whole-file note, P5 more than 8 statements, P6 ledger match.
- `probe_tail.py`: builds a real tail note with `_drop_note`, and puts back one of four lines.
- `probe_exposure2.py`: reads `clickI_night140.db` to `clickI_night154.db` read-only. It lists sessions with a `dropped` result and the commit shas that first show after that turn.
- `probe_exposure.py`: a first version with a wrong result format. Its output is void.
- A `python -c` read of s340's turns on night 154 that showed the commit result format.

## (d) Usage

Estimate, because the agent cannot read its harness line: about 90k input tokens, 12k output tokens, about 102k total. The cap was 40k. The night reads and the code reads put the review over the cap. Read the harness line for the true number.
