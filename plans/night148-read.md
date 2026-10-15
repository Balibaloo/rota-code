# Night 148 read: 3 of 3 batches merge with no cancel, and bg_3 merges the version message the principal declined twice

Rota workflow throughout, except where a line says meta workflow. Read on
Opus, 2026-10-15 00:5x to 01:1x by the clock.

Sources:

- `.rota/clickI_night148.db` (209 sessions, 884 turns), `.rota/clickI_night147.db`
  and `.rota/night_cassettes.db`, each opened with `file:...?mode=ro`.
- `.rota/night148.log` (122 lines) and `.rota/night147.log`.
- `.rota/clickI_night148.principal.jsonl`, the rows with `"night": "148"`.
- `.rota/ollama_night147.log`, the `[GIN]` lines dated 2026/10/15: 503 `/api/chat`.
- The tree `C:/Users/roman/rota_night148` at 92c4f126, read only:
  `rota/tools/nightcount.py`, `rota/roles/api.py` (`kind_questions`
  8884-8910), `rota/roles/prompts/terminologist/survey.md`.
- `git log` and `git diff` in `D:/repos/_AI/sample_repos/clickI`, read only.
  The batch worktrees `bg_1` to `bg_3` are gone, so the read used the main
  repository's objects and the branches `batch/bg_1` to `batch/bg_3`.
- Scripts in this session's `scratchpad/r148/`: `q.py`, `dump.py`,
  `errs.py`, `f233.py`, `pj.py`.

Walk boundaries: onboarding is s1 to s99. Walk 1 starts at s100 on `m_p1`,
walk 2 at s126 on `m_p2`, walk 3 at s164 on `m_p3` (observed: `messages`,
`sessions.trigger_msg`).

The three batches (observed: `batches`, `verdicts`, the log, `git diff`):

| Batch | Item | End | Steps, asks, dollars | Wall or cost |
|---|---|---|---|---|
| bg_1 | `echo_json` | merged at walk 1's end | 32, 4, 0.54 | three Developer wakes, s120 to s122, 484 s of turn time on refused rewrites of `utils.py` |
| bg_2 | `confirm_default_on_eof` | merged at walk 2's end | 47, 4, 0.56 | three reds, all frame 230's lambda passed to `CliRunner.invoke`; 7 wakes to green |
| bg_3 | `version_option_show_python` | merged at walk 3's end | 54, 4, 0.56 | merged code replaces the version message, which the principal declined at m70 and m81 |

The brief's facts hold, with four corrections:

1. The principal's record holds 1 row with `"model": "replay"` on night 148,
   m2. The other 5 replay rows are night 147's (observed: the jsonl, by
   night).
2. Onboarding is 99 sessions, s1 to s99. 84 are on `cassette:` and 15 are
   live. The 125 sessions on `ollama` include the walks (observed:
   `sessions`).
3. The 1 landed commit after an invention, 2559537c, is not a write after an
   invented result. The commit landed at s153 turn 3, and the made-up turn,
   turn 6, already carried the sha in its own prompt (section 11).
4. No survey wake ran after bg_3's merge. The night ended at the merge
   (section 5).

## 0. The answer in brief

| Frame | Measure | Night 148 |
|---|---|---|
| 233, onboarding | minutes, sessions on `cassette:`, asks | 4 minutes against 15. 84 of 99 on `cassette:` against 70. 3 asks, caused by frame 237's survey brief line, which runs live by design. 5 of 5 cut turns of night 147 replayed |
| 238, the set_approval door | batches abandoned after `set_approval` on an item the principal approved | 0 of 3. 0 `contested` calls, so the door did not fire. 2 refusals, both `_must_exist` on decision ids |
| 239, `tests_missing` by batch | re-dispatched batches that merge untested | 0 of 0. No batch was re-dispatched. 3 of 3 merges had one test per criterion |
| 234, line reading | verdicts that contest a line the words do not fault | 0 of 5 numbered corrections. 0 batches abandoned of 3. The door's line-1, unnamed-line and ledger-note refusals fired 0 times. 1 clarify verdict, m81, approved a check and a decision the words fault |
| 237, survey after a merge | survey wakes that quarantine on a prose list | 0 of 5. 5 of 5 first replies are calls the parser reads |
| 202, surface move | criteria whose text and surface disagree that reach a Tester encode | 0 of 5. The door fired once, s188, and the seat went back to `version_option` |
| 240, quarantine after an approve | walk ends that name a quarantine whose cause is gone | 0 of 3 |
| 187 and 219 | contested wakes with every call refused; principal decisions that differ from his words | 0 of 0, no item went contested. 0 principal rows changed. The door refused 1 write under a principal's id |
| 173 | admitted span writes that remove a statement, with a `dropped` note | 0 of 0. No admitted write removed a statement |
| 229, 228, 236 | cycle refusals, `touch_strayed` and `touch_mistaken` wakes | 0, 0 and 0 |
| 204 | `conflict`, `scope`, `default`, `invented` rows | 3, 0, 13, 2, and 3 `other`. The 3 conflicts are onboarding notes the principal answered. No merge waited on a row |
| merged code | merges that carry what the principal declined | 1 of 3, bg_3. bg_1 and bg_2 put their tests in new files against his words |

