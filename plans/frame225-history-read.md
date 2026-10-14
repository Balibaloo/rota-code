# Frame 225, pass 2: the history read for candidate D

Meta workflow. Read-only history read on Opus, brief `read225_brief.md` in session 58da19ca's scratchpad, 2026-10-14. The question: does candidate D of `plans/night146-read.md` section 13 need a ruling from Roman, or does the history settle it?

## 0. The answer

The history settles candidate D, and no question goes to Roman (reasoned: sections 1 and 2). Roman's words of 2026-09-03 rule that elicitation runs at intent-time. They say nothing about the fold. The ruled text in `rota/DECISIONS.md` says "contest with words goes back to the desk that assumed it". It does not say that the item is contested. The clause "even where the principal approved that row in the same breath" is in one place only: the docstring of a test that the build session wrote in commit 8018c376. That clause is a meta workflow design choice, and it carries the build session's reason, "they rejected the reading". On night 146 the principal rejected no reading. On m191 he wrote "Ok, approved. One thing to add". On m251 he wrote "Ok, that's what I asked for. Line 2 just repeats line 1". So the premise of the clause fails on 2 of 2 pages.

One constraint holds candidate D to the ruled text. The principal's words on the contested default must still reach the desk that took the default. Today they reach it through the contested tick. Under candidate D they need another carrier, for example a `revise` on the item or the relay's words beside the approve. If they do not reach the desk, the fix repeats review 1's high of 2026-10-13: "his 'no' reaches no desk" (reasoned: `plans/frame225-review-1.md` as the stack's status of 2026-10-13 01:02 quotes it). On m190 the addition "default to False" reached the item text only through the contested wake s328 (observed: section 3).

## 1. What A1 said, and the case it was written for

The name "A1" is the responsibility audit's first universe item, "eliciting what the principal wants, including what he did not think to say". It is not a ruling's number (observed: `rota/DECISIONS.md` line 1343, 2026-10-14).

Roman's typed words around the ruling, from the build transcripts (observed: `C:\Users\roman\.claude\projects\d--repos--AI-Custom-AI-TUI\280f8821*.jsonl`, script `scratchpad/r225/roman_msgs.py`, 2026-10-14):

- 2026-09-03 12:26: "so it feels like it doesent have any planning ability, / Like if i say i want a CRM or something, it should ask me a billion questions / I want that"
- 2026-09-03 12:30: "oh right yes, this is a missing top level capabilty right?"
- 2026-09-03 12:40: "lets do this now / this is a usability priority / / do we have a design?"
- 2026-09-04 12:25: "2 i always wanted the liason to infer the decision allocation, wait do we now have the ability to ammend and reply to things that the principal is asked to approve?"

The transcripts of `d--repos-rota` start on 2026-09-16, so the 2026-09-03 session sits under the older project directory `d--repos--AI-Custom-AI-TUI` (observed: first timestamps of the 25 dates in `d--repos-rota`, 2026-10-14). This read used that directory with the same filter. That is a deviation from the brief's path, because the brief's path holds no message from 2026-09-03.

The ruled entry in `rota/DECISIONS.md`, "The seed interview runs at intent-time" (ruled: Roman, 2026-09-03, "lets do this now, this is a usability priority"), says: "Approve is the keypress that takes the default (a decision under the principal's name resolving the entry ...); contest with words goes back to the desk that assumed it."

The case it was written for: "tip calculator pls" was read by three desks as three programs, and nobody asked for the inputs (observed: `rota/DECISIONS.md` lines 1345 to 1352). The case is a silent point that a desk filled with a default, shown to the principal so that he can take it or overrule it.

The sentence "a contested assumption contests its row" comes from the design plan, not from Roman:

- `plans/a1-seed-interview-at-intent.md` line 48, the table row for "contest, with words": "the default is overruled at the keypress ... and the row the assumption was about is contested, so its owner amends it through the contested loop with `principal_said` in front of it" (observed: the file, 2026-10-14).
- Lines 76 to 79 give the reason. The first draft gave the relay seat `decisions.author`, and the model wrote "fourteen decisions a session, five of five". So "Both rulings on an assumption close at the keypress instead, and a contested assumption contests its row, which the contested loop already amends from `principal_said`" (observed: the file, and `git log -S` finds it first in cb1765d6, 2026-10-14).

