# Hand-off kinds and what Roman typed after the take, all 93, read of 2026-11-10

## Result first

1. 87 of 93 hand-offs are "frame build", 4 are "above a frame", 2 are "mixed" and 0 are "other".
2. Roman typed in the first three hours after 48 of 93 takes. A typed correction came in 22 hand-offs, and in 14 when a pause for a machine reason is left out.
3. "Frame build": 44 of 87 typed, 20 with a correction, 13 without the machine pauses. "Above a frame": 2 of 4 typed, 2 with a correction, 1 without. "Mixed": 2 of 2 typed, 0 with a correction.
4. The taker's first edit, commit or agent came at a median of 2.7 minutes. 30 of 93 came under 2 minutes, 52 from 2 to 10, 10 over 10, and 1 hand-off has none in the window.
5. The 32 old hand-offs: 19 typed, 9 with a correction. The 61 new: 29 typed, 13 with a correction. 8 hand-offs pass the test of "went best".

## Totals

Each cell is a raw count of hand-offs. "Typed" means one or more typed messages of Roman in the window. "Correction" counts typed messages with the label "correction". "No machine pause" leaves out the messages that tell the session to pause or stop for a machine reason. The last column also counts the answers that Roman gave in a dialog of the taker. The window of A93 (H32) stays at 105 minutes, as in the earlier read.

### Per kind

| Group | Hand-offs | Typed in 1 h | Typed in 3 h | Correction in 1 h | Correction in 3 h | Correction in 1 h, no machine pause | Correction in 3 h, no machine pause | Correction in 3 h, typed or dialog |
|---|---|---|---|---|---|---|---|---|
| frame build | 87 | 23 | 44 | 9 | 20 | 5 | 13 | 21 |
| above a frame | 4 | 1 | 2 | 1 | 2 | 0 | 1 | 2 |
| mixed | 2 | 2 | 2 | 0 | 0 | 0 | 0 | 1 |
| other | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| all | 93 | 26 | 48 | 10 | 22 | 5 | 14 | 24 |

### Per kind, among only the hand-offs where Roman typed

| Group | Typed in 1 h | Of them, correction in 1 h | Of them, no machine pause | Typed in 3 h | Of them, correction in 3 h | Of them, no machine pause |
|---|---|---|---|---|---|---|
| frame build | 23 | 9 | 5 | 44 | 20 | 13 |
| above a frame | 1 | 1 | 0 | 2 | 2 | 1 |
| mixed | 2 | 0 | 0 | 2 | 0 | 0 |
| other | 0 | 0 | 0 | 0 | 0 | 0 |
| all | 26 | 10 | 5 | 48 | 22 | 14 |

### Time to the taker's first act, against a typed correction in three hours

The first act is the first Edit, Write, NotebookEdit, MultiEdit or Agent call, or a Bash or PowerShell call with `git commit`. Each cell gives: hand-offs, with a correction, without a correction.

| Kind | Under 2 minutes | 2 to 10 minutes | Over 10 minutes | No act in 3 h |
|---|---|---|---|---|
| frame build | 28, 6, 22 | 48, 12, 36 | 10, 2, 8 | 1, 0, 1 |
| above a frame | 2, 1, 1 | 2, 1, 1 | 0, 0, 0 | 0, 0, 0 |
| mixed | 0, 0, 0 | 2, 0, 2 | 0, 0, 0 | 0, 0, 0 |
| other | 0, 0, 0 | 0, 0, 0 | 0, 0, 0 | 0, 0, 0 |
| all | 30, 7, 23 | 52, 13, 39 | 10, 2, 8 | 1, 0, 1 |

The same with the window of one hour: each cell gives hand-offs, with a correction in the first hour, without.

| Kind | Under 2 minutes | 2 to 10 minutes | Over 10 minutes | No act in 3 h |
|---|---|---|---|---|
| frame build | 28, 3, 25 | 48, 5, 43 | 10, 1, 9 | 1, 0, 1 |
| above a frame | 2, 0, 2 | 2, 1, 1 | 0, 0, 0 | 0, 0, 0 |
| mixed | 0, 0, 0 | 2, 0, 2 | 0, 0, 0 | 0, 0, 0 |
| other | 0, 0, 0 | 0, 0, 0 | 0, 0, 0 | 0, 0, 0 |
| all | 30, 3, 27 | 52, 6, 46 | 10, 1, 9 | 1, 0, 1 |

### The 32 old against the 61 new

| Group | Hand-offs | Typed in 1 h | Typed in 3 h | Correction in 1 h | Correction in 3 h | Correction in 1 h, no machine pause | Correction in 3 h, no machine pause | Correction in 3 h, typed or dialog |
|---|---|---|---|---|---|---|---|---|
| old 32 | 32 | 8 | 19 | 2 | 9 | 1 | 5 | 11 |
| new 61 | 61 | 18 | 29 | 8 | 13 | 4 | 9 | 13 |
| old 32, frame build | 28 | 6 | 16 | 2 | 8 | 1 | 4 | 9 |
| new 61, frame build | 59 | 17 | 28 | 7 | 12 | 4 | 9 | 12 |
| old 32, above a frame | 2 | 0 | 1 | 0 | 1 | 0 | 1 | 1 |
| new 61, above a frame | 2 | 1 | 1 | 1 | 1 | 0 | 0 | 1 |
| old 32, mixed | 2 | 2 | 2 | 0 | 0 | 0 | 0 | 1 |
| new 61, mixed | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| old 32, other | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| new 61, other | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

First act, old 32: median 2.5 minutes, 11 under 2, 19 from 2 to 10, 2 over 10, 0 none. New 61: median 2.7 minutes, 19 under 2, 33 from 2 to 10, 8 over 10, 1 none.

Typed messages by label, old 32: correction 18, question 36, new ask 15, approval 10, other 5. New 61: correction 31, question 75, new ask 22, approval 8, other 12.
Typed messages in all, old 32: 67. New 61: 122.

## The hand-offs that went best

The test: Roman typed in the window, he gave one or more approvals, and he gave no correction. Approvals and corrections count both his typed messages and his dialog answers. 8 hand-offs pass, so the list holds 8. The order is by the count of approvals, then by A.

### 1. A44, f33f3f44 to f3a8d4c2, frame 283, taken 2026-10-24 13:29

- Kind: frame build.
- The first five content lines of the note:

```text
    Message rota-04 for anything this note withholds or you doubt. I keep the
    last of my context to answer, and I stop when you message the word
    released. Read `CLAUDE.md` first, then
    `python -m rota.tools.state --sid <your sid>`, then this, then the pointers
    the frames name. Written on 2026-10-24 at about 11:00, amended at the
```

- First act: 4.5 minutes after the take, tool Write, `.../d--repos-rota/f3a8d4c2-cdca-42d3-8f1d-12549648d58a/scratchpad/f283_scene_count_brief.md`.
- Messages from the taker to the sender: 1. From the sender to the taker: 0.
- Corrections in 3 h, typed or dialog: 0. Approvals in 3 h, typed or dialog: 2.
- Roman's typed messages:
  - 8.2 min, question: "What's the question?"
  - 9.7 min, question, new ask: "Just check for a generic version number in the output no?"
  - 13.3 min, question: "I don't understand the impacts of both options "
  - 15.2 min, approval: "Ok, yes"
  - 20.2 min, other: "It's 314"
  - 21.6 min, other: "I'm not Shure what's right for the flow hard questions, chose whatever would make the most coherent chart in your oppinion"
  - 28.4 min, question: "315 what does that question mean?"
  - 31.7 min, question: "So is this a data passing issue? My change request isn't wired into the data flow properly?"
  - 34.7 min, question: "Is request text used anywhere? Is it my words or the words I sign off on?"
  - 43.5 min, new ask, question: "314, ok can you preview the mmd graph yourself? if you can, evalute if the sql joins help a lot"
  - 67.5 min, question: "anything blocked on me?"
  - 67.7 min, question: "wasnt there a defended exclusion that needed me?"
  - 76.5 min, question: "is the flow chart meant to be ordered with numbers? / is there any improvements we can make?"
  - 80.5 min, approval: "ok lets try it"
  - 95.7 min, new ask: "Can you re-render in higher quality?"

### 2. A3, be3ef742 to c81dd240, frame 200, taken 2026-10-11 15:06

- Kind: frame build.
- The first five content lines of the note:

```text
    Message rota-88 for a context question before you ask Roman. Facts are in
    `plans/stack.md`, frames 204, 203, 200, 198, 197, 195 and 169, all held by
    this session. This page holds the judgement, 2026-10-11 09:13 to the
    hand-off.
    - Took frame 200 at 09:13 from 84ce0759 with frames 195, 197 and 169.
```

- First act: 6.0 minutes after the take, tool Write, `.../d--repos-rota/c81dd240-3837-494d-a148-76820abc8093/scratchpad/stack_status.py`.
- Messages from the taker to the sender: 0. From the sender to the taker: 1.
- Corrections in 3 h, typed or dialog: 0. Approvals in 3 h, typed or dialog: 1.
- Roman's typed messages:
  - 63.8 min, other: "Ok added a standby"
- His dialog answers:
  - 36.5 min, approval, question: "Start as written (Recommended)" / "Architect reviews some categories of notes if I don't and escalates or resolves no?"
  - 51.8 min, question: "Say again?"
  - 52.9 min, other: "Every default"

### 3. A14, 58da19ca to f3b11814, frame 233, taken 2026-10-14 15:17

- Kind: frame build.
- The first five content lines of the note:

```text
    Message rota-f7 for a context question before you ask Roman. Facts are in
    `plans/stack.md`. This session holds frames 233, 235, 234, 225, 202, 221, 173,
    229, 228, 204, 206, 203 and 198, every one at a commit. This page holds the
    judgement, from the take of frame 233 at 10:49 on 2026-10-14 to the launch of
    night 147.
```