## 1. Frame 233, the replayed onboarding

The 4 minutes hold. The log reads `== onboard 00:06` and `== walk 1 00:10`,
and `ONBOARDED after 107 steps, 3 asks` with `principal: 3 calls, 0.46
dollars on opus, 1 replayed` (observed: `.rota/night148.log`).

84 of 99 onboarding sessions are on `cassette:`. The 15 live sessions cost
99 s of turn time in all (observed: `sessions.backend`, `turns.ms`). The
first turn whose prompt differs from night 147's session of the same seat,
matched by role, wake kind, refs and message verb (observed: `f233.py`):

| Session | Seat | First diff | Cause |
|---|---|---|---|
| s68, s69 | Terminologist survey | turn 1, system | frame 237's `survey.md` line: "Write each word as one call on its own line ... A list under a call name runs nothing. Record at most five words." |
| s70 | Terminologist term_collision | no match in 147 | a wake night 147 did not have: s68 wrote `Option` beside `option`, so `option#src_click` collided |
| s73 | Vision Keeper reorient | turn 1, user | the glossary rows that s68 and s69 wrote |
| s89 | Liaison blindspot | turn 1, user | "the glossary holds 15 live terms" against 11 |
| s90, s95 | Liaison observed_entries, agenda | no match in 147 | wakes night 147 did not have, downstream of the glossary |
| s91, s96, s97 | Liaison converse | turn 1, user | the principal's live words at m7, m12 and m14 |
| s92, s98 | Liaison verdict | turn 1, user | the rows on the changed pages |
| s93, s94, s99 | Architect and Terminologist relays | turn 1, user, or no match | the relayed rows of the changed rulings |

All 15 live sessions trace to one cause: frame 237's brief line changed
s68's system prompt, which is a changed brief, and the mechanism runs a
changed brief live on purpose (reasoned: the chain above). No live session
is a missed match.

The 3 asks follow from that chain. m2 replayed, because its page matched the
recorded page. m6 carried 27 glossary and constraint lines that s68, s69 and
s70 wrote live, against night 147's page, so the principal answered live:
"Lines 18 to 28 are wrong, because those sentinel values and the context
stack helpers are click's own internals". m11 carried line 4, "given up
after the attempt bound: -|tick:constraint_zero|", a gap note from the live
s89 that night 147's page did not hold. The principal asked about it, the
Liaison asked back at m13, and he answered "I don't know what that line
means. Your team wrote it, not me" (observed: the jsonl pages and words).
That line is candidate G.

Pass 4's `done_reason` marks replayed the five turns night 147 missed. s9,
s24, s41, s71 and s81 are all on `cassette:` on night 148, and the cassette
holds a `done_reasons` table (observed: `sessions.backend`, the cassette
schema).

Frame 233's three lines: the 15 minutes holds at 4, the 70 holds at 84, and
the walks kept their shape, one request and one batch each. The asks are
not part of the ends-when, and their cause is a changed brief, not a missed
match. Frame 233 closes (reasoned: the three parts of the ends-when).

## 2. Frame 238, the set_approval door

