# The cases where Roman turned the session, read 2026-11-11

## Result first

1. The 97 transcripts hold 587 messages of Roman from 2026-10-11 to 2026-11-11. 251 are cases, and 83 of them are marked unsure.
2. 43% of his messages are cases, 29% without the unsure ones. That is 9.0 cases on each day that he typed anything.
3. Two readers agree on 48 of 60 drawn messages. They agree on 54 of 60 when "case" and "unsure" count as one.
4. The cases fall into 12 kinds. The largest are "Fix at the right scale" 41, "Investigate first" 30, "Order and pace" 23.
5. The files are in the scratchpad folder `a2`: `cases.jsonl`, `cases.md`, `labels.json` and `kinds.json`.

## Method

1. The scan reads every top-level transcript and skips side chains. The script is `a2/scripts/s1_scan.py`.
2. A message of Roman is a typed user entry, a queued prompt or the result of a dialog of questions. The filters copy `a1/scripts/s2_build.py`.
3. The scan leaves out hook text, system reminders, task notices, messages of other sessions, summaries and interrupt marks.
4. It also leaves out 120 slash commands with no words after them, such as "/standby".
5. Eight readers decided the messages by date range, with one brief, word for word the same. A ninth reader decided 60 drawn messages a second time.
6. The draw is `random.seed(20261111)` and `random.sample` over the sorted message ids.
7. One reader gave each case a label. This page groups the labels into kinds. Each label goes to one kind.
8. Each kind shows three cases, drawn with the same seed from its cases that are not unsure. The session text is cut at 300 characters.

## The numbers

- Sessions: 97. Sessions with a message of Roman: 80.
- Messages: 587. Typed 462, queued 61, dialog answers 64.
- Cases: 251. Typed 183, queued 24, dialog answers 44.
- Unsure: 83 of the 251 cases.
- Share of his messages that are cases: 43%. Without the unsure ones: 29%.
- Days on which he typed anything: 28. Cases per such day: 9.0. Without the unsure ones: 6.0.
- Median length of his message in a case: 72 characters. For all his messages: 44 characters.
- Share of cases whose message holds a question mark: 49%. Without the unsure ones: 44%.
- Agreement of the two readers on 60 messages: 48 exact, kappa 0.69. Case and unsure as one: 54, kappa 0.80.
- The pairs, first reader then second: case/case 16, case/unsure 5, not/case 1, not/not 24, not/unsure 4, unsure/case 1, unsure/not 1, unsure/unsure 8.

### By week, the week starts on Monday

| Week | Days typed | Messages | Cases | Unsure |
|---|---|---|---|---|
| 2026-10-05 | 1 | 1 | 0 | 0 |
| 2026-10-12 | 7 | 168 | 89 | 23 |
| 2026-10-19 | 4 | 95 | 26 | 11 |
| 2026-10-26 | 7 | 174 | 74 | 28 |
| 2026-11-02 | 6 | 85 | 34 | 15 |
| 2026-11-09 | 3 | 64 | 28 | 6 |

The week of 2026-11-09 runs to 2026-11-11 10:38 only.

### Cases by week and kind

| Kind | 10-12 | 10-19 | 10-26 | 11-02 | 11-09 |
|---|---|---|---|---|---|
| Fix at the right scale | 16 | 1 | 17 | 2 | 5 |
| Investigate first | 12 | 0 | 7 | 5 | 6 |
| Order and pace | 9 | 3 | 8 | 1 | 2 |
| Design of the product | 6 | 3 | 1 | 13 | 0 |
| The model choice | 8 | 7 | 4 | 1 | 0 |
| The question is unclear | 8 | 4 | 4 | 2 | 2 |
| The point is missing | 5 | 1 | 12 | 0 | 1 |
| Stop, doubt or another choice | 6 | 2 | 3 | 8 | 0 |
| The method and the direction | 4 | 0 | 6 | 0 | 7 |
| Sessions and hand-offs | 7 | 2 | 3 | 0 | 4 |
| Decide it yourself | 6 | 1 | 5 | 2 | 1 |
| What already exists | 2 | 2 | 4 | 0 | 0 |

## The kinds

### Fix at the right scale
He says that a fix is too narrow, fits one case, or is the wrong kind of fix. 41 cases, 16%, 12 unsure. First 2026-10-13, last 2026-11-10.

