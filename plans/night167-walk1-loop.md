# Night 167, walk 1: the line 1 loop on get_app_dir_windows

- Date: 2026-10-26 06:11, read while the night runs.
- The night's commit: 40b16f78, profile `local-gemma-cr-ts`, from `C:/Users/roman/rota_n167g`.
- Sources, all read-only: `.rota/night167.log` lines 98 to 131;
  `.rota/clickI.principal.jsonl`, the `call` rows of m42, m66 and m118;
  `.rota/clickI.db` by `?mode=ro`, the tables `items`, `messages`, `entries`,
  `sessions`, `tool_calls`, `turns`, `receipts`, `tick_attempts`, `batches`,
  `test_runs` and `criteria`; `rota/roles/api.py`, `rota/core/cycles.py`,
  `rota/roles/prompts/liaison/*.tools`, `plans/stack.md`,
  `plans/night163-read.md`.

## The result

**The walk 1 loop has no exit inside the team: line 1 is the item's text, a
Vision Keeper amend on `tick:contested` put a sentence of his test talk on it,
the Liaison holds no call that writes an item, and the one wake that may
rewrite it is quarantined since s235, so walk 1 ended only at the quiet bound
after 174 steps (log line 121).**

Walk 2 started at 06:09 on a new request, `clear()`, and the principal parked
the app folder change "until the clear change is merged, and then go back to
it" (log line 131).

## 1. What line 1 of the present page is built from

Line 1 under "You asked" is `items.text` of `get_app_dir_windows`.

- m66, line 1: "In get_app_dir on Windows, when APPDATA or LOCALAPPDATA is not
  set, use the AppData Roaming or AppData Local folder under the home folder
  instead of the bare home folder. Its check calls the function without an app
  name, so it fails before it tests anything." (`clickI.principal.jsonl`, the
  `call` row of m66).
- m118, line 1: "In get_app_dir on Windows, when APPDATA or LOCALAPPDATA is not
  set, use the AppData Roaming or AppData Local folder under the home folder
  instead of the bare home folder. Only test the app folder tests and the utils
  file." (the `call` row of m118). This text is `items.text` now, version 5,
  approval `contested`.
- m42, line 1 holds the first sentence only. So the stop page replies m43 and
  m51 did not write line 1.

The appended sentence came from his reply to a present page, not from a stop
page reply. The path, in order:

1. m57, his reply to the present page m56: "Line 10 is still wrong. Its check
   calls the function without an app name, so it fails before it tests
   anything. ..." The runner stored it as the entry `e_m58` and the verdict
   m58 contested the item (messages m57, m58, m60).
2. s161, the Vision Keeper on `tick:contested`, asserted a paraphrase. The
   words door refused it with the step from `_amend_step` (`api.py` 1446 to
   1453, called at 1817): "Write his words about get_app_dir_windows ...
   amend '<item text>' with his sentence ...". `_item_sentence` (`api.py`
   1428) gives his longest sentence that is not about the page, and here that
   sentence is about the test (s161 turn 5).
3. s161 seq 9 asserted the item text plus "Its check calls the function ..."
   (`tool_calls`, `receipts`).
4. His removal requests then became new appended sentences, because the same
   step offers only an amend with his sentence. s187 wrote "Only test the
   utils file and the app folder tests." from `e_m77`, his m76 reply. s199
   wrote "Only test the app folder tests and the utils file." from `e_m86`
   (`tool_calls` s187 seq 8 and 9, s199 seq 8 and 9).
5. s176, s212, s226, s231 and s233 asserted the current text again. Each got
   `"unchanged": true` and wrote nothing (`turns` s176 t2, s233 t2).

The Liaison cannot remove the sentence. Its `.tools` files hold no
`problem.assert` and no other write to `items`. Only the Vision Keeper's mode
files hold `problem.assert`. The Liaison can relay to the Vision Keeper, but a
relay wake does not rewrite a decided item (`api.py` 1689 to 1706). The
relay's `problem.set_approval` refusal says "the contested wake carries the
words. Leave it" (`api.py` 2119, s211 and s225 turn 5). The contested wake is
quarantined: `tick_attempts` row `vision_keeper|tick:contested|get_app_dir_windows`,
attempts 3, quarantined 1, after s226, s231 and s233 wrote nothing (Liaison
s235, `tick:quarantined`). So from s235 no role can change line 1, and the
loop has no exit. Before s235, a plain assert of the first sentence alone
probably passed the door, because it adds no new word (`api.py` 1803 to 1815,
reasoned, not run). No refusal text offered that form.