0 of 3 batches were abandoned after a `set_approval` (observed: `batches`,
all `merged`). Every `problem.set_approval` call of the night
(observed: `tool_calls`, the turns' results):

| Session | Item | Latest landed ruling | Relay's verdict | Door |
|---|---|---|---|---|
| s8 (cassette) | 4 onboarding items | m2, approve | approve | landed |
| s108 | `echo_json`, `how_it_works` | m22, approve | approve | landed |
| s140 | `confirm_default_on_eof` and 4 more | m41, approve | approve | landed |
| s147 | `confirm_default_on_eof` | m46, approve | approve | landed |
| s180 | `version_option_show_python` | m66, approve | approve | landed |
| s207 | `d_f422882cbd`, `d_74_challenge_ver_opt_show_py` | m81, approve | approve | refused twice |

Every call asked for `approved`. No call asked for `contested`, so frame
238's door had no call to judge (observed). s207's two refusals are the
`_must_exist` door: "no items row with id='d_f422882cbd'; ... they are not
items rows. Answer what the relay names, or end the session". The seat sent
prose, "The relay names are 'd_f422882cbd' and
'd_74_challenge_ver_opt_show_py'.", and the session ended. The two ids are
decisions. The Liaison relayed a decision approval to the Vision Keeper,
whose `set_approval` takes items only (observed: s207). bg_3 merged after
it, so this refusal cost one wake and no batch.

## 3. Frame 239, `tests_missing` by batch

No batch was re-dispatched. Each item had one batch, `bg_1`, `bg_2` and
`bg_3`, and each merged on its first dispatch, so the ratio reads 0 of 0
(observed: `batches`).

| Batch | Criteria | Tests joined to the batch | Test per criterion |
|---|---|---|---|
| bg_1 | `echo_json_helper` | `tst_echo_json_compact` | yes |
| bg_2 | `cr_1`, `cr_2`, `cr_3_confirm_default_on_eof` | `tst_confirm_eof_returns_default`, `tst_confirm_eof_exact_default`, `tst_confirm_eof_raises_on_false` | yes |
| bg_3 | `ver_opt_show_py` | `tst_ver_opt_show_py` | yes |

All five tests have `tests.batch_id` equal to their own batch (observed:
`tests`). Each merge had a test per criterion. Section 10 reads whether
each test tests its criterion.

## 4. Frame 234, the verdict's line reading, pass 2

0 of 5 verdicts on a numbered correction contest a line the words do not
fault (observed: `rulings.per_item`, the pages, the `rulings.rule` calls):

| Page | Words name | Ruled `contest` | Fault |
|---|---|---|---|
| m6, onboarding | lines 18 to 28 | lines 18 to 28, the 11 constraint rows | none |
| m11 and m14, onboarding | line 4 | line 4, `l_b0945bbaa7` | none |
| m30, line 3, files | line 3 | line 3, `bg_1` | none |
| m50, line 5, files | line 5 | line 5, `bg_2` | none |
| m70, line 2, check | line 2 | line 2, `ver_opt_show_py` | none |

At m70 the second sentence, "It should also be added to the end of the
normal version message, not replace that message", is about the format on
line 2. So a contest of line 2 alone reads the words right (reasoned).

The door's refusals of pass 2 and pass 2b fired 0 times: no line-1 contest,
no unnamed-line contest, no ledger-note contest. Two other refusals fired
on `rulings.rule`:

- s91 turn 2: "lines 1, 2, ... 17 have no ruling. Every line of the page
  takes one". The seat re-sent the call with 1 to 17 `approve` and 18 to
  28 `contest`, and it landed.
- s97 turn 2: "you asked this in m13, and the principal answered it in
  m14". The seat sent the ruling with line 4 `contest`, and it landed.

The cancel wall of night 146 did not recur. The principal corrected one
line of a "Before I build this" page on every walk, m30 line 3, m50 line 5
and m70 line 2, and 0 of 3 batches were cancelled (observed: the log,
`batches`). Night 147 read 0 of 3 too, so the line reads 0 of 6 over two
nights.

The residue is on the other side of the verdict. At m81, a clarify page
about the test and the Vision Keeper's decision `d_74_challenge_ver_opt_show_py`,
the principal wrote "It should not expect only the command name and the
Python version." The decision's text and the test's comment both say
"{command} {python_version}". The verdict `r_3340e1e9d9` ruled all four
rows `approve` (observed: `rulings`, `decisions`, the m81 page). The
ends-when names this shape: a "wrong" on a check rules it `revise`. So 1 of
1 clarify verdicts on a check approved what the words fault (reasoned).
Section 10 follows its cost.

## 5. Frame 237, the survey after a merge

0 of 5 Terminologist survey wakes after a merge quarantined (observed:
`tick_attempts` holds one quarantined key, `-|tick:constraint_zero|`, from
onboarding). bg_1's merge woke s129, s130 and s131. bg_2's merge woke s167
and s168. bg_3's merge was the night's last event, so no survey followed it.
The Architect's surveys s132, s133, s169 and s170 ran beside them.

Each first reply, its calls and the cap of five words (observed: `turns`
turn 1). Every first reply opens with two or three sentences and then
`TOOL:` lines that the parser reads. The calls carry no `why` argument, so
the cap measured is the brief's "Record at most five words".

| Session | Area | First reply, the first call verbatim | Words | End |
|---|---|---|---|---|
| s129 | `src/click` | `TOOL: glossary.amend(term="stream", sense_body="An I/O object managed by Click for encoding and buffering, specifically wrapped via _NonClosingTextIOWrapper ...` | 3 of 5 | attested in turn 1 |
| s130 | `.` | `TOOL: glossary.amend(term="decorator", sense_body="A function that transforms another function into a Click command, group, or parameter ...` | 5 of 5 | 4 landed, `decorator` refused 5 times, no attest |
| s131 | `.` | `TOOL: glossary.amend(term="command", sense_body="An executable CLI unit defined by decorators ...` | 5 of 5 | `parser` refused, session ended |
| s167 | `src/click` | `TOOL: code.source(path="src/click/core.py", start=0, end=400)`, then 4 `glossary.amend` | 4 of 5 | attested |
| s168 | `.` | `TOOL: glossary.amend(term="choice", sense_body="A parameter type representing a selection from a fixed set of values ...` | 3 of 5 | `choice` refused, session ended |

The prose shape is gone: 5 of 5 replies are calls (observed). The residue is
the refusal "nothing you read this session says 'decorator'", on a CUT area
page, "104 of 147 files are not shown". s130, s131 and s168 each named a
word from a file they never opened. s130 and s131 are one of the 5 repeated
wakes, because s130 ended with no attest on `.` (observed: nightcount's
groups). The cause is not the prose shape, so by the third part frame 237
closes, and the cut-area refusal is the review's low 2 shape, a candidate
only if it costs a merge (reasoned).

## 6. Frame 202, the surface move door, pass 2

0 of 5 criteria have a text and a surface that disagree at a Tester encode
(observed: `criteria`, final state):

| Criterion | Text names | `surface_refs` |
|---|---|---|
| `echo_json_helper` | `echo_json` | `["echo_json"]` |
| `cr_1`, `cr_2`, `cr_3_confirm_default_on_eof` | `confirm()` | `src/click/termui.py::confirm` |
| `ver_opt_show_py` | `version_option` | `src/click/decorators.py::version_option` |

`echo_json_helper` holds a bare name and not `path::symbol`, at version 5,
and the doors admitted it (observed). That is a note, not a disagreement.

Every `criteria.respecify` is s188's, after the m70 contest relayed at m73,
with the door's answers verbatim (observed: s188's turns):