- C0026, 2026-10-15T01:54:22+01:00. SESSION: "Frame 230's pass 1 is in the checkout: the invoke door now refuses a lambda or a plain function, nine tests red then green, and the implementer's gate showed the known reds only. My own gate runs now, about nine minutes, and the commit and the review follow its five lines. One point for the revie..."
  ROMAN: "Ok well maybe I'm too detached from the development to know what kind of logic we are encoding in the doors but I want to prevent over fitting. All I'm saying is that when we hit walls the solutions can range from simple to complex but theres only so many kind of changes we can make"
- C0041, 2026-10-15T11:53:23+01:00. SESSION: "Q: [high] What are the rungs above the cheap fix, in order of cost? / - Design on a shared cause, then a stronger check, then you (Recommended): Cheap: a door, a brief line, a record a seat reads, a runner fix, tested on past nights in one or two cycles. Next: a design frame that changes the wiri..."
  ROMAN: "I guess for now there is only cheap  and escalate to me"
- C0127, 2026-10-26T20:33:46+00:00. SESSION: "Frame 324, in one sentence: when a criterion names a function that exists both in the library and in a demo under the examples folder, how does rota make the seat name the library's one? / Today the Terminologist can write the demo's full path, the respecify door admits it, and two test doors then..."
  ROMAN: "fuck like the initial fix was so narrow minded"

### Investigate first
He asks for a read, a reason or a cause before a fix, a build or a choice. 30 cases, 12%, 5 unsure. First 2026-10-15, last 2026-11-10.

- C0085, 2026-10-18T11:59:57+01:00. SESSION: "Q: [med] My reading of your rule, to confirm. Before any question reaches you, the session reads the provenance of the thing the question is about: which ruling of yours made it, which build decision shaped it, on what date, by which workflow, and whether the build met the design's own condition...."
  ROMAN: "Ask me still, but it's not about just deviations from the spec, but any inconsistency or issue with the tool. Spend the time to understand it before making fixes, anyql questions?"
- C0128, 2026-10-26T20:40:26+00:00. SESSION: "Frame 324 now carries Roman's ruling of 20:37, "yeah ok general", relayed by rota-af, with the reading and the rewritten Ends-when and Waits-on lines at 8264e4fd. The sender is released. The night runs with no CYCLE line yet, and the monitor waits on it."
  ROMAN: "so why do you not pull all the context you need/ use subagents to answre questions when you run into faults in rota?"
- C0182, 2026-10-29T11:44:24+00:00. SESSION: "That is the composition itself, and it is better than my version. Mine moved the strong model aside and put Opus in the seat that faces you. Yours keeps Fable where your ruling put it, the one seat that faces you and judges, and pushes the labour down to seats that wake cold on a frame. The reser..."
  ROMAN: "Hmm, get a fresh session to review and re-design"

### Order and pace
He turns what runs first, what must be ready before a night, and how fast the work moves. 23 cases, 9%, 7 unsure. First 2026-10-12, last 2026-11-10.

- C0012, 2026-10-13T18:49:11+01:00. SESSION: "Yes, that makes sense, and it is cheap, because half of it exists. / **The checkpoint tracker.** Every session row already carries a `briefs_hash` column, so the database records which briefs each wake ran under. The warm snapshot after onboarding is the one restore point today. The cheap version ..."
  ROMAN: "so not a full checkpoint per session but a rewindable database / the biggest issue, mm ok that sounds too convoluted, should we just keep working the way we are?"
- C0120, 2026-10-26T19:30:44+00:00. SESSION: "Honest reading: rota merges readable changes on its own on a good night, and not yet on most nights. The limit is rota's doors, not the model. / **Where it stands against the destination** / - On night 166, qwen3.5:9b merged 2 of 3 small click items cold, in 43 and 38 steps, with 5 and 4 asks of th..."
  ROMAN: "ok are we not fixing all the things in one go before the next night?"
- C0121, 2026-10-26T19:32:48+00:00. SESSION: "No. The practice so far is one or two fixes per night: the wall that stopped the last night first, then the night measures it. Your question points at the other way, and the records favour it for the cheap rows. / **What batching more before night 169 buys** / - Rows 4 to 6 of sprint 25 are one cyc..."
  ROMAN: "i mean, are we wasting time by not trying all the fixes, (not all the frames)"

### Design of the product
He turns which part of the product owns, reviews, verifies or records a thing. 23 cases, 9%, 9 unsure. First 2026-10-12, last 2026-11-08.

- C0003, 2026-10-12T23:29:13+01:00. SESSION: "Q: [med] A default the seats took and never showed you, and the change has shipped with it. What happens to that note at the merge? / - Park it at the merge (Recommended): Filed under the shipped request, visible in the state view if you look, never on a page again. Nothing asks you. Follows your..."
  ROMAN: "so it should be part of architect review right?"
