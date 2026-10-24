# Night 160's read

Rota workflow, read by the meta workflow. Night 160 ran cold from
`C:/Users/roman/rota_night160` at 695e8be7, the branch head at 20:11, from
20:11 to 21:44 on 2026-10-23, on `D:/repos/_AI/sample_repos/clickI`, with
the agent principal on Opus (observed: `.rota/launch_night160.sh`, the
log). Records: `.rota/clickI_night160.db` (opened `?mode=ro`),
`.rota/night160.log`, `.rota/night160_report.txt`,
`.rota/night160_truth.txt`, `.rota/clickI.principal.jsonl`, and the clickI
repository (git read-only). Read on 2026-10-24 by one agent on Opus with
three extract agents on Opus. Their extracts are in the scratchpad `n160/`
directory: `a_bg2.md`, `b_bg1_walk3_liaison.md`, `c_doors.md`. The
synthesising agent checked the bg_2 red test body and the head docstring,
s255's respecify and answer turns, s231's hold, the discard lines of s189
and s191, the contested set at `api.py:11117`, and the principal's calls.

**The result.** Nothing merged, against 1 merge on night 159 (observed:
`.rota/night160_truth.txt`). The test loop held better than on night 159.
bg_1's wrong test was fixed by his words, and frame 304's and frame 308's
doors fired right each time (observed: section 1). The death moved one
step down, to the review. Both live items had code that does what he
asked, and both stopped at the Critic's lines check. That check wants an
added line of code copied from the diff. On bg_1 the seat could not copy
`(',', ':')` and the door named a phantom key. On bg_2 the criterion asks
for a docstring and the door refuses every docstring line (observed: W1).
bg_2 then died on a test of docstring wording, because its criteria hold
his notes about the checks and not behaviour (observed: W2). bg_3 was
cancelled by a wrong `revise` on its request line at 21:40, two minutes
before Ollama stopped (observed: W3). Walk 3 counts only up to 21:42.

## 0. The night in numbers

| Measure | Value |
|---|---|
| Phases | onboarding (107 steps, 3 asks), walk 1 20:13 (64 steps, 6 asks, quiet, "Stuck. The team gave up on: review for bg_1"), walk 2 20:36 (146 steps, 13 asks, quiet, "the code is written, but 1 test is still failing"), walk 3 21:36 (53 steps, 5 asks, quiet after Ollama failed at 21:42) |
| Steps, asks | 370 steps, 27 asks, 24 of them in the walks (night 159: 492 steps, 43 asks, 40 in the walks) |
| Batches | 3: bg_1 `echo_json` deferred at 8877b1b8, review tick quarantined, then parked by his m53; bg_2 `confirm_default_on_eof` deferred at f770f88d with 1 test of 37 red, 7 commits; bg_3 `version_option_show_python` abandoned, "its item is no longer schedulable", 0 commits |
| Merges | 0. "no merge into main after the reset at 20:11:10; 0 'rota: deliver' commits" (observed: the truth file). Night 159: 1 of 4 |
| Sessions | 314 sessions, 1373 turns (night 159: 413, 1897); Liaison 89, Vision Keeper 68, Terminologist 43, Critic 37, Developer 30, Architect 27, Tester 20 |
| Batch sessions | bg_1 24, bg_2 62, bg_3 7, no batch 221 |
| Failed seats | 24, s291 to s314, all `LLMUnavailable` or `RemoteDisconnected` after 21:42 |
| Principal | 24 live calls on Opus in the walks (6, 13 and 5), and onboarding 1 live and 3 replayed |
| CYCLE lines | 4: Developer tests_failing on bg_1 and Critic review on bg_1 (walk 1); Critic review on bg_2 and Developer verdict_failed on bg_2 (walk 2) |
| Verdicts | 2, both `fail` on bg_2 cr_3 (s188 at 6ed4f8b4, s248 at 905345ed). 0 pass verdicts landed all night |
| Made up | 74 turns in 35 sessions, "ran anyway: 0 writes after an invention" (night 159: 115 in 47) |
| Repeats | "18 wakes repeated, 69 sessions, 51 of them repeats" (night 159: 15, 44, 29) |
| Window | "dropped to fit the window" 159 turns in 24 sessions (night 159: 198 in 33); dangling pointers 51 turns in 13 sessions (s258 15, s117 8, s24 7) |
| After the end line | 135 turns in 54 sessions hold "Your work for this session is complete" (night 159: 212 in 96) |
| Rota failures | "Rota itself failed 3 times": 3 open `glossary.lookup` faults from s111 on the term "argument" (night 159: 17) |

