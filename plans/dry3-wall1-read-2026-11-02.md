# dry3 wall 1 read: the onboarding baseline of 235 rows is too long for one call, and the run says rest while the survey still runs (2026-11-02)

Reader: an agent of session ce483c7b, read-only at 234b118b on `rota/foundation`. The copies are `dry3w5`, `dry3w6` and `dry3w7` in the scratchpad of ce483c7b, and `dry1w14` and `dry2w5` in the scratchpad of 208997ee. The reader did not open the live dry3 database or `C:/Users/roman/rota_dry3/`. The probes are in `.../ce483c7b-.../scratchpad/w11read/`.

## Result

1. Wall A is not frame 358's re-survey: the three Liaison sessions s174 to s176 ran before the merge, on the first onboarding baseline of 235 rows ("glossary_terms:99, constraints:114, model_areas:22"), and each first reply was cut at 23,463 characters while it copied the 235 ids, which the door adds by itself (observed: `sessions`, turn 6 output lines 17 and 35, sandbox.py 4314 to 4321).
2. The stopped page m39 then fed a loop: the re-survey's writes to rows in the key lifted its quarantine, so m39 said "after 0 attempts", his "Drop it" landed as `contest` and not as a drop, and on dry3w7 the predicate offers the same 235 rows again, with a fourth Liaison session s207 held at the hand stop (observed: `tick_attempts` in dry3w6 and dry3w7, `r_m44`, `oe.py`; reasoned: db.py 1052 and principal.py 3482 to 3484).
3. No open or parked frame covers wall A or wall B, and m39 is the rowless-key line of frame 354 and not a park page of frame 330, so 'try again' or 'drop' on thirty-plus of the team's own rows is no act that fits a careful person (observed: the headings and `state`; reasoned: section 4).
4. Wall B happened once and not twice: the rest line "Nothing waits on you and nothing is building." printed only on turn 2, because `render_state` reads asks, batches and stopped keys and never the frontier, and a further find is that `rota run` never reaps a dead claim, so turn 8 ran 0 sessions with "every ready role is busy" (observed: grep of the turn outputs, principal.py 306 to 588, boot.py 63 to 82 and its one caller in cockpit/server.py 671).
5. The reach of wall A is 1 model wake that grows with the project, `tick:observed_entries`, and 3 places that inherit its size, and on dry1 and dry2 the same wake ran 3 times with 10 to 21 rows and never quarantined (observed: predicates.py, the copies; reasoned: section 5).
6. The smallest fix for wall A is a size bound in `observed_entries` that takes the existing lazy path past one page of rows, at about 3 cycles, and it needs Roman's ruling because the election is "the principal's call", while wall B is a frontier read in `render_state` at about 2 cycles, and wall A is the bigger issue by the purpose line (reasoned: section 6).

## 1. Find

The order of turn 6 (observed: `b5rq8vxu8.output`, the step lines): cycle 11 is `liaison<-tick:quarantined`, and cycle 29 is `do:merge()` with "[merged bg_1]". The merge commit `4f12af1e` is dated 20:27:37, inside turn 6, 19:29 to 21:06 (observed: `git log` on icalendarI). The brief says the merge came on turn 7. The copies say turn 6 (observed: `batches.status = 'merged'` in dry3w6).