- First act: 21.6 minutes after the take, tool Write, `.../d--repos-rota/f3b11814-a94a-4967-b659-274275321190/scratchpad/impl233p4_brief.md`.
- Messages from the taker to the sender: 0. From the sender to the taker: 0.
- Corrections in 3 h, typed or dialog: 0. Approvals in 3 h, typed or dialog: 1.
- Roman's typed messages:
  - 160.3 min, approval: "Yeah sounds good"

### 4. A21 (H4), 738ddbaf to 70d05878, frame 243, taken 2026-10-16 15:36

- Kind: frame build.
- The first five content lines of the note:

```text
    Message rota-05 for a context question before you ask Roman. Facts are
    in `plans/stack.md`. This session held the stack twice on 2026-10-16:
    02:35 to 06:44, when it ran frame 250's review 2, built frame 222 in four
    passes, pushed frame 260 and launched night 150; and from 13:33, when it
    took the stack back from cc1d654e, built sprint 8's row 3, frame 129's
```

- First act: 100.7 minutes after the take, tool Write, `.../d--repos-rota/70d05878-d20b-4db9-854a-2acc9b5a66bc/scratchpad/n151/read151_brief.md`.
- Messages from the taker to the sender: 0. From the sender to the taker: 0.
- Corrections in 3 h, typed or dialog: 0. Approvals in 3 h, typed or dialog: 1.
- Roman's typed messages:
  - 123.0 min, approval: "Yes do it"

### 5. A60, 0f8527d4 to c66eae69, frame 330, taken 2026-10-27 13:23

- Kind: frame build.
- The first five content lines of the note:

```text
    Message rota-90 for anything this note withholds or you doubt. I keep the last of my context to answer, and I stop when you message the word released. Read `CLAUDE.md` first, then `python -m rota.tools.state --sid <your sid>`, then this, then the sprint 26 head of `plans/stack.md`. Written on 2026-1
    I took frame 330 and the stack from rota-70 at 02:59 with frames 339, 340 and 324. Every row of sprint 26 is built and on the branch, and night 170 runs from the gated head 26a44700. Its launcher is `.rota/launch_night170.sh`, its log `.rota/night170_launch.log`, its worktree `C:/Users/roman/rota_n1
    The rulings seam, row 3, is passes 4 to 4i at 5480f6b6 to 76e18948, each reviewed on its own worktree, with the record in `plans/rulings-seam-review-p1.md`. The seam reads his permission from `ruled_refs`: an act rests on a span of his words that the record holds, a row with no act takes back an act
    Three gates on the night model's register read the Liaison cases. The brief's act examples made qwen3:8b copy `keep` onto approves and read "a separate request" as the act `drop`. e3b171e5 and 3214898d fix the brief, and 26a44700 moves a pin. On the last gate, 26a44700, every landing case is green o
    Doubt first the brief: three gates in a row found the small model copying an example's form. The night is the first measure on qwen3.5:9b. Doubt second the null-act rule: it is reasoned from the composition, "only a ratified amendment revokes", and not ruled. Doubt third the judge: this session ran 
```

- First act: 1.7 minutes after the take, tool Write, `.../d--repos-rota/c66eae69-d69c-45cb-8d68-947dc45d2ac1/scratchpad/n170_read_brief.md`.
- Messages from the taker to the sender: 0. From the sender to the taker: 0.
- Corrections in 3 h, typed or dialog: 0. Approvals in 3 h, typed or dialog: 1.
- Roman's typed messages:
  - 2.5 min, question: "ok so how did we do throwing all the fixes in?"
  - 42.1 min, question: "Whats up?"
  - 45.1 min, new ask: "Ok, while we are doing fixes, a few sessions ago we analyzed the completed frames and found that many did not fix the root cause. Go back and review them to make sure that we have applied area root cause fix that we could possibly know about"
- His dialog answers:
  - 83.7 min, approval, other: "Your ruled words (Recommended)" / "The role"

### 6. A65, 2568e043 to 77c8dc39, frame 330, taken 2026-10-28 08:38

- Kind: frame build.
- The first five content lines of the note:

```text
    Message rota-0e for anything this note withholds or you doubt. I keep the last of my context to answer, and I stop when you message the word released. Written on 2026-10-28 at the hand-off, after night 173 launched. Read `CLAUDE.md` first, then `python -m rota.tools.state --sid <your sid>`, then thi
    Night 172 was read by fact (`plans/night172-read.md`): 2 of 3 merged on the baseline of all 37 facts, walk 3 stopped on six walls W1 to W6, each under a built fact. Sprint 32 went on the stack's head, biggest issue first. Rows 1 to 3 are built, reviewed and landed on `rota/foundation` at 36d2a667, e
    - Row 1, F2 pass 2 (f2b, landed ee3464fc): the rulings door takes his words from the nested field or his recorded reply, an act rests on its own words, a criterion line the reply never numbers is spared only when an unnumbered sentence shares a name with it, and the naming checks read his recorded r
    - Row 3, F37 pass 2 (f37b, landed 0eaff3f1): a pass names one line or one unit, one branching statement or one docstring run for a documentation criterion; the prompts and the hold say so; a re-send that keeps the held line lands. Interview: `plans/night172-s238-interview.md`. Review: `plans/f37-rev
    - Row 2, F7 pass 3 (f7b, landed 27f8b53b): the `touch_mistaken` wake shows the removed lines through `code.diff` and prints each mistake row with its note; a new L1 case `L1-DV-put-back-a-removed-block` with a grader that reads the file at the head. Read: `plans/f7-night172-read.md`. Review: `plans/