1. Surface `src/click/core.py::CommandCollection`: "'src/click/core.py::CommandCollection'
   lives in src/click/core.py, and the batch expects to touch
   src/click/decorators.py, ... No word of the request or the ticket names
   CommandCollection."
2. Surface `src/click/decorators.py::custom_version_option`: "The item asks
   for `version_option`, and this move drops `version_option` from the
   surface. The surface is what the test calls. Keep
   `src/click/decorators.py::version_option` in surface_refs. If the
   principal asked for `custom_version_option` itself, name
   `custom_version_option` in backticks in the criterion's text." This is
   frame 202's door.
3. Surface `src/click/decorators.py::version_option`: `OK criteria.respecify ->
   {"id": "ver_opt_show_py", "respecified": true}`.

The door fired once and the seat went back to the right surface. The
review's "give {n}" shape appeared once, in the true sense: the request "Give
version_option a show_python flag" names `version_option`, and the door
kept it. No false "give echo the result" match appeared (reasoned: the
three answers).

The ratio: 0 of 5 on night 148. Read with night 147 as the first night, as
the brief says, the two nights hold 2 of 8, which is 1 in 4 and above 1 in
5. Read with night 148 as the first night after pass 2, which is how the
status line of 22:01 sets it, the frame needs one more night (reasoned).

## 7. Frame 240, the quarantine after an approve

0 of 3 walk ends name a quarantine. Each walk ends "Done: N change(s) built,
tested and merged." with no "Stuck" line (observed: the log). The only
quarantined key all night is `-|tick:constraint_zero|`, 3 attempts,
`reported=1`, from onboarding. Its cause, the constraint-zero tick, did not
end. It is the line on m11 that the principal could not read, candidate G
(observed: `tick_attempts`, `ledger` row `l_b0945bbaa7`).

