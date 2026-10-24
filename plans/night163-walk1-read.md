# Night 163, walk 1: the read of bg_1's failed verdict, the stuck, and walk 3's page

Read-only, on Opus, from the live `.rota/clickI.db` and `.rota/night163.log`,
2026-10-24. Brief: `n163_walk1_brief.md` in session e7141541's scratchpad.

## Verdict

1. The Critic's fail is right by the door and wrong by the request. The
   door refused a pass because the line for c_1 was not an added line.
   That refusal is correct. The cause is criterion c_1, "format_filename
   returns os.path.basename(path) when shorten=True." A docstring-only
   change can never add a line that meets c_1. This is not frame 311's
   sign: the docstring line for c_2 was accepted each time. Frame 306.
2. The stuck: `developer|tick:verdict_failed|bg_1` was quarantined after 3
   attempts. His approve at m35 landed no verdict, because `land` returns
   None on an all-approve page with a built batch. Nothing moved, so
   nothing lifted the key. Frame 312 (the ruled lever, not built), widened.
3. Walk 3's lines 3 to 6 are item 1's own rows: the item, its guess, c_1
   and c_2. The Vision Keeper's signoff submit put `format_filename_example`
   on the page. This is not the agenda path of frame 316 and not 5758cc46
   at work. It is a second path to the same sign. Frame 316, widened.
4. The cancel came from his contest at m49. The contest set the item to
   `contested`, and the `cancel` predicate abandons a batch whose item is
   not approved. His m35 words reached the transcript and the ruling row
   only. Frame 316 (the "take them off this page" half), with frame 312.

## 1. The verdict

Three Critic sessions reviewed bg_1, all on `tick:review`, model qwen3.5:9b.

| Session | Turns | Calls | Commit | Result |
|---|---|---|---|---|
| s125 | 9 | 17 | df80e1c3 | fail on c_1 |
| s127 | 7 | 10 | 1ecbb9b8 | fail on c_1 |
| s131 | 8 | 11 | 40480656 | fail on c_1 |

Total: 24 turns and 38 calls. The Developer sessions s126, s128, s129,
s130, s132, s133 and s134 ran on `tick:verdict_failed` between the reviews.

The criteria under tk_1:

- c_1: "format_filename returns os.path.basename(path) when shorten=True."
- c_2: "The docstring of format_filename includes an example demonstrating
  that a/b/c.txt becomes c.txt with shorten=True."

The diff s131 saw (turn 1), cut to the change:

```
+    .. versionadded:: 8.0
+        Added the ``shorten`` parameter.
+    .. versionchanged:: 8.1
+        The docstring now includes an example ...
+    Example:
+        >>> format_filename("a/b/c.txt", shorten=True)
+        "c.txt"
     """
     if shorten:
         filename = os.path.basename(filename)
@@ -479,8 +492,6 @@
     return filename
-
-
 def get_app_dir(...)
```

The door's refusal, s131 turns 2 and 3, the same in s125:

> ERROR verdicts.emit(batch_id='bg_1'): the line for c_1, 'if shorten:', is
> not an added line of the diff of batch bg_1. Copy one line of the [diff]
> block that starts with +, without the +, and send the pass again. If no
> added line meets c_1, that is a fail on it

The fail verdict s131 wrote itself at turn 3, row
`critic:bg_1:40480656...`:

> Criterion c_1 requires evidence that format_filename returns
> os.path.basename(path) when shorten=True. The diff adds only
> documentation, not implementation code. The existing implementation line
> (if shorten: filename = os.path.basename(filename)) was not added in this
> diff, so there is no added line meeting the criterion.

The diff is right by c_2 and by his words. The diff also deletes two blank
lines before `get_app_dir`, which is a small stray. By c_1 no diff can be
right, because the behaviour already exists. The Critic wrote the fail
itself after the door refused its pass twice. The door did not refuse the
docstring line: each pass carried the `>>> format_filename` line for c_2,
and the refusal named c_1 only. So the sign is not frame 311's.