The clarify pages m81, m90, m102 and m112 are the Liaison's own questions
after each relay. They do not change the item either.

## 2. Why no CYCLE line fired

`cycle()` keys each committed session as role, wake kind, detail and wake
refs. A message wake's detail is its verb only (`cycles.py` 33 to 39). Three
rounds must have equal key sequences and equal receipt signatures (`cycles.py`
100 to 116). The loop fails the first test:

- The principal's replies and the Liaison's pages are not sessions, and a
  message key holds no body. Six equal rejections and four equal questions
  never enter a key.
- The tick keys change each round. `tick:touch_note` detail is "expected 1,
  possible 1" at s171, "expected 24, possible 0" at s182 and "expected 3,
  possible 1" at s220. `tick:annotate` refs are `bg_2`, `bg_3` and `bg_4`.
  `tick:grouping` refs are `tk_2` and then `tk_3`.
- The rounds differ in shape. s191 to s194 hold three `tick:guess` sessions
  and a guess quarantine. s205 is a signoff. s216 and s217 re-slice to tk_3.
  s231 to s235 hold three contested ticks and the quarantine.

`cycle(conn, last=...)` on the read-only database returns None at s199, s220,
s234 and s240.

## 3. Whether an open frame names this wall

Frame 315 names it. The phrases "fix it and try again", "keep only what I
asked for" and "appended" have 0 hits on `plans/stack.md`. "take it out" has 3
hits, all in frame 204, about another matter. The hits for "stop page", "line
1" and "the ask" name other walls.

- Frame 315's site is "the Vision Keeper's amend on `tick:contested`"
  (`stack.md` 1319).
- Its status of 2026-10-24 06:05 names the departure: "`_item_sentence` ...
  offered one sentence through frame 263's filter" (`stack.md` 1326).
- Its status of 06:35 says "The amend's sentence stays as it is until Roman
  rules" (`stack.md` 1330).
- Its status of 18:19 records night 163's case: "the words door made the item
  text his refusal" (`stack.md` 1332, `night163-read.md` 148).

Frame 315's "Ends when" line names the carry of criteria and the id refusal.
It does not name an item text that holds a sentence he asks to remove, or a
contested tick that quarantines with that text in place. Night 167 is a
second case of the open question at `stack.md` 1330, and a worse one.

## 4. What the night has given to frames 328, 329 and 323

The sessions by role and model (`sessions`):

| Role | Model | Sessions | Where |
|---|---|---|---|
| Tester | gemma4:12b-it-qat | 5 | s126, s128, s131, s141, s142, all on bg_1 |
| Critic | gemma4:12b-it-qat | 15 | s77 to s90 on onboarding claims, s153 on the item |

No Critic emitted a verdict. There are 0 `verdicts.emit` calls.

- Frame 328, the encode note: 0 fires. s125, a Developer, committed bg_1 at
  5c8c80b5 before s126 encoded. The Tester's encodes got no "fails at line"
  note (`turns` s126 to s142). The cause is not read here.
- Frame 328, the live-text quote check: 3 refusals, s143, s146 and s147 on
  `tst_c4`: "quotes= holds `mock_appdata = ...`, and it is not in the live
  text of tst_c4". The seat sent the same quote again each time. s127 and
  s130 sent challenges m36 and m38 on `c_5`. s133 was refused as a repeat.
- Frame 329: 0 fires. The Terminologist made 21 `criteria.respecify` calls
  (s140, s224, s239, s247). No call was refused as a twin, and the 13 criteria
  hold no two equal texts on one ticket.
- bg_2 exercised neither site. The present page m66 cancelled it before a
  Developer, a Tester or a Critic woke (sessions s169 to s173). bg_3 and bg_4
  had the same end.

Frame 323's Gemma seats ran, but on one batch only. The Tester's 5 sessions
are all on bg_1, and the Critic judged no batch.

## The recommendation

Let the night run. Walk 1 already ended at its quiet bound, and walk 2 builds
`clear()`, which is the night's only chance to give frames 328, 329 and 323 a
batch that reaches the Tester and the Critic.

Read the log again when walk 2 resumes `get_app_dir_windows`. Its line 1 still
holds the extra sentence and its contested tick is still quarantined, so that
walk can only repeat walk 1.