| Step | Session | What happened |
|---|---|---|
| Wake 1 | s174 | `tick:observed_entries`, detail "glossary_terms:99, constraints:114, model_areas:22", 235 refs of names such as `alarm`, `calendar#src_icalendar_cal`, `src/icalendar/timezone`. Tools: `msg.present_principal` only (observed: `brief.list` refusal in s176, "available: msg.present_principal"). First reply: one call `msg.present_principal(refs=['alarm', ...` of 23,463 characters. The list runs past its end and repeats, `'vweekday'` 8 times, until the output budget cuts it. The door: "ERROR reply cut: your reply was cut at the output budget before it ended ... the last call did not run". 25 turns, 575,581 characters in and 398,456 out, no write (observed: `turns`, `tool_calls`). |
| Wake 2 | s175 | The same first reply, 23,463 characters, the same cut. Later turns try a triple-quoted string ("refs are ids, and 'alarm, alarm#src_icalendar_tests_events,' is not one"), then `round_no=0` inside the list ("'round_no=0' names no row"), then "'[' was never closed". Reply 8: "I am unable to fulfill this request because the list of references provided is too large to be included in a single tool call." 11 turns, no write (observed). |
| Wake 3 | s176 | The same first reply. Reply 6: "I have no tool to map these names to IDs, and I am forbidden from inventing IDs for existing rows." 8 turns, no write (observed). |
| Why no row | all three | The predicate waits for a `present` whose `body_refs` hold the rows. None was sent. At temperature zero the three first replies are byte-identical, so attempts 2 and 3 buy nothing (observed: three lengths of 23,463; reasoned: `loop.py` 307 to 313 says this of night 88). |
| Quarantine | runner | The key `liaison|tick:observed_entries|alarm,alarm#src_icalendar_tests_events,...` is quarantined at 3 (observed: turn 6 line 17, "1 abandoned: observed_entries for alarm, ..."). |
| Report | s177 | `tick:quarantined`, one ref, the key itself, as `rowless_key` adds it (observed: `wake_refs`). Reply 1 copies the 235 names again and fails, "unterminated argument list". Reply 2 sends `msg.present_principal(refs=[235 names], round_no=0)` of 2,261 characters, and the door reads the names as parts of the woken key, so m39 carries the key (observed: `tool_calls`, `messages.m39.body_refs`; sandbox.py 4322 to 4327). |
| Lift | s191 to s196 | The re-survey after the merge writes `glossary.amend` 5 times and `model.describe` on `.` and `src/icalendar` (observed: `tool_calls`). Each is a row in the key. `_lift_quarantines` lifts every quarantined key whose refs hold the moved row, `pairs=True` (observed: db.py 1052). In dry3w6 the key has no row in `tick_attempts` (observed). |
| m39 as rendered | page | Line 1 `how_it_works`. "The team gave up on a step:" line 2 "the team could not finish a step for alarm, alarm#src_icalendar_tests_events, ... src/icalendar/timezone after 0 attempts", all 235 names, not thirty. "Reply 'try again' on a step to run it again. Reply 'drop' on it to stop it." Footer "'ok' approves this page, and nothing is built." Lines 3 to 7 are the read-backs of m6, m19, m20, m21 and m27 (observed: `probe_pages.py dry3w6 m39`, and the turn 6 agenda). |
| Answer | s203 | m44: "Line 2: I do not know this step and I did not ask for it. Drop it. The rest is right." `rulings.rule(rulings={"2": "drop", "3": "ok", ..., "rest": "approve", "c2": "none"})` on the second call (observed). |
| Landing | land | `r_m44` per_item: the key `contest`, the five readings and `how_it_works` `approve` (observed: `rulings`, `ruled_refs`). `_step_verdicts` maps 'drop' to `approve` only for a key that `rowless_key` still finds quarantined (observed: principal.py 3482 to 3484, `_STEP_ROWS` = `{'try again': ('contest', ...), 'drop': ('approve', ...)}`). The key was lifted, so 'drop' became a contest (reasoned). |
| Verdict | s205, s206 | m46 to the Liaison. s205 relays m47 to the Architect with 21 area refs as contested. s206 tries `model.adopt` twice and ends: "Adopting is blocked by the contested ruling. No further action possible." (observed) |
| The 8 notes | scheduler | `l_55619eb7a3`, author `scheduler`, kind `other`, status `parked`, about `canonical_order_duplicate_keys`: "After the merge the team re-read the project and recorded these notes: ["alarm#src_icalendar", "availability", "conference", "icalendar_alarms", "icalendar_caselessdict", "icalendar_config", "icalendar_enums", "image"]". No session wrote it. `do:resurvey_note` wrote it through `loop._perform` (observed: dry3w6 `observed_entries` returns `do:resurvey_note` with 8 refs; the ledger row in dry3w7). |
| After turn 7 | dry3w7 | The key `liaison|tick:observed_entries|...` again, attempts 1, quarantined 0. `claims` holds `liaison`, `s207`, with no session row and no checkpoint. The predicate returns `liaison tick:observed_entries 235 glossary_terms:99, constraints:114, model_areas:22` (observed: `oe.py dry3w7`). |
| Turn 8 | run | One step, "idle: every ready role is busy", 0 sessions. Outstanding `agenda n=1` and `observed_entries n=1`, both the Liaison's (observed: `b521btnhh.output`). The claim of s207 holds the Liaison, and `rota run` reaps no claim, because `boot.reap_claims` runs only from `core.boot.boot`, which only `cockpit/server.py` 671 calls (observed: grep). |

