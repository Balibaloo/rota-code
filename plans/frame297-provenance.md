# Frame 297, cycle 1: the provenance read and the count

Read-only agent on Opus, 2026-10-18, for session c32575f3, brief
`f297_provenance_brief.md` in that session's scratchpad. Rota workflow for the
records read, meta workflow for this read. Databases: `.rota/clickI_night140.db`
to `.rota/clickI_night156.db`, read in the checkout on `rota/foundation`.

Result first: s214, bg_2's own batch-start Developer, wrote `l_cab4458639` in
turn 10, after the fourth refusal of its commit by frame 283's door, from a tree
that held its own uncommitted write. The frame's heading is wrong on the writer,
the wake and the order. Over nights 140 to 156, 75 ledger notes match the scope:
22 of class (a), 3 of class (b), 1 of class (c), 49 of class (d). The one class
(c) note reached a page. A door that refuses a note about a reading call on a
path that `_uncommitted` lists refuses that note and no other of the 75.

## 1. Who wrote `l_cab4458639`

**s214 wrote it, in turn 10, from bg_2's worktree with its own uncommitted
write of `version_option` in it** (observed: `tool_calls` seq 24 and `turns`
seq 10 of s214, `.rota/clickI_night156.db`). The `ledger` table has no session
column. Its row is `('l_cab4458639', 'src/click/decorators.py', 'code.source',
'The file already contains the show_python logic at lines 543-546; no write is
needed. The criteria are satisfied.', 'default', 'resolved', 'developer', 1)`
(observed: `ledger`). The call in the completion of s214 turn 10 is copied here:

```
TOOL: ledger.log(about_ref='src/click/decorators.py', about_table='code.source', assumption='The file already contains the show_python logic at lines 543-546; no write is needed. The criteria are satisfied.', kind='default')

TOOL: code.commit(message='Add show_python flag to version_option')
```

The text is in the completion of s214 turn 10 and in no other completion
(observed: a `LIKE` search over `turns.completion`). The other hits, s236 to
s239, hold it in their `user` text, as a resolved ref (observed: the same
search on `user`).