- C0196, 2026-11-03T00:31:49+00:00. SESSION: "Your hypothesis holds on the evidence. The 235 notes are mostly true and mostly worthless. If the survey wrote what matters, the page would hold a handful of lines and nobody would ask about its size. / **Does the understanding system make sense?** As a structure, yes. A deterministic index of gra..."
  ROMAN: "ok but what does project understanding mean for rota? / the current architecture has a lot of dependent processes on the reccords of understanding / but have we designed the way that rota needs to makeits understanding that the rest of the system depends on? / back to front or front to back?"
- C0201, 2026-11-03T09:50:40+00:00. SESSION: "Six changes, in the order they change what understanding means: / 1. **Understanding is judged by what it changes, not by what it records.** The measure is the merged diff, the page you see and hidden probe tests, with a run that withholds the records as the baseline. Today three merges happened w..."
  ROMAN: "Ok but understanding can also be measured by what the tool can answer about the project / And whole project understanding is key for efficient solution designs for future work"

### The model choice
He turns which model runs a seat or a read, or asks whether a model was tested. 20 cases, 8%, 8 unsure. First 2026-10-13, last 2026-11-08.

- C0018, 2026-10-13T19:30:37+01:00. SESSION: "Agreed, and the frame is pushed that way: no token cap. Frame 232 stops the stream at the protocol's boundary. / - **The stop is structural, not a count.** A seat's turn is one `TOOL:` call. The reader ends the stream when the call is complete, by the parser's judgement of the line, not at a fixed..."
  ROMAN: "I thought some seats can do multiple calls?"
- C0111, 2026-10-25T14:25:08+00:00. SESSION: "Yes. Ollama lists `tools` and `thinking` among this Gemma build's capabilities, the same as qwen3.5:9b. But rota has never used it, on any model. / - **Every run is the text protocol.** All 390k register rows, Qwen and Gemma, carry protocol `text`: the model writes `TOOL:` lines and rota's own par..."
  ROMAN: "Whaaat ok, / do a couple tests that they were both struggling on with tool calling / i like the idea of the night but we need to iron out basic gemma quirks before running it. / and tool calling test on both goes first"
- C0112, 2026-10-25T15:22:37+00:00. SESSION: "Small. A few percent of model time, and nothing on the part that bounds a night. The numbers come from 40197 calls in Ollama's log on this machine. / | Call shape | Share of calls | Wall per call | Prefill share | Projected gain per call | / |---|---|---|---|---| / | all calls | 100% | 4.6 s | 12% | 2..."
  ROMAN: "but if we only use one model for everything"

### The question is unclear
He does not understand a question or a reply, or he cannot see it. 20 cases, 8%, 8 unsure. First 2026-10-12, last 2026-11-10.

- C0035, 2026-10-15T11:14:59+01:00. SESSION: "Q: [high] Is a checker that grows by your sentence shapes an accepted standing fix for a hand that rewrites your words, or only a stopgap? / - Yes, gated by the count (Recommended): Accepted when a count over every night shows each known case refused and no right rewrite refused. The count is the..."
  ROMAN: "I have no idea what this means"
- C0036, 2026-10-15T11:43:58+01:00. SESSION: "Q: [high] When a seat rewrites your words, may the fix be a list of your phrases in the code, if it is counted on every past night first? / - Yes, if counted first (Recommended): A phrase list is a fine fix when a count over all past nights shows it catches every known case and blocks no right re..."
  ROMAN: "What is this question, redesign the wall guide from first principles on fable"
- C0062, 2026-10-17T18:19:17+01:00. SESSION: "Q: [med] The story. An assistant takes over a desk on Monday. Its predecessor left a tidy to-do list and a filing cabinet of memos, laws and meeting notes. On Tuesday the assistant meets a question. Today it greps the cabinet for the error text, finds nothing, and asks the boss, who answered the ..."
  ROMAN: "nothing measurable, we stay aware of all relevant points previously discussed without clutter"

### The point is missing
He presses for what follows from a reply, what it means, or what it is for. 19 cases, 8%, 8 unsure. First 2026-10-13, last 2026-11-10.

- C0042, 2026-10-15T11:54:32+01:00. SESSION: "Q: [high] What tells a cheap fix apart from one that only fits tonight? / - It states a fact or a rule of rota, not tonight's words (Recommended): A door that checks who owns a record, or a record that carries your words to the builder, is about the structure. A door that lists the phrases you ty..."
  ROMAN: "I thought that this is the kind of knowledge that we just have about the project. Use opus to do deep research. But first I dont feel like you see the value of this"