(observed: `.rota/night160.log`, `.rota/night160_report.txt`, `sessions`,
`.rota/clickI.principal.jsonl`, 2026-10-24.)

The brief says "walk 1 went quiet after 146 steps and 13 asks". The log
gives those numbers to walk 2, which started at 20:36. Walk 1 went quiet
after 64 steps and 6 asks (observed: the log's "quiet after" lines).

**The end of walk 3 is not a wall of rota's.** The Ollama runner failed
to load at 21:42:17. The desktop app shut itself down at 21:42:42, after
it downloaded update v0.40.10 at 19:33 (observed: `%LOCALAPPDATA%/Ollama/app.log`
and `server.log`, as the brief gives them). Every seat from s291 to s314
failed with `LLMUnavailable`. The quarantines of
`vision_keeper|tick:contested`, `critic|tick:challenge` and the Liaison
ticks on version_option are these failures, not judgements (observed: the
report, tick attempts). Walk 3 measured one confirm, one shift page, one
approved page, one clarify (m143) and the touch page m147 with its wrong
cancel (observed: log lines 133 to 149). No Developer, Tester or Critic
ran on bg_3.

## 1. The held frames

**Frame 304, the arrange door. The count went against the frame, 2 of 2
batches deferred with the code right, from 1 of 4. But neither death was
this door's, and the door was right on its 1 fire.** The door fired once,
at s220 turn 3, on `tst_confirm_no_wait_on_eof`: "Line 7,
`mock_stdin.read.return_value = ""`, reads `mock_stdin.read`. The spec of
`mock_stdin` is `open`". A probe confirms the line raises `AttributeError`
(observed: extract C section 2). So the refused test could not have
passed. s220 then sent the same body ten times and got parse refusals, not
this door (observed). bg_1's code is right by his words at 8877b1b8:
compact JSON, then a newline, then a flush (observed: the diff). bg_2's
code returns the default at end of input with the flag on, from 6ed4f8b
on (observed: `git show f770f88`). Two defects stay at its head: the
`except (KeyboardInterrupt, EOFError)` branch also returns the default on
an interrupt, and a dead `prompt = _build_prompt` line sits above the real
call (observed: the head; reasoned: "when stdin is closed" names end of
input and not an interrupt). bg_1 died at the review (W1). bg_2 died on a
test that code can pass with the right docstring words (W2). By the
frame's third clause, neither cause is this door (reasoned).

**Frame 308, the answer door. Met on night 2: 0 partial answers of 8, and
every door fire right.** 12 Terminologist sessions woke on a ruling
relay, and 8 answers went out (observed: extract B section 3). 2 answers
went out with no landed respecify, m38 and m43 on bg_1. The "criterion
stands" route admitted both, and both were right, because his m35 and m40
asked for a test fix and not new words (reasoned). Night 159 had 5 of 5
such answers on bg_4, all wrong. The park door, "no change built from this
criterion has a commit yet", fired 4 times in s175, as cycle 3 says. Each
fire was right, because bg_2 had no commit until s176 (observed). The
landed-respecify door, "No respecify of cr_3 has landed in this session",
fired 8 times: s219 1, s246 1, s255 2, s265 4. All were right (observed).
s255 shows the door working. Its cr_3 respecify was refused three times
with "the principal contested these words", the answer was refused each
time, and m118 went out only after a cr_3 text landed (observed: s255
turns 2 to 6). One cost remains: s265 ended with no answer. And the text
that landed is still a note about a test, "Line 4's check must verify",
which the door does not read (W2).

**Frame 305, the line reader. Met on its counts: 0 wrong refusals of 7,
and 0 Liaison sessions that end on a repeated refusal of a line-2
contest.** The reader refused 7 times, all right by his words (observed:
extract B section 4). It cued "Line 3's check is still wrong" to line 3
and not line 4, the ledger line, in s140. It cued "Please don't drop this
change" and "I don't want to give up on this change" as words that do not
fault the batch line, in s152, s193, s209, s217 and s225. s140 ended on a
repeated refusal, but on the ledger line and not a line-2 contest. The
reader missed two rulings, by the words:

- **s290, "revise" on line 1.** His m148: "Line 2 is wrong: the Python
  version should show only when show_python is turned on ... Line 5 is
  also not what I asked for". The seat ruled line 1, the request,
  `revise`. The reader's `contested` set holds only `"contest"` values
  (observed: `rota/roles/api.py:11117`). So `_line_refusal` returns at
  `if not request_first or 1 not in contested` (observed:
  `api.py:10303`). The revise set the item to contested, and the
  scheduler cancelled bg_3 (observed: extract B section 6). The cancel is
  wrong by his words (reasoned). This is W3.
- **s169, "approve" on a change.** His m62: "Mostly yes, but the first one
  should also say that the flag is off by default". All three criteria
  were ruled approve. He said it again on m64 (observed). The reader does
  not read an approve against "but ... should also say" (reasoned).

So the counts are met, and the miss is outside the frame's predicate. The
words "Line 2 is wrong" were read right as a line. The fault is the
ruling verb, which the reader does not check (reasoned).

**Frame 272, the page-named replies. Met: 0 first sessions that contest a
line from an earlier page's reply, from 2.** Earlier replies in
`recent_chat` now carry row ids, for example "Row echo_json_helper of page
m34's check is wrong" (observed: s140's prompt). No old line number
reached a new ruling. s290's line-1 revise did not come from
`recent_chat`: m143 there says what m148 says (reasoned: extract B
section 6). Night 1 of 3.