The "Rota itself failed 3 times" rows are the 3 rows of `faults`
(observed):

| Row | Session | Text | Open frame |
|---|---|---|---|
| `f_b24aefa8d9` | s110 | "The term argument is undefined in the glossary but was used in criteria." | none, candidate J |
| `f_aab947a89e` | s110 | "The term argument was used in criteria but is not in the glossary." | none, candidate J |
| `f_92f4e36cd0` | s155 | "The tests use `runner.invoke(lambda: confirm(...))` which passes a plain function to CliRunner.invoke ..." | frame 230 |

The two s110 rows have one cause. s68 wrote the row `argument` with the term
`Argument`. `glossary.lookup(term='argument')` answered "no entry for
'argument'. The glossary holds 16 terms", because the lookup matches the
term's case. Later s167's amend of `_Argument` overwrote that row's term
(observed: `glossary_terms`, `tool_calls`).

## 8. Frames 187 and 219, the contested tick and the decision id

0 of 0 contested wakes. No item went `contested`. Every item ends
`approved`, and no `tick:contested` wake ran (observed: `items`,
`sessions.wake_kind`). The reason: every correction contested a criterion,
a batch's files line or a ledger note, and no ruling contested an item. The
two challenges to the Vision Keeper, m63 and m74, woke challenge-mode
sessions, s175 and s189.

0 `decisions` rows whose author was the principal changed. All 10 principal
rows are at version 1 (observed: `decisions`). Frame 219's door fired once.
s175 sent `decisions.author(id='d_97657a8200', ...)` and got "d_97657a8200
is a decision by principal. A decision is its author's record, so write
yours under a new id." It then tried the Developer's `d_f504bd794d`, refused
the same way, and landed `d_1234567890`, an id it made up (observed: s175's
turns).

The residue is a supersede. s189 landed `d_74_challenge_ver_opt_show_py`, at
version 3, with `supersedes='d_565d2845d4'`, the principal's signoff
decision. Its text reads "must append the running Python version to the
message in the format "{command} {python_version}"". The principal had
written at m71, 6 sessions before, "not replace that message with just the
command name and the Python version" (observed: `decisions`, the m71
words). The principal's row is kept, so frame 219's line holds. The
decision that now stands says what he declined. That is candidate H.

## 9. Frames 173, 229, 228, 236 and 204

- Frame 173: 0 of 0. The admitted span writes are s122's on `utils.py`,
  s153's on `termui.py` and s190's on `decorators.py`. The merged diffs
  remove 0 statements: +12, then -1 blank line in bg_1, +8 in bg_2, +14 -4
  in bg_3, where the 4 removed lines are the `echo(...)` call kept in the
  new `else` branch (observed: `git diff --numstat`, `git diff`). No
  `"dropped"` note appears, and none was owed.
- Frame 229: 0 cycle-door refusals. The two "circular import" strings are in
  s18 and s88, cassette prose (observed: `turns`). The third night at 0 of 0.
- Frame 228: 0 `touch_strayed` wakes. `touch_strays` is empty. The third
  night at 0 of 0.
- Frame 236: 0 `touch_mistaken` wakes. The second night at 0 of 0.
- Frame 204, the fourth night of pass 2 (observed: `ledger`):

| Kind | Rows | Who wrote | Who answered | A merge waited |
|---|---|---|---|---|
| `conflict` | 3 | onboarding reconcile, `@prose` | the principal, at m11 and m14 | no |
| `scope` | 0 | | | |
| `default` | 13 | 4 resolved at signoff, 9 open, by the Developer, Tester, Terminologist and Vision Keeper | the principal for the 4 | no |
| `invented` | 2 | Terminologist `l_3d48f763a2`, Tester `l_51fa2a2e6c` | nobody, open | no |
| `other` | 3 | Developer s155 | nobody, open | no |

  The 3 `other` rows are the door's own three questions, copied as notes:
  "The obstacle is a rule of rota (a permission, a door, a tool) or the
  content of a row?", "If the note is wrong, who must say so: ...", "Did you
  pick, could you not pick, or did you not need to?" The text is
  `kind_questions` in `rota/roles/api.py:8900` (observed). That is
  candidate L. No walk wrote a `conflict`, so the ratio of conflicts an
  owner answered before the merge has no walk row on this night.

