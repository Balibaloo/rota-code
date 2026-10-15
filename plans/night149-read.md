# Night 149 read: 1 of 2 batches merges, and a Vision Keeper's rewrite of the approved item cancels bg_2 after five contests of one claim

Rota workflow throughout, except where a line says meta workflow. Read on
Opus, 2026-10-15 16:0x to 16:2x by the clock.

Sources:

- `.rota/clickI_night149.db` (255 sessions, 1261 turns) and every
  `.rota/clickI_night1*.db` for the cross-night counts, each opened with
  `file:...?mode=ro`.
- `.rota/night149.log` (179 lines) and `.rota/clickI_night149.principal.jsonl`,
  the 25 rows with `"night": "149"`.
- `plans/night149-cycle1.md`, taken as read. This read extends it to walk 3.
- The tree `C:/Users/roman/rota_night149` at 401bbf3f, read only:
  `rota/roles/api.py` lines 1285 to 1430 (the item-rewrite door), 8355 to
  8383 (`_LINE_REF`), 8468 to 8506 (`_unnamed_contest`), 8754 to 8790 (the
  batch-line door).
- `git show` in `D:/repos/_AI/sample_repos/clickI` and its worktree `bg_2`,
  read only. The worktree `bg_1` is gone, so bg_1 is read from the merge
  aa4b190 and its two parents.
- `rota.tools.nightcount.count` on the night database, read only.
- Scripts in session cd6300cd's `scratchpad/n149/`: `q.py`, `dump.py`,
  `pj.py`, `block.py`, `xcount.py`, `xprop.py`.

Walk boundaries: onboarding is s1 to s99, walk 1 starts at s100 on `m_p1`,
walk 2 at s136 on `m_p2`, walk 3 at s206 on `m_p3` (observed:
`sessions.trigger_msg`).

| Batch | Item | End | Steps, asks, dollars | Wall or cost |
|---|---|---|---|---|
| bg_1 | `echo_json` | merged at walk 1's end, aa4b190 | 44, 6, 0.87 | 4 fault rows, frame 247. The re-annotate kept two declined grains, frame 244 |
| bg_2 | `confirm_default_on_eof` | cancelled at 15:55, "its item is no longer schedulable" | walk 2 82, 8, 1.21; walk 3 63, 6, 1.05 | five contests of one claim; the cycle, frame 254; the cancel, frame 129's door gap |

The brief's facts hold, with three additions:

1. The show_python request reached seats, late in walk 3: s209 (Vision
   Keeper deliver, `problem.assert` of `version_option_show_python`), s252
   (Critic, the claim falsified), s253 and s255 (Terminologist), s254
   (Architect). No page about it reached the principal. The item ends
   `draft`, version 2 (observed: `sessions`, `items`).
2. bg_2 did not leave the schedule through the exhausted ladder. The
   Vision Keeper s232, in propose mode, rewrote the approved item's text,
   and the item went to `draft` (section 1.4).
3. At the night's end, cr_1, cr_2 and cr_4 say "instead of aborting", and
   cr_5 and cr_6 still say "instead of raising a UsageError" (observed:
   `criteria`, the last page in the log).

## 0. The answer in brief

| Frame | Measure | Night 149 |
|---|---|---|
| 243, the declined format merged | merges that carry what the principal declined | 0 of 1. bg_1 carries nothing he declined. bg_2 was cancelled before a merge, with the declined words still in 2 of 6 criteria and its tests in new files he declined three times |
| 243, the seam | the block, the texts, the supersede door | The block reached 31 of 31 Developer and Tester wakes after a contest, longest 9,270 characters, never cut. The texts moved to his words only when a landed ruling quoted the declined phrase, s215. 0 supersede refusals. 3 of 5 replies to bg_2's pages made no ruling row |
| 244, the re-annotate | re-annotates after a files contest that keep a declined file | 2 of 2, s125 and s172, the same as night 148. 1 of 2 blocks lists files he kept. No sign that the sentence changed the 2 plain annotate wakes |
| 245, unresolved after green | unresolved wakes on a green test | 0 of 1. The one wake, s244, named a red test. No Critic challenge to a Tester, so no merge held on one |
| 246, the raw key | pages with a raw tick key | 0 of 1. s89 attested `found` with one landed `gap` note. m11's "line 2" is the note in words: "the prose files are checked", the reverse of the fact it came from |
| 230, the lambda door | lambda or plain-function bodies landed | 0. 10 such bodies were sent and other doors refused them first. 4 sessions met the plain-function branch |
| 254, the stdin door | right bodies refused | 1 of 3 sessions, s197, 4 refusals of one right body. s216's refusal was right. s191's 8 refusals were of wrong bodies, for a wrong fact |
| 239 | re-dispatched batches that merge untested | 0 of 0 |
| 202 | criteria with text and surface apart that reach a Tester encode | 0 of 6 |
| 187 | contested Vision Keeper wakes with every call refused | 0 of 2, s109 and s158 |
| 236 | `touch_mistaken` on a surfaced file | 0 of 0, the third night |
| 204 | note kinds | 3 `conflict`, 1 `gap`, 10 `invented`, 3 `other`, 1 `scope`, 16 `default`. No merge waited on a row |
| 173 | admitted span writes that remove a statement, with a `dropped` note | 2 of 2. s228's commit 6ea9f90 still removed confirm's y/n branch |