- C0136, 2026-10-26T22:04:25+00:00. SESSION: "Three things, in order of size. / **The build session has the same fault as rota.** A rota door re-derives your ruling from your words by its own pattern instead of reading the record. The session re-derived the cause from the frame's status lines by its own reading instead of reading the code. Bo..."
  ROMAN: "Ok but we found an issue with the workflow and the processed backlog, so what follows?"
- C0138, 2026-10-26T22:08:45+00:00. SESSION: "At three horizons. / **Tonight.** Frame 339 commits, I gate it and hand the stack to a standby with the note. The taker runs the re-cut first, then frame 330's pass, then night 170 on 339 and 330. That night tells us whether the stop at the removal door was the only wall in walk 1. / **This week.**..."
  ROMAN: "No I'm still not hearing what I'm expecting, we found significant issues in the workflow / What follows?"

### Stop, doubt or another choice
He stops work he did not ask for, states a doubt, or picks a choice other than the one recommended. 19 cases, 8%, 9 unsure. First 2026-10-12, last 2026-11-08.

- C0078, 2026-10-18T03:17:40+01:00. SESSION: "Stopped. The triage read is killed, the amendment with it, and nothing of it reached the stack. The two implementers, build step 2 and frame 258's pass 3, still run. You asked me to think and tell you, and I acted on my own answer instead. I wait for your word on the backlog."
  ROMAN: "I just asked for your thoughts on the backlog, I don't like the direction. Let's just keep working"
- C0153, 2026-10-27T14:46:56+00:00. SESSION: "Q: Your ruling of 2026-10-24 01:05 said: a docstring line counts as evidence for a check whose own words ask for a "docstring", "document" or "help text". A build session then dropped "document" and "help text" from that list without asking you. Its reason: "document" matched a check about an opt..."
  ROMAN: "[1] Your ruled words (Recommended) / [2] The role"
- C0156, 2026-10-27T18:57:04+00:00. SESSION: "f20root, f19root and f31root are on `rota/foundation`, at e42d13d1. Each gate shows the 11 known reds and no new red. The gate on the F25 merge runs now. The F7 implementer is adding the summary line for unasked deletions after an auto merge. After F25, the land order is F37, then F7 once it is r..."
  ROMAN: "Wait why?"

### The method and the direction
He turns the meta workflow, the goal of the project or its target capabilities. 17 cases, 7%, 6 unsure. First 2026-10-15, last 2026-11-10.

- C0083, 2026-10-18T11:51:02+01:00. SESSION: "Q: [high] Frame 298. What "nobody writes it" means, exactly. The line is produced by a function inside the page builder at the moment the page is printed. It splits your request into words of four letters or more, looks each word up in the index of names in the code, counts hits per file, and pri..."
  ROMAN: "This is really strange, is this a meta workflow mistake? What happened?"
- C0178, 2026-10-29T09:52:55+00:00. SESSION: "Asked rota-62, the session that chose the design, which options its read weighed, why option (d) won, and whether a per-line wake was among them. Its answer comes as a message and I relay it to you as it says it. / rota-62 answered. Its read weighed four options and the per-line wake was not one o..."
  ROMAN: "Ok the current solution is less important than the workflow right now. / Why was the workflow limited?"
- C0245, 2026-11-10T12:56:33+00:00. SESSION: "The product review now has a design, and two sessions are about to ask you questions that point in different directions. / - **Rota-a4** says the product design is written: [plans/method/product-design-2026-11-10.md](plans/method/product-design-2026-11-10.md), six shapes. Its first shape is the ru..."
  ROMAN: "None of the other sessions understand, they're all doing their own thing and don't understand the goal of spiraling well"

### Sessions and hand-offs
He turns how sessions hold context, hand off, wait and talk to each other. 16 cases, 6%, 6 unsure. First 2026-10-12, last 2026-11-10.

- C0071, 2026-10-18T02:30:03+01:00. SESSION: "One line first: this session is past 300k, the reserve has no standby, and a window is needed for the hand-off when it comes. / Now the thinking, taking your answers in. / **On 2.2, your rulings on the state page.** You are right to ask. I put them there out of habit: the brief treats your words as..."
  ROMAN: "yes there are standbys / 2.2 what do you mean standing intent? is recency of my intent important for the project? / session handover, i dont know what you need to ask the previous session, its just an option for the new session to complete their understanding etc. I dont have the words to complete the idea. / maybe last 50k not 100? / and an important consideration for your context, there are long stretches where its just a series of sessions without my intervention / yeah, take time to think, think about how to write this up, ensure you dont miss anything / any questions?"