## 10. The merged code

Each merge against the principal's words (observed: `git diff` of
`2c8cd3a..002fbcb`, `002fbcb..517e61d`, `517e61d..a83cc50`, the jsonl):

**bg_1, `echo_json`.** The principal asked at m27 for "compact output from
the standard library json module, with no extra spaces after commas or
colons. The JSON goes on one line, and a single newline follows it", and
at m30 "echo itself should not change ... the new helper should sit beside
echo in utils.py with its own tests in the echo test file." The diff adds
`echo_json` at the end of `utils.py` with `json.dumps(obj,
separators=(",", ":"))` and writes to `_default_text_stdout()`. `echo` is
unchanged. The test sits in a new file, `tests/test_utils/test_echo_json.py`,
not in the echo test file. The encode door sent it there: "tests/test_utils/test_echo.py
is already inh_5f7b1750's file; two tests in one file overwrite each other
on disk." The three asserts check exact compact output with the newline, so
the test tests the criterion. Verdict: does what he asked. The test's file
is against his words, by a door.

**bg_2, `confirm(default_on_eof=False)`.** The principal said at m41 "the
flag defaults to False", at m46 "With the flag on and stdin closed, confirm
should return the default it was given", and at m50 "I'd expect the new
tests to go with the other confirm and prompt tests". The diff adds the
flag at `False` and returns `default` in the `except (KeyboardInterrupt,
EOFError)` branch. So with the flag on, Ctrl-C also returns the default,
which nobody asked for. The three tests sit in three new files at the tests
root, not with the confirm tests. `tst_confirm_eof_returns_default` and
`tst_confirm_eof_exact_default` assert `result.exit_code == 0` alone, and
neither reads the returned value, so `cr_2`, "exactly the default value", is
not tested. `tst_confirm_eof_raises_on_false` asserts `exit_code != 0`,
which a `TypeError` from the old signature also meets (reasoned: the
bodies). Verdict: the behaviour asked holds, the Ctrl-C path is extra, and
2 of 3 tests do not test their criterion. That is night 147's candidate F
shape.

**bg_3, `version_option(show_python=False)`.** The principal said at m66
"major.minor.micro, taken from sys.version_info", at m70 "It should also be
added to the end of the normal version message, not replace that message
with just the command name and the Python version", and at m81 "It should
not expect only the command name and the Python version." The diff's
docstring says "in the format "{command} {python_version}". This replaces
the default message." The code calls `echo(f"{prog_name}
{python_version}")` in place of the message. The test asserts
`expected_version in result.output`, which the declined output also meets.
Verdict: the merged code carries what the principal declined twice. The
test cannot see it.

Candidate E counts 1 of 3 merges on night 148, against 1 of 3 on night 147.
The chain on bg_3 (observed: `criteria`, `decisions`, `rulings`, the
sessions):

1. s182 specified "the output format must be "{command} {python_version}"
   where python_version is obtained from sys.version".
2. The principal contested line 2 at m70. s188 respecified the text to hold
   both "{command} {python_version}" and "appended to the end of the normal
   version message".
3. s189 wrote `d_74_challenge_ver_opt_show_py` with "{command}
   {python_version}" and superseded the principal's decision.
4. s190 committed `0252730` to the first half of the text.
5. The m81 verdict approved the decision and the test.
6. s203 answered m80 with `code.commit` and "nothing changed".

## 11. The other shapes

- Made-up turns, frame 181's family (the nightcount counter): 77 turns in
  22 sessions against 195 in 58. 10 turns in 6 sessions are cassette
  replays in onboarding. The walks hold 67 in 16, most in s148 (Architect
  annotate, 15), s122 (10) and s121 (8) (observed: `FABRICATED_RESULT` over
  `turns`).
- The landed commit after an invention, 2559537c: 0 writes after an invented
  result. s153 committed at turn 3. Its first made-up turn is turn 6, and
  turn 6's prompt already holds the sha (observed).
- Dangling pointers: 36 turns in 9 sessions. s24 (7) is a cassette replay of
  a reconcile. s122 (7) and s121 (6) are bg_1's Developers, which re-read
  `utils.py` after the cut (observed: nightcount).
- Repeated wakes, 5 groups: s130 and s131 (survey of `.` with no attest),
  s132 and s169 (Architect survey after each merge), s155 and s157, s191
  and s192, s193, s196 and s198 (observed: `nightcount.count`). The last
  three are the red chains below.
