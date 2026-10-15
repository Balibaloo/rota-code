# Roman's rulings on walls, doors, briefs and escalation

This record collects what Roman ruled about the fix of a wall. It is task C
of frame 251's research. It is a collection. It recommends nothing.

How to read an entry:

- A quote in double quotes is Roman's own words, copied verbatim with his
  spelling.
- A source of eight hex characters is a build transcript in
  `C:\Users\roman\.claude\projects\d--repos-rota\`. "typed" means a typed
  message. "AUQ" means his answer to an `AskUserQuestion`, and the question
  is cut to its first words.
- Transcript times are UTC, as the transcript stores them. The records use
  local time, which is one hour later. So a record's 01:54 is a
  transcript's 00:54.
- "Record paraphrase" means a record states the ruling in its own words.
  The entry keeps the record's own mark.

Counts: 58 entries. 47 come from the transcripts. 11 come from the records
only. Some transcript entries also cite the record that holds them.

The scan read 108 transcript files (2026-09-16 to 2026-10-15). It kept typed
messages under 2000 characters and the `answers` field of `AskUserQuestion`
results. The script is
`scratchpad\f251\scan.py` of session dae006d1.

## 1. Where a fix goes, and the kinds of change

1. "Ok the door approach cannot be used for every issue identified, there
   needs to be another ladder here". 2026-10-15 00:50 UTC. 4754aaec, typed.
   (ruled: Roman, 2026-10-15)
2. "Ok well maybe I'm too detached from the development to know what kind of
   logic we are encoding in the doors but I want to prevent over fitting. All
   I'm saying is that when we hit walls the solutions can range from simple
   to complex but theres only so many kind of changes we can make".
   2026-10-15 00:54 UTC. 4754aaec, typed. Record: `plans/stack.md:317`
   cites it as "there's only so many kind of changes we can make" (ruled:
   Roman, 2026-10-15 01:5x). (ruled: Roman, 2026-10-15)
3. To the question "Which rung above the doors should carry your words to
   the seats that build and check?": "I'm saying it's not as simple as adding
   a reminder". 2026-10-15 00:51 UTC. 4754aaec, AUQ. (ruled: Roman,
   2026-10-15)
4. "Ok and why not a brief change? How does a predicate catch this?"
   2026-10-15 01:15 UTC. 4754aaec, typed. A question, recorded here because
   it challenges a door choice. (ruled: Roman, 2026-10-15)
5. "But anyways, this wall ladder is not sound." and "Ok so the ladder needs
   design and review passes itself". 2026-10-15 01:19 and 01:21 UTC.
   4754aaec, typed. Record: `plans/stack.md:279` (ruled: Roman, 2026-10-15
   02:22). (ruled: Roman, 2026-10-15)
6. "Importantly make the fable reviewer review  if the wall ladder is the
   right thing for this project". 2026-10-15 09:43 UTC. 4754aaec, typed.
   Record: `plans/stack.md:290`. (ruled: Roman, 2026-10-15)
7. "No, sorry I kicked this off poorly. I just want to spend time to reason
   about all the kinds of problems that we can have with walls in rota and
   make a reasoning guide for future sessions to offload that work off them.
   That's what I want". 2026-10-15 09:57 UTC. 4754aaec, AUQ. Record:
   `plans/stack.md:292`. (ruled: Roman, 2026-10-15)
8. "It's a guide to making decisions about how to fix walls. So night reader
   maybe, solution designer definitely". 2026-10-15 10:46 UTC. dae006d1,
   AUQ. (ruled: Roman, 2026-10-15)
9. The decisions the guide makes easier: "Where the fix goes, by kind of
   problem", "Whether to fix at all", "Whether a fix overfits the night"
   (three options chosen, multi-select). 2026-10-15 10:47 UTC. dae006d1, AUQ.
   (ruled: Roman, 2026-10-15)
10. Two walls are one kind by "The same cause in the structure".
    2026-10-15 10:48 UTC. dae006d1, AUQ. (ruled: Roman, 2026-10-15)
11. "I guess for now there is only cheap  and escalate to me". The question
    asked for the rungs above the cheap fix. 2026-10-15 10:53 UTC. dae006d1,
    AUQ. (ruled: Roman, 2026-10-15)
12. "Yes that's exactly it, and whilst we're doing the research, we can do an
    evaluation, review and proper design pass on top". 2026-10-15 10:55 UTC.
    dae006d1, AUQ. (ruled: Roman, 2026-10-15)
13. "What is this question, redesign the wall guide from first principles on
    fable". The question asked whether the fix may be a list of his phrases
    in the code. 2026-10-15 10:43 UTC. dae006d1, AUQ. (ruled: Roman,
    2026-10-15)

## 2. Door or brief

14. "these deterministic checks I'm not so sure about their quality, the
    system prompt is where the real work is I believe". 2026-09-02, before
    the transcripts. Record paraphrase: `plans/operating-facts.md:289`,
    "Roman ruled prompts over guards. No rule bounds an LLM judgement."
    (ruled: Roman, 2026-09-02)
15. "slicing should be an intelligent LLM operation" and "I'm not sure a
    deterministic guard is able to fix this" (the criterion-word detector,
    reverted). Before 2026-09-02, no date in the record.
    `plans/operating-facts.md:290`. Record quote, no own mark.
16. Record paraphrase: "Before you add a guard, ask whether the brief's
    structure can carry the rule. Prefer the brief unless the rule is a fact
    about the harness (stdin, imports, stale runs) or state semantics. Do not
    bound LLM judgements (slicing, triage, review) by rule."
    `plans/operating-facts.md:293`. Section "Rulings on briefs and doors",
    no own mark.
17. "Ok but our briefs are not perfect, maybe we can iterate briefs on the
    specific case before doing a full re-record." 2026-10-15 01:19 UTC.
    4754aaec, typed. Record: `plans/stack.md:279`. (ruled: Roman,
    2026-10-15)
18. To "Two of the ten red cases stay red for reasons a brief line cannot
    fix": "Both: the Tester may read source, and the survey desk gets the
    guard (Recommended)". 2026-09-24 20:42 UTC. 8736e9fc, AUQ. (ruled:
    Roman, 2026-09-24)
19. To the question on a refused write that ends the matter or leaves a job
    undone: "The door says which kind (Recommended)". 2026-09-27 18:11 UTC.
    213e58fd, AUQ. (ruled: Roman, 2026-09-27)
20. To the frame 61 redesign, a line at the end of every prompt while a
    refused write stands: "So nothing being set in stone but needing
    carefully deliberation to change it. Do we need to redesign something?"
    2026-09-25 09:00 UTC. 5748c2d9, AUQ. (ruled: Roman, 2026-09-25)
21. "[high] Given that both the structure and the model let the empty pass
    through": "Pass names a line per requirement (Recommended)". 2026-10-07
    07:56 UTC. 6cc11c8b, AUQ. Record: `plans/archive/stack-2026-10-08.md:20`,
    "the door refuses a pass that leaves a criterion unnamed" (ruled: Roman,
    2026-10-07 08:57). (ruled: Roman, 2026-10-07)
22. "Yes, add the edge (Recommended)", the Architect at the exhausted rung
    gets the reads-tests edge. 2026-10-01 14:12 UTC. 10885dab, AUQ. Record:
    `plans/archive/stack-2026-10-02.md:48` (ruled: Roman, 2026-10-01 15:12).
    (ruled: Roman, 2026-10-01)
23. "Yes (Recommended)": rewrite the case so the stall leaves the Architect's
    desk to a named next seat, and send the emergency exit to the coverage
    backlog. 2026-10-01 16:18 UTC. 10885dab, AUQ. Record:
    `plans/archive/stack-2026-10-02.md:52` (ruled: Roman, 2026-10-01 17:19).
    (ruled: Roman, 2026-10-01)
24. Record paraphrase: a brief change is one frame. "five brief edits are one
    frame, not five hand-offs". `plans/archive/stack-2026-09-17.md:11`
    (ruled: Roman, 2026-09-17).

## 3. Overfit and what generalises

25. "Ok, and are we not over fitting?" 2026-10-15 00:47 UTC. 4754aaec,
    typed. (ruled: Roman, 2026-10-15)
26. "I want to prevent over fitting" (in entry 2). 2026-10-15 00:54 UTC.
    4754aaec, typed.
27. To "[high] What tells a cheap fix apart from one that only fits
    tonight?": "I thought that this is the kind of knowledge that we just have
    about the project. Use opus to do deep research. But first I dont feel
    like you see the value of this". 2026-10-15 10:54 UTC. dae006d1, AUQ.
    Record: `plans/stack.md:296`. (ruled: Roman, 2026-10-15)
28. "so we have to be carefull to ensure that the workflow generalises".
    The question was on notes that park at the merge. 2026-10-11 13:02 UTC.
    be3ef742, AUQ. (ruled: Roman, 2026-10-11)
29. "Are any of the fixes specific to the language or model? Are they one off
    fixes or general issues that any language or model would have struggled
    with?" 2026-10-05 08:43 UTC. 5101d8d0, typed. A question that sets the
    test. (ruled: Roman, 2026-10-05)
30. "Ok, should any of these have been caught by the register or something?
    ... Are there any categories of test that implementing now would save us
    time running the nights?" 2026-10-05 08:46 UTC. 5101d8d0, typed.
    (ruled: Roman, 2026-10-05)
31. Record paraphrase: the lexical respecify door is dropped "because its
    predicate cannot be stated without the night's words, rung 1's overfit
    test". `plans/stack.md:317` (ruled: Roman, 2026-10-15 01:5x). The test
    itself is the session's reading of his words. The Fable review of
    02:05 then replaced it with a count (`plans/stack.md:318`, observed).
32. Record: `rota/DECISIONS.md:375`, the warning in `l1_liaison.yaml`, "a
    brief that can only be tuned in one direction gets tuned until the other
    direction breaks". *Consequence:* "no per-model brief mechanism is needed
    and none should be built." The record carries no Roman mark.

## 4. The model's judgement and the ceiling

33. "Have we confirmed that larger models, eg Gemma are capable? If not then
    it's the structures fault". 2026-09-23 14:08 UTC. dba7e375, typed.
    Record: `plans/archive/stack-2026-09-23.md:1669`, "Every local model
    invents under the same pointer, so the fault is the structure's" (ruled:
    Roman, 2026-09-23 15:00, "if not then it's the structure's fault").
34. "can we double check that the large local model handles this well?"
    2026-09-23 12:10 UTC. 07e01dfc, typed. (ruled: Roman, 2026-09-23)
35. "so we dont know what went wrong, but what went wrong is either in the
    model context (data/tooling/environment) or in the model itsself, so we
    need to categorize that". 2026-09-18 15:03 UTC. 75d12c2b, typed.
    (ruled: Roman, 2026-09-18)
36. "Were assuming that zero temperature models will be coonsistent enough
    to have similar enough responses to the same problem set, this is
    something that we need to validate". 2026-09-18 15:06 UTC. 75d12c2b,
    typed. (ruled: Roman, 2026-09-18)
37. To an empty pass by the inspector: "Is this a model limitation also?"
    2026-10-07 07:55 UTC. 6cc11c8b, AUQ. The next answer (entry 21) put the
    fix in the structure. (ruled: Roman, 2026-10-07)
38. To a tester that says the test is wrong and keeps it: "Interview the
    model". 2026-10-02 14:01 UTC. eca94a44, AUQ. Record paraphrase:
    `CLAUDE.md`, "When a seat has a fact in front of it and does not act on
    it, interview the model in its context before a second brief shape"
    (ruled: Roman, 2026-10-02 15:02, frame 110).
39. "Ok nice, and do we have guidance for you or just a reminder that
    interviewing the model in its context is a great investigation tool?"
    2026-10-02 22:48 UTC. 46f23339, typed. (ruled: Roman, 2026-10-02)
40. "Ok I trust your judgement, keep going though the batches, I'm going
    afk". 2026-09-23 03:57 UTC. 9fe32e55, typed. This is the build session's
    judgement, meta workflow. (ruled: Roman, 2026-09-23)

## 5. Escalation to Roman

41. "The budget line, if theres something wrong with the ticket it will
    escalate before this, so budget is a useless escalation signal."
    2026-09-17 00:58 UTC. 32a42b78, typed. (ruled: Roman, 2026-09-17)
42. "Wait but do we need any of this? or will the fable session just be able
    to handle escalations that have multi frame, project wide implications?"
    2026-09-17 12:43 UTC. cc3d4e4e, typed. (ruled: Roman, 2026-09-17)
43. "So if a wall is only a small inefficiency and we can't fix it easily
    then leave it, however the idea is that we either can fix it cheaply
    (which is what the guide documents) or we need to lean on a more
    expensive fix higher up the ladder, or if we dont expect anything in the
    wall ladder to fix it, escalate all the way to the top so that we can
    discuss the problem and design at the highest level". 2026-10-15 10:51
    UTC. dae006d1, AUQ. (ruled: Roman, 2026-10-15)
44. Rota workflow: a given-up change put back in the chair: "It waits for the
    principal (Recommended)". 2026-09-27 18:19 UTC. 213e58fd, AUQ. (ruled:
    Roman, 2026-09-27)
45. Rota workflow: "Architect reviews some categories of notes if I don't
    and escalates or resolves no?" 2026-10-11 14:43 UTC, then "Every
    default" at 14:59 UTC. c81dd240, AUQ. Record: `plans/stack.md:573`
    (ruled: Roman, 2026-10-11 15:49).
46. Rota workflow: "right but notes can come from many sources and seats
    cant escalate to everyone? is that right? anyways, this is a big question
    that we are building up a corpus of evidence for that we need to do a
    complete design pass over initialy". 2026-10-11 14:05 UTC. be3ef742,
    typed. Record: `plans/stack.md:567`. (ruled: Roman, 2026-10-11)
47. Record: `rota/LAWS.md:183`, law 6, "Escalation only climbs. The ladder
    is Developer → Architect → Vision Keeper → Liaison." At the Liaison
    "It is never silence" (ruled 2026-09-13, `plans/principal-flow.md`).
48. Record paraphrase, meta workflow: escalate as a blocked frame when "a
    ruling is needed, a wall survives three cycles, a change touches the
    composition, or the budget is spent". Before that, an agent reads the
    records for a prior ruling. `CLAUDE.md`, "The assistant" (ruled: Roman,
    2026-10-03). Before any question, two reads: `CLAUDE.md` (ruled: Roman,
    2026-10-04 14:52, "yeah add it").
49. Record paraphrase, meta workflow: "The session picks the next night's
    wall itself" (ruled: Roman, 2026-10-12 23:52, "debug planing is
    relatively intuitive as long as it doesn't open large questions that
    lead you to do autonomous investigations first"). `CLAUDE.md`.
50. Record paraphrase, meta workflow: "You have signoff to run the nights"
    (ruled: Roman, 2026-09-22 19:28). `plans/operating-facts.md:171`.

## 6. Re-records

51. To the case that lost 10 of 10 greens on a re-record: "Re-record freely,
    keep the rule". 2026-09-20 23:16 UTC. cb5428a2, AUQ. Record paraphrase:
    "A re-record runs without asking (ruled: Roman, 2026-09-20)",
    `plans/archive/stack-2026-09-22.md:1065`.
52. "Yeah maybe clone this as a backup legacy dB and migrate over What's
    useful, full re-record is approved if necessary". 2026-09-21 15:00 UTC.
    75f21e35, AUQ. Record: `plans/archive/register-key-design-2026-09-21.md:308`.
    (ruled: Roman, 2026-09-21)
53. Record paraphrase: "The existing rows are written off, not re-recorded"
    (ruled: Roman, 2026-09-21, asked with two other answers).
    `plans/archive/stack-2026-09-21.md:1177`.
54. "Repair, is there anything else that will stale that we should do at the
    same time?" (frame 65, full re-record of 128 cases). 2026-09-23 01:03
    UTC. 001e49dd, AUQ. Then "Full re-record" at 03:38 UTC, 9fe32e55, AUQ.
    (ruled: Roman, 2026-09-23)
55. "If code changed, CPU is cheap, if prompts changed, they need to be
    tested, am I missing an optimisation here?" then "The gate re-records its
    stale set (Recommended)". 2026-09-27 18:42 and 18:44 UTC. 213e58fd, AUQ.
    (ruled: Roman, 2026-09-27)
56. "Checkpoints should only be dropped if the briefs that made them have
    been affected, is it cheap to make a system that tracks what briefs have
    beeen used to make a certain state of db, and if any brief changes,
    rewind the db down to when the last brief that was used." 2026-10-13
    17:46 UTC. e669185f, typed. Record: `plans/archive/stack-2026-10-13.md:195`.
    (ruled: Roman, 2026-10-13)

## 7. When to leave a wall unfixed

57. Entry 43 holds the main ruling: "if a wall is only a small inefficiency
    and we can't fix it easily then leave it". Three earlier answers left a
    wall unfixed on purpose:
    - Frame 55, model drift at a fixed key: "Write it off with the reason
      (Recommended)". 2026-09-22 21:15 UTC. 41cb5184, AUQ. (ruled: Roman,
      2026-09-22)
    - A stored reply cut at the guessed tool answer, six GPU hours of
      re-records: "Park it". 2026-10-04 11:51 UTC. 5e8ace65, AUQ. (ruled:
      Roman, 2026-10-04)
    - An old failure on the known-failures list: "Add it to the list now
      (Recommended)". 2026-09-27 18:07 UTC. 213e58fd, AUQ. (ruled: Roman,
      2026-09-27)
58. A night that loops on another frame's wall is stopped: "ok so in the
    future we need to do the same". 2026-10-09 20:19 local. Record:
    `plans/archive/stack-2026-10-10.md:44` and `CLAUDE.md` (ruled: Roman,
    2026-10-09 20:19). Also the focus question: "are we not focusing on the
    biggest issue then?" and "the biggest issue, mm ok that sounds too
    convoluted, should we just keep working the way we are?" 2026-10-13
    17:46 and 17:49 UTC. e669185f, typed. (ruled: Roman, 2026-10-13)

## What the scan did not find

- No typed message names "ceiling" or "small model". The ceiling entries
  (section 4) come from his questions about larger models.
- No transcript holds the 2026-09-02 words of entry 14. The transcripts
  start on 2026-09-16, so the record is the only source.
- The words of the re-record rule of 2026-09-20 ("re-records are cheap")
  are not in a typed message under 2000 characters. Only the record holds
  them.
- The scan skipped messages over 2000 characters. A long ruling typed as one
  message is not in this file.