**Frame 309, the journal. Met: the journal holds 763 rows, and the log's
21 "test(s)" lines add up to 763.** The live `test_runs` table holds 216
rows (observed: extract C section 5).

**Frame 283, the removal door. Met: 9 fires seen, all right; 0 landed
removals of a base statement with a note; 0 merges that hold one.** All 9
fires are the commit-note variant: s189 4, s191 3, s197 2 (observed:
extract C section 1). Each session had made one noted write that dropped
4 statements of base `confirm()`, and the tree still did not hold them.
Two more commits, s189 turn 18 and s191 turn 13, have no recorded result,
because neither session had a next turn. The hand-off's 11 holds only if
those two were refused too (reasoned). The unnoted variant, "No
criterion, request or ruling of the principal names", fired 0 times. The
diff `2c8cd3a..f770f88` removes 2 blank lines and nothing else (observed).
The second ends-when count, batches whose first red project test follows
an unnoted removal, is 0 of 2 (observed: bg_2's red test is its own).

**Frames 302, 303 and 306 on their night 1.**

- **302: met. 0 guess or annotate rows that name a source path not in the
  index, from 6.** The door refused 3 bare symbols, all right: s159
  `confirm`, s275 `version_option` and `show_python` (observed: extract C
  section 3). It admitted 2 new test files in an indexed test directory,
  `tests/test_utils/test_echo_json.py` and `tests/test_version_option.py`.
  That admission is by design (observed: `api.py:6214`, frame 302 review
  2).
- **303: met, and not exercised. 0 `propose` calls and 0 team rows under
  "You asked", from 1.** All 3 items trace to his own entries (observed:
  extract C section 4).
- **306: not met. His words on m84, m89, m94, m109, m114 and m121 did not
  reach the criteria as behaviour.** Each of the six says the line's text
  is "my note pasted in". s195 wrote cr_2 and cr_3 as notes about tests,
  and s255 kept that form after m114: cr_2 v15 "Line 3's check must give
  confirm an empty, closed input", cr_3 v8 "Line 4's check must verify
  that confirm()'s docstring explains" (observed: `criteria`). "Pass a
  default of True" (m114) reached the test `tst_confirm_no_wait_on_eof`
  v5 and no criterion. "Drop them", the comments (m121), reached nothing
  (observed: the test body, the head). The merge count is 0 of 0, because
  nothing merged.

**Frame 201, night 3 of 3. Not met: 0 wrong passes, because no pass
landed, and 1 Critic session of 1 with no verdict after the hold.** The
hold fired once all night, in s231 turns 7 to 10 on bg_2: "HELD
verdicts.emit: before the pass lands, answer for cr_1 ..., cr_2 ... and
cr_3" (observed: s231's turns). The seat sent the same pass four times
and ended with no verdict (observed). This is the shape that the register
showed on 2026-10-23: "the seat that reads 'send the call' sends the same
pass" (observed: frame 201's status of 15:17). In 19 of 20 review
sessions the lines door refused the pass before the hold could run
(observed: extract B section 2). So the hold had one live sample, and it
failed.

**Frame 301, night 3 of 3. Met, and not exercised: 0 refusals with the
stdin text for a test under `CliRunner`.** No test body used `input=`
(observed: extract C section 6). The stdin-close door fired 4 times, all
right (s196, s228, s247, s256). The NameError guard fired 4 times (s181,
s220 twice, s247). Three nights at 0, but this night held no body that
the predicate is about (reasoned).

**Frame 297, night 3 of 3. Met: 0 page notes found that cite uncommitted
lines, 0 inherited writes, 2 discards.** The runner discarded
`src/click/termui.py` at the end of s189 and s191 (observed: the account
lines in their last completions). s197's first commit returned "nothing
changed", so it did not inherit their writes (observed). The note check
is not exhaustive (observed: extract C section 7).

**Frame 257, claimed on cycle 1. The reading holds with one correction,
and the overwrite did not kill bg_1.** s111 sent 15 `criteria.specify`
calls on `echo_json_helper`, ticket tk_1, not 4. Four landed. Version 2
was "must end with exactly one newline character", and version 4 overwrote
it (observed: extract B section 1). The Tester encoded
`output.endswith("}")`, and s127 to s129 hit the attempt cap. His m35 and
m40 then fixed the test through the "criterion stands" route, and s144's
v3 passed (observed). So the overwrite cost one cycle and 2 asks (m34,
m39). bg_1 died later, at the review (W1). The count's reading holds:
the call admits a second text under a landed id on the same ticket
(observed: cycle 1, `api.py:5288`).

**Frame 311, pushed on cycles 3 and 4. Confirmed: 30 docstring refusals
in 15 Critic sessions, and 1 wrong fail.** The door is at `api.py:12478`
("holds {n} lines, and they are docstring lines") and `api.py:12554`
("does nothing that a criterion asks for") (observed: extract A section
2). By session: s198 1, s200 2, s229 2, s248 6, s205, s206, s207, s213,
s214, s215, s221, s222 and s223 2 each, s231 2 (one on cr_1, one on
cr_3). All others are on cr_3 (observed: `turns`). s248 then landed the
fail "A pass must name one added line of code ... No such line exists in
the diff for cr_3", which repeats the door's rule (observed: `verdicts`).
The Developer's moves after each fail:

- After s188's fail at 6ed4f8b4: s189 and s191 rewrote the whole function,
  dropped 4 base statements, and frame 283's door refused each commit.
  The runner discarded both trees. s197 committed 52a6817, a docstring
  sentence "Callers who do not enable this flag will still abort"
  (observed: extracts A and C).
- After s248's fail at 905345ed: s249 sent a commit with "docstring already
  explains", and the runner answered "nothing changed". s250 and s251 met
  the docstring-span refusal, "To replace docstring whole send start=297,
  end=329", then parse refusals, then the test-file door (observed: cycle
  4). s258 and s264 then committed 4a2a6af, 8c57d8e, 4dc41af and f770f88.
  These add only code comments, "return default immediately without
  waiting", and the dead line (observed: `git diff 905345e f770f88`). A
  comment never reaches `confirm.__doc__`, so the red test could not move
  (reasoned).