- bg_2's three reds: all three were s154's bodies with `runner.invoke(lambda:
  confirm(...))`, frame 230's shape, which the encode door admitted. The
  Developer challenged each test, s155, s157 and s160, with one escalation
  to the Architect, s159. The Tester fixed each in one wake, s156, s158 and
  s161. Seven wakes, 111 s of turn time (observed). Frame 230 reads 3
  bodies landed against 2 on night 145.
- bg_3's one red: s192's body had no `package_name`, and the decorator
  raised "test_version_option_show_python_flag is not installed". s197 put
  `package_name='test_version_option_show_python_flag'`, frame 223's shape,
  and stayed red. s199 put `package_name='click'` and went green. The
  Tester fixed it in two wakes, after three Developer challenges, s193,
  s196 and s198, a Researcher question and an empty Tester wake, s195.
  Frame 223 reads 1 of 2 bodies after a reasoned challenge green on the
  first run.
- Frame 222's import hint: 0 NameError hints fired (observed: `errs.py`).
- Frame 212's answer door: s200 sent `msg.answer_developer` four times and
  got "add no row to the refs of m76 ... Write what you found with
  decisions.author" each time. It wrote no decision and ended "with nothing
  done". s159 met the same door once and then landed m57. 1 of 2 Architect
  answer wakes ended with no answer.
- Frame 174, empty answers: m76's `unresolved_note` reads "the session woken
  by it wrote nothing and sent nothing", s195. 1 row.
- Frame 224: a register measure, no night sign.
- Frame 223: see bg_3's red above.
- Frame 241, the agenda's notes: 0 of 3 signoff pages, m22, m41 and m66,
  carry a note of another request.
- Frame 242's two lows: the `_` wildcard had nothing to delete, because
  `constraint_zero` was the only quarantined key and no approve named it.
  No `tick:unresolved` key outlived a closed ledger entry. 0 of 0 for both.
- Two stale questions to the principal (new, candidate N): `tick:unresolved`
  on m76 woke s200 and s201 after s199's test was green at harness run 4.
  s201 reported, and the Liaison asked the principal at m81 about a test
  that already passed. His answer changed nothing in the code. The chain
  s200 to s207 is 8 wakes, 108 s and 1 ask (observed: the log order,
  `messages`).

## 12. Candidate frames, new

- **G. The blindspot note puts a raw tick key on the principal's page.**
  Site: the Liaison's blindspot tick and the `gap` note it writes from
  `tick_attempts`, s89. Count: 1 page, 2 of 3 onboarding asks, m11 and the
  Liaison's m13. Price: 2 cycles.
- **H. Candidate E, again: the merged code carries the format the principal
  declined.** Site: the respecify text that keeps both formats, the Vision
  Keeper's challenge decision that supersedes a principal decision, and the
  clarify verdict's `approve`. Count: 1 of 3 merges, the second night
  running. Price: a scope read first, 2 cycles, then a design.
- **I. The re-annotate after a files-line contest keeps the files the
  principal declined.** Site: the Architect's relay mode and
  `batches.annotate`. Count: 2 of 2. s119 kept
  `tests/test_utils/test_echo_via_pager.py` after "the pager tests have
  nothing to do with this". s152 kept all ten `tests/test_defaults.py`
  grains after "they have nothing to do with confirm". s153 and s154 then
  tried to write `tests/test_defaults.py`. Price: 2 cycles.
- **J. `glossary.lookup` matches the term's case, and a survey amend
  rewrites another row's term.** Site: `glossary.lookup` and
  `glossary.amend` in `rota/roles/api.py`. Count: 2 fault rows, 1
  criterion's term ref unresolved. Price: 2 cycles.
- **L. The Developer logs the kind door's three questions as three notes.**
  Site: `kind_questions` and the `ledger.log` door. Count: 3 `other` rows,
  s155. Price: 1 cycle, a door text.
- **M. A criterion ruling relayed to the Terminologist ends in
  `glossary.adopt` on a criterion id.** Site: the Liaison's relay route for
  criteria rows. Count: 4 wakes, s114, s146, s205 and s206, every adopt
  refused. Price: 2 cycles. Low.
- **N. `tick:unresolved` escalates a challenge after its test went green.**
  Site: the `unresolved` predicate. Count: 1 chain, 8 wakes, 1 ask. Price: 2
  cycles.