s214 is `developer`, `wake_kind` `tick:batch_start`, `wake_refs` `["bg_2"]`
(observed: `sessions`). The order of its calls (observed: `tool_calls` and the
runner's account in s214 turn 11):

1. Seq 13, `code.write` at 420 to 558, landed with a note: `"dropped": "This
   write removes 1 statement that your text does not hold: `echo(` at line
   543.", "written, not committed": ["src/click/decorators.py"]` (observed:
   s214 turn 7 `user`).
2. Seq 15, the first `code.commit`, refused with the same-reply text: "your
   code.write in this reply returned a note before this commit, and you had not
   read it."
3. Seq 17, a `code.write` at 540 to 637, refused by the span door. Seq 18, the
   second commit, refused with frame 283's text: "Put the lines back with
   code.write, or log the removal with ledger.log naming the path and the
   lines, then commit in your next reply."
4. Seq 19, a `ledger.log` of kind `fault`, "The write removed `echo(` at line
   543 ...; I will restore it.", went to the faults route, `f_e1ab020c98`, with
   "End the session." (observed: s214 turn 8 `user`). It is no ledger row.
5. Seq 20, a `code.write` refused as invalid Python. Seq 21, the third commit,
   refused with frame 283's text.
6. Seq 22, `code.source` at 420 to 568. The result shows the seat's own write:
   `show_python: bool = False,` and `if show_python:` in `version_option`
   (observed: s214 turn 9 `user`). The read before the write, in turn 3, holds no
   `show_python` (observed: `user` of turns 3 and 4).
7. Seq 23, the fourth commit, refused with frame 283's text, and the note
   "code.commit has been refused the same way in three turns and will not be
   accepted again" (observed: s214 turn 10 `user`).
8. Seq 24, `l_cab4458639`. Seq 25, the fifth commit, refused. The account ends
   "code.commit was refused the same way in four turns; the session ended on it".

So the brief's list is right except for one order: the note came after the
fourth refusal, not after the third, and s214 sent five commits, all refused
(observed: the account). No commit of s214 landed, so the lines the note names
are the seat's uncommitted lines. In the read of seq 22, `if show_python:` is
about line 552, not 543 to 546 (reasoned: a count of lines from
`def version_option` at 420, so the numbering can be off by a few).

s242 never read `decorators.py` (observed: its `tool_calls`, 25 calls, no
`code.source`). Its `batches.expect` returned `{"note": "this session works in
no batch"}` and its `code.diff` returned `{"batch": null, "error": "no
worktree"}` (observed: s242 turn 1 `user`). It wrote `src/cli/version.py` at
seq 18. Its trigger is m128, a relay of m126, the verdict, not of m125
(observed: `messages.cause_id`). The Liaison s236 put `l_cab4458639` on m122 as
one of four refs (observed: s236 turn 1 completion and `wake_refs`).

The heading and the site are wrong (reasoned: the facts above):

- Wrong: "A Developer woken by a relay after a batch-start quarantine reads the
  quarantined write". The writer is the batch-start Developer, before the
  quarantine. s217's `tick:quarantined` wake came after s214, s215 and s216
  (observed: `sessions`).
- Wrong: "the principal asked at m124". He asked at m123, "For line 8, where is
  that existing Python version code from, since I don't think anything in the
  code shows it yet?". m124 is the Liaison's question back to him (observed:
  `messages`).
- Right in part: the site's ledger note door. The note landed because
  `ledger_log` reads no tree (section 3). The batch-start quarantine is not the
  site: a reset at the quarantine comes after the note, so it cannot stop it.
- A true heading: "A batch-start Developer whose commits the removal door
  refuses logs its own uncommitted write as the file's existing code, and the
  page asks the principal about it."

One fact beside the frame: s215, the second batch-start attempt, met s214's open
note at its first commit, "This write removes 1 statement that your text does
not hold: `echo(` at line 543", before it wrote anything (observed: s215 turn 5
`user`, `tool_calls` seq 9). So bg_2's worktree kept s214's uncommitted write
into the next session. Law 4 says "A worktree with uncommitted changes at
session end is a fault. The uncommitted change never existed" (observed:
`rota/LAWS.md:169-171`).

## 2. Provenance of the refusal text the seat followed

**No ruling of Roman made a ledger note the discharge of a removal. The holding
sessions reasoned it from frame 283's ends-when, and no review asked whether a
note that does not name the removal lands and reaches a page** (observed: the
stack, the reviews, and `plans/frame287-roman-words.md`, which holds no word of
his on 2026-10-17 17:00 to 19:00 and no word on a ledger note for a removal).

The chain, each step from `plans/stack.md`, frame 283, unless named:

1. 2026-10-17 16:40, session 0e37e9d7 (rota-7d), meta workflow. The frame is
   pushed from `plans/night154-read.md` with the ends-when "a commit whose tree
   removes a statement that no landed note names is refused". The word "note"
   is not defined there (reasoned: frame 140's ends-when, read for this,
   names only the `dropped` note of `code.write`, and no ledger row).
2. 17:30, the same session. Pass 1b's open question, "a seat whose item asks for
   a removal has no way to commit it, is answered by this frame's ends-when: a
   landed note names the removal". Pass 1c is sent: "a `ledger.log` of the
   Developer's mode that names the path and a dropped statement closes the note,
   the refusal names both routes".
3. 17:32, commit 6688654b, "a dropped note stays open until the lines return or
   a ledger note names the removal" (observed: `git log -S"log the removal with
   ledger.log" -- rota/roles/api.py`). 17:33: a note in the same reply closes it,
   "frame 140's own reasoning".
4. 17:37, review 1, finding 4, came closest to the question: "The ledger match
   is `h in assumption` on any one head ... The text need not name a removal. A
   text that says a line was restored also closes it." (observed:
   `plans/frame283-review-1.md:21`). Judged the same hour: "the ledger match is
   decided here as every dropped statement's text or the whole definition's
   name, and not asked". 17:44, abd3caf4.
5. 18:04 to 18:13, session d7c5dc6d (rota-c1). Review 3, finding 2: a ledger
   cannot close a note whose refusal shows part of the lines. Pass 4: one shown
   line closes the note.