Why the rows were never on file as presented (observed: predicates.py 683 to 691): `presented` reads the `body_refs` of every `present`. m39's refs are the key, `how_it_works` and the readings, not the 235 ids. So the put-once rule never closes these rows, and the predicate offers them again after every lift (reasoned).

Wall B in brief (observed: the turn outputs and `sessions` per copy):

| Turn | Steps | Sessions | Last line |
|---|---|---|---|
| 1 | 40 | 40 | "stopped at the 40-session limit", then "Waiting on you: 2 things." |
| 2 | 40 | 37 | "stopped at the 40-session limit", then "Nothing waits on you and nothing is building. 5 things approved so far." Outstanding `survey n=16` and `constraint_zero n=1`. |
| 3 | 40 | 27 | "stopped at the 40-session limit", then "Waiting on you: 3 things." (m14, m16, m18). Outstanding `survey n=22`, `term_collision n=6`. |
| 4 | 40 | 40 | "stopped at the 40-session limit", then "Waiting on you." (m26). Outstanding `challenge n=11`. |
| 5 | 22 | 22 | "quiescent after 22 sessions (357s)", then "Waiting on you." (m33). |
| 6 | 40 | 35 | "stopped at the 40-session limit", then "Waiting on you: 3 things." (m38, m39, m40). |
| 7 | killed | 5 in the copy | "run exit 127" at 21:35, stopped by hand. |
| 8 | 1 | 0 | "idle: every ready role is busy", then the Done line. |

The brief says turns 2 and 3 printed the rest line. Only turn 2 did (observed: `grep -c "Nothing waits"`, 2 hits, both in `br0ama7td.output`). On turns 1, 3, 4 and 6 a page waited, so the seat had an act and ran again (reasoned).

## 2. Match by symptom

- **Frame 358, open.** It keeps re-survey rows off the page (observed: `resurvey_rows`, `do:resurvey_note`, predicates.py 704 to 721). That path worked on dry3: 8 rows, one ledger row, one state line (observed). The 235 rows are onboarding rows, offered before the first merge, so frame 358 does not reach them (observed: the order of turn 6). Its footer part worked: m39 says "nothing is built" (observed). Frame 358 does not cover wall A.
- **Frame 357, open.** A drop on a team row is "his objection on file" (observed: 6e5306b7). Line 2 is a stopped step and not a row, so frame 357 does not apply (reasoned).
- **Frame 266, open.** "unterminated argument list" is s177's last error (observed). The error is a sign and not the cause, because the 235-id list breaks the call in every form the seat tried (reasoned).
- **Frame 327, open.** The `refs` door refusal. s175 met "refs are ids" when it passed one string (observed). A sign, not the cause (reasoned).
- **Frame 264, parked.** The account rows and an observed row that cannot change. Near in subject, not the size (observed: the heading).
- **Frames 253, 276, 157, 87.** A quarantine key on the state page, a quarantine page for a contested item, the cockpit frontier, a key that outlives a deferral (observed: the headings). None names a wake too large to answer, or a lift by a re-survey.
- **Frame 354, closed 2026-11-01.** It built the rowless key as its own ref and the 'try again' and 'drop' menu (observed: the archive heading, conditions 3 and the review notes in principal.py 3079 to 3087). m39 is that design working on a key it was not sized for (reasoned).
- **Frame 330, parked.** Its park page is for a batch with a spent ladder (observed: the heading). m39 names no batch, so it is not a park page under frame 330 (observed: `park_owns` reads a batch, principal.py 3528 to 3533).
- **Wall B.** No open or parked frame names the session limit, the rest line or a dead claim (observed: `python -m rota.tools.state`, the stack headings). Frame 354 named the limit for the click survey cost and closed (observed).