**Frames 258, 143, 140 and 266 at their residue rows.**

- 258: 1 contest on a line no sentence names, from 1: s290's revise on
  line 1 from m148, which names lines 2 and 5. It cost bg_3 (observed: W3).
- 143: 0 of 4 batch tests assert a value the criterion does not give.
  `tst_confirm_default_on_eof` v3 asserts `False` with no default passed,
  which is `confirm`'s own default (observed: the test bodies).
- 140: 0 landed writes carry a dropped note, and no project test went red
  (observed: extract C section 8).
- 266: 0 Liaison sessions end on a repeated parse refusal. The one session
  that did is the Tester s220 (observed: extract C section 8).

## 2. Every wall the night met

**Both live items had right code and died at or after the review. The
three largest walls are the Critic's lines check, criteria that hold his
notes about the checks, and a line-1 revise that cancelled a request**
(reasoned: W1 to W3). The night merged 0 of 3 items in 314 sessions,
against 1 of 4 in 413 on night 159 (observed: section 0).

| # | Wall and sign | Sessions | Asks | Place by section 4 |
|---|---|---|---|---|
| W1 | **The Critic's lines check refuses a right pass on both batches.** (a) bg_1: the diff is right and its test passes from s144. Five Critics, s145, s146, s148, s149 and s150, sent 28 pass emits and landed no verdict. The seat wraps `file.write(json.dumps(obj, separators=(',', ':')))` in single quotes, the dict splits, and the door names the phantom key "', ' is not a criterion of batch bg_1". When the seat changes the quotes it drops the comma. The door offered the right line as "nearest" in s145, s149 and s150, and no seat copied it (observed: cycle 2, extract B section 1). (b) bg_2: cr_3 asks for a docstring. The door refused 30 docstring lines in 15 sessions, and s248 turned its pass into a fail that quotes the door (observed: section 1, frame 311). (c) Each review quarantine sent him a page that says "The team stopped work on this change" (m45, m84, m89, m94, m114). He asked on m46 "What did the review object to?", and nothing answered (observed: W5) | bg_1 6 (5 Critics, s151); bg_2 about 26 (15 Critics, s249 to s251, the Liaisons s208, s216, s224, s252 and their rulings) | 5 (m45, m84, m89, m94, m114) | One door, `_pass_lines_check`, frame 170's lines check, with two causes. (b) is **cause 8**: the predicate "a pass names an added line of code" is not the fact "the diff does what the criterion says". Frame 311 holds it. (a) is **cause 9**: the refusal names the phantom key and not the quote, and it asks the seat to copy a token run the 9b model cannot copy. Frame 266 holds the fragment key for the Liaison's parser only, and frame 201 holds the loop sign. By step 1, one door with two open frames is one design frame: the Critic names a line by its number in the diff, and a documentation criterion takes a docstring line. 3 cycles (reasoned: 311's 2 plus 1 for the number route) |
| W2 | **bg_2's criteria hold his notes about the checks, so the last test checks wording.** s195 wrote cr_2 and cr_3 as "Line 3's check must ..." and "Line 4's check must ...". He said six times that the text is "my note pasted in" (m84, m89, m94, m109, m114, m121). s255's landed cr_3 v8 still reads "Line 4's check must verify that confirm()'s docstring explains ... without waiting" (observed: `criteria`, s255 turn 4). s256 then encoded v7 of `tst_confirm_help_documentation`, line 12: `assert 'returns the default' in doc.lower() and ('without waiting' in doc.lower() or 'immediately' in doc.lower())`. The head docstring says "returns the default value on EOF rather than waiting", which meets his words and fails the test (observed: the test body, `git show f770f88`). This test was red at 905345ed (attempt 14) and at f770f88d (attempt 16), and it is the only red test (observed: extract A section 1). The Developers could not edit the docstring: the span door asks for the whole docstring, 297 to 329, and their rewrites did not parse. So they added comments, which cannot change `__doc__` (observed: W6) | about 18 (Terminologists s195, s211, s219, s227, s246, s255, s265; Testers s199, s201, s203, s220, s228, s230, s247, s256; Developers s257, s258, s264) | 6, shared with W1 (m84 to m121) | **Cause 1** at the Terminologist hop: his words about a page line and its check become criterion text. The mechanism is **cause 10**: the Terminologist has no route for a note about a check except the criterion's text, so "pass a default of True" reached the test only through a criterion rewrite (reasoned: s255's calls). Frame 306 holds it, and its first ends-when part is the provenance read. The read is 1 cycle, and the fix is 2 to 3: a note about a check goes to the Tester, and a criterion that names a page line or "check" is refused at `criteria.respecify`, with s195 and s255 as red tests |
| W3 | **A "revise" on line 1 cancelled a request he wanted built.** His m148 named lines 2 and 5 of the touch page m147. s290 ruled line 1, the request, `revise`, and the reader did not check it, because `contested` holds only `"contest"` (observed: `api.py:11117` and `10303`). The revise set the item to contested, and `do:cancel: abandoned bg_3: its item is no longer schedulable` followed (observed: the log, `predicates.py:1548`). Ollama failed two minutes later, so the night could not have built bg_3 in any case (observed: the log) | 1 (s290) and bg_3's 7 | 1 (m147) | **Frame 258's sign** and **cause 8 on frame 305's reader**: the predicate checks a contest of line 1 and not a revise. A case on frame 305, with r_b517f1bc53 as the red test: the line-1 checks read `revise` as they read `contest`. 1 cycle (reasoned: one predicate line and a test). s169's approve on "Mostly yes, but ... should also say" is a second case on the same reader, read before the fix |
| W4 | **The criterion that held his newline was overwritten.** s111's fourth landed specify on `echo_json_helper` replaced "must end with exactly one newline character" (observed: section 1, frame 257). The Tester encoded `output.endswith("}")`. s127 to s129 tried to remove the newline and failed on their own write text (observed: cycle 1). His m35 and m40 fixed the test, and both respecifies were refused because the seat named a test node as a surface (s136, s143) (observed) | about 17 (s111 to s144) | 2 (m34, m39) | **Cause 8** on `criteria.specify`, wrong not to fire. Frame 257 holds it, with its count done. 2 cycles, as priced |
| W5 | **The page after a review with no verdict says the team stopped work, and he parked bg_1 on that belief.** m45: "The team stopped work on this change." His m46 asked what the review objected to. s152's ruling approved all lines, and no seat answered or restarted the review (observed: extract B section 1). On the shift page he answered m53, "Line 1 is approved and built, and it needs nothing from me, so leave it", while its review was quarantined (observed) | 2 (s151, s152) | 2 (m45, m53) | **Cause 11**: what reaches him is not the state. No open frame holds it. A new frame: a review that landed no verdict is named so on the page, and a shift page names a parked batch's stuck tick. 1 cycle |
| W6 | **The Developer cannot edit a docstring.** The span door answers a write inside a docstring with "To replace docstring whole send start=297, end=329". s250 and s251 tried, and the texts did not parse, once because the text began with `:param` at column 0 (observed: cycle 4). The later seats wrote comments, and s264's f770f88 says "remove stray comments" and adds the dead line `prompt = _build_prompt` (observed: extract A section 2) | 5 (s250, s251, s257, s258, s264) | 1 (m121, "comments aren't executable code") | **Cause 9**: the refusal points the seat to a 33-line rewrite it cannot make. No open frame holds it. An interview of s250 first, 1 cycle, before any door change |
| W7 | His onboarding m6, "Drop those lines", was not carried out. The Architect s93 made no call, and the 11 constraints remain (observed: extract B section 7) | 2 (s93, s99) | 1 (m6) | Not placed. Plausibly **cause 10**, a drop with no call in the Architect's mode. Not read |
| W8 | The quarantine of `constraint_zero` at onboarding, a fifth night | 1 | 0 | Not placed. Extract B reasons a disagreement on prose-only areas, which this database cannot show |
| W9 | Turns after "Your work for this session is complete" (135 in 54 sessions), window drops (159 in 24), made up (74 in 35), repeats (51 of 69) | about 100 | 0 | All down from night 159 but the repeats, with 24% fewer sessions. Frames 139 and 208 hold the window signs. Not read |