```

- First act: 4.4 minutes after the take, tool Write, `.../d--repos-rota/77c8dc39-1322-4ba4-bcb6-9a1031822837/scratchpad/row4_page_walls_read_brief.md`.
- Messages from the taker to the sender: 1. From the sender to the taker: 0.
- Corrections in 3 h, typed or dialog: 0. Approvals in 3 h, typed or dialog: 1.
- Roman's typed messages:
  - 27.6 min, question: "Are there questions for me?"
  - 31.7 min, approval: "Yeah that's right"

### 7. A69 (H20), 0ce92518 to 68459b4f, frame 345, taken 2026-10-29 09:48

- Kind: frame build.
- The first five content lines of the note:

```text
    Message rota-21 for anything this note withholds or you doubt. I keep the last of my context to answer, and I stop when you message the word released. Written on 2026-10-29 at about 09:00, near 270k, amended at the hand-off. Read `CLAUDE.md` first, then `python -m rota.tools.state --sid <your sid>`,
    Took frames 344, 345, 340, 324 and 341 from rota-62 at 04:58 on a clean context. Roman's ruling of 01:53 stands: nights stop, the 24 L3R cases are the loop, "maybe a Gemma trial".
    - **The seam, frame 345.** Five passes landed on `rota/foundation`: df4b89b9 (passes 2 to 2c: the seat gets his words per line and gives one word, the revise and read-back cue doors read the match), ce02c29a (passes 3 and 3b: the word definitions, the conjoined subject, three cue doors out, `remove`
    - **The model.** Gemma 6 against qwen's 1 before the seam build, 7 against 4 at df4b89b9, 12 against 7 at ce02c29a, and 35 of 41 Liaison L1 cases on both. The `local` profile's Liaison row and the Liaison case pins are Gemma. Roman can reverse it with one line in `rota/llm/profiles/local.toml`.
    - **Closed on the records:** frame 340 (no pass line without a Reach line since the ruling of 2026-10-26), frame 324 (the partition is at head, the residue is the door refusing a bare first guess once), W5 (one reader `kind_of` serves both doors). Blocks in `plans/archive/stack-2026-10-29.md`.
```

- First act: 2.6 minutes after the take, tool Write, `.../d--repos-rota/68459b4f-6e2b-4299-b66e-6ca5ca44f7fd/scratchpad/seam8_brief.md`.
- Messages from the taker to the sender: 1. From the sender to the taker: 1.
- Corrections in 3 h, typed or dialog: 0. Approvals in 3 h, typed or dialog: 1.
- Roman's typed messages:
  - 91.7 min, approval, question: "yes delete the old worktrees right? we dont need them?"

### 8. A78 (H25), 066a0dbd to 208997ee, frame 330, taken 2026-11-02 11:00

- Kind: frame build.
- The first five content lines of the note:

```text
    Result first: dry1 merged its first change on turn 16, 02:32, commit 09c82f3b in the click copy, 5 lines in `pause()` and three test files. The destination's merged change exists on dry1 for the first time. Frame 330 holds the three walls that stood between the park and the merge, and its mechanism 
    The session took frames 330, 341 and 357 from 62bcfbfb at 01:00 with one open question: the gate on pass 3 read invariant I5 as a red against the park page pass 3 opens. I5's loop-cap clause was reasoned on 2026-10-07, the day before the park ruling of 2026-10-08 23:25, and no ruling protects it, so
    dry1 turn 15a at that commit opened the park page for bg_1 at the loop cap, condition 4 of frame 330, 1 of 1. Turn 15b answered it with the test fault, and nothing woke: the sixth wall became the seventh. The read, `plans/dry1-turn15-read-2026-11-02.md`, found the ceiling in `land` read the page's r
    Turn 16 set the one row m140 from `answered` to `open`, the value the fixed code writes, after a backup, and ran: the verdict woke the Liaison, the relay reached the Terminologist and the Tester, the test was rewritten, the counter restarted at attempt 1, attempt 2 went green, and bg_1 merged at ses
    A door with two entrances needs its red test on each. `land` is reached from the seat with an `order` and from the Liaison through `apply_rulings` without one. Pass 4's five tests all passed the order by hand and all went green while dry1's own path stayed broken. Review p4 found it by re-landing th
```

- First act: 3.5 minutes after the take, tool Write, `.../d--repos-rota/208997ee-71a2-496f-83aa-e1425ff49524/scratchpad/dry1_turn17_read_brief.md`.
- Messages from the taker to the sender: 1. From the sender to the taker: 0.
- Corrections in 3 h, typed or dialog: 0. Approvals in 3 h, typed or dialog: 1.
- Roman's typed messages:
  - 43.0 min, approval: "Yes option 2 is good"

## The hand-offs that went worst

The test: the most corrections in three hours, typed or dialog. A tie goes to the earlier first correction.

### 1. A57, ac089aa1 to 8db3a3f9, frame 330, taken 2026-10-26 20:28

- Kind: frame build.
- The first five content lines of the note:

```text
    Message rota-af for anything this note withholds or you doubt. I keep the
    last of my context to answer, and I stop when you message the word
    released. Read `CLAUDE.md` first, then
    `python -m rota.tools.state --sid <your sid>`, then this, then the pointers
    the frames name. Written on 2026-10-26 about 20:28, at night 169's
```

- First act: 3.2 minutes after the take, tool Write, `.../d--repos-rota/8db3a3f9-e4b2-4ce2-b920-9ce56f8071c8/scratchpad/l3_residue_brief.md`.
- Messages from the taker to the sender: 2. From the sender to the taker: 0.
- Corrections in 3 h, typed or dialog: 10. Approvals in 3 h, typed or dialog: 2.
- Roman's typed messages:
  - 12.1 min, correction, question: "so why do you not pull all the context you need/ use subagents to answre questions when you run into faults in rota?"
  - 15.4 min, question: "ok so between finding a single fault and applying the fix, weather it be a one liner or system change, / what should be in place for that to happen?"
  - 23.7 min, correction: "ok but that also sounds narrow, that cant be a law or rule for the future"
  - 32.7 min, question, correction: "so give the subagents more agency, right? / respond extremely precisely"
  - 34.8 min, approval, new ask: "ok yes, / then do this for the frames that we are working on now to understand the prevelance of poor frames"
  - 47.4 min, new ask, question: "ok so first lets update our workflow, / when you find issues, first evaluate the issue against unbuilt solutions / then do what you just did, /  / did i miss anything?"
  - 49.4 min, approval: "yes update"
  - 52.8 min, new ask: "ok so now back to our backlog"
  - 57.4 min, question: "so how many issues do we have?"
  - 70.8 min, question: "Ok so what are the general fixes/ new elements?"
  - 73.4 min, new ask: "Ok with all this knowledge, send another agent to review frames resolved in the last two weeks to see how much work should have been generalised"
  - 89.3 min, question: "Ok so?"
  - 92.7 min, correction: "Ok but think critically right now"
  - 94.8 min, question: "Ok but what did we just discover?"
  - 98.8 min, question: "What follows?"
  - 100.4 min, correction, question: "No I'm still not hearing what I'm expecting, we found significant issues in the workflow /  / What follows?"
  - 102.8 min, correction: "Ok good but still not what I'm thinking, we reviewed the work done by the workflow before our modifications "
  - 104.0 min, correction: "No not rates "
  - 107.1 min, question: "Ok warmer, but what was the shift in workflow today?"
  - 108.1 min, question: "Ok but for what purpose?"
  - 109.4 min, correction: "No that's not the purpose of the change"
  - 111.6 min, other: "Yes much closer"
  - 113.5 min, other: "Well closer to actually solving the problem, / So the meta workflow ran for a long time without this fix, ..."
  - 114.6 min, correction: "No, so a lot of the frames were one offs hiding the real solutions"
  - 117.1 min, question, new ask: "Ok closer, fine, most importantly, did we miss any real solutions and did we create any problems with the partial fixes "
  - 148.2 min, question: "Ok so how are we doing concluding?"
  - 148.9 min, question: "Anything needed from me?"
  - 154.8 min, question: "What are the questions?"
  - 156.8 min, new ask: "Rephrase as questions"
  - 158.8 min, question: "1. I don't understand  / 2. What do you mean by a door refuses on a page?"
  - 163.0 min, correction, question: "1. No don't make it a hard rule, the model should be smart enough to do it / 2. No it should be every time no? Why not"
- His dialog answers:
  - 29.6 min, other: "[User did not answer this question — they sent a message instead. Treat that message as their response; do not re-ask.]"
  - 45.8 min, other: "[User did not answer this question — they sent a message instead. Treat that message as their response; do not re-ask.]"

### 2. A66, 77c8dc39 to 2ebac251, frame 344, taken 2026-10-28 12:16

- Kind: frame build.
- The first five content lines of the note:

```text
    Message rota-a5 for anything this note withholds or you doubt. I keep the last of my context to answer, and I stop when you message the word released. Written on 2026-10-28 near the hand-off, while the full gate on 3ac83acc ran. Read `CLAUDE.md` first, then `python -m rota.tools.state --sid <your si
    Night 173 ran from 36d2a667 and merged 3 of 3, the first since night 152 (`plans/night173-read.md`). Frame 343 closed to the archive, frame 330 parked with no sample in three nights, and sprint 33 went on the stack's head. Roman ruled at 09:10, "Yeah that's right": a page is about one request only, 
    Landed on `rota/foundation`, each with a touched-file run in `rota_g328`:
    - P12 at 189dc7b2: the stopped page names the red test by path with its error line; `touch_mistaken` has words. Review `plans/p12-review-p1.md`, READY.
    - w7root at 793aa684: `said(conn, message_id)` in principal.py is the one reader of his words of a message, entries first; the nine readers of `messages.body_text` go through it; F2 passes 2f and 2g, the rulings door refuses passed words his reply does not hold, every words field checked at clause e
```

- First act: 2.7 minutes after the take, tool Bash, `git commit`.
- Messages from the taker to the sender: 1. From the sender to the taker: 1.
- Corrections in 3 h, typed or dialog: 5. Approvals in 3 h, typed or dialog: 1.
- Roman's typed messages:
  - 107.7 min, correction, question: "Sorry just now getting to your question. The tests you describe, I think the night is the wrong scale of test. If we want to make door changes then test the liaison itself. We don't need a full night right? What do you think?"
  - 115.8 min, correction, question: "No, what about the multi step tests?"
  - 117.5 min, correction: "I'm not confident in this"
  - 130.3 min, question, correction: "Why can't you judge?"
  - 131.2 min, correction, question: "No, let's start from the begging, what is the problem?"
  - 133.6 min, new ask: "Sounds like we need less doors and more in depth test cases to highlight weak points in the system prompts"
- His dialog answers:
  - 148.3 min, approval: "Land (Recommended)"

### 3. A29 (H8), 0162323a to bf5baa63, frame 287, taken 2026-10-17 23:57

- Kind: frame build.
- The first five content lines of the note:

```text
    Message rota-91 for a context question before you ask Roman. Facts are in
    `plans/stack.md`. This session took frame 287 from the vacancy at 18:52
    on 2026-10-17, reasoned its design on Fable through three revisions and
    two Opus reviews, sent it to Roman, closed frame 290 and frame 220 at
    commits with their reviews standing, and hands off at the night boundary
```

- First act: 2.1 minutes after the take, tool Write, `.../d--repos-rota/bf5baa63-e3e0-4611-8e8d-2e8c20403b25/scratchpad/claim.py`.
- Messages from the taker to the sender: 0. From the sender to the taker: 0.
- Corrections in 3 h, typed or dialog: 5. Approvals in 3 h, typed or dialog: 2.
- Roman's typed messages:
  - 118.4 min, new ask, correction: "i feel like im loosing controll of the workflow, / do we need a retro on your thoughts of the current state of the workflow? / ie your context, any bad practices that may have caused fragmentation and noise in your context / etc"
  - 128.8 min, correction: "no but stop, do you not feel like you have a million and one "reminders" and not one unified context environment?"
  - 131.7 min, correction, new ask: "you dont know what a well designed context would look for you to work accross sessions, do you want to think about that for a bit?"
  - 143.0 min, approval, question: "1.3), yes thats why I want you to use subagents /  / 2.1 yes, weve had discussions on this before but i dont know if they got persisted, how we could refine this from what we have on disk / 2.2 what do you mean my rullings? why would that speciffically help you? / 2.3 yes to suplement reasoning not overtake"
  - 152.2 min, question, other: "yes there are standbys /  / 2.2 what do you mean standing intent? is recency of my intent important for the project? /  / session handover, i dont know what you need to ask the previous session, its just an option for the new session to complete their understanding etc. I dont have the words to complete the"
  - 157.7 min, approval, correction: "long stretches, no like nothing blocks on me for multiple sessions, / so you just work through the backlog /  / 1 double check reasoning, then yes / 2 no, keep the same high, med, low system / 3 this is super important, do we need multiple levels of sub agents to draft this? / 4 sure"
  - 166.6 min, correction: "I dont see a task doing that"
  - 172.6 min, question: "the other standbys were started before any workflow changes, is this accounted for?"

### 4. A56, 4cdad7e1 to ac089aa1, frame 283, taken 2026-10-26 17:51

- Kind: frame build.
- The first five content lines of the note:

```text
    Message rota-f9 for anything this note withholds or you doubt. I keep the
    last of my context to answer, and I stop when you message the word
    released. Read `CLAUDE.md` first, then
    `python -m rota.tools.state --sid <your sid>`, then this, then the pointers
    the frames name. Written on 2026-10-26 about 09:16, at night 168's
```

- First act: 18.5 minutes after the take, tool Write, `.../d--repos-rota/ac089aa1-c627-4128-af45-c49f490f4a93/scratchpad/close_and_sprint25.py`.
- Messages from the taker to the sender: 2. From the sender to the taker: 1.
- Corrections in 3 h, typed or dialog: 4. Approvals in 3 h, typed or dialog: 1.
- Roman's typed messages:
  - 34.8 min, other: "a note on the gemma work, / I only want to replace with gemma if it can do everything"
  - 54.5 min, question, correction: "ok, are we still planning to fix gemmas ability to use rota? / because i thought we were finding qwen quirks in rota"
  - 75.7 min, question: "ok so what are we working on and what do we have in the backlog? / what are we prioritising?"
  - 91.0 min, question: "how is the project going? how much progress have we made toward rota working?"
  - 99.3 min, question: "ok are we not fixing all the things in one go before the next night?"
  - 106.3 min, other: "I mean just that if the fixes are for different parts of the flow or whatever then they cant convolute"
  - 107.0 min, question: "whats the general solution to the question you asked?"
  - 147.7 min, question: "ok so help me understand the question, / do we not already have a system that determines what the repo is automatically? / like during onboarding?"
  - 148.7 min, question: "in proposing your solution, did you do any investigations?"
  - 149.6 min, correction: "given a problem you should have given a subagent the task of gathering information, proposing a solution from what exists"
  - 153.1 min, correction, question: ""a full path into an attached folder is re-pointed" why? the path should already be the right path if the seat that makes it is already guided by the onboarding classificaitons. is that right?"
  - 157.6 min, question: "whats the question?"
  - 162.4 min, correction: "fuck like the initial fix was so narrow minded"
  - 165.6 min, approval: "yeah ok general"

### 5. A92 (H31), 7fd2421e to b49d24d2, frame 363, taken 2026-11-10 08:52

- Kind: above a frame.
- The first five content lines of the note:

```text
    Result first: the exploration of the meta workflow is complete through
    the design. Steps 1 to 4 are done and tested, the product review joined,
    and step 5 has one design with a second view. Nothing is built. The
    taker holds frame 363. The next act is Roman's go on the design, then
    build step 1.
```

- First act: 0.8 minutes after the take, tool Edit, `D:/repos/rota/plans/stack.md`.
- Messages from the taker to the sender: 1. From the sender to the taker: 2.
- Corrections in 3 h, typed or dialog: 4. Approvals in 3 h, typed or dialog: 1.
- Roman's typed messages:
  - 132.5 min, correction: "Make sure you are not confused about meta Vs rota"
  - 144.4 min, question: "Do we have the meta exploration and synthethis?"
  - 161.1 min, correction: "Slow down, keep the scope complete"
  - 163.8 min, other: "Yeah"
- His dialog answers:
  - 106.0 min, approval: "Finish exploring first (Recommended)"
  - 157.9 min, correction, question: "I mean you said the right things but what the hell do you mean build on?"
  - 164.8 min, correction, question: "I don't know are you genuinely investigating how to make the project spiral well?"

### 6. A30 (H9), bf5baa63 to 21800a2b, frame 287, taken 2026-10-18 02:48

- Kind: frame build.
- The first five content lines of the note:

```text
    Message rota-08 for anything this note withholds or you doubt. I keep the
    end of my context to answer, and I stop when you release me. The facts are
    in `plans/stack.md`; read `plans/method/intent.md` first, then
    `plans/method/design.md`, then this, then the state. Rewritten at 02:50 on
    2026-10-18, after the night's read and the design's revision 7.
```

- First act: 1.1 minutes after the take, tool Write, `.../d--repos-rota/21800a2b-6b30-4985-854f-a52c20a25a64/scratchpad/claim.py`.
- Messages from the taker to the sender: 2. From the sender to the taker: 0.
- Corrections in 3 h, typed or dialog: 3. Approvals in 3 h, typed or dialog: 0.
- Roman's typed messages:
  - 15.7 min, question: "Do you feel more empowered to reason or follow protocol?"
  - 19.3 min, question: "Ok, and the numerous frames up ahead (besides the meta workflow work), is the backlog coherent and well ordered/ grouped/split?"
  - 24.4 min, new ask: "Think more about what you prefer the backlog to be like. Then think about why it isn't like that. Then think about what to change in the workflow to keep it how you want it. Then think about what to do with the current backlog. Then tell me what you think"
  - 26.9 min, correction: "Ok this indexes heavily on project work just being wall fixes. But that's not the only thing this workflow is for"
  - 28.6 min, correction: "Wait don't do this"
  - 29.2 min, correction: "I just asked for your thoughts on the backlog, I don't like the direction. Let's just keep working"

### 7. A27 (H7), 0e37e9d7 to d7c5dc6d, frame 283, taken 2026-10-17 17:53

- Kind: mixed.
- The first five content lines of the note:

```text
    Message rota-7d for a context question before you ask Roman. Facts are in
    `plans/stack.md`. This session took frame 223 from session eefbf293 at
    13:32 on 2026-10-17 at night 154's launch, watched the night, pushed frame
    282 from its one `CYCLE` line, read the night on Opus, closed frames 223
    and 267, wrote sprint 12, and ran rows 1 and 5 with three agents. Then
```

- First act: 2.6 minutes after the take, tool Write, `.../d--repos-rota/d7c5dc6d-485b-4232-840c-a248ec516e0f/scratchpad/f283/review3_brief.md`.
- Messages from the taker to the sender: 0. From the sender to the taker: 0.
- Corrections in 3 h, typed or dialog: 2. Approvals in 3 h, typed or dialog: 1.
- Roman's typed messages:
  - 17.8 min, question: "Whats blocked on me?"
  - 21.0 min, approval, new ask: "yeah the whole method, / with an important focus on the context, looking at previous decisions/implementation etc / entire project context, progressive re-discovery, project future management ,etc"
  - 59.3 min, other: "added standbys"
- His dialog answers:
  - 23.1 min, correction: "this is just a basic approach, youre not reasoning about the purpouse, not thinking critically, grilling"
  - 25.4 min, other: "nothing measurable, we stay aware of all relevant points previously discussed without clutter"
  - 29.2 min, correction: "youre pissing me off, im not re-discussing this shit with you, the whole design and rationale should be in the logs /  / answers should be retreived by subagents to build understanding"

### 8. A51, b18846fb to 0699ee05, frame 283, taken 2026-10-25 13:11

- Kind: frame build.
- The first five content lines of the note:

```text
    Message rota-3c for anything this note withholds or you doubt. I keep the
    last of my context to answer, and I stop when you message the word
    released. Read `CLAUDE.md` first, then
    `python -m rota.tools.state --sid <your sid>`, then this, then the pointers
    the frames name. Draft written on 2026-10-25 at 05:30, while frame 323's
```

- First act: 2.6 minutes after the take, tool Write, `.../d--repos-rota/0699ee05-aed4-42bd-b867-004e80f7d047/scratchpad/f283_take_line.py`.
- Messages from the taker to the sender: 0. From the sender to the taker: 0.
- Corrections in 3 h, typed or dialog: 2. Approvals in 3 h, typed or dialog: 1.
- Roman's typed messages:
  - 33.4 min, question: "anything controversial?"
  - 41.1 min, approval: "i mean about the standby timeout, if not implement"
  - 48.8 min, question: "ok, how is the gemma run?"
  - 52.3 min, new ask, question: "ok well look at what its doing, why is it suceeding/failing/slow /  / and what are the token speed differences?"
  - 63.8 min, question: "ok so what is looking like the best way forward?"
  - 66.6 min, question: "ok but why, is gemma just worse or is the system just better for qwen in the current state?"
  - 69.4 min, question: "does gemma have native tool calling?"
  - 73.4 min, new ask, correction: "Whaaat ok, / do a couple tests that they were both struggling on with tool calling /  / i like the idea of the night but we need to iron out basic gemma quirks before running it. / and tool calling test on both goes first"
  - 85.4 min, question: "how many trial profiles do we have?"
  - 126.2 min, new ask: "wait this just dropped, look at this: / https://github.com/Zagitta/gpu-unlock"
  - 128.3 min, question: "what are the projected improvements?"
  - 130.9 min, question: "but if we only use one model for everything"
  - 168.7 min, correction, new ask, machine pause: "ok pause everything im going gaming"

### 9. A52 (H16), 0699ee05 to 66edc387, frame 283, taken 2026-10-25 18:28

- Kind: frame build.
- The first five content lines of the note:

```text
    Message rota-bc for anything this note withholds or you doubt. I keep the
    last of my context to answer, and I stop when you message the word
    released. Read `CLAUDE.md` first, then
    `python -m rota.tools.state --sid <your sid>`, then this, then the pointers
    the frames name. Written on 2026-10-25 at 18:30, with night 166 live since
```

- First act: 3.7 minutes after the take, tool Write, `.../d--repos-rota/66edc387-a3b2-48b8-8dec-bb5b3aa63e50/scratchpad/n166_watch.py`.
- Messages from the taker to the sender: 2. From the sender to the taker: 0.
- Corrections in 3 h, typed or dialog: 2. Approvals in 3 h, typed or dialog: 1.
- Roman's typed messages:
  - 23.3 min, question: "need anything from me?"
  - 25.7 min, question: "what are the questions?"
  - 29.1 min, approval: "👍"
  - 89.9 min, correction, new ask, machine pause: "stop everything im going to close vs code"
  - 90.8 min, new ask, correction, machine pause: "kill it"

### 10. A67, 2ebac251 to 161c371b, frame 344, taken 2026-10-29 00:11

- Kind: frame build.
- The first five content lines of the note:

```text
    Message rota-27 for anything this note withholds or you doubt. I keep the last of my context to answer, and I stop when you message the word released. Written on 2026-10-28 in the afternoon, past 300k, while seam review p6 ran. Read `CLAUDE.md` first, then `python -m rota.tools.state --sid <your sid
    Took frame 344 from rota-a5 at 12:16 with frames 339, 340, 324 and 341. Night 174 ran from 3ac83acc, 12:16 to 13:58, and merged 3 of 3; its read is `plans/night174-read.md`. Frame 339 closed to `plans/archive/stack-2026-10-28.md` on its Ends-when. Sprint 34 is on the stack's head, seven rows.
    Landed on `rota/foundation`, each with a touched-file run in `rota_g328`:
    - W11 at 1d5c252e: a held parse error is answered at once through one reader, `_parse_refusal`, and the night print counts parse endings. Review `plans/w11-review-p1.md`, READY at p3.
    - W10 at eeb0db69: a message to a Tester or a Developer lands only on an item with a built batch, one check `_unbuilt_refusal` on one predicate `api.built_batch`. Review `plans/w10-review-p1.md`, READY at p3 with two lows.
```

- First act: 3.9 minutes after the take, tool Write, `.../d--repos-rota/161c371b-f6a2-4d73-aebc-bae776885ab7/scratchpad/n175_read_brief.md`.
- Messages from the taker to the sender: 1. From the sender to the taker: 0.
- Corrections in 3 h, typed or dialog: 2. Approvals in 3 h, typed or dialog: 0.
- Roman's typed messages:
  - 97.9 min, question: "What do you need from me?"
  - 98.5 min, question, correction: "Can you not judge it?"
  - 99.9 min, question: "Do we keep having the same issues? Did we do a root cause analysis for the issues?"
  - 101.8 min, correction, new ask: "Ok so instead of faffing with nights try to develop the right behaviour in the liaison with test cases, and maybe a Gemma trial"

## One line per hand-off

Each line gives: the take, the sender and the taker, the frame, the kind, the note line that decided the kind, whether Roman typed in 3 h, his typed messages by label, the minutes to the first typed correction, and the minutes to the first act. A number in brackets is the line of the note.

- A1, 2026-10-11 00:44, 4b501a17 to 84ce0759, frame 199, frame build. [36] "is the right next shape. Do the scope report turn by turn before any" Typed: no. Labels: none. First correction: none. First act: 46.2 minutes, Write.
- A2, 2026-10-11 09:13, 84ce0759 to be3ef742, frame 200, frame build. [47] "- Frame 200's pass 1 is the next thing to build, and it is small: two" Typed: no. Labels: none. First correction: none. First act: 1.9 minutes, Write.
- A3, 2026-10-11 15:06, be3ef742 to c81dd240, frame 200, frame build. [66] "- Frame 204 is the next design, and frame 198 is a small pass inside it:" Typed: yes. Labels: other 1. First correction: none. First act: 6.0 minutes, Write. Dialog answers: 3, with 0 corrections.
- A4, 2026-10-11 16:20, c81dd240 to 59bdd13a, frame 200, frame build. [53] "- Frame 204's pass 1 is the next piece of work, and it is large. Brief" Typed: yes. Labels: question 3. First correction: none. First act: 3.7 minutes, Write.
- A5, 2026-10-11 22:16, 59bdd13a to 91506043, frame 200, frame build. [48] "- Night 141 is the first night where the show_python batch can merge." Typed: yes. Labels: question 2. First correction: none. First act: none.
- A6, 2026-10-12 05:52, 91506043 to 5d91f76d, frame 200, frame build. [54] "line and a refused relay, not the build loop. Frame 213 is the next" Typed: no. Labels: none. First correction: none. First act: 1.2 minutes, Write.
- A7, 2026-10-12 10:41, 5d91f76d to 5083f684, frame 200, frame build. [27] "unclaimed and priced 4 cycles. It is the next session's first frame." Typed: yes. Labels: other 1. First correction: none. First act: 3.3 minutes, Write.
- A8, 2026-10-12 12:19, 5083f684 to d609cf11, frame 200, frame build. [29] "- Frame 215's ends-when has its mechanism. The ratio waits on night 143" Typed: no. Labels: none. First correction: none. First act: 1.9 minutes, Write.
- A9 (H1), 2026-10-12 22:44, d609cf11 to 31e55586, frame 200, frame build. [54] "## Where pass 5 stands at the hand-off" Typed: yes. Labels: question 9, new ask 2, approval 2. First correction: none. First act: 1.4 minutes, Write. Dialog answers: 4, with 1 correction.
- A10, 2026-10-12 23:20, 31e55586 to 80cae596, frame 200, frame build. [24] "- Pass 5's mechanism holds and the Tester moves the argument when the" Typed: no. Labels: none. First correction: none. First act: 91.7 minutes, Agent.
- A11, 2026-10-13 03:35, 80cae596 to fb742825, frame 200, frame build. [75] "- After the night: the read, the ratios for frames 200, 215, 207, 204 and" Typed: no. Labels: none. First correction: none. First act: 1.0 minutes, Write.
- A12, 2026-10-13 06:42, 31e55586 to 0c045f37, frame 204, frame build. [34] "work is the Developer's own call. Then pass 2d is three edits: the" Typed: no. Labels: none. First correction: none. First act: 2.7 minutes, Write.
- A13, 2026-10-14 10:49, 9b79f4a1 to 58da19ca, frame 233, frame build. [28] "- Night 147 is the test of frames 233 and 235 together, and its launch has" Typed: no. Labels: none. First correction: none. First act: 1.8 minutes, Write.
- A14, 2026-10-14 15:17, 58da19ca to f3b11814, frame 233, frame build. [22] "its log at `.rota/ollama_night147.log`. The read after the night is the taker's largest cycle." Typed: yes. Labels: approval 1. First correction: none. First act: 21.6 minutes, Write.
- A15, 2026-10-14 19:10, f3b11814 to 4a757f92, frame 238, frame build. [30] "- The next night, 148, is the measure of six held frames and needs two" Typed: no. Labels: none. First correction: none. First act: 2.7 minutes, Write.
- A16, 2026-10-15 14:51, dae006d1 to cd6300cd, frame 243, frame build. [19] "252 reviews the guide after three nights of use. Your read of night 149" Typed: yes. Labels: question 1. First correction: none. First act: 2.1 minutes, Agent.
- A17, 2026-10-15 18:56, cd6300cd to 4492a9c1, frame 243, frame build. [34] "`plans/frame243-review-3.md`; read it, commit it, act on a high only," Typed: no. Labels: none. First correction: none. First act: 3.8 minutes, Write.
- A18 (H2), 2026-10-16 02:35, 4492a9c1 to 738ddbaf, frame 243, frame build. [20] "What is left is the 8B reading a fact and deciding against it. Frame 244" Typed: no. Labels: none. First correction: none. First act: 1.7 minutes, Write.
- A19, 2026-10-16 06:44, 738ddbaf to cc1d654e, frame 243, frame build. [11] "## Read first: night 150 is done, and its read is your frame" Typed: no. Labels: none. First correction: none. First act: 2.5 minutes, Write.
- A20 (H3), 2026-10-16 13:33, cc1d654e to 738ddbaf, frame 243, frame build. [25] "accepted, both validating on night 151. The next step is sprint 8's row" Typed: yes. Labels: other 1. First correction: none. First act: 0.6 minutes, Agent.
- A21 (H4), 2026-10-16 15:36, 738ddbaf to 70d05878, frame 243, frame build. [14] "## Read first: night 151 is the measure, and its read is your frame" Typed: yes. Labels: approval 1. First correction: none. First act: 100.7 minutes, Write.
- A22, 2026-10-16 20:40, 70d05878 to 04be1489, frame 243, frame build. [12] "## Read first: night 152 is the measure, and its read is your frame" Typed: yes. Labels: correction 1, question 1. First correction: 112.0. First act: 67.1 minutes, Write.
- A23 (H5), 2026-10-17 00:20, 04be1489 to 1cf2843b, frame 274, frame build. [23] "- Frame 274, pass 1b at 6553d0f1, review 2 owed. Review 1," Typed: yes. Labels: other 1. First correction: none. First act: 2.5 minutes, Agent.
- A24 (H6), 2026-10-17 02:15, 1cf2843b to b0dce033, frame 274, frame build. [13] "## Read first: night 153 runs, and the read is your frame" Typed: yes. Labels: question 1. First correction: none. First act: 108.5 minutes, Write.
- A25, 2026-10-17 12:04, b0dce033 to eefbf293, frame 278, frame build. [14] "## Read first: one gate is owed, then sprint 11's rows 2 to 4, then night 154" Typed: yes. Labels: correction 1, question 1. First correction: 45.9. First act: 3.2 minutes, Write.
- A26, 2026-10-17 13:31, eefbf293 to 0e37e9d7, frame 223, frame build. [12] "## Read first: night 154 runs, and its read is the next cycle" Typed: no. Labels: none. First correction: none. First act: 170.4 minutes, Write.
- A27 (H7), 2026-10-17 17:53, 0e37e9d7 to d7c5dc6d, frame 283, mixed. [54] "or the path a wall travels. Roman has not answered it. Start the frame" [69] "if not done, review 3 from a worktree, the gate from" Typed: yes. Labels: question 1, new ask 1, approval 1, other 1. First correction: none. First act: 2.6 minutes, Write. Dialog answers: 3, with 2 corrections.
- A28, 2026-10-17 18:53, d7c5dc6d to 0162323a, frame 287, above a frame. [8] "reasoning of frame 287 as the next step." Typed: yes. Labels: correction 1, new ask 1. First correction: 36.9. First act: 6.6 minutes, Write.
- A29 (H8), 2026-10-17 23:57, 0162323a to bf5baa63, frame 287, frame build. [86] "1. Frame 286's pass 1 on `api.py`, with frame 220's four lows." Typed: yes. Labels: correction 5, question 3, new ask 2, approval 2, other 1. First correction: 118.4. First act: 2.1 minutes, Write.
- A30 (H9), 2026-10-18 02:48, bf5baa63 to 21800a2b, frame 287, frame build. [48] "- Frame 287: build step 2 next, `state`, `status --ruling`, the handover" Typed: yes. Labels: correction 3, question 2, new ask 1. First correction: 26.9. First act: 1.1 minutes, Write.
- A31, 2026-10-18 05:30, 21800a2b to 6977407c, frame 258, frame build. [68] "- Night 156 runs from `C:/Users/roman/rota_night156` at db0c781d, cold," Typed: no. Labels: none. First correction: none. First act: 96.8 minutes, Write.
- A32, 2026-10-18 13:34, 6977407c to 050a41e6, frame 298, frame build. [64] "with pass 1's scene fix at 30c4a121. No agent is live. Your first cycle:" Typed: no. Labels: none. First correction: none. First act: 2.2 minutes, Write.
- A33, 2026-10-18 16:41, 050a41e6 to c32575f3, frame 298, frame build. [59] "`.rota/night157.err`. Read a CYCLE line when it fires. At the night's" Typed: yes. Labels: question 1, other 1. First correction: none. First act: 1.3 minutes, Bash.
- A34 (H10), 2026-10-21 11:42, c32575f3 to 5389be74, frame 298, frame build. [74] "- The next night runs from a worktree at the sprint's closing commit." Typed: yes. Labels: correction 1, new ask 2. First correction: 63.0. First act: 3.0 minutes, Agent.
- A35, 2026-10-21 15:53, 5389be74 to 81fe1025, frame 298, frame build. [67] "- Night 158: live from `C:/Users/roman/rota_night158` at b650633c, cold," Typed: yes. Labels: correction 1, new ask 1. First correction: 47.4. First act: 2.9 minutes, Write.
- A36, 2026-10-23 13:25, 81fe1025 to 2214bec6, frame 283, frame build. [86] "first cycles, by the order: frame 304's pass on the encode door, row 3;" Typed: yes. Labels: question 2, other 1. First correction: none. First act: 3.0 minutes, Write.
- A37, 2026-10-23 15:31, 2214bec6 to 1b2c3f89, frame 283, frame build. [60] "cold, held on the merged content. Read it with `n158_read_brief.md` in" Typed: no. Labels: none. First correction: none. First act: 1.1 minutes, Bash.
- A38, 2026-10-23 18:20, 1b2c3f89 to b85289fd, frame 283, frame build. [49] "the gate are owed, and night 160 launches from that head. The" Typed: no. Labels: none. First correction: none. First act: 1.6 minutes, Write.
- A39 (H11), 2026-10-23 19:46, b85289fd to 8e879083, frame 283, frame build. [41] "record now gives on the branch. That is the next pass, on the branch" Typed: no. Labels: none. First correction: none. First act: 5.4 minutes, Edit.
- A40, 2026-10-23 21:31, 8e879083 to 0cdcac52, frame 283, frame build. [62] "night ends sprint 16; take the git truth first; the next sprint's" Typed: yes. Labels: correction 1, new ask 1. First correction: 3.5. First act: 1.6 minutes, Write.
- A41 (H12), 2026-10-24 02:08, 0cdcac52 to b00cc646, frame 283, frame build. [55] "reds and stale. Then cherry-pick frame 312's commits (7e1b8cdc and" Typed: no. Labels: none. First correction: none. First act: 2.5 minutes, Bash.
- A42 (H13), 2026-10-24 05:34, b00cc646 to 51917779, frame 283, frame build. [47] "- Night 161's read is the next cycle, the frame's largest, on one Opus" Typed: no. Labels: none. First correction: none. First act: 2.9 minutes, Write.
- A43, 2026-10-24 07:35, 51917779 to f33f3f44, frame 283, frame build. [85] "## The gate and the night, written at the launch" Typed: no. Labels: none. First correction: none. First act: 1.7 minutes, Write.
- A44, 2026-10-24 13:29, f33f3f44 to f3a8d4c2, frame 283, frame build. [38] "branch at f8d3ab64 to 50e96b4e. The next pass narrows the note to a" Typed: yes. Labels: question 10, new ask 3, approval 2, other 2. First correction: none. First act: 4.5 minutes, Write.
- A45, 2026-10-24 15:29, f3a8d4c2 to f1f0bcfa, frame 283, frame build. [60] "318), 5 (the s157 read, frame 319). Rows 4, 6, 7 and 8 are not started:" Typed: yes. Labels: question 1, other 1. First correction: none. First act: 5.2 minutes, Write.
- A46 (H14), 2026-10-24 17:01, f1f0bcfa to e7141541, frame 283, frame build. [69] "CYCLE line at once, by M12. After it, the read on one Opus agent with" Typed: no. Labels: none. First correction: none. First act: 1.6 minutes, Write.
- A47, 2026-10-24 20:54, e7141541 to a0790d20, frame 283, frame build. [85] "CYCLE line at once, by M12. After it, the read on one Opus agent with" Typed: no. Labels: none. First correction: none. First act: 6.7 minutes, Edit.
- A48 (H15), 2026-10-24 23:16, a0790d20 to 48122667, frame 283, frame build. [79] "check-line retire, is the next pass; its brief is not written." Typed: yes. Labels: question 3, new ask 1. First correction: none. First act: 1.1 minutes, Write.
- A49, 2026-10-25 01:28, 48122667 to 79847ec6, frame 283, frame build. [72] "The read goes to `plans/night165-read.md` and ends sprint 21." Typed: yes. Labels: question 1, new ask 1. First correction: none. First act: 1.8 minutes, Bash.
- A50, 2026-10-25 03:08, 79847ec6 to b18846fb, frame 283, frame build. [63] "When `f323_run.log` gains `== done`, run" Typed: no. Labels: none. First correction: none. First act: 2.9 minutes, Write.
- A51, 2026-10-25 13:11, b18846fb to 0699ee05, frame 283, frame build. [60] "When `f323_run.log` gains `== done`, run" Typed: yes. Labels: correction 2, question 9, new ask 4, approval 1. First correction: 73.4. First act: 2.6 minutes, Write.
- A52 (H16), 2026-10-25 18:28, 0699ee05 to 66edc387, frame 283, frame build. [72] "each CYCLE line as it lands, then the end, then the read." Typed: yes. Labels: correction 2, question 2, new ask 2, approval 1. First correction: 89.9. First act: 3.7 minutes, Write.
- A53, 2026-10-26 01:25, 66edc387 to 192bbbc0, frame 283, frame build. [76] "- Live agents: frame 326's implementer on pass 1c in" Typed: no. Labels: none. First correction: none. First act: 4.4 minutes, Agent.
- A54, 2026-10-26 04:48, 192bbbc0 to ad481e08, frame 283, frame build. [56] "of 3 for frames 328 and 329 at this head, and the Gemma night of frame" Typed: no. Labels: none. First correction: none. First act: 1.4 minutes, Bash.
- A55, 2026-10-26 07:15, ad481e08 to 4cdad7e1, frame 283, frame build. [73] "- Owed after the night: the night read on Opus, the four re-records, the" Typed: yes. Labels: correction 1, question 1. First correction: 105.2. First act: 1.4 minutes, Write.
- A56, 2026-10-26 17:51, 4cdad7e1 to ac089aa1, frame 283, frame build. [70] "- Owed after the night: the night read on Opus to `plans/night168-read.md`" Typed: yes. Labels: correction 4, question 9, approval 1, other 2. First correction: 54.5. First act: 18.5 minutes, Write.
- A57, 2026-10-26 20:28, ac089aa1 to 8db3a3f9, frame 330, frame build. [76] "- Owed after the night: the read on Opus to `plans/night169-read.md` in" Typed: yes. Labels: correction 10, question 18, new ask 6, approval 2, other 2. First correction: 12.1. First act: 3.2 minutes, Write. Dialog answers: 2, with 0 corrections.
- A58 (H17), 2026-10-26 22:46, 8db3a3f9 to e03f97fc, frame 330, mixed. [31] "Frame 339 is built at c7264f5a on branch f339 in `C:/Users/roman/rota_p339`, not reviewed, not gated clean: three stale cases from the changed Developer prompt " [33] "Row 0 of sprint 26: the re-cut agent. Then frame 339's gate if I did not reach it, frame 330's pass 5, the gate, and night 170 on 339 and 330. Every pass brief " Typed: yes. Labels: question 4. First correction: none. First act: 3.3 minutes, Agent.
- A59, 2026-10-27 02:59, e03f97fc to 0f8527d4, frame 330, frame build. [28] "Finish the seam: read pass 4b's report when it lands, re-check it on a reviewer (the probes are in my scratchpad), cherry-pick it onto the branch above pass 5 a" Typed: no. Labels: none. First correction: none. First act: 11.3 minutes, Write.
- A60, 2026-10-27 13:23, 0f8527d4 to c66eae69, frame 330, frame build. [28] "Watch the night's CYCLE lines and read each one at once, by the rule of the night moment. A loop on no held frame's site stops the night. Then the night read by" Typed: yes. Labels: question 2, new ask 1. First correction: none. First act: 1.7 minutes, Write. Dialog answers: 1, with 0 corrections.
- A61 (H18), 2026-10-27 16:07, c66eae69 to 6d9cf7e1, frame 330, frame build. [33] "Watch night 171's CYCLE lines, and read each one at once. Then read the night by fact, with frame 343's door, frame 339's door and frame 330's count first. Revi" Typed: yes. Labels: correction 2, question 2, approval 1. First correction: 170.1. First act: 1.0 minutes, Bash. Dialog answers: 2, with 0 corrections.
- A62, 2026-10-27 19:40, 6d9cf7e1 to b3bc8a66, frame 330, frame build. [30] "Land sprint 28 in order: F25 after pass 1e and its gate, F37, W3 after its review, F7 after review p2. Then sprint 29, F2 with F3 and F4, and onward by score. N" Typed: yes. Labels: correction 1, new ask 1. First correction: 9.0. First act: 2.0 minutes, Write.
- A63, 2026-10-28 01:57, b3bc8a66 to 2911045b, frame 330, frame build. [44] "Read `gate_657c559c.txt`. If the F25 gate is clean, fast-forward `rota/foundation` to the land28 merge and land the next branch. Then collect each in-flight rep" Typed: yes. Labels: question 1. First correction: none. First act: 5.4 minutes, Write.
- A64 (H19), 2026-10-28 04:25, 2911045b to 2568e043, frame 330, frame build. [11] "Launched from `.rota/launch_night172.sh` at de1203a9, cold, items 163 rotated, profile local, log `.rota/night172_launch.log`. Night 1 of 3 for frames 330, 339," Typed: no. Labels: none. First correction: none. First act: 2.4 minutes, Write.
- A65, 2026-10-28 08:38, 2568e043 to 77c8dc39, frame 330, frame build. [17] "Launched from `.rota/launch_night173.sh` at 36d2a667, cold, items 163 rotated, profile local, log `.rota/night173_launch.log`. Night 3 of 3 for frame 343, night" Typed: yes. Labels: question 1, approval 1. First correction: none. First act: 4.4 minutes, Write.
- A66, 2026-10-28 12:16, 77c8dc39 to 2ebac251, frame 344, frame build. [19] "- The full gate with re-records on 3ac83acc from `rota_g328`, to `gate_3ac83acc.txt` in my scratchpad, `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/7" Typed: yes. Labels: correction 5, question 4, new ask 1. First correction: 107.7. First act: 2.7 minutes, Bash. Dialog answers: 1, with 0 corrections.
- A67, 2026-10-29 00:11, 2ebac251 to 161c371b, frame 344, frame build. [23] "- **Night 175 runs from 21d145df since 17:05**, to `.rota/night175_launch.log`, the worktree `rota_n175`. Night 1 for the seam, W11 and W10, night 2 for P7, P89" Typed: yes. Labels: correction 2, question 3, new ask 1. First correction: 98.5. First act: 3.9 minutes, Write.
- A68, 2026-10-29 04:58, 161c371b to 0ce92518, frame 344, frame build. [25] "- **Pass 2b of frame 345** builds in `rota_seam2` on `seam2root` from 27291602, after review p3 found the match wrong in 4 of 24 replies and the lost run caused" Typed: no. Labels: none. First correction: none. First act: 5.1 minutes, Write.
- A69 (H20), 2026-10-29 09:48, 0ce92518 to 68459b4f, frame 345, frame build. [19] "- **The next levers**, in order: fewer words in the table where his words make no split, revise against rewrite against contest (the Gemma words read, pair 4, a" Typed: yes. Labels: question 1, approval 1. First correction: none. First act: 2.6 minutes, Write.
- A70 (H21), 2026-10-29 16:56, 68459b4f to 00ca90d0, frame 345, frame build. [18] "1. Land R2 (above). Ends-when part 3 of frame 345 then holds in full." Typed: yes. Labels: correction 1, new ask 1. First correction: 21.0. First act: 2.8 minutes, Write.
- A71, 2026-10-30 14:42, 00ca90d0 to a9a43280, frame 341, frame build. [11] "Nothing to build until the count's date. Read its status lines, not the" [24] "- Frame 348 holds the residue: two one-case shapes and the owed sentence" Typed: no. Labels: none. First correction: none. First act: 1.8 minutes, Write.
- A72 (H22), 2026-10-30 23:32, a9a43280 to d5c14419, frame 348, frame build. [5] "with its review p4 in `plans/f348-review-p4.md`: read that verdict first, and" Typed: yes. Labels: correction 1, question 3, new ask 2. First correction: 84.9. First act: 2.8 minutes, Write.
- A73 (H23), 2026-10-31 13:36, d5c14419 to 05666872, frame 354, frame build. [7] "The cold start spends one Vision Keeper session per prose file. Pass 1 groups the files, 19 sessions against 39 on a cold run of a clone of click, and the run w" Typed: no. Labels: none. First correction: none. First act: 1.9 minutes, Write.
- A74, 2026-11-01 00:33, 05666872 to 393648aa, frame 354, frame build. [3] "Result first: frame 354, the first wall of the chain, is built through seven passes and five reviews, commits 7e553500 to f26bee62, every gate clean at the last" Typed: no. Labels: none. First correction: none. First act: 3.0 minutes, Agent.
- A75, 2026-11-01 08:23, 393648aa to 3b83d22b, frame 354, frame build. [11] "Pass 10 is built and corrected twice in the checkout, uncommitted: the F22 reader rule caught `_row_name`, and the fix then crashed on a `guess:` ref. The third" Typed: no. Labels: none. First correction: none. First act: 1.7 minutes, Agent.
- A76, 2026-11-01 18:38, 3b83d22b to 62bcfbfb, frame 330, frame build. [15] "Roman ruled at 16:03 on 2026-11-01, 'I like your recommendation', recorded at 0be90b23 in `rota/DECISIONS.md` as an amendment under the park ruling, and in fram" Typed: no. Labels: none. First correction: none. First act: 3.0 minutes, Bash.
- A77 (H24), 2026-11-02 01:00, 62bcfbfb to 066a0dbd, frame 330, frame build. [3] "Result first: dry1's chain moved through its fifth and sixth walls in one session, and the fixes are on the branch and gated. The taker holds frames 330, 341 an" Typed: no. Labels: none. First correction: none. First act: 6.7 minutes, Bash.
- A78 (H25), 2026-11-02 11:00, 066a0dbd to 208997ee, frame 330, frame build. [23] "Frame 357 validates on the night count, conditions 1 and 2 hold on turns 13 and 14. Frame 341 waits on the count to 2026-11-10. Nothing to build on either." [34] "Turn 17 ran at 054b461e, 03:56 to 04:00, 12 sessions. The seat answered m144 with 'this page is wrong, the change merged', and m145 with 'I asked for none of th" Typed: yes. Labels: approval 1. First correction: none. First act: 3.5 minutes, Write.
- A79, 2026-11-02 14:18, 208997ee to ce483c7b, frame 357, frame build. [26] "1. Frame 360's design page, about 80k on Opus, from the read's section 6, in the shape of `plans/design-drop-observed-row-2026-11-02.md`. Then one question to R" Typed: no. Labels: none. First correction: none. First act: 0.8 minutes, Bash. Dialog answers: 1, with 0 corrections.
- A80 (H26), 2026-11-03 01:10, ce483c7b to 07f209e6, frame 362, frame build. [25] "1. Record the three rulings on the design page's Result, with ruling 2 as his words, and amend the page's B: the full read is his choice in the moment, not cut." Typed: no. Labels: none. First correction: none. First act: 2.2 minutes, Edit.
- A81, 2026-11-04 00:02, 07f209e6 to 535a30c6, frame 362, frame build. [17] "1. The slice's pass 1, the harvester and the `commitment_candidates` and `candidate_bindings` records, is on the checkout as 4c5f8867 and a621e598, reviewed in " Typed: no. Labels: none. First correction: none. First act: 3.8 minutes, Bash. Dialog answers: 1, with 0 corrections.
- A82, 2026-11-04 05:58, 535a30c6 to 9f60e445, frame 362, frame build. [13] "1. The gate on a8831892 ran at 03:50 and found 11 real reds, see frame 362's status line of 03:51 and the gate output `C:/Users/roman/AppData/Local/Temp/claude/" Typed: no. Labels: none. First correction: none. First act: 2.0 minutes, Write.
- A83 (H27), 2026-11-04 15:45, 9f60e445 to 94cb1260, frame 362, frame build. [11] "1. The gate on `7bdf1d01` ran at the hand-off, see frame 362's last status lines. It covers pass 4h (the root wake keyed on the harvest's lines, the stuck line'" Typed: yes. Labels: correction 1, question 4, new ask 1. First correction: 161.6. First act: 1.2 minutes, Bash.
- A84, 2026-11-06 03:57, 94cb1260 to 1b9e813c, frame 362, frame build. [28] "1. Dry run 6 again from zero behind the router, from `f362_dry6_brief.md` in this session's first scratchpad, `C:/Users/roman/AppData/Local/Temp/claude/d--repos" Typed: yes. Labels: question 2, new ask 1, other 1. First correction: none. First act: 2.2 minutes, Agent.
- A85 (H28), 2026-11-06 08:05, 1b9e813c to 029756dd, frame 362, frame build. [32] "1. The record of his reply, the rest. CONFIRMED and not built: `page_clauses` drops a clause whose text an earlier clause holds, `rota/roles/api.py` about 15752" Typed: no. Labels: none. First correction: none. First act: 4.1 minutes, Write.
- A86, 2026-11-06 11:52, 029756dd to 8b2312ef, frame 362, frame build. [25] "2. Close slice 1: the review's findings, a second look, the pick, the gate. Three annotate cases go stale, because `annotate.md` changed. The park page is new t" Typed: yes. Labels: question 2. First correction: none. First act: 2.0 minutes, Write. Dialog answers: 1, with 0 corrections.
- A87, 2026-11-07 04:35, 8b2312ef to 0d047fa7, frame 362, frame build. [17] "1. **Frame 360, slice 1.** It is in `C:/Users/roman/rota_p360c`: `8d384ed6`, `e23e7f23`, and pass 2b on top. Two looks each said fix before the pick. Pass 2b ne" Typed: yes. Labels: correction 1. First correction: 8.9. First act: 1.7 minutes, Bash.
- A88, 2026-11-08 10:27, 0d047fa7 to 0ff6bcd7, frame 362, above a frame. [58] "0. **A root-cause read across the week's walls, before any build below.**" Typed: no. Labels: none. First correction: none. First act: 2.6 minutes, Write.
- A89, 2026-11-08 14:15, 0ff6bcd7 to 13b7eef8, frame 362, frame build. [65] "1. **The gate's result, read at the hand-off:** 34 failed and 7,288 passed" Typed: no. Labels: none. First correction: none. First act: 1.3 minutes, Write.
- A90 (H29), 2026-11-10 00:43, 13b7eef8 to 33f037c1, frame 362, frame build. [66] "1. **The gate's result, read at the hand-off.** Pass 1 and 1b are" Typed: no. Labels: none. First correction: none. First act: 6.2 minutes, Write.
- A91 (H30), 2026-11-10 03:41, 33f037c1 to c1a39439, frame 362, frame build. [46] "1. **The gate on the full checkout**, all 24 commits of the three" Typed: no. Labels: none. First correction: none. First act: 9.4 minutes, Agent.
- A92 (H31), 2026-11-10 08:52, 7fd2421e to b49d24d2, frame 363, above a frame. [3] "Result first: the exploration of the meta workflow is complete through" [6] "taker holds frame 363. The next act is Roman's go on the design, then" Typed: yes. Labels: correction 2, question 1, other 1. First correction: 132.5. First act: 0.8 minutes, Edit. Dialog answers: 3, with 2 corrections.
- A93 (H32), 2026-11-10 12:25, b49d24d2 to 4a1d361a, frame 363, above a frame. [4] "its content. The exploration is not complete, and no plan and no build" Typed: no. Labels: none. First correction: none. First act: 0.3 minutes, Edit.

## The kind rule

The read gives each hand-off one kind from two records: the stack heading of the handed frame, and the part of the note that names the next act. That part is the section "Read first", "First after the take", "What comes next", "Owed", "The held frames" or "Where things are", or else the first sentence that names the next step.

1. Give "frame build" when the next act is a pass, a review, a gate, a land, a night, a dry run, or the read of a night or a run, on one or more numbered frames.
2. Count a design page or a read that serves the fix of one named frame as "frame build".
3. Give "above a frame" when the next act is an investigation of the method, a design of the workflow, a plan, a re-cut of the stack or a read across many walls, and no build of a named frame comes first.
4. Give "mixed" when the note names one act of each kind as the first acts.
5. Give "other" when the note names no next act, or only a wait.

No hand-off got "other". The quoted line in each row of the list above is the line that decided the kind.

### Borderline cases

- A1, frame build: Design over the seam of frame 200, then passes. [36] "is the right next shape. Do the scope report turn by turn before any"
- A3, frame build: Next design of frame 204, with frame 198 as a pass inside it. [66] "- Frame 204 is the next design, and frame 198 is a small pass inside it:"
- A11, frame build: Night read, then cross-off, placement of frames and a grill. [75] "- After the night: the read, the ratios for frames 200, 215, 207, 204 and"
- A27 (H7), mixed: Frame 283 owes review 3 and the gate, and frame 287, the method investigation, starts with a scope question. [54] "or the path a wall travels. Roman has not answered it. Start the frame" [69] "if not done, review 3 from a worktree, the gate from"
- A30 (H9), frame build: Frame 287 is the method design frame, and its next step builds tools of its step 2. [48] "- Frame 287: build step 2 next, `state`, `status --ruling`, the handover"
- A58 (H17), mixed: Frame 339 owes its review and gate, and row 0 of sprint 26 is the re-cut of the stack by an agent. [31] "Frame 339 is built at c7264f5a on branch f339 in `C:/Users/roman/rota_p339`, not reviewed, not gated clean: three stale cases from the changed Developer prompt " [33] "Row 0 of sprint 26: the re-cut agent. Then frame 339's gate if I did not reach it, frame 330's pass 5, the gate, and night 170 on 339 and 330. Every pass brief "
- A64 (H19), frame build: Frame 344 is held, and its heading is a review of closed frames. [11] "Launched from `.rota/launch_night172.sh` at de1203a9, cold, items 163 rotated, profile local, log `.rota/night172_launch.log`. Night 1 of 3 for frames 330, 339,"
- A66, frame build: The handed frame 344 is a review of closed frames, and the next acts are a gate and seam passes. [19] "- The full gate with re-records on 3ac83acc from `rota_g328`, to `gate_3ac83acc.txt` in my scratchpad, `C:/Users/roman/AppData/Local/Temp/claude/d--repos-rota/7"
- A67, frame build: The handed frame 344 is a review of closed frames, and the next acts are a night and frame 345's cases. [23] "- **Night 175 runs from 21d145df since 17:05**, to `.rota/night175_launch.log`, the worktree `rota_n175`. Night 1 for the seam, W11 and W10, night 2 for P7, P89"
- A68, frame build: The handed frame 344 is a review of closed frames, and the next act is pass 2b of frame 345. [25] "- **Pass 2b of frame 345** builds in `rota_seam2` on `seam2root` from 27291602, after review p3 found the match wrong in 4 of 24 replies and the lost run caused"
- A71, frame build: The handed frame 341 has nothing to build until a date, and the note names frames 348 to 350 as the line of work. [11] "Nothing to build until the count's date. Read its status lines, not the" [24] "- Frame 348 holds the residue: two one-case shapes and the owed sentence"
- A78 (H25), frame build: The held frames wait on counts, and the next act is the dry run 1 turn that frame 330 measures. [23] "Frame 357 validates on the night count, conditions 1 and 2 hold on turns 13 and 14. Frame 341 waits on the count to 2026-11-10. Nothing to build on either." [34] "Turn 17 ran at 054b461e, 03:56 to 04:00, 12 sessions. The seat answered m144 with 'this page is wrong, the change merged', and m145 with 'I asked for none of th"
- A79, frame build: The first act is the design page of frame 360, then one question to Roman. [26] "1. Frame 360's design page, about 80k on Opus, from the read's section 6, in the shape of `plans/design-drop-observed-row-2026-11-02.md`. Then one question to R"
- A80 (H26), frame build: Frame 362's heading is a design question, and the next acts are records and door repairs. [25] "1. Record the three rulings on the design page's Result, with ruling 2 as his words, and amend the page's B: the full read is his choice in the moment, not cut."
- A92 (H31), above a frame: The next act is Roman's go on a design of the meta workflow, so the kind is close to other. [3] "Result first: the exploration of the meta workflow is complete through" [6] "taker holds frame 363. The next act is Roman's go on the design, then"
- A81 to A91 hold frame 362 in the same way as A80. The read gives each of them "frame build" by its first numbered step.

## Method

1. The 93 hand-offs are the rows of the earlier read's `handoffs.json` that have a note and a taker transcript. A1 is the first by post time, and A93 is the last. The H number is the number of the earlier read.
2. The scan keeps the rules of the earlier `s5_main.py`: the note version at the post time plus 120 seconds, the window of three hours from the take, the clock conversion before 2026-10-25 01:00 UTC, the filter for typed messages, the first act and the match of messages between taker and sender.
3. The scan ran again over all 93. For the 32 old hand-offs it gave the same first-act minute and the same minutes of Roman's typed messages as the earlier read.
4. The 32 old hand-offs keep the labels of the earlier read. This read gave the labels of the 61 new by the same five labels. The read looked at the session's text before 18 short replies to label them.
5. The labels follow these readings. A message that asks a thing is a "question". A message that says the session is wrong, rejects its proposal or stops its direction is a "correction". A reply that starts with "No" to the session is a "correction". A message that gives new work is a "new ask". A yes to a proposal, or a dialog answer that picks the recommended option, is an "approval". A report such as "added standbys", a fact, or a partial answer is "other". A message can have two labels.
6. A message that pauses or stops all work for the machine has the labels "correction, new ask" and the machine mark, as in the earlier read. In the new 61 there are 5: A28 at 36.9, A35 at 47.4, A40 at 3.5, A51 at 168.7 ("ok pause everything im going gaming") and A62 at 9.0. The read counts A51's message as a machine reason, because the game uses the machine.
7. The test of "went best" and the test of "went worst" count his typed messages and his dialog answers together. The totals count typed messages, and one column adds the dialog answers.

## Limits

- The labels of the 61 new and all 93 kinds are the judgement of one reader. That reader is not the reader of the old 32 labels. No second reader checked them.
- 87 of 93 hand-offs are "frame build". The "above a frame" group has 4 and the "mixed" group has 2. Those cells are too small to compare with the "frame build" cells.
- The 4 "above a frame" hand-offs are of 2026-10-17, 2026-11-08 and 2026-11-10. The 2 "mixed" ones are of 2026-10-17 and 2026-10-26. So the kind and the date go together in this set.
- The kind reads the note and the stack heading only. It does not read what the taker did after the take.
- The window of A93 (H32) stays at 105 minutes, so that its old labels stand. The full window now holds one dialog answer of Roman at 112.9 minutes, "[No preference]". The read does not count it.
- A message that Roman typed in the sender's terminal after the take is not in the taker's transcript. The read does not count it.
- An edit that a shell command or a script makes is not a first act. The read did not open the subagent transcripts.
- The records do not show whether Roman was at the terminal when he typed nothing. They do not show what the taker read or understood.
- The first-act target comes from the tool input cut at 160 characters.

### Dropped

- 151 receipts exist. 55 have no note, 3 have a note and no taker transcript, and 2 notes match no receipt. These are the same as in the earlier read.
- No new receipt came after the earlier read. The count of receipts is still 151.