Is m39 the right page? By the code, yes: nothing stops quietly, and a rowless key gets its own numbered line (observed: principal.py 3073 to 3076). In meaning, no. The step is the team's own baseline, his attention is asked for 235 names, and both offered acts fail: 'try again' reruns a byte-identical reply, and 'drop' landed as a contest because the key had gone (reasoned: section 1). The read-backs of m6 to m27 ride every present by the seam design, 2.3 (observed: the `reading:` refs). They do not belong under a stopped step that he did not ask for, because "The rest is right." then rules six lines with one sentence (reasoned).

## 3. The purpose and the provenance

- The wake carries the ids: 24b02ea1, 2026-08-26, "the observed offer names its rows, because Liaison cannot fetch them" (observed: git). The same commit made the door add the wake's refs to a present: "added, never substituted ... what it cannot enumerate must arrive enumerated" (observed: sandbox.py 4314 to 4321).
- The prompt asks the seat to copy every id: 08231e54, 2026-09-09, from tipsK, "Put them to the principal with **one** `msg.present_principal` whose refs are **every id in your wake's refs**" (observed: git, `observed_entries.md`). The measured case had 2 to 3 rows a page over 8 sessions (observed: the prompt). The build workflow wrote both, and the reader found no ruling of Roman on either (reasoned: the commit bodies cite tipsK and a sandbox case).
- So since 2026-09-09 one Liaison wake carries every observed row of an onboarding in one call, and the seat copies what the door already adds (reasoned).
- The one-page rule: "One page, once the rows are all there" (tipsM, 2026-09-09, observed: the predicate's docstring).
- Frame 358's passes 1 to 1c, 2026-11-02 (19feac1a, e7e8e829, 7720c05c, a84a1cf4), changed only which rows count as onboarding rows. The onboarding baseline still goes out as one wake with every row (observed: predicates.py 704 to 806).
- The 40-session limit: `drive(... limit ...)` in `onboard_run.py`, 90f09152, 2026-08-11, "a tick that cannot drain", and `rota run --limit` default 40 at 111899b4, 2026-08-19 (observed: git blame).
- The rest line: 9c5c71fe, 2026-09-08, "A stopped run looked like a thinking run. render_state composes the state once: what waits on you, what shipped, what is stuck." (observed: the commit body, principal.py 578 to 582).
- The rest line does not read the outstanding wakes. `render_state` prints it when no ask, no running or pending batch, no stopped key and no aside line exists (observed: principal.py 306 to 588 has no `frontier` call). The run's own line "stopped at the 40-session limit" comes first, in machine words (observed: onboard_run.py 118 to 119).
- The lift: "A quarantine holds while its subject is unchanged. A write that moves the subject is the exit" (observed: db.py 1020 to 1053). A key of 235 refs has 235 subjects, so any survey write exits it (reasoned).

## 4. What a careful person meant, and what the code offered

**Wall A.** He asked for one change in `caselessdict.py` (observed: m1). After the merge he should see the Done line, the merged change and at most one line about the team's own notes, the shape frame 358 built (reasoned: the purpose line and frame 358's design). On a project of 2,794 grains, a page of 235 observed rows asks him to confirm the team's reading of the whole library before his one change. That is work he did not ask for (reasoned: `plans/composition.md`, purpose). The code offered him a numbered step with 235 names, 'try again' or 'drop'. 'try again' cannot succeed, because the reply is the same at temperature zero (observed: three replies of 23,463). 'drop' is the right word, and the code then lost it (observed: `contest` in `r_m44`). Neither act ends the loop, because the rows were never on file as presented (reasoned: section 1). The seat's answer, "I do not know this step and I did not ask for it", is the purpose line in his words (observed: m44).

The code already has the right end: `rota elect lazy` defers every observed row to the ledger with no session and no page (observed: cli.py 800 to 816, predicates.py 784 to 792). Nothing asks the careful person to elect, and the config row was empty on dry3 (observed: `config` has no `baseline_election` value). So the eager path is the default by absence (reasoned).

**Wall B.** When a run stops at its limit with wakes outstanding, the line should say that the team is still working and that a new run goes on, for example "The team is still reading the project: 16 steps wait. Run again to go on." (reasoned). On turn 2 a careful person alone reads "Nothing waits on you and nothing is building." as rest, and nothing tells him to run again (reasoned). The line above it, "stopped at the 40-session limit", could make him try once more, but 9c5c71fe says the principal's line is the one that counts (reasoned: the commit body). Turn 8 is the same reading in a worse form: the Done line and "idle: every ready role is busy", with the Liaison held by a dead claim for ever (observed). A careful person after a reboot cannot know that the cockpit's boot is the only reap (reasoned).