(observed: extracts A, B and C, `turns`, `tool_calls`, `criteria`,
`tests`, `test_run_journal`, `verdicts`, the pages in
`.rota/clickI.principal.jsonl`, the clickI repository, 2026-10-24.)

**bg_1: one wall or two.** Two, one after the other (reasoned). W4 put a
wrong test in front of right code, and his words fixed it through the test
route. W1 then refused every pass on a quote split that has nothing to do
with the criterion's text. W5 left it parked. Cycle 1 called the first
quarantine "bg_1's death". It was not. bg_1 died at the review.

**bg_2: the test that stayed red, and the rungs.**

1. At 905345ed the one red test was `tst_confirm_help_documentation`.
   Attempt 12 failed on "docstring must mention that callers who do not
   enable the flag still abort at end of input". Attempt 14 failed on line
   12 of v7 (observed: `test_run_journal` seq 614 and 688).
2. At f770f88d the same line 12 failed, attempt 16 (observed: seq 762).
   The other two tests pass from attempt 5 on.
3. The review rungs: s198 to s248, 15 Critic sessions, 4 review
   quarantines, each one a page to him and a reset by his answer (observed:
   the report's wakes).
4. The ladder after `tick:exhausted`: s232 Developer `verdicts.load`; s233
   Architect `msg.challenge_vision_keeper`; s234 Vision Keeper
   `decisions.author(id='d_1234567890')`; s235 report; s236 Liaison
   clarify m103; s237 relay; s238 Architect `model.adopt(ids=['bg_2'])`
   (observed: extract A section 3). No rung named the docstring door or
   the wording test (reasoned).
5. The verdict_failed rungs after s248: s249 to s251 and s257 with no
   commit, then s258 and s264 with comment commits (observed: the
   report's batch list).
6. At the walk-2 end the log says "the code is written, but 1 test is
   still failing". Walk 3's shift page then parked bg_2 behind
   version_option, by his m135 (observed).

**His words on m84, m114 and m121.** They reached the tests and not the
criteria. m84 asked the check to close stdin first: `tst_confirm_no_wait_on_eof`
v5 sets `sys.stdin = StringIO('')`. m114 asked for a default of True: v5
passes `default=True`. m121 asked to drop the comments: they stay
(observed: the test bodies, the head). Each said the line's text is his
note, and cr_2 and cr_3 stayed notes (W2).

## 3. The request line

**The request line killed one item, bg_3, by a ruling verb, and it held
everywhere else** (observed: W3). The costs left on the line:

1. **A revise on line 1 that no sentence names.** m148 named lines 2 and
   5. The reader does not check a `revise`, and a revise on the request
   cancels the batch (W3). This is frame 258's own sign, with frame 305's
   reader as the site.
2. **A needless clarify.** m143 asked "Should the version_option include
   the Python version in its message". The item text already says so. His
   answer added "off by default", which the page m147 then still missed on
   line 2 (observed: the log; reasoned).
3. **The team rows held.** 0 `propose` calls, 0 team rows under "You
   asked" (observed: frame 303).
4. **The guess held.** 0 source paths outside the index. The 2 admitted
   new test files are by design (observed: frame 302).

## 4. The agent principal's asks and tokens

28 calls on Opus: 1 live and 3 replayed at onboarding, then 6, 13 and 5 by
walk (observed: the log's `principal:` lines and the jsonl). The 24 live
calls in the walks are 18 pages, 3 clarify questions and 3 confirms
(night 159: 40 calls, 24 pages, 13 clarify, 3 confirms). He read 29.6k
characters of pages and wrote 5.4k characters of answers, about 7.4k and
1.4k tokens at four characters a token (night 159: 56.7k and 10.7k
characters) (observed: the jsonl; reasoned: the ratio). The harness gives
no token count. Asks per merge: 24 for 0 merges. bg_2 took 13 of his
answers. Six of them say that the criterion text is his note pasted in
(observed: W2). Five pages told him "The team stopped work on this
change" when a review had landed no verdict (observed: W1, W5).

## 5. What the next night should be held on

**Hold the next night on the review: a right diff gets a verdict, and a
criterion keeps behaviour and not his notes about a check** (reasoned: W1
and W2). The test loop moved on this night: the wrong bg_1 test was
fixed, and frames 304 and 308 fired right. Both deaths moved to the
Critic's lines check and to criteria that describe tests. The order, with
a price per row:

| Rank | Row | Cycles |
|---|---|---|
| 1 | **The Critic's lines check as one design frame, frame 311 with the fragment-key case** (W1): a documentation criterion takes a docstring line, and the Critic names an added line by its number, so no seat copies quotes. s205 and s148 are the red tests | 3 |
| 2 | **Frame 306's provenance, then its route** (W2): a note about a check goes to the Tester, and `criteria.respecify` refuses a text that names a page line or a check. s195 and s255 are the red tests | 1 for the read, 2 to 3 for the fix |
| 3 | **The reader reads `revise` on line 1 as it reads `contest`** (W3), a case on frame 305 with r_b517f1bc53 as the red test, and s169's approve read first | 1 |
| 4 | **The page names a review with no verdict** (W5), a new frame under cause 11, with m45 and m53 as the cases | 1 |
| 5 | **Frame 257's door**, a second specify of one id in one session is refused (W4), its count done | 2 |
| 6 | **The Developer's docstring edit** (W6), an interview of s250 before any door change | 1 |
| 7 | **Frame 201's hold**: s231 re-sent the same pass four times. Its night 3 did not validate it. Decide after row 1, because the lines check hides the hold in 19 of 20 sessions | 1 for the decision |

Night 161 then measures frames 302, 303, 304, 308, 272 and 283 on their
night 2, frames 305 and 306 after their rows, and frame 201's hold, which
night 160 sampled once. Frames 297 and 301 close their three nights at 0.
Frame 301 met no body its predicate is about on any of them (observed:
section 1). Frame 309 is met.

Check that Ollama runs and that its desktop app will not update itself
before the launch. The night lost walk 3 to an update that the app
downloaded at 19:33 and applied at 21:42 (observed: the brief's
`app.log` reading). This is an operating fact, not a wall of rota's.

## Usage

The three extract agents ran on Opus, each with a cap of 60k tokens, and
each went past it: A 101.1k, B 147.9k, C 120.7k by the harness counter
(observed: the harness usage lines). Their own counts were lower, 57k,
105k and 70k. A did not read s195's door results or map 4a2a6af to
4dc41af to sessions. A also said that s255's answer went out with no
landed respecify, and that bg_2's turns hold no discard line. The
synthesising agent read both and found them wrong: m118 went out after
cr_3 landed, and s189 and s191 end on a discard line (observed: s255
turns 4 to 6, the completions of s189 turn 19 and s191 turn 14). C did not
count frames 258 and 143, and the synthesising agent counted them. Not
read on this night: the turns of W7, W8 and W9, s188's first fail on
"help text", and why s189's and s191's last commits have no result.
