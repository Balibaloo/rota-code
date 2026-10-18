# The rulings ledger

This file records the outcomes of discussions between Roman and the build sessions: what was asked, what he said, what it means, and where the rule lives.
One writer keeps it: the session that holds the frame. No other session and no agent writes it unless that session briefs the agent.
A session searches this file by the words of its question. No session loads it whole at start.
An entry never changes a rule by itself. A rule changes only in the file that the entry's `Rule:` line names.

### R1. The seed interview runs at intent time, and the sign-off page shows the open assumptions (2026-09-03, rota workflow)
- Keys: seed interview, intent-time, intent time, signoff page, sign-off page, open assumptions, law 8, law 11, `principal.land`, approve keypress, contest with words, "derive it" default, elicitation, A1, tip calculator, what are the inputs, `how_it_works`, `render_refs`, `plans/a1-seed-interview-at-intent.md`, SEAT.md
- Situation: The principal typed "tip calculator pls", three desks read it as three programs, and nobody asked what the inputs are. The audit graded elicitation as designed but not built.
- Said: "lets do this now, this is a usability priority" (2026-09-03, time unknown, session unknown)
- Means: The interview runs at intent time too, and what the words left silent is logged where a desk assumed it. The page the principal signs carries those assumptions. Approve takes the default, and a contest goes back to the desk that assumed it. (reasoned: the agent's reading of the record, which the session wrote)
- Rule: `rota/DECISIONS.md`, "### The seed interview runs at intent-time, and the signoff page is its first moment" (line 1340); build order in `plans/a1-seed-interview-at-intent.md`
- Supersedes: none

### R2. Two sources in the repository that disagree always go to the principal as a page (2026-09-12, rota workflow)
- Keys: conflicting sources, conflict page, two documents disagree, recency, prefer code, the four pages, one surface, interview page, touch guess, amendment, `principal.land`, hold at intent time only, amendment level 2, level 3 invalidate by touch, `rota/DECISIONS.md` four pages
- Situation: Roman ruled on the four kinds of page that the principal answers: the interview, the touch guess at sign-off, an amendment, and a conflict between sources. The question was whether the tool may settle a conflict by itself, by recency or by preferring code.
- Said: no verbatim words in the record. The record gives his reason as a paraphrase: "a conflict page that never appears on a repository with conflicts shows the tool is failing" (2026-09-12, time unknown, session unknown)
- Means: The tool never resolves a conflict between two documents by itself. A repository with conflicts and no conflict page is a failing tool. (reasoned: the agent's reading)
- Rule: `rota/DECISIONS.md`, "### The seat's four pages are one surface (2026-09-12)", ruling 4 (line 1370)
- Supersedes: none

### R3. There is no silence: a page is a hold or a note, and no predicate reads a clock (2026-09-13, rota workflow)
- Keys: silence approves, no silence, hold, note, keypress, batch defers, owed on the register, contest after the work, amendment, law 9, predicate reads a clock, wall, step, slice read, plan path, principal flow, `plans/principal-flow.md`, wsff, click first, defaults measured by a person, Critic cost, band order
- Situation: The design `plans/principal-flow.md` took six pages and three paths from the "Why Software Factories Fail" talk. Roman ruled five points on it, and one point was whether a page that nobody answers counts as approval.
- Said: no verbatim words in the record. The record lists five rulings under "Roman ruled:" (2026-09-13, time unknown, session unknown)
- Means: A page either waits on a keypress (a hold) or waits on nobody (a note). A note stays owed, and a contest after the work is an amendment under law 9. No predicate reads a clock, a wall or a step, and "silence approves" is gone. (reasoned: the agent's reading)
- Rule: `rota/DECISIONS.md`, "### The principal's flow: five rulings (2026-09-13)", ruling 2 (line 1418)
- Supersedes: none

### R4. A red project test with the criterion's own test green is the builder's own regression, and the principal gets no question (2026-09-14, rota workflow)
- Keys: broken project test, project's own tests red, builder's regression, Developer regression, parked batch, park ask, page to the principal, criterion test red, intent disagreement, note with no question, escalation, frame 114, frame 115
- Situation: A batch parked because tests failed. The question was whether every parked batch goes to the principal for a ruling.
- Said: no verbatim words found in the four sources. `rota/DECISIONS.md` cites "builder's regression (ruled 2026-09-14)" (time unknown, session unknown)
- Means: Only a red criterion test may be a disagreement about intent, so only that case goes to the principal. When only the project's own tests are red, the builder broke what worked, and the team writes a note with no question. (reasoned: the agent's reading of the 2026-10-08 entry that cites the ruling)
- Rule: `rota/DECISIONS.md`, "### The park ask is a page with rows..." point 3 (line 1466); `CLAUDE.md`, the paragraph "Before a frame blocks on Roman" cites it
- Supersedes: none

### R5. A seat failure is first placed as a fault of the model's context or a fault of the model itself (2026-09-18, rota workflow)
- Keys: Developer regression, night 70, night 86, merge luck, categorise, categorize, model context, data, tooling, environment, prompt, the model itself, cause of a failure, what went wrong, last suspect, wall guide, `plans/wall-guide.md`
- Situation: Night 70 merged, and night 86 then cut a batch from the same sentence and the Developer used ten attempts on its tests. Either something regressed or night 70's merge was luck.
- Said: "so we dont know what went wrong, but what went wrong is either in the model context (data/tooling/environment) or in the model itsself, so we need to categorize that" (2026-09-18 15:03 UTC, session 75d12c2b)
- Means: The frame ends when the cause is placed as one of two: what the Developer was given differs between the nights, or it was given the same thing and the model did differently. (reasoned: the agent's reading, written as the frame's ends-when)
- Rule: `plans/archive/stack-2026-09-23.md`, the investigation frame's ends-when (line 1224); the cause order today is `plans/wall-guide.md`, section 4
- Supersedes: none

### R6. The higher context window goes to every wake, and a strict monitor watches for a spill into RAM (2026-09-19, rota workflow)
- Keys: context window, num_ctx, 12288, 16384, second cap, higher cap, paging, spill into RAM, spill monitor, `/api/ps`, turn speed warning, bounded wake, unbounded wake, context length management, context caps, `discover.recommend`, `setup.plan`, fit table, turn-2 dumps, frame 43
- Situation: The assistant recommended that the higher window stay in the design with no workload assigned, because no workload needed it yet. The day before, Roman had said that the second cap exists only to avoid paging and that "the gating factor is required quality not low frequency".
- Said: "1 ok give higher window to everyone but monitor strictly when the higher context is actually spilling into ram" (2026-09-19 02:50 UTC, session 9108c499)
- Means: The window rises for every wake, and a monitor warns with specifics, until dismissed, only when a spill really happens. (reasoned: the agent's reading, from the price line "The window rises to 16384 for every wake")
- Rule: `plans/archive/stack-2026-09-20.md`, price line 1 (line 95); the design is `plans/archive/context-caps-design-2026-09-18.md`
- Supersedes: none

### R7. A decision notifies Roman's phone, and not only a waiting prompt (2026-09-20, meta workflow)
- Keys: notification, mobile notification, phone, PushNotification, AskUserQuestion, `inputNeededNotifEnabled`, decision must notify, input and decisions, escalation, blocked frame, one notification per stop
- Situation: Roman asked for mobile notifications in this project, and the first set-up covered only input prompts. He then asked for decisions too.
- Said: "Ok that worked, can you do notifications for both input and decisions" (2026-09-20 02:14 UTC, session 0549dc76), then "Oh ok no you were right, that's proactive" (02:16 UTC, the same session)
- Means: An input prompt notifies by the harness setting. A decision in prose notifies by a message the session sends itself. (reasoned: the agent's reading; the assistant's reply between the two messages is not in the sources)
- Rule: `CLAUDE.md`, the paragraph "An escalation reaches Roman on his phone" (line 466)
- Supersedes: none

### R8. A frame is named in words, because Roman does not know the frames by number (2026-09-20, meta workflow)
- Keys: frame name, frame number, heading, status line, "Frame 50" is an index, what is happening, plain words, report to Roman, F-number, tag
- Situation: A hand-off happened while Roman read the terminal, and the replies named frames by number only. He could not follow what was happening.
- Said: "I don't know the frames by numbers, what  is happening?" (2026-09-20 14:51 UTC, session 0549dc76)
- Means: Every frame carries a name of a few words in its heading, and every mention of the frame carries the name with the number. (reasoned: the agent's reading, written later into `CLAUDE.md`)
- Rule: `CLAUDE.md`, "Every frame carries a name of a few words in its heading" (line 512); memory `rota-frames-mean-not-number.md`
- Supersedes: none

### R9. A hand-off means the session stops and the whole stack goes to one session, never side work to a second worker (2026-09-20, meta workflow)
- Keys: hand-off, hand off, handover, `handover.py hand`, standby, side work, parallel work, two sessions one checkout, one session holds the stack, `plans/stack.md` overwritten, dispatch to a standby, Roman assigns work
- Situation: The session handed a frame it had never held to a standby and kept working. Two live sessions then wrote `plans/stack.md` in one checkout.
- Said: "Ok, I don't mind handing off but handing off means stopping and handing off the stack, not handing side work to another worker." (2026-09-20 14:55 UTC, session 0549dc76)
- Means: Run `hand` only when this session stops. A task that looks like it needs a fresh session is a frame on the stack, not a claim to a standby. (reasoned: the agent's reading, written into `CLAUDE.md`)
- Rule: `CLAUDE.md`, "A hand-off means you stop and the stack goes to one session" (line 96); memory `hand-off-means-stopping.md`
- Supersedes: none

### R10. The old register is cloned as a legacy backup, what is useful migrates, and a full re-record is approved (2026-09-21, meta workflow)
- Keys: register, `tests/rota/cassettes.db`, legacy database, backup, clone, migrate, full re-record, re-record approval, history of what the model did, evidence that gates an acceptance, `casestatus`, stale, frame 49, frame 55
- Situation: The register mixed the record of what the model did with the evidence that gates an acceptance. The session offered three options, and Roman chose none of them.
- Said: "clone this as a backup legacy dB and migrate over what's useful, full re-record is approved if necessary" (2026-09-21, time unknown, session unknown; the status line is 15:20)
- Means: The clone keeps the history. The new register holds only the evidence that gates. A re-record needs no further ask. (reasoned: the agent's reading in the same status line)
- Rule: `plans/archive/stack-2026-09-21.md`, status 2026-09-21 15:20 (line 1239); memory `rota-rerecords-are-cheap.md`
- Supersedes: none

### R11. The assistant runs the nights the stack needs and does not ask per night (2026-09-22, meta workflow)
- Keys: night, walk, sign-off, signoff to run the nights, GPU, launch a night, ask per night, start the night now, hour of the night, frame 63, night 89, validating frame
- Situation: Frame 63's walk was asked twice in one day and each time held for his word. The session asked a third time with "start the night now" recommended.
- Said: "You have signoff to run the nights" and "Continue however is best" (2026-09-22 19:28, session 41cb5184)
- Means: The ruling is standing. The hour stays the assistant's judgement, because a night takes the machine for about two hours. (reasoned: the agent's reading, written into the operating facts)
- Rule: `plans/operating-facts.md`, "## Running rota", "The assistant has sign-off to run the nights" (line 173)
- Supersedes: none

### R12. The `think` pin goes into every tier's cassette key, and the full re-record is the accepted price (2026-09-23, meta workflow)
- Keys: cassette key, `think`, `think: false`, `think_for`, `Pins.think`, key omits a value the wire carries, STALE, full re-record, 128 live calls, `rota/testkit/fixtures.py`, frame 65, the cassette key cannot pin a field it omits, register
- Situation: Every tier built its pins through `think_for`, which returned `None`, while the backend always sent `think: false`. The key omitted a value the wire carried, and 162891 of 162921 rows were keyed at the absent value.
- Said: "Repair" (2026-09-23, time unknown, session 001e49dd holds the frame; asked with the count)
- Means: Every case reads STALE after the repair until a full re-record. He chose the repair from options that carried that count. (confirmed: he chose the asked option with its price in front of him)
- Rule: `plans/archive/stack-2026-09-23.md`, frame 65, "The price" (line 303); `rota/testkit/fixtures.py`, the comment "a set pin keys the recording" (line 962)
- Supersedes: none

### R13. When a stronger model would also fail on the same turn, the fault is the structure's and not the model's (2026-09-23, rota workflow)
- Keys: self healing, self-healing, structure's fault, structures fault, model capability, Gemma, larger model, stronger model, Opus as a seat, every local model invents, evicted result, `_fit`, repeat refusal, fabrication, frame 75, frame 76, cause of a wall, the structure is the agent
- Situation: The session reported the limits of the seats on a night. Every local model invented a result under the same pointer to an evicted source.
- Said: "Have we confirmed that larger models, eg Gemma are capable? If not then it's the structures fault" (2026-09-23 14:08 UTC, session dba7e375), after "The system is meant to be self healing, are the limits clearer?" (14:03 UTC)
- Means: Before a wall is put on a model, check that a stronger model succeeds on the same turn. If no model succeeds, fix the structure. (reasoned: the agent's reading, written into the wall guide)
- Rule: `plans/wall-guide.md`, the cause entry that quotes "Roman's test" (line 317); `plans/composition.md`, "The structure is the agent"
- Supersedes: none

### R14. Opus builds and Fable judges, and the judge line stays after a blind count (2026-09-24, meta workflow)
- Keys: Opus, Fable, judge line, reviewer model, design review model, implementer model, blind review, false finding, absent value read as a date, frame 74, frame 65's ten findings, `model: "opus"`
- Situation: An Opus 5.5 reviewer read frame 65's commit blind. It found 8 of 10 findings, missed 2, and added 1 false finding that read an absent value as a date.
- Said: no verbatim words. He took both recommended answers in one notification, "the line stays, Fable judges" among them (2026-09-24 01:07, session 2087bc13)
- Means: Opus implements and sweeps. The holding session, on Fable, judges the output. (confirmed: he took the recommended answer as written)
- Rule: `CLAUDE.md`, "Opus builds, Fable judges" (line 290). The same paragraph now records the ruling of 2026-10-07 that puts every agent on Opus and keeps Fable for the holding session alone.
- Supersedes: none

### R15. Warm onboarding is the gauntlet's default, and a cold run is the exception (2026-09-24, rota workflow)
- Keys: warm onboarding, warm start, cold onboarding, `GAUNTLET_COLD=1`, onboarding cache, automatic invalidation, soft file, night, walk, gauntlet default, onboarding phase
- Situation: Roman asked if the warm onboarding system still cached onboarding for the walks. It existed but was not on by default.
- Said: "Why is this not always on? This has automatic invalidation right?" (2026-09-24 01:23 UTC, session 2087bc13)
- Means: Warm is the default. Set `GAUNTLET_COLD=1` when a frame's walk covers onboarding or a soft file moved. (reasoned: the agent's reading, written into the operating facts)
- Rule: `plans/operating-facts.md`, "Warm is the gauntlet's default since 2026-09-24" (line 162)
- Supersedes: none

### R16. When Roman is away, the session judges without him, and a ruling still goes to his phone (2026-09-24, meta workflow)
- Keys: afk, away from keyboard, judge without me, autonomy, decide alone, ruling, notification, AskUserQuestion, hand off if needed, 400k, night 91
- Situation: Night 91 ran, and Roman left the keyboard. The session asked how far it could decide alone.
- Said: "Ok I'm going afk, judge without me for now, don't hesitate to hand off if needed" (2026-09-24 01:29 UTC, session 2087bc13)
- Means: The session decides judgement and completion. A ruling still goes by one AskUserQuestion with the recommended answer, and the frame waits on it. (reasoned: the agent's reading in the status line)
- Rule: `plans/archive/stack-2026-09-23.md`, status 2026-09-24 02:29 (line 2071); today the rated-question rules in `CLAUDE.md`, "Rate every question's impact"
- Supersedes: none

### R17. An unclear hand-off goes as a message to the previous session, not to Roman (2026-09-24, meta workflow)
- Keys: hand-off unclear, ask the previous session, sender, context question, message the sender, grill, momentum note, `plans/handoff-<sid>.md`, standby wake, Roman answers rulings only
- Situation: A session took a hand-off and had questions about the context. Roman named who answers them.
- Said: "Message the previous session if not clear, unless you need to grill me" (2026-09-24 14:56 UTC, session 8736e9fc)
- Means: A context question goes to the sender. Only a ruling goes to Roman. (reasoned: the agent's reading)
- Rule: memory `ask-the-previous-session-first.md`; `CLAUDE.md`, the momentum-note paragraph, "messages the sender for a context question before it asks Roman"
- Supersedes: none

### R18. One read-only diff review runs after every pass, whatever the pass touches (2026-09-27, meta workflow)
- Keys: diff review, review after every pass, reviewer, worktree at the pass's commit, predicate, write path, narrower review line, frame 86, four reviews, defect left by a pass, walk
- Situation: Frame 86 had four reviews, and each found a defect that the previous pass left. The session offered a narrower line, a review only where a predicate or the write path moves.
- Said: "What do you meant by diff review only when a predicate or write path moves?" (2026-09-27 18:38 UTC, session 213e58fd), in the same message as "Status changes, yes" and "Hand off, sure"
- Means: Every pass gets one read-only review on a worktree at its commit. The last review runs before the walk. The narrower line is declined. (reasoned: the agent's reading as written in `CLAUDE.md`; his final words are not in the four sources)
- Rule: `CLAUDE.md`, "One read-only diff review runs after every pass" (line 408)
- Supersedes: none

### R19. A CYCLE line during a night is read when it fires, not at the end of the night (2026-09-29, meta workflow)
- Keys: CYCLE line, cycle detection, loop, night, walk, wait for the end, check a cycle, step cap, stop a night, read the turns, push a frame while the night runs
- Situation: Roman asked if the runs detect cycles. The session had waited for a night's end before it read the records.
- Said: "Don't wait for end blindly, if you hit a cycle, check it" (2026-09-29 04:28 UTC, session b4768744)
- Means: At a CYCLE line, read the turns, the calls, the commits and the count at once, and push the frame while the night runs. (reasoned: the agent's reading, written into memory)
- Rule: memory `rota-check-a-cycle-when-it-fires.md`; `CLAUDE.md`, "A night is stopped when its loop is a known open frame's wall" (a later ruling, 2026-10-09)
- Supersedes: none

### R20. A session past 300k that holds no frame hands off at once and is never idle (2026-09-30, meta workflow)
- Keys: idle, 300k, 356k, 400k, no frame, hand off, handover, context count, wait for 400k, standby, empty session, `handover.py hand`, session 7448850f
- Situation: Session 7448850f held no frame at 356k. It asked whether to hand the stack to the standby now or wait.
- Said: "hand off, and you should never be idle like this, the rule is hand off" (2026-09-30 22:46 UTC, session 7448850f, an AskUserQuestion answer)
- Means: The 400k line protects a held frame. It never keeps an empty session alive. (reasoned: the agent's reading, written into `CLAUDE.md`)
- Rule: `CLAUDE.md`, "A session past 300k that closes its last frame hands off at once" (line 20); memory `hand-off-never-idle.md`
- Supersedes: none

### R21. A session past 300k that holds only waiting frames hands off at once (2026-10-01, meta workflow)
- Keys: idle, 299k, 300k, 400k, validating frame, waiting frame, held frame waits on a night, unclaimed frames, frame 106, frame 100, hand off, handover, standby, when to hand off, is waiting for a night idle
- Situation: A session sat at 299k and held one validating frame that waited on a night. Frames 106 and 100 waited unclaimed.
- Said: no verbatim words in the sources. `CLAUDE.md` gives the ruling without a quote (2026-10-01, time unknown, session unknown)
- Means: Idle means every held frame waits on something outside the session. An idle session past 300k writes the status line, commits, and hands off. (reasoned: the agent's reading as written in `CLAUDE.md`)
- Rule: `CLAUDE.md`, "Past 300k, a session that is idle hands off at once" (line 29)
- Supersedes: none (extends R20 from no frame to waiting frames)

### R22. The Architect gets an edge that reads the test runs, so it can see that the last attempt failed (2026-10-01, rota workflow)
- Keys: Architect, reads-tests edge, `test_runs`, graph edge, exhausted rung, dead end, tenth attempt failed, streaming attempt, batch looks finished, frame 106, law 3, contact lists derived
- Situation: At the exhausted rung the Architect read the batch's diff but could not see that the tenth attempt failed, because the graph gave it no edge to the test runs. The seat treated the batch as finished and never reported the dead end.
- Said: "Yes, add the edge (Recommended)", the option he chose for "Does the Architect get a reads-tests edge?" (2026-10-01 14:12 UTC, session 10885dab, an AskUserQuestion answer)
- Means: Add a read edge from the Architect to the test runs. (confirmed: he chose this option)
- Rule: `rota/LAWS.md`, "### 3. Contact lists are derived, not designed" (line 121) governs the edge; no other location read
- Supersedes: none

### R23. The Critic's doubt about a criterion goes to the Terminologist, who writes the criteria, not to the Architect (2026-10-01, rota workflow)
- Keys: Critic, doubt about a criterion, criterion is wrong, challenge edge, Critic to Architect, Critic to Terminologist, who writes the criteria, Terminologist writes criteria, Architect writes constraints, verdict's reason, law 3, contact lists derived, no hand-drawn routes, boot check, declared exception, frame 107, `rota/roles/prompts/critic/base.md`
- Situation: Roman first ruled a Critic-to-Architect challenge edge. The session then showed that law 3 derives every route from who writes the records the sender reads, and the Terminologist writes the criteria.
- Said: "Wait the terminologist writes the criteria? Not the architect?", then "The Terminologist (Recommended)" to "So where does the Critic's doubt about a criterion go?" (2026-10-01 14:24 and 14:25 UTC, session 10885dab, AskUserQuestion answers)
- Means: The route follows law 3. The Critic's doubt about a criterion goes to the Terminologist, and no exception is declared. (confirmed: he chose this option)
- Rule: `rota/LAWS.md`, law 3 (line 121). `rota/roles/prompts/critic/base.md` line 11 still says "A doubt about what a criterion should say belongs to the Architect" (observed: 2026-10-18, this read; later frames not read)
- Supersedes: his first answer of 14:12 UTC, "Yes, add the edge" for a Critic-to-Architect edge

### R24. The dead-end case asserts that a stall leaves the Architect's desk to a named next seat (2026-10-01, rota workflow)
- Keys: dead-end case, dead end, stall, Architect, exhausted rung, proposes a seam, Vision Keeper, loop between proposals and answers, what does the case accept, success criterion of a register case, emergency exit, coverage backlog, frame 106
- Situation: After four passes the Architect at the dead-end rung proposed a seam to the Vision Keeper in every run instead of reporting a dead end. Three of five runs looped, and the session asked what the case should count as success.
- Said: "So looking at the system as a whole, what should happen here and why?", then "Yes (Recommended)" to "Do I rewrite the case to assert that the stall leaves the Architect's desk to a named next seat, and send the emergency exit back to the coverage backlog?" (2026-10-01 16:17 and 16:18 UTC, session 10885dab, AskUserQuestion answers)
- Means: The case passes when the stall moves on to a named seat. An emergency exit is a separate backlog item. (confirmed: he chose this option)
- Rule: none found in the sources read
- Supersedes: none

### R25. Every question to Roman carries an impact rating, and a low one runs on a 20-minute timer (2026-10-02, meta workflow)
- Keys: question rating, impact, high medium low, `[high]`, `[med]`, `[low]`, blast radius, waiting for Roman, idle on a question, timer, 20 minutes, sleep 1200, taken by timeout, notification prefix, PushNotification, AskUserQuestion
- Situation: A session waited idle 5 hours 18 minutes on two questions whose answers were both the recommended ones. Roman asked how long it waited and what the blast radius of his answer was.
- Said: "No, don't do that, you need to estimate the impact of the question, high medium low, if the impact is low, set a 20 minute timer and continue with recommended if I don't reply" (2026-10-02 08:45 UTC, session eca94a44), then "make the notification start with [high|med|low]" (08:49 UTC)
- Means: Rate every question. A low question goes by notification with a 20-minute timer, then the recommended answer runs. A high or medium question waits. (reasoned: the agent's reading as written in `CLAUDE.md`)
- Rule: `CLAUDE.md`, "Rate every question's impact as high, medium or low" (line 482); memory `run-the-recommended-path-while-asking.md`
- Supersedes: none

### R26. The night report tool drops its read-cost line, because the cost follows the questions and not the print (2026-10-02, meta workflow)
- Keys: night report tool, morning read cost, 40k, 60k, 95k, cost line, ends-when on a cost, print gaps, read of a night
- Situation: The tool was meant to make the morning read cost under 40k, and the line had moved to 60k. Four nights measured 95k, and the cost followed the questions asked.
- Said: "Drop the cost line, fix two print gaps, close (Recommended)" (2026-10-02 13:29 UTC, session eca94a44, an AskUserQuestion answer to a `[low]` question)
- Means: The frame closes on the print fixes. A cost line that the tool cannot control is not an ends-when. (confirmed for the first sentence: he chose this option; the second sentence is reasoned: the agent's reading)
- Rule: none found in the sources read
- Supersedes: his answer of 08:26 UTC the same day, "Fix the two wrong counts, move the line to 60k (Recommended)"

### R27. When a seat has the fact and does not act on it, interview the model in its context before a second brief shape (2026-10-02, meta workflow)
- Keys: interview the model, interview the seat, `probes/frame37/interview_turn.py --seq`, replay the turn, brief rewrite did not work, two rewrites, Tester never fixes the test, says the test is wrong but does not fix it, frame 110, escaped JSON string
- Situation: The Tester saw the full failure and in three of five runs said that the test called the function wrongly. It never fixed the test, and two rewrites of its instructions changed nothing.
- Said: "Interview the model" (2026-10-02 14:01 UTC, session eca94a44, an AskUserQuestion answer to "What next?")
- Means: An agent replays the seat's exact turn and asks it what it read, what it understood and what would have moved it. The fix is decided from the answers. (reasoned: the agent's reading as written in `CLAUDE.md`)
- Rule: `CLAUDE.md`, "interview the model in its context before a second brief shape" (line 257); memory `rota-interview-the-seat.md`
- Supersedes: none

### R28. Tell Roman what a frame means, and the number is only a tag such as F-101 (2026-10-02, meta workflow)
- Keys: frame numbers, F-101, what does the frame mean, project state, meaning of a frame, story, habit, do not persist, talk to Roman
- Situation: Roman said he did not know what the frame numbers meant for the app and the project. He asked for a way to stay aware of the project's state.
- Said: "I dont care about every number being followed by a description but for me the meaning of the frame is important whereas the number is not / You can abbreviate (F-101) / Don't make that persisted, just give yourself a habit to communicate meaning with me" (2026-10-02 17:58 UTC, session 46f23339)
- Means: In talk with Roman, say what the frame changes in rota. Write the number as a short tag. Keep this as a habit, not a repository rule. (reasoned: the agent's reading)
- Rule: memory `rota-frames-mean-not-number.md`
- Supersedes: none (refines R8 for talk with Roman)

### R29. An agent looks for the historical context of a question before the session asks it (2026-10-02, meta workflow)
- Keys: historical context, history read, ask an agent, prior ruling, before asking Roman, past discussions, decisions log
- Situation: The session was about to ask Roman questions about the project. Roman named the step before the ask.
- Said: "Ask an agent to look for any historical context for your questions" (2026-10-02 18:00 UTC, session 46f23339)
- Means: Before a question goes to Roman, an agent reads the records for prior context. (reasoned: the agent's reading)
- Rule: `CLAUDE.md`, "Before a frame blocks on Roman, an agent reads the records for a prior ruling" (line 441); memory `rota-history-before-escalation.md`
- Supersedes: none

### R30. A frame on a seat's behaviour closes on a ratio, and a residue with another cause becomes a new frame (2026-10-03, meta workflow)
- Keys: ends-when, close a frame, ratio, baseline, zero on a stochastic seat, residue rule, one bad shift, 27 of 28, burst, six questions at once, repeated question, telling-off, refusal repeats, push the burst, frame 111
- Situation: After two fixes, 27 of 28 Developer shifts stayed under the line of three identical refusals. One shift fired six questions at once on its first turn, four of them already answered.
- Said: "Close and push the burst (Recommended)" (2026-10-03 12:42 UTC, session 3d6e6173, an AskUserQuestion answer to a `[med]` question)
- Means: The frame closes, because the one shift left had a different cause. The burst is a new frame. (confirmed: he chose this option; the general three-part rule is the agent's reading, reasoned)
- Rule: `CLAUDE.md`, "An ends-when on a seat's behaviour has three parts" (line 240)
- Supersedes: none

### R31. The second card's first job is to keep the gate moving (2026-10-04, meta workflow)
- Keys: second card, second GPU, Titan, GTX TITAN X, slow bench, checker, gate, sign-off, night holds the GPU, rented GPU, online models, OpenRouter, budget 20 dollars a month, parallel nights
- Situation: A night held the 3080 for two hours, and the gate waited behind it. The Titan sat unused, and a rented card was another option.
- Said: "Keep the checker moving (Recommended)" (2026-10-04 01:33 UTC, session 3d6e6173, an AskUserQuestion answer to a `[med]` question)
- Means: The Titan serves the gate's re-records, not a second night. (confirmed: he chose this option)
- Rule: `plans/operating-facts.md`, "## Hardware and drives" (lines 61 to 77)
- Supersedes: none

### R32. The gate may run during a night and re-runs only the timing tests that fail (2026-10-04, meta workflow)
- Keys: gate during a night, gate beside a night, flaky tests, stopwatch tests, timing tests, crowded machine, no sign-off while a night runs, re-read the stumbles, `python -m rota.tools.gate`, smaller bites, trial on the Titan
- Situation: The rule was no sign-off while a night runs, because three timing tests once failed beside a night and passed alone. The session asked what the rule should become.
- Said: "Check during the night, re-read the stumbles (Recommended)" (2026-10-04 01:35 UTC), and "Try the smaller-bites setting first" if the Titan trial fails (01:36 UTC, session 3d6e6173, AskUserQuestion answers)
- Means: The gate runs beside a night, and only the failures are run again alone. (confirmed: he chose this option)
- Rule: `plans/operating-facts.md`, "The gate ran beside a night on a bench from 52e9ee8 to 585a9bc" (line 75)
- Supersedes: none

### R33. A stale case waits for the main card, because the Titan's recordings differ from the 3080's (2026-10-04, meta workflow)
- Keys: stale case, re-record, Titan, 3080, second card gives different answers, configuration mismatch, flash attention, batch size, CUDA, recording differs by card, gate waits for the main card, frame 124
- Situation: The gate re-recorded 15 cases on the Titan, and one failed there that passed on the 3080. Roman asked for a check of configuration mismatches, and every setting matched.
- Said: "Are we sure it's just the card? Is there no configuration mismatches?" (11:51 UTC), then "Wait for the main card (Recommended)" (2026-10-04 11:54 UTC, session 5e8ace65, AskUserQuestion answers)
- Means: The gate beside a night waits for the main card for its re-records. (confirmed: he chose this option)
- Rule: `plans/operating-facts.md`, "Since 585a9bc the gate beside a night waits for the main card with its re-records" (line 73)
- Supersedes: R32 for re-records on the Titan

### R34. The cut of a reply at a tool answer the seat wrote itself is parked (2026-10-04, rota workflow)
- Keys: fabricated tool result, predicted tool answer, seat writes the answer before the tool runs, invented result, cut the stored reply, drops the rest, warns, long replies push reads out, six GPU hours, re-records, park
- Situation: A seat sometimes wrote the answer it expected from a tool in its own reply. The fix cut the stored reply at that point and cost about six GPU hours of re-records.
- Said: "Park it" (2026-10-04 11:51 UTC, session 5e8ace65, an AskUserQuestion answer to a `[med]` question)
- Means: The fix does not run now. It waits as a parked frame. (reasoned: the agent's reading)
- Rule: none found in the sources read
- Supersedes: none

### R35. Before a question goes to Roman, an agent reads the decisions and past discussions, because he has often ruled already (2026-10-04, meta workflow)
- Keys: history read, prior ruling, already discussed, decisions log, transcripts, `C:\Users\roman\.claude\projects\d--repos-rota\*.jsonl`, `rota/DECISIONS.md`, `LAWS.md`, `plans/archive/`, `git log -S`, inherited question, recommended answer tested, frame 114, frame 115, Developer broke a project file, Architect has no place to write an answer
- Situation: Session 419281dc asked inherited questions about a broken project file and the Architect's answer. He sent each back for a read of past decisions.
- Said: "sorry i may have missexplained, when i meant "investigate our decisions, previous thoughts etc" i meant, that we have already discussed this, use a subagent to search our decisions logs, etc ie meta" (2026-10-04 13:34 UTC, session 419281dc, an AskUserQuestion answer); `CLAUDE.md` gives "yeah add it" at 14:52
- Means: An agent answers two things first: what the records say, and whether the recommended answer holds against the evidence. A question that the read dissolves is not asked. (reasoned: the agent's reading as written in `CLAUDE.md`)
- Rule: `CLAUDE.md`, "Before any question goes to Roman, new or inherited, an agent answers two things" (line 451)
- Supersedes: none (extends R29)

### R36. The non-implementer agents run on Fable (2026-10-05, meta workflow)
- Keys: agent model, Fable, Opus, reviewer model, reader model, non-implementer subagents, model choice
- Situation: The session ran every agent on Opus under the ruling of 2026-09-24. Roman asked for a change.
- Said: "Please switch to fable for the non-implementer subagents" (2026-10-05 11:07 UTC, session c81b16d3)
- Means: Reads and reviews run on Fable, and implementers stay on Opus. (reasoned: the agent's reading)
- Rule: none today. R37 replaced it.
- Supersedes: R14 for the non-implementer agents

### R37. Every agent runs on Opus again, reads and reviews included, because Fable cost more (2026-10-07, meta workflow)
- Keys: agent model, `model: "opus"`, Opus, Fable, night read cost, review cost, 437k, non-implementer subagents, reviewer model, which model for an agent
- Situation: One day on Fable for the non-implementer agents cost 437k for a night read and 180k to 250k for a review. On Opus the same work cost about 100k to 130k.
- Said: "Please switch back to opus for the relevant subagents" (2026-10-07 00:50, session unknown; quoted in `CLAUDE.md`)
- Means: Pass `model: "opus"` on every agent. Fable is the holding session alone. (reasoned: the agent's reading as written in `CLAUDE.md`)
- Rule: `CLAUDE.md`, "Every agent runs on Opus again" (line 293); memory `rota-agents-run-on-opus.md`
- Supersedes: R36

### R38. A Critic's pass names one added diff line per criterion, because an empty pass let a defect through (2026-10-07, rota workflow)
- Keys: Critic, pass verdict, empty pass, inspector, signs passed, `verdicts.emit`, `lines=`, one line per criterion, line the diff does not add, `LinesRefusal`, `rota/roles/prompts/critic/review.md`, requirement removed still passed, model limitation or structure
- Situation: The Critic signed a pass in the first minute with no note on ten batches in a row. A batch passed with an untested defect, and a rerun with one criterion's code removed still passed twice.
- Said: "Is this a model limitation also?", then "Pass names a line per requirement (Recommended)" (2026-10-07 07:55 and 07:56 UTC, session 6cc11c8b, AskUserQuestion answers to a `[high]` question)
- Means: A pass carries each criterion's id with the diff line that meets it, and the tool refuses a pass with a missing or unadded line. (confirmed: he chose this option)
- Rule: `rota/roles/prompts/critic/review.md`, the `verdicts.emit` paragraph (line 32); `rota/roles/api.py`, the lines check (line 10960)
- Supersedes: none

### R39. The park ask is a page of criterion rows, and the principal never gets a fix word (2026-10-08, rota workflow)
- Keys: park ask, parked batch, fix choices, fix word, count of fix choices, why would an implementer fail, principal rules on criteria, criterion rows, test expectation beside the criterion, approve contest revise, Tester rewrites the test, builder's regression, frame 142, law 9
- Situation: Frame 142 asked how many fix choices the park page should offer. Roman sent the question back twice and asked why a builder would fail to implement a fix.
- Said: "No I mean think about it, why would an implementer fail to implement the fix?" (2026-10-08 18:55 UTC, session acb1f403), then "sounds good" to the assistant's reading (2026-10-08 23:25, quoted in `rota/DECISIONS.md`)
- Means: A fix is the team's verb, and a retry at zero temperature repeats the failure. The page shows each criterion with its test's expectation, and the principal rules on the criteria, never on a test. (confirmed: "sounds good" to this reading)
- Rule: `rota/DECISIONS.md`, "### The park ask is a page with rows, and the principal's words always land on a row (2026-10-08)" (line 1445)
- Supersedes: none (keeps R4 as its point 3)

### R40. A hand-off carries a momentum note with the judgement, and the taker asks the sender for context (2026-10-09, meta workflow)
- Keys: momentum note, `plans/handoff-<sid>.md`, hand-off loses context, handover momentum, judgement not facts, transcript pointer, too noisy, context questions to the sender, peer name in the first line
- Situation: Roman said a hand-off loses context momentum. The assistant proposed a note with the judgement, a pointer to the transcript turns, and questions to the sender.
- Said: "1 yes / 2 too noisy over time? / 3 yeah would be good for some context questions" (2026-10-09 00:08 UTC, session acb1f403)
- Means: Write the note before the hand command. Do not point at transcript turns. The taker messages the sender before it asks Roman. (reasoned: the agent's reading as written in `CLAUDE.md`)
- Rule: `CLAUDE.md`, "A hand-off carries a momentum note beside the status line" (line 82); memory `rota-handoff-momentum-note.md`
- Supersedes: none (extends R17)

### R41. The frames are re-batched around what the principal sees (2026-10-09, rota workflow)
- Keys: principal's page, status page, none of these lines is about what I asked for, Liaison writes notes about internal rules, page never empty, second change never started, wrong test file, correction refused, build preview, what the principal sees, re-batch frames
- Situation: On a night the principal said eleven times that no line was about his ask, and each time the Liaison added a note about an internal rule. A correction about the wrong test file was refused five times.
- Said: "Re-batch around what the principal sees (Recommended)" (2026-10-09 09:31 UTC, session d7cf65d1, an AskUserQuestion answer to a `[high]` question)
- Means: The open frames are grouped by the principal's view, not by seat. (reasoned: the agent's reading; the question text is cut in the stream)
- Rule: none found in the sources read
- Supersedes: none

### R42. A night that loops on another frame's wall, with no new data for the held frame, is stopped and read (2026-10-09, meta workflow)
- Keys: stop a night, loop, CYCLE line, step cap, abandoned batches, another frame's wall, held frame gets no data, night 137, walk 3, frame 186, frame 190, is there a point in keeping going
- Situation: Night 137's walk 3 looped on frame 186's wall, with eleven batches abandoned in twenty minutes and no page for frame 190. Walk 1 already held the measure.
- Said: "well is there a point in keepin going with it?", then "ok so in the future we need to do the same, update your context infrastructure" (2026-10-09 19:19 UTC, session 45fc3fe2)
- Means: At each CYCLE line, name the frame. When the loop is not the held frame's and the walks before gave the measure, stop the night, copy the records and start the read. (reasoned: the agent's reading as written in `CLAUDE.md`)
- Rule: `CLAUDE.md`, "A night is stopped when its loop is a known open frame's wall" (line 422); memory `rota-stop-a-night-that-measures-nothing.md`
- Supersedes: none (extends R19)

### R43. One design frame covers the second request, in place of three frames that each held a piece (2026-10-10, rota workflow)
- Keys: second request, new request, old request's page comes back, Liaison asks which lines relate, new words land on the old item, grouping opens batches on the old item, put-off item on every page, contested item, frame 185, frame 186, frame 190, night 137, design frame
- Situation: Night 137 showed that when the principal moved to a new request, the old request's page came back and the new words landed on the old item. Three open frames each held a piece of that wall.
- Said: "One design frame over the second request (Recommended)" (2026-10-10 02:29 UTC, session 45fc3fe2, an AskUserQuestion answer to a `[med]` question)
- Means: Frames 185, 186 and 190 fold into one design frame. (confirmed: he chose this option)
- Rule: none found in the sources read
- Supersedes: none

### R44. A frame taken at a hand-off continues without a check with Roman (2026-10-10, meta workflow)
- Keys: handed frame, hand-off, take, wake steps, ask before starting, check the reading, pass 1, frame 193, standby, state reply
- Situation: A session took frame 193 at a hand-off and asked Roman before pass 1. Roman said the hand-off is his assignment.
- Said: "Yes, don't ask when you are handed over to" (2026-10-10 03:46 UTC, session 3be6b81d)
- Means: Reply with the state, then start the frame's next step. Check the reading first only on a frame Roman gives fresh. (reasoned: the agent's reading as written in `CLAUDE.md`)
- Rule: `CLAUDE.md`, "A handed frame continues without a check" (line 220); memory `rota-handed-frame-continues.md`
- Supersedes: none