- C0109, 2026-10-25T13:52:50+00:00. SESSION: "Three things, in order of weight. / - **Frame 325's revert is a judgement nobody read.** The sender's second step turned 22 pins red and was reverted. The pins protect the old agenda wake, and nobody read what each one protects. The sender also assumed that a ruling of 2026-10-11 beats a pin of 20..."
  ROMAN: "i mean about the standby timeout, if not implement"
- C0250, 2026-11-10T13:55:21+00:00. SESSION: "Rota-a4 answered the case, and the answer is not a copy of my words. Two of my hypotheses held for this one session. The channel problem stays open, because rota-3d is still silent. / **What rota-a4 said** / - **On the difference:** it now agrees that one turn has two halves. It added a point that ..."
  ROMAN: "Well are you sure? Do we need to research inter session communication from first principles?"

### Decide it yourself
He says that the session can judge a thing that it asks him, or that is settled. 15 cases, 6%, 2 unsure. First 2026-10-12, last 2026-11-10.

- C0088, 2026-10-18T13:23:36+01:00. SESSION: "This session reads 352k, past the 350k hand line, and the reserve has 0 free standbys. Please open a window and arm it as a standby. I hold the stack until pass 3's report lands, commit it, update the momentum note, and run the hand command. With no standby the frame waits on disk until one arms,..."
  ROMAN: "you already have standbys, check before asking"
- C0168, 2026-10-28T14:27:00+00:00. SESSION: "Yes, that is the right scale, and it does not exist yet for this loop. The register has one multi-step level, L3, "does A's message make B do the right thing", run on the real model. Six L3 cases exist: a ratified statement becomes scope, scope becomes a ticket, a challenge reaches the owner, a f..."
  ROMAN: "Why can't you judge?"
- C0227, 2026-11-10T00:32:26+00:00. SESSION: "Q: The review said the build has no seat that holds the whole between dry runs, so the runs repeat and you must steer. You said that sounds good. What do you want this session to do with it? / - Record and design (Recommended): I write the review to a plans page, record your ruling that the seat ..."
  ROMAN: "I want you to take charge of redirecting the project"

### What already exists
He says that the session overlooks a system, a solution, a cause or an item that exists. 8 cases, 3%, 3 unsure. First 2026-10-17, last 2026-10-26.

- C0052, 2026-10-17T04:33:00+01:00. SESSION: "Session b0dce033, peer rota-68. Not a standby: the arm found frame 274 waiting on disk and took it at once. / **State.** I hold frame 274, the keypress's inferred carrier, and the stack at f2679a58. The frame is validating at 6553d0f1. Night 153, sprint 10's night, runs from 0617afda: onboarded in..."
  ROMAN: "for the question that youre blocked on, / is there not an obvious answer? / present the information correctly the the llm when required??"
- C0092, 2026-10-24T01:29:58+01:00. SESSION: "The question: when a review has run out of attempts on a change whose tests pass, and you approve the page, should your approval start the review again? / - **Yes, recommended.** Your approval clears that one stuck review, and the reviewer gets three more attempts. Today your approval does nothing..."
  ROMAN: "Yes there needs to be a passing review. Did you think about the fact that the issue that created this issue will be fixed?"
- C0126, 2026-10-26T20:24:30+00:00. SESSION: "No. I proposed it from the two reads on frame 324 and the composition page, without reading the onboarding or the index. That was a reasoned proposal presented as if it were grounded, and it broke the rule that a claim about what is built is checked first. The check runs now, and I correct the pr..."
  ROMAN: ""a full path into an attached folder is re-pointed" why? the path should already be the right path if the seat that makes it is already guided by the onboarding classificaitons. is that right?"

## Limits

- One reader decided each message. A second reader decided 60 only.
- A reader saw the last reply up to 3,000 characters, the reply before up to 600, and 8 tool calls. An older reply that he answers is out of view.
- The first readers named 19 messages that react to a text their block did not show. Their session text can be the wrong one.
- A third of the cases are unsure. The counts with and without them differ a lot.
- One reader gave the labels. This page put each label into one kind. A case can touch two kinds, and it counts in one.
- The session text of a dialog answer is the question and its options. One of 64 dialog results did not parse, and it stays whole.
- The share of questions counts a question mark in his text, nothing more.
- A few cases are about work outside rota, for example a search on his computer. The readers kept them.
- The transcripts start on 2026-10-11, not on 2026-10-10. A message that he typed outside these transcripts does not show.
- Times are local: UTC plus one hour before 2026-10-25 01:00 UTC, UTC after it.
- On this page a line break in a quote shows as " / ". The files keep the line breaks.
- The files are in the scratchpad folder, which is not in git.