So the item contest was the carrier that took the principal's words to the owner. The carrier replaced a tool that the model misused. It was not a rule about the item's approval (reasoned: lines 76 to 79 name the carrier as the reason).

## 2. Did A1 or a later ruling consider an approve of the item beside a contest of its default?

The build session considered the case. Roman did not rule it (observed: the sources below, 2026-10-14).

- Commit 8018c376, 2026-09-04 13:27, wrote `per_item[row["about_ref"]] = "contest"` with no check of the item's own ruling. The test `test_contesting_an_assumption_overrules_it_and_contests_its_row` lands `per_item={"how_it_works": "approve", "L1": "contest"}` and asserts `{"how_it_works": "contest", "L1": "contest"}` (observed: `git show 8018c376:tests/rota/test_signoff_assumptions.py` lines 132 to 161).
- Its docstring says: "contests the row the assumption was about, even where the principal approved that row in the same breath: they rejected the reading, so the owner amends it through the contested loop with `principal_said` in front of it" (observed: the same file, line 135 to 138).
- The commit message says "a contested assumption contests its row" and "A1 at intent-time (ruled 2026-09-03)". The "ruled" mark covers intent-time elicitation. The fold is the build session's mechanism (reasoned: the DECISIONS entry above holds no sentence about the item).
- No typed message by Roman between 2026-09-02 and 2026-10-14 in either transcript directory names the same-page case. The keyword filter "assumption", "default", "contest" found 2 messages in the 2026-09-02 to 2026-09-05 window and 11 after it, and none is about the fold (observed: `scratchpad/r225/out2.txt` to `out4.txt`, 2026-10-14).
- `git log -S "overruled at signoff"` lists 8018c376 and then build and plan commits only, df474208 and fca24dbc among them. No commit records a ruling by Roman on the case (observed: 2026-10-14).

The Liaison briefs read against the fold, not for it:

- `rota/roles/prompts/liaison/agenda.md`: "An approved line becomes a decision. A contested line goes back to the desk that took the default." It says nothing about the item (observed: lines 12 to 14, 2026-10-14).
- `rota/roles/prompts/liaison/submit.md`: "The principal may approve an item while its assumption stays open" (observed: lines 12 to 13, last changed b519a246, 2026-08-10).

The claim of the stack's status of 2026-10-13 00:55, "ruling A1 of 2026-09-03, a contested assumption contests its row even where the same answer approves the row", joins two sources. The first half is a plan line that the build session wrote. The "even where" half is a test docstring that the build session wrote. Neither is Roman's words (reasoned: the quotes above). The claim's mark "ruling" is a copied claim. It stays (reasoned) until a quote of Roman is found.

One fact changed after 2026-09-04. Commit b57772f5 of 2026-09-10 makes the Liaison infer `per_item` from the principal's words (observed: `git log -1 b57772f5`). On 2026-09-04 a contest on a line was the principal's own act. On night 146 both the item approve and the note contest are the Liaison's reading of one reply. So the docstring's premise, "they rejected the reading", now depends on the Liaison's classification of a sentence (reasoned: b57772f5 and the replies in section 3).

## 3. Night 146: m190 and m250

All rows read from `.rota/clickI_night146.db` with `mode=ro` (observed: 2026-10-14). On each page, line 1 is the item and line 2 is the Vision Keeper's `default` note (observed: `messages.body_refs` of m190 and m250).

**m190.** The ruling is `r_ffa9a2eac0`, `per_item` `{"confirm_default_on_eof": "approve", "l_cd78147ada": "contest"}`.