## 1. Frame 243, the declined format merged

Frame 243 validates at 7a2cb843. The night ran at 401bbf3f, which holds it
(reasoned: the frame's status line of 14:51).

### 1.1 The ratio: bg_1 against his words

bg_1 merged as aa4b190, "rota: deliver bg_1", with 37a28655 (`src/click/utils.py`,
19 lines) and c3cec221 (`tests/test_utils/test_echo_json.py`, 14 lines)
(observed: `git show`). His words on each page and the merged code:

| Page | His words | Merged code |
|---|---|---|
| m17, m24 | "use only the standard library json module, with no new dependency" | `import json` inside `echo_json`. No new dependency |
| m29 | "the new helper sits next to echo and writes an object as compact one-line JSON" | `echo_json` follows `echo` in `utils.py`. `json.dumps(obj, separators=(",", ":"))` |
| m34 | "keep the change small" | 1 function, 1 test file |
| m38 | "leave echo alone", "add new tests for it next to the echo tests" | `echo` is unchanged. The test sits beside `tests/test_utils/test_echo.py` |
| m45 | "print only the compact JSON on one line and then a newline, with nothing before or after it" | For `obj=None` the helper prints nothing, not `null` and a newline |

Count: 0 of 1 merges carry what he declined (observed: the diff against the
jsonl words). The `None` branch is not a declined format. It is a lost
requirement: s114 sent `criteria.specify` four times under the one id
`echo_json_helper`, and each call replaced the last, so "must end with
exactly one newline ... regardless" and "must handle any valid Python
object" reached no test (observed: `tool_calls` s114 seq 7, 8, 9, 13 to 19;
`criteria` version 4). That is candidate N4, section 11.

bg_2 never merged, so it adds no count. Had it merged, its tests sat in
four new files under `tests/test_utils/`, which he declined at m85, m91 and
m92, "not ... a new test file", and two criteria still held the declined
words (reasoned: `tests`, `criteria` at the end).

### 1.2 The block and the criterion texts over walks 2 and 3

The block `[the principal contested these criteria]` reached every
Developer and Tester wake after each landed contest (observed: `block.py`,
turn 1 of each session):

| Wakes | Rulings in the block | Entries | Characters |
|---|---|---|---|
| s174 to s186, 9 wakes | r_3aa5b4358e (m74) | 6 | 3,772 |
| s191 to s197, 7 wakes | + r_cb56c527ea (m86) | 12 | 7,495 |
| s216 to s231, 15 wakes | + r_80d30c50e6 (m105) | 15 | 9,270 |

The cycle read's figures stand for the first two rows. The third row is
this read's: 15 entries, because r_80d30c50e6 contests three criteria.
s237 to s251 come after the cancel and carry no block. No wake lost the
block's end. Four Developer wakes were cut, s192, s217, s218 and s229, and
each cut fell after the block, inside the `tests.load` rows, at about 17,600
characters (observed: "CUT your wake: 9,790 of 27,372 characters are not
shown" in s217). The block took about half of the shown wake, so it pushed
red test rows into the cut (reasoned: the block starts at about 6,500 and
ends at about 15,800 of 17,583 shown characters).

The texts after each respecify (observed: `tool_calls`, `turns.completion`,
`criteria`):

| Respecify | The words it relayed | Result |
|---|---|---|
| s173, after m74 | "today confirm aborts when stdin is closed, it doesn't raise a usage error" | "UsageError" stays in cr_2, cr_4, cr_6 |
| s190, after m86 | "Lines 3, 5 and 7 still say it raises a usage error when today it aborts" | "UsageError" back in cr_1 and cr_5 |
| s215, after m105 | "Lines 2, 3, 5, 6 and 7 are also wrong to say \"instead of raising a UsageError\"" | cr_1, cr_2, cr_4: "instead of aborting" |
| s235, after m121 | "please change those words to \"instead of aborting\"" | refused: "the principal approved cr_5_confirm_default_on_eof ... Keep the words" |
| s247, s248, after m132 | "Change the implementation, not the line" | refused, the same door |

So the Terminologist moved the text when the landed ruling quoted the
declined phrase and contested the criterion (s215). It did not move the text
where the ruling paraphrased (s173, s190), with the same block in the
Developer and Tester wakes (reasoned: the three rows above; cause 5 by the
cycle read for s190). cr_5 and cr_6 kept the declined words for another
reason: the verdict s212 ruled lines 6 and 7 `approve` against "Lines 2, 3,
5, 6 and 7 are also wrong", and m120's clarify verdict ruled cr_5 `approve`
against "please change those words" (section 7.3, candidate N3, frame 250).

### 1.3 Which replies made a ruling row

| Reply | Page | Ruling row | Why |
|---|---|---|---|
| m74 | m73, touch page | r_3aa5b4358e, bg_2 contest | bg_2 had no head commit, so the batch-line door let the contest pass |
| m86 | m85, abandon | r_cb56c527ea, bg_2 approve | s188 turn 1 contested line 8, met the batch-line door, and turn 2 approved line 8 |
| m92 | m91, abandon | none | s199 sent the same `rulings.rule` three times with line 8 `contest`. The batch-line door refused each: "line 8: bg_2 is the change's line: a prediction of what it touches, and a ruling on it moves nothing. To stop the change, contest the item confirm_default_on_eof, line 1. Otherwise approve line 8". The repeat rule ended the session |
| m96 | m95, signoff | none | s205's right contest of lines 2 to 7 met `_unnamed_contest` five times: "The words name lines 1 to 3, 5 and 8 to 11 and do not name lines 4, 6 and 7". `_LINE_REF` reads "to" and "-" as a range and not "through", so "Lines 2 through 7" named line 2 alone. Turn 6 was prose, and the session ended |
| m105 | m91 again | r_80d30c50e6, bg_2 approve | s212 met the batch-line door, then approved line 8. It also approved lines 6 and 7, which the words fault |
| m106 | m95 again | none | s213 contested notes 8 to 11, which m106 does not name. The door refused that rightly. The seat repeated and was ended. m95 is `open` at the night's end |

3 of 6 replies to bg_2's pages made no ruling row, and 3 of the 3 that did
discarded his files correction on line 8 (observed: `rulings`, `turns` of
s188, s199, s205, s212, s213).

### 1.4 Why bg_2 left the schedule at 15:55

The Architect s230 sent `msg.propose_vision_keeper` on cr_5 and test_cr5,
m118. The Vision Keeper s232 woke in propose mode, authored
`d_5_confirm_default_on_eof`, and then sent:

```
problem.assert(id="confirm_default_on_eof", text="Let confirm() take a default_on_eof flag: when stdin is closed it returns the default instead of aborting. The flag default is passed to confirm itself.", kind="in_scope")
```

The call landed. The item went to version 3, `draft`, and lost "The flag
defaults to False, so nothing changes for people who already call
confirm", which he said at m57, m66 and m70 (observed: `items`, s232's
turns). The cancel followed: "abandoned bg_2: its item is no longer
schedulable" (observed: the log, 15:55).

