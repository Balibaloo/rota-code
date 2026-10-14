# Frame 240, the scope read: why the contested tick's quarantine outlived the approve

Read by an agent on Opus 5.5, 2026-10-14, at commit 91e754d6, for session
4a757f92. Read only. The database is `.rota/clickI_night147.db`, opened
`mode=ro`. The workflow of the fault is the rota workflow (the seats). The
workflow of the fix is the meta workflow (the build session).

## 1. The answer

The principal's approve at m148 reached the `items` row through a raw
`UPDATE` in `principal.land`, which never calls `_lift_quarantines`. The
one pipeline write after it, relay session s303, set `approved` over
`approved`, so `_subject_moved` read false (observed: the queries in
section 2, and `rota/roles/principal.py:1915-1924`).

The quarantine came first. The approve came after it. Nothing between the
two lifted the key.

## 2. The chain, in dispatch order

The `messages` and `sessions` tables carry no clock. The order below is
`sessions.seq` and `messages.seq`, which is commit order. The night log
dates the window: `do:cancel` at 17:08 and walk 2's end before 17:23
(observed: `.rota/night147.log` lines 140 to 161).

1. s285 (relay m136) admitted `problem.set_approval(id=
   'defines_commands_and_options', approval='contested')`. The item went
   `approved` to `contested` (observed: `tool_calls` s285 seq 5, `receipts`
   s285 `items` v24).
2. s287 and s288 ran `tick:contested` on the item. The key
   `vision_keeper|tick:contested|defines_commands_and_options` reached 2
   attempts (observed: `sessions` 287, 288).
3. s290 ruled the principal's m140 answer ("please leave it as it is")
   `contest`, ruling r_501a8b541b. `land` wrote `contested` over
   `contested`, a no-op. s291 (relay m141) set `contested` three times, no
   move (observed: `rulings`, `tool_calls` s291).
4. s292 ran `tick:contested` again. `note_dispatch` in `loop.py:303`
   counted it before the session, so the key read 3 attempts.
5. The next step's `frontier` ran `quarantine_overrun`
   (`scheduler.py:1374`, `2265-2282`). The key went `quarantined=1` before
   s293 dispatched (reasoned: the call order in `frontier` and the loop's
   one session per step).
6. s294 (relay m143) called `problem.set_approval(... 'approved')` three
   times. The door refused all three: "defines_commands_and_options is
   contested at version 1, and no verdict of the principal approved it".
   Its receipt (v26) came from `problem.prioritize`, a `priority` write.
   `_subject_state` compares `version`, `approval` and `status` only, so
   `moved` read false and the lift did not fire. That is correct (observed:
   `turns` s294 seq 6).
7. s299 (Liaison, `tick:quarantined`, detail "1 abandoned: contested for
   defines_commands_and_options (vision_keeper), 3 attempts") reported the
   key and wrote the page m148 (observed: `sessions` 299, `tool_calls`).
8. The principal answered m149 and m150. Ruling r_6ba5a57257 on ask m148
   holds `"defines_commands_and_options": "approve"`, status `landed`,
   verdict m150 (observed: `rulings`).
9. `land` wrote the state at the keypress: `UPDATE items SET approval =
   'approved', approval_ver = version WHERE id = ? AND approval IS NOT ?`.
   The row went `contested` to `approved`. This is a raw write. No
   `Write`, no `session_commit`, no `_lift_quarantines` (observed:
   `principal.py:1915-1924`, and the map: "land (raw)").
10. s303 (relay m152) called `problem.set_approval(... 'approved')` and
    `problem.prioritize`. The row was already `approved`, so `before` and
    after match and `_subject_moved` returned false. The lift did not fire.
    This is frame 80's rule working as designed (observed: `tool_calls`
    s303, `receipts` s303 v28, `db.py:554-570`).
11. Walk 2's end and walk 3's end both read the row through
    `render_state` (`principal.py:409-415`): "Stuck. The team gave up on:
    contested for defines_commands_and_options" (observed: log lines 160
    and 188). The end state is `items` `approved` v1 and `tick_attempts`
    `attempts 3, quarantined 1, reported 1` (observed).

The walk-2 line was already false, so the false line reached the
principal twice, not once.

## 3. The write path of the approve

| Step | Function | Table | Row | Through the pipeline | Lift |
|---|---|---|---|---|---|
| m148 verdict lands | `principal.land` (`apply_rulings` or `pump`) | `items` | `defines_commands_and_options` | no, raw `UPDATE` | never called |
| m152 relay | `api.problem_set_approval` then `db.session_commit` | `items` | same | yes | called, `moved=False` |