- The note `l_cd78147ada`, kind `default`, author `vision_keeper`: "The confirm() function will now accept a default_on_eof flag, allowing it to return a default value when stdin is closed instead of aborting."
- The principal's reply m191: "Ok, approved. One thing to add to line 2: the flag should default to False, so nothing changes for people who already call confirm."
- The decision `d_43f1814a9c`: "overruled at signoff: Ok, approved. One thing to add to line 2: ... (was assumed: ...)".
- The verdict m192 and the relay m193 carry `["confirm_default_on_eof"]` to the Vision Keeper, and the night's read says the relay carried `contest` and s328 set the item `contested` (observed: `plans/night146-read.md` section 7).
- The item's text after the night includes "which defaults to `False`", so the addition reached the item. The item's approval at the end of the night is `contested`, version 9 (observed: `items`).
- The cost: no batch was live (observed: `plans/night146-read.md` section 7). The item went through more pages after this one. At m218, m226 and m233 the principal contested the item with "Line 1 is not in my words any more", and at the end the item was parked (observed: `rulings` r_73d1452fb2, r_b700a45acd, r_df870c9cad, r_fb3eb554ee). This read did not trace whether s328's rewrite caused those three contests.

**m250.** The ruling is `r_8b2329d2da`, `per_item` `{"version_option_show_python": "approve", "l_cee175bedd": "contest"}`.

- The note `l_cee175bedd`, kind `default`, author `vision_keeper`: "The `version_option` will include a `show_python` flag that appends the running Python version to the message."
- The principal's reply m251: "Ok, that's what I asked for. Line 2 just repeats line 1, so it doesn't add anything. The Python version should come from the running interpreter's version info, shown as major.minor.micro."
- The decision `d_8ce5debe17`: "overruled at signoff: Ok, that's what I asked for. Line 2 just repeats line 1 ...".
- The cost: the `tick:contested` wake s399 wrote "The `version_option` will display the running Python version as major.minor.micro without requiring a flag". s402 approved the text, bg_6 built on it, and the principal contested the rewrite at m259, so bg_6 was cancelled before a build (observed: `plans/night146-read.md` sections 1 and 4, lines 42 and 339 to 347). The item's final text has the flag back, and its approval is `approved`, version 8 (observed: `items`).

In both replies the principal approves the item and adds a detail. Neither reply rejects the default's reading. On m251 he calls line 2 a repeat of line 1, which agrees with the default (reasoned: the quoted words).

## 4. The recommended answer

1. The history settles candidate D. No question goes to Roman (reasoned: sections 1 and 2).
2. Roman ruled elicitation at intent-time and "contest with words goes back to the desk that assumed it". He never ruled the item's approval on that path.
3. "Even where the same breath approves" is the build session's test docstring of 2026-09-04, with the reason "they rejected the reading".
4. Since 2026-09-10 the Liaison infers both rulings from one reply. On night 146, 2 of 2 replies approved and added a detail, and rejected nothing.
5. So an explicit approve of the item wins over a contest inferred on its default. Pass 1d's precedence for the other kinds already holds this.
6. Keep the ruled half: the decision with the words resolves the note, and the words reach the Vision Keeper.
7. The carrier for the words must change, because the contested tick is today's only carrier. Use a `revise` on the item or the words on the relay beside the approve.
8. Without that carrier, candidate D reopens review 1's high. m190's "default to False" reached the item only through s328.
9. Change the test of 8018c376 and its docstring in the pass, and cite this record as the reason.
10. Correct the stack's mark of 2026-10-13 00:55 from "ruling" to the build session's design, with this record as the pointer.

A draft question, for use only if the holding session reads the ruled text differently. [med]: an edit to the fold and a test depend on the answer, and no GPU hour or composition line does.

> You ask a builder to fit a new door. The foreman shows you the plan, and under it his own note: "the door opens inwards". You say "Yes, that's the door. One thing to add: make it white." Today the foreman hears a complaint about the note, so he tears up the plan and redraws the door, and the builder stops. If the approval wins, the plan stays, the builder carries on, and the foreman adds "white" to the plan. If the complaint wins, as today, the foreman redraws first, and sometimes he redraws more than you asked. It is like a waiter who takes "the steak is fine, but no salt" as a complaint and sends the whole plate back to the kitchen. Which reading do you want?

## 5. Counts and usage

- Roman's typed messages read: 77 in the 2026-09-02 to 2026-09-05 window (headings only, 4 in full), and 13 keyword hits in all windows.
- Quotes of Roman on the same-page case found: 0.
- Night 146 pages with an item approve beside a `default` contest: 2, and 2 of 2 replies approve and add a detail.
- Batches cancelled by the fold on those pages: 1, bg_6 through s399.
- Token usage: about 45k by this agent's own count of its context, against a cap of 80k. The harness line is the authority.