The door that refuses a rewrite of "the principal's own words" in
`_assert_door` (`rota/roles/api.py` lines 1305 to 1430 at 401bbf3f) fires
for a `challenge` message, a `tick:exhausted` wake and a `tick:contested`
wake. Any other wake returns None at `if wake != "tick:contested": return
None`. A propose wake is admitted (observed: the code). The same door
refused s185's and s203's asserts in challenge mode on walk 2: "is the
principal's own words. A challenge does not rewrite them".

Over every night database, 24 Vision Keeper `problem.assert` calls on an
existing item came from a propose wake, and 7 landed, on nights 119, 124,
127, 130, 133, 146 and 149 (observed: `xprop.py`, 2026-10-15 16:1x). How
many of the 7 rewrote a decided item is not counted, because the item's
provenance at the call is not kept (reasoned).

This is frame 129's sign, "A Vision Keeper that ... authors a decision and
then asserts it", and night 132's abandon was the same shape. Placed in
section 12.

### 1.5 The supersede door

0 refusals on the whole night. The cycle read's three `supersedes='e_m26'`
calls of s109 stand. Walk 3 has no `decisions.author` with `supersedes`
(observed: `tool_calls`). The route that replaced his row on this night was
`problem.assert`, not `supersedes` (section 1.4).

### 1.6 The show_python request

The shift page asked whether the new request goes first. He said "Now. I'll
answer the open pages on the confirm change first", and the Liaison ruled
`{"confirm_default_on_eof": "now"}`, park `ip_cb13772835` (observed:
`rulings` r_87e0623e98, `item_parks`). The confirm pages then took walk 3.
The request reached the Vision Keeper, the Critic, the Terminologist and
the Architect as deliveries after the cancel, and no page. So walk 3 gives
no count of frame 243's main measure (reasoned: no batch for the item).

## 2. Frame 244, the re-annotate keeps declined files

Frame 244 validates at 51e6ff33. Ratio: 2 of 2 re-annotates after a files
contest keep a declined file, the same as night 148 (observed: `tool_calls`,
`turns`):

- s125, after m39: the block listed 31 grains with "he said: ... it lists
  many tests that have nothing to do with this change, like shell
  completion, context objects, formatting and the pager. ... leave echo
  alone". The seat annotated `src/click/utils.py::echo`,
  `tests/test_utils/test_echo.py::test_echo` and
  `tests/test_utils/test_echo_via_pager.py::test_echo_via_pager`. The pager
  and `echo` stay, both declined.
- s172, after m74: "Line 8 lists the defaults tests and the short help code
  in utils, which have nothing to do with this change". The seat annotated
  `src/click/termui.py`, `src/click/utils.py`,
  `tests/test_utils/test_confirm.py` and `tests/test_defaults.py`. Two
  declined files stay.

The review's two counts:

- Can the block list a file he kept: yes, 1 of 2. s172's block lists
  `src/click/termui.py` and `src/click/termui.py::confirm` under "he contested
  these files", and his words ask for termui. s125's block lists no file he
  kept (observed: the block text).
- Did the sentence change plain annotate wakes: no sign. The 2 plain wakes,
  s121 and s168, each landed `batches.annotate`, and each had made-up
  turns. No control exists for the sentence alone (reasoned).