Cause: c_1 is a behaviour criterion on a docstring-only item. Session s123
(`tick:criterion_repair`, wake "s1 says 'shows' and c_1 says 'returns'.
Both cannot hold.") respecified c_1 three times and kept "returns". His
words at m24 and m29 ("the code does not change") did not reach c_1.
Frame 306, "The principal's words on a page do not reach the criterion".

Side note: s131 called `verdicts.claim_encodes('c_1', encodes=False)` after
its earlier True, and the door refused the reversal. The s125 fail landed
the same way. The Critic then repeated a pass after its verdict landed, and
the runner ended s131 for a verbatim repeat.

## 2. The stuck

The sequence after the fails:

1. The Developer tick `verdict_failed` fired seven times. s126 committed a
   comment, then the docstring. s128 asked the Vision Keeper three times
   and committed nothing. s134 logged ledger row `l_7e7cc4d680`, "The
   existing implementation satisfies c_1, but the Critic rejected it
   claiming the line was missing.", and committed nothing.
2. `tick_attempts` holds `developer|tick:verdict_failed|bg_1` at 3
   attempts, quarantined 1. bg_1 was quarantined on that key, a Developer
   key, not a review key.
3. s135 (`tick:quarantined`, "1 abandoned: verdict_failed for bg_1
   (developer), 3 attempts") presented m35, "The team stopped work on this
   change."
4. m36, his words, became entry `e_m36`. s136 called `rulings.rule` with
   approve on all four lines. Ruling `r_804110d08b` landed with
   `verdict_id` None.
5. s141 (`tick:agenda`, ledger=1) presented m39 on `l_7e7cc4d680`. He
   contested line 5 at m40. The verdict m41 relayed m42 to the Developer.
   s144 ran 5 turns, and its `code.commit` returned "committed: False, why:
   nothing changed". The runner ended s144: "named an act and did not
   perform it".

Why no tick fired: a quarantine lifts only on a moved row
(`_lift_quarantines` in `rota/core/db.py`, about lines 595 to 660). The
batch key lifts on a head commit, a criterion move or a test move of bg_1.
At m35 the approve moved nothing. In `land`, `rota/roles/principal.py`
about line 2081, a page with a built batch drops every approve on the batch
and on the items, and an all-approve rest returns None. The ask was already
closed, so the ruling is "landed" with no verdict and no lift. At m39 the
Developer's commit changed nothing, so no head move. The tick that should
fire is `criterion_repair` on c_1 for the Terminologist, or a restarted
`verdict_failed`. The Developer cannot meet c_1 by any edit.

Frame 312's ruled lever is "an approve on a page whose quarantined key is a
review clears that key". bg_1's key is `tick:verdict_failed`, so the lever
as worded would not cover m35. The lever needs to cover any batch key on a
"stopped work" page.

The line "Stuck. The team gave up on: verdict_failed for bg_1" comes from
the shift-state function in `rota/roles/principal.py`, line 448. It reads
`tick_attempts WHERE quarantined = 1 AND tick_key NOT LIKE
'%tick:constraint_zero%'`, minus keys of parked batches. Walk 2 printed
the same line after 1 step, because nothing had changed.

## 3. Walk 3's page m48

The chain:

1. s149 (Vision Keeper, deliver of m46) wrote item `clear_returns_bool`.
2. s151 (`tick:signoff`, refs `clear_returns_bool`) saw the pre-run
   `problem.consult`, which lists every item, and sent
   `msg.submit_liaison` with six refs: `clear_returns_bool`,
   `defines_commands_and_options`, `format_filename_example`,
   `how_it_works`, `parses_and_executes_inputs`,
   `provides_command_line_interface`. The submit door accepted refs beyond
   the tick's one ref.
3. s152 presented m48 on the same six refs. The ruling `r_9aa589dc0a`
   keys show the page rows in order: `clear_returns_bool`,
   `guess:clear_returns_bool`, `format_filename_example`,
   `guess:format_filename_example`, `c_1`, `c_2`, the four description
   items and `l_1aaeaadd30`.

So lines 3 to 6 are item 1's own rows: the item, its touch guess, and its
two criteria. They are not a ledger row and not the Vision Keeper's
reading of the new item. The Vision Keeper's signoff submit carried item 1
by its id. Frame 316's fix, `8f9e5fd7` ("an agenda page carries the open
rows of one item"), acts on the agenda tick. 5758cc46 only adds
`ledger.list` to the converse mode. m48 is a submit page, so neither fix
was on its path. Cause: the signoff submit takes any item id that
`problem.consult` shows, not only the tick's refs. Frame 316, widened to
the submit path.

## 4. The cancel

At m49 he wrote "Please take lines 3 to 6 off this page and keep only the
clear() work." The ruling turned that into contest on
`format_filename_example`, its guess, c_1 and c_2. `land` set the item to
`contested`. The `cancel` predicate (`rota/core/predicates.py` about line
1536) abandons a live batch whose item is not approved, and
`rota/core/loop.py` line 446 printed "abandoned bg_1: its item is no
longer schedulable". The item lift in `_lift_quarantines` matches keys
ending in the item id, so the bg_1 key stays quarantined in the table.

The contest also relayed m52 to the Terminologist. s156 respecified c_1 and
c_2 with clear() text, "For clear(), the output stays the same and only the
re...", under item 1's ticket tk_1. The live `criteria` table still shows
the old texts, so the respecify may not have landed yet. Frame 315 holds
the nearest sign.

His m35 words, "I don't want to drop this change", reached entry `e_m36`
and the words of ruling `r_804110d08b`. They reached no decision, no ledger
row, no `item_parks` row and no criterion. His "take them off this page"
at m49 reached the item as a contest, which dropped the change he had
asked to keep. Frame 316 holds that half, "take them off this page"
reaches nothing, and here it reached the wrong thing.

## Usage

About 55k tokens in and 9k out, estimated.