## 5. The reach

Wall A. The places where one wake or one record carries a set that grows with the project (observed: the files; the count is reasoned):

1. `observed_entries`, predicates.py 669 to 806: one Liaison wake with every onboarding row, and a prompt that asks the seat to copy them all. This is the one model wake whose refs grow with the project.
2. `tick_quarantined`, predicates.py 1924 to 1957, with `rowless_key`: the quarantine wake inherits the key as its ref, and the key carries every ref of the stalled wake. s177 tried to copy them again (observed).
3. The stopped-step line, principal.py 3073 to 3087: `_gave_up_words` prints every ref of the key on one line, 235 names on m39 (observed).
4. `_lift_quarantines`, db.py 1052: `pairs=True` lifts a key on a write to any of its refs, so a large key cannot stay quarantined through a re-survey, and his ruling on it then lands on no step (observed: dry3w6; reasoned).

The other wakes with a list of refs are bounded (observed: the code). `tick:agenda` holds at most `PAGE_ASSUMPTIONS` = 7. `tick:reconcile` groups prose files and splits a quarantined group (frame 354). `tick:term_collision` is one term. `awaiting_confirm`, `slicing`, `grouping` and `signoff` grow with the request, not the project. `do:defer_baseline`, `do:resurvey_note` and `tick:constraint_zero` are scheduler acts with no model.

The count on the dry runs (observed: `sessions` and `tick_attempts`, read-only):

- dry1 (dry1w14, 1,188 grains): 2 Liaison `observed_entries` wakes, s142 with 21 rows ("glossary_terms:14, constraints:5, model_areas:2") and s287 with 15 rows ("constraints:15"). 0 quarantined.
- dry2 (dry2w5, 29 grains): 1 wake, s50 with 10 rows. 0 quarantined.
- dry3 (2,794 grains): 3 wakes with 235 rows, 1 quarantine, 1 fourth wake held at s207.

The bound sits between 21 and 235 rows (reasoned). The reader did not measure where the cut starts. It depends on the Liaison's model, `gemma4:12b-it-qat` on dry3 (observed: turn 1 output), and on `max_tokens`.

Wall B. The places that print rest while wakes are outstanding (observed: grep):

1. `render_state`, principal.py 578 and 581, two lines in one function.
2. Its callers: `onboard_run._say_where_we_are` at the limit stop, the idle stop, the quiescent stop and the model stop, and `rota agenda`, cli.py 751. The limit stop and the idle stop can end with wakes outstanding. The quiescent stop cannot, because the frontier is empty (reasoned: onboard_run.py 64 to 70).
3. The dead claim: `loop.step` skips a role with a claim, loop.py 280 to 292, and `rota run` never calls `reap_claims` (observed). The Done line then reads as rest (observed: turn 8).

On dry3 the rest line printed 1 time in 8 turns, and the idle stop with a dead claim 1 time (observed).

The term-collision clarifies m14, m16, m18 and m26 are an ask the composition allows. Two senses of one word is an obligation by f6ac0c5b, 2026-08-14, and a conflict only he can settle is a page he always sees (observed: git; the comment at scheduler.py 799 cites DECISIONS.md, "The seat's four pages are one surface"). They share the sign of frames 357 and 358, rows of the team's that he did not ask for, and `component` or `jCal` has nothing to do with `canonsort_keys` (reasoned). He answered each in one sentence and the run went on (observed: m19 to m27), so the cost was low on dry3. They are not a wall now. If a larger project puts tens of them to him, they join wall A's question of what onboarding may ask him before his request (reasoned).

## 6. The proposal

**Wall A, at `observed_entries`, predicates.py about 794 to 806.** When the fresh rows are more than one page holds, take the lazy path that exists: return `do:defer_baseline` with the rows, and show one state line, "The team read the project and recorded N notes. Ask me to show them.", in the shape of frame 358's re-survey line. Below the bound, keep the page, and change the prompt line to "call `msg.present_principal` with the first id only; the door adds every row of your wake", because the door already does (reasoned: sandbox.py 4318 to 4321).