The files contests after the head commit never reached the Architect. m86,
m92 and m105 each faulted line 8, and the batch-line door refused the
contest each time (section 1.3). That is candidate N1, not this frame's
door. Frame 244 stays open. The seat had his words and the block and kept
the files twice, so the guide's step 7, the interview of s125 and s172,
comes before a pass 2 (reasoned: the frame's own status of 13:18 found
cause 2 out).

## 3. Frame 245, the unresolved tick after green

Frame 245 validates at f6e03017. One `tick:unresolved` wake, s244, the
Architect on m117 (observed: `sessions`). m117 was a Developer challenge to
the Tester on test_cr5, and its note reads "the session woken by it wrote
nothing and sent nothing" (s231, frame 174's sign). test_cr5 was red then:
the harness read 1 to 3 not passing at walk 3, and `test_runs` holds no row
for test_cr5 at all (observed: the log; `test_runs`). So the wake was right.
Ratio: 0 of 1 unresolved wakes on a green test.

The review's watch: no Critic challenge to a Tester ran on this night, so
no merge held on one, 0 of 0 (observed: `messages`, verbs). s244 met frame
212's answer door four times and then sent `msg.report_liaison`, m130, which
became the m131 ask.

## 4. Frame 246, the raw key on his page

Frame 246 validates at 401bbf3f. Pages with a raw tick key: 0 of 1
blindspot page (observed: m11's page in the jsonl).

The review's line, against night 148's s89: this night's s89 called
`code.gaps`, whose facts read "43 prose files indexed; reconcile checked
the root README and nothing else" and "the glossary holds 15 live terms"
with no key. It logged 2 `gap` notes. `@glossary` was refused, "names no
row". `@prose`, "the prose files are checked", landed as l_07c5d7845c. It
attested `outcome="found"` (observed: s89's turns). So the zero is not a
`none_found` session with no note.

m11: line 2 of the page was "the prose files are checked". He asked "I
don't understand line 2. Which prose files do you mean, and what are they
checked against?" The Liaison asked him back at m13, and he said "I didn't
write line 2. It's your team's note ... otherwise drop the line." 2 of the 3
onboarding asks again. The key is gone, and the note now says the reverse
of its fact in words he cannot place (reasoned: the fact says the README
alone was checked). This is cause 11 again, the frame's own cause on a new
sign, so it is a residue for frame 253's helper or a new frame (section 12,
N5).

## 5. Frame 230, the lambda door, and frame 254, the stdin door

Frame 230 validates at 0d0f4771. Bodies that pass a lambda or a plain
function to `.invoke` and land: 0 (observed: `tests`, no stored body has
either). Sent: s179, 2 bodies with `runner.invoke(lambda: None, input='')`,
refused by the constant-assertion door. s191, 4 bodies with
`runner.invoke(lambda: confirm(...), input="")`, sent twice, refused by the
stdin door. The plain-function branch fired in s195, s197, s237 and s250. The
lambda branch fired 0 times, because another door refused first. After the
plain-function refusal, s197's next body was a local `@click.command()`,
the right route (observed: `turns`).

Frame 254, pushed from the cycle read. The refusal "where stdin is
captured" stands in 3 Tester sessions on this night (observed: `turns`):

- s197: 4 refusals of the one right body, the cycle read's case. Confirmed.
- s216, walk 3: 4 refusals of bodies that call a bare `confirm()` under
  pytest with no import and no stdin patch. Right refusals. Its turn 3
  bodies set `sys.stdin = StringIO('')` and landed.
- s191: 8 refusals of the lambda bodies. The bodies are wrong, but the
  refusal names a wrong fact: the call never runs, because `.invoke` gets a
  lambda. The stdin door fires before the invoke door, so the seat learns
  the wrong cause (reasoned: cause 9 by the guide; a line for frame 254's
  pass).

So 1 of 3 sessions refused a right body on this night, and no other right
body was refused.

## 6. Frames 239, 202, 187, 236, 204 and 173

**Frame 239.** bg_2 was not re-dispatched after either abandon. After m85,
"keep working" landed as r_cb56c527ea with `bg_2: approve`, and the same
batch ran attempts 2 and 3. After m91, the walk 3 reply landed
r_80d30c50e6, and the same batch ran attempts 5 to 10, then `tick:exhausted`
in s229, s239 and s241. The cancel left bg_2's tests in `tests`, test_cr1,
test_cr3, test_cr5, test_cr6 and test_cr5_revised, bound to the abandoned
batch, and no later batch exists to count them. Ratio 0 of 0, the second
night (observed: `batches`, `tests`, `sessions`).

**Frame 202.** 0 of 6 criteria reached a Tester encode with a text and a
surface that disagree. s173 sent `src/click/termui.py::commit` as the
surface 36 times, and the surface door refused each: "is not a symbol the
index knows". s247's surface `tests/test_termui.py::...` never landed.
Every surface at every encode was `src/click/termui.py::confirm` (observed:
`criteria`, s173's turns). Over two nights of pass 2: 0 of 11, against at
most 1 in 5.

**Frame 187.** 2 contested Vision Keeper wakes, s109 (`how_it_works`) and
s158 (`confirm_default_on_eof`). Neither had every call refused: both
asserts and both reports landed. 0 of 2 (observed: `tool_calls`). The
five contests of walks 2 and 3 were on criteria, not on an item, so they
woke the Terminologist and not this tick. s109's wake came from a contest
the words did not support, candidate N6.

**Frame 236.** 0 `touch_mistaken` wakes. The two touch wakes were
`touch_note`, s122 "expected 31, possible 0" and s169 "expected 17, possible
0" (observed: `sessions`). 0 of 0, the third night.

**Frame 204.** 3 `conflict` (onboarding, Vision Keeper, resolved on his
pages), 1 `gap` (l_07c5d7845c, resolved when he said drop), 10 `invented`
(l_0d6d242d89 resolved by his m57 contest; 9 open on bg_2's ticket and
criteria, by the Tester and the Terminologist), 3 `other` and 1 `scope` (the
Developer, open, each a sentence about the test's stdin patch), 16 `default`.
No merge waited on a row. bg_1 merged, and bg_2 left on the item rewrite,
not on a note (observed: `ledger`). l_a980dab2e3 holds the fact he gave
three times: "The criterion text says 'raises UsageError' but the code shows
it raises Abort() on EOF". No seat answered it.

**Frame 173.** 2 admitted span writes removed a statement the text does not
hold, and both carried a `dropped` note. s192: "removes 1 statement ...
`except (KeyboardInterrupt, EOFError):` at line 336", a true rewrite that
landed in 39f9365. s228: "removes 1 statement ... `if value in ("y",
"yes"):` at line 340". The commit 6ea9f90 then removed confirm's whole
y/n branch, nine lines, and left `rv` unset on a normal answer (observed:
`git show 6ea9f90`). 2 of 2 against 9 in 10. The residue is that a note does
not stop a commit (reasoned).

## 7. The abandons and the keep-working replies

### 7.1 m85

Predicate: `tick:quarantined` on the Developer's `tests_failing` for bg_2 at
3 attempts, s187. "Keep working" landed on the batch: r_cb56c527ea with
`bg_2: approve`, the key lifted, s192 and s193 ran attempts 2 and 3. The
Developer then fitted the product to the wrong tests in 39f9365, frame 171's
case, as the cycle read found (observed). His files sentence on line 8 was
discarded by the batch-line door (section 1.3).

### 7.2 m91

Predicate: the Tester's `tests_missing` for bg_2 at 3 attempts, s198, the
cycle. In walk 2 the reply m92 landed nowhere (section 1.3). In walk 3 the
reply m105 landed r_80d30c50e6 with `bg_2: approve`. The batch then ran to
attempt 10 of 10, and s232's rewrite cancelled it at 15:55 (observed).

### 7.3 Is "m92 made no ruling row" a known frame's wall?

- Frame 185, a deferral with no ruling word: no. m92 defers nothing.
- Frame 192, `drop` lands nowhere after a repeated refused call: the same
  effect, a different cause. 192's key is a ruling word. Here the ruling
  words were right, and the batch-line door refused the contest of line 8.
- Frame 214, a reply that lands as a new request: no.

So it is a new wall by the residue rule, N1. Two more replies landed
nowhere for other causes: m96 on the "through" range, N2, and m106 on a
right refusal the seat repeated (cause 4 or 5, unread; no interview).
The three together: 3 of 6 replies to bg_2's pages lost his words, 0 of 9
over all walks of night 148 (reasoned: night 148's read names no reply with
no ruling).

The approve of lines his words fault is a fourth path. s212 approved lines
6 and 7 against "Lines 2, 3, 5, 6 and 7 are also wrong", and s199 and s213
sent the same approves in calls that were refused for other lines. m120's
clarify verdict approved cr_5 against "please change those words to
\"instead of aborting\"", and the respecify door then held the declined
words, frame 250's case (observed: `rulings`, `turns`). Candidate N3.

## 8. The fault rows

| Rows | Session, walk | Text, short | Open frame |
|---|---|---|---|
| 4 | s114, walk 1 | "The term argument is undefined in the glossary but was used in criteria" | Frame 247: the glossary row is `Argument`, id `argument`, and `glossary.lookup(term='argument')` misses it |
| 2 | s180, s186, walk 2 | "The test mocks sys.stdin to None ... input() raises RuntimeError 'lost sys.stdin'" | Frame 171: the Developer then caught RuntimeError in 39f9365 |
| 2 | s193, s228 | "The test expects confirm to return None when default=None ... the current code raises Abort" | None. A Developer's work note written as a fault |
| 3 | s224, s226 (2) | "The test calls confirm() with echo=False, but confirm() does not have an 'echo' parameter" | Frame 143's family, a Tester writes an argument the function lacks. s226 also tried to commit an `echo` parameter, frame 171 |

Walk 1's "Rota itself failed 4 times" is the 4 s114 rows. Walks 2 and 3
printed no such line, and they hold 7 rows (observed: `faults`, the log).
The fault table as a Developer's diary is unframed, low, listed in section
11.

## 9. The other shapes

- **Made-up turns**, frame 113 (parked, the guide's cause 7, "not now"):
  120 turns in 44 sessions against 77 in 22. 10 in 6 are onboarding cassette
  replays, walk 1 14 in 5, walk 2 65 in 20, walk 3 31 in 13. Most: s172
  (Architect relay, 11), s168 (annotate, 9), s174 (Developer, 9) (observed:
  `FABRICATED_RESULT` over `turns`).
- **The 3 landed commits after an invention**: nightcount prints
  37a28655 and 39f9365f, and 0 writes after an invented result. s126
  committed 37a28655 at turn 12 after made-up turns 4, 6 and 7. s192
  committed 39f9365f at turn 17 after made-up turns 6 and 9 (observed:
  `turns`). The third is not named by the tool (reasoned).
- **Dangling pointers**, 78 turns in 20 sessions: s224 (14), s183 (9), s193
  (9), all bg_2 Developer `tests_failing` wakes that re-read `termui.py`.
  Frame 139's sign, two reads of one file drop each other (observed:
  nightcount).
- **Repeated wakes**, 6 groups: s127 and s133; s143 and s144; s180, s183,
  s186 and s192; s187 and s198; s193, s217, s218, s220, s224, s226 and
  s228; s195, s196 and s197 (observed: `nightcount.count`). The 7-wake group
  is bg_2's attempts 3 to 9 on one prompt shape.
- **Frame 222's import hint**: 6 hints in 6 sessions, 1 right. s177, s191,
  s196 named `from click.termui import confirm` for `cli_app`, s197 for
  `cli_app_with_confirm`, s177 and s195 for `CliRunner`. s216's for
  `confirm` was right. 1 of 6 against 3 of 3 (observed: `turns`).
- **Frame 212's answer door**: s222 met it once and then answered, m113.
  s244 met it four times and sent `msg.report_liaison`. 1 of 2 Architect
  answer wakes ended with no answer.
- **Frame 174**: m117, "the session woken by it wrote nothing and sent
  nothing", s231. 1 row.
- **Frames 224, 223, 242, 248, 249**: no sign. No `version_option` test was
  written, no quarantine was lifted by an approve, 0 `other` rows hold a
  door's question, no criterion ruling reached `glossary.adopt`.
- **Frame 241**: 2 pages carry notes of another request or of none. m57
  line 4 was the echo_json note, "which is my first change and not this
  one". m95 lines 8 to 11 were four glossary terms, "notes 8 to 11 have
  nothing to do with this change" (observed: the pages, the words).
- **Frame 247**: 4 fault rows, section 8.
- **The gate's flaky `test_map`**: no gate ran on this night.
- **New**: candidates N1 to N7, section 11.

## 10. The merged code and the cancel, in cost

The one merge, bg_1: 44 steps, 6 asks, 0.87 dollars. The cancel, bg_2: 145
steps, 14 asks, 2.26 dollars over walks 2 and 3, with walk 3's show_python
deliveries inside it. Onboarding: 107 steps, 3 asks, 0.32 dollars. Night 149:
3.45 dollars. Night 148's three merges: 133 steps, 12 asks, 1.66 dollars on
the walks, 2.12 with onboarding (observed: both logs).

## 11. Candidate frames, new

- **N1. A files correction after the head commit lands nowhere.** Site: the
  batch-line door in `rulings_rule`, `rota/roles/api.py` about lines 8754 to
  8790. Count: on night 149, 3 of 3 replies that faulted line 8 after bg_2's
  head commit, m86, m92 and m105; 2 approved line 8 on the door's advice, 1
  ended with no ruling. Over nights 136 to 149, 25 sessions met the door and
  8 replies made no ruling row (observed: `xcount.py`, 2026-10-15 16:1x).
  Price: 2 to 3 cycles.
- **N2. `_LINE_REF` does not read "through" as a range.** Site: `_LINE_REF`
  and `_ref_lines`, `rota/roles/api.py` lines 8355 to 8383. Count: 3
  principal replies over 50 nights hold "lines N through M", 1 met the
  door (s205, 5 refusals), 3 of 3 made no ruling row (observed:
  `xcount.py`). Price: 1 to 2 cycles.
- **N3. The verdict approves lines his words fault.** Site: the Liaison's
  verdict on a present page, `_line_refusal`, which refuses a contest of a
  matched line and has no branch for an approve of a faulted line. Count:
  s212 approved 2 named faulted lines and landed, s199 and s213 the same in
  refused calls, and m120's clarify approve is frame 250's. Effect: cr_5 and
  cr_6 kept the declined words. Price: 3 cycles with frame 250, one count.
- **N4. `criteria.specify` under one id replaces the last criterion.** Site:
  `criteria.specify` in `rota/roles/api.py`. Count: s114, 4 criteria under
  `echo_json_helper`, 1 stands, and the merged `echo_json(None)` prints
  nothing. Price: 2 cycles, a count over every night first.
- **N5. The blindspot `gap` note states the reverse of its fact.** Site:
  s89's `ledger.log` text from `code_gaps`, beside frame 253. Count: 1 page,
  2 of 3 onboarding asks, m11 and m13. Price: 2 cycles.
- **N6. A contest lands on a line no sentence names when one sentence
  corrects the request.** Site: `_unnamed_contest`'s spare of item lines.
  Count: m25, "ok, this matches what I asked for. Please keep it to the
  standard library json module", ruled `how_it_works: contest`. Cost: the
  m29 ask and s109's rewrite of `how_it_works` to version 3. Price: 2 cycles.
  Low.
- **N7. A Developer writes work notes as fault rows.** Site: the Developer's
  `faults` route. Count: 7 of 7 walk 2 and 3 rows. Unpriced, low.

## 12. Every wall placed by the guide

Each placement follows `plans/wall-guide.md` section 4, in order, and stops
at the first step that places.

**W1. bg_2's cancel by s232's assert (frame 129's case).**
1. Open frame's sign: yes, frame 129, a Vision Keeper authors a decision and
   then asserts it on the item. The case goes to frame 129, placed by cause.
2. Instrument: right. The assert is in `tool_calls` and the item version
   moved.
3. Does the sign name his words: yes. His words "the flag defaults to
   False" left the item. The first hop whose output differs is s232's
   `problem.assert`. The hop had a door, so step 4 decides the shape.
4. Door: it did not fire. It was wrong not to fire, because its predicate
   is the wake kind and its fact is the row's owner. Cause 8, "A door's
   predicate is not its fact", by its effect cause 1, "His words change on a
   hop".
8. Decide: the cheap fix, the door refuses a rewrite of a decided item on
   every wake that is not his contest, key the item's provenance, a value
   no seat varies, 2 cycles. The count is 24 propose-wake asserts, 7
   landed. No escalation: "The tool never rules for the Principal" already
   rules it.

**W2. N1, the files correction after the head commit.**
1. Open frame's sign: frames 192 and 244 share the effect. The cause
   differs, so a new frame.
2. Instrument: right. The refusal is in s199's next `user` text.
3. His words: yes. The first hop that differs is the Liaison's verdict. The
   hop had no slot for a files correction after the build starts. Cause 1,
   the missing-slot shape.
8. Decide: the cheap fix for a missing slot, a route. A contest of the batch
   line after the head commit lands with his words and goes to the
   Architect's re-annotate, and the refusal stops saying "Otherwise approve
   line 8" for a line his words fault. 2 to 3 cycles. Escalate: no. "The
   principal's words always land on a row" is ruled (Roman, 2026-10-08,
   `rota/DECISIONS.md` line 1445). Frame 142's design 2.D says a ruling after
   the head commit moves nothing. That premise is the question for the
   pass's history read, because the Developer's fence reads `batch_touch`
   (reasoned).

**W3. N2, "through".**
1. Open frame's sign: frame 234's door, closed. A residue, so a new frame.
2. Instrument: right.
3. His words: the hop's output, s205's call, matched his words. The hop
   did not differ, so the step does not place.
4. Door: it fired and was wrong to fire on lines 6 and 7. Cause 8. The key
   is a regex token, a value no seat varies.
8. Decide: the cheap fix with its count, 3 replies over 50 nights, 1 to 2
   cycles.

**W4. N3, the approve of faulted lines.**
1. Open frame's sign: frame 250 for m120, a clarify verdict. s212 is a
   present page, a residue of closed frame 234 on the other side.
2. Instrument: right.
3. His words: yes. The first hop that differs is the Liaison's verdict. The
   seat read the words and wrote something else. Cause 1, the rewrite
   shape.
8. Decide: cause 1's cheap fix, a counted door that reads a fact of the text:
   a line the words number in a sentence with a fault cue takes no
   `approve`. `_line_reading` already computes the faulted set. Two open
   frames under one cause, 250 and N3, become one frame on the verdict hop
   (step 1's rule). 3 cycles with the count.

**W5. Frame 254, the stdin door.** The cycle read's placement stands:
cause 8, wrong to fire. This read adds s191: right to fire on a wrong
body and the fact wrong, cause 9, one line for the same pass.

**W6. Frame 243's seam on walks 2 and 3.**
1. Open frame's sign: yes, frame 243.
3. His words: the first hop that differs is the Terminologist's respecify.
   The seat had the block and his words, and kept the declined phrase twice
   (s173, s190). It moved once, when the landed ruling quoted the phrase
   (s215).
6. and 7. The fact was in the prompt. Whether the seat read it is the
   interview's question. The cycle read placed s190 as cause 5. The guide's
   cause 5 ruling says interview first. No interview ran.
8. Decide: an open frame with its reason. Frame 243 stays validating on
   its ratio. The interview of s190 against s215 is one cycle, and it tells
   whether a quote of the declined phrase in the ruling is the record shape
   the seat reads.

**W7. N4, one criterion id written four times.**
1. Open frame's sign: no.
2. Instrument: right. `criteria.version` is 4.
3. His words: no. The sign is a lost requirement of the seat's own.
4. Door: none fired. A specify under an id this session already wrote
   replaces it with no refusal. Wrong not to fire. Cause 8.
8. Decide: the cheap fix after a count over every night, 2 cycles.

**W8. N5, the gap note in words.**
1. Open frame's sign: frame 246's cause on a new sign, beside frame 253.
2. Instrument: right.
3. His words or his page: the page. Cause 11, "What reaches him is not
   his".
8. Decide: cause 11's entry says escalate, always, as a design question.
   Frames 190 and 193 already ruled what the page holds. The question left
   is whether a note about rota's own coverage belongs on his onboarding
   page. Recommended answer: no, it goes to the state view. Fold into frame
   253, 2 cycles. [med]

**W9. N6, the contest of an agreed line.**
1. Open frame's sign: frame 234, closed. A residue, a new frame.
3. His words: the verdict differs. But the door read the words, so step 4.
4. Door: it did not fire, because a sentence with no line number spares
   every item line, and `how_it_works` is an item line that is not his
   request. Wrong not to fire. Cause 8.
8. Decide: the cheap fix, the spare covers line 1 alone, 2 cycles, low.

**W10. The cut of four Developer wakes behind the block.**
1. Open frame's sign: frame 243's own low, the block's size.
2. Instrument: right.
6. The fact, the red test rows, was absent from the prompt. Cause 2, "The
   prompt lacks the fact".
8. Decide: "not now, when": the seats recovered the rows by `tests.load` at
   a step cost. The frame's pass 2, if it runs, shows one block per ruling
   and drops entries for approved criteria. Stays a low of frame 243.

**W11. Frame 222's hints, 1 of 6 right.** Step 1: an open frame's sign,
frame 222, placed there by its own cause 9. Step 8: frame 222's cheap fix,
2 cycles.

## 13. For the sprint boundary

### 13.1 The open frames that this night's counts close

- Frame 243 stays validating, night 1 of 3: 0 of 1 merges carry what he
  declined. The night shows three new routes that lose his words before a
  merge (N1, N2, N3), and the item rewrite that ended the batch (W1).
- Frame 244 stays open: 2 of 2, no move. The interview of s125 and s172
  comes first.
- Frame 245 stays validating, night 1 of 3: 0 of 1.
- Frame 246 stays validating, night 1 of 3: 0 of 1 pages with a raw key.
  m11's note goes to frame 253 as N5.
- Frame 230 stays validating, night 1 of 3: 0 landed. The lambda branch
  fired 0 times.
- Frame 254 stays open: its pass has not run. Night count 1 of 3 sessions.
- Frame 239 stays validating, the second night of 0 of 0.
- Frame 202 closes. 0 of 6, and 0 of 11 over the two nights of pass 2,
  against at most 1 in 5.
- Frame 187 closes on its ratio: 0 of 2 contested wakes with every call
  refused, against at most 1 in 3, after 0 of 0 on night 148.
- Frame 236 closes by cause 8's close rule: a door, 0 cases over three
  nights, and a green door test. The count line stays here, so a later fire
  reopens it.
- Frame 204 stays validating, the fifth night of pass 2. No merge waited on
  a row. The seam night waits on its order.
- Frame 173 stays open: 2 of 2 notes, and the residue that a note does not
  stop a removal reaching a commit.
- Frame 129 takes W1's case and leaves the parked list.

### 13.2 One order for the next sprint

By the wall that cost the most steps or asks on this night, then by price
(reasoned: sections 1 to 12):

1. Frame 129, the item-rewrite door on every wake: 2 cycles. It ended bg_2
   after 145 steps and 14 asks.
2. N1, the files correction after the head commit: 2 to 3 cycles. 3 of 3
   files corrections on bg_2 lost.
3. N2, "through": 1 to 2 cycles. 1 reply lost, 5 refusals.
4. Frame 250 with N3, the verdict hop: 3 cycles. cr_5 and cr_6 kept the
   declined words.
5. Frame 254, the stdin door: 2 to 3 cycles. The cycle, 3 Tester wakes.
6. Frame 222, the import hint: 2 cycles. 1 of 6 right, inside the cycle.
7. Frame 243's interview of s190 against s215: 1 cycle.
8. Frame 244's interview of s125 and s172, then pass 2: 2 to 3 cycles.
9. Frame 253 with N5: 2 cycles. 2 onboarding asks.
10. N4, one criterion id written four times: 2 cycles.
11. Frame 247, the lookup case: 2 cycles. 4 fault rows.
12. Frame 241, the agenda's notes: 2 cycles. 2 pages.
13. Frame 171, the Developer fits the product to a wrong test: 3 cycles. 2
    cases.
14. Frame 212, the answer door: 2 to 3 cycles. 1 of 2.
15. Frames 223, 173, 242, 174, 248, 249, 224, 216, 217, 218, 214, 220, 211
    and 116, and N6 and N7: no new sign or low, 1 to 3 cycles each.

Frame 252 stays parked at rank 1: this read is its first of three, 11 walls
placed. Rows 1 to 6 are about 14 cycles, and the interviews 2 more, one
sprint by the rule of 2026-10-11 05:51.

### 13.3 The next night's wall

The wall that cost the most is bg_2's: 145 steps and 14 asks, and no merge.
Its chain is five contests of one claim. His words were lost at the verdict
three ways, N1, N2 and N3. They reached the criteria only when a ruling
quoted the phrase. Then a propose wake rewrote his item and cancelled the
batch, W1. The next night's wall is frame 243, held on its ratio, with
frame 129's door, N1, N2 and N3 built before the night, because each one is
a route by which the declined words survive or his words land nowhere.
Frames 239, 245, 246 and 230 count on it again.

The one merge cost 44 steps, 6 asks and 0.87 dollars. The cancel cost 145
steps, 14 asks and 2.26 dollars. Night 148's three merges cost 133 steps, 12
asks and 1.66 dollars (observed: section 10).

Usage: about 280k tokens of the 300k cap.