- **F, again.** 2 of 3 bg_2 tests assert the exit code and not the returned
  value. Unpriced, low, beside frame 182.

## 13. For the sprint boundary

### 13.1 The open frames that this night's counts close

- Frame 238 closes on its ratio, 0 of 3 batches abandoned. The door did not
  fire, because no seat asked for `contested`. Its test covers the
  mechanism (reasoned: the ends-when names batches).
- Frame 239 stays validating. No batch was re-dispatched, so 0 of 0. All 3
  merges had a test per criterion.
- Frame 234 closes. Cancels at a correction: 0 of 3, and 0 of 6 over two
  nights. Over-contests: 0 of 5. The m81 approve of a faulted check is the
  ends-when's `revise` sign, so either keep it open for that, or close it
  and fold m81 into candidate H. The read recommends closing it with H,
  because H is the wall that spoiled the merge.
- Frame 237 closes. 0 of 5 quarantines, 5 of 5 calls.
- Frame 202 stays validating, 0 of 5. One night more, or 2 of 8 if night 147
  counts.
- Frame 240 closes. 0 of 3 walk ends.
- Frame 187 stays validating, 0 of 0 contested wakes.
- Frame 219 closes. 0 principal rows changed, the door refused the one try.
  The supersede by s189 goes to candidate H.
- Frame 233 closes. 4 minutes, 84 of 99, 5 of 5 cut turns replayed.
- Frame 173 stays open, 0 of 0. The ratio has no denominator.
- Frame 229 closes at three nights of 0 of 0. The door never fired in the
  three nights, so the close rests on its door test alone.
- Frame 228 closes at three nights of 0 of 0, on the same terms.
- Frame 236 stays validating, the second night of 0 of 0.
- Frame 204 stays validating, the fourth night of pass 2. 0 walk conflicts,
  no merge waited on a row. The seam night waits on Roman's order.

### 13.2 One order for the next sprint

By what cost the most steps or asks on this night first, then by price
(reasoned: the batch table and sections 1 to 12):

1. Candidate H, the declined format merged: a scope read, 2 cycles, then a
   design. bg_3, 54 steps, the m81 ask.
2. Frame 230, the lambda door: 2 cycles. bg_2's three reds, 7 wakes.
3. Candidate I, the re-annotate keeps declined files: 2 cycles. 2 of 2.
4. Candidate N, the unresolved tick after green: 2 cycles. 8 wakes, 1 ask.
5. Candidate G, the raw tick key on a page: 2 cycles. 2 onboarding asks.
6. Frame 212, the answer door: 2 to 3 cycles, an interview first. s200.
7. Frame 223, the package value: 2 to 3 cycles. 1 of 2.
8. Candidate J, the glossary lookup case: 2 cycles. 2 fault rows.
9. Frame 173, the span door: 3 cycles, no sign on this night.
10. Frame 222, the import hint: 2 cycles, no sign on this night.
11. Frame 241, the agenda's notes: 2 cycles, 0 of 3 on this night.
12. Frame 242, the wildcard and the raw writes: 2 cycles, 0 of 0.
13. Frame 174, the empty answers: 2 cycles. 1 row.
14. Candidates L and M: 1 and 2 cycles. Low.
15. Frames 224, 216, 217, 218, 214, 220, 211 and 116: no sign on this
    night, 2 to 3 cycles each. Candidate F: unpriced, low.

Rows 1 to 5 are about 10 cycles plus H's design, about 18 cycles with one
night, one sprint by the rule of 2026-10-11 05:51.

### 13.3 The next night's wall

No batch was cancelled, so no wall stopped a batch. The wall that cost the
most is candidate H: bg_3 took 54 steps and the night's last ask, and its
merge carries the format the principal declined at m70 and m81. Frame 230
cost bg_2 three reds and 7 wakes beside it. The next night's wall is
candidate H, with frame 230 beside it. H needs a scope read before a design,
so the next night is not a count night alone. Frames 239, 202, 187 and 236
still count on it.

The three merges cost 133 steps, 12 asks and 1.66 dollars on the walks: 32,
4 and 0.54; 47, 4 and 0.56; 54, 4 and 0.56. Night 147's three merges cost
300 steps and 25 asks, 101 and 9, 159 and 12, 40 and 4, and 3.63 dollars
for the night. Night 148 cost 2.12 dollars with onboarding, in 50 minutes
against 2 hours 17 (observed: both logs, the jsonl).