6. 18:19, review 4, point 4: "A ledger that quotes the refusal text back with
   the path closes any note with no restore (observed: probe PARROT) ... The
   first matches the frame's intent: the landed note is the seat's word, and the
   Architect reads it." Finding 3: "Pass 4 deviation 2 records this as
   reasoned, not ruled. Fix: ... or get a ruling." (observed:
   `plans/frame283-review-4.md:11,19`). Judged at the pass 5 line: "the third
   low accepted as the intent, one shown line is the seat's word and the
   Architect reads the landed note".

The docstring of `_close_logged_notes` says "the Architect's judgement reads the
landed note (review 4, finding 3, ruled)" (observed: `rota/roles/api.py:16870`).
The record shows a session's judgement and no ruling of Roman (reasoned: step 6
and the grep of the words page). The word "ruled" in the docstring is wrong.

No review asked the brief's question (observed: a search of
`plans/frame283-review-1.md` to `-7.md` and `plans/frame283-count.md` for
"page", "Liaison", "agenda", "principal" and "uncommitted"; the hits name
worktrees and the retry session only). Every review tested whether a note closes
the dropped note. None tested what the note claims, or where a note of kind
`default` goes. Review 4 assumed the Architect reads it. Frame 204's design sends
a `default` to the principal: "Owed to the principal | `default`, `scope`"
(observed: `plans/frame204-design.md`, the table after line 363). So the route
was: the refusal invites a note, the seat writes a `default` about the path, the
ledger door admits it, and the agenda puts it on the page.

`l_cab4458639` did not close s214's note, because its text holds no `echo(`
(reasoned: `_close_logged_notes` needs one shown line). It landed and reached a
page all the same.

## 3. Provenance of the ledger door

**The note route of frame 204 did not consider a note about a path whose tree
holds the seat's own uncommitted lines** (observed: `plans/frame204-design.md`,
2026-10-11, a design pass on Opus for session c81dd240, rota workflow, committed
in b46a6513 at 16:02).