- It covers places 1 to 4 of the reach: no model wake carries the large set, so no quarantine, no stopped line and no lift loop follows (reasoned).
- Price: about 3 cycles. The predicate branch with a red test from the dry3w6 rows, 2 cycles; the prompt line, 1 cycle in the same pass; one review (reasoned: frame 358's actual of 4 cycles for the same shape, and `plans/operating-facts.md` line 250).
- It leaves out: the 235-name stopped line and the `pairs=True` lift for any other large key; the lost 'drop' on a lifted step (principal.py 3482); the dead claim on `rota run`; and whether a project of 2,794 grains is in the destination at all, which says "a small Python repository" (reasoned).
- It changes a page the seat gets and a prompt's shape. It also decides the election by size, and the code says "It is the principal's call and nothing else's -- no session decides it" (observed: cli.py 800 to 804, 05fbe247, 2026-08-26). So it needs a design page and Roman's ruling. The question for him opens with that ruling and its date, by the rule of 2026-10-25.

**Wall B, at `render_state`, principal.py about 576 to 582.** Read `frontier(conn, principal_present=False)` before the rest line. When wakes wait, print "The team is still working: N steps wait. Run again to go on." in place of "Nothing waits on you and nothing is building.". Separately, call `reap_claims` at the start of `rota run`, cli.py `cmd_run`, so a hand stop does not hold a role for ever.

- It covers places 1 to 3 of wall B's reach (reasoned).
- Price: about 2 cycles for the line with a red test from the dry3w2 copy, and 1 to 2 cycles for the reap with a test from the dry3w7 claim (reasoned: a door text or a number is 2 cycles).
- It leaves out the cost of the cold survey on a large project: 4 runs of 40 before the first present page (observed: section 1). The limit of 40 stays.
- It changes a state line and not a seat's form, a prompt's shape or a door family, so it needs no ruling by that rule (reasoned). The doubt is that "Run again" is an instruction to him, and the reader found no ruling on whether the state line may tell him to run (reasoned).

Doubt:

- The reader did not test that `msg.present_principal` with one id lands all 235 rows. Frame 354 made the door refuse an empty list (observed: frame 354, condition 3), and the reader did not trace the order of the add and the check.
- The bound between 21 and 235 rows is not measured. A count of the id characters against `max_tokens` on the Liaison's model would place it.
- The lift by the re-survey is reasoned from db.py 1052 and the absence of the row in dry3w6. The reader did not replay the writes of s191 to s196 to see which one lifted it.
- Turn 8 ran on the live database, not on dry3w7. The claim of s207 is in the copy, and the busy line is in the output, so the match is strong but not proven (reasoned).
- m40, "Before I build this ... Reply 'ok' to go ahead.", reached him after `bg_1` had merged in turn 6. A touch note waits on nothing by R7, so this is by design, but a careful person reads it as a gate (observed: the turn 6 agenda; reasoned). The reader did not read it further.

Which wall is bigger, by the purpose line "no work happens that the Principal did not ask for, and no work stays invisible": wall A (reasoned). It breaks both halves. It puts 235 of the team's rows on his page, his 'drop' does not stop it, and the offer comes back after every lift, on every project of this size. Wall B breaks the second half once per cold start, and the next page he gets corrects it.

## Probes

All in `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/ce483c7b-be58-4d58-bfc4-db1081518842/scratchpad/w11read/`, read-only on the copies:

- `q.py`, `t2.py`, `t3.py`, `probe_pages.py`: copied from `w10read`. `probe_pages.py` renders m39 on dry3w6.
- `u1.py`, `u2.py`, `u3.py`: the user text of a turn, with long lines folded.
- `res.py`: the door's results per turn.
- `msgs.py`: every message in one line.
- `rr.py`: `r_m44` and its `ruled_refs`.
- `oe.py`: `onboarding_phase` and `observed_entries` on dry3w5, dry3w6 and dry3w7.

## Usage

About 125k tokens by the reader's estimate, against the cap of about 100k. The reader had no harness counter in view. Most of the excess was the 235-id lists inside the session dumps.