## 4. Why the lift did not fire

- (observed) `land` is the only writer that moved the approval from
  `contested` to `approved`. The map lists it as `land (raw)`. The grep of
  `_lift_quarantines` in `rota/` finds callers in `db.py:841` and
  `boot.py:168` only.
- (observed) The pipeline write after the approve set the value the row
  held. `_subject_moved` returns false on it by design.
- (reasoned) The docstring of `_lift_quarantines` says an approval change
  is an exit. It is true only for an approval change that goes through
  `session_commit`. Since frame 190's design moved the state to the
  keypress, the approval change of a ruling never goes through it.

The same shape was found once before. Frame 87's diff review found that
`reconcile_worktrees` wrote `head_commit` raw, so the lift never ran. The
fix was to call `_lift_quarantines` after the raw write in
`boot.py:168` (observed: commit 4ae68ea7, 2026-09-30).

## 5. The prior rulings the pass must keep

1. Frame 80 (`plans/archive/quarantine-revive-design-2026-09-24.md`): a
   write that sets the value a row already holds moves nothing. Night 91's
   relay approved an approved item three times, and each write revived a
   criteria tick that had given up. The pass must lift only when `land`'s
   `UPDATE` changes the row. The `AND approval IS NOT ?` clause gives that
   fact as `rowcount`.
2. Frame 86's pass 4 review (`db.py:589-592`): a commit never lifts a
   park's quarantine. A ruling write is not a commit, so the `do:park`
   exclusion does not apply. Keep the exclusion untouched.
3. Frame 87 (commit 4ae68ea7): a raw write that is an exit calls the lift
   after it. The pass follows this precedent.
4. Frame 142's design, 2.F (test `test_a_criterion_move_ends_the_rest_and_
   a_bare_lift_keeps_it`): a bare lift with nothing moved keeps a park at
   rest. The park key names the batch (`developer|tick:tests_failing|bg_2`),
   not the item, so an item lift does not reach it.
5. Law 6, in the lift's first comment: only a move revives.

## 6. Pass 1 shape

One edit site: `rota/roles/principal.py`, the loop at lines 1915 to 1924
in `land`.

- Keep the `UPDATE`. Read its `rowcount`.
- When `rowcount` is 1, call `_lift_quarantines(conn, Write("items", ref,
  {"approval": state}, op="update", amends=False), True)`. Import it
  inside the function from `..core.db`, as `boot.py` does.
- Add a comment that cites night 147's key and frame 87's precedent.

The test, red first, in a new file `tests/rota/test_frame240_land_lifts.py`:
seed an item `defines_commands_and_options` at `contested`, a
`tick_attempts` row `vision_keeper|tick:contested|defines_commands_and_options`
at `3, 1, 1`, an open `present` ask that names the item, and call `land`
with `per_item={"defines_commands_and_options": "approve"}`. Expect the
item `approved` and no `tick_attempts` row for the key. Add a second case:
the item already `approved`, the same quarantined row, the same `land`.
Expect the row kept (frame 80). The first case is red on the tree now. The
second is green now and must stay green.

## 7. The risk

- A lift on every `land` call, also with no change, revives frame 80's
  loop. Night 91's criteria tick ran five rounds of ten sessions. The
  `rowcount` guard prevents it.
- The lift deletes every quarantined key whose refs name the item, not
  only the `tick:contested` key. A principal's contest of an approved item
  also changes the row, so it also lifts, for example, a quarantined
  `terminologist|tick:criteria|<item>`. That key then wakes again when
  the item returns to `approved`, at attempt 1 (reasoned: the LIKE
  patterns at `db.py:596-601`). The pipeline lift has the same width, and
  this is the docstring's rule, so the pass keeps it. A narrower variant
  lifts only `%|tick:contested|<id>` and only on `approved`. Choose it
  only if the review finds a key that a ruling must not revive.
- A lift inside `land` runs in the caller's transaction. `land` already
  writes several tables raw in one transaction, so the delete joins it
  (reasoned: no `commit` in the loop at lines 1915 to 1924).
- `render_state` reads every quarantined key. After the fix, a key whose
  item moved goes, and the walk-end line drops it. No other reader of
  `tick_attempts` depends on a key that outlives its item's approve
  (reasoned: the readers at `predicates.py:1647`, `scheduler.py:591`,
  `988`, `1585`, `api.py:11332`, `principal.py:366`, `1165` each read the
  key as "the team gave up", which is false once the item moved).

## 8. Tokens

About 60k of context in this read, one agent, no sub-agent.