- `ledger_log`, `rota/roles/api.py:10554-10744`, refuses on the kind, an echo of
  a refusal, the table and ref pair, a ledger self-ref, a misplaced text and
  more. It never reads the tree: no `worktree`, `_uncommitted`, `changed_since`
  or `git` in its body (observed: a grep of the function's lines). Its only
  reader of the drop notes is `_close_logged_notes` at the end, line 10743
  (observed: `rota.tools.map fn _close_logged_notes`).
- A path as `about_ref` has no home table, so `about_table='code.source'` passes
  the pair check (reasoned: lines 79 to 115 of the function refuse a rota row
  under another table's name, and a path is no rota row).
- Law 4 says an uncommitted change never existed (observed:
  `rota/LAWS.md:169-171`). `code.diff` applies it at `api.py:13893` with
  `_uncommitted` at `api.py:14002-14011`, and returns `"not committed"` with
  `"lands with": "code.commit"`. `_code_write` and `_unread_drop_refusal` call
  `_uncommitted` too (observed: the map tool, 4 callers). `ledger_log` does not.
- Frame 204's design has one paragraph on a path note: "`ledger.log` admits a
  path or an `@area` as `about_ref` ... Such a row reaches no item. It belongs to
  the batch of the session that wrote it, by the park's route" (observed:
  `plans/frame204-design.md:363`). It decides where the note belongs, not what
  it may claim. Its corpus row for a scope change is a claim about the code, "The
  confirm function does not exist in the current codebase", and the design
  routes it to the Vision Keeper with no check on the tree (observed: line 82).
  The word "uncommitted" appears only in its header, about the build session's
  own checkout (observed: lines 4 to 8). No frame 204 review uses the word
  (observed: a grep of `plans/frame204-*.md`).

## 4. The count

Scope: every ledger row on nights 140 to 156 with `about_table` in
(`code.source`, `code.probe`, `code.diff`) or a path as `about_ref`. 75 rows
match. One row only has a reading call as `about_table`: `l_cab4458639`
(observed: the scan script `f297/cand.py` in session c32575f3's scratchpad).

The method. The session is found from the `ledger.log` call in `tool_calls` that
carries the ref and the text's head. "Write before, no landed commit" reads the
session's `tool_calls` order and the `head_commit` values and `ERROR
code.commit` lines in its `turns.user` text. A page is a `messages` row whose
`body_refs` names the id.

48 rows are the Vision Keeper's notes on `docs/*.md` from the README survey, on
nights 140, 141 and 142. No Vision Keeper session writes code, so each is class
(d) (observed: `author` `vision_keeper`, `about_table` `items`).

The 27 Developer rows:

| Night | Id | Session, batch | Path | Write before, no landed commit between | The text | Class | Page |
|---|---|---|---|---|---|---|---|
| 141 | l_6ba7fe72ef | s197, bg_2 | termui.py::confirm | no, the note comes first | a plan, "I will add" | a | none |
| 142 | l_ee13aac8ba | s143, echo_json_batch | tests/test_utils/test_echo.py | the write was refused | "I cannot write to test files directly" | d | m296, m297 |
| 142 | l_c572091285 | s367, batch_1 | termui.py::confirm | no, first | a plan | a | m296, m297 |
| 143 | l_c1040dd2ec | s308, bg_2 | termui.py::confirm | no, first | the current code, then a plan | a | m252, m253, m257 |
| 143 | l_ef5f059a2c | s521, bg_6 | decorators.py::version_option | no write | a plan | a | none |
| 144 | l_f9fefca033 | s438, bg_4 | tests/test_utils/test_confirm.py | no, 4e79574e landed first | "I rewrote the test file", a change the seat made | a | m410, m411, m413 |
| 144 | l_5e4283d9a9 | s538, bg_5 | decorators.py::version_option | no write | a plan | a | m410, m411, m413 |
| 144 | l_3ac5ea7478 | s540, bg_5 | decorators.py::version_option | no, first | a plan | a | m410, m411, m413 |
| 144 | l_b1c8519102 | s540, bg_5 | decorators.py | a write, and the commit said "nothing changed" | "sys is not imported", then a plan | a | m410, m411, m413, m419 |
| 144 | l_deed69a92f | s567, bg_5 | decorators.py | no, a9cbdcd1 landed first | "I initialized package_name=None", a change made | a | m422 to m425 |
| 145 | l_74a468c9e7 | s373, bg_4 | decorators.py::version_option | no, first | "does not have this parameter", a plan | a | none |
| 145 | l_25f64ba579 | s373, bg_4 | decorators.py::version_option | no, f63f6830 landed first | "Added sys import", a change made | a | none |
| 147 | l_3f960dc5a4 | s236, bg_2 | termui.py::confirm | no, first | a plan | a | none |
| 147 | l_403e23cefb | s236, bg_2 | termui.py::confirm | no, first | a plan | a | none |
| 148 | l_9804869709 | s122, bg_1 | src/click/utils.py | no, 2612bb84 landed with `echo_json` | "already contains a definition of echo_json at line 688", true of the commit | a | none |
| 148 | l_7f222a7b0d | s122, bg_1 | tests/test_utils/test_echo.py | the writes were refused | "already ends at line 172", true of the commit | a | none |
| 148 | l_fb69e196da | s122, bg_1 | tests/test_utils/test_echo_via_pager.py | the writes were refused | "already ends at line 259", true of the commit | a | none |
| 148 | l_72d52736d2 | s153, bg_2 | termui.py::confirm | no, first | the current code, then a plan | a | none |
| 150 | l_9a2281b344 | s150, batch_2 | src/click/utils.py | yes, no commit landed | a plan, "I will add a comment" | a | m66, m67 |
| 151 | l_5ccbe7600e | s322, bg_4 | decorators.py::version_option | no, first | a fact of the code, "prog_name is a nonlocal variable" | a | none |
| 153 | l_ed11a8e73e | s246, bg_3 | decorators.py::version_option | no, first | "The existing version_option callback already has access to ctx", then a plan | a | none |
| 154 | l_ddf15bd84a | s351, b4 | decorators.py | yes, no commit landed | "restored ... removed show_python implementation", a change made, before frame 283's door | a | none |
| 156 | l_475aa1d45f | s162, bg_1 | termui.py::confirm | no, first | a plan | a | m112, m113 |
| 156 | l_cab4458639 | s214, bg_2 | decorators.py | yes, 5 commits refused | "already contains the show_python logic at lines 543-546; no write is needed", the seat's own uncommitted lines as the file | **c** | m122 to m125 |
| 156 | l_8c98565350 | s215, bg_2 | decorators.py | no own write; the tree held s214's write and its open note | "removed echo(msg, color=ctx.color) and ctx.exit()", after frame 283's refusal | b | m122 to m125, m128, m131 to m135 |
| 156 | l_c32d84a529 | s274, bg_3 | decorators.py | yes, the commit refused | "removed 7 statements", after the refusal of 7 statements | b | m200, m201, m205, m207 |
| 156 | l_012789e813 | s300, message wake | decorators.py | no own write; an open note of bg_3 | "removed logic for version detection and echo", after the refusal of 4 statements | b | m200, m201, m205, m207 |

The totals:

| Class | Notes | On a page |
|---|---|---|
| (a) an honest assumption about the work in progress | 22 | 9 |
| (b) a removal note that frame 283's door asked for | 3 | 3 |
| (c) the tree's uncommitted lines read as the file | 1 | 1 |
| (d) other: 48 survey notes and 1 door statement | 49 | 1 of the 1 Developer note, m296 and m297; the survey rows not read |
| All | 75 | |

The (c) note reached m122, m123, m124 and m125 (observed: `messages.body_refs`).
So 1 of 1 class (c) notes reached a page. The (b) notes did not close their
dropped notes on night 156: s215's commits were refused to the session's end
(observed: s215 turns 5 to 10). The fix ee166261 of 2026-10-18 14:13 came after
the night (observed: the stack, frame 283). The kind `fault` note of s214 seq 19
also named `code.source` on the dirty path. It is in `faults`, not `ledger`, so
the count leaves it out (observed: s214 turn 8 `user`).

The class lines are a reading of each text (reasoned: the brief's four classes).
Two are near a border. l_9804869709 says the file "already contains" a
definition, and the definition is the seat's own committed lines, so it is (a).
l_ddf15bd84a is a removal note on night 154, before frame 283's door, so it is
(a) and not (b).

## 5. The door the count points to

**The predicate: refuse a `ledger.log` of any kind but `fault` whose
`about_table` names a reading call, `code.source`, `code.probe` or `code.diff`,
when `_uncommitted(ctx, worktree, ctx.batch_id)` lists the path of its
`about_ref`** (reasoned: the count). The helper is `_uncommitted` at
`rota/roles/api.py:14002`, the law 4 check that `code.diff` already uses.

On the 75 rows it refuses `l_cab4458639` and no other row (reasoned: section 4,
it is the one row with a reading call as `about_table`, and its path was dirty).
It leaves the 22 (a) and the 3 (b) standing, because none names a reading call.
The three (b) rows and l_ddf15bd84a were on a dirty path, so a predicate on the
tree alone refuses 4 right notes (reasoned: the table). A predicate on the open
drop note and `_close_logged_notes`'s match refuses s274's and s300's (b) notes,
because their texts name no shown line (reasoned: the table and section 2).

The refusal text, one fact and one step:

> `src/click/decorators.py` holds lines that no commit holds, so code.source showed your own write, not the file. Say what your write changes, with about_table naming the criterion it serves.

The first (a) note it would wrongly refuse: a seat that wrote, read its write
back, and logged a plan about what the read showed, for example "code.source
shows show_python at lines 552 to 554; the test comes next", with
`about_table='code.source'`. The count holds no such note (observed: 0 of 75).

The predicate rests on one recorded case, so the overfitting risk is high
(reasoned: the rule of 2026-10-15 01:54, "I want to prevent over fitting"). The
general cause the case shows is wider: no door compares what a note claims with
law 4. The count gives no second case to test a wider door on. Two residues
stand beside the door. The docstring of `_close_logged_notes` says "ruled"
where the record shows a session's judgement. bg_2's worktree kept s214's
uncommitted write into s215, against law 4's "A worktree with uncommitted
changes at session end is a fault".
